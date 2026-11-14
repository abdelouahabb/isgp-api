# Zero to Hero Tornado — Etape 4/6 : Persistance SQLite3 WAL Non-Bloquante (run_in_executor)
# Execution : .venv/bin/python tornado-version/zero_to_hero/etape_04_persistance_sqlite_wal.py
# Evolution depuis l'Etape 3 : remplacement de la liste en memoire par SQLite3 (WAL + FK + busy_timeout)
# execute dans un ThreadPoolExecutor afin de ne jamais bloquer la boucle IOLoop Tornado.

import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import math
import os
import sqlite3
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

DOSSIER = os.path.dirname(os.path.abspath(__file__))
CHEMIN_DB = os.path.join(DOSSIER, "zero_to_hero_isgp.db")
DB_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="sqlite-wal")

DOMAINES_VALIDES = {"Architecture", "Backend", "Data", "Securite", "DevOps"}
COLONNES_TRI = {"id": "id", "titre": "titre", "duree_jours": "duree_jours", "tarif_dzd": "tarif_dzd"}


def ouvrir_connexion():
    conn = sqlite3.connect(CHEMIN_DB, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


def initialiser_schema_sqlite():
    with ouvrir_connexion() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS formations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                titre TEXT NOT NULL,
                domaine TEXT NOT NULL,
                duree_jours INTEGER NOT NULL CHECK(duree_jours BETWEEN 1 AND 30),
                tarif_dzd INTEGER NOT NULL CHECK(tarif_dzd >= 0)
            )
        """)
        nb = conn.execute("SELECT COUNT(*) FROM formations").fetchone()[0]
        if nb == 0:
            semences = [
                ("ISGP-101", "Fondamentaux HTTP/1.1 & Architecture REST", "Architecture", 3, 45000),
                ("ISGP-201", "Serveurs Asynchrones Tornado & IOLoop", "Backend", 5, 65000),
                ("ISGP-204", "Persistance SQLite WAL & Integrite ACID", "Data", 4, 55000),
                ("ISGP-301", "Securite API : HMAC, Cookies Signes & RBAC", "Securite", 5, 72000),
            ]
            conn.executemany(
                "INSERT INTO formations (code, titre, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
                semences,
            )
        conn.commit()


def valider_formation(payload, partiel=False):
    if not isinstance(payload, dict):
        return {"_corps": "Objet JSON requis."}
    erreurs = {}
    if not partiel or "code" in payload:
        code = str(payload.get("code", "")).strip()
        if not (3 <= len(code) <= 24):
            erreurs["code"] = "Le code doit contenir entre 3 et 24 caracteres."
    if not partiel or "titre" in payload:
        titre = str(payload.get("titre", "")).strip()
        if not (4 <= len(titre) <= 140):
            erreurs["titre"] = "Le titre doit contenir entre 4 et 140 caracteres."
    if not partiel or "domaine" in payload:
        if str(payload.get("domaine", "Backend")).strip() not in DOMAINES_VALIDES:
            erreurs["domaine"] = f"Domaine autorise : {sorted(DOMAINES_VALIDES)}"
    if not partiel or "duree_jours" in payload:
        try:
            if not (1 <= int(payload.get("duree_jours", 0)) <= 30):
                erreurs["duree_jours"] = "Duree comprise entre 1 et 30 jours."
        except (TypeError, ValueError):
            erreurs["duree_jours"] = "Nombre entier requis."
    if not partiel or "tarif_dzd" in payload:
        try:
            if int(payload.get("tarif_dzd", -1)) < 0:
                erreurs["tarif_dzd"] = "Tarif positif ou nul requis."
        except (TypeError, ValueError):
            erreurs["tarif_dzd"] = "Nombre entier requis."
    return erreurs


async def executer_db(fn, *args):
    return await tornado.ioloop.IOLoop.current().run_in_executor(DB_EXECUTOR, fn, *args)


def _db_lister(domaine, col_tri, desc, limit, offset):
    sens = "DESC" if desc else "ASC"
    with ouvrir_connexion() as conn:
        if domaine:
            total = conn.execute("SELECT COUNT(*) FROM formations WHERE lower(domaine)=lower(?)", (domaine,)).fetchone()[0]
            rows = conn.execute(
                f"SELECT * FROM formations WHERE lower(domaine)=lower(?) ORDER BY {col_tri} {sens} LIMIT ? OFFSET ?",
                (domaine, limit, offset),
            ).fetchall()
        else:
            total = conn.execute("SELECT COUNT(*) FROM formations").fetchone()[0]
            rows = conn.execute(
                f"SELECT * FROM formations ORDER BY {col_tri} {sens} LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
    return total, [dict(r) for r in rows]


def _db_obtenir(fid):
    with ouvrir_connexion() as conn:
        row = conn.execute("SELECT * FROM formations WHERE id = ?", (fid,)).fetchone()
        return dict(row) if row else None


def _db_inserer(code, titre, domaine, jours, tarif):
    with ouvrir_connexion() as conn:
        cur = conn.execute(
            "INSERT INTO formations (code, titre, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
            (code, titre, domaine, jours, tarif),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM formations WHERE id = ?", (cur.lastrowid,)).fetchone()
        return dict(row)


def _db_mettre_a_jour(fid, champs):
    with ouvrir_connexion() as conn:
        actuel = conn.execute("SELECT * FROM formations WHERE id = ?", (fid,)).fetchone()
        if not actuel:
            return None
        fusion = dict(actuel)
        fusion.update(champs)
        conn.execute(
            "UPDATE formations SET code=?, titre=?, domaine=?, duree_jours=?, tarif_dzd=? WHERE id=?",
            (fusion["code"], fusion["titre"], fusion["domaine"], int(fusion["duree_jours"]), int(fusion["tarif_dzd"]), fid),
        )
        conn.commit()
        return dict(conn.execute("SELECT * FROM formations WHERE id = ?", (fid,)).fetchone())


def _db_supprimer(fid):
    with ouvrir_connexion() as conn:
        cur = conn.execute("DELETE FROM formations WHERE id = ?", (fid,))
        conn.commit()
        return cur.rowcount > 0


def _db_diagnostic():
    with ouvrir_connexion() as conn:
        jm = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        nb = conn.execute("SELECT COUNT(*) FROM formations;").fetchone()[0]
    return {"sqlite_version": sqlite3.sqlite_version, "journal_mode": jm, "foreign_keys": fk, "nb_formations": nb, "executor": "ThreadPoolExecutor(4)"}


class BaseProblemHandler(tornado.web.RequestHandler):
    def repondre_probleme(self, status, title, detail, errors=None):
        self.set_status(status)
        corps = {"type": "https://api.isgp.dz/problems/sql-api", "title": title, "status": status, "detail": detail, "instance": self.request.path}
        if errors:
            corps["errors"] = errors
        self.write(corps)
        self.set_header("Content-Type", "application/problem+json; charset=UTF-8")

    def lire_json(self):
        try:
            return tornado.escape.json_decode(self.request.body or b"{}")
        except ValueError:
            return None


class AccueilSqliteHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("etape_04_sqlite.html", titre_page="Portail Formations ISGP — Etape 4 (SQLite WAL & Executor)")


class SqliteDiagnosticHandler(tornado.web.RequestHandler):
    async def get(self):
        self.write(await executer_db(_db_diagnostic))


class FormationsSqlCollectionHandler(BaseProblemHandler):
    async def get(self):
        domaine = self.get_query_argument("domaine", "").strip()
        tri_brut = self.get_query_argument("tri", "id").strip() or "id"
        page = max(1, int(self.get_query_argument("page", "1")))
        limit = min(50, max(1, int(self.get_query_argument("limit", "10"))))
        col = COLONNES_TRI.get(tri_brut.lstrip("-"), "id")
        total, items = await executer_db(_db_lister, domaine, col, tri_brut.startswith("-"), limit, (page - 1) * limit)
        self.write({"meta": {"page": page, "limit": limit, "total": total, "total_pages": max(1, math.ceil(total / limit))}, "data": items})

    async def post(self):
        payload = self.lire_json()
        erreurs = valider_formation(payload, partiel=False)
        if erreurs:
            return self.repondre_probleme(422, "Validation echouee", "Payload invalide.", erreurs)
        try:
            cree = await executer_db(
                _db_inserer,
                str(payload["code"]).strip(),
                str(payload["titre"]).strip(),
                str(payload.get("domaine", "Backend")).strip(),
                int(payload["duree_jours"]),
                int(payload["tarif_dzd"]),
            )
        except sqlite3.IntegrityError:
            return self.repondre_probleme(409, "Conflit SQLite UNIQUE", "Ce code formation existe deja.")
        self.set_status(201)
        self.write({"data": cree})


class FormationSqlItemHandler(BaseProblemHandler):
    async def get(self, id_str):
        entite = await executer_db(_db_obtenir, int(id_str))
        if not entite:
            return self.repondre_probleme(404, "Introuvable", f"Formation #{id_str} absente.")
        self.write({"data": entite})

    async def put(self, id_str):
        payload = self.lire_json()
        erreurs = valider_formation(payload, partiel=False)
        if erreurs:
            return self.repondre_probleme(422, "Validation PUT echouee", "Champs invalides.", erreurs)
        maj = await executer_db(_db_mettre_a_jour, int(id_str), payload)
        if not maj:
            return self.repondre_probleme(404, "Introuvable", f"Formation #{id_str} absente.")
        self.write({"data": maj})

    async def patch(self, id_str):
        payload = self.lire_json()
        erreurs = valider_formation(payload, partiel=True)
        if erreurs:
            return self.repondre_probleme(422, "Validation PATCH echouee", "Champs invalides.", erreurs)
        champs = {k: payload[k] for k in ("code", "titre", "domaine", "duree_jours", "tarif_dzd") if k in payload}
        maj = await executer_db(_db_mettre_a_jour, int(id_str), champs)
        if not maj:
            return self.repondre_probleme(404, "Introuvable", f"Formation #{id_str} absente.")
        self.write({"data": maj})

    async def delete(self, id_str):
        ok = await executer_db(_db_supprimer, int(id_str))
        if not ok:
            return self.repondre_probleme(404, "Introuvable", f"Formation #{id_str} absente.")
        self.set_status(204)
        self.finish()


def make_app():
    initialiser_schema_sqlite()
    return tornado.web.Application(
        [
            (r"/", AccueilSqliteHandler),
            (r"/api/bonjour", SqliteDiagnosticHandler),
            (r"/api/v1/sqlite-diagnostic", SqliteDiagnosticHandler),
            (r"/api/v1/formations", FormationsSqlCollectionHandler),
            (r"/api/v1/formations/([0-9]+)", FormationSqlItemHandler),
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
    r_diag = await client.fetch(f"http://127.0.0.1:{port}/api/v1/sqlite-diagnostic")
    diag = tornado.escape.json_decode(r_diag.body)
    assert r_html.code == 200 and diag["journal_mode"].lower() == "wal" and diag["foreign_keys"] == 1
    if "--once" in sys.argv:
        r_post = await client.fetch(
            f"http://127.0.0.1:{port}/api/v1/formations",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"code": "TMP-WAL-01", "titre": "Verification SQLite WAL", "domaine": "Data", "duree_jours": 2, "tarif_dzd": 30000}),
        )
        cid = tornado.escape.json_decode(r_post.body)["data"]["id"]
        r_del = await client.fetch(f"http://127.0.0.1:{port}/api/v1/formations/{cid}", method="DELETE")
        assert r_del.code == 204
        print(f"[ETAPE 4 OK] SQLite WAL ({diag['journal_mode']}) + run_in_executor valides sur http://127.0.0.1:{port}/")
        server.stop()
        return

    print(f"[ETAPE 4 OK] Portail SQLite WAL : http://127.0.0.1:{port}/ | Diagnostic : http://127.0.0.1:{port}/api/v1/sqlite-diagnostic")
    print("Serveur Tornado actif (Ctrl+C pour arreter).")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
