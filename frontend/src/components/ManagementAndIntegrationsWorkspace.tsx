"use client";

import React from "react";
import { ExternalLink, Link2Off, ShieldCheck } from "lucide-react";
import { MetricStrip, OriginBadge, PlainOrientationBar, StatusPill } from "@/components/DesignSystem";
import { AnalyticsAttributionPanel } from "@/components/ConversationalAutomationAndAnalytics";
import { BrandIntelligenceCenter } from "@/components/BrandAndOnboardingHub";
import { PlansAndUsagePanel } from "@/components/AIEnginesHubWorkspace";
import { AuditCenterWorkspace } from "@/components/AuditCenterWorkspace";

export function FinanceAndReportsWorkspace({
  mode,
  financeData,
  finType,
  setFinType,
  finAmount,
  setFinAmount,
  finDesc,
  setFinDesc,
  finOrigin,
  setFinOrigin,
  reportsData,
  analyticsAttrData,
  apiFetch,
  onReload,
  showNotice,
}: any) {
  if (mode === "finance") {
    return (
      <div className="space-y-5 max-w-7xl mx-auto ug-fade-in">
        <MetricStrip
          items={[
            {
              key: "rev",
              label: "Receita Real / Importada",
              value: `R$ ${financeData.kpis.real_revenue.toLocaleString("pt-BR")}`,
              origin: "IMPORTED",
              source: "Razão Financeiro",
              period: "Acumulado",
            },
            {
              key: "prof",
              label: "Lucro Líquido Real",
              value: `R$ ${financeData.kpis.real_profit.toLocaleString("pt-BR")}`,
              origin: "REAL",
              source: "PostgreSQL",
              period: "Líquido",
            },
            {
              key: "roi",
              label: "Margem / ROI / ROAS",
              value: `${financeData.kpis.margin_pct}% | ${financeData.kpis.roas_multiplier}x`,
              subtext: `ROI: ${financeData.kpis.roi_pct}%`,
              origin: "REAL",
            },
            {
              key: "cac",
              label: "CAC / Ticket Médio",
              value: `R$ ${financeData.kpis.cac_brl} / R$ ${financeData.kpis.average_ticket_brl}`,
              origin: "ESTIMATED",
            },
          ]}
        />

        <div className="ug-card rounded-xl p-5 space-y-4">
          <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">
            Registrar / Importar Lançamento Financeiro (Sem Mistura de Simulações)
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
            <select value={finType} onChange={(e) => setFinType(e.target.value)} aria-label="Tipo financeiro" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]">
              <option value="REVENUE">Receita (REVENUE)</option>
              <option value="EXPENSE">Despesa Operacional (EXPENSE)</option>
              <option value="AD_SPEND">Investimento em Mídia (AD_SPEND)</option>
            </select>
            <input type="number" value={finAmount} onChange={(e) => setFinAmount(e.target.value)} placeholder="Valor R$" aria-label="Valor financeiro" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)] tabular-nums" />
            <select value={finOrigin} onChange={(e) => setFinOrigin(e.target.value)} aria-label="Origem do dado" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]">
              <option value="REAL">DADO REAL</option>
              <option value="IMPORTED">DADO IMPORTADO</option>
              <option value="ESTIMATED">ESTIMATIVA</option>
              <option value="GOAL">META</option>
            </select>
            <input value={finDesc} onChange={(e) => setFinDesc(e.target.value)} placeholder="Descrição" aria-label="Descrição do lançamento" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
            <button
              type="button"
              onClick={async () => {
                await apiFetch("/api/v1/finance/records", {
                  method: "POST",
                  body: JSON.stringify({
                    period_date: new Date().toISOString().slice(0, 10),
                    record_type: finType,
                    amount: Number(finAmount) || 0,
                    data_origin: finOrigin,
                    description: finDesc,
                  }),
                });
                await onReload();
                showNotice("Lançamento registrado!");
              }}
              className="py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
            >
              Registrar Lançamento
            </button>
          </div>
        </div>

        <div className="ug-card rounded-xl overflow-hidden">
          <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
            Razão de Lançamentos Financeiros
          </div>
          <div className="divide-y divide-white/[0.05]">
            {financeData.records.map((r: any) => (
              <div key={r.id} className="px-5 py-3 flex items-center justify-between text-xs gap-2">
                <div className="text-[var(--ug-text-secondary)]">
                  <strong className="text-[var(--ug-text-primary)]">{r.record_type}</strong> • {r.description} ({r.period_date})
                </div>
                <div className="flex items-center gap-3 shrink-0 tabular-nums">
                  <span className="font-semibold text-[var(--ug-text-primary)]">R$ {r.amount.toLocaleString("pt-BR")}</span>
                  <OriginBadge origin={r.data_origin} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      <AnalyticsAttributionPanel attribution={analyticsAttrData} />
      <div className="ug-card rounded-2xl overflow-hidden">
        <div className="px-5 py-4 border-b border-[var(--ug-border-subtle)] flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">Relatório Executivo Consolidado</h3>
            <p className="text-xs text-[var(--ug-text-muted)] mt-0.5">
              Empresa: {reportsData.tenant?.brand_name || reportsData.tenant?.name || "—"} • Plano: {reportsData.tenant?.plan_tier || "—"}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={async () => {
                const bkp = await apiFetch("/api/v1/system/backup", { method: "POST" });
                showNotice(`Backup criado: ${bkp.backup_file} (${bkp.size_bytes} bytes)`);
              }}
              className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
            >
              Gerar Snapshot &amp; Backup Agora
            </button>
            <button
              type="button"
              onClick={async () => {
                const res = await apiFetch("/api/v1/system/backup/test-restore", { method: "POST" });
                showNotice(
                  res.status === "RESTORE_VERIFIED" || res.restore_test_passed
                    ? `Restauração isolada OK (${res.total_restored_records ?? res.records_checked ?? 0} registros, SHA-256 ${String(res.sha256 || "").slice(0, 10)})`
                    : `Teste de restauração: ${res.status || "verificar logs"}`
                );
              }}
              className="px-3.5 py-1.5 rounded-lg border border-emerald-500/35 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs font-medium"
            >
              Testar Restauração Isolada (SHA-256)
            </button>
          </div>
        </div>

        <MetricStrip
          items={[
            {
              key: "rec",
              label: "Receita Real Confirmada",
              value: `R$ ${Number(reportsData.financial_performance?.real_revenue || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`,
              origin: "REAL",
              source: "Finance Engine",
            },
            {
              key: "prof",
              label: "Lucro Real / Margem",
              value: `R$ ${Number(reportsData.financial_performance?.real_profit || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`,
              subtext: `${Number(reportsData.financial_performance?.margin_pct || 0)}% margem`,
              origin: "REAL",
            },
            {
              key: "ld",
              label: "Leads Reais & Conversão",
              value: `${reportsData.financial_performance?.leads_total ?? 0} leads`,
              subtext: `${reportsData.financial_performance?.conversion_rate_pct ?? 0}% conv.`,
              origin: "REAL",
            },
            {
              key: "int",
              label: "Conexões Externas",
              value: `${(reportsData.integrations_summary?.connected || []).length} ativas`,
              subtext: `${(reportsData.integrations_summary?.pending_credentials || []).length} opcionais`,
              origin: "REAL",
            },
          ]}
        />

        <details className="border-t border-[var(--ug-border-subtle)]">
          <summary className="px-5 py-3 text-xs font-semibold text-[var(--ug-text-secondary)] cursor-pointer hover:text-[var(--ug-text-primary)]">
            Ver Detalhes Técnicos Completos (JSON de Auditoria)
          </summary>
          <pre className="p-4 border-t border-[var(--ug-border-subtle)] text-xs text-[var(--ug-text-secondary)] overflow-x-auto bg-[var(--ug-bg)]">
            {JSON.stringify(reportsData, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}

export function IntegrationsAndSettingsWorkspace({
  mode,
  meData,
  integrationsData,
  intgStatusFilter,
  setIntgStatusFilter,
  credInputs,
  credFieldInputs,
  setCredFieldInputs,
  plansOverview,
  editCompanyName,
  setEditCompanyName,
  editBrandName,
  setEditBrandName,
  editDomain,
  setEditDomain,
  editNiche,
  setEditNiche,
  editAudience,
  setEditAudience,
  newTenantName,
  setNewTenantName,
  auditData,
  apiFetch,
  onReload,
  showNotice,
}: any) {
  if (mode === "integrations") {
    const filtered = (integrationsData || []).filter((intg: any) => {
      if (intgStatusFilter === "CONNECTED") return intg.status === "CONNECTED";
      if (intgStatusFilter === "PENDING") return intg.status !== "CONNECTED";
      return true;
    });

    return (
      <div className="space-y-5 max-w-6xl mx-auto ug-fade-in">
        <PlainOrientationBar
          whatIsIt="Central de Conexões Oficiais & OAuth 2.0 (18 Plataformas)"
          whyUseIt="Habilita leitura real de métricas e publicação externa quando você autorizar com chaves oficiais"
          nextStep="Sem OAuth conectado, todas as áreas continuam seguras no Modo Assistido 1-Clique"
        />

        <div className="flex flex-wrap items-end justify-between gap-3 pb-3 border-b border-[var(--ug-border)]">
          <div>
            <h3 className="text-base font-semibold text-[var(--ug-text-primary)]">
              Conectar Ferramentas Externas (Status Real)
            </h3>
            <p className="text-xs text-[var(--ug-text-muted)]">
              Tokens criptografados em Fernet AES-128. Nenhuma conexão externa é simulada.
            </p>
          </div>
          <div className="flex items-center gap-1.5" role="group" aria-label="Filtrar status de integrações">
            {[
              { id: "ALL", label: `Todas (${integrationsData.length})` },
              { id: "CONNECTED", label: `Conectadas (${integrationsData.filter((i: any) => i.status === "CONNECTED").length})` },
              { id: "PENDING", label: `Pendentes (${integrationsData.filter((i: any) => i.status !== "CONNECTED").length})` },
            ].map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => setIntgStatusFilter(f.id as any)}
                className={`px-3 py-1 rounded-lg text-xs font-medium border transition ${
                  intgStatusFilter === f.id
                    ? "bg-indigo-600 text-white border-indigo-500"
                    : "border-[var(--ug-border)] text-[var(--ug-text-secondary)] hover:bg-white/[0.04]"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((intg: any) => {
            const reqFields: string[] = intg.setup_guide?.required_credentials || ["api_key"];
            const provMap = credFieldInputs[intg.provider_key] || {};
            const isConn = intg.status === "CONNECTED";
            const hasOAuth = Boolean(intg.setup_guide?.oauth_authorize_url);
            return (
              <div key={intg.provider_key} className="ug-card rounded-xl p-4 space-y-2.5 text-xs">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-[var(--ug-text-primary)] text-sm">{intg.provider_name}</span>
                  <StatusPill
                    status={isConn ? "EXECUTED" : intg.status === "ERROR" ? "FAILED" : "NEEDS_CREDENTIALS"}
                    label={isConn ? "Conectada" : intg.status === "ERROR" ? "Falha na Conexão" : "Aguardando Conexão"}
                  />
                </div>
                <div className="text-[var(--ug-text-secondary)]">
                  <strong>O que habilita:</strong> {intg.setup_guide.features_unlocked}
                </div>
                <div className="text-[var(--ug-text-muted)]">
                  <strong>Onde obter:</strong> {intg.setup_guide.where_to_obtain}
                </div>
                {intg.last_error && <div className="text-amber-400 text-[11px]">{intg.last_error}</div>}
                <div className="grid grid-cols-1 gap-2 pt-1">
                  {reqFields.map((rk) => {
                    const inputId = `ug-intg-${intg.provider_key}-${rk}`;
                    return (
                      <div key={rk}>
                        <label htmlFor={inputId} className="block text-[10px] font-medium text-[var(--ug-text-secondary)] mb-0.5">
                          {rk.replace(/_/g, " ").toUpperCase()}
                        </label>
                        <input
                          id={inputId}
                          type={rk.includes("secret") || rk.includes("token") || rk.includes("key") ? "password" : "text"}
                          value={provMap[rk] ?? ""}
                          onChange={(e) =>
                            setCredFieldInputs({
                              ...credFieldInputs,
                              [intg.provider_key]: { ...provMap, [rk]: e.target.value },
                            })
                          }
                          placeholder={`Ex.: cole ${rk}`}
                          className="w-full px-2.5 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                        />
                      </div>
                    );
                  })}
                </div>
                <div className="flex flex-wrap gap-2 pt-1">
                  <button
                    type="button"
                    onClick={async () => {
                      const credsObj: Record<string, string> = {};
                      const missing: string[] = [];
                      for (const rk of reqFields) {
                        const v = (provMap[rk] || credInputs[intg.provider_key] || "").trim();
                        if (!v) missing.push(rk);
                        credsObj[rk] = v;
                      }
                      if (missing.length > 0) {
                        showNotice(`Preencha: ${missing.join(", ")}`);
                        return;
                      }
                      const r = await apiFetch("/api/v1/integrations/connect", {
                        method: "POST",
                        body: JSON.stringify({ provider_key: intg.provider_key, credentials: credsObj }),
                      });
                      await onReload();
                      showNotice(`${intg.provider_name}: ${r.message}`);
                    }}
                    className="flex-1 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
                  >
                    Salvar &amp; Testar Conexão
                  </button>
                  <button
                    type="button"
                    onClick={async () => {
                      const r = await apiFetch(`/api/v1/integrations/${intg.provider_key}/test`, { method: "POST" });
                      await onReload();
                      showNotice(`${intg.provider_name}: ${r.message}`);
                    }}
                    className="px-3 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-primary)] font-medium"
                  >
                    Testar Conexão
                  </button>
                  {hasOAuth && (
                    <button
                      type="button"
                      onClick={async () => {
                        const res = await apiFetch(`/api/v1/integrations/oauth/${intg.provider_key}/start`);
                        if (res.status === "READY" && res.authorize_url) {
                          window.open(res.authorize_url, "_blank", "noopener,noreferrer");
                        } else {
                          showNotice(res.message || "Cadastre client_id e client_secret primeiro.");
                        }
                      }}
                      className="px-3 py-1.5 rounded-lg border border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/10 font-medium inline-flex items-center gap-1"
                    >
                      <ExternalLink className="w-3 h-3" aria-hidden="true" />
                      <span>OAuth 2.0</span>
                    </button>
                  )}
                  {isConn && intg.provider_key !== "google_pagespeed_insights" && (
                    <button
                      type="button"
                      onClick={async () => {
                        await apiFetch(`/api/v1/integrations/${intg.provider_key}/disconnect`, { method: "POST" });
                        await onReload();
                        showNotice(`${intg.provider_name} desconectada.`);
                      }}
                      className="px-2.5 py-1.5 rounded-lg border border-red-500/30 text-red-300 hover:bg-red-500/10 inline-flex items-center gap-1"
                      aria-label={`Desconectar ${intg.provider_name}`}
                    >
                      <Link2Off className="w-3 h-3" aria-hidden="true" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (mode === "audit" && auditData) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
        <AuditCenterWorkspace
          auditData={auditData}
          apiFetch={apiFetch}
          onReload={onReload}
          showNotice={showNotice}
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="ug-card rounded-xl overflow-hidden">
            <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
              Logs de Execução dos Agentes de IA
            </div>
            <div className="divide-y divide-white/[0.05] max-h-[520px] overflow-y-auto text-xs">
              {auditData.agent_execution_logs.map((l: any) => (
                <div key={l.id} className="px-5 py-3 space-y-1">
                  <div className="flex justify-between font-semibold text-indigo-400">
                    <span>{l.agent_name}</span>
                    <span className="tabular-nums">{l.duration_ms}ms • {l.status}</span>
                  </div>
                  <div className="text-[var(--ug-text-secondary)]">Tarefa: {l.task_name} • {l.workflow_run_id}</div>
                  <div className="text-[10px] text-[var(--ug-text-muted)]">{l.created_at}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="ug-card rounded-xl overflow-hidden">
            <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
              Trilha de Auditoria &amp; Segurança
            </div>
            <div className="divide-y divide-white/[0.05] max-h-[520px] overflow-y-auto text-xs">
              {auditData.audit_logs.map((a: any) => (
                <div key={a.id} className="px-5 py-3 space-y-1">
                  <div className="flex justify-between font-semibold text-emerald-400">
                    <span>{a.action}</span>
                    <span className="tabular-nums">IP: {a.ip_address}</span>
                  </div>
                  <div className="text-[var(--ug-text-secondary)]">Ator: {a.actor} • {a.resource_type} #{a.resource_id}</div>
                  <div className="text-[10px] text-[var(--ug-text-muted)]">{a.created_at}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      <div className="ug-card rounded-xl p-5 space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">Identidade da Empresa &amp; Marca Ativa</h3>
          <p className="text-xs text-[var(--ug-text-muted)] mt-0.5">
            Preencha como sua empresa atua para que todos os agentes, propostas e conteúdos usem sua marca corretamente.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
          <div>
            <label htmlFor="ug-edit-company-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Nome Oficial da Empresa *
            </label>
            <input id="ug-edit-company-input" value={editCompanyName} onChange={(e) => setEditCompanyName(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]" />
          </div>
          <div>
            <label htmlFor="ug-edit-brand-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Nome da Marca (exibição) *
            </label>
            <input id="ug-edit-brand-input" value={editBrandName} onChange={(e) => setEditBrandName(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]" />
          </div>
          <div>
            <label htmlFor="ug-edit-domain-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Site / Domínio Principal
            </label>
            <input id="ug-edit-domain-input" value={editDomain} onChange={(e) => setEditDomain(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]" />
          </div>
          <div>
            <label htmlFor="ug-edit-niche-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Nicho / Segmento de Atuação
            </label>
            <input id="ug-edit-niche-input" value={editNiche} onChange={(e) => setEditNiche(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]" />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="ug-edit-audience-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
              Público-Alvo Principal (quem compra de você)
            </label>
            <input id="ug-edit-audience-input" value={editAudience} onChange={(e) => setEditAudience(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]" />
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <span className="text-[11px] text-[var(--ug-text-muted)]">
            Empresa ativa: <strong className="text-indigo-400">{meData.active_tenant?.brand_name}</strong> • Alterações isoladas neste workspace.
          </span>
          <button
            type="button"
            onClick={async () => {
              if (!editCompanyName.trim() || !editBrandName.trim()) {
                showNotice("Preencha o Nome Oficial e o Nome da Marca.");
                return;
              }
              await apiFetch("/api/v1/tenants/current", {
                method: "PUT",
                body: JSON.stringify({
                  name: editCompanyName.trim(),
                  brand_name: editBrandName.trim(),
                  domain: editDomain.trim(),
                  niche: editNiche.trim(),
                  target_audience: editAudience.trim(),
                }),
              });
              await onReload();
              showNotice("Identidade atualizada com sucesso!");
            }}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
          >
            Salvar Identidade da Empresa
          </button>
        </div>
      </div>

      <div className="ug-card rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-semibold text-[var(--ug-text-primary)] flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-indigo-400" aria-hidden="true" />
          <span>Nível de Autonomia Operacional da IA</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { level: 1, title: "NÍVEL 1 — ASSISTIDO", desc: "A IA analisa e recomenda; você executa." },
            { level: 2, title: "NÍVEL 2 — SEMIAUTÔNOMO (Padrão Recomendado)", desc: "A IA prepara e pede confirmação antes de ações externas." },
            { level: 3, title: "NÍVEL 3 — AUTÔNOMO", desc: "Executa atividades internas autorizadas dentro dos limites de segurança." },
          ].map((lvl) => (
            <button
              type="button"
              key={lvl.level}
              onClick={async () => {
                await apiFetch("/api/v1/tenants/current", { method: "PUT", body: JSON.stringify({ autonomy_default_level: lvl.level }) });
                await onReload();
                showNotice(`Autonomia atualizada para Nível ${lvl.level}!`);
              }}
              className={`p-4 rounded-xl border text-left transition ${
                meData.active_tenant.autonomy_default_level === lvl.level
                  ? "bg-indigo-600/15 border-indigo-500 text-[var(--ug-text-primary)]"
                  : "bg-[var(--ug-bg)] border-[var(--ug-border)] text-[var(--ug-text-secondary)]"
              }`}
            >
              <div className="font-semibold text-xs mb-1">{lvl.title}</div>
              <div className="text-[11px] text-[var(--ug-text-muted)]">{lvl.desc}</div>
            </button>
          ))}
        </div>
      </div>

      <PlansAndUsagePanel meData={meData} plansOverview={plansOverview} apiFetch={apiFetch} onReload={onReload} showNotice={showNotice} />
      <BrandIntelligenceCenter apiFetch={apiFetch} onReload={onReload} showNotice={showNotice} />

      <div className="ug-card rounded-xl p-5 space-y-3">
        <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">Nova Empresa / Unidade (Isolamento Completo)</h3>
        <div className="flex flex-wrap gap-3">
          <input value={newTenantName} onChange={(e) => setNewTenantName(e.target.value)} placeholder="Ex.: Nova Unidade Comercial Ltda" aria-label="Nome da Nova Empresa ou Filial" className="flex-1 min-w-[220px] px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]" />
          <button
            type="button"
            onClick={async () => {
              if (!newTenantName.trim()) return;
              await apiFetch("/api/v1/tenants", { method: "POST", body: JSON.stringify({ name: newTenantName.trim(), brand_name: newTenantName.trim() }) });
              setNewTenantName("");
              await onReload();
              showNotice("Nova empresa criada com isolamento completo!");
            }}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
          >
            Adicionar Empresa
          </button>
        </div>
      </div>
    </div>
  );
}

export function CustomerSuccessWorkspace({
  csData,
  csName,
  setCsName,
  csEmail,
  setCsEmail,
  csNps,
  setCsNps,
  csText,
  setCsText,
  apiFetch,
  onReload,
  showNotice,
}: any) {
  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      <MetricStrip
        items={[
          { key: "nps", label: "NPS Médio", value: `${csData.summary.average_nps} / 10`, origin: "REAL", source: "CS Engine" },
          { key: "csat", label: "CSAT Médio", value: `${csData.summary.average_csat} / 5`, origin: "REAL", source: "CS Engine" },
          { key: "churn", label: "Risco de Churn", value: csData.summary.high_churn_risk_count, origin: "REAL" },
          { key: "upsell", label: "Oportunidades Upsell", value: csData.summary.upsell_ready_count, origin: "ESTIMATED" },
        ]}
      />

      <div className="ug-card rounded-xl p-5 space-y-4">
        <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">
          Registrar Pesquisa de Satisfação (NPS / CSAT) &amp; Detectar Risco ou Upsell
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
          <input value={csName} onChange={(e) => setCsName(e.target.value)} placeholder="Nome do Cliente" aria-label="Nome do Cliente CS" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          <input value={csEmail} onChange={(e) => setCsEmail(e.target.value)} placeholder="E-mail do Cliente" aria-label="E-mail do Cliente CS" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          <select value={csNps} onChange={(e) => setCsNps(e.target.value)} aria-label="Nota NPS" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]">
            {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0].map((n) => (
              <option key={n} value={n}>Nota NPS: {n}</option>
            ))}
          </select>
          <input value={csText} onChange={(e) => setCsText(e.target.value)} placeholder="Feedback do cliente" aria-label="Feedback do cliente" className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          <button
            type="button"
            onClick={async () => {
              if (!csName || !csText) return;
              await apiFetch("/api/v1/customer-success/feedbacks", {
                method: "POST",
                body: JSON.stringify({
                  customer_name: csName,
                  customer_email: csEmail,
                  nps_score: Number(csNps),
                  csat_score: Number(csNps) >= 8 ? 5 : 3,
                  feedback_text: csText,
                }),
              });
              setCsName("");
              setCsEmail("");
              setCsText("");
              await onReload();
              showNotice("Feedback analisado pelo AI Customer Success!");
            }}
            className="py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
          >
            Analisar Feedback
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {csData.feedbacks.map((f: any) => (
          <div key={f.id} className="ug-card rounded-xl p-4 text-xs space-y-1.5">
            <div className="flex items-center justify-between gap-2">
              <span className="font-semibold text-[var(--ug-text-primary)]">{f.customer_name}</span>
              <StatusPill status={f.churn_risk === "HIGH" ? "FAILED" : "EXECUTED"} label={`NPS ${f.nps_score} • Risco: ${f.churn_risk}`} />
            </div>
            <p className="text-[var(--ug-text-secondary)]">&ldquo;{f.feedback_text}&rdquo;</p>
            <div className="text-indigo-400"><strong>Ação de Retenção:</strong> {f.retention_suggestion}</div>
            <div className="text-emerald-400"><strong>Oportunidade Comercial (Upsell):</strong> {f.upsell_opportunity}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
