# UNION GROWTH OS — ESTRATÉGIA DE GROWTH & MOTOR 0–90 DIAS (FASE 27)

## 1. Evolução do Growth Execution Center (`growth_plans` & `growth_plan_steps`)

Na Fase 26, os planos 0/7/30/90 dias eram gerados em memória a cada clique. Na Fase 27, cada plano e cada etapa passaram a persistir no **PostgreSQL**:
- **`GET /api/v1/growth-os/growth-plan/current`**: recarrega automaticamente o último plano ativo ao abrir o workspace.
- **`PATCH /api/v1/growth-os/growth-plan/steps/{step_id}`**: ciclo completo de execução operacional via comandos **`EXECUTE`**, **`COMPLETE`** (`Concluído`), **`REPLAN`** (`Replanejado` com atualização de horizonte e data-limite) e **`CANCEL`** (`Cancelado`).
- **Atributos Completos por Etapa:** `priority_score` (0–100), `owner_label`, `due_date`, `dependencies`, `success_metric`, `evidence`, `next_action`, `probability_origin: "ESTIMATED"` e disclaimer explícito de que probabilidades e resultados esperados são hipóteses operacionais (não garantias).

## 2. Retenção Diária & Time-to-First-Value (TTFV)

- **Onboarding 6 Etapas** + **Growth Score (12 pilares reais)** + **ASK UNION** + **Templates em 1 Clique** reduzem o atrito inicial para PMEs brasileiras sem exigência de cartão de crédito ou configuração técnica prévia (`R$ 0` inicial).
- **Evidência Ao Vivo:** capturada em `UNION_GROWTH_OS_PHASE27_EVIDENCE/06_phase27_persistent_growth_center.png` após transições reais `Planejado -> Concluído -> Replanejado`.
