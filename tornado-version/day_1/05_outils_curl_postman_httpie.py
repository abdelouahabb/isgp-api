# Fichier : day_1/05_outils_curl_postman_httpie.py
# Exécution : .venv/bin/python day_1/05_outils_curl_postman_httpie.py
# Objectif : Comprendre et exécuter de vraies commandes 'curl' contre un serveur Tornado :
#   1. Les requêtes GET avec Query Parameters (?page=1&limit=2 -> self.get_query_argument)
#   2. Les en-têtes d'authentification (-H 'X-API-Key: ...' -> self.request.headers.get)
#   3. L'envoi d'un Payload JSON (-H 'Content-Type: application/json' -d '{...}' -> json_decode(self.request.body))
#   4. L'envoi d'un Formulaire HTML (-d 'cle=valeur' -> self.get_body_argument)

import socket
import subprocess
import threading
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web


def _demarrer_serveur_tornado_demo():
    """Démarre un mini-serveur Tornado en tâche de fond si le port 8888 n'est pas déjà ouvert."""
    class DemoFormationsHandler(tornado.web.RequestHandler):
        def get(self):
            page = int(self.get_query_argument("page", "1"))
            limit = int(self.get_query_argument("limit", "2"))
            self.write({"meta": {"page": page, "limit": limit}, "formations": [{"id": 1, "titre": "API Tornado"}]})

    class DemoAdminStatsHandler(tornado.web.RequestHandler):
        def get(self):
            if self.request.headers.get("X-API-Key") != "isgp-secret-2026":
                self.set_status(401)
                self.write({"erreur": "X-API-Key invalide"})
                return
            self.write({"acces": "Autorisé via X-API-Key (Tornado)", "stagiaires_certifies": 148})

    class DemoTokenHandler(tornado.web.RequestHandler):
        def post(self):
            corps = tornado.escape.json_decode(self.request.body or b"{}")
            self.write({"access_token": "eyJ0b3JuYWRvIjp0cnVlfQ.signature_hmac", "utilisateur": corps.get("identifiant")})

    class DemoFormHandler(tornado.web.RequestHandler):
        def post(self):
            titre = self.get_body_argument("titre", "")
            salle = self.get_body_argument("salle", "Salle A")
            self.set_status(201)
            self.write({"message": "Formulaire reçu par Tornado via self.get_body_argument", "titre": titre, "salle": salle})

    app = tornado.web.Application([
        (r"/api/sandbox/formations", DemoFormationsHandler),
        (r"/api/sandbox/admin-stats", DemoAdminStatsHandler),
        (r"/api/sandbox/auth/token", DemoTokenHandler),
        (r"/api/sandbox/formulaire-formation", DemoFormHandler),
    ])
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]

    def _run():
        loop = tornado.ioloop.IOLoop(make_current=True)
        server = tornado.httpserver.HTTPServer(app)
        server.add_sockets(sockets)
        loop.start()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return f"http://127.0.0.1:{port}"


def _obtenir_base_url():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", 8888)) == 0:
            return "http://127.0.0.1:8888"
    return _demarrer_serveur_tornado_demo()


BASE_URL = _obtenir_base_url()


def executer_commande_curl(titre, arguments_curl):
    print("=" * 74)
    print(f"TEST : {titre}")
    print("COMMANDE : " + " ".join(arguments_curl))
    print("-" * 74)
    resultat = subprocess.run(
        arguments_curl, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5
    )
    lignes = [
        l for l in resultat.stdout.splitlines()
        if not l.startswith("X-Flask-Handler-Code:") and not l.startswith("X-Flask-Trace-Steps:")
    ]
    print("\n".join(lignes).strip())
    print()


# 1. Requête GET avec '-i' (inclut la Status Line et les Headers HTTP de réponse)
executer_commande_curl(
    "1. GET avec inspection des en-têtes (-i) et paramètres d'URL (self.get_query_argument)",
    ["curl", "-s", "-i", f"{BASE_URL}/api/sandbox/formations?page=1&limit=2"],
)

# 2. Requête Authentifiée par Clé API (-H 'X-API-Key: ...')
executer_commande_curl(
    "2. GET protégé par en-tête de sécurité (-H 'X-API-Key: isgp-secret-2026')",
    ["curl", "-s", "-i", "-H", "X-API-Key: isgp-secret-2026", f"{BASE_URL}/api/sandbox/admin-stats"],
)

# 3. Requête POST envoyant un Payload JSON (-X POST -H 'Content-Type: application/json' -d '{...}')
executer_commande_curl(
    "3. POST envoyant un corps JSON (lu par tornado.escape.json_decode(self.request.body))",
    [
        "curl", "-s", "-i",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", '{"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}',
        f"{BASE_URL}/api/sandbox/auth/token",
    ],
)

# 4. Requête POST envoyant des données de Formulaire HTML (-d 'cle=valeur' -> application/x-www-form-urlencoded)
executer_commande_curl(
    "4. POST simulant un Formulaire HTML <form> (lu par self.get_body_argument côté Tornado)",
    [
        "curl", "-s", "-i",
        "-X", "POST",
        "-d", "titre=Atelier+Curl+Tornado&formateur=ISGP&duree_jours=3&salle=Salle+B",
        f"{BASE_URL}/api/sandbox/formulaire-formation",
    ],
)
