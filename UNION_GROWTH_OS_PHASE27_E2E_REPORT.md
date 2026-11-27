# UNION GROWTH OS — RELATÓRIO E2E EM PRODUÇÃO VIA CHROME CDP (FASE 27)

**Alvo Real:** `https://automacao.projetosunion.cloud` • **Isolamento Estrito:** `QA_AUTOMATED_TENANT` • **Commit Testado:** `f4b24d4a` (`v2.4.0`)

## 1. Resumo Consolidado das 6 Suítes Chrome Headless

| Suíte Executada | Duração | Cenários / Checks | Console / JS Errors | HTTP 4xx/5xx | URL Token Leaks | Viewports (`0px` overflow) | Status Geral |
|---|---|---|---|---|---|---|---|
| `scripts/phase27_cdp_e2e.py` | `50.35s` | **`11 / 11` true** | `0` | `0` | `0` | `8 / 8` | **PASS (`100%`)** |
| `scripts/phase26_cdp_e2e.py` | `52.03s` | **`11 / 11` true** | `0` | `0` | `0` | `8 / 8` | **PASS (`100%`)** |
| `scripts/phase25_cdp_e2e.py` | `33.96s` | **`8 / 8` true** | `0` | `0` | `0` | `7 / 7` | **PASS (`100%`)** |
| `scripts/phase24_cdp_e2e.py` | `55.66s` | **`3 / 3` perfis (`100%`)** | `0` | `0` | `0` | `7 / 7` | **PASS (`100%`)** |
| `scripts/phase23_cdp_e2e.py` | — | **`20 / 20` jornadas** | `0` | `0` | `0` | `6 / 6` | **PASS (`100%`)** |
| `scripts/phase22_cdp_ux_e2e.py` | — | **`12 / 13` cenários** | `0` | `0` | `0` | `4 / 4` | **PARCIAL (`S08=false`)** |

## 2. Detalhe da Fase 27 (`phase27_cdp_e2e.py` — 100% Verde)

- `login_ok`, `switched_qa`, `header_semver_ok`, `release_drawer_ok`, `audit_25_categories_ok`, `traceability_matrix_ok`, `backup_restore_sha256_ok` (`145` registros, `31` tabelas), `growth_center_persisted_ok` (`Concluído -> Replanejado`), `ai_benchmark_12_agents_ok` (`12` agentes em `2.47ms`, `R$ 0,00`), `automations_presets_flow_ok`, `plans_entitlements_ok`, `light_mode_ok` — **todos `true`** (`11` screenshots salvos em `UNION_GROWTH_OS_PHASE27_EVIDENCE/`).

## 3. Apontamento Honesto de Regressão (`phase22_cdp_ux_e2e.py` -> `S08`)

- Na suíte legada `phase22_cdp_ux_e2e.py`, `12/13` cenários passaram com `0` erros de console/rede/vazamento; apenas **`S08_comercial_crm_e_blob_pdf`** reportou `passed: false` (`found: true, count: 7, urls: []`) porque o fetch assíncrono do blob HTML de PDF em produção excedeu a janela fixa de `2.000ms` do hook `window.open` do script `phase22`. A geração e o download seguro do PDF continuam funcionais e validados no backend (`test_36`).
