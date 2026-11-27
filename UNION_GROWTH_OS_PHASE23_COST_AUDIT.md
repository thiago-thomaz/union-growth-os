# FASE 23 — AUDITORIA FINANCEIRA, CUSTOS DE IA & CONFORMIDADE (`FREE_ONLY`)

## 1. Política Padrão de Proteção Financeira
- **Modo Ativo**: `FREE_ONLY` em todos os tenants novos e no Tenant 1 (`ai_engines_hub.py`).
- **Bloqueio de Modelos Pagos**: `gpt-4o`, `gpt-4o-mini`, `claude-3.7`, `dall-e-3`, `imagen-3.0-generate-002` e `veo-2.0-generate-001` são bloqueados antes de qualquer chamada externa caso `FREE_ONLY` esteja ativo (`BLOCKED_FREE_ONLY`).
- **Sem Custos Escondidos de Orquestração**: Toda automação conversacional e scheduler cron roda nativamente em **Python + APScheduler** dentro da VPS já contratada (**R$ 0,00 adicional**, **0% dependência do n8n**).

## 2. Mecanismos de Proteção de Cota e Disponibilidade (Fase 23)
1. **Cache TTL In-Memory (`180s`)**: Chamadas idênticas bem-sucedidas ao `AIRouter` reutilizam o resultado em cache, economizando RPM/RPD e tokens gratuitos.
2. **Circuit Breaker por Provedor (`90s` após `>=3` falhas)**: Evita martelar provedores fora do ar ou com cota esgotada (`HTTP 402`/`5xx`), retornando estado honesto `CIRCUIT_OPEN`.
3. **Limites Granulares (`_check_usage_limits`)**: Teto diário/mensal global, por modalidade, por provedor e por agente verificados antes de toda chamada HTTP externa.
4. **Custo Operacional Adicional da Fase 23**: **R$ 0,00** (nenhuma API paga contratada, nenhum serviço pago adicionado ao stack).
