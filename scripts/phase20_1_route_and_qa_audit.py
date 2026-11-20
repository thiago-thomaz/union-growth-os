"""
FASE 20.1 — Auditoria Independente de Cobertura Real de Todas as Rotas da API,
Segurança (Auth/RBAC/Multi-Tenant), e Isolamento de Dados em Produção.
"""
import inspect
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
AUDIT_DB = ROOT_DIR / "data" / "phase20_1_route_audit.db"
if AUDIT_DB.exists():
    AUDIT_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{AUDIT_DB.as_posix()}"
os.environ["SCHEDULER_ENABLED"] = "false"
os.environ["RATE_LIMIT_PER_MINUTE"] = "2000"
sys.path.insert(0, str(ROOT_DIR / "backend"))

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.api.routes import router as api_v1_router
from app.main import app

EVIDENCE_DIR = ROOT_DIR / "UNION_GROWTH_OS_PHASE20_1_EVIDENCE"
for sub in ("routes", "security", "e2e", "ai_engine", "frontend", "performance", "qa_data", "deployment"):
    (EVIDENCE_DIR / sub).mkdir(parents=True, exist_ok=True)


INTENTIONALLY_PUBLIC_PATHS = {
    "/health",
    "/ready",
    "/robots.txt",
    "/sitemap.xml",
    "/lp/{slug}",
    "/{full_path:path}",
    "/api/{full_path:path}",
    "/",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/integrations/oauth/callback",
    "/api/v1/public/landing-pages/{slug}/capture",
    "/api/v1/affiliates/redirect/{tracking_code}",
    "/api/v1/commercial/payments/webhook",
}


def inspect_all_routes() -> list[dict[str, Any]]:
    routes_info = []
    seen_method_path = {}
    duplicates = []

    raw_routes = list(app.routes) + list(api_v1_router.routes)
    for r in raw_routes:
        if not isinstance(r, APIRoute):
            continue
        path = r.path
        methods = sorted(set(r.methods or set()) - {"HEAD", "OPTIONS"})
        endpoint = r.endpoint
        func_name = endpoint.__name__
        try:
            src = inspect.getsource(endpoint)
        except Exception:
            src = ""

        # Inspect dependencies recursively
        dep_names = set()
        def _collect_deps(dependant):
            if dependant.call is not None:
                dep_names.add(getattr(dependant.call, "__name__", str(dependant.call)))
            for sub in getattr(dependant, "dependencies", []):
                _collect_deps(sub)

        _collect_deps(r.dependant)
        has_auth = ("get_current_user" in dep_names) or ("_checker" in dep_names)
        has_rbac = "_checker" in dep_names
        uses_tenant = ("get_active_tenant_id" in src) or ("tenant_id" in src)
        uses_db = "get_db" in dep_names or "SessionLocal" in src
        has_body_schema = len(r.dependant.body_params) > 0
        is_api = path.startswith("/api/")

        for m in methods:
            key = f"{m} {path}"
            if key in seen_method_path:
                duplicates.append({"route": key, "first": seen_method_path[key], "duplicate": func_name})
            else:
                seen_method_path[key] = func_name

            routes_info.append({
                "method": m,
                "path": path,
                "function": func_name,
                "is_api": is_api,
                "intentionally_public": path in INTENTIONALLY_PUBLIC_PATHS,
                "has_auth": has_auth,
                "has_rbac": has_rbac,
                "uses_tenant": uses_tenant,
                "uses_db": uses_db,
                "has_body_schema": has_body_schema,
                "dependencies": sorted(dep_names),
            })

    return routes_info, duplicates


