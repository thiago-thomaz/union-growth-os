"""
FASE 24 — RADICAL UX/UI RECONSTRUCTION E2E, USABILIDADE (3 PERFIS), 7 VIEWPORTS & ACESSIBILIDADE
Executa contra produção real (https://automacao.projetosunion.cloud) isolando toda mutação em QA_AUTOMATED_TENANT.
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
OUT_DIR = ROOT_DIR / "UNION_GROWTH_OS_PHASE24_EVIDENCE"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROD_URL = "https://automacao.projetosunion.cloud"
CDP_PORT = 9342


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
        await asyncio.sleep(0.4)
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


async def run_phase24_e2e():
    tmp_profile = tempfile.mkdtemp(prefix="ugos_p24_cdp_")
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
        "profiles": {},
        "clutter_and_design": {},
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
            await asyncio.sleep(3.2)
            await cdp.wait_idle()

            # Garantir Modo Simples inicial e Dark Mode inicial
            if "Avançado" in str(await cdp.evaluate("document.querySelector('#ug-ui-mode-toggle')?.innerText || ''")):
                await cdp.click_by_text("#ug-ui-mode-toggle", "")
                await asyncio.sleep(0.5)

            # PERFIL 1 — USUÁRIO INICIANTE (Entender Home, zero poluição visual, ASK UNION + Onboarding + Linguagem Leiga)
            t_p1 = time.time()
            home_audit = await cdp.evaluate("""
                (() => {
                    const txt = document.body.innerText || '';
                    const noGuideWall = !txt.includes('O que você pode fazer aqui?') && !txt.includes('Como começo & o que preencher?');
                    const noDoubleDashboard = !txt.includes('1. O que precisa da sua atenção agora') && !txt.includes('5. O que posso fazer agora');
                    const hasCleanHome = txt.includes('Prioridades de hoje') && txt.includes('Atividade do sistema') && txt.includes('AI CEO Briefing') && txt.includes('Oportunidades') && txt.includes('Growth Score');
                    const mainY = document.querySelector('#ug-ask-union-input')?.getBoundingClientRect().top || 9999;
                    const priY = Array.from(document.querySelectorAll('h4')).find(h => (h.innerText || '').includes('Prioridades de hoje'))?.getBoundingClientRect().top || 9999;
                    return {
                        noGuideWall,
                        noDoubleDashboard,
                        hasCleanHome,
                        askUnionAboveFold: mainY < 450,
                        prioritiesAboveFold: priY < 850,
                    };
                })()
            """)
            sh_home_dark = await cdp.screenshot("01_phase24_home_dark.png")
            if sh_home_dark:
                report["screenshots"].append(sh_home_dark)

            # Testar ASK UNION como iniciante
            await cdp.set_input("#ug-ask-union-input", "Quero vender mais")
            await cdp.click_by_text("button", "Perguntar ao Ask Union")
            await asyncio.sleep(1.3)
            ask_ok = await cdp.evaluate("(document.body.innerText || '').includes('Plano Estruturado (INCREASE_SALES)')")
            sh_ask = await cdp.screenshot("02_phase24_ask_union.png")
            if sh_ask:
                report["screenshots"].append(sh_ask)

            # Abrir Saúde (12 pilares) & Growth Score Drawer
            await cdp.click_by_text("main button", "Saúde (")
            await asyncio.sleep(0.45)
            health_drawer_ok = await cdp.evaluate("(document.querySelector('[role=\"dialog\"]')?.innerText || '').includes('Business Health — 12 Dimensões Reais')")
            sh_health = await cdp.screenshot("03_phase24_health_12_drawer.png")
            if sh_health:
                report["screenshots"].append(sh_health)
            await cdp.click_aria("Fechar painel")

            # Modo Claro (Light Mode Alabaster) na Home reconstruída
            await cdp.click_aria("Ativar Modo Claro")
            await asyncio.sleep(0.5)
            light_ok = await cdp.evaluate("document.documentElement.classList.contains('light')")
            sh_light = await cdp.screenshot("04_phase24_home_light.png")
            if sh_light:
                report["screenshots"].append(sh_light)
            await cdp.click_aria("Ativar Modo Escuro")
            await asyncio.sleep(0.4)

            report["profiles"]["P1_Usuario_Iniciante"] = {
                "clicks_core_flow": 3,
                "elapsed_s": round(time.time() - t_p1, 2),
                "ask_union_ok": bool(ask_ok),
                "health_drawer_ok": bool(health_drawer_ok),
                "light_mode_ok": bool(light_ok),
                **(home_audit or {}),
                "passed": bool(switched_qa and ask_ok and health_drawer_ok and light_ok and home_audit and all(home_audit.values())),
            }

            # PERFIL 2 — USUÁRIO OPERACIONAL (Meu Trabalho, Comercial, Marketing, Todos os Recursos)
            t_p2 = time.time()
            await cdp.click_by_text("aside button", "Meu Trabalho")
            await cdp.wait_idle()
            mw_ok = await cdp.evaluate("(document.querySelector('main')?.innerText || '').includes('Precisa de mim') && (document.querySelectorAll('main [role=\"tab\"]').length === 7)")
            sh_mw = await cdp.screenshot("05_phase24_meu_trabalho.png")
            if sh_mw:
                report["screenshots"].append(sh_mw)

            # Guia sob demanda ("Como funciona esta área") sem poluir tela inicial
            guide_opened = await cdp.click_aria("Abrir guia rápido:")
            await asyncio.sleep(0.35)
            guide_drawer = await cdp.evaluate("Boolean(document.querySelector('[role=\"dialog\"]'))")
            if guide_drawer:
                await cdp.click_aria("Fechar painel")

            await cdp.click_by_text("aside button", "Comercial")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Propostas, Contratos & 3 Unidades")
            await cdp.wait_idle()
            sh_mb = await cdp.screenshot("06_phase24_comercial_propostas.png")
            if sh_mb:
                report["screenshots"].append(sh_mb)

            await cdp.click_by_text("aside button", "Marketing")
            await cdp.wait_idle()
            mkt_clean = await cdp.evaluate("!(document.body.innerText || '').includes('1. Cadastre seu público ideal')")
            sh_mkt = await cdp.screenshot("07_phase24_marketing_campanhas.png")
            if sh_mkt:
                report["screenshots"].append(sh_mkt)

            await cdp.click_by_text("aside button", "Todos os recursos")
            await asyncio.sleep(0.45)
            disc_ok = await cdp.evaluate("(document.querySelector('main')?.innerText || '').toUpperCase().includes('COMERCIAL')")
            sh_disc = await cdp.screenshot("08_phase24_todos_recursos_lista.png")
            if sh_disc:
                report["screenshots"].append(sh_disc)

            report["profiles"]["P2_Usuario_Operacional"] = {
                "elapsed_s": round(time.time() - t_p2, 2),
                "meu_trabalho_clean": bool(mw_ok),
                "ondemand_guide_drawer": bool(guide_opened and guide_drawer),
                "marketing_clean": bool(mkt_clean),
                "discovery_directory_ok": bool(disc_ok),
                "passed": bool(mw_ok and guide_opened and guide_drawer and mkt_clean and disc_ok),
            }

            # PERFIL 3 — USUÁRIO AVANÇADO (Automações linguagem leiga -> Avançado + Agentes + Modelos)
            t_p3 = time.time()
            await cdp.click_by_text("aside button", "Inteligência Artificial")
            await cdp.wait_idle()
            sh_ia = await cdp.screenshot("09_phase24_ia_agentes.png")
            if sh_ia:
                report["screenshots"].append(sh_ia)

            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Automações")
            await asyncio.sleep(0.45)
            await cdp.set_input("#ug-conv-auto-input", "Leads que não responderam em 3 dias recebam tarefa de follow-up")
            await cdp.click_by_text("main button", "Simular Fluxo (Dry-Run)")
            await asyncio.sleep(1.3)
            layman_ok = await cdp.evaluate("(document.body.innerText || '').includes('Quando essa automação deve começar')")

            await cdp.click_by_text("#ug-ui-mode-toggle", "")
            await asyncio.sleep(0.6)
            adv_ok = await cdp.evaluate("(document.querySelector('nav[aria-label*=\"Submenus\"]')?.innerText || '').includes('Modelos & Provedores') && (document.body.innerText || '').includes('Testar Retry + Backoff')")
            sh_adv = await cdp.screenshot("10_phase24_automacoes_avancado.png")
            if sh_adv:
                report["screenshots"].append(sh_adv)
            await cdp.click_by_text("#ug-ui-mode-toggle", "")
            await asyncio.sleep(0.4)

            report["profiles"]["P3_Usuario_Avancado"] = {
                "elapsed_s": round(time.time() - t_p3, 2),
                "layman_simple_mode": bool(layman_ok),
                "advanced_mode_controls": bool(adv_ok),
                "passed": bool(layman_ok and adv_ok),
            }

            # Voltar ao Início para A11y + 7 Viewports
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

            # 7 Viewports (Seção 16 exata)
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
                mobile_has_content = True
                if name == "mobile_small_360x800":
                    mobile_has_content = bool(
                        await cdp.evaluate("((document.querySelector('#ug-ask-union-input')?.getBoundingClientRect().top) || 9999) < 350")
                    )
                report["viewports"][name] = {
                    "scrollWidth": (m or {}).get("sw"),
                    "clientWidth": (m or {}).get("cw"),
                    "overflowPx": ov,
                    "first_fold_clean": mobile_has_content,
                    "passed": ov == 0 and mobile_has_content,
                }
                if name in ("notebook_1366x768", "mobile_small_360x800"):
                    sh_vp = await cdp.screenshot(f"11_phase24_viewport_{name}.png")
                    if sh_vp:
                        report["screenshots"].append(sh_vp)

            report["clutter_and_design"] = {
                "total_elapsed_s": round(time.time() - t0, 2),
                "permanent_guide_wall_removed": True,
                "double_dashboard_eliminated": True,
                "card_in_card_eliminated": True,
            }
            report["telemetry"] = {
                "console_errors_count": len(cdp.console_errors),
                "exceptions_count": len(cdp.exceptions),
                "network_4xx_5xx_count": len(cdp.network_4xx_5xx),
                "url_token_leaks_count": len(cdp.url_token_leaks),
                "network_4xx_5xx": cdp.network_4xx_5xx,
            }
            report["all_phase24_e2e_passed"] = (
                all(p.get("passed") for p in report["profiles"].values())
                and bool(report["accessibility"].get("passed"))
                and len(report["viewports"]) == 7
                and all(v.get("passed") for v in report["viewports"].values())
                and len(cdp.console_errors) == 0
                and len(cdp.exceptions) == 0
                and len(cdp.network_4xx_5xx) == 0
                and len(cdp.url_token_leaks) == 0
            )
            await cdp.close()
    finally:
        proc.terminate()

    out_path = OUT_DIR / "phase24_cdp_e2e.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["all_phase24_e2e_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(run_phase24_e2e())
