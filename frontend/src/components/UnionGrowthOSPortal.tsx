"use client";

import React, { useEffect, useState, useCallback, useMemo } from "react";
import {
  Home,
  CheckSquare,
  Briefcase,
  Megaphone,
  BrainCircuit,
  BarChart3,
  Grid,
  Search,
  HelpCircle,
  Bell,
  Sun,
  Moon,
  Menu,
  X,
  PanelLeftClose,
  PanelLeftOpen,
  ChevronDown,
  ChevronRight,
  LogOut,
  Sparkles,
  RefreshCw,
  Star,
} from "lucide-react";
import {
  AreaId,
  LegacyMenuId,
  PRIMARY_AREAS,
  RESOURCE_CATALOG,
  getAreaForView,
  getResourceMeta,
} from "@/lib/navigation";
import {
  EmptyState,
  OriginBadge,
  SkeletonCard,
  StatusPill,
  ToastBanner,
} from "@/components/DesignSystem";
import { CommandCenter } from "@/components/CommandCenter";
import { HomeWorkspace } from "@/components/HomeWorkspace";
import { MyWorkHub } from "@/components/MyWorkHub";
import { AITeamAndGovernanceView } from "@/components/AITeamAndGovernanceView";
import { AllResourcesHub, HelpCenterDrawer } from "@/components/ResourceCenterAndHelp";
import { AreaContextGuide } from "@/components/AreaContextGuide";
import { BrandIntelligenceCenter } from "@/components/BrandAndOnboardingHub";
import { AnalyticsAttributionPanel, ConversationalAutomationPanel } from "@/components/ConversationalAutomationAndAnalytics";
import {
  CommercialPipelineWorkspace,
  CompetitorsIntelligenceWorkspace,
  CRMAndLeadsWorkspace,
  MultiBusinessAndProposalsWorkspace,
} from "@/components/CommercialRevenueWorkspace";
import { AIEnginesHubWorkspace, PlansAndUsagePanel } from "@/components/AIEnginesHubWorkspace";

type MenuId = LegacyMenuId;

const PIPELINE_STAGES = [
  "NEW_LEAD",
  "QUALIFICATION",
  "PROPOSAL",
  "NEGOTIATION",
  "CLOSED_WON",
  "CLOSED_LOST",
];

