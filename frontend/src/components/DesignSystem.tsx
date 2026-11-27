"use client";

import React, { useEffect } from "react";
import { X, CheckCircle2, AlertTriangle, Info, ShieldAlert, Clock, Ban, Sparkles } from "lucide-react";

/**
 * Design System 3.0 — Whisper-quiet semantic origin indicator.
 * Shows transparent provenance (REAL, ESTIMATED, SANDBOX, TEST/UNAVAILABLE) without border fatigue.
 */
export function OriginBadge({ origin }: { origin?: string }) {
  const o = (origin || "REAL").toUpperCase();
  const cfg: Record<string, { dot: string; text: string; bg: string; label: string }> = {
    REAL: { dot: "bg-emerald-400", text: "text-emerald-400", bg: "bg-emerald-500/10", label: "Dado Real" },
    IMPORTED: { dot: "bg-sky-400", text: "text-sky-400", bg: "bg-sky-500/10", label: "Importado" },
    ESTIMATED: { dot: "bg-amber-400", text: "text-amber-300", bg: "bg-amber-500/10", label: "Estimativa" },
    GOAL: { dot: "bg-indigo-400", text: "text-indigo-300", bg: "bg-indigo-500/10", label: "Meta" },
    SANDBOX: { dot: "bg-orange-400", text: "text-orange-300", bg: "bg-orange-500/10", label: "Sandbox" },
    SIMULATION: { dot: "bg-orange-400", text: "text-orange-300", bg: "bg-orange-500/10", label: "Simulação" },
    TEST: { dot: "bg-zinc-400", text: "text-[var(--ug-text-muted)]", bg: "bg-white/[0.04]", label: "Teste QA" },
  };
  const item = cfg[o] || cfg.REAL;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium ${item.bg} ${item.text}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${item.dot}`} aria-hidden="true" />
      <span>{item.label}</span>
    </span>
  );
}

/**
 * Design System 3.0 — StatusPill minimalista com ponto ou ícone sutil.
 */
export function StatusPill({
  status,
  label,
}: {
  status:
    | "EXECUTED"
    | "PENDING"
    | "BLOCKED"
    | "FAILED"
    | "SIMULATED"
    | "SANDBOX"
    | "NEEDS_CREDENTIALS"
    | "RUNNING";
  label?: string;
}) {
  const cfg: Record<string, { cls: string; text: string; icon: React.ReactNode }> = {
    EXECUTED: {
      cls: "bg-emerald-500/10 text-emerald-400",
      text: "Executado",
      icon: <CheckCircle2 className="w-3 h-3 shrink-0" aria-hidden="true" />,
    },
    RUNNING: {
      cls: "bg-indigo-500/12 text-indigo-300",
      text: "IA Executando",
      icon: <Sparkles className="w-3 h-3 shrink-0" aria-hidden="true" />,
    },
    PENDING: {
      cls: "bg-amber-500/12 text-amber-300",
      text: "Aguardando Aprovação",
      icon: <Clock className="w-3 h-3 shrink-0" aria-hidden="true" />,
    },
    BLOCKED: {
      cls: "bg-zinc-500/15 text-zinc-300",
      text: "Bloqueado",
      icon: <Ban className="w-3 h-3 shrink-0" aria-hidden="true" />,
    },
    FAILED: {
      cls: "bg-red-500/12 text-red-400",
      text: "Falhou",
      icon: <AlertTriangle className="w-3 h-3 shrink-0" aria-hidden="true" />,
    },
    SIMULATED: {
      cls: "bg-orange-500/12 text-orange-300",
      text: "Simulado",
      icon: <Info className="w-3 h-3 shrink-0" aria-hidden="true" />,
    },
    SANDBOX: {
      cls: "bg-orange-500/12 text-orange-300",
      text: "Sandbox",
      icon: <ShieldAlert className="w-3 h-3 shrink-0" aria-hidden="true" />,
    },
    NEEDS_CREDENTIALS: {
      cls: "bg-sky-500/12 text-sky-300",
      text: "Conectar ferramenta",
      icon: <Info className="w-3 h-3 shrink-0" aria-hidden="true" />,
    },
  };
  const item = cfg[status] || cfg.PENDING;
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium ${item.cls}`}
    >
      {item.icon}
      <span>{label || item.text}</span>
    </span>
  );
}

/**
 * Stripe-style hairline horizontal metric strip: zero nested boxes.
 */
export interface MetricStripItem {
  key: string;
  label: string;
  value: string | number;
  subtext?: string;
  origin?: string;
  onClick?: () => void;
}

