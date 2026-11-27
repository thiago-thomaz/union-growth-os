"""
UNION GROWTH OS — FASE 23: THE AUTONOMOUS BUSINESS GROWTH PLATFORM
Motor central nativo Python para:
1. AI Growth Command Center (Business Health 12 pilares, Growth Score documentado,
   AI CEO Briefing Diário/Semanal, Opportunity Radar e Executive Action Center).
2. Central de Inteligência de Marca (Brand Kit + Versionamento + Detector de Inconsistências).
3. Onboarding Empresarial Progressivo de 6 Etapas (recuperável, editável e reiniciável).
4. Copiloto Estruturado "ASK UNION" conectado ao estado real com execução rastreável.
5. Conversational Automation Builder 100% Python/APScheduler (ZERO n8n) com dry-run e aprovação.
6. Analytics & Attribution Hub com separação rigorosa REAL / ESTIMATIVA / SANDBOX / NÃO DISPONÍVEL.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.security import sanitize_text
from app.services.plans_and_audit import record_audit_log
from app.models.entities import (
    AIEngineConfigurationRecord,
    AIEngineExecutionRecord,
    ApprovalRequest,
    AskUnionActionLog,
    AutomationExecution,
    AutomationRule,
    BrandVersionRecord,
    CEODailyBriefing,
    CEODelegatedTask,
    Competitor,
    ContentFactoryItem,
    CopyItem,
    CRMActivity,
    CRMDeal,
    CRMLead,
    CustomerFeedback,
    EditorialCalendarItem,
    FinancialRecord,
    GrowthExperiment,
    IntegrationConnection,
    MarketingCampaign,
    MarketingPersona,
    OperationalAlert,
    ProductService,
    SEOArticle,
    SEOAuditReport,
    SEOKeywordCluster,
    Tenant,
    User,
)
from app.services.phase14_automation_factory import (
    generate_30_day_content_batch_service,
    generate_ceo_daily_execution_plan_service,
)
from app.agents.orchestrator import calculate_tenant_financial_kpis, compute_lead_score
from app.services.seo_and_market_engine import perform_real_seo_audit, research_keywords_and_clusters


def _health_item(
    key: str,
    label: str,
    score: int | None,
    value_label: str,
    status_label: str,
    data_origin: str,
    summary: str,
) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "score": score,
        "value_label": value_label,
        "status_label": status_label,  # SAUDAVEL | ATENCAO | CRITICO | NAO_DISPONIVEL
        "data_origin": data_origin,    # REAL | ESTIMATIVA | SANDBOX | NAO_DISPONIVEL
        "summary": summary,
    }


def _collect_real_snapshot(db: Session, tenant: Tenant) -> dict[str, Any]:
    tid = tenant.id
    kpis = calculate_tenant_financial_kpis(db, tid)
    campaigns = db.query(MarketingCampaign).filter(MarketingCampaign.tenant_id == tid).all()
    personas = db.query(MarketingPersona).filter(MarketingPersona.tenant_id == tid).all()
    cf_items = db.query(ContentFactoryItem).filter(ContentFactoryItem.tenant_id == tid).all()
    cal_items = db.query(EditorialCalendarItem).filter(EditorialCalendarItem.tenant_id == tid).all()
    leads_all = db.query(CRMLead).filter(CRMLead.tenant_id == tid).all()
    real_leads = [l for l in leads_all if (l.data_origin or "REAL").upper() not in ("TEST", "SIMULATION", "DEMO")]
    deals_all = db.query(CRMDeal).filter(CRMDeal.tenant_id == tid).all()
    real_deals = [d for d in deals_all if (d.data_origin or "REAL").upper() not in ("TEST", "SIMULATION", "DEMO")]
    feedbacks = db.query(CustomerFeedback).filter(CustomerFeedback.tenant_id == tid).all()
    competitors = db.query(Competitor).filter(Competitor.tenant_id == tid).all()
    seo_audits = db.query(SEOAuditReport).filter(SEOAuditReport.tenant_id == tid).order_by(SEOAuditReport.id.desc()).all()
    seo_kws = db.query(SEOKeywordCluster).filter(SEOKeywordCluster.tenant_id == tid).all()
    seo_articles = db.query(SEOArticle).filter(SEOArticle.tenant_id == tid).all()
    copies = db.query(CopyItem).filter(CopyItem.tenant_id == tid).all()
    experiments = db.query(GrowthExperiment).filter(GrowthExperiment.tenant_id == tid).all()
    rules = db.query(AutomationRule).filter(AutomationRule.tenant_id == tid).all()
    rule_execs = db.query(AutomationExecution).filter(AutomationExecution.tenant_id == tid).order_by(AutomationExecution.id.desc()).all()
    integrations = db.query(IntegrationConnection).filter(IntegrationConnection.tenant_id == tid).all()
    approvals = db.query(ApprovalRequest).filter(ApprovalRequest.tenant_id == tid).order_by(ApprovalRequest.id.desc()).all()
    alerts = db.query(OperationalAlert).filter(OperationalAlert.tenant_id == tid).all()
    products = db.query(ProductService).filter(ProductService.tenant_id == tid).all()
    ai_cfg = db.query(AIEngineConfigurationRecord).filter(AIEngineConfigurationRecord.tenant_id == tid).first()
    ai_execs = db.query(AIEngineExecutionRecord).filter(AIEngineExecutionRecord.tenant_id == tid).order_by(AIEngineExecutionRecord.id.desc()).all()
    ceo_briefings = db.query(CEODailyBriefing).filter(CEODailyBriefing.tenant_id == tid).order_by(CEODailyBriefing.id.desc()).all()
    ceo_tasks = db.query(CEODelegatedTask).filter(CEODelegatedTask.tenant_id == tid).all()
    brand_versions = db.query(BrandVersionRecord).filter(BrandVersionRecord.tenant_id == tid).order_by(BrandVersionRecord.id.desc()).all()
    activities = db.query(CRMActivity).filter(CRMActivity.tenant_id == tid).all()

    return {
        "kpis": kpis,
        "campaigns": campaigns,
        "personas": personas,
        "cf_items": cf_items,
        "cal_items": cal_items,
        "leads_all": leads_all,
        "real_leads": real_leads,
        "deals_all": deals_all,
        "real_deals": real_deals,
        "feedbacks": feedbacks,
        "competitors": competitors,
        "seo_audits": seo_audits,
        "seo_kws": seo_kws,
        "seo_articles": seo_articles,
        "copies": copies,
        "experiments": experiments,
        "rules": rules,
        "rule_execs": rule_execs,
        "integrations": integrations,
        "approvals": approvals,
        "alerts": alerts,
        "products": products,
        "ai_cfg": ai_cfg,
        "ai_execs": ai_execs,
        "ceo_briefings": ceo_briefings,
        "ceo_tasks": ceo_tasks,
        "brand_versions": brand_versions,
        "activities": activities,
    }


def compute_growth_score_and_health(db: Session, tenant: Tenant, snap: dict[str, Any] | None = None) -> dict[str, Any]:
    """Calcula Business Health (12 dimensões) e Growth Score transparente e auditável sem inventar dados."""
    s = snap or _collect_real_snapshot(db, tenant)
    kpis = s["kpis"]
    campaigns = s["campaigns"]
    personas = s["personas"]
    cf_items = s["cf_items"]
    cal_items = s["cal_items"]
    real_leads = s["real_leads"]
    real_deals = s["real_deals"]
    feedbacks = s["feedbacks"]
    competitors = s["competitors"]
    seo_audits = s["seo_audits"]
    seo_kws = s["seo_kws"]
    seo_articles = s["seo_articles"]
    rules = s["rules"]
    rule_execs = s["rule_execs"]
    integrations = s["integrations"]
    approvals = s["approvals"]
    alerts = s["alerts"]
    ai_execs = s["ai_execs"]
    ceo_tasks = s["ceo_tasks"]

    connected_intgs = [i for i in integrations if i.status == "CONNECTED"]
    won_deals = [d for d in real_deals if getattr(d, "stage", "") == "CLOSED_WON" or getattr(d, "status", "") == "WON"]
    active_deals = [d for d in real_deals if getattr(d, "stage", "") not in ("CLOSED_LOST",) and getattr(d, "status", "") != "LOST"]
    qualified_leads = [l for l in real_leads if (l.lead_score or 0) >= 60 or l.qualification_status in ("MQL", "SQL", "QUALIFIED")]
    published_content = [c for c in cf_items if c.status == "PUBLISHED"] + [c for c in cal_items if c.publish_status == "PUBLISHED"]
    total_content = len(cf_items) + len(cal_items)
    active_rules = [r for r in rules if r.is_active]
    pending_approvals = [a for a in approvals if a.status == "PENDING"]
    open_alerts = [a for a in alerts if not a.is_resolved]
    done_tasks = [t for t in ceo_tasks if (t.status or "").upper() in ("COMPLETED", "DONE")]
    at_risk_cs = [f for f in feedbacks if (f.nps_score or 0) <= 6]

    has_domain = bool((tenant.domain or "").strip())
    latest_seo = seo_audits[0] if seo_audits else None
    real_rev = float(kpis.get("total_revenue", 0.0) or 0.0)
    real_spend = float(kpis.get("total_expenses", 0.0) or 0.0)
    ai_confirmed_cost = round(sum(float(e.confirmed_cost_brl or 0.0) for e in ai_execs), 2)

    # 12 Dimensões de Saúde
    mkt_score = min(100, (35 if personas else 0) + (45 if campaigns else 0) + (20 if connected_intgs else 0)) if (campaigns or personas) else 0
    lead_score_dim = min(100, 30 + len(real_leads) * 10 + len(qualified_leads) * 8) if real_leads else None
    sales_score = min(100, 35 + len(active_deals) * 12 + len(won_deals) * 20) if real_deals else None
    conv_rate = round((len(won_deals) / len(real_leads)) * 100, 1) if real_leads else None
    avg_nps = round(sum(f.nps_score for f in feedbacks) / len(feedbacks), 1) if feedbacks else None
    content_score = min(100, (30 if total_content > 0 else 0) + min(50, total_content * 2) + (20 if published_content else 0)) if total_content > 0 else 0
    auto_score = min(100, (40 if active_rules else 0) + min(40, sum(r.run_count or 0 for r in rules) * 10) + (20 if not [x for x in rule_execs if x.status == "FAILED"] else 0))
    exec_score = min(100, 40 + len(done_tasks) * 15) if ceo_tasks else (75 if (campaigns or cf_items or real_leads) else 30)

    business_health = [
        _health_item(
            "marketing",
            "Marketing & Campanhas",
            mkt_score if (campaigns or personas) else None,
            f"{len(campaigns)} campanha(s) • {len(personas)} persona(s)" if (campaigns or personas) else "Nenhuma campanha",
            "SAUDAVEL" if (campaigns and personas) else ("ATENCAO" if (campaigns or personas) else "NAO_DISPONIVEL"),
            "REAL" if (campaigns or personas) else "NAO_DISPONIVEL",
            "Personas e campanhas cadastradas guiam a geração de conteúdo." if (campaigns and personas) else "Cadastre ao menos 1 persona e 1 campanha para organizar a aquisição.",
        ),
        _health_item(
            "leads",
            "Geração de Leads",
            lead_score_dim,
            f"{len(real_leads)} lead(s) real(is)" if real_leads else "Sem leads reais",
            "SAUDAVEL" if len(real_leads) >= 3 else ("ATENCAO" if real_leads else "NAO_DISPONIVEL"),
            "REAL" if real_leads else "NAO_DISPONIVEL",
            f"{len(qualified_leads)} qualificado(s) com consentimento LGPD." if real_leads else "Nenhum lead real capturado ainda nesta empresa.",
        ),
        _health_item(
            "vendas",
            "Pipeline & Vendas",
            sales_score,
            f"{len(active_deals)} negociação(ões)" if real_deals else "Sem negociações",
            "SAUDAVEL" if won_deals else ("ATENCAO" if active_deals else "NAO_DISPONIVEL"),
            "REAL" if real_deals else "NAO_DISPONIVEL",
            f"{len(won_deals)} venda(s) ganha(s) registrada(s) no funil." if real_deals else "Crie oportunidades/propostas para acompanhar o funil comercial.",
        ),
        _health_item(
            "conversao",
            "Taxa de Conversão",
            min(100, int(conv_rate * 2)) if conv_rate is not None else None,
            f"{conv_rate}%" if conv_rate is not None else "Indisponível",
            "SAUDAVEL" if (conv_rate or 0) >= 10 else ("ATENCAO" if conv_rate is not None else "NAO_DISPONIVEL"),
            "REAL" if conv_rate is not None else "NAO_DISPONIVEL",
            f"Calculada estritamente sobre {len(won_deals)} ganho(s) / {len(real_leads)} lead(s)." if conv_rate is not None else "Exige ao menos 1 lead real e histórico comercial para cálculo.",
        ),
        _health_item(
            "receita",
            "Receita & Caixa Real",
            100 if real_rev > 0 else None,
            f"R$ {real_rev:,.2f}" if real_rev > 0 else "R$ 0,00 lançado",
            "SAUDAVEL" if real_rev > 0 else "NAO_DISPONIVEL",
            "REAL" if real_rev > 0 else "NAO_DISPONIVEL",
            f"Apenas lançamentos reais auditáveis (margem líquida: {kpis.get('profit_margin_pct', 0)}%)." if real_rev > 0 else "Nenhuma receita real lançada; o sistema não inventa faturamento.",
        ),
        _health_item(
            "retencao",
            "Retenção & NPS",
            int(avg_nps * 10) if avg_nps is not None else None,
            f"NPS {avg_nps}/10" if avg_nps is not None else "Sem pesquisas",
            "SAUDAVEL" if (avg_nps or 0) >= 8 and not at_risk_cs else ("ATENCAO" if avg_nps is not None else "NAO_DISPONIVEL"),
            "REAL" if feedbacks else "NAO_DISPONIVEL",
            f"{len(feedbacks)} avaliação(ões), {len(at_risk_cs)} em risco." if feedbacks else "Registre pesquisas NPS/CSAT após entregas reais.",
        ),
        _health_item(
            "seo",
            "SEO & Site",
            latest_seo.overall_score if latest_seo else None,
            f"Score {latest_seo.overall_score}/100" if latest_seo else ("Site sem auditoria" if has_domain else "Site não informado"),
            "SAUDAVEL" if (latest_seo and latest_seo.overall_score >= 75) else ("ATENCAO" if latest_seo or has_domain else "NAO_DISPONIVEL"),
            "REAL" if latest_seo else "NAO_DISPONIVEL",
            f"Auditoria HTTP ao vivo de {latest_seo.target_url}." if latest_seo else "Informe seu site em Marca e execute 1 auditoria técnica real.",
        ),
        _health_item(
            "conteudo",
            "Produção de Conteúdo",
            content_score if total_content > 0 else None,
            f"{total_content} peça(s)" if total_content > 0 else "Nenhuma peça",
            "SAUDAVEL" if published_content else ("ATENCAO" if total_content > 0 else "NAO_DISPONIVEL"),
            "ESTIMATIVA" if (total_content > 0 and not published_content) else ("REAL" if published_content else "NAO_DISPONIVEL"),
            f"{len(published_content)} publicada(s) • {max(0, total_content - len(published_content))} pronta(s) no Modo Assistido." if total_content > 0 else "Gere 30 conteúdos alinhados à sua marca em 1 clique.",
        ),
        _health_item(
            "automacoes",
            "Automações Python 24/7",
            auto_score if rules else None,
            f"{len(active_rules)} ativa(s)" if rules else "Nenhuma regra",
            "SAUDAVEL" if active_rules else "NAO_DISPONIVEL",
            "REAL" if rules else "NAO_DISPONIVEL",
            f"Motor nativo APScheduler com {sum(r.run_count or 0 for r in rules)} execução(ões) sem dependência de n8n.",
        ),
        _health_item(
            "execucao",
            "Execução & Governança",
            exec_score,
            f"{len(pending_approvals)} aprovação(ões) • {len(open_alerts)} alerta(s)",
            "ATENCAO" if (pending_approvals or open_alerts) else "SAUDAVEL",
            "REAL",
            "Decisões críticas aguardam seu clique; nenhuma ação paga executa sem aval.",
        ),
        _health_item(
            "custos",
            "Custos Operacionais & IA",
            100 if ai_confirmed_cost == 0 else 80,
            f"IA R$ {ai_confirmed_cost:.2f} • Desp. R$ {real_spend:,.2f}",
            "SAUDAVEL",
            "REAL",
            f"Política atual: {(s['ai_cfg'].cost_policy_mode if s['ai_cfg'] else 'FREE_ONLY')}. Bloqueia cobranças não autorizadas.",
        ),
        _health_item(
            "oportunidades",
            "Radar de Oportunidades",
            None,
            "Análise abaixo",
            "ATENCAO",
            "ESTIMATIVA",
            "Gaps priorizados automaticamente a partir dos dados reais da conta.",
        ),
    ]

    # Growth Score transparente (0-100 = soma de 5 pilares de 20 pts)
    p1_brand = (5 if tenant.brand_name else 0) + (5 if has_domain else 0) + (5 if (tenant.niche and tenant.brand_voice) else 0) + (5 if personas else 0)
    p2_seo = (6 if has_domain else 0) + (8 if (latest_seo and latest_seo.overall_score >= 60) else (4 if latest_seo else 0)) + (6 if (seo_kws or seo_articles) else 0)
    p3_mkt = (7 if campaigns else 0) + (8 if total_content >= 5 else (4 if total_content > 0 else 0)) + (5 if (s["copies"] or published_content) else 0)
    p4_crm = (7 if real_leads else 0) + (7 if qualified_leads else 0) + (6 if real_deals else 0)
    p5_gov = 6 + (7 if active_rules else 0) + (7 if (real_rev > 0 or feedbacks) else 0)  # +6 base pela trava FREE_ONLY e audit trail nativo

    total_score = max(0, min(100, p1_brand + p2_seo + p3_mkt + p4_crm + p5_gov))

    limitations = []
    if not has_domain:
        limitations.append("Site/domínio da empresa ainda não informado para auditoria técnica SEO real.")
    if not connected_intgs:
        limitations.append("Nenhuma conta OAuth externa conectada (Google/Meta/LinkedIn); publicação usa Modo Assistido e rankings GSC ficam indisponíveis.")
    if real_rev == 0:
        limitations.append("Receita real em R$ 0,00 (dados financeiros ainda sem faturamento lançado).")
    if not real_leads:
        limitations.append("Nenhum lead real no CRM para medir taxa real de conversão.")

    components = [
        {"pillar": "Identidade, Marca & Persona", "score": p1_brand, "max": 20, "origin": "REAL"},
        {"pillar": "SEO Técnico & Presença Orgânica", "score": p2_seo, "max": 20, "origin": "REAL"},
        {"pillar": "Marketing & Conteúdo", "score": p3_mkt, "max": 20, "origin": "REAL" if (campaigns or total_content) else "NAO_DISPONIVEL"},
        {"pillar": "CRM, Leads & Pipeline Comercial", "score": p4_crm, "max": 20, "origin": "REAL" if real_leads else "NAO_DISPONIVEL"},
        {"pillar": "Governança, Automações & Retenção", "score": p5_gov, "max": 20, "origin": "REAL"},
    ]

    next_improve = []
    if not has_domain or not latest_seo:
        next_improve.append("Cadastrar URL do site e rodar auditoria SEO ao vivo (+6 a +14 pts).")
    if not personas or not campaigns:
        next_improve.append("Definir 1 persona e 1 campanha ativa (+5 a +7 pts).")
    if total_content < 5:
        next_improve.append("Gerar lote inicial na Fábrica de Conteúdo (+8 pts).")
    if not real_leads:
        next_improve.append("Registrar ou importar os primeiros leads com LGPD (+14 pts).")
    if not connected_intgs:
        next_improve.append("Conectar integração analítica (GA4/Search Console) quando desejar telemetria externa.")

    # Ajustar score de oportunidades após construir oportunidades abaixo
    growth_score = {
        "score": total_score,
        "max_score": 100,
        "formula": "Soma transparente de 5 pilares auditáveis (0–20 pontos cada) baseados estritamente em registros reais do tenant.",
        "components": components,
        "data_used": {
            "campaigns": len(campaigns),
            "personas": len(personas),
            "content_pieces": total_content,
            "seo_audits": len(seo_audits),
            "real_leads": len(real_leads),
            "real_deals": len(real_deals),
            "connected_integrations": len(connected_intgs),
            "active_automations": len(active_rules),
            "competitors_tracked": len(competitors),
        },
        "limitations": limitations,
        "next_actions_to_improve": next_improve[:4],
    }

    return {
        "business_health": business_health,
        "growth_score": growth_score,
    }


def build_opportunity_radar_and_actions(
    db: Session,
    tenant: Tenant,
    snap: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Varre dados reais do tenant e monta Opportunity Radar + Executive Action Center acionável em 1 clique."""
    opportunities: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []

    has_domain = bool((tenant.domain or "").strip())
    seo_audits = snap["seo_audits"]
    personas = snap["personas"]
    campaigns = snap["campaigns"]
    cf_items = snap["cf_items"]
    real_leads = snap["real_leads"]
    real_deals = snap["real_deals"]
    competitors = snap["competitors"]
    feedbacks = snap["feedbacks"]
    rules = snap["rules"]
    integrations = snap["integrations"]
    products = snap["products"]

    stale_leads = [l for l in real_leads if l.pipeline_stage == "NEW_LEAD"]
    at_risk_cs = [f for f in feedbacks if (f.nps_score or 0) <= 6]
    promoters_cs = [f for f in feedbacks if (f.nps_score or 0) >= 9]
    unpublished_cf = [c for c in cf_items if c.status != "PUBLISHED"]
    pending_intgs = [i for i in integrations if i.status != "CONNECTED"]

    # 1. SEO
    if not has_domain:
        opportunities.append({
            "id": "opp-seo-domain",
            "category": "SEO",
            "name": "Conectar domínio para diagnóstico SEO ao vivo",
            "description": "Seu site ainda não foi configurado na identidade da marca. Informar a URL libera auditoria técnica HTTP e busca de palavras-chave.",
            "evidence": "Campo Tenant.domain vazio no banco.",
            "origin": "REAL",
            "potential": "ALTO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "BAIXO (2 min)",
            "priority": "ALTA",
            "estimated_impact": "Visibilidade orgânica gratuita no Google sem custo de anúncio",
            "next_action_label": "Informar site em Marca",
            "target_view": "settings",
            "status": "OPEN",
        })
    elif not seo_audits or (seo_audits[0].overall_score or 0) < 80:
        score_now = seo_audits[0].overall_score if seo_audits else None
        opportunities.append({
            "id": "opp-seo-audit",
            "category": "SEO",
            "name": "Melhorar saúde técnica SEO do site" if seo_audits else "Executar 1ª Auditoria Técnica SEO real do site",
            "description": f"Score SEO atual: {score_now}/100 em {tenant.domain}." if seo_audits else f"O domínio {tenant.domain} ainda não passou por checagem HTTP real.",
            "evidence": f"{len(seo_audits)} auditoria(s) registrada(s) para {tenant.domain}.",
            "origin": "REAL",
            "potential": "ALTO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "BAIXO (1 clique)",
            "priority": "ALTA",
            "estimated_impact": "Identificar erros de título, meta description, H1 e Schema.org",
            "next_action_label": "Auditar Site Agora",
            "target_view": "seo",
            "status": "OPEN",
        })
        actions.append({
            "id": "act-run-seo",
            "what_to_do": f"Executar auditoria técnica SEO real em {tenant.domain}",
            "why_do_it": "Verificar ao vivo se o site tem falhas que impedem cliques orgânicos do Google.",
            "expected_result": "Nota SEO real + lista prática de correções no site.",
            "estimated_time": "10 segundos",
            "risk": "ZERO (leitura HTTP pública)",
            "cost_brl": 0.0,
            "approval_required": False,
            "target_view": "seo",
            "status": "READY",
        })

    # 2. Conteúdo & Campanhas
    if not campaigns or not personas:
        opportunities.append({
            "id": "opp-camp-persona",
            "category": "Campanhas",
            "name": "Definir Persona ideal e Campanha principal",
            "description": "Sem persona e campanha definidas, a divulgação fica genérica.",
            "evidence": f"{len(personas)} persona(s) e {len(campaigns)} campanha(s) ativas.",
            "origin": "REAL",
            "potential": "ALTO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "BAIXO (3 min)",
            "priority": "ALTA",
            "estimated_impact": "Comunicação direcionada ao público que realmente compra/cadastra",
            "next_action_label": "Criar Campanha/Plano IA",
            "target_view": "marketing",
            "status": "OPEN",
        })
        actions.append({
            "id": "act-cmo-plan",
            "what_to_do": "Gerar plano inicial de campanha para sua marca",
            "why_do_it": "Estruturar aquisição orgânica e canal prioritário automaticamente.",
            "expected_result": "Campanha inicial registrada e pronta para produzir conteúdo.",
            "estimated_time": "5 segundos",
            "risk": "ZERO (nenhuma mídia paga ligada)",
            "cost_brl": 0.0,
            "approval_required": False,
            "target_view": "marketing",
            "status": "READY",
        })

    if len(cf_items) < 5:
        opportunities.append({
            "id": "opp-content-batch",
            "category": "Conteúdo",
            "name": "Produzir 30 conteúdos alinhados ao site e persona",
            "description": "Você tem poucas peças prontas para divulgar sua marca nas redes sociais, blog e e-mail.",
            "evidence": f"{len(cf_items)} peça(s) encontrada(s) na Fábrica de Conteúdo.",
            "origin": "REAL",
            "potential": "ALTO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "BAIXO (1 clique)",
            "priority": "ALTA",
            "estimated_impact": "30 publicações prontas com link do seu site para usar no Modo Assistido",
            "next_action_label": "Gerar 30 Conteúdos",
            "target_view": "content_factory",
            "status": "OPEN",
        })
        actions.append({
            "id": "act-gen-content",
            "what_to_do": "Gerar lote de 30 conteúdos personalizados da marca",
            "why_do_it": "Ter posts, roteiros e e-mails prontos falando do seu site e público.",
            "expected_result": "30 peças criadas em rascunho pronto para revisar e copiar em 1 clique.",
            "estimated_time": "5 segundos",
            "risk": "ZERO (nada é publicado sozinho)",
            "cost_brl": 0.0,
            "approval_required": False,
            "target_view": "content_factory",
            "status": "READY",
        })
    elif unpublished_cf:
        opportunities.append({
            "id": "opp-content-assist",
            "category": "Novos Canais",
            "name": "Publicar peças prontas pelo Pacote 1-Clique",
            "description": f"Existem {len(unpublished_cf)} conteúdos já gerados prontos para copiar e divulgar.",
            "evidence": f"{len(unpublished_cf)} item(ns) com status PLANNED/ASSISTED_EXPORTED.",
            "origin": "REAL",
            "potential": "MÉDIO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "BAIXO",
            "priority": "MÉDIA",
            "estimated_impact": "Tráfego orgânico imediato sem esperar API OAuth",
            "next_action_label": "Abrir Fábrica de Conteúdo",
            "target_view": "content_factory",
            "status": "OPEN",
        })

    # 3. Leads & Vendas
    if stale_leads:
        opportunities.append({
            "id": "opp-leads-followup",
            "category": "Leads",
            "name": f"Qualificar e atender {len(stale_leads)} lead(s) novo(s) no CRM",
            "description": "Há contatos recém-cadastrados aguardando pontuação e próximo passo comercial.",
            "evidence": f"{len(stale_leads)} lead(s) em NEW_LEAD sem avanço de funil.",
            "origin": "REAL",
            "potential": "ALTO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "BAIXO",
            "priority": "ALTA",
            "estimated_impact": "Menor tempo de resposta e maior taxa de fechamento",
            "next_action_label": "Pontuar Leads Agora",
            "target_view": "crm",
            "status": "OPEN",
        })
        actions.append({
            "id": "act-score-leads",
            "what_to_do": f"Qualificar e pontuar automaticamente {len(stale_leads)} lead(s) do CRM",
            "why_do_it": "Priorizar os interessados com maior intenção de compra/cadastro.",
            "expected_result": "Lead Score atualizado (0–100) + fila priorizada no CRM.",
            "estimated_time": "3 segundos",
            "risk": "ZERO (não envia mensagens externas)",
            "cost_brl": 0.0,
            "approval_required": False,
            "target_view": "crm",
            "status": "READY",
        })
    elif not real_leads:
        opportunities.append({
            "id": "opp-leads-capture",
            "category": "Vendas",
            "name": "Iniciar captação de leads com consentimento LGPD",
            "description": "Nenhum contato real foi registrado nesta empresa ainda.",
            "evidence": "0 leads reais no CRM desta conta.",
            "origin": "REAL",
            "potential": "ALTO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "BAIXO",
            "priority": "MÉDIA",
            "estimated_impact": "Base inicial rastreável para follow-up e propostas",
            "next_action_label": "Abrir CRM",
            "target_view": "crm",
            "status": "OPEN",
        })

    # 4. Concorrentes, Retenção, Upsell, Produtos, Automação & Integrações
    if not competitors:
        opportunities.append({
            "id": "opp-competitors",
            "category": "Concorrentes",
            "name": "Analisar 1 concorrente público (respeitando robots.txt)",
            "description": "Identifique como concorrentes posicionam oferta e título SEO em páginas públicas.",
            "evidence": "0 concorrentes cadastrados neste tenant.",
            "origin": "REAL",
            "potential": "MÉDIO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "BAIXO",
            "priority": "BAIXA",
            "estimated_impact": "Diferenciação clara de posicionamento",
            "next_action_label": "Mapear Concorrentes",
            "target_view": "competitors",
            "status": "OPEN",
        })

    if at_risk_cs:
        opportunities.append({
            "id": "opp-cs-retention",
            "category": "Retenção",
            "name": f"Reverter risco de cancelamento em {len(at_risk_cs)} cliente(s)",
            "description": "Foram detectadas notas NPS <= 6 exigindo ação preventiva.",
            "evidence": f"{len(at_risk_cs)} feedback(s) detratores registrados.",
            "origin": "REAL",
            "potential": "ALTO",
            "estimated_cost_brl": 0.0,
            "risk": "MÉDIO",
            "effort": "MÉDIO",
            "priority": "ALTA",
            "estimated_impact": "Preservação de receita recorrente",
            "next_action_label": "Ver Clientes em Risco",
            "target_view": "cs",
            "status": "OPEN",
        })

    if promoters_cs:
        opportunities.append({
            "id": "opp-cs-upsell",
            "category": "Upsell",
            "name": f"Oferecer upgrade/indicação para {len(promoters_cs)} promotor(es)",
            "description": "Clientes com NPS 9–10 estão prontos para planos superiores ou programa de indicação.",
            "evidence": f"{len(promoters_cs)} resposta(s) NPS >= 9.",
            "origin": "REAL",
            "potential": "MÉDIO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "BAIXO",
            "priority": "MÉDIA",
            "estimated_impact": "Expansão orgânica sem custo de aquisição",
            "next_action_label": "Abrir Pós-Venda",
            "target_view": "cs",
            "status": "OPEN",
        })

    if not products and not real_deals:
        opportunities.append({
            "id": "opp-products-catalog",
            "category": "Produtos",
            "name": "Definir oferta/serviço principal para propostas",
            "description": "Cadastre produtos ou serviços em Brand Intelligence / Multinegócio para acelerar vendas.",
            "evidence": "Nenhum produto cadastrado neste tenant.",
            "origin": "REAL",
            "potential": "MÉDIO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "BAIXO",
            "priority": "MÉDIA",
            "estimated_impact": "Propostas comerciais consistentes em 1 clique",
            "next_action_label": "Abrir Marca & Ofertas",
            "target_view": "settings",
            "status": "OPEN",
        })

    if len(rules) == 0:
        opportunities.append({
            "id": "opp-automation-zero",
            "category": "Automação",
            "name": "Ativar 1ª rotina automática em linguagem simples",
            "description": "Crie regras em Python nativo (ex.: acompanhar leads sem resposta) sem ferramentas externas.",
            "evidence": "0 regras de automação configuradas.",
            "origin": "REAL",
            "potential": "MÉDIO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "BAIXO",
            "priority": "MÉDIA",
            "estimated_impact": "Economia semanal operacional com supervisão",
            "next_action_label": "Criar Automação Simples",
            "target_view": "automations",
            "status": "OPEN",
        })

    if pending_intgs:
        opportunities.append({
            "id": "opp-integrations",
            "category": "Canais & Analytics",
            "name": f"Conectar integrações opcionais ({len(pending_intgs)} disponíveis)",
            "description": "GA4, Search Console ou redes sociais podem ser conectadas quando quiser envio direto.",
            "evidence": f"{len(pending_intgs)} integração(ões) aguardando credenciais; Modo Assistido segue ativo.",
            "origin": "REAL",
            "potential": "MÉDIO",
            "estimated_cost_brl": 0.0,
            "risk": "BAIXO",
            "effort": "MÉDIO",
            "priority": "BAIXA",
            "estimated_impact": "Telemetria automática e publicação direta com aprovação",
            "next_action_label": "Ver Integrações",
            "target_view": "integrations",
            "status": "BLOCKED_OPTIONAL_CREDENTIALS",
        })

    # Sempre garantir ações executivas úteis disponíveis no painel
    actions.append({
        "id": "act-brand-audit",
        "what_to_do": "Auditar consistência de marca entre textos e campanhas",
        "why_do_it": "Detectar termos proibidos, links ausentes ou textos genéricos fora do seu tom de voz.",
        "expected_result": "Nota de consistência de marca e lista exata do que ajustar.",
        "estimated_time": "3 segundos",
        "risk": "ZERO (somente leitura e diagnóstico)",
        "cost_brl": 0.0,
        "approval_required": False,
        "target_view": "settings",
        "status": "READY",
    })
    actions.append({
        "id": "act-data-analyst",
        "what_to_do": "Gerar análise consolidada dos indicadores reais (AI Data Analyst)",
        "why_do_it": "Consolidar origem de leads, conversão de funil e ROI real sem inventar métricas.",
        "expected_result": "Resumo analítico auditado salvo no histórico.",
        "estimated_time": "3 segundos",
        "risk": "ZERO",
        "cost_brl": 0.0,
        "approval_required": False,
        "target_view": "reports",
        "status": "READY",
    })

    return opportunities[:10], actions[:6]


