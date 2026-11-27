"use client";

import React, { useEffect, useState } from "react";
import { CheckCircle2, Cpu, KeyRound, ShieldCheck, Sparkles, TrendingUp } from "lucide-react";
import { FilterTabBar, MetricStrip, OriginBadge, StatusPill } from "@/components/DesignSystem";

export function AIEnginesHubWorkspace({
  aiEnginesConfig,
  setAiEnginesConfig,
  aiHubSubmenu,
  setAiHubSubmenu,
  aiKeyInputs,
  setAiKeyInputs,
  aiEndpointInputs,
  setAiEndpointInputs,
  aiGenTopic,
  setAiGenTopic,
  aiGenPlatform,
  aiGenMode,
  setAiGenMode,
  aiPieceType,
  setAiPieceType,
  aiImgPrompt,
  setAiImgPrompt,
  aiImgMode,
  setAiImgMode,
  aiVidPrompt,
  setAiVidPrompt,
  aiVidStage,
  setAiVidStage,
  aiGenLoading,
  setAiGenLoading,
  aiGenResult,
  setAiGenResult,
  apiFetch,
  showNotice,
}: {
  aiEnginesConfig: any;
  setAiEnginesConfig: (v: any) => void;
  aiHubSubmenu: string;
  setAiHubSubmenu: (v: string) => void;
  aiKeyInputs: Record<string, string>;
  setAiKeyInputs: (v: Record<string, string>) => void;
  aiEndpointInputs: Record<string, string>;
  setAiEndpointInputs: (v: Record<string, string>) => void;
  aiGenTopic: string;
  setAiGenTopic: (v: string) => void;
  aiGenPlatform: string;
  aiGenMode: string;
  setAiGenMode: (v: string) => void;
  aiPieceType: string;
  setAiPieceType: (v: string) => void;
  aiImgPrompt: string;
  setAiImgPrompt: (v: string) => void;
  aiImgMode: string;
  setAiImgMode: (v: string) => void;
  aiVidPrompt: string;
  setAiVidPrompt: (v: string) => void;
  aiVidStage: string;
  setAiVidStage: (v: string) => void;
  aiGenLoading: boolean;
  setAiGenLoading: (v: boolean) => void;
  aiGenResult: any;
  setAiGenResult: (v: any) => void;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  showNotice: (msg: string) => void;
}) {
  const defaultProviderKey = aiEnginesConfig?.configuration?.default_provider_key || "gemini";
  const defaultProviderObj = (aiEnginesConfig?.providers || []).find((p: any) => p.provider_key === defaultProviderKey);
  const hasRealKey = Boolean(defaultProviderObj?.has_credential);

  return (
    <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
      <section className="ug-card rounded-xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <StatusPill
                status={hasRealKey ? "EXECUTED" : "PENDING"}
                label={hasRealKey ? "GEMINI CONECTADO (CHAVE ATIVA)" : "AGUARDANDO CHAVE GRATUITA (BYO-KEY)"}
              />
              <span className="px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 text-[11px] font-medium">
                MODO: {aiEnginesConfig.configuration?.cost_policy_mode || "FREE_ONLY"}
              </span>
            </div>
            <h3 className="text-base font-semibold text-[var(--ug-text-primary)]">
              UNION AI ENGINE HUB — Central Multimotor com Governança de Custos
            </h3>
            <p className="text-xs text-[var(--ug-text-muted)]">
              Motor Prioritário: <strong>{defaultProviderKey.toUpperCase()}</strong> ({aiEnginesConfig.configuration?.default_text_model}) • Trava gratuita ativa por padrão.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setAiHubSubmenu("providers")}
              className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
            >
              CONFIGURAR GEMINI
            </button>
            <button
              type="button"
              onClick={() => setAiHubSubmenu("tests")}
              className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
            >
              TESTAR MOTOR
            </button>
            <button
              type="button"
              onClick={() => setAiHubSubmenu("campaigns_ai")}
              className="px-3 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-primary)] text-xs font-semibold"
            >
              GERAR CAMPANHA COMPLETA
            </button>
          </div>
        </div>

        <FilterTabBar
          activeId={aiHubSubmenu}
          onChange={setAiHubSubmenu}
          tabs={[
            { id: "dashboard_ai", label: "Visão AI" },
            { id: "providers", label: "Provedores & Chaves" },
            { id: "models", label: "Modelos" },
            { id: "configuration", label: "Política & Agentes" },
            { id: "campaigns_ai", label: "Campanhas AI" },
            { id: "image_studio", label: "Image Studio" },
            { id: "video_studio", label: "Video Studio" },
            { id: "usage_costs", label: "Uso & Custos" },
            { id: "history", label: "Histórico & Testes" },
          ]}
        />
      </section>

      {aiHubSubmenu === "dashboard_ai" && (
        <div className="space-y-4">
          <MetricStrip
            items={[
              {
                key: "def",
                label: "Motor Prioritário",
                value: defaultProviderKey.toUpperCase(),
                subtext: hasRealKey
                  ? `Conectado • ${aiEnginesConfig.configuration?.default_text_model}`
                  : `Pendente chave • ${aiEnginesConfig.configuration?.default_text_model}`,
                origin: hasRealKey ? "REAL" : "ESTIMATED",
              },
              {
                key: "policy",
                label: "Política de Custo",
                value: aiEnginesConfig.configuration?.cost_policy_mode || "FREE_ONLY",
                subtext: aiEnginesConfig.configuration?.allow_paid_fallback ? "Fallback pago autorizado" : "Zero cobrança garantida",
                origin: "REAL",
              },
              {
                key: "reqs",
                label: "Requisições • Tokens",
                value: `${aiEnginesConfig.usage_and_costs?.total_requests || 0} reqs`,
                subtext: `${aiEnginesConfig.usage_and_costs?.total_tokens || 0} tokens auditados`,
                origin: "REAL",
              },
              {
                key: "provs",
                label: "Catálogo Multimotor",
                value: `${(aiEnginesConfig.providers || []).length} provedores`,
                subtext: `${(aiEnginesConfig.models || []).length} modelos mapeados`,
                origin: "REAL",
              },
            ]}
          />

          <div className="ug-card rounded-xl p-4 flex flex-wrap gap-2">
            <button type="button" onClick={() => setAiHubSubmenu("providers")} className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold">
              CONFIGURAR GEMINI
            </button>
            <button type="button" onClick={() => setAiHubSubmenu("models")} className="px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold">
              SELECIONAR MOTOR
            </button>
            <button type="button" onClick={() => setAiHubSubmenu("campaigns_ai")} className="px-3.5 py-2 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-primary)] text-xs font-semibold">
              GERAR CAMPANHA COMPLETA
            </button>
            <button type="button" onClick={() => setAiHubSubmenu("image_studio")} className="px-3.5 py-2 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-primary)] text-xs font-semibold">
              GERAR IMAGEM
            </button>
            <button type="button" onClick={() => setAiHubSubmenu("video_studio")} className="px-3.5 py-2 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-primary)] text-xs font-semibold">
              GERAR ROTEIRO DE VÍDEO
            </button>
            <button type="button" onClick={() => setAiHubSubmenu("tests")} className="px-3.5 py-2 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.05] text-[var(--ug-text-primary)] text-xs font-semibold">
              TESTAR MOTOR
            </button>
          </div>
        </div>
      )}

      {aiHubSubmenu === "providers" && (
        <div className="ug-card rounded-xl divide-y divide-white/[0.05] text-xs">
          {(aiEnginesConfig.providers || []).map((p: any) => (
            <div key={p.provider_key} className="p-5 space-y-3">
              <div className="flex flex-wrap justify-between items-start gap-2">
                <div>
                  <div className="font-semibold text-sm text-[var(--ug-text-primary)] flex items-center gap-2">
                    <span>{p.name}</span>
                    <StatusPill
                      status={p.has_credential ? "EXECUTED" : "PENDING"}
                      label={p.has_credential ? `Configurada (${p.masked_credential})` : "Aguardando API Key"}
                    />
                  </div>
                  <div className="text-[11px] text-[var(--ug-text-muted)] mt-0.5">
                    {p.cost_tier} • {p.cost_notes}
                  </div>
                </div>
                {p.last_test_status && (
                  <span className="text-[11px] text-indigo-400">Último Teste: {p.last_test_status}</span>
                )}
              </div>
              <p className="text-[var(--ug-text-secondary)] text-[11px]">{p.limitations_text}</p>
              {p.provider_key === "openai_compatible" && (
                <input
                  value={aiEndpointInputs[p.provider_key] ?? p.base_url ?? ""}
                  onChange={(e) => setAiEndpointInputs({ ...aiEndpointInputs, [p.provider_key]: e.target.value })}
                  placeholder="Endpoint Base URL explícito (ex.: http://localhost:11434/v1)"
                  className="w-full px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                />
              )}
              <div className="flex flex-wrap gap-2">
                <input
                  type="password"
                  value={aiKeyInputs[p.provider_key] || ""}
                  onChange={(e) => setAiKeyInputs({ ...aiKeyInputs, [p.provider_key]: e.target.value })}
                  placeholder={`Inserir API Key para ${p.name} (Fernet AES-128)`}
                  aria-label={`Chave API de ${p.name}`}
                  className="flex-1 min-w-[200px] px-3 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                />
                <button
                  type="button"
                  onClick={async () => {
                    await apiFetch("/api/v1/ai-engine-hub/credentials", {
                      method: "POST",
                      body: JSON.stringify({
                        provider_key: p.provider_key,
                        api_key: aiKeyInputs[p.provider_key] || "",
                        custom_endpoint_url: aiEndpointInputs[p.provider_key] || p.base_url,
                        is_active: true,
                      }),
                    });
                    setAiKeyInputs({ ...aiKeyInputs, [p.provider_key]: "" });
                    const refreshed = await apiFetch("/api/v1/ai-engine-hub/overview");
                    setAiEnginesConfig(refreshed);
                    showNotice(`Credencial de ${p.name} criptografada e salva!`);
                  }}
                  className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
                >
                  {p.provider_key === "gemini" ? "CONFIGURAR GEMINI" : "Salvar Chave"}
                </button>
                <button
                  type="button"
                  onClick={async () => {
                    const res = await apiFetch("/api/v1/ai-engine-hub/test-connection", {
                      method: "POST",
                      body: JSON.stringify({ provider_key: p.provider_key }),
                    });
                    const refreshed = await apiFetch("/api/v1/ai-engine-hub/overview");
                    setAiEnginesConfig(refreshed);
                    showNotice(`Teste ${p.name}: ${res.status} (${res.error || "OK"})`);
                  }}
                  className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
                >
                  TESTAR MOTOR
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {aiHubSubmenu === "models" && (
        <div className="ug-card rounded-xl divide-y divide-white/[0.05] text-xs">
          {(aiEnginesConfig.models || []).map((m: any) => {
            const isDefault = aiEnginesConfig.configuration?.default_text_model === m.model_id;
            return (
              <div key={`${m.provider_key}:${m.model_id}`} className="p-4 flex flex-wrap items-center justify-between gap-3">
                <div className="space-y-0.5 max-w-2xl">
                  <div className="font-semibold text-[var(--ug-text-primary)] flex items-center gap-2">
                    <span>{m.display_name}</span>
                    <span className="px-2 py-0.5 rounded bg-white/[0.05] text-[10px] text-emerald-400">{m.cost_tier}</span>
                  </div>
                  <div className="text-[11px] text-[var(--ug-text-muted)]">
                    Provedor: {m.provider_key} • Modalidade: {m.modality} • {m.known_quota_note}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={async () => {
                    const updated = await apiFetch("/api/v1/ai-engine-hub/configuration", {
                      method: "PUT",
                      body: JSON.stringify({
                        default_provider_key: m.provider_key,
                        default_text_model: m.model_id,
                      }),
                    });
                    setAiEnginesConfig(updated);
                    showNotice(`Motor selecionado: ${m.provider_key} / ${m.model_id}`);
                  }}
                  className={`px-3.5 py-1.5 rounded-lg font-semibold ${
                    isDefault ? "bg-emerald-600 text-white" : "bg-indigo-600 hover:bg-indigo-500 text-white"
                  }`}
                >
                  {isDefault ? "✓ MOTOR SELECIONADO" : "SELECIONAR MOTOR"}
                </button>
              </div>
            );
          })}
        </div>
      )}

      {aiHubSubmenu === "configuration" && (
        <div className="space-y-4 text-xs">
          <div className="ug-card rounded-xl p-5 space-y-3">
            <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">Política de Custos (FREE_ONLY vs OWNER_APPROVED)</h4>
            <div className="flex flex-wrap gap-2">
              {["FREE_ONLY", "OWNER_APPROVED"].map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={async () => {
                    const updated = await apiFetch("/api/v1/ai-engine-hub/configuration", {
                      method: "PUT",
                      body: JSON.stringify({ cost_policy_mode: mode }),
                    });
                    setAiEnginesConfig(updated);
                    showNotice(`Política de custos atualizada para ${mode}!`);
                  }}
                  className={`px-4 py-2 rounded-lg font-semibold border ${
                    aiEnginesConfig.configuration?.cost_policy_mode === mode
                      ? "bg-emerald-600 border-emerald-500 text-white"
                      : "border-[var(--ug-border)] text-[var(--ug-text-secondary)]"
                  }`}
                >
                  Modo {mode}
                </button>
              ))}
            </div>
          </div>

          <div className="ug-card rounded-xl divide-y divide-white/[0.05]">
            {Object.values(aiEnginesConfig.configuration?.agent_routing || {}).map((ag: any) => (
              <div key={ag.agent_id} className="px-5 py-3 flex flex-wrap justify-between items-center gap-2">
                <div className="font-medium text-[var(--ug-text-primary)]">{ag.agent_name} ({ag.agent_id})</div>
                <div className="text-[11px] text-[var(--ug-text-muted)] tabular-nums">
                  Motor: {ag.provider_key} • Modelo: {ag.model_id} • Limite: {ag.daily_limit}/dia
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {aiHubSubmenu === "campaigns_ai" && (
        <div className="ug-card rounded-xl p-5 space-y-4 text-xs">
          <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">Motor de Campanhas AI</h4>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <input
              value={aiGenTopic}
              onChange={(e) => setAiGenTopic(e.target.value)}
              placeholder="Nome / Oferta da Campanha"
              className="md:col-span-2 px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]"
            />
            <select
              value={aiGenMode}
              onChange={(e) => setAiGenMode(e.target.value)}
              className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]"
            >
              <option value="FULL_CAMPAIGN">GERAR CAMPANHA COMPLETA (25 Itens)</option>
              <option value="SINGLE_PIECE">GERAR PEÇA INDIVIDUAL</option>
            </select>
            <select
              value={aiPieceType}
              onChange={(e) => setAiPieceType(e.target.value)}
              className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]"
            >
              {["ALL", "POST", "IMAGE", "VIDEO", "COPY", "EMAIL", "ARTICLE", "LANDING_PAGE", "CAROUSEL", "AD", "SCRIPT", "SEO", "CTA"].map((pt) => (
                <option key={pt} value={pt}>{pt}</option>
              ))}
            </select>
          </div>
          <button
            type="button"
            disabled={aiGenLoading}
            onClick={async () => {
              setAiGenLoading(true);
              try {
                const res = await apiFetch("/api/v1/ai-engine-hub/campaigns/generate", {
                  method: "POST",
                  body: JSON.stringify({
                    generation_scope: aiGenMode,
                    piece_type: aiPieceType,
                    campaign_name: aiGenTopic,
                    product_or_offer: aiGenTopic,
                    channel: aiGenPlatform,
                  }),
                });
                setAiGenResult(res);
                const refreshed = await apiFetch("/api/v1/ai-engine-hub/overview");
                setAiEnginesConfig(refreshed);
                showNotice(res.ok ? "Campanha gerada pelo motor de IA!" : `Aviso: ${res.status} — ${res.error}`);
              } finally {
                setAiGenLoading(false);
              }
            }}
            className="px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
          >
            GERAR CAMPANHA COMPLETA
          </button>
          {aiGenResult && (
            <pre className="p-3 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-secondary)] max-h-80 overflow-y-auto whitespace-pre-wrap text-[11px]">
              {JSON.stringify(aiGenResult, null, 2)}
            </pre>
          )}
        </div>
      )}

      {aiHubSubmenu === "image_studio" && (
        <div className="ug-card rounded-xl p-5 space-y-4 text-xs">
          <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">AI Image Studio (Capacidade &amp; Custo Real)</h4>
          <p className="text-[var(--ug-text-muted)]">
            Modelos gratuitos de texto geram prompts estruturados (`PROMPT_ONLY`). Renderização direta paga exige `OWNER_APPROVED` + faturamento externo ativo.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input
              value={aiImgPrompt}
              onChange={(e) => setAiImgPrompt(e.target.value)}
              placeholder="Prompt da imagem..."
              className="md:col-span-2 px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]"
            />
            <select
              value={aiImgMode}
              onChange={(e) => setAiImgMode(e.target.value)}
              className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]"
            >
              <option value="GENERATE_IMAGE">Renderizar Imagem (Imagen 3 / DALL-E 3)</option>
              <option value="PROMPT_ONLY">Gerar Prompt Técnico Gratuito</option>
            </select>
          </div>
          <button
            type="button"
            onClick={async () => {
              const res = await apiFetch("/api/v1/ai-engine-hub/image-studio/generate", {
                method: "POST",
                body: JSON.stringify({ prompt: aiImgPrompt, operation_mode: aiImgMode }),
              });
              setAiGenResult(res);
              const refreshed = await apiFetch("/api/v1/ai-engine-hub/overview");
              setAiEnginesConfig(refreshed);
              showNotice(res.ok ? `Image Studio: ${res.delivery_stage}` : `Bloqueado/Aviso: ${res.status}`);
            }}
            className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
          >
            GERAR IMAGEM
          </button>
          {aiGenResult && (
            <pre className="p-3 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-secondary)] max-h-72 overflow-y-auto whitespace-pre-wrap text-[11px]">
              {JSON.stringify(aiGenResult, null, 2)}
            </pre>
          )}
        </div>
      )}

      {aiHubSubmenu === "video_studio" && (
        <div className="ug-card rounded-xl p-5 space-y-4 text-xs">
          <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">AI Video Studio (Roteiro vs Renderização)</h4>
          <p className="text-[var(--ug-text-muted)]">
            Roteiro/storyboard são entregues gratuitamente; renderização direta de vídeo pago nunca ocorre sem autorização explícita.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input
              value={aiVidPrompt}
              onChange={(e) => setAiVidPrompt(e.target.value)}
              placeholder="Tema do vídeo..."
              className="md:col-span-2 px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]"
            />
            <select
              value={aiVidStage}
              onChange={(e) => setAiVidStage(e.target.value)}
              className="px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-primary)]"
            >
              <option value="SCRIPT_AND_STORYBOARD">Roteiro + Storyboard (STORYBOARD_ONLY)</option>
              <option value="SCRIPT_ONLY">Apenas Roteiro (SCRIPT_ONLY)</option>
              <option value="DIRECT_VIDEO_GENERATION">Vídeo Direto (Veo 2 Pago)</option>
            </select>
          </div>
          <button
            type="button"
            onClick={async () => {
              const res = await apiFetch("/api/v1/ai-engine-hub/video-studio/generate", {
                method: "POST",
                body: JSON.stringify({ prompt: aiVidPrompt, target_stage: aiVidStage }),
              });
              setAiGenResult(res);
              const refreshed = await apiFetch("/api/v1/ai-engine-hub/overview");
              setAiEnginesConfig(refreshed);
              showNotice(res.ok ? `Video Studio: ${res.delivery_stage}` : `Bloqueado/Aviso: ${res.status}`);
            }}
            className="px-5 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-semibold"
          >
            GERAR ROTEIRO DE VÍDEO
          </button>
          {aiGenResult && (
            <pre className="p-3 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-[var(--ug-text-secondary)] max-h-72 overflow-y-auto whitespace-pre-wrap text-[11px]">
              {JSON.stringify(aiGenResult, null, 2)}
            </pre>
          )}
        </div>
      )}

      {aiHubSubmenu === "usage_costs" && (
        <div className="ug-card rounded-xl divide-y divide-white/[0.05] text-xs">
          {Object.entries(aiEnginesConfig.usage_and_costs?.by_cost_classification || {}).map(([bucket, info]: [string, any]) => (
            <div key={bucket} className="px-5 py-3 flex justify-between items-center tabular-nums">
              <div>
                <div className="font-semibold text-[var(--ug-text-primary)]">{bucket}</div>
                <div className="text-[11px] text-[var(--ug-text-muted)]">{info.requests} reqs • {info.tokens} tokens</div>
              </div>
              <span className="text-emerald-400 font-semibold">
                {info.estimated_cost_brl === null ? "DESCONHECIDO" : `R$ ${info.estimated_cost_brl}`}
              </span>
            </div>
          ))}
        </div>
      )}

      {(aiHubSubmenu === "history" || aiHubSubmenu === "tests") && (
        <div className="ug-card rounded-xl overflow-hidden text-xs">
          <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] flex justify-between items-center">
            <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">Histórico de Execuções &amp; Testes</h4>
            <button
              type="button"
              onClick={async () => {
                showNotice("Testando conexão e geração real no motor padrão...");
                const res = await apiFetch("/api/v1/ai-engine-hub/test-connection", {
                  method: "POST",
                  body: JSON.stringify({
                    provider_key: defaultProviderKey,
                    model_id: aiEnginesConfig.configuration?.default_text_model || "gemini-2.5-flash",
                  }),
                });
                if (res.ok) {
                  await apiFetch("/api/v1/ai-engine-hub/route-execute", {
                    method: "POST",
                    body: JSON.stringify({
                      task_type: "test_generation",
                      required_capability: "text_generation",
                      prompt: "Teste rápido de conexão e geração real no UNION AI ENGINE HUB.",
                    }),
                  });
                }
                const refreshed = await apiFetch("/api/v1/ai-engine-hub/overview");
                setAiEnginesConfig(refreshed);
                showNotice(res.ok ? `Motor ${res.provider_key.toUpperCase()} CONECTADO!` : `Teste: ${res.status} (${res.error})`);
              }}
              className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
            >
              TESTAR MOTOR
            </button>
          </div>
          <div className="divide-y divide-white/[0.05] max-h-96 overflow-y-auto">
            {(aiEnginesConfig.recent_executions || []).map((ex: any) => (
              <div key={ex.execution_uuid} className="px-5 py-3 flex flex-wrap justify-between items-center gap-2">
                <div>
                  <div className="font-medium text-[var(--ug-text-primary)]">
                    {ex.task_type} • {ex.requested_provider}:{ex.requested_model} → {ex.executed_provider || "NENHUM"}:{ex.executed_model || "-"}
                  </div>
                  <div className="text-[11px] text-[var(--ug-text-muted)]">
                    Origem: {ex.execution_origin} • {ex.cost_classification} • {ex.total_tokens} tokens
                  </div>
                  {ex.error_message && <div className="text-amber-400 text-[11px]">{ex.error_message}</div>}
                </div>
                <StatusPill status={ex.status === "SUCCESS" ? "EXECUTED" : "PENDING"} label={ex.status} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function PlansAndUsagePanel({
  meData,
  plansOverview,
  apiFetch,
  onReload,
  showNotice,
}: {
  meData: any;
  plansOverview: any;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  showNotice: (msg: string) => void;
}) {
  const [entitlements, setEntitlements] = useState<any>(null);
  useEffect(() => {
    let active = true;
    apiFetch("/api/v1/plans/entitlements")
      .then((res) => {
        if (active) setEntitlements(res);
      })
      .catch(() => null);
    return () => {
      active = false;
    };
  }, [apiFetch, meData?.active_tenant?.plan_tier]);

  const catalog = entitlements?.plans_catalog || plansOverview?.plans_catalog || meData?.plans_catalog || {};
  const meters = Object.values(entitlements?.usage_meters || plansOverview?.usage_meters || {}) as any[];
  const activeTier = meData?.active_tenant?.plan_tier || "ENTERPRISE";
  const billingReady = entitlements?.billing_readiness;

  return (
    <section className="ug-card rounded-xl p-5 space-y-5 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-semibold text-[var(--ug-text-primary)] flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-indigo-400" aria-hidden="true" />
            <span>Planos PLG &amp; Consumo do Workspace</span>
          </h3>
          <p className="text-[11px] text-[var(--ug-text-muted)] mt-0.5">
            Medidores reais e prontidão de cobrança: <strong>{billingReady ? (billingReady.charge_enabled ? "Cobrança Ativa" : "Cobrança desativada (autorização explícita exigida)") : "Sem cobrança automática ativa"}</strong>.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <StatusPill status="EXECUTED" label={billingReady?.checkout_mode === "STRIPE_OR_ASAAS_READY_DISABLED" ? "Pronto (R$ 0 agora)" : "Sem cobrança live"} />
          <OriginBadge origin="REAL" />
        </div>
      </div>

      {meters.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {meters.map((m: any) => (
            <div key={m.label} className="p-3 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] space-y-1.5">
              <div className="flex justify-between items-center text-[11px]">
                <span className="text-[var(--ug-text-secondary)] truncate">{m.label}</span>
                <span className="font-semibold text-[var(--ug-text-primary)] tabular-nums">
                  {m.used}/{m.limit}
                </span>
              </div>
              <div className="h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
                <div
                  className={`h-full rounded-full ${m.near_limit ? "bg-amber-400" : "bg-indigo-500"}`}
                  style={{ width: `${Math.min(100, m.usage_pct || 0)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {Object.values(catalog).map((pl: any) => {
          const isCurrent = activeTier === pl.code;
          return (
            <div
              key={pl.code}
              className={`p-4 rounded-xl border flex flex-col justify-between gap-3 ${
                isCurrent
                  ? "bg-indigo-500/10 border-indigo-500/50"
                  : "bg-[var(--ug-bg)] border-[var(--ug-border)]"
              }`}
            >
              <div className="space-y-2">
                <div className="flex justify-between items-start gap-1">
                  <div className="font-semibold text-sm text-[var(--ug-text-primary)]">{pl.name}</div>
                </div>
                <div className="text-[11px] font-semibold text-indigo-400 tabular-nums">
                  {pl.recommended_price_usd === 0
                    ? "R$ 0 / mês"
                    : `Ref.: R$ ${pl.monthly_price_reference_brl}/mês ($${pl.recommended_price_usd})`}
                </div>
                <div className="text-[11px] text-[var(--ug-text-muted)]">
                  Até {pl.max_companies} empresa(s) • {pl.agents_included.length} agentes
                </div>
                <ul className="space-y-1 text-[11px] text-[var(--ug-text-secondary)]">
                  {(pl.features || []).slice(0, 4).map((f: string, idx: number) => (
                    <li key={idx}>• {f}</li>
                  ))}
                </ul>
              </div>
              <button
                type="button"
                onClick={async () => {
                  await apiFetch("/api/v1/tenants/current", {
                    method: "PUT",
                    body: JSON.stringify({ plan_tier: pl.code }),
                  });
                  await onReload();
                  showNotice(`Plano alterado para ${pl.name}!`);
                }}
                className={`w-full py-1.5 rounded-lg font-medium ${
                  isCurrent
                    ? "bg-indigo-600 text-white"
                    : "border border-[var(--ug-border)] hover:bg-indigo-600 hover:text-white text-[var(--ug-text-primary)]"
                }`}
              >
                {isCurrent ? "Plano Ativo" : `Selecionar ${pl.name}`}
              </button>
            </div>
          );
        })}
      </div>
    </section>
  );
}
