# Zero to Hero Tornado — Etape 3/6 : CRUD Complet (POST, PUT, PATCH, DELETE) & Validation RFC 7807
# Execution : .venv/bin/python tornado-version/zero_to_hero/etape_03_crud_et_validation_rfc7807.py
# Evolution depuis l'Etape 2 : ajout des mutations REST et des erreurs normalisees application/problem+json

import asyncio
import json
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
]

DOMAINES_VALIDES = {"Architecture", "Backend", "Data", "Securite", "DevOps"}
CHAMPS_TRI = {"id", "titre", "duree_jours", "tarif_dzd"}


def valider_formation(payload, partiel=False):
    if not isinstance(payload, dict):
        return {"_corps": "Un objet JSON valide est requis."}
    erreurs = {}
    if not partiel or "code" in payload:
        code = str(payload.get("code", "")).strip()
        if len(code) < 3 or len(code) > 20:
            erreurs["code"] = "Le code catalogue doit contenir entre 3 et 20 caracteres."
    if not partiel or "titre" in payload:
        titre = str(payload.get("titre", "")).strip()
        if len(titre) < 4 or len(titre) > 140:
            erreurs["titre"] = "Le titre doit contenir entre 4 et 140 caracteres."
    if not partiel or "domaine" in payload:
        domaine = str(payload.get("domaine", "Backend")).strip()
        if domaine not in DOMAINES_VALIDES:
            erreurs["domaine"] = f"Domaine invalide. Valeurs acceptees : {sorted(DOMAINES_VALIDES)}"
    if not partiel or "duree_jours" in payload:
        try:
            jours = int(payload.get("duree_jours", 0))
            if not (1 <= jours <= 30):
                erreurs["duree_jours"] = "La duree doit etre comprise entre 1 et 30 jours."
        except (TypeError, ValueError):
            erreurs["duree_jours"] = "La duree doit etre un entier."
    if not partiel or "tarif_dzd" in payload:
        try:
            tarif = int(payload.get("tarif_dzd", -1))
            if tarif < 0:
                erreurs["tarif_dzd"] = "Le tarif en DZD doit etre positif ou nul."
        except (TypeError, ValueError):
            erreurs["tarif_dzd"] = "Le tarif doit etre un entier."
    return erreurs


class ProblemJsonBaseHandler(tornado.web.RequestHandler):
    def repondre_probleme(self, status, title, detail, errors=None, type_slug="validation-error"):
        self.set_status(status)
        corps = {
            "type": f"https://api.isgp.dz/problems/{type_slug}",
            "title": title,
            "status": status,
            "detail": detail,
            "instance": self.request.path,
        }
        if errors:
            corps["errors"] = errors
        self.write(corps)
        # Note Tornado : self.write(dict) positionne application/json, on applique donc problem+json juste apres
        self.set_header("Content-Type", "application/problem+json; charset=UTF-8")

    def lire_json(self):
        try:
            return tornado.escape.json_decode(self.request.body or b"{}")
        except ValueError:
            return None


class AccueilCrudHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("etape_03_crud.html", titre_page="Portail Formations ISGP — Etape 3 (CRUD & RFC 7807)")


class BonjourApiHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"etape": 3, "service": "Portail & API Catalogue ISGP", "statut": "operationnel"})


class FormationsCollectionHandler(ProblemJsonBaseHandler):
    def get(self):
        domaine = self.get_query_argument("domaine", "").strip()
        tri_brut = self.get_query_argument("tri", "id").strip() or "id"
        page = max(1, int(self.get_query_argument("page", "1")))
        limit = min(50, max(1, int(self.get_query_argument("limit", "10"))))
        inverse = tri_brut.startswith("-")
        cle = tri_brut.lstrip("-") if tri_brut.lstrip("-") in CHAMPS_TRI else "id"
        filtrees = [f for f in FORMATIONS if not domaine or f["domaine"].lower() == domaine.lower()]
        filtrees.sort(key=lambda x: x[cle], reverse=inverse)
        total = len(filtrees)
        debut = (page - 1) * limit
        self.write({
            "meta": {"page": page, "limit": limit, "total": total, "total_pages": max(1, math.ceil(total / limit))},
            "data": filtrees[debut : debut + limit],
        })

    def post(self):
        payload = self.lire_json()
        erreurs = valider_formation(payload, partiel=False)
        if erreurs:
            return self.repondre_probleme(422, "Echec de validation metier", "Certains champs violent le contrat ISGP.", erreurs)
        nouvel_id = max((f["id"] for f in FORMATIONS), default=0) + 1
        entite = {
            "id": nouvel_id,
            "code": str(payload["code"]).strip(),
            "titre": str(payload["titre"]).strip(),
            "domaine": str(payload.get("domaine", "Backend")).strip(),
            "duree_jours": int(payload["duree_jours"]),
            "tarif_dzd": int(payload["tarif_dzd"]),
        }
        FORMATIONS.append(entite)
        self.set_status(201)
        self.set_header("Location", f"/api/v1/formations/{nouvel_id}")
        self.write({"data": entite})


