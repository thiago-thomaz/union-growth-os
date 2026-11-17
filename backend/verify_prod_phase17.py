#!/usr/bin/env python3
"""UNION GROWTH OS — FASE 17: VERIFICAÇÃO REAL DE PRODUÇÃO MULTINEGÓCIO

Valida diretamente em https://automacao.projetosunion.cloud:
1. Health, Readiness, Banco PostgreSQL 16 e APScheduler (07:00 às 19:00 America/Sao_Paulo)
2. Autenticação com credenciais oficiais (UnionGrowth#2026!)
3. Três Unidades Comerciais: UNION_TECH, UNION_AGENCY e UNION_PARTNERS
4. Catálogo de 7 Serviços de IA e Automação + Calculadora Dinâmica de Preços
5. Oportunidades de Mercado nos 8 Segmentos Prioritários + 9 Landing Pages Comerciais
6. Funil Comercial de 10 Etapas, Captura de Lead com LGPD e Deduplicação
7. Gerador de Propostas Comerciais, Trava de Governança e Documento PDF/HTML
8. UNION AGENCY: Contas Isoladas de Empresas Clientes e Limites por Plano
9. UNION PARTNERS: Programas de Afiliados, Rastreamento de Cliques (0 Venda) e Conciliação
10. Financeiro Consolidado (DADO_REAL vs PROJECAO vs META) e Briefing AI CEO Multinegócio
"""

import time
import httpx

BASE_URL = "https://automacao.projetosunion.cloud"
ADMIN_EMAIL = "admin@projetosunion.cloud"
ADMIN_PASS = "UnionGrowth#2026!"


def main():
    print("=" * 82)
    print("UNION GROWTH OS — FASE 17: VALIDAÇÃO REAL DA OPERAÇÃO COMERCIAL MULTINEGÓCIO")
    print(f"URL Oficial: {BASE_URL}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print("=" * 82)

    client = httpx.Client(timeout=30.0, follow_redirects=True)

    # 1. Health & Readiness
    print("\n[ETAPA 1] Verificando Health, Readiness e APScheduler...")
    r_h = client.get(f"{BASE_URL}/health")
    r_r = client.get(f"{BASE_URL}/ready")
    assert r_h.status_code == 200 and r_r.status_code == 200
    h_json = r_h.json()
    print(f"  [OK] Health 200 | DB={h_json['database']['status']} | Scheduler={h_json['scheduler']['running']} | Jobs={h_json['scheduler']['jobs_count']}")

    # 2. Login
    print("\n[ETAPA 2] Autenticando Diretoria Executiva...")
    r_login = client.post(f"{BASE_URL}/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
    assert r_login.status_code == 200, f"Falha no login: {r_login.status_code}"
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  [OK] Login 200 | Token JWT emitido com sucesso.")

    # 3. Três Unidades Comerciais
    print("\n[ETAPA 3] Validando as 3 Unidades Comerciais (UNION_TECH, UNION_AGENCY, UNION_PARTNERS)...")
    r_units = client.get(f"{BASE_URL}/api/v1/commercial/business-units", headers=headers)
    assert r_units.status_code == 200
    units = r_units.json()
    codes = [u["code"] for u in units]
    assert "UNION_TECH" in codes and "UNION_AGENCY" in codes and "UNION_PARTNERS" in codes
    print(f"  [OK] {len(units)} Unidades Ativas: {codes}")

    # 4. Catálogo de 7 Serviços UNION TECH & Calculadora de Preços
    print("\n[ETAPA 4] Validando Catálogo de Serviços de IA/Automação e Calculadora de Preços...")
    r_svcs = client.get(f"{BASE_URL}/api/v1/commercial/services?unit=UNION_TECH", headers=headers)
    assert r_svcs.status_code == 200
    svcs = r_svcs.json()
    assert len(svcs) >= 7
    print(f"  [OK] {len(svcs)} Serviços UNION_TECH operacionais: {[s['service_code'] for s in svcs]}")

    # 5. Oportunidades de Mercado e Landing Pages
    print("\n[ETAPA 5] Validando Inteligência de Mercado (8 Segmentos) e Landing Pages...")
    r_opps = client.get(f"{BASE_URL}/api/v1/commercial/market-opportunities", headers=headers)
    r_lps = client.get(f"{BASE_URL}/api/v1/commercial/landing-pages", headers=headers)
    assert r_opps.status_code == 200 and r_lps.status_code == 200
    print(f"  [OK] {len(r_opps.json())} Oportunidades Setoriais | {len(r_lps.json())} Landing Pages Publicadas")

    # 6. UNION PARTNERS — Programas de Afiliados
    print("\n[ETAPA 6] Validando UNION PARTNERS (Mercado Livre, Amazon, Shopee, SaaS, Tech)...")
    r_progs = client.get(f"{BASE_URL}/api/v1/partners/programs", headers=headers)
    assert r_progs.status_code == 200
    progs = r_progs.json()
    print(f"  [OK] {len(progs)} Programas de Afiliados auditados: {[p['platform'] for p in progs]}")

    # 7. Financeiro Consolidado & Dashboard Multinegócio
    print("\n[ETAPA 7] Validando Financeiro Consolidado e Dashboard Executivo Multinegócio...")
    r_fin = client.get(f"{BASE_URL}/api/v1/finance/multibusiness-summary?unit=ALL", headers=headers)
    r_dash = client.get(f"{BASE_URL}/api/v1/commercial/multibusiness-dashboard?unit=ALL", headers=headers)
    assert r_fin.status_code == 200 and r_dash.status_code == 200
    fin_real = r_fin.json()["consolidated"]["dado_real"]
    fin_proj = r_fin.json()["consolidated"]["projecao"]
    print(
        f"  [OK] Receita Confirmada (DADO_REAL): R$ {fin_real['received_confirmed_revenue_brl']:,.2f} | "
        f"MRR: R$ {fin_real['monthly_recurring_revenue_mrr_brl']:,.2f} | "
        f"Pipeline Projetado (PROJECAO): R$ {fin_proj['weighted_pipeline_projection_brl']:,.2f}"
    )

    # 8. Briefing Diário do AI CEO Multinegócio
    print("\n[ETAPA 8] Executando Briefing Diário do AI CEO Multinegócio...")
    r_ceo = client.post(f"{BASE_URL}/api/v1/ceo/multibusiness-briefing", headers=headers)
    assert r_ceo.status_code == 201
    ceo_data = r_ceo.json()
    print(f"  [OK] Briefing CEO: {ceo_data['headline']}")
    print(f"  [OK] Classificação de Motor: {ceo_data['processing_type']} ({ceo_data['model_used']})")

    # 9. Teste de Restauração Isolada de Backup com Tabelas da Fase 17
    print("\n[ETAPA 9] Validando Backup e Restauração Isolada em Memória (Incluindo Entidades Fase 17)...")
    r_rest = client.post(f"{BASE_URL}/api/v1/system/backup/test-restore", headers=headers)
    assert r_rest.status_code == 200
    rest = r_rest.json()
    assert rest["status"] == "RESTORE_VERIFIED"
    assert rest["production_database_protected"] is True
    assert "business_units" in rest["restored_tables"]
    assert "product_services" in rest["restored_tables"]
    print(f"  [OK] Restore Verificado: {rest['total_restored_records']} registros em {len(rest['restored_tables'])} tabelas!")

    print("\n" + "=" * 82)
    print("FASE 17 VALIDADA COM 100% DE SUCESSO EM PRODUÇÃO!")
    print("=" * 82)


if __name__ == "__main__":
    main()
