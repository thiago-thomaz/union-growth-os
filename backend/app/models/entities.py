from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(180), nullable=False)
    slug = Column(String(120), unique=True, index=True, nullable=False)
    brand_name = Column(String(180), nullable=False)
    logo_url = Column(String(500), default="")
    primary_color = Column(String(20), default="#6366F1")
    secondary_color = Column(String(20), default="#10B981")
    domain = Column(String(255), default="")
    niche = Column(String(180), default="Tecnologia & B2B SaaS")
    target_audience = Column(Text, default="Empresas e empreendedores buscando crescimento previsível")
    products_json = Column(Text, default="[]")
    services_json = Column(Text, default="[]")
    social_links_json = Column(Text, default="{}")
    strategy_summary = Column(Text, default="")
    plan_tier = Column(String(40), default="ENTERPRISE")  # STARTER, PRO, BUSINESS, ENTERPRISE
    autonomy_default_level = Column(Integer, default=2)  # 1=Assistido, 2=Semiautônomo, 3=Autônomo
    agent_autonomy_json = Column(Text, default="{}")
    owner_email = Column(String(255), index=True, nullable=False)
    data_retention_days = Column(Integer, default=365)
    lgpd_dpo_email = Column(String(255), default="dpo@empresa.com.br")
    # Fase 23 — Modo UX Simples/Avançado, Brand Intelligence & Onboarding Progressivo 6 Etapas
    ui_mode = Column(String(20), default="SIMPLE")
    brand_voice = Column(String(160), default="Consultivo, claro e orientado a resultados")
    brand_fonts = Column(String(160), default="Inter + Plus Jakarta Sans")
    brand_differentials = Column(Text, default="")
    brand_allowed_terms = Column(Text, default="")
    brand_forbidden_terms = Column(Text, default="lucro garantido, milagre financeiro, ganhe dinheiro fácil")
    brand_examples = Column(Text, default="")
    brand_country = Column(String(80), default="Brasil")
    brand_description = Column(Text, default="")
    growth_goals_json = Column(Text, default="[]")
    onboarding_step = Column(Integer, default=1)
    onboarding_state_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(180), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="owner")  # owner, admin, manager, analyst, viewer
    is_active = Column(Boolean, default=True)
    lgpd_consent = Column(Boolean, default=True)
    lgpd_consent_at = Column(DateTime, default=utcnow)
    marketing_opt_in = Column(Boolean, default=True)
    preferences_json = Column(Text, default="{}")
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class StrategicGoal(Base):
    __tablename__ = "strategic_goals"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    period = Column(String(40), default="MONTHLY")  # MONTHLY, QUARTERLY, ANNUAL
    metric_name = Column(String(100), nullable=False)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    unit = Column(String(30), default="BRL")
    data_origin = Column(String(30), default="GOAL")  # REAL, IMPORTED, ESTIMATED, GOAL
    financial_impact_score = Column(Float, default=85.0)
    priority = Column(String(30), default="HIGH")
    status = Column(String(40), default="ON_TRACK")
    deadline = Column(String(40), default="")
    created_at = Column(DateTime, default=utcnow)


class CEODailyBriefing(Base):
    __tablename__ = "ceo_daily_briefings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    briefing_date = Column(String(30), index=True, nullable=False)
    summary_headline = Column(String(500), nullable=False)
    what_happened_json = Column(Text, default="[]")
    what_is_working_json = Column(Text, default="[]")
    what_is_wrong_json = Column(Text, default="[]")
    opportunities_json = Column(Text, default="[]")
    urgent_problems_json = Column(Text, default="[]")
    recommendations_json = Column(Text, default="[]")
    priority_actions_json = Column(Text, default="[]")
    automation_candidates_json = Column(Text, default="[]")
    data_sources_summary_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=utcnow)


class MarketingPersona(Base):
    __tablename__ = "marketing_personas"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(180), nullable=False)
    role_segment = Column(String(180), default="")
    demographics = Column(Text, default="")
    pains_json = Column(Text, default="[]")
    desires_json = Column(Text, default="[]")
    objections_json = Column(Text, default="[]")
    channels_json = Column(Text, default="[]")
    value_proposition = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)


class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(220), nullable=False)
    campaign_type = Column(String(50), default="ACQUISITION")  # ACQUISITION, LAUNCH, SEASONAL, RETENTION
    channel = Column(String(80), default="Multi-Channel")
    objective = Column(Text, default="")
    funnel_stage = Column(String(60), default="TOFU/MOFU/BOFU")
    budget_planned = Column(Float, default=0.0)
    spend_real = Column(Float, default=0.0)
    revenue_attributed = Column(Float, default=0.0)
    roi_pct = Column(Float, default=0.0)
    leads_generated = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    data_origin = Column(String(30), default="REAL")  # REAL, IMPORTED, ESTIMATED, GOAL
    status = Column(String(40), default="ACTIVE")
    business_unit_code = Column(String(50), default="UNION_TECH", index=True)  # UNION_TECH, UNION_AGENCY, UNION_PARTNERS
    monthly_plan_json = Column(Text, default="{}")
    start_date = Column(String(40), default="")
    end_date = Column(String(40), default="")
    created_at = Column(DateTime, default=utcnow)


class SEOAuditReport(Base):
    __tablename__ = "seo_audit_reports"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    target_url = Column(String(500), nullable=False)
    status_code = Column(Integer, default=200)
    response_time_ms = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    title_tag = Column(String(500), default="")
    meta_description = Column(Text, default="")
    h1_tags_json = Column(Text, default="[]")
    h2_tags_json = Column(Text, default="[]")
    internal_links_count = Column(Integer, default=0)
    external_links_count = Column(Integer, default=0)
    images_missing_alt_count = Column(Integer, default=0)
    has_robots_txt = Column(Boolean, default=False)
    has_sitemap_xml = Column(Boolean, default=False)
    is_indexable = Column(Boolean, default=True)
    schema_org_types_json = Column(Text, default="[]")
    issues_json = Column(Text, default="[]")
    recommendations_json = Column(Text, default="[]")
    suggested_title = Column(String(300), default="")
    suggested_meta_description = Column(Text, default="")
    generated_schema_json = Column(Text, default="{}")
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class SEOKeywordCluster(Base):
    __tablename__ = "seo_keyword_clusters"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    seed_keyword = Column(String(255), nullable=False)
    search_intent = Column(String(60), default="COMMERCIAL")
    long_tail_keywords_json = Column(Text, default="[]")
    cluster_topics_json = Column(Text, default="[]")
    backlink_strategy_json = Column(Text, default="[]")
    source = Column(String(80), default="Autocomplete + Deterministic Semantic Analysis")
    created_at = Column(DateTime, default=utcnow)


class SEOArticle(Base):
    __tablename__ = "seo_articles"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(300), nullable=False)
    slug = Column(String(300), nullable=False)
    target_keyword = Column(String(200), nullable=False)
    search_intent = Column(String(60), default="INFORMATIONAL")
    meta_title = Column(String(200), nullable=False)
    meta_description = Column(String(320), nullable=False)
    outline_json = Column(Text, default="[]")
    content_markdown = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    keyword_density_pct = Column(Float, default=1.2)
    readability_score = Column(Float, default=85.0)
    internal_links_suggestions_json = Column(Text, default="[]")
    schema_json_ld = Column(Text, default="{}")
    status = Column(String(50), default="READY_FOR_REVIEW")
    created_at = Column(DateTime, default=utcnow)


