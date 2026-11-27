# UNION GROWTH OS — FASE 25: MAPEAMENTO DE FUNCIONALIDADES E REESTRUTURAÇÃO

## 1. Arquitetura de Navegação & Fluxos Consolidados (Sem Perda de Recursos)

| Área Principal | Submenu | Destino Modular / Estado DS 3.0 | Ação Executada na Fase 25 |
| :--- | :--- | :--- | :--- |
| **Início** | Workspace Executivo | [HomeWorkspace.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/HomeWorkspace.tsx) | Adicionada barra compacta de **6 marcos TTFV** (`activationData`) antes do `first_value_achieved`, mantendo `ASK UNION`, KPIs reais, Prioridades e AI CEO Briefing acima da dobra |
| **Meu Trabalho** | Central de Triagem (7 filtros) | [MyWorkHub.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/MyWorkHub.tsx) | Preservada com Drawer lateral acessível |
| **Comercial** | Leads & CRM | [CommercialRevenueWorkspace.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/CommercialRevenueWorkspace.tsx) | Extraído de `page.tsx`; reconstruído em DS 3.0 com **CRM Revenue Intelligence** + botão Follow-up 1 clique |
| **Comercial** | Pipeline & Vendas | [CommercialRevenueWorkspace.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/CommercialRevenueWorkspace.tsx) | Extraído e reconstruído com Kanban DS 3.0 + previsão ponderada |
| **Comercial** | Propostas, Contratos & 3 Unidades | [CommercialRevenueWorkspace.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/CommercialRevenueWorkspace.tsx) | Extraído; `17` etapas recolhidas por padrão (`Ver funil (17 etapas)`) e foco padrão em `Propostas PDF & Fechamento` |
| **Comercial** | Concorrentes | [CommercialRevenueWorkspace.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/CommercialRevenueWorkspace.tsx) | Extraído para visualização DS 3.0 |
| **Marketing** | SEO & Artigos | [UnionGrowthOSPortal.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/UnionGrowthOSPortal.tsx) | Atualizado para exibir `canonical_url`, `has_viewport`, OpenGraph, `body_word_count` e disclaimer SERP |
| **Marketing** | Campanhas, Fábrica 30, Calendário, Criativos, Copy, Growth | [UnionGrowthOSPortal.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/UnionGrowthOSPortal.tsx) | Preservados ponta a ponta (extração parcial planejada para Fase 26) |
| **Inteligência Artificial** | Visão & Agentes | [AITeamAndGovernanceView.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/AITeamAndGovernanceView.tsx) | Corrigido status enganoso de provedor ativo quando `has_credential === false` |
| **Inteligência Artificial** | Modelos & Provedores (9 sub-abas) | [AIEnginesHubWorkspace.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/AIEnginesHubWorkspace.tsx) | Extraído de `page.tsx`; substituídas abas numeradas legadas por `FilterTabBar` e selos honestos `AGUARDANDO CHAVE GRATUITA` vs `CONECTADO` |
| **Inteligência Artificial** | AI CEO, Automações 24/7, Piloto | `ConversationalAutomationAndAnalytics.tsx` + Portal | Copiloto/Automações enriquecidos no backend (`COMPETITIVE_INTEL`, `RETENTION_CHURN`, gatilhos stalled/SEO) |
| **Gestão** | Configurações & Planos | `PlansAndUsagePanel` + Portal | Grid PLG de 5 planos (`FREE`..`ENTERPRISE`) + 5 medidores reais de cota por tenant (sem cobrança ativa) |

---

## 2. Novos Endpoints Introduzidos na Fase 25
1. `GET /api/v1/plans/overview`: retorna catálogo PLG completo + `usage_meters` reais do tenant + flag `charge_enabled: false`.
2. `GET /api/v1/growth-os/revenue-intelligence`: leads quentes sem contato, negociações paradas (`>= 5 dias` ou sem atividade CRM), win rate, ticket médio e `next_best_actions`.
3. `POST /api/v1/crm/leads/{lead_id}/quick-followup`: agenda atividade `FOLLOW_UP`, recalcula score e avança lead de `NEW_LEAD` para `QUALIFICATION` (bloqueando se `opt_out` LGPD).
4. `GET /api/v1/growth-os/activation-retention`: calcula 6 marcos reais de ativação (`first_value_achieved`) e lista `daily_return_triggers` reais do PostgreSQL.
5. Enriquecimento sem breaking-change em `GET /api/v1/seo/overview` e `POST /api/v1/seo/audit`: campo `technical_signals` (`canonical_url`, `has_viewport`, `og_title`, `og_description`, `og_image`, `body_word_count`).
