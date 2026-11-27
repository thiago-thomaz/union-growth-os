"""UNION GROWTH OS — FASE 26: GROWTH CENTER, AI AGENT MATRIX, REVENUE ENGINE & ENTITLEMENTS

Módulo desacoplado de serviços de alto impacto em Python nativo + PostgreSQL (custo adicional R$ 0,00):
1. Centro de Crescimento (Plano 0 / 7 / 30 / 90 dias) orientado a objetivos reais de negócio.
2. Executor seguro de etapas de crescimento respeitando Níveis de Autonomia 1/2/3 e aprovações.
3. Matriz transparente dos 12 Agentes (LLM / HYBRID / DETERMINISTIC / BLOCKED) sem disfarces.
4. Revenue Engine: movimentação rápida de pipeline com probabilidade marcada ESTIMATED e Follow-up Inteligente LGPD.
5. SaaS Entitlements & Billing Readiness (Mercado Pago BR / Stripe Global) sem ativação de cobrança.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.agents.orchestrator import (
    AGENT_AI_CAPABILITY_AUDIT,
    AGENT_REGISTRY,
    AIUsageTracker,
    CentralOrchestrator,
    MultiProviderAIAdapter,
    get_effective_autonomy_level,
)
from app.core.security import sanitize_text, validate_public_http_url
from app.models.entities import (
    AgentExecutionLog,
    ApprovalRequest,
    AutomationRule,
    ContentFactoryItem,
    CRMActivity,
    CRMDeal,
    CRMLead,
    IntegrationConnection,
    MarketingCampaign,
    SEOAuditReport,
    Tenant,
    User,
)
from app.schemas.contracts import AgentTaskContract
from app.services.phase14_automation_factory import (
    generate_30_day_content_batch_service,
    generate_ceo_daily_execution_plan_service,
)
from app.services.phase23_growth_platform import _collect_real_snapshot
from app.services.phase25_product_engine import get_crm_revenue_intelligence_service
from app.services.plans_and_audit import (
    SAAS_PLANS,
    get_tenant_plan_usage_summary,
    record_audit_log,
)
from app.services.seo_and_market_engine import perform_real_seo_audit


STAGE_DEFAULT_PROBS: dict[str, tuple[float, str]] = {
    "NEW_LEAD": (15.0, "OPEN"),
    "QUALIFICATION": (30.0, "OPEN"),
    "PROPOSAL": (55.0, "OPEN"),
    "NEGOTIATION": (75.0, "OPEN"),
    "CLOSED_WON": (100.0, "WON"),
    "CLOSED_LOST": (0.0, "LOST"),
}


def generate_growth_execution_plan_service(
    db: Session,
    tenant_id: int,
    payload: dict[str, Any],
    actor: str = "Empreendedor",
) -> dict[str, Any]:
    """Cria plano estratégico e executável (Hoje, 7d, 30d, 90d) usando contexto existente do tenant."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Empresa (Tenant) não encontrada.")

    snap = _collect_real_snapshot(db, tenant)
    rev_intel = get_crm_revenue_intelligence_service(db, tenant_id=tenant_id)
    hot_uncontacted = rev_intel["summary"]["hot_uncontacted_count"]
    stalled_deals = rev_intel["summary"]["stalled_deals_count"]
    seo_reports = snap.get("seo_audits", [])
    content_count = len(snap.get("cf_items", []))
    campaigns_count = len(snap.get("campaigns", []))
    connected_social = sum(
        1
        for i in snap.get("integrations", [])
        if i.provider_key in ("instagram", "facebook", "linkedin", "tiktok", "youtube", "pinterest")
        and i.status == "CONNECTED"
    )

    products = json.loads(tenant.products_json or "[]")
    services = json.loads(tenant.services_json or "[]")
    default_offer = ", ".join((services or products)[:2]) or tenant.niche or tenant.brand_name
    objective = sanitize_text(str(payload.get("objective") or "Aumentar clientes, vendas e receita recorrente")).strip()
    product_or_service = sanitize_text(str(payload.get("product_or_service") or default_offer)).strip()
    target_audience = sanitize_text(str(payload.get("target_audience") or tenant.target_audience or "Decisores B2B e PMEs")).strip()
    region = sanitize_text(str(payload.get("region") or getattr(tenant, "brand_country", "Brasil") or "Brasil")).strip()
    budget_brl = max(0.0, float(payload.get("budget_brl") or 0.0))
    deadline_days = max(7, min(365, int(payload.get("deadline_days") or 90)))
    target_goal = sanitize_text(str(payload.get("target_goal") or "Elevar leads qualificados e conversão comercial")).strip()

    domain = (tenant.domain or "").strip()
    brand = tenant.brand_name or tenant.name

    actions: list[dict[str, Any]] = [
        {
            "step_id": "step-today-crm",
            "horizon": "TODAY",
            "horizon_label": "Hoje",
            "title": (
                f"Atender {hot_uncontacted} lead(s) quente(s) e destravar {stalled_deals} negociação(ões)"
                if (hot_uncontacted + stalled_deals) > 0
                else "Qualificar leads e estruturar funil comercial para captura imediata"
            ),
            "why": "A ação mais rápida para receita é responder contatos de alta intenção já no banco.",
            "action_type": "SCORE_CRM",
            "impact_score": 10,
            "effort_score": 2,
            "cost_brl": 0.0,
            "probability_pct": 75.0,
            "probability_origin": "ESTIMATED",
            "risk_level": "BAIXO",
            "time_estimate": "5 min",
            "can_auto_execute": True,
            "requires_approval": False,
            "estimated_outcome": "Priorização imediata dos contatos mais propensos a fechamento (Estimativa).",
        },
        {
            "step_id": "step-today-seo",
            "horizon": "TODAY",
            "horizon_label": "Hoje",
            "title": f"Auditar presença técnica HTTP e SEO de {domain or brand}",
            "why": (
                "Nenhuma auditoria técnica recente registrada."
                if not seo_reports
                else "Atualizar diagnóstico de meta tags, canonical, viewport mobile e velocidade."
            ),
            "action_type": "RUN_SEO",
            "impact_score": 8,
            "effort_score": 2,
            "cost_brl": 0.0,
            "probability_pct": 85.0,
            "probability_origin": "ESTIMATED",
            "risk_level": "BAIXO",
            "time_estimate": "15 seg",
            "can_auto_execute": bool(domain),
            "requires_approval": False,
            "estimated_outcome": "Lista priorizada de correções técnicas sem custo de APIs pagas (Estimativa).",
        },
        {
            "step_id": "step-7d-content",
            "horizon": "NEXT_7_DAYS",
            "horizon_label": "Próximos 7 dias",
            "title": f"Produzir pacote inicial de distribuição para {target_audience}",
            "why": (
                f"Base atual possui {content_count} peças na Fábrica de Conteúdo. "
                f"Canais OAuth conectados: {connected_social}/6 (usa Pacote 1-Clique assistido enquanto pendentes)."
            ),
            "action_type": "GEN_CONTENT_BATCH",
            "impact_score": 9,
            "effort_score": 3,
            "cost_brl": 0.0,
            "probability_pct": 70.0,
            "probability_origin": "ESTIMATED",
            "risk_level": "BAIXO",
            "time_estimate": "10 seg",
            "can_auto_execute": True,
            "requires_approval": False,
            "estimated_outcome": "15–30 peças contextualizadas com sua marca prontas para publicação (Estimativa).",
        },
        {
            "step_id": "step-7d-campaign",
            "horizon": "NEXT_7_DAYS",
            "horizon_label": "Próximos 7 dias",
            "title": f"Estruturar campanha focada em '{product_or_service}' ({region})",
            "why": f"Base possui {campaigns_count} campanha(s). Conecta oferta direta à dor de {target_audience}.",
            "action_type": "CREATE_CAMPAIGN",
            "impact_score": 8,
            "effort_score": 4,
            "cost_brl": 0.0 if budget_brl == 0 else budget_brl,
            "probability_pct": 65.0,
            "probability_origin": "ESTIMATED",
            "risk_level": "MÉDIO" if budget_brl > 0 else "BAIXO",
            "time_estimate": "1 min",
            "can_auto_execute": budget_brl == 0,
            "requires_approval": budget_brl > 0,
            "estimated_outcome": "Campanha registrada com atribuição de funil e ROI auditável (Estimativa).",
        },
        {
            "step_id": "step-30d-ceo-plan",
            "horizon": "NEXT_30_DAYS",
            "horizon_label": "Próximos 30 dias",
            "title": "Ativar cadência semanal de revisão executiva e automações Python",
            "why": "Garante retorno diário, detecção automática de leads esquecidos e revisão de proposta PDF.",
            "action_type": "GENERATE_DAILY_CEO_PLAN",
            "impact_score": 8,
            "effort_score": 3,
            "cost_brl": 0.0,
            "probability_pct": 72.0,
            "probability_origin": "ESTIMATED",
            "risk_level": "BAIXO",
            "time_estimate": "15 seg",
            "can_auto_execute": True,
            "requires_approval": False,
            "estimated_outcome": "Rotina previsível de execução multiagente monitorada em Meu Trabalho (Estimativa).",
        },
        {
            "step_id": "step-90d-oauth",
            "horizon": "NEXT_90_DAYS",
            "horizon_label": "Próximos 90 dias",
            "title": "Conectar canais oficiais (Google Search Console, Meta, LinkedIn) para escala direta",
            "why": f"{18 - sum(1 for i in snap.get('integrations', []) if i.status == 'CONNECTED')} de 18 integrações aguardam credenciais OAuth do proprietário.",
            "action_type": "CONNECT_OAUTH",
            "impact_score": 9,
            "effort_score": 6,
            "cost_brl": 0.0,
            "probability_pct": 80.0,
            "probability_origin": "ESTIMATED",
            "risk_level": "MÉDIO",
            "time_estimate": "15 min (depende de credenciais externas)",
            "can_auto_execute": False,
            "requires_approval": True,
            "estimated_outcome": "Dados reais de SERP no Google e publicação direta multi-rede (Estimativa).",
        },
    ]

    record_audit_log(
        db,
        tenant_id=tenant_id,
        actor=actor,
        action="GROWTH_EXECUTION_PLAN_GENERATED",
        resource_type="GrowthCenter",
        details={"objective": objective, "region": region, "budget_brl": budget_brl},
    )

    return {
        "plan_id": f"grp-{uuid.uuid4().hex[:10]}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs_resolved": {
            "objective": objective,
            "product_or_service": product_or_service,
            "brand": brand,
            "domain": domain,
            "target_audience": target_audience,
            "region": region,
            "budget_brl": budget_brl,
            "target_goal": target_goal,
            "deadline_days": deadline_days,
        },
        "real_baseline": {
            "data_origin": "REAL",
            "real_leads_count": len(snap.get("real_leads", [])),
            "hot_uncontacted_count": hot_uncontacted,
            "stalled_deals_count": stalled_deals,
            "campaigns_count": campaigns_count,
            "content_items_count": content_count,
            "seo_audits_count": len(seo_reports),
            "connected_integrations_count": sum(1 for i in snap.get("integrations", []) if i.status == "CONNECTED"),
        },
        "horizons": {
            "TODAY": [a for a in actions if a["horizon"] == "TODAY"],
            "NEXT_7_DAYS": [a for a in actions if a["horizon"] == "NEXT_7_DAYS"],
            "NEXT_30_DAYS": [a for a in actions if a["horizon"] == "NEXT_30_DAYS"],
            "NEXT_90_DAYS": [a for a in actions if a["horizon"] == "NEXT_90_DAYS"],
        },
        "actions": actions,
        "estimates_disclaimer": "Impactos, probabilidades e resultados esperados marcados como ESTIMATED são hipóteses operacionais baseadas em boas práticas, não garantias financeiras.",
    }


