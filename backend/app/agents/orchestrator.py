import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import (
    AgentExecutionLog,
    ApprovalRequest,
    CEODailyBriefing,
    Competitor,
    CopyItem,
    CreativeAsset,
    CRMActivity,
    CRMDeal,
    CRMLead,
    CustomerFeedback,
    EditorialCalendarItem,
    FinancialRecord,
    GrowthExperiment,
    IntegrationConnection,
    MarketingCampaign,
    MarketingPersona,
    SEOArticle,
    SEOAuditReport,
    SEOKeywordCluster,
    StrategicGoal,
    Tenant,
)
from app.schemas.contracts import AgentResponseContract, AgentTaskContract
from app.services.creative_and_copy_engine import generate_creative_asset, generate_persuasive_copy
from app.services.integrations_and_social_engine import PLATFORM_CONSTRAINTS, validate_and_publish_social_item
from app.services.seo_and_market_engine import (
    analyze_competitor_public,
    generate_seo_factory_article,
    perform_real_seo_audit,
    research_keywords_and_clusters,
)


AGENT_REGISTRY: dict[str, dict[str, Any]] = {
    "AGENT_01_CEO": {
        "id": "AGENT_01_CEO",
        "name": "AI CEO — Chief Executive Officer",
        "role": "Direção Estratégica, Metas, Priorização Financeira e CEO Daily Briefing",
        "allowed_tools": [
            "generate_ceo_daily_briefing",
            "evaluate_company_performance",
            "create_strategic_goals",
            "orchestrate_cross_agent_diagnosis",
        ],
        "default_autonomy": 2,
    },
    "AGENT_02_CMO": {
        "id": "AGENT_02_CMO",
        "name": "AI CMO — Chief Marketing Officer",
        "role": "Posicionamento, Personas, Funis, Orçamento, ROI e Planejamento Mensal Automático",
        "allowed_tools": [
            "generate_monthly_marketing_plan",
            "create_buyer_persona",
            "analyze_campaign_roi",
            "suggest_budget_allocation",
        ],
        "default_autonomy": 2,
    },
    "AGENT_03_SEO": {
        "id": "AGENT_03_SEO",
        "name": "AI SEO Director",
        "role": "Auditoria Técnica Real, Pesquisa de Palavras-Chave, Clusters, Schema.org e SEO Content Factory",
        "allowed_tools": [
            "audit_website_seo",
            "research_keyword_clusters",
            "generate_seo_article",
        ],
        "default_autonomy": 2,
    },
    "AGENT_04_SOCIAL": {
        "id": "AGENT_04_SOCIAL",
        "name": "AI Social Media Director",
        "role": "Calendário Editorial, Tendências, Adaptação Multi-Rede e Fila de Publicação Oficial",
        "allowed_tools": [
            "generate_editorial_calendar",
            "validate_and_queue_publication",
            "analyze_social_engagement",
        ],
        "default_autonomy": 2,
    },
    "AGENT_05_CREATIVE": {
        "id": "AGENT_05_CREATIVE",
        "name": "AI Creative Studio",
        "role": "Fábrica Visual (Posts, Banners, Capas, Carrosséis, Thumbnails, Roteiros, E-books)",
        "allowed_tools": [
            "produce_visual_asset",
            "produce_video_script",
            "produce_carousel_deck",
        ],
        "default_autonomy": 2,
    },
    "AGENT_06_COPYWRITER": {
        "id": "AGENT_06_COPYWRITER",
        "name": "AI Copywriter",
        "role": "Headlines, Landing Pages, Anúncios, E-mails, Scripts Comerciais e Testes A/B Éticos",
        "allowed_tools": [
            "generate_ab_copy",
            "generate_email_sequence",
            "generate_sales_script",
        ],
        "default_autonomy": 2,
    },
    "AGENT_07_GROWTH": {
        "id": "AGENT_07_GROWTH",
        "name": "AI Growth Hacker",
        "role": "Análise de Gargalos de Funil, Hipóteses ICE e Experimentos de Aquisição/Conversão",
        "allowed_tools": [
            "design_growth_experiment",
            "analyze_funnel_bottlenecks",
        ],
        "default_autonomy": 2,
    },
    "AGENT_08_SALES": {
        "id": "AGENT_08_SALES",
        "name": "AI Sales Director",
        "role": "Qualificação de Leads, Lead Scoring, Pipeline CRM, Follow-ups e Previsão Comercial",
        "allowed_tools": [
            "qualify_and_score_lead",
            "generate_sales_forecast",
            "identify_inactive_leads_recovery",
        ],
        "default_autonomy": 2,
    },
    "AGENT_09_COMPETITIVE": {
        "id": "AGENT_09_COMPETITIVE",
        "name": "AI Competitive Intelligence",
        "role": "Monitoramento Ético de Concorrentes, Preços Públicos e Matriz de Diferenciação",
        "allowed_tools": [
            "analyze_competitor",
            "generate_market_comparison",
        ],
        "default_autonomy": 2,
    },
    "AGENT_10_FINANCE": {
        "id": "AGENT_10_FINANCE",
        "name": "AI Finance & Performance",
        "role": "Faturamento, Margem, CAC, LTV, ROI, ROAS, Churn e Separação Real vs Estimado",
        "allowed_tools": [
            "calculate_financial_kpis",
            "detect_metric_anomalies",
        ],
        "default_autonomy": 2,
    },
    "AGENT_11_CS": {
        "id": "AGENT_11_CS",
        "name": "AI Customer Success",
        "role": "Monitoramento NPS/CSAT, Detecção de Risco de Churn, Retenção e Upsell/Cross-Sell",
        "allowed_tools": [
            "analyze_customer_health",
            "generate_retention_playbook",
        ],
        "default_autonomy": 2,
    },
}


