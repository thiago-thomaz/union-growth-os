# UNION GROWTH OS — FASE 26: DESIGN SYSTEM 4.0

**Versão:** `2.3.0 — FASE 26`  

## 1. Tokens Obsidian & Alabaster (`globals.css`)
- **Obsidian Dark (`html.dark`)**: fundo `--ug-bg: #09090b`, superfícies `--ug-surface: #0c0c0f` / `--ug-surface-elevated: #111115`, bordas hairline `--ug-border`, texto `--ug-text-primary`, `--ug-text-secondary`, `--ug-text-muted`.
- **Alabaster Light (`html.light`)**: fundo `--ug-bg: #fafafa`, cartões crisp `#ffffff`, divisórias `#e4e4e7`, contraste calibrado para leitura confortável em ambientes claros — incluindo Login e pós-venda CS na Fase 26.

## 2. Componentes Centrais (`DesignSystem.tsx`)
| Componente | Papel na Interface | Evolução na Fase 26 |
| :--- | :--- | :--- |
| `MetricStrip` | Faixa horizontal estilo Stripe com divisor `divide-x` | Inclusão das props `source?: string` e `period?: string` com tipografia `tabular-nums` |
| `PlainOrientationBar` | Barra compacta 1 linha orientando usuário leigo em módulos complexos | Adicionado na Fase 26 (`whatIsIt`, `whyUseIt`, `nextStep`) sem virar parede de texto |
| `OriginBadge` | Tag inquebrável de honestidade de dados | `REAL`, `IMPORTED`, `ESTIMATED`, `GOAL`, `SANDBOX`, `SIMULATION` |
| `StatusPill` | Badge padronizada (`EXECUTED`, `PENDING`, `BLOCKED`, `FAILED`, `NEEDS_CREDENTIALS`) | Aplicada em Matriz de Agentes, Billing Readiness e Aprovações |
| `FilterTabBar` | Abas de filtro semânticas com contadores | Reutilizada nos horizontes `Todos / Hoje / 7 Dias / 30 Dias / 90 Dias` |
| `EmptyState` / `Drawer` / `ToastBanner` | Estados vazios acionáveis e gavetas acessíveis (`Escape` + `aria-modal`) | Mantidos consistentes em todos os novos workspaces |
