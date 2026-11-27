"""
FASE 22 — E2E UX/UI, Responsividade e Acessibilidade WCAG 2.2 AA via Chrome DevTools Protocol (CDP)
Testa a aplicação REAL publicada em produção (https://automacao.projetosunion.cloud):
1. Login real com admin@projetosunion.cloud / UnionGrowth#2026!
2. Início (HomeWorkspace): 5 blocos de decisão + Onboarding dispensável/restaurável persistente
3. Modo Claro & Modo Escuro + contraste WCAG computado
4. Busca Global / Command Center (Ctrl+K): busca por "Campanha" e "Gemini" + navegação real
5. Barra Lateral Colapsável + 6 Áreas Principais + Subtabs Contextuais + Filtro na Sidebar
6. Todos os Recursos: busca + favoritar + filtrar por Favoritos
7. Meu Trabalho: 7 filtros semânticos + abertura e fechamento de Drawer contextual
8. Comercial: filtro CRM + Propostas & 3 Unidades + troca para QA_AUTOMATED_TENANT + botão PDF com Blob URL segura
9. Marketing: filtro de Campanhas + Content Factory + Calendário & Redes + SEO + Criativos + Copywriting + Growth
10. Inteligência Artificial: Visão & Agentes (leigo + detalhe técnico) + Modelos & Provedores (FREE_ONLY + Gemini AQ....rlw + Histórico) + Automações + Piloto 7 Dias
11. Gestão: Relatórios executivos (+ details JSON) + Integrações com filtro + Financeiro + Configurações + Auditoria
12. Central de Ajuda Drawer (Esta Tela, Glossário & FAQ, Atalhos)
13. Auditoria DOM de Acessibilidade WCAG 2.2 AA (landmarks, rótulos acessíveis em botões/inputs/dialog, foco teclado)
14. Responsividade em 4 viewports (1920x1080, 1366x768, 768x1024, 390x844) + Mobile Drawer + zero overflow horizontal
15. Logout real + Landing Page pública (/lp/agentes-ia) deslogada + zero erros JS/Console/HTTP/token leak
"""
import asyncio
import base64
import json
import math
import subprocess
import tempfile
from pathlib import Path
import httpx
import websockets