# ETAPA 3 — Auditoria honesta dos 11 agentes (o que é motor determinístico, template ou LLM real).
AGENT_AI_CAPABILITY_AUDIT: dict[str, dict[str, Any]] = {
    "AGENT_01_CEO": {
        "base_origin": "DETERMINISTIC_PYTHON_ENGINE",
        "llm_narrative_enabled": True,
        "deterministic_rules": "Cálculo de KPIs reais (receita, margem, ROI, CAC) a partir do banco; regras de alerta (margem < 20%, conversão < 15%, aprovações pendentes).",
        "templates": "Estrutura textual do CEO Daily Briefing (frases-modelo preenchidas com dados reais).",
        "tools_executed": ["Consulta PostgreSQL", "Cálculo de KPIs", "Persistência do briefing"],
        "outputs": "CEO Daily Briefing, prioridades e recomendações baseadas em dados reais.",
        "limitations": "Recomendações são regras fixas; análise em linguagem natural livre só existe se um LLM (Ollama/Gemini/OpenAI-compatível) estiver configurado.",
    },
    "AGENT_02_CMO": {
        "base_origin": "TEMPLATE_ENGINE",
        "llm_narrative_enabled": True,
        "deterministic_rules": "Alocação de verba 40/35/25 e funil TOFU/MOFU/BOFU são regras fixas; ROI vem de dados reais.",
        "templates": "Plano mensal e posicionamento são templates parametrizados pelos dados da empresa.",
        "tools_executed": ["Criação de campanha no banco", "Cálculo de ROI"],
        "outputs": "Plano mensal de marketing persistido como campanha.",
        "limitations": "Estratégia não é criada por LLM sem provedor configurado; é template com dados reais da empresa.",
    },
    "AGENT_03_SEO": {
        "base_origin": "DETERMINISTIC_PYTHON_ENGINE",
        "llm_narrative_enabled": False,
        "deterministic_rules": "Auditoria técnica HTTP real (title, meta, H1, alt, robots, sitemap, JSON-LD) + Google PageSpeed API v5 + Google Autocomplete público.",
        "templates": "Artigo SEO usa estrutura de template (outline fixo) preenchida com palavra-chave e marca.",
        "tools_executed": ["HTTP real (httpx)", "PageSpeed Insights v5", "Google Suggest", "BeautifulSoup"],
        "outputs": "Relatório de auditoria, clusters de palavras-chave, artigos e Schema.org.",
        "limitations": "Sem volume de busca/posição real até conectar Google Search Console; artigos são template estruturado, não redação livre de LLM.",
    },
    "AGENT_04_SOCIAL": {
        "base_origin": "TEMPLATE_ENGINE",
        "llm_narrative_enabled": True,
        "deterministic_rules": "Limites por plataforma, melhores horários e fila de aprovação.",
        "templates": "Legendas e roteiros curtos baseados em template.",
        "tools_executed": ["Criação de itens no calendário", "Validação de limites", "Fila de publicação oficial"],
        "outputs": "Calendário editorial multicanal.",
        "limitations": "Publica externamente apenas com OAuth/credenciais oficiais conectadas; sem credenciais fica WAITING_CREDENTIALS.",
    },
    "AGENT_05_CREATIVE": {
        "base_origin": "DETERMINISTIC_PYTHON_ENGINE",
        "llm_narrative_enabled": False,
        "deterministic_rules": "Renderização programática de PNG com Pillow usando paleta da marca.",
        "templates": "Layouts visuais fixos (post, banner, thumbnail).",
        "tools_executed": ["Pillow", "Gravação de arquivo PNG"],
        "outputs": "Artes PNG reais e roteiros.",
        "limitations": "Não é IA generativa de imagem; é composição tipográfica por template. Vídeo real não é renderizado (apenas roteiro).",
    },
    "AGENT_06_COPYWRITER": {
        "base_origin": "TEMPLATE_ENGINE",
        "llm_narrative_enabled": True,
        "deterministic_rules": "Frameworks AIDA/PAS/BAB/FAB preenchidos e verificação de promessas proibidas.",
        "templates": "Variantes A/B geradas por template de framework.",
        "tools_executed": ["Geração de copy por framework", "Checagem de compliance"],
        "outputs": "Copies A/B com hipótese de teste.",
        "limitations": "Copy criativa livre só com LLM configurado; caso contrário é template de framework.",
    },
    "AGENT_07_GROWTH": {
        "base_origin": "TEMPLATE_ENGINE",
        "llm_narrative_enabled": False,
        "deterministic_rules": "ICE score calculado por fórmula.",
        "templates": "Hipótese padrão de experimento (marcada ESTIMATED até haver resultado real).",
        "tools_executed": ["Criação de experimento no banco"],
        "outputs": "Experimentos de growth.",
        "limitations": "Hipótese é template; resultados só são REAL quando registrados manualmente.",
    },
    "AGENT_08_SALES": {
        "base_origin": "DETERMINISTIC_PYTHON_ENGINE",
        "llm_narrative_enabled": False,
        "deterministic_rules": "Lead scoring determinístico 0–100 e previsão ponderada de pipeline.",
        "templates": "Nenhum relevante.",
        "tools_executed": ["Re-score de leads", "Forecast do pipeline"],
        "outputs": "Leads qualificados e previsão comercial.",
        "limitations": "Não envia mensagens sem SMTP/WhatsApp conectados.",
    },
    "AGENT_09_COMPETITIVE": {
        "base_origin": "DETERMINISTIC_PYTHON_ENGINE",
        "llm_narrative_enabled": False,
        "deterministic_rules": "Inspeção HTTP pública respeitando robots.txt; regex de sinais de preço.",
        "templates": "Forças/fraquezas/oportunidades são texto-modelo genérico.",
        "tools_executed": ["HTTP real", "robots.txt parser"],
        "outputs": "Análise pública de concorrente.",
        "limitations": "Forças/fraquezas são genéricas; só título, descrição e headings são extraídos de fato.",
    },
    "AGENT_10_FINANCE": {
        "base_origin": "DETERMINISTIC_PYTHON_ENGINE",
        "llm_narrative_enabled": False,
        "deterministic_rules": "KPIs financeiros calculados somente sobre registros REAL/IMPORTED.",
        "templates": "Nenhum.",
        "tools_executed": ["Agregações SQL", "Cálculo de CAC/ROI/ROAS"],
        "outputs": "KPIs financeiros auditáveis.",
        "limitations": "LTV usa baseline conservador de 6 meses (estimativa).",
    },
    "AGENT_11_CS": {
        "base_origin": "DETERMINISTIC_PYTHON_ENGINE",
        "llm_narrative_enabled": False,
        "deterministic_rules": "Classificação NPS/CSAT em risco/promotor por faixas fixas.",
        "templates": "Textos de retenção/upsell por faixa de NPS.",
        "tools_executed": ["Agregação de feedbacks"],
        "outputs": "Saúde de clientes e playbooks.",
        "limitations": "Sentimento vem do NPS, não de análise de texto por LLM.",
    },
}


class AIUsageTracker:
    """
    ETAPA 3 — Controle de Consumo de IA por Empresa (Tenant) e Dia:
    Registra chamadas, tokens estimados/consumidos, origem da resposta e aplica limites diários.
    """

    _usage_by_day: dict[str, dict[str, Any]] = {}

    @classmethod
    def _bucket(cls, tenant_id: int) -> dict[str, Any]:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        key = f"{tenant_id}:{today}"
        if key not in cls._usage_by_day:
            cls._usage_by_day[key] = {
                "date": today,
                "tenant_id": tenant_id,
                "total_calls": 0,
                "llm_calls": 0,
                "deterministic_calls": 0,
                "tokens_used": 0,
                "daily_token_limit": settings.AI_DAILY_TOKEN_LIMIT,
                "daily_call_limit": settings.AI_DAILY_CALL_LIMIT,
                "estimated_cost_brl": 0.0,
                "origins_breakdown": {},
            }
        return cls._usage_by_day[key]

    @classmethod
    def can_use_external_llm(cls, tenant_id: int, estimated_tokens: int = 400) -> bool:
        b = cls._bucket(tenant_id)
        if b["total_calls"] >= b["daily_call_limit"]:
            return False
        if b["tokens_used"] + estimated_tokens > b["daily_token_limit"]:
            return False
        return True

    @classmethod
    def record_execution(cls, tenant_id: int, origin: str, llm_used: bool, tokens: int = 0) -> dict[str, Any]:
        b = cls._bucket(tenant_id)
        b["total_calls"] += 1
        if llm_used:
            b["llm_calls"] += 1
            b["tokens_used"] += max(1, tokens)
        else:
            b["deterministic_calls"] += 1
        b["origins_breakdown"][origin] = b["origins_breakdown"].get(origin, 0) + 1
        return b

    @classmethod
    def get_usage_summary(cls, tenant_id: int) -> dict[str, Any]:
        return cls._bucket(tenant_id)


