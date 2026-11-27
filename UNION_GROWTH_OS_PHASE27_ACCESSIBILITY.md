# UNION GROWTH OS — AUDITORIA DE ACESSIBILIDADE & RESPONSIVIDADE (FASE 27)

## 1. Telemetria WCAG Verificada ao Vivo (`phase27_cdp_e2e.py`)

- **`document.documentElement.lang`:** **`pt-BR`**
- **`total_buttons` visíveis avaliados:** **`63`**
- **`unlabeled_buttons`:** **`0`**
- **`unlabeled_inputs`:** **`0`**
- **Atalhos & Modais Acessíveis:** `Drawer` com fechamento via `Escape`, `aria-modal` e rótulos explícitos (`aria-label` no `#ug-version-badge-btn`, toggle Light/Dark, Busca `Ctrl+K`, Modo Simples/Avançado e formulário de Marca).

## 2. Matriz Responsiva (`0px` Overflow Horizontal em 8/8 Resoluções)

| Viewport | `scrollWidth` | `clientWidth` | `overflowPx` | Status |
|---|---|---|---|---|
| `desktop_1920x1080` | `1914` | `1914` | `0` | `PASSED` |
| `desktop_1440x900` | `1434` | `1434` | `0` | `PASSED` |
| `notebook_1366x768` | `1360` | `1360` | `0` | `PASSED` |
| `compact_1024x768` | `1018` | `1018` | `0` | `PASSED` |
| `tablet_768x1024` | `768` | `768` | `0` | `PASSED` |
| `mobile_430x932` | `430` | `430` | `0` | `PASSED` |
| `mobile_390x844` | `390` | `390` | `0` | `PASSED` |
| `mobile_small_360x800` | `360` | `360` | `0` | `PASSED` |

- **Ajuste Mobile Executado na Fase 27:** ocultado `#ug-version-badge-btn` abaixo de `640px` (`hidden sm:inline-flex`), movendo o atalho clicável `v2.4.0` no mobile para o rodapé da sidebar para liberar integralmente a barra de título em `360x800` (`11_phase27_mobile_360x800.png`).
- **Pendência Honesta:** teste manual com leitores de tela (`NVDA` / `VoiceOver`) permanece pendente (`Categoria 23: 94.0/100`).
