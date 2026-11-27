# UNION GROWTH OS — DESIGN SYSTEM 5.0 (FASE 27)

## 1. Tokens & Componentes Evoluídos

- **Tema Duplo (`globals.css`)**: Obsidian Dark (`#09090b`, `#0c0c0f`, `#111115`) & Alabaster Light (`#fafafa`, `#ffffff`, `#f4f4f5`) com bordas hairline (`--ug-border-subtle`) e `.tabular-nums` em indicadores financeiros, scores e latências.
- **`DesignSystem.tsx` (`MetricStripItem` v5.0)**:
  - Campos suportados: `key`, `label`, `value`, `subtext`, `origin` (`REAL`/`ESTIMATED`/`IMPORTED`/`SANDBOX`), `source`, `period`, `updatedAt`, `statusLabel`, `calculationMethod`, `onClick`.
- **`StatusPill` & `OriginBadge`**:
  - Estados tipados (`EXECUTED`, `RUNNING`, `PENDING`, `BLOCKED`, `FAILED`, `SIMULATED`, `SANDBOX`, `NEEDS_CREDENTIALS`) com labels customizáveis em português (`Concluído`, `Replanejado`, `Planejado`, `Cancelado`).
- **Novos Componentes Modulares Fase 27**:
  - `ReleaseHistoryDrawer.tsx` (`202` linhas): usa `Drawer` acessível (`Escape`, `aria-modal`, foco).
  - `AuditCenterWorkspace.tsx` (`356` linhas): `PlainOrientationBar`, `MetricStrip`, `FilterTabBar`, tabela responsiva da Matriz e painéis de restauração SHA-256.
- **Tamanho de Bundle Medido**: rota principal `/` com `83.7 kB` (First Load JS `189 kB`) após build estático Next.js `15.1.3`.
