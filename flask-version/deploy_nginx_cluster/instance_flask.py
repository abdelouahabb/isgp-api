"""
Fichier : deploy_nginx_cluster/instance_flask.py
Exécution (4 instances sur 4 ports distincts) :
  PORT=8001 INSTANCE_ID=flask-node-1 .venv/bin/python deploy_nginx_cluster/instance_flask.py
  PORT=8002 INSTANCE_ID=flask-node-2 .venv/bin/python deploy_nginx_cluster/instance_flask.py
  PORT=8003 INSTANCE_ID=flask-node-3 .venv/bin/python deploy_nginx_cluster/instance_flask.py
  PORT=8004 INSTANCE_ID=flask-node-4 .venv/bin/python deploy_nginx_cluster/instance_flask.py
"""

import os
import socket
import time
from flask import Flask, Response, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

PORT = int(os.environ.get("PORT", 8001))
INSTANCE_ID = os.environ.get("INSTANCE_ID", f"flask-node-{PORT}")
DEMARRAGE = time.time()


@app.after_request
def injecter_entetes_noeud(reponse):
    reponse.headers["X-Flask-Instance"] = INSTANCE_ID
    reponse.headers["X-Flask-Port"] = str(PORT)
    reponse.headers["X-Flask-PID"] = str(os.getpid())
    return reponse


@app.route("/api/health", methods=["GET"])
def healthcheck():
    return jsonify({
        "statut": "UP",
        "instance_id": INSTANCE_ID,
        "port": PORT,
        "pid": os.getpid(),
        "uptime_secondes": round(time.time() - DEMARRAGE, 1),
    }), 200


@app.route("/api/v1/formations", methods=["GET"])
def lister_formations():
    return jsonify({
        "traite_par_instance": {
            "instance_id": INSTANCE_ID,
            "hote_local": f"127.0.0.1:{PORT}",
            "pid_linux": os.getpid(),
            "hostname": socket.gethostname(),
        },
        "contexte_reverse_proxy_nginx": {
            "ip_client_reelle": request.remote_addr,
            "x_forwarded_for": request.headers.get("X-Forwarded-For", "appel-direct-sans-nginx"),
            "x_forwarded_proto": request.headers.get("X-Forwarded-Proto", "http"),
            "x_request_id": request.headers.get("X-Request-ID", "local"),
        },
        "data": [
            {"id": 1, "titre": "Architecture API REST & Flask", "salle": "Salle A"},
            {"id": 2, "titre": "Déploiement Nginx Load Balancer & Upload Offload", "salle": "Labo Prod"},
        ],
    }), 200


@app.route("/api/v1/upload-offload", methods=["POST"])
def finaliser_upload_delegue_a_nginx():
    """
    Réception d'un upload délégué à Nginx (client_body_in_file_only + proxy_pass_request_body off) :
    Flask reçoit 0 octet dans request.data ! Nginx a déjà écrit les 20 Mo sur disque et passe le chemin.
    """
    chemin_temp_nginx = request.headers.get("X-Uploaded-File-Path", "")
    octets_declares = int(request.headers.get("X-Uploaded-Bytes", "0") or 0)
    nom_original = os.path.basename(request.headers.get("X-Original-Filename", "document.pdf"))

    if not chemin_temp_nginx:
        return jsonify({"erreur": "En-tête interne X-Uploaded-File-Path absent (route réservée à Nginx)"}), 400

    # Si le fichier temporaire posé par Nginx existe sur disque, on inspecte seulement les 5 premiers octets !
    if os.path.isfile(chemin_temp_nginx):
        with open(chemin_temp_nginx, "rb") as f:
            if not f.read(5).startswith(b"%PDF-"):
                return jsonify({"status": 415, "erreur": "Magic Bytes invalides (attendu %PDF-)"}), 415

    return jsonify({
        "statut": "OFFLOAD_NGINX_VALIDE",
        "instance_id": INSTANCE_ID,
        "octets_lus_par_python_sur_reseau": len(request.get_data()),  # Vaut 0 !
        "octets_ecrits_par_nginx_sur_disque": octets_declares,
        "chemin_spool_nginx": chemin_temp_nginx,
        "nom_assaini": nom_original,
    }), 201


@app.route("/api/v1/exports/<doc_id>", methods=["GET"])
def telecharger_pdf_prive_x_accel(doc_id: str):
    """
    Symétrie inverse en téléchargement : Python vérifie les droits en < 1 ms, puis délègue
    100 % du transfert binaire au noyau Linux via l'en-tête interne Nginx X-Accel-Redirect !
    """
    nom_sain = "".join(c for c in doc_id if c.isalnum() or c in "_-") or "attestation"
    rep = Response(b"", status=200)
    rep.headers["Content-Type"] = "application/pdf"
    rep.headers["Content-Disposition"] = f'attachment; filename="{nom_sain}.pdf"'
    rep.headers["X-Accel-Redirect"] = f"/_protected_exports/{nom_sain}.pdf"
    return rep


if __name__ == "__main__":
    import sys
    with app.test_client() as c:
        rep = c.get("/api/v1/formations", headers={"X-Forwarded-For": "197.204.12.88", "X-Forwarded-Proto": "https"})
        assert rep.status_code == 200
        rep_up = c.post("/api/v1/upload-offload", headers={"X-Uploaded-File-Path": "/var/spool/nginx/0001", "X-Uploaded-Bytes": "18874368"})
        assert rep_up.status_code == 201 and rep_up.get_json()["octets_lus_par_python_sur_reseau"] == 0
        rep_dl = c.get("/api/v1/exports/certificat_2026")
        assert rep_dl.headers.get("X-Accel-Redirect") == "/_protected_exports/certificat_2026.pdf"
        print("[OK] Instance Flask + Offload Nginx + X-Accel-Redirect validés :", INSTANCE_ID)
    if "--once" not in sys.argv:
        print(f"\n[{INSTANCE_ID}] Serveur Flask WSGI actif sur http://127.0.0.1:{PORT} (Ctrl+C pour arrêter)")
        app.run(host="127.0.0.1", port=PORT, debug=False)
