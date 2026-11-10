import hashlib
import hmac
import html
import re
import secrets
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

bearer_scheme = HTTPBearer(auto_error=False)
_fernet = Fernet(settings.fernet_key)

# In-memory sliding window rate limiter
_rate_buckets: dict[str, list[float]] = defaultdict(list)

INVALIDATED_WEAK_PASSWORDS = {
    "uniongrowth@2026",
    "admin123",
    "admin123456",
    "1234567890",
    "password123",
    "qwerty1234",
}


def validate_strong_password(password: str) -> tuple[bool, str]:
    """
    Validates that a password meets enterprise security requirements and is NOT
    the invalidated initial default password.
    """
    if not password or len(password) < 10:
        return False, "A senha deve ter no mínimo 10 caracteres."
    if password.strip().lower() in INVALIDATED_WEAK_PASSWORDS:
        return False, "Esta senha padrão/fraca foi invalidada por política de segurança. Escolha uma senha forte exclusiva."
    if not re.search(r"[A-Z]", password):
        return False, "A senha deve conter pelo menos uma letra maiúscula."
    if not re.search(r"[a-z]", password):
        return False, "A senha deve conter pelo menos uma letra minúscula."
    if not re.search(r"\d", password):
        return False, "A senha deve conter pelo menos um número."
    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "A senha deve conter pelo menos um caractere especial (ex: !@#$%&*)."
    return True, "Senha forte validada."


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou expirado: {exc}",
        )


def encrypt_secret(plain_text: str) -> str:
    if not plain_text:
        return ""
    return _fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")


def decrypt_secret(cipher_text: str) -> str:
    if not cipher_text:
        return ""
    try:
        return _fernet.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""


def mask_secret(plain_text: str) -> str:
    if not plain_text:
        return ""
    if len(plain_text) <= 6:
        return "***"
    return f"{plain_text[:3]}...{plain_text[-3:]}"


def sanitize_text(value: str | None) -> str:
    if not value:
        return ""
    cleaned = re.sub(r"<script.*?>.*?</script>", "", value, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"javascript:", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"on\w+\s*=", "", cleaned, flags=re.IGNORECASE)
    return html.escape(cleaned.strip(), quote=False)


def generate_high_impact_token(user_id: int, tenant_id: int, action_type: str) -> str:
    """Generate a deterministic HMAC confirmation token for high-impact actions."""
    minute_bucket = int(time.time() // 600)
    msg = f"{user_id}:{tenant_id}:{action_type}:{minute_bucket}".encode("utf-8")
    sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), msg, hashlib.sha256).hexdigest()[:16]
    return f"CONFIRM-{sig.upper()}"


def verify_high_impact_token(user_id: int, tenant_id: int, action_type: str, token: str) -> bool:
    if not token:
        return False
    for offset in (0, -1):
        minute_bucket = int(time.time() // 600) + offset
        msg = f"{user_id}:{tenant_id}:{action_type}:{minute_bucket}".encode("utf-8")
        sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), msg, hashlib.sha256).hexdigest()[:16]
        if hmac.compare_digest(token, f"CONFIRM-{sig.upper()}"):
            return True
    return False


_login_failures: dict[str, list[float]] = defaultdict(list)
LOGIN_MAX_FAILURES = 8
LOGIN_WINDOW_SECONDS = 300


def _login_key(request: Request, email: str) -> str:
    ip = request.client.host if request.client else "local"
    fwd = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return f"{fwd or ip}|{email.lower()}"


def check_login_allowed(request: Request, email: str) -> None:
    key = _login_key(request, email)
    now = time.time()
    _login_failures[key] = [t for t in _login_failures[key] if t > now - LOGIN_WINDOW_SECONDS]
    if len(_login_failures[key]) >= LOGIN_MAX_FAILURES:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas de login falhas. Aguarde alguns minutos.",
        )


def register_login_failure(request: Request, email: str) -> None:
    _login_failures[_login_key(request, email)].append(time.time())


def clear_login_failures(request: Request, email: str) -> None:
    _login_failures.pop(_login_key(request, email), None)


def enforce_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "local"
    now = time.time()
    window_start = now - 60.0
    bucket = _rate_buckets[client_ip]
    _rate_buckets[client_ip] = [t for t in bucket if t > window_start]
    if len(_rate_buckets[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Limite de requisições excedido (Rate Limit). Aguarde alguns segundos.",
        )
    _rate_buckets[client_ip].append(now)


def user_must_change_password(user) -> bool:
    import json as _json

    try:
        return bool(_json.loads(user.preferences_json or "{}").get("must_change_password"))
    except Exception:
        return False


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    from app.models.entities import User

    enforce_rate_limit(request)
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária. Forneça Bearer Token.",
        )
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sem identificador de usuário.")
    user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado ou inativo.")

    if user_must_change_password(user) and request.url.path not in ("/api/v1/auth/change-password", "/api/v1/auth/me"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PASSWORD_CHANGE_REQUIRED: defina uma nova senha forte em /api/v1/auth/change-password antes de continuar.",
        )

    header_tenant = request.headers.get("X-Tenant-Id")
    if header_tenant and header_tenant.isdigit():
        requested_tid = int(header_tenant)
        if requested_tid != user.tenant_id and user.role == "owner":
            from app.models.entities import Tenant
            t = db.query(Tenant).filter(Tenant.id == requested_tid, Tenant.owner_email == user.email).first()
            if t:
                user.active_tenant_override = requested_tid
    return user


def get_active_tenant_id(user) -> int:
    return getattr(user, "active_tenant_override", None) or user.tenant_id


def require_roles(*allowed_roles: str):
    def _checker(user=Depends(get_current_user)):
        if user.role not in allowed_roles and user.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão insuficiente. Requer um dos papéis: {', '.join(allowed_roles)}",
            )
        return user

    return _checker

