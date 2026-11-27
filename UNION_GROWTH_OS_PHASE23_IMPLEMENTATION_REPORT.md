# FASE 23 — RELATÓRIO DE IMPLEMENTAÇÃO TÉCNICA (BACKEND, FRONTEND, IA & CI/CD)

**Projeto**: `UNION GROWTH OS — The Autonomous Business Growth Platform`  
**Commits Entregues**: `3db428b3eaf37664e49e0cfd2bf9c7f3a7412c53` (implementação Fase 23) e `afb2912dd2fb4e46e1f569b664d0cf5761b4ac45` (correções de produção PostgreSQL `CRMDeal.stage`, `VARCHAR(180)`, textos `12 agentes` e E2E)

---

## 1. Persistência e Modelos de Dados (`backend/app/models/` e `core/database.py`)
- **`Tenant` (`backend/app/models/entities.py`)**: 12 novas colunas com migração SQL idempotente em PostgreSQL e SQLite (`run_automatic_schema_migrations` em `backend/app/core/database.py`):
  - `ui_mode` (`SIMPLE` / `ADVANCED`), `brand_voice`, `brand_fonts`, `brand_differentials`, `brand_allowed_terms`, `brand_forbidden_terms`, `brand_examples`, `brand_country`, `brand_description`, `growth_goals_json`, `onboarding_step`, `onboarding_state_json`.
- **Novas Tabelas**:
  - `BrandVersionRecord` (`brand_versions`): histórico versionado de snapshots da marca e score de consistência.
  - `AskUnionActionLog` (`ask_union_action_logs`): registro auditável de prompts, intenções classificadas e ações geradas pelo copiloto ASK UNION.
- **Alargamento de Coluna PostgreSQL**: `AgentExecutionLog.provider_used` ampliado de `VARCHAR(80)` para `VARCHAR(180)` (`entities.py` + `ALTER TABLE agent_execution_logs ALTER COLUMN provider_used TYPE VARCHAR(180)` em `database.py`), evitando erro `psycopg2.errors.StringDataRightTruncation` no boot recovery do `APScheduler`.

## 2. Motor Growth OS Fase 23 (`backend/app/services/phase23_growth_platform.py`)
- **`compute_growth_score_and_health`**: calcula `Growth Score Documentado` (0–100, 5 blocos de 20 pts = 100 pts) e **Business Health (12 dimensões)** usando dados reais de `CRMLead`, `CRMDeal` (`stage`/`status`), `MarketingCampaign`, `SEOAuditReport`, `FinancialRecord`, `CustomerFeedback`, `AutomationRule`, `ApprovalRequest`, `IntegrationConnection`, sem inventar números (`NAO_DISPONIVEL` / `ESTIMATIVA` / `REAL`).
- **`build_opportunity_radar_and_actions` & `execute_or_decide_executive_action_service`**: radar de oportunidades + **Executive Action Center** com decisões `EXECUTE`, `APPROVE`, `SCHEDULE` (cria `AutomationRule` Python/APScheduler) e `REJECT`.
- **`audit_brand_consistency_service` & `save_brand_intelligence_service`**: central visual/verbal, versionamento e auditoria automática de termos proibidos/ausência de site/diferenciais em campanhas, copies e Content Factory.
- **`get_progressive_onboarding_service` & `save_progressive_onboarding_step_service`**: onboarding progressivo em 6 etapas recuperáveis com geração de plano inicial e ações recomendadas.
- **`ask_union_copilot_service`**: classifica intenções (*Quero vender mais*, SEO, divulgação, retenção, CRM, automação) e cria ações executáveis rastreáveis.
- **`build_conversational_automation_service`**: interpreta pedidos em português natural, gera preview completo com risco R$ 0, simula (`dry_run`) e persiste regra real Python + `APScheduler` após aprovação explícita (zero dependência de `n8n`).
- **`get_analytics_attribution_service`**: consolida funil comercial de 6 etapas e atribuição First-Touch por canal real de CRM, marcando GA4/Search Console externos como `NAO_DISPONIVEL` quando desconectados.

