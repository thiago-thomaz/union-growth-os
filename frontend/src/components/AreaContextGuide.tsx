"use client";

import React, { useEffect, useState } from "react";
import { ArrowRight, Bot, CheckCircle2, ChevronDown, ChevronUp, Compass, Info, ShieldAlert } from "lucide-react";
import { AreaId, LegacyMenuId } from "@/lib/navigation";

interface AreaGuideContent {
  title: string;
  whatCanDo: string;
  howToStart: string;
  whatToFill: string;
  whatHappensNext: string;
  whatAiDoes: string;
  needsApprovalOrCreds: string;
  recommendedLabel: string;
  recommendedTarget: LegacyMenuId;
}

const AREA_GUIDES: Record<AreaId, AreaGuideContent> = {
  inicio: {
    title: "Guia do Início — Seu Painel de Decisão Diária",
    whatCanDo: "Ver prioridades reais do dia, aprovações pendentes, ações da IA e os 4 indicadores principais do negócio.",
    howToStart: "Revise os cards do Bloco 1 ('O que precisa da sua atenção') ou conclua os primeiros passos de configuração.",
    whatToFill: "Nada obrigatório nesta tela — ela consolida automaticamente os dados das outras áreas.",
    whatHappensNext: "Cada ação clicada leva direto ao módulo certo para resolver em 1 ou 2 cliques.",
    whatAiDoes: "O AI CEO lê seus indicadores reais e gera o resumo executivo sem inventar números.",
    needsApprovalOrCreds: "Qualquer gasto financeiro, cobrança ou publicação externa aguarda sua autorização explícita.",
    recommendedLabel: "Ver Pendências em Meu Trabalho",
    recommendedTarget: "my_work",
  },
  meu_trabalho: {
    title: "Guia de Meu Trabalho — Caixa Unificada de Ações",
    whatCanDo: "Aprovar ou recusar solicitações da IA, resolver alertas operacionais e acompanhar tarefas comerciais.",
    howToStart: "Use os filtros superiores ('Precisa de mim' ou 'Aguardando aprovação') e clique em um item para abrir os detalhes.",
    whatToFill: "Apenas escolha Aprovar ou Recusar quando uma decisão crítica exigir confirmação humana.",
    whatHappensNext: "Itens aprovados avançam imediatamente no histórico auditável; recusados ficam bloqueados com registro.",
    whatAiDoes: "Agentes preparam campanhas, propostas e diagnósticos e enviam para esta fila quando exigem supervisão.",
    needsApprovalOrCreds: "Decisões financeiras e envios externos nunca executam sem seu clique em Aprovar.",
    recommendedLabel: "Ver Fila Completa",
    recommendedTarget: "my_work",
  },
  comercial: {
    title: "Guia Comercial — Leads, Propostas e Vendas",
    whatCanDo: "Cadastrar leads com consentimento LGPD, buscar contatos, mover negociações no funil e gerar propostas com PDF seguro.",
    howToStart: "Cadastre um lead em 'Leads & CRM' ou gere uma proposta comercial em 'Propostas, Contratos & 3 Unidades'.",
    whatToFill: "Nome do contato, e-mail corporativo, empresa e valor estimado para iniciar a qualificação automática.",
    whatHappensNext: "A IA calcula o Score do lead (0 a 100), cria tarefa de follow-up e coloca propostas na fila de aprovação.",
    whatAiDoes: "Qualifica oportunidades, estrutura preços pela tabela aprovada e monitora etapas do funil.",
    needsApprovalOrCreds: "Envio final de proposta vinculante e cobranças exigem sua aprovação; pagamentos Sandbox ficam isolados.",
    recommendedLabel: "Cadastrar Novo Lead",
    recommendedTarget: "crm",
  },
  marketing: {
    title: "Guia de Marketing — Campanhas, Conteúdo e SEO",
    whatCanDo: "Definir personas ideais, criar campanhas, gerar lote de 30 conteúdos ou agendar posts individuais no calendário.",
    howToStart: "Comece criando uma Persona ou Campanha em 'Campanhas & Personas' e gere peças em 'Fábrica de Conteúdo'.",
    whatToFill: "Nome da campanha, canal principal e orçamento planejado (ou apenas um título/tema no Calendário).",
    whatHappensNext: "Você baixa o pacote pronto em 1 clique ('Modo Assistido') ou publica ao conectar suas contas sociais.",
    whatAiDoes: "Gera textos persuasivos AIDA/PAS, imagens locais PNG, auditorias técnicas SEO e cronograma semanal.",
    needsApprovalOrCreds: "Publicação automática direta exige credencial social em Integrações; sem ela, o Modo Assistido funciona normalmente.",
    recommendedLabel: "Ir para Campanhas & Personas",
    recommendedTarget: "marketing",
  },
  ia: {
    title: "Guia de Inteligência Artificial — Agentes e Motores",
    whatCanDo: "Entender o papel dos 12 agentes, conectar sua chave gratuita do Google Gemini, testar conexão real e ajustar autonomia.",
    howToStart: "Siga os 3 passos do Assistente de Configuração abaixo (Chave Gratuita -> Testar Conexão -> Escolher Autonomia).",
    whatToFill: "Apenas sua chave gratuita do Google AI Studio (começa com 'AIzaSy...') se desejar ativar textos via LLM.",
    whatHappensNext: "Mesmo sem chave externa, rotinas determinísticas e proteções de custo continuam operando normalmente.",
    whatAiDoes: "Executa diagnósticos coordenados, cria copies e automatiza triagens dentro dos limites definidos.",
    needsApprovalOrCreds: "Trava financeira FREE_ONLY ativa por padrão: modelos pagos (GPT-4o, Imagen 3, Veo 2) ficam bloqueados automaticamente.",
    recommendedLabel: "Abrir Modelos & Provedores",
    recommendedTarget: "ai_engines",
  },
  gestao: {
    title: "Guia de Gestão — Empresa, Integrações e Relatórios",
    whatCanDo: "Configurar nome/marca da empresa, conectar integrações oficiais, revisar finanças reais e exportar backups.",
    howToStart: "Atualize os dados da sua empresa em 'Configurações & Planos' e revise as integrações desejadas.",
    whatToFill: "Nome da empresa, marca, nicho e credenciais apenas das integrações externas que desejar automatizar.",
    whatHappensNext: "Os agentes e o painel Início passam a refletir sua marca, relatórios consolidados e integrações ativas.",
    whatAiDoes: "Consolida receita real x importada x estimada sem inventar faturamento e gera relatórios executivos.",
    needsApprovalOrCreds: "Alterações financeiras e de plano ficam registradas na Auditoria Imutável; credenciais usam criptografia Fernet.",
    recommendedLabel: "Configurar Empresa & Marca",
    recommendedTarget: "settings",
  },
  todos_recursos: {
    title: "Guia da Central Completa de Recursos",
    whatCanDo: "Buscar qualquer ferramenta por nome ou palavra-chave, fixar seus favoritos e acessar últimos módulos.",
    howToStart: "Digite o que procura no campo de busca acima ou clique em uma categoria.",
    whatToFill: "Apenas a busca opcional ou clique na estrela para salvar módulos nos seus Favoritos.",
    whatHappensNext: "Clicar em 'Abrir' leva direto ao módulo desejado sem alterar a organização das 6 áreas.",
    whatAiDoes: "Exibe transparentemente quais módulos dependem de credenciais ou estão no Modo Assistido/Sandbox.",
    needsApprovalOrCreds: "Os cards mostram etiquetas claras do que está 100% operacional ou aguardando configuração.",
    recommendedLabel: "Voltar ao Início",
    recommendedTarget: "overview",
  },
};