class EditorialCalendarItem(Base):
    __tablename__ = "editorial_calendar_items"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)  # instagram, facebook, tiktok, youtube, linkedin, pinterest
    content_format = Column(String(50), default="POST")  # POST, CAROUSEL, REELS_SHORT, VIDEO, THUMBNAIL
    caption = Column(Text, nullable=False)
    hashtags_json = Column(Text, default="[]")
    media_asset_id = Column(Integer, nullable=True)
    video_script = Column(Text, default="")
    scheduled_for = Column(String(50), nullable=False)
    best_time_rationale = Column(String(255), default="")
    approval_status = Column(String(40), default="PENDING_REVIEW")  # PENDING_REVIEW, APPROVED, AUTO_APPROVED, REJECTED
    publish_status = Column(String(40), default="DRAFT")  # DRAFT, QUEUED, PUBLISHED, FAILED, WAITING_CREDENTIALS
    retry_count = Column(Integer, default=0)
    last_error = Column(Text, default="")
    external_post_id = Column(String(120), default="")
    metrics_json = Column(Text, default="{}")
    business_unit_code = Column(String(50), default="UNION_TECH", index=True)
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class CreativeAsset(Base):
    __tablename__ = "creative_assets"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    asset_type = Column(String(60), nullable=False)
    platform = Column(String(60), default="instagram")
    dimensions = Column(String(40), default="1080x1080")
    file_path = Column(String(500), default="")
    preview_data_uri = Column(Text, default="")
    content_json = Column(Text, default="{}")
    brand_palette_json = Column(Text, default="{}")
    license_info = Column(String(255), default="Original Generated Asset - Commercial Use Permitted (Royalty-Free)")
    is_approved = Column(Boolean, default=True)
    campaign_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class CopyItem(Base):
    __tablename__ = "copy_items"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    copy_type = Column(String(60), nullable=False)
    framework = Column(String(40), default="AIDA")
    tone = Column(String(60), default="Consultivo & Executivo")
    target_audience = Column(String(255), default="")
    variant_a = Column(Text, nullable=False)
    variant_b = Column(Text, nullable=False)
    ab_test_hypothesis = Column(Text, default="")
    compliance_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class GrowthExperiment(Base):
    __tablename__ = "growth_experiments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    channel = Column(String(80), nullable=False)
    hypothesis = Column(Text, nullable=False)
    objective = Column(String(255), nullable=False)
    target_audience = Column(String(255), default="")
    indicator_metric = Column(String(120), nullable=False)
    estimated_cost = Column(Float, default=0.0)
    baseline_conversion_pct = Column(Float, default=0.0)
    real_result_conversion_pct = Column(Float, nullable=True)
    real_result_summary = Column(Text, default="Aguardando coleta de dados reais do experimento")
    data_origin = Column(String(30), default="ESTIMATED")  # ESTIMATED until real result recorded -> REAL
    ice_score = Column(Float, default=8.0)
    status = Column(String(40), default="PLANNED")  # PLANNED, RUNNING, COMPLETED
    conclusion = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)


class CRMCompany(Base):
    __tablename__ = "crm_companies"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(200), nullable=False)
    industry = Column(String(120), default="")
    website = Column(String(255), default="")
    size = Column(String(60), default="PME")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)


class CRMLead(Base):
    __tablename__ = "crm_leads"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    full_name = Column(String(180), nullable=False)
    email = Column(String(255), index=True, nullable=False)
    phone = Column(String(60), default="")
    company_name = Column(String(180), default="")
    source_channel = Column(String(80), default="Organic SEO")
    buy_intent = Column(String(40), default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT
    lead_score = Column(Integer, default=50)
    qualification_status = Column(String(50), default="NEW")  # NEW, QUALIFIED, NURTURING, CONVERTED, INACTIVE
    pipeline_stage = Column(String(50), default="NEW_LEAD")  # NEW_LEAD, QUALIFICATION, PROPOSAL, NEGOTIATION, CLOSED_WON, CLOSED_LOST
    estimated_value = Column(Float, default=0.0)
    data_origin = Column(String(30), default="REAL")  # REAL, IMPORTED
    consent_lgpd = Column(Boolean, default=True)
    consent_source = Column(String(120), default="Opt-in Formulário / Cadastro Direto")
    opt_out = Column(Boolean, default=False)
    business_unit_code = Column(String(50), default="UNION_TECH", index=True)
    funnel_stage = Column(String(50), default="LEAD")  # VISITANTE, INTERESSADO, LEAD, QUALIFICADO, DIAGNOSTICO, PROPOSTA, NEGOCIACAO, GANHO, PERDIDO, POS_VENDA
    legal_basis = Column(String(80), default="CONSENTIMENTO_OPT_IN")
    purpose_description = Column(String(255), default="Atendimento comercial e envio de proposta solicitada")
    campaign_attribution = Column(String(120), default="")
    contact_blocked = Column(Boolean, default=False)
    lost_reason = Column(String(255), default="")
    reactivation_count = Column(Integer, default=0)
    outreach_draft_message = Column(Text, default="")
    outreach_approved_by_owner = Column(Boolean, default=False)
    last_outreach_at = Column(DateTime, nullable=True)
    last_contact_at = Column(DateTime, default=utcnow)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)


class CRMDeal(Base):
    __tablename__ = "crm_deals"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(220), nullable=False)
    stage = Column(String(50), default="PROPOSAL")  # NEW_LEAD, QUALIFICATION, PROPOSAL, NEGOTIATION, CLOSED_WON, CLOSED_LOST
    value = Column(Float, default=0.0)
    probability_pct = Column(Float, default=50.0)
    expected_close_date = Column(String(40), default="")
    status = Column(String(40), default="OPEN")  # OPEN, WON, LOST
    follow_up_plan_json = Column(Text, default="[]")
    business_unit_code = Column(String(50), default="UNION_TECH", index=True)
    offer_id = Column(Integer, nullable=True)
    proposal_id = Column(Integer, nullable=True)
    recurring_mrr_brl = Column(Float, default=0.0)
    one_time_setup_brl = Column(Float, default=0.0)
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class CRMActivity(Base):
    __tablename__ = "crm_activities"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=True)
    deal_id = Column(Integer, ForeignKey("crm_deals.id", ondelete="CASCADE"), nullable=True)
    activity_type = Column(String(50), default="FOLLOW_UP")  # CALL, EMAIL, WHATSAPP, MEETING, FOLLOW_UP, RECOVERY
    subject = Column(String(255), nullable=False)
    description = Column(Text, default="")
    due_date = Column(String(50), default="")
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(180), nullable=False)
    website_url = Column(String(500), nullable=False)
    category = Column(String(120), default="Concorrente Direto")
    public_pricing_summary = Column(Text, default="Não listado publicamente")
    positioning_summary = Column(Text, default="")
    strengths_json = Column(Text, default="[]")
    weaknesses_json = Column(Text, default="[]")
    differentiation_opportunities_json = Column(Text, default="[]")
    robots_txt_respected = Column(Boolean, default=True)
    last_analyzed_at = Column(DateTime, nullable=True)
    analysis_report_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=utcnow)


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    period_date = Column(String(30), index=True, nullable=False)
    record_type = Column(String(40), nullable=False)  # REVENUE, EXPENSE, AD_SPEND
    category = Column(String(100), default="Operacional")
    channel = Column(String(80), default="Direct")
    amount = Column(Float, nullable=False)
    data_origin = Column(String(30), default="REAL")  # REAL, IMPORTED, ESTIMATED, GOAL, PROJECTION
    business_unit_code = Column(String(50), default="UNION_TECH", index=True)
    revenue_status = Column(String(40), default="RECEIVED")  # RECEIVED, CONFIRMED, PENDING_RECONCILIATION, PROJECTED
    is_recurring = Column(Boolean, default=False)
    description = Column(String(300), default="")
    created_at = Column(DateTime, default=utcnow)


