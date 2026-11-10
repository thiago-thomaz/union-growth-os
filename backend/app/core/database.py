import hashlib
import json
import logging
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

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


def run_automatic_schema_migrations(engine_instance=None):
    """
    Executa migrações DDL seguras e idempotentes para garantir compatibilidade
    regressiva entre versões sem perda de dados na VPS (Fase 15).
    """
    eng = engine_instance or engine
    dialect_name = eng.dialect.name
    migrations = [
        ("agent_execution_logs", "model_used", "VARCHAR(100) DEFAULT 'rule-based-v1'"),
        ("agent_execution_logs", "processing_type", "VARCHAR(50) DEFAULT 'DETERMINISTIC_PYTHON_ENGINE'"),
        ("agent_execution_logs", "tokens_consumed", "INTEGER DEFAULT 0"),
        ("agent_execution_logs", "estimated_cost_brl", "FLOAT DEFAULT 0.0"),
        ("content_factory_items", "responsible_agent", "VARCHAR(80) DEFAULT 'AGENT_04_SOCIAL'"),
        ("content_factory_items", "change_history_json", "TEXT DEFAULT '[]'"),
    ]

    with eng.connect() as conn:
        for table, col, col_def in migrations:
            try:
                if dialect_name == "postgresql":
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_def};"))
                    conn.commit()
                elif dialect_name == "sqlite":
                    pragma = conn.execute(text(f"PRAGMA table_info({table});")).fetchall()
                    existing_cols = {row[1] for row in pragma}
                    if col not in existing_cols:
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_def};"))
            except Exception as e:
                logger.debug("Migração idempotente para %s.%s ignorada: %s", table, col, e)


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
        ContentFactoryItem,
        CEODelegatedTask,
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
            "content_factory_items": _serialize_rows(ContentFactoryItem),
            "ceo_delegated_tasks": _serialize_rows(CEODelegatedTask),
            "integrations_count": len(_serialize_rows(IntegrationConnection)),
        },
    }

    raw_json = json.dumps(payload, ensure_ascii=False, indent=2)
    backup_file.write_text(raw_json, encoding="utf-8")
    computed_sha256 = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

    if ACTIVE_DB_URL.startswith("sqlite:///"):
        sqlite_path = Path(ACTIVE_DB_URL.replace("sqlite:///", ""))
        if sqlite_path.exists():
            shutil.copy2(sqlite_path, backup_dir / f"sqlite_snapshot_{ts}.db")

    return {
        "backup_file": backup_file.name,
        "path": str(backup_file),
        "size_bytes": backup_file.stat().st_size,
        "sha256": computed_sha256,
        "created_at": payload["metadata"]["created_at"],
        "tenant_id": tenant_id,
    }