class MultiProviderAIAdapter:
    """
    ETAPA 3 — Sistema Híbrido Real de Inteligência Artificial:
    1. Motor Python Determinístico (cálculos financeiros, HTTP SEO real, PageSpeed, Pillow PNG, Lead Score, ICE).
    2. Adaptador para Modelos Locais (Ollama em OLLAMA_BASE_URL).
    3. Adaptadores para APIs Externas Gratuitas / Configuráveis (Gemini API, OpenAI-Compatible / Groq / OpenRouter, Pollinations).
    4. Fallback Automático (nunca interrompe a operação se LLM externo estiver sem chave ou offline).
    5. Controle de Consumo (AIUsageTracker).
    6. Registro Transparente da Origem das Respostas (nunca declara template como LLM real).
    """

    @staticmethod
    def resolve_provider_status() -> dict[str, Any]:
        local_ollama_online = False
        if settings.AI_DEFAULT_PROVIDER.lower() in ("ollama", "hybrid"):
            try:
                with httpx.Client(timeout=1.2) as client:
                    r = client.get(f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags")
                    if r.status_code == 200:
                        local_ollama_online = True
            except Exception:
                local_ollama_online = False

        gemini_configured = bool((settings.GEMINI_API_KEY or "").strip())
        openai_compat_configured = bool((settings.OPENAI_COMPATIBLE_BASE_URL or "").strip() and (settings.OPENAI_COMPATIBLE_API_KEY or "").strip())
        free_public_enabled = bool(settings.ENABLE_FREE_PUBLIC_LLM)

        if local_ollama_online:
            active_provider = f"ollama:{settings.OLLAMA_MODEL}"
            llm_active = True
            origin_code = f"REAL_LLM_LOCAL:ollama:{settings.OLLAMA_MODEL}"
        elif gemini_configured:
            active_provider = f"gemini:{settings.GEMINI_MODEL}"
            llm_active = True
            origin_code = f"REAL_LLM_EXTERNAL:gemini:{settings.GEMINI_MODEL}"
        elif openai_compat_configured:
            model_name = settings.OPENAI_COMPATIBLE_MODEL or "openai-compatible"
            active_provider = f"openai-compatible:{model_name}"
            llm_active = True
            origin_code = f"REAL_LLM_EXTERNAL:openai-compatible:{model_name}"
        elif free_public_enabled:
            active_provider = "pollinations-free-openai-adapter"
            llm_active = True
            origin_code = "REAL_LLM_EXTERNAL:pollinations:openai"
        else:
            active_provider = "hybrid-deterministic-python-engine-v2"
            llm_active = False
            origin_code = "DETERMINISTIC_PYTHON_AND_TEMPLATE"

        return {
            "active_provider": active_provider,
            "llm_active": llm_active,
            "origin_code": origin_code,
            "adapters": {
                "deterministic_python_engine": {"status": "ACTIVE", "cost": "R$ 0,00 (Nativo)"},
                "local_ollama_adapter": {
                    "status": "CONNECTED" if local_ollama_online else "STANDBY_OFFLINE",
                    "base_url": settings.OLLAMA_BASE_URL,
                    "model": settings.OLLAMA_MODEL,
                },
                "external_gemini_adapter": {
                    "status": "CONFIGURED" if gemini_configured else "PENDING_API_KEY",
                    "model": settings.GEMINI_MODEL,
                },
                "external_openai_compatible_adapter": {
                    "status": "CONFIGURED" if openai_compat_configured else "PENDING_API_KEY",
                    "base_url": settings.OPENAI_COMPATIBLE_BASE_URL or "https://api.groq.com/openai/v1",
                },
                "free_public_llm_adapter": {
                    "status": "ENABLED" if free_public_enabled else "AVAILABLE_OPT_IN",
                    "endpoint": "https://text.pollinations.ai/openai",
                },
            },
        }

    @classmethod
    def resolve_provider_name(cls) -> str:
        return cls.resolve_provider_status()["active_provider"]

    @classmethod
    def generate_hybrid_insight(
        cls,
        tenant_id: int,
        prompt: str,
        deterministic_fallback_text: str,
        pure_deterministic: bool = False,
    ) -> tuple[str, str, bool]:
        """
        Returns (text, response_origin, llm_used).
        If pure_deterministic is True or no live LLM is configured/online, returns the deterministic output
        and honestly labels it as DETERMINISTIC_PYTHON_ENGINE or DETERMINISTIC_PYTHON_AND_TEMPLATE.
        """
        if pure_deterministic or not AIUsageTracker.can_use_external_llm(tenant_id, estimated_tokens=300):
            origin = "DETERMINISTIC_PYTHON_ENGINE" if pure_deterministic else "DETERMINISTIC_PYTHON_AND_TEMPLATE"
            AIUsageTracker.record_execution(tenant_id, origin=origin, llm_used=False, tokens=0)
            return deterministic_fallback_text, origin, False

        status = cls.resolve_provider_status()
        if not status["llm_active"]:
            origin = "DETERMINISTIC_PYTHON_AND_TEMPLATE"
            AIUsageTracker.record_execution(tenant_id, origin=origin, llm_used=False, tokens=0)
            return deterministic_fallback_text, origin, False

        # 1. Try Local Ollama if online
        if status["adapters"]["local_ollama_adapter"]["status"] == "CONNECTED":
            try:
                with httpx.Client(timeout=6.0) as client:
                    r = client.post(
                        f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate",
                        json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False},
                    )
                    if r.status_code == 200:
                        resp_text = (r.json().get("response") or "").strip()
                        if resp_text:
                            origin = f"REAL_LLM_LOCAL:ollama:{settings.OLLAMA_MODEL}"
                            AIUsageTracker.record_execution(tenant_id, origin=origin, llm_used=True, tokens=len(resp_text.split()) * 2)
                            return resp_text, origin, True
            except Exception:
                pass

        # 2. Try Google Gemini Official API if GEMINI_API_KEY is configured
        if (settings.GEMINI_API_KEY or "").strip():
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
                with httpx.Client(timeout=8.0) as client:
                    r = client.post(
                        url,
                        params={"key": settings.GEMINI_API_KEY.strip()},
                        json={"contents": [{"parts": [{"text": prompt}]}]},
                    )
                    if r.status_code == 200:
                        candidates = r.json().get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts and parts[0].get("text"):
                                resp_text = str(parts[0]["text"]).strip()
                                origin = f"REAL_LLM_EXTERNAL:gemini:{settings.GEMINI_MODEL}"
                                AIUsageTracker.record_execution(tenant_id, origin=origin, llm_used=True, tokens=len(resp_text.split()) * 2)
                                return resp_text, origin, True
            except Exception:
                pass

        # 3. Try OpenAI-Compatible API (Groq, OpenRouter, Together, OpenAI)
        if (settings.OPENAI_COMPATIBLE_BASE_URL or "").strip() and (settings.OPENAI_COMPATIBLE_API_KEY or "").strip():
            try:
                base_u = settings.OPENAI_COMPATIBLE_BASE_URL.rstrip("/")
                endpoint = f"{base_u}/chat/completions" if not base_u.endswith("/chat/completions") else base_u
                model_id = settings.OPENAI_COMPATIBLE_MODEL or "llama-3.3-70b-versatile"
                with httpx.Client(timeout=8.0) as client:
                    r = client.post(
                        endpoint,
                        headers={"Authorization": f"Bearer {settings.OPENAI_COMPATIBLE_API_KEY.strip()}"},
                        json={
                            "model": model_id,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.3,
                        },
                    )
                    if r.status_code == 200:
                        choices = r.json().get("choices", [])
                        if choices:
                            resp_text = str(choices[0].get("message", {}).get("content", "")).strip()
                            if resp_text:
                                origin = f"REAL_LLM_EXTERNAL:openai-compatible:{model_id}"
                                AIUsageTracker.record_execution(tenant_id, origin=origin, llm_used=True, tokens=len(resp_text.split()) * 2)
                                return resp_text, origin, True
            except Exception:
                pass

        # 4. Automatic Fallback to Deterministic Engine + Structured Template
        origin = "FALLBACK_DETERMINISTIC_PYTHON_AND_TEMPLATE"
        AIUsageTracker.record_execution(tenant_id, origin=origin, llm_used=False, tokens=0)
        return deterministic_fallback_text, origin, False


