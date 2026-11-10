"""FASE 13 services: company onboarding, autonomy limits, 10-step marketing pipeline, 24/7 verification."""
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.agents.orchestrator import (
    AGENT_REGISTRY,
    DEFAULT_AUTONOMY_LIMITS,
    CentralOrchestrator,
    calculate_tenant_financial_kpis,
    get_effective_autonomy_level,
    get_tenant_autonomy_config,
)
from app.core.security import sanitize_text
from app.models.entities import (
    AgentExecutionLog,
    ApprovalRequest,
    AuditLog,
    AutomationExecution,
    AutomationRule,
    Competitor,
    CopyItem,
    CreativeAsset,
    EditorialCalendarItem,
    MarketingCampaign,
    MarketingPersona,
    SchedulerHeartbeat,
    SEOArticle,
    StrategicGoal,
    Tenant,
)
from app.schemas.contracts import AgentTaskContract
from app.services.automation_scheduler import BOOT_ID, execute_automation_rule, scheduler
from app.services.creative_and_copy_engine import generate_creative_asset, generate_persuasive_copy
from app.services.integrations_and_social_engine import (
    PLATFORM_CONSTRAINTS,
    ensure_tenant_integrations_seeded,
    validate_and_publish_social_item,
)
from app.services.seo_and_market_engine import (
    analyze_competitor_public,
    generate_seo_factory_article,
    perform_real_seo_audit,
    research_keywords_and_clusters,
)


# ---------------------------------------------------------------------------
# ETAPA 9 — Autonomy & limits
# ---------------------------------------------------------------------------
def save_autonomy_config(db: Session, tenant: Tenant, level: int, agent_levels: dict[str, int], limits: dict[str, Any]) -> dict[str, Any]:
    clean_agents = {k: int(v) for k, v in agent_levels.items() if k in AGENT_REGISTRY and int(v) in (1, 2, 3)}
    merged = {**DEFAULT_AUTONOMY_LIMITS, **{k: v for k, v in limits.items() if k in DEFAULT_AUTONOMY_LIMITS}}
    merged["require_approval_for_financial_actions"] = True  # imutável: ação financeira sempre exige aprovação
    payload = {**clean_agents, "_limits": merged}
    tenant.autonomy_default_level = level
    tenant.agent_autonomy_json = json.dumps(payload, ensure_ascii=False)
    db.commit()
    return get_tenant_autonomy_config(tenant)


def _today_start() -> datetime:
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)


def get_daily_usage(db: Session, tenant_id: int) -> dict[str, Any]:
    start = _today_start()
    pubs = (
        db.query(EditorialCalendarItem)
        .filter(
            EditorialCalendarItem.tenant_id == tenant_id,
            EditorialCalendarItem.publish_status == "PUBLISHED",
            EditorialCalendarItem.platform != "blog",
            EditorialCalendarItem.created_at >= start,
        )
        .count()
    )
    msgs = (
        db.query(AuditLog)
        .filter(AuditLog.tenant_id == tenant_id, AuditLog.action.like("MESSAGE_SENT%"), AuditLog.created_at >= start)
        .count()
    )
    active_campaigns = (
        db.query(MarketingCampaign)
        .filter(MarketingCampaign.tenant_id == tenant_id, MarketingCampaign.status == "ACTIVE")
        .count()
    )
    return {"publications_today": pubs, "messages_today": msgs, "active_campaigns": active_campaigns}


def check_autonomy_limit(db: Session, tenant: Tenant, action: str, amount: float = 0.0) -> tuple[bool, str]:
    """action: PUBLISH | MESSAGE | CAMPAIGN | BUDGET | EXTERNAL | COMMERCIAL_CHANGE."""
    cfg = get_tenant_autonomy_config(tenant)
    lim = cfg["limits"]
    usage = get_daily_usage(db, tenant.id)
    if action == "PUBLISH" and usage["publications_today"] >= int(lim["max_daily_publications"]):
        return False, f"Limite diário de publicações atingido ({lim['max_daily_publications']})."
    if action == "MESSAGE" and usage["messages_today"] >= int(lim["max_daily_messages"]):
        return False, f"Limite diário de mensagens atingido ({lim['max_daily_messages']})."
    if action == "CAMPAIGN" and usage["active_campaigns"] >= int(lim["max_active_campaigns"]):
        return False, f"Limite de campanhas ativas atingido ({lim['max_active_campaigns']})."
    if action == "BUDGET":
        return False, "Ação financeira exige aprovação humana (sempre)."
    if action == "EXTERNAL" and not lim["allow_external_actions"]:
        return False, "Ações externas autônomas desabilitadas (allow_external_actions=false)."
    if action == "COMMERCIAL_CHANGE" and not lim["allow_commercial_changes"]:
        return False, "Alterações comerciais autônomas desabilitadas (allow_commercial_changes=false)."
    return True, "OK"