## 3. Equipe de 12 Agentes & Resiliência de Provedores
- **`AGENT_12_DATA_ANALYST` (`AI Data Analyst`)** adicionado em `backend/app/agents/orchestrator.py`, `backend/app/services/plans_and_audit.py` (matriz Enterprise), `backend/app/services/ai_engines_hub.py` (`ALL_12_AGENTS`) e `frontend/src/components/AITeamAndGovernanceView.tsx`.
- **Resiliência em `AIRouter.route_and_execute` (`ai_engines_hub.py`)**:
  - Cache TTL in-memory de `180s` por `(tenant_id, provedor, modelo, capacidade, hash_prompt)`.
  - Circuit breaker por `(tenant_id, provedor)` de `90s` após `>=3` falhas transitórias reais (`5xx`/timeout/`429`), executando sempre validações estáticas (`BLOCKED_CAPABILITY`, `BLOCKED_FREE_ONLY`, `BLOCKED_LIMIT`) antes do disjuntor e limpando o circuito ao salvar nova credencial ou validar conexão (`ok=True`).
- **Otimização do Probe Local Ollama & Fallback PageSpeed**: cache de `30s` em `MultiProviderAIAdapter.resolve_provider_status()` usando `urllib.request.urlopen` (`0.45s`) para URLs `http://` (evitando overhead repetido de `ssl.create_default_context()` no Windows) e cache curto de `120s` em fallbacks do `fetch_pagespeed_insights` (`seo_and_market_engine.py`).

## 4. Endpoints REST (`backend/app/api/routes.py` & `schemas/contracts.py`)
- `GET /api/v1/growth-os/command-center`
- `POST /api/v1/growth-os/actions/decide`
- `GET /api/v1/growth-os/brand`, `PUT /api/v1/growth-os/brand`, `POST /api/v1/growth-os/brand/audit`
- `GET /api/v1/growth-os/onboarding`, `POST /api/v1/growth-os/onboarding`
- `POST /api/v1/growth-os/ask-union`, `POST /api/v1/growth-os/ask-union/execute`
- `GET /api/v1/growth-os/analytics-attribution`
- `POST /api/v1/automations/conversational-build`
- `POST /api/v1/agents/AGENT_12_DATA_ANALYST/execute`
- Atualização em `GET /api/v1/auth/me` e `PUT /api/v1/tenants/current` para persistir `ui_mode` e resumo de marca/onboarding.

## 5. Frontend Next.js 15 (`frontend/src/`)
- `GrowthCommandCenter.tsx`: **ASK UNION**, **Growth Score Documentado** com metodologia expansível, **Business Health (12 dimensões)**, **AI CEO Briefing (Hoje & Semana)**, **Opportunity Radar** e **Executive Action Center**.
- `BrandAndOnboardingHub.tsx`: `ProgressiveOnboardingWizard` (6 etapas salváveis/reiniciáveis) e `BrandIntelligenceCenter` (identidade visual/verbal, preview, versões e detector de inconsistências).
- `ConversationalAutomationAndAnalytics.tsx`: `ConversationalAutomationPanel` e `AnalyticsAttributionPanel`.
- `page.tsx`: botão persistente `#ug-ui-mode-toggle` (`Modo Simples` / `Modo Avançado` com rótulo compacto responsivo em `< sm`), textos atualizados para 12 agentes e exportação estática para `frontend/out/`.

## 6. CI/CD GitHub Actions (`.github/workflows/ci-cd.yml`)
- Actions atualizadas para `actions/checkout@v7`, `actions/setup-python@v7`, `actions/setup-node@v7` com `node-version: "22"`, verificação `npx tsc --noEmit && npm run build`, auditoria de Dockerfile, `pytest` completo (`49` testes) e audit de segredos.
