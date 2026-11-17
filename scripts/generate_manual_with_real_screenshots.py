#!/usr/bin/env python3
"""
Gera o Manual Oficial de Uso do UNION GROWTH OS com:
1. Captura de 10 screenshots reais em alta resolução (1440x950) diretamente da produção https://automacao.projetosunion.cloud
2. Geração do documento Word (.docx) completo com imagens reais embutidas
3. Geração do documento PDF (.pdf) completo com imagens reais embutidas
"""

import asyncio
import base64
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import httpx
import websockets
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BASE_URL = "https://automacao.projetosunion.cloud"
ADMIN_EMAIL = "admin@projetosunion.cloud"
ADMIN_PASS = "UnionGrowth#2026!"

ROOT_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = ROOT_DIR / "docs" / "manual" / "screenshots"
PUBLIC_MANUAL_DIR = ROOT_DIR / "frontend" / "public" / "manual"
OUT_MANUAL_DIR = ROOT_DIR / "frontend" / "out" / "manual"
ARTIFACT_DIR = Path(r"C:\Users\Thiago Thomaz\.gemini\antigravity\brain\fa8e9ad9-decb-4e71-be16-10aafa90bb28")

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


async def cdp_call(ws, method: str, params: dict | None = None, msg_id: int = 1) -> dict:
    payload = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(payload))
    while True:
        raw = await ws.recv()
        data = json.loads(raw)
        if data.get("id") == msg_id:
            return data


async def capture_screenshot(ws, out_path: Path, msg_id: int):
    res = await cdp_call(ws, "Page.captureScreenshot", {"format": "png", "fromSurface": True}, msg_id=msg_id)
    b64_data = res["result"]["data"]
    img_bytes = base64.b64decode(b64_data)
    out_path.write_bytes(img_bytes)
    # Copiar também para o diretório de artifacts do chat
    if ARTIFACT_DIR.exists():
        shutil.copy2(out_path, ARTIFACT_DIR / out_path.name)
    print(f"  [SCREENSHOT] Salvo: {out_path.name} ({len(img_bytes) // 1024} KB)")


