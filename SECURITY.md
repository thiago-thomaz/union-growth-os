# Política de Segurança e Governança (SECURITY.md) — UNION GROWTH OS

## 1. Autenticação e Controle de Acesso (RBAC)

- Senhas armazenadas exclusivamente com hash **bcrypt** (`rounds=10`).
- Sessões autenticadas via **JWT Bearer Token** (`HS256`) com expiração configurável.
- Controle de acesso baseado em papéis (**RBAC**): `owner`, `admin`, `manager`, `analyst`, `viewer`.
- Isolamento rigoroso **Multi-Tenant**: todas as consultas SQL filtram obrigatoriamente por `tenant_id`.

---

## 2. Criptografia de Segredos e Credenciais de Terceiros

- Nenhum token OAuth ou chave de API é armazenado em texto puro ou no código-fonte.
- Todas as credenciais cadastradas na **Central de Integrações** são criptografadas em repouso utilizando **Fernet (`cryptography.fernet`)** derivado de `ENCRYPTION_KEY`.
- A interface exibe apenas versões mascaradas (`abc...xyz`).

---

## 3. Governança LGPD e Proteção de Dados

- Cadastro de leads no CRM exige flag explícita `consent_lgpd=true` e registro da origem do consentimento (`consent_source`).
- Disparo em massa sem consentimento é bloqueado por design.
- Suporte a `opt_out` imediato e gestão de preferências de privacidade (`PUT /api/v1/auth/lgpd-preferences`).

---

## 4. Proteção de Endpoints e Confirmação de Alto Impacto

- **Sanitização Anti-XSS**: remoção de tags `<script>`, handlers `on*` e escape HTML em entradas de texto.
- **Proteção contra SQL Injection**: uso exclusivo de queries parametrizadas via SQLAlchemy ORM.
- **Rate Limiting**: janela deslizante por IP (`RATE_LIMIT_PER_MINUTE`).
- **Headers de Segurança**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`.
- **Trava de Alto Impacto**: criação de campanhas com gasto financeiro ou aprovação de ações críticas exige token de confirmação HMAC (`CONFIRM-...`) ou aprovação explícita na Central de Aprovações.
