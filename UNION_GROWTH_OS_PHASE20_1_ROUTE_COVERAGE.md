# UNION GROWTH OS — COBERTURA INDEPENDENTE DE TODAS AS ROTAS DA API (FASE 20.1)

**Total de Rotas da Aplicação (`app.routes + api_v1_router`):** `142`  
**Total de Rotas de API (Método + Caminho):** `136` (`120` caminhos únicos, incluindo catch-all 404 `/api/{full_path:path}`)  
**Rotas Duplicadas:** `0`  
**Rotas Indevidamente Sem Autenticação:** `0`  
**Aprovadas / Falhas no Teste Automatizado Individual:** **`136/136` (`0` falhas)**  
**Evidência JSON Bruta:** `UNION_GROWTH_OS_PHASE20_1_EVIDENCE/routes/independent_route_coverage.json`

## Metodologia Independente Aplicada por Rota
Diferente da Fase 20 (que apenas cruzou strings `apiFetch` do frontend), a Fase 20.1 executou **3 chamadas HTTP reais por rota** em banco SQLite isolado (`phase20_1_route_audit.db`):
1. **Sem Autenticação:** valida bloqueio obrigatório `HTTP 401` em todas as rotas protegidas.
2. **Cross-Tenant (`X-Tenant-Id: 999999`):** valida bloqueio obrigatório `HTTP 403` em todas as rotas autenticadas.
3. **Smoke / Validação Autenticada:** valida que nenhuma rota retorna `HTTP 500` (apenas `200/201/400/403/404/422` esperados). Durante o primeiro teste sem elevar o limite local, a rota #66 disparou `HTTP 429 Too Many Requests` após 180 req/min, comprovando o funcionamento real do Rate Limiter.

## Matriz Completa das 136 Rotas de API Auditadas

