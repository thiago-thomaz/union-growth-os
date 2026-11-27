"""
FASE 26 — PRODUCT TRANSFORMATION, GROWTH EXECUTION CENTER (0/7/30/90d), AGENTS MATRIX, REVENUE ENGINE & DS 4.0 E2E
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
OUT_DIR = ROOT_DIR / "UNION_GROWTH_OS_PHASE26_EVIDENCE"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROD_URL = "https://automacao.projetosunion.cloud"
CDP_PORT = 9346


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
        await asyncio.sleep(0.25)
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


async def run_phase26_e2e():
    tmp_profile = tempfile.mkdtemp(prefix="ugos_p26_cdp_")
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

            login_ok = await cdp.evaluate("""
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
            await asyncio.sleep(4.0)
            await cdp.wait_idle()

            # Switch exclusively to QA_AUTOMATED_TENANT before mutations
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

            # 1. Home DS 4.0 (attribution + Growth Execution Center CTA)
            home_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Growth Score') && t.includes('Prioridades de hoje') && t.includes('Centro de Crescimento (0–90d)');
                })()
            """)
            sh1 = await cdp.screenshot("01_phase26_home_ds4.png")
            if sh1:
                report["screenshots"].append(sh1)

            # 2. Centro de Crescimento 0/7/30/90 dias
            await cdp.click_by_text("main button", "Centro de Crescimento (0–90d)")
            await asyncio.sleep(0.8)
            await cdp.click_by_text("main button", "Gerar Plano 0–90d")
            await asyncio.sleep(2.0)
            await cdp.wait_idle()
            growth_center_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Centro de Crescimento Executivo') && t.includes('Plano de Execução Priorizado') && t.includes('Hoje') && t.includes('90 Dias');
                })()
            """)
            sh2 = await cdp.screenshot("02_phase26_growth_center_0_90d.png")
            if sh2:
                report["screenshots"].append(sh2)

            # 3. AI Agents Matrix (classificacao real sem disfarces)
            await cdp.click_by_text("aside button", "Inteligência Artificial")
            await asyncio.sleep(1.5)
            await cdp.wait_idle()
            agents_matrix_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Classificação Técnica Auditada') && t.includes('Híbridos') && t.includes('Determinísticos') && t.includes('Simulados: 0') && t.includes('HYBRID') && t.includes('DETERMINISTIC');
                })()
            """)
            sh3 = await cdp.screenshot("03_phase26_agents_matrix_honest.png")
            if sh3:
                report["screenshots"].append(sh3)

            # 4. Comercial -> Leads & CRM (Smart Follow-up IA LGPD) + Pipeline Move-Stage
            await cdp.click_by_text("aside button", "Comercial")
            await asyncio.sleep(1.2)
            await cdp.wait_idle()
            # Ensure QA tenant has an LGPD lead or click Follow-up IA on first lead
            clicked_followup = await cdp.click_by_text("main button", "Follow-up IA")
            if not clicked_followup:
                await cdp.set_input("#ug-lead-name-input", "QA Phase 26 Lead")
                await cdp.set_input("#ug-lead-email-input", "qa.phase26@union.test")
                await cdp.click_by_text("main button", "Registrar Lead")
                await asyncio.sleep(1.5)
                await cdp.wait_idle()
                clicked_followup = await cdp.click_by_text("main button", "Follow-up IA")
            await asyncio.sleep(1.2)
            smart_followup_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Modo Manual Seguro') || t.includes('Copiar Texto');
                })()
            """)
            sh4 = await cdp.screenshot("04_phase26_crm_smart_followup.png")
            if sh4:
                report["screenshots"].append(sh4)

            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Pipeline & Vendas")
            await asyncio.sleep(0.8)
            pipeline_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Nova Negociação no Pipeline') && (t.includes('Prob.:') || t.includes('Sem itens'));
                })()
            """)
            sh5 = await cdp.screenshot("05_phase26_pipeline_move_stage.png")
            if sh5:
                report["screenshots"].append(sh5)

            # 5. Marketing -> SEO & Artigos (Prioritized Recommendations + Technical Signals)
            await cdp.click_by_text("aside button", "Marketing")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "SEO & Artigos")
            await asyncio.sleep(0.6)
            await cdp.set_input('input[placeholder="https://seudominio.com.br"]', "https://automacao.projetosunion.cloud")
            await cdp.click_by_text("main button", "Executar Auditoria Técnica Real")
            await asyncio.sleep(2.5)
            await cdp.wait_idle()
            seo_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Canonical:') && t.includes('Correções Priorizadas por Impacto');
                })()
            """)
            sh6 = await cdp.screenshot("06_phase26_seo_prioritized.png")
            if sh6:
                report["screenshots"].append(sh6)

            # 6. Gestão -> Integrações (OAuth 2.0 + Disconnect honest) & Configurações & Planos (Entitlements)
            await cdp.click_by_text("aside button", "Gestão")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Integrações")
            await asyncio.sleep(0.7)
            oauth_ok = await cdp.evaluate("(document.querySelector('main')?.innerText || '').includes('Central de Conexões Oficiais') && (document.querySelector('main')?.innerText || '').includes('OAuth 2.0')")
            sh7 = await cdp.screenshot("07_phase26_integrations_oauth.png")
            if sh7:
                report["screenshots"].append(sh7)

            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Configurações & Planos")
            await asyncio.sleep(1.2)
            plans_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Planos PLG & Consumo do Workspace') && t.includes('Cobrança desativada');
                })()
            """)
            sh8 = await cdp.screenshot("08_phase26_plans_entitlements.png")
            if sh8:
                report["screenshots"].append(sh8)

            # 7. Light Mode & Customer Success DS 4.0 check
            await cdp.click_aria("Ativar Modo Claro")
            await asyncio.sleep(0.5)
            light_ok = await cdp.evaluate("document.documentElement.classList.contains('light')")
            sh9 = await cdp.screenshot("09_phase26_light_mode.png")
            if sh9:
                report["screenshots"].append(sh9)
            await cdp.click_aria("Ativar Modo Escuro")
            await asyncio.sleep(0.4)

            # 8. Accessibility & 8 Viewports (including 430x932 & 360x800)
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
                ("mobile_430x932", 430, 932, True),
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
                    sh10 = await cdp.screenshot("10_phase26_mobile_360x800.png")
                    if sh10:
                        report["screenshots"].append(sh10)

            report["checks"] = {
                "login_ok": bool(login_ok),
                "switched_qa": bool(switched_qa),
                "home_ds4_ok": bool(home_ok),
                "growth_center_0_90d_ok": bool(growth_center_ok),
                "agents_matrix_honest_ok": bool(agents_matrix_ok),
                "crm_smart_followup_ok": bool(smart_followup_ok),
                "pipeline_move_stage_ok": bool(pipeline_ok),
                "seo_prioritized_recs_ok": bool(seo_ok),
                "oauth_integrations_ok": bool(oauth_ok),
                "plans_entitlements_readiness_ok": bool(plans_ok),
                "light_mode_ok": bool(light_ok),
                "total_elapsed_s": round(time.time() - t0, 2),
            }
            report["telemetry"] = {
                "console_errors_count": len(cdp.console_errors),
                "exceptions_count": len(cdp.exceptions),
                "network_4xx_5xx_count": len(cdp.network_4xx_5xx),
                "url_token_leaks_count": len(cdp.url_token_leaks),
                "network_4xx_5xx": cdp.network_4xx_5xx,
            }
            report["all_phase26_e2e_passed"] = (
                bool(
                    login_ok
                    and switched_qa
                    and home_ok
                    and growth_center_ok
                    and agents_matrix_ok
                    and smart_followup_ok
                    and pipeline_ok
                    and seo_ok
                    and oauth_ok
                    and plans_ok
                    and light_ok
                )
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

    out_path = OUT_DIR / "phase26_cdp_e2e.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["all_phase26_e2e_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(run_phase26_e2e())
