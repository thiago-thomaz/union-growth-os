# UNION GROWTH OS — FASE 25: AUDITORIA PROFUNDA DE UX

**Escopo Auditado:** Fluxos completos em Desktop (`1920x1080`, `1440x900`, `1366x768`, `1024x768`), Tablet (`768x1024`) e Mobile (`390x844`, `360x800`) via Chrome DevTools Protocol (CDP) em produção.

---

## 1. Problemas Reais Encontrados Antes das Correções da Fase 25
1. **Discrepância Drástica Entre Home Moderna e Subtelas Legadas**: após a Fase 24 reconstruir `Início`, `Meu Trabalho`, `Brand` e `Todos os Recursos`, entrar em **`Comercial -> Leads & CRM`**, **`Pipeline & Vendas`**, **`Propostas, Contratos & 3 Unidades`** ou **`Modelos & Provedores`** devolvia o usuário a caixas legadas azuis (`#0f1629`), títulos verbosos (`1.`, `2.`, `9.`) e funil de **17 caixas vazias/zeradas** sempre abertas em `Propostas & 3 Unidades`.
2. **Sinalização Enganosa no Controle Rápido de IA**: o painel de `Visão & Agentes` imprimia `"Serviço ativo: GEMINI"` mesmo quando o tenant (`QA_AUTOMATED_TENANT`, por exemplo) não possuía nenhuma chave cadastrada (`has_credential: false`), confundindo usuários iniciantes.
3. **Lentidão Percebida no Login e Troca de Workspace**: `loadAllActiveData()` disparava 32 `fetch()` paralelos e **bloqueava `setMeData(me)` até a última das 32 respostas**, mantendo o portal inteiro e o seletor `#ug-tenant-select` invisíveis por ~5,5–6s durante o carregamento inicial.
4. **Falta de Ação Imediata de Receita no CRM**: leads quentes sem resposta e negociações estagnadas não possuíam resumo acionável nem botão de follow-up rápido no topo do CRM.

---

## 2. Evoluções de UX Implementadas e Validados na Fase 25
1. **Hidratação em 2 Ondas (`Wave 1` < 1s + `Wave 2` com `loadSeqRef`)**: `#ug-tenant-select`, saudação, checklist TTFV, `ASK UNION`, `Prioridades de hoje` e `AI CEO Briefing` carregam imediatamente com as 5 chamadas críticas; os 27 módulos secundários hidratam logo atrás sem travar a UI e sem corrida se o usuário trocar de empresa no meio.
2. **Onboarding Orientado a TTFV Real (`HomeWorkspace.tsx` + `/api/v1/growth-os/activation-retention`)**: indicador compacto de 6 marcos concretos conectados ao banco + gatilhos reais de retorno diário (`aprovações pendentes`, `leads quentes`, `deals parados`, `conteúdos prontos`).
3. **CRM Revenue Intelligence (`CommercialRevenueWorkspace.tsx`)**: faixa superior mostra `Leads Quentes em Entrada`, `Negociações Paradas` e `Taxa de Conversão`, com bloco acionável `Atenção Comercial Prioritária` permitindo avançar/criar follow-up em 1 clique.
4. **Limpeza de Ruído em Multinegócio**: resumo de 17 etapas do funil recolhido por padrão sob botão explícito `Ver funil (17 etapas)` + abas horizontais underline `FilterTabBar` focadas em `Propostas PDF & Fechamento` primeiro.
5. **Honestidade Radical de Status de IA**: mostra `AGUARDANDO CHAVE GRATUITA (BYO-KEY)` e `NATIVO (GEMINI sem chave)` quando não há chave; mostra `GEMINI CONECTADO (CHAVE ATIVA)` e histórico real (incluindo HTTP 402 quando chave sem cota free) apenas quando existe credencial ativa.
