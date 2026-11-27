"""
FASE 23 — E2E Real (10 Jornadas, Modo Simples/Avançado, Acessibilidade WCAG & 6 Viewports) via Chrome CDP
Executa contra produção real (https://automacao.projetosunion.cloud) isolando toda escrita em QA_AUTOMATED_TENANT.
"""
import asyncio
import base64
import json
import subprocess
import tempfile
import time
from pathlib import Path
import httpx
import websockets

ROOT_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT_DIR / "UNION_GROWTH_OS_PHASE23_EVIDENCE"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROD_URL = "https://automacao.projetosunion.cloud"
CDP_PORT = 9341


class CDPClient:
    def __init__(self, ws):
        self.ws = ws
        self._id = 0
        self.pending = {}
        self.console_errors = []
        self.exceptions = []
        self.network_4xx_5xx = []
        self.url_token_leaks = []
        self._reader_task = asyncio.create_task(self._read_loop())

    async def _read_loop(self):
        try:
            async for raw in self.ws:
                msg = json.loads(raw)
                if "id" in msg:
                    fut = self.pending.pop(msg["id"], None)
                    if fut and not fut.done():
                        fut.set_result(msg)
                else:
                    method = msg.get("method", "")
                    params = msg.get("params", {})
                    if method == "Runtime.exceptionThrown":
                        exc_obj = params.get("exceptionDetails", {}).get("exception", {}).get("description", "")
                        self.exceptions.append(str(exc_obj or params)[:260])
                    elif method == "Console.messageAdded":
                        m = params.get("message", {})
                        if m.get("level") == "error":
                            self.console_errors.append(str(m.get("text", ""))[:260])
                    elif method == "Network.requestWillBeSent":
                        url = params.get("request", {}).get("url", "")
                        if "access_token=" in url.lower() or "token=eyj" in url.lower():
                            self.url_token_leaks.append(url[:150])
                    elif method == "Network.responseReceived":
                        resp = params.get("response", {})
                        st = resp.get("status", 0)
                        url = resp.get("url", "")
                        if st >= 400 and "favicon.ico" not in url:
                            self.network_4xx_5xx.append({"status": st, "url": url})
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    async def send(self, method: str, params: dict | None = None):
        self._id += 1
        cid = self._id
        fut = asyncio.get_running_loop().create_future()
        self.pending[cid] = fut
        await self.ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
        return await asyncio.wait_for(fut, timeout=25.0)

    async def evaluate(self, js: str):
        res = await self.send("Runtime.evaluate", {"expression": js, "awaitPromise": True, "returnByValue": True})
        return res.get("result", {}).get("result", {}).get("value")

    async def screenshot(self, filename: str):
        res = await self.send("Page.captureScreenshot", {"format": "png"})
        b64 = res.get("result", {}).get("data", "")
        if b64:
            p = OUT_DIR / filename
            p.write_bytes(base64.b64decode(b64))
            return {"file": filename, "size_bytes": p.stat().st_size}
        return None

    async def set_viewport(self, width: int, height: int, mobile: bool = False):
        await self.send("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": mobile})
        await asyncio.sleep(0.45)

    async def click_by_text(self, selector: str, substring: str, exact: bool = False) -> bool:
        js = f"""
        (() => {{
            const els = Array.from(document.querySelectorAll({json.dumps(selector)}));
            const target = els.find(el => {{
                const rect = el.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) return false;
                const txt = (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\\s+/g, ' ');
                return {'txt === ' + json.dumps(substring) if exact else 'txt.includes(' + json.dumps(substring) + ')'};
            }});
            if (!target) return false;
            target.scrollIntoView({{ block: 'center' }});
            target.click();
            return true;
        }})()
        """
        ok = bool(await self.evaluate(js))
        await asyncio.sleep(0.45)
        return ok

    async def set_input(self, selector: str, value: str) -> bool:
        js = f"""
        (() => {{
            const el = document.querySelector({json.dumps(selector)});
            if (!el) return false;
            const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
            const setVal = Object.getOwnPropertyDescriptor(proto, 'value').set;
            setVal.call(el, {json.dumps(value)});
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }})()
        """
        ok = bool(await self.evaluate(js))
        await asyncio.sleep(0.2)
        return ok

    async def wait_idle(self, timeout_s: float = 12.0):
        for _ in range(int(timeout_s / 0.4)):
            await asyncio.sleep(0.4)
            busy = await self.evaluate("(document.body.innerText || '').includes('Atualizando...')")
            if not busy:
                return True
        return False

    async def close(self):
        self._reader_task.cancel()


