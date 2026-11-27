export type AreaId =
  | "inicio"
  | "meu_trabalho"
  | "comercial"
  | "marketing"
  | "ia"
  | "gestao"
  | "todos_recursos";

export type LegacyMenuId =
  | "overview"
  | "my_work"
  | "all_resources"
  | "ai_team_overview"
  | "multibusiness"
  | "ceo"
  | "marketing"
  | "seo"
  | "social"
  | "creative"
  | "copywriter"
  | "growth"
  | "crm"
  | "commercial"
  | "competitors"
  | "finance"
  | "cs"
  | "calendar"
  | "content_factory"
  | "ceo_plan"
  | "operational247"
  | "pilot7d"
  | "automations"
  | "approvals"
  | "reports"
  | "integrations"
  | "settings"
  | "audit"
  | "ai_engines";

export interface SubTabConfig {
  id: LegacyMenuId;
  label: string;
  shortDesc: string;
  legacyNum?: string;
  advancedOnly?: boolean;
}

export interface AreaConfig {
  id: AreaId;
  label: string;
  description: string;
  defaultView: LegacyMenuId;
  primaryCtaLabel: string;
  primaryCtaTarget: LegacyMenuId;
  subtabs: SubTabConfig[];
}

export interface ResourceCatalogItem {
  id: LegacyMenuId;
  area: AreaId;
  category: "Início & Trabalho" | "Comercial" | "Marketing" | "Inteligência Artificial" | "Gestão";
  legacyNum: string;
  name: string;
  description: string;
  keywords: string[];
  statusHint?: "OPERATIONAL" | "NEEDS_CREDENTIALS" | "SANDBOX_MODE" | "QUOTA_CHECK";
}

