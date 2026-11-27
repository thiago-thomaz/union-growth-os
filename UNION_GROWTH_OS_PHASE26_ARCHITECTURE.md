# UNION GROWTH OS — FASE 26: SOFTWARE ARCHITECTURE

**Versão:** `2.3.0 — FASE 26`  

## 1. Visão Arquitetural Modularizada
```
Cliente Web (Next.js 15 Static Export - `frontend/out`)
  ├── Shell Enxuto: `UnionGrowthOSPortal.tsx` (1.741 linhas, -57% vs 4.039)
  ├── Core DS 4.0: `DesignSystem.tsx`, `HomeWorkspace.tsx`, `MyWorkHub.tsx`, `CommandCenter.tsx`
  ├── Centro 0-90d: `GrowthExecutionCenter.tsx`
  ├── Domínios: `CommercialRevenueWorkspace.tsx`, `MarketingAndSEOWorkspace.tsx`,
  │             `AIAutonomyAndOpsWorkspace.tsx`, `ManagementAndIntegrationsWorkspace.tsx`,
  │             `AIEnginesHubWorkspace.tsx`, `AITeamAndGovernanceView.tsx`
  ▼ HTTPS + Traefik
API FastAPI (`uvicorn --timeout-keep-alive 75 --proxy-headers`)
  ├── `backend/app/api/routers/phase26_routes.py` (/growth-os/bootstrap, /growth-plan, /agents/matrix, /plans/entitlements, CRM)
  ├── `backend/app/api/routes.py` (routers legados preservando 100% compatibilidade)
  ├── Serviços: `phase26_growth_os_engine.py`, `phase25_product_engine.py`, `phase23_growth_platform.py`,
  │             `seo_and_market_engine.py`, `integrations_and_social_engine.py`, `plans_and_audit.py`
  ├── Orquestração: `orchestrator.py` (12 agentes + `AIUsageTracker` persistido + `Free-Only` router)
  ├── Automação Nativa: `APScheduler` (127 rotinas Python internas, 0% n8n)
  ▼
PostgreSQL 16 (`union-growth-os-db`, container isolado na VPS Coolify)
```

## 2. Próximo Passo Arquitetural (Debt Backlog)
- Continuar extração progressiva dos endpoints restantes de `routes.py` (`4.127+` linhas) para módulos temáticos em `backend/app/api/routers/` (`auth`, `crm`, `marketing`, `seo`, `ai_hub`, `admin`).
- Avaliar worker dedicado (Celery/ARQ/Redis) caso volume de tarefas SEO ou lotes assíncronos cresça para milhares de tenants concorrentes.
