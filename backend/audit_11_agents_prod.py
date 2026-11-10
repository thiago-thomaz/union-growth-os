import httpx
import time
import json

token_resp = httpx.post('https://automacao.projetosunion.cloud/api/v1/auth/login', json={'email': 'admin@projetosunion.cloud', 'password': 'UnionGrowth#2026!'})
token = token_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

agents = [
    ('AGENT_01_CEO', 'CEO Daily Briefing', {}),
    ('AGENT_02_CMO', 'Plano de Marketing Mensal', {'campaign_name': 'Expansao Q1'}),
    ('AGENT_03_SEO', 'Auditoria Tecnica SEO', {'target_url': 'https://automacao.projetosunion.cloud'}),
    ('AGENT_04_SOCIAL', 'Calendario Social 7 Dias', {'platforms': ['instagram', 'linkedin']}),
    ('AGENT_05_CREATIVE', 'Asset Grafico PNG', {'headline': 'Union Growth OS Ativo'}),
    ('AGENT_06_COPYWRITER', 'Copy AIDA Alta Conversao', {'product_name': 'Union Growth OS', 'target_audience': 'CEOs e Diretores'}),
    ('AGENT_07_GROWTH', 'Experimento ICE', {'metric': 'Taxa de Conversao'}),
    ('AGENT_08_SALES', 'Lead Scoring e Forecast', {}),
    ('AGENT_09_COMPETITIVE', 'Analise Competitiva Publica', {'competitor_url': 'https://example.com'}),
    ('AGENT_10_FINANCE', 'KPIs Financeiros Consolidados', {}),
    ('AGENT_11_CS', 'Matriz NPS e Retenção', {})
]

print("=== EXECUTING REAL AUDIT OF 11 AGENTS ON PRODUCTION ===")
results = []
for agent_id, name, params in agents:
    t0 = time.time()
    try:
        r = httpx.post(f"https://automacao.projetosunion.cloud/api/v1/agents/{agent_id}/execute", headers=headers, json=params, timeout=30.0)
        dt = time.time() - t0
        st = r.status_code
        print(f"[{agent_id}] ({name}) -> HTTP {st} in {dt:.2f}s")
        if st == 200:
            d = r.json()
            res_obj = d.get("result", {})
            res_keys = list(res_obj.keys()) if isinstance(res_obj, dict) else str(type(res_obj))
            status_val = d.get("status")
            print(f"   Status: {status_val} | Keys: {res_keys}")
            results.append({
                "agent_id": agent_id,
                "name": name,
                "status_code": st,
                "duration_s": round(dt, 2),
                "status": status_val,
                "keys": res_keys,
                "sample": str(res_obj)[:150]
            })
        else:
            print(f"   Error: {r.text[:200]}")
            results.append({
                "agent_id": agent_id,
                "name": name,
                "status_code": st,
                "duration_s": round(dt, 2),
                "error": r.text[:200]
            })
    except Exception as e:
        print(f"   Exception: {e}")
        results.append({
            "agent_id": agent_id,
            "name": name,
            "error": str(e)
        })

print("\n--- Summary of Agent Execution ---")
print(f"Total audited: {len(results)} | Successful: {sum(1 for x in results if x.get('status_code') == 200)}")

# Also query the execution logs to verify database persistence
logs_resp = httpx.get("https://automacao.projetosunion.cloud/api/v1/agents/execution-logs?limit=15", headers=headers)
print(f"Agent Execution Logs Endpoint: HTTP {logs_resp.status_code}")
if logs_resp.status_code == 200:
    logs = logs_resp.json().get("items", [])
    print(f"Total persisted logs fetched: {len(logs)}")
    for l in logs[:5]:
        print(f" - {l.get('created_at')} | {l.get('agent_name')} | Status: {l.get('status')} | Engine: {l.get('processing_type')} | Model: {l.get('model_used')} | Cost: R$ {l.get('estimated_cost_brl')}")
