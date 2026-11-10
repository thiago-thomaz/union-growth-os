import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger("union_growth_os.database")


class Base(DeclarativeBase):
    pass


def _build_engine():
    db_url = settings.normalized_database_url
    try:
        if db_url.startswith("sqlite"):
            engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                pool_pre_ping=True,
            )
        else:
            engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                connect_args={"connect_timeout": 5},
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        return engine, db_url, False
    except Exception as exc:
        logger.warning(
            "Primary database (%s) unreachable (%s). Activating automatic SQLite fallback.",
            db_url.split("@")[-1] if "@" in db_url else db_url,
            exc,
        )
        fallback_engine = create_engine(
            settings.FALLBACK_SQLITE_URL,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
        return fallback_engine, settings.FALLBACK_SQLITE_URL, True


engine, ACTIVE_DB_URL, IS_FALLBACK_DB = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_health() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        backend_type = "sqlite" if ACTIVE_DB_URL.startswith("sqlite") else "postgresql"
        return {
            "status": "healthy",
            "engine": backend_type,
            "is_fallback": IS_FALLBACK_DB,
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "error": str(exc),
            "is_fallback": IS_FALLBACK_DB,
        }


def create_database_backup(db: Session, tenant_id: int | None = None) -> dict:
    """Create a portable JSON + SQLite file backup of tenant or system data."""
    from app.models.entities import (
        Tenant,
        User,
        StrategicGoal,
        CEODailyBriefing,
        MarketingCampaign,
        SEOAuditReport,
        SEOArticle,
        EditorialCalendarItem,
        CreativeAsset,
        CopyItem,
        GrowthExperiment,
        CRMLead,
        CRMDeal,
        Competitor,
        FinancialRecord,
        CustomerFeedback,
        AutomationRule,
        IntegrationConnection,
    )

    backup_dir = Path(settings.BACKUP_DIR)
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    suffix = f"tenant_{tenant_id}" if tenant_id else "full"
    backup_file = backup_dir / f"backup_{suffix}_{ts}.json"

    def _serialize_rows(model_cls):
        q = db.query(model_cls)
        if tenant_id is not None and hasattr(model_cls, "tenant_id"):
            q = q.filter(model_cls.tenant_id == tenant_id)
        elif tenant_id is not None and model_cls is Tenant:
            q = q.filter(Tenant.id == tenant_id)
        rows = []
        for obj in q.all():
            item = {}
            for col in obj.__table__.columns:
                val = getattr(obj, col.name)
                if isinstance(val, datetime):
                    val = val.isoformat()
                item[col.name] = val
            rows.append(item)
        return rows

    payload = {
        "metadata": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": settings.APP_VERSION,
            "tenant_id": tenant_id,
            "engine": "sqlite" if ACTIVE_DB_URL.startswith("sqlite") else "postgresql",
        },
        "data": {
            "tenants": _serialize_rows(Tenant),
            "users_count": len(_serialize_rows(User)),
            "strategic_goals": _serialize_rows(StrategicGoal),
            "ceo_briefings": _serialize_rows(CEODailyBriefing),
            "marketing_campaigns": _serialize_rows(MarketingCampaign),
            "seo_audits": _serialize_rows(SEOAuditReport),
            "seo_articles": _serialize_rows(SEOArticle),
            "editorial_calendar": _serialize_rows(EditorialCalendarItem),
            "creative_assets": _serialize_rows(CreativeAsset),
            "copy_items": _serialize_rows(CopyItem),
            "growth_experiments": _serialize_rows(GrowthExperiment),
            "crm_leads": _serialize_rows(CRMLead),
            "crm_deals": _serialize_rows(CRMDeal),
            "competitors": _serialize_rows(Competitor),
            "financial_records": _serialize_rows(FinancialRecord),
            "customer_feedbacks": _serialize_rows(CustomerFeedback),
            "automation_rules": _serialize_rows(AutomationRule),
            "integrations_count": len(_serialize_rows(IntegrationConnection)),
        },
    }

    backup_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if ACTIVE_DB_URL.startswith("sqlite:///"):
        sqlite_path = Path(ACTIVE_DB_URL.replace("sqlite:///", ""))
        if sqlite_path.exists():
            shutil.copy2(sqlite_path, backup_dir / f"sqlite_snapshot_{ts}.db")

    return {
        "backup_file": backup_file.name,
        "path": str(backup_file),
        "size_bytes": backup_file.stat().st_size,
        "created_at": payload["metadata"]["created_at"],
        "tenant_id": tenant_id,
    }

