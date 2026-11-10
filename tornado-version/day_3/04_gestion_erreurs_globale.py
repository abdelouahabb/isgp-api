# Fichier : day_3/04_gestion_erreurs_globale.py
# Exécution : .venv/bin/python day_3/04_gestion_erreurs_globale.py
# Objectif : Surcharger write_error(self, status_code, **kwargs) et default_handler_class dans Tornado
#            pour ne JAMAIS renvoyer une page HTML d'erreur par défaut à un client d'API JSON (404, 405, 500).

import asyncio
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web


# 1. CLASSE DE BASE SURCHARGEANT write_error() POUR FORMATER TOUTES LES ERREURS EN JSON
class JsonApiBaseHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        """Remplace la page HTML d'erreur par défaut de Tornado par un objet JSON structuré."""
        self.set_header("Content-Type", "application/json; charset=UTF-8")

        if status_code == 404:
            self.finish({
                "erreur": "Ressource ou route introuvable (404 Not Found)",
                "chemin_demande": self.request.path,
                "methode": self.request.method,
            })
        elif status_code == 405:
            self.finish({
                "erreur": f"La méthode {self.request.method} n'est pas autorisée sur {self.request.path} (405 Method Not Allowed)",
            })
        elif status_code >= 500:
            exc_info = kwargs.get("exc_info")
            if exc_info:
                exc_type, exc_val, _ = exc_info
                print(f"[ERREUR CRITIQUE SERVEUR TORNADO] {exc_type.__name__}: {exc_val}")
            self.finish({
                "erreur": "Erreur interne du serveur (500 Internal Server Error)",
                "conseil": "Veuillez communiquer l'horodatage à l'administrateur.",
            })
        else:
            self.finish({
                "erreur": self._reason,
                "status_code": status_code,
            })


# 2. HANDLER PAR DÉFAUT POUR LES ROUTES INEXISTANTES (default_handler_class -> 404 JSON)
class NotFoundJsonHandler(JsonApiBaseHandler):
    def prepare(self):
        raise tornado.web.HTTPError(404)


class DivisionHandler(JsonApiBaseHandler):
    def get(self):
        a = float(self.get_query_argument("a", "100"))
        b = float(self.get_query_argument("b", "0"))  # Si b=0 -> ZeroDivisionError intercepté par write_error(500) !
        self.write({"resultat": a / b})


def make_app():
    return tornado.web.Application(
        [(r"/api/v1/division", DivisionHandler)],
        default_handler_class=NotFoundJsonHandler,
    )


async def _demo():
    app = make_app()
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    print("=== 1. TEST ROUTE INEXISTANTE (404 via default_handler_class + write_error) ===")
    r404 = await client.fetch(f"http://127.0.0.1:{port}/api/route-inconnue", raise_error=False)
    print("Statut :", r404.code, "| JSON :", tornado.escape.json_decode(r404.body))

    print("\n=== 2. TEST MÉTHODE NON AUTORISÉE (405 Method Not Allowed en JSON) ===")
    r405 = await client.fetch(f"http://127.0.0.1:{port}/api/v1/division", method="DELETE", raise_error=False)
    print("Statut :", r405.code, "| JSON :", tornado.escape.json_decode(r405.body))

    print("\n=== 3. TEST EXCEPTION PYTHON IMPRÉVUE (ZeroDivisionError -> 500 JSON propre) ===")
    r500 = await client.fetch(f"http://127.0.0.1:{port}/api/v1/division?a=100&b=0", raise_error=False)
    print("Statut :", r500.code, "| JSON :", tornado.escape.json_decode(r500.body))
    server.stop()


if __name__ == "__main__":
    if "--serve" in sys.argv:
        make_app().listen(8889)
        tornado.ioloop.IOLoop.current().start()
    else:
        asyncio.run(_demo())
