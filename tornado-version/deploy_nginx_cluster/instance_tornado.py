"""
Fichier : deploy_nginx_cluster/instance_tornado.py (Noeud Tornado HTTPServer)
Exécution (4 instances Tornado non-bloquantes sur 4 ports distincts) :
  PORT=8001 INSTANCE_ID=tornado-node-1 .venv/bin/python deploy_nginx_cluster/instance_tornado.py
"""

import asyncio
import os
import socket
import sys
import time
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

PORT = int(os.environ.get("PORT", 8001))
INSTANCE_ID = os.environ.get("INSTANCE_ID", f"tornado-node-{PORT}")
DEMARRAGE = time.time()


class BaseClusterNodeHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("X-Tornado-Instance", INSTANCE_ID)
        self.set_header("X-Tornado-Port", str(PORT))
        self.set_header("X-Tornado-PID", str(os.getpid()))


class HealthcheckHandler(BaseClusterNodeHandler):
    def get(self):
        self.write({
            "statut": "UP",
            "moteur": "Tornado Non-Blocking HTTPServer",
            "instance_id": INSTANCE_ID,
            "port": PORT,
            "pid": os.getpid(),
            "uptime_secondes": round(time.time() - DEMARRAGE, 1),
        })


class FormationsClusterHandler(BaseClusterNodeHandler):
    def get(self):
        self.write({
            "traite_par_instance": {
                "instance_id": INSTANCE_ID,
                "hote_local": f"127.0.0.1:{PORT}",
                "pid_linux": os.getpid(),
                "hostname": socket.gethostname(),
            },
            "contexte_reverse_proxy_nginx": {
                "ip_client_reelle": self.request.remote_ip,
                "protocole_reel": self.request.protocol,
                "x_forwarded_for": self.request.headers.get("X-Forwarded-For", "appel-direct-sans-nginx"),
                "x_forwarded_proto": self.request.headers.get("X-Forwarded-Proto", "http"),
                "x_request_id": self.request.headers.get("X-Request-ID", "local"),
            },
            "data": [
                {"id": 1, "titre": "Architecture API REST & Tornado IOLoop", "salle": "Salle A"},
                {"id": 2, "titre": "Déploiement Nginx Load Balancer & Upload Offload", "salle": "Labo Prod"},
            ],
        })


class NginxUploadOffloadHandler(BaseClusterNodeHandler):
    def post(self):
        chemin_temp_nginx = self.request.headers.get("X-Uploaded-File-Path", "")
        octets_declares = int(self.request.headers.get("X-Uploaded-Bytes", "0") or 0)
        nom_original = os.path.basename(self.request.headers.get("X-Original-Filename", "document.pdf"))
        if not chemin_temp_nginx:
            self.set_status(400)
            return self.write({"erreur": "En-tête interne X-Uploaded-File-Path manquant"})
        if os.path.isfile(chemin_temp_nginx):
            with open(chemin_temp_nginx, "rb") as f:
                if not f.read(5).startswith(b"%PDF-"):
                    self.set_status(415)
                    return self.write({"status": 415, "erreur": "Magic Bytes invalides"})
        self.set_status(201)
        self.write({
            "statut": "OFFLOAD_NGINX_VALIDE",
            "instance_id": INSTANCE_ID,
            "octets_lus_par_python_sur_reseau": len(self.request.body),
            "octets_ecrits_par_nginx_sur_disque": octets_declares,
            "chemin_spool_nginx": chemin_temp_nginx,
            "nom_assaini": nom_original,
        })


class ProtectedExportXAccelHandler(BaseClusterNodeHandler):
    def get(self, doc_id: str):
        nom_sain = "".join(c for c in doc_id if c.isalnum() or c in "_-") or "attestation"
        self.set_header("Content-Type", "application/pdf")
        self.set_header("Content-Disposition", f'attachment; filename="{nom_sain}.pdf"')
        self.set_header("X-Accel-Redirect", f"/_protected_exports/{nom_sain}.pdf")
        self.finish()


def make_app():
    return tornado.web.Application([
        (r"/api/health", HealthcheckHandler),
        (r"/api/v1/formations", FormationsClusterHandler),
        (r"/api/v1/upload-offload", NginxUploadOffloadHandler),
        (r"/api/v1/exports/([a-zA-Z0-9_-]+)", ProtectedExportXAccelHandler),
    ])


async def _run_node():
    app = make_app()
    bind_port = PORT
    try:
        sockets = tornado.netutil.bind_sockets(bind_port, "127.0.0.1")
    except OSError:
        sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    active_port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    rep = await client.fetch(
        f"http://127.0.0.1:{active_port}/api/v1/formations",
        headers={"X-Forwarded-For": "197.204.12.88", "X-Forwarded-Proto": "https"},
    )
    assert rep.code == 200
    rep_up = await client.fetch(
        f"http://127.0.0.1:{active_port}/api/v1/upload-offload",
        method="POST",
        body=b"",
        headers={"X-Uploaded-File-Path": "/var/spool/nginx/0001", "X-Uploaded-Bytes": "18874368"},
    )
    assert rep_up.code == 201 and tornado.escape.json_decode(rep_up.body)["octets_lus_par_python_sur_reseau"] == 0
    rep_dl = await client.fetch(f"http://127.0.0.1:{active_port}/api/v1/exports/certificat_2026")
    assert rep_dl.headers.get("X-Accel-Redirect") == "/_protected_exports/certificat_2026.pdf"
    print("[OK] Instance Tornado + Offload Nginx + X-Accel-Redirect validés :", INSTANCE_ID)

    if "--once" in sys.argv:
        server.stop()
    else:
        print(f"\n[{INSTANCE_ID}] Boucle IOLoop Tornado (xheaders=True) active sur http://127.0.0.1:{active_port} (Ctrl+C pour arrêter)")
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(_run_node())
    except KeyboardInterrupt:
        print("\n[IOLOOP TORNADO] Arrêt propre demandé par l'utilisateur (Ctrl+C).")
