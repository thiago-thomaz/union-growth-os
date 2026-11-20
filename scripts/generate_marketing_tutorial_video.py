"""
Gera o VÍDEO TUTORIAL COMPLETO COM ÁUDIO EXPLICATIVO EM PORTUGUÊS (MP4 Full HD 1920x1080):
- Narração neural em Português Brasileiro (pt-BR-AntonioNeural via edge-tts, com fallback SAPI)
- 9 cenas passo a passo mostrando as telas reais de produção (https://automacao.projetosunion.cloud)
- Destaques visuais (callouts) indicando onde clicar em cada etapa da geração de marketing
- Exporta MP4 H.264 + AAC compatível com todos os navegadores, Windows Media Player e WhatsApp/celular
"""

import asyncio
import os
import shutil
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = ROOT_DIR / "docs" / "manual" / "screenshots"
TMP_VIDEO_DIR = ROOT_DIR / "docs" / "manual" / ".video_build_tmp"
PUBLIC_MANUAL_DIR = ROOT_DIR / "frontend" / "public" / "manual"
OUT_MANUAL_DIR = ROOT_DIR / "frontend" / "out" / "manual"
ARTIFACT_DIR = Path(r"C:\Users\Thiago Thomaz\.gemini\antigravity\brain\fa8e9ad9-decb-4e71-be16-10aafa90bb28")
DOWNLOADS_DIR = Path(os.path.expanduser("~/Downloads"))

OUTPUT_MP4 = ROOT_DIR / "TUTORIAL_MARKETING_UNION_GROWTH_OS.mp4"

