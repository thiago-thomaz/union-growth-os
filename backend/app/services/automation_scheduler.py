import json
import logging
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.agents.orchestrator import CentralOrchestrator, get_effective_autonomy_level
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.entities import AuditLog, AutomationExecution, AutomationRule, SchedulerHeartbeat, Tenant
from app.schemas.contracts import AgentTaskContract

logger = logging.getLogger("union_growth_os.scheduler")

_scheduler_lock = threading.Lock()
_running_rules_lock: set[int] = set()
scheduler = BackgroundScheduler(timezone="UTC")


DEFAULT_12_AUTOMATION_TEMPLATES: list[dict[str, Any]] = [
    {
        "code_key": "daily_trends_07h",
        "name": "01. Pesquisa Diária de Tendências e Oportunidades de Conteúdo (07:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 7 * * *",
        "action_agent": "AGENT_04_SOCIAL",
        "action_task": "research_trends_and_plan_content",
        "frequency_label": "Diário às 07:00",
        "scheduled_time": "07:00",
        "priority": "HIGH",
    },
    {
        "code_key": "daily_ceo_briefing_08h",
        "name": "02. Execução Diária do CEO Daily Briefing (08:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 8 * * *",
        "action_agent": "AGENT_01_CEO",
        "action_task": "generate_ceo_daily_briefing",
        "frequency_label": "Diário às 08:00",
        "scheduled_time": "08:00",
        "priority": "CRITICAL",
    },
    {
        "code_key": "daily_content_planning_09h",
        "name": "03. Planejamento Diário de Conteúdo e Temas (09:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 9 * * *",
        "action_agent": "AGENT_02_CMO",
        "action_task": "plan_daily_content",
        "frequency_label": "Diário às 09:00",
        "scheduled_time": "09:00",
        "priority": "HIGH",
    },
    {
        "code_key": "daily_content_production_10h",
        "name": "04. Produção Automática da Content Factory (10:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 10 * * *",
        "action_agent": "AGENT_05_CREATIVE",
        "action_task": "produce_content_factory_assets",
        "frequency_label": "Diário às 10:00",
        "scheduled_time": "10:00",
        "priority": "HIGH",
    },
    {
        "code_key": "daily_publish_prep_11h",
        "name": "05. Validação e Preparação de Fila de Publicações (11:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 11 * * *",
        "action_agent": "AGENT_04_SOCIAL",
        "action_task": "prepare_social_publications",
        "frequency_label": "Diário às 11:00",
        "scheduled_time": "11:00",
        "priority": "MEDIUM",
    },
    {
        "code_key": "daily_new_leads_check",
        "name": "06. Verificação e Qualificação Diária de Leads Novos (12:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 12 * * *",
        "action_agent": "AGENT_08_SALES",
        "action_task": "qualify_daily_leads",
        "frequency_label": "Diário às 12:00",
        "scheduled_time": "12:00",
        "priority": "HIGH",
    },
    {
        "code_key": "daily_seo_research_14h",
        "name": "07. Pesquisa Diária de SEO e Oportunidades Técnicas (14:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 14 * * *",
        "action_agent": "AGENT_03_SEO",
        "action_task": "daily_seo_research",
        "frequency_label": "Diário às 14:00",
        "scheduled_time": "14:00",
        "priority": "HIGH",
    },
    {
        "code_key": "daily_competitor_analysis_15h",
        "name": "08. Monitoramento Diário de Concorrentes e Preços Públicos (15:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 15 * * *",
        "action_agent": "AGENT_09_COMPETITIVE",
        "action_task": "weekly_competitor_intelligence",
        "frequency_label": "Diário às 15:00",
        "scheduled_time": "15:00",
        "priority": "MEDIUM",
    },
    {
        "code_key": "daily_campaign_review_16h",
        "name": "09. Revisão Diária de Campanhas, Criativos e Conversões (16:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 16 * * *",
        "action_agent": "AGENT_02_CMO",
        "action_task": "daily_campaign_review",
        "frequency_label": "Diário às 16:00",
        "scheduled_time": "16:00",
        "priority": "HIGH",
    },
    {
        "code_key": "daily_social_metrics_review",
        "name": "10. Análise Diária de Publicações e Métricas Sociais (17:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 17 * * *",
        "action_agent": "AGENT_04_SOCIAL",
        "action_task": "analyze_daily_publications",
        "frequency_label": "Diário às 17:00",
        "scheduled_time": "17:00",
        "priority": "MEDIUM",
    },
    {
        "code_key": "daily_executive_report_18h",
        "name": "11. Relatório Diário Executivo e Consolidação Financeira (18:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 18 * * *",
        "action_agent": "AGENT_10_FINANCE",
        "action_task": "generate_daily_executive_report",
        "frequency_label": "Diário às 18:00",
        "scheduled_time": "18:00",
        "priority": "CRITICAL",
    },
    {
        "code_key": "weekly_seo_report",
        "name": "12. Auditoria e Relatório Semanal de SEO (Segunda 09:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 9 * * 1",
        "action_agent": "AGENT_03_SEO",
        "action_task": "weekly_seo_audit_and_keywords",
        "frequency_label": "Semanal (Segunda 09:00)",
        "scheduled_time": "09:00",
        "priority": "HIGH",
    },
    {
        "code_key": "weekly_campaign_evaluation",
        "name": "13. Avaliação Semanal de Campanhas e ROI (Sexta 17:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 17 * * 5",
        "action_agent": "AGENT_02_CMO",
        "action_task": "weekly_campaign_roi_review",
        "frequency_label": "Semanal (Sexta 17:00)",
        "scheduled_time": "17:00",
        "priority": "HIGH",
    },
    {
        "code_key": "weekly_database_backup_sun",
        "name": "14. Backup e Manutenção Preventiva do Banco PostgreSQL (Domingo 02:00)",
        "trigger_type": "CRON",
        "cron_expression": "0 2 * * 0",
        "action_agent": "AGENT_01_CEO",
        "action_task": "weekly_database_backup",
        "frequency_label": "Semanal (Domingo 02:00)",
        "scheduled_time": "02:00",
        "priority": "HIGH",
    },
    {
        "code_key": "monthly_strategic_planning",
        "name": "15. Planejamento Estratégico e Marketing Mensal",
        "trigger_type": "CRON",
        "cron_expression": "0 6 1 * *",
        "action_agent": "AGENT_02_CMO",
        "action_task": "generate_monthly_marketing_plan",
        "frequency_label": "Mensal (Dia 1 às 06:00)",
        "scheduled_time": "06:00",
        "priority": "CRITICAL",
    },
    {
        "code_key": "event_on_lead_created",
        "name": "16. Gatilho Imediato: Qualificar e Pontuar Novo Lead no CRM",
        "trigger_type": "EVENT",
        "cron_expression": "",
        "event_name": "lead.created",
        "action_agent": "AGENT_08_SALES",
        "action_task": "qualify_and_score_new_lead",
        "frequency_label": "Tempo Real (Evento)",
        "scheduled_time": "Imediato",
        "priority": "CRITICAL",
    },
    {
        "code_key": "event_on_publication_failed",
        "name": "17. Gatilho de Recuperação: Registrar Erro e Reexecutar Publicação com Backoff",
        "trigger_type": "EVENT",
        "cron_expression": "",
        "event_name": "publication.failed",
        "action_agent": "AGENT_04_SOCIAL",
        "action_task": "retry_failed_publication",
        "frequency_label": "Tempo Real (Falha)",
        "scheduled_time": "Imediato",
        "priority": "HIGH",
    },
    {
        "code_key": "threshold_kpi_drop_alert",
        "name": "18. Alerta de Queda de Indicador: Identificar Causa Provável e Notificar",
        "trigger_type": "THRESHOLD",
        "cron_expression": "",
        "event_name": "kpi.drop_detected",
        "action_agent": "AGENT_10_FINANCE",
        "action_task": "diagnose_kpi_drop",
        "frequency_label": "Monitoramento Contínuo",
        "scheduled_time": "Contínuo",
        "priority": "CRITICAL",
    },
    {
        "code_key": "event_on_goal_achieved",
        "name": "19. Gatilho de Meta Atingida: Gerar Relatório Executivo de Conquista",
        "trigger_type": "EVENT",
        "cron_expression": "",
        "event_name": "goal.achieved",
        "action_agent": "AGENT_01_CEO",
        "action_task": "generate_goal_achievement_report",
        "frequency_label": "Tempo Real (Meta)",
        "scheduled_time": "Imediato",
        "priority": "HIGH",
    },
]