def verify_backup_integrity(backup_path: str | Path) -> dict[str, Any]:
    """Valida integridade estrutural, parse JSON e contagem de tabelas de um arquivo de backup."""
    path = Path(backup_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de backup não encontrado: {path}")

    raw = path.read_text(encoding="utf-8")
    sha256 = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    try:
        data = json.loads(raw)
    except Exception as exc:
        return {"valid": False, "error": f"JSON inválido ou corrompido: {exc}", "sha256": sha256}

    meta = data.get("metadata", {})
    tables = data.get("data", {})
    if not isinstance(tables, dict):
        return {"valid": False, "error": "Chave 'data' ausente ou inválida no backup", "sha256": sha256}

    total_records = 0
    table_counts: dict[str, int] = {}
    for tname, items in tables.items():
        if isinstance(items, list):
            c = len(items)
            table_counts[tname] = c
            total_records += c
        elif isinstance(items, int):
            table_counts[tname] = items

    return {
        "valid": True,
        "backup_file": path.name,
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256,
        "created_at": meta.get("created_at"),
        "version": meta.get("version"),
        "tenant_id": meta.get("tenant_id"),
        "engine_source": meta.get("engine"),
        "total_records": total_records,
        "table_counts": table_counts,
    }


def restore_database_from_backup(
    backup_path: str | Path,
    target_engine_url: str | None = None,
    allow_production_overwrite: bool = False,
) -> dict[str, Any]:
    """
    Restaura os dados do backup em um banco de dados isolado (ou no banco de destino especificado).
    Garante proteção estrita: impede restauração acidental sobre o banco de produção em execução
    a menos que allow_production_overwrite=True seja explicitamente informado.
    """
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
        ContentFactoryItem,
        CEODelegatedTask,
    )

    path = Path(backup_path)
    integrity = verify_backup_integrity(path)
    if not integrity.get("valid"):
        raise ValueError(f"Backup corrompido ou inválido: {integrity.get('error')}")

    target_url = target_engine_url or "sqlite:///:memory:"

    # Trava de segurança para proteção do banco de produção
    if target_url == ACTIVE_DB_URL and not allow_production_overwrite:
        raise ValueError(
            "Segurança Ativa: Restauração direta sobre o banco de produção ativo bloqueada por segurança. "
            "Para testes, utilize um banco isolado ou sqlite:///:memory:."
        )

    # Criar engine isolada
    if target_url.startswith("sqlite"):
        test_engine = create_engine(target_url, connect_args={"check_same_thread": False})
    else:
        test_engine = create_engine(target_url)

    # Criar todas as tabelas no banco de destino
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSession()

    restored_counts: dict[str, int] = {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))["data"]

        model_map = [
            ("tenants", Tenant),
            ("strategic_goals", StrategicGoal),
            ("ceo_briefings", CEODailyBriefing),
            ("marketing_campaigns", MarketingCampaign),
            ("seo_audits", SEOAuditReport),
            ("seo_articles", SEOArticle),
            ("editorial_calendar", EditorialCalendarItem),
            ("creative_assets", CreativeAsset),
            ("copy_items", CopyItem),
            ("growth_experiments", GrowthExperiment),
            ("crm_leads", CRMLead),
            ("crm_deals", CRMDeal),
            ("competitors", Competitor),
            ("financial_records", FinancialRecord),
            ("customer_feedbacks", CustomerFeedback),
            ("automation_rules", AutomationRule),
            ("content_factory_items", ContentFactoryItem),
            ("ceo_delegated_tasks", CEODelegatedTask),
        ]

        for key, model_cls in model_map:
            rows = data.get(key, [])
            restored = 0
            for r in rows:
                row_dict = dict(r)
                # Converter strings ISO em datetimes para colunas DateTime
                for col in model_cls.__table__.columns:
                    cname = col.name
                    if cname in row_dict and isinstance(row_dict[cname], str) and ("datetime" in str(col.type).lower() or "date" in str(col.type).lower()):
                        try:
                            row_dict[cname] = datetime.fromisoformat(row_dict[cname].replace("Z", "+00:00"))
                        except Exception:
                            row_dict[cname] = None
                instance = model_cls(**{k: v for k, v in row_dict.items() if hasattr(model_cls, k)})
                session.merge(instance)
                restored += 1
            session.commit()
            restored_counts[key] = restored

        return {
            "status": "RESTORE_SUCCESS",
            "target_engine": target_url.split("@")[-1] if "@" in target_url else target_url,
            "backup_file": path.name,
            "sha256_verified": integrity["sha256"],
            "restored_tables": restored_counts,
            "total_restored_records": sum(restored_counts.values()),
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        session.close()


def enforce_backup_retention(retention_days: int = 30, min_backups_kept: int = 5) -> list[str]:
    """Exclui backups mais antigos que retention_days, preservando no mínimo min_backups_kept."""
    backup_dir = Path(settings.BACKUP_DIR)
    if not backup_dir.exists():
        return []

    files = sorted(list(backup_dir.glob("backup_*.json")), key=lambda p: p.stat().st_mtime, reverse=True)
    if len(files) <= min_backups_kept:
        return []

    cutoff = time.time() - (retention_days * 86400)
    purged = []
    # Manter os min_backups_kept mais recentes incondicionalmente
    for f in files[min_backups_kept:]:
        if f.stat().st_mtime < cutoff:
            f.unlink(missing_ok=True)
            purged.append(f.name)
    return purged