SCENES = [
    {
        "step_badge": "INTRODUÇÃO & ACESSO",
        "title": "Potencial da Plataforma e Login no UNION GROWTH OS",
        "image": "01_tela_login.png",
        "highlight_boxes": [
            (490, 240, 950, 720, "1. Acesse automacao.projetosunion.cloud e entre"),
        ],
        "subtitles": [
            "• Substitui o trabalho manual de 5 a 8 profissionais (CMO, Copywriter, SEO, Social Media)",
            "• Acesse https://automacao.projetosunion.cloud e clique em 'Acessar Central Executiva'",
        ],
        "narration": (
            "Bem-vindo ao tutorial prático de geração de marketing do Union Growth O S. "
            "Esta plataforma substitui o trabalho braçal de uma agência inteira, unindo onze agentes "
            "de inteligência artificial e trinta e duas automações nativas em Python. "
            "Para começar, acesse automacao ponto projetos union ponto cloud, preencha suas credenciais executivas "
            "e clique no botão azul Acessar Central Executiva."
        ),
    },
    {
        "step_badge": "VISÃO GERAL & MULTI-TENANT",
        "title": "Escolhendo a Empresa Ativa e Acionando o Orquestrador",
        "image": "02_visao_geral.png",
        "highlight_boxes": [
            (10, 62, 245, 125, "Seletor Multi-Tenant (Sua Empresa ou Cliente)"),
            (1070, 12, 1300, 56, "Acionar Orquestrador Multiagente"),
        ],
        "subtitles": [
            "• Topo Esquerdo: Escolha a Empresa Ativa (sua operação ou cliente da UNION AGENCY)",
            "• Topo Direito: Clique em 'Acionar Orquestrador Multiagente' para diagnóstico completo",
        ],
        "narration": (
            "Na Visão Geral, observe no canto superior esquerdo o seletor Empresa Ativa Multi-Tenant. "
            "Ali você escolhe se vai produzir o marketing para a sua própria empresa ou para qualquer cliente da sua agência. "
            "No canto superior direito, o botão verde Acionar Orquestrador Multiagente coloca os onze diretores de inteligência artificial "
            "para diagnosticar e atualizar toda a estratégia em segundos."
        ),
    },
    {
        "step_badge": "PASSO 1 DE 6 — ESTRATÉGIA",
        "title": "Menu 03: Definindo Buyer Persona e Campanha no AI CMO",
        "image": "08_marketing_cmo.png",
        "highlight_boxes": [
            (6, 250, 246, 286, "Clique no Menu 03: Marketing (AI CMO)"),
            (280, 180, 1410, 520, "Cadastre a Buyer Persona e a Campanha Estratégica"),
        ],
        "subtitles": [
            "• Menu 03 Marketing (AI CMO): Cadastre a Buyer Persona (Cargo, Dor e Proposta de Valor)",
            "• Crie a Campanha (Aquisição, Retenção ou Monetização) definindo canais e orçamento",
        ],
        "narration": (
            "Passo um: no menu lateral esquerdo, clique em zero três, Marketing A I C M O. "
            "Primeiro, cadastre a sua Buyer Persona informando o perfil do comprador, o cargo decisor e a sua proposta de valor. "
            "Em seguida, crie a sua campanha estratégica escolhendo o objetivo de aquisição, retenção ou monetização, "
            "os canais principais e o orçamento. Isso orienta todos os agentes criativos da plataforma."
        ),
    },
    {
        "step_badge": "PASSO 2 DE 6 — ESCALA 30 DIAS",
        "title": "Menu 06: Gerando 30 Dias de Conteúdo na Content Factory 30D",
        "image": "11_content_factory.png",
        "highlight_boxes": [
            (6, 355, 246, 392, "Clique no Menu 06: Content Factory 30D"),
            (1140, 88, 1410, 150, "Clique em 'Gerar Lote de 30 Publicações'"),
            (280, 170, 960, 215, "Filtre por Canal (LinkedIn, Instagram, TikTok, Blog SEO)"),
        ],
        "subtitles": [
            "• Menu 06 Content Factory 30D: Clique no botão roxo 'Gerar Lote de 30 Publicações'",
            "• Receba 30 peças (Topo, Meio e Fundo de Funil) com Copy, Prompt Visual, Nota e CTA",
        ],
        "narration": (
            "Passo dois: acesse o menu zero seis, Content Factory trinta D. Este é o principal motor de escala da ferramenta. "
            "Clique no botão roxo Gerar Lote de Trinta Publicações no canto superior direito. "
            "Em poucos segundos, a inteligência artificial produz trinta peças completas distribuídas entre topo, meio e fundo de funil, "
            "já com título, copy formatada, prompt visual, hashtags, nota de qualidade e chamada para ação. "
            "Filtre pelo canal desejado e copie o pacote pronto."
        ),
    },
    {
        "step_badge": "PASSO 3 DE 6 — TRÁFEGO ORGÂNICO",
        "title": "Menu 04: Auditoria Técnica Real, Keywords e Artigos no SEO Director",
        "image": "09_seo_director.png",
        "highlight_boxes": [
            (6, 286, 246, 320, "Clique no Menu 04: SEO Director"),
            (280, 85, 1410, 290, "1. Audite URL Real  |  2. Mapeie Keywords  |  3. Gere Artigo SEO"),
        ],
        "subtitles": [
            "• Menu 04 SEO Director: Inspecione qualquer site em tempo real (Score 0 a 100, Title, H1, Schema)",
            "• Mapeie clusters de palavras-chave e gere artigos completos otimizados para o Google",
        ],
        "narration": (
            "Passo três: para atrair clientes pelo Google, clique no menu zero quatro, S E O Director. "
            "Digite a U R L do seu site ou do cliente e clique em Executar Auditoria Real para verificar velocidade, títulos, "
            "meta tags e Schema ponto org. Depois, pesquise sua palavra-chave principal para descobrir termos de cauda longa "
            "e clique em Gerar Artigo S E O Completo para produzir artigos estruturados prontos para publicação."
        ),
    },
    {
        "step_badge": "PASSO 4 DE 6 — COPYWRITING",
        "title": "Menu 11: Cartas de Vendas, Anúncios e Sequências no AI Copywriter",
        "image": "16_copywriter.png",
        "highlight_boxes": [
            (6, 535, 246, 570, "Clique no Menu 11: Copywriter"),
            (280, 85, 1410, 260, "Escolha Formato + Framework (AIDA / PAS) e clique em Gerar Copy"),
        ],
        "subtitles": [
            "• Menu 11 Copywriter: Crie textos persuasivos para Landing Pages, Anúncios e E-mails",
            "• Utilize os frameworks clássicos AIDA (Atenção, Interesse, Desejo, Ação) ou PAS",
        ],
        "narration": (
            "Passo quatro: acesse o menu onze, Copywriter. Aqui você gera textos altamente persuasivos para páginas de vendas, "
            "anúncios patrocinados, sequências de e-mail e scripts comerciais. "
            "Basta escolher o formato, selecionar o framework A I D A ou P A S, informar o nome da oferta e o benefício principal, "
            "e clicar em Gerar Copy Persuasiva."
        ),
    },
    {
        "step_badge": "PASSO 5 DE 6 — ESTÚDIO VISUAL",
        "title": "Menu 10: Roteiros de Reels, Shorts e Carrosséis no Creative Studio",
        "image": "15_creative_studio.png",
        "highlight_boxes": [
            (6, 500, 246, 535, "Clique no Menu 10: Creative Studio"),
            (280, 85, 1410, 250, "Gere Roteiros de Vídeo Cena a Cena e Briefings de Carrossel"),
        ],
        "subtitles": [
            "• Menu 10 Creative Studio: Crie roteiros visuais cena a cena para Reels, TikTok e Carrosséis",
            "• Inclui direção visual, texto de cada slide/cena, prompt de imagem e CTA",
        ],
        "narration": (
            "Passo cinco: no menu dez, Creative Studio, você cria a direção visual das suas campanhas. "
            "Informe o título da peça, escolha entre carrossel, roteiro de Reels ou banner de anúncio, "
            "defina a headline e a chamada para ação, e clique em Gerar Ativo Criativo para receber o roteiro cena a cena."
        ),
    },
    {
        "step_badge": "PASSO 6 DE 6 — PUBLICAÇÃO",
        "title": "Menus 05 e 18: Agendamento Multicanal e Fila de Publicação",
        "image": "10_redes_sociais.png",
        "highlight_boxes": [
            (6, 320, 246, 355, "Clique no Menu 05: Redes Sociais"),
            (280, 155, 1410, 235, "Agende por Rede Social (Instagram, LinkedIn, TikTok, YouTube)"),
            (280, 250, 1410, 560, "Clique em 'Aprovar & Publicar' em cada peça agendada"),
        ],
        "subtitles": [
            "• Menu 05 Redes Sociais / Menu 18 Calendário: Agende posts ou gere lote multicanal com IA",
            "• Clique em 'Aprovar & Publicar' para disparo via API ou cópia na fila assistida",
        ],
        "narration": (
            "Passo seis: acesse o menu zero cinco, Redes Sociais, ou o menu dezoito, Calendário Editorial. "
            "Aqui você agenda cada publicação escolhendo a plataforma, o formato e o horário, ou clica em Gerar Lote de Posts Multicanal. "
            "Nos cartões agendados, basta clicar em Aprovar e Publicar para enviar pela A P I oficial conectada "
            "ou liberar na fila assistida."
        ),
    },
    {
        "step_badge": "CONVERSÃO & FECHAMENTO",
        "title": "Menu 17M: Convertendo o Marketing em Leads, Propostas e Receita Real",
        "image": "03_multinegocio_3_unidades.png",
        "highlight_boxes": [
            (6, 180, 246, 215, "Menu 17M: Multinegócio (3 Unidades)"),
            (280, 440, 1410, 710, "Acompanhe as 5 Gavetas Financeiras Fase 18.1 e o Funil de 17 Etapas"),
        ],
        "subtitles": [
            "• Direcione o CTA dos conteúdos para as 9 Landing Pages comerciais integradas ao CRM",
            "• Acompanhe no Menu 17M a evolução do Visitante até a Proposta, Contrato e Pagamento",
        ],
        "narration": (
            "Para transformar todo esse marketing em dinheiro no caixa, direcione a chamada para ação dos seus conteúdos "
            "para as nove Landing Pages comerciais públicas do sistema. "
            "Cada visitante capturado entra automaticamente no C R M com pontuação B A N T e avança pelo funil do menu Multinegócio "
            "até a emissão da proposta em P D F, assinatura do contrato e pagamento via Pix ou Mercado Pago. "
            "Excelentes resultados com o Union Growth O S!"
        ),
    },
]


