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
    description: "Prioridades de hoje, metas, oportunidades e assistente ASK UNION.",
    defaultView: "overview",
    primaryCtaLabel: "Meu Trabalho",
    primaryCtaTarget: "my_work",
    subtabs: [],
  },
  {
    id: "meu_trabalho",
    label: "Meu Trabalho",
    description: "Fila unificada de tarefas, aprovações, alertas e execuções.",
    defaultView: "my_work",
    primaryCtaLabel: "Aprovações",
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
    description: "Leads, pipeline de vendas, propostas, clientes e mercado.",
    defaultView: "crm",
    primaryCtaLabel: "Novo Lead",
    primaryCtaTarget: "crm",
    subtabs: [
      { id: "crm", label: "Leads & CRM", shortDesc: "Captação LGPD, qualificação e pontuação automática", legacyNum: "13" },
      { id: "commercial", label: "Pipeline & Vendas", shortDesc: "Funil comercial e negociações ativas", legacyNum: "14" },
      { id: "multibusiness", label: "Propostas, Contratos & 3 Unidades", shortDesc: "Propostas PDF, ofertas e cobranças", legacyNum: "17M" },
      { id: "cs", label: "Relacionamento & CS", shortDesc: "Satisfação, saúde do cliente e retenção", legacyNum: "17" },
      { id: "competitors", label: "Concorrentes", shortDesc: "Monitoramento ético de mercado", legacyNum: "15" },
    ],
  },
  {
    id: "marketing",
    label: "Marketing",
    description: "Campanhas, conteúdo, calendário editorial, SEO e criativos.",
    defaultView: "marketing",
    primaryCtaLabel: "Criar Campanha",
    primaryCtaTarget: "marketing",
    subtabs: [
      { id: "marketing", label: "Campanhas & Personas", shortDesc: "Público ideal e campanhas multicanal", legacyNum: "03" },
      { id: "content_factory", label: "Fábrica de Conteúdo", shortDesc: "Produção mensal em lote (30 dias)", legacyNum: "06" },
      { id: "social", label: "Calendário & Redes", shortDesc: "Agenda editorial e publicação assistida", legacyNum: "05/18" },
      { id: "seo", label: "SEO & Artigos", shortDesc: "Auditoria técnica do site, palavras-chave e blog", legacyNum: "04" },
      { id: "creative", label: "Criativos", shortDesc: "Peças visuais e roteiros", legacyNum: "10" },
      { id: "copywriter", label: "Copywriting A/B", shortDesc: "Textos persuasivos e testes A/B", legacyNum: "11", advancedOnly: true },
      { id: "growth", label: "Growth & Testes", shortDesc: "Experimentos de conversão", legacyNum: "12", advancedOnly: true },
    ],
  },
  {
    id: "ia",
    label: "Inteligência Artificial",
    description: "Equipe de agentes, serviços de IA e automações 24/7.",
    defaultView: "ai_team_overview",
    primaryCtaLabel: "Serviços de IA",
    primaryCtaTarget: "ai_engines",
    subtabs: [
      { id: "ai_team_overview", label: "Visão & Agentes", shortDesc: "Papel dos 12 agentes e autonomia" },
      { id: "ai_engines", label: "Modelos & Provedores", shortDesc: "Serviços de IA conectados (Gemini gratuito, Groq e limites)", legacyNum: "25", advancedOnly: true },
      { id: "ceo", label: "AI CEO & Estratégia", shortDesc: "Briefings executivos e metas", legacyNum: "02" },
      { id: "automations", label: "Automações 24/7", shortDesc: "Rotinas automáticas em linguagem natural", legacyNum: "19" },
      { id: "operational247", label: "Monitoramento & Alertas", shortDesc: "Saúde contínua das rotinas e custos", legacyNum: "08", advancedOnly: true },
      { id: "pilot7d", label: "Piloto 7 Dias", shortDesc: "Simulação operacional de 7 dias", legacyNum: "09", advancedOnly: true },
    ],
  },
  {
    id: "gestao",
    label: "Gestão",
    description: "Financeiro, analytics, conexões externas, marca e planos.",
    defaultView: "finance",
    primaryCtaLabel: "Relatórios",
    primaryCtaTarget: "reports",
    subtabs: [
      { id: "finance", label: "Financeiro & ROI", shortDesc: "Receita real vs importada, custos e margem", legacyNum: "16" },
      { id: "reports", label: "Relatórios", shortDesc: "Indicadores, funil e atribuição", legacyNum: "21" },
      { id: "integrations", label: "Integrações", shortDesc: "Conectar ferramentas externas", legacyNum: "22" },
      { id: "settings", label: "Configurações & Planos", shortDesc: "Marca, empresas e autonomia", legacyNum: "23" },
      { id: "audit", label: "Auditoria & Logs", shortDesc: "Histórico completo de ações e segurança", legacyNum: "24", advancedOnly: true },
    ],
  },
];