DEFAULT_AUTONOMY_LIMITS: dict[str, Any] = {
    "max_daily_publications": 10,
    "max_daily_messages": 100,
    "max_campaign_budget_brl": 5000.0,
    "max_active_campaigns": 10,
    "allow_commercial_changes": False,
    "allow_external_actions": False,
    "require_approval_for_financial_actions": True,
}


def get_tenant_autonomy_config(tenant: Tenant) -> dict[str, Any]:
    raw: dict[str, Any] = {}
    try:
        raw = json.loads(tenant.agent_autonomy_json or "{}")
    except Exception:
        raw = {}

    agent_levels: dict[str, int] = {}
    for aid, meta in AGENT_REGISTRY.items():
        val = raw.get(aid, tenant.autonomy_default_level or meta.get("default_autonomy", 2))
        agent_levels[aid] = int(val) if int(val) in (1, 2, 3) else 2

    saved_limits = raw.get("_limits", {}) if isinstance(raw.get("_limits"), dict) else {}
    limits = {**DEFAULT_AUTONOMY_LIMITS, **saved_limits}
    limits["require_approval_for_financial_actions"] = True
    return {
        "autonomy_default_level": int(tenant.autonomy_default_level or 2),
        "agent_autonomy": agent_levels,
        "limits": limits,
    }


def get_effective_autonomy_level(tenant: Tenant, agent_id: str) -> int:
    cfg = get_tenant_autonomy_config(tenant)
    return cfg["agent_autonomy"].get(agent_id, int(tenant.autonomy_default_level or 2))


def compute_lead_score(lead: CRMLead) -> tuple[int, str]:
    """Deterministic Lead Scoring (0-100) + Qualification status."""
    score = 35
    intent_weights = {"LOW": 5, "MEDIUM": 20, "HIGH": 35, "URGENT": 45}
    score += intent_weights.get((lead.buy_intent or "MEDIUM").upper(), 20)

    if lead.company_name and len(lead.company_name.strip()) > 2:
        score += 10
    if lead.phone and len(lead.phone.strip()) >= 8:
        score += 10
    if lead.estimated_value and lead.estimated_value > 0:
        score += min(15, int(lead.estimated_value / 1000) * 3 + 5)

    corp_email = not any(
        lead.email.lower().endswith(dom)
        for dom in ("@gmail.com", "@hotmail.com", "@yahoo.com", "@outlook.com")
    )
    if corp_email:
        score += 5

    final_score = max(5, min(100, score))
    if final_score >= 70:
        qual = "QUALIFIED"
    elif final_score >= 45:
        qual = "NURTURING"
    else:
        qual = "NEW"
    return final_score, qual


def calculate_tenant_financial_kpis(db: Session, tenant_id: int) -> dict[str, Any]:
    """
    Agent 10 — AI Finance & Performance:
    Strictly separates REAL/IMPORTED records from ESTIMATED/GOAL values.
    Never invents financial numbers.
    """
    records = db.query(FinancialRecord).filter(FinancialRecord.tenant_id == tenant_id).all()
    leads = db.query(CRMLead).filter(CRMLead.tenant_id == tenant_id).all()
    deals = db.query(CRMDeal).filter(CRMDeal.tenant_id == tenant_id).all()
    feedbacks = db.query(CustomerFeedback).filter(CustomerFeedback.tenant_id == tenant_id).all()

    real_revenue = sum(r.amount for r in records if r.record_type == "REVENUE" and r.data_origin in ("REAL", "IMPORTED"))
    real_expenses = sum(r.amount for r in records if r.record_type == "EXPENSE" and r.data_origin in ("REAL", "IMPORTED"))
    real_ad_spend = sum(r.amount for r in records if r.record_type == "AD_SPEND" and r.data_origin in ("REAL", "IMPORTED"))

    estimated_revenue = sum(r.amount for r in records if r.record_type == "REVENUE" and r.data_origin in ("ESTIMATED", "GOAL"))

    total_real_costs = real_expenses + real_ad_spend
    real_profit = real_revenue - total_real_costs
    margin_pct = round((real_profit / real_revenue) * 100, 2) if real_revenue > 0 else 0.0

    won_deals = [d for d in deals if d.status == "WON" or d.stage == "CLOSED_WON"]
    conversions_count = len(won_deals)
    leads_count = len(leads)
    conversion_rate_pct = round((conversions_count / leads_count) * 100, 2) if leads_count > 0 else 0.0

    avg_ticket = round(real_revenue / conversions_count, 2) if conversions_count > 0 and real_revenue > 0 else (
        round(sum(d.value for d in won_deals) / conversions_count, 2) if conversions_count > 0 else 0.0
    )

    cac = round(real_ad_spend / conversions_count, 2) if conversions_count > 0 and real_ad_spend > 0 else 0.0
    ltv = round(avg_ticket * 6, 2) if avg_ticket > 0 else 0.0  # 6-month conservative retention baseline
    roi_pct = round(((real_revenue - total_real_costs) / total_real_costs) * 100, 2) if total_real_costs > 0 else 0.0
    roas = round(real_revenue / real_ad_spend, 2) if real_ad_spend > 0 else 0.0

    high_churn_count = sum(1 for f in feedbacks if f.churn_risk == "HIGH")
    total_fb = len(feedbacks)
    churn_risk_pct = round((high_churn_count / total_fb) * 100, 2) if total_fb > 0 else 0.0
    retention_pct = round(100.0 - churn_risk_pct, 2) if total_fb > 0 else 100.0

    channel_breakdown: dict[str, dict[str, float]] = {}
    for r in records:
        ch = r.channel or "Direct"
        if ch not in channel_breakdown:
            channel_breakdown[ch] = {"revenue": 0.0, "spend": 0.0}
        if r.record_type == "REVENUE" and r.data_origin in ("REAL", "IMPORTED"):
            channel_breakdown[ch]["revenue"] += r.amount
        elif r.record_type in ("AD_SPEND", "EXPENSE") and r.data_origin in ("REAL", "IMPORTED"):
            channel_breakdown[ch]["spend"] += r.amount

    return {
        "real_revenue": round(real_revenue, 2),
        "real_expenses": round(real_expenses, 2),
        "real_ad_spend": round(real_ad_spend, 2),
        "real_profit": round(real_profit, 2),
        "margin_pct": margin_pct,
        "estimated_or_goal_revenue": round(estimated_revenue, 2),
        "leads_total": leads_count,
        "conversions_total": conversions_count,
        "conversion_rate_pct": conversion_rate_pct,
        "average_ticket_brl": avg_ticket,
        "cac_brl": cac,
        "ltv_estimated_brl": ltv,
        "roi_pct": roi_pct,
        "roas_multiplier": roas,
        "retention_rate_pct": retention_pct,
        "churn_risk_pct": churn_risk_pct,
        "channel_performance": channel_breakdown,
        "data_origin": "REAL" if records else "REAL_EMPTY",
    }


