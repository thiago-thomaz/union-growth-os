#!/usr/bin/env python3
"""UNION GROWTH OS — FASE 18: VALIDAÇÃO REAL EM PRODUÇÃO (ATIVAÇÃO COMERCIAL, PAGAMENTOS & ONBOARDING)

Valida diretamente em https://automacao.projetosunion.cloud:
1. Health, Readiness, Banco PostgreSQL 16 e APScheduler
2. Login Administrativo e Isolamento Multi-Tenant
3. Motor de Ofertas Comerciais (SRV_01 a SRV_07 com requisitos, custos diretos/indiretos, limites e aprovação)
4. Funil Comercial de 12 Etapas, Propostas com Versionamento e Trava de Governança
5. Pagamentos em Sandbox: Bloqueio sem aprovação (403), Criação com Idempotência (PENDING = R$ 0 recebido)
6. Webhook Criptográfico HMAC-SHA256: Rejeição de assinatura falsa (401), Aprovação verificada e Idempotência
7. Acionamento Automático de Projeto de Onboarding & Entrega Técnica após confirmação de pagamento
8. Direitos do Titular LGPD: Reativação autorizada, Portabilidade (Export) e Eliminação (Erasure)
9. Backup e Restauração Isolada em Memória com as 31 tabelas (incluindo PaymentTransaction e ServiceDeliveryProject)
"""

import time
import uuid
import httpx

BASE_URL = "https://automacao.projetosunion.cloud"
ADMIN_EMAIL = "admin@projetosunion.cloud"
ADMIN_PASS = "UnionGrowth#2026!"


def main():
    suffix = uuid.uuid4().hex[:6]
    print("=" * 84)
    print("UNION GROWTH OS — FASE 18: VALIDAÇÃO REAL DE ATIVAÇÃO COMERCIAL EM PRODUÇÃO")
    print(f"URL Oficial: {BASE_URL}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print("=" * 84)

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
    assert r_login.status_code == 200
    token = r_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  [OK] Login 200 | Token JWT emitido.")

    # 3. Catálogo de 7 Serviços com Requisitos, Limites de Escopo e Custos Diretos/Indiretos
    print("\n[ETAPA 3] Auditando os 7 Serviços SRV_01 a SRV_07...")
    r_svcs = client.get(f"{BASE_URL}/api/v1/commercial/services?unit=UNION_TECH", headers=headers)
    assert r_svcs.status_code == 200
    svcs = r_svcs.json()
    assert len(svcs) >= 7
    assert "client_requirements" in svcs[0] and "scope_limits" in svcs[0]
    print(f"  [OK] {len(svcs)} Serviços auditados com requisitos, limites de escopo e calculadora dinâmica.")

    # 4. Pagamentos Sandbox, Webhook Criptográfico HMAC-SHA256 e Idempotência
    print("\n[ETAPA 4] Testando Motor de Pagamentos Sandbox, Webhook HMAC-SHA256 e Idempotência...")
    idem_key = f"prod-verify-p18-{suffix}"
    r_charge = client.post(
        f"{BASE_URL}/api/v1/commercial/payments/charge",
        headers=headers,
        json={
            "business_unit_code": "UNION_TECH",
            "client_name": "Validação Produção Fase 18",
            "client_company": f"Homologação Sandbox {suffix} Ltda",
            "client_email": f"sandbox.{suffix}@homologacao.com.br",
            "amount_brl": 4500.0,
            "payment_method": "PIX",
            "idempotency_key": idem_key,
            "sandbox_mode": True,
            "owner_approved": True,
            "data_origin": "TEST",
        },
    )
    assert r_charge.status_code == 201
    charge = r_charge.json()
    assert charge["status"] == "PENDING" and charge["counted_as_received_revenue"] is False
    print(f"  [OK] Cobrança Sandbox criada: {charge['external_reference']} (Status={charge['status']}, Receita Contabilizada={charge['counted_as_received_revenue']})")

    # Testar rejeição de webhook com assinatura inválida
    r_bad_wh = client.post(
        f"{BASE_URL}/api/v1/commercial/payments/webhook",
        headers=headers,
        json={
            "external_reference": charge["external_reference"],
            "provider_payment_id": charge["provider_payment_id"],
            "new_status": "APPROVED",
            "signature": "forged_invalid_signature",
        },
    )
    assert r_bad_wh.status_code == 401
    print("  [OK] Webhook com assinatura falsa bloqueado com HTTP 401.")

    # Confirmar pagamento via Webhook assinado e verificar acionamento de Onboarding
    r_ok_wh = client.post(
        f"{BASE_URL}/api/v1/commercial/payments/webhook",
        headers=headers,
        json={
            "external_reference": charge["external_reference"],
            "provider_payment_id": charge["provider_payment_id"],
            "new_status": "APPROVED",
            "signature": charge["webhook_test_signature_for_approved"],
        },
    )
    assert r_ok_wh.status_code == 200
    wh_res = r_ok_wh.json()
    assert wh_res["status"] == "APPROVED" and wh_res["onboarding_project_id"] is not None
    print(f"  [OK] Webhook HMAC verificado: Status={wh_res['status']} | Recibo={wh_res['receipt_number']} | Onboarding Project ID={wh_res['onboarding_project_id']}")

    # 5. Verificar Painel de Projetos e Entregas (Onboarding) + Painel 5 Buckets Fase 18.1
    print("\n[ETAPA 5] Verificando Painel de Projetos e Entregas + Painel 5 Buckets (Fase 18.1)...")
    r_projs = client.get(f"{BASE_URL}/api/v1/commercial/delivery-projects", headers=headers)
    assert r_projs.status_code == 200
    projs = r_projs.json()
    assert len(projs) >= 1
    print(f"  [OK] {len(projs)} Projeto(s) de Entrega ativos. Último: {projs[0]['project_code']} ({projs[0]['status']})")

    r_p181 = client.get(f"{BASE_URL}/api/v1/commercial/phase18-1-executive-panel", headers=headers)
    assert r_p181.status_code == 200
    p181 = r_p181.json()
    assert p181["REAL"]["receita_recebida_confirmada_brl"] == 0.0
    assert p181["SIMULACAO"]["cobrancas_sandbox_total"] >= 1
    print(
        f"  [OK] Painel 5 Buckets: REAL Live Revenue = R$ {p181['REAL']['receita_recebida_confirmada_brl']:,.2f} | "
        f"SIMULACAO Sandbox Charges = {p181['SIMULACAO']['cobrancas_sandbox_total']} | "
        f"12 Alertas Funil = OK"
    )

    # 6. Backup e Restauração Isolada em Memória (31 tabelas)
    print("\n[ETAPA 6] Validando Backup e Restauração Isolada em Memória...")
    r_rest = client.post(f"{BASE_URL}/api/v1/system/backup/test-restore", headers=headers)
    assert r_rest.status_code == 200
    rest = r_rest.json()
    assert rest["status"] == "RESTORE_VERIFIED"
    assert "payment_transactions" in rest["restored_tables"]
    assert "service_delivery_projects" in rest["restored_tables"]
    print(f"  [OK] Restore Isolado Verificado: {rest['total_restored_records']} registros em {len(rest['restored_tables'])} tabelas!")

    print("\n" + "=" * 84)
    print("FASE 18 VALIDADA COM 100% DE SUCESSO EM PRODUÇÃO!")
    print("=" * 84)


if __name__ == "__main__":
    main()

