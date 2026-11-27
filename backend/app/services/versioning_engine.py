"""UNION GROWTH OS — FASE 27: SEMANTIC VERSIONING & PERSISTENT RELEASE HISTORY ENGINE"""

from __future__ import annotations

import json
import os
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import load_release_manifest, settings
from app.core.database import check_db_health
from app.models.entities import ReleaseRecord, SystemAuditSnapshot
from app.services.automation_scheduler import get_scheduler_status


def sync_release_records_service(db: Session) -> dict[str, Any]:
    """Sincroniza releases do release_manifest.json para a tabela PostgreSQL `release_records`."""
    manifest = load_release_manifest()
    releases = manifest.get("releases", []) or []
    source_commit = os.getenv("SOURCE_COMMIT", "local")
    env_name = settings.ENVIRONMENT

    synced = 0
    for rel in releases:
        ver = str(rel.get("version") or "").strip()
        if not ver:
            continue
        existing = db.query(ReleaseRecord).filter(ReleaseRecord.version == ver).first()
        commit_val = source_commit if ver == manifest.get("current_version") and source_commit not in ("", "local", "unknown") else str(rel.get("commit_sha") or "")
        if existing:
            if commit_val and not existing.commit_sha:
                existing.commit_sha = commit_val
            existing.title = str(rel.get("title") or existing.title)
            existing.features_json = json.dumps(rel.get("features", []), ensure_ascii=False)
            existing.fixes_json = json.dumps(rel.get("fixes", []), ensure_ascii=False)
            existing.security_json = json.dumps(rel.get("security_improvements", []), ensure_ascii=False)
            existing.tests_summary = str(rel.get("tests_summary") or existing.tests_summary)
            existing.environment = env_name if ver == manifest.get("current_version") else str(rel.get("environment_default", "production"))
        else:
            rec = ReleaseRecord(
                version=ver,
                git_tag=str(rel.get("git_tag") or f"v{ver}"),
                release_date=str(rel.get("release_date") or ""),
                phase_label=str(rel.get("phase") or ""),
                commit_sha=commit_val,
                environment=env_name if ver == manifest.get("current_version") else str(rel.get("environment_default", "production")),
                deploy_status=str(rel.get("deploy_status") or "PUBLISHED"),
                title=str(rel.get("title") or f"Release v{ver}"),
                features_json=json.dumps(rel.get("features", []), ensure_ascii=False),
                fixes_json=json.dumps(rel.get("fixes", []), ensure_ascii=False),
                security_json=json.dumps(rel.get("security_improvements", []), ensure_ascii=False),
                tests_summary=str(rel.get("tests_summary") or ""),
                readiness_status="PRODUCTION_READY",
            )
            db.add(rec)
        synced += 1
    db.commit()
    return {"synced_count": synced, "current_version": settings.APP_VERSION}


def _parse_semver(ver: str) -> dict[str, int]:
    parts = [int(p) for p in ver.lstrip("v").split(".") if p.isdigit()]
    while len(parts) < 3:
        parts.append(0)
    return {"major": parts[0], "minor": parts[1], "patch": parts[2]}


def get_system_version_payload(db: Session) -> dict[str, Any]:
    """Payload consumido pelo cabeçalho global do frontend e monitoramento externo."""
    manifest = load_release_manifest()
    db_info = check_db_health()
    sched = get_scheduler_status()
    git_commit = os.getenv("SOURCE_COMMIT", "local")
    short_commit = git_commit[:8] if git_commit not in ("", "local", "unknown") else git_commit
    latest_audit = db.query(SystemAuditSnapshot).order_by(SystemAuditSnapshot.id.desc()).first()
    releases_count = db.query(ReleaseRecord).count()

    is_healthy = db_info.get("status") == "healthy" and bool(sched.get("running"))
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "semver": manifest.get("semver") or _parse_semver(settings.APP_VERSION),
        "git_tag": manifest.get("git_tag") or f"v{settings.APP_VERSION}",
        "phase": manifest.get("phase") or "FASE 27",
        "release_channel": manifest.get("release_channel", "STABLE"),
        "environment": settings.ENVIRONMENT,
        "environment_label": "PRODUCTION" if settings.ENVIRONMENT.lower() == "production" else "DEVELOPMENT",
        "platform_state": "STABLE" if is_healthy else "DEGRADED",
        "git_commit": git_commit,
        "short_commit": short_commit,
        "health": {
            "healthy": is_healthy,
            "database": db_info,
            "scheduler_jobs": sched.get("jobs_count", 0),
        },
        "latest_audit_score": latest_audit.global_score if latest_audit else None,
        "latest_readiness_status": latest_audit.readiness_status if latest_audit else "PENDING_AUDIT",
        "releases_count": releases_count,
        "source": "release_manifest.json + Git Tag + SOURCE_COMMIT + PostgreSQL",
    }


def list_releases_history_payload(db: Session) -> dict[str, Any]:
    """Retorna histórico completo de releases persistido no PostgreSQL."""
    rows = db.query(ReleaseRecord).order_by(ReleaseRecord.id.desc()).all()
    if not rows:
        sync_release_records_service(db)
        rows = db.query(ReleaseRecord).order_by(ReleaseRecord.id.desc()).all()

    items: list[dict[str, Any]] = []
    for r in rows:
        items.append(
            {
                "id": r.id,
                "version": r.version,
                "semver": _parse_semver(r.version),
                "git_tag": r.git_tag,
                "release_date": r.release_date,
                "phase": r.phase_label,
                "commit_sha": r.commit_sha or ("active" if r.version == settings.APP_VERSION else ""),
                "environment": r.environment,
                "deploy_status": r.deploy_status,
                "title": r.title,
                "features": json.loads(r.features_json or "[]"),
                "fixes": json.loads(r.fixes_json or "[]"),
                "security_improvements": json.loads(r.security_json or "[]"),
                "tests_summary": r.tests_summary,
                "audit_score": r.audit_score,
                "readiness_status": r.readiness_status,
            }
        )

    # Sort descending by SemVer tuple so latest version is always on top
    items.sort(key=lambda x: (x["semver"]["major"], x["semver"]["minor"], x["semver"]["patch"]), reverse=True)
    return {
        "current_version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "total_releases": len(items),
        "releases": items,
    }
