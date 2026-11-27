# UNION GROWTH OS — FASE 25: ESTRATÉGIA DE ATIVAÇÃO (TTFV) & RETENÇÃO

## 1. Implementação Real em Produção (`GET /api/v1/growth-os/activation-retention`)
Na Fase 25, substituímos a noção genérica de "progresso de configuração" por um motor real auditado diretamente contra o PostgreSQL ([phase25_product_engine.py](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/backend/app/services/phase25_product_engine.py)):

- **6 Marcos Concretos de Time-to-First-Value (TTFV):**
  1. `empresa_configurada` — Empresa, nicho e público-alvo definidos.
  2. `marca_definida` — Site oficial e tom de voz configurados.
  3. `seo_auditado` — 1ª Auditoria SEO técnica HTTP executada.
  4. `conteudo_criado` — Peças geradas na Content Factory para o site/nicho.
  5. `primeiro_lead` — 1º lead real registrado com consentimento LGPD.
  6. `primeira_automacao` — Pelo menos 1 rotina automática Python ativa.
- **Critério de Primeiro Valor Atingido (`first_value_achieved`):** `completed_milestones >= 3`.
- **Exposição na UI:** barra discreta em [HomeWorkspace.tsx](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/frontend/src/components/HomeWorkspace.tsx) que desaparece automaticamente após `first_value_achieved === true`.

---

## 2. Motivos Diários Reais de Retorno ("Habit Loops" sem Push Fake)
O payload `daily_return_triggers` calcula pendências concretas do workspace para trazer o usuário de volta por utilidade operacional:
- Aprovações pendentes aguardando decisão do owner (`ApprovalRequest`).
- Leads quentes com `lead_score >= 65` sem retorno registrado no CRM.
- Negociações abertas estagnadas (`>= 5` dias ou sem tarefa vinculada).
- Conteúdos prontos aguardando distribuição via Pacote 1-Clique (`ready_content`).

*Dados ao vivo no Tenant 1 na auditoria pós-deploy:* `activation_pct: 100%` (`6/6`), `3` gatilhos reais diários ativos (`2` leads quentes sem retorno, `1` negociação parada, `59` conteúdos prontos). No tenant QA limpo, exibe progressão incremental real conforme as ações ocorrem.
