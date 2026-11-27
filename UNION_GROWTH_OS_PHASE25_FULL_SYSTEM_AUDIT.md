# UNION GROWTH OS — FASE 25: AUDITORIA COMPLETA E INDEPENDENTE DO SISTEMA

**Data da Auditoria:** 2026-11-27  
**Commit Auditado em Produção:** [`b6162c2859b16514b8666736f23c0e9d9c8ac34a`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os)  
**Produção Primária:** https://automacao.projetosunion.cloud | **Secundária:** https://uniongrowth.72.62.13.62.sslip.io  

---

## 1. Postura da Auditoria (Regra Zero Complacência)
Esta auditoria não presume sucesso de fases anteriores. Cada camada foi inspecionada diretamente no código-fonte, no banco PostgreSQL de produção (via API autenticada somente leitura e tenant isolado `QA_AUTOMATED_TENANT`), no pipeline GitHub Actions e em navegador Chrome real com telemetria CDP.

---

## 2. Mapa Arquitetural Atual Observado
- **Backend FastAPI (`backend/app/`)**: **21 módulos Python totalizando 22.049 linhas**, além de **`2.807` linhas de testes** em [test_union_growth_os.py](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/backend/tests/test_union_growth_os.py).
  - Núcleo concentrado ainda pesado em [routes.py](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/backend/app/api/routes.py) (`4.127` linhas), [phase17_commercial_engine.py](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/backend/app/services/phase17_commercial_engine.py) (`3.200` linhas) e [ai_engines_hub.py](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/backend/app/services/ai_engines_hub.py) (`2.621` linhas).
- **Frontend Next.js 15 (`frontend/src/`)**: Export estático (`Route /` `74.1 kB`, `First Load JS` `180 kB`) servido pelo FastAPI em produção.
  - [UnionGrowthOSPortal.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/UnionGrowthOSPortal.tsx) foi reduzido de **`5.535` para `4.028` linhas** nesta Fase 25 com extração de [CommercialRevenueWorkspace.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/CommercialRevenueWorkspace.tsx) (`1.388` linhas) e [AIEnginesHubWorkspace.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/AIEnginesHubWorkspace.tsx) (`694` linhas), mas ainda precisa de modularização adicional futura para telas legadas de Marketing/Configurações.
- **Banco & Agendamento**: PostgreSQL 16 (`is_fallback: false`), **127 rotinas APScheduler nativas em Python** (zero dependência de `n8n`), **5 tenants ativos** em produção (`1 Union Growth Holding Ltda`, `2` & `3 TecnoAgro`, `5 QA_AUTOMATED_TENANT`, `6 Meu Autonomo`).

---

## 3. Classificação Crítica do Que Existe Hoje

