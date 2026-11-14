# Fichier : zero_to_hero/etape_04_persistance_sqlite_wal.py
# Étape 4/6 : Persistance Relationnelle SQLite (WAL, Foreign Keys, busy_timeout) & Cycle flask.g
# Exécution : .venv/bin/python flask-version/zero_to_hero/etape_04_persistance_sqlite_wal.py

import json
import math
import os
import sqlite3
import sys
from flask import Flask, Response, g, jsonify, render_template, request

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DOSSIER_COURANT, "isgp_zero_to_hero.db")
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))
CHAMPS_TRI = {"id", "duree_jours", "tarif_dzd", "titre"}


def get_db():
    """Ouvre une connexion SQLite unique par requete HTTP dans flask.g avec PRAGMAs industriels."""
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA busy_timeout=5000;")
        g.db = conn
    return g.db


@app.teardown_appcontext
def fermer_db(exception=None):
    """Ferme proprement le descripteur SQLite a la fin de chaque contexte de requete WSGI."""
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS formations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                titre TEXT NOT NULL,
                domaine TEXT NOT NULL DEFAULT 'Backend',
                duree_jours INTEGER NOT NULL CHECK(duree_jours BETWEEN 1 AND 30),
                tarif_dzd INTEGER NOT NULL CHECK(tarif_dzd >= 0)
            )
        """)
        if db.execute("SELECT COUNT(*) FROM formations").fetchone()[0] == 0:
            semences = [
                ("API-101", "Fondamentaux HTTP/1.1 & JSON", "Architecture", 3, 45000),
                ("FLK-201", "Services Web RESTful avec Flask", "Backend", 5, 65000),
                ("SQL-301", "Persistance SQLite WAL & ACID", "Data", 4, 58000),
                ("SEC-401", "Securite Bearer HMAC, Cookies & RBAC", "Securite", 5, 75000),
            ]
            db.executemany(
                "INSERT INTO formations (code, titre, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
                semences,
            )
        db.commit()


def erreur_rfc7807(status, title, detail, erreurs=None):
    prob = {"type": "https://api.isgp.dz/erreurs/sqlite", "title": title, "status": status, "detail": detail}
    if erreurs:
        prob["errors"] = erreurs
    return Response(json.dumps(prob, ensure_ascii=False), status=status, mimetype="application/problem+json")


def valider_formation(corps, partiel=False):
    if not isinstance(corps, dict):
        return {"_corps": "Objet JSON requis."}
    err = {}
    if not partiel or "code" in corps:
        if not (3 <= len(str(corps.get("code", "")).strip()) <= 16):
            err["code"] = "Code requis (3 a 16 caracteres)."
    if not partiel or "titre" in corps:
        if not (4 <= len(str(corps.get("titre", "")).strip()) <= 120):
            err["titre"] = "Titre requis (4 a 120 caracteres)."
    if not partiel or "duree_jours" in corps:
        try:
            if not (1 <= int(corps.get("duree_jours")) <= 30):
                err["duree_jours"] = "Duree entre 1 et 30 jours."
        except (TypeError, ValueError):
            err["duree_jours"] = "Entier requis."
    if not partiel or "tarif_dzd" in corps:
        try:
            if int(corps.get("tarif_dzd")) < 0:
                err["tarif_dzd"] = "Tarif positif requis."
        except (TypeError, ValueError):
            err["tarif_dzd"] = "Entier requis."
    return err


@app.route("/", methods=["GET"])
def page_sqlite():
    return render_template("etape_04_sqlite.html", etape="Etape 4/6 — Persistance SQLite WAL & Cycle flask.g"), 200


@app.route("/api/v1/sqlite-pragmas", methods=["GET"])
def inspecter_pragmas():
    db = get_db()
    return jsonify({
        "journal_mode": db.execute("PRAGMA journal_mode;").fetchone()[0],
        "foreign_keys": db.execute("PRAGMA foreign_keys;").fetchone()[0],
        "busy_timeout_ms": db.execute("PRAGMA busy_timeout;").fetchone()[0],
        "fichier_db": os.path.basename(DB_PATH),
    }), 200


@app.route("/api/v1/formations", methods=["GET"])
def lister_formations():
    db = get_db()
    domaine = request.args.get("domaine", "").strip()
    tri = request.args.get("tri", "id").strip()
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(20, max(1, request.args.get("limit", 10, type=int)))

    sens = "DESC" if tri.startswith("-") else "ASC"
    col = tri.lstrip("-") if tri.lstrip("-") in CHAMPS_TRI else "id"
    clause = "WHERE lower(domaine) = lower(?)" if domaine else ""
    params = (domaine,) if domaine else ()

    total = db.execute(f"SELECT COUNT(*) FROM formations {clause}", params).fetchone()[0]
    lignes = db.execute(
        f"SELECT * FROM formations {clause} ORDER BY {col} {sens} LIMIT ? OFFSET ?",
        (*params, limit, (page - 1) * limit),
    ).fetchall()
    return jsonify({
        "meta": {"page": page, "total": total, "total_pages": max(1, math.ceil(total / limit))},
        "data": [dict(r) for r in lignes],
    }), 200


@app.route("/api/v1/formations", methods=["POST"])
def creer_formation():
    corps = request.get_json(silent=True)
    err = valider_formation(corps)
    if err:
        return erreur_rfc7807(422, "Validation echouee", "Champs invalides.", err)
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO formations (code, titre, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
            (
                str(corps["code"]).strip().upper(),
                str(corps["titre"]).strip(),
                str(corps.get("domaine", "Backend")).strip() or "Backend",
                int(corps["duree_jours"]),
                int(corps["tarif_dzd"]),
            ),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return erreur_rfc7807(409, "Conflit d'unicite SQL", "Ce code de formation existe deja.")
    creee = dict(db.execute("SELECT * FROM formations WHERE id = ?", (cur.lastrowid,)).fetchone())
    return jsonify({"data": creee}), 201


@app.route("/api/v1/formations/<int:formation_id>", methods=["DELETE"])
def supprimer_formation(formation_id):
    db = get_db()
    cur = db.execute("DELETE FROM formations WHERE id = ?", (formation_id,))
    db.commit()
    if cur.rowcount == 0:
        return erreur_rfc7807(404, "Introuvable", f"Formation #{formation_id} absente.")
    return jsonify({"statut": "supprime", "id": formation_id}), 200


init_db()

if __name__ == "__main__":
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        prag = client.get("/api/v1/sqlite-pragmas").get_json()
        assert prag["journal_mode"].lower() == "wal" and prag["foreign_keys"] == 1
        code_test = "TST-404"
        r_post = client.post("/api/v1/formations", json={"code": code_test, "titre": "Test SQLite WAL", "domaine": "Data", "duree_jours": 3, "tarif_dzd": 49000})
        assert r_post.status_code == 201
        fid = r_post.get_json()["data"]["id"]
        assert client.delete(f"/api/v1/formations/{fid}").status_code == 200
        print("[ETAPE 04 OK] SQLite WAL + foreign_keys=ON + busy_timeout=5000 + Teardown flask.g valides.")

    if "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        print(f"[ETAPE 04] Portail SQLite WAL actif sur http://127.0.0.1:{port}")
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