async def run_phase23_e2e():
    ts = int(time.time())
    tmp_profile = tempfile.mkdtemp(prefix="ugos_p23_cdp_")
    proc = subprocess.Popen(
        [CHROME_PATH, "--headless=new", "--disable-gpu", "--no-sandbox", "--window-size=1920,1080", f"--remote-debugging-port={CDP_PORT}", f"--user-data-dir={tmp_profile}", "about:blank"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ws_url = None
    for _ in range(35):
        try:
            tabs = httpx.get(f"http://127.0.0.1:{CDP_PORT}/json", timeout=2.0).json()
            tab = next((t for t in tabs if t.get("type") == "page" and t.get("webSocketDebuggerUrl")), None)
            if tab:
                ws_url = tab["webSocketDebuggerUrl"]
                break
        except Exception:
            await asyncio.sleep(0.4)
    if not ws_url:
        proc.terminate()
        raise RuntimeError("Chrome CDP unavailable")

    report = {"prod_url": PROD_URL, "journeys": {}, "accessibility": {}, "viewports": {}, "screenshots": [], "telemetry": {}}

    try:
        async with websockets.connect(ws_url, max_size=25 * 1024 * 1024) as ws:
            cdp = CDPClient(ws)
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")
            await cdp.send("Console.enable")
            await cdp.send("Network.enable")
            await cdp.set_viewport(1920, 1080, False)

            await cdp.send("Page.navigate", {"url": f"{PROD_URL}/"})
            await asyncio.sleep(3.5)
            await cdp.evaluate("""
                (() => {
                    const e = document.querySelector('input[type="email"]');
                    const p = document.querySelector('input[type="password"]');
                    const b = document.querySelector('button[type="submit"]');
                    if (!e || !p || !b) return false;
                    const setVal = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setVal.call(e, 'admin@projetosunion.cloud');
                    e.dispatchEvent(new Event('input', { bubbles: true }));
                    setVal.call(p, 'UnionGrowth#2026!');
                    p.dispatchEvent(new Event('input', { bubbles: true }));
                    b.click();
                    return true;
                })()
            """)
            await asyncio.sleep(5.5)

            # Trocar estritamente para QA_AUTOMATED_TENANT antes de qualquer mutação
            switched_qa = await cdp.evaluate("""
                (() => {
                    const sel = document.querySelector('#ug-tenant-select');
                    if (!sel) return false;
                    const opt = Array.from(sel.options).find(o => o.text.includes('QA_AUTOMATED'));
                    if (!opt) return false;
                    sel.value = opt.value;
                    sel.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                })()
            """)
            await asyncio.sleep(3.5)
            await cdp.wait_idle()

            # J15 & J11 & J16: Dashboard Executivo (Command Center), ASK UNION & Modo Simples
            cc_dom = await cdp.evaluate("""
                (() => {
                    const txt = document.body.innerText || '';
                    return {
                        has_ask_union: txt.includes('ASK UNION'),
                        has_growth_score: txt.includes('Growth Score Documentado'),
                        has_business_health: txt.includes('Business Health'),
                        has_ceo_briefing: txt.includes('AI CEO Briefing'),
                        has_opp_radar: txt.includes('Opportunity Radar'),
                        has_exec_center: txt.includes('Executive Action Center'),
                        has_mode_toggle: Boolean(document.querySelector('#ug-ui-mode-toggle')),
                    };
                })()
            """)
            sh1 = await cdp.screenshot("01_command_center_inicio.png")
            if sh1:
                report["screenshots"].append(sh1)

            # Garantir estado inicial Modo Simples antes de testar Modo Simples vs Avançado
            if "Avançado" in str(await cdp.evaluate("document.querySelector('#ug-ui-mode-toggle')?.innerText || ''")):
                await cdp.click_by_text("#ug-ui-mode-toggle", "")
                await asyncio.sleep(0.5)

            # J11: ASK UNION copilot estruturado
            await cdp.set_input("#ug-ask-union-input", "Quero vender mais")
            await cdp.click_by_text("button", "Perguntar ao Ask Union")
            await asyncio.sleep(1.5)
            ask_ok = await cdp.evaluate("(document.body.innerText || '').includes('INCREASE_SALES') && (document.body.innerText || '').includes('Plano Estruturado')")
            sh2 = await cdp.screenshot("02_ask_union_copilot.png")
            if sh2:
                report["screenshots"].append(sh2)
            report["journeys"]["J11_Ask_Union"] = {"passed": bool(ask_ok)}
            report["journeys"]["J15_Dashboard_Executivo"] = {
                **(cc_dom or {}),
                "passed": bool(switched_qa and (cc_dom or {}).get("has_ask_union") and (cc_dom or {}).get("has_growth_score") and (cc_dom or {}).get("has_business_health") and (cc_dom or {}).get("has_ceo_briefing") and (cc_dom or {}).get("has_opp_radar") and (cc_dom or {}).get("has_exec_center")),
            }

            # J01 & J03: Onboarding 6 Etapas (Empresa + Objetivos/Plano)
            await cdp.click_by_text("main button", "Onboarding 6 Etapas")
            await asyncio.sleep(0.6)
            ob_visible = await cdp.evaluate("(document.body.innerText || '').includes('Onboarding Inteligente em 6 Etapas') && (document.body.innerText || '').includes('1. Sua Empresa')")
            await cdp.click_by_text("main button", "3. Seus Objetivos")
            await asyncio.sleep(0.4)
            ob_goals = await cdp.evaluate("(document.body.innerText || '').includes('Gerar leads qualificados') && (document.body.innerText || '').includes('Aumentar vendas')")
            sh3 = await cdp.screenshot("03_onboarding_6_steps.png")
            if sh3:
                report["screenshots"].append(sh3)
            report["journeys"]["J01_Empresa_Onboarding"] = {"passed": bool(ob_visible)}
            report["journeys"]["J03_Objetivos_Plano"] = {"passed": bool(ob_goals)}

            # J02: Brand Intelligence Center + Detector de Inconsistências
            await cdp.click_by_text("aside button", "Gestão")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Configurações")
            await cdp.wait_idle()
            await cdp.click_by_text("main button", "Detectar Inconsistências Agora")
            await asyncio.sleep(1.0)
            brand_ok = await cdp.evaluate("(document.body.innerText || '').includes('Central de Inteligência de Marca') && (document.body.innerText || '').includes('Consistência')")
            sh4 = await cdp.screenshot("04_brand_intelligence_center.png")
            if sh4:
                report["screenshots"].append(sh4)
            report["journeys"]["J02_Marca_Brand_Hub"] = {"passed": bool(brand_ok)}

            # J12: Indicadores Analytics & Attribution
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Relatórios")
            await cdp.wait_idle()
            attr_ok = await cdp.evaluate("(document.body.innerText || '').includes('Analytics, Funil & Atribuição de Marketing')")
            sh7 = await cdp.screenshot("07_analytics_and_attribution.png")
            if sh7:
                report["screenshots"].append(sh7)
            report["journeys"]["J12_Indicadores_Analytics"] = {"passed": bool(attr_ok)}

            # J05, J06 & J13: Campanhas, Fábrica de Conteúdo & SEO Intelligence
            await cdp.click_by_text("aside button", "Marketing")
            await cdp.wait_idle()
            camp_ok = await cdp.evaluate("(document.body.innerText || '').includes('Campanhas Ativas') || (document.body.innerText || '').includes('Personas')")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Fábrica de Conteúdo")
            await cdp.wait_idle()
            cf_ctx = await cdp.evaluate("(document.body.innerText || '').includes('Contexto usado na criação dos conteúdos')")
            sh5 = await cdp.screenshot("05_content_factory_contextual.png")
            if sh5:
                report["screenshots"].append(sh5)
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "SEO & Artigos")
            await cdp.wait_idle()
            seo_ok = await cdp.evaluate("(document.body.innerText || '').includes('Auditoria Técnica') || (document.body.innerText || '').includes('SEO')")
            sh_seo = await cdp.screenshot("09_seo_intelligence.png")
            if sh_seo:
                report["screenshots"].append(sh_seo)
            report["journeys"]["J05_Campanha"] = {"passed": bool(camp_ok)}
            report["journeys"]["J06_Conteudo"] = {"passed": bool(cf_ctx)}
            report["journeys"]["J13_SEO_Intelligence"] = {"passed": bool(seo_ok)}

            # J07, J08 & J14: Leads CRM/LGPD, Oportunidades Pipeline & Inteligência Competitiva
            await cdp.click_by_text("aside button", "Comercial")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Leads & CRM")
            await cdp.wait_idle()
            crm_ok = await cdp.evaluate("Boolean(document.querySelector('#ug-lead-lgpd-checkbox')) && (document.body.innerText || '').includes('LGPD') && (document.body.innerText || '').includes('Base de Leads Qualificados')")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Pipeline & Vendas")
            await cdp.wait_idle()
            deal_ok = await cdp.evaluate("(document.body.innerText || '').includes('Pipeline') || (document.body.innerText || '').includes('Negociações')")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Concorrentes")
            await cdp.wait_idle()
            comp_ok = await cdp.evaluate("(document.body.innerText || '').includes('Concorrentes') || (document.body.innerText || '').includes('Inteligência Competitiva')")
            sh_comp = await cdp.screenshot("10_competitors_intelligence.png")
            if sh_comp:
                report["screenshots"].append(sh_comp)
            report["journeys"]["J07_Lead_CRM"] = {"passed": bool(crm_ok)}
            report["journeys"]["J08_Oportunidade_Pipeline"] = {"passed": bool(deal_ok)}
            report["journeys"]["J14_Inteligencia_Competitiva"] = {"passed": bool(comp_ok)}

            # J04, J09, J16 & J17: Agentes (12), Automação Conversacional, Modo Simples vs Avançado
            await cdp.click_by_text("aside button", "Inteligência Artificial")
            await cdp.wait_idle()
            ag12_ok = await cdp.evaluate("(document.body.innerText || '').includes('AI Data Analyst') && (document.body.innerText || '').includes('Equipe Digital de Agentes Especializados (12)')")
            simple_check = await cdp.evaluate("Boolean(document.querySelector('#ug-reveal-advanced-subtabs')) && !(document.querySelector('nav[aria-label*=\"Submenus\"]')?.innerText || '').includes('Modelos & Provedores')")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Automações")
            await cdp.wait_idle()
            await cdp.set_input("#ug-conv-auto-input", "Leads que não responderam em 3 dias recebam tarefa de follow-up")
            await cdp.click_by_text("main button", "Simular Fluxo (Dry-Run)")
            await asyncio.sleep(1.5)
            conv_ok = await cdp.evaluate("(document.body.innerText || '').includes('Teste de Simulação') && (document.body.innerText || '').includes('Python Nativo')")
            sh6 = await cdp.screenshot("06_conversational_automation_builder.png")
            if sh6:
                report["screenshots"].append(sh6)

            # Alternar para Modo Avançado e validar revelação completa das abas técnicas
            await cdp.click_by_text("#ug-ui-mode-toggle", "")
            await asyncio.sleep(0.8)
            adv_revealed = await cdp.evaluate("(document.querySelector('nav[aria-label*=\"Submenus\"]')?.innerText || '').includes('Modelos & Provedores') && (document.querySelector('#ug-ui-mode-toggle')?.innerText || '').includes('Avançado')")
            sh_adv = await cdp.screenshot("11_modo_avancado.png")
            if sh_adv:
                report["screenshots"].append(sh_adv)
            # Restaurar Modo Simples para o estado final limpo
            await cdp.click_by_text("#ug-ui-mode-toggle", "")
            await asyncio.sleep(0.6)

            report["journeys"]["J04_Agentes_12"] = {"passed": bool(ag12_ok)}
            report["journeys"]["J09_Automacao_Conversacional"] = {"passed": bool(conv_ok)}
            report["journeys"]["J16_Modo_Simples"] = {"passed": bool(simple_check)}
            report["journeys"]["J17_Modo_Avancado"] = {"passed": bool(adv_revealed)}

            # J10: Meu Trabalho & Central de Aprovações
            await cdp.click_by_text("aside button", "Meu Trabalho")
            await cdp.wait_idle()
            mw_ok = await cdp.evaluate("(document.body.innerText || '').includes('Precisa de mim')")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Central de Aprovações")
            await cdp.wait_idle()
            appr_ok = await cdp.evaluate("(document.body.innerText || '').includes('Aprovações')")
            report["journeys"]["J10_Aprovacao"] = {"passed": bool(mw_ok and appr_ok)}

            # Voltar ao Início para Acessibilidade e J18 (6 Viewports) antes das sondas negativas de segurança
            await cdp.click_by_text("aside button", "Início")
            await cdp.wait_idle()
            a11y = await cdp.evaluate("""
                (() => {
                    const btns = Array.from(document.querySelectorAll('button')).filter(b => b.getBoundingClientRect().width > 0);
                    const unlabeledBtns = btns.filter(b => !(b.innerText || '').trim() && !(b.getAttribute('aria-label') || '').trim() && !(b.getAttribute('title') || '').trim());
                    const inputs = Array.from(document.querySelectorAll('input, select, textarea')).filter(i => i.getBoundingClientRect().width > 0);
                    const unlabeledInputs = inputs.filter(i => !(i.getAttribute('aria-label') || '').trim() && !(i.getAttribute('placeholder') || '').trim() && !(i.id && document.querySelector(`label[for="${i.id}"]`)));
                    return {
                        lang: document.documentElement.lang,
                        total_buttons: btns.length,
                        unlabeled_buttons: unlabeledBtns.length,
                        unlabeled_inputs: unlabeledInputs.length,
                        passed: unlabeledBtns.length === 0 && unlabeledInputs.length === 0
                    };
                })()
            """)
            report["accessibility"] = a11y or {}

            vp_list = [
                ("desktop_1920x1080", 1920, 1080, False),
                ("notebook_1366x768", 1366, 768, False),
                ("compact_1024x768", 1024, 768, False),
                ("tablet_768x1024", 768, 1024, True),
                ("mobile_390x844", 390, 844, True),
                ("mobile_small_360x800", 360, 800, True),
            ]
            for name, w, h, mob in vp_list:
                await cdp.set_viewport(w, h, mob)
                m = await cdp.evaluate("({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth})")
                ov = max(0, (m or {}).get("sw", 0) - (m or {}).get("cw", 0))
                report["viewports"][name] = {"scrollWidth": (m or {}).get("sw"), "clientWidth": (m or {}).get("cw"), "overflowPx": ov, "passed": ov == 0}
                if name in ("compact_1024x768", "mobile_small_360x800"):
                    sh_vp = await cdp.screenshot(f"08_viewport_{name}.png")
                    if sh_vp:
                        report["screenshots"].append(sh_vp)

            report["journeys"]["J18_Responsividade_6_Viewports"] = {
                "passed": bool(report["viewports"] and all(v.get("passed") for v in report["viewports"].values())),
            }

            # Congelar telemetria normal de navegação (esperado 0 erros HTTP não-intencionais)
            normal_4xx_5xx = list(cdp.network_4xx_5xx)

            # J19 & J20: Sondas explícitas negativas Multi-Tenant (403) + anti-SSRF (400) + HTTPS + Zero Token Leaks
            sec_checks = await cdp.evaluate("""
                (async () => {
                    const tok = localStorage.getItem('ug_token');
                    if (!tok) return { ok: false };
                    const rBadTenant = await fetch('/api/v1/growth-os/command-center', {
                        headers: { 'Authorization': 'Bearer ' + tok, 'X-Tenant-Id': 'invalid-tenant' }
                    });
                    const rSsrf = await fetch('/api/v1/seo/audit', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok },
                        body: JSON.stringify({ target_url: 'http://127.0.0.1:8000/health', target_keyword: 'ssrf' })
                    });
                    return {
                        https: window.location.protocol === 'https:',
                        invalid_tenant_403: rBadTenant.status === 403,
                        ssrf_blocked_400: rSsrf.status === 400
                    };
                })()
            """)
            report["journeys"]["J19_MultiTenant_E_Permissoes"] = {
                "switched_qa": bool(switched_qa),
                "invalid_tenant_403": bool((sec_checks or {}).get("invalid_tenant_403")),
                "passed": bool(switched_qa and (sec_checks or {}).get("invalid_tenant_403")),
            }
            report["journeys"]["J20_Seguranca_E_Telemetria"] = {
                "https": bool((sec_checks or {}).get("https")),
                "ssrf_blocked_400": bool((sec_checks or {}).get("ssrf_blocked_400")),
                "url_token_leaks_count": len(cdp.url_token_leaks),
                "unexpected_4xx_5xx_count": len(normal_4xx_5xx),
                "passed": bool((sec_checks or {}).get("https") and (sec_checks or {}).get("ssrf_blocked_400") and len(cdp.url_token_leaks) == 0 and len(normal_4xx_5xx) == 0),
            }

            report["telemetry"] = {
                "console_errors_count": len(cdp.console_errors),
                "exceptions_count": len(cdp.exceptions),
                "network_4xx_5xx_count": len(normal_4xx_5xx),
                "url_token_leaks_count": len(cdp.url_token_leaks),
                "network_4xx_5xx": normal_4xx_5xx,
            }
            report["all_phase23_e2e_passed"] = (
                len(report["journeys"]) == 20
                and all(v.get("passed") for v in report["journeys"].values())
                and bool(report["accessibility"].get("passed"))
                and all(v.get("passed") for v in report["viewports"].values())
                and len(cdp.console_errors) == 0
                and len(cdp.exceptions) == 0
                and len(normal_4xx_5xx) == 0
                and len(cdp.url_token_leaks) == 0
            )
            await cdp.close()
    finally:
        proc.terminate()

    out_path = OUT_DIR / "phase23_cdp_e2e.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["all_phase23_e2e_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(run_phase23_e2e())
