# UNION GROWTH OS — MONETIZAÇÃO PLG, ENTITLEMENTS & BILLING READINESS (FASE 27)

## 1. Catálogo PLG & Preços Referenciais (`plans_and_audit.py`)

| Tier | Limite Empresas | Leads CRM | Automações | Ações IA / Mês | Agentes | Referência Preço (`SANDBOX`) |
|---|---|---|---|---|---|---|
| `FREE` | `1` | `100` | `2` | `30` | `4` | `R$ 0 / mês` |
| `STARTER` | `1` | `1.000` | `8` | `250` | `7` | `Ref.: R$ 147/mês ($29)` |
| `PRO` | `3` | `10.000` | `25` | `1.500` | `10` | `Ref.: R$ 397/mês ($79)` |
| `BUSINESS` | `10` | `50.000` | `100` | `5.000` | `12` | `Ref.: R$ 897/mês ($179)` |
| `ENTERPRISE` | `999` | `500.000` | `999` | `50.000` | `12` | `Ref.: R$ 1.990/mês ($399)` |

## 2. Enforcement Real Implementado na Fase 27

- `enforce_tenant_entitlement(db, tenant, resource_key, owner_email)` agora bloqueia efetivamente no **backend** (HTTP **`402 Payment Required`**) quando o limite do plano ativo é atingido:
  - `POST /api/v1/tenants` (criação de empresa além do limite `max_companies` do plano ativo).
  - `POST /api/v1/crm/leads` (criação de lead além de `max_crm_leads`).
  - Testado e comprovado no `pytest test_53` (troca via `POST /api/v1/plans/change-tier` para `FREE` -> `POST /tenants` bloqueado com `402` -> volta para `ENTERPRISE` -> `201`).
- **Política de Cobrança Zero:** `billing_readiness.charge_enabled = false` e `authorization_required = true` mantidos em todos os endpoints; webhooks HMAC de pagamento (`Mercado Pago` / `Stripe`) estruturados em modo `SANDBOX`, aguardando credenciais e autorização do proprietário (**Score Categoria 16: `78.0 / 100 — SANDBOX`**).
