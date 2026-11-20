# FASE 20.1 — REVISÃO INDEPENDENTE DE SEGURANÇA, MULTI-TENANT E DEFECT-01..05

**Evidência Bruta:** `UNION_GROWTH_OS_PHASE20_1_EVIDENCE/security/phase20_1_security_and_defects.json` & `UNION_GROWTH_OS_PHASE20_1_EVIDENCE/frontend/phase20_1_cdp_browser_audit.json`  
**Status de Segurança Pós-Correções 20.1:** **APROVADO (`0` vulnerabilidades P0/P1 abertas)**

---

## 1. Descoberta e Remediação Crítica no `DEFECT-03` (Vazamento de JWT em URL)

### Problema Identificado pela Auditoria Independente
Na Fase 20, o botão `PDF` das propostas comerciais foi alterado para `<a href="/api/v1/commercial/proposals/{id}/pdf?access_token=<JWT>&tenant_id=<tid>" target="_blank">`, e `get_current_user` passou a aceitar `?access_token=` em qualquer endpoint.
- **Prova de Vazamento Real:** Nos logs do container em produção (`coolify:application_logs`), registrou-se literalmente `GET /api/v1/commercial/proposals/2/pdf?access_token=<REDACTED> HTTP/1.1 200 OK`, confirmando exposição do token JWT completo (validade 24h) em logs de acesso do servidor, histórico do navegador, cabeçalho `Referer` e capturas de tela.

### Arquitetura Segura Implementada na Fase 20.1
1. **Backend (`backend/app/core/security.py`):** Removido 100% o suporte a `access_token` e `tenant_id` via query string. Qualquer tentativa de enviar `?access_token=<JWT>` sem header `Authorization: Bearer` agora retorna imediatamente **`HTTP 401 Unauthorized`**.
2. **Backend (`backend/app/api/routes.py` e `backend/app/main.py`):** O endpoint `GET /api/v1/commercial/proposals/{proposal_id}/pdf` agora retorna cabeçalhos restritivos preservados pelo middleware global (`setdefault`):
   - `Cache-Control: no-store, private, max-age=0`
   - `Pragma: no-cache`
   - `Referrer-Policy: no-referrer`
   - `X-Robots-Tag: noindex, nofollow`
3. **Frontend (`frontend/src/app/page.tsx`):** Substituído o link `<a>` por um `<button>` que executa `fetch(p.pdf_url, { headers: { Authorization: "Bearer ...", "X-Tenant-Id": "..." } })`, converte o HTML autenticado em `Blob` local em memória e abre `URL.createObjectURL(blob)` (`blob:https://automacao.projetosunion.cloud/...`) com `noopener,noreferrer` e revogação automática (`URL.revokeObjectURL`).
4. **Comprovação ao Vivo (API + Chrome CDP):**
   - `GET /api/v1/commercial/proposals/{id}/pdf?access_token=...` -> **`HTTP 401`**
   - `GET /api/v1/commercial/proposals/{id}/pdf` com `Authorization` + `X-Tenant-Id` -> **`HTTP 200`** + `Cache-Control: no-store, private, max-age=0` + `Referrer-Policy: no-referrer`
   - `GET /api/v1/commercial/proposals/{id}/pdf` com `X-Tenant-Id: 999999` -> **`HTTP 403`**
   - Clique real no botão `PDF` no Chrome CDP -> abriu `blob:https://automacao.projetosunion.cloud/2fd09ae9-b060-4688-bee8-b6e9df465591` com **`url_token_leaks_count: 0`** em 96 requisições monitoradas.

---

## 2. Reauditoria Independente de Todos os 5 Defeitos + Endurecimentos da Fase 20.1

| Defeito / Vetor | Testes Independentes Executados | Resultado em Produção (`p201-8b05cfd6`) | Veredito |
|---|---|---|---|
| **DEFECT-01 + Probes Bot** | `GET/POST/DELETE /api/v1/inexistente-*`, `GET /api/v2/sub/inexistente`, `GET /wp-login.php`, `GET /.env`, `GET /.git/config` | **7/7 retornaram `HTTP 404` (`application/json`)** | **CORRIGIDO & COMPROVADO** |
| **DEFECT-02 (Multi-Tenant)** | `X-Tenant-Id: 999999`, `X-Tenant-Id: 1 OR 1=1`, usuário secundário registrado tentando acessar Tenant 1 (`test_45`), sem token, JWT forjado, JWT em query string | `403`, `403`, `403`, `401`, `401`, `401` (testado também em **136/136 rotas**!) | **CORRIGIDO & COMPROVADO** |
| **DEFECT-03 (PDF Seguro)** | Zero JWT em URL + `fetch` autenticado + `Blob` + `no-store` + `no-referrer` | `401` em URL token, `200` via Header, `blob:` no Chrome CDP, `0` leaks | **REMEDIADO & COMPROVADO** |
| **DEFECT-04 (Landing Pages Públicas)** | `GET /lp/agentes-ia` (`200 HTML` deslogado), `GET /lp/nao-existe` (`404`), captura sem LGPD (`400`), captura com `<script>alert(1)</script>` (sanitizado e persistido via readback DB), formulário verificado no Chrome CDP | Todos aprovados sem exceção | **CORRIGIDO & COMPROVADO** |
| **DEFECT-05 (Piloto 7 Dias)** | `GET /api/v1/system/pilot-7-days` (`200`, `days_simulated: 7`) + abertura do Menu `09` no Chrome CDP sem clicar em executar | Pré-carregado automaticamente no boot | **CORRIGIDO & COMPROVADO** |

---

## 3. Risco Residual Documentado (Transparência)

- **Rate Limiter em Memória (`_rate_buckets` em `security.py`):** Comprovadamente funcional (bloqueou com `HTTP 429` após 180 req/min durante a varredura local de rotas). Em arquitetura de réplica única (atual VPS/Coolify), é eficaz; caso o sistema escale para múltiplas réplicas/workers no futuro, recomenda-se migrar os contadores para Redis.
