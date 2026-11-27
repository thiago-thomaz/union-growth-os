"use client";

import React, { useState } from "react";
import {
  Activity,
  ArrowRight,
  Bot,
  Calendar,
  CheckCircle2,
  Compass,
  FilePlus2,
  Megaphone,
  Play,
  Radar,
  RefreshCw,
  SearchCheck,
  Send,
  Sparkles,
  Star,
  UserPlus,
  X,
  XCircle,
} from "lucide-react";
import { LegacyMenuId, getResourceMeta } from "@/lib/navigation";
import { UIMode, simplifyTechnicalText } from "@/lib/plainLanguage";
import { EmptyState, MetricStrip, OriginBadge, StatusPill } from "@/components/DesignSystem";
import { BusinessHealthAndScoreDrawer } from "@/components/GrowthCommandCenter";
import { ProgressiveOnboardingWizard } from "@/components/BrandAndOnboardingHub";

export function HomeWorkspace({
  meData,
  overviewData,
  commandCenterData,
  activationData,
  crmData,
  marketingData,
  approvalsData,
  integrationsData,
  systemAlerts,
  contentFactoryItems,
  uiMode,
  showOnboardingWizard,
  setShowOnboardingWizard,
  favoriteIds,
  recentIds,
  onboardingDismissed,
  onDismissOnboarding,
  onRestoreOnboarding,
  onNavigate,
  onRunOrchestrator,
  apiFetch,
  onReload,
  showNotice,
}: {
  meData: any;
  overviewData: any;
  commandCenterData: any;
  activationData?: any;
  agentsData?: any;
  crmData: any;
  marketingData: any;
  approvalsData: any[];
  integrationsData: any[];
  systemAlerts: any[];
  contentFactoryItems: any[];
  automationsData?: any;
  aiEnginesConfig?: any;
  uiMode: UIMode;
  showOnboardingWizard: boolean;
  setShowOnboardingWizard: React.Dispatch<React.SetStateAction<boolean>>;
  favoriteIds: LegacyMenuId[];
  recentIds: LegacyMenuId[];
  onboardingDismissed: boolean;
  onDismissOnboarding: () => void;
  onRestoreOnboarding: () => void;
  onNavigate: (view: LegacyMenuId) => void;
  onRunOrchestrator: () => Promise<void>;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  showNotice: (msg: string) => void;
}) {
  const [askInput, setAskInput] = useState("");
  const [askBusy, setAskBusy] = useState(false);
  const [askResult, setAskResult] = useState<any>(null);
  const [execBusyId, setExecBusyId] = useState("");
  const [healthDrawerOpen, setHealthDrawerOpen] = useState(false);

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Bom dia" : hour < 18 ? "Boa tarde" : "Boa noite";
  const tenantName = meData?.active_tenant?.brand_name || "sua empresa";
  const firstName = meData?.user?.full_name?.split(" ")[0] || "Diretor";

  // Dados reais consolidados (sem duplicação nem números fictícios)
  const gs = commandCenterData?.growth_score || { score: 0, max_score: 100 };
  const briefing = commandCenterData?.ceo_briefing || overviewData?.ceo_briefing || {};
  const opportunities: any[] = commandCenterData?.opportunity_radar || [];
  const execActions: any[] = commandCenterData?.executive_actions || [];
  const health: any[] = commandCenterData?.business_health || [];

  const realLeads = (crmData?.leads || []).filter(
    (l: any) => !["TEST", "SIMULATION", "DEMO"].includes((l.data_origin || "REAL").toUpperCase())
  );
  const openDealsCount = (crmData?.deals || []).filter(
    (d: any) => !["CLOSED_WON", "CLOSED_LOST"].includes((d.stage || d.status || "").toUpperCase())
  ).length;
  const campaignsCount = (marketingData?.campaigns || []).length;
  const pendingApprovals = (approvalsData || []).filter((a: any) => a.status === "PENDING");
  const openAlerts = (systemAlerts || []).filter((a: any) => a.status !== "RESOLVED");
  const recentLogs: any[] = overviewData?.recent_agent_logs || [];

  // Progresso discreto de Onboarding (6 Etapas)
  const currentObStep = Math.min(6, Math.max(1, Number(meData?.active_tenant?.onboarding_step || 1)));
  const obPct = Math.round((currentObStep / 6) * 100);

  // Consolidar "Prioridades de hoje" (fonte única: Executive Action Center + pendências reais críticas)
  interface UnifiedPriority {
    id: string;
    title: string;
    reason: string;
    priority: "ALTA" | "MÉDIA" | "NORMAL";
    actionLabel: string;
    targetView: LegacyMenuId;
    canDecide?: boolean;
    meta?: string;
  }

  const prioritiesList: UnifiedPriority[] = [];
  if (pendingApprovals.length > 0) {
    prioritiesList.push({
      id: "pending-approvals",
      title: `${pendingApprovals.length} decisão(ões) aguardando aprovação`,
      reason: "Ações externas ou comerciais aguardam sua confirmação em Meu Trabalho.",
      priority: "ALTA",
      actionLabel: "Revisar agora",
      targetView: "approvals",
    });
  }
  if (openAlerts.length > 0) {
    prioritiesList.push({
      id: "open-alerts",
      title: `${openAlerts.length} alerta(s) em monitoramento`,
      reason: simplifyTechnicalText(openAlerts[0]?.title || "Há avisos abertos que merecem atenção.", uiMode),
      priority: "ALTA",
      actionLabel: "Verificar",
      targetView: "my_work",
    });
  }
  for (const act of execActions) {
    if (prioritiesList.length >= (uiMode === "SIMPLE" ? 5 : 8)) break;
    prioritiesList.push({
      id: act.id,
      title: act.what_to_do,
      reason: simplifyTechnicalText(`${act.why_do_it} (${act.expected_result})`, uiMode),
      priority: act.risk === "ALTO" ? "ALTA" : "MÉDIA",
      actionLabel: "Executar",
      targetView: act.target_view || "overview",
      canDecide: true,
      meta: `${act.estimated_time || "Rápido"} • Custo R$ ${act.cost_brl ?? 0}`,
    });
  }
  if (realLeads.length > 0 && prioritiesList.length < 4) {
    const newLeadsCount = realLeads.filter((l: any) => l.pipeline_stage === "NEW_LEAD").length;
    if (newLeadsCount > 0) {
      prioritiesList.push({
        id: "crm-followup",
        title: `Responder ${newLeadsCount} novo(s) lead(s) no CRM`,
        reason: "Contatos recentes prontos para qualificação e envio de proposta.",
        priority: "MÉDIA",
        actionLabel: "Abrir CRM",
        targetView: "crm",
      });
    }
  }
  const readyContentCount = (contentFactoryItems || []).filter((c: any) => !c.published_at).length;
  if (readyContentCount > 0 && prioritiesList.length < 5) {
    prioritiesList.push({
      id: "ready-content",
      title: `${readyContentCount} conteúdo(s) pronto(s) para publicação`,
      reason: "Peças geradas disponíveis para revisão ou pacote em 1 clique.",
      priority: "NORMAL",
      actionLabel: "Ver conteúdos",
      targetView: "content_factory",
    });
  }

  const submitAskUnion = async (customPrompt?: string) => {
    const q = (customPrompt ?? askInput).trim();
    if (!q || q.length < 2) {
      showNotice("Escreva o que você deseja resolver (ex.: Quero vender mais).");
      return;
    }
    setAskBusy(true);
    try {
      const res = await apiFetch("/api/v1/growth-os/ask-union", {
        method: "POST",
        body: JSON.stringify({ prompt: q, auto_execute_safe: false }),
      });
      setAskResult(res);
      if (!customPrompt) setAskInput("");
      await onReload();
    } catch (e: any) {
      showNotice(e?.message || "Erro ao consultar ASK UNION.");
    } finally {
      setAskBusy(false);
    }
  };

  const handleActionDecision = async (actionId: string, decision: "EXECUTE" | "SCHEDULE" | "APPROVE" | "REJECT") => {
    setExecBusyId(`${actionId}:${decision}`);
    try {
      const res = await apiFetch("/api/v1/growth-os/actions/decide", {
        method: "POST",
        body: JSON.stringify({ action_id: actionId, decision }),
      });
      await onReload();
      showNotice(res?.message || "Ação processada!");
    } catch (e: any) {
      showNotice(e?.message || "Erro ao executar ação.");
    } finally {
      setExecBusyId("");
    }
  };

  // Montar Resumo Inteligente horizontal apenas com indicadores reais úteis
  const summaryMetrics = [
    {
      key: "growth_score",
      label: "Growth Score",
      value: `${gs.score}/100`,
      subtext: "Ver nota e 12 dimensões →",
      origin: "REAL",
      onClick: () => setHealthDrawerOpen(true),
    },
    {
      key: "leads",
      label: "Leads Reais",
      value: realLeads.length,
      subtext: realLeads.length > 0 ? "Base qualificada LGPD" : "Nenhum lead cadastrado",
      origin: "REAL",
      onClick: () => onNavigate("crm"),
    },
    {
      key: "deals",
      label: "Oportunidades",
      value: openDealsCount,
      subtext: openDealsCount > 0 ? "Em negociação ativa" : "Abrir funil de vendas",
      origin: openDealsCount > 0 ? "REAL" : "ESTIMATED",
      onClick: () => onNavigate("commercial"),
    },
    {
      key: "campaigns",
      label: "Campanhas",
      value: campaignsCount,
      subtext: `${readyContentCount} peça(s) pronta(s)`,
      origin: "REAL",
      onClick: () => onNavigate("marketing"),
    },
    {
      key: "pending",
      label: "Pendências",
      value: pendingApprovals.length + openAlerts.length,
      subtext: pendingApprovals.length > 0 ? "Aguardam sua decisão" : "Tudo em dia agora",
      origin: "REAL",
      onClick: () => onNavigate("my_work"),
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      {/* ÁREA 1 — CABEÇALHO CONTEXTUAL + CHECKLIST DISCRETO DE ONBOARDING */}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="space-y-1">
          <h3 className="text-xl font-semibold tracking-tight text-[var(--ug-text-primary)]">
            {greeting}, {firstName}.
          </h3>
          <p className="text-xs text-[var(--ug-text-muted)]">
            Visão executiva de <strong className="text-[var(--ug-text-secondary)] font-medium">{tenantName}</strong>{" "}
            • dados reais, sem métricas simuladas.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {onboardingDismissed ? (
            <button
              type="button"
              onClick={onRestoreOnboarding}
              className="px-2.5 py-1.5 rounded-lg border border-[var(--ug-border)] text-xs text-[var(--ug-text-secondary)] hover:text-[var(--ug-text-primary)] hover:bg-white/[0.04] transition inline-flex items-center gap-1.5"
            >
              <Compass className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
              <span>Configuração ({currentObStep}/6)</span>
            </button>
          ) : (
            <div className="inline-flex items-center gap-1 rounded-lg border border-[var(--ug-border)] bg-[var(--ug-surface)] px-2.5 py-1">
              <button
                type="button"
                onClick={() => setShowOnboardingWizard((v) => !v)}
                className="inline-flex items-center gap-2 text-xs text-[var(--ug-text-secondary)] hover:text-[var(--ug-text-primary)] transition"
              >
                <Compass className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
                <span>Onboarding 6 Etapas</span>
                <span className="text-[11px] font-medium text-indigo-400 tabular-nums">
                  {currentObStep}/6 ({obPct}%)
                </span>
              </button>
              <button
                type="button"
                onClick={onDismissOnboarding}
                aria-label="Dispensar checklist de onboarding"
                title="Ocultar barra de onboarding"
                className="p-0.5 rounded text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)] hover:bg-white/[0.06]"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}

          <button
            type="button"
            onClick={() => setHealthDrawerOpen(true)}
            className="px-2.5 py-1.5 rounded-lg border border-[var(--ug-border)] text-xs font-medium text-[var(--ug-text-secondary)] hover:text-[var(--ug-text-primary)] hover:bg-white/[0.04] transition inline-flex items-center gap-1.5"
          >
            <Activity className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
            <span>Saúde ({health.length || 12} pilares)</span>
          </button>

          <button
            type="button"
            onClick={onRunOrchestrator}
            className="px-3 py-1.5 rounded-lg bg-white/[0.05] hover:bg-white/[0.09] border border-[var(--ug-border)] text-xs font-medium text-[var(--ug-text-primary)] transition inline-flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
            <span>Analisar Agora</span>
          </button>
        </div>
      </div>

      {/* Onboarding Progressivo sob demanda (só abre quando solicitado) */}
      {showOnboardingWizard && (
        <ProgressiveOnboardingWizard
          apiFetch={apiFetch}
          onReload={onReload}
          onNavigate={onNavigate}
          onClose={() => setShowOnboardingWizard(false)}
          showNotice={showNotice}
        />
      )}

      {/* ÁREA 6 (CENTRAL) — ASK UNION SPOTLIGHT STRIP */}
      <section aria-label="Ask Union — Assistente de Crescimento" className="ug-spotlight-strip rounded-2xl p-4 space-y-2.5">
        <div className="flex items-center justify-between gap-2 text-[11px]">
          <span className="font-semibold tracking-wider text-indigo-400 inline-flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
            <span>ASK UNION</span>
          </span>
          <span className="text-[var(--ug-text-muted)] hidden sm:inline">Assistente conectado aos seus dados reais</span>
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submitAskUnion();
          }}
          className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2"
        >
          <div className="flex-1 flex items-center gap-2.5 px-3 py-2 rounded-xl bg-[var(--ug-bg)] border border-[var(--ug-border)] focus-within:border-indigo-500/60 transition">
            <input
              id="ug-ask-union-input"
              value={askInput}
              onChange={(e) => setAskInput(e.target.value)}
              aria-label="Perguntar ao Ask Union"
              placeholder={`O que você quer resolver hoje em ${tenantName}?`}
              className="w-full bg-transparent text-xs sm:text-sm text-[var(--ug-text-primary)] placeholder:text-[var(--ug-text-muted)] focus:outline-none border-none"
            />
          </div>
          <button
            type="submit"
            disabled={askBusy}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold inline-flex items-center justify-center gap-1.5 shrink-0 transition"
          >
            <Send className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{askBusy ? "Analisando..." : "Perguntar ao Ask Union"}</span>
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-2 text-[11px]">
          <span className="text-[var(--ug-text-muted)]">Sugestões rápidas:</span>
          {[
            "Quero vender mais",
            "Quero divulgar meu site nas redes",
            "Quando entrar um lead, analisar e avisar",
          ].map((pill) => (
            <button
              key={pill}
              type="button"
              onClick={() => submitAskUnion(pill)}
              className="px-2.5 py-0.5 rounded-full bg-white/[0.04] hover:bg-white/[0.08] border border-[var(--ug-border)] text-[var(--ug-text-secondary)] hover:text-[var(--ug-text-primary)] transition"
            >
              {pill}
            </button>
          ))}
        </div>

        {askResult && (
          <div className="pt-3 border-t border-[var(--ug-border)] space-y-2.5 text-xs ug-fade-in">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-semibold text-[var(--ug-text-primary)]">
                Plano Estruturado ({askResult.intent})
              </span>
              <OriginBadge origin="REAL" />
            </div>
            <p className="text-[var(--ug-text-secondary)] leading-relaxed">{askResult.diagnosis}</p>
            <ul className="space-y-1 text-[var(--ug-text-secondary)] list-disc pl-4">
              {(askResult.plan_steps || []).map((st: string, i: number) => (
                <li key={i}>{simplifyTechnicalText(st, uiMode)}</li>
              ))}
            </ul>
            {(askResult.suggested_actions || []).length > 0 && (
              <div className="flex flex-wrap gap-2 pt-1">
                {askResult.suggested_actions.map((sa: any) => (
                  <div key={sa.id} className="inline-flex items-center gap-1.5">
                    {sa.id !== "act-create-conv-auto" && (
                      <button
                        type="button"
                        disabled={execBusyId === `${sa.id}:EXECUTE`}
                        onClick={() => handleActionDecision(sa.id, "EXECUTE")}
                        className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-medium inline-flex items-center gap-1"
                      >
                        <Play className="w-3 h-3" aria-hidden="true" />
                        <span>{execBusyId === `${sa.id}:EXECUTE` ? "Executando..." : sa.label}</span>
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => onNavigate(sa.target_view)}
                      className="px-2.5 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-secondary)] text-[11px]"
                    >
                      Abrir tela →
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </section>

      {/* ÁREA 2 — RESUMO INTELIGENTE (FAIXA HORIZONTAL STRIPE-STYLE) */}
      <section aria-label="Resumo inteligente do negócio">
        <MetricStrip items={summaryMetrics} />
      </section>

      {/* ÁREAS 3, 4 & 5 — FOCO DO DIA (PRIORIDADES + ATIVIDADE) E INTELIGÊNCIA (AI CEO + OPORTUNIDADES) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Coluna Principal (7 cols): Prioridades de Hoje + Atividade do Sistema */}
        <div className="lg:col-span-7 space-y-6">
          <section aria-label="Prioridades de hoje" className="space-y-2.5">
            <div className="flex items-center justify-between gap-2">
              <h4 className="text-[13px] font-semibold text-[var(--ug-text-primary)]">
                Prioridades de hoje
              </h4>
              <button
                type="button"
                onClick={() => onNavigate("my_work")}
                className="text-xs font-medium text-indigo-400 hover:underline inline-flex items-center gap-1"
              >
                <span>Ver tudo em Meu Trabalho</span>
                <ArrowRight className="w-3 h-3" aria-hidden="true" />
              </button>
            </div>

            {prioritiesList.length === 0 ? (
              <EmptyState
                icon={<CheckCircle2 className="w-5 h-5" />}
                title="Sem pendências urgentes agora"
                description="Use o ASK UNION acima ou os atalhos abaixo para iniciar campanhas ou cadastrar novos leads."
                actionLabel="Abrir Meu Trabalho"
                onAction={() => onNavigate("my_work")}
              />
            ) : (
              <div className="ug-card rounded-xl divide-y divide-white/[0.05]">
                {prioritiesList.map((item) => (
                  <div
                    key={item.id}
                    className="px-4 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-white/[0.02] transition"
                  >
                    <div className="flex items-start gap-2.5 min-w-0">
                      <span
                        className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${item.priority === "ALTA"
                            ? "bg-amber-400"
                            : item.priority === "MÉDIA"
                              ? "bg-indigo-400"
                              : "bg-emerald-400"
                          }`}
                        aria-hidden="true"
                      />
                      <div className="min-w-0 space-y-0.5">
                        <div className="text-xs font-medium text-[var(--ug-text-primary)]">{item.title}</div>
                        <p className="text-[11px] text-[var(--ug-text-muted)] line-clamp-2">{item.reason}</p>
                        {item.meta && (
                          <div className="text-[10px] text-[var(--ug-text-muted)]">{item.meta}</div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0 pl-4 sm:pl-0">
                      {item.canDecide ? (
                        <>
                          <button
                            type="button"
                            disabled={Boolean(execBusyId)}
                            onClick={() => handleActionDecision(item.id, "EXECUTE")}
                            className="px-2.5 py-1 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-medium inline-flex items-center gap-1"
                          >
                            <Play className="w-3 h-3" aria-hidden="true" />
                            <span>Executar</span>
                          </button>
                          {uiMode === "ADVANCED" && (
                            <button
                              type="button"
                              disabled={Boolean(execBusyId)}
                              onClick={() => handleActionDecision(item.id, "SCHEDULE")}
                              aria-label={`Agendar ${item.title}`}
                              className="p-1.5 rounded-md border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-secondary)]"
                            >
                              <Calendar className="w-3 h-3" />
                            </button>
                          )}
                          <button
                            type="button"
                            disabled={Boolean(execBusyId)}
                            onClick={() => handleActionDecision(item.id, "REJECT")}
                            aria-label={`Ignorar ${item.title}`}
                            className="p-1.5 rounded-md hover:bg-red-500/15 text-[var(--ug-text-muted)] hover:text-red-400"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                          </button>
                        </>
                      ) : null}
                      <button
                        type="button"
                        onClick={() => onNavigate(item.targetView)}
                        className="px-2.5 py-1 rounded-md border border-[var(--ug-border)] hover:bg-white/[0.05] text-[11px] font-medium text-[var(--ug-text-secondary)] hover:text-[var(--ug-text-primary)]"
                      >
                        {item.canDecide ? "Abrir →" : `${item.actionLabel} →`}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Atividade do sistema */}
          <section aria-label="Atividade do sistema" className="space-y-2.5">
            <div className="flex items-center justify-between gap-2">
              <h4 className="text-[13px] font-semibold text-[var(--ug-text-primary)]">
                Atividade do sistema
              </h4>
              <button
                type="button"
                onClick={() => onNavigate(uiMode === "ADVANCED" ? "audit" : "my_work")}
                className="text-xs font-medium text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)]"
              >
                Ver histórico →
              </button>
            </div>

            {recentLogs.length === 0 ? (
              <div className="ug-card rounded-xl px-4 py-4 text-xs text-[var(--ug-text-muted)]">
                Nenhuma atividade recente registrada nesta empresa ainda.
              </div>
            ) : (
              <div className="ug-card rounded-xl divide-y divide-white/[0.05]">
                {recentLogs.slice(0, 4).map((log: any, idx: number) => (
                  <div key={log.id || idx} className="px-4 py-2.5 flex items-center justify-between gap-3 text-xs">
                    <div className="min-w-0">
                      <div className="font-medium text-[var(--ug-text-primary)] truncate">
                        {log.agent_name || log.agent_id} • {log.task_name || "Execução"}
                      </div>
                      <div className="text-[11px] text-[var(--ug-text-muted)] truncate">
                        {simplifyTechnicalText(log.summary || "Concluído sem pendências", uiMode)}
                      </div>
                    </div>
                    <StatusPill
                      status={log.status === "FAILED" ? "FAILED" : log.status === "PENDING_APPROVAL" ? "PENDING" : "EXECUTED"}
                      label={log.status === "COMPLETED" ? "Executado" : log.status}
                    />
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Coluna Lateral (5 cols): AI CEO Briefing + Oportunidades */}
        <div className="lg:col-span-5 space-y-6">
          <section aria-label="AI CEO Briefing" className="space-y-2.5">
            <div className="flex items-center justify-between gap-2">
              <h4 className="text-[13px] font-semibold text-[var(--ug-text-primary)] flex items-center gap-1.5">
                <Bot className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
                <span>AI CEO Briefing</span>
              </h4>
              <OriginBadge origin="REAL" />
            </div>

            <div className="ug-card rounded-xl p-4 space-y-3 text-xs">
              <p className="text-[var(--ug-text-secondary)] leading-relaxed">
                {simplifyTechnicalText(
                  briefing.summary || briefing.headline || "Resumo estratégico baseado nos registros atuais.",
                  uiMode
                )}
              </p>

              {(briefing.day_plan || []).length > 0 && (
                <div className="pt-2.5 border-t border-[var(--ug-border-subtle)] space-y-1">
                  <div className="text-[11px] font-semibold text-indigo-300">Plano de Hoje</div>
                  <ul className="space-y-1 text-[11px] text-[var(--ug-text-secondary)] list-disc pl-4">
                    {briefing.day_plan.slice(0, 3).map((d: string, i: number) => (
                      <li key={i}>{simplifyTechnicalText(d, uiMode)}</li>
                    ))}
                  </ul>
                </div>
              )}

              {(briefing.week_plan || []).length > 0 && (
                <div className="pt-2.5 border-t border-[var(--ug-border-subtle)] space-y-1">
                  <div className="text-[11px] font-semibold text-emerald-400">Foco da Semana</div>
                  <ul className="space-y-1 text-[11px] text-[var(--ug-text-secondary)] list-disc pl-4">
                    {briefing.week_plan.slice(0, 3).map((w: string, i: number) => (
                      <li key={i}>{simplifyTechnicalText(w, uiMode)}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </section>

          <section aria-label="Oportunidades" className="space-y-2.5">
            <div className="flex items-center justify-between gap-2">
              <h4 className="text-[13px] font-semibold text-[var(--ug-text-primary)] flex items-center gap-1.5">
                <Radar className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
                <span>Oportunidades ({opportunities.length})</span>
              </h4>
              <span className="text-[11px] text-[var(--ug-text-muted)]">Custo R$ 0,00</span>
            </div>

            {opportunities.length === 0 ? (
              <div className="ug-card rounded-xl px-4 py-4 text-xs text-[var(--ug-text-muted)]">
                Nenhuma lacuna aberta nos pilares avaliados agora.
              </div>
            ) : (
              <div className="ug-card rounded-xl divide-y divide-white/[0.05]">
                {opportunities.slice(0, uiMode === "SIMPLE" ? 4 : 6).map((op: any) => (
                  <div key={op.id} className="px-4 py-3 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium text-[var(--ug-text-primary)] truncate">
                        {op.category}: {op.name}
                      </span>
                      <span
                        className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${op.priority === "ALTA"
                            ? "bg-amber-500/12 text-amber-300"
                            : "bg-white/[0.05] text-[var(--ug-text-muted)]"
                          }`}
                      >
                        {op.priority}
                      </span>
                    </div>
                    <p className="text-[11px] text-[var(--ug-text-muted)]">
                      {simplifyTechnicalText(op.description, uiMode)}
                    </p>
                    <div className="flex items-center justify-between gap-2 text-[11px]">
                      <span className="text-[var(--ug-text-muted)]">
                        Impacto: <strong className="text-[var(--ug-text-secondary)]">{op.estimated_impact}</strong>
                      </span>
                      <button
                        type="button"
                        onClick={() => onNavigate(op.target_view)}
                        className="text-indigo-400 hover:underline font-medium inline-flex items-center gap-1 whitespace-nowrap shrink-0"
                      >
                        <span>{op.next_action_label}</span>
                        <ArrowRight className="w-3 h-3" aria-hidden="true" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>

      {/* ACESSOS RÁPIDOS + MARCOS DE ATIVAÇÃO (TTFV) */}
      {activationData && !activationData.first_value_achieved && (
        <section aria-label="Marcos iniciais de ativação" className="ug-card rounded-xl px-4 py-3 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" aria-hidden="true" />
            <span className="font-medium text-[var(--ug-text-primary)]">
              Primeira entrega de valor ({activationData.completed_milestones}/{activationData.total_milestones} marcos)
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {(activationData.milestones || []).filter((m: any) => !m.done).slice(0, 3).map((m: any) => (
              <button
                key={m.key}
                type="button"
                onClick={() => onNavigate(m.target_view)}
                className="px-2.5 py-1 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[11px] text-[var(--ug-text-secondary)]"
              >
                {m.label} →
              </button>
            ))}
          </div>
        </section>
      )}

      {/* ACESSOS RÁPIDOS DISCRETOS */}
      <section aria-label="Ações rápidas" className="pt-2 border-t border-[var(--ug-border-subtle)] flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] text-[var(--ug-text-muted)] mr-1">Ações rápidas:</span>
          {[
            { label: "Novo Lead", target: "crm" as LegacyMenuId, icon: <UserPlus className="w-3.5 h-3.5 text-emerald-400" /> },
            { label: "Criar Campanha", target: "marketing" as LegacyMenuId, icon: <Megaphone className="w-3.5 h-3.5 text-indigo-400" /> },
            { label: "Auditoria SEO", target: "seo" as LegacyMenuId, icon: <SearchCheck className="w-3.5 h-3.5 text-sky-400" /> },
            { label: "Nova Proposta", target: "multibusiness" as LegacyMenuId, icon: <FilePlus2 className="w-3.5 h-3.5 text-purple-400" /> },
          ].map((qa) => (
            <button
              key={qa.target}
              type="button"
              onClick={() => onNavigate(qa.target)}
              className="px-2.5 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-xs font-medium text-[var(--ug-text-secondary)] hover:text-[var(--ug-text-primary)] inline-flex items-center gap-1.5 transition"
            >
              {qa.icon}
              <span>{qa.label}</span>
            </button>
          ))}
        </div>

        {(favoriteIds.length > 0 || recentIds.length > 0) && (
          <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
            <Star className="w-3 h-3 text-amber-400" aria-hidden="true" />
            {(favoriteIds.length > 0 ? favoriteIds : recentIds).slice(0, 3).map((id) => {
              const meta = getResourceMeta(id);
              if (!meta) return null;
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => onNavigate(id)}
                  className="px-2 py-0.5 rounded bg-white/[0.04] hover:bg-white/[0.08] text-[var(--ug-text-secondary)]"
                >
                  {meta.name.split(" — ")[0]}
                </button>
              );
            })}
          </div>
        )}
      </section>

      <BusinessHealthAndScoreDrawer
        open={healthDrawerOpen}
        onClose={() => setHealthDrawerOpen(false)}
        commandCenter={commandCenterData}
        uiMode={uiMode}
      />
    </div>
  );
}