| Domínio | Estado Auditado | Evidência Concreta e Crítica Honesta |
| :--- | :--- | :--- |
| **Autenticação, JWT, RBAC & Multi-Tenant** | **REAL E FUNCIONAL** | `bcrypt (rounds=10)`, JWT `HS256`, isolamento por `tenant_id` e `X-Tenant-Id` validado contra `403`, bloqueio de brute-force (`8 falhas / 5 min`), rate limit `600/min`, SSRF bloqueado. |
| **CRM, Leads LGPD & Revenue Intelligence** | **REAL E FUNCIONAL** | Leads com opt-in LGPD, score `0–100`, detecção de leads quentes sem retorno e negócios estagnados em `/api/v1/growth-os/revenue-intelligence` + follow-up em 1 clique. |
| **Propostas PDF, Pipeline & Multinegócio** | **REAL E FUNCIONAL** | PDF seguro via `Blob URL`, aprovação obrigatória de proprietário, funil fechado para `CRMDeal`. Ponto fraco pré-Fase 25 corrigido: funil visual de 17 etapas poluía com zeros; agora colapsável e limpo em DS 3.0. |
| **Agentes de IA (12) & AI Engine Hub** | **REAL MAS PARCIAL** | `/api/v1/agents/audit` confirma `"4 de 12 agentes usam LLM real agora"` (adaptador público gratuito Pollinations quando sem chave BYO); `8` operam em lógica determinística/templates Python. Chave Gemini do tenant 1 exibe `QUOTA_OR_BILLING_REQUIRED` (HTTP 402 bloqueado em `FREE_ONLY`, zero cobrança); demais provedores aguardam chave BYO. `AIUsageTracker` legado ainda mantém cache em memória (enquanto `AIEngineExecutionRecord` persiste no PostgreSQL). |
| **SEO & Inteligência Técnica** | **REAL MAS INCOMPLETA** | Executa GET HTTP público anti-SSRF, mede tempo, `robots.txt`, `sitemap.xml` e agora extrai `canonical_url`, `has_viewport`, tags OpenGraph e contagem de palavras. **Lacuna declarada**: sem Google Search Console OAuth conectado, não há dados reais de cliques/impressões da SERP. |
| **Redes Sociais & Integrações (18)** | **PENDING CREDENTIALS (17/18)** | Apenas **`1` de `18`** conectada (`google_pagespeed_insights`). **`0/6` redes sociais** conectadas via OAuth oficial; publicação opera honestamente via **Pacote 1-Clique (Modo Assistido)** até o cliente inserir chaves próprias. |
| **Financeiro & Pagamentos** | **REAL + SANDBOX SEPARADO** | Separa `IMPORTED`/`REAL` de registros `TEST` (`mp_sbx_*`). **Zero transações live pagas** recebidas até o momento; gateway de cobrança fica bloqueado sem credenciais live e autorização. |
| **Planos SaaS & Monetização (PLG)** | **REAL ESTRUTURALMENTE (SEM COBRANÇA)** | Pré-Fase 25 todos os 5 tenants eram `ENTERPRISE` a `R$ 0,00`. Agora catálogo `FREE` -> `ENTERPRISE` com medidores reais (`/api/v1/plans/overview`) existe e roda no portal em `PLG_STRUCTURE_SIMULATION_ONLY_NO_LIVE_BILLING`. Falta checkout automatizado (`Stripe`/`Mercado Pago` live) apenas quando houver decisão comercial. |
| **CI/CD & Auto Deploy** | **FUNCIONAL COM GAP DE SECRETS** | Testes `pytest` (52), `tsc`, `next build` e scan de segredos rodam no GitHub Actions. Porém **Auto Deploy automático no Coolify ainda requer ação do proprietário**: `is_auto_deploy_enabled: false` no Coolify (`source_id: 0`) e ausência de `COOLIFY_API_TOKEN`/`COOLIFY_DEPLOY_WEBHOOK` nos Secrets do GitHub. |

---

## 4. Redundâncias, Peso Morto & Débitos Técnicos Remanescentes
1. **Arquivos monolíticos remanescentes**: `UnionGrowthOSPortal.tsx` (`4.028` linhas), `routes.py` (`4.127` linhas), `phase17_commercial_engine.py` (`3.200` linhas) dificultam manutenção em escala global; devem ser fatiados gradualmente em Fase 26.
2. **Proliferação de relatórios no repositório**: dezenas de `.md` de fases anteriores acumulados na raiz; em ciclo futuro convém consolidar em `/docs/phases/`.
3. **Dependência de credenciais do usuário para valor pleno externo**: sem OAuth social/GSC e chaves Gemini Free Tier / Groq ativas, o produto entrega valor nativo sólido (CRM, SEO técnico HTTP, Automações Python, Propostas PDF, Marca, Content Factory determinístico), mas ainda depende de configuração externa para publicação direta e LLM de ponta em 100% dos fluxos.
4. **Concorrência na hidratação frontend**: corrigida na Fase 25 dividindo `loadAllActiveData()` em **Wave 1** (5 chamadas vitais de Shell/Home) e **Wave 2** (27 secundárias com trava `loadSeqRef`), eliminando bloqueio de ~6s no seletor de empresa e corrida ao trocar tenant. O passo seguinte futuro é consolidar endpoints de leitura inicial em um único BFF `/api/v1/bootstrap`.
