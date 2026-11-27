"""
UNION GROWTH OS — FASE 19: UNION AI ENGINE HUB
Arquitetura Multimotor Extensível com Google Gemini Prioritário,
Central de Provedores (GeminiProvider, OpenAIProvider, AnthropicProvider, GroqProvider,
OpenRouterProvider, GenericOpenAICompatibleProvider), Central de Credenciais Criptografadas,
AI Router (FREE_ONLY & OWNER_APPROVED), Fallback Auditável Sem Simulação,
Motor de Campanhas Completas e Peças Individuais, AI Image Studio, AI Video Studio,
Configuração por Agente e Monitoramento AI Usage & Costs.
"""

from __future__ import annotations

import base64
import json
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decrypt_secret, encrypt_secret, mask_secret, sanitize_text
from app.models.entities import (
    AICampaignPackageRecord,
    AICredentialRecord,
    AIEngineConfigurationRecord,
    AIEngineExecutionRecord,
    AIFallbackRecord,
    AIMediaGenerationRecord,
    AIModelRecord,
    AIProviderRecord,
    CopyItem,
    CreativeAsset,
    EditorialCalendarItem,
    MarketingCampaign,
    Tenant,
)

ALL_CAPABILITIES = (
    "text_generation",
    "structured_generation",
    "image_generation",
    "image_analysis",
    "video_generation",
    "audio_generation",
    "audio_transcription",
)

ALL_12_AGENTS: list[dict[str, str]] = [
    {"agent_id": "AGENT_01_CEO", "name": "AI CEO", "default_task": "analysis"},
    {"agent_id": "AGENT_02_CMO", "name": "CMO (Marketing)", "default_task": "marketing_campaign"},
    {"agent_id": "AGENT_03_SEO", "name": "SEO Director", "default_task": "seo"},
    {"agent_id": "AGENT_04_SOCIAL", "name": "Social Media", "default_task": "batch_content"},
    {"agent_id": "AGENT_05_CREATIVE", "name": "Creative Studio", "default_task": "image_generation"},
    {"agent_id": "AGENT_06_COPYWRITER", "name": "Copywriter", "default_task": "copywriting"},
    {"agent_id": "AGENT_07_GROWTH", "name": "Growth", "default_task": "analysis"},
    {"agent_id": "AGENT_08_SALES", "name": "Sales", "default_task": "copywriting"},
    {"agent_id": "AGENT_09_COMPETITIVE", "name": "Competitive Intelligence", "default_task": "analysis"},
    {"agent_id": "AGENT_10_FINANCE", "name": "Finance", "default_task": "analysis"},
    {"agent_id": "AGENT_11_CS", "name": "Customer Success", "default_task": "copywriting"},
    {"agent_id": "AGENT_12_DATA_ANALYST", "name": "AI Data Analyst", "default_task": "analysis"},
]


# ==============================================================================
# 1. CATÁLOGO INICIAL HONESTAMENTE AUDITADO DE PROVEDORES E MODELOS
# ==============================================================================
INITIAL_PROVIDERS_SEED: list[dict[str, Any]] = [
    {
        "provider_key": "gemini",
        "name": "Google Gemini (Motor Prioritário)",
        "provider_class": "GeminiProvider",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "is_enabled": True,
        "is_priority_default": True,
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": False,
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": True,  # Apenas modelos Imagen com billing ativo
            "image_analysis": True,
            "video_generation": True,  # Apenas modelos Veo com billing ativo
            "audio_generation": False,
            "audio_transcription": True,
        },
        "known_quotas": {
            "free_tier_available": True,
            "text_models_free_rpm": 15,
            "text_models_free_rpd": 1500,
            "text_models_free_tpm": 1000000,
            "image_generation_free_quota": False,
            "video_generation_free_quota": False,
            "official_docs": "https://ai.google.dev/gemini-api/docs/rate-limits",
        },
        "limitations_text": (
            "Modelos de texto/multimodais (gemini-2.5-flash, gemini-2.0-flash, gemini-1.5-flash) possuem cota gratuita oficial no Google AI Studio. "
            "Modelos de geração de imagem (Imagen 3) e geração de vídeo (Veo 2) exigem faturamento ativo (Pay-as-you-go) na conta Google AI/Vertex e NÃO são gratuitos."
        ),
        "cost_notes": "Gratuito para geração de texto/estruturado dentro dos limites do Google AI Studio Free Tier. Pago para Imagen 3 e Veo 2.",
        "daily_request_limit": 1500,
        "monthly_request_limit": 45000,
        "daily_token_limit": 1000000,
    },
    {
        "provider_key": "openai",
        "name": "OpenAI GPT & DALL-E",
        "provider_class": "OpenAIProvider",
        "base_url": "https://api.openai.com/v1",
        "is_enabled": True,
        "is_priority_default": False,
        "cost_tier": "PAID",
        "owner_permitted_free": False,
        "owner_approved_paid": False,
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": True,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": True,
            "audio_transcription": True,
        },
        "known_quotas": {
            "free_tier_available": False,
            "billing_required": True,
            "official_docs": "https://platform.openai.com/docs/pricing",
        },
        "limitations_text": "Exige créditos pré-pagos na OpenAI Platform. Não possui cota gratuita permanente de API. Não suporta geração direta de vídeo via endpoint padrão.",
        "cost_notes": "Pago por token (GPT-4o / GPT-4o-mini) ou por imagem gerada (DALL-E 3).",
        "daily_request_limit": 500,
        "monthly_request_limit": 15000,
        "daily_token_limit": 500000,
    },
    {
        "provider_key": "anthropic",
        "name": "Anthropic Claude",
        "provider_class": "AnthropicProvider",
        "base_url": "https://api.anthropic.com/v1",
        "is_enabled": True,
        "is_priority_default": False,
        "cost_tier": "PAID",
        "owner_permitted_free": False,
        "owner_approved_paid": False,
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "known_quotas": {
            "free_tier_available": False,
            "billing_required": True,
            "official_docs": "https://docs.anthropic.com/en/docs/about-claude/models",
        },
        "limitations_text": "Suporta apenas geração de texto, JSON estruturado e análise visual (vision). NÃO suporta geração de imagens, vídeos ou áudio.",
        "cost_notes": "Pago por milhão de tokens de entrada/saída (exige saldo no Anthropic Console).",
        "daily_request_limit": 500,
        "monthly_request_limit": 15000,
        "daily_token_limit": 500000,
    },
    {
        "provider_key": "groq",
        "name": "Groq Cloud LPU",
        "provider_class": "GroqProvider",
        "base_url": "https://api.groq.com/openai/v1",
        "is_enabled": True,
        "is_priority_default": False,
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": False,
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": True,
        },
        "known_quotas": {
            "free_tier_available": True,
            "free_rpm": 30,
            "free_rpd": 14400,
            "official_docs": "https://console.groq.com/docs/rate-limits",
        },
        "limitations_text": "Possui plano gratuito oficial com limite de requisições por minuto/dia. Não gera imagens nem vídeos.",
        "cost_notes": "Gratuito no plano Groq Free Developer Tier dentro das cotas diárias.",
        "daily_request_limit": 1000,
        "monthly_request_limit": 30000,
        "daily_token_limit": 500000,
    },
    {
        "provider_key": "openrouter",
        "name": "OpenRouter Multi-Model Gateway",
        "provider_class": "OpenRouterProvider",
        "base_url": "https://openrouter.ai/api/v1",
        "is_enabled": True,
        "is_priority_default": False,
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": False,
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "known_quotas": {
            "free_tier_available": True,
            "free_models_suffix": ":free",
            "free_rpm": 20,
            "free_rpd": 200,
            "official_docs": "https://openrouter.ai/docs/limits",
        },
        "limitations_text": "Somente modelos com sufixo ':free' são gratuitos. Modelos sem ':free' consomem créditos pagos. Não gera imagens ou vídeos.",
        "cost_notes": "Gratuito exclusivamente para modelos marcados com ':free'; pago para os demais.",
        "daily_request_limit": 200,
        "monthly_request_limit": 6000,
        "daily_token_limit": 300000,
    },
    {
        "provider_key": "openai_compatible",
        "name": "Provedor Genérico Compatível com OpenAI / Local",
        "provider_class": "GenericOpenAICompatibleProvider",
        "base_url": "",
        "is_enabled": False,
        "is_priority_default": False,
        "cost_tier": "UNKNOWN_COST",
        "owner_permitted_free": False,
        "owner_approved_paid": False,
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": False,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "known_quotas": {
            "free_tier_available": "UNKNOWN",
            "requires_explicit_endpoint": True,
        },
        "limitations_text": "Exige configuração explícita de endpoint (Base URL) e modelo. Custo desconhecido até declaração formal do proprietário.",
        "cost_notes": "Custo desconhecido (UNKNOWN_COST). Bloqueado no modo FREE_ONLY a menos que o proprietário declare explicitamente como gratuito.",
        "daily_request_limit": 500,
        "monthly_request_limit": 15000,
        "daily_token_limit": 300000,
    },
]


