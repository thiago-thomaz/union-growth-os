# UNION GROWTH OS — FASE 25: AUDITORIA DE DESIGN & INTERFACE (DS 3.0)

**Referência Visual Avaliada:** 9 capturas novas da Fase 25 (`UNION_GROWTH_OS_PHASE25_EVIDENCE/`) + 12 da Fase 24 + 12 da Fase 23 + 16 da Fase 22 inspecionadas diretamente.

---

## 1. Consistência do Design System 3.0 (Obsidian Dark & Alabaster Light)
- **Tokens Globais (`globals.css`, `DesignSystem.tsx`)**:
  - Superfícies Dark (`#09090b`, `#0c0c0f`, `#111115`) com divisórias hairline sutis (`divide-y divide-white/[0.05]`, `border-[var(--ug-border-subtle)]`).
  - Superfícies Light (`Alabaster #fafafa / #ffffff / #f4f4f5`) validadas em `08_phase25_light_mode_crm.png` e `04_phase24_home_light.png` sem perda de contraste em textos, botões ou inputs.
  - Tipografia `.tabular-nums` aplicada em todos os medidores financeiros, contadores do pipeline, medidores de cota PLG e métricas de SEO.
  - Selos sem quebra (`whitespace-nowrap shrink-0`): `OriginBadge` (`REAL`, `ESTIMATIVA`, `META`, `SANDBOX`, `SIMULACAO`) e `StatusPill`.

---

## 2. Correções Visuais Executadas na Fase 25
| Área Reconstruída | Antes | Depois (Fase 25) |
| :--- | :--- | :--- |
| **Leads & CRM** | Blocos inline antigos em `page.tsx` com estética azul legada | `CommercialRevenueWorkspace.tsx` com `MetricStrip` hairline, card de captura limpo, lista com busca e painel de ações comerciais ao lado |
| **Pipeline Kanban** | Kanban antigo em mistura de cores e espaços irregulares | `CommercialPipelineWorkspace`: 4 KPIs no topo + 6 colunas proporcionais em DS 3.0 (`Novo Lead`, `Qualificação`, `Proposta Enviada`, `Em Negociação`, `Venda Ganha`, `Perdida`) |
| **Multinegócio & Propostas** | 17 blocos zerados sempre abertos + cards dentro de cards | Seletor de 3 unidades + faixa `Transparência Financeira` + funil colapsável + 4 abas `FilterTabBar` underline |
| **Concorrentes** | Painel escuro isolado sem hierarquia | `CompetitorsIntelligenceWorkspace` em DS 3.0 |
| **AI Engine Hub (9 sub-abas)** | Abas numeradas (`1.`, `2.`... `9.`) e cards azulados antigos | `AIEnginesHubWorkspace.tsx` com `FilterTabBar`, `MetricStrip`, badges honestos e divisórias limpas |
| **SEO Técnico** | Exibia apenas score e título sugerido | Exibe chips técnicos reais: `Canonical`, `Mobile Viewport`, `OpenGraph`, contagem de palavras e disclaimer de Search Console |
| **Configurações -> Planos PLG** | Não existia comparativo nem medidores no portal | `PlansAndUsagePanel` com 5 barras de consumo reais e grid comparativo limpo de 5 colunas (`FREE` -> `ENTERPRISE`) |

---

## 3. Pontos Visuais Ainda Melhoráveis (Honestidade Visual)
1. **Tela de Login (`UnionGrowthOSPortal.tsx`)**: mantém card limpo, porém os botões de alternância `Entrar / Cadastrar` usam `bg-slate-900/90` em vez de tokens dinâmicos DS 3.0 para Modo Claro pré-login.
2. **Módulos Secundários ainda em `UnionGrowthOSPortal.tsx`**: telas menos acessadas (ex.: `creative`, `copywriter`, `growth`, `integrations`) ainda residem no arquivo grande de `4.028` linhas — embora já usem classes `.ug-card`, devem ser modularizadas em arquivos dedicados em Fase 26.
3. **Toast Temporário x Botões no Rodapé Direito**: conforme observado em `07_phase25_settings_plg_plans.png`, quando um toast dispara (`bottom-4 right-4`), ele se sobrepõe brevemente ao último card inferior direito se a rolagem estiver exatamente ali (desaparece automaticamente após timeout, sem bloquear o DOM).
