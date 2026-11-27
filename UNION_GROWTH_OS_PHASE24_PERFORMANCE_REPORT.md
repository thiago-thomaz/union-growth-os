# FASE 24 — RELATÓRIO DE PERFORMANCE, BUNDLE & LATÊNCIA OBSERVADA

**Framework**: Next.js `15.1.3` (App Router com Static Export `frontend/out/`) servida diretamente pelo Uvicorn/FastAPI em produção.

---

## 1. Evolução do Bundle de Produção (`npm run build`)

| Métrica de Build | Baseline Fase 23 (`4dacfb2` / `8df9f67`) | Fase 24 Final (`cb67ad84`) | Variação |
|---|---|---|---|
| Rota `/` (App JS + página) | `74.2 kB` | **`71.3 kB`** | **`-2.9 kB` (`-3.9%`)** |
| First Load JS da Rota `/` | `180 kB` | **`177 kB`** | **`-3.0 kB` (`-1.7%`)** |
| Rota `/_not-found` | — | **`979 B`** (First Load `106 kB`) | Estável |
| First Load JS Compartilhado | — | **`105 kB`** (`52.9 kB` + `50.5 kB` + `1.94 kB`) | Leve & estático |

*Conclusão do Build*: Mesmo após reconstruir todos os módulos de UX, adicionar a camada `plainLanguage.ts`, os componentes do `DesignSystem 3.0`, o `BusinessHealthAndScoreDrawer` e o glossário da Central de Ajuda, o bundle ficou **menor** que o da Fase 23 pela eliminação de markup duplicado e remoção de dezenas de containers aninhados.

---

## 2. Otimizações Estruturais & Latência Observada ao Vivo

1. **Zero Font/Asset Externo Bloqueante**: Tipografia declarada com pilha nativa moderna (`"Inter", ui-sans-serif, system-ui, ...`) em `globals.css` sem fetches bloqueantes de rede externa durante o carregamento inicial.
2. **Menos Nós DOM Acima da Dobra**: Consolidação da Home duplicada (`GrowthCommandCenter` + `HomeWorkspace`) e substituição de 5 cards fixos do `AreaContextGuide` + grade de 27 cards em `Todos os Recursos` por listas `divide-y` e drawers montados sob demanda.
3. **Cache & Circuit Breaker Preservados no Backend**: Cache TTL (`180s`) + disjuntor (`90s`) no `AIRouter` e cache de probe local (`30s`) em `ai_engines_hub.py`, sem chamadas extras por renderização.
4. **Tempos Medidos na Execução Live em Produção (`https://automacao.projetosunion.cloud`)**:
   - **`P1_Usuario_Iniciante`** (inclui login, verificação Home, ASK UNION, Drawer 12 pilares e troca Dark/Light): **`28.93s`**.
   - **`P2_Usuario_Operacional`** (Meu Trabalho, Drawer guia sob demanda, Marketing, Diretório de recursos): **`7.07s`**.
   - **`P3_Usuario_Avancado`** (alternância e verificação Modo Simples <-> Modo Avançado): **`6.43s`**.
   - **Execução Completa `phase24_cdp_e2e.py`** (todos os perfis, 7 viewports e 12 screenshots em nuvem): **`60.6s`** com `0` erros HTTP `4xx`/`5xx`.
   - **Regressão `phase22_cdp_ux_e2e.py`**: **`102` requisições de rede** atendidas em nuvem com **`0` falhas** (`network_failures_count: 0`).
