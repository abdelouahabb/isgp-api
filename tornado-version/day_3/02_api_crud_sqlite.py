# Fichier : day_3/02_api_crud_sqlite.py
# Exécution : .venv/bin/python day_3/02_api_crud_sqlite.py
# Objectif : Persistance relationnelle SQLite complète (GET, POST, PUT, DELETE) dans Tornado :
#   - Requêtes paramétrées (?) neutralisant 100% des Injections SQL
#   - Handler Web tornado.template + Formulaire HTML (self.get_body_argument -> day_3/templates/catalogue_sqlite.html)
#   - Handlers API REST JSON (tornado.escape.json_decode -> self.write)

import asyncio
import json
import os
import sqlite3
import sys
import urllib.parse
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DOSSIER_COURANT, "day_3_formations.db")


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS formations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            duree_jours INTEGER DEFAULT 5,
            salle TEXT DEFAULT 'Salle A'
        )
    """)
    nb = conn.execute("SELECT COUNT(*) FROM formations").fetchone()[0]
    if nb == 0:
        conn.execute(
            "INSERT INTO formations (titre, duree_jours, salle) VALUES (?, ?, ?)",
            ("Architecture des APIs REST Tornado & SQLite", 5, "Salle A"),
        )
    conn.commit()
    conn.close()


init_db()


# 1. HANDLER WEB TORNADO TEMPLATE + FORMULAIRE HTML (<form method="POST"> -> self.get_body_argument -> SQLite)
class CatalogueSqlitePageHandler(tornado.web.RequestHandler):
    def get(self):
        conn = get_db()
        lignes = conn.execute("SELECT * FROM formations ORDER BY id ASC").fetchall()
        conn.close()
        self.render("catalogue_sqlite.html", formations=[dict(r) for r in lignes], message=None)

    def post(self):
        message = None
        titre = self.get_body_argument("titre", "").strip()
        try:
            duree_jours = int(self.get_body_argument("duree_jours", "5"))
        except ValueError:
            duree_jours = 5
        salle = self.get_body_argument("salle", "Salle A").strip() or "Salle A"

        if len(titre) >= 3:
            conn = get_db()
            cur = conn.execute(
                "INSERT INTO formations (titre, duree_jours, salle) VALUES (?, ?, ?)",
                (titre, duree_jours, salle),
            )
            conn.commit()
            message = f"Formation '{titre}' insérée dans SQLite (ID #{cur.lastrowid})"
            conn.close()

        conn = get_db()
        lignes = conn.execute("SELECT * FROM formations ORDER BY id ASC").fetchall()
        conn.close()
        self.render("catalogue_sqlite.html", formations=[dict(r) for r in lignes], message=message)


# 2. HANDLER API REST COLLECTION (/api/formations : GET, POST)
class FormationsSqliteApiHandler(tornado.web.RequestHandler):
    def get(self):
        conn = get_db()
        lignes = conn.execute("SELECT * FROM formations ORDER BY id ASC").fetchall()
        conn.close()
        # Attention : dans Tornado, self.write() n'accepte pas une list Python brute pour des raisons
        # historiques de sécurité JSON, ou on enveloppe dans un dict / json.dumps :
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps([dict(r) for r in lignes], ensure_ascii=False))

    def post(self):
        est_json = "application/json" in self.request.headers.get("Content-Type", "")
        if est_json:
            source = tornado.escape.json_decode(self.request.body or b"{}")
            titre = str(source.get("titre", "")).strip()
            duree_jours = int(source.get("duree_jours", 5))
            salle = str(source.get("salle", "Salle A")).strip()
        else:
            titre = self.get_body_argument("titre", "").strip()
            duree_jours = int(self.get_body_argument("duree_jours", "5"))
            salle = self.get_body_argument("salle", "Salle A").strip()

        if len(titre) < 3:
            self.set_status(422)
            self.write({"erreur": "Le champ 'titre' (min 3 caractères) est requis"})
            return

        conn = get_db()
        cur = conn.execute(
            "INSERT INTO formations (titre, duree_jours, salle) VALUES (?, ?, ?)",
            (titre, duree_jours, salle),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        self.set_status(201)
        self.write({"id": new_id, "titre": titre, "duree_jours": duree_jours, "salle": salle})


# 3. HANDLER API REST RESSOURCE INDIVIDUELLE (/api/formations/([0-9]+) : PUT, DELETE)
class FormationSqliteDetailHandler(tornado.web.RequestHandler):
    def put(self, id_str):
        formation_id = int(id_str)
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        conn = get_db()
        actuelle = conn.execute("SELECT * FROM formations WHERE id = ?", (formation_id,)).fetchone()
        if not actuelle:
            conn.close()
            self.set_status(404)
            self.write({"erreur": f"Formation ID {formation_id} introuvable"})
            return

        titre = corps.get("titre", actuelle["titre"])
        salle = corps.get("salle", actuelle["salle"])
        conn.execute("UPDATE formations SET titre = ?, salle = ? WHERE id = ?", (titre, salle, formation_id))
        conn.commit()
        conn.close()
        self.write({"message": "Mise à jour effectuée", "id": formation_id, "titre": titre, "salle": salle})

    def delete(self, id_str):
        formation_id = int(id_str)
        conn = get_db()
        cur = conn.execute("DELETE FROM formations WHERE id = ?", (formation_id,))
        conn.commit()
        supprime = cur.rowcount > 0
        conn.close()
        if not supprime:
            self.set_status(404)
            self.write({"erreur": f"Formation ID {formation_id} introuvable"})
            return
        self.write({"message": f"Formation ID {formation_id} supprimée"})


class PortailSqliteHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("portail_d3_02.html")


def make_app():
    return tornado.web.Application(
        [
            (r"/", PortailSqliteHandler),
            (r"/formations-sqlite", CatalogueSqlitePageHandler),
            (r"/api/formations", FormationsSqliteApiHandler),
            (r"/api/formations/([0-9]+)", FormationSqliteDetailHandler),
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

    print("=== 1. AJOUT VIA FORMULAIRE HTML (POST /formations-sqlite -> self.get_body_argument) ===")
    rep_form = await client.fetch(
        f"http://127.0.0.1:{port}/formations-sqlite",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=urllib.parse.urlencode({"titre": "Sécurité SQL & Tornado", "duree_jours": "4", "salle": "Salle B"}),
    )
    for l in rep_form.body.decode("utf-8").splitlines():
        if "notification-succes" in l or "Sécurité SQL" in l:
            print("  ->", l.strip())

    print("\n=== 2. LECTURE DU CATALOGUE SQLITE (GET /api/formations -> JSON) ===")
    rep_api = await client.fetch(f"http://127.0.0.1:{port}/api/formations")
    print(tornado.escape.json_decode(rep_api.body))
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
