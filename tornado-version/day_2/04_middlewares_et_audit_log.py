# Fichier : day_2/04_middlewares_et_audit_log.py
# Exécution : .venv/bin/python day_2/04_middlewares_et_audit_log.py
# Objectif : Implémenter le cycle de vie d'un RequestHandler Tornado :
#   1. set_default_headers(self) : En-têtes de sécurité appliqués par défaut
#   2. prepare(self)             : S'exécute AVANT get/post/put/delete (chronomètre + X-Request-ID)
#   3. on_finish(self)           : S'exécute APRÈS l'envoi de la réponse (journalisation d'audit)

import asyncio
import sys
import time
import uuid
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web


# CLASSE DE BASE TRANSVERSALE (Équivalent orienté objet des middlewares dans Tornado)
class BaseAuditHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        # 1. En-tête de sécurité systématique contre le reniflage MIME
        self.set_header("X-Content-Type-Options", "nosniff")

    def prepare(self):
        # 2. HOOK AVANT REQUÊTE : Démarre le chronomètre et attribue un X-Request-ID
        self.heure_debut = time.perf_counter()
        self.request_id = self.request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:8]}"
        self.set_header("X-Request-ID", self.request_id)

    def on_finish(self):
        # 3. HOOK APRÈS REQUÊTE : Mesure la durée totale et écrit la trace d'audit
        duree_ms = round((time.perf_counter() - self.heure_debut) * 1000, 2)
        print(
            f"[AUDIT TORNADO] {self.request.method} {self.request.path} "
            f"-> HTTP {self.get_status()} ({duree_ms} ms) [ID: {self.request_id}]"
        )


class StatutHandler(BaseAuditHandler):
    def get(self):
        duree_ms = round((time.perf_counter() - self.heure_debut) * 1000, 2)
        self.set_header("X-Response-Time-Ms", str(duree_ms))
        self.write({
            "service": "ISGP Tornado API Core",
            "request_id": self.request_id,
            "statut": "opérationnel",
        })


def make_app():
    return tornado.web.Application([(r"/api/v1/statut", StatutHandler)])


async def _demo():
    app = make_app()
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    rep = await client.fetch(f"http://127.0.0.1:{port}/api/v1/statut")
    print("En-tête X-Request-ID :", rep.headers.get("X-Request-ID"))
    print("Payload JSON         :", tornado.escape.json_decode(rep.body))
    server.stop()


if __name__ == "__main__":
    if "--serve" in sys.argv:
        make_app().listen(8889)
        tornado.ioloop.IOLoop.current().start()
    else:
        asyncio.run(_demo())
