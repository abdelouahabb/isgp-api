# Fichier : day_4/01_secrets_et_api_key.py
# Exécution : .venv/bin/python day_4/01_secrets_et_api_key.py
# Objectif : Authentification Machine-à-Machine par en-tête X-API-Key dans Tornado
#            avec os.environ et comparaison en temps constant hmac.compare_digest

import asyncio
import hmac
import os
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

# 1. Lecture des secrets depuis les variables d'environnement du système
API_SECRET_KEY = os.environ.get("API_SECRET_KEY", "cle-signature-interne-isgp-2026")
PARTNER_API_KEY = os.environ.get("PARTNER_API_KEY", "isgp-secret-2026")


class StatsConfidentiellesHandler(tornado.web.RequestHandler):
    def get(self):
        # 2. Lecture de la clé transmise dans l'en-tête HTTP X-API-Key
        cle_recue = self.request.headers.get("X-API-Key", "")

        # 3. Comparaison en temps constant (protège contre les attaques temporelles / Timing Attacks)
        if not hmac.compare_digest(cle_recue, PARTNER_API_KEY):
            self.set_status(401)
            self.write({
                "erreur": "Accès non autorisé (401). En-tête X-API-Key manquant ou invalide."
            })
            return

        self.write({
            "acces": "Autorisé via X-API-Key (Tornado RequestHandler)",
            "stagiaires_certifies": 148,
        })


def make_app():
    return tornado.web.Application([(r"/api/admin/statistiques", StatsConfidentiellesHandler)])


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

    print("=== 1. APPEL SANS CLÉ X-API-KEY (401 Unauthorized) ===")
    r1 = await client.fetch(f"http://127.0.0.1:{port}/api/admin/statistiques", raise_error=False)
    print("Statut :", r1.code, "| JSON :", tornado.escape.json_decode(r1.body))

    print("\n=== 2. APPEL AVEC CLÉ X-API-KEY VALIDE (200 OK) ===")
    r2 = await client.fetch(
        f"http://127.0.0.1:{port}/api/admin/statistiques",
        headers={"X-API-Key": "isgp-secret-2026"},
    )
    print("Statut :", r2.code, "| JSON :", tornado.escape.json_decode(r2.body))
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
