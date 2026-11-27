# UNION GROWTH OS — FASE 26: INTEGRATION AUDIT

**Versão:** `2.3.0 — FASE 26`  

## 1. Estado Real das 18 Integrações Externas
- **Nativas sem credencial externa (1/18 conectada por padrão):** `google_pagespeed_insights` + crawler HTML técnico próprio.
- **Pendentes de credenciais / OAuth do proprietário (17/18):** `ga4`, `google_search_console`, `google_business_profile`, `youtube`, `meta_business`, `instagram`, `facebook_pages`, `linkedin`, `tiktok`, `pinterest`, `whatsapp_cloud`, `smtp_email`, `mercado_pago`, `stripe`, `rds_webhook`, `openai`, `anthropic`.
- **Redes Sociais conectadas para publicação direta:** `0/6` — mitigado pelo **Pacote Assistido 1-Clique** com checklist e texto pronto.

## 2. OAuth 2.0 & Fluxo de Desconexão (`ManagementAndIntegrationsWorkspace.tsx`)
- Botão **OAuth 2.0** aciona `/api/v1/integrations/oauth/{provider_key}/start`: valida presença prévia de `client_id` e `client_secret` criptografados com state HMAC antes de abrir URL oficial (nunca simula conexão OAuth sem aplicativo aprovado).
- Botão **Desconectar** aciona `POST /api/v1/integrations/{provider_key}/disconnect` limpando credenciais criptografadas em Fernet AES-128 do tenant com registro em `AuditLog`.