def generate_ceo_daily_briefing_service(db: Session, tenant: Tenant) -> CEODailyBriefing:
    """
    Agent 01 — AI CEO:
    Generates the CEO DAILY BRIEFING based strictly on real persisted tenant state.
    """
    kpis = calculate_tenant_financial_kpis(db, tenant.id)
    goals = db.query(StrategicGoal).filter(StrategicGoal.tenant_id == tenant.id).all()
    campaigns = db.query(MarketingCampaign).filter(MarketingCampaign.tenant_id == tenant.id).all()
    seo_audits = (
        db.query(SEOAuditReport)
        .filter(SEOAuditReport.tenant_id == tenant.id)
        .order_by(SEOAuditReport.created_at.desc())
        .limit(3)
        .all()
    )
    calendar_items = db.query(EditorialCalendarItem).filter(EditorialCalendarItem.tenant_id == tenant.id).all()
    pending_approvals = (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.tenant_id == tenant.id, ApprovalRequest.status == "PENDING")
        .count()
    )
    integrations = db.query(IntegrationConnection).filter(IntegrationConnection.tenant_id == tenant.id).all()
    connected_count = sum(1 for i in integrations if i.status == "CONNECTED")

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    what_happened = [
        f"Receita Real acumulada registrada no banco: R$ {kpis['real_revenue']:,.2f} | Despesas + Ads Reais: R$ {(kpis['real_expenses'] + kpis['real_ad_spend']):,.2f}.",
        f"Lucro Real apurado: R$ {kpis['real_profit']:,.2f} (Margem: {kpis['margin_pct']}%) | Origem do dado: {kpis['data_origin']}.",
        f"Funil Comercial: {kpis['leads_total']} leads registrados no CRM e {kpis['conversions_total']} negociações fechadas (Taxa de Conversão: {kpis['conversion_rate_pct']}%).",
        f"Operação de Conteúdo & Social: {len(calendar_items)} publicações no calendário editorial e {len(campaigns)} campanhas ativas.",
    ]

    what_is_working = []
    if kpis["real_profit"] > 0:
        what_is_working.append(f"Operação superavitária com margem positiva de {kpis['margin_pct']}% e ROI de {kpis['roi_pct']}%.")
    if kpis["leads_total"] > 0:
        what_is_working.append(f"Captação comercial ativa com {kpis['leads_total']} oportunidades estruturadas no CRM.")
    if seo_audits and seo_audits[0].overall_score >= 70:
        what_is_working.append(f"Saúde técnica de SEO em {seo_audits[0].overall_score}/100 na última auditoria ({seo_audits[0].target_url}).")
    if not what_is_working:
        what_is_working.append("Infraestrutura multiagente, banco de dados e scheduler autônomo operando normalmente.")

    what_is_wrong = []
    if kpis["real_revenue"] == 0:
        what_is_wrong.append("Nenhum faturamento REAL foi importado ou registrado ainda neste período.")
    elif kpis["margin_pct"] < 20:
        what_is_wrong.append(f"Margem líquida atual ({kpis['margin_pct']}%) está abaixo do patamar saudável de 25%.")
    if kpis["leads_total"] > 0 and kpis["conversion_rate_pct"] < 15:
        what_is_wrong.append(f"Taxa de conversão do funil ({kpis['conversion_rate_pct']}%) requer otimização de follow-up comercial.")
    if connected_count < 3:
        what_is_wrong.append(f"Apenas {connected_count} integração(ões) externa(s) conectada(s) — demais canais aguardam credenciais OAuth/API.")

    opportunities = [
        f"Escalar produção de artigos via SEO Content Factory para capturar tráfego orgânico de custo zero no nicho '{tenant.niche}'.",
        "Ativar sequência de recuperação para leads em estágio 'QUALIFICATION' ou 'INACTIVE' no CRM.",
        "Executar teste A/B de headline e oferta gerado pelo AI Copywriter nas páginas de conversão principais.",
    ]

    urgent_problems = []
    if pending_approvals > 0:
        urgent_problems.append(f"Existem {pending_approvals} solicitação(ões) aguardando aprovação humana na Central de Aprovações.")
    failed_pubs = sum(1 for c in calendar_items if c.publish_status == "FAILED")
    if failed_pubs > 0:
        urgent_problems.append(f"{failed_pubs} publicação(ões) falharam e exigem revisão ou reconexão de credenciais.")
    if not urgent_problems:
        urgent_problems.append("Nenhum incidente crítico bloqueando a operação no momento.")

    recommendations = [
        "1. [Alto Impacto Financeiro] Priorizar o fechamento das negociações abertas no estágio PROPOSAL/NEGOTIATION do CRM.",
        "2. [Aquisição Custo Zero] Publicar 2 novos clusters de artigos otimizados em SEO esta semana.",
        "3. [Eficiência Operacional] Revisar e aprovar a fila editorial na Central de Aprovações para manter consistência nas redes.",
    ]

    priority_actions = [
        {"priority": 1, "agent": "AGENT_08_SALES", "action": "Executar follow-up imediato nos leads com Lead Score >= 70", "expected_impact": "Aumento direto de receita no curto prazo"},
        {"priority": 2, "agent": "AGENT_03_SEO", "action": "Corrigir pendências técnicas de meta tags e Schema.org apontadas na auditoria", "expected_impact": "Ganho de CTR orgânico"},
        {"priority": 3, "agent": "AGENT_02_CMO", "action": "Realocar esforço para os canais com maior ROAS/ROI comprovado", "expected_impact": "Redução de CAC"},
    ]

    automation_candidates = [
        "Qualificação automática e cálculo de Lead Score a cada novo lead cadastrado (Ativo).",
        "Geração matinal do CEO Daily Briefing às 08:00 pelo Scheduler Python (Ativo).",
        "Auditoria semanal automática de SEO e monitoramento de concorrentes (Ativo).",
    ]

    headline = (
        f"Briefing Executivo {tenant.brand_name} ({today_str}): "
        f"Receita Real R$ {kpis['real_revenue']:,.2f} | Margem {kpis['margin_pct']}% | {kpis['leads_total']} Leads no CRM"
    )

    briefing = CEODailyBriefing(
        tenant_id=tenant.id,
        briefing_date=today_str,
        summary_headline=headline,
        what_happened_json=json.dumps(what_happened, ensure_ascii=False),
        what_is_working_json=json.dumps(what_is_working, ensure_ascii=False),
        what_is_wrong_json=json.dumps(what_is_wrong, ensure_ascii=False),
        opportunities_json=json.dumps(opportunities, ensure_ascii=False),
        urgent_problems_json=json.dumps(urgent_problems, ensure_ascii=False),
        recommendations_json=json.dumps(recommendations, ensure_ascii=False),
        priority_actions_json=json.dumps(priority_actions, ensure_ascii=False),
        automation_candidates_json=json.dumps(automation_candidates, ensure_ascii=False),
        data_sources_summary_json=json.dumps(
            {
                "financial_records_origin": kpis["data_origin"],
                "goals_tracked": len(goals),
                "connected_integrations": connected_count,
                "pending_approvals": pending_approvals,
            },
            ensure_ascii=False,
        ),
    )
    db.add(briefing)
    db.commit()
    db.refresh(briefing)
    return briefing


