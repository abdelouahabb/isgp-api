# Fichier : day_5/03_architecture_blueprints.py
# Exécution : .venv/bin/python day_5/03_architecture_blueprints.py
# Objectif : Structurer une API Tornado modulaire (tables de routes par domaine) et comprendre le Versioning (/api/v1 vs /api/v2) :
#   1. Module Web tornado.template (/portail -> day_5/templates/portail_blueprint.html)
#   2. Module API v1 (/api/v1/formations) : Schéma plat historique + En-têtes de Dépréciation (RFC 8594)
#   3. Module API v2 (/api/v2/formations) : Nouveau schéma avec Rupture de Contrat (Breaking Change)
#   4. Module Supervision (/api/health/live & /api/health/ready) + Application Factory (make_app)

import asyncio
import os
import sys
import time
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DEMARRAGE_SERVEUR = time.time()

# SOURCE DE DONNÉES MÉTIER PARTAGÉE ENTRE v1, v2 ET LE PORTAIL WEB
CATALOGUE_METIER = [
    {"id": 1, "code": "ISGP-API-101", "titre": "Architecture API REST & Tornado", "jours": 5, "tarif_dzd": 65000},
    {"id": 2, "code": "ISGP-WEB-202", "titre": "Templates Tornado & Formulaires", "jours": 3, "tarif_dzd": 45000},
    {"id": 3, "code": "ISGP-SEC-303", "titre": "Sécurité JWT, OAuth2 & WAF", "jours": 4, "tarif_dzd": 60000},
]


# 1. MODULE WEB (tornado.template) : Sert les pages HTML depuis day_5/templates/
class PortailWebHandler(tornado.web.RequestHandler):
    def get(self):
        titres = [f["titre"] for f in CATALOGUE_METIER]
        self.render(
            "portail_blueprint.html",
            titre="Portail des Formations ISGP (Module Web Tornado)",
            items=titres,
        )


WEB_ROUTES = [(r"/portail", PortailWebHandler)]


# 2. MODULE API v1 (/api/v1/formations) : Contrat historique maintenu pour les anciens clients
class FormationsV1Handler(tornado.web.RequestHandler):
    def set_default_headers(self):
        # Norme IETF RFC 8594 : Avertit les clients que v1 reste active mais sera éteinte à une date précise
        self.set_header("X-API-Version", "1.0")
        self.set_header("Deprecation", "true")
        self.set_header("Sunset", "Thu, 31 Dec 2026 23:59:59 GMT")
        self.set_header("Link", '</api/v2/formations>; rel="successor-version"')

    def get(self):
        # Schéma v1 (Historique) : "intitule" (str) et "duree" (int)
        format_v1 = [
            {"id": f["id"], "intitule": f["titre"], "duree": f["jours"], "prix": f["tarif_dzd"]}
            for f in CATALOGUE_METIER
        ]
        self.write({"version": "v1", "items": format_v1})


API_V1_ROUTES = [(r"/api/v1/formations", FormationsV1Handler)]


# 3. MODULE API v2 (/api/v2/formations) : Nouveau contrat avec Breaking Changes assumés
class FormationsV2Handler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("X-API-Version", "2.0")

    def get(self):
        format_v2 = [
            {
                "id": f["id"],
                "code_catalogue": f["code"],
                "titre": f["titre"],
                "duree": {"valeur": f["jours"], "unite": "jours", "heures_pedagogiques": f["jours"] * 7},
                "tarification": {"montant_ht": f["tarif_dzd"], "devise": "DZD"},
                "links": {"self": f"/api/v2/formations/{f['id']}"},
            }
            for f in CATALOGUE_METIER
        ]
        self.write({
            "meta": {"version": "v2", "total": len(format_v2), "retrocompatible_v1": False},
            "data": format_v2,
        })


API_V2_ROUTES = [(r"/api/v2/formations", FormationsV2Handler)]


# 4. MODULE SUPERVISION : Sondes de santé (/api/health/live & /api/health/ready)
class LivenessProbeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"statut": "UP", "uptime_secondes": round(time.time() - DEMARRAGE_SERVEUR, 1)})


class ReadinessProbeHandler(tornado.web.RequestHandler):
    def get(self):
        db_connectee = True
        self.set_status(200 if db_connectee else 503)
        self.write({"pret": db_connectee, "dependances": {"sqlite": "OK"}})


HEALTH_ROUTES = [
    (r"/api/health/live", LivenessProbeHandler),
    (r"/api/health/ready", ReadinessProbeHandler),
]


# 5. APPLICATION FACTORY TORNADO : Assemblage modulaire de v1, v2, Web et Santé
def create_app():
    toutes_les_routes = WEB_ROUTES + API_V1_ROUTES + API_V2_ROUTES + HEALTH_ROUTES
    return tornado.web.Application(
        toutes_les_routes,
        template_path=os.path.join(DOSSIER_COURANT, "templates"),
    )


app = create_app()


async def _demo():
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    print("=== 1. MODULE API v1 (AVEC EN-TÊTES DE DÉPRÉCIATION RFC 8594) ===")
    r1 = await client.fetch(f"http://127.0.0.1:{port}/api/v1/formations")
    print("Headers v1 :", {k: r1.headers[k] for k in ("X-API-Version", "Deprecation", "Sunset", "Link")})
    print("JSON v1    :", tornado.escape.json_decode(r1.body)["items"][0])

    print("\n=== 2. MODULE API v2 (NOUVEAU SCHÉMA ENRICHI COEXISTANT) ===")
    r2 = await client.fetch(f"http://127.0.0.1:{port}/api/v2/formations")
    print("Headers v2 :", {"X-API-Version": r2.headers["X-API-Version"]})
    print("JSON v2    :", tornado.escape.json_decode(r2.body)["data"][0])
    server.stop()


if __name__ == "__main__":
    if "--serve" in sys.argv:
        app.listen(8889)
        tornado.ioloop.IOLoop.current().start()
    else:
        asyncio.run(_demo())
