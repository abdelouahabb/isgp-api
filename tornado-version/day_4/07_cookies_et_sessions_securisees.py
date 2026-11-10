# Fichier : day_4/07_cookies_et_sessions_securisees.py
# Exécution : .venv/bin/python day_4/07_cookies_et_sessions_securisees.py
# Objectif : Maîtriser la gestion et la sécurité des Cookies dans Tornado :
#   1. Cookie standard non signé (self.get_cookie / self.set_cookie) -> Préférences UI uniquement
#   2. Les 3 drapeaux de sécurité obligatoires : httponly=True (anti-XSS), secure=True (HTTPS), samesite="Strict" (anti-CSRF)
#   3. Cookie signé et horodaté nativement par HMAC-SHA256 dans Tornado (self.set_secure_cookie / self.get_secure_cookie avec cookie_secret)
#   4. Révocation propre d'un cookie (self.clear_cookie)

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

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))

# Clé secrète serveur obligatoire pour signer cryptographiquement les cookies via set_secure_cookie()
COOKIE_SECRET = os.environ.get("TORNADO_COOKIE_SECRET", "cle-secrete-hmac-cookies-tornado-isgp-2026")


# 1. CONNEXION : Émettre un cookie signé Tornado (set_secure_cookie) + HttpOnly + SameSite
class CookieLoginHandler(tornado.web.RequestHandler):
    def post(self):
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        identifiant = str(corps.get("identifiant", "stagiaire_isgp")).strip()
        theme_choisi = str(corps.get("theme", "institutionnel")).strip()

        session_payload = json.dumps({"utilisateur": identifiant, "role": "auditeur_securite"})

        # A. Cookie signé et horodaté nativement par Tornado (HMAC-SHA256 avec cookie_secret)
        self.set_secure_cookie(
            name="isgp_session",
            value=session_payload,
            expires_days=1,
            httponly=True,     # Bouclier anti-XSS : inaccessible via document.cookie en JS
            secure=False,      # Mettre True en production (exige HTTPS)
            samesite="Strict", # Bouclier anti-CSRF : jamais envoyé depuis un site externe
            path="/",
        )

        # B. Cookie de préférence visuelle non sensible (lisible par le JS frontal si besoin)
        self.set_cookie("isgp_theme", theme_choisi, expires_days=30, httponly=False, samesite="Lax", path="/")

        self.write({
            "statut": "Authentifié par Cookies sécurisés Tornado (set_secure_cookie)",
            "utilisateur": identifiant,
            "cookies_emis": [
                "isgp_session (Signé HMAC-SHA256 Tornado + HttpOnly + SameSite=Strict)",
                "isgp_theme (Préférence UI)",
            ],
        })


# 2. INSPECTION : Lire et vérifier le cookie signé via self.get_secure_cookie()
class CookieInspectHandler(tornado.web.RequestHandler):
    def get(self):
        # get_secure_cookie vérifie automatiquement la signature HMAC-SHA256 et l'horodatage !
        session_bytes = self.get_secure_cookie("isgp_session", max_age_days=1)
        theme = self.get_cookie("isgp_theme", default="clair")

        if not session_bytes:
            self.set_status(401)
            self.write({"erreur": "Aucun cookie signé valide reçu ou signature falsifiée (401)"})
            return

        session_data = tornado.escape.json_decode(session_bytes)
        self.write({
            "authentifie": True,
            "session_tornado_signee_hmac": session_data,
            "cookie_preference_theme": theme,
            "en_tete_cookie_brut": self.request.headers.get("Cookie", ""),
        })


# 3. PORTAIL WEB TORNADO TEMPLATE PROTÉGÉ PAR LES COOKIES SIGNÉS
class PortailCookiesHtmlHandler(tornado.web.RequestHandler):
    def get(self):
        session_bytes = self.get_secure_cookie("isgp_session", max_age_days=1)
        if not session_bytes:
            self.set_status(401)
            self.write({"erreur": "Session absente"})
            return
        session_data = tornado.escape.json_decode(session_bytes)
        self.render(
            "portail_cookies.html",
            utilisateur=session_data["utilisateur"],
            role=session_data.get("role", "invité"),
            theme=self.get_cookie("isgp_theme", default="institutionnel"),
        )


# 4. DÉCONNEXION : Forcer l'expiration immédiate des cookies (self.clear_cookie)
class CookieLogoutHandler(tornado.web.RequestHandler):
    def post(self):
        self.clear_cookie("isgp_session", path="/")
        self.clear_cookie("isgp_theme", path="/")
        self.write({"statut": "Déconnecté — Cookies révoqués via self.clear_cookie()"})


def make_app():
    return tornado.web.Application(
        [
            (r"/api/auth/cookie-login", CookieLoginHandler),
            (r"/api/auth/cookie-inspect", CookieInspectHandler),
            (r"/portail-cookies", PortailCookiesHtmlHandler),
            (r"/api/auth/cookie-logout", CookieLogoutHandler),
        ],
        template_path=os.path.join(DOSSIER_COURANT, "templates"),
        cookie_secret=COOKIE_SECRET,
    )


async def _demo():
    app = make_app()
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    print("=== 1. CONNEXION (POST /api/auth/cookie-login) -> EN-TÊTES Set-Cookie ===")
    r_login = await client.fetch(
        f"http://127.0.0.1:{port}/api/auth/cookie-login",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"identifiant": "yasmine.merabet", "theme": "sombre"}),
    )
    cookies_recus = []
    for sc in r_login.headers.get_list("Set-Cookie"):
        print("  Set-Cookie :", sc)
        cookies_recus.append(sc.split(";", 1)[0])

    cookie_header = "; ".join(cookies_recus)
    print("\n=== 2. REQUÊTE AUTHENTIFIÉE PAR COOKIE SIGNÉ TORNADO (GET /api/auth/cookie-inspect) ===")
    r_insp = await client.fetch(
        f"http://127.0.0.1:{port}/api/auth/cookie-inspect",
        headers={"Cookie": cookie_header},
    )
    print("  Statut :", r_insp.code, "| JSON :", tornado.escape.json_decode(r_insp.body))

    print("\n=== 3. DÉCONNEXION ET RÉVOCATION (POST /api/auth/cookie-logout) ===")
    r_out = await client.fetch(f"http://127.0.0.1:{port}/api/auth/cookie-logout", method="POST", body=b"")
    print("  Réponse logout :", tornado.escape.json_decode(r_out.body))
    server.stop()


if __name__ == "__main__":
    if "--serve" in sys.argv:
        make_app().listen(8889)
        tornado.ioloop.IOLoop.current().start()
    else:
        asyncio.run(_demo())
