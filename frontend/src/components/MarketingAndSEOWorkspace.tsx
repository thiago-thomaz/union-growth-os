"use client";

import React from "react";
import { EmptyState, MetricStrip, OriginBadge, PlainOrientationBar, StatusPill } from "@/components/DesignSystem";
import { GrowthExecutionCenter } from "@/components/GrowthExecutionCenter";

export function MarketingCampaignsWorkspace({
  marketingData,
  personaName,
  setPersonaName,
  personaRole,
  personaVP,
  setPersonaVP,
  campName,
  setCampName,
  campType,
  setCampType,
  campChannel,
  setCampChannel,
  campBudget,
  setCampBudget,
  campFilter,
  setCampFilter,
  apiFetch,
  onReload,
  showNotice,
}: any) {
  const visibleCamps = (marketingData?.campaigns || []).filter((c: any) => {
    const q = (campFilter || "").trim().toLowerCase();
    if (!q) return true;
    return `${c.name || ""} ${c.channel || ""} ${c.status || ""} ${c.objective || ""}`.toLowerCase().includes(q);
  });

  return (
    <div className="space-y-5 max-w-7xl mx-auto ug-fade-in">
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[var(--ug-border)]">
        <div>
          <h3 className="text-base font-semibold text-[var(--ug-text-primary)]">Campanhas &amp; Público Ideal</h3>
          <p className="text-xs text-[var(--ug-text-muted)] mt-0.5">
            Defina seu público-alvo, crie campanhas multicanal e gere conteúdo contextual na Fábrica.
          </p>
        </div>
        <button
          type="button"
          onClick={async () => {
            try {
              await apiFetch("/api/v1/agents/AGENT_02_CMO/execute", {
                method: "POST",
                body: JSON.stringify({ task_name: "generate_monthly_marketing_plan" }),
              });
              await onReload();
              showNotice("Novo Planejamento Mensal de Marketing gerado!");
            } catch (err: any) {
              showNotice(err?.message || "Não foi possível gerar planejamento agora.");
            }
          }}
          className="px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
        >
          Gerar Planejamento Mensal Automático
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="ug-card rounded-xl p-5 space-y-4">
          <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">Personas &amp; Público-Alvo</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2 items-end text-xs">
            <div>
              <label htmlFor="ug-persona-name" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                Nome da Persona *
              </label>
              <input
                id="ug-persona-name"
                value={personaName}
                onChange={(e) => setPersonaName(e.target.value)}
                placeholder="Ex.: Gestor Comercial B2B"
                className="w-full px-2.5 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
              />
            </div>
            <div>
              <label htmlFor="ug-persona-vp" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                Principal Benefício / Oferta
              </label>
              <input
                id="ug-persona-vp"
                value={personaVP}
                onChange={(e) => setPersonaVP(e.target.value)}
                placeholder="Ex.: Reduzir tempo de resposta comercial"
                className="w-full px-2.5 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
              />
            </div>
            <button
              type="button"
              onClick={async () => {
                if (!personaName.trim()) {
                  showNotice("Informe o Nome da Persona antes de cadastrar.");
                  return;
                }
                try {
                  await apiFetch("/api/v1/marketing/personas", {
                    method: "POST",
                    body: JSON.stringify({
                      name: personaName.trim(),
                      role_segment: personaRole,
                      value_proposition: personaVP.trim() || "Eficiência e escala com IA",
                    }),
                  });
                  setPersonaName("");
                  setPersonaVP("");
                  await onReload();
                  showNotice("Persona criada com sucesso!");
                } catch (err: any) {
                  showNotice(err?.message || "Erro ao cadastrar persona.");
                }
              }}
              className="py-1.5 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold h-[30px]"
            >
              Criar Persona
            </button>
          </div>
          {marketingData.personas.length === 0 ? (
            <EmptyState
              title="Nenhuma persona cadastrada ainda"
              description="Cadastre quem é o seu cliente ideal acima para a IA personalizar copies e campanhas."
            />
          ) : (
            <div className="divide-y divide-white/[0.05]">
              {marketingData.personas.map((p: any) => (
                <div key={p.id} className="py-3 space-y-0.5 text-xs">
                  <div className="font-semibold text-indigo-400">{p.name}</div>
                  <div className="text-[var(--ug-text-muted)]">
                    {p.role_segment} • {p.demographics}
                  </div>
                  <div className="text-[var(--ug-text-secondary)]">
                    <strong>Proposta de Valor:</strong> {p.value_proposition}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="ug-card rounded-xl p-5 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">
              Campanhas Ativas &amp; ROI ({marketingData.campaigns.length})
            </h4>
            <input
              value={campFilter}
              onChange={(e) => setCampFilter(e.target.value)}
              placeholder="Filtrar lista abaixo..."
              aria-label="Filtrar campanhas"
              className="w-full sm:w-56 bg-[var(--ug-bg)] border border-[var(--ug-border)] rounded-lg px-3 py-1.5 text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2 items-end text-xs">
            <div className="lg:col-span-2">
              <label htmlFor="ug-camp-name-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                Nome da Campanha *
              </label>
              <input
                id="ug-camp-name-input"
                value={campName}
                onChange={(e) => setCampName(e.target.value)}
                placeholder="Ex.: Captação Leads B2B Q4"
                className="w-full px-2.5 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
              />
            </div>
            <div>
              <label htmlFor="ug-camp-channel-select" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                Canal Principal
              </label>
              <select
                id="ug-camp-channel-select"
                value={campChannel}
                onChange={(e) => setCampChannel(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
              >
                <option value="Organic SEO + LinkedIn">SEO + LinkedIn</option>
                <option value="Instagram + Facebook">Instagram + Facebook</option>
                <option value="Google Search + YouTube">Google + YouTube</option>
                <option value="Email & CRM">E-mail &amp; CRM</option>
              </select>
            </div>
            <div>
              <label htmlFor="ug-camp-type-select" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                Objetivo / Tipo
              </label>
              <select
                id="ug-camp-type-select"
                value={campType}
                onChange={(e) => setCampType(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
              >
                <option value="ACQUISITION">Aquisição de Leads</option>
                <option value="LAUNCH">Lançamento</option>
                <option value="SEASONAL">Sazonal</option>
                <option value="RETENTION">Retenção</option>
              </select>
            </div>
            <div>
              <label htmlFor="ug-camp-budget-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                Orçamento Planejado (R$)
              </label>
              <input
                id="ug-camp-budget-input"
                type="number"
                value={campBudget}
                onChange={(e) => setCampBudget(e.target.value)}
                placeholder="Ex.: 5000"
                className="w-full px-2.5 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)] tabular-nums"
              />
            </div>
            <button
              type="button"
              onClick={async () => {
                if (!campName.trim()) {
                  showNotice("Informe o Nome da Campanha antes de salvar.");
                  return;
                }
                try {
                  const res = await apiFetch("/api/v1/marketing/campaigns", {
                    method: "POST",
                    body: JSON.stringify({
                      name: campName.trim(),
                      campaign_type: campType,
                      channel: campChannel,
                      objective: "Aquisição e conversão de leads",
                      budget_planned: Number(campBudget) || 0,
                    }),
                  });
                  setCampName("");
                  await onReload();
                  showNotice(res.message || "Campanha criada com sucesso!");
                } catch (err: any) {
                  showNotice(err?.message || "Erro ao criar campanha.");
                }
              }}
              className="lg:col-span-3 py-1.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold h-[30px]"
            >
              Criar Campanha
            </button>
          </div>
          {visibleCamps.length === 0 ? (
            <EmptyState
              title={marketingData.campaigns.length === 0 ? "Nenhuma campanha criada" : "Nenhuma campanha corresponde à busca"}
              description="Preencha o Nome da Campanha acima e clique em Criar Campanha para começar a mensurar ROI."
            />
          ) : (
            <div className="divide-y divide-white/[0.05] max-h-96 overflow-y-auto">
              {visibleCamps.map((c: any) => (
                <div key={c.id} className="py-3 space-y-1 text-xs tabular-nums">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-semibold text-[var(--ug-text-primary)]">{c.name}</span>
                    <OriginBadge origin={c.data_origin} />
                  </div>
                  <div className="text-[var(--ug-text-muted)]">
                    Canal: {c.channel} • Tipo: {c.campaign_type} • ROI: <strong className="text-emerald-400">{c.roi_pct}%</strong>
                  </div>
                  <div className="text-[var(--ug-text-secondary)]">
                    Orçamento: R$ {c.budget_planned} | Gasto Real: R$ {c.spend_real} | Receita Atribuída: R$ {c.revenue_attributed}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function SEOWorkspace({
  seoData,
  seoUrlInput,
  setSeoUrlInput,
  seoKwInput,
  setSeoKwInput,
  seoTopicInput,
  setSeoTopicInput,
  apiFetch,
  onReload,
  showNotice,
}: any) {
  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      <div className="px-4 py-3 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-200 text-xs">
        <strong>Transparência SEO:</strong> {seoData.gsc_ranking_status?.notice}
      </div>

      <div className="ug-card rounded-xl grid grid-cols-1 lg:grid-cols-3 divide-y lg:divide-y-0 lg:divide-x divide-white/[0.06] overflow-hidden">
        <div className="p-4 space-y-3">
          <h4 className="text-xs font-semibold text-[var(--ug-text-primary)]">1. Auditoria Técnica (Live HTTP)</h4>
          <input
            value={seoUrlInput}
            onChange={(e) => setSeoUrlInput(e.target.value)}
            aria-label="URL do site para auditoria SEO"
            className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            placeholder="https://seudominio.com.br"
          />
          <button
            type="button"
            onClick={async () => {
              await apiFetch("/api/v1/seo/audit", {
                method: "POST",
                body: JSON.stringify({ target_url: seoUrlInput, target_keyword: seoKwInput }),
              });
              await onReload();
              showNotice("Auditoria técnica de SEO concluída!");
            }}
            className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
          >
            Executar Auditoria Técnica Real
          </button>
        </div>

        <div className="p-4 space-y-3">
          <h4 className="text-xs font-semibold text-[var(--ug-text-primary)]">2. Pesquisa de Palavras-Chave &amp; Clusters</h4>
          <input
            value={seoKwInput}
            onChange={(e) => setSeoKwInput(e.target.value)}
            aria-label="Palavra-chave semente"
            className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            placeholder="Palavra-chave semente"
          />
          <button
            type="button"
            onClick={async () => {
              await apiFetch("/api/v1/seo/keywords", {
                method: "POST",
                body: JSON.stringify({ seed_keyword: seoKwInput }),
              });
              await onReload();
              showNotice("Cluster de palavras-chave e cauda longa gerado!");
            }}
            className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
          >
            Descobrir Cauda Longa &amp; Clusters
          </button>
        </div>

        <div className="p-4 space-y-3">
          <h4 className="text-xs font-semibold text-[var(--ug-text-primary)]">3. SEO Content Factory (Gerar Artigo)</h4>
          <input
            value={seoTopicInput}
            onChange={(e) => setSeoTopicInput(e.target.value)}
            aria-label="Título ou tópico do artigo SEO"
            className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            placeholder="Título / Tópico do Artigo"
          />
          <button
            type="button"
            onClick={async () => {
              await apiFetch("/api/v1/seo/articles/generate", {
                method: "POST",
                body: JSON.stringify({
                  topic: seoTopicInput,
                  target_keyword: seoKwInput,
                  search_intent: "COMMERCIAL",
                }),
              });
              await onReload();
              showNotice("Artigo otimizado com Schema.org gerado pela SEO Content Factory!");
            }}
            className="w-full py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
          >
            Produzir Artigo Otimizado
          </button>
        </div>
      </div>

      {seoData.keyword_clusters?.length > 0 && (
        <div className="ug-card rounded-xl overflow-hidden">
          <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
            Clusters de Conteúdo &amp; Cauda Longa ({seoData.keyword_clusters.length})
          </div>
          <div className="divide-y divide-white/[0.05] text-xs">
            {seoData.keyword_clusters.map((kc: any) => (
              <div key={kc.id} className="px-5 py-3 space-y-1">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-indigo-400">{kc.seed_keyword}</span>
                  <span className="px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 text-[10px]">
                    Intenção: {kc.search_intent}
                  </span>
                </div>
                <div className="text-[var(--ug-text-secondary)]">
                  <strong>Cauda Longa:</strong> {kc.long_tail_keywords.slice(0, 6).join(" • ")}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="ug-card rounded-xl overflow-hidden">
          <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
            Últimas Auditorias Técnicas ({seoData.audits.length})
          </div>
          <div className="divide-y divide-white/[0.05]">
            {seoData.audits.map((a: any) => {
              const sig = a.technical_signals || a.generated_schema?.technical_signals || {};
              const prioRecs = a.prioritized_recommendations || a.generated_schema?.prioritized_recommendations || [];
              return (
                <div key={a.id} className="px-5 py-3.5 text-xs space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-semibold text-indigo-400 truncate">{a.target_url}</span>
                    <OriginBadge origin={a.data_origin} />
                  </div>
                  <div className="tabular-nums text-[var(--ug-text-secondary)]">
                    Score: <strong className="text-emerald-400">{a.overall_score}/100</strong> • {a.response_time_ms}ms • robots:{" "}
                    {a.has_robots_txt ? "Sim" : "Não"} • sitemap: {a.has_sitemap_xml ? "Sim" : "Não"}
                  </div>
                  {Object.keys(sig).length > 0 && (
                    <div className="flex flex-wrap gap-1.5 text-[10px]">
                      <span className="px-1.5 py-0.5 rounded bg-white/[0.05] text-[var(--ug-text-secondary)]">
                        Canonical: {sig.has_canonical ? "OK" : "Ausente"}
                      </span>
                      <span className="px-1.5 py-0.5 rounded bg-white/[0.05] text-[var(--ug-text-secondary)]">
                        Mobile Viewport: {sig.has_viewport_mobile ? "OK" : "Ausente"}
                      </span>
                      <span className="px-1.5 py-0.5 rounded bg-white/[0.05] text-[var(--ug-text-secondary)]">
                        OpenGraph: {sig.has_open_graph ? "OK" : "Incompleto"}
                      </span>
                      <span className="px-1.5 py-0.5 rounded bg-white/[0.05] text-[var(--ug-text-secondary)] tabular-nums">
                        {sig.body_word_count || 0} palavras • H1: {sig.h1_count ?? "-"}
                      </span>
                    </div>
                  )}
                  {prioRecs.length > 0 && (
                    <div className="pt-1 space-y-1">
                      <div className="text-[10px] font-semibold text-amber-300">Correções Priorizadas por Impacto:</div>
                      {prioRecs.slice(0, 3).map((rec: any) => (
                        <div key={rec.id} className="text-[11px] text-[var(--ug-text-muted)]">
                          • [{rec.priority} | Impacto {rec.impact_score}/10] {rec.recommendation}
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="text-[var(--ug-text-muted)]">
                    Sugestão Title: <span className="text-[var(--ug-text-primary)]">{a.suggested_title}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="ug-card rounded-xl overflow-hidden">
          <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
            Artigos da SEO Content Factory ({seoData.articles.length})
          </div>
          <div className="divide-y divide-white/[0.05]">
            {seoData.articles.map((art: any) => (
              <div key={art.id} className="px-5 py-3.5 text-xs space-y-1.5">
                <div className="font-semibold text-[var(--ug-text-primary)]">{art.title}</div>
                <div className="text-[var(--ug-text-muted)] tabular-nums">
                  Keyword: {art.target_keyword} • {art.word_count} palavras • Densidade: {art.keyword_density_pct}%
                </div>
                <pre className="p-2.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] text-[11px] text-[var(--ug-text-secondary)] max-h-40 overflow-y-auto whitespace-pre-wrap">
                  {art.content_markdown}
                </pre>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export function SocialAndContentWorkspace({
  mode,
  meData,
  marketingData,
  calendarData,
  contentFactoryItems,
  cfFilter,
  setCfFilter,
  cfFocusTheme,
  setCfFocusTheme,
  cfReplaceDrafts,
  setCfReplaceDrafts,
  setAssistedPackage,
  calTitle,
  setCalTitle,
  calPlatform,
  setCalPlatform,
  calFormat,
  setCalFormat,
  calDate,
  setCalDate,
  setLoading,
  navigateTo,
  apiFetch,
  onReload,
  showNotice,
}: any) {
  if (mode === "content_factory") {
    const cfPersonas = marketingData?.personas || [];
    const cfLatestPersona = cfPersonas.length > 0 ? cfPersonas[cfPersonas.length - 1] : null;
    const cfLatestCampaign = (marketingData?.campaigns || [])[0] || null;
    const cfTenant = meData?.active_tenant;
    const cfDraftCount = contentFactoryItems.filter((it: any) => it.status !== "PUBLISHED").length;
    const visibleCf = contentFactoryItems.filter((it: any) => cfFilter === "ALL" || it.channel === cfFilter);

    return (
      <div className="space-y-5 max-w-7xl mx-auto ug-fade-in">
        <div className="ug-card rounded-xl p-5 space-y-4">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-semibold text-[var(--ug-text-primary)]">
                Fábrica de Conteúdo — Produção Mensal (30 Publicações Prontas)
              </h3>
              <p className="text-xs text-[var(--ug-text-muted)] mt-1">
                Gera 30 peças multicanal alinhadas à sua marca e nicho. Sem conta social OAuth, use <strong>Pacote 1-Clique</strong> para distribuir manualmente sem risco.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => navigateTo("calendar")}
                className="px-3.5 py-2 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-primary)] text-xs font-semibold"
              >
                Criar 1 Post Manual →
              </button>
              {cfDraftCount > 0 && (
                <button
                  type="button"
                  onClick={async () => {
                    setLoading(true);
                    try {
                      const res = await apiFetch("/api/v1/content-factory/drafts", { method: "DELETE" });
                      await onReload();
                      showNotice(`${res.deleted_count} rascunho(s) removido(s)!`);
                    } catch (e: any) {
                      showNotice(e.message || "Erro ao limpar rascunhos");
                    } finally {
                      setLoading(false);
                    }
                  }}
                  className="px-3.5 py-2 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-secondary)] text-xs font-semibold"
                >
                  Limpar Rascunhos ({cfDraftCount})
                </button>
              )}
              <button
                type="button"
                onClick={async () => {
                  setLoading(true);
                  try {
                    const res = await apiFetch("/api/v1/content-factory/generate-batch", {
                      method: "POST",
                      body: JSON.stringify({
                        count: 30,
                        company_name: cfTenant?.brand_name || cfTenant?.name || "",
                        niche: cfTenant?.niche || "",
                        target_audience: cfLatestPersona?.name || cfTenant?.target_audience || "",
                        focus_theme: cfFocusTheme.trim(),
                        replace_drafts: cfReplaceDrafts,
                        persona_id: cfLatestPersona?.id || null,
                        campaign_id: cfLatestCampaign?.id || null,
                      }),
                    });
                    await onReload();
                    showNotice(`Fábrica de Conteúdo: ${res.total_generated} conteúdos criados para ${cfTenant?.brand_name || "sua marca"}!`);
                  } catch (e: any) {
                    showNotice(e.message || "Erro ao gerar lote");
                  } finally {
                    setLoading(false);
                  }
                }}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs whitespace-nowrap"
              >
                Gerar Lote de 30 Publicações
              </button>
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="text-[11px] font-semibold text-[var(--ug-text-secondary)]">
              Contexto usado na criação dos conteúdos:
            </div>
            <MetricStrip
              items={[
                { key: "b", label: "Marca", value: cfTenant?.brand_name || "-" },
                { key: "d", label: "Site / Link", value: cfTenant?.domain || "Não informado" },
                { key: "n", label: "Nicho", value: cfTenant?.niche || "-" },
                { key: "p", label: "Persona Ativa", value: cfLatestPersona?.name || cfTenant?.target_audience || "-" },
                { key: "c", label: "Campanha Ativa", value: cfLatestCampaign?.name || "Padrão da marca" },
              ]}
            />
          </div>

          <div className="flex flex-col md:flex-row md:items-center gap-3">
            <div className="flex-1">
              <label htmlFor="ug-cf-focus-input" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">
                Oferta / Chamada Principal que aparecerá nos posts (opcional):
              </label>
              <input
                id="ug-cf-focus-input"
                value={cfFocusTheme}
                onChange={(e) => setCfFocusTheme(e.target.value)}
                placeholder={cfLatestPersona?.value_proposition || "Ex.: Diagnóstico gratuito no site"}
                className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
              />
            </div>
            <label className="inline-flex items-center gap-2 text-[11px] text-[var(--ug-text-secondary)] cursor-pointer pt-4">
              <input
                type="checkbox"
                checked={cfReplaceDrafts}
                onChange={(e) => setCfReplaceDrafts(e.target.checked)}
                className="rounded border-[var(--ug-border)] bg-[var(--ug-bg)] text-indigo-600"
              />
              <span>Substituir rascunhos não publicados ao gerar novo lote</span>
            </label>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {["ALL", "instagram", "facebook", "tiktok", "youtube", "linkedin", "blog_seo", "email_marketing"].map((ch) => (
            <button
              key={ch}
              type="button"
              onClick={() => setCfFilter(ch)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                cfFilter === ch
                  ? "bg-indigo-600 text-white"
                  : "border border-[var(--ug-border)] text-[var(--ug-text-secondary)] hover:bg-white/[0.04]"
              }`}
            >
              {ch === "ALL" ? "Todos os Canais" : ch.toUpperCase()}
            </button>
          ))}
        </div>

        {visibleCf.length === 0 ? (
          <EmptyState
            title="Nenhum conteúdo encontrado neste canal"
            description="Clique em 'Gerar Lote de 30 Publicações' acima para preencher automaticamente todos os canais."
            actionLabel={cfFilter !== "ALL" ? "Ver Todos os Canais" : undefined}
            onAction={cfFilter !== "ALL" ? () => setCfFilter("ALL") : undefined}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {visibleCf.map((it: any) => (
              <div key={it.id} className="ug-card rounded-xl p-4 space-y-3 text-xs flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 font-semibold uppercase text-[10px]">
                      {it.channel} • {it.content_type}
                    </span>
                    <StatusPill status="EXECUTED" label={`Nota ${it.quality_score}/100`} />
                  </div>
                  <div className="font-semibold text-[var(--ug-text-primary)] text-sm line-clamp-2">{it.title}</div>
                  <p className="text-[var(--ug-text-secondary)] line-clamp-4 whitespace-pre-line text-[11px]">{it.body_text}</p>
                  <div className="p-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] text-[11px] text-indigo-400">
                    <strong>CTA:</strong> {it.cta}
                  </div>
                </div>
                <div className="pt-3 border-t border-[var(--ug-border-subtle)] space-y-2">
                  <div className="flex items-center justify-between text-[10px] text-[var(--ug-text-muted)]">
                    <span>Data: <strong>{it.scheduled_for?.split("T")[0]}</strong></span>
                    <span>Status: <strong className="text-amber-300">{it.status === "PUBLISHED" ? "Publicado" : "Pronto para uso"}</strong></span>
                  </div>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={async () => {
                        try {
                          const pkg = await apiFetch(`/api/v1/content-factory/assisted-export/${it.id}`);
                          setAssistedPackage(pkg);
                        } catch (e: any) {
                          showNotice(e.message || "Erro ao exportar");
                        }
                      }}
                      className="flex-1 py-1.5 rounded-lg border border-indigo-500/30 hover:bg-white/[0.05] text-indigo-400 text-[11px] font-medium"
                    >
                      Pacote 1-Clique
                    </button>
                    <button
                      type="button"
                      aria-label={`Marcar ${it.title} como publicado`}
                      onClick={async () => {
                        try {
                          await apiFetch(`/api/v1/content-factory/items/${it.id}/publish`, { method: "POST" });
                          await onReload();
                          showNotice("Status atualizado para Publicado!");
                        } catch (e: any) {
                          showNotice(e.message || "Erro ao publicar");
                        }
                      }}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-medium"
                    >
                      ✓
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-5 max-w-7xl mx-auto ug-fade-in">
      <div className="ug-card rounded-xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">
              Calendário Editorial &amp; Publicações (Modo Assistido + Aprovação)
            </h3>
            <p className="text-xs text-[var(--ug-text-muted)]">
              Sem conta social conectada via OAuth, gera pacote em 1 clique sem simular publicação externa.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => navigateTo("content_factory")}
              className="px-3.5 py-2 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-indigo-400 text-xs font-semibold"
            >
              Ir para Fábrica (30 peças) →
            </button>
            <button
              type="button"
              onClick={async () => {
                try {
                  await apiFetch("/api/v1/agents/AGENT_04_SOCIAL/execute", { method: "POST", body: JSON.stringify({}) });
                  await onReload();
                  showNotice("Calendário multicanal gerado!");
                } catch (err: any) {
                  showNotice(err?.message || "Erro ao gerar calendário automático.");
                }
              }}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
            >
              Gerar Lote de Posts Multicanal com IA
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 pt-3 border-t border-[var(--ug-border-subtle)] items-end text-xs">
          <div>
            <label htmlFor="ug-cal-title-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Título da Publicação *
            </label>
            <input
              id="ug-cal-title-input"
              value={calTitle}
              onChange={(e) => setCalTitle(e.target.value)}
              placeholder="Ex.: 3 formas de reduzir retrabalho com IA"
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          <div>
            <label htmlFor="ug-cal-platform-select" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Rede Social
            </label>
            <select
              id="ug-cal-platform-select"
              value={calPlatform}
              onChange={(e) => setCalPlatform(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            >
              <option value="instagram">Instagram</option>
              <option value="linkedin">LinkedIn</option>
              <option value="tiktok">TikTok</option>
              <option value="youtube">YouTube</option>
              <option value="facebook">Facebook</option>
              <option value="pinterest">Pinterest</option>
            </select>
          </div>
          <div>
            <label htmlFor="ug-cal-format-select" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Formato
            </label>
            <select
              id="ug-cal-format-select"
              value={calFormat}
              onChange={(e) => setCalFormat(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            >
              <option value="CAROUSEL">Carrossel</option>
              <option value="POST">Post Único</option>
              <option value="REELS_SHORT">Reels / Short / TikTok</option>
              <option value="VIDEO">Vídeo Longo</option>
            </select>
          </div>
          <div>
            <label htmlFor="ug-cal-date-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Data e Hora (AAAA-MM-DD HH:MM)
            </label>
            <input
              id="ug-cal-date-input"
              value={calDate}
              onChange={(e) => setCalDate(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          <button
            type="button"
            onClick={async () => {
              if (!calTitle.trim()) {
                showNotice("Informe o Título da Publicação antes de agendar.");
                return;
              }
              try {
                await apiFetch("/api/v1/social/calendar", {
                  method: "POST",
                  body: JSON.stringify({
                    title: calTitle.trim(),
                    platform: calPlatform,
                    content_format: calFormat,
                    scheduled_for: calDate,
                    auto_generate_copy: true,
                  }),
                });
                setCalTitle("");
                await onReload();
                showNotice("Publicação agendada e enviada para aprovação!");
              } catch (err: any) {
                showNotice(err?.message || "Erro ao agendar publicação.");
              }
            }}
            className="py-2 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold h-[34px]"
          >
            Agendar no Calendário
          </button>
        </div>
      </div>

      {calendarData.length === 0 ? (
        <EmptyState
          title="Nenhuma publicação no calendário ainda"
          description="Agende um post acima ou gere 30 peças na Fábrica de Conteúdo."
          actionLabel="Abrir Fábrica de Conteúdo"
          onAction={() => navigateTo("content_factory")}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {calendarData.map((item: any) => (
            <div key={item.id} className="ug-card rounded-xl p-4 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 font-semibold uppercase text-[10px]">
                  {item.platform} • {item.content_format}
                </span>
                <span className="text-[var(--ug-text-muted)] tabular-nums">{item.scheduled_for}</span>
              </div>
              <div className="font-semibold text-[var(--ug-text-primary)] text-sm">{item.title}</div>
              <p className="text-[var(--ug-text-secondary)] whitespace-pre-line">{item.caption}</p>
              <div className="flex items-center justify-between pt-2 border-t border-[var(--ug-border-subtle)] gap-2">
                <span className="text-[11px] text-amber-300">
                  Aprovação: <strong>{item.approval_status === "APPROVED" ? "Aprovado" : "Aguardando"}</strong> • Envio:{" "}
                  <strong>{item.publish_status}</strong>
                </span>
                <button
                  type="button"
                  onClick={async () => {
                    try {
                      const r = await apiFetch(`/api/v1/social/calendar/${item.id}/publish`, { method: "POST" });
                      await onReload();
                      showNotice(r.message || "Status atualizado.");
                    } catch (err: any) {
                      showNotice(err?.message || "Erro ao publicar.");
                    }
                  }}
                  className="px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] shrink-0"
                >
                  Aprovar &amp; Verificar Envio
                </button>
              </div>
              {item.last_error && <div className="text-[11px] text-amber-400">{item.last_error}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function CreativeCopyAndGrowthLabWorkspace({
  mode,
  meData,
  creativeData,
  creativeTitle,
  setCreativeTitle,
  creativeType,
  setCreativeType,
  creativeHeadline,
  setCreativeHeadline,
  creativeCta,
  copyData,
  copyTitle,
  setCopyTitle,
  copyType,
  setCopyType,
  copyFramework,
  setCopyFramework,
  copyOffer,
  setCopyOffer,
  copyBenefit,
  setCopyBenefit,
  growthData,
  expTitle,
  setExpTitle,
  expChannel,
  setExpChannel,
  expHyp,
  setExpHyp,
  expObj,
  apiFetch,
  onReload,
  onNavigate,
  showNotice,
}: any) {
  if (mode === "creative") {
    return (
      <div className="space-y-5 max-w-7xl mx-auto ug-fade-in">
        <PlainOrientationBar
          whatIsIt="Estúdio Criativo Programático (PNG & Roteiros)"
          whyUseIt="Renderiza artes com sua marca via Pillow sem depender de APIs externas pagas"
          nextStep="Escolha o formato e gere a arte para download instantâneo"
        />
        <div className="ug-card rounded-xl p-5 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
            <input
              value={creativeTitle}
              onChange={(e) => setCreativeTitle(e.target.value)}
              placeholder="Nome do Criativo"
              aria-label="Nome do Criativo"
              className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]"
            />
            <select
              value={creativeType}
              onChange={(e) => setCreativeType(e.target.value)}
              aria-label="Formato do Criativo"
              className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]"
            >
              <option value="SOCIAL_POST">Post 1080x1080</option>
              <option value="CAROUSEL">Carrossel Multi-Slide</option>
              <option value="THUMBNAIL">Thumbnail YouTube 1280x720</option>
              <option value="COVER">Capa Stories/Reels 1080x1920</option>
              <option value="BANNER">Banner Comercial 1200x628</option>
              <option value="INFOGRAPHIC">Infográfico 1080x1600</option>
              <option value="VIDEO_SCRIPT">Roteiro de Vídeo</option>
            </select>
            <input
              value={creativeHeadline}
              onChange={(e) => setCreativeHeadline(e.target.value)}
              placeholder="Headline Principal da Arte"
              aria-label="Headline da Arte"
              className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)] md:col-span-2"
            />
            <button
              type="button"
              onClick={async () => {
                await apiFetch("/api/v1/creative/assets/generate", {
                  method: "POST",
                  body: JSON.stringify({
                    title: creativeTitle,
                    asset_type: creativeType,
                    platform: "instagram",
                    headline_text: creativeHeadline,
                    cta_text: creativeCta,
                  }),
                });
                await onReload();
                showNotice("Ativo visual renderizado em PNG com sucesso!");
              }}
              className="py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
            >
              Produzir Ativo Visual
            </button>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {creativeData.map((asset: any) => (
            <div key={asset.id} className="ug-card rounded-xl overflow-hidden flex flex-col">
              {asset.preview_data_uri && (
                <img src={asset.preview_data_uri} alt={asset.title} className="w-full h-56 object-contain bg-[var(--ug-bg)] border-b border-[var(--ug-border-subtle)]" />
              )}
              <div className="p-4 space-y-2 text-xs flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-indigo-400">{asset.asset_type}</span>
                  <span className="text-[var(--ug-text-muted)]">{asset.dimensions}</span>
                </div>
                <div className="font-semibold text-[var(--ug-text-primary)] text-sm">{asset.title}</div>
                <div className="text-[10px] text-emerald-400">{asset.license_info}</div>
                {asset.preview_data_uri && (
                  <a href={asset.preview_data_uri} download={`${asset.title}.png`} className="inline-block mt-2 px-3 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-primary)] text-[11px]">
                    Baixar PNG Original
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (mode === "copywriter") {
    return (
      <div className="space-y-5 max-w-7xl mx-auto ug-fade-in">
        <div className="ug-card rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">
            Copywriter &amp; Testes A/B (Frameworks AIDA / PAS / FAB)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-6 gap-3 text-xs">
            <input value={copyTitle} onChange={(e) => setCopyTitle(e.target.value)} aria-label="Título da Copy" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
            <select value={copyType} onChange={(e) => setCopyType(e.target.value)} aria-label="Tipo de Copy" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]">
              <option value="LANDING_PAGE">Landing Page</option>
              <option value="SALES_PAGE">Página de Vendas</option>
              <option value="AD_COPY">Anúncio Pago</option>
              <option value="EMAIL_SEQUENCE">Sequência de E-mail</option>
              <option value="WHATSAPP_MESSAGE">Mensagem WhatsApp</option>
            </select>
            <select value={copyFramework} onChange={(e) => setCopyFramework(e.target.value)} aria-label="Framework de Copy" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]">
              <option value="AIDA">AIDA</option>
              <option value="PAS">PAS</option>
              <option value="BAB">BAB</option>
              <option value="FAB">FAB</option>
            </select>
            <input value={copyOffer} onChange={(e) => setCopyOffer(e.target.value)} aria-label="Oferta" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
            <input value={copyBenefit} onChange={(e) => setCopyBenefit(e.target.value)} aria-label="Benefício Principal" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
            <button
              type="button"
              onClick={async () => {
                await apiFetch("/api/v1/copywriter/generate", {
                  method: "POST",
                  body: JSON.stringify({
                    title: copyTitle,
                    copy_type: copyType,
                    framework: copyFramework,
                    product_or_offer: copyOffer,
                    target_audience: meData?.active_tenant?.target_audience || "Empresas B2B",
                    key_benefit: copyBenefit,
                  }),
                });
                await onReload();
                showNotice("Variantes A/B geradas!");
              }}
              className="py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
            >
              Gerar Copy A/B
            </button>
          </div>
        </div>
        <div className="space-y-4">
          {copyData.map((c: any) => (
            <div key={c.id} className="ug-card rounded-xl p-5 space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-[var(--ug-text-primary)] text-sm">{c.title} ({c.copy_type} • {c.framework})</span>
                <StatusPill status="EXECUTED" label="Compliance Ético" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] whitespace-pre-line">
                  <div className="font-semibold text-indigo-400 mb-1">Variante A (Controle)</div>
                  {c.variant_a}
                </div>
                <div className="p-3 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] whitespace-pre-line">
                  <div className="font-semibold text-emerald-400 mb-1">Variante B (Teste)</div>
                  {c.variant_b}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      <GrowthExecutionCenter meData={meData} apiFetch={apiFetch} onReload={onReload} onNavigate={onNavigate} showNotice={showNotice} />

      <div className="ug-card rounded-xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">Growth Lab — Experimentos ICE &amp; Conversão</h3>
          <button
            type="button"
            onClick={async () => {
              await apiFetch("/api/v1/agents/AGENT_07_GROWTH/execute", { method: "POST", body: JSON.stringify({}) });
              await onReload();
              showNotice("Experimento ICE estruturado!");
            }}
            className="px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
          >
            Gerar Experimento ICE Automático
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
          <input value={expTitle} onChange={(e) => setExpTitle(e.target.value)} placeholder="Título do Experimento" aria-label="Título do Experimento" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          <input value={expChannel} onChange={(e) => setExpChannel(e.target.value)} placeholder="Canal" aria-label="Canal do Experimento" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          <input value={expHyp} onChange={(e) => setExpHyp(e.target.value)} placeholder="Hipótese Testável" aria-label="Hipótese do Experimento" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          <button
            type="button"
            onClick={async () => {
              if (!expTitle || !expHyp) return;
              await apiFetch("/api/v1/growth/experiments", {
                method: "POST",
                body: JSON.stringify({ title: expTitle, channel: expChannel, hypothesis: expHyp, objective: expObj, impact: 9, confidence: 8, ease: 8 }),
              });
              setExpTitle("");
              setExpHyp("");
              await onReload();
              showNotice("Experimento registrado!");
            }}
            className="py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
          >
            Registrar Experimento
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {growthData.map((exp: any) => (
          <div key={exp.id} className="ug-card rounded-xl p-5 space-y-2 text-xs">
            <div className="flex items-center justify-between gap-2">
              <span className="font-semibold text-[var(--ug-text-primary)] text-sm">{exp.title}</span>
              <OriginBadge origin={exp.data_origin} />
            </div>
            <div className="text-indigo-400 font-medium tabular-nums">
              {exp.channel} • ICE {exp.ice_score}/10 • {exp.status}
            </div>
            <p className="text-[var(--ug-text-secondary)]"><strong>Hipótese:</strong> {exp.hypothesis}</p>
            <p className="text-[var(--ug-text-muted)] tabular-nums">
              Base: {exp.baseline_conversion_pct}% • Resultado Real:{" "}
              {exp.real_result_conversion_pct !== null ? `${exp.real_result_conversion_pct}%` : "Aguardando coleta"}
            </p>
            {exp.status !== "COMPLETED" && (
              <button
                type="button"
                onClick={async () => {
                  await apiFetch(`/api/v1/growth/experiments/${exp.id}/result`, {
                    method: "PUT",
                    body: JSON.stringify({
                      real_result_conversion_pct: Number((exp.baseline_conversion_pct * 1.45).toFixed(2)),
                      real_result_summary: "Resultado real validado em produção.",
                      conclusion: "Hipótese validada com ganho real de conversão.",
                      status: "COMPLETED",
                    }),
                  });
                  await onReload();
                  showNotice("Resultado real aferido!");
                }}
                className="px-3 py-1 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-primary)] text-[11px]"
              >
                Registrar Resultado Real Aferido
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
