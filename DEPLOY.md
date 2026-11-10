# Guia de Deploy em Cloud (GitHub + Docker + Coolify) — UNION GROWTH OS

## 1. Arquitetura de Deploy em Nuvem

O **UNION GROWTH OS** foi projetado para rodar 24/7 em servidor Cloud gerenciado pelo **Coolify** com proxy reverso **Traefik + Let's Encrypt HTTPS**, banco de dados **PostgreSQL persistente** e volumes dedicados para ativos e backups.

---

## 2. Fluxo Automatizado de Deploy Contínuo

1. **Desenvolvimento e Testes**:
   - Execute `pytest backend/tests -v` para validar todos os módulos antes do commit.
2. **Versionamento Git & GitHub**:
   - Repositório: `thiago-thomaz/union-growth-os` (branch `main`).
3. **Build & Deploy no Coolify**:
   - Build Pack: `dockerfile` (`/Dockerfile` multi-stage que compila o Next.js e empacota o backend Python 3.12 + APScheduler).
   - Porta Exposta: `8000`.
   - Health Check: `GET /health` (intervalo 20s).
4. **Persistência e Segurança**:
   - Banco de Dados PostgreSQL persistente via `DATABASE_URL`.
   - Volumes persistentes preservados entre deploys (`delete_volumes=false`).

---

## 3. Política de Rollback

Caso uma atualização apresente falha no health check (`/health` ou `/ready`):
1. O container antigo é mantido pelo Traefik até que o novo container passe no health check.
2. Para reverter manualmente para um commit anterior no Coolify, acione o deploy do SHA anterior ou execute `git revert HEAD && git push origin main`.
3. Caso necessário restaurar dados, utilize os snapshots gerados em `/app/data/backups` via endpoint `POST /api/v1/system/backup`.
