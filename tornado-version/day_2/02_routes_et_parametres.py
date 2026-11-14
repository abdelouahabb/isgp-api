# Fichier : day_2/02_routes_et_parametres.py
# Exécution : .venv/bin/python day_2/02_routes_et_parametres.py
# Objectif : Maîtriser le routage par Expressions Régulières (Regex) de Tornado :
#   - Groupes capturants r"/api/saluer/([^/]+)" et r"/api/v1/stagiaires/([0-9]+)"
#   - Différence avec <variable> (Flask), :variable (Postman/Express) et {variable} (OpenAPI/FastAPI)
#   - Lecture des Query Parameters (?ht=2500&taux=19 via self.get_query_argument)

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

STAGIAIRES = {
    1: {"id": 1, "prenom": "Yasmine", "nom": "Merabet", "specialite": "Architecture API & Sécurité"},
    2: {"id": 2, "prenom": "Amine", "nom": "Benali", "specialite": "Python, Tornado & Bases SQL"},
}


# 1. GROUPE CAPTURANT REGEX TEXTE r"/api/saluer/([^/]+)" :
#    Tornado transmet chaque parenthèse capturante en argument positionnel de get(self, prenom) !
class SaluerStagiaireHandler(tornado.web.RequestHandler):
    def get(self, prenom):
        self.write({
            "message": f"Bienvenue au séminaire API Tornado, {prenom}",
            "longueur_chaine": len(prenom),
            "syntaxe_route_tornado": r"/api/saluer/([^/]+)",
            "equivalent_flask": "/api/saluer/<prenom>",
            "equivalent_postman_express": "/api/saluer/:prenom",
            "equivalent_openapi_fastapi": "/api/saluer/{prenom}",
        })


# 2. GROUPE REGEX ENTIER r"/api/v1/stagiaires/([0-9]+)" : Rejette tout texte non numérique en 404
class StagiaireJsonHandler(tornado.web.RequestHandler):
    def get(self, stagiaire_id_str):
        stagiaire_id = int(stagiaire_id_str)
        stagiaire = STAGIAIRES.get(stagiaire_id)
        if not stagiaire:
            self.set_status(404)
            self.write({"erreur": f"Stagiaire #{stagiaire_id} introuvable"})
            return
        self.write({"data": stagiaire})


# 3. ROUTE WEB DYNAMIQUE TORNADO TEMPLATE : Injecte le stagiaire dans day_2/templates/fiche_stagiaire.html
class FicheStagiaireHtmlHandler(tornado.web.RequestHandler):
    def get(self, stagiaire_id_str):
        stagiaire_id = int(stagiaire_id_str)
        stagiaire = STAGIAIRES.get(stagiaire_id)
        if not stagiaire:
            self.set_status(404)
            self.write({"erreur": f"Stagiaire #{stagiaire_id} introuvable"})
            return
        self.render("fiche_stagiaire.html", stagiaire=stagiaire)


# 4. PARAMÈTRES DE REQUÊTE APRÈS '?' (Query String lue via self.get_query_argument)
class CalculTvaHandler(tornado.web.RequestHandler):
    def get(self):
        prix_ht = float(self.get_query_argument("ht", "1000.0"))
        taux = float(self.get_query_argument("taux", "19.0"))
        montant_tva = prix_ht * (taux / 100.0)
        self.write({
            "prix_ht": prix_ht,
            "taux_tva": taux,
            "montant_tva": round(montant_tva, 2),
            "prix_ttc": round(prix_ht + montant_tva, 2),
        })


class PortailRoutesHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("portail_d2_02.html")


def make_app():
    return tornado.web.Application(
        [
            (r"/", PortailRoutesHandler),
            (r"/api/saluer/([^/]+)", SaluerStagiaireHandler),
            (r"/api/v1/stagiaires/([0-9]+)", StagiaireJsonHandler),
            (r"/stagiaires/([0-9]+)/fiche", FicheStagiaireHtmlHandler),
            (r"/api/calcul-tva", CalculTvaHandler),
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

    print("=== 1. TEST PARAMÈTRE DE CHEMIN REGEX r'/api/saluer/([^/]+)' ===")
    r1 = await client.fetch(f"http://127.0.0.1:{port}/api/saluer/Yasmine")
    print(tornado.escape.json_decode(r1.body))

    print("\n=== 2. TEST GROUPE REGEX ([0-9]+) + RENDU TORNADO TEMPLATE ===")
    r2 = await client.fetch(f"http://127.0.0.1:{port}/stagiaires/1/fiche")
    print(r2.body.decode("utf-8").strip())

    print("\n=== 3. TEST QUERY PARAMETERS (?ht=2500&taux=19 via self.get_query_argument) ===")
    r3 = await client.fetch(f"http://127.0.0.1:{port}/api/calcul-tva?ht=2500&taux=19")
    print(tornado.escape.json_decode(r3.body))
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
