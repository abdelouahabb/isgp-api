"""
Fichier : deploy_nginx_cluster/instance_fastapi.py
Exécution (4 instances FastAPI / Uvicorn sur 4 ports distincts) :
  PORT=8001 INSTANCE_ID=fastapi-node-1 .venv/bin/python deploy_nginx_cluster/instance_fastapi.py
"""

import os
import socket
import sys
import time
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.testclient import TestClient

app = FastAPI(title="ISGP — Instance Cluster FastAPI / Uvicorn (ASGI)", version="2.1.0")

PORT = int(os.environ.get("PORT", 8001))
INSTANCE_ID = os.environ.get("INSTANCE_ID", f"fastapi-node-{PORT}")
DEMARRAGE = time.time()


@app.middleware("http")
async def injecter_entetes_noeud(request: Request, call_next):
    reponse = await call_next(request)
    reponse.headers["X-FastAPI-Instance"] = INSTANCE_ID
    reponse.headers["X-FastAPI-Port"] = str(PORT)
    reponse.headers["X-FastAPI-PID"] = str(os.getpid())
    return reponse


@app.get("/api/health", status_code=status.HTTP_200_OK)
def healthcheck():
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
            "x_request_id": request.headers.get("X-Request-ID", "local"),
        },
        "data": [
            {"id": 1, "titre": "Architecture API REST & FastAPI (ASGI)", "salle": "Salle A"},
            {"id": 2, "titre": "Déploiement Nginx Load Balancer & Upload Offload", "salle": "Labo Prod"},
        ],
    }


@app.post("/api/v1/upload-offload", status_code=status.HTTP_201_CREATED)
async def finaliser_upload_delegue_a_nginx(request: Request):
    """Nginx a déjà stocké le fichier sur disque NVMe et transmet uniquement X-Uploaded-File-Path !"""
    chemin_temp_nginx = request.headers.get("X-Uploaded-File-Path", "")
    octets_declares = int(request.headers.get("X-Uploaded-Bytes", "0") or 0)
    nom_original = os.path.basename(request.headers.get("X-Original-Filename", "document.pdf"))
    corps_recu = await request.body()

    if not chemin_temp_nginx:
        raise HTTPException(status_code=400, detail="En-tête interne X-Uploaded-File-Path manquant")
    if os.path.isfile(chemin_temp_nginx):
        with open(chemin_temp_nginx, "rb") as f:
            if not f.read(5).startswith(b"%PDF-"):
                raise HTTPException(status_code=415, detail="Magic Bytes invalides (attendu %PDF-)")

    return {
        "statut": "OFFLOAD_NGINX_VALIDE",
        "instance_id": INSTANCE_ID,
        "octets_lus_par_python_sur_reseau": len(corps_recu),
        "octets_ecrits_par_nginx_sur_disque": octets_declares,
        "chemin_spool_nginx": chemin_temp_nginx,
        "nom_assaini": nom_original,
    }


@app.get("/api/v1/exports/{doc_id}")
async def telecharger_pdf_prive_x_accel(doc_id: str):
    nom_sain = "".join(c for c in doc_id if c.isalnum() or c in "_-") or "attestation"
    return Response(
        content=b"",
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{nom_sain}.pdf"',
            "X-Accel-Redirect": f"/_protected_exports/{nom_sain}.pdf",
        },
    )


if __name__ == "__main__":
    with TestClient(app) as c:
        rep = c.get("/api/v1/formations", headers={"X-Forwarded-For": "197.204.12.88", "X-Forwarded-Proto": "https"})
        assert rep.status_code == 200
        rep_up = c.post("/api/v1/upload-offload", headers={"X-Uploaded-File-Path": "/var/spool/nginx/0001", "X-Uploaded-Bytes": "18874368"})
        assert rep_up.status_code == 201 and rep_up.json()["octets_lus_par_python_sur_reseau"] == 0
        rep_dl = c.get("/api/v1/exports/certificat_2026")
        assert rep_dl.headers.get("X-Accel-Redirect") == "/_protected_exports/certificat_2026.pdf"
        print("[OK] Instance FastAPI + Offload Nginx + X-Accel-Redirect validés :", INSTANCE_ID)
    if "--once" not in sys.argv:
        import uvicorn
        print(f"\n[{INSTANCE_ID}] Serveur Uvicorn ASGI actif sur http://127.0.0.1:{PORT} (Ctrl+C pour arrêter)")
        uvicorn.run(app, host="127.0.0.1", port=PORT, proxy_headers=True, forwarded_allow_ips="*")
