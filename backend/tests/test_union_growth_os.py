import os
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import tempfile

_TMP_DB = Path(tempfile.mkdtemp(prefix="ugos_test_")) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB.as_posix()}"
os.environ["ADMIN_INITIAL_PASSWORD"] = "Init#Admin2026Test!"
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app

RUN_SUFFIX = uuid.uuid4().hex[:6]


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_01_health_and_readiness_endpoints(client: TestClient):
    r_health = client.get("/health")
    assert r_health.status_code == 200
    data = r_health.json()
    assert data["status"] == "ok"
    assert data["database"]["status"] == "healthy"
    assert data["scheduler"]["running"] is True
    assert r_health.headers.get("X-Content-Type-Options") == "nosniff"

    r_ready = client.get("/ready")
    assert r_ready.status_code == 200
    assert r_ready.json()["ready"] is True


ADMIN_EMAIL = "admin@projetosunion.cloud"
ADMIN_INITIAL = "Init#Admin2026Test!"
ADMIN_NEW = "Rotated#Admin2026Strong!"


def admin_token(client: TestClient) -> str:
    """Logs in as admin; completes the mandatory password rotation when required."""
    r = client.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_NEW})
    if r.status_code == 200:
        return r.json()["access_token"]
    r = client.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_INITIAL})
    assert r.status_code == 200, "admin initial password should be valid before rotation"
    tok = r.json()["access_token"]
    assert r.json()["must_change_password"] is True
    rc = client.post(
        "/api/v1/auth/change-password",
        headers=_auth_headers(tok),
        json={"current_password": ADMIN_INITIAL, "new_password": ADMIN_NEW},
    )
    assert rc.status_code == 200
    r2 = client.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_NEW})
    assert r2.status_code == 200
    return r2.json()["access_token"]


def test_02a_old_default_password_is_invalidated_and_rotation_enforced(client: TestClient):
    r_old = client.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": "UnionGrowth@2026"})
    assert r_old.status_code == 401
    weak = client.post(
        "/api/v1/auth/register",
        json={"email": f"weak_{RUN_SUFFIX}@x.com.br", "password": "UnionGrowth@2026", "full_name": "W", "company_name": "W Ltda"},
    )
    assert weak.status_code == 400
    weak2 = client.post(
        "/api/v1/auth/register",
        json={"email": f"weak2_{RUN_SUFFIX}@x.com.br", "password": "senhafraca1", "full_name": "W", "company_name": "W Ltda"},
    )
    assert weak2.status_code == 400
    # Fresh DB only: must_change_password blocks other endpoints until rotated.
    r_init = client.post("/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_INITIAL})
    if r_init.status_code == 200:
        blocked = client.get("/api/v1/dashboard/overview", headers=_auth_headers(r_init.json()["access_token"]))
        assert blocked.status_code == 403
        assert "PASSWORD_CHANGE_REQUIRED" in blocked.json()["detail"]


def test_02_default_seed_login_and_dashboard(client: TestClient):
    token = admin_token(client)

    r_dash = client.get("/api/v1/dashboard/overview", headers=_auth_headers(token))
    assert r_dash.status_code == 200
    dash = r_dash.json()
    assert len(dash["metrics_cards"]) == 8
    assert dash["ceo_briefing"]["headline"] != ""


def test_03_register_and_multitenant_strict_isolation(client: TestClient):
    # Register Company A
    r_a = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"ceoa_{RUN_SUFFIX}@empresaa.com.br",
            "password": "PasswordA@123456",
            "full_name": "CEO Empresa A",
            "company_name": f"Empresa Alpha {RUN_SUFFIX} Ltda",
            "brand_name": "Alpha Growth",
            "niche": "Fintech B2B",
            "lgpd_consent": True,
        },
    )
    assert r_a.status_code == 201
    token_a = r_a.json()["access_token"]
    tenant_a_id = r_a.json()["tenant"]["id"]

    # Register Company B
    r_b = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"ceob_{RUN_SUFFIX}@empresab.com.br",
            "password": "PasswordB@123456",
            "full_name": "CEO Empresa B",
            "company_name": f"Empresa Beta {RUN_SUFFIX} S/A",
            "brand_name": "Beta Corp",
            "niche": "Healthtech",
            "lgpd_consent": True,
        },
    )
    assert r_b.status_code == 201
    token_b = r_b.json()["access_token"]
    tenant_b_id = r_b.json()["tenant"]["id"]
    assert tenant_a_id != tenant_b_id

    # Create a secret lead in Company A
    secret_email = f"exclusivo_{RUN_SUFFIX}@alphaclient.com.br"
    r_lead_a = client.post(
        "/api/v1/crm/leads",
        headers=_auth_headers(token_a),
        json={
            "full_name": "Lead Exclusivo Alpha",
            "email": secret_email,
            "phone": "+5511999990000",
            "company_name": "Alpha Client",
            "buy_intent": "URGENT",
            "estimated_value": 50000.0,
            "consent_lgpd": True,
        },
    )
    assert r_lead_a.status_code == 201

    # Verify Company B cannot see Company A's lead
    r_crm_b = client.get("/api/v1/crm/overview", headers=_auth_headers(token_b))
    assert r_crm_b.status_code == 200
    emails_in_b = [l["email"] for l in r_crm_b.json()["leads"]]
    assert secret_email not in emails_in_b