class CustomerFeedback(Base):
    __tablename__ = "customer_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    customer_name = Column(String(180), nullable=False)
    customer_email = Column(String(255), default="")
    nps_score = Column(Integer, default=9)  # 0-10
    csat_score = Column(Integer, default=5)  # 1-5
    sentiment = Column(String(40), default="POSITIVE")  # POSITIVE, NEUTRAL, NEGATIVE, CRITICAL
    churn_risk = Column(String(40), default="LOW")  # LOW, MEDIUM, HIGH
    recurring_issue_tag = Column(String(120), default="")
    feedback_text = Column(Text, nullable=False)
    retention_suggestion = Column(Text, default="")
    upsell_opportunity = Column(Text, default="")
    status = Column(String(40), default="OPEN")
    created_at = Column(DateTime, default=utcnow)


class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(220), nullable=False)
    code_key = Column(String(100), index=True, nullable=False)
    trigger_type = Column(String(50), default="CRON")  # CRON, EVENT, THRESHOLD
    cron_expression = Column(String(80), default="0 8 * * *")
    event_name = Column(String(100), default="")
    condition_json = Column(Text, default="{}")
    action_agent = Column(String(80), nullable=False)
    action_task = Column(String(120), nullable=False)
    frequency_label = Column(String(80), default="Diário")
    scheduled_time = Column(String(30), default="08:00")
    priority = Column(String(30), default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    owner_role = Column(String(60), default="AI Orchestrator")
    business_unit_code = Column(String(50), default="ALL", index=True)
    is_active = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=60)
    last_run_at = Column(DateTime, nullable=True)
    last_status = Column(String(40), default="READY")
    run_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)


class AutomationExecution(Base):
    __tablename__ = "automation_executions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    rule_id = Column(Integer, ForeignKey("automation_rules.id", ondelete="CASCADE"), index=True, nullable=False)
    idempotency_key = Column(String(160), index=True, nullable=False)
    status = Column(String(40), default="SUCCESS")  # RUNNING, SUCCESS, FAILED, RETRIED, BLOCKED
    attempt_number = Column(Integer, default=1)
    duration_ms = Column(Float, default=0.0)
    result_summary_json = Column(Text, default="{}")
    error_message = Column(Text, default="")
    started_at = Column(DateTime, default=utcnow)
    finished_at = Column(DateTime, default=utcnow)


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    agent_id = Column(String(80), nullable=False)
    action_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    payload_json = Column(Text, default="{}")
    autonomy_level_at_creation = Column(Integer, default=2)
    is_high_impact = Column(Boolean, default=False)
    status = Column(String(40), default="PENDING")  # PENDING, APPROVED, REJECTED, EXECUTED, FAILED
    reviewed_by_user_id = Column(Integer, nullable=True)
    review_notes = Column(Text, default="")
    execution_result_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=utcnow)
    reviewed_at = Column(DateTime, nullable=True)


class IntegrationConnection(Base):
    __tablename__ = "integration_connections"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    provider_key = Column(String(80), index=True, nullable=False)
    provider_name = Column(String(140), nullable=False)
    category = Column(String(80), default="Marketing & Analytics")
    status = Column(String(40), default="PENDING_CREDENTIALS")  # CONNECTED, PENDING_CREDENTIALS, ERROR, DISCONNECTED
    encrypted_credentials = Column(Text, default="")
    masked_credentials_preview = Column(String(120), default="")
    scopes_json = Column(Text, default="[]")
    account_identifier = Column(String(180), default="")
    last_tested_at = Column(DateTime, nullable=True)
    last_error = Column(Text, default="")
    updated_at = Column(DateTime, default=utcnow)


class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    workflow_run_id = Column(String(100), index=True, nullable=False)
    agent_id = Column(String(60), index=True, nullable=False)
    agent_name = Column(String(120), nullable=False)
    task_name = Column(String(140), nullable=False)
    parent_agent_id = Column(String(60), default="")
    autonomy_level = Column(Integer, default=2)
    provider_used = Column(String(180), default="deterministic-expert-engine")
    model_used = Column(String(100), default="rule-based-v1")
    processing_type = Column(String(50), default="DETERMINISTIC_PYTHON_ENGINE")  # REAL_LLM, LOCAL_MODEL, DETERMINISTIC_PYTHON_ENGINE, TEMPLATE_ENGINE, FALLBACK
    tokens_consumed = Column(Integer, default=0)
    estimated_cost_brl = Column(Float, default=0.0)
    input_payload_json = Column(Text, default="{}")
    output_payload_json = Column(Text, default="{}")
    quality_score = Column(Float, default=95.0)
    duration_ms = Column(Float, default=0.0)
    status = Column(String(40), default="COMPLETED")
    created_at = Column(DateTime, default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, nullable=True)
    actor = Column(String(120), default="system")
    action = Column(String(140), index=True, nullable=False)
    resource_type = Column(String(100), default="system")
    resource_id = Column(String(100), default="")
    ip_address = Column(String(80), default="127.0.0.1")
    details_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=utcnow)



class SchedulerHeartbeat(Base):
    """Persisted scheduler liveness evidence (survives restarts; used for 24/7 operational audit)."""

    __tablename__ = "scheduler_heartbeats"

    id = Column(Integer, primary_key=True, index=True)
    boot_id = Column(String(40), index=True, nullable=False)
    jobs_count = Column(Integer, default=0)
    kind = Column(String(30), default="HEARTBEAT")  # BOOT, HEARTBEAT, CATCHUP
    note = Column(String(300), default="")
    created_at = Column(DateTime, default=utcnow, index=True)


# ==============================================================================
# FASE 14 — CONTENT FACTORY, CEO DAILY PLAN, OPERATIONAL ALERTS & PILOT
# ==============================================================================
class ContentFactoryItem(Base):
    """Batch-generated omnichannel content produced by the UNION Content Factory."""

    __tablename__ = "content_factory_items"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    batch_id = Column(String(64), index=True, nullable=False)
    channel = Column(String(50), nullable=False)  # instagram, facebook, tiktok, youtube, linkedin, pinterest, blog_seo, email_marketing
    content_type = Column(String(50), nullable=False)  # POST, CAROUSEL, REELS_SHORT, YOUTUBE_SCRIPT, SEO_ARTICLE, SALES_EMAIL, SEASONAL_CAMPAIGN
    objective = Column(String(100), default="brand_awareness")
    target_audience = Column(String(150), default="Público Geral")
    title = Column(String(255), nullable=False)
    body_text = Column(Text, nullable=False)
    cta = Column(String(255), nullable=False)
    hashtags_json = Column(Text, default="[]")
    media_specs_json = Column(Text, default="{}")
    image_url = Column(String(500), default="")
    scheduled_for = Column(String(50), nullable=False)
    quality_score = Column(Integer, default=90)
    is_duplicate = Column(Boolean, default=False)
    similarity_hash = Column(String(64), default="")
    status = Column(String(40), default="PLANNED")  # PLANNED, APPROVED, QUEUED, PUBLISHED, ASSISTED_EXPORTED
    responsible_agent = Column(String(80), default="AGENT_04_SOCIAL")
    change_history_json = Column(Text, default="[]")
    published_post_id = Column(String(120), default="")
    business_unit_code = Column(String(50), default="UNION_TECH", index=True)
    utm_campaign = Column(String(120), default="")
    approval_status = Column(String(40), default="PENDING_REVIEW")
    data_origin = Column(String(30), default="GOAL")
    created_at = Column(DateTime, default=utcnow)


