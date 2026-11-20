"use client";

import React, { useMemo, useState } from "react";
import {
  CheckCircle2,
  Clock,
  Filter,
  Search,
  ShieldAlert,
  Sparkles,
  AlertTriangle,
  Ban,
  ArrowUpRight,
  Inbox,
} from "lucide-react";
import { LegacyMenuId } from "@/lib/navigation";
import { Drawer, EmptyState, StatusPill } from "@/components/DesignSystem";

type WorkFilter =
  | "ALL"
  | "NEEDS_ME"
  | "AI_RUNNING"
  | "PENDING_APPROVAL"
  | "COMPLETED"
  | "FAILED"
  | "BLOCKED";

export interface UnifiedWorkItem {
  id: string;
  kind: "APPROVAL" | "ALERT" | "CRM_ACTIVITY" | "CEO_TASK" | "AI_EXEC" | "INTEGRATION";
  rawId?: number | string;
  title: string;
  description: string;
  origin: string;
  priority: "ALTA" | "MÉDIA" | "BAIXA";
  statusBucket: WorkFilter;
  pillStatus: "EXECUTED" | "PENDING" | "BLOCKED" | "FAILED" | "SIMULATED" | "SANDBOX" | "NEEDS_CREDENTIALS" | "RUNNING";
  dateLabel: string;
  ownerLabel: string;
  relatedAgent?: string;
  primaryActionLabel: string;
  secondaryActionLabel?: string;
  targetMenu: LegacyMenuId;
  evidence?: string;
  canApproveInline?: boolean;
}

