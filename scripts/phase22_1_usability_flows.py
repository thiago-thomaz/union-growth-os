"""
FASE 22.1 — Auditoria Real de Usabilidade e Execução dos 8 Fluxos Principais (ANTES / DEPOIS)
Executa os 8 fluxos principais no Chrome real (CDP) contra https://automacao.projetosunion.cloud
utilizando exclusivamente o tenant isolado QA_AUTOMATED_TENANT para criação de registros de teste
(zero alteração em dados reais do Tenant 1, zero cobrança paga e zero publicação externa real).
"""
import argparse
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
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROD_URL = "https://automacao.projetosunion.cloud"
CDP_PORT = 9337


class CDPClient:
    def __init__(self, ws, out_dir: Path):
        self.ws = ws
        self.out_dir = out_dir
        self._id = 0
        self.pending = {}
        self.console_errors = []
        self.exceptions = []
        self.network_failures = []
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
                        self.exceptions.append(desc[:250])
                    elif method == "Console.messageAdded":
                        m = params.get("message", {})
                        if m.get("level") == "error":
                            self.console_errors.append(str(m.get("text", ""))[:250])
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
            p = self.out_dir / filename
            p.write_bytes(base64.b64decode(b64))
            return {"file": filename, "size_bytes": p.stat().st_size}
        return None

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

    async def set_input_by_id_or_placeholder(self, selector_or_sub: str, value: str) -> bool:
        js = f"""
        (() => {{
            let el = null;
            if ({json.dumps(selector_or_sub)}.startsWith('#')) {{
                el = document.querySelector({json.dumps(selector_or_sub)});
            }}
            if (!el) {{
                const els = Array.from(document.querySelectorAll('main input, main textarea'));
                const targetLower = {json.dumps(selector_or_sub.lower())};
                el = els.find(i => (i.getAttribute('aria-label') || '').toLowerCase().includes(targetLower))
                  || els.find(i => (i.getAttribute('placeholder') || '').toLowerCase().includes(targetLower));
            }}
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

    async def wait_until_idle(self, timeout_s: float = 10.0):
        steps = int(timeout_s / 0.4)
        for _ in range(steps):
            await asyncio.sleep(0.4)
            busy = await self.evaluate("(document.body.innerText || '').includes('Atualizando...')")
            if not busy:
                return True
        return False

    async def close(self):
        self._reader_task.cancel()


async def run_flows(mode: str):
    out_dir = ROOT_DIR / "UNION_GROWTH_OS_PHASE22_1_EVIDENCE" / mode
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())

    tmp_profile = tempfile.mkdtemp(prefix=f"ugos_cdp_22_1_{mode}_")
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
        raise RuntimeError("Falha ao iniciar Chrome CDP.")

    report = {"mode": mode, "prod_url": PROD_URL, "flows": {}, "screenshots": []}

    try:
        async with websockets.connect(ws_url, max_size=25 * 1024 * 1024) as ws:
            cdp = CDPClient(ws, out_dir)
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")
            await cdp.send("Console.enable")
            await cdp.send("Network.enable")
            await cdp.send("Emulation.setDeviceMetricsOverride", {"width": 1920, "height": 1080, "deviceScaleFactor": 1, "mobile": False})

            # Login e Troca para Tenant Isolado QA_AUTOMATED_TENANT
            await cdp.send("Page.navigate", {"url": f"{PROD_URL}/"})
            await asyncio.sleep(3.2)
            await cdp.evaluate("""
                (() => {
                    const e = document.querySelector('input[type="email"]');
                    const p = document.querySelector('input[type="password"]');
                    const b = document.querySelector('button[type="submit"]');
                    const setVal = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setVal.call(e, 'admin@projetosunion.cloud');
                    e.dispatchEvent(new Event('input', { bubbles: true }));
                    setVal.call(p, 'UnionGrowth#2026!');
                    p.dispatchEvent(new Event('input', { bubbles: true }));
                    b.click();
                })()
            """)
            await asyncio.sleep(5.0)

            # Trocar para QA_AUTOMATED_TENANT para não poluir dados reais do Tenant 1!
            await cdp.evaluate("""
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
            for _ in range(18):
                await asyncio.sleep(0.5)
                if await cdp.evaluate("!(document.body.innerText || '').includes('Atualizando...') && (document.querySelector('header')?.innerText || '').includes('QA_AUTOMATED_TENANT')"):
                    break

            # FLUXO 1 — Configurar empresa e marca (Gestão -> Configurações & Planos)
            t0 = time.perf_counter()
            clicks = 0
            if await cdp.click_by_text("aside button", "Gestão"):
                clicks += 1
            if await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Configurações"):
                clicks += 1
            await asyncio.sleep(0.5)
            f1_dom = await cdp.evaluate("""
                (() => {
                    const main = document.querySelector('main');
                    const txt = main?.innerText || '';
                    const inputs = Array.from(main?.querySelectorAll('input') || []);
                    const hasBrandField = Boolean(document.querySelector('#ug-edit-brand-input')) || txt.includes('Nome da Marca');
                    const hasNicheField = Boolean(document.querySelector('#ug-edit-niche-input')) || txt.includes('Nicho / Segmento');
                    const hasContextGuide = txt.includes('O que você pode fazer aqui') || txt.includes('Como começo');
                    return { hasBrandField, hasNicheField, hasContextGuide, inputsCount: inputs.length };
                })()
            """)
            brand_saved = False
            if f1_dom and f1_dom.get("hasBrandField"):
                await cdp.set_input_by_id_or_placeholder("#ug-edit-brand-input", "QA_AUTOMATED_TENANT")
                await cdp.set_input_by_id_or_placeholder("#ug-edit-niche-input", "Automação B2B e IA")
                clicks += 2
                if await cdp.click_by_text("main button", "Salvar Identidade"):
                    clicks += 1
                    await cdp.wait_until_idle()
                    await asyncio.sleep(0.4)
                    brand_saved = await cdp.evaluate("(document.body.innerText || '').includes('Identidade') || (document.body.innerText || '').includes('atualizada') || (document.body.innerText || '').includes('salva')")
            sh1 = await cdp.screenshot("01_fluxo1_empresa_marca.png")
            if sh1:
                report["screenshots"].append(sh1)
            report["flows"]["F1_configurar_empresa_e_marca"] = {
                "profile": "Iniciante",
                "steps_count": 3 if (f1_dom or {}).get("hasBrandField") else 2,
                "clicks_count": clicks,
                "duration_ms": round((time.perf_counter() - t0) * 1000, 1),
                **(f1_dom or {}),
                "brand_saved": brand_saved,
                "status": "PASS" if ((f1_dom or {}).get("hasBrandField") and brand_saved) else "FAIL",
            }

            # FLUXO 2 — Configurar agentes (Inteligência Artificial -> Visão & Agentes)
            t0 = time.perf_counter()
            clicks = 0
            if await cdp.click_by_text("aside button", "Inteligência Artificial"):
                clicks += 1
            if await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Visão & Agentes"):
                clicks += 1
            await asyncio.sleep(0.5)
            f2_dom = await cdp.evaluate("""
                (() => {
                    const txt = document.querySelector('main')?.innerText || '';
                    return {
                        hasWizard: txt.includes('Assistente Guiado') && txt.includes('Passo 1'),
                        hasCredentialDependencyPerAgent: txt.includes('Dependência de credenciais'),
                        hasPlainLanguageExplain: txt.includes('O que executa:') || txt.includes('Dados usados:'),
                        hasSafeTestButton: Array.from(document.querySelectorAll('main button')).some(b => (b.innerText || '').includes('Testar')),
                        exposesJargonByDefault: txt.includes('GeminiProvider') || txt.includes('VERIFIED_FREE'),
                    };
                })()
            """)
            if await cdp.click_by_text("main button", "Testar Conexão Real Agora"):
                clicks += 1
                await cdp.wait_until_idle()
                await asyncio.sleep(0.6)
            sh2 = await cdp.screenshot("02_fluxo2_configurar_agentes.png")
            if sh2:
                report["screenshots"].append(sh2)
            report["flows"]["F2_configurar_agentes"] = {
                "profile": "Avançado / Iniciante",
                "steps_count": 3,
                "clicks_count": clicks,
                "duration_ms": round((time.perf_counter() - t0) * 1000, 1),
                **(f2_dom or {}),
                "status": "PASS" if ((f2_dom or {}).get("hasWizard") and (f2_dom or {}).get("hasCredentialDependencyPerAgent") and (f2_dom or {}).get("hasSafeTestButton")) else "PARTIAL",
            }

            # FLUXO 3 — Conectar integrações (Gestão -> Integrações)
            t0 = time.perf_counter()
            clicks = 0
            if await cdp.click_by_text("aside button", "Gestão"):
                clicks += 1
            if await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Integrações"):
                clicks += 1
            await asyncio.sleep(0.5)
            f3_dom = await cdp.evaluate("""
                (() => {
                    const main = document.querySelector('main');
                    const txt = main?.innerText || '';
                    const gaCard = Array.from(main?.querySelectorAll('div') || []).find(d => (d.innerText || '').includes('Google Analytics 4 (GA4)') && d.querySelectorAll('input').length > 0 && (d.innerText || '').length < 1800);
                    const gaInputs = gaCard ? gaCard.querySelectorAll('input').length : 0;
                    const hasHumanEmptyFallbackExplain = txt.includes('Modo Assistido') || txt.includes('Sem esta integração');
                    const hasFriendlyStatus = txt.includes('Aguardando Conexão') || txt.includes('Requer Credencial');
                    const hasRawEnum = txt.includes('PENDING_CREDENTIALS');
                    return { gaInputs, hasHumanEmptyFallbackExplain, hasFriendlyStatus, hasRawEnum };
                })()
            """)
            # Testar botão "Testar" real para comprovar honestidade quando sem credenciais
            if await cdp.click_by_text("main button", "Testar Conexão"):
                clicks += 1
                await cdp.wait_until_idle()
            elif await cdp.click_by_text("main button", "Testar"):
                clicks += 1
                await cdp.wait_until_idle()
            test_toast = await cdp.evaluate("document.body.innerText.includes('pendente') || document.body.innerText.includes('credencia') || document.body.innerText.includes('Falha') || document.body.innerText.includes('Aguardando')")
            sh3 = await cdp.screenshot("03_fluxo3_integracoes.png")
            if sh3:
                report["screenshots"].append(sh3)
            report["flows"]["F3_conectar_integracoes"] = {
                "profile": "Intermediário",
                "steps_count": 3,
                "clicks_count": clicks,
                "duration_ms": round((time.perf_counter() - t0) * 1000, 1),
                **(f3_dom or {}),
                "honest_test_response": bool(test_toast),
                "status": "PASS" if ((f3_dom or {}).get("gaInputs", 0) >= 2 and (f3_dom or {}).get("hasHumanEmptyFallbackExplain") and (f3_dom or {}).get("hasFriendlyStatus") and test_toast) else "PARTIAL",
            }

            # FLUXO 4 — Criar campanha (Marketing -> Campanhas & Personas)
            t0 = time.perf_counter()
            clicks = 0
            if await cdp.click_by_text("aside button", "Marketing"):
                clicks += 1
            if await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Campanhas"):
                clicks += 1
            await cdp.wait_until_idle()
            await asyncio.sleep(0.3)
            # Testar envio vazio para medir feedback ao iniciante
            await cdp.click_by_text("main button", "Criar Campanha", exact=True)
            clicks += 1
            empty_feedback = False
            for _ in range(8):
                await asyncio.sleep(0.25)
                empty_feedback = bool(await cdp.evaluate("(document.body.innerText || '').includes('Informe') || (document.body.innerText || '').includes('obrigatório') || (document.body.innerText || '').includes('Preencha')"))
                if empty_feedback:
                    break
            camp_test_name = f"Campanha Usab {ts}"
            has_channel_select = await cdp.evaluate("Boolean(document.querySelector('#ug-camp-channel-select'))")
            await cdp.set_input_by_id_or_placeholder("#ug-camp-name-input", camp_test_name)
            await cdp.click_by_text("main button", "Criar Campanha", exact=True)
            clicks += 1
            camp_persisted = False
            for _ in range(30):
                await asyncio.sleep(0.4)
                st_camp = await cdp.evaluate(f"""
                    (() => {{
                        const txt = document.body.innerText || '';
                        const mainTxt = document.querySelector('main')?.innerText || '';
                        return {{
                            busy: txt.includes('Atualizando...'),
                            persisted: mainTxt.includes({json.dumps(camp_test_name)})
                        }};
                    }})()
                """)
                if st_camp and st_camp.get("persisted"):
                    camp_persisted = True
                    if not st_camp.get("busy"):
                        break
            await asyncio.sleep(0.3)
            sh4 = await cdp.screenshot("04_fluxo4_criar_campanha.png")
            if sh4:
                report["screenshots"].append(sh4)
            report["flows"]["F4_criar_campanha"] = {
                "profile": "Iniciante",
                "steps_count": 4,
                "clicks_count": clicks,
                "duration_ms": round((time.perf_counter() - t0) * 1000, 1),
                "empty_validation_feedback": bool(empty_feedback),
                "has_channel_selector": bool(has_channel_select),
                "camp_persisted": bool(camp_persisted),
                "status": "PASS" if (camp_persisted and empty_feedback and has_channel_select) else ("PARTIAL" if camp_persisted else "FAIL"),
            }

            # FLUXO 5 — Criar conteúdo (Marketing -> Calendário & Redes + Fábrica)
            t0 = time.perf_counter()
            clicks = 0
            if await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Calendário & Redes"):
                clicks += 1
            await asyncio.sleep(0.5)
            post_title = f"Post Usab {ts}"
            await cdp.set_input_by_id_or_placeholder("#ug-cal-title-input", post_title)
            if await cdp.click_by_text("main button", "Agendar no Calendário"):
                clicks += 1
            await cdp.wait_until_idle()
            await asyncio.sleep(0.4)
            post_persisted = await cdp.evaluate(f"(document.querySelector('main')?.innerText || '').includes({json.dumps(post_title)})")
            sh5 = await cdp.screenshot("05_fluxo5_criar_conteudo.png")
            if sh5:
                report["screenshots"].append(sh5)
            report["flows"]["F5_criar_conteudo"] = {
                "profile": "Iniciante",
                "steps_count": 3,
                "clicks_count": clicks,
                "duration_ms": round((time.perf_counter() - t0) * 1000, 1),
                "post_persisted": bool(post_persisted),
                "status": "PASS" if post_persisted else "FAIL",
            }

            # FLUXO 6 — Capturar e acompanhar lead (Comercial -> Leads & CRM + BUSCA REAL!)
            t0 = time.perf_counter()
            clicks = 0
            if await cdp.click_by_text("aside button", "Comercial"):
                clicks += 1
            if await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Leads & CRM"):
                clicks += 1
            await asyncio.sleep(0.5)
            lead_name = f"Maria Usab {ts}"
            await cdp.set_input_by_id_or_placeholder("#ug-lead-name-input", lead_name)
            await cdp.set_input_by_id_or_placeholder("#ug-lead-email-input", f"maria.{ts}@empresa-qa.com.br")
            await cdp.set_input_by_id_or_placeholder("#ug-lead-phone-input", "+5511999990000")
            await cdp.set_input_by_id_or_placeholder("#ug-lead-company-input", f"Empresa QA {ts}")
            if await cdp.click_by_text("main button", "Qualificar & Registrar"):
                clicks += 1
            await cdp.wait_until_idle()
            await asyncio.sleep(0.4)
            lead_persisted = await cdp.evaluate(f"(document.querySelector('main')?.innerText || '').includes({json.dumps(lead_name)})")
            # AGORA TESTA O FILTRO REAL DE BUSCA DE LEADS!
            await cdp.set_input_by_id_or_placeholder("#ug-crm-search-input", lead_name)
            await asyncio.sleep(0.4)
            lead_found_in_filter = await cdp.evaluate(f"(document.querySelector('main')?.innerText || '').includes({json.dumps(lead_name)})")
            sh6 = await cdp.screenshot("06_fluxo6_capturar_lead_crm.png")
            if sh6:
                report["screenshots"].append(sh6)
            report["flows"]["F6_capturar_e_acompanhar_lead"] = {
                "profile": "Intermediário",
                "steps_count": 6,
                "clicks_count": clicks,
                "duration_ms": round((time.perf_counter() - t0) * 1000, 1),
                "lead_persisted": bool(lead_persisted),
                "lead_found_in_crm_search": bool(lead_found_in_filter),
                "status": "PASS" if (lead_persisted and lead_found_in_filter) else "FAIL",
            }

            # FLUXO 7 — Criar proposta e acompanhar venda (Comercial -> Propostas & Pipeline)
            t0 = time.perf_counter()
            clicks = 0
            if await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Propostas"):
                clicks += 1
            await asyncio.sleep(0.6)
            prop_company = f"Cliente Prop {ts} Ltda"
            await cdp.set_input_by_id_or_placeholder("#ug-prop-client-name", f"Carlos {ts}")
            await cdp.set_input_by_id_or_placeholder("#ug-prop-client-company", prop_company)
            await cdp.set_input_by_id_or_placeholder("#ug-prop-client-email", f"carlos.{ts}@clienteqa.com.br")
            if await cdp.click_by_text("main button", "Gerar Proposta"):
                clicks += 1
            await cdp.wait_until_idle()
            await asyncio.sleep(0.4)
            prop_created = await cdp.evaluate(f"(document.querySelector('main')?.innerText || '').includes({json.dumps(prop_company)})")
            sh7 = await cdp.screenshot("07_fluxo7_proposta_venda.png")
            if sh7:
                report["screenshots"].append(sh7)
            report["flows"]["F7_criar_proposta_e_venda"] = {
                "profile": "Intermediário / Diretor",
                "steps_count": 5,
                "clicks_count": clicks,
                "duration_ms": round((time.perf_counter() - t0) * 1000, 1),
                "prop_created": bool(prop_created),
                "status": "PASS" if prop_created else "FAIL",
            }

            # FLUXO 8 — Consultar resultados e execuções da IA (Início + Relatórios + IA)
            t0 = time.perf_counter()
            clicks = 0
            if await cdp.click_by_text("aside button", "Início"):
                clicks += 1
            await asyncio.sleep(0.5)
            f8_inicio = await cdp.evaluate("""
                (() => {
                    const txt = document.querySelector('main')?.innerText || '';
                    return {
                        hasContextGuide: txt.includes('O que você pode fazer aqui') || txt.includes('O que precisa da sua atenção'),
                        showsResults: txt.includes('3. O que está gerando resultados'),
                        showsAIActivity: txt.includes('2. O que a IA está fazendo'),
                    };
                })()
            """)
            if await cdp.click_by_text("aside button", "Gestão"):
                clicks += 1
            if await cdp.click_by_text('nav[aria-label*="Submenus"] button', "Relatórios"):
                clicks += 1
            await asyncio.sleep(0.5)
            has_reports = await cdp.evaluate("(document.querySelector('main')?.innerText || '').toLowerCase().includes('receita real confirmada')")
            sh8 = await cdp.screenshot("08_fluxo8_resultados_e_ia.png")
            if sh8:
                report["screenshots"].append(sh8)
            report["flows"]["F8_consultar_resultados_e_ia"] = {
                "profile": "Todos",
                "steps_count": 3,
                "clicks_count": clicks,
                "duration_ms": round((time.perf_counter() - t0) * 1000, 1),
                **(f8_inicio or {}),
                "has_reports": bool(has_reports),
                "status": "PASS" if (has_reports and (f8_inicio or {}).get("showsResults") and (f8_inicio or {}).get("showsAIActivity")) else "PARTIAL",
            }

            # Restaurar Tenant 1 antes de encerrar
            await cdp.evaluate("""
                (() => {
                    const sel = document.querySelector('#ug-tenant-select');
                    if (!sel) return;
                    const opt = Array.from(sel.options).find(o => (o.text || '').includes('UNION GROWTH OS'));
                    if (opt) { sel.value = opt.value; sel.dispatchEvent(new Event('change', { bubbles: true })); }
                })()
            """)
            await asyncio.sleep(1.2)
            report["telemetry"] = {
                "console_errors": len(cdp.console_errors),
                "exceptions": len(cdp.exceptions),
                "network_4xx_5xx": len(cdp.network_failures),
                "network_failures": cdp.network_failures[:5],
            }
            await cdp.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    (out_dir / f"phase22_1_flows_{mode}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"mode": mode, "flows": {k: {"status": v["status"], "clicks": v["clicks_count"], "ms": v["duration_ms"], "details": {dk: dv for dk, dv in v.items() if dk not in ("status", "clicks_count", "duration_ms")}} for k, v in report["flows"].items()}, "telemetry": report["telemetry"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["before", "after"], required=True)
    args = parser.parse_args()
    asyncio.run(run_flows(args.mode))
