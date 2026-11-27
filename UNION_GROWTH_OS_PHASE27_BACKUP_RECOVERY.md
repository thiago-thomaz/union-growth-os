# UNION GROWTH OS — BACKUP, INTEGRIDADE SHA-256 & RECUPERAÇÃO ISOLADA (FASE 27)

## 1. Mecanismo Verificado em Produção

- **Geração de Snapshot Portátil:** `POST /api/v1/system/backup` cria JSON versionado isolado por tenant em `data/backups/` com cálculo de digest **SHA-256** e retenção automática (`enforce_backup_retention(retention_days=30, min_backups_kept=5)`).
- **Trava Anti-Sobrescrita de Produção:** `restore_database_from_backup` (`database.py:435`) bloqueia explicitamente `target_url == ACTIVE_DB_URL` se `allow_production_overwrite=False`.
- **Teste de Restauração Isolada na UI (Novo na Fase 27):**
  - Exposto diretamente via botão **"Testar Restauração Isolada"** em `AuditCenterWorkspace.tsx` e **"Testar Restauração Isolada (SHA-256)"** em `ManagementAndIntegrationsWorkspace.tsx` (`Relatórios`).
  - Executa `POST /api/v1/system/backup/test-restore` restaurando integralmente para **`sqlite:///:memory:`**.
  - **Evidência Live em Produção (`05_phase27_backup_restore_test.png`):**
    - Arquivo testado: `backup_tenant_5_20261127_211201_862014.json`
    - Digest: `SHA-256: 810e2c4290d0a633f0559a8921fc94328819c613c1fcbc0890181dfd530f4f50`
    - Resultado: **`RESTORE_VERIFIED` — `145` registros restaurados e validados em `31` tabelas**.
- **Score Categoria 22 (`Backup`):** **`92.0 / 100` (`REAL`)** — único gap restante: replicação off-site opcional em bucket S3/Backblaze (depende credenciais externas).
