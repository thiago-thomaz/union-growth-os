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
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "2000")
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


def test_29_backup_integrity_and_isolated_restore_verification(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # Executa teste real de restauração em ambiente isolado (in-memory SQLite)
    r = client.post("/api/v1/system/backup/test-restore", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "RESTORE_VERIFIED"
    assert data["production_database_protected"] is True
    assert data["isolated_environment"] == "sqlite:///:memory:"
    assert data["total_restored_records"] > 0
    assert "tenants" in data["restored_tables"]
    assert "strategic_goals" in data["restored_tables"]


def test_30_agent_execution_logs_processing_types(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    r = client.get("/api/v1/agents/execution-logs", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert "processing_type_breakdown" in data
    breakdown = data["processing_type_breakdown"]
    for expected_key in ("REAL_LLM", "LOCAL_MODEL", "DETERMINISTIC_PYTHON_ENGINE", "TEMPLATE_ENGINE", "FALLBACK"):
        assert expected_key in breakdown
    if data["logs"]:
        first_log = data["logs"][0]
        assert "processing_type" in first_log
        assert "model_used" in first_log
        assert "tokens_consumed" in first_log


def test_31_crm_lead_opt_out_and_origin_classification(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Cria lead com data_origin TEST
    lead_payload = {
        "full_name": "Juliana Teste LGPD",
        "email": f"juliana.teste.{RUN_SUFFIX}@empresa.com.br",
        "phone": "+5511988887777",
        "company_name": "Empresa Teste SA",
        "source_channel": "Formulário Web",
        "buy_intent": "HIGH",
        "estimated_value": 7500.0,
        "data_origin": "TEST",
        "consent_lgpd": True,
        "consent_source": "Opt-in voluntário",
        "notes": "Lead de validação automatizada da Fase 15",
    }
    r_create = client.post("/api/v1/crm/leads", headers=h, json=lead_payload)
    assert r_create.status_code == 201
    lead_id = r_create.json()["id"]

    # 2. Executa descadastro formal (opt-out)
    r_optout = client.post(f"/api/v1/crm/leads/{lead_id}/opt-out", headers=h)
    assert r_optout.status_code == 200
    assert r_optout.json()["opt_out"] is True

    # 3. Consulta CRM overview com filtro de origem TEST
    r_overview = client.get("/api/v1/crm/overview?origin=TEST", headers=h)
    assert r_overview.status_code == 200
    comm = r_overview.json()["commercial_summary"]
    assert "data_origin_breakdown" in comm
    assert comm["data_origin_breakdown"]["TEST"] >= 1
    # Garante que o lead criado está nos resultados
    leads = r_overview.json()["leads"]
    assert any(l["id"] == lead_id and l["opt_out"] is True for l in leads)


def test_32_content_factory_item_update_and_history(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Obtém lista de itens da Content Factory (ou gera se ainda não houver itens)
    r_items = client.get("/api/v1/content-factory/items?limit=5", headers=h)
    assert r_items.status_code == 200
    items = r_items.json()
    if not items:
        r_gen = client.post("/api/v1/content-factory/generate-batch", headers=h, json={"count": 5})
        assert r_gen.status_code == 201
        items = client.get("/api/v1/content-factory/items?limit=5", headers=h).json()
    assert len(items) >= 1
    item_id = items[0]["id"]

    # 2. Edita o item com rastreabilidade de histórico
    update_payload = {
        "title": "Título Editorial Revisado por Especialista — Versão Otimizada",
        "cta": "Clique no link e acesse o diagnóstico exclusivo agora.",
        "notes": "Ajuste de copy e alinhamento de headline para o público-alvo",
    }
    r_update = client.put(f"/api/v1/content-factory/items/{item_id}", headers=h, json=update_payload)
    assert r_update.status_code == 200
    updated = r_update.json()
    assert updated["title"] == update_payload["title"]
    assert updated["cta"] == update_payload["cta"]
    assert len(updated["change_history"]) >= 1
    last_entry = updated["change_history"][-1]
    assert last_entry["action"] == "EDITED"


# ===================== FASE 17 — OPERAÇÃO COMERCIAL MULTINEGÓCIO =====================
def test_33_phase17_three_business_units_services_and_pricing_calculator(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Três unidades comerciais independentes (UNION_TECH, UNION_AGENCY, UNION_PARTNERS)
    r_units = client.get("/api/v1/commercial/business-units", headers=h)
    assert r_units.status_code == 200
    units = r_units.json()
    unit_codes = {u["code"] for u in units}
    assert {"UNION_TECH", "UNION_AGENCY", "UNION_PARTNERS"}.issubset(unit_codes)

    # 2. Catálogo de 7 serviços de IA/Automação em UNION_TECH
    r_svcs = client.get("/api/v1/commercial/services?unit=UNION_TECH", headers=h)
    assert r_svcs.status_code == 200
    tech_svcs = r_svcs.json()
    assert len(tech_svcs) >= 7
    svc_codes = {s["service_code"] for s in tech_svcs}
    for code in (
        "SRV_01_DIAGNOSTICO",
        "SRV_02_AGENTES_IA",
        "SRV_03_AUTOMACAO_PROCESSOS",
        "SRV_04_DASHBOARDS",
        "SRV_05_MARKETING_IA",
        "SRV_06_CRM_COMERCIAL",
        "SRV_07_SISTEMAS_SOB_MEDIDA",
    ):
        assert code in svc_codes

    # 3. Calculadora dinâmica de custos/preços e aprovação do proprietário
    svc_id = tech_svcs[0]["id"]
    r_price = client.put(
        f"/api/v1/commercial/services/{svc_id}/pricing",
        headers=h,
        json={
            "dev_hours_estimated": 20.0,
            "complexity_level": "MEDIUM",
            "hourly_rate_brl": 160.0,
            "infra_cost_brl": 100.0,
            "tools_api_cost_brl": 50.0,
            "support_cost_brl": 200.0,
            "tax_rate_pct": 12.0,
            "target_margin_pct": 45.0,
            "owner_approve_pricing": True,
        },
    )
    assert r_price.status_code == 200
    calc = r_price.json()["pricing_calculator"]
    assert calc["estimated_cost_brl"] > 0
    assert calc["suggested_price_brl"] > calc["estimated_cost_brl"]
    assert calc["pricing_approved_by_owner"] is True

    # 4. Cadastro e listagem de ofertas comerciais
    r_off = client.post(
        "/api/v1/commercial/offers",
        headers=h,
        json={
            "business_unit_code": "UNION_TECH",
            "product_service_id": svc_id,
            "name": f"Oferta Teste Automação {RUN_SUFFIX}",
            "headline": "Diagnóstico + Protótipo Funcional",
            "offer_type": "HYBRID_SETUP_PLUS_MRR",
            "plan_tier": "PRO",
            "setup_fee_brl": 4500.0,
            "monthly_fee_brl": 590.0,
            "included_items": ["Mapeamento", "Agente IA"],
            "owner_approved": True,
            "data_origin": "TEST",
        },
    )
    assert r_off.status_code == 201
    assert r_off.json()["owner_approved"] is True


def test_34_phase17_market_opportunities_and_landing_pages(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Oportunidades de mercado nos 8 segmentos prioritários
    r_opps = client.get("/api/v1/commercial/market-opportunities", headers=h)
    assert r_opps.status_code == 200
    opps = r_opps.json()
    assert len(opps) >= 8

    # 2. Pesquisa de nova oportunidade sob demanda
    r_res = client.post(
        "/api/v1/commercial/market-opportunities/research",
        headers=h,
        json={
            "segment": "Logística e Transportadoras",
            "business_unit_code": "UNION_TECH",
            "custom_focus": "Rastreamento automatizado de entregas e atendimento de ocorrências",
        },
    )
    assert r_res.status_code == 201
    assert r_res.json()["segment"] == "Logística e Transportadoras"

    # 3. Landing pages comerciais independentes (UNION TECH + 6 específicas + AGENCY + PARTNERS)
    r_lps = client.get("/api/v1/commercial/landing-pages", headers=h)
    assert r_lps.status_code == 200
    lps = r_lps.json()
    slugs = {lp["slug"] for lp in lps}
    for expected_slug in (
        "union-tech",
        "agentes-ia",
        "automacao-empresarial",
        "consultoria-ia",
        "crm-inteligente",
        "marketing-automatizado",
        "sistemas-sob-medida",
        "union-agency",
        "union-partners",
    ):
        assert expected_slug in slugs


def test_35_phase17_landing_page_lead_capture_deduplication_scoring_and_funnel(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    lead_email = f"diretor.tech.{RUN_SUFFIX}@clienteindustrial.com.br"

    # 1. Captura de lead via Landing Page com consentimento LGPD
    r_cap1 = client.post(
        "/api/v1/commercial/landing-pages/capture-lead",
        headers=h,
        json={
            "landing_page_slug": "agentes-ia",
            "full_name": "Roberto Almeida",
            "email": lead_email,
            "phone": "+5511977776666",
            "company_name": "Indústria Almeida Ltda",
            "buy_intent": "URGENT",
            "estimated_value": 18000.0,
            "consent_lgpd": True,
            "utm_campaign": "lp_agentes_ia_q4",
            "data_origin": "TEST",
        },
    )
    assert r_cap1.status_code == 201
    d1 = r_cap1.json()
    assert d1["deduplicated"] is False
    assert d1["business_unit_code"] == "UNION_TECH"
    assert d1["lead_score"] >= 70
    lead_id = d1["lead_id"]

    # 2. Deduplicação automática ao enviar mesmo e-mail na mesma unidade
    r_cap2 = client.post(
        "/api/v1/commercial/landing-pages/capture-lead",
        headers=h,
        json={
            "landing_page_slug": "automacao-empresarial",
            "full_name": "Roberto Almeida Diretor",
            "email": lead_email,
            "phone": "+5511977776666",
            "company_name": "Indústria Almeida Ltda",
            "buy_intent": "URGENT",
            "estimated_value": 22000.0,
            "consent_lgpd": True,
            "data_origin": "TEST",
        },
    )
    assert r_cap2.status_code == 201
    d2 = r_cap2.json()
    assert d2["deduplicated"] is True
    assert d2["lead_id"] == lead_id

    # 3. Evolução no funil de 10 etapas (DIAGNOSTICO)
    r_stg = client.put(
        f"/api/v1/crm/leads/{lead_id}/funnel-stage",
        headers=h,
        json={"funnel_stage": "DIAGNOSTICO", "notes": "Reunião de diagnóstico agendada."},
    )
    assert r_stg.status_code == 200
    assert r_stg.json()["funnel_stage"] == "DIAGNOSTICO"


def test_36_phase17_commercial_proposals_owner_approval_gate_pdf_and_deal_closing(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Gerar proposta comercial
    r_prop = client.post(
        "/api/v1/commercial/proposals",
        headers=h,
        json={
            "business_unit_code": "UNION_TECH",
            "service_code": "SRV_02_AGENTES_IA",
            "client_name": "Marcos Viana",
            "client_company": f"Viana Distribuidora {RUN_SUFFIX} Ltda",
            "client_email": f"marcos.{RUN_SUFFIX}@vianadist.com.br",
            "identified_problem": "Atendimento comercial lento e perda de cotações no WhatsApp.",
            "setup_price_brl": 6500.0,
            "monthly_price_brl": 690.0,
            "data_origin": "TEST",
        },
    )
    assert r_prop.status_code == 201
    prop = r_prop.json()
    prop_id = prop["id"]
    assert prop["status"] == "PENDING_APPROVAL"
    assert prop["owner_approved"] is False

    # 2. Trava de Governança: proibir envio/fechamento vinculante sem aprovação do proprietário
    r_forbidden = client.put(
        f"/api/v1/commercial/proposals/{prop_id}/status",
        headers=h,
        json={"status": "ACCEPTED", "owner_approve": False},
    )
    assert r_forbidden.status_code == 403

    # 3. Gerar documento PDF/HTML imprimível da proposta
    r_pdf = client.get(f"/api/v1/commercial/proposals/{prop_id}/pdf", headers=h)
    assert r_pdf.status_code == 200
    assert "PROPOSTA COMERCIAL" in r_pdf.text
    assert prop["proposal_number"] in r_pdf.text

    # 4. Aprovar pelo proprietário e fechar negócio (ACCEPTED)
    r_accept = client.put(
        f"/api/v1/commercial/proposals/{prop_id}/status",
        headers=h,
        json={"status": "ACCEPTED", "owner_approve": True},
    )
    assert r_accept.status_code == 200
    assert r_accept.json()["status"] == "ACCEPTED"
    assert r_accept.json()["owner_approved"] is True


def test_37_phase17_union_agency_isolated_clients_and_plan_limits(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    r_create = client.post(
        "/api/v1/agency/clients",
        headers=h,
        json={
            "client_name": f"Clínica Vida Plena {RUN_SUFFIX} Ltda",
            "brand_name": f"VidaPlena {RUN_SUFFIX}",
            "segment": "Clínicas e Saúde",
            "plan_tier": "BUSINESS",
            "setup_fee_brl": 2500.0,
            "monthly_retainer_brl": 4900.0,
            "owner_approved_pricing": True,
            "data_origin": "TEST",
        },
    )
    assert r_create.status_code == 201
    c_data = r_create.json()
    assert c_data["plan_tier"] == "BUSINESS"
    assert c_data["plan_limits"]["max_monthly_contents"] == 60

    r_list = client.get("/api/v1/agency/clients", headers=h)
    assert r_list.status_code == 200
    assert any(c["id"] == c_data["id"] for c in r_list.json())


def test_38_phase17_union_partners_affiliates_click_tracking_and_commission_reconciliation(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Verificar programas de afiliados (Mercado Livre, Amazon, Shopee, etc.)
    r_progs = client.get("/api/v1/partners/programs", headers=h)
    assert r_progs.status_code == 200
    progs = r_progs.json()
    platforms = {p["platform"] for p in progs}
    assert {"mercado_livre", "amazon", "shopee"}.issubset(platforms)
    ml_prog_id = next(p["id"] for p in progs if p["platform"] == "mercado_livre")

    # 2. Cadastrar produto curado com link rastreável e aviso publicitário
    r_prod = client.post(
        "/api/v1/partners/products",
        headers=h,
        json={
            "program_id": ml_prog_id,
            "name": f"Servidor Mini PC Corporativo {RUN_SUFFIX}",
            "category": "Hardware & Infraestrutura",
            "brand": "Dell / Lenovo",
            "observed_price_brl": 3200.0,
            "price_source": "Consulta Oficial Mercado Livre",
            "authorized_url": "https://www.mercadolivre.com.br/p/MLB12345",
            "affiliate_url": "https://mercadolivre.com/sec/test12345",
            "commission_pct": 8.0,
            "data_origin": "TEST",
        },
    )
    assert r_prod.status_code == 201
    prod = r_prod.json()
    prod_id = prod["id"]
    tracking_code = prod["tracking_code"]
    assert "AFILIADO" in prod["disclosure_label"].upper()

    # 3. Registrar clique rastreável -> NUNCA deve contar como venda ou receita
    r_click = client.post(
        "/api/v1/partners/clicks",
        headers=h,
        json={"tracking_code": tracking_code, "source_channel": "Artigo Comparativo Blog"},
    )
    assert r_click.status_code == 201
    click_data = r_click.json()
    assert click_data["counted_as_sale"] is False
    assert click_data["revenue_recorded_brl"] == 0.0

    # 4. Registrar conversão pendente -> NÃO concilia no financeiro até confirmação
    ext_order = f"ORD-ML-{RUN_SUFFIX}"
    r_conv = client.post(
        "/api/v1/partners/conversions",
        headers=h,
        json={
            "product_id": prod_id,
            "click_id": click_data["click_id"],
            "external_order_id": ext_order,
            "sale_amount_brl": 3200.0,
            "commission_amount_brl": 256.0,
            "commission_status": "PENDING_CONFIRMATION",
            "attribution_evidence": "Pedido aguardando prazo de entrega na plataforma",
            "data_origin": "TEST",
        },
    )
    assert r_conv.status_code == 201
    conv = r_conv.json()
    assert conv["reconciled_in_finance"] is False
    conv_id = conv["conversion_id"]

    # 5. Conciliar comissão após confirmação da plataforma
    r_rec = client.post(
        f"/api/v1/partners/conversions/{conv_id}/reconcile",
        headers=h,
        json={
            "commission_status": "PAID",
            "attribution_evidence": f"Relatório Oficial Mercado Livre Afiliados #{ext_order} — Pago",
        },
    )
    assert r_rec.status_code == 200
    rec_data = r_rec.json()
    assert rec_data["reconciled_in_finance"] is True
    assert rec_data["financial_record_id"] is not None


def test_39_phase17_multibusiness_dashboard_finance_and_ceo_briefing(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Gerar lote de conteúdo específico para uma unidade (UNION_PARTNERS)
    r_cf = client.post(
        "/api/v1/content-factory/generate-batch",
        headers=h,
        json={"count": 3, "business_unit_code": "UNION_PARTNERS", "utm_campaign": "afiliados_q4"},
    )
    assert r_cf.status_code == 201
    assert r_cf.json()["items"][0]["business_unit_code"] == "UNION_PARTNERS"

    # 2. Resumo financeiro multinegócio separando DADO_REAL, PROJECAO e META
    r_fin = client.get("/api/v1/finance/multibusiness-summary?unit=ALL", headers=h)
    assert r_fin.status_code == 200
    fin = r_fin.json()
    assert "dado_real" in fin["consolidated"]
    assert "projecao" in fin["consolidated"]
    assert "meta" in fin["consolidated"]
    assert "UNION_TECH" in fin["units"]
    assert "UNION_AGENCY" in fin["units"]
    assert "UNION_PARTNERS" in fin["units"]

    # 3. Briefing diário consolidado do AI CEO com classificação honesta DETERMINISTIC_PYTHON_ENGINE
    r_ceo = client.post("/api/v1/ceo/multibusiness-briefing", headers=h)
    assert r_ceo.status_code == 201
    ceo = r_ceo.json()
    assert ceo["processing_type"] == "DETERMINISTIC_PYTHON_ENGINE"
    assert "UNION_TECH" in ceo["units_performance"]

    # 4. Dashboard executivo multinegócio
    r_dash = client.get("/api/v1/commercial/multibusiness-dashboard?unit=UNION_TECH", headers=h)
    assert r_dash.status_code == 200
    dash = r_dash.json()
    assert dash["selected_unit"] == "UNION_TECH"
    assert len(dash["business_units"]) == 3
    assert "sales_funnel_10_stages" in dash


# ===================== FASE 18 — ATIVAÇÃO COMERCIAL REAL, PAGAMENTOS & ONBOARDING =====================
def test_40_phase18_payments_sandbox_charge_webhook_hmac_idempotency_and_onboarding(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Trava de Governança: proibir criação de cobrança sem aprovação do proprietário
    r_unauth = client.post(
        "/api/v1/commercial/payments/charge",
        headers=h,
        json={
            "business_unit_code": "UNION_TECH",
            "client_name": "Cliente Sem Aprovação",
            "client_company": "Empresa X Ltda",
            "client_email": f"x.{RUN_SUFFIX}@empresa.com.br",
            "amount_brl": 5200.0,
            "payment_method": "PIX",
            "sandbox_mode": True,
            "owner_approved": False,
            "data_origin": "TEST",
        },
    )
    assert r_unauth.status_code == 403

    # 2. Emitir cobrança em Sandbox com aprovação do proprietário e chave de idempotência
    idem_key = f"idem-charge-{RUN_SUFFIX}"
    r_charge = client.post(
        "/api/v1/commercial/payments/charge",
        headers=h,
        json={
            "business_unit_code": "UNION_TECH",
            "client_name": "Diretor Financeiro",
            "client_company": f"Grupo Industrial {RUN_SUFFIX} S.A.",
            "client_email": f"fin.{RUN_SUFFIX}@grupoind.com.br",
            "amount_brl": 7800.0,
            "payment_method": "PIX",
            "idempotency_key": idem_key,
            "sandbox_mode": True,
            "owner_approved": True,
            "data_origin": "TEST",
        },
    )
    assert r_charge.status_code == 201
    charge = r_charge.json()
    assert charge["status"] == "PENDING"
    assert charge["execution_mode"] == "SANDBOX"
    assert charge["reconciled_in_finance"] is False
    assert charge["counted_as_received_revenue"] is False
    assert charge["idempotent_reused"] is False

    # 3. Idempotência de criação de cobrança: mesma idempotency_key retorna a mesma transação
    r_charge_dup = client.post(
        "/api/v1/commercial/payments/charge",
        headers=h,
        json={
            "business_unit_code": "UNION_TECH",
            "client_name": "Diretor Financeiro",
            "client_company": f"Grupo Industrial {RUN_SUFFIX} S.A.",
            "client_email": f"fin.{RUN_SUFFIX}@grupoind.com.br",
            "amount_brl": 7800.0,
            "payment_method": "PIX",
            "idempotency_key": idem_key,
            "sandbox_mode": True,
            "owner_approved": True,
            "data_origin": "TEST",
        },
    )
    assert r_charge_dup.status_code == 201
    assert r_charge_dup.json()["idempotent_reused"] is True
    assert r_charge_dup.json()["id"] == charge["id"]

    # 4. Webhook com assinatura criptográfica inválida deve ser rejeitado (HTTP 401)
    r_wh_bad = client.post(
        "/api/v1/commercial/payments/webhook",
        headers=h,
        json={
            "external_reference": charge["external_reference"],
            "provider_payment_id": charge["provider_payment_id"],
            "new_status": "APPROVED",
            "signature": "invalid_forged_signature_12345",
        },
    )
    assert r_wh_bad.status_code == 401

    # 5. Webhook com assinatura HMAC-SHA256 válida confirma pagamento, concilia financeiro e cria projeto de Onboarding
    valid_sig = charge["webhook_test_signature_for_approved"]
    r_wh_ok = client.post(
        "/api/v1/commercial/payments/webhook",
        headers=h,
        json={
            "external_reference": charge["external_reference"],
            "provider_payment_id": charge["provider_payment_id"],
            "new_status": "APPROVED",
            "signature": valid_sig,
        },
    )
    assert r_wh_ok.status_code == 200
    wh_data = r_wh_ok.json()
    assert wh_data["status"] == "APPROVED"
    assert wh_data["webhook_signature_verified"] is True
    assert wh_data["reconciled_in_finance"] is True
    assert wh_data["counted_as_received_revenue"] is True
    assert wh_data["financial_record_id"] is not None
    assert wh_data["onboarding_project_id"] is not None
    assert wh_data["idempotent_duplicate"] is False

    # 6. Idempotência de Webhook: reenviar o mesmo evento APPROVED não duplica receita nem projeto
    r_wh_dup = client.post(
        "/api/v1/commercial/payments/webhook",
        headers=h,
        json={
            "external_reference": charge["external_reference"],
            "provider_payment_id": charge["provider_payment_id"],
            "new_status": "APPROVED",
            "signature": valid_sig,
        },
    )
    assert r_wh_dup.status_code == 200
    assert r_wh_dup.json()["idempotent_duplicate"] is True
    assert r_wh_dup.json()["financial_record_id"] == wh_data["financial_record_id"]


def test_41_phase18_onboarding_delivery_lifecycle_and_lgpd_subject_rights(client: TestClient):
    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Verificar projeto de entrega criado e avançar checklist / conclusão
    r_projs = client.get("/api/v1/commercial/delivery-projects", headers=h)
    assert r_projs.status_code == 200
    projs = r_projs.json()
    assert len(projs) >= 1
    proj_id = projs[0]["id"]

    r_upd = client.put(
        f"/api/v1/commercial/delivery-projects/{proj_id}",
        headers=h,
        json={
            "completed_checklist_step": "Coleta de credenciais",
            "deliverable_submitted": "Mapeamento",
            "status": "COMPLETED",
            "client_validation_status": "APPROVED_BY_CLIENT",
            "client_validation_notes": "Entrega validada com sucesso pelo cliente.",
        },
    )
    assert r_upd.status_code == 200
    assert r_upd.json()["status"] == "COMPLETED"
    assert r_upd.json()["progress_pct"] == 100.0
    assert r_upd.json()["client_validation_status"] == "APPROVED_BY_CLIENT"

    # 2. Criar lead para testar reativação autorizada, exportação LGPD e eliminação LGPD
    r_lead = client.post(
        "/api/v1/crm/leads",
        headers=h,
        json={
            "full_name": " Helena Titular LGPD",
            "email": f"helena.lgpd.{RUN_SUFFIX}@titular.com.br",
            "phone": "+5511966665555",
            "company_name": "Helena Consultoria Ltda",
            "buy_intent": "HIGH",
            "estimated_value": 9000.0,
            "consent_lgpd": True,
            "data_origin": "TEST",
        },
    )
    assert r_lead.status_code == 201
    lead_id = r_lead.json()["id"]

    # Reativação com consentimento válido
    r_react = client.post(
        f"/api/v1/crm/leads/{lead_id}/reactivate",
        headers=h,
        json={"authorization_basis": "Consentimento opt-in ativo", "custom_message_notes": "Retomada de diagnóstico"},
    )
    assert r_react.status_code == 200
    assert r_react.json()["reactivation_count"] == 1

    # Exportação de portabilidade LGPD
    r_exp = client.get(f"/api/v1/crm/leads/{lead_id}/lgpd-export", headers=h)
    assert r_exp.status_code == 200
    assert r_exp.json()["personal_data"]["id"] == lead_id

    # Direito de eliminação LGPD
    r_del = client.delete(f"/api/v1/crm/leads/{lead_id}/lgpd-erasure", headers=h)
    assert r_del.status_code == 200
    assert r_del.json()["status"] == "LGPD_ERASED"


# ===================== FASE 18.1 — CICLO COMERCIAL COMPLETO (20 ETAPAS) & PAINEL 5 BUCKETS =====================
def test_42_phase18_1_full_20_step_commercial_cycle_and_5_bucket_panel(client: TestClient):
    from app.services.phase17_commercial_engine import compute_payment_webhook_signature

    token = admin_token(client)
    h = _auth_headers(token)

    # Proteção de preços aprovados: serviço 1 já foi aprovado em test_33; tentar alterar sem autorização deve retornar 403
    svcs = client.get("/api/v1/commercial/services?unit=UNION_TECH", headers=h).json()
    approved_svc = next((s for s in svcs if s["pricing_calculator"]["pricing_approved_by_owner"]), svcs[0])
    assert "scope_included" in approved_svc and "scope_excluded" in approved_svc and "approval_criteria" in approved_svc
    if approved_svc["pricing_calculator"]["pricing_approved_by_owner"]:
        r_block_price = client.put(
            f"/api/v1/commercial/services/{approved_svc['id']}/pricing",
            headers=h,
            json={"configured_price_brl": 999.0, "owner_approve_pricing": False, "force_owner_override": False},
        )
        assert r_block_price.status_code == 403

    # 1 & 2. Cadastro de Lead + Deduplicação
    cycle_email = f"ciclo181.{RUN_SUFFIX}@clientevalidacao.com.br"
    r_l1 = client.post(
        "/api/v1/commercial/landing-pages/capture-lead",
        headers=h,
        json={
            "landing_page_slug": "union-tech",
            "full_name": "Eduardo Ciclo Completo",
            "email": cycle_email,
            "phone": "+5511955554444",
            "company_name": f"Eduardo Tech {RUN_SUFFIX} Ltda",
            "buy_intent": "URGENT",
            "estimated_value": 15000.0,
            "consent_lgpd": True,
            "data_origin": "SIMULATION",
        },
    )
    assert r_l1.status_code == 201
    lead_id = r_l1.json()["lead_id"]

    r_l2 = client.post(
        "/api/v1/commercial/landing-pages/capture-lead",
        headers=h,
        json={
            "landing_page_slug": "union-tech",
            "full_name": "Eduardo Ciclo Duplicado",
            "email": cycle_email,
            "phone": "+5511955554444",
            "company_name": f"Eduardo Tech {RUN_SUFFIX} Ltda",
            "buy_intent": "URGENT",
            "estimated_value": 15000.0,
            "consent_lgpd": True,
            "data_origin": "SIMULATION",
        },
    )
    assert r_l2.status_code == 201 and r_l2.json()["deduplicated"] is True

    # 3, 4 & 5. Qualificação, Preparação de Abordagem (com cooldown de frequência), Diagnóstico e Oportunidade
    r_out1 = client.post(
        f"/api/v1/crm/leads/{lead_id}/prepare-outreach",
        headers=h,
        json={"service_code": "SRV_03_AUTOMACAO_PROCESSOS", "custom_angle": "Eliminação de planilhas", "owner_approve_outreach": False},
    )
    assert r_out1.status_code == 200
    assert r_out1.json()["external_message_sent"] is False

    # Tentar disparar segunda abordagem em menos de 24h sem override do proprietário -> bloqueio anti-spam 429
    r_out_spam = client.post(
        f"/api/v1/crm/leads/{lead_id}/prepare-outreach",
        headers=h,
        json={"service_code": "SRV_03_AUTOMACAO_PROCESSOS", "owner_approve_outreach": False},
    )
    assert r_out_spam.status_code == 429

    for stg in ("QUALIFICACAO", "DIAGNOSTICO", "OPORTUNIDADE"):
        r_s = client.put(f"/api/v1/crm/leads/{lead_id}/funnel-stage", headers=h, json={"funnel_stage": stg})
        assert r_s.status_code == 200 and r_s.json()["funnel_stage"] == stg

    # 6, 7, 8 & 9. Proposta, Bloqueio sem Aprovação, Aprovação e Contrato
    r_prop = client.post(
        "/api/v1/commercial/proposals",
        headers=h,
        json={
            "business_unit_code": "UNION_TECH",
            "lead_id": lead_id,
            "service_code": "SRV_03_AUTOMACAO_PROCESSOS",
            "client_name": "Eduardo Ciclo Completo",
            "client_company": f"Eduardo Tech {RUN_SUFFIX} Ltda",
            "client_email": cycle_email,
            "identified_problem": "Retrabalho manual entre vendas e financeiro.",
            "setup_price_brl": 6200.0,
            "monthly_price_brl": 590.0,
            "data_origin": "SIMULATION",
        },
    )
    assert r_prop.status_code == 201
    prop_id = r_prop.json()["id"]

    # Bloqueio sem aprovação (7)
    r_blk = client.put(f"/api/v1/commercial/proposals/{prop_id}/status", headers=h, json={"status": "SENT", "owner_approve": False})
    assert r_blk.status_code == 403

    # Aprovação e Contrato com evidência (8 & 9)
    r_app = client.put(
        f"/api/v1/commercial/proposals/{prop_id}/status",
        headers=h,
        json={"status": "SENT", "owner_approve": True, "acceptance_evidence": "Aprovado para envio formal"},
    )
    assert r_app.status_code == 200 and r_app.json()["owner_approved"] is True

    # 10, 11, 12, 13 & 14. Cobrança Sandbox, Webhook Inválido, Webhook Válido, Evento Duplicado e Estados (REFUNDED)
    r_chg = client.post(
        "/api/v1/commercial/payments/charge",
        headers=h,
        json={
            "proposal_id": prop_id,
            "lead_id": lead_id,
            "business_unit_code": "UNION_TECH",
            "client_name": "Eduardo Ciclo Completo",
            "client_company": f"Eduardo Tech {RUN_SUFFIX} Ltda",
            "client_email": cycle_email,
            "amount_brl": 6200.0,
            "payment_method": "PIX",
            "idempotency_key": f"idem-181-{RUN_SUFFIX}",
            "sandbox_mode": True,
            "owner_approved": True,
            "data_origin": "SIMULATION",
        },
    )
    assert r_chg.status_code == 201
    chg = r_chg.json()

    # Webhook inválido (12)
    r_wh_inv = client.post(
        "/api/v1/commercial/payments/webhook",
        headers=h,
        json={"external_reference": chg["external_reference"], "provider_payment_id": chg["provider_payment_id"], "new_status": "APPROVED", "signature": "bad"},
    )
    assert r_wh_inv.status_code == 401

    # Webhook válido -> Pagamento Aprovado + Criação do Projeto de Entrega (11, 14 & 15)
    r_wh_val = client.post(
        "/api/v1/commercial/payments/webhook",
        headers=h,
        json={
            "external_reference": chg["external_reference"],
            "provider_payment_id": chg["provider_payment_id"],
            "new_status": "APPROVED",
            "signature": chg["webhook_test_signature_for_approved"],
        },
    )
    assert r_wh_val.status_code == 200
    proj_id = r_wh_val.json()["onboarding_project_id"]
    assert proj_id is not None

    # Evento duplicado (13)
    r_wh_dup = client.post(
        "/api/v1/commercial/payments/webhook",
        headers=h,
        json={
            "external_reference": chg["external_reference"],
            "provider_payment_id": chg["provider_payment_id"],
            "new_status": "APPROVED",
            "signature": chg["webhook_test_signature_for_approved"],
        },
    )
    assert r_wh_dup.status_code == 200 and r_wh_dup.json()["idempotent_duplicate"] is True

    # 16, 17 & 18. Checklist, Bloqueio de Conclusão sem Evidência, Conclusão com Evidência e Pós-Venda
    r_no_ev = client.put(
        f"/api/v1/commercial/delivery-projects/{proj_id}",
        headers=h,
        json={"status": "COMPLETED"},
    )
    assert r_no_ev.status_code == 400  # Exige evidência!

    r_done = client.put(
        f"/api/v1/commercial/delivery-projects/{proj_id}",
        headers=h,
        json={
            "completed_checklist_step": "Testes de qualidade",
            "execution_evidence": "Deploy homologado em produção e ata de aceite assinada pelo cliente.",
            "status": "COMPLETED",
            "client_validation_status": "APPROVED_BY_CLIENT",
        },
    )
    assert r_done.status_code == 200 and r_done.json()["status"] == "COMPLETED"

    # Testar estorno (REFUNDED) em uma segunda cobrança para validar reversão de reconciliação
    r_chg2 = client.post(
        "/api/v1/commercial/payments/charge",
        headers=h,
        json={
            "business_unit_code": "UNION_TECH",
            "client_name": "Cliente Estorno Teste",
            "client_company": "Estorno Ltda",
            "client_email": f"estorno.{RUN_SUFFIX}@teste.com.br",
            "amount_brl": 1500.0,
            "payment_method": "PIX",
            "sandbox_mode": True,
            "owner_approved": True,
            "data_origin": "SIMULATION",
        },
    ).json()
    sig_refund = compute_payment_webhook_signature(r_chg2["external_reference"], r_chg2["provider_payment_id"], "REFUNDED")
    r_wh_ref = client.post(
        "/api/v1/commercial/payments/webhook",
        headers=h,
        json={
            "external_reference": r_chg2["external_reference"],
            "provider_payment_id": r_chg2["provider_payment_id"],
            "new_status": "REFUNDED",
            "signature": sig_refund,
        },
    )
    assert r_wh_ref.status_code == 200 and r_wh_ref.json()["reconciled_in_finance"] is False

    # Validar Painel Executivo de 5 Buckets (REAL, ESTIMATIVA, PROJECAO, META, SIMULACAO)
    r_panel = client.get("/api/v1/commercial/phase18-1-executive-panel", headers=h)
    assert r_panel.status_code == 200
    panel = r_panel.json()
    for bucket in ("REAL", "ESTIMATIVA", "PROJECAO", "META", "SIMULACAO", "funnel_12_stage_alerts"):
        assert bucket in panel
    # Como nenhuma transação foi feita via PRODUCTION_API real do Mercado Pago, receita live REAL deve ser 0.0
    assert panel["REAL"]["receita_recebida_confirmada_brl"] == 0.0
    assert panel["REAL"]["first_real_paid_customer_verified"] is False
    assert panel["SIMULACAO"]["cobrancas_sandbox_total"] >= 2

    # 19 & 20. Exportação LGPD e Eliminação LGPD
    r_exp = client.get(f"/api/v1/crm/leads/{lead_id}/lgpd-export", headers=h)
    assert r_exp.status_code == 200
    r_eras = client.delete(f"/api/v1/crm/leads/{lead_id}/lgpd-erasure", headers=h)
    assert r_eras.status_code == 200 and r_eras.json()["status"] == "LGPD_ERASED"


def test_43_phase19_union_ai_engine_hub_complete_suite(client: TestClient, monkeypatch):
    """
    FASE 19 — UNION AI ENGINE HUB:
    Valida todos os requisitos da Fase 19:
    1. Overview inicial: Gemini prioritário (gemini-2.5-flash), modo FREE_ONLY, 6 provedores e 12 agentes configurados.
    2. Criptografia Fernet de API Keys, mascaramento e isolamento multi-tenant.
    3. Teste de conexão com credencial inválida, credencial válida (mock HTTP nos testes automatizados) e modelo inexistente.
    4. AI Router em modo FREE_ONLY: bloqueio estrito de motores pagos (OpenAI GPT-4o, Anthropic Claude, Imagen 3, Veo 2) e custo desconhecido (GenericOpenAICompatibleProvider).
    5. Verificação estrita de capacidades individuais (Anthropic/Groq não geram imagens ou vídeos; modelo de texto Gemini Flash não finge image_generation).
    6. Geração de texto, geração estruturada JSON, campanha completa (25 itens) e peça individual via Gemini.
    7. Fallback inteligente (Gemini falha temporariamente -> fallback automático para Groq gratuito autorizado -> AIFallbackRecord registrado).
    8. Honestidade estrita: quando todos os motores compatíveis falham, retorna falha clara e NÃO simula template como IA real.
    9. AI IMAGE STUDIO (PROMPT_ONLY gratuito vs GENERATE_IMAGE com Imagen 3 em OWNER_APPROVED).
    10. AI VIDEO STUDIO (separação estrita entre SCRIPT_ONLY / STORYBOARD_ONLY com video_effectively_generated=False vs DIRECT_VIDEO_GENERATION).
    11. Limites de uso (bloqueio BLOCKED_LIMIT quando limite diário é atingido) e monitoramento AI USAGE & COSTS.
    """
    import json
    from app.services.ai_engines_hub import GeminiProvider, GroqProvider

    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Overview inicial do UNION AI ENGINE HUB
    r_ov = client.get("/api/v1/ai-engine-hub/overview", headers=h)
    assert r_ov.status_code == 200
    ov = r_ov.json()
    assert ov["configuration"]["default_provider_key"] == "gemini"
    assert ov["configuration"]["default_text_model"] == "gemini-2.5-flash"
    assert ov["configuration"]["cost_policy_mode"] == "FREE_ONLY"
    assert len(ov["providers"]) >= 6
    assert len(ov["configuration"]["agent_routing"]) == 12

    # 2. Teste de conexão sem credencial / credencial curta inválida -> INVALID_CREDENTIALS
    r_test_inv = client.post(
        "/api/v1/ai-engine-hub/test-connection",
        headers=h,
        json={"provider_key": "gemini", "model_id": "gemini-2.5-flash"},
    )
    assert r_test_inv.status_code == 200
    assert r_test_inv.json()["ok"] is False
    assert r_test_inv.json()["status"] == "INVALID_CREDENTIALS"

    # 3. Salvar credencial criptografada com Fernet -> nunca expõe a chave integral
    raw_secret_key = "AIzaSyTestMockGeminiKeyForUnitTesting123456"
    r_cred = client.post(
        "/api/v1/ai-engine-hub/credentials",
        headers=h,
        json={"provider_key": "gemini", "api_key": raw_secret_key, "is_active": True},
    )
    assert r_cred.status_code == 200
    cred_data = r_cred.json()
    assert cred_data["has_credential"] is True
    assert raw_secret_key not in json.dumps(cred_data)
    assert "***" in cred_data["masked_key_preview"] or "..." in cred_data["masked_key_preview"]

    # 4. Bloqueio de motores pagos e de custo desconhecido em FREE_ONLY
    for paid_prov, paid_mod in [("openai", "gpt-4o"), ("anthropic", "claude-3-7-sonnet-latest"), ("openai_compatible", "custom-openai-model")]:
        r_blk = client.post(
            "/api/v1/ai-engine-hub/route-execute",
            headers=h,
            json={
                "task_type": "copywriting",
                "required_capability": "text_generation",
                "provider_key": paid_prov,
                "model_id": paid_mod,
                "prompt": "Teste bloqueio FREE_ONLY",
            },
        )
        assert r_blk.status_code == 200
        # Sem fallback válido configurado ainda, deve falhar/bloquear sem cobrar e sem simular
        assert r_blk.json()["ok"] is False
        assert r_blk.json()["estimated_cost_brl"] == 0.0

    # 5. Bloqueio de capacidade inexistente (ex.: tentar image_generation em modelo de texto gemini-2.5-flash ou anthropic)
    r_cap_blk = client.post(
        "/api/v1/ai-engine-hub/route-execute",
        headers=h,
        json={
            "task_type": "image_generation",
            "required_capability": "image_generation",
            "provider_key": "gemini",
            "model_id": "gemini-2.5-flash",
            "prompt": "Gerar imagem com modelo de texto",
        },
    )
    assert r_cap_blk.status_code == 200
    assert r_cap_blk.json()["ok"] is False
    assert r_cap_blk.json()["status"] == "BLOCKED_CAPABILITY"

    # 6. Mock controlado de GeminiProvider (APENAS para teste unitário automatizado — documentado no relatório)
    def mock_gemini_test_conn(self, model_id="gemini-2.5-flash"):
        if model_id == "modelo-inexistente-999":
            return {"ok": False, "status": "MODEL_NOT_FOUND", "error": "Modelo não encontrado."}
        return {"ok": True, "status": "CONNECTED", "latency_ms": 42.0, "models_discovered": ["gemini-2.5-flash", "gemini-2.0-flash"]}

    def mock_gemini_gen_text(self, model_id, prompt, system_instruction="", temperature=0.4):
        if model_id == "modelo-indisponivel":
            raise LookupError("Modelo indisponível.")
        return {
            "text": f"[MOCK_UNIT_TEST_GEMINI_OUTPUT] Estratégia gerada para: {prompt[:80]}",
            "provider_key": "gemini",
            "model_id": model_id,
            "input_tokens": 25,
            "output_tokens": 45,
            "total_tokens": 70,
            "duration_ms": 55.0,
        }

    def mock_gemini_gen_struct(self, model_id, prompt, schema_hint="", temperature=0.2):
        return {
            "data": {"headline": "Campanha IA Estruturada", "cta": "Agendar Diagnóstico"},
            "text": '{"headline": "Campanha IA Estruturada", "cta": "Agendar Diagnóstico"}',
            "provider_key": "gemini",
            "model_id": model_id,
            "input_tokens": 20,
            "output_tokens": 30,
            "total_tokens": 50,
            "duration_ms": 48.0,
        }

    monkeypatch.setattr(GeminiProvider, "test_connection", mock_gemini_test_conn)
    monkeypatch.setattr(GeminiProvider, "generate_text", mock_gemini_gen_text)
    monkeypatch.setattr(GeminiProvider, "generate_structured", mock_gemini_gen_struct)

    # Validar conexão mockada com credencial válida e modelo inexistente
    r_conn_ok = client.post("/api/v1/ai-engine-hub/test-connection", headers=h, json={"provider_key": "gemini", "model_id": "gemini-2.5-flash"})
    assert r_conn_ok.status_code == 200 and r_conn_ok.json()["ok"] is True and r_conn_ok.json()["status"] == "CONNECTED"

    r_conn_404 = client.post("/api/v1/ai-engine-hub/test-connection", headers=h, json={"provider_key": "gemini", "model_id": "modelo-inexistente-999"})
    assert r_conn_404.status_code == 200 and r_conn_404.json()["ok"] is False and r_conn_404.json()["status"] == "MODEL_NOT_FOUND"

    # 7. Geração de Texto e Geração Estruturada via AI Router
    r_txt = client.post(
        "/api/v1/ai-engine-hub/route-execute",
        headers=h,
        json={"task_type": "copywriting", "required_capability": "text_generation", "prompt": "Criar copy para UNION TECH"},
    )
    assert r_txt.status_code == 200 and r_txt.json()["ok"] is True
    assert r_txt.json()["executed_provider"] == "gemini"
    assert r_txt.json()["cost_classification"] == "VERIFIED_FREE"

    r_str = client.post(
        "/api/v1/ai-engine-hub/route-execute",
        headers=h,
        json={"task_type": "seo", "required_capability": "structured_generation", "prompt": "Gerar JSON SEO"},
    )
    assert r_str.status_code == 200 and r_str.json()["ok"] is True
    assert r_str.json()["output"]["data"]["headline"] == "Campanha IA Estruturada"

    # 8. GERAR CAMPANHA COMPLETA (25 componentes) e GERAR PEÇA INDIVIDUAL
    r_camp = client.post(
        "/api/v1/ai-engine-hub/campaigns/generate",
        headers=h,
        json={
            "generation_scope": "FULL_CAMPAIGN",
            "campaign_name": f"Campanha Fase 19 {RUN_SUFFIX}",
            "product_or_offer": "Agentes de IA Especializados",
            "channel": "LinkedIn & Google SEO",
        },
    )
    assert r_camp.status_code == 200 and r_camp.json()["ok"] is True
    pkg = r_camp.json()["package"]
    assert "1_objetivo" in pkg and "25_cronograma" in pkg

    r_piece = client.post(
        "/api/v1/ai-engine-hub/campaigns/generate",
        headers=h,
        json={"generation_scope": "SINGLE_PIECE", "piece_type": "CTA", "campaign_name": "CTA Rápido"},
    )
    assert r_piece.status_code == 200 and r_piece.json()["ok"] is True and r_piece.json()["piece_type"] == "CTA"

    # 9. AI IMAGE STUDIO: PROMPT_ONLY (gratuito via Gemini Flash) vs GENERATE_IMAGE (bloqueado em FREE_ONLY para Imagen 3 pago)
    r_img_prompt = client.post(
        "/api/v1/ai-engine-hub/image-studio/generate",
        headers=h,
        json={"prompt": "Banner executivo de IA", "operation_mode": "PROMPT_ONLY"},
    )
    assert r_img_prompt.status_code == 200 and r_img_prompt.json()["ok"] is True
    assert r_img_prompt.json()["delivery_stage"] == "PROMPT_ONLY"
    assert r_img_prompt.json()["image_generated"] is False

    r_img_paid_blk = client.post(
        "/api/v1/ai-engine-hub/image-studio/generate",
        headers=h,
        json={"prompt": "Banner renderizado Imagen 3", "operation_mode": "GENERATE_IMAGE"},
    )
    assert r_img_paid_blk.status_code == 200 and r_img_paid_blk.json()["ok"] is False
    assert r_img_paid_blk.json()["status"] == "BLOCKED_FREE_ONLY"

    # 10. AI VIDEO STUDIO: Separação estrita entre Roteiro/Storyboard (video_effectively_generated=False) e Vídeo Direto (bloqueado em FREE_ONLY)
    r_vid_script = client.post(
        "/api/v1/ai-engine-hub/video-studio/generate",
        headers=h,
        json={"prompt": "Roteiro Reels Automação", "target_stage": "SCRIPT_AND_STORYBOARD"},
    )
    assert r_vid_script.status_code == 200 and r_vid_script.json()["ok"] is True
    assert r_vid_script.json()["delivery_stage"] == "STORYBOARD_ONLY"
    assert r_vid_script.json()["video_effectively_generated"] is False
    assert len(r_vid_script.json()["storyboard"]) == 3

    r_vid_direct_blk = client.post(
        "/api/v1/ai-engine-hub/video-studio/generate",
        headers=h,
        json={"prompt": "Vídeo Veo 2 Direto", "target_stage": "DIRECT_VIDEO_GENERATION"},
    )
    assert r_vid_direct_blk.status_code == 200 and r_vid_direct_blk.json()["ok"] is False
    assert r_vid_direct_blk.json()["video_effectively_generated"] is False

    # 11. Teste de Fallback Inteligente (Gemini falha temporariamente -> Fallback para Groq Gratuito autorizado)
    def mock_gemini_fail(self, model_id, prompt, system_instruction="", temperature=0.4):
        raise RuntimeError("Erro 503 temporário simulado no Gemini.")

    def mock_groq_ok(self, model_id, prompt, system_instruction="", temperature=0.4):
        return {
            "text": f"[MOCK_GROQ_FALLBACK_OK] {prompt[:50]}",
            "provider_key": "groq",
            "model_id": model_id,
            "input_tokens": 15,
            "output_tokens": 25,
            "total_tokens": 40,
            "duration_ms": 22.0,
        }

    monkeypatch.setattr(GeminiProvider, "generate_text", mock_gemini_fail)
    monkeypatch.setattr(GroqProvider, "generate_text", mock_groq_ok)
    client.post("/api/v1/ai-engine-hub/credentials", headers=h, json={"provider_key": "groq", "api_key": "gsk_mock_groq_key_1234567890", "is_active": True})

    r_fb = client.post(
        "/api/v1/ai-engine-hub/route-execute",
        headers=h,
        json={"task_type": "copywriting", "required_capability": "text_generation", "prompt": "Testar fallback para Groq"},
    )
    assert r_fb.status_code == 200 and r_fb.json()["ok"] is True
    assert r_fb.json()["fallback_used"] is True
    assert r_fb.json()["executed_provider"] == "groq"

    # 12. Verificar Limites Configuráveis (definir daily_requests = 1 -> bloquear próxima chamada com BLOCKED_LIMIT)
    client.put(
        "/api/v1/ai-engine-hub/configuration",
        headers=h,
        json={"limits": {"daily_requests": 1}},
    )
    r_lim_blk = client.post(
        "/api/v1/ai-engine-hub/route-execute",
        headers=h,
        json={"task_type": "copywriting", "required_capability": "text_generation", "prompt": "Deve bloquear por limite diário"},
    )
    assert r_lim_blk.status_code == 200 and r_lim_blk.json()["ok"] is False
    assert r_lim_blk.json()["status"] == "BLOCKED_LIMIT"

    # Restaurar limite diário padrão (1500) e validar histórico + AI USAGE & COSTS
    r_restored = client.put(
        "/api/v1/ai-engine-hub/configuration",
        headers=h,
        json={"limits": {"daily_requests": 1500}},
    )
    assert r_restored.status_code == 200
    final_ov = r_restored.json()
    assert final_ov["usage_and_costs"]["by_cost_classification"]["VERIFIED_FREE"]["requests"] >= 5
    assert len(final_ov["recent_fallbacks"]) >= 1


def test_44_phase20_qa_defects_security_and_e2e_15_scenarios(client: TestClient, monkeypatch):
    """
    FASE 20 — Suite Completa de Regressão (DEFECT-01 a DEFECT-05), Segurança Multi-Tenant
    e 15 Cenários E2E Integrados no tenant isolado QA_AUTOMATED_TENANT.
    """
    from app.services.ai_engines_hub import GeminiProvider

    token = admin_token(client)
    h = _auth_headers(token)

    # =========================================================================
    # PARTE 1: VALIDAÇÃO DE REGRESSÃO DOS 5 DEFEITOS CORRIGIDOS NA FASE 20
    # =========================================================================

    # DEFECT-01: Rota /api/* inexistente DEVE retornar JSON 404 (e nunca index.html com HTTP 200)
    r_bad_api = client.get("/api/v1/rota-inexistente-auditoria-fase20")
    assert r_bad_api.status_code == 404
    assert "application/json" in r_bad_api.headers.get("content-type", "")

    # DEFECT-02: Isolamento Multi-Tenant estrito no header X-Tenant-Id
    r_cross_tenant = client.get(
        "/api/v1/dashboard/overview",
        headers={**h, "X-Tenant-Id": "999999"},
    )
    assert r_cross_tenant.status_code == 403

    r_invalid_tenant_hdr = client.get(
        "/api/v1/dashboard/overview",
        headers={**h, "X-Tenant-Id": "abc_sql_inject"},
    )
    assert r_invalid_tenant_hdr.status_code == 403

    # DEFECT-04: Landing Page pública GET /lp/{slug} e captura pública POST /api/v1/public/landing-pages/{slug}/capture
    r_public_lp = client.get("/lp/agentes-ia")
    assert r_public_lp.status_code == 200
    assert "text/html" in r_public_lp.headers.get("content-type", "")
    assert "Agentes de IA" in r_public_lp.text
    assert "lgpd" in r_public_lp.text.lower()

    r_public_lp_404 = client.get("/lp/slug-inexistente-999")
    assert r_public_lp_404.status_code == 404

    # Captura pública sem consentimento LGPD deve falhar com HTTP 400
    r_pub_no_lgpd = client.post(
        "/api/v1/public/landing-pages/agentes-ia/capture",
        json={
            "landing_page_slug": "agentes-ia",
            "full_name": "Visitante Sem Consentimento",
            "email": f"nolgpd.{RUN_SUFFIX}@teste.com.br",
            "phone": "+5511988887777",
            "company_name": "Empresa Teste",
            "buy_intent": "HIGH",
            "estimated_value": 5000.0,
            "consent_lgpd": False,
            "data_origin": "TEST",
        },
    )
    assert r_pub_no_lgpd.status_code == 400

    # Captura pública com payload XSS deve sanitizar tags <script> e criar lead
    r_pub_xss = client.post(
        "/api/v1/public/landing-pages/agentes-ia/capture",
        json={
            "landing_page_slug": "agentes-ia",
            "full_name": "Visitante Publico <script>alert(1)</script>",
            "email": f"pub.xss.{RUN_SUFFIX}@teste.com.br",
            "phone": "+5511977776666",
            "company_name": "Corp <script>evil()</script> Ltda",
            "buy_intent": "URGENT",
            "estimated_value": 8500.0,
            "consent_lgpd": True,
            "data_origin": "TEST",
        },
    )
    assert r_pub_xss.status_code == 201
    pub_lead_id = r_pub_xss.json()["lead_id"]
    created_pub_lead = client.get(f"/api/v1/crm/leads/{pub_lead_id}/lgpd-export", headers=h).json()["personal_data"]
    assert "<script>" not in created_pub_lead["full_name"].lower()
    assert "<script>" not in created_pub_lead["company_name"].lower()

    # DEFECT-05: Histórico do Piloto 7 Dias disponível no GET /api/v1/system/pilot-7-days
    r_pilot_hist = client.get("/api/v1/system/pilot-7-days", headers=h)
    assert r_pilot_hist.status_code == 200
    assert "days_simulated" in r_pilot_hist.json()

    # =========================================================================
    # PARTE 2: 15 CENÁRIOS E2E NO TENANT ISOLADO QA_AUTOMATED_TENANT
    # =========================================================================
    r_qa_tenant = client.post(
        "/api/v1/tenants",
        headers=h,
        json={
            "name": "QA_AUTOMATED_TENANT",
            "brand_name": f"QA_AUTOMATED_TENANT_{RUN_SUFFIX}",
            "niche": "Auditoria & QA E2E",
            "primary_color": "#4F46E5",
            "secondary_color": "#10B981",
        },
    )
    assert r_qa_tenant.status_code == 201
    qa_tid = r_qa_tenant.json()["id"]
    qa_h = {**h, "X-Tenant-Id": str(qa_tid)}

    # CENÁRIO 1 & 2 — CAPTAÇÃO DE LEAD + QUALIFICAÇÃO AUTOMÁTICA (Lead Score >= 65)
    r_c1 = client.post(
        "/api/v1/commercial/landing-pages/capture-lead",
        headers=qa_h,
        json={
            "landing_page_slug": "union-tech",
            "full_name": "Roberto Diretor QA",
            "email": f"roberto.qa.{RUN_SUFFIX}@empresaqa.com.br",
            "phone": "+5511991112222",
            "company_name": f"QA Enterprise {RUN_SUFFIX} S.A.",
            "buy_intent": "URGENT",
            "estimated_value": 18000.0,
            "consent_lgpd": True,
            "utm_campaign": "qa_e2e_phase20",
            "data_origin": "TEST",
        },
    )
    assert r_c1.status_code == 201
    c1_data = r_c1.json()
    qa_lead_id = c1_data["lead_id"]
    assert c1_data["lead_score"] >= 65
    assert c1_data["qualification_status"] == "QUALIFIED"
    assert c1_data["funnel_stage"] == "QUALIFICADO"

    # CENÁRIO 3 — CRM COMPLETO (Movimentação de etapas)
    for stage in ("DIAGNOSTICO", "PROPOSTA", "NEGOCIACAO"):
        r_stg = client.put(
            f"/api/v1/crm/leads/{qa_lead_id}/funnel-stage",
            headers=qa_h,
            json={"funnel_stage": stage, "notes": f"Avanço E2E para {stage}"},
        )
        assert r_stg.status_code == 200
        assert r_stg.json()["funnel_stage"] == stage

    # CENÁRIO 4 — CAMPANHA DE MARKETING + COPY + CRIATIVO + CALENDÁRIO EDITORIAL
    r_mkt_camp = client.post(
        "/api/v1/marketing/campaigns",
        headers=qa_h,
        json={
            "name": f"Campanha E2E QA {RUN_SUFFIX}",
            "campaign_type": "ACQUISITION",
            "objective": "LEAD_GENERATION",
            "channel": "LinkedIn & Google",
            "budget_planned": 0.0,
        },
    )
    assert r_mkt_camp.status_code == 201

    r_copy = client.post(
        "/api/v1/copywriter/generate",
        headers=qa_h,
        json={
            "title": f"Copy QA {RUN_SUFFIX}",
            "copy_type": "AD_COPY",
            "framework": "PAS",
            "product_or_offer": "Agentes de IA UNION TECH",
            "target_audience": "CTOs e COOs",
            "key_benefit": "Automatizar triagem comercial 24/7",
        },
    )
    assert r_copy.status_code == 201

    r_cre = client.post(
        "/api/v1/creative/assets/generate",
        headers=qa_h,
        json={
            "title": f"Criativo QA {RUN_SUFFIX}",
            "asset_type": "CAROUSEL",
            "platform": "linkedin",
            "headline_text": "Operação Autônoma com IA",
            "subheadline_text": "Indicadores auditáveis em tempo real",
            "cta_text": "Solicitar Diagnóstico",
        },
    )
    assert r_cre.status_code == 201

    r_cal = client.post(
        "/api/v1/social/calendar",
        headers=qa_h,
        json={
            "title": f"Post Editorial QA {RUN_SUFFIX}",
            "platform": "linkedin",
            "content_format": "POST",
            "caption": "Como eliminar gargalos manuais com IA nativa em Python.",
            "hashtags": ["#IA", "#Automacao"],
            "scheduled_for": "2026-12-01 09:00",
        },
    )
    assert r_cal.status_code == 201

    # CENÁRIO 5 — UNION AI ENGINE HUB (Política FREE_ONLY + Roteamento Gemini + Registro de Custo Zero)
    def mock_gemini_e2e_text(self, model_id, prompt, system_instruction="", temperature=0.4):
        return {
            "text": f"[GEMINI_QA_E2E_OK] Estratégia gerada para: {prompt[:60]}",
            "provider_key": "gemini",
            "model_id": model_id,
            "input_tokens": 25,
            "output_tokens": 45,
            "total_tokens": 70,
            "duration_ms": 35.0,
        }

    monkeypatch.setattr(GeminiProvider, "generate_text", mock_gemini_e2e_text)
    client.post(
        "/api/v1/ai-engine-hub/credentials",
        headers=qa_h,
        json={"provider_key": "gemini", "api_key": "AIzaSyQA_Isolated_Key_1234567890", "is_active": True},
    )
    r_ai_exec = client.post(
        "/api/v1/ai-engine-hub/route-execute",
        headers=qa_h,
        json={"task_type": "campaigns", "required_capability": "text_generation", "prompt": "Campanha E2E QA_AUTOMATED_TENANT"},
    )
    assert r_ai_exec.status_code == 200 and r_ai_exec.json()["ok"] is True
    assert r_ai_exec.json()["cost_classification"] == "VERIFIED_FREE"

    # CENÁRIO 6 — PROPOSTA COMERCIAL + PDF IMPRIMÍVEL (DEFECT-03 via ?access_token=)
    r_prop = client.post(
        "/api/v1/commercial/proposals",
        headers=qa_h,
        json={
            "business_unit_code": "UNION_TECH",
            "lead_id": qa_lead_id,
            "service_code": "SRV_02_AGENTES_IA",
            "client_name": "Roberto Diretor QA",
            "client_company": f"QA Enterprise {RUN_SUFFIX} S.A.",
            "client_email": f"roberto.qa.{RUN_SUFFIX}@empresaqa.com.br",
            "identified_problem": "Triagem manual lenta e falta de qualificação 24/7.",
            "setup_price_brl": 6800.0,
            "monthly_price_brl": 690.0,
            "data_origin": "TEST",
        },
    )
    assert r_prop.status_code == 201
    prop_id = r_prop.json()["id"]
    assert r_prop.json()["status"] == "PENDING_APPROVAL"

    # DEFECT-03 (Endurecido na Fase 20.1): Token em URL DEVE ser rejeitado (401), enquanto header Authorization + X-Tenant-Id retorna 200 sem cache
    r_pdf_url_token_blocked = client.get(f"/api/v1/commercial/proposals/{prop_id}/pdf?access_token={token}&tenant_id={qa_tid}")
    assert r_pdf_url_token_blocked.status_code == 401

    r_pdf_secure = client.get(f"/api/v1/commercial/proposals/{prop_id}/pdf", headers=qa_h)
    assert r_pdf_secure.status_code == 200
    assert "text/html" in r_pdf_secure.headers.get("content-type", "")
    assert "no-store" in r_pdf_secure.headers.get("cache-control", "").lower()
    assert r_pdf_secure.headers.get("referrer-policy") == "no-referrer"

    # CENÁRIO 7 — APROVAÇÃO HUMANA (Bloqueio sem owner_approve=True + Aprovação com owner_approve=True)
    r_prop_block = client.put(
        f"/api/v1/commercial/proposals/{prop_id}/status",
        headers=qa_h,
        json={"status": "SENT", "owner_approve": False},
    )
    assert r_prop_block.status_code == 403

    r_prop_approve = client.put(
        f"/api/v1/commercial/proposals/{prop_id}/status",
        headers=qa_h,
        json={"status": "SENT", "owner_approve": True, "acceptance_evidence": "Aprovado para envio formal pela Diretoria"},
    )
    assert r_prop_approve.status_code == 200
    assert r_prop_approve.json()["status"] == "SENT"
    assert r_prop_approve.json()["owner_approved"] is True

    # CENÁRIO 8 — CONTRATO / ACEITE FORMAL
    r_contract = client.put(
        f"/api/v1/commercial/proposals/{prop_id}/status",
        headers=qa_h,
        json={
            "status": "ACCEPTED",
            "owner_approve": True,
            "acceptance_evidence": "Aceite digital E2E QA_AUTOMATED_TENANT IP 127.0.0.1",
        },
    )
    assert r_contract.status_code == 200
    assert r_contract.json()["status"] == "ACCEPTED"

    # CENÁRIO 9 — COBRANÇA SANDBOX, WEBHOOK HMAC-SHA256, IDEMPOTÊNCIA E ESTORNO
    r_charge = client.post(
        "/api/v1/commercial/payments/charge",
        headers=qa_h,
        json={
            "business_unit_code": "UNION_TECH",
            "proposal_id": prop_id,
            "client_name": "Roberto Diretor QA",
            "client_company": f"QA Enterprise {RUN_SUFFIX} S.A.",
            "client_email": f"roberto.qa.{RUN_SUFFIX}@empresaqa.com.br",
            "amount_brl": 6800.0,
            "payment_method": "PIX",
            "idempotency_key": f"qa-e2e-idem-{RUN_SUFFIX}",
            "sandbox_mode": True,
            "owner_approved": True,
            "data_origin": "TEST",
        },
    )
    assert r_charge.status_code == 201
    charge_obj = r_charge.json()

    r_wh = client.post(
        "/api/v1/commercial/payments/webhook",
        headers=qa_h,
        json={
            "external_reference": charge_obj["external_reference"],
            "provider_payment_id": charge_obj["provider_payment_id"],
            "new_status": "APPROVED",
            "signature": charge_obj["webhook_test_signature_for_approved"],
        },
    )
    assert r_wh.status_code == 200
    wh_obj = r_wh.json()
    assert wh_obj["status"] == "APPROVED"
    assert wh_obj["onboarding_project_id"] is not None
    qa_proj_id = wh_obj["onboarding_project_id"]

    # CENÁRIO 10 & 11 — ONBOARDING AUTOMÁTICO E ENTREGA COM EVIDÊNCIA OBRIGATÓRIA
    r_proj_list = client.get("/api/v1/commercial/delivery-projects", headers=qa_h)
    assert r_proj_list.status_code == 200
    assert any(p["id"] == qa_proj_id for p in r_proj_list.json())

    # Tentar concluir sem evidência deve bloquear com HTTP 400
    r_deliv_blk = client.put(
        f"/api/v1/commercial/delivery-projects/{qa_proj_id}",
        headers=qa_h,
        json={"status": "COMPLETED", "delivery_evidence": ""},
    )
    assert r_deliv_blk.status_code == 400

    # Concluir com evidência auditável
    r_deliv_ok = client.put(
        f"/api/v1/commercial/delivery-projects/{qa_proj_id}",
        headers=qa_h,
        json={
            "completed_checklist_step": "Kickoff e levantamento de requisitos",
            "deliverable_submitted": "Agente de IA configurado e homologado",
            "delivery_evidence": "https://automacao.projetosunion.cloud/evidencia-entrega-qa-fase20",
            "status": "COMPLETED",
            "client_validation_status": "APPROVED_BY_CLIENT",
            "client_validation_notes": "Homologado no teste E2E da Fase 20.",
        },
    )
    assert r_deliv_ok.status_code == 200
    assert r_deliv_ok.json()["status"] == "COMPLETED"
    assert r_deliv_ok.json()["progress_pct"] == 100.0

    # CENÁRIO 12 — FINANCEIRO (Separação estrita entre Receita Real, Simulação/Teste e Estorno nos 5 Buckets)
    r_panel = client.get("/api/v1/commercial/phase18-1-executive-panel", headers=qa_h)
    assert r_panel.status_code == 200
    panel = r_panel.json()
    for bucket in ("REAL", "ESTIMATIVA", "PROJECAO", "META", "SIMULACAO"):
        assert bucket in panel
    assert panel["REAL"]["receita_recebida_confirmada_brl"] == 0.0
    assert panel["SIMULACAO"]["cobrancas_sandbox_total"] >= 1

    # CENÁRIO 13 — PÓS-VENDA / CUSTOMER SUCCESS (NPS)
    r_cs = client.post(
        "/api/v1/customer-success/feedbacks",
        headers=qa_h,
        json={
            "customer_name": f"QA Enterprise {RUN_SUFFIX} S.A.",
            "customer_email": f"roberto.qa.{RUN_SUFFIX}@empresaqa.com.br",
            "nps_score": 10,
            "csat_score": 5,
            "feedback_text": "Entrega impecável e auditável na Fase 20.",
        },
    )
    assert r_cs.status_code == 201
    assert r_cs.json()["churn_risk"] == "LOW"

    # CENÁRIO 14 — DASHBOARD E KPIs (Consistência com o banco de dados do tenant QA)
    r_ov = client.get("/api/v1/dashboard/overview", headers=qa_h)
    assert r_ov.status_code == 200
    ov_data = r_ov.json()
    assert ov_data["tenant"]["name"] == "QA_AUTOMATED_TENANT"

    # CENÁRIO 15 — RELATÓRIO EXECUTIVO E BACKUP
    r_rep = client.get("/api/v1/reports/executive", headers=qa_h)
    assert r_rep.status_code == 200
    r_bkp = client.post("/api/v1/system/backup", headers=h)
    assert r_bkp.status_code == 201
    assert r_bkp.json()["size_bytes"] > 100


def test_45_phase20_1_security_zero_url_tokens_free_only_and_qa_isolation(client: TestClient, monkeypatch):
    """
    FASE 20.1 — Testes de Regressão da Auditoria Independente:
    1. Proibição absoluta de JWT / tenant_id em query strings (AUDIT-20.1-SEC-01).
    2. Bloqueio de probes maliciosos (.php, .env, .git) e rotas /api/* inexistentes em múltiplos métodos (DEFECT-01 + AUDIT-20.1-SEC-02).
    3. Isolamento Multi-Tenant para usuário secundário de outro tenant (não pode acessar Tenant 1 via X-Tenant-Id -> HTTP 403).
    4. Bloqueio estrito FREE_ONLY sem mascaramento por fallback quando provedor pago/desconhecido é solicitado (AUDIT-20.1-AI-01).
    5. Classificação clara de HTTP 402 como QUOTA_OR_BILLING_REQUIRED sem cobrança.
    6. Isolamento de leads TEST/SIMULATION fora do contador REAL de leads em calculate_tenant_financial_kpis (AUDIT-20.1-QA-01).
    7. Exclusão de tenants QA_* do APScheduler de produção (AUDIT-20.1-SCHED-01).
    """
    from app.services.ai_engines_hub import GeminiProvider
    from app.services.automation_scheduler import _is_qa_isolated_tenant

    token = admin_token(client)
    h = _auth_headers(token)

    # 1. Proibição de JWT em query string em qualquer endpoint protegido
    r_qs_jwt = client.get(f"/api/v1/dashboard/overview?access_token={token}")
    assert r_qs_jwt.status_code == 401

    # 2. Rotas /api/* inexistentes (GET, POST, PUT, DELETE) e probes .php/.env -> sempre 404 JSON
    for method, path in [
        ("GET", "/api/v1/nao-existe-20-1"),
        ("GET", "/api/v2/subcaminho/inexistente"),
        ("POST", "/api/v1/nao-existe-20-1"),
        ("DELETE", "/api/v1/nao-existe-20-1"),
        ("GET", "/wp-login.php"),
        ("GET", "/.env"),
        ("GET", "/.git/config"),
    ]:
        resp = client.request(method, path)
        assert resp.status_code == 404, f"{method} {path} retornou {resp.status_code}"
        assert "application/json" in resp.headers.get("content-type", "")

    # 3. Usuário de outro tenant tentando acessar Tenant 1 via X-Tenant-Id -> HTTP 403
    sec_email = f"auditor.tenant2.{RUN_SUFFIX}@empresa2.com.br"
    r_reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": sec_email,
            "password": "StrongAudit#2026!",
            "full_name": "Auditor Segundo Tenant",
            "company_name": f"Empresa Isolada {RUN_SUFFIX}",
            "lgpd_consent": True,
        },
    )
    assert r_reg.status_code == 201
    sec_token = r_reg.json()["access_token"]
    r_bypass = client.get(
        "/api/v1/dashboard/overview",
        headers={"Authorization": f"Bearer {sec_token}", "X-Tenant-Id": "1"},
    )
    assert r_bypass.status_code == 403

    # 4. FREE_ONLY estrito mesmo com allow_fallback=True (não mascara com fallback nem PROVIDER_ERROR)
    for pkey, mid in [
        ("openai", "gpt-4o"),
        ("anthropic", "claude-3-7-sonnet-latest"),
        ("openai_compatible", "custom-openai-model"),
    ]:
        r_blk = client.post(
            "/api/v1/ai-engine-hub/route-execute",
            headers=h,
            json={
                "task_type": "copywriting",
                "required_capability": "text_generation",
                "preferred_provider": pkey,
                "preferred_model": mid,
                "prompt": "Teste bloqueio estrito FREE_ONLY",
            },
        )
        assert r_blk.status_code == 200
        body = r_blk.json()
        assert body["ok"] is False
        assert body["status"] == "BLOCKED_FREE_ONLY", f"{pkey}:{mid} retornou {body}"
        assert body["estimated_cost_brl"] == 0.0

    # 5. Classificação de HTTP 402 como QUOTA_OR_BILLING_REQUIRED (zero cobrança)
    def mock_gemini_402(self, model_id, prompt, system_instruction="", temperature=0.4):
        raise RuntimeError("Cota gratuita esgotada ou faturamento exigido pela Google (HTTP 402 Payment Required).")

    monkeypatch.setattr(GeminiProvider, "generate_text", mock_gemini_402)
    client.post(
        "/api/v1/ai-engine-hub/credentials",
        headers=h,
        json={"provider_key": "gemini", "api_key": "AQ.TestKey402_1234567890", "is_active": True},
    )
    r_402 = client.post(
        "/api/v1/ai-engine-hub/route-execute",
        headers=h,
        json={"task_type": "copywriting", "required_capability": "text_generation", "prompt": "Teste 402"},
    )
    assert r_402.status_code == 200
    assert r_402.json()["ok"] is False
    assert r_402.json()["status"] == "QUOTA_OR_BILLING_REQUIRED"
    assert r_402.json()["estimated_cost_brl"] == 0.0

    # 6. Isolamento de leads TEST fora do contador REAL de leads no Dashboard
    sec_h = {"Authorization": f"Bearer {sec_token}"}
    ov_before = client.get("/api/v1/dashboard/overview", headers=sec_h).json()
    leads_before = next(c["raw_value"] for c in ov_before["metrics_cards"] if c["key"] == "leads")

    r_test_lead = client.post(
        "/api/v1/crm/leads",
        headers=sec_h,
        json={
            "full_name": "Lead QA Isolado",
            "email": f"lead.qa.isolado.{RUN_SUFFIX}@teste.com.br",
            "phone": "+5511999998888",
            "company_name": "Empresa QA",
            "buy_intent": "HIGH",
            "estimated_value": 5000.0,
            "consent_lgpd": True,
            "data_origin": "TEST",
        },
    )
    assert r_test_lead.status_code == 201
    ov_after = client.get("/api/v1/dashboard/overview", headers=sec_h).json()
    leads_after = next(c["raw_value"] for c in ov_after["metrics_cards"] if c["key"] == "leads")
    assert leads_after == leads_before

    # 7. Verificação da função de exclusão de tenants QA_* no scheduler
    class _DummyTenant:
        def __init__(self, name):
            self.name = name

    assert _is_qa_isolated_tenant(_DummyTenant("QA_AUTOMATED_TENANT")) is True
    assert _is_qa_isolated_tenant(_DummyTenant("Union Growth Holding Ltda")) is False










