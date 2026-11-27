# UNION GROWTH OS — VALIDAÇÃO DE PRODUÇÃO EM NUVEM (FASE 27)

## 1. Verificação Direta das Duas URLs em Produção (`commit f4b24d4a` / `v2.4.0`)

| Endpoint | `https://automacao.projetosunion.cloud` | `https://uniongrowth.72.62.13.62.sslip.io` |
|---|---|---|
| `GET /health` | **HTTP `200`** — `version: 2.4.0`, `git_commit: f4b24d4a`, `environment: production` | **HTTP `200`** — `version: 2.4.0`, `git_commit: f4b24d4a`, `environment: production` |
| `GET /ready` | **HTTP `200`** — PostgreSQL `healthy`, `is_fallback: false`, `127` jobs | **HTTP `200`** — PostgreSQL `healthy`, `is_fallback: false`, `127` jobs |
| `GET /api/v1/system/version` | **HTTP `200`** — `semver: {2,4,0}`, `git_tag: v2.4.0`, `latest_audit_score: 86.9` | **HTTP `200`** — `semver: {2,4,0}`, `git_tag: v2.4.0`, `latest_audit_score: 86.9` |

## 2. Persistência Real Validada no PostgreSQL 16 (`QA_AUTOMATED_TENANT`)

- `release_records`: **`6`** releases sincronizados (`v1.0.0` .. `v2.4.0`).
- `system_audit_snapshots`: **`5`** snapshots históricos gravados; último snapshot `#5` com score **`86.9/100`** (`PRODUCTION_READY`).
- `growth_plans` / `growth_plan_steps`: planos salvos e etapas atualizadas (`Concluído` / `Replanejado`) persistindo após recarregamento.
- Restauração isolada SHA-256 validada ao vivo sem modificar produção (`145` registros em `31` tabelas).
