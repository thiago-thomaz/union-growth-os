"""UNION GROWTH OS — FASE 17: OPERAÇÃO COMERCIAL MULTINEGÓCIO, AQUISIÇÃO DE CLIENTES E GERAÇÃO DE RECEITA

Implementa os motores de negócio reais e auditáveis para administrar 3 unidades independentes:
1. UNION TECH: Comercialização de serviços próprios de IA, agentes, automação, dashboards e software sob medida.
2. UNION AGENCY: Operação de marketing, SEO, conteúdo, CRM e growth para empresas clientes isoladas.
3. UNION PARTNERS: Marketing de afiliados (Mercado Livre, Amazon, Shopee, SaaS) com rastreamento de cliques e conciliação estrita de comissões.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.agents.orchestrator import compute_lead_score
from app.core.config import settings
from app.models.entities import (
    AffiliateClick,
    AffiliateConversion,
    AffiliateProduct,
    AffiliateProgram,
    AgencyClientAccount,
    ApprovalRequest,
    AuditLog,
    AutomationRule,
    BusinessUnit,
    CEODailyBriefing,
    CommercialOffer,
    CommercialProposal,
    ContentFactoryItem,
    CRMActivity,
    CRMDeal,
    CRMLead,
    EditorialCalendarItem,
    FinancialRecord,
    IntegrationConnection,
    LandingPage,
    MarketingCampaign,
    MarketOpportunity,
    OperationalAlert,
    PaymentTransaction,
    ProductService,
    ServiceDeliveryProject,
    Tenant,
)

COMPLEXITY_MULTIPLIERS = {
    "LOW": 1.0,
    "MEDIUM": 1.25,
    "HIGH": 1.55,
    "ENTERPRISE": 2.0,
}

AGENCY_PLAN_LIMITS = {
    "STARTER": {"max_campaigns": 2, "max_monthly_contents": 12, "max_channels": 2, "seo_audits_per_month": 2},
    "PRO": {"max_campaigns": 5, "max_monthly_contents": 30, "max_channels": 4, "seo_audits_per_month": 6},
    "BUSINESS": {"max_campaigns": 12, "max_monthly_contents": 60, "max_channels": 6, "seo_audits_per_month": 15},
    "ENTERPRISE": {"max_campaigns": 50, "max_monthly_contents": 150, "max_channels": 8, "seo_audits_per_month": 50},
}

FUNNEL_STAGES_ORDER = [
    "VISITANTE",
    "INTERESSADO",
    "LEAD",
    "QUALIFICACAO",
    "QUALIFICADO",
    "DIAGNOSTICO",
    "OPORTUNIDADE",
    "PROPOSTA",
    "APROVACAO",
    "NEGOCIACAO",
    "CONTRATO",
    "PAGAMENTO",
    "ONBOARDING",
    "ENTREGA",
    "POS_VENDA",
    "GANHO",
    "PERDIDO",
]


def calculate_service_pricing(
    dev_hours: float,
    complexity: str,
    hourly_rate: float,
    infra_cost: float,
    tools_api_cost: float,
    support_cost: float,
    tax_rate_pct: float,
    target_margin_pct: float,
) -> dict[str, float]:
    """
    Calcula custo estimado, preço sugerido e margem líquida de forma determinística
    considerando horas, complexidade, infraestrutura, APIs, suporte, impostos e margem alvo.
    """
    comp_mult = COMPLEXITY_MULTIPLIERS.get(complexity.upper(), 1.25)
    labor_cost = max(0.0, dev_hours) * max(0.0, hourly_rate) * comp_mult
    total_cost = round(labor_cost + max(0.0, infra_cost) + max(0.0, tools_api_cost) + max(0.0, support_cost), 2)

    deductions_ratio = (max(0.0, tax_rate_pct) + max(0.0, target_margin_pct)) / 100.0
    divisor = max(0.15, 1.0 - deductions_ratio)
    suggested_price = round(total_cost / divisor, 2)
    net_margin_pct = round(((suggested_price * (1.0 - tax_rate_pct / 100.0) - total_cost) / max(1.0, suggested_price)) * 100.0, 2)

    return {
        "complexity_multiplier": comp_mult,
        "labor_cost_brl": round(labor_cost, 2),
        "estimated_cost_brl": total_cost,
        "suggested_price_brl": suggested_price,
        "estimated_margin_pct": net_margin_pct,
    }


def ensure_phase17_multibusiness_seeded(db: Session, tenant: Tenant) -> dict[str, Any]:
    """
    Inicializa de forma idempotente a estrutura multinegócio da Fase 17:
    - 3 Unidades Comerciais (UNION_TECH, UNION_AGENCY, UNION_PARTNERS)
    - Catálogo inicial de 7 serviços de IA/Automação (UNION_TECH) + serviços de Agência
    - Ofertas comerciais configuráveis
    - 8 Oportunidades de Mercado mapeadas
    - 9 Landing Pages comerciais
    - 5 Programas de Afiliados (Mercado Livre, Amazon, Shopee, SaaS, Tech)
    - 12 Rotinas Comerciais 24/7 no APScheduler (07:00 às 19:00 America/Sao_Paulo)
    """
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 1. TRÊS UNIDADES DE NEGÓCIO
    units_spec = [
        {
            "code": "UNION_TECH",
            "name": "UNION TECH — Inteligência Artificial, Automação & Sistemas",
            "business_type": "B2B Technology, AI Agents & Process Automation Services",
            "description": "Comercialização de serviços próprios de tecnologia, agentes de IA, automação empresarial, integrações, dashboards executivos e sistemas sob medida.",
            "target_audience": "PMEs, Varejo, Clínicas, Distribuidores, E-commerces e Operações B2B",
            "value_proposition": "Redução de trabalho manual, atendimento inteligente 24/7 e sistemas autônomos sob medida com ROI mensurável.",
            "products_services": [
                "Diagnóstico de Automação",
                "Agentes de IA",
                "Automação Empresarial",
                "Dashboards Inteligentes",
                "Marketing com IA",
                "CRM e Automação Comercial",
                "Sistemas Sob Medida",
            ],
            "acquisition_channels": ["Landing Pages Técnicas", "SEO Orgânico", "Diagnóstico Gratuito", "LinkedIn B2B", "Indicações"],
            "revenue_streams": ["Implantação (Setup)", "Projetos Fechados", "Mensalidades (MRR)", "Suporte & Manutenção", "Consultoria", "Licenciamento"],
            "monthly_revenue_goal_brl": 35000.0,
            "monthly_budget_brl": 1500.0,
        },
        {
            "code": "UNION_AGENCY",
            "name": "UNION AGENCY — Marketing Digital, SEO, Content Factory & Growth",
            "business_type": "B2B Marketing, SEO, Content & Commercial Growth Agency",
            "description": "Operação completa de planejamento estratégico, SEO, redes sociais, Content Factory, copywriting, CRM e geração de leads para empresas clientes.",
            "target_audience": "Empresas que buscam terceirizar marketing, SEO e geração de demanda com inteligência artificial",
            "value_proposition": "Equipe digital completa de 11 especialistas operando o marketing, conteúdo e funil comercial da sua empresa todos os dias.",
            "products_services": [
                "Plano Starter Growth",
                "Plano Pro Marketing & SEO",
                "Plano Business Full-Funnel",
                "Plano Enterprise Dedicated",
            ],
            "acquisition_channels": ["Auditoria SEO Gratuita", "Content Factory Showcase", "Inbound Marketing", "Parcerias"],
            "revenue_streams": ["Taxa de Implantação", "Planos Mensais Recorrentes (Retainer)", "Projetos Especiais", "Serviços Adicionais"],
            "monthly_revenue_goal_brl": 25000.0,
            "monthly_budget_brl": 1000.0,
        },
        {
            "code": "UNION_PARTNERS",
            "name": "UNION PARTNERS — Afiliados, Curadoria & Parcerias Comerciais",
            "business_type": "Affiliate Marketing, Product Curation & Tech Partnerships",
            "description": "Operação de recomendações, comparativos técnicos e curadoria de produtos e ferramentas em programas oficiais de afiliados e parcerias.",
            "target_audience": "Compradores online, gestores de PMEs e profissionais buscando ferramentas, equipamentos e soluções testadas",
            "value_proposition": "Curadoria técnica transparente, comparativos objetivos e links oficiais verificados nos maiores marketplaces e plataformas SaaS.",
            "products_services": [
                "Curadoria Mercado Livre",
                "Curadoria Amazon Brasil",
                "Curadoria Shopee Oficial",
                "Afiliados de Ferramentas SaaS & Cloud",
                "Parcerias de Tecnologia B2B",
            ],
            "acquisition_channels": ["Artigos de Comparação SEO", "Redes Sociais", "YouTube Reviews", "Pinterest", "Guias de Compra"],
            "revenue_streams": ["Comissões por Vendas Atribuídas e Confirmadas", "Comissões por Indicação SaaS", "Parcerias Comerciais Aprovadas"],
            "monthly_revenue_goal_brl": 10000.0,
            "monthly_budget_brl": 500.0,
        },
    ]

    for u in units_spec:
        existing_u = (
            db.query(BusinessUnit)
            .filter(BusinessUnit.tenant_id == tenant.id, BusinessUnit.code == u["code"])
            .first()
        )
        if not existing_u:
            db.add(
                BusinessUnit(
                    tenant_id=tenant.id,
                    code=u["code"],
                    name=u["name"],
                    business_type=u["business_type"],
                    description=u["description"],
                    target_audience=u["target_audience"],
                    value_proposition=u["value_proposition"],
                    products_services_json=json.dumps(u["products_services"], ensure_ascii=False),
                    acquisition_channels_json=json.dumps(u["acquisition_channels"], ensure_ascii=False),
                    revenue_streams_json=json.dumps(u["revenue_streams"], ensure_ascii=False),
                    monthly_revenue_goal_brl=u["monthly_revenue_goal_brl"],
                    monthly_budget_brl=u["monthly_budget_brl"],
                    status="ACTIVE",
                    data_origin="REAL",
                )
            )
    db.commit()

    # 2. CATÁLOGO COMERCIAL INICIAL — 7 SERVIÇOS UNION TECH + 2 SERVIÇOS UNION AGENCY
    services_catalog = [
        {
            "business_unit_code": "UNION_TECH",
            "service_code": "SRV_01_DIAGNOSTICO",
            "name": "SERVIÇO 01 — Diagnóstico de Automação e Inteligência Artificial",
            "category": "Consultoria & Arquitetura",
            "description": "Mapeamento completo de processos operacionais, identificação de gargalos manuais, oportunidades de IA e plano executivo de implantação com ROI estimado.",
            "problem_solved": "Empresas que perdem horas em tarefas manuais e planilhas desconectadas, mas não sabem por onde começar a automatizar com segurança.",
            "target_audience": "PMEs, Clínicas, Escritórios, Distribuidores e Operações Comerciais",
            "benefits": [
                "Visão clara dos processos que mais consomem tempo e dinheiro",
                "Arquitetura recomendada sem dependência de licenças caras",
                "Cronograma de implantação priorizado por retorno financeiro",
            ],
            "scope_summary": "Entrevistas operacionais, análise de ferramentas atuais, desenho de fluxos futuros e relatório técnico-comercial.",
            "deliverables": [
                "Mapa de Processos e Gargalos Operacionais",
                "Matriz de Oportunidades de IA e Automação",
                "Plano Técnico de Implantação e Orçamento Detalhado",
            ],
            "estimated_timeline_days": 7,
            "dev_hours_estimated": 12.0,
            "complexity_level": "LOW",
            "hourly_rate_brl": 150.0,
            "infra_cost_brl": 0.0,
            "tools_api_cost_brl": 0.0,
            "support_cost_brl": 150.0,
            "tax_rate_pct": 12.0,
            "target_margin_pct": 45.0,
            "recurring_monthly_brl": 0.0,
        },
        {
            "business_unit_code": "UNION_TECH",
            "service_code": "SRV_02_AGENTES_IA",
            "name": "SERVIÇO 02 — Agentes de IA Especializados",
            "category": "Inteligência Artificial Empresarial",
            "description": "Desenvolvimento e implantação de agentes inteligentes especializados em atendimento, triagem comercial, suporte técnico ou análise operacional.",
            "problem_solved": "Demora no atendimento a leads, perda de vendas fora do horário comercial e sobrecarga da equipe com perguntas repetitivas.",
            "target_audience": "Clínicas, E-commerces, Imobiliárias, Prestadores de Serviços e Empresas B2B",
            "benefits": [
                "Atendimento e qualificação imediata 24/7",
                "Base de conhecimento treinada nas regras reais da empresa",
                "Encaminhamento estruturado para fechamento humano",
            ],
            "scope_summary": "Configuração do motor de IA/regras, integração com base de conhecimento, fluxos de segurança e painel de acompanhamento.",
            "deliverables": [
                "Agente de IA configurado e validado",
                "Base de conhecimento estruturada da empresa",
                "Painel de histórico e transferência para atendimento humano",
            ],
            "estimated_timeline_days": 15,
            "dev_hours_estimated": 28.0,
            "complexity_level": "MEDIUM",
            "hourly_rate_brl": 150.0,
            "infra_cost_brl": 120.0,
            "tools_api_cost_brl": 100.0,
            "support_cost_brl": 250.0,
            "tax_rate_pct": 12.0,
            "target_margin_pct": 45.0,
            "recurring_monthly_brl": 690.0,
        },
        {
            "business_unit_code": "UNION_TECH",
            "service_code": "SRV_03_AUTOMACAO_PROCESSOS",
            "name": "SERVIÇO 03 — Automação Empresarial e Integrações",
            "category": "Automação & Integração de Sistemas",
            "description": "Automatização nativa em Python de rotinas repetitivas, sincronização entre sistemas (ERP, CRM, Financeiro) e alertas operacionais.",
            "problem_solved": "Retrabalho manual de digitação entre sistemas, erros operacionais, atrasos em cobranças e falta de sincronia entre vendas e financeiro.",
            "target_audience": "Distribuidores, Varejo, Indústrias Leves, Contabilidades e Empresas de Serviços",
            "benefits": [
                "Eliminação de digitação manual e erros humanos",
                "Execução programada 24/7 com logs e retry automático",
                "Arquitetura 100% própria em Python sem mensalidades de plataformas no-code",
            ],
            "scope_summary": "Desenvolvimento de conectores via API, agendadores nativos, tratamento de falhas e logs de auditoria.",
            "deliverables": [
                "Rotinas de automação nativas em produção",
                "Integrações via API entre os sistemas do cliente",
                "Monitoramento de execução com alertas de falha",
            ],
            "estimated_timeline_days": 20,
            "dev_hours_estimated": 32.0,
            "complexity_level": "MEDIUM",
            "hourly_rate_brl": 150.0,
            "infra_cost_brl": 100.0,
            "tools_api_cost_brl": 50.0,
            "support_cost_brl": 300.0,
            "tax_rate_pct": 12.0,
            "target_margin_pct": 45.0,
            "recurring_monthly_brl": 590.0,
        },
        {
            "business_unit_code": "UNION_TECH",
            "service_code": "SRV_04_DASHBOARDS",
            "name": "SERVIÇO 04 — Dashboards Inteligentes e Relatórios Executivos",
            "category": "Business Intelligence & Dados",
            "description": "Construção de painéis gerenciais em tempo real consolidando vendas, financeiro, marketing e indicadores operacionais com alertas automáticos.",
            "problem_solved": "Diretores que tomam decisões no escuro ou dependem de planilhas manuais demoradas e desatualizadas.",
            "target_audience": "CEOs, Diretores Comerciais, Gestores Financeiros e Redes de Varejo",
            "benefits": [
                "Visão consolidada em tempo real de receitas, custos e margens",
                "Separação rigorosa entre dados reais, metas e projeções",
                "Briefings executivos diários gerados automaticamente",
            ],
            "scope_summary": "Modelagem de indicadores, conexão com bancos de dados/planilhas, interface web responsiva e exportação de relatórios.",
            "deliverables": [
                "Dashboard Executivo Web com controle de acesso",
                "Motor de consolidação automática de KPIs",
                "Relatório diário/semanal automatizado para a diretoria",
            ],
            "estimated_timeline_days": 14,
            "dev_hours_estimated": 24.0,
            "complexity_level": "MEDIUM",
            "hourly_rate_brl": 150.0,
            "infra_cost_brl": 80.0,
            "tools_api_cost_brl": 0.0,
            "support_cost_brl": 200.0,
            "tax_rate_pct": 12.0,
            "target_margin_pct": 45.0,
            "recurring_monthly_brl": 490.0,
        },
        {
            "business_unit_code": "UNION_TECH",
            "service_code": "SRV_05_MARKETING_IA",
            "name": "SERVIÇO 05 — Infraestrutura de Marketing e Conteúdo com IA",
            "category": "Martech & Automação de Marketing",
            "description": "Implantação de fábrica de conteúdo, auditoria contínua de SEO, calendário editorial e páginas de captura de alta conversão.",
            "problem_solved": "Empresas sem presença digital consistente, alto custo de produção de conteúdo e baixo tráfego orgânico qualificado.",
            "target_audience": "Empresas B2B, Clínicas, E-commerces e Marcas Próprias",
            "benefits": [
                "Produção estruturada de conteúdo multicanal",
                "Otimização técnica de SEO e Core Web Vitals",
                "Calendário editorial com fluxo de aprovação",
            ],
            "scope_summary": "Configuração de SEO técnico, templates de marca, Content Factory e calendário de publicação.",
            "deliverables": [
                "Central Content Factory configurada para a marca",
                "Auditoria e otimização de SEO técnico (Sitemap, Schema.org)",
                "Calendário editorial de 30 dias pronto para publicação",
            ],
            "estimated_timeline_days": 12,
            "dev_hours_estimated": 20.0,
            "complexity_level": "MEDIUM",
            "hourly_rate_brl": 150.0,
            "infra_cost_brl": 80.0,
            "tools_api_cost_brl": 50.0,
            "support_cost_brl": 200.0,
            "tax_rate_pct": 12.0,
            "target_margin_pct": 45.0,
            "recurring_monthly_brl": 790.0,
        },
        {
            "business_unit_code": "UNION_TECH",
            "service_code": "SRV_06_CRM_COMERCIAL",
            "name": "SERVIÇO 06 — CRM Inteligente e Automação Comercial",
            "category": "Vendas & Gestão de Pipeline",
            "description": "Implantação de CRM com captura de leads, deduplicação, lead scoring automático, funil de vendas, gerador de propostas e governança LGPD.",
            "problem_solved": "Leads esquecidos sem follow-up, propostas demoradas e falta de previsibilidade de fechamento comercial.",
            "target_audience": "Equipes comerciais B2B, Consultorias, Distribuidoras e Prestadores de Serviços",
            "benefits": [
                "Priorização automática dos leads mais quentes (Lead Scoring)",
                "Geração rápida de propostas comerciais padronizadas",
                "Conformidade nativa com LGPD (consentimento e opt-out)",
            ],
            "scope_summary": "Configuração de etapas do funil, formulários de captura, régua de follow-up e modelos de propostas.",
            "deliverables": [
                "CRM configurado com funil de 10 etapas e Lead Scoring",
                "Landing Page integrada com captura e deduplicação de leads",
                "Gerador de propostas comerciais em PDF/HTML",
            ],
            "estimated_timeline_days": 14,
            "dev_hours_estimated": 22.0,
            "complexity_level": "MEDIUM",
            "hourly_rate_brl": 150.0,
            "infra_cost_brl": 80.0,
            "tools_api_cost_brl": 0.0,
            "support_cost_brl": 220.0,
            "tax_rate_pct": 12.0,
            "target_margin_pct": 45.0,
            "recurring_monthly_brl": 590.0,
        },
        {
            "business_unit_code": "UNION_TECH",
            "service_code": "SRV_07_SISTEMAS_SOB_MEDIDA",
            "name": "SERVIÇO 07 — Sistemas Empresariais e Plataformas Sob Medida",
            "category": "Engenharia de Software Customizada",
            "description": "Projeto, desenvolvimento full-stack (Python/FastAPI + Next.js + PostgreSQL) e implantação em nuvem de sistemas exclusivos para o negócio do cliente.",
            "problem_solved": "Processos específicos de negócio que softwares de prateleira não atendem ou cobram mensalidades proibitivas por usuário.",
            "target_audience": "Médias e Grandes Empresas, Startups, Redes de Franquias e Operações Especializadas",
            "benefits": [
                "Sistema 100% aderente à regra de negócio da empresa",
                "Sem cobrança abusiva por licença de usuário adicional",
                "Implantação segura em nuvem com backup e monitoramento",
            ],
            "scope_summary": "Levantamento de requisitos, arquitetura de banco de dados, backend API, frontend moderno, testes automatizados e deploy.",
            "deliverables": [
                "Aplicação Web Full-Stack em produção com HTTPS",
                "Banco de dados PostgreSQL isolado com backups automáticos",
                "Documentação técnica e treinamento da equipe",
            ],
            "estimated_timeline_days": 45,
            "dev_hours_estimated": 80.0,
            "complexity_level": "HIGH",
            "hourly_rate_brl": 160.0,
            "infra_cost_brl": 250.0,
            "tools_api_cost_brl": 100.0,
            "support_cost_brl": 600.0,
            "tax_rate_pct": 12.0,
            "target_margin_pct": 45.0,
            "recurring_monthly_brl": 1200.0,
        },
        {
            "business_unit_code": "UNION_AGENCY",
            "service_code": "AGY_01_GROWTH_RETAINER",
            "name": "UNION AGENCY — Assessoria Mensal de Growth, SEO e Conteúdo",
            "category": "Agência de Marketing & Growth",
            "description": "Operação contínua de planejamento, calendário editorial, Content Factory, SEO técnico e gestão de leads para empresas clientes.",
            "problem_solved": "Empresas que precisam de geração constante de demanda e autoridade digital sem contratar uma equipe interna inteira.",
            "target_audience": "PMEs, Marcas Regionais, Profissionais Liberais e E-commerces",
            "benefits": [
                "Calendário editorial de 30 peças mensais prontas",
                "Otimização semanal de SEO e palavras-chave",
                "Relatório executivo mensal de performance e leads",
            ],
            "scope_summary": "Gestão contínua de conteúdo, SEO, campanhas e acompanhamento do funil comercial do cliente.",
            "deliverables": [
                "30 conteúdos mensais multicanal",
                "Relatórios semanais de SEO e concorrentes",
                "Gestão ativa do pipeline de leads da empresa",
            ],
            "estimated_timeline_days": 30,
            "dev_hours_estimated": 16.0,
            "complexity_level": "MEDIUM",
            "hourly_rate_brl": 140.0,
            "infra_cost_brl": 50.0,
            "tools_api_cost_brl": 50.0,
            "support_cost_brl": 150.0,
            "tax_rate_pct": 12.0,
            "target_margin_pct": 45.0,
            "recurring_monthly_brl": 2500.0,
        },
    ]

    for s in services_catalog:
        existing_s = (
            db.query(ProductService)
            .filter(ProductService.tenant_id == tenant.id, ProductService.service_code == s["service_code"])
            .first()
        )
        if not existing_s:
            calc = calculate_service_pricing(
                dev_hours=s["dev_hours_estimated"],
                complexity=s["complexity_level"],
                hourly_rate=s["hourly_rate_brl"],
                infra_cost=s["infra_cost_brl"],
                tools_api_cost=s["tools_api_cost_brl"],
                support_cost=s["support_cost_brl"],
                tax_rate_pct=s["tax_rate_pct"],
                target_margin_pct=s["target_margin_pct"],
            )
            db.add(
                ProductService(
                    tenant_id=tenant.id,
                    business_unit_code=s["business_unit_code"],
                    service_code=s["service_code"],
                    name=s["name"],
                    category=s["category"],
                    description=s["description"],
                    problem_solved=s["problem_solved"],
                    target_audience=s["target_audience"],
                    benefits_json=json.dumps(s["benefits"], ensure_ascii=False),
                    scope_summary=s["scope_summary"],
                    deliverables_json=json.dumps(s["deliverables"], ensure_ascii=False),
                    estimated_timeline_days=s["estimated_timeline_days"],
                    dev_hours_estimated=s["dev_hours_estimated"],
                    complexity_level=s["complexity_level"],
                    hourly_rate_brl=s["hourly_rate_brl"],
                    infra_cost_brl=s["infra_cost_brl"],
                    tools_api_cost_brl=s["tools_api_cost_brl"],
                    support_cost_brl=s["support_cost_brl"],
                    tax_rate_pct=s["tax_rate_pct"],
                    target_margin_pct=s["target_margin_pct"],
                    estimated_cost_brl=calc["estimated_cost_brl"],
                    suggested_price_brl=calc["suggested_price_brl"],
                    configured_price_brl=calc["suggested_price_brl"],
                    recurring_monthly_brl=s["recurring_monthly_brl"],
                    estimated_margin_pct=calc["estimated_margin_pct"],
                    pricing_approved_by_owner=False,
                    availability_status="AVAILABLE",
                    data_origin="REAL",
                )
            )
    db.commit()

    # 3. OFERTAS COMERCIAIS E PLANOS CONFIGURÁVEIS
    if db.query(CommercialOffer).filter(CommercialOffer.tenant_id == tenant.id).count() == 0:
        offers_seed = [
            {
                "business_unit_code": "UNION_TECH",
                "name": "Pacote Aceleração IA — Diagnóstico + Agente de Atendimento",
                "headline": "Mapeamento de gargalos + implantação de Agente de IA em 15 dias",
                "offer_type": "HYBRID_SETUP_PLUS_MRR",
                "plan_tier": "PRO",
                "setup_fee_brl": 6800.0,
                "monthly_fee_brl": 690.0,
                "included_items": ["Diagnóstico de Processos", "Agente de IA 24/7", "Painel de Monitoramento"],
                "limits": {"agents": 1, "channels": 2, "support_sla_hours": 24},
            },
            {
                "business_unit_code": "UNION_AGENCY",
                "name": "Plano Agency STARTER",
                "headline": "Presença digital consistente e SEO básico para pequenas empresas",
                "offer_type": "RECURRING_PLAN",
                "plan_tier": "STARTER",
                "setup_fee_brl": 900.0,
                "monthly_fee_brl": 1490.0,
                "included_items": ["12 Conteúdos/mês", "2 Auditorias SEO/mês", "Relatório Mensal"],
                "limits": AGENCY_PLAN_LIMITS["STARTER"],
            },
            {
                "business_unit_code": "UNION_AGENCY",
                "name": "Plano Agency PRO",
                "headline": "Content Factory 30D + SEO Técnico + Gestão de Funil CRM",
                "offer_type": "RECURRING_PLAN",
                "plan_tier": "PRO",
                "setup_fee_brl": 1500.0,
                "monthly_fee_brl": 2900.0,
                "included_items": ["30 Conteúdos/mês", "SEO Semanal", "CRM & Lead Scoring", "Copywriting A/B"],
                "limits": AGENCY_PLAN_LIMITS["PRO"],
            },
            {
                "business_unit_code": "UNION_AGENCY",
                "name": "Plano Agency BUSINESS",
                "headline": "Operação completa de Marketing, Vendas e Inteligência Competitiva",
                "offer_type": "RECURRING_PLAN",
                "plan_tier": "BUSINESS",
                "setup_fee_brl": 2500.0,
                "monthly_fee_brl": 4900.0,
                "included_items": ["60 Conteúdos/mês", "Monitoramento de Concorrentes", "Funil Completo", "Dashboard Dedicado"],
                "limits": AGENCY_PLAN_LIMITS["BUSINESS"],
            },
            {
                "business_unit_code": "UNION_AGENCY",
                "name": "Plano Agency ENTERPRISE",
                "headline": "Diretoria Digital Dedicada Multi-Unidades com Customização Total",
                "offer_type": "RECURRING_PLAN",
                "plan_tier": "ENTERPRISE",
                "setup_fee_brl": 5000.0,
                "monthly_fee_brl": 8900.0,
                "included_items": ["150 Conteúdos/mês", "11 Agentes Dedicados", "Integrações Customizadas", "SLA Prioritário"],
                "limits": AGENCY_PLAN_LIMITS["ENTERPRISE"],
            },
        ]
        for off in offers_seed:
            db.add(
                CommercialOffer(
                    tenant_id=tenant.id,
                    business_unit_code=off["business_unit_code"],
                    name=off["name"],
                    headline=off["headline"],
                    offer_type=off["offer_type"],
                    plan_tier=off["plan_tier"],
                    setup_fee_brl=off["setup_fee_brl"],
                    monthly_fee_brl=off["monthly_fee_brl"],
                    included_items_json=json.dumps(off["included_items"], ensure_ascii=False),
                    limits_json=json.dumps(off["limits"], ensure_ascii=False),
                    owner_approved=False,
                    is_active=True,
                    data_origin="REAL",
                )
            )
        db.commit()

    # 4. INTELIGÊNCIA COMERCIAL — 8 SEGMENTOS PRIORITÁRIOS DE MERCADO
    if db.query(MarketOpportunity).filter(MarketOpportunity.tenant_id == tenant.id).count() == 0:
        opportunities_seed = [
            {
                "segment": "Varejo",
                "identified_problem": "Perda de clientes recorrentes por falta de pós-venda automatizado, ruptura de estoque sem alerta e atendimento lento no balcão/online.",
                "recommended_service_code": "SRV_03_AUTOMACAO_PROCESSOS",
                "recommended_service_name": "SERVIÇO 03 — Automação Empresarial e Integrações",
                "ideal_customer_profile": "Redes de lojas físicas e varejistas omnichannel com 5 a 50 funcionários",
                "commercial_potential": "HIGH",
                "implementation_difficulty": "MEDIUM",
                "priority": "HIGH",
                "justification": "Rápido retorno sobre investimento ao integrar ERP/PDV com alertas de recompra e painel diário de giro.",
            },
            {
                "segment": "Restaurantes",
                "identified_problem": "Alto volume de mensagens em horários de pico, perda de reservas/pedidos diretos e dependência excessiva de taxas de aplicativos de entrega.",
                "recommended_service_code": "SRV_02_AGENTES_IA",
                "recommended_service_name": "SERVIÇO 02 — Agentes de IA Especializados",
                "ideal_customer_profile": "Restaurantes, operações de delivery próprio e redes gastronômicas locais",
                "commercial_potential": "HIGH",
                "implementation_difficulty": "LOW",
                "priority": "HIGH",
                "justification": "Agente de triagem de cardápio/reservas e automação de fidelização reduzem custos operacionais imediatamente.",
            },
            {
                "segment": "Distribuidores",
                "identified_problem": "Cotações manuais demoradas por vendedores, pedidos digitados manualmente no ERP e falta de acompanhamento de clientes inativos.",
                "recommended_service_code": "SRV_06_CRM_COMERCIAL",
                "recommended_service_name": "SERVIÇO 06 — CRM Inteligente e Automação Comercial",
                "ideal_customer_profile": "Distribuidoras B2B de alimentos, autopeças, materiais elétricos e insumos",
                "commercial_potential": "VERY_HIGH",
                "implementation_difficulty": "MEDIUM",
                "priority": "URGENT",
                "justification": "Ticket médio B2B elevado; recuperar apenas 3 clientes inativos por mês paga toda a automação.",
            },
            {
                "segment": "Clínicas e Prestadores de Serviços",
                "identified_problem": "Taxa elevada de faltas (no-show) em consultas, recepção sobrecarregada respondendo dúvidas básicas e leads sem confirmação.",
                "recommended_service_code": "SRV_02_AGENTES_IA",
                "recommended_service_name": "SERVIÇO 02 — Agentes de IA Especializados",
                "ideal_customer_profile": "Clínicas médicas, odontológicas, estéticas e escritórios de advocacia/contabilidade",
                "commercial_potential": "VERY_HIGH",
                "implementation_difficulty": "LOW",
                "priority": "URGENT",
                "justification": "Redução de no-show com lembretes T-24h/T-6h nativos em Python e qualificação imediata de agendamentos.",
            },
            {
                "segment": "Pequenas e Médias Empresas (PMEs)",
                "identified_problem": "Falta de visibilidade financeira consolidada, processos dependentes do dono e ausência de funil comercial estruturado.",
                "recommended_service_code": "SRV_01_DIAGNOSTICO",
                "recommended_service_name": "SERVIÇO 01 — Diagnóstico de Automação e Inteligência Artificial",
                "ideal_customer_profile": "PMEs com faturamento entre R$ 50 mil e R$ 500 mil/mês buscando eficiência",
                "commercial_potential": "HIGH",
                "implementation_difficulty": "LOW",
                "priority": "HIGH",
                "justification": "Porta de entrada de baixo atrito comercial que converte naturalmente para projetos de automação e dashboards.",
            },
            {
                "segment": "E-commerce",
                "identified_problem": "Alto custo de aquisição em anúncios pagos, baixo tráfego orgânico SEO em páginas de categoria e abandono de carrinho.",
                "recommended_service_code": "SRV_05_MARKETING_IA",
                "recommended_service_name": "SERVIÇO 05 — Infraestrutura de Marketing e Conteúdo com IA",
                "ideal_customer_profile": "Lojas virtuais de nicho e marcas D2C buscando reduzir CAC",
                "commercial_potential": "HIGH",
                "implementation_difficulty": "MEDIUM",
                "priority": "HIGH",
                "justification": "A combinação de SEO técnico automatizado + Content Factory reduz a dependência de mídia paga.",
            },
            {
                "segment": "Serviços Profissionais",
                "identified_problem": "Propostas comerciais feitas manualmente em horas, falta de presença em redes B2B (LinkedIn) e pipeline imprevisível.",
                "recommended_service_code": "SRV_06_CRM_COMERCIAL",
                "recommended_service_name": "SERVIÇO 06 — CRM Inteligente e Automação Comercial",
                "ideal_customer_profile": "Consultorias, engenharias, arquiteturas, corretoras e agências B2B",
                "commercial_potential": "HIGH",
                "implementation_difficulty": "LOW",
                "priority": "MEDIUM",
                "justification": "O gerador de propostas e o funil estruturado aceleram o fechamento de contratos consultivos.",
            },
            {
                "segment": "Empresas de Tecnologia",
                "identified_problem": "Backlog de desenvolvimento travado em demandas internas, necessidade de dashboards executivos e integrações customizadas.",
                "recommended_service_code": "SRV_07_SISTEMAS_SOB_MEDIDA",
                "recommended_service_name": "SERVIÇO 07 — Sistemas Empresariais e Plataformas Sob Medida",
                "ideal_customer_profile": "Software houses, SaaS em crescimento e departamentos de TI corporativos",
                "commercial_potential": "VERY_HIGH",
                "implementation_difficulty": "HIGH",
                "priority": "HIGH",
                "justification": "Contratos de maior valor agregado para desenvolvimento de módulos específicos, portais e motores de IA.",
            },
        ]
        for opp in opportunities_seed:
            db.add(
                MarketOpportunity(
                    tenant_id=tenant.id,
                    business_unit_code="UNION_TECH",
                    segment=opp["segment"],
                    identified_problem=opp["identified_problem"],
                    recommended_service_code=opp["recommended_service_code"],
                    recommended_service_name=opp["recommended_service_name"],
                    ideal_customer_profile=opp["ideal_customer_profile"],
                    commercial_potential=opp["commercial_potential"],
                    implementation_difficulty=opp["implementation_difficulty"],
                    priority=opp["priority"],
                    justification=opp["justification"],
                    information_source="Análise Setorial Determinística + Mapeamento de Gargalos Operacionais B2B",
                    researched_at=today_str,
                    data_origin="REAL",
                )
            )
        db.commit()

    # 5. LANDING PAGES COMERCIAIS INDEPENDENTES (UNION TECH + 6 ESPECÍFICAS + AGENCY + PARTNERS)
    landing_pages_seed = [
        {
            "business_unit_code": "UNION_TECH",
            "slug": "union-tech",
            "title": "UNION TECH — Inteligência Artificial, Agentes e Automação Empresarial",
            "value_proposition": "Transformamos operações manuais em sistemas autônomos, inteligentes e auditáveis em Python.",
            "problem_statement": "Sua equipe perde horas todos os dias copiando dados entre planilhas, demorando para responder leads e tomando decisões sem indicadores claros.",
            "solution_summary": "Projetamos e implantamos Agentes de IA, Automações Nativas, CRMs Inteligentes e Sistemas Sob Medida na sua infraestrutura.",
            "benefits": [
                "Arquitetura 100% própria em Python sem dependência de n8n ou mensalidades ocultas",
                "Integração direta com seus sistemas atuais e banco de dados PostgreSQL",
                "Retorno sobre investimento (ROI) mapeado antes do início do projeto",
            ],
            "real_example_description": "Demonstração Real: O próprio UNION GROWTH OS opera 11 agentes coordenados, 20 rotinas automatizadas no APScheduler e CRM com Lead Scoring em produção contínua.",
            "differentials": ["Código proprietário auditável", "Segurança e conformidade LGPD nativa", "Acompanhamento executivo"],
            "cta_text": "Solicitar Diagnóstico de Automação",
        },
        {
            "business_unit_code": "UNION_TECH",
            "slug": "agentes-ia",
            "title": "Agentes de IA para Atendimento, Triagem Comercial e Processos",
            "value_proposition": "Atendimento técnico e qualificação comercial imediata 24 horas por dia com governança e supervisão.",
            "problem_statement": "Leads esfriam quando aguardam horas por uma resposta comercial, enquanto sua equipe gasta tempo respondendo sempre as mesmas dúvidas.",
            "solution_summary": "Implantamos Agentes de IA conectados à base de conhecimento real da sua empresa, com regras determinísticas e escalonamento para humanos.",
            "benefits": ["Qualificação imediata 24/7", "Zero invenção de preços ou promessas", "Integração direta ao pipeline do CRM"],
            "real_example_description": "Demonstração Real: Orquestrador multiagente com controle de nível de autonomia (Níveis 1, 2 e 3) e trava para ações críticas.",
            "differentials": ["Arquitetura híbrida determinística + LLM", "Controle de custos de tokens", "Logs completos de auditoria"],
            "cta_text": "Quero um Agente de IA na Minha Empresa",
        },
        {
            "business_unit_code": "UNION_TECH",
            "slug": "automacao-empresarial",
            "title": "Automação Empresarial e Integração de Sistemas em Python",
            "value_proposition": "Elimine tarefas repetitivas, retrabalho manual e falhas operacionais com automações nativas 24/7.",
            "problem_statement": "Processos financeiros, alertas de vencimento, sincronização de cadastros e relatórios feitos manualmente geram erros e custos invisíveis.",
            "solution_summary": "Desenvolvemos rotinas automatizadas com APScheduler, controle de idempotência, retentativa automática (backoff) e alertas em tempo real.",
            "benefits": ["Zero dependência de n8n ou Zapier", "Idempotência garantida contra duplicidades", "Monitoramento de heartbeats 24/7"],
            "real_example_description": "Demonstração Real: Motor de automação executando rotinas diárias das 07:00 às 19:00 com recuperação automática pós-restart.",
            "differentials": ["100% nativo em Python 3.12", "Persistência em PostgreSQL 16", "Sem cobrança por tarefa executada"],
            "cta_text": "Mapear Processos para Automatizar",
        },
        {
            "business_unit_code": "UNION_TECH",
            "slug": "consultoria-ia",
            "title": "Diagnóstico e Consultoria de Transformação Digital & IA",
            "value_proposition": "Saiba exatamente onde aplicar Inteligência Artificial e Automação para reduzir custos e escalar vendas.",
            "problem_statement": "Muitas empresas querem adotar IA, mas correm o risco de gastar em ferramentas desconexas que não trazem resultado financeiro.",
            "solution_summary": "Executamos um diagnóstico técnico de 7 dias mapeando processos, gargalos, arquitetura de dados e cronograma de implantação.",
            "benefits": ["Mapa claro de prioridades", "Orçamento previsível e transparente", "Plano prático sem jargões vazios"],
            "real_example_description": "Demonstração Real: Calculadora transparente de escopo técnico, custos de infraestrutura e margem operacional.",
            "differentials": ["Visão executiva e de engenharia combinadas", "Foco em redução real de custos", "Entrega de plano acionável"],
            "cta_text": "Agendar Diagnóstico Técnico",
        },
        {
            "business_unit_code": "UNION_TECH",
            "slug": "crm-inteligente",
            "title": "CRM Inteligente, Lead Scoring e Automação de Propostas",
            "value_proposition": "Organize todos os seus leads, priorize oportunidades quentes e gere propostas comerciais em segundos.",
            "problem_statement": "Vendedores perdem negócios porque esquecem de fazer follow-up ou demoram dias para enviar uma proposta comercial formal.",
            "solution_summary": "CRM completo com funil de 10 etapas, deduplicação automática, pontuação de leads (0 a 100) e gerador de propostas em PDF/HTML.",
            "benefits": ["Funil visual de Visitante a Pós-Venda", "Gerador de propostas com aprovação do diretor", "Conformidade LGPD nativa com opt-out"],
            "real_example_description": "Demonstração Real: Módulo CRM & Propostas operando nativamente no UNION GROWTH OS.",
            "differentials": ["Deduplicação inteligente por e-mail", "Forecast ponderado de receita", "Sem mensalidade por assento de vendedor"],
            "cta_text": "Implantar CRM Inteligente",
        },
        {
            "business_unit_code": "UNION_TECH",
            "slug": "marketing-automatizado",
            "title": "Infraestrutura de Marketing Automatizado, SEO e Content Factory",
            "value_proposition": "Transforme seu marketing em uma linha de produção contínua de conteúdo, tráfego orgânico e leads.",
            "problem_statement": "Manter redes sociais atualizadas, publicar artigos otimizados para o Google e monitorar concorrentes manualmente exige uma equipe cara.",
            "solution_summary": "Implantamos sua própria Content Factory 30D integrada a auditorias técnicas de SEO, Core Web Vitals e calendário editorial.",
            "benefits": ["Geração em lote de 30 peças mensais", "Auditoria real de SEO e Schema.org", "Pacote de publicação assistida com 1 clique"],
            "real_example_description": "Demonstração Real: Content Factory produzindo peças para Instagram, LinkedIn, TikTok, YouTube, Blog e E-mail.",
            "differentials": ["Anti-duplicação semântica por hash", "Artes geradas programaticamente em PNG", "Integração direta com funil de vendas"],
            "cta_text": "Ativar Marketing Automatizado",
        },
        {
            "business_unit_code": "UNION_TECH",
            "slug": "sistemas-sob-medida",
            "title": "Desenvolvimento de Sistemas Empresariais e Plataformas Web Sob Medida",
            "value_proposition": "Softwares corporativos de alta performance construídos sob medida para a operação da sua empresa.",
            "problem_statement": "Sistemas engessados limitam o crescimento da sua empresa e cobram caro por cada adaptação ou novo usuário.",
            "solution_summary": "Desenvolvimento Full-Stack com Python (FastAPI), Next.js, PostgreSQL e Docker, implantado em nuvem dedicada com CI/CD e backups.",
            "benefits": ["Arquitetura multi-tenant escalável", "Painéis rápidos e modernos", "Implantação automatizada com HTTPS Let's Encrypt"],
            "real_example_description": "Demonstração Real: Plataforma UNION GROWTH OS com 33+ testes automatizados, backup com verificação em memória e deploy contínuo.",
            "differentials": ["Testes automatizados de ponta a ponta", "Segurança JWT + Bcrypt + Rate Limiting", "Código limpo e documentado"],
            "cta_text": "Solicitar Orçamento de Sistema Sob Medida",
        },
        {
            "business_unit_code": "UNION_AGENCY",
            "slug": "union-agency",
            "title": "UNION AGENCY — Assessoria de Marketing, SEO e Growth Impulsionada por IA",
            "value_proposition": "Sua empresa atendida por uma operação completa de marketing, SEO, conteúdo e inteligência comercial.",
            "problem_statement": "Agências tradicionais entregam apenas posts soltos sem conexão com SEO, geração de leads ou retorno financeiro.",
            "solution_summary": "Planos mensais (Starter, Pro, Business e Enterprise) com conta isolada, calendário de 30 dias, SEO técnico e relatórios transparentes.",
            "benefits": ["Conta multi-tenant 100% isolada", "Calendário editorial completo", "Foco em geração de leads e autoridade orgânica"],
            "real_example_description": "Demonstração Real: Gestão multiempresa com isolamento estrito de dados, campanhas e conteúdos.",
            "differentials": ["Transparência total entre dados reais e metas", "Execução diária disciplinada", "Planos escaláveis"],
            "cta_text": "Conhecer Planos da UNION AGENCY",
        },
        {
            "business_unit_code": "UNION_PARTNERS",
            "slug": "union-partners",
            "title": "UNION PARTNERS — Curadoria Técnica, Comparativos e Parcerias Oficiais",
            "value_proposition": "Recomendações técnicas imparciais, comparativos de ferramentas e ofertas verificadas nas maiores plataformas.",
            "problem_statement": "Comprar equipamentos de tecnologia, infraestrutura ou ferramentas digitais sem análise técnica leva a escolhas erradas.",
            "solution_summary": "Analisamos especificações, preços observados e custo-benefício em programas oficiais (Mercado Livre, Amazon, Shopee e SaaS).",
            "benefits": ["Links oficiais verificados", "Transparência total de divulgação publicitária", "Comparativos técnicos objetivos"],
            "real_example_description": "Demonstração Real: Sistema próprio de rastreamento de cliques e conciliação auditável de comissões.",
            "differentials": ["Identificação clara de links de afiliado", "Verificação de disponibilidade e fonte", "Foco em utilidade real para o comprador"],
            "cta_text": "Ver Curadoria de Produtos & Parcerias",
        },
    ]

    for lp in landing_pages_seed:
        existing_lp = (
            db.query(LandingPage)
            .filter(LandingPage.tenant_id == tenant.id, LandingPage.slug == lp["slug"])
            .first()
        )
        if not existing_lp:
            db.add(
                LandingPage(
                    tenant_id=tenant.id,
                    business_unit_code=lp["business_unit_code"],
                    slug=lp["slug"],
                    title=lp["title"],
                    value_proposition=lp["value_proposition"],
                    problem_statement=lp["problem_statement"],
                    solution_summary=lp["solution_summary"],
                    benefits_json=json.dumps(lp["benefits"], ensure_ascii=False),
                    real_example_description=lp["real_example_description"],
                    differentials_json=json.dumps(lp["differentials"], ensure_ascii=False),
                    cta_text=lp["cta_text"],
                    is_published=True,
                    data_origin="REAL",
                )
            )
    db.commit()

    # 6. PROGRAMAS DE AFILIADOS E PRODUTOS INICIAIS (UNION PARTNERS)
    programs_seed = [
        {
            "name": "Programa de Afiliados Mercado Livre Oficial",
            "platform": "mercado_livre",
            "approval_status": "PENDING_CREDENTIALS",
            "credentials_status": "PENDING_CREDENTIALS",
            "rules_summary": "Proibido alterar preços divulgados; obrigatório usar link curto/oficial gerado na central de afiliados do Mercado Livre.",
            "default_commission_pct": 8.0,
            "attribution_window_days": 7,
            "payment_conditions": "Pagamento oficial após confirmação de entrega e prazo de devolução.",
            "limitations": "API pública de leitura de itens disponível; geração de link com tag de afiliado requer conta aprovada no programa social/afiliados ML.",
            "official_api_status": "API Pública de Catálogo Ativa / Credencial de Afiliado Pendente",
        },
        {
            "name": "Programa de Associados Amazon Brasil",
            "platform": "amazon",
            "approval_status": "PENDING_CREDENTIALS",
            "credentials_status": "PENDING_CREDENTIALS",
            "rules_summary": "Obrigatório exibir aviso de Associado Amazon; proibido armazenar preços fixos sem data/hora da consulta.",
            "default_commission_pct": 9.0,
            "attribution_window_days": 1,
            "payment_conditions": "Pagamento mensal via transferência bancária (aprox. 60 dias após o fim do mês da venda enviada).",
            "limitations": "Product Advertising API 5.0 exige conta de Associado validada com vendas qualificadas e chaves PA-API.",
            "official_api_status": "PENDING_CREDENTIALS (Requer Associate Tag + PA-API Keys)",
        },
        {
            "name": "Programa de Afiliados Shopee Brasil",
            "platform": "shopee",
            "approval_status": "PENDING_CREDENTIALS",
            "credentials_status": "PENDING_CREDENTIALS",
            "rules_summary": "Uso exclusivo de links rastreáveis oficiais; vedado bidding em marcas registradas Shopee.",
            "default_commission_pct": 7.5,
            "attribution_window_days": 7,
            "payment_conditions": "Repasse após validação do pedido concluído sem disputa.",
            "limitations": "Open API de Afiliados Shopee requer App ID e Secret aprovados no painel Shopee Affiliate.",
            "official_api_status": "PENDING_CREDENTIALS (Requer Shopee Affiliate App ID & Secret)",
        },
        {
            "name": "Programas de Afiliados de Ferramentas Digitais & Cloud",
            "platform": "digital_tools",
            "approval_status": "PENDING_CREDENTIALS",
            "credentials_status": "PENDING_CREDENTIALS",
            "rules_summary": "Indicação transparente de plataformas de hospedagem, infraestrutura cloud, domínios e produtividade B2B.",
            "default_commission_pct": 20.0,
            "attribution_window_days": 30,
            "payment_conditions": "Comissão por assinatura confirmada após período de garantia (30 a 60 dias).",
            "limitations": "Conciliação via painel do parceiro ou webhook de pós-conversão.",
            "official_api_status": "Rastreamento por UTM/Link + Conciliação Manual ou Webhook",
        },
        {
            "name": "Parcerias Comerciais de Serviços de Tecnologia",
            "platform": "tech_partners",
            "approval_status": "APPROVED",
            "credentials_status": "INTERNAL_TRACKING_ACTIVE",
            "rules_summary": "Parcerias B2B de indicação cruzada (referral fee) com consultorias, contabilidades e integradores.",
            "default_commission_pct": 10.0,
            "attribution_window_days": 90,
            "payment_conditions": "Comissão paga proporcionalmente ao recebimento efetivo da fatura do cliente indicado.",
            "limitations": "Exige registro formal da indicação e contrato pago pelo cliente.",
            "official_api_status": "Rastreamento Interno Ativo no CRM & Financeiro",
        },
    ]

    for prog in programs_seed:
        existing_prog = (
            db.query(AffiliateProgram)
            .filter(AffiliateProgram.tenant_id == tenant.id, AffiliateProgram.platform == prog["platform"])
            .first()
        )
        if not existing_prog:
            db.add(
                AffiliateProgram(
                    tenant_id=tenant.id,
                    business_unit_code="UNION_PARTNERS",
                    name=prog["name"],
                    platform=prog["platform"],
                    approval_status=prog["approval_status"],
                    credentials_status=prog["credentials_status"],
                    rules_summary=prog["rules_summary"],
                    default_commission_pct=prog["default_commission_pct"],
                    attribution_window_days=prog["attribution_window_days"],
                    payment_conditions=prog["payment_conditions"],
                    limitations=prog["limitations"],
                    official_api_status=prog["official_api_status"],
                    data_origin="REAL",
                )
            )
    db.commit()

    # 7. ROTINAS DE AUTOMAÇÃO COMERCIAL 24/7 (SEÇÃO 13: 07:00 ÀS 19:00 AMERICA/SAO_PAULO)
    commercial_schedule_specs = [
        ("p17_0700_market_research", "07:00 — Pesquisa Diária de Oportunidades Comerciais (UNION TECH)", "0 7 * * *", "07:00", "AGENT_09_COMPETITIVE", "research_commercial_opportunities", "UNION_TECH"),
        ("p17_0800_ceo_multibusiness", "08:00 — CEO Daily Briefing Consolidado Multinegócio", "0 8 * * *", "08:00", "AGENT_01_CEO", "generate_multibusiness_briefing", "ALL"),
        ("p17_0900_commercial_plan", "09:00 — Planejamento Comercial e Metas das 3 Unidades", "0 9 * * *", "09:00", "AGENT_02_CMO", "plan_multibusiness_campaigns", "ALL"),
        ("p17_1000_content_generation", "10:00 — Geração de Conteúdo por Unidade (Tech, Agency, Partners)", "0 10 * * *", "10:00", "AGENT_06_COPYWRITER", "generate_unit_contents", "ALL"),
        ("p17_1100_publish_queue_check", "11:00 — Verificação da Fila de Publicação e Pacotes Assistidos", "0 11 * * *", "11:00", "AGENT_04_SOCIAL", "verify_publishing_queue", "ALL"),
        ("p17_1200_lead_qualification", "12:00 — Qualificação e Lead Scoring de Leads Autorizados", "0 12 * * *", "12:00", "AGENT_08_SALES", "qualify_authorized_leads", "UNION_TECH"),
        ("p17_1400_seo_research", "14:00 — Pesquisa SEO e Monitoramento de Páginas Comerciais", "0 14 * * *", "14:00", "AGENT_03_SEO", "audit_commercial_landing_pages", "UNION_TECH"),
        ("p17_1500_competitive_analysis", "15:00 — Análise Competitiva e Curadoria de Ofertas", "0 15 * * *", "15:00", "AGENT_09_COMPETITIVE", "analyze_market_and_affiliates", "UNION_PARTNERS"),
        ("p17_1600_deals_followup", "16:00 — Acompanhamento de Negociações e Propostas Pendentes", "0 16 * * *", "16:00", "AGENT_08_SALES", "followup_open_proposals_and_deals", "UNION_TECH"),
        ("p17_1700_campaigns_analysis", "17:00 — Análise de Campanhas de Clientes e Conversão", "0 17 * * *", "17:00", "AGENT_07_GROWTH", "evaluate_unit_conversion_funnels", "UNION_AGENCY"),
        ("p17_1800_financial_report", "18:00 — Relatório Financeiro e Conciliação por Unidade", "0 18 * * *", "18:00", "AGENT_10_FINANCE", "consolidate_multibusiness_finance", "ALL"),
        ("p17_1900_commercial_summary", "19:00 — Relatório Comercial Consolidado de Fim de Dia", "0 19 * * *", "19:00", "AGENT_01_CEO", "compile_end_of_day_commercial_report", "ALL"),
    ]

    for code_key, name, cron_expr, sched_time, agent_id, task_name, unit_code in commercial_schedule_specs:
        existing_rule = (
            db.query(AutomationRule)
            .filter(AutomationRule.tenant_id == tenant.id, AutomationRule.code_key == code_key)
            .first()
        )
        if not existing_rule:
            db.add(
                AutomationRule(
                    tenant_id=tenant.id,
                    name=name,
                    code_key=code_key,
                    trigger_type="CRON",
                    cron_expression=cron_expr,
                    action_agent=agent_id,
                    action_task=task_name,
                    frequency_label="Diário (America/Sao_Paulo)",
                    scheduled_time=sched_time,
                    priority="HIGH",
                    owner_role="AI CEO & Commercial Director",
                    business_unit_code=unit_code,
                    is_active=True,
                    max_retries=3,
                    timeout_seconds=60,
                    last_status="READY",
                )
            )
    db.commit()

    return {
        "units_count": db.query(BusinessUnit).filter(BusinessUnit.tenant_id == tenant.id).count(),
        "services_count": db.query(ProductService).filter(ProductService.tenant_id == tenant.id).count(),
        "offers_count": db.query(CommercialOffer).filter(CommercialOffer.tenant_id == tenant.id).count(),
        "opportunities_count": db.query(MarketOpportunity).filter(MarketOpportunity.tenant_id == tenant.id).count(),
        "landing_pages_count": db.query(LandingPage).filter(LandingPage.tenant_id == tenant.id).count(),
        "affiliate_programs_count": db.query(AffiliateProgram).filter(AffiliateProgram.tenant_id == tenant.id).count(),
    }


def update_product_service_pricing(
    db: Session,
    tenant_id: int,
    service_id: int,
    payload: Any,
) -> dict[str, Any]:
    """
    Atualiza os parâmetros de custo/margem de um serviço e permite aprovação pelo proprietário.
    Protege preços já aprovados anteriormente: não sobrescreve sem autorização explícita (owner_approve_pricing ou force_owner_override).
    """
    svc = (
        db.query(ProductService)
        .filter(ProductService.tenant_id == tenant_id, ProductService.id == service_id)
        .first()
    )
    if not svc:
        raise ValueError(f"Serviço #{service_id} não encontrado para este tenant.")

    if svc.pricing_approved_by_owner and not (
        payload.owner_approve_pricing or getattr(payload, "force_owner_override", False)
    ):
        raise PermissionError(
            "Governança de Preços: Este serviço já possui preço aprovado pelo proprietário. "
            "Para alterar um preço já aprovado, informe owner_approve_pricing=True ou force_owner_override=True."
        )

    if payload.dev_hours_estimated is not None:
        svc.dev_hours_estimated = payload.dev_hours_estimated
    if payload.complexity_level is not None:
        svc.complexity_level = payload.complexity_level
    if payload.hourly_rate_brl is not None:
        svc.hourly_rate_brl = payload.hourly_rate_brl
    if payload.infra_cost_brl is not None:
        svc.infra_cost_brl = payload.infra_cost_brl
    if payload.tools_api_cost_brl is not None:
        svc.tools_api_cost_brl = payload.tools_api_cost_brl
    if payload.support_cost_brl is not None:
        svc.support_cost_brl = payload.support_cost_brl
    if payload.tax_rate_pct is not None:
        svc.tax_rate_pct = payload.tax_rate_pct
    if payload.target_margin_pct is not None:
        svc.target_margin_pct = payload.target_margin_pct
    if payload.commercial_terms is not None:
        svc.commercial_terms = payload.commercial_terms

    calc = calculate_service_pricing(
        dev_hours=svc.dev_hours_estimated,
        complexity=svc.complexity_level,
        hourly_rate=svc.hourly_rate_brl,
        infra_cost=svc.infra_cost_brl,
        tools_api_cost=svc.tools_api_cost_brl,
        support_cost=svc.support_cost_brl,
        tax_rate_pct=svc.tax_rate_pct,
        target_margin_pct=svc.target_margin_pct,
    )
    svc.estimated_cost_brl = calc["estimated_cost_brl"]
    svc.suggested_price_brl = calc["suggested_price_brl"]

    if payload.configured_price_brl is not None:
        svc.configured_price_brl = payload.configured_price_brl
        net_after_tax = svc.configured_price_brl * (1.0 - svc.tax_rate_pct / 100.0)
        svc.estimated_margin_pct = round(
            ((net_after_tax - svc.estimated_cost_brl) / max(1.0, svc.configured_price_brl)) * 100.0, 2
        )
    else:
        svc.configured_price_brl = calc["suggested_price_brl"]
        svc.estimated_margin_pct = calc["estimated_margin_pct"]

    if payload.recurring_monthly_brl is not None:
        svc.recurring_monthly_brl = payload.recurring_monthly_brl

    if payload.owner_approve_pricing:
        svc.pricing_approved_by_owner = True

    db.commit()
    db.refresh(svc)
    return serialize_product_service(svc)


def serialize_product_service(svc: ProductService) -> dict[str, Any]:
    reqs = json.loads(getattr(svc, "client_requirements_json", "[]") or "[]")
    if not reqs:
        reqs = [
            "Ponto focal responsável para validação de regras de negócio",
            "Credenciais/acessos de homologação aos sistemas que serão integrados",
        ]
    direct_cost = getattr(svc, "direct_cost_brl", 0.0) or svc.estimated_cost_brl
    indirect_cost = getattr(svc, "indirect_cost_brl", 0.0) or round(svc.support_cost_brl * 0.5, 2)
    scope_inc = json.loads(getattr(svc, "scope_included_json", "[]") or "[]") or json.loads(svc.deliverables_json or "[]")
    scope_exc = json.loads(getattr(svc, "scope_excluded_json", "[]") or "[]") or [
        "Custos de APIs pagas de terceiros ou verba de tráfego pago",
        "Desenvolvimento de módulos fora da especificação técnica aprovada",
    ]
    return {
        "id": svc.id,
        "business_unit_code": svc.business_unit_code,
        "service_code": svc.service_code,
        "name": svc.name,
        "category": svc.category,
        "description": svc.description,
        "problem_solved": svc.problem_solved,
        "target_audience": svc.target_audience,
        "benefits": json.loads(svc.benefits_json or "[]"),
        "scope_summary": svc.scope_summary,
        "scope_included": scope_inc,
        "scope_excluded": scope_exc,
        "deliverables": json.loads(svc.deliverables_json or "[]"),
        "estimated_timeline_days": svc.estimated_timeline_days,
        "client_requirements": reqs,
        "billing_model": getattr(svc, "billing_model", "SETUP_PLUS_MRR" if svc.recurring_monthly_brl > 0 else "SETUP_ONLY"),
        "recurrence_eligible": bool(getattr(svc, "recurrence_eligible", True)),
        "scope_limits": getattr(
            svc,
            "scope_limits",
            "Escopo restrito aos entregáveis listados; integrações ou módulos adicionais sob orçamento complementar.",
        ),
        "approval_criteria": getattr(
            svc,
            "approval_criteria",
            "Validação de escopo técnico, margem mínima >= 30% e aprovação expressa do proprietário.",
        ),
        "pricing_calculator": {
            "dev_hours_estimated": svc.dev_hours_estimated,
            "complexity_level": svc.complexity_level,
            "hourly_rate_brl": svc.hourly_rate_brl,
            "direct_cost_brl": direct_cost,
            "indirect_cost_brl": indirect_cost,
            "infra_cost_brl": svc.infra_cost_brl,
            "tools_api_cost_brl": svc.tools_api_cost_brl,
            "support_cost_brl": svc.support_cost_brl,
            "tax_rate_pct": svc.tax_rate_pct,
            "minimum_margin_pct": getattr(svc, "minimum_margin_pct", 30.0),
            "target_margin_pct": svc.target_margin_pct,
            "estimated_cost_brl": svc.estimated_cost_brl,
            "suggested_price_brl": svc.suggested_price_brl,
            "price_recommendation_label": "SUGESTÃO DA CALCULADORA — SUJEITO A REVISÃO E APROVAÇÃO DO PROPRIETÁRIO",
            "configured_price_brl": svc.configured_price_brl,
            "recurring_monthly_brl": svc.recurring_monthly_brl,
            "estimated_margin_pct": svc.estimated_margin_pct,
            "pricing_approved_by_owner": svc.pricing_approved_by_owner,
        },
        "commercial_terms": svc.commercial_terms,
        "availability_status": svc.availability_status,
        "data_origin": svc.data_origin,
    }


def capture_lead_from_landing_page(
    db: Session,
    tenant_id: int,
    payload: Any,
) -> dict[str, Any]:
    """
    Captura lead de uma Landing Page comercial com:
    - Validação de consentimento e finalidade LGPD
    - Deduplicação automática por e-mail dentro de (tenant_id, business_unit_code)
    - Cálculo determinístico de Lead Score (0 a 100)
    - Atribuição de campanha e estágio no funil de 10 etapas
    """
    if not payload.consent_lgpd:
        raise ValueError("Conformidade LGPD: É necessário o consentimento explícito para captura comercial do lead.")

    lp = (
        db.query(LandingPage)
        .filter(LandingPage.tenant_id == tenant_id, LandingPage.slug == payload.landing_page_slug)
        .first()
    )
    unit_code = lp.business_unit_code if lp else "UNION_TECH"

    from app.core.security import sanitize_text

    clean_email = sanitize_text(payload.email.strip().lower())
    clean_name = sanitize_text(payload.full_name.strip())
    clean_phone = sanitize_text(payload.phone.strip())
    clean_company = sanitize_text(payload.company_name.strip())
    clean_purpose = sanitize_text(getattr(payload, "purpose_description", "") or "Atendimento comercial e envio de proposta solicitada")
    clean_utm = sanitize_text(getattr(payload, "utm_campaign", "") or "")
    clean_notes = sanitize_text(getattr(payload, "notes", "") or "")

    existing_lead = (
        db.query(CRMLead)
        .filter(
            CRMLead.tenant_id == tenant_id,
            CRMLead.email == clean_email,
            CRMLead.business_unit_code == unit_code,
        )
        .first()
    )

    temp_lead_for_score = CRMLead(
        tenant_id=tenant_id,
        full_name=clean_name,
        email=clean_email,
        phone=clean_phone,
        company_name=clean_company,
        source_channel=f"LandingPage:{payload.landing_page_slug}",
        buy_intent=payload.buy_intent,
        estimated_value=payload.estimated_value,
        consent_lgpd=True,
    )
    score, qual_status = compute_lead_score(temp_lead_for_score)
    funnel_stg = "QUALIFICADO" if score >= 65 else "LEAD"

    if existing_lead:
        if existing_lead.opt_out or existing_lead.contact_blocked:
            raise ValueError("Este contato solicitou opt-out ou bloqueio de comunicações comerciais (LGPD).")
        existing_lead.full_name = clean_name or existing_lead.full_name
        existing_lead.phone = clean_phone or existing_lead.phone
        existing_lead.company_name = clean_company or existing_lead.company_name
        existing_lead.buy_intent = payload.buy_intent
        existing_lead.estimated_value = max(existing_lead.estimated_value, payload.estimated_value)
        existing_lead.lead_score = max(existing_lead.lead_score, score)
        existing_lead.last_contact_at = datetime.now(timezone.utc)
        if clean_utm:
            existing_lead.campaign_attribution = clean_utm
        db.commit()
        db.refresh(existing_lead)
        return {
            "deduplicated": True,
            "lead_id": existing_lead.id,
            "business_unit_code": existing_lead.business_unit_code,
            "lead_score": existing_lead.lead_score,
            "qualification_status": existing_lead.qualification_status,
            "funnel_stage": existing_lead.funnel_stage,
            "legal_basis": existing_lead.legal_basis,
            "data_origin": existing_lead.data_origin,
        }

    new_lead = CRMLead(
        tenant_id=tenant_id,
        full_name=clean_name,
        email=clean_email,
        phone=clean_phone,
        company_name=clean_company,
        source_channel=f"LandingPage:{payload.landing_page_slug}",
        buy_intent=payload.buy_intent,
        lead_score=score,
        qualification_status=qual_status,
        pipeline_stage="QUALIFICATION" if score >= 65 else "NEW_LEAD",
        funnel_stage=funnel_stg,
        estimated_value=payload.estimated_value,
        business_unit_code=unit_code,
        consent_lgpd=True,
        consent_source=f"Landing Page /{payload.landing_page_slug}",
        legal_basis="CONSENTIMENTO_OPT_IN_E_PROCEDIMENTO_PRELIMINAR_CONTRATUAL",
        purpose_description=clean_purpose,
        campaign_attribution=clean_utm,
        opt_out=False,
        contact_blocked=False,
        notes=clean_notes,
        data_origin=payload.data_origin,
    )
    db.add(new_lead)
    if lp:
        lp.leads_captured_count = (lp.leads_captured_count or 0) + 1
    db.commit()
    db.refresh(new_lead)

    db.add(
        CRMActivity(
            tenant_id=tenant_id,
            lead_id=new_lead.id,
            activity_type="FOLLOW_UP",
            subject=f"[{unit_code}] Triagem Comercial — Lead capturado via /{payload.landing_page_slug}",
            description=f"Score={score}. Finalidade LGPD: {new_lead.purpose_description}. Aguardando revisão/diagnóstico.",
            due_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            completed=False,
        )
    )
    db.commit()

    return {
        "deduplicated": False,
        "lead_id": new_lead.id,
        "business_unit_code": new_lead.business_unit_code,
        "lead_score": new_lead.lead_score,
        "qualification_status": new_lead.qualification_status,
        "funnel_stage": new_lead.funnel_stage,
        "legal_basis": new_lead.legal_basis,
        "data_origin": new_lead.data_origin,
    }


def create_commercial_proposal_service(
    db: Session,
    tenant: Tenant,
    payload: Any,
) -> dict[str, Any]:
    """
    Gera uma proposta comercial completa vinculada a um serviço e cliente.
    Nasce com status DRAFT ou PENDING_APPROVAL e owner_approved=False (nunca envia proposta vinculante sem aprovação).
    """
    svc = (
        db.query(ProductService)
        .filter(ProductService.tenant_id == tenant.id, ProductService.service_code == payload.service_code)
        .first()
    )

    deliverables = payload.deliverables
    if not deliverables and svc:
        deliverables = json.loads(svc.deliverables_json or "[]")
    if not deliverables:
        deliverables = [
            "Mapeamento técnico e arquitetura da solução",
            "Desenvolvimento, configuração e testes integrados",
            "Implantação assistida e treinamento operacional",
        ]

    timeline = payload.timeline_schedule
    if not timeline:
        days = svc.estimated_timeline_days if svc else 15
        timeline = [
            "Etapa 1 (Dias 1 a 3): Kickoff, acessos e especificação detalhada",
            f"Etapa 2 (Dias 4 a {max(5, days - 3)}): Construção, integrações e testes",
            f"Etapa 3 (Até Dia {days}): Homologação, entrada em produção e entrega",
        ]

    setup_val = payload.setup_price_brl if payload.setup_price_brl > 0 else (svc.configured_price_brl if svc else 3500.0)
    monthly_val = payload.monthly_price_brl if payload.monthly_price_brl >= 0 else (svc.recurring_monthly_brl if svc else 0.0)
    total_contract = round(setup_val + (monthly_val * 12), 2)

    proposed_sol = payload.proposed_solution or (
        svc.description if svc else "Implantação de solução tecnológica e automação personalizada UNION TECH."
    )
    scope_txt = payload.scope_details or (
        svc.scope_summary if svc else "Escopo fechado conforme entregáveis listados nesta proposta comercial."
    )

    prop_num = f"PROP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    now_iso = datetime.now(timezone.utc).isoformat()
    initial_version_history = [
        {
            "version": 1,
            "timestamp": now_iso,
            "status": "PENDING_APPROVAL",
            "setup_price_brl": setup_val,
            "monthly_price_brl": monthly_val,
            "notes": "Versão 1 gerada e submetida à revisão do proprietário.",
        }
    ]
    diag_txt = getattr(payload, "diagnosis_summary", "") or (
        f"Diagnóstico Técnico: Identificado gargalo em '{payload.identified_problem}'. Recomendada implantação de {payload.service_code}."
    )
    contract_txt = getattr(payload, "contract_terms", "") or (
        "MINUTA DE CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE TECNOLOGIA E AUTOMAÇÃO: "
        "1. Objeto restrito aos entregáveis descritos; 2. Confidencialidade (NDA) e proteção de dados (LGPD); "
        "3. Sujeito à aprovação expressa do proprietário e confirmação de pagamento."
    )
    proposal = CommercialProposal(
        tenant_id=tenant.id,
        business_unit_code=payload.business_unit_code,
        proposal_number=prop_num,
        lead_id=payload.lead_id,
        service_code=payload.service_code,
        company_issuer_name=tenant.name,
        client_name=payload.client_name,
        client_company=payload.client_company,
        client_email=payload.client_email,
        identified_problem=payload.identified_problem,
        diagnosis_summary=diag_txt,
        proposed_solution=proposed_sol,
        scope_details=scope_txt,
        deliverables_json=json.dumps(deliverables, ensure_ascii=False),
        timeline_schedule_json=json.dumps(timeline, ensure_ascii=False),
        setup_price_brl=setup_val,
        monthly_price_brl=monthly_val,
        total_contract_value_brl=total_contract,
        payment_terms=payload.payment_terms,
        validity_days=payload.validity_days,
        version_number=1,
        version_history_json=json.dumps(initial_version_history, ensure_ascii=False),
        contract_terms=contract_txt,
        contract_status="PENDING_REVIEW",
        acceptance_evidence="",
        status="PENDING_APPROVAL",
        owner_approved=False,
        data_origin=payload.data_origin,
    )
    db.add(proposal)

    if payload.lead_id:
        lead = db.query(CRMLead).filter(CRMLead.tenant_id == tenant.id, CRMLead.id == payload.lead_id).first()
        if lead:
            lead.funnel_stage = "PROPOSTA"
            lead.pipeline_stage = "PROPOSAL"

    # Registrar solicitação de aprovação humana para envio vinculante
    db.add(
        ApprovalRequest(
            tenant_id=tenant.id,
            agent_id="AGENT_08_SALES",
            action_type="COMMERCIAL_PROPOSAL_BINDING_SEND",
            title=f"Aprovar proposta comercial {prop_num} para {payload.client_company} (R$ {setup_val:,.2f})",
            payload_json=json.dumps(
                {
                    "proposal_number": prop_num,
                    "client_company": payload.client_company,
                    "setup_price_brl": setup_val,
                    "monthly_price_brl": monthly_val,
                },
                ensure_ascii=False,
            ),
            autonomy_level_at_creation=tenant.autonomy_default_level,
            is_high_impact=True,
            status="PENDING",
        )
    )
    db.commit()
    db.refresh(proposal)
    return serialize_proposal(proposal)


def update_proposal_status_service(
    db: Session,
    tenant_id: int,
    user_id: int,
    proposal_id: int,
    payload: Any,
) -> dict[str, Any]:
    """
    Atualiza o status da proposta comercial respeitando a trava:
    - Não envia proposta vinculante (SENT) nem aceita contrato (ACCEPTED) sem aprovação do proprietário.
    - Quando ACCEPTED com aprovação, cria/atualiza o CRMDeal (CLOSED_WON) e registra receita confirmada.
    """
    prop = (
        db.query(CommercialProposal)
        .filter(CommercialProposal.tenant_id == tenant_id, CommercialProposal.id == proposal_id)
        .first()
    )
    if not prop:
        raise ValueError(f"Proposta #{proposal_id} não encontrada.")

    if payload.owner_approve:
        prop.owner_approved = True
        prop.approved_by_user_id = user_id
        prop.approved_at = datetime.now(timezone.utc)

    target_status = payload.status.upper()
    if target_status in ("SENT", "ACCEPTED") and not prop.owner_approved:
        raise PermissionError(
            "Governança Comercial: Não é permitido enviar proposta vinculante (SENT) ou fechar contrato (ACCEPTED) "
            "sem aprovação expressa do proprietário (owner_approve=True)."
        )

    prop.status = target_status
    prop.version_number = (getattr(prop, "version_number", 1) or 1) + 1
    history = json.loads(getattr(prop, "version_history_json", "[]") or "[]")
    evidence_str = getattr(payload, "acceptance_evidence", "") or ""
    if evidence_str:
        prop.acceptance_evidence = evidence_str
    if prop.owner_approved and getattr(prop, "contract_status", "DRAFT") in ("DRAFT", "PENDING_REVIEW"):
        prop.contract_status = "APPROVED_BY_OWNER"
    if target_status == "ACCEPTED":
        prop.contract_status = "ACCEPTED_WITH_EVIDENCE" if prop.acceptance_evidence else "APPROVED_BY_OWNER"
    history.append(
        {
            "version": prop.version_number,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": target_status,
            "owner_approved": prop.owner_approved,
            "acceptance_evidence": prop.acceptance_evidence,
        }
    )
    prop.version_history_json = json.dumps(history, ensure_ascii=False)

    if target_status == "ACCEPTED":
        if prop.lead_id:
            lead = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id, CRMLead.id == prop.lead_id).first()
            if lead:
                lead.funnel_stage = "GANHO"
                lead.pipeline_stage = "CLOSED_WON"
                lead.qualification_status = "CONVERTED"

        existing_deal = (
            db.query(CRMDeal)
            .filter(CRMDeal.tenant_id == tenant_id, CRMDeal.proposal_id == prop.id)
            .first()
        )
        if not existing_deal:
            deal = CRMDeal(
                tenant_id=tenant_id,
                lead_id=prop.lead_id,
                title=f"[{prop.business_unit_code}] Contrato {prop.proposal_number} — {prop.client_company}",
                stage="CLOSED_WON",
                value=prop.setup_price_brl + prop.monthly_price_brl,
                probability_pct=100.0,
                expected_close_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                status="WON",
                business_unit_code=prop.business_unit_code,
                proposal_id=prop.id,
                recurring_mrr_brl=prop.monthly_price_brl,
                one_time_setup_brl=prop.setup_price_brl,
                data_origin=prop.data_origin,
            )
            db.add(deal)

        if prop.setup_price_brl > 0:
            db.add(
                FinancialRecord(
                    tenant_id=tenant_id,
                    period_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    record_type="REVENUE",
                    category=f"Venda de Serviço ({prop.service_code})",
                    channel=prop.business_unit_code,
                    amount=prop.setup_price_brl,
                    business_unit_code=prop.business_unit_code,
                    revenue_status="CONFIRMED",
                    is_recurring=False,
                    data_origin=prop.data_origin,
                    description=f"Implantação/Projeto aprovado via Proposta {prop.proposal_number} ({prop.client_company})",
                )
            )
        if prop.monthly_price_brl > 0:
            db.add(
                FinancialRecord(
                    tenant_id=tenant_id,
                    period_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    record_type="REVENUE",
                    category=f"Mensalidade Recorrente ({prop.service_code})",
                    channel=prop.business_unit_code,
                    amount=prop.monthly_price_brl,
                    business_unit_code=prop.business_unit_code,
                    revenue_status="CONFIRMED",
                    is_recurring=True,
                    data_origin=prop.data_origin,
                    description=f"MRR contratado via Proposta {prop.proposal_number} ({prop.client_company})",
                )
            )

    db.commit()
    db.refresh(prop)
    return serialize_proposal(prop)


def serialize_proposal(prop: CommercialProposal) -> dict[str, Any]:
    return {
        "id": prop.id,
        "proposal_number": prop.proposal_number,
        "business_unit_code": prop.business_unit_code,
        "lead_id": prop.lead_id,
        "service_code": prop.service_code,
        "company_issuer_name": prop.company_issuer_name,
        "client_name": prop.client_name,
        "client_company": prop.client_company,
        "client_email": prop.client_email,
        "identified_problem": prop.identified_problem,
        "proposed_solution": prop.proposed_solution,
        "scope_details": prop.scope_details,
        "deliverables": json.loads(prop.deliverables_json or "[]"),
        "timeline_schedule": json.loads(prop.timeline_schedule_json or "[]"),
        "setup_price_brl": prop.setup_price_brl,
        "monthly_price_brl": prop.monthly_price_brl,
        "total_contract_value_brl": prop.total_contract_value_brl,
        "payment_terms": prop.payment_terms,
        "validity_days": prop.validity_days,
        "conditions_and_limitations": prop.conditions_and_limitations,
        "next_steps": prop.next_steps,
        "status": prop.status,
        "owner_approved": prop.owner_approved,
        "approved_at": prop.approved_at.isoformat() if prop.approved_at else None,
        "diagnosis_summary": getattr(prop, "diagnosis_summary", ""),
        "version_number": getattr(prop, "version_number", 1),
        "version_history": json.loads(getattr(prop, "version_history_json", "[]") or "[]"),
        "contract_terms": getattr(prop, "contract_terms", ""),
        "contract_status": getattr(prop, "contract_status", "DRAFT"),
        "acceptance_evidence": getattr(prop, "acceptance_evidence", ""),
        "data_origin": prop.data_origin,
        "pdf_url": f"/api/v1/commercial/proposals/{prop.id}/pdf",
        "created_at": prop.created_at.isoformat() if prop.created_at else "",
    }


def render_public_landing_page_html(lp: LandingPage) -> str:
    benefits = json.loads(lp.benefits_json or "[]")
    differentials = json.loads(lp.differentials_json or "[]")
    benefits_html = "".join(f"<li>✓ {b}</li>" for b in benefits)
    diffs_html = "".join(f"<li>★ {d}</li>" for d in differentials)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{lp.title} — UNION GROWTH OS</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #070b14; color: #f8fafc; margin: 0; padding: 0; line-height: 1.6; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 48px 24px; }}
  .badge {{ display: inline-block; padding: 4px 12px; border-radius: 999px; background: rgba(79,70,229,0.2); border: 1px solid #4f46e5; color: #a5b4fc; font-size: 12px; font-weight: 700; letter-spacing: 0.05em; }}
  h1 {{ font-size: 34px; margin: 16px 0 12px; color: #ffffff; }}
  .subtitle {{ font-size: 18px; color: #cbd5e1; margin-bottom: 32px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; }}
  @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
  .card {{ background: #0f1629; border: 1px solid #1e293b; border-radius: 12px; padding: 24px; }}
  .card h3 {{ margin-top: 0; color: #818cf8; font-size: 16px; }}
  ul {{ list-style: none; padding: 0; margin: 0; }}
  li {{ padding: 6px 0; color: #e2e8f0; font-size: 14px; }}
  .form-card {{ background: #111827; border: 1px solid #4f46e5; border-radius: 12px; padding: 28px; }}
  input, select, textarea {{ width: 100%; box-sizing: border-box; padding: 10px 12px; margin-bottom: 12px; border-radius: 8px; border: 1px solid #334155; background: #070b14; color: #fff; font-size: 14px; }}
  button {{ width: 100%; padding: 14px; border: none; border-radius: 8px; background: #4f46e5; color: #fff; font-weight: 700; font-size: 15px; cursor: pointer; }}
  button:hover {{ background: #4338ca; }}
  .lgpd {{ font-size: 12px; color: #94a3b8; display: flex; align-items: flex-start; gap: 8px; margin-bottom: 16px; }}
  .lgpd input {{ width: auto; margin-top: 3px; }}
  #msg {{ margin-top: 12px; font-size: 14px; font-weight: 600; }}
</style>
</head>
<body>
  <div class="container">
    <span class="badge">{lp.business_unit_code} • /{lp.slug}</span>
    <h1>{lp.title}</h1>
    <div class="subtitle">{lp.value_proposition}</div>
    <div class="grid">
      <div class="card">
        <h3>O Desafio Operacional</h3>
        <p style="font-size:14px;color:#cbd5e1;">{lp.problem_statement}</p>
        <h3>Nossa Solução Técnica</h3>
        <p style="font-size:14px;color:#cbd5e1;">{lp.solution_summary}</p>
        <h3>Benefícios Comprovados</h3>
        <ul>{benefits_html}</ul>
        <h3 style="margin-top:16px;">Diferenciais</h3>
        <ul>{diffs_html}</ul>
      </div>
      <div class="form-card">
        <h3 style="margin-top:0;color:#fff;font-size:18px;">{lp.cta_text}</h3>
        <form id="lpForm">
          <input type="text" id="full_name" placeholder="Seu Nome Completo *" required />
          <input type="email" id="email" placeholder="E-mail Corporativo *" required />
          <input type="text" id="phone" placeholder="WhatsApp / Telefone *" required />
          <input type="text" id="company_name" placeholder="Empresa / Organização *" required />
          <select id="buy_intent">
            <option value="HIGH">Alta Prioridade (Implantação em até 30 dias)</option>
            <option value="URGENT">Urgente (Diagnóstico Imediato)</option>
            <option value="MEDIUM">Avaliação Técnica / Orçamento</option>
          </select>
          <label class="lgpd">
            <input type="checkbox" id="consent_lgpd" required />
            <span>Concordo com o tratamento dos dados para contato comercial conforme a LGPD. {lp.privacy_policy_summary}</span>
          </label>
          <button type="submit">{lp.cta_text}</button>
          <div id="msg"></div>
        </form>
      </div>
    </div>
    <div class="card">
      <h3>Caso Real em Operação</h3>
      <p style="font-size:14px;color:#cbd5e1;margin:0;">{lp.real_example_description}</p>
    </div>
  </div>
  <script>
    document.getElementById('lpForm').addEventListener('submit', async function(e) {{
      e.preventDefault();
      const msg = document.getElementById('msg');
      msg.style.color = '#93c5fd';
      msg.textContent = 'Enviando solicitação...';
      try {{
        const res = await fetch('/api/v1/public/landing-pages/{lp.slug}/capture', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            landing_page_slug: '{lp.slug}',
            full_name: document.getElementById('full_name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            company_name: document.getElementById('company_name').value,
            buy_intent: document.getElementById('buy_intent').value,
            estimated_value: 6800,
            consent_lgpd: document.getElementById('consent_lgpd').checked,
            data_origin: 'REAL'
          }})
        }});
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Falha ao enviar');
        msg.style.color = '#34d399';
        msg.textContent = 'Solicitação registrada com sucesso! Protocolo Lead #' + data.lead_id + ' (Score: ' + data.lead_score + ').';
      }} catch (err) {{
        msg.style.color = '#f87171';
        msg.textContent = err.message;
      }}
    }});
  </script>
</body>
</html>"""