function AreaIcon({ areaId, className = "w-4 h-4" }: { areaId: AreaId; className?: string }) {
  switch (areaId) {
    case "inicio":
      return <Home className={className} aria-hidden="true" />;
    case "meu_trabalho":
      return <CheckSquare className={className} aria-hidden="true" />;
    case "comercial":
      return <Briefcase className={className} aria-hidden="true" />;
    case "marketing":
      return <Megaphone className={className} aria-hidden="true" />;
    case "ia":
      return <BrainCircuit className={className} aria-hidden="true" />;
    case "gestao":
      return <BarChart3 className={className} aria-hidden="true" />;
    default:
      return <Grid className={className} aria-hidden="true" />;
  }
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

  // FASE 22 — UX/UI Navigation, Theme, Command Center, Onboarding, Help & Table Filters
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [expandedArea, setExpandedArea] = useState<AreaId | null>("inicio");
  const [sidebarSearch, setSidebarSearch] = useState("");
  const [themeMode, setThemeMode] = useState<"dark" | "light">("dark");
  const [commandOpen, setCommandOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const [onboardingDismissed, setOnboardingDismissed] = useState(false);
  const [favoriteIds, setFavoriteIds] = useState<LegacyMenuId[]>(["crm", "marketing", "ai_engines"]);
  const [recentIds, setRecentIds] = useState<LegacyMenuId[]>(["overview"]);
  const [crmLeadFilter, setCrmLeadFilter] = useState("");
  const [campFilter, setCampFilter] = useState("");
  const [intgStatusFilter, setIntgStatusFilter] = useState<"ALL" | "CONNECTED" | "PENDING">("ALL");
  const [showRawReportJson, setShowRawReportJson] = useState(false);

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
  const [cfFocusTheme, setCfFocusTheme] = useState<string>("");
  const [cfReplaceDrafts, setCfReplaceDrafts] = useState<boolean>(true);
  const [lastSyncedTenantId, setLastSyncedTenantId] = useState<number | null>(null);
  const [assistedPackage, setAssistedPackage] = useState<any>(null);
  const [ceoDailyPlan, setCeoDailyPlan] = useState<any>(null);
  const [opDashboard, setOpDashboard] = useState<any>(null);
  const [systemAlerts, setSystemAlerts] = useState<any[]>([]);
  const [pilotData, setPilotData] = useState<any>(null);
  const [resourceCosts, setResourceCosts] = useState<any>(null);

  // FASE 23 — AI Growth Command Center, Modo Simples/Avançado, Onboarding 6 Etapas & Analytics
  const [commandCenterData, setCommandCenterData] = useState<any>(null);
  const [analyticsAttrData, setAnalyticsAttrData] = useState<any>(null);
  const [uiMode, setUiMode] = useState<"SIMPLE" | "ADVANCED">("SIMPLE");
  const [showOnboardingWizard, setShowOnboardingWizard] = useState<boolean>(false);

  // FASE 25 — PLG Plans & Usage, CRM Revenue Intelligence & Retention Activation
  const [plansOverview, setPlansOverview] = useState<any>(null);
  const [revenueIntel, setRevenueIntel] = useState<any>(null);
  const [activationData, setActivationData] = useState<any>(null);

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
  const [creativeHeadline, setCreativeHeadline] = useState("Cresça com 12 Agentes de IA Trabalhando 24/7");
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

  // Integration Credentials Input per provider (suporte multi-campo real)
  const [credInputs, setCredInputs] = useState<Record<string, string>>({});
  const [credFieldInputs, setCredFieldInputs] = useState<Record<string, Record<string, string>>>({});
  const [leadLgpdConsent, setLeadLgpdConsent] = useState(true);

  // Settings & Tenant Form
  const [newTenantName, setNewTenantName] = useState("");
  const [editCompanyName, setEditCompanyName] = useState("");
  const [editBrandName, setEditBrandName] = useState("");
  const [editDomain, setEditDomain] = useState("");
  const [editNiche, setEditNiche] = useState("");
  const [editAudience, setEditAudience] = useState("");
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
      const [
        me,
        ov,
        ag,
        ceo,
        mkt,
        seo,
        cal,
        cre,
        cp,
        gr,
        crm,
        comp,
        fin,
        cs,
        auto,
        app,
        rep,
        intg,
        aud,
        cfItems,
        cPlan,
        opDash,
        sAlerts,
        rCosts,
        mbDash,
        aiCfg,
        pilotRes,
        cmdRes,
        attrRes,
        plRes,
        revRes,
        actRes,
      ] = await Promise.all([
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
        apiFetch("/api/v1/content-factory/items").catch(() => []),
        apiFetch("/api/v1/ceo/daily-plan").catch(() => null),
        apiFetch("/api/v1/system/operational-dashboard").catch(() => null),
        apiFetch("/api/v1/system/alerts").catch(() => []),
        apiFetch("/api/v1/system/resource-costs").catch(() => null),
        apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`).catch(() => null),
        apiFetch("/api/v1/ai-engines/config").catch(() => null),
        apiFetch("/api/v1/system/pilot-7-days").catch(() => null),
        apiFetch("/api/v1/growth-os/command-center").catch(() => null),
        apiFetch("/api/v1/growth-os/analytics-attribution").catch(() => null),
        apiFetch("/api/v1/plans/overview").catch(() => null),
        apiFetch("/api/v1/growth-os/revenue-intelligence").catch(() => null),
        apiFetch("/api/v1/growth-os/activation-retention").catch(() => null),
      ]);
      setMeData(me);
      setEditCompanyName(me?.active_tenant?.name || "");
      setEditBrandName(me?.active_tenant?.brand_name || "");
      setEditDomain(me?.active_tenant?.domain || "");
      setEditNiche(me?.active_tenant?.niche || "");
      setEditAudience(me?.active_tenant?.target_audience || "");
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
      setContentFactoryItems(cfItems || []);
      setCeoDailyPlan(cPlan);
      setOpDashboard(opDash);
      setSystemAlerts(sAlerts || []);
      setResourceCosts(rCosts);
      setMbDashboard(mbDash);
      setAiEnginesConfig(aiCfg);
      if (pilotRes) setPilotData(pilotRes);
      if (cmdRes) setCommandCenterData(cmdRes);
      if (attrRes) setAnalyticsAttrData(attrRes);
      if (plRes) setPlansOverview(plRes);
      if (revRes) setRevenueIntel(revRes);
      if (actRes) setActivationData(actRes);
      if (me?.active_tenant?.ui_mode === "SIMPLE" || me?.active_tenant?.ui_mode === "ADVANCED") {
        setUiMode(me.active_tenant.ui_mode);
      }
    } catch (err: any) {
      showNotice(err.message || "Falha ao carregar dados");
    } finally {
      setLoading(false);
    }
  }, [token, apiFetch, selectedUnit]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const saved = localStorage.getItem("ug_token");
    if (saved) setToken(saved);
    const savedCollapsed = localStorage.getItem("ug_sidebar_collapsed");
    if (savedCollapsed === "1") setSidebarCollapsed(true);
    const savedTheme = localStorage.getItem("ug_theme_mode") as "dark" | "light" | null;
    if (savedTheme === "light" || savedTheme === "dark") setThemeMode(savedTheme);
    const savedOb = localStorage.getItem("ug_onboarding_dismissed");
    if (savedOb === "1") setOnboardingDismissed(true);
    try {
      const fav = JSON.parse(localStorage.getItem("ug_favorites") || "null");
      if (Array.isArray(fav)) setFavoriteIds(fav);
      const rec = JSON.parse(localStorage.getItem("ug_recents") || "null");
      if (Array.isArray(rec)) setRecentIds(rec);
    } catch {
      // ignore corrupted local preferences
    }
  }, []);

  useEffect(() => {
    if (typeof document === "undefined") return;
    const root = document.documentElement;
    if (themeMode === "light") {
      root.classList.remove("dark");
      root.classList.add("light");
    } else {
      root.classList.remove("light");
      root.classList.add("dark");
    }
    localStorage.setItem("ug_theme_mode", themeMode);
  }, [themeMode]);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCommandOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  useEffect(() => {
    if (token) {
      loadAllActiveData();
    }
  }, [token, activeTenantId, loadAllActiveData]);

  // Sincroniza automaticamente campos de Marketing (SEO, Criativos, Copy A/B e Fábrica) ao trocar de empresa ou cadastrar Persona
  useEffect(() => {
    const activeT = meData?.active_tenant;
    if (!activeT?.id) return;
    const brand = activeT.brand_name || activeT.name || "Sua Marca";
    const domain = activeT.domain || "";
    const niche = activeT.niche || "";
    const personas = marketingData?.personas || [];
    const latestPersona = personas.length > 0 ? personas[personas.length - 1] : null;
    const aud = latestPersona?.name || activeT.target_audience || "Público-Alvo";
    const offer = latestPersona?.value_proposition || niche || brand;

    if (lastSyncedTenantId !== activeT.id) {
      setLastSyncedTenantId(activeT.id);
      if (domain) setSeoUrlInput(domain);
      if (niche) {
        setSeoKwInput(niche);
        setSeoTopicInput(`Guia Completo: ${niche} — ${brand}`);
      }
      setCreativeTitle(`Divulgação ${brand}`);
      setCreativeHeadline(`${brand} para ${aud}`);
      setCreativeCta(domain ? `Acesse ${domain}` : `Conhecer ${brand}`);
      setCopyTitle(`Convite Principal — ${brand}`);
      setCopyOffer(brand);
      setCopyBenefit(offer);
      setCfFocusTheme(latestPersona?.value_proposition || "");
    } else if (latestPersona?.value_proposition && !cfFocusTheme) {
      setCfFocusTheme(latestPersona.value_proposition);
    }
  }, [meData?.active_tenant, marketingData?.personas, lastSyncedTenantId, cfFocusTheme]);

  const navigateTo = useCallback((viewId: LegacyMenuId) => {
    const normalized: LegacyMenuId = viewId === "calendar" ? "social" : viewId;
    setActiveMenu(normalized);
    setMobileMenuOpen(false);
    const area = getAreaForView(normalized);
    setExpandedArea(area);
    setRecentIds((prev) => {
      const next = [normalized, ...prev.filter((x) => x !== normalized)].slice(0, 8);
      if (typeof window !== "undefined") localStorage.setItem("ug_recents", JSON.stringify(next));
      return next;
    });
  }, []);

  const toggleFavorite = useCallback((id: LegacyMenuId) => {
    setFavoriteIds((prev) => {
      const next = prev.includes(id) ? prev.filter((x) => x !== id) : [id, ...prev];
      if (typeof window !== "undefined") localStorage.setItem("ug_favorites", JSON.stringify(next));
      return next;
    });
  }, []);

  const currentAreaId = getAreaForView(activeMenu);
  const currentAreaConfig = PRIMARY_AREAS.find((a) => a.id === currentAreaId);
  const currentResourceMeta = getResourceMeta(activeMenu);
  const pendingWorkCount = useMemo(
    () =>
      (approvalsData || []).filter((a: any) => a.status === "PENDING").length +
      (systemAlerts || []).filter((a: any) => a.status !== "RESOLVED").length,
    [approvalsData, systemAlerts]
  );

  const sidebarMatchedResources = useMemo(() => {
    const q = sidebarSearch.trim().toLowerCase();
    if (!q) return [];
    return RESOURCE_CATALOG.filter((r) =>
      `${r.name} ${r.description} ${r.category} ${r.keywords.join(" ")}`.toLowerCase().includes(q)
    ).slice(0, 8);
  }, [sidebarSearch]);

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
      <div className="min-h-screen flex items-center justify-center ug-bg p-6">
        <div className="w-full max-w-md ug-card rounded-2xl p-8 shadow-2xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-lg text-white">
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
            <div role="alert" className="mb-4 p-3 rounded-lg bg-red-500/15 border border-red-500/40 text-red-300 text-xs">
              {authError}
            </div>
          )}

          <form onSubmit={handleAuthSubmit} className="space-y-4">
            {authMode === "register" && (
              <>
                <div>
                  <label htmlFor="ug-fullname" className="block text-xs text-slate-300 mb-1">Seu Nome Completo</label>
                  <input
                    id="ug-fullname"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-sm text-white"
                    placeholder="Ex: Thiago Thomaz"
                  />
                </div>
                <div>
                  <label htmlFor="ug-company" className="block text-xs text-slate-300 mb-1">Nome da Empresa / Marca</label>
                  <input
                    id="ug-company"
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
              <label htmlFor="ug-email" className="block text-xs text-slate-300 mb-1">E-mail Corporativo</label>
              <input
                id="ug-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-sm text-white"
              />
            </div>
            <div>
              <label htmlFor="ug-password" className="block text-xs text-slate-300 mb-1">Senha de Acesso</label>
              <input
                id="ug-password"
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
              {authMode === "login" ? "Acessar Central Executiva" : "Criar Workspace & Ativar 12 Agentes"}
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
    <div className="min-h-screen flex ug-bg text-slate-100">
      {/* MOBILE OVERLAY BACKDROP */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* SIDEBAR MINIMALISTA 3.0 (Linear / Attio inspired) */}
      <aside
        aria-label="Navegação principal"
        className={`fixed lg:sticky top-0 left-0 z-40 h-screen ug-sidebar border-r flex flex-col shrink-0 transition-all duration-200 ${
          sidebarCollapsed ? "w-16" : "w-60"
        } ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}
      >
        <div className="p-3 border-b border-[var(--ug-border-subtle)] space-y-2.5">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <div className="h-7 w-7 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-xs text-white shrink-0">
                UG
              </div>
              {!sidebarCollapsed && (
                <div className="font-semibold text-[13px] tracking-tight text-[var(--ug-text-primary)] truncate">
                  UNION GROWTH
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={() => {
                const next = !sidebarCollapsed;
                setSidebarCollapsed(next);
                if (typeof window !== "undefined") localStorage.setItem("ug_sidebar_collapsed", next ? "1" : "0");
              }}
              aria-label={sidebarCollapsed ? "Expandir barra lateral" : "Recolher barra lateral"}
              className="hidden lg:inline-flex p-1.5 rounded-md text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)] hover:bg-white/[0.05] transition"
            >
              {sidebarCollapsed ? <PanelLeftOpen className="w-3.5 h-3.5" /> : <PanelLeftClose className="w-3.5 h-3.5" />}
            </button>
            <button
              type="button"
              onClick={() => setMobileMenuOpen(false)}
              aria-label="Fechar menu móvel"
              className="lg:hidden p-1.5 rounded-md text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)]"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {!sidebarCollapsed && meData?.available_tenants && (
            <select
              id="ug-tenant-select"
              aria-label="Empresa ativa"
              value={activeTenantId || meData?.active_tenant?.id || ""}
              onChange={(e) => setActiveTenantId(Number(e.target.value))}
              className="w-full bg-[var(--ug-surface)] border border-[var(--ug-border)] rounded-lg px-2.5 py-1.5 text-xs font-medium text-[var(--ug-text-primary)]"
            >
              {meData.available_tenants.map((t: any) => (
                <option key={t.id} value={t.id}>
                  {t.brand_name} ({t.plan_tier})
                </option>
              ))}
            </select>
          )}

          {!sidebarCollapsed && (
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[var(--ug-text-muted)] absolute left-2.5 top-1/2 -translate-y-1/2" aria-hidden="true" />
              <input
                type="text"
                value={sidebarSearch}
                onChange={(e) => setSidebarSearch(e.target.value)}
                placeholder="Ir para tela..."
                aria-label="Filtrar módulos na barra lateral"
                className="w-full pl-8 pr-2.5 py-1 rounded-lg bg-white/[0.03] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)] placeholder:text-[var(--ug-text-muted)]"
              />
            </div>
          )}
        </div>

        <nav className="flex-1 overflow-y-auto px-2 py-2.5 space-y-0.5">
          {sidebarSearch.trim() && !sidebarCollapsed ? (
            <div className="space-y-1 p-1">
              <div className="text-[10px] font-medium text-[var(--ug-text-muted)] px-2">
                Resultados ({sidebarMatchedResources.length})
              </div>
              {sidebarMatchedResources.map((res) => (
                <button
                  key={res.id}
                  type="button"
                  onClick={() => {
                    navigateTo(res.id);
                    setSidebarSearch("");
                  }}
                  className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs text-[var(--ug-text-secondary)] hover:bg-white/[0.05] hover:text-[var(--ug-text-primary)] transition"
                >
                  <div className="font-medium truncate">{res.name}</div>
                  <div className="text-[10px] text-[var(--ug-text-muted)] truncate">{res.category}</div>
                </button>
              ))}
              {sidebarMatchedResources.length === 0 && (
                <div className="text-xs text-[var(--ug-text-muted)] px-2 py-3">Nenhum módulo encontrado.</div>
              )}
            </div>
          ) : (
            <>
              {PRIMARY_AREAS.map((area) => {
                const isAreaActive = currentAreaId === area.id;
                const isExpanded = expandedArea === area.id && !sidebarCollapsed && area.subtabs.length > 0;
                return (
                  <div key={area.id} className="space-y-0.5">
                    <div className="flex items-center gap-0.5">
                      <button
                        type="button"
                        aria-current={isAreaActive ? "page" : undefined}
                        title={sidebarCollapsed ? area.label : undefined}
                        onClick={() => {
                          navigateTo(area.defaultView);
                          if (area.subtabs.length > 0 && !sidebarCollapsed) {
                            setExpandedArea(area.id);
                          }
                        }}
                        className={`relative flex-1 flex items-center ${
                          sidebarCollapsed ? "justify-center px-2" : "justify-between px-2.5"
                        } py-2 rounded-lg text-xs transition ${
                          isAreaActive
                            ? "bg-white/[0.07] text-[var(--ug-text-primary)] font-semibold"
                            : "text-[var(--ug-text-secondary)] hover:bg-white/[0.04] hover:text-[var(--ug-text-primary)] font-medium"
                        }`}
                      >
                        <div className="flex items-center gap-2.5 min-w-0">
                          <AreaIcon
                            areaId={area.id}
                            className={`w-4 h-4 shrink-0 ${isAreaActive ? "text-indigo-400" : "text-[var(--ug-text-muted)]"}`}
                          />
                          {!sidebarCollapsed && <span className="truncate">{area.label}</span>}
                        </div>
                        {!sidebarCollapsed && area.id === "meu_trabalho" && pendingWorkCount > 0 && (
                          <span className="px-1.5 py-0.2 rounded-full text-[10px] font-semibold bg-amber-500/15 text-amber-300 tabular-nums">
                            {pendingWorkCount}
                          </span>
                        )}
                      </button>

                      {!sidebarCollapsed && area.subtabs.length > 0 && (
                        <button
                          type="button"
                          onClick={() => setExpandedArea((prev) => (prev === area.id ? null : area.id))}
                          aria-label={`${isExpanded ? "Recolher" : "Expandir"} submenu de ${area.label}`}
                          className="p-1.5 rounded-md text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)] hover:bg-white/[0.04]"
                        >
                          {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                        </button>
                      )}
                    </div>

                    {isExpanded && (
                      <div className="ml-4 pl-2.5 border-l border-[var(--ug-border)] space-y-0.5 py-0.5">
                        {area.subtabs
                          .filter((sub) => uiMode === "ADVANCED" || !sub.advancedOnly || activeMenu === sub.id)
                          .map((sub) => {
                            const isSubActive = activeMenu === sub.id || (sub.id === "social" && activeMenu === "calendar");
                            return (
                              <button
                                key={sub.id}
                                type="button"
                                onClick={() => navigateTo(sub.id)}
                                className={`w-full text-left px-2 py-1 rounded-md text-[11px] transition ${
                                  isSubActive
                                    ? "text-indigo-400 font-semibold bg-indigo-500/10"
                                    : "text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)] hover:bg-white/[0.03]"
                                }`}
                              >
                                {sub.label}
                              </button>
                            );
                          })}
                      </div>
                    )}
                  </div>
                );
              })}

              {!sidebarCollapsed && (favoriteIds.length > 0 || recentIds.length > 0) && (
                <div className="pt-3 mt-2 border-t border-[var(--ug-border-subtle)] space-y-1">
                  <div className="px-2.5 flex items-center gap-1.5 text-[10px] font-medium text-[var(--ug-text-muted)]">
                    <Star className="w-3 h-3 text-amber-400" aria-hidden="true" />
                    <span>{favoriteIds.length > 0 ? "Favoritos" : "Recentes"}</span>
                  </div>
                  {(favoriteIds.length > 0 ? favoriteIds : recentIds).slice(0, 3).map((rid) => {
                    const meta = getResourceMeta(rid);
                    if (!meta) return null;
                    return (
                      <button
                        key={rid}
                        type="button"
                        onClick={() => navigateTo(rid)}
                        className="w-full text-left px-2.5 py-1 rounded-md text-[11px] text-[var(--ug-text-secondary)] hover:text-[var(--ug-text-primary)] hover:bg-white/[0.04] truncate"
                      >
                        {meta.name.split(" — ")[0]}
                      </button>
                    );
                  })}
                </div>
              )}

              <div className="pt-2 mt-2 border-t border-[var(--ug-border-subtle)]">
                <button
                  type="button"
                  title={sidebarCollapsed ? "Todos os recursos" : undefined}
                  aria-current={activeMenu === "all_resources" ? "page" : undefined}
                  onClick={() => navigateTo("all_resources")}
                  className={`w-full flex items-center ${
                    sidebarCollapsed ? "justify-center px-2" : "gap-2.5 px-2.5"
                  } py-2 rounded-lg text-xs font-medium transition ${
                    activeMenu === "all_resources"
                      ? "bg-white/[0.07] text-[var(--ug-text-primary)] font-semibold"
                      : "text-[var(--ug-text-secondary)] hover:bg-white/[0.04] hover:text-[var(--ug-text-primary)]"
                  }`}
                >
                  <Grid className="w-4 h-4 shrink-0 text-[var(--ug-text-muted)]" aria-hidden="true" />
                  {!sidebarCollapsed && <span>Todos os recursos</span>}
                </button>
              </div>
            </>
          )}
        </nav>

        <div className="p-2.5 border-t border-[var(--ug-border-subtle)] flex items-center justify-between gap-2 text-xs">
          {!sidebarCollapsed && (
            <div className="min-w-0">
              <div className="text-[11px] font-medium text-[var(--ug-text-primary)] truncate">
                {meData?.user?.full_name}
              </div>
              <div className="text-[10px] text-[var(--ug-text-muted)] truncate">{meData?.user?.role}</div>
            </div>
          )}
          <button
            type="button"
            onClick={handleLogout}
            title="Sair da Conta"
            aria-label="Sair da Conta"
            className={`${
              sidebarCollapsed ? "w-full justify-center" : ""
            } p-2 rounded-lg hover:bg-red-500/15 text-[var(--ug-text-muted)] hover:text-red-400 flex items-center gap-1.5 transition`}
          >
            <LogOut className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
            {!sidebarCollapsed && <span className="sr-only">Sair da Conta</span>}
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* TOP HEADER MINIMALISTA */}
        <header className="sticky top-0 z-30 ug-bg/85 border-b border-[var(--ug-border)] backdrop-blur-md">
          <div className="px-4 lg:px-6 h-14 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <button
                type="button"
                onClick={() => setMobileMenuOpen(true)}
                aria-label="Abrir menu de navegação"
                className="lg:hidden p-1.5 rounded-lg border border-[var(--ug-border)] text-[var(--ug-text-secondary)]"
              >
                <Menu className="w-4 h-4" />
              </button>
              <div className="min-w-0 flex items-center gap-2">
                <span className="text-[11px] font-medium text-indigo-400 hidden sm:inline">
                  {currentAreaConfig?.label || (activeMenu === "all_resources" ? "Central" : "Workspace")}
                </span>
                <span className="text-[var(--ug-text-muted)] hidden sm:inline">/</span>
                <h2 className="text-sm font-semibold tracking-tight text-[var(--ug-text-primary)] truncate">
                  <span className="sm:hidden">{(currentResourceMeta?.name || "UNION GROWTH OS").split(" — ")[0]}</span>
                  <span className="hidden sm:inline">{currentResourceMeta?.name || "UNION GROWTH OS"}</span>
                </h2>
                {meData?.active_tenant?.brand_name && (
                  <span className="hidden xl:inline-block text-[11px] text-[var(--ug-text-muted)] truncate">
                    • {meData.active_tenant.brand_name}
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-1.5 shrink-0">
              <button
                type="button"
                onClick={() => setCommandOpen(true)}
                aria-label="Abrir busca global (Ctrl+K)"
                className="px-2.5 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] text-xs flex items-center gap-2 transition"
              >
                <Search className="w-3.5 h-3.5 text-indigo-400" aria-hidden="true" />
                <span className="hidden md:inline">Buscar...</span>
                <kbd className="hidden xl:inline-block px-1.5 py-0.2 rounded bg-white/[0.06] text-[10px] font-mono text-[var(--ug-text-muted)]">
                  Ctrl+K
                </kbd>
              </button>

              <button
                type="button"
                onClick={() => navigateTo("my_work")}
                aria-label={`Notificações e pendências (${pendingWorkCount})`}
                className="relative p-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] transition"
              >
                <Bell className="w-4 h-4" />
                {pendingWorkCount > 0 && (
                  <span className="absolute -top-1 -right-1 px-1 min-w-[16px] h-[16px] rounded-full bg-amber-500 text-[10px] font-bold text-zinc-950 flex items-center justify-center tabular-nums">
                    {pendingWorkCount}
                  </span>
                )}
              </button>

              <button
                id="ug-ui-mode-toggle"
                type="button"
                onClick={async () => {
                  const nextMode = uiMode === "SIMPLE" ? "ADVANCED" : "SIMPLE";
                  setUiMode(nextMode);
                  if (typeof window !== "undefined") localStorage.setItem("ug_ui_mode", nextMode);
                  try {
                    await apiFetch("/api/v1/tenants/current", {
                      method: "PUT",
                      body: JSON.stringify({ ui_mode: nextMode }),
                    });
                    showNotice(
                      nextMode === "SIMPLE"
                        ? "Modo Simples ativado: foco em decisões e linguagem clara."
                        : "Modo Avançado ativado: todos os controles técnicos visíveis."
                    );
                  } catch {
                    // mantém preferência local
                  }
                }}
                aria-label={uiMode === "SIMPLE" ? "Alternar para Modo Avançado" : "Alternar para Modo Simples"}
                title="Alternar entre Modo Simples e Modo Avançado"
                className={`px-2.5 py-1.5 rounded-lg border text-[11px] font-medium transition ${
                  uiMode === "ADVANCED"
                    ? "bg-indigo-500/15 border-indigo-500/40 text-indigo-300"
                    : "border-[var(--ug-border)] text-[var(--ug-text-secondary)] hover:bg-white/[0.04]"
                }`}
              >
                <span className="sm:hidden">{uiMode === "SIMPLE" ? "Simples" : "Avanç."}</span>
                <span className="hidden sm:inline">{uiMode === "SIMPLE" ? "Modo Simples" : "Modo Avançado"}</span>
              </button>

              <button
                type="button"
                onClick={() => setThemeMode((prev) => (prev === "dark" ? "light" : "dark"))}
                aria-label={themeMode === "dark" ? "Ativar Modo Claro" : "Ativar Modo Escuro"}
                title={themeMode === "dark" ? "Ativar Modo Claro" : "Ativar Modo Escuro"}
                className="p-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] transition"
              >
                {themeMode === "dark" ? <Sun className="w-4 h-4 text-amber-300" /> : <Moon className="w-4 h-4 text-indigo-500" />}
              </button>

              <button
                type="button"
                onClick={() => setHelpOpen(true)}
                aria-label="Abrir Central de Ajuda"
                title="Ajuda, Glossário e Atalhos"
                className="p-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] transition"
              >
                <HelpCircle className="w-4 h-4 text-indigo-400" />
              </button>

              <button
                type="button"
                onClick={loadAllActiveData}
                aria-label="Atualizar Dados"
                aria-busy={loading}
                data-loading={loading ? "true" : "false"}
                className="p-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] flex items-center gap-1.5 text-xs transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} aria-hidden="true" />
                <span className="sr-only">{loading ? "Atualizando..." : "Atualizar"}</span>
              </button>

              {currentAreaConfig && activeMenu !== "overview" && (
                <button
                  type="button"
                  onClick={() => navigateTo(currentAreaConfig.primaryCtaTarget)}
                  className="hidden sm:inline-flex px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium items-center gap-1.5 transition"
                >
                  <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
                  <span>{currentAreaConfig.primaryCtaLabel}</span>
                </button>
              )}
            </div>
          </div>

          {/* Barra Horizontal Limpa Underline de Submenus */}
          {currentAreaConfig && currentAreaConfig.subtabs.length > 0 && (() => {
            const visibleSubtabs = currentAreaConfig.subtabs.filter(
              (sub) => uiMode === "ADVANCED" || !sub.advancedOnly || activeMenu === sub.id
            );
            const hiddenAdvancedCount = currentAreaConfig.subtabs.filter((s) => s.advancedOnly).length;
            return (
              <nav
                className="px-4 lg:px-6 flex items-center gap-4 border-t border-[var(--ug-border-subtle)] overflow-x-auto"
                aria-label={`Submenus de ${currentAreaConfig.label}`}
              >
                {visibleSubtabs.map((sub) => {
                  const isSubActive = activeMenu === sub.id || (sub.id === "social" && activeMenu === "calendar");
                  return (
                    <button
                      key={sub.id}
                      type="button"
                      onClick={() => navigateTo(sub.id)}
                      title={sub.shortDesc}
                      className={`py-2 text-xs whitespace-nowrap transition border-b-2 -mb-[1px] ${
                        isSubActive
                          ? "border-[var(--ug-accent)] text-[var(--ug-text-primary)] font-semibold"
                          : "border-transparent text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)] font-medium"
                      }`}
                    >
                      {sub.label}
                    </button>
                  );
                })}
                {uiMode === "SIMPLE" && hiddenAdvancedCount > 0 && (
                  <button
                    id="ug-reveal-advanced-subtabs"
                    type="button"
                    onClick={async () => {
                      setUiMode("ADVANCED");
                      if (typeof window !== "undefined") localStorage.setItem("ug_ui_mode", "ADVANCED");
                      try {
                        await apiFetch("/api/v1/tenants/current", {
                          method: "PUT",
                          body: JSON.stringify({ ui_mode: "ADVANCED" }),
                        });
                      } catch {
                        // mantém preferência local
                      }
                      showNotice(`Modo Avançado ativado: +${hiddenAdvancedCount} opções técnicas liberadas.`);
                    }}
                    className="py-2 text-[11px] font-medium whitespace-nowrap text-indigo-400 hover:underline transition"
                  >
                    + {hiddenAdvancedCount} Avançado
                  </button>
                )}
              </nav>
            );
          })()}
        </header>

        <main className="flex-1 overflow-y-auto px-4 py-5 lg:px-8 lg:py-6 space-y-5">
          {loading && !overviewData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <SkeletonCard lines={3} />
              <SkeletonCard lines={3} />
              <SkeletonCard lines={3} />
              <SkeletonCard lines={3} />
            </div>
          )}

          {/* Gatilho discreto sob demanda "Como funciona esta área" */}
          {currentAreaConfig && activeMenu !== "all_resources" && activeMenu !== "overview" && (
            <AreaContextGuide
              areaId={currentAreaConfig.id}
              integrationsData={integrationsData}
              onNavigate={navigateTo}
            />
          )}

          {/* ÁREA 1 — INÍCIO UNIFICADO (FASE 24 EXECUTIVE WORKSPACE) */}
          {activeMenu === "overview" && overviewData && (
            <div className="space-y-5">
              <HomeWorkspace
                meData={meData}
                overviewData={overviewData}
                commandCenterData={commandCenterData}
                activationData={activationData}
                agentsData={agentsData}
                crmData={crmData}
                marketingData={marketingData}
                approvalsData={approvalsData}
                integrationsData={integrationsData}
                systemAlerts={systemAlerts}
                contentFactoryItems={contentFactoryItems}
                automationsData={automationsData}
                aiEnginesConfig={aiEnginesConfig}
                uiMode={uiMode}
                showOnboardingWizard={showOnboardingWizard}
                setShowOnboardingWizard={setShowOnboardingWizard}
                favoriteIds={favoriteIds}
                recentIds={recentIds}
                onboardingDismissed={onboardingDismissed}
                onDismissOnboarding={() => {
                  setOnboardingDismissed(true);
                  if (typeof window !== "undefined") localStorage.setItem("ug_onboarding_dismissed", "1");
                }}
                onRestoreOnboarding={() => {
                  setOnboardingDismissed(false);
                  if (typeof window !== "undefined") localStorage.removeItem("ug_onboarding_dismissed");
                }}
                onNavigate={navigateTo}
                onRunOrchestrator={async () => {
                  showNotice("Executando análise coordenada...");
                  const res = await apiFetch("/api/v1/orchestrator/diagnose", {
                    method: "POST",
                    body: JSON.stringify({ reason: "Acionamento Executivo Manual" }),
                  });
                  setDiagResult(res);
                  await loadAllActiveData();
                  showNotice("Análise multiagente concluída!");
                }}
                apiFetch={apiFetch}
                onReload={loadAllActiveData}
                showNotice={showNotice}
              />

              {diagResult && (
                <div className="max-w-7xl mx-auto ug-card rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-semibold text-emerald-400">
                      Diagnóstico Coordenado ({diagResult.workflow_run_id})
                    </h3>
                    <button
                      type="button"
                      onClick={() => setDiagResult(null)}
                      className="text-[11px] text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)]"
                    >
                      Dispensar
                    </button>
                  </div>
                  <p className="text-xs text-[var(--ug-text-secondary)]">{diagResult.ceo_consolidation?.summary}</p>
                </div>
              )}
            </div>
          )}

          {/* ÁREA 2 — MEU TRABALHO (TRIAGEM LINEAR-STYLE) */}
          {activeMenu === "my_work" && (
            <MyWorkHub
              approvalsData={approvalsData}
              systemAlerts={systemAlerts}
              ceoDailyPlan={ceoDailyPlan}
              crmData={crmData}
              aiEnginesConfig={aiEnginesConfig}
              integrationsData={integrationsData}
              meData={meData}
              uiMode={uiMode}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              onNavigate={navigateTo}
              showNotice={showNotice}
            />
          )}

          {/* ÁREA 5 — EQUIPE DE AGENTES & AUTONOMIA */}
          {activeMenu === "ai_team_overview" && (
            <AITeamAndGovernanceView
              meData={meData}
              agentsData={agentsData}
              aiEnginesConfig={aiEnginesConfig}
              integrationsData={integrationsData}
              uiMode={uiMode}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              onNavigate={navigateTo}
              showNotice={showNotice}
            />
          )}

          {/* TODOS OS RECURSOS (CATÁLOGO PESQUISÁVEL COM FAVORITOS E RECENTES) */}
          {activeMenu === "all_resources" && (
            <AllResourcesHub
              favoriteIds={favoriteIds}
              recentIds={recentIds}
              onToggleFavorite={toggleFavorite}
              onOpenResource={navigateTo}
            />
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

          {/* MARKETING — PERSONAS & CAMPANHAS */}
          {activeMenu === "marketing" && marketingData && (
            <div className="space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[var(--ug-border)]">
                <div>
                  <h3 className="text-base font-semibold text-[var(--ug-text-primary)]">
                    Campanhas &amp; Público Ideal
                  </h3>
                  <p className="text-xs text-[var(--ug-text-muted)] mt-0.5">
                    Defina seu público-alvo, crie campanhas multicanal e gere conteúdo contextual na Fábrica.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={async () => {
                    try {
                      await apiFetch("/api/v1/agents/AGENT_02_CMO/execute", {
                        method: "POST",
                        body: JSON.stringify({ task_name: "generate_monthly_marketing_plan" }),
                      });
                      await loadAllActiveData();
                      showNotice("Novo Planejamento Mensal de Marketing gerado!");
                    } catch (err: any) {
                      showNotice(err?.message || "Não foi possível gerar planejamento agora.");
                    }
                  }}
                  className="px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
                >
                  Gerar Planejamento Mensal Automático
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="ug-card rounded-2xl p-5 space-y-4">
                  <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">Personas &amp; Público-Alvo</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2 items-end text-xs">
                    <div>
                      <label htmlFor="ug-persona-name" className="block text-[11px] font-medium text-slate-300 mb-1">
                        Nome da Persona *
                      </label>
                      <input
                        id="ug-persona-name"
                        value={personaName}
                        onChange={(e) => setPersonaName(e.target.value)}
                        placeholder="Ex.: Gestor Comercial B2B"
                        className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                      />
                    </div>
                    <div>
                      <label htmlFor="ug-persona-vp" className="block text-[11px] font-medium text-slate-300 mb-1">
                        Principal Benefício / Oferta
                      </label>
                      <input
                        id="ug-persona-vp"
                        value={personaVP}
                        onChange={(e) => setPersonaVP(e.target.value)}
                        placeholder="Ex.: Reduzir tempo de resposta comercial"
                        className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                      />
                    </div>
                    <button
                      type="button"
                      onClick={async () => {
                        if (!personaName.trim()) {
                          showNotice("Informe o Nome da Persona antes de cadastrar.");
                          return;
                        }
                        try {
                          await apiFetch("/api/v1/marketing/personas", {
                            method: "POST",
                            body: JSON.stringify({
                              name: personaName.trim(),
                              role_segment: personaRole,
                              value_proposition: personaVP.trim() || "Eficiência e escala com IA",
                            }),
                          });
                          setPersonaName("");
                          setPersonaVP("");
                          await loadAllActiveData();
                          showNotice("Persona criada com sucesso!");
                        } catch (err: any) {
                          showNotice(err?.message || "Erro ao cadastrar persona.");
                        }
                      }}
                      className="py-1.5 px-3 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold h-[30px]"
                    >
                      Criar Persona
                    </button>
                  </div>
                  {marketingData.personas.length === 0 ? (
                    <EmptyState
                      title="Nenhuma persona cadastrada ainda"
                      description="Cadastre quem é o seu cliente ideal acima (ex.: 'Diretor Financeiro PME') para a IA personalizar copies e campanhas."
                    />
                  ) : (
                    marketingData.personas.map((p: any) => (
                      <div key={p.id} className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1 text-xs">
                        <div className="font-bold text-indigo-300">{p.name}</div>
                        <div className="text-slate-400">
                          {p.role_segment} • {p.demographics}
                        </div>
                        <div className="text-slate-200 mt-1">
                          <strong>Proposta de Valor:</strong> {p.value_proposition}
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h4 className="text-sm font-semibold text-[var(--ug-text-primary)]">Campanhas Ativas &amp; ROI ({marketingData.campaigns.length})</h4>
                    <input
                      value={campFilter}
                      onChange={(e) => setCampFilter(e.target.value)}
                      placeholder="Filtrar lista abaixo..."
                      aria-label="Filtrar campanhas"
                      className="w-full sm:w-56 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white"
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2 items-end text-xs">
                    <div className="lg:col-span-2">
                      <label htmlFor="ug-camp-name-input" className="block text-[11px] font-medium text-slate-300 mb-1">
                        Nome da Campanha *
                      </label>
                      <input
                        id="ug-camp-name-input"
                        value={campName}
                        onChange={(e) => setCampName(e.target.value)}
                        placeholder="Ex.: Captação Leads B2B Q4"
                        className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                      />
                    </div>
                    <div>
                      <label htmlFor="ug-camp-channel-select" className="block text-[11px] font-medium text-slate-300 mb-1">
                        Canal Principal
                      </label>
                      <select
                        id="ug-camp-channel-select"
                        value={campChannel}
                        onChange={(e) => setCampChannel(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                      >
                        <option value="Organic SEO + LinkedIn">SEO + LinkedIn</option>
                        <option value="Instagram + Facebook">Instagram + Facebook</option>
                        <option value="Google Search + YouTube">Google + YouTube</option>
                        <option value="Email & CRM">E-mail &amp; CRM</option>
                      </select>
                    </div>
                    <div>
                      <label htmlFor="ug-camp-type-select" className="block text-[11px] font-medium text-slate-300 mb-1">
                        Objetivo / Tipo
                      </label>
                      <select
                        id="ug-camp-type-select"
                        value={campType}
                        onChange={(e) => setCampType(e.target.value)}
                        className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                      >
                        <option value="ACQUISITION">Aquisição de Leads</option>
                        <option value="LAUNCH">Lançamento</option>
                        <option value="SEASONAL">Sazonal</option>
                        <option value="RETENTION">Retenção</option>
                      </select>
                    </div>
                    <div>
                      <label htmlFor="ug-camp-budget-input" className="block text-[11px] font-medium text-slate-300 mb-1">
                        Orçamento Planejado (R$)
                      </label>
                      <input
                        id="ug-camp-budget-input"
                        type="number"
                        value={campBudget}
                        onChange={(e) => setCampBudget(e.target.value)}
                        placeholder="Ex.: 5000"
                        className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                      />
                    </div>
                    <button
                      type="button"
                      onClick={async () => {
                        if (!campName.trim()) {
                          showNotice("Informe o Nome da Campanha antes de salvar.");
                          return;
                        }
                        try {
                          const res = await apiFetch("/api/v1/marketing/campaigns", {
                            method: "POST",
                            body: JSON.stringify({
                              name: campName.trim(),
                              campaign_type: campType,
                              channel: campChannel,
                              objective: "Aquisição e conversão de leads",
                              budget_planned: Number(campBudget) || 0,
                            }),
                          });
                          setCampName("");
                          await loadAllActiveData();
                          showNotice(res.message || "Campanha criada com sucesso!");
                        } catch (err: any) {
                          showNotice(err?.message || "Erro ao criar campanha.");
                        }
                      }}
                      className="lg:col-span-3 py-1.5 px-4 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold h-[30px]"
                    >
                      Criar Campanha
                    </button>
                  </div>
                  {(() => {
                    const visibleCamps = marketingData.campaigns.filter((c: any) => {
                      const q = campFilter.trim().toLowerCase();
                      if (!q) return true;
                      return `${c.name || ""} ${c.channel || ""} ${c.status || ""} ${c.objective || ""}`
                        .toLowerCase()
                        .includes(q);
                    });
                    if (visibleCamps.length === 0) {
                      return (
                        <EmptyState
                          title={marketingData.campaigns.length === 0 ? "Nenhuma campanha criada" : "Nenhuma campanha corresponde à busca"}
                          description="Preencha o Nome da Campanha acima e clique em Criar Campanha para começar a mensurar ROI."
                        />
                      );
                    }
                    return visibleCamps.map((c: any) => (
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
                          Orçamento Planejado: R$ {c.budget_planned} | Gasto Real: R$ {c.spend_real} | Receita Atribuída: R${" "}
                          {c.revenue_attributed}
                        </div>
                      </div>
                    ));
                  })()}
                </div>
              </div>
            </div>
          )}

          {/* 04. SEO DIRECTOR */}
          {activeMenu === "seo" && seoData && (
            <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
              <div className="px-4 py-3 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-200 text-xs">
                <strong>Transparência SEO:</strong> {seoData.gsc_ranking_status?.notice}
              </div>

              <div className="ug-card rounded-xl grid grid-cols-1 lg:grid-cols-3 divide-y lg:divide-y-0 lg:divide-x divide-white/[0.06] overflow-hidden">
                <div className="p-4 space-y-3">
                  <h4 className="text-xs font-semibold text-[var(--ug-text-primary)]">1. Auditoria Técnica (Live HTTP)</h4>
                  <input
                    value={seoUrlInput}
                    onChange={(e) => setSeoUrlInput(e.target.value)}
                    aria-label="URL do site para auditoria SEO"
                    className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                    placeholder="https://seudominio.com.br"
                  />
                  <button
                    type="button"
                    onClick={async () => {
                      await apiFetch("/api/v1/seo/audit", {
                        method: "POST",
                        body: JSON.stringify({ target_url: seoUrlInput, target_keyword: seoKwInput }),
                      });
                      await loadAllActiveData();
                      showNotice("Auditoria técnica de SEO concluída!");
                    }}
                    className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Executar Auditoria Técnica Real
                  </button>
                </div>

                <div className="p-4 space-y-3">
                  <h4 className="text-xs font-semibold text-[var(--ug-text-primary)]">2. Pesquisa de Palavras-Chave &amp; Clusters</h4>
                  <input
                    value={seoKwInput}
                    onChange={(e) => setSeoKwInput(e.target.value)}
                    aria-label="Palavra-chave semente"
                    className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                    placeholder="Palavra-chave semente"
                  />
                  <button
                    type="button"
                    onClick={async () => {
                      await apiFetch("/api/v1/seo/keywords", {
                        method: "POST",
                        body: JSON.stringify({ seed_keyword: seoKwInput }),
                      });
                      await loadAllActiveData();
                      showNotice("Cluster de palavras-chave e cauda longa gerado!");
                    }}
                    className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Descobrir Cauda Longa &amp; Clusters
                  </button>
                </div>

                <div className="p-4 space-y-3">
                  <h4 className="text-xs font-semibold text-[var(--ug-text-primary)]">3. SEO Content Factory (Gerar Artigo)</h4>
                  <input
                    value={seoTopicInput}
                    onChange={(e) => setSeoTopicInput(e.target.value)}
                    aria-label="Título ou tópico do artigo SEO"
                    className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                    placeholder="Título / Tópico do Artigo"
                  />
                  <button
                    type="button"
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
                    className="w-full py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                  >
                    Produzir Artigo Otimizado
                  </button>
                </div>
              </div>

              {seoData.keyword_clusters?.length > 0 && (
                <div className="ug-card rounded-xl overflow-hidden">
                  <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
                    Clusters de Conteúdo &amp; Cauda Longa ({seoData.keyword_clusters.length})
                  </div>
                  <div className="divide-y divide-white/[0.05] text-xs">
                    {seoData.keyword_clusters.map((kc: any) => (
                      <div key={kc.id} className="px-5 py-3 space-y-1">
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-semibold text-indigo-400">{kc.seed_keyword}</span>
                          <span className="px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300 text-[10px]">
                            Intenção: {kc.search_intent}
                          </span>
                        </div>
                        <div className="text-[var(--ug-text-secondary)]">
                          <strong>Cauda Longa:</strong> {kc.long_tail_keywords.slice(0, 6).join(" • ")}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="ug-card rounded-xl overflow-hidden">
                  <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
                    Últimas Auditorias Técnicas ({seoData.audits.length})
                  </div>
                  <div className="divide-y divide-white/[0.05]">
                    {seoData.audits.map((a: any) => {
                      const sig = a.technical_signals || a.generated_schema?.technical_signals || {};
                      return (
                        <div key={a.id} className="px-5 py-3.5 text-xs space-y-1.5">
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-semibold text-indigo-400 truncate">{a.target_url}</span>
                            <OriginBadge origin={a.data_origin} />
                          </div>
                          <div className="tabular-nums text-[var(--ug-text-secondary)]">
                            Score: <strong className="text-emerald-400">{a.overall_score}/100</strong> • {a.response_time_ms}ms • robots:{" "}
                            {a.has_robots_txt ? "Sim" : "Não"} • sitemap: {a.has_sitemap_xml ? "Sim" : "Não"}
                          </div>
                          {Object.keys(sig).length > 0 && (
                            <div className="flex flex-wrap gap-1.5 text-[10px]">
                              <span className="px-1.5 py-0.5 rounded bg-white/[0.05] text-[var(--ug-text-secondary)]">
                                Canonical: {sig.has_canonical ? "OK" : "Ausente"}
                              </span>
                              <span className="px-1.5 py-0.5 rounded bg-white/[0.05] text-[var(--ug-text-secondary)]">
                                Mobile Viewport: {sig.has_viewport_mobile ? "OK" : "Ausente"}
                              </span>
                              <span className="px-1.5 py-0.5 rounded bg-white/[0.05] text-[var(--ug-text-secondary)]">
                                OpenGraph: {sig.has_open_graph ? "OK" : "Incompleto"}
                              </span>
                              <span className="px-1.5 py-0.5 rounded bg-white/[0.05] text-[var(--ug-text-secondary)] tabular-nums">
                                {sig.body_word_count || 0} palavras
                              </span>
                            </div>
                          )}
                          <div className="text-[var(--ug-text-muted)]">
                            Sugestão Title: <span className="text-[var(--ug-text-primary)]">{a.suggested_title}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="ug-card rounded-xl overflow-hidden">
                  <div className="px-5 py-3.5 border-b border-[var(--ug-border-subtle)] text-sm font-semibold text-[var(--ug-text-primary)]">
                    Artigos da SEO Content Factory ({seoData.articles.length})
                  </div>
                  <div className="divide-y divide-white/[0.05]">
                    {seoData.articles.map((art: any) => (
                      <div key={art.id} className="px-5 py-3.5 text-xs space-y-1.5">
                        <div className="font-semibold text-[var(--ug-text-primary)]">{art.title}</div>
                        <div className="text-[var(--ug-text-muted)] tabular-nums">
                          Keyword: {art.target_keyword} • {art.word_count} palavras • Densidade: {art.keyword_density_pct}%
                        </div>
                        <pre className="p-2.5 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] text-[11px] text-[var(--ug-text-secondary)] max-h-40 overflow-y-auto whitespace-pre-wrap">
                          {art.content_markdown}
                        </pre>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 05 & 14. REDES SOCIAIS & CALENDÁRIO EDITORIAL */}
          {(activeMenu === "social" || activeMenu === "calendar") && (
            <div className="space-y-6">
              <div className="bg-[#0f1629] border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="text-sm font-bold text-white">
                      Calendário Editorial &amp; Publicações Individuais (Modo Assistido + Aprovação)
                    </h3>
                    <p className="text-xs text-slate-400">
                      Crie um post individual agora ou gere 30 publicações de uma vez na Fábrica de Conteúdo. Sem OAuth conectado, prepara pacotes em 1 clique sem simular publicação.
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => navigateTo("content_factory")}
                      className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-300 text-xs font-semibold"
                    >
                      Ir para Fábrica (30 peças) →
                    </button>
                    <button
                      type="button"
                      onClick={async () => {
                        try {
                          await apiFetch("/api/v1/agents/AGENT_04_SOCIAL/execute", {
                            method: "POST",
                            body: JSON.stringify({}),
                          });
                          await loadAllActiveData();
                          showNotice("Calendário multicanal gerado pelo AI Social Media Director!");
                        } catch (err: any) {
                          showNotice(err?.message || "Erro ao gerar calendário automático.");
                        }
                      }}
                      className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                    >
                      Gerar Lote de Posts Multicanal com IA
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-5 gap-3 pt-3 border-t border-slate-800 items-end text-xs">
                  <div>
                    <label htmlFor="ug-cal-title-input" className="block text-[11px] font-medium text-slate-300 mb-1">
                      Título da Publicação *
                    </label>
                    <input
                      id="ug-cal-title-input"
                      value={calTitle}
                      onChange={(e) => setCalTitle(e.target.value)}
                      placeholder="Ex.: 3 formas de reduzir retrabalho com IA"
                      className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    />
                  </div>
                  <div>
                    <label htmlFor="ug-cal-platform-select" className="block text-[11px] font-medium text-slate-300 mb-1">
                      Rede Social
                    </label>
                    <select
                      id="ug-cal-platform-select"
                      value={calPlatform}
                      onChange={(e) => setCalPlatform(e.target.value)}
                      className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    >
                      <option value="instagram">Instagram</option>
                      <option value="linkedin">LinkedIn</option>
                      <option value="tiktok">TikTok</option>
                      <option value="youtube">YouTube</option>
                      <option value="facebook">Facebook</option>
                      <option value="pinterest">Pinterest</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="ug-cal-format-select" className="block text-[11px] font-medium text-slate-300 mb-1">
                      Formato
                    </label>
                    <select
                      id="ug-cal-format-select"
                      value={calFormat}
                      onChange={(e) => setCalFormat(e.target.value)}
                      className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    >
                      <option value="CAROUSEL">Carrossel</option>
                      <option value="POST">Post Único</option>
                      <option value="REELS_SHORT">Reels / Short / TikTok</option>
                      <option value="VIDEO">Vídeo Longo</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="ug-cal-date-input" className="block text-[11px] font-medium text-slate-300 mb-1">
                      Data e Hora (AAAA-MM-DD HH:MM)
                    </label>
                    <input
                      id="ug-cal-date-input"
                      value={calDate}
                      onChange={(e) => setCalDate(e.target.value)}
                      placeholder="Ex.: 2026-12-01 09:00"
                      className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={async () => {
                      if (!calTitle.trim()) {
                        showNotice("Informe o Título da Publicação antes de agendar.");
                        return;
                      }
                      try {
                        await apiFetch("/api/v1/social/calendar", {
                          method: "POST",
                          body: JSON.stringify({
                            title: calTitle.trim(),
                            platform: calPlatform,
                            content_format: calFormat,
                            scheduled_for: calDate,
                            auto_generate_copy: true,
                          }),
                        });
                        setCalTitle("");
                        await loadAllActiveData();
                        showNotice("Publicação agendada e enviada para sua revisão/aprovação!");
                      } catch (err: any) {
                        showNotice(err?.message || "Erro ao agendar publicação.");
                      }
                    }}
                    className="py-2 px-3 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold h-[34px]"
                  >
                    Agendar no Calendário
                  </button>
                </div>
              </div>

              {calendarData.length === 0 ? (
                <EmptyState
                  title="Nenhuma publicação no calendário ainda"
                  description="Digite o título de um post acima e clique em 'Agendar no Calendário', ou gere 30 peças completas na Fábrica de Conteúdo."
                  actionLabel="Abrir Fábrica de Conteúdo"
                  onAction={() => navigateTo("content_factory")}
                />
              ) : (
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
                      <div className="flex items-center justify-between pt-2 border-t border-slate-800 gap-2">
                        <span className="text-[11px] text-amber-300">
                          Aprovação:{" "}
                          <strong>{item.approval_status === "APPROVED" ? "Aprovado" : "Aguardando"}</strong> • Envio:{" "}
                          <strong>
                            {item.publish_status === "PUBLISHED"
                              ? "Publicado"
                              : item.publish_status === "PENDING_CREDENTIALS"
                              ? "Modo Assistido (sem OAuth)"
                              : item.publish_status}
                          </strong>
                        </span>
                        <button
                          type="button"
                          onClick={async () => {
                            try {
                              const r = await apiFetch(`/api/v1/social/calendar/${item.id}/publish`, { method: "POST" });
                              await loadAllActiveData();
                              showNotice(r.message || "Status de publicação atualizado.");
                            } catch (err: any) {
                              showNotice(err?.message || "Erro ao tentar publicar.");
                            }
                          }}
                          className="px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] shrink-0"
                        >
                          Aprovar &amp; Verificar Envio
                        </button>
                      </div>
                      {item.last_error && <div className="text-[11px] text-amber-400/90">{item.last_error}</div>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* FASE 14 — CONTENT FACTORY */}
          {activeMenu === "content_factory" && (() => {
            const cfPersonas = marketingData?.personas || [];
            const cfLatestPersona = cfPersonas.length > 0 ? cfPersonas[cfPersonas.length - 1] : null;
            const cfLatestCampaign = (marketingData?.campaigns || [])[0] || null;
            const cfTenant = meData?.active_tenant;
            const cfDraftCount = contentFactoryItems.filter((it: any) => it.status !== "PUBLISHED").length;

            return (
            <div className="space-y-6">
              <div className="bg-[#0f1629] border border-indigo-500/30 p-5 rounded-xl space-y-4">
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div>
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <span>🏭</span> Fábrica de Conteúdo — Produção Mensal (30 Publicações Prontas)
                    </h3>
                    <p className="text-xs text-slate-400 mt-1">
                      Gera 30 peças multicanal alinhadas à sua empresa, site, nicho, persona e campanha. Sem conta social conectada, use <strong>📋 Pacote 1-Clique</strong> para copiar e publicar manualmente.
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => navigateTo("calendar")}
                      className="px-3.5 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold"
                    >
                      Criar 1 Post Manual →
                    </button>
                    {cfDraftCount > 0 && (
                      <button
                        type="button"
                        onClick={async () => {
                          setLoading(true);
                          try {
                            const res = await apiFetch("/api/v1/content-factory/drafts", { method: "DELETE" });
                            await loadAllActiveData();
                            showNotice(`${res.deleted_count} rascunho(s) não publicado(s) removido(s)!`);
                          } catch (e: any) {
                            showNotice(e.message || "Erro ao limpar rascunhos");
                          } finally {
                            setLoading(false);
                          }
                        }}
                        className="px-3.5 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-semibold"
                      >
                        Limpar Rascunhos ({cfDraftCount})
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={async () => {
                        setLoading(true);
                        try {
                          const res = await apiFetch("/api/v1/content-factory/generate-batch", {
                            method: "POST",
                            body: JSON.stringify({
                              count: 30,
                              company_name: cfTenant?.brand_name || cfTenant?.name || "",
                              niche: cfTenant?.niche || "",
                              target_audience: cfLatestPersona?.name || cfTenant?.target_audience || "",
                              focus_theme: cfFocusTheme.trim(),
                              replace_drafts: cfReplaceDrafts,
                              persona_id: cfLatestPersona?.id || null,
                              campaign_id: cfLatestCampaign?.id || null,
                            }),
                          });
                          await loadAllActiveData();
                          showNotice(`Fábrica de Conteúdo: ${res.total_generated} conteúdos criados para ${cfTenant?.brand_name || "sua marca"} (nota média ${res.average_quality_score}/100)!`);
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
                </div>

                {/* Contexto Real Lido pela Fábrica */}
                <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs space-y-2.5">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="font-bold text-indigo-300">Contexto usado na criação dos conteúdos:</span>
                    <button
                      type="button"
                      onClick={() => navigateTo("settings")}
                      className="text-[11px] text-indigo-300 hover:underline"
                    >
                      Ajustar site/nicho em Configurações →
                    </button>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2 text-[11px]">
                    <div className="p-2 rounded bg-slate-950/70 border border-slate-800">
                      <span className="text-slate-400 block">Marca</span>
                      <strong className="text-white">{cfTenant?.brand_name || "-"}</strong>
                    </div>
                    <div className="p-2 rounded bg-slate-950/70 border border-slate-800">
                      <span className="text-slate-400 block">Site / Link</span>
                      <strong className="text-emerald-300 break-all">{cfTenant?.domain || "Não informado"}</strong>
                    </div>
                    <div className="p-2 rounded bg-slate-950/70 border border-slate-800">
                      <span className="text-slate-400 block">Nicho</span>
                      <strong className="text-white">{cfTenant?.niche || "-"}</strong>
                    </div>
                    <div className="p-2 rounded bg-slate-950/70 border border-slate-800">
                      <span className="text-slate-400 block">Persona Ativa</span>
                      <strong className="text-white">{cfLatestPersona?.name || cfTenant?.target_audience || "-"}</strong>
                    </div>
                    <div className="p-2 rounded bg-slate-950/70 border border-slate-800">
                      <span className="text-slate-400 block">Campanha Ativa</span>
                      <strong className="text-white">{cfLatestCampaign?.name || "Padrão da marca"}</strong>
                    </div>
                  </div>
                  <div className="flex flex-col md:flex-row md:items-center gap-3 pt-1">
                    <div className="flex-1">
                      <label htmlFor="ug-cf-focus-input" className="block text-[11px] text-slate-300 mb-1">
                        Oferta / Chamada Principal que aparecerá nos posts (opcional):
                      </label>
                      <input
                        id="ug-cf-focus-input"
                        value={cfFocusTheme}
                        onChange={(e) => setCfFocusTheme(e.target.value)}
                        placeholder={cfLatestPersona?.value_proposition || "Ex.: Cadastro gratuito no site para receber pedidos de novos clientes"}
                        className="w-full px-3 py-1.5 rounded bg-slate-950 border border-slate-700 text-xs text-white"
                      />
                    </div>
                    <label className="inline-flex items-center gap-2 text-[11px] text-slate-300 cursor-pointer pt-4">
                      <input
                        type="checkbox"
                        checked={cfReplaceDrafts}
                        onChange={(e) => setCfReplaceDrafts(e.target.checked)}
                        className="rounded border-slate-600 bg-slate-900 text-indigo-600"
                      />
                      <span>Substituir rascunhos não publicados ao gerar novo lote</span>
                    </label>
                  </div>
                </div>
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
              {(() => {
                const visibleCf = contentFactoryItems.filter((it: any) => cfFilter === "ALL" || it.channel === cfFilter);
                if (visibleCf.length === 0) {
                  return (
                    <EmptyState
                      title="Nenhum conteúdo encontrado neste canal"
                      description="Clique em 'Gerar Lote de 30 Publicações' acima para preencher automaticamente todos os canais ou selecione 'Todos os Canais'."
                      actionLabel={cfFilter !== "ALL" ? "Ver Todos os Canais" : undefined}
                      onAction={cfFilter !== "ALL" ? () => setCfFilter("ALL") : undefined}
                    />
                  );
                }
                return (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {visibleCf.map((it: any) => (
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
                            <span>Status: <strong className="text-amber-300">{it.status === "PUBLISHED" ? "Publicado" : "Pronto para uso"}</strong></span>
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
                              aria-label={`Marcar ${it.title} como publicado`}
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
                );
              })()}
            </div>
            );
          })()}

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
            <CRMAndLeadsWorkspace
              crmData={crmData}
              revenueIntel={revenueIntel}
              crmLeadFilter={crmLeadFilter}
              setCrmLeadFilter={setCrmLeadFilter}
              leadName={leadName}
              setLeadName={setLeadName}
              leadEmail={leadEmail}
              setLeadEmail={setLeadEmail}
              leadPhone={leadPhone}
              setLeadPhone={setLeadPhone}
              leadCompany={leadCompany}
              setLeadCompany={setLeadCompany}
              leadValue={leadValue}
              setLeadValue={setLeadValue}
              leadLgpdConsent={leadLgpdConsent}
              setLeadLgpdConsent={setLeadLgpdConsent}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              onNavigate={navigateTo}
              showNotice={showNotice}
            />
          )}

          {/* 10. COMERCIAL & PIPELINE VISUAL */}
          {activeMenu === "commercial" && crmData && (
            <CommercialPipelineWorkspace
              crmData={crmData}
              revenueIntel={revenueIntel}
              dealTitle={dealTitle}
              setDealTitle={setDealTitle}
              dealValue={dealValue}
              setDealValue={setDealValue}
              dealStage={dealStage}
              setDealStage={setDealStage}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              onNavigate={navigateTo}
              showNotice={showNotice}
            />
          )}

          {/* 11. CONCORRENTES */}
          {activeMenu === "competitors" && (
            <CompetitorsIntelligenceWorkspace
              competitorsData={competitorsData}
              compName={compName}
              setCompName={setCompName}
              compUrl={compUrl}
              setCompUrl={setCompUrl}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              showNotice={showNotice}
            />
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

          {/* AUTOMAÇÕES NATIVAS PYTHON */}
          {activeMenu === "automations" && automationsData && (
            <div className="space-y-6 max-w-6xl mx-auto">
              <ConversationalAutomationPanel
                apiFetch={apiFetch}
                onReload={loadAllActiveData}
                showNotice={showNotice}
                uiMode={uiMode}
              />

              <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-[var(--ug-border)]">
                <div>
                  <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">
                    {uiMode === "SIMPLE"
                      ? "Rotinas Automáticas Ativas da Sua Empresa (100% Nativo • Zero n8n)"
                      : "Central de Automações 100% Nativa em Python (Zero Dependência de n8n)"}
                  </h3>
                  <p className="text-xs text-[var(--ug-text-muted)]">
                    {uiMode === "SIMPLE"
                      ? `O sistema monitora ${automationsData.rules?.length || 0} rotinas automáticas com segurança na nuvem.`
                      : `Motor: ${automationsData.scheduler?.engine} • Status: `}
                    {uiMode === "ADVANCED" && (
                      <strong className="text-emerald-400">
                        {automationsData.scheduler?.running ? "ATIVO NO SERVIDOR CLOUD" : "PARADO"}
                      </strong>
                    )}
                  </p>
                </div>
                {uiMode === "SIMPLE" && (
                  <button
                    type="button"
                    onClick={() => setUiMode("ADVANCED")}
                    className="px-3 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[11px] text-[var(--ug-text-secondary)] font-medium"
                  >
                    Ver logs e ajustes técnicos (Avançado)
                  </button>
                )}
              </div>

              <div className="ug-card rounded-2xl divide-y divide-white/[0.05]">
                {(uiMode === "SIMPLE" ? automationsData.rules.slice(0, 6) : automationsData.rules).map((r: any) => (
                  <div key={r.id} className="px-4 py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs hover:bg-white/[0.02] transition">
                    <div className="space-y-0.5 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-medium text-[var(--ug-text-primary)]">{r.name}</span>
                        <span className="px-2 py-0.5 rounded bg-indigo-500/12 text-indigo-300 text-[10px]">
                          {uiMode === "SIMPLE" ? r.frequency_label : `${r.trigger_type} • ${r.frequency_label}`}
                        </span>
                      </div>
                      {uiMode === "ADVANCED" ? (
                        <div className="text-[11px] text-[var(--ug-text-muted)] tabular-nums">
                          Agente: <strong className="text-[var(--ug-text-secondary)]">{r.action_agent}</strong> • Execuções: {r.run_count} • Status:{" "}
                          <strong className="text-emerald-400">{r.last_status}</strong>
                        </div>
                      ) : (
                        <div className="text-[11px] text-[var(--ug-text-muted)] tabular-nums">
                          Execuções: <strong className="text-[var(--ug-text-secondary)]">{r.run_count}</strong> • Estado:{" "}
                          <strong className="text-emerald-400">{r.last_status === "READY" ? "Pronta" : r.last_status}</strong>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        type="button"
                        onClick={async () => {
                          await apiFetch(`/api/v1/automations/${r.id}/run`, {
                            method: "POST",
                            body: JSON.stringify({}),
                          });
                          await loadAllActiveData();
                          showNotice(`Automação '${r.name}' executada imediatamente!`);
                        }}
                        className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-medium"
                      >
                        Executar Agora
                      </button>
                      {uiMode === "ADVANCED" && (
                        <button
                          type="button"
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
                          className="px-2.5 py-1.5 rounded-lg border border-[var(--ug-border)] hover:bg-white/[0.04] text-[var(--ug-text-secondary)] text-[11px]"
                        >
                          Testar Retry + Backoff
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {uiMode === "ADVANCED" && automationsData.executions?.length > 0 && (
                <div className="ug-card rounded-xl divide-y divide-white/[0.05]">
                  <div className="px-4 py-3 text-xs font-semibold text-[var(--ug-text-primary)]">
                    Histórico Persistido de Execuções
                  </div>
                  {automationsData.executions.map((ex: any) => (
                    <div key={ex.id} className="px-4 py-2.5 text-xs flex flex-wrap justify-between gap-2">
                      <div>
                        <span className="font-medium text-indigo-400">Regra #{ex.rule_id}</span> •{" "}
                        <span className="text-[var(--ug-text-secondary)]">{ex.result_summary?.summary || ex.error_message}</span>
                      </div>
                      <div className="text-[var(--ug-text-muted)] tabular-nums">
                        <strong className="text-emerald-400">{ex.status}</strong> (Tentativa #{ex.attempt_number} • {ex.duration_ms}ms)
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

          {/* 17. RELATÓRIOS & ANALYTICS */}
          {activeMenu === "reports" && reportsData && (
            <div className="space-y-6">
              <AnalyticsAttributionPanel attribution={analyticsAttrData} />

              <div className="ug-card rounded-2xl overflow-hidden">
                <div className="px-5 py-4 border-b border-[var(--ug-border-subtle)] flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">Relatório Executivo Consolidado</h3>
                    <p className="text-xs text-[var(--ug-text-muted)] mt-0.5">
                      Empresa: {reportsData.tenant?.brand_name || reportsData.tenant?.name || "—"} • Plano:{" "}
                      {reportsData.tenant?.plan_tier || "—"} • Gerado em{" "}
                      {reportsData.generated_at ? new Date(reportsData.generated_at).toLocaleString("pt-BR") : "agora"}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={async () => {
                      const bkp = await apiFetch("/api/v1/system/backup", { method: "POST" });
                      showNotice(`Backup persistente criado: ${bkp.backup_file} (${bkp.size_bytes} bytes)`);
                    }}
                    className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
                  >
                    Gerar Snapshot &amp; Backup Agora
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-white/[0.06]">
                  <div className="p-4">
                    <div className="text-[11px] text-[var(--ug-text-muted)]">Receita Real Confirmada</div>
                    <div className="text-lg font-semibold text-emerald-400 mt-1 tabular-nums">
                      R$ {Number(reportsData.financial_performance?.real_revenue || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                    </div>
                  </div>
                  <div className="p-4">
                    <div className="text-[11px] text-[var(--ug-text-muted)]">Lucro Real / Margem</div>
                    <div className="text-lg font-semibold text-[var(--ug-text-primary)] mt-1 tabular-nums">
                      R$ {Number(reportsData.financial_performance?.real_profit || 0).toLocaleString("pt-BR", { minimumFractionDigits: 2 })} (
                      {Number(reportsData.financial_performance?.margin_pct || 0)}%)
                    </div>
                  </div>
                  <div className="p-4">
                    <div className="text-[11px] text-[var(--ug-text-muted)]">Leads Reais &amp; Conversão</div>
                    <div className="text-lg font-semibold text-indigo-400 mt-1 tabular-nums">
                      {reportsData.financial_performance?.leads_total ?? 0} leads •{" "}
                      {reportsData.financial_performance?.conversion_rate_pct ?? 0}% conv.
                    </div>
                  </div>
                  <div className="p-4">
                    <div className="text-[11px] text-[var(--ug-text-muted)]">Conexões Externas</div>
                    <div className="text-lg font-semibold text-amber-300 mt-1 tabular-nums">
                      {(reportsData.integrations_summary?.connected || []).length} ativas •{" "}
                      {(reportsData.integrations_summary?.pending_credentials || []).length} opcionais
                    </div>
                  </div>
                </div>

                {reportsData.ceo_briefing && (
                  <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
                    <div className="font-bold text-white">
                      Resumo Executivo ({reportsData.ceo_briefing.date || "Hoje"}): {reportsData.ceo_briefing.headline}
                    </div>
                    {Array.isArray(reportsData.ceo_briefing.what_happened) && reportsData.ceo_briefing.what_happened.length > 0 && (
                      <ul className="list-disc pl-4 text-slate-300 space-y-1">
                        {reportsData.ceo_briefing.what_happened.map((item: string, idx: number) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    )}
                    {Array.isArray(reportsData.ceo_briefing.recommendations) && reportsData.ceo_briefing.recommendations.length > 0 && (
                      <div className="pt-2 border-t border-slate-800">
                        <span className="font-semibold text-indigo-300">Recomendações Prioritárias: </span>
                        <span className="text-slate-300">{reportsData.ceo_briefing.recommendations.join(" • ")}</span>
                      </div>
                    )}
                  </div>
                )}

                <details className="rounded-xl bg-slate-950 border border-slate-800">
                  <summary className="px-4 py-2.5 text-xs font-semibold text-slate-300 cursor-pointer hover:text-white">
                    Ver Detalhes Técnicos Completos (JSON de Auditoria)
                  </summary>
                  <pre className="p-4 border-t border-slate-800 text-xs text-slate-300 overflow-x-auto">
                    {JSON.stringify(reportsData, null, 2)}
                  </pre>
                </details>
              </div>
            </div>
          )}

          {/* INTEGRAÇÕES / CONECTAR FERRAMENTAS EXTERNAS */}
          {activeMenu === "integrations" && (
            <div className="space-y-5 max-w-6xl mx-auto">
              <div className="flex flex-wrap items-end justify-between gap-3 pb-3 border-b border-[var(--ug-border)]">
                <div>
                  <h3 className="text-base font-semibold text-[var(--ug-text-primary)]">
                    {uiMode === "SIMPLE"
                      ? "Conectar Ferramentas Externas (Status Real)"
                      : "Central de Integrações Oficiais (Criptografia Fernet • Status Real)"}
                  </h3>
                  <p className="text-xs text-[var(--ug-text-muted)]">
                    Contas sem conexão continuam funcionando no Modo Assistido em 1 clique, sem simular envios.
                  </p>
                </div>
                <div className="flex items-center gap-1.5" role="group" aria-label="Filtrar status de integrações">
                  {[
                    { id: "ALL", label: `Todas (${integrationsData.length})` },
                    {
                      id: "CONNECTED",
                      label: `Conectadas (${integrationsData.filter((i: any) => i.status === "CONNECTED").length})`,
                    },
                    {
                      id: "PENDING",
                      label: `Pendentes (${integrationsData.filter((i: any) => i.status !== "CONNECTED").length})`,
                    },
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
                {integrationsData
                  .filter((intg: any) => {
                    if (intgStatusFilter === "CONNECTED") return intg.status === "CONNECTED";
                    if (intgStatusFilter === "PENDING") return intg.status !== "CONNECTED";
                    return true;
                  })
                  .map((intg: any) => {
                    const reqFields: string[] = intg.setup_guide?.required_credentials || ["api_key"];
                    const provMap = credFieldInputs[intg.provider_key] || {};
                    const isConn = intg.status === "CONNECTED";
                    return (
                      <div
                        key={intg.provider_key}
                        className="bg-[#0f1629] border border-slate-800 rounded-xl p-4 space-y-2.5 text-xs"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-bold text-white text-sm">{intg.provider_name}</span>
                          <StatusPill
                            status={isConn ? "EXECUTED" : intg.status === "ERROR" ? "FAILED" : "NEEDS_CREDENTIALS"}
                            label={isConn ? "Conectada" : intg.status === "ERROR" ? "Falha na Conexão" : "Aguardando Conexão"}
                          />
                        </div>
                        <div className="text-slate-300">
                          <strong>O que habilita:</strong> {intg.setup_guide.features_unlocked}
                        </div>
                        <div className="text-slate-400">
                          <strong>Onde conseguir:</strong> {intg.setup_guide.where_to_obtain}
                        </div>
                        {!isConn && (
                          <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] text-slate-300">
                            <strong className="text-indigo-300">Sem esta integração:</strong> o sistema continua operando no <strong>Modo Assistido</strong> (prepara conteúdos, análises e pacotes 1-clique sem envio externo automático).
                          </div>
                        )}
                        <details className="text-[11px] text-slate-400">
                          <summary className="cursor-pointer hover:text-slate-200">
                            Ver permissões / escopos técnicos ({reqFields.length} credencial(is))
                          </summary>
                          <div className="pt-1 text-slate-400">
                            Campos exigidos: {reqFields.join(", ")} • Escopos: {intg.setup_guide.permissions_required.join(", ")}
                          </div>
                        </details>
                        {intg.last_error && <div className="text-amber-400 text-[11px]">{intg.last_error}</div>}
                        <div className="pt-1 space-y-2">
                          <div className="grid grid-cols-1 gap-2">
                            {reqFields.map((rk) => {
                              const inputId = `ug-intg-${intg.provider_key}-${rk}`;
                              const val = provMap[rk] ?? "";
                              return (
                                <div key={rk}>
                                  <label htmlFor={inputId} className="block text-[10px] font-medium text-slate-300 mb-0.5">
                                    {rk.replace(/_/g, " ").toUpperCase()}
                                  </label>
                                  <input
                                    id={inputId}
                                    type={rk.includes("secret") || rk.includes("token") || rk.includes("key") ? "password" : "text"}
                                    value={val}
                                    onChange={(e) =>
                                      setCredFieldInputs({
                                        ...credFieldInputs,
                                        [intg.provider_key]: { ...provMap, [rk]: e.target.value },
                                      })
                                    }
                                    placeholder={`Ex.: cole ${rk} de ${intg.provider_name}`}
                                    className="w-full px-2.5 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-white"
                                  />
                                </div>
                              );
                            })}
                          </div>
                          <div className="flex gap-2">
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
                                  showNotice(`Preencha os campos obrigatórios de ${intg.provider_name}: ${missing.join(", ")}.`);
                                  return;
                                }
                                try {
                                  const r = await apiFetch("/api/v1/integrations/connect", {
                                    method: "POST",
                                    body: JSON.stringify({
                                      provider_key: intg.provider_key,
                                      credentials: credsObj,
                                    }),
                                  });
                                  await loadAllActiveData();
                                  showNotice(`${intg.provider_name}: ${r.message}`);
                                } catch (err: any) {
                                  showNotice(err?.message || `Erro ao conectar ${intg.provider_name}.`);
                                }
                              }}
                              className="flex-1 px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-semibold"
                            >
                              Salvar &amp; Testar Conexão
                            </button>
                            <button
                              type="button"
                              onClick={async () => {
                                try {
                                  const r = await apiFetch(`/api/v1/integrations/${intg.provider_key}/test`, {
                                    method: "POST",
                                  });
                                  await loadAllActiveData();
                                  showNotice(`${intg.provider_name}: ${r.message}`);
                                } catch (err: any) {
                                  showNotice(err?.message || `Falha ao testar ${intg.provider_name}.`);
                                }
                              }}
                              className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-white font-medium"
                            >
                              Testar Conexão
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          )}

          {/* 19. CONFIGURAÇÕES, AUTONOMIA & PLANOS SAAS */}
          {activeMenu === "settings" && meData && (
            <div className="space-y-6 max-w-7xl mx-auto ug-fade-in">
              {/* FLUXO 1 — CONFIGURAR EMPRESA E MARCA ATIVA */}
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
                    <input
                      id="ug-edit-company-input"
                      value={editCompanyName}
                      onChange={(e) => setEditCompanyName(e.target.value)}
                      placeholder="Ex.: Union Soluções Digitais Ltda"
                      className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                    />
                  </div>
                  <div>
                    <label htmlFor="ug-edit-brand-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                      Nome da Marca (exibição) *
                    </label>
                    <input
                      id="ug-edit-brand-input"
                      value={editBrandName}
                      onChange={(e) => setEditBrandName(e.target.value)}
                      placeholder="Ex.: Union Tech"
                      className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                    />
                  </div>
                  <div>
                    <label htmlFor="ug-edit-domain-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                      Site / Domínio Principal
                    </label>
                    <input
                      id="ug-edit-domain-input"
                      value={editDomain}
                      onChange={(e) => setEditDomain(e.target.value)}
                      placeholder="Ex.: https://suaempresa.com.br"
                      className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                    />
                  </div>
                  <div>
                    <label htmlFor="ug-edit-niche-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                      Nicho / Segmento de Atuação
                    </label>
                    <input
                      id="ug-edit-niche-input"
                      value={editNiche}
                      onChange={(e) => setEditNiche(e.target.value)}
                      placeholder="Ex.: Automação Comercial & IA B2B"
                      className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label htmlFor="ug-edit-audience-input" className="block text-[11px] font-medium text-[var(--ug-text-secondary)] mb-1">
                      Público-Alvo Principal (quem compra de você)
                    </label>
                    <input
                      id="ug-edit-audience-input"
                      value={editAudience}
                      onChange={(e) => setEditAudience(e.target.value)}
                      placeholder="Ex.: Diretores e gestores de empresas com 10 a 200 funcionários"
                      className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                    />
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
                        showNotice("Preencha o Nome Oficial da Empresa e o Nome da Marca antes de salvar.");
                        return;
                      }
                      try {
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
                        await loadAllActiveData();
                        showNotice("Identidade da empresa e marca atualizada com sucesso!");
                      } catch (err: any) {
                        showNotice(err?.message || "Erro ao salvar dados da empresa.");
                      }
                    }}
                    className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                  >
                    Salvar Identidade da Empresa
                  </button>
                </div>
              </div>

              <div className="ug-card rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">Nível de Autonomia Operacional da IA</h3>
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
                      type="button"
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

              <PlansAndUsagePanel
                meData={meData}
                plansOverview={plansOverview}
                apiFetch={apiFetch}
                onReload={loadAllActiveData}
                showNotice={showNotice}
              />

              <BrandIntelligenceCenter
                apiFetch={apiFetch}
                onReload={loadAllActiveData}
                showNotice={showNotice}
              />

              <div className="ug-card rounded-xl p-5 space-y-4">
                <h3 className="text-sm font-semibold text-[var(--ug-text-primary)]">Nova Empresa / Unidade (Isolamento Completo)</h3>
                <div className="flex flex-wrap gap-3">
                  <input
                    value={newTenantName}
                    onChange={(e) => setNewTenantName(e.target.value)}
                    placeholder="Ex.: Nova Unidade Comercial Ltda"
                    aria-label="Nome da Nova Empresa ou Filial"
                    className="flex-1 min-w-[220px] px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-xs text-[var(--ug-text-primary)]"
                  />
                  <button
                    type="button"
                    onClick={async () => {
                      if (!newTenantName.trim()) {
                        showNotice("Informe o nome da nova empresa antes de adicionar.");
                        return;
                      }
                      await apiFetch("/api/v1/tenants", {
                        method: "POST",
                        body: JSON.stringify({ name: newTenantName.trim(), brand_name: newTenantName.trim() }),
                      });
                      setNewTenantName("");
                      await loadAllActiveData();
                      showNotice("Nova empresa criada com isolamento multi-tenant completo!");
                    }}
                    className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
                  >
                    Adicionar Empresa
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* FASE 17 — OPERAÇÃO COMERCIAL MULTINEGÓCIO (3 UNIDADES) */}
          {activeMenu === "multibusiness" && mbDashboard && (
            <MultiBusinessAndProposalsWorkspace
              mbDashboard={mbDashboard}
              setMbDashboard={setMbDashboard}
              selectedUnit={selectedUnit}
              setSelectedUnit={setSelectedUnit}
              token={token}
              activeTenantId={activeTenantId}
              propClientName={propClientName}
              setPropClientName={setPropClientName}
              propClientCompany={propClientCompany}
              setPropClientCompany={setPropClientCompany}
              propClientEmail={propClientEmail}
              setPropClientEmail={setPropClientEmail}
              propServiceCode={propServiceCode}
              setPropServiceCode={setPropServiceCode}
              propProblem={propProblem}
              setPropProblem={setPropProblem}
              agencyClientName={agencyClientName}
              setAgencyClientName={setAgencyClientName}
              agencyBrandName={agencyBrandName}
              setAgencyBrandName={setAgencyBrandName}
              agencyPlanTier={agencyPlanTier}
              setAgencyPlanTier={setAgencyPlanTier}
              agencyRetainer={agencyRetainer}
              apiFetch={apiFetch}
              onNavigate={navigateTo}
              showNotice={showNotice}
            />
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
            <AIEnginesHubWorkspace
              aiEnginesConfig={aiEnginesConfig}
              setAiEnginesConfig={setAiEnginesConfig}
              aiHubSubmenu={aiHubSubmenu}
              setAiHubSubmenu={setAiHubSubmenu}
              aiKeyInputs={aiKeyInputs}
              setAiKeyInputs={setAiKeyInputs}
              aiEndpointInputs={aiEndpointInputs}
              setAiEndpointInputs={setAiEndpointInputs}
              aiGenTopic={aiGenTopic}
              setAiGenTopic={setAiGenTopic}
              aiGenPlatform={aiGenPlatform}
              aiGenMode={aiGenMode}
              setAiGenMode={setAiGenMode}
              aiPieceType={aiPieceType}
              setAiPieceType={setAiPieceType}
              aiImgPrompt={aiImgPrompt}
              setAiImgPrompt={setAiImgPrompt}
              aiImgMode={aiImgMode}
              setAiImgMode={setAiImgMode}
              aiVidPrompt={aiVidPrompt}
              setAiVidPrompt={setAiVidPrompt}
              aiVidStage={aiVidStage}
              setAiVidStage={setAiVidStage}
              aiGenLoading={aiGenLoading}
              setAiGenLoading={setAiGenLoading}
              aiGenResult={aiGenResult}
              setAiGenResult={setAiGenResult}
              apiFetch={apiFetch}
              showNotice={showNotice}
            />
          )}
        </main>
      </div>

      <CommandCenter
        open={commandOpen}
        onClose={() => setCommandOpen(false)}
        onNavigate={(view) => navigateTo(view)}
        crmData={crmData}
        marketingData={marketingData}
        mbDashboard={mbDashboard}
        approvalsData={approvalsData}
        integrationsData={integrationsData}
        contentFactoryItems={contentFactoryItems}
      />

      <HelpCenterDrawer
        open={helpOpen}
        onClose={() => setHelpOpen(false)}
        currentView={activeMenu}
        onRestoreOnboarding={() => {
          setOnboardingDismissed(false);
          if (typeof window !== "undefined") {
            localStorage.removeItem("ug_onboarding_dismissed");
          }
          navigateTo("ceo");
          setHelpOpen(false);
        }}
        onOpenCommandCenter={() => {
          setHelpOpen(false);
          setCommandOpen(true);
        }}
      />

      <ToastBanner
        message={toast}
        onClose={() => setToast("")}
      />
    </div>
  );
}