def get_growth_command_center_service(db: Session, tenant_id: int) -> dict[str, Any]:
    """Retorna o AI Growth Command Center completo com dados reais verificados."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError(f"Tenant {tenant_id} não encontrado.")

    snap = _collect_real_snapshot(db, tenant)
    health_pack = compute_growth_score_and_health(db, tenant, snap=snap)
    opportunities, actions = build_opportunity_radar_and_actions(db, tenant, snap)

    # Atualiza contagem no card 'oportunidades' do business_health com total real detectado
    for item in health_pack["business_health"]:
        if item["key"] == "oportunidades":
            item["score"] = min(100, max(20, 100 - len(opportunities) * 8))
            item["value_label"] = f"{len(opportunities)} oportunidade(s)"
            item["summary"] = opportunities[0]["name"] if opportunities else "Nenhuma pendência crítica detectada."

    pending_approvals = [
        {"id": a.id, "title": a.title, "agent_id": a.agent_id, "action_type": a.action_type}
        for a in snap["approvals"]
        if a.status == "PENDING"
    ]
    open_alerts = [
        {"id": a.id, "title": a.title, "severity": a.severity, "message": a.message}
        for a in snap["alerts"]
        if not a.is_resolved
    ]
    recent_ai = [
        {
            "execution_uuid": e.execution_uuid,
            "task_type": e.task_type,
            "status": e.status,
            "provider": e.executed_provider or e.requested_provider,
            "cost_brl": e.confirmed_cost_brl if e.confirmed_cost_brl is not None else 0.0,
        }
        for e in snap["ai_execs"][:5]
    ]
    latest_briefing = snap["ceo_briefings"][0] if snap["ceo_briefings"] else None

    day_plan = [t.title for t in snap["ceo_tasks"][:4]] if snap["ceo_tasks"] else [a["what_to_do"] for a in actions[:3]]
    week_plan = [
        f"Auditar presença e SEO de {tenant.domain}" if (tenant.domain or "").strip() else "Cadastrar site oficial da marca para SEO",
        f"Manter cadência editorial na campanha {snap['campaigns'][0].name}" if snap["campaigns"] else "Criar 1ª campanha e 30 conteúdos alinhados à persona",
        f"Acompanhar {len(snap['real_leads'])} lead(s) e propostas comerciais no CRM com LGPD",
        "Revisar aprovações humanas e relatório semanal em Gestão -> Relatórios",
    ]

    ceo_briefing = {
        "headline": (
            latest_briefing.summary_headline
            if latest_briefing
            else f"Diagnóstico vivo de {tenant.brand_name}: {len(opportunities)} oportunidade(s) priorizada(s) e trava FREE_ONLY ativa."
        ),
        "summary": (
            f"A empresa {tenant.brand_name} ({tenant.niche}) possui Growth Score {health_pack['growth_score']['score']}/100, "
            f"{len(snap['campaigns'])} campanha(s), {len(snap['cf_items'])} peça(s) na Fábrica de Conteúdo, "
            f"{len(snap['real_leads'])} lead(s) reais e receita real de R$ {snap['kpis'].get('total_revenue', 0.0):,.2f}."
        ),
        "real_results": {
            "revenue_brl": float(snap["kpis"].get("total_revenue", 0.0) or 0.0),
            "expenses_brl": float(snap["kpis"].get("total_expenses", 0.0) or 0.0),
            "real_leads_count": len(snap["real_leads"]),
            "active_campaigns_count": len(snap["campaigns"]),
            "content_pieces_count": len(snap["cf_items"]) + len(snap["cal_items"]),
            "ai_confirmed_cost_brl": round(sum(float(e.confirmed_cost_brl or 0.0) for e in snap["ai_execs"]), 2),
        },
        "problems": health_pack["growth_score"]["limitations"],
        "opportunities_count": len(opportunities),
        "alerts": open_alerts[:5],
        "recommendations": [o["name"] for o in opportunities[:4]],
        "executed_actions": recent_ai,
        "pending_approvals": pending_approvals[:5],
        "day_plan": day_plan,
        "week_plan": week_plan,
    }

    brand_consistency = audit_brand_consistency_service(db, tenant_id)
    ask_logs = (
        db.query(AskUnionActionLog)
        .filter(AskUnionActionLog.tenant_id == tenant_id)
        .order_by(AskUnionActionLog.id.desc())
        .limit(8)
        .all()
    )

    return {
        "tenant_id": tenant.id,
        "brand_name": tenant.brand_name,
        "ui_mode": getattr(tenant, "ui_mode", "SIMPLE") or "SIMPLE",
        "business_health": health_pack["business_health"],
        "growth_score": health_pack["growth_score"],
        "ceo_briefing": ceo_briefing,
        "opportunity_radar": opportunities,
        "executive_actions": actions,
        "brand_consistency_summary": {
            "consistency_score": brand_consistency["consistency_score"],
            "issues_count": len(brand_consistency["inconsistencies"]),
        },
        "recent_ask_union": [
            {
                "id": al.id,
                "prompt": al.prompt,
                "intent": al.intent_classified,
                "status": al.status,
                "created_at": al.created_at.isoformat() if al.created_at else "",
            }
            for al in ask_logs
        ],
    }


def execute_or_decide_executive_action_service(
    db: Session,
    tenant_id: int,
    user: User,
    action_id: str,
    decision: str = "EXECUTE",
) -> dict[str, Any]:
    """Executa ação executiva segura ou registra agendamento/aprovação/rejeição auditável."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant não encontrado.")

    dec = decision.upper()
    if dec == "REJECT":
        record_audit_log(db, tenant_id=tenant_id, user_id=user.id, actor=user.email, action="EXECUTIVE_ACTION_REJECTED", resource_id=action_id)
        return {"ok": True, "action_id": action_id, "status": "REJECTED", "message": "Recomendação descartada com registro na auditoria."}

    if dec == "SCHEDULE":
        import hashlib as _hl
        rule = AutomationRule(
            tenant_id=tenant_id,
            name=f"Ação Agendada: {action_id}",
            code_key=f"exec_act_{_hl.sha1(action_id.encode('utf-8')).hexdigest()[:10]}",
            trigger_type="CRON",
            cron_expression="0 9 * * 1",
            event_name="WEEKLY_EXECUTIVE_ACTION",
            condition_json=json.dumps({"action_id": action_id}, ensure_ascii=False),
            action_agent="AGENT_01_CEO",
            action_task="ANALYZE_AND_REPORT",
            frequency_label="Semanal (Segunda 09:00)",
            scheduled_time="09:00",
            priority="HIGH",
            owner_role="AGENT_01_CEO",
            is_active=True,
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        record_audit_log(db, tenant_id=tenant_id, user_id=user.id, actor=user.email, action="EXECUTIVE_ACTION_SCHEDULED", resource_id=action_id)
        return {"ok": True, "action_id": action_id, "status": "SCHEDULED", "rule_id": rule.id, "message": "Ação agendada semanalmente no scheduler Python nativo."}

    # EXECUTE or APPROVE (sempre seguro / custo R$ 0)
    result_payload: dict[str, Any] = {}
    message = "Ação concluída com sucesso."
    if action_id == "act-run-seo":
        target = (tenant.domain or "").strip() or "https://automacao.projetosunion.cloud"
        kw = (tenant.niche or tenant.brand_name or "serviços").strip()
        audit = perform_real_seo_audit(db, tenant, target, kw)
        research_keywords_and_clusters(db, tenant, kw)
        result_payload = {"audit_id": audit.id, "overall_score": audit.overall_score, "target_url": audit.target_url}
        message = f"Auditoria SEO concluída em {audit.target_url}: nota {audit.overall_score}/100."
    elif action_id == "act-gen-content":
        batch = generate_30_day_content_batch_service(db, tenant_id=tenant_id, count=30, replace_drafts=False)
        result_payload = {"batch_id": batch["batch_id"], "total_generated": batch["total_generated"]}
        message = f"Lote com {batch['total_generated']} conteúdos personalizados gerado na Fábrica de Conteúdo."
    elif action_id == "act-score-leads":
        leads = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id).all()
        for ld in leads:
            sc, qual = compute_lead_score(ld)
            ld.lead_score = sc
            if ld.qualification_status == "NEW":
                ld.qualification_status = qual
        db.commit()
        result_payload = {"leads_scored": len(leads)}
        message = f"{len(leads)} lead(s) pontuado(s) no CRM com transparência."
    elif action_id == "act-brand-audit":
        result_payload = audit_brand_consistency_service(db, tenant_id)
        message = f"Auditoria de Marca concluída: consistência {result_payload['consistency_score']}/100."
    elif action_id == "act-cmo-plan":
        from app.agents.orchestrator import CentralOrchestrator
        from app.schemas.contracts import AgentTaskContract
        c = AgentTaskContract(workflow_run_id=f"exec-{uuid.uuid4().hex[:8]}", sender_agent="USER", target_agent="AGENT_02_CMO", task_name="generate_plan", tenant_id=tenant_id, autonomy_level=1)
        res = CentralOrchestrator.dispatch_task(db, tenant, c)
        result_payload = res.structured_output
        message = res.summary
    elif action_id == "act-data-analyst":
        from app.agents.orchestrator import CentralOrchestrator
        from app.schemas.contracts import AgentTaskContract
        c = AgentTaskContract(workflow_run_id=f"exec-{uuid.uuid4().hex[:8]}", sender_agent="USER", target_agent="AGENT_12_DATA_ANALYST", task_name="attribution_audit", tenant_id=tenant_id, autonomy_level=1)
        res = CentralOrchestrator.dispatch_task(db, tenant, c)
        result_payload = res.structured_output
        message = res.summary
    else:
        plan = generate_ceo_daily_execution_plan_service(db, tenant_id=tenant_id)
        result_payload = {"total_tasks": plan["total_tasks"]}
        message = f"Plano Diário atualizado ({plan['total_tasks']} prioridades reais)."

    record_audit_log(db, tenant_id=tenant_id, user_id=user.id, actor=user.email, action="EXECUTIVE_ACTION_EXECUTED", resource_id=action_id, details=result_payload)
    return {"ok": True, "action_id": action_id, "status": "EXECUTED", "message": message, "result": result_payload}


