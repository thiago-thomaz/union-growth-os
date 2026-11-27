import json
from typing import Any
from sqlalchemy.orm import Session
from app.models.entities import (
    AIEngineExecutionRecord,
    AuditLog,
    AutomationRule,
    CRMLead,
    Tenant,
    User,
)


SAAS_PLANS: dict[str, dict[str, Any]] = {
    "FREE": {
        "code": "FREE",
        "name": "Free (Ativação PLG)",
        "target_segment": "Empreendedores e validação inicial (Product-Led Growth)",
        "max_companies": 1,
        "max_users": 2,
        "max_crm_leads": 100,
        "max_active_automations": 2,
        "monthly_ai_actions_limit": 30,
        "agents_included": ["AGENT_01_CEO", "AGENT_03_SEO", "AGENT_04_SOCIAL", "AGENT_08_SALES"],
        "features": [
            "1 workspace empresarial",
            "Até 100 leads CRM com governança LGPD",
            "Auditoria SEO HTTP gratuita + ASK UNION básico",
            "Até 2 rotinas Python automáticas",
            "Modo Assistido 1-Clique (custo zero)",
        ],
        "recommended_price_usd": 0.0,
        "monthly_price_reference_brl": 0.0,
        "billing_status": "PLG_STRUCTURE_SIMULATION_ONLY_NO_LIVE_BILLING",
    },
    "STARTER": {
        "code": "STARTER",
        "name": "Starter",
        "target_segment": "Profissionais autônomos e microempresas em tração",
        "max_companies": 1,
        "max_users": 3,
        "max_crm_leads": 1000,
        "max_active_automations": 8,
        "monthly_ai_actions_limit": 250,
        "agents_included": [
            "AGENT_01_CEO",
            "AGENT_02_CMO",
            "AGENT_03_SEO",
            "AGENT_04_SOCIAL",
            "AGENT_05_CREATIVE",
            "AGENT_06_COPYWRITER",
            "AGENT_08_SALES",
        ],
        "features": [
            "1 empresa com Central de Marca versionada",
            "Fábrica de Conteúdo (30 peças/lote) + Copywriting",
            "CRM completo até 1.000 leads LGPD",
            "Até 8 automações nativas em Python",
            "Auditoria SEO técnica + Google Autocomplete",
        ],
        "recommended_price_usd": 29.0,
        "monthly_price_reference_brl": 147.0,
        "billing_status": "DISABLED_BY_DEFAULT_REQUIRES_AUTHORIZATION",
    },
    "PRO": {
        "code": "PRO",
        "name": "Pro (Recomendado — ICP Principal)",
        "target_segment": "PMEs B2B, prestadores de serviços e operações em crescimento",
        "max_companies": 3,
        "max_users": 10,
        "max_crm_leads": 10000,
        "max_active_automations": 25,
        "monthly_ai_actions_limit": 1500,
        "agents_included": [
            "AGENT_01_CEO",
            "AGENT_02_CMO",
            "AGENT_03_SEO",
            "AGENT_04_SOCIAL",
            "AGENT_05_CREATIVE",
            "AGENT_06_COPYWRITER",
            "AGENT_07_GROWTH",
            "AGENT_08_SALES",
            "AGENT_09_COMPETITIVE",
            "AGENT_11_CS",
        ],
        "features": [
            "Até 3 empresas isoladas (multi-tenant)",
            "CRM Revenue Intelligence + Propostas PDF",
            "10 agentes + Concorrentes + CS / NPS",
            "Até 25 automações conversacionais Python",
            "Central multimotor de IA gratuita (Gemini/Groq)",
        ],
        "recommended_price_usd": 79.0,
        "monthly_price_reference_brl": 397.0,
        "billing_status": "DISABLED_BY_DEFAULT_REQUIRES_AUTHORIZATION",
    },
    "BUSINESS": {
        "code": "BUSINESS",
        "name": "Business",
        "target_segment": "Empresas com times comerciais e múltiplos canais",
        "max_companies": 10,
        "max_users": 30,
        "max_crm_leads": 50000,
        "max_active_automations": 100,
        "monthly_ai_actions_limit": 5000,
        "agents_included": [
            "AGENT_01_CEO",
            "AGENT_02_CMO",
            "AGENT_03_SEO",
            "AGENT_04_SOCIAL",
            "AGENT_05_CREATIVE",
            "AGENT_06_COPYWRITER",
            "AGENT_07_GROWTH",
            "AGENT_08_SALES",
            "AGENT_09_COMPETITIVE",
            "AGENT_10_FINANCE",
            "AGENT_11_CS",
            "AGENT_12_DATA_ANALYST",
        ],
        "features": [
            "Até 10 empresas e 30 usuários com RBAC completo",
            "Todos os 12 Agentes + AI Data Analyst",
            "Financeiro & ROI auditável sem mistura Sandbox",
            "Automações escaláveis com retry e backoff",
            "Relatórios executivos & Atribuição por canal",
        ],
        "recommended_price_usd": 179.0,
        "monthly_price_reference_brl": 897.0,
        "billing_status": "DISABLED_BY_DEFAULT_REQUIRES_AUTHORIZATION",
    },
    "ENTERPRISE": {
        "code": "ENTERPRISE",
        "name": "Enterprise & Agências",
        "target_segment": "Agências multi-conta, holdings e operações multi-unidade",
        "max_companies": 999,
        "max_users": 9999,
        "max_crm_leads": 500000,
        "max_active_automations": 999,
        "monthly_ai_actions_limit": 50000,
        "agents_included": [
            "AGENT_01_CEO",
            "AGENT_02_CMO",
            "AGENT_03_SEO",
            "AGENT_04_SOCIAL",
            "AGENT_05_CREATIVE",
            "AGENT_06_COPYWRITER",
            "AGENT_07_GROWTH",
            "AGENT_08_SALES",
            "AGENT_09_COMPETITIVE",
            "AGENT_10_FINANCE",
            "AGENT_11_CS",
            "AGENT_12_DATA_ANALYST",
        ],
        "features": [
            "Workspaces multi-tenant e sub-contas de agência",
            "RBAC estrito, auditoria completa e backup JSON sob demanda",
            "Propostas, Contratos e Módulos Multinegócio completos",
            "Política BYO-Key multimotor com trava FREE_ONLY / OWNER_APPROVED",
            "Todos os 12 Agentes + Orquestrador Central",
        ],
        "recommended_price_usd": 399.0,
        "monthly_price_reference_brl": 1990.0,
        "billing_status": "DISABLED_BY_DEFAULT_REQUIRES_AUTHORIZATION",
    },
}


