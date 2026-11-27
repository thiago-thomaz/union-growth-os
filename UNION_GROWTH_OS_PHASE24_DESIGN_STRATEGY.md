# FASE 24 — ESTRATÉGIA DE RECONSTRUÇÃO UX/UI

**Objetivo**: Transformar o `UNION GROWTH OS` em um *Executive Growth Workspace* limpo, intuitivo e rápido, preservando 100% do backend FastAPI, regras de negócio, RBAC, multi-tenancy, `FREE_ONLY`, Python `APScheduler` (zero `n8n`) e fluxos existentes.

---

## 1. Pilares da Nova Experiência
1. **Corte Radical de Poluição Visual ("Zero Card-inside-Card")**:
   - Remoção definitiva do bloco permanente `AreaContextGuide` (5 caixas em todo cabeçalho de área) — substituído por guia sob demanda em `Drawer` lateral acionado por pill sutil **"Como funciona?"**.
   - Remoção da duplicação na Home (`GrowthCommandCenter` + `HomeWorkspace`) — criação de **1 Workspace Executivo Único** seguindo exatamente a arquitetura funcional de 6 camadas:
     1) **Cabeçalho Contextual + Barra Discreta de Onboarding** (ocultável / recuperável sem dominar a tela)
     2) **ASK UNION Spotlight Strip** (entrada direta natural + 3 atalhos leves + plano executável sob demanda)
     3) **Resumo Inteligente** (faixa horizontal hairline com KPIs reais + expansor sob demanda do **Business Health 12 dimensões** e fórmula auditável do **Growth Score**)
     4) **Prioridades de Hoje** (lista moderna de tarefas priorizadas com ação em 1 clique)
     5) **AI CEO Briefing & Oportunidades & Atividade do Sistema** (coluna contextual direta com resumo de hoje/semana, gaps acionáveis e timeline real)
     6) **Atalhos Rápidos & Diagnóstico Coordenado**
2. **Navegação Enxuta e Sem Sobrecarga**:
   - Sidebar (`240px` / `64px` colapsada) reduzida às 6 áreas principais (`Início`, `Meu Trabalho`, `Comercial`, `Marketing`, `Inteligência Artificial`, `Gestão`) + seção compacta de `Favoritos/Recentes` (quando existentes) + acesso `Todos os recursos`.
   - Subnavegação horizontal convertida em **underline tabs** limpas (`border-b`) sem botões encapsulados; opções técnicas permanecem ocultas em **Modo Simples** com liberação imediata no botão `+ N Avançado` ou `#ug-ui-mode-toggle`.
3. **Experiência Leiga vs. Avançada Real (`plainLanguage.ts`)**:
   - No **Modo Simples** (padrão), termos técnicos (*Webhook*, *Rate limit*, *Provider*, *Trigger*, *Dry-Run*) são traduzidos para linguagem natural empreendedora (*Conectar ferramenta externa*, *Limite de solicitações*, *Serviço de IA*, *Quando essa automação deve começar*, *Simular antes de ativar*), ocultando dumps técnicos/JSON até a troca para **Modo Avançado** ou clique explícito.
4. **Refatoração Visual Progressiva em Todas as Áreas**:
   - **Meu Trabalho**: triagem em lista contínua + underline tabs + `Drawer` lateral de decisão rápida.
   - **Todos os Recursos**: diretório pesquisável agrupado em listas limpas por categoria (fim da grade de 27 cards).
   - **Onboarding 6 Etapas**: stepper focado com barra de progresso contínua, sem grid de 6 blocos competindo.
   - **Brand Intelligence Center**: preview de marca + formulário limpo + auditoria acionável + histórico discreto.
   - **Automações & Analytics**: construtor em linguagem natural integrado em strip + funil comercial de 6 etapas em faixa única + tabela sem bordas pesadas.
   - **Comercial, Marketing, IA & Gestão**: harmonização completa para o Design System 3.0 (Obsidian Dark & Crisp Alabaster Light), removendo numerações legadas (`02.`, `03.`, `17M`) dos títulos principais e preservando todos os fluxos de negócio, formulários e controles de segurança/LGPD.
