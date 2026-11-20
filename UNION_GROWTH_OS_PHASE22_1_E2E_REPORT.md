# FASE 22.1 — RELATÓRIO DE TESTES E2E, ACESSIBILIDADE, RESPONSIVIDADE & PROXY RATE-LIMIT

**Alvo Real Testado**: `https://automacao.projetosunion.cloud` (Deploy Coolify `swpy83sa5wshb558fadlrzwc`, commit de aplicação [`91acfafb9baffe9dd989fee7c8eb5538c14a1023`](https://github.com/thiago-thomaz/union-growth-os/commit/91acfafb9baffe9dd989fee7c8eb5538c14a1023))  
**Tenant Isolado de Teste**: `QA_AUTOMATED_TENANT` (dados reais do Tenant 1 preservados)

---

## 1. Suíte de Fluxos de Usabilidade Reais (CDP — Fase 22.1 AFTER)
Executor: [`scripts/phase22_1_usability_flows.py`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/scripts/phase22_1_usability_flows.py) (`--mode after`)  
Evidência JSON: [`phase22_1_flows_after.json`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/after/phase22_1_flows_after.json)

- **Resultado Geral**: **8 / 8 fluxos PASS** (`F1` a `F8`)
- **Erros de Console JS**: `0`
- **Exceções de Runtime JS**: `0`
- **Respostas HTTP `4xx/5xx`**: `0` (`network_failures: []`)

---

## 2. Regressão Completa Fase 22 UX/UI (CDP E2E, Acessibilidade & 4 Viewports)
Evidência JSON: [`phase22_cdp_ux_e2e.json`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_SCREENSHOTS/phase22_cdp_ux_e2e.json)

### 2.1 Cenários Funcionais Executados (Todos `passed: true`)
| Cenário | Descrição | Resultado |
|---|---|---|
| `S01_S02_login_and_inicio_5blocks` | Login real + Sidebar em 6 áreas + 5 blocos do Início + Onboarding | `PASS` (`has_sidebar_areas: true`, `has_5_blocks: true`, `has_onboarding: true`) |
| `S03_onboarding_dismiss_and_restore` | Ocultar e restaurar checklist de onboarding em `localStorage` | `PASS` (`dismissed_ok: true`, `restored_ok: true`, `visible_again: true`) |
| `S04_theme_light_dark_toggle` | Alternância Light Mode (`rgb(241, 245, 249)` bg / `rgb(15, 23, 42)` fg) e restauração Dark Mode | `PASS` |
| `S05_command_center_global_search` | Command Center (`Ctrl+K`), busca global (`Campanha` e `Gemini`) e navegação | `PASS` |
| `S06_sidebar_and_todos_recursos_favoritos` | Recolher (`80px`) e expandir (`256px`) sidebar + Favoritos em `Todos os recursos` | `PASS` |
| `S07_meu_trabalho_7_filtros_drawer` | 7 filtros (`Precisa de mim`, `IA executando`, `Aguardando aprovação`, `Concluído`, `Falhou`, `Bloqueado`, `Tudo`) + Drawer lateral | `PASS` |
| `S08_comercial_crm_e_blob_pdf` | CRM + troca segura para `QA_AUTOMATED_TENANT` + Geração de PDF seguro via `blob:` (`count: 6`, sem token na URL) | `PASS` |
| `S09_marketing_subtabs_e_filtro` | Sub-abas (`SEO`, `Calendário`, `Fábrica de Conteúdo`) + filtro de campanhas | `PASS` |
| `S10_ia_ux_e_motores` | Visão & Agentes + Provedores + Histórico honesto | `PASS` |
| `S11_gestao_relatorios_integracoes` | Relatórios + filtros de Integrações (`Pendentes` / `Todas`) | `PASS` |
| `S12_central_de_ajuda` | Drawer da Central de Ajuda (Glossário + Atalhos) | `PASS` |
| `S15_logout_and_public_lp` | Logout real + validação da Landing Page pública (formulário + consentimento LGPD) | `PASS` |

### 2.2 Acessibilidade & Landmarks HTML5
- `lang`: `"pt-BR"`
- `landmarks`: `aside: true`, `header: true`, `main: true`, `nav: true`
- `total_visible_buttons`: `53`
- `unlabeled_buttons_count`: `0`
- `unlabeled_inputs_count`: `0`

### 2.3 Responsividade Multi-Tela (0px de Overflow Horizontal)
| Viewport | `scrollWidth` vs `clientWidth` | `overflowPx` | Drawer Mobile | Resultado |
|---|---:|---:|---|---|
| `desktop_1920x1080` | `1905` / `1905` | `0` | `true` | `PASS` |
| `notebook_1366x768` | `1351` / `1351` | `0` | `true` | `PASS` |
| `tablet_768x1024` | `768` / `768` | `0` | `true` | `PASS` |
| `mobile_390x844` | `390` / `390` | `0` | `true` | `PASS` |

### 2.4 Telemetria da Sessão Completa Fase 22
- `total_network_requests`: `94`
- `console_errors_count`: `0`
- `runtime_exceptions_count`: `0`
- `network_failures_count`: `0`
- `url_token_leaks_count`: `0`
- `all_phase22_e2e_passed`: `true`

---

## 3. Correção de Rate-Limit Sob Proxy Reverso & CI/CD
- **Proxy Traefik (`10.0.1.11`)**: Em produção, `enforce_rate_limit` ([`backend/app/core/security.py`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/backend/app/core/security.py#L174-L176)) passou a ler `X-Forwarded-For` antes de `request.client.host` e `RATE_LIMIT_PER_MINUTE` ([`backend/app/core/config.py`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/backend/app/core/config.py#L61)) foi calibrado para `600`, zerando respostas `429` durante carregamento simultâneo dos `27` endpoints da SPA e mantendo os testes de segurança (`test_24 + test_45 -> 2 passed in 19.91s`).
- **GitHub Actions CI/CD**: Execução [`44818026262`](https://github.com/thiago-thomaz/union-growth-os/actions/runs/44818026262) no commit `91acfafb9baffe9dd989fee7c8eb5538c14a1023` finalizou com `status: completed` e `conclusion: success` (`updated_at: 2026-11-20T21:12:16Z`).
