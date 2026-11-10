"""
================================================================================
LABORATOIRE SQLITE & SÉCURITÉ SQL — ÉDITION TORNADO (IOLOOP NON-BLOQUANT)
================================================================================
Ce script autonome illustre l'intégration professionnelle de SQLite3 dans une
API REST Tornado (`tornado.web.RequestHandler`) sans dépendance externe :
  1. Cycle de vie de connexion SQLite dans `RequestHandler` (`prepare` / `on_finish`)
  2. Activation de `PRAGMA journal_mode = WAL` et `PRAGMA foreign_keys = ON`
  3. Exécution via `IOLoop.current().run_in_executor` pour ne jamais bloquer l'IOLoop
  4. Requêtes paramétrées positionnelles (`?` — qmark) et nommées (`:nom` — named)
  5. Neutralisation d'une attaque par Injection SQL (`' OR '1'='1`) & Liste blanche `ORDER BY`
================================================================================
"""

import asyncio
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
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialiser_schema_et_donnees():
    conn = ouvrir_connexion_sqlite()
    with conn:
        conn.execute("DROP TABLE IF EXISTS formations_lab")
        conn.execute(
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
        donnees_initiales = [
            ("API-101", "Architecture REST & Tornado IOLoop", "Salle A", 5, 45000.0),
            ("SEC-202", "Sécurité des APIs, JWT & Requêtes Préparées", "Salle B", 4, 52000.0),
            ("SQL-303", "Persistance SQLite WAL & Modélisation Relationnelle", "Salle A", 3, 38000.0),
        ]
        conn.executemany(
            """
            INSERT INTO formations_lab (code_interne, titre, salle, duree_jours, budget_dzd)
            VALUES (?, ?, ?, ?, ?)
            """,
            donnees_initiales,
        )
    conn.close()


class FormationsSqliteHandler(tornado.web.RequestHandler):
    """
    Handler Tornado démontrant l'usage sécurisé de SQLite3 avec :
    - `run_in_executor` pour déporter l'E/S disque SQLite hors du thread de l'IOLoop
    - les marqueurs `?` (qmark) et `:nom` (named)
    """

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

        def _executer_select():
            conn = ouvrir_connexion_sqlite()
            try:
                rows = conn.execute(sql, tuple(params)).fetchall()
                return [dict(r) for r in rows]
            finally:
                conn.close()

        # Déport de la requête SQLite dans le ThreadPoolExecutor pour garder l'IOLoop non-bloquant
        data = await tornado.ioloop.IOLoop.current().run_in_executor(None, _executer_select)

        self.set_status(200)
        self.write(json.dumps({
            "framework": "Tornado (sqlite3 + run_in_executor)",
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

        def _executer_insert():
            conn = ouvrir_connexion_sqlite()
            try:
                with conn:
                    cur = conn.execute(
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
                row = conn.execute("SELECT * FROM formations_lab WHERE id = ?", (nouvel_id,)).fetchone()
                return dict(row)
            finally:
                conn.close()

        try:
            formation_creee = await tornado.ioloop.IOLoop.current().run_in_executor(None, _executer_insert)
        except sqlite3.IntegrityError as exc:
            self.set_status(409)
            self.write({
                "erreur": "Violation de contrainte d'intégrité SQLite (UNIQUE ou CHECK)",
                "detail_sqlite": str(exc),
            })
            return

        self.set_status(201)
        self.write(json.dumps({
            "statut": "Formation insérée sur l'IOLoop via run_in_executor + transaction ACID",
            "formation": formation_creee,
        }, ensure_ascii=False))


def make_app():
    return tornado.web.Application([
        (r"/api/sqlite/formations", FormationsSqliteHandler),
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
    print("=== DÉMONSTRATION SQLITE3 SOUS TORNADO (RUN_IN_EXECUTOR + `?` & `:nom`) ===")

    rep1 = await client.fetch(f"http://127.0.0.1:{port}/api/sqlite/formations?salle=Salle%20A&tri=duree_jours&ordre=desc")
    r1 = tornado.escape.json_decode(rep1.body)
    print(f"1. SELECT paramétré (?) : {r1['total']} lignes | SQL = {r1['requete_preparee_sql']}")
    print(f"   Paramètres liés      : {r1['parametres_lies_tuple']}")

    payload_injection = "Salle A' OR '1'='1"
    qs = urllib.parse.urlencode({"salle": payload_injection})
    rep_inj = await client.fetch(f"http://127.0.0.1:{port}/api/sqlite/formations?{qs}")
    r_inj = tornado.escape.json_decode(rep_inj.body)
    print(f"\n2. Test anti-Injection SQL avec ?salle=\"{payload_injection}\" :")
    print(f"   -> Lignes retournées : {r_inj['total']} (Attendu: 0 — l'injection est traitée comme un simple texte littéral !)")

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
    print(f"\n3. INSERT paramétré (:nom) -> Statut HTTP {rep_post.code} | ID créé = {r_post['formation']['id']}")

    if "--once" in sys.argv:
        server.stop()
    else:
        print("\n" + "=" * 76)
        print(f"[BOUCLE IOLOOP TORNADO ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Testez : http://127.0.0.1:{port}/api/sqlite/formations")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement la boucle IOLoop.")
        print("=" * 76)
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(executer_laboratoire_sqlite())
    except KeyboardInterrupt:
        print("\n[IOLOOP TORNADO] Arrêt propre demandé par l'utilisateur (Ctrl+C).")
