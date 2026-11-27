"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  FileText,
  Flame,
  Radar,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import { LegacyMenuId } from "@/lib/navigation";
import { EmptyState, FilterTabBar, MetricStrip, OriginBadge, StatusPill } from "@/components/DesignSystem";

const PIPELINE_STAGES = [
  { id: "NEW_LEAD", label: "Novo Lead" },
  { id: "QUALIFICATION", label: "Qualificação" },
  { id: "PROPOSAL", label: "Proposta Enviada" },
  { id: "NEGOTIATION", label: "Em Negociação" },
  { id: "CLOSED_WON", label: "Venda Ganha" },
  { id: "CLOSED_LOST", label: "Perdida" },
];

export function CRMAndLeadsWorkspace({
  crmData,
  revenueIntel,
  crmLeadFilter,
  setCrmLeadFilter,
  leadName,
  setLeadName,
  leadEmail,
  setLeadEmail,
  leadPhone,
  setLeadPhone,
  leadCompany,
  setLeadCompany,
  leadValue,
  setLeadValue,
  leadLgpdConsent,
  setLeadLgpdConsent,
  apiFetch,
  onReload,
  onNavigate,
  showNotice,
}: {
  crmData: any;
  revenueIntel: any;
  crmLeadFilter: string;
  setCrmLeadFilter: (v: string) => void;
  leadName: string;
  setLeadName: (v: string) => void;
  leadEmail: string;
  setLeadEmail: (v: string) => void;
  leadPhone: string;
  setLeadPhone: (v: string) => void;
  leadCompany: string;
  setLeadCompany: (v: string) => void;
  leadValue: string;
  setLeadValue: (v: string) => void;
  leadLgpdConsent: boolean;
  setLeadLgpdConsent: (v: boolean) => void;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  onNavigate: (view: LegacyMenuId) => void;
  showNotice: (msg: string) => void;
}) {
  const [followUpBusyId, setFollowUpBusyId] = useState<number | null>(null);
  const revSum = revenueIntel?.summary;
  const hotLeads: any[] = revenueIntel?.hot_uncontacted_leads || [];
  const hotLeadIds = new Set(hotLeads.map((x) => x.lead_id));

  const visibleLeads = (crmData?.leads || []).filter((l: any) => {
    const q = crmLeadFilter.trim().toLowerCase();
    if (!q) return true;
    return `${l.full_name || ""} ${l.company_name || ""} ${l.email || ""} ${l.qualification_status || ""} ${l.pipeline_stage || ""}`
      .toLowerCase()
      .includes(q);
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      {revSum && (
        <MetricStrip
          items={[
            {
              key: "real_leads",
              label: "Leads Reais",
              value: revSum.real_leads_count,
              subtext: "Base LGPD validada",
              origin: "REAL",
            },
            {
              key: "hot_uncontacted",
              label: "Leads Quentes em Entrada",
              value: revSum.hot_uncontacted_count,
              subtext: revSum.hot_uncontacted_count > 0 ? "Priorizar 1º contato" : "Nenhum lead quente parado",
              origin: "REAL",
            },
            {
              key: "stalled_deals",
              label: "Negociações Paradas",
              value: revSum.stalled_deals_count,
              subtext: revSum.stalled_deals_count > 0 ? "Ação recomendada no funil" : "Fluxo em movimento",
              origin: "REAL",
              onClick: () => onNavigate("commercial"),
            },
            {
              key: "win_rate",
              label: "Taxa de Conversão",
              value: `${revSum.win_rate_pct}%`,
              subtext: `Ticket médio R$ ${Number(revSum.avg_ticket_brl || 0).toLocaleString("pt-BR")}`,
              origin: revSum.won_deals_count > 0 ? "REAL" : "ESTIMATED",
            },
          ]}
        />
      )}

      {/* Próxima Melhor Ação (CRM Revenue Intelligence) */}
      {(revenueIntel?.next_best_actions || []).length > 0 && (
        <section className="ug-card rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2.5 min-w-0">
            <Flame className="w-4 h-4 text-amber-400 shrink-0" aria-hidden="true" />
            <div className="min-w-0">
              <span className="font-semibold text-[var(--ug-text-primary)]">
                Próxima Ação de Receita:{" "}
              </span>
              <span className="text-[var(--ug-text-secondary)]">
                {revenueIntel.next_best_actions[0].title} — {revenueIntel.next_best_actions[0].impact}
              </span>
            </div>
          </div>
          {revenueIntel.next_best_actions[0].type === "QUICK_FOLLOWUP" && (
            <button
              type="button"
              disabled={followUpBusyId === revenueIntel.next_best_actions[0].lead_id}
              onClick={async () => {
                const lid = revenueIntel.next_best_actions[0].lead_id;
                setFollowUpBusyId(lid);
                try {
                  const res = await apiFetch(`/api/v1/crm/leads/${lid}/quick-followup`, { method: "POST" });
                  await onReload();
                  showNotice(res?.message || "Follow-up registrado!");
                } catch (err: any) {
                  showNotice(err?.message || "Erro ao registrar follow-up.");
                } finally {
                  setFollowUpBusyId(null);
                }
              }}
              className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium shrink-0"
            >
              Registrar Follow-up (1 Clique)
            </button>
          )}
        </section>
      )}

      {/* Cadastro rápido LGPD */}
      <section className="ug-card rounded-xl p-5 space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">
            Capturar e Qualificar Novo Lead (CRM com IA &amp; LGPD)
          </h4>
          <p className="text-xs text-[var(--ug-text-muted)] mt-0.5">
            Ao registrar, a IA calcula a pontuação (0 a 100) e agenda o próximo passo comercial.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-3 items-end text-xs">
          <div>
            <label htmlFor="ug-lead-name-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Nome do Contato *
            </label>
            <input
              id="ug-lead-name-input"
              value={leadName}
              onChange={(e) => setLeadName(e.target.value)}
              placeholder="Ex.: Maria Oliveira"
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          <div>
            <label htmlFor="ug-lead-email-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              E-mail Corporativo *
            </label>
            <input
              id="ug-lead-email-input"
              type="email"
              value={leadEmail}
              onChange={(e) => setLeadEmail(e.target.value)}
              placeholder="Ex.: maria@empresa.com.br"
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          <div>
            <label htmlFor="ug-lead-phone-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              WhatsApp / Telefone
            </label>
            <input
              id="ug-lead-phone-input"
              value={leadPhone}
              onChange={(e) => setLeadPhone(e.target.value)}
              placeholder="Ex.: +55 11 99999-0000"
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          <div>
            <label htmlFor="ug-lead-company-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Empresa
            </label>
            <input
              id="ug-lead-company-input"
              value={leadCompany}
              onChange={(e) => setLeadCompany(e.target.value)}
              placeholder="Ex.: Alpha Soluções"
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          <div>
            <label htmlFor="ug-lead-value-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Valor Estimado (R$)
            </label>
            <input
              id="ug-lead-value-input"
              type="number"
              value={leadValue}
              onChange={(e) => setLeadValue(e.target.value)}
              placeholder="Ex.: 15000"
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)] tabular-nums"
            />
          </div>
          <button
            type="button"
            onClick={async () => {
              if (!leadName.trim() || !leadEmail.trim()) {
                showNotice("Preencha o Nome do Contato e o E-mail Corporativo para registrar o lead.");
                return;
              }
              if (!leadLgpdConsent) {
                showNotice("Marque a confirmação de consentimento LGPD antes de cadastrar o lead.");
                return;
              }
              try {
                await apiFetch("/api/v1/crm/leads", {
                  method: "POST",
                  body: JSON.stringify({
                    full_name: leadName.trim(),
                    email: leadEmail.trim(),
                    phone: leadPhone.trim(),
                    company_name: leadCompany.trim(),
                    buy_intent: "URGENT",
                    estimated_value: Number(leadValue) || 0,
                    consent_lgpd: true,
                    data_origin: "REAL",
                  }),
                });
                setLeadName("");
                setLeadEmail("");
                setLeadPhone("");
                setLeadCompany("");
                await onReload();
                showNotice("Lead cadastrado, pontuado pelo AI Sales Director e follow-up criado!");
              } catch (err: any) {
                showNotice(err?.message || "Erro ao registrar lead.");
              }
            }}
            className="py-2 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold h-[34px]"
          >
            Qualificar &amp; Registrar
          </button>
        </div>
        <div className="flex items-center gap-2 pt-1">
          <input
            id="ug-lead-lgpd-checkbox"
            type="checkbox"
            checked={leadLgpdConsent}
            onChange={(e) => setLeadLgpdConsent(e.target.checked)}
            className="rounded border-[var(--ug-border)]"
          />
          <label htmlFor="ug-lead-lgpd-checkbox" className="text-[11px] text-[var(--ug-text-secondary)] cursor-pointer">
            Confirmo que o contato autorizou o tratamento comercial destes dados conforme a LGPD.
          </label>
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <section className="lg:col-span-7 ug-card rounded-xl overflow-hidden">
          <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] flex flex-wrap items-center justify-between gap-2">
            <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">
              Base de Leads Qualificados ({crmData.leads.length})
            </h4>
            <input
              id="ug-crm-search-input"
              value={crmLeadFilter}
              onChange={(e) => setCrmLeadFilter(e.target.value)}
              placeholder="Buscar lead por nome, empresa ou status..."
              aria-label="Filtrar leads no CRM"
              className="w-full sm:w-64 bg-[var(--ug-bg)] border border-[var(--ug-border)] rounded-lg px-3 py-1.5 text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          {visibleLeads.length === 0 ? (
            <div className="p-4">
              <EmptyState
                title={crmData.leads.length === 0 ? "Nenhum lead cadastrado ainda" : "Nenhum lead corresponde à busca"}
                description={
                  crmData.leads.length === 0
                    ? "Use o formulário acima para registrar seu primeiro contato qualificado."
                    : "Tente outro nome, empresa ou limpe o campo de busca."
                }
                actionLabel={crmLeadFilter ? "Limpar busca" : undefined}
                onAction={crmLeadFilter ? () => setCrmLeadFilter("") : undefined}
              />
            </div>
          ) : (
            <div className="divide-y divide-white/[0.05]">
              {visibleLeads.map((l: any) => (
                <div key={l.id} className="px-5 py-3.5 hover:bg-white/[0.02] transition flex flex-wrap justify-between items-center gap-3 text-xs">
                  <div className="space-y-0.5 min-w-0">
                    <div className="font-semibold text-[var(--ug-text-primary)] flex items-center gap-2 flex-wrap">
                      <span>{l.full_name} ({l.company_name || "Direto"})</span>
                      {hotLeadIds.has(l.id) && (
                        <span className="px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 text-[10px] font-medium">
                          Prioritário
                        </span>
                      )}
                    </div>
                    <div className="text-[var(--ug-text-muted)]">
                      {l.email} {l.phone ? `• ${l.phone}` : ""} • Origem: {l.source_channel}
                    </div>
                    <div className="text-indigo-400 tabular-nums">
                      {l.qualification_status} • {l.pipeline_stage} • Est.: R$ {l.estimated_value}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-semibold tabular-nums">
                      Score {l.lead_score}/100
                    </span>
                    <OriginBadge origin={l.data_origin} />
                    {hotLeadIds.has(l.id) && (
                      <button
                        type="button"
                        disabled={followUpBusyId === l.id}
                        onClick={async () => {
                          setFollowUpBusyId(l.id);
                          try {
                            const res = await apiFetch(`/api/v1/crm/leads/${l.id}/quick-followup`, { method: "POST" });
                            await onReload();
                            showNotice(res?.message || "Follow-up criado!");
                          } finally {
                            setFollowUpBusyId(null);
                          }
                        }}
                        className="px-2.5 py-1 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-secondary)] text-[11px] font-medium"
                      >
                        Follow-up
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="lg:col-span-5 ug-card rounded-xl overflow-hidden">
          <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] flex items-center justify-between">
            <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">Atividades &amp; Retorno Comercial</h4>
            <button
              type="button"
              onClick={() => onNavigate("commercial")}
              className="text-xs font-medium text-indigo-400 hover:underline inline-flex items-center gap-1"
            >
              <span>Avançar no Funil</span>
              <ArrowRight className="w-3 h-3" aria-hidden="true" />
            </button>
          </div>
          {crmData.activities.length === 0 ? (
            <div className="p-4">
              <EmptyState
                title="Nenhuma tarefa de retorno aberta"
                description="Ao registrar um lead ao lado, o AI Sales Director cria automaticamente o próximo passo de acompanhamento."
              />
            </div>
          ) : (
            <div className="divide-y divide-white/[0.05]">
              {crmData.activities.slice(0, 12).map((a: any) => (
                <div key={a.id} className="px-5 py-3 text-xs space-y-1">
                  <div className="flex justify-between font-semibold text-[var(--ug-text-primary)] gap-2">
                    <span className="truncate">{a.subject}</span>
                    <span className="text-[11px] text-indigo-400 tabular-nums shrink-0">{a.due_date}</span>
                  </div>
                  <div className="text-[11px] text-[var(--ug-text-muted)]">{a.description}</div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export function CommercialPipelineWorkspace({
  crmData,
  revenueIntel,
  dealTitle,
  setDealTitle,
  dealValue,
  setDealValue,
  dealStage,
  setDealStage,
  apiFetch,
  onReload,
  onNavigate,
  showNotice,
}: {
  crmData: any;
  revenueIntel: any;
  dealTitle: string;
  setDealTitle: (v: string) => void;
  dealValue: string;
  setDealValue: (v: string) => void;
  dealStage: string;
  setDealStage: (v: string) => void;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  onNavigate: (view: LegacyMenuId) => void;
  showNotice: (msg: string) => void;
}) {
  const stalledIds = new Set((revenueIntel?.stalled_deals || []).map((d: any) => d.deal_id));

  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      <MetricStrip
        items={[
          {
            key: "open_deals",
            label: "Negociações Abertas",
            value: crmData.commercial_summary.open_deals_count,
            subtext: stalledIds.size > 0 ? `${stalledIds.size} parada(s) precisando de ação` : "Em ritmo saudável",
            origin: "REAL",
          },
          {
            key: "won_deals",
            label: "Vendas Fechadas",
            value: crmData.commercial_summary.won_deals_count,
            subtext: `Win Rate ${revenueIntel?.summary?.win_rate_pct ?? 0}%`,
            origin: "REAL",
          },
          {
            key: "won_rev",
            label: "Receita Fechada",
            value: `R$ ${Number(crmData.commercial_summary.won_revenue_brl || 0).toLocaleString("pt-BR")}`,
            subtext: "Contratos ganhos",
            origin: "REAL",
          },
          {
            key: "forecast",
            label: "Previsão Ponderada do Funil",
            value: `R$ ${Number(crmData.commercial_summary.weighted_forecast_brl || 0).toLocaleString("pt-BR")}`,
            subtext: "Valor ajustado por etapa",
            origin: "ESTIMATED",
          },
        ]}
      />

      <section className="ug-card rounded-xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">Nova Negociação no Pipeline</h4>
            <p className="text-xs text-[var(--ug-text-muted)] mt-0.5">
              Cadastre oportunidades para acompanhar etapa por etapa até o fechamento.
            </p>
          </div>
          <button
            type="button"
            onClick={() => onNavigate("multibusiness")}
            className="text-xs font-medium text-indigo-400 hover:underline inline-flex items-center gap-1"
          >
            <FileText className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Gerar Proposta com PDF →</span>
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end text-xs">
          <div>
            <label htmlFor="ug-deal-title-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Título da Negociação *
            </label>
            <input
              id="ug-deal-title-input"
              value={dealTitle}
              onChange={(e) => setDealTitle(e.target.value)}
              placeholder="Ex.: Projeto Automação IA — Sul Logística"
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            />
          </div>
          <div>
            <label htmlFor="ug-deal-value-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Valor do Contrato (R$)
            </label>
            <input
              id="ug-deal-value-input"
              type="number"
              value={dealValue}
              onChange={(e) => setDealValue(e.target.value)}
              placeholder="Ex.: 25000"
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)] tabular-nums"
            />
          </div>
          <div>
            <label htmlFor="ug-deal-stage-select" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Etapa Atual
            </label>
            <select
              id="ug-deal-stage-select"
              value={dealStage}
              onChange={(e) => setDealStage(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            >
              {PIPELINE_STAGES.map((st) => (
                <option key={st.id} value={st.id}>
                  {st.label}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            onClick={async () => {
              if (!dealTitle.trim()) {
                showNotice("Informe o Título da Negociação antes de adicionar ao funil.");
                return;
              }
              try {
                await apiFetch("/api/v1/crm/deals", {
                  method: "POST",
                  body: JSON.stringify({
                    title: dealTitle.trim(),
                    stage: dealStage,
                    value: Number(dealValue) || 0,
                    probability_pct: 70,
                    data_origin: "REAL",
                  }),
                });
                setDealTitle("");
                await onReload();
                showNotice("Negociação adicionada ao Pipeline Comercial!");
              } catch (err: any) {
                showNotice(err?.message || "Erro ao registrar negociação.");
              }
            }}
            className="py-2 px-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold h-[34px]"
          >
            Adicionar Negociação ao Funil
          </button>
        </div>
      </section>

      {/* Kanban DS 3.0 limpo sem card dentro de card */}
      <div className="ug-card rounded-2xl grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 divide-y md:divide-y-0 md:divide-x divide-white/[0.06] overflow-hidden">
        {PIPELINE_STAGES.map((stageObj) => {
          const stageDeals = crmData.deals.filter((d: any) => d.stage === stageObj.id);
          return (
            <div key={stageObj.id} className="p-3.5 space-y-2.5">
              <div className="text-[11px] font-semibold text-[var(--ug-text-secondary)] flex justify-between pb-1.5 border-b border-[var(--ug-border-subtle)]">
                <span>{stageObj.label}</span>
                <span className="tabular-nums text-indigo-400">({stageDeals.length})</span>
              </div>
              {stageDeals.length === 0 ? (
                <div className="py-6 text-center text-[11px] text-[var(--ug-text-muted)]">
                  Sem itens
                </div>
              ) : (
                <div className="divide-y divide-white/[0.05]">
                  {stageDeals.map((d: any) => (
                    <div key={d.id} className="py-2.5 text-xs space-y-1.5">
                      <div className="font-medium text-[var(--ug-text-primary)] flex items-start justify-between gap-1">
                        <span>{d.title}</span>
                        {stalledIds.has(d.id) && (
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" aria-label="Negociação parada" />
                        )}
                      </div>
                      <div className="text-emerald-400 font-semibold tabular-nums">
                        R$ {Number(d.value || 0).toLocaleString("pt-BR")}
                      </div>
                      <select
                        aria-label={`Mover etapa de ${d.title}`}
                        value={d.stage}
                        onChange={async (e) => {
                          await apiFetch(`/api/v1/crm/deals/${d.id}/stage`, {
                            method: "PUT",
                            body: JSON.stringify({ stage: e.target.value }),
                          });
                          await onReload();
                          showNotice(`Negociação movida para ${e.target.value}!`);
                        }}
                        className="w-full px-2 py-1 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[11px] text-[var(--ug-text-secondary)]"
                      >
                        {PIPELINE_STAGES.map((s) => (
                          <option key={s.id} value={s.id}>
                            Mover: {s.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function MultiBusinessAndProposalsWorkspace({
  mbDashboard,
  setMbDashboard,
  selectedUnit,
  setSelectedUnit,
  token,
  activeTenantId,
  propClientName,
  setPropClientName,
  propClientCompany,
  setPropClientCompany,
  propClientEmail,
  setPropClientEmail,
  propServiceCode,
  setPropServiceCode,
  propProblem,
  setPropProblem,
  agencyClientName,
  setAgencyClientName,
  agencyBrandName,
  setAgencyBrandName,
  agencyPlanTier,
  setAgencyPlanTier,
  agencyRetainer,
  apiFetch,
  onNavigate,
  showNotice,
}: {
  mbDashboard: any;
  setMbDashboard: (v: any) => void;
  selectedUnit: string;
  setSelectedUnit: (v: string) => void;
  token: string;
  activeTenantId: number | null;
  propClientName: string;
  setPropClientName: (v: string) => void;
  propClientCompany: string;
  setPropClientCompany: (v: string) => void;
  propClientEmail: string;
  setPropClientEmail: (v: string) => void;
  propServiceCode: string;
  setPropServiceCode: (v: string) => void;
  propProblem: string;
  setPropProblem: (v: string) => void;
  agencyClientName: string;
  setAgencyClientName: (v: string) => void;
  agencyBrandName: string;
  setAgencyBrandName: (v: string) => void;
  agencyPlanTier: string;
  setAgencyPlanTier: (v: string) => void;
  agencyRetainer: string;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onNavigate: (view: LegacyMenuId) => void;
  showNotice: (msg: string) => void;
}) {
  const [subSection, setSubSection] = useState<string>("propostas");
  const [showAllFunnelStages, setShowAllFunnelStages] = useState(false);

  const fin = mbDashboard?.financial_summary?.consolidated;
  const panel18 = mbDashboard?.phase18_1_executive_panel;
  const funnelEntries = Object.entries(mbDashboard?.sales_funnel_10_stages || {});

  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      {/* Cabeçalho Enxuto + Filtro de Unidade */}
      <section className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-[var(--ug-text-primary)]">
            Propostas PDF, Contratos &amp; Operação Multinegócio
          </h2>
          <p className="text-xs text-[var(--ug-text-muted)]">
            Fonte: {mbDashboard.data_source} • Período: {mbDashboard.period_reference} • Separação estrita entre DADO REAL, PROJEÇÃO e META
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {[
            { code: "ALL", label: "Visão Consolidada (3 Unidades)" },
            { code: "UNION_TECH", label: "Unidade A: UNION TECH" },
            { code: "UNION_AGENCY", label: "Unidade B: UNION AGENCY" },
            { code: "UNION_PARTNERS", label: "Unidade C: UNION PARTNERS" },
          ].map((u) => (
            <button
              key={u.code}
              type="button"
              onClick={async () => {
                setSelectedUnit(u.code);
                const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${u.code}`);
                setMbDashboard(res);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
                selectedUnit === u.code
                  ? "bg-indigo-600 border-indigo-500 text-white"
                  : "border-[var(--ug-border)] text-[var(--ug-text-secondary)] hover:bg-white/[0.04]"
              }`}
            >
              {u.label}
            </button>
          ))}
          <button
            type="button"
            onClick={async () => {
              await apiFetch("/api/v1/ceo/multibusiness-briefing", { method: "POST" });
              const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`);
              setMbDashboard(res);
              showNotice("Briefing Consolidado Multinegócio gerado pelo AI CEO!");
            }}
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 text-white"
          >
            Gerar Briefing CEO Multinegócio
          </button>
        </div>
      </section>

      {/* KPIs Consolidados em MetricStrip Único */}
      {fin && (
        <MetricStrip
          items={[
            {
              key: "rev",
              label: "Receita Confirmada",
              value: `R$ ${Number(fin.dado_real.received_confirmed_revenue_brl || 0).toLocaleString("pt-BR")}`,
              subtext: `MRR Ativo: R$ ${Number(fin.dado_real.monthly_recurring_revenue_mrr_brl || 0).toLocaleString("pt-BR")}`,
              origin: "REAL",
            },
            {
              key: "profit",
              label: "Lucro Líquido & Margem",
              value: `R$ ${Number(fin.dado_real.net_profit_brl || 0).toLocaleString("pt-BR")}`,
              subtext: `Margem: ${fin.dado_real.margin_pct}% • Custos: R$ ${Number(fin.dado_real.expenses_and_costs_brl || 0).toLocaleString("pt-BR")}`,
              origin: "REAL",
            },
            {
              key: "pipe",
              label: "Pipeline Ponderado",
              value: `R$ ${Number(fin.projecao.weighted_pipeline_projection_brl || 0).toLocaleString("pt-BR")}`,
              subtext: `Negociações abertas: ${fin.projecao.open_deals_count}`,
              origin: "ESTIMATED",
            },
            {
              key: "goal",
              label: "Meta Mensal",
              value: `R$ ${Number(fin.meta.monthly_revenue_goal_brl || 0).toLocaleString("pt-BR")}`,
              subtext: `Atingimento Real: ${fin.meta.goal_attainment_pct}%`,
              origin: "GOAL",
            },
          ]}
        />
      )}

      {/* Transparência Financeira + Toggle do Funil de 17 Etapas */}
      {panel18 && (
        <section className="ug-card rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-[var(--ug-border-subtle)] flex flex-wrap justify-between items-center gap-2 text-xs">
            <span className="font-semibold text-[var(--ug-text-primary)]">
              Transparência Financeira (Real • Estimativa • Projeção • Meta • Sandbox)
            </span>
            <div className="flex items-center gap-3">
              <span className="text-[11px] text-emerald-400 font-medium">
                1º Pagamento Live: {panel18.REAL.first_real_paid_customer_verified ? "CONFIRMADO" : "AGUARDANDO (R$ 0,00)"}
              </span>
              {funnelEntries.length > 0 && (
                <button
                  type="button"
                  onClick={() => setShowAllFunnelStages((v) => !v)}
                  className="text-[11px] text-indigo-400 hover:underline inline-flex items-center gap-1"
                >
                  <span>{showAllFunnelStages ? "Ocultar etapas detalhadas" : `Ver funil (${funnelEntries.length} etapas)`}</span>
                  {showAllFunnelStages ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>
              )}
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 divide-y sm:divide-y-0 sm:divide-x divide-white/[0.06] text-xs">
            <div className="p-3.5 space-y-0.5">
              <div className="font-semibold text-emerald-400">Real</div>
              <div className="text-[var(--ug-text-primary)] tabular-nums">Receita Live: R$ {panel18.REAL.receita_recebida_confirmada_brl}</div>
              <div className="text-[11px] text-[var(--ug-text-muted)]">Leads: {panel18.REAL.leads_reais} • Contratos: {panel18.REAL.contratos_assinados_com_evidencia}</div>
            </div>
            <div className="p-3.5 space-y-0.5">
              <div className="font-semibold text-amber-300">Estimativa</div>
              <div className="text-[var(--ug-text-primary)] tabular-nums">Custo Médio: R$ {panel18.ESTIMATIVA.custo_medio_servico_brl}</div>
              <div className="text-[11px] text-[var(--ug-text-muted)]">Margem Catálogo: {panel18.ESTIMATIVA.margem_estimada_catalogo_pct}%</div>
            </div>
            <div className="p-3.5 space-y-0.5">
              <div className="font-semibold text-sky-300">Projeção</div>
              <div className="text-[var(--ug-text-primary)] tabular-nums">Pipeline: R$ {panel18.PROJECAO.pipeline_ponderado_aberto_brl}</div>
              <div className="text-[11px] text-[var(--ug-text-muted)]">Abertas: {panel18.PROJECAO.negociacoes_abertas_count}</div>
            </div>
            <div className="p-3.5 space-y-0.5">
              <div className="font-semibold text-indigo-300">Meta</div>
              <div className="text-[var(--ug-text-primary)] tabular-nums">Meta Mensal: R$ {panel18.META.meta_mensal_total_brl}</div>
            </div>
            <div className="p-3.5 space-y-0.5">
              <div className="font-semibold text-[var(--ug-text-secondary)]">Simulação / Sandbox</div>
              <div className="text-[var(--ug-text-primary)] tabular-nums">Sandbox: {panel18.SIMULACAO.cobrancas_sandbox_total} ({panel18.SIMULACAO.pagamentos_sandbox_aprovados} aprov.)</div>
              <div className="text-[11px] text-[var(--ug-text-muted)] tabular-nums">Volume Sandbox: R$ {panel18.SIMULACAO.valor_transacionado_sandbox_brl}</div>
            </div>
          </div>
          {showAllFunnelStages && funnelEntries.length > 0 && (
            <div className="border-t border-[var(--ug-border-subtle)] grid grid-cols-3 sm:grid-cols-6 lg:grid-cols-9 divide-x divide-y divide-white/[0.04] bg-white/[0.01]">
              {funnelEntries.map(([stage, count]: [string, any]) => (
                <div key={stage} className="p-2.5 text-center">
                  <div className="text-[10px] text-[var(--ug-text-muted)] truncate">{stage}</div>
                  <div className="text-sm font-semibold text-indigo-400 tabular-nums">{count}</div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Abas Limpas por Fluxo (mantém Propostas PDF em foco por padrão!) */}
      <FilterTabBar
        activeId={subSection}
        onChange={setSubSection}
        tabs={[
          { id: "propostas", label: "Propostas PDF & Fechamento", count: (mbDashboard.proposals || []).length },
          { id: "servicos", label: "Catálogo & Preços", count: (mbDashboard.services_catalog || []).length },
          { id: "unidades", label: "Agência & Afiliados", count: (mbDashboard.agency_clients || []).length },
          { id: "pagamentos", label: "Pagamentos Sandbox & Entregas", count: (mbDashboard.payments || []).length },
        ]}
      />

      {subSection === "propostas" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <section className="lg:col-span-6 ug-card rounded-xl p-5 space-y-3.5 text-xs">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">Gerador de Propostas Comerciais</h3>
                <p className="text-[11px] text-[var(--ug-text-muted)] mt-0.5">
                  1. Gere a proposta → 2. Abra o PDF seguro → 3. Aprovar &amp; Fechar → 4. Acompanhe no Pipeline.
                </p>
              </div>
              <button
                type="button"
                onClick={() => onNavigate("commercial")}
                className="text-xs font-medium text-indigo-400 hover:underline"
              >
                Ver Pipeline →
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <div>
                <label htmlFor="ug-prop-client-name" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                  Nome do Decisor *
                </label>
                <input
                  id="ug-prop-client-name"
                  value={propClientName}
                  onChange={(e) => setPropClientName(e.target.value)}
                  placeholder="Ex.: Carlos Eduardo Silva"
                  className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                />
              </div>
              <div>
                <label htmlFor="ug-prop-client-company" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                  Empresa Cliente *
                </label>
                <input
                  id="ug-prop-client-company"
                  value={propClientCompany}
                  onChange={(e) => setPropClientCompany(e.target.value)}
                  placeholder="Ex.: Sul Logística Ltda"
                  className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                />
              </div>
              <div>
                <label htmlFor="ug-prop-client-email" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                  E-mail Corporativo *
                </label>
                <input
                  id="ug-prop-client-email"
                  type="email"
                  value={propClientEmail}
                  onChange={(e) => setPropClientEmail(e.target.value)}
                  placeholder="Ex.: carlos@sullogistica.com.br"
                  className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                />
              </div>
              <div>
                <label htmlFor="ug-prop-service-select" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                  Serviço Ofertado
                </label>
                <select
                  id="ug-prop-service-select"
                  value={propServiceCode}
                  onChange={(e) => setPropServiceCode(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                >
                  {(mbDashboard.services_catalog || []).map((s: any) => (
                    <option key={s.service_code} value={s.service_code}>
                      {s.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label htmlFor="ug-prop-problem-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                Problema do cliente que esta proposta resolve
              </label>
              <textarea
                id="ug-prop-problem-input"
                value={propProblem}
                onChange={(e) => setPropProblem(e.target.value)}
                placeholder="Ex.: Leads demoram 4h para serem respondidos e planilhas atrasam o acompanhamento comercial."
                className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)] h-16"
              />
            </div>
            <button
              type="button"
              onClick={async () => {
                if (!propClientName.trim() || !propClientCompany.trim() || !propClientEmail.trim()) {
                  showNotice("Preencha Nome do Decisor, Empresa Cliente e E-mail Corporativo para gerar a proposta.");
                  return;
                }
                try {
                  await apiFetch("/api/v1/commercial/proposals", {
                    method: "POST",
                    body: JSON.stringify({
                      business_unit_code: "UNION_TECH",
                      service_code: propServiceCode,
                      client_name: propClientName.trim(),
                      client_company: propClientCompany.trim(),
                      client_email: propClientEmail.trim(),
                      identified_problem: propProblem.trim() || "Gargalos manuais em atendimento e integração de dados.",
                    }),
                  });
                  setPropClientName("");
                  setPropClientCompany("");
                  setPropClientEmail("");
                  setPropProblem("");
                  const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`);
                  setMbDashboard(res);
                  showNotice("Proposta comercial gerada e enviada para aprovação humana!");
                } catch (err: any) {
                  showNotice(err?.message || "Erro ao gerar proposta comercial.");
                }
              }}
              className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
            >
              Gerar Proposta Comercial (Aguardará Sua Aprovação)
            </button>
          </section>

          <section className="lg:col-span-6 ug-card rounded-xl overflow-hidden text-xs">
            <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] flex items-center justify-between">
              <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">
                Propostas Emitidas ({(mbDashboard.proposals || []).length})
              </h4>
              <span className="text-[11px] text-[var(--ug-text-muted)]">Abertura segura via Blob</span>
            </div>
            {(mbDashboard.proposals || []).length === 0 ? (
              <div className="p-4">
                <EmptyState
                  title="Nenhuma proposta gerada ainda"
                  description="Preencha os campos ao lado para emitir sua primeira proposta em PDF."
                />
              </div>
            ) : (
              <div className="divide-y divide-white/[0.05] max-h-[420px] overflow-y-auto">
                {(mbDashboard.proposals || []).map((p: any) => (
                  <div key={p.id} className="px-5 py-3.5 flex justify-between items-center gap-3">
                    <div className="min-w-0">
                      <div className="font-semibold text-[var(--ug-text-primary)] truncate">
                        {p.proposal_number} • {p.client_company}
                      </div>
                      <div className="text-[var(--ug-text-muted)] tabular-nums mt-0.5">
                        Setup: R$ {p.setup_price_brl} • MRR: R$ {p.monthly_price_brl}/mês •{" "}
                        <span className={p.status === "ACCEPTED" ? "text-emerald-400 font-medium" : "text-amber-300 font-medium"}>
                          {p.status === "ACCEPTED" ? "Aprovada & Fechada" : p.status === "PENDING_APPROVAL" ? "Aguardando Aprovação" : p.status}
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-1.5 shrink-0">
                      <button
                        type="button"
                        onClick={async () => {
                          try {
                            const hdrs: Record<string, string> = {};
                            if (token) hdrs["Authorization"] = `Bearer ${token}`;
                            if (activeTenantId) hdrs["X-Tenant-Id"] = String(activeTenantId);
                            const resp = await fetch(p.pdf_url, { headers: hdrs });
                            if (!resp.ok) {
                              showNotice(`Falha ao abrir PDF da proposta (HTTP ${resp.status}).`);
                              return;
                            }
                            const htmlText = await resp.text();
                            const blob = new Blob([htmlText], { type: "text/html;charset=utf-8" });
                            const blobUrl = URL.createObjectURL(blob);
                            window.open(blobUrl, "_blank", "noopener,noreferrer");
                            setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
                          } catch (err: any) {
                            showNotice(err?.message || "Erro ao carregar PDF da proposta.");
                          }
                        }}
                        className="px-2.5 py-1 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.06] text-indigo-400 font-medium"
                      >
                        PDF
                      </button>
                      {p.status !== "ACCEPTED" && (
                        <button
                          type="button"
                          onClick={async () => {
                            try {
                              await apiFetch(`/api/v1/commercial/proposals/${p.id}/status`, {
                                method: "PUT",
                                body: JSON.stringify({ status: "ACCEPTED", owner_approve: true }),
                              });
                              const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`);
                              setMbDashboard(res);
                              showNotice(`Proposta ${p.proposal_number} aprovada e fechada!`);
                            } catch (err: any) {
                              showNotice(err?.message || "Erro ao aprovar proposta.");
                            }
                          }}
                          className="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium"
                        >
                          Aprovar &amp; Fechar
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      )}

      {subSection === "servicos" && (
        <section className="ug-card rounded-xl divide-y divide-white/[0.05] text-xs">
          {(mbDashboard.services_catalog || []).map((svc: any) => (
            <div key={svc.id} className="p-4 flex flex-col lg:flex-row lg:items-center justify-between gap-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-[var(--ug-text-primary)]">{svc.name}</span>
                  <span className="px-2 py-0.5 rounded bg-white/[0.05] text-[10px] text-[var(--ug-text-muted)]">
                    {svc.business_unit_code}
                  </span>
                </div>
                <p className="text-[11px] text-[var(--ug-text-muted)]">{svc.problem_solved}</p>
              </div>
              <div className="flex flex-wrap items-center gap-4 shrink-0 tabular-nums">
                <div className="text-right">
                  <div className="text-[11px] text-[var(--ug-text-muted)]">Custo ({svc.pricing_calculator.dev_hours_estimated}h)</div>
                  <div className="text-[var(--ug-text-secondary)]">R$ {svc.pricing_calculator.estimated_cost_brl}</div>
                </div>
                <div className="text-right">
                  <div className="text-[11px] text-[var(--ug-text-muted)]">Setup • MRR</div>
                  <div className="font-semibold text-emerald-400">
                    R$ {svc.pricing_calculator.configured_price_brl} • R$ {svc.pricing_calculator.recurring_monthly_brl}/mês
                  </div>
                </div>
                <button
                  type="button"
                  onClick={async () => {
                    await apiFetch(`/api/v1/commercial/services/${svc.id}/pricing`, {
                      method: "PUT",
                      body: JSON.stringify({ owner_approve_pricing: true }),
                    });
                    const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`);
                    setMbDashboard(res);
                    showNotice(`Preço de ${svc.service_code} aprovado pelo proprietário!`);
                  }}
                  className="px-3 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-indigo-600 hover:text-white text-[var(--ug-text-primary)] font-medium transition"
                >
                  {svc.pricing_calculator.pricing_approved_by_owner ? "Aprovado ✓" : "Aprovar Tabela"}
                </button>
              </div>
            </div>
          ))}
        </section>
      )}

      {subSection === "unidades" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs">
          <section className="ug-card rounded-xl p-5 space-y-3">
            <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">
              UNION AGENCY — Contas de Clientes
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              <input
                value={agencyClientName}
                onChange={(e) => setAgencyClientName(e.target.value)}
                placeholder="Razão Social Cliente"
                className="px-2.5 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
              />
              <input
                value={agencyBrandName}
                onChange={(e) => setAgencyBrandName(e.target.value)}
                placeholder="Marca"
                className="px-2.5 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
              />
              <select
                value={agencyPlanTier}
                onChange={(e) => setAgencyPlanTier(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
              >
                <option value="STARTER">STARTER</option>
                <option value="PRO">PRO</option>
                <option value="BUSINESS">BUSINESS</option>
                <option value="ENTERPRISE">ENTERPRISE</option>
              </select>
              <button
                type="button"
                onClick={async () => {
                  if (!agencyClientName || !agencyBrandName) return;
                  await apiFetch("/api/v1/agency/clients", {
                    method: "POST",
                    body: JSON.stringify({
                      client_name: agencyClientName,
                      brand_name: agencyBrandName,
                      plan_tier: agencyPlanTier,
                      monthly_retainer_brl: Number(agencyRetainer) || 2900,
                      owner_approved_pricing: true,
                    }),
                  });
                  setAgencyClientName("");
                  setAgencyBrandName("");
                  const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`);
                  setMbDashboard(res);
                  showNotice("Conta isolada adicionada na UNION AGENCY!");
                }}
                className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium"
              >
                + Cliente
              </button>
            </div>
            <div className="divide-y divide-white/[0.05] max-h-48 overflow-y-auto">
              {(mbDashboard.agency_clients || []).map((c: any) => (
                <div key={c.id} className="py-2.5 flex justify-between">
                  <span className="text-[var(--ug-text-primary)]">
                    <strong>{c.brand_name}</strong> ({c.client_name}) • {c.plan_tier}
                  </span>
                  <span className="text-emerald-400 font-semibold tabular-nums">R$ {c.monthly_retainer_brl}/mês</span>
                </div>
              ))}
            </div>
          </section>

          <section className="ug-card rounded-xl p-5 space-y-3">
            <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">
              UNION PARTNERS — Programas de Afiliados
            </h3>
            <div className="divide-y divide-white/[0.05] max-h-56 overflow-y-auto">
              {(mbDashboard.affiliate_operation?.programs || []).map((prog: any) => (
                <div key={prog.id} className="py-2.5 flex justify-between items-center gap-2">
                  <div>
                    <div className="font-medium text-[var(--ug-text-primary)]">{prog.name}</div>
                    <div className="text-[11px] text-[var(--ug-text-muted)]">
                      Comissão Ref: {prog.default_commission_pct}% • Janela: {prog.attribution_window_days}d • {prog.official_api_status}
                    </div>
                  </div>
                  <StatusPill status={prog.approval_status === "ACTIVE" ? "EXECUTED" : "PENDING"} label={prog.approval_status} />
                </div>
              ))}
            </div>
          </section>
        </div>
      )}

      {subSection === "pagamentos" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs">
          <section className="ug-card rounded-xl p-5 space-y-3">
            <div className="flex flex-wrap justify-between items-center gap-2">
              <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">
                Pagamentos (Sandbox Verificado / Webhook HMAC)
              </h3>
              <button
                type="button"
                onClick={async () => {
                  const created = await apiFetch("/api/v1/commercial/payments/charge", {
                    method: "POST",
                    body: JSON.stringify({
                      business_unit_code: "UNION_TECH",
                      client_name: "Cliente Sandbox Executivo",
                      client_company: "Empresa Homologação Ltda",
                      client_email: "financeiro@homologacao.com.br",
                      amount_brl: 4800.0,
                      payment_method: "PIX",
                      sandbox_mode: true,
                      owner_approved: true,
                      data_origin: "TEST",
                    }),
                  });
                  const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`);
                  setMbDashboard(res);
                  showNotice(`Cobrança ${created.external_reference} criada em modo ${created.execution_mode} (PENDING)!`);
                }}
                className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium"
              >
                + Emitir Cobrança Sandbox
              </button>
            </div>
            <p className="text-[11px] text-[var(--ug-text-muted)]">
              Cobrança PENDING nunca entra como receita real; somente confirmação por Webhook HMAC-SHA256 concilia no Financeiro.
            </p>
            <div className="divide-y divide-white/[0.05] max-h-56 overflow-y-auto">
              {(mbDashboard.payments || []).map((pt: any) => (
                <div key={pt.id} className="py-2.5 flex justify-between items-center gap-2">
                  <div>
                    <div className="font-medium text-[var(--ug-text-primary)]">
                      {pt.external_reference} • {pt.client_company || pt.client_name}
                    </div>
                    <div className="text-[var(--ug-text-muted)] tabular-nums">
                      R$ {pt.amount_brl} ({pt.payment_method} • {pt.execution_mode}) • {pt.status}
                    </div>
                  </div>
                  <OriginBadge origin={pt.execution_mode === "SANDBOX" ? "SANDBOX" : "REAL"} />
                </div>
              ))}
            </div>
          </section>

          <section className="ug-card rounded-xl p-5 space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">
                Projetos &amp; Entregas ({(mbDashboard.delivery_projects || []).length})
              </h3>
            </div>
            <div className="divide-y divide-white/[0.05] max-h-64 overflow-y-auto">
              {(mbDashboard.delivery_projects || []).map((dp: any) => (
                <div key={dp.id} className="py-2.5 space-y-1.5">
                  <div className="flex justify-between items-center gap-2">
                    <span className="font-medium text-[var(--ug-text-primary)]">
                      {dp.project_code} • {dp.client_company} ({dp.service_code})
                    </span>
                    <StatusPill status={dp.status === "COMPLETED" ? "EXECUTED" : "PENDING"} label={`${dp.status} (${dp.progress_pct}%)`} />
                  </div>
                  <div className="flex justify-between items-center text-[11px] text-[var(--ug-text-muted)]">
                    <span>Prazo: {dp.due_date} • Validação: {dp.client_validation_status}</span>
                    {dp.status !== "COMPLETED" && (
                      <button
                        type="button"
                        onClick={async () => {
                          await apiFetch(`/api/v1/commercial/delivery-projects/${dp.id}`, {
                            method: "PUT",
                            body: JSON.stringify({
                              status: "COMPLETED",
                              client_validation_status: "APPROVED_BY_CLIENT",
                              client_validation_notes: "Homologado pela diretoria do cliente.",
                            }),
                          });
                          const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`);
                          setMbDashboard(res);
                          showNotice(`Projeto ${dp.project_code} concluído e validado!`);
                        }}
                        className="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium"
                      >
                        Concluir Entrega
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

export function CompetitorsIntelligenceWorkspace({
  competitorsData,
  compName,
  setCompName,
  compUrl,
  setCompUrl,
  apiFetch,
  onReload,
  showNotice,
}: {
  competitorsData: any[];
  compName: string;
  setCompName: (v: string) => void;
  compUrl: string;
  setCompUrl: (v: string) => void;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  showNotice: (msg: string) => void;
}) {
  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      <section className="ug-card rounded-xl p-5 space-y-3">
        <div className="flex items-center justify-between gap-2">
          <div>
            <h3 className="text-sm font-semibold text-[var(--ug-text-primary)] flex items-center gap-2">
              <Radar className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              <span>AI Competitive Intelligence — Análise Ética de Sites Públicos</span>
            </h3>
            <p className="text-xs text-[var(--ug-text-muted)]">
              Respeita robots.txt, bloqueia SSRF e extrai títulos, propostas, headings e sinais públicos reais de preço.
            </p>
          </div>
          <OriginBadge origin="REAL" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <input
            value={compName}
            onChange={(e) => setCompName(e.target.value)}
            placeholder="Nome do Concorrente"
            aria-label="Nome do concorrente"
            className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
          />
          <input
            value={compUrl}
            onChange={(e) => setCompUrl(e.target.value)}
            placeholder="https://concorrente.com.br"
            aria-label="Site do concorrente"
            className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
          />
          <button
            type="button"
            onClick={async () => {
              if (!compName) return;
              try {
                await apiFetch("/api/v1/competitors", {
                  method: "POST",
                  body: JSON.stringify({ name: compName, website_url: compUrl }),
                });
                setCompName("");
                await onReload();
                showNotice("Concorrente analisado respeitando robots.txt!");
              } catch (err: any) {
                showNotice(err?.message || "Erro ao analisar concorrente.");
              }
            }}
            className="py-2 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
          >
            Analisar Concorrente
          </button>
        </div>
      </section>

      {competitorsData.length === 0 ? (
        <EmptyState
          title="Nenhum concorrente monitorado ainda"
          description="Adicione o domínio público de um concorrente acima para extrair posicionamento e diferenciais."
        />
      ) : (
        <div className="ug-card rounded-xl divide-y divide-white/[0.05] text-xs">
          {competitorsData.map((c: any) => (
            <div key={c.id} className="p-5 space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm text-[var(--ug-text-primary)]">{c.name}</span>
                  <span className="text-indigo-400">{c.website_url}</span>
                </div>
                <StatusPill status="EXECUTED" label="robots.txt respeitado" />
              </div>
              <p className="text-[var(--ug-text-secondary)]">{c.positioning_summary}</p>
              <p className="text-[var(--ug-text-muted)]">
                <strong>Sinais Públicos de Preço:</strong> {c.public_pricing_summary}
              </p>
              <div className="pt-2 border-t border-[var(--ug-border-subtle)] space-y-1">
                <div className="font-medium text-emerald-400">Oportunidades de Diferenciação:</div>
                {(c.differentiation_opportunities || []).map((op: string, idx: number) => (
                  <div key={idx} className="text-[var(--ug-text-secondary)]">
                    • {op}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
