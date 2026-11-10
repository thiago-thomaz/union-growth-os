import base64
import hashlib
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "assets").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "backups").mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    APP_NAME: str = "UNION GROWTH OS"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = False

    DATABASE_URL: str = f"sqlite:///{(DATA_DIR / 'union_growth_os.db').as_posix()}"
    FALLBACK_SQLITE_URL: str = f"sqlite:///{(DATA_DIR / 'union_growth_os_fallback.db').as_posix()}"

    SECRET_KEY: str = "union-growth-os-default-secret-key-change-in-prod-2026"
    JWT_SECRET: str = "union-growth-os-jwt-secret-key-change-in-prod-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENCRYPTION_KEY: str = ""

    PUBLIC_URL: str = "https://automacao.projetosunion.cloud"
    CUSTOM_DOMAIN_URL: str = "https://automacao.projetosunion.cloud"
    CORS_ORIGINS: str = "https://automacao.projetosunion.cloud,https://uniongrowth.72.62.13.62.sslip.io,https://growth.projetosunion.cloud,http://localhost:3000,http://localhost:8000"

    ADMIN_INITIAL_EMAIL: str = "admin@projetosunion.cloud"
    ADMIN_INITIAL_PASSWORD: str = ""

    AI_DEFAULT_PROVIDER: str = "hybrid"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_COMPATIBLE_BASE_URL: str = ""
    OPENAI_COMPATIBLE_API_KEY: str = ""
    OPENAI_COMPATIBLE_MODEL: str = ""
    ENABLE_FREE_PUBLIC_LLM: bool = False
    AI_DAILY_TOKEN_LIMIT: int = 250000
    AI_DAILY_CALL_LIMIT: int = 500
    PAGESPEED_API_KEY: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@projetosunion.cloud"
    SMTP_USE_TLS: bool = True

    SCHEDULER_ENABLED: bool = True
    BACKUP_DIR: str = str(DATA_DIR / "backups")
    ASSETS_DIR: str = str(DATA_DIR / "assets")
    DATA_RETENTION_DAYS: int = 365
    RATE_LIMIT_PER_MINUTE: int = 180

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def normalized_database_url(self) -> str:
        url = self.DATABASE_URL.strip()
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and "+psycopg2" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    @property
    def cors_origins_list(self) -> list[str]:
        raw = (self.CORS_ORIGINS or "").strip()
        if not raw or raw == "*":
            return [
                self.PUBLIC_URL,
                self.CUSTOM_DOMAIN_URL,
                "http://localhost:3000",
                "http://localhost:8000",
                "http://127.0.0.1:8000",
            ]
        return [o.strip() for o in raw.split(",") if o.strip()]

    @property
    def fernet_key(self) -> bytes:
        if self.ENCRYPTION_KEY and len(self.ENCRYPTION_KEY.strip()) == 44:
            try:
                base64.urlsafe_b64decode(self.ENCRYPTION_KEY.strip())
                return self.ENCRYPTION_KEY.strip().encode("utf-8")
            except Exception:
                pass
        digest = hashlib.sha256((self.ENCRYPTION_KEY or self.SECRET_KEY).encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)


settings = Settings()

