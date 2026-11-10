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
    data_origin = Column(String(30), default="REAL")  # REAL, IMPORTED, ESTIMATED, GOAL
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
    provider_used = Column(String(80), default="deterministic-expert-engine")
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