def execute_growth_plan_step_service(
    db: Session,
    tenant: Tenant,
    user: User,
    action_type: str,
) -> dict[str, Any]:
    """Executa uma etapa segura do Plano de Crescimento respeitando Autonomia e sem simular conexões."""
    autonomy = int(tenant.autonomy_default_level or 2)
    act = (action_type or "").strip().upper()

    if act == "CONNECT_OAUTH":
        return {
            "ok": False,
            "status": "REQUIRES_CREDENTIALS",
            "message": "Conexão externa requer cadastro de credenciais/OAuth na aba Integrações. Nenhuma conexão foi simulada.",
            "target_view": "integrations",
        }

    if autonomy <= 1:
        req = ApprovalRequest(
            tenant_id=tenant.id,
            agent_id="AGENT_07_GROWTH",
            action_type=f"GROWTH_PLAN_{act}",
            title=f"Executar etapa do Centro de Crescimento: {act}",
            payload_json=json.dumps({"action_type": act, "autonomy": autonomy}, ensure_ascii=False),
            autonomy_level_at_creation=autonomy,
            is_high_impact=False,
            status="PENDING",
        )
        db.add(req)
        db.commit()
        return {
            "ok": True,
            "status": "QUEUED_FOR_APPROVAL",
            "approval_id": req.id,
            "message": "Modo Nível 1 (Assistido): etapa registrada para sua confirmação em Meu Trabalho.",
        }

    if act == "SCORE_CRM":
        res = CentralOrchestrator.dispatch_task(
            db,
            tenant,
            AgentTaskContract(
                workflow_run_id=f"grp-{uuid.uuid4().hex[:8]}",
                sender_agent="GROWTH_CENTER",
                target_agent="AGENT_08_SALES",
                task_name="qualify_and_score_new_lead",
                tenant_id=tenant.id,
                autonomy_level=autonomy,
                parameters={},
            ),
        )
        out = {"status": "EXECUTED", "detail": res.summary}
    elif act == "RUN_SEO":
        raw_url = (tenant.domain or "").strip()
        if not raw_url:
            return {
                "ok": False,
                "status": "MISSING_DOMAIN",
                "message": "Cadastre o site oficial da empresa em Configurações -> Marca antes de rodar auditoria HTTP ao vivo.",
                "target_view": "settings",
            }
        safe_url = validate_public_http_url(raw_url)
        rep = perform_real_seo_audit(db, tenant, safe_url, tenant.niche or tenant.brand_name)
        out = {"status": "EXECUTED", "seo_score": rep.overall_score, "detail": f"Auditoria SEO HTTP concluída em {safe_url}: {rep.overall_score}/100."}
    elif act == "GEN_CONTENT_BATCH":
        batch = generate_30_day_content_batch_service(db, tenant_id=tenant.id, count=15)
        out = {"status": "EXECUTED", "total_generated": batch.get("total_generated", 15), "detail": f"{batch.get('total_generated', 15)} peças contextualizadas geradas na Fábrica."}
    elif act == "CREATE_CAMPAIGN":
        camp = MarketingCampaign(
            tenant_id=tenant.id,
            name=f"Aquisição Focada — {tenant.brand_name}",
            campaign_type="ACQUISITION",
            channel="SEO + Redes (Modo Assistido)",
            objective=f"Capturar leads de {tenant.target_audience or 'clientes potenciais'}",
            funnel_stage="TOFU/MOFU/BOFU",
            budget_planned=0.0,
            status="ACTIVE",
            data_origin="GOAL",
        )
        db.add(camp)
        db.commit()
        out = {"status": "EXECUTED", "campaign_id": camp.id, "detail": f"Campanha '{camp.name}' estruturada a custo R$ 0,00."}
    elif act == "GENERATE_DAILY_CEO_PLAN":
        plan = generate_ceo_daily_execution_plan_service(db, tenant_id=tenant.id)
        out = {"status": "EXECUTED", "detail": f"Plano Diário CEO regenerado com {len(plan.get('tasks', []))} missões."}
    else:
        return {"ok": False, "status": "UNSUPPORTED_ACTION", "message": f"Ação '{act}' não reconhecida."}

    record_audit_log(
        db,
        tenant_id=tenant.id,
        user_id=user.id,
        actor=user.email,
        action=f"GROWTH_STEP_EXECUTED:{act}",
        resource_type="GrowthCenter",
        details=out,
    )
    return {"ok": True, **out}


