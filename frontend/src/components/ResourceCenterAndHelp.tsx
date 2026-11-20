"use client";

import React, { useMemo, useState } from "react";
import { ArrowRight, BookOpen, HelpCircle, Keyboard, Search, Sparkles, Star } from "lucide-react";
import { LegacyMenuId, RESOURCE_CATALOG, ResourceCatalogItem, getResourceMeta } from "@/lib/navigation";
import { Drawer, EmptyState, StatusPill } from "@/components/DesignSystem";

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

  const categories = ["Todas", "Favoritos", "Início & Trabalho", "Comercial", "Marketing", "Inteligência Artificial", "Gestão"];

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

  const statusBadge = (hint?: ResourceCatalogItem["statusHint"]) => {
    if (hint === "NEEDS_CREDENTIALS") return <StatusPill status="NEEDS_CREDENTIALS" label="Requer Credenciais" />;
    if (hint === "SANDBOX_MODE") return <StatusPill status="SANDBOX" label="Sandbox + Real" />;
    if (hint === "QUOTA_CHECK") return <StatusPill status="EXECUTED" label="Free Tier Ativo" />;
    return <StatusPill status="EXECUTED" label="Operacional" />;
  };

  return (
    <div className="space-y-6">
      <div className="ug-card rounded-2xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-white ug-text-primary">Central Completa de Recursos (Todos os Módulos)</h3>
            <p className="text-xs text-slate-400 ug-text-muted">
              Encontre rapidamente qualquer ferramenta, fixe seus favoritos e acesse seus módulos recentes.
            </p>
          </div>
          <div className="relative w-full sm:w-80">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar recurso por nome ou palavra-chave..."
              aria-label="Buscar recurso em Todos os Recursos"
              className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white"
            />
          </div>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {categories.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                category === cat
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {recentIds.length > 0 && (
          <div className="pt-2 border-t border-slate-800 flex flex-wrap items-center gap-2 text-xs">
            <span className="text-slate-400 font-medium">Últimos acessados:</span>
            {recentIds.slice(0, 6).map((rid) => {
              const meta = getResourceMeta(rid);
              if (!meta) return null;
              return (
                <button
                  key={rid}
                  type="button"
                  onClick={() => onOpenResource(rid)}
                  className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 hover:border-indigo-500/40 text-indigo-300 text-[11px]"
                >
                  {meta.name.split(" — ")[0]}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="Nenhum recurso encontrado"
          description="Nenhuma ferramenta corresponde ao filtro selecionado."
          actionLabel="Limpar filtros"
          onAction={() => {
            setSearch("");
            setCategory("Todas");
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((item) => {
            const isFav = favoriteIds.includes(item.id);
            return (
              <div key={item.id} className="ug-card rounded-2xl p-4 flex flex-col justify-between gap-3 hover:border-indigo-500/40 transition">
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[10px] font-semibold text-indigo-300">
                      {item.category}
                    </span>
                    <button
                      type="button"
                      onClick={() => onToggleFavorite(item.id)}
                      aria-label={isFav ? `Remover ${item.name} dos favoritos` : `Adicionar ${item.name} aos favoritos`}
                      aria-pressed={isFav}
                      className="p-1 rounded-lg hover:bg-slate-800 text-slate-400"
                    >
                      <Star className={`w-4 h-4 ${isFav ? "fill-amber-400 text-amber-400" : ""}`} />
                    </button>
                  </div>
                  <h4 className="text-sm font-bold text-white ug-text-primary">{item.name}</h4>
                  <p className="text-xs text-slate-400 ug-text-muted leading-relaxed">{item.description}</p>
                </div>

                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-2">
                  {statusBadge(item.statusHint)}
                  <button
                    type="button"
                    onClick={() => onOpenResource(item.id)}
                    className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold inline-flex items-center gap-1"
                  >
                    Abrir
                    <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
                  </button>
                </div>
              </div>
            );
          })}
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
      title="Central de Ajuda & Guias do Sistema"
      subtitle="Explicações práticas sem jargões técnicos"
    >
      <div className="flex gap-1.5 pb-2 border-b border-slate-800">
        {[
          { id: "contextual", label: "Esta Tela", icon: <HelpCircle className="w-3.5 h-3.5" /> },
          { id: "glossary", label: "Glossário & FAQ", icon: <BookOpen className="w-3.5 h-3.5" /> },
          { id: "shortcuts", label: "Atalhos", icon: <Keyboard className="w-3.5 h-3.5" /> },
        ].map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id as any)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold inline-flex items-center gap-1.5 ${
              tab === t.id ? "bg-indigo-600 text-white" : "bg-slate-900 border border-slate-800 text-slate-300"
            }`}
          >
            {t.icon}
            {t.label}
          </button>
        ))}
      </div>

      {tab === "contextual" && (
        <div className="space-y-4 text-xs">
          <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/30 space-y-2">
            <div className="text-[11px] font-semibold uppercase text-indigo-300">Onde você está agora</div>
            <div className="text-sm font-bold text-white">{meta?.name || "UNION GROWTH OS"}</div>
            <p className="text-slate-300 leading-relaxed">
              {meta?.description || "Workspace principal de gestão empresarial, comercial, marketing e IA."}
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="font-bold text-white flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-emerald-400" aria-hidden="true" />
              Como trabalhar melhor na plataforma
            </div>
            <ul className="space-y-1.5 text-slate-300 list-disc pl-4">
              <li>Comece pelo menu <strong>Início</strong> para ver prioridades do dia e resultados reais.</li>
              <li>Use <strong>Meu Trabalho</strong> para aprovar solicitações da IA e acompanhar alertas.</li>
              <li>Pressione <strong>Ctrl + K</strong> (ou <strong>Cmd + K</strong>) para encontrar qualquer módulo, lead ou campanha na hora.</li>
              <li>Se preferir rever a lista de primeiros passos no Início, clique no botão abaixo.</li>
            </ul>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => {
                onRestoreOnboarding();
                onClose();
              }}
              className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
            >
              Reabrir Guia Inicial (Onboarding)
            </button>
            <button
              type="button"
              onClick={() => {
                onClose();
                onOpenCommandCenter();
              }}
              className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-semibold"
            >
              Abrir Busca Global (Ctrl+K)
            </button>
          </div>
        </div>
      )}

      {tab === "glossary" && (
        <div className="space-y-3 text-xs">
          {[
            {
              term: "Política FREE_ONLY nos Motores de IA",
              desc: "Trava financeira padrão que bloqueia qualquer modelo pago (como GPT-4o, Imagen 3 ou Veo 2), garantindo que somente modelos gratuitos autorizados sejam acionados.",
            },
            {
              term: "Dado Real vs Dado Importado vs Sandbox",
              desc: "O sistema nunca mistura receitas simuladas ou testes de QA com sua receita real. Pagamentos de homologação ficam isolados como Sandbox.",
            },
            {
              term: "Níveis de Autonomia (1, 2 e 3)",
              desc: "No Nível 2 (Recomendado), os agentes preparam campanhas, análises e propostas, mas aguardam sua aprovação humana antes de ações externas ou financeiras.",
            },
            {
              term: "Publicação Assistida vs Credenciais OAuth",
              desc: "Enquanto tokens oficiais de redes sociais ou anúncios não forem conectados em Integrações, o sistema gera pacotes prontos (texto + mídia + link direto) para publicação em 1 clique.",
            },
            {
              term: "Multi-Tenant (Empresas Isoladas)",
              desc: "Cada empresa cadastrada no seletor superior possui banco lógico isolado: leads, finanças e campanhas nunca se misturam entre empresas.",
            },
          ].map((g) => (
            <div key={g.term} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
              <div className="font-bold text-indigo-300">{g.term}</div>
              <p className="text-slate-300 leading-relaxed">{g.desc}</p>
            </div>
          ))}
        </div>
      )}

      {tab === "shortcuts" && (
        <div className="space-y-2 text-xs">
          {[
            { keys: "Ctrl + K / Cmd + K", desc: "Abrir Busca Global e Central de Comandos de qualquer tela" },
            { keys: "Esc", desc: "Fechar painéis laterais, central de ajuda ou busca global" },
            { keys: "Tab / Shift + Tab", desc: "Navegar pelo teclado entre sidebar, abas e ações principais" },
            { keys: "Enter / Setas ↑ ↓", desc: "Selecionar resultados dentro da Busca Global" },
          ].map((s) => (
            <div key={s.keys} className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-3">
              <span className="text-slate-300">{s.desc}</span>
              <kbd className="px-2 py-1 rounded bg-slate-800 text-indigo-300 font-mono text-[11px] shrink-0">{s.keys}</kbd>
            </div>
          ))}
        </div>
      )}
    </Drawer>
  );
}