export const PRIMARY_AREAS: AreaConfig[] = [
  {
    id: "inicio",
    label: "Início",
    description: "Visão executiva do dia: prioridades, operação da IA e resultados reais.",
    defaultView: "overview",
    primaryCtaLabel: "Abrir Meu Trabalho",
    primaryCtaTarget: "my_work",
    subtabs: [],
  },
  {
    id: "meu_trabalho",
    label: "Meu Trabalho",
    description: "Central unificada de tarefas, aprovações, alertas e execuções da IA.",
    defaultView: "my_work",
    primaryCtaLabel: "Revisar Aprovações",
    primaryCtaTarget: "approvals",
    subtabs: [
      { id: "my_work", label: "Caixa de Ações", shortDesc: "Tudo o que precisa da sua atenção em um só lugar" },
      { id: "approvals", label: "Central de Aprovações", shortDesc: "Decisões formais de alto impacto", legacyNum: "20" },
      { id: "ceo_plan", label: "Plano Diário", shortDesc: "Prioridades executivas organizadas pelo AI CEO", legacyNum: "07" },
    ],
  },
  {
    id: "comercial",
    label: "Comercial",
    description: "Leads, pipeline de vendas, propostas, clientes e pós-venda.",
    defaultView: "crm",
    primaryCtaLabel: "Novo Lead",
    primaryCtaTarget: "crm",
    subtabs: [
      { id: "crm", label: "Leads & CRM", shortDesc: "Captação LGPD, qualificação e Lead Scoring", legacyNum: "13" },
      { id: "commercial", label: "Pipeline & Vendas", shortDesc: "Funil comercial e negociações ativas", legacyNum: "14" },
      { id: "multibusiness", label: "Propostas, Contratos & 3 Unidades", shortDesc: "Propostas PDF, ofertas, cobranças e entregas", legacyNum: "17M" },
      { id: "cs", label: "Relacionamento & CS", shortDesc: "NPS, CSAT, saúde do cliente e retenção", legacyNum: "17" },
      { id: "competitors", label: "Concorrentes", shortDesc: "Inteligência competitiva e battlecards", legacyNum: "15" },
    ],
  },
  {
    id: "marketing",
    label: "Marketing",
    description: "Campanhas, conteúdo em escala, calendário, SEO, criativos e growth.",
    defaultView: "marketing",
    primaryCtaLabel: "Criar Campanha",
    primaryCtaTarget: "marketing",
    subtabs: [
      { id: "marketing", label: "Campanhas & Personas", shortDesc: "Estratégia CMO, personas e campanhas", legacyNum: "03" },
      { id: "content_factory", label: "Fábrica de Conteúdo", shortDesc: "Produção mensal em lote (30 dias)", legacyNum: "06" },
      { id: "social", label: "Calendário & Redes", shortDesc: "Agenda editorial e publicação assistida", legacyNum: "05/18" },
      { id: "seo", label: "SEO & Artigos", shortDesc: "Auditoria técnica real, keywords e blog", legacyNum: "04" },
      { id: "creative", label: "Criativos", shortDesc: "Peças visuais PNG e vídeos MP4", legacyNum: "10" },
      { id: "copywriter", label: "Copywriting A/B", shortDesc: "Textos persuasivos e testes A/B", legacyNum: "11", advancedOnly: true },
      { id: "growth", label: "Growth & Testes", shortDesc: "Experimentos ICE e conversão", legacyNum: "12", advancedOnly: true },
    ],
  },
  {
    id: "ia",
    label: "Inteligência Artificial",
    description: "Equipe de agentes, modelos de IA, automações 24/7 e controle de autonomia.",
    defaultView: "ai_team_overview",
    primaryCtaLabel: "Configurar Motores de IA",
    primaryCtaTarget: "ai_engines",
    subtabs: [
      { id: "ai_team_overview", label: "Visão & Agentes", shortDesc: "Entenda o que cada agente faz e controle a autonomia" },
      { id: "ai_engines", label: "Modelos & Provedores", shortDesc: "Google Gemini gratuito, GPT, Claude, Groq e limites", legacyNum: "25", advancedOnly: true },
      { id: "ceo", label: "AI CEO & Estratégia", shortDesc: "Briefings executivos e metas OKR", legacyNum: "02" },
      { id: "automations", label: "Automações 24/7", shortDesc: "Rotinas nativas em Python (sem n8n)", legacyNum: "19" },
      { id: "operational247", label: "Monitoramento & Alertas", shortDesc: "Saúde do scheduler, heartbeats e custos", legacyNum: "08", advancedOnly: true },
      { id: "pilot7d", label: "Piloto 7 Dias", shortDesc: "Simulação operacional assistida de 7 dias", legacyNum: "09", advancedOnly: true },
    ],
  },
  {
    id: "gestao",
    label: "Gestão",
    description: "Financeiro, relatórios, integrações, auditoria e configurações da conta.",
    defaultView: "finance",
    primaryCtaLabel: "Gerar Relatório",
    primaryCtaTarget: "reports",
    subtabs: [
      { id: "finance", label: "Financeiro & ROI", shortDesc: "Receita real vs importada, despesas, CAC e LTV", legacyNum: "16" },
      { id: "reports", label: "Relatórios", shortDesc: "Relatórios executivos auditáveis", legacyNum: "21" },
      { id: "integrations", label: "Integrações", shortDesc: "Credenciais OAuth, APIs e canais externos", legacyNum: "22" },
      { id: "settings", label: "Configurações & Planos", shortDesc: "Autonomia, empresas multi-tenant e planos", legacyNum: "23" },
      { id: "audit", label: "Auditoria & Logs", shortDesc: "Trilha imutável de ações e segurança", legacyNum: "24", advancedOnly: true },
    ],
  },
];