export function AreaContextGuide({
  areaId,
  integrationsData,
  aiEnginesConfig,
  onNavigate,
}: {
  areaId: AreaId;
  integrationsData: any[];
  aiEnginesConfig: any;
  onNavigate: (view: LegacyMenuId) => void;
}) {
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setCollapsed(localStorage.getItem(`ug_ctx_guide_${areaId}`) === "1");
    }
  }, [areaId]);

  const toggleCollapsed = () => {
    const next = !collapsed;
    setCollapsed(next);
    if (typeof window !== "undefined") {
      if (next) localStorage.setItem(`ug_ctx_guide_${areaId}`, "1");
      else localStorage.removeItem(`ug_ctx_guide_${areaId}`);
    }
  };

  const guide = AREA_GUIDES[areaId] || AREA_GUIDES.inicio;
  const connectedCount = (integrationsData || []).filter((i: any) => i.status === "CONNECTED").length;
  const geminiProv = (aiEnginesConfig?.providers || []).find((p: any) => p.provider_key === "gemini");
  const aiReady = Boolean(geminiProv?.has_credential && geminiProv?.last_test_status === "CONNECTED");
  const lastErr = String(geminiProv?.last_test_error || "");
  const quotaBlocked = lastErr.includes("402") || lastErr.toLowerCase().includes("cota");

  let dependencyAlert: { text: string; tone: "ok" | "warn" } | null = null;
  if (areaId === "marketing") {
    dependencyAlert =
      connectedCount > 0
        ? { text: `${connectedCount} integração(ões) ativa(s). Contas sem OAuth operam em Modo Assistido (pacote 1-clique).`, tone: "ok" }
        : { text: "Nenhuma rede social conectada ainda: publicações automáticas externas usam Modo Assistido (você baixa e posta em 1 clique, sem simular envio).", tone: "warn" };
  } else if (areaId === "ia") {
    dependencyAlert = quotaBlocked
      ? { text: "Chave Gemini atual bloqueada por cota/faturamento (HTTP 402). Nenhuma cobrança foi feita; substitua por uma chave AIzaSy... Free Tier abaixo.", tone: "warn" }
      : aiReady
      ? { text: "Motor gratuito Gemini conectado e validado com trava FREE_ONLY ativa (zero cobrança inesperada).", tone: "ok" }
      : { text: "Nenhuma chave LLM validada agora: os agentes operam no modo determinístico seguro sem custos até você configurar o Gemini gratuito.", tone: "warn" };
  }

  return (
    <section
      aria-label="Orientação contextual da área"
      className="ug-card rounded-2xl border border-indigo-500/25 p-4 text-xs"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Compass className="w-4 h-4 text-indigo-400 shrink-0" aria-hidden="true" />
          <h4 className="font-bold text-white ug-text-primary">{guide.title}</h4>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => onNavigate(guide.recommendedTarget)}
            className="px-2.5 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/40 text-indigo-300 font-semibold inline-flex items-center gap-1"
          >
            <span>{guide.recommendedLabel}</span>
            <ArrowRight className="w-3 h-3" aria-hidden="true" />
          </button>
          <button
            type="button"
            onClick={toggleCollapsed}
            aria-expanded={!collapsed}
            aria-label={collapsed ? "Expandir orientação da área" : "Recolher orientação da área"}
            className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white inline-flex items-center gap-1"
          >
            <span>{collapsed ? "Como funciona?" : "Recolher guia"}</span>
            {collapsed ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {!collapsed && (
        <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
            <div className="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
              <div className="font-semibold text-indigo-300">O que você pode fazer aqui?</div>
              <p className="text-slate-300 leading-relaxed">{guide.whatCanDo}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
              <div className="font-semibold text-emerald-300">Como começo &amp; o que preencher?</div>
              <p className="text-slate-300 leading-relaxed">{guide.howToStart} {guide.whatToFill}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
              <div className="font-semibold text-sky-300">O que acontece depois?</div>
              <p className="text-slate-300 leading-relaxed">{guide.whatHappensNext}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1 md:col-span-1 lg:col-span-2">
              <div className="font-semibold text-purple-300 flex items-center gap-1">
                <Bot className="w-3.5 h-3.5" aria-hidden="true" />
                O que a IA pode fazer aqui?
              </div>
              <p className="text-slate-300 leading-relaxed">{guide.whatAiDoes}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
              <div className="font-semibold text-amber-300 flex items-center gap-1">
                <ShieldAlert className="w-3.5 h-3.5" aria-hidden="true" />
                Depende da sua aprovação?
              </div>
              <p className="text-slate-300 leading-relaxed">{guide.needsApprovalOrCreds}</p>
            </div>
          </div>

          {dependencyAlert && (
            <div
              className={`p-2.5 rounded-xl border flex items-center gap-2 text-[11px] ${
                dependencyAlert.tone === "ok"
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-200"
                  : "bg-amber-500/10 border-amber-500/30 text-amber-200"
              }`}
            >
              {dependencyAlert.tone === "ok" ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" aria-hidden="true" />
              ) : (
                <Info className="w-4 h-4 text-amber-400 shrink-0" aria-hidden="true" />
              )}
              <span>{dependencyAlert.text}</span>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
