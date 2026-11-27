# Changelog — UNION GROWTH OS

## [2.4.0 — FASE 27] — 2026-11-27

### Versionamento SemVer Oficial, Auditoria 25 Categorias, Centro de Crescimento Persistente & Entitlement Enforcement Real
- **Sistema Oficial de Versionamento SemVer (`release_manifest.json`, `versioning_engine.py`, Git tag `v2.4.0`)**:
  - Remoção da versão estática `1.0.0` em `config.py`; exposição dinâmica de `version: 2.4.0`, `semver`, `git_tag: v2.4.0`, `environment: production`, `release_channel: STABLE`, `git_commit` (`SOURCE_COMMIT`), saúde PostgreSQL e jobs APScheduler em `/health`, `/ready`, `GET /api/v1/system/version` e `GET /api/v1/system/releases`, sincronizado em `release_records` no PostgreSQL.
  - Badge discreta e clicável `#ug-version-badge-btn` (`v2.4.0 • PRODUCTION | STABLE • f4b24d4a`) no header desktop/tablet (`sm:inline-flex`) e no rodapé da barra lateral mobile, abrindo o **`ReleaseHistoryDrawer.tsx`** com timeline completa `v1.0.0` → `v2.4.0`.
- **Central Persistente de Auditoria Completa (`phase27_routes.py`, `phase27_audit_and_growth_engine.py`, `AuditCenterWorkspace.tsx`)**:
  - `POST /api/v1/system/audit/run` e `GET /api/v1/system/audit/history` persistindo snapshots históricos em `system_audit_snapshots`.
  - Avaliação ponderada honesta das **25 categorias obrigatórias** (score observado em produção: **`86.9/100` — `PRODUCTION_READY`**, com **`19`** bloqueios/pendências externas listados sem inflar artificialmente para `100/100`) + **Matriz de Rastreabilidade** (`REAL`, `REAL_PARTIAL`, `SANDBOX`, `BLOCKED`).
  - Exposição na interface do botão **"Testar Restauração Isolada"** (`POST /api/v1/system/backup/test-restore`) em `AuditCenterWorkspace.tsx` e `ManagementAndIntegrationsWorkspace.tsx` validando integridade SHA-256 + `sqlite:///:memory:` (`145` registros em `31` tabelas verificados em produção) sem tocar nos dados ativos.
- **Growth Execution Center Persistido no PostgreSQL (`growth_plans`, `growth_plan_steps`, `GrowthExecutionCenter.tsx`)**:
  - `GET /api/v1/growth-os/growth-plan/current` e `PATCH /api/v1/growth-os/growth-plan/steps/{step_id}` com comandos `EXECUTE`, `COMPLETE`, `CANCEL` e `REPLAN`, exibindo `priority_score`, `owner_label`, `due_date`, `dependencies`, `success_metric`, `evidence` e `next_action`.
- **Entitlements Reais no Backend, Tier Switching, AI Benchmark & Presets Python (`plans_and_audit.py`, `routes.py`, `AIEnginesHubWorkspace.tsx`, `AIAutonomyAndOpsWorkspace.tsx`)**:
  - `enforce_tenant_entitlement` aplicado diretamente em `POST /api/v1/tenants` e `POST /api/v1/crm/leads` (HTTP `402` quando quota excedida no plano ativo) + `POST /api/v1/plans/change-tier` (`charge_enabled: false`).
  - `GET /api/v1/ai/benchmark` medindo latência, modo real (`4/12 HYBRID`, `8/12 DETERMINISTIC`, `0 SIMULATED`) e conformidade `FREE_ONLY` (`R$ 0,00`), mais 3 **Templates Visuais em 1 Clique** com fluxo linear na área de Automações 24/7 (`0% n8n`).
  - `DesignSystem.tsx` DS 5.0 enriquecido com metadados `updatedAt`, `statusLabel` e tooltip `calculationMethod` no `MetricStrip`, além de `busy_timeout=30000` + WAL no SQLite de fallback/testes e filtro temporal seguro em `recover_missed_runs`.