def ensure_tenant_automations_seeded(db: Session, tenant_id: int) -> list[AutomationRule]:
    existing_keys = {
        r.code_key
        for r in db.query(AutomationRule).filter(AutomationRule.tenant_id == tenant_id).all()
    }
    added = False
    for tpl in DEFAULT_12_AUTOMATION_TEMPLATES:
        if tpl["code_key"] not in existing_keys:
            rule = AutomationRule(
                tenant_id=tenant_id,
                name=tpl["name"],
                code_key=tpl["code_key"],
                trigger_type=tpl["trigger_type"],
                cron_expression=tpl["cron_expression"],
                event_name=tpl.get("event_name", ""),
                condition_json="{}",
                action_agent=tpl["action_agent"],
                action_task=tpl["action_task"],
                frequency_label=tpl["frequency_label"],
                scheduled_time=tpl["scheduled_time"],
                priority=tpl["priority"],
                owner_role="AI Orchestrator",
                is_active=True,
                max_retries=3,
                timeout_seconds=60,
            )
            db.add(rule)
            added = True
    if added:
        db.commit()
    return (
        db.query(AutomationRule)
        .filter(AutomationRule.tenant_id == tenant_id)
        .order_by(AutomationRule.id.asc())
        .all()
    )


def execute_automation_rule(
    db: Session,
    rule: AutomationRule,
    idempotency_key: str | None = None,
    context_params: dict[str, Any] | None = None,
    simulate_failure_once: bool = False,
) -> AutomationExecution:
    """
    Executes an AutomationRule with:
    - Idempotency check (prevents duplicate execution for the same idempotency_key)
    - Concurrency control lock per rule.id
    - Automatic retry with exponential backoff up to rule.max_retries
    - Full execution logging in AutomationExecution
    """
    idem_key = idempotency_key or f"rule-{rule.id}-{uuid.uuid4().hex[:10]}"

    existing_exec = (
        db.query(AutomationExecution)
        .filter(
            AutomationExecution.tenant_id == rule.tenant_id,
            AutomationExecution.rule_id == rule.id,
            AutomationExecution.idempotency_key == idem_key,
            AutomationExecution.status.in_(("SUCCESS", "RETRIED")),
        )
        .first()
    )
    if existing_exec:
        return existing_exec

    with _scheduler_lock:
        if rule.id in _running_rules_lock:
            blocked = AutomationExecution(
                tenant_id=rule.tenant_id,
                rule_id=rule.id,
                idempotency_key=idem_key,
                status="BLOCKED",
                attempt_number=1,
                duration_ms=0.0,
                result_summary_json=json.dumps({"reason": "CONCURRENCY_LOCK_ACTIVE"}),
                error_message="Regra já está em execução concorrente.",
            )
            db.add(blocked)
            db.commit()
            db.refresh(blocked)
            return blocked
        _running_rules_lock.add(rule.id)

    try:
        tenant = db.query(Tenant).filter(Tenant.id == rule.tenant_id).first()
        if not tenant:
            raise RuntimeError("Tenant não encontrado para execução da automação.")

        max_attempts = max(1, int(rule.max_retries or 3))
        last_error = ""
        started_at = datetime.now(timezone.utc)
        t0 = time.perf_counter()

        for attempt in range(1, max_attempts + 1):
            try:
                if simulate_failure_once and attempt == 1:
                    raise RuntimeError("Falha transitória simulada para validação de retry com backoff.")

                contract = AgentTaskContract(
                    workflow_run_id=f"auto-{rule.id}-{uuid.uuid4().hex[:8]}",
                    sender_agent="SCHEDULER",
                    target_agent=rule.action_agent,
                    task_name=rule.action_task,
                    tenant_id=tenant.id,
                    autonomy_level=get_effective_autonomy_level(tenant, rule.action_agent),
                    parameters=context_params or {"mode": "automated_run"},
                    timeout_seconds=rule.timeout_seconds or 60,
                )
                agent_res = CentralOrchestrator.dispatch_task(db, tenant, contract)
                duration_ms = round((time.perf_counter() - t0) * 1000, 2)

                exec_record = AutomationExecution(
                    tenant_id=tenant.id,
                    rule_id=rule.id,
                    idempotency_key=idem_key,
                    status="SUCCESS" if attempt == 1 else "RETRIED",
                    attempt_number=attempt,
                    duration_ms=duration_ms,
                    result_summary_json=json.dumps(
                        {
                            "summary": agent_res.summary,
                            "agent_id": agent_res.agent_id,
                            "attempts_used": attempt,
                        },
                        ensure_ascii=False,
                    ),
                    error_message="" if attempt == 1 else f"Recuperado na tentativa {attempt} após erro: {last_error}",
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc),
                )
                db.add(exec_record)
                rule.last_run_at = datetime.now(timezone.utc)
                rule.last_status = "SUCCESS"
                rule.run_count = (rule.run_count or 0) + 1
                db.commit()
                db.refresh(exec_record)
                return exec_record

            except Exception as exc:
                last_error = str(exc)
                if attempt < max_attempts:
                    time.sleep(0.05 * (2 ** (attempt - 1)))

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        failed_record = AutomationExecution(
            tenant_id=rule.tenant_id,
            rule_id=rule.id,
            idempotency_key=idem_key,
            status="FAILED",
            attempt_number=max_attempts,
            duration_ms=duration_ms,
            result_summary_json=json.dumps({"failed_after_attempts": max_attempts}),
            error_message=last_error,
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
        )
        db.add(failed_record)
        rule.last_run_at = datetime.now(timezone.utc)
        rule.last_status = "FAILED"
        rule.failure_count = (rule.failure_count or 0) + 1
        db.add(
            AuditLog(
                tenant_id=rule.tenant_id,
                actor="scheduler",
                action="ALERT:AUTOMATION_FAILED",
                resource_type="automation_rule",
                resource_id=str(rule.id),
                details_json=json.dumps({"code_key": rule.code_key, "attempts": max_attempts, "error": last_error[:300]}, ensure_ascii=False),
            )
        )
        logger.error("ALERT automation %s failed after %s attempts: %s", rule.code_key, max_attempts, last_error)
        db.commit()
        db.refresh(failed_record)
        return failed_record
    finally:
        with _scheduler_lock:
            _running_rules_lock.discard(rule.id)


