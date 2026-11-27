# FASE 24 — AUDITORIA INDEPENDENTE DE UX/UI & ARQUITETURA VISUAL

**Produto**: `UNION GROWTH OS` (`https://automacao.projetosunion.cloud`)  
**Baseline Auditada**: Commit `8df9f6770b33fa3316fa8fac30206b11ec742b50` (Fase 23)  
**Método**: Inspeção direta do código (`frontend/src/` — 14 arquivos, `page.tsx` com `5.531` linhas) e análise visual das capturas reais de produção (`1920x1080` e `360x800`).

---

## 1. Diagnóstico Estrutural Real (Evidências Observadas)

| # | Problema Estrutural Encontrado | Onde Ocorre no Código / Tela | Impacto na Experiência | Solução Estrutural Fase 24 |
|---|---|---|---|---|
| 1 | **Dashboard Duplicado na Home ("Double Dashboard")** | `page.tsx` L1118–1194 renderiza `<GrowthCommandCenter />` + `<HomeWorkspace />` empilhados em `overview` | Repetição de saudação, Onboarding (botão + banner 8 cards), AI CEO Briefing (2x), ações (Executive Action Center + Bloco 1) e KPIs (Business Health 12 + Bloco 3) | Consolidar tudo em **1 único Executive Workspace** sereno com 6 áreas integradas sem redundância |
| 2 | **Muralha Permanente de Instruções (`AreaContextGuide`)** | `page.tsx` L1109 renderiza 5 caixas bordadas (`~220px` desktop / `>750px` no mobile `360x800`) no topo de TODAS as telas | Em `360x800`, 100% da primeira dobra mostra só texto de instrução; em `Marketing` e `Início`, empurra a operação real para baixo | Substituir o bloco fixo de 5 caixas por gatilho discreto **Drawer sob demanda** ("Como funciona?") sem ocupar dobra |
| 3 | **Fadiga de "Card Dentro de Card"** | `GrowthCommandCenter.tsx`, `HomeWorkspace.tsx`, `MyWorkHub.tsx`, `BrandAndOnboardingHub.tsx`, `page.tsx` (`multibusiness`, `marketing`) | Bordas `slate-800` sobre `#0f1629` sobre `#070b14` + dezenas de pills concorrendo sem hierarquia | Adotar **Design System 3.0**: superfícies neutras Obsidian/Alabaster, divisores hairline (`divide-y`), strips horizontais (`divide-x`) e zero borda aninhada desnecessária |
| 4 | **Monólito `page.tsx` (`5.531` linhas)** | `frontend/src/app/page.tsx` | Manutenção pesada, repetição visual de tabelas/formulários e falta de primitivas uniformes | Extrair componentes reutilizáveis do Design System 3.0 e unificar padrões de lista, cabeçalho e métricas |
| 5 | **Sidebar e Header Repetitivos** | `page.tsx` L676–1095 | Sidebar com busca + selector + 6 blocos indigo sólidos chamativos; Header repete empresa/plano/autonomia e usa caixas bordadas nos submenus | Reconstruir Sidebar minimalista (indicador ativo sutil, favoritos/recents discretos), Header enxuto e subnavegação em tabs com underline limpa |
| 6 | **ASK UNION Encaixotado** | `GrowthCommandCenter.tsx` L112–223 | Mais um card gigante bordado competindo com outros 6 cards | Transformar em **Spotlight Strip natural** integrado à Home com input direto, 3 sugestões sutis e resposta acionável limpa |
| 7 | **Meu Trabalho & Todos os Recursos com Peso Visual** | `MyWorkHub.tsx` (cards individuais + 7 botões em caixas), `AllResourcesHub.tsx` (grade pesada de 27 cards) | Excesso de bordas e ruído ao triar tarefas ou buscar uma ferramenta | **Meu Trabalho**: tabela/lista de triagem estilo Linear com tabs underline + Drawer lateral.<br>**Todos os recursos**: diretório pesquisável em lista agrupada por categoria |
| 8 | **Jargão Técnico no Modo Simples** | Termos como *APScheduler*, *Cron*, *Dry-Run*, *Webhook*, *Provider*, *Rate limit* expostos sem tradução | Usuário empreendedor leigo precisa interpretar conceitos de engenharia | Criar camada adaptativa de linguagem simples (`Conectar ferramenta externa`, `Limite de solicitações`, `Serviço de IA`, `Quando essa automação deve começar`, `Simular antes de ativar`) |

---

## 2. Inventário Auditado da Base Existente (`frontend/src/`)
- `src/app/page.tsx`: `5.531` linhas (`296 kB`) — Shell + login + todas as telas legadas + estado global.
- `src/components/HomeWorkspace.tsx`: `550` linhas — Home 5 blocos (duplicada com `GrowthCommandCenter`).
- `src/components/GrowthCommandCenter.tsx`: `459` linhas — ASK UNION, Growth Score, AI CEO Briefing, Business Health 12, Radar, Executive Action Center.
- `src/components/MyWorkHub.tsx`: `469` linhas — Fila unificada de ações + Drawer lateral.
- `src/components/BrandAndOnboardingHub.tsx`: `503` linhas — Onboarding 6 etapas + Central de Marca.
- `src/components/AITeamAndGovernanceView.tsx`: `534` linhas — Assistente IA + 12 agentes.
- `src/components/ConversationalAutomationAndAnalytics.tsx`: `202` linhas — Automação conversacional + Analytics First-Touch.
- `src/components/AreaContextGuide.tsx`: `231` linhas — Guia permanente de 5 caixas no topo de cada módulo.
- `src/components/ResourceCenterAndHelp.tsx`: `299` linhas — Catálogo de 27 recursos + Help Drawer.
- `src/components/DesignSystem.tsx`: `234` linhas — `OriginBadge`, `StatusPill`, `EmptyState`, `SkeletonCard`, `Drawer`, `ToastBanner`.
- `src/components/CommandCenter.tsx`: `326` linhas — Busca Global `Ctrl+K`.
- `src/lib/navigation.ts`: `203` linhas — Configuração de 6 áreas + 27 recursos + `advancedOnly`.