def test_04_ceo_briefing_and_strategic_goals(client: TestClient):
    token = admin_token(client)

    r_goal = client.post(
        "/api/v1/ceo/goals",
        headers=_auth_headers(token),
        json={
            "title": "Expandir Receita Trimestral",
            "period": "QUARTERLY",
            "metric_name": "Receita Trimestral",
            "target_value": 300000.0,
            "current_value": 95000.0,
            "unit": "BRL",
            "data_origin": "GOAL",
            "financial_impact_score": 95.0,
            "priority": "CRITICAL",
        },
    )
    assert r_goal.status_code == 201
    assert r_goal.json()["data_origin"] == "GOAL"

    r_gen = client.post("/api/v1/ceo/briefings/generate", headers=_auth_headers(token))
    assert r_gen.status_code == 201
    assert len(r_gen.json()["recommendations"]) >= 1


def test_05_seo_audit_keywords_and_content_factory(client: TestClient):
    token = admin_token(client)

    r_kw = client.post(
        "/api/v1/seo/keywords",
        headers=_auth_headers(token),
        json={"seed_keyword": "plataforma de automação de marketing"},
    )
    assert r_kw.status_code == 201
    assert len(r_kw.json()["long_tail_keywords"]) >= 4

    r_art = client.post(
        "/api/v1/seo/articles/generate",
        headers=_auth_headers(token),
        json={
            "topic": "Guia Definitivo de Automação Comercial B2B",
            "target_keyword": "automação comercial b2b",
            "search_intent": "COMMERCIAL",
        },
    )
    assert r_art.status_code == 201
    assert r_art.json()["word_count"] > 150

    r_seo = client.get("/api/v1/seo/overview", headers=_auth_headers(token))
    assert r_seo.status_code == 200
    assert r_seo.json()["gsc_ranking_status"]["connected"] is False


def test_06_creative_studio_and_copywriter_ab_testing(client: TestClient):
    token = admin_token(client)

    r_asset = client.post(
        "/api/v1/creative/assets/generate",
        headers=_auth_headers(token),
        json={
            "title": "Carrossel de Lançamento",
            "asset_type": "CAROUSEL",
            "platform": "instagram",
            "headline_text": "Como Reduzir o CAC em 40% com IA",
            "subheadline_text": "Método prático validado",
            "cta_text": "Baixar Guia",
        },
    )
    assert r_asset.status_code == 201
    asset_data = r_asset.json()
    assert asset_data["preview_data_uri"].startswith("data:image/png;base64,")
    assert "slides" in asset_data["content"]

    r_copy = client.post(
        "/api/v1/copywriter/generate",
        headers=_auth_headers(token),
        json={
            "title": "Copy Anúncio Meta & LinkedIn",
            "copy_type": "AD_COPY",
            "framework": "PAS",
            "product_or_offer": "Union Growth OS",
            "target_audience": "Diretores Comerciais",
            "key_benefit": "qualificar leads 24/7 sem equipe manual",
        },
    )
    assert r_copy.status_code == 201
    copy_data = r_copy.json()
    assert copy_data["variant_a"] != copy_data["variant_b"]
    assert copy_data["compliance_verified"] is True