def build_autonomy_panel(db: Session, tenant: Tenant) -> dict[str, Any]:
    cfg = get_tenant_autonomy_config(tenant)
    usage = get_daily_usage(db, tenant.id)
    logs = (
        db.query(AgentExecutionLog)
        .filter(AgentExecutionLog.tenant_id == tenant.id)
        .order_by(AgentExecutionLog.id.desc())
        .limit(30)
        .all()
    )
    approvals = (
        db.query(ApprovalRequest).filter(ApprovalRequest.tenant_id == tenant.id).order_by(ApprovalRequest.id.desc()).limit(50).all()
    )
    return {
        "config": cfg,
        "usage_today": usage,
        "agents": [
            {
                "agent_id": aid,
                "name": meta["name"],
                "autonomy_level": cfg["agent_autonomy"].get(aid, 2),
                "level_label": {1: "Assistido (tudo exige aprovação)", 2: "Semiautônomo (ações externas exigem aprovação)", 3: "Autônomo (dentro dos limites)"}[
                    cfg["agent_autonomy"].get(aid, 2)
                ],
            }
            for aid, meta in AGENT_REGISTRY.items()
        ],
        "executed_tasks": [
            {
                "id": l.id,
                "agent_id": l.agent_id,
                "task_name": l.task_name,
                "status": l.status,
                "provider_used": l.provider_used,
                "created_at": l.created_at.isoformat(),
            }
            for l in logs
        ],
        "pending_tasks": [
            {
                "id": a.id,
                "agent_id": a.agent_id,
                "action_type": a.action_type,
                "title": a.title,
                "is_high_impact": a.is_high_impact,
                "created_at": a.created_at.isoformat(),
            }
            for a in approvals
            if a.status == "PENDING"
        ],
        "decided_tasks": [
            {"id": a.id, "title": a.title, "status": a.status, "action_type": a.action_type}
            for a in approvals
            if a.status != "PENDING"
        ][:15],
        "policy": "Toda ação financeira/alto impacto exige aprovação humana independentemente do nível de autonomia.",
    }


# ---------------------------------------------------------------------------
# ETAPA 8 — Onboarding wizard (no invented facts)
# ---------------------------------------------------------------------------
def _clean_list(values: list[str]) -> list[str]:
    return [sanitize_text(v) for v in values if v and v.strip()]


