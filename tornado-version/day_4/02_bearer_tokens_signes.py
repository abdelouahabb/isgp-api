# Fichier : day_4/02_bearer_tokens_signes.py
# Exécution : .venv/bin/python day_4/02_bearer_tokens_signes.py
# Objectif : Émission et vérification de Bearer Tokens signés par HMAC dans Tornado

import asyncio
import json
import os
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SECRET_KEY = os.environ.get("API_SECRET_KEY", "secret-signature-isgp-2026")
signer = URLSafeTimedSerializer(SECRET_KEY)


# 1. HANDLER DE CONNEXION : Émission du Bearer Token signé
class AuthTokenHandler(tornado.web.RequestHandler):
    def post(self):
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        if corps.get("identifiant") != "stagiaire" or corps.get("mot_de_passe") != "isgp2026":
            self.set_status(401)
            self.write({"erreur": "Identifiants invalides"})
            return

        charge_utile = {"utilisateur": corps["identifiant"], "role": "participant_isgp"}
        token = signer.dumps(charge_utile)
        self.write({
            "access_token": token,
            "token_type": "Bearer",
            "expires_in_seconds": 300,
        })


# 2. HANDLER PROTÉGÉ : Vérification de la signature et de l'expiration du Token
class ProfilProtegeHandler(tornado.web.RequestHandler):
    def get(self):
        entete_auth = self.request.headers.get("Authorization", "")
        if not entete_auth.startswith("Bearer "):
            self.set_status(401)
            self.write({"erreur": "En-tête 'Authorization: Bearer <token>' requis"})
            return

        token = entete_auth.split(" ", 1)[1].strip()
        try:
            donnees_utilisateur = signer.loads(token, max_age=300)  # Expire après 300s (5 min)
            self.write({"acces": "Token vérifié par Tornado", "profil": donnees_utilisateur})
        except SignatureExpired:
            self.set_status(401)
            self.write({"erreur": "Le jeton (Token) a expiré"})
        except BadSignature:
            self.set_status(401)
            self.write({"erreur": "Signature du jeton invalide (jeton falsifié)"})


def make_app():
    return tornado.web.Application([
        (r"/api/auth/token", AuthTokenHandler),
        (r"/api/auth/profil", ProfilProtegeHandler),
    ])


async def _demo():
    app = make_app()
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    print("=== 1. ÉMISSION DU BEARER TOKEN (POST /api/auth/token) ===")
    r_tok = await client.fetch(
        f"http://127.0.0.1:{port}/api/auth/token",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}),
    )
    data_tok = tornado.escape.json_decode(r_tok.body)
    token = data_tok["access_token"]
    print("Token émis :", token[:36] + "...")

    print("\n=== 2. ACCÈS À LA ROUTE PROTÉGÉE (GET /api/auth/profil) ===")
    r_prof = await client.fetch(
        f"http://127.0.0.1:{port}/api/auth/profil",
        headers={"Authorization": f"Bearer {token}"},
    )
    print("Profil décodé :", tornado.escape.json_decode(r_prof.body))
    server.stop()


if __name__ == "__main__":
    if "--serve" in sys.argv:
        make_app().listen(8889)
        tornado.ioloop.IOLoop.current().start()
    else:
        asyncio.run(_demo())