export const RESOURCE_CATALOG: ResourceCatalogItem[] = [
  { id: "overview", area: "inicio", category: "Início & Trabalho", legacyNum: "01", name: "Início — Workspace Executivo", description: "Prioridades de hoje, ASK UNION, metas e oportunidades reais.", keywords: ["inicio", "home", "dashboard", "visao geral", "kpis"], statusHint: "OPERATIONAL" },
  { id: "my_work", area: "meu_trabalho", category: "Início & Trabalho", legacyNum: "NEW", name: "Meu Trabalho", description: "Fila unificada de tarefas, aprovações, alertas e execuções da IA.", keywords: ["trabalho", "tarefas", "pendencias", "inbox", "acoes"], statusHint: "OPERATIONAL" },
  { id: "crm", area: "comercial", category: "Comercial", legacyNum: "13", name: "Leads & CRM", description: "Cadastro de leads com LGPD, qualificação e pontuação automática.", keywords: ["crm", "leads", "contatos", "lgpd", "scoring"], statusHint: "OPERATIONAL" },
  { id: "commercial", area: "comercial", category: "Comercial", legacyNum: "14", name: "Pipeline de Vendas", description: "Gestão visual de negociações por etapa do funil.", keywords: ["pipeline", "vendas", "deals", "negociacoes", "funil"], statusHint: "OPERATIONAL" },
  { id: "multibusiness", area: "comercial", category: "Comercial", legacyNum: "17M", name: "Propostas, Contratos & 3 Unidades", description: "Propostas PDF seguras, contratos, cobranças Sandbox e entregas.", keywords: ["multinegocio", "propostas", "pdf", "contratos", "pagamentos", "landing pages", "unidades"], statusHint: "SANDBOX_MODE" },
  { id: "cs", area: "comercial", category: "Comercial", legacyNum: "17", name: "Relacionamento & CS", description: "Satisfação NPS/CSAT, detecção de risco e retenção.", keywords: ["cs", "customer success", "nps", "csat", "churn", "clientes"], statusHint: "OPERATIONAL" },
  { id: "competitors", area: "comercial", category: "Comercial", legacyNum: "15", name: "Inteligência Competitiva", description: "Análise ética de concorrentes e diferenciais.", keywords: ["concorrentes", "mercado", "battlecards"], statusHint: "OPERATIONAL" },
  { id: "marketing", area: "marketing", category: "Marketing", legacyNum: "03", name: "Campanhas & Personas", description: "Definição de público ideal e campanhas multicanal.", keywords: ["marketing", "cmo", "campanhas", "personas"], statusHint: "OPERATIONAL" },
  { id: "content_factory", area: "marketing", category: "Marketing", legacyNum: "06", name: "Fábrica de Conteúdo (30 Dias)", description: "Produção em lote de publicações mensais e pacote assistido.", keywords: ["content factory", "conteudo", "30 dias", "posts", "lote"], statusHint: "OPERATIONAL" },
  { id: "social", area: "marketing", category: "Marketing", legacyNum: "05/18", name: "Calendário Editorial & Redes", description: "Agenda de publicações e pacotes prontos em 1 clique.", keywords: ["redes sociais", "calendario", "editorial", "instagram", "linkedin", "agendar"], statusHint: "NEEDS_CREDENTIALS" },
  { id: "seo", area: "marketing", category: "Marketing", legacyNum: "04", name: "SEO Técnico & Artigos", description: "Auditoria real de sites, palavras-chave e artigos otimizados.", keywords: ["seo", "google", "auditoria", "artigos", "keywords", "blog"], statusHint: "OPERATIONAL" },
  { id: "creative", area: "marketing", category: "Marketing", legacyNum: "10", name: "Estúdio Criativo", description: "Artes PNG e roteiros programáticos hospedados localmente.", keywords: ["criativos", "creative", "imagens", "banners", "carrossel", "video"], statusHint: "OPERATIONAL" },
  { id: "copywriter", area: "marketing", category: "Marketing", legacyNum: "11", name: "Copywriter & Testes A/B", description: "Textos persuasivos e variantes A/B para anúncios e páginas.", keywords: ["copy", "copywriter", "textos", "anuncios", "emails", "ab"], statusHint: "OPERATIONAL" },
  { id: "growth", area: "marketing", category: "Marketing", legacyNum: "12", name: "Experimentos de Crescimento", description: "Hipóteses ICE e acompanhamento de conversão.", keywords: ["growth", "experimentos", "conversao", "ice"], statusHint: "OPERATIONAL" },
  { id: "ai_team_overview", area: "ia", category: "Inteligência Artificial", legacyNum: "NEW", name: "Equipe de Agentes & Autonomia", description: "Visão clara dos 12 agentes digitais e controle de supervisão.", keywords: ["agentes", "equipe ia", "autonomia", "orquestrador"], statusHint: "OPERATIONAL" },
  { id: "ai_engines", area: "ia", category: "Inteligência Artificial", legacyNum: "25", name: "Serviços de IA & Limites", description: "Conexão de Gemini gratuito, Groq e proteção contra cobranças pagas.", keywords: ["gemini", "gpt", "claude", "groq", "modelos", "provedores", "api key", "ia"], statusHint: "QUOTA_CHECK" },
  { id: "ceo", area: "ia", category: "Inteligência Artificial", legacyNum: "02", name: "AI CEO & Metas Estratégicas", description: "Briefings executivos e acompanhamento de objetivos.", keywords: ["ceo", "briefing", "metas", "okr", "estrategia"], statusHint: "OPERATIONAL" },
  { id: "ceo_plan", area: "meu_trabalho", category: "Inteligência Artificial", legacyNum: "07", name: "Plano Diário do AI CEO", description: "Prioridades recomendadas do dia com base nos dados reais.", keywords: ["plano diario", "prioridades", "rotina"], statusHint: "OPERATIONAL" },
  { id: "automations", area: "ia", category: "Inteligência Artificial", legacyNum: "19", name: "Automações 24/7", description: "Crie regras automáticas falando em português, 100% nativo Python.", keywords: ["automacoes", "cron", "scheduler", "python", "rotinas"], statusHint: "OPERATIONAL" },
  { id: "operational247", area: "ia", category: "Inteligência Artificial", legacyNum: "08", name: "Monitoramento Contínuo 24/7", description: "Saúde das rotinas automáticas e alertas do sistema.", keywords: ["alertas", "24/7", "monitoramento", "saude", "heartbeat"], statusHint: "OPERATIONAL" },
  { id: "pilot7d", area: "ia", category: "Inteligência Artificial", legacyNum: "09", name: "Piloto de 7 Dias", description: "Simulação guiada do ciclo operacional semanal.", keywords: ["piloto", "7 dias", "simulacao", "validacao"], statusHint: "OPERATIONAL" },
  { id: "approvals", area: "meu_trabalho", category: "Inteligência Artificial", legacyNum: "20", name: "Central de Aprovações", description: "Confirmação humana para ações externas e decisões financeiras.", keywords: ["aprovacoes", "governanca", "seguranca", "autorizacao"], statusHint: "OPERATIONAL" },
  { id: "finance", area: "gestao", category: "Gestão", legacyNum: "16", name: "Financeiro & ROI", description: "Receita real vs importada, custos e margem sem misturar simulações.", keywords: ["financeiro", "receita", "despesas", "roi", "roas", "cac", "ltv"], statusHint: "OPERATIONAL" },
  { id: "reports", area: "gestao", category: "Gestão", legacyNum: "21", name: "Relatórios & Analytics", description: "Funil comercial, atribuição por canal e relatórios executivos.", keywords: ["relatorios", "executivo", "exportar", "resumo", "analytics"], statusHint: "OPERATIONAL" },
  { id: "integrations", area: "gestao", category: "Gestão", legacyNum: "22", name: "Conectar Ferramentas Externas", description: "Redes sociais, Google, e-mail e meios de pagamento com criptografia.", keywords: ["integracoes", "credenciais", "oauth", "meta", "google", "smtp"], statusHint: "NEEDS_CREDENTIALS" },
  { id: "settings", area: "gestao", category: "Gestão", legacyNum: "23", name: "Marca, Empresas & Planos", description: "Central de Marca, empresas multi-tenant, autonomia e planos.", keywords: ["configuracoes", "planos", "empresas", "tenant", "autonomia", "marca"], statusHint: "OPERATIONAL" },
  { id: "audit", area: "gestao", category: "Gestão", legacyNum: "24", name: "Auditoria & Logs de Segurança", description: "Histórico completo e imutável das ações no sistema.", keywords: ["auditoria", "logs", "historico", "seguranca", "compliance"], statusHint: "OPERATIONAL" },
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