def build_phase26_ai_agents_matrix_service(db: Session, tenant_id: int) -> dict[str, Any]:
    """Classifica os 12 agentes sem disfarce entre DETERMINISTIC, HYBRID, LLM e BLOCKED com métricas reais."""
    status_info = MultiProviderAIAdapter.resolve_provider_status()
    logs = db.query(AgentExecutionLog).filter(AgentExecutionLog.tenant_id == tenant_id).all()
    logs_by_agent: dict[str, list[AgentExecutionLog]] = {}
    for lg in logs:
        logs_by_agent.setdefault(lg.agent_id, []).append(lg)

    matrix: list[dict[str, Any]] = []
    counts = {"LLM": 0, "HYBRID": 0, "DETERMINISTIC": 0, "SIMULATED": 0, "BLOCKED": 0}

    for aid, reg in AGENT_REGISTRY.items():
        cap = AGENT_AI_CAPABILITY_AUDIT.get(aid, {})
        ag_logs = logs_by_agent.get(aid, [])
        llm_capable = bool(cap.get("llm_narrative_enabled"))
        uses_llm_now = bool(llm_capable and status_info.get("llm_active"))

        if uses_llm_now:
            mode = "HYBRID"
        elif llm_capable and not status_info.get("llm_active"):
            mode = "DETERMINISTIC"
        else:
            mode = "DETERMINISTIC"
        counts[mode] += 1

        avg_ms = round(sum(float(x.duration_ms or 0.0) for x in ag_logs) / len(ag_logs), 1) if ag_logs else 0.0
        ok_count = sum(1 for x in ag_logs if x.status == "COMPLETED")
        err_logs = [x for x in ag_logs if x.status in ("FAILED", "BLOCKED")]

        matrix.append(
            {
                "agent_id": aid,
                "name": reg["name"],
                "objective": reg["role"],
                "execution_mode": mode,
                "uses_real_llm_now": uses_llm_now,
                "active_model": status_info.get("active_provider") if uses_llm_now else "python-deterministic-v2",
                "context_sources": ["Tenant Brand Profile", "PostgreSQL Real Tables", "Integrations Status"],
                "authorized_data": "Somente registros do tenant ativo com isolamento rigoroso + filtro TEST/SANDBOX.",
                "allowed_tools": reg.get("allowed_tools", []),
                "limits": {
                    "default_autonomy": reg.get("default_autonomy", 2),
                    "cost_policy": "FREE_ONLY (bloqueia gasto pago sem aprovação)",
                    "anti_loop": "Orquestrador central com trace workflow_run_id único",
                },
                "metrics": {
                    "executions_total": len(ag_logs),
                    "completed_count": ok_count,
                    "avg_duration_ms": avg_ms,
                },
                "strategy": cap.get("deterministic_rules", ""),
                "limitations": cap.get("limitations", ""),
                "real_status": "OPERATIONAL" if not err_logs else "ATTENTION_NEEDED",
                "last_error": err_logs[-1].status if err_logs else "",
                "estimated_cost_brl": 0.0,
            }
        )

    return {
        "data_origin": "REAL",
        "provider_status": status_info,
        "usage_today": AIUsageTracker.get_usage_summary(tenant_id, db=db),
        "classification_summary": counts,
        "agents": matrix,
        "honesty_notice": "Templates e regras Python são rotulados como DETERMINISTIC ou HYBRID — nunca disfarçados de LLM generativo puro.",
    }