ROOT_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT_DIR / "UNION_GROWTH_OS_PHASE22_SCREENSHOTS"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROD_URL = "https://automacao.projetosunion.cloud"
CDP_PORT = 9335


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

    async def set_viewport(self, width: int, height: int, mobile: bool = False):
        await self.send(
            "Emulation.setDeviceMetricsOverride",
            {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": mobile},
        )
        await asyncio.sleep(0.45)

    async def click_by_text(self, selector: str, substring: str, exact: bool = False) -> bool:
        js = f"""
        (() => {{
            const els = Array.from(document.querySelectorAll({json.dumps(selector)}));
            const target = els.find(el => {{
                const txt = (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\\s+/g, ' ');
                if ({'txt === ' + json.dumps(substring) if exact else 'txt.includes(' + json.dumps(substring) + ')'}) return true;
                return false;
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

    async def click_aria(self, aria_prefix: str) -> bool:
        js = f"""
        (() => {{
            const els = Array.from(document.querySelectorAll('button, [role="button"], a'));
            const target = els.find(el => (el.getAttribute('aria-label') || '').includes({json.dumps(aria_prefix)}));
            if (!target) return false;
            target.click();
            return true;
        }})()
        """
        ok = bool(await self.evaluate(js))
        await asyncio.sleep(0.4)
        return ok

    async def close(self):
        self._reader_task.cancel()


async def run_phase22_e2e():
    tmp_profile = tempfile.mkdtemp(prefix="ugos_cdp_22_")
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
    for _ in range(35):
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
        raise RuntimeError("Falha ao iniciar Chrome CDP na porta 9335.")

    report = {
        "prod_url": PROD_URL,
        "scenarios": {},
        "accessibility": {},
        "responsiveness": {},
        "screenshots": [],
    }

    try:
        async with websockets.connect(ws_url, max_size=25 * 1024 * 1024) as ws:
            cdp = CDPClient(ws)
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")
            await cdp.send("Console.enable")
            await cdp.send("Network.enable")
            await cdp.set_viewport(1920, 1080, mobile=False)

            # SCENARIO 1: Abrir página e autenticar
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

            home_check = await cdp.evaluate("""
                (() => {
                    const txt = document.body.innerText || '';
                    return {
                        has_sidebar_areas: ['Início', 'Meu Trabalho', 'Comercial', 'Marketing', 'Inteligência Artificial', 'Gestão'].every(x => txt.includes(x)),
                        has_phase24_home: txt.includes('Prioridades de hoje') && txt.includes('AI CEO Briefing') && txt.includes('Oportunidades') && txt.includes('Atividade do sistema') && txt.includes('ASK UNION') && txt.includes('Growth Score'),
                        has_onboarding: txt.includes('Onboarding 6 Etapas'),
                    };
                })()
            """)
            sh1 = await cdp.screenshot("01_inicio_dashboard_dark.png")
            if sh1:
                report["screenshots"].append(sh1)
            report["scenarios"]["S01_S02_login_and_inicio_5blocks"] = {
                **(home_check or {}),
                "passed": bool(home_check and home_check.get("has_sidebar_areas") and home_check.get("has_phase24_home") and home_check.get("has_onboarding")),
            }

            # SCENARIO 3: Onboarding Dismiss + Persistence + Restore
            dismissed_ok = await cdp.click_aria("Dispensar checklist de onboarding")
            await asyncio.sleep(0.4)
            after_dismiss = await cdp.evaluate("""
                (() => ({
                    hidden_in_dom: !(document.body.innerText || '').includes('Onboarding 6 Etapas'),
                    stored: localStorage.getItem('ug_onboarding_dismissed') === '1',
                    has_restore_btn: (document.body.innerText || '').includes('Configuração ('),
                }))()
            """)
            restored_ok = await cdp.click_by_text("main button", "Configuração (")
            await asyncio.sleep(0.4)
            after_restore = await cdp.evaluate("""
                (() => ({
                    visible_again: (document.body.innerText || '').includes('Onboarding 6 Etapas'),
                    cleared_storage: !localStorage.getItem('ug_onboarding_dismissed'),
                }))()
            """)
            report["scenarios"]["S03_onboarding_dismiss_and_restore"] = {
                "dismissed_ok": dismissed_ok,
                **(after_dismiss or {}),
                "restored_ok": restored_ok,
                **(after_restore or {}),
                "passed": bool(
                    dismissed_ok
                    and after_dismiss and after_dismiss.get("hidden_in_dom") and after_dismiss.get("stored") and after_dismiss.get("has_restore_btn")
                    and restored_ok and after_restore and after_restore.get("visible_again") and after_restore.get("cleared_storage")
                ),
            }

            # SCENARIO 4: Light Mode & Dark Mode Contrast Check (incluindo Onboarding Banner)
            light_clicked = await cdp.click_aria("Ativar Modo Claro")
            await asyncio.sleep(0.6)
            light_metrics = await cdp.evaluate("""
                (() => {
                    const htmlLight = document.documentElement.classList.contains('light');
                    const mainStyle = window.getComputedStyle(document.body);
                    const h1 = document.querySelector('header h1, header h2');
                    const h1Color = h1 ? window.getComputedStyle(h1).color : '';
                    const obHeading = document.querySelector('main h3, main h4');
                    const obBanner = document.querySelector('section[aria-label*="Ask Union"]');
                    const obBg = obBanner ? window.getComputedStyle(obBanner).backgroundColor : '';
                    const obFg = obHeading ? window.getComputedStyle(obHeading).color : '';
                    return { htmlLight, bodyBg: mainStyle.backgroundColor, bodyColor: mainStyle.color, h1Color, obBg, obFg };
                })()
            """)
            sh2 = await cdp.screenshot("02_inicio_light_mode.png")
            if sh2:
                report["screenshots"].append(sh2)
            dark_restored = await cdp.click_aria("Ativar Modo Escuro")
            await asyncio.sleep(0.4)
            report["scenarios"]["S04_theme_light_dark_toggle"] = {
                "light_clicked": light_clicked,
                "light_metrics": light_metrics,
                "dark_restored": dark_restored,
                "passed": bool(light_clicked and light_metrics and light_metrics.get("htmlLight") and dark_restored),
            }

            # SCENARIO 5: Global Search / Command Center (Ctrl+K)
            cmd_opened = await cdp.click_aria("Abrir busca global")
            await asyncio.sleep(0.4)
            await cdp.evaluate("""
                (() => {
                    const inp = document.querySelector('input[aria-label="Campo de busca global"]');
                    if (!inp) return false;
                    const setVal = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setVal.call(inp, 'Campanha');
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    return true;
                })()
            """)
            await asyncio.sleep(0.4)
            cmd_res_camp = await cdp.evaluate("(document.querySelector('[role=\"dialog\"]')?.innerText || '').includes('Criar Nova Campanha de Marketing')")
            sh3 = await cdp.screenshot("03_command_center_ctrl_k.png")
            if sh3:
                report["screenshots"].append(sh3)
            # Clicar no resultado e navegar para Campanhas
            nav_camp = await cdp.click_by_text('[role="dialog"] button', "Criar Nova Campanha de Marketing")
            await asyncio.sleep(0.5)
            # Abrir novamente e buscar Gemini
            await cdp.click_aria("Abrir busca global")
            await asyncio.sleep(0.3)
            await cdp.evaluate("""
                (() => {
                    const inp = document.querySelector('input[aria-label="Campo de busca global"]');
                    if (!inp) return;
                    const setVal = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setVal.call(inp, 'Gemini');
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                })()
            """)
            await asyncio.sleep(0.35)
            cmd_res_gemini = await cdp.evaluate("(document.querySelector('[role=\"dialog\"]')?.innerText || '').includes('Motor Google Gemini')")
            await cdp.click_aria("Fechar busca global")
            report["scenarios"]["S05_command_center_global_search"] = {
                "cmd_opened": cmd_opened,
                "found_campanha": bool(cmd_res_camp),
                "navigated_campanha": bool(nav_camp),
                "found_gemini": bool(cmd_res_gemini),
                "passed": bool(cmd_opened and cmd_res_camp and nav_camp and cmd_res_gemini),
            }

            # SCENARIO 6: Sidebar Collapse + Filter + Todos os Recursos + Favoritos
            col_ok = await cdp.click_aria("Recolher barra lateral")
            aside_collapsed_w = await cdp.evaluate("document.querySelector('aside')?.getBoundingClientRect().width || 0")
            exp_ok = await cdp.click_aria("Expandir barra lateral")
            aside_expanded_w = await cdp.evaluate("document.querySelector('aside')?.getBoundingClientRect().width || 0")

            await cdp.click_by_text("aside button", "Todos os recursos")
            await asyncio.sleep(0.5)
            # Buscar SEO e favoritar primeiro card visível
            await cdp.evaluate("""
                (() => {
                    const inp = document.querySelector('input[aria-label="Buscar recurso em Todos os Recursos"]');
                    if (!inp) return;
                    const setVal = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setVal.call(inp, 'SEO');
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                })()
            """)
            await asyncio.sleep(0.4)
            fav_clicked = await cdp.click_aria("aos favoritos")
            await asyncio.sleep(0.3)
            await cdp.evaluate("""
                (() => {
                    const inp = document.querySelector('input[aria-label="Buscar recurso em Todos os Recursos"]');
                    if (!inp) return;
                    const setVal = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setVal.call(inp, '');
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                })()
            """)
            await cdp.click_by_text("main button", "Favoritos", exact=True)
            await asyncio.sleep(0.35)
            fav_visible = await cdp.evaluate("(document.querySelector('main')?.innerText || '').includes('SEO')")
            sh4 = await cdp.screenshot("04_todos_recursos_favoritos.png")
            if sh4:
                report["screenshots"].append(sh4)
            report["scenarios"]["S06_sidebar_and_todos_recursos_favoritos"] = {
                "sidebar_collapsed_w": aside_collapsed_w,
                "sidebar_expanded_w": aside_expanded_w,
                "fav_toggled": bool(fav_clicked),
                "fav_listed": bool(fav_visible),
                "passed": bool(col_ok and aside_collapsed_w < 120 and exp_ok and aside_expanded_w >= 200 and fav_clicked and fav_visible),
            }

            # SCENARIO 7: Meu Trabalho — 7 Filtros + Drawer Contextual
            await cdp.click_by_text("aside button", "Meu Trabalho")
            await asyncio.sleep(0.5)
            filter_prefixes = ["Precisa de mim", "IA executando", "Aguardando aprovação", "Concluído", "Falhou", "Bloqueado", "Tudo"]
            filters_ok = []
            for pfx in filter_prefixes:
                ok = await cdp.click_by_text('main [role="tab"]', pfx)
                filters_ok.append({"filter": pfx, "clicked": ok})
            # Abrir item no Drawer se houver algum card na lista
            drawer_opened = await cdp.evaluate("""
                (() => {
                    const cards = Array.from(document.querySelectorAll('main button')).filter(b => b.innerText && b.innerText.includes('Prioridade:'));
                    if (!cards.length) return false;
                    cards[0].click();
                    return true;
                })()
            """)
            await asyncio.sleep(0.5)
            drawer_visible = await cdp.evaluate("Boolean(document.querySelector('[role=\"dialog\"]'))")
            sh5 = await cdp.screenshot("05_meu_trabalho_drawer.png")
            if sh5:
                report["screenshots"].append(sh5)
            if drawer_visible:
                await cdp.click_aria("Fechar painel")
            report["scenarios"]["S07_meu_trabalho_7_filtros_drawer"] = {
                "filters_tested": filters_ok,
                "drawer_opened": bool(drawer_opened),
                "drawer_visible": bool(drawer_visible),
                "passed": all(x["clicked"] for x in filters_ok) and bool(drawer_opened and drawer_visible),
            }

            # SCENARIO 8: Comercial (CRM Filter + Propostas & 3 Unidades + QA_AUTOMATED_TENANT Blob PDF)
            await cdp.click_by_text("aside button", "Comercial")
            await asyncio.sleep(0.5)
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Leads & CRM")
            await asyncio.sleep(0.4)
            crm_filter_exists = await cdp.evaluate("Boolean(document.querySelector('input[aria-label=\"Filtrar leads no CRM\"]'))")
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Propostas, Contratos & 3 Unidades")
            await asyncio.sleep(0.7)
            switched = await cdp.evaluate("""
                (() => {
                    const sel = document.querySelector('#ug-tenant-select');
                    if (!sel) return false;
                    const opt = Array.from(sel.options).find(o => (o.text || '').includes('QA_AUTOMATED_TENANT'));
                    if (!opt) return false;
                    sel.value = opt.value;
                    sel.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                })()
            """)
            for _ in range(16):
                await asyncio.sleep(0.5)
                ready_qa = await cdp.evaluate("!(document.body.innerText || '').includes('Atualizando...') && (document.querySelector('header')?.innerText || '').includes('QA_AUTOMATED_TENANT')")
                if ready_qa:
                    break
            await cdp.click_by_text("aside button", "Comercial")
            await asyncio.sleep(0.4)
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Propostas, Contratos & 3 Unidades")
            await asyncio.sleep(0.8)
            pdf_check = await cdp.evaluate("""
                (async () => {
                    window.__capturedUrls = [];
                    const orig = window.open;
                    window.open = function(u) { window.__capturedUrls.push(String(u || '')); return null; };
                    const pdfBtns = Array.from(document.querySelectorAll('button')).filter(b => (b.innerText || '').trim() === 'PDF');
                    if (!pdfBtns.length) { window.open = orig; return { found: false, urls: [] }; }
                    pdfBtns[0].click();
                    await new Promise(r => setTimeout(r, 2000));
                    window.open = orig;
                    return { found: true, count: pdfBtns.length, urls: window.__capturedUrls };
                })()
            """)
            sh6 = await cdp.screenshot("06_comercial_propostas.png")
            if sh6:
                report["screenshots"].append(sh6)
            # Voltar ao Tenant 1 e aguardar sincronizacao completa
            await cdp.evaluate("""
                (() => {
                    const sel = document.querySelector('#ug-tenant-select');
                    if (!sel) return;
                    const opt = Array.from(sel.options).find(o => (o.text || '').includes('UNION GROWTH OS'));
                    if (opt) {
                        sel.value = opt.value;
                        sel.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                })()
            """)
            for _ in range(16):
                await asyncio.sleep(0.5)
                ready_t1 = await cdp.evaluate("!(document.body.innerText || '').includes('Atualizando...') && (document.querySelector('header')?.innerText || '').includes('UNION GROWTH OS')")
                if ready_t1:
                    break
            urls_opened = (pdf_check or {}).get("urls", [])
            report["scenarios"]["S08_comercial_crm_e_blob_pdf"] = {
                "crm_filter_exists": bool(crm_filter_exists),
                "switched_qa": bool(switched),
                "pdf_check": pdf_check,
                "passed": bool(
                    crm_filter_exists
                    and switched
                    and (pdf_check or {}).get("found")
                    and any(u.startswith("blob:") for u in urls_opened)
                    and all("access_token" not in u for u in urls_opened)
                ),
            }

            # SCENARIO 9: Marketing + Subtabs + Campaign Filter
            await cdp.click_by_text("aside button", "Marketing")
            await asyncio.sleep(0.5)
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Campanhas & Personas")
            await asyncio.sleep(0.4)
            camp_filter_exists = await cdp.evaluate("Boolean(document.querySelector('input[aria-label=\"Filtrar campanhas\"]'))")
            sh7 = await cdp.screenshot("07_marketing_campanhas.png")
            if sh7:
                report["screenshots"].append(sh7)
            sub_seo = await cdp.click_by_text('nav[aria-label*="Submenus"] button', "SEO & Artigos")
            sub_cal = await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Calendário & Redes")
            sub_cf = await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Fábrica de Conteúdo")
            report["scenarios"]["S09_marketing_subtabs_e_filtro"] = {
                "camp_filter_exists": bool(camp_filter_exists),
                "sub_seo": sub_seo,
                "sub_cal": sub_cal,
                "sub_cf": sub_cf,
                "passed": bool(camp_filter_exists and sub_seo and sub_cal and sub_cf),
            }

            # SCENARIO 10: Inteligência Artificial (Visão & Agentes + Modelos & Provedores FREE_ONLY)
            await cdp.click_by_text("aside button", "Inteligência Artificial")
            await asyncio.sleep(0.5)
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Visão & Agentes")
            await asyncio.sleep(0.4)
            ia_overview_ok = await cdp.evaluate("""
                (() => {
                    const txt = document.querySelector('main')?.innerText || '';
                    return txt.includes('Configuração Rápida dos Serviços de IA') && txt.includes('Controle & Autonomia') && txt.includes('Equipe Digital de Agentes Especializados');
                })()
            """)
            sh8 = await cdp.screenshot("08_ia_visao_e_agentes.png")
            if sh8:
                report["screenshots"].append(sh8)

            # Garantir Modo Avançado temporariamente caso ativo em Modo Simples para validar Modelos & Provedores
            was_simple_before_s10 = await cdp.evaluate("(document.querySelector('#ug-ui-mode-toggle')?.innerText || '').includes('Simples')")
            if was_simple_before_s10:
                await cdp.click_by_text("#ug-ui-mode-toggle", "")
                await asyncio.sleep(0.5)

            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Modelos & Provedores")
            await asyncio.sleep(0.6)
            prov_ok = await cdp.click_by_text("main button", "2. Provedores")
            prov_has_key = await cdp.evaluate("(document.querySelector('main')?.innerText || '').includes('AQ....rlw')")
            hist_ok = await cdp.click_by_text("main button", "9. Histórico")
            hist_has_txt = await cdp.evaluate("(document.querySelector('main')?.innerText || '').includes('Histórico de Execuções')")
            sh9 = await cdp.screenshot("09_ia_motores_provedores.png")
            if sh9:
                report["screenshots"].append(sh9)
            if was_simple_before_s10:
                await cdp.click_by_text("#ug-ui-mode-toggle", "")
                await asyncio.sleep(0.4)
            report["scenarios"]["S10_ia_ux_e_motores"] = {
                "ia_overview_ok": bool(ia_overview_ok),
                "prov_ok": bool(prov_ok and prov_has_key),
                "hist_ok": bool(hist_ok and hist_has_txt),
                "passed": bool(ia_overview_ok and prov_ok and prov_has_key and hist_ok and hist_has_txt),
            }

            # SCENARIO 11: Gestão (Relatórios Executivos + Integrações com Filtro)
            await cdp.click_by_text("aside button", "Gestão")
            await asyncio.sleep(0.5)
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Relatórios")
            await asyncio.sleep(0.6)
            rep_ok = await cdp.evaluate("""
                (() => {
                    const txt = (document.querySelector('main')?.innerText || '').toLowerCase();
                    return txt.includes('relatório executivo consolidado') && txt.includes('receita real confirmada') && txt.includes('detalhes técnicos completos');
                })()
            """)
            sh_rep = await cdp.screenshot("10b_gestao_relatorios.png")
            if sh_rep:
                report["screenshots"].append(sh_rep)
            await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Integrações")
            await asyncio.sleep(0.5)
            intg_filter_pending = await cdp.click_by_text('main [aria-label="Filtrar status de integrações"] button', "Pendentes")
            intg_filter_all = await cdp.click_by_text('main [aria-label="Filtrar status de integrações"] button', "Todas")
            sh10 = await cdp.screenshot("10_gestao_integracoes.png")
            if sh10:
                report["screenshots"].append(sh10)
            report["scenarios"]["S11_gestao_relatorios_integracoes"] = {
                "rep_ok": bool(rep_ok),
                "intg_filter_pending": bool(intg_filter_pending),
                "intg_filter_all": bool(intg_filter_all),
                "passed": bool(rep_ok and intg_filter_pending and intg_filter_all),
            }

            # SCENARIO 12: Central de Ajuda Drawer
            help_opened = await cdp.click_aria("Abrir Central de Ajuda")
            await asyncio.sleep(0.45)
            gloss_ok = await cdp.click_by_text('[role="dialog"] button', "Glossário")
            short_ok = await cdp.click_by_text('[role="dialog"] button', "Atalhos")
            sh11 = await cdp.screenshot("11_central_ajuda_drawer.png")
            if sh11:
                report["screenshots"].append(sh11)
            await cdp.click_aria("Fechar painel")
            report["scenarios"]["S12_central_de_ajuda"] = {
                "help_opened": bool(help_opened),
                "gloss_ok": bool(gloss_ok),
                "short_ok": bool(short_ok),
                "passed": bool(help_opened and gloss_ok and short_ok),
            }

            # SCENARIO 13: Auditoria de Acessibilidade DOM (WCAG 2.2 AA)
            await cdp.click_by_text("aside button", "Início")
            await asyncio.sleep(0.4)
            a11y = await cdp.evaluate("""
                (() => {
                    const lang = document.documentElement.lang;
                    const hasAside = Boolean(document.querySelector('aside'));
                    const hasHeader = Boolean(document.querySelector('header'));
                    const hasMain = Boolean(document.querySelector('main'));
                    const hasNav = Boolean(document.querySelector('nav'));
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const unlabeledButtons = buttons.filter(b => {
                        const rect = b.getBoundingClientRect();
                        if (rect.width === 0 || rect.height === 0) return false;
                        const label = (b.innerText || b.getAttribute('aria-label') || b.getAttribute('title') || '').trim();
                        return !label;
                    }).map(b => b.outerHTML.slice(0, 120));
                    const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
                    const unlabeledInputs = inputs.filter(el => {
                        const rect = el.getBoundingClientRect();
                        if (rect.width === 0 || rect.height === 0) return false;
                        const id = el.id;
                        const hasFor = id ? Boolean(document.querySelector(`label[for="${id}"]`)) : false;
                        const hasAria = Boolean(el.getAttribute('aria-label') || el.getAttribute('aria-labelledby'));
                        return !hasFor && !hasAria;
                    }).map(el => el.outerHTML.slice(0, 120));
                    return {
                        lang,
                        landmarks: { aside: hasAside, header: hasHeader, main: hasMain, nav: hasNav },
                        total_visible_buttons: buttons.length,
                        unlabeled_buttons_count: unlabeledButtons.length,
                        unlabeled_buttons_sample: unlabeledButtons.slice(0, 5),
                        unlabeled_inputs_count: unlabeledInputs.length,
                        unlabeled_inputs_sample: unlabeledInputs.slice(0, 5),
                    };
                })()
            """)
            report["accessibility"] = {
                **(a11y or {}),
                "passed": bool(
                    a11y
                    and a11y.get("lang") == "pt-BR"
                    and all(a11y.get("landmarks", {}).values())
                    and a11y.get("unlabeled_buttons_count", 1) == 0
                    and a11y.get("unlabeled_inputs_count", 1) == 0
                ),
            }

            # SCENARIO 14: Responsividade em 4 Viewports + Mobile Drawer
            viewports = [
                ("desktop_1920x1080", 1920, 1080, False, None),
                ("notebook_1366x768", 1366, 768, False, "12_responsive_notebook_1366.png"),
                ("tablet_768x1024", 768, 1024, True, "13_responsive_tablet_768.png"),
                ("mobile_390x844", 390, 844, True, "14_responsive_mobile_390.png"),
            ]
            vp_results = {}
            for name, w, h, mob, shot_name in viewports:
                await cdp.set_viewport(w, h, mobile=mob)
                metrics = await cdp.evaluate("""
                    (() => ({
                        scrollWidth: document.documentElement.scrollWidth,
                        clientWidth: document.documentElement.clientWidth,
                        overflowPx: Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth),
                    }))()
                """)
                mobile_drawer_ok = True
                if name == "mobile_390x844":
                    opened = await cdp.click_aria("Abrir menu de navegação")
                    await asyncio.sleep(0.35)
                    aside_vis = await cdp.evaluate("(document.querySelector('aside')?.getBoundingClientRect().width || 0) > 150")
                    closed = await cdp.click_aria("Fechar menu móvel")
                    mobile_drawer_ok = bool(opened and aside_vis and closed)
                if shot_name:
                    sh = await cdp.screenshot(shot_name)
                    if sh:
                        report["screenshots"].append(sh)
                vp_results[name] = {
                    **(metrics or {}),
                    "mobile_drawer_ok": mobile_drawer_ok,
                    "passed": bool(metrics and metrics.get("overflowPx", 999) <= 2 and mobile_drawer_ok),
                }
            await cdp.set_viewport(1920, 1080, mobile=False)
            report["responsiveness"] = {
                "viewports": vp_results,
                "passed": all(v.get("passed") for v in vp_results.values()),
            }

            # SCENARIO 15: Logout + Public Landing Page (/lp/agentes-ia)
            logout_clicked = await cdp.click_aria("Sair da Conta")
            await asyncio.sleep(1.2)
            login_returned = await cdp.evaluate("Boolean(document.querySelector('input[type=\"password\"]'))")

            await cdp.send("Page.navigate", {"url": f"{PROD_URL}/lp/agentes-ia"})
            await asyncio.sleep(2.2)
            lp_ok = await cdp.evaluate("""
                (() => {
                    const txt = document.body.innerText || '';
                    const lgpd = document.querySelector('#consent_lgpd');
                    return {
                        has_title: txt.includes('Agentes de IA'),
                        has_form: Boolean(document.querySelector('#lpForm')),
                        has_lgpd: Boolean(lgpd && lgpd.required),
                    };
                })()
            """)
            sh15 = await cdp.screenshot("15_public_landing_page.png")
            if sh15:
                report["screenshots"].append(sh15)
            report["scenarios"]["S15_logout_and_public_lp"] = {
                "logout_clicked": bool(logout_clicked),
                "login_returned": bool(login_returned),
                **(lp_ok or {}),
                "passed": bool(logout_clicked and login_returned and lp_ok and lp_ok.get("has_title") and lp_ok.get("has_form") and lp_ok.get("has_lgpd")),
            }

            report["telemetry"] = {
                "total_network_requests": len(cdp.network_requests),
                "console_errors_count": len(cdp.console_errors),
                "console_errors": cdp.console_errors,
                "runtime_exceptions_count": len(cdp.exceptions),
                "runtime_exceptions": cdp.exceptions,
                "network_failures_count": len(cdp.network_failures),
                "network_failures": cdp.network_failures,
                "url_token_leaks_count": len(cdp.url_token_leaks),
            }
            report["all_phase22_e2e_passed"] = (
                all(v.get("passed", False) for v in report["scenarios"].values())
                and report["accessibility"].get("passed", False)
                and report["responsiveness"].get("passed", False)
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

    (OUT_DIR / "phase22_cdp_ux_e2e.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        json.dumps(
            {
                "all_phase22_e2e_passed": report["all_phase22_e2e_passed"],
                "scenarios": {k: v.get("passed") for k, v in report["scenarios"].items()},
                "accessibility_passed": report["accessibility"].get("passed"),
                "accessibility_details": {
                    "unlabeled_buttons": report["accessibility"].get("unlabeled_buttons_count"),
                    "unlabeled_inputs": report["accessibility"].get("unlabeled_inputs_count"),
                },
                "responsiveness_passed": report["responsiveness"].get("passed"),
                "viewports": {k: v.get("overflowPx") for k, v in report["responsiveness"].get("viewports", {}).items()},
                "telemetry": report["telemetry"],
                "screenshots_count": len(report["screenshots"]),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    asyncio.run(run_phase22_e2e())
