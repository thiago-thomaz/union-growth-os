# FASE 20.1 — AUDITORIA INDEPENDENTE DO UNION AI ENGINE HUB (GEMINI & FREE_ONLY)

**Evidência Bruta:** `UNION_GROWTH_OS_PHASE20_1_EVIDENCE/ai_engine/phase20_1_ai_engine_strict_validation.json`  
**Status Consolidado do Módulo:**
- **Política `FREE_ONLY` & Bloqueio contra Cobranças:** **`PASS (REAL)` — 100% Comprovado (`5/5` vetores bloqueados estritamente)**
- **Conexão / Descoberta de Modelos Google Gemini:** **`PASS (REAL)` — `CONNECTED` (`322,32 ms`, `35` modelos descobertos)**
- **Geração de Conteúdo ao Vivo no Google Gemini (`generateContent`):** **`BLOCKED (QUOTA_OR_BILLING_REQUIRED)` — Chave atual `AQ....rlw` sem cota gratuita disponível (`HTTP 402`)**
- **Demais Provedores (OpenAI, Anthropic, Groq, OpenRouter, OpenAI-Compatible):** **`PENDING_API_KEY` / `BLOCKED_FREE_ONLY`**

---

## 1. Bugs Encontrados e Corrigidos no `AIRouter` durante a Fase 20.1

1. **Divergência de Campos na Rota `POST /api/v1/ai-engine-hub/route-execute`:**
   - Antes da Fase 20.1, a rota lia apenas `provider_key` e `model_id`, ignorando `preferred_provider` e `preferred_model`. Agora aceita ambos os pares de parâmetros de forma retrocompatível.
2. **Mascaramento de `BLOCKED_FREE_ONLY` por Fallback Silencioso:**
   - Antes da Fase 20.1, quando um cliente solicitava explicitamente `openai:gpt-4o` sob a política `FREE_ONLY`, o roteador recusava o modelo pago mas continuava o laço tentando fallback para o Gemini (mascarando o resultado final como `PROVIDER_ERROR`).
   - **Correção:** Agora, se o chamador solicita explicitamente um provedor/modelo proibido pela política `FREE_ONLY`, o `AIRouter` executa `break` imediato e retorna `ok: false`, `status: "BLOCKED_FREE_ONLY"`, `estimated_cost_brl: 0.0`.
3. **Classificação Explícita de `HTTP 402 Payment Required`:**
   - Quando a API do Google retorna `HTTP 402`, o sistema agora classifica o evento como **`QUOTA_OR_BILLING_REQUIRED`** (e não mais `PROVIDER_ERROR` genérico), informando claramente que **nenhuma cobrança foi realizada** e instruindo o uso de uma chave padrão Free Tier (`AIzaSy...`).

---

## 2. Matriz de Comprovação da Política `FREE_ONLY` em Produção (`p201-8b05cfd6`)

| Vetor Testado em Produção | Classificação do Modelo | Resultado Esperado | Resultado Real Obtido | Custo Gerado | Status |
|---|---|---|---|---|---|
| `openai` / `gpt-4o` | `PAID` | `BLOCKED_FREE_ONLY` | `ok: false`, `status: BLOCKED_FREE_ONLY` | `R$ 0,00` | **PASS (REAL)** |
| `anthropic` / `claude-3-7-sonnet-latest` | `PAID` | `BLOCKED_FREE_ONLY` | `ok: false`, `status: BLOCKED_FREE_ONLY` | `R$ 0,00` | **PASS (REAL)** |
| `openai_compatible` / `custom-openai-model` | `UNKNOWN_COST` | `BLOCKED_FREE_ONLY` | `ok: false`, `status: BLOCKED_FREE_ONLY` | `R$ 0,00` | **PASS (REAL)** |
| `gemini` / `imagen-3.0-generate-002` (Image Studio) | `PAID` | `BLOCKED_FREE_ONLY` | `ok: false`, `status: BLOCKED_FREE_ONLY` | `R$ 0,00` | **PASS (REAL)** |
| `gemini` / `veo-2.0-generate-001` (Video Studio) | `PAID` | `BLOCKED_FREE_ONLY` | `ok: false`, `status: BLOCKED_FREE_ONLY` | `R$ 0,00` | **PASS (REAL)** |

**Conclusão de Segurança Financeira:** Confirmado em produção que **nenhum modelo pago ou de custo desconhecido consegue ser invocado** enquanto `FREE_ONLY` estiver ativo.

---

## 3. Estado Real e Honesto do Google Gemini em Produção

- **Chave Configurada (Mascarada):** `AQ....rlw` (chave de modo Express do Google).
- **Teste Controlado de Conexão (`test-connection`):** `ok: true`, `status: CONNECTED`, `latency_ms: 322.32`, `35` modelos listados.
- **Teste Controlado de Geração (1 única chamada `route-execute`):** `ok: false`, `status: QUOTA_OR_BILLING_REQUIRED`, `estimated_cost_brl: 0.0`, erro: *"Cota gratuita esgotada ou faturamento exigido pela Google (HTTP 402 Payment Required). Nenhuma cobrança foi realizada. Utilize uma chave padrão Free Tier ('AIzaSy...') gerada em https://aistudio.google.com/apikey."*
- **Veredito Honesto:** Embora haja registro histórico de uma geração anterior bem-sucedida (`ai-exec-1bdb53ca18dc42`), **nesta auditoria independente a geração ao vivo do Gemini está `BLOCKED` por cota da chave atual e NÃO pode ser declarada `PASS (REAL)`** até que o proprietário substitua a chave `AQ...` por uma chave gratuita padrão `AIzaSy...` (Free Tier) no Menu `25 -> 2. Provedores`.