export const RESOURCE_CATALOG: ResourceCatalogItem[] = [
  { id: "overview", area: "inicio", category: "Início & Trabalho", legacyNum: "01", name: "Início — Painel Executivo", description: "Visão principal com prioridades do dia, operação da IA e resultados reais.", keywords: ["inicio", "home", "dashboard", "visao geral", "kpis"], statusHint: "OPERATIONAL" },
  { id: "my_work", area: "meu_trabalho", category: "Início & Trabalho", legacyNum: "NEW", name: "Meu Trabalho — Caixa Unificada", description: "Central de tarefas, aprovações, alertas e execuções da IA com filtros rápidos.", keywords: ["trabalho", "tarefas", "pendencias", "inbox", "acoes"], statusHint: "OPERATIONAL" },
  { id: "crm", area: "comercial", category: "Comercial", legacyNum: "13", name: "CRM & Gestão de Leads", description: "Cadastro de leads com consentimento LGPD, qualificação e Lead Scoring automático.", keywords: ["crm", "leads", "contatos", "lgpd", "scoring"], statusHint: "OPERATIONAL" },
  { id: "commercial", area: "comercial", category: "Comercial", legacyNum: "14", name: "Pipeline Comercial & Oportunidades", description: "Gestão visual de negociações por etapa do funil de vendas.", keywords: ["pipeline", "vendas", "deals", "negociacoes", "funil"], statusHint: "OPERATIONAL" },
  { id: "multibusiness", area: "comercial", category: "Comercial", legacyNum: "17M", name: "Sistema Comercial Multinegócio (3 Unidades)", description: "UNION TECH, AGENCY e PARTNERS: propostas PDF seguras, contratos, cobranças Sandbox e entregas.", keywords: ["multinegocio", "propostas", "pdf", "contratos", "pagamentos", "landing pages", "unidades"], statusHint: "SANDBOX_MODE" },
  { id: "cs", area: "comercial", category: "Comercial", legacyNum: "17", name: "Customer Success & Pós-Venda", description: "Pesquisas de NPS/CSAT, detecção de risco de churn e ações de retenção.", keywords: ["cs", "customer success", "nps", "csat", "churn", "clientes"], statusHint: "OPERATIONAL" },
  { id: "competitors", area: "comercial", category: "Comercial", legacyNum: "15", name: "Inteligência Competitiva", description: "Monitoramento ético de concorrentes, diferenciais e battlecards.", keywords: ["concorrentes", "mercado", "battlecards"], statusHint: "OPERATIONAL" },
  { id: "marketing", area: "marketing", category: "Marketing", legacyNum: "03", name: "Campanhas & Personas (AI CMO)", description: "Criação de personas ideais e estruturação de campanhas multicanal.", keywords: ["marketing", "cmo", "campanhas", "personas"], statusHint: "OPERATIONAL" },
  { id: "content_factory", area: "marketing", category: "Marketing", legacyNum: "06", name: "Fábrica de Conteúdo (30 Dias)", description: "Geração em lote de peças mensais com controle anti-duplicação e pacote assistido.", keywords: ["content factory", "conteudo", "30 dias", "posts", "lote"], statusHint: "OPERATIONAL" },
  { id: "social", area: "marketing", category: "Marketing", legacyNum: "05/18", name: "Calendário Editorial & Redes Sociais", description: "Planejamento de publicações multicanal com fila de aprovação e exportação assistida.", keywords: ["redes sociais", "calendario", "editorial", "instagram", "linkedin", "agendar"], statusHint: "NEEDS_CREDENTIALS" },
  { id: "seo", area: "marketing", category: "Marketing", legacyNum: "04", name: "SEO Técnico & Artigos", description: "Auditoria HTTP real de sites, clusters de palavras-chave e geração de artigos otimizados.", keywords: ["seo", "google", "auditoria", "artigos", "keywords", "blog"], statusHint: "OPERATIONAL" },
  { id: "creative", area: "marketing", category: "Marketing", legacyNum: "10", name: "Creative Studio (Artes & Vídeos)", description: "Criação de peças visuais PNG e vídeos MP4 programáticos hospedados localmente.", keywords: ["criativos", "creative", "imagens", "banners", "carrossel", "video"], statusHint: "OPERATIONAL" },
  { id: "copywriter", area: "marketing", category: "Marketing", legacyNum: "11", name: "Copywriter & Testes A/B", description: "Headlines, landing pages, anúncios e e-mails com variantes A/B (AIDA, PAS, BAB).", keywords: ["copy", "copywriter", "textos", "anuncios", "emails", "ab"], statusHint: "OPERATIONAL" },
  { id: "growth", area: "marketing", category: "Marketing", legacyNum: "12", name: "Growth Hacker & Experimentos", description: "Registro de hipóteses ICE Score, testes de conversão e declaração de vencedores.", keywords: ["growth", "experimentos", "conversao", "ice"], statusHint: "OPERATIONAL" },
  { id: "ai_team_overview", area: "ia", category: "Inteligência Artificial", legacyNum: "NEW", name: "Equipe de Agentes & Autonomia", description: "Visão simplificada dos agentes de IA, permissões, dados utilizados e execução sob demanda.", keywords: ["agentes", "equipe ia", "autonomia", "orquestrador"], statusHint: "OPERATIONAL" },
  { id: "ai_engines", area: "ia", category: "Inteligência Artificial", legacyNum: "25", name: "UNION AI ENGINE HUB (Motores de IA)", description: "Central multimotor (Google Gemini gratuito, OpenAI, Claude, Groq), trava FREE_ONLY e custos.", keywords: ["gemini", "gpt", "claude", "groq", "modelos", "provedores", "api key", "ia"], statusHint: "QUOTA_CHECK" },
  { id: "ceo", area: "ia", category: "Inteligência Artificial", legacyNum: "02", name: "AI CEO & Metas Estratégicas", description: "Briefings executivos diários e acompanhamento de metas comerciais OKR.", keywords: ["ceo", "briefing", "metas", "okr", "estrategia"], statusHint: "OPERATIONAL" },
  { id: "ceo_plan", area: "meu_trabalho", category: "Inteligência Artificial", legacyNum: "07", name: "Plano Diário do AI CEO", description: "Lista priorizada de ações recomendadas do dia gerada a partir do estado real da conta.", keywords: ["plano diario", "prioridades", "rotina"], statusHint: "OPERATIONAL" },
  { id: "automations", area: "ia", category: "Inteligência Artificial", legacyNum: "19", name: "Automações Nativas Python 24/7", description: "Rotinas agendadas no APScheduler com idempotência e retry automático (zero n8n).", keywords: ["automacoes", "cron", "scheduler", "python", "rotinas"], statusHint: "OPERATIONAL" },
  { id: "operational247", area: "ia", category: "Inteligência Artificial", legacyNum: "08", name: "Painel 24/7, Alertas & Custos", description: "Monitoramento contínuo de heartbeats, alertas operacionais e custos de recursos.", keywords: ["alertas", "24/7", "monitoramento", "saude", "heartbeat"], statusHint: "OPERATIONAL" },
  { id: "pilot7d", area: "ia", category: "Inteligência Artificial", legacyNum: "09", name: "Piloto Operacional de 7 Dias", description: "Simulação guiada e histórico de validação do ciclo operacional semanal.", keywords: ["piloto", "7 dias", "simulacao", "validacao"], statusHint: "OPERATIONAL" },
  { id: "approvals", area: "meu_trabalho", category: "Inteligência Artificial", legacyNum: "20", name: "Central de Aprovações Humanas", description: "Fila de governança para aprovar ou recusar ações externas e de alto impacto.", keywords: ["aprovacoes", "governanca", "seguranca", "autorizacao"], statusHint: "OPERATIONAL" },
  { id: "finance", area: "gestao", category: "Gestão", legacyNum: "16", name: "Financeiro, CAC, LTV & ROI", description: "Lançamentos financeiros, margem líquida e separação estrita Real vs Importado vs Simulação.", keywords: ["financeiro", "receita", "despesas", "roi", "roas", "cac", "ltv"], statusHint: "OPERATIONAL" },
  { id: "reports", area: "gestao", category: "Gestão", legacyNum: "21", name: "Relatórios Executivos", description: "Consolidação executiva de desempenho comercial, marketing e operação.", keywords: ["relatorios", "executivo", "exportar", "resumo"], statusHint: "OPERATIONAL" },
  { id: "integrations", area: "gestao", category: "Gestão", legacyNum: "22", name: "Central de Integrações & Credenciais", description: "Conexão segura com redes sociais, anúncios, e-mail e gateways com status transparente.", keywords: ["integracoes", "credenciais", "oauth", "meta", "google", "smtp"], statusHint: "NEEDS_CREDENTIALS" },
  { id: "settings", area: "gestao", category: "Gestão", legacyNum: "23", name: "Configurações, Planos & Empresas", description: "Gestão multi-tenant isolada, níveis de autonomia, marca e planos SaaS.", keywords: ["configuracoes", "planos", "empresas", "tenant", "autonomia", "marca"], statusHint: "OPERATIONAL" },
  { id: "audit", area: "gestao", category: "Gestão", legacyNum: "24", name: "Auditoria & Logs de Segurança", description: "Histórico auditável de todas as ações de usuários, aprovações e alterações críticas.", keywords: ["auditoria", "logs", "historico", "seguranca", "compliance"], statusHint: "OPERATIONAL" },
];

export function getAreaForView(viewId: LegacyMenuId): AreaId {
  if (viewId === "overview") return "inicio";
  if (viewId === "all_resources") return "todos_recursos";
  if (viewId === "calendar") return "marketing";
  for (const area of PRIMARY_AREAS) {
    if (area.defaultView === viewId || area.subtabs.some((t) => t.id === viewId)) {
      return area.id;
    }
  }
  return "inicio";
}

export function getResourceMeta(viewId: LegacyMenuId): ResourceCatalogItem | undefined {
  if (viewId === "calendar") return RESOURCE_CATALOG.find((r) => r.id === "social");
  return RESOURCE_CATALOG.find((r) => r.id === viewId);
}
