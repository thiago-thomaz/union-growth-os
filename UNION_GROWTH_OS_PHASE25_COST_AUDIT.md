# UNION GROWTH OS — FASE 25: AUDITORIA DE CUSTOS & GOVERNANÇA `FREE_ONLY`

**Custo Adicional Incorrido na Fase 25:** **R\$ 0,00**.

---

## 1. Política de Custos Verificada em Produção (`GET /api/v1/ai-engines/config`)
- **Modo Padrão:** `cost_policy_mode: "FREE_ONLY"`
- **Fallback Pago:** `allow_paid_fallback: false` (`monthly_budget_brl: 0.0`)
- **Proteção Comprovada Ao Vivo:** na captura de produção [09_ia_motores_provedores.png](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/UNION_GROWTH_OS_PHASE25_EVIDENCE/../UNION_GROWTH_OS_PHASE22_SCREENSHOTS/09_ia_motores_provedores.png), chamadas ao Gemini sem cota gratuita disponível registram `QUOTA_OR_BILLING_REQUIRED (HTTP 402 Payment Required) — Nenhuma cobrança foi realizada` sem escalar para consumo pago.
- **Limites Globais do Hub:** `daily_requests: 1.500`, `monthly_requests: 30.000`, `daily_tokens: 500.000` (Text `1.200`, Image `50`, Video `20`), além da cota de uso por plano PLG medida em `/api/v1/plans/overview`.

---

## 2. Custos Operacionais de Infraestrutura & Recursos
- **VPS / Coolify / PostgreSQL 16 / Traefik / GitHub Actions:** infraestrutura já existente utilizada sem contratação de novos servidores, bancos gerenciados pagos ou serviços externos pagos (`APScheduler` nativo em Python substitui custos recorrentes de Zapier/Make/n8n cloud).
- **Auditorias SEO & Webhooks:** coleta HTTP pública gratuita + Google Autocomplete sem consumo de APIs pagas (ex.: Semrush/Ahrefs).
- **Ponto de Atenção Técnico:** o `AIUsageTracker` legado ainda agrega contadores diários em memória; manter o monitoramento via `AIEngineExecutionRecord` (persistido em PostgreSQL) e migrar o tracker legado para o banco em Fase 26.
