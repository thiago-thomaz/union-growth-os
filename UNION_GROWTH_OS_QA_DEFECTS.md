# UNION GROWTH OS — RELATÓRIO DE DEFEITOS ENCONTRADOS E CORRIGIDOS (FASE 20)

**Projeto:** UNION GROWTH OS  
**Repositório:** `https://github.com/thiago-thomaz/union-growth-os` (`main`)  
**Ambiente de Produção:** `https://automacao.projetosunion.cloud` (`https://uniongrowth.72.62.13.62.sslip.io`)  
**Status Consolidado de Defeitos:** **0 P0 | 4 P1 Corrigidos | 1 P2 Corrigido | 0 Pendentes**

---

## Resumo Executivo de Defeitos

| ID | Severidade | Módulo | Título da Falha | Status Final | Teste de Regressão |
|---|---|---|---|---|---|
| **DEFECT-01** | **P1 (Alta)** | Backend / Roteamento SPA | Rota catch-all `serve_spa` retornava `HTTP 200 (index.html)` para endpoints `/api/*` `GET` inexistentes | **CORRIGIDO & VALIDADO EM PRODUÇÃO** | `test_44_phase20_qa_defects_security_and_e2e_15_scenarios` |
| **DEFECT-02** | **P1 (Alta)** | Segurança / Multi-Tenant | Header `X-Tenant-Id` de tenant não pertencente ao usuário era ignorado silenciosamente (`HTTP 200`) em vez de retornar `HTTP 403 Forbidden` | **CORRIGIDO & VALIDADO EM PRODUÇÃO** | `test_44_phase20_qa_defects_security_and_e2e_15_scenarios` |
| **DEFECT-03** | **P1 (Alta)** | Comercial / Propostas PDF | Botão `PDF` em Propostas Comerciais (`<a href={p.pdf_url} target="_blank">`) abria nova aba sem token JWT e falhava com `HTTP 401` | **CORRIGIDO & VALIDADO EM PRODUÇÃO** | `test_44_phase20_qa_defects_security_and_e2e_15_scenarios` |
| **DEFECT-04** | **P1 (Alta)** | Comercial / Landing Pages & LGPD | URLs públicas `/lp/{slug}` caíam no login administrativo da SPA, sem rota pública de captura nem sanitização explícita de `<script>` no serviço de captura | **CORRIGIDO & VALIDADO EM PRODUÇÃO** | `test_44_phase20_qa_defects_security_and_e2e_15_scenarios` |
| **DEFECT-05** | **P2 (Média)** | Frontend / Menu 09 Piloto 7 Dias | `loadAllActiveData()` não carregava `GET /api/v1/system/pilot-7-days` na inicialização do painel | **CORRIGIDO & VALIDADO EM PRODUÇÃO** | `test_44_phase20_qa_defects_security_and_e2e_15_scenarios` |
| **HIST-P1-01** | **P1 (Alta)** | UNION AI ENGINE HUB / Gemini | Chave Google AI Studio 2026 (`AQ....rlw`) retornava `HTTP 404` no alias legado `gemini-2.5-flash` e sofria latência alta em `gemini-flash-latest` | **CORRIGIDO (Commit `5cb052e`)** | `test_43_phase19_union_ai_engine_hub_complete_suite` |

---

## Detalhamento Técnico de Cada Defeito

### 1. `DEFECT-01` — Rota Catch-All da SPA Mascarando Endpoints `/api/*` Inexistentes com `HTTP 200`
- **Severidade:** `P1`
- **Módulo:** Backend FastAPI (`backend/app/main.py`)
- **Passos para Reproduzir (Antes da Correção):**
  1. Enviar `GET https://automacao.projetosunion.cloud/api/v1/rota-inexistente`
  2. Observar resposta `HTTP 200 OK` com `Content-Type: text/html; charset=utf-8` (conteúdo do `frontend/out/index.html`).
