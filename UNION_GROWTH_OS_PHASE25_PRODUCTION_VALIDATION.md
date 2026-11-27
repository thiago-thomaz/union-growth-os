# UNION GROWTH OS — FASE 25: VALIDAÇÃO COMPLETA EM PRODUÇÃO CLOUD

**Deployment Coolify Código:** `vb5t8pngj2c7qpq5pklnwqpe` (`status: finished`)  
**Commit Vivo em `/health.git_commit`:** `b6162c2859b16514b8666736f23c0e9d9c8ac34a`  
**Docker Keep-Alive:** `--timeout-keep-alive 75 --proxy-headers` em [Dockerfile](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/Dockerfile)

---

## 1. Saúde das Rotas Públicas & Infraestrutura Coolify
| Endpoint | URL Primária (`automacao.projetosunion.cloud`) | URL Secundária (`uniongrowth.72.62.13.62.sslip.io`) |
| :--- | :--- | :--- |
| `GET /health` | `200 OK` • `postgresql` (`is_fallback: false`) • `git_commit: b6162c28...` | `200 OK` • `postgresql` (`is_fallback: false`) • `git_commit: b6162c28...` |
| `GET /ready` | `200 OK` • `ready: true` • `127` jobs `APScheduler Native Python` | `200 OK` • `ready: true` • `127` jobs `APScheduler Native Python` |
| `GET /` | `200 OK` (`len=7013` static Next.js 15 HTML) | `200 OK` (`len=7013` static Next.js 15 HTML) |
| `GET /docs` | `200 OK` (`len=976` Swagger/OpenAPI) | `200 OK` (`len=976` Swagger/OpenAPI) |

- **Integridade do Servidor & Outros Projetos (`get_infrastructure_overview`):** `1` servidor (`localhost`), `2` projetos, **`11` aplicações** (`arena-play` e demais projetos preservados sem qualquer alteração), `1` banco PostgreSQL (`union-growth-os-db` saudável), `1` serviço.
- **Container Logs (`swpy83sa5wshb558fadlrzwc`):** respostas `200 OK` limpas e zero tracebacks após rollout com `keep-alive 75`.

---

## 2. Validação E2E Contra Produção Real (Chrome CDP + APIs)
- `scripts/phase25_cdp_e2e.py`: **`all_phase25_e2e_passed: true`** (`30.05s`, `0` console errors, `0` HTTP 4xx/5xx, `0px` overflow em 7 viewports).
- `scripts/phase24_cdp_e2e.py`: **`all_phase24_e2e_passed: true`** (`44.42s`, `P1/P2/P3` aprovados, `0` HTTP 4xx/5xx).
- `scripts/phase23_cdp_e2e.py`: **`all_phase23_e2e_passed: true`** (`20/20` jornadas aprovadas).
- `scripts/phase22_cdp_ux_e2e.py`: **`all_phase22_e2e_passed: true`** (`S01..S15` aprovados, `111` requisições monitoradas sem falhas).

*Obs.: Os arquivos de documentação Markdown gerados nesta fase serão sincronizados em um commit final de docs/evidência com novo deploy no Coolify para garantir `git HEAD == /health.git_commit` antes da entrega definitiva.*