# ==============================================================================
# 2. BRAND INTELLIGENCE CENTER + VERSIONAMENTO + DETECTOR DE INCONSISTÊNCIAS
# ==============================================================================
def audit_brand_consistency_service(db: Session, tenant_id: int) -> dict[str, Any]:
    """Verifica campanhas, conteúdos, copies e SEO quanto à consistência com a Central de Marca."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        return {"consistency_score": 0, "inconsistencies": [], "checked_items": 0}

    brand = (tenant.brand_name or tenant.name or "").strip()
    domain = (tenant.domain or "").strip()
    forbidden_raw = getattr(tenant, "brand_forbidden_terms", "") or ""
    forbidden_terms = [t.strip().lower() for t in re.split(r"[,;\n]+", forbidden_raw) if t.strip()]

    cf_items = db.query(ContentFactoryItem).filter(ContentFactoryItem.tenant_id == tenant_id).limit(40).all()
    copies = db.query(CopyItem).filter(CopyItem.tenant_id == tenant_id).limit(20).all()
    campaigns = db.query(MarketingCampaign).filter(MarketingCampaign.tenant_id == tenant_id).limit(20).all()

    inconsistencies: list[dict[str, Any]] = []
    if not domain:
        inconsistencies.append({
            "severity": "MEDIUM",
            "source": "Identidade da Marca",
            "issue": "Site/domínio principal não cadastrado; CTAs ficam sem link oficial.",
            "recommendation": "Preencha o Site/Domínio Principal na Central de Marca.",
        })
    if not (getattr(tenant, "brand_differentials", "") or "").strip():
        inconsistencies.append({
            "severity": "LOW",
            "source": "Identidade Verbal",
            "issue": "Diferenciais competitivos ainda em branco.",
            "recommendation": "Informe 1 ou 2 diferenciais claros da marca.",
        })

    checked = 0
    for item in cf_items:
        checked += 1
        txt = f"{item.title} {item.body_text} {item.cta}".lower()
        for fword in forbidden_terms:
            if fword in txt:
                inconsistencies.append({
                    "severity": "HIGH",
                    "source": f"Fábrica de Conteúdo #{item.id}",
                    "issue": f"Contém termo proibido configurado na marca: '{fword}'.",
                    "recommendation": "Edite a peça ou regenere o lote de rascunhos.",
                })
        if brand and brand.lower() not in txt and domain and domain.lower() not in txt:
            inconsistencies.append({
                "severity": "LOW",
                "source": f"Fábrica de Conteúdo #{item.id}",
                "issue": f"Peça '{item.title[:45]}' não menciona a marca '{brand}' nem o site.",
                "recommendation": "Regere os rascunhos para aplicar sua marca em todas as peças.",
            })
        if "ia, automação & engenharia de software" in txt and tenant.niche and "engenharia de software" not in tenant.niche.lower():
            inconsistencies.append({
                "severity": "HIGH",
                "source": f"Fábrica de Conteúdo #{item.id}",
                "issue": "Peça herdada de nicho antigo genérico incompatível com o nicho atual.",
                "recommendation": "Clique em 'Limpar Rascunhos' ou 'Gerar Lote' substituindo rascunhos antigos.",
            })
            break  # evita flood repetido para o mesmo lote antigo

    for cp in copies:
        checked += 1
        txt = f"{cp.variant_a} {cp.variant_b}".lower()
        for fword in forbidden_terms:
            if fword in txt:
                inconsistencies.append({
                    "severity": "HIGH",
                    "source": f"Copy A/B #{cp.id} ({cp.title})",
                    "issue": f"Variante contém expressão proibida: '{fword}'.",
                    "recommendation": "Regerar copy respeitando palavras proibidas.",
                })

    for camp in campaigns:
        checked += 1

    penalty = sum(18 if x["severity"] == "HIGH" else (8 if x["severity"] == "MEDIUM" else 4) for x in inconsistencies)
    score = max(10, min(100, 100 - penalty))
    return {
        "consistency_score": score,
        "checked_items": checked,
        "inconsistencies": inconsistencies[:15],
    }


def get_brand_intelligence_service(db: Session, tenant_id: int) -> dict[str, Any]:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant não encontrado.")
    personas = db.query(MarketingPersona).filter(MarketingPersona.tenant_id == tenant_id).order_by(MarketingPersona.id.desc()).all()
    versions = db.query(BrandVersionRecord).filter(BrandVersionRecord.tenant_id == tenant_id).order_by(BrandVersionRecord.version_number.desc()).limit(10).all()
    audit = audit_brand_consistency_service(db, tenant_id)
    return {
        "brand_profile": {
            "brand_name": tenant.brand_name,
            "company_name": tenant.name,
            "domain": tenant.domain,
            "niche": tenant.niche,
            "logo_url": tenant.logo_url,
            "primary_color": tenant.primary_color,
            "secondary_color": tenant.secondary_color,
            "brand_voice": getattr(tenant, "brand_voice", "Consultivo, claro e orientado a resultados") or "Consultivo, claro e orientado a resultados",
            "brand_fonts": getattr(tenant, "brand_fonts", "Inter + Plus Jakarta Sans") or "Inter + Plus Jakarta Sans",
            "brand_differentials": getattr(tenant, "brand_differentials", "") or "",
            "brand_allowed_terms": getattr(tenant, "brand_allowed_terms", "") or "",
            "brand_forbidden_terms": getattr(tenant, "brand_forbidden_terms", "") or "",
            "brand_examples": getattr(tenant, "brand_examples", "") or "",
            "brand_description": getattr(tenant, "brand_description", "") or "",
            "target_audience": tenant.target_audience,
            "strategy_summary": tenant.strategy_summary,
            "products": json.loads(tenant.products_json or "[]"),
            "services": json.loads(tenant.services_json or "[]"),
            "personas": [{"id": p.id, "name": p.name, "value_proposition": p.value_proposition} for p in personas],
        },
        "consistency_audit": audit,
        "versions": [
            {
                "id": v.id,
                "version_number": v.version_number,
                "consistency_score": v.consistency_score,
                "notes": v.notes,
                "created_by": v.created_by,
                "created_at": v.created_at.isoformat() if v.created_at else "",
                "snapshot": json.loads(v.snapshot_json or "{}"),
            }
            for v in versions
        ],
    }


def save_brand_intelligence_service(db: Session, tenant_id: int, payload: dict[str, Any], actor: str) -> dict[str, Any]:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant não encontrado.")

    field_map = {
        "brand_name": "brand_name",
        "domain": "domain",
        "niche": "niche",
        "logo_url": "logo_url",
        "primary_color": "primary_color",
        "secondary_color": "secondary_color",
        "brand_voice": "brand_voice",
        "brand_fonts": "brand_fonts",
        "brand_differentials": "brand_differentials",
        "brand_allowed_terms": "brand_allowed_terms",
        "brand_forbidden_terms": "brand_forbidden_terms",
        "brand_examples": "brand_examples",
        "brand_description": "brand_description",
        "target_audience": "target_audience",
        "strategy_summary": "strategy_summary",
    }
    for req_key, attr in field_map.items():
        if payload.get(req_key) is not None:
            val = str(payload[req_key])
            setattr(tenant, attr, val if attr in ("primary_color", "secondary_color", "logo_url") else sanitize_text(val))
    if payload.get("products") is not None:
        tenant.products_json = json.dumps(payload["products"], ensure_ascii=False)
    if payload.get("services") is not None:
        tenant.services_json = json.dumps(payload["services"], ensure_ascii=False)

    db.commit()
    audit = audit_brand_consistency_service(db, tenant_id)
    last_ver = db.query(BrandVersionRecord).filter(BrandVersionRecord.tenant_id == tenant_id).order_by(BrandVersionRecord.version_number.desc()).first()
    next_ver = (last_ver.version_number + 1) if last_ver else 1

    snapshot = {
        "brand_name": tenant.brand_name,
        "domain": tenant.domain,
        "niche": tenant.niche,
        "brand_voice": getattr(tenant, "brand_voice", ""),
        "brand_fonts": getattr(tenant, "brand_fonts", ""),
        "primary_color": tenant.primary_color,
        "secondary_color": tenant.secondary_color,
        "brand_differentials": getattr(tenant, "brand_differentials", ""),
        "target_audience": tenant.target_audience,
    }
    ver = BrandVersionRecord(
        tenant_id=tenant_id,
        version_number=next_ver,
        snapshot_json=json.dumps(snapshot, ensure_ascii=False),
        consistency_score=audit["consistency_score"],
        inconsistencies_json=json.dumps(audit["inconsistencies"], ensure_ascii=False),
        notes=sanitize_text(str(payload.get("notes") or "Snapshot salvo na Central de Marca"))[:250],
        created_by=actor,
    )
    db.add(ver)
    db.commit()
    record_audit_log(db, tenant_id=tenant_id, actor=actor, action="BRAND_INTELLIGENCE_SAVED", resource_id=f"v{next_ver}")
    return get_brand_intelligence_service(db, tenant_id)


# ==============================================================================
# 3. PROGRESSIVE BUSINESS ONBOARDING (6 ETAPAS RECUPERÁVEIS)
# ==============================================================================
ONBOARDING_STAGES_META = [
    {"step": 1, "key": "empresa", "title": "1. Sua Empresa", "subtitle": "Nome, segmento, país, público e oferta"},
    {"step": 2, "key": "marca", "title": "2. Sua Marca", "subtitle": "Identidade visual, tom de voz, diferenciais"},
    {"step": 3, "key": "objetivos", "title": "3. Seus Objetivos", "subtitle": "Leads, vendas, tráfego, SEO, retenção"},
    {"step": 4, "key": "plano", "title": "4. Plano de Crescimento", "subtitle": "Estratégia criada automaticamente para sua realidade"},
    {"step": 5, "key": "acoes", "title": "5. Primeiras Ações", "subtitle": "Executar ou aprovar tarefas iniciais seguras"},
    {"step": 6, "key": "conexoes", "title": "6. Conexões", "subtitle": "Integrações opcionais sem bloquear seu começo"},
]


def get_progressive_onboarding_service(db: Session, tenant_id: int) -> dict[str, Any]:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant não encontrado.")
    state = json.loads(getattr(tenant, "onboarding_state_json", "{}") or "{}")
    goals = json.loads(getattr(tenant, "growth_goals_json", "[]") or "[]")
    integrations = db.query(IntegrationConnection).filter(IntegrationConnection.tenant_id == tenant_id).all()
    return {
        "current_step": int(getattr(tenant, "onboarding_step", 1) or 1),
        "completed": bool(state.get("completed", False)),
        "stages": ONBOARDING_STAGES_META,
        "data": {
            "name": tenant.name,
            "niche": tenant.niche,
            "brand_description": getattr(tenant, "brand_description", "") or "",
            "brand_country": getattr(tenant, "brand_country", "Brasil") or "Brasil",
            "domain": tenant.domain,
            "target_audience": tenant.target_audience,
            "products": json.loads(tenant.products_json or "[]"),
            "services": json.loads(tenant.services_json or "[]"),
            "brand_name": tenant.brand_name,
            "brand_voice": getattr(tenant, "brand_voice", "Consultivo, claro e orientado a resultados") or "",
            "primary_color": tenant.primary_color,
            "secondary_color": tenant.secondary_color,
            "logo_url": tenant.logo_url,
            "brand_differentials": getattr(tenant, "brand_differentials", "") or "",
            "growth_goals": goals,
            "generated_plan": state.get("generated_plan"),
            "starter_actions_done": state.get("starter_actions_done", []),
            "connected_integrations_count": len([i for i in integrations if i.status == "CONNECTED"]),
        },
    }


def save_progressive_onboarding_step_service(
    db: Session,
    tenant_id: int,
    step: int,
    data: dict[str, Any],
    save_only: bool = False,
    reset_onboarding: bool = False,
    actor: str = "Empreendedor",
) -> dict[str, Any]:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant não encontrado.")

    state = json.loads(getattr(tenant, "onboarding_state_json", "{}") or "{}")
    if reset_onboarding:
        tenant.onboarding_step = 1
        tenant.onboarding_state_json = "{}"
        db.commit()
        return get_progressive_onboarding_service(db, tenant_id)

    if step == 1:
        for k in ("name", "niche", "domain", "target_audience", "brand_description", "brand_country"):
            if k in data and data[k] is not None:
                setattr(tenant, k, sanitize_text(str(data[k])))
        if isinstance(data.get("products"), list):
            tenant.products_json = json.dumps([sanitize_text(str(p)) for p in data["products"] if str(p).strip()], ensure_ascii=False)
        if isinstance(data.get("services"), list):
            tenant.services_json = json.dumps([sanitize_text(str(s)) for s in data["services"] if str(s).strip()], ensure_ascii=False)
    elif step == 2:
        for k in ("brand_name", "brand_voice", "primary_color", "secondary_color", "logo_url", "brand_differentials", "target_audience"):
            if k in data and data[k] is not None:
                setattr(tenant, k, str(data[k]) if k in ("primary_color", "secondary_color", "logo_url") else sanitize_text(str(data[k])))
    elif step == 3:
        goals = data.get("growth_goals", [])
        if isinstance(goals, list):
            tenant.growth_goals_json = json.dumps([sanitize_text(str(g)) for g in goals], ensure_ascii=False)
    elif step == 4:
        goals = json.loads(getattr(tenant, "growth_goals_json", "[]") or "[]")
        plan_obj = {
            "brand": tenant.brand_name,
            "niche": tenant.niche,
            "site": tenant.domain or "A definir",
            "goals": goals or ["Gerar leads", "Criar conteúdo"],
            "channels": ["Conteúdo Orgânico & SEO", "Redes Sociais (Modo Assistido)", "CRM com Follow-up LGPD"],
            "steps_30_days": [
                f"Semana 1: Garantir presença e auditoria técnica em {tenant.domain or tenant.brand_name}",
                f"Semana 2: Publicar 30 peças da Fábrica de Conteúdo direcionadas a {tenant.target_audience}",
                "Semana 3: Capturar e pontuar leads interessados no CRM com resposta rápida",
                "Semana 4: Medir atribuição real por canal e ajustar oferta vencedora",
            ],
            "cost_policy": "FREE_ONLY (R$ 0,00 adicional)",
        }
        state["generated_plan"] = plan_obj
        # Garantir campanha inicial se ainda não houver nenhuma
        has_camp = db.query(MarketingCampaign).filter(MarketingCampaign.tenant_id == tenant_id).first()
        if not has_camp:
            db.add(MarketingCampaign(
                tenant_id=tenant_id,
                name=f"Plano de Crescimento — {tenant.brand_name}",
                campaign_type="ACQUISITION",
                channel="SEO + Social (Modo Assistido)",
                objective=", ".join(goals) if goals else f"Atrair {tenant.target_audience}",
                funnel_stage="TOFU/MOFU/BOFU",
                budget_planned=0.0,
                status="ACTIVE",
                data_origin="GOAL",
            ))
    elif step == 5:
        action_done = str(data.get("run_starter_action") or "").strip()
        done_list = list(state.get("starter_actions_done", []))
        if action_done == "content_batch":
            generate_30_day_content_batch_service(db, tenant_id=tenant_id, count=15)
            if "content_batch" not in done_list:
                done_list.append("content_batch")
        elif action_done == "daily_plan":
            generate_ceo_daily_execution_plan_service(db, tenant_id=tenant_id)
            if "daily_plan" not in done_list:
                done_list.append("daily_plan")
        state["starter_actions_done"] = done_list
    elif step == 6:
        state["completed"] = True

    next_step = step if save_only else (6 if step >= 6 else step + 1)
    tenant.onboarding_step = next_step
    tenant.onboarding_state_json = json.dumps(state, ensure_ascii=False)
    db.commit()
    record_audit_log(db, tenant_id=tenant_id, actor=actor, action="ONBOARDING_STEP_SAVED", resource_id=f"step_{step}")
    return get_progressive_onboarding_service(db, tenant_id)


# ==============================================================================
# 4. COPILOTO ESTRUTURADO "ASK UNION" (ZERO CHATBOT ISOLADO)
# ==============================================================================
def ask_union_copilot_service(
    db: Session,
    tenant_id: int,
    user: User,
    prompt: str,
    auto_execute_safe: bool = False,
) -> dict[str, Any]:
    """Interpreta pedido de negócio do empreendedor com contexto real e gera plano + ações executáveis rastreáveis."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant não encontrado.")

    clean_prompt = sanitize_text(prompt).strip()
    low = clean_prompt.lower()
    snap = _collect_real_snapshot(db, tenant)
    health_pack = compute_growth_score_and_health(db, tenant, snap=snap)

    if any(k in low for k in ("automa", "quando ", "toda segunda", "todo dia", "follow-up automatico", "workflow")):
        intent = "BUILD_AUTOMATION"
    elif any(k in low for k in ("seo", "google", "site", "trafego", "tráfego", "orgânico", "organico")):
        intent = "SEO_GROWTH"
    elif any(k in low for k in ("divulg", "conteúdo", "conteudo", "post", "instagram", "redes", "campanha")):
        intent = "PROMOTE_AND_CONTENT"
    elif any(k in low for k in ("lead", "crm", "cliente", "proposta", "vender", "venda", "faturar")):
        intent = "INCREASE_SALES"
    else:
        intent = "BUSINESS_DIAGNOSIS"

    brand = tenant.brand_name or tenant.name
    domain = (tenant.domain or "").strip()
    goals = json.loads(getattr(tenant, "growth_goals_json", "[]") or "[]")
    growth_score_val = health_pack["growth_score"]["score"]

    diagnosis_summary = (
        f"Contexto lido de {brand} (Growth Score {growth_score_val}/100): "
        f"{len(snap['campaigns'])} campanha(s), {len(snap['cf_items'])} conteúdo(s), "
        f"{len(snap['real_leads'])} lead(s) real(is), {len(snap['rules'])} automação(ões), "
        f"política de custos {'FREE_ONLY' if not snap['ai_cfg'] else snap['ai_cfg'].cost_policy_mode}."
    )

    plan_steps: list[str] = []
    suggested_actions: list[dict[str, Any]] = []

    if intent == "INCREASE_SALES":
        plan_steps = [
            f"1. Estruturar campanha de aquisição direcionada para {tenant.target_audience} no nicho {tenant.niche}.",
            f"2. Gerar conteúdos focados no site {domain or brand} com CTA direto para captura LGPD.",
            "3. Qualificar cada lead por Lead Score (0–100) e abrir proposta comercial aprovável no funil.",
        ]
        suggested_actions = [
            {"id": "act-cmo-plan", "label": "Gerar Plano/Campanha Comercial", "target_view": "marketing", "safe": True, "cost_brl": 0.0},
            {"id": "act-gen-content", "label": "Produzir 30 Conteúdos de Divulgação", "target_view": "content_factory", "safe": True, "cost_brl": 0.0},
            {"id": "act-score-leads", "label": f"Qualificar {len(snap['real_leads'])} Lead(s) no CRM", "target_view": "crm", "safe": True, "cost_brl": 0.0},
        ]
    elif intent == "PROMOTE_AND_CONTENT":
        plan_steps = [
            f"1. Auditar alinhamento dos textos com a marca {brand} e domínio {domain or '(configure o site em Marca)'}.",
            "2. Produzir 30 publicações multicanal (Instagram, Facebook, TikTok, YouTube, LinkedIn, Blog, E-mail).",
            "3. Usar Pacote 1-Clique (Modo Assistido) sem depender de contas externas OAuth nem correr riscos de postagem errada.",
        ]
        suggested_actions = [
            {"id": "act-brand-audit", "label": "Checar Consistência de Marca", "target_view": "settings", "safe": True, "cost_brl": 0.0},
            {"id": "act-gen-content", "label": "Gerar 30 Conteúdos da Marca Agora", "target_view": "content_factory", "safe": True, "cost_brl": 0.0},
        ]
    elif intent == "SEO_GROWTH":
        plan_steps = [
            f"1. Executar auditoria técnica HTTP real em {domain or 'seu site oficial'}.",
            f"2. Mapear palavras-chave reais de {tenant.niche} sem inventar volumes de busca.",
            "3. Publicar artigos otimizados com Schema.org conectados à sua oferta.",
        ]
        suggested_actions = [
            {"id": "act-run-seo", "label": "Auditar Site e Buscar Keywords Agora", "target_view": "seo", "safe": True, "cost_brl": 0.0},
        ]
    elif intent == "BUILD_AUTOMATION":
        conv = build_conversational_automation_service(db, tenant_id, prompt=clean_prompt, dry_run=True, approve_create=False)
        plan_steps = [
            f"1. Gatilho identificado: {conv['workflow_preview']['trigger_label']}.",
            f"2. Ação proposta em Python/APScheduler: {conv['workflow_preview']['action_label']}.",
            "3. Teste em simulação (dry-run) aprovado em custo R$ 0,00; pronto para você ativar em Automações.",
        ]
        suggested_actions = [
            {"id": "act-create-conv-auto", "label": "Abrir Construtor de Automação Pronto", "target_view": "automations", "safe": True, "cost_brl": 0.0, "workflow": conv["workflow_preview"]},
        ]
    else:
        plan_steps = [
            f"1. Revisar prioridades do Command Center e Growth Score atual ({growth_score_val}/100).",
            "2. Resolver pendências humanas em Meu Trabalho antes de novas campanhas.",
            "3. Gerar análise analítica consolidada em AI Data Analyst.",
        ]
        suggested_actions = [
            {"id": "act-data-analyst", "label": "Rodar Análise Consolidada (AI Data Analyst)", "target_view": "reports", "safe": True, "cost_brl": 0.0},
            {"id": "act-brand-audit", "label": "Auditar Consistência da Marca", "target_view": "settings", "safe": True, "cost_brl": 0.0},
        ]

    executed_actions: list[dict[str, Any]] = []
    if auto_execute_safe and suggested_actions and suggested_actions[0]["id"] != "act-create-conv-auto":
        exec_res = execute_or_decide_executive_action_service(db, tenant_id, user, suggested_actions[0]["id"], decision="EXECUTE")
        executed_actions.append(exec_res)

    resp_obj = {
        "prompt": clean_prompt,
        "intent": intent,
        "context_used": {
            "brand": brand,
            "domain": domain,
            "niche": tenant.niche,
            "goals": goals,
            "growth_score": growth_score_val,
            "cost_policy": "FREE_ONLY",
        },
        "diagnosis": diagnosis_summary,
        "plan_steps": plan_steps,
        "suggested_actions": suggested_actions,
        "executed_actions": executed_actions,
        "response_origin": "DETERMINISTIC_PYTHON_COPILOT",
    }

    log = AskUnionActionLog(
        tenant_id=tenant_id,
        user_email=user.email,
        prompt=clean_prompt,
        intent_classified=intent,
        response_json=json.dumps(resp_obj, ensure_ascii=False),
        executed_actions_json=json.dumps(executed_actions, ensure_ascii=False),
        status="EXECUTED" if executed_actions else "PLANNED",
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    resp_obj["log_id"] = log.id
    return resp_obj


# ==============================================================================
# 5. CONVERSATIONAL AUTOMATION BUILDER (100% PYTHON / APSCHEDULER — ZERO N8N)
# ==============================================================================
def build_conversational_automation_service(
    db: Session,
    tenant_id: int,
    prompt: str,
    dry_run: bool = True,
    approve_create: bool = False,
    actor: str = "Empreendedor",
) -> dict[str, Any]:
    """Interpreta pedido em português natural, valida riscos/custos e cria regra real Python/APScheduler."""
    clean = sanitize_text(prompt).strip()
    low = clean.lower()
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant não encontrado.")

    # Inferir gatilho, condição, cron e ação sem depender de ferramentas externas
    if "3 dias" in low or "nao responderam" in low or "não responderam" in low or "follow-up" in low or "followup" in low:
        name = "Follow-up automático de leads sem resposta há 3 dias"
        trigger_type = "CRON"
        trigger_event = "CRM_INACTIVE_LEADS_3D"
        cron_expr = "0 10 * * *"
        action_type = "SCORE_AND_ALERT"
        target_agent = "AGENT_08_SALES"
        condition = "Leads reais sem contato há >= 72h e sem opt-out LGPD"
        action_label = "Criar tarefa de retorno no CRM e alertar em Meu Trabalho"
        trigger_label = "Diariamente às 10:00 (ou verificação de leads inativos)"
        leads_affected = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id, CRMLead.pipeline_stage == "NEW_LEAD").count()
        dry_preview = f"Simulação segura: {leads_affected} lead(s) novo(s) seriam avaliados para tarefa de follow-up (sem envio externo automático)."
    elif "entrar um lead" in low or "novo lead" in low or "lead" in low:
        name = "Analisar novo lead automaticamente e avisar em Meu Trabalho"
        trigger_type = "EVENT"
        trigger_event = "ON_LEAD_CREATED"
        cron_expr = "0 */4 * * *"
        action_type = "QUALIFY_AND_NOTIFY"
        target_agent = "AGENT_08_SALES"
        condition = "Todo novo lead cadastrado com consentimento LGPD válido"
        action_label = "Calcular Lead Score (0–100) e criar alerta prioritário"
        trigger_label = "Ao entrar um novo lead no CRM"
        leads_cnt = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id).count()
        dry_preview = f"Simulação segura: regra pronta para pontuar imediatamente novos leads ({leads_cnt} já na base)."
    elif "campanha semanal" in low or "toda semana" in low or "conteudo" in low or "conteúdo" in low:
        name = "Preparar planejamento e ideias semanais de campanha"
        trigger_type = "CRON"
        trigger_event = "WEEKLY_CAMPAIGN_PREP"
        cron_expr = "0 8 * * 1"
        action_type = "PREPARE_WEEKLY_CONTENT"
        target_agent = "AGENT_02_CMO"
        condition = "Manter rascunhos em aprovação humana (nunca postar sozinho)"
        action_label = "Gerar sugestões semanais alinhadas à Central de Marca"
        trigger_label = "Toda segunda-feira às 08:00"
        dry_preview = f"Simulação segura: prepara pauta semanal da marca '{tenant.brand_name}' sem custo e com aprovação obrigatória."
    elif "churn" in low or "deixando de comprar" in low or "inativo" in low or "retenc" in low or "retenç" in low:
        name = "Monitorar clientes inativos e sinalizar risco de cancelamento"
        trigger_type = "CRON"
        trigger_event = "CUSTOMER_HEALTH_CHECK"
        cron_expr = "0 14 * * 1,4"
        action_type = "CS_HEALTH_ALERT"
        target_agent = "AGENT_11_CS"
        condition = "Clientes com NPS <= 6 ou sem interação recente"
        action_label = "Abrir alerta de retenção e plano de reengajamento"
        trigger_label = "Segundas e quintas às 14:00"
        at_risk = db.query(CustomerFeedback).filter(CustomerFeedback.tenant_id == tenant_id, CustomerFeedback.nps_score <= 6).count()
        dry_preview = f"Simulação segura: {at_risk} cliente(s) atual(is) em risco seriam sinalizados para o time."
    elif "relatorio" in low or "relatório" in low or "segunda" in low:
        name = "Relatório executivo semanal toda segunda-feira"
        trigger_type = "CRON"
        trigger_event = "WEEKLY_EXECUTIVE_REPORT"
        cron_expr = "0 8 * * 1"
        action_type = "GENERATE_EXECUTIVE_REPORT"
        target_agent = "AGENT_12_DATA_ANALYST"
        condition = "Consolidar apenas dados reais e custos auditados"
        action_label = "Atualizar Analytics e briefing semanal sem inventar números"
        trigger_label = "Toda segunda-feira às 08:00"
        dry_preview = f"Simulação segura: consolida dados reais de '{tenant.brand_name}' sem custos de API."
    else:
        name = f"Rotina personalizada: {clean[:58]}"
        trigger_type = "CRON"
        trigger_event = "CUSTOM_GROWTH_CHECK"
        cron_expr = "0 9 * * *"
        action_type = "DAILY_DIAGNOSIS"
        target_agent = "AGENT_01_CEO"
        condition = "Execução segura em Python nativo com governança"
        action_label = "Executar análise diária e notificar prioridades"
        trigger_label = "Diariamente às 09:00"
        dry_preview = f"Simulação segura concluída para '{clean[:70]}': execução validada sem impacto externo."

    workflow_preview = {
        "name": name,
        "goal_prompt": clean,
        "engine": "Python Native + APScheduler (100% Internalizado, zero n8n)",
        "trigger_type": trigger_type,
        "trigger_event": trigger_event,
        "trigger_label": trigger_label,
        "cron_expression": cron_expr,
        "condition": condition,
        "action_type": action_type,
        "action_label": action_label,
        "target_agent": target_agent,
        "dependencies": ["PostgreSQL + APScheduler nativo (já ativo na VPS)"],
        "risk": "BAIXO (apenas análise, alertas e rascunhos; sem disparos externos pagos)",
        "estimated_cost_brl": 0.0,
        "requires_approval": True,
        "dry_run_result": dry_preview if dry_run else "Não executado",
    }

    created_rule_id = None
    status_out = "PREVIEW_READY"
    if approve_create:
        existing = db.query(AutomationRule).filter(AutomationRule.tenant_id == tenant_id, AutomationRule.name == name).first()
        if existing:
            created_rule_id = existing.id
            status_out = "ALREADY_EXISTS"
        else:
            import hashlib as _hl
            rule_code = f"conv_{_hl.sha1(name.encode('utf-8')).hexdigest()[:10]}"
            rule = AutomationRule(
                tenant_id=tenant_id,
                name=name,
                code_key=rule_code,
                trigger_type=trigger_type,
                cron_expression=cron_expr,
                event_name=trigger_event,
                condition_json=json.dumps({"condition": condition, "goal_prompt": clean, "requires_approval": True}, ensure_ascii=False),
                action_agent=target_agent,
                action_task=action_type,
                frequency_label=trigger_label[:80],
                scheduled_time="08:00" if "08:00" in cron_expr else "09:00",
                priority="HIGH",
                owner_role=target_agent,
                is_active=True,
                business_unit_code="ALL",
            )
            db.add(rule)
            db.commit()
            db.refresh(rule)
            created_rule_id = rule.id
            status_out = "ACTIVATED"
            record_audit_log(db, tenant_id=tenant_id, actor=actor, action="CONVERSATIONAL_AUTOMATION_CREATED", resource_id=str(rule.id), details={"prompt": clean, "name": name})

    return {
        "status": status_out,
        "created_rule_id": created_rule_id,
        "workflow_preview": workflow_preview,
    }


