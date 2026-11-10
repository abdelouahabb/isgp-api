# Fichier : day_4/05_cors_webhooks_headers.py
# Exécution : .venv/bin/python day_4/05_cors_webhooks_headers.py
# Objectif : Configurer CORS dans set_default_headers(), limiter la taille maximale du Payload
#            (max_body_size dans HTTPServer) et vérifier la signature HMAC-SHA256 d'un Webhook entrant.

import asyncio
import hashlib
import hmac
import json
import os
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "whsec_isgp_partenaire_2026")
ORIGINES_AUTORISEES = {"http://localhost:3000", "https://portail.isgp.dz"}


# 1. CONFIGURATION CORS STRICTE & EN-TÊTES DE SÉCURITÉ HTTP DANS TORNADO
class SecureCorsBaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        origine = self.request.headers.get("Origin", "")
        if origine in ORIGINES_AUTORISEES:
            self.set_header("Access-Control-Allow-Origin", origine)
            self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
            self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.set_header("X-Content-Type-Options", "nosniff")
        self.set_header("X-Frame-Options", "DENY")
        self.set_header("Cache-Control", "no-store")

    def options(self, *args, **kwargs):
        # Réponse immédiate 204 No Content aux requêtes Preflight CORS du navigateur
        self.set_status(204)
        self.finish()


# 2. RÉCEPTION SÉCURISÉE D'UN WEBHOOK (Vérification HMAC-SHA256 de self.request.body)
class WebhookPaiementHandler(SecureCorsBaseHandler):
    def post(self):
        signature_recue = self.request.headers.get("X-Webhook-Signature", "")
        corps_brut = self.request.body  # Octets exacts reçus sur le socket TCP

        # Calcul de l'empreinte HMAC-SHA256 attendue avec le secret partagé
        signature_calculee = "sha256=" + hmac.new(
            WEBHOOK_SECRET.encode("utf-8"),
            corps_brut,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature_recue, signature_calculee):
            self.set_status(401)
            self.write({"erreur": "Signature Webhook invalide (401 Unauthorized)"})
            return

        evenement = tornado.escape.json_decode(corps_brut or b"{}")
        self.write({"statut": "Webhook authentifié et traité par Tornado", "evenement": evenement})


def make_app():
    return tornado.web.Application([(r"/api/webhooks/paiement", WebhookPaiementHandler)])


async def _demo():
    app = make_app()
    app.settings["log_function"] = lambda h: print(
        f"[IOLOOP TORNADO] HTTP {h.get_status()} | {h.request.method} {h.request.uri} ({h.request.remote_ip}) | {round(1000.0 * h.request.request_time(), 2)} ms"
    )
    bind_port = 0 if os.environ.get("ISGP_WEB_RUNNER") == "1" else int(os.environ.get("PORT", 8889))
    try:
        sockets = tornado.netutil.bind_sockets(bind_port, "127.0.0.1")
    except OSError:
        sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app, max_body_size=1 * 1024 * 1024)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    corps = json.dumps({"evenement": "paiement.reussi", "montant_dzd": 65000}).encode("utf-8")
    sig = "sha256=" + hmac.new(WEBHOOK_SECRET.encode("utf-8"), corps, hashlib.sha256).hexdigest()

    rep = await client.fetch(
        f"http://127.0.0.1:{port}/api/webhooks/paiement",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Origin": "https://portail.isgp.dz",
            "X-Webhook-Signature": sig,
        },
        body=corps,
    )
    print("En-tête CORS :", rep.headers.get("Access-Control-Allow-Origin"))
    print("Réponse JSON :", tornado.escape.json_decode(rep.body))
    if os.environ.get("ISGP_WEB_RUNNER") == "1" or "--once" in sys.argv:
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
