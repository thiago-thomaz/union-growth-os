import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
data = json.loads(
    (root / "UNION_GROWTH_OS_PHASE20_1_EVIDENCE" / "routes" / "independent_route_coverage.json").read_text(encoding="utf-8")
)

lines = [
    "# UNION GROWTH OS — COBERTURA INDEPENDENTE DE TODAS AS ROTAS DA API (FASE 20.1)",
    "",
    f"**Total de Rotas da Aplicação (`app.routes + api_v1_router`):** `{data['total_app_routes']}`  ",
    f"**Total de Rotas de API (Método + Caminho):** `{data['total_api_method_routes']}` (`{data['unique_api_paths']}` caminhos únicos, incluindo catch-all 404 `/api/{{full_path:path}}`)  ",
    f"**Rotas Duplicadas:** `{len(data['duplicates'])}`  ",
    f"**Rotas Indevidamente Sem Autenticação:** `{len(data['unexpected_unauthenticated_api_routes'])}`  ",
    f"**Aprovadas / Falhas no Teste Automatizado Individual:** **`{data['routes_passed']}/{data['total_api_method_routes']}` (`{data['routes_failed']}` falhas)**  ",
    "**Evidência JSON Bruta:** `UNION_GROWTH_OS_PHASE20_1_EVIDENCE/routes/independent_route_coverage.json`",
    "",
    "## Metodologia Independente Aplicada por Rota",
    "Diferente da Fase 20 (que apenas cruzou strings `apiFetch` do frontend), a Fase 20.1 executou **3 chamadas HTTP reais por rota** em banco SQLite isolado (`phase20_1_route_audit.db`):",
    "1. **Sem Autenticação:** valida bloqueio obrigatório `HTTP 401` em todas as rotas protegidas.",
    "2. **Cross-Tenant (`X-Tenant-Id: 999999`):** valida bloqueio obrigatório `HTTP 403` em todas as rotas autenticadas.",
    "3. **Smoke / Validação Autenticada:** valida que nenhuma rota retorna `HTTP 500` (apenas `200/201/400/403/404/422` esperados). Durante o primeiro teste sem elevar o limite local, a rota #66 disparou `HTTP 429 Too Many Requests` após 180 req/min, comprovando o funcionamento real do Rate Limiter.",
    "",
    "## Matriz Completa das 136 Rotas de API Auditadas",
    "",
    "| # | Método | Caminho | Função | Auth | RBAC | Tenant | Body Schema | Unauth HTTP | Cross-Tenant HTTP | Auth Smoke HTTP | Status |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|",
]

for i, r in enumerate(data["all_routes"], 1):
    lines.append(
        f"| {i} | `{r['method']}` | `{r['path']}` | `{r['function']}` | {r['has_auth']} | {r['has_rbac']} | {r['uses_tenant']} | {r['has_body_schema']} | `{r['unauth_status']}` | `{r['cross_tenant_status']}` | `{r['auth_smoke_status']}` | **{r['verdict']}** |"
    )

out_path = root / "UNION_GROWTH_OS_PHASE20_1_ROUTE_COVERAGE.md"
out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {len(lines)} lines to {out_path}")
