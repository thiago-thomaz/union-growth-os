"use client";

import React from "react";
import { Activity, ShieldCheck, TrendingUp } from "lucide-react";
import { Drawer, OriginBadge, StatusPill } from "@/components/DesignSystem";
import { UIMode, simplifyTechnicalText } from "@/lib/plainLanguage";

export function BusinessHealthAndScoreDrawer({
  open,
  onClose,
  commandCenter,
  uiMode,
}: {
  open: boolean;
  onClose: () => void;
  commandCenter: any;
  uiMode: UIMode;
}) {
  if (!commandCenter) return null;
  const gs = commandCenter.growth_score || {
    score: 0,
    max_score: 100,
    formula: "",
    components: [],
    limitations: [],
    next_actions_to_improve: [],
  };
  const health: any[] = commandCenter.business_health || [];

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
    <Drawer
      open={open}
      onClose={onClose}
      title={`Saúde do Negócio (${health.length} dimensões) & Growth Score (${gs.score}/100)`}
      subtitle="Transparência auditável sobre seus dados reais, sem números inventados"
      widthClass="max-w-2xl"
    >
      <div className="space-y-6 text-xs">
        {/* Bloco 1 — Growth Score Documentado */}
        <section className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <h4 className="font-semibold text-[var(--ug-text-primary)] flex items-center gap-1.5">
              <TrendingUp className="w-4 h-4 text-emerald-400" aria-hidden="true" />
              Growth Score Documentado
            </h4>
            <div className="flex items-center gap-2">
              <OriginBadge origin="REAL" />
              <span className="text-base font-semibold text-indigo-400 tabular-nums">
                {gs.score}/{gs.max_score || 100}
              </span>
            </div>
          </div>

          <div className="ug-card rounded-xl p-4 space-y-2.5">
            {(gs.components || []).map((c: any) => (
              <div key={c.pillar} className="space-y-1">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-[var(--ug-text-secondary)]">{c.pillar}</span>
                  <span className="font-semibold text-[var(--ug-text-primary)] tabular-nums">
                    {c.score}/{c.max}
                  </span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                  <div
                    className="h-full bg-indigo-500 rounded-full"
                    style={{ width: `${Math.round((c.score / (c.max || 20)) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {gs.formula && (
            <p className="text-[11px] text-[var(--ug-text-secondary)] leading-relaxed">
              <strong className="text-[var(--ug-text-primary)]">Critério:</strong> {gs.formula}
            </p>
          )}

          {(gs.next_actions_to_improve || []).length > 0 && (
            <div className="space-y-1">
              <div className="text-[11px] font-semibold text-emerald-400">Como melhorar sua nota agora:</div>
              <ul className="list-disc pl-4 space-y-0.5 text-[11px] text-[var(--ug-text-secondary)]">
                {gs.next_actions_to_improve.map((n: string, i: number) => (
                  <li key={i}>{simplifyTechnicalText(n, uiMode)}</li>
                ))}
              </ul>
            </div>
          )}

          {(gs.limitations || []).length > 0 && (
            <div className="space-y-1">
              <div className="text-[11px] font-semibold text-amber-400">Limitações transparentes:</div>
              <ul className="list-disc pl-4 space-y-0.5 text-[11px] text-[var(--ug-text-muted)]">
                {gs.limitations.map((l: string, i: number) => (
                  <li key={i}>{simplifyTechnicalText(l, uiMode)}</li>
                ))}
              </ul>
            </div>
          )}
        </section>

        {/* Bloco 2 — 12 Dimensões de Business Health */}
        <section className="space-y-3 pt-4 border-t border-[var(--ug-border)]">
          <h4 className="font-semibold text-[var(--ug-text-primary)] flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-emerald-400" aria-hidden="true" />
            Business Health — 12 Dimensões Reais
          </h4>
          <div className="ug-card rounded-xl divide-y divide-white/[0.05]">
            {health.map((h: any) => (
              <div key={h.key} className="px-4 py-3 flex items-start justify-between gap-4">
                <div className="min-w-0 space-y-0.5">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-[var(--ug-text-primary)]">{h.label}</span>
                    <OriginBadge origin={h.data_origin === "NAO_DISPONIVEL" ? "TEST" : h.data_origin} />
                  </div>
                  <p className="text-[11px] text-[var(--ug-text-muted)] leading-relaxed">
                    {simplifyTechnicalText(h.summary, uiMode)}
                  </p>
                </div>
                <div className="text-right shrink-0 space-y-1">
                  <div className="font-semibold text-[var(--ug-text-primary)] tabular-nums">{h.value_label}</div>
                  <StatusPill status={statusTone(h.status_label)} label={statusText(h.status_label)} />
                </div>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-[var(--ug-text-muted)]">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" aria-hidden="true" />
            <span>Dados ausentes de integrações externas nunca são preenchidos com estimativas falsas.</span>
          </div>
        </section>
      </div>
    </Drawer>
  );
}

/** Compatibility re-export so existing lazy imports stay valid if referenced externally. */
export function GrowthCommandCenter() {
  return null;
}
