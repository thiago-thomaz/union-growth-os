from typing import Any, Literal
from pydantic import BaseModel, EmailStr, Field


DataOriginType = Literal["REAL", "IMPORTED", "ESTIMATED", "GOAL", "PROJECTION", "SIMULATION", "TEST", "DEMO"]
BusinessUnitCodeType = Literal["UNION_TECH", "UNION_AGENCY", "UNION_PARTNERS", "ALL"]
AutonomyLevelType = Literal[1, 2, 3]
PlanTierType = Literal["FREE", "STARTER", "PRO", "BUSINESS", "ENTERPRISE"]


# --- Auth & Multi-Tenant ---
class UserRegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)
    full_name: str
    company_name: str
    brand_name: str | None = None
    domain: str = ""
    niche: str = "Tecnologia & Negócios Digitais"
    lgpd_consent: bool = True


class UserLoginRequest(BaseModel):
    email: str
    password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=10)


class TenantCreateRequest(BaseModel):
    name: str
    brand_name: str
    domain: str = ""
    niche: str = "B2B & SaaS"
    primary_color: str = "#6366F1"
    secondary_color: str = "#10B981"
    target_audience: str = "Empresas em expansão"
    plan_tier: PlanTierType = "ENTERPRISE"


class TenantUpdateRequest(BaseModel):
    name: str | None = None
    brand_name: str | None = None
    domain: str | None = None
    niche: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    target_audience: str | None = None
    strategy_summary: str | None = None
    plan_tier: PlanTierType | None = None
    autonomy_default_level: AutonomyLevelType | None = None
    agent_autonomy: dict[str, int] | None = None
    products: list[str] | None = None
    services: list[str] | None = None
    ui_mode: Literal["SIMPLE", "ADVANCED"] | None = None
    brand_voice: str | None = None
    brand_fonts: str | None = None
    brand_differentials: str | None = None
    brand_allowed_terms: str | None = None
    brand_forbidden_terms: str | None = None
    brand_examples: str | None = None
    brand_country: str | None = None
    brand_description: str | None = None
    growth_goals: list[str] | None = None
    onboarding_step: int | None = None
    onboarding_state: dict[str, Any] | None = None


class UserRoleUpdateRequest(BaseModel):
    role: Literal["owner", "admin", "manager", "analyst", "viewer"]


class LGPDPreferencesRequest(BaseModel):
    lgpd_consent: bool
    marketing_opt_in: bool
    preferences: dict[str, Any] = {}


# --- Inter-Agent Typed Communication Contracts ---
class AgentTaskContract(BaseModel):
    workflow_run_id: str
    sender_agent: str
    target_agent: str
    task_name: str
    tenant_id: int
    autonomy_level: AutonomyLevelType = 2
    parameters: dict[str, Any] = {}
    max_depth: int = 3
    current_depth: int = 0
    timeout_seconds: int = 30


class AgentResponseContract(BaseModel):
    workflow_run_id: str
    agent_id: str
    agent_name: str
    task_name: str
    status: Literal["COMPLETED", "PENDING_APPROVAL", "BLOCKED", "FAILED"]
    autonomy_level: AutonomyLevelType
    provider_used: str
    response_origin: str = "HYBRID_DETERMINISTIC_AND_TEMPLATE"
    llm_used: bool = False
    quality_score: float = Field(ge=0.0, le=100.0)
    data_origin: DataOriginType = "REAL"
    summary: str
    structured_output: dict[str, Any]
    recommendations: list[str] = []
    requires_human_approval: bool = False
    approval_request_id: int | None = None


# --- Module Requests ---
class StrategicGoalCreate(BaseModel):
    title: str
    period: Literal["MONTHLY", "QUARTERLY", "ANNUAL"] = "MONTHLY"
    metric_name: str
    target_value: float
    current_value: float = 0.0
    unit: str = "BRL"
    data_origin: DataOriginType = "GOAL"
    financial_impact_score: float = 85.0
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "HIGH"
    deadline: str = ""