export function MyWorkHub({
  approvalsData,
  systemAlerts,
  ceoDailyPlan,
  crmData,
  aiEnginesConfig,
  integrationsData,
  meData,
  apiFetch,
  onReload,
  onNavigate,
  showNotice,
}: {
  approvalsData: any[];
  systemAlerts: any[];
  ceoDailyPlan: any;
  crmData: any;
  aiEnginesConfig: any;
  integrationsData: any[];
  meData: any;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  onNavigate: (view: LegacyMenuId) => void;
  showNotice: (msg: string) => void;
}) {
  const [filter, setFilter] = useState<WorkFilter>("ALL");
  const [search, setSearch] = useState("");
  const [selectedItem, setSelectedItem] = useState<UnifiedWorkItem | null>(null);
  const [busyId, setBusyId] = useState<string>("");

  const items = useMemo<UnifiedWorkItem[]>(() => {
    const list: UnifiedWorkItem[] = [];

    // 1. Aprovações Humanas
    for (const req of approvalsData || []) {
      const isPending = req.status === "PENDING";
      const isRejected = req.status === "REJECTED";
      list.push({
        id: `app-${req.id}`,
        kind: "APPROVAL",
        rawId: req.id,
        title: req.title,
        description: `Tipo de decisão: ${req.action_type}. Aguarda decisão explícita para manter a governança do negócio.`,
        origin: "Central de Aprovações",
        priority: isPending ? "ALTA" : "BAIXA",
        statusBucket: isPending ? "PENDING_APPROVAL" : isRejected ? "BLOCKED" : "COMPLETED",
        pillStatus: isPending ? "PENDING" : isRejected ? "BLOCKED" : "EXECUTED",
        dateLabel: req.created_at ? String(req.created_at).slice(0, 10) : "Hoje",
        ownerLabel: isPending ? "Você (Diretor)" : "Revisado",
        relatedAgent: req.agent_id,
        primaryActionLabel: isPending ? "Aprovar Ação" : "Ver Fila",
        secondaryActionLabel: isPending ? "Recusar" : "Abrir Central",
        targetMenu: "approvals",
        evidence: req.payload_json || undefined,
        canApproveInline: isPending,
      });
    }

    // 2. Alertas Operacionais
    for (const al of systemAlerts || []) {
      const resolved = al.status === "RESOLVED";
      list.push({
        id: `alert-${al.id || al.title}`,
        kind: "ALERT",
        title: al.title || "Alerta Operacional",
        description: al.message || al.description || "Aviso gerado pelo monitoramento contínuo.",
        origin: "Monitoramento 24/7",
        priority: al.severity === "CRITICAL" || al.severity === "HIGH" ? "ALTA" : "MÉDIA",
        statusBucket: resolved ? "COMPLETED" : "NEEDS_ME",
        pillStatus: resolved ? "EXECUTED" : "FAILED",
        dateLabel: al.created_at ? String(al.created_at).slice(0, 10) : "Hoje",
        ownerLabel: "Você / Operação",
        relatedAgent: al.source_module || "Monitoramento",
        primaryActionLabel: "Abrir Painel 24/7",
        targetMenu: "operational247",
      });
    }

    // 3. Prioridades do Plano Diário do AI CEO
    for (const task of ceoDailyPlan?.tasks || ceoDailyPlan?.priority_actions || []) {
      list.push({
        id: `ceo-${task.id || task.action || Math.random()}`,
        kind: "CEO_TASK",
        title: task.title || task.action || "Ação Estratégica Recomendada",
        description: task.expected_impact || task.description || "Prioridade identificada com base nos dados atuais.",
        origin: "Plano Diário do AI CEO",
        priority: task.priority === 1 || task.priority === "CRITICAL" ? "ALTA" : "MÉDIA",
        statusBucket: task.status === "DONE" ? "COMPLETED" : "NEEDS_ME",
        pillStatus: task.status === "DONE" ? "EXECUTED" : "RUNNING",
        dateLabel: "Hoje",
        ownerLabel: "Equipe + IA",
        relatedAgent: task.agent || "AGENT_01_CEO",
        primaryActionLabel: "Abrir Plano Diário",
        targetMenu: "ceo_plan",
      });
    }

    // 4. Atividades / Follow-ups no CRM
    for (const act of crmData?.activities || []) {
      list.push({
        id: `crm-${act.id}`,
        kind: "CRM_ACTIVITY",
        title: act.subject,
        description: act.description,
        origin: "CRM & Follow-ups",
        priority: "MÉDIA",
        statusBucket: act.status === "COMPLETED" ? "COMPLETED" : "NEEDS_ME",
        pillStatus: act.status === "COMPLETED" ? "EXECUTED" : "PENDING",
        dateLabel: act.due_date || "Programado",
        ownerLabel: "Comercial",
        relatedAgent: "AGENT_08_SALES",
        primaryActionLabel: "Abrir CRM",
        targetMenu: "crm",
      });
    }

    // 5. Execuções Recentes do Motor de IA
    for (const ex of (aiEnginesConfig?.recent_executions || []).slice(0, 15)) {
      const st = String(ex.status || "").toUpperCase();
      const isBlocked = st.includes("BLOCKED") || st.includes("QUOTA");
      const isFailed = st.includes("ERROR") || st.includes("FAILED");
      const isOk = st === "SUCCESS";
      list.push({
        id: `ai-${ex.execution_uuid}`,
        kind: "AI_EXEC",
        title: `IA (${ex.task_type}): ${ex.requested_provider}:${ex.requested_model}`,
        description: ex.error_message || `Execução concluída via ${ex.executed_provider}:${ex.executed_model} (${ex.total_tokens} tokens).`,
        origin: "Motores de IA",
        priority: isBlocked || isFailed ? "ALTA" : "BAIXA",
        statusBucket: isOk ? "COMPLETED" : isBlocked ? "BLOCKED" : isFailed ? "FAILED" : "AI_RUNNING",
        pillStatus: isOk ? "EXECUTED" : isBlocked ? "BLOCKED" : isFailed ? "FAILED" : "RUNNING",
        dateLabel: ex.created_at ? String(ex.created_at).slice(0, 10) : "Recente",
        ownerLabel: "Automático (IA)",
        relatedAgent: ex.agent_id || "AI_ENGINE_HUB",
        primaryActionLabel: isBlocked || isFailed ? "Ajustar Motor / Chave" : "Ver Histórico IA",
        targetMenu: "ai_engines",
        evidence: `ID: ${ex.execution_uuid} • Origem: ${ex.execution_origin} • Classificação: ${ex.cost_classification}`,
      });
    }

    // 6. Integrações Pendentes de Credenciais
    for (const intg of (integrationsData || []).filter((i: any) => i.status !== "CONNECTED").slice(0, 4)) {
      list.push({
        id: `intg-${intg.provider_key}`,
        kind: "INTEGRATION",
        title: `Conectar ${intg.provider_name}`,
        description: intg.setup_guide?.features_unlocked || "Necessário informar credenciais oficiais para ativar.",
        origin: "Integrações",
        priority: "BAIXA",
        statusBucket: "BLOCKED",
        pillStatus: "NEEDS_CREDENTIALS",
        dateLabel: "Pendente",
        ownerLabel: "Configuração",
        primaryActionLabel: "Conectar Credencial",
        targetMenu: "integrations",
      });
    }

    return list;
  }, [approvalsData, systemAlerts, ceoDailyPlan, crmData, aiEnginesConfig, integrationsData]);

  const counts = useMemo(() => {
    return {
      ALL: items.length,
      NEEDS_ME: items.filter((i) => i.statusBucket === "NEEDS_ME" || i.statusBucket === "PENDING_APPROVAL").length,
      AI_RUNNING: items.filter((i) => i.statusBucket === "AI_RUNNING").length,
      PENDING_APPROVAL: items.filter((i) => i.statusBucket === "PENDING_APPROVAL").length,
      COMPLETED: items.filter((i) => i.statusBucket === "COMPLETED").length,
      FAILED: items.filter((i) => i.statusBucket === "FAILED").length,
      BLOCKED: items.filter((i) => i.statusBucket === "BLOCKED").length,
    };
  }, [items]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return items.filter((it) => {
      if (filter === "NEEDS_ME") {
        if (it.statusBucket !== "NEEDS_ME" && it.statusBucket !== "PENDING_APPROVAL") return false;
      } else if (filter !== "ALL" && it.statusBucket !== filter) {
        return false;
      }
      if (q && !`${it.title} ${it.description} ${it.origin} ${it.relatedAgent || ""}`.toLowerCase().includes(q)) {
        return false;
      }
      return true;
    });
  }, [items, filter, search]);

  const handleInlineDecision = async (item: UnifiedWorkItem, decision: "APPROVE" | "REJECT") => {
    if (item.kind !== "APPROVAL" || !item.rawId) return;
    setBusyId(item.id);
    try {
      await apiFetch(`/api/v1/approvals/${item.rawId}/decide`, {
        method: "POST",
        body: JSON.stringify({
          decision,
          confirmation_token: meData?.high_impact_confirmation_token || "CONFIRMED_BY_HUMAN",
        }),
      });
      await onReload();
      setSelectedItem(null);
      showNotice(decision === "APPROVE" ? "Solicitação aprovada e executada!" : "Solicitação recusada com segurança.");
    } catch (err: any) {
      showNotice(err?.message || "Não foi possível processar a decisão.");
    } finally {
      setBusyId("");
    }
  };

  const tabs: { id: WorkFilter; label: string; icon: React.ReactNode }[] = [
    { id: "ALL", label: `Tudo (${counts.ALL})`, icon: <Inbox className="w-3.5 h-3.5" /> },
    { id: "NEEDS_ME", label: `Precisa de mim (${counts.NEEDS_ME})`, icon: <Clock className="w-3.5 h-3.5" /> },
    { id: "AI_RUNNING", label: `IA executando (${counts.AI_RUNNING})`, icon: <Sparkles className="w-3.5 h-3.5" /> },
    { id: "PENDING_APPROVAL", label: `Aguardando aprovação (${counts.PENDING_APPROVAL})`, icon: <ShieldAlert className="w-3.5 h-3.5" /> },
    { id: "COMPLETED", label: `Concluído (${counts.COMPLETED})`, icon: <CheckCircle2 className="w-3.5 h-3.5" /> },
    { id: "FAILED", label: `Falhou (${counts.FAILED})`, icon: <AlertTriangle className="w-3.5 h-3.5" /> },
    { id: "BLOCKED", label: `Bloqueado (${counts.BLOCKED})`, icon: <Ban className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="space-y-5">
      {/* Barra de Filtros e Busca */}
      <div className="ug-card rounded-2xl p-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-white ug-text-primary">
              Meu Trabalho — Caixa Unificada de Tarefas & Decisões
            </h3>
            <p className="text-xs text-slate-400 ug-text-muted">
              Aprove solicitações, resolva alertas e acompanhe execuções da IA sem precisar abrir vários módulos.
            </p>
          </div>
          <div className="relative w-full sm:w-72">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filtrar tarefas, alertas ou agentes..."
              aria-label="Filtrar tarefas em Meu Trabalho"
              className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white"
            />
          </div>
        </div>

        <div className="flex flex-wrap gap-1.5 pt-1" role="tablist" aria-label="Filtros de Meu Trabalho">
          {tabs.map((t) => (
            <button
              key={t.id}
              type="button"
              role="tab"
              aria-selected={filter === t.id}
              onClick={() => setFilter(t.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium inline-flex items-center gap-1.5 transition ${
                filter === t.id
                  ? "bg-indigo-600 text-white shadow"
                  : "bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800"
              }`}
            >
              {t.icon}
              <span>{t.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Lista de Tarefas */}
      {filtered.length === 0 ? (
        <EmptyState
          icon={<Filter className="w-5 h-5" />}
          title="Nenhum item encontrado neste filtro"
          description="Altere o filtro acima ou limpe a busca para visualizar todas as tarefas, aprovações e execuções."
          actionLabel="Mostrar Tudo"
          onAction={() => {
            setFilter("ALL");
            setSearch("");
          }}
        />
      ) : (
        <div className="space-y-2.5">
          {filtered.map((item) => (
            <div
              key={item.id}
              className="ug-card rounded-xl p-4 hover:border-indigo-500/40 transition flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <button
                type="button"
                onClick={() => setSelectedItem(item)}
                className="flex-1 text-left space-y-1.5 min-w-0"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold text-white ug-text-primary">{item.title}</span>
                  <StatusPill status={item.pillStatus} />
                  <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[10px] text-slate-300">
                    {item.origin}
                  </span>
                </div>
                <p className="text-xs text-slate-400 ug-text-muted line-clamp-2">{item.description}</p>
                <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-500">
                  <span>Prioridade: <strong className="text-slate-300">{item.priority}</strong></span>
                  <span>Responsável: <strong className="text-slate-300">{item.ownerLabel}</strong></span>
                  {item.relatedAgent && <span>Agente: <strong className="text-indigo-300">{item.relatedAgent}</strong></span>}
                  <span>Data: {item.dateLabel}</span>
                </div>
              </button>

              <div className="flex flex-wrap items-center gap-2 shrink-0">
                {item.canApproveInline ? (
                  <>
                    <button
                      type="button"
                      disabled={busyId === item.id}
                      onClick={() => handleInlineDecision(item, "APPROVE")}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                    >
                      Aprovar
                    </button>
                    <button
                      type="button"
                      disabled={busyId === item.id}
                      onClick={() => handleInlineDecision(item, "REJECT")}
                      className="px-3 py-1.5 rounded-lg bg-red-600/80 hover:bg-red-600 text-white text-xs font-semibold"
                    >
                      Recusar
                    </button>
                  </>
                ) : (
                  <button
                    type="button"
                    onClick={() => onNavigate(item.targetMenu)}
                    className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold inline-flex items-center gap-1"
                  >
                    {item.primaryActionLabel}
                    <ArrowUpRight className="w-3.5 h-3.5" aria-hidden="true" />
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => setSelectedItem(item)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs"
                >
                  Detalhes
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Drawer Contextual de Detalhe */}
      <Drawer
        open={Boolean(selectedItem)}
        onClose={() => setSelectedItem(null)}
        title={selectedItem?.title || "Detalhes da Tarefa"}
        subtitle={selectedItem ? `${selectedItem.origin} • Responsável: ${selectedItem.ownerLabel}` : undefined}
      >
        {selectedItem && (
          <div className="space-y-4 text-xs">
            <div className="flex flex-wrap items-center gap-2">
              <StatusPill status={selectedItem.pillStatus} />
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 font-semibold">
                Prioridade: {selectedItem.priority}
              </span>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">{selectedItem.dateLabel}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
              <div className="font-semibold text-slate-300">Descrição e Contexto</div>
              <p className="text-slate-200 leading-relaxed">{selectedItem.description}</p>
            </div>

            {selectedItem.relatedAgent && (
              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800">
                <div className="text-slate-400">Agente ou Módulo Relacionado</div>
                <div className="font-semibold text-indigo-300 mt-0.5">{selectedItem.relatedAgent}</div>
              </div>
            )}

            {selectedItem.evidence && (
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <div className="font-semibold text-slate-300">Evidência / Payload Registrado</div>
                <pre className="text-[11px] text-slate-400 whitespace-pre-wrap break-all">{selectedItem.evidence}</pre>
              </div>
            )}

            <div className="pt-2 flex flex-wrap gap-2">
              {selectedItem.canApproveInline && (
                <>
                  <button
                    type="button"
                    onClick={() => handleInlineDecision(selectedItem, "APPROVE")}
                    className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
                  >
                    Aprovar e Executar
                  </button>
                  <button
                    type="button"
                    onClick={() => handleInlineDecision(selectedItem, "REJECT")}
                    className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white font-semibold"
                  >
                    Recusar
                  </button>
                </>
              )}
              <button
                type="button"
                onClick={() => {
                  onNavigate(selectedItem.targetMenu);
                  setSelectedItem(null);
                }}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold inline-flex items-center gap-1.5"
              >
                Abrir Módulo de Origem
                <ArrowUpRight className="w-3.5 h-3.5" aria-hidden="true" />
              </button>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
