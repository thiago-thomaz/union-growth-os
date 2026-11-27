# UNION GROWTH OS — FASE 26: AUTOMATION ENGINE (100% PYTHON NATIVO)

**Versão:** `2.3.0 — FASE 26`  

## 1. Arquitetura 100% Autônoma (Zero Dependência do `n8n`)
- **Scheduler Embutido (`APScheduler`)**: `127` jobs ativos rodando no container FastAPI principal sem dependência de serviços externos ou webhooks pagos de terceiros.
- **Construtor Conversacional (`ConversationalAutomationPanel.tsx` + `/automations/conversational-build`)**: transforma pedidos em português natural (leads sem resposta, negócios parados em negociação, rotinas SEO/Briefing) em regras estruturadas Python com **Dry-Run prévio obrigatório** e confirmação humana antes de persistir no PostgreSQL.
- **Confiabilidade & Backoff**: todas as execuções contam com controle de idempotência e validação de Retry + Backoff visível no Modo Avançado.
- **Separação Segura UI (`Modo Simples` vs `Modo Avançado`)**: usuários leigos veem rótulos de frequência simples (`Diariamente às 08h`), enquanto operadores avançados acessam triggers, agente executor e botão `Testar Retry + Backoff`.
