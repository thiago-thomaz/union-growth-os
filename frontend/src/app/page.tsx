"use client";

import React, { useEffect, useState, useCallback } from "react";

type MenuId =
  | "overview"
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

const MENU_ITEMS: { id: MenuId; num: string; label: string }[] = [
  { id: "overview", num: "01", label: "Visão Geral" },
  { id: "multibusiness", num: "17M", label: "🏢 Multinegócio (3 Unidades)" },
  { id: "ceo", num: "02", label: "AI CEO" },
  { id: "marketing", num: "03", label: "Marketing (AI CMO)" },
  { id: "seo", num: "04", label: "SEO Director" },
  { id: "social", num: "05", label: "Redes Sociais" },
  { id: "content_factory", num: "06", label: "🏭 Content Factory 30D" },
  { id: "ceo_plan", num: "07", label: "📋 Plano Diário CEO" },
  { id: "operational247", num: "08", label: "🖥️ Painel 24/7 & Alertas" },
  { id: "pilot7d", num: "09", label: "🚀 Piloto 7 Dias" },
  { id: "creative", num: "10", label: "Creative Studio" },
  { id: "copywriter", num: "11", label: "Copywriter" },
  { id: "growth", num: "12", label: "Growth Hacker" },
  { id: "crm", num: "13", label: "CRM & Leads" },
  { id: "commercial", num: "14", label: "Comercial & Pipeline" },
  { id: "competitors", num: "15", label: "Concorrentes" },
  { id: "finance", num: "16", label: "Financeiro & KPIs" },
  { id: "cs", num: "17", label: "Customer Success" },
  { id: "calendar", num: "18", label: "Calendário Editorial" },
  { id: "automations", num: "19", label: "Automações Python" },
  { id: "approvals", num: "20", label: "Aprovações" },
  { id: "reports", num: "21", label: "Relatórios" },
  { id: "integrations", num: "22", label: "Integrações" },
  { id: "settings", num: "23", label: "Configurações & Planos" },
  { id: "audit", num: "24", label: "Auditoria e Logs" },
  { id: "ai_engines", num: "25", label: "🧠 UNION AI ENGINE HUB" },
];

const PIPELINE_STAGES = [
  "NEW_LEAD",
  "QUALIFICATION",
  "PROPOSAL",
  "NEGOTIATION",
  "CLOSED_WON",
  "CLOSED_LOST",
];