- **Qualidade, CI/CD & Cloud**: `54/54` pytest (`72.93s`), `npx tsc --noEmit` + `next build` (`83.7 kB` `/` | First Load `189 kB`), GitHub Actions CI `46068240519` (`success`), deploy Coolify `wvpqqwdpdftf2ar2tiwwctlw` (`finished`), ambas URLs HTTP `200`, `phase27_cdp_e2e.py` .. `phase23_cdp_e2e.py` `100%` aprovadas e `phase22_cdp_ux_e2e.py` com `12/13` cenários aprovados (`S08` timeout de captura).

## [2.3.0 — FASE 26] — 2026-11-27

### Transformação Modular, Centro de Crescimento (0–90d), Matriz de IA, Revenue Engine & DS 4.0
- **Decomposição do Monólito Frontend (`UnionGrowthOSPortal.tsx` `4.039` → `1.741` linhas, `-56.9%`)**: extração completa das visões legadas para `GrowthExecutionCenter.tsx`, `AIAutonomyAndOpsWorkspace.tsx`, `MarketingAndSEOWorkspace.tsx`, `ManagementAndIntegrationsWorkspace.tsx` e `CustomerSuccessWorkspace`, com Login e Modal Assistido migrados para tokens Light/Dark DS 4.0.
- **Bootstrap Executivo & Centro de Crescimento (`phase26_routes.py`, `phase26_growth_os_engine.py`)**:
  - `GET /api/v1/growth-os/bootstrap`: consolida Onda 1 da Home de 5 requests para 1 chamada.
  - `POST /api/v1/growth-os/growth-plan` + `/execute-step`: organiza objetivos do negócio em ações `TODAY`, `NEXT_7_DAYS`, `NEXT_30_DAYS` e `NEXT_90_DAYS` com `ESTIMATED` explícito e trava honesta para `CONNECT_OAUTH`.
- **Matriz Transparente de IA & Uso Persistido (`orchestrator.py`, `GET /api/v1/agents/matrix`)**: `AIUsageTracker` agora consulta `AgentExecutionLog` e `AIEngineExecutionRecord` no PostgreSQL; interface exibe badges reais `HYBRID` (`4/12`) e `DETERMINISTIC` (`8/12`) com `0` agentes simulados.
- **Revenue Engine, SEO Priorizado & Billing Readiness (`CommercialRevenueWorkspace.tsx`, `seo_and_market_engine.py`, `AIEnginesHubWorkspace.tsx`)**:
  - `POST /api/v1/crm/deals/{deal_id}/move-stage` (`ESTIMATED`) e `/crm/leads/{lead_id}/smart-followup` (trava LGPD `opt_out` + modo manual seguro de cópia).
  - Sinais SEO enriquecidos (`h1_count`, `internal_links_count`, `external_links_count`, `images_missing_alt_count`) + `prioritized_recommendations`.
  - `GET /api/v1/plans/entitlements` com `billing_readiness.charge_enabled = false` e botões `OAuth 2.0` / `Desconectar` em Integrações.
- **Qualidade, CI/CD & Cloud**: `scripts/ci_deploy_and_verify.py` endurecido com 8 tentativas durante swap no Traefik/Coolify, GitHub Actions run `46054595810` `success`, `53/53` pytest (`84.06s`) e `5/5` suítes Chrome CDP (`phase26`..`phase22`) aprovadas em produção sem erros de console/rede e `0px` overflow em `8` viewports.

## [2.2.0 — FASE 25] — 2026-11-27

### Auditoria Global, Inteligência Competitiva (32 Plataformas), PLG, Revenue Intelligence & Resiliência Cloud
- **Estrutura PLG & Medidores de Consumo Reais (`plans_and_audit.py`, `GET /api/v1/plans/overview`)**: Inclusão do tier **`FREE` (Ativação PLG)** ao lado de `STARTER`, `PRO`, `BUSINESS` e `ENTERPRISE` com preços referenciais auditados e medidores em tempo real por tenant (`empresas`, `usuários`, `leads`, `automações`, `ações IA`), mantendo **`billing_status: PLG_STRUCTURE_SIMULATION_ONLY_NO_LIVE_BILLING`** e zero cobrança automática ativa.
- **CRM Revenue Intelligence & Ativação TTFV (`phase25_product_engine.py`)**:
  - `GET /api/v1/growth-os/revenue-intelligence` & `POST /api/v1/crm/leads/{lead_id}/quick-followup`: detecção de leads quentes sem contato (`score >= 65`), negociações estagnadas (`>= 5 dias` ou sem atividade CRM) e agendamento de follow-up em 1 clique com bloqueio LGPD (`opt_out`).
  - `GET /api/v1/growth-os/activation-retention`: checklist de 6 marcos reais de Time-to-First-Value + `daily_return_triggers` exibido discretamente em `HomeWorkspace.tsx` até `first_value_achieved`.
