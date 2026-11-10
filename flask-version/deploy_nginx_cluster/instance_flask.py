"""
Fichier : deploy_nginx_cluster/instance_flask.py
Exécution (4 instances sur 4 ports distincts) :
  PORT=8001 INSTANCE_ID=flask-node-1 .venv/bin/python deploy_nginx_cluster/instance_flask.py
  PORT=8002 INSTANCE_ID=flask-node-2 .venv/bin/python deploy_nginx_cluster/instance_flask.py
  PORT=8003 INSTANCE_ID=flask-node-3 .venv/bin/python deploy_nginx_cluster/instance_flask.py
  PORT=8004 INSTANCE_ID=flask-node-4 .venv/bin/python deploy_nginx_cluster/instance_flask.py

Ou en production avec Gunicorn :
  INSTANCE_ID=flask-node-1 gunicorn -w 2 -b 127.0.0.1:8001 deploy_nginx_cluster.instance_flask:app
"""

import os
import socket
import time
from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# CRITIQUE DERRIÈRE NGINX : ProxyFix permet à Flask de lire la véritable adresse IP du client
# transmise par Nginx dans 'X-Forwarded-For' et le vrai protocole HTTPS dans 'X-Forwarded-Proto'
# (sinon request.remote_addr vaudrait toujours '127.0.0.1', l'adresse locale de Nginx !).
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

PORT = int(os.environ.get("PORT", 8001))
INSTANCE_ID = os.environ.get("INSTANCE_ID", f"flask-node-{PORT}")
DEMARRAGE = time.time()


@app.after_request
def injecter_entetes_noeud(reponse):
    """Ajoute l'identifiant de l'instance Flask dans les en-têtes HTTP pour vérifier le Load Balancing."""
    reponse.headers["X-Flask-Instance"] = INSTANCE_ID
    reponse.headers["X-Flask-Port"] = str(PORT)
    reponse.headers["X-Flask-PID"] = str(os.getpid())
    return reponse


@app.route("/api/health", methods=["GET"])
def healthcheck():
    """Sonde de santé appelée par Nginx ou l'orchestrateur pour vérifier que l'instance est vivante."""
    return jsonify({
        "statut": "UP",
        "instance_id": INSTANCE_ID,
        "port": PORT,
        "pid": os.getpid(),
        "uptime_secondes": round(time.time() - DEMARRAGE, 1),
    }), 200


@app.route("/api/v1/formations", methods=["GET"])
def lister_formations():
    """Route métier dynamique traitée par l'une des 4 instances Flask."""
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
        },
        "data": [
            {"id": 1, "titre": "Architecture API REST & Flask", "salle": "Salle A"},
            {"id": 2, "titre": "Déploiement Nginx Load Balancer (4 instances)", "salle": "Labo Prod"},
        ],
    }), 200


if __name__ == "__main__":
    import sys
    with app.test_client() as c:
        rep = c.get("/api/v1/formations", headers={"X-Forwarded-For": "197.204.12.88", "X-Forwarded-Proto": "https"})
        print("Statut :", rep.status_code)
        print("En-tête X-Flask-Instance :", rep.headers.get("X-Flask-Instance"))
        print("Payload JSON :", rep.get_json())
    if os.environ.get("ISGP_WEB_RUNNER") != "1" and "--once" not in sys.argv:
        print(f"\n[{INSTANCE_ID}] Serveur Flask WSGI actif sur http://127.0.0.1:{PORT} (Ctrl+C pour arrêter)")
        app.run(host="127.0.0.1", port=PORT, debug=False)
