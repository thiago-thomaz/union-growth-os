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
    problemSolved: "Evita que você perca tempo juntando números soltos para saber o que fazer hoje.",
    dataUsed: "Receita real/importada, metas, leads do CRM e alertas abertos",
    canExecute: "Gerar briefing executivo e delegar tarefas do plano diário",
    scheduleHint: "Diário às 08:00 e sob demanda",
    needsApproval: "Não (somente análise e priorização)",
    credentialDep: "Funciona 100% nativo (sem credencial externa)",
  },
  AGENT_02_CMO: {
    problemSolved: "Estrutura personas e campanhas organizadas em vez de ações de marketing aleatórias.",
    dataUsed: "Personas cadastradas, campanhas ativas e ROI por canal",
    canExecute: "Sugerir planejamento mensal de marketing e metas de aquisição",
    scheduleHint: "Diário às 09:00 e 16:00",
    needsApproval: "Sim, se orçamento sugerido > R$ 10.000",
    credentialDep: "Nativo + textos opcionais via Gemini gratuito",
  },
  AGENT_03_SEO: {
    problemSolved: "Descobre falhas técnicas no seu site que impedem aparição no Google.",
    dataUsed: "URL pública configurada na empresa, palavras-chave e artigos",
    canExecute: "Auditoria HTTP real de meta tags, títulos H1 e estrutura Schema.org",
    scheduleHint: "Diário às 14:00 e Segunda 09:00",
    needsApproval: "Não",
    credentialDep: "Auditoria HTTP nativa; Google Search Console opcional",
  },
  AGENT_04_SOCIAL: {
    problemSolved: "Mantém constância nas redes sociais sem precisar escrever tudo do zero todo dia.",
    dataUsed: "Calendário editorial e status das integrações sociais",
    canExecute: "Criar cronograma multicanal e preparar pacotes em 1 clique",
    scheduleHint: "Diário às 07:00, 11:00 e 17:00",
    needsApproval: "Sim, antes de qualquer publicação externa",
    credentialDep: "OAuth social para envio direto; Modo Assistido sem API",
  },
  AGENT_05_CREATIVE: {
    problemSolved: "Produz artes PNG, capas e roteiros padronizados para campanhas rapidamente.",
    dataUsed: "Identidade da marca, ofertas e títulos de campanhas",
    canExecute: "Renderizar artes visuais locais em PNG e roteiros estruturados",
    scheduleHint: "Diário às 10:00",
    needsApproval: "Não (gera rascunhos visuais locais sem custo)",
    credentialDep: "Funciona nativo (imagens pagas Imagen 3 ficam bloqueadas)",
  },
  AGENT_06_COPYWRITER: {
    problemSolved: "Elimina bloqueio criativo na criação de anúncios, páginas e e-mails persuasivos.",
    dataUsed: "Personas, benefícios da oferta e frameworks AIDA/PAS",
    canExecute: "Gerar variantes de texto A/B prontas para revisão",
    scheduleHint: "Diário às 10:00",
    needsApproval: "Não (gera rascunhos editáveis)",
    credentialDep: "Nativo + geração avançada via Gemini Free Tier",
  },
  AGENT_07_GROWTH: {
    problemSolved: "Identifica em qual etapa do funil os clientes estão parando.",
    dataUsed: "Taxas do funil comercial e experimentos registrados",
    canExecute: "Calcular prioridades (ICE Score) e comparar resultados reais",
    scheduleHint: "Diário às 17:00",
    needsApproval: "Não",
    credentialDep: "Funciona 100% nativo",
  },
  AGENT_08_SALES: {
    problemSolved: "Evita que leads interessados fiquem esperando horas sem atendimento ou follow-up.",
    dataUsed: "Leads capturados com LGPD, notas de qualificação e propostas",
    canExecute: "Pontuar leads (0–100) e agendar tarefas de retorno comercial",
    scheduleHint: "Diário às 12:00 e 16:00",
    needsApproval: "Sim, para envio final de proposta vinculante",
    credentialDep: "Funciona 100% nativo no CRM interno",
  },
  AGENT_09_COMPETITIVE: {
    problemSolved: "Monitora concorrentes públicos sem trabalho manual de pesquisa.",
    dataUsed: "URLs públicas informadas (sempre respeitando robots.txt)",
    canExecute: "Comparar posicionamento e diferenciais competitivos",
    scheduleHint: "Diário às 15:00",
    needsApproval: "Não",
    credentialDep: "Funciona 100% nativo",
  },
  AGENT_10_FINANCE: {
    problemSolved: "Garante visão real de caixa e lucro sem misturar metas ou testes Sandbox.",
    dataUsed: "Lançamentos reais/importados, custos e faturas do pipeline",
    canExecute: "Recalcular margem, ROI, CAC, LTV e alertas financeiros",
    scheduleHint: "Diário às 18:00",
    needsApproval: "Imutável (sempre exige aprovação humana financeira)",
    credentialDep: "Funciona nativo; Mercado Pago opcional para cobrança",
  },
  AGENT_11_CS: {
    problemSolved: "Detecta clientes insatisfeitos antes do cancelamento (risco de churn).",
    dataUsed: "Pesquisas de NPS/CSAT e comentários pós-venda",
    canExecute: "Classificar risco de retenção e sugerir ação preventiva",
    scheduleHint: "Monitoramento contínuo",
    needsApproval: "Não",
    credentialDep: "Funciona 100% nativo",
  },
  AGENT_12_DATA_ANALYST: {
    problemSolved: "Consolida métricas reais, Growth Score transparente e origem dos clientes sem inventar números.",
    dataUsed: "Leads reais, funil comercial, finanças auditáveis e auditorias SEO",
    canExecute: "Calcular Growth Score (0–100) e mapa de atribuição por canal",
    scheduleHint: "Sob demanda e toda segunda-feira",
    needsApproval: "Não (somente leitura analítica)",
    credentialDep: "100% nativo (GA4 opcional)",
  },
};