class CEODelegatedTask(Base):
    """Actionable delegated tasks assigned by the Autonomous Digital CEO to specialists."""

    __tablename__ = "ceo_delegated_tasks"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    briefing_date = Column(String(30), index=True, nullable=False)
    target_agent = Column(String(50), nullable=False)  # cmo, seo, social, creative, copywriter, growth, sales, finance
    title = Column(String(255), nullable=False)
    objective = Column(Text, nullable=False)
    priority = Column(String(20), default="HIGH")  # URGENT, HIGH, MEDIUM, LOW
    status = Column(String(30), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    deliverable = Column(Text, default="")
    action_type = Column(String(60), default="EXECUTE")
    created_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)


class OperationalAlert(Base):
    """Central operational alerts with severity, category, and actionable suggestions."""

    __tablename__ = "operational_alerts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    severity = Column(String(20), default="INFO")  # INFO, WARNING, CRITICAL
    category = Column(String(50), nullable=False)  # SCHEDULER, SOCIAL_API, DATABASE, SYSTEM, REVENUE, SEO
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    suggested_action = Column(Text, default="")
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    resolved_at = Column(DateTime, nullable=True)


class PilotOperationalRun(Base):
    """Audit log of 7-day autonomous pilot simulations and production runs."""

    __tablename__ = "pilot_operational_runs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    run_date = Column(String(30), nullable=False)
    day_number = Column(Integer, nullable=False)
    status = Column(String(30), default="COMPLETED")
    actions_executed_json = Column(Text, default="[]")
    metrics_summary_json = Column(Text, default="{}")
    errors_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=utcnow)


