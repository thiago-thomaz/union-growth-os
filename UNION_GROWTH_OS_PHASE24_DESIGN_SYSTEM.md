# FASE 24 — DESIGN SYSTEM 3.0 (SPECIFICATION & TOKENS)

**Filosofia**: Inspiração estrutural em **Linear**, **Stripe**, **Attio**, **Notion** e **Vercel** — neutralidade arquitetural, respiro visual, contraste WCAG 2.2 AA e densidade informacional controlada sem excesso de bordas ou containers concorrentes.

---

## 1. Tokens Semânticos (`frontend/src/app/globals.css`)

### Dark Canvas (`Obsidian Precision`)
- `--ug-bg`: `#09090b` (fundo principal neutro)
- `--ug-sidebar`: `#0c0c0f` (barra lateral discreta separada por hairline `1px`)
- `--ug-surface`: `#111115` (superfície primária de seção/painel)
- `--ug-surface-2`: `#18181d` (hover / linhas elevadas sem precisar de nova borda)
- `--ug-border`: `rgba(255, 255, 255, 0.08)` (contorno hairline primário)
- `--ug-border-subtle`: `rgba(255, 255, 255, 0.05)` (divisores de lista `divide-y` e colunas `divide-x`)
- `--ug-text-primary`: `#fafafa`
- `--ug-text-secondary`: `#a1a1aa`
- `--ug-text-muted`: `#71717a`
- `--ug-accent`: `#6366f1` / `--ug-accent-soft`: `rgba(99, 102, 241, 0.14)`

### Light Canvas (`Crisp Alabaster`)
- `--ug-bg`: `#fafafa`
- `--ug-sidebar`: `#f4f4f5`
- `--ug-surface`: `#ffffff` (sombra hairline `0 1px 2px rgba(9, 9, 11, 0.04)`)
- `--ug-surface-2`: `#f4f4f5`
- `--ug-border`: `#e4e4e7`
- `--ug-border-subtle`: `#f0f0f2`
- `--ug-text-primary`: `#09090b`
- `--ug-text-secondary`: `#52525b`
- `--ug-text-muted`: `#71717a`
- `--ug-accent`: `#4f46e5` / `--ug-accent-soft`: `rgba(79, 70, 229, 0.09)`

---

## 2. Tipografia & Escala Espacial
- **Família**: `"Inter", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` (sem dependência de rede externa no build).
- **Números Tabulares (`.tabular-nums`)**: obrigatório em contadores, datas, scores (`XX/100`), moeda (`R$`) e tabelas.
- **Hierarquia Estrita (máx. 4 níveis ativos por tela)**:
  1. Page Title (`18px–20px`, `font-semibold`, `-0.02em` tracking)
  2. Section Heading (`13px`, `font-semibold`)
  3. Primary Content / List Row (`13px`, `font-medium`)
  4. Metadata / Origin / Helper (`11px–12px`, `--ug-text-muted`)

---

## 3. Catálogo de Componentes Primitivos (`frontend/src/components/DesignSystem.tsx`)
1. **`OriginBadge`**: chip discreto com ponto cromático `6px` + texto semântico (`Dado Real`, `Estimativa`, `Sandbox`, `Teste QA`, `Não Disponível`) sem bordas pesadas.
2. **`StatusPill`**: indicador de estado minimalista (`Executado`, `Aguardando Aprovação`, `IA Executando`, `Bloqueado`, `Falhou`, `Pendente`) com ícone/dot discreto.
3. **`MetricStrip`**: faixa horizontal unificada com divisores hairline (`divide-y sm:divide-y-0 sm:divide-x`) para KPIs sem criar 5 cards independentes.
4. **`ListSurface` & `ListRow`**: contêiner limpo com separadores finos (`divide-y`) substituindo pilhas de `.rounded-xl border` por item.
5. **`FilterTabBar`**: abas de filtro em estilo underline com badge numérico discreto, zero botões encapsulados.
6. **`SectionBlock`**: bloco editorial leve com título + resumo curto + ação à direita.
7. **`Drawer`**: painel deslizante lateral com suporte completo a `Escape`, foco e `aria-modal`.
8. **`EmptyState` & `SkeletonCard` & `ToastBanner`**: estados vazios serenos com 1 CTA claro, placeholders `animate-pulse` respeitando `prefers-reduced-motion` e notificações discretas de canto.