class MarketingPersonaCreate(BaseModel):
    name: str
    role_segment: str
    demographics: str = ""
    pains: list[str] = []
    desires: list[str] = []
    objections: list[str] = []
    channels: list[str] = []
    value_proposition: str = ""


class MarketingCampaignCreate(BaseModel):
    name: str
    campaign_type: Literal["ACQUISITION", "LAUNCH", "SEASONAL", "RETENTION", "RECOVERY"] = "ACQUISITION"
    channel: str = "Multi-Channel"
    objective: str
    funnel_stage: str = "Full-Funnel"
    budget_planned: float = 0.0
    spend_real: float = 0.0
    revenue_attributed: float = 0.0
    leads_generated: int = 0
    conversions: int = 0
    data_origin: DataOriginType = "REAL"
    start_date: str = ""
    end_date: str = ""
    confirmation_token: str | None = None


class SEOAuditRequest(BaseModel):
    target_url: str
    target_keyword: str = ""


class SEOKeywordResearchRequest(BaseModel):
    seed_keyword: str
    niche: str = ""


class SEOArticleGenerateRequest(BaseModel):
    topic: str
    target_keyword: str
    search_intent: Literal["INFORMATIONAL", "COMMERCIAL", "TRANSACTIONAL", "NAVIGATIONAL"] = "INFORMATIONAL"
    target_word_count: int = 900


class EditorialItemCreate(BaseModel):
    title: str
    platform: Literal["instagram", "facebook", "tiktok", "youtube", "linkedin", "pinterest", "blog", "email"]
    content_format: Literal["POST", "CAROUSEL", "REELS_SHORT", "VIDEO", "STORY", "THUMBNAIL", "ARTICLE", "PIN"] = "POST"
    caption: str = ""
    hashtags: list[str] = []
    video_script: str = ""
    scheduled_for: str
    auto_generate_copy: bool = True


class CreativeAssetGenerateRequest(BaseModel):
    title: str
    asset_type: Literal[
        "SOCIAL_POST",
        "BANNER",
        "COVER",
        "CAROUSEL",
        "INFOGRAPHIC",
        "THUMBNAIL",
        "AD_CREATIVE",
        "PRESENTATION",
        "EBOOK",
        "VIDEO_SCRIPT",
        "SHORT_VIDEO",
        "INSTITUTIONAL_VIDEO",
    ] = "SOCIAL_POST"
    platform: str = "instagram"
    headline_text: str
    subheadline_text: str = ""
    cta_text: str = "Saiba Mais"
    campaign_id: int | None = None


class CopyGenerateRequest(BaseModel):
    title: str
    copy_type: Literal[
        "HEADLINE",
        "CTA",
        "LANDING_PAGE",
        "SALES_PAGE",
        "AD_COPY",
        "EMAIL_SEQUENCE",
        "SALES_SCRIPT",
        "WHATSAPP_MESSAGE",
        "PRODUCT_DESCRIPTION",
        "SEO_TEXT",
    ] = "LANDING_PAGE"
    framework: Literal["AIDA", "PAS", "BAB", "FAB", "4PS", "STORYBRAND"] = "AIDA"
    product_or_offer: str
    target_audience: str
    key_benefit: str
    tone: str = "Executivo, claro e persuasivo"


class GrowthExperimentCreate(BaseModel):
    title: str
    channel: str
    hypothesis: str
    objective: str
    target_audience: str = ""
    indicator_metric: str = "Taxa de Conversão (%)"
    estimated_cost: float = 0.0
    baseline_conversion_pct: float = 2.0
    real_result_conversion_pct: float | None = None
    impact: int = Field(default=8, ge=1, le=10)
    confidence: int = Field(default=8, ge=1, le=10)
    ease: int = Field(default=8, ge=1, le=10)


