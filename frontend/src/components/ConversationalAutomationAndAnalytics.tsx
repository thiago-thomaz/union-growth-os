"use client";

import React, { useState } from "react";
import { BarChart3, CheckCircle2, Sparkles, Workflow } from "lucide-react";
import { OriginBadge, StatusPill } from "@/components/DesignSystem";
import { UIMode, simplifyTechnicalText } from "@/lib/plainLanguage";

export function ConversationalAutomationPanel({
  apiFetch,
  onReload,
  showNotice,
  uiMode = "SIMPLE",
}: {
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  showNotice: (msg: string) => void;
  uiMode?: UIMode;
}) {
  const [prompt, setPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [preview, setPreview] = useState<any>(null);

  const runBuilder = async (approveCreate: boolean, overridePrompt?: string) => {
    const q = (overridePrompt ?? prompt).trim();
    if (q.length < 4) {
      showNotice("Descreva a automação desejada em português simples.");
      return;
    }
    setBusy(true);
    try {
      const res = await apiFetch("/api/v1/automations/conversational-build", {
        method: "POST",
        body: JSON.stringify({ prompt: q, dry_run: true, approve_create: approveCreate }),
      });
      setPreview(res);
      if (overridePrompt) setPrompt(overridePrompt);
      if (approveCreate) {
        await onReload();
        showNotice(`Automação '${res.workflow_preview?.name}' salva em Python nativo!`);
      }
    } catch (e: any) {
      showNotice(e?.message || "Erro no construtor conversacional.");
    } finally {
      setBusy(false);
    }
  };

  const examples = [
    "Quando entrar um lead, quero que a IA analise e me avise",
    "Leads que não responderam em 3 dias recebam tarefa de follow-up",
    "Quero gerar um relatório toda segunda-feira",
    "Acompanhar clientes deixando de comprar",
  ];

  return (
    <section aria-label="Construtor Conversacional de Automações" className="ug-spotlight-strip rounded-2xl p-5 space-y-4">
      <div className="space-y-0.5">
        <h3 className="text-sm font-semibold text-[var(--ug-text-primary)] flex items-center gap-2">
          <Workflow className="w-4 h-4 text-indigo-400" aria-hidden="true" />
          <span>
            {uiMode === "SIMPLE"
              ? "Criar Automação Falando em Português (100% Nativo • Zero n8n)"
              : "Criar Automação em Linguagem Natural (100% Python Nativo • Zero n8n)"}
          </span>
        </h3>
        <p className="text-xs text-[var(--ug-text-muted)]">
          Descreva o que quer automatizar. Simulamos quando vai rodar e o impacto antes de ativar.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-2">
        <input
          id="ug-conv-auto-input"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          aria-label="Descreva a automação desejada"
          placeholder="Ex.: Leads que não responderam em 3 dias recebam tarefa de follow-up"
          className="flex-1 px-3 py-2 rounded-xl bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
        />
        <button
          type="button"
          disabled={busy}
          onClick={() => runBuilder(false)}
          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium inline-flex items-center justify-center gap-1.5 shrink-0"
        >
          <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
          <span>{busy ? "Analisando..." : "Simular Fluxo (Dry-Run)"}</span>
        </button>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {examples.map((ex) => (
          <button
            key={ex}
            type="button"
            onClick={() => runBuilder(false, ex)}
            className="px-2.5 py-1 rounded-full bg-white/[0.04] hover:bg-white/[0.08] border border-[var(--ug-border)] text-[11px] text-[var(--ug-text-secondary)] transition"
          >
            {ex}
          </button>
        ))}
      </div>

      {preview?.workflow_preview && (
        <div className="pt-3 border-t border-[var(--ug-border)] space-y-3 text-xs ug-fade-in">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="font-semibold text-[var(--ug-text-primary)]">{preview.workflow_preview.name}</span>
            <StatusPill status={preview.status === "ACTIVATED" ? "EXECUTED" : "PENDING"} label={preview.status} />
          </div>
          <div className="ug-card rounded-xl grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-white/[0.06] text-[11px]">
            <div className="p-3 space-y-0.5">
              <strong className="text-[var(--ug-text-muted)] block">
                {uiMode === "SIMPLE" ? "Quando essa automação deve começar" : "1. Gatilho"}
              </strong>
              <span className="text-[var(--ug-text-primary)]">{preview.workflow_preview.trigger_label}</span>
            </div>
            <div className="p-3 space-y-0.5">
              <strong className="text-[var(--ug-text-muted)] block">Condição aplicada</strong>
              <span className="text-[var(--ug-text-primary)]">
                {simplifyTechnicalText(preview.workflow_preview.condition, uiMode)}
              </span>
            </div>
            <div className="p-3 space-y-0.5">
              <strong className="text-[var(--ug-text-muted)] block">Ação &amp; Risco</strong>
              <span className="text-[var(--ug-text-primary)]">
                {preview.workflow_preview.action_label} • {preview.workflow_preview.risk}
              </span>
            </div>
          </div>
          <div className="text-[11px] text-emerald-400">
            <strong>Teste de Simulação:</strong> {preview.workflow_preview.dry_run_result} • Custo estimado: R${" "}
            {preview.workflow_preview.estimated_cost_brl}
          </div>
          {preview.status === "PREVIEW_READY" && (
            <button
              type="button"
              disabled={busy}
              onClick={() => runBuilder(true)}
              className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium inline-flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Aprovar e Ativar Automação no Servidor</span>
            </button>
          )}
        </div>
      )}
    </section>
  );
}

export function AnalyticsAttributionPanel({ attribution }: { attribution: any }) {
  if (!attribution) return null;
  const funnel: any[] = attribution.funnel || [];
  const channels: any[] = attribution.channels || [];

  return (
    <section aria-label="Analytics e Atribuição de Resultados" className="ug-card rounded-2xl p-5 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-[var(--ug-border-subtle)]">
        <div className="space-y-0.5">
          <h3 className="text-sm font-semibold text-[var(--ug-text-primary)] flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-indigo-400" aria-hidden="true" />
            <span>Analytics, Funil &amp; Atribuição de Marketing</span>
          </h3>
          <p className="text-xs text-[var(--ug-text-muted)]">{attribution.attribution_methodology}</p>
        </div>
        <StatusPill
          status={attribution.external_analytics_status === "CONNECTED" ? "EXECUTED" : "NEEDS_CREDENTIALS"}
          label={attribution.external_analytics_status === "CONNECTED" ? "GA4/Ads Conectado" : "GA4 Externo: Não Disponível"}
        />
      </div>

      {/* Funil horizontal em faixa única Stripe-style */}
      <div className="ug-card rounded-xl grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 divide-y sm:divide-y-0 sm:divide-x divide-white/[0.06] overflow-hidden text-xs">
        {funnel.map((st: any) => (
          <div key={st.stage} className="px-3.5 py-3 space-y-1">
            <div className="text-[11px] text-[var(--ug-text-muted)] truncate">{st.stage}</div>
            <div className="text-lg font-semibold text-[var(--ug-text-primary)] tabular-nums">{st.count}</div>
            <OriginBadge origin={st.origin} />
          </div>
        ))}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="text-[11px] text-[var(--ug-text-muted)] border-b border-[var(--ug-border)]">
              <th className="py-2 pr-3 font-medium">Canal / Origem</th>
              <th className="py-2 pr-3 font-medium">Leads Reais</th>
              <th className="py-2 pr-3 font-medium">Qualificados</th>
              <th className="py-2 pr-3 font-medium">Pipeline Estimado (R$)</th>
              <th className="py-2 font-medium">Origem dos Dados</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.05]">
            {channels.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-4 text-[var(--ug-text-muted)]">
                  Nenhum lead real atribuído por canal ainda (o sistema não inventa tráfego).
                </td>
              </tr>
            ) : (
              channels.map((ch: any) => (
                <tr key={ch.channel} className="text-[var(--ug-text-secondary)] hover:bg-white/[0.02]">
                  <td className="py-2.5 pr-3 font-medium text-[var(--ug-text-primary)]">{ch.channel}</td>
                  <td className="py-2.5 pr-3 tabular-nums">{ch.leads}</td>
                  <td className="py-2.5 pr-3 tabular-nums">{ch.qualified_leads}</td>
                  <td className="py-2.5 pr-3 tabular-nums">
                    R$ {Number(ch.estimated_pipeline_brl || 0).toLocaleString("pt-BR")}
                  </td>
                  <td className="py-2.5">
                    <OriginBadge origin={ch.data_origin} />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
