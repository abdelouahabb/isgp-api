import os
# Fichier : day_4/03_rate_limiting_429.py
# Exécution : .venv/bin/python day_4/03_rate_limiting_429.py
# Objectif : Implémenter un Rate Limiter à fenêtre glissante dans Tornado (429 Too Many Requests)

import asyncio
import sys
import time
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

# Configuration du Rate Limiter : max 3 requêtes par tranche de 20 secondes par IP
LIMITE_REQUETES = 3
FENETRE_SECONDES = 20
historique_ip = {}  # {"127.0.0.1": [timestamp1, timestamp2, ...]}


class CatalogueRateLimitHandler(tornado.web.RequestHandler):
    def get(self):
        ip_client = self.request.remote_ip or "127.0.0.1"
        maintenant = time.time()

        # 1. Conserver uniquement les appels effectués durant les 20 dernières secondes
        appels_recents = [t for t in historique_ip.get(ip_client, []) if maintenant - t < FENETRE_SECONDES]

        # 2. Vérifier si le plafond est atteint
        if len(appels_recents) >= LIMITE_REQUETES:
            attente = int(FENETRE_SECONDES - (maintenant - appels_recents[0])) + 1
            self.set_status(429)
            self.set_header("Retry-After", str(attente))
            self.set_header("X-RateLimit-Limit", str(LIMITE_REQUETES))
            self.set_header("X-RateLimit-Remaining", "0")
            self.write({
                "erreur": "Quota de requêtes dépassé (429 Too Many Requests)",
                "limite": f"{LIMITE_REQUETES} requêtes par {FENETRE_SECONDES} secondes",
                "reessayer_dans_secondes": attente,
            })
            return

        # 3. Enregistrer l'appel actuel et calculer le quota restant
        appels_recents.append(maintenant)
        historique_ip[ip_client] = appels_recents
        restant = LIMITE_REQUETES - len(appels_recents)

        self.set_header("X-RateLimit-Limit", str(LIMITE_REQUETES))
        self.set_header("X-RateLimit-Remaining", str(restant))
        self.write({"message": "Requête acceptée par Tornado", "quota_restant": restant})


def make_app():
    return tornado.web.Application([(r"/api/catalogue-protege", CatalogueRateLimitHandler)])


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

    print("=== RAFALE DE 4 REQUÊTES SUR /api/catalogue-protege (LIMITE = 3) ===")
    for i in range(1, 5):
        r = await client.fetch(f"http://127.0.0.1:{port}/api/catalogue-protege", raise_error=False)
        print(
            f"  Appel #{i} -> HTTP {r.code} | Remaining={r.headers.get('X-RateLimit-Remaining')} "
            f"| Body={tornado.escape.json_decode(r.body)}"
        )
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
