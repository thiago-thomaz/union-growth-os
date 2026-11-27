"use client";

import React, { useState } from "react";
import { ArrowRight, Bot, CheckCircle2, HelpCircle, ShieldAlert } from "lucide-react";
import { AreaId, LegacyMenuId } from "@/lib/navigation";
import { Drawer } from "@/components/DesignSystem";

interface AreaGuideContent {
  title: string;
  whatCanDo: string;
  howToStart: string;
  whatHappensNext: string;
  whatAiDoes: string;
  needsApprovalOrCreds: string;
  recommendedLabel: string;
  recommendedTarget: LegacyMenuId;
}

const AREA_GUIDES: Record<AreaId, AreaGuideContent> = {
  inicio: {
    title: "Como funciona o Início",
    whatCanDo: "Acompanhe prioridades reais do dia, indicadores verificados e peça ajuda ao ASK UNION em linguagem natural.",
    howToStart: "Revise as Prioridades de hoje ou digite o que deseja resolver no campo ASK UNION.",
    whatHappensNext: "Cada item leva direto à ação correspondente sem navegar por menus técnicos.",
    whatAiDoes: "Lê empresa, marca, CRM, site e campanhas reais sem inventar dados.",
    needsApprovalOrCreds: "Cobranças, gastos ou publicações externas nunca executam sem sua aprovação.",
    recommendedLabel: "Abrir Meu Trabalho",
    recommendedTarget: "my_work",
  },
  meu_trabalho: {
    title: "Como funciona Meu Trabalho",
    whatCanDo: "Aprove solicitações da IA, resolva alertas e acompanhe tarefas comerciais em uma única lista.",
    howToStart: "Use as abas superiores ('Precisa de mim' ou 'Aguardando aprovação') e clique em um item.",
    whatHappensNext: "Itens aprovados avançam no histórico; recusados ficam bloqueados com registro.",
    whatAiDoes: "Agentes preparam campanhas, propostas e diagnósticos e enviam aqui quando exigem supervisão.",
    needsApprovalOrCreds: "Decisões financeiras e envios externos aguardam sua confirmação.",
    recommendedLabel: "Ver Central de Aprovações",
    recommendedTarget: "approvals",
  },
  comercial: {
    title: "Como funciona Comercial",
    whatCanDo: "Cadastre leads com consentimento LGPD, acompanhe negociações, gere propostas PDF e analise concorrentes.",
    howToStart: "Adicione um lead em Leads & CRM ou abra o Pipeline para mover oportunidades.",
    whatHappensNext: "A IA pontua leads automaticamente (0–100) e prepara tarefas de retorno.",
    whatAiDoes: "Qualifica oportunidades, estrutura propostas e monitora estágios sem perder contexto.",
    needsApprovalOrCreds: "Envio final de propostas e cobranças exigem sua aprovação.",
    recommendedLabel: "Cadastrar Novo Lead",
    recommendedTarget: "crm",
  },
  marketing: {
    title: "Como funciona Marketing",
    whatCanDo: "Defina seu público ideal, crie campanhas, produza conteúdos para 30 dias e audite seu site no Google (SEO).",
    howToStart: "Cadastre público e campanha em Campanhas & Personas e gere conteúdo na Fábrica.",
    whatHappensNext: "Baixe pacotes prontos em 1 clique ou publique após conectar suas redes sociais.",
    whatAiDoes: "Cria textos, roteiros, artes visuais e auditorias técnicas reais do seu site.",
    needsApprovalOrCreds: "Sem rede social conectada, o Modo Assistido libera tudo para copiar em 1 clique.",
    recommendedLabel: "Ir para Campanhas",
    recommendedTarget: "marketing",
  },
  ia: {
    title: "Como funciona Inteligência Artificial",
    whatCanDo: "Configure sua equipe de 12 agentes, ajuste autonomia e crie automações falando em português.",
    howToStart: "Descreva uma regra em Automações 24/7 ou ajuste permissões dos agentes.",
    whatHappensNext: "Tudo roda em Python nativo na própria nuvem, sem custos surpresa.",
    whatAiDoes: "Analisa negócio, prioriza ações, prepara conteúdos e monitora falhas 24/7.",
    needsApprovalOrCreds: "Trava gratuita (FREE_ONLY) ativa por padrão: modelos pagos permanecem bloqueados.",
    recommendedLabel: "Criar Automação",
    recommendedTarget: "automations",
  },
  gestao: {
    title: "Como funciona Gestão",
    whatCanDo: "Gerencie identidade da marca, empresas, financeiro real, relatórios, conecte ferramentas externas e auditoria.",
    howToStart: "Mantenha a Central de Marca atualizada para melhorar toda comunicação automática.",
    whatHappensNext: "Relatórios e o painel inicial refletem automaticamente os dados reais consolidados.",
    whatAiDoes: "Separa estritamente dados reais, projeções e simulações Sandbox.",
    needsApprovalOrCreds: "Alterações financeiras e de planos ficam registradas na auditoria.",
    recommendedLabel: "Configurações & Marca",
    recommendedTarget: "settings",
  },
  todos_recursos: {
    title: "Central de Descoberta",
    whatCanDo: "Encontre qualquer ferramenta por palavra-chave e fixe favoritos para acesso instantâneo.",
    howToStart: "Digite o que procura no campo de busca ou clique na estrela para favoritar.",
    whatHappensNext: "Os favoritos aparecem no menu lateral para abrir em 1 clique.",
    whatAiDoes: "Sinaliza com clareza quais integrações exigem conexão externa.",
    needsApprovalOrCreds: "Módulos principais operam mesmo sem conexões OAuth.",
    recommendedLabel: "Voltar ao Início",
    recommendedTarget: "overview",
  },
};

