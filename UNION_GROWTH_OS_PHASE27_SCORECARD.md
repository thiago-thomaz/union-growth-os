# UNION GROWTH OS — SCORECARD OFICIAL DAS 25 CATEGORIAS (FASE 27)

**Score Global Ponderado Observado em Produção:** **`86.9 / 100`** (`PRODUCTION_READY`)  
**Nota de Integridade:** A plataforma **NÃO** atribui `100/100` nem `SCALE_READY` artificialmente enquanto existirem integrações OAuth desconectadas, cota LLM Gemini limitada (`HTTP 402`), billing live desabilitado (`charge_enabled=false`), secrets de CI pendentes ou arquitetura em container único.

| # | Categoria | Peso | Score Real | Status | Evidência Verificada | Principal Gap / Dependência Externa |
|---|---|---|---|---|---|---|
| 1 | **UX/UI** | `5%` | **`94.0`** | `REAL` | DS 5.0, badge SemVer, `0` cliques quebrados | Evoluir editor visual multi-condição |
| 2 | **Design System** | `4%` | **`95.0`** | `REAL` | Obsidian Dark / Alabaster Light + contraste AA | Pequenos ajustes em submódulos legados |
| 3 | **Onboarding** | `4%` | **`90.0`** | `REAL` | 6 etapas persistidas + TTFV + Guia contextual | Preenchimento automático via OAuth |
| 4 | **Core Functionality** | `5%` | **`92.0`** | `REAL` | 150+ rotas FastAPI + Bootstrap + Growth persistido | Fluxos sociais em Modo Assistido (sem OAuth) |
| 5 | **Backend** | `5%` | **`92.0`** | `REAL` | FastAPI + routers `phase26/27` + PostgreSQL 16 | `routes.py` legado (`4.146` linhas) |
| 6 | **Frontend** | `4%` | **`93.0`** | `REAL` | Next.js 15 static (`83.7 kB` /) + zero console errors | Comprimir ainda mais estados globais |
| 7 | **Security** | `5%` | **`90.0`** | `REAL` | `bcrypt`, HS256, Fernet, RBAC 403, Anti-SSRF, Rate-Limit | JWT em `localStorage`; sem cookie `HttpOnly`/MFA ainda |
| 8 | **LGPD** | `4%` | **`93.0`** | `REAL` | Opt-in obrigatório, opt-out lock, export/exclusão | Portal público self-service de preferências |
| 9 | **Integrations** | `5%` | **`45.2`** | `BLOCKED` | `1/18` conectadas no banco | `17/18` integrações aguardando OAuth/credenciais |
| 10 | **AI** | `5%` | **`78.0`** | `REAL_PARTIAL` | `4/12` HYBRID, `8/12` DETERMINISTIC, `0` SIMULATED | Chave Gemini Tenant 1 em HTTP `402`; 8 determinísticos |
| 11 | **Automation** | `4%` | **`91.0`** | `REAL` | `127` jobs APScheduler (`31` regras, `0` falhas, `0%` n8n) | Sem fila worker distribuída externa ainda |
| 12 | **CRM** | `4%` | **`93.0`** | `REAL` | `8` leads reais, `3` deals, scoring 0-100, follow-up LGPD | Sync bidirecional IMAP/WhatsApp aguarda OAuth |
| 13 | **Revenue** | `4%` | **`92.0`** | `REAL` | Propostas PDF Blob, `move-stage`, 3 unidades | Assinatura jurídica externa fora do escopo gratuito |
| 14 | **Marketing** | `4%` | **`88.0`** | `REAL_PARTIAL` | `7` campanhas, Pillow PNG, Copy A/B, Fábrica 30d | Publicação social direta aguarda OAuth |
| 15 | **SEO** | `4%` | **`84.0`** | `REAL_PARTIAL` | Crawler HTTP ao vivo + `h1`/alt/canonical + recomendações | Posições SERP aguardam Search Console OAuth |
| 16 | **Monetization** | `4%` | **`78.0`** | `SANDBOX` | 5 planos PLG + enforcement `402` + `charge_enabled=false` | `0` cobranças live até autorização + credenciais |
| 17 | **Customer Success** | `3%` | **`88.0`** | `REAL` | `3` feedbacks NPS/CSAT + detecção risco/upsell | Pesquisas automáticas por e-mail aguardam SMTP |
| 18 | **Analytics** | `4%` | **`86.0`** | `REAL_PARTIAL` | First-Touch CRM/Financeiro + Growth Score 12 pilares | Tráfego web externo aguarda OAuth GA4 |
| 19 | **Performance** | `4%` | **`93.0`** | `REAL` | Bootstrap consolidado, `--timeout-keep-alive 75`, static | Cache Redis futuro para relatórios pesados |
| 20 | **CI/CD** | `4%` | **`84.0`** | `REAL_PARTIAL` | GitHub Actions CI + Coolify Deploy API + Manifest | Secrets `COOLIFY_API_TOKEN`/`WEBHOOK` ausentes no GitHub |
| 21 | **Reliability** | `4%` | **`94.0`** | `REAL` | PostgreSQL 16 (`is_fallback=false`) + scheduler ativo | Single replica VPS sem multi-AZ failover automático |
| 22 | **Backup** | `3%` | **`92.0`** | `REAL` | Snapshots SHA-256 + restore isolado `145` regs/`31` tabs | Storage off-site S3/Backblaze opcional |
| 23 | **Accessibility** | `3%` | **`94.0`** | `REAL` | `pt-BR`, `0/63` botões sem rótulo, `8` viewports `0px` | Auditoria manual leitor de tela NVDA/VoiceOver |
| 24 | **Architecture** | `3%` | **`85.0`** | `REAL` | `phase26/27` modulares + manifest + DS modular | Refatorar `routes.py` legado (`4.146` linhas) |
| 25 | **Scalability** | `3%` | **`76.0`** | `REAL_PARTIAL` | Pool `10+20`, índices `tenant_id`, stateless JWT | Requer Redis workers + read-replicas para milhões |

---
**Cálculo Auditado:** Soma ponderada exata (`prod_snapshot.json`, `audit_id=5`): **`86.9 / 100` (`PRODUCTION_READY`)**.
