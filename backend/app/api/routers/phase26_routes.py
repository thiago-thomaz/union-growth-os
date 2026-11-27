"""Modular FastAPI sub-router for Phase 26 capabilities — UNION GROWTH OS."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_active_tenant_id, get_current_user, require_roles
from app.models.entities import Tenant, User
from app.services.phase14_automation_factory import get_ceo_daily_plan_service
from app.services.phase23_growth_platform import get_growth_command_center_service
from app.services.phase25_product_engine import get_activation_and_retention_service
from app.services.phase26_growth_os_engine import (
    build_phase26_ai_agents_matrix_service,
    execute_growth_plan_step_service,
    get_saas_entitlements_and_billing_readiness_service,
    move_crm_deal_stage_service,
    prepare_smart_lead_followup_service,
)
from app.services.phase27_audit_and_growth_engine import (
    create_persistent_growth_plan_service,
    get_current_persistent_growth_plan_service,
)
from app.services.versioning_engine import get_system_version_payload

phase26_router = APIRouter()


class GrowthPlanInput(BaseModel):
    objective: str = Field(default="Aumentar clientes, vendas e receita recorrente", min_length=2, max_length=300)
    product_or_service: str = Field(default="", max_length=220)
    target_audience: str = Field(default="", max_length=220)
    region: str = Field(default="Brasil", max_length=120)
    budget_brl: float = Field(default=0.0, ge=0.0)
    target_goal: str = Field(default="", max_length=220)
    deadline_days: int = Field(default=90, ge=7, le=365)


class GrowthStepExecuteInput(BaseModel):
    action_type: str = Field(..., min_length=2, max_length=80)


class DealMoveStageInput(BaseModel):
    stage: str = Field(..., min_length=2, max_length=50)


def _tenant_or_404(db: Session, tid: int) -> Tenant:
    t = db.query(Tenant).filter(Tenant.id == tid).first()
    if not t:
        raise HTTPException(status_code=404, detail="Empresa (Tenant) não encontrada.")
    return t


@phase26_router.get("/growth-os/bootstrap")
def growth_os_fast_bootstrap(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Consolida os payloads iniciais críticos (Wave 1) em 1 requisição única sem duplicar lógica."""
    from app.api.routes import get_dashboard_overview, get_me

    tid = get_active_tenant_id(user)
    return {
        "me": get_me(user=user, db=db),
        "overview": get_dashboard_overview(user=user, db=db),
        "command_center": get_growth_command_center_service(db, tenant_id=tid),
        "activation_retention": get_activation_and_retention_service(db, tenant_id=tid),
        "ceo_daily_plan": get_ceo_daily_plan_service(db, tenant_id=tid),
        "version_info": get_system_version_payload(db),
        "growth_plan": get_current_persistent_growth_plan_service(db, tenant_id=tid),
    }


@phase26_router.post("/growth-os/growth-plan")
def create_growth_execution_plan(
    payload: GrowthPlanInput,
    user: User = Depends(require_roles("owner", "admin", "manager")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    try:
        return create_persistent_growth_plan_service(db, tenant_id=tid, payload=payload.model_dump(), actor=user.email)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))


@phase26_router.post("/growth-os/growth-plan/execute-step")
def execute_growth_plan_step(
    payload: GrowthStepExecuteInput,
    user: User = Depends(require_roles("owner", "admin", "manager")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    tenant = _tenant_or_404(db, tid)
    try:
        return execute_growth_plan_step_service(db, tenant=tenant, user=user, action_type=payload.action_type)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@phase26_router.get("/agents/matrix")
def get_agents_classification_matrix(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    return build_phase26_ai_agents_matrix_service(db, tenant_id=tid)


@phase26_router.post("/crm/deals/{deal_id}/move-stage")
def move_crm_deal_stage(
    deal_id: int,
    payload: DealMoveStageInput,
    user: User = Depends(require_roles("owner", "admin", "manager")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    try:
        return move_crm_deal_stage_service(db, tenant_id=tid, deal_id=deal_id, new_stage=payload.stage, actor=user.email)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@phase26_router.post("/crm/leads/{lead_id}/smart-followup")
def prepare_smart_lead_followup(
    lead_id: int,
    user: User = Depends(require_roles("owner", "admin", "manager")),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    tenant = _tenant_or_404(db, tid)
    try:
        return prepare_smart_lead_followup_service(db, tenant=tenant, lead_id=lead_id, actor=user.email)
    except ValueError as ve:
        code = status.HTTP_400_BAD_REQUEST if "LGPD" in str(ve) else status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=code, detail=str(ve))


@phase26_router.get("/plans/entitlements")
def get_saas_entitlements_readiness(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tid = get_active_tenant_id(user)
    tenant = _tenant_or_404(db, tid)
    return get_saas_entitlements_and_billing_readiness_service(db, tenant=tenant, owner_email=user.email)