/**
 * Fase 24 — Substitui a muralha permanente de 5 caixas no topo das páginas
 * por um gatilho discreto sob demanda que abre um Drawer limpo quando o usuário quiser.
 */
export function AreaContextGuide({
  areaId,
  integrationsData,
  onNavigate,
}: {
  areaId: AreaId;
  integrationsData: any[];
  aiEnginesConfig?: any;
  onNavigate: (view: LegacyMenuId) => void;
}) {
  const [open, setOpen] = useState(false);
  const guide = AREA_GUIDES[areaId];
  if (!guide) return null;

  const connectedCount = (integrationsData || []).filter((i: any) => i.status === "CONNECTED").length;

  return (
    <>
      <div className="flex items-center justify-end">
        <button
          type="button"
          onClick={() => setOpen(true)}
          aria-label={`Abrir guia rápido: ${guide.title}`}
          className="inline-flex items-center gap-1.5 text-[11px] font-medium text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)] transition py-0.5"
        >
          <HelpCircle className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
          <span>Como funciona esta área</span>
          <span className="text-emerald-400 font-semibold">• {connectedCount} conexão(ões)</span>
        </button>
      </div>

      <Drawer
        open={open}
        onClose={() => setOpen(false)}
        title={guide.title}
        subtitle="Orientação rápida da área atual"
      >
        <div className="space-y-4 text-xs leading-relaxed">
          <div className="space-y-1">
            <div className="font-semibold text-[var(--ug-text-primary)]">O que você resolve aqui</div>
            <p className="text-[var(--ug-text-secondary)]">{guide.whatCanDo}</p>
          </div>

          <div className="space-y-1">
            <div className="font-semibold text-emerald-400">Como começar</div>
            <p className="text-[var(--ug-text-secondary)]">{guide.howToStart}</p>
          </div>

          <div className="space-y-1">
            <div className="font-semibold text-sky-400">O que acontece depois</div>
            <p className="text-[var(--ug-text-secondary)]">{guide.whatHappensNext}</p>
          </div>

          <div className="p-3.5 rounded-xl bg-white/[0.03] border border-[var(--ug-border)] space-y-1.5">
            <div className="font-semibold text-indigo-300 flex items-center gap-1.5">
              <Bot className="w-3.5 h-3.5" aria-hidden="true" /> O que a IA faz automaticamente
            </div>
            <p className="text-[var(--ug-text-secondary)]">{guide.whatAiDoes}</p>
          </div>

          <div className="p-3.5 rounded-xl bg-amber-500/8 border border-amber-500/20 space-y-1.5">
            <div className="font-semibold text-amber-300 flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5" aria-hidden="true" /> Segurança e Aprovação
            </div>
            <p className="text-[var(--ug-text-secondary)]">{guide.needsApprovalOrCreds}</p>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-[var(--ug-border)]">
            <span className="inline-flex items-center gap-1.5 text-emerald-400 text-[11px] font-medium">
              <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
              {connectedCount} integração(ões) ativa(s)
            </span>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                onNavigate(guide.recommendedTarget);
              }}
              className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium inline-flex items-center gap-1"
            >
              <span>{guide.recommendedLabel}</span>
              <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
            </button>
          </div>
        </div>
      </Drawer>
    </>
  );
}