def load_font(size: int, bold: bool = False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


async def synthesize_narration(text: str, out_audio_path: Path):
    try:
        comm = edge_tts.Communicate(text, voice="pt-BR-AntonioNeural", rate="+4%")
        await comm.save(str(out_audio_path))
        if out_audio_path.exists() and out_audio_path.stat().st_size > 1000:
            return
    except Exception as e:
        print(f"  [WARN] edge_tts falhou ({e}), usando fallback Windows SAPI...")

    # Fallback para Windows SAPI (Microsoft Maria Desktop pt-BR)
    wav_path = out_audio_path.with_suffix(".wav")
    safe_text = text.replace("'", " ").replace('"', " ")
    ps_cmd = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Female, [System.Speech.Synthesis.VoiceAge]::NotSet, 0, [System.Globalization.CultureInfo]::GetCultureInfo('pt-BR')); "
        f"$s.SetOutputToWaveFile('{wav_path}'); "
        f"$s.Speak('{safe_text}'); "
        "$s.Dispose();"
    )
    subprocess.run(["powershell", "-Command", ps_cmd], check=True)
    shutil.move(str(wav_path), str(out_audio_path))


def render_annotated_1080p_frame(scene: dict, idx: int, total: int, out_png_path: Path):
    canvas_w, canvas_h = 1920, 1080
    canvas = Image.new("RGB", (canvas_w, canvas_h), (7, 11, 20))
    draw = ImageDraw.Draw(canvas)

    font_badge = load_font(18, bold=True)
    font_title = load_font(28, bold=True)
    font_sub = load_font(21, bold=False)
    font_callout = load_font(18, bold=True)

    # Top Header Bar (height 88px)
    draw.rectangle([0, 0, canvas_w, 88], fill=(15, 23, 42))
    draw.line([0, 88, canvas_w, 88], fill=(79, 70, 229), width=3)

    # Badge Pill
    badge_text = f"  {scene['step_badge']}  "
    draw.rounded_rectangle([32, 22, 310, 64], radius=10, fill=(79, 70, 229))
    draw.text((44, 31), badge_text.strip(), font=font_badge, fill=(255, 255, 255))

    # Title
    draw.text((335, 26), scene["title"], font=font_title, fill=(248, 250, 252))

    # Step Progress Indicator on Top Right
    prog_text = f"Etapa {idx + 1} de {total}"
    draw.rounded_rectangle([1710, 22, 1888, 64], radius=10, fill=(16, 185, 129))
    draw.text((1735, 31), prog_text, font=font_badge, fill=(255, 255, 255))

    # Screenshot Region (y=96 to y=944 -> height 848px)
    src_img_path = SCREENSHOTS_DIR / scene["image"]
    if src_img_path.exists():
        with Image.open(src_img_path).convert("RGB") as raw_im:
            orig_w, orig_h = raw_im.size
            # Scale screenshot to fit inside 1840 x 836
            target_area_w, target_area_h = 1840, 836
            scale = min(target_area_w / orig_w, target_area_h / orig_h)
            new_w, new_h = int(orig_w * scale), int(orig_h * scale)
            resized = raw_im.resize((new_w, new_h), Image.Resampling.LANCZOS)

            offset_x = (canvas_w - new_w) // 2
            offset_y = 96 + (target_area_h - new_h) // 2

            # Outer subtle frame around screenshot
            draw.rounded_rectangle(
                [offset_x - 4, offset_y - 4, offset_x + new_w + 4, offset_y + new_h + 4],
                radius=8,
                outline=(51, 65, 85),
                width=2,
            )
            canvas.paste(resized, (offset_x, offset_y))

            # Draw High-Visibility Callout Boxes & Labels on the Screenshot
            for box in scene.get("highlight_boxes", []):
                bx1, by1, bx2, by2, label = box
                sx1 = int(offset_x + bx1 * scale)
                sy1 = int(offset_y + by1 * scale)
                sx2 = int(offset_x + bx2 * scale)
                sy2 = int(offset_y + by2 * scale)

                # Outer glow + inner bright emerald/amber border
                draw.rounded_rectangle([sx1 - 3, sy1 - 3, sx2 + 3, sy2 + 3], radius=8, outline=(16, 185, 129), width=4)
                draw.rounded_rectangle([sx1, sy1, sx2, sy2], radius=6, outline=(250, 204, 21), width=3)

                # Label tag above or below the highlight box
                lbl_w = len(label) * 10 + 28
                lbl_h = 34
                lbl_x = max(24, min(sx1, canvas_w - lbl_w - 24))
                lbl_y = sy1 - lbl_h - 6 if sy1 - lbl_h - 6 > 100 else sy2 + 6
                draw.rounded_rectangle(
                    [lbl_x, lbl_y, lbl_x + lbl_w, lbl_y + lbl_h],
                    radius=6,
                    fill=(16, 185, 129),
                    outline=(255, 255, 255),
                    width=2,
                )
                draw.text((lbl_x + 12, lbl_y + 6), label, font=font_callout, fill=(7, 11, 20))

    # Bottom Subtitle / Instruction Bar (y=944 to 1080 -> height 136px)
    draw.rectangle([0, 944, canvas_w, canvas_h], fill=(15, 23, 42))
    draw.line([0, 944, canvas_w, 944], fill=(16, 185, 129), width=3)

    y_sub = 962
    for line in scene.get("subtitles", []):
        draw.text((48, y_sub), line, font=font_sub, fill=(226, 232, 240))
        y_sub += 40

    # Progress bar along the very bottom edge (y=1070..1080)
    prog_w = int(canvas_w * ((idx + 1) / total))
    draw.rectangle([0, 1070, prog_w, 1080], fill=(16, 185, 129))

    canvas.save(str(out_png_path), format="PNG")