def render_proposal_printable_html(prop: CommercialProposal) -> str:
    """Renderiza documento HTML/PDF executivo pronto para impressão ou exportação em PDF."""
    deliverables_li = "".join(f"<li>{item}</li>" for item in json.loads(prop.deliverables_json or "[]"))
    timeline_li = "".join(f"<li>{item}</li>" for item in json.loads(prop.timeline_schedule_json or "[]"))
    approval_badge = (
        "APROVADA PELO PROPRIETÁRIO PARA ENVIO VINCULANTE"
        if prop.owner_approved
        else "RASCUNHO / AGUARDANDO APROVAÇÃO DO PROPRIETÁRIO"
    )
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<title>Proposta Comercial {prop.proposal_number} — {prop.client_company}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #0f172a; margin: 40px; line-height: 1.5; }}
  .header {{ border-bottom: 3px solid #4f46e5; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; }}
  .badge {{ background: #eef2ff; color: #3730a3; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 12px; }}
  h1 {{ font-size: 22px; margin: 0 0 6px 0; color: #1e1b4b; }}
  h2 {{ font-size: 15px; color: #4f46e5; text-transform: uppercase; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; margin-top: 22px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; background: #f8fafc; padding: 16px; border-radius: 8px; }}
  .price-box {{ background: #1e1b4b; color: #ffffff; padding: 18px; border-radius: 8px; margin-top: 16px; }}
  @media print {{ .no-print {{ display: none; }} body {{ margin: 15mm; }} }}
</style>
</head>
<body>
  <div class="no-print" style="margin-bottom: 20px; text-align: right;">
    <button onclick="window.print()" style="background:#4f46e5;color:#fff;border:none;padding:10px 18px;border-radius:6px;cursor:pointer;font-weight:bold;">
      Imprimir / Salvar como PDF
    </button>
  </div>
  <div class="header">
    <div>
      <h1>PROPOSTA COMERCIAL Nº {prop.proposal_number}</h1>
      <div>Emitente: <strong>{prop.company_issuer_name} ({prop.business_unit_code})</strong></div>
      <div>Data de Emissão: {prop.created_at.strftime('%d/%m/%Y') if prop.created_at else ''} | Validade: {prop.validity_days} dias</div>
    </div>
    <div class="badge">{prop.status} — {approval_badge}</div>
  </div>
  <div class="grid">
    <div><strong>Cliente / Empresa:</strong> {prop.client_company}</div>
    <div><strong>Responsável:</strong> {prop.client_name} ({prop.client_email})</div>
  </div>
  <h2>1. Diagnóstico e Problema Identificado</h2>
  <p>{prop.identified_problem}</p>
  <h2>2. Solução Proposta ({prop.service_code})</h2>
  <p>{prop.proposed_solution}</p>
  <h2>3. Escopo Técnico</h2>
  <p>{prop.scope_details}</p>
  <h2>4. Entregáveis</h2>
  <ul>{deliverables_li}</ul>
  <h2>5. Cronograma Estimado</h2>
  <ul>{timeline_li}</ul>
  <h2>6. Investimento e Condições Comerciais</h2>
  <div class="price-box">
    <div>Implantação / Projeto (Setup): <strong>R$ {prop.setup_price_brl:,.2f}</strong></div>
    <div>Mensalidade Recorrente (Suporte / Operação): <strong>R$ {prop.monthly_price_brl:,.2f} / mês</strong></div>
    <div>Valor Global Estimado (12 meses): <strong>R$ {prop.total_contract_value_brl:,.2f}</strong></div>
    <div style="margin-top:8px;font-size:13px;color:#cbd5e1;">Forma de Pagamento: {prop.payment_terms}</div>
  </div>
  <h2>7. Condições, Limitações e Próximos Passos</h2>
  <p><strong>Limitações:</strong> {prop.conditions_and_limitations}</p>
  <p><strong>Próximos Passos:</strong> {prop.next_steps}</p>
</body>
</html>"""


def record_affiliate_click_service(
    db: Session,
    tenant_id: int,
    payload: Any,
) -> dict[str, Any]:
    """
    Registra um clique em link de afiliado rastreável.
    REGRA DE OURO: Um clique NUNCA é contabilizado como venda ou receita confirmada.
    """
    prod = (
        db.query(AffiliateProduct)
        .filter(AffiliateProduct.tenant_id == tenant_id, AffiliateProduct.tracking_code == payload.tracking_code)
        .first()
    )
    if not prod:
        raise ValueError(f"Link rastreável '{payload.tracking_code}' não encontrado.")

    click = AffiliateClick(
        tenant_id=tenant_id,
        product_id=prod.id,
        program_id=prod.program_id,
        tracking_code=prod.tracking_code,
        source_channel=payload.source_channel,
        utm_campaign=payload.utm_campaign,
        visitor_fingerprint=payload.visitor_fingerprint or uuid.uuid4().hex[:12],
    )
    db.add(click)
    prod.clicks_count = (prod.clicks_count or 0) + 1
    db.commit()
    db.refresh(click)

    return {
        "click_id": click.id,
        "product_id": prod.id,
        "product_name": prod.name,
        "tracking_code": prod.tracking_code,
        "destination_affiliate_url": prod.affiliate_url,
        "disclosure_label": prod.disclosure_label,
        "clicks_total": prod.clicks_count,
        "counted_as_sale": False,
        "revenue_recorded_brl": 0.0,
        "policy_note": "Clique registrado para rastreamento de tráfego. Nenhuma receita ou venda é contabilizada apenas por clique.",
    }


def record_affiliate_conversion_service(
    db: Session,
    tenant_id: int,
    payload: Any,
) -> dict[str, Any]:
    """
    Registra uma conversão de afiliado.
    Se o status for ESTIMATED ou PENDING_CONFIRMATION, NÃO entra como receita recebida no financeiro
    até que seja conciliada com evidência da plataforma.
    """
    prod = (
        db.query(AffiliateProduct)
        .filter(AffiliateProduct.tenant_id == tenant_id, AffiliateProduct.id == payload.product_id)
        .first()
    )
    if not prod:
        raise ValueError(f"Produto de afiliado #{payload.product_id} não encontrado.")

    existing = (
        db.query(AffiliateConversion)
        .filter(
            AffiliateConversion.tenant_id == tenant_id,
            AffiliateConversion.external_order_id == payload.external_order_id,
        )
        .first()
    )
    if existing:
        raise ValueError(f"Pedido externo '{payload.external_order_id}' já está registrado.")

    conv = AffiliateConversion(
        tenant_id=tenant_id,
        product_id=prod.id,
        program_id=prod.program_id,
        click_id=payload.click_id,
        external_order_id=payload.external_order_id,
        sale_amount_brl=payload.sale_amount_brl,
        commission_amount_brl=payload.commission_amount_brl,
        commission_status=payload.commission_status,
        attribution_evidence=payload.attribution_evidence,
        reconciled_in_finance=False,
        data_origin=payload.data_origin,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    if payload.commission_status in ("APPROVED", "PAID") and payload.attribution_evidence.strip():
        return reconcile_affiliate_commission_service(
            db=db,
            tenant_id=tenant_id,
            conversion_id=conv.id,
            commission_status=payload.commission_status,
            attribution_evidence=payload.attribution_evidence,
        )

    return {
        "conversion_id": conv.id,
        "external_order_id": conv.external_order_id,
        "commission_amount_brl": conv.commission_amount_brl,
        "commission_status": conv.commission_status,
        "reconciled_in_finance": conv.reconciled_in_finance,
        "financial_record_id": conv.financial_record_id,
    }


def reconcile_affiliate_commission_service(
    db: Session,
    tenant_id: int,
    conversion_id: int,
    commission_status: str,
    attribution_evidence: str,
) -> dict[str, Any]:
    """
    Concilia formalmente uma comissão de afiliado após confirmação da plataforma.
    Somente após APPROVED ou PAID com evidência de atribuição cria o registro em FinancialRecord.
    """
    conv = (
        db.query(AffiliateConversion)
        .filter(AffiliateConversion.tenant_id == tenant_id, AffiliateConversion.id == conversion_id)
        .first()
    )
    if not conv:
        raise ValueError(f"Conversão #{conversion_id} não encontrada.")

    if not attribution_evidence or len(attribution_evidence.strip()) < 5:
        raise ValueError("Evidência de atribuição/confirmação da plataforma é obrigatória para conciliar comissão.")

    conv.commission_status = commission_status.upper()
    conv.attribution_evidence = attribution_evidence.strip()
    conv.reconciled_at = datetime.now(timezone.utc)

    prod = db.query(AffiliateProduct).filter(AffiliateProduct.id == conv.product_id).first()

    if conv.commission_status in ("APPROVED", "PAID") and not conv.reconciled_in_finance:
        fin = FinancialRecord(
            tenant_id=tenant_id,
            period_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            record_type="REVENUE",
            category=f"Comissão de Afiliado ({prod.platform if prod else 'UNION_PARTNERS'})",
            channel="UNION_PARTNERS",
            amount=conv.commission_amount_brl,
            business_unit_code="UNION_PARTNERS",
            revenue_status="RECEIVED" if conv.commission_status == "PAID" else "CONFIRMED",
            is_recurring=False,
            data_origin=conv.data_origin,
            description=f"Comissão conciliada ref. Pedido {conv.external_order_id} — Evidência: {conv.attribution_evidence}",
        )
        db.add(fin)
        db.flush()
        conv.reconciled_in_finance = True
        conv.financial_record_id = fin.id
        if prod:
            prod.confirmed_conversions_count = (prod.confirmed_conversions_count or 0) + 1

    db.commit()
    db.refresh(conv)
    return {
        "conversion_id": conv.id,
        "external_order_id": conv.external_order_id,
        "commission_amount_brl": conv.commission_amount_brl,
        "commission_status": conv.commission_status,
        "attribution_evidence": conv.attribution_evidence,
        "reconciled_in_finance": conv.reconciled_in_finance,
        "financial_record_id": conv.financial_record_id,
    }


def build_multibusiness_financial_summary(
    db: Session,
    tenant_id: int,
    unit_filter: str = "ALL",
) -> dict[str, Any]:
    """
    Constrói a visão financeira consolidada e individual das 3 unidades:
    - Separa rigorosamente DADO_REAL (REAL/IMPORTED) de ESTIMATIVA (ESTIMATED), META (GOAL) e PROJEÇÃO (PROJECTION).
    - Nunca mistura projeção de pipeline ou comissão pendente com faturamento recebido/confirmado.
    """
    units = db.query(BusinessUnit).filter(BusinessUnit.tenant_id == tenant_id).all()
    fin_records = db.query(FinancialRecord).filter(FinancialRecord.tenant_id == tenant_id).all()
    deals = db.query(CRMDeal).filter(CRMDeal.tenant_id == tenant_id).all()
    leads = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id).all()
    proposals = db.query(CommercialProposal).filter(CommercialProposal.tenant_id == tenant_id).all()
    agency_clients = db.query(AgencyClientAccount).filter(AgencyClientAccount.tenant_id == tenant_id).all()
    aff_clicks = db.query(AffiliateClick).filter(AffiliateClick.tenant_id == tenant_id).all()
    aff_convs = db.query(AffiliateConversion).filter(AffiliateConversion.tenant_id == tenant_id).all()

    def _compute_unit_metrics(ucode: str | None) -> dict[str, Any]:
        u_fin = [r for r in fin_records if (ucode is None or getattr(r, "business_unit_code", "UNION_TECH") == ucode)]
        u_deals = [d for d in deals if (ucode is None or getattr(d, "business_unit_code", "UNION_TECH") == ucode)]
        u_leads = [l for l in leads if (ucode is None or getattr(l, "business_unit_code", "UNION_TECH") == ucode)]
        u_props = [p for p in proposals if (ucode is None or getattr(p, "business_unit_code", "UNION_TECH") == ucode)]

        real_revenues = [
            r.amount
            for r in u_fin
            if r.record_type == "REVENUE"
            and r.data_origin in ("REAL", "IMPORTED")
            and getattr(r, "revenue_status", "RECEIVED") in ("RECEIVED", "CONFIRMED")
        ]
        real_mrr_records = [
            r.amount
            for r in u_fin
            if r.record_type == "REVENUE"
            and r.data_origin in ("REAL", "IMPORTED")
            and getattr(r, "is_recurring", False)
        ]
        expenses = [
            r.amount
            for r in u_fin
            if r.record_type in ("EXPENSE", "AD_SPEND") and r.data_origin in ("REAL", "IMPORTED")
        ]
        ad_spend = [
            r.amount for r in u_fin if r.record_type == "AD_SPEND" and r.data_origin in ("REAL", "IMPORTED")
        ]

        open_deals = [d for d in u_deals if d.status == "OPEN"]
        won_deals = [d for d in u_deals if d.status == "WON" and d.data_origin in ("REAL", "IMPORTED")]

        gross_rev = round(sum(real_revenues), 2)
        total_exp = round(sum(expenses), 2)
        total_ad = round(sum(ad_spend), 2)
        net_profit = round(gross_rev - total_exp, 2)
        margin_pct = round((net_profit / gross_rev) * 100.0, 2) if gross_rev > 0 else 0.0

        mrr_deals = sum(getattr(d, "recurring_mrr_brl", 0.0) for d in won_deals)
        mrr_agency = (
            sum(c.monthly_retainer_brl for c in agency_clients if c.status == "ACTIVE" and c.owner_approved_pricing and c.data_origin == "REAL")
            if (ucode in (None, "UNION_AGENCY"))
            else 0.0
        )
        mrr_total = round(max(sum(real_mrr_records), mrr_deals + mrr_agency), 2)

        projected_pipeline = round(sum(d.value * (d.probability_pct / 100.0) for d in open_deals), 2)

        customers_won = max(1, len(won_deals))
        cac = round(total_ad / customers_won, 2) if total_ad > 0 else 0.0
        avg_ticket = round(gross_rev / customers_won, 2) if gross_rev > 0 else 0.0
        ltv = round(avg_ticket * 6.0, 2)
        roi_pct = round(((gross_rev - total_exp) / total_exp) * 100.0, 2) if total_exp > 0 else 0.0
        roas = round(gross_rev / total_ad, 2) if total_ad > 0 else 0.0
        conv_rate = round((len(won_deals) / len(u_leads)) * 100.0, 2) if u_leads else 0.0

        goal_val = sum(
            u.monthly_revenue_goal_brl for u in units if (ucode is None or u.code == ucode)
        )

        return {
            "unit_code": ucode or "CONSOLIDATED",
            "dado_real": {
                "gross_revenue_brl": gross_rev,
                "received_confirmed_revenue_brl": gross_rev,
                "monthly_recurring_revenue_mrr_brl": mrr_total,
                "expenses_and_costs_brl": total_exp,
                "ad_spend_brl": total_ad,
                "net_profit_brl": net_profit,
                "margin_pct": margin_pct,
                "leads_total": len(u_leads),
                "proposals_total": len(u_props),
                "deals_won_count": len(won_deals),
                "conversion_rate_pct": conv_rate,
                "cac_brl": cac,
                "roi_pct": roi_pct,
                "roas": roas,
            },
            "estimativa": {
                "ltv_estimated_6m_brl": ltv,
            },
            "projecao": {
                "weighted_pipeline_projection_brl": projected_pipeline,
                "open_deals_count": len(open_deals),
            },
            "meta": {
                "monthly_revenue_goal_brl": round(goal_val, 2),
                "goal_attainment_pct": round((gross_rev / goal_val) * 100.0, 2) if goal_val > 0 else 0.0,
            },
        }

    pending_commissions = round(
        sum(c.commission_amount_brl for c in aff_convs if c.commission_status in ("ESTIMATED", "PENDING_CONFIRMATION")),
        2,
    )
    approved_commissions = round(
        sum(c.commission_amount_brl for c in aff_convs if c.commission_status == "APPROVED" and c.data_origin == "REAL"),
        2,
    )
    paid_commissions = round(
        sum(c.commission_amount_brl for c in aff_convs if c.commission_status == "PAID" and c.data_origin == "REAL"),
        2,
    )

    by_unit = {
        "UNION_TECH": _compute_unit_metrics("UNION_TECH"),
        "UNION_AGENCY": {
            **_compute_unit_metrics("UNION_AGENCY"),
            "active_clients_count": sum(1 for c in agency_clients if c.status == "ACTIVE"),
            "at_risk_clients_count": sum(1 for c in agency_clients if c.status == "AT_RISK"),
        },
        "UNION_PARTNERS": {
            **_compute_unit_metrics("UNION_PARTNERS"),
            "affiliate_metrics": {
                "total_clicks": len(aff_clicks),
                "total_conversions": len(aff_convs),
                "pending_commissions_brl": pending_commissions,
                "approved_commissions_brl": approved_commissions,
                "paid_commissions_brl": paid_commissions,
            },
        },
    }

    consolidated = _compute_unit_metrics(None if unit_filter == "ALL" else unit_filter)

    return {
        "selected_unit": unit_filter,
        "consolidated": consolidated,
        "units": by_unit,
        "governance_note": (
            "Separação estrita ativa: Projeções de pipeline e comissões pendentes (PENDING_CONFIRMATION) "
            "jamais são somadas em 'received_confirmed_revenue_brl' (DADO_REAL)."
        ),
    }


def generate_commercial_alerts(db: Session, tenant_id: int) -> list[dict[str, Any]]:
    """
    Verifica e gera alertas comerciais inteligentes conforme Seção 15:
    - Lead importante sem acompanhamento
    - Proposta sem resposta / aguardando aprovação
    - Campanha com baixo desempenho
    - Conteúdo não publicado
    - Integração desconectada
    - Comissão de afiliado não conciliada
    - Cliente da agência em risco
    """
    alerts = []

    high_leads = (
        db.query(CRMLead)
        .filter(CRMLead.tenant_id == tenant_id, CRMLead.lead_score >= 70, CRMLead.funnel_stage == "LEAD")
        .count()
    )
    if high_leads > 0:
        alerts.append({
            "severity": "WARNING",
            "category": "CRM_LEAD",
            "title": f"{high_leads} Lead(s) de alto potencial aguardando diagnóstico",
            "message": "Existem leads qualificados com score >= 70 que ainda não avançaram para DIAGNÓSTICO ou PROPOSTA.",
            "suggested_action": "Acionar qualificação e gerar proposta comercial na aba Propostas.",
        })

    pending_props = (
        db.query(CommercialProposal)
        .filter(
            CommercialProposal.tenant_id == tenant_id,
            CommercialProposal.status.in_(("DRAFT", "PENDING_APPROVAL", "SENT")),
        )
        .count()
    )
    if pending_props > 0:
        alerts.append({
            "severity": "INFO",
            "category": "PROPOSAL",
            "title": f"{pending_props} Proposta(s) comercial(is) pendente(s) de aprovação ou resposta",
            "message": "Propostas aguardando revisão do proprietário ou acompanhamento de fechamento.",
            "suggested_action": "Revisar propostas na seção Propostas & Fechamento.",
        })

    unreconciled_convs = (
        db.query(AffiliateConversion)
        .filter(AffiliateConversion.tenant_id == tenant_id, AffiliateConversion.reconciled_in_finance == False)  # noqa: E712
        .count()
    )
    if unreconciled_convs > 0:
        alerts.append({
            "severity": "WARNING",
            "category": "AFFILIATES",
            "title": f"{unreconciled_convs} Comissão(ões) de afiliados aguardando conciliação",
            "message": "Existem conversões registradas em UNION PARTNERS aguardando confirmação da plataforma para conciliação financeira.",
            "suggested_action": "Verificar evidência do pedido na plataforma e conciliar na aba UNION PARTNERS.",
        })

    pending_integrations = (
        db.query(IntegrationConnection)
        .filter(IntegrationConnection.tenant_id == tenant_id, IntegrationConnection.status == "PENDING_CREDENTIALS")
        .count()
    )
    if pending_integrations > 0:
        alerts.append({
            "severity": "INFO",
            "category": "INTEGRATIONS",
            "title": f"{pending_integrations} Integrações externas aguardando credenciais OAuth",
            "message": "Publicação social opera em modo Pacote Assistido até a conexão das credenciais oficiais.",
            "suggested_action": "Conectar tokens oficiais na Central de Integrações quando desejar disparo externo automático.",
        })

    unpublished_contents = (
        db.query(ContentFactoryItem)
        .filter(ContentFactoryItem.tenant_id == tenant_id, ContentFactoryItem.status == "PLANNED")
        .count()
    )
    if unpublished_contents > 0:
        alerts.append({
            "severity": "INFO",
            "category": "CONTENT",
            "title": f"{unpublished_contents} Conteúdos planejados na fila da Content Factory",
            "message": "Peças prontas aguardando aprovação ou exportação assistida.",
            "suggested_action": "Revisar e exportar pacotes na aba Content Factory.",
        })

    return alerts


def build_multibusiness_executive_dashboard(
    db: Session,
    tenant: Tenant,
    unit_filter: str = "ALL",
) -> dict[str, Any]:
    """
    Painel Executivo Multinegócio consolidando UNION_TECH, UNION_AGENCY e UNION_PARTNERS,
    com filtro por unidade, funil de 10 etapas, catálogo, propostas, clientes, afiliados e alertas.
    """
    seeded_counts = ensure_phase17_multibusiness_seeded(db, tenant)
    fin_summary = build_multibusiness_financial_summary(db, tenant.id, unit_filter=unit_filter)

    units = db.query(BusinessUnit).filter(BusinessUnit.tenant_id == tenant.id).all()
    services_q = db.query(ProductService).filter(ProductService.tenant_id == tenant.id)
    offers_q = db.query(CommercialOffer).filter(CommercialOffer.tenant_id == tenant.id)
    opps_q = db.query(MarketOpportunity).filter(MarketOpportunity.tenant_id == tenant.id)
    lps_q = db.query(LandingPage).filter(LandingPage.tenant_id == tenant.id)
    props_q = db.query(CommercialProposal).filter(CommercialProposal.tenant_id == tenant.id)
    leads_q = db.query(CRMLead).filter(CRMLead.tenant_id == tenant.id)
    campaigns_q = db.query(MarketingCampaign).filter(MarketingCampaign.tenant_id == tenant.id)
    contents_q = db.query(ContentFactoryItem).filter(ContentFactoryItem.tenant_id == tenant.id)

    if unit_filter in ("UNION_TECH", "UNION_AGENCY", "UNION_PARTNERS"):
        services_q = services_q.filter(ProductService.business_unit_code == unit_filter)
        offers_q = offers_q.filter(CommercialOffer.business_unit_code == unit_filter)
        opps_q = opps_q.filter(MarketOpportunity.business_unit_code == unit_filter)
        lps_q = lps_q.filter(LandingPage.business_unit_code == unit_filter)
        props_q = props_q.filter(CommercialProposal.business_unit_code == unit_filter)
        leads_q = leads_q.filter(CRMLead.business_unit_code == unit_filter)
        campaigns_q = campaigns_q.filter(MarketingCampaign.business_unit_code == unit_filter)
        contents_q = contents_q.filter(ContentFactoryItem.business_unit_code == unit_filter)

    leads_list = leads_q.order_by(CRMLead.id.desc()).all()
    funnel_breakdown = {stg: 0 for stg in FUNNEL_STAGES_ORDER}
    for l in leads_list:
        stg = getattr(l, "funnel_stage", "LEAD") or "LEAD"
        funnel_breakdown[stg] = funnel_breakdown.get(stg, 0) + 1

    agency_clients = (
        db.query(AgencyClientAccount)
        .filter(AgencyClientAccount.tenant_id == tenant.id)
        .order_by(AgencyClientAccount.id.desc())
        .all()
    )
    aff_programs = (
        db.query(AffiliateProgram)
        .filter(AffiliateProgram.tenant_id == tenant.id)
        .order_by(AffiliateProgram.id.asc())
        .all()
    )
    aff_products = (
        db.query(AffiliateProduct)
        .filter(AffiliateProduct.tenant_id == tenant.id)
        .order_by(AffiliateProduct.id.desc())
        .all()
    )
    aff_conversions = (
        db.query(AffiliateConversion)
        .filter(AffiliateConversion.tenant_id == tenant.id)
        .order_by(AffiliateConversion.id.desc())
        .limit(25)
        .all()
    )

    return {
        "selected_unit": unit_filter,
        "period_reference": datetime.now(timezone.utc).strftime("%Y-%m"),
        "data_source": "PostgreSQL 16 Real-Time Relational Engine",
        "seeded_summary": seeded_counts,
        "business_units": [
            {
                "id": u.id,
                "code": u.code,
                "name": u.name,
                "business_type": u.business_type,
                "description": u.description,
                "target_audience": u.target_audience,
                "value_proposition": u.value_proposition,
                "products_services": json.loads(u.products_services_json or "[]"),
                "acquisition_channels": json.loads(u.acquisition_channels_json or "[]"),
                "revenue_streams": json.loads(u.revenue_streams_json or "[]"),
                "monthly_revenue_goal_brl": u.monthly_revenue_goal_brl,
                "monthly_budget_brl": u.monthly_budget_brl,
                "status": u.status,
            }
            for u in units
        ],
        "financial_summary": fin_summary,
        "sales_funnel_10_stages": funnel_breakdown,
        "services_catalog": [serialize_product_service(s) for s in services_q.order_by(ProductService.id.asc()).all()],
        "commercial_offers": [
            {
                "id": o.id,
                "business_unit_code": o.business_unit_code,
                "name": o.name,
                "headline": o.headline,
                "offer_type": o.offer_type,
                "plan_tier": o.plan_tier,
                "setup_fee_brl": o.setup_fee_brl,
                "monthly_fee_brl": o.monthly_fee_brl,
                "included_items": json.loads(o.included_items_json or "[]"),
                "limits": json.loads(o.limits_json or "{}"),
                "owner_approved": o.owner_approved,
                "is_active": o.is_active,
            }
            for o in offers_q.order_by(CommercialOffer.id.asc()).all()
        ],
        "market_opportunities": [
            {
                "id": m.id,
                "business_unit_code": m.business_unit_code,
                "segment": m.segment,
                "identified_problem": m.identified_problem,
                "recommended_service_code": m.recommended_service_code,
                "recommended_service_name": m.recommended_service_name,
                "ideal_customer_profile": m.ideal_customer_profile,
                "commercial_potential": m.commercial_potential,
                "implementation_difficulty": m.implementation_difficulty,
                "priority": m.priority,
                "justification": m.justification,
                "information_source": m.information_source,
                "researched_at": m.researched_at,
            }
            for m in opps_q.order_by(MarketOpportunity.id.asc()).all()
        ],
        "landing_pages": [
            {
                "id": lp.id,
                "business_unit_code": lp.business_unit_code,
                "slug": lp.slug,
                "title": lp.title,
                "value_proposition": lp.value_proposition,
                "problem_statement": lp.problem_statement,
                "solution_summary": lp.solution_summary,
                "benefits": json.loads(lp.benefits_json or "[]"),
                "real_example_description": lp.real_example_description,
                "differentials": json.loads(lp.differentials_json or "[]"),
                "cta_text": lp.cta_text,
                "views_count": lp.views_count,
                "leads_captured_count": lp.leads_captured_count,
                "conversions_count": lp.conversions_count,
                "is_published": lp.is_published,
            }
            for lp in lps_q.order_by(LandingPage.id.asc()).all()
        ],
        "proposals": [serialize_proposal(p) for p in props_q.order_by(CommercialProposal.id.desc()).limit(25).all()],
        "agency_clients": [
            {
                "id": c.id,
                "client_name": c.client_name,
                "brand_name": c.brand_name,
                "slug": c.slug,
                "segment": c.segment,
                "target_audience": c.target_audience,
                "products": json.loads(c.products_json or "[]"),
                "objectives": json.loads(c.objectives_json or "[]"),
                "communication_tone": c.communication_tone,
                "plan_tier": c.plan_tier,
                "plan_limits": AGENCY_PLAN_LIMITS.get(c.plan_tier, AGENCY_PLAN_LIMITS["PRO"]),
                "setup_fee_brl": c.setup_fee_brl,
                "monthly_retainer_brl": c.monthly_retainer_brl,
                "campaigns_count": c.campaigns_count,
                "contents_count": c.contents_count,
                "leads_count": c.leads_count,
                "status": c.status,
                "owner_approved_pricing": c.owner_approved_pricing,
            }
            for c in agency_clients
        ],
        "affiliate_operation": {
            "programs": [
                {
                    "id": p.id,
                    "name": p.name,
                    "platform": p.platform,
                    "approval_status": p.approval_status,
                    "credentials_status": p.credentials_status,
                    "rules_summary": p.rules_summary,
                    "default_commission_pct": p.default_commission_pct,
                    "attribution_window_days": p.attribution_window_days,
                    "payment_conditions": p.payment_conditions,
                    "limitations": p.limitations,
                    "official_api_status": p.official_api_status,
                }
                for p in aff_programs
            ],
            "products": [
                {
                    "id": pr.id,
                    "program_id": pr.program_id,
                    "platform": pr.platform,
                    "name": pr.name,
                    "category": pr.category,
                    "brand": pr.brand,
                    "observed_price_brl": pr.observed_price_brl,
                    "price_source": pr.price_source,
                    "observed_at": pr.observed_at,
                    "availability_status": pr.availability_status,
                    "authorized_url": pr.authorized_url,
                    "affiliate_url": pr.affiliate_url,
                    "tracking_code": pr.tracking_code,
                    "commission_pct": pr.commission_pct,
                    "estimated_commission_brl": pr.estimated_commission_brl,
                    "curation_score": pr.curation_score,
                    "disclosure_label": pr.disclosure_label,
                    "clicks_count": pr.clicks_count,
                    "confirmed_conversions_count": pr.confirmed_conversions_count,
                }
                for pr in aff_products
            ],
            "conversions": [
                {
                    "id": cv.id,
                    "product_id": cv.product_id,
                    "external_order_id": cv.external_order_id,
                    "sale_amount_brl": cv.sale_amount_brl,
                    "commission_amount_brl": cv.commission_amount_brl,
                    "commission_status": cv.commission_status,
                    "attribution_evidence": cv.attribution_evidence,
                    "reconciled_in_finance": cv.reconciled_in_finance,
                    "financial_record_id": cv.financial_record_id,
                }
                for cv in aff_conversions
            ],
        },
        "counts_by_unit": {
            "campaigns": campaigns_q.count(),
            "contents": contents_q.count(),
            "leads": len(leads_list),
        },
        "payments": [
            serialize_payment_transaction(pt)
            for pt in db.query(PaymentTransaction)
            .filter(PaymentTransaction.tenant_id == tenant.id)
            .order_by(PaymentTransaction.id.desc())
            .limit(25)
            .all()
        ],
        "delivery_projects": [
            serialize_delivery_project(dp)
            for dp in db.query(ServiceDeliveryProject)
            .filter(ServiceDeliveryProject.tenant_id == tenant.id)
            .order_by(ServiceDeliveryProject.id.desc())
            .limit(25)
            .all()
        ],
        "commercial_alerts": generate_commercial_alerts(db, tenant.id),
        "phase18_1_executive_panel": build_phase18_1_executive_panel(db, tenant.id),
    }


def generate_multibusiness_ceo_daily_report(db: Session, tenant: Tenant) -> dict[str, Any]:
    """
    Produz o relatório diário do AI CEO consolidando as 3 unidades (UNION_TECH, UNION_AGENCY, UNION_PARTNERS)
    e registra honestamente processing_type = DETERMINISTIC_PYTHON_ENGINE.
    """
    ensure_phase17_multibusiness_seeded(db, tenant)
    fin = build_multibusiness_financial_summary(db, tenant.id, unit_filter="ALL")
    alerts = generate_commercial_alerts(db, tenant.id)
    opps_count = db.query(MarketOpportunity).filter(MarketOpportunity.tenant_id == tenant.id).count()
    props_count = db.query(CommercialProposal).filter(CommercialProposal.tenant_id == tenant.id).count()

    cons_real = fin["consolidated"]["dado_real"]
    cons_proj = fin["consolidated"]["projecao"]

    report = {
        "briefing_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "processing_type": "DETERMINISTIC_PYTHON_ENGINE",
        "model_used": "python-multibusiness-ceo-v17",
        "headline": (
            f"Diretoria Multinegócio Ativa — Receita Real Confirmada: R$ {cons_real['gross_revenue_brl']:,.2f} | "
            f"MRR: R$ {cons_real['monthly_recurring_revenue_mrr_brl']:,.2f} | "
            f"Pipeline Projetado: R$ {cons_proj['weighted_pipeline_projection_brl']:,.2f}"
        ),
        "units_performance": {
            "UNION_TECH": fin["units"]["UNION_TECH"],
            "UNION_AGENCY": fin["units"]["UNION_AGENCY"],
            "UNION_PARTNERS": fin["units"]["UNION_PARTNERS"],
        },
        "opportunities_mapped": opps_count,
        "proposals_total": props_count,
        "alerts": alerts,
        "priorities": [
            "1. [UNION_TECH] Converter leads qualificados das Landing Pages em Diagnósticos de Automação (SRV_01) e Agentes de IA (SRV_02).",
            "2. [UNION_AGENCY] Expandir contratos mensais recorrentes (Planos PRO e BUSINESS) com entrega automatizada via Content Factory.",
            "3. [UNION_PARTNERS] Curar produtos de alta demanda e conciliar apenas comissões comprovadas nas plataformas oficiais.",
        ],
        "execution_plan_today": [
            "07:00 — Pesquisa de oportunidades setoriais (AGENT_09_COMPETITIVE)",
            "08:00 — Consolidação do CEO Daily Briefing Multinegócio (AGENT_01_CEO)",
            "09:00 — Planejamento de ofertas e campanhas por unidade (AGENT_02_CMO)",
            "10:00 — Produção de lotes de conteúdo segmentados (AGENT_06_COPYWRITER)",
            "12:00 — Qualificação e scoring de leads capturados (AGENT_08_SALES)",
            "16:00 — Follow-up de propostas e negociações abertas (AGENT_08_SALES)",
            "18:00 — Conciliação financeira estrita por unidade (AGENT_10_FINANCE)",
        ],
    }

    briefing = CEODailyBriefing(
        tenant_id=tenant.id,
        briefing_date=report["briefing_date"],
        summary_headline=report["headline"],
        what_happened_json=json.dumps(
            [
                f"UNION_TECH Receita Real: R$ {fin['units']['UNION_TECH']['dado_real']['gross_revenue_brl']:,.2f}",
                f"UNION_AGENCY Receita Real: R$ {fin['units']['UNION_AGENCY']['dado_real']['gross_revenue_brl']:,.2f}",
                f"UNION_PARTNERS Receita Real: R$ {fin['units']['UNION_PARTNERS']['dado_real']['gross_revenue_brl']:,.2f}",
            ],
            ensure_ascii=False,
        ),
        what_is_working_json=json.dumps(
            ["Isolamento multinegócio e multi-tenant ativo", "Calculadora dinâmica de serviços operacional", "Rastreamento de afiliados sem falsos positivos"],
            ensure_ascii=False,
        ),
        what_is_wrong_json=json.dumps([a["title"] for a in alerts], ensure_ascii=False),
        opportunities_json=json.dumps([f"{opps_count} oportunidades mapeadas em 8 segmentos prioritários"], ensure_ascii=False),
        urgent_problems_json=json.dumps([a["message"] for a in alerts if a["severity"] in ("WARNING", "CRITICAL")], ensure_ascii=False),
        recommendations_json=json.dumps(report["priorities"], ensure_ascii=False),
        priority_actions_json=json.dumps(report["execution_plan_today"], ensure_ascii=False),
        data_sources_summary_json=json.dumps({"engine": "DETERMINISTIC_PYTHON_ENGINE", "units": 3}, ensure_ascii=False),
    )
    db.add(briefing)
    db.commit()
    return report


# ==============================================================================
# FASE 18 — MOTOR DE PAGAMENTOS (MERCADO PAGO & SANDBOX), WEBHOOKS & ONBOARDING
# ==============================================================================
def compute_payment_webhook_signature(external_reference: str, provider_payment_id: str, new_status: str) -> str:
    """Calcula assinatura HMAC-SHA256 determinística para validação criptográfica de notificações de webhook."""
    msg = f"{external_reference}:{provider_payment_id}:{new_status.upper()}".encode("utf-8")
    return hmac.new(settings.SECRET_KEY.encode("utf-8"), msg, hashlib.sha256).hexdigest()


def serialize_payment_transaction(tx: PaymentTransaction) -> dict[str, Any]:
    return {
        "id": tx.id,
        "business_unit_code": tx.business_unit_code,
        "proposal_id": tx.proposal_id,
        "lead_id": tx.lead_id,
        "client_name": tx.client_name,
        "client_company": tx.client_company,
        "client_email": tx.client_email,
        "provider": tx.provider,
        "external_reference": tx.external_reference,
        "provider_payment_id": tx.provider_payment_id,
        "idempotency_key": tx.idempotency_key,
        "amount_brl": tx.amount_brl,
        "payment_method": tx.payment_method,
        "payment_link_url": tx.payment_link_url,
        "execution_mode": tx.execution_mode,
        "status": tx.status,
        "owner_approved": tx.owner_approved,
        "webhook_signature_verified": tx.webhook_signature_verified,
        "webhook_events": json.loads(tx.webhook_events_json or "[]"),
        "receipt_number": tx.receipt_number,
        "reconciled_in_finance": tx.reconciled_in_finance,
        "financial_record_id": tx.financial_record_id,
        "onboarding_project_id": tx.onboarding_project_id,
        "counted_as_received_revenue": bool(tx.status == "APPROVED" and tx.reconciled_in_finance),
        "data_origin": tx.data_origin,
        "created_at": tx.created_at.isoformat() if tx.created_at else "",
        "paid_at": tx.paid_at.isoformat() if tx.paid_at else None,
    }


def create_payment_charge_service(
    db: Session,
    tenant_id: int,
    payload: Any,
) -> dict[str, Any]:
    """
    Cria uma cobrança comercial vinculada a uma proposta/cliente:
    - Exige owner_approved=True (proibido criar cobranças sem aprovação do proprietário).
    - Garante idempotência estrita via idempotency_key.
    - NUNCA registra receita recebida apenas porque a cobrança (PENDING) foi criada.
    - Se Mercado Pago estiver sem credenciais de produção ou sandbox_mode=True, opera em modo SANDBOX transparente.
    """
    if not payload.owner_approved:
        raise PermissionError(
            "Governança Financeira: Não é permitido emitir cobrança comercial sem aprovação expressa do proprietário (owner_approved=True)."
        )

    idem_key = (payload.idempotency_key or "").strip() or f"pay-{tenant_id}-{payload.proposal_id or 0}-{uuid.uuid4().hex[:10]}"
    existing = (
        db.query(PaymentTransaction)
        .filter(PaymentTransaction.tenant_id == tenant_id, PaymentTransaction.idempotency_key == idem_key)
        .first()
    )
    if existing:
        out = serialize_payment_transaction(existing)
        out["idempotent_reused"] = True
        return out

    mp_conn = (
        db.query(IntegrationConnection)
        .filter(IntegrationConnection.tenant_id == tenant_id, IntegrationConnection.provider_key == "mercado_pago")
        .first()
    )
    mp_connected = bool(mp_conn and mp_conn.status == "CONNECTED")
    exec_mode = "SANDBOX" if (payload.sandbox_mode or not mp_connected) else "PRODUCTION_API"

    ext_ref = f"UG-{payload.business_unit_code}-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    prov_pay_id = f"mp_{'sbx' if exec_mode == 'SANDBOX' else 'live'}_{uuid.uuid4().hex[:10]}"
    pay_link = f"https://www.mercadopago.com.br/checkout/v1/redirect?pref_id={prov_pay_id}&ref={ext_ref}"

    tx = PaymentTransaction(
        tenant_id=tenant_id,
        business_unit_code=payload.business_unit_code,
        proposal_id=payload.proposal_id,
        lead_id=payload.lead_id,
        client_name=payload.client_name.strip(),
        client_company=payload.client_company.strip(),
        client_email=payload.client_email.strip().lower(),
        provider="mercado_pago",
        external_reference=ext_ref,
        provider_payment_id=prov_pay_id,
        idempotency_key=idem_key,
        amount_brl=round(payload.amount_brl, 2),
        payment_method=payload.payment_method,
        payment_link_url=pay_link,
        execution_mode=exec_mode,
        status="PENDING",
        owner_approved=True,
        webhook_signature_verified=False,
        webhook_events_json=json.dumps(
            [{"timestamp": datetime.now(timezone.utc).isoformat(), "event": "CHARGE_CREATED", "status": "PENDING", "mode": exec_mode}],
            ensure_ascii=False,
        ),
        reconciled_in_finance=False,
        data_origin=payload.data_origin,
    )
    db.add(tx)
    if payload.lead_id:
        lead = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id, CRMLead.id == payload.lead_id).first()
        if lead:
            lead.funnel_stage = "PAGAMENTO"
    db.commit()
    db.refresh(tx)

    out = serialize_payment_transaction(tx)
    out["idempotent_reused"] = False
    out["webhook_test_signature_for_approved"] = compute_payment_webhook_signature(ext_ref, prov_pay_id, "APPROVED")
    return out


def process_payment_webhook_service(
    db: Session,
    tenant_id: int,
    payload: Any,
) -> dict[str, Any]:
    """
    Processa notificação de webhook de pagamento:
    1. Valida assinatura criptográfica HMAC-SHA256 (rejeita com PermissionError se inválida).
    2. Garante idempotência (notificações repetidas para o mesmo status não duplicam receita nem projetos).
    3. Somente quando new_status == 'APPROVED' registra receita confirmada/recebida em FinancialRecord
       e dispara automaticamente a criação do projeto de Onboarding & Entrega Técnica.
    """
    expected_sig = compute_payment_webhook_signature(
        payload.external_reference,
        payload.provider_payment_id,
        payload.new_status,
    )
    if not payload.signature or not hmac.compare_digest(payload.signature.strip(), expected_sig):
        raise PermissionError("Assinatura criptográfica do webhook de pagamento inválida ou ausente (HMAC-SHA256 mismatch).")

    tx = (
        db.query(PaymentTransaction)
        .filter(
            PaymentTransaction.tenant_id == tenant_id,
            PaymentTransaction.external_reference == payload.external_reference,
        )
        .first()
    )
    if not tx:
        raise ValueError(f"Transação com external_reference '{payload.external_reference}' não encontrada.")

    target_status = payload.new_status.upper()

    # Proteção de Idempotência: se já está no mesmo status e já conciliado, retorna sem duplicar
    if tx.status == target_status and (target_status != "APPROVED" or tx.reconciled_in_finance):
        out = serialize_payment_transaction(tx)
        out["idempotent_duplicate"] = True
        return out

    events = json.loads(tx.webhook_events_json or "[]")
    events.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": payload.event_id or f"evt_{uuid.uuid4().hex[:8]}",
            "status": target_status,
            "signature_verified": True,
        }
    )
    tx.webhook_events_json = json.dumps(events, ensure_ascii=False)
    tx.webhook_signature_verified = True
    tx.provider_payment_id = payload.provider_payment_id
    tx.status = target_status
    tx.updated_at = datetime.now(timezone.utc)

    if target_status == "APPROVED" and not tx.reconciled_in_finance:
        tx.paid_at = datetime.now(timezone.utc)
        tx.receipt_number = f"REC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{tx.id:04d}"

        fin = FinancialRecord(
            tenant_id=tenant_id,
            period_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            record_type="REVENUE",
            category=f"Pagamento Confirmado ({tx.payment_method})",
            channel=tx.business_unit_code,
            amount=tx.amount_brl,
            business_unit_code=tx.business_unit_code,
            revenue_status="RECEIVED",
            is_recurring=False,
            data_origin=tx.data_origin,
            description=f"Recebimento confirmado via Webhook Verificado ({tx.external_reference} / {tx.provider_payment_id}) — Cliente: {tx.client_company or tx.client_name}",
        )
        db.add(fin)
        db.flush()
        tx.reconciled_in_finance = True
        tx.financial_record_id = fin.id

        svc_code = "SRV_01_DIAGNOSTICO"
        scope_str = "Implantação de solução tecnológica conforme proposta aprovada."
        if tx.proposal_id:
            prop = db.query(CommercialProposal).filter(CommercialProposal.id == tx.proposal_id).first()
            if prop:
                prop.status = "ACCEPTED"
                prop.contract_status = "ACCEPTED_WITH_EVIDENCE"
                prop.acceptance_evidence = f"Pagamento aprovado #{tx.provider_payment_id} ({tx.receipt_number})"
                svc_code = prop.service_code
                scope_str = prop.scope_details

        if tx.lead_id:
            lead = db.query(CRMLead).filter(CRMLead.id == tx.lead_id).first()
            if lead:
                lead.funnel_stage = "ONBOARDING"
                lead.pipeline_stage = "CLOSED_WON"
                lead.qualification_status = "CONVERTED"

        # Acionar automaticamente Onboarding & Entrega do Serviço
        if not tx.onboarding_project_id:
            proj = create_service_delivery_project_internal(
                db=db,
                tenant_id=tenant_id,
                business_unit_code=tx.business_unit_code,
                proposal_id=tx.proposal_id,
                payment_id=tx.id,
                lead_id=tx.lead_id,
                client_name=tx.client_name,
                client_company=tx.client_company or tx.client_name,
                client_email=tx.client_email,
                service_code=svc_code,
                contracted_scope=scope_str,
                data_origin=tx.data_origin,
            )
            tx.onboarding_project_id = proj.id

    elif target_status in ("REFUNDED", "CANCELLED", "REJECTED", "DISPUTED"):
        tx.reconciled_in_finance = False
        if tx.financial_record_id:
            fin_rec = db.query(FinancialRecord).filter(FinancialRecord.id == tx.financial_record_id).first()
            if fin_rec:
                fin_rec.revenue_status = target_status

    db.commit()
    db.refresh(tx)
    out = serialize_payment_transaction(tx)
    out["idempotent_duplicate"] = False
    return out


def create_service_delivery_project_internal(
    db: Session,
    tenant_id: int,
    business_unit_code: str,
    proposal_id: int | None,
    payment_id: int | None,
    lead_id: int | None,
    client_name: str,
    client_company: str,
    client_email: str,
    service_code: str,
    contracted_scope: str,
    due_date: str = "",
    data_origin: str = "REAL",
) -> ServiceDeliveryProject:
    svc = (
        db.query(ProductService)
        .filter(ProductService.tenant_id == tenant_id, ProductService.service_code == service_code)
        .first()
    )
    svc_name = svc.name if svc else f"Projeto Técnico ({service_code})"
    days = svc.estimated_timeline_days if svc else 15
    target_due = due_date or (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d")

    deliverables_list = json.loads(svc.deliverables_json or "[]") if svc else [
        "Mapeamento Técnico e Arquitetura",
        "Implantação e Testes Integrados",
        "Treinamento e Handover Operacional",
    ]
    checklist = [
        {"step": "1. Boas-vindas, Kickoff e alinhamento de expectativas", "completed": True},
        {"step": "2. Coleta de credenciais, acessos e documentos técnicos do cliente", "completed": False},
        {"step": "3. Configuração de ambiente e execução técnica do escopo", "completed": False},
        {"step": "4. Testes de qualidade, segurança e homologação assistida", "completed": False},
        {"step": "5. Entrega final, validação formal do cliente e ativação de pós-venda", "completed": False},
    ]
    tasks = [
        {"title": "Reunião de Kickoff e levantamento de acessos", "owner": "AGENT_11_CS", "status": "COMPLETED"},
        {"title": f"Execução técnica dos entregáveis de {service_code}", "owner": "AGENT_01_CEO", "status": "IN_PROGRESS"},
        {"title": "Homologação final e coleta de aceite do cliente", "owner": "AGENT_11_CS", "status": "PENDING"},
    ]
    docs_required = [
        "Cadastro societário e contato do ponto focal técnico",
        "Credenciais de homologação/APIs dos sistemas integrados (quando aplicável)",
    ]

    proj = ServiceDeliveryProject(
        tenant_id=tenant_id,
        business_unit_code=business_unit_code,
        project_code=f"PRJ-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:5].upper()}",
        proposal_id=proposal_id,
        payment_id=payment_id,
        lead_id=lead_id,
        client_name=client_name,
        client_company=client_company,
        client_email=client_email,
        service_code=service_code,
        service_name=svc_name,
        contracted_scope=contracted_scope or (svc.scope_summary if svc else "Escopo técnico conforme proposta aprovada."),
        tasks_json=json.dumps(tasks, ensure_ascii=False),
        milestones_json=json.dumps(
            [
                {"milestone": "M1: Kickoff & Acessos", "due_in_days": 3},
                {"milestone": "M2: Desenvolvimento & Integração", "due_in_days": max(5, days - 3)},
                {"milestone": "M3: Homologação & Go-Live", "due_in_days": days},
            ],
            ensure_ascii=False,
        ),
        required_documents_json=json.dumps(docs_required, ensure_ascii=False),
        onboarding_checklist_json=json.dumps(checklist, ensure_ascii=False),
        deliverables_json=json.dumps([{"name": d, "status": "IN_PROGRESS"} for d in deliverables_list], ensure_ascii=False),
        client_validation_status="PENDING",
        status="ONBOARDING",
        progress_pct=20.0,
        due_date=target_due,
        data_origin=data_origin,
    )
    db.add(proj)
    db.flush()
    return proj


def update_service_delivery_project_service(
    db: Session,
    tenant_id: int,
    project_id: int,
    payload: Any,
) -> dict[str, Any]:
    proj = (
        db.query(ServiceDeliveryProject)
        .filter(ServiceDeliveryProject.tenant_id == tenant_id, ServiceDeliveryProject.id == project_id)
        .first()
    )
    if not proj:
        raise ValueError(f"Projeto de entrega #{project_id} não encontrado.")

    if payload.completed_checklist_step:
        checklist = json.loads(proj.onboarding_checklist_json or "[]")
        for item in checklist:
            if payload.completed_checklist_step.lower() in item["step"].lower():
                item["completed"] = True
        proj.onboarding_checklist_json = json.dumps(checklist, ensure_ascii=False)
        done_count = sum(1 for item in checklist if item.get("completed"))
        proj.progress_pct = round((done_count / max(1, len(checklist))) * 100.0, 1)

    if payload.deliverable_submitted:
        delivs = json.loads(proj.deliverables_json or "[]")
        for d in delivs:
            if payload.deliverable_submitted.lower() in d["name"].lower():
                d["status"] = "DELIVERED"
        proj.deliverables_json = json.dumps(delivs, ensure_ascii=False)

    if payload.execution_evidence is not None:
        proj.execution_evidence = payload.execution_evidence.strip()
    if payload.progress_pct is not None:
        proj.progress_pct = payload.progress_pct
    if payload.client_validation_status is not None:
        proj.client_validation_status = payload.client_validation_status
    if payload.client_validation_notes is not None:
        proj.client_validation_notes = payload.client_validation_notes
    if payload.status is not None:
        if payload.status in ("DELIVERED", "COMPLETED"):
            has_evidence = bool(
                getattr(proj, "execution_evidence", "")
                or payload.execution_evidence
                or payload.deliverable_submitted
                or payload.client_validation_notes
                or proj.client_validation_notes
            )
            if not has_evidence:
                raise ValueError(
                    "Governança de Entrega: Não é permitido marcar projeto como DELIVERED ou COMPLETED sem registrar evidência técnica de execução."
                )
            proj.progress_pct = 100.0
            proj.completed_at = datetime.now(timezone.utc)
            if proj.lead_id:
                lead = db.query(CRMLead).filter(CRMLead.id == proj.lead_id).first()
                if lead:
                    lead.funnel_stage = "POS_VENDA" if payload.status == "COMPLETED" else "ENTREGA"
            if payload.status == "COMPLETED":
                db.add(
                    CRMActivity(
                        tenant_id=tenant_id,
                        lead_id=proj.lead_id,
                        activity_type="FOLLOW_UP",
                        subject=f"[PÓS-VENDA] Acompanhamento de Satisfação e Expansão — {proj.project_code} ({proj.client_company})",
                        description=f"Entrega concluída com evidência registrada. Agendar revisão de resultados e oportunidade de recorrência.",
                        due_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        completed=False,
                    )
                )
        proj.status = payload.status

    db.commit()
    db.refresh(proj)
    return serialize_delivery_project(proj)


def serialize_delivery_project(proj: ServiceDeliveryProject) -> dict[str, Any]:
    return {
        "id": proj.id,
        "project_code": proj.project_code,
        "business_unit_code": proj.business_unit_code,
        "proposal_id": proj.proposal_id,
        "payment_id": proj.payment_id,
        "lead_id": proj.lead_id,
        "client_name": proj.client_name,
        "client_company": proj.client_company,
        "client_email": proj.client_email,
        "service_code": proj.service_code,
        "service_name": proj.service_name,
        "contracted_scope": proj.contracted_scope,
        "responsible_owner": proj.responsible_owner,
        "tasks": json.loads(proj.tasks_json or "[]"),
        "milestones": json.loads(proj.milestones_json or "[]"),
        "required_documents": json.loads(proj.required_documents_json or "[]"),
        "onboarding_checklist": json.loads(proj.onboarding_checklist_json or "[]"),
        "deliverables": json.loads(proj.deliverables_json or "[]"),
        "client_validation_status": proj.client_validation_status,
        "client_validation_notes": proj.client_validation_notes,
        "execution_evidence": getattr(proj, "execution_evidence", ""),
        "status": proj.status,
        "progress_pct": proj.progress_pct,
        "due_date": proj.due_date,
        "data_origin": proj.data_origin,
        "created_at": proj.created_at.isoformat() if proj.created_at else "",
        "completed_at": proj.completed_at.isoformat() if proj.completed_at else None,
    }


def reactivate_crm_lead_service(
    db: Session,
    tenant_id: int,
    lead_id: int,
    payload: Any,
) -> dict[str, Any]:
    """Reativa um lead estagnado/perdido verificando rigorosamente consentimento LGPD e ausência de opt-out."""
    lead = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id, CRMLead.id == lead_id).first()
    if not lead:
        raise ValueError("Lead não encontrado.")
    if lead.opt_out or getattr(lead, "contact_blocked", False) or not lead.consent_lgpd:
        raise PermissionError("Bloqueio LGPD: Não é permitido reativar contato que solicitou opt-out ou não possui consentimento ativo.")

    lead.funnel_stage = "QUALIFICACAO"
    lead.pipeline_stage = "QUALIFICATION"
    lead.qualification_status = "QUALIFIED"
    lead.reactivation_count = (getattr(lead, "reactivation_count", 0) or 0) + 1
    lead.last_contact_at = datetime.now(timezone.utc)
    lead.notes = f"{lead.notes}\n[REATIVAÇÃO AUTORIZADA] Base: {payload.authorization_basis}. {payload.custom_message_notes}".strip()

    db.add(
        CRMActivity(
            tenant_id=tenant_id,
            lead_id=lead.id,
            activity_type="RECOVERY",
            subject=f"Reativação Comercial Autorizada — {lead.full_name}",
            description=f"Base legal verificada ({payload.authorization_basis}). Mensagem preparada para revisão.",
            due_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            completed=False,
        )
    )
    db.commit()
    db.refresh(lead)
    return {
        "lead_id": lead.id,
        "full_name": lead.full_name,
        "funnel_stage": lead.funnel_stage,
        "reactivation_count": lead.reactivation_count,
        "consent_lgpd": lead.consent_lgpd,
        "opt_out": lead.opt_out,
    }


def export_lead_lgpd_data_service(db: Session, tenant_id: int, lead_id: int) -> dict[str, Any]:
    """Exporta pacote completo de dados pessoais do titular em conformidade com o direito de acesso/portabilidade da LGPD."""
    lead = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id, CRMLead.id == lead_id).first()
    if not lead:
        raise ValueError("Lead não encontrado.")
    activities = db.query(CRMActivity).filter(CRMActivity.tenant_id == tenant_id, CRMActivity.lead_id == lead.id).all()
    proposals = db.query(CommercialProposal).filter(CommercialProposal.tenant_id == tenant_id, CommercialProposal.lead_id == lead.id).all()
    return {
        "lgpd_right": "PORTABILIDADE_E_ACESSO_DO_TITULAR",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "personal_data": {
            "id": lead.id,
            "full_name": lead.full_name,
            "email": lead.email,
            "phone": lead.phone,
            "company_name": lead.company_name,
            "consent_lgpd": lead.consent_lgpd,
            "consent_source": lead.consent_source,
            "legal_basis": getattr(lead, "legal_basis", "CONSENTIMENTO_OPT_IN"),
            "purpose_description": getattr(lead, "purpose_description", ""),
            "opt_out": lead.opt_out,
            "created_at": lead.created_at.isoformat() if lead.created_at else "",
        },
        "activities_recorded": [{"subject": a.subject, "type": a.activity_type, "due_date": a.due_date} for a in activities],
        "proposals_recorded": [p.proposal_number for p in proposals],
    }


def erase_lead_lgpd_data_service(db: Session, tenant_id: int, user_id: int, user_email: str, lead_id: int) -> dict[str, Any]:
    """Executa anonimização/exclusão de dados pessoais mediante solicitação do titular (Direito de Eliminação LGPD)."""
    lead = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id, CRMLead.id == lead_id).first()
    if not lead:
        raise ValueError("Lead não encontrado.")
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            actor=user_email,
            action="LGPD_DATA_SUBJECT_ERASURE",
            resource_type="CRMLead",
            resource_id=str(lead_id),
            details_json=json.dumps({"erased_at": datetime.now(timezone.utc).isoformat(), "status": "ANONYMIZED_AND_DELETED"}),
        )
    )
    db.delete(lead)
    db.commit()
    return {"status": "LGPD_ERASED", "lead_id": lead_id}


# ==============================================================================
# FASE 18.1 — ABORDAGEM COMERCIAL COM COOLDOWN & PAINEL EXECUTIVO (5 BUCKETS)
# ==============================================================================
def prepare_lead_outreach_service(
    db: Session,
    tenant_id: int,
    lead_id: int,
    payload: Any,
) -> dict[str, Any]:
    """
    Prepara abordagem comercial personalizada para revisão do proprietário:
    - Respeita LGPD (bloqueia opt_out ou sem consentimento).
    - Aplica controle de frequência de contato (cooldown mínimo de 24 horas entre abordagens).
    - NUNCA dispara mensagem externa automaticamente sem aprovação do proprietário.
    """
    lead = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id, CRMLead.id == lead_id).first()
    if not lead:
        raise ValueError("Lead não encontrado.")
    if lead.opt_out or getattr(lead, "contact_blocked", False) or not lead.consent_lgpd:
        raise PermissionError("Conformidade LGPD: Contato bloqueado ou sem consentimento válido para abordagem comercial.")

    now = datetime.now(timezone.utc)
    last_out = getattr(lead, "last_outreach_at", None)
    if last_out:
        if last_out.tzinfo is None:
            last_out = last_out.replace(tzinfo=timezone.utc)
        hours_since = (now - last_out).total_seconds() / 3600.0
        if hours_since < 24.0 and not payload.owner_approve_outreach:
            raise ValueError(
                f"Controle de Frequência Comercial: Última abordagem preparada há {hours_since:.1f}h (mínimo 24h para evitar spam)."
            )

    svc = (
        db.query(ProductService)
        .filter(ProductService.tenant_id == tenant_id, ProductService.service_code == payload.service_code)
        .first()
    )
    svc_name = svc.name if svc else payload.service_code
    draft = (
        f"Olá {lead.full_name}, tudo bem? Aqui é da diretoria técnica da UNION TECH.\n"
        f"Analisamos o perfil da {lead.company_name or 'sua operação'} e preparamos uma sugestão prática via {svc_name} "
        f"({payload.custom_angle or 'redução de trabalho manual e automação em Python'}).\n"
        f"Podemos agendar um diagnóstico técnico de 15 minutos? (Caso não deseje receber comunicações, responda SAIR para opt-out imediato)."
    )
    lead.outreach_draft_message = draft
    lead.outreach_approved_by_owner = bool(payload.owner_approve_outreach)
    lead.last_outreach_at = now
    db.commit()
    db.refresh(lead)
    return {
        "lead_id": lead.id,
        "full_name": lead.full_name,
        "company_name": lead.company_name,
        "service_code": payload.service_code,
        "outreach_draft_message": lead.outreach_draft_message,
        "outreach_approved_by_owner": lead.outreach_approved_by_owner,
        "external_message_sent": False,
        "governance_note": "Abordagem preparada no CRM. Nenhum disparo externo ocorre sem aprovação do proprietário e canal conectado.",
    }


def build_phase18_1_executive_panel(db: Session, tenant_id: int) -> dict[str, Any]:
    """
    Painel Executivo da Fase 18.1 separando estritamente:
    - REAL (apenas registros com data_origin == 'REAL' e pagamentos em PRODUCTION_API confirmados; exibe 0 quando não houver evidência real)
    - ESTIMATIVA (custos e margens estimadas pela calculadora)
    - PROJECAO (pipeline aberto ponderado)
    - META (objetivos mensais das 3 unidades)
    - SIMULACAO (registros Sandbox, TEST, DEMO e IMPORTED)
    Inclui também os 12 alertas de transição do funil comercial.
    """
    leads = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id).all()
    opps = db.query(MarketOpportunity).filter(MarketOpportunity.tenant_id == tenant_id).all()
    props = db.query(CommercialProposal).filter(CommercialProposal.tenant_id == tenant_id).all()
    payments = db.query(PaymentTransaction).filter(PaymentTransaction.tenant_id == tenant_id).all()
    projects = db.query(ServiceDeliveryProject).filter(ServiceDeliveryProject.tenant_id == tenant_id).all()
    fin_records = db.query(FinancialRecord).filter(FinancialRecord.tenant_id == tenant_id).all()
    deals = db.query(CRMDeal).filter(CRMDeal.tenant_id == tenant_id).all()
    units = db.query(BusinessUnit).filter(BusinessUnit.tenant_id == tenant_id).all()
    svcs = db.query(ProductService).filter(ProductService.tenant_id == tenant_id).all()

    # 1. Separar REAL estrito (excluindo IMPORTED, TEST, DEMO, SIMULATION e SANDBOX)
    real_leads = [l for l in leads if l.data_origin == "REAL"]
    real_qualified_leads = [l for l in real_leads if l.qualification_status == "QUALIFIED" or l.lead_score >= 65]
    real_props = [p for p in props if p.data_origin == "REAL"]
    real_props_approved = [p for p in real_props if p.owner_approved]
    real_props_sent = [p for p in real_props if p.status in ("SENT", "VIEWED", "NEGOTIATION", "ACCEPTED")]
    real_contracts_signed = [p for p in real_props if getattr(p, "contract_status", "") == "ACCEPTED_WITH_EVIDENCE"]

    real_live_payments_pending = [
        pt for pt in payments if pt.data_origin == "REAL" and pt.execution_mode == "PRODUCTION_API" and pt.status == "PENDING"
    ]
    real_live_payments_confirmed = [
        pt for pt in payments if pt.data_origin == "REAL" and pt.execution_mode == "PRODUCTION_API" and pt.status == "APPROVED" and pt.reconciled_in_finance
    ]
    real_received_revenue = round(sum(pt.amount_brl for pt in real_live_payments_confirmed), 2)
    real_costs = round(
        sum(r.amount for r in fin_records if r.data_origin == "REAL" and r.record_type in ("EXPENSE", "AD_SPEND")),
        2,
    )
    real_margin_pct = round(((real_received_revenue - real_costs) / real_received_revenue) * 100.0, 2) if real_received_revenue > 0 else 0.0

    real_projects = [pr for pr in projects if pr.data_origin == "REAL"]
    real_projects_running = [pr for pr in real_projects if pr.status in ("ONBOARDING", "IN_PROGRESS", "WAITING_CLIENT")]
    real_projects_completed = [pr for pr in real_projects if pr.status in ("DELIVERED", "COMPLETED") and getattr(pr, "execution_evidence", "")]
    real_conv_rate = round((len(real_contracts_signed) / len(real_leads)) * 100.0, 2) if real_leads else 0.0

    # 2. Separar SIMULAÇÃO / SANDBOX / HISTÓRICO IMPORTADO
    sim_leads = [l for l in leads if l.data_origin in ("TEST", "DEMO", "SIMULATION", "IMPORTED")]
    sim_payments = [pt for pt in payments if pt.execution_mode == "SANDBOX" or pt.data_origin in ("TEST", "DEMO", "SIMULATION")]
    sim_payments_confirmed = [pt for pt in sim_payments if pt.status == "APPROVED"]
    sim_projects = [pr for pr in projects if pr.data_origin in ("TEST", "DEMO", "SIMULATION")]
    imported_revenue = round(
        sum(r.amount for r in fin_records if r.data_origin == "IMPORTED" and r.record_type == "REVENUE"),
        2,
    )

    # 3. Alertas das 12 etapas do funil (ETAPA 4)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    overdue_projects = [
        pr for pr in projects if pr.status not in ("DELIVERED", "COMPLETED") and pr.due_date and pr.due_date < today_str
    ]
    funnel_12_alerts = {
        "01_novo_lead": sum(1 for l in leads if l.funnel_stage in ("VISITANTE", "LEAD")),
        "02_lead_qualificado": sum(1 for l in leads if l.funnel_stage in ("QUALIFICACAO", "QUALIFICADO")),
        "03_oportunidade_prioritaria": sum(1 for o in opps if o.priority in ("HIGH", "URGENT")),
        "04_diagnostico_pendente": sum(1 for l in leads if l.funnel_stage == "DIAGNOSTICO"),
        "05_proposta_aguardando_aprovacao": sum(1 for p in props if p.status in ("DRAFT", "PENDING_APPROVAL") and not p.owner_approved),
        "06_proposta_enviada": sum(1 for p in props if p.status in ("SENT", "VIEWED", "NEGOTIATION")),
        "07_contrato_aguardando_assinatura": sum(1 for p in props if p.owner_approved and getattr(p, "contract_status", "") != "ACCEPTED_WITH_EVIDENCE"),
        "08_pagamento_pendente": sum(1 for pt in payments if pt.status == "PENDING"),
        "09_pagamento_confirmado": sum(1 for pt in payments if pt.status == "APPROVED"),
        "10_onboarding_iniciado": sum(1 for pr in projects if pr.status in ("ONBOARDING", "IN_PROGRESS")),
        "11_entrega_atrasada": len(overdue_projects),
        "12_pos_venda": sum(1 for pr in projects if pr.status == "COMPLETED"),
    }

    open_deals = [d for d in deals if d.status == "OPEN"]
    avg_est_margin = round(sum(s.estimated_margin_pct for s in svcs) / max(1, len(svcs)), 2)

    return {
        "REAL": {
            "leads_reais": len(real_leads),
            "leads_qualificados": len(real_qualified_leads),
            "oportunidades_mapeadas": len(opps),
            "propostas_aprovadas": len(real_props_approved),
            "propostas_enviadas": len(real_props_sent),
            "contratos_assinados_com_evidencia": len(real_contracts_signed),
            "cobrancas_pendentes_producao": len(real_live_payments_pending),
            "pagamentos_confirmados_producao": len(real_live_payments_confirmed),
            "receita_recebida_confirmada_brl": real_received_revenue,
            "custos_reais_brl": real_costs,
            "margem_real_pct": real_margin_pct,
            "projetos_em_execucao": len(real_projects_running),
            "entregas_concluidas_com_evidencia": len(real_projects_completed),
            "taxa_conversao_real_pct": real_conv_rate,
            "first_real_paid_customer_verified": len(real_live_payments_confirmed) > 0,
        },
        "ESTIMATIVA": {
            "custo_medio_servico_brl": round(sum(s.estimated_cost_brl for s in svcs) / max(1, len(svcs)), 2),
            "margem_estimada_catalogo_pct": avg_est_margin,
        },
        "PROJECAO": {
            "pipeline_ponderado_aberto_brl": round(sum(d.value * (d.probability_pct / 100.0) for d in open_deals), 2),
            "negociacoes_abertas_count": len(open_deals),
        },
        "META": {
            "meta_mensal_total_brl": round(sum(u.monthly_revenue_goal_brl for u in units), 2),
        },
        "SIMULACAO": {
            "leads_teste_e_importados": len(sim_leads),
            "cobrancas_sandbox_total": len(sim_payments),
            "pagamentos_sandbox_aprovados": len(sim_payments_confirmed),
            "valor_transacionado_sandbox_brl": round(sum(pt.amount_brl for pt in sim_payments_confirmed), 2),
            "projetos_entrega_sandbox": len(sim_projects),
            "historico_importado_seed_brl": imported_revenue,
        },
        "funnel_12_stage_alerts": funnel_12_alerts,
        "honesty_statement": (
            "Transparência Estrita Fase 18.1: O bloco REAL exibe 0.00 para receita recebida enquanto não houver "
            "pagamento liquidado via PRODUCTION_API (Mercado Pago Live). Transações Sandbox e dados de seed ficam "
            "isolados no bloco SIMULACAO."
        ),
    }


