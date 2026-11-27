# UNION GROWTH OS — ARQUITETURA DO SISTEMA (FASE 27)

## 1. Estrutura Backend & Banco de Dados

| Componente | Linhas | Responsabilidade na Fase 27 |
|---|---|---|
| `backend/app/main.py` | `199` | Lifespan: migrações DDL, seed inicial, `sync_release_records_service`, scheduler Python, static out |
| `backend/app/core/config.py` | `117` | `load_release_manifest()`, `APP_VERSION="2.4.0"`, detecção automática de `ENVIRONMENT="production"` |
| `backend/app/core/database.py` | `541` | PostgreSQL pool (`pool_size=10`, `max_overflow=20`), WAL + `busy_timeout=30000` em SQLite, backup/restore SHA-256 |
| `backend/app/models/entities.py` | `1411` | Adicionadas `ReleaseRecord`, `SystemAuditSnapshot`, `GrowthPlanRecord`, `GrowthPlanStepRecord` |
| `backend/app/services/versioning_engine.py` | `141` | Fonte única SemVer + persistência de releases no PostgreSQL |
| `backend/app/services/phase27_audit_and_growth_engine.py` | `673` | Auditoria não destrutiva 25 categorias + Matriz + Plano de Crescimento persistente + Benchmark 12 agentes |
| `backend/app/api/routers/phase27_routes.py` | `154` | `/system/version`, `/releases`, `/audit/run`, `/audit/history`, `/growth-plan/current`, `/steps/{id}`, `/ai/benchmark`, `/plans/change-tier` |
| `backend/app/api/routers/phase26_routes.py` | `150` | Bootstrap consolidado (+ `version_info` + `growth_plan`) |
| `backend/app/api/routes.py` | `4146` | Rotas principais + enforcement real de entitlements em `POST /tenants` e `POST /crm/leads` |

## 2. Estrutura Frontend Modular (`frontend/src/components/`)

- `UnionGrowthOSPortal.tsx` (`1.791` linhas): shell global, header com badge SemVer `#ug-version-badge-btn`, controle de áreas/submenus e drawers.
- `ReleaseHistoryDrawer.tsx` (`202` linhas) & `AuditCenterWorkspace.tsx` (`356` linhas): novos módulos Fase 27.
- `GrowthExecutionCenter.tsx` (`407` linhas), `AIEnginesHubWorkspace.tsx` (`760` linhas), `AIAutonomyAndOpsWorkspace.tsx` (`497` linhas).

## 3. Dívida Técnica Arquitetural Honesta

- `routes.py` (`4.146` linhas) concentra rotas legadas das Fases 1–21 e deverá ser fatiado em sub-routers por domínio (`crm`, `marketing`, `finance`, `seo`) sem quebrar compatibilidade. Score Categoria 24: **`85.0/100`**.
