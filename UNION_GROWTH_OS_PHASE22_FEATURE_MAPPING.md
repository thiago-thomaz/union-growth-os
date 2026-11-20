# FASE 22 — MAPEAMENTO COMPLETO DE FUNCIONALIDADES PRESERVADAS (100% PARIDADE)

Este documento comprova que **nenhuma funcionalidade existente do UNION GROWTH OS foi removida, desativada ou ocultada** na reestruturação da Fase 22. Os 26 módulos originais da barra lateral plana foram reorganizados em **6 Áreas Principais Orientadas a Tarefas** + **Central de "Todos os Recursos"** pesquisável e **Central de Comandos (`Ctrl+K`)**.

---

## 1. Estrutura de Navegação Nova vs Anterior

| Estrutura Anterior (Sidebar Plana — 26 Menus) | Nova Área Principal | Submenu Contextual (Subtab Horizontal) | Código Interno (`LegacyMenuId`) | Modo de Acesso Direto |
|---|---|---|---|---|
| **01. Visão Geral (AI CEO)** | **Início** | *(Visão Inicial Executiva — 5 Blocos + Onboarding)* | `ceo` | Menu `Início` ou `Ctrl+K` ("Visão Geral" / "Início") |
| *(Novo Hub Unificado)* | **Meu Trabalho** | *(Caixa Unificada com 7 Filtros + Drawer)* | `my_work` | Menu `Meu Trabalho`, Notificações Header, `Ctrl+K` |
| **14. CRM (AI Sales)** | **Comercial** | **Leads & CRM** (com busca por nome/empresa/status) | `crm` | `Comercial -> Leads & CRM`, `Ctrl+K` ("Lead") |
| **15. Pipeline Comercial** | **Comercial** | **Pipeline & Propostas** (Kanban e movimentação de estágio) | `commercial` | `Comercial -> Pipeline & Propostas`, `Ctrl+K` |
| **17M. Sistema Comercial Multinegócio** | **Comercial** | **Propostas & 3 Unidades** (inclui botão seguro PDF Blob) | `multibusiness` | `Comercial -> Propostas & 3 Unidades`, `Ctrl+K` ("Proposta") |
| **16. Concorrentes** | **Comercial** | **Concorrentes** (análise respeitando `robots.txt`) | `competitors` | `Comercial -> Concorrentes`, `Todos os recursos` |
| **18. Customer Success (NPS/Churn)** | **Comercial** | **Clientes & NPS** (feedbacks, retenção e churn) | `cs` | `Comercial -> Clientes & NPS`, `Todos os recursos` |
| **02. Planejamento Marketing** | **Marketing** | **Campanhas** (busca e ROI por canal) | `marketing` | `Marketing -> Campanhas`, `Ctrl+K` ("Campanha") |
| **04. Fábrica de Conteúdo AI** | **Marketing** | **Fábrica de Conteúdo** (lote multicanal + download) | `content_factory` | `Marketing -> Fábrica de Conteúdo`, `Ctrl+K` |
| **05. Redes Sociais** | **Marketing** | *(Unificado no submenu)* **Calendário & Redes** | `calendar` *(alias `social`)* | `Marketing -> Calendário & Redes` |
| **18. Calendário Editorial** | **Marketing** | **Calendário & Redes** (agenda multicanal + status) | `calendar` | `Marketing -> Calendário & Redes`, `Ctrl+K` |
| **03. SEO & Conteúdo** | **Marketing** | **SEO & Artigos** (auditoria técnica, clusters, Schema.org) | `seo` | `Marketing -> SEO & Artigos`, `Ctrl+K` ("SEO") |
| **10. Criativos & Design** | **Marketing** | **Criativos & Vídeos** (render PNG/MP4 e galeria local) | `creative` | `Marketing -> Criativos & Vídeos`, `Todos os recursos` |
| **11. Copywriting & Ads** | **Marketing** | **Copywriting & Ads** (variantes AIDA/PAS e A/B) | `copywriter` | `Marketing -> Copywriting & Ads`, `Todos os recursos` |
| **13. Growth & Experimentos** | **Marketing** | **Growth & Experimentos** (ICE Score e resultados reais) | `growth` | `Marketing -> Growth & Experimentos`, `Todos os recursos` |
| **25. UNION AI Engine Hub** *(Visão Geral)* | **Inteligência Artificial** | **Visão & Agentes** (cards leigos + painel técnico colapsável) | `ai_team_overview` | `Inteligência Artificial -> Visão & Agentes` |
| **25. UNION AI Engine Hub** *(Motores/Chaves)* | **Inteligência Artificial** | **Modelos & Provedores** (Gemini, `FREE_ONLY`, 10 subtabs originais) | `ai_engines` | `Inteligência Artificial -> Modelos & Provedores`, `Ctrl+K` ("Gemini") |
| **07. CEO Daily Plan (OKRs)** | **Inteligência Artificial** | **Plano Diário AI CEO** (briefings e missões diárias) | `ceo_plan` | `Inteligência Artificial -> Plano Diário AI CEO` |
| **08. Operação 24/7 & Alertas** | **Inteligência Artificial** | **Operação 24/7 & Alertas** (rotinas contínuas e alertas) | `operational247` | `Inteligência Artificial -> Operação 24/7 & Alertas` |
| **19. Automações & Regras** | **Inteligência Artificial** | **Automações** (regras nativas em Python sem n8n) | `automations` | `Inteligência Artificial -> Automações`, `Ctrl+K` |
| **09. Piloto 7 Dias** | **Inteligência Artificial** | **Piloto 7 Dias** (simulação/teste controlado de operação) | `pilot7d` | `Inteligência Artificial -> Piloto 7 Dias` |
| **17. Financeiro & KPIs** | **Gestão** | **Financeiro** (receita real x importada x estimada) | `finance` | `Gestão -> Financeiro`, `Ctrl+K` ("Financeiro") |
| **21. Relatórios Executivos** | **Gestão** | **Relatórios** (cards visuais + backup + JSON colapsável) | `reports` | `Gestão -> Relatórios`, `Ctrl+K` ("Relatório") |
| **22. Integrações Oficiais** | **Gestão** | **Integrações** (filtro Todas/Conectadas/Pendentes + Fernet) | `integrations` | `Gestão -> Integrações`, `Ctrl+K` ("Integrações") |
| **23. Configurações & Autonomia** | **Gestão** | **Configurações** (empresa, planos e níveis 1/2/3 de autonomia) | `settings` | `Gestão -> Configurações`, `Todos os recursos` |
| **24. Auditoria & Logs** | **Gestão** | **Auditoria & Logs** (trilha imutável e execuções) | `audit` | `Gestão -> Auditoria & Logs`, `Todos os recursos` |
| **20. Aprovações** *(legado)* | **Meu Trabalho** | **Central Completa de Aprovações** | `approvals` | Botão "Abrir Central" / `Todos os recursos` |
| *(Novo Catálogo Unificado)* | **Todos os recursos** | *(Busca por palavra-chave + categorias + Favoritos + Recentes)* | `all_resources` | Rodapé da Sidebar ou final do `Ctrl+K` |

