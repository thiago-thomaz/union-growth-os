import json
from typing import Any
from sqlalchemy.orm import Session
from app.models.entities import AuditLog, Tenant


SAAS_PLANS: dict[str, dict[str, Any]] = {
    "STARTER": {
        "code": "STARTER",
        "name": "Starter",
        "max_companies": 1,
        "max_users": 2,
        "agents_included": ["AGENT_01_CEO", "AGENT_03_SEO", "AGENT_04_SOCIAL", "AGENT_05_CREATIVE", "AGENT_06_COPYWRITER"],
        "features": [
            "1 empresa",
            "SEO básico e auditoria técnica",
            "Calendário editorial",
            "Produção de conteúdo e artes",
            "Relatórios básicos",
        ],
        "monthly_price_reference_brl": 0.0,
        "billing_status": "DISABLED_BY_DEFAULT_REQUIRES_AUTHORIZATION",
    },
    "PRO": {
        "code": "PRO",
        "name": "Pro",
        "max_companies": 3,
        "max_users": 10,
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
        ],
        "features": [
            "Agentes adicionais (CMO, Growth, Sales, Concorrentes)",
            "CRM completo com pipeline e lead scoring",
            "Central de Automações nativas em Python",
            "Central de Integrações oficiais",
            "Análise de concorrentes",
        ],
        "monthly_price_reference_brl": 0.0,
        "billing_status": "DISABLED_BY_DEFAULT_REQUIRES_AUTHORIZATION",
    },
    "BUSINESS": {
        "code": "BUSINESS",
        "name": "Business",
        "max_companies": 10,
        "max_users": 50,
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
        ],
        "features": [
            "Multiusuários com RBAC completo",
            "Multiempresa (Multi-tenant isolado)",
            "Gestão financeira e performance avançada",
            "Relatórios executivos e CEO Daily Briefing",
            "Automações avançadas com retry e backoff",
        ],
        "monthly_price_reference_brl": 0.0,
        "billing_status": "DISABLED_BY_DEFAULT_REQUIRES_AUTHORIZATION",
    },
    "ENTERPRISE": {
        "code": "ENTERPRISE",
        "name": "Enterprise",
        "max_companies": 999,
        "max_users": 9999,
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
        ],
        "features": [
            "Multiunidades ilimitadas",
            "Permissões avançadas e governança LGPD",
            "Personalização completa de marca e templates",
            "Auditoria completa e backup sob demanda",
            "Todos os 11 Agentes + Orquestrador Central habilitados",
        ],
        "monthly_price_reference_brl": 0.0,
        "billing_status": "DISABLED_BY_DEFAULT_REQUIRES_AUTHORIZATION",
    },
}


def get_tenant_plan_info(tenant: Tenant) -> dict[str, Any]:
    tier = (tenant.plan_tier or "ENTERPRISE").upper()
    return SAAS_PLANS.get(tier, SAAS_PLANS["ENTERPRISE"])


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

