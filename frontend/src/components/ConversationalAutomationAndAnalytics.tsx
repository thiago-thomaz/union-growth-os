"use client";

import React, { useState } from "react";
import { BarChart3, CheckCircle2, Play, Sparkles, Workflow } from "lucide-react";
import { OriginBadge, StatusPill } from "@/components/DesignSystem";

export function ConversationalAutomationPanel({
  apiFetch,
  onReload,
  showNotice,
}: {
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  showNotice: (msg: string) => void;
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
        showNotice(`Automação '${res.workflow_preview?.name}' salva em Python/APScheduler!`);
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
    <section aria-label="Construtor Conversacional de Automações" className="bg-[#0f1629] border border-indigo-500/35 rounded-xl p-5 space-y-4">
      <div>
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Workflow className="w-4 h-4 text-indigo-400" aria-hidden="true" />
          Criar Automação em Linguagem Natural (100% Python Nativo • Zero n8n)
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Descreva com suas palavras o que quer automatizar. Nós mostramos os gatilhos, riscos e simulação antes de você autorizar.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-2">
        <input
          id="ug-conv-auto-input"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          aria-label="Descreva a automação desejada"
          placeholder="Ex.: Leads que não responderam em 3 dias recebam tarefa de follow-up"
          className="flex-1 px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white"
        />
        <button
          type="button"
          disabled={busy}
          onClick={() => runBuilder(false)}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold inline-flex items-center justify-center gap-1.5"
        >
          <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
          {busy ? "Analisando..." : "Simular Fluxo (Dry-Run)"}
        </button>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {examples.map((ex) => (
          <button
            key={ex}
            type="button"
            onClick={() => runBuilder(false, ex)}
            className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-700 text-[11px] text-slate-300"
          >
            {ex}
          </button>
        ))}
      </div>

      {preview?.workflow_preview && (
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2.5 text-xs">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="font-bold text-indigo-300">{preview.workflow_preview.name}</span>
            <StatusPill status={preview.status === "ACTIVATED" ? "EXECUTED" : "PENDING"} label={preview.status} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-[11px]">
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
              <strong className="text-slate-300 block">1. Gatilho</strong>
              <span className="text-slate-200">{preview.workflow_preview.trigger_label}</span>
            </div>
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
              <strong className="text-slate-300 block">2. Condição</strong>
              <span className="text-slate-200">{preview.workflow_preview.condition}</span>
            </div>
            <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
              <strong className="text-slate-300 block">3. Ação &amp; Risco</strong>
              <span className="text-slate-200">{preview.workflow_preview.action_label} • {preview.workflow_preview.risk}</span>
            </div>
          </div>
          <div className="p-2.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-200 text-[11px]">
            <strong>Teste de Simulação:</strong> {preview.workflow_preview.dry_run_result} • Custo estimado: R$ {preview.workflow_preview.estimated_cost_brl}
          </div>
          {preview.status === "PREVIEW_READY" && (
            <button
              type="button"
              disabled={busy}
              onClick={() => runBuilder(true)}
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold inline-flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
              Aprovar e Ativar Automação no Servidor
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
    <section aria-label="Analytics e Atribuição de Resultados" className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-indigo-400" aria-hidden="true" />
            Analytics, Funil &amp; Atribuição de Marketing
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">{attribution.attribution_methodology}</p>
        </div>
        <StatusPill
          status={attribution.external_analytics_status === "CONNECTED" ? "EXECUTED" : "NEEDS_CREDENTIALS"}
          label={attribution.external_analytics_status === "CONNECTED" ? "GA4/Ads Conectado" : "GA4 Externo: Não Disponível"}
        />
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 text-xs">
        {funnel.map((st: any) => (
          <div key={st.stage} className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
            <div className="text-[11px] text-slate-400 truncate">{st.stage}</div>
            <div className="text-lg font-bold text-white">{st.count}</div>
            <OriginBadge origin={st.origin} />
          </div>
        ))}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="text-[11px] text-slate-400 border-b border-slate-800">
              <th className="py-2 pr-3">Canal / Origem</th>
              <th className="py-2 pr-3">Leads Reais</th>
              <th className="py-2 pr-3">Qualificados</th>
              <th className="py-2 pr-3">Pipeline Estimado (R$)</th>
              <th className="py-2">Classificação</th>
            </tr>
          </thead>
          <tbody>
            {channels.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-3 text-slate-400">
                  Nenhum lead real atribuído por canal ainda (o sistema não inventa tráfego).
                </td>
              </tr>
            ) : (
              channels.map((ch: any) => (
                <tr key={ch.channel} className="border-b border-slate-900 text-slate-200">
                  <td className="py-2 pr-3 font-medium">{ch.channel}</td>
                  <td className="py-2 pr-3">{ch.leads}</td>
                  <td className="py-2 pr-3">{ch.qualified_leads}</td>
                  <td className="py-2 pr-3">R$ {Number(ch.estimated_pipeline_brl || 0).toLocaleString("pt-BR")}</td>
                  <td className="py-2"><OriginBadge origin={ch.data_origin} /></td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
