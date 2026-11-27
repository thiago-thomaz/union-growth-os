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

            # J1 & J2 & J9 & J10: Command Center, Ask Union, Modo Simples vs Avançado, Onboarding 6 etapas
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

            # Testar Modo Avançado toggle + retorno a Modo Simples
            mode_toggled = await cdp.click_by_text("#ug-ui-mode-toggle", "")
            await asyncio.sleep(0.8)
            adv_text = await cdp.evaluate("document.querySelector('#ug-ui-mode-toggle')?.innerText || ''")
            await cdp.click_by_text("#ug-ui-mode-toggle", "")
            await asyncio.sleep(0.5)

            # Testar ASK UNION
            await cdp.set_input("#ug-ask-union-input", "Quero vender mais")
            await cdp.click_by_text("button", "Perguntar ao Ask Union")
            await asyncio.sleep(1.5)
            ask_ok = await cdp.evaluate("(document.body.innerText || '').includes('INCREASE_SALES') && (document.body.innerText || '').includes('Plano Estruturado')")
            sh2 = await cdp.screenshot("02_ask_union_copilot.png")
            if sh2:
                report["screenshots"].append(sh2)
            report["journeys"]["J01_CommandCenter_AskUnion_Modes"] = {
                "switched_qa": bool(switched_qa),
                **(cc_dom or {}),
                "mode_switched_to_advanced": "Avançado" in str(adv_text),
                "ask_union_structured_ok": bool(ask_ok),
                "passed": bool(switched_qa and (cc_dom or {}).get("has_ask_union") and (cc_dom or {}).get("has_growth_score") and ask_ok and "Avançado" in str(adv_text)),
            }

            # J02: Onboarding 6 Etapas
            await cdp.click_by_text("main button", "Onboarding 6 Etapas")
            await asyncio.sleep(0.6)
            ob_visible = await cdp.evaluate("(document.body.innerText || '').includes('Onboarding Inteligente em 6 Etapas')")
            sh3 = await cdp.screenshot("03_onboarding_6_steps.png")
            if sh3:
                report["screenshots"].append(sh3)
            report["journeys"]["J02_Progressive_Onboarding_6Steps"] = {"visible": bool(ob_visible), "passed": bool(ob_visible)}

            # J03: Brand Intelligence Center + Detector de Inconsistências (Gestão -> Configurações & Planos)
            await cdp.click_by_text("aside button", "Gestão")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Configurações")
            await cdp.wait_idle()
            await cdp.click_by_text("main button", "Detectar Inconsistências Agora")
            await asyncio.sleep(1.0)
            brand_ok = await cdp.evaluate("(document.body.innerText || '').includes('Central de Inteligência de Marca') && (document.body.innerText || '').includes('Consistência')")
            sh4 = await cdp.screenshot("04_brand_intelligence_center.png")
            if sh4:
                report["screenshots"].append(sh4)
            report["journeys"]["J03_Brand_Intelligence_And_Audit"] = {"passed": bool(brand_ok)}

            # J04 & J05: Marketing Campanhas + Fábrica de Conteúdo Contextual
            await cdp.click_by_text("aside button", "Marketing")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Fábrica de Conteúdo")
            await cdp.wait_idle()
            cf_ctx = await cdp.evaluate("(document.body.innerText || '').includes('Contexto usado na criação dos conteúdos')")
            sh5 = await cdp.screenshot("05_content_factory_contextual.png")
            if sh5:
                report["screenshots"].append(sh5)
            report["journeys"]["J04_J05_Marketing_And_Content_Factory"] = {"has_context_panel": bool(cf_ctx), "passed": bool(cf_ctx)}

            # J06: Comercial CRM
            await cdp.click_by_text("aside button", "Comercial")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "CRM")
            await cdp.wait_idle()
            crm_ok = await cdp.evaluate("(document.body.innerText || '').includes('Consentimento LGPD')")
            report["journeys"]["J06_CRM_And_LGPD"] = {"passed": bool(crm_ok)}

            # J07 & J08: AI Team (12 Agentes) + Conversational Automation Builder
            await cdp.click_by_text("aside button", "Inteligência Artificial")
            await cdp.wait_idle()
            ag12_ok = await cdp.evaluate("(document.body.innerText || '').includes('AI Data Analyst') || (document.body.innerText || '').includes('Equipe Digital de Agentes Especializados (12)')")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Automações")
            await cdp.wait_idle()
            await cdp.set_input("#ug-conv-auto-input", "Leads que não responderam em 3 dias recebam tarefa de follow-up")
            await cdp.click_by_text("main button", "Simular Fluxo (Dry-Run)")
            await asyncio.sleep(1.5)
            conv_ok = await cdp.evaluate("(document.body.innerText || '').includes('Teste de Simulação') && (document.body.innerText || '').includes('Python Nativo')")
            sh6 = await cdp.screenshot("06_conversational_automation_builder.png")
            if sh6:
                report["screenshots"].append(sh6)
            report["journeys"]["J07_J08_Agents12_And_Conversational_Automation"] = {"agents_12_ok": bool(ag12_ok), "conv_builder_ok": bool(conv_ok), "passed": bool(ag12_ok and conv_ok)}

            # J09: Meu Trabalho + Aprovações
            await cdp.click_by_text("aside button", "Meu Trabalho")
            await cdp.wait_idle()
            mw_ok = await cdp.evaluate("(document.body.innerText || '').includes('Precisa de mim')")
            report["journeys"]["J09_MyWork_And_Approvals"] = {"passed": bool(mw_ok)}

            # J10: Gestão -> Relatórios & Analytics Attribution
            await cdp.click_by_text("aside button", "Gestão")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Relatórios")
            await cdp.wait_idle()
            attr_ok = await cdp.evaluate("(document.body.innerText || '').includes('Analytics, Funil & Atribuição de Marketing')")
            sh7 = await cdp.screenshot("07_analytics_and_attribution.png")
            if sh7:
                report["screenshots"].append(sh7)
            report["journeys"]["J10_Analytics_And_Attribution"] = {"passed": bool(attr_ok)}

            # Voltar ao Início para Acessibilidade & 6 Viewports
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

            report["telemetry"] = {
                "console_errors_count": len(cdp.console_errors),
                "exceptions_count": len(cdp.exceptions),
                "network_4xx_5xx_count": len(cdp.network_4xx_5xx),
                "url_token_leaks_count": len(cdp.url_token_leaks),
                "network_4xx_5xx": cdp.network_4xx_5xx,
            }
            report["all_phase23_e2e_passed"] = (
                all(v.get("passed") for v in report["journeys"].values())
                and bool(report["accessibility"].get("passed"))
                and all(v.get("passed") for v in report["viewports"].values())
                and len(cdp.console_errors) == 0
                and len(cdp.exceptions) == 0
                and len(cdp.network_4xx_5xx) == 0
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
