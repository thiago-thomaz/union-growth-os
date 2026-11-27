# FASE 24 — FLUXOS DE USUÁRIO VALIDADOS (3 PERFIS DE MATURIDADE)

**Ambiente Validado**: `https://automacao.projetosunion.cloud` (Tenant isolado `QA_AUTOMATED_TENANT`, commit `cb67ad84a2f82953ccc3ba8102e17141cc61fc6c`)  
**Script Automatizado**: `scripts/phase24_cdp_e2e.py`

---

## 1. Perfil 1 — Usuário Iniciante / Empreendedor Leigo (`P1_Usuario_Iniciante`)
**Objetivo**: Chegar ao sistema, entender imediatamente o que fazer na primeira dobra, usar linguagem natural sem jargão técnico e tomar decisões em no máximo 3 cliques.
1. Login em `https://automacao.projetosunion.cloud` -> carregamento direto no **Workspace Executivo Único (`Início`)** sem muralha de 5 caixas no topo (`noGuideWall: true`) e sem dashboard duplicado (`noDoubleDashboard: true`).
2. Acima da dobra (`askUnionAboveFold: true`, `prioritiesAboveFold: true`):
   - **Passo 1**: Digitar objetivo simples ou escolher sugestão rápida no **ASK UNION Spotlight Strip** (`#ug-ask-union-input`) -> plano acionável exibido sem sair da tela (`ask_union_ok: true`).
   - **Passo 2**: Clicar no expansor **`Saúde (12 pilares)` / `Ver nota e 12 dimensões`** na faixa `MetricStrip` -> abertura do `BusinessHealthAndScoreDrawer` mostrando nota `64/100`, fórmula auditável e diagnóstico dos 12 pilares (`health_drawer_ok: true`).
   - **Passo 3**: Alternar tema **Obsidian Dark <-> Crisp Alabaster Light** mantendo legibilidade imediata (`light_mode_ok: true`).
- **Métrica Observada em Produção**: `clicks_core_flow: 3`, tempo de execução **`28.93s`**, **`passed: true`**.

---

## 2. Perfil 2 — Usuário Operacional (`P2_Usuario_Operacional`)
**Objetivo**: Triar pendências diárias, consultar guia sob demanda apenas quando precisar e executar campanhas sem poluição visual.
1. Navegar até **`Meu Trabalho`** -> lista de triagem estilo Linear (`divide-y`) com abas underline (`Todas`, `Decisões`, `Execuções`, `Alertas`, etc.) e abertura de detalhes em `Drawer` lateral sem perder o contexto da lista (`meu_trabalho_clean: true`).
2. Acionar o gatilho discreto **`Como funciona esta área`** -> abertura do guia contextual em `Drawer` lateral apenas sob demanda (`ondemand_guide_drawer: true`).
3. Acessar **`Marketing` -> `Campanhas`** -> formulários e listagem de personas/campanhas alinhados ao DS 3.0 com badges `whitespace-nowrap` (`marketing_clean: true`).
4. Abrir **`Todos os recursos`** -> diretório pesquisável organizado em listas agrupadas por categoria, substituindo a antiga grade de 27 caixas (`discovery_directory_ok: true`).
- **Métrica Observada em Produção**: tempo de execução **`7.07s`**, **`passed: true`**.

---

## 3. Perfil 3 — Usuário Avançado (`P3_Usuario_Avancado`)
**Objetivo**: Alternar dinamicamente entre simplicidade operacional e controles técnicos completos com persistência real em banco (`tenants.ui_mode`).
1. Estado inicial **`Modo Simples`** (`#ug-ui-mode-toggle`): sub-abas técnicas avançadas ocultas (expostas apenas sob demanda em `+ N Avançado`), rótulos traduzidos por `plainLanguage.ts` (`Quando essa automação deve começar`, `Serviço de IA`, `Conectar ferramenta externa`, `Limite de solicitações`, `Simular antes de ativar`) (`layman_simple_mode: true`).
2. Alternar para **`Modo Avançado`**: liberação imediata de sub-abas técnicas (`Auditoria & Logs`, `Motores de IA`, `Operação 24/7`, `Piloto 7 Dias`, `Copywriter`, `Growth`) e campos técnicos de webhook/cron nativo Python (`advanced_mode_controls: true`).
- **Métrica Observada em Produção**: tempo de execução **`6.43s`**, **`passed: true`**.
