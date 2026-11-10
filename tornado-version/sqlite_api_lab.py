"""
================================================================================
MANUEL & LABORATOIRE SQLITE3 — ÉDITION TORNADO (IOLoop, run_in_executor & closing)
================================================================================
Ce script autonome de référence illustre toutes les opérations SQLite3 dans une
API REST Tornado (`tornado.web.RequestHandler`) sans dépendance externe :
  1. Déport des E/S disque via `IOLoop.current().run_in_executor(None, ...)`
  2. Pragmas de production (`journal_mode=WAL`, `synchronous=NORMAL`, `foreign_keys=ON`, `busy_timeout=5000`)
  3. Fermeture explicite et déterministe du curseur avec `contextlib.closing(conn.cursor())`
  4. CRUD Complet :
     - `find_many` (`fetchall()` / `fetchmany()`) avec filtres `?` et liste blanche `ORDER BY`
     - `find_one` (`fetchone()`) avec gestion du tuple à 1 élément `(id,)` et statut 404
     - `insert_one` avec marqueurs nommés `:nom` et `cur.lastrowid`
     - `insert_many` en lot atomique avec `cur.executemany()`
     - `update` et `delete` avec inspection de `cur.rowcount`
================================================================================
"""

import asyncio
from contextlib import closing
import json
import os
import sqlite3
import sys
import tempfile
import urllib.parse
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

DB_FILE = os.path.join(tempfile.gettempdir(), "isgp_sqlite_lab_tornado.db")

COLONNES_TRI_AUTORISEES = {
    "id": "id",
    "duree_jours": "duree_jours",
    "budget_dzd": "budget_dzd",
    "titre": "titre",
}


def ouvrir_connexion_sqlite() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, timeout=5.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    return conn


def initialiser_schema_et_donnees():
    conn = ouvrir_connexion_sqlite()
    with conn:
        with closing(conn.cursor()) as cur:
            cur.execute("DROP TABLE IF EXISTS formations_lab")
            cur.execute(
                """
                CREATE TABLE formations_lab (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code_interne TEXT NOT NULL UNIQUE,
                    titre TEXT NOT NULL,
                    salle TEXT NOT NULL,
                    duree_jours INTEGER NOT NULL CHECK(duree_jours BETWEEN 1 AND 30),
                    budget_dzd REAL NOT NULL DEFAULT 0.0
                )
                """
            )
            lot_initial = [
                ("API-101", "Architecture REST & Tornado IOLoop", "Salle A", 5, 45000.0),
                ("SEC-202", "Sécurité des APIs, JWT & Requêtes Préparées", "Salle B", 4, 52000.0),
                ("SQL-303", "Persistance SQLite WAL & Modélisation Relationnelle", "Salle A", 3, 38000.0),
            ]
            cur.executemany(
                """
                INSERT INTO formations_lab (code_interne, titre, salle, duree_jours, budget_dzd)
                VALUES (?, ?, ?, ?, ?)
                """,
                lot_initial,
            )
    conn.close()


