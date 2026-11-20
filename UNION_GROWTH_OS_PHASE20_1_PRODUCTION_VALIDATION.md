# FASE 20.1 — VALIDAÇÃO DE PRODUÇÃO, PERFORMANCE E ISOLAMENTO DE DADOS QA

**Domínio Principal:** `https://automacao.projetosunion.cloud`  
**Domínio Alternativo:** `https://uniongrowth.72.62.13.62.sslip.io`  
**Coolify Application UUID:** `swpy83sa5wshb558fadlrzwc`  
**Deployment Auditado:** `2k2zr3wuvg9yslexsn2bhpoj` (`status: finished`, `force_rebuild: true`)  
**Commit Verificado em `/health` e `/ready`:** `bcca50ee8ad0e03770008122d24e4efa2e0f9cea` *(ambos os domínios sincronizados)*

---

## 1. Saúde de Infraestrutura, Banco e Scheduler

Evidência bruta: `UNION_GROWTH_OS_PHASE20_1_EVIDENCE/deployment/phase20_1_prod_health.json`

- **Health (`/health`):** `HTTP 200 OK`, `status: "ok"` nos dois domínios HTTPS.
- **Readiness (`/ready`):** `HTTP 200 OK`, `ready: true`.
- **PostgreSQL 16 (`database`):** `status: "healthy"`, `engine: "postgresql"`, `is_fallback: false`.
- **APScheduler Nativo (`scheduler`):** `running: true`, `engine: "APScheduler Native Python (100% Internalized)"`, `timezone: "America/Sao_Paulo"`, zero dependência de n8n.
  - **Correção de Isolamento Aplicada (`AUDIT-20.1-SCHED-01`):** `QA_AUTOMATED_TENANT` (Tenant 5) foi removido do agendamento de CRONs em segundo plano via `_is_qa_isolated_tenant()`.
- **SEO Técnico Público:** `/robots.txt` (`HTTP 200`), `/sitemap.xml` (`HTTP 200`), `/lp/agentes-ia` (`HTTP 200`).
- **Headers de Segurança:** `strict-transport-security`, `x-content-type-options: nosniff`, `x-frame-options: SAMEORIGIN`, `x-xss-protection: 1; mode=block`, `referrer-policy` presentes (com `no-referrer` + `Cache-Control: no-store, private, max-age=0` preservados no PDF de propostas).

---

## 2. Benchmark Controlado de Performance (Warm Keep-Alive vs Cold TLS)

Evidência bruta: `UNION_GROWTH_OS_PHASE20_1_EVIDENCE/performance/phase20_1_performance_benchmark.json` (`run_id: p201-8b05cfd6`).

**Correção de Transparência em Relação à Fase 20:** O relatório da Fase 20 havia reportado `p50 < 350ms` enquanto o JSON bruto registrava `1639,51ms` porque cada chamada abria um novo handshake TCP+TLS. Nesta auditoria independente, separamos rigorosamente conexões **Warm Keep-Alive** de conexões **Cold TLS**:

| Endpoint Testado em Produção | Média Warm Keep-Alive (3 amostras) | Latência Cold TLS (Handshake Novo) | Status HTTP | Diagnóstico Técnico |
|---|---:|---:|---:|---|
| `GET /health` | **`78,27 ms`** | `1.759,57 ms` | `200` | Excelente em Keep-Alive; cold time dominado por RTT TLS internacional cliente->VPS. |
| `GET /ready` | **`546,07 ms`** | `853,80 ms` | `200` | Dentro do SLA, com pequena variância de rede. |
| `GET /lp/agentes-ia` | **`310,64 ms`** | `1.001,31 ms` | `200` | Rápido; realiza leitura + incremento `views_count` no PostgreSQL 16. |
| `GET /api/v1/ai-engine-hub/overview` | **`270,72 ms`** | — | `200` | Rápido mesmo consolidando 6 provedores, 16 modelos e 12 agentes. |
| `GET /api/v1/dashboard/overview` | **`1.263,95 ms`** | — | `200` | **Ponto de melhoria identificado (P3):** agrega múltiplas queries SQLAlchemy sequenciais na mesma request; funcional sem erros, mas recomendável otimizar consultas em ciclos futuros. |

---

## 3. Auditoria de Isolamento de Dados QA na Base de Produção

Evidência bruta: `UNION_GROWTH_OS_PHASE20_1_EVIDENCE/qa_data/production_tenants_and_isolation_audit.json` & `phase20_1_security_and_defects.json`.

- **Tenant Principal (`Tenant 1 — Union Growth Holding Ltda`):**
  - `real_confirmed_revenue_brl`: **`R$ 0,00`** (nenhuma transação `SANDBOX` de QA contaminou a receita real).
  - `metrics_cards["revenue"]`: `R$ 48.500,00` explicitamente rotulado como **`DADO IMPORTADO`** (`origin: IMPORTED`).
  - `metrics_cards["leads"]`: Após a correção `AUDIT-20.1-QA-01`, passou a exibir **`2` (`DADO REAL`)**, excluindo automaticamente os 3 registros históricos com `data_origin="TEST"` (`validacao.fase15@empresa.com.br`).
  - Nenhuma proposta comercial de QA foi criada no Tenant 1 (`found_pdf_button: false` no Tenant 1, `3` propostas exclusivamente no `QA_AUTOMATED_TENANT`).
- **Tenant Isolado (`Tenant 5 — QA_AUTOMATED_TENANT`):**
  - Concentra 100% dos registros de teste E2E da Fase 20 e Fase 20.1 (`data_origin="TEST"` / `sandbox_mode=True`).
  - `metrics_cards["leads"]`: **`0`** leads reais (todos corretamente isolados como `TEST`).
  - Excluído do agendamento de jobs CRON em background do APScheduler.
- **Outros Serviços da VPS (`72.62.13.62`):** Nenhum outro container, banco ou volume na VPS foi interrompido ou alterado.
