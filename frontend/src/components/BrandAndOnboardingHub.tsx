"use client";

import React, { useEffect, useState } from "react";
import { Compass, History, Palette, RotateCcw, ShieldAlert, Sparkles } from "lucide-react";
import { StatusPill } from "@/components/DesignSystem";
import { LegacyMenuId } from "@/lib/navigation";

export function ProgressiveOnboardingWizard({
  apiFetch,
  onReload,
  onNavigate,
  onClose,
  showNotice,
}: {
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  onNavigate: (view: LegacyMenuId) => void;
  onClose?: () => void;
  showNotice: (msg: string) => void;
}) {
  const [obData, setObData] = useState<any>(null);
  const [step, setStep] = useState<number>(1);
  const [busy, setBusy] = useState(false);

  const [name, setName] = useState("");
  const [niche, setNiche] = useState("");
  const [domain, setDomain] = useState("");
  const [desc, setDesc] = useState("");
  const [audience, setAudience] = useState("");
  const [productsStr, setProductsStr] = useState("");
  const [brandName, setBrandName] = useState("");
  const [brandVoice, setBrandVoice] = useState("");
  const [brandDiff, setBrandDiff] = useState("");
  const [primaryColor, setPrimaryColor] = useState("#6366F1");
  const [goals, setGoals] = useState<string[]>([]);

  const loadOb = async () => {
    try {
      const res = await apiFetch("/api/v1/growth-os/onboarding");
      setObData(res);
      setStep(res.current_step || 1);
      const d = res.data || {};
      setName(d.name || "");
      setNiche(d.niche || "");
      setDomain(d.domain || "");
      setDesc(d.brand_description || "");
      setAudience(d.target_audience || "");
      setProductsStr((d.products || []).join(", "));
      setBrandName(d.brand_name || "");
      setBrandVoice(d.brand_voice || "Consultivo, claro e orientado a resultados");
      setBrandDiff(d.brand_differentials || "");
      setPrimaryColor(d.primary_color || "#6366F1");
      setGoals(d.growth_goals || []);
    } catch {
      // silencioso
    }
  };

  useEffect(() => {
    loadOb();
  }, []);

  const saveStep = async (targetStep: number, saveOnly = false, extraData: Record<string, any> = {}, reset = false) => {
    setBusy(true);
    try {
      let payloadData: Record<string, any> = { ...extraData };
      if (targetStep === 1) {
        payloadData = {
          name,
          niche,
          domain,
          brand_description: desc,
          target_audience: audience,
          products: productsStr.split(",").map((s) => s.trim()).filter(Boolean),
        };
      } else if (targetStep === 2) {
        payloadData = {
          brand_name: brandName,
          brand_voice: brandVoice,
          brand_differentials: brandDiff,
          primary_color: primaryColor,
          target_audience: audience,
        };
      } else if (targetStep === 3) {
        payloadData = { growth_goals: goals };
      }

      const res = await apiFetch("/api/v1/growth-os/onboarding", {
        method: "POST",
        body: JSON.stringify({ step: targetStep, save_only: saveOnly, reset_onboarding: reset, data: payloadData }),
      });
      setObData(res);
      setStep(res.current_step || targetStep);
      await onReload();
      showNotice(reset ? "Onboarding reiniciado para a Etapa 1." : saveOnly ? "Progresso salvo!" : `Etapa ${targetStep} concluída!`);
    } catch (e: any) {
      showNotice(e?.message || "Erro ao salvar etapa.");
    } finally {
      setBusy(false);
    }
  };

  const goalOptions = [
    "Gerar leads qualificados",
    "Aumentar vendas",
    "Divulgar site e tráfego",
    "Melhorar SEO no Google",
    "Melhorar retenção",
    "Criar conteúdo consistente",
    "Automatizar tarefas",
  ];

  const stages = obData?.stages || [];
  const pct = Math.round(((step || 1) / 6) * 100);

  return (
    <section
      aria-label="Onboarding Empresarial Progressivo"
      className="ug-card rounded-2xl p-5 space-y-4 ug-fade-in"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Compass className="w-4 h-4 text-indigo-400" aria-hidden="true" />
          <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">
            Onboarding Inteligente em 6 Etapas
          </h3>
          <span className="text-[11px] text-[var(--ug-text-muted)] tabular-nums">Etapa {step} de 6</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={busy}
            onClick={() => saveStep(step, false, {}, true)}
            className="px-2.5 py-1 rounded-md border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] text-[11px] inline-flex items-center gap-1"
          >
            <RotateCcw className="w-3 h-3" aria-hidden="true" />
            <span>Recomeçar</span>
          </button>
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="px-2.5 py-1 rounded-md border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] text-[11px]"
            >
              Fechar
            </button>
          )}
        </div>
      </div>

      {/* Barra de progresso contínua + passos horizontais limpos */}
      <div className="space-y-2">
        <div className="w-full h-1 rounded-full bg-white/[0.06] overflow-hidden">
          <div className="h-full bg-indigo-500 transition-all duration-300" style={{ width: `${pct}%` }} />
        </div>
        <div className="flex items-center gap-3 border-b border-[var(--ug-border-subtle)] overflow-x-auto pb-2">
          {stages.map((st: any) => {
            const active = step === st.step;
            const completed = st.step < (obData?.current_step || 1);
            return (
              <button
                key={st.step}
                type="button"
                onClick={() => setStep(st.step)}
                className={`text-[11px] whitespace-nowrap font-medium transition ${
                  active
                    ? "text-indigo-400 font-semibold"
                    : completed
                    ? "text-emerald-400"
                    : "text-[var(--ug-text-muted)] hover:text-[var(--ug-text-secondary)]"
                }`}
              >
                {st.title}
              </button>
            );
          })}
        </div>
      </div>

      {step === 1 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div>
            <label htmlFor="ob-company" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Nome da Empresa *</label>
            <input id="ob-company" value={name} onChange={(e) => setName(e.target.value)} className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          </div>
          <div>
            <label htmlFor="ob-niche" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Segmento / Nicho *</label>
            <input id="ob-niche" value={niche} onChange={(e) => setNiche(e.target.value)} className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          </div>
          <div>
            <label htmlFor="ob-domain" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Site Oficial</label>
            <input id="ob-domain" value={domain} onChange={(e) => setDomain(e.target.value)} placeholder="https://..." className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          </div>
          <div>
            <label htmlFor="ob-aud" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Quem é seu Público?</label>
            <input id="ob-aud" value={audience} onChange={(e) => setAudience(e.target.value)} className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="ob-products" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Produtos / Serviços (separados por vírgula)</label>
            <input id="ob-products" value={productsStr} onChange={(e) => setProductsStr(e.target.value)} placeholder="Ex.: Cadastro gratuito, Planos destaque" className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="ob-desc" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Descrição simples do negócio</label>
            <textarea id="ob-desc" rows={2} value={desc} onChange={(e) => setDesc(e.target.value)} className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div>
            <label htmlFor="ob-bname" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Nome da Marca *</label>
            <input id="ob-bname" value={brandName} onChange={(e) => setBrandName(e.target.value)} className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          </div>
          <div>
            <label htmlFor="ob-voice" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Tom de Voz</label>
            <input id="ob-voice" value={brandVoice} onChange={(e) => setBrandVoice(e.target.value)} className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          </div>
          <div>
            <label htmlFor="ob-diff" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Diferenciais</label>
            <input id="ob-diff" value={brandDiff} onChange={(e) => setBrandDiff(e.target.value)} placeholder="Ex.: Cadastro em 2 minutos sem taxa inicial" className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
          </div>
          <div>
            <label htmlFor="ob-color" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Cor Principal da Marca</label>
            <input id="ob-color" type="color" value={primaryColor} onChange={(e) => setPrimaryColor(e.target.value)} className="h-9 w-20 rounded bg-[var(--ug-bg)] border border-[var(--ug-border)]" />
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-2.5 text-xs">
          <p className="text-[var(--ug-text-secondary)]">Escolha seus objetivos principais para os próximos 30 dias:</p>
          <div className="flex flex-wrap gap-2">
            {goalOptions.map((g) => {
              const active = goals.includes(g);
              return (
                <button
                  key={g}
                  type="button"
                  onClick={() => setGoals((prev) => (prev.includes(g) ? prev.filter((x) => x !== g) : [...prev, g]))}
                  className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition ${
                    active
                      ? "bg-indigo-600 border-indigo-500 text-white"
                      : "bg-white/[0.03] border-[var(--ug-border)] text-[var(--ug-text-secondary)] hover:text-[var(--ug-text-primary)]"
                  }`}
                >
                  {active ? "✓ " : ""}
                  {g}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {step === 4 && (
        <div className="p-3.5 rounded-xl bg-white/[0.025] border border-[var(--ug-border)] space-y-2 text-xs">
          <div className="font-semibold text-indigo-400">4. Plano Inicial Sugerido</div>
          {obData?.data?.generated_plan ? (
            <ul className="list-disc pl-4 space-y-1 text-[var(--ug-text-secondary)]">
              {(obData.data.generated_plan.steps_30_days || []).map((s: string, i: number) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          ) : (
            <p className="text-[var(--ug-text-secondary)]">
              Clique em &ldquo;Gerar Plano &amp; Avançar&rdquo; abaixo para estruturar seus próximos 30 dias com base na sua marca.
            </p>
          )}
        </div>
      )}

      {step === 5 && (
        <div className="flex flex-wrap gap-2 text-xs">
          <button
            type="button"
            disabled={busy}
            onClick={() => saveStep(5, true, { run_starter_action: "content_batch" })}
            className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium"
          >
            Gerar 15 Conteúdos Iniciais (Sem Publicar)
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => saveStep(5, true, { run_starter_action: "daily_plan" })}
            className="px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium"
          >
            Gerar Plano Diário de Tarefas
          </button>
        </div>
      )}

      {step === 6 && (
        <div className="p-3.5 rounded-xl bg-white/[0.025] border border-[var(--ug-border)] space-y-2 text-xs">
          <div className="font-semibold text-emerald-400">6. Conectar Ferramentas Externas (Opcional)</div>
          <p className="text-[var(--ug-text-secondary)]">
            Você possui <strong>{obData?.data?.connected_integrations_count || 0}</strong> conexão(ões) ativa(s). O restante funciona no Modo Assistido em 1 clique.
          </p>
          <button
            type="button"
            onClick={() => onNavigate("integrations")}
            className="px-3 py-1.5 rounded-md border border-[var(--ug-border)] text-indigo-400 hover:bg-white/[0.04] font-medium"
          >
            Ver Conexões Disponíveis →
          </button>
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-[var(--ug-border)]">
        <div className="flex gap-2">
          {step > 1 && (
            <button
              type="button"
              onClick={() => setStep((s) => s - 1)}
              className="px-3 py-1.5 rounded-lg border border-[var(--ug-border)] text-[var(--ug-text-secondary)] text-xs"
            >
              ← Voltar
            </button>
          )}
          <button
            type="button"
            disabled={busy}
            onClick={() => saveStep(step, true)}
            className="px-3 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] text-xs"
          >
            Salvar e continuar depois
          </button>
        </div>
        <button
          type="button"
          disabled={busy}
          onClick={() => saveStep(step, false)}
          className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
        >
          {step === 4 && !obData?.data?.generated_plan
            ? "Gerar Plano & Avançar →"
            : step === 6
            ? "Concluir Onboarding ✓"
            : "Salvar e Avançar →"}
        </button>
      </div>
    </section>
  );
}

export function BrandIntelligenceCenter({
  apiFetch,
  onReload,
  showNotice,
}: {
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  showNotice: (msg: string) => void;
}) {
  const [brandData, setBrandData] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  const [voice, setVoice] = useState("");
  const [fonts, setFonts] = useState("");
  const [diff, setDiff] = useState("");
  const [allowedTerms, setAllowedTerms] = useState("");
  const [forbiddenTerms, setForbiddenTerms] = useState("");
  const [examples, setExamples] = useState("");

  const loadBrand = async () => {
    try {
      const res = await apiFetch("/api/v1/growth-os/brand");
      setBrandData(res);
      const bp = res.brand_profile || {};
      setVoice(bp.brand_voice || "");
      setFonts(bp.brand_fonts || "");
      setDiff(bp.brand_differentials || "");
      setAllowedTerms(bp.brand_allowed_terms || "");
      setForbiddenTerms(bp.brand_forbidden_terms || "");
      setExamples(bp.brand_examples || "");
    } catch {
      // silencioso
    }
  };

  useEffect(() => {
    loadBrand();
  }, []);

  if (!brandData) return null;
  const bp = brandData.brand_profile || {};
  const audit = brandData.consistency_audit || { consistency_score: 100, checked_items: 0, inconsistencies: [] };

  return (
    <section aria-label="Central de Inteligência de Marca" className="ug-card rounded-2xl p-5 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-[var(--ug-border-subtle)]">
        <div className="space-y-0.5">
          <h3 className="text-sm font-semibold text-[var(--ug-text-primary)] flex items-center gap-2">
            <Palette className="w-4 h-4 text-indigo-400" aria-hidden="true" />
            <span>Central de Inteligência de Marca</span>
          </h3>
          <p className="text-xs text-[var(--ug-text-muted)]">
            Diretrizes únicas lidas por campanhas, textos e auditorias para manter consistência automática.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs">
            <span
              className="w-6 h-6 rounded-md flex items-center justify-center font-bold text-white text-[10px]"
              style={{ backgroundColor: bp.primary_color || "#6366F1" }}
            >
              {(bp.brand_name || "UG").slice(0, 2).toUpperCase()}
            </span>
            <span className="text-[var(--ug-text-secondary)] font-medium">{bp.brand_name}</span>
          </div>
          <StatusPill
            status={audit.consistency_score >= 85 ? "EXECUTED" : "PENDING"}
            label={`Consistência: ${audit.consistency_score}/100`}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        <div>
          <label htmlFor="ug-brand-voice" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Tom de Voz da Marca</label>
          <input id="ug-brand-voice" value={voice} onChange={(e) => setVoice(e.target.value)} className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
        </div>
        <div>
          <label htmlFor="ug-brand-fonts" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Fontes / Tipografia</label>
          <input id="ug-brand-fonts" value={fonts} onChange={(e) => setFonts(e.target.value)} className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
        </div>
        <div>
          <label htmlFor="ug-brand-diff" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Diferenciais Competitivos</label>
          <input id="ug-brand-diff" value={diff} onChange={(e) => setDiff(e.target.value)} placeholder="Ex.: Sem mensalidade inicial, conexão direta com clientes" className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
        </div>
        <div>
          <label htmlFor="ug-brand-allowed" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Termos Recomendados</label>
          <input id="ug-brand-allowed" value={allowedTerms} onChange={(e) => setAllowedTerms(e.target.value)} placeholder="Ex.: cadastro gratuito, orçamento direto" className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
        </div>
        <div className="md:col-span-2">
          <label htmlFor="ug-brand-forbidden" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Termos Proibidos (bloqueio automático de inconsistência)</label>
          <input id="ug-brand-forbidden" value={forbiddenTerms} onChange={(e) => setForbiddenTerms(e.target.value)} className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
        </div>
        <div className="md:col-span-2">
          <label htmlFor="ug-brand-examples" className="block text-[11px] text-[var(--ug-text-secondary)] mb-1">Exemplos de Comunicação Ideal</label>
          <textarea id="ug-brand-examples" rows={2} value={examples} onChange={(e) => setExamples(e.target.value)} placeholder="Ex.: Cadastre seu perfil grátis e receba contatos da sua cidade." className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]" />
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                const res = await apiFetch("/api/v1/growth-os/brand", {
                  method: "PUT",
                  body: JSON.stringify({
                    brand_voice: voice,
                    brand_fonts: fonts,
                    brand_differentials: diff,
                    brand_allowed_terms: allowedTerms,
                    brand_forbidden_terms: forbiddenTerms,
                    brand_examples: examples,
                  }),
                });
                setBrandData(res);
                await onReload();
                showNotice("Nova versão da Central de Marca salva e auditada!");
              } catch (e: any) {
                showNotice(e?.message || "Erro ao salvar Brand Intelligence.");
              } finally {
                setBusy(false);
              }
            }}
            className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
          >
            Salvar Versão da Marca
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                const res = await apiFetch("/api/v1/growth-os/brand/audit", { method: "POST" });
                setBrandData((prev: any) => ({ ...prev, consistency_audit: res }));
                showNotice(`Auditoria concluída: consistência ${res.consistency_score}/100 (${res.checked_items} itens verificados).`);
              } finally {
                setBusy(false);
              }
            }}
            className="px-3.5 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] text-xs font-medium inline-flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
            <span>Detectar Inconsistências Agora</span>
          </button>
        </div>

        {(brandData.versions || []).length > 0 && (
          <div className="text-[11px] text-[var(--ug-text-muted)] flex items-center gap-2 flex-wrap tabular-nums">
            <History className="w-3.5 h-3.5" aria-hidden="true" />
            {brandData.versions.slice(0, 3).map((v: any) => (
              <span key={v.id} className="px-2 py-0.5 rounded bg-white/[0.04]">
                v{v.version_number} ({v.consistency_score}/100)
              </span>
            ))}
          </div>
        )}
      </div>

      {(audit.inconsistencies || []).length > 0 && (
        <div className="pt-3 border-t border-[var(--ug-border-subtle)] space-y-1.5 text-xs">
          <div className="font-medium text-amber-400 flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Inconsistências detectadas ({audit.inconsistencies.length})</span>
          </div>
          {audit.inconsistencies.map((inc: any, idx: number) => (
            <div key={idx} className="text-[11px] text-[var(--ug-text-secondary)]">
              <strong className="text-[var(--ug-text-primary)]">[{inc.source}]</strong> {inc.issue}{" "}
              <span className="text-indigo-400">→ {inc.recommendation}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