async def build_video():
    print("=== INICIANDO GERAÇÃO DO VÍDEO TUTORIAL COM ÁUDIO EM PORTUGUÊS ===")
    if TMP_VIDEO_DIR.exists():
        shutil.rmtree(TMP_VIDEO_DIR, ignore_errors=True)
    TMP_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"  [FFMPEG] Binário localizado: {ffmpeg_exe}")

    segment_files = []
    total_scenes = len(SCENES)

    for idx, scene in enumerate(SCENES):
        print(f"  [CENA {idx+1}/{total_scenes}] Processando: {scene['title']}...")
        frame_png = TMP_VIDEO_DIR / f"scene_{idx:02d}.png"
        audio_mp3 = TMP_VIDEO_DIR / f"scene_{idx:02d}.mp3"
        segment_mp4 = TMP_VIDEO_DIR / f"segment_{idx:02d}.mp4"

        render_annotated_1080p_frame(scene, idx, total_scenes, frame_png)
        await synthesize_narration(scene["narration"], audio_mp3)

        # Codifica cada cena (imagem 1080p + áudio neural pt-BR) em um segmento MP4 H.264 + AAC
        cmd = [
            ffmpeg_exe,
            "-y",
            "-loop",
            "1",
            "-framerate",
            "15",
            "-i",
            str(frame_png),
            "-i",
            str(audio_mp3),
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-preset",
            "veryfast",
            "-crf",
            "22",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-ar",
            "44100",
            "-ac",
            "2",
            "-pix_fmt",
            "yuv420p",
            "-shortest",
            str(segment_mp4),
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segment_files.append(segment_mp4)
        print(f"    -> Segmento {idx+1} codificado ({segment_mp4.stat().st_size // 1024} KB)")

    # Concatena todos os 9 segmentos no MP4 final com faststart para streaming imediato no navegador
    concat_list_path = TMP_VIDEO_DIR / "concat_list.txt"
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for seg in segment_files:
            safe_p = str(seg.resolve()).replace("\\", "/")
            f.write(f"file '{safe_p}'\n")

    concat_cmd = [
        ffmpeg_exe,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list_path),
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        str(OUTPUT_MP4),
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    size_kb = OUTPUT_MP4.stat().st_size // 1024
    print(f"[MP4 FINAL] Vídeo gerado com sucesso: {OUTPUT_MP4} ({size_kb} KB)")

    # Copia para Downloads, Artifact Dir e frontend/public/manual + frontend/out/manual
    for target_dir in [PUBLIC_MANUAL_DIR, OUT_MANUAL_DIR, ARTIFACT_DIR, DOWNLOADS_DIR]:
        if target_dir.exists() or target_dir in (PUBLIC_MANUAL_DIR, OUT_MANUAL_DIR):
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(OUTPUT_MP4, target_dir / OUTPUT_MP4.name)
            print(f"  [COPIADO] -> {target_dir / OUTPUT_MP4.name}")

    shutil.rmtree(TMP_VIDEO_DIR, ignore_errors=True)
    print("=== VÍDEO TUTORIAL CONCLUÍDO COM SUCESSO! ===")


if __name__ == "__main__":
    asyncio.run(build_video())
