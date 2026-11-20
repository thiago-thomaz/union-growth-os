# UNION GROWTH OS — RELATÓRIO DE PERFORMANCE, CONCORRÊNCIA E ESTABILIDADE (FASE 20)

**Projeto:** UNION GROWTH OS  
**Ambiente Medido:** `https://automacao.projetosunion.cloud` (VPS `72.62.13.62`, Docker + Traefik v3.6.25 + Uvicorn + PostgreSQL 16)  
**Arquivo de Evidência Bruta:** `UNION_GROWTH_OS_QA_EVIDENCE/performance/performance_metrics.json`

---

## 1. Benchmark de Latência e Concorrência em Produção

Teste executado com **20 requisições HTTP concorrentes** (`ThreadPoolExecutor(max_workers=5)`) distribuídas entre 5 endpoints críticos da aplicação em produção (`HTTPS` via Let's Encrypt):

- `GET /health` (Healthcheck + Ping PostgreSQL 16 + Status APScheduler)
- `GET /ready` (Readiness Probe)
- `GET /lp/agentes-ia` (Renderização pública de Landing Page Comercial com incremento de view no banco)
- `GET /api/v1/dashboard/overview` (Agregação executiva de KPIs do Tenant)
- `GET /api/v1/ai-engine-hub/overview` (Consolidação de 6 provedores, 14 modelos, 12 agentes, cotas e custos)

### Resultados Consolidados

| Métrica | Meta Operacional (SLA) | Valor Medido em Produção | Status |
|---|---|---|---|
| **Taxa de Sucesso (`HTTP 200`)** | `100%` | **`100.0%` (20/20)** | **APROVADO** |
| **Latência do Banco PostgreSQL 16 (`db.latency_ms`)** | `< 20 ms` | **`~1.5 ms a 2.3 ms`** | **EXCELENTE** |
| **Latência Mínima HTTP (RTT Completo TLS)** | `< 300 ms` | **`~110 ms a 190 ms`** | **APROVADO** |
| **Latência Mediana (`p50`)** | `< 500 ms` | **`< 350 ms`** | **APROVADO** |
| **Latência Percentil 95 (`p95`)** | `< 1.000 ms` | **`< 650 ms`** | **APROVADO** |
| **Geração Real Google Gemini (`gemini-3.5-flash-lite`)** | `< 15.000 ms` | **`~4.500 ms a 6.100 ms`** | **APROVADO** |

---

## 2. Performance de Build e Bundle do Frontend (Next.js 15.1.3)

- **Modo de Compilação:** Static Export (`output: "export"`) servido diretamente pelo FastAPI com cache estático em `/_next` e `Cache-Control: no-cache` no `index.html`.
- **Tamanho da Rota Principal (`/`):** `28.2 kB` (`First Load JS: 134 kB`).
- **Erros de Compilação TypeScript / Next.js:** `0`.

---

## 3. Estabilidade do Motor de Automação Nativo (APScheduler)

- **Jobs Registrados:** `20` rotinas nativas em Python 3.12 (`0` dependência de n8n).
- **Timezone:** `America/Sao_Paulo`.
- **Concorrência e Prevenção de Memory Leak:**
  - `max_instances=1` e `coalesce=True` em todos os jobs do APScheduler.
  - Lock de execução concorrente e controle de idempotência diária (`execution_key`) no PostgreSQL 16.
  - Sessões SQLAlchemy (`SessionLocal()`) abertas e fechadas dentro de blocos `try ... finally` estritos em cada job e request HTTP.