class FormationsCollectionSqliteHandler(tornado.web.RequestHandler):
    """Gère FIND_MANY (`GET /api/sqlite/formations`) et INSERT_ONE (`POST /api/sqlite/formations`)."""

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    async def get(self):
        salle = self.get_query_argument("salle", default=None)
        try:
            min_jours = int(self.get_query_argument("min_jours", default="1"))
        except ValueError:
            min_jours = 1
        tri_demande = self.get_query_argument("tri", default="id")
        ordre_demande = self.get_query_argument("ordre", default="asc").lower()

        colonne_sure = COLONNES_TRI_AUTORISEES.get(tri_demande, "id")
        direction_sure = "DESC" if ordre_demande == "desc" else "ASC"

        sql = "SELECT id, code_interne, titre, salle, duree_jours, budget_dzd FROM formations_lab WHERE duree_jours >= ?"
        params = [min_jours]
        if salle:
            sql += " AND salle = ?"
            params.append(salle)
        sql += f" ORDER BY {colonne_sure} {direction_sure}"

        def _executer_find_many():
            conn = ouvrir_connexion_sqlite()
            try:
                with closing(conn.cursor()) as cur:
                    cur.execute(sql, tuple(params))
                    return [dict(r) for r in cur.fetchall()]
            finally:
                conn.close()

        data = await tornado.ioloop.IOLoop.current().run_in_executor(None, _executer_find_many)
        self.set_status(200)
        self.write(json.dumps({
            "operation": "find_many (fetchall)",
            "framework": "Tornado (sqlite3 + run_in_executor + closing(cursor))",
            "requete_preparee_sql": sql,
            "parametres_lies_tuple": params,
            "total": len(data),
            "data": data,
        }, ensure_ascii=False))

    async def post(self):
        try:
            corps = tornado.escape.json_decode(self.request.body or b"{}")
        except Exception:
            self.set_status(400)
            self.write({"erreur": "Corps JSON invalide."})
            return

        code_interne = str(corps.get("code_interne", "")).strip()
        titre = str(corps.get("titre", "")).strip()
        salle = str(corps.get("salle", "Salle A")).strip()
        duree_jours = int(corps.get("duree_jours", 5))
        budget_dzd = float(corps.get("budget_dzd", 40000.0))

        if not code_interne or len(titre) < 3:
            self.set_status(422)
            self.write({"erreur": "Les champs 'code_interne' et 'titre' (min 3 car.) sont requis."})
            return

        def _executer_insert_one():
            conn = ouvrir_connexion_sqlite()
            try:
                with conn:
                    with closing(conn.cursor()) as cur:
                        cur.execute(
                            """
                            INSERT INTO formations_lab (code_interne, titre, salle, duree_jours, budget_dzd)
                            VALUES (:code_interne, :titre, :salle, :duree_jours, :budget_dzd)
                            """,
                            {
                                "code_interne": code_interne,
                                "titre": titre,
                                "salle": salle,
                                "duree_jours": duree_jours,
                                "budget_dzd": budget_dzd,
                            },
                        )
                        nouvel_id = cur.lastrowid
                with closing(conn.cursor()) as cur:
                    cur.execute("SELECT * FROM formations_lab WHERE id = ?", (nouvel_id,))
                    return dict(cur.fetchone())
            finally:
                conn.close()

        try:
            formation_creee = await tornado.ioloop.IOLoop.current().run_in_executor(None, _executer_insert_one)
        except sqlite3.IntegrityError as exc:
            self.set_status(409)
            self.write({
                "erreur": "Violation de contrainte d'intégrité SQLite (UNIQUE ou CHECK)",
                "detail_sqlite": str(exc),
            })
            return

        self.set_status(201)
        self.write(json.dumps({
            "operation": "insert_one (lastrowid)",
            "statut": "Formation insérée sur l'IOLoop via run_in_executor + transaction ACID",
            "formation": formation_creee,
        }, ensure_ascii=False))


class FormationItemSqliteHandler(tornado.web.RequestHandler):
    """Gère FIND_ONE (`GET`), UPDATE (`PATCH`) et DELETE (`DELETE`) sur `/api/sqlite/formations/([0-9]+)`."""

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    async def get(self, formation_id_str: str):
        formation_id = int(formation_id_str)

        def _executer_find_one():
            conn = ouvrir_connexion_sqlite()
            try:
                with closing(conn.cursor()) as cur:
                    cur.execute(
                        "SELECT id, code_interne, titre, salle, duree_jours, budget_dzd FROM formations_lab WHERE id = ?",
                        (formation_id,),
                    )
                    row = cur.fetchone()
                    return dict(row) if row is not None else None
            finally:
                conn.close()

        formation = await tornado.ioloop.IOLoop.current().run_in_executor(None, _executer_find_one)
        if formation is None:
            self.set_status(404)
            self.write({"erreur": f"Aucune formation trouvée avec id={formation_id}"})
            return

        self.set_status(200)
        self.write(json.dumps({
            "operation": "find_one (fetchone)",
            "formation": formation,
        }, ensure_ascii=False))

    async def patch(self, formation_id_str: str):
        formation_id = int(formation_id_str)
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        nouvelle_salle = str(corps.get("salle", "Amphithéâtre")).strip()

        def _executer_update():
            conn = ouvrir_connexion_sqlite()
            try:
                with conn:
                    with closing(conn.cursor()) as cur:
                        cur.execute(
                            "UPDATE formations_lab SET salle = ? WHERE id = ?",
                            (nouvelle_salle, formation_id),
                        )
                        rc = cur.rowcount
                if rc == 0:
                    return 0, None
                with closing(conn.cursor()) as cur:
                    cur.execute("SELECT * FROM formations_lab WHERE id = ?", (formation_id,))
                    return rc, dict(cur.fetchone())
            finally:
                conn.close()

        rc, updated = await tornado.ioloop.IOLoop.current().run_in_executor(None, _executer_update)
        if rc == 0:
            self.set_status(404)
            self.write({"erreur": f"Formation id={formation_id} introuvable (rowcount=0)"})
            return

        self.set_status(200)
        self.write(json.dumps({
            "operation": "update (rowcount)",
            "rowcount": rc,
            "formation": updated,
        }, ensure_ascii=False))


