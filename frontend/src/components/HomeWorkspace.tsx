"use client";

import React from "react";
import {
  AlertCircle,
  ArrowRight,
  Bot,
  CheckCircle2,
  ChevronRight,
  Clock,
  Compass,
  FilePlus2,
  Megaphone,
  Plus,
  SearchCheck,
  ShieldAlert,
  Sparkles,
  Star,
  UserPlus,
  X,
} from "lucide-react";
import { LegacyMenuId, getResourceMeta } from "@/lib/navigation";
import { EmptyState, OriginBadge, StatusPill } from "@/components/DesignSystem";

interface PriorityCardItem {
  id: string;
  countLabel: string;
  title: string;
  description: string;
  severity: "urgent" | "warning" | "info" | "success";
  actionLabel: string;
  targetView: LegacyMenuId;
}

export function HomeWorkspace({
  meData,
  overviewData,
  agentsData,
  crmData,
  marketingData,
  approvalsData,
  integrationsData,
  systemAlerts,
  contentFactoryItems,
  automationsData,
  aiEnginesConfig,
  favoriteIds,
  recentIds,
  onboardingDismissed,
  onDismissOnboarding,
  onRestoreOnboarding,
  onNavigate,
  onRunOrchestrator,
}: {
  meData: any;
  overviewData: any;
  agentsData: any;
  crmData: any;
  marketingData: any;
  approvalsData: any[];
  integrationsData: any[];
  systemAlerts: any[];
  contentFactoryItems: any[];
  automationsData: any;
  aiEnginesConfig: any;
  favoriteIds: LegacyMenuId[];
  recentIds: LegacyMenuId[];
  onboardingDismissed: boolean;
  onDismissOnboarding: () => void;
  onRestoreOnboarding: () => void;
  onNavigate: (view: LegacyMenuId) => void;
  onRunOrchestrator: () => Promise<void>;
}) {
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Bom dia" : hour < 18 ? "Boa tarde" : "Boa noite";

  // Calcular checklist progressivo real de Onboarding (Seção 10)
  const hasCompany = Boolean(meData?.active_tenant?.name);
  const hasBrand = Boolean(meData?.active_tenant?.brand_name);
  const hasAnyIntegration = (integrationsData || []).some((i: any) => i.status === "CONNECTED");
  const hasAiConfigured = (aiEnginesConfig?.providers || []).some((p: any) => p.has_credential);
  const hasCampaign = (marketingData?.campaigns || []).length > 0;
  const realLeads = (crmData?.leads || []).filter((l: any) => !["TEST", "SIMULATION", "DEMO"].includes((l.data_origin || "REAL").toUpperCase()));
  const hasLeads = realLeads.length > 0;
  const hasAutomationsRun = (automationsData?.rules || []).some((r: any) => (r.run_count || 0) > 0);
  const hasReviewedOverview = Boolean(overviewData);

  const onboardingSteps: { id: string; title: string; done: boolean; target: LegacyMenuId }[] = [
    { id: "ob-1", title: "Configure sua empresa", done: hasCompany, target: "settings" },
    { id: "ob-2", title: "Configure sua marca e identidade", done: hasBrand, target: "settings" },
    { id: "ob-3", title: "Conecte suas integrações", done: hasAnyIntegration, target: "integrations" },
    { id: "ob-4", title: "Configure os motores e agentes de IA", done: hasAiConfigured, target: "ai_engines" },
    { id: "ob-5", title: "Crie sua primeira campanha", done: hasCampaign, target: "marketing" },
    { id: "ob-6", title: "Cadastre seus primeiros leads", done: hasLeads, target: "crm" },
    { id: "ob-7", title: "Ative e execute automações 24/7", done: hasAutomationsRun, target: "automations" },
    { id: "ob-8", title: "Revise seus indicadores reais", done: hasReviewedOverview, target: "finance" },
  ];
  const onboardingDoneCount = onboardingSteps.filter((s) => s.done).length;
  const onboardingPct = Math.round((onboardingDoneCount / onboardingSteps.length) * 100);

  // Bloco 1: Prioridades reais do dia (máx. 5 itens)
  const pendingApprovals = (approvalsData || []).filter((a: any) => a.status === "PENDING");
  const openAlerts = (systemAlerts || []).filter((a: any) => a.status !== "RESOLVED");
  const leadsNeedingFollowup = realLeads.filter((l: any) => l.pipeline_stage === "NEW_LEAD" || l.qualification_status === "QUALIFIED");
  const pendingIntegrations = (integrationsData || []).filter((i: any) => i.status !== "CONNECTED");
  const readyContents = (contentFactoryItems || []).filter((c: any) => !c.published_at);
  const aiExecCount = overviewData?.autonomy_status_panel?.executed_by_ai_count || 0;
  const failedExecs = (aiEnginesConfig?.recent_executions || []).filter((e: any) => e.status !== "SUCCESS");

  const priorities: PriorityCardItem[] = [];
  if (pendingApprovals.length > 0) {
    priorities.push({
      id: "pri-approvals",
      countLabel: `${pendingApprovals.length}`,
      title: `${pendingApprovals.length} ação(ões) aguardam sua aprovação`,
      description: "Decisões de alto impacto aguardando liberação humana.",
      severity: "urgent",
      actionLabel: "Revisar agora",
      targetView: "my_work",
    });
  }
  if (openAlerts.length > 0) {
    priorities.push({
      id: "pri-alerts",
      countLabel: `${openAlerts.length}`,
      title: `${openAlerts.length} alerta(s) operacional(is) em aberto`,
      description: openAlerts[0]?.title || "Verifique notificações técnicas e avisos de execução.",
      severity: "warning",
      actionLabel: "Ver alertas",
      targetView: "operational247",
    });
  }
  if (leadsNeedingFollowup.length > 0) {
    priorities.push({
      id: "pri-leads",
      countLabel: `${leadsNeedingFollowup.length}`,
      title: `${leadsNeedingFollowup.length} lead(s) pronto(s) para acompanhamento`,
      description: "Contatos no CRM que exigem avanço comercial ou proposta.",
      severity: "info",
      actionLabel: "Abrir CRM",
      targetView: "crm",
    });
  }
  if (readyContents.length > 0) {
    priorities.push({
      id: "pri-content",
      countLabel: `${readyContents.length}`,
      title: `${readyContents.length} conteúdo(s) pronto(s) na fábrica`,
      description: "Peças geradas disponíveis para revisão e publicação assistida.",
      severity: "success",
      actionLabel: "Ver conteúdos",
      targetView: "content_factory",
    });
  }
  if (pendingIntegrations.length > 0) {
    priorities.push({
      id: "pri-intg",
      countLabel: `${pendingIntegrations.length}`,
      title: `${pendingIntegrations.length} integração(ões) precisam de credenciais`,
      description: "Conecte redes sociais, anúncios ou e-mail para liberar publicação automática.",
      severity: "warning",
      actionLabel: "Configurar",
      targetView: "integrations",
    });
  }
  if (failedExecs.length > 0 && priorities.length < 5) {
    priorities.push({
      id: "pri-ai-err",
      countLabel: `${failedExecs.length}`,
      title: "Atenção na cota ou configuração do motor de IA",
      description: failedExecs[0]?.error_message || "Verifique a chave gratuita e limites em Modelos & Provedores.",
      severity: "warning",
      actionLabel: "Verificar IA",
      targetView: "ai_engines",
    });
  }
  const topPriorities = priorities.slice(0, 5);

  // Bloco 3: Resultados — Selecionar os 4 KPIs mais importantes do backend
  const keyOrder = ["revenue", "leads", "campaigns", "roi"];
  const allCards: any[] = overviewData?.metrics_cards || [];
  const essentialCards = keyOrder
    .map((k) => allCards.find((c) => c.key === k))
    .filter(Boolean);

  const severityStyles: Record<string, string> = {
    urgent: "border-red-500/40 bg-red-500/5",
    warning: "border-amber-500/40 bg-amber-500/5",
    info: "border-indigo-500/40 bg-indigo-500/5",
    success: "border-emerald-500/40 bg-emerald-500/5",
  };

  return (
    <div className="space-y-6">
      {/* Saudação discreta + contexto */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-white ug-text-primary">
            {greeting}, {meData?.user?.full_name?.split(" ")[0] || "Diretor"}.
          </h3>
          <p className="text-xs text-slate-400 ug-text-muted mt-0.5">
            Aqui está o resumo real do que precisa da sua atenção hoje em{" "}
            <strong className="text-slate-200 ug-text-primary">{meData?.active_tenant?.brand_name}</strong>.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {onboardingDismissed && (
            <button
              type="button"
              onClick={onRestoreOnboarding}
              className="px-3 py-1.5 rounded-lg border border-slate-700 text-xs text-slate-300 hover:bg-slate-800 transition flex items-center gap-1.5"
            >
              <Compass className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
              Guia Inicial ({onboardingDoneCount}/{onboardingSteps.length})
            </button>
          )}
          <button
            type="button"
            onClick={onRunOrchestrator}
            className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center gap-1.5 shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
            Executar Análise do Dia
          </button>
        </div>
      </div>

      {/* Onboarding Contextual Progressivo (Dispensável e Persistente) */}
      {!onboardingDismissed && (
        <section
          aria-label="Primeiros passos no sistema"
          className="ug-card rounded-2xl p-5 border border-indigo-500/30 bg-gradient-to-r from-indigo-950/30 via-[#0f1629] to-[#0f1629]"
        >
          <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
            <div>
              <div className="flex items-center gap-2">
                <Compass className="w-4 h-4 text-indigo-400" aria-hidden="true" />
                <h4 className="text-sm font-bold text-white ug-text-primary">
                  Primeiros Passos — Configuração Guiada ({onboardingDoneCount} de {onboardingSteps.length})
                </h4>
              </div>
              <p className="text-xs text-slate-400 ug-text-muted mt-0.5">
                Você pode navegar livremente pelo sistema a qualquer momento. Conclua quando quiser:
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs font-bold text-indigo-300">{onboardingPct}%</span>
              <button
                type="button"
                onClick={onDismissOnboarding}
                aria-label="Dispensar checklist de onboarding"
                className="px-2.5 py-1 rounded-lg text-[11px] text-slate-400 hover:text-white hover:bg-slate-800 flex items-center gap-1"
              >
                <X className="w-3.5 h-3.5" aria-hidden="true" />
                Ocultar
              </button>
            </div>
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mb-4">
            <div className="h-full bg-indigo-500 transition-all duration-300" style={{ width: `${onboardingPct}%` }} />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {onboardingSteps.map((step, i) => (
              <button
                key={step.id}
                type="button"
                onClick={() => onNavigate(step.target)}
                className={`p-2.5 rounded-xl border text-left transition flex items-center justify-between gap-2 ${
                  step.done
                    ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-200"
                    : "bg-slate-900/70 border-slate-800 hover:border-indigo-500/50 text-slate-200"
                }`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  {step.done ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" aria-hidden="true" />
                  ) : (
                    <span className="w-4 h-4 rounded-full border border-slate-600 text-[10px] flex items-center justify-center shrink-0">
                      {i + 1}
                    </span>
                  )}
                  <span className="text-xs font-medium truncate">{step.title}</span>
                </div>
                <ChevronRight className="w-3.5 h-3.5 text-slate-500 shrink-0" aria-hidden="true" />
              </button>
            ))}
          </div>
        </section>
      )}

      {/* BLOCO 1 — O QUE PRECISA DA MINHA ATENÇÃO? */}
      <section aria-label="Prioridades do dia" className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-bold text-white ug-text-primary flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-400" aria-hidden="true" />
            1. O que precisa da sua atenção agora
          </h4>
          <button
            type="button"
            onClick={() => onNavigate("my_work")}
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            Ver tudo em Meu Trabalho
            <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
          </button>
        </div>

        {topPriorities.length === 0 ? (
          <EmptyState
            icon={<CheckCircle2 className="w-5 h-5" />}
            title="Tudo sob controle no momento"
            description="Não há aprovações pendentes ou alertas críticos agora. Use o Acesso Rápido abaixo para criar novas campanhas ou cadastrar leads."
            actionLabel="Abrir Meu Trabalho"
            onAction={() => onNavigate("my_work")}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {topPriorities.map((pri) => (
              <div
                key={pri.id}
                className={`rounded-xl border p-4 flex flex-col justify-between gap-3 ${severityStyles[pri.severity]}`}
              >
                <div className="space-y-1">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-bold text-white ug-text-primary">{pri.title}</span>
                  </div>
                  <p className="text-[11px] text-slate-300 ug-text-muted leading-relaxed">{pri.description}</p>
                </div>
                <button
                  type="button"
                  onClick={() => onNavigate(pri.targetView)}
                  className="self-start inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-300 hover:text-indigo-200"
                >
                  {pri.actionLabel}
                  <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* BLOCO 2 & 3 — OPERAÇÃO DA IA + RESULTADOS REAIS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* BLOCO 2 — O QUE A IA ESTÁ FAZENDO? */}
        <section aria-label="Operação da Inteligência Artificial" className="lg:col-span-5 ug-card rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white ug-text-primary flex items-center gap-2">
              <Bot className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              2. O que a IA está fazendo
            </h4>
            <button
              type="button"
              onClick={() => onNavigate("ai_team_overview")}
              className="text-xs font-semibold text-indigo-400 hover:underline"
            >
              Gerenciar IA →
            </button>
          </div>

          <div className="grid grid-cols-2 gap-2.5">
            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
              <div className="text-[11px] text-slate-400">Agentes Disponíveis</div>
              <div className="text-lg font-bold text-white mt-0.5">{(agentsData?.agents || []).length || 11} agentes</div>
              <div className="text-[10px] text-emerald-400 mt-0.5">Autonomia Nível {meData?.active_tenant?.autonomy_default_level || 2}</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
              <div className="text-[11px] text-slate-400">Ações Executadas</div>
              <div className="text-lg font-bold text-emerald-400 mt-0.5">{aiExecCount}</div>
              <div className="text-[10px] text-slate-400 mt-0.5">
                {pendingApprovals.length} aguardando aprovação
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-slate-300">Resumo Executivo do AI CEO</span>
              <StatusPill status="EXECUTED" label="Atualizado" />
            </div>
            <p className="text-xs text-slate-200 leading-relaxed">
              {overviewData?.ceo_briefing?.headline || "Sistema operacional e pronto para análise."}
            </p>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
            <span>
              Motor IA padrão:{" "}
              <strong className="text-slate-200 uppercase">
                {aiEnginesConfig?.configuration?.default_provider_key || "gemini"}
              </strong>{" "}
              ({aiEnginesConfig?.configuration?.cost_policy_mode || "FREE_ONLY"})
            </span>
            <button
              type="button"
              onClick={() => onNavigate("ai_engines")}
              className="text-indigo-400 hover:underline font-medium"
            >
              Ver motores
            </button>
          </div>
        </section>

        {/* BLOCO 3 — O QUE ESTÁ GERANDO RESULTADOS? */}
        <section aria-label="Resultados essenciais" className="lg:col-span-7 ug-card rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white ug-text-primary flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" aria-hidden="true" />
              3. O que está gerando resultados
            </h4>
            <button
              type="button"
              onClick={() => onNavigate("finance")}
              className="text-xs font-semibold text-indigo-400 hover:underline"
            >
              Ver indicadores completos →
            </button>
          </div>

          {essentialCards.length === 0 ? (
            <EmptyState
              title="Sem indicadores registrados ainda"
              description="Cadastre seus primeiros leads, campanhas ou registros financeiros para acompanhar o desempenho real aqui."
            />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {essentialCards.map((card: any) => (
                <div key={card.key} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs text-slate-400">{card.label}</span>
                    <OriginBadge origin={card.origin} />
                  </div>
                  <div className="text-2xl font-bold text-white">{card.value}</div>
                  <div className="text-[11px] text-slate-400">{card.subtext}</div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* BLOCO 4 & 5 — ATIVIDADE RECENTE + ACESSO RÁPIDO & FAVORITOS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* BLOCO 4 — ATIVIDADE RECENTE */}
        <section aria-label="Atividade recente" className="lg:col-span-7 ug-card rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white ug-text-primary flex items-center gap-2">
              <Clock className="w-4 h-4 text-sky-400" aria-hidden="true" />
              4. Atividade recente
            </h4>
            <button
              type="button"
              onClick={() => onNavigate("audit")}
              className="text-xs font-semibold text-indigo-400 hover:underline"
            >
              Histórico completo →
            </button>
          </div>

          {(overviewData?.recent_agent_logs || []).length === 0 ? (
            <EmptyState
              title="Nenhuma atividade executada recentemente"
              description="Quando os agentes ou sua equipe executarem rotinas, os registros reais aparecerão aqui."
            />
          ) : (
            <div className="divide-y divide-slate-800/80">
              {(overviewData?.recent_agent_logs || []).slice(0, 5).map((log: any, idx: number) => (
                <div key={log.id || idx} className="py-2.5 flex items-center justify-between gap-3 text-xs">
                  <div className="min-w-0">
                    <div className="font-semibold text-white truncate">
                      {log.agent_name || log.agent_id} • {log.task_name || "Execução"}
                    </div>
                    <div className="text-[11px] text-slate-400 truncate">
                      {log.summary || "Concluído sem observações"}
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

        {/* BLOCO 5 — O QUE POSSO FAZER AGORA? (ACESSO RÁPIDO + FAVORITOS + RECENTES) */}
        <section aria-label="Acesso rápido" className="lg:col-span-5 ug-card rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-white ug-text-primary flex items-center gap-2">
              <Plus className="w-4 h-4 text-emerald-400" aria-hidden="true" />
              5. O que posso fazer agora
            </h4>
            <button
              type="button"
              onClick={() => onNavigate("all_resources")}
              className="text-xs font-semibold text-indigo-400 hover:underline"
            >
              Todos os recursos →
            </button>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {[
              { label: "Novo Lead", target: "crm" as LegacyMenuId, icon: <UserPlus className="w-3.5 h-3.5 text-emerald-400" /> },
              { label: "Criar Campanha", target: "marketing" as LegacyMenuId, icon: <Megaphone className="w-3.5 h-3.5 text-indigo-400" /> },
              { label: "Auditoria SEO", target: "seo" as LegacyMenuId, icon: <SearchCheck className="w-3.5 h-3.5 text-sky-400" /> },
              { label: "Nova Proposta PDF", target: "multibusiness" as LegacyMenuId, icon: <FilePlus2 className="w-3.5 h-3.5 text-purple-400" /> },
            ].map((qa) => (
              <button
                key={qa.target}
                type="button"
                onClick={() => onNavigate(qa.target)}
                className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-indigo-500/50 text-left transition flex items-center gap-2 text-xs font-semibold text-white"
              >
                {qa.icon}
                <span className="truncate">{qa.label}</span>
              </button>
            ))}
          </div>

          {(favoriteIds.length > 0 || recentIds.length > 0) && (
            <div className="pt-2 border-t border-slate-800 space-y-2">
              <div className="text-[11px] font-semibold text-slate-400 flex items-center gap-1.5">
                <Star className="w-3 h-3 text-amber-400" aria-hidden="true" />
                {favoriteIds.length > 0 ? "Seus Atalhos Favoritos" : "Últimos Acessados"}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(favoriteIds.length > 0 ? favoriteIds : recentIds).slice(0, 5).map((id) => {
                  const meta = getResourceMeta(id);
                  if (!meta) return null;
                  return (
                    <button
                      key={id}
                      type="button"
                      onClick={() => onNavigate(id)}
                      className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 hover:border-indigo-500/40 text-[11px] text-slate-200"
                    >
                      {meta.name.split(" — ")[0]}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
