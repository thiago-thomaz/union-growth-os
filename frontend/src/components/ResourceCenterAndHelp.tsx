"use client";

import React, { useMemo, useState } from "react";
import { ArrowRight, BookOpen, HelpCircle, Keyboard, Search, Sparkles, Star } from "lucide-react";
import { LegacyMenuId, RESOURCE_CATALOG, ResourceCatalogItem, getResourceMeta } from "@/lib/navigation";
import { Drawer, EmptyState, FilterTabBar, StatusPill } from "@/components/DesignSystem";

/**
 * Fase 24 — Central de Descoberta & Busca sem grade pesada de 27 cards.
 */
export function AllResourcesHub({
  favoriteIds,
  recentIds,
  onToggleFavorite,
  onOpenResource,
}: {
  favoriteIds: LegacyMenuId[];
  recentIds: LegacyMenuId[];
  onToggleFavorite: (id: LegacyMenuId) => void;
  onOpenResource: (id: LegacyMenuId) => void;
}) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string>("Todas");

  const categories = [
    "Todas",
    "Favoritos",
    "Início & Trabalho",
    "Comercial",
    "Marketing",
    "Inteligência Artificial",
    "Gestão",
  ];

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return RESOURCE_CATALOG.filter((item) => {
      if (category === "Favoritos" && !favoriteIds.includes(item.id)) return false;
      if (category !== "Todas" && category !== "Favoritos" && item.category !== category) return false;
      if (q && !`${item.name} ${item.description} ${item.category} ${item.keywords.join(" ")}`.toLowerCase().includes(q)) {
        return false;
      }
      return true;
    });
  }, [search, category, favoriteIds]);

  const grouped = useMemo(() => {
    return filtered.reduce<Record<string, ResourceCatalogItem[]>>((acc, item) => {
      acc[item.category] = acc[item.category] || [];
      acc[item.category].push(item);
      return acc;
    }, {});
  }, [filtered]);

  const statusBadge = (hint?: ResourceCatalogItem["statusHint"]) => {
    if (hint === "NEEDS_CREDENTIALS") return <StatusPill status="NEEDS_CREDENTIALS" label="Conexão Opcional" />;
    if (hint === "SANDBOX_MODE") return <StatusPill status="SANDBOX" label="Sandbox + Real" />;
    if (hint === "QUOTA_CHECK") return <StatusPill status="EXECUTED" label="Free Tier" />;
    return <StatusPill status="EXECUTED" label="Ativo" />;
  };

  return (
    <div className="space-y-5 max-w-6xl mx-auto ug-fade-in">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold tracking-tight text-[var(--ug-text-primary)]">
            Todos os recursos
          </h3>
          <p className="text-xs text-[var(--ug-text-muted)]">
            Busque qualquer ferramenta, fixe seus favoritos no menu lateral e abra em 1 clique.
          </p>
        </div>
        <div className="relative w-full sm:w-80">
          <Search className="w-3.5 h-3.5 text-[var(--ug-text-muted)] absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar recurso por nome ou assunto..."
            aria-label="Buscar recurso em Todos os Recursos"
            className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-[var(--ug-surface)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
          />
        </div>
      </div>

      <FilterTabBar
        tabs={categories.map((cat) => ({ id: cat, label: cat }))}
        activeId={category}
        onChange={setCategory}
        ariaLabel="Categorias de recursos"
      />

      {recentIds.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-[11px] text-[var(--ug-text-muted)]">Acessados recentemente:</span>
          {recentIds.slice(0, 6).map((rid) => {
            const meta = getResourceMeta(rid);
            if (!meta) return null;
            return (
              <button
                key={rid}
                type="button"
                onClick={() => onOpenResource(rid)}
                className="px-2.5 py-1 rounded-md border border-[var(--ug-border)] hover:bg-white/[0.04] text-[11px] text-[var(--ug-text-secondary)] hover:text-[var(--ug-text-primary)] transition"
              >
                {meta.name.split(" — ")[0]}
              </button>
            );
          })}
        </div>
      )}

      {filtered.length === 0 ? (
        <EmptyState
          title="Nenhum recurso encontrado"
          description="Nenhuma ferramenta corresponde ao filtro atual."
          actionLabel="Limpar filtros"
          onAction={() => {
            setSearch("");
            setCategory("Todas");
          }}
        />
      ) : (
        <div className="space-y-6">
          {Object.entries(grouped).map(([catName, catItems]) => (
            <section key={catName} className="space-y-2">
              <h4 className="text-[11px] font-semibold uppercase tracking-wider text-[var(--ug-text-muted)]">
                {catName} ({catItems.length})
              </h4>
              <div className="ug-card rounded-xl divide-y divide-white/[0.05]">
                {catItems.map((item) => {
                  const isFav = favoriteIds.includes(item.id);
                  return (
                    <div
                      key={item.id}
                      className="px-4 py-3 hover:bg-white/[0.02] transition flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                    >
                      <div className="min-w-0 space-y-0.5 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-medium text-[var(--ug-text-primary)]">{item.name}</span>
                          {statusBadge(item.statusHint)}
                        </div>
                        <p className="text-[11px] text-[var(--ug-text-muted)] truncate">{item.description}</p>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <button
                          type="button"
                          onClick={() => onToggleFavorite(item.id)}
                          aria-label={isFav ? `Remover ${item.name} dos favoritos` : `Adicionar ${item.name} aos favoritos`}
                          aria-pressed={isFav}
                          className="p-1.5 rounded-md hover:bg-white/[0.06] text-[var(--ug-text-muted)] transition"
                        >
                          <Star className={`w-3.5 h-3.5 ${isFav ? "fill-amber-400 text-amber-400" : ""}`} />
                        </button>
                        <button
                          type="button"
                          onClick={() => onOpenResource(item.id)}
                          className="px-3 py-1 rounded-md border border-[var(--ug-border)] hover:bg-indigo-600 hover:border-indigo-500 hover:text-white text-[var(--ug-text-secondary)] text-xs font-medium inline-flex items-center gap-1 transition"
                        >
                          <span>Abrir</span>
                          <ArrowRight className="w-3 h-3" aria-hidden="true" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}

export function HelpCenterDrawer({
  open,
  onClose,
  currentView,
  onRestoreOnboarding,
  onOpenCommandCenter,
}: {
  open: boolean;
  onClose: () => void;
  currentView: LegacyMenuId;
  onRestoreOnboarding: () => void;
  onOpenCommandCenter: () => void;
}) {
  const [tab, setTab] = useState<"contextual" | "glossary" | "shortcuts">("contextual");
  const meta = getResourceMeta(currentView);

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title="Central de Ajuda"
      subtitle="Explicações práticas em linguagem clara"
    >
      <FilterTabBar
        tabs={[
          { id: "contextual", label: "Esta Tela", icon: <HelpCircle className="w-3.5 h-3.5" /> },
          { id: "glossary", label: "Glossário", icon: <BookOpen className="w-3.5 h-3.5" /> },
          { id: "shortcuts", label: "Atalhos", icon: <Keyboard className="w-3.5 h-3.5" /> },
        ]}
        activeId={tab}
        onChange={(id) => setTab(id as any)}
        ariaLabel="Seções da Central de Ajuda"
      />

      {tab === "contextual" && (
        <div className="space-y-4 text-xs">
          <div className="p-4 rounded-xl bg-white/[0.03] border border-[var(--ug-border)] space-y-1.5">
            <div className="text-[11px] font-medium text-indigo-400">Tela Atual</div>
            <div className="text-sm font-semibold text-[var(--ug-text-primary)]">{meta?.name || "UNION GROWTH OS"}</div>
            <p className="text-[var(--ug-text-secondary)] leading-relaxed">
              {meta?.description || "Workspace principal de crescimento, vendas, marketing e IA."}
            </p>
          </div>

          <div className="space-y-1.5">
            <div className="font-semibold text-[var(--ug-text-primary)] flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
              Dicas rápidas
            </div>
            <ul className="space-y-1.5 text-[var(--ug-text-secondary)] list-disc pl-4">
              <li>No <strong>Início</strong> você vê o que precisa fazer hoje e pede planos ao ASK UNION.</li>
              <li>Em <strong>Meu Trabalho</strong> ficam aprovações e alertas centralizados.</li>
              <li>Use <strong>Ctrl + K</strong> para buscar qualquer tela, lead ou campanha instantaneamente.</li>
            </ul>
          </div>

          <div className="flex flex-wrap gap-2 pt-2">
            <button
              type="button"
              onClick={() => {
                onRestoreOnboarding();
                onClose();
              }}
              className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium"
            >
              Reabrir Guia Inicial (Onboarding)
            </button>
            <button
              type="button"
              onClick={() => {
                onClose();
                onOpenCommandCenter();
              }}
              className="px-3.5 py-2 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] font-medium"
            >
              Abrir Busca Global (Ctrl+K)
            </button>
          </div>
        </div>
      )}

      {tab === "glossary" && (
        <div className="ug-card rounded-xl divide-y divide-white/[0.05] text-xs">
          {[
            {
              term: "Modo Simples vs. Modo Avançado",
              desc: "O Modo Simples traduz termos técnicos e esconde ajustes profundos; você pode liberar controles técnicos em 1 clique no topo.",
            },
            {
              term: "Trava Gratuita (FREE_ONLY)",
              desc: "Impede acionamento de modelos pagos sem sua autorização, usando serviços de IA gratuitos configurados.",
            },
            {
              term: "Dado Real vs. Estimativa vs. Sandbox",
              desc: "Receitas simuladas ou testes QA nunca se misturam ao faturamento real da sua empresa.",
            },
            {
              term: "Níveis de Autonomia (1 a 3)",
              desc: "A IA prepara campanhas e análises, mas ações financeiras ou envios externos sempre passam por aprovação.",
            },
            {
              term: "Conectar Ferramenta Externa (OAuth)",
              desc: "Enquanto contas externas não estiverem conectadas, a plataforma gera pacotes prontos em 1 clique.",
            },
          ].map((g) => (
            <div key={g.term} className="p-3.5 space-y-1">
              <div className="font-semibold text-indigo-300">{g.term}</div>
              <p className="text-[var(--ug-text-secondary)] leading-relaxed">{g.desc}</p>
            </div>
          ))}
        </div>
      )}

      {tab === "shortcuts" && (
        <div className="ug-card rounded-xl divide-y divide-white/[0.05] text-xs">
          {[
            { keys: "Ctrl + K / Cmd + K", desc: "Abrir Busca Global e Comandos" },
            { keys: "Esc", desc: "Fechar painéis laterais ou busca" },
            { keys: "Tab / Shift + Tab", desc: "Navegar pelo teclado entre controles" },
            { keys: "Enter / ↑ ↓", desc: "Selecionar item na Busca Global" },
          ].map((s) => (
            <div key={s.keys} className="px-4 py-3 flex items-center justify-between gap-3">
              <span className="text-[var(--ug-text-secondary)]">{s.desc}</span>
              <kbd className="px-2 py-0.5 rounded bg-white/[0.06] text-indigo-300 font-mono text-[11px] shrink-0">
                {s.keys}
              </kbd>
            </div>
          ))}
        </div>
      )}
    </Drawer>
  );
}
