"use client";

import React, { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, DatabaseBackup, Play, ShieldCheck } from "lucide-react";
import { FilterTabBar, MetricStrip, OriginBadge, PlainOrientationBar, StatusPill } from "@/components/DesignSystem";

export function AuditCenterWorkspace({
  auditData,
  apiFetch,
  onReload,
  showNotice,
}: {
  auditData: any;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  showNotice: (msg: string) => void;
}) {
  const [historyData, setHistoryData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("categories");
  const [runningAudit, setRunningAudit] = useState(false);
  const [restoreResult, setRestoreResult] = useState<any>(null);
  const [testingRestore, setTestingRestore] = useState(false);

  const loadHistory = async () => {
    try {
      const h = await apiFetch("/api/v1/system/audit/history");
      setHistoryData(h);
    } catch {
      // ignore initial error
    }
  };

  useEffect(() => {
    loadHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const latest = historyData?.latest;
  const categories = latest?.categories || [];
  const matrix = latest?.traceability_matrix || [];
  const blockers = latest?.external_blockers || [];
  const runs = historyData?.history || [];

  const runCompleteAudit = async () => {
    setRunningAudit(true);
    try {
      const res = await apiFetch("/api/v1/system/audit/run", { method: "POST" });
      await loadHistory();
      await onReload();
      showNotice(`Auditoria 25 categorias concluída: ${res.global_score}/100 (${res.readiness_status})`);
    } catch (err: any) {
      showNotice(err?.message || "Erro ao executar auditoria completa.");
    } finally {
      setRunningAudit(false);
    }
  };

  const runRestoreCheck = async () => {
    setTestingRestore(true);
    try {
      const res = await apiFetch("/api/v1/system/backup/test-restore", { method: "POST" });
      setRestoreResult(res);
      showNotice(`Restauração isolada validada (SHA-256 ${String(res.sha256 || "").slice(0, 10)})!`);
    } catch (err: any) {
      showNotice(err?.message || "Erro no teste de restauração.");
    } finally {
      setTestingRestore(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      <PlainOrientationBar
        whatIsIt="Central de Auditoria Executiva & Governança (25 Categorias Baseadas em Evidência)"
        whyUseIt="Mede maturidade real sem mascarar limitações ou dependências externas e valida restauração SHA-256 sem afetar dados"
        nextStep="Clique em EXECUTAR AUDITORIA COMPLETA para gerar um novo snapshot histórico persistido"
        actionLabel={runningAudit ? "Auditando 25 pilares..." : "EXECUTAR AUDITORIA COMPLETA"}
        onAction={runCompleteAudit}
      />

      <MetricStrip
        items={[
          {
            key: "score",
            label: "Score Global Real",
            value: latest ? `${latest.global_score}/100` : "Aguardando",
            subtext: latest?.readiness_status || "Sem auditoria ainda",
            origin: "REAL",
            source: "25 Categorias Ponderadas",
            period: latest ? `v${latest.version}` : "On-demand",
          },
          {
            key: "runs",
            label: "Auditorias Persistidas",
            value: runs.length,
            subtext: "Histórico PostgreSQL",
            origin: "REAL",
            source: "SystemAuditSnapshot",
            period: "Acumulado",
          },
          {
            key: "blockers",
            label: "Pendências Externas",
            value: blockers.length,
            subtext: "Credenciais / Gateway / LLM",
            origin: "REAL",
            source: "Gatekeeper 100/100",
            period: "Tempo real",
          },
          {
            key: "agent_logs",
            label: "Execuções de Agentes",
            value: (auditData?.agent_execution_logs || []).length,
            subtext: "Últimos registros auditáveis",
            origin: "REAL",
            source: "AgentExecutionLog",
            period: "Recente",
          },
          {
            key: "sec_logs",
            label: "Trilha de Segurança",
            value: (auditData?.audit_logs || []).length,
            subtext: "Audit trail imutável",
            origin: "REAL",
            source: "AuditLog",
            period: "Recente",
          },
        ]}
      />

      <div className="ug-card rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
        <FilterTabBar
          ariaLabel="Visões da Central de Auditoria"
          activeId={activeTab}
          onChange={setActiveTab}
          tabs={[
            { id: "categories", label: "25 Categorias & Notas", count: categories.length },
            { id: "matrix", label: "Matriz de Rastreabilidade", count: matrix.length },
            { id: "backup", label: "Backup, Histórico & Recuperação", count: runs.length },
            { id: "logs", label: "Logs Brutos (IA & Segurança)" },
          ]}
        />
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={testingRestore}
            onClick={runRestoreCheck}
            className="px-3 py-1.5 rounded-lg border border-emerald-500/35 text-emerald-400 hover:bg-emerald-500/10 font-medium inline-flex items-center gap-1.5"
          >
            <DatabaseBackup className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{testingRestore ? "Testando Restore..." : "Testar Restauração Isolada"}</span>
          </button>
          <button
            type="button"
            disabled={runningAudit}
            onClick={runCompleteAudit}
            className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold inline-flex items-center gap-1.5"
          >
            <Play className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{runningAudit ? "Executando..." : "EXECUTAR AUDITORIA COMPLETA"}</span>
          </button>
        </div>
      </div>

      {restoreResult && (
        <div className="ug-card rounded-xl p-4 border border-emerald-500/30 text-xs space-y-1">
          <div className="font-semibold text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" aria-hidden="true" />
            <span>Teste de Recuperação Isolada Concluído (Produção Preservada)</span>
          </div>
          <div className="text-[var(--ug-text-secondary)]">
            Arquivo: <strong>{restoreResult.backup_tested}</strong> • SHA-256: <code className="font-mono">{restoreResult.sha256}</code> •
            Registros verificados: <strong className="tabular-nums">{restoreResult.total_restored_records ?? restoreResult.restore_report?.total_restored_records ?? 0}</strong> (
            {restoreResult.restored_tables && typeof restoreResult.restored_tables === "object"
              ? Object.keys(restoreResult.restored_tables).length
              : restoreResult.restored_tables ?? "-"}{" "}
            tabelas)
          </div>
        </div>
      )}

      {!latest && activeTab !== "logs" && (
        <div className="ug-card rounded-xl p-6 text-center space-y-3 text-xs">
          <ShieldCheck className="w-6 h-6 text-indigo-400 mx-auto" aria-hidden="true" />
          <div className="font-semibold text-[var(--ug-text-primary)]">Nenhuma auditoria de 25 categorias executada neste workspace ainda</div>
          <p className="text-[var(--ug-text-muted)]">
            Clique em <strong>EXECUTAR AUDITORIA COMPLETA</strong> para inspecionar os dados reais, sem alterar registros de clientes.
          </p>
        </div>
      )}

      {latest && activeTab === "categories" && (
        <div className="ug-card rounded-xl overflow-hidden text-xs">
          <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] flex flex-wrap items-center justify-between gap-2">
            <div>
              <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">
                Scorecard Objetivo das 25 Categorias — {latest.global_score}/100 ({latest.readiness_status})
              </h4>
              <p className="text-[11px] text-[var(--ug-text-muted)]">{latest.honesty_disclaimer}</p>
            </div>
            <OriginBadge origin="REAL" />
          </div>
          <div className="divide-y divide-white/[0.05]">
            {categories.map((cat: any) => (
              <div key={cat.category} className="px-5 py-3.5 space-y-1.5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-[var(--ug-text-primary)]">{cat.category}</span>
                    <StatusPill
                      status={cat.status === "BLOCKED" ? "NEEDS_CREDENTIALS" : cat.status === "SANDBOX" ? "PENDING" : "EXECUTED"}
                      label={cat.status}
                    />
                  </div>
                  <span className="font-semibold text-indigo-400 tabular-nums">
                    {cat.score}/100 (peso {cat.weight_pct}%)
                  </span>
                </div>
                <div className="text-[11px] text-[var(--ug-text-secondary)]">
                  <strong>Evidência:</strong> {cat.evidence} • <strong>Teste:</strong> {cat.test}
                </div>
                <div className="text-[11px] text-[var(--ug-text-muted)]">
                  <strong>Gap / Bloqueio:</strong> {cat.failure_or_gap} •{" "}
                  <strong>Dependência:</strong> {cat.external_dependency} •{" "}
                  <strong>Próxima ação:</strong> {cat.next_action}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {latest && activeTab === "matrix" && (
        <div className="ug-card rounded-xl overflow-x-auto text-xs">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[var(--ug-border)] text-[11px] text-[var(--ug-text-muted)]">
                <th className="py-3 px-4">Funcionalidade</th>
                <th className="py-3 px-4">Frontend</th>
                <th className="py-3 px-4">API / Banco</th>
                <th className="py-3 px-4">Status Real</th>
                <th className="py-3 px-4">Problema / Correção</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05]">
              {matrix.map((row: any, i: number) => (
                <tr key={i} className="hover:bg-white/[0.02]">
                  <td className="py-3 px-4 font-semibold text-[var(--ug-text-primary)]">{row.functionality}</td>
                  <td className="py-3 px-4 text-[var(--ug-text-secondary)]">{row.frontend}</td>
                  <td className="py-3 px-4 text-[var(--ug-text-muted)]">
                    <div>{row.api}</div>
                    <div className="text-[10px]">{row.database}</div>
                  </td>
                  <td className="py-3 px-4">
                    <StatusPill
                      status={row.status === "BLOCKED" ? "NEEDS_CREDENTIALS" : row.status === "SANDBOX" ? "PENDING" : "EXECUTED"}
                      label={row.status}
                    />
                  </td>
                  <td className="py-3 px-4 text-[11px] text-[var(--ug-text-muted)]">
                    <div><strong>Gap:</strong> {row.issue}</div>
                    <div className="text-emerald-400"><strong>Ação:</strong> {row.fix}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "backup" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs">
          <div className="ug-card rounded-xl overflow-hidden">
            <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
              Histórico de Auditorias Executadas ({runs.length})
            </div>
            <div className="divide-y divide-white/[0.05]">
              {runs.map((r: any) => (
                <div key={r.audit_id} className="px-5 py-3 flex items-center justify-between gap-2">
                  <div>
                    <div className="font-semibold text-[var(--ug-text-primary)]">
                      Auditoria #{r.audit_id} • v{r.version} ({r.readiness_status})
                    </div>
                    <div className="text-[11px] text-[var(--ug-text-muted)]">
                      Por: {r.triggered_by} • {String(r.created_at || "").slice(0, 19).replace("T", " ")}
                    </div>
                  </div>
                  <span className="font-semibold text-indigo-400 tabular-nums">{r.global_score}/100</span>
                </div>
              ))}
            </div>
          </div>

          <div className="ug-card rounded-xl overflow-hidden">
            <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)] flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" aria-hidden="true" />
              <span>Bloqueios Externos Que Impedem 100/100 ({blockers.length})</span>
            </div>
            <div className="divide-y divide-white/[0.05]">
              {blockers.map((b: any, i: number) => (
                <div key={i} className="px-5 py-3 space-y-1">
                  <div className="flex justify-between font-semibold text-[var(--ug-text-primary)]">
                    <span>{b.category}</span>
                    <span className="text-amber-400 tabular-nums">{b.score}/100</span>
                  </div>
                  <div className="text-[var(--ug-text-secondary)]">{b.gap}</div>
                  <div className="text-[11px] text-[var(--ug-text-muted)]">
                    <strong>Requisito:</strong> {b.external_dependency}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === "logs" && auditData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs">
          <div className="ug-card rounded-xl overflow-hidden">
            <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
              Logs de Execução dos Agentes de IA
            </div>
            <div className="divide-y divide-white/[0.05] max-h-[520px] overflow-y-auto">
              {(auditData.agent_execution_logs || []).map((l: any) => (
                <div key={l.id} className="px-5 py-3 space-y-1">
                  <div className="flex justify-between font-semibold text-indigo-400">
                    <span>{l.agent_name}</span>
                    <span className="tabular-nums">{l.duration_ms}ms • {l.status}</span>
                  </div>
                  <div className="text-[var(--ug-text-secondary)]">Tarefa: {l.task_name} • {l.workflow_run_id}</div>
                  <div className="text-[10px] text-[var(--ug-text-muted)]">{l.created_at}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="ug-card rounded-xl overflow-hidden">
            <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
              Trilha de Auditoria &amp; Segurança
            </div>
            <div className="divide-y divide-white/[0.05] max-h-[520px] overflow-y-auto">
              {(auditData.audit_logs || []).map((a: any) => (
                <div key={a.id} className="px-5 py-3 space-y-1">
                  <div className="flex justify-between font-semibold text-emerald-400">
                    <span>{a.action}</span>
                    <span className="tabular-nums">IP: {a.ip_address}</span>
                  </div>
                  <div className="text-[var(--ug-text-secondary)]">Ator: {a.actor} • {a.resource_type} #{a.resource_id}</div>
                  <div className="text-[10px] text-[var(--ug-text-muted)]">{a.created_at}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