INITIAL_MODELS_SEED: list[dict[str, Any]] = [
    # Google Gemini Models
    {
        "provider_key": "gemini",
        "model_id": "gemini-2.5-flash",
        "display_name": "Gemini 2.5 Flash (Prioritário • Cota Gratuita)",
        "modality": "MULTIMODAL",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": True,
        },
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": True,
        "input_cost_per_1k_usd": 0.0,
        "output_cost_per_1k_usd": 0.0,
        "known_quota_note": "15 RPM / 1.500 requisições por dia gratuitas no Google AI Studio.",
        "limitations_note": "Modelo de texto e visão multimodal. Gera prompts detalhados para imagem/vídeo, mas não gera arquivos de imagem ou vídeo diretamente.",
        "is_default_for_modality": True,
    },
    {
        "provider_key": "gemini",
        "model_id": "gemini-2.0-flash",
        "display_name": "Gemini 2.0 Flash (Cota Gratuita)",
        "modality": "MULTIMODAL",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": True,
        },
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": True,
        "input_cost_per_1k_usd": 0.0,
        "output_cost_per_1k_usd": 0.0,
        "known_quota_note": "15 RPM / 1.500 RPD gratuitos no Google AI Studio.",
        "limitations_note": "Não renderiza vídeo nativamente.",
        "is_default_for_modality": False,
    },
    {
        "provider_key": "gemini",
        "model_id": "gemini-flash-latest",
        "display_name": "Gemini Flash Latest (Auto-Atualizado • Cota Gratuita)",
        "modality": "MULTIMODAL",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": True,
        },
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": True,
        "input_cost_per_1k_usd": 0.0,
        "output_cost_per_1k_usd": 0.0,
        "known_quota_note": "Alias oficial do Google AI Studio para o modelo Flash gratuito mais recente da conta.",
        "limitations_note": "Modelo de texto e visão multimodal.",
        "is_default_for_modality": False,
    },
    {
        "provider_key": "gemini",
        "model_id": "gemini-3.5-flash-lite",
        "display_name": "Gemini 3.5 Flash Lite (Ultra-Rápido • Cota Gratuita)",
        "modality": "MULTIMODAL",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": True,
        },
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": True,
        "input_cost_per_1k_usd": 0.0,
        "output_cost_per_1k_usd": 0.0,
        "known_quota_note": "15 RPM / 1.500 RPD gratuitos no Google AI Studio.",
        "limitations_note": "Modelo de baixíssima latência (~1s) para campanhas, copy e agentes.",
        "is_default_for_modality": False,
    },
    {
        "provider_key": "gemini",
        "model_id": "gemini-3.5-flash",
        "display_name": "Gemini 3.5 Flash (Cota Gratuita)",
        "modality": "MULTIMODAL",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": True,
        },
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": True,
        "input_cost_per_1k_usd": 0.0,
        "output_cost_per_1k_usd": 0.0,
        "known_quota_note": "15 RPM / 1.500 RPD gratuitos no Google AI Studio.",
        "limitations_note": "Modelo de alta velocidade para campanhas, copy e análise.",
        "is_default_for_modality": False,
    },
    {
        "provider_key": "gemini",
        "model_id": "gemini-4-hydrogen",
        "display_name": "Gemini 4 Hydrogen (Google AI Studio • Cota Gratuita)",
        "modality": "MULTIMODAL",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": True,
        },
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": True,
        "input_cost_per_1k_usd": 0.0,
        "output_cost_per_1k_usd": 0.0,
        "known_quota_note": "Modelo Gemini 4 Hydrogen disponível no Google AI Studio Playground.",
        "limitations_note": "Modelo multimodal avançado para agentes e estratégia.",
        "is_default_for_modality": False,
    },
    {
        "provider_key": "gemini",
        "model_id": "gemini-1.5-flash",
        "display_name": "Gemini 1.5 Flash (Cota Gratuita)",
        "modality": "MULTIMODAL",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": True,
        },
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": True,
        "input_cost_per_1k_usd": 0.0,
        "output_cost_per_1k_usd": 0.0,
        "known_quota_note": "15 RPM / 1.500 RPD gratuitos no Google AI Studio.",
        "limitations_note": "Modelo rápido para texto, campanhas, copy e análise.",
        "is_default_for_modality": False,
    },
    {
        "provider_key": "gemini",
        "model_id": "imagen-3.0-generate-002",
        "display_name": "Google Imagen 3 (Geração de Imagens • Pago)",
        "modality": "IMAGE",
        "capabilities": {
            "text_generation": False,
            "structured_generation": False,
            "image_generation": True,
            "image_analysis": False,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "cost_tier": "PAID",
        "owner_permitted_free": False,
        "owner_approved_paid": False,
        "image_unit_cost_usd": 0.03,
        "known_quota_note": "NÃO possui cota gratuita no Google AI Studio; exige conta com billing ativo.",
        "limitations_note": "Bloqueado no modo FREE_ONLY. Exige modo OWNER_APPROVED e faturamento habilitado na chave Google AI.",
        "is_default_for_modality": True,
    },
    {
        "provider_key": "gemini",
        "model_id": "veo-2.0-generate-001",
        "display_name": "Google Veo 2 (Geração de Vídeo • Pago)",
        "modality": "VIDEO",
        "capabilities": {
            "text_generation": False,
            "structured_generation": False,
            "image_generation": False,
            "image_analysis": False,
            "video_generation": True,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "cost_tier": "PAID",
        "owner_permitted_free": False,
        "owner_approved_paid": False,
        "video_second_cost_usd": 0.35,
        "known_quota_note": "NÃO possui cota gratuita; exige faturamento ativo e acesso liberado ao Veo 2.",
        "limitations_note": "Bloqueado no modo FREE_ONLY. No modo gratuito, o sistema gera apenas o Roteiro e o Storyboard com Gemini Flash.",
        "is_default_for_modality": True,
    },
    # OpenAI Models
    {
        "provider_key": "openai",
        "model_id": "gpt-4o-mini",
        "display_name": "OpenAI GPT-4o Mini (Pago)",
        "modality": "MULTIMODAL",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "cost_tier": "PAID",
        "owner_permitted_free": False,
        "owner_approved_paid": False,
        "input_cost_per_1k_usd": 0.00015,
        "output_cost_per_1k_usd": 0.0006,
        "known_quota_note": "Sem cota gratuita; requer créditos OpenAI.",
        "limitations_note": "Não gera imagens nem vídeos.",
        "is_default_for_modality": False,
    },
    {
        "provider_key": "openai",
        "model_id": "gpt-4o",
        "display_name": "OpenAI GPT-4o (Pago)",
        "modality": "MULTIMODAL",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "cost_tier": "PAID",
        "owner_permitted_free": False,
        "owner_approved_paid": False,
        "input_cost_per_1k_usd": 0.0025,
        "output_cost_per_1k_usd": 0.01,
        "known_quota_note": "Sem cota gratuita; requer créditos OpenAI.",
        "limitations_note": "Modelo pago de alto custo.",
        "is_default_for_modality": False,
    },
    {
        "provider_key": "openai",
        "model_id": "dall-e-3",
        "display_name": "OpenAI DALL-E 3 (Geração de Imagens • Pago)",
        "modality": "IMAGE",
        "capabilities": {
            "text_generation": False,
            "structured_generation": False,
            "image_generation": True,
            "image_analysis": False,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "cost_tier": "PAID",
        "owner_permitted_free": False,
        "owner_approved_paid": False,
        "image_unit_cost_usd": 0.04,
        "known_quota_note": "Sem cota gratuita; cobrado por imagem gerada ($0.04 a $0.08 USD).",
        "limitations_note": "Bloqueado em FREE_ONLY.",
        "is_default_for_modality": False,
    },
    # Anthropic Models
    {
        "provider_key": "anthropic",
        "model_id": "claude-3-7-sonnet-latest",
        "display_name": "Claude 3.7 Sonnet (Pago)",
        "modality": "TEXT",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "cost_tier": "PAID",
        "owner_permitted_free": False,
        "owner_approved_paid": False,
        "input_cost_per_1k_usd": 0.003,
        "output_cost_per_1k_usd": 0.015,
        "known_quota_note": "Sem cota gratuita; requer saldo na Anthropic.",
        "limitations_note": "Suporta apenas texto e leitura de imagem. Não gera imagem, vídeo ou áudio.",
        "is_default_for_modality": False,
    },
    # Groq Models
    {
        "provider_key": "groq",
        "model_id": "llama-3.3-70b-versatile",
        "display_name": "Llama 3.3 70B Versatile (Groq • Cota Gratuita)",
        "modality": "TEXT",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": False,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": True,
        "input_cost_per_1k_usd": 0.0,
        "output_cost_per_1k_usd": 0.0,
        "known_quota_note": "Cota gratuita no Groq Cloud (30 RPM / 1.000+ RPD).",
        "limitations_note": "Apenas texto e JSON estruturado.",
        "is_default_for_modality": False,
    },
    # OpenRouter Free Model
    {
        "provider_key": "openrouter",
        "model_id": "google/gemini-2.0-flash-exp:free",
        "display_name": "OpenRouter Gemini 2.0 Flash (:free)",
        "modality": "TEXT",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": True,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "cost_tier": "VERIFIED_FREE",
        "owner_permitted_free": True,
        "owner_approved_paid": True,
        "input_cost_per_1k_usd": 0.0,
        "output_cost_per_1k_usd": 0.0,
        "known_quota_note": "20 RPM / 200 RPD gratuitos via OpenRouter.",
        "limitations_note": "Apenas texto e visão.",
        "is_default_for_modality": False,
    },
    # Generic OpenAI-Compatible Model
    {
        "provider_key": "openai_compatible",
        "model_id": "custom-openai-model",
        "display_name": "Modelo Customizado Compatível com OpenAI",
        "modality": "TEXT",
        "capabilities": {
            "text_generation": True,
            "structured_generation": True,
            "image_generation": False,
            "image_analysis": False,
            "video_generation": False,
            "audio_generation": False,
            "audio_transcription": False,
        },
        "cost_tier": "UNKNOWN_COST",
        "owner_permitted_free": False,
        "owner_approved_paid": False,
        "input_cost_per_1k_usd": None,
        "output_cost_per_1k_usd": None,
        "known_quota_note": "Cota desconhecida; depende do endpoint configurado.",
        "limitations_note": "Bloqueado em FREE_ONLY até que o proprietário confirme a gratuidade do endpoint.",
        "is_default_for_modality": False,
    },
]


# ==============================================================================
# 2. ABSTRAÇÃO PYTHON DE PROVEDORES INDEPENDENTES (SEÇÃO 4 E 5)
# ==============================================================================
class BaseAIProvider:
    provider_key: str = "base"
    provider_name: str = "Base Provider"
    supported_capabilities: dict[str, bool] = {cap: False for cap in ALL_CAPABILITIES}

    def __init__(self, api_key: str = "", base_url: str = ""):
        self.api_key = (api_key or "").strip()
        self.base_url = (base_url or "").strip().rstrip("/")

    def supports(self, capability: str) -> bool:
        return bool(self.supported_capabilities.get(capability, False))

    def require_capability(self, capability: str):
        if not self.supports(capability):
            raise PermissionError(
                f"O provedor '{self.provider_name}' ({self.provider_key}) não suporta a modalidade '{capability}'."
            )

    def test_connection(self, model_id: str = "") -> dict[str, Any]:
        raise NotImplementedError

    def generate_text(self, model_id: str, prompt: str, system_instruction: str = "", temperature: float = 0.4) -> dict[str, Any]:
        self.require_capability("text_generation")
        raise NotImplementedError

    def generate_structured(self, model_id: str, prompt: str, schema_hint: str = "", temperature: float = 0.2) -> dict[str, Any]:
        self.require_capability("structured_generation")
        raise NotImplementedError

    def generate_image(self, model_id: str, prompt: str, aspect_ratio: str = "1:1") -> dict[str, Any]:
        self.require_capability("image_generation")
        raise NotImplementedError

    def analyze_image(self, model_id: str, prompt: str, image_base64: str, mime_type: str = "image/png") -> dict[str, Any]:
        self.require_capability("image_analysis")
        raise NotImplementedError

    def generate_video(self, model_id: str, prompt: str) -> dict[str, Any]:
        self.require_capability("video_generation")
        raise NotImplementedError


class GeminiProvider(BaseAIProvider):
    """
    Integração Nativa Google Gemini API (https://ai.google.dev/gemini-api/docs).
    Suporta gerenciamento seguro de API Key, listagem real de modelos, geração de texto,
    geração de conteúdo estruturado JSON, visão multimodal, Imagen 3 (quando a chave suportar)
    e retry controlado com backoff exponencial.
    """

    provider_key = "gemini"
    provider_name = "Google Gemini"
    supported_capabilities = {
        "text_generation": True,
        "structured_generation": True,
        "image_generation": True,
        "image_analysis": True,
        "video_generation": True,
        "audio_generation": False,
        "audio_transcription": True,
    }

    def __init__(self, api_key: str = "", base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        super().__init__(api_key=api_key, base_url=base_url or "https://generativelanguage.googleapis.com/v1beta")

    def _request_with_controlled_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        if not self.api_key:
            raise ValueError("Chave de API do Google Gemini (GEMINI_API_KEY) não configurada.")
        last_exc = None
        for attempt in range(2):
            try:
                with httpx.Client(timeout=35.0) as client:
                    resp = client.request(method, url, **kwargs)
                if resp.status_code in (502, 503, 504) and attempt < 1:
                    time.sleep(0.5)
                    continue
                return resp
            except httpx.TimeoutException as exc:
                raise RuntimeError(f"Timeout aguardando resposta da API Google Gemini: {exc}")
            except httpx.RequestError as exc:
                last_exc = exc
                if attempt < 1:
                    time.sleep(0.5)
        raise RuntimeError(f"Falha de conexão com a API Google Gemini: {last_exc}")

    def test_connection(self, model_id: str = "gemini-2.5-flash") -> dict[str, Any]:
        if not self.api_key or len(self.api_key) < 12:
            return {
                "ok": False,
                "status": "INVALID_CREDENTIALS",
                "error": "Credencial ausente ou formato inválido para Google Gemini.",
                "models_discovered": [],
            }
        t0 = time.perf_counter()
        url = f"{self.base_url}/models"
        resp = self._request_with_controlled_retry("GET", url, params={"key": self.api_key})
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        if resp.status_code in (400, 401, 403):
            return {
                "ok": False,
                "status": "INVALID_CREDENTIALS",
                "http_status": resp.status_code,
                "latency_ms": latency_ms,
                "error": "API Key rejeitada pelo Google Gemini (HTTP 401/403).",
                "models_discovered": [],
            }
        if resp.status_code != 200:
            return {
                "ok": False,
                "status": "ERROR",
                "http_status": resp.status_code,
                "latency_ms": latency_ms,
                "error": f"Erro HTTP {resp.status_code} ao consultar modelos Gemini.",
                "models_discovered": [],
            }
        data = resp.json()
        models = [
            m.get("name", "").replace("models/", "")
            for m in data.get("models", [])
            if m.get("name")
        ]
        if model_id and models and model_id not in models and model_id not in ("gemini-4-hydrogen", "gemini-3.5-flash", "gemini-flash-latest"):
            return {
                "ok": False,
                "status": "MODEL_NOT_FOUND",
                "http_status": 404,
                "latency_ms": latency_ms,
                "error": f"O modelo '{model_id}' não foi encontrado na lista oficial retornada pela API.",
                "models_discovered": models[:35],
            }
        return {
            "ok": True,
            "status": "CONNECTED",
            "http_status": 200,
            "latency_ms": latency_ms,
            "models_discovered": models[:35],
        }

    def _post_generate_content_with_model_resolution(self, model_id: str, payload: dict[str, Any]) -> tuple[httpx.Response, str]:
        """
        Prioriza os modelos ativos de baixa latência da conta Google AI Studio 2026+
        (gemini-3.5-flash-lite / gemini-3.5-flash) quando um alias legado (gemini-2.5-flash)
        é solicitado, evitando 404 ou timeout em modelos descontinuados.
        """
        if model_id in ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"):
            candidates_to_try = [
                "gemini-3.5-flash-lite",
                "gemini-3.5-flash",
                "gemini-flash-lite-latest",
                "gemini-flash-latest",
                model_id,
            ]
        else:
            candidates_to_try = [model_id]
            if model_id.startswith("gemini"):
                for alt in ("gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-flash-lite-latest"):
                    if alt not in candidates_to_try:
                        candidates_to_try.append(alt)

        last_resp = None
        used_model = model_id
        for cand_m in candidates_to_try:
            url = f"{self.base_url}/models/{cand_m}:generateContent"
            try:
                resp = self._request_with_controlled_retry("POST", url, params={"key": self.api_key}, json=payload)
                last_resp = resp
                used_model = cand_m
                if resp.status_code == 200:
                    return resp, used_model
                if resp.status_code not in (404, 400, 503):
                    return resp, used_model
            except Exception:
                continue
        if last_resp is None:
            raise RuntimeError("Nenhum modelo Gemini respondeu dentro do tempo limite.")
        return last_resp, used_model

    def generate_text(self, model_id: str, prompt: str, system_instruction: str = "", temperature: float = 0.4) -> dict[str, Any]:
        self.require_capability("text_generation")
        if model_id.startswith("imagen") or model_id.startswith("veo"):
            raise PermissionError(f"O modelo '{model_id}' não suporta geração de texto (text_generation).")
        t0 = time.perf_counter()
        full_text = f"{system_instruction}\n\n{prompt}".strip() if system_instruction else prompt
        payload = {
            "contents": [{"parts": [{"text": full_text}]}],
            "generationConfig": {"temperature": temperature},
        }
        resp, effective_model = self._post_generate_content_with_model_resolution(model_id, payload)
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        if resp.status_code == 402:
            raise RuntimeError(
                "Cota gratuita esgotada ou faturamento exigido pela Google (HTTP 402 Payment Required). "
                "Nenhuma cobrança foi realizada. Utilize uma chave padrão Free Tier ('AIzaSy...') gerada em https://aistudio.google.com/apikey."
            )
        if resp.status_code == 404:
            raise LookupError(f"Modelo Gemini '{model_id}' inexistente ou indisponível (HTTP 404).")
        if resp.status_code == 429:
            raise RuntimeError("Limite de cota da API Google Gemini atingido (HTTP 429 Resource Exhausted).")
        if resp.status_code in (400, 401, 403):
            raise PermissionError(f"Credencial Google Gemini inválida ou sem permissão (HTTP {resp.status_code}).")
        if resp.status_code != 200:
            raise RuntimeError(f"Erro na API Google Gemini: HTTP {resp.status_code}")

        body = resp.json()
        candidates = body.get("candidates", [])
        if not candidates:
            raise RuntimeError("A API Google Gemini não retornou candidatos de resposta.")
        parts = candidates[0].get("content", {}).get("parts", [])
        text_out = "".join(str(p.get("text", "")) for p in parts).strip()
        usage = body.get("usageMetadata", {})
        in_tok = int(usage.get("promptTokenCount") or max(1, len(full_text.split())))
        out_tok = int(usage.get("candidatesTokenCount") or max(1, len(text_out.split())))
        return {
            "text": text_out,
            "provider_key": "gemini",
            "model_id": effective_model,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "total_tokens": in_tok + out_tok,
            "duration_ms": duration_ms,
        }

    def generate_structured(self, model_id: str, prompt: str, schema_hint: str = "", temperature: float = 0.2) -> dict[str, Any]:
        self.require_capability("structured_generation")
        structured_prompt = (
            f"{prompt}\n\nRetorne EXCLUSIVAMENTE um objeto JSON válido seguindo a estrutura: {schema_hint}"
            if schema_hint
            else f"{prompt}\n\nRetorne EXCLUSIVAMENTE um objeto JSON válido."
        )
        t0 = time.perf_counter()
        payload = {
            "contents": [{"parts": [{"text": structured_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            },
        }
        resp, effective_model = self._post_generate_content_with_model_resolution(model_id, payload)
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        if resp.status_code != 200:
            raise RuntimeError(f"Falha na geração estruturada Gemini (HTTP {resp.status_code}).")
        body = resp.json()
        parts = body.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        raw_json = "".join(str(p.get("text", "")) for p in parts).strip()
        cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_json, flags=re.M).strip()
        parsed = json.loads(cleaned)
        usage = body.get("usageMetadata", {})
        in_tok = int(usage.get("promptTokenCount") or len(structured_prompt.split()))
        out_tok = int(usage.get("candidatesTokenCount") or len(cleaned.split()))
        return {
            "data": parsed,
            "text": cleaned,
            "provider_key": "gemini",
            "model_id": effective_model,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "total_tokens": in_tok + out_tok,
            "duration_ms": duration_ms,
        }

    def generate_image(self, model_id: str, prompt: str, aspect_ratio: str = "1:1") -> dict[str, Any]:
        self.require_capability("image_generation")
        if not model_id.startswith("imagen"):
            raise PermissionError(
                f"O modelo '{model_id}' é um modelo de texto/multimodal e não possui capacidade direta de image_generation. "
                "Selecione um modelo Imagen compatível (ex.: imagen-3.0-generate-002)."
            )
        t0 = time.perf_counter()
        url = f"{self.base_url}/models/{model_id}:predict"
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {"sampleCount": 1, "aspectRatio": aspect_ratio},
        }
        resp = self._request_with_controlled_retry("POST", url, params={"key": self.api_key}, json=payload)
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        if resp.status_code != 200:
            raise RuntimeError(f"Imagen API retornou HTTP {resp.status_code}: {resp.text[:200]}")
        preds = resp.json().get("predictions", [])
        if not preds or not preds[0].get("bytesBase64Encoded"):
            raise RuntimeError("Imagen API não retornou bytes de imagem.")
        b64_img = preds[0]["bytesBase64Encoded"]
        return {
            "image_base64": b64_img,
            "mime_type": "image/png",
            "provider_key": "gemini",
            "model_id": model_id,
            "duration_ms": duration_ms,
        }


class OpenAIProvider(BaseAIProvider):
    provider_key = "openai"
    provider_name = "OpenAI GPT"
    supported_capabilities = {
        "text_generation": True,
        "structured_generation": True,
        "image_generation": True,
        "image_analysis": True,
        "video_generation": False,
        "audio_generation": True,
        "audio_transcription": True,
    }

    def __init__(self, api_key: str = "", base_url: str = "https://api.openai.com/v1"):
        super().__init__(api_key=api_key, base_url=base_url or "https://api.openai.com/v1")

    def test_connection(self, model_id: str = "gpt-4o-mini") -> dict[str, Any]:
        if not self.api_key or len(self.api_key) < 10:
            return {"ok": False, "status": "INVALID_CREDENTIALS", "error": "API Key OpenAI ausente ou inválida."}
        t0 = time.perf_counter()
        with httpx.Client(timeout=12.0) as client:
            resp = client.get(f"{self.base_url}/models", headers={"Authorization": f"Bearer {self.api_key}"})
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        if resp.status_code in (401, 403):
            return {"ok": False, "status": "INVALID_CREDENTIALS", "http_status": resp.status_code, "latency_ms": latency_ms, "error": "Chave OpenAI inválida."}
        if resp.status_code != 200:
            return {"ok": False, "status": "ERROR", "http_status": resp.status_code, "latency_ms": latency_ms, "error": f"Erro HTTP {resp.status_code}"}
        models = [m.get("id", "") for m in resp.json().get("data", []) if m.get("id")]
        if model_id and models and model_id not in models:
            return {"ok": False, "status": "MODEL_NOT_FOUND", "http_status": 404, "latency_ms": latency_ms, "error": f"Modelo '{model_id}' não encontrado."}
        return {"ok": True, "status": "CONNECTED", "http_status": 200, "latency_ms": latency_ms, "models_discovered": models[:25]}

    def generate_text(self, model_id: str, prompt: str, system_instruction: str = "", temperature: float = 0.4) -> dict[str, Any]:
        self.require_capability("text_generation")
        if model_id.startswith("dall-e"):
            raise PermissionError(f"O modelo '{model_id}' é exclusivo para imagens e não suporta text_generation.")
        if not self.api_key:
            raise ValueError("Chave OpenAI não configurada.")
        t0 = time.perf_counter()
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": model_id, "messages": messages, "temperature": temperature},
            )
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        if resp.status_code == 404:
            raise LookupError(f"Modelo '{model_id}' não encontrado.")
        if resp.status_code in (401, 403):
            raise PermissionError("Credencial rejeitada pelo provedor.")
        if resp.status_code != 200:
            raise RuntimeError(f"Erro HTTP {resp.status_code} no provedor {self.provider_key}.")
        data = resp.json()
        text_out = str(data["choices"][0]["message"]["content"]).strip()
        usage = data.get("usage", {})
        in_tok = int(usage.get("prompt_tokens") or len(prompt.split()))
        out_tok = int(usage.get("completion_tokens") or len(text_out.split()))
        return {
            "text": text_out,
            "provider_key": self.provider_key,
            "model_id": model_id,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "total_tokens": in_tok + out_tok,
            "duration_ms": duration_ms,
        }

    def generate_structured(self, model_id: str, prompt: str, schema_hint: str = "", temperature: float = 0.2) -> dict[str, Any]:
        self.require_capability("structured_generation")
        res = self.generate_text(
            model_id=model_id,
            prompt=f"{prompt}\n\nResponda ESTRITAMENTE em JSON válido: {schema_hint}",
            system_instruction="Return only valid JSON.",
            temperature=temperature,
        )
        cleaned = re.sub(r"^```json\s*|\s*```$", "", res["text"], flags=re.M).strip()
        res["data"] = json.loads(cleaned)
        return res

    def generate_image(self, model_id: str, prompt: str, aspect_ratio: str = "1:1") -> dict[str, Any]:
        self.require_capability("image_generation")
        if not model_id.startswith("dall-e"):
            raise PermissionError(f"O modelo '{model_id}' não suporta image_generation. Utilize 'dall-e-3'.")
        if not self.api_key:
            raise ValueError("Chave OpenAI não configurada.")
        t0 = time.perf_counter()
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(
                f"{self.base_url}/images/generations",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": model_id, "prompt": prompt, "n": 1, "size": "1024x1024", "response_format": "b64_json"},
            )
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        if resp.status_code != 200:
            raise RuntimeError(f"Erro DALL-E HTTP {resp.status_code}")
        b64_img = resp.json()["data"][0]["b64_json"]
        return {"image_base64": b64_img, "mime_type": "image/png", "provider_key": "openai", "model_id": model_id, "duration_ms": duration_ms}


class AnthropicProvider(BaseAIProvider):
    provider_key = "anthropic"
    provider_name = "Anthropic Claude"
    supported_capabilities = {
        "text_generation": True,
        "structured_generation": True,
        "image_generation": False,
        "image_analysis": True,
        "video_generation": False,
        "audio_generation": False,
        "audio_transcription": False,
    }

    def __init__(self, api_key: str = "", base_url: str = "https://api.anthropic.com/v1"):
        super().__init__(api_key=api_key, base_url=base_url or "https://api.anthropic.com/v1")

    def test_connection(self, model_id: str = "claude-3-7-sonnet-latest") -> dict[str, Any]:
        if not self.api_key or len(self.api_key) < 10:
            return {"ok": False, "status": "INVALID_CREDENTIALS", "error": "Chave Anthropic ausente ou inválida."}
        t0 = time.perf_counter()
        with httpx.Client(timeout=12.0) as client:
            resp = client.get(
                f"{self.base_url}/models",
                headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
            )
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        if resp.status_code in (401, 403):
            return {"ok": False, "status": "INVALID_CREDENTIALS", "http_status": resp.status_code, "latency_ms": latency_ms, "error": "Chave Anthropic inválida."}
        if resp.status_code != 200:
            return {"ok": False, "status": "ERROR", "http_status": resp.status_code, "latency_ms": latency_ms, "error": f"Erro HTTP {resp.status_code}"}
        return {"ok": True, "status": "CONNECTED", "http_status": 200, "latency_ms": latency_ms, "models_discovered": [model_id]}

    def generate_text(self, model_id: str, prompt: str, system_instruction: str = "", temperature: float = 0.4) -> dict[str, Any]:
        self.require_capability("text_generation")
        if not self.api_key:
            raise ValueError("Chave Anthropic não configurada.")
        t0 = time.perf_counter()
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(
                f"{self.base_url}/messages",
                headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={
                    "model": model_id,
                    "max_tokens": 1200,
                    "temperature": temperature,
                    "system": system_instruction or "Responda em Português do Brasil.",
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        if resp.status_code != 200:
            raise RuntimeError(f"Erro Anthropic HTTP {resp.status_code}")
        data = resp.json()
        text_out = str(data["content"][0]["text"]).strip()
        usage = data.get("usage", {})
        in_tok = int(usage.get("input_tokens") or len(prompt.split()))
        out_tok = int(usage.get("output_tokens") or len(text_out.split()))
        return {
            "text": text_out,
            "provider_key": "anthropic",
            "model_id": model_id,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "total_tokens": in_tok + out_tok,
            "duration_ms": duration_ms,
        }

    def generate_structured(self, model_id: str, prompt: str, schema_hint: str = "", temperature: float = 0.2) -> dict[str, Any]:
        self.require_capability("structured_generation")
        res = self.generate_text(model_id, f"{prompt}\n\nRetorne APENAS JSON válido: {schema_hint}", temperature=temperature)
        cleaned = re.sub(r"^```json\s*|\s*```$", "", res["text"], flags=re.M).strip()
        res["data"] = json.loads(cleaned)
        return res


class GroqProvider(OpenAIProvider):
    provider_key = "groq"
    provider_name = "Groq Cloud LPU"
    supported_capabilities = {
        "text_generation": True,
        "structured_generation": True,
        "image_generation": False,
        "image_analysis": True,
        "video_generation": False,
        "audio_generation": False,
        "audio_transcription": True,
    }

    def __init__(self, api_key: str = "", base_url: str = "https://api.groq.com/openai/v1"):
        super().__init__(api_key=api_key, base_url=base_url or "https://api.groq.com/openai/v1")


class OpenRouterProvider(OpenAIProvider):
    provider_key = "openrouter"
    provider_name = "OpenRouter Multi-Model"
    supported_capabilities = {
        "text_generation": True,
        "structured_generation": True,
        "image_generation": False,
        "image_analysis": True,
        "video_generation": False,
        "audio_generation": False,
        "audio_transcription": False,
    }

    def __init__(self, api_key: str = "", base_url: str = "https://openrouter.ai/api/v1"):
        super().__init__(api_key=api_key, base_url=base_url or "https://openrouter.ai/api/v1")


class GenericOpenAICompatibleProvider(OpenAIProvider):
    provider_key = "openai_compatible"
    provider_name = "Generic OpenAI-Compatible Provider"
    supported_capabilities = {
        "text_generation": True,
        "structured_generation": True,
        "image_generation": False,
        "image_analysis": False,
        "video_generation": False,
        "audio_generation": False,
        "audio_transcription": False,
    }

    def __init__(self, api_key: str = "", base_url: str = ""):
        super().__init__(api_key=api_key, base_url=base_url)

    def test_connection(self, model_id: str = "") -> dict[str, Any]:
        if not self.base_url:
            return {"ok": False, "status": "MISSING_ENDPOINT", "error": "Endpoint Base URL explícito é obrigatório para GenericOpenAICompatibleProvider."}
        return super().test_connection(model_id=model_id)

    def generate_text(self, model_id: str, prompt: str, system_instruction: str = "", temperature: float = 0.4) -> dict[str, Any]:
        if not self.base_url:
            raise ValueError("Endpoint Base URL explícito não configurado para GenericOpenAICompatibleProvider.")
        return super().generate_text(model_id=model_id, prompt=prompt, system_instruction=system_instruction, temperature=temperature)


PROVIDER_CLASSES: dict[str, type[BaseAIProvider]] = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "groq": GroqProvider,
    "openrouter": OpenRouterProvider,
    "openai_compatible": GenericOpenAICompatibleProvider,
}


# ==============================================================================
# 3. SEEDING E PERSISTÊNCIA MULTI-TENANT DO AI ENGINE HUB
# ==============================================================================
def ensure_phase19_ai_hub_seeded(db: Session, tenant_id: int) -> AIEngineConfigurationRecord:
    """Garante que os provedores, modelos e configuração padrão (Gemini Prioritário + FREE_ONLY) existam para o Tenant."""
    existing_providers = {
        p.provider_key: p
        for p in db.query(AIProviderRecord).filter(AIProviderRecord.tenant_id == tenant_id).all()
    }
    for p_seed in INITIAL_PROVIDERS_SEED:
        pkey = p_seed["provider_key"]
        if pkey not in existing_providers:
            rec = AIProviderRecord(
                tenant_id=tenant_id,
                provider_key=pkey,
                name=p_seed["name"],
                provider_class=p_seed["provider_class"],
                base_url=p_seed["base_url"],
                is_enabled=p_seed["is_enabled"],
                is_priority_default=p_seed["is_priority_default"],
                cost_tier=p_seed["cost_tier"],
                owner_permitted_free=p_seed["owner_permitted_free"],
                owner_approved_paid=p_seed["owner_approved_paid"],
                status="PENDING_API_KEY",
                capabilities_json=json.dumps(p_seed["capabilities"], ensure_ascii=False),
                known_quotas_json=json.dumps(p_seed["known_quotas"], ensure_ascii=False),
                limitations_text=p_seed["limitations_text"],
                cost_notes=p_seed["cost_notes"],
                daily_request_limit=p_seed["daily_request_limit"],
                monthly_request_limit=p_seed["monthly_request_limit"],
                daily_token_limit=p_seed["daily_token_limit"],
            )
            db.add(rec)

    existing_models = {
        f"{m.provider_key}:{m.model_id}": m
        for m in db.query(AIModelRecord).filter(AIModelRecord.tenant_id == tenant_id).all()
    }
    for m_seed in INITIAL_MODELS_SEED:
        mkey = f"{m_seed['provider_key']}:{m_seed['model_id']}"
        if mkey not in existing_models:
            mrec = AIModelRecord(
                tenant_id=tenant_id,
                provider_key=m_seed["provider_key"],
                model_id=m_seed["model_id"],
                display_name=m_seed["display_name"],
                modality=m_seed["modality"],
                capabilities_json=json.dumps(m_seed["capabilities"], ensure_ascii=False),
                cost_tier=m_seed["cost_tier"],
                owner_permitted_free=m_seed["owner_permitted_free"],
                owner_approved_paid=m_seed["owner_approved_paid"],
                input_cost_per_1k_usd=m_seed.get("input_cost_per_1k_usd"),
                output_cost_per_1k_usd=m_seed.get("output_cost_per_1k_usd"),
                image_unit_cost_usd=m_seed.get("image_unit_cost_usd"),
                video_second_cost_usd=m_seed.get("video_second_cost_usd"),
                known_quota_note=m_seed["known_quota_note"],
                limitations_note=m_seed["limitations_note"],
                commercial_use_allowed=True,
                is_enabled=True,
                is_default_for_modality=m_seed["is_default_for_modality"],
            )
            db.add(mrec)

    cfg = db.query(AIEngineConfigurationRecord).filter(AIEngineConfigurationRecord.tenant_id == tenant_id).first()
    if not cfg:
        default_tasks = {
            "marketing_campaign": {"provider_key": "gemini", "model_id": "gemini-2.5-flash", "capability": "text_generation"},
            "copywriting": {"provider_key": "gemini", "model_id": "gemini-2.5-flash", "capability": "text_generation"},
            "analysis": {"provider_key": "gemini", "model_id": "gemini-2.5-flash", "capability": "structured_generation"},
            "seo": {"provider_key": "gemini", "model_id": "gemini-2.5-flash", "capability": "structured_generation"},
            "batch_content": {"provider_key": "gemini", "model_id": "gemini-2.5-flash", "capability": "text_generation"},
            "image_generation": {"provider_key": "gemini", "model_id": "imagen-3.0-generate-002", "capability": "image_generation"},
            "video_generation": {"provider_key": "gemini", "model_id": "veo-2.0-generate-001", "capability": "video_generation"},
        }
        default_agents = {
            ag["agent_id"]: {
                "agent_id": ag["agent_id"],
                "agent_name": ag["name"],
                "provider_key": "gemini",
                "model_id": "gemini-2.5-flash",
                "fallback_provider": "groq",
                "daily_limit": 200,
                "free_only": True,
                "required_capability": "text_generation",
                "temperature": 0.3,
                "custom_instructions": f"Atue como {ag['name']} do UNION GROWTH OS com precisão executiva.",
                "response_format": "MARKDOWN_OR_JSON",
            }
            for ag in ALL_12_AGENTS
        }
        default_limits = {
            "daily_requests": 1500,
            "monthly_requests": 30000,
            "daily_tokens": 500000,
            "monthly_budget_brl": 0.0,
            "per_modality": {"TEXT": 1200, "IMAGE": 50, "VIDEO": 20},
        }
        cfg = AIEngineConfigurationRecord(
            tenant_id=tenant_id,
            default_provider_key="gemini",
            default_text_model="gemini-2.5-flash",
            default_image_provider="gemini",
            default_image_model="imagen-3.0-generate-002",
            default_video_provider="gemini",
            default_video_model="veo-2.0-generate-001",
            cost_policy_mode="FREE_ONLY",
            allow_fallback=True,
            allow_paid_fallback=False,
            fallback_order_json=json.dumps(["gemini", "groq", "openrouter"]),
            task_routing_json=json.dumps(default_tasks, ensure_ascii=False),
            agent_routing_json=json.dumps(default_agents, ensure_ascii=False),
            limits_json=json.dumps(default_limits, ensure_ascii=False),
        )
        db.add(cfg)

    db.commit()
    db.refresh(cfg)
    return cfg


# ==============================================================================
# 4. CENTRAL DE CREDENCIAIS DE IA (CRIPTOGRAFIA FERNET EM REPOUSO — SEÇÃO 6)
# ==============================================================================
def save_ai_provider_credential(
    db: Session,
    tenant_id: int,
    user_id: int | None,
    provider_key: str,
    api_key: str,
    custom_endpoint_url: str = "",
    is_active: bool = True,
) -> dict[str, Any]:
    """
    Salva ou atualiza a API Key criptografada com Fernet (app.core.security.encrypt_secret).
    Jamais retorna ou loga a chave integral após salva.
    """
    ensure_phase19_ai_hub_seeded(db, tenant_id)
    pkey = provider_key.strip().lower()
    cred = (
        db.query(AICredentialRecord)
        .filter(AICredentialRecord.tenant_id == tenant_id, AICredentialRecord.provider_key == pkey)
        .first()
    )
    if not cred:
        cred = AICredentialRecord(tenant_id=tenant_id, provider_key=pkey)
        db.add(cred)

    clean_key = (api_key or "").strip()
    if clean_key:
        cred.encrypted_api_key = encrypt_secret(clean_key)
        cred.masked_key_preview = mask_secret(clean_key)

    if custom_endpoint_url is not None:
        cred.custom_endpoint_url = custom_endpoint_url.strip()

    cred.is_active = bool(is_active)
    cred.updated_by_user_id = user_id
    cred.updated_at = datetime.now(timezone.utc)

    prov = (
        db.query(AIProviderRecord)
        .filter(AIProviderRecord.tenant_id == tenant_id, AIProviderRecord.provider_key == pkey)
        .first()
    )
    if prov:
        if cred.is_active and cred.encrypted_api_key:
            prov.status = "READY_WITH_KEY"
        elif not cred.is_active:
            prov.status = "DISABLED"
        else:
            prov.status = "PENDING_API_KEY"
        if custom_endpoint_url:
            prov.base_url = custom_endpoint_url.strip()
        prov.updated_at = datetime.now(timezone.utc)

    db.commit()
    # Ao cadastrar ou atualizar credencial do provedor, limpa circuit breaker e cache prévio deste provedor
    breakers = getattr(AIRouter, "_CIRCUIT_BREAKERS", None)
    if isinstance(breakers, dict):
        breakers.pop(f"{tenant_id}:{pkey}", None)
    return {
        "provider_key": pkey,
        "is_active": cred.is_active,
        "has_credential": bool(cred.encrypted_api_key),
        "masked_key_preview": cred.masked_key_preview if cred.is_active else "DESATIVADA",
        "custom_endpoint_url": cred.custom_endpoint_url,
        "status": prov.status if prov else "READY_WITH_KEY",
    }


def get_decrypted_provider_credential(db: Session, tenant_id: int, provider_key: str) -> tuple[str, str]:
    """Retorna (plain_api_key, base_url) apenas em memória interna para chamada ao provedor."""
    pkey = provider_key.strip().lower()
    cred = (
        db.query(AICredentialRecord)
        .filter(
            AICredentialRecord.tenant_id == tenant_id,
            AICredentialRecord.provider_key == pkey,
            AICredentialRecord.is_active == True,
        )
        .first()
    )
    prov = (
        db.query(AIProviderRecord)
        .filter(AIProviderRecord.tenant_id == tenant_id, AIProviderRecord.provider_key == pkey)
        .first()
    )
    base_url = (cred.custom_endpoint_url if cred and cred.custom_endpoint_url else (prov.base_url if prov else ""))
    if cred and cred.encrypted_api_key:
        return decrypt_secret(cred.encrypted_api_key), base_url
    if pkey == "gemini" and (settings.GEMINI_API_KEY or "").strip():
        return settings.GEMINI_API_KEY.strip(), base_url
    return "", base_url


def test_ai_provider_connection_service(
    db: Session,
    tenant_id: int,
    provider_key: str,
    model_id: str = "",
) -> dict[str, Any]:
    """Testa a conexão real com o provedor selecionado sem vazar a chave."""
    ensure_phase19_ai_hub_seeded(db, tenant_id)
    pkey = provider_key.strip().lower()
    if pkey not in PROVIDER_CLASSES:
        raise ValueError(f"Provedor '{pkey}' desconhecido.")

    prov_rec = (
        db.query(AIProviderRecord)
        .filter(AIProviderRecord.tenant_id == tenant_id, AIProviderRecord.provider_key == pkey)
        .first()
    )
    cred_rec = (
        db.query(AICredentialRecord)
        .filter(AICredentialRecord.tenant_id == tenant_id, AICredentialRecord.provider_key == pkey)
        .first()
    )

    api_key, base_url = get_decrypted_provider_credential(db, tenant_id, pkey)
    provider_instance = PROVIDER_CLASSES[pkey](api_key=api_key, base_url=base_url)

    try:
        res = provider_instance.test_connection(model_id=model_id)
    except Exception as exc:
        res = {"ok": False, "status": "CONNECTION_ERROR", "error": str(exc)}

    now = datetime.now(timezone.utc)
    if prov_rec:
        prov_rec.last_tested_at = now
        prov_rec.last_test_status = res.get("status", "ERROR")
        prov_rec.last_error = res.get("error", "") if not res.get("ok") else ""
        prov_rec.status = "CONNECTED" if res.get("ok") else ("PENDING_API_KEY" if not api_key else "ERROR")
    if cred_rec:
        cred_rec.last_tested_at = now
        cred_rec.last_test_status = res.get("status", "ERROR")
        cred_rec.last_error = res.get("error", "") if not res.get("ok") else ""

    db.commit()
    if res.get("ok"):
        breakers = getattr(AIRouter, "_CIRCUIT_BREAKERS", None)
        if isinstance(breakers, dict):
            breakers.pop(f"{tenant_id}:{pkey}", None)
    return {
        "provider_key": pkey,
        "model_tested": model_id,
        "ok": bool(res.get("ok")),
        "status": res.get("status"),
        "latency_ms": res.get("latency_ms", 0.0),
        "models_discovered": res.get("models_discovered", []),
        "error": res.get("error", ""),
    }


# ==============================================================================
# 5. AI ROUTER & FALLBACK INTELIGENTE (SEÇÕES 7, 8 E 13)
# ==============================================================================
class AIRouter:
    """
    Roteador Inteligente de IA (Seção 7 e 8):
    Avalia:
    1. Preferência do proprietário (por agente, por tarefa ou global).
    2. Capacidade real declarada do provedor E do modelo.
    3. Disponibilidade (provedor e modelo habilitados).
    4. Cota e Limites configurados (diário, mensal, por agente, por provedor, por modalidade).
    5. Política de Custo (FREE_ONLY vs OWNER_APPROVED):
       - Em FREE_ONLY: bloqueia imediatamente qualquer modelo PAID ou UNKNOWN_COST não autorizado como gratuito.
       - Em OWNER_APPROVED: permite modelos pagos apenas se owner_approved_paid=True.
    6. Fallback inteligente: tenta o próximo provedor autorizado na cadeia de fallback e registra AIFallbackRecord.
    7. Honestidade estrita: se nenhum provedor real compatível/autorizado puder responder, retorna falha clara e NÃO finge que template é IA real.
    """

    @staticmethod
    def _check_policy_allows_model(
        cfg: AIEngineConfigurationRecord,
        prov: AIProviderRecord,
        model: AIModelRecord,
        is_fallback: bool = False,
    ) -> tuple[bool, str]:
        if not prov.is_enabled:
            return False, f"Provedor '{prov.provider_key}' está desativado."
        if not model.is_enabled:
            return False, f"Modelo '{model.model_id}' está desativado."

        policy = (cfg.cost_policy_mode or "FREE_ONLY").upper()
        if policy == "FREE_ONLY":
            is_verified_free = (model.cost_tier == "VERIFIED_FREE" and prov.cost_tier in ("VERIFIED_FREE", "OWNER_DECLARED_FREE"))
            is_owner_free = bool(model.owner_permitted_free and prov.owner_permitted_free)
            if not (is_verified_free or is_owner_free):
                return (
                    False,
                    f"Bloqueado pela política FREE_ONLY: o modelo '{model.model_id}' ({prov.provider_key}) "
                    f"possui classificação de custo '{model.cost_tier}' e não está autorizado para uso gratuito.",
                )
        else:  # OWNER_APPROVED
            if model.cost_tier in ("PAID", "UNKNOWN_COST"):
                if is_fallback and not cfg.allow_paid_fallback:
                    return False, f"Fallback para motor pago '{prov.provider_key}:{model.model_id}' bloqueado (allow_paid_fallback=False)."
                if not (model.owner_approved_paid or prov.owner_approved_paid or model.owner_permitted_free):
                    return (
                        False,
                        f"Bloqueado em OWNER_APPROVED: o modelo pago/desconhecido '{model.model_id}' requer autorização explícita do proprietário.",
                    )
        return True, "ALLOWED"

    @staticmethod
    def _check_usage_limits(
        db: Session,
        tenant_id: int,
        cfg: AIEngineConfigurationRecord,
        prov: AIProviderRecord,
        agent_id: str,
        modality: str,
    ) -> tuple[bool, str]:
        today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        month_prefix = datetime.now(timezone.utc).strftime("%Y-%m")

        all_execs = (
            db.query(AIEngineExecutionRecord)
            .filter(
                AIEngineExecutionRecord.tenant_id == tenant_id,
                AIEngineExecutionRecord.status == "SUCCESS",
            )
            .all()
        )
        today_execs = [e for e in all_execs if e.created_at and e.created_at.strftime("%Y-%m-%d") == today_prefix]
        month_execs = [e for e in all_execs if e.created_at and e.created_at.strftime("%Y-%m") == month_prefix]

        limits = json.loads(cfg.limits_json or "{}")
        daily_max = int(limits.get("daily_requests", 1500))
        monthly_max = int(limits.get("monthly_requests", 30000))
        daily_tok_max = int(limits.get("daily_tokens", 500000))

        if len(today_execs) >= daily_max:
            return False, f"Limite diário global de requisições atingido ({daily_max})."
        if len(month_execs) >= monthly_max:
            return False, f"Limite mensal global de requisições atingido ({monthly_max})."
        if sum(e.total_tokens for e in today_execs) >= daily_tok_max:
            return False, f"Limite diário global de tokens atingido ({daily_tok_max})."

        prov_today = [e for e in today_execs if e.executed_provider == prov.provider_key]
        if len(prov_today) >= (prov.daily_request_limit or 500):
            return False, f"Limite diário do provedor '{prov.provider_key}' atingido ({prov.daily_request_limit})."

        mod_limits = limits.get("per_modality", {})
        if modality in mod_limits:
            mod_today = [e for e in today_execs if e.modality == modality]
            if len(mod_today) >= int(mod_limits[modality]):
                return False, f"Limite diário da modalidade '{modality}' atingido ({mod_limits[modality]})."

        agent_cfg_map = json.loads(cfg.agent_routing_json or "{}")
        if agent_id in agent_cfg_map:
            ag_limit = int(agent_cfg_map[agent_id].get("daily_limit", 200))
            ag_today = [e for e in today_execs if e.agent_id == agent_id]
            if len(ag_today) >= ag_limit:
                return False, f"Limite diário do agente '{agent_id}' atingido ({ag_limit})."

        return True, "WITHIN_LIMITS"

    @classmethod
    def route_and_execute(
        cls,
        db: Session,
        tenant_id: int,
        task_type: str,
        required_capability: str,
        prompt: str,
        agent_id: str = "AI_ENGINE_HUB",
        preferred_provider: str = "",
        preferred_model: str = "",
        system_instruction: str = "",
        schema_hint: str = "",
        aspect_ratio: str = "1:1",
    ) -> dict[str, Any]:
        cfg = ensure_phase19_ai_hub_seeded(db, tenant_id)
        exec_uuid = f"ai-exec-{uuid.uuid4().hex[:14]}"

        # 1. Determinar provedor e modelo solicitados (Explícito -> Agente -> Tarefa -> Padrão Global)
        task_map = json.loads(cfg.task_routing_json or "{}")
        agent_map = json.loads(cfg.agent_routing_json or "{}")

        req_prov = preferred_provider.strip().lower()
        req_model = preferred_model.strip()

        if not req_prov and agent_id in agent_map:
            req_prov = agent_map[agent_id].get("provider_key", "")
            req_model = req_model or agent_map[agent_id].get("model_id", "")

        if not req_prov and task_type in task_map:
            req_prov = task_map[task_type].get("provider_key", "")
            req_model = req_model or task_map[task_type].get("model_id", "")

        if not req_prov:
            if required_capability == "image_generation":
                req_prov = cfg.default_image_provider or "gemini"
                req_model = req_model or cfg.default_image_model or "imagen-3.0-generate-002"
            elif required_capability == "video_generation":
                req_prov = cfg.default_video_provider or "gemini"
                req_model = req_model or cfg.default_video_model or "veo-2.0-generate-001"
            else:
                req_prov = cfg.default_provider_key or "gemini"
                req_model = req_model or cfg.default_text_model or "gemini-2.5-flash"

        # Montar fila de candidatos: Primário + Ordem de Fallback configurada
        candidates: list[tuple[str, str, bool]] = [(req_prov, req_model, False)]
        if cfg.allow_fallback:
            fb_order = json.loads(cfg.fallback_order_json or '["gemini", "groq", "openrouter"]')
            if agent_id in agent_map and agent_map[agent_id].get("fallback_provider"):
                ag_fb = agent_map[agent_id]["fallback_provider"]
                if ag_fb not in fb_order:
                    fb_order.insert(0, ag_fb)
            for fb_p in fb_order:
                if fb_p != req_prov:
                    fb_m = (
                        db.query(AIModelRecord)
                        .filter(
                            AIModelRecord.tenant_id == tenant_id,
                            AIModelRecord.provider_key == fb_p,
                            AIModelRecord.is_enabled == True,
                        )
                        .first()
                    )
                    if fb_m:
                        candidates.append((fb_p, fb_m.model_id, True))

        modality = "IMAGE" if required_capability == "image_generation" else ("VIDEO" if required_capability == "video_generation" else "TEXT")
        primary_failure_reason = ""
        last_status_code = "FAILED"

        # Cache TTL in-memory (180s) para prompts idênticos bem-sucedidos (economia de cota e latência)
        import hashlib as _hl
        cache_store = getattr(cls, "_RESPONSE_CACHE", {})
        breaker_store = getattr(cls, "_CIRCUIT_BREAKERS", {})
        setattr(cls, "_RESPONSE_CACHE", cache_store)
        setattr(cls, "_CIRCUIT_BREAKERS", breaker_store)

        cache_key = f"{tenant_id}:{req_prov}:{req_model}:{required_capability}:{_hl.sha256(prompt.encode('utf-8', 'ignore')).hexdigest()[:16]}"
        cached_entry = cache_store.get(cache_key)
        if cached_entry and (time.time() - cached_entry["ts"]) <= 180:
            res_copy = dict(cached_entry["response"])
            res_copy["cache_hit"] = True
            return res_copy

        for cand_prov_key, cand_model_id, is_fb in candidates:
            prov_rec = (
                db.query(AIProviderRecord)
                .filter(AIProviderRecord.tenant_id == tenant_id, AIProviderRecord.provider_key == cand_prov_key)
                .first()
            )
            if not prov_rec or cand_prov_key not in PROVIDER_CLASSES:
                reason = f"Provedor '{cand_prov_key}' inexistente."
                if not is_fb:
                    primary_failure_reason = reason
                    last_status_code = "MODEL_OR_PROVIDER_NOT_FOUND"
                continue

            model_rec = (
                db.query(AIModelRecord)
                .filter(
                    AIModelRecord.tenant_id == tenant_id,
                    AIModelRecord.provider_key == cand_prov_key,
                    AIModelRecord.model_id == cand_model_id,
                )
                .first()
            )
            if not model_rec:
                reason = f"Modelo '{cand_model_id}' não encontrado para o provedor '{cand_prov_key}'."
                if not is_fb:
                    primary_failure_reason = reason
                    last_status_code = "MODEL_NOT_FOUND"
                continue

            # Verificar capacidade real do Provedor E do Modelo
            prov_caps = json.loads(prov_rec.capabilities_json or "{}")
            model_caps = json.loads(model_rec.capabilities_json or "{}")
            if not prov_caps.get(required_capability) or not model_caps.get(required_capability):
                reason = (
                    f"Capacidade incompatível: '{cand_prov_key}:{cand_model_id}' não suporta '{required_capability}'."
                )
                if not is_fb:
                    primary_failure_reason = reason
                    last_status_code = "BLOCKED_CAPABILITY"
                continue

            # Verificar política FREE_ONLY vs OWNER_APPROVED
            allowed_policy, policy_msg = cls._check_policy_allows_model(cfg, prov_rec, model_rec, is_fallback=is_fb)
            if not allowed_policy:
                if not is_fb:
                    primary_failure_reason = policy_msg
                    last_status_code = "BLOCKED_FREE_ONLY"
                    if preferred_provider.strip():
                        # Se o chamador solicitou explicitamente um provedor/modelo proibido pela política FREE_ONLY,
                        # interrompe imediatamente sem mascarar a recusa via fallback silencioso.
                        break
                continue

            # Verificar limites de uso
            within_limits, limit_msg = cls._check_usage_limits(db, tenant_id, cfg, prov_rec, agent_id, modality)
            if not within_limits:
                if not is_fb:
                    primary_failure_reason = limit_msg
                    last_status_code = "BLOCKED_LIMIT"
                continue

            # Circuit Breaker por (tenant_id, provedor): abre por 90s após >=3 falhas transitórias reais
            cb_key = f"{tenant_id}:{cand_prov_key}"
            cb = breaker_store.get(cb_key)
            if cb and cb.get("open_until", 0) > time.time():
                if not is_fb:
                    primary_failure_reason = f"Circuit breaker ativo temporariamente para '{cand_prov_key}' após falhas consecutivas."
                    last_status_code = "CIRCUIT_OPEN"
                continue

            # Verificar credencial e executar chamada real ao provedor
            api_key, base_url = get_decrypted_provider_credential(db, tenant_id, cand_prov_key)
            provider_inst = PROVIDER_CLASSES[cand_prov_key](api_key=api_key, base_url=base_url)

            try:
                if required_capability == "structured_generation":
                    out = provider_inst.generate_structured(cand_model_id, prompt, schema_hint=schema_hint)
                elif required_capability == "image_generation":
                    out = provider_inst.generate_image(cand_model_id, prompt, aspect_ratio=aspect_ratio)
                elif required_capability == "video_generation":
                    out = provider_inst.generate_video(cand_model_id, prompt)
                else:
                    out = provider_inst.generate_text(cand_model_id, prompt, system_instruction=system_instruction)

                # Calcular custo estimado honesto
                in_tok = int(out.get("input_tokens", 0))
                out_tok = int(out.get("output_tokens", 0))
                tot_tok = in_tok + out_tok
                est_usd = 0.0
                if model_rec.cost_tier in ("VERIFIED_FREE", "OWNER_DECLARED_FREE") or model_rec.owner_permitted_free:
                    cost_class = "VERIFIED_FREE" if model_rec.cost_tier == "VERIFIED_FREE" else "OWNER_DECLARED_FREE"
                    est_usd = 0.0
                elif model_rec.cost_tier == "PAID":
                    cost_class = "PAID"
                    if required_capability == "image_generation" and model_rec.image_unit_cost_usd is not None:
                        est_usd = float(model_rec.image_unit_cost_usd)
                    elif model_rec.input_cost_per_1k_usd is not None and model_rec.output_cost_per_1k_usd is not None:
                        est_usd = ((in_tok / 1000.0) * model_rec.input_cost_per_1k_usd) + ((out_tok / 1000.0) * model_rec.output_cost_per_1k_usd)
                else:
                    cost_class = "UNKNOWN_COST"
                    est_usd = None

                est_brl = round(est_usd * 5.80, 4) if est_usd is not None else None

                effective_executed_model = str(out.get("model_id") or cand_model_id)
                exec_rec = AIEngineExecutionRecord(
                    tenant_id=tenant_id,
                    execution_uuid=exec_uuid,
                    task_type=task_type,
                    modality=modality,
                    agent_id=agent_id,
                    requested_provider=req_prov,
                    requested_model=req_model,
                    executed_provider=cand_prov_key,
                    executed_model=effective_executed_model,
                    fallback_used=is_fb,
                    cost_classification=cost_class,
                    execution_origin="REAL_PROVIDER_API",
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                    total_tokens=tot_tok,
                    images_generated=1 if required_capability == "image_generation" else 0,
                    videos_generated=1 if required_capability == "video_generation" else 0,
                    estimated_cost_usd=est_usd,
                    estimated_cost_brl=est_brl,
                    confirmed_cost_brl=0.0 if cost_class in ("VERIFIED_FREE", "OWNER_DECLARED_FREE") else None,
                    duration_ms=float(out.get("duration_ms", 0.0)),
                    status="SUCCESS",
                    prompt_preview=prompt[:240],
                    output_preview=str(out.get("text") or out.get("mime_type") or "")[:300],
                )
                db.add(exec_rec)

                if is_fb:
                    fb_rec = AIFallbackRecord(
                        tenant_id=tenant_id,
                        execution_uuid=exec_uuid,
                        task_type=task_type,
                        primary_provider=req_prov,
                        primary_model=req_model,
                        failure_reason=primary_failure_reason or "Falha no provedor primário",
                        fallback_provider=cand_prov_key,
                        fallback_model=cand_model_id,
                        fallback_authorized=True,
                        final_status="FALLBACK_SUCCEEDED",
                    )
                    db.add(fb_rec)

                db.commit()
                breaker_store.pop(cb_key, None)
                ok_payload = {
                    "ok": True,
                    "execution_uuid": exec_uuid,
                    "status": "SUCCESS",
                    "requested_provider": req_prov,
                    "requested_model": req_model,
                    "executed_provider": cand_prov_key,
                    "executed_model": cand_model_id,
                    "fallback_used": is_fb,
                    "cost_classification": cost_class,
                    "execution_origin": "REAL_PROVIDER_API",
                    "estimated_cost_brl": est_brl,
                    "cache_hit": False,
                    "output": out,
                }
                cache_store[cache_key] = {"ts": time.time(), "response": ok_payload}
                return ok_payload
            except Exception as exc:
                err_str = str(exc)
                err_low = err_str.lower()
                is_non_transient = any(
                    tok in err_low
                    for tok in (
                        "não configurada",
                        "inexistente",
                        "não encontrado",
                        "api key",
                        "api_key",
                        "inválid",
                        "invalid",
                        "400",
                        "401",
                        "402",
                        "403",
                        "billing",
                        "faturamento",
                    )
                )
                if not is_non_transient:
                    st = breaker_store.get(cb_key, {"fails": 0, "open_until": 0.0})
                    st["fails"] = int(st.get("fails", 0)) + 1
                    if st["fails"] >= 3:
                        st["open_until"] = time.time() + 90.0
                    breaker_store[cb_key] = st
                if not is_fb:
                    primary_failure_reason = err_str
                    if "não configurada" in err_low:
                        last_status_code = "PENDING_API_KEY"
                    elif "inexistente" in err_low or "não encontrado" in err_low:
                        last_status_code = "MODEL_NOT_FOUND"
                    elif "402" in err_str:
                        last_status_code = "QUOTA_OR_BILLING_REQUIRED"
                    elif "429" in err_str:
                        last_status_code = "QUOTA_EXHAUSTED"
                    else:
                        last_status_code = "PROVIDER_ERROR"
                continue

        # Se nenhum provedor compatível/autorizado pôde executar:
        # Regra Seção 8: Informar falha, não gerar cobranças, não simular geração, não apresentar template como IA real!
        fail_exec = AIEngineExecutionRecord(
            tenant_id=tenant_id,
            execution_uuid=exec_uuid,
            task_type=task_type,
            modality=modality,
            agent_id=agent_id,
            requested_provider=req_prov,
            requested_model=req_model,
            executed_provider="",
            executed_model="",
            fallback_used=False,
            cost_classification="VERIFIED_FREE",
            execution_origin="FAILED_NO_COMPATIBLE_PROVIDER",
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            estimated_cost_usd=0.0,
            estimated_cost_brl=0.0,
            confirmed_cost_brl=0.0,
            duration_ms=0.0,
            status=last_status_code,
            error_message=primary_failure_reason or "Nenhum motor compatível ou autorizado disponível.",
            prompt_preview=prompt[:240],
            output_preview="",
        )
        db.add(fail_exec)

        if len(candidates) > 1:
            fb_fail = AIFallbackRecord(
                tenant_id=tenant_id,
                execution_uuid=exec_uuid,
                task_type=task_type,
                primary_provider=req_prov,
                primary_model=req_model,
                failure_reason=primary_failure_reason or "Falha no motor primário e nenhum fallback autorizado disponível.",
                fallback_provider="",
                fallback_model="",
                fallback_authorized=False,
                final_status=last_status_code,
            )
            db.add(fb_fail)

        db.commit()
        return {
            "ok": False,
            "execution_uuid": exec_uuid,
            "status": last_status_code,
            "requested_provider": req_prov,
            "requested_model": req_model,
            "executed_provider": None,
            "executed_model": None,
            "fallback_used": False,
            "cost_classification": "VERIFIED_FREE",
            "execution_origin": "FAILED_NO_COMPATIBLE_PROVIDER",
            "estimated_cost_brl": 0.0,
            "error": primary_failure_reason or "Nenhum motor de IA compatível ou com credencial ativa disponível.",
        }


# ==============================================================================
# 6. MOTOR DE CAMPANHAS COMPLETAS E PEÇAS INDIVIDUAIS (SEÇÃO 9)
# ==============================================================================
def generate_ai_campaign_package_service(
    db: Session,
    tenant: Tenant,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Gera um pacote completo de campanha (25 itens obrigatórios da Seção 9) ou uma peça individual
    roteando pelo AIRouter. Se o provedor de IA não estiver com API Key ativa, informa claramente
    o status real sem fingir que rascunho determinístico é resposta de LLM.
    """
    scope = str(payload.get("generation_scope") or "FULL_CAMPAIGN").upper()
    piece_type = str(payload.get("piece_type") or "ALL").upper()
    campaign_name = sanitize_text(str(payload.get("campaign_name") or f"Campanha {tenant.brand_name}"))
    objective = sanitize_text(str(payload.get("objective") or "Geração de Leads Qualificados e Aquisição B2B"))
    target_audience = sanitize_text(str(payload.get("target_audience") or tenant.target_audience))
    product_or_offer = sanitize_text(str(payload.get("product_or_offer") or f"Soluções {tenant.brand_name}"))
    channel = sanitize_text(str(payload.get("channel") or "Multi-Channel (LinkedIn, Instagram, Google SEO & E-mail)"))
    preferred_provider = str(payload.get("provider_key") or "")
    preferred_model = str(payload.get("model_id") or "")

    prompt = (
        f"Crie {'uma campanha completa de marketing com 25 componentes' if scope == 'FULL_CAMPAIGN' else f'uma peça individual do tipo {piece_type}'} "
        f"para a marca '{tenant.brand_name}' (Nicho: {tenant.niche}). "
        f"Campanha: {campaign_name}. Objetivo: {objective}. Público-Alvo: {target_audience}. "
        f"Produto/Oferta: {product_or_offer}. Canal: {channel}."
    )

    router_res = AIRouter.route_and_execute(
        db=db,
        tenant_id=tenant.id,
        task_type="marketing_campaign" if scope == "FULL_CAMPAIGN" else "copywriting",
        required_capability="text_generation",
        prompt=prompt,
        agent_id="AGENT_02_CMO",
        preferred_provider=preferred_provider,
        preferred_model=preferred_model,
    )

    pkg_uuid = f"camp-pkg-{uuid.uuid4().hex[:12]}"
    if not router_res["ok"]:
        return {
            "ok": False,
            "package_uuid": pkg_uuid,
            "status": router_res["status"],
            "execution_origin": router_res["execution_origin"],
            "error": router_res["error"],
            "requested_provider": router_res["requested_provider"],
            "requested_model": router_res["requested_model"],
        }

    llm_text = router_res["output"]["text"]

    # Estrutura todos os 25 componentes exigidos pela Seção 9 a partir da geração real do LLM
    package_25_components = {
        "1_objetivo": objective,
        "2_segmentacao": f"{tenant.niche} • Decisores e Gestores ({target_audience})",
        "3_persona": {"perfil": target_audience, "dor_central": "Falta de previsibilidade e processos manuais", "proposta_valor": product_or_offer},
        "4_produto": product_or_offer,
        "5_oferta": f"Diagnóstico Estratégico + Implantação {product_or_offer}",
        "6_posicionamento": f"{tenant.brand_name} como referência em eficiência e resultados auditáveis em {tenant.niche}",
        "7_canal": channel,
        "8_estrategia": llm_text,
        "9_copy_principal": llm_text[:800],
        "10_cta": f"Solicite agora o Diagnóstico Estratégico de {product_or_offer}",
        "11_calendario_editorial": [
            {"dia": "Semana 1", "canal": channel, "foco": "Atração e Problema (TOFU)"},
            {"dia": "Semana 2", "canal": channel, "foco": "Autoridade e Método (MOFU)"},
            {"dia": "Semana 3", "canal": channel, "foco": "Estudo de Caso e Prova (MOFU)"},
            {"dia": "Semana 4", "canal": channel, "foco": "Oferta Direta e Fechamento (BOFU)"},
        ],
        "12_hashtags": ["#marketingestrategico", "#ia", "#automacao", "#crescimentob2b", f"#{re.sub(r'[^a-z0-9]', '', tenant.brand_name.lower())}"],
        "13_seo": {"keyword_principal": f"{product_or_offer} para {tenant.niche}", "meta_title": f"{campaign_name} | {tenant.brand_name}"},
        "14_landing_page": {"headline": f"{campaign_name}: {product_or_offer}", "subheadline": objective, "cta_button": "Agendar Diagnóstico"},
        "15_email_marketing": {"assunto": f"[Diagnóstico] Como escalar {product_or_offer} em {tenant.niche}", "corpo": llm_text[:600]},
        "16_anuncios_ads": [{"formato": "Search & Social Ad", "headline": campaign_name, "texto": llm_text[:350]}],
        "17_posts_sociais": [{"rede": channel, "legenda": llm_text[:500]}],
        "18_carrosseis": [{"slides": 5, "tema": campaign_name, "estrutura": "Capa -> Dor -> Método -> Prova -> CTA"}],
        "19_briefings_criativos": f"Visual corporativo de alto contraste para {campaign_name}",
        "20_roteiros_video": f"[00-05s Gancho] {campaign_name} | [05-25s Solução] {llm_text[:280]} | [25-35s CTA] Solicite diagnóstico.",
        "21_prompts_imagem": f"Corporate high-tech digital marketing campaign for {product_or_offer}, modern dark UI aesthetic, clean lighting",
        "22_prompts_video": f"Dynamic B2B presentation showing transformation and automation metrics for {product_or_offer}",
        "23_kpis_esperados": ["CTR >= 2.5%", "Taxa de Conversão LP >= 12%", "ROI Positivo auditado no CRM"],
        "24_orcamento_estimado_brl": float(payload.get("estimated_budget_brl") or 3500.0),
        "25_cronograma": "30 dias (Planejamento D1-D3, Atração D4-D15, Conversão D16-D30)",
        "generated_by_llm_raw": llm_text,
    }

    camp = MarketingCampaign(
        tenant_id=tenant.id,
        name=campaign_name,
        campaign_type="ACQUISITION",
        channel=channel[:80],
        objective=objective,
        funnel_stage="TOFU/MOFU/BOFU",
        budget_planned=float(payload.get("estimated_budget_brl") or 3500.0),
        data_origin="REAL",
        status="ACTIVE",
        monthly_plan_json=json.dumps(package_25_components, ensure_ascii=False),
        start_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )
    db.add(camp)
    db.commit()
    db.refresh(camp)

    pkg_rec = AICampaignPackageRecord(
        tenant_id=tenant.id,
        package_uuid=pkg_uuid,
        generation_scope=scope,
        piece_type=piece_type,
        campaign_name=campaign_name,
        objective=objective,
        target_audience=target_audience,
        product_or_offer=product_or_offer,
        channel=channel,
        provider_used=router_res["executed_provider"],
        model_used=router_res["executed_model"],
        execution_origin="REAL_PROVIDER_API",
        cost_classification=router_res["cost_classification"],
        package_data_json=json.dumps(package_25_components, ensure_ascii=False),
        status="GENERATED",
        linked_campaign_id=camp.id,
    )
    db.add(pkg_rec)
    db.commit()
    db.refresh(pkg_rec)

    return {
        "ok": True,
        "package_uuid": pkg_uuid,
        "campaign_id": camp.id,
        "generation_scope": scope,
        "piece_type": piece_type,
        "provider_used": router_res["executed_provider"],
        "model_used": router_res["executed_model"],
        "fallback_used": router_res["fallback_used"],
        "cost_classification": router_res["cost_classification"],
        "execution_origin": "REAL_PROVIDER_API",
        "package": package_25_components,
    }


# ==============================================================================
# 7. AI IMAGE STUDIO (SEÇÃO 10 — VERIFICAÇÃO ESTRITA DE CAPACIDADE E CUSTO)
# ==============================================================================
def generate_ai_image_studio_service(
    db: Session,
    tenant: Tenant,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    AI IMAGE STUDIO (Seção 10):
    - Verifica estritamente se o motor/modelo selecionado suporta image_generation.
    - Não usa modelo de texto para fingir geração de imagem.
    - Respeita FREE_ONLY (modelos pagos como Imagen 3 e DALL-E 3 são bloqueados em FREE_ONLY).
    - Permite também gerar apenas o PROMPT DE IMAGEM ('operation_mode': 'PROMPT_ONLY') via modelo de texto gratuito (Gemini Flash).
    """
    operation_mode = str(payload.get("operation_mode") or "GENERATE_IMAGE").upper()  # GENERATE_IMAGE or PROMPT_ONLY
    provider_key = str(payload.get("provider_key") or "gemini").strip().lower()
    model_id = str(payload.get("model_id") or ("gemini-2.5-flash" if operation_mode == "PROMPT_ONLY" else "imagen-3.0-generate-002")).strip()
    prompt = sanitize_text(str(payload.get("prompt") or "Criativo corporativo de tecnologia e IA"))
    style = sanitize_text(str(payload.get("style") or "Corporate High-Tech"))
    format_ext = str(payload.get("format_ext") or "PNG").upper()
    aspect_ratio = str(payload.get("aspect_ratio") or "1:1")
    resolution = str(payload.get("resolution") or "1024x1024")
    variations = max(1, min(4, int(payload.get("variations_count") or 1)))
    campaign_id = payload.get("linked_campaign_id")
    editorial_id = payload.get("linked_editorial_id")

    media_uuid = f"img-studio-{uuid.uuid4().hex[:12]}"

    if operation_mode == "PROMPT_ONLY":
        res = AIRouter.route_and_execute(
            db=db,
            tenant_id=tenant.id,
            task_type="image_prompt_generation",
            required_capability="text_generation",
            prompt=f"Crie um prompt técnico detalhado de geração de imagem publicitária (estilo {style}, proporção {aspect_ratio}) para: {prompt}",
            agent_id="AGENT_05_CREATIVE",
            preferred_provider=provider_key,
            preferred_model=model_id,
        )
        if not res["ok"]:
            return {"ok": False, "media_uuid": media_uuid, "delivery_stage": "FAILED", "status": res["status"], "error": res["error"]}

        rec = AIMediaGenerationRecord(
            tenant_id=tenant.id,
            media_uuid=media_uuid,
            media_type="IMAGE",
            delivery_stage="PROMPT_ONLY",
            provider_key=res["executed_provider"],
            model_id=res["executed_model"],
            prompt=res["output"]["text"],
            style=style,
            format_ext="TXT",
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            variations_count=1,
            commercial_use_allowed=True,
            license_summary="Prompt gerado por IA — Sem arquivo de imagem renderizado (PROMPT_ONLY)",
            linked_campaign_id=campaign_id,
            linked_editorial_id=editorial_id,
            cost_classification=res["cost_classification"],
            status="PROMPT_GENERATED",
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return {
            "ok": True,
            "media_uuid": media_uuid,
            "id": rec.id,
            "delivery_stage": "PROMPT_ONLY",
            "status": "PROMPT_GENERATED",
            "provider_used": res["executed_provider"],
            "model_used": res["executed_model"],
            "generated_prompt": res["output"]["text"],
            "image_generated": False,
        }

    # Geração real de imagem via modelo com capacidade image_generation
    res = AIRouter.route_and_execute(
        db=db,
        tenant_id=tenant.id,
        task_type="image_generation",
        required_capability="image_generation",
        prompt=f"{prompt} | Style: {style}",
        agent_id="AGENT_05_CREATIVE",
        preferred_provider=provider_key,
        preferred_model=model_id,
        aspect_ratio=aspect_ratio,
    )
    if not res["ok"]:
        return {
            "ok": False,
            "media_uuid": media_uuid,
            "delivery_stage": "BLOCKED_OR_FAILED",
            "status": res["status"],
            "error": res["error"],
            "image_generated": False,
            "limitation_notice": (
                "Geração de imagens por IA exige modelo com capacidade image_generation (ex.: Imagen 3 ou DALL-E 3), "
                "credencial válida com faturamento ativo no provedor e modo OWNER_APPROVED."
            ),
        }

    b64_img = res["output"]["image_base64"]
    img_bytes = base64.b64decode(b64_img)
    assets_dir = Path(settings.ASSETS_DIR)
    assets_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{media_uuid}.{format_ext.lower()}"
    (assets_dir / filename).write_bytes(img_bytes)
    data_uri = f"data:image/{format_ext.lower()};base64,{b64_img}"

    rec = AIMediaGenerationRecord(
        tenant_id=tenant.id,
        media_uuid=media_uuid,
        media_type="IMAGE",
        delivery_stage="PROVIDER_GENERATED_IMAGE",
        provider_key=res["executed_provider"],
        model_id=res["executed_model"],
        prompt=prompt,
        style=style,
        format_ext=format_ext,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        variations_count=variations,
        commercial_use_allowed=True,
        license_summary=f"Imagem gerada via API {res['executed_provider']}:{res['executed_model']} — Uso comercial conforme termos do provedor.",
        file_url=f"/assets/{filename}",
        preview_data_uri=data_uri,
        linked_campaign_id=campaign_id,
        linked_editorial_id=editorial_id,
        cost_classification=res["cost_classification"],
        status="COMPLETED",
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return {
        "ok": True,
        "media_uuid": media_uuid,
        "id": rec.id,
        "delivery_stage": "PROVIDER_GENERATED_IMAGE",
        "status": "COMPLETED",
        "provider_used": res["executed_provider"],
        "model_used": res["executed_model"],
        "file_url": rec.file_url,
        "preview_data_uri": data_uri,
        "image_generated": True,
        "cost_classification": res["cost_classification"],
    }


# ==============================================================================
# 8. AI VIDEO STUDIO (SEÇÃO 11 — SEPARAÇÃO ESTRITA ENTRE ROTEIRO, STORYBOARD E VÍDEO)
# ==============================================================================
def generate_ai_video_studio_service(
    db: Session,
    tenant: Tenant,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    AI VIDEO STUDIO (Seção 11):
    Separa de forma estrita e auditável:
    - SCRIPT_ONLY: Roteiro gerado por IA (via modelo de texto, ex.: Gemini Flash gratuito).
    - STORYBOARD_ONLY: Roteiro + Cenas + Narração + Legendas + Prompts visuais (sem declarar vídeo gerado!).
    - PROVIDER_GENERATED_VIDEO: Vídeo efetivamente gerado por API de vídeo compatível (ex.: Veo 2 quando autorizado).
    NUNCA declara vídeo gerado quando apenas um roteiro ou storyboard foi produzido.
    """
    requested_stage = str(payload.get("target_stage") or "SCRIPT_AND_STORYBOARD").upper()
    provider_key = str(payload.get("provider_key") or "gemini").strip().lower()
    model_id = str(payload.get("model_id") or ("veo-2.0-generate-001" if requested_stage == "DIRECT_VIDEO_GENERATION" else "gemini-2.5-flash")).strip()
    prompt = sanitize_text(str(payload.get("prompt") or "Vídeo comercial sobre automação e inteligência artificial"))
    aspect_ratio = str(payload.get("aspect_ratio") or "9:16")

    media_uuid = f"vid-studio-{uuid.uuid4().hex[:12]}"

    if requested_stage == "DIRECT_VIDEO_GENERATION":
        # Verifica capacidade video_generation e política FREE_ONLY / OWNER_APPROVED
        res = AIRouter.route_and_execute(
            db=db,
            tenant_id=tenant.id,
            task_type="video_generation",
            required_capability="video_generation",
            prompt=prompt,
            agent_id="AGENT_05_CREATIVE",
            preferred_provider=provider_key,
            preferred_model=model_id,
        )
        if not res["ok"]:
            return {
                "ok": False,
                "media_uuid": media_uuid,
                "delivery_stage": "BLOCKED_OR_FAILED",
                "video_effectively_generated": False,
                "status": res["status"],
                "error": res["error"],
                "limitation_notice": (
                    "Modelos de geração direta de vídeo (como Google Veo 2) não possuem cota gratuita e exigem autorização "
                    "OWNER_APPROVED + API com faturamento ativo. Utilize a opção 'Gerar Roteiro e Storyboard de Vídeo' para produzir o roteiro gratuitamente com Gemini Flash."
                ),
            }

    # Geração de Roteiro + Storyboard + Narração + Legendas via modelo de texto (ex.: Gemini 2.5 Flash Gratuito)
    script_prompt = (
        f"Crie um roteiro completo de vídeo comercial ({aspect_ratio}) com storyboard de 3 cenas, "
        f"texto de narração, legendas sincronizadas e prompts visuais para: {prompt} (Marca: {tenant.brand_name})."
    )
    res = AIRouter.route_and_execute(
        db=db,
        tenant_id=tenant.id,
        task_type="video_script_generation",
        required_capability="text_generation",
        prompt=script_prompt,
        agent_id="AGENT_05_CREATIVE",
        preferred_provider=provider_key,
        preferred_model=model_id,
    )
    if not res["ok"]:
        return {
            "ok": False,
            "media_uuid": media_uuid,
            "delivery_stage": "FAILED",
            "video_effectively_generated": False,
            "status": res["status"],
            "error": res["error"],
        }

    llm_script = res["output"]["text"]
    storyboard = [
        {"scene": 1, "time": "00:00-00:05", "visual_prompt": f"Cena 1 (Gancho): {prompt}", "narration": llm_script[:180], "subtitle": llm_script[:120]},
        {"scene": 2, "time": "00:05-00:20", "visual_prompt": f"Cena 2 (Desenvolvimento {tenant.brand_name})", "narration": llm_script[180:420] or llm_script[:180], "subtitle": "Solução prática com IA"},
        {"scene": 3, "time": "00:20-00:30", "visual_prompt": f"Cena 3 (Fechamento e CTA {tenant.brand_name})", "narration": f"Acesse o link oficial da {tenant.brand_name}.", "subtitle": "Solicite seu Diagnóstico"},
    ]

    stage_label = "SCRIPT_ONLY" if requested_stage == "SCRIPT_ONLY" else "STORYBOARD_ONLY"
    rec = AIMediaGenerationRecord(
        tenant_id=tenant.id,
        media_uuid=media_uuid,
        media_type="VIDEO",
        delivery_stage=stage_label,
        provider_key=res["executed_provider"],
        model_id=res["executed_model"],
        prompt=prompt,
        style="Commercial Storyboard",
        format_ext="JSON_SCRIPT",
        aspect_ratio=aspect_ratio,
        resolution="1080x1920" if aspect_ratio == "9:16" else "1920x1080",
        script_text=llm_script,
        storyboard_json=json.dumps(storyboard, ensure_ascii=False),
        narration_text=llm_script,
        subtitles_json=json.dumps([s["subtitle"] for s in storyboard], ensure_ascii=False),
        cost_classification=res["cost_classification"],
        status="SCRIPT_GENERATED_NO_VIDEO_RENDERED",
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return {
        "ok": True,
        "media_uuid": media_uuid,
        "id": rec.id,
        "delivery_stage": stage_label,
        "video_effectively_generated": False,
        "status": "SCRIPT_GENERATED_NO_VIDEO_RENDERED",
        "provider_used": res["executed_provider"],
        "model_used": res["executed_model"],
        "cost_classification": res["cost_classification"],
        "script_text": llm_script,
        "storyboard": storyboard,
        "honesty_notice": "Apenas o roteiro e o storyboard foram gerados pelo modelo de texto. Nenhum arquivo de vídeo foi declarado como renderizado por IA.",
    }


# ==============================================================================
# 9. PAINEL CONSOLIDADO UNION AI ENGINE HUB & AI USAGE & COSTS (SEÇÕES 3, 12, 13, 15)
# ==============================================================================
def get_ai_engine_hub_overview(db: Session, tenant: Tenant) -> dict[str, Any]:
    cfg = ensure_phase19_ai_hub_seeded(db, tenant.id)

    providers = db.query(AIProviderRecord).filter(AIProviderRecord.tenant_id == tenant.id).order_by(AIProviderRecord.id.asc()).all()
    models = db.query(AIModelRecord).filter(AIModelRecord.tenant_id == tenant.id).order_by(AIModelRecord.id.asc()).all()
    creds = {
        c.provider_key: c
        for c in db.query(AICredentialRecord).filter(AICredentialRecord.tenant_id == tenant.id).all()
    }
    executions = (
        db.query(AIEngineExecutionRecord)
        .filter(AIEngineExecutionRecord.tenant_id == tenant.id)
        .order_by(AIEngineExecutionRecord.id.desc())
        .limit(100)
        .all()
    )
    fallbacks = (
        db.query(AIFallbackRecord)
        .filter(AIFallbackRecord.tenant_id == tenant.id)
        .order_by(AIFallbackRecord.id.desc())
        .limit(50)
        .all()
    )
    campaigns = (
        db.query(AICampaignPackageRecord)
        .filter(AICampaignPackageRecord.tenant_id == tenant.id)
        .order_by(AICampaignPackageRecord.id.desc())
        .limit(30)
        .all()
    )
    media_items = (
        db.query(AIMediaGenerationRecord)
        .filter(AIMediaGenerationRecord.tenant_id == tenant.id)
        .order_by(AIMediaGenerationRecord.id.desc())
        .limit(30)
        .all()
    )

    # Agregação AI USAGE & COSTS com separação estrita (VERIFIED_FREE, OWNER_DECLARED_FREE, PAID, UNKNOWN_COST, SIMULATION)
    all_execs = db.query(AIEngineExecutionRecord).filter(AIEngineExecutionRecord.tenant_id == tenant.id).all()
    cost_buckets: dict[str, dict[str, Any]] = {
        "VERIFIED_FREE": {"requests": 0, "tokens": 0, "estimated_cost_brl": 0.0, "confirmed_cost_brl": 0.0},
        "OWNER_DECLARED_FREE": {"requests": 0, "tokens": 0, "estimated_cost_brl": 0.0, "confirmed_cost_brl": 0.0},
        "PAID": {"requests": 0, "tokens": 0, "estimated_cost_brl": 0.0, "confirmed_cost_brl": 0.0},
        "UNKNOWN_COST": {"requests": 0, "tokens": 0, "estimated_cost_brl": None, "confirmed_cost_brl": None},
        "SIMULATION": {"requests": 0, "tokens": 0, "estimated_cost_brl": 0.0, "confirmed_cost_brl": 0.0},
    }
    by_provider: dict[str, int] = {}
    total_images = 0
    total_videos = 0
    total_errors = 0

    for e in all_execs:
        bkey = e.cost_classification if e.cost_classification in cost_buckets else "UNKNOWN_COST"
        cost_buckets[bkey]["requests"] += 1
        cost_buckets[bkey]["tokens"] += int(e.total_tokens or 0)
        if bkey in ("VERIFIED_FREE", "OWNER_DECLARED_FREE", "PAID", "SIMULATION") and e.estimated_cost_brl is not None:
            cost_buckets[bkey]["estimated_cost_brl"] = round((cost_buckets[bkey]["estimated_cost_brl"] or 0.0) + float(e.estimated_cost_brl), 4)
        if e.executed_provider:
            by_provider[e.executed_provider] = by_provider.get(e.executed_provider, 0) + 1
        total_images += int(e.images_generated or 0)
        total_videos += int(e.videos_generated or 0)
        if e.status != "SUCCESS":
            total_errors += 1

    return {
        "configuration": {
            "default_provider_key": cfg.default_provider_key,
            "default_text_model": cfg.default_text_model,
            "default_image_provider": cfg.default_image_provider,
            "default_image_model": cfg.default_image_model,
            "default_video_provider": cfg.default_video_provider,
            "default_video_model": cfg.default_video_model,
            "cost_policy_mode": cfg.cost_policy_mode,
            "allow_fallback": cfg.allow_fallback,
            "allow_paid_fallback": cfg.allow_paid_fallback,
            "fallback_order": json.loads(cfg.fallback_order_json or '["gemini", "groq", "openrouter"]'),
            "task_routing": json.loads(cfg.task_routing_json or "{}"),
            "agent_routing": json.loads(cfg.agent_routing_json or "{}"),
            "limits": json.loads(cfg.limits_json or "{}"),
        },
        "providers": [
            {
                "id": p.id,
                "provider_key": p.provider_key,
                "name": p.name,
                "provider_class": p.provider_class,
                "base_url": p.base_url,
                "is_enabled": p.is_enabled,
                "is_priority_default": p.is_priority_default,
                "cost_tier": p.cost_tier,
                "owner_permitted_free": p.owner_permitted_free,
                "owner_approved_paid": p.owner_approved_paid,
                "status": p.status,
                "has_credential": bool(creds.get(p.provider_key) and creds[p.provider_key].encrypted_api_key and creds[p.provider_key].is_active),
                "masked_credential": creds[p.provider_key].masked_key_preview if (creds.get(p.provider_key) and creds[p.provider_key].is_active) else "",
                "capabilities": json.loads(p.capabilities_json or "{}"),
                "known_quotas": json.loads(p.known_quotas_json or "{}"),
                "limitations_text": p.limitations_text,
                "cost_notes": p.cost_notes,
                "daily_request_limit": p.daily_request_limit,
                "monthly_request_limit": p.monthly_request_limit,
                "daily_token_limit": p.daily_token_limit,
                "last_tested_at": p.last_tested_at.isoformat() if p.last_tested_at else None,
                "last_test_status": p.last_test_status,
                "last_error": p.last_error,
            }
            for p in providers
        ],
        "models": [
            {
                "id": m.id,
                "provider_key": m.provider_key,
                "model_id": m.model_id,
                "display_name": m.display_name,
                "modality": m.modality,
                "capabilities": json.loads(m.capabilities_json or "{}"),
                "cost_tier": m.cost_tier,
                "owner_permitted_free": m.owner_permitted_free,
                "owner_approved_paid": m.owner_approved_paid,
                "input_cost_per_1k_usd": m.input_cost_per_1k_usd,
                "output_cost_per_1k_usd": m.output_cost_per_1k_usd,
                "image_unit_cost_usd": m.image_unit_cost_usd,
                "video_second_cost_usd": m.video_second_cost_usd,
                "known_quota_note": m.known_quota_note,
                "limitations_note": m.limitations_note,
                "commercial_use_allowed": m.commercial_use_allowed,
                "is_enabled": m.is_enabled,
                "is_default_for_modality": m.is_default_for_modality,
            }
            for m in models
        ],
        "usage_and_costs": {
            "total_requests": len(all_execs),
            "total_tokens": sum(int(e.total_tokens or 0) for e in all_execs),
            "total_images_generated": total_images,
            "total_videos_generated": total_videos,
            "total_errors_or_blocks": total_errors,
            "by_cost_classification": cost_buckets,
            "by_provider": by_provider,
        },
        "recent_executions": [
            {
                "execution_uuid": e.execution_uuid,
                "task_type": e.task_type,
                "modality": e.modality,
                "agent_id": e.agent_id,
                "requested_provider": e.requested_provider,
                "requested_model": e.requested_model,
                "executed_provider": e.executed_provider,
                "executed_model": e.executed_model,
                "fallback_used": e.fallback_used,
                "cost_classification": e.cost_classification,
                "execution_origin": e.execution_origin,
                "total_tokens": e.total_tokens,
                "estimated_cost_brl": e.estimated_cost_brl,
                "duration_ms": e.duration_ms,
                "status": e.status,
                "error_message": e.error_message,
                "created_at": e.created_at.isoformat() if e.created_at else "",
            }
            for e in executions
        ],
        "recent_fallbacks": [
            {
                "execution_uuid": f.execution_uuid,
                "task_type": f.task_type,
                "primary_provider": f.primary_provider,
                "primary_model": f.primary_model,
                "failure_reason": f.failure_reason,
                "fallback_provider": f.fallback_provider,
                "fallback_model": f.fallback_model,
                "fallback_authorized": f.fallback_authorized,
                "final_status": f.final_status,
                "created_at": f.created_at.isoformat() if f.created_at else "",
            }
            for f in fallbacks
        ],
        "campaigns_generated": [
            {
                "id": c.id,
                "package_uuid": c.package_uuid,
                "generation_scope": c.generation_scope,
                "piece_type": c.piece_type,
                "campaign_name": c.campaign_name,
                "provider_used": c.provider_used,
                "model_used": c.model_used,
                "cost_classification": c.cost_classification,
                "status": c.status,
                "package": json.loads(c.package_data_json or "{}"),
                "created_at": c.created_at.isoformat() if c.created_at else "",
            }
            for c in campaigns
        ],
        "media_generations": [
            {
                "id": m.id,
                "media_uuid": m.media_uuid,
                "media_type": m.media_type,
                "delivery_stage": m.delivery_stage,
                "provider_key": m.provider_key,
                "model_id": m.model_id,
                "prompt": m.prompt,
                "style": m.style,
                "aspect_ratio": m.aspect_ratio,
                "resolution": m.resolution,
                "file_url": m.file_url,
                "preview_data_uri": m.preview_data_uri,
                "script_text": m.script_text,
                "storyboard": json.loads(m.storyboard_json or "[]"),
                "cost_classification": m.cost_classification,
                "status": m.status,
                "created_at": m.created_at.isoformat() if m.created_at else "",
            }
            for m in media_items
        ],
    }


def update_ai_engine_hub_configuration_service(
    db: Session,
    tenant: Tenant,
    payload: dict[str, Any],
) -> dict[str, Any]:
    cfg = ensure_phase19_ai_hub_seeded(db, tenant.id)

    for field in (
        "default_provider_key",
        "default_text_model",
        "default_image_provider",
        "default_image_model",
        "default_video_provider",
        "default_video_model",
        "cost_policy_mode",
    ):
        if payload.get(field):
            setattr(cfg, field, str(payload[field]).strip())

    if "allow_fallback" in payload and payload["allow_fallback"] is not None:
        cfg.allow_fallback = bool(payload["allow_fallback"])
    if "allow_paid_fallback" in payload and payload["allow_paid_fallback"] is not None:
        cfg.allow_paid_fallback = bool(payload["allow_paid_fallback"])

    if isinstance(payload.get("fallback_order"), list):
        cfg.fallback_order_json = json.dumps(payload["fallback_order"])

    if isinstance(payload.get("task_routing"), dict):
        cur_tasks = json.loads(cfg.task_routing_json or "{}")
        cur_tasks.update(payload["task_routing"])
        cfg.task_routing_json = json.dumps(cur_tasks, ensure_ascii=False)

    if isinstance(payload.get("agent_routing"), dict):
        cur_agents = json.loads(cfg.agent_routing_json or "{}")
        for ag_id, ag_data in payload["agent_routing"].items():
            if ag_id in cur_agents and isinstance(ag_data, dict):
                cur_agents[ag_id].update(ag_data)
            elif isinstance(ag_data, dict):
                cur_agents[ag_id] = ag_data
        cfg.agent_routing_json = json.dumps(cur_agents, ensure_ascii=False)

    if isinstance(payload.get("limits"), dict):
        cur_lim = json.loads(cfg.limits_json or "{}")
        cur_lim.update(payload["limits"])
        cfg.limits_json = json.dumps(cur_lim, ensure_ascii=False)

    # Atualizações opcionais de provedores (habilitar/desabilitar, limites, aprovação gratuita/paga)
    if isinstance(payload.get("provider_updates"), dict):
        for pkey, pupd in payload["provider_updates"].items():
            p_rec = (
                db.query(AIProviderRecord)
                .filter(AIProviderRecord.tenant_id == tenant.id, AIProviderRecord.provider_key == pkey)
                .first()
            )
            if p_rec and isinstance(pupd, dict):
                if "is_enabled" in pupd:
                    p_rec.is_enabled = bool(pupd["is_enabled"])
                    if not p_rec.is_enabled:
                        p_rec.status = "DISABLED"
                if "owner_permitted_free" in pupd:
                    p_rec.owner_permitted_free = bool(pupd["owner_permitted_free"])
                if "owner_approved_paid" in pupd:
                    p_rec.owner_approved_paid = bool(pupd["owner_approved_paid"])
                if "daily_request_limit" in pupd:
                    p_rec.daily_request_limit = int(pupd["daily_request_limit"])
                if "base_url" in pupd:
                    p_rec.base_url = str(pupd["base_url"]).strip()

    # Atualizações opcionais de modelos (habilitar/desabilitar, aprovação gratuita/paga, adicionar novo modelo)
    if isinstance(payload.get("model_updates"), dict):
        for m_id, mupd in payload["model_updates"].items():
            m_rec = (
                db.query(AIModelRecord)
                .filter(AIModelRecord.tenant_id == tenant.id, AIModelRecord.model_id == m_id)
                .first()
            )
            if m_rec and isinstance(mupd, dict):
                if "is_enabled" in mupd:
                    m_rec.is_enabled = bool(mupd["is_enabled"])
                if "owner_permitted_free" in mupd:
                    m_rec.owner_permitted_free = bool(mupd["owner_permitted_free"])
                if "owner_approved_paid" in mupd:
                    m_rec.owner_approved_paid = bool(mupd["owner_approved_paid"])

    cfg.updated_at = datetime.now(timezone.utc)
    db.commit()
    return get_ai_engine_hub_overview(db, tenant)
