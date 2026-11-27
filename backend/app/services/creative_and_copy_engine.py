import base64
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import CopyItem, CreativeAsset, Tenant

DIMENSIONS_MAP: dict[str, tuple[int, int]] = {
    "SOCIAL_POST": (1080, 1080),
    "CAROUSEL": (1080, 1080),
    "COVER": (1080, 1920),
    "SHORT_VIDEO": (1080, 1920),
    "THUMBNAIL": (1280, 720),
    "INSTITUTIONAL_VIDEO": (1280, 720),
    "BANNER": (1200, 628),
    "AD_CREATIVE": (1080, 1080),
    "INFOGRAPHIC": (1080, 1600),
    "PRESENTATION": (1280, 720),
    "EBOOK": (900, 1200),
    "VIDEO_SCRIPT": (1080, 1080),
}


def _hex_to_rgb(hex_color: str, default: tuple[int, int, int] = (99, 102, 241)) -> tuple[int, int, int]:
    h = (hex_color or "").lstrip("#")
    if len(h) == 6:
        try:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        except ValueError:
            pass
    return default


def _render_brand_png(
    width: int,
    height: int,
    brand_name: str,
    asset_type: str,
    headline: str,
    subheadline: str,
    cta: str,
    primary_hex: str,
    secondary_hex: str,
) -> tuple[bytes, str]:
    """Renders a clean, modern SaaS marketing graphic using Pillow and returns (png_bytes, data_uri)."""
    # Render at 1/2 resolution for speed & compact storage while keeping crisp typography
    render_w = max(540, width // 2)
    render_h = max(360, height // 2)

    img = Image.new("RGB", (render_w, render_h), (12, 16, 29))
    draw = ImageDraw.Draw(img)

    c1 = _hex_to_rgb(primary_hex, (99, 102, 241))
    c2 = _hex_to_rgb(secondary_hex, (16, 185, 129))

    # Top accent bar & geometric glow cards
    draw.rectangle([0, 0, render_w, 12], fill=c1)
    draw.rectangle([0, render_h - 10, render_w, render_h], fill=c2)

    # Decorative geometric accent shapes
    draw.ellipse([render_w - 180, -60, render_w + 60, 180], outline=c1, width=4)
    draw.ellipse([-80, render_h - 160, 140, render_h + 60], outline=c2, width=4)

    # Inner frame
    pad = 36
    draw.rounded_rectangle(
        [pad, pad, render_w - pad, render_h - pad],
        radius=18,
        fill=(20, 26, 46),
        outline=c1,
        width=2,
    )

    font = ImageFont.load_default()

    # Brand badge
    draw.rounded_rectangle([pad + 24, pad + 24, pad + 280, pad + 58], radius=8, fill=c1)
    draw.text((pad + 36, pad + 35), f"{brand_name.upper()[:24]} | {asset_type}", fill=(255, 255, 255), font=font)

    # Headline text wrapping
    words = headline.split()
    lines: list[str] = []
    current = ""
    for w in words:
        if len(current) + len(w) + 1 <= 42:
            current = f"{current} {w}".strip()
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)

    y_cursor = pad + 90
    for line in lines[:5]:
        draw.text((pad + 26, y_cursor), line, fill=(248, 250, 252), font=font)
        y_cursor += 26

    if subheadline:
        y_cursor += 12
        sub_words = subheadline.split()
        sub_line = ""
        for sw in sub_words:
            if len(sub_line) + len(sw) + 1 <= 50:
                sub_line = f"{sub_line} {sw}".strip()
            else:
                draw.text((pad + 26, y_cursor), sub_line, fill=(148, 163, 184), font=font)
                y_cursor += 20
                sub_line = sw
        if sub_line:
            draw.text((pad + 26, y_cursor), sub_line, fill=(148, 163, 184), font=font)
            y_cursor += 24

    # CTA Button
    cta_y = render_h - pad - 68
    draw.rounded_rectangle([pad + 24, cta_y, pad + 240, cta_y + 42], radius=10, fill=c2)
    draw.text((pad + 44, cta_y + 15), f">> {cta.upper()[:22]}", fill=(10, 14, 24), font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    png_bytes = buf.getvalue()
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return png_bytes, f"data:image/png;base64,{b64}"


def generate_creative_asset(
    db: Session,
    tenant: Tenant,
    title: str,
    asset_type: str,
    platform: str,
    headline_text: str,
    subheadline_text: str = "",
    cta_text: str = "Saiba Mais",
    campaign_id: int | None = None,
) -> CreativeAsset:
    """Produces a real visual PNG asset + structured deck/script/ebook content in the Creative Studio."""
    atype = asset_type.upper()
    w, h = DIMENSIONS_MAP.get(atype, (1080, 1080))
    dims_str = f"{w}x{h}"

    png_bytes, data_uri = _render_brand_png(
        width=w,
        height=h,
        brand_name=tenant.brand_name,
        asset_type=atype,
        headline=headline_text,
        subheadline=subheadline_text or f"Estratégia oficial {tenant.brand_name} para {platform}",
        cta=cta_text,
        primary_hex=tenant.primary_color,
        secondary_hex=tenant.secondary_color,
    )

    assets_dir = Path(settings.ASSETS_DIR)
    assets_dir.mkdir(parents=True, exist_ok=True)
    safe_slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:40]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    filename = f"tenant_{tenant.id}_{atype.lower()}_{safe_slug}_{ts}.png"
    file_path = assets_dir / filename
    file_path.write_bytes(png_bytes)

    structured_content: dict[str, Any] = {
        "headline": headline_text,
        "subheadline": subheadline_text,
        "cta": cta_text,
        "platform": platform,
        "dimensions": dims_str,
    }

    if atype == "CAROUSEL":
        structured_content["slides"] = [
            {"slide": 1, "type": "Hook / Capa", "title": headline_text, "body": "Deslize para ver o método prático passo a passo."},
            {"slide": 2, "type": "Problema", "title": "O erro silencioso que trava o crescimento", "body": "Operar sem previsibilidade aumenta o CAC e reduz a margem."},
            {"slide": 3, "type": "Solução", "title": f"O método {tenant.brand_name}", "body": subheadline_text or "Automação inteligente + execução orientada a dados reais."},
            {"slide": 4, "type": "Prova / Passo Prático", "title": "Checklist de Execução", "body": "1. Auditoria de funil\n2. Conteúdo estratégico\n3. Qualificação automática no CRM"},
            {"slide": 5, "type": "CTA", "title": cta_text, "body": f"Acesse {tenant.domain or 'nosso link na bio'} e fale com um especialista."},
        ]
    elif atype in ("VIDEO_SCRIPT", "SHORT_VIDEO", "INSTITUTIONAL_VIDEO"):
        structured_content["video_production"] = {
            "duration_seconds": 45 if atype != "INSTITUTIONAL_VIDEO" else 120,
            "scenes": [
                {"time": "00:00-00:05", "visual": "Close-up dinâmico + legenda em destaque", "narration": f"Você sabia que é possível escalar resultados em {tenant.niche} sem multiplicar custos operacionais?"},
                {"time": "00:05-00:20", "visual": "Demonstração do problema vs painel organizado", "narration": f"{headline_text}. Muitas empresas perdem oportunidades todos os dias por falta de processo."},
                {"time": "00:20-00:35", "visual": f"Identidade visual {tenant.brand_name} + 3 pilares em tela", "narration": subheadline_text or f"Com a {tenant.brand_name}, você integra estratégia, aquisição e atendimento."},
                {"time": "00:35-00:45", "visual": "Cartela final com logo, site e botão CTA", "narration": f"{cta_text} agora mesmo."},
            ],
        }
    elif atype in ("EBOOK", "PRESENTATION", "INFOGRAPHIC"):
        structured_content["chapters"] = [
            {"section": 1, "title": f"Introdução Executiva: {headline_text}", "key_points": ["Cenário atual do mercado", "Métricas de eficiência"]},
            {"section": 2, "title": "Arquitetura de Crescimento Previsível", "key_points": ["Atração qualificada (SEO & Social)", "Conversão estruturada no CRM"]},
            {"section": 3, "title": f"Plano de Implementação {tenant.brand_name}", "key_points": ["Primeiros 30 dias", "Indicadores de sucesso e ROI"]},
        ]

    palette = {
        "primary": tenant.primary_color,
        "secondary": tenant.secondary_color,
        "background": "#0C101D",
        "surface": "#141A2E",
    }

    asset = CreativeAsset(
        tenant_id=tenant.id,
        title=title,
        asset_type=atype,
        platform=platform,
        dimensions=dims_str,
        file_path=str(file_path),
        preview_data_uri=data_uri,
        content_json=json.dumps(structured_content, ensure_ascii=False),
        brand_palette_json=json.dumps(palette, ensure_ascii=False),
        license_info="Original Generated Asset - 100% Royalty-Free Commercial License",
        is_approved=True,
        campaign_id=campaign_id,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


FORBIDDEN_DECEPTIVE_CLAIMS = [
    r"lucro garantido sem risco",
    r"fique rico rápido",
    r"100%\s+garantido\s+sem\s+esforço",
    r"milagre financeiro",
]


def _sanitize_ethical_copy(text: str) -> tuple[str, bool]:
    cleaned = text
    for pattern in FORBIDDEN_DECEPTIVE_CLAIMS:
        cleaned = re.sub(pattern, "resultados consistentes baseados em método e execução", cleaned, flags=re.I)
    return cleaned, True


def generate_persuasive_copy(
    db: Session,
    tenant: Tenant,
    title: str,
    copy_type: str,
    framework: str,
    product_or_offer: str,
    target_audience: str,
    key_benefit: str,
    tone: str = "Executivo e persuasivo",
) -> CopyItem:
    """AI Copywriter: Generates Variant A & Variant B copy for A/B testing using ethical persuasion frameworks."""
    ctype = copy_type.upper()
    fw = framework.upper()
    aud = target_audience.strip() or tenant.target_audience
    offer = product_or_offer.strip() or tenant.brand_name
    benefit = key_benefit.strip() or "gerar resultados e conquistar novos clientes"
    site_cta = f" em {tenant.domain.strip()}" if getattr(tenant, "domain", "").strip() else ""

    if fw == "PAS":
        var_a = (
            f"[PROBLEMA] {aud} frequentemente perdem oportunidades valiosas por falta de divulgação estruturada.\n"
            f"[AGITAÇÃO] Cada semana sem visibilidade clara significa clientes buscando opções em outro lugar.\n"
            f"[SOLUÇÃO] Conheça {offer} da {tenant.brand_name}: feito para {benefit} com clareza e confiança.\n"
            f"[CTA] Acesse{site_cta} e comece hoje mesmo."
        )
        var_b = (
            f"[PROBLEMA] Quanto tempo e clientes você perde dependendo apenas de indicações aleatórias?\n"
            f"[AGITAÇÃO] Sem um canal direto funcionando todos os dias, seu crescimento fica imprevisível.\n"
            f"[SOLUÇÃO] Com {offer} ({tenant.brand_name}), {aud} conseguem {benefit} de forma prática.\n"
            f"[CTA] Clique e acesse{site_cta} agora mesmo."
        )
    elif fw == "BAB":
        var_a = (
            f"[ANTES] Pouca visibilidade, divulgação cansativa e perda de boas oportunidades.\n"
            f"[DEPOIS] Fluxo constante para {aud} conseguirem {benefit} todas as semanas.\n"
            f"[PONTE] {offer} da {tenant.brand_name} simplifica tudo em um só lugar.\n"
            f"[CTA] Visite{site_cta} e dê o próximo passo agora."
        )
        var_b = (
            f"[ANTES] Esforço manual tentando atrair interessados sem retorno garantido.\n"
            f"[DEPOIS] Presença clara e direta com foco em {benefit}.\n"
            f"[PONTE] Conte com {offer} da {tenant.brand_name}.\n"
            f"[CTA] Acesse{site_cta} para saber como funciona."
        )
    else:  # AIDA / FAB / 4PS / STORYBRAND
        var_a = (
            f"[ATENÇÃO] Atenção {aud}: veja como {benefit} com a {tenant.brand_name}!\n"
            f"[INTERESSE] Com {offer}, você conecta seu trabalho diretamente a quem já está procurando.\n"
            f"[DESEJO] Sem burocracia, com divulgação contínua e foco real em resultados para o seu dia a dia.\n"
            f"[AÇÃO] Acesse{site_cta} e faça parte da {tenant.brand_name} hoje mesmo."
        )
        var_b = (
            f"[ATENÇÃO] {benefit.capitalize()}: a oportunidade prática para {aud}.\n"
            f"[INTERESSE] Conheça {offer} ({tenant.brand_name}) e ganhe destaque onde seus clientes buscam.\n"
            f"[DESEJO] Mais alcance, mais contatos interessados e processo simples do começo ao fim.\n"
            f"[AÇÃO] Entre{site_cta} e aproveite agora."
        )

    var_a, ok_a = _sanitize_ethical_copy(var_a)
    var_b, ok_b = _sanitize_ethical_copy(var_b)

    # Enriquecimento automático via AI Router (Menu 25 — UNION AI ENGINE HUB) quando chave ativa
    try:
        from app.services.ai_engines_hub import AIRouter
        if settings.ENVIRONMENT != "test":
            ai_prompt = (
                f"Escreva uma copy persuasiva de alta conversão no formato {fw} para '{offer}' da marca '{tenant.brand_name}'. "
                f"Público-alvo: {aud}. Benefício principal: {benefit}. Tipo de peça: {ctype}. Tom: {tone}."
            )
            ai_res = AIRouter.route_and_execute(
                db=db,
                tenant_id=tenant.id,
                task_type="copywriting",
                required_capability="text_generation",
                prompt=ai_prompt,
                agent_id="AGENT_06_COPYWRITER",
            )
            if ai_res.get("ok") and ai_res.get("output", {}).get("text"):
                var_a, ok_a = _sanitize_ethical_copy(ai_res["output"]["text"])
    except Exception:
        pass

    hypothesis = (
        f"Testar se a abordagem da Variante A (foco direto em '{benefit}') gera maior CTR/Conversão "
        f"do que a Variante B (foco em redução de custo de oportunidade) junto ao público '{aud}'."
    )

    item = CopyItem(
        tenant_id=tenant.id,
        title=title,
        copy_type=ctype,
        framework=fw,
        tone=tone,
        target_audience=aud,
        variant_a=var_a,
        variant_b=var_b,
        ab_test_hypothesis=hypothesis,
        compliance_verified=(ok_a and ok_b),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

