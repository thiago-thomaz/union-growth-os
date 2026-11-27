"""
FASE 27 — GLOBAL VERSIONING (SemVer), 25-CATEGORY AUDIT CENTER, TRACEABILITY MATRIX,
SHA-256 BACKUP RESTORE TEST, PERSISTENT GROWTH CENTER (0-90D), AI 12-AGENT BENCHMARK,
VISUAL AUTOMATION PRESETS & WCAG/8-VIEWPORT E2E
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
OUT_DIR = ROOT_DIR / "UNION_GROWTH_OS_PHASE27_EVIDENCE"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROD_URL = "https://automacao.projetosunion.cloud"
CDP_PORT = 9347


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
                if (el.disabled) return false;
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

    async def wait_idle(self, timeout_s: float = 15.0):
        for _ in range(int(timeout_s / 0.4)):
            await asyncio.sleep(0.4)
            busy = await self.evaluate("document.querySelector('button[aria-label=\"Atualizar Dados\"]')?.getAttribute('data-loading') === 'true'")
            if not busy:
                return True
        return False

    async def wait_for_text(self, selector: str, substring: str, timeout_s: float = 14.0) -> bool:
        for _ in range(int(timeout_s / 0.4)):
            found = await self.evaluate(f"((document.querySelector({json.dumps(selector)})?.innerText) || '').includes({json.dumps(substring)})")
            if found:
                return True
            await asyncio.sleep(0.4)
        return False

    async def close(self):
        self._reader_task.cancel()


async def run_phase27_e2e():
    tmp_profile = tempfile.mkdtemp(prefix="ugos_p27_cdp_")
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
            await asyncio.sleep(4.2)
            await cdp.wait_idle()

            # Isolar exclusivamente no tenant QA_AUTOMATED_TENANT
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
            await asyncio.sleep(2.2)
            await cdp.wait_idle()

            # 1. Global Header SemVer Badge
            header_semver_ok = await cdp.evaluate("""
                (() => {
                    const b = document.querySelector('#ug-version-badge-btn');
                    if (!b) return false;
                    const txt = b.innerText || '';
                    return txt.includes('v2.4.0') && txt.includes('PRODUCTION');
                })()
            """)
            sh1 = await cdp.screenshot("01_phase27_header_semver_badge.png")
            if sh1:
                report["screenshots"].append(sh1)

            # 2. Release History Drawer
            await cdp.evaluate("document.querySelector('#ug-version-badge-btn')?.click()")
            await cdp.wait_for_text("body", "Histórico de Releases (6)", timeout_s=10.0)
            await asyncio.sleep(0.4)
            release_drawer_ok = await cdp.evaluate("""
                (() => {
                    const t = document.body.innerText || '';
                    return t.includes('Controle SemVer') && t.includes('2.4.0') && t.includes('Histórico de Releases') && t.includes('v2.3.0');
                })()
            """)
            sh2 = await cdp.screenshot("02_phase27_release_history_drawer.png")
            if sh2:
                report["screenshots"].append(sh2)

            # Jump from Drawer -> Audit Center (or click menu)
            jumped_audit = await cdp.click_by_text("button", "Central de Auditoria")
            if not jumped_audit:
                await cdp.click_by_text("aside button", "Gestão")
                await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Auditoria")
            await asyncio.sleep(1.5)
            await cdp.wait_idle()

            # 3. 25-Category Evidence Audit Center
            await cdp.click_by_text("main button", "EXECUTAR AUDITORIA COMPLETA")
            await cdp.wait_for_text("main", "Scorecard Objetivo das 25 Categorias", timeout_s=20.0)
            await asyncio.sleep(0.5)
            audit_25_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Scorecard Objetivo das 25 Categorias') && t.includes('1. UX/UI') && t.includes('25. Scalability');
                })()
            """)
            sh3 = await cdp.screenshot("03_phase27_audit_25_categories.png")
            if sh3:
                report["screenshots"].append(sh3)

            # 4. Traceability Matrix
            await cdp.click_by_text("main button", "Matriz de Rastreabilidade")
            await cdp.wait_for_text("main", "Sistema SemVer + Histórico de Releases", timeout_s=8.0)
            await asyncio.sleep(0.4)
            traceability_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Sistema SemVer + Histórico de Releases') && t.includes('Growth Execution Center');
                })()
            """)
            sh4 = await cdp.screenshot("04_phase27_traceability_matrix.png")
            if sh4:
                report["screenshots"].append(sh4)

            # 5. Isolated Backup SHA-256 Restore Test
            await cdp.click_by_text("main button", "Backup, Histórico")
            await asyncio.sleep(0.6)
            await cdp.click_by_text("main button", "Testar Restauração Isolada")
            await cdp.wait_for_text("main", "Teste de Recuperação Isolada Concluído", timeout_s=15.0)
            await asyncio.sleep(0.4)
            restore_sha_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Teste de Recuperação Isolada Concluído') && t.includes('SHA-256');
                })()
            """)
            sh5 = await cdp.screenshot("05_phase27_backup_restore_test.png")
            if sh5:
                report["screenshots"].append(sh5)

            # 6. Persistent Growth Execution Center (0/7/30/90d + Concluir + Replanejar)
            await cdp.click_by_text("aside button", "Início")
            await asyncio.sleep(0.8)
            await cdp.click_by_text("main button", "Centro de Crescimento (0–90d)")
            await asyncio.sleep(1.2)
            await cdp.click_by_text("main button", "Gerar Plano 0–90d")
            await asyncio.sleep(1.2)
            await cdp.wait_for_text("main", "Gerar Plano 0–90d", timeout_s=15.0)
            await cdp.wait_for_text("main", "Plano de Execução Priorizado", timeout_s=15.0)
            await cdp.click_by_text("main button", "Concluir")
            done_ok = await cdp.wait_for_text("main", "Concluído", timeout_s=12.0)
            await cdp.wait_idle()
            await asyncio.sleep(0.6)
            await cdp.click_by_text("main button", "Replanejar")
            replan_ok = await cdp.wait_for_text("main", "Replanejado", timeout_s=12.0)
            await cdp.wait_idle()
            await asyncio.sleep(0.5)
            growth_persist_ok = bool(done_ok and replan_ok) and await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Prioridade:') && t.includes('Responsável:') && t.includes('Meta de sucesso:') && t.includes('Replanejado');
                })()
            """)
            sh6 = await cdp.screenshot("06_phase27_persistent_growth_center.png")
            if sh6:
                report["screenshots"].append(sh6)

            # 7. AI Benchmark 12 Agents (R$ 0,00) + 8. Visual Automations Presets
            await cdp.click_by_text("aside button", "Inteligência Artificial")
            await asyncio.sleep(0.8)
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Automações 24/7")
            await cdp.wait_for_text("main", "Templates Visuais em 1 Clique", timeout_s=10.0)
            auto_presets_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Templates Visuais em 1 Clique') && t.includes('Ativar Preset em 1 Clique');
                })()
            """)
            sh8 = await cdp.screenshot("08_phase27_automations_presets_flow.png")
            if sh8:
                report["screenshots"].append(sh8)

            # Revelar sub-abas avançadas para abrir Modelos & Provedores e rodar Benchmark 12 Agentes
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Avançado")
            await asyncio.sleep(1.0)
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Modelos")
            await cdp.wait_for_text("main", "Política & Agentes", timeout_s=10.0)
            await cdp.click_by_text("main button", "Política & Agentes")
            await asyncio.sleep(0.6)
            await cdp.click_by_text("main button", "Benchmark 12 Agentes")
            await cdp.wait_for_text("main", "Resultado do Benchmark (12 agentes", timeout_s=12.0)
            await asyncio.sleep(0.4)
            ai_benchmark_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Resultado do Benchmark (12 agentes') && t.includes('Custo: R$ 0,00');
                })()
            """)
            sh7 = await cdp.screenshot("07_phase27_ai_benchmark_12_agents.png")
            if sh7:
                report["screenshots"].append(sh7)
            # Restaurar Modo Simples para manter o estado limpo
            await cdp.evaluate("document.querySelector('#ug-ui-mode-toggle')?.click()")
            await asyncio.sleep(0.6)

            await cdp.click_by_text("aside button", "Gestão")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Configurações & Planos")
            await asyncio.sleep(1.2)
            plans_ok = await cdp.evaluate("""
                (() => {
                    const t = document.querySelector('main')?.innerText || '';
                    return t.includes('Planos PLG & Consumo do Workspace') && t.includes('Cobrança desativada');
                })()
            """)
            sh9 = await cdp.screenshot("09_phase27_plans_entitlements.png")
            if sh9:
                report["screenshots"].append(sh9)

            # 9. Light Mode & WCAG & 8 Viewports
            await cdp.click_aria("Ativar Modo Claro")
            await asyncio.sleep(0.5)
            light_ok = await cdp.evaluate("document.documentElement.classList.contains('light')")
            sh10 = await cdp.screenshot("10_phase27_light_mode.png")
            if sh10:
                report["screenshots"].append(sh10)
            await cdp.click_aria("Ativar Modo Escuro")
            await asyncio.sleep(0.4)

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
                    sh11 = await cdp.screenshot("11_phase27_mobile_360x800.png")
                    if sh11:
                        report["screenshots"].append(sh11)

            report["checks"] = {
                "login_ok": bool(login_ok),
                "switched_qa": bool(switched_qa),
                "header_semver_ok": bool(header_semver_ok),
                "release_drawer_ok": bool(release_drawer_ok),
                "audit_25_categories_ok": bool(audit_25_ok),
                "traceability_matrix_ok": bool(traceability_ok),
                "backup_restore_sha256_ok": bool(restore_sha_ok),
                "growth_center_persisted_ok": bool(growth_persist_ok),
                "ai_benchmark_12_agents_ok": bool(ai_benchmark_ok),
                "automations_presets_flow_ok": bool(auto_presets_ok),
                "plans_entitlements_ok": bool(plans_ok),
                "light_mode_ok": bool(light_ok),
                "total_elapsed_s": round(time.time() - t0, 2),
            }
            report["telemetry"] = {
                "console_errors_count": len(cdp.console_errors),
                "console_errors": cdp.console_errors,
                "exceptions_count": len(cdp.exceptions),
                "exceptions": cdp.exceptions,
                "network_4xx_5xx_count": len(cdp.network_4xx_5xx),
                "url_token_leaks_count": len(cdp.url_token_leaks),
                "network_4xx_5xx": cdp.network_4xx_5xx,
            }
            report["all_phase27_e2e_passed"] = (
                bool(
                    login_ok
                    and switched_qa
                    and header_semver_ok
                    and release_drawer_ok
                    and audit_25_ok
                    and traceability_ok
                    and restore_sha_ok
                    and growth_persist_ok
                    and ai_benchmark_ok
                    and auto_presets_ok
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

    out_path = OUT_DIR / "phase27_cdp_e2e.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["all_phase27_e2e_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(run_phase27_e2e())