# ==============================================================================
# FASE 17 — OPERAÇÃO COMERCIAL MULTINEGÓCIO (UNION TECH, AGENCY, PARTNERS)
# ==============================================================================
class BusinessUnit(Base):
    """Unidades comerciais independentes integradas ao mesmo AI CEO."""

    __tablename__ = "business_units"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    code = Column(String(50), index=True, nullable=False)  # UNION_TECH, UNION_AGENCY, UNION_PARTNERS
    name = Column(String(180), nullable=False)
    business_type = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    target_audience = Column(Text, default="")
    value_proposition = Column(Text, default="")
    products_services_json = Column(Text, default="[]")
    acquisition_channels_json = Column(Text, default="[]")
    revenue_streams_json = Column(Text, default="[]")
    monthly_revenue_goal_brl = Column(Float, default=0.0)
    monthly_budget_brl = Column(Float, default=0.0)
    status = Column(String(40), default="ACTIVE")
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class ProductService(Base):
    """Catálogo comercial de produtos e serviços com calculadora dinâmica de custos e preços."""

    __tablename__ = "product_services"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    business_unit_code = Column(String(50), index=True, nullable=False)  # UNION_TECH, UNION_AGENCY, UNION_PARTNERS
    service_code = Column(String(60), index=True, nullable=False)  # SRV_01_DIAGNOSTICO, etc.
    name = Column(String(220), nullable=False)
    category = Column(String(120), default="IA & Automação")
    description = Column(Text, nullable=False)
    problem_solved = Column(Text, nullable=False)
    target_audience = Column(Text, nullable=False)
    benefits_json = Column(Text, default="[]")
    scope_summary = Column(Text, default="")
    deliverables_json = Column(Text, default="[]")
    estimated_timeline_days = Column(Integer, default=15)
    # Parâmetros da Calculadora Dinâmica de Precificação
    dev_hours_estimated = Column(Float, default=20.0)
    complexity_level = Column(String(40), default="MEDIUM")  # LOW, MEDIUM, HIGH, ENTERPRISE
    hourly_rate_brl = Column(Float, default=150.0)
    infra_cost_brl = Column(Float, default=0.0)
    tools_api_cost_brl = Column(Float, default=0.0)
    support_cost_brl = Column(Float, default=0.0)
    tax_rate_pct = Column(Float, default=12.0)
    target_margin_pct = Column(Float, default=45.0)
    # Resultados Calculados e Preço Configurável pelo Proprietário
    estimated_cost_brl = Column(Float, default=0.0)
    suggested_price_brl = Column(Float, default=0.0)
    configured_price_brl = Column(Float, default=0.0)
    recurring_monthly_brl = Column(Float, default=0.0)
    estimated_margin_pct = Column(Float, default=45.0)
    pricing_approved_by_owner = Column(Boolean, default=False)
    client_requirements_json = Column(Text, default="[]")
    direct_cost_brl = Column(Float, default=0.0)
    indirect_cost_brl = Column(Float, default=0.0)
    minimum_margin_pct = Column(Float, default=30.0)
    billing_model = Column(String(50), default="SETUP_PLUS_MRR")  # SETUP_ONLY, SETUP_PLUS_MRR, MONTHLY_RETAINER, MILESTONE_BASED
    recurrence_eligible = Column(Boolean, default=True)
    scope_limits = Column(Text, default="Escopo restrito aos entregáveis listados; integrações ou módulos adicionais sob orçamento complementar.")
    scope_included_json = Column(Text, default="[]")
    scope_excluded_json = Column(Text, default="[]")
    approval_criteria = Column(Text, default="Validação de escopo técnico, margem mínima >= 30% e aprovação expressa do proprietário.")
    commercial_terms = Column(Text, default="50% na assinatura e 50% na entrega homologada; ou assinatura recorrente mensal.")
    availability_status = Column(String(40), default="AVAILABLE")  # AVAILABLE, CUSTOM_QUOTE, PAUSED
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class CommercialOffer(Base):
    """Ofertas comerciais e pacotes estruturados por unidade de negócio."""

    __tablename__ = "commercial_offers"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    business_unit_code = Column(String(50), index=True, nullable=False)
    product_service_id = Column(Integer, ForeignKey("product_services.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(220), nullable=False)
    headline = Column(String(300), default="")
    offer_type = Column(String(50), default="HYBRID_SETUP_PLUS_MRR")  # ONE_TIME, RECURRING_PLAN, HYBRID_SETUP_PLUS_MRR
    plan_tier = Column(String(40), default="PRO")  # STARTER, PRO, BUSINESS, ENTERPRISE, CUSTOM
    setup_fee_brl = Column(Float, default=0.0)
    monthly_fee_brl = Column(Float, default=0.0)
    included_items_json = Column(Text, default="[]")
    limits_json = Column(Text, default="{}")
    payment_conditions = Column(String(255), default="PIX, Boleto Corporativo ou Cartão Empresarial")
    owner_approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class MarketOpportunity(Base):
    """Inteligência comercial e pesquisa de oportunidades por segmento de mercado."""

    __tablename__ = "market_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    business_unit_code = Column(String(50), default="UNION_TECH", index=True)
    segment = Column(String(120), index=True, nullable=False)  # Varejo, Restaurantes, Distribuidores, Clínicas, PMEs, E-commerce, etc.
    identified_problem = Column(Text, nullable=False)
    recommended_service_code = Column(String(60), nullable=False)
    recommended_service_name = Column(String(220), nullable=False)
    ideal_customer_profile = Column(Text, nullable=False)
    commercial_potential = Column(String(40), default="HIGH")  # MEDIUM, HIGH, VERY_HIGH
    implementation_difficulty = Column(String(40), default="MEDIUM")  # LOW, MEDIUM, HIGH
    priority = Column(String(30), default="HIGH")  # MEDIUM, HIGH, URGENT
    justification = Column(Text, nullable=False)
    information_source = Column(String(255), default="Mapeamento Setorial Determinístico + Sinais Públicos")
    opportunity_score = Column(Integer, default=85)
    problem_campaign_theme = Column(String(160), default="Automação de Atendimento & IA")
    researched_at = Column(String(40), nullable=False)
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class LandingPage(Base):
    """Landing pages comerciais independentes por unidade e serviço."""

    __tablename__ = "landing_pages"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    business_unit_code = Column(String(50), index=True, nullable=False)
    slug = Column(String(120), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    value_proposition = Column(Text, nullable=False)
    problem_statement = Column(Text, nullable=False)
    solution_summary = Column(Text, nullable=False)
    benefits_json = Column(Text, default="[]")
    real_example_description = Column(Text, default="")
    differentials_json = Column(Text, default="[]")
    cta_text = Column(String(180), default="Solicitar Diagnóstico Comercial")
    privacy_policy_summary = Column(Text, default="Seus dados são protegidos sob a LGPD (Lei 13.709/2018) e utilizados exclusivamente para retorno comercial autorizado, com opt-out imediato.")
    views_count = Column(Integer, default=0)
    leads_captured_count = Column(Integer, default=0)
    conversions_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class CommercialProposal(Base):
    """Gerador de propostas comerciais com ciclo de vida completo e trava de aprovação do proprietário."""

    __tablename__ = "commercial_proposals"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    business_unit_code = Column(String(50), index=True, nullable=False)
    proposal_number = Column(String(60), index=True, nullable=False)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="SET NULL"), nullable=True)
    service_code = Column(String(60), default="SRV_01_DIAGNOSTICO")
    company_issuer_name = Column(String(200), default="UNION GROWTH HOLDING LTDA")
    client_name = Column(String(180), nullable=False)
    client_company = Column(String(200), nullable=False)
    client_email = Column(String(255), nullable=False)
    identified_problem = Column(Text, nullable=False)
    proposed_solution = Column(Text, nullable=False)
    scope_details = Column(Text, nullable=False)
    deliverables_json = Column(Text, default="[]")
    timeline_schedule_json = Column(Text, default="[]")
    setup_price_brl = Column(Float, default=0.0)
    monthly_price_brl = Column(Float, default=0.0)
    total_contract_value_brl = Column(Float, default=0.0)
    payment_terms = Column(String(255), default="50% no aceite e 50% na entrega final + mensalidade recorrente a partir de D+30.")
    validity_days = Column(Integer, default=10)
    conditions_and_limitations = Column(Text, default="Proposta sujeita a validação técnica de escopo. Não inclui custos de APIs pagas de terceiros ou compra de tráfego pago.")
    next_steps = Column(Text, default="1. Aprovação formal da proposta; 2. Assinatura do contrato; 3. Reunião de Kickoff Técnico.")
    status = Column(String(40), default="DRAFT")  # DRAFT, PENDING_APPROVAL, SENT, VIEWED, NEGOTIATION, ACCEPTED, REJECTED, EXPIRED
    owner_approved = Column(Boolean, default=False)
    approved_by_user_id = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    diagnosis_summary = Column(Text, default="")
    version_number = Column(Integer, default=1)
    version_history_json = Column(Text, default="[]")
    contract_terms = Column(Text, default="Cláusulas padrão de prestação de serviços de tecnologia, confidencialidade (NDA), LGPD e SLA de suporte.")
    contract_status = Column(String(50), default="DRAFT")  # DRAFT, PENDING_REVIEW, APPROVED_BY_OWNER, ACCEPTED_WITH_EVIDENCE
    acceptance_evidence = Column(String(300), default="")
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class AgencyClientAccount(Base):
    """Contas isoladas de empresas clientes atendidas pela unidade UNION AGENCY."""

    __tablename__ = "agency_client_accounts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    business_unit_code = Column(String(50), default="UNION_AGENCY", index=True)
    client_name = Column(String(200), nullable=False)
    brand_name = Column(String(180), nullable=False)
    slug = Column(String(120), index=True, nullable=False)
    segment = Column(String(120), default="PME & Serviços")
    target_audience = Column(Text, default="")
    products_json = Column(Text, default="[]")
    objectives_json = Column(Text, default="[]")
    communication_tone = Column(String(120), default="Profissional, Consultivo e Orientado a Resultados")
    plan_tier = Column(String(40), default="PRO")  # STARTER, PRO, BUSINESS, ENTERPRISE
    setup_fee_brl = Column(Float, default=0.0)
    monthly_retainer_brl = Column(Float, default=0.0)
    connected_networks_json = Column(Text, default="[]")
    campaigns_count = Column(Integer, default=0)
    contents_count = Column(Integer, default=0)
    leads_count = Column(Integer, default=0)
    status = Column(String(40), default="ACTIVE")  # ONBOARDING, ACTIVE, AT_RISK, PAUSED
    owner_approved_pricing = Column(Boolean, default=False)
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class AffiliateProgram(Base):
    """Programas de afiliados e parcerias comerciais gerenciados pela unidade UNION PARTNERS."""

    __tablename__ = "affiliate_programs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    business_unit_code = Column(String(50), default="UNION_PARTNERS", index=True)
    name = Column(String(180), nullable=False)
    platform = Column(String(80), index=True, nullable=False)  # mercado_livre, amazon, shopee, digital_tools, tech_partners
    approval_status = Column(String(40), default="PENDING_CREDENTIALS")  # PENDING_CREDENTIALS, APPROVED, ACTIVE, REJECTED
    credentials_status = Column(String(60), default="PENDING_CREDENTIALS")
    rules_summary = Column(Text, default="")
    default_commission_pct = Column(Float, default=8.0)
    attribution_window_days = Column(Integer, default=7)
    payment_conditions = Column(String(255), default="Repasse conforme calendário oficial da plataforma após confirmação da venda.")
    limitations = Column(Text, default="Comissão somente devida após faturamento definitivo e ausência de devolução/cancelamento.")
    official_api_status = Column(String(120), default="Requer token/credencial de afiliado oficial")
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class AffiliateProduct(Base):
    """Produtos e ferramentas curados para recomendação e comparação pela UNION PARTNERS."""

    __tablename__ = "affiliate_products"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    business_unit_code = Column(String(50), default="UNION_PARTNERS", index=True)
    program_id = Column(Integer, ForeignKey("affiliate_programs.id", ondelete="CASCADE"), index=True, nullable=False)
    platform = Column(String(80), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(120), default="Tecnologia & Produtividade")
    brand = Column(String(120), default="")
    observed_price_brl = Column(Float, default=0.0)
    price_source = Column(String(180), default="Cadastro Manual / Consulta Autorizada")
    observed_at = Column(String(40), nullable=False)
    availability_status = Column(String(50), default="AVAILABLE")  # AVAILABLE, OUT_OF_STOCK, UNVERIFIED
    authorized_url = Column(String(500), nullable=False)
    affiliate_url = Column(String(500), nullable=False)
    tracking_code = Column(String(80), index=True, nullable=False)
    commission_pct = Column(Float, default=8.0)
    estimated_commission_brl = Column(Float, default=0.0)
    curation_score = Column(Float, default=85.0)
    comparison_notes = Column(Text, default="")
    disclosure_label = Column(String(255), default="PUBLICIDADE / LINK DE AFILIADO: Podemos receber comissão sem custo adicional para o comprador.")
    offer_status = Column(String(40), default="ACTIVE")
    clicks_count = Column(Integer, default=0)
    confirmed_conversions_count = Column(Integer, default=0)
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)