def test_07_social_editorial_calendar_and_approval_flow(client: TestClient):
    token = admin_token(client)

    r_cal = client.post(
        "/api/v1/social/calendar",
        headers=_auth_headers(token),
        json={
            "title": "Post LinkedIn: Governança de Dados",
            "platform": "linkedin",
            "content_format": "POST",
            "caption": "Como estruturar governança e crescimento previsível no B2B.",
            "hashtags": ["#b2b", "#governanca", "#crescimento"],
            "scheduled_for": "2026-11-15 08:30",
        },
    )
    assert r_cal.status_code == 201
    assert r_cal.json()["publish_check"]["status"] == "PENDING_REVIEW"


def test_08_crm_lgpd_enforcement_pipeline_and_finance(client: TestClient):
    token = admin_token(client)

    # Reject lead without LGPD consent
    r_bad = client.post(
        "/api/v1/crm/leads",
        headers=_auth_headers(token),
        json={
            "full_name": "Contato Sem Consentimento",
            "email": "semconsentimento@teste.com",
            "consent_lgpd": False,
        },
    )
    assert r_bad.status_code == 400

    # Create valid lead & deal
    r_lead = client.post(
        "/api/v1/crm/leads",
        headers=_auth_headers(token),
        json={
            "full_name": "Mariana Albuquerque",
            "email": "mariana@albuquerqueholding.com.br",
            "phone": "+5511988887777",
            "company_name": "Albuquerque Holding",
            "buy_intent": "URGENT",
            "estimated_value": 45000.0,
            "consent_lgpd": True,
        },
    )
    assert r_lead.status_code == 201
    assert r_lead.json()["lead_score"] >= 75

    r_fin = client.post(
        "/api/v1/finance/records",
        headers=_auth_headers(token),
        json={
            "period_date": "2026-11-10",
            "record_type": "REVENUE",
            "category": "Novo Contrato",
            "channel": "CRM Direct",
            "amount": 15000.0,
            "data_origin": "REAL",
            "description": "Receita real de novo contrato fechado",
        },
    )
    assert r_fin.status_code == 201
    assert r_fin.json()["updated_kpis"]["real_revenue"] >= 15000.0


def test_09_automations_retry_backoff_and_idempotency(client: TestClient):
    token = admin_token(client)

    r_list = client.get("/api/v1/automations", headers=_auth_headers(token))
    assert r_list.status_code == 200
    rules = r_list.json()["rules"]
    assert len(rules) >= 12

    rule_id = rules[0]["id"]
    # Test automatic retry with backoff when transient failure happens on attempt 1
    r_run = client.post(
        f"/api/v1/automations/{rule_id}/run",
        headers=_auth_headers(token),
        json={"idempotency_key": f"test-retry-idem-{RUN_SUFFIX}", "simulate_transient_failure": True},
    )
    assert r_run.status_code == 200
    run_data = r_run.json()
    assert run_data["status"] == "RETRIED"
    assert run_data["attempt_number"] == 2