def run_company_onboarding(db: Session, user, payload, existing_tenant: Tenant | None) -> dict[str, Any]:
    segment = sanitize_text(payload.segment)
    products = _clean_list(payload.products)
    services = _clean_list(payload.services)
    ident = payload.visual_identity or {}
    brand_name = sanitize_text(ident.get("brand_name") or payload.name)

    if existing_tenant is None:
        slug = f"{re.sub(r'[^a-z0-9]+', '-', payload.name.lower()).strip('-') or 'empresa'}-{uuid.uuid4().hex[:6]}"
        tenant = Tenant(name=sanitize_text(payload.name), slug=slug, brand_name=brand_name, owner_email=user.email, plan_tier="ENTERPRISE", autonomy_default_level=2)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    else:
        tenant = existing_tenant
        tenant.name = sanitize_text(payload.name)
        tenant.brand_name = brand_name

    tenant.niche = segment
    tenant.domain = sanitize_text(payload.website)
    tenant.target_audience = sanitize_text(payload.target_audience)
    tenant.primary_color = ident.get("primary_color") or tenant.primary_color
    tenant.secondary_color = ident.get("secondary_color") or tenant.secondary_color
    tenant.products_json = json.dumps(products, ensure_ascii=False)
    tenant.services_json = json.dumps(services, ensure_ascii=False)
    tenant.social_links_json = json.dumps({k: sanitize_text(v) for k, v in payload.social_networks.items() if v}, ensure_ascii=False)
    tenant.strategy_summary = sanitize_text(payload.description)
    db.commit()
    db.refresh(tenant)

    ensure_tenant_integrations_seeded(db, tenant.id)
    from app.services.automation_scheduler import ensure_tenant_automations_seeded

    ensure_tenant_automations_seeded(db, tenant.id)

    # --- Gaps: what the user did NOT inform (never invented) ---
    gaps = []
    if not payload.website:
        gaps.append("Site não informado: auditoria SEO técnica e PageSpeed não podem ser executadas.")
    if not payload.social_networks:
        gaps.append("Nenhuma rede social informada: calendário gerado apenas para canais internos (blog).")
    if not payload.competitors:
        gaps.append("Concorrentes não informados: análise competitiva não executada.")
    if not payload.commercial_goals:
        gaps.append("Metas comerciais não informadas: nenhuma meta foi criada (não inventamos metas).")
    if not products and not services:
        gaps.append("Produtos/serviços não informados.")

    # --- Competitors: real public inspection ---
    competitors_out = []
    for c in payload.competitors[:5]:
        url = (c.get("website") or c.get("website_url") or "").strip()
        cname = sanitize_text(c.get("name") or url)
        if not url:
            continue
        comp = Competitor(tenant_id=tenant.id, name=cname, website_url=url, category="Concorrente informado no onboarding")
        db.add(comp)
        db.commit()
        db.refresh(comp)
        try:
            analyze_competitor_public(db, tenant, comp)
        except Exception:
            pass
        competitors_out.append({"id": comp.id, "name": comp.name, "website_url": comp.website_url})

    # --- Goals: exactly what user informed, labeled GOAL ---
    goals_out = []
    for g in payload.commercial_goals[:10]:
        try:
            target = float(g.get("target_value", 0))
        except (TypeError, ValueError):
            continue
        if target <= 0:
            continue
        goal = StrategicGoal(
            tenant_id=tenant.id,
            title=sanitize_text(str(g.get("title") or g.get("metric_name") or "Meta comercial")),
            period=str(g.get("period", "MONTHLY")).upper() if str(g.get("period", "MONTHLY")).upper() in ("MONTHLY", "QUARTERLY", "ANNUAL") else "MONTHLY",
            metric_name=sanitize_text(str(g.get("metric_name") or g.get("title") or "Meta")),
            target_value=target,
            current_value=float(g.get("current_value", 0) or 0),
            unit=str(g.get("unit", "BRL")),
            data_origin="GOAL",
            priority=str(g.get("priority", "HIGH")).upper(),
            deadline=str(g.get("deadline", "")),
        )
        db.add(goal)
        goals_out.append({"title": goal.title, "target_value": goal.target_value, "origin": "GOAL"})
    db.commit()

    # --- SEO plan: real keyword research on informed segment ---
    seed = f"{segment} {payload.region}".strip() if payload.region and "Brasil" not in payload.region else segment
    cluster = research_keywords_and_clusters(db, tenant, seed)
    seo_audit = None
    if payload.website:
        try:
            seo_audit = perform_real_seo_audit(db, tenant, payload.website, segment)
        except Exception:
            seo_audit = None

    # --- Persona from informed audience only ---
    persona = MarketingPersona(
        tenant_id=tenant.id,
        name=f"Público-alvo informado: {sanitize_text(payload.target_audience)[:120]}",
        role_segment=segment,
        demographics=f"Região: {sanitize_text(payload.region)}",
        pains_json="[]",
        desires_json="[]",
        objections_json="[]",
        channels_json=json.dumps(list(payload.social_networks.keys()), ensure_ascii=False),
        value_proposition=sanitize_text(payload.description)[:500],
    )
    db.add(persona)
    db.commit()

    # --- Diagnosis (deterministic from provided data) ---
    diagnosis = {
        "empresa": tenant.name,
        "segmento": segment,
        "regiao": payload.region,
        "resumo_informado": sanitize_text(payload.description),
        "ofertas": {"produtos": products, "servicos": services},
        "presenca_digital": {
            "site": payload.website or "NÃO INFORMADO",
            "redes_sociais": payload.social_networks or "NÃO INFORMADAS",
            "auditoria_seo_score": seo_audit.overall_score if seo_audit else None,
            "auditoria_seo_origem": seo_audit.data_origin if seo_audit else "NAO_EXECUTADA",
        },
        "concorrentes_analisados": len(competitors_out),
        "lacunas_de_informacao": gaps,
        "origem": "DETERMINISTIC_PYTHON_ENGINE — apenas dados informados no cadastro; nenhuma métrica de mercado foi inventada.",
    }

    long_tails = json.loads(cluster.long_tail_keywords_json)
    marketing_plan = {
        "posicionamento": f"{brand_name} em {segment} para {payload.target_audience}",
        "tom_de_voz": ident.get("tone_of_voice", ""),
        "funil": {"TOFU": "Conteúdo educativo e SEO", "MOFU": "Provas, comparativos e materiais ricos", "BOFU": "Diagnóstico/proposta comercial"},
        "canais_priorizados": list(payload.social_networks.keys()) + ["blog/SEO"],
        "orcamento_midia": "R$ 0,00 — nenhum gasto é executado sem aprovação humana",
        "origem": "TEMPLATE_ENGINE parametrizado com os dados do cadastro",
    }
    seo_plan = {
        "palavra_chave_semente": seed,
        "intencao_de_busca": cluster.search_intent,
        "palavras_cauda_longa": long_tails[:12],
        "clusters": json.loads(cluster.cluster_topics_json),
        "fonte_palavras_chave": cluster.source,
        "volume_de_busca": "NÃO DISPONÍVEL — conecte o Google Search Console para dados reais",
        "origem": "REAL (autocomplete público) + ESTIMATED (clusters)",
    }
    commercial_plan = {
        "metas_informadas": goals_out,
        "etapas_funil_crm": ["NEW_LEAD", "QUALIFICATION", "PROPOSAL", "NEGOTIATION", "CLOSED_WON"],
        "acao_recomendada": "Cadastrar leads reais no CRM com consentimento LGPD; lead scoring determinístico é aplicado automaticamente.",
        "origem": "DETERMINISTIC_PYTHON_ENGINE",
    }

    # --- Social calendar only for networks informed (+ blog) ---
    calendar_out = []
    base = datetime.now(timezone.utc)
    networks = [n for n in payload.social_networks.keys() if n.lower() in PLATFORM_CONSTRAINTS]
    networks.append("blog")
    kw_topics = long_tails[:len(networks)] or [segment]
    for idx, plat in enumerate(networks):
        topic = kw_topics[idx % len(kw_topics)]
        best = PLATFORM_CONSTRAINTS[plat.lower()]["recommended_best_times"][0]
        item = EditorialCalendarItem(
            tenant_id=tenant.id,
            title=f"[{plat.upper()}] {topic}"[:250],
            platform=plat.lower(),
            content_format="ARTICLE" if plat == "blog" else "POST",
            caption=f"{brand_name}: {topic}. {sanitize_text(payload.description)[:300]}",
            hashtags_json=json.dumps([f"#{re.sub(r'[^a-z0-9]', '', segment.lower())[:20]}"], ensure_ascii=False),
            scheduled_for=f"{(base + timedelta(days=idx + 1)).strftime('%Y-%m-%d')} {best}",
            best_time_rationale=f"Janela recomendada para {plat}",
            approval_status="PENDING_REVIEW",
            publish_status="QUEUED",
            data_origin="ESTIMATED",
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        calendar_out.append({"id": item.id, "platform": plat, "title": item.title, "scheduled_for": item.scheduled_for})

    # --- First campaigns (no budget, no invented results) ---
    campaigns_out = []
    for name, ctype, channel, obj in [
        (f"Campanha de Autoridade Orgânica — {brand_name}", "ACQUISITION", "SEO + Social Orgânico", f"Gerar visibilidade orgânica em {segment} para {payload.target_audience}"),
        (f"Campanha de Geração de Demanda — {brand_name}", "LAUNCH", "Conteúdo + CRM", "Captar leads com consentimento e iniciar relacionamento"),
    ]:
        camp = MarketingCampaign(
            tenant_id=tenant.id, name=name, campaign_type=ctype, channel=channel, objective=obj,
            budget_planned=0.0, spend_real=0.0, revenue_attributed=0.0, data_origin="GOAL", status="PLANNED",
            monthly_plan_json=json.dumps({"origem": "TEMPLATE_ENGINE", "observacao": "Sem verba; resultados reais serão registrados via integrações/CRM."}, ensure_ascii=False),
            start_date=base.strftime("%Y-%m-%d"),
        )
        db.add(camp)
        db.commit()
        db.refresh(camp)
        campaigns_out.append({"id": camp.id, "name": camp.name, "status": camp.status})

    db.add(AuditLog(tenant_id=tenant.id, user_id=user.id, actor=user.email, action="COMPANY_ONBOARDING_COMPLETED", resource_type="tenant", resource_id=str(tenant.id)))
    db.commit()

    return {
        "tenant_id": tenant.id,
        "tenant_slug": tenant.slug,
        "switch_header": {"X-Tenant-Id": tenant.id},
        "diagnostico_empresarial": diagnosis,
        "plano_de_marketing": marketing_plan,
        "plano_de_seo": seo_plan,
        "calendario_redes_sociais": calendar_out,
        "plano_comercial": commercial_plan,
        "metas": goals_out,
        "primeiras_campanhas": campaigns_out,
        "concorrentes": competitors_out,
        "lacunas_de_informacao": gaps,
    }


# ---------------------------------------------------------------------------
# ETAPA 4 — 10-step marketing pipeline
# ---------------------------------------------------------------------------
def run_full_marketing_pipeline(db: Session, user, tenant: Tenant, req) -> dict[str, Any]:
    run_id = f"pipeline-{uuid.uuid4().hex[:10]}"
    steps: list[dict[str, Any]] = []
    kw = (req.target_keyword or tenant.niche or tenant.brand_name).strip()
    offer = (req.product_or_offer or (json.loads(tenant.products_json or "[]") or [tenant.brand_name])[0]).strip()
    platforms = [p.lower() for p in req.platforms if p.lower() in PLATFORM_CONSTRAINTS] or ["blog"]

    def add_step(n: int, agent: str, title: str, status: str, origin: str, detail: dict[str, Any]) -> None:
        steps.append({"step": n, "agent": agent, "title": title, "status": status, "response_origin": origin, "detail": detail})

    def dispatch(agent_id: str, task: str, params: dict[str, Any]):
        contract = AgentTaskContract(
            workflow_run_id=run_id, sender_agent="PIPELINE_ORCHESTRATOR", target_agent=agent_id, task_name=task,
            tenant_id=tenant.id, autonomy_level=get_effective_autonomy_level(tenant, agent_id), parameters=params,
        )
        return CentralOrchestrator.dispatch_task(db, tenant, contract)

    # 1. CEO
    ceo = dispatch("AGENT_01_CEO", "analyze_kpis_for_campaign", {})
    kpis = calculate_tenant_financial_kpis(db, tenant.id)
    add_step(1, "AI CEO", "Análise de indicadores", "COMPLETED", ceo.response_origin, {
        "headline": ceo.summary, "kpis_reais": {"receita": kpis["real_revenue"], "margem_pct": kpis["margin_pct"], "leads": kpis["leads_total"], "origem_dos_dados": kpis["data_origin"]},
        "recomendacoes": ceo.recommendations[:3],
    })

    # 2. CMO (budget > 0 => approval required, never executed autonomously)
    budget_note = "Sem verba de mídia"
    approval_budget_id = None
    if req.budget_planned_brl > 0:
        ar = ApprovalRequest(
            tenant_id=tenant.id, agent_id="AGENT_02_CMO", action_type="PAID_CAMPAIGN_BUDGET",
            title=f"Aprovar verba de mídia R$ {req.budget_planned_brl:,.2f} — {req.campaign_name}",
            payload_json=json.dumps({"budget_brl": req.budget_planned_brl, "run_id": run_id}), is_high_impact=True, status="PENDING",
        )
        db.add(ar)
        db.commit()
        db.refresh(ar)
        approval_budget_id = ar.id
        budget_note = f"Verba R$ {req.budget_planned_brl:,.2f} PENDENTE de aprovação humana (aprovação #{ar.id})"
    cmo = dispatch("AGENT_02_CMO", "create_campaign_strategy", {"campaign_name": req.campaign_name, "budget_planned": 0.0})
    add_step(2, "AI CMO", "Estratégia de marketing", "COMPLETED", cmo.response_origin, {
        "campaign_id": cmo.structured_output.get("campaign_id"), "plano": cmo.structured_output.get("monthly_plan"), "verba": budget_note,
    })
    campaign_id = cmo.structured_output.get("campaign_id")

    # 3. SEO
    cluster = research_keywords_and_clusters(db, tenant, kw)
    article = generate_seo_factory_article(db, tenant, topic=f"Guia Completo: {kw.title()}", target_keyword=kw)
    seo_detail: dict[str, Any] = {
        "cluster_id": cluster.id, "palavras_cauda_longa": json.loads(cluster.long_tail_keywords_json)[:6],
        "fonte_palavras_chave": cluster.source, "artigo_id": article.id, "artigo_titulo": article.title,
        "artigo_palavras": article.word_count, "volume_de_busca": "NÃO DISPONÍVEL (requer Google Search Console)",
    }
    if tenant.domain:
        try:
            audit = perform_real_seo_audit(db, tenant, tenant.domain, kw)
            seo_detail["auditoria"] = {"score": audit.overall_score, "origem": audit.data_origin, "pagespeed": json.loads(audit.generated_schema_json).get("pagespeed_insights")}
        except Exception as exc:
            seo_detail["auditoria"] = f"falhou: {exc}"
    add_step(3, "AI SEO Director", "Pesquisa de oportunidades", "COMPLETED", "DETERMINISTIC_PYTHON_ENGINE (HTTP/autocomplete reais) + TEMPLATE_ENGINE (artigo)", seo_detail)

    # 4. Social calendar
    base = datetime.now(timezone.utc)
    items: list[EditorialCalendarItem] = []
    for idx, plat in enumerate(platforms):
        best = PLATFORM_CONSTRAINTS[plat]["recommended_best_times"][0]
        it = EditorialCalendarItem(
            tenant_id=tenant.id, title=f"[{plat.upper()}] {req.campaign_name}"[:250], platform=plat,
            content_format="ARTICLE" if plat == "blog" else "POST", caption="(rascunho — será preenchido pelo Copywriter)",
            hashtags_json=json.dumps([f"#{re.sub(r'[^a-z0-9]', '', kw.lower())[:20]}"]),
            scheduled_for=f"{(base + timedelta(days=idx + 1)).strftime('%Y-%m-%d')} {best}",
            best_time_rationale=f"Janela recomendada para {plat}", approval_status="PENDING_REVIEW", publish_status="DRAFT",
        )
        db.add(it)
        db.commit()
        db.refresh(it)
        items.append(it)
    add_step(4, "AI Social Media", "Calendário editorial", "COMPLETED", "TEMPLATE_ENGINE", {"itens": [{"id": i.id, "plataforma": i.platform, "agendado_para": i.scheduled_for} for i in items]})

    # 5. Copy
    copy_obj = generate_persuasive_copy(
        db=db, tenant=tenant, title=f"Copy — {req.campaign_name}", copy_type="AD_COPY", framework="AIDA",
        product_or_offer=offer, target_audience=tenant.target_audience, key_benefit=f"resultados reais em {kw}",
    )
    add_step(5, "AI Copywriter", "Redação dos conteúdos", "COMPLETED", "TEMPLATE_ENGINE (framework AIDA)", {"copy_id": copy_obj.id, "variante_a": copy_obj.variant_a[:400], "variante_b": copy_obj.variant_b[:400]})

    # 6. Creative
    asset = generate_creative_asset(
        db=db, tenant=tenant, title=f"Arte — {req.campaign_name}", asset_type="SOCIAL_POST", platform=platforms[0] if platforms[0] != "blog" else "instagram",
        headline_text=offer[:70], subheadline_text=f"{kw}"[:90], cta_text="Saiba mais", campaign_id=campaign_id,
    )
    add_step(6, "AI Creative Studio", "Produção das artes", "COMPLETED", "DETERMINISTIC_PYTHON_ENGINE (Pillow PNG)", {"asset_id": asset.id, "dimensoes": asset.dimensions, "arquivo": asset.file_path})

    # 7. Prepare publications
    for it in items:
        it.caption = (copy_obj.variant_a or "")[: PLATFORM_CONSTRAINTS[it.platform]["max_chars"]]
        it.media_asset_id = asset.id
        it.publish_status = "QUEUED"
    db.commit()
    add_step(7, "Orquestrador", "Preparação das publicações", "COMPLETED", "DETERMINISTIC_PYTHON_ENGINE", {"preparadas": len(items), "ativo_visual_id": asset.id})

    # 8 + 9. Approval / publish (respects autonomy, limits, official API)
    level = get_effective_autonomy_level(tenant, "AGENT_04_SOCIAL")
    ok_ext, why_ext = check_autonomy_limit(db, tenant, "EXTERNAL")
    auto_exec = bool(req.auto_approve_execution and level >= 3 and ok_ext)
    results = []
    for it in items:
        if auto_exec:
            ok_pub, why_pub = check_autonomy_limit(db, tenant, "PUBLISH") if it.platform != "blog" else (True, "OK")
            if ok_pub:
                it.approval_status = "AUTO_APPROVED"
                db.commit()
            else:
                results.append({"item_id": it.id, "platform": it.platform, "status": "BLOCKED_BY_LIMIT", "message": why_pub})
                continue
        res = validate_and_publish_social_item(db, tenant, it, force_execute=False)
        results.append({"item_id": it.id, "platform": it.platform, **res})
    approvals_pending = [r for r in results if r.get("status") == "PENDING_REVIEW"]
    add_step(8, "Usuário / Autonomia", "Aprovação ou execução autorizada",
             "AWAITING_USER_APPROVAL" if approvals_pending else "COMPLETED", "POLICY_ENGINE", {
        "execucao_automatica": auto_exec,
        "motivo": "Autonomia nível 3 + allow_external_actions habilitado" if auto_exec else f"Aprovação humana exigida (nível {level}; {why_ext})",
        "pendentes_na_central_de_aprovacoes": len(approvals_pending), "aprovacao_de_verba": approval_budget_id,
    })
    published = [r for r in results if r.get("status") == "PUBLISHED"]
    waiting = [r for r in results if r.get("status") == "WAITING_CREDENTIALS"]
    add_step(9, "Central de Publicação", "Publicação via API oficial",
             "COMPLETED" if published else "WAITING", "OFFICIAL_API_ADAPTER", {
        "publicadas": published, "aguardando_credenciais": [{"platform": w["platform"], "message": w.get("message")} for w in waiting],
        "pendentes_de_aprovacao": [r["platform"] for r in approvals_pending],
        "nota": "Nenhuma publicação externa é simulada: sem OAuth/credenciais ou sem aprovação, o item permanece na fila.",
    })

    # 10. Analytics (real only)
    cal_all = db.query(EditorialCalendarItem).filter(EditorialCalendarItem.id.in_([i.id for i in items])).all()
    analytics = {
        "itens_total": len(cal_all),
        "itens_publicados_reais": sum(1 for c in cal_all if c.publish_status == "PUBLISHED"),
        "itens_na_fila": sum(1 for c in cal_all if c.publish_status in ("QUEUED", "WAITING_CREDENTIALS")),
        "metricas_de_engajamento": "NÃO DISPONÍVEL — requer posts publicados em rede conectada (alcance, cliques, leads reais).",
        "leads_atribuidos": "NÃO DISPONÍVEL — requer rastreamento/CRM com origem da campanha.",
        "origem": "REAL (contagens do banco) — nenhuma métrica de desempenho foi inventada",
    }
    if campaign_id:
        camp = db.query(MarketingCampaign).filter(MarketingCampaign.id == campaign_id).first()
        if camp:
            plan = json.loads(camp.monthly_plan_json or "{}")
            plan["pipeline_run_id"] = run_id
            plan["analytics_snapshot"] = analytics
            camp.monthly_plan_json = json.dumps(plan, ensure_ascii=False)
            db.commit()
    add_step(10, "Módulo de Análise", "Registro de resultados reais", "COMPLETED", "DETERMINISTIC_PYTHON_ENGINE", analytics)

    db.add(AuditLog(tenant_id=tenant.id, user_id=user.id, actor=user.email, action="FULL_MARKETING_PIPELINE_RUN", resource_type="pipeline", resource_id=run_id,
                    details_json=json.dumps({"steps": len(steps), "published": len(published), "waiting": len(waiting)})))
    db.commit()
    return {
        "run_id": run_id, "campaign_id": campaign_id, "campaign_name": req.campaign_name, "steps": steps,
        "summary": {
            "passos_concluidos": sum(1 for s in steps if s["status"] == "COMPLETED"),
            "aguardando_usuario": sum(1 for s in steps if s["status"] == "AWAITING_USER_APPROVAL"),
            "aguardando_credenciais": len(waiting),
            "publicadas": len(published),
        },
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# ETAPA 7 — Automation verification
# ---------------------------------------------------------------------------
def verify_all_automations(db: Session, tenant: Tenant) -> dict[str, Any]:
    rules = db.query(AutomationRule).filter(AutomationRule.tenant_id == tenant.id).order_by(AutomationRule.id.asc()).all()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    rows = []
    for r in rules:
        key = f"verify-{stamp}-{r.id}"
        first = execute_automation_rule(db, r, idempotency_key=key)
        second = execute_automation_rule(db, r, idempotency_key=key)
        count = db.query(AutomationExecution).filter(AutomationExecution.rule_id == r.id, AutomationExecution.idempotency_key == key).count()
        rows.append({
            "rule_id": r.id, "code_key": r.code_key, "trigger": r.trigger_type, "first_status": first.status,
            "idempotent_same_execution": first.id == second.id, "executions_for_key": count, "duration_ms": first.duration_ms,
            "registered_in_scheduler": (scheduler.get_job(f"rule-{r.id}") is not None) if r.trigger_type == "CRON" else None,
        })
    # retry/backoff proof on first rule
    retry_row = None
    if rules:
        ex = execute_automation_rule(db, rules[0], idempotency_key=f"verify-retry-{stamp}", simulate_failure_once=True)
        retry_row = {"status": ex.status, "attempt_number": ex.attempt_number, "message": ex.error_message}
    return {
        "verified_at": datetime.now(timezone.utc).isoformat(), "total_rules": len(rules),
        "all_succeeded": all(r["first_status"] in ("SUCCESS", "RETRIED") for r in rows),
        "all_idempotent": all(r["idempotent_same_execution"] and r["executions_for_key"] == 1 for r in rows),
        "retry_test": retry_row, "rules": rows,
        "scheduler": {"running": scheduler.running, "jobs": [j.id for j in scheduler.get_jobs()], "boot_id": BOOT_ID},
    }


def build_operational_log(db: Session, tenant: Tenant, hours: int = 24) -> dict[str, Any]:
    since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=hours)
    hb = db.query(SchedulerHeartbeat).filter(SchedulerHeartbeat.created_at >= since).order_by(SchedulerHeartbeat.id.asc()).all()
    first_hb = db.query(SchedulerHeartbeat).order_by(SchedulerHeartbeat.id.asc()).first()
    execs = (
        db.query(AutomationExecution)
        .filter(AutomationExecution.tenant_id == tenant.id, AutomationExecution.started_at >= since)
        .order_by(AutomationExecution.id.asc())
        .all()
    )
    boots = sorted({h.boot_id for h in hb})
    covered_h = 0.0
    if hb:
        covered_h = round((hb[-1].created_at - hb[0].created_at).total_seconds() / 3600, 2)
    by_status: dict[str, int] = {}
    for e in execs:
        by_status[e.status] = by_status.get(e.status, 0) + 1
    dup = (
        db.query(AutomationExecution.rule_id, AutomationExecution.idempotency_key, func.count(AutomationExecution.id))
        .filter(AutomationExecution.tenant_id == tenant.id, AutomationExecution.status.in_(("SUCCESS", "RETRIED")))
        .group_by(AutomationExecution.rule_id, AutomationExecution.idempotency_key)
        .having(func.count(AutomationExecution.id) > 1)
        .count()
    )
    return {
        "window_hours": hours,
        "monitoring_started_at": first_hb.created_at.isoformat() if first_hb else None,
        "observed_hours_covered": covered_h,
        "twenty_four_hour_goal_reached": covered_h >= 24.0,
        "heartbeats": len(hb),
        "boots_observed": boots,
        "restarts_observed": max(0, len(boots) - 1),
        "executions_by_status": by_status,
        "duplicate_success_executions": dup,
        "recent_events": [{"kind": h.kind, "boot_id": h.boot_id, "jobs": h.jobs_count, "note": h.note, "at": h.created_at.isoformat()} for h in hb[-40:]],
        "recent_executions": [
            {"rule_id": e.rule_id, "status": e.status, "attempt": e.attempt_number, "key": e.idempotency_key, "at": e.started_at.isoformat()} for e in execs[-40:]
        ],
        "note": "Evidência persistida em PostgreSQL. A meta de 24h só é marcada como atingida quando o intervalo observado real ≥ 24h.",
    }

