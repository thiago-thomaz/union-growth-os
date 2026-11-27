# UNION GROWTH OS — FASE 25: RELATÓRIO DE SEGURANÇA, PRIVACIDADE & LGPD

**Auditoria Ao Vivo Consultada:** `GET https://automacao.projetosunion.cloud/api/v1/security/audit` + testes `test_23`, `test_24`, `test_44`, `test_45`, `test_48`, `test_49`, `test_50` + Chrome CDP `J19` / `J20`.

---

## 1. Controles Confirmados em Produção
| Controle | Estado Real Observado |
| :--- | :--- |
| **Chaves de Assinatura JWT/Cripto** | `default_signing_secrets_in_use: false` (variáveis próprias em produção) |
| **Senha Padrão Insegura / Rotação** | `users_with_invalidated_default_password_still_valid: 0`, `users_requiring_password_change: 0` |
| **Hashing de Senhas** | `bcrypt (rounds=10)` |
| **Sessão / Token** | `HS256, expira em 1440 min` |
| **Criptografia de Credenciais BYO / Integrações** | `Fernet (AES-128-CBC + HMAC)` — chaves nunca retornam abertas na UI (`AQ....rlw` mascarado) |
| **Proteção Brute-Force Login** | `8 falhas / 5 min por IP+e-mail` (`test_24` e `test_48` validam isolamento sem confiar em spoof de `X-Forwarded-For` não autorizado) |
| **Rate Limit Global** | `600 req/min` |
| **CORS Restrito** | Lista explícita de 5 origens autorizadas (`automacao.projetosunion.cloud`, `uniongrowth.72.62.13.62.sslip.io`, `growth.projetosunion.cloud`, `localhost:3000`, `localhost:8000`) |
| **Anti-SSRF em SEO / Webhooks** | `validate_public_http_url` / `safe_public_http_get` bloqueiam `127.0.0.1`, redes privadas e IPs metadata cloud com HTTP `400` (`test_49` e `J20`) |
| **Isolamento Multi-Tenant & RBAC** | Consultas filtram `tenant_id`; `X-Tenant-Id` inválido ou alheio devolve HTTP `403` (`J19`); `viewer` bloqueado de mutações (`test_50`) |
| **LGPD Nativa** | Captura de leads exige consentimento explícito; leads marcados em `opt_out` bloqueiam `POST /api/v1/crm/leads/{lead_id}/quick-followup`; direitos do titular validados em `test_41` |
| **Scanner de Segredos no CI** | Corrigido na Fase 25 ([ci-cd.yml](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/.github/workflows/ci-cd.yml)) usando regex para tokens sem manter strings literais sensíveis no YAML |

---

## 2. Gaps de Segurança Restantes para Padrão Enterprise Global (SOC 2 / ISO)
1. **Armazenamento do Token JWT no Browser (`localStorage.ug_token`)**: embora haja zero vazamento de token na URL (`url_token_leaks_count: 0`) e PDFs usem `Blob URL`, `HttpOnly Secure SameSite=Lax` em cookies reduziria a superfície contra qualquer XSS futuro.
2. **MFA / TOTP (2FA)** e **SSO (SAML / Google Workspace OIDC)**: ainda não implementados; importantes para vendas no segmento Enterprise internacional.
3. **Auto Deploy Webhook Secret no GitHub**: `COOLIFY_API_TOKEN` / `COOLIFY_DEPLOY_WEBHOOK` permanecem pendentes de cadastro manual pelo proprietário no painel do GitHub (sem expor tokens no repositório).
