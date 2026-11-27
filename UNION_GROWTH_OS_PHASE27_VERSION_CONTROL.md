# UNION GROWTH OS — CONTROLE DE VERSÃO E RELEASE LIFECYCLE (FASE 27)

## 1. Política Oficial SemVer (`MAJOR.MINOR.PATCH`)

| Versão | Tag Git | Fase | Data | Commit | Ambiente | Estado |
|---|---|---|---|---|---|---|
| **`2.4.0`** | `v2.4.0` | FASE 27 | `2026-11-27` | `f4b24d4a` | `production` | `PUBLISHED` (Ativo) |
| `2.3.0` | `v2.3.0` | FASE 26 | `2026-11-27` | `5eefdd74` | `production` | `PUBLISHED` |
| `2.2.0` | `v2.2.0` | FASE 25 | `2026-11-27` | — | `production` | `PUBLISHED` |
| `2.1.0` | `v2.1.0` | FASE 24 | `2026-11-27` | — | `production` | `PUBLISHED` |
| `2.0.0` | `v2.0.0` | FASE 23 | `2026-11-26` | — | `production` | `PUBLISHED` |
| `1.0.0` | `v1.0.0` | FASES 1–22 | `2026-11-10` | — | `production` | `PUBLISHED` |

## 2. Arquitetura de Fonte Única de Verdade

- **`release_manifest.json`** (copiado para `/app/release_manifest.json` no `Dockerfile`): define `current_version`, objeto `semver` (`major: 2, minor: 4, patch: 0`), `git_tag: "v2.4.0"`, `release_channel: "STABLE"` e changelog estruturado de funcionalidades, correções, segurança e cobertura de testes.
- **`backend/app/core/config.py`**: `load_release_manifest()` lê o manifesto dinamicamente no boot; `ENVIRONMENT` é resolvido para `"production"` automaticamente via variável de ambiente `ENVIRONMENT=production` no `Dockerfile` ou presença de `SOURCE_COMMIT`.
- **`backend/app/services/versioning_engine.py`** + **`ReleaseRecord` (`release_records` PostgreSQL)**: sincroniza na inicialização do FastAPI (`lifespan`) os registros de versão no banco de dados relacional e associa automaticamente a última pontuação auditada (`86.9/100` — `PRODUCTION_READY`).
- **Endpoints Ativos**:
  - `GET /health` & `GET /ready`: expõem `version: "2.4.0"`, `environment: "production"`, `release_channel: "STABLE"`, `git_tag: "v2.4.0"`, `git_commit`, saúde do PostgreSQL e do `APScheduler`.
  - `GET /api/v1/system/version`: metadata completa para a UI e integradores.
  - `GET /api/v1/system/releases`: histórico completo persistido exibido no **`ReleaseHistoryDrawer.tsx`**.