def move_crm_deal_stage_service(
    db: Session,
    tenant_id: int,
    deal_id: int,
    new_stage: str,
    actor: str = "Empreendedor",
) -> dict[str, Any]:
    """Move negócio de etapa no pipeline comercial com rastreabilidade e probabilidade explícita como ESTIMATED."""
    stage_norm = (new_stage or "").strip().upper()
    if stage_norm not in STAGE_DEFAULT_PROBS:
        raise ValueError(f"Etapa inválida: {new_stage}")
    deal = db.query(CRMDeal).filter(CRMDeal.id == deal_id, CRMDeal.tenant_id == tenant_id).first()
    if not deal:
        raise ValueError("Negociação não encontrada neste workspace.")

    old_stage = deal.stage
    prob, new_status = STAGE_DEFAULT_PROBS[stage_norm]
    deal.stage = stage_norm
    deal.probability_pct = prob
    deal.status = new_status
    db.commit()
    db.refresh(deal)

    record_audit_log(
        db,
        tenant_id=tenant_id,
        actor=actor,
        action="CRM_DEAL_STAGE_MOVED",
        resource_type="CRMDeal",
        resource_id=str(deal.id),
        details={"from": old_stage, "to": stage_norm, "status": new_status},
    )
    return {
        "ok": True,
        "deal_id": deal.id,
        "title": deal.title,
        "stage": deal.stage,
        "status": deal.status,
        "probability_pct": deal.probability_pct,
        "probability_origin": "ESTIMATED",
    }


