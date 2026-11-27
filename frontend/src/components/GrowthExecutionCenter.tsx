"use client";

import React, { useEffect, useState } from "react";
import { Calendar, CheckCircle2, Play, Rocket, Sparkles, Target } from "lucide-react";
import { FilterTabBar, MetricStrip, OriginBadge, PlainOrientationBar, StatusPill } from "@/components/DesignSystem";

export function GrowthExecutionCenter({
  meData,
  apiFetch,
  onReload,
  onNavigate,
  showNotice,
}: {
  meData: any;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  onNavigate: (view: any) => void;
  showNotice: (msg: string) => void;
}) {
  const tenant = meData?.active_tenant || {};
  const [objective, setObjective] = useState("Quero conseguir mais clientes e aumentar vendas");
  const [productOrService, setProductOrService] = useState(
    (tenant.services?.[0] || tenant.products?.[0] || tenant.niche || "").toString()
  );
  const [audience, setAudience] = useState((tenant.target_audience || "").toString());
  const [region, setRegion] = useState("Brasil");
  const [budget, setBudget] = useState("0");
  const [deadlineDays, setDeadlineDays] = useState("90");
  const [planData, setPlanData] = useState<any>(null);
  const [loadingPlan, setLoadingPlan] = useState(false);
  const [execBusyStep, setExecBusyStep] = useState("");
  const [horizonFilter, setHorizonFilter] = useState("ALL");

  useEffect(() => {
    let active = true;
    apiFetch("/api/v1/growth-os/growth-plan/current")
      .then((res) => {
        if (active && res?.plan) {
          setPlanData(res.plan);
        }
      })
      .catch(() => null);
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [meData?.active_tenant?.id]);

  const quickGoals = [
    "Quero conseguir mais clientes",
    "Quero vender mais no CRM",
    "Quero aparecer no Google (SEO)",
    "Quero divulgar minha empresa",
  ];

  const generatePlan = async (overrideObjective?: string) => {
    setLoadingPlan(true);
    try {
      const res = await apiFetch("/api/v1/growth-os/growth-plan", {
        method: "POST",
        body: JSON.stringify({
          objective: (overrideObjective ?? objective).trim() || "Aumentar clientes e vendas",
          product_or_service: productOrService.trim(),
          target_audience: audience.trim(),
          region: region.trim() || "Brasil",
          budget_brl: Number(budget) || 0,
          deadline_days: Number(deadlineDays) || 90,
        }),
      });
      setPlanData(res);
      showNotice("Plano de Crescimento (0 / 7 / 30 / 90 dias) salvo no PostgreSQL!");
    } catch (err: any) {
      showNotice(err?.message || "Erro ao montar plano de crescimento.");
    } finally {
      setLoadingPlan(false);
    }
  };

  const updatePersistedStep = async (step: any, command: "EXECUTE" | "COMPLETE" | "CANCEL" | "REPLAN", nextHorizon?: string) => {
    setExecBusyStep(step.step_id);
    try {
      if (step.db_id) {
        const res = await apiFetch(`/api/v1/growth-os/growth-plan/steps/${step.db_id}`, {
          method: "PATCH",
          body: JSON.stringify({ command, horizon: nextHorizon }),
        });
        setPlanData((prev: any) => {
          if (!prev) return prev;
          return {
            ...prev,
            actions: (prev.actions || []).map((a: any) =>
              a.db_id === step.db_id ? { ...a, ...res.step } : a
            ),
          };
        });
        await onReload();
        if (command === "EXECUTE" && res.execution?.target_view) {
          onNavigate(res.execution.target_view);
        }
        showNotice(
          res.execution?.detail ||
            `Etapa '${step.title}' atualizada para ${res.step?.status || command}!`
        );
      } else {
        const res = await apiFetch("/api/v1/growth-os/growth-plan/execute-step", {
          method: "POST",
          body: JSON.stringify({ action_type: step.action_type }),
        });
        await onReload();
        if (res.target_view) onNavigate(res.target_view);
        showNotice(res.detail || res.message || "Etapa executada!");
      }
    } catch (err: any) {
      showNotice(err?.message || "Erro ao atualizar etapa.");
    } finally {
      setExecBusyStep("");
    }
  };

  const executeStep = async (step: any) => updatePersistedStep(step, "EXECUTE");

  const visibleActions = (planData?.actions || []).filter(
    (a: any) => horizonFilter === "ALL" || a.horizon === horizonFilter
  );

  return (
    <div className="space-y-5 max-w-7xl mx-auto ug-fade-in">
      <PlainOrientationBar
        whatIsIt="Centro de Crescimento Executivo (0 / 7 / 30 / 90 dias)"
        whyUseIt="Transforma seu objetivo comercial em ações reais sem você precisar entender ferramentas técnicas"
        nextStep="Escolha ou escreva seu objetivo e gere seu plano priorizado abaixo"
      />

      <section className="ug-card rounded-xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold text-[var(--ug-text-primary)] flex items-center gap-2">
              <Rocket className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              <span>Qual resultado você quer alcançar agora?</span>
            </h3>
            <p className="text-xs text-[var(--ug-text-muted)] mt-0.5">
              Os dados já cadastrados da marca <strong>{tenant.brand_name || "sua empresa"}</strong> são lidos automaticamente.
            </p>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {quickGoals.map((g) => (
              <button
                key={g}
                type="button"
                onClick={() => {
                  setObjective(g);
                  generatePlan(g);
                }}
                className="px-2.5 py-1 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[11px] text-[var(--ug-text-secondary)] transition"
              >
                {g}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-6 gap-3 text-xs items-end">
          <div className="md:col-span-2">
            <label htmlFor="ug-gc-objective" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">
              Objetivo Principal
            </label>
            <input
              id="ug-gc-objective"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="Ex.: Conseguir 20 novos clientes B2B"
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          <div>
            <label htmlFor="ug-gc-offer" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">
              Produto / Serviço
            </label>
            <input
              id="ug-gc-offer"
              value={productOrService}
              onChange={(e) => setProductOrService(e.target.value)}
              placeholder="Automação / Consultoria"
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          <div>
            <label htmlFor="ug-gc-region" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">
              Região
            </label>
            <input
              id="ug-gc-region"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          <div>
            <label htmlFor="ug-gc-budget" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">
              Verba Opcional (R$)
            </label>
            <input
              id="ug-gc-budget"
              type="number"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)] tabular-nums"
            />
          </div>
          <button
            type="button"
            disabled={loadingPlan}
            onClick={() => generatePlan()}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white text-xs font-semibold flex items-center justify-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{loadingPlan ? "Calculando..." : "Gerar Plano 0–90d"}</span>
          </button>
        </div>
      </section>

      {planData && (
        <div className="space-y-4">
          <MetricStrip
            items={[
              {
                key: "leads",
                label: "Leads Reais Hoje",
                value: planData.real_baseline?.real_leads_count ?? 0,
                subtext: `${planData.real_baseline?.hot_uncontacted_count ?? 0} quente(s) sem retorno`,
                origin: "REAL",
                source: "CRM PostgreSQL",
                period: "Base atual",
              },
              {
                key: "stalled",
                label: "Negócios Abertos / Parados",
                value: planData.real_baseline?.stalled_deals_count ?? 0,
                subtext: "Oportunidades prioritárias",
                origin: "REAL",
                source: "Revenue Engine",
                period: "Agora",
              },
              {
                key: "content",
                label: "Peças Prontas",
                value: planData.real_baseline?.content_items_count ?? 0,
                subtext: `${planData.real_baseline?.campaigns_count ?? 0} campanha(s)`,
                origin: "REAL",
                source: "Fábrica de Conteúdo",
                period: "Acumulado",
              },
              {
                key: "seo",
                label: "Auditorias SEO HTTP",
                value: planData.real_baseline?.seo_audits_count ?? 0,
                subtext: `${planData.real_baseline?.connected_integrations_count ?? 0}/18 integrações`,
                origin: "REAL",
                source: "Motor SEO HTTP",
                period: "Histórico",
              },
            ]}
          />

          <div className="ug-card rounded-xl overflow-hidden">
            <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-emerald-400" aria-hidden="true" />
                <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">Plano de Execução Priorizado</h4>
                <OriginBadge origin="ESTIMATED" />
              </div>
              <FilterTabBar
                activeId={horizonFilter}
                onChange={setHorizonFilter}
                tabs={[
                  { id: "ALL", label: "Todos", count: (planData.actions || []).length },
                  { id: "TODAY", label: "Hoje", count: (planData.horizons?.TODAY || []).length },
                  { id: "NEXT_7_DAYS", label: "7 Dias", count: (planData.horizons?.NEXT_7_DAYS || []).length },
                  { id: "NEXT_30_DAYS", label: "30 Dias", count: (planData.horizons?.NEXT_30_DAYS || []).length },
                  { id: "NEXT_90_DAYS", label: "90 Dias", count: (planData.horizons?.NEXT_90_DAYS || []).length },
                ]}
              />
            </div>

            <div className="divide-y divide-white/[0.05]">
              {visibleActions.map((step: any) => (
                <div key={step.step_id} className="px-5 py-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4 text-xs">
                  <div className="space-y-1.5 min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 font-semibold text-[10px]">
                        <Calendar className="w-3 h-3 inline mr-1" aria-hidden="true" />
                        {step.horizon_label}
                      </span>
                      <span className="font-semibold text-[var(--ug-text-primary)] text-sm">{step.title}</span>
                      <OriginBadge origin={step.probability_origin} />
                      {step.status && (
                        <StatusPill
                          status={
                            step.status === "COMPLETED"
                              ? "EXECUTED"
                              : step.status === "IN_PROGRESS"
                              ? "RUNNING"
                              : step.status === "CANCELLED"
                              ? "BLOCKED"
                              : "PENDING"
                          }
                          label={
                            step.status === "COMPLETED"
                              ? "Concluído"
                              : step.status === "IN_PROGRESS"
                              ? "Em Execução"
                              : step.status === "REPLANNED"
                              ? "Replanejado"
                              : step.status === "CANCELLED"
                              ? "Cancelado"
                              : "Planejado"
                          }
                        />
                      )}
                      {typeof step.priority_score === "number" && (
                        <span className="px-2 py-0.5 rounded bg-white/[0.06] text-[10px] font-mono text-[var(--ug-text-secondary)]">
                          Prioridade: {step.priority_score}/100
                        </span>
                      )}
                    </div>
                    <p className="text-[var(--ug-text-secondary)]">{step.why}</p>
                    <div className="flex flex-wrap gap-3 text-[11px] text-[var(--ug-text-muted)] tabular-nums">
                      <span>Impacto: <strong>{step.impact_score}/10</strong></span>
                      <span>Esforço: <strong>{step.effort_score}/10</strong></span>
                      <span>Custo: <strong>R$ {step.cost_brl}</strong></span>
                      <span>Probabilidade (est.): <strong>{step.probability_pct}%</strong></span>
                      <span>Tempo: <strong>{step.time_estimate}</strong></span>
                      <span>Risco: <strong>{step.risk_level}</strong></span>
                      {step.owner_label && <span>Responsável: <strong>{step.owner_label}</strong></span>}
                      {step.due_date && <span>Prazo: <strong>{step.due_date}</strong></span>}
                    </div>
                    {step.success_metric && (
                      <div className="text-[11px] text-emerald-400">Meta de sucesso: {step.success_metric}</div>
                    )}
                    {!step.success_metric && (
                      <div className="text-[11px] text-emerald-400">Resultado esperado: {step.estimated_outcome}</div>
                    )}
                    {(step.evidence || step.next_action) && (
                      <div className="text-[11px] text-[var(--ug-text-muted)]">
                        {[step.evidence && `Evidência: ${step.evidence}`, step.next_action && `Próxima ação: ${step.next_action}`]
                          .filter(Boolean)
                          .join(" • ")}
                      </div>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2 shrink-0">
                    {step.requires_approval && (
                      <StatusPill status="PENDING" label="Exige Confirmação" />
                    )}
                    <button
                      type="button"
                      disabled={execBusyStep === step.step_id}
                      onClick={() => executeStep(step)}
                      className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-60 text-white text-xs font-semibold flex items-center gap-1.5 transition"
                    >
                      <Play className="w-3 h-3" aria-hidden="true" />
                      <span>{execBusyStep === step.step_id ? "Executando..." : "Executar Agora"}</span>
                    </button>
                    {step.db_id > 0 && step.status !== "COMPLETED" && (
                      <button
                        type="button"
                        disabled={execBusyStep === step.step_id}
                        onClick={() => updatePersistedStep(step, "COMPLETE")}
                        className="px-2.5 py-2 rounded-lg border border-emerald-500/35 text-emerald-300 hover:bg-emerald-500/10 text-[11px] font-medium"
                      >
                        Concluir
                      </button>
                    )}
                    {step.db_id > 0 && step.status !== "REPLANNED" && (
                      <button
                        type="button"
                        disabled={execBusyStep === step.step_id}
                        onClick={() => updatePersistedStep(step, "REPLAN", "NEXT_30_DAYS")}
                        className="px-2.5 py-2 rounded-lg border border-[var(--ug-border)] text-[var(--ug-text-secondary)] hover:bg-white/[0.04] text-[11px]"
                      >
                        Replanejar
                      </button>
                    )}
                    {step.db_id > 0 && step.status !== "CANCELLED" && (
                      <button
                        type="button"
                        disabled={execBusyStep === step.step_id}
                        onClick={() => updatePersistedStep(step, "CANCEL")}
                        className="px-2.5 py-2 rounded-lg border border-red-500/30 text-red-300 hover:bg-red-500/10 text-[11px]"
                      >
                        Cancelar
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <div className="px-5 py-2.5 bg-white/[0.02] border-t border-[var(--ug-border-subtle)] text-[11px] text-[var(--ug-text-muted)] flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-amber-400 shrink-0" aria-hidden="true" />
              <span>{planData.estimates_disclaimer}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
