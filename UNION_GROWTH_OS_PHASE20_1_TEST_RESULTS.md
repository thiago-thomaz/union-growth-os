# FASE 20.1 — RESULTADOS REPRODUZÍVEIS DE TESTES (BACKEND, E2E E NAVEGADOR REAL CDP)

**Execução E2E Independente (`run_id`):** `p201-8b05cfd6`  
**Commit em Produção Testado:** `bcca50ee8ad0e03770008122d24e4efa2e0f9cea`

---

## 1. Suíte Completa de Regressão Backend (`pytest`)

- **Comando executado:** `python -m pytest tests/test_union_growth_os.py -q --tb=short`
- **Resultado Real:** **`46 passed in 348.76s (0:05:48)`** (`0 failed`, `0 skipped`).
- **Observação de Auditoria:** A Fase 20 havia reportado `44/44` testes sem finalizar a execução completa após as edições; a suíte real continha `45` testes e agora conta com **`46` testes** após a inclusão de `test_45_phase20_1_security_zero_url_tokens_free_only_and_qa_isolation`, todos executados até o fim com `exit code 0`.
- **Qualidade das Assertions:** Os novos testes em `test_44` e `test_45` provaram sua capacidade de falhar diante de defeitos reais — durante a própria Fase 20.1, `test_44` detectou a sobrescrita de `Referrer-Policy` no middleware global e `test_45` detectou `HTTP 405` em `POST /api/v1/nao-existe`, ambos corrigidos em `backend/app/main.py`.

---

## 2. Reexecução Independente dos 15 Cenários E2E em Produção (`QA_AUTOMATED_TENANT`)

Evidência bruta: `UNION_GROWTH_OS_PHASE20_1_EVIDENCE/e2e/phase20_1_e2e_15_scenarios.json` (`run_id: p201-8b05cfd6`).  
**Resumo Estrito (Zero Falsos Positivos):** **`13 PASS (REAL)` | `1 PASS (SANDBOX)` | `1 BLOCKED (QUOTA_OR_BILLING_REQUIRED)` | `0 FAIL`**

| # | Cenário E2E | Classificação Honesta | Verificação Real de Persistência / Evidência (`p201-8b05cfd6`) |
|---|---|---|---|
| **01** | Captação de Lead + Sanitização XSS + Readback DB | **`PASS (REAL)`** | `HTTP 201` -> Lead criado no PostgreSQL 16 -> `GET /lgpd-export` confirmou persistência e remoção da tag `<script>alert(1)</script>`. |
| **02** | Qualificação Automática (Lead Score) | **`PASS (REAL)`** | `lead_score >= 65`, `qualification_status: QUALIFIED`. |
| **03** | CRM Pipeline (Progressão de Funil) | **`PASS (REAL)`** | `PUT /funnel-stage` -> `HTTP 200`, estágio `PROPOSTA` persistido. |
| **04** | Campanha de Marketing & Copywriting A/B | **`PASS (REAL)`** | `POST /marketing/campaigns` (`201`) e `POST /copywriter/generate` (`201`) com IDs persistidos. |
| **05** | UNION AI ENGINE HUB (`FREE_ONLY` + Gemini Live) | **`BLOCKED (QUOTA_OR_BILLING_REQUIRED)`** | Política `FREE_ONLY` bloqueou `5/5` motores pagos/desconhecidos (`BLOCKED_FREE_ONLY`), `test-connection` retornou `CONNECTED` (`322ms`), mas a geração ao vivo no Gemini retornou `HTTP 402` (`QUOTA_OR_BILLING_REQUIRED`, `R$ 0,00`) por cota esgotada da chave Express `AQ....rlw`. **Marcado honestamente como `BLOCKED`.** |
| **06** | Proposta Comercial + PDF Seguro (Zero Token em URL) | **`PASS (REAL)`** | Proposta criada (`201`); `?access_token=` rejeitado (`401`); header `Authorization` retornou `200` com `Cache-Control: no-store, private, max-age=0` e `Referrer-Policy: no-referrer`; cross-tenant bloqueado (`403`). |
| **07** | Governança de Aprovação Humana | **`PASS (REAL)`** | Envio sem aprovação (`owner_approve=False`) retornou `403`; com `owner_approve=True` retornou `200` (`SENT`). |
| **08** | Aceite Formal de Contrato | **`PASS (REAL)`** | `PUT /status` -> `200` (`ACCEPTED`) com evidência digital `Aceite Digital p201-8b05cfd6`. |
| **09** | Cobrança PIX, Webhook HMAC-SHA256 & Idempotência | **`PASS (SANDBOX)`** | Cobrança criada (`201`), assinatura forjada rejeitada (`401`), HMAC válida aprovada (`200`), replay detectado (`idempotent_duplicate: true`), projeto de onboarding criado. **Classificado estritamente como `SANDBOX`, não pagamento bancário real.** |
| **10** | Onboarding Automático Pós-Pagamento | **`PASS (REAL)`** | `GET /commercial/delivery-projects` confirmou persistência do projeto criado pelo webhook. |
| **11** | Entrega com Evidência Auditável Obrigatória | **`PASS (REAL)`** | Conclusão sem evidência bloqueada (`400`); concluído (`COMPLETED`, `100.0%`) após envio de URL de evidência. |
| **12** | Isolamento Financeiro nos 5 Buckets | **`PASS (REAL)`** | `REAL.receita_recebida_confirmada_brl == 0.0` (sem contaminação), `SIMULACAO.cobrancas_sandbox_total >= 1`. |
| **13** | Customer Success / NPS Pós-Venda | **`PASS (REAL)`** | `POST /customer-success/feedbacks` -> `201`, `churn_risk: LOW`. |
| **14** | Consistência do Dashboard vs Banco | **`PASS (REAL)`** | `GET /dashboard/overview` no `QA_AUTOMATED_TENANT` retornou `0` leads reais (excluindo corretamente todos os leads `data_origin="TEST"`). |
| **15** | Relatório Executivo & Backup Verificado | **`PASS (REAL)`** | `GET /reports/executive` (`200`) e `POST /system/backup` (`201`, arquivo gerado e validado). |

