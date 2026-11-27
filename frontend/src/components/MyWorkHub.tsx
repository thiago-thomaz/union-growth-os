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
import { UIMode, simplifyTechnicalText } from "@/lib/plainLanguage";
import { Drawer, EmptyState, FilterTabBar, StatusPill } from "@/components/DesignSystem";

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
  uiMode = "SIMPLE",
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
  uiMode?: UIMode;
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

    for (const req of approvalsData || []) {
      const isPending = req.status === "PENDING";
      const isRejected = req.status === "REJECTED";
      list.push({
        id: `app-${req.id}`,
        kind: "APPROVAL",
        rawId: req.id,
        title: req.title,
        description: `Decisão: ${req.action_type}. Aguarda confirmação humana explícita.`,
        origin: "Central de Aprovações",
        priority: isPending ? "ALTA" : "BAIXA",
        statusBucket: isPending ? "PENDING_APPROVAL" : isRejected ? "BLOCKED" : "COMPLETED",
        pillStatus: isPending ? "PENDING" : isRejected ? "BLOCKED" : "EXECUTED",
        dateLabel: req.created_at ? String(req.created_at).slice(0, 10) : "Hoje",
        ownerLabel: isPending ? "Você" : "Revisado",
        relatedAgent: req.agent_id,
        primaryActionLabel: isPending ? "Aprovar" : "Ver fila",
        secondaryActionLabel: isPending ? "Recusar" : "Abrir",
        targetMenu: "approvals",
        evidence: req.payload_json || undefined,
        canApproveInline: isPending,
      });
    }

    for (const al of systemAlerts || []) {
      const resolved = al.status === "RESOLVED";
      list.push({
        id: `alert-${al.id || al.title}`,
        kind: "ALERT",
        title: simplifyTechnicalText(al.title || "Alerta Operacional", uiMode),
        description: simplifyTechnicalText(al.message || al.description || "Aviso de monitoramento contínuo.", uiMode),
        origin: "Monitoramento",
        priority: al.severity === "CRITICAL" || al.severity === "HIGH" ? "ALTA" : "MÉDIA",
        statusBucket: resolved ? "COMPLETED" : "NEEDS_ME",
        pillStatus: resolved ? "EXECUTED" : "FAILED",
        dateLabel: al.created_at ? String(al.created_at).slice(0, 10) : "Hoje",
        ownerLabel: "Operação",
        relatedAgent: al.source_module || "Monitoramento",
        primaryActionLabel: "Verificar",
        targetMenu: "operational247",
      });
    }

    for (const task of ceoDailyPlan?.tasks || ceoDailyPlan?.priority_actions || []) {
      list.push({
        id: `ceo-${task.id || task.action || Math.random()}`,
        kind: "CEO_TASK",
        title: task.title || task.action || "Ação Estratégica Recomendada",
        description: simplifyTechnicalText(task.expected_impact || task.description || "Prioridade recomendada pelo AI CEO.", uiMode),
        origin: "Plano Diário",
        priority: task.priority === 1 || task.priority === "CRITICAL" ? "ALTA" : "MÉDIA",
        statusBucket: task.status === "DONE" ? "COMPLETED" : "NEEDS_ME",
        pillStatus: task.status === "DONE" ? "EXECUTED" : "RUNNING",
        dateLabel: "Hoje",
        ownerLabel: "Equipe + IA",
        relatedAgent: task.agent || "AGENT_01_CEO",
        primaryActionLabel: "Abrir plano",
        targetMenu: "ceo_plan",
      });
    }

    for (const act of crmData?.activities || []) {
      list.push({
        id: `crm-${act.id}`,
        kind: "CRM_ACTIVITY",
        title: act.subject,
        description: act.description,
        origin: "CRM & Vendas",
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

    for (const ex of (aiEnginesConfig?.recent_executions || []).slice(0, 12)) {
      const st = String(ex.status || "").toUpperCase();
      const isBlocked = st.includes("BLOCKED") || st.includes("QUOTA");
      const isFailed = st.includes("ERROR") || st.includes("FAILED");
      const isOk = st === "SUCCESS";
      list.push({
        id: `ai-${ex.execution_uuid}`,
        kind: "AI_EXEC",
        title: `IA (${ex.task_type}): ${ex.requested_provider}`,
        description: simplifyTechnicalText(
          ex.error_message || `Concluído em ${ex.executed_provider}:${ex.executed_model}.`,
          uiMode
        ),
        origin: "Serviços de IA",
        priority: isBlocked || isFailed ? "ALTA" : "BAIXA",
        statusBucket: isOk ? "COMPLETED" : isBlocked ? "BLOCKED" : isFailed ? "FAILED" : "AI_RUNNING",
        pillStatus: isOk ? "EXECUTED" : isBlocked ? "BLOCKED" : isFailed ? "FAILED" : "RUNNING",
        dateLabel: ex.created_at ? String(ex.created_at).slice(0, 10) : "Recente",
        ownerLabel: "IA",
        relatedAgent: ex.agent_id || "AI_ENGINE_HUB",
        primaryActionLabel: isBlocked || isFailed ? "Verificar IA" : "Detalhes",
        targetMenu: "ai_engines",
        evidence: `ID: ${ex.execution_uuid} • Origem: ${ex.execution_origin} • Política: ${ex.cost_classification}`,
      });
    }

    for (const intg of (integrationsData || []).filter((i: any) => i.status !== "CONNECTED").slice(0, 4)) {
      list.push({
        id: `intg-${intg.provider_key}`,
        kind: "INTEGRATION",
        title: `Conectar ${intg.provider_name}`,
        description: intg.setup_guide?.features_unlocked || "Conexão externa opcional para liberar envio direto.",
        origin: "Integrações",
        priority: "BAIXA",
        statusBucket: "BLOCKED",
        pillStatus: "NEEDS_CREDENTIALS",
        dateLabel: "Opcional",
        ownerLabel: "Configuração",
        relatedAgent: intg.provider_key,
        primaryActionLabel: "Conectar",
        targetMenu: "integrations",
      });
    }

    return list;
  }, [approvalsData, systemAlerts, ceoDailyPlan, crmData, aiEnginesConfig, integrationsData, uiMode]);

  const counts = useMemo(
    () => ({
      ALL: items.length,
      NEEDS_ME: items.filter((i) => i.statusBucket === "NEEDS_ME" || i.statusBucket === "PENDING_APPROVAL").length,
      AI_RUNNING: items.filter((i) => i.statusBucket === "AI_RUNNING").length,
      PENDING_APPROVAL: items.filter((i) => i.statusBucket === "PENDING_APPROVAL").length,
      COMPLETED: items.filter((i) => i.statusBucket === "COMPLETED").length,
      FAILED: items.filter((i) => i.statusBucket === "FAILED").length,
      BLOCKED: items.filter((i) => i.statusBucket === "BLOCKED").length,
    }),
    [items]
  );

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
      showNotice(decision === "APPROVE" ? "Solicitação aprovada e executada!" : "Solicitação recusada.");
    } catch (err: any) {
      showNotice(err?.message || "Não foi possível processar a decisão.");
    } finally {
      setBusyId("");
    }
  };

  const tabs = [
    { id: "ALL", label: "Tudo", count: counts.ALL, icon: <Inbox className="w-3.5 h-3.5" /> },
    { id: "NEEDS_ME", label: "Precisa de mim", count: counts.NEEDS_ME, icon: <Clock className="w-3.5 h-3.5" /> },
    { id: "AI_RUNNING", label: "IA executando", count: counts.AI_RUNNING, icon: <Sparkles className="w-3.5 h-3.5" /> },
    { id: "PENDING_APPROVAL", label: "Aguardando aprovação", count: counts.PENDING_APPROVAL, icon: <ShieldAlert className="w-3.5 h-3.5" /> },
    { id: "COMPLETED", label: "Concluído", count: counts.COMPLETED, icon: <CheckCircle2 className="w-3.5 h-3.5" /> },
    { id: "FAILED", label: "Falhou", count: counts.FAILED, icon: <AlertTriangle className="w-3.5 h-3.5" /> },
    { id: "BLOCKED", label: "Bloqueado", count: counts.BLOCKED, icon: <Ban className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="space-y-5 max-w-6xl mx-auto ug-fade-in">
      {/* Cabeçalho e Busca */}
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold tracking-tight text-[var(--ug-text-primary)]">
            Meu Trabalho
          </h3>
          <p className="text-xs text-[var(--ug-text-muted)]">
            Aprove decisões, resolva pendências e acompanhe execuções em uma única fila.
          </p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search className="w-3.5 h-3.5 text-[var(--ug-text-muted)] absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filtrar fila de trabalho..."
            aria-label="Filtrar tarefas em Meu Trabalho"
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-[var(--ug-surface)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
          />
        </div>
      </div>

      {/* Filtros Underline (Linear style) */}
      <FilterTabBar
        tabs={tabs}
        activeId={filter}
        onChange={(id) => setFilter(id as WorkFilter)}
        ariaLabel="Filtros de Meu Trabalho"
      />

      {/* Lista de Triagem Contínua */}
      {filtered.length === 0 ? (
        <EmptyState
          icon={<Filter className="w-5 h-5" />}
          title="Nenhum item neste filtro"
          description="Altere a aba selecionada ou limpe a busca acima para ver todas as ações."
          actionLabel="Mostrar Tudo"
          onAction={() => {
            setFilter("ALL");
            setSearch("");
          }}
        />
      ) : (
        <div className="ug-card rounded-xl divide-y divide-white/[0.05]">
          {filtered.map((item) => (
            <div
              key={item.id}
              className="px-4 py-3 hover:bg-white/[0.02] transition flex flex-col md:flex-row md:items-center justify-between gap-3"
            >
              <button
                type="button"
                onClick={() => setSelectedItem(item)}
                className="flex-1 text-left flex items-start gap-3 min-w-0"
              >
                <span
                  className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${
                    item.priority === "ALTA"
                      ? "bg-amber-400"
                      : item.priority === "MÉDIA"
                      ? "bg-indigo-400"
                      : "bg-zinc-500"
                  }`}
                  aria-hidden="true"
                />
                <div className="min-w-0 space-y-0.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-medium text-[var(--ug-text-primary)]">{item.title}</span>
                    <StatusPill status={item.pillStatus} />
                  </div>
                  <p className="text-[11px] text-[var(--ug-text-muted)] line-clamp-1">{item.description}</p>
                  <div className="flex flex-wrap items-center gap-3 text-[11px] text-[var(--ug-text-muted)] tabular-nums">
                    <span>{item.origin}</span>
                    <span>• Prioridade: {item.priority}</span>
                    <span>• Responsável: {item.ownerLabel}</span>
                    {uiMode === "ADVANCED" && item.relatedAgent && (
                      <span className="text-indigo-400">• {item.relatedAgent}</span>
                    )}
                    <span>• {item.dateLabel}</span>
                  </div>
                </div>
              </button>

              <div className="flex flex-wrap items-center gap-1.5 shrink-0 pl-5 md:pl-0">
                {item.canApproveInline ? (
                  <>
                    <button
                      type="button"
                      disabled={busyId === item.id}
                      onClick={() => handleInlineDecision(item, "APPROVE")}
                      className="px-2.5 py-1 rounded-md bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-medium"
                    >
                      Aprovar
                    </button>
                    <button
                      type="button"
                      disabled={busyId === item.id}
                      onClick={() => handleInlineDecision(item, "REJECT")}
                      className="px-2.5 py-1 rounded-md border border-red-500/30 hover:bg-red-500/15 text-red-400 text-[11px] font-medium"
                    >
                      Recusar
                    </button>
                  </>
                ) : (
                  <button
                    type="button"
                    onClick={() => onNavigate(item.targetMenu)}
                    className="px-2.5 py-1 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-medium inline-flex items-center gap-1"
                  >
                    <span>{item.primaryActionLabel}</span>
                    <ArrowUpRight className="w-3 h-3" aria-hidden="true" />
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => setSelectedItem(item)}
                  className="px-2.5 py-1 rounded-md border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-secondary)] text-[11px]"
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
              <span className="text-[11px] text-[var(--ug-text-secondary)]">
                Prioridade: <strong>{selectedItem.priority}</strong>
              </span>
              <span className="text-[11px] text-[var(--ug-text-muted)] tabular-nums">• {selectedItem.dateLabel}</span>
            </div>

            <div className="space-y-1">
              <div className="font-semibold text-[var(--ug-text-primary)]">Contexto</div>
              <p className="text-[var(--ug-text-secondary)] leading-relaxed">{selectedItem.description}</p>
            </div>

            {selectedItem.relatedAgent && (
              <div className="pt-2 border-t border-[var(--ug-border-subtle)] flex items-center justify-between">
                <span className="text-[var(--ug-text-muted)]">Responsável / Origem</span>
                <span className="font-medium text-indigo-400">{selectedItem.relatedAgent}</span>
              </div>
            )}

            {selectedItem.evidence && (uiMode === "ADVANCED" || selectedItem.kind === "APPROVAL") && (
              <div className="p-3 rounded-lg bg-white/[0.03] border border-[var(--ug-border)] space-y-1">
                <div className="text-[11px] font-medium text-[var(--ug-text-secondary)]">Registro auditável</div>
                <pre className="text-[11px] text-[var(--ug-text-muted)] whitespace-pre-wrap break-all font-mono">
                  {selectedItem.evidence}
                </pre>
              </div>
            )}

            <div className="pt-3 border-t border-[var(--ug-border)] flex flex-wrap gap-2">
              {selectedItem.canApproveInline && (
                <>
                  <button
                    type="button"
                    onClick={() => handleInlineDecision(selectedItem, "APPROVE")}
                    className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium"
                  >
                    Aprovar e Executar
                  </button>
                  <button
                    type="button"
                    onClick={() => handleInlineDecision(selectedItem, "REJECT")}
                    className="px-3.5 py-1.5 rounded-lg border border-red-500/30 text-red-400 hover:bg-red-500/15 font-medium"
                  >
                    Recusar
                  </button>
                </>
              )}
              <button
                type="button"
                onClick={() => {
                  const target = selectedItem.targetMenu;
                  setSelectedItem(null);
                  onNavigate(target);
                }}
                className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium inline-flex items-center gap-1"
              >
                <span>Abrir {selectedItem.origin}</span>
                <ArrowUpRight className="w-3.5 h-3.5" aria-hidden="true" />
              </button>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}
