import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.agents.orchestrator import (
    AGENT_AI_CAPABILITY_AUDIT,
    AGENT_REGISTRY,
    AIUsageTracker,
    CentralOrchestrator,
    MultiProviderAIAdapter,
    calculate_tenant_financial_kpis,
    compute_lead_score,
    generate_ceo_daily_briefing_service,
    get_effective_autonomy_level,
    get_tenant_autonomy_config,
)
from app.core.database import check_db_health, create_database_backup, get_db
from app.core.security import (
    check_login_allowed,
    clear_login_failures,
    create_access_token,
    generate_high_impact_token,
    get_active_tenant_id,
    get_current_user,
    hash_password,
    register_login_failure,
    require_roles,
    sanitize_text,
    user_must_change_password,
    validate_strong_password,
    verify_high_impact_token,
    verify_password,
)
from app.models.entities import (
    AgentExecutionLog,
    ApprovalRequest,
    AuditLog,
    AutomationExecution,
    AutomationRule,
    CEODailyBriefing,
    Competitor,
    CopyItem,
    CreativeAsset,
    CRMActivity,
    CRMCompany,
    CRMDeal,
    CRMLead,
    CustomerFeedback,
    EditorialCalendarItem,
    FinancialRecord,
    GrowthExperiment,
    IntegrationConnection,
    MarketingCampaign,
    MarketingPersona,
    SEOArticle,
    SEOAuditReport,
    SEOKeywordCluster,
    StrategicGoal,
    Tenant,
    User,
)
from app.schemas.contracts import (
    AgentTaskContract,
    ApprovalDecisionRequest,
    AutomationRuleCreate,
    AutonomyConfigUpdateRequest,
    CompanyOnboardingRequest,
    CompetitorCreate,
    CopyGenerateRequest,
    CreativeAssetGenerateRequest,
    CRMDealCreate,
    CRMLeadCreate,
    CustomerFeedbackCreate,
    EditorialItemCreate,
    FinancialRecordCreate,
    FullMarketingOperationRequest,
    GrowthExperimentCreate,
    GrowthExperimentUpdateResult,
    IntegrationConnectRequest,
    LGPDPreferencesRequest,
    MarketingCampaignCreate,
    MarketingPersonaCreate,
    PasswordChangeRequest,
    SEOArticleGenerateRequest,
    SEOAuditRequest,
    SEOKeywordResearchRequest,
    StrategicGoalCreate,
    TenantCreateRequest,
    TenantUpdateRequest,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.services.automation_scheduler import (
    ensure_tenant_automations_seeded,
    execute_automation_rule,
    get_scheduler_status,
    trigger_event_automations,
)
from app.services.creative_and_copy_engine import generate_creative_asset, generate_persuasive_copy
from app.services.integrations_and_social_engine import (
    INTEGRATION_CATALOG,
    audit_social_platforms_detailed,
    build_oauth_authorization_url,
    ensure_tenant_integrations_seeded,
    save_integration_credentials,
    test_integration_connection,
    validate_and_publish_social_item,
)
from app.services.phase13_services import (
    build_autonomy_panel,
    build_operational_log,
    check_autonomy_limit,
    run_company_onboarding,
    run_full_marketing_pipeline,
    save_autonomy_config,
    verify_all_automations,
)
from app.services.plans_and_audit import SAAS_PLANS, get_tenant_plan_info, record_audit_log
from app.services.seo_and_market_engine import (
    analyze_competitor_public,
    generate_seo_factory_article,
    perform_real_seo_audit,
    research_keywords_and_clusters,
)

router = APIRouter(prefix="/api/v1")


def _get_tenant_or_404(db: Session, tenant_id: int) -> Tenant:
    t = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Empresa (Tenant) não encontrada.")
    return t


# ==============================================================================
# 1. AUTHENTICATION, RBAC, LGPD & MULTI-TENANT MANAGEMENT
# ==============================================================================
@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register_user_and_tenant(payload: UserRegisterRequest, request: Request, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    ok_pwd, pwd_msg = validate_strong_password(payload.password)
    if not ok_pwd:
        raise HTTPException(status_code=400, detail=pwd_msg)
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado no sistema.")

    base_slug = re.sub(r"[^a-z0-9]+", "-", payload.company_name.lower()).strip("-") or "empresa"
    slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

    tenant = Tenant(
        name=sanitize_text(payload.company_name),
        slug=slug,
        brand_name=sanitize_text(payload.brand_name or payload.company_name),
        domain=sanitize_text(payload.domain),
        niche=sanitize_text(payload.niche),
        plan_tier="ENTERPRISE",
        autonomy_default_level=2,
        owner_email=email,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    user = User(
        tenant_id=tenant.id,
        email=email,
        full_name=sanitize_text(payload.full_name),
        hashed_password=hash_password(payload.password),
        role="owner",
        is_active=True,
        lgpd_consent=payload.lgpd_consent,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    ensure_tenant_integrations_seeded(db, tenant.id)
    ensure_tenant_automations_seeded(db, tenant.id)
    generate_ceo_daily_briefing_service(db, tenant)

    record_audit_log(
        db,
        tenant_id=tenant.id,
        user_id=user.id,
        actor=user.email,
        action="USER_AND_TENANT_REGISTERED",
        resource_type="tenant",
        resource_id=str(tenant.id),
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    token = create_access_token({"sub": str(user.id), "tenant_id": tenant.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "tenant_id": tenant.id,
            "lgpd_consent": user.lgpd_consent,
        },
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "brand_name": tenant.brand_name,
            "slug": tenant.slug,
            "plan_tier": tenant.plan_tier,
            "autonomy_default_level": tenant.autonomy_default_level,
        },
    }


@router.post("/auth/login")
def login_user(payload: UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    check_login_allowed(request, email)
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        register_login_failure(request, email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")
    clear_login_failures(request, email)

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    tenant = _get_tenant_or_404(db, user.tenant_id)
    record_audit_log(
        db,
        tenant_id=tenant.id,
        user_id=user.id,
        actor=user.email,
        action="USER_LOGIN_SUCCESS",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else "127.0.0.1",
    )

    token = create_access_token({"sub": str(user.id), "tenant_id": tenant.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "must_change_password": user_must_change_password(user),
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "tenant_id": tenant.id,
            "lgpd_consent": user.lgpd_consent,
        },
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "brand_name": tenant.brand_name,
            "slug": tenant.slug,
            "plan_tier": tenant.plan_tier,
            "autonomy_default_level": tenant.autonomy_default_level,
        },
    }


@router.post("/auth/change-password")
def change_password(
    payload: PasswordChangeRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta.")
    ok_pwd, msg = validate_strong_password(payload.new_password)
    if not ok_pwd:
        raise HTTPException(status_code=400, detail=msg)
    if verify_password(payload.new_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="A nova senha deve ser diferente da atual.")
    user.hashed_password = hash_password(payload.new_password)
    try:
        prefs = json.loads(user.preferences_json or "{}")
    except Exception:
        prefs = {}
    prefs["must_change_password"] = False
    prefs["password_changed_at"] = datetime.now(timezone.utc).isoformat()
    user.preferences_json = json.dumps(prefs, ensure_ascii=False)
    db.commit()
    record_audit_log(
        db,
        tenant_id=user.tenant_id,
        user_id=user.id,
        actor=user.email,
        action="PASSWORD_CHANGED",
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else "127.0.0.1",
    )
    return {"status": "password_changed", "must_change_password": False}


@router.get("/auth/me")
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    owned_tenants = db.query(Tenant).filter(Tenant.owner_email == user.email).all()
    if not owned_tenants:
        owned_tenants = [tenant]
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "tenant_id": tid,
            "lgpd_consent": user.lgpd_consent,
            "marketing_opt_in": user.marketing_opt_in,
            "must_change_password": user_must_change_password(user),
        },
        "active_tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "brand_name": tenant.brand_name,
            "slug": tenant.slug,
            "domain": tenant.domain,
            "niche": tenant.niche,
            "primary_color": tenant.primary_color,
            "secondary_color": tenant.secondary_color,
            "target_audience": tenant.target_audience,
            "plan_tier": tenant.plan_tier,
            "autonomy_default_level": tenant.autonomy_default_level,
            "agent_autonomy": get_tenant_autonomy_config(tenant)["agent_autonomy"],
            "autonomy_limits": get_tenant_autonomy_config(tenant)["limits"],
            "products": json.loads(tenant.products_json or "[]"),
            "services": json.loads(tenant.services_json or "[]"),
        },
        "available_tenants": [
            {"id": t.id, "name": t.name, "brand_name": t.brand_name, "plan_tier": t.plan_tier}
            for t in owned_tenants
        ],
        "plans_catalog": SAAS_PLANS,
        "high_impact_confirmation_token": generate_high_impact_token(user.id, tid, "CRITICAL_ACTION"),
    }


@router.put("/auth/lgpd-preferences")
def update_lgpd_preferences(
    payload: LGPDPreferencesRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    user.lgpd_consent = payload.lgpd_consent
    user.marketing_opt_in = payload.marketing_opt_in
    user.preferences_json = json.dumps(payload.preferences, ensure_ascii=False)
    db.commit()
    record_audit_log(
        db,
        tenant_id=tid,
        user_id=user.id,
        actor=user.email,
        action="LGPD_PREFERENCES_UPDATED",
        details={"lgpd_consent": payload.lgpd_consent, "marketing_opt_in": payload.marketing_opt_in},
    )
    return {"status": "updated", "lgpd_consent": user.lgpd_consent, "marketing_opt_in": user.marketing_opt_in}


@router.get("/tenants")
def list_user_tenants(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenants = db.query(Tenant).filter(Tenant.owner_email == user.email).all()
    if not tenants:
        tenants = [_get_tenant_or_404(db, user.tenant_id)]
    return [
        {
            "id": t.id,
            "name": t.name,
            "brand_name": t.brand_name,
            "slug": t.slug,
            "domain": t.domain,
            "niche": t.niche,
            "plan_tier": t.plan_tier,
            "autonomy_default_level": t.autonomy_default_level,
        }
        for t in tenants
    ]


@router.post("/tenants", status_code=status.HTTP_201_CREATED)
def create_additional_tenant(
    payload: TenantCreateRequest,
    user: User = Depends(require_roles("owner", "admin")),
    db: Session = Depends(get_db),
):
    slug = f"{re.sub(r'[^a-z0-9]+', '-', payload.name.lower()).strip('-')}-{uuid.uuid4().hex[:6]}"
    t = Tenant(
        name=sanitize_text(payload.name),
        slug=slug,
        brand_name=sanitize_text(payload.brand_name),
        domain=sanitize_text(payload.domain),
        niche=sanitize_text(payload.niche),
        primary_color=payload.primary_color,
        secondary_color=payload.secondary_color,
        target_audience=sanitize_text(payload.target_audience),
        plan_tier=payload.plan_tier,
        autonomy_default_level=2,
        owner_email=user.email,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    ensure_tenant_integrations_seeded(db, t.id)
    ensure_tenant_automations_seeded(db, t.id)
    generate_ceo_daily_briefing_service(db, t)
    record_audit_log(db, tenant_id=t.id, user_id=user.id, actor=user.email, action="TENANT_CREATED", resource_id=str(t.id))
    return {"id": t.id, "name": t.name, "brand_name": t.brand_name, "slug": t.slug, "plan_tier": t.plan_tier}


@router.put("/tenants/current")
def update_current_tenant(
    payload: TenantUpdateRequest,
    user: User = Depends(require_roles("owner", "admin")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    if payload.name is not None:
        tenant.name = sanitize_text(payload.name)
    if payload.brand_name is not None:
        tenant.brand_name = sanitize_text(payload.brand_name)
    if payload.domain is not None:
        tenant.domain = sanitize_text(payload.domain)
    if payload.niche is not None:
        tenant.niche = sanitize_text(payload.niche)
    if payload.primary_color is not None:
        tenant.primary_color = payload.primary_color
    if payload.secondary_color is not None:
        tenant.secondary_color = payload.secondary_color
    if payload.target_audience is not None:
        tenant.target_audience = sanitize_text(payload.target_audience)
    if payload.strategy_summary is not None:
        tenant.strategy_summary = sanitize_text(payload.strategy_summary)
    if payload.plan_tier is not None:
        tenant.plan_tier = payload.plan_tier
    if payload.autonomy_default_level is not None:
        tenant.autonomy_default_level = payload.autonomy_default_level
    if payload.agent_autonomy is not None:
        try:
            existing_cfg = json.loads(tenant.agent_autonomy_json or "{}")
        except Exception:
            existing_cfg = {}
        merged_cfg = {k: v for k, v in payload.agent_autonomy.items() if k in AGENT_REGISTRY}
        if "_limits" in existing_cfg:
            merged_cfg["_limits"] = existing_cfg["_limits"]
        tenant.agent_autonomy_json = json.dumps(merged_cfg, ensure_ascii=False)
    if payload.products is not None:
        tenant.products_json = json.dumps(payload.products, ensure_ascii=False)
    if payload.services is not None:
        tenant.services_json = json.dumps(payload.services, ensure_ascii=False)
    db.commit()
    record_audit_log(db, tenant_id=tid, user_id=user.id, actor=user.email, action="TENANT_SETTINGS_UPDATED")
    return {"status": "updated", "tenant_id": tenant.id, "autonomy_default_level": tenant.autonomy_default_level}


# ==============================================================================
# 2. EXECUTIVE DASHBOARD & OVERVIEW (VISÃO GERAL)
# ==============================================================================
@router.get("/dashboard/overview")
def get_dashboard_overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    kpis = calculate_tenant_financial_kpis(db, tid)

    campaigns = db.query(MarketingCampaign).filter(MarketingCampaign.tenant_id == tid).all()
    calendar_items = db.query(EditorialCalendarItem).filter(EditorialCalendarItem.tenant_id == tid).all()
    seo_articles = db.query(SEOArticle).filter(SEOArticle.tenant_id == tid).count()
    creative_assets = db.query(CreativeAsset).filter(CreativeAsset.tenant_id == tid).count()
    copy_items = db.query(CopyItem).filter(CopyItem.tenant_id == tid).count()
    seo_audits = (
        db.query(SEOAuditReport)
        .filter(SEOAuditReport.tenant_id == tid)
        .order_by(SEOAuditReport.created_at.desc())
        .limit(5)
        .all()
    )
    automations = db.query(AutomationRule).filter(AutomationRule.tenant_id == tid).all()
    agent_logs = (
        db.query(AgentExecutionLog)
        .filter(AgentExecutionLog.tenant_id == tid)
        .order_by(AgentExecutionLog.created_at.desc())
        .limit(12)
        .all()
    )
    approvals = db.query(ApprovalRequest).filter(ApprovalRequest.tenant_id == tid).all()
    integrations = ensure_tenant_integrations_seeded(db, tid)
    latest_briefing = (
        db.query(CEODailyBriefing)
        .filter(CEODailyBriefing.tenant_id == tid)
        .order_by(CEODailyBriefing.created_at.desc())
        .first()
    )
    if not latest_briefing:
        latest_briefing = generate_ceo_daily_briefing_service(db, tenant)

    seo_avg_score = round(sum(a.overall_score for a in seo_audits) / len(seo_audits), 1) if seo_audits else 0.0

    return {
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "brand_name": tenant.brand_name,
            "niche": tenant.niche,
            "plan": get_tenant_plan_info(tenant),
            "autonomy_default_level": tenant.autonomy_default_level,
        },
        "metrics_cards": [
            {
                "key": "revenue",
                "label": "Receita Real Consolidada",
                "value": f"R$ {kpis['real_revenue']:,.2f}",
                "raw_value": kpis["real_revenue"],
                "origin": "IMPORTED" if kpis["real_revenue"] > 0 else "REAL",
                "subtext": f"Lucro: R$ {kpis['real_profit']:,.2f} ({kpis['margin_pct']}% margem)",
            },
            {
                "key": "leads",
                "label": "Leads no CRM",
                "value": str(kpis["leads_total"]),
                "raw_value": kpis["leads_total"],
                "origin": "REAL",
                "subtext": f"Conversões: {kpis['conversions_total']} ({kpis['conversion_rate_pct']}%)",
            },
            {
                "key": "roi",
                "label": "ROI Comercial & Mídia",
                "value": f"{kpis['roi_pct']}%",
                "raw_value": kpis["roi_pct"],
                "origin": "REAL",
                "subtext": f"ROAS: {kpis['roas_multiplier']}x | CAC: R$ {kpis['cac_brl']:,.2f}",
            },
            {
                "key": "campaigns",
                "label": "Campanhas Ativas",
                "value": str(sum(1 for c in campaigns if c.status == "ACTIVE")),
                "raw_value": len(campaigns),
                "origin": "REAL",
                "subtext": f"Total estruturadas: {len(campaigns)}",
            },
            {
                "key": "scheduled_posts",
                "label": "Publicações Programadas",
                "value": str(len(calendar_items)),
                "raw_value": len(calendar_items),
                "origin": "REAL",
                "subtext": f"Na fila: {sum(1 for c in calendar_items if c.publish_status == 'QUEUED')}",
            },
            {
                "key": "contents_produced",
                "label": "Conteúdos & Ativos Produzidos",
                "value": str(seo_articles + creative_assets + copy_items),
                "raw_value": seo_articles + creative_assets + copy_items,
                "origin": "REAL",
                "subtext": f"{seo_articles} artigos SEO | {creative_assets} criativos | {copy_items} copies",
            },
            {
                "key": "seo_evolution",
                "label": "Score Técnico de SEO",
                "value": f"{seo_avg_score}/100",
                "raw_value": seo_avg_score,
                "origin": seo_audits[0].data_origin if seo_audits else "ESTIMATED",
                "subtext": f"{len(seo_audits)} auditoria(s) executada(s)",
            },
            {
                "key": "automations",
                "label": "Automações Nativas Ativas",
                "value": f"{sum(1 for a in automations if a.is_active)}/{len(automations)}",
                "raw_value": len(automations),
                "origin": "REAL",
                "subtext": "Scheduler Python em execução contínua",
            },
        ],
        "autonomy_status_panel": {
            "executed_by_ai_count": len(agent_logs),
            "pending_approval_count": sum(1 for a in approvals if a.status == "PENDING"),
            "failed_count": sum(1 for a in automations if a.last_status == "FAILED"),
            "blocked_count": sum(1 for l in agent_logs if l.status == "BLOCKED"),
            "needs_configuration_count": sum(1 for i in integrations if i.status == "PENDING_CREDENTIALS"),
        },
        "ceo_briefing": {
            "id": latest_briefing.id,
            "date": latest_briefing.briefing_date,
            "headline": latest_briefing.summary_headline,
            "recommendations": json.loads(latest_briefing.recommendations_json),
            "urgent_problems": json.loads(latest_briefing.urgent_problems_json),
            "opportunities": json.loads(latest_briefing.opportunities_json),
        },
        "recent_agent_logs": [
            {
                "id": lg.id,
                "workflow_run_id": lg.workflow_run_id,
                "agent_id": lg.agent_id,
                "agent_name": lg.agent_name,
                "task_name": lg.task_name,
                "status": lg.status,
                "duration_ms": lg.duration_ms,
                "created_at": lg.created_at.isoformat(),
            }
            for lg in agent_logs
        ],
    }


# ==============================================================================
# 3. AI AGENTS & CENTRAL ORCHESTRATOR
# ==============================================================================
@router.get("/agents")
def list_agents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    logs = db.query(AgentExecutionLog).filter(AgentExecutionLog.tenant_id == tid).all()
    counts: dict[str, int] = {}
    for lg in logs:
        counts[lg.agent_id] = counts.get(lg.agent_id, 0) + 1

    status_info = MultiProviderAIAdapter.resolve_provider_status()
    result = []
    for aid, meta in AGENT_REGISTRY.items():
        result.append(
            {
                **meta,
                "effective_autonomy_level": get_effective_autonomy_level(tenant, aid),
                "executions_count": counts.get(aid, 0),
                "active_provider": status_info["active_provider"],
                "ai_audit": AGENT_AI_CAPABILITY_AUDIT.get(aid, {}),
            }
        )
    return {"agents": result, "provider": status_info["active_provider"], "llm_active": status_info["llm_active"]}


@router.get("/agents/audit")
def audit_agents_intelligence(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """ETAPA 3 — auditoria honesta: motor determinístico vs template vs LLM real, com consumo e origem das respostas."""
    tid = get_active_tenant_id(user)
    status_info = MultiProviderAIAdapter.resolve_provider_status()
    logs = db.query(AgentExecutionLog).filter(AgentExecutionLog.tenant_id == tid).all()
    origin_counts: dict[str, dict[str, int]] = {}
    for lg in logs:
        m = re.search(r"origem=(.+)$", lg.provider_used or "")
        origin = m.group(1) if m else "LEGACY_DETERMINISTIC_ENGINE (anterior à Fase 13)"
        origin_counts.setdefault(lg.agent_id, {})
        origin_counts[lg.agent_id][origin] = origin_counts[lg.agent_id].get(origin, 0) + 1
    agents = []
    for aid, meta in AGENT_REGISTRY.items():
        cap = AGENT_AI_CAPABILITY_AUDIT.get(aid, {})
        agents.append(
            {
                "agent_id": aid,
                "name": meta["name"],
                "uses_real_llm_now": bool(status_info["llm_active"] and cap.get("llm_narrative_enabled")),
                "llm_model": status_info["active_provider"] if (status_info["llm_active"] and cap.get("llm_narrative_enabled")) else None,
                "llm_capable": bool(cap.get("llm_narrative_enabled")),
                "base_origin": cap.get("base_origin"),
                "deterministic_rules": cap.get("deterministic_rules"),
                "templates": cap.get("templates"),
                "tools_executed": cap.get("tools_executed", []),
                "outputs": cap.get("outputs"),
                "limitations": cap.get("limitations"),
                "responses_by_origin": origin_counts.get(aid, {}),
            }
        )
    real_llm_agents = sum(1 for a in agents if a["uses_real_llm_now"])
    return {
        "provider_status": status_info,
        "usage_today": AIUsageTracker.get_usage_summary(tid),
        "agents": agents,
        "verdict": (
            f"{real_llm_agents} de {len(agents)} agentes usam LLM real agora."
            if real_llm_agents
            else "NENHUM agente usa LLM real neste momento: todas as respostas vêm do motor Python determinístico e/ou templates. "
            "Configure OLLAMA_BASE_URL, GEMINI_API_KEY ou OPENAI_COMPATIBLE_* para ativar a camada de linguagem natural."
        ),
    }


@router.post("/agents/{agent_id}/execute")
def execute_single_agent(
    agent_id: str,
    parameters: dict[str, Any] | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    if agent_id not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Agente '{agent_id}' não encontrado.")

    contract = AgentTaskContract(
        workflow_run_id=f"manual-{uuid.uuid4().hex[:10]}",
        sender_agent="USER_EXECUTIVE",
        target_agent=agent_id,
        task_name=(parameters or {}).get("task_name", "execute_primary_mission"),
        tenant_id=tid,
        autonomy_level=get_effective_autonomy_level(tenant, agent_id),
        parameters=parameters or {},
    )
    res = CentralOrchestrator.dispatch_task(db, tenant, contract)
    record_audit_log(
        db,
        tenant_id=tid,
        user_id=user.id,
        actor=user.email,
        action=f"AGENT_EXECUTED:{agent_id}",
        resource_type="agent",
        resource_id=agent_id,
    )
    return res.model_dump()


@router.post("/orchestrator/diagnose")
def trigger_full_orchestrator_diagnosis(
    payload: dict[str, Any] | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    reason = (payload or {}).get("reason", "Diagnóstico Multiagente Acionado pelo Painel Executivo")
    result = CentralOrchestrator.run_multi_agent_executive_diagnosis(db, tenant, trigger_reason=reason)
    record_audit_log(db, tenant_id=tid, user_id=user.id, actor=user.email, action="ORCHESTRATOR_FULL_DIAGNOSIS")
    return result


# ==============================================================================
# 4. AGENT 01 — AI CEO (METAS & CEO DAILY BRIEFING)
# ==============================================================================
@router.get("/ceo/briefings")
def get_ceo_briefings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    briefings = (
        db.query(CEODailyBriefing)
        .filter(CEODailyBriefing.tenant_id == tid)
        .order_by(CEODailyBriefing.created_at.desc())
        .limit(10)
        .all()
    )
    if not briefings:
        briefings = [generate_ceo_daily_briefing_service(db, tenant)]
    goals = db.query(StrategicGoal).filter(StrategicGoal.tenant_id == tid).order_by(StrategicGoal.financial_impact_score.desc()).all()
    return {
        "briefings": [
            {
                "id": b.id,
                "briefing_date": b.briefing_date,
                "summary_headline": b.summary_headline,
                "what_happened": json.loads(b.what_happened_json),
                "what_is_working": json.loads(b.what_is_working_json),
                "what_is_wrong": json.loads(b.what_is_wrong_json),
                "opportunities": json.loads(b.opportunities_json),
                "urgent_problems": json.loads(b.urgent_problems_json),
                "recommendations": json.loads(b.recommendations_json),
                "priority_actions": json.loads(b.priority_actions_json),
                "automation_candidates": json.loads(b.automation_candidates_json),
                "data_sources_summary": json.loads(b.data_sources_summary_json),
                "created_at": b.created_at.isoformat(),
            }
            for b in briefings
        ],
        "goals": [
            {
                "id": g.id,
                "title": g.title,
                "period": g.period,
                "metric_name": g.metric_name,
                "target_value": g.target_value,
                "current_value": g.current_value,
                "unit": g.unit,
                "data_origin": g.data_origin,
                "financial_impact_score": g.financial_impact_score,
                "priority": g.priority,
                "status": g.status,
                "deadline": g.deadline,
            }
            for g in goals
        ],
    }


@router.post("/ceo/briefings/generate", status_code=status.HTTP_201_CREATED)
def generate_new_ceo_briefing(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    b = generate_ceo_daily_briefing_service(db, tenant)
    record_audit_log(db, tenant_id=tid, user_id=user.id, actor=user.email, action="CEO_DAILY_BRIEFING_GENERATED", resource_id=str(b.id))
    return {
        "id": b.id,
        "briefing_date": b.briefing_date,
        "summary_headline": b.summary_headline,
        "what_happened": json.loads(b.what_happened_json),
        "what_is_working": json.loads(b.what_is_working_json),
        "what_is_wrong": json.loads(b.what_is_wrong_json),
        "opportunities": json.loads(b.opportunities_json),
        "urgent_problems": json.loads(b.urgent_problems_json),
        "recommendations": json.loads(b.recommendations_json),
        "priority_actions": json.loads(b.priority_actions_json),
    }


@router.post("/ceo/goals", status_code=status.HTTP_201_CREATED)
def create_strategic_goal(payload: StrategicGoalCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    g = StrategicGoal(
        tenant_id=tid,
        title=sanitize_text(payload.title),
        period=payload.period,
        metric_name=sanitize_text(payload.metric_name),
        target_value=payload.target_value,
        current_value=payload.current_value,
        unit=payload.unit,
        data_origin=payload.data_origin,
        financial_impact_score=payload.financial_impact_score,
        priority=payload.priority,
        deadline=payload.deadline,
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    if g.current_value >= g.target_value and g.target_value > 0:
        trigger_event_automations(db, tid, "goal.achieved", {"goal_id": g.id, "title": g.title})
    return {"id": g.id, "title": g.title, "period": g.period, "target_value": g.target_value, "data_origin": g.data_origin}


# ==============================================================================
# 5. AGENT 02 — AI CMO (MARKETING, PERSONAS, CAMPANHAS & PLANO MENSAL)
# ==============================================================================
@router.get("/marketing/overview")
def get_marketing_overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    personas = db.query(MarketingPersona).filter(MarketingPersona.tenant_id == tid).all()
    campaigns = db.query(MarketingCampaign).filter(MarketingCampaign.tenant_id == tid).order_by(MarketingCampaign.id.desc()).all()
    return {
        "personas": [
            {
                "id": p.id,
                "name": p.name,
                "role_segment": p.role_segment,
                "demographics": p.demographics,
                "pains": json.loads(p.pains_json or "[]"),
                "desires": json.loads(p.desires_json or "[]"),
                "objections": json.loads(p.objections_json or "[]"),
                "channels": json.loads(p.channels_json or "[]"),
                "value_proposition": p.value_proposition,
            }
            for p in personas
        ],
        "campaigns": [
            {
                "id": c.id,
                "name": c.name,
                "campaign_type": c.campaign_type,
                "channel": c.channel,
                "objective": c.objective,
                "funnel_stage": c.funnel_stage,
                "budget_planned": c.budget_planned,
                "spend_real": c.spend_real,
                "revenue_attributed": c.revenue_attributed,
                "roi_pct": c.roi_pct,
                "leads_generated": c.leads_generated,
                "conversions": c.conversions,
                "data_origin": c.data_origin,
                "status": c.status,
                "monthly_plan": json.loads(c.monthly_plan_json or "{}"),
            }
            for c in campaigns
        ],
    }


@router.post("/marketing/personas", status_code=status.HTTP_201_CREATED)
def create_persona(payload: MarketingPersonaCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    p = MarketingPersona(
        tenant_id=tid,
        name=sanitize_text(payload.name),
        role_segment=sanitize_text(payload.role_segment),
        demographics=sanitize_text(payload.demographics),
        pains_json=json.dumps(payload.pains, ensure_ascii=False),
        desires_json=json.dumps(payload.desires, ensure_ascii=False),
        objections_json=json.dumps(payload.objections, ensure_ascii=False),
        channels_json=json.dumps(payload.channels, ensure_ascii=False),
        value_proposition=sanitize_text(payload.value_proposition),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id, "name": p.name}


@router.post("/marketing/campaigns", status_code=status.HTTP_201_CREATED)
def create_campaign(payload: MarketingCampaignCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    # High-impact check: spending money / paid budget requires explicit confirmation
    if payload.spend_real > 0 or payload.budget_planned > 10000:
        if not payload.confirmation_token or not verify_high_impact_token(user.id, tid, "CRITICAL_ACTION", payload.confirmation_token):
            req = ApprovalRequest(
                tenant_id=tid,
                agent_id="AGENT_02_CMO",
                action_type="PAID_CAMPAIGN_BUDGET",
                title=f"Aprovar Orçamento de Campanha: {payload.name} (R$ {payload.budget_planned:,.2f})",
                payload_json=json.dumps(payload.model_dump(), ensure_ascii=False),
                autonomy_level_at_creation=2,
                is_high_impact=True,
                status="PENDING",
            )
            db.add(req)
            db.commit()
            db.refresh(req)
            return {
                "status": "PENDING_HIGH_IMPACT_APPROVAL",
                "approval_request_id": req.id,
                "message": "Ação de alto impacto financeiro (orçamento/gasto em campanha) enviada para confirmação explícita na Central de Aprovações.",
            }

    roi = round(((payload.revenue_attributed - payload.spend_real) / payload.spend_real) * 100, 1) if payload.spend_real > 0 else 0.0
    c = MarketingCampaign(
        tenant_id=tid,
        name=sanitize_text(payload.name),
        campaign_type=payload.campaign_type,
        channel=sanitize_text(payload.channel),
        objective=sanitize_text(payload.objective),
        funnel_stage=payload.funnel_stage,
        budget_planned=payload.budget_planned,
        spend_real=payload.spend_real,
        revenue_attributed=payload.revenue_attributed,
        roi_pct=roi,
        leads_generated=payload.leads_generated,
        conversions=payload.conversions,
        data_origin=payload.data_origin,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "name": c.name, "roi_pct": c.roi_pct, "data_origin": c.data_origin}


# ==============================================================================
# 6. AGENT 03 — AI SEO DIRECTOR & SEO CONTENT FACTORY
# ==============================================================================
@router.get("/seo/overview")
def get_seo_overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    audits = db.query(SEOAuditReport).filter(SEOAuditReport.tenant_id == tid).order_by(SEOAuditReport.id.desc()).all()
    clusters = db.query(SEOKeywordCluster).filter(SEOKeywordCluster.tenant_id == tid).order_by(SEOKeywordCluster.id.desc()).all()
    articles = db.query(SEOArticle).filter(SEOArticle.tenant_id == tid).order_by(SEOArticle.id.desc()).all()
    gsc_conn = (
        db.query(IntegrationConnection)
        .filter(IntegrationConnection.tenant_id == tid, IntegrationConnection.provider_key == "google_search_console")
        .first()
    )
    return {
        "gsc_ranking_status": {
            "connected": bool(gsc_conn and gsc_conn.status == "CONNECTED"),
            "notice": (
                "Conectado ao Google Search Console."
                if (gsc_conn and gsc_conn.status == "CONNECTED")
                else "Posições no Google NÃO são simuladas. Conecte o Google Search Console na aba Integrações para importar posições reais da SERP."
            ),
        },
        "audits": [
            {
                "id": a.id,
                "target_url": a.target_url,
                "status_code": a.status_code,
                "response_time_ms": a.response_time_ms,
                "overall_score": a.overall_score,
                "title_tag": a.title_tag,
                "meta_description": a.meta_description,
                "h1_tags": json.loads(a.h1_tags_json or "[]"),
                "internal_links_count": a.internal_links_count,
                "external_links_count": a.external_links_count,
                "images_missing_alt_count": a.images_missing_alt_count,
                "has_robots_txt": a.has_robots_txt,
                "has_sitemap_xml": a.has_sitemap_xml,
                "is_indexable": a.is_indexable,
                "issues": json.loads(a.issues_json or "[]"),
                "recommendations": json.loads(a.recommendations_json or "[]"),
                "suggested_title": a.suggested_title,
                "suggested_meta_description": a.suggested_meta_description,
                "generated_schema": json.loads(a.generated_schema_json or "{}"),
                "data_origin": a.data_origin,
                "created_at": a.created_at.isoformat(),
            }
            for a in audits
        ],
        "keyword_clusters": [
            {
                "id": kc.id,
                "seed_keyword": kc.seed_keyword,
                "search_intent": kc.search_intent,
                "long_tail_keywords": json.loads(kc.long_tail_keywords_json or "[]"),
                "clusters": json.loads(kc.cluster_topics_json or "[]"),
                "backlink_strategy": json.loads(kc.backlink_strategy_json or "[]"),
                "source": kc.source,
            }
            for kc in clusters
        ],
        "articles": [
            {
                "id": art.id,
                "title": art.title,
                "slug": art.slug,
                "target_keyword": art.target_keyword,
                "search_intent": art.search_intent,
                "meta_title": art.meta_title,
                "meta_description": art.meta_description,
                "word_count": art.word_count,
                "keyword_density_pct": art.keyword_density_pct,
                "readability_score": art.readability_score,
                "content_markdown": art.content_markdown,
                "schema_json_ld": json.loads(art.schema_json_ld or "{}"),
                "status": art.status,
                "created_at": art.created_at.isoformat(),
            }
            for art in articles
        ],
    }


@router.post("/seo/audit", status_code=status.HTTP_201_CREATED)
def run_seo_audit(payload: SEOAuditRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    report = perform_real_seo_audit(db, tenant, payload.target_url, payload.target_keyword)
    return {
        "id": report.id,
        "target_url": report.target_url,
        "overall_score": report.overall_score,
        "response_time_ms": report.response_time_ms,
        "issues": json.loads(report.issues_json),
        "recommendations": json.loads(report.recommendations_json),
        "suggested_title": report.suggested_title,
        "suggested_meta_description": report.suggested_meta_description,
        "data_origin": report.data_origin,
    }


@router.post("/seo/keywords", status_code=status.HTTP_201_CREATED)
def run_keyword_research(payload: SEOKeywordResearchRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    cluster = research_keywords_and_clusters(db, tenant, payload.seed_keyword)
    return {
        "id": cluster.id,
        "seed_keyword": cluster.seed_keyword,
        "search_intent": cluster.search_intent,
        "long_tail_keywords": json.loads(cluster.long_tail_keywords_json),
        "clusters": json.loads(cluster.cluster_topics_json),
        "backlink_strategy": json.loads(cluster.backlink_strategy_json),
        "source": cluster.source,
    }


@router.post("/seo/articles/generate", status_code=status.HTTP_201_CREATED)
def create_seo_article(payload: SEOArticleGenerateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    art = generate_seo_factory_article(db, tenant, payload.topic, payload.target_keyword, payload.search_intent)
    return {
        "id": art.id,
        "title": art.title,
        "slug": art.slug,
        "word_count": art.word_count,
        "keyword_density_pct": art.keyword_density_pct,
        "content_markdown": art.content_markdown,
        "status": art.status,
    }


# ==============================================================================
# 7. AGENT 04 — SOCIAL MEDIA & CENTRAL DE PUBLICAÇÃO / CALENDÁRIO
# ==============================================================================
@router.get("/social/calendar")
def get_editorial_calendar(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    items = (
        db.query(EditorialCalendarItem)
        .filter(EditorialCalendarItem.tenant_id == tid)
        .order_by(EditorialCalendarItem.scheduled_for.asc())
        .all()
    )
    return [
        {
            "id": i.id,
            "title": i.title,
            "platform": i.platform,
            "content_format": i.content_format,
            "caption": i.caption,
            "hashtags": json.loads(i.hashtags_json or "[]"),
            "video_script": i.video_script,
            "scheduled_for": i.scheduled_for,
            "best_time_rationale": i.best_time_rationale,
            "approval_status": i.approval_status,
            "publish_status": i.publish_status,
            "retry_count": i.retry_count,
            "last_error": i.last_error,
            "external_post_id": i.external_post_id,
            "data_origin": i.data_origin,
        }
        for i in items
    ]


@router.post("/social/calendar", status_code=status.HTTP_201_CREATED)
def create_editorial_item(payload: EditorialItemCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)

    caption = payload.caption.strip()
    if not caption and payload.auto_generate_copy:
        caption = (
            f"{payload.title} — Estratégia {tenant.brand_name} para {tenant.niche}.\n\n"
            f"Acompanhe nossos indicadores e soluções para {tenant.target_audience}."
        )
    hashtags = payload.hashtags or ["#marketing", "#negocios", "#crescimento", f"#{tenant.slug.replace('-', '')}"]

    item = EditorialCalendarItem(
        tenant_id=tid,
        title=sanitize_text(payload.title),
        platform=payload.platform,
        content_format=payload.content_format,
        caption=sanitize_text(caption),
        hashtags_json=json.dumps(hashtags, ensure_ascii=False),
        video_script=sanitize_text(payload.video_script),
        scheduled_for=payload.scheduled_for,
        best_time_rationale=f"Janela recomendada para {payload.platform}",
        approval_status="PENDING_REVIEW",
        publish_status="QUEUED",
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    pub_result = validate_and_publish_social_item(db, tenant, item, force_execute=False)
    return {"id": item.id, "title": item.title, "publish_check": pub_result}


@router.post("/social/calendar/{item_id}/publish")
def trigger_social_item_publication(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    item = db.query(EditorialCalendarItem).filter(EditorialCalendarItem.id == item_id, EditorialCalendarItem.tenant_id == tid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item do calendário não encontrado.")
    item.approval_status = "APPROVED"
    db.commit()
    if item.platform.lower() != "blog":
        ok_lim, why_lim = check_autonomy_limit(db, tenant, "PUBLISH")
        if not ok_lim:
            item.approval_status = "PENDING_REVIEW"
            db.commit()
            return {"item_id": item.id, "status": "BLOCKED_BY_LIMIT", "message": why_lim}
    res = validate_and_publish_social_item(db, tenant, item, force_execute=True)
    return {"item_id": item.id, "approval_status": item.approval_status, "publish_status": item.publish_status, **res}


# ==============================================================================
# 8. AGENT 05 & 06 — CREATIVE STUDIO & AI COPYWRITER
# ==============================================================================
@router.get("/creative/assets")
def list_creative_assets(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    assets = db.query(CreativeAsset).filter(CreativeAsset.tenant_id == tid).order_by(CreativeAsset.id.desc()).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "asset_type": a.asset_type,
            "platform": a.platform,
            "dimensions": a.dimensions,
            "preview_data_uri": a.preview_data_uri,
            "content": json.loads(a.content_json or "{}"),
            "brand_palette": json.loads(a.brand_palette_json or "{}"),
            "license_info": a.license_info,
            "is_approved": a.is_approved,
            "created_at": a.created_at.isoformat(),
        }
        for a in assets
    ]


@router.post("/creative/assets/generate", status_code=status.HTTP_201_CREATED)
def generate_new_creative_asset(
    payload: CreativeAssetGenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    a = generate_creative_asset(
        db=db,
        tenant=tenant,
        title=sanitize_text(payload.title),
        asset_type=payload.asset_type,
        platform=payload.platform,
        headline_text=sanitize_text(payload.headline_text),
        subheadline_text=sanitize_text(payload.subheadline_text),
        cta_text=sanitize_text(payload.cta_text),
        campaign_id=payload.campaign_id,
    )
    return {
        "id": a.id,
        "title": a.title,
        "asset_type": a.asset_type,
        "dimensions": a.dimensions,
        "preview_data_uri": a.preview_data_uri,
        "content": json.loads(a.content_json or "{}"),
        "license_info": a.license_info,
    }


@router.get("/copywriter/items")
def list_copy_items(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    items = db.query(CopyItem).filter(CopyItem.tenant_id == tid).order_by(CopyItem.id.desc()).all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "copy_type": c.copy_type,
            "framework": c.framework,
            "tone": c.tone,
            "target_audience": c.target_audience,
            "variant_a": c.variant_a,
            "variant_b": c.variant_b,
            "ab_test_hypothesis": c.ab_test_hypothesis,
            "compliance_verified": c.compliance_verified,
            "created_at": c.created_at.isoformat(),
        }
        for c in items
    ]


@router.post("/copywriter/generate", status_code=status.HTTP_201_CREATED)
def generate_copy_endpoint(payload: CopyGenerateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    c = generate_persuasive_copy(
        db=db,
        tenant=tenant,
        title=sanitize_text(payload.title),
        copy_type=payload.copy_type,
        framework=payload.framework,
        product_or_offer=sanitize_text(payload.product_or_offer),
        target_audience=sanitize_text(payload.target_audience),
        key_benefit=sanitize_text(payload.key_benefit),
        tone=sanitize_text(payload.tone),
    )
    return {
        "id": c.id,
        "title": c.title,
        "copy_type": c.copy_type,
        "framework": c.framework,
        "variant_a": c.variant_a,
        "variant_b": c.variant_b,
        "ab_test_hypothesis": c.ab_test_hypothesis,
        "compliance_verified": c.compliance_verified,
    }


# ==============================================================================
# 9. AGENT 07 — AI GROWTH HACKER (EXPERIMENTOS ICE)
# ==============================================================================
@router.get("/growth/experiments")
def list_growth_experiments(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    exps = db.query(GrowthExperiment).filter(GrowthExperiment.tenant_id == tid).order_by(GrowthExperiment.ice_score.desc()).all()
    return [
        {
            "id": e.id,
            "title": e.title,
            "channel": e.channel,
            "hypothesis": e.hypothesis,
            "objective": e.objective,
            "target_audience": e.target_audience,
            "indicator_metric": e.indicator_metric,
            "estimated_cost": e.estimated_cost,
            "baseline_conversion_pct": e.baseline_conversion_pct,
            "real_result_conversion_pct": e.real_result_conversion_pct,
            "real_result_summary": e.real_result_summary,
            "data_origin": e.data_origin,
            "ice_score": e.ice_score,
            "status": e.status,
            "conclusion": e.conclusion,
        }
        for e in exps
    ]


@router.post("/growth/experiments", status_code=status.HTTP_201_CREATED)
def create_growth_experiment(payload: GrowthExperimentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    ice = round((payload.impact + payload.confidence + payload.ease) / 3.0, 2)
    origin = "REAL" if payload.real_result_conversion_pct is not None else "ESTIMATED"
    exp = GrowthExperiment(
        tenant_id=tid,
        title=sanitize_text(payload.title),
        channel=sanitize_text(payload.channel),
        hypothesis=sanitize_text(payload.hypothesis),
        objective=sanitize_text(payload.objective),
        target_audience=sanitize_text(payload.target_audience),
        indicator_metric=sanitize_text(payload.indicator_metric),
        estimated_cost=payload.estimated_cost,
        baseline_conversion_pct=payload.baseline_conversion_pct,
        real_result_conversion_pct=payload.real_result_conversion_pct,
        data_origin=origin,
        ice_score=ice,
        status="RUNNING",
        conclusion="Experimento em andamento.",
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return {"id": exp.id, "title": exp.title, "ice_score": exp.ice_score, "data_origin": exp.data_origin}


@router.put("/growth/experiments/{exp_id}/result")
def record_growth_experiment_result(
    exp_id: int,
    payload: GrowthExperimentUpdateResult,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    exp = db.query(GrowthExperiment).filter(GrowthExperiment.id == exp_id, GrowthExperiment.tenant_id == tid).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experimento não encontrado.")
    exp.real_result_conversion_pct = payload.real_result_conversion_pct
    exp.real_result_summary = sanitize_text(payload.real_result_summary)
    exp.conclusion = sanitize_text(payload.conclusion)
    exp.status = payload.status
    exp.data_origin = "REAL"
    db.commit()
    return {"id": exp.id, "status": exp.status, "real_result_conversion_pct": exp.real_result_conversion_pct, "data_origin": exp.data_origin}


# ==============================================================================
# 10. AGENT 08 — CRM, LEADS, PIPELINE & COMERCIAL
# ==============================================================================
@router.get("/crm/overview")
def get_crm_overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    leads = db.query(CRMLead).filter(CRMLead.tenant_id == tid).order_by(CRMLead.lead_score.desc()).all()
    deals = db.query(CRMDeal).filter(CRMDeal.tenant_id == tid).order_by(CRMDeal.id.desc()).all()
    activities = db.query(CRMActivity).filter(CRMActivity.tenant_id == tid).order_by(CRMActivity.id.desc()).all()

    open_deals = [d for d in deals if d.status == "OPEN"]
    won_deals = [d for d in deals if d.status == "WON" or d.stage == "CLOSED_WON"]
    weighted_forecast = round(sum(d.value * (d.probability_pct / 100.0) for d in open_deals), 2)

    return {
        "commercial_summary": {
            "total_leads": len(leads),
            "qualified_leads": sum(1 for l in leads if l.qualification_status == "QUALIFIED"),
            "open_deals_count": len(open_deals),
            "won_deals_count": len(won_deals),
            "won_revenue_brl": round(sum(d.value for d in won_deals), 2),
            "weighted_forecast_brl": weighted_forecast,
        },
        "leads": [
            {
                "id": l.id,
                "full_name": l.full_name,
                "email": l.email,
                "phone": l.phone,
                "company_name": l.company_name,
                "source_channel": l.source_channel,
                "buy_intent": l.buy_intent,
                "lead_score": l.lead_score,
                "qualification_status": l.qualification_status,
                "pipeline_stage": l.pipeline_stage,
                "estimated_value": l.estimated_value,
                "data_origin": l.data_origin,
                "consent_lgpd": l.consent_lgpd,
                "opt_out": l.opt_out,
                "notes": l.notes,
                "created_at": l.created_at.isoformat(),
            }
            for l in leads
        ],
        "deals": [
            {
                "id": d.id,
                "lead_id": d.lead_id,
                "title": d.title,
                "stage": d.stage,
                "value": d.value,
                "probability_pct": d.probability_pct,
                "expected_close_date": d.expected_close_date,
                "status": d.status,
                "data_origin": d.data_origin,
            }
            for d in deals
        ],
        "activities": [
            {
                "id": a.id,
                "lead_id": a.lead_id,
                "deal_id": a.deal_id,
                "activity_type": a.activity_type,
                "subject": a.subject,
                "description": a.description,
                "due_date": a.due_date,
                "completed": a.completed,
            }
            for a in activities
        ],
    }


@router.post("/crm/leads", status_code=status.HTTP_201_CREATED)
def create_crm_lead(payload: CRMLeadCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    if not payload.consent_lgpd:
        raise HTTPException(
            status_code=400,
            detail="Violação de Governança LGPD: não é permitido cadastrar contatos sem consentimento ou base legal válida.",
        )

    lead = CRMLead(
        tenant_id=tid,
        full_name=sanitize_text(payload.full_name),
        email=payload.email.strip().lower(),
        phone=sanitize_text(payload.phone),
        company_name=sanitize_text(payload.company_name),
        source_channel=sanitize_text(payload.source_channel),
        buy_intent=payload.buy_intent,
        estimated_value=payload.estimated_value,
        data_origin=payload.data_origin,
        consent_lgpd=payload.consent_lgpd,
        consent_source=sanitize_text(payload.consent_source),
        notes=sanitize_text(payload.notes),
    )
    lead.lead_score, lead.qualification_status = compute_lead_score(lead)
    lead.pipeline_stage = "QUALIFICATION" if lead.lead_score >= 70 else "NEW_LEAD"
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Create automatic follow-up task in CRM
    follow_up = CRMActivity(
        tenant_id=tid,
        lead_id=lead.id,
        activity_type="FOLLOW_UP",
        subject=f"Primeiro Contato Consultivo: {lead.full_name} (Score {lead.lead_score})",
        description=f"Apresentar diagnóstico personalizado para {lead.company_name or lead.full_name}.",
        due_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )
    db.add(follow_up)
    db.commit()

    # Trigger Automation #9 (Quando um lead chegar: qualificar e registrar no CRM)
    trigger_event_automations(db, tid, "lead.created", {"lead_id": lead.id})

    return {
        "id": lead.id,
        "full_name": lead.full_name,
        "lead_score": lead.lead_score,
        "qualification_status": lead.qualification_status,
        "pipeline_stage": lead.pipeline_stage,
        "data_origin": lead.data_origin,
    }


@router.post("/crm/deals", status_code=status.HTTP_201_CREATED)
def create_crm_deal(payload: CRMDealCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    deal_status = "WON" if payload.stage == "CLOSED_WON" else ("LOST" if payload.stage == "CLOSED_LOST" else "OPEN")
    d = CRMDeal(
        tenant_id=tid,
        lead_id=payload.lead_id,
        title=sanitize_text(payload.title),
        stage=payload.stage,
        value=payload.value,
        probability_pct=100.0 if deal_status == "WON" else payload.probability_pct,
        expected_close_date=payload.expected_close_date,
        status=deal_status,
        data_origin=payload.data_origin,
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return {"id": d.id, "title": d.title, "stage": d.stage, "value": d.value, "status": d.status}


@router.put("/crm/deals/{deal_id}/stage")
def update_crm_deal_stage(
    deal_id: int,
    payload: dict[str, Any],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    d = db.query(CRMDeal).filter(CRMDeal.id == deal_id, CRMDeal.tenant_id == tid).first()
    if not d:
        raise HTTPException(status_code=404, detail="Negociação não encontrada.")
    new_stage = payload.get("stage", d.stage)
    d.stage = new_stage
    if new_stage == "CLOSED_WON":
        d.status = "WON"
        d.probability_pct = 100.0
    elif new_stage == "CLOSED_LOST":
        d.status = "LOST"
        d.probability_pct = 0.0
    else:
        d.status = "OPEN"
    db.commit()
    return {"id": d.id, "stage": d.stage, "status": d.status}


# ==============================================================================
# 11. AGENT 09 — COMPETITIVE INTELLIGENCE (CONCORRENTES)
# ==============================================================================
@router.get("/competitors")
def list_competitors(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    comps = db.query(Competitor).filter(Competitor.tenant_id == tid).order_by(Competitor.id.desc()).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "website_url": c.website_url,
            "category": c.category,
            "public_pricing_summary": c.public_pricing_summary,
            "positioning_summary": c.positioning_summary,
            "strengths": json.loads(c.strengths_json or "[]"),
            "weaknesses": json.loads(c.weaknesses_json or "[]"),
            "differentiation_opportunities": json.loads(c.differentiation_opportunities_json or "[]"),
            "robots_txt_respected": c.robots_txt_respected,
            "last_analyzed_at": c.last_analyzed_at.isoformat() if c.last_analyzed_at else None,
        }
        for c in comps
    ]


@router.post("/competitors", status_code=status.HTTP_201_CREATED)
def add_and_analyze_competitor(payload: CompetitorCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    comp = Competitor(
        tenant_id=tid,
        name=sanitize_text(payload.name),
        website_url=payload.website_url.strip(),
        category=sanitize_text(payload.category),
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    comp = analyze_competitor_public(db, tenant, comp)
    return {
        "id": comp.id,
        "name": comp.name,
        "website_url": comp.website_url,
        "positioning_summary": comp.positioning_summary,
        "public_pricing_summary": comp.public_pricing_summary,
        "differentiation_opportunities": json.loads(comp.differentiation_opportunities_json),
        "robots_txt_respected": comp.robots_txt_respected,
    }


# ==============================================================================
# 12. AGENT 10 — FINANCE & PERFORMANCE
# ==============================================================================
@router.get("/finance/overview")
def get_finance_overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    kpis = calculate_tenant_financial_kpis(db, tid)
    records = db.query(FinancialRecord).filter(FinancialRecord.tenant_id == tid).order_by(FinancialRecord.period_date.desc()).all()
    return {
        "kpis": kpis,
        "records": [
            {
                "id": r.id,
                "period_date": r.period_date,
                "record_type": r.record_type,
                "category": r.category,
                "channel": r.channel,
                "amount": r.amount,
                "data_origin": r.data_origin,
                "description": r.description,
            }
            for r in records
        ],
    }


@router.post("/finance/records", status_code=status.HTTP_201_CREATED)
def create_financial_record(payload: FinancialRecordCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    rec = FinancialRecord(
        tenant_id=tid,
        period_date=payload.period_date,
        record_type=payload.record_type,
        category=sanitize_text(payload.category),
        channel=sanitize_text(payload.channel),
        amount=payload.amount,
        data_origin=payload.data_origin,
        description=sanitize_text(payload.description),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    kpis = calculate_tenant_financial_kpis(db, tid)
    if kpis["margin_pct"] < 0:
        trigger_event_automations(db, tid, "kpi.drop_detected", {"margin_pct": kpis["margin_pct"]})
    return {"id": rec.id, "amount": rec.amount, "record_type": rec.record_type, "data_origin": rec.data_origin, "updated_kpis": kpis}


# ==============================================================================
# 13. AGENT 11 — CUSTOMER SUCCESS
# ==============================================================================
@router.get("/customer-success/overview")
def get_customer_success_overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    items = db.query(CustomerFeedback).filter(CustomerFeedback.tenant_id == tid).order_by(CustomerFeedback.id.desc()).all()
    avg_nps = round(sum(i.nps_score for i in items) / len(items), 1) if items else 0.0
    avg_csat = round(sum(i.csat_score for i in items) / len(items), 1) if items else 0.0
    return {
        "summary": {
            "total_feedbacks": len(items),
            "average_nps": avg_nps,
            "average_csat": avg_csat,
            "high_churn_risk_count": sum(1 for i in items if i.churn_risk == "HIGH"),
            "upsell_ready_count": sum(1 for i in items if i.nps_score >= 9),
        },
        "feedbacks": [
            {
                "id": f.id,
                "customer_name": f.customer_name,
                "customer_email": f.customer_email,
                "nps_score": f.nps_score,
                "csat_score": f.csat_score,
                "sentiment": f.sentiment,
                "churn_risk": f.churn_risk,
                "recurring_issue_tag": f.recurring_issue_tag,
                "feedback_text": f.feedback_text,
                "retention_suggestion": f.retention_suggestion,
                "upsell_opportunity": f.upsell_opportunity,
                "status": f.status,
            }
            for f in items
        ],
    }


@router.post("/customer-success/feedbacks", status_code=status.HTTP_201_CREATED)
def add_customer_feedback(payload: CustomerFeedbackCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    if payload.nps_score <= 6:
        sentiment = "NEGATIVE"
        churn_risk = "HIGH"
        retention = "Acionar gerente de conta em até 4h para call de diagnóstico e plano de correção."
        upsell = "Suspenso até estabilização da saúde da conta."
        tag = "Alerta de Retenção"
    elif payload.nps_score <= 8:
        sentiment = "NEUTRAL"
        churn_risk = "MEDIUM"
        retention = "Agendar revisão mensal de resultados (QBR) para destravar adoção."
        upsell = "Apresentar módulo complementar após melhoria de engajamento."
        tag = "Adoção Parcial"
    else:
        sentiment = "POSITIVE"
        churn_risk = "LOW"
        retention = "Solicitar depoimento real autorizado e convidar para programa de indicação."
        upsell = "Elegível para upgrade de plano (Business/Enterprise) ou expansão multiunidade."
        tag = "Promotor / Expansão"

    fb = CustomerFeedback(
        tenant_id=tid,
        customer_name=sanitize_text(payload.customer_name),
        customer_email=payload.customer_email.strip(),
        nps_score=payload.nps_score,
        csat_score=payload.csat_score,
        sentiment=sentiment,
        churn_risk=churn_risk,
        recurring_issue_tag=tag,
        feedback_text=sanitize_text(payload.feedback_text),
        retention_suggestion=retention,
        upsell_opportunity=upsell,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {
        "id": fb.id,
        "sentiment": fb.sentiment,
        "churn_risk": fb.churn_risk,
        "retention_suggestion": fb.retention_suggestion,
        "upsell_opportunity": fb.upsell_opportunity,
    }


# ==============================================================================
# 14. AUTOMAÇÕES NATIVAS EM PYTHON & SCHEDULER
# ==============================================================================
@router.get("/automations")
def list_automations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    rules = ensure_tenant_automations_seeded(db, tid)
    execs = (
        db.query(AutomationExecution)
        .filter(AutomationExecution.tenant_id == tid)
        .order_by(AutomationExecution.id.desc())
        .limit(25)
        .all()
    )
    return {
        "scheduler": get_scheduler_status(),
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "code_key": r.code_key,
                "trigger_type": r.trigger_type,
                "cron_expression": r.cron_expression,
                "event_name": r.event_name,
                "action_agent": r.action_agent,
                "action_task": r.action_task,
                "frequency_label": r.frequency_label,
                "scheduled_time": r.scheduled_time,
                "priority": r.priority,
                "owner_role": r.owner_role,
                "is_active": r.is_active,
                "max_retries": r.max_retries,
                "last_run_at": r.last_run_at.isoformat() if r.last_run_at else None,
                "last_status": r.last_status,
                "run_count": r.run_count,
                "failure_count": r.failure_count,
            }
            for r in rules
        ],
        "executions": [
            {
                "id": ex.id,
                "rule_id": ex.rule_id,
                "idempotency_key": ex.idempotency_key,
                "status": ex.status,
                "attempt_number": ex.attempt_number,
                "duration_ms": ex.duration_ms,
                "result_summary": json.loads(ex.result_summary_json or "{}"),
                "error_message": ex.error_message,
                "finished_at": ex.finished_at.isoformat(),
            }
            for ex in execs
        ],
    }


@router.post("/automations", status_code=status.HTTP_201_CREATED)
def create_custom_automation(payload: AutomationRuleCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    r = AutomationRule(
        tenant_id=tid,
        name=sanitize_text(payload.name),
        code_key=sanitize_text(payload.code_key),
        trigger_type=payload.trigger_type,
        cron_expression=payload.cron_expression,
        event_name=payload.event_name,
        condition_json=json.dumps(payload.condition, ensure_ascii=False),
        action_agent=payload.action_agent,
        action_task=payload.action_task,
        frequency_label=payload.frequency_label,
        scheduled_time=payload.scheduled_time,
        priority=payload.priority,
        max_retries=payload.max_retries,
        timeout_seconds=payload.timeout_seconds,
        is_active=True,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"id": r.id, "name": r.name, "code_key": r.code_key}


@router.post("/automations/{rule_id}/run")
def run_automation_now(
    rule_id: int,
    payload: dict[str, Any] | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    rule = db.query(AutomationRule).filter(AutomationRule.id == rule_id, AutomationRule.tenant_id == tid).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Regra de automação não encontrada.")

    idem = (payload or {}).get("idempotency_key")
    sim_fail = bool((payload or {}).get("simulate_transient_failure", False))
    ex = execute_automation_rule(db, rule, idempotency_key=idem, simulate_failure_once=sim_fail)
    return {
        "execution_id": ex.id,
        "rule_id": rule.id,
        "status": ex.status,
        "attempt_number": ex.attempt_number,
        "duration_ms": ex.duration_ms,
        "result_summary": json.loads(ex.result_summary_json or "{}"),
        "error_message": ex.error_message,
    }


# ==============================================================================
# 15. CENTRAL DE APROVAÇÕES & AUTONOMIA OPERACIONAL
# ==============================================================================
@router.get("/approvals")
def list_approvals(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    reqs = db.query(ApprovalRequest).filter(ApprovalRequest.tenant_id == tid).order_by(ApprovalRequest.id.desc()).all()
    return [
        {
            "id": r.id,
            "agent_id": r.agent_id,
            "action_type": r.action_type,
            "title": r.title,
            "payload": json.loads(r.payload_json or "{}"),
            "autonomy_level_at_creation": r.autonomy_level_at_creation,
            "is_high_impact": r.is_high_impact,
            "status": r.status,
            "review_notes": r.review_notes,
            "execution_result": json.loads(r.execution_result_json or "{}"),
            "created_at": r.created_at.isoformat(),
        }
        for r in reqs
    ]


@router.post("/approvals/{req_id}/decide")
def decide_approval_request(
    req_id: int,
    payload: ApprovalDecisionRequest,
    user: User = Depends(require_roles("owner", "admin", "manager")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    req = db.query(ApprovalRequest).filter(ApprovalRequest.id == req_id, ApprovalRequest.tenant_id == tid).first()
    if not req:
        raise HTTPException(status_code=404, detail="Solicitação de aprovação não encontrada.")

    if payload.decision == "REJECT":
        req.status = "REJECTED"
        req.reviewed_by_user_id = user.id
        req.review_notes = sanitize_text(payload.review_notes)
        req.reviewed_at = datetime.now(timezone.utc)
        db.commit()
        record_audit_log(db, tenant_id=tid, user_id=user.id, actor=user.email, action="APPROVAL_REJECTED", resource_id=str(req.id))
        return {"id": req.id, "status": req.status}

    if req.is_high_impact:
        token = payload.confirmation_token or ""
        if not verify_high_impact_token(user.id, tid, "CRITICAL_ACTION", token):
            raise HTTPException(status_code=400, detail="Token de confirmação de ação de alto impacto inválido.")

    req.status = "APPROVED"
    req.reviewed_by_user_id = user.id
    req.review_notes = sanitize_text(payload.review_notes)
    req.reviewed_at = datetime.now(timezone.utc)

    data = json.loads(req.payload_json or "{}")
    exec_res: dict[str, Any] = {"approved": True}

    if req.action_type == "SOCIAL_PUBLISH" and "calendar_item_id" in data:
        cal_item = (
            db.query(EditorialCalendarItem)
            .filter(EditorialCalendarItem.id == int(data["calendar_item_id"]), EditorialCalendarItem.tenant_id == tid)
            .first()
        )
        if cal_item:
            cal_item.approval_status = "APPROVED"
            exec_res = validate_and_publish_social_item(db, tenant, cal_item, force_execute=True)

    req.execution_result_json = json.dumps(exec_res, ensure_ascii=False)
    req.status = "EXECUTED"
    db.commit()
    record_audit_log(db, tenant_id=tid, user_id=user.id, actor=user.email, action="APPROVAL_APPROVED_AND_EXECUTED", resource_id=str(req.id))
    return {"id": req.id, "status": req.status, "execution_result": exec_res}


# ==============================================================================
# 16. CENTRAL DE INTEGRAÇÕES OFICIAIS
# ==============================================================================
@router.get("/integrations")
def get_integrations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    conns = ensure_tenant_integrations_seeded(db, tid)
    result = []
    for c in conns:
        meta = INTEGRATION_CATALOG.get(c.provider_key, {})
        result.append(
            {
                "id": c.id,
                "provider_key": c.provider_key,
                "provider_name": c.provider_name,
                "category": c.category,
                "status": c.status,
                "masked_credentials_preview": c.masked_credentials_preview,
                "account_identifier": c.account_identifier,
                "scopes": json.loads(c.scopes_json or "[]"),
                "last_tested_at": c.last_tested_at.isoformat() if c.last_tested_at else None,
                "last_error": c.last_error,
                "setup_guide": {
                    "required_credentials": meta.get("required_credentials", []),
                    "where_to_obtain": meta.get("where_to_obtain", ""),
                    "permissions_required": meta.get("permissions_required", []),
                    "how_to_test": meta.get("how_to_test", ""),
                    "features_unlocked": meta.get("features_unlocked", ""),
                    "oauth_authorize_url": build_oauth_authorization_url(
                        c.provider_key,
                        client_id="YOUR_CLIENT_ID",
                        redirect_uri="https://uniongrowth.72.62.13.62.sslip.io/api/v1/integrations/oauth/callback",
                        state=f"tenant_{tid}_{c.provider_key}",
                    ),
                },
            }
        )
    return result


@router.post("/integrations/connect")
def connect_integration(
    payload: IntegrationConnectRequest,
    user: User = Depends(require_roles("owner", "admin")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    res = save_integration_credentials(
        db=db,
        tenant_id=tid,
        provider_key=payload.provider_key,
        credentials=payload.credentials,
        account_identifier=payload.account_identifier,
        scopes=payload.scopes,
    )
    record_audit_log(
        db,
        tenant_id=tid,
        user_id=user.id,
        actor=user.email,
        action=f"INTEGRATION_CONFIGURED:{payload.provider_key}",
        resource_type="integration",
        resource_id=payload.provider_key,
    )
    return res


@router.post("/integrations/{provider_key}/test")
def test_integration_endpoint(
    provider_key: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    ensure_tenant_integrations_seeded(db, tid)
    conn = (
        db.query(IntegrationConnection)
        .filter(IntegrationConnection.tenant_id == tid, IntegrationConnection.provider_key == provider_key)
        .first()
    )
    if not conn:
        raise HTTPException(status_code=404, detail="Integração não encontrada.")
    return test_integration_connection(db, conn)


@router.post("/integrations/{provider_key}/disconnect")
def disconnect_integration_endpoint(
    provider_key: str,
    user: User = Depends(require_roles("owner", "admin")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    conn = (
        db.query(IntegrationConnection)
        .filter(IntegrationConnection.tenant_id == tid, IntegrationConnection.provider_key == provider_key)
        .first()
    )
    if not conn:
        raise HTTPException(status_code=404, detail="Integração não encontrada.")
    conn.encrypted_credentials = ""
    conn.masked_credentials_preview = ""
    conn.status = "DISCONNECTED"
    conn.last_error = "Desconectado manualmente pelo administrador."
    db.commit()
    record_audit_log(db, tenant_id=tid, user_id=user.id, actor=user.email, action=f"INTEGRATION_DISCONNECTED:{provider_key}")
    return {"provider_key": provider_key, "status": conn.status}


# ==============================================================================
# 17. RELATÓRIOS EXECUTIVOS, AUDITORIA, LOGS & BACKUP
# ==============================================================================
@router.get("/reports/executive")
def generate_executive_report(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    kpis = calculate_tenant_financial_kpis(db, tid)
    briefing = (
        db.query(CEODailyBriefing)
        .filter(CEODailyBriefing.tenant_id == tid)
        .order_by(CEODailyBriefing.id.desc())
        .first()
    ) or generate_ceo_daily_briefing_service(db, tenant)
    integrations = ensure_tenant_integrations_seeded(db, tid)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tenant": {"id": tenant.id, "name": tenant.name, "brand_name": tenant.brand_name, "plan_tier": tenant.plan_tier},
        "financial_performance": kpis,
        "ceo_briefing": {
            "date": briefing.briefing_date,
            "headline": briefing.summary_headline,
            "what_happened": json.loads(briefing.what_happened_json),
            "recommendations": json.loads(briefing.recommendations_json),
        },
        "integrations_summary": {
            "connected": [i.provider_name for i in integrations if i.status == "CONNECTED"],
            "pending_credentials": [i.provider_name for i in integrations if i.status == "PENDING_CREDENTIALS"],
            "error_or_disconnected": [i.provider_name for i in integrations if i.status in ("ERROR", "DISCONNECTED")],
        },
    }


@router.get("/audit-logs")
def get_audit_and_agent_logs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    audits = db.query(AuditLog).filter(AuditLog.tenant_id == tid).order_by(AuditLog.id.desc()).limit(50).all()
    agent_logs = db.query(AgentExecutionLog).filter(AgentExecutionLog.tenant_id == tid).order_by(AgentExecutionLog.id.desc()).limit(50).all()
    return {
        "audit_logs": [
            {
                "id": a.id,
                "actor": a.actor,
                "action": a.action,
                "resource_type": a.resource_type,
                "resource_id": a.resource_id,
                "ip_address": a.ip_address,
                "details": json.loads(a.details_json or "{}"),
                "created_at": a.created_at.isoformat(),
            }
            for a in audits
        ],
        "agent_execution_logs": [
            {
                "id": l.id,
                "workflow_run_id": l.workflow_run_id,
                "agent_id": l.agent_id,
                "agent_name": l.agent_name,
                "task_name": l.task_name,
                "parent_agent_id": l.parent_agent_id,
                "autonomy_level": l.autonomy_level,
                "provider_used": l.provider_used,
                "quality_score": l.quality_score,
                "duration_ms": l.duration_ms,
                "status": l.status,
                "created_at": l.created_at.isoformat(),
            }
            for l in agent_logs
        ],
    }


@router.post("/system/backup", status_code=status.HTTP_201_CREATED)
def trigger_database_backup(
    user: User = Depends(require_roles("owner", "admin")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    info = create_database_backup(db, tenant_id=tid)
    record_audit_log(
        db,
        tenant_id=tid,
        user_id=user.id,
        actor=user.email,
        action="DATABASE_BACKUP_CREATED",
        resource_type="backup",
        resource_id=info["backup_file"],
    )
    return info



# ==============================================================================
# 18. FASE 13 — AUDITORIA REAL, AUTONOMIA E ATIVAÇÃO COMERCIAL
# ==============================================================================
OAUTH_PROVIDER_CONFIG: dict[str, dict[str, str]] = {
    "instagram": {"token_url": "https://graph.facebook.com/v21.0/oauth/access_token"},
    "facebook": {"token_url": "https://graph.facebook.com/v21.0/oauth/access_token"},
    "meta_business": {"token_url": "https://graph.facebook.com/v21.0/oauth/access_token"},
    "youtube": {"token_url": "https://oauth2.googleapis.com/token"},
    "google_search_console": {"token_url": "https://oauth2.googleapis.com/token"},
    "google_analytics_4": {"token_url": "https://oauth2.googleapis.com/token"},
    "linkedin": {"token_url": "https://www.linkedin.com/oauth/v2/accessToken"},
    "tiktok": {"token_url": "https://open.tiktokapis.com/v2/oauth/token/"},
    "pinterest": {"token_url": "https://api.pinterest.com/v5/oauth/token"},
}


def _load_integration_creds(conn: IntegrationConnection) -> dict[str, Any]:
    from app.core.security import decrypt_secret

    try:
        return json.loads(decrypt_secret(conn.encrypted_credentials) or "{}") if conn.encrypted_credentials else {}
    except Exception:
        return {}


@router.get("/social/platforms-audit")
def social_platforms_audit(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    return audit_social_platforms_detailed(db, tid)


@router.get("/integrations/oauth/{provider_key}/start")
def oauth_start(provider_key: str, user: User = Depends(require_roles("owner", "admin")), db: Session = Depends(get_db)):
    from datetime import timedelta as _td

    from app.core.config import settings as _settings

    tid = get_active_tenant_id(user)
    if provider_key not in OAUTH_PROVIDER_CONFIG:
        raise HTTPException(status_code=404, detail="Provedor sem fluxo OAuth suportado.")
    ensure_tenant_integrations_seeded(db, tid)
    conn = db.query(IntegrationConnection).filter(IntegrationConnection.tenant_id == tid, IntegrationConnection.provider_key == provider_key).first()
    creds = _load_integration_creds(conn) if conn else {}
    client_id = str(creds.get("client_id", "")).strip()
    redirect_uri = f"{_settings.PUBLIC_URL.rstrip('/')}/api/v1/integrations/oauth/callback"
    if not client_id or not creds.get("client_secret"):
        return {
            "status": "AGUARDANDO_CREDENCIAIS",
            "message": "Cadastre client_id e client_secret do app OAuth em /integrations/connect (campos 'client_id' e 'client_secret') para iniciar a autorização.",
            "redirect_uri_to_register_in_provider_console": redirect_uri,
            "where_to_obtain": INTEGRATION_CATALOG.get(provider_key, {}).get("where_to_obtain", ""),
        }
    state = create_access_token({"sub": str(user.id), "tid": tid, "prov": provider_key, "kind": "oauth_state"}, expires_delta=_td(minutes=15))
    return {
        "status": "READY",
        "authorize_url": build_oauth_authorization_url(provider_key, client_id=client_id, redirect_uri=redirect_uri, state=state),
        "redirect_uri": redirect_uri,
    }


@router.get("/integrations/oauth/callback")
def oauth_callback(code: str = "", state: str = "", error: str = "", db: Session = Depends(get_db)):
    import httpx
    from fastapi.responses import HTMLResponse

    from app.core.config import settings as _settings
    from app.core.security import decode_access_token

    def page(msg: str, ok: bool) -> HTMLResponse:
        color = "#10B981" if ok else "#EF4444"
        return HTMLResponse(f"<html><body style='font-family:sans-serif;background:#0f172a;color:#fff;padding:40px'><h2 style='color:{color}'>{msg}</h2><a style='color:#818cf8' href='/'>Voltar ao UNION GROWTH OS</a></body></html>")

    if error:
        return page(f"Autorização negada pela plataforma: {sanitize_text(error)}", False)
    try:
        st = decode_access_token(state)
    except HTTPException:
        return page("State OAuth inválido ou expirado.", False)
    if st.get("kind") != "oauth_state" or not code:
        return page("Requisição OAuth inválida.", False)
    tid, prov = int(st["tid"]), str(st["prov"])
    conn = db.query(IntegrationConnection).filter(IntegrationConnection.tenant_id == tid, IntegrationConnection.provider_key == prov).first()
    creds = _load_integration_creds(conn) if conn else {}
    cfg = OAUTH_PROVIDER_CONFIG.get(prov)
    if not conn or not cfg or not creds.get("client_id") or not creds.get("client_secret"):
        return page("Credenciais do app OAuth ausentes.", False)
    redirect_uri = f"{_settings.PUBLIC_URL.rstrip('/')}/api/v1/integrations/oauth/callback"
    try:
        with httpx.Client(timeout=12.0) as client:
            r = client.post(cfg["token_url"], data={
                "grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri,
                "client_id": creds["client_id"], "client_secret": creds["client_secret"],
            })
        if r.status_code != 200:
            return page(f"Falha na troca do código por token (HTTP {r.status_code}).", False)
        tok = r.json()
    except Exception as exc:
        return page(f"Erro de rede na troca de token: {type(exc).__name__}", False)
    access = tok.get("access_token", "")
    if not access:
        return page("A plataforma não retornou access_token.", False)
    merged = {**creds, "access_token": access, "oauth_access_token": access, "page_access_token": access if prov in ("instagram", "facebook") else creds.get("page_access_token", "")}
    if tok.get("refresh_token"):
        merged["refresh_token"] = tok["refresh_token"]
    save_integration_credentials(db=db, tenant_id=tid, provider_key=prov, credentials=merged)
    record_audit_log(db, tenant_id=tid, user_id=int(st["sub"]), actor="oauth-callback", action=f"OAUTH_TOKEN_STORED:{prov}", resource_type="integration", resource_id=prov)
    return page(f"{prov} autorizado. Token armazenado com criptografia Fernet. Complete os identificadores restantes em Integrações.", True)


@router.post("/onboarding/company", status_code=status.HTTP_201_CREATED)
def onboarding_company(
    payload: CompanyOnboardingRequest,
    user: User = Depends(require_roles("owner", "admin")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    existing = None if payload.create_new_tenant else _get_tenant_or_404(db, tid)
    return run_company_onboarding(db, user, payload, existing)


@router.get("/autonomy/panel")
def autonomy_panel(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    return build_autonomy_panel(db, _get_tenant_or_404(db, tid))


@router.put("/autonomy/limits")
def update_autonomy(
    payload: AutonomyConfigUpdateRequest,
    user: User = Depends(require_roles("owner", "admin")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    cfg = save_autonomy_config(db, tenant, payload.autonomy_default_level, payload.agent_autonomy, payload.limits)
    record_audit_log(db, tenant_id=tid, user_id=user.id, actor=user.email, action="AUTONOMY_CONFIG_UPDATED", details={"level": payload.autonomy_default_level, "limits": cfg["limits"]})
    return cfg


@router.post("/marketing/full-operation-pipeline", status_code=status.HTTP_201_CREATED)
def marketing_full_pipeline(
    payload: FullMarketingOperationRequest,
    user: User = Depends(require_roles("owner", "admin", "manager")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    tenant = _get_tenant_or_404(db, tid)
    return run_full_marketing_pipeline(db, user, tenant, payload)


@router.post("/automations/verify-operation")
def automations_verify(user: User = Depends(require_roles("owner", "admin")), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    return verify_all_automations(db, _get_tenant_or_404(db, tid))


@router.get("/automations/operational-log")
def automations_operational_log(hours: int = 24, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tid = get_active_tenant_id(user)
    return build_operational_log(db, _get_tenant_or_404(db, tid), hours=max(1, min(hours, 168)))


@router.get("/ai/status")
def ai_status(user: User = Depends(get_current_user)):
    tid = get_active_tenant_id(user)
    return {"providers": MultiProviderAIAdapter.resolve_provider_status(), "usage_today": AIUsageTracker.get_usage_summary(tid)}


@router.get("/security/audit")
def security_self_audit(user: User = Depends(require_roles("owner", "admin")), db: Session = Depends(get_db)):
    """Auditoria de segurança sem expor segredos."""
    from app.core.config import settings as _s

    default_secret_in_use = _s.SECRET_KEY.startswith("union-growth-os-default") or _s.JWT_SECRET.startswith("union-growth-os-jwt-secret")
    users = db.query(User).all()
    weak = [u.email for u in users if verify_password("UnionGrowth@2026", u.hashed_password)]
    return {
        "default_signing_secrets_in_use": default_secret_in_use,
        "users_with_invalidated_default_password_still_valid": len(weak),
        "users_requiring_password_change": sum(1 for u in users if user_must_change_password(u)),
        "password_hash": "bcrypt (rounds=10)",
        "jwt": f"{_s.JWT_ALGORITHM}, expira em {_s.ACCESS_TOKEN_EXPIRE_MINUTES} min",
        "credentials_encryption": "Fernet (AES-128-CBC + HMAC)",
        "cors_allowed_origins": _s.cors_origins_list,
        "rate_limit_per_minute": _s.RATE_LIMIT_PER_MINUTE,
        "login_bruteforce_protection": "8 falhas / 5 min por IP+e-mail",
        "tenant_isolation": "Todas as consultas filtram tenant_id; X-Tenant-Id só aceito para tenants do próprio owner",
        "environment": _s.ENVIRONMENT,
    }