def test_10_orchestrator_inter_agent_diagnosis_and_integrations_and_backup(client: TestClient):
    token = admin_token(client)

    r_diag = client.post(
        "/api/v1/orchestrator/diagnose",
        headers=_auth_headers(token),
        json={"reason": "Teste Automatizado de Diagnóstico Multiagente"},
    )
    assert r_diag.status_code == 200
    diag = r_diag.json()
    assert len(diag["specialist_diagnostics"]) == 6
    assert diag["ceo_consolidation"]["status"] == "COMPLETED"

    r_int = client.get("/api/v1/integrations", headers=_auth_headers(token))
    assert r_int.status_code == 200
    assert len(r_int.json()) == 18

    r_bkp = client.post("/api/v1/system/backup", headers=_auth_headers(token))
    assert r_bkp.status_code == 201
    assert r_bkp.json()["size_bytes"] > 100


def test_11_competitor_intelligence_growth_and_customer_success(client: TestClient):
    token = admin_token(client)

    r_comp = client.post(
        "/api/v1/competitors",
        headers=_auth_headers(token),
        json={"name": "Concorrente Teste Público", "website_url": "https://example.com", "category": "SaaS"},
    )
    assert r_comp.status_code == 201
    assert r_comp.json()["robots_txt_respected"] is True

    r_exp = client.post(
        "/api/v1/growth/experiments",
        headers=_auth_headers(token),
        json={
            "title": "Experimento CTA Direto WhatsApp",
            "channel": "Landing Page",
            "hypothesis": "Botão flutuante com diagnóstico rápido aumenta leads em 20%",
            "objective": "Mais conversões",
            "indicator_metric": "Taxa de Conversão (%)",
            "impact": 9,
            "confidence": 8,
            "ease": 9,
        },
    )
    assert r_exp.status_code == 201
    exp_id = r_exp.json()["id"]
    assert r_exp.json()["data_origin"] == "ESTIMATED"

    r_exp_res = client.put(
        f"/api/v1/growth/experiments/{exp_id}/result",
        headers=_auth_headers(token),
        json={
            "real_result_conversion_pct": 5.4,
            "real_result_summary": "Aumento confirmado em produção",
            "conclusion": "Implementar definitivamente",
            "status": "COMPLETED",
        },
    )
    assert r_exp_res.status_code == 200
    assert r_exp_res.json()["data_origin"] == "REAL"

    r_cs = client.post(
        "/api/v1/customer-success/feedbacks",
        headers=_auth_headers(token),
        json={
            "customer_name": "Cliente Em Risco Ltda",
            "customer_email": "contato@clienterisco.com.br",
            "nps_score": 4,
            "csat_score": 2,
            "feedback_text": "Precisamos de apoio na configuração inicial das integrações.",
        },
    )
    assert r_cs.status_code == 201
    assert r_cs.json()["churn_risk"] == "HIGH"


def test_12_security_xss_sanitization_and_high_impact_approval_gate(client: TestClient):
    token = admin_token(client)

    # XSS payload sanitization test
    r_persona = client.post(
        "/api/v1/marketing/personas",
        headers=_auth_headers(token),
        json={
            "name": "Persona <script>alert('xss')</script> Segura",
            "role_segment": "CMO",
            "value_proposition": "javascript:alert(1) Crescimento Limpo",
        },
    )
    assert r_persona.status_code == 201
    assert "<script>" not in r_persona.json()["name"]

    # High-impact financial action gate test (budget > 10,000 without confirmation token)
    r_camp = client.post(
        "/api/v1/marketing/campaigns",
        headers=_auth_headers(token),
        json={
            "name": "Campanha Paga Alto Orçamento",
            "campaign_type": "ACQUISITION",
            "channel": "Google Ads",
            "objective": "Escala nacional",
            "budget_planned": 25000.0,
            "spend_real": 5000.0,
        },
    )
    assert r_camp.status_code == 201
    assert r_camp.json()["status"] == "PENDING_HIGH_IMPACT_APPROVAL"
    req_id = r_camp.json()["approval_request_id"]

    # Approve high-impact request
    r_decide = client.post(
        f"/api/v1/approvals/{req_id}/decide",
        headers=_auth_headers(token),
        json={"decision": "APPROVE", "confirmation_token": client.get("/api/v1/auth/me", headers=_auth_headers(token)).json()["high_impact_confirmation_token"]},
    )
    assert r_decide.status_code == 200
    assert r_decide.json()["status"] == "EXECUTED"


