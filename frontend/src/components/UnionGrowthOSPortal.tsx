"use client";

import React, { useEffect, useState, useCallback, useMemo, useRef } from "react";
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
import { ReleaseHistoryDrawer } from "@/components/ReleaseHistoryDrawer";
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
import { AIAutonomyAndOpsWorkspace } from "@/components/AIAutonomyAndOpsWorkspace";
import {
  CreativeCopyAndGrowthLabWorkspace,
  MarketingCampaignsWorkspace,
  SEOWorkspace,
  SocialAndContentWorkspace,
} from "@/components/MarketingAndSEOWorkspace";
import {
  CustomerSuccessWorkspace,
  FinanceAndReportsWorkspace,
  IntegrationsAndSettingsWorkspace,
} from "@/components/ManagementAndIntegrationsWorkspace";

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
  const loadSeqRef = useRef(0);
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

  // FASE 27 — Versionamento SemVer & Drawer de Releases
  const [versionInfo, setVersionInfo] = useState<any>(null);
  const [releaseDrawerOpen, setReleaseDrawerOpen] = useState<boolean>(false);

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
    const seq = ++loadSeqRef.current;
    setLoading(true);
    try {
      // Fase 26: Carrega Bootstrap Executivo Consolidado em 1 única chamada rápida (< 1s)
      const boot = await apiFetch("/api/v1/growth-os/bootstrap").catch(() => null);
      const me = boot?.me ?? (await apiFetch("/api/v1/auth/me"));
      const ov = boot?.overview ?? (await apiFetch("/api/v1/dashboard/overview"));
      const cPlan = boot?.ceo_daily_plan ?? (await apiFetch("/api/v1/ceo/daily-plan").catch(() => null));
      const cmdRes = boot?.command_center ?? (await apiFetch("/api/v1/growth-os/command-center").catch(() => null));
      const actRes = boot?.activation_retention ?? (await apiFetch("/api/v1/growth-os/activation-retention").catch(() => null));
      const verRes = boot?.version_info ?? (await apiFetch("/api/v1/system/version").catch(() => null));
      if (loadSeqRef.current !== seq) return;
      if (verRes) setVersionInfo(verRes);
      setMeData(me);
      setEditCompanyName(me?.active_tenant?.name || "");
      setEditBrandName(me?.active_tenant?.brand_name || "");
      setEditDomain(me?.active_tenant?.domain || "");
      setEditNiche(me?.active_tenant?.niche || "");
      setEditAudience(me?.active_tenant?.target_audience || "");
      setBrandColorPrimary(me?.active_tenant?.primary_color || "#6366F1");
      setBrandColorSecondary(me?.active_tenant?.secondary_color || "#10B981");
      if (me?.active_tenant?.ui_mode === "SIMPLE" || me?.active_tenant?.ui_mode === "ADVANCED") {
        setUiMode(me.active_tenant.ui_mode);
      }
      setOverviewData(ov);
      setCeoDailyPlan(cPlan);
      if (cmdRes) setCommandCenterData(cmdRes);
      if (actRes) setActivationData(actRes);

      const [
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
        opDash,
        sAlerts,
        rCosts,
        mbDash,
        aiCfg,
        pilotRes,
        attrRes,
        plRes,
        revRes,
      ] = await Promise.all([
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
        apiFetch("/api/v1/system/operational-dashboard").catch(() => null),
        apiFetch("/api/v1/system/alerts").catch(() => []),
        apiFetch("/api/v1/system/resource-costs").catch(() => null),
        apiFetch(`/api/v1/commercial/multibusiness-dashboard?unit=${selectedUnit}`).catch(() => null),
        apiFetch("/api/v1/ai-engines/config").catch(() => null),
        apiFetch("/api/v1/system/pilot-7-days").catch(() => null),
        apiFetch("/api/v1/growth-os/analytics-attribution").catch(() => null),
        apiFetch("/api/v1/plans/overview").catch(() => null),
        apiFetch("/api/v1/growth-os/revenue-intelligence").catch(() => null),
      ]);
      if (loadSeqRef.current !== seq) return;
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
      setOpDashboard(opDash);
      setSystemAlerts(sAlerts || []);
      setResourceCosts(rCosts);
      setMbDashboard(mbDash);
      setAiEnginesConfig(aiCfg);
      if (pilotRes) setPilotData(pilotRes);
      if (attrRes) setAnalyticsAttrData(attrRes);
      if (plRes) setPlansOverview(plRes);
      if (revRes) setRevenueIntel(revRes);
    } catch (err: any) {
      if (loadSeqRef.current === seq) {
        showNotice(err.message || "Falha ao carregar dados");
      }
    } finally {
      if (loadSeqRef.current === seq) {
        setLoading(false);
      }
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
              <h1 className="text-xl font-bold text-[var(--ug-text-primary)] tracking-tight">UNION GROWTH OS</h1>
              <p className="text-xs text-[var(--ug-text-muted)]">AI Business, CEO, Marketing, SEO & CRM Platform</p>
            </div>
          </div>

          <div className="flex gap-2 mb-6 bg-[var(--ug-bg)] border border-[var(--ug-border-subtle)] p-1 rounded-lg">
            <button
              type="button"
              onClick={() => setAuthMode("login")}
              className={`flex-1 py-2 text-xs font-semibold rounded-md transition ${
                authMode === "login" ? "bg-indigo-600 text-white" : "text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)]"
              }`}
            >
              Entrar no Sistema
            </button>
            <button
              type="button"
              onClick={() => setAuthMode("register")}
              className={`flex-1 py-2 text-xs font-semibold rounded-md transition ${
                authMode === "register" ? "bg-indigo-600 text-white" : "text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)]"
              }`}
            >
              Nova Empresa (Multi-Tenant)
            </button>
          </div>

          {authError && (
            <div role="alert" className="mb-4 p-3 rounded-lg bg-red-500/15 border border-red-500/40 text-red-400 text-xs">
              {authError}
            </div>
          )}

          <form onSubmit={handleAuthSubmit} className="space-y-4">
            {authMode === "register" && (
              <>
                <div>
                  <label htmlFor="ug-fullname" className="block text-xs text-[var(--ug-text-secondary)] mb-1">Seu Nome Completo</label>
                  <input
                    id="ug-fullname"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-sm text-[var(--ug-text-primary)]"
                    placeholder="Ex: Thiago Thomaz"
                  />
                </div>
                <div>
                  <label htmlFor="ug-company" className="block text-xs text-[var(--ug-text-secondary)] mb-1">Nome da Empresa / Marca</label>
                  <input
                    id="ug-company"
                    required
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-sm text-[var(--ug-text-primary)]"
                    placeholder="Ex: Union Digital Ltda"
                  />
                </div>
              </>
            )}
            <div>
              <label htmlFor="ug-email" className="block text-xs text-[var(--ug-text-secondary)] mb-1">E-mail Corporativo</label>
              <input
                id="ug-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-sm text-[var(--ug-text-primary)]"
              />
            </div>
            <div>
              <label htmlFor="ug-password" className="block text-xs text-[var(--ug-text-secondary)] mb-1">Senha de Acesso</label>
              <input
                id="ug-password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[var(--ug-bg)] border border-[var(--ug-border)] text-sm text-[var(--ug-text-primary)]"
              />
            </div>
            <button
              type="submit"
              className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition"
            >
              {authMode === "login" ? "Acessar Central Executiva" : "Criar Workspace & Ativar 12 Agentes"}
            </button>
          </form>

          <div className="mt-5 pt-4 border-t border-[var(--ug-border)] text-[11px] text-[var(--ug-text-muted)] space-y-2">
            <div className="flex items-center justify-between">
              <p className="font-semibold text-[var(--ug-text-secondary)]">Credenciais Executivas Padrão:</p>
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
              E-mail: <code className="text-indigo-400 font-mono">admin@projetosunion.cloud</code>
            </p>
            <p>
              Senha: <code className="text-indigo-400 font-mono font-bold">UnionGrowth#2026!</code>
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
                id="ug-version-badge-btn"
                type="button"
                onClick={() => setReleaseDrawerOpen(true)}
                aria-label={`Versão ${versionInfo?.version || "2.4.0"} — Abrir histórico de releases e ambiente`}
                className="px-2.5 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 text-[11px] font-medium inline-flex items-center gap-1.5 transition"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" aria-hidden="true" />
                <span className="font-mono font-semibold">v{versionInfo?.version || "2.4.0"}</span>
                <span className="hidden xl:inline text-emerald-300/80">
                  • {versionInfo?.environment_label || "PRODUCTION | STABLE"}
                </span>
                {versionInfo?.short_commit && (
                  <span className="hidden 2xl:inline font-mono text-[10px] text-emerald-200/70">
                    • {versionInfo.short_commit}
                  </span>
                )}
              </button>

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

          {/* ÁREAS MODULARES DS 4.0 — IA, CEO, MARKETING, SEO, SOCIAL & GROWTH CENTER */}
          {(activeMenu === "ceo" || activeMenu === "ceo_plan" || activeMenu === "operational247" || activeMenu === "pilot7d") && (
            <AIAutonomyAndOpsWorkspace
              mode={activeMenu}
              meData={meData}
              ceoData={ceoData || { briefings: [], goals: [] }}
              goalTitle={goalTitle}
              setGoalTitle={setGoalTitle}
              goalPeriod={goalPeriod}
              setGoalPeriod={setGoalPeriod}
              goalMetric={goalMetric}
              goalTarget={goalTarget}
              setGoalTarget={setGoalTarget}
              ceoDailyPlan={ceoDailyPlan}
              setCeoDailyPlan={setCeoDailyPlan}
              opDashboard={opDashboard}
              systemAlerts={systemAlerts}
              pilotData={pilotData}
              setPilotData={setPilotData}
              automationsData={automationsData}
              approvalsData={approvalsData}
              uiMode={uiMode}
              setUiMode={setUiMode}
              setLoading={setLoading}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              showNotice={showNotice}
            />
          )}

          {activeMenu === "marketing" && marketingData && (
            <MarketingCampaignsWorkspace
              marketingData={marketingData}
              personaName={personaName}
              setPersonaName={setPersonaName}
              personaRole={personaRole}
              personaVP={personaVP}
              setPersonaVP={setPersonaVP}
              campName={campName}
              setCampName={setCampName}
              campType={campType}
              setCampType={setCampType}
              campChannel={campChannel}
              setCampChannel={setCampChannel}
              campBudget={campBudget}
              setCampBudget={setCampBudget}
              campFilter={campFilter}
              setCampFilter={setCampFilter}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              showNotice={showNotice}
            />
          )}

          {activeMenu === "seo" && seoData && (
            <SEOWorkspace
              seoData={seoData}
              seoUrlInput={seoUrlInput}
              setSeoUrlInput={setSeoUrlInput}
              seoKwInput={seoKwInput}
              setSeoKwInput={setSeoKwInput}
              seoTopicInput={seoTopicInput}
              setSeoTopicInput={setSeoTopicInput}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              showNotice={showNotice}
            />
          )}

          {(activeMenu === "social" || activeMenu === "calendar" || activeMenu === "content_factory") && (
            <SocialAndContentWorkspace
              mode={activeMenu === "content_factory" ? "content_factory" : "social"}
              meData={meData}
              marketingData={marketingData}
              calendarData={calendarData}
              contentFactoryItems={contentFactoryItems}
              cfFilter={cfFilter}
              setCfFilter={setCfFilter}
              cfFocusTheme={cfFocusTheme}
              setCfFocusTheme={setCfFocusTheme}
              cfReplaceDrafts={cfReplaceDrafts}
              setCfReplaceDrafts={setCfReplaceDrafts}
              setAssistedPackage={setAssistedPackage}
              calTitle={calTitle}
              setCalTitle={setCalTitle}
              calPlatform={calPlatform}
              setCalPlatform={setCalPlatform}
              calFormat={calFormat}
              setCalFormat={setCalFormat}
              calDate={calDate}
              setCalDate={setCalDate}
              setLoading={setLoading}
              navigateTo={navigateTo}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              showNotice={showNotice}
            />
          )}

          {(activeMenu === "creative" || activeMenu === "copywriter" || activeMenu === "growth") && (
            <CreativeCopyAndGrowthLabWorkspace
              mode={activeMenu}
              meData={meData}
              creativeData={creativeData}
              creativeTitle={creativeTitle}
              setCreativeTitle={setCreativeTitle}
              creativeType={creativeType}
              setCreativeType={setCreativeType}
              creativeHeadline={creativeHeadline}
              setCreativeHeadline={setCreativeHeadline}
              creativeCta={creativeCta}
              copyData={copyData}
              copyTitle={copyTitle}
              setCopyTitle={setCopyTitle}
              copyType={copyType}
              setCopyType={setCopyType}
              copyFramework={copyFramework}
              setCopyFramework={setCopyFramework}
              copyOffer={copyOffer}
              setCopyOffer={setCopyOffer}
              copyBenefit={copyBenefit}
              setCopyBenefit={setCopyBenefit}
              growthData={growthData}
              expTitle={expTitle}
              setExpTitle={setExpTitle}
              expChannel={expChannel}
              setExpChannel={setExpChannel}
              expHyp={expHyp}
              setExpHyp={setExpHyp}
              expObj={expObj}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              onNavigate={navigateTo}
              showNotice={showNotice}
            />
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

          {/* ÁREAS MODULARES DS 4.0 — FINANCEIRO, CS, AUTOMAÇÕES, RELATÓRIOS, INTEGRAÇÕES, CONFIG & MULTI-BUSINESS */}
          {((activeMenu === "finance" && financeData) || (activeMenu === "reports" && reportsData)) && (
            <FinanceAndReportsWorkspace
              mode={activeMenu}
              financeData={financeData}
              finType={finType}
              setFinType={setFinType}
              finAmount={finAmount}
              setFinAmount={setFinAmount}
              finDesc={finDesc}
              setFinDesc={setFinDesc}
              finOrigin={finOrigin}
              setFinOrigin={setFinOrigin}
              reportsData={reportsData}
              analyticsAttrData={analyticsAttrData}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              showNotice={showNotice}
            />
          )}

          {activeMenu === "cs" && csData && (
            <CustomerSuccessWorkspace
              csData={csData}
              csName={csName}
              setCsName={setCsName}
              csEmail={csEmail}
              setCsEmail={setCsEmail}
              csNps={csNps}
              setCsNps={setCsNps}
              csText={csText}
              setCsText={setCsText}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              showNotice={showNotice}
            />
          )}

          {((activeMenu === "automations" && automationsData) || activeMenu === "approvals") && (
            <AIAutonomyAndOpsWorkspace
              mode={activeMenu}
              meData={meData}
              ceoData={ceoData}
              goalTitle={goalTitle}
              setGoalTitle={setGoalTitle}
              goalPeriod={goalPeriod}
              setGoalPeriod={setGoalPeriod}
              goalMetric={goalMetric}
              goalTarget={goalTarget}
              setGoalTarget={setGoalTarget}
              ceoDailyPlan={ceoDailyPlan}
              setCeoDailyPlan={setCeoDailyPlan}
              opDashboard={opDashboard}
              systemAlerts={systemAlerts}
              pilotData={pilotData}
              setPilotData={setPilotData}
              automationsData={automationsData}
              approvalsData={approvalsData}
              uiMode={uiMode}
              setUiMode={setUiMode}
              setLoading={setLoading}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              showNotice={showNotice}
            />
          )}

          {((activeMenu === "integrations") || (activeMenu === "settings" && meData) || (activeMenu === "audit" && auditData)) && (
            <IntegrationsAndSettingsWorkspace
              mode={activeMenu}
              meData={meData}
              integrationsData={integrationsData}
              intgStatusFilter={intgStatusFilter}
              setIntgStatusFilter={setIntgStatusFilter}
              credInputs={credInputs}
              credFieldInputs={credFieldInputs}
              setCredFieldInputs={setCredFieldInputs}
              plansOverview={plansOverview}
              editCompanyName={editCompanyName}
              setEditCompanyName={setEditCompanyName}
              editBrandName={editBrandName}
              setEditBrandName={setEditBrandName}
              editDomain={editDomain}
              setEditDomain={setEditDomain}
              editNiche={editNiche}
              setEditNiche={setEditNiche}
              editAudience={editAudience}
              setEditAudience={setEditAudience}
              newTenantName={newTenantName}
              setNewTenantName={setNewTenantName}
              auditData={auditData}
              apiFetch={apiFetch}
              onReload={loadAllActiveData}
              showNotice={showNotice}
            />
          )}

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

      {assistedPackage && (
        <div className="fixed inset-0 bg-black/75 flex items-center justify-center p-4 z-50" role="dialog" aria-modal="true" aria-label="Pacote de Publicação Assistida">
          <div className="ug-card rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl text-xs">
            <div className="flex items-center justify-between border-b border-[var(--ug-border-subtle)] pb-3">
              <h3 className="text-sm font-bold text-[var(--ug-text-primary)]">
                Pacote de Publicação Assistida (1 Clique) — {String(assistedPackage.channel || "").toUpperCase()}
              </h3>
              <button type="button" onClick={() => setAssistedPackage(null)} aria-label="Fechar pacote assistido" className="text-[var(--ug-text-muted)] hover:text-[var(--ug-text-primary)] text-base font-bold">✕</button>
            </div>
            <div className="space-y-2">
              <label htmlFor="ug-assisted-copy" className="text-[var(--ug-text-secondary)] font-semibold block">Legenda Formatada com Hashtags:</label>
              <textarea id="ug-assisted-copy" readOnly rows={6} value={assistedPackage.formatted_copy_for_clipboard || ""} className="w-full bg-[var(--ug-bg)] border border-[var(--ug-border)] rounded-lg p-3 text-[var(--ug-text-primary)] text-xs font-mono" />
              <button
                type="button"
                onClick={() => {
                  navigator.clipboard.writeText(assistedPackage.formatted_copy_for_clipboard || "");
                  showNotice("Texto copiado para a área de transferência com sucesso!");
                }}
                className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs"
              >
                Copiar Texto Completo para o Clipboard
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              {assistedPackage.media_download_url && (
                <a href={assistedPackage.media_download_url} target="_blank" rel="noopener noreferrer" className="py-2 px-3 rounded-lg border border-[var(--ug-border)] text-center text-[var(--ug-text-primary)] hover:bg-white/[0.04] font-medium">
                  Baixar Mídia / Arte PNG
                </a>
              )}
              {assistedPackage.platform_upload_url && (
                <a href={assistedPackage.platform_upload_url} target="_blank" rel="noopener noreferrer" className="py-2 px-3 rounded-lg border border-indigo-500/30 text-center text-indigo-400 hover:bg-indigo-500/10 font-medium">
                  Abrir Canal para Publicar →
                </a>
              )}
            </div>
            {Array.isArray(assistedPackage.checklist) && assistedPackage.checklist.length > 0 && (
              <ul className="space-y-1 text-[11px] text-[var(--ug-text-muted)] list-disc pl-4">
                {assistedPackage.checklist.map((c: string, i: number) => <li key={i}>{c}</li>)}
              </ul>
            )}
          </div>
        </div>
      )}

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

      <ReleaseHistoryDrawer
        open={releaseDrawerOpen}
        onClose={() => setReleaseDrawerOpen(false)}
        versionInfo={versionInfo}
        apiFetch={apiFetch}
        onNavigate={(view) => {
          setReleaseDrawerOpen(false);
          navigateTo(view);
        }}
      />

      <ToastBanner
        message={toast}
        onClose={() => setToast("")}
      />
    </div>
  );
}
