"""UNION GROWTH OS — FASE 25: REVENUE INTELLIGENCE, RETENTION & PLG ACTIVATION ENGINE

Consolida inteligência executável em dados reais do PostgreSQL (custo R$ 0,00 adicional):
1. CRM Revenue Intelligence: detecta negociações estagnadas no funil e leads quentes sem retorno.
2. Follow-up rápido isolado por tenant (sem disparos externos automáticos não autorizados).
3. Activation & Retention Habit Loop: mede 6 marcos reais de ativação (Time-to-First-Value) e
   motivos diários de retorno com origem estritamente auditada (REAL / NAO_DISPONIVEL).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.agents.orchestrator import compute_lead_score
from app.models.entities import (
    ApprovalRequest,
    AutomationRule,
    ContentFactoryItem,
    CRMActivity,
    CRMDeal,
    CRMLead,
    SEOAuditReport,
    Tenant,
)
from app.services.plans_and_audit import record_audit_log


def get_crm_revenue_intelligence_service(db: Session, tenant_id: int) -> dict[str, Any]:
    """Identifica gargalos reais de receita no CRM/Pipeline e sugere próximas ações em 1 clique."""
    leads = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id).all()
    real_leads = [l for l in leads if (l.data_origin or "REAL").upper() not in ("TEST", "SIMULATION", "DEMO")]
    deals = db.query(CRMDeal).filter(CRMDeal.tenant_id == tenant_id).all()
    real_deals = [d for d in deals if (d.data_origin or "REAL").upper() not in ("TEST", "SIMULATION", "DEMO")]
    activities = db.query(CRMActivity).filter(CRMActivity.tenant_id == tenant_id).all()

    activity_lead_ids = {a.lead_id for a in activities if a.lead_id is not None}
    hot_uncontacted_leads = []
    for ld in real_leads:
        if getattr(ld, "opt_out", False):
            continue
        is_hot = (ld.lead_score or 0) >= 65
        if is_hot and (ld.pipeline_stage == "NEW_LEAD" or ld.id not in activity_lead_ids):
            hot_uncontacted_leads.append(
                {
                    "lead_id": ld.id,
                    "full_name": ld.full_name,
                    "company_name": ld.company_name or "Direto",
                    "lead_score": ld.lead_score or 0,
                    "estimated_value_brl": float(ld.estimated_value or 0.0),
                    "pipeline_stage": ld.pipeline_stage,
                    "reason": "Score >= 65 aguardando primeiro avanço ou follow-up registrado.",
                }
            )

    now = datetime.now(timezone.utc)
    stalled_deals = []
    stage_breakdown: dict[str, dict[str, Any]] = {}
    for d in real_deals:
        st = (d.stage or "NEW_LEAD").upper()
        bucket = stage_breakdown.setdefault(st, {"stage": st, "count": 0, "total_brl": 0.0, "weighted_brl": 0.0})
        bucket["count"] += 1
        val = float(d.value or 0.0)
        bucket["total_brl"] = round(bucket["total_brl"] + val, 2)
        bucket["weighted_brl"] = round(bucket["weighted_brl"] + val * ((d.probability_pct or 50.0) / 100.0), 2)

        if st not in ("CLOSED_WON", "CLOSED_LOST"):
            created = d.created_at.replace(tzinfo=timezone.utc) if d.created_at and d.created_at.tzinfo is None else (d.created_at or now)
            age_days = max(0, (now - created).days)
            has_lead_act = d.lead_id in activity_lead_ids if d.lead_id else False
            if age_days >= 5 or not has_lead_act:
                stalled_deals.append(
                    {
                        "deal_id": d.id,
                        "title": d.title,
                        "stage": st,
                        "value_brl": val,
                        "age_days": age_days,
                        "reason": f"Sem avanço há {age_days} dia(s)" if age_days >= 5 else "Sem tarefa vinculada no CRM",
                    }
                )

    open_deals = [d for d in real_deals if (d.stage or "").upper() not in ("CLOSED_WON", "CLOSED_LOST")]
    won_deals = [d for d in real_deals if (d.stage or "").upper() == "CLOSED_WON"]
    avg_ticket = round(sum(float(d.value or 0.0) for d in won_deals) / len(won_deals), 2) if won_deals else 0.0
    win_rate_pct = round((len(won_deals) / len(real_deals)) * 100.0, 1) if real_deals else 0.0

    next_best_actions: list[dict[str, Any]] = []
    if hot_uncontacted_leads:
        top_lead = sorted(hot_uncontacted_leads, key=lambda x: x["lead_score"], reverse=True)[0]
        next_best_actions.append(
            {
                "id": f"followup-lead-{top_lead['lead_id']}",
                "type": "QUICK_FOLLOWUP",
                "lead_id": top_lead["lead_id"],
                "title": f"Avançar lead quente: {top_lead['full_name']} (Score {top_lead['lead_score']})",
                "impact": f"R$ {top_lead['estimated_value_brl']:,.2f} potenciais sem retorno registrado",
            }
        )
    if stalled_deals:
        top_deal = sorted(stalled_deals, key=lambda x: x["value_brl"], reverse=True)[0]
        next_best_actions.append(
            {
                "id": f"stalled-deal-{top_deal['deal_id']}",
                "type": "UNBLOCK_DEAL",
                "deal_id": top_deal["deal_id"],
                "title": f"Destravar negociação parada: {top_deal['title']}",
                "impact": f"R$ {top_deal['value_brl']:,.2f} em {top_deal['stage']}",
            }
        )

    return {
        "data_origin": "REAL",
        "summary": {
            "real_leads_count": len(real_leads),
            "hot_uncontacted_count": len(hot_uncontacted_leads),
            "open_deals_count": len(open_deals),
            "stalled_deals_count": len(stalled_deals),
            "won_deals_count": len(won_deals),
            "avg_ticket_brl": avg_ticket,
            "win_rate_pct": win_rate_pct,
        },
        "hot_uncontacted_leads": hot_uncontacted_leads[:10],
        "stalled_deals": stalled_deals[:10],
        "stage_breakdown": list(stage_breakdown.values()),
        "next_best_actions": next_best_actions,
    }


def quick_create_lead_followup_service(
    db: Session,
    tenant_id: int,
    lead_id: int,
    actor: str,
) -> dict[str, Any]:
    """Cria tarefa interna de follow-up e qualifica lead quente sem envio externo automático."""
    lead = db.query(CRMLead).filter(CRMLead.id == lead_id, CRMLead.tenant_id == tenant_id).first()
    if not lead:
        raise ValueError("Lead não encontrado neste workspace.")
    if getattr(lead, "opt_out", False):
        raise ValueError("Lead em opt-out LGPD: contato bloqueado.")

    score, qual = compute_lead_score(lead)
    lead.lead_score = score
    if lead.qualification_status == "NEW":
        lead.qualification_status = qual
    if lead.pipeline_stage == "NEW_LEAD":
        lead.pipeline_stage = "QUALIFICATION"

    act = CRMActivity(
        tenant_id=tenant_id,
        lead_id=lead.id,
        activity_type="FOLLOW_UP",
        subject=f"Follow-up Prioritário: {lead.full_name} (Score {score})",
        description=f"Retorno consultivo agendado internamente para {lead.company_name or lead.full_name}.",
        due_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )
    db.add(act)
    db.commit()
    db.refresh(act)
    record_audit_log(
        db,
        tenant_id=tenant_id,
        actor=actor,
        action="CRM_QUICK_FOLLOWUP_CREATED",
        resource_type="CRMLead",
        resource_id=str(lead.id),
        details={"lead_score": score, "pipeline_stage": lead.pipeline_stage},
    )
    return {
        "ok": True,
        "lead_id": lead.id,
        "pipeline_stage": lead.pipeline_stage,
        "lead_score": score,
        "activity_id": act.id,
        "message": f"Follow-up registrado e lead {lead.full_name} avançado para {lead.pipeline_stage}.",
    }


def get_activation_and_retention_service(db: Session, tenant_id: int) -> dict[str, Any]:
    """Mede marcos reais de ativação (TTFV) e razões concretas de retorno diário sem inventar métricas."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant não encontrado.")

    has_company_profile = bool((tenant.name or "").strip() and (tenant.niche or "").strip() and (tenant.target_audience or "").strip())
    has_brand_ready = bool((tenant.domain or "").strip() and (getattr(tenant, "brand_voice", "") or "").strip())
    seo_count = db.query(SEOAuditReport).filter(SEOAuditReport.tenant_id == tenant_id).count()
    content_count = db.query(ContentFactoryItem).filter(ContentFactoryItem.tenant_id == tenant_id).count()
    real_leads_count = sum(
        1
        for l in db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id).all()
        if (l.data_origin or "REAL").upper() not in ("TEST", "SIMULATION", "DEMO")
    )
    active_rules_count = db.query(AutomationRule).filter(AutomationRule.tenant_id == tenant_id, AutomationRule.is_active == True).count()
    pending_approvals = db.query(ApprovalRequest).filter(ApprovalRequest.tenant_id == tenant_id, ApprovalRequest.status == "PENDING").count()
    ready_content = db.query(ContentFactoryItem).filter(ContentFactoryItem.tenant_id == tenant_id, ContentFactoryItem.status != "PUBLISHED").count()

    milestones = [
        {"key": "empresa_configurada", "label": "Empresa, nicho e público definidos", "done": has_company_profile, "target_view": "settings"},
        {"key": "marca_definida", "label": "Site oficial e tom de voz configurados", "done": has_brand_ready, "target_view": "settings"},
        {"key": "seo_auditado", "label": "1ª Auditoria SEO técnica executada", "done": seo_count > 0, "target_view": "seo"},
        {"key": "conteudo_criado", "label": "Conteúdos gerados para sua marca", "done": content_count > 0, "target_view": "content_factory"},
        {"key": "primeiro_lead", "label": "1º Lead real registrado com LGPD", "done": real_leads_count > 0, "target_view": "crm"},
        {"key": "primeira_automacao", "label": "Rotina automática Python ativa", "done": active_rules_count > 0, "target_view": "automations"},
    ]
    done_count = sum(1 for m in milestones if m["done"])
    activation_pct = round((done_count / len(milestones)) * 100)

    rev_intel = get_crm_revenue_intelligence_service(db, tenant_id)
    daily_triggers = []
    if pending_approvals > 0:
        daily_triggers.append({"title": f"{pending_approvals} aprovação(ões) aguardando decisão", "target_view": "approvals"})
    if rev_intel["summary"]["hot_uncontacted_count"] > 0:
        daily_triggers.append({"title": f"{rev_intel['summary']['hot_uncontacted_count']} lead(s) quente(s) sem retorno no CRM", "target_view": "crm"})
    if rev_intel["summary"]["stalled_deals_count"] > 0:
        daily_triggers.append({"title": f"{rev_intel['summary']['stalled_deals_count']} negociação(ões) parada(s) no pipeline", "target_view": "commercial"})
    if ready_content > 0:
        daily_triggers.append({"title": f"{ready_content} conteúdo(s) pronto(s) para Pacote 1-Clique", "target_view": "content_factory"})

    return {
        "data_origin": "REAL",
        "activation_pct": activation_pct,
        "completed_milestones": done_count,
        "total_milestones": len(milestones),
        "first_value_achieved": done_count >= 3,
        "milestones": milestones,
        "daily_return_triggers": daily_triggers,
    }