def trigger_event_automations(
    db: Session,
    tenant_id: int,
    event_name: str,
    context_params: dict[str, Any] | None = None,
) -> list[AutomationExecution]:
    rules = (
        db.query(AutomationRule)
        .filter(
            AutomationRule.tenant_id == tenant_id,
            AutomationRule.event_name == event_name,
            AutomationRule.is_active == True,
        )
        .all()
    )
    results = []
    for r in rules:
        results.append(execute_automation_rule(db, r, context_params=context_params))
    return results


BOOT_ID = uuid.uuid4().hex[:12]
SCHEDULER_TZ = "America/Sao_Paulo"


def _record_heartbeat(db: Session, kind: str = "HEARTBEAT", note: str = "") -> None:
    db.add(
        SchedulerHeartbeat(
            boot_id=BOOT_ID,
            jobs_count=len(scheduler.get_jobs()) if scheduler.running else 0,
            kind=kind,
            note=note[:300],
        )
    )
    db.commit()


def _scheduled_slot_key(rule_id: int, slot: datetime) -> str:
    return f"cron-{rule_id}-{slot.strftime('%Y%m%d%H%M')}"


def _run_cron_rule_job(rule_id: int, slot_iso: str | None = None) -> None:
    """Job body for real CRON automations. Idempotent per (rule, scheduled slot)."""
    db = SessionLocal()
    try:
        rule = db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
        if not rule or not rule.is_active:
            return
        slot = datetime.fromisoformat(slot_iso) if slot_iso else datetime.now(timezone.utc).replace(second=0, microsecond=0)
        execute_automation_rule(db, rule, idempotency_key=_scheduled_slot_key(rule.id, slot))
    except Exception as exc:
        logger.error("Cron job for rule %s crashed: %s", rule_id, exc)
    finally:
        db.close()


