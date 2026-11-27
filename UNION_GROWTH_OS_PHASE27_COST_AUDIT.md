# UNION GROWTH OS — AUDITORIA DE CUSTOS & GOVERNANÇA FINANCEIRA (FASE 27)

## 1. Política Estrita R$ 0,00 Extra

| Área de Custo | Política Ativa em `v2.4.0` | Valor Gasto na Fase 27 | Trava de Segurança Implementada |
|---|---|---|---|
| **Infraestrutura VPS / Coolify** | Servidor e PostgreSQL 16 existentes | **`R$ 0,00` adicional** | Zero novas instâncias, workers externos ou serviços pagos |
| **Modelos de IA (LLM / Mídia)** | `cost_policy_mode = "FREE_ONLY"` | **`R$ 0,00`** | `allow_paid_fallback = false`; `paid_calls_blocked = true` |
| **Geração de Mídia & Imagens** | `Pillow` local programático + roteiro texto | **`R$ 0,00`** | Nenhuma API paga de imagem/vídeo chamada |
| **SEO / Concorrentes /Crawler** | HTTP público nativo + PageSpeed gratuito | **`R$ 0,00`** | Sem SaaS SEO pago ou scraping em lote pago |
| **Automações & Agendamento** | `APScheduler` Python interno (`127` jobs) | **`R$ 0,00`** | **`0%` n8n** (proibição arquitetural obedecida) |
| **Cobrança SaaS / Gateways** | `charge_enabled = false` (`SANDBOX`) | **`R$ 0,00`** | Webhooks prontos apenas com autorização explícita do dono |