---

## 3. Auditoria Real de Frontend via Chrome DevTools Protocol (CDP)

Evidência bruta: `UNION_GROWTH_OS_PHASE20_1_EVIDENCE/frontend/phase20_1_cdp_browser_audit.json` + 6 screenshots Full HD (`1920x1080`).

| Verificação Real no Navegador Chrome | Resultado Medido em Produção | Status |
|---|---|---|
| **Login Real via Formulário DOM** | Autenticação bem-sucedida (`admin@projetosunion.cloud`) | **PASS** |
| **Card "Leads no CRM" no Tenant 1 (Domínio Real)** | Renderizou **`2` (DADO REAL)** — comprovando exclusão dos 3 leads `TEST` | **PASS** |
| **Navegação Real por Todos os Menus Laterais** | **`26 / 26` menus** (`01..25` + `17M Multinegócio`) clicados e renderizados | **PASS** |
| **Auditoria Estática de Botões (`page.tsx`)** | `79 / 79` botões possuem handler `onClick` ou `type="submit"` (`0` mortos) | **PASS** |
| **Menu `09 Piloto 7 Dias` (DEFECT-05)** | Histórico de 7 dias já pré-carregado automaticamente no boot | **PASS** |
| **Menu `17M Multinegócio` + Troca de Tenant + Clique Real em `PDF`** | Abriu `blob:https://automacao.projetosunion.cloud/2fd09ae9-b060-4688-bee8-b6e9df465591` (Header `Authorization`, **`0` `access_token` em URLs**) | **PASS** |
| **Menu `25 UNION AI ENGINE HUB` + Sub-abas** | Badge `FREE_ONLY`, motor `GEMINI`, sub-aba `2. Provedores` com máscara `AQ....rlw`, sub-aba `9. Histórico` renderizadas | **PASS** |
| **Logout Real** | Retornou imediatamente à tela de login com formulário de senha | **PASS** |
| **Landing Page Pública `/lp/agentes-ia` (Deslogado)** | Renderizou LP pública completa com formulário e checkbox LGPD `required` | **PASS** |
| **Telemetria Chrome DevTools (`96` requests observados)** | **`0` erros de Console | `0` Exceções JS | `0` falhas HTTP 4xx/5xx | `0` vazamentos de token em URL** | **PASS** |
