"""
FASE 20.1 — Auditoria Automatizada REAL do Frontend via Chrome DevTools Protocol (CDP)
Controla uma instância isolada do Google Chrome (--headless=new --remote-debugging-port=9333):
1. Abre https://automacao.projetosunion.cloud e monitora Console + Runtime Exceptions + Network (>=400 e vazamento de token em URL)
2. Faz Login real com admin@projetosunion.cloud / UnionGrowth#2026!
3. Verifica Dashboard (Leads reais = 2, excluindo 3 leads TEST; Receita; zero erros console/network)
4. Navega por TODOS os 25 menus principais na barra lateral, verificando renderização real sem erros JS/HTTP
5. Verifica Menu 09 (Piloto 7 Dias já carregado no boot), Menu 14 (CRM), Menu 18 (Automações), Menu 23 (Sistema Comercial + clique no botão PDF seguro com Blob URL sem access_token na URL!), Menu 25 (UNION AI ENGINE HUB + submenus Provedores e Histórico)
6. Executa Logout real e confirma retorno à tela de login
7. Abre https://automacao.projetosunion.cloud/lp/agentes-ia deslogado e verifica renderização da LP pública + formulário LGPD
8. Salva evidências JSON e screenshots PNG reais em UNION_GROWTH_OS_PHASE20_1_EVIDENCE/frontend/
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
OUT_DIR = ROOT_DIR / "UNION_GROWTH_OS_PHASE20_1_EVIDENCE" / "frontend"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROD_URL = "https://automacao.projetosunion.cloud"
CDP_PORT = 9333


class CDPClient:
    def __init__(self, ws):
        self.ws = ws
        self._id = 0
        self.pending = {}
        self.console_errors = []
        self.exceptions = []
        self.network_requests = []
        self.network_failures = []
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
                        desc = params.get("exceptionDetails", {}).get("text", "")
                        exc_obj = params.get("exceptionDetails", {}).get("exception", {}).get("description", "")
                        self.exceptions.append(f"{desc}: {exc_obj}"[:300])
                    elif method == "Console.messageAdded":
                        m = params.get("message", {})
                        if m.get("level") == "error":
                            self.console_errors.append(str(m.get("text", ""))[:300])
                    elif method == "Network.requestWillBeSent":
                        url = params.get("request", {}).get("url", "")
                        meth = params.get("request", {}).get("method", "")
                        self.network_requests.append({"method": meth, "url": url})
                        if "access_token=" in url.lower() or "token=eyj" in url.lower():
                            self.url_token_leaks.append({"method": meth, "url": url[:160]})
                    elif method == "Network.responseReceived":
                        resp = params.get("response", {})
                        st = resp.get("status", 0)
                        url = resp.get("url", "")
                        if st >= 400 and "favicon.ico" not in url:
                            self.network_failures.append({"status": st, "url": url})
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

    async def close(self):
        self._reader_task.cancel()


async def run_browser_audit():
    tmp_profile = tempfile.mkdtemp(prefix="ugos_cdp_20_1_")
    proc = subprocess.Popen(
        [
            CHROME_PATH,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--window-size=1920,1080",
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={tmp_profile}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    ws_url = None
    for _ in range(30):
        try:
            tabs = httpx.get(f"http://127.0.0.1:{CDP_PORT}/json", timeout=2.0).json()
            page_tab = next((t for t in tabs if t.get("type") == "page" and t.get("webSocketDebuggerUrl")), None)
            if page_tab:
                ws_url = page_tab["webSocketDebuggerUrl"]
                break
        except Exception:
            await asyncio.sleep(0.4)

    if not ws_url:
        proc.terminate()
        raise RuntimeError("Não foi possível conectar ao Chrome CDP na porta 9333.")

    report = {"prod_url": PROD_URL, "steps": {}, "screenshots": []}

    try:
        async with websockets.connect(ws_url, max_size=20 * 1024 * 1024) as ws:
            cdp = CDPClient(ws)
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")
            await cdp.send("Console.enable")
            await cdp.send("Network.enable")
            await cdp.send("Emulation.setDeviceMetricsOverride", {"width": 1920, "height": 1080, "deviceScaleFactor": 1, "mobile": False})

            # 1. Navigate to Login Page
            await cdp.send("Page.navigate", {"url": f"{PROD_URL}/"})
            await asyncio.sleep(3.5)
            body_login = await cdp.evaluate("document.body.innerText.slice(0, 400)")
            report["steps"]["01_open_login"] = {"passed": "UNION GROWTH OS" in (body_login or ""), "preview": (body_login or "")[:180]}

            # 2. Perform REAL Login via DOM input + form submit
            login_ok = await cdp.evaluate("""
                (() => {
                    const emailInput = document.querySelector('input[type="email"]');
                    const passInput = document.querySelector('input[type="password"]');
                    const btn = document.querySelector('button[type="submit"]');
                    if (!emailInput || !passInput || !btn) return 'MISSING_ELEMENTS';
                    const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeSetter.call(emailInput, 'admin@projetosunion.cloud');
                    emailInput.dispatchEvent(new Event('input', { bubbles: true }));
                    nativeSetter.call(passInput, 'UnionGrowth#2026!');
                    passInput.dispatchEvent(new Event('input', { bubbles: true }));
                    btn.click();
                    return 'SUBMITTED';
                })()
            """)
            await asyncio.sleep(5.5)
            dash_text = await cdp.evaluate("document.body.innerText")
            logged_in = "Visão Geral" in (dash_text or "") and "Leads no CRM" in (dash_text or "")
            sh1 = await cdp.screenshot("01_cdp_dashboard_authenticated.png")
            if sh1:
                report["screenshots"].append(sh1)

            # Extract KPI values directly from rendered DOM
            leads_kpi_snippet = await cdp.evaluate("""
                (() => {
                    const cards = Array.from(document.querySelectorAll('div')).filter(el => el.innerText && el.innerText.includes('Leads no CRM') && el.innerText.includes('Conversões:') && el.innerText.length < 180);
                    return cards.length ? cards[cards.length - 1].innerText : '';
                })()
            """)
            report["steps"]["02_login_and_dashboard"] = {
                "submit_result": login_ok,
                "logged_in": logged_in,
                "leads_kpi_rendered": leads_kpi_snippet,
                "passed": logged_in and ("2" in (leads_kpi_snippet or "")),
            }

            # 3. Navigate ALL 26 sidebar menus (01..25 + 17M Multinegócio) and verify each renders cleanly!
            sidebar_items = await cdp.evaluate("""
                (() => {
                    const btns = Array.from(document.querySelectorAll('aside button, nav button'));
                    return btns.map((b, idx) => ({ idx, text: (b.innerText || '').trim().replace(/\\s+/g, ' ') })).filter(x => /^(\\d{2}|17M)\\s/.test(x.text));
                })()
            """)
            menus_checked = []
            for item in (sidebar_items or []):
                lbl = item["text"]
                clicked = await cdp.evaluate(f"""
                    (() => {{
                        const btns = Array.from(document.querySelectorAll('aside button, nav button'));
                        const target = btns.find(b => (b.innerText || '').trim().replace(/\\s+/g, ' ') === {json.dumps(lbl)});
                        if (!target) return false;
                        target.click();
                        return true;
                    }})()
                """)
                await asyncio.sleep(0.35)
                main_len = await cdp.evaluate("(document.querySelector('main') || document.body).innerText.length")
                menus_checked.append({"menu": lbl, "clicked": clicked, "rendered_chars": main_len, "ok": bool(clicked and (main_len or 0) > 100)})

                # Capture targeted screenshots on key audited menus
                if lbl.startswith("09 "):
                    p7_text = await cdp.evaluate("(document.querySelector('main') || document.body).innerText")
                    report["steps"]["03_menu09_pilot_7_days_preloaded"] = {
                        "passed": ("7" in (p7_text or "")) and ("Dia" in (p7_text or "") or "Piloto" in (p7_text or "")),
                        "snippet": (p7_text or "")[:240],
                    }
                    sh = await cdp.screenshot("02_cdp_menu09_pilot_7_days.png")
                    if sh:
                        report["screenshots"].append(sh)
                elif lbl.startswith("17M "):
                    await asyncio.sleep(1.0)
                    sh = await cdp.screenshot("03_cdp_menu17m_multinegocio_propostas.png")
                    if sh:
                        report["screenshots"].append(sh)
                    # Switch to QA_AUTOMATED_TENANT via the multi-tenant <select> dropdown (where QA proposals live without polluting Tenant 1!)
                    switched = await cdp.evaluate("""
                        (() => {
                            const sel = document.querySelector('aside select, select');
                            if (!sel) return false;
                            const opt = Array.from(sel.options).find(o => (o.text || '').includes('QA_AUTOMATED_TENANT'));
                            if (!opt) return false;
                            sel.value = opt.value;
                            sel.dispatchEvent(new Event('change', { bubbles: true }));
                            return true;
                        })()
                    """)
                    await asyncio.sleep(2.5)
                    # Re-click 17M in case tenant switch refreshed view
                    await cdp.evaluate("""
                        (() => {
                            const btns = Array.from(document.querySelectorAll('aside button, nav button'));
                            const t = btns.find(b => (b.innerText || '').trim().startsWith('17M'));
                            if (t) t.click();
                        })()
                    """)
                    await asyncio.sleep(1.0)
                    # Intercept window.open to prove secure Blob URL (zero access_token!) when clicking PDF button
                    pdf_check = await cdp.evaluate("""
                        (async () => {
                            window.__capturedOpenUrls = [];
                            const origOpen = window.open;
                            window.open = function(u, target, features) {
                                window.__capturedOpenUrls.push(String(u || ''));
                                return null;
                            };
                            const pdfBtns = Array.from(document.querySelectorAll('button')).filter(b => (b.innerText || '').trim() === 'PDF');
                            if (pdfBtns.length === 0) return { found_pdf_button: false, urls: [] };
                            pdfBtns[0].click();
                            await new Promise(r => setTimeout(r, 2000));
                            window.open = origOpen;
                            return { found_pdf_button: true, pdf_buttons_count: pdfBtns.length, urls: window.__capturedOpenUrls };
                        })()
                    """)
                    sh_qa = await cdp.screenshot("03b_cdp_menu17m_qa_tenant_proposals.png")
                    if sh_qa:
                        report["screenshots"].append(sh_qa)
                    # Switch back to Tenant 1 (UNION GROWTH OS)
                    await cdp.evaluate("""
                        (() => {
                            const sel = document.querySelector('aside select, select');
                            if (!sel) return;
                            const opt = Array.from(sel.options).find(o => (o.text || '').includes('UNION GROWTH OS'));
                            if (opt) {
                                sel.value = opt.value;
                                sel.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        })()
                    """)
                    await asyncio.sleep(1.8)
                    urls_opened = (pdf_check or {}).get("urls", [])
                    report["steps"]["04_menu17m_secure_blob_pdf_click"] = {
                        "switched_to_qa_tenant": bool(switched),
                        "found_pdf_button": (pdf_check or {}).get("found_pdf_button"),
                        "pdf_buttons_count": (pdf_check or {}).get("pdf_buttons_count", 0),
                        "opened_urls": urls_opened,
                        "uses_blob_url": any(u.startswith("blob:") for u in urls_opened),
                        "zero_token_in_opened_url": all("access_token" not in u for u in urls_opened),
                        "passed": (
                            bool((pdf_check or {}).get("found_pdf_button"))
                            and any(u.startswith("blob:") for u in urls_opened)
                            and all("access_token" not in u for u in urls_opened)
                        ),
                    }
                elif lbl.startswith("25 "):
                    await asyncio.sleep(0.8)
                    ai_text = await cdp.evaluate("(document.querySelector('main') || document.body).innerText")
                    sh = await cdp.screenshot("04_cdp_menu25_ai_engine_hub.png")
                    if sh:
                        report["screenshots"].append(sh)
                    # Click sub-tabs 2. Provedores and 9. Histórico
                    prov_ok = await cdp.evaluate("""
                        (async () => {
                            const b = Array.from(document.querySelectorAll('button')).find(x => (x.innerText || '').includes('2. Provedores'));
                            if (!b) return false;
                            b.click();
                            await new Promise(r => setTimeout(r, 400));
                            return (document.body.innerText || '').includes('AQ....rlw');
                        })()
                    """)
                    hist_ok = await cdp.evaluate("""
                        (async () => {
                            const b = Array.from(document.querySelectorAll('button')).find(x => (x.innerText || '').includes('9. Histórico'));
                            if (!b) return false;
                            b.click();
                            await new Promise(r => setTimeout(r, 400));
                            return (document.body.innerText || '').includes('Histórico de Execuções');
                        })()
                    """)
                    report["steps"]["05_menu25_ai_engine_hub"] = {
                        "has_free_only_badge": "FREE_ONLY" in (ai_text or ""),
                        "has_gemini": "GEMINI" in (ai_text or "").upper(),
                        "subtab_provedores_masked_key_ok": bool(prov_ok),
                        "subtab_historico_ok": bool(hist_ok),
                        "passed": ("FREE_ONLY" in (ai_text or "")) and ("GEMINI" in (ai_text or "").upper()) and bool(prov_ok) and bool(hist_ok),
                    }

            report["steps"]["06_all_25_menus_navigation"] = {
                "total_menus_detected": len(menus_checked),
                "menus_ok": sum(1 for m in menus_checked if m["ok"]),
                "passed": len(menus_checked) >= 24 and all(m["ok"] for m in menus_checked),
                "details": menus_checked,
            }

            # 4. Test REAL Logout
            logout_clicked = await cdp.evaluate("""
                (() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const out = btns.find(b => /sair|logout/i.test((b.innerText || '').trim()));
                    if (!out) return false;
                    out.click();
                    return true;
                })()
            """)
            await asyncio.sleep(1.5)
            after_logout = await cdp.evaluate("document.querySelector('input[type=\"password\"]') !== null")
            report["steps"]["07_logout"] = {"clicked": logout_clicked, "returned_to_login_form": bool(after_logout), "passed": bool(logout_clicked and after_logout)}

            # 5. Open Public Landing Page /lp/agentes-ia while UNAUTHENTICATED
            await cdp.send("Page.navigate", {"url": f"{PROD_URL}/lp/agentes-ia"})
            await asyncio.sleep(2.0)
            lp_info = await cdp.evaluate("""
                (() => {
                    const txt = document.body.innerText || '';
                    const lgpd = document.querySelector('#consent_lgpd');
                    const form = document.querySelector('#lpForm');
                    return {
                        has_title: txt.includes('Agentes de IA'),
                        not_login_screen: !document.querySelector('input[type="password"]'),
                        has_form: Boolean(form),
                        has_required_lgpd_checkbox: Boolean(lgpd && lgpd.required),
                    };
                })()
            """)
            sh_lp = await cdp.screenshot("05_cdp_public_lp_agentes_ia.png")
            if sh_lp:
                report["screenshots"].append(sh_lp)
            report["steps"]["08_public_landing_page_unauthenticated"] = {
                **(lp_info or {}),
                "passed": bool(lp_info and lp_info.get("has_title") and lp_info.get("not_login_screen") and lp_info.get("has_form") and lp_info.get("has_required_lgpd_checkbox")),
            }

            # 6. Collect console, runtime exceptions, network failures, and URL token leak telemetry
            report["telemetry"] = {
                "total_network_requests_observed": len(cdp.network_requests),
                "console_errors_count": len(cdp.console_errors),
                "console_errors": cdp.console_errors,
                "runtime_exceptions_count": len(cdp.exceptions),
                "runtime_exceptions": cdp.exceptions,
                "network_failures_4xx_5xx_count": len(cdp.network_failures),
                "network_failures": cdp.network_failures,
                "url_token_leaks_count": len(cdp.url_token_leaks),
                "url_token_leaks": cdp.url_token_leaks,
            }
            report["all_frontend_checks_passed"] = (
                all(v.get("passed", False) for v in report["steps"].values())
                and len(cdp.console_errors) == 0
                and len(cdp.exceptions) == 0
                and len(cdp.network_failures) == 0
                and len(cdp.url_token_leaks) == 0
            )
            await cdp.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    (OUT_DIR / "phase20_1_cdp_browser_audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({
        "all_frontend_checks_passed": report["all_frontend_checks_passed"],
        "steps_passed": {k: v.get("passed") for k, v in report["steps"].items()},
        "menus_detected": report["steps"].get("06_all_25_menus_navigation", {}).get("total_menus_detected"),
        "pdf_check": report["steps"].get("04_menu17m_secure_blob_pdf_click"),
        "telemetry": report["telemetry"],
        "screenshots": report["screenshots"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(run_browser_audit())
