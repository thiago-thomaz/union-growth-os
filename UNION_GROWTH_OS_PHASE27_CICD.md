# UNION GROWTH OS — CI/CD, GITHUB ACTIONS & COOLIFY DEPLOY (FASE 27)

## 1. Histórico Real Verificado na Fase 27

- **Workflow `.github/workflows/ci-cd.yml`:** executa `test-and-validate` (Python + PostgreSQL/SQLite `pytest` + TypeScript `tsc --noEmit` + Next.js static export + Security Audit) e `deploy-and-verify`.
- **Execuções GitHub Actions Observadas:**
  - Commit `c546d63a` (tag `v2.4.0` inicial): Run **`46065918941`** — `completed: success`.
  - Commit `528dc6a3` (mobile polish + timing): Run **`46066953956`** — `completed: success`.
  - Commit `f4b24d4a` (fix `restored_tables` UI + CDP E2E): Run **`46068240519`** — **`completed: success`**.
- **Coolify Deployments (`app_uuid: swpy83sa5wshb558fadlrzwc`):**
  - Build `f4b24d4a` via `deployment_uuid`: **`wvpqqwdpdftf2ar2tiwwctlw`** -> status **`finished`** sem indisponibilidade (zero-downtime Traefik).
  - Isolamento VPS comprovado via `get_infrastructure_overview`: **11 aplicações preservadas**, incluindo **`arena-play` (`dinqcdvkvrasqwlj4sdu50i2`) 100% intocada** e banco `union-growth-os-db` (`thkpm0vkt5f4rj8znd3e2abi`) `running:healthy`.

## 2. Gap Transparente de CI/CD (`Categoria 20: 84.0/100 — REAL_PARTIAL`)

- As chaves **`COOLIFY_API_TOKEN`** e **`COOLIFY_DEPLOY_WEBHOOK`** ainda não constam nos **Secrets** do repositório GitHub (`Settings -> Secrets -> Actions`); por isso o job `deploy-and-verify` automático via GitHub Runner requer acionamento via API/MCP Coolify ou inclusão manual dos secrets pelo proprietário.
