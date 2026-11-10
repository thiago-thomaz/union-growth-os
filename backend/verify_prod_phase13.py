import httpx
import json
import sys
from pathlib import Path

base = "https://uniongrowth.72.62.13.62.sslip.io"
admin_email = "admin@projetosunion.cloud"

secret_file = Path("data/admin_prod_initial.secret.txt")
if not secret_file.exists():
    print("Secret file missing!")
    sys.exit(1)

initial_pwd = secret_file.read_text(encoding="utf-8").strip()

with httpx.Client(timeout=30.0, follow_redirects=True) as client:
    print("=== 1. HEALTH & READINESS ===")
    h = client.get(f"{base}/health")
    print("HEALTH:", h.status_code, h.json())
    rdy = client.get(f"{base}/ready")
    print("READY:", rdy.status_code, rdy.json()["ready"])

    print("=== 2. ROBOTS.TXT & SITEMAP.XML ===")
    rob = client.get(f"{base}/robots.txt")
    print("ROBOTS:", rob.status_code, rob.text[:120].strip())
    sit = client.get(f"{base}/sitemap.xml")
    print("SITEMAP:", sit.status_code, sit.text[:120].strip())

    print("=== 3. OLD DEFAULT PASSWORD REJECTION ===")
    old_l = client.post(f"{base}/api/v1/auth/login", json={"email": admin_email, "password": "UnionGrowth@2026"})
    print("OLD DEFAULT LOGIN STATUS:", old_l.status_code, "(401 EXPECTED)")
    assert old_l.status_code == 401

    print("=== 4. INITIAL STRONG PASSWORD LOGIN & ROTATION ===")
    new_perm_pwd = initial_pwd + "#Rotated2026!"
    l_perm = client.post(f"{base}/api/v1/auth/login", json={"email": admin_email, "password": new_perm_pwd})
    if l_perm.status_code == 200:
        print("ALREADY ROTATED. LOGIN OK. must_change_password:", l_perm.json()["must_change_password"])
        token = l_perm.json()["access_token"]
    else:
        l_init = client.post(f"{base}/api/v1/auth/login", json={"email": admin_email, "password": initial_pwd})
        print("INITIAL LOGIN STATUS:", l_init.status_code, "must_change_password:", l_init.json().get("must_change_password"))
        assert l_init.status_code == 200
        init_token = l_init.json()["access_token"]
        rot = client.post(
            f"{base}/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {init_token}"},
            json={"current_password": initial_pwd, "new_password": new_perm_pwd},
        )
        print("PASSWORD ROTATION STATUS:", rot.status_code, rot.json())
        assert rot.status_code == 200
        l_after = client.post(f"{base}/api/v1/auth/login", json={"email": admin_email, "password": new_perm_pwd})
        assert l_after.status_code == 200
        token = l_after.json()["access_token"]
        print("LOGIN WITH ROTATED PASSWORD OK. must_change_password:", l_after.json()["must_change_password"])

    headers = {"Authorization": f"Bearer {token}"}

    print("=== 5. SECURITY SELF AUDIT ===")
    sec = client.get(f"{base}/api/v1/security/audit", headers=headers)
    print("SECURITY AUDIT:", sec.status_code, sec.json())

    print("=== 6. AGENTS AI AUDIT (ETAPA 3) ===")
    ai = client.get(f"{base}/api/v1/agents/audit", headers=headers)
    print("AGENTS AUDIT STATUS:", ai.status_code)
    print("AI VERDICT:", ai.json()["verdict"])
    sample = ai.json()["agents"][0]
    print("SAMPLE AGENT 01 (CEO):", sample["base_origin"], "| rules:", sample["deterministic_rules"][:80])

    print("=== 7. SOCIAL PLATFORMS AUDIT (ETAPA 5) ===")
    soc = client.get(f"{base}/api/v1/social/platforms-audit", headers=headers)
    print("SOCIAL AUDIT STATUS:", soc.status_code, "TOTAL PLATFORMS:", soc.json()["total_social_platforms"])
    for p in soc.json()["platforms"]:
        print(f"  - {p['platform']}: status={p['connection_status']}, funcionando={len(p['status_matrix']['FUNCIONANDO'])} recursos")

    print("=== 8. ONBOARDING FIRST OPERATIONAL COMPANY (ETAPA 8) ===")
    onb_payload = {
        "name": "TecnoAgro Soluções Inteligentes Ltda",
        "segment": "Agrotech & Máquinas Agrícolas B2B",
        "description": "Plataforma de telemetria e gestão de frotas agrícolas para produtores de grãos.",
        "products": ["Sensor de Telemetria AgroIoT Pro", "Software de Gestão SafraMax"],
        "services": ["Instalação e Calibração em Campo", "Consultoria de Eficiência Operacional"],
        "target_audience": "Produtores rurais médios e grandes (acima de 1.500 hectares) no Centro-Oeste",
        "region": "Mato Grosso e Goiás",
        "competitors": [{"name": "AgroMonitor Brasil", "website_url": "https://example.com"}],
        "visual_identity": {
            "brand_name": "TecnoAgro",
            "primary_color": "#059669",
            "secondary_color": "#D97706",
            "tone_of_voice": "Consultivo, Técnico e de Campo",
        },
        "website": "https://example.com",
        "social_networks": {"linkedin": "https://linkedin.com/company/tecnoagro", "instagram": "https://instagram.com/tecnoagro"},
        "commercial_goals": [
            {"title": "Alcançar 50 fazendas conectadas no Q1", "metric_name": "Fazendas Conectadas", "target_value": 50, "unit": "UN", "period": "QUARTERLY"},
            {"title": "Atingir R$ 120.000 MRR em telemetria", "metric_name": "MRR Telemetria", "target_value": 120000, "unit": "BRL", "period": "MONTHLY"},
        ],
        "create_new_tenant": True,
    }
    onb = client.post(f"{base}/api/v1/onboarding/company", headers=headers, json=onb_payload)
    print("ONBOARDING STATUS:", onb.status_code)
    onb_data = onb.json()
    new_tid = onb_data["tenant_id"]
    print("NEW TENANT ID:", new_tid, "SLUG:", onb_data["tenant_slug"])
    print("METAS CRIADAS (ORIGEM GOAL):", len(onb_data["metas"]))
    print("CAMPANHAS INICIAIS (ORIGEM GOAL/PLANNED):", len(onb_data["primeiras_campanhas"]))
    print("CALENDÁRIO CRIADO:", len(onb_data["calendario_redes_sociais"]))
    print("LACUNAS HONESTAS:", onb_data["lacunas_de_informacao"])

    print("=== 9. FULL 10-STEP MARKETING PIPELINE (ETAPA 4) ===")
    pipe_headers = {"Authorization": f"Bearer {token}", "X-Tenant-Id": str(new_tid)}
    pipe_payload = {
        "campaign_name": "Safra Eficiente 2027: Telemetria e Redução de Diesel",
        "product_or_offer": "Sensor AgroIoT Pro",
        "target_keyword": "telemetria de máquinas agrícolas",
        "platforms": ["instagram", "linkedin", "blog"],
        "budget_planned_brl": 1500.0,
        "auto_approve_execution": False,
    }
    pipe = client.post(f"{base}/api/v1/marketing/full-operation-pipeline", headers=pipe_headers, json=pipe_payload)
    print("PIPELINE STATUS:", pipe.status_code)
    pipe_data = pipe.json()
    print("STEPS COMPLETED COUNT:", len(pipe_data["steps"]))
    for s in pipe_data["steps"]:
        print(f"  Passo {s['step']}: [{s['agent']}] {s['title']} -> {s['status']} (origem: {s['response_origin'][:45]})")
    print("PIPELINE SUMMARY:", pipe_data["summary"])

    print("=== 10. VERIFY ALL 12 AUTOMATIONS 24/7 (ETAPA 7) ===")
    ver = client.post(f"{base}/api/v1/automations/verify-operation", headers=pipe_headers)
    print("AUTOMATIONS VERIFY STATUS:", ver.status_code)
    v_data = ver.json()
    print("TOTAL RULES:", v_data["total_rules"], "ALL SUCCEEDED:", v_data["all_succeeded"], "ALL IDEMPOTENT:", v_data["all_idempotent"])
    print("RETRY TEST:", v_data["retry_test"])
    print("SCHEDULER STATUS:", v_data["scheduler"])

    print("=== 11. 24H OPERATIONAL LOG (ETAPA 7) ===")
    op = client.get(f"{base}/api/v1/automations/operational-log?hours=24", headers=pipe_headers)
    print("OPERATIONAL LOG STATUS:", op.status_code)
    print("HEARTBEATS COUNT:", op.json()["heartbeats"], "DUPLICATE SUCCESS:", op.json()["duplicate_success_executions"])

    print("=== 12. AUTONOMY PANEL & LIMITS (ETAPA 9) ===")
    pan = client.get(f"{base}/api/v1/autonomy/panel", headers=pipe_headers)
    print("AUTONOMY PANEL STATUS:", pan.status_code)
    print("AGENTS COUNT:", len(pan.json()["agents"]), "PENDING TASKS:", len(pan.json()["pending_tasks"]))
    print("POLICY:", pan.json()["policy"])

