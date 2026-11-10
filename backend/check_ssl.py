import socket
import ssl
import httpx

hostname = "automacao.projetosunion.cloud"

print("=" * 60)
print(f"VERIFICANDO CERTIFICADO SSL E ENDPOINTS EM: {hostname}")
print("=" * 60)

ctx = ssl.create_default_context()
with socket.create_connection((hostname, 443), timeout=10) as sock:
    with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
        cert = ssock.getpeercert()
        print("Cert Subject:", dict(x[0] for x in cert.get("subject", [])))
        print("Cert Issuer:", dict(x[0] for x in cert.get("issuer", [])))
        print("Cert Valid Until:", cert.get("notAfter"))
        print("Cipher Suite:", ssock.cipher())

with httpx.Client(timeout=15.0, follow_redirects=True) as client:
    for path in ["/", "/health", "/ready", "/robots.txt", "/sitemap.xml", "/api/v1/auth/login"]:
        url = f"https://{hostname}{path}"
        res = client.get(url) if path != "/api/v1/auth/login" else client.post(url, json={})
        print(f"[{res.status_code}] {url} -> Content-Type: {res.headers.get('content-type')}")

print("\nVERIFICAÇÃO CONCLUÍDA COM SUCESSO!")
