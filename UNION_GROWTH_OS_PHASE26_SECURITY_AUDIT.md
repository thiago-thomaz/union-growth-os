# UNION GROWTH OS — FASE 26: SECURITY & LGPD AUDIT

**Versão:** `2.3.0 — FASE 26`  

## 1. Controles Ativos Validados em Código & Testes
- **Autenticação & Hash:** `bcrypt` + JWT `HS256` assinado (`EXPIRATION` configurado), rotacionado a partir de defaults antigos (`test_02a`), com bloqueio brute-force de login (`rate_limited`).
- **Isolamento Multi-Tenant Estrito:** header `X-Tenant-Id` validado contra vínculos do usuário (`403` em tentativas cruzadas, testado em `test_03` e `E2E J19`).
- **RBAC por Perfil:** `viewer` bloqueado com `HTTP 403` em mutações (`/growth-os/brand`, `/growth-os/actions/decide`, `/automations/conversational-build`, `/onboarding`, `/autonomy/limits`).
- **Anti-SSRF:** `validate_public_http_url` / `safe_public_http_get` bloqueiam `127.0.0.1`, `localhost`, IPs privados RFC1918 e metadados cloud (`169.254.169.254`) com `HTTP 400`.
- **Criptografia de Credenciais & Higiene de URL:** segredos gravados via `Fernet AES-128`; zero `access_token=` ou `Bearer` exposto em query strings ou logs de auditoria (`url_token_leaks_count == 0`).
- **Governança LGPD no Revenue Engine:** `smart-followup` e `quick-followup` recusam contatos com `opt_out` ativo e exigem consentimento `consent_lgpd` na captura.

## 2. Itens em Roadmap de Segurança Enterprise
- Migração futura de armazenamento de JWT de `localStorage` para cookies `HttpOnly; SameSite=Lax; Secure`.
- Suporte a MFA (TOTP) e SSO SAML/OIDC para clientes `ENTERPRISE`.