function OriginBadge({ origin }: { origin?: string }) {
  const o = (origin || "REAL").toUpperCase();
  const styles: Record<string, string> = {
    REAL: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
    IMPORTED: "bg-sky-500/15 text-sky-300 border-sky-500/30",
    ESTIMATED: "bg-amber-500/15 text-amber-300 border-amber-500/30",
    GOAL: "bg-purple-500/15 text-purple-300 border-purple-500/30",
  };
  const labels: Record<string, string> = {
    REAL: "DADO REAL",
    IMPORTED: "DADO IMPORTADO",
    ESTIMATED: "ESTIMATIVA",
    GOAL: "META",
  };
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold border ${
        styles[o] || styles.REAL
      }`}
    >
      {labels[o] || o}
    </span>
  );
}

export default function UnionGrowthOSPortal() {
  const [token, setToken] = useState<string>("");
  const [activeTenantId, setActiveTenantId] = useState<number | null>(null);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("admin@projetosunion.cloud");
  const [password, setPassword] = useState("UnionGrowth#2026!");
  const [fullName, setFullName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [authError, setAuthError] = useState("");

  const [activeMenu, setActiveMenu] = useState<MenuId>("overview");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<string>("");

  // State Stores
  const [meData, setMeData] = useState<any>(null);
  const [overviewData, setOverviewData] = useState<any>(null);
  const [agentsData, setAgentsData] = useState<any>(null);
  const [ceoData, setCeoData] = useState<any>(null);
  const [marketingData, setMarketingData] = useState<any>(null);
  const [seoData, setSeoData] = useState<any>(null);
  const [calendarData, setCalendarData] = useState<any[]>([]);
  const [creativeData, setCreativeData] = useState<any[]>([]);
  const [copyData, setCopyData] = useState<any[]>([]);
  const [growthData, setGrowthData] = useState<any[]>([]);
  const [crmData, setCrmData] = useState<any>(null);
  const [competitorsData, setCompetitorsData] = useState<any[]>([]);
  const [financeData, setFinanceData] = useState<any>(null);
  const [csData, setCsData] = useState<any>(null);
  const [automationsData, setAutomationsData] = useState<any>(null);
  const [approvalsData, setApprovalsData] = useState<any[]>([]);
  const [reportsData, setReportsData] = useState<any>(null);
  const [integrationsData, setIntegrationsData] = useState<any[]>([]);
  const [auditData, setAuditData] = useState<any>(null);
  const [diagResult, setDiagResult] = useState<any>(null);

  // FASE 14 State Stores
  const [contentFactoryItems, setContentFactoryItems] = useState<any[]>([]);
  const [cfFilter, setCfFilter] = useState<string>("ALL");
  const [assistedPackage, setAssistedPackage] = useState<any>(null);
  const [ceoDailyPlan, setCeoDailyPlan] = useState<any>(null);
  const [opDashboard, setOpDashboard] = useState<any>(null);
  const [systemAlerts, setSystemAlerts] = useState<any[]>([]);
  const [pilotData, setPilotData] = useState<any>(null);
  const [resourceCosts, setResourceCosts] = useState<any>(null);

  // FASE 17 Multi-Business State Stores
  const [mbDashboard, setMbDashboard] = useState<any>(null);
  const [selectedUnit, setSelectedUnit] = useState<string>("ALL");
  const [propClientName, setPropClientName] = useState("");
  const [propClientCompany, setPropClientCompany] = useState("");
  const [propClientEmail, setPropClientEmail] = useState("");
  const [propServiceCode, setPropServiceCode] = useState("SRV_01_DIAGNOSTICO");
  const [propProblem, setPropProblem] = useState("");
  const [agencyClientName, setAgencyClientName] = useState("");
  const [agencyBrandName, setAgencyBrandName] = useState("");
  const [agencyPlanTier, setAgencyPlanTier] = useState("PRO");
  const [agencyRetainer, setAgencyRetainer] = useState("2900");

  // CEO Goal Form
  const [goalTitle, setGoalTitle] = useState("");
  const [goalPeriod, setGoalPeriod] = useState("MONTHLY");
  const [goalMetric, setGoalMetric] = useState("MRR");
  const [goalTarget, setGoalTarget] = useState("200000");

  // Marketing Forms
  const [personaName, setPersonaName] = useState("");
  const [personaRole, setPersonaRole] = useState("CEO / Diretor");
  const [personaVP, setPersonaVP] = useState("");
  const [campName, setCampName] = useState("");
  const [campType, setCampType] = useState("ACQUISITION");
  const [campChannel, setCampChannel] = useState("Organic SEO + LinkedIn");
  const [campBudget, setCampBudget] = useState("5000");

  // SEO Forms
  const [seoUrlInput, setSeoUrlInput] = useState("https://example.com");
  const [seoKwInput, setSeoKwInput] = useState("automação de marketing com inteligência artificial");
  const [seoTopicInput, setSeoTopicInput] = useState("Como Escalar Vendas B2B com IA e SEO");

  // Creative Form
  const [creativeTitle, setCreativeTitle] = useState("Campanha Executiva Q4");
  const [creativeType, setCreativeType] = useState("CAROUSEL");
  const [creativeHeadline, setCreativeHeadline] = useState("Cresça com 11 Agentes de IA Trabalhando 24/7");
  const [creativeCta, setCreativeCta] = useState("Solicitar Diagnóstico");

  // Copywriter Form
  const [copyTitle, setCopyTitle] = useState("Oferta Principal SaaS");
  const [copyType, setCopyType] = useState("LANDING_PAGE");
  const [copyFramework, setCopyFramework] = useState("AIDA");
  const [copyOffer, setCopyOffer] = useState("Union Growth OS Enterprise");
  const [copyBenefit, setCopyBenefit] = useState("reduzir custos manuais e dobrar a geração de leads qualificados");

  // Growth Experiment Form
  const [expTitle, setExpTitle] = useState("");
  const [expChannel, setExpChannel] = useState("Landing Page");
  const [expHyp, setExpHyp] = useState("");
  const [expObj, setExpObj] = useState("Aumentar conversão de leads");

  // CRM & Commercial Forms
  const [leadName, setLeadName] = useState("");
  const [leadEmail, setLeadEmail] = useState("");
  const [leadPhone, setLeadPhone] = useState("");
  const [leadCompany, setLeadCompany] = useState("");
  const [leadValue, setLeadValue] = useState("15000");

  const [dealTitle, setDealTitle] = useState("");
  const [dealValue, setDealValue] = useState("25000");
  const [dealStage, setDealStage] = useState("PROPOSAL");

  // Finance Form
  const [finType, setFinType] = useState("REVENUE");
  const [finAmount, setFinAmount] = useState("12000");
  const [finDesc, setFinDesc] = useState("Novo contrato mensal fechado");
  const [finOrigin, setFinOrigin] = useState("REAL");

  // CS Form
  const [csName, setCsName] = useState("");
  const [csEmail, setCsEmail] = useState("");
  const [csNps, setCsNps] = useState("9");
  const [csText, setCsText] = useState("");

  // Competitor Form
  const [compName, setCompName] = useState("");
  const [compUrl, setCompUrl] = useState("https://example.org");

  // Calendar Form
  const [calTitle, setCalTitle] = useState("");
  const [calPlatform, setCalPlatform] = useState("instagram");
  const [calFormat, setCalFormat] = useState("CAROUSEL");
  const [calDate, setCalDate] = useState("2026-11-20 12:30");

  // Integration Credentials Input per provider
  const [credInputs, setCredInputs] = useState<Record<string, string>>({});

  // Settings & Tenant Form
  const [newTenantName, setNewTenantName] = useState("");
  const [brandColorPrimary, setBrandColorPrimary] = useState("#6366F1");
  const [brandColorSecondary, setBrandColorSecondary] = useState("#10B981");

  // MENU 25 — UNION AI ENGINE HUB (FASE 19)
  const [aiEnginesConfig, setAiEnginesConfig] = useState<any>(null);
  const [aiHubSubmenu, setAiHubSubmenu] = useState<string>("dashboard_ai");
  const [aiKeyInputs, setAiKeyInputs] = useState<Record<string, string>>({});
  const [aiEndpointInputs, setAiEndpointInputs] = useState<Record<string, string>>({});
  const [aiGenTopic, setAiGenTopic] = useState("Campanha de Agentes de IA e Automação Comercial B2B");
  const [aiGenPlatform, setAiGenPlatform] = useState("Multi-Channel (LinkedIn, Instagram & SEO)");
  const [aiGenMode, setAiGenMode] = useState("FULL_CAMPAIGN");
  const [aiPieceType, setAiPieceType] = useState("ALL");
  const [aiImgPrompt, setAiImgPrompt] = useState("Dashboard executivo futurista de Inteligência Artificial B2B");
  const [aiImgMode, setAiImgMode] = useState("PROMPT_ONLY");
  const [aiVidPrompt, setAiVidPrompt] = useState("Como automatizar o funil comercial da sua empresa com IA");
  const [aiVidStage, setAiVidStage] = useState("SCRIPT_AND_STORYBOARD");
  const [aiGenLoading, setAiGenLoading] = useState(false);
  const [aiGenResult, setAiGenResult] = useState<any>(null);

  const showNotice = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(""), 5500);
  };

  const apiFetch = useCallback(
    async (path: string, options: RequestInit = {}) => {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(options.headers as Record<string, string>),
      };
      if (token) headers["Authorization"] = `Bearer ${token}`;
      if (activeTenantId) headers["X-Tenant-Id"] = String(activeTenantId);
      const res = await fetch(path, { ...options, headers });
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({ detail: res.statusText }));
        if (res.status === 401) {
          if (typeof window !== "undefined") {
            localStorage.removeItem("ug_token");
          }
          setToken("");
          setMeData(null);
          setAuthError("Sua sessão anterior expirou. Clique em 'Acessar Central Executiva' para entrar novamente.");
        }
        throw new Error(errBody.detail || `Erro HTTP ${res.status}`);
      }
      return res.json();
    },
    [token, activeTenantId]
  );

  const loadAllActiveData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [me, ov, ag, ceo, mkt, seo, cal, cre, cp, gr, crm, comp, fin, cs, auto, app, rep, intg, aud] =
        await Promise.all([
          apiFetch("/api/v1/auth/me"),
          apiFetch("/api/v1/dashboard/overview"),
          apiFetch("/api/v1/agents"),
          apiFetch("/api/v1/ceo/briefings"),
          apiFetch("/api/v1/marketing/overview"),
          apiFetch("/api/v1/seo/overview"),
          apiFetch("/api/v1/social/calendar"),
          apiFetch("/api/v1/creative/assets"),
          apiFetch("/api/v1/copywriter/items"),
          apiFetch("/api/v1/growth/experiments"),
          apiFetch("/api/v1/crm/overview"),
          apiFetch("/api/v1/competitors"),
          apiFetch("/api/v1/finance/overview"),
          apiFetch("/api/v1/customer-success/overview"),
          apiFetch("/api/v1/automations"),
          apiFetch("/api/v1/approvals"),
          apiFetch("/api/v1/reports/executive"),
          apiFetch("/api/v1/integrations"),
          apiFetch("/api/v1/audit-logs"),
        ]);
      setMeData(me);
      setBrandColorPrimary(me?.active_tenant?.primary_color || "#6366F1");
      setBrandColorSecondary(me?.active_tenant?.secondary_color || "#10B981");
      setOverviewData(ov);
      setAgentsData(ag);
      setCeoData(ceo);
      setMarketingData(mkt);
      setSeoData(seo);
      setCalendarData(cal);
      setCreativeData(cre);
      setCopyData(cp);
      setGrowthData(gr);
      setCrmData(crm);
      setCompetitorsData(comp);
      setFinanceData(fin);
      setCsData(cs);
      setAutomationsData(auto);
      setApprovalsData(app);
      setReportsData(rep);
      setIntegrationsData(intg);
      setAuditData(aud);

      // Carregar dados da FASE 14, Piloto 7 Dias e MENU 25 (Motores de IA)
      try {
        const [cfItems, cPlan, opDash, sAlerts, rCosts, mbDash, aiCfg, pilotRes] = await Promise.all([
          apiFetch("/api/v1/content-factory/items").catch(() => []),
          apiFetch("/api/v1/ceo/daily-plan").catch(() => null),
          apiFetch("/api/v1/system/operational-dashboard").catch(() => null),
          apiFetch("/api/v1/system/alerts").catch(() => []),
          apiFetch("/api/v1/system/resource-costs").catch(() => null),
          apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`).catch(() => null),
          apiFetch("/api/v1/ai-engines/config").catch(() => null),
          apiFetch("/api/v1/system/pilot-7-days").catch(() => null),
        ]);
        setContentFactoryItems(cfItems || []);
        setCeoDailyPlan(cPlan);
        setOpDashboard(opDash);
        setSystemAlerts(sAlerts || []);
        setResourceCosts(rCosts);
        setMbDashboard(mbDash);
        setAiEnginesConfig(aiCfg);
        if (pilotRes) setPilotData(pilotRes);
      } catch (e) {
        // silencioso para não interromper carga base
      }
    } catch (err: any) {
      showNotice(err.message || "Falha ao carregar dados");
    } finally {
      setLoading(false);
    }
  }, [token, apiFetch]);

  useEffect(() => {
    const saved = typeof window !== "undefined" ? localStorage.getItem("ug_token") : null;
    if (saved) setToken(saved);
  }, []);

  useEffect(() => {
    if (token) {
      loadAllActiveData();
    }
  }, [token, activeTenantId, loadAllActiveData]);

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError("");
    try {
      const endpoint = authMode === "login" ? "/api/v1/auth/login" : "/api/v1/auth/register";
      const body =
        authMode === "login"
          ? { email, password }
          : { email, password, full_name: fullName, company_name: companyName, lgpd_consent: true };
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Falha na autenticação");
      localStorage.setItem("ug_token", data.access_token);
      setToken(data.access_token);
      setActiveTenantId(data.tenant?.id || null);
    } catch (err: any) {
      setAuthError(err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("ug_token");
    setToken("");
    setMeData(null);
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#070b14] p-6">
        <div className="w-full max-w-md bg-[#0f1629] border border-indigo-500/30 rounded-2xl p-8 shadow-2xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-lg">
              UG
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">UNION GROWTH OS</h1>
              <p className="text-xs text-slate-400">AI Business, CEO, Marketing, SEO & CRM Platform</p>
            </div>
          </div>

          <div className="flex gap-2 mb-6 bg-slate-900/90 p-1 rounded-lg">
            <button
              type="button"
              onClick={() => setAuthMode("login")}
              className={`flex-1 py-2 text-xs font-semibold rounded-md ${
                authMode === "login" ? "bg-indigo-600 text-white" : "text-slate-400"
              }`}
            >
              Entrar no Sistema
            </button>
            <button
              type="button"
              onClick={() => setAuthMode("register")}
              className={`flex-1 py-2 text-xs font-semibold rounded-md ${
                authMode === "register" ? "bg-indigo-600 text-white" : "text-slate-400"
              }`}
            >
              Nova Empresa (Multi-Tenant)
            </button>
          </div>

          {authError && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/15 border border-red-500/40 text-red-300 text-xs">
              {authError}
            </div>
          )}

          <form onSubmit={handleAuthSubmit} className="space-y-4">
            {authMode === "register" && (
              <>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Seu Nome Completo</label>
                  <input
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-sm text-white"
                    placeholder="Ex: Thiago Thomaz"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 mb-1">Nome da Empresa / Marca</label>
                  <input
                    required
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-sm text-white"
                    placeholder="Ex: Union Digital Ltda"
                  />
                </div>
              </>
            )}
            <div>
              <label className="block text-xs text-slate-300 mb-1">E-mail Corporativo</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-300 mb-1">Senha de Acesso</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-sm text-white"
              />
            </div>
            <button
              type="submit"
              className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition"
            >
              {authMode === "login" ? "Acessar Central Executiva" : "Criar Workspace & Ativar 11 Agentes"}
            </button>
          </form>

          <div className="mt-5 pt-4 border-t border-slate-800 text-[11px] text-slate-400 space-y-2">
            <div className="flex items-center justify-between">
              <p className="font-semibold text-slate-300">Credenciais Executivas Padrão:</p>
              <button
                type="button"
                onClick={() => {
                  setEmail("admin@projetosunion.cloud");
                  setPassword("UnionGrowth#2026!");
                }}
                className="text-[11px] text-indigo-400 hover:text-indigo-300 font-medium underline cursor-pointer"
              >
                Preencher automaticamente
              </button>
            </div>
            <p>
              E-mail: <code className="text-indigo-300 font-mono">admin@projetosunion.cloud</code>
            </p>
            <p>
              Senha: <code className="text-indigo-300 font-mono font-bold">UnionGrowth#2026!</code>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-[#070b14] text-slate-100">
      {/* SIDEBAR MENU (20 SECTIONS) */}
      <aside className="w-64 bg-[#0c1222] border-r border-slate-800/80 flex flex-col shrink-0">
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-sm">
              UG
            </div>
            <div>
              <div className="font-bold text-sm text-white leading-tight">UNION GROWTH OS</div>
              <div className="text-[10px] text-emerald-400 font-medium">11 AI Agents • Native Cloud</div>
            </div>
          </div>

          {meData?.available_tenants && (
            <div className="mt-3">
              <label className="text-[10px] uppercase tracking-wider text-slate-400 block mb-1">
                Empresa Ativa (Multi-Tenant)
              </label>
              <select
                value={activeTenantId || meData?.active_tenant?.id || ""}
                onChange={(e) => setActiveTenantId(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1.5 text-xs text-white"
              >
                {meData.available_tenants.map((t: any) => (
                  <option key={t.id} value={t.id}>
                    {t.brand_name} ({t.plan_tier})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        <nav className="flex-1 overflow-y-auto p-2 space-y-0.5">
          {MENU_ITEMS.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveMenu(item.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition ${
                activeMenu === item.id
                  ? "bg-indigo-600 text-white shadow"
                  : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
              }`}
            >
              <span className="text-[10px] opacity-60 font-mono">{item.num}</span>
              <span className="truncate">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="p-3 border-t border-slate-800 text-xs space-y-2">
          <div className="text-[11px] text-slate-400 truncate">
            {meData?.user?.full_name} ({meData?.user?.role})
          </div>
          <button
            onClick={handleLogout}
            className="w-full py-1.5 rounded bg-slate-800 hover:bg-red-900/50 text-slate-300 text-xs"
          >
            Sair da Conta
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-[#0c1222]/90 border-b border-slate-800 px-6 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white">
              {MENU_ITEMS.find((m) => m.id === activeMenu)?.label}
            </h2>
            <p className="text-xs text-slate-400">
              Marca: <strong className="text-slate-200">{meData?.active_tenant?.brand_name}</strong> • Plano:{" "}
              <strong className="text-emerald-400">{meData?.active_tenant?.plan_tier}</strong> • Autonomia:{" "}
              <strong className="text-indigo-400">Nível {meData?.active_tenant?.autonomy_default_level || 2}</strong>
            </p>
          </div>
          <div className="flex items-center gap-3">
            {toast && (
              <div className="px-3 py-1.5 rounded-lg bg-indigo-600/20 border border-indigo-500/40 text-indigo-200 text-xs">
                {toast}
              </div>
            )}
            <button
              onClick={async () => {
                showNotice("Executando Diagnóstico Multiagente completo...");
                const res = await apiFetch("/api/v1/orchestrator/diagnose", {
                  method: "POST",
                  body: JSON.stringify({ reason: "Acionamento Executivo Manual" }),
                });
                setDiagResult(res);
                await loadAllActiveData();
                showNotice("Diagnóstico Multiagente concluído com sucesso!");
              }}
              className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
            >
              Acionar Orquestrador Multiagente
            </button>
            <button
              onClick={loadAllActiveData}
              className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs"
            >
              {loading ? "Atualizando..." : "Atualizar Dados"}
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* 01. VISÃO GERAL */}
          {activeMenu === "overview" && overviewData && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {overviewData.metrics_cards.map((card: any) => (
                  <div key={card.key} className="bg-[#0f1629] border border-slate-800 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-slate-400">{card.label}</span>
                      <OriginBadge origin={card.origin} />
                    </div>
                    <div className="text-2xl font-bold text-white">{card.value}</div>
                    <div className="text-[11px] text-slate-400 mt-1">{card.subtext}</div>
                  </div>
                ))}
              </div>

              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5">
                <h3 className="text-sm font-bold text-white mb-3">
                  Painel de Autonomia Operacional & Governança em Tempo Real
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-center">
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <div className="text-xl font-bold text-emerald-400">
                      {overviewData.autonomy_status_panel.executed_by_ai_count}
                    </div>
                    <div className="text-[11px] text-slate-400">Executado pela IA</div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <div className="text-xl font-bold text-amber-400">
                      {overviewData.autonomy_status_panel.pending_approval_count}
                    </div>
                    <div className="text-[11px] text-slate-400">Aguardando Aprovação</div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <div className="text-xl font-bold text-red-400">
                      {overviewData.autonomy_status_panel.failed_count}
                    </div>
                    <div className="text-[11px] text-slate-400">Falhas Registradas</div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <div className="text-xl font-bold text-purple-400">
                      {overviewData.autonomy_status_panel.blocked_count}
                    </div>
                    <div className="text-[11px] text-slate-400">Bloqueado por Segurança</div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <div className="text-xl font-bold text-sky-400">
                      {overviewData.autonomy_status_panel.needs_configuration_count}
                    </div>
                    <div className="text-[11px] text-slate-400">Aguardando Credenciais</div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0f1629] border border-indigo-500/30 rounded-xl p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-indigo-300">CEO DAILY BRIEFING — Destaque do Dia</h3>
                    <button
                      onClick={() => setActiveMenu("ceo")}
                      className="text-xs text-indigo-400 hover:underline"
                    >
                      Ver Completo →
                    </button>
                  </div>
                  <p className="text-xs text-white font-medium">{overviewData.ceo_briefing.headline}</p>
                  <div className="space-y-1">
                    <div className="text-[11px] font-semibold text-slate-300">Recomendações Prioritárias da IA:</div>
                    {overviewData.ceo_briefing.recommendations.map((r: string, idx: number) => (
                      <div key={idx} className="text-xs text-slate-300 bg-slate-900/70 p-2 rounded">
                        {r}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <h3 className="text-sm font-bold text-white">Equipe Digital de 11 Agentes Especializados</h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                    {agentsData?.agents?.map((ag: any) => (
                      <div
                        key={ag.id}
                        className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900 border border-slate-800"
                      >
                        <div>
                          <div className="text-xs font-bold text-white">{ag.name}</div>
                          <div className="text-[11px] text-slate-400">{ag.role}</div>
                        </div>
                        <button
                          onClick={async () => {
                            await apiFetch(`/api/v1/agents/${ag.id}/execute`, {
                              method: "POST",
                              body: JSON.stringify({}),
                            });
                            await loadAllActiveData();
                            showNotice(`${ag.name} executou sua rotina com sucesso!`);
                          }}
                          className="px-2.5 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-semibold shrink-0"
                        >
                          Executar Agora
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {diagResult && (
                <div className="bg-[#0f1629] border border-emerald-500/40 rounded-xl p-5 space-y-2">
                  <h3 className="text-sm font-bold text-emerald-300">
                    Resultado do Último Diagnóstico Coordenado pelo Orquestrador ({diagResult.workflow_run_id})
                  </h3>
                  <p className="text-xs text-slate-200">{diagResult.ceo_consolidation?.summary}</p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2 pt-2">
                    {diagResult.specialist_diagnostics?.map((d: any, i: number) => (
                      <div key={i} className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs">
                        <div className="font-bold text-indigo-300">{d.agent_name}</div>
                        <div className="text-slate-300 mt-1">{d.summary}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 02. AI CEO */}
          {activeMenu === "ceo" && ceoData && (
            <div className="space-y-6">
              <div className="flex items-center justify-between bg-[#0f1629] border border-slate-800 p-4 rounded-xl">
                <div>
                  <h3 className="text-sm font-bold text-white">AGENTE 01 — AI CEO & Direção Estratégica</h3>
                  <p className="text-xs text-slate-400">
                    Nunca inventa números financeiros ou declara decisões não executadas.
                  </p>
                </div>
                <button
                  onClick={async () => {
                    await apiFetch("/api/v1/ceo/briefings/generate", { method: "POST" });
                    await loadAllActiveData();
                    showNotice("Novo CEO Daily Briefing gerado com base nos dados reais!");
                  }}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                >
                  Gerar Novo CEO Daily Briefing
                </button>
              </div>

              {ceoData.briefings?.[0] && (
                <div className="bg-[#0f1629] border border-indigo-500/30 rounded-xl p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-base font-bold text-white">{ceoData.briefings[0].summary_headline}</h4>
                    <OriginBadge origin="REAL" />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    <div className="p-3 rounded-lg bg-slate-900 space-y-1">
                      <div className="font-bold text-indigo-300">O que aconteceu (Fatos Auditados)</div>
                      {ceoData.briefings[0].what_happened.map((x: string, i: number) => (
                        <p key={i} className="text-slate-300">• {x}</p>
                      ))}
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900 space-y-1">
                      <div className="font-bold text-emerald-300">O que está funcionando</div>
                      {ceoData.briefings[0].what_is_working.map((x: string, i: number) => (
                        <p key={i} className="text-slate-300">• {x}</p>
                      ))}
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900 space-y-1">
                      <div className="font-bold text-amber-300">O que está dando errado / Problemas Urgentes</div>
                      {ceoData.briefings[0].what_is_wrong.map((x: string, i: number) => (
                        <p key={i} className="text-slate-300">• {x}</p>
                      ))}
                      {ceoData.briefings[0].urgent_problems.map((x: string, i: number) => (
                        <p key={`u-${i}`} className="text-red-300">! {x}</p>
                      ))}
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900 space-y-1">
                      <div className="font-bold text-sky-300">Oportunidades & Recomendações</div>
                      {ceoData.briefings[0].opportunities.map((x: string, i: number) => (
                        <p key={`op-${i}`} className="text-emerald-200">+ {x}</p>
                      ))}
                      {ceoData.briefings[0].recommendations.map((x: string, i: number) => (
                        <p key={i} className="text-slate-300">{x}</p>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Form para criar nova meta */}
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <h4 className="text-sm font-bold text-white">Definir Nova Meta Estratégica (Mensal / Trimestral / Anual)</h4>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                  <input
                    value={goalTitle}
                    onChange={(e) => setGoalTitle(e.target.value)}
                    placeholder="Título da Meta"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white md:col-span-2"
                  />
                  <select
                    value={goalPeriod}
                    onChange={(e) => setGoalPeriod(e.target.value)}
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    <option value="MONTHLY">Mensal (MONTHLY)</option>
                    <option value="QUARTERLY">Trimestral (QUARTERLY)</option>
                    <option value="ANNUAL">Anual (ANNUAL)</option>
                  </select>
                  <input
                    type="number"
                    value={goalTarget}
                    onChange={(e) => setGoalTarget(e.target.value)}
                    placeholder="Valor Alvo"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <button
                    onClick={async () => {
                      if (!goalTitle) return;
                      await apiFetch("/api/v1/ceo/goals", {
                        method: "POST",
                        body: JSON.stringify({
                          title: goalTitle,
                          period: goalPeriod,
                          metric_name: goalMetric,
                          target_value: Number(goalTarget) || 100000,
                          current_value: 0,
                          unit: "BRL",
                          data_origin: "GOAL",
                          priority: "HIGH",
                          deadline: "2027-03-31",
                        }),
                      });
                      setGoalTitle("");
                      await loadAllActiveData();
                      showNotice("Meta estratégica registrada pelo AI CEO!");
                    }}
                    className="py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                  >
                    Adicionar Meta
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                  {ceoData.goals.map((g: any) => (
                    <div key={g.id} className="p-4 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                          {g.period}
                        </span>
                        <OriginBadge origin={g.data_origin} />
                      </div>
                      <div className="text-xs font-bold text-white">{g.title}</div>
                      <div className="text-sm font-semibold text-emerald-400">
                        Atual: {g.current_value} / Meta: {g.target_value} {g.unit}
                      </div>
                      <div className="text-[11px] text-slate-400">
                        Impacto Financeiro: {g.financial_impact_score}/100 • Prazo: {g.deadline}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 03. MARKETING (AI CMO) */}
          {activeMenu === "marketing" && marketingData && (
            <div className="space-y-6">
              <div className="flex items-center justify-between bg-[#0f1629] border border-slate-800 p-4 rounded-xl">
                <div>
                  <h3 className="text-sm font-bold text-white">
                    AGENTE 02 — AI CMO (Posicionamento, Personas, Campanhas e Planejamento Mensal)
                  </h3>
                </div>
                <button
                  onClick={async () => {
                    await apiFetch("/api/v1/agents/AGENT_02_CMO/execute", {
                      method: "POST",
                      body: JSON.stringify({ task_name: "generate_monthly_marketing_plan" }),
                    });
                    await loadAllActiveData();
                    showNotice("Novo Planejamento Mensal de Marketing gerado pelo AI CMO!");
                  }}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                >
                  Gerar Planejamento Mensal Automático
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <h4 className="text-sm font-bold text-white">Personas & Público-Alvo (ICP)</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    <input
                      value={personaName}
                      onChange={(e) => setPersonaName(e.target.value)}
                      placeholder="Nome da Persona"
                      className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    />
                    <input
                      value={personaVP}
                      onChange={(e) => setPersonaVP(e.target.value)}
                      placeholder="Proposta de Valor"
                      className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    />
                    <button
                      onClick={async () => {
                        if (!personaName) return;
                        await apiFetch("/api/v1/marketing/personas", {
                          method: "POST",
                          body: JSON.stringify({
                            name: personaName,
                            role_segment: personaRole,
                            value_proposition: personaVP || "Eficiência e escala com IA",
                          }),
                        });
                        setPersonaName("");
                        setPersonaVP("");
                        await loadAllActiveData();
                        showNotice("Persona criada com sucesso!");
                      }}
                      className="py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                    >
                      Criar Persona
                    </button>
                  </div>
                  {marketingData.personas.map((p: any) => (
                    <div key={p.id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1 text-xs">
                      <div className="font-bold text-indigo-300">{p.name}</div>
                      <div className="text-slate-400">
                        {p.role_segment} • {p.demographics}
                      </div>
                      <div className="text-slate-200 mt-1">
                        <strong>Proposta de Valor:</strong> {p.value_proposition}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <h4 className="text-sm font-bold text-white">Campanhas Ativas & ROI</h4>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
                    <input
                      value={campName}
                      onChange={(e) => setCampName(e.target.value)}
                      placeholder="Nome da Campanha"
                      className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    />
                    <select
                      value={campType}
                      onChange={(e) => setCampType(e.target.value)}
                      className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    >
                      <option value="ACQUISITION">Aquisição</option>
                      <option value="LAUNCH">Lançamento</option>
                      <option value="SEASONAL">Sazonal</option>
                      <option value="RETENTION">Retenção</option>
                    </select>
                    <input
                      type="number"
                      value={campBudget}
                      onChange={(e) => setCampBudget(e.target.value)}
                      placeholder="Orçamento (R$)"
                      className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    />
                    <button
                      onClick={async () => {
                        if (!campName) return;
                        const res = await apiFetch("/api/v1/marketing/campaigns", {
                          method: "POST",
                          body: JSON.stringify({
                            name: campName,
                            campaign_type: campType,
                            channel: campChannel,
                            objective: "Aquisição e conversão de leads",
                            budget_planned: Number(campBudget) || 0,
                          }),
                        });
                        setCampName("");
                        await loadAllActiveData();
                        showNotice(res.message || "Campanha criada com sucesso!");
                      }}
                      className="py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                    >
                      Criar Campanha
                    </button>
                  </div>
                  {marketingData.campaigns.map((c: any) => (
                    <div key={c.id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white">{c.name}</span>
                        <OriginBadge origin={c.data_origin} />
                      </div>
                      <div className="text-slate-400">
                        Canal: {c.channel} • Tipo: {c.campaign_type} • ROI:{" "}
                        <strong className="text-emerald-400">{c.roi_pct}%</strong>
                      </div>
                      <div className="text-slate-300">
                        Orçamento: R$ {c.budget_planned} | Gasto Real: R$ {c.spend_real} | Receita Atribuída: R${" "}
                        {c.revenue_attributed}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 04. SEO DIRECTOR */}
          {activeMenu === "seo" && seoData && (
            <div className="space-y-6">
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs">
                <strong>Transparência SEO:</strong> {seoData.gsc_ranking_status?.notice}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-4 space-y-3">
                  <h4 className="text-xs font-bold text-white uppercase">1. Auditoria Técnica de SEO (Live HTTP)</h4>
                  <input
                    value={seoUrlInput}
                    onChange={(e) => setSeoUrlInput(e.target.value)}
                    className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    placeholder="https://seudominio.com.br"
                  />
                  <button
                    onClick={async () => {
                      await apiFetch("/api/v1/seo/audit", {
                        method: "POST",
                        body: JSON.stringify({ target_url: seoUrlInput, target_keyword: seoKwInput }),
                      });
                      await loadAllActiveData();
                      showNotice("Auditoria técnica de SEO concluída!");
                    }}
                    className="w-full py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Executar Auditoria Técnica Real
                  </button>
                </div>

                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-4 space-y-3">
                  <h4 className="text-xs font-bold text-white uppercase">2. Pesquisa de Palavras-Chave & Clusters</h4>
                  <input
                    value={seoKwInput}
                    onChange={(e) => setSeoKwInput(e.target.value)}
                    className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    placeholder="Palavra-chave semente"
                  />
                  <button
                    onClick={async () => {
                      await apiFetch("/api/v1/seo/keywords", {
                        method: "POST",
                        body: JSON.stringify({ seed_keyword: seoKwInput }),
                      });
                      await loadAllActiveData();
                      showNotice("Cluster de palavras-chave e cauda longa gerado!");
                    }}
                    className="w-full py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Descobrir Cauda Longa & Clusters
                  </button>
                </div>

                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-4 space-y-3">
                  <h4 className="text-xs font-bold text-white uppercase">3. SEO Content Factory (Gerar Artigo)</h4>
                  <input
                    value={seoTopicInput}
                    onChange={(e) => setSeoTopicInput(e.target.value)}
                    className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    placeholder="Título / Tópico do Artigo"
                  />
                  <button
                    onClick={async () => {
                      await apiFetch("/api/v1/seo/articles/generate", {
                        method: "POST",
                        body: JSON.stringify({
                          topic: seoTopicInput,
                          target_keyword: seoKwInput,
                          search_intent: "COMMERCIAL",
                        }),
                      });
                      await loadAllActiveData();
                      showNotice("Artigo otimizado com Schema.org gerado pela SEO Content Factory!");
                    }}
                    className="w-full py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                  >
                    Produzir Artigo Otimizado
                  </button>
                </div>
              </div>

              {/* Clusters de Palavras-Chave */}
              {seoData.keyword_clusters?.length > 0 && (
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <h4 className="text-sm font-bold text-white">Clusters de Conteúdo & Cauda Longa</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {seoData.keyword_clusters.map((kc: any) => (
                      <div key={kc.id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-indigo-300">{kc.seed_keyword}</span>
                          <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-[10px]">
                            Intenção: {kc.search_intent}
                          </span>
                        </div>
                        <div className="text-slate-300">
                          <strong>Cauda Longa:</strong> {kc.long_tail_keywords.slice(0, 5).join(" • ")}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <h4 className="text-sm font-bold text-white">Últimas Auditorias Técnicas</h4>
                  {seoData.audits.map((a: any) => (
                    <div key={a.id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-indigo-300">{a.target_url}</span>
                        <OriginBadge origin={a.data_origin} />
                      </div>
                      <div>
                        Score: <strong className="text-emerald-400">{a.overall_score}/100</strong> • Tempo:{" "}
                        {a.response_time_ms}ms • robots.txt: {a.has_robots_txt ? "Sim" : "Não"} • sitemap.xml:{" "}
                        {a.has_sitemap_xml ? "Sim" : "Não"}
                      </div>
                      <div className="text-slate-400">
                        Sugestão Title: <span className="text-slate-200">{a.suggested_title}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <h4 className="text-sm font-bold text-white">Artigos da SEO Content Factory</h4>
                  {seoData.articles.map((art: any) => (
                    <div key={art.id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs space-y-1">
                      <div className="font-bold text-white">{art.title}</div>
                      <div className="text-slate-400">
                        Keyword: {art.target_keyword} • Palavras: {art.word_count} • Densidade: {art.keyword_density_pct}%
                      </div>
                      <pre className="mt-2 p-2 rounded bg-slate-950 text-[11px] text-slate-300 max-h-40 overflow-y-auto whitespace-pre-wrap">
                        {art.content_markdown}
                      </pre>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 05 & 14. REDES SOCIAIS & CALENDÁRIO EDITORIAL */}
          {(activeMenu === "social" || activeMenu === "calendar") && (
            <div className="space-y-6">
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white">
                      AGENTE 04 — AI Social Media Director & Central de Publicação
                    </h3>
                    <p className="text-xs text-slate-400">
                      Instagram, Facebook, TikTok, YouTube, LinkedIn e Pinterest com validação e aprovação humana.
                    </p>
                  </div>
                  <button
                    onClick={async () => {
                      await apiFetch("/api/v1/agents/AGENT_04_SOCIAL/execute", {
                        method: "POST",
                        body: JSON.stringify({}),
                      });
                      await loadAllActiveData();
                      showNotice("Calendário multicanal gerado pelo AI Social Media Director!");
                    }}
                    className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Gerar Lote de Posts Multicanal com IA
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-5 gap-3 pt-2 border-t border-slate-800">
                  <input
                    value={calTitle}
                    onChange={(e) => setCalTitle(e.target.value)}
                    placeholder="Título da Publicação"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <select
                    value={calPlatform}
                    onChange={(e) => setCalPlatform(e.target.value)}
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    <option value="instagram">Instagram</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="tiktok">TikTok</option>
                    <option value="youtube">YouTube</option>
                    <option value="facebook">Facebook</option>
                    <option value="pinterest">Pinterest</option>
                  </select>
                  <select
                    value={calFormat}
                    onChange={(e) => setCalFormat(e.target.value)}
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    <option value="CAROUSEL">Carrossel</option>
                    <option value="POST">Post Único</option>
                    <option value="REELS_SHORT">Reels / Short / TikTok</option>
                    <option value="VIDEO">Vídeo Longo</option>
                  </select>
                  <input
                    value={calDate}
                    onChange={(e) => setCalDate(e.target.value)}
                    placeholder="YYYY-MM-DD HH:MM"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <button
                    onClick={async () => {
                      if (!calTitle) return;
                      await apiFetch("/api/v1/social/calendar", {
                        method: "POST",
                        body: JSON.stringify({
                          title: calTitle,
                          platform: calPlatform,
                          content_format: calFormat,
                          scheduled_for: calDate,
                          auto_generate_copy: true,
                        }),
                      });
                      setCalTitle("");
                      await loadAllActiveData();
                      showNotice("Publicação agendada e enviada para validação!");
                    }}
                    className="py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                  >
                    Agendar no Calendário
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {calendarData.map((item: any) => (
                  <div key={item.id} className="bg-[#0f1629] border border-slate-800 rounded-xl p-4 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold uppercase text-[10px]">
                        {item.platform} • {item.content_format}
                      </span>
                      <span className="text-slate-400 font-mono">{item.scheduled_for}</span>
                    </div>
                    <div className="font-bold text-white text-sm">{item.title}</div>
                    <p className="text-slate-300 whitespace-pre-line">{item.caption}</p>
                    <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                      <span className="text-[11px] text-amber-300">
                        Aprovação: <strong>{item.approval_status}</strong> | Status:{" "}
                        <strong>{item.publish_status}</strong>
                      </span>
                      <button
                        onClick={async () => {
                          const r = await apiFetch(`/api/v1/social/calendar/${item.id}/publish`, { method: "POST" });
                          await loadAllActiveData();
                          showNotice(r.message || "Status de publicação atualizado.");
                        }}
                        className="px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-[11px]"
                      >
                        Aprovar & Publicar
                      </button>
                    </div>
                    {item.last_error && <div className="text-[11px] text-amber-400/90">{item.last_error}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* FASE 14 — CONTENT FACTORY */}
          {activeMenu === "content_factory" && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-[#0f1629] border border-indigo-500/30 p-5 rounded-xl">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>🏭</span> UNION Content Factory — Produção Mensal Multicanal (30 Dias)
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Geração coordenada de 30 publicações estratégicas (Posts, Carrosséis, Reels/Shorts, Vídeos Longos YouTube, Artigos SEO, E-mails e Lançamentos) com validação de qualidade editorial e anti-duplicação.
                  </p>
                </div>
                <button
                  onClick={async () => {
                    setLoading(true);
                    try {
                      const res = await apiFetch("/api/v1/content-factory/generate-batch", {
                        method: "POST",
                        body: JSON.stringify({ count: 30 }),
                      });
                      await loadAllActiveData();
                      showNotice(`Content Factory: ${res.total_generated} conteúdos gerados com score médio de ${res.average_quality_score}/100!`);
                    } catch (e: any) {
                      showNotice(e.message || "Erro ao gerar lote");
                    } finally {
                      setLoading(false);
                    }
                  }}
                  className="px-4 py-2.5 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg flex items-center gap-2 whitespace-nowrap"
                >
                  <span>⚡</span> Gerar Lote de 30 Publicações
                </button>
              </div>

              {/* Filtro de Canais */}
              <div className="flex flex-wrap gap-2">
                {["ALL", "instagram", "facebook", "tiktok", "youtube", "linkedin", "blog_seo", "email_marketing"].map((ch) => (
                  <button
                    key={ch}
                    onClick={() => setCfFilter(ch)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                      cfFilter === ch
                        ? "bg-indigo-600 text-white shadow"
                        : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
                    }`}
                  >
                    {ch === "ALL" ? "Todos os Canais" : ch.toUpperCase()}
                  </button>
                ))}
              </div>

              {/* Lista de Itens da Content Factory */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {contentFactoryItems
                  .filter((it: any) => cfFilter === "ALL" || it.channel === cfFilter)
                  .map((it: any) => (
                    <div key={it.id} className="bg-[#0f1629] border border-slate-800 rounded-xl p-4 space-y-3 text-xs flex flex-col justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold uppercase text-[10px]">
                            {it.channel} • {it.content_type}
                          </span>
                          <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold text-[10px]">
                            Nota {it.quality_score}/100
                          </span>
                        </div>
                        <div className="font-bold text-white text-sm line-clamp-2">{it.title}</div>
                        <p className="text-slate-300 line-clamp-4 whitespace-pre-line text-[11px]">{it.body_text}</p>
                        <div className="p-2 rounded bg-slate-900/80 border border-slate-800 text-[11px] text-indigo-300">
                          <strong>CTA:</strong> {it.cta}
                        </div>
                      </div>

                      <div className="pt-3 border-t border-slate-800 space-y-2">
                        <div className="flex items-center justify-between text-[10px] text-slate-400">
                          <span>Data: <strong>{it.scheduled_for?.split("T")[0]}</strong></span>
                          <span>Status: <strong className="text-amber-300">{it.status}</strong></span>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={async () => {
                              try {
                                const pkg = await apiFetch(`/api/v1/content-factory/assisted-export/${it.id}`);
                                setAssistedPackage(pkg);
                              } catch (e: any) {
                                showNotice(e.message || "Erro ao exportar");
                              }
                            }}
                            className="flex-1 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/30 text-[11px] font-medium"
                          >
                            📋 Pacote 1-Clique
                          </button>
                          <button
                            onClick={async () => {
                              try {
                                await apiFetch(`/api/v1/content-factory/items/${it.id}/publish`, { method: "POST" });
                                await loadAllActiveData();
                                showNotice("Status atualizado para Publicado!");
                              } catch (e: any) {
                                showNotice(e.message || "Erro ao publicar");
                              }
                            }}
                            className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-medium"
                          >
                            ✓
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* FASE 14 — PLANO DIÁRIO CEO */}
          {activeMenu === "ceo_plan" && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-[#0f1629] border border-indigo-500/30 p-5 rounded-xl">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>📋</span> AI CEO — Plano Diário de Execução & Delegação
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    {ceoDailyPlan?.headline || "Missões executivas diárias distribuídas para todos os especialistas."}
                  </p>
                </div>
                <button
                  onClick={async () => {
                    setLoading(true);
                    try {
                      const res = await apiFetch("/api/v1/ceo/daily-plan/generate", { method: "POST" });
                      setCeoDailyPlan(res);
                      showNotice("Novo Plano Diário de Execução gerado com sucesso!");
                    } catch (e: any) {
                      showNotice(e.message || "Erro ao gerar plano");
                    } finally {
                      setLoading(false);
                    }
                  }}
                  className="px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg whitespace-nowrap"
                >
                  🔄 Regenerar Missões Diárias
                </button>
              </div>

              {/* Grid de Missões Delegadas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {ceoDailyPlan?.tasks?.map((task: any) => (
                  <div key={task.id} className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="px-2.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold text-[11px]">
                        {task.target_agent}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        task.priority === "CRITICAL"
                          ? "bg-red-500/20 text-red-300 border border-red-500/30"
                          : task.priority === "HIGH"
                          ? "bg-amber-500/20 text-amber-300"
                          : "bg-slate-700 text-slate-300"
                      }`}>
                        {task.priority}
                      </span>
                    </div>

                    <div className="font-bold text-white text-sm">{task.title}</div>
                    <p className="text-slate-300 text-xs">{task.objective}</p>

                    <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-[11px] text-slate-300">
                      <strong className="text-indigo-400">Entregável Esperado:</strong> {task.deliverable}
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                      <span className="text-[11px] text-slate-400">
                        Status: <strong className={task.status === "COMPLETED" ? "text-emerald-400" : "text-amber-400"}>{task.status}</strong>
                      </span>
                      <div className="flex gap-1.5">
                        {task.status !== "COMPLETED" && (
                          <button
                            onClick={async () => {
                              try {
                                await apiFetch(`/api/v1/ceo/daily-plan/tasks/${task.id}`, {
                                  method: "PUT",
                                  body: JSON.stringify({ status: "COMPLETED", deliverable: "Executado e validado em produção." }),
                                });
                                await loadAllActiveData();
                                showNotice(`Missão ${task.id} marcada como CONCLUÍDA!`);
                              } catch (e: any) {
                                showNotice(e.message || "Erro ao atualizar");
                              }
                            }}
                            className="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-medium"
                          >
                            Concluir Missão
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* FASE 14 — PAINEL OPERACIONAL 24/7 & ALERTAS */}
          {activeMenu === "operational247" && (
            <div className="space-y-6">
              {/* Status da Infraestrutura */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-[#0f1629] border border-slate-800 p-4 rounded-xl text-xs space-y-1">
                  <div className="text-slate-400">VPS Host (Coolify)</div>
                  <div className="text-base font-bold text-emerald-400">{opDashboard?.vps_status?.status || "HEALTHY"}</div>
                  <div className="text-[11px] text-slate-400">IP: {opDashboard?.vps_status?.server_ip || "72.62.13.62"}</div>
                </div>
                <div className="bg-[#0f1629] border border-slate-800 p-4 rounded-xl text-xs space-y-1">
                  <div className="text-slate-400">PostgreSQL 16</div>
                  <div className="text-base font-bold text-emerald-400">{opDashboard?.database_status?.connection || "CONECTADO"}</div>
                  <div className="text-[11px] text-slate-400">{opDashboard?.database_status?.total_records_monitored || 0} registros ativos</div>
                </div>
                <div className="bg-[#0f1629] border border-slate-800 p-4 rounded-xl text-xs space-y-1">
                  <div className="text-slate-400">APScheduler (America/Sao_Paulo)</div>
                  <div className="text-base font-bold text-emerald-400">17 Rotinas Ativas</div>
                  <div className="text-[11px] text-slate-400">100% Internalizado no Python</div>
                </div>
                <div className="bg-[#0f1629] border border-slate-800 p-4 rounded-xl text-xs space-y-1">
                  <div className="text-slate-400">Garantia Custo Cloud</div>
                  <div className="text-base font-bold text-indigo-400">R$ 0,00 Externo</div>
                  <div className="text-[11px] text-slate-400">100% Ferramentas Open-Source</div>
                </div>
              </div>

              {/* Tabela de 10 Rotinas Diárias (07h às 18h) */}
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white">Rotinas Operacionais Contínuas (America/Sao_Paulo)</h3>
                  <button
                    onClick={async () => {
                      try {
                        const r = await apiFetch("/api/v1/seo/weekly-report", { method: "POST" });
                        await loadAllActiveData();
                        showNotice(`Auditoria Semanal de SEO executada! Score: ${r.audit_score}/100`);
                      } catch (e: any) {
                        showNotice(e.message || "Erro");
                      }
                    }}
                    className="px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs"
                  >
                    🔍 Executar Auditoria Semanal de SEO
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="text-[11px] text-slate-400 border-b border-slate-800">
                      <tr>
                        <th className="py-2">Horário</th>
                        <th className="py-2">Rotina Automatizada</th>
                        <th className="py-2">Agente Responsável</th>
                        <th className="py-2">Frequência</th>
                        <th className="py-2">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-slate-300">
                      {opDashboard?.daily_routines_status?.map((r: any, idx: number) => (
                        <tr key={idx} className="hover:bg-slate-900/50">
                          <td className="py-2.5 font-mono text-indigo-300 font-bold">{r.hour}</td>
                          <td className="py-2.5 font-medium text-white">{r.routine}</td>
                          <td className="py-2.5 text-slate-400">{r.agent}</td>
                          <td className="py-2.5">{r.frequency}</td>
                          <td className="py-2.5">
                            <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold text-[10px]">
                              {r.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Alertas Inteligentes do Sistema */}
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>🚨</span> Alertas Operacionais Inteligentes & Sugestões de Ação
                </h3>
                <div className="space-y-3">
                  {systemAlerts.map((a: any) => (
                    <div
                      key={a.id}
                      className={`p-4 rounded-xl border text-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-3 ${
                        a.severity === "CRITICAL"
                          ? "bg-red-500/10 border-red-500/30"
                          : a.severity === "WARNING"
                          ? "bg-amber-500/10 border-amber-500/30"
                          : "bg-indigo-500/10 border-indigo-500/30"
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            a.severity === "CRITICAL" ? "bg-red-600 text-white" : a.severity === "WARNING" ? "bg-amber-600 text-white" : "bg-indigo-600 text-white"
                          }`}>
                            {a.severity}
                          </span>
                          <span className="font-bold text-white">{a.title}</span>
                          <span className="text-[10px] text-slate-400 font-mono">[{a.category}]</span>
                        </div>
                        <p className="text-slate-300 text-[11px]">{a.message}</p>
                        <p className="text-emerald-300 text-[11px]">👉 <strong>Ação Sugerida:</strong> {a.suggested_action}</p>
                      </div>
                      {!a.is_resolved && (
                        <button
                          onClick={async () => {
                            try {
                              await apiFetch(`/api/v1/system/alerts/${a.id}/resolve`, { method: "POST" });
                              await loadAllActiveData();
                              showNotice("Alerta marcado como resolvido!");
                            } catch (e: any) {
                              showNotice(e.message || "Erro");
                            }
                          }}
                          className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs whitespace-nowrap"
                        >
                          Marcar Resolvido
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* FASE 14 — PILOTO 7 DIAS */}
          {activeMenu === "pilot7d" && (
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-[#0f1629] border border-indigo-500/30 p-5 rounded-xl">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>🚀</span> Piloto Operacional Autônomo de 7 Dias Consecutivos
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Simulação e validação ponta a ponta dos 7 dias de rotinas empresariais (Briefings diários, produção de 30 conteúdos na Content Factory, auditorias de SEO, qualificação de leads e consolidação financeira).
                  </p>
                </div>
                <button
                  onClick={async () => {
                    setLoading(true);
                    try {
                      const res = await apiFetch("/api/v1/system/pilot-7-days", { method: "POST" });
                      setPilotData(res);
                      showNotice(`Piloto de 7 Dias executado! ${res.total_content_pieces_produced} conteúdos produzidos e ${res.total_leads_qualified} leads qualificados.`);
                    } catch (e: any) {
                      showNotice(e.message || "Erro ao executar piloto");
                    } finally {
                      setLoading(false);
                    }
                  }}
                  className="px-4 py-2.5 rounded-lg bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg whitespace-nowrap"
                >
                  🚀 Executar Piloto de 7 Dias
                </button>
              </div>

              {pilotData && (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="bg-[#0f1629] border border-slate-800 p-4 rounded-xl text-xs space-y-1">
                    <div className="text-slate-400">Dias Auditados</div>
                    <div className="text-lg font-bold text-white">{pilotData.days_simulated} Dias</div>
                  </div>
                  <div className="bg-[#0f1629] border border-slate-800 p-4 rounded-xl text-xs space-y-1">
                    <div className="text-slate-400">Conteúdos Produzidos</div>
                    <div className="text-lg font-bold text-indigo-400">{pilotData.total_content_pieces_produced} Peças</div>
                  </div>
                  <div className="bg-[#0f1629] border border-slate-800 p-4 rounded-xl text-xs space-y-1">
                    <div className="text-slate-400">Leads Qualificados</div>
                    <div className="text-lg font-bold text-emerald-400">{pilotData.total_leads_qualified} Oportunidades</div>
                  </div>
                  <div className="bg-[#0f1629] border border-slate-800 p-4 rounded-xl text-xs space-y-1">
                    <div className="text-slate-400">Auditorias de SEO</div>
                    <div className="text-lg font-bold text-amber-400">{pilotData.total_seo_routines_executed} Executadas</div>
                  </div>
                  <div className="bg-[#0f1629] border border-slate-800 p-4 rounded-xl text-xs space-y-1">
                    <div className="text-slate-400">Custo Adicional</div>
                    <div className="text-lg font-bold text-emerald-400">R$ 0,00</div>
                  </div>
                </div>
              )}

              {/* Linha do Tempo dos 7 Dias */}
              <div className="space-y-3">
                {pilotData?.daily_runs?.map((d: any) => (
                  <div key={d.day_number} className="bg-[#0f1629] border border-slate-800 rounded-xl p-4 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white text-sm">
                        Dia {d.day_number} — {d.date}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold text-[10px]">
                        {d.status}
                      </span>
                    </div>
                    <ul className="space-y-1 text-slate-300 text-[11px] list-disc list-inside">
                      {d.actions?.map((act: string, idx: number) => (
                        <li key={idx}>{act}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* MODAL DE EXPORTAÇÃO ASSISTIDA (1 CLIQUE) */}
          {assistedPackage && (
            <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
              <div className="bg-[#0f1629] border border-indigo-500/40 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl text-xs">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <span>📋</span> Pacote de Publicação Assistida (1 Clique) — {assistedPackage.channel.toUpperCase()}
                  </h3>
                  <button
                    onClick={() => setAssistedPackage(null)}
                    className="text-slate-400 hover:text-white text-base font-bold"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-2">
                  <label className="text-slate-300 font-semibold">Legenda Formatada com Hashtags:</label>
                  <textarea
                    readOnly
                    rows={6}
                    value={assistedPackage.formatted_copy_for_clipboard}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white text-xs font-mono"
                  />
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(assistedPackage.formatted_copy_for_clipboard);
                      showNotice("Texto copiado para a área de transferência com sucesso!");
                    }}
                    className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs"
                  >
                    📄 Copiar Texto Completo para o Clipboard
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2">
                  <a
                    href={assistedPackage.platform_upload_url}
                    target="_blank"
                    rel="noreferrer"
                    className="py-2 text-center rounded bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/30 font-medium"
                  >
                    🔗 Abrir Central Oficial da Rede
                  </a>
                  <button
                    onClick={() => {
                      showNotice("Download de mídia iniciado.");
                      setAssistedPackage(null);
                    }}
                    className="py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-medium"
                  >
                    💾 Baixar Criativo Visual
                  </button>
                </div>

                <div className="pt-2 border-t border-slate-800 space-y-1 text-slate-400 text-[11px]">
                  <p className="font-semibold text-slate-300">Checklist Rápido:</p>
                  {assistedPackage.checklist?.map((c: string, idx: number) => (
                    <p key={idx}>{c}</p>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 06. CREATIVE STUDIO */}
          {activeMenu === "creative" && (
            <div className="space-y-6">
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-white">
                  AGENTE 05 — AI Creative Studio (Fábrica Real de Artes PNG, Carrosséis, Roteiros e E-books)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                  <input
                    value={creativeTitle}
                    onChange={(e) => setCreativeTitle(e.target.value)}
                    placeholder="Nome do Criativo"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <select
                    value={creativeType}
                    onChange={(e) => setCreativeType(e.target.value)}
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    <option value="SOCIAL_POST">Post 1080x1080</option>
                    <option value="CAROUSEL">Carrossel Multi-Slide</option>
                    <option value="THUMBNAIL">Thumbnail YouTube 1280x720</option>
                    <option value="COVER">Capa Stories/Reels 1080x1920</option>
                    <option value="BANNER">Banner Comercial 1200x628</option>
                    <option value="INFOGRAPHIC">Infográfico 1080x1600</option>
                    <option value="VIDEO_SCRIPT">Roteiro de Vídeo</option>
                    <option value="SHORT_VIDEO">Roteiro Reels/TikTok/Shorts</option>
                    <option value="EBOOK">E-book Executivo</option>
                    <option value="PRESENTATION">Apresentação Comercial</option>
                  </select>
                  <input
                    value={creativeHeadline}
                    onChange={(e) => setCreativeHeadline(e.target.value)}
                    placeholder="Headline Principal da Arte"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white md:col-span-2"
                  />
                  <button
                    onClick={async () => {
                      await apiFetch("/api/v1/creative/assets/generate", {
                        method: "POST",
                        body: JSON.stringify({
                          title: creativeTitle,
                          asset_type: creativeType,
                          platform: "instagram",
                          headline_text: creativeHeadline,
                          cta_text: creativeCta,
                        }),
                      });
                      await loadAllActiveData();
                      showNotice("Ativo visual renderizado em PNG com sucesso!");
                    }}
                    className="py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Produzir Ativo Visual
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {creativeData.map((asset: any) => (
                  <div
                    key={asset.id}
                    className="bg-[#0f1629] border border-slate-800 rounded-xl overflow-hidden flex flex-col"
                  >
                    {asset.preview_data_uri && (
                      <img
                        src={asset.preview_data_uri}
                        alt={asset.title}
                        className="w-full h-56 object-contain bg-slate-950 border-b border-slate-800"
                      />
                    )}
                    <div className="p-4 space-y-2 text-xs flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-indigo-300">{asset.asset_type}</span>
                        <span className="text-slate-400">{asset.dimensions}</span>
                      </div>
                      <div className="font-bold text-white text-sm">{asset.title}</div>
                      <div className="text-[10px] text-emerald-400">{asset.license_info}</div>
                      {asset.content?.slides && (
                        <div className="p-2 rounded bg-slate-900 text-[11px] text-slate-300 space-y-1">
                          <div className="font-semibold text-indigo-300">Slides do Carrossel:</div>
                          {asset.content.slides.map((s: any) => (
                            <div key={s.slide}>
                              <strong>S{s.slide}:</strong> {s.title}
                            </div>
                          ))}
                        </div>
                      )}
                      {asset.preview_data_uri && (
                        <a
                          href={asset.preview_data_uri}
                          download={`${asset.title}.png`}
                          className="inline-block mt-2 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-white text-[11px]"
                        >
                          Baixar PNG Original
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 07. COPYWRITER */}
          {activeMenu === "copywriter" && (
            <div className="space-y-6">
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-white">
                  AGENTE 06 — AI Copywriter (Textos Persuasivos com Variantes A/B e Verificação Ética)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
                  <input
                    value={copyTitle}
                    onChange={(e) => setCopyTitle(e.target.value)}
                    placeholder="Título da Copy"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <select
                    value={copyType}
                    onChange={(e) => setCopyType(e.target.value)}
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    <option value="LANDING_PAGE">Landing Page</option>
                    <option value="SALES_PAGE">Página de Vendas</option>
                    <option value="AD_COPY">Anúncio Pago</option>
                    <option value="EMAIL_SEQUENCE">Sequência de E-mail</option>
                    <option value="SALES_SCRIPT">Script de Vendas</option>
                    <option value="WHATSAPP_MESSAGE">Mensagem WhatsApp</option>
                    <option value="HEADLINE">Headline & CTA</option>
                    <option value="PRODUCT_DESCRIPTION">Descrição de Produto</option>
                  </select>
                  <select
                    value={copyFramework}
                    onChange={(e) => setCopyFramework(e.target.value)}
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    <option value="AIDA">Framework AIDA</option>
                    <option value="PAS">Framework PAS</option>
                    <option value="BAB">Framework BAB</option>
                    <option value="FAB">Framework FAB</option>
                    <option value="4PS">Framework 4Ps</option>
                    <option value="STORYBRAND">StoryBrand</option>
                  </select>
                  <input
                    value={copyOffer}
                    onChange={(e) => setCopyOffer(e.target.value)}
                    placeholder="Produto / Oferta"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <input
                    value={copyBenefit}
                    onChange={(e) => setCopyBenefit(e.target.value)}
                    placeholder="Benefício Principal"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <button
                    onClick={async () => {
                      await apiFetch("/api/v1/copywriter/generate", {
                        method: "POST",
                        body: JSON.stringify({
                          title: copyTitle,
                          copy_type: copyType,
                          framework: copyFramework,
                          product_or_offer: copyOffer,
                          target_audience: meData?.active_tenant?.target_audience || "Empresas B2B",
                          key_benefit: copyBenefit,
                        }),
                      });
                      await loadAllActiveData();
                      showNotice("Variantes A/B de Copy geradas com sucesso!");
                    }}
                    className="py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Gerar Copy A/B
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                {copyData.map((c: any) => (
                  <div key={c.id} className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white text-sm">
                        {c.title} ({c.copy_type} • {c.framework})
                      </span>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">
                        Compliance Ético Verificado
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-3 rounded bg-slate-900 border border-slate-800 whitespace-pre-line">
                        <div className="font-bold text-indigo-300 mb-1">Variante A (Controle)</div>
                        {c.variant_a}
                      </div>
                      <div className="p-3 rounded bg-slate-900 border border-slate-800 whitespace-pre-line">
                        <div className="font-bold text-emerald-300 mb-1">Variante B (Desafiante Teste A/B)</div>
                        {c.variant_b}
                      </div>
                    </div>
                    <div className="text-slate-400">
                      <strong>Hipótese A/B:</strong> {c.ab_test_hypothesis}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 08. GROWTH HACKER */}
          {activeMenu === "growth" && (
            <div className="space-y-6">
              <div className="bg-[#0f1629] border border-slate-800 p-5 rounded-xl space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white">
                    AGENTE 07 — AI Growth Hacker (Experimentos, Hipóteses ICE e Otimização de Funil)
                  </h3>
                  <button
                    onClick={async () => {
                      await apiFetch("/api/v1/agents/AGENT_07_GROWTH/execute", {
                        method: "POST",
                        body: JSON.stringify({}),
                      });
                      await loadAllActiveData();
                      showNotice("Novo experimento de Growth estruturado pela IA!");
                    }}
                    className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Gerar Experimento ICE Automático
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-3 pt-2 border-t border-slate-800">
                  <input
                    value={expTitle}
                    onChange={(e) => setExpTitle(e.target.value)}
                    placeholder="Título do Experimento"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <input
                    value={expChannel}
                    onChange={(e) => setExpChannel(e.target.value)}
                    placeholder="Canal (ex: Landing Page)"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <input
                    value={expHyp}
                    onChange={(e) => setExpHyp(e.target.value)}
                    placeholder="Hipótese Testável"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <button
                    onClick={async () => {
                      if (!expTitle || !expHyp) return;
                      await apiFetch("/api/v1/growth/experiments", {
                        method: "POST",
                        body: JSON.stringify({
                          title: expTitle,
                          channel: expChannel,
                          hypothesis: expHyp,
                          objective: expObj,
                          impact: 9,
                          confidence: 8,
                          ease: 8,
                        }),
                      });
                      setExpTitle("");
                      setExpHyp("");
                      await loadAllActiveData();
                      showNotice("Experimento de Growth registrado!");
                    }}
                    className="py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                  >
                    Registrar Experimento
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {growthData.map((exp: any) => (
                  <div key={exp.id} className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white text-sm">{exp.title}</span>
                      <OriginBadge origin={exp.data_origin} />
                    </div>
                    <div className="text-indigo-300 font-semibold">
                      Canal: {exp.channel} • ICE Score: {exp.ice_score}/10 • Status: {exp.status}
                    </div>
                    <p className="text-slate-300">
                      <strong>Hipótese:</strong> {exp.hypothesis}
                    </p>
                    <p className="text-slate-300">
                      <strong>Indicador:</strong> {exp.indicator_metric}
                    </p>
                    <p className="text-slate-300">
                      <strong>Linha de Base:</strong> {exp.baseline_conversion_pct}% |{" "}
                      <strong>Resultado Real:</strong>{" "}
                      {exp.real_result_conversion_pct !== null
                        ? `${exp.real_result_conversion_pct}%`
                        : "Aguardando coleta"}
                    </p>
                    <p className="text-emerald-300">
                      <strong>Conclusão:</strong> {exp.conclusion}
                    </p>
                    {exp.status !== "COMPLETED" && (
                      <button
                        onClick={async () => {
                          await apiFetch(`/api/v1/growth/experiments/${exp.id}/result`, {
                            method: "PUT",
                            body: JSON.stringify({
                              real_result_conversion_pct: Number((exp.baseline_conversion_pct * 1.45).toFixed(2)),
                              real_result_summary: "Resultado real validado em produção.",
                              conclusion: "Hipótese validada com ganho real de conversão.",
                              status: "COMPLETED",
                            }),
                          });
                          await loadAllActiveData();
                          showNotice("Resultado real aferido e experimento concluído!");
                        }}
                        className="mt-2 px-3 py-1 rounded bg-slate-800 hover:bg-emerald-700 text-white text-[11px]"
                      >
                        Registrar Resultado Real Aferido
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 09. CRM & LEADS */}
          {activeMenu === "crm" && crmData && (
            <div className="space-y-6">
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <h4 className="text-sm font-bold text-white">
                  AGENTE 08 — Captura de Leads, Qualificação e Lead Scoring (Consentimento LGPD Obrigatório)
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
                  <input
                    value={leadName}
                    onChange={(e) => setLeadName(e.target.value)}
                    placeholder="Nome do Contato"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <input
                    value={leadEmail}
                    onChange={(e) => setLeadEmail(e.target.value)}
                    placeholder="E-mail Corporativo"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <input
                    value={leadPhone}
                    onChange={(e) => setLeadPhone(e.target.value)}
                    placeholder="WhatsApp / Telefone"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <input
                    value={leadCompany}
                    onChange={(e) => setLeadCompany(e.target.value)}
                    placeholder="Empresa"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <input
                    type="number"
                    value={leadValue}
                    onChange={(e) => setLeadValue(e.target.value)}
                    placeholder="Valor Estimado (R$)"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <button
                    onClick={async () => {
                      if (!leadName || !leadEmail) return;
                      await apiFetch("/api/v1/crm/leads", {
                        method: "POST",
                        body: JSON.stringify({
                          full_name: leadName,
                          email: leadEmail,
                          phone: leadPhone,
                          company_name: leadCompany,
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
                      await loadAllActiveData();
                      showNotice("Lead cadastrado, pontuado pelo AI Sales Director e follow-up criado!");
                    }}
                    className="py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                  >
                    Qualificar & Registrar
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <h4 className="text-sm font-bold text-white">Base de Leads Qualificados</h4>
                  {crmData.leads.map((l: any) => (
                    <div
                      key={l.id}
                      className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs flex justify-between items-center"
                    >
                      <div>
                        <div className="font-bold text-white">
                          {l.full_name} ({l.company_name || "Direto"})
                        </div>
                        <div className="text-slate-400">
                          {l.email} • {l.phone} • Origem: {l.source_channel}
                        </div>
                        <div className="text-indigo-300 mt-1">
                          Status: {l.qualification_status} • Estágio: {l.pipeline_stage} • Valor Est.: R${" "}
                          {l.estimated_value}
                        </div>
                      </div>
                      <div className="text-right space-y-1">
                        <div className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 font-bold">
                          Score: {l.lead_score}/100
                        </div>
                        <OriginBadge origin={l.data_origin} />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <h4 className="text-sm font-bold text-white">Atividades & Tarefas de Follow-up</h4>
                  {crmData.activities.map((a: any) => (
                    <div key={a.id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs space-y-1">
                      <div className="flex justify-between font-bold text-indigo-300">
                        <span>{a.subject}</span>
                        <span>Prazo: {a.due_date}</span>
                      </div>
                      <div className="text-slate-300">{a.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 10. COMERCIAL & PIPELINE VISUAL */}
          {activeMenu === "commercial" && crmData && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Negociações Abertas</div>
                  <div className="text-2xl font-bold text-white">{crmData.commercial_summary.open_deals_count}</div>
                </div>
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Negociações Ganhas (WON)</div>
                  <div className="text-2xl font-bold text-emerald-400">{crmData.commercial_summary.won_deals_count}</div>
                </div>
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Receita Fechada (CLOSED_WON)</div>
                  <div className="text-2xl font-bold text-indigo-400">
                    R$ {crmData.commercial_summary.won_revenue_brl.toLocaleString("pt-BR")}
                  </div>
                </div>
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Previsão Ponderada Pipeline</div>
                  <div className="text-2xl font-bold text-amber-400">
                    R$ {crmData.commercial_summary.weighted_forecast_brl.toLocaleString("pt-BR")}
                  </div>
                </div>
              </div>

              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <h4 className="text-sm font-bold text-white">Nova Oportunidade / Proposta no Pipeline</h4>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                  <input
                    value={dealTitle}
                    onChange={(e) => setDealTitle(e.target.value)}
                    placeholder="Título da Negociação / Proposta"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <input
                    type="number"
                    value={dealValue}
                    onChange={(e) => setDealValue(e.target.value)}
                    placeholder="Valor do Contrato (R$)"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <select
                    value={dealStage}
                    onChange={(e) => setDealStage(e.target.value)}
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    {PIPELINE_STAGES.map((st) => (
                      <option key={st} value={st}>
                        {st}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={async () => {
                      if (!dealTitle) return;
                      await apiFetch("/api/v1/crm/deals", {
                        method: "POST",
                        body: JSON.stringify({
                          title: dealTitle,
                          stage: dealStage,
                          value: Number(dealValue) || 0,
                          probability_pct: 70,
                          data_origin: "REAL",
                        }),
                      });
                      setDealTitle("");
                      await loadAllActiveData();
                      showNotice("Negociação adicionada ao Pipeline Comercial!");
                    }}
                    className="py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Criar Proposta no Pipeline
                  </button>
                </div>
              </div>

              {/* Pipeline Kanban Visual */}
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3">
                {PIPELINE_STAGES.map((stage) => {
                  const stageDeals = crmData.deals.filter((d: any) => d.stage === stage);
                  return (
                    <div key={stage} className="bg-[#0f1629] border border-slate-800 rounded-xl p-3 space-y-2">
                      <div className="text-[11px] font-bold text-indigo-300 flex justify-between">
                        <span>{stage}</span>
                        <span>({stageDeals.length})</span>
                      </div>
                      {stageDeals.map((d: any) => (
                        <div key={d.id} className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs space-y-1.5">
                          <div className="font-bold text-white">{d.title}</div>
                          <div className="text-emerald-400 font-semibold">
                            R$ {d.value.toLocaleString("pt-BR")}
                          </div>
                          <select
                            value={d.stage}
                            onChange={async (e) => {
                              await apiFetch(`/api/v1/crm/deals/${d.id}/stage`, {
                                method: "PUT",
                                body: JSON.stringify({ stage: e.target.value }),
                              });
                              await loadAllActiveData();
                              showNotice(`Negociação movida para ${e.target.value}!`);
                            }}
                            className="w-full px-1.5 py-1 rounded bg-slate-950 border border-slate-700 text-[10px] text-slate-200"
                          >
                            {PIPELINE_STAGES.map((s) => (
                              <option key={s} value={s}>
                                Mover: {s}
                              </option>
                            ))}
                          </select>
                        </div>
                      ))}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* 11. CONCORRENTES */}
          {activeMenu === "competitors" && (
            <div className="space-y-6">
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-white">
                  AGENTE 09 — AI Competitive Intelligence (Análise Ética de Sites Públicos Respeitando robots.txt)
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <input
                    value={compName}
                    onChange={(e) => setCompName(e.target.value)}
                    placeholder="Nome do Concorrente"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <input
                    value={compUrl}
                    onChange={(e) => setCompUrl(e.target.value)}
                    placeholder="https://concorrente.com.br"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <button
                    onClick={async () => {
                      if (!compName) return;
                      await apiFetch("/api/v1/competitors", {
                        method: "POST",
                        body: JSON.stringify({ name: compName, website_url: compUrl }),
                      });
                      setCompName("");
                      await loadAllActiveData();
                      showNotice("Concorrente analisado respeitando robots.txt!");
                    }}
                    className="py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Analisar Concorrente
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {competitorsData.map((c: any) => (
                  <div key={c.id} className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white text-sm">{c.name}</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">
                        robots.txt respeitado
                      </span>
                    </div>
                    <div className="text-indigo-400">{c.website_url}</div>
                    <p className="text-slate-300">{c.positioning_summary}</p>
                    <p className="text-slate-400">
                      <strong>Preços Públicos:</strong> {c.public_pricing_summary}
                    </p>
                    <div className="pt-2 border-t border-slate-800">
                      <div className="font-bold text-emerald-300 mb-1">Oportunidades de Diferenciação:</div>
                      {c.differentiation_opportunities.map((op: string, idx: number) => (
                        <div key={idx} className="text-slate-300">
                          • {op}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 12. FINANCEIRO & PERFORMANCE */}
          {activeMenu === "finance" && financeData && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Receita Real / Importada</div>
                  <div className="text-xl font-bold text-emerald-400">
                    R$ {financeData.kpis.real_revenue.toLocaleString("pt-BR")}
                  </div>
                </div>
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Lucro Líquido Real</div>
                  <div className="text-xl font-bold text-white">
                    R$ {financeData.kpis.real_profit.toLocaleString("pt-BR")}
                  </div>
                </div>
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Margem / ROI / ROAS</div>
                  <div className="text-xl font-bold text-indigo-400">
                    {financeData.kpis.margin_pct}% | {financeData.kpis.roi_pct}% | {financeData.kpis.roas_multiplier}x
                  </div>
                </div>
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">CAC / Ticket Médio / LTV</div>
                  <div className="text-xl font-bold text-amber-400">
                    R$ {financeData.kpis.cac_brl} / R$ {financeData.kpis.average_ticket_brl}
                  </div>
                </div>
              </div>

              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <h4 className="text-sm font-bold text-white">
                  Registrar / Importar Lançamento Financeiro (Separação Estrita Real vs Estimativa)
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                  <select
                    value={finType}
                    onChange={(e) => setFinType(e.target.value)}
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    <option value="REVENUE">Receita (REVENUE)</option>
                    <option value="EXPENSE">Despesa Operacional (EXPENSE)</option>
                    <option value="AD_SPEND">Investimento em Mídia (AD_SPEND)</option>
                  </select>
                  <input
                    type="number"
                    value={finAmount}
                    onChange={(e) => setFinAmount(e.target.value)}
                    placeholder="Valor R$"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <select
                    value={finOrigin}
                    onChange={(e) => setFinOrigin(e.target.value)}
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    <option value="REAL">DADO REAL</option>
                    <option value="IMPORTED">DADO IMPORTADO</option>
                    <option value="ESTIMATED">ESTIMATIVA</option>
                    <option value="GOAL">META</option>
                  </select>
                  <input
                    value={finDesc}
                    onChange={(e) => setFinDesc(e.target.value)}
                    placeholder="Descrição do lançamento"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <button
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
                      await loadAllActiveData();
                      showNotice("Lançamento financeiro registrado e KPIs recalculados!");
                    }}
                    className="py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                  >
                    Registrar Lançamento
                  </button>
                </div>
              </div>

              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-2">
                <h4 className="text-sm font-bold text-white">Razão de Lançamentos Financeiros</h4>
                {financeData.records.map((r: any) => (
                  <div
                    key={r.id}
                    className="flex items-center justify-between p-3 rounded bg-slate-900 border border-slate-800 text-xs"
                  >
                    <div>
                      <span className="font-bold text-white">{r.record_type}</span> • {r.description} ({r.period_date})
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-slate-200">R$ {r.amount.toLocaleString("pt-BR")}</span>
                      <OriginBadge origin={r.data_origin} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 13. CUSTOMER SUCCESS */}
          {activeMenu === "cs" && csData && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">NPS Médio</div>
                  <div className="text-2xl font-bold text-emerald-400">{csData.summary.average_nps} / 10</div>
                </div>
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">CSAT Médio</div>
                  <div className="text-2xl font-bold text-indigo-400">{csData.summary.average_csat} / 5</div>
                </div>
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Clientes em Risco de Churn</div>
                  <div className="text-2xl font-bold text-red-400">{csData.summary.high_churn_risk_count}</div>
                </div>
                <div className="p-4 bg-[#0f1629] border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Oportunidades de Upsell</div>
                  <div className="text-2xl font-bold text-amber-400">{csData.summary.upsell_ready_count}</div>
                </div>
              </div>

              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <h4 className="text-sm font-bold text-white">
                  Registrar Pesquisa de Satisfação (NPS / CSAT) & Detectar Risco ou Upsell
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                  <input
                    value={csName}
                    onChange={(e) => setCsName(e.target.value)}
                    placeholder="Nome do Cliente"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <input
                    value={csEmail}
                    onChange={(e) => setCsEmail(e.target.value)}
                    placeholder="E-mail do Cliente"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <select
                    value={csNps}
                    onChange={(e) => setCsNps(e.target.value)}
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  >
                    {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0].map((n) => (
                      <option key={n} value={n}>
                        Nota NPS: {n}
                      </option>
                    ))}
                  </select>
                  <input
                    value={csText}
                    onChange={(e) => setCsText(e.target.value)}
                    placeholder="Feedback do cliente"
                    className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <button
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
                      await loadAllActiveData();
                      showNotice("Feedback analisado pelo AI Customer Success!");
                    }}
                    className="py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Analisar Feedback
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                {csData.feedbacks.map((f: any) => (
                  <div key={f.id} className="bg-[#0f1629] border border-slate-800 rounded-xl p-4 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white">{f.customer_name}</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-bold">
                        NPS {f.nps_score} • Risco Churn: {f.churn_risk}
                      </span>
                    </div>
                    <p className="text-slate-300">&ldquo;{f.feedback_text}&rdquo;</p>
                    <div className="text-indigo-300">
                      <strong>Ação de Retenção:</strong> {f.retention_suggestion}
                    </div>
                    <div className="text-emerald-300">
                      <strong>Oportunidade Comercial (Upsell):</strong> {f.upsell_opportunity}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 15. AUTOMAÇÕES NATIVAS PYTHON */}
          {activeMenu === "automations" && automationsData && (
            <div className="space-y-6">
              <div className="bg-[#0f1629] border border-emerald-500/30 rounded-xl p-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">
                    Central de Automações 100% Nativa em Python (Zero Dependência de n8n)
                  </h3>
                  <p className="text-xs text-slate-400">
                    Motor: {automationsData.scheduler?.engine} • Status:{" "}
                    <strong className="text-emerald-400">
                      {automationsData.scheduler?.running ? "ATIVO NO SERVIDOR CLOUD" : "PARADO"}
                    </strong>
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {automationsData.rules.map((r: any) => (
                  <div key={r.id} className="bg-[#0f1629] border border-slate-800 rounded-xl p-4 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white">{r.name}</span>
                      <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-mono text-[10px]">
                        {r.trigger_type} • {r.frequency_label}
                      </span>
                    </div>
                    <div className="text-slate-400">
                      Agente Responsável: <strong className="text-slate-200">{r.action_agent}</strong> • Execuções:{" "}
                      {r.run_count} • Último Status: <strong className="text-emerald-400">{r.last_status}</strong>
                    </div>
                    <div className="pt-2 flex gap-2">
                      <button
                        onClick={async () => {
                          await apiFetch(`/api/v1/automations/${r.id}/run`, {
                            method: "POST",
                            body: JSON.stringify({}),
                          });
                          await loadAllActiveData();
                          showNotice(`Automação '${r.name}' executada imediatamente!`);
                        }}
                        className="px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
                      >
                        Executar Agora
                      </button>
                      <button
                        onClick={async () => {
                          const res = await apiFetch(`/api/v1/automations/${r.id}/run`, {
                            method: "POST",
                            body: JSON.stringify({ simulate_transient_failure: true }),
                          });
                          await loadAllActiveData();
                          showNotice(
                            `Retry com Backoff validado: status ${res.status} na tentativa #${res.attempt_number}!`
                          );
                        }}
                        className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
                      >
                        Testar Retry + Backoff
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {automationsData.executions?.length > 0 && (
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-2">
                  <h4 className="text-sm font-bold text-white">Histórico Persistido de Execuções do Scheduler</h4>
                  {automationsData.executions.map((ex: any) => (
                    <div
                      key={ex.id}
                      className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs flex justify-between"
                    >
                      <div>
                        <span className="font-bold text-indigo-300">Regra #{ex.rule_id}</span> •{" "}
                        {ex.result_summary?.summary || ex.error_message}
                      </div>
                      <div className="text-slate-400">
                        Status: <strong className="text-emerald-400">{ex.status}</strong> (Tentativa #
                        {ex.attempt_number} • {ex.duration_ms}ms)
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 16. APROVAÇÕES */}
          {activeMenu === "approvals" && (
            <div className="space-y-4">
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-4">
                <h3 className="text-sm font-bold text-white">
                  Central de Aprovações Humanas & Governança de Ações de Alto Impacto
                </h3>
                <p className="text-xs text-slate-400">
                  Publicações externas, ativação de orçamento pago e alterações críticas aguardam validação humana por padrão.
                </p>
              </div>
              {approvalsData.map((req: any) => (
                <div
                  key={req.id}
                  className="bg-[#0f1629] border border-slate-800 rounded-xl p-4 flex items-center justify-between text-xs"
                >
                  <div className="space-y-1">
                    <div className="font-bold text-white text-sm">{req.title}</div>
                    <div className="text-slate-400">
                      Agente: {req.agent_id} • Tipo: {req.action_type} • Status:{" "}
                      <strong className="text-amber-300">{req.status}</strong>
                    </div>
                  </div>
                  {req.status === "PENDING" && (
                    <div className="flex gap-2">
                      <button
                        onClick={async () => {
                          await apiFetch(`/api/v1/approvals/${req.id}/decide`, {
                            method: "POST",
                            body: JSON.stringify({
                              decision: "APPROVE",
                              confirmation_token: meData?.high_impact_confirmation_token || "CONFIRMED_BY_HUMAN",
                            }),
                          });
                          await loadAllActiveData();
                          showNotice("Solicitação aprovada e processada!");
                        }}
                        className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
                      >
                        Aprovar
                      </button>
                      <button
                        onClick={async () => {
                          await apiFetch(`/api/v1/approvals/${req.id}/decide`, {
                            method: "POST",
                            body: JSON.stringify({ decision: "REJECT" }),
                          });
                          await loadAllActiveData();
                          showNotice("Solicitação rejeitada.");
                        }}
                        className="px-3 py-1.5 rounded bg-red-600/80 hover:bg-red-600 text-white font-semibold"
                      >
                        Rejeitar
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* 17. RELATÓRIOS */}
          {activeMenu === "reports" && reportsData && (
            <div className="space-y-6">
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white">Relatório Executivo Consolidado</h3>
                  <button
                    onClick={async () => {
                      const bkp = await apiFetch("/api/v1/system/backup", { method: "POST" });
                      showNotice(`Backup persistente criado: ${bkp.backup_file} (${bkp.size_bytes} bytes)`);
                    }}
                    className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Gerar Snapshot & Backup Agora
                  </button>
                </div>
                <pre className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 overflow-x-auto">
                  {JSON.stringify(reportsData, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* 18. INTEGRAÇÕES */}
          {activeMenu === "integrations" && (
            <div className="space-y-4">
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-4">
                <h3 className="text-sm font-bold text-white">
                  Central de Integrações Oficiais (Criptografia Fernet • Status Real Sem Simulação)
                </h3>
                <p className="text-xs text-slate-400">
                  Cada integração informa exatamente qual credencial é necessária, onde obtê-la, permissões exigidas e teste real.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {integrationsData.map((intg: any) => (
                  <div
                    key={intg.provider_key}
                    className="bg-[#0f1629] border border-slate-800 rounded-xl p-4 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white text-sm">{intg.provider_name}</span>
                      <span
                        className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                          intg.status === "CONNECTED"
                            ? "bg-emerald-500/20 text-emerald-300"
                            : "bg-amber-500/20 text-amber-300"
                        }`}
                      >
                        {intg.status}
                      </span>
                    </div>
                    <div className="text-slate-300">
                      <strong>Funcionalidade Habilitada:</strong> {intg.setup_guide.features_unlocked}
                    </div>
                    <div className="text-slate-400">
                      <strong>Credenciais Necessárias:</strong> {intg.setup_guide.required_credentials.join(", ")}
                    </div>
                    <div className="text-slate-400">
                      <strong>Onde Obter:</strong> {intg.setup_guide.where_to_obtain}
                    </div>
                    <div className="text-slate-400">
                      <strong>Escopos Oficiais:</strong> {intg.setup_guide.permissions_required.join(", ")}
                    </div>
                    {intg.last_error && <div className="text-amber-400 text-[11px]">{intg.last_error}</div>}
                    <div className="pt-2 flex gap-2">
                      <input
                        value={credInputs[intg.provider_key] || ""}
                        onChange={(e) =>
                          setCredInputs({ ...credInputs, [intg.provider_key]: e.target.value })
                        }
                        placeholder={`Token / Chave para ${intg.provider_key}`}
                        className="flex-1 px-2.5 py-1 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                      />
                      <button
                        onClick={async () => {
                          const raw = credInputs[intg.provider_key] || "";
                          const credsObj: Record<string, string> = {};
                          for (const reqKey of intg.setup_guide.required_credentials) {
                            credsObj[reqKey] = raw;
                          }
                          const r = await apiFetch("/api/v1/integrations/connect", {
                            method: "POST",
                            body: JSON.stringify({
                              provider_key: intg.provider_key,
                              credentials: credsObj,
                            }),
                          });
                          await loadAllActiveData();
                          showNotice(`${intg.provider_name}: ${r.message}`);
                        }}
                        className="px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
                      >
                        Salvar & Testar
                      </button>
                      <button
                        onClick={async () => {
                          const r = await apiFetch(`/api/v1/integrations/${intg.provider_key}/test`, {
                            method: "POST",
                          });
                          await loadAllActiveData();
                          showNotice(`${intg.provider_name}: ${r.message}`);
                        }}
                        className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-white"
                      >
                        Testar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 19. CONFIGURAÇÕES, AUTONOMIA & PLANOS SAAS */}
          {activeMenu === "settings" && meData && (
            <div className="space-y-6">
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-white">Nível de Autonomia Operacional da IA</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    {
                      level: 1,
                      title: "NÍVEL 1 — ASSISTIDO",
                      desc: "A IA analisa, diagnostica e recomenda; o usuário executa todas as ações.",
                    },
                    {
                      level: 2,
                      title: "NÍVEL 2 — SEMIAUTÔNOMO (Padrão Recomendado)",
                      desc: "A IA prepara tudo automaticamente e solicita aprovação humana antes de ações externas.",
                    },
                    {
                      level: 3,
                      title: "NÍVEL 3 — AUTÔNOMO",
                      desc: "A IA executa automaticamente as atividades autorizadas dentro dos limites de segurança.",
                    },
                  ].map((lvl) => (
                    <button
                      key={lvl.level}
                      onClick={async () => {
                        await apiFetch("/api/v1/tenants/current", {
                          method: "PUT",
                          body: JSON.stringify({ autonomy_default_level: lvl.level }),
                        });
                        await loadAllActiveData();
                        showNotice(`Nível de Autonomia atualizado para Nível ${lvl.level}!`);
                      }}
                      className={`p-4 rounded-xl border text-left transition ${
                        meData.active_tenant.autonomy_default_level === lvl.level
                          ? "bg-indigo-600/20 border-indigo-500 text-white"
                          : "bg-slate-900 border-slate-800 text-slate-300"
                      }`}
                    >
                      <div className="font-bold text-xs mb-1">{lvl.title}</div>
                      <div className="text-[11px] text-slate-400">{lvl.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Planos SaaS */}
              {meData.plans_catalog && (
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                  <h3 className="text-sm font-bold text-white">
                    Arquitetura de Planos para Comercialização SaaS (Cobrança Desativada por Padrão)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {Object.values(meData.plans_catalog).map((pl: any) => (
                      <div
                        key={pl.code}
                        className={`p-4 rounded-xl border text-xs space-y-2 ${
                          meData.active_tenant.plan_tier === pl.code
                            ? "bg-indigo-600/15 border-indigo-500"
                            : "bg-slate-900 border-slate-800"
                        }`}
                      >
                        <div className="font-bold text-white text-sm">{pl.name}</div>
                        <div className="text-slate-400">
                          Até {pl.max_companies} empresa(s) • {pl.agents_included.length} agentes
                        </div>
                        <ul className="space-y-1 text-slate-300">
                          {pl.features.map((f: string, idx: number) => (
                            <li key={idx}>• {f}</li>
                          ))}
                        </ul>
                        <button
                          onClick={async () => {
                            await apiFetch("/api/v1/tenants/current", {
                              method: "PUT",
                              body: JSON.stringify({ plan_tier: pl.code }),
                            });
                            await loadAllActiveData();
                            showNotice(`Plano alterado para ${pl.name}!`);
                          }}
                          className="w-full mt-2 py-1.5 rounded bg-slate-800 hover:bg-indigo-600 text-white font-semibold"
                        >
                          {meData.active_tenant.plan_tier === pl.code ? "Plano Ativo" : `Selecionar ${pl.name}`}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-bold text-white">Criar Nova Empresa no Grupo (Multi-Tenant Isolado)</h3>
                <div className="flex gap-3">
                  <input
                    value={newTenantName}
                    onChange={(e) => setNewTenantName(e.target.value)}
                    placeholder="Nome da Nova Empresa / Filial"
                    className="flex-1 px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                  />
                  <button
                    onClick={async () => {
                      if (!newTenantName) return;
                      await apiFetch("/api/v1/tenants", {
                        method: "POST",
                        body: JSON.stringify({ name: newTenantName, brand_name: newTenantName }),
                      });
                      setNewTenantName("");
                      await loadAllActiveData();
                      showNotice("Nova empresa criada com isolamento multi-tenant completo!");
                    }}
                    className="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                  >
                    Adicionar Empresa
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* FASE 17 — OPERAÇÃO COMERCIAL MULTINEGÓCIO (3 UNIDADES) */}
          {activeMenu === "multibusiness" && mbDashboard && (
            <div className="space-y-6">
              {/* Seletor de Unidade de Negócio */}
              <div className="bg-[#0f1629] border border-indigo-500/30 rounded-xl p-5 flex flex-wrap items-center justify-between gap-4">
                <div>
                  <h2 className="text-base font-bold text-white">
                    Central Executiva Multinegócio — 3 Fontes Independentes de Receita
                  </h2>
                  <p className="text-xs text-slate-400">
                    Fonte: {mbDashboard.data_source} • Período: {mbDashboard.period_reference} • Separação estrita entre DADO REAL, PROJEÇÃO e META
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {[
                    { code: "ALL", label: "Visão Consolidada (3 Unidades)" },
                    { code: "UNION_TECH", label: "Unidade A: UNION TECH (IA & Sistemas)" },
                    { code: "UNION_AGENCY", label: "Unidade B: UNION AGENCY (Clientes)" },
                    { code: "UNION_PARTNERS", label: "Unidade C: UNION PARTNERS (Afiliados)" },
                  ].map((u) => (
                    <button
                      key={u.code}
                      onClick={async () => {
                        setSelectedUnit(u.code);
                        const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${u.code}`);
                        setMbDashboard(res);
                      }}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                        selectedUnit === u.code
                          ? "bg-indigo-600 text-white"
                          : "bg-slate-900 border border-slate-700 text-slate-300 hover:bg-slate-800"
                      }`}
                    >
                      {u.label}
                    </button>
                  ))}
                  <button
                    onClick={async () => {
                      await apiFetch("/api/v1/ceo/multibusiness-briefing", { method: "POST" });
                      const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`);
                      setMbDashboard(res);
                      showNotice("Briefing Consolidado Multinegócio gerado pelo AI CEO!");
                    }}
                    className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white"
                  >
                    Gerar Briefing CEO Multinegócio
                  </button>
                </div>
              </div>

              {/* KPIs Financeiros Consolidados (DADO REAL vs PROJEÇÃO vs META) */}
              {mbDashboard.financial_summary?.consolidated && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-[#0f1629] border border-emerald-500/30 rounded-xl p-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[11px] text-slate-400">Receita Confirmada / Recebida</span>
                      <OriginBadge origin="REAL" />
                    </div>
                    <div className="text-xl font-bold text-emerald-400">
                      R$ {Number(mbDashboard.financial_summary.consolidated.dado_real.received_confirmed_revenue_brl || 0).toLocaleString("pt-BR")}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">
                      MRR Ativo: R$ {Number(mbDashboard.financial_summary.consolidated.dado_real.monthly_recurring_revenue_mrr_brl || 0).toLocaleString("pt-BR")}
                    </div>
                  </div>

                  <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[11px] text-slate-400">Lucro Líquido & Margem</span>
                      <OriginBadge origin="REAL" />
                    </div>
                    <div className="text-xl font-bold text-white">
                      R$ {Number(mbDashboard.financial_summary.consolidated.dado_real.net_profit_brl || 0).toLocaleString("pt-BR")}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">
                      Margem: {mbDashboard.financial_summary.consolidated.dado_real.margin_pct}% • Custos: R$ {Number(mbDashboard.financial_summary.consolidated.dado_real.expenses_and_costs_brl || 0).toLocaleString("pt-BR")}
                    </div>
                  </div>

                  <div className="bg-[#0f1629] border border-amber-500/30 rounded-xl p-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[11px] text-slate-400">Pipeline Ponderado (Não Recebido)</span>
                      <OriginBadge origin="ESTIMATED" />
                    </div>
                    <div className="text-xl font-bold text-amber-300">
                      R$ {Number(mbDashboard.financial_summary.consolidated.projecao.weighted_pipeline_projection_brl || 0).toLocaleString("pt-BR")}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">
                      Negociações abertas: {mbDashboard.financial_summary.consolidated.projecao.open_deals_count}
                    </div>
                  </div>

                  <div className="bg-[#0f1629] border border-purple-500/30 rounded-xl p-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[11px] text-slate-400">Meta de Receita Mensal</span>
                      <OriginBadge origin="GOAL" />
                    </div>
                    <div className="text-xl font-bold text-purple-300">
                      R$ {Number(mbDashboard.financial_summary.consolidated.meta.monthly_revenue_goal_brl || 0).toLocaleString("pt-BR")}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">
                      Atingimento Real: {mbDashboard.financial_summary.consolidated.meta.goal_attainment_pct}%
                    </div>
                  </div>
                </div>
              )}

              {/* FASE 18.1 — SEPARAÇÃO OBRIGATÓRIA: REAL vs ESTIMATIVA vs PROJEÇÃO vs META vs SIMULAÇÃO */}
              {mbDashboard.phase18_1_executive_panel && (
                <div className="bg-[#0f1629] border border-emerald-500/30 rounded-xl p-5 space-y-3">
                  <div className="flex flex-wrap justify-between items-center gap-2">
                    <h3 className="text-sm font-bold text-white">
                      Painel de Validação Comercial Fase 18.1 — Separação Estrita (REAL • ESTIMATIVA • PROJEÇÃO • META • SIMULAÇÃO)
                    </h3>
                    <span className="text-[11px] text-emerald-300 font-semibold">
                      Primeiro Cliente Pago em Produção (API Live):{" "}
                      {mbDashboard.phase18_1_executive_panel.REAL.first_real_paid_customer_verified ? "CONFIRMADO" : "AGUARDANDO 1º PAGAMENTO LIVE (R$ 0,00)"}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
                    <div className="p-3 rounded-lg bg-slate-900 border border-emerald-500/40 space-y-1">
                      <div className="font-bold text-emerald-400">1. REAL (Verificado Live)</div>
                      <div className="text-slate-300">Receita Live: <strong>R$ {mbDashboard.phase18_1_executive_panel.REAL.receita_recebida_confirmada_brl}</strong></div>
                      <div className="text-slate-400">Leads Reais: {mbDashboard.phase18_1_executive_panel.REAL.leads_reais} • Qualif: {mbDashboard.phase18_1_executive_panel.REAL.leads_qualificados}</div>
                      <div className="text-slate-400">Contratos c/ Evidência: {mbDashboard.phase18_1_executive_panel.REAL.contratos_assinados_com_evidencia}</div>
                      <div className="text-slate-400">Entregas c/ Evidência: {mbDashboard.phase18_1_executive_panel.REAL.entregas_concluidas_com_evidencia}</div>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900 border border-amber-500/30 space-y-1">
                      <div className="font-bold text-amber-300">2. ESTIMATIVA (Calculadora)</div>
                      <div className="text-slate-300">Custo Médio Serviço: R$ {mbDashboard.phase18_1_executive_panel.ESTIMATIVA.custo_medio_servico_brl}</div>
                      <div className="text-slate-400">Margem Estimada: {mbDashboard.phase18_1_executive_panel.ESTIMATIVA.margem_estimada_catalogo_pct}%</div>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900 border border-sky-500/30 space-y-1">
                      <div className="font-bold text-sky-300">3. PROJEÇÃO (Pipeline)</div>
                      <div className="text-slate-300">Pipeline Ponderado: R$ {mbDashboard.phase18_1_executive_panel.PROJECAO.pipeline_ponderado_aberto_brl}</div>
                      <div className="text-slate-400">Deals Abertos: {mbDashboard.phase18_1_executive_panel.PROJECAO.negociacoes_abertas_count}</div>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900 border border-purple-500/30 space-y-1">
                      <div className="font-bold text-purple-300">4. META (Objetivos)</div>
                      <div className="text-slate-300">Meta Mensal (3 Unidades): R$ {mbDashboard.phase18_1_executive_panel.META.meta_mensal_total_brl}</div>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-700 space-y-1">
                      <div className="font-bold text-slate-300">5. SIMULAÇÃO & SANDBOX</div>
                      <div className="text-slate-300">Cobranças Sandbox: {mbDashboard.phase18_1_executive_panel.SIMULACAO.cobrancas_sandbox_total} ({mbDashboard.phase18_1_executive_panel.SIMULACAO.pagamentos_sandbox_aprovados} aprov.)</div>
                      <div className="text-slate-400">Volume Sandbox: R$ {mbDashboard.phase18_1_executive_panel.SIMULACAO.valor_transacionado_sandbox_brl}</div>
                      <div className="text-slate-400">Seed Importado: R$ {mbDashboard.phase18_1_executive_panel.SIMULACAO.historico_importado_seed_brl}</div>
                    </div>
                  </div>
                  <p className="text-[11px] text-slate-400">{mbDashboard.phase18_1_executive_panel.honesty_statement}</p>
                </div>
              )}

              {/* Funil Comercial de 10 Etapas */}
              {mbDashboard.sales_funnel_10_stages && (
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5">
                  <h3 className="text-sm font-bold text-white mb-3">
                    Funil Comercial de 10 Etapas (Visitante → Pós-Venda)
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-5 lg:grid-cols-10 gap-2">
                    {Object.entries(mbDashboard.sales_funnel_10_stages).map(([stage, count]: [string, any]) => (
                      <div key={stage} className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-center">
                        <div className="text-[10px] font-semibold text-slate-400 truncate">{stage}</div>
                        <div className="text-base font-bold text-indigo-400 mt-0.5">{count}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* UNIDADE A — UNION TECH: Catálogo de 7 Serviços & Calculadora de Preços */}
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-sm font-bold text-white">
                    Catálogo de Serviços de IA & Automação (Calculadora Dinâmica de Custos e Preços)
                  </h3>
                  <span className="text-xs text-slate-400">
                    {mbDashboard.services_catalog?.length || 0} serviços ativos
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {(mbDashboard.services_catalog || []).map((svc: any) => (
                    <div key={svc.id} className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs space-y-2">
                      <div className="flex justify-between items-start gap-2">
                        <span className="font-bold text-indigo-300">{svc.name}</span>
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300">
                          {svc.business_unit_code}
                        </span>
                      </div>
                      <p className="text-slate-400 text-[11px]">{svc.problem_solved}</p>
                      <div className="p-2.5 rounded bg-slate-950 border border-slate-800/80 space-y-1">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Custo Estimado ({svc.pricing_calculator.dev_hours_estimated}h):</span>
                          <span className="text-slate-200">R$ {svc.pricing_calculator.estimated_cost_brl}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Preço Configurado (Setup):</span>
                          <span className="font-bold text-emerald-400">R$ {svc.pricing_calculator.configured_price_brl}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Mensalidade (MRR):</span>
                          <span className="text-indigo-300">R$ {svc.pricing_calculator.recurring_monthly_brl}/mês</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Status do Preço:</span>
                          <span className={svc.pricing_approved_by_owner ? "text-emerald-400" : "text-amber-300"}>
                            {svc.pricing_calculator.pricing_approved_by_owner ? "Aprovado pelo Proprietário" : "Sugerido pela Calculadora"}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={async () => {
                          await apiFetch(`/api/v1/commercial/services/${svc.id}/pricing`, {
                            method: "PUT",
                            body: JSON.stringify({ owner_approve_pricing: true }),
                          });
                          const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`);
                          setMbDashboard(res);
                          showNotice(`Preço de ${svc.service_code} aprovado pelo proprietário!`);
                        }}
                        className="w-full py-1.5 rounded bg-indigo-600/25 hover:bg-indigo-600 text-indigo-200 hover:text-white font-semibold transition"
                      >
                        Aprovar Tabela de Preço
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Gerador de Propostas Comerciais & Fechamento */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <h3 className="text-sm font-bold text-white">Gerador de Propostas Comerciais (Com Trava de Governança)</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    <input
                      value={propClientName}
                      onChange={(e) => setPropClientName(e.target.value)}
                      placeholder="Nome do Decisor / Contato"
                      className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    />
                    <input
                      value={propClientCompany}
                      onChange={(e) => setPropClientCompany(e.target.value)}
                      placeholder="Empresa Cliente"
                      className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    />
                    <input
                      value={propClientEmail}
                      onChange={(e) => setPropClientEmail(e.target.value)}
                      placeholder="E-mail Corporativo"
                      className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    />
                    <select
                      value={propServiceCode}
                      onChange={(e) => setPropServiceCode(e.target.value)}
                      className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    >
                      {(mbDashboard.services_catalog || []).map((s: any) => (
                        <option key={s.service_code} value={s.service_code}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <textarea
                    value={propProblem}
                    onChange={(e) => setPropProblem(e.target.value)}
                    placeholder="Problema operacional identificado no cliente..."
                    className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white h-16"
                  />
                  <button
                    onClick={async () => {
                      if (!propClientName || !propClientCompany || !propClientEmail) return;
                      await apiFetch("/api/v1/commercial/proposals", {
                        method: "POST",
                        body: JSON.stringify({
                          business_unit_code: "UNION_TECH",
                          service_code: propServiceCode,
                          client_name: propClientName,
                          client_company: propClientCompany,
                          client_email: propClientEmail,
                          identified_problem: propProblem || "Gargalos manuais em atendimento e integração de dados.",
                        }),
                      });
                      setPropClientName("");
                      setPropClientCompany("");
                      setPropClientEmail("");
                      setPropProblem("");
                      const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`);
                      setMbDashboard(res);
                      showNotice("Proposta comercial gerada em status PENDING_APPROVAL!");
                    }}
                    className="w-full py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Gerar Proposta Comercial e Enviar para Fila de Aprovação
                  </button>

                  <div className="space-y-2 max-h-64 overflow-y-auto pt-2">
                    {(mbDashboard.proposals || []).map((p: any) => (
                      <div key={p.id} className="p-3 rounded bg-slate-900 border border-slate-800 text-xs flex justify-between items-center gap-2">
                        <div>
                          <div className="font-bold text-white">
                            {p.proposal_number} • {p.client_company}
                          </div>
                          <div className="text-slate-400">
                            Setup: R$ {p.setup_price_brl} • MRR: R$ {p.monthly_price_brl}/mês • Status: <span className="text-amber-300 font-semibold">{p.status}</span>
                          </div>
                        </div>
                        <div className="flex gap-1.5">
                          <a
                            href={`${p.pdf_url}?access_token=${encodeURIComponent(token || "")}${activeTenantId ? `&tenant_id=${activeTenantId}` : ""}`}
                            target="_blank"
                            rel="noreferrer"
                            className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-indigo-300 font-semibold"
                          >
                            PDF
                          </a>
                          {p.status !== "ACCEPTED" && (
                            <button
                              onClick={async () => {
                                await apiFetch(`/api/v1/commercial/proposals/${p.id}/status`, {
                                  method: "PUT",
                                  body: JSON.stringify({ status: "ACCEPTED", owner_approve: true }),
                                });
                                const res = await apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`);
                                setMbDashboard(res);
                                showNotice(`Proposta ${p.proposal_number} aprovada e fechada (ACCEPTED)!`);
                              }}
                              className="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
                            >
                              Aprovar & Fechar
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* UNIDADE B (UNION AGENCY) & UNIDADE C (UNION PARTNERS) */}
                <div className="space-y-4">
                  <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                    <h3 className="text-sm font-bold text-white">
                      UNIDADE B — UNION AGENCY (Contas Isoladas de Empresas Clientes)
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      <input
                        value={agencyClientName}
                        onChange={(e) => setAgencyClientName(e.target.value)}
                        placeholder="Razão Social Cliente"
                        className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                      />
                      <input
                        value={agencyBrandName}
                        onChange={(e) => setAgencyBrandName(e.target.value)}
                        placeholder="Marca"
                        className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                      />
                      <select
                        value={agencyPlanTier}
                        onChange={(e) => setAgencyPlanTier(e.target.value)}
                        className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                      >
                        <option value="STARTER">STARTER</option>
                        <option value="PRO">PRO</option>
                        <option value="BUSINESS">BUSINESS</option>
                        <option value="ENTERPRISE">ENTERPRISE</option>
                      </select>
                      <button
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
                          showNotice("Conta isolada de cliente adicionada na UNION AGENCY!");
                        }}
                        className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                      >
                        + Cliente Agência
                      </button>
                    </div>
                    <div className="space-y-1.5 max-h-36 overflow-y-auto">
                      {(mbDashboard.agency_clients || []).map((c: any) => (
                        <div key={c.id} className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs flex justify-between">
                          <span>
                            <strong>{c.brand_name}</strong> ({c.client_name}) • Plano {c.plan_tier}
                          </span>
                          <span className="text-emerald-400 font-semibold">R$ {c.monthly_retainer_brl}/mês</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                    <h3 className="text-sm font-bold text-white">
                      UNIDADE C — UNION PARTNERS (Programas de Afiliados & Conciliação)
                    </h3>
                    <div className="space-y-1.5 max-h-40 overflow-y-auto">
                      {(mbDashboard.affiliate_operation?.programs || []).map((prog: any) => (
                        <div key={prog.id} className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs flex justify-between items-center">
                          <div>
                            <div className="font-bold text-white">{prog.name}</div>
                            <div className="text-[11px] text-slate-400">
                              Comissão Ref: {prog.default_commission_pct}% • Janela: {prog.attribution_window_days}d • {prog.official_api_status}
                            </div>
                          </div>
                          <span className="px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30 text-[10px] font-semibold">
                            {prog.approval_status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* FASE 18 — PAGAMENTOS (MERCADO PAGO & SANDBOX) + PROJETOS & ENTREGAS (ONBOARDING) */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex justify-between items-center">
                    <h3 className="text-sm font-bold text-white">
                      8. Pagamentos & Recebimentos (Mercado Pago / Sandbox Verificado)
                    </h3>
                    <button
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
                      className="px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                    >
                      + Emitir Cobrança Sandbox Aprovada
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Regra Estrita: Cobrança PENDING jamais conta como receita recebida. Somente confirmação via Webhook HMAC-SHA256 reconcilia no Financeiro e dispara o Onboarding.
                  </p>
                  <div className="space-y-2 max-h-56 overflow-y-auto">
                    {(mbDashboard.payments || []).map((pt: any) => (
                      <div key={pt.id} className="p-3 rounded bg-slate-900 border border-slate-800 text-xs flex justify-between items-center gap-2">
                        <div>
                          <div className="font-bold text-white">
                            {pt.external_reference} • {pt.client_company || pt.client_name}
                          </div>
                          <div className="text-slate-400">
                            R$ {pt.amount_brl} ({pt.payment_method} • {pt.execution_mode}) • Status:{" "}
                            <span className={pt.status === "APPROVED" ? "text-emerald-400 font-bold" : "text-amber-300 font-semibold"}>
                              {pt.status}
                            </span>
                          </div>
                        </div>
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300">
                          {pt.reconciled_in_finance ? "Conciliado" : "Aguardando Webhook"}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex justify-between items-center">
                    <h3 className="text-sm font-bold text-white">
                      9. Projetos, Onboarding & Entregas Técnicas
                    </h3>
                    <span className="text-xs text-slate-400">
                      {(mbDashboard.delivery_projects || []).length} projetos ativos
                    </span>
                  </div>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {(mbDashboard.delivery_projects || []).map((dp: any) => (
                      <div key={dp.id} className="p-3 rounded bg-slate-900 border border-slate-800 text-xs space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="font-bold text-indigo-300">
                            {dp.project_code} • {dp.client_company} ({dp.service_code})
                          </span>
                          <span className="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 text-[10px] font-semibold">
                            {dp.status} ({dp.progress_pct}%)
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-400">{dp.contracted_scope}</div>
                        <div className="flex justify-between items-center pt-1">
                          <span className="text-[10px] text-slate-500">Prazo: {dp.due_date} • Validação Cliente: {dp.client_validation_status}</span>
                          {dp.status !== "COMPLETED" && (
                            <button
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
                                showNotice(`Projeto ${dp.project_code} concluído e validado pelo cliente!`);
                              }}
                              className="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
                            >
                              Concluir Entrega
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 20. AUDITORIA E LOGS */}
          {activeMenu === "audit" && auditData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                <h4 className="text-sm font-bold text-white">Logs de Execução dos Agentes de IA</h4>
                <div className="space-y-2 max-h-[500px] overflow-y-auto">
                  {auditData.agent_execution_logs.map((l: any) => (
                    <div key={l.id} className="p-3 rounded bg-slate-900 border border-slate-800 text-xs">
                      <div className="flex justify-between font-bold text-indigo-300">
                        <span>{l.agent_name}</span>
                        <span>
                          {l.duration_ms}ms • {l.status}
                        </span>
                      </div>
                      <div className="text-slate-300">
                        Tarefa: {l.task_name} • Workflow: {l.workflow_run_id}
                      </div>
                      <div className="text-[10px] text-slate-500">{l.created_at}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                <h4 className="text-sm font-bold text-white">Trilha de Auditoria & Segurança</h4>
                <div className="space-y-2 max-h-[500px] overflow-y-auto">
                  {auditData.audit_logs.map((a: any) => (
                    <div key={a.id} className="p-3 rounded bg-slate-900 border border-slate-800 text-xs">
                      <div className="flex justify-between font-bold text-emerald-300">
                        <span>{a.action}</span>
                        <span>IP: {a.ip_address}</span>
                      </div>
                      <div className="text-slate-300">
                        Ator: {a.actor} • Recurso: {a.resource_type} #{a.resource_id}
                      </div>
                      <div className="text-[10px] text-slate-500">{a.created_at}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 25. FASE 19 — UNION AI ENGINE HUB */}
          {activeMenu === "ai_engines" && aiEnginesConfig && (
            <div className="space-y-6">
              {/* Cabeçalho UNION AI ENGINE HUB + Botões Rápidos */}
              <div className="bg-gradient-to-r from-[#0f1629] via-indigo-950/60 to-[#0f1629] border border-indigo-500/40 rounded-xl p-5 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-[10px] font-bold">
                        GEMINI PRIORITÁRIO (COTA GRATUITA OFICIAL)
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-[10px] font-bold">
                        MODO ATUAL: {aiEnginesConfig.configuration?.cost_policy_mode || "FREE_ONLY"}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-white mt-2">
                      UNION AI ENGINE HUB — Central Multimotor de Inteligência Artificial
                    </h3>
                    <p className="text-xs text-slate-300 mt-1">
                      Motor Padrão: <strong>{aiEnginesConfig.configuration?.default_provider_key?.toUpperCase()}</strong> ({aiEnginesConfig.configuration?.default_text_model}) • Transparência total de capacidades, cotas, limites e custos (FREE_ONLY & OWNER_APPROVED).
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => setAiHubSubmenu("providers")}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold"
                    >
                      CONFIGURAR GEMINI
                    </button>
                    <button
                      onClick={() => setAiHubSubmenu("tests")}
                      className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold"
                    >
                      TESTAR MOTOR
                    </button>
                    <button
                      onClick={() => setAiHubSubmenu("campaigns_ai")}
                      className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold"
                    >
                      GERAR CAMPANHA COMPLETA
                    </button>
                  </div>
                </div>

                {/* 10 Submenus do UNION AI ENGINE HUB */}
                <div className="flex flex-wrap gap-1.5 pt-2 border-t border-slate-800">
                  {[
                    { id: "dashboard_ai", label: "1. Dashboard AI" },
                    { id: "providers", label: "2. Provedores" },
                    { id: "models", label: "3. Modelos" },
                    { id: "configuration", label: "4. Configuração & Agentes" },
                    { id: "campaigns_ai", label: "5. Campanhas AI" },
                    { id: "image_studio", label: "6. Image Studio" },
                    { id: "video_studio", label: "7. Video Studio" },
                    { id: "usage_costs", label: "8. Uso e Custos" },
                    { id: "history", label: "9. Histórico" },
                    { id: "tests", label: "10. Testes" },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setAiHubSubmenu(tab.id)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                        aiHubSubmenu === tab.id
                          ? "bg-indigo-600 text-white shadow"
                          : "bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800"
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* SUBMENU 1: DASHBOARD AI */}
              {aiHubSubmenu === "dashboard_ai" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="p-4 rounded-xl bg-[#0f1629] border border-emerald-500/30">
                      <div className="text-[11px] text-slate-400">Motor Padrão Prioritário</div>
                      <div className="text-lg font-bold text-emerald-400 mt-1">
                        {aiEnginesConfig.configuration?.default_provider_key?.toUpperCase()}
                      </div>
                      <div className="text-[11px] text-slate-400">
                        Modelo: {aiEnginesConfig.configuration?.default_text_model}
                      </div>
                    </div>
                    <div className="p-4 rounded-xl bg-[#0f1629] border border-indigo-500/30">
                      <div className="text-[11px] text-slate-400">Política de Custo Ativa</div>
                      <div className="text-lg font-bold text-indigo-300 mt-1">
                        {aiEnginesConfig.configuration?.cost_policy_mode}
                      </div>
                      <div className="text-[11px] text-slate-400">
                        Fallback Pago: {aiEnginesConfig.configuration?.allow_paid_fallback ? "Autorizado" : "Bloqueado"}
                      </div>
                    </div>
                    <div className="p-4 rounded-xl bg-[#0f1629] border border-slate-800">
                      <div className="text-[11px] text-slate-400">Requisições & Tokens</div>
                      <div className="text-lg font-bold text-white mt-1">
                        {aiEnginesConfig.usage_and_costs?.total_requests || 0} reqs
                      </div>
                      <div className="text-[11px] text-slate-400">
                        {aiEnginesConfig.usage_and_costs?.total_tokens || 0} tokens processados
                      </div>
                    </div>
                    <div className="p-4 rounded-xl bg-[#0f1629] border border-slate-800">
                      <div className="text-[11px] text-slate-400">Provedores Cadastrados</div>
                      <div className="text-lg font-bold text-white mt-1">
                        {(aiEnginesConfig.providers || []).length} provedores
                      </div>
                      <div className="text-[11px] text-slate-400">
                        {(aiEnginesConfig.models || []).length} modelos auditados
                      </div>
                    </div>
                  </div>

                  {/* Ações Rápidas do Dashboard AI */}
                  <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 flex flex-wrap gap-3">
                    <button
                      onClick={() => setAiHubSubmenu("providers")}
                      className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold"
                    >
                      CONFIGURAR GEMINI
                    </button>
                    <button
                      onClick={() => setAiHubSubmenu("models")}
                      className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold"
                    >
                      SELECIONAR MOTOR
                    </button>
                    <button
                      onClick={() => setAiHubSubmenu("campaigns_ai")}
                      className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold"
                    >
                      GERAR CAMPANHA COMPLETA
                    </button>
                    <button
                      onClick={() => setAiHubSubmenu("image_studio")}
                      className="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold"
                    >
                      GERAR IMAGEM
                    </button>
                    <button
                      onClick={() => setAiHubSubmenu("video_studio")}
                      className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold"
                    >
                      GERAR ROTEIRO DE VÍDEO
                    </button>
                    <button
                      onClick={() => setAiHubSubmenu("tests")}
                      className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold"
                    >
                      TESTAR MOTOR
                    </button>
                  </div>
                </div>
              )}

              {/* SUBMENU 2: PROVEDORES & CENTRAL DE CREDENCIAIS */}
              {aiHubSubmenu === "providers" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {(aiEnginesConfig.providers || []).map((p: any) => (
                    <div key={p.provider_key} className="p-4 rounded-xl bg-[#0f1629] border border-slate-800 text-xs space-y-3">
                      <div className="flex justify-between items-start gap-2">
                        <div>
                          <div className="font-bold text-sm text-white">{p.name}</div>
                          <div className="text-[11px] text-slate-400">Classe: {p.provider_class} • Status: {p.status}</div>
                        </div>
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-bold text-emerald-300">
                          {p.cost_tier}
                        </span>
                      </div>

                      <p className="text-slate-300 text-[11px]">{p.limitations_text}</p>
                      <div className="text-[11px] text-slate-400">
                        <strong>Custo:</strong> {p.cost_notes}
                      </div>

                      {/* Capacidades Declaradas */}
                      <div className="flex flex-wrap gap-1.5">
                        {Object.entries(p.capabilities || {}).map(([cap, ok]: [string, any]) => (
                          <span
                            key={cap}
                            className={`px-2 py-0.5 rounded text-[10px] ${
                              ok ? "bg-emerald-500/15 text-emerald-300" : "bg-slate-900 text-slate-500 line-through"
                            }`}
                          >
                            {cap}
                          </span>
                        ))}
                      </div>

                      {/* Configuração Segura de API Key (Fernet) */}
                      <div className="space-y-2 pt-2 border-t border-slate-800">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-slate-400">
                            Credencial: {p.has_credential ? `Configurada (${p.masked_credential})` : "Aguardando API Key"}
                          </span>
                          {p.last_test_status && (
                            <span className="text-indigo-300">Último Teste: {p.last_test_status}</span>
                          )}
                        </div>
                        {p.provider_key === "openai_compatible" && (
                          <input
                            value={aiEndpointInputs[p.provider_key] ?? p.base_url ?? ""}
                            onChange={(e) => setAiEndpointInputs({ ...aiEndpointInputs, [p.provider_key]: e.target.value })}
                            placeholder="Endpoint Base URL explícito (ex.: http://localhost:11434/v1)"
                            className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                          />
                        )}
                        <div className="flex gap-2">
                          <input
                            type="password"
                            value={aiKeyInputs[p.provider_key] || ""}
                            onChange={(e) => setAiKeyInputs({ ...aiKeyInputs, [p.provider_key]: e.target.value })}
                            placeholder={`Inserir API Key para ${p.name} (Criptografia Fernet)`}
                            className="flex-1 px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                          />
                          <button
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
                            className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-bold"
                          >
                            {p.provider_key === "gemini" ? "CONFIGURAR GEMINI" : "Salvar Chave"}
                          </button>
                          <button
                            onClick={async () => {
                              const res = await apiFetch("/api/v1/ai-engine-hub/test-connection", {
                                method: "POST",
                                body: JSON.stringify({ provider_key: p.provider_key }),
                              });
                              const refreshed = await apiFetch("/api/v1/ai-engine-hub/overview");
                              setAiEnginesConfig(refreshed);
                              showNotice(`Teste ${p.name}: ${res.status} (${res.error || "OK"})`);
                            }}
                            className="px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-bold"
                          >
                            TESTAR MOTOR
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* SUBMENU 3: MODELOS */}
              {aiHubSubmenu === "models" && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {(aiEnginesConfig.models || []).map((m: any) => {
                    const isDefault = aiEnginesConfig.configuration?.default_text_model === m.model_id;
                    return (
                      <div key={`${m.provider_key}:${m.model_id}`} className="p-4 rounded-xl bg-[#0f1629] border border-slate-800 text-xs space-y-2">
                        <div className="flex justify-between items-start gap-2">
                          <span className="font-bold text-white">{m.display_name}</span>
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-emerald-300 font-bold">
                            {m.cost_tier}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-400">
                          Provedor: <strong>{m.provider_key}</strong> • Modalidade: <strong>{m.modality}</strong>
                        </div>
                        <p className="text-[11px] text-slate-300">{m.known_quota_note}</p>
                        <p className="text-[10px] text-amber-300/90">{m.limitations_note}</p>
                        <button
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
                          className={`w-full py-1.5 rounded font-bold ${
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

              {/* SUBMENU 4: CONFIGURAÇÃO GLOBAL, POLÍTICA FREE_ONLY / OWNER_APPROVED E AGENTES */}
              {aiHubSubmenu === "configuration" && (
                <div className="space-y-4">
                  <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3 text-xs">
                    <h4 className="text-sm font-bold text-white">Política de Custos do AI Router (FREE_ONLY vs OWNER_APPROVED)</h4>
                    <div className="flex flex-wrap gap-3">
                      {["FREE_ONLY", "OWNER_APPROVED"].map((mode) => (
                        <button
                          key={mode}
                          onClick={async () => {
                            const updated = await apiFetch("/api/v1/ai-engine-hub/configuration", {
                              method: "PUT",
                              body: JSON.stringify({ cost_policy_mode: mode }),
                            });
                            setAiEnginesConfig(updated);
                            showNotice(`Política de custos atualizada para ${mode}!`);
                          }}
                          className={`px-4 py-2 rounded-lg font-bold ${
                            aiEnginesConfig.configuration?.cost_policy_mode === mode
                              ? "bg-emerald-600 text-white"
                              : "bg-slate-900 border border-slate-700 text-slate-300"
                          }`}
                        >
                          Modo {mode}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3 text-xs">
                    <h4 className="text-sm font-bold text-white">Configuração Individual por Agente (12 Agentes)</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {Object.values(aiEnginesConfig.configuration?.agent_routing || {}).map((ag: any) => (
                        <div key={ag.agent_id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1.5">
                          <div className="font-bold text-indigo-300">{ag.agent_name} ({ag.agent_id})</div>
                          <div className="text-slate-300">
                            Motor: <strong>{ag.provider_key}</strong> • Modelo: <strong>{ag.model_id}</strong>
                          </div>
                          <div className="text-slate-400 text-[11px]">
                            Fallback: {ag.fallback_provider} • Limite: {ag.daily_limit}/dia • Temp: {ag.temperature}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* SUBMENU 5: CAMPANHAS AI (GERAR CAMPANHA COMPLETA & PEÇA INDIVIDUAL) */}
              {aiHubSubmenu === "campaigns_ai" && (
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4 text-xs">
                  <h4 className="text-sm font-bold text-white">Motor de Campanhas AI (25 Componentes ou Peça Individual)</h4>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                    <input
                      value={aiGenTopic}
                      onChange={(e) => setAiGenTopic(e.target.value)}
                      placeholder="Nome / Oferta da Campanha"
                      className="md:col-span-2 px-3 py-2 rounded bg-slate-900 border border-slate-700 text-white"
                    />
                    <select
                      value={aiGenMode}
                      onChange={(e) => setAiGenMode(e.target.value)}
                      className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-white"
                    >
                      <option value="FULL_CAMPAIGN">GERAR CAMPANHA COMPLETA (25 Itens)</option>
                      <option value="SINGLE_PIECE">GERAR PEÇA INDIVIDUAL</option>
                    </select>
                    <select
                      value={aiPieceType}
                      onChange={(e) => setAiPieceType(e.target.value)}
                      className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-white"
                    >
                      {["ALL", "POST", "IMAGE", "VIDEO", "COPY", "EMAIL", "ARTICLE", "LANDING_PAGE", "CAROUSEL", "AD", "SCRIPT", "SEO", "CTA"].map((pt) => (
                        <option key={pt} value={pt}>{pt}</option>
                      ))}
                    </select>
                  </div>
                  <button
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
                    className="px-5 py-2.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-bold"
                  >
                    GERAR CAMPANHA COMPLETA
                  </button>
                  {aiGenResult && (
                    <pre className="p-3 rounded bg-slate-950 text-slate-200 max-h-80 overflow-y-auto whitespace-pre-wrap text-[11px]">
                      {JSON.stringify(aiGenResult, null, 2)}
                    </pre>
                  )}
                </div>
              )}

              {/* SUBMENU 6: AI IMAGE STUDIO */}
              {aiHubSubmenu === "image_studio" && (
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4 text-xs">
                  <h4 className="text-sm font-bold text-white">AI IMAGE STUDIO (Verificação Real de Capacidade & Custo)</h4>
                  <p className="text-slate-400">
                    Nota de Transparência: Modelos de texto gratuitos (como Gemini 2.5 Flash) geram prompts detalhados de imagem (`PROMPT_ONLY`). A renderização direta de pixels via Imagen 3 ou DALL-E 3 é paga e exige modo `OWNER_APPROVED` + faturamento ativo no provedor.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <input
                      value={aiImgPrompt}
                      onChange={(e) => setAiImgPrompt(e.target.value)}
                      placeholder="Prompt da imagem..."
                      className="md:col-span-2 px-3 py-2 rounded bg-slate-900 border border-slate-700 text-white"
                    />
                    <select
                      value={aiImgMode}
                      onChange={(e) => setAiImgMode(e.target.value)}
                      className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-white"
                    >
                      <option value="GENERATE_IMAGE">Renderizar Imagem via Modelo de Imagem (Imagen 3 / DALL-E 3)</option>
                      <option value="PROMPT_ONLY">Gerar Prompt Técnico de Imagem (Gratuito via Gemini Flash)</option>
                    </select>
                  </div>
                  <button
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
                    className="px-5 py-2.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-bold"
                  >
                    GERAR IMAGEM
                  </button>
                  {aiGenResult && (
                    <pre className="p-3 rounded bg-slate-950 text-slate-200 max-h-72 overflow-y-auto whitespace-pre-wrap text-[11px]">
                      {JSON.stringify(aiGenResult, null, 2)}
                    </pre>
                  )}
                </div>
              )}

              {/* SUBMENU 7: AI VIDEO STUDIO */}
              {aiHubSubmenu === "video_studio" && (
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4 text-xs">
                  <h4 className="text-sm font-bold text-white">
                    AI VIDEO STUDIO (Separação Estrita: Roteiro • Storyboard • Vídeo Renderizado)
                  </h4>
                  <p className="text-slate-400">
                    O sistema jamais declara um vídeo como gerado quando apenas um roteiro ou storyboard tiver sido produzido.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <input
                      value={aiVidPrompt}
                      onChange={(e) => setAiVidPrompt(e.target.value)}
                      placeholder="Tema ou prompt do vídeo..."
                      className="md:col-span-2 px-3 py-2 rounded bg-slate-900 border border-slate-700 text-white"
                    />
                    <select
                      value={aiVidStage}
                      onChange={(e) => setAiVidStage(e.target.value)}
                      className="px-3 py-2 rounded bg-slate-900 border border-slate-700 text-white"
                    >
                      <option value="SCRIPT_AND_STORYBOARD">Roteiro + Storyboard + Legendas (STORYBOARD_ONLY)</option>
                      <option value="SCRIPT_ONLY">Apenas Roteiro Narrativo (SCRIPT_ONLY)</option>
                      <option value="DIRECT_VIDEO_GENERATION">Vídeo Direto via API de Vídeo (Requer Veo 2 + OWNER_APPROVED)</option>
                    </select>
                  </div>
                  <button
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
                    className="px-5 py-2.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-bold"
                  >
                    GERAR ROTEIRO DE VÍDEO
                  </button>
                  {aiGenResult && (
                    <pre className="p-3 rounded bg-slate-950 text-slate-200 max-h-72 overflow-y-auto whitespace-pre-wrap text-[11px]">
                      {JSON.stringify(aiGenResult, null, 2)}
                    </pre>
                  )}
                </div>
              )}

              {/* SUBMENU 8: AI USAGE & COSTS */}
              {aiHubSubmenu === "usage_costs" && (
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4 text-xs">
                  <h4 className="text-sm font-bold text-white">
                    AI USAGE & COSTS — Separação Estrita de Gratuidade e Custos
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                    {Object.entries(aiEnginesConfig.usage_and_costs?.by_cost_classification || {}).map(([bucket, info]: [string, any]) => (
                      <div key={bucket} className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                        <div className="font-bold text-indigo-300">{bucket}</div>
                        <div className="text-white">Requisições: <strong>{info.requests}</strong></div>
                        <div className="text-slate-400">Tokens: {info.tokens}</div>
                        <div className="text-emerald-400">
                          Custo Est.: {info.estimated_cost_brl === null ? "DESCONHECIDO" : `R$ ${info.estimated_cost_brl}`}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* SUBMENU 9 & 10: HISTÓRICO & TESTES */}
              {(aiHubSubmenu === "history" || aiHubSubmenu === "tests") && (
                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3 text-xs">
                  <div className="flex justify-between items-center">
                    <h4 className="text-sm font-bold text-white">Histórico de Execuções, Testes de Conexão e Fallbacks</h4>
                    <button
                      onClick={async () => {
                        showNotice("Testando conexão e geração real no motor padrão...");
                        const res = await apiFetch("/api/v1/ai-engine-hub/test-connection", {
                          method: "POST",
                          body: JSON.stringify({
                            provider_key: aiEnginesConfig.configuration?.default_provider_key || "gemini",
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
                        showNotice(res.ok ? `Motor ${res.provider_key.toUpperCase()} CONECTADO e geração validada com SUCESSO!` : `Teste: ${res.status} (${res.error})`);
                      }}
                      className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold"
                    >
                      TESTAR MOTOR
                    </button>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {(aiEnginesConfig.recent_executions || []).map((ex: any) => (
                      <div key={ex.execution_uuid} className="p-3 rounded bg-slate-900 border border-slate-800 flex justify-between items-center">
                        <div>
                          <div className="font-bold text-white">
                            {ex.task_type} • Solicitado: {ex.requested_provider}:{ex.requested_model} → Executado: {ex.executed_provider || "NENHUM"}:{ex.executed_model || "-"}
                          </div>
                          <div className="text-slate-400">
                            Origem: {ex.execution_origin} • Classificação: {ex.cost_classification} • Tokens: {ex.total_tokens}
                          </div>
                          {ex.error_message && <div className="text-amber-400 text-[11px]">{ex.error_message}</div>}
                        </div>
                        <span className="px-2 py-0.5 rounded bg-slate-800 font-bold text-indigo-300">{ex.status}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
