"use client";

import React, { useEffect, useState } from "react";
import { CheckCircle2, GitCommit, ShieldCheck, Sparkles, Tag, Wrench } from "lucide-react";
import { Drawer, StatusPill } from "@/components/DesignSystem";
import { LegacyMenuId } from "@/lib/navigation";

export function ReleaseHistoryDrawer({
  open,
  onClose,
  versionInfo,
  apiFetch,
  onNavigate,
}: {
  open: boolean;
  onClose: () => void;
  versionInfo: any;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onNavigate: (view: LegacyMenuId) => void;
}) {
  const [releasesData, setReleasesData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    let active = true;
    setLoading(true);
    apiFetch("/api/v1/system/releases")
      .then((res) => {
        if (active) setReleasesData(res);
      })
      .catch(() => null)
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [open, apiFetch]);

  const semver = versionInfo?.semver || { major: 2, minor: 4, patch: 0 };
  const releases = releasesData?.releases || [];

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title={`UNION GROWTH OS • v${versionInfo?.version || "2.4.0"}`}
      subtitle={`${versionInfo?.environment_label || "PRODUCTION"} | ${versionInfo?.platform_state || "STABLE"} • Build ${versionInfo?.short_commit || "local"}`}
      widthClass="max-w-2xl"
    >
      <div className="space-y-5 text-xs">
        {/* Status Atual da Plataforma */}
        <section className="ug-card rounded-xl p-4 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Tag className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              <span className="font-semibold text-[var(--ug-text-primary)]">
                Controle SemVer ({semver.major}.{semver.minor}.{semver.patch})
              </span>
            </div>
            <StatusPill
              status={versionInfo?.health?.healthy !== false ? "EXECUTED" : "FAILED"}
              label={versionInfo?.platform_state || "STABLE"}
            />
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
            <div className="p-2.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)]">
              <div className="text-[var(--ug-text-muted)]">Versão</div>
              <div className="font-semibold text-[var(--ug-text-primary)] tabular-nums">
                v{versionInfo?.version || "2.4.0"}
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)]">
              <div className="text-[var(--ug-text-muted)]">Ambiente</div>
              <div className="font-semibold text-indigo-400">{versionInfo?.environment_label || "PRODUCTION"}</div>
            </div>
            <div className="p-2.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)]">
              <div className="text-[var(--ug-text-muted)]">Commit</div>
              <div className="font-mono font-semibold text-[var(--ug-text-primary)] truncate">
                {versionInfo?.short_commit || "local"}
              </div>
            </div>
            <div className="p-2.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)]">
              <div className="text-[var(--ug-text-muted)]">Score Auditoria</div>
              <div className="font-semibold text-emerald-400 tabular-nums">
                {versionInfo?.latest_audit_score !== null && versionInfo?.latest_audit_score !== undefined
                  ? `${versionInfo.latest_audit_score}/100`
                  : "Executar auditoria"}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-[11px] text-[var(--ug-text-muted)]">
            <span>
              Banco: <strong className="text-[var(--ug-text-secondary)]">{versionInfo?.health?.database?.engine || "postgresql"}</strong> •{" "}
              Scheduler: <strong className="text-[var(--ug-text-secondary)]">{versionInfo?.health?.scheduler_jobs ?? 127} jobs</strong>
            </span>
            <button
              type="button"
              onClick={() => {
                onClose();
                onNavigate("audit");
              }}
              className="px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
            >
              Abrir Central de Auditoria →
            </button>
          </div>
        </section>

        {/* Histórico Persistido de Releases */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-[var(--ug-text-primary)] flex items-center gap-1.5">
              <GitCommit className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              <span>Histórico de Releases ({releases.length})</span>
            </h4>
            <span className="text-[11px] text-[var(--ug-text-muted)]">Fonte: release_manifest + PostgreSQL</span>
          </div>

          {loading ? (
            <div className="ug-card rounded-xl p-6 text-center text-[var(--ug-text-muted)]">
              Carregando histórico de versões...
            </div>
          ) : (
            <div className="space-y-3">
              {releases.map((rel: any) => (
                <div key={rel.version} className="ug-card rounded-xl p-4 space-y-2.5">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 font-mono font-semibold">
                        v{rel.version}
                      </span>
                      <span className="font-semibold text-[var(--ug-text-primary)]">{rel.title}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[10px]">
                      {rel.audit_score !== null && rel.audit_score !== undefined && (
                        <span className="px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-semibold tabular-nums">
                          Score {rel.audit_score}/100
                        </span>
                      )}
                      <span className="text-[var(--ug-text-muted)] tabular-nums">{rel.release_date}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 text-[10px] text-[var(--ug-text-muted)]">
                    <span>Tag: <code className="text-indigo-400">{rel.git_tag}</code></span>
                    <span>• Deploy: <strong>{rel.deploy_status}</strong></span>
                    <span>• Ambiente: <strong className="uppercase">{rel.environment}</strong></span>
                    {rel.commit_sha && <span>• Commit: <code className="font-mono">{String(rel.commit_sha).slice(0, 8)}</code></span>}
                  </div>

                  {rel.features?.length > 0 && (
                    <div className="space-y-1 pt-1">
                      <div className="text-[10px] font-semibold text-indigo-400 flex items-center gap-1">
                        <Sparkles className="w-3 h-3" aria-hidden="true" /> Funcionalidades
                      </div>
                      <ul className="list-disc pl-4 space-y-0.5 text-[11px] text-[var(--ug-text-secondary)]">
                        {rel.features.map((f: string, idx: number) => <li key={idx}>{f}</li>)}
                      </ul>
                    </div>
                  )}

                  {rel.fixes?.length > 0 && (
                    <div className="space-y-1">
                      <div className="text-[10px] font-semibold text-amber-300 flex items-center gap-1">
                        <Wrench className="w-3 h-3" aria-hidden="true" /> Correções
                      </div>
                      <ul className="list-disc pl-4 space-y-0.5 text-[11px] text-[var(--ug-text-muted)]">
                        {rel.fixes.map((f: string, idx: number) => <li key={idx}>{f}</li>)}
                      </ul>
                    </div>
                  )}

                  {rel.security_improvements?.length > 0 && (
                    <div className="space-y-1">
                      <div className="text-[10px] font-semibold text-emerald-400 flex items-center gap-1">
                        <ShieldCheck className="w-3 h-3" aria-hidden="true" /> Segurança
                      </div>
                      <ul className="list-disc pl-4 space-y-0.5 text-[11px] text-[var(--ug-text-muted)]">
                        {rel.security_improvements.map((s: string, idx: number) => <li key={idx}>{s}</li>)}
                      </ul>
                    </div>
                  )}

                  {rel.tests_summary && (
                    <div className="pt-1 border-t border-[var(--ug-border-subtle)] text-[10px] text-[var(--ug-text-muted)] flex items-center gap-1.5">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" aria-hidden="true" />
                      <span>Testes: {rel.tests_summary}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </Drawer>
  );
}
