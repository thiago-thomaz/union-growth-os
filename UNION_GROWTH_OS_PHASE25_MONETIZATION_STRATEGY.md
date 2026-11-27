# UNION GROWTH OS — FASE 25: ESTRATÉGIA DE MONETIZAÇÃO (ESTRUTURA PLG — COBRANÇA DESATIVADA)

**Status Financeiro em Produção:** `billing_status: "PLG_STRUCTURE_SIMULATION_ONLY_NO_LIVE_BILLING"` (`charge_enabled: false`). **Nenhuma cobrança real foi ativada.**

---

## 1. Problema Identificado na Auditoria Pré-Fase 25
Na auditoria inicial de produção, todos os `5` tenants (`1..6`) operavam no tier `ENTERPRISE` sem limites diferenciados, com `monthly_price_reference_brl: 0.0` e sem plano `FREE` estruturado para aquisição Product-Led Growth (PLG). Em SaaS internacional, oferecer o teto Enterprise gratuito remove qualquer mecanismo natural de upgrade baseado em valor/consumo.

---

## 2. Nova Escada de Monetização Implementada (`plans_and_audit.py` + `GET /api/v1/plans/overview`)

| Plano | Ref. BRL / Mês | Ref. USD / Mês | Empresas | Usuários | Leads CRM | Automações | Ações IA / Mês | Agentes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`FREE` (Ativação PLG)** | **R\$ 0** | **US\$ 0** | `1` | `2` | `100` | `2` | `30` | `4` (`CEO`, `SEO`, `SOCIAL`, `SALES`) |
| **`STARTER`** | R\$ 147 | US\$ 29 | `1` | `3` | `1.000` | `8` | `250` | `7` (+ `CMO`, `CREATIVE`, `COPY`) |
| **`PRO` (ICP Principal)** | R\$ 397 | US\$ 79 | `3` | `10` | `10.000` | `25` | `1.500` | `10` (+ `GROWTH`, `COMPETITIVE`, `CS`) |
| **`BUSINESS`** | R\$ 897 | US\$ 179 | `10` | `30` | `50.000` | `100` | `5.000` | **`12` (inclui `FINANCE` e `DATA_ANALYST`)** |
| **`ENTERPRISE` & Agências** | R\$ 1.990 | US\$ 399 | `999` | `9.999` | `500.000` | `999` | `50.000` | **`12` + Multinegócio/Sub-contas** |

---

## 3. Benchmarking com Concorrentes Globais
- Frente a **Attio (`Free` 3 assentos, Pro `US$ 79/seat`)**, **HubSpot (`Starter US$ 15–20`, Pro `US$ 90+/seat + US$ 1,5k onboarding`)**, **Make (`Free 1k ops`, `US$ 9+/mês`)** e **GoHighLevel (`US$ 97–497/mês`)**, a estrutura proposta posiciona o `PRO` (`US$ 79/mês` para até `10` usuários e `3` empresas) com forte relação valor/assento sem quebrar margem (pois IA usa `BYO-Key` ou motor determinístico Python).
- **Motor de Billing Recomendado quando o Proprietário Autorizar Faturamento Real:**
  - **Mercado Brasil:** Mercado Pago (PIX + Assinatura recorrente nacional) ou Stripe Brasil.
  - **Mercado Internacional:** **Stripe Billing (`2.9% + 30¢ + 0.7%`)** ou **Paddle MoR (`5% + 50¢` com VAT/impostos globais assumidos)** quando houver expansão em USD/EUR.
