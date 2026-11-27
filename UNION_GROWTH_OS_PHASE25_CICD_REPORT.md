# UNION GROWTH OS — FASE 25: RELATÓRIO DE CI/CD & COOLIFY AUTO DEPLOY

## 1. Diagnóstico Independente de CI/CD & Auto Deploy Realizado na Fase 25
Durante a execução da Fase 25, o CI no GitHub Actions (`46025223779`) detectou duas falhas reais antes de atingir o estado verde final:
1. **Scanner de Segredos no YAML:** [ci-cd.yml](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/.github/workflows/ci-cd.yml) mantinha string literal de token antigo no próprio verificador. Foi substituído por expressões regulares genéricas (`ghp_...`, `AIzaSy...`, `Bearer \d+|...`).
2. **Erro Transitório `502` no Container Swap:** [ci_deploy_and_verify.py](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity%20-%20Projetos/2027/Marketing%20Digital%20automático/union-growth-os/scripts/ci_deploy_and_verify.py) realizava apenas 1 tentativa por endpoint enquanto o Coolify trocava o container no Traefik. Foram adicionadas até **4 tentativas com pausa de 5s** exclusivamente em erros `502/503/504`/conexão, mantendo obrigatoriedade integral de `HTTP 200`, DB saudável e scheduler ativo, além de registro honesto em `$GITHUB_STEP_SUMMARY`.

---

## 2. Validação do Pipeline Após Correção
- **GitHub Actions Run `46043812259`** (commit `b6162c2859b16514b8666736f23c0e9d9c8ac34a`):
  - Job `Backend Tests, Frontend Build, Security Audit & Docker Lint`: **`completed / success`** (`52/52` pytest + `tsc` + `next build` + Dockerfile lint + secret regex scan).
  - Job `Automatic Deploy to Coolify VPS & Production Health Checks`: **`completed / success`**.

---

## 3. Auditoria Honesta Sobre Auto Deploy Automático (Ação Pendente do Proprietário)
**Veredito Sem Maquiagem:** o deploy deste ciclo foi disparado via API oficial autenticada do Coolify (`coolify:deploy`, deployment `vb5t8pngj2c7qpq5pklnwqpe`), **não** por push automático passivo:
- No Coolify, a aplicação `union-growth-os` (`swpy83sa5wshb558fadlrzwc`) usa `source_id: 0` (GitHub público) com `is_auto_deploy_enabled: false`. O GitHub App cadastrado (`meu-github-app-tt`, `app_id: 4393428`) lista o repositório com `permissions.pull: false`.
- No GitHub (`thiago-thomaz/union-growth-os`), os Secrets `COOLIFY_API_TOKEN` e `COOLIFY_DEPLOY_WEBHOOK` não estão preenchidos (`PENDING_GITHUB_SECRETS`).

**Passos Exatos para 100% Auto Deploy Zero-Toque (Proprietário):**
1. No **GitHub -> Repo Settings -> Secrets and variables -> Actions**, adicionar `COOLIFY_API_TOKEN` (token API do Coolify) e `COOLIFY_DEPLOY_WEBHOOK` (`http://72.62.13.62:8000/api/v1/deploy?uuid=swpy83sa5wshb558fadlrzwc`).
2. Opcionalmente no **Coolify -> GitHub App (`meu-github-app-tt`)**, conceder permissão de `Contents: Read` no repositório `thiago-thomaz/union-growth-os` e ativar `Auto Deploy` na configuração da aplicação.
