"use client";

import React, { useState } from "react";
import { Bot, Cpu, Play, ShieldCheck, Sliders, ChevronDown, ChevronUp, Info } from "lucide-react";
import { LegacyMenuId } from "@/lib/navigation";
import { EmptyState, StatusPill } from "@/components/DesignSystem";

const AGENT_FRIENDLY_META: Record<string, { dataUsed: string; scheduleHint: string; needsApproval: string }> = {
  AGENT_01_CEO: { dataUsed: "Indicadores financeiros reais, metas OKR e logs dos agentes", scheduleHint: "Diário às 08:00 e sob demanda", needsApproval: "Não (apenas leitura/briefing)" },
  AGENT_02_CMO: { dataUsed: "Personas, campanhas ativas e ROI por canal", scheduleHint: "Diário às 09:00 e 16:00", needsApproval: "Sim, se orçamento > R$ 10.000" },
  AGENT_03_SEO: { dataUsed: "Site oficial público, palavras-chave e artigos", scheduleHint: "Diário às 14:00 e Segunda 09:00", needsApproval: "Não" },
  AGENT_04_SOCIAL: { dataUsed: "Calendário editorial e status das integrações sociais", scheduleHint: "Diário às 07:00, 11:00 e 17:00", needsApproval: "Sim, antes de publicar externamente" },
  AGENT_05_CREATIVE: { dataUsed: "Ofertas da marca e títulos de campanhas", scheduleHint: "Diário às 10:00", needsApproval: "Não (gera peças locais PNG/MP4)" },
  AGENT_06_COPYWRITER: { dataUsed: "Personas, benefícios e frameworks AIDA/PAS", scheduleHint: "Diário às 10:00", needsApproval: "Não" },
  AGENT_07_GROWTH: { dataUsed: "Métricas de funil e experimentos ICE", scheduleHint: "Diário às 17:00", needsApproval: "Não" },
  AGENT_08_SALES: { dataUsed: "Leads do CRM, score e propostas", scheduleHint: "Diário às 12:00 e 16:00", needsApproval: "Sim, para envio de proposta vinculante" },
  AGENT_09_COMPETITIVE: { dataUsed: "Sites públicos concorrentes (respeita robots.txt)", scheduleHint: "Diário às 15:00", needsApproval: "Não" },
  AGENT_10_FINANCE: { dataUsed: "Lançamentos reais, importados e custos de mídia", scheduleHint: "Diário às 18:00", needsApproval: "Imutável (sempre exige aprovação financeira)" },
  AGENT_11_CS: { dataUsed: "Pesquisas de NPS/CSAT e feedbacks de clientes", scheduleHint: "Monitoramento contínuo", needsApproval: "Não" },
};