- **SEO Técnico Ao Vivo (`seo_and_market_engine.py`)**: Extração HTTP pública real de `canonical_url`, `has_viewport`, tags OpenGraph (`og_title`/`og_description`/`og_image`) e `body_word_count` sem custo adicional, além de disclaimer transparente de Google Search Console.
- **Decomposição Modular & DS 3.0 (`CommercialRevenueWorkspace.tsx`, `AIEnginesHubWorkspace.tsx`, `UnionGrowthOSPortal.tsx`, `AITeamAndGovernanceView.tsx`)**: Extração de ~1.500 linhas do monólito principal para módulos DS 3.0 Obsidian/Alabaster (Leads & CRM, Pipeline Kanban, Multinegócio com funil de 17 etapas colapsável, Concorrentes, AI Engine Hub sem abas numeradas e painel `PlansAndUsagePanel`), correção do aviso enganoso de chave IA ausente e hidratação **Wave 1 + Wave 2** com trava `loadSeqRef`.
- **Infraestrutura, CI/CD & Validação E2E Total**: Adicionado `--timeout-keep-alive 75 --proxy-headers` no `Dockerfile` (zerando `502` no swap Traefik/Uvicorn), correção de scanner regex no `.github/workflows/ci-cd.yml`, tolerância a swap no `scripts/ci_deploy_and_verify.py` (GitHub Actions run `46043812259` `success`), **`52/52` testes `pytest`** aprovados e **4 suítes Chrome CDP ao vivo** (`phase25_cdp_e2e.py`, `phase24_cdp_e2e.py`, `phase23_cdp_e2e.py`, `phase22_cdp_ux_e2e.py`) 100% verdes em produção, com 21 relatórios independentes e Scorecard.

## [2.1.0 — FASE 24] — 2026-11-27

### Reconstrução Radical de UX/UI & Design System 3.0
- **Design System 3.0 (`globals.css`, `DesignSystem.tsx`)**: Nova identidade visual Obsidian Dark (`#09090b`, `#0c0c0f`, `#111115`) & Crisp Alabaster Light (`#fafafa`, `#ffffff`, `#f4f4f5`) com contornos hairline (`divide-y` / `divide-x`), `.tabular-nums`, `MetricStrip`, `FilterTabBar` underline, `OriginBadge` sem quebra (`whitespace-nowrap shrink-0`) e `Drawer` acessível (`Escape`, `aria-modal`).
- **Workspace Executivo Único (`HomeWorkspace.tsx`, `GrowthCommandCenter.tsx`)**: Eliminação do duplo dashboard empilhado na rota `overview`, unificando saudação, checklist discreto de 6 etapas, **ASK UNION Spotlight Strip**, faixa de métricas reais, `Prioridades de hoje`, `AI CEO Briefing`, `Oportunidades` e `BusinessHealthAndScoreDrawer` sob demanda (`12` dimensões + fórmula auditável do Growth Score).
- **Fim da Muralha de Instruções (`AreaContextGuide.tsx`) & Navegação Minimalista (`page.tsx`, `ResourceCenterAndHelp.tsx`)**: Remoção das 5 caixas permanentes do topo de todas as telas (agora acessíveis sob demanda via `Como funciona esta área`), Sidebar enxuta com Favoritos/Recentes discretos, **Meu Trabalho (`MyWorkHub.tsx`)** em lista de triagem estilo Linear e diretório **Todos os recursos** agrupado por categoria sem grade de 27 caixas.
- **Modo Simples em Linguagem Natural (`plainLanguage.ts`)**: Tradução automática de termos técnicos (*Webhook*, *Rate limit*, *Provider*, *Trigger*, *Dry-Run*) no **Modo Simples**, preservando controles técnicos no **Modo Avançado**.
- **Performance, Telemetria & Qualidade Validada em Produção**: Bundle reduzido na rota `/` de `74.2 kB` (First Load `180 kB`) para **`71.3 kB` (First Load `177 kB`)**, exposição de `aria-busy`/`data-loading` no botão `Atualizar Dados`, **`51/51` testes `pytest`**, suíte Chrome CDP **Fase 24 (`3` perfis + `7` viewports `0px` overflow + `61` botões sem falhas)**, **Fase 23 (`20/20` jornadas)** e **Fase 22 (`S01..S15` incluindo `S08`)** todas 100% aprovadas em produção.