class GrowthExperimentUpdateResult(BaseModel):
    real_result_conversion_pct: float
    real_result_summary: str
    conclusion: str
    status: Literal["RUNNING", "COMPLETED", "ARCHIVED"] = "COMPLETED"


class CRMLeadCreate(BaseModel):
    full_name: str
    email: str
    phone: str = ""
    company_name: str = ""
    source_channel: str = "Organic SEO"
    buy_intent: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] = "HIGH"
    estimated_value: float = 0.0
    consent_lgpd: bool = True
    consent_source: str = "Opt-in Formulário Oficial"
    legal_basis: str = "CONSENTIMENTO_OPT_IN"
    purpose_description: str = "Atendimento comercial e envio de proposta solicitada"
    campaign_attribution: str = ""
    business_unit_code: str = "UNION_TECH"
    funnel_stage: str = "LEAD"
    notes: str = ""
    data_origin: DataOriginType = "REAL"


class CRMDealCreate(BaseModel):
    lead_id: int | None = None
    title: str
    stage: Literal["NEW_LEAD", "QUALIFICATION", "PROPOSAL", "NEGOTIATION", "CLOSED_WON", "CLOSED_LOST"] = "PROPOSAL"
    value: float
    probability_pct: float = 60.0
    expected_close_date: str = ""
    business_unit_code: str = "UNION_TECH"
    offer_id: int | None = None
    proposal_id: int | None = None
    recurring_mrr_brl: float = 0.0
    one_time_setup_brl: float = 0.0
    data_origin: DataOriginType = "REAL"


class CompetitorCreate(BaseModel):
    name: str
    website_url: str
    category: str = "Concorrente Direto"


class FinancialRecordCreate(BaseModel):
    period_date: str
    record_type: Literal["REVENUE", "EXPENSE", "AD_SPEND"]
    category: str = "Operacional"
    channel: str = "Direct"
    amount: float
    business_unit_code: str = "UNION_TECH"
    revenue_status: Literal["RECEIVED", "CONFIRMED", "PENDING_RECONCILIATION", "PROJECTED"] = "RECEIVED"
    is_recurring: bool = False
    data_origin: DataOriginType = "REAL"
    description: str = ""


class CustomerFeedbackCreate(BaseModel):
    customer_name: str
    customer_email: str = ""
    nps_score: int = Field(default=9, ge=0, le=10)
    csat_score: int = Field(default=5, ge=1, le=5)
    feedback_text: str


class AutomationRuleCreate(BaseModel):
    name: str
    code_key: str
    trigger_type: Literal["CRON", "EVENT", "THRESHOLD"] = "CRON"
    cron_expression: str = "0 8 * * *"
    event_name: str = ""
    condition: dict[str, Any] = {}
    action_agent: str
    action_task: str
    frequency_label: str = "Diário"
    scheduled_time: str = "08:00"
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "HIGH"
    max_retries: int = 3
    timeout_seconds: int = 60


class IntegrationConnectRequest(BaseModel):
    provider_key: str
    credentials: dict[str, Any]
    account_identifier: str = ""
    scopes: list[str] = []


class ApprovalDecisionRequest(BaseModel):
    decision: Literal["APPROVE", "REJECT"]
    review_notes: str = ""
    confirmation_token: str | None = None


class CompanyOnboardingRequest(BaseModel):
    name: str
    segment: str
    description: str
    products: list[str] = []
    services: list[str] = []
    target_audience: str
    region: str = "Brasil (Nacional)"
    competitors: list[dict[str, str]] = []
    visual_identity: dict[str, str] = {
        "brand_name": "",
        "primary_color": "#6366F1",
        "secondary_color": "#10B981",
        "tone_of_voice": "Consultivo, Técnico e Orientado a Resultados",
    }
    website: str = ""
    social_networks: dict[str, str] = {}
    commercial_goals: list[dict[str, Any]] = []
    create_new_tenant: bool = False


