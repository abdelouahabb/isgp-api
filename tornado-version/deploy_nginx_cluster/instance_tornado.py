"""
Fichier : deploy_nginx_cluster/instance_tornado.py (Noeud Tornado HTTPServer)
Exécution (4 instances Tornado non-bloquantes sur 4 ports distincts) :
  PORT=8001 INSTANCE_ID=tornado-node-1 .venv/bin/python deploy_nginx_cluster/instance_tornado.py
  PORT=8002 INSTANCE_ID=tornado-node-2 .venv/bin/python deploy_nginx_cluster/instance_tornado.py
  PORT=8003 INSTANCE_ID=tornado-node-3 .venv/bin/python deploy_nginx_cluster/instance_tornado.py
  PORT=8004 INSTANCE_ID=tornado-node-4 .venv/bin/python deploy_nginx_cluster/instance_tornado.py
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
        """Ajoute l'identifiant de l'instance Tornado dans les en-têtes HTTP pour vérifier le Load Balancing."""
        self.set_header("X-Tornado-Instance", INSTANCE_ID)
        self.set_header("X-Tornado-Port", str(PORT))
        self.set_header("X-Tornado-PID", str(os.getpid()))


class HealthcheckHandler(BaseClusterNodeHandler):
    def get(self):
        """Sonde de santé appelée par Nginx ou l'orchestrateur pour vérifier que l'IOLoop est vivante."""
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
        """Route métier dynamique traitée par l'une des 4 instances Tornado."""
        self.write({
            "traite_par_instance": {
                "instance_id": INSTANCE_ID,
                "hote_local": f"127.0.0.1:{PORT}",
                "pid_linux": os.getpid(),
                "hostname": socket.gethostname(),
            },
            "contexte_reverse_proxy_nginx": {
                # Grâce à HTTPServer(app, xheaders=True), self.request.remote_ip et self.request.protocol
                # reflètent automatiquement X-Forwarded-For et X-Forwarded-Proto transmis par Nginx !
                "ip_client_reelle": self.request.remote_ip,
                "protocole_reel": self.request.protocol,
                "x_forwarded_for": self.request.headers.get("X-Forwarded-For", "appel-direct-sans-nginx"),
                "x_forwarded_proto": self.request.headers.get("X-Forwarded-Proto", "http"),
            },
            "data": [
                {"id": 1, "titre": "Architecture API REST & Tornado IOLoop", "salle": "Salle A"},
                {"id": 2, "titre": "Déploiement Nginx Load Balancer (4 instances Tornado)", "salle": "Labo Prod"},
            ],
        })


def make_app():
    return tornado.web.Application([
        (r"/api/health", HealthcheckHandler),
        (r"/api/v1/formations", FormationsClusterHandler),
    ])


async def _test_in_memory():
    app = make_app()
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    ephemeral_port = sockets[0].getsockname()[1]
    # CRITIQUE DERRIÈRE NGINX : xheaders=True permet à Tornado HTTPServer de lire X-Forwarded-For et X-Forwarded-Proto
    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()
    rep = await client.fetch(
        f"http://127.0.0.1:{ephemeral_port}/api/v1/formations",
        headers={"X-Forwarded-For": "197.204.12.88", "X-Forwarded-Proto": "https"},
    )
    print("Statut :", rep.code)
    print("En-tête X-Tornado-Instance :", rep.headers.get("X-Tornado-Instance"))
    print("Payload JSON :", tornado.escape.json_decode(rep.body))
    server.stop()


if __name__ == "__main__":
    if "--test" in sys.argv:
        asyncio.run(_test_in_memory())
    else:
        server = tornado.httpserver.HTTPServer(make_app(), xheaders=True)
        server.listen(PORT, address="127.0.0.1")
        print(f"[{INSTANCE_ID}] Tornado HTTPServer (xheaders=True) actif sur http://127.0.0.1:{PORT}")
        tornado.ioloop.IOLoop.current().start()
