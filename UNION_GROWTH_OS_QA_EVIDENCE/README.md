# UNION GROWTH OS — DIRETÓRIO DE EVIDÊNCIAS VERIFICÁVEIS DE QA E PRODUÇÃO (FASE 20)

Este diretório contém as evidências brutas coletadas diretamente contra o ambiente de produção (`https://automacao.projetosunion.cloud` e `https://uniongrowth.72.62.13.62.sslip.io`) e da suíte automatizada de regressão e E2E (`44/44 testes`).

## Estrutura de Evidências

- **`phase20_live_validation_summary.json`**: Resumo executivo da execução E2E ao vivo em produção (commit SHA ativo, status de segurança, métricas de latência e screenshots).
- **`deployment/health_ready_validation.json`**: Respostas reais de `/health`, `/ready`, `/robots.txt`, `/sitemap.xml` nos 2 domínios HTTPS e cabeçalhos de segurança HTTP.
- **`security/defects_and_security_validation.json`**: Comprovação real das correções `DEFECT-01` (404 JSON em rotas `/api/*`), `DEFECT-02` (bloqueio 403 cross-tenant em `X-Tenant-Id`), `DEFECT-03` (PDF de proposta comercial via `?access_token=`), `DEFECT-04` (Landing Page pública `/lp/agentes-ia` + bloqueio LGPD 400) e `DEFECT-05` (histórico do Piloto 7 Dias).
- **`e2e/e2e_15_scenarios_live_results.json`**: Trilha completa dos **15 Cenários E2E** executados no tenant isolado `QA_AUTOMATED_TENANT` + execução real ao vivo do **Google Gemini (`gemini-3.5-flash-lite`, `VERIFIED_FREE`, `R$ 0,00`)** no Tenant Principal.
- **`performance/performance_metrics.json`**: Benchmark de concorrência (20 requisições simultâneas, `p50`, `p95`, `avg_latency_ms` e `100%` de taxa de sucesso).
- **`screenshots/`**: Capturas de tela Full HD (`1920x1080`) tiradas via Headless Chrome diretamente da URL de produção:
  - `01_production_login_and_app.png`
  - `02_public_landing_page_agentes_ia.png`
  - `03_public_landing_page_union_tech.png`
  - `04_proposal_printable_pdf_view.png`
