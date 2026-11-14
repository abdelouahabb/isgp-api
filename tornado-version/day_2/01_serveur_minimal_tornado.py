# Fichier : day_2/01_serveur_minimal_tornado.py
# Exécution : .venv/bin/python day_2/01_serveur_minimal_tornado.py
# Objectif : Comprendre comment Tornado (tornado.web.Application & RequestHandler) sert à la fois :
#   1. Des pages Web HTML via tornado.template (self.render -> day_2/templates/accueil.html)
#   2. Des routes d'API RESTful normalisées en JSON (self.write(dict) -> /api/v1/...)

import asyncio
import os
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))

MODULES_BOOTCAMP = [
    "Jour 1 : Architecture Web, HTTP/1.1, JSON & curl",
    "Jour 2 : Tornado IOLoop, RequestHandler, Templates & Formulaires HTML",
    "Jour 3 : Ingénierie CRUD, Validation RFC 7807 & SQLite ACID",
    "Jour 4 : Sécurité API (AuthN 401, AuthZ 403, Cookies Signés HMAC, Rate Limiting 429)",
    "Jour 5 : AsyncHTTPClient, Modularité, Tests & Swagger OpenAPI 3.0",
]


# 1. HANDLER WEB HTML : Rendu via tornado.template (day_2/templates/accueil.html)
#    Zéro HTML écrit en dur dans le code Python !
class AccueilHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "accueil.html",
            organisme="ISGP",
            intitule="Développement d'APIs et services web (Tornado)",
            version_api="v1.0",
            modules=MODULES_BOOTCAMP,
        )


# 2. HANDLER API REST : self.write(dict) sérialise automatiquement en JSON (200 OK)
class BonjourApiHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({
            "message": "Service Tornado IOLoop opérationnel",
            "organisme": "ISGP",
            "statut": "actif",
            "version": "v1.0",
        })


# 3. COLLECTION RESTFUL (Niveau 2 de Richardson : nom au pluriel + versioning /api/v1)
class ModulesCollectionHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({
            "total": len(MODULES_BOOTCAMP),
            "data": MODULES_BOOTCAMP,
        })


class PortailMinimalHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("portail_d2_01.html", modules=MODULES_BOOTCAMP)


def make_app():
    return tornado.web.Application(
        [
            (r"/", PortailMinimalHandler),
            (r"/accueil", AccueilHandler),
            (r"/api/bonjour", BonjourApiHandler),
            (r"/api/v1/modules", ModulesCollectionHandler),
        ],
        template_path=os.path.join(DOSSIER_COURANT, "templates"),
    )


async def _demo():
    app = make_app()
    app.settings["log_function"] = lambda h: print(
        f"[IOLOOP TORNADO] HTTP {h.get_status()} | {h.request.method} {h.request.uri} ({h.request.remote_ip}) | {round(1000.0 * h.request.request_time(), 2)} ms"
    )
    bind_port = int(os.environ.get("PORT", 8889))
    try:
        sockets = tornado.netutil.bind_sockets(bind_port, "127.0.0.1")
    except OSError:
        sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    rep_html = await client.fetch(f"http://127.0.0.1:{port}/accueil")
    print("=== 1. RENDU DU TEMPLATE TORNADO (GET /accueil -> day_2/templates/accueil.html) ===")
    print(rep_html.body.decode("utf-8").strip())

    rep_json = await client.fetch(f"http://127.0.0.1:{port}/api/bonjour")
    print("\n=== 2. RÉPONSE API JSON (GET /api/bonjour -> self.write(dict)) ===")
    print("Statut HTTP :", rep_json.code, "| Content-Type :", rep_json.headers["Content-Type"])
    print("Payload JSON :", tornado.escape.json_decode(rep_json.body))
    if "--once" in sys.argv:
        server.stop()
    else:
        print("\n" + "=" * 76)
        print(f"[BOUCLE IOLOOP TORNADO ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print("  -> La boucle d'événements IOLoop reste ouverte en mode interactif !")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print(f"  -> Testez les routes en direct : http://127.0.0.1:{port} (navigateur, curl, Postman)")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement la boucle IOLoop.")
        print("=" * 76)
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(_demo())
    except KeyboardInterrupt:
        print("\n[IOLOOP TORNADO] Arrêt propre demandé par l'utilisateur (Ctrl+C).")