class AffiliateClick(Base):
    """Registro auditável de cliques em links rastreáveis (NUNCA contabilizado como venda)."""

    __tablename__ = "affiliate_clicks"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("affiliate_products.id", ondelete="CASCADE"), index=True, nullable=False)
    program_id = Column(Integer, ForeignKey("affiliate_programs.id", ondelete="CASCADE"), index=True, nullable=False)
    tracking_code = Column(String(80), index=True, nullable=False)
    source_channel = Column(String(80), default="Direct")
    utm_campaign = Column(String(120), default="")
    visitor_fingerprint = Column(String(120), default="")
    clicked_at = Column(DateTime, default=utcnow)


class AffiliateConversion(Base):
    """Registro de conversões e conciliação de comissões de afiliados."""

    __tablename__ = "affiliate_conversions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("affiliate_products.id", ondelete="CASCADE"), index=True, nullable=False)
    program_id = Column(Integer, ForeignKey("affiliate_programs.id", ondelete="CASCADE"), index=True, nullable=False)
    click_id = Column(Integer, ForeignKey("affiliate_clicks.id", ondelete="SET NULL"), nullable=True)
    external_order_id = Column(String(120), index=True, nullable=False)
    sale_amount_brl = Column(Float, default=0.0)
    commission_amount_brl = Column(Float, default=0.0)
    commission_status = Column(String(40), default="PENDING_CONFIRMATION")  # ESTIMATED, PENDING_CONFIRMATION, APPROVED, PAID, REJECTED
    attribution_evidence = Column(String(300), default="")
    reconciled_in_finance = Column(Boolean, default=False)
    financial_record_id = Column(Integer, nullable=True)
    data_origin = Column(String(30), default="REAL")
    converted_at = Column(DateTime, default=utcnow)
    reconciled_at = Column(DateTime, nullable=True)


# ==============================================================================
# FASE 18 — PAGAMENTOS (MERCADO PAGO & SANDBOX), WEBHOOKS & ONBOARDING/ENTREGA
# ==============================================================================
class PaymentTransaction(Base):
    """
    Transações de cobrança e recebimento comercial (Mercado Pago API / Sandbox).
    REGRA DE OURO: Nunca marcar como receita recebida sem confirmação verificável (APPROVED).
    Nunca armazenar dados completos de cartão (PCI Safety).
    """

    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    business_unit_code = Column(String(50), default="UNION_TECH", index=True)
    proposal_id = Column(Integer, ForeignKey("commercial_proposals.id", ondelete="SET NULL"), nullable=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="SET NULL"), nullable=True)
    client_name = Column(String(180), nullable=False)
    client_company = Column(String(200), default="")
    client_email = Column(String(255), nullable=False)
    provider = Column(String(60), default="mercado_pago")
    external_reference = Column(String(120), index=True, nullable=False)
    provider_payment_id = Column(String(120), index=True, default="")
    idempotency_key = Column(String(160), unique=True, index=True, nullable=False)
    amount_brl = Column(Float, nullable=False)
    payment_method = Column(String(50), default="PIX")  # PIX, BOLETO, CHECKOUT_PRO
    payment_link_url = Column(String(500), default="")
    execution_mode = Column(String(40), default="SANDBOX")  # SANDBOX, PRODUCTION_API, PENDING_CREDENTIALS
    status = Column(String(40), default="PENDING")  # PENDING, APPROVED, REJECTED, CANCELLED, REFUNDED, DISPUTED
    owner_approved = Column(Boolean, default=False)
    webhook_signature_verified = Column(Boolean, default=False)
    webhook_events_json = Column(Text, default="[]")
    receipt_number = Column(String(80), default="")
    reconciled_in_finance = Column(Boolean, default=False)
    financial_record_id = Column(Integer, nullable=True)
    onboarding_project_id = Column(Integer, nullable=True)
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow)
    paid_at = Column(DateTime, nullable=True)


class ServiceDeliveryProject(Base):
    """Projetos de Onboarding e Entrega Técnica acionados após confirmação de pagamento/contrato."""

    __tablename__ = "service_delivery_projects"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    business_unit_code = Column(String(50), default="UNION_TECH", index=True)
    project_code = Column(String(60), index=True, nullable=False)
    proposal_id = Column(Integer, ForeignKey("commercial_proposals.id", ondelete="SET NULL"), nullable=True)
    payment_id = Column(Integer, ForeignKey("payment_transactions.id", ondelete="SET NULL"), nullable=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id", ondelete="SET NULL"), nullable=True)
    client_name = Column(String(180), nullable=False)
    client_company = Column(String(200), nullable=False)
    client_email = Column(String(255), nullable=False)
    service_code = Column(String(60), nullable=False)
    service_name = Column(String(220), nullable=False)
    contracted_scope = Column(Text, nullable=False)
    responsible_owner = Column(String(120), default="Diretoria de Engenharia & IA (UNION TECH)")
    tasks_json = Column(Text, default="[]")
    milestones_json = Column(Text, default="[]")
    required_documents_json = Column(Text, default="[]")
    onboarding_checklist_json = Column(Text, default="[]")
    deliverables_json = Column(Text, default="[]")
    client_validation_status = Column(String(40), default="PENDING")  # PENDING, REQUESTED, APPROVED_BY_CLIENT
    client_validation_notes = Column(Text, default="")
    execution_evidence = Column(Text, default="")
    status = Column(String(40), default="ONBOARDING")  # ONBOARDING, IN_PROGRESS, WAITING_CLIENT, DELIVERED, COMPLETED
    progress_pct = Column(Float, default=15.0)
    due_date = Column(String(40), default="")
    data_origin = Column(String(30), default="REAL")
    created_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)