def get_tenant_plan_info(tenant: Tenant) -> dict[str, Any]:
    tier = (tenant.plan_tier or "ENTERPRISE").upper()
    return SAAS_PLANS.get(tier, SAAS_PLANS["ENTERPRISE"])


def get_tenant_plan_usage_summary(db: Session, tenant: Tenant, owner_email: str = "") -> dict[str, Any]:
    """Mede consumo real por tenant comparado aos limites do catálogo PLG (sem bloqueio destrutivo nem cobrança ativa)."""
    plan = get_tenant_plan_info(tenant)
    tid = tenant.id
    owner = owner_email or tenant.owner_email or ""

    companies_count = db.query(Tenant).filter(Tenant.owner_email == owner).count() if owner else 1
    users_count = db.query(User).filter(User.tenant_id == tid).count()
    leads_count = db.query(CRMLead).filter(CRMLead.tenant_id == tid).count()
    active_automations = db.query(AutomationRule).filter(AutomationRule.tenant_id == tid, AutomationRule.is_active == True).count()
    ai_runs_count = db.query(AIEngineExecutionRecord).filter(AIEngineExecutionRecord.tenant_id == tid).count()

    def _meter(label: str, used: int, limit: int) -> dict[str, Any]:
        pct = min(100, round((used / max(1, limit)) * 100, 1))
        return {
            "label": label,
            "used": used,
            "limit": limit,
            "usage_pct": pct,
            "near_limit": pct >= 80.0,
            "exceeded": used > limit,
        }

    meters = {
        "companies": _meter("Empresas / Workspaces", companies_count, plan["max_companies"]),
        "users": _meter("Usuários ativos", users_count, plan["max_users"]),
        "crm_leads": _meter("Leads no CRM", leads_count, plan["max_crm_leads"]),
        "automations": _meter("Automações ativas", active_automations, plan["max_active_automations"]),
        "ai_actions": _meter("Execuções IA (histórico)", ai_runs_count, plan["monthly_ai_actions_limit"]),
    }
    upgrade_reasons = [m["label"] for m in meters.values() if m["near_limit"] or m["exceeded"]]

    return {
        "active_plan": plan,
        "plans_catalog": SAAS_PLANS,
        "usage_meters": meters,
        "upgrade_recommended": len(upgrade_reasons) > 0 and plan["code"] != "ENTERPRISE",
        "upgrade_reasons": upgrade_reasons,
        "billing_status": "PLG_STRUCTURE_SIMULATION_ONLY_NO_LIVE_BILLING",
        "charge_enabled": False,
        "data_origin": "REAL",
    }


def record_audit_log(
    db: Session,
    tenant_id: int,
    action: str,
    actor: str = "system",
    user_id: int | None = None,
    resource_type: str = "system",
    resource_id: str = "",
    ip_address: str = "127.0.0.1",
    details: dict[str, Any] | None = None,
) -> AuditLog:
    entry = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        ip_address=ip_address,
        details_json=json.dumps(details or {}, ensure_ascii=False),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
