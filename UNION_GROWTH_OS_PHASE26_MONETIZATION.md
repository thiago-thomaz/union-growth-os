# UNION GROWTH OS — FASE 26: MONETIZATION & BILLING READINESS

**Versão:** `2.3.0 — FASE 26`  

## 1. Estrutura Comercial PLG (Sem Cobrança Automática Ativa)
| Tier | Referência Mensal | Limite Empresas | Agentes Incluídos | Limites Chave |
| :--- | :--- | :---: | :---: | :--- |
| **`FREE` (Ativação PLG)** | **R$ 0 / mês** | 1 | 4 (`CEO`, `SEO`, `SOCIAL`, `SALES`) | 100 leads CRM, 2 automações, 30 ações IA/mês |
| **`STARTER`** | Ref.: R$ 147 / US$ 29 | 1 | 7 | 1.000 leads, 8 automações, 250 ações IA |
| **`PRO` (ICP Principal)** | Ref.: R$ 397 / US$ 79 | 3 | 10 (`+ GROWTH`, `COMPETITIVE`, `CS`) | 10.000 leads, 25 automações, 1.500 ações IA |
| **`BUSINESS`** | Ref.: R$ 897 / US$ 179 | 10 | 12 (Todos + `DATA_ANALYST`) | 50.000 leads, 100 automações, 5.000 ações IA |
| **`ENTERPRISE`** | Ref.: R$ 1.990 / US$ 399 | 999 | 12 + Multinegócio | Multi-unidade, 500k leads, RBAC & auditoria completos |

## 2. Entitlements & Prontidão de Billing (`GET /api/v1/plans/entitlements`)
- **`charge_enabled: false` / `authorization_required: true`**: trava explícita na UI (`Cobrança desativada — autorização explícita exigida`) e na camada de serviço.
- **Prontidão Técnica para Ativação Futura:**
  - **Brasil (`Mercado Pago`)**: suporte preparado para PIX & Cartão Recorrente + validação webhook HMAC já implementada em backend (aguarda `live_credentials` após autorização explícita do proprietário).
  - **Global (`Stripe Billing / Paddle MoR`)**: estrutura de tiers em USD e entitlements pronta para integração internacional futura sem cobrança live hoje.
- Nenhuma projeção ou garantia de faturamento é exibida no sistema; apenas receita lançada como `REAL`/`IMPORTED` conta nos KPIs.