class AutonomyConfigUpdateRequest(BaseModel):
    autonomy_default_level: AutonomyLevelType = 2
    agent_autonomy: dict[str, int] = {}
    limits: dict[str, Any] = {
        "max_daily_publications": 10,
        "max_daily_messages": 100,
        "max_campaign_budget_brl": 5000.0,
        "max_active_campaigns": 10,
        "allow_commercial_changes": False,
        "allow_external_actions": False,
        "require_approval_for_financial_actions": True,
    }


class FullMarketingOperationRequest(BaseModel):
    campaign_name: str = "Campanha Integrada 360º — Aquisição & Autoridade Digital"
    product_or_offer: str = ""
    target_keyword: str = ""
    platforms: list[str] = ["instagram", "linkedin", "youtube", "blog"]
    budget_planned_brl: float = 0.0
    auto_approve_execution: bool = True
    confirmation_token: str | None = None


# ==============================================================================
# FASE 14 — SCHEMAS: CONTENT FACTORY, CEO PLAN, OPERATIONAL & PILOT
# ==============================================================================
class ContentFactoryBatchGenerateRequest(BaseModel):
    company_name: str = ""
    niche: str = ""
    target_audience: str = ""
    business_unit_code: str = ""
    utm_campaign: str = ""
    focus_theme: str = ""
    replace_drafts: bool = False
    persona_id: int | None = None
    campaign_id: int | None = None
    count: int = 30
    platforms: list[str] = [
        "instagram",
        "facebook",
        "tiktok",
        "youtube",
        "linkedin",
        "pinterest",
        "blog_seo",
        "email_marketing",
    ]


class ContentFactoryItemResponse(BaseModel):
    id: int
    batch_id: str
    business_unit_code: str = "UNION_TECH"
    utm_campaign: str = ""
    approval_status: str = "PENDING_REVIEW"
    channel: str
    content_type: str
    objective: str
    target_audience: str
    title: str
    body_text: str
    cta: str
    hashtags: list[str] = []
    media_specs: dict[str, Any] = {}
    image_url: str = ""
    scheduled_for: str
    quality_score: int
    is_duplicate: bool
    status: str
    responsible_agent: str = "AGENT_04_SOCIAL"
    change_history: list[dict[str, Any]] = []
    published_post_id: str = ""
    data_origin: str = "GOAL"
    created_at: str


class ContentFactoryBatchResponse(BaseModel):
    batch_id: str
    total_generated: int
    items_by_channel: dict[str, int]
    items_by_type: dict[str, int]
    average_quality_score: float
    duplicates_prevented: int
    items: list[ContentFactoryItemResponse]


class AssistedPublishingPackageResponse(BaseModel):
    item_id: int
    channel: str
    title: str
    formatted_copy_for_clipboard: str
    hashtags_formatted: str
    media_download_url: str
    recommended_best_time: str
    platform_upload_url: str
    checklist: list[str]


class CEODelegatedTaskResponse(BaseModel):
    id: int
    briefing_date: str
    target_agent: str
    title: str
    objective: str
    priority: str
    status: str
    deliverable: str = ""
    action_type: str = "EXECUTE"
    created_at: str
    completed_at: str | None = None


class CEODailyPlanResponse(BaseModel):
    briefing_date: str
    headline: str
    total_tasks: int
    tasks_pending: int
    tasks_completed: int
    tasks: list[CEODelegatedTaskResponse]


class CEOTaskUpdateRequest(BaseModel):
    status: str
    deliverable: str = ""


class WeeklySEORoutineResponse(BaseModel):
    tenant_id: int
    audit_score: int
    core_web_vitals: dict[str, Any]
    keywords_monitored_count: int
    top_opportunities: list[dict[str, Any]]
    schema_org_valid: bool
    sitemap_status: str
    robots_status: str
    recommendations: list[str]
    generated_at: str


