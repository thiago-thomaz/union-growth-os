"""
FASE 20 — AUDITORIA PROFUNDA DO AMBIENTE, ROTAS BACKEND vs FRONTEND, BANCO E PRODUÇÃO
Inspeciona:
1. Todas as rotas registradas no FastAPI (app.main:app)
2. Todas as chamadas apiFetch() e <a href=...> no frontend (frontend/src/app/page.tsx)
3. Cruzamento exato Frontend -> Backend (detecta rotas inexistentes, métodos incorretos ou links quebrados)
4. Teste de todos os endpoints GET em produção (https://automacao.projetosunion.cloud)
"""

import json
import re
import sys
from pathlib import Path

import httpx

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.api.routes import router  # noqa: E402


def audit_routes_and_frontend():
    backend_routes: dict[str, set[str]] = {}
    route_regexes: list[tuple[re.Pattern, str, set[str]]] = []

    for r in router.routes:
        path = getattr(r, "path", "")
        methods = set(getattr(r, "methods", set())) - {"HEAD", "OPTIONS"}
        if path and methods:
            backend_routes.setdefault(path, set()).update(methods)
            pattern_str = "^" + re.sub(r"\{[^\}]+\}", r"[^/]+", path) + "$"
            route_regexes.append((re.compile(pattern_str), path, methods))

    print(f"=== 1. ROTAS BACKEND REGISTRADAS: {len(backend_routes)} ===")

    tsx_path = ROOT_DIR / "frontend" / "src" / "app" / "page.tsx"
    tsx = tsx_path.read_text(encoding="utf-8")

    # Extrair todas as chamadas apiFetch("..." ou `...`, { method: "..." })
    fe_pattern = re.compile(
        r'apiFetch\(\s*[`"]([^`"]+)[`"]\s*(?:,\s*\{([^\}]*)\})?',
        re.DOTALL,
    )
    mismatches = []
    fe_calls_found = []

    for m in fe_pattern.finditer(tsx):
        raw_url = m.group(1)
        opts = m.group(2) or ""
        method_match = re.search(r'method:\s*["\']([A-Z]+)["\']', opts)
        method = method_match.group(1) if method_match else "GET"

        clean_path = raw_url.split("?")[0]
        test_path = re.sub(r"\$\{[^\}]+\}", "1", clean_path)
        fe_calls_found.append((method, raw_url, test_path))

        matched_route = None
        matched_methods: set[str] = set()
        for rx, r_path, r_methods in route_regexes:
            if rx.match(test_path):
                matched_route = r_path
                matched_methods |= r_methods

        if not matched_route:
            mismatches.append(f"[ROTA INEXISTENTE NO BACKEND] Frontend chama {method} {raw_url} (test_path={test_path})")
        elif method not in matched_methods:
            mismatches.append(
                f"[MÉTODO HTTP INCOMPATÍVEL] Frontend chama {method} {raw_url}, mas backend {matched_route} só aceita {sorted(matched_methods)}"
            )

    print(f"=== 2. CHAMADAS apiFetch NO FRONTEND: {len(fe_calls_found)} ===")
    for method, raw_url, _ in sorted(set(fe_calls_found)):
        print(f"  {method:6s} {raw_url}")

    print(f"\n=== 3. DISCREPÂNCIAS FRONTEND vs BACKEND: {len(mismatches)} ===")
    for mm in mismatches:
        print("  !", mm)

    # Verificar links <a href=...> no frontend
    hrefs = re.findall(r'href=\{?[`"\']?([^`"\'>\s\}]+)', tsx)
    print(f"\n=== 4. LINKS <a href> NO FRONTEND: {hrefs} ===")


def audit_production_endpoints():
    base = "https://automacao.projetosunion.cloud"
    alt = "https://uniongrowth.72.62.13.62.sslip.io"
    print("\n=== 5. AUDITORIA DE PRODUÇÃO AO VIVO ===")
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for name, url in [
            ("PROD /health", f"{base}/health"),
            ("PROD /ready", f"{base}/ready"),
            ("PROD /docs", f"{base}/docs"),
            ("PROD /robots.txt", f"{base}/robots.txt"),
            ("PROD /sitemap.xml", f"{base}/sitemap.xml"),
            ("ALT /health", f"{alt}/health"),
        ]:
            try:
                r = client.get(url)
                print(f"  {name:18s} -> HTTP {r.status_code} ({len(r.content)} bytes)")
            except Exception as e:
                print(f"  {name:18s} -> ERRO: {e}")

        # Login e teste de todos os GETs do dashboard
        rl = client.post(
            f"{base}/api/v1/auth/login",
            json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth#2026!"},
        )
        print(f"  LOGIN ADMIN        -> HTTP {rl.status_code}")
        if rl.status_code == 200:
            tok = rl.json()["access_token"]
            h = {"Authorization": f"Bearer {tok}"}
            get_endpoints = [
                "/api/v1/auth/me",
                "/api/v1/tenants",
                "/api/v1/dashboard/overview",
                "/api/v1/agents",
                "/api/v1/ceo/briefings",
                "/api/v1/ceo/goals",
                "/api/v1/ceo/daily-plan",
                "/api/v1/marketing/overview",
                "/api/v1/seo/overview",
                "/api/v1/social/calendar",
                "/api/v1/content-factory/items",
                "/api/v1/creative/assets",
                "/api/v1/copywriter/items",
                "/api/v1/growth/experiments",
                "/api/v1/crm/overview",
                "/api/v1/competitors",
                "/api/v1/finance/overview",
                "/api/v1/finance/multibusiness-summary",
                "/api/v1/customer-success/overview",
                "/api/v1/automations",
                "/api/v1/approvals",
                "/api/v1/reports/executive",
                "/api/v1/integrations",
                "/api/v1/audit-logs",
                "/api/v1/system/operational-dashboard",
                "/api/v1/system/alerts",
                "/api/v1/system/resource-costs",
                "/api/v1/pilot/history",
                "/api/v1/commercial/multibusiness-dashboard",
                "/api/v1/commercial/phase18-1-executive-panel",
                "/api/v1/commercial/services",
                "/api/v1/commercial/offers",
                "/api/v1/commercial/market-opportunities",
                "/api/v1/commercial/landing-pages",
                "/api/v1/commercial/proposals",
                "/api/v1/commercial/payments",
                "/api/v1/commercial/delivery-projects",
                "/api/v1/agency/clients",
                "/api/v1/partners/programs",
                "/api/v1/partners/products",
                "/api/v1/ai-engine-hub/overview",
            ]
            for ep in get_endpoints:
                r = client.get(f"{base}{ep}", headers=h)
                status_label = "OK" if r.status_code == 200 else f"FAIL ({r.text[:120]})"
                print(f"  GET {ep:45s} -> HTTP {r.status_code} {status_label}")


if __name__ == "__main__":
    audit_routes_and_frontend()
    audit_production_endpoints()
