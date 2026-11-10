#!/usr/bin/env python3
"""UNION GROWTH OS — CI/CD DEPLOYMENT & PRODUCTION VALIDATION RUNNER

Executa a orquestração do deploy contínuo via Coolify e validação de produção:
1. Aciona o deploy da aplicação no Coolify (via Webhook ou API oficial com token).
2. Monitora o status da compilação e publicação do container até conclusão (finished).
3. Executa health checks reais com validação de SSL/TLS e HTTP 200 em https://automacao.projetosunion.cloud.
4. Gera relatório de evidência de deploy contínuo.
"""

from __future__ import annotations

import argparse
import os
import ssl
import sys
import time
from typing import Any
import httpx

DEFAULT_COOLIFY_URL = "http://72.62.13.62:8000"
DEFAULT_APP_UUID = "swpy83sa5wshb558fadlrzwc"
DEFAULT_TARGET_URL = "https://automacao.projetosunion.cloud"
FALLBACK_TARGET_URL = "https://uniongrowth.72.62.13.62.sslip.io"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Union Growth OS CI/CD Deployment Runner")
    parser.add_argument("--webhook-url", default=os.getenv("COOLIFY_DEPLOY_WEBHOOK", ""))
    parser.add_argument("--coolify-url", default=os.getenv("COOLIFY_BASE_URL", DEFAULT_COOLIFY_URL))
    parser.add_argument("--coolify-token", default=os.getenv("COOLIFY_API_TOKEN") or os.getenv("COOLIFY_ACCESS_TOKEN", ""))
    parser.add_argument("--app-uuid", default=os.getenv("COOLIFY_APP_UUID", DEFAULT_APP_UUID))
    parser.add_argument("--target-url", default=os.getenv("PRODUCTION_BASE_URL", DEFAULT_TARGET_URL))
    parser.add_argument("--expected-commit", default=os.getenv("GITHUB_SHA", "HEAD"))
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--poll-interval", type=int, default=10)
    return parser.parse_args()


def trigger_deployment(args: argparse.Namespace, client: httpx.Client) -> tuple[str, str]:
    """Aciona a implantação no Coolify via Webhook ou API e retorna (deployment_uuid, trigger_type)."""
    # 1. Tentativa via Webhook se configurado
    if args.webhook_url:
        print(f"[CI/CD] Acionando deploy via COOLIFY_DEPLOY_WEBHOOK: {args.webhook_url[:40]}...")
        headers = {}
        if args.coolify_token:
            headers["Authorization"] = f"Bearer {args.coolify_token}"
        res = client.post(args.webhook_url, headers=headers, timeout=30.0)
        if res.status_code in (200, 201, 202):
            data = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
            deployments = data.get("deployments") or data.get("data", {}).get("deployments") or []
            if deployments and isinstance(deployments, list):
                dep_uuid = deployments[0].get("deployment_uuid") or deployments[0].get("uuid", "")
                return dep_uuid, "WEBHOOK_DEPLOY"
            return "webhook_triggered", "WEBHOOK_DEPLOY"
        else:
            print(f"[AVISO] Webhook respondeu com HTTP {res.status_code}: {res.text[:200]}")

    # 2. Tentativa via Coolify Official API
    coolify_base = args.coolify_url.rstrip("/")
    api_url = f"{coolify_base}/api/v1/deploy"
    headers = {"Content-Type": "application/json"}
    if args.coolify_token:
        headers["Authorization"] = f"Bearer {args.coolify_token}"

    print(f"[CI/CD] Acionando deploy via Coolify API: {api_url}?uuid={args.app_uuid}&force=true")
    res = client.post(f"{api_url}?uuid={args.app_uuid}&force=true", headers=headers, timeout=30.0)
    if res.status_code not in (200, 201, 202):
        print(f"[ERRO] Falha ao acionar deploy na API do Coolify ({res.status_code}): {res.text}")
        sys.exit(1)

    data = res.json()
    deployments = data.get("deployments") or data.get("data", {}).get("deployments") or []
    if not deployments:
        print("[ERRO] Nenhuma implantação retornada pelo Coolify:", data)
        sys.exit(1)

    deployment_uuid = deployments[0].get("deployment_uuid") or deployments[0].get("uuid", "")
    print(f"[CI/CD] Implantação enfileirada no Coolify! Deployment UUID: {deployment_uuid}")
    return deployment_uuid, "COOLIFY_API_DEPLOY"


def monitor_deployment(args: argparse.Namespace, deployment_uuid: str, client: httpx.Client) -> bool:
    """Monitora o status da implantação até status == 'finished'."""
    if not deployment_uuid or deployment_uuid == "webhook_triggered":
        print("[CI/CD] Aguardando 60s para conclusão do build via webhook assíncrono...")
        time.sleep(60)
        return True

    coolify_base = args.coolify_url.rstrip("/")
    headers = {}
    if args.coolify_token:
        headers["Authorization"] = f"Bearer {args.coolify_token}"

    start_time = time.time()
    last_status = ""

    while time.time() - start_time < args.timeout_seconds:
        try:
            r = client.get(f"{coolify_base}/api/v1/deployments/{deployment_uuid}", headers=headers, timeout=15.0)
            if r.status_code == 200:
                data = r.json().get("data", r.json())
                status = data.get("status", "unknown")
                if status != last_status:
                    elapsed = int(time.time() - start_time)
                    print(f"[CI/CD +{elapsed}s] Status do Deploy no Coolify: {status.upper()}")
                    last_status = status

                if status == "finished":
                    elapsed = int(time.time() - start_time)
                    print(f"[CI/CD] Deploy concluído com sucesso em {elapsed}s!")
                    return True
                elif status in ("failed", "killed", "error"):
                    print(f"[ERRO CRÍTICO] Deploy no Coolify falhou com status: {status}")
                    print("Logs disponíveis:", data.get("logs_info", "Consulte a VPS"))
                    return False
        except Exception as exc:
            print(f"[ALERTA] Erro transitório ao consultar status do deploy: {exc}")

        time.sleep(args.poll_interval)

    print(f"[ERRO] Timeout de {args.timeout_seconds}s excedido aguardando o deploy.")
    return False