class OperationalDashboardResponse(BaseModel):
    vps_status: dict[str, Any]
    coolify_status: dict[str, Any]
    git_info: dict[str, Any]
    database_status: dict[str, Any]
    scheduler_status: dict[str, Any]
    daily_routines_status: list[dict[str, Any]]
    social_queue_summary: dict[str, int]
    business_kpis: dict[str, Any]
    alerts_count: int


class OperationalAlertResponse(BaseModel):
    id: int
    severity: str
    category: str
    title: str
    message: str
    suggested_action: str
    is_resolved: bool
    created_at: str


class PilotRunResponse(BaseModel):
    day_number: int
    date: str
    status: str
    actions_count: int
    actions: list[str]
    metrics: dict[str, Any]


class PilotSummaryResponse(BaseModel):
    tenant_id: int
    days_simulated: int
    total_content_pieces_produced: int
    total_seo_routines_executed: int
    total_leads_qualified: int
    total_ceo_briefings: int
    zero_unexpected_costs: bool
    all_days_healthy: bool
    daily_runs: list[PilotRunResponse]


class ResourceCostsResponse(BaseModel):
    tenant_id: int
    database_records_total: int
    estimated_db_size_mb: float
    ai_engine_calls_total: int
    ai_deterministic_calls: int
    ai_llm_calls: int
    external_api_costs_brl: float
    currency: str = "BRL"
    verdict: str


# ==============================================================================
# FASE 17 — SCHEMAS: MULTI-BUSINESS COMMERCIAL OPERATION
# ==============================================================================
class ProductServicePricingUpdateRequest(BaseModel):
    dev_hours_estimated: float | None = None
    complexity_level: Literal["LOW", "MEDIUM", "HIGH", "ENTERPRISE"] | None = None
    hourly_rate_brl: float | None = None
    infra_cost_brl: float | None = None
    tools_api_cost_brl: float | None = None
    support_cost_brl: float | None = None
    tax_rate_pct: float | None = None
    target_margin_pct: float | None = None
    configured_price_brl: float | None = None
    recurring_monthly_brl: float | None = None
    owner_approve_pricing: bool = False
    force_owner_override: bool = False
    commercial_terms: str | None = None


class CommercialOfferCreateRequest(BaseModel):
    business_unit_code: Literal["UNION_TECH", "UNION_AGENCY", "UNION_PARTNERS"] = "UNION_TECH"
    product_service_id: int | None = None
    name: str
    headline: str = ""
    offer_type: Literal["ONE_TIME", "RECURRING_PLAN", "HYBRID_SETUP_PLUS_MRR"] = "HYBRID_SETUP_PLUS_MRR"
    plan_tier: Literal["STARTER", "PRO", "BUSINESS", "ENTERPRISE", "CUSTOM"] = "PRO"
    setup_fee_brl: float = 0.0
    monthly_fee_brl: float = 0.0
    included_items: list[str] = []
    limits: dict[str, Any] = {}
    payment_conditions: str = "PIX, Boleto Corporativo ou Cartão Empresarial"
    owner_approved: bool = False
    data_origin: DataOriginType = "REAL"


class LandingPageCaptureLeadRequest(BaseModel):
    landing_page_slug: str
    full_name: str
    email: str
    phone: str = ""
    company_name: str = ""
    buy_intent: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] = "HIGH"
    estimated_value: float = 0.0
    consent_lgpd: bool = True
    purpose_description: str = "Solicitação de diagnóstico e proposta comercial via Landing Page"
    utm_campaign: str = ""
    notes: str = ""
    data_origin: DataOriginType = "REAL"


class LeadFunnelStageUpdateRequest(BaseModel):
    funnel_stage: Literal[
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
        "GANHO",
        "PERDIDO",
        "POS_VENDA",
    ]
    lost_reason: str = ""
    notes: str = ""


