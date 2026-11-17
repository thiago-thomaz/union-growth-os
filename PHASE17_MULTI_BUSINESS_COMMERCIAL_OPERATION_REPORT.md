# UNION GROWTH OS — FASE 17: OPERAÇÃO COMERCIAL MULTINEGÓCIO, AQUISIÇÃO DE CLIENTES E GERAÇÃO DE RECEITA

**Data da Implantação e Auditoria**: 17 de Novembro de 2026  
**Responsável Técnico**: Antigravity CTO, Principal AI Architect & Growth Director  
**URL Oficial de Produção**: [https://automacao.projetosunion.cloud](https://automacao.projetosunion.cloud)  
**Repositório GitHub**: [https://github.com/thiago-thomaz/union-growth-os](https://github.com/thiago-thomaz/union-growth-os) (`main`)  
**VPS Oficial**: `72.62.13.62` (Coolify + Docker + Traefik + PostgreSQL 16 + FastAPI + Next.js 15 + APScheduler)  

---

## 1. QUADRO EXECUTIVO DE CLASSIFICAÇÃO (FASE 17)

| Item Auditado | Classificação | Evidência Técnica Real em Produção |
| :--- | :---: | :--- |
| **1. Auditoria Inicial & Preservação** | **APROVADO** | Commit anterior `ddb3b5e` verificado; 100% dos módulos, agentes e projetos da VPS preservados |
| **2. Três Unidades Comerciais** | **APROVADO** | `UNION_TECH`, `UNION_AGENCY` e `UNION_PARTNERS` persistidas no PostgreSQL e integradas ao AI CEO |
| **3. Arquitetura Multinegócio & Migrações** | **APROVADO** | 11 novas entidades + 20 colunas idempotentes adicionadas sem quebrar dados existentes |
| **4. Catálogo UNION TECH (7 Serviços)** | **APROVADO** | `SRV_01` a `SRV_07` ativos com calculadora dinâmica (horas, complexidade, infra, impostos, margem) |
| **5. Inteligência Comercial (8 Segmentos)** | **APROVADO** | Varejo, Restaurantes, Distribuidores, Clínicas, PMEs, E-commerce, Serviços e Tech mapeados |
| **6. Aquisição, Deduplicação & LGPD** | **APROVADO** | Captura com base legal, finalidade, opt-out, bloqueio e deduplicação automática por e-mail/unidade |
| **7. 9 Landing Pages & Funil de 10 Etapas** | **APROVADO** | `union-tech` + 6 páginas técnicas + `union-agency` + `union-partners`; funil `VISITANTE` → `POS_VENDA` |
| **8. Gerador de Propostas & Trava Humana** | **APROVADO** | Geração de propostas + visualização PDF/HTML + trava estrita (proibido fechar sem `owner_approved`) |
| **9. UNION AGENCY — Operação Clientes** | **APROVADO** | Contas isoladas de clientes com planos configuráveis (`STARTER`, `PRO`, `BUSINESS`, `ENTERPRISE`) |
| **10. UNION PARTNERS — Afiliados** | **PARCIAL** | 5 programas mapeados, rastreamento de cliques (0 venda por clique) e conciliação pronta; APIs externas aguardam credenciais |
| **11. Content Factory Multinegócio** | **APROVADO** | Lotes segmentados por unidade (`business_unit_code`) e UTM; publicação assistida honesta ativa |
| **12. AI CEO Consolidado (11 Agentes)** | **APROVADO** | Briefing diário consolidando as 3 unidades com classificação honesta `DETERMINISTIC_PYTHON_ENGINE` |
| **13. Automação Comercial 24/7** | **APROVADO** | 12 rotinas comerciais das `07:00` às `19:00` (`America/Sao_Paulo`) ativas no APScheduler com idempotência |
| **14. Financeiro Consolidado & Por Unidade**| **APROVADO** | Separação rigorosa entre `DADO_REAL`, `ESTIMATIVA`, `PROJECAO` e `META` |
| **15. Dashboard Executivo Multinegócio** | **APROVADO** | Nova central `🏢 Multinegócio (3 Unidades)` com filtro individual/consolidado e ações reais |
| **16. Suíte de Testes (40 Testes)** | **APROVADO** | 40/40 testes automatizados aprovados (33 anteriores + 7 novos testes da Fase 17) |
| **17. CI/CD & Deploy Automático na VPS** | **APROVADO** | Código publicado no GitHub `main`, implantado via Coolify na VPS e validado com HTTP 200 |

---

## 2. AUDITORIA INICIAL E ARQUITETURA REAPROVEITADA

Antes de qualquer alteração, o estado real do repositório e da VPS foi auditado:
- **Commit Anterior Verificado**: `ddb3b5eb64c5e95b1d626b6ab9f398fa0da32194` (implantado no Coolify sob o deployment `cwpv66ev81bfuabuntrqavfc`).
- **Isolamento Estrito da VPS**: Os demais containers do servidor (`arena-play`, `barberflow`, `cidade-ativa-prefeitura`, `union-money-ai`, etc.) permaneceram 100% intocados.
- **Módulos Reaproveitados**:
  - `CRMLead`, `CRMDeal`, `CRMActivity` foram estendidos via migrações DDL idempotentes (`run_automatic_schema_migrations`) para suportar `business_unit_code`, `funnel_stage` (10 etapas), `legal_basis`, `purpose_description`, `campaign_attribution` e `recurring_mrr_brl`, evitando duplicação de tabelas de CRM.
  - `ContentFactoryItem`, `EditorialCalendarItem`, `MarketingCampaign`, `FinancialRecord` e `AutomationRule` receberam `business_unit_code` para segmentação nativa entre as 3 unidades.

---

## 3. TRÊS UNIDADES COMERCIAIS INDEPENDENTES

| Código | Nome da Unidade | Foco Operacional | Fontes de Receita |
| :--- | :--- | :--- | :--- |
| **`UNION_TECH`** | UNION TECH — IA, Automação & Sistemas | Comercialização de serviços próprios de tecnologia, agentes de IA, automações em Python, dashboards e sistemas sob medida. | Implantação (Setup), Projetos Fechados, Mensalidades (MRR), Suporte, Consultoria e Licenciamento. |
| **`UNION_AGENCY`** | UNION AGENCY — Marketing, SEO & Growth | Operação de marketing digital, SEO técnico, Content Factory 30D, copywriting e geração de leads para empresas clientes. | Implantação, Planos Mensais Recorrentes (`STARTER`, `PRO`, `BUSINESS`, `ENTERPRISE`) e Projetos Especiais. |
| **`UNION_PARTNERS`**| UNION PARTNERS — Afiliados & Parcerias | Curadoria técnica, comparativos e links rastreáveis em programas de afiliados (Mercado Livre, Amazon, Shopee, SaaS e Tech). | Comissões por vendas atribuídas e confirmadas pelas plataformas, indicações SaaS e parcerias B2B. |

---

## 4. CATÁLOGO COMERCIAL UNION TECH E CALCULADORA DINÂMICA DE PREÇOS

Foram implementados os **7 Serviços Principais da UNION TECH** com calculadora dinâmica (`calculate_service_pricing`) baseada em horas de desenvolvimento, nível de complexidade (`LOW=1.0x`, `MEDIUM=1.25x`, `HIGH=1.55x`, `ENTERPRISE=2.0x`), valor/hora, infraestrutura, APIs/ferramentas, suporte, impostos configuráveis e margem desejada:

1. **`SRV_01_DIAGNOSTICO`**: Diagnóstico de Automação e Inteligência Artificial (Prazo: 7 dias | 12h estimadas | Complexidade: LOW).
2. **`SRV_02_AGENTES_IA`**: Agentes de IA Especializados em Atendimento, Suporte ou Vendas (Prazo: 15 dias | 28h estimadas | Complexidade: MEDIUM).
3. **`SRV_03_AUTOMACAO_PROCESSOS`**: Automação Empresarial e Integrações Nativas em Python (Prazo: 20 dias | 32h estimadas | Complexidade: MEDIUM).
4. **`SRV_04_DASHBOARDS`**: Dashboards Inteligentes e Relatórios Executivos (Prazo: 14 dias | 24h estimadas | Complexidade: MEDIUM).
5. **`SRV_05_MARKETING_IA`**: Infraestrutura de Marketing e Conteúdo com IA (Prazo: 12 dias | 20h estimadas | Complexidade: MEDIUM).
6. **`SRV_06_CRM_COMERCIAL`**: CRM Inteligente, Lead Scoring e Automação Comercial (Prazo: 14 dias | 22h estimadas | Complexidade: MEDIUM).
7. **`SRV_07_SISTEMAS_SOB_MEDIDA`**: Sistemas Empresariais e Plataformas Full-Stack Sob Medida (Prazo: 45 dias | 80h estimadas | Complexidade: HIGH).

> **Governança de Preços**: Nenhum preço é imposto de forma fixa. O proprietário pode ajustar horas, custos, impostos, margem e preço final via `PUT /api/v1/commercial/services/{id}/pricing` e marcar `owner_approve_pricing=True`.

---

## 5. INTELIGÊNCIA COMERCIAL, LANDING PAGES, FUNIL DE 10 ETAPAS E PROPOSTAS

- **Oportunidades de Mercado (`MarketOpportunity`)**: Mapeamento estruturado dos 8 segmentos prioritários (**Varejo, Restaurantes, Distribuidores, Clínicas e Prestadores de Serviços, PMEs, E-commerce, Serviços Profissionais e Empresas de Tecnologia**), conectando dores reais ao serviço recomendado, sem inventar empresas ou contatos ilegais.
- **9 Landing Pages Independentes (`LandingPage`)**:
  - Página principal: `/union-tech`
  - Páginas específicas: `/agentes-ia`, `/automacao-empresarial`, `/consultoria-ia`, `/crm-inteligente`, `/marketing-automatizado`, `/sistemas-sob-medida`
  - Páginas das demais unidades: `/union-agency` e `/union-partners`
  - Nenhuma página utiliza depoimentos fictícios, logotipos falsos ou promessas irreais; todas exibem exemplos reais da arquitetura do próprio UNION GROWTH OS.
- **Funil Comercial de 10 Etapas**:
  `VISITANTE → INTERESSADO → LEAD → QUALIFICADO → DIAGNOSTICO → PROPOSTA → NEGOCIACAO → GANHO → PERDIDO → POS_VENDA`
- **Gerador de Propostas Comerciais (`CommercialProposal`)**:
  - Ciclo de status completo: `DRAFT`, `PENDING_APPROVAL`, `SENT`, `VIEWED`, `NEGOTIATION`, `ACCEPTED`, `REJECTED`, `EXPIRED`.
  - **Trava Estrita de Governança**: O endpoint `PUT /api/v1/commercial/proposals/{id}/status` bloqueia com `HTTP 403` qualquer tentativa de mudar o status para `SENT` ou `ACCEPTED` sem `owner_approve=True`.
  - **Exportação PDF/HTML**: Endpoint `GET /api/v1/commercial/proposals/{id}/pdf` gera documento executivo formatado para impressão/PDF.

---

## 6. UNION AGENCY E UNION PARTNERS (AFILIADOS)

### 6.1. UNION AGENCY (`AgencyClientAccount`)
- Gestão de contas isoladas por cliente com marca, segmento, público-alvo, objetivos, tom de voz e limites automáticos por plano (`STARTER`, `PRO`, `BUSINESS`, `ENTERPRISE`).

### 6.2. UNION PARTNERS (`AffiliateProgram`, `AffiliateProduct`, `AffiliateClick`, `AffiliateConversion`)
- **5 Programas Cadastrados**: Mercado Livre, Amazon Brasil, Shopee Brasil, Ferramentas Digitais & Cloud, e Parcerias de Tecnologia B2B.
- **Regra Estrita Anti-Falso Positivo**:
  1. Cliques registrados em `POST /api/v1/partners/clicks` retornam explicitamente `counted_as_sale: False` e `revenue_recorded_brl: 0.0`.
  2. Conversões registradas com status `ESTIMATED` ou `PENDING_CONFIRMATION` permanecem com `reconciled_in_finance: False` e **não entram no faturamento confirmado**.
  3. Somente após conciliação formal (`POST /api/v1/partners/conversions/{id}/reconcile`) com `commission_status` em `APPROVED` ou `PAID` e evidência de atribuição da plataforma, o valor é lançado em `FinancialRecord` (`UNION_PARTNERS`).

---

## 7. AUTOMAÇÃO COMERCIAL 24/7 NO APSCHEDULER (`America/Sao_Paulo`)

Foram configuradas e ativadas as 12 rotinas comerciais diárias no APScheduler nativo em Python (zero dependência de n8n):

| Horário | Código da Regra | Agente Responsável | Unidade | Missão Executada |
| :---: | :--- | :--- | :---: | :--- |
| **07:00** | `p17_0700_market_research` | `AGENT_09_COMPETITIVE` | `UNION_TECH` | Pesquisa diária de oportunidades comerciais setoriais |
| **08:00** | `p17_0800_ceo_multibusiness` | `AGENT_01_CEO` | `ALL` | CEO Daily Briefing Consolidado Multinegócio |
| **09:00** | `p17_0900_commercial_plan` | `AGENT_02_CMO` | `ALL` | Planejamento comercial e metas das 3 unidades |
| **10:00** | `p17_1000_content_generation` | `AGENT_06_COPYWRITER` | `ALL` | Geração de conteúdo segmentado por unidade |
| **11:00** | `p17_1100_publish_queue_check`| `AGENT_04_SOCIAL` | `ALL` | Verificação da fila de publicação e pacotes assistidos |
| **12:00** | `p17_1200_lead_qualification` | `AGENT_08_SALES` | `UNION_TECH` | Qualificação e Lead Scoring de leads autorizados |
| **14:00** | `p17_1400_seo_research` | `AGENT_03_SEO` | `UNION_TECH` | Pesquisa SEO e monitoramento de landing pages comerciais |
| **15:00** | `p17_1500_competitive_analysis`| `AGENT_09_COMPETITIVE` | `UNION_PARTNERS`| Análise competitiva e curadoria de ofertas |
| **16:00** | `p17_1600_deals_followup` | `AGENT_08_SALES` | `UNION_TECH` | Acompanhamento de negociações e propostas pendentes |
| **17:00** | `p17_1700_campaigns_analysis` | `AGENT_07_GROWTH` | `UNION_AGENCY` | Análise de campanhas de clientes e conversão |
| **18:00** | `p17_1800_financial_report` | `AGENT_10_FINANCE` | `ALL` | Relatório financeiro e conciliação estrita por unidade |
| **19:00** | `p17_1900_commercial_summary` | `AGENT_01_CEO` | `ALL` | Relatório comercial consolidado de fim de dia |

---

## 8. TESTES AUTOMATIZADOS (40 TESTES APROVADOS)

A suíte de testes (`backend/tests/test_union_growth_os.py`) foi expandida de 33 para **40 testes automatizados**, validando:
- `test_33`: Criação das 3 unidades, 7 serviços UNION TECH, calculadora de preços e ofertas.
- `test_34`: 8 segmentos de oportunidades de mercado, pesquisa sob demanda e 9 landing pages.
- `test_35`: Captura de lead via landing page com LGPD, deduplicação por e-mail/unidade, lead scoring e funil de 10 etapas.
- `test_36`: Propostas comerciais, bloqueio HTTP 403 sem aprovação do proprietário, geração de PDF/HTML e fechamento (`ACCEPTED`).
- `test_37`: Contas isoladas de clientes na `UNION_AGENCY` e limites por plano.
- `test_38`: Programas de afiliados (`UNION_PARTNERS`), clique rastreável registrando zero venda/receita, conversão pendente e conciliação financeira com evidência.
- `test_39`: Content Factory por unidade, resumo financeiro separando `dado_real`, `projecao` e `meta`, briefing CEO multinegócio e dashboard.

---

## 9. PENDÊNCIAS QUE DEPENDEM EXCLUSIVAMENTE DE AÇÃO HUMANA

1. **Aprovação Comercial de Tabelas de Preços e Propostas**: Revisar e aprovar os preços finais configurados para cada serviço na aba `🏢 Multinegócio (3 Unidades)`.
2. **Credenciais de Afiliados (`UNION_PARTNERS`)**: Cadastrar os IDs/Tags de afiliado aprovados no Mercado Livre, Amazon Associados e Shopee Afiliados para substituir os links de referência pelos links com tag de comissão ativa.
3. **Credenciais OAuth de Redes Sociais e Analytics**: Vincular App ID / Client Secret na Central de Integrações quando desejar disparo externo automático (até lá, o modo de **Publicação Assistida** permanece 100% operacional).
4. **Custos Adicionais**: **R$ 0,00** (nenhum serviço pago externo, API paga ou tráfego pago foi contratado).