## [2.0.0 — FASE 23] — 2026-11-26

### Adicionado & Evoluído
- **FASE 23 (World-Class AI Growth Platform, UX Revolution 2.0 & Competitive Intelligence)**:
  - **Inteligência Competitiva (15 Plataformas)**: Análise comparativa documentada de HubSpot, GoHighLevel, Jasper, Salesforce Agentforce, Adobe GenStudio, Semrush, Mailchimp, Canva, Notion, Intercom, Metricool, Stripe, Amplitude, Linear e Make.
  - **AI Growth Command Center (`GrowthCommandCenter.tsx`)**: Painel executivo consolidando **Business Health em 12 dimensões** (`REAL`/`ESTIMATIVA`/`NAO_DISPONIVEL`), **Growth Score Documentado (0–100)** com metodologia auditável, **AI CEO Briefing (Hoje & Semana)**, **Opportunity Radar** e **Executive Action Center**.
  - **ASK UNION (Copiloto Contextual)**: Interpretação de objetivos em português natural conectados ao estado real do tenant para montar planos estruturados e ações rastreáveis (`AskUnionActionLog`).
  - **Modo Simples vs. Modo Avançado Persistente e Real**: Seletor `#ug-ui-mode-toggle` persistido em banco (`tenants.ui_mode`) e `localStorage`, ocultando realmente sub-abas técnicas (`advancedOnly`) no Modo Simples com atalho `+ N Avançado` (`#ug-reveal-advanced-subtabs`), além de simplificação visual em Automações 24/7 e layout responsivo validado de `1920x1080` a `360x800`.
  - **Onboarding Inteligente Progressivo (6 Etapas)**: Fluxo recuperável e reiniciável em banco (`onboarding_step`, `onboarding_state_json`).
  - **Brand Intelligence Center**: Central visual/verbal única (`brand_voice`, `brand_fonts`, `brand_differentials`, `brand_allowed_terms`, `brand_forbidden_terms`, `brand_examples`), versionamento (`brand_versions`) e detector automático de inconsistências.
  - **12 Especialistas de IA (`AGENT_12_DATA_ANALYST`) & Resiliência**: Adição oficial do `AI Data Analyst`, cache TTL (`180s`) + circuit breaker (`90s`, resetável ao salvar credencial e avaliado após validações estáticas) no `AIRouter` preservando `FREE_ONLY`, cache de status Ollama e alargamento PostgreSQL de `AgentExecutionLog.provider_used` para `VARCHAR(180)`.
  - **Automation Builder Conversacional Nativo Python**: Construção e simulação dry-run em linguagem natural convertendo pedidos em `AutomationRule` Python/`APScheduler` (0% dependência de `n8n`).
  - **Analytics & Attribution Hub**: Funil de 6 etapas e atribuição First-Touch real em CRM/Financeiro, com estado transparente `NAO_DISPONIVEL` para analytics externos sem OAuth.
  - **Hardening SSRF, RBAC, CI/CD v7 & Qualidade**: Proteção anti-SSRF (`validate_public_http_url` / `safe_public_http_get`), alinhamento RBAC (`manager` em mutações Fase 23), pipeline `actions/checkout@v7` + `setup-python@v7` + `setup-node@v7` (Node 22), **`51/51` testes `pytest`** (`test_01..test_50`), e suíte E2E Chrome CDP em produção (**`20/20` jornadas** + regressão `S01..S15` + `6` viewports sem overflow).

