"""
FASE 25 — GLOBAL PRODUCT AUDIT, REVENUE INTELLIGENCE, PLG PLANS, SEO SIGNALS & UX/UI E2E
Executa em Chrome real contra produção (https://automacao.projetosunion.cloud) isolado em QA_AUTOMATED_TENANT.
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
OUT_DIR = ROOT_DIR / "UNION_GROWTH_OS_PHASE25_EVIDENCE"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROD_URL = "https://automacao.projetosunion.cloud"
CDP_PORT = 9344


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

    async def click_aria(self, prefix: str) -> bool:
        ok = bool(
            await self.evaluate(
                f"(() => {{ const el = Array.from(document.querySelectorAll('button')).find(b => (b.getAttribute('aria-label') || '').includes({json.dumps(prefix)})); if (!el) return false; el.click(); return true; }})()"
            )
        )
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

    async def wait_idle(self, timeout_s: float = 15.0):
        for _ in range(int(timeout_s / 0.4)):
            await asyncio.sleep(0.4)
            busy = await self.evaluate("document.querySelector('button[aria-label=\"Atualizar Dados\"]')?.getAttribute('data-loading') === 'true'")
            if not busy:
                return True
        return False

    async def close(self):
        self._reader_task.cancel()


async def run_phase25_e2e():
    tmp_profile = tempfile.mkdtemp(prefix="ugos_p25_cdp_")
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

    report = {
        "prod_url": PROD_URL,
        "checks": {},
        "accessibility": {},
        "viewports": {},
        "screenshots": [],
        "telemetry": {},
    }

    try:
        async with websockets.connect(ws_url, max_size=25 * 1024 * 1024) as ws:
            cdp = CDPClient(ws)
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")
            await cdp.send("Console.enable")
            await cdp.send("Network.enable")
            await cdp.set_viewport(1920, 1080, False)

            t0 = time.time()
            await cdp.send("Page.navigate", {"url": f"{PROD_URL}/"})
            await asyncio.sleep(3.2)
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
            await asyncio.sleep(4.5)
            await cdp.wait_idle()

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
            await asyncio.sleep(2.0)
            await cdp.wait_idle()

            # 1. Home + TTFV + ASK UNION
            sh1 = await cdp.screenshot("01_phase25_home_dark.png")
            if sh1:
                report["screenshots"].append(sh1)

            # 2. Comercial -> Leads & CRM (Revenue Intelligence) + Light Mode Check
            await cdp.click_by_text("aside button", "Comercial")
            await cdp.wait_idle()
            crm_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Leads Quentes em Entrada') && t.includes('Negociações Paradas') && t.includes('Taxa de Conversão');
                })()
            """)
            sh2 = await cdp.screenshot("02_phase25_crm_revenue_intel.png")
            if sh2:
                report["screenshots"].append(sh2)

            await cdp.click_aria("Ativar Modo Claro")
            await asyncio.sleep(0.45)
            light_crm_ok = await cdp.evaluate("document.documentElement.classList.contains('light')")
            sh8 = await cdp.screenshot("08_phase25_light_mode_crm.png")
            if sh8:
                report["screenshots"].append(sh8)
            await cdp.click_aria("Ativar Modo Escuro")
            await asyncio.sleep(0.4)

            # 3. Pipeline & Vendas DS 3.0
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Pipeline & Vendas")
            await asyncio.sleep(0.45)
            pipe_ok = await cdp.evaluate("(document.querySelector('main')?.innerText || '').includes('Nova Negociação no Pipeline')")
            sh3 = await cdp.screenshot("03_phase25_pipeline_ds3.png")
            if sh3:
                report["screenshots"].append(sh3)

            # 4. Propostas, Contratos & 3 Unidades DS 3.0 (collapsed 17-stage noise funnel)
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Propostas, Contratos & 3 Unidades")
            await cdp.wait_idle()
            mb_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Propostas PDF & Fechamento') && t.includes('Ver funil (') && !t.includes('VISITANTE');
                })()
            """)
            sh4 = await cdp.screenshot("04_phase25_multibusiness_ds3.png")
            if sh4:
                report["screenshots"].append(sh4)

            # 5. Marketing -> SEO & Artigos (Technical Signals)
            await cdp.click_by_text("aside button", "Marketing")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "SEO & Artigos")
            await asyncio.sleep(0.45)
            await cdp.set_input('input[placeholder="https://seudominio.com.br"]', "https://automacao.projetosunion.cloud")
            await cdp.click_by_text("main button", "Executar Auditoria Técnica Real")
            await asyncio.sleep(2.5)
            await cdp.wait_idle()
            seo_sig_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Canonical:') && t.includes('Mobile Viewport:') && t.includes('OpenGraph:');
                })()
            """)
            sh5 = await cdp.screenshot("05_phase25_seo_technical_signals.png")
            if sh5:
                report["screenshots"].append(sh5)

            # 6. IA -> Visão & Agentes + Motores & Provedores DS 3.0
            await cdp.click_by_text("aside button", "Inteligência Artificial")
            await asyncio.sleep(0.45)
            await cdp.click_by_text("main button", "Avançado: ver todos os serviços de IA")
            await asyncio.sleep(0.5)
            ai_hub_ok = await cdp.evaluate("(document.querySelector('main')?.innerText || '').includes('UNION AI ENGINE HUB')")
            sh6 = await cdp.screenshot("06_phase25_ai_hub_honest.png")
            if sh6:
                report["screenshots"].append(sh6)

            # 7. Gestão -> Configurações & Planos (5 Tiers PLG + Usage Meters)
            await cdp.click_by_text("aside button", "Gestão")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Configurações & Planos")
            await asyncio.sleep(0.5)
            plg_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Planos PLG & Consumo do Workspace') && t.includes('Free (Ativação PLG)') && t.includes('Pro (Recomendado');
                })()
            """)
            sh7 = await cdp.screenshot("07_phase25_settings_plg_plans.png")
            if sh7:
                report["screenshots"].append(sh7)

            # 8. Accessibility & 7 Viewports
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
                        passed: document.documentElement.lang === 'pt-BR' && unlabeledBtns.length === 0 && unlabeledInputs.length === 0
                    };
                })()
            """)
            report["accessibility"] = a11y or {}

            vp_list = [
                ("desktop_1920x1080", 1920, 1080, False),
                ("desktop_1440x900", 1440, 900, False),
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
                report["viewports"][name] = {
                    "scrollWidth": (m or {}).get("sw"),
                    "clientWidth": (m or {}).get("cw"),
                    "overflowPx": ov,
                    "passed": ov == 0,
                }
                if name == "mobile_small_360x800":
                    sh9 = await cdp.screenshot("09_phase25_viewport_mobile_360x800.png")
                    if sh9:
                        report["screenshots"].append(sh9)

            report["checks"] = {
                "switched_qa": bool(switched_qa),
                "crm_revenue_intel_ok": bool(crm_ok),
                "light_mode_crm_ok": bool(light_crm_ok),
                "pipeline_ds3_ok": bool(pipe_ok),
                "multibusiness_ds3_ok": bool(mb_ok),
                "seo_technical_signals_ok": bool(seo_sig_ok),
                "ai_hub_ds3_ok": bool(ai_hub_ok),
                "plg_plans_and_meters_ok": bool(plg_ok),
                "total_elapsed_s": round(time.time() - t0, 2),
            }
            report["telemetry"] = {
                "console_errors_count": len(cdp.console_errors),
                "exceptions_count": len(cdp.exceptions),
                "network_4xx_5xx_count": len(cdp.network_4xx_5xx),
                "url_token_leaks_count": len(cdp.url_token_leaks),
                "network_4xx_5xx": cdp.network_4xx_5xx,
            }
            report["all_phase25_e2e_passed"] = (
                bool(switched_qa and crm_ok and light_crm_ok and pipe_ok and mb_ok and seo_sig_ok and ai_hub_ok and plg_ok)
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

    out_path = OUT_DIR / "phase25_cdp_e2e.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["all_phase25_e2e_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(run_phase25_e2e())
