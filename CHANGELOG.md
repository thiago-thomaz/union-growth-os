# Changelog — UNION GROWTH OS

## [1.0.0] — 2026-11-10

### Adicionado
- **FASE 1 (Auditoria)**: Mapeamento completo do ambiente local e infraestrutura Cloud Coolify/Traefik.
- **FASE 2 & 3 (Arquitetura & Fundação)**: Backend FastAPI + SQLAlchemy (PostgreSQL + fallback SQLite), autenticação JWT + bcrypt, RBAC, isolamento Multi-Tenant e planos SaaS (`STARTER`, `PRO`, `BUSINESS`, `ENTERPRISE`).
- **FASE 4 (11 Agentes & Orquestrador)**: Implementação dos 11 agentes (`AI CEO`, `AI CMO`, `AI SEO Director`, `AI Social Media Director`, `AI Creative Studio`, `AI Copywriter`, `AI Growth Hacker`, `AI Sales Director`, `AI Competitive Intelligence`, `AI Finance & Performance`, `AI Customer Success`) e `CentralOrchestrator` com contratos tipados e prevenção de ciclos.
- **FASE 5 (Conteúdo & Criativos)**: Geração real de imagens PNG com `Pillow`, carrosséis, roteiros de vídeo, e-books, copies A/B e `SEO Content Factory`.
- **FASE 6 (Comercial & CRM)**: CRM completo com Leads, Empresas, Negociações, Atividades, Lead Scoring automático (0–100), validação LGPD e previsão comercial ponderada.
- **FASE 7 (Automações Nativas)**: `APScheduler` 100% em Python com as 12 regras de automação predefinidas, controle de concorrência, idempotência e retry com backoff exponencial.
- **FASE 8 (Integrações Oficiais)**: Catálogo de 16 integrações com guia de ativação, criptografia Fernet e testadores reais de conexão (SMTP, Meta Graph API, Mercado Pago, etc.).
- **FASE 9 (Segurança & Governança)**: Rate limiting, headers de segurança, sanitização anti-XSS, trava de alto impacto e backup completo JSON/SQLite.
- **FASE 10, 11 & 12 (Produção Cloud, Validação & Otimização)**: Painel Executivo Next.js 15 TypeScript Tailwind CSS com 20 seções, suíte `pytest` aprovada e deploy automatizado em nuvem com HTTPS no Coolify.
- **FASE 13 (Auditoria Real, Autonomia & Ativação Comercial)**:
  - Invalidação da senha inicial fraca padrão e rotação forçada (`must_change_password`).
  - Proteção contra força bruta em logins (8 falhas / 5 min) e CORS restrito a origens permitidas.
  - Sistema de IA Híbrido Real com motor Python determinístico, rastreamento honesto de origem (`response_origin`) e controle diário de tokens (`AIUsageTracker`).
  - Auditoria completa dos 11 agentes e matriz de capacidades (sem fingir LLM onde opera template ou regra determinística).
  - Pipeline de Operação de Marketing em 10 etapas integradas ponta a ponta (`POST /api/v1/marketing/full-operation-pipeline`).
  - Auditoria individual e categorização das 6 redes sociais (`GET /api/v1/social/platforms-audit`) e rotas OAuth 2.0 oficiais.
  - Auditoria técnica de SEO real integrada à API pública Google PageSpeed Insights v5, sitemap.xml e robots.txt dinâmicos.
  - Scheduler APScheduler 100% nativo em Python sincronizado no PostgreSQL (`scheduler_heartbeats`), idempotência comprovada e recuperação após reinício (`BOOT`/`CATCHUP`).
  - Assistente de Onboarding da Primeira Empresa (`POST /api/v1/onboarding/company`) sem inventar dados, gerando planos e diagnósticos a partir de informações informadas.
  - Painel de Autonomia por Agente e limites operacionais estritos (`PUT /api/v1/autonomy/limits`), garantindo aprovação humana obrigatória para ações financeiras.
  - Suíte de testes automatizados expandida para 25 testes aprovados (`25 passed`).

