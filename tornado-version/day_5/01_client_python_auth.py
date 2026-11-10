# Fichier : day_5/01_client_python_auth.py
# Exécution : .venv/bin/python day_5/01_client_python_auth.py
# Objectif : Construire un client HTTP asynchrone résilient avec tornado.httpclient.AsyncHTTPClient
#            (connect_timeout, request_timeout, gestion des codes 401/429 et Bearer Token)

import asyncio
import json
import socket
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.netutil
import tornado.web


def _creer_serveur_auth_ephemere():
    """Démarre un serveur Tornado local si le port 8888 n'est pas actif."""
    class TokenHandler(tornado.web.RequestHandler):
        def post(self):
            corps = tornado.escape.json_decode(self.request.body or b"{}")
            self.write({
                "access_token": "eyJ0b3JuYWRvX2NsaWVudCI6dHJ1ZX0.hmac_sha256_isgp",
                "token_type": "Bearer",
                "utilisateur": corps.get("identifiant", "stagiaire"),
            })

    class ProfilHandler(tornado.web.RequestHandler):
        def get(self):
            auth = self.request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                self.set_status(401)
                self.write({"erreur": "Bearer Token requis"})
                return
            self.write({
                "acces": "Autorisé via AsyncHTTPClient Tornado",
                "profil_decode": {"utilisateur": "stagiaire", "role": "stagiaire", "scopes": ["formations:read"]},
            })

    app = tornado.web.Application([
        (r"/api/sandbox/auth/token", TokenHandler),
        (r"/api/sandbox/auth/profil", ProfilHandler),
    ])
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    return server, f"http://127.0.0.1:{port}"


async def appeler_api_tornado(url, method="GET", headers=None, payload=None, timeout=5.0):
    """Client HTTP non-bloquant basé sur tornado.httpclient.AsyncHTTPClient avec Timeouts stricts."""
    client = tornado.httpclient.AsyncHTTPClient()
    entetes = {"Accept": "application/json"}
    if headers:
        entetes.update(headers)
    corps = None
    if payload is not None:
        corps = json.dumps(payload).encode("utf-8")
        entetes["Content-Type"] = "application/json"

    req = tornado.httpclient.HTTPRequest(
        url=url,
        method=method,
        headers=entetes,
        body=corps,
        connect_timeout=2.0,
        request_timeout=timeout,
    )
    # raise_error=False permet d'inspecter proprement les statuts 400/401/403/429 sans lever d'exception
    reponse = await client.fetch(req, raise_error=False)
    return reponse.code, tornado.escape.json_decode(reponse.body or b"{}")


async def _main():
    server = None
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", 8888)) == 0:
            base_url = "http://127.0.0.1:8888"
        else:
            server, base_url = _creer_serveur_auth_ephemere()

    # 1. Authentification initiale pour obtenir le Bearer Token
    statut_login, rep_login = await appeler_api_tornado(
        f"{base_url}/api/sandbox/auth/token",
        method="POST",
        payload={"identifiant": "stagiaire", "mot_de_passe": "isgp2026"},
    )
    mon_token = rep_login["access_token"]
    print(f"1. [HTTP {statut_login}] Jeton Bearer obtenu via AsyncHTTPClient : {mon_token[:32]}...")

    # 2. Appel de la route protégée en injectant l'en-tête Authorization
    statut_profil, rep_profil = await appeler_api_tornado(
        f"{base_url}/api/sandbox/auth/profil",
        headers={"Authorization": f"Bearer {mon_token}"},
    )
    print(f"2. [HTTP {statut_profil}] Profil sécurisé reçu :")
    print(json.dumps(rep_profil, indent=2, ensure_ascii=False))

    if server:
        server.stop()


if __name__ == "__main__":
    asyncio.run(_main())
