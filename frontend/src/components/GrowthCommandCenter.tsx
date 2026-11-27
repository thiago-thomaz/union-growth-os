"use client";

import React, { useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Bot,
  Calendar,
  CheckCircle2,
  Compass,
  Play,
  Radar,
  Send,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  XCircle,
} from "lucide-react";
import { LegacyMenuId } from "@/lib/navigation";
import { EmptyState, OriginBadge, StatusPill } from "@/components/DesignSystem";

export function GrowthCommandCenter({
  meData,
  commandCenter,
  uiMode,
  apiFetch,
  onReload,
  onNavigate,
  onOpenOnboarding,
  showNotice,
}: {
  meData: any;
  commandCenter: any;
  uiMode: "SIMPLE" | "ADVANCED";
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  onNavigate: (view: LegacyMenuId) => void;
  onOpenOnboarding: () => void;
  showNotice: (msg: string) => void;
}) {
  const [askInput, setAskInput] = useState("");
  const [askBusy, setAskBusy] = useState(false);
  const [askResult, setAskResult] = useState<any>(null);
  const [execBusyId, setExecBusyId] = useState("");
  const [showFormula, setShowFormula] = useState(false);

  if (!commandCenter) return null;

  const gs = commandCenter.growth_score || { score: 0, max_score: 100, components: [], limitations: [], next_actions_to_improve: [] };
  const health: any[] = commandCenter.business_health || [];
  const briefing = commandCenter.ceo_briefing || {};
  const opportunities: any[] = commandCenter.opportunity_radar || [];
  const execActions: any[] = commandCenter.executive_actions || [];
  const visibleHealth = uiMode === "SIMPLE" ? health.slice(0, 6) : health;

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

  const statusTone = (st: string) => {
    if (st === "SAUDAVEL") return "EXECUTED";
    if (st === "ATENCAO") return "PENDING";
    if (st === "CRITICO") return "FAILED";
    return "NEEDS_CREDENTIALS";
  };

  const statusText = (st: string) => {
    if (st === "SAUDAVEL") return "Saudável";
    if (st === "ATENCAO") return "Atenção";
    if (st === "CRITICO") return "Crítico";
    return "Não Disponível";
  };

  return (
    <div className="space-y-6">
      {/* 1. ASK UNION — COPILOTO ESTRUTURADO EM LINGUAGEM NATURAL */}
      <section
        aria-label="Ask Union — Copiloto de Crescimento"
        className="ug-card ug-onboarding-banner rounded-2xl border border-indigo-500/35 p-5 space-y-4"
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              <h3 className="text-sm font-bold text-white ug-text-primary">
                ASK UNION — O que você quer destravar hoje em {meData?.active_tenant?.brand_name}?
              </h3>
            </div>
            <p className="text-xs text-slate-400 ug-text-muted mt-0.5">
              Peça em linguagem natural. A IA lê sua marca, CRM, site e campanhas reais para montar um plano executável (custo R$ 0,00).
            </p>
          </div>
          <button
            type="button"
            onClick={onOpenOnboarding}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-300 text-xs font-semibold inline-flex items-center gap-1.5"
          >
            <Compass className="w-3.5 h-3.5" aria-hidden="true" />
            Onboarding 6 Etapas (Passo {meData?.active_tenant?.onboarding_step || 1}/6)
          </button>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            submitAskUnion();
          }}
          className="flex flex-col sm:flex-row gap-2"
        >
          <input
            id="ug-ask-union-input"
            value={askInput}
            onChange={(e) => setAskInput(e.target.value)}
            aria-label="Perguntar ao Ask Union"
            placeholder="Ex.: Quero vender mais • Quero divulgar meu site • Organizar meus leads • Criar automação"
            className="flex-1 px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700 text-xs text-white placeholder:text-slate-500"
          />
          <button
            type="submit"
            disabled={askBusy}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold inline-flex items-center justify-center gap-1.5 shrink-0"
          >
            <Send className="w-3.5 h-3.5" aria-hidden="true" />
            {askBusy ? "Analisando..." : "Perguntar ao Ask Union"}
          </button>
        </form>

        <div className="flex flex-wrap gap-1.5">
          {[
            "Quero vender mais",
            "Quero divulgar meu site nas redes",
            "Como melhorar meu Google / SEO?",
            "Quando entrar um lead, analisar e avisar",
          ].map((pill) => (
            <button
              key={pill}
              type="button"
              onClick={() => submitAskUnion(pill)}
              className="px-2.5 py-1 rounded-full bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 text-[11px] text-slate-300 transition"
            >
              {pill}
            </button>
          ))}
        </div>

        {askResult && (
          <div className="p-4 rounded-xl bg-slate-950/80 border border-indigo-500/30 space-y-3 text-xs">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-bold text-indigo-300">
                Plano Estruturado ({askResult.intent})
              </span>
              <OriginBadge origin="REAL" />
            </div>
            <p className="text-slate-300">{askResult.diagnosis}</p>
            <ul className="space-y-1 text-slate-200">
              {(askResult.plan_steps || []).map((st: string, i: number) => (
                <li key={i}>{st}</li>
              ))}
            </ul>
            {(askResult.suggested_actions || []).length > 0 && (
              <div className="flex flex-wrap gap-2 pt-1">
                {askResult.suggested_actions.map((sa: any) => (
                  <div key={sa.id} className="flex items-center gap-1.5">
                    {sa.id !== "act-create-conv-auto" && (
                      <button
                        type="button"
                        disabled={execBusyId === `${sa.id}:EXECUTE`}
                        onClick={() => handleActionDecision(sa.id, "EXECUTE")}
                        className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-semibold inline-flex items-center gap-1"
                      >
                        <Play className="w-3 h-3" aria-hidden="true" />
                        {execBusyId === `${sa.id}:EXECUTE` ? "Executando..." : sa.label}
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => onNavigate(sa.target_view)}
                      className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px]"
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

      {/* 2. GROWTH SCORE DOCUMENTADO + AI CEO BRIEFING */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <section className="ug-card rounded-2xl p-5 lg:col-span-5 space-y-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-white ug-text-primary flex items-center gap-1.5">
                <TrendingUp className="w-4 h-4 text-emerald-400" aria-hidden="true" />
                Growth Score Documentado
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">Nota auditável calculada 100% sobre seus dados reais.</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-extrabold text-indigo-300">{gs.score}/100</div>
              <OriginBadge origin="REAL" />
            </div>
          </div>

          <div className="w-full h-2.5 rounded-full bg-slate-900 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-emerald-500 transition-all"
              style={{ width: `${gs.score}%` }}
            />
          </div>

          <div className="space-y-2 text-xs">
            {(gs.components || []).map((c: any) => (
              <div key={c.pillar} className="space-y-1">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-300">{c.pillar}</span>
                  <span className="font-bold text-white">{c.score}/{c.max}</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-slate-900 overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${Math.round((c.score / c.max) * 100)}%` }} />
                </div>
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={() => setShowFormula((v) => !v)}
            className="text-[11px] text-indigo-300 hover:underline font-medium"
          >
            {showFormula ? "Ocultar metodologia e limitações ↑" : "Ver metodologia, limitações e como subir a nota ↓"}
          </button>

          {showFormula && (
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-[11px]">
              <div className="text-slate-300"><strong>Fórmula:</strong> {gs.formula}</div>
              {(gs.limitations || []).length > 0 && (
                <div>
                  <strong className="text-amber-300 block">Limitações atuais:</strong>
                  <ul className="list-disc pl-4 text-slate-400 space-y-0.5">
                    {gs.limitations.map((l: string, i: number) => <li key={i}>{l}</li>)}
                  </ul>
                </div>
              )}
              {(gs.next_actions_to_improve || []).length > 0 && (
                <div>
                  <strong className="text-emerald-300 block">Próximas ações para evoluir:</strong>
                  <ul className="list-disc pl-4 text-slate-300 space-y-0.5">
                    {gs.next_actions_to_improve.map((n: string, i: number) => <li key={i}>{n}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>

        <section className="ug-card rounded-2xl p-5 lg:col-span-7 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h3 className="text-sm font-bold text-white ug-text-primary flex items-center gap-1.5">
                <Bot className="w-4 h-4 text-indigo-400" aria-hidden="true" />
                AI CEO Briefing — Hoje &amp; Semana
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">{briefing.headline}</p>
            </div>
            <OriginBadge origin="REAL" />
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">{briefing.summary}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1.5">
              <div className="font-bold text-indigo-300">Plano de Hoje</div>
              <ul className="space-y-1 text-[11px] text-slate-300 list-disc pl-4">
                {(briefing.day_plan || []).map((d: string, i: number) => <li key={i}>{d}</li>)}
              </ul>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1.5">
              <div className="font-bold text-emerald-300">Foco da Semana</div>
              <ul className="space-y-1 text-[11px] text-slate-300 list-disc pl-4">
                {(briefing.week_plan || []).map((w: string, i: number) => <li key={i}>{w}</li>)}
              </ul>
            </div>
          </div>
        </section>
      </div>

      {/* 3. BUSINESS HEALTH (12 PILARES TRANSPARENTES) */}
      <section className="ug-card rounded-2xl p-5 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h3 className="text-sm font-bold text-white ug-text-primary flex items-center gap-1.5">
              <Activity className="w-4 h-4 text-emerald-400" aria-hidden="true" />
              Business Health ({visibleHealth.length} de {health.length} dimensões)
            </h3>
            <p className="text-xs text-slate-400">
              Transparência total: cada indicador mostra se é Dado Real, Estimativa ou Não Disponível.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {visibleHealth.map((h: any) => (
            <div key={h.key} className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2 text-xs">
              <div className="flex items-center justify-between gap-2">
                <span className="font-semibold text-white truncate">{h.label}</span>
                <OriginBadge origin={h.data_origin === "NAO_DISPONIVEL" ? "TEST" : h.data_origin} />
              </div>
              <div className="flex items-center justify-between gap-2">
                <span className="text-sm font-bold text-indigo-300">{h.value_label}</span>
                <StatusPill status={statusTone(h.status_label)} label={statusText(h.status_label)} />
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">{h.summary}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 4. OPPORTUNITY RADAR & EXECUTIVE ACTION CENTER */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <section className="ug-card rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white ug-text-primary flex items-center gap-1.5">
              <Radar className="w-4 h-4 text-amber-400" aria-hidden="true" />
              Opportunity Radar ({opportunities.length})
            </h3>
            <span className="text-[11px] text-slate-400">Baseado em gaps reais</span>
          </div>

          {opportunities.length === 0 ? (
            <EmptyState
              title="Nenhuma lacuna pendente"
              description="Todos os pilares avaliados possuem atividade registrada."
            />
          ) : (
            <div className="space-y-2.5">
              {opportunities.slice(0, uiMode === "SIMPLE" ? 4 : 8).map((op: any) => (
                <div key={op.id} className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-1.5">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="font-bold text-white">{op.category}: {op.name}</span>
                    <StatusPill status={op.priority === "ALTA" ? "PENDING" : "EXECUTED"} label={`Prioridade ${op.priority}`} />
                  </div>
                  <p className="text-[11px] text-slate-300">{op.description}</p>
                  <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-[11px] text-slate-400">
                    <span>Impacto: <strong className="text-slate-200">{op.estimated_impact}</strong> • Custo: R$ {op.estimated_cost_brl}</span>
                    <button
                      type="button"
                      onClick={() => onNavigate(op.target_view)}
                      className="text-indigo-300 hover:underline font-semibold inline-flex items-center gap-1"
                    >
                      {op.next_action_label} <ArrowRight className="w-3 h-3" aria-hidden="true" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="ug-card rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white ug-text-primary flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" aria-hidden="true" />
              Executive Action Center ({execActions.length})
            </h3>
            <span className="text-[11px] text-emerald-400 font-semibold">Custo R$ 0,00</span>
          </div>

          <div className="space-y-2.5">
            {execActions.map((act: any) => (
              <div key={act.id} className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-2">
                <div className="font-bold text-white">{act.what_to_do}</div>
                <div className="text-[11px] text-slate-300">
                  <strong>Por que:</strong> {act.why_do_it} • <strong>Resultado:</strong> {act.expected_result}
                </div>
                <div className="text-[11px] text-slate-400">
                  Tempo: {act.estimated_time} • Risco: {act.risk} • Custo: R$ {act.cost_brl ?? 0}
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  <button
                    type="button"
                    disabled={Boolean(execBusyId)}
                    onClick={() => handleActionDecision(act.id, "EXECUTE")}
                    className="px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-semibold inline-flex items-center gap-1"
                  >
                    <Play className="w-3 h-3" aria-hidden="true" />
                    Executar
                  </button>
                  <button
                    type="button"
                    disabled={Boolean(execBusyId)}
                    onClick={() => handleActionDecision(act.id, "SCHEDULE")}
                    className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] inline-flex items-center gap-1"
                  >
                    <Calendar className="w-3 h-3" aria-hidden="true" />
                    Agendar
                  </button>
                  <button
                    type="button"
                    disabled={Boolean(execBusyId)}
                    onClick={() => handleActionDecision(act.id, "REJECT")}
                    className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-red-900/40 text-slate-300 text-[11px] inline-flex items-center gap-1"
                  >
                    <XCircle className="w-3 h-3" aria-hidden="true" />
                    Ignorar
                  </button>
                  <button
                    type="button"
                    onClick={() => onNavigate(act.target_view)}
                    className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-indigo-300 text-[11px]"
                  >
                    Ver detalhes
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
