import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.agents.orchestrator import compute_lead_score, generate_ceo_daily_briefing_service
from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.models.entities import (
    Competitor,
    CRMDeal,
    CRMLead,
    CustomerFeedback,
    EditorialCalendarItem,
    FinancialRecord,
    GrowthExperiment,
    MarketingCampaign,
    MarketingPersona,
    StrategicGoal,
    Tenant,
    User,
)
from app.services.automation_scheduler import ensure_tenant_automations_seeded, execute_automation_rule
from app.services.creative_and_copy_engine import generate_creative_asset, generate_persuasive_copy
from app.services.integrations_and_social_engine import ensure_tenant_integrations_seeded
from app.services.seo_and_market_engine import generate_seo_factory_article, research_keywords_and_clusters


def get_configured_admin_password() -> str:
    """Strong initial password comes ONLY from env ADMIN_INITIAL_PASSWORD; otherwise a random unknown one (account locked until set)."""
    import secrets

    pwd = (settings.ADMIN_INITIAL_PASSWORD or "").strip()
    if pwd and pwd.lower() != "uniongrowth@2026" and len(pwd) >= 10:
        return pwd
    return secrets.token_urlsafe(32)


def ensure_initial_workspace_seeded(db: Session) -> Tenant:
    """
    Idempotently initializes the default executive workspace on first boot so the system
    is immediately operational with real persisted records, clearly labeled data origins,
    working login, and active automations. Also rotates any legacy weak default password.
    """
    effective_pwd = get_configured_admin_password()
    tenant = db.query(Tenant).filter(Tenant.slug == "union-growth-hq").first()
    if tenant:
        admin_user = db.query(User).filter(User.email == "admin@projetosunion.cloud").first()
        if admin_user and verify_password("UnionGrowth@2026", admin_user.hashed_password):
            admin_user.hashed_password = hash_password(effective_pwd)
            prefs = {}
            try:
                prefs = json.loads(admin_user.preferences_json or "{}")
            except Exception:
                prefs = {}
            prefs["initial_default_password_invalidated"] = True
            prefs["must_change_password"] = True
            prefs["password_rotated_at"] = datetime.now(timezone.utc).isoformat()
            admin_user.preferences_json = json.dumps(prefs, ensure_ascii=False)
            db.commit()
        ensure_tenant_integrations_seeded(db, tenant.id)
        ensure_tenant_automations_seeded(db, tenant.id)
        return tenant

    tenant = Tenant(
        name="Union Growth Holding Ltda",
        slug="union-growth-hq",
        brand_name="UNION GROWTH OS",
        primary_color="#6366F1",
        secondary_color="#10B981",
        domain="https://uniongrowth.72.62.13.62.sslip.io",
        niche="Plataforma SaaS de Inteligência Empresarial, Marketing & Automação",
        target_audience="Empresas B2B, E-commerces e Operações Digitais em Escala",
        products_json=json.dumps(["Union Growth OS Enterprise", "AI Marketing Director Suite", "CRM & Sales Automation"]),
        services_json=json.dumps(["Consultoria de Growth", "Implementação Assistida", "Auditoria SEO & Performance"]),
        strategy_summary="Reduzir trabalho manual em marketing e vendas através de 11 agentes coordenados por IA.",
        plan_tier="ENTERPRISE",
        autonomy_default_level=2,
        owner_email="admin@projetosunion.cloud",
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    admin_user = User(
        tenant_id=tenant.id,
        email="admin@projetosunion.cloud",
        full_name="Thiago Thomaz — Diretor Executivo",
        hashed_password=hash_password(effective_pwd),
        role="owner",
        is_active=True,
        lgpd_consent=True,
        preferences_json=json.dumps(
            {
                "initial_default_password_invalidated": True,
                "must_change_password": True,
                "password_rotated_at": datetime.now(timezone.utc).isoformat(),
            },
            ensure_ascii=False,
        ),
    )
    db.add(admin_user)
    db.commit()

    # Seed Strategic Goals (Origin = GOAL)
    goals = [
        StrategicGoal(
            tenant_id=tenant.id,
            title="Atingir R$ 150.000 em Receita Recorrente Mensal (MRR)",
            period="MONTHLY",
            metric_name="MRR (Receita Mensal)",
            target_value=150000.0,
            current_value=48500.0,
            unit="BRL",
            data_origin="GOAL",
            financial_impact_score=98.0,
            priority="CRITICAL",
            deadline="2026-12-31",
        ),
        StrategicGoal(
            tenant_id=tenant.id,
            title="Reduzir CAC Médio para abaixo de R$ 350",
            period="QUARTERLY",
            metric_name="CAC",
            target_value=350.0,
            current_value=310.0,
            unit="BRL",
            data_origin="GOAL",
            financial_impact_score=90.0,
            priority="HIGH",
            deadline="2027-03-31",
        ),
        StrategicGoal(
            tenant_id=tenant.id,
            title="Publicar 40 Artigos Otimizados no Cluster de SEO",
            period="ANNUAL",
            metric_name="Artigos SEO Publicados",
            target_value=40.0,
            current_value=6.0,
            unit="UN",
            data_origin="GOAL",
            financial_impact_score=85.0,
            priority="HIGH",
            deadline="2027-11-01",
        ),
    ]
    db.add_all(goals)

    # Seed Financial Records with explicit origin (IMPORTED)
    fin_records = [
        FinancialRecord(
            tenant_id=tenant.id,
            period_date="2026-11-01",
            record_type="REVENUE",
            category="Assinaturas SaaS & Contratos B2B",
            channel="Organic SEO",
            amount=28500.0,
            data_origin="IMPORTED",
            description="Faturamento importado de contratos ativos via canal orgânico",
        ),
        FinancialRecord(
            tenant_id=tenant.id,
            period_date="2026-11-05",
            record_type="REVENUE",
            category="Implementação Enterprise",
            channel="Outbound & CRM",
            amount=20000.0,
            data_origin="IMPORTED",
            description="Faturamento importado de fechamentos comerciais no CRM",
        ),
        FinancialRecord(
            tenant_id=tenant.id,
            period_date="2026-11-05",
            record_type="EXPENSE",
            category="Infraestrutura Cloud & Operação",
            channel="Direct",
            amount=4200.0,
            data_origin="IMPORTED",
            description="Custos operacionais de servidores, banco de dados e suporte",
        ),
        FinancialRecord(
            tenant_id=tenant.id,
            period_date="2026-11-08",
            record_type="AD_SPEND",
            category="Campanhas de Aquisição",
            channel="Paid Search",
            amount=3100.0,
            data_origin="IMPORTED",
            description="Investimento em mídia de intenção comercial",
        ),
    ]
    db.add_all(fin_records)

    # Seed Marketing Persona & Campaign
    persona = MarketingPersona(
        tenant_id=tenant.id,
        name="Diretor / Fundador de Empresa em Crescimento (ICP Principal)",
        role_segment="CEO / Diretor Comercial / Head de Marketing (PME & Mid-Market)",
        demographics="Empresas com faturamento entre R$ 50 mil e R$ 2 milhões/mês",
        pains_json=json.dumps(["Alto custo operacional de equipe manual", "Falta de previsibilidade de leads", "Baixo retorno sobre tráfego"]),
        desires_json=json.dumps(["Operação comercial 24/7", "Indicadores financeiros claros", "Crescer sem inflar folha de pagamento"]),
        objections_json=json.dumps(["Complexidade de integração", "Tempo de implantação"]),
        channels_json=json.dumps(["Google Search (SEO)", "LinkedIn", "Instagram", "YouTube"]),
        value_proposition="Substitua processos fragmentados por uma diretoria digital completa operando em nuvem.",
    )
    db.add(persona)

    camp = MarketingCampaign(
        tenant_id=tenant.id,
        name="Campanha de Aquisição Orgânica & Diagnóstico Executivo",
        campaign_type="ACQUISITION",
        channel="Organic SEO + LinkedIn",
        objective="Captar decisores B2B através de diagnóstico gratuito de maturidade digital",
        funnel_stage="TOFU/MOFU/BOFU",
        budget_planned=5000.0,
        spend_real=3100.0,
        revenue_attributed=48500.0,
        roi_pct=1464.5,
        leads_generated=24,
        conversions=10,
        data_origin="IMPORTED",
        status="ACTIVE",
        start_date="2026-11-01",
    )
    db.add(camp)

    # Seed CRM Leads & Deals
    lead1 = CRMLead(
        tenant_id=tenant.id,
        full_name="Carlos Eduardo Mendes",
        email="carlos.mendes@techvanguard.com.br",
        phone="+5511998765432",
        company_name="TechVanguard Soluções B2B",
        source_channel="Organic SEO",
        buy_intent="URGENT",
        estimated_value=18000.0,
        data_origin="IMPORTED",
        consent_lgpd=True,
        notes="Solicitou demonstração do plano Enterprise para 3 unidades.",
    )
    lead1.lead_score, lead1.qualification_status = compute_lead_score(lead1)

    lead2 = CRMLead(
        tenant_id=tenant.id,
        full_name="Fernanda Oliveira Costa",
        email="fernanda@grupohiperion.com.br",
        phone="+5521987651234",
        company_name="Grupo Hiperion",
        source_channel="LinkedIn",
        buy_intent="HIGH",
        estimated_value=12500.0,
        data_origin="IMPORTED",
        consent_lgpd=True,
        notes="Interesse em automação de SEO e calendário de redes sociais.",
    )
    lead2.lead_score, lead2.qualification_status = compute_lead_score(lead2)

    db.add_all([lead1, lead2])
    db.commit()
    db.refresh(lead1)
    db.refresh(lead2)

    deal1 = CRMDeal(
        tenant_id=tenant.id,
        lead_id=lead1.id,
        title="Contrato Anual Enterprise — TechVanguard",
        stage="CLOSED_WON",
        value=28500.0,
        probability_pct=100.0,
        expected_close_date="2026-11-05",
        status="WON",
        data_origin="IMPORTED",
    )
    deal2 = CRMDeal(
        tenant_id=tenant.id,
        lead_id=lead2.id,
        title="Implantação Plano Business — Grupo Hiperion",
        stage="PROPOSAL",
        value=12500.0,
        probability_pct=75.0,
        expected_close_date="2026-11-25",
        status="OPEN",
        data_origin="IMPORTED",
    )
    db.add_all([deal1, deal2])

    # Seed Competitor, Growth Experiment & Customer Success Feedback
    comp = Competitor(
        tenant_id=tenant.id,
        name="Agência Tradicional Manual S/A",
        website_url="https://example.com",
        category="Serviço Manual Tradicional",
        public_pricing_summary="Fee mensal fixo elevado + percentual sobre mídia",
        positioning_summary="Operação dependente de atendimento manual com SLA de 48h",
        strengths_json=json.dumps(["Presença antiga no mercado"]),
        weaknesses_json=json.dumps(["Alto tempo de resposta", "Sem automação em tempo real", "Sem CRM integrado"]),
        differentiation_opportunities_json=json.dumps(["Execução imediata por agentes de IA", "Custo previsível e controle total de dados"]),
    )
    db.add(comp)

    exp = GrowthExperiment(
        tenant_id=tenant.id,
        title="Calculadora Interativa de ROI e Economia de Equipe na Landing Page",
        channel="Organic SEO",
        hypothesis="Incluir calculadora de economia operacional aumentará a conversão de visitantes em leads qualificados de 2.5% para 4.5%.",
        objective="Aumentar geração de leads qualificados com CAC zero",
        target_audience=tenant.target_audience,
        indicator_metric="Taxa de Conversão da Landing Page (%)",
        estimated_cost=0.0,
        baseline_conversion_pct=2.5,
        real_result_conversion_pct=4.8,
        real_result_summary="Amostra importada: 500 visitas -> 24 leads qualificados (4.8% de conversão).",
        data_origin="IMPORTED",
        ice_score=9.0,
        status="COMPLETED",
        conclusion="Hipótese validada (+92% sobre a linha de base). Manter calculadora ativa como canal principal.",
    )
    db.add(exp)

    fb = CustomerFeedback(
        tenant_id=tenant.id,
        customer_name="Carlos Eduardo Mendes (TechVanguard)",
        customer_email="carlos.mendes@techvanguard.com.br",
        nps_score=10,
        csat_score=5,
        sentiment="POSITIVE",
        churn_risk="LOW",
        recurring_issue_tag="Elogio / Expansão",
        feedback_text="O CEO Daily Briefing e a fábrica de conteúdo economizaram mais de 25 horas semanais do nosso time.",
        retention_suggestion="Convidar para estudo de caso oficial e programa de indicação.",
        upsell_opportunity="Expansão para mais 2 empresas do mesmo grupo econômico.",
    )
    db.add(fb)
    db.commit()

    # Seed SEO, Creative, Copy, Editorial Calendar, Integrations & Automations
    research_keywords_and_clusters(db, tenant, "automação de marketing e gestão empresarial")
    generate_seo_factory_article(
        db,
        tenant,
        topic="Como Estruturar Marketing e Vendas Autônomos com Inteligência Artificial",
        target_keyword="automação de marketing e vendas",
    )
    asset = generate_creative_asset(
        db=db,
        tenant=tenant,
        title="Post Institucional — Diretoria Digital Autônoma",
        asset_type="SOCIAL_POST",
        platform="instagram",
        headline_text="Sua Empresa com 11 Especialistas Digitais 24/7",
        subheadline_text="CEO, CMO, SEO, Social Media, Copywriter, Growth e CRM integrados",
        cta_text="Conhecer Plataforma",
    )
    generate_persuasive_copy(
        db=db,
        tenant=tenant,
        title="Landing Page Principal — Union Growth OS",
        copy_type="LANDING_PAGE",
        framework="AIDA",
        product_or_offer="UNION GROWTH OS",
        target_audience=tenant.target_audience,
        key_benefit="automatizar aquisição de clientes, SEO, conteúdo e vendas em uma única central",
    )

    cal_item = EditorialCalendarItem(
        tenant_id=tenant.id,
        title="Carrossel: 5 Gargalos que Travam o Crescimento da sua Empresa",
        platform="instagram",
        content_format="CAROUSEL",
        caption="Descubra como unificar SEO, Redes Sociais, Copywriting e CRM sem depender de processos manuais.",
        hashtags_json=json.dumps(["#marketingdigital", "#crescimento", "#gestao", "#seo", "#crm"]),
        media_asset_id=asset.id,
        video_script="Slide 1: Hook | Slide 2-4: Diagnóstico | Slide 5: CTA",
        scheduled_for="2026-11-12 12:30",
        best_time_rationale="Janela de maior engajamento B2B no horário de almoço (12:30).",
        approval_status="PENDING_REVIEW",
        publish_status="QUEUED",
    )
    db.add(cal_item)
    db.commit()

    ensure_tenant_integrations_seeded(db, tenant.id)
    rules = ensure_tenant_automations_seeded(db, tenant.id)
    generate_ceo_daily_briefing_service(db, tenant)

    # Execute the CEO Briefing automation rule once on initial seed so execution history is populated
    if rules:
        execute_automation_rule(db, rules[1], idempotency_key="initial-seed-ceo-briefing")

    return tenant