- **Resultado Esperado:** Resposta `HTTP 404 Not Found` em formato `application/json`.
- **Resultado Obtido (Antes da Correção):** `HTTP 200 OK` (`text/html`).
- **Causa Raiz:** O handler `@app.get("/{full_path:path}") async def serve_spa(full_path: str)` servia `index.html` para qualquer caminho não estático, inclusive caminhos iniciados por `api/`.
- **Correção Aplicada (`backend/app/main.py`):**
  - Adicionada verificação no início de `serve_spa`: se `normalized == "api" or normalized.startswith("api/")`, retorna imediatamente `JSONResponse(status_code=404, content={"detail": f"Endpoint API não encontrado: /{normalized}"})`.
- **Evidência Pós-Correção:** `UNION_GROWTH_OS_QA_EVIDENCE/security/defects_and_security_validation.json` (`DEFECT_01_unmatched_api_returns_json_404.passed = true`).

---

### 2. `DEFECT-02` — Falha de Rejeição Explícita (`HTTP 403`) em Tentativa de Acesso Cross-Tenant via `X-Tenant-Id`
- **Severidade:** `P1`
- **Módulo:** Segurança & Autenticação (`backend/app/core/security.py`)
- **Passos para Reproduzir (Antes da Correção):**
  1. Autenticar como usuário válido e enviar requisição com header `X-Tenant-Id: 999999` (tenant pertencente a terceiros ou inexistente) ou `X-Tenant-Id: 1 OR 1=1`.
  2. Observar que o sistema ignorava o header silenciosamente e retornava `HTTP 200` com os dados do tenant padrão do usuário.
- **Resultado Esperado:** Bloqueio explícito com `HTTP 403 Forbidden` sempre que `X-Tenant-Id` for malformado ou apontar para uma organização que não pertença ao `owner` autenticado.
- **Resultado Obtido (Antes da Correção):** `HTTP 200 OK` (fallback silencioso).
- **Causa Raiz:** Em `get_current_user` (`backend/app/core/security.py`), a condição `if t: user.active_tenant_override = requested_tid` não possuía cláusula `else` para lançar `HTTPException(status_code=403)`.
- **Correção Aplicada (`backend/app/core/security.py`):**
  - Validação estrita do header `X-Tenant-Id`: valores não numéricos ou IDs de tenants cujo `owner_email` não corresponda ao usuário autenticado (ou usuário sem papel `owner`) disparam imediatamente `HTTP 403 Forbidden`.
- **Evidência Pós-Correção:** `UNION_GROWTH_OS_QA_EVIDENCE/security/defects_and_security_validation.json` (`DEFECT_02_cross_tenant_header_blocked_403.passed = true`).

---

### 3. `DEFECT-03` — Botão `PDF` de Proposta Comercial Retornando `HTTP 401` ao Abrir em Nova Aba do Navegador
- **Severidade:** `P1`
- **Módulo:** Frontend (`frontend/src/app/page.tsx`) & Backend (`backend/app/core/security.py`)
- **Passos para Reproduzir (Antes da Correção):**
  1. Acessar Menu `23 🏛️ Sistema Comercial (3 Unidades)` -> `Propostas Comerciais`.
  2. Clicar no botão `PDF` (`<a href="/api/v1/commercial/proposals/1/pdf" target="_blank">`).
  3. A nova aba do navegador envia `GET` sem o header `Authorization: Bearer <token>`, recebendo `HTTP 401 {"detail":"Autenticação necessária. Forneça Bearer Token."}`.
- **Resultado Esperado:** Abertura da versão imprimível HTML/PDF da proposta comercial em nova aba com `HTTP 200 OK`.
- **Resultado Obtido (Antes da Correção):** `HTTP 401 Unauthorized` na nova aba.
- **Causa Raiz:** Links HTML nativos `<a target="_blank">` não anexam o token JWT salvo no `localStorage`.
- **Correção Aplicada:**
  - Em `backend/app/core/security.py` (`get_current_user`), adicionado suporte seguro a fallback `request.query_params.get("access_token")` quando o header `Authorization` não estiver presente.
  - Em `frontend/src/app/page.tsx`, atualizado o link do botão `PDF` para `${p.pdf_url}?access_token=${encodeURIComponent(token || "")}`.
