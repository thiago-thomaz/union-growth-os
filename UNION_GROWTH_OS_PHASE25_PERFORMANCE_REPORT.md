# UNION GROWTH OS — FASE 25: RELATÓRIO DE PERFORMANCE & ARQUITETURA HTTP

## 1. Métricas de Build e Tamanho de Bundle
- **Toolchain:** Next.js `15.1.3` (`output: "export"` estático servido pelo FastAPI em produção).
- **Bundle Medido pós-Fase 25 (`npm run build`):**
  - Rota `/` principal: **`74.1 kB`**
  - **First Load JS total:** **`180 kB`** (`105 kB` chunks compartilhados `4bd1b696` `52.9 kB` + `517` `50.5 kB` + `1.94 kB`).
  - `/_not-found`: `979 B` (`106 kB` First Load).
  - Nota comparativa honesta: comparado aos `71.3 kB` / `177 kB` da Fase 24, houve acréscimo de `+2.8 kB` porque o código extraído de CRM Revenue Intelligence, Kanban, Multinegócio DS 3.0 e Planos PLG acrescentou componentes semânticos e props em vez de blocos inline simples, mantendo First Load JS dentro do orçamento enxuto (`<= 180 kB`).

---

## 2. Gargalos Críticos Identificados & Resolvidos na Fase 25
1. **Race de `502 Bad Gateway` entre Uvicorn e Traefik (Infraestrutura):**
   - **Causa raiz observada em produção:** `Dockerfile` iniciava Uvicorn sem `--timeout-keep-alive`, usando o padrão curto de **5 segundos** enquanto o Traefik mantinha sockets keep-alive em reuso, provocando `502 Bad Gateway` esporádico sob rajada de requisições (`auth/me`).
   - **Correção aplicada ([Dockerfile](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing%20Digital%20automático/union-growth-os/Dockerfile)):** `--timeout-keep-alive 75 --proxy-headers`.
   - **Resultado comprovado em 4 suítes CDP seguidas:** `network_4xx_5xx_count: 0` em todas elas após o deploy.
2. **Bloqueio de ~6s na Renderização Inicial do Portal (`UnionGrowthOSPortal.tsx`):**
   - **Causa raiz observada:** `loadAllActiveData()` usava um único `Promise.all` de **32 endpoints simultâneos** antes de chamar `setMeData(me)`, retardando a aparição do seletor de empresa `#ug-tenant-select` e do workspace `Início`.
   - **Correção aplicada:** hidratação dividida em **Wave 1** (5 chamadas vitais: `/auth/me`, `/dashboard/overview`, `/ceo/daily-plan`, `/growth-os/command-center`, `/growth-os/activation-retention`) liberando a UI em **< 1s**, seguida pela **Wave 2** (27 secundárias) protegida contra race-condition via `loadSeqRef`.

---

## 3. Otimizações Recomendadas para Escala Global (Fase 26+)
1. **Endpoint BFF Agregador (`GET /api/v1/bootstrap`)**: condensar os ~27 endpoints secundários em 1 ou 2 payloads cacheados por `tenant_id` (`ETag` / TTL curto), reduzindo tráfego de 32 conexões HTTP/1.1 paralelas para `<= 3`.
2. **Dynamic Import por Área no Frontend**: carregar `AIEnginesHubWorkspace` e `CommercialRevenueWorkspace` sob demanda via `next/dynamic` reduzirá a rota `/` para menos de `50 kB`.
3. **Fila Assíncrona Externa (`Redis + Worker`)**: desacoplar execuções LLM demoradas e rotinas periódicas do processo web principal para escalar réplicas stateless horizontalmente.
