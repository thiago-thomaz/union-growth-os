import os
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

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


def test_02_default_seed_login_and_dashboard(client: TestClient):
    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth@2026"},
    )
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]

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
            "password": "PasswordA@123",
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
            "password": "PasswordB@123",
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
    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth@2026"},
    )
    token = r_login.json()["access_token"]

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
    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth@2026"},
    )
    token = r_login.json()["access_token"]

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
    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth@2026"},
    )
    token = r_login.json()["access_token"]

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
    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth@2026"},
    )
    token = r_login.json()["access_token"]

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
    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth@2026"},
    )
    token = r_login.json()["access_token"]

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
    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth@2026"},
    )
    token = r_login.json()["access_token"]

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
    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth@2026"},
    )
    token = r_login.json()["access_token"]

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
    assert len(r_int.json()) == 16

    r_bkp = client.post("/api/v1/system/backup", headers=_auth_headers(token))
    assert r_bkp.status_code == 201
    assert r_bkp.json()["size_bytes"] > 100


def test_11_competitor_intelligence_growth_and_customer_success(client: TestClient):
    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth@2026"},
    )
    token = r_login.json()["access_token"]

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
    r_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@projetosunion.cloud", "password": "UnionGrowth@2026"},
    )
    token = r_login.json()["access_token"]

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
        json={"decision": "APPROVE", "confirmation_token": "CONFIRMED_BY_HUMAN"},
    )
    assert r_decide.status_code == 200
    assert r_decide.json()["status"] == "EXECUTED"


def test_13_frontend_static_ui_served(client: TestClient):
    r_home = client.get("/")
    assert r_home.status_code == 200
    assert "UNION GROWTH OS" in r_home.text