export function AITeamAndGovernanceView({
  meData,
  agentsData,
  aiEnginesConfig,
  integrationsData,
  apiFetch,
  onReload,
  onNavigate,
  showNotice,
}: {
  meData: any;
  agentsData: any;
  aiEnginesConfig: any;
  integrationsData: any[];
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  onNavigate: (view: LegacyMenuId) => void;
  showNotice: (msg: string) => void;
}) {
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const [runningAgent, setRunningAgent] = useState<string>("");

  const currentAutonomy = meData?.active_tenant?.autonomy_default_level || 2;
  const costPolicy = aiEnginesConfig?.configuration?.cost_policy_mode || "FREE_ONLY";
  const defaultProvider = aiEnginesConfig?.configuration?.default_provider_key || "gemini";
  const defaultModel = aiEnginesConfig?.configuration?.default_text_model || "gemini-2.5-flash";
  const recentExecs = aiEnginesConfig?.recent_executions || [];
  const connectedIntegrations = (integrationsData || []).filter((i: any) => i.status === "CONNECTED");

  return (
    <div className="space-y-6">
      {/* Resumo simples para usuário leigo + Proteção Financeira */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="ug-card rounded-2xl p-5 space-y-2 border-indigo-500/30">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-indigo-300 flex items-center gap-1.5">
              <Cpu className="w-4 h-4" aria-hidden="true" /> Motor de IA Prioritário
            </span>
            <StatusPill
              status={costPolicy === "FREE_ONLY" ? "EXECUTED" : "PENDING"}
              label={costPolicy === "FREE_ONLY" ? "Somente Gratuito" : "Aprovado pelo Diretor"}
            />
          </div>
          <div className="text-lg font-bold text-white uppercase">{defaultProvider}</div>
          <p className="text-xs text-slate-400">
            {costPolicy === "FREE_ONLY"
              ? "Proteção de custos ativa: modelos pagos ficam bloqueados automaticamente para evitar qualquer cobrança inesperada."
              : "Uso de modelos pagos habilitado mediante autorização explícita."}
          </p>
          <button
            type="button"
            onClick={() => onNavigate("ai_engines")}
            className="text-xs font-semibold text-indigo-400 hover:underline pt-1 inline-block"
          >
            Configurar chaves e modelos →
          </button>
        </div>

        <div className="ug-card rounded-2xl p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-emerald-300 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4" aria-hidden="true" /> Como sua Equipe IA Opera
            </span>
            <span className="text-[11px] font-bold text-slate-300">Nível {currentAutonomy}</span>
          </div>
          <div className="flex gap-1.5 pt-1">
            {[
              { lvl: 1, name: "1. Assistido" },
              { lvl: 2, name: "2. Semiautônomo" },
              { lvl: 3, name: "3. Autônomo" },
            ].map((opt) => (
              <button
                key={opt.lvl}
                type="button"
                onClick={async () => {
                  await apiFetch("/api/v1/tenants/current", {
                    method: "PUT",
                    body: JSON.stringify({ autonomy_default_level: opt.lvl }),
                  });
                  await onReload();
                  showNotice(`Autonomia da IA ajustada para ${opt.name}!`);
                }}
                className={`flex-1 py-1.5 px-2 rounded-lg text-[11px] font-semibold border transition ${
                  currentAutonomy === opt.lvl
                    ? "bg-indigo-600 text-white border-indigo-500"
                    : "bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800"
                }`}
              >
                {opt.name}
              </button>
            ))}
          </div>
          <p className="text-[11px] text-slate-400">
            Ações financeiras e publicações externas sempre respeitam as travas de governança.
          </p>
        </div>

        <div className="ug-card rounded-2xl p-5 space-y-2">
          <span className="text-xs font-semibold text-sky-300 flex items-center gap-1.5">
            <Sliders className="w-4 h-4" aria-hidden="true" /> Integrações Disponíveis
          </span>
          <div className="text-lg font-bold text-white">
            {connectedIntegrations.length} conectada(s) de {(integrationsData || []).length}
          </div>
          <p className="text-xs text-slate-400">
            Quando falta credencial externa, os agentes geram pacotes prontos para você revisar sem interromper o trabalho.
          </p>
          <button
            type="button"
            onClick={() => onNavigate("integrations")}
            className="text-xs font-semibold text-indigo-400 hover:underline pt-1 inline-block"
          >
            Ver integrações →
          </button>
        </div>
      </div>

      {/* Catálogo Humano dos Agentes */}
      <section className="ug-card rounded-2xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-white ug-text-primary flex items-center gap-2">
              <Bot className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              Equipe Digital de Agentes Especializados ({(agentsData?.agents || []).length})
            </h3>
            <p className="text-xs text-slate-400">
              Veja exatamente o que cada agente faz, quando trabalha, quais dados usa e execute sob demanda.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowTechnicalDetails((v) => !v)}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs inline-flex items-center gap-1.5"
          >
            <Info className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
            {showTechnicalDetails ? "Ocultar detalhes técnicos" : "Detalhes técnicos (avançado)"}
            {showTechnicalDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {(agentsData?.agents || []).map((ag: any) => {
            const meta = AGENT_FRIENDLY_META[ag.id] || {
              dataUsed: "Dados operacionais do seu workspace",
              scheduleHint: "Sob demanda",
              needsApproval: "Conforme nível de autonomia",
            };
            return (
              <div key={ag.id} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between gap-3 text-xs">
                <div className="space-y-1.5">
                  <div className="flex items-start justify-between gap-2">
                    <div className="font-bold text-white">{ag.name}</div>
                    <StatusPill status="EXECUTED" label="Pronto" />
                  </div>
                  <p className="text-slate-300 leading-relaxed">{ag.role}</p>
                  <div className="pt-1 space-y-1 text-[11px] text-slate-400">
                    <div><strong className="text-slate-300">Dados usados:</strong> {meta.dataUsed}</div>
                    <div><strong className="text-slate-300">Quando trabalha:</strong> {meta.scheduleHint}</div>
                    <div><strong className="text-slate-300">Requer aprovação?</strong> {meta.needsApproval}</div>
                  </div>
                  {showTechnicalDetails && (
                    <div className="mt-2 p-2 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-indigo-300">
                      ID: {ag.id} • Modelo Padrão: {defaultModel} • Ferramentas: {(ag.allowed_tools || []).join(", ") || "core"}
                    </div>
                  )}
                </div>

                <button
                  type="button"
                  disabled={runningAgent === ag.id}
                  onClick={async () => {
                    setRunningAgent(ag.id);
                    try {
                      await apiFetch(`/api/v1/agents/${ag.id}/execute`, {
                        method: "POST",
                        body: JSON.stringify({}),
                      });
                      await onReload();
                      showNotice(`${ag.name} executou sua rotina com sucesso!`);
                    } finally {
                      setRunningAgent("");
                    }
                  }}
                  className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold inline-flex items-center justify-center gap-1.5"
                >
                  <Play className="w-3 h-3" aria-hidden="true" />
                  {runningAgent === ag.id ? "Executando..." : "Executar Agora"}
                </button>
              </div>
            );
          })}
        </div>
      </section>

      {/* Histórico Transparente das Execuções de IA (Seção 13) */}
      <section className="ug-card rounded-2xl p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white ug-text-primary">Últimas Execuções da IA (Visão Transparente)</h3>
            <p className="text-xs text-slate-400">
              Cada item diferencia claramente o que foi executado, bloqueado por custo/cota ou que falhou.
            </p>
          </div>
          <button
            type="button"
            onClick={() => onNavigate("ai_engines")}
            className="text-xs font-semibold text-indigo-400 hover:underline"
          >
            Abrir Central de Motores →
          </button>
        </div>

        {recentExecs.length === 0 ? (
          <EmptyState
            title="Nenhuma execução via motor LLM registrada"
            description="Quando você gerar campanhas ou testar o motor de IA em Modelos & Provedores, cada solicitação aparecerá aqui."
            actionLabel="Configurar ou Testar Motor"
            onAction={() => onNavigate("ai_engines")}
          />
        ) : (
          <div className="space-y-2">
            {recentExecs.slice(0, 6).map((ex: any) => {
              const st = String(ex.status || "");
              const pill =
                st === "SUCCESS"
                  ? "EXECUTED"
                  : st.includes("BLOCKED") || st.includes("QUOTA")
                  ? "BLOCKED"
                  : st.includes("ERROR") || st.includes("FAILED")
                  ? "FAILED"
                  : "PENDING";
              return (
                <div key={ex.execution_uuid} className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-xs flex flex-wrap items-center justify-between gap-3">
                  <div className="space-y-0.5 min-w-0">
                    <div className="font-semibold text-white">
                      Solicitado para {ex.task_type} ({ex.requested_provider}:{ex.requested_model})
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {ex.executed_provider
                        ? `Executado em ${ex.executed_provider}:${ex.executed_model} • ${ex.total_tokens} tokens • Custo: R$ ${ex.estimated_cost_brl ?? 0}`
                        : ex.error_message || "Não executado — verifique status"}
                    </div>
                  </div>
                  <StatusPill status={pill} label={st} />
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