# ==============================================================================
# FASE 19 — UNION AI ENGINE HUB (PROVIDERS, MODELS, CREDENTIALS, ROUTER, USAGE, MEDIA)
# ==============================================================================
class AIProviderRecord(Base):
    """Registro central de provedores de Inteligência Artificial por Tenant."""

    __tablename__ = "ai_provider_records"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    provider_key = Column(String(60), index=True, nullable=False)  # gemini, openai, anthropic, groq, openrouter, openai_compatible
    name = Column(String(160), nullable=False)
    provider_class = Column(String(100), nullable=False)  # GeminiProvider, OpenAIProvider, AnthropicProvider, GroqProvider, OpenRouterProvider, GenericOpenAICompatibleProvider
    base_url = Column(String(500), default="")
    is_enabled = Column(Boolean, default=True)
    is_priority_default = Column(Boolean, default=False)
    # VERIFIED_FREE, OWNER_DECLARED_FREE, PAID, UNKNOWN_COST
    cost_tier = Column(String(40), default="UNKNOWN_COST")
    owner_permitted_free = Column(Boolean, default=False)
    owner_approved_paid = Column(Boolean, default=False)
    status = Column(String(40), default="PENDING_API_KEY")  # CONNECTED, READY_WITH_KEY, PENDING_API_KEY, DISABLED, ERROR
    capabilities_json = Column(Text, default="{}")
    known_quotas_json = Column(Text, default="{}")
    limitations_text = Column(Text, default="")
    cost_notes = Column(Text, default="")
    daily_request_limit = Column(Integer, default=500)
    monthly_request_limit = Column(Integer, default=10000)
    daily_token_limit = Column(Integer, default=250000)
    last_tested_at = Column(DateTime, nullable=True)
    last_test_status = Column(String(40), default="NOT_TESTED")
    last_error = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow)


class AIModelRecord(Base):
    """Catálogo configurável e atualizável de modelos de IA e suas capacidades individuais."""

    __tablename__ = "ai_model_records"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    provider_key = Column(String(60), index=True, nullable=False)
    model_id = Column(String(140), index=True, nullable=False)
    display_name = Column(String(180), nullable=False)
    modality = Column(String(40), default="TEXT")  # TEXT, IMAGE, VIDEO, AUDIO, MULTIMODAL
    capabilities_json = Column(Text, default="{}")
    # VERIFIED_FREE, OWNER_DECLARED_FREE, PAID, UNKNOWN_COST
    cost_tier = Column(String(40), default="UNKNOWN_COST")
    owner_permitted_free = Column(Boolean, default=False)
    owner_approved_paid = Column(Boolean, default=False)
    input_cost_per_1k_usd = Column(Float, nullable=True)
    output_cost_per_1k_usd = Column(Float, nullable=True)
    image_unit_cost_usd = Column(Float, nullable=True)
    video_second_cost_usd = Column(Float, nullable=True)
    known_quota_note = Column(Text, default="")
    limitations_note = Column(Text, default="")
    commercial_use_allowed = Column(Boolean, default=True)
    is_enabled = Column(Boolean, default=True)
    is_default_for_modality = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)


class AICredentialRecord(Base):
    """Central de Credenciais de IA com criptografia Fernet em repouso e isolamento multi-tenant."""

    __tablename__ = "ai_credential_records"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    provider_key = Column(String(60), index=True, nullable=False)
    label = Column(String(140), default="Chave Principal")
    encrypted_api_key = Column(Text, default="")
    masked_key_preview = Column(String(100), default="")
    custom_endpoint_url = Column(String(500), default="")
    extra_headers_json = Column(Text, default="{}")
    is_active = Column(Boolean, default=True)
    last_tested_at = Column(DateTime, nullable=True)
    last_test_status = Column(String(40), default="NOT_TESTED")
    last_error = Column(Text, default="")
    updated_by_user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow)


class AIEngineConfigurationRecord(Base):
    """Configuração global, por tarefa e por agente do AI Router e políticas FREE_ONLY / OWNER_APPROVED."""

    __tablename__ = "ai_engine_configurations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    default_provider_key = Column(String(60), default="gemini")
    default_text_model = Column(String(140), default="gemini-2.5-flash")
    default_image_provider = Column(String(60), default="gemini")
    default_image_model = Column(String(140), default="imagen-3.0-generate-002")
    default_video_provider = Column(String(60), default="gemini")
    default_video_model = Column(String(140), default="veo-2.0-generate-001")
    # FREE_ONLY or OWNER_APPROVED
    cost_policy_mode = Column(String(40), default="FREE_ONLY")
    allow_fallback = Column(Boolean, default=True)
    allow_paid_fallback = Column(Boolean, default=False)
    fallback_order_json = Column(Text, default='["gemini", "groq", "openrouter"]')
    task_routing_json = Column(Text, default="{}")
    agent_routing_json = Column(Text, default="{}")
    limits_json = Column(Text, default="{}")
    updated_at = Column(DateTime, default=utcnow)


class AIEngineExecutionRecord(Base):
    """Rastreabilidade completa de cada execução de IA, tokens, tempo, status e classificação de custo."""

    __tablename__ = "ai_engine_executions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    execution_uuid = Column(String(80), unique=True, index=True, nullable=False)
    task_type = Column(String(80), index=True, nullable=False)
    modality = Column(String(40), default="TEXT")
    agent_id = Column(String(60), default="AI_ENGINE_HUB")
    requested_provider = Column(String(60), nullable=False)
    requested_model = Column(String(140), nullable=False)
    executed_provider = Column(String(60), default="")
    executed_model = Column(String(140), default="")
    fallback_used = Column(Boolean, default=False)
    # VERIFIED_FREE, OWNER_DECLARED_FREE, PAID, UNKNOWN_COST, SIMULATION
    cost_classification = Column(String(40), default="VERIFIED_FREE")
    # REAL_PROVIDER_API, BLOCKED_POLICY, BLOCKED_CAPABILITY, FAILED_PROVIDER
    execution_origin = Column(String(60), default="REAL_PROVIDER_API")
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    images_generated = Column(Integer, default=0)
    videos_generated = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, nullable=True)
    estimated_cost_brl = Column(Float, nullable=True)
    confirmed_cost_brl = Column(Float, nullable=True)
    duration_ms = Column(Float, default=0.0)
    status = Column(String(50), default="SUCCESS")  # SUCCESS, FAILED, BLOCKED_FREE_ONLY, BLOCKED_CAPABILITY, BLOCKED_LIMIT, PENDING_API_KEY
    error_message = Column(Text, default="")
    prompt_preview = Column(Text, default="")
    output_preview = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)


class AIFallbackRecord(Base):
    """Registro auditável de tentativas de fallback entre provedores."""

    __tablename__ = "ai_fallback_records"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    execution_uuid = Column(String(80), index=True, nullable=False)
    task_type = Column(String(80), default="text_generation")
    primary_provider = Column(String(60), nullable=False)
    primary_model = Column(String(140), nullable=False)
    failure_reason = Column(Text, nullable=False)
    fallback_provider = Column(String(60), default="")
    fallback_model = Column(String(140), default="")
    fallback_authorized = Column(Boolean, default=False)
    final_status = Column(String(50), default="FAILED")
    created_at = Column(DateTime, default=utcnow)