def _build_trigger(cron_expression: str):
    from apscheduler.triggers.cron import CronTrigger

    try:
        return CronTrigger.from_crontab(cron_expression, timezone=SCHEDULER_TZ)
    except Exception:
        return CronTrigger.from_crontab(cron_expression, timezone="UTC")


def sync_cron_jobs(db: Session) -> int:
    """Registers one real APScheduler cron job per active CRON AutomationRule (all tenants)."""
    count = 0
    rules = (
        db.query(AutomationRule)
        .filter(AutomationRule.trigger_type == "CRON", AutomationRule.is_active == True)  # noqa: E712
        .all()
    )
    wanted_ids = set()
    for r in rules:
        if not r.cron_expression:
            continue
        job_id = f"rule-{r.id}"
        wanted_ids.add(job_id)
        scheduler.add_job(
            _run_cron_rule_job,
            _build_trigger(r.cron_expression),
            args=[r.id],
            id=job_id,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            misfire_grace_time=3600,
        )
        count += 1
    for job in scheduler.get_jobs():
        if job.id.startswith("rule-") and job.id not in wanted_ids:
            scheduler.remove_job(job.id)
    return count


def recover_missed_runs(db: Session, lookback_hours: int = 36) -> list[dict[str, Any]]:
    """After a restart, runs CRON slots that should have fired while the app was down (idempotent)."""
    recovered: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=lookback_hours)
    rules = (
        db.query(AutomationRule)
        .filter(AutomationRule.trigger_type == "CRON", AutomationRule.is_active == True)  # noqa: E712
        .all()
    )
    for r in rules:
        if not r.cron_expression:
            continue
        trigger = _build_trigger(r.cron_expression)
        last_slot = None
        cursor = window_start
        for _ in range(500):
            nxt = trigger.get_next_fire_time(None, cursor)
            if not nxt or nxt > now:
                break
            last_slot = nxt
            cursor = nxt + timedelta(seconds=1)
        if last_slot is None:
            continue
        last_slot_utc = last_slot.astimezone(timezone.utc)
        last_run = r.last_run_at.replace(tzinfo=timezone.utc) if (r.last_run_at and r.last_run_at.tzinfo is None) else r.last_run_at
        if last_run and last_run >= last_slot_utc:
            continue
        key = _scheduled_slot_key(r.id, last_slot_utc)
        ex = execute_automation_rule(db, r, idempotency_key=key)
        recovered.append({"rule_id": r.id, "code_key": r.code_key, "slot": last_slot_utc.isoformat(), "status": ex.status})
    if recovered:
        _record_heartbeat(db, kind="CATCHUP", note=f"Recuperadas {len(recovered)} execucoes perdidas durante indisponibilidade")
    return recovered


