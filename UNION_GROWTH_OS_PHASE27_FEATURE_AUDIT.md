# UNION GROWTH OS — MATRIZ DE RASTREABILIDADE & FUNCIONALIDADES (FASE 27)

Extraído diretamente da execução em produção (`GET /api/v1/system/audit/history`, `audit_id=5`, `QA_AUTOMATED_TENANT`, commit `f4b24d4a`):

| Funcionalidade | Frontend | API / Backend | Banco PostgreSQL | Testes | Status Real | Gap / Correção |
|---|---|---|---|---|---|---|
| **Sistema SemVer + Histórico de Releases** | Header Global + `ReleaseHistoryDrawer.tsx` | `GET /system/version`, `/releases` | `release_records` | `test_53` + CDP Fase 27 | `REAL` | Nenhum |
| **Central de Auditoria 25 Categorias** | `AuditCenterWorkspace.tsx` (`audit`) | `POST /system/audit/run`, `GET /audit/history` | `system_audit_snapshots` | `test_53` + CDP Fase 27 | `REAL` | Nenhum |
| **Growth Execution Center (0–90d)** | `GrowthExecutionCenter.tsx` | `POST/GET /growth-plan`, `PATCH /steps/{id}` | `growth_plans`, `growth_plan_steps` | `test_52`, `test_53` + CDP | `REAL` | Etapa externa OAuth depende credenciais |
| **12 Agentes Especialistas & ASK UNION** | `AITeamAndGovernanceView`, `HomeWorkspace` | `GET /agents/matrix`, `/ai/benchmark`, `/ask-union` | `agent_execution_logs`, `ask_union_logs` | `test_14,30,47,52,53` | `REAL_PARTIAL` | 4/12 HYBRID; chave Gemini Tenant 1 em HTTP 402 |
| **CRM Leads, LGPD, Smart Follow-up & Pipeline** | `CommercialRevenueWorkspace.tsx` | `/crm/leads`, `/smart-followup`, `/move-stage` | `crm_leads`, `crm_deals`, `crm_activities` | `test_08,31,51,52` + CDP | `REAL` | Disparo WhatsApp/SMTP aguarda OAuth (Modo Cópia ativo) |
| **Marketing, Fábrica 30 Peças & Social** | `MarketingAndSEOWorkspace.tsx` | `/content-factory/*`, `/social/calendar/*` | `marketing_campaigns`, `content_factory_items` | `test_06,07,25,32,46` | `REAL_PARTIAL` | 0/6 redes OAuth conectadas (usa Pacote 1-Clique) |
| **SEO Técnico HTTP & Search Console** | `SEOWorkspace` | `/seo/audit`, `/keywords`, `/articles/generate` | `seo_audit_reports`, `seo_articles` | `test_05,27,51,52` | `REAL_PARTIAL` | Crawler HTML ao vivo OK; SERP aguarda Search Console OAuth |
| **18 Integrações Externas & OAuth 2.0** | `IntegrationsAndSettingsWorkspace` | `/integrations/connect`, `/oauth/{p}/start` | `integration_connections` | `test_16`, `test_17` | `BLOCKED` | 1/18 integrações conectadas; 17 aguardando credenciais |
| **Automações 100% Nativas Python** | `AIAutonomyAndOpsWorkspace.tsx` | `/automations/*`, `/conversational-automation` | `automation_rules`, `automation_executions` | `test_09,22,47` + CDP | `REAL` | Worker único Uvicorn (sem fila Redis externa ainda) |
| **Monetização PLG, Entitlements & Billing** | `PlansAndUsagePanel` | `/plans/overview`, `/entitlements`, `/change-tier` | `tenants.plan_tier`, `payment_transactions` | `test_40,51,52,53` | `SANDBOX` | Enforcement backend ativo (`402`); `charge_enabled=false` |
| **Backup Portátil JSON + Restauração SHA-256** | Relatórios & Central Auditoria | `POST /system/backup`, `/backup/test-restore` | Disco + `sqlite:///:memory:` | `test_29` + CDP 05 | `REAL` | Botão SHA-256 validado com `145` registros (`31` tabelas) |