- **Evidência Pós-Correção:** `UNION_GROWTH_OS_QA_EVIDENCE/screenshots/04_proposal_printable_pdf_view.png` e `DEFECT_03_proposal_pdf_browser_link_with_access_token.passed = true`.

---

### 4. `DEFECT-04` — Landing Pages Públicas `/lp/{slug}` Sem Renderização Pública Independente e Sanitização XSS na Captura
- **Severidade:** `P1`
- **Módulo:** Backend (`backend/app/main.py`, `backend/app/api/routes.py`, `backend/app/services/phase17_commercial_engine.py`)
- **Passos para Reproduzir (Antes da Correção):**
  1. Acessar `https://automacao.projetosunion.cloud/lp/agentes-ia` como visitante anônimo.
  2. A requisição caía no `serve_spa` e exibia a tela de login administrativo em vez da Landing Page pública de captura.
- **Resultado Esperado:** Renderização pública de `/lp/{slug}` com incremento de `views_count`, formulário interativo com checkbox obrigatório de consentimento LGPD, endpoint público `POST /api/v1/public/landing-pages/{slug}/capture` protegido por Rate Limit e sanitização XSS (`sanitize_text`).
- **Resultado Obtido (Antes da Correção):** Tela de login da SPA e endpoint `/api/v1/commercial/landing-pages/capture-lead` exigindo token administrativo.
- **Causa Raiz:** Ausência de rota pública `GET /lp/{slug}` em `main.py` e endpoint público de submissão sem `Depends(get_current_user)`. Além disso, `capture_lead_from_landing_page` fazia `.strip()` sem aplicar `sanitize_text()` nos campos de texto livre.
- **Correção Aplicada:**
  - Criada função `render_public_landing_page_html(lp)` e sanitização completa via `sanitize_text()` em `capture_lead_from_landing_page` (`backend/app/services/phase17_commercial_engine.py`).
  - Criada rota pública `GET /lp/{slug}` em `backend/app/main.py` e rota pública `POST /api/v1/public/landing-pages/{slug}/capture` em `backend/app/api/routes.py`.
- **Evidência Pós-Correção:** `UNION_GROWTH_OS_QA_EVIDENCE/screenshots/02_public_landing_page_agentes_ia.png`, `03_public_landing_page_union_tech.png` e `DEFECT_04_public_landing_page_and_lgpd_enforcement.passed = true`.

---

### 5. `DEFECT-05` — Histórico do Menu `09 🚀 Piloto 7 Dias` Não Carregado na Inicialização (`loadAllActiveData`)
- **Severidade:** `P2`
- **Módulo:** Frontend (`frontend/src/app/page.tsx`)
- **Passos para Reproduzir (Antes da Correção):**
  1. Executar o Piloto de 7 Dias e recarregar a página (`F5`).
  2. Abrir o Menu `09 🚀 Piloto 7 Dias` e notar que `pilotData` iniciava `null` até clicar novamente no botão de execução.
- **Resultado Esperado:** Carregamento automático do histórico persistido em `GET /api/v1/system/pilot-7-days` ao abrir o dashboard.
- **Causa Raiz:** `apiFetch("/api/v1/system/pilot-7-days")` não estava incluído no `Promise.all` de `loadAllActiveData()`.
- **Correção Aplicada (`frontend/src/app/page.tsx`):**
  - Incluído `apiFetch("/api/v1/system/pilot-7-days").catch(() => null)` no `Promise.all` de `loadAllActiveData()` com atualização automática de `setPilotData(pilotRes)`.
- **Evidência Pós-Correção:** Build estático Next.js regenerado e `DEFECT_05_pilot_7_days_history_endpoint.passed = true`.