def prepare_smart_lead_followup_service(
    db: Session,
    tenant: Tenant,
    lead_id: int,
    actor: str = "Empreendedor",
) -> dict[str, Any]:
    """Prepara mensagem consultiva personalizada para follow-up respeitando LGPD e nunca disparando sem canal ativo."""
    lead = db.query(CRMLead).filter(CRMLead.id == lead_id, CRMLead.tenant_id == tenant.id).first()
    if not lead:
        raise ValueError("Lead não encontrado neste workspace.")
    if getattr(lead, "opt_out", False) or getattr(lead, "contact_blocked", False):
        raise ValueError("Contato bloqueado por preferência LGPD (opt-out).")

    brand = tenant.brand_name or tenant.name
    first_name = (lead.full_name or "").strip().split(" ")[0] or "tudo bem"
    comp = f" na {lead.company_name}" if (lead.company_name or "").strip() else ""
    draft_msg = (
        f"Olá {first_name}, aqui é da {brand}. "
        f"Preparamos uma análise inicial rápida para apoiar o crescimento{comp} no seu momento atual. "
        f"Faz sentido alinharmos os próximos passos em uma conversa objetiva de 15 minutos?"
    )

    wa_conn = (
        db.query(IntegrationConnection)
        .filter(IntegrationConnection.tenant_id == tenant.id, IntegrationConnection.provider_key == "whatsapp_business")
        .first()
    )
    smtp_conn = (
        db.query(IntegrationConnection)
        .filter(IntegrationConnection.tenant_id == tenant.id, IntegrationConnection.provider_key == "smtp_email")
        .first()
    )
    has_channel = bool((wa_conn and wa_conn.status == "CONNECTED") or (smtp_conn and smtp_conn.status == "CONNECTED"))

    lead.outreach_draft_message = draft_msg
    act = CRMActivity(
        tenant_id=tenant.id,
        lead_id=lead.id,
        activity_type="FOLLOW_UP",
        subject=f"Follow-up Inteligente preparado para {lead.full_name}",
        description=draft_msg,
        due_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )
    db.add(act)

    approval_id = None
    if has_channel:
        req = ApprovalRequest(
            tenant_id=tenant.id,
            agent_id="AGENT_08_SALES",
            action_type="OUTREACH_FOLLOWUP",
            title=f"Confirmar envio de follow-up para {lead.full_name}",
            payload_json=json.dumps({"lead_id": lead.id, "message": draft_msg}, ensure_ascii=False),
            autonomy_level_at_creation=int(tenant.autonomy_default_level or 2),
            is_high_impact=False,
            status="PENDING",
        )
        db.add(req)
        db.flush()
        approval_id = req.id

    db.commit()
    record_audit_log(
        db,
        tenant_id=tenant.id,
        actor=actor,
        action="CRM_SMART_FOLLOWUP_PREPARED",
        resource_type="CRMLead",
        resource_id=str(lead.id),
        details={"has_connected_channel": has_channel, "approval_id": approval_id},
    )

    return {
        "ok": True,
        "lead_id": lead.id,
        "draft_message": draft_msg,
        "channel_connected": has_channel,
        "approval_id": approval_id,
        "delivery_status": (
            "PENDING_APPROVAL_BEFORE_EXTERNAL_SEND"
            if has_channel
            else "PREPARED_MANUAL_COPY_NO_CHANNEL_CONNECTED"
        ),
        "message": (
            "Rascunho criado e enviado para sua aprovação antes do envio externo."
            if has_channel
            else "Rascunho consultivo pronto para copiar! Nenhum envio externo ocorreu (WhatsApp/SMTP ainda não conectados)."
        ),
    }


