# FASE 23 — RELATÓRIO DE CI/CD, AUTO DEPLOY, GITHUB ACTIONS & INFRAESTRUTURA VPS

**Projeto**: `UNION GROWTH OS — The Autonomous Business Growth Platform`  
**Repositório GitHub**: `https://github.com/thiago-thomaz/union-growth-os` (branch `main`)  
**Aplicação Coolify**: `union-growth-os` (`swpy83sa5wshb558fadlrzwc`) no servidor `localhost` (`s14duf5l3yrrn0xobdqs6zhu`)

---

## 1. Auditoria do Pipeline CI/CD (`.github/workflows/ci-cd.yml`)

O pipeline em `.github/workflows/ci-cd.yml` executa automaticamente a cada `push` em `main` e `pull_request` com duas etapas:

1. **Job 1 — `Backend Tests, Frontend Build, Security Audit & Docker Lint`** (`actions/checkout@v7`, `actions/setup-python@v7`, `actions/setup-node@v7` Node 22):
   - Typecheck + build estático Next.js 15 (`npx tsc --noEmit && npm run build`).
   - Validação de `Dockerfile` e arquivos críticos.
   - Execução completa da suíte `pytest backend/tests/test_union_growth_os.py -v` (`51/51` testes locais + validação no container CI).
   - Varredura automatizada contra vazamento de segredos em código e HTML/bundles exportados.
2. **Job 2 — `Automatic Deploy to Coolify VPS & Production Health Checks`**:
   - Executa `python scripts/ci_deploy_and_verify.py`.
   - Quando os secrets `COOLIFY_DEPLOY_WEBHOOK` e `COOLIFY_API_TOKEN` estão ausentes no repositório GitHub, o script pula o acionamento duplicado pelo Actions e valida diretamente a saúde dos endpoints públicos (`/`, `/health`, `/ready`, `/robots.txt`, `/sitemap.xml`) em produção.

### Histórico Verificado de Execuções GitHub Actions (Observado via API)
| Run ID | Commit SHA | Evento | Job 1 (Build/Tests/Security) | Job 2 (Deploy/Health) | Status Final |
|---|---|---|---|---|---|
| **`46005341388`** | `4dacfb2fa3070f36985eef01afa30faa87fd4c9f` | `push main` (Fase 23 Hardening + 20 Jornadas) | `completed / success` | `completed / success` | **SUCCESS** |
| **`45928536225`** | `782834cdd43ed4db050346c4164549b22c23956f` | `push main` (Docs + Evidências Fase 23) | `completed / success` | `completed / success` | **SUCCESS** |
| **`45927206281`** | `afb2912dd2fb4e46e1f569b664d0cf5761b4ac45` | `push main` (Fix `CRMDeal.stage` + `VARCHAR(180)`) | `completed / success` | `completed / success` | **SUCCESS** |

---

## 2. Investigação do Auto Deploy (`is_auto_deploy_enabled = false`) & Bloqueio Documentado

Durante a auditoria independente da infraestrutura Coolify (`coolify:get_application` em `swpy83sa5wshb558fadlrzwc`), foi identificado objetivamente o seguinte comportamento:

1. **Estado Atual no Coolify**:
   - `is_auto_deploy_enabled: false`
   - Webhook GitHub manual (`manual_webhook_secret_github`) presente na aplicação, com GitHub App `meu-github-app-tt` (`app_id: 4393428`) / `Public GitHub` registrados na instância Coolify.
2. **Bloqueio Externo Real para Alteração Automática da Flag**:
   - O schema oficial da ferramenta MCP `coolify:application(action="update")` não expõe o parâmetro `is_auto_deploy_enabled`, e os GitHub Secrets (`COOLIFY_DEPLOY_WEBHOOK` / `COOLIFY_API_TOKEN`) no repositório `thiago-thomaz/union-growth-os` exigem autenticação de administrador do repositório no GitHub UI.
   - Em estrita conformidade com as regras de segurança (proibição de contorno de controle de acesso ou manipulação direta não sancionada de painel/banco interno do Coolify), **não foi aplicado bypass**.
3. **Mitigação Sancionada & Deploys Verificados via API Oficial Coolify (`coolify:deploy`)**:
   - Todos os deploys de produção da Fase 23 foram acionados pelo caminho oficial sancionado (`coolify:deploy`, `is_api: true`) e acompanhados até `status: "finished"`:
     - Deploy **`pjawq26uudxwex95xb1rtkzd`** (`4dacfb2fa3070f36985eef01afa30faa87fd4c9f`) — `finished` (`2026-11-27T13:15:15Z`)
     - Deploy **`xyqfhcfgzdfob0nsac952lfi`** (`782834cdd43ed4db050346c4164549b22c23956f`) — `finished`
     - Deploy **`pnhvxxbmarh63vgeuj9hgkhj`** (`afb2912dd2fb4e46e1f569b664d0cf5761b4ac45`) — `finished`
     - Deploy **`oxojj1ju3ocst4fyaillsxuq`** (`3db428b3eaf37664e49e0cfd2bf9c7f3a7412c53`) — `finished`