class CommercialProposalCreateRequest(BaseModel):
    business_unit_code: Literal["UNION_TECH", "UNION_AGENCY", "UNION_PARTNERS"] = "UNION_TECH"
    lead_id: int | None = None
    service_code: str = "SRV_01_DIAGNOSTICO"
    client_name: str
    client_company: str
    client_email: str
    identified_problem: str
    diagnosis_summary: str = ""
    proposed_solution: str = ""
    scope_details: str = ""
    deliverables: list[str] = []
    timeline_schedule: list[str] = []
    setup_price_brl: float = 0.0
    monthly_price_brl: float = 0.0
    validity_days: int = 10
    payment_terms: str = "50% na assinatura e 50% na entrega homologada + recorrência mensal."
    contract_terms: str = ""
    data_origin: DataOriginType = "REAL"


class CommercialProposalStatusUpdateRequest(BaseModel):
    status: Literal[
        "DRAFT",
        "PENDING_APPROVAL",
        "SENT",
        "VIEWED",
        "NEGOTIATION",
        "ACCEPTED",
        "REJECTED",
        "EXPIRED",
    ]
    owner_approve: bool = False
    acceptance_evidence: str = ""
    confirmation_token: str | None = None


class AgencyClientAccountCreateRequest(BaseModel):
    client_name: str
    brand_name: str
    segment: str = "PME & Serviços"
    target_audience: str = "Clientes B2B e B2C regionais"
    products: list[str] = []
    objectives: list[str] = ["Geração de Leads", "Posicionamento SEO", "Gestão de Redes Sociais"]
    communication_tone: str = "Profissional, Consultivo e Orientado a Resultados"
    plan_tier: PlanTierType = "PRO"
    setup_fee_brl: float = 0.0
    monthly_retainer_brl: float = 0.0
    owner_approved_pricing: bool = False
    data_origin: DataOriginType = "REAL"


class AffiliateProductCreateRequest(BaseModel):
    program_id: int
    name: str
    category: str = "Tecnologia & Produtividade"
    brand: str = ""
    observed_price_brl: float
    price_source: str = "Consulta Direta na Página Oficial da Plataforma"
    availability_status: Literal["AVAILABLE", "OUT_OF_STOCK", "UNVERIFIED"] = "AVAILABLE"
    authorized_url: str
    affiliate_url: str
    commission_pct: float = 8.0
    comparison_notes: str = ""
    data_origin: DataOriginType = "REAL"


class AffiliateClickRecordRequest(BaseModel):
    tracking_code: str
    source_channel: str = "Blog / Content Factory"
    utm_campaign: str = ""
    visitor_fingerprint: str = ""


class AffiliateConversionRecordRequest(BaseModel):
    product_id: int
    click_id: int | None = None
    external_order_id: str
    sale_amount_brl: float
    commission_amount_brl: float
    commission_status: Literal["ESTIMATED", "PENDING_CONFIRMATION", "APPROVED", "PAID", "REJECTED"] = "PENDING_CONFIRMATION"
    attribution_evidence: str = "Relatório de Pedido na Plataforma"
    data_origin: DataOriginType = "REAL"


class AffiliateCommissionReconcileRequest(BaseModel):
    commission_status: Literal["APPROVED", "PAID", "REJECTED"]
    attribution_evidence: str
    confirmation_token: str | None = None


class MarketOpportunityResearchRequest(BaseModel):
    segment: str = "Varejo"
    business_unit_code: Literal["UNION_TECH", "UNION_AGENCY", "UNION_PARTNERS"] = "UNION_TECH"
    custom_focus: str = ""


# ==============================================================================
# FASE 18 — SCHEMAS: PAGAMENTOS (MERCADO PAGO & SANDBOX), WEBHOOKS & ONBOARDING
# ==============================================================================
class PaymentChargeCreateRequest(BaseModel):
    proposal_id: int | None = None
    lead_id: int | None = None
    business_unit_code: Literal["UNION_TECH", "UNION_AGENCY", "UNION_PARTNERS"] = "UNION_TECH"
    client_name: str
    client_company: str = ""
    client_email: str
    amount_brl: float = Field(gt=0.0)
    payment_method: Literal["PIX", "BOLETO", "CHECKOUT_PRO"] = "PIX"
    idempotency_key: str = ""
    sandbox_mode: bool = True
    owner_approved: bool = False
    data_origin: DataOriginType = "REAL"