async def capture_all_production_screenshots() -> list[dict]:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_MANUAL_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MANUAL_DIR.mkdir(parents=True, exist_ok=True)

    chrome_bin = next((p for p in CHROME_PATHS if os.path.exists(p)), None)
    if not chrome_bin:
        raise RuntimeError("Navegador Chrome/Edge não encontrado para captura de screenshots.")

    # Obter token real de produção
    with httpx.Client(timeout=20.0) as client:
        r_login = client.post(f"{BASE_URL}/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
        r_login.raise_for_status()
        jwt_token = r_login.json()["access_token"]

    user_data_dir = ROOT_DIR / "data" / "chrome_manual_profile"
    user_data_dir.mkdir(parents=True, exist_ok=True)
    port = 9244

    proc = subprocess.Popen(
        [
            chrome_bin,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--window-size=1440,950",
            f"--remote-debugging-port={port}",
            f"--user-data-dir={user_data_dir}",
            BASE_URL,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        # Aguardar inicialização do CDP
        ws_url = None
        for _ in range(30):
            try:
                tabs = httpx.get(f"http://127.0.0.1:{port}/json", timeout=2.0).json()
                page_tab = next((t for t in tabs if t.get("type") == "page"), None)
                if page_tab and page_tab.get("webSocketDebuggerUrl"):
                    ws_url = page_tab["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if not ws_url:
            raise RuntimeError("Não foi possível conectar ao Chrome DevTools Protocol.")

        async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
            msg_id = 1
            await cdp_call(ws, "Page.enable", msg_id=msg_id); msg_id += 1
            await cdp_call(ws, "Runtime.enable", msg_id=msg_id); msg_id += 1
            await cdp_call(
                ws,
                "Emulation.setDeviceMetricsOverride",
                {"width": 1440, "height": 950, "deviceScaleFactor": 1.25, "mobile": False},
                msg_id=msg_id,
            ); msg_id += 1

            # 1. Limpar localStorage para garantir que a Tela de Login apareça limpa
            await cdp_call(ws, "Runtime.evaluate", {"expression": "localStorage.clear(); location.reload();"}, msg_id=msg_id); msg_id += 1
            await asyncio.sleep(3.5)

            s1 = SCREENSHOTS_DIR / "01_tela_login.png"
            await capture_screenshot(ws, s1, msg_id); msg_id += 1

            # 2. Injetar o token JWT real de produção e recarregar na Visão Geral
            js_login = f"localStorage.setItem('ug_token', '{jwt_token}'); location.reload();"
            await cdp_call(ws, "Runtime.evaluate", {"expression": js_login}, msg_id=msg_id); msg_id += 1
            await asyncio.sleep(5.5)

            s2 = SCREENSHOTS_DIR / "02_visao_geral.png"
            await capture_screenshot(ws, s2, msg_id); msg_id += 1

            # Função auxiliar para clicar em um item do menu lateral pelo texto
            async def click_menu_by_text(label_substring: str, wait_sec: float = 2.5, scroll_y: int = 0):
                nonlocal msg_id
                js_click = f"""
                (() => {{
                  const btns = Array.from(document.querySelectorAll('aside button'));
                  const target = btns.find(b => b.innerText.includes({json.dumps(label_substring)}));
                  if (target) target.click();
                  window.scrollTo(0, {scroll_y});
                  return target ? target.innerText : 'NOT_FOUND';
                }})()
                """
                await cdp_call(ws, "Runtime.evaluate", {"expression": js_click}, msg_id=msg_id); msg_id += 1
                await asyncio.sleep(wait_sec)
                if scroll_y > 0:
                    await cdp_call(
                        ws,
                        "Runtime.evaluate",
                        {"expression": f"window.scrollTo(0, {scroll_y}); document.querySelector('main')?.scrollTo(0, {scroll_y});"},
                        msg_id=msg_id,
                    ); msg_id += 1
                    await asyncio.sleep(0.8)

            # 3. Multinegócio (Topo: 3 Unidades, Painel 5 Blocos Fase 18.1 e Funil)
            await click_menu_by_text("Multinegócio", wait_sec=3.0, scroll_y=0)
            s3 = SCREENSHOTS_DIR / "03_multinegocio_3_unidades.png"
            await capture_screenshot(ws, s3, msg_id); msg_id += 1

            # 4. Multinegócio (Parte Inferior: Catálogo 7 Serviços, Propostas, Pagamentos Sandbox & Entregas)
            await click_menu_by_text("Multinegócio", wait_sec=1.0, scroll_y=720)
            s4 = SCREENSHOTS_DIR / "04_servicos_propostas_pagamentos.png"
            await capture_screenshot(ws, s4, msg_id); msg_id += 1

            # 5. AI CEO
            await click_menu_by_text("AI CEO", wait_sec=2.0, scroll_y=0)
            s5 = SCREENSHOTS_DIR / "05_ai_ceo.png"
            await capture_screenshot(ws, s5, msg_id); msg_id += 1

            # 6. Content Factory 30D
            await click_menu_by_text("Content Factory", wait_sec=2.2, scroll_y=0)
            s6 = SCREENSHOTS_DIR / "06_content_factory.png"
            await capture_screenshot(ws, s6, msg_id); msg_id += 1

            # 7. Painel 24/7 & Alertas
            await click_menu_by_text("Painel 24/7", wait_sec=2.2, scroll_y=0)
            s7 = SCREENSHOTS_DIR / "07_painel_24_7.png"
            await capture_screenshot(ws, s7, msg_id); msg_id += 1

            # 8. CRM & Leads
            await click_menu_by_text("CRM & Leads", wait_sec=2.0, scroll_y=0)
            s8 = SCREENSHOTS_DIR / "08_crm_leads.png"
            await capture_screenshot(ws, s8, msg_id); msg_id += 1

            # 9. Automações Python
            await click_menu_by_text("Automações Python", wait_sec=2.0, scroll_y=0)
            s9 = SCREENSHOTS_DIR / "09_automacoes_python.png"
            await capture_screenshot(ws, s9, msg_id); msg_id += 1

            # 10. Configurações & Planos (Autonomia Níveis 1, 2 e 3)
            await click_menu_by_text("Configurações", wait_sec=2.0, scroll_y=0)
            s10 = SCREENSHOTS_DIR / "10_configuracoes_autonomia.png"
            await capture_screenshot(ws, s10, msg_id); msg_id += 1

            return [
                {
                    "file": s1,
                    "title": "1. Acesso Oficial e Login Executivo (Multi-Tenant)",
                    "description": (
                        "Acesse https://automacao.projetosunion.cloud. Na tela inicial, clique no botão 'Preencher automaticamente' "
                        "para inserir as credenciais executivas (admin@projetosunion.cloud / UnionGrowth#2026!) ou crie uma nova empresa isolada "
                        "na aba 'Nova Empresa (Multi-Tenant)'. Em seguida, clique em 'Acessar Central Executiva'."
                    ),
                },
                {
                    "file": s2,
                    "title": "2. Visão Geral Executiva e Orquestrador Multiagente",
                    "description": (
                        "Após o login, a Visão Geral apresenta os indicadores principais, o resumo diário do AI CEO, a equipe de "
                        "11 Agentes Especialistas e o botão verde 'Acionar Orquestrador Multiagente' no topo direito, que executa um ciclo "
                        "coordenado entre todos os departamentos."
                    ),
                },
                {
                    "file": s3,
                    "title": "3. Central Executiva Multinegócio (3 Unidades & Painel Fase 18.1)",
                    "description": (
                        "No menu lateral '17M 🏢 Multinegócio (3 Unidades)', você alterna entre a Visão Consolidada e as 3 unidades "
                        "independentes: Unidade A (UNION TECH — IA & Sistemas), Unidade B (UNION AGENCY — Clientes de Marketing) e "
                        "Unidade C (UNION PARTNERS — Afiliados). O Painel de Validação Fase 18.1 separa rigorosamente os dados em 5 blocos: "
                        "REAL, ESTIMATIVA, PROJEÇÃO, META e SIMULAÇÃO & SANDBOX, além do Funil Comercial Completo."
                    ),
                },
                {
                    "file": s4,
                    "title": "4. Catálogo de 7 Serviços, Propostas, Pagamentos Sandbox e Entregas",
                    "description": (
                        "Rolando a Central Multinegócio, você gerencia: (a) Os 7 Serviços de IA e Automação da UNION TECH com calculadora "
                        "dinâmica de custos e botão 'Aprovar Tabela de Preço'; (b) O Gerador de Propostas Comerciais com link direto para PDF "
                        "imprimível e botão 'Aprovar & Fechar'; (c) Contas de Clientes da UNION AGENCY; (d) Programas de Afiliados da UNION PARTNERS; "
                        "(e) Emissão de Cobranças Sandbox/Mercado Pago e acompanhamento de Projetos de Entrega (Onboarding)."
                    ),
                },
                {
                    "file": s5,
                    "title": "5. AI CEO — Diretoria Estratégica e Metas Corporativas",
                    "description": (
                        "Na aba '02 AI CEO', você consulta o CEO Daily Briefing (o que aconteceu, o que está funcionando, gargalos e "
                        "recomendações prioritárias), gera um novo briefing atualizado a qualquer momento e cadastra Metas Estratégicas "
                        "mensais, trimestrais ou anuais."
                    ),
                },
                {
                    "file": s6,
                    "title": "6. Content Factory 30D — Fábrica de Conteúdo Multicanal",
                    "description": (
                        "Na aba '06 🏭 Content Factory 30D', gere lotes de 30 peças mensais para Instagram, LinkedIn, TikTok, YouTube, "
                        "Facebook, Pinterest, Blog SEO e E-mail com controle anti-duplicação. Cada peça possui botão 'Pacote 1-Clique' "
                        "para publicação assistida (copia legenda, hashtags e checklist) sem exigir APIs pagas."
                    ),
                },
                {
                    "file": s7,
                    "title": "7. Painel Operacional 24/7, Infraestrutura VPS e Alertas",
                    "description": (
                        "Na aba '08 🖥️ Painel 24/7 & Alertas', acompanhe em tempo real a saúde da VPS (72.62.13.62), container Coolify, "
                        "banco PostgreSQL 16, jobs ativos no APScheduler e a Central de Alertas Operacionais com ações recomendadas."
                    ),
                },
                {
                    "file": s8,
                    "title": "8. CRM Inteligente, Qualificação de Leads e Governança LGPD",
                    "description": (
                        "Na aba '13 CRM & Leads', cadastre e gerencie leads com pontuação automática (Lead Scoring 0 a 100), filtro por "
                        "origem (REAL, TEST, IMPORTED), registro de consentimento LGPD e botão de descadastro/bloqueio imediato (Opt-out)."
                    ),
                },
                {
                    "file": s9,
                    "title": "9. Automações Nativas em Python (APScheduler 24/7)",
                    "description": (
                        "Na aba '19 Automações Python', visualize e dispare manualmente qualquer uma das rotinas automatizadas (07:00 às 19:00 "
                        "no fuso America/Sao_Paulo), com controle de idempotência, retentativa automática e histórico auditável no banco."
                    ),
                },
                {
                    "file": s10,
                    "title": "10. Configurações da Marca, Níveis de Autonomia (1, 2 e 3) e Multi-Tenant",
                    "description": (
                        "Na aba '23 Configurações & Planos', defina as cores da marca, escolha o Nível de Autonomia (Nível 1 Assistido, "
                        "Nível 2 Semiautônomo ou Nível 3 Autônomo — mantendo travas humanas obrigatórias para ações financeiras e contratos) "
                        "e adicione novas empresas isoladas no grupo."
                    ),
                },
            ]
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


def build_word_manual(sections: list[dict], docx_path: Path):
    doc = Document()

    # Configurar estilo base
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # Capa / Título Principal
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = title_p.add_run("MANUAL OFICIAL DE USO DO SISTEMA\nUNION GROWTH OS")
    run_t.bold = True
    run_t.font.size = Pt(22)
    run_t.font.color.rgb = RGBColor(49, 46, 129)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_s = sub_p.add_run(
        "Plataforma Multinegócio de Inteligência Artificial, Diretoria Executiva (AI CEO),\n"
        "Automação Comercial, Marketing, SEO, Content Factory e CRM\n\n"
        f"URL Oficial de Produção: {BASE_URL}\n"
        "Versão Atualizada — Fase 18.1 (Operação Multinegócio: UNION TECH, UNION AGENCY e UNION PARTNERS)"
    )
    run_s.font.size = Pt(11)
    run_s.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph()

    # Bloco 1: Credenciais e Acesso Rápido
    h1 = doc.add_heading("1. Dados de Acesso Rápido à Produção", level=1)
    t_cred = doc.add_table(rows=5, cols=2)
    t_cred.style = "Table Grid"
    rows_data = [
        ("Endereço Oficial (HTTPS)", BASE_URL),
        ("E-mail Administrativo", ADMIN_EMAIL),
        ("Senha Executiva Padrão", ADMIN_PASS),
        ("Botão de Acesso Rápido", "Na tela de login, clique em 'Preencher automaticamente' e depois em 'Acessar Central Executiva'."),
        ("Isolamento e Segurança", "Autenticação JWT + Bcrypt, Multi-Tenant isolado, proteção LGPD e travas humanas para preços/contratos."),
    ]
    for idx, (k, v) in enumerate(rows_data):
        t_cred.rows[idx].cells[0].text = k
        t_cred.rows[idx].cells[1].text = v

    doc.add_paragraph()

    # Bloco 2: Visão das 3 Unidades de Negócio
    doc.add_heading("2. Estrutura Multinegócio (3 Fontes Independentes de Receita)", level=1)
    t_units = doc.add_table(rows=4, cols=3)
    t_units.style = "Table Grid"
    headers_u = ["Unidade Comercial", "Foco Principal", "Como Operar no Sistema"]
    for j, h_text in enumerate(headers_u):
        t_units.rows[0].cells[j].text = h_text
    units_rows = [
        (
            "UNIDADE A — UNION TECH",
            "Venda de serviços próprios de IA, Agentes, Automação em Python, Dashboards, CRM e Sistemas Sob Medida (SRV_01 a SRV_07).",
            "Revise e aprove os preços na calculadora dinâmica, capture leads nas 9 Landing Pages, gere propostas em PDF, emita cobranças e acompanhe o Onboarding.",
        ),
        (
            "UNIDADE B — UNION AGENCY",
            "Operação de Marketing Digital, SEO, Content Factory 30D e Gestão Comercial para empresas clientes.",
            "Cadastre contas isoladas de clientes nos planos STARTER, PRO, BUSINESS ou ENTERPRISE e gere lotes mensais de conteúdo e auditorias SEO.",
        ),
        (
            "UNIDADE C — UNION PARTNERS",
            "Marketing de Afiliados e Curadoria Técnica (Mercado Livre, Amazon, Shopee, Ferramentas SaaS e Parcerias Tech).",
            "Cadastre produtos curados com aviso publicitário claro, rastreie cliques (sem contar clique como venda) e concilie apenas comissões confirmadas.",
        ),
    ]
    for i, r_vals in enumerate(units_rows, start=1):
        for j, val in enumerate(r_vals):
            t_units.rows[i].cells[j].text = val

    doc.add_page_break()

    # Bloco 3: Passo a Passo Visual com Imagens Reais
    doc.add_heading("3. Guia Passo a Passo com Telas Reais do Sistema", level=1)
    for sec in sections:
        doc.add_heading(sec["title"], level=2)
        p_desc = doc.add_paragraph(sec["description"])
        p_desc.paragraph_format.space_after = Pt(8)
        if sec["file"].exists():
            pic_p = doc.add_paragraph()
            pic_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pic_p.add_run().add_picture(str(sec["file"]), width=Inches(6.2))
        doc.add_paragraph()

    # Bloco 4: Fluxo Comercial Completo de 12 Etapas
    doc.add_heading("4. Como Executar o Ciclo Comercial Completo (Do Lead ao Pós-Venda)", level=1)
    steps_flow = [
        "Passo 1 (Captura e Qualificação): O lead entra por uma das 9 Landing Pages ou é cadastrado em '13 CRM & Leads' com consentimento LGPD. O sistema deduplica por e-mail e calcula o Lead Score (0 a 100).",
        "Passo 2 (Diagnóstico e Proposta): Na aba '17M Multinegócio', selecione o serviço recomendado (SRV_01 a SRV_07), preencha os dados do cliente no Gerador de Propostas e clique em 'Gerar Proposta Comercial'.",
        "Passo 3 (Aprovação do Proprietário e PDF): Clique em 'PDF' para abrir/imprimir a proposta formatada. Nenhuma proposta ou contrato é enviado ou aceito sem sua aprovação ('Aprovar & Fechar').",
        "Passo 4 (Cobrança e Webhook Verificado): Emita a cobrança (opera em modo Sandbox seguro por padrão até que você conecte o token de produção do Mercado Pago). O sistema jamais soma cobrança pendente como receita recebida.",
        "Passo 5 (Onboarding e Entrega com Evidência): Assim que o pagamento é confirmado via Webhook assinado, o sistema cria automaticamente o Projeto de Entrega com checklist de 5 etapas. Ao concluir com evidência técnica, o cliente avança para Pós-Venda.",
    ]
    for st in steps_flow:
        doc.add_paragraph(st, style="List Bullet")

    doc.save(str(docx_path))
    print(f"[WORD] Manual .docx gerado com sucesso: {docx_path} ({docx_path.stat().st_size // 1024} KB)")


def build_pdf_manual(sections: list[dict], pdf_path: Path):
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ManualTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=25,
        textColor=colors.HexColor("#1e1b4b"),
        alignment=1,
        spaceAfter=12,
    )
    sub_style = ParagraphStyle(
        "ManualSub",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=18,
    )
    h1_style = ParagraphStyle(
        "ManualH1",
        parent=styles["Heading1"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#312e81"),
        spaceBefore=12,
        spaceAfter=8,
    )
    h2_style = ParagraphStyle(
        "ManualH2",
        parent=styles["Heading2"],
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#4338ca"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ManualBody",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=8,
    )

    story = []
    story.append(Paragraph("MANUAL OFICIAL DE USO DO SISTEMA — UNION GROWTH OS", title_style))
    story.append(
        Paragraph(
            f"Plataforma Multinegócio de IA, Diretoria Executiva (AI CEO), Marketing, SEO, Content Factory e CRM<br/>"
            f"<b>URL Oficial:</b> {BASE_URL} | <b>E-mail:</b> {ADMIN_EMAIL} | <b>Senha:</b> {ADMIN_PASS}",
            sub_style,
        )
    )

    story.append(Paragraph("1. Credenciais e Acesso Rápido", h1_style))
    cred_table_data = [
        ["Campo", "Valor / Instrução Oficial"],
        ["URL Oficial (HTTPS)", BASE_URL],
        ["E-mail Administrativo", ADMIN_EMAIL],
        ["Senha Executiva", ADMIN_PASS],
        ["Acesso em 1 Clique", "Clique em 'Preencher automaticamente' na tela de login e depois em 'Acessar Central Executiva'."],
    ]
    t = Table(cred_table_data, colWidths=[5.0 * cm, 13.0 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#312e81")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 12))

    story.append(Paragraph("2. Guia Visual Passo a Passo com Telas Reais de Produção", h1_style))
    for idx, sec in enumerate(sections):
        story.append(Paragraph(sec["title"], h2_style))
        story.append(Paragraph(sec["description"], body_style))
        if sec["file"].exists():
            img = RLImage(str(sec["file"]), width=17.5 * cm, height=11.5 * cm)
            story.append(img)
            story.append(Spacer(1, 10))
        if idx % 2 == 1 and idx < len(sections) - 1:
            story.append(PageBreak())

    story.append(Paragraph("3. Resumo do Ciclo Comercial de 12 Etapas e Governança", h1_style))
    story.append(
        Paragraph(
            "• <b>Separação Financeira Estrita (5 Blocos):</b> O painel separa obrigatoriamente REAL, ESTIMATIVA, PROJEÇÃO, META e SIMULAÇÃO & SANDBOX.<br/>"
            "• <b>Travas de Aprovação do Proprietário:</b> Nenhuma tabela de preços aprovada é alterada, nenhuma proposta vinculante é aceita e nenhuma cobrança é emitida sem aprovação expressa do proprietário.<br/>"
            "• <b>Onboarding e Entrega:</b> Após confirmação criptográfica do pagamento via Webhook HMAC-SHA256, o sistema cria automaticamente o Projeto de Entrega com checklist de 5 etapas.",
            body_style,
        )
    )

    doc.build(story)
    print(f"[PDF] Manual .pdf gerado com sucesso: {pdf_path} ({pdf_path.stat().st_size // 1024} KB)")


async def main():
    print("=== INICIANDO CAPTURA DE SCREENSHOTS REAIS E GERAÇÃO DO MANUAL (WORD & PDF) ===")
    sections = await capture_all_production_screenshots()

    docx_root = ROOT_DIR / "MANUAL_DE_USO_UNION_GROWTH_OS.docx"
    pdf_root = ROOT_DIR / "MANUAL_DE_USO_UNION_GROWTH_OS.pdf"

    build_word_manual(sections, docx_root)
    build_pdf_manual(sections, pdf_root)

    # Copiar para public/manual, out/manual e pasta de artifacts do chat
    for dest_dir in (PUBLIC_MANUAL_DIR, OUT_MANUAL_DIR, ARTIFACT_DIR):
        if dest_dir.exists():
            shutil.copy2(docx_root, dest_dir / docx_root.name)
            shutil.copy2(pdf_root, dest_dir / pdf_root.name)

    print("=== CONCLUÍDO COM SUCESSO! ===")


if __name__ == "__main__":
    asyncio.run(main())

