"""
Fichier : deploy_nginx_cluster/instance_fastapi.py
Exécution (4 instances FastAPI / Uvicorn sur 4 ports distincts) :
  PORT=8001 INSTANCE_ID=fastapi-node-1 .venv/bin/python deploy_nginx_cluster/instance_fastapi.py --serve
  PORT=8002 INSTANCE_ID=fastapi-node-2 .venv/bin/python deploy_nginx_cluster/instance_fastapi.py --serve
  PORT=8003 INSTANCE_ID=fastapi-node-3 .venv/bin/python deploy_nginx_cluster/instance_fastapi.py --serve
  PORT=8004 INSTANCE_ID=fastapi-node-4 .venv/bin/python deploy_nginx_cluster/instance_fastapi.py --serve

Ou en production avec Uvicorn (--proxy-headers) :
  INSTANCE_ID=fastapi-node-1 uvicorn deploy_nginx_cluster.instance_fastapi:app --host 127.0.0.1 --port 8001 --proxy-headers --forwarded-allow-ips="127.0.0.1"
"""

import os
import socket
import sys
import time
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient

app = FastAPI(
    title="ISGP — Instance Cluster FastAPI / Uvicorn (ASGI)",
    version="2.0.0",
)

# CRITIQUE DERRIÈRE NGINX : Avec Uvicorn (--proxy-headers), ou en lisant X-Forwarded-For / X-Real-IP,
# FastAPI récupère la véritable adresse IP du client transmise par le Reverse Proxy Nginx
# et le vrai protocole HTTPS dans 'X-Forwarded-Proto' (sinon request.client.host vaudrait '127.0.0.1').

PORT = int(os.environ.get("PORT", 8001))
INSTANCE_ID = os.environ.get("INSTANCE_ID", f"fastapi-node-{PORT}")
DEMARRAGE = time.time()


@app.middleware("http")
async def injecter_entetes_noeud(request: Request, call_next):
    """Ajoute l'identifiant de l'instance FastAPI/Uvicorn dans les en-têtes HTTP pour vérifier le Load Balancing."""
    reponse = await call_next(request)
    reponse.headers["X-FastAPI-Instance"] = INSTANCE_ID
    reponse.headers["X-FastAPI-Port"] = str(PORT)
    reponse.headers["X-FastAPI-PID"] = str(os.getpid())
    return reponse


@app.get("/api/health", status_code=status.HTTP_200_OK)
def healthcheck():
    """Sonde de santé appelée par Nginx ou l'orchestrateur pour vérifier que l'instance ASGI est vivante."""
    return {
        "statut": "UP",
        "moteur": "FastAPI / Uvicorn ASGI",
        "instance_id": INSTANCE_ID,
        "port": PORT,
        "pid": os.getpid(),
        "uptime_secondes": round(time.time() - DEMARRAGE, 1),
    }


@app.get("/api/v1/formations", status_code=status.HTTP_200_OK)
def lister_formations(request: Request):
    """Route métier dynamique traitée par l'une des 4 instances FastAPI / Uvicorn."""
    x_forwarded_for = request.headers.get("X-Forwarded-For", "appel-direct-sans-nginx")
    ip_reelle = (
        x_forwarded_for.split(",")[0].strip()
        if x_forwarded_for != "appel-direct-sans-nginx"
        else (request.client.host if request.client else "127.0.0.1")
    )
    return {
        "traite_par_instance": {
            "instance_id": INSTANCE_ID,
            "moteur_asgi": "Uvicorn + FastAPI",
            "hote_local": f"127.0.0.1:{PORT}",
            "pid_linux": os.getpid(),
            "hostname": socket.gethostname(),
        },
        "contexte_reverse_proxy_nginx": {
            "ip_client_reelle": ip_reelle,
            "x_forwarded_for": x_forwarded_for,
            "x_forwarded_proto": request.headers.get("X-Forwarded-Proto", "http"),
        },
        "data": [
            {"id": 1, "titre": "Architecture API REST & FastAPI (ASGI)", "salle": "Salle A"},
            {"id": 2, "titre": "Déploiement Nginx Load Balancer (4 instances Uvicorn)", "salle": "Labo Prod"},
        ],
    }


if __name__ == "__main__":
    if "--serve" not in sys.argv:
        with TestClient(app) as c:
            rep = c.get(
                "/api/v1/formations",
                headers={"X-Forwarded-For": "197.204.12.88", "X-Forwarded-Proto": "https"},
            )
            assert rep.status_code == 200
            print("Statut :", rep.status_code)
            print("En-tête X-FastAPI-Instance :", rep.headers.get("X-FastAPI-Instance"))
            print("Payload JSON :", rep.json())
    else:
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=PORT, proxy_headers=True, forwarded_allow_ips="*")
