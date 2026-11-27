# UNION GROWTH OS — AUDITORIA DE SEGURANÇA & LGPD (FASE 27)

## 1. Evidências Reais Verificadas (`GET /api/v1/security/audit` em Produção)

- `default_signing_secrets_in_use`: **`false`**
- `users_with_invalidated_default_password_still_valid`: **`0`**
- `users_requiring_password_change`: **`0`**
- `password_hash`: `bcrypt (rounds=10)`
- `jwt`: `HS256, expira em 1440 min`
- `credentials_encryption`: `Fernet (AES-128-CBC + HMAC)`
- `cors_allowed_origins`: estritamente restrito (`automacao.projetosunion.cloud`, `uniongrowth.72.62.13.62.sslip.io`, `growth.projetosunion.cloud`, localhosts de dev — sem `*`).
- `rate_limit_per_minute`: `600` (`test_48` valida bloqueio `429` e isolamento X-Forwarded-For).
- `login_bruteforce_protection`: `8 falhas / 5 min por IP+e-mail` (`test_24`).
- `tenant_isolation`: todas as queries filtradas por `tenant_id` (`X-Tenant-Id` bloqueia com `403` acesso entre donos — `test_03`, `test_50`, J19).
- **Anti-SSRF:** `validate_public_http_url` bloqueando loopback/privado/cloud metadata (`test_49`, J20 `400`).
- **LGPD:** opt-in obrigatório (`400` se `consent_lgpd=false`), bloqueio de disparo em `opt_out`, direitos de exportação e exclusão (`test_08`, `test_31`, `test_41`).
- **Zero Tokens em URL:** verificado em `0` ocorrências nos 6 scripts Chrome CDP (`url_token_leaks_count: 0`).

## 2. Gaps Conhecidos (Explicando Score 90/100 em Security e 93/100 em LGPD)

1. Autenticação do frontend ainda armazena JWT em `localStorage` (sem migração para cookies `HttpOnly` + `SameSite` + MFA TOTP ainda).
2. Portal público self-service de gestão de preferências LGPD previsto para fases futuras.