## [1.0.0] — 2026-11-10

### Adicionado
- **FASE 1 (Auditoria)**: Mapeamento completo do ambiente local e infraestrutura Cloud Coolify/Traefik.
- **FASE 2 & 3 (Arquitetura & Fundação)**: Backend FastAPI + SQLAlchemy (PostgreSQL + fallback SQLite), autenticação JWT + bcrypt, RBAC, isolamento Multi-Tenant e planos SaaS (`STARTER`, `PRO`, `BUSINESS`, `ENTERPRISE`).
- **FASE 4 (11 Agentes & Orquestrador)**: Implementação dos 11 agentes (`AI CEO`, `AI CMO`, `AI SEO Director`, `AI Social Media Director`, `AI Creative Studio`, `AI Copywriter`, `AI Growth Hacker`, `AI Sales Director`, `AI Competitive Intelligence`, `AI Finance & Performance`, `AI Customer Success`) e `CentralOrchestrator` com contratos tipados e prevenção de ciclos.
- **FASE 5 (Conteúdo & Criativos)**: Geração real de imagens PNG com `Pillow`, carrosséis, roteiros de vídeo, e-books, copies A/B e `SEO Content Factory`.
- **FASE 6 (Comercial & CRM)**: CRM completo com Leads, Empresas, Negociações, Atividades, Lead Scoring automático (0–100), validação LGPD e previsão comercial ponderada.
- **FASE 7 (Automações Nativas)**: `APScheduler` 100% em Python com as 12 regras de automação predefinidas, controle de concorrência, idempotência e retry com backoff exponencial.
- **FASE 8 (Integrações Oficiais)**: Catálogo de 16 integrações com guia de ativação, criptografia Fernet e testadores reais de conexão (SMTP, Meta Graph API, Mercado Pago, etc.).
- **FASE 9 (Segurança & Governança)**: Rate limiting, headers de segurança, sanitização anti-XSS, trava de alto impacto e backup completo JSON/SQLite.
- **FASE 10, 11 & 12 (Produção Cloud, Validação & Otimização)**: Painel Executivo Next.js 15 TypeScript Tailwind CSS com 20 seções, suíte `pytest` aprovada e deploy automatizado em nuvem com HTTPS no Coolify.
- **FASE 13 (Auditoria Real, Autonomia & Ativação Comercial)**:
  - Invalidação da senha inicial fraca padrão e rotação forçada (`must_change_password`).
  - Proteção contra força bruta em logins (8 falhas / 5 min) e CORS restrito a origens permitidas.
  - Sistema de IA Híbrido Real com motor Python determinístico, rastreamento honesto de origem (`response_origin`) e controle diário de tokens (`AIUsageTracker`).
  - Auditoria completa dos 11 agentes e matriz de capacidades (sem fingir LLM onde opera template ou regra determinística).
  - Pipeline de Operação de Marketing em 10 etapas integradas ponta a ponta (`POST /api/v1/marketing/full-operation-pipeline`).
  - Auditoria individual e categorização das 6 redes sociais (`GET /api/v1/social/platforms-audit`) e rotas OAuth 2.0 oficiais.
  - Auditoria técnica de SEO real integrada à API pública Google PageSpeed Insights v5, sitemap.xml e robots.txt dinâmicos.
  - Scheduler APScheduler 100% nativo em Python sincronizado no PostgreSQL (`scheduler_heartbeats`), idempotência comprovada e recuperação após reinício (`BOOT`/`CATCHUP`).
  - Assistente de Onboarding da Primeira Empresa (`POST /api/v1/onboarding/company`) sem inventar dados, gerando planos e diagnósticos a partir de informações informadas.
  - Painel de Autonomia por Agente e limites operacionais estritos (`PUT /api/v1/autonomy/limits`), garantindo aprovação humana obrigatória para ações financeiras.
  - Suíte de testes automatizados expandida para 25 testes aprovados (`25 passed`).