export function AITeamAndGovernanceView({
  meData,
  agentsData,
  aiEnginesConfig,
  integrationsData,
  apiFetch,
  onReload,
  onNavigate,
  showNotice,
}: {
  meData: any;
  agentsData: any;
  aiEnginesConfig: any;
  integrationsData: any[];
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
    <div className="space-y-6">
      {/* ASSISTENTE GUIADO DE CONFIGURAÇÃO DE IA (3 PASSOS REAIS, ZERO COBRANÇA PAGA) */}
      <section
        aria-label="Assistente guiado de configuração de IA"
        className="ug-card ug-onboarding-banner rounded-2xl border border-indigo-500/30 p-5 space-y-4"
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <Wrench className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              <h3 className="text-sm font-bold text-white ug-text-primary">
                Assistente Guiado de Configuração de IA (3 Passos Simples)
              </h3>
            </div>
            <p className="text-xs text-slate-400 ug-text-muted mt-0.5">
              Configure o motor gratuito sem termos técnicos. A trava financeira <strong>FREE_ONLY</strong> impede qualquer cobrança automática no cartão.
            </p>
          </div>
          <StatusPill
            status={costPolicy === "FREE_ONLY" ? "EXECUTED" : "PENDING"}
            label={costPolicy === "FREE_ONLY" ? "Trava Gratuita (FREE_ONLY)" : "Uso Pago Aprovado"}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 text-xs">
          {/* PASSO 1 */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-indigo-300 flex items-center gap-1.5">
                <KeyRound className="w-3.5 h-3.5" aria-hidden="true" />
                Passo 1: Chave Gratuita Gemini
              </span>
              <span className="text-[10px] text-slate-400">
                {geminiProv?.has_credential ? `Atual: ${geminiProv.masked_credential}` : "Opcional"}
              </span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Crie uma chave gratuita no Google AI Studio (começa com <code className="text-indigo-300">AIzaSy...</code>) para gerar campanhas e textos.
            </p>
            <div>
              <label htmlFor="ug-wizard-gemini-key" className="block text-[11px] font-medium text-slate-300 mb-1">
                Chave API Google Gemini (Free Tier)
              </label>
              <input
                id="ug-wizard-gemini-key"
                type="password"
                value={wizardKey}
                onChange={(e) => setWizardKey(e.target.value)}
                placeholder="Ex.: AIzaSyB... (criptografia Fernet)"
                className="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-white"
              />
            </div>
            <button
              type="button"
              disabled={wizardBusy}
              onClick={async () => {
                if (!wizardKey.trim()) {
                  showNotice("Cole sua chave do Google AI Studio (AIzaSy...) antes de salvar.");
                  return;
                }
                setWizardBusy(true);
                try {
                  await apiFetch("/api/v1/ai-engine-hub/credentials", {
                    method: "POST",
                    body: JSON.stringify({
                      provider_key: "gemini",
                      api_key: wizardKey.trim(),
                      is_active: true,
                    }),
                  });
                  setWizardKey("");
                  await onReload();
                  showNotice("Chave Gemini salva com criptografia Fernet! Agora clique em 'Testar Conexão Real' no Passo 2.");
                } catch (err: any) {
                  showNotice(err?.message || "Erro ao salvar chave do Gemini.");
                } finally {
                  setWizardBusy(false);
                }
              }}
              className="w-full py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
            >
              Salvar Chave Gratuita
            </button>
          </div>

          {/* PASSO 2 */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2.5 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-emerald-300 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
                  Passo 2: Testar Motor Real
                </span>
                <span className="text-[10px] text-slate-400">Sem custos</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Verifica ao vivo se a chave atual responde no Free Tier do Google sem simular sucesso.
              </p>
              {wizardTestOut && (
                <div
                  className={`p-2 rounded-lg border text-[11px] ${
                    wizardTestOut.ok
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-200"
                      : "bg-amber-500/10 border-amber-500/30 text-amber-200"
                  }`}
                >
                  <strong>Status real: {wizardTestOut.status}</strong>
                  {wizardTestOut.error ? ` — ${wizardTestOut.error}` : " — Conexão validada com sucesso!"}
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
                    showNotice(
                      res.ok
                        ? "Teste real do Gemini aprovado e conectado!"
                        : `Resultado real do teste: ${res.status} (${res.error || "verifique credencial/cota"})`
                    );
                  } catch (err: any) {
                    showNotice(err?.message || "Falha ao testar conexão com provedor.");
                  } finally {
                    setWizardBusy(false);
                  }
                }}
                className="w-full py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold inline-flex items-center justify-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
                {wizardBusy ? "Testando conexão..." : "Testar Conexão Real Agora"}
              </button>
              <button
                type="button"
                onClick={() => onNavigate("ai_engines")}
                className="w-full py-1 text-[11px] text-indigo-300 hover:underline"
              >
                Avançado: ver todos os modelos & provedores →
              </button>
            </div>
          </div>

          {/* PASSO 3 */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-amber-300 flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" />
                Passo 3: Controle & Autonomia
              </span>
              <span className="text-[11px] font-bold text-slate-300">Nível {currentAutonomy}</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Defina o quanto os 12 agentes podem agir sozinhos antes de pedir sua confirmação em <strong>Meu Trabalho</strong>.
            </p>
            <div className="flex gap-1.5 pt-1">
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
                    showNotice(`Autonomia da IA atualizada para ${opt.name}!`);
                  }}
                  className={`flex-1 py-1.5 px-2 rounded-lg text-[11px] font-semibold border transition ${
                    currentAutonomy === opt.lvl
                      ? "bg-indigo-600 text-white border-indigo-500"
                      : "bg-slate-950 border-slate-800 text-slate-300 hover:bg-slate-800"
                  }`}
                >
                  {opt.name}
                </button>
              ))}
            </div>
            <div className="text-[11px] text-slate-400 pt-1">
              Motor ativo: <strong className="text-slate-200 uppercase">{defaultProvider}</strong> • Integrações ativas:{" "}
              <strong className="text-slate-200">{connectedIntegrations.length}/{(integrationsData || []).length}</strong>
            </div>
          </div>
        </div>
      </section>

      {/* Catálogo Humano dos Agentes */}
      <section className="ug-card rounded-2xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold text-white ug-text-primary flex items-center gap-2">
              <Bot className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              Equipe Digital de Agentes Especializados ({(agentsData?.agents || []).length})
            </h3>
            <p className="text-xs text-slate-400">
              Escolha o especialista conforme o problema que deseja resolver hoje, teste com 1 clique e acompanhe o resultado logo abaixo.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <input
              value={agentSearch}
              onChange={(e) => setAgentSearch(e.target.value)}
              placeholder="Buscar agente (ex.: SEO, vendas, financeiro)..."
              aria-label="Filtrar agentes especializados"
              className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white w-56"
            />
            <button
              type="button"
              onClick={() => setShowTechnicalDetails((v) => !v)}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs inline-flex items-center gap-1.5"
            >
              <Info className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
              {showTechnicalDetails ? "Ocultar detalhes técnicos" : "Detalhes técnicos (avançado)"}
              {showTechnicalDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {filteredAgents.map((ag: any) => {
            const meta = AGENT_FRIENDLY_META[ag.id] || {
              problemSolved: "Automatiza análises operacionais desta área.",
              dataUsed: "Dados operacionais do seu workspace",
              canExecute: ag.role,
              scheduleHint: "Sob demanda",
              needsApproval: "Conforme nível de autonomia",
              credentialDep: "Nativo no sistema",
            };
            return (
              <div key={ag.id} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between gap-3 text-xs">
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="font-bold text-white">{ag.name}</div>
                    <StatusPill status="EXECUTED" label="Pronto" />
                  </div>
                  <p className="text-indigo-200 text-[11px] font-medium leading-relaxed">{meta.problemSolved}</p>
                  <div className="pt-1 space-y-1 text-[11px] text-slate-400">
                    <div><strong className="text-slate-300">O que executa:</strong> {meta.canExecute}</div>
                    <div><strong className="text-slate-300">Dados usados:</strong> {meta.dataUsed}</div>
                    <div><strong className="text-slate-300">Dependência de credenciais:</strong> {meta.credentialDep}</div>
                    <div><strong className="text-slate-300">Quando trabalha:</strong> {meta.scheduleHint}</div>
                    <div><strong className="text-slate-300">Permissão / Aprovação:</strong> {meta.needsApproval}</div>
                  </div>
                  {showTechnicalDetails && (
                    <div className="mt-2 p-2 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-indigo-300">
                      ID: {ag.id} • Modelo Padrão: {defaultModel} • Ferramentas: {(ag.allowed_tools || []).join(", ") || "core"}
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
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
                        showNotice(`${ag.name} executado com sucesso! Acompanhe na Auditoria/Histórico.`);
                      } catch (err: any) {
                        showNotice(err?.message || `Erro ao executar ${ag.name}.`);
                      } finally {
                        setRunningAgent("");
                      }
                    }}
                    className="flex-1 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold inline-flex items-center justify-center gap-1.5"
                  >
                    <Play className="w-3 h-3" aria-hidden="true" />
                    {runningAgent === ag.id ? "Executando..." : "Executar Rotina Segura"}
                  </button>
                  <button
                    type="button"
                    onClick={() => onNavigate("audit")}
                    className="px-2.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px]"
                    title="Acompanhar histórico de execuções deste agente"
                  >
                    Resultados
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Histórico Transparente das Execuções de IA (Seção 13) */}
      <section id="ai-recent-executions" className="ug-card rounded-2xl p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white ug-text-primary flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-indigo-400" aria-hidden="true" />
              Últimas Execuções da IA (Visão Transparente)
            </h3>
            <p className="text-xs text-slate-400">
              Cada solicitação diferencia claramente o que rodou no motor gratuito, o que ficou bloqueado por cota/política e o custo exato (R$ 0,00).
            </p>
          </div>
          <button
            type="button"
            onClick={() => onNavigate("ai_engines")}
            className="text-xs font-semibold text-indigo-400 hover:underline flex items-center gap-1"
          >
            <Sliders className="w-3.5 h-3.5" aria-hidden="true" />
            Abrir Central Completa →
          </button>
        </div>

        {recentExecs.length === 0 ? (
          <EmptyState
            title="Nenhuma execução via motor LLM registrada"
            description="Quando você testar a conexão acima ou gerar campanhas com IA, cada execução real ou bloqueio aparecerá aqui com total transparência."
            actionLabel="Abrir Modelos & Provedores"
            onAction={() => onNavigate("ai_engines")}
          />
        ) : (
          <div className="space-y-2">
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
                <div key={ex.execution_uuid} className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 text-xs flex flex-wrap items-center justify-between gap-3">
                  <div className="space-y-0.5 min-w-0">
                    <div className="font-semibold text-white">
                      Solicitado para {ex.task_type} ({ex.requested_provider}:{ex.requested_model})
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {ex.executed_provider
                        ? `Executado em ${ex.executed_provider}:${ex.executed_model} • ${ex.total_tokens} tokens • Custo: R$ ${ex.estimated_cost_brl ?? 0}`
                        : ex.error_message || "Não executado — verifique status"}
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