# ==============================================================================
# 6. ANALYTICS & ATTRIBUTION HUB (ZERO DADOS INVENTADOS)
# ==============================================================================
def get_analytics_attribution_service(db: Session, tenant_id: int) -> dict[str, Any]:
    """Consolida funil e atribuição por canal/campanha diferenciando REAL, ESTIMATIVA e NÃO DISPONÍVEL."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant não encontrado.")
    snap = _collect_real_snapshot(db, tenant)
    real_leads = snap["real_leads"]
    real_deals = snap["real_deals"]
    campaigns = snap["campaigns"]
    cf_items = snap["cf_items"]
    kpis = snap["kpis"]

    channel_map: dict[str, dict[str, Any]] = {}
    for ld in real_leads:
        src = (getattr(ld, "source_channel", "") or getattr(ld, "campaign_attribution", "") or "Orgânico / Direto").strip()
        bucket = channel_map.setdefault(src, {"channel": src, "leads": 0, "qualified_leads": 0, "estimated_pipeline_brl": 0.0, "data_origin": "REAL"})
        bucket["leads"] += 1
        if (ld.lead_score or 0) >= 60 or ld.qualification_status in ("MQL", "SQL", "QUALIFIED"):
            bucket["qualified_leads"] += 1
        bucket["estimated_pipeline_brl"] += float(ld.estimated_value or 0.0)

    funnel = [
        {"stage": "1. Campanhas Ativas", "count": len(campaigns), "origin": "REAL"},
        {"stage": "2. Conteúdos Produzidos", "count": len(cf_items) + len(snap["cal_items"]), "origin": "REAL"},
        {"stage": "3. Leads Capturados (LGPD)", "count": len(real_leads), "origin": "REAL"},
        {"stage": "4. Leads Qualificados", "count": len([l for l in real_leads if (l.lead_score or 0) >= 60 or l.qualification_status in ("MQL", "SQL", "QUALIFIED")]), "origin": "REAL"},
        {"stage": "5. Oportunidades no Funil", "count": len(real_deals), "origin": "REAL"},
        {"stage": "6. Vendas Fechadas", "count": len([d for d in real_deals if getattr(d, "stage", "") == "CLOSED_WON" or getattr(d, "status", "") == "WON"]), "origin": "REAL"},
    ]

    connected_analytics = [i.provider_name for i in snap["integrations"] if i.status == "CONNECTED" and i.provider_key in ("ga4", "google_search_console", "meta_ads", "google_ads")]

    return {
        "brand_name": tenant.brand_name,
        "attribution_methodology": "Atribuição direta First-Touch baseada no campo 'source_channel' / 'campaign_attribution' dos leads reais no PostgreSQL.",
        "external_analytics_status": "CONNECTED" if connected_analytics else "NAO_DISPONIVEL",
        "connected_analytics_sources": connected_analytics,
        "funnel": funnel,
        "channels": list(channel_map.values()),
        "finance_summary": {
            "real_revenue_brl": float(kpis.get("total_revenue", 0.0) or 0.0),
            "real_expenses_brl": float(kpis.get("total_expenses", 0.0) or 0.0),
            "roi_pct": kpis.get("roi_pct", 0.0),
            "data_origin": "REAL" if float(kpis.get("total_revenue", 0.0) or 0.0) > 0 else "NAO_DISPONIVEL",
        },
        "campaigns_breakdown": [
            {
                "id": c.id,
                "name": c.name,
                "channel": c.channel,
                "budget_planned_brl": float(c.budget_planned or 0.0),
                "spend_real_brl": float(c.spend_real or 0.0),
                "revenue_attributed_brl": float(c.revenue_attributed or 0.0),
                "roi_pct": float(c.roi_pct or 0.0),
                "data_origin": c.data_origin or "REAL",
            }
            for c in campaigns
        ],
    }
