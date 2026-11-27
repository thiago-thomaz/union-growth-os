# UNION GROWTH OS — ESCALABILIDADE & PRONTIDÃO DE CRESCIMENTO (FASE 27)

## 1. Análise Técnica Honesta (`Score Categoria 25: 76.0 / 100 — REAL_PARTIAL`)

| Dimensão | Implementado Hoje (`v2.4.0`) | Capacidade Estimada | Requisito para Escala Massiva (`10k–1M+` usuários) |
|---|---|---|---|
| **Banco de Dados** | PostgreSQL 16 dedicado (`pool_size=10`, `max_overflow=20`), isolamento por `tenant_id` | Centenas de PMEs com baixa/média concorrência | Read-replicas, PgBouncer, particionamento por `tenant_id` |
| **API & Compute** | Container único FastAPI + Uvicorn (`--timeout-keep-alive 75`) | Dezenas de requisições/seg sustentadas | Múltiplas réplicas stateless atrás de Load Balancer |
| **Filas & Agendamentos** | `APScheduler` Python in-process (`127` jobs, lock em memória + idempotência no DB) | Ideal em container único; 0% n8n | Migrar execução assíncrona pesada para Redis + Celery/ARQ workers dedicados |
| **Frontend Static Export** | Next.js 15 static export (`83.7 kB` /) | Pode ser distribuído em CDN global com custo mínimo | Servido pelo FastAPI hoje; migrável para Cloudflare/CDN sem alteração |
| **Storage de Mídia/Backups** | Volume persistente local em disco (`data/backups/`, `artifacts/`) | Adequado para operação inicial | Offload para S3/R2/Backblaze B2 com CDN |