export function MetricStrip({ items }: { items: MetricStripItem[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div
      className="ug-card rounded-xl grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 divide-y sm:divide-y-0 sm:divide-x divide-white/[0.06] overflow-hidden"
    >
      {items.map((item) => {
        const Wrapper: any = item.onClick ? "button" : "div";
        return (
          <Wrapper
            key={item.key}
            {...(item.onClick ? { type: "button", onClick: item.onClick } : {})}
            className={`px-4 py-3.5 text-left space-y-1 transition ${
              item.onClick ? "hover:bg-white/[0.025] cursor-pointer" : ""
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-[11px] font-medium text-[var(--ug-text-muted)] truncate">
                {item.label}
              </span>
              {item.origin && <OriginBadge origin={item.origin} />}
            </div>
            <div className="text-xl font-semibold tracking-tight text-[var(--ug-text-primary)] tabular-nums">
              {item.value}
            </div>
            {item.subtext && (
              <div className="text-[11px] text-[var(--ug-text-muted)] truncate">{item.subtext}</div>
            )}
          </Wrapper>
        );
      })}
    </div>
  );
}

/**
 * FilterTabBar — Minimalist underline tabs (zero boxed chips).
 */
export interface FilterTabOption {
  id: string;
  label: string;
  count?: number;
  icon?: React.ReactNode;
}

export function FilterTabBar({
  tabs,
  activeId,
  onChange,
  ariaLabel = "Filtros",
}: {
  tabs: FilterTabOption[];
  activeId: string;
  onChange: (id: string) => void;
  ariaLabel?: string;
}) {
  return (
    <div
      role="tablist"
      aria-label={ariaLabel}
      className="flex items-center gap-4 border-b border-[var(--ug-border)] overflow-x-auto"
    >
      {tabs.map((t) => {
        const active = t.id === activeId;
        return (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange(t.id)}
            className={`relative pb-2.5 pt-1 text-xs font-medium whitespace-nowrap inline-flex items-center gap-1.5 transition border-b-2 -mb-[1px] ${
              active
                ? "border-[var(--ug-accent)] text-[var(--ug-text-primary)] font-semibold"
                : "border-transparent text-[var(--ug-text-muted)] hover:text-[var(--ug-text-secondary)]"
            }`}
          >
            {t.icon}
            <span>{t.label}</span>
            {typeof t.count === "number" && (
              <span
                className={`px-1.5 py-0.2 rounded-full text-[10px] tabular-nums ${
                  active
                    ? "bg-indigo-500/15 text-indigo-300"
                    : "bg-white/[0.05] text-[var(--ug-text-muted)]"
                }`}
              >
                {t.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

export function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
}: {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div className="ug-card rounded-xl border-dashed p-8 text-center flex flex-col items-center justify-center gap-3">
      {icon && (
        <div className="w-10 h-10 rounded-full bg-indigo-500/10 flex items-center justify-center text-indigo-400">
          {icon}
        </div>
      )}
      <div className="space-y-1 max-w-md">
        <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">{title}</h4>
        <p className="text-xs text-[var(--ug-text-muted)] leading-relaxed">{description}</p>
      </div>
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="mt-1 px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}

export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <div
      className="ug-card rounded-xl p-5 space-y-3 animate-pulse"
      aria-busy="true"
      aria-label="Carregando conteúdo"
    >
      <div className="h-3 w-1/3 bg-white/[0.06] rounded" />
      <div className="h-6 w-1/2 bg-white/[0.08] rounded" />
      {Array.from({ length: Math.max(1, lines - 2) }).map((_, i) => (
        <div key={i} className="h-2.5 w-4/5 bg-white/[0.04] rounded" />
      ))}
    </div>
  );
}

export function Drawer({
  open,
  onClose,
  title,
  subtitle,
  children,
  widthClass = "max-w-lg",
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  widthClass?: string;
}) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-black/55 backdrop-blur-[2px]"
      role="dialog"
      aria-modal="true"
      aria-label={title}
      onClick={onClose}
    >
      <div
        className={`relative w-full ${widthClass} h-full ug-surface border-l border-[var(--ug-border)] flex flex-col shadow-2xl ug-fade-in`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-5 py-4 border-b border-[var(--ug-border)] flex items-start justify-between gap-3 shrink-0">
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-[var(--ug-text-primary)] truncate">{title}</h3>
            {subtitle && (
              <p className="text-xs text-[var(--ug-text-muted)] mt-0.5 truncate">{subtitle}</p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar painel"
            className="p-1.5 rounded-lg text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)] hover:bg-white/[0.06] transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-5 space-y-4">{children}</div>
      </div>
    </div>
  );
}

export function ToastBanner({ message, onClose }: { message: string; onClose: () => void }) {
  if (!message) return null;
  return (
    <div
      role="status"
      aria-live="polite"
      className="fixed bottom-5 right-5 z-50 max-w-md px-4 py-2.5 rounded-xl bg-[#18181d] border border-white/10 text-zinc-100 shadow-2xl flex items-center gap-2.5 text-xs font-medium ug-fade-in"
    >
      <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" aria-hidden="true" />
      <span className="flex-1 leading-snug">{message}</span>
      <button
        type="button"
        onClick={onClose}
        aria-label="Fechar notificação"
        className="p-1 rounded-md hover:bg-white/10 text-zinc-400 hover:text-white transition"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