class AICampaignPackageRecord(Base):
    """Pacotes completos de campanha e peças individuais gerados pelo UNION AI ENGINE HUB."""

    __tablename__ = "ai_campaign_packages"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    package_uuid = Column(String(80), unique=True, index=True, nullable=False)
    generation_scope = Column(String(40), default="FULL_CAMPAIGN")  # FULL_CAMPAIGN, SINGLE_PIECE
    piece_type = Column(String(50), default="ALL")  # ALL, POST, IMAGE, VIDEO, COPY, EMAIL, ARTICLE, LANDING_PAGE, CAROUSEL, AD, SCRIPT, SEO, CTA
    campaign_name = Column(String(240), nullable=False)
    objective = Column(String(180), default="")
    target_audience = Column(Text, default="")
    product_or_offer = Column(String(240), default="")
    channel = Column(String(80), default="Multi-Channel")
    provider_used = Column(String(60), default="")
    model_used = Column(String(140), default="")
    execution_origin = Column(String(60), default="REAL_PROVIDER_API")
    cost_classification = Column(String(40), default="VERIFIED_FREE")
    package_data_json = Column(Text, default="{}")
    status = Column(String(40), default="GENERATED")
    linked_campaign_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class AIMediaGenerationRecord(Base):
    """
    Histórico do AI IMAGE STUDIO e AI VIDEO STUDIO.
    Separa estritamente:
    - Para vídeo: SCRIPT_ONLY, STORYBOARD_ONLY, PIPELINE_ASSEMBLED_VIDEO, RENDERED_VIDEO, PROVIDER_GENERATED_VIDEO, WAITING_PROCESSING.
    - Para imagem: PROVIDER_GENERATED_IMAGE, PROMPT_ONLY, FAILED.
    """

    __tablename__ = "ai_media_generations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    media_uuid = Column(String(80), unique=True, index=True, nullable=False)
    media_type = Column(String(30), index=True, nullable=False)  # IMAGE, VIDEO
    delivery_stage = Column(String(50), nullable=False)  # SCRIPT_ONLY, STORYBOARD_ONLY, PIPELINE_ASSEMBLED_VIDEO, RENDERED_VIDEO, PROVIDER_GENERATED_VIDEO, WAITING_PROCESSING, PROVIDER_GENERATED_IMAGE, PROMPT_ONLY
    provider_key = Column(String(60), nullable=False)
    model_id = Column(String(140), nullable=False)
    prompt = Column(Text, nullable=False)
    style = Column(String(80), default="Corporate Modern")
    format_ext = Column(String(30), default="PNG")
    aspect_ratio = Column(String(30), default="1:1")
    resolution = Column(String(40), default="1024x1024")
    variations_count = Column(Integer, default=1)
    commercial_use_allowed = Column(Boolean, default=True)
    license_summary = Column(String(255), default="Subject to Provider Terms")
    file_url = Column(String(500), default="")
    preview_data_uri = Column(Text, default="")
    script_text = Column(Text, default="")
    storyboard_json = Column(Text, default="[]")
    narration_text = Column(Text, default="")
    subtitles_json = Column(Text, default="[]")
    linked_campaign_id = Column(Integer, nullable=True)
    linked_editorial_id = Column(Integer, nullable=True)
    cost_classification = Column(String(40), default="VERIFIED_FREE")
    status = Column(String(40), default="COMPLETED")
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)


class BrandVersionRecord(Base):
    """Histórico versionado da Central de Inteligência de Marca (Fase 23)."""

    __tablename__ = "brand_versions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    version_number = Column(Integer, default=1, nullable=False)
    snapshot_json = Column(Text, nullable=False, default="{}")
    consistency_score = Column(Integer, default=100)
    inconsistencies_json = Column(Text, default="[]")
    notes = Column(String(255), default="Snapshot da identidade e diretrizes de marca")
    created_by = Column(String(255), default="")
    created_at = Column(DateTime, default=utcnow)


class AskUnionActionLog(Base):
    """Registro auditável do copiloto conversacional ASK UNION e ações executadas (Fase 23)."""

    __tablename__ = "ask_union_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    user_email = Column(String(255), default="")
    prompt = Column(Text, nullable=False)
    intent_classified = Column(String(80), default="GENERAL_GROWTH")
    response_json = Column(Text, default="{}")
    executed_actions_json = Column(Text, default="[]")
    status = Column(String(40), default="COMPLETED")
    created_at = Column(DateTime, default=utcnow)


class ReleaseRecord(Base):
    """Histórico oficial e rastreável de releases SemVer em PostgreSQL (Fase 27)."""

    __tablename__ = "release_records"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(40), unique=True, index=True, nullable=False)
    git_tag = Column(String(50), default="")
    release_date = Column(String(40), default="")
    phase_label = Column(String(50), default="")
    commit_sha = Column(String(80), default="")
    environment = Column(String(40), default="production")
    deploy_status = Column(String(40), default="PUBLISHED")
    title = Column(String(255), nullable=False)
    features_json = Column(Text, default="[]")
    fixes_json = Column(Text, default="[]")
    security_json = Column(Text, default="[]")
    tests_summary = Column(String(255), default="")
    audit_score = Column(Float, nullable=True)
    readiness_status = Column(String(40), default="PRODUCTION_READY")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class SystemAuditSnapshot(Base):
    """Snapshot persistente das auditorias de 25 categorias baseadas em evidência (Fase 27)."""

    __tablename__ = "system_audit_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    version = Column(String(40), nullable=False)
    git_commit = Column(String(80), default="")
    environment = Column(String(40), default="production")
    global_score = Column(Float, nullable=False)
    readiness_status = Column(String(40), nullable=False)  # NOT_READY, DEVELOPMENT, BETA, PRODUCTION_READY, SCALE_READY
    categories_json = Column(Text, nullable=False, default="[]")
    traceability_matrix_json = Column(Text, nullable=False, default="[]")
    blockers_json = Column(Text, nullable=False, default="[]")
    next_actions_json = Column(Text, nullable=False, default="[]")
    triggered_by = Column(String(255), default="system")
    created_at = Column(DateTime, default=utcnow)


class GrowthPlanRecord(Base):
    """Plano de Execução de Crescimento persistido por empresa/tenant (Fase 27)."""

    __tablename__ = "growth_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_uuid = Column(String(60), unique=True, index=True, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    objective = Column(String(300), nullable=False)
    product_or_service = Column(String(220), default="")
    target_audience = Column(String(220), default="")
    region = Column(String(120), default="Brasil")
    budget_brl = Column(Float, default=0.0)
    target_goal = Column(String(220), default="")
    deadline_days = Column(Integer, default=90)
    real_baseline_json = Column(Text, default="{}")
    status = Column(String(40), default="ACTIVE")
    created_by = Column(String(255), default="")
    created_at = Column(DateTime, default=utcnow)


class GrowthPlanStepRecord(Base):
    """Etapa acionável do Plano de Crescimento com status, responsável, prazo e evidência (Fase 27)."""

    __tablename__ = "growth_plan_steps"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("growth_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), index=True, nullable=False)
    step_key = Column(String(80), nullable=False)
    horizon = Column(String(30), index=True, nullable=False)  # TODAY, NEXT_7_DAYS, NEXT_30_DAYS, NEXT_90_DAYS
    horizon_label = Column(String(60), default="")
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    action_type = Column(String(80), nullable=False)
    priority_score = Column(Float, default=80.0)
    impact_score = Column(Integer, default=8)
    confidence_score = Column(Integer, default=8)
    effort_score = Column(Integer, default=3)
    cost_brl = Column(Float, default=0.0)
    risk_level = Column(String(30), default="BAIXO")
    time_estimate = Column(String(80), default="1 min")
    owner_label = Column(String(120), default="AI Growth Director + Proprietário")
    due_date = Column(String(40), default="")
    dependencies_json = Column(Text, default="[]")
    success_metric = Column(String(255), default="")
    data_source = Column(String(120), default="PostgreSQL Real Snapshot")
    evidence_text = Column(Text, default="")
    next_action = Column(String(255), default="")
    probability_pct = Column(Float, default=70.0)
    probability_origin = Column(String(30), default="ESTIMATED")
    can_auto_execute = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    status = Column(String(40), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, CANCELLED, REQUIRES_CREDENTIALS
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)