class FormationItemHandler(ProblemJsonBaseHandler):
    def _trouver(self, fid):
        for idx, f in enumerate(FORMATIONS):
            if f["id"] == fid:
                return idx, f
        return -1, None

    def get(self, id_str):
        _, entite = self._trouver(int(id_str))
        if not entite:
            return self.repondre_probleme(404, "Ressource introuvable", f"Aucune formation #{id_str}.", type_slug="not-found")
        self.write({"data": entite})

    def put(self, id_str):
        idx, entite = self._trouver(int(id_str))
        if not entite:
            return self.repondre_probleme(404, "Ressource introuvable", f"Aucune formation #{id_str}.", type_slug="not-found")
        payload = self.lire_json()
        erreurs = valider_formation(payload, partiel=False)
        if erreurs:
            return self.repondre_probleme(422, "Echec de validation PUT", "Remplacement complet invalide.", erreurs)
        remplacee = {
            "id": entite["id"],
            "code": str(payload["code"]).strip(),
            "titre": str(payload["titre"]).strip(),
            "domaine": str(payload["domaine"]).strip(),
            "duree_jours": int(payload["duree_jours"]),
            "tarif_dzd": int(payload["tarif_dzd"]),
        }
        FORMATIONS[idx] = remplacee
        self.write({"data": remplacee})

    def patch(self, id_str):
        _, entite = self._trouver(int(id_str))
        if not entite:
            return self.repondre_probleme(404, "Ressource introuvable", f"Aucune formation #{id_str}.", type_slug="not-found")
        payload = self.lire_json()
        erreurs = valider_formation(payload, partiel=True)
        if erreurs:
            return self.repondre_probleme(422, "Echec de validation PATCH", "Modification partielle invalide.", erreurs)
        for cle in ("code", "titre", "domaine"):
            if cle in payload:
                entite[cle] = str(payload[cle]).strip()
        for cle in ("duree_jours", "tarif_dzd"):
            if cle in payload:
                entite[cle] = int(payload[cle])
        self.write({"data": entite})

    def delete(self, id_str):
        idx, entite = self._trouver(int(id_str))
        if not entite:
            return self.repondre_probleme(404, "Ressource introuvable", f"Aucune formation #{id_str}.", type_slug="not-found")
        FORMATIONS.pop(idx)
        self.set_status(204)
        self.finish()


def make_app():
    return tornado.web.Application(
        [
            (r"/", AccueilCrudHandler),
            (r"/api/bonjour", BonjourApiHandler),
            (r"/api/v1/formations", FormationsCollectionHandler),
            (r"/api/v1/formations/([0-9]+)", FormationItemHandler),
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
    assert r_html.code == 200 and "text/html" in r_html.headers["Content-Type"]
    if "--once" in sys.argv:
        r_422 = await client.fetch(
            f"http://127.0.0.1:{port}/api/v1/formations",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"code": "A", "titre": "No", "duree_jours": 99, "tarif_dzd": -1}),
            raise_error=False,
        )
        assert r_422.code == 422 and "application/problem+json" in r_422.headers["Content-Type"]
        r_201 = await client.fetch(
            f"http://127.0.0.1:{port}/api/v1/formations",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"code": "ISGP-399", "titre": "Test CRUD Automatique", "domaine": "Backend", "duree_jours": 3, "tarif_dzd": 50000}),
        )
        cid = tornado.escape.json_decode(r_201.body)["data"]["id"]
        r_patch = await client.fetch(
            f"http://127.0.0.1:{port}/api/v1/formations/{cid}",
            method="PATCH",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"tarif_dzd": 52000}),
        )
        assert r_patch.code == 200 and tornado.escape.json_decode(r_patch.body)["data"]["tarif_dzd"] == 52000
        r_del = await client.fetch(f"http://127.0.0.1:{port}/api/v1/formations/{cid}", method="DELETE")
        assert r_del.code == 204
        print(f"[ETAPE 3 OK] CRUD & RFC 7807 valides sur http://127.0.0.1:{port}/")
        server.stop()
        return

    print(f"[ETAPE 3 OK] Site CRUD & RFC 7807 : http://127.0.0.1:{port}/ | API : http://127.0.0.1:{port}/api/v1/formations")
    print("Serveur Tornado actif (Ctrl+C pour arreter).")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
