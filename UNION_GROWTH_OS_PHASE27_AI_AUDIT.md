# UNION GROWTH OS — AUDITORIA DA CAMADA DE IA & BENCHMARK (FASE 27)

## 1. Resultado Real do Benchmark (`GET /api/v1/ai/benchmark`)

Executado ao vivo em produção (`https://automacao.projetosunion.cloud`, tenant `QA_AUTOMATED_TENANT`, `prod_snapshot.json`):
- **`elapsed_ms`**: `2.47ms` no browser (`0` chamadas pagas disparadas)
- **`cost_policy`**: `FREE_ONLY` (`paid_calls_blocked: true`, **`cost_incurred_brl: 0.0`**)
- **`agents_total`**: `12` (**`4` `HYBRID`** / **`8` `DETERMINISTIC`** / **`0` `SIMULATED`**)

| ID | Agente | Modo Auditado | Política de Custo | Observações Medidas |
|---|---|---|---|---|
| `AGENT_01_CEO` | AI CEO — Chief Executive Officer | `HYBRID` | `FREE_ONLY` | LLM gratuito opcional + fallback determinístico |
| `AGENT_02_CMO` | AI CMO — Chief Marketing Officer | `HYBRID` | `FREE_ONLY` | LLM gratuito opcional + fallback determinístico |
| `AGENT_03_SEO` | AI SEO Director | `DETERMINISTIC` | `FREE_ONLY` | Crawler HTML HTTP ao vivo + regras técnicas |
| `AGENT_04_SOCIAL` | AI Social Media Director | `HYBRID` | `FREE_ONLY` | Calendário, 30 peças e pacote 1-Clique |
| `AGENT_05_CREATIVE` | AI Creative Studio | `DETERMINISTIC` | `FREE_ONLY` | Artes programáticas PNG (`Pillow`) + roteiros |
| `AGENT_06_COPYWRITER` | AI Copywriter | `HYBRID` | `FREE_ONLY` | Frameworks PAS/AIDA + variação A/B |
| `AGENT_07_GROWTH` | AI Growth Hacker | `DETERMINISTIC` | `FREE_ONLY` | Matriz ICE + Centro de Crescimento persistido |
| `AGENT_08_SALES` | AI Sales Director | `DETERMINISTIC` | `FREE_ONLY` | `5` execuções observadas, `100.0%` sucesso, **`24.9ms`** média |
| `AGENT_09_COMPETITIVE` | AI Competitive Intelligence | `DETERMINISTIC` | `FREE_ONLY` | Monitoramento ético público anti-SSRF |
| `AGENT_10_FINANCE` | AI Finance & Performance | `DETERMINISTIC` | `FREE_ONLY` | Cálculo real de margem, CAC e aprovações |
| `AGENT_11_CS` | AI Customer Success | `DETERMINISTIC` | `FREE_ONLY` | NPS/CSAT e detecção de churn/upsell |
| `AGENT_12_DATA_ANALYST` | AI Data Analyst | `DETERMINISTIC` | `FREE_ONLY` | Atribuição First-Touch e Growth Score 12 pilares |

## 2. Limitação Externa Documentada

A chave Gemini cadastrada no provedor retorna **HTTP `402` (cota gratuita esgotada)**, mantendo os 4 agentes `HYBRID` em fallback determinístico seguro até substituição de chave pelo proprietário, sem gerar cobrança ou simulações enganosas.