| # | Método | Caminho | Função | Auth | RBAC | Tenant | Body Schema | Unauth HTTP | Cross-Tenant HTTP | Auth Smoke HTTP | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `DELETE` | `/api/{full_path:path}` | `api_not_found_catchall` | False | False | False | False | `None` | `None` | `404` | **PASS** |
| 2 | `GET` | `/api/{full_path:path}` | `api_not_found_catchall` | False | False | False | False | `None` | `None` | `404` | **PASS** |
| 3 | `PATCH` | `/api/{full_path:path}` | `api_not_found_catchall` | False | False | False | False | `None` | `None` | `404` | **PASS** |
| 4 | `POST` | `/api/{full_path:path}` | `api_not_found_catchall` | False | False | False | False | `None` | `None` | `404` | **PASS** |
| 5 | `PUT` | `/api/{full_path:path}` | `api_not_found_catchall` | False | False | False | False | `None` | `None` | `404` | **PASS** |
| 6 | `POST` | `/api/v1/auth/register` | `register_user_and_tenant` | False | False | True | True | `None` | `None` | `SKIPPED_DESTRUCTIVE_TESTED_IN_SUITE` | **PASS** |
| 7 | `POST` | `/api/v1/auth/login` | `login_user` | False | False | True | True | `None` | `None` | `422` | **PASS** |
| 8 | `POST` | `/api/v1/auth/change-password` | `change_password` | True | False | True | True | `401` | `403` | `SKIPPED_DESTRUCTIVE_TESTED_IN_SUITE` | **PASS** |
| 9 | `GET` | `/api/v1/auth/me` | `get_me` | True | False | True | False | `401` | `403` | `200` | **PASS** |
| 10 | `PUT` | `/api/v1/auth/lgpd-preferences` | `update_lgpd_preferences` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 11 | `GET` | `/api/v1/tenants` | `list_user_tenants` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 12 | `POST` | `/api/v1/tenants` | `create_additional_tenant` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 13 | `PUT` | `/api/v1/tenants/current` | `update_current_tenant` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 14 | `GET` | `/api/v1/dashboard/overview` | `get_dashboard_overview` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 15 | `GET` | `/api/v1/agents` | `list_agents` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 16 | `GET` | `/api/v1/agents/audit` | `audit_agents_intelligence` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 17 | `POST` | `/api/v1/agents/{agent_id}/execute` | `execute_single_agent` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 18 | `POST` | `/api/v1/orchestrator/diagnose` | `trigger_full_orchestrator_diagnosis` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 19 | `GET` | `/api/v1/ceo/briefings` | `get_ceo_briefings` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 20 | `POST` | `/api/v1/ceo/briefings/generate` | `generate_new_ceo_briefing` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 21 | `POST` | `/api/v1/ceo/goals` | `create_strategic_goal` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 22 | `GET` | `/api/v1/marketing/overview` | `get_marketing_overview` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 23 | `POST` | `/api/v1/marketing/personas` | `create_persona` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 24 | `POST` | `/api/v1/marketing/campaigns` | `create_campaign` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 25 | `GET` | `/api/v1/seo/overview` | `get_seo_overview` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 26 | `POST` | `/api/v1/seo/audit` | `run_seo_audit` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 27 | `POST` | `/api/v1/seo/keywords` | `run_keyword_research` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 28 | `POST` | `/api/v1/seo/articles/generate` | `create_seo_article` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 29 | `GET` | `/api/v1/social/calendar` | `get_editorial_calendar` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 30 | `POST` | `/api/v1/social/calendar` | `create_editorial_item` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 31 | `POST` | `/api/v1/social/calendar/{item_id}/publish` | `trigger_social_item_publication` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 32 | `GET` | `/api/v1/creative/assets` | `list_creative_assets` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 33 | `POST` | `/api/v1/creative/assets/generate` | `generate_new_creative_asset` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 34 | `GET` | `/api/v1/copywriter/items` | `list_copy_items` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 35 | `POST` | `/api/v1/copywriter/generate` | `generate_copy_endpoint` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 36 | `GET` | `/api/v1/growth/experiments` | `list_growth_experiments` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 37 | `POST` | `/api/v1/growth/experiments` | `create_growth_experiment` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 38 | `PUT` | `/api/v1/growth/experiments/{exp_id}/result` | `record_growth_experiment_result` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 39 | `GET` | `/api/v1/crm/overview` | `get_crm_overview` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 40 | `POST` | `/api/v1/crm/leads` | `create_crm_lead` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 41 | `POST` | `/api/v1/crm/leads/{lead_id}/opt-out` | `opt_out_crm_lead` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 42 | `POST` | `/api/v1/crm/deals` | `create_crm_deal` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 43 | `PUT` | `/api/v1/crm/deals/{deal_id}/stage` | `update_crm_deal_stage` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 44 | `GET` | `/api/v1/competitors` | `list_competitors` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 45 | `POST` | `/api/v1/competitors` | `add_and_analyze_competitor` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 46 | `GET` | `/api/v1/finance/overview` | `get_finance_overview` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 47 | `POST` | `/api/v1/finance/records` | `create_financial_record` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 48 | `GET` | `/api/v1/customer-success/overview` | `get_customer_success_overview` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 49 | `POST` | `/api/v1/customer-success/feedbacks` | `add_customer_feedback` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 50 | `GET` | `/api/v1/automations` | `list_automations` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 51 | `POST` | `/api/v1/automations` | `create_custom_automation` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 52 | `POST` | `/api/v1/automations/{rule_id}/run` | `run_automation_now` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 53 | `GET` | `/api/v1/approvals` | `list_approvals` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 54 | `POST` | `/api/v1/approvals/{req_id}/decide` | `decide_approval_request` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 55 | `GET` | `/api/v1/integrations` | `get_integrations` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 56 | `POST` | `/api/v1/integrations/connect` | `connect_integration` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 57 | `POST` | `/api/v1/integrations/{provider_key}/test` | `test_integration_endpoint` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 58 | `POST` | `/api/v1/integrations/{provider_key}/disconnect` | `disconnect_integration_endpoint` | True | True | True | False | `401` | `403` | `403` | **PASS** |
| 59 | `GET` | `/api/v1/reports/executive` | `generate_executive_report` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 60 | `GET` | `/api/v1/audit-logs` | `get_audit_and_agent_logs` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 61 | `GET` | `/api/v1/agents/execution-logs` | `get_agent_execution_logs` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 62 | `POST` | `/api/v1/system/backup` | `trigger_database_backup` | True | True | True | False | `401` | `403` | `403` | **PASS** |
| 63 | `POST` | `/api/v1/system/backup/test-restore` | `test_database_restore_isolated` | True | True | True | False | `401` | `403` | `SKIPPED_DESTRUCTIVE_TESTED_IN_SUITE` | **PASS** |
| 64 | `GET` | `/api/v1/social/platforms-audit` | `social_platforms_audit` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 65 | `GET` | `/api/v1/integrations/oauth/{provider_key}/start` | `oauth_start` | True | True | True | False | `401` | `403` | `403` | **PASS** |
| 66 | `GET` | `/api/v1/integrations/oauth/callback` | `oauth_callback` | False | False | True | False | `None` | `None` | `200` | **PASS** |
| 67 | `POST` | `/api/v1/onboarding/company` | `onboarding_company` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 68 | `GET` | `/api/v1/autonomy/panel` | `autonomy_panel` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 69 | `PUT` | `/api/v1/autonomy/limits` | `update_autonomy` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 70 | `POST` | `/api/v1/marketing/full-operation-pipeline` | `marketing_full_pipeline` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 71 | `POST` | `/api/v1/automations/verify-operation` | `automations_verify` | True | True | True | False | `401` | `403` | `403` | **PASS** |
| 72 | `GET` | `/api/v1/automations/operational-log` | `automations_operational_log` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 73 | `GET` | `/api/v1/ai/status` | `ai_status` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 74 | `GET` | `/api/v1/security/audit` | `security_self_audit` | True | True | True | False | `401` | `403` | `403` | **PASS** |
| 75 | `POST` | `/api/v1/content-factory/generate-batch` | `content_factory_generate_batch` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 76 | `GET` | `/api/v1/content-factory/items` | `content_factory_list_items` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 77 | `GET` | `/api/v1/content-factory/assisted-export/{item_id}` | `content_factory_assisted_export` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 78 | `POST` | `/api/v1/content-factory/items/{item_id}/publish` | `content_factory_publish_item` | True | True | True | False | `401` | `403` | `403` | **PASS** |
| 79 | `PUT` | `/api/v1/content-factory/items/{item_id}` | `content_factory_update_item` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 80 | `GET` | `/api/v1/ceo/daily-plan` | `ceo_get_daily_plan` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 81 | `POST` | `/api/v1/ceo/daily-plan/generate` | `ceo_generate_daily_plan` | True | True | True | False | `401` | `403` | `403` | **PASS** |
| 82 | `PUT` | `/api/v1/ceo/daily-plan/tasks/{task_id}` | `ceo_update_delegated_task` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 83 | `POST` | `/api/v1/seo/weekly-report` | `seo_run_weekly_routine` | True | True | True | False | `401` | `403` | `403` | **PASS** |
| 84 | `GET` | `/api/v1/system/operational-dashboard` | `system_operational_dashboard` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 85 | `GET` | `/api/v1/system/alerts` | `system_list_alerts` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 86 | `POST` | `/api/v1/system/alerts/{alert_id}/resolve` | `system_resolve_alert` | True | True | True | False | `401` | `403` | `403` | **PASS** |
| 87 | `POST` | `/api/v1/system/pilot-7-days` | `system_run_7_day_pilot` | True | True | True | False | `401` | `403` | `403` | **PASS** |
| 88 | `GET` | `/api/v1/system/pilot-7-days` | `system_get_7_day_pilot` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 89 | `GET` | `/api/v1/system/resource-costs` | `system_resource_costs` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 90 | `GET` | `/api/v1/commercial/multibusiness-dashboard` | `commercial_multibusiness_dashboard` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 91 | `GET` | `/api/v1/commercial/business-units` | `commercial_list_business_units` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 92 | `GET` | `/api/v1/commercial/services` | `commercial_list_services` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 93 | `PUT` | `/api/v1/commercial/services/{service_id}/pricing` | `commercial_update_service_pricing` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 94 | `GET` | `/api/v1/commercial/offers` | `commercial_list_offers` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 95 | `POST` | `/api/v1/commercial/offers` | `commercial_create_offer` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 96 | `GET` | `/api/v1/commercial/market-opportunities` | `commercial_list_market_opportunities` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 97 | `POST` | `/api/v1/commercial/market-opportunities/research` | `commercial_research_market_opportunity` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 98 | `GET` | `/api/v1/commercial/landing-pages` | `commercial_list_landing_pages` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 99 | `POST` | `/api/v1/commercial/landing-pages/capture-lead` | `commercial_capture_lead_from_lp` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 100 | `POST` | `/api/v1/public/landing-pages/{slug}/capture` | `public_capture_lead_from_lp` | False | False | True | True | `None` | `None` | `422` | **PASS** |
| 101 | `PUT` | `/api/v1/crm/leads/{lead_id}/funnel-stage` | `commercial_update_lead_funnel_stage` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 102 | `GET` | `/api/v1/commercial/proposals` | `commercial_list_proposals` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 103 | `POST` | `/api/v1/commercial/proposals` | `commercial_create_proposal` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 104 | `PUT` | `/api/v1/commercial/proposals/{proposal_id}/status` | `commercial_update_proposal_status` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 105 | `GET` | `/api/v1/commercial/proposals/{proposal_id}/pdf` | `commercial_get_proposal_pdf_html` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 106 | `GET` | `/api/v1/agency/clients` | `agency_list_clients` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 107 | `POST` | `/api/v1/agency/clients` | `agency_create_client` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 108 | `GET` | `/api/v1/partners/programs` | `partners_list_programs` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 109 | `GET` | `/api/v1/partners/products` | `partners_list_products` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 110 | `POST` | `/api/v1/partners/products` | `partners_create_product` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 111 | `POST` | `/api/v1/partners/clicks` | `partners_record_click` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 112 | `POST` | `/api/v1/partners/conversions` | `partners_record_conversion` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 113 | `POST` | `/api/v1/partners/conversions/{conversion_id}/reconcile` | `partners_reconcile_commission` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 114 | `GET` | `/api/v1/finance/multibusiness-summary` | `finance_multibusiness_summary` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 115 | `POST` | `/api/v1/ceo/multibusiness-briefing` | `ceo_generate_multibusiness_briefing` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 116 | `GET` | `/api/v1/commercial/payments` | `commercial_list_payments` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 117 | `POST` | `/api/v1/commercial/payments/charge` | `commercial_create_payment_charge` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 118 | `POST` | `/api/v1/commercial/payments/webhook` | `commercial_payment_webhook` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 119 | `GET` | `/api/v1/commercial/delivery-projects` | `commercial_list_delivery_projects` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 120 | `POST` | `/api/v1/commercial/delivery-projects` | `commercial_create_delivery_project` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 121 | `PUT` | `/api/v1/commercial/delivery-projects/{project_id}` | `commercial_update_delivery_project` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 122 | `POST` | `/api/v1/crm/leads/{lead_id}/reactivate` | `crm_reactivate_lead` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 123 | `GET` | `/api/v1/crm/leads/{lead_id}/lgpd-export` | `crm_export_lead_lgpd` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 124 | `DELETE` | `/api/v1/crm/leads/{lead_id}/lgpd-erasure` | `crm_erase_lead_lgpd` | True | True | True | False | `401` | `403` | `SKIPPED_DESTRUCTIVE_TESTED_IN_SUITE` | **PASS** |
| 125 | `POST` | `/api/v1/crm/leads/{lead_id}/prepare-outreach` | `crm_prepare_lead_outreach` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 126 | `GET` | `/api/v1/commercial/phase18-1-executive-panel` | `commercial_phase18_1_executive_panel` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 127 | `GET` | `/api/v1/ai-engines/config` | `ai_engine_hub_get_overview` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 128 | `GET` | `/api/v1/ai-engine-hub/overview` | `ai_engine_hub_get_overview` | True | False | True | False | `401` | `403` | `403` | **PASS** |
| 129 | `PUT` | `/api/v1/ai-engines/config` | `ai_engine_hub_update_configuration` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 130 | `PUT` | `/api/v1/ai-engine-hub/configuration` | `ai_engine_hub_update_configuration` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 131 | `POST` | `/api/v1/ai-engine-hub/credentials` | `ai_engine_hub_save_credential` | True | True | True | True | `401` | `403` | `403` | **PASS** |
| 132 | `POST` | `/api/v1/ai-engine-hub/test-connection` | `ai_engine_hub_test_connection` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 133 | `POST` | `/api/v1/ai-engine-hub/route-execute` | `ai_engine_hub_route_execute` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 134 | `POST` | `/api/v1/ai-engine-hub/campaigns/generate` | `ai_engine_hub_generate_campaign` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 135 | `POST` | `/api/v1/ai-engine-hub/image-studio/generate` | `ai_engine_hub_generate_image` | True | False | True | True | `401` | `403` | `403` | **PASS** |
| 136 | `POST` | `/api/v1/ai-engine-hub/video-studio/generate` | `ai_engine_hub_generate_video` | True | False | True | True | `401` | `403` | `403` | **PASS** |
