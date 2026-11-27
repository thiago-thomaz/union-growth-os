"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { Search, ArrowRight, Command, Sparkles, Users, Megaphone, FileText, ShieldCheck, Plug, X } from "lucide-react";
import { LegacyMenuId, RESOURCE_CATALOG } from "@/lib/navigation";

interface SearchResultItem {
  id: string;
  group: string;
  title: string;
  subtitle: string;
  targetMenu: LegacyMenuId;
  badge?: string;
}

export function CommandCenter({
  open,
  onClose,
  onNavigate,
  crmData,
  marketingData,
  mbDashboard,
  approvalsData,
  integrationsData,
  contentFactoryItems,
}: {
  open: boolean;
  onClose: () => void;
  onNavigate: (viewId: LegacyMenuId) => void;
  crmData: any;
  marketingData: any;
  mbDashboard: any;
  approvalsData: any[];
  integrationsData: any[];
  contentFactoryItems: any[];
}) {
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (open) {
      setQuery("");
      setActiveIndex(0);
      setTimeout(() => inputRef.current?.focus(), 40);
    }
  }, [open]);

  const results = useMemo<SearchResultItem[]>(() => {
    const q = query.trim().toLowerCase();
    const out: SearchResultItem[] = [];

    const quickActions: SearchResultItem[] = [
      { id: "act-lead", group: "Ações Rápidas", title: "Cadastrar Novo Lead no CRM", subtitle: "Comercial → Leads & CRM", targetMenu: "crm", badge: "Ação" },
      { id: "act-camp", group: "Ações Rápidas", title: "Criar Nova Campanha de Marketing", subtitle: "Marketing → Campanhas", targetMenu: "marketing", badge: "Ação" },
      { id: "act-seo", group: "Ações Rápidas", title: "Executar Auditoria Técnica SEO", subtitle: "Marketing → SEO & Artigos", targetMenu: "seo", badge: "Ação" },
      { id: "act-gemini", group: "Ações Rápidas", title: "Configurar ou Testar Motor Google Gemini", subtitle: "IA → Modelos & Provedores", targetMenu: "ai_engines", badge: "IA" },
      { id: "act-prop", group: "Ações Rápidas", title: "Gerar Proposta Comercial ou Ver PDF", subtitle: "Comercial → Propostas & 3 Unidades", targetMenu: "multibusiness", badge: "Comercial" },
      { id: "act-rep", group: "Ações Rápidas", title: "Ver Relatório Executivo & Backup", subtitle: "Gestão → Relatórios", targetMenu: "reports", badge: "Gestão" },
    ];
    for (const act of quickActions) {
      if (!q || act.title.toLowerCase().includes(q) || act.subtitle.toLowerCase().includes(q)) {
        out.push(act);
      }
    }

    for (const mod of RESOURCE_CATALOG) {
      const hay = `${mod.name} ${mod.description} ${mod.category} ${mod.keywords.join(" ")}`.toLowerCase();
      if (!q || hay.includes(q)) {
        out.push({
          id: `mod-${mod.id}`,
          group: "Recursos",
          title: mod.name,
          subtitle: `${mod.category} • ${mod.description}`,
          targetMenu: mod.id,
          badge: mod.category.split(" ")[0],
        });
      }
    }

    for (const l of (crmData?.leads || []).slice(0, 40)) {
      const hay = `${l.full_name} ${l.company_name || ""} ${l.email || ""}`.toLowerCase();
      if (q && hay.includes(q)) {
        out.push({
          id: `lead-${l.id}`,
          group: "Leads no CRM",
          title: `${l.full_name} (${l.company_name || "Contato Direto"})`,
          subtitle: `${l.email} • Estágio: ${l.pipeline_stage} • Score ${l.lead_score}/100`,
          targetMenu: "crm",
          badge: l.data_origin === "TEST" ? "Teste QA" : "Lead",
        });
      }
    }

    for (const c of (marketingData?.campaigns || []).slice(0, 40)) {
      const hay = `${c.name} ${c.channel || ""} ${c.campaign_type || ""}`.toLowerCase();
      if (q && hay.includes(q)) {
        out.push({
          id: `camp-${c.id}`,
          group: "Campanhas",
          title: c.name,
          subtitle: `Canal: ${c.channel} • Tipo: ${c.campaign_type}`,
          targetMenu: "marketing",
          badge: "Campanha",
        });
      }
    }

    for (const p of (mbDashboard?.proposals || []).slice(0, 25)) {
      const hay = `${p.proposal_number} ${p.client_company} ${p.client_name} ${p.status}`.toLowerCase();
      if (q && hay.includes(q)) {
        out.push({
          id: `prop-${p.id}`,
          group: "Propostas Comerciais",
          title: `${p.proposal_number} — ${p.client_company}`,
          subtitle: `Setup R$ ${p.setup_price_brl} • Status: ${p.status}`,
          targetMenu: "multibusiness",
          badge: "Proposta",
        });
      }
    }

    for (const cf of (contentFactoryItems || []).slice(0, 30)) {
      const hay = `${cf.title || ""} ${cf.channel || ""} ${cf.theme || ""}`.toLowerCase();
      if (q && hay.includes(q)) {
        out.push({
          id: `cf-${cf.id}`,
          group: "Conteúdos",
          title: cf.title || cf.theme || `Peça #${cf.id}`,
          subtitle: `Canal: ${cf.channel || "Multi"} • Status: ${cf.status || "READY"}`,
          targetMenu: "content_factory",
          badge: "Conteúdo",
        });
      }
    }

    for (const ap of (approvalsData || []).slice(0, 20)) {
      if (q && `${ap.title} ${ap.action_type}`.toLowerCase().includes(q)) {
        out.push({
          id: `ap-${ap.id}`,
          group: "Aprovações",
          title: ap.title,
          subtitle: `Agente: ${ap.agent_id} • Status: ${ap.status}`,
          targetMenu: "approvals",
          badge: ap.status,
        });
      }
    }

    for (const intg of integrationsData || []) {
      if (q && `${intg.provider_name} ${intg.provider_key}`.toLowerCase().includes(q)) {
        out.push({
          id: `intg-${intg.provider_key}`,
          group: "Integrações",
          title: intg.provider_name,
          subtitle: `Status: ${intg.status}`,
          targetMenu: "integrations",
          badge: intg.status === "CONNECTED" ? "Conectado" : "Configurar",
        });
      }
    }

    return out.slice(0, q ? 24 : 14);
  }, [query, crmData, marketingData, mbDashboard, contentFactoryItems, approvalsData, integrationsData]);

  useEffect(() => {
    setActiveIndex(0);
  }, [query]);

  if (!open) return null;

  const grouped = results.reduce<Record<string, SearchResultItem[]>>((acc, item) => {
    acc[item.group] = acc[item.group] || [];
    acc[item.group].push(item);
    return acc;
  }, {});

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      e.preventDefault();
      onClose();
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((prev) => Math.min(results.length - 1, prev + 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) => Math.max(0, prev - 1));
    } else if (e.key === "Enter" && results[activeIndex]) {
      e.preventDefault();
      onNavigate(results[activeIndex].targetMenu);
      onClose();
    }
  };

  const groupIcon = (grp: string) => {
    if (grp.includes("Leads")) return <Users className="w-3.5 h-3.5 text-emerald-400" />;
    if (grp.includes("Campanha")) return <Megaphone className="w-3.5 h-3.5 text-purple-400" />;
    if (grp.includes("Proposta") || grp.includes("Conteúdo")) return <FileText className="w-3.5 h-3.5 text-sky-400" />;
    if (grp.includes("Aprova")) return <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />;
    if (grp.includes("Integra")) return <Plug className="w-3.5 h-3.5 text-indigo-400" />;
    return <Sparkles className="w-3.5 h-3.5 text-indigo-400" />;
  };

  let flatCursor = -1;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh] px-4 bg-black/65 backdrop-blur-[2px]"
      role="dialog"
      aria-modal="true"
      aria-label="Busca Global e Central de Comandos"
      onClick={onClose}
    >
      <div
        className="w-full max-w-2xl ug-surface border border-[var(--ug-border)] rounded-2xl shadow-2xl overflow-hidden ug-fade-in"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--ug-border)]">
          <Search className="w-4 h-4 text-indigo-400 shrink-0" aria-hidden="true" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar recursos, ações, leads, campanhas ou configurações..."
            aria-label="Campo de busca global"
            className="flex-1 bg-transparent text-sm text-[var(--ug-text-primary)] placeholder:text-[var(--ug-text-muted)] focus:outline-none border-none"
          />
          <kbd className="hidden sm:inline-flex items-center px-2 py-0.5 rounded bg-white/[0.06] text-[10px] font-mono text-[var(--ug-text-muted)]">
            ESC
          </kbd>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar busca global"
            className="p-1 rounded-lg text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)] hover:bg-white/[0.06]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="max-h-[60vh] overflow-y-auto p-3 space-y-4">
          {results.length === 0 ? (
            <div className="py-10 text-center space-y-1">
              <p className="text-sm font-medium text-[var(--ug-text-primary)]">
                Nenhum resultado para &ldquo;{query}&rdquo;
              </p>
              <p className="text-xs text-[var(--ug-text-muted)]">
                Tente buscar por &ldquo;Campanha&rdquo;, &ldquo;Lead&rdquo;, &ldquo;Gemini&rdquo;, &ldquo;SEO&rdquo; ou &ldquo;Financeiro&rdquo;.
              </p>
            </div>
          ) : (
            Object.entries(grouped).map(([grp, items]) => (
              <div key={grp} className="space-y-1">
                <div className="px-2 flex items-center gap-1.5 text-[11px] font-medium text-[var(--ug-text-muted)]">
                  {groupIcon(grp)}
                  <span>{grp}</span>
                </div>
                {items.map((item) => {
                  flatCursor += 1;
                  const idx = flatCursor;
                  const selected = idx === activeIndex;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onMouseEnter={() => setActiveIndex(idx)}
                      onClick={() => {
                        onNavigate(item.targetMenu);
                        onClose();
                      }}
                      className={`w-full flex items-center justify-between gap-3 px-3 py-2 rounded-lg text-left transition ${
                        selected ? "bg-indigo-600/15" : "hover:bg-white/[0.04]"
                      }`}
                    >
                      <div className="min-w-0">
                        <div className="text-xs font-medium text-[var(--ug-text-primary)] truncate">{item.title}</div>
                        <div className="text-[11px] text-[var(--ug-text-muted)] truncate">{item.subtitle}</div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {item.badge && (
                          <span className="px-2 py-0.5 rounded bg-white/[0.06] text-[10px] text-[var(--ug-text-secondary)]">
                            {item.badge}
                          </span>
                        )}
                        <ArrowRight className="w-3.5 h-3.5 text-[var(--ug-text-muted)]" aria-hidden="true" />
                      </div>
                    </button>
                  );
                })}
              </div>
            ))
          )}
        </div>

        <div className="px-4 py-2.5 border-t border-[var(--ug-border)] flex items-center justify-between text-[11px] text-[var(--ug-text-muted)]">
          <div className="flex items-center gap-2">
            <Command className="w-3.5 h-3.5" aria-hidden="true" />
            <span>↑ ↓ para navegar • Enter para abrir</span>
          </div>
          <button
            type="button"
            onClick={() => {
              onNavigate("all_resources");
              onClose();
            }}
            className="text-indigo-400 hover:underline font-medium"
          >
            Todos os recursos →
          </button>
        </div>
      </div>
    </div>
  );
}
