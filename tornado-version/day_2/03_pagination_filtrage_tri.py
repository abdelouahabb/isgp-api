# Fichier : day_2/03_pagination_filtrage_tri.py
# Exécution : .venv/bin/python day_2/03_pagination_filtrage_tri.py
# Exemple d'appel :
#   http://127.0.0.1:8889/api/v1/formations?page=1&limit=2&salle=Salle+A&tri=duree_jours&ordre=desc

import asyncio
import math
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

CATALOGUE = [
    {"id": 1, "code": "API-101", "titre": "Fondamentaux HTTP & REST", "duree_jours": 2, "salle": "Salle A"},
    {"id": 2, "code": "TRN-201", "titre": "Développement API avec Tornado", "duree_jours": 5, "salle": "Salle A"},
    {"id": 3, "code": "SQL-202", "titre": "Persistance SQLite & Transactions", "duree_jours": 3, "salle": "Salle B"},
    {"id": 4, "code": "SEC-301", "titre": "Sécurité, Bearer Tokens & HMAC", "duree_jours": 4, "salle": "Labo 1"},
    {"id": 5, "code": "OPS-302", "titre": "Rate Limiting & Résilience", "duree_jours": 2, "salle": "Labo 1"},
    {"id": 6, "code": "PRO-401", "titre": "Architecture Modulaire & Production", "duree_jours": 5, "salle": "Salle B"},
]


class FormationsPaginationHandler(tornado.web.RequestHandler):
    def get(self):
        # 1. FILTRAGE (Query Params lus via self.get_query_argument)
        salle_filtre = self.get_query_argument("salle", "").strip()
        min_jours = int(self.get_query_argument("min_jours", "1"))

        resultats = [
            f for f in CATALOGUE
            if f["duree_jours"] >= min_jours
            and (not salle_filtre or f["salle"].lower() == salle_filtre.lower())
        ]

        # 2. TRI DYNAMIQUE (?tri=duree_jours&ordre=desc) avec liste blanche
        champ_tri = self.get_query_argument("tri", "id")
        if champ_tri not in ("id", "duree_jours", "titre"):
            champ_tri = "id"
        inversion = self.get_query_argument("ordre", "asc").lower() == "desc"
        resultats.sort(key=lambda x: x[champ_tri], reverse=inversion)

        # 3. PAGINATION (?page=1&limit=2)
        page = max(1, int(self.get_query_argument("page", "1")))
        limit = min(50, max(1, int(self.get_query_argument("limit", "3"))))
        total_elements = len(resultats)
        total_pages = max(1, math.ceil(total_elements / limit))

        debut = (page - 1) * limit
        fin = debut + limit
        tranche_page = resultats[debut:fin]

        self.write({
            "meta": {
                "page_actuelle": page,
                "elements_par_page": limit,
                "total_elements": total_elements,
                "total_pages": total_pages,
                "a_page_suivante": page < total_pages,
                "a_page_precedente": page > 1,
            },
            "data": tranche_page,
        })


def make_app():
    return tornado.web.Application([(r"/api/v1/formations", FormationsPaginationHandler)])


async def _demo():
    app = make_app()
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    url = f"http://127.0.0.1:{port}/api/v1/formations?page=1&limit=2&salle=Salle+A&tri=duree_jours&ordre=desc"
    rep = await client.fetch(url)
    print("=== TEST PAGINATION, FILTRAGE ET TRI DANS TORNADO ===")
    print(tornado.escape.json_decode(rep.body))
    server.stop()


if __name__ == "__main__":
    if "--serve" in sys.argv:
        make_app().listen(8889)
        tornado.ioloop.IOLoop.current().start()
    else:
        asyncio.run(_demo())
