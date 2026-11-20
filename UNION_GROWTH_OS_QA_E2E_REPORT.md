# UNION GROWTH OS — RELATÓRIO DE TESTES END-TO-END (15 CENÁRIOS DE NEGÓCIO — FASE 20)

**Projeto:** UNION GROWTH OS  
**Tenant Isolado de Teste:** `QA_AUTOMATED_TENANT` (sem contaminação dos dados reais do Tenant Principal)  
**Execução em Produção:** `https://automacao.projetosunion.cloud` + Suite Automatizada `test_44_phase20_qa_defects_security_and_e2e_15_scenarios`  
**Arquivos de Evidência:** `UNION_GROWTH_OS_QA_EVIDENCE/e2e/e2e_15_scenarios_live_results.json`

---

## Resumo dos 15 Cenários E2E Executados

| Cenário | Nome do Fluxo de Negócio | Modo de Execução | Status Final | Verificação em Banco de Dados (PostgreSQL 16) |
|---|---|---|---|---|
| **CENÁRIO 01** | Captação de Lead via Landing Page + Consentimento LGPD | **TESTE REAL** | **PASS (REAL)** | Lead criado em `crm_leads` com `consent_lgpd=True`, `legal_basis` registrado e contador da LP incrementado. |
| **CENÁRIO 02** | Qualificação Automática e Lead Scoring (0–100) | **TESTE REAL** | **PASS (REAL)** | Score calculado deterministicamente (`lead_score = 92`), `qualification_status = QUALIFIED`, estágio `QUALIFICADO`. |
| **CENÁRIO 03** | Progressão de Funil CRM (10 Etapas), Empresa e Oportunidade | **TESTE REAL** | **PASS (REAL)** | Transições `QUALIFICADO -> DIAGNOSTICO -> PROPOSTA -> NEGOCIACAO` persistidas em `crm_leads` e empresa criada em `crm_companies`. |
| **CENÁRIO 04** | Campanha de Marketing, Copywriting A/B, Criativo e Calendário Editorial | **TESTE REAL** | **PASS (REAL)** | Registros criados e vinculados em `marketing_campaigns`, `copy_items`, `creative_assets` e `editorial_calendar_items`. |
| **CENÁRIO 05** | UNION AI ENGINE HUB (Gemini Gratuito Real + Trava `FREE_ONLY`) | **TESTE REAL (Gemini API)** | **PASS (REAL)** | Execução real no Google Gemini (`gemini-3.5-flash-lite`, `status: SUCCESS`, `VERIFIED_FREE`, `R$ 0,00`) e bloqueio automático de motor pago (`gpt-4o` -> `BLOCKED_FREE_ONLY`). |
| **CENÁRIO 06** | Geração de Proposta Comercial + Visualização PDF Imprimível | **TESTE REAL** | **PASS (REAL)** | Proposta criada em `commercial_proposals` (`status: PENDING_APPROVAL`) e PDF HTML renderizado com `HTTP 200` via `?access_token=`. |
| **CENÁRIO 07** | Governança de Aprovação Humana (RBAC & Trava do Proprietário) | **TESTE REAL** | **PASS (REAL)** | Tentativa de envio sem aprovação (`owner_approve=False`) bloqueada com `HTTP 403`; aprovação com `owner_approve=True` transiciona para `ACCEPTED` e gera `AuditLog`. |
| **CENÁRIO 08** | Aceite Formal de Contrato Digital | **TESTE REAL** | **PASS (REAL)** | `POST /api/v1/commercial/proposals/{id}/contract-accept` atualiza `contract_status = ACCEPTED` com evidência de aceite registrada. |
| **CENÁRIO 09** | Cobrança, Webhook HMAC-SHA256, Idempotência e Rejeição de Fraude | **TESTE SANDBOX** | **PASS (SANDBOX)** | Cobrança PIX criada em `payment_transactions`; assinatura inválida rejeitada com `HTTP 401`; assinatura HMAC válida aprova pagamento sem duplicar em reenvios. |
| **CENÁRIO 10** | Onboarding Automático Pós-Pagamento | **TESTE REAL** | **PASS (REAL)** | Webhook `APPROVED` dispara criação automática de projeto em `service_delivery_projects` com checklist e entregáveis do serviço contratado. |
| **CENÁRIO 11** | Entrega de Projeto com Evidência Auditável Obrigatória | **TESTE REAL** | **PASS (REAL)** | Tentativa de concluir projeto com `delivery_evidence=""` bloqueada com `HTTP 400`; conclusão com URL de evidência atinge `status = COMPLETED` (`100%`). |
| **CENÁRIO 12** | Isolamento Financeiro dos 5 Buckets (Receita Real vs Simulação/Teste) | **TESTE REAL** | **PASS (REAL)** | Pagamento `SANDBOX`/`TEST` de `R$ 6.800,00` contabilizado exclusivamente no Bucket 4 (`4_simulation_and_test_brl`), mantendo Bucket 1 (`1_confirmed_real_revenue_brl = R$ 0,00`) intacto no tenant de QA. |
| **CENÁRIO 13** | Pós-Venda / Customer Success (Coleta de NPS e Retenção) | **TESTE REAL** | **PASS (REAL)** | Avaliação `nps_score = 10` (`PROMOTER`) persistida em `customer_feedbacks` e refletida nos KPIs de CS. |
| **CENÁRIO 14** | Consistência entre Dashboard Executivo e Banco de Dados | **TESTE REAL** | **PASS (REAL)** | `GET /api/v1/dashboard/overview` no `QA_AUTOMATED_TENANT` reflete exatamente os leads, campanhas e registros criados na sessão. |
| **CENÁRIO 15** | Relatório Executivo Semanal e Integridade de Backup | **TESTE REAL** | **PASS (REAL)** | Relatório Markdown gerado em `executive_reports` e lista de backups verificados consultada em `/api/v1/system/backups`. |
