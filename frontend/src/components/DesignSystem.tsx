"use client";

import React, { useEffect } from "react";
import { X, CheckCircle2, AlertTriangle, Info, ShieldAlert, Clock, Ban, Sparkles } from "lucide-react";

export function OriginBadge({ origin }: { origin?: string }) {
  const o = (origin || "REAL").toUpperCase();
  const styles: Record<string, string> = {
    REAL: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    IMPORTED: "bg-sky-500/15 text-sky-400 border-sky-500/30",
    ESTIMATED: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    GOAL: "bg-purple-500/15 text-purple-400 border-purple-500/30",
    SANDBOX: "bg-orange-500/15 text-orange-400 border-orange-500/30",
    SIMULATION: "bg-orange-500/15 text-orange-400 border-orange-500/30",
    TEST: "bg-slate-500/15 text-slate-400 border-slate-500/30",
  };
  const labels: Record<string, string> = {
    REAL: "Dado Real",
    IMPORTED: "Dado Importado",
    ESTIMATED: "Estimativa",
    GOAL: "Meta",
    SANDBOX: "Sandbox",
    SIMULATION: "Simulação",
    TEST: "Teste QA",
  };
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wide border ${
        styles[o] || styles.REAL
      }`}
    >
      {labels[o] || o}
    </span>
  );
}

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
  const cfg: Record<
    string,
    { cls: string; text: string; icon: React.ReactNode }
  > = {
    EXECUTED: {
      cls: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
      text: "Executado",
      icon: <CheckCircle2 className="w-3 h-3" aria-hidden="true" />,
    },
    RUNNING: {
      cls: "bg-indigo-500/15 text-indigo-300 border-indigo-500/30",
      text: "IA Executando",
      icon: <Sparkles className="w-3 h-3" aria-hidden="true" />,
    },
    PENDING: {
      cls: "bg-amber-500/15 text-amber-300 border-amber-500/30",
      text: "Aguardando Aprovação",
      icon: <Clock className="w-3 h-3" aria-hidden="true" />,
    },
    BLOCKED: {
      cls: "bg-purple-500/15 text-purple-300 border-purple-500/30",
      text: "Bloqueado",
      icon: <Ban className="w-3 h-3" aria-hidden="true" />,
    },
    FAILED: {
      cls: "bg-red-500/15 text-red-400 border-red-500/30",
      text: "Falhou",
      icon: <AlertTriangle className="w-3 h-3" aria-hidden="true" />,
    },
    SIMULATED: {
      cls: "bg-orange-500/15 text-orange-300 border-orange-500/30",
      text: "Simulado",
      icon: <Info className="w-3 h-3" aria-hidden="true" />,
    },
    SANDBOX: {
      cls: "bg-orange-500/15 text-orange-300 border-orange-500/30",
      text: "Sandbox",
      icon: <ShieldAlert className="w-3 h-3" aria-hidden="true" />,
    },
    NEEDS_CREDENTIALS: {
      cls: "bg-sky-500/15 text-sky-300 border-sky-500/30",
      text: "Pendente de Credenciais",
      icon: <Info className="w-3 h-3" aria-hidden="true" />,
    },
  };
  const item = cfg[status] || cfg.PENDING;
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium border ${item.cls}`}
    >
      {item.icon}
      {label || item.text}
    </span>
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
    <div className="ug-card rounded-xl border border-dashed border-slate-700/80 p-8 text-center flex flex-col items-center justify-center gap-3">
      {icon && (
        <div className="w-11 h-11 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
          {icon}
        </div>
      )}
      <div className="space-y-1 max-w-md">
        <h4 className="text-sm font-semibold text-white ug-text-primary">{title}</h4>
        <p className="text-xs text-slate-400 ug-text-muted leading-relaxed">{description}</p>
      </div>
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="mt-1 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}

export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <div className="ug-card rounded-xl p-5 space-y-3 animate-pulse" aria-busy="true" aria-label="Carregando conteúdo">
      <div className="h-3.5 w-1/3 bg-slate-800 rounded" />
      <div className="h-7 w-1/2 bg-slate-800 rounded" />
      {Array.from({ length: Math.max(1, lines - 2) }).map((_, i) => (
        <div key={i} className="h-3 w-4/5 bg-slate-800/80 rounded" />
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
      className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-[2px]"
      role="dialog"
      aria-modal="true"
      aria-label={title}
      onClick={onClose}
    >
      <div
        className={`relative w-full ${widthClass} h-full bg-[#0d1425] ug-surface border-l border-slate-800 flex flex-col shadow-2xl`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-5 py-4 border-b border-slate-800 flex items-start justify-between gap-3 shrink-0">
          <div>
            <h3 className="text-base font-bold text-white ug-text-primary">{title}</h3>
            {subtitle && <p className="text-xs text-slate-400 ug-text-muted mt-0.5">{subtitle}</p>}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar painel"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400"
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
      className="fixed bottom-5 right-5 z-50 max-w-md px-4 py-3 rounded-xl bg-indigo-600 text-white shadow-2xl border border-indigo-400/40 flex items-center gap-3 text-xs font-medium"
    >
      <CheckCircle2 className="w-4 h-4 shrink-0 text-indigo-100" aria-hidden="true" />
      <span className="flex-1 leading-snug">{message}</span>
      <button
        type="button"
        onClick={onClose}
        aria-label="Fechar notificação"
        className="p-1 rounded hover:bg-indigo-500/60 transition"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