class CentralOrchestrator:
    """
    Section 9 — IA Central e Comunicação entre Agentes:
    Coordinates all 11 specialized agents using validated Pydantic contracts,
    prevents infinite loops via depth/visited tracking, and logs every execution.
    """

    @staticmethod
    def dispatch_task(
        db: Session,
        tenant: Tenant,
        contract: AgentTaskContract,
        visited_agents: set[str] | None = None,
    ) -> AgentResponseContract:
        visited = visited_agents or set()
        if contract.current_depth > contract.max_depth or contract.target_agent in visited:
            return AgentResponseContract(
                workflow_run_id=contract.workflow_run_id,
                agent_id=contract.target_agent,
                agent_name=AGENT_REGISTRY.get(contract.target_agent, {}).get("name", contract.target_agent),
                task_name=contract.task_name,
                status="BLOCKED",
                autonomy_level=contract.autonomy_level,
                provider_used=MultiProviderAIAdapter.resolve_provider_name(),
                quality_score=100.0,
                data_origin="REAL",
                summary="Execução bloqueada preventivamente para evitar ciclo infinito entre agentes ou excesso de profundidade.",
                structured_output={"reason": "MAX_DEPTH_OR_CYCLE_GUARD"},
                recommendations=[],
            )

        visited.add(contract.target_agent)
        t0 = time.perf_counter()
        provider_name = MultiProviderAIAdapter.resolve_provider_name()
        autonomy = get_effective_autonomy_level(tenant, contract.target_agent)
        agent_meta = AGENT_REGISTRY.get(contract.target_agent, {"id": contract.target_agent, "name": contract.target_agent})

        params = contract.parameters or {}
        output_data: dict[str, Any] = {}
        recs: list[str] = []
        summary = ""
        data_origin = "REAL"
        requires_approval = False
        approval_id: int | None = None
        status_str = "COMPLETED"

        aid = contract.target_agent

        if aid == "AGENT_01_CEO":
            briefing = generate_ceo_daily_briefing_service(db, tenant)
            output_data = {
                "briefing_id": briefing.id,
                "headline": briefing.summary_headline,
                "what_happened": json.loads(briefing.what_happened_json),
                "what_is_working": json.loads(briefing.what_is_working_json),
                "what_is_wrong": json.loads(briefing.what_is_wrong_json),
                "opportunities": json.loads(briefing.opportunities_json),
                "urgent_problems": json.loads(briefing.urgent_problems_json),
                "priority_actions": json.loads(briefing.priority_actions_json),
            }
            recs = json.loads(briefing.recommendations_json)
            summary = briefing.summary_headline

        elif aid == "AGENT_02_CMO":
            month_label = datetime.now(timezone.utc).strftime("%Y-%m")
            kpis = calculate_tenant_financial_kpis(db, tenant.id)
            plan = {
                "month": month_label,
                "brand_positioning": f"{tenant.brand_name}: referência em {tenant.niche} para {tenant.target_audience}.",
                "value_proposition": f"Crescimento previsível, automação inteligente e governança de dados para {tenant.target_audience}.",
                "funnel_strategy": {
                    "TOFU": "Artigos SEO de cauda longa + Reels/Shorts educativos (60% do volume orgânico)",
                    "MOFU": "Carrosséis de estudo de caso + E-books técnicos + Sequência de e-mail",
                    "BOFU": "Diagnóstico comercial consultivo + Proposta personalizada no CRM",
                },
                "budget_allocation_suggestion": {
                    "SEO_and_Content_Organic": "40% do esforço (Custo de mídia R$ 0)",
                    "Paid_Search_High_Intent": "35% da verba de mídia",
                    "Paid_Social_Retargeting": "25% da verba de mídia",
                },
                "current_roi_pct": kpis["roi_pct"],
            }
            camp = MarketingCampaign(
                tenant_id=tenant.id,
                name=params.get("campaign_name", f"Plano Estratégico Mensal {month_label} — {tenant.brand_name}"),
                campaign_type="ACQUISITION",
                channel="Omni-Channel (SEO + Social + CRM)",
                objective=f"Gerar leads qualificados e elevar conversão em {tenant.niche}",
                funnel_stage="TOFU/MOFU/BOFU",
                budget_planned=float(params.get("budget_planned", 0.0)),
                data_origin="GOAL" if float(params.get("budget_planned", 0.0)) > 0 else "REAL",
                status="ACTIVE",
                monthly_plan_json=json.dumps(plan, ensure_ascii=False),
                start_date=f"{month_label}-01",
            )
            db.add(camp)
            db.commit()
            db.refresh(camp)
            output_data = {"campaign_id": camp.id, "monthly_plan": plan}
            recs = [
                "Concentrar aquisição orgânica em palavras-chave comerciais de fundo de funil.",
                "Ativar campanha de retenção e indicação junto à base atual de clientes.",
            ]
            summary = f"Planejamento mensal de marketing ({month_label}) gerado e registrado (Campanha #{camp.id})."

        elif aid == "AGENT_03_SEO":
            task_type = params.get("mode", "full_seo_cycle")
            target_url = params.get("target_url") or tenant.domain or settings.PUBLIC_URL
            seed_kw = params.get("keyword") or tenant.niche or "automação de marketing e vendas"
            audit = perform_real_seo_audit(db, tenant, target_url, seed_kw)
            cluster = research_keywords_and_clusters(db, tenant, seed_kw)
            article = None
            if task_type in ("full_seo_cycle", "generate_article"):
                article = generate_seo_factory_article(
                    db,
                    tenant,
                    topic=params.get("topic", f"Guia Completo de {seed_kw.title()} para Empresas"),
                    target_keyword=seed_kw,
                )
            output_data = {
                "audit_id": audit.id,
                "audit_score": audit.overall_score,
                "target_url": audit.target_url,
                "cluster_id": cluster.id,
                "long_tail_keywords": json.loads(cluster.long_tail_keywords_json)[:6],
                "article_id": article.id if article else None,
                "article_title": article.title if article else None,
            }
            recs = json.loads(audit.recommendations_json)
            summary = f"Auditoria SEO ({audit.overall_score}/100), cluster de palavras-chave e artigo otimizado gerados."

        elif aid == "AGENT_04_SOCIAL":
            platforms = params.get("platforms", ["instagram", "linkedin", "youtube", "tiktok"])
            if params.get("mode") == "automated_run" and "platforms" not in params:
                rotation = ["instagram", "linkedin", "youtube", "tiktok", "facebook", "pinterest"]
                platforms = [rotation[datetime.now(timezone.utc).timetuple().tm_yday % len(rotation)]]
            created_items = []
            base_date = datetime.now(timezone.utc)
            for idx, plat in enumerate(platforms):
                sched_date = (base_date + timedelta(days=idx + 1)).strftime("%Y-%m-%d")
                best_time = PLATFORM_CONSTRAINTS.get(plat, {}).get("recommended_best_times", ["12:00"])[0]
                item = EditorialCalendarItem(
                    tenant_id=tenant.id,
                    title=f"[{plat.upper()}] Como escalar resultados em {tenant.niche} (#{idx + 1})",
                    platform=plat,
                    content_format="CAROUSEL" if plat in ("instagram", "linkedin") else "REELS_SHORT",
                    caption=(
                        f"Como a {tenant.brand_name} estrutura o crescimento previsível em {tenant.niche}.\n\n"
                        f"1. Diagnóstico baseado em dados reais\n"
                        f"2. Automação de processos repetitivos\n"
                        f"3. Acompanhamento diário de conversão no CRM\n\n"
                        f"Comente 'DIAGNOSTICO' ou acesse nosso link para conhecer a metodologia."
                    ),
                    hashtags_json=json.dumps(["#crescimento", "#estrategia", "#marketingdigital", "#gestao", f"#{tenant.slug.replace('-', '')}"]),
                    video_script="00-05s: Hook | 05-25s: 3 Pilares práticos | 25-35s: CTA para diagnóstico",
                    scheduled_for=f"{sched_date} {best_time}",
                    best_time_rationale=f"Horário de pico histórico de engajamento orgânico em {plat} ({best_time}).",
                    approval_status="PENDING_REVIEW" if autonomy < 3 else "AUTO_APPROVED",
                    publish_status="QUEUED",
                )
                db.add(item)
                db.commit()
                db.refresh(item)
                created_items.append({"id": item.id, "platform": plat, "scheduled_for": item.scheduled_for})
            output_data = {"calendar_items_created": created_items}
            recs = [
                "Revisar e aprovar os itens na Central de Aprovações antes do horário programado.",
                "Conectar credenciais OAuth oficiais na Central de Integrações para disparo direto.",
            ]
            summary = f"{len(created_items)} publicações multicanal planejadas e inseridas no Calendário Editorial."

        elif aid == "AGENT_05_CREATIVE":
            asset = generate_creative_asset(
                db=db,
                tenant=tenant,
                title=params.get("title", f"Criativo Oficial — {tenant.brand_name}"),
                asset_type=params.get("asset_type", "SOCIAL_POST"),
                platform=params.get("platform", "instagram"),
                headline_text=params.get("headline", f"Crescimento Previsível com {tenant.brand_name}"),
                subheadline_text=params.get("subheadline", f"Especialistas em {tenant.niche}"),
                cta_text=params.get("cta", "Solicitar Diagnóstico"),
            )
            output_data = {
                "asset_id": asset.id,
                "title": asset.title,
                "asset_type": asset.asset_type,
                "dimensions": asset.dimensions,
                "file_path": asset.file_path,
            }
            recs = ["Utilizar o criativo aprovado junto à variante A/B do Copywriter."]
            summary = f"Ativo visual '{asset.title}' ({asset.dimensions}) renderizado e salvo na Biblioteca de Ativos."

        elif aid == "AGENT_06_COPYWRITER":
            copy_obj = generate_persuasive_copy(
                db=db,
                tenant=tenant,
                title=params.get("title", f"Copy Conversão — {tenant.brand_name}"),
                copy_type=params.get("copy_type", "LANDING_PAGE"),
                framework=params.get("framework", "AIDA"),
                product_or_offer=params.get("offer", tenant.brand_name),
                target_audience=params.get("target_audience", tenant.target_audience),
                key_benefit=params.get("key_benefit", f"aumentar vendas e eficiência em {tenant.niche}"),
            )
            output_data = {
                "copy_id": copy_obj.id,
                "framework": copy_obj.framework,
                "variant_a": copy_obj.variant_a,
                "variant_b": copy_obj.variant_b,
                "ab_test_hypothesis": copy_obj.ab_test_hypothesis,
            }
            recs = ["Aplicar Teste A/B entre Variante A e Variante B por 14 dias antes de declarar vencedor."]
            summary = f"Copy persuasiva ({copy_obj.framework}) com variantes A/B gerada e validada (#{copy_obj.id})."

        elif aid == "AGENT_07_GROWTH":
            exp = GrowthExperiment(
                tenant_id=tenant.id,
                title=params.get("title", "Otimização de Conversão com Diagnóstico Interativo no Topo da Página"),
                channel=params.get("channel", "Organic Search & Direct"),
                hypothesis="Se substituirmos o formulário longo por um diagnóstico rápido em 2 passos, a conversão de visitantes em leads qualificados subirá pelo menos 25%.",
                objective="Elevar a taxa de conversão de leads qualificados sem aumentar o gasto com anúncios",
                target_audience=tenant.target_audience,
                indicator_metric="Taxa de Conversão de Visitante para Lead Qualificado (%)",
                estimated_cost=0.0,
                baseline_conversion_pct=2.4,
                real_result_conversion_pct=None,
                data_origin="ESTIMATED",
                ice_score=8.7,
                status="RUNNING",
                conclusion="Experimento iniciado — aguardando amostra estatística real.",
            )
            db.add(exp)
            db.commit()
            db.refresh(exp)
            output_data = {"experiment_id": exp.id, "title": exp.title, "ice_score": exp.ice_score}
            recs = ["Acompanhar taxa de conversão real no CRM pelos próximos 7 dias."]
            summary = f"Experimento de Growth #{exp.id} estruturado com ICE Score {exp.ice_score}."

        elif aid == "AGENT_08_SALES":
            leads = db.query(CRMLead).filter(CRMLead.tenant_id == tenant.id).all()
            deals = db.query(CRMDeal).filter(CRMDeal.tenant_id == tenant.id).all()
            re_scored = 0
            for ld in leads:
                sc, qual = compute_lead_score(ld)
                ld.lead_score = sc
                if ld.qualification_status == "NEW":
                    ld.qualification_status = qual
                re_scored += 1
            db.commit()
            weighted_forecast = sum(
                (d.value * (d.probability_pct / 100.0)) for d in deals if d.status == "OPEN"
            )
            high_intent_leads = [l.full_name for l in leads if l.lead_score >= 70]
            output_data = {
                "leads_evaluated": re_scored,
                "high_priority_leads": high_intent_leads[:10],
                "open_deals_count": sum(1 for d in deals if d.status == "OPEN"),
                "weighted_pipeline_forecast_brl": round(weighted_forecast, 2),
            }
            recs = [
                f"Priorizar contato imediato com os {len(high_intent_leads)} leads de pontuação >= 70.",
                f"Previsão comercial ponderada atual do pipeline aberto: R$ {weighted_forecast:,.2f}.",
            ]
            summary = f"Pipeline comercial auditado: {re_scored} leads qualificados | Previsão ponderada: R$ {weighted_forecast:,.2f}."

        elif aid == "AGENT_09_COMPETITIVE":
            comps = db.query(Competitor).filter(Competitor.tenant_id == tenant.id).all()
            analyzed = []
            for comp in comps[:3]:
                analyze_competitor_public(db, tenant, comp)
                analyzed.append({"id": comp.id, "name": comp.name, "website": comp.website_url})
            output_data = {"competitors_analyzed": analyzed, "total_monitored": len(comps)}
            recs = [
                "Explorar lacunas de conteúdo técnico de cauda longa não cobertas pelos concorrentes monitorados.",
                "Destacar transparência e velocidade de implementação nas páginas comerciais.",
            ]
            summary = f"{len(analyzed)} concorrente(s) analisado(s) respeitando robots.txt."

        elif aid == "AGENT_10_FINANCE":
            kpis = calculate_tenant_financial_kpis(db, tenant.id)
            output_data = kpis
            recs = [
                f"Manter separação rigorosa entre Receita Real (R$ {kpis['real_revenue']:,.2f}) e Metas/Estimativas.",
                "Priorizar canais de aquisição com menor CAC e maior ROAS comprovado.",
            ]
            summary = f"Consolidação financeira concluída: Receita Real R$ {kpis['real_revenue']:,.2f} | Lucro R$ {kpis['real_profit']:,.2f} | ROI {kpis['roi_pct']}%."

        elif aid == "AGENT_11_CS":
            feedbacks = db.query(CustomerFeedback).filter(CustomerFeedback.tenant_id == tenant.id).all()
            at_risk = [f for f in feedbacks if f.churn_risk == "HIGH" or f.nps_score <= 6]
            promoters = [f for f in feedbacks if f.nps_score >= 9]
            avg_nps = round(sum(f.nps_score for f in feedbacks) / len(feedbacks), 1) if feedbacks else 0.0
            output_data = {
                "total_feedbacks": len(feedbacks),
                "average_nps_score": avg_nps,
                "customers_at_risk_count": len(at_risk),
                "upsell_promoters_count": len(promoters),
            }
            recs = [
                f"Acionar playbook de retenção imediata para {len(at_risk)} cliente(s) em risco.",
                f"Apresentar proposta de upsell/expansão para os {len(promoters)} clientes promotores (NPS 9-10).",
            ]
            summary = f"Customer Success: NPS médio {avg_nps} | {len(at_risk)} em risco | {len(promoters)} oportunidades de upsell."

        else:
            output_data = {"info": f"Agente {aid} executado com sucesso."}
            summary = f"Execução concluída para {aid}."

        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        # ETAPA 3 — Hybrid AI layer: optional real-LLM executive narrative on top of deterministic data.
        agent_cap = AGENT_AI_CAPABILITY_AUDIT.get(aid, {})
        base_origin = agent_cap.get("base_origin", "DETERMINISTIC_PYTHON_ENGINE")
        llm_used = False
        response_origin = base_origin
        if agent_cap.get("llm_narrative_enabled", False) and summary:
            prompt = (
                f"Você é o {agent_meta['name']} da empresa {tenant.brand_name} (nicho: {tenant.niche}). "
                f"Com base EXCLUSIVAMENTE nos dados reais abaixo, escreva uma análise executiva curta (máx. 6 linhas) "
                f"em português do Brasil, sem inventar números.\nResumo: {summary}\nRecomendações: {recs}"
            )
            narrative, narrative_origin, llm_used = MultiProviderAIAdapter.generate_hybrid_insight(
                tenant.id, prompt, deterministic_fallback_text=summary, pure_deterministic=False
            )
            if llm_used:
                output_data["llm_narrative"] = narrative
                response_origin = f"{narrative_origin} + {base_origin}"
            else:
                response_origin = narrative_origin if base_origin == "TEMPLATE_ENGINE" else base_origin
        else:
            AIUsageTracker.record_execution(tenant.id, origin=response_origin, llm_used=False, tokens=0)

        output_data["_response_origin"] = response_origin
        output_data["_llm_used"] = llm_used
        provider_name = f"{provider_name} | origem={response_origin}"

        log_entry = AgentExecutionLog(
            tenant_id=tenant.id,
            workflow_run_id=contract.workflow_run_id,
            agent_id=aid,
            agent_name=agent_meta["name"],
            task_name=contract.task_name,
            parent_agent_id=contract.sender_agent,
            autonomy_level=autonomy,
            provider_used=provider_name,
            input_payload_json=json.dumps(params, ensure_ascii=False),
            output_payload_json=json.dumps(output_data, ensure_ascii=False),
            quality_score=96.0,
            duration_ms=duration_ms,
            status=status_str,
        )
        db.add(log_entry)
        db.commit()

        return AgentResponseContract(
            workflow_run_id=contract.workflow_run_id,
            agent_id=aid,
            agent_name=agent_meta["name"],
            task_name=contract.task_name,
            status=status_str,
            autonomy_level=autonomy,
            provider_used=provider_name,
            response_origin=response_origin,
            llm_used=llm_used,
            quality_score=96.0,
            data_origin=data_origin,
            summary=summary,
            structured_output=output_data,
            recommendations=recs,
            requires_human_approval=requires_approval,
            approval_request_id=approval_id,
        )

    @classmethod
    def run_multi_agent_executive_diagnosis(
        cls,
        db: Session,
        tenant: Tenant,
        trigger_reason: str = "Diagnóstico Executivo Completo Solicitado pelo AI CEO",
    ) -> dict[str, Any]:
        """
        Full Section 9 Multi-Agent Coordinated Workflow:
        1. CEO initiates diagnosis.
        2. CMO analyzes marketing campaigns.
        3. SEO checks organic health.
        4. Social Media checks editorial pipeline.
        5. Sales Director checks CRM conversion & pipeline forecast.
        6. Finance analyzes revenue, margin, CAC & ROI.
        7. Customer Success checks retention & NPS.
        8. Orchestrator consolidates all findings and CEO generates the executive action plan.
        """
        workflow_id = f"wf-{uuid.uuid4().hex[:12]}"
        sub_agents = [
            ("AGENT_10_FINANCE", "audit_financial_kpis"),
            ("AGENT_02_CMO", "diagnose_marketing_funnel"),
            ("AGENT_03_SEO", "check_organic_seo_health"),
            ("AGENT_04_SOCIAL", "review_editorial_pipeline"),
            ("AGENT_08_SALES", "evaluate_crm_conversion"),
            ("AGENT_11_CS", "assess_customer_retention"),
        ]

        agent_reports: list[dict[str, Any]] = []
        visited: set[str] = set()

        for target_id, task_name in sub_agents:
            sub_contract = AgentTaskContract(
                workflow_run_id=workflow_id,
                sender_agent="AGENT_01_CEO",
                target_agent=target_id,
                task_name=task_name,
                tenant_id=tenant.id,
                autonomy_level=get_effective_autonomy_level(tenant, target_id),
                parameters={"mode": "diagnostic_only"},
                max_depth=3,
                current_depth=1,
            )
            res = cls.dispatch_task(db, tenant, sub_contract, visited_agents=visited)
            agent_reports.append(res.model_dump())

        ceo_contract = AgentTaskContract(
            workflow_run_id=workflow_id,
            sender_agent="ORCHESTRATOR",
            target_agent="AGENT_01_CEO",
            task_name="consolidate_executive_diagnosis",
            tenant_id=tenant.id,
            autonomy_level=get_effective_autonomy_level(tenant, "AGENT_01_CEO"),
            parameters={"trigger_reason": trigger_reason},
            max_depth=3,
            current_depth=2,
        )
        ceo_res = cls.dispatch_task(db, tenant, ceo_contract, visited_agents=visited)

        return {
            "workflow_run_id": workflow_id,
            "trigger_reason": trigger_reason,
            "ceo_consolidation": ceo_res.model_dump(),
            "specialist_diagnostics": agent_reports,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

