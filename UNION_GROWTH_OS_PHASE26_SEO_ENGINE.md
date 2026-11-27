# UNION GROWTH OS — FASE 26: SEO ENGINE

**Versão:** `2.3.0 — FASE 26`  

## 1. Motor SEO Técnico Ao Vivo (`seo_and_market_engine.py`)
1. **Crawler HTTP Público Anti-SSRF (`perform_real_seo_audit`)**: valida URL pública com `validate_public_http_url` antes de conectar.
2. **Sinais Reais Extraídos na Fase 26**:
   - `<title>`, `<meta name="description">`, `rel="canonical"`, `<meta name="viewport">`, OpenGraph (`og:title`, `og:description`, `og:image`), `robots.txt`, `sitemap.xml`, tempo de resposta (`response_time_ms`), contagem real de palavras (`body_word_count`).
   - Novos sinais adicionados na Fase 26: **`h1_count`**, **`internal_links_count`**, **`external_links_count`** e **`images_missing_alt_count`**.
3. **Recomendações Priorizadas (`prioritized_recommendations`)**:
   - Retornadas em `/seo/audit` e `/seo/overview` ordenadas por `(impact_score, -effort_score)` com classificação `HIGH`/`MEDIUM`, instrução técnica acionável e justificativa (ex.: ausências de canonical, OpenGraph, H1, alt em imagens, viewport mobile ou texto < 600 palavras).
4. **Honestidade SERP / Google Search Console**: banner explícito informa que posições orgânicas no Google **nunca são simuladas** e exigem conexão OAuth oficial ao Google Search Console.