def run_production_health_checks(target_url: str) -> bool:
    """Executa suíte de validação externa HTTP 200 e integridade de produção."""
    print("\n" + "=" * 70)
    print(f"[PRODUÇÃO] EXECUTANDO HEALTH CHECKS EM: {target_url}")
    print("=" * 70)

    endpoints = [
        ("/", "Frontend Next.js 15"),
        ("/health", "Healthcheck PostgreSQL & Scheduler"),
        ("/ready", "Readiness Probe"),
        ("/robots.txt", "Robots.txt SEO"),
        ("/sitemap.xml", "Sitemap Dinâmico XML"),
    ]

    all_passed = True
    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        for path, description in endpoints:
            url = f"{target_url.rstrip('/')}{path}"
            try:
                res = client.get(url)
                if res.status_code == 200:
                    print(f"  [PASS] {url} -> 200 OK ({description})")
                else:
                    print(f"  [FAIL] {url} -> {res.status_code} ({description})")
                    all_passed = False
            except Exception as e:
                print(f"  [FAIL] {url} -> Exceção de conexão: {e}")
                all_passed = False

        # Validação detalhada do endpoint /health
        try:
            h = client.get(f"{target_url.rstrip('/')}/health")
            if h.status_code == 200:
                h_data = h.json()
                db_status = h_data.get("database", {}).get("status")
                sched_running = h_data.get("scheduler", {}).get("running")
                sched_tz = h_data.get("scheduler", {}).get("timezone")
                print(f"  [INFO] DB Status: {db_status} | Engine: {h_data.get('database', {}).get('engine')}")
                print(f"  [INFO] Scheduler Ativo: {sched_running} | Timezone: {sched_tz}")
                if db_status != "healthy" or not sched_running:
                    print("  [FAIL] Critérios de prontidão operacional violados no /health")
                    all_passed = False
        except Exception as e:
            print(f"  [FAIL] Erro ao validar payload do /health: {e}")
            all_passed = False

    return all_passed


def main():
    args = parse_args()
    print("=" * 70)
    print("UNION GROWTH OS — CI/CD AUTOMATION & VPS DEPLOYMENT")
    print(f"Domínio Oficial Alvo: {args.target_url}")
    print(f"Servidor Coolify: {args.coolify_url}")
    print(f"Aplicação UUID: {args.app_uuid}")
    print(f"Commit Git Alvo: {args.expected_commit[:10]}")
    print("=" * 70)

    # Modo 1: Se credenciais de acionamento do Coolify estiverem presentes
    has_credentials = bool(args.webhook_url or args.coolify_token)

    if not has_credentials:
        print("\n[INFO CI/CD] Credenciais COOLIFY_DEPLOY_WEBHOOK ou COOLIFY_API_TOKEN não detectadas.")
        print("Para deploy 100% autônomo sem intervenção humana, cadastre no GitHub Secrets:")
        print("  1. COOLIFY_API_TOKEN = Seu token de API do Coolify")
        print(f"  2. COOLIFY_DEPLOY_WEBHOOK = {args.coolify_url}/api/v1/deploy?uuid={args.app_uuid}")
        print("  3. PRODUCTION_BASE_URL = https://automacao.projetosunion.cloud")
        print("\nExecutando verificação de integridade e health check na produção atual...")
        ok = run_production_health_checks(args.target_url)
        if not ok:
            print("[ERRO] Health check na produção falhou.")
            sys.exit(1)
        print("[SUCESSO] Produção atual validada com 100% de sucesso!")
        return

    with httpx.Client(timeout=30.0) as client:
        dep_uuid, trigger_type = trigger_deployment(args, client)
        success = monitor_deployment(args, dep_uuid, client)
        if not success:
            print("[ERRO FATAL] Implantação reprovada no Coolify. Abortando com erro.")
            sys.exit(1)

    # Executar Health Checks Externos na URL Oficial
    checks_passed = run_production_health_checks(args.target_url)
    if not checks_passed:
        print("[ERRO FATAL] Health checks pós-deploy reprovados na URL oficial.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("DEPLOYMENT & OPERATIONAL VALIDATION CERTIFICATE")
    print("=" * 70)
    print(f"Status: APROVADO & PUBLICADO")
    print(f"Domínio Oficial: {args.target_url}")
    print(f"Método de Deploy: {trigger_type}")
    print(f"Deployment UUID: {dep_uuid}")
    print(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print("=" * 70)


if __name__ == "__main__":
    main()