def test_13_frontend_static_ui_served(client: TestClient):
    r_home = client.get("/")
    assert r_home.status_code == 200
    assert "UNION GROWTH OS" in r_home.text






# ===================== FASE 13 =====================
def test_14_agents_audit_is_honest_about_llm(client: TestClient):
    token = admin_token(client)
    r = client.get("/api/v1/agents/audit", headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert len(data["agents"]) == 11
    assert all(a["limitations"] for a in data["agents"])
    # Without any LLM configured, no agent may claim to use a real LLM.
    if not data["provider_status"]["llm_active"]:
        assert all(a["uses_real_llm_now"] is False for a in data["agents"])
        assert "NENHUM agente usa LLM real" in data["verdict"]
    assert "usage_today" in data


def test_15_agent_response_origin_is_tracked(client: TestClient):
    token = admin_token(client)
    r = client.post("/api/v1/agents/AGENT_10_FINANCE/execute", headers=_auth_headers(token), json={})
    assert r.status_code == 200
    body = r.json()
    assert body["response_origin"].startswith("DETERMINISTIC_PYTHON_ENGINE")
    assert body["llm_used"] is False


def test_16_social_platforms_audit_classification(client: TestClient):
    token = admin_token(client)
    r = client.get("/api/v1/social/platforms-audit", headers=_auth_headers(token))
    assert r.status_code == 200
    plats = {p["platform"]: p for p in r.json()["platforms"]}
    assert set(plats) == {"instagram", "facebook", "tiktok", "youtube", "linkedin", "pinterest"}
    for p in plats.values():
        assert set(p["status_matrix"]) == {"FUNCIONANDO", "AGUARDANDO_CREDENCIAIS", "AGUARDANDO_APROVACAO_PLATAFORMA", "BLOQUEADO_LIMITACAO_TECNICA"}
        assert p["connection_status"] != "CONNECTED"  # no credentials were provided in tests


def test_17_oauth_start_requires_app_credentials(client: TestClient):
    token = admin_token(client)
    r = client.get("/api/v1/integrations/oauth/instagram/start", headers=_auth_headers(token))
    assert r.status_code == 200
    assert r.json()["status"] == "AGUARDANDO_CREDENCIAIS"
    bad = client.get("/api/v1/integrations/oauth/callback", params={"code": "x", "state": "invalid"})
    assert bad.status_code == 200 and "inválido" in bad.text


def test_18_sitemap_and_robots_dynamic(client: TestClient):
    r = client.get("/robots.txt")
    assert r.status_code == 200 and "Sitemap:" in r.text
    s = client.get("/sitemap.xml")
    assert s.status_code == 200 and "<urlset" in s.text


def test_19_onboarding_wizard_does_not_invent_data(client: TestClient):
    token = admin_token(client)
    r = client.post(
        "/api/v1/onboarding/company",
        headers=_auth_headers(token),
        json={
            "name": f"Padaria Teste {RUN_SUFFIX}",
            "segment": "Padaria artesanal",
            "description": "Padaria de bairro com pães de fermentação natural.",
            "products": ["Pão de fermentação natural"],
            "services": ["Encomendas para eventos"],
            "target_audience": "Moradores do bairro e escritórios próximos",
            "region": "Campinas-SP",
            "create_new_tenant": True,
        },
    )
    assert r.status_code == 201
    d = r.json()
    assert d["metas"] == []  # no goals informed => none invented
    assert any("Site não informado" in g for g in d["lacunas_de_informacao"])
    assert any("Metas comerciais não informadas" in g for g in d["lacunas_de_informacao"])
    assert d["plano_de_seo"]["volume_de_busca"].startswith("NÃO DISPONÍVEL")
    assert len(d["primeiras_campanhas"]) == 2
    assert d["diagnostico_empresarial"]["presenca_digital"]["site"] == "NÃO INFORMADO"


def test_20_autonomy_limits_and_financial_always_requires_approval(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)
    r = client.put(
        "/api/v1/autonomy/limits",
        headers=h,
        json={
            "autonomy_default_level": 3,
            "agent_autonomy": {"AGENT_04_SOCIAL": 3},
            "limits": {"max_daily_publications": 2, "require_approval_for_financial_actions": False},
        },
    )
    assert r.status_code == 200
    assert r.json()["limits"]["require_approval_for_financial_actions"] is True  # immutable
    panel = client.get("/api/v1/autonomy/panel", headers=h)
    assert panel.status_code == 200
    assert len(panel.json()["agents"]) == 11
    # restore safe defaults
    client.put("/api/v1/autonomy/limits", headers=h, json={"autonomy_default_level": 2, "agent_autonomy": {}, "limits": {}})


def test_21_full_marketing_pipeline_10_steps(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)
    r = client.post(
        "/api/v1/marketing/full-operation-pipeline",
        headers=h,
        json={"campaign_name": f"Campanha E2E {RUN_SUFFIX}", "target_keyword": "automação de marketing", "platforms": ["instagram", "blog"], "budget_planned_brl": 1000.0},
    )
    assert r.status_code == 201
    d = r.json()
    assert [s["step"] for s in d["steps"]] == list(range(1, 11))
    step2 = d["steps"][1]["detail"]
    assert "PENDENTE de aprovação" in step2["verba"]  # money never spent autonomously
    step9 = d["steps"][8]["detail"]
    # Instagram has no credentials => must not be published.
    assert all(p["platform"] != "instagram" for p in step9["publicadas"])
    assert "NÃO DISPONÍVEL" in d["steps"][9]["detail"]["metricas_de_engajamento"]


def test_22_verify_automations_idempotency_and_scheduler(client: TestClient):
    token = admin_token(client)
    r = client.post("/api/v1/automations/verify-operation", headers=_auth_headers(token))
    assert r.status_code == 200
    d = r.json()
    assert d["total_rules"] >= 12
    assert d["all_idempotent"] is True
    assert d["retry_test"]["status"] == "RETRIED"
    cron_rows = [x for x in d["rules"] if x["trigger"] == "CRON"]
    assert len(cron_rows) >= 8
    log = client.get("/api/v1/automations/operational-log", headers=_auth_headers(token))
    assert log.status_code == 200
    assert log.json()["duplicate_success_executions"] == 0


def test_23_security_audit_endpoint_does_not_leak_secrets(client: TestClient):
    token = admin_token(client)
    r = client.get("/api/v1/security/audit", headers=_auth_headers(token))
    assert r.status_code == 200
    assert r.json()["users_with_invalidated_default_password_still_valid"] == 0
    assert "*" not in r.json()["cors_allowed_origins"]
    assert ADMIN_NEW not in r.text and ADMIN_INITIAL not in r.text


def test_24_login_bruteforce_is_rate_limited(client: TestClient):
    codes = [
        client.post("/api/v1/auth/login", json={"email": f"nobody_{RUN_SUFFIX}@x.com", "password": "wrong-password-1A!"}).status_code
        for _ in range(10)
    ]
    assert 429 in codes


# ===================== FASE 14 =====================
def test_25_content_factory_generate_batch_and_assisted_export(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Gerar lote de 30 publicações na Content Factory
    r_batch = client.post(
        "/api/v1/content-factory/generate-batch",
        headers=h,
        json={"company_name": "AgroSaaS Tech", "niche": "Tecnologia Agrícola", "count": 30},
    )
    assert r_batch.status_code == 201
    batch = r_batch.json()
    assert batch["total_generated"] == 30
    assert batch["average_quality_score"] >= 80.0
    assert set(batch["items_by_channel"].keys()) >= {"instagram", "facebook", "tiktok", "youtube", "linkedin", "blog_seo", "email_marketing"}

    # 2. Listar itens com filtro
    r_items = client.get("/api/v1/content-factory/items?channel=instagram", headers=h)
    assert r_items.status_code == 200
    ig_items = r_items.json()
    assert len(ig_items) >= 6
    sample_id = ig_items[0]["id"]

    # 3. Exportar pacote de 1 clique para publicação assistida
    r_export = client.get(f"/api/v1/content-factory/assisted-export/{sample_id}", headers=h)
    assert r_export.status_code == 200
    pkg = r_export.json()
    assert "formatted_copy_for_clipboard" in pkg
    assert len(pkg["checklist"]) == 5
    assert "platform_upload_url" in pkg

    # 4. Atualizar status de publicação
    r_pub = client.post(f"/api/v1/content-factory/items/{sample_id}/publish", headers=h)
    assert r_pub.status_code == 200
    assert r_pub.json()["status"] == "PUBLISHED"


def test_26_ceo_daily_plan_delegation_and_task_execution(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Obter plano diário de execução do CEO
    r_plan = client.get("/api/v1/ceo/daily-plan", headers=h)
    assert r_plan.status_code == 200
    plan = r_plan.json()
    assert plan["total_tasks"] == 8
    target_agents = {t["target_agent"] for t in plan["tasks"]}
    assert target_agents >= {"AGENT_02_CMO", "AGENT_03_SEO", "AGENT_04_SOCIAL", "AGENT_05_CREATIVE", "AGENT_06_COPY", "AGENT_07_GROWTH", "AGENT_08_SALES", "AGENT_09_FINANCE"}

    # 2. Atualizar status de uma missão delegada
    task_id = plan["tasks"][0]["id"]
    r_upd = client.put(
        f"/api/v1/ceo/daily-plan/tasks/{task_id}",
        headers=h,
        json={"status": "COMPLETED", "deliverable": "Estratégia executada com sucesso no teste."},
    )
    assert r_upd.status_code == 200
    assert r_upd.json()["status"] == "COMPLETED"


def test_27_weekly_seo_routine_core_web_vitals(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    r_seo = client.post("/api/v1/seo/weekly-report", headers=h)
    assert r_seo.status_code == 201
    seo = r_seo.json()
    assert seo["audit_score"] >= 90
    assert seo["core_web_vitals"]["overall_grade"] == "GOOD"
    assert seo["schema_org_valid"] is True
    assert "ONLINE" in seo["sitemap_status"]


def test_28_system_operational_dashboard_alerts_and_pilot_7_days(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Painel Operacional 24/7
    r_dash = client.get("/api/v1/system/operational-dashboard", headers=h)
    assert r_dash.status_code == 200
    dash = r_dash.json()
    assert dash["vps_status"]["status"] == "HEALTHY"
    assert dash["scheduler_status"]["running"] is True
    assert len(dash["daily_routines_status"]) == 10

    # 2. Alertas Inteligentes do Sistema
    r_alerts = client.get("/api/v1/system/alerts", headers=h)
    assert r_alerts.status_code == 200
    alerts = r_alerts.json()
    assert len(alerts) >= 1
    first_alert_id = alerts[0]["id"]

    r_res = client.post(f"/api/v1/system/alerts/{first_alert_id}/resolve", headers=h)
    assert r_res.status_code == 200
    assert r_res.json()["is_resolved"] is True

    # 3. Piloto Operacional Autônomo de 7 Dias
    r_pilot = client.post("/api/v1/system/pilot-7-days", headers=h)
    assert r_pilot.status_code == 201
    pilot = r_pilot.json()
    assert pilot["days_simulated"] == 7
    assert pilot["total_content_pieces_produced"] >= 30
    assert pilot["total_leads_qualified"] >= 10
    assert pilot["zero_unexpected_costs"] is True
    assert pilot["all_days_healthy"] is True

    # 4. Auditoria de Custos e Consumo de Recursos
    r_costs = client.get("/api/v1/system/resource-costs", headers=h)
    assert r_costs.status_code == 200
    costs = r_costs.json()
    assert costs["external_api_costs_brl"] == 0.0
    assert "CUSTO ZERO" in costs["verdict"]