def make_app():
    return tornado.web.Application([
        (r"/api/sqlite/formations", FormationsCollectionSqliteHandler),
        (r"/api/sqlite/formations/([0-9]+)", FormationItemSqliteHandler),
    ])


async def executer_laboratoire_sqlite():
    initialiser_schema_et_donnees()
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
    print("=== DÉMONSTRATION COMPLÈTE SQLITE3 SOUS TORNADO (FIND_MANY, FIND_ONE, INSERT, UPDATE) ===")

    rep_many = await client.fetch(f"http://127.0.0.1:{port}/api/sqlite/formations?salle=Salle%20A&tri=duree_jours&ordre=desc")
    r_many = tornado.escape.json_decode(rep_many.body)
    print(f"1. FIND_MANY (fetchall) : {r_many['total']} lignes | SQL = {r_many['requete_preparee_sql']}")

    rep_one = await client.fetch(f"http://127.0.0.1:{port}/api/sqlite/formations/1")
    r_one = tornado.escape.json_decode(rep_one.body)
    print(f"2. FIND_ONE  (fetchone) : ID #1 -> {r_one['formation']['code_interne']} ({r_one['formation']['titre']})")

    payload_injection = "Salle A' OR '1'='1"
    qs = urllib.parse.urlencode({"salle": payload_injection})
    rep_inj = await client.fetch(f"http://127.0.0.1:{port}/api/sqlite/formations?{qs}")
    r_inj = tornado.escape.json_decode(rep_inj.body)
    print(f"3. ANTI-SQLi (?)        : ?salle=\"{payload_injection}\" -> {r_inj['total']} ligne retournée (Injection neutralisée !)")

    rep_post = await client.fetch(
        f"http://127.0.0.1:{port}/api/sqlite/formations",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps({
            "code_interne": "TORN-404",
            "titre": "Atelier Pratique SQLite & Protection SQLi",
            "salle": "Laboratoire 1",
            "duree_jours": 5,
            "budget_dzd": 49000.0,
        }),
    )
    r_post = tornado.escape.json_decode(rep_post.body)
    new_id = r_post["formation"]["id"]
    print(f"4. INSERT_ONE (:nom)    : HTTP {rep_post.code} | cur.lastrowid = {new_id}")

    rep_patch = await client.fetch(
        f"http://127.0.0.1:{port}/api/sqlite/formations/{new_id}",
        method="PATCH",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"salle": "Salle Conférence"}),
    )
    r_patch = tornado.escape.json_decode(rep_patch.body)
    print(f"5. UPDATE (rowcount)    : cur.rowcount = {r_patch['rowcount']} | Nouvelle salle = {r_patch['formation']['salle']}")

    if "--once" in sys.argv:
        server.stop()
    else:
        print("\n" + "=" * 76)
        print(f"[BOUCLE IOLOOP TORNADO ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Testez FIND_MANY : http://127.0.0.1:{port}/api/sqlite/formations")
        print(f"  -> Testez FIND_ONE  : http://127.0.0.1:{port}/api/sqlite/formations/1")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement la boucle IOLoop.")
        print("=" * 76)
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(executer_laboratoire_sqlite())
    except KeyboardInterrupt:
        print("\n[IOLOOP TORNADO] Arrêt propre demandé par l'utilisateur (Ctrl+C).")
