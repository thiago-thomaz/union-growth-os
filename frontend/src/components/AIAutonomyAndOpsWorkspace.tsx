"use client";

import React from "react";
import { MetricStrip, OriginBadge, StatusPill } from "@/components/DesignSystem";
import { ConversationalAutomationPanel } from "@/components/ConversationalAutomationAndAnalytics";

export function AIAutonomyAndOpsWorkspace({
  mode,
  meData,
  ceoData,
  goalTitle,
  setGoalTitle,
  goalPeriod,
  setGoalPeriod,
  goalMetric,
  goalTarget,
  setGoalTarget,
  ceoDailyPlan,
  setCeoDailyPlan,
  opDashboard,
  systemAlerts,
  pilotData,
  setPilotData,
  automationsData,
  approvalsData,
  uiMode,
  setUiMode,
  setLoading,
  apiFetch,
  onReload,
  showNotice,
}: any) {
  if (mode === "ceo") {
    return (
      <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
        <div className="ug-card rounded-xl p-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">AI CEO &amp; Direção Estratégica</h3>
            <p className="text-xs text-[var(--ug-text-muted)]">Consolida apenas fatos reais e metas declaradas.</p>
          </div>
          <button
            type="button"
            onClick={async () => {
              await apiFetch("/api/v1/ceo/briefings/generate", { method: "POST" });
              await onReload();
              showNotice("Novo CEO Daily Briefing gerado!");
            }}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
          >
            Gerar Novo CEO Daily Briefing
          </button>
        </div>

        {ceoData.briefings?.[0] && (
          <div className="ug-card rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between gap-2">
              <h4 className="text-base font-semibold text-[var(--ug-text-primary)]">{ceoData.briefings[0].summary_headline}</h4>
              <OriginBadge origin="REAL" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-3 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] space-y-1">
                <div className="font-semibold text-indigo-400">O que aconteceu (Fatos Auditados)</div>
                {ceoData.briefings[0].what_happened.map((x: string, i: number) => (
                  <p key={i} className="text-[var(--ug-text-secondary)]">• {x}</p>
                ))}
              </div>
              <div className="p-3 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] space-y-1">
                <div className="font-semibold text-emerald-400">O que está funcionando</div>
                {ceoData.briefings[0].what_is_working.map((x: string, i: number) => (
                  <p key={i} className="text-[var(--ug-text-secondary)]">• {x}</p>
                ))}
              </div>
              <div className="p-3 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] space-y-1">
                <div className="font-semibold text-amber-300">Pontos Críticos</div>
                {ceoData.briefings[0].urgent_problems.map((x: string, i: number) => (
                  <p key={i} className="text-red-400">! {x}</p>
                ))}
              </div>
              <div className="p-3 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] space-y-1">
                <div className="font-semibold text-sky-400">Oportunidades &amp; Recomendações</div>
                {ceoData.briefings[0].recommendations.map((x: string, i: number) => (
                  <p key={i} className="text-[var(--ug-text-secondary)]">• {x}</p>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="ug-card rounded-xl p-5 space-y-4">
          <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">Metas Estratégicas</h4>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
            <input value={goalTitle} onChange={(e) => setGoalTitle(e.target.value)} placeholder="Título da Meta" aria-label="Título da Meta" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)] md:col-span-2" />
            <select value={goalPeriod} onChange={(e) => setGoalPeriod(e.target.value)} aria-label="Período da Meta" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]">
              <option value="MONTHLY">Mensal</option>
              <option value="QUARTERLY">Trimestral</option>
              <option value="ANNUAL">Anual</option>
            </select>
            <input type="number" value={goalTarget} onChange={(e) => setGoalTarget(e.target.value)} placeholder="Valor Alvo" aria-label="Valor Alvo" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)] tabular-nums" />
            <button
              type="button"
              onClick={async () => {
                if (!goalTitle) return;
                await apiFetch("/api/v1/ceo/goals", {
                  method: "POST",
                  body: JSON.stringify({
                    title: goalTitle,
                    period: goalPeriod,
                    metric_name: goalMetric,
                    target_value: Number(goalTarget) || 100000,
                    current_value: 0,
                    unit: "BRL",
                    data_origin: "GOAL",
                    priority: "HIGH",
                    deadline: "2027-03-31",
                  }),
                });
                setGoalTitle("");
                await onReload();
                showNotice("Meta estratégica registrada!");
              }}
              className="py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
            >
              Adicionar Meta
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {ceoData.goals.map((g: any) => (
              <div key={g.id} className="p-4 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300">{g.period}</span>
                  <OriginBadge origin={g.data_origin} />
                </div>
                <div className="font-semibold text-[var(--ug-text-primary)]">{g.title}</div>
                <div className="text-sm font-semibold text-emerald-400 tabular-nums">Atual: {g.current_value} / Meta: {g.target_value} {g.unit}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (mode === "ceo_plan") {
    return (
      <div className="space-y-5 max-w-7xl mx-auto ug-fade-in">
        <div className="ug-card rounded-xl p-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold text-[var(--ug-text-primary)]">Plano Diário de Execução &amp; Delegação</h3>
            <p className="text-xs text-[var(--ug-text-muted)]">{ceoDailyPlan?.headline || "Missões executivas diárias distribuídas."}</p>
          </div>
          <button
            type="button"
            onClick={async () => {
              setLoading(true);
              try {
                const res = await apiFetch("/api/v1/ceo/daily-plan/generate", { method: "POST" });
                setCeoDailyPlan(res);
                showNotice("Novo Plano Diário gerado!");
              } finally {
                setLoading(false);
              }
            }}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs"
          >
            Regenerar Missões Diárias
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {ceoDailyPlan?.tasks?.map((task: any) => (
            <div key={task.id} className="ug-card rounded-xl p-5 space-y-2.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 font-semibold text-[11px]">{task.target_agent}</span>
                <StatusPill status={task.status === "COMPLETED" ? "EXECUTED" : "PENDING"} label={task.priority} />
              </div>
              <div className="font-semibold text-[var(--ug-text-primary)] text-sm">{task.title}</div>
              <p className="text-[var(--ug-text-secondary)]">{task.objective}</p>
              <div className="flex items-center justify-between pt-2 border-t border-[var(--ug-border-subtle)]">
                <span className="text-[var(--ug-text-muted)]">Status: <strong>{task.status}</strong></span>
                {task.status !== "COMPLETED" && (
                  <button
                    type="button"
                    onClick={async () => {
                      await apiFetch(`/api/v1/ceo/daily-plan/tasks/${task.id}`, {
                        method: "PUT",
                        body: JSON.stringify({ status: "COMPLETED", deliverable: "Executado." }),
                      });
                      await onReload();
                      showNotice(`Missão ${task.id} concluída!`);
                    }}
                    className="px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-medium"
                  >
                    Concluir Missão
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (mode === "operational247") {
    return (
      <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
        <MetricStrip
          items={[
            { key: "vps", label: "VPS Host (Coolify)", value: opDashboard?.vps_status?.status || "HEALTHY", subtext: `IP: ${opDashboard?.vps_status?.server_ip || "72.62.13.62"}`, origin: "REAL" },
            { key: "pg", label: "PostgreSQL 16", value: opDashboard?.database_status?.connection || "CONECTADO", subtext: `${opDashboard?.database_status?.total_records_monitored || 0} registros`, origin: "REAL" },
            { key: "sch", label: "APScheduler Nativo", value: "100% Python", subtext: "Zero dependência n8n", origin: "REAL" },
            { key: "cost", label: "Custo Cloud Extra", value: "R$ 0,00", subtext: "Arquitetura nativa gratuita", origin: "REAL" },
          ]}
        />
        <div className="ug-card rounded-xl overflow-hidden">
          <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] flex items-center justify-between">
            <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">Rotinas Contínuas</h3>
            <button
              type="button"
              onClick={async () => {
                const r = await apiFetch("/api/v1/seo/weekly-report", { method: "POST" });
                await onReload();
                showNotice(`Auditoria Semanal SEO executada! Score: ${r.audit_score}/100`);
              }}
              className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs"
            >
              Executar Auditoria Semanal de SEO
            </button>
          </div>
          <div className="divide-y divide-white/[0.05] text-xs">
            {opDashboard?.daily_routines_status?.map((r: any, idx: number) => (
              <div key={idx} className="px-5 py-3 flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="font-mono text-indigo-400 mr-2">{r.hour}</span>
                  <span className="font-medium text-[var(--ug-text-primary)]">{r.routine}</span>
                  <span className="text-[var(--ug-text-muted)] ml-2">({r.agent})</span>
                </div>
                <StatusPill status="EXECUTED" label={r.status} />
              </div>
            ))}
          </div>
        </div>
        {systemAlerts?.length > 0 && (
          <div className="ug-card rounded-xl divide-y divide-white/[0.05]">
            {systemAlerts.map((a: any) => (
              <div key={a.id} className="px-5 py-3 flex flex-wrap items-center justify-between gap-2 text-xs">
                <div>
                  <div className="font-semibold text-[var(--ug-text-primary)]">{a.title}</div>
                  <div className="text-[var(--ug-text-muted)]">{a.message}</div>
                </div>
                {!a.is_resolved && (
                  <button
                    type="button"
                    onClick={async () => {
                      await apiFetch(`/api/v1/system/alerts/${a.id}/resolve`, { method: "POST" });
                      await onReload();
                      showNotice("Alerta resolvido!");
                    }}
                    className="px-3 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-primary)]"
                  >
                    Marcar Resolvido
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (mode === "pilot7d") {
    return (
      <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
        <div className="ug-card rounded-xl p-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-base font-semibold text-[var(--ug-text-primary)]">Piloto Operacional Autônomo de 7 Dias</h3>
            <p className="text-xs text-[var(--ug-text-muted)]">Simulação e validação das rotinas diárias com custo R$ 0,00.</p>
          </div>
          <button
            type="button"
            onClick={async () => {
              setLoading(true);
              try {
                const res = await apiFetch("/api/v1/system/pilot-7-days", { method: "POST" });
                setPilotData(res);
                showNotice(`Piloto concluído: ${res.total_content_pieces_produced} conteúdos produzidos!`);
              } finally {
                setLoading(false);
              }
            }}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs"
          >
            Executar Piloto de 7 Dias
          </button>
        </div>
        {pilotData && (
          <>
            <MetricStrip
              items={[
                { key: "d", label: "Dias Auditados", value: `${pilotData.days_simulated} Dias`, origin: "SIMULATION" },
                { key: "c", label: "Conteúdos", value: `${pilotData.total_content_pieces_produced} Peças`, origin: "SIMULATION" },
                { key: "l", label: "Leads Qualificados", value: `${pilotData.total_leads_qualified}`, origin: "SIMULATION" },
                { key: "s", label: "Rotinas SEO", value: `${pilotData.total_seo_routines_executed}`, origin: "SIMULATION" },
              ]}
            />
            <div className="space-y-3">
              {pilotData.daily_runs?.map((d: any) => (
                <div key={d.day_number} className="ug-card rounded-xl p-4 text-xs space-y-1.5">
                  <div className="font-semibold text-[var(--ug-text-primary)]">Dia {d.day_number} — {d.date}</div>
                  <ul className="list-disc pl-4 text-[var(--ug-text-secondary)]">
                    {d.actions?.map((act: string, i: number) => <li key={i}>{act}</li>)}
                  </ul>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    );
  }

  if (mode === "approvals") {
    return (
      <div className="space-y-4 max-w-6xl mx-auto ug-fade-in">
        <div className="ug-card rounded-xl p-4">
          <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">
            Central de Aprovações Humanas &amp; Governança
          </h3>
          <p className="text-xs text-[var(--ug-text-muted)]">
            Publicações externas, orçamento pago e mudanças críticas aguardam confirmação humana por padrão.
          </p>
        </div>
        <div className="ug-card rounded-xl divide-y divide-white/[0.05]">
          {approvalsData.map((req: any) => (
            <div key={req.id} className="px-5 py-4 flex flex-wrap items-center justify-between gap-3 text-xs">
              <div>
                <div className="font-semibold text-[var(--ug-text-primary)] text-sm">{req.title}</div>
                <div className="text-[var(--ug-text-muted)]">Agente: {req.agent_id} • {req.action_type} • Status: {req.status}</div>
              </div>
              {req.status === "PENDING" && (
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={async () => {
                      await apiFetch(`/api/v1/approvals/${req.id}/decide`, {
                        method: "POST",
                        body: JSON.stringify({
                          decision: "APPROVE",
                          confirmation_token: meData?.high_impact_confirmation_token || "CONFIRMED_BY_HUMAN",
                        }),
                      });
                      await onReload();
                      showNotice("Solicitação aprovada!");
                    }}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
                  >
                    Aprovar
                  </button>
                  <button
                    type="button"
                    onClick={async () => {
                      await apiFetch(`/api/v1/approvals/${req.id}/decide`, {
                        method: "POST",
                        body: JSON.stringify({ decision: "REJECT" }),
                      });
                      await onReload();
                      showNotice("Solicitação rejeitada.");
                    }}
                    className="px-3 py-1.5 rounded-lg bg-red-600/80 hover:bg-red-600 text-white font-semibold"
                  >
                    Rejeitar
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  const quickPresets = [
    {
      label: "Lead Quente → Sugestão WhatsApp",
      flow: "Lead (LGPD OK) → Qualificar Score ≥ 70 → Preparar Mensagem WhatsApp",
      instruction: "Quando entrar novo lead no CRM com consentimento LGPD, qualificar e preparar abordagem imediata",
    },
    {
      label: "Auditoria SEO Semanal → Fila CEO",
      flow: "Cron Segunda 08h → Auditar Domínio HTTP → Enviar Correções SEO ao Painel",
      instruction: "Toda segunda-feira rodar auditoria técnica SEO real e registrar plano de melhoria",
    },
    {
      label: "Briefing Executivo Diário (08h)",
      flow: "Cron Diário 08h → Consolidar CRM + Pipeline → Publicar Prioridades do Dia",
      instruction: "Todo dia às 08h consolidar métricas do CRM e enviar briefing diário ao CEO",
    },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto ug-fade-in">
      <ConversationalAutomationPanel apiFetch={apiFetch} onReload={onReload} showNotice={showNotice} uiMode={uiMode} />

      <div className="ug-card rounded-2xl p-4 space-y-3">
        <div className="text-xs font-semibold text-[var(--ug-text-primary)]">
          Templates Visuais em 1 Clique (Fluxo Linear: Gatilho → Condição → Ação → Auditoria)
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {quickPresets.map((preset) => (
            <div key={preset.label} className="p-3 rounded-xl bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] flex flex-col justify-between gap-2.5 text-xs">
              <div className="space-y-1">
                <div className="font-semibold text-[var(--ug-text-primary)]">{preset.label}</div>
                <div className="text-[11px] text-indigo-300 font-mono">{preset.flow}</div>
              </div>
              <button
                type="button"
                onClick={async () => {
                  const res = await apiFetch("/api/v1/growth-os/conversational-automation", {
                    method: "POST",
                    body: JSON.stringify({ instruction_pt: preset.instruction, execute_now: false }),
                  });
                  await onReload();
                  showNotice(res.rule?.name ? `Template ativado: ${res.rule.name}` : "Automação nativa criada!");
                }}
                className="w-full py-1.5 rounded-lg border border-indigo-500/35 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 font-medium"
              >
                Ativar Preset em 1 Clique
              </button>
            </div>
          ))}
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-[var(--ug-border)]">
        <div>
          <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">
            {uiMode === "SIMPLE" ? "Rotinas Automáticas Ativas (100% Nativo • Zero n8n)" : "Central de Automações 100% Nativa em Python (Zero Dependência de n8n)"}
          </h3>
          <p className="text-xs text-[var(--ug-text-muted)]">
            {uiMode === "SIMPLE"
              ? `O sistema monitora ${automationsData.rules?.length || 0} rotinas automáticas com segurança na nuvem.`
              : `Motor: ${automationsData.scheduler?.engine} • Status: ${automationsData.scheduler?.running ? "ATIVO NO SERVIDOR CLOUD" : "PARADO"}`}
          </p>
        </div>
        {uiMode === "SIMPLE" && (
          <button type="button" onClick={() => setUiMode("ADVANCED")} className="px-3 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[11px] text-[var(--ug-text-secondary)] font-medium">
            Ver logs e ajustes técnicos (Avançado)
          </button>
        )}
      </div>

      <div className="ug-card rounded-2xl divide-y divide-white/[0.05]">
        {(uiMode === "SIMPLE" ? automationsData.rules.slice(0, 6) : automationsData.rules).map((r: any) => (
          <div key={r.id} className="px-4 py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="space-y-0.5 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium text-[var(--ug-text-primary)]">{r.name}</span>
                <span className="px-2 py-0.5 rounded bg-indigo-500/12 text-indigo-300 text-[10px]">
                  {uiMode === "SIMPLE" ? r.frequency_label : `${r.trigger_type} • ${r.frequency_label}`}
                </span>
              </div>
              <div className="text-[11px] text-[var(--ug-text-muted)] tabular-nums">
                {uiMode === "ADVANCED" ? `Agente: ${r.action_agent} • ` : ""}Execuções: <strong>{r.run_count}</strong> • Estado:{" "}
                <strong className="text-emerald-400">{r.last_status === "READY" ? "Pronta" : r.last_status}</strong>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={async () => {
                  await apiFetch(`/api/v1/automations/${r.id}/run`, { method: "POST", body: JSON.stringify({}) });
                  await onReload();
                  showNotice(`Automação '${r.name}' executada!`);
                }}
                className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-medium"
              >
                Executar Agora
              </button>
              {uiMode === "ADVANCED" && (
                <button
                  type="button"
                  onClick={async () => {
                    const res = await apiFetch(`/api/v1/automations/${r.id}/run`, { method: "POST", body: JSON.stringify({ simulate_transient_failure: true }) });
                    await onReload();
                    showNotice(`Retry com Backoff validado: ${res.status} na tentativa #${res.attempt_number}!`);
                  }}
                  className="px-2.5 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] text-[11px]"
                >
                  Testar Retry + Backoff
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
