import os
# Fichier : day_5/02_pagination_filtrage_production.py
# Exécution : .venv/bin/python day_5/02_pagination_filtrage_production.py
# Objectif : Ingénierie Avancée d'une API Tornado de Production (100 % Tornado Non-Blocking) :
#   1. Pagination par Offset/Limit (?page=2&per_page=2) avec enveloppe normalisée (meta, data, links)
#   2. Pagination Haute Performance par Curseur (?after_id=2&limit=2) pour les grands volumes SQL
#   3. Filtrage multi-critères (?domaine=Securite&duree_min=4) & Tri sécurisé par liste blanche (Whitelist)

import asyncio
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

CATALOGUE_FORMATIONS = [
    {"id": 1, "titre": "Architecture API REST & Tornado", "domaine": "Backend", "duree_jours": 5, "tarif_dzd": 65000},
    {"id": 2, "titre": "Templates Tornado & Formulaires Web", "domaine": "Web", "duree_jours": 3, "tarif_dzd": 45000},
    {"id": 3, "titre": "Persistance SQLite & Transactions ACID", "domaine": "Data", "duree_jours": 4, "tarif_dzd": 55000},
    {"id": 4, "titre": "Sécurité JWT, Cookies Signés & RBAC", "domaine": "Securite", "duree_jours": 5, "tarif_dzd": 70000},
    {"id": 5, "titre": "Déploiement Nginx, HTTPServer & Load Balancing", "domaine": "DevOps", "duree_jours": 4, "tarif_dzd": 60000},
]

# Liste blanche stricte des champs autorisés pour le tri (empêche toute injection dans ORDER BY)
CHAMPS_TRI_AUTORISES = {"id", "duree_jours", "tarif_dzd", "titre"}


# 1. RECHERCHE MULTI-CRITÈRES, TRI SÉCURISÉ ET PAGINATION OFFSET/LIMIT
class CatalogueOffsetHandler(tornado.web.RequestHandler):
    def get(self):
        domaine = self.get_query_argument("domaine", "").strip()
        duree_min = int(self.get_query_argument("duree_min", "1"))
        tri = self.get_query_argument("sort", "id").strip()
        page = max(1, int(self.get_query_argument("page", "1")))
        per_page = min(20, max(1, int(self.get_query_argument("per_page", "2"))))

        # Gestion du tri décroissant (ex: ?sort=-tarif_dzd) avec validation par liste blanche
        ordre_inverse = tri.startswith("-")
        cle_tri = tri.lstrip("-")
        if cle_tri not in CHAMPS_TRI_AUTORISES:
            self.set_status(422)
            self.write({
                "erreur": f"Champ de tri '{cle_tri}' interdit",
                "champs_autorises": sorted(CHAMPS_TRI_AUTORISES),
            })
            return

        # Filtrage métier
        resultats = [
            f for f in CATALOGUE_FORMATIONS
            if f["duree_jours"] >= duree_min and (not domaine or f["domaine"].lower() == domaine.lower())
        ]
        resultats.sort(key=lambda x: x[cle_tri], reverse=ordre_inverse)

        # Découpage de la fenêtre Offset / Limit
        total = len(resultats)
        offset = (page - 1) * per_page
        tranche = resultats[offset : offset + per_page]

        self.write({
            "meta": {
                "mode_pagination": "offset_limit",
                "page": page,
                "per_page": per_page,
                "total_items": total,
                "total_pages": max(1, (total + per_page - 1) // per_page),
            },
            "data": tranche,
            "links": {
                "self": f"/api/v1/catalogue/offset?page={page}&per_page={per_page}",
                "next": f"/api/v1/catalogue/offset?page={page + 1}&per_page={per_page}" if offset + per_page < total else None,
            },
        })


# 2. PAGINATION PAR CURSEUR (?after_id=2&limit=2) : Temps constant O(1) sur des millions de lignes SQL
class CatalogueCursorHandler(tornado.web.RequestHandler):
    def get(self):
        after_id = int(self.get_query_argument("after_id", "0"))
        limit = min(20, max(1, int(self.get_query_argument("limit", "2"))))

        # Équivalent SQL : SELECT * FROM formations WHERE id > ? ORDER BY id ASC LIMIT ?
        suivants = [f for f in CATALOGUE_FORMATIONS if f["id"] > after_id][:limit]
        prochain_curseur = suivants[-1]["id"] if len(suivants) == limit else None

        self.write({
            "meta": {
                "mode_pagination": "cursor_keyset",
                "after_id": after_id,
                "limit": limit,
                "next_cursor": prochain_curseur,
            },
            "data": suivants,
            "links": {
                "next": f"/api/v1/catalogue/cursor?after_id={prochain_curseur}&limit={limit}" if prochain_curseur else None,
            },
        })


class PortailPaginationProdHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("portail_d5_02.html")


def make_app():
    dossier = os.path.dirname(os.path.abspath(__file__))
    return tornado.web.Application(
        [
            (r"/", PortailPaginationProdHandler),
            (r"/api/v1/catalogue/offset", CatalogueOffsetHandler),
            (r"/api/v1/catalogue/cursor", CatalogueCursorHandler),
        ],
        template_path=os.path.join(dossier, "templates"),
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

    print("=== 1. PAGINATION OFFSET/LIMIT + TRI DÉCROISSANT (?sort=-tarif_dzd&page=1&per_page=2) ===")
    r1 = await client.fetch(f"http://127.0.0.1:{port}/api/v1/catalogue/offset?sort=-tarif_dzd&page=1&per_page=2")
    print(tornado.escape.json_decode(r1.body))

    print("\n=== 2. PAGINATION PAR CURSEUR HAUTE PERFORMANCE (?after_id=2&limit=2) ===")
    r2 = await client.fetch(f"http://127.0.0.1:{port}/api/v1/catalogue/cursor?after_id=2&limit=2")
    print(tornado.escape.json_decode(r2.body))
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