class PaymentWebhookNotificationRequest(BaseModel):
    external_reference: str
    provider_payment_id: str
    new_status: Literal["PENDING", "APPROVED", "REJECTED", "CANCELLED", "REFUNDED", "DISPUTED"]
    amount_brl: float | None = None
    event_id: str = ""
    signature: str = ""


class ServiceDeliveryProjectCreateRequest(BaseModel):
    proposal_id: int | None = None
    payment_id: int | None = None
    lead_id: int | None = None
    business_unit_code: Literal["UNION_TECH", "UNION_AGENCY", "UNION_PARTNERS"] = "UNION_TECH"
    client_name: str
    client_company: str
    client_email: str
    service_code: str = "SRV_01_DIAGNOSTICO"
    contracted_scope: str = ""
    due_date: str = ""
    data_origin: DataOriginType = "REAL"


class ServiceDeliveryUpdateRequest(BaseModel):
    status: Literal["ONBOARDING", "IN_PROGRESS", "WAITING_CLIENT", "DELIVERED", "COMPLETED"] | None = None
    progress_pct: float | None = None
    client_validation_status: Literal["PENDING", "REQUESTED", "APPROVED_BY_CLIENT"] | None = None
    client_validation_notes: str | None = None
    execution_evidence: str | None = None
    completed_checklist_step: str | None = None
    deliverable_submitted: str | None = None


class LeadReactivationRequest(BaseModel):
    authorization_basis: str = "Opt-in prévio válido e ausência de opt-out (LGPD)"
    custom_message_notes: str = ""


class LeadOutreachPrepRequest(BaseModel):
    service_code: str = "SRV_01_DIAGNOSTICO"
    custom_angle: str = ""
    owner_approve_outreach: bool = False


# ==============================================================================
# FASE 23 — SCHEMAS: COMMAND CENTER, ASK UNION, BRAND INTELLIGENCE, ONBOARDING & CONVERSATIONAL AUTOMATION
# ==============================================================================
class BrandIntelligenceUpdateRequest(BaseModel):
    brand_name: str | None = None
    domain: str | None = None
    niche: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    brand_voice: str | None = None
    brand_fonts: str | None = None
    brand_differentials: str | None = None
    brand_allowed_terms: str | None = None
    brand_forbidden_terms: str | None = None
    brand_examples: str | None = None
    brand_description: str | None = None
    target_audience: str | None = None
    strategy_summary: str | None = None
    products: list[str] | None = None
    services: list[str] | None = None
    notes: str = "Atualização via Central de Inteligência de Marca"


class ProgressiveOnboardingStepRequest(BaseModel):
    step: int = Field(ge=1, le=6)
    save_only: bool = False
    reset_onboarding: bool = False
    data: dict[str, Any] = {}


class AskUnionRequest(BaseModel):
    prompt: str = Field(min_length=2, max_length=2000)
    auto_execute_safe: bool = False


class AskUnionExecuteActionRequest(BaseModel):
    log_id: int | None = None
    action_id: str
    decision: Literal["EXECUTE", "APPROVE", "REJECT", "SCHEDULE"] = "EXECUTE"


class ExecutiveActionDecisionRequest(BaseModel):
    action_id: str
    decision: Literal["EXECUTE", "SCHEDULE", "APPROVE", "REJECT"] = "EXECUTE"


class ConversationalAutomationRequest(BaseModel):
    prompt: str = Field(min_length=4, max_length=1500)
    dry_run: bool = True
    approve_create: bool = False






