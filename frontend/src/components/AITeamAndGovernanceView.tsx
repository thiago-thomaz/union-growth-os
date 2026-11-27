"use client";

import React, { useState } from "react";
import {
  Bot,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Cpu,
  Info,
  KeyRound,
  Play,
  ShieldCheck,
  Sliders,
  Sparkles,
  Wrench,
} from "lucide-react";
import { LegacyMenuId } from "@/lib/navigation";
import { UIMode, simplifyTechnicalText } from "@/lib/plainLanguage";
import { EmptyState, StatusPill } from "@/components/DesignSystem";

const AGENT_FRIENDLY_META: Record<
  string,
  {
    problemSolved: string;
    dataUsed: string;
    canExecute: string;
    scheduleHint: string;
    needsApproval: string;
    credentialDep: string;
  }
> = {
  AGENT_01_CEO: {
    problemSolved: "Consolida números reais do negócio e define o que priorizar hoje.",
    dataUsed: "Receita real/importada, metas, leads do CRM e alertas abertos",
    canExecute: "Gerar briefing executivo e delegar tarefas do plano diário",
    scheduleHint: "Diário às 08:00 e sob demanda",
    needsApproval: "Não (somente análise e priorização)",
    credentialDep: "100% nativo (sem credencial externa)",
  },
  AGENT_02_CMO: {
    problemSolved: "Organiza público ideal e campanhas multicanal focadas em resultado.",
    dataUsed: "Personas cadastradas, campanhas ativas e ROI por canal",
    canExecute: "Sugerir planejamento mensal de marketing e metas",
    scheduleHint: "Diário às 09:00 e 16:00",
    needsApproval: "Sim, se orçamento > R$ 10.000",
    credentialDep: "Nativo + textos opcionais via Gemini gratuito",
  },
  AGENT_03_SEO: {
    problemSolved: "Identifica falhas no seu site que atrapalham o posicionamento no Google.",
    dataUsed: "URL pública da empresa, palavras-chave e artigos",
    canExecute: "Auditoria real de títulos, meta tags e estrutura",
    scheduleHint: "Diário às 14:00 e Segunda 09:00",
    needsApproval: "Não",
    credentialDep: "Auditoria nativa; Search Console opcional",
  },
  AGENT_04_SOCIAL: {
    problemSolved: "Mantém frequência de publicações com pacotes prontos em 1 clique.",
    dataUsed: "Calendário editorial e redes sociais conectadas",
    canExecute: "Criar cronograma semanal e pacotes assistidos",
    scheduleHint: "Diário às 07:00, 11:00 e 17:00",
    needsApproval: "Sim, antes de publicar externamente",
    credentialDep: "Conexão social para envio direto; Modo Assistido sem API",
  },
  AGENT_05_CREATIVE: {
    problemSolved: "Produz artes visuais locais PNG e roteiros estruturados para campanhas.",
    dataUsed: "Identidade da marca, ofertas e títulos",
    canExecute: "Renderizar artes PNG locais e roteiros",
    scheduleHint: "Diário às 10:00",
    needsApproval: "Não (gera rascunhos locais gratuitos)",
    credentialDep: "100% nativo (modelos pagos bloqueados)",
  },
  AGENT_06_COPYWRITER: {
    problemSolved: "Escreve variações de anúncios, páginas e e-mails persuasivos.",
    dataUsed: "Personas, diferenciais e frameworks AIDA/PAS",
    canExecute: "Gerar variantes de texto A/B para revisão",
    scheduleHint: "Diário às 10:00",
    needsApproval: "Não (gera rascunhos editáveis)",
    credentialDep: "Nativo + geração via Gemini Free Tier",
  },
  AGENT_07_GROWTH: {
    problemSolved: "Descobre onde clientes estão saindo no funil de vendas.",
    dataUsed: "Taxas do funil comercial e experimentos",
    canExecute: "Priorizar testes de conversão por impacto",
    scheduleHint: "Diário às 17:00",
    needsApproval: "Não",
    credentialDep: "100% nativo",
  },
  AGENT_08_SALES: {
    problemSolved: "Evita que leads fiquem sem retorno e acelera fechamento comercial.",
    dataUsed: "Leads com consentimento LGPD, qualificação e propostas",
    canExecute: "Pontuar leads (0–100) e agendar follow-ups",
    scheduleHint: "Diário às 12:00 e 16:00",
    needsApproval: "Sim, para envio final de proposta",
    credentialDep: "100% nativo no CRM interno",
  },
  AGENT_09_COMPETITIVE: {
    problemSolved: "Analisa concorrentes públicos respeitando boas práticas da web.",
    dataUsed: "Sites públicos cadastrados",
    canExecute: "Comparar posicionamento e diferenciais",
    scheduleHint: "Diário às 15:00",
    needsApproval: "Não",
    credentialDep: "100% nativo",
  },
  AGENT_10_FINANCE: {
    problemSolved: "Separa faturamento real de metas ou testes para proteger seu caixa.",
    dataUsed: "Lançamentos reais/importados, custos e cobranças",
    canExecute: "Calcular margem, ROI, CAC e LTV auditáveis",
    scheduleHint: "Diário às 18:00",
    needsApproval: "Imutável (sempre requer confirmação humana)",
    credentialDep: "Nativo; meio de pagamento opcional",
  },
  AGENT_11_CS: {
    problemSolved: "Detecta clientes com sinal de cancelamento antes da saída.",
    dataUsed: "Pesquisas de satisfação e histórico pós-venda",
    canExecute: "Sinalizar risco e sugerir ação de retenção",
    scheduleHint: "Contínuo",
    needsApproval: "Não",
    credentialDep: "100% nativo",
  },
  AGENT_12_DATA_ANALYST: {
    problemSolved: "Calcula seu Growth Score auditável e atribuição por canal sem inventar números.",
    dataUsed: "Leads reais, vendas, finanças e SEO",
    canExecute: "Consolidar Growth Score (0–100) e funil",
    scheduleHint: "Sob demanda e semanalmente",
    needsApproval: "Não (somente leitura)",
    credentialDep: "100% nativo (GA4 opcional)",
  },
};

