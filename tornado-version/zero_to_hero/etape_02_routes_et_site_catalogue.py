# Zero to Hero Tornado — Etape 2/6 : Routes Regex, Filtrage, Tri, Pagination & Site Catalogue
# Execution : .venv/bin/python tornado-version/zero_to_hero/etape_02_routes_et_site_catalogue.py
# Evolution depuis l'Etape 1 : conservation de GET / et GET /api/bonjour + ajout du catalogue /api/v1/formations

import asyncio
import math
import os
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.netutil
import tornado.web

DOSSIER = os.path.dirname(os.path.abspath(__file__))

FORMATIONS = [
    {"id": 1, "code": "ISGP-101", "titre": "Fondamentaux HTTP/1.1 & Architecture REST", "domaine": "Architecture", "duree_jours": 3, "tarif_dzd": 45000},
    {"id": 2, "code": "ISGP-201", "titre": "Serveurs Asynchrones Tornado & IOLoop", "domaine": "Backend", "duree_jours": 5, "tarif_dzd": 65000},
    {"id": 3, "code": "ISGP-204", "titre": "Persistance SQLite WAL & Integrite ACID", "domaine": "Data", "duree_jours": 4, "tarif_dzd": 55000},
    {"id": 4, "code": "ISGP-301", "titre": "Securite API : HMAC, Cookies Signes & RBAC", "domaine": "Securite", "duree_jours": 5, "tarif_dzd": 72000},
    {"id": 5, "code": "ISGP-401", "titre": "Gouvernance OpenAPI 3.0 & Reverse Proxy Nginx", "domaine": "DevOps", "duree_jours": 3, "tarif_dzd": 58000},
]

CHAMPS_TRI_AUTORISES = {"id", "titre", "duree_jours", "tarif_dzd"}


class AccueilCatalogueHandler(tornado.web.RequestHandler):
    def get(self):
        domaines = sorted({f["domaine"] for f in FORMATIONS})
        self.render(
            "etape_02_catalogue.html",
            titre_page="Portail Formations ISGP — Etape 2 (Catalogue & Filtrage)",
            nb_initial=len(FORMATIONS),
            domaines=domaines,
        )


class BonjourApiHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"etape": 2, "service": "Portail & API Catalogue ISGP", "statut": "operationnel"})


class FormationsListHandler(tornado.web.RequestHandler):
    def get(self):
        domaine = self.get_query_argument("domaine", "").strip()
        tri_brut = self.get_query_argument("tri", "id").strip() or "id"
        page = max(1, int(self.get_query_argument("page", "1")))
        limit = min(25, max(1, int(self.get_query_argument("limit", "3"))))

        inverse = tri_brut.startswith("-")
        cle_tri = tri_brut.lstrip("-")
        if cle_tri not in CHAMPS_TRI_AUTORISES:
            cle_tri = "id"

        filtrees = [
            f for f in FORMATIONS
            if not domaine or f["domaine"].lower() == domaine.lower()
        ]
        filtrees.sort(key=lambda x: x[cle_tri], reverse=inverse)

        total = len(filtrees)
        total_pages = max(1, math.ceil(total / limit))
        debut = (page - 1) * limit
        self.write({
            "meta": {"page": page, "limit": limit, "total": total, "total_pages": total_pages, "tri": tri_brut},
            "data": filtrees[debut : debut + limit],
        })


class FormationDetailHandler(tornado.web.RequestHandler):
    def get(self, id_str):
        fid = int(id_str)
        for f in FORMATIONS:
            if f["id"] == fid:
                self.write({"data": f})
                return
        self.set_status(404)
        self.write({"erreur": f"Formation #{fid} introuvable dans le catalogue ISGP"})


def make_app():
    return tornado.web.Application(
        [
            (r"/", AccueilCatalogueHandler),
            (r"/api/bonjour", BonjourApiHandler),
            (r"/api/v1/formations", FormationsListHandler),
            (r"/api/v1/formations/([0-9]+)", FormationDetailHandler),
        ],
        template_path=os.path.join(DOSSIER, "templates"),
    )


async def main():
    port_cible = int(os.environ.get("PORT", 8889))
    try:
        sockets = tornado.netutil.bind_sockets(port_cible, "127.0.0.1")
    except OSError:
        sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(make_app())
    server.add_sockets(sockets)

    client = tornado.httpclient.AsyncHTTPClient()
    r_html = await client.fetch(f"http://127.0.0.1:{port}/")
    r_list = await client.fetch(f"http://127.0.0.1:{port}/api/v1/formations?domaine=Securite&tri=-tarif_dzd")
    r_item = await client.fetch(f"http://127.0.0.1:{port}/api/v1/formations/2")
    r_404 = await client.fetch(f"http://127.0.0.1:{port}/api/v1/formations/999", raise_error=False)
    assert r_html.code == 200 and "text/html" in r_html.headers["Content-Type"]
    assert tornado.escape.json_decode(r_list.body)["meta"]["total"] == 1
    assert tornado.escape.json_decode(r_item.body)["data"]["code"] == "ISGP-201"
    assert r_404.code == 404
    print(f"[ETAPE 2 OK] Site Catalogue : http://127.0.0.1:{port}/ | API : http://127.0.0.1:{port}/api/v1/formations")
    if "--once" in sys.argv:
        server.stop()
        return
    print("Serveur Tornado actif (Ctrl+C pour arreter).")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