def test_every_route_independently():
    routes_info, duplicates = inspect_all_routes()
    api_routes = [r for r in routes_info if r["is_api"]]

    unauth_findings = []
    for r in api_routes:
        if not r["has_auth"] and not r["intentionally_public"]:
            unauth_findings.append(r)

    results = []
    with TestClient(app) as client:
        # Login as admin
        r_login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth#2026!"},
        )
        assert r_login.status_code == 200, f"Login failed: {r_login.text}"
        token = r_login.json()["access_token"]
        auth_h = {"Authorization": f"Bearer {token}"}
        cross_h = {"Authorization": f"Bearer {token}", "X-Tenant-Id": "999999"}

        # Test every API route
        for r in api_routes:
            method = r["method"]
            path = r["path"]
            # Substitute path params with safe test IDs
            concrete_path = re.sub(r"\{[^\}]+\}", "1", path)
            concrete_path = concrete_path.replace("/lp/1", "/lp/agentes-ia")
            if "{slug}" in path:
                concrete_path = path.replace("{slug}", "agentes-ia")
            if "{agent_id}" in path:
                concrete_path = path.replace("{agent_id}", "AGENT_01_CEO")
            if "{platform}" in path:
                concrete_path = path.replace("{platform}", "instagram")
            if "{tracking_code}" in path:
                concrete_path = path.replace("{tracking_code}", "nonexistent-code")
            if "{backup_filename}" in path:
                concrete_path = path.replace("{backup_filename}", "nonexistent.db")

            entry = {
                "method": method,
                "path": path,
                "concrete_path": concrete_path,
                "function": r["function"],
                "has_auth": r["has_auth"],
                "has_rbac": r["has_rbac"],
                "uses_tenant": r["uses_tenant"],
                "has_body_schema": r["has_body_schema"],
                "unauth_status": None,
                "cross_tenant_status": None,
                "auth_smoke_status": None,
                "verdict": "PASS",
                "issues": [],
            }

            # 1. Unauthenticated check on protected routes
            if r["has_auth"]:
                req_kwargs = {"json": {}} if method in ("POST", "PUT", "PATCH") else {}
                resp_unauth = client.request(method, concrete_path, **req_kwargs)
                entry["unauth_status"] = resp_unauth.status_code
                if resp_unauth.status_code != 401:
                    entry["issues"].append(f"Expected 401 without auth, got {resp_unauth.status_code}")

                # 2. Cross-tenant isolation check (X-Tenant-Id: 999999)
                resp_cross = client.request(method, concrete_path, headers=cross_h, **req_kwargs)
                entry["cross_tenant_status"] = resp_cross.status_code
                if resp_cross.status_code != 403:
                    entry["issues"].append(f"Expected 403 on cross-tenant X-Tenant-Id:999999, got {resp_cross.status_code}")

            # 3. Authenticated functional/validation check
            if method == "GET":
                resp_ok = client.get(concrete_path, headers=auth_h)
                entry["auth_smoke_status"] = resp_ok.status_code
                if resp_ok.status_code >= 500:
                    entry["issues"].append(f"Server error HTTP {resp_ok.status_code}: {resp_ok.text[:200]}")
            else:
                # Avoid destructive mutation on backup restore / lgpd erasure / delete in generic smoke
                if any(kw in path for kw in ("restore", "erasure", "change-password", "register")):
                    entry["auth_smoke_status"] = "SKIPPED_DESTRUCTIVE_TESTED_IN_SUITE"
                else:
                    resp_val = client.request(method, concrete_path, headers=auth_h, json={})
                    entry["auth_smoke_status"] = resp_val.status_code
                    if resp_val.status_code >= 500:
                        entry["issues"].append(f"Server error HTTP {resp_val.status_code}: {resp_val.text[:200]}")

            if entry["issues"]:
                entry["verdict"] = "FAIL"
            results.append(entry)

    report = {
        "total_app_routes": len(routes_info),
        "total_api_method_routes": len(api_routes),
        "unique_api_paths": len({r["path"] for r in api_routes}),
        "duplicates": duplicates,
        "unexpected_unauthenticated_api_routes": unauth_findings,
        "routes_passed": sum(1 for x in results if x["verdict"] == "PASS"),
        "routes_failed": sum(1 for x in results if x["verdict"] == "FAIL"),
        "failed_details": [x for x in results if x["verdict"] == "FAIL"],
        "all_routes": results,
    }
    out = EVIDENCE_DIR / "routes" / "independent_route_coverage.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "all_routes"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_every_route_independently()
