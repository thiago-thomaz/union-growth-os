# UNION GROWTH OS — FASE 26: AI ENGINE & TRANSPARENCY REPORT

**Versão:** `2.3.0 — FASE 26`  

## 1. Arquitetura do Motor de IA & Governança de Custos
- **Orquestrador Central (`backend/app/agents/orchestrator.py`)**: coordena `12` especialistas (`AGENT_01_CEO` .. `AGENT_12_DATA_ANALYST`) via `AgentTaskContract` tipado com prevenção de ciclos via `workflow_run_id` e histórico imutável em PostgreSQL (`AgentExecutionLog`, `AIEngineExecutionRecord`).
- **Política de Custo (`FREE_ONLY` padrão)**: bloqueia qualquer modelo pago automaticamente caso não haja `OWNER_APPROVED`.
- **`AIUsageTracker` Persistido (`orchestrator.py` + PostgreSQL)**: na Fase 26, `AIUsageTracker.get_usage_summary(tenant_id, db=db)` deixou de depender apenas de contadores em memória volátil e passou a somar execuções reais do dia no PostgreSQL (`AgentExecutionLog` + `AIEngineExecutionRecord`).

## 2. Matriz de Classificação sem Disfarces (`GET /api/v1/agents/matrix`)
Ao vivo na nuvem (`https://automacao.projetosunion.cloud`) com provedor gratuito Pollinations disponível em fallback:
- **`HYBRID` (4 de 12 agentes):** `AGENT_02_CMO`, `AGENT_04_SOCIAL`, `AGENT_06_COPYWRITER`, `AGENT_09_COMPETITIVE` — combinam regras estruturadas Python com geração textual LLM opcional via `AIRouter` + fallback determinístico resiliente.
- **`DETERMINISTIC` (8 de 12 agentes):** `AGENT_01_CEO`, `AGENT_03_SEO`, `AGENT_05_CREATIVE` (Pillow PNG local), `AGENT_07_GROWTH`, `AGENT_08_SALES`, `AGENT_10_FINANCE`, `AGENT_11_CS`, `AGENT_12_DATA_ANALYST`.
- **`SIMULATED`: `0 de 12`** — nenhuma resposta heurística ou template é rotulada como IA generativa.

## 3. Bloqueios & Limitações Atuais
- Chave Gemini cadastrada anteriormente pelo usuário no Tenant 1 encontra-se com retorno externo `HTTP 402` (`QUOTA_OR_BILLING_REQUIRED`), corretamente barrada em `FREE_ONLY`. Basta substituir por uma chave gratuita ativa do Google AI Studio (`https://aistudio.google.com/apikey`) para uso direto no Gemini Free Tier.
