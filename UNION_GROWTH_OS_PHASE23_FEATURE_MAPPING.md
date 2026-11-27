# FASE 23 — MAPEAMENTO DE FUNCIONALIDADES (REAL vs. SANDBOX vs. BLOCKED)

| Módulo / Recurso | Status Real na Produção | Classificação de Dados | Observação Verificada |
|---|---|---|---|
| **AI Growth Command Center** | 100% Operacional | `REAL` / `ESTIMATIVA` / `NAO_DISPONIVEL` | Consolida 12 dimensões de saúde, Growth Score documentado, Briefing Diário/Semanal, Radar e Ações |
| **ASK UNION (Copiloto)** | 100% Operacional | `REAL` | Classifica intenção do empreendedor com contexto real do banco e executa/agenda ações rastreáveis |
| **Modo Simples / Avançado** | 100% Operacional | `REAL` | Alternância persistida em PostgreSQL (`tenants.ui_mode`) e cabeçalho |
| **Onboarding Progressivo 6 Etapas** | 100% Operacional | `REAL` | Salva/recupera/reinicia etapas 1–6 em banco (`onboarding_step`, `onboarding_state_json`) |
| **Brand Intelligence Center** | 100% Operacional | `REAL` | Central visual/verbal, versionamento (`brand_versions`) e detector automático de inconsistências |
| **Fábrica de Conteúdo (30 Peças)** | 100% Operacional | `GOAL` / `REAL` | Lê marca, site, nicho, persona, oferta e campanha; pacote assistido em 1 clique |
| **Conversational Automation Builder** | 100% Operacional | `REAL` | 100% Python/APScheduler (zero n8n); dry-run + aprovação explícita persistida |
| **12 Agentes (`AGENT_01..AGENT_12`)** | 100% Operacional | `DETERMINISTIC_PYTHON_ENGINE` / `TEMPLATE_ENGINE` | Inclui novo `AGENT_12_DATA_ANALYST`; narrativa LLM opcional quando há cota gratuita válida |
| **Analytics & Attribution Hub** | 100% Operacional | `REAL` / `NAO_DISPONIVEL` | Atribuição First-Touch real em CRM/Financeiro; GA4/Search Console externos ficam `NAO_DISPONIVEL` sem OAuth |
| **Pagamentos & Cobrança** | Isolado | `SANDBOX` | Mercado Pago opera estritamente em Sandbox até configuração explícita e aprovação do proprietário |
| **Publicação Direta Social / Google Ads / OpenAI / Imagen 3 / Veo 2** | Aguardando Credencial ou Política Gratuita | `BLOCKED` / `Modo Assistido` | `FREE_ONLY` bloqueia modelos pagos (`HTTP 402`/GPT-4o); redes sem OAuth usam Modo Assistido sem simular envio |
