# Fichier : day_4/04_refresh_token_et_rbac.py
# Exécution : .venv/bin/python day_4/04_refresh_token_et_rbac.py
# Objectif : Implémenter un décorateur @exiger_role sur les méthodes d'un RequestHandler Tornado,
#            le contrôle d'accès par rôle (RBAC : 401 vs 403), et le cycle Access / Refresh Token.

import asyncio
import json
import os
import sys
from functools import wraps
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SECRET_KEY = os.environ.get("API_SECRET_KEY", "secret-signature-isgp-2026")
access_signer = URLSafeTimedSerializer(SECRET_KEY, salt="access-token")
refresh_signer = URLSafeTimedSerializer(SECRET_KEY, salt="refresh-token")

# Liste noire (Blacklist) des jetons révoqués lors d'une déconnexion (Logout)
jetons_revoques = set()


# 1. DÉCORATEUR D'AUTHENTIFICATION ET DE CONTRÔLE DE RÔLE (RBAC) POUR TORNADO REQUESTHANDLER
def exiger_role(role_minimum=None):
    def decorateur(methode_handler):
        @wraps(methode_handler)
        def enveloppe(self, *args, **kwargs):
            auth = self.request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                self.set_status(401)
                self.write({"erreur": "401 Unauthorized : Bearer Token manquant"})
                return

            token = auth.split(" ", 1)[1].strip()
            if token in jetons_revoques:
                self.set_status(401)
                self.write({"erreur": "401 Unauthorized : Ce jeton a été révoqué (déconnecté)"})
                return

            try:
                utilisateur = access_signer.loads(token, max_age=300)
            except SignatureExpired:
                self.set_status(401)
                self.write({"erreur": "401 Unauthorized : Access Token expiré. Utilisez /api/auth/refresh"})
                return
            except BadSignature:
                self.set_status(401)
                self.write({"erreur": "401 Unauthorized : Signature du jeton invalide"})
                return

            # Vérification du Rôle (RBAC) : 403 Forbidden si authentifié mais droits insuffisants !
            if role_minimum and utilisateur.get("role") != role_minimum:
                self.set_status(403)
                self.write({
                    "erreur": f"403 Forbidden : Rôle '{role_minimum}' requis (votre rôle : '{utilisateur.get('role')}')"
                })
                return

            self.current_user = utilisateur
            return methode_handler(self, *args, **kwargs)
        return enveloppe
    return decorateur


# 2. LOGIN : Émet un Access Token (5 min) ET un Refresh Token (7 jours)
class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        identifiant = corps.get("identifiant", "stagiaire")
        role = "admin" if identifiant == "directeur" else "stagiaire"

        payload = {"sub": identifiant, "role": role}
        self.write({
            "access_token": access_signer.dumps(payload),
            "refresh_token": refresh_signer.dumps(payload),
            "token_type": "Bearer",
            "access_expires_in": 300,
            "refresh_expires_in": 604800,
        })


# 3. REFRESH : Échange un Refresh Token valide contre un nouvel Access Token neuf
class RefreshHandler(tornado.web.RequestHandler):
    def post(self):
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        rt = corps.get("refresh_token", "")
        try:
            payload = refresh_signer.loads(rt, max_age=604800)
            nouvel_access = access_signer.dumps(payload)
            self.write({"access_token": nouvel_access, "expires_in": 300})
        except (BadSignature, SignatureExpired):
            self.set_status(401)
            self.write({"erreur": "Refresh Token invalide ou expiré"})


# 4. ROUTE RÉSERVÉE AU RÔLE 'admin' (Démontre 401 vs 403 vs 200)
class AuditAdminHandler(tornado.web.RequestHandler):
    @exiger_role("admin")
    def get(self):
        self.write({"acces": "Autorisé (Admin Tornado)", "operateur": self.current_user["sub"]})


def make_app():
    return tornado.web.Application([
        (r"/api/auth/login", LoginHandler),
        (r"/api/auth/refresh", RefreshHandler),
        (r"/api/admin/audit", AuditAdminHandler),
    ])


async def _demo():
    app = make_app()
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    # Connexion en tant que stagiaire
    r_stag = await client.fetch(
        f"http://127.0.0.1:{port}/api/auth/login",
        method="POST",
        body=json.dumps({"identifiant": "stagiaire"}),
    )
    tok_stag = tornado.escape.json_decode(r_stag.body)["access_token"]

    # Connexion en tant que directeur (admin)
    r_dir = await client.fetch(
        f"http://127.0.0.1:{port}/api/auth/login",
        method="POST",
        body=json.dumps({"identifiant": "directeur"}),
    )
    tok_dir = tornado.escape.json_decode(r_dir.body)["access_token"]

    r_403 = await client.fetch(
        f"http://127.0.0.1:{port}/api/admin/audit",
        headers={"Authorization": f"Bearer {tok_stag}"},
        raise_error=False,
    )
    print("1. Stagiaire sur /api/admin/audit -> HTTP", r_403.code, ":", tornado.escape.json_decode(r_403.body))

    r_200 = await client.fetch(
        f"http://127.0.0.1:{port}/api/admin/audit",
        headers={"Authorization": f"Bearer {tok_dir}"},
    )
    print("2. Directeur sur /api/admin/audit -> HTTP", r_200.code, ":", tornado.escape.json_decode(r_200.body))
    server.stop()


if __name__ == "__main__":
    if "--serve" in sys.argv:
        make_app().listen(8889)
        tornado.ioloop.IOLoop.current().start()
    else:
        asyncio.run(_demo())