---

## 2. Redundâncias Resolvidas sem Quebra de Compatibilidade

1. **Redes Sociais (`social`) + Calendário Editorial (`calendar`)**:
   - Anteriormente exibidos como dois botões separados na sidebar competindo pelo mesmo fluxo visual.
   - Agora unificados sob **`Marketing -> Calendário & Redes`**, mantendo compatibilidade interna com o ID `calendar` (e fallback seguro se qualquer rotina chamar `social`).
2. **Aprovações (`approvals`) + Alertas (`operational247`) + Tarefas de Follow-up (`crm`)**:
   - Continuam existindo em seus módulos especializados, mas passam a convergir na caixa unificada **`Meu Trabalho`**, reduzindo o atrito de abrir 3 telas diferentes para checar pendências do dia.
3. **Configuração de IA vs Execução de Agentes (`ai_team_overview` + `ai_engines`)**:
   - Usuário iniciante acessa **`Inteligência Artificial -> Visão & Agentes`** para compreender em linguagem clara o que cada especialista faz, quando roda e se exige aprovação.
   - Usuário técnico continua acessando o hub completo **`Modelos & Provedores`** (`ai_engines`) com todas as 10 abas (Dashboard AI, Provedores, Modelos, Agentes, Image Studio, Video Studio, Copy Studio, Custos, Histórico e Testes) preservadas na íntegra.
4. **Relatórios Executivos (`reports`)**:
   - Anteriormente exibia exclusivamente um bloco `<pre>` JSON técnico bruto na tela principal.
   - Agora apresenta 4 KPIs executivos + resumo do CEO Briefing em texto legível, preservando o JSON integral dentro de um `<details>` colapsável ("Ver Detalhes Técnicos Completos").

---

## 3. Fluxos Públicos e Transversais Preservados

- **Autenticação & Multi-Tenant (`#ug-tenant-select`)**: Preservado no topo da sidebar (quando expandida), mantendo isolamento por empresa e suporte imediato a `QA_AUTOMATED_TENANT`.
- **Download Seguro de PDF (`multibusiness`)**: Preservado com `fetch(p.pdf_url, { headers: Authorization })` + `URL.createObjectURL(blob)`, sem exposição de `access_token` em URLs.
- **Landing Page Pública (`/lp/agentes-ia`)**: Preservada 100% funcional para visitantes deslogados com captura de lead LGPD.
- **Persistência no Navegador (`localStorage`)**: Tema Claro/Escuro (`ug_theme_mode`), Sidebar Recolhida (`ug_sidebar_collapsed`), Checklist de Onboarding Dispensado (`ug_onboarding_dismissed`), Favoritos (`ug_favorite_resources`) e Módulos Recentes (`ug_recent_resources`).
