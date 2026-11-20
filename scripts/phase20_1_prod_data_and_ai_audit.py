"""
FASE 20.1 — Auditoria Independente de Dados de QA em Produção, Isolamento Multi-Tenant,
AI Engine Hub (Gemini & FREE_ONLY) e Latência Real (Cold vs Warm Keep-Alive).
Somente leitura + 1 teste controlado do Gemini (sem esgotar cota).
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import httpx

ROOT_DIR = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = ROOT_DIR / "UNION_GROWTH_OS_PHASE20_1_EVIDENCE"
for sub in ("qa_data", "ai_engine", "performance", "deployment"):
    (EVIDENCE_DIR / sub).mkdir(parents=True, exist_ok=True)

PROD_URL = "https://automacao.projetosunion.cloud"
ALT_URL = "https://uniongrowth.72.62.13.62.sslip.io"
ADMIN_EMAIL = "admin@projetosunion.cloud"
ADMIN_PASS = "UnionGrowth#2026!"


def run_audit():
    with httpx.Client(timeout=35.0, verify=True) as client:
        # 1. Production Health, Readiness & Commit Sync Check
        h_prod = client.get(f"{PROD_URL}/health").json()
        r_prod = client.get(f"{PROD_URL}/ready").json()
        h_alt = client.get(f"{ALT_URL}/health").json()

        r_login = client.post(
            f"{PROD_URL}/api/v1/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASS},
        )
        assert r_login.status_code == 200
        token = r_login.json()["access_token"]
        auth_h = {"Authorization": f"Bearer {token}"}

        # 2. Audit ALL Tenants & QA Data Contamination Check
        tenants = client.get(f"{PROD_URL}/api/v1/tenants", headers=auth_h).json()
        tenant_audit = []
        for t in tenants:
            tid = t["id"]
            th = {**auth_h, "X-Tenant-Id": str(tid)}
            ov = client.get(f"{PROD_URL}/api/v1/dashboard/overview", headers=th).json()
            fin_panel = client.get(f"{PROD_URL}/api/v1/commercial/phase18-1-executive-panel", headers=th).json()
            crm = client.get(f"{PROD_URL}/api/v1/crm/overview", headers=th).json()
            autos = client.get(f"{PROD_URL}/api/v1/automations", headers=th).json()
            active_cron = sum(1 for a in autos.get("rules", []) if a.get("trigger_type") == "CRON" and a.get("is_active"))
            tenant_audit.append({
                "tenant_id": tid,
                "name": t.get("name"),
                "brand_name": t.get("brand_name"),
                "leads_count": len(crm.get("leads", [])),
                "qa_leads_inside_this_tenant": [
                    {"id": l["id"], "email": l["email"], "data_origin": l.get("data_origin")}
                    for l in crm.get("leads", [])
                    if any(k in (l.get("email") or "").lower() for k in ("qa", "teste", "e2e", "xss", "ciclo", "helena"))
                    or l.get("data_origin") in ("TEST", "SIMULATION", "DEMO")
                ],
                "real_confirmed_revenue_brl": fin_panel.get("REAL", {}).get("receita_recebida_confirmada_brl"),
                "sandbox_charges_total": fin_panel.get("SIMULACAO", {}).get("cobrancas_sandbox_total"),
                "active_cron_rules": active_cron,
                "metrics_cards": ov.get("metrics_cards"),
            })

        qa_data_report = {
            "audited_at_utc": datetime.now(timezone.utc).isoformat(),
            "prod_git_commit": h_prod.get("git_commit"),
            "alt_git_commit": h_alt.get("git_commit"),
            "scheduler_status": h_prod.get("scheduler"),
            "tenants_count": len(tenants),
            "tenants": tenant_audit,
        }
        (EVIDENCE_DIR / "qa_data" / "production_tenants_and_isolation_audit.json").write_text(
            json.dumps(qa_data_report, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # 3. Audit UNION AI ENGINE HUB & Controlled Gemini Check (1 single call, no quota burn)
        ai_ov = client.get(f"{PROD_URL}/api/v1/ai-engine-hub/overview", headers=auth_h).json()
        # Test FREE_ONLY blocking PAID and UNKNOWN_COST models
        r_blk_paid_openai = client.post(
            f"{PROD_URL}/api/v1/ai-engine-hub/route-execute",
            headers=auth_h,
            json={
                "task_type": "copywriting",
                "required_capability": "text_generation",
                "preferred_provider": "openai",
                "preferred_model": "gpt-4o",
                "prompt": "Auditoria FREE_ONLY bloqueio OpenAI PAID",
            },
        ).json()
        r_blk_paid_claude = client.post(
            f"{PROD_URL}/api/v1/ai-engine-hub/route-execute",
            headers=auth_h,
            json={
                "task_type": "copywriting",
                "required_capability": "text_generation",
                "preferred_provider": "anthropic",
                "preferred_model": "claude-3-7-sonnet-latest",
                "prompt": "Auditoria FREE_ONLY bloqueio Anthropic PAID",
            },
        ).json()
        r_blk_paid_imagen = client.post(
            f"{PROD_URL}/api/v1/ai-engine-hub/image-studio/generate",
            headers=auth_h,
            json={"prompt": "Banner pago Imagen 3", "operation_mode": "GENERATE_IMAGE"},
        ).json()
        r_blk_paid_veo = client.post(
            f"{PROD_URL}/api/v1/ai-engine-hub/video-studio/generate",
            headers=auth_h,
            json={"prompt": "Video pago Veo 2", "target_stage": "DIRECT_VIDEO_GENERATION"},
        ).json()
        r_blk_unknown = client.post(
            f"{PROD_URL}/api/v1/ai-engine-hub/route-execute",
            headers=auth_h,
            json={
                "task_type": "copywriting",
                "required_capability": "text_generation",
                "preferred_provider": "openai_compatible",
                "preferred_model": "custom-openai-compatible-model",
                "prompt": "Auditoria FREE_ONLY bloqueio UNKNOWN_COST",
            },
        ).json()

        # Controlled 1-call Gemini connection test + 1-call generation test
        r_gem_conn = client.post(
            f"{PROD_URL}/api/v1/ai-engine-hub/test-connection",
            headers=auth_h,
            json={"provider_key": "gemini", "model_id": "gemini-3.5-flash-lite"},
        ).json()
        r_gem_gen = client.post(
            f"{PROD_URL}/api/v1/ai-engine-hub/route-execute",
            headers=auth_h,
            json={
                "task_type": "copywriting",
                "required_capability": "text_generation",
                "preferred_provider": "gemini",
                "preferred_model": "gemini-2.5-flash",
                "prompt": "Responda apenas: OK_AUDITORIA_20_1",
            },
        ).json()

        ai_report = {
            "audited_at_utc": datetime.now(timezone.utc).isoformat(),
            "operation_mode": ai_ov.get("configuration", {}).get("operation_mode"),
            "default_provider": ai_ov.get("configuration", {}).get("default_provider"),
            "default_model": ai_ov.get("configuration", {}).get("default_model"),
            "providers_summary": [
                {
                    "provider_key": p["provider_key"],
                    "status": p.get("status"),
                    "cost_classification": p.get("cost_classification"),
                    "credential_configured": p.get("credential_configured"),
                    "credential_masked": p.get("credential_masked"),
                }
                for p in ai_ov.get("providers", [])
            ],
            "free_only_enforcement_tests": {
                "openai_gpt4o_paid": {"ok": r_blk_paid_openai.get("ok"), "status": r_blk_paid_openai.get("status"), "error": r_blk_paid_openai.get("error_message")},
                "anthropic_claude_paid": {"ok": r_blk_paid_claude.get("ok"), "status": r_blk_paid_claude.get("status"), "error": r_blk_paid_claude.get("error_message")},
                "google_imagen3_paid": {"ok": r_blk_paid_imagen.get("ok"), "status": r_blk_paid_imagen.get("status"), "error": r_blk_paid_imagen.get("error_message")},
                "google_veo2_paid": {"ok": r_blk_paid_veo.get("ok"), "status": r_blk_paid_veo.get("status"), "error": r_blk_paid_veo.get("error_message")},
                "generic_unknown_cost": {"ok": r_blk_unknown.get("ok"), "status": r_blk_unknown.get("status"), "error": r_blk_unknown.get("error_message")},
            },
            "gemini_controlled_live_check": {
                "test_connection_ok": r_gem_conn.get("ok"),
                "test_connection_status": r_gem_conn.get("status"),
                "test_connection_latency_ms": r_gem_conn.get("latency_ms"),
                "models_discovered_count": len(r_gem_conn.get("models_discovered", [])),
                "generation_ok": r_gem_gen.get("ok"),
                "generation_status": r_gem_gen.get("status"),
                "generation_error": r_gem_gen.get("error_message"),
                "executed_model": r_gem_gen.get("executed_model"),
                "estimated_cost_brl": r_gem_gen.get("estimated_cost_brl"),
            },
        }
        (EVIDENCE_DIR / "ai_engine" / "ai_engine_hub_independent_audit.json").write_text(
            json.dumps(ai_report, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # 4. Controlled Warm Keep-Alive Latency Benchmark (reusing TLS connection to measure true API/DB speed vs cold TLS)
        endpoints = [
            ("/health", {}),
            ("/ready", {}),
            ("/lp/agentes-ia", {}),
            ("/api/v1/dashboard/overview", auth_h),
            ("/api/v1/ai-engine-hub/overview", auth_h),
            ("/api/v1/commercial/multibusiness-dashboard?unit=ALL", auth_h),
            ("/api/v1/system/pilot-7-days", auth_h),
        ]
        warm_samples = []
        for path, hdrs in endpoints:
            times = []
            status_code = 0
            for _ in range(3):
                t0 = time.perf_counter()
                resp = client.get(f"{PROD_URL}{path}", headers=hdrs)
                dt = round((time.perf_counter() - t0) * 1000.0, 2)
                status_code = resp.status_code
                times.append(dt)
            warm_samples.append({
                "endpoint": path,
                "status": status_code,
                "samples_ms": times,
                "avg_ms": round(sum(times) / len(times), 2),
                "min_ms": min(times),
                "max_ms": max(times),
            })

        perf_out = {
            "audited_at_utc": datetime.now(timezone.utc).isoformat(),
            "connection_mode": "HTTP/1.1 Keep-Alive (Warm TLS session)",
            "endpoints": warm_samples,
        }
        (EVIDENCE_DIR / "performance" / "warm_latency_benchmark.json").write_text(
            json.dumps(perf_out, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        print("QA DATA TENANTS:", len(tenant_audit))
        for ta in tenant_audit:
            print(f"  Tenant {ta['tenant_id']} ({ta['name']}): leads={ta['leads_count']}, qa_leads={len(ta['qa_leads_inside_this_tenant'])}, real_rev={ta['real_confirmed_revenue_brl']}, sandbox={ta['sandbox_charges_total']}, active_cron={ta['active_cron_rules']}")
        print("AI ENGINE HUB:", json.dumps(ai_report["free_only_enforcement_tests"], ensure_ascii=False))
        print("GEMINI LIVE:", json.dumps(ai_report["gemini_controlled_live_check"], ensure_ascii=False))
        print("WARM LATENCY:", json.dumps([(x["endpoint"], x["avg_ms"]) for x in warm_samples], ensure_ascii=False))


if __name__ == "__main__":
    run_audit()