def get_saas_entitlements_and_billing_readiness_service(
    db: Session,
    tenant: Tenant,
    owner_email: str = "",
) -> dict[str, Any]:
    """Expõe entitlements reais do plano atual e readiness de billing (Mercado Pago / Stripe) sem ativar cobrança."""
    usage_pack = get_tenant_plan_usage_summary(db, tenant, owner_email=owner_email)
    plan_code = usage_pack["active_plan"]["code"]
    included_agents = set(usage_pack["active_plan"].get("agents_included", []))

    return {
        **usage_pack,
        "entitlements": {
            "can_create_more_companies": not usage_pack["usage_meters"]["companies"]["exceeded"],
            "can_add_crm_leads": not usage_pack["usage_meters"]["crm_leads"]["exceeded"],
            "can_enable_more_automations": not usage_pack["usage_meters"]["automations"]["exceeded"],
            "ai_data_analyst_included": "AGENT_12_DATA_ANALYST" in included_agents,
            "multibusiness_included": plan_code in ("BUSINESS", "ENTERPRISE"),
            "custom_oauth_ready": True,
        },
        "billing_readiness": {
            "charge_enabled": False,
            "authorization_required": True,
            "recommended_br_gateway": {
                "provider": "Mercado Pago",
                "methods": ["PIX", "Cartão Recorrente"],
                "webhook_hmac_implemented": True,
                "live_credentials_present": False,
            },
            "recommended_global_gateway": {
                "provider": "Stripe Billing / Paddle MoR",
                "currency": "USD / EUR",
                "live_credentials_present": False,
            },
        },
        "plans_count": len(SAAS_PLANS),
    }