export function AITeamAndGovernanceView({
  meData,
  agentsData,
  aiEnginesConfig,
  integrationsData,
  uiMode = "SIMPLE",
  apiFetch,
  onReload,
  onNavigate,
  showNotice,
}: {
  meData: any;
  agentsData: any;
  aiEnginesConfig: any;
  integrationsData: any[];
  uiMode?: UIMode;
  apiFetch: (path: string, options?: RequestInit) => Promise<any>;
  onReload: () => Promise<void>;
  onNavigate: (view: LegacyMenuId) => void;
  showNotice: (msg: string) => void;
}) {
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const [runningAgent, setRunningAgent] = useState<string>("");
  const [wizardKey, setWizardKey] = useState("");
  const [wizardBusy, setWizardBusy] = useState(false);
  const [wizardTestOut, setWizardTestOut] = useState<any>(null);
  const [agentSearch, setAgentSearch] = useState("");

  const currentAutonomy = meData?.active_tenant?.autonomy_default_level || 2;
  const costPolicy = aiEnginesConfig?.configuration?.cost_policy_mode || "FREE_ONLY";
  const defaultProvider = aiEnginesConfig?.configuration?.default_provider_key || "gemini";
  const defaultModel = aiEnginesConfig?.configuration?.default_text_model || "gemini-2.5-flash";
  const recentExecs = aiEnginesConfig?.recent_executions || [];
  const connectedIntegrations = (integrationsData || []).filter((i: any) => i.status === "CONNECTED");
  const geminiProv = (aiEnginesConfig?.providers || []).find((p: any) => p.provider_key === "gemini");

  const filteredAgents = (agentsData?.agents || []).filter((ag: any) => {
    const q = agentSearch.trim().toLowerCase();
    if (!q) return true;
    const meta = AGENT_FRIENDLY_META[ag.id];
    return `${ag.name} ${ag.role} ${meta?.problemSolved || ""} ${meta?.canExecute || ""}`.toLowerCase().includes(q);
  });

  return (
    <div className="space-y-6 max-w-6xl mx-auto ug-fade-in">
      {/* ASSISTENTE DE IA EM FAIXA ÚNICA (3 PASSOS HORIZONTAIS) */}
      <section aria-label="Assistente guiado de configuração de IA" className="ug-card rounded-2xl overflow-hidden">
        <div className="px-5 py-4 border-b border-[var(--ug-border-subtle)] flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-[var(--ug-text-primary)] flex items-center gap-2">
              <Wrench className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              <span>Configuração Rápida dos Serviços de IA (3 Passos)</span>
            </h3>
            <p className="text-xs text-[var(--ug-text-muted)] mt-0.5">
              A trava gratuita (FREE_ONLY) bloqueia qualquer cobrança automática paga por padrão.
            </p>
          </div>
          <StatusPill
            status={costPolicy === "FREE_ONLY" ? "EXECUTED" : "PENDING"}
            label={costPolicy === "FREE_ONLY" ? "Trava Gratuita Ativa" : "Uso Pago Aprovado"}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 divide-y lg:divide-y-0 lg:divide-x divide-white/[0.06] text-xs">
          {/* Passo 1 */}
          <div className="p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-[var(--ug-text-primary)] flex items-center gap-1.5">
                <KeyRound className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
                1. Chave Gratuita Gemini
              </span>
              <span className="text-[10px] text-[var(--ug-text-muted)]">
                {geminiProv?.has_credential ? geminiProv.masked_credential : "Opcional"}
              </span>
            </div>
            <label htmlFor="ug-wizard-gemini-key" className="block text-[11px] text-[var(--ug-text-muted)]">
              Chave gratuita do Google AI Studio (criptografada)
            </label>
            <input
              id="ug-wizard-gemini-key"
              type="password"
              value={wizardKey}
              onChange={(e) => setWizardKey(e.target.value)}
              placeholder="AIzaSy..."
              className="w-full px-2.5 py-1.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
            />
            <button
              type="button"
              disabled={wizardBusy}
              onClick={async () => {
                if (!wizardKey.trim()) {
                  showNotice("Cole sua chave gratuita antes de salvar.");
                  return;
                }
                setWizardBusy(true);
                try {
                  await apiFetch("/api/v1/ai-engine-hub/credentials", {
                    method: "POST",
                    body: JSON.stringify({ provider_key: "gemini", api_key: wizardKey.trim(), is_active: true }),
                  });
                  setWizardKey("");
                  await onReload();
                  showNotice("Chave salva com criptografia! Clique em Testar Conexão.");
                } catch (err: any) {
                  showNotice(err?.message || "Erro ao salvar chave.");
                } finally {
                  setWizardBusy(false);
                }
              }}
              className="w-full py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium"
            >
              Salvar Chave Gratuita
            </button>
          </div>

          {/* Passo 2 */}
          <div className="p-4 space-y-2.5 flex flex-col justify-between">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-[var(--ug-text-primary)] flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" aria-hidden="true" />
                  2. Testar Conexão Real
                </span>
                <span className="text-[10px] text-[var(--ug-text-muted)]">Sem custo</span>
              </div>
              <p className="text-[11px] text-[var(--ug-text-muted)]">
                Confirma se sua chave gratuita está respondendo corretamente sem simular sucesso.
              </p>
              {wizardTestOut && (
                <div className={`text-[11px] ${wizardTestOut.ok ? "text-emerald-400" : "text-amber-400"}`}>
                  Status: {wizardTestOut.status} {wizardTestOut.error ? `— ${wizardTestOut.error}` : "— Conectado"}
                </div>
              )}
            </div>
            <div className="space-y-1.5">
              <button
                type="button"
                disabled={wizardBusy}
                onClick={async () => {
                  setWizardBusy(true);
                  try {
                    const res = await apiFetch("/api/v1/ai-engine-hub/test-connection", {
                      method: "POST",
                      body: JSON.stringify({ provider_key: "gemini" }),
                    });
                    setWizardTestOut(res);
                    await onReload();
                    showNotice(res.ok ? "Conexão aprovada!" : `Resultado: ${res.status}`);
                  } catch (err: any) {
                    showNotice(err?.message || "Falha ao testar conexão.");
                  } finally {
                    setWizardBusy(false);
                  }
                }}
                className="w-full py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium inline-flex items-center justify-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
                <span>{wizardBusy ? "Testando..." : "Testar Conexão Real Agora"}</span>
              </button>
              <button
                type="button"
                onClick={() => onNavigate("ai_engines")}
                className="w-full text-[11px] text-indigo-400 hover:underline"
              >
                Avançado: ver todos os serviços de IA →
              </button>
            </div>
          </div>

          {/* Passo 3 */}
          <div className="p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-[var(--ug-text-primary)] flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-amber-400" aria-hidden="true" />
                3. Controle &amp; Autonomia
              </span>
              <span className="text-[11px] font-medium text-[var(--ug-text-secondary)]">Nível {currentAutonomy}</span>
            </div>
            <p className="text-[11px] text-[var(--ug-text-muted)]">
              Controle o quanto a IA pode agir antes de pedir aprovação em Meu Trabalho.
            </p>
            <div className="flex gap-1.5">
              {[
                { lvl: 1, name: "1. Assistido" },
                { lvl: 2, name: "2. Recomendado" },
                { lvl: 3, name: "3. Autônomo" },
              ].map((opt) => (
                <button
                  key={opt.lvl}
                  type="button"
                  onClick={async () => {
                    await apiFetch("/api/v1/tenants/current", {
                      method: "PUT",
                      body: JSON.stringify({ autonomy_default_level: opt.lvl }),
                    });
                    await onReload();
                    showNotice(`Autonomia atualizada para ${opt.name}!`);
                  }}
                  className={`flex-1 py-1.5 px-2 rounded-lg text-[11px] font-medium border transition ${
                    currentAutonomy === opt.lvl
                      ? "bg-indigo-600 text-white border-indigo-500"
                      : "bg-white/[0.03] border-[var(--ug-border)] text-[var(--ug-text-secondary)]"
                  }`}
                >
                  {opt.name}
                </button>
              ))}
            </div>
            <div className="text-[11px] text-[var(--ug-text-muted)]">
              Serviço ativo: <strong className="text-[var(--ug-text-primary)] uppercase">{defaultProvider}</strong> • Conexões:{" "}
              <strong className="text-[var(--ug-text-primary)]">{connectedIntegrations.length}/{(integrationsData || []).length}</strong>
            </div>
          </div>
        </div>
      </section>

      {/* Equipe Digital de Agentes (Lista / Grade Limpa sem caixas pesadas internas) */}
      <section className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-[var(--ug-text-primary)] flex items-center gap-2">
              <Bot className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              <span>Equipe Digital de Agentes Especializados ({(agentsData?.agents || []).length})</span>
            </h3>
            <p className="text-xs text-[var(--ug-text-muted)]">
              Escolha um especialista pelo objetivo e execute sob demanda com 1 clique.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <input
              value={agentSearch}
              onChange={(e) => setAgentSearch(e.target.value)}
              placeholder="Buscar agente..."
              aria-label="Filtrar agentes especializados"
              className="px-3 py-1.5 rounded-lg bg-[var(--ug-surface)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)] w-48"
            />
            <button
              type="button"
              onClick={() => setShowTechnicalDetails((v) => !v)}
              className="px-3 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] text-xs inline-flex items-center gap-1.5"
            >
              <Info className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
              <span>{showTechnicalDetails ? "Ocultar detalhes técnicos" : "Detalhes técnicos"}</span>
              {showTechnicalDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        <div className="ug-card rounded-2xl divide-y divide-white/[0.05]">
          {filteredAgents.map((ag: any) => {
            const meta = AGENT_FRIENDLY_META[ag.id] || {
              problemSolved: "Automatiza análises operacionais desta área.",
              dataUsed: "Dados do seu workspace",
              canExecute: ag.role,
              scheduleHint: "Sob demanda",
              needsApproval: "Conforme autonomia",
              credentialDep: "Nativo",
            };
            return (
              <div
                key={ag.id}
                className="px-4 py-3.5 hover:bg-white/[0.02] transition flex flex-col lg:flex-row lg:items-center justify-between gap-3 text-xs"
              >
                <div className="space-y-1 min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-[var(--ug-text-primary)]">{ag.name}</span>
                    <StatusPill status="EXECUTED" label="Pronto" />
                    <span className="text-[11px] text-[var(--ug-text-muted)]">• {meta.scheduleHint}</span>
                  </div>
                  <p className="text-[11px] text-indigo-300">{meta.problemSolved}</p>
                  <div className="text-[11px] text-[var(--ug-text-muted)]">
                    <strong>Ação:</strong> {meta.canExecute} • <strong>Aprovação:</strong> {meta.needsApproval} •{" "}
                    <strong>Requisito:</strong> {simplifyTechnicalText(meta.credentialDep, uiMode)}
                  </div>
                  {(showTechnicalDetails || uiMode === "ADVANCED") && (
                    <div className="text-[10px] font-mono text-indigo-400 pt-0.5">
                      ID: {ag.id} • Modelo: {defaultModel} • Ferramentas: {(ag.allowed_tools || []).join(", ") || "core"}
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    disabled={runningAgent === ag.id}
                    onClick={async () => {
                      setRunningAgent(ag.id);
                      try {
                        await apiFetch(`/api/v1/agents/${ag.id}/execute`, {
                          method: "POST",
                          body: JSON.stringify({}),
                        });
                        await onReload();
                        showNotice(`${ag.name} executado com sucesso!`);
                      } catch (err: any) {
                        showNotice(err?.message || `Erro ao executar ${ag.name}.`);
                      } finally {
                        setRunningAgent("");
                      }
                    }}
                    className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-medium inline-flex items-center gap-1"
                  >
                    <Play className="w-3 h-3" aria-hidden="true" />
                    <span>{runningAgent === ag.id ? "Executando..." : "Executar Agora"}</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => onNavigate("audit")}
                    className="px-2.5 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] text-[11px]"
                  >
                    Histórico
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Histórico Transparente das Execuções */}
      <section id="ai-recent-executions" className="space-y-3">
        <div className="flex items-center justify-between gap-2">
          <div>
            <h3 className="text-sm font-semibold text-[var(--ug-text-primary)] flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              <span>Últimas Execuções dos Serviços de IA</span>
            </h3>
            <p className="text-xs text-[var(--ug-text-muted)]">
              Registra execuções reais gratuitas, bloqueios por limite e custo R$ 0,00.
            </p>
          </div>
          <button
            type="button"
            onClick={() => onNavigate("ai_engines")}
            className="text-xs font-medium text-indigo-400 hover:underline inline-flex items-center gap-1"
          >
            <Sliders className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Central Avançada →</span>
          </button>
        </div>

        {recentExecs.length === 0 ? (
          <EmptyState
            title="Nenhuma execução via serviço externo registrada"
            description="Quando testar sua chave ou gerar textos via Gemini/Groq, cada registro aparecerá aqui."
            actionLabel="Abrir Modelos & Provedores"
            onAction={() => onNavigate("ai_engines")}
          />
        ) : (
          <div className="ug-card rounded-xl divide-y divide-white/[0.05]">
            {recentExecs.slice(0, 6).map((ex: any) => {
              const st = String(ex.status || "");
              const pill =
                st === "SUCCESS"
                  ? "EXECUTED"
                  : st.includes("BLOCKED") || st.includes("QUOTA")
                  ? "BLOCKED"
                  : st.includes("ERROR") || st.includes("FAILED")
                  ? "FAILED"
                  : "PENDING";
              return (
                <div key={ex.execution_uuid} className="px-4 py-3 text-xs flex flex-wrap items-center justify-between gap-3">
                  <div className="space-y-0.5 min-w-0">
                    <div className="font-medium text-[var(--ug-text-primary)]">
                      {ex.task_type} ({ex.requested_provider}:{ex.requested_model})
                    </div>
                    <div className="text-[11px] text-[var(--ug-text-muted)]">
                      {ex.executed_provider
                        ? `${ex.executed_provider}:${ex.executed_model} • ${ex.total_tokens} tokens • R$ ${ex.estimated_cost_brl ?? 0}`
                        : ex.error_message || "Não executado"}
                    </div>
                  </div>
                  <StatusPill status={pill} label={st} />
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