4. **Ação Opcional para o Administrador no Coolify / GitHub (Quando Desejar Push-to-Deploy Nativo)**:
   - No painel Coolify da aplicação `union-growth-os` → *Configuration* → habilitar **Auto Deploy** (`is_auto_deploy_enabled = true`) OU cadastrar `COOLIFY_API_TOKEN` + `COOLIFY_DEPLOY_WEBHOOK` em *GitHub Settings → Secrets and variables → Actions*.

---

## 3. Auditoria de Infraestrutura VPS & Isolamento de Outros Projetos (Seção 26)

Auditoria **100% somente leitura** executada via `coolify:get_infrastructure_overview` e `coolify:get_server` (`s14duf5l3yrrn0xobdqs6zhu`, servidor `localhost` acessível):

- **Sistema Operacional & Runtime**: Ubuntu 24.04 (`noble`), kernel `6.8.0-147-generic` (alerta informativo do host: kernel `6.8.0-149-generic` pendente de reboot agendado pelo dono, `0` atualizações de segurança pendentes), Docker `29.1.5`, Traefik `v3.6.25`, Coolify Sentinel ativo, fila de deploys `25`, `concurrent_builds: 2`.
- **Banco de Dados**: `union-growth-os-db` (`thkpm0vkt5f4rj8znd3e2abi`, `standalone-postgresql`, `running:healthy`, `is_public: false`).
- **Inventário Completo das 11 Aplicações & 1 Serviço na VPS (Zero Alteração / Zero Interferência)**:

| Recurso Coolify | UUID | Repositório / Tipo | Domínio(s) | Status Pós-Deploy | Ação Realizada |
|---|---|---|---|---|---|
| **`union-growth-os`** | `swpy83sa5wshb558fadlrzwc` | `thiago-thomaz/union-growth-os` | `automacao.projetosunion.cloud`, `uniongrowth.72.62.13.62.sslip.io` | **`running:healthy`** | Atualizado (`4dacfb2`) |
| `arena-play` | `dinqcdvkvrasqwlj4sdu50i2` | `thiago-thomaz/arena-play` | `arena.projetosunion.cloud` | `running:unknown` | **Intocado (Blindado)** |
| `barberflow` | `7ho00pvb569n5m3jgee0fnsi` | `thiago-thomaz/barberflow` | `barber.projetosunion.cloud` | `running:healthy` | **Intocado** |
| `cidade-ativa-prefeitura` | `hvzvni7cuzg8soxwt5a0ijlo` | `thiago-thomaz/TT` | `hvzvni...sslip.io` | `running:healthy` | **Intocado** |
| `proativos` | `wpwxtlhzdhwd7tqeohdxdqt5` | `thiago-thomaz/proativos` | `proativos.projetosunion.cloud` | `running:unknown` | **Intocado** |
| `radar-hub12verticais...` | `6atr2cuewo8c8r7ln1pgjcwx` | `thiago-thomaz/radar-hub12verticaisdeoportunidades` | `radar.projetosunion.cloud` | `running:healthy` | **Intocado** |
| `union-money-ai` | `q8xnbh2ncefepqe6nhpqsgju` | `thiago-thomaz/union-money-ai` | `afiliados.projetosunion.cloud` | `running:healthy` | **Intocado** |
| `autopilot` | `i9mhxq0rhwwxnp7071x1wvoz` | `thiago-thomaz/Autopilot` | — | `exited:unhealthy` (pré-existente) | **Intocado** |
| `bot-meu-autonomo` | `y14k4xks800hdnh7m9awpfo6` | `thiago-thomaz/bot-meu-autonomo` | `y14k4...sslip.io` | `exited:unhealthy` (pré-existente) | **Intocado** |
| `docker-image-kfqib...` | `kfqib7khsae0hnnurptry6bu` | `coollabsio/coolify` | `evo.projetosunion.cloud` | `exited:unhealthy` (pré-existente) | **Intocado** |
| `fire-crawl-novo` | `gfxoo96afl9goh4isz1eqxaf` | `thiago-thomaz/FireCrawl-novo` | `app.projetosunion.cloud` | `exited:unhealthy` (pré-existente) | **Intocado** |
| `metatrader5-xp` (Service) | `q94awai6zskgc5wzr3desi8s` | Service container | — | `exited` (pré-existente) | **Intocado** |

> **Conclusão de Infraestrutura**: Nenhuma aplicação vizinha teve container reiniciado, variável alterada, rota Traefik modificada ou banco acessado. Todos os recursos saudáveis permaneceram `running:healthy` / ativos após o rollout do `union-growth-os`.
