# UNION GROWTH OS — AI Business & Marketing Director

Plataforma completa e autônoma de gestão empresarial, marketing digital, SEO, redes sociais, fábrica de conteúdo, copywriting, growth hacking, inteligência competitiva, finanças, customer success e CRM com arquitetura multiagente e operação contínua em nuvem.

---

## 1. Visão Geral da Arquitetura

- **Backend**: Python 3.12 + FastAPI + SQLAlchemy 2.0 + Pydantic v2 + APScheduler (100% nativo em Python, sem dependência de n8n).
- **Banco de Dados**: PostgreSQL 16 em produção (persistente via volume dedicado) + SQLite automático para desenvolvimento e fallback de alta disponibilidade.
- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS (Painel Executivo SaaS Dark Mode com 20 módulos integrados).
- **Inteligência Artificial**: Arquitetura multiagente com Orquestrador Central, contratos JSON tipados, prevenção de ciclos infinitos, suporte a modelos locais (Ollama), provedores externos compatíveis com OpenAI e Motor Especialista Determinístico embutido (funciona 100% sem exigir chaves pagas).

---

## 2. Os 11 Agentes Especializados

1. **AGENTE 01 — AI CEO**: Direção estratégica, metas mensais/trimestrais/anuais, priorização por impacto financeiro e geração diária do **CEO DAILY BRIEFING**.
2. **AGENTE 02 — AI CMO**: Posicionamento de marca, ICP/Personas, funis de conversão, alocação de orçamento, análise de ROI e planejamento mensal automático.
3. **AGENTE 03 — AI SEO DIRECTOR**: Auditoria técnica HTTP real (`robots.txt`, `sitemap.xml`, `<title>`, `<meta>`, `H1-H2`, `alt`, Schema.org JSON-LD, tempo de resposta), pesquisa de palavras-chave de cauda longa, clusters e **SEO Content Factory**.
4. **AGENTE 04 — AI SOCIAL MEDIA DIRECTOR**: Calendário editorial, adaptação para Instagram, Facebook, TikTok, YouTube, LinkedIn e Pinterest, validação de limites e fila de publicação com aprovação humana.
5. **AGENTE 05 — AI CREATIVE STUDIO**: Geração real de ativos visuais em PNG (`Pillow`), carrosséis multi-slide, thumbnails, banners, roteiros de vídeo e e-books com licença comercial livre.
6. **AGENTE 06 — AI COPYWRITER**: Textos persuasivos nos frameworks `AIDA`, `PAS`, `BAB`, `FAB`, `4PS` e `Storybrand` com geração de Variantes A/B e filtro de conformidade ética.
7. **AGENTE 07 — AI GROWTH HACKER**: Descoberta de gargalos de funil e gestão de experimentos com pontuação ICE, hipótese, indicador, custo estimado e resultado real.
8. **AGENTE 08 — AI SALES DIRECTOR & CRM**: Captura de leads com consentimento LGPD obrigatório, Lead Scoring (0–100), pipeline visual de negociações, follow-ups automáticos e previsão comercial ponderada.
9. **AGENTE 09 — AI COMPETITIVE INTELLIGENCE**: Análise ética de sites públicos de concorrentes respeitando `robots.txt` e geração de oportunidades de diferenciação.
10. **AGENTE 10 — AI FINANCE & PERFORMANCE**: Consolidação de Receita, Despesas, Lucro, Margem, CAC, LTV, ROI, ROAS, Ticket Médio e Churn com separação estrita entre dados `REAL`, `IMPORTED`, `ESTIMATED` e `GOAL`.
11. **AGENTE 11 — AI CUSTOMER SUCCESS**: Monitoramento de NPS/CSAT, detecção de clientes em risco de churn, sugestões de retenção e mapeamento de upsell/cross-sell.

---

## 3. Documentação Complementar

- [INSTALL.md](./INSTALL.md) — Instruções de instalação e execução local.
- [DEPLOY.md](./DEPLOY.md) — Pipeline de deploy contínuo (GitHub -> Coolify -> Docker -> Cloud HTTPS).
- [OPERATIONS.md](./OPERATIONS.md) — Manual de operação dos agentes, níveis de autonomia, scheduler e integrações.
- [SECURITY.md](./SECURITY.md) — Governança LGPD, RBAC, criptografia Fernet, confirmação de alto impacto e backups.
- [CHANGELOG.md](./CHANGELOG.md) — Histórico de versões e fases implementadas.
- [UNION_GROWTH_OS_FINAL_REPORT.md](./UNION_GROWTH_OS_FINAL_REPORT.md) — Relatório executivo e técnico final do projeto.