def _periodic_scheduler_heartbeat() -> None:
    """Persists liveness evidence and keeps cron jobs synchronized with the database."""
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).all()
        for t in tenants:
            ensure_tenant_automations_seeded(db, t.id)
        sync_cron_jobs(db)
        _record_heartbeat(db, kind="HEARTBEAT", note="tick")
    except Exception as exc:
        logger.warning("Scheduler heartbeat warning: %s", exc)
    finally:
        db.close()


def _boot_recovery_task() -> None:
    db = SessionLocal()
    try:
        for t in db.query(Tenant).all():
            ensure_tenant_automations_seeded(db, t.id)
        jobs = sync_cron_jobs(db)
        _record_heartbeat(db, kind="BOOT", note=f"boot_id={BOOT_ID}; cron_jobs={jobs}")
        recover_missed_runs(db)
    except Exception as exc:
        logger.error("Boot recovery failed: %s", exc)
    finally:
        db.close()


def start_native_scheduler() -> dict[str, Any]:
    if not settings.SCHEDULER_ENABLED:
        return {"running": False, "reason": "DISABLED_BY_CONFIG"}
    if not scheduler.running:
        scheduler.add_job(
            _periodic_scheduler_heartbeat,
            "interval",
            minutes=15,
            id="union_growth_os_heartbeat",
            replace_existing=True,
        )
        scheduler.start()
        threading.Thread(target=_boot_recovery_task, name="ugos-boot-recovery", daemon=True).start()
    return {
        "running": scheduler.running,
        "jobs_count": len(scheduler.get_jobs()),
        "engine": "APScheduler Native Python (No n8n)",
        "boot_id": BOOT_ID,
    }


def get_scheduler_status() -> dict[str, Any]:
    return {
        "running": scheduler.running,
        "jobs_count": len(scheduler.get_jobs()) if scheduler.running else 0,
        "engine": "APScheduler Native Python (100% Internalized)",
        "boot_id": BOOT_ID,
        "timezone": SCHEDULER_TZ,
    }

