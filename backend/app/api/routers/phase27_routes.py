"""Modular FastAPI sub-router for Phase 27 capabilities — UNION GROWTH OS."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_active_tenant_id, get_current_user, require_roles
from app.models.entities import Tenant, User
from app.services.phase27_audit_and_growth_engine import (
    get_current_persistent_growth_plan_service,
    get_system_audit_history_service,
    run_ai_agents_benchmark_service,
    run_complete_system_audit_service,
    update_growth_plan_step_service,
)
from app.services.plans_and_audit import SAAS_PLANS, get_tenant_plan_usage_summary, record_audit_log
from app.services.versioning_engine import get_system_version_payload, list_releases_history_payload

phase27_router = APIRouter()


class StepActionInput(BaseModel):
    command: str = Field(..., description="EXECUTE, COMPLETE, CANCEL ou REPLAN")
    horizon: str | None = Field(default=None)
    due_date: str | None = Field(default=None)


class ChangePlanTierInput(BaseModel):
    plan_tier: str = Field(..., min_length=2, max_length=30)
    sandbox_checkout_ack: bool = Field(default=False)


def _tenant_or_404(db: Session, tid: int) -> Tenant:
    t = db.query(Tenant).filter(Tenant.id == tid).first()
    if not t:
        raise HTTPException(status_code=404, detail="Empresa (Tenant) não encontrada.")
    return t


@phase27_router.get("/system/version")
def get_system_version(db: Session = Depends(get_db)):
    """Retorna versão oficial SemVer, ambiente, build/commit e status operacional."""
    return get_system_version_payload(db)


@phase27_router.get("/system/releases")
def get_system_releases(db: Session = Depends(get_db)):
    """Histórico rastreável e persistido de releases do UNION GROWTH OS."""
    return list_releases_history_payload(db)


@phase27_router.post("/system/audit/run")
def run_complete_system_audit(
    user: User = Depends(require_roles("owner", "admin", "manager")),
    db: Session = Depends(get_db),
):
    """Executa auditoria completa não-destrutiva de 25 categorias e persiste snapshot histórico."""
    tid = get_active_tenant_id(user)
    tenant = _tenant_or_404(db, tid)
    return run_complete_system_audit_service(db, tenant=tenant, actor=user.email)


@phase27_router.get("/system/audit/history")
def get_system_audit_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna última auditoria completa e histórico comparativo persistido no PostgreSQL."""
    tid = get_active_tenant_id(user)
    return get_system_audit_history_service(db, tenant_id=tid)


@phase27_router.get("/growth-os/growth-plan/current")
def get_current_growth_plan(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Carrega o plano de crescimento ativo persistido no PostgreSQL para o tenant."""
    tid = get_active_tenant_id(user)
    return {"plan": get_current_persistent_growth_plan_service(db, tenant_id=tid)}


@phase27_router.patch("/growth-os/growth-plan/steps/{step_id}")
def update_growth_plan_step(
    step_id: int,
    payload: StepActionInput,
    user: User = Depends(require_roles("owner", "admin", "manager")),
    db: Session = Depends(get_db),
):
    """Executa, conclui, cancela ou replaneja uma etapa persistida do Centro de Crescimento."""
    tid = get_active_tenant_id(user)
    tenant = _tenant_or_404(db, tid)
    try:
        return update_growth_plan_step_service(
            db,
            tenant=tenant,
            user=user,
            step_db_id=step_id,
            command=payload.command,
            new_horizon=payload.horizon,
            new_due_date=payload.due_date,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@phase27_router.get("/ai/benchmark")
def get_ai_agents_benchmark(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Benchmark real e não-destrutivo dos 12 agentes (latência, fallback e trava FREE_ONLY)."""
    tid = get_active_tenant_id(user)
    return run_ai_agents_benchmark_service(db, tenant_id=tid)


@phase27_router.post("/plans/change-tier")
def change_tenant_plan_tier(
    payload: ChangePlanTierInput,
    user: User = Depends(require_roles("owner", "admin")),
    db: Session = Depends(get_db),
):
    """Atualiza tier PLG com validação backend estrita e zero cobrança automática live."""
    tid = get_active_tenant_id(user)
    tenant = _tenant_or_404(db, tid)
    code = payload.plan_tier.strip().upper()
    if code not in SAAS_PLANS:
        raise HTTPException(status_code=400, detail=f"Plano '{code}' inválido. Opções: {', '.join(SAAS_PLANS.keys())}")
    old_tier = tenant.plan_tier
    tenant.plan_tier = code
    db.commit()
    db.refresh(tenant)
    record_audit_log(
        db,
        tenant_id=tid,
        user_id=user.id,
        actor=user.email,
        action="PLAN_TIER_CHANGED_SANDBOX",
        resource_type="Tenant",
        resource_id=str(tid),
        details={"from": old_tier, "to": code, "charge_enabled": False},
    )
    summary = get_tenant_plan_usage_summary(db, tenant, owner_email=user.email)
    return {
        "ok": True,
        "previous_plan": old_tier,
        "new_plan": code,
        "charge_enabled": False,
        "message": f"Plano alterado para {SAAS_PLANS[code]['name']} (modo Sandbox/PLG — nenhuma cobrança realizada).",
        **summary,
    }
