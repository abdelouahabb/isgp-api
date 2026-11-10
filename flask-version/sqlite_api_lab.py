"""
================================================================================
MANUEL & LABORATOIRE SQLITE3 — ÉDITION FLASK (WSGI, g.db & contextlib.closing)
================================================================================
Ce script autonome de référence illustre toutes les opérations SQLite3 dans une
API REST Flask sans dépendance externe (bibliothèque standard sqlite3) :
  1. Connexion par requête HTTP (`flask.g` + `@app.teardown_appcontext`)
  2. Pragmas de production (`journal_mode=WAL`, `synchronous=NORMAL`, `foreign_keys=ON`, `busy_timeout=5000`)
  3. Fermeture explicite et déterministe du curseur avec `contextlib.closing(conn.cursor())`
  4. CRUD Complet :
     - `find_many` (`fetchall()` / `fetchmany()`) avec filtres `?` et liste blanche `ORDER BY`
     - `find_one` (`fetchone()`) avec gestion du tuple à 1 élément `(id,)` et statut 404
     - `insert_one` avec marqueurs nommés `:nom`, `BEGIN IMMEDIATE`, et `cur.lastrowid`
     - `insert_many` en lot atomique avec `cur.executemany()`
     - `update` et `delete` avec inspection de `cur.rowcount`
================================================================================
"""

from contextlib import closing
import os
import socket as _sock
import sqlite3
import sys
import tempfile
from flask import Flask, g, jsonify, request

app = Flask(__name__)
DB_FILE = os.path.join(tempfile.gettempdir(), "isgp_sqlite_lab_flask.db")


# ==============================================================================
# 1. CONNEXION SQLITE3, PRAGMAS DE PRODUCTION & FERMETURE GARANTIE
# ==============================================================================
def get_db() -> sqlite3.Connection:
    """Ouvre une connexion SQLite attachée au contexte de la requête HTTP courante (flask.g)."""
    if "db" not in g:
        conn = sqlite3.connect(DB_FILE, timeout=5.0)
        conn.row_factory = sqlite3.Row
        # Pragmas recommandés pour une API Web multi-workers :
        conn.execute("PRAGMA journal_mode = WAL;")      # Lectures/écritures concurrentes
        conn.execute("PRAGMA synchronous = NORMAL;")    # Sécurisé en mode WAL et 5x plus rapide que FULL
        conn.execute("PRAGMA foreign_keys = ON;")       # Intégrité référentielle activée
        conn.execute("PRAGMA busy_timeout = 5000;")     # Attente max de 5s si verrou d'écriture actif
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """Ferme systématiquement la connexion SQLite à la fin de la requête HTTP."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def initialiser_schema_et_donnees():
    """Initialise la table et charge un lot initial via executemany()."""
    conn = sqlite3.connect(DB_FILE)
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
                ("API-101", "Architecture REST & Flask WSGI", "Salle A", 5, 45000.0),
                ("SEC-202", "Sécurité des APIs, JWT & Requêtes Préparées", "Salle B", 4, 52000.0),
                ("SQL-303", "Persistance SQLite WAL & Modélisation Relationnelle", "Salle A", 3, 38000.0),
            ]
            # INSERT_MANY : executemany() compile l'arbre syntaxique SQL une seule fois pour tout le lot
            cur.executemany(
                """
                INSERT INTO formations_lab (code_interne, titre, salle, duree_jours, budget_dzd)
                VALUES (?, ?, ?, ?, ?)
                """,
                lot_initial,
            )
    conn.close()


# ==============================================================================
# 2. OPÉRATIONS FIND_MANY, FIND_ONE, INSERT, UPDATE & DELETE
# ==============================================================================
COLONNES_TRI_AUTORISEES = {
    "id": "id",
    "duree_jours": "duree_jours",
    "budget_dzd": "budget_dzd",
    "titre": "titre",
}


@app.route("/api/sqlite/formations", methods=["GET"])
def lister_formations():
    """FIND_MANY : Lecture multiple via fetchall() (ou fetchmany) avec fermeture explicite du curseur."""
    salle = request.args.get("salle")
    min_jours = request.args.get("min_jours", default=1, type=int)
    tri_demande = request.args.get("tri", "id")
    ordre_demande = request.args.get("ordre", "asc").lower()

    colonne_sure = COLONNES_TRI_AUTORISEES.get(tri_demande, "id")
    direction_sure = "DESC" if ordre_demande == "desc" else "ASC"

    sql = "SELECT id, code_interne, titre, salle, duree_jours, budget_dzd FROM formations_lab WHERE duree_jours >= ?"
    params = [min_jours]
    if salle:
        sql += " AND salle = ?"
        params.append(salle)
    sql += f" ORDER BY {colonne_sure} {direction_sure}"

    db = get_db()
    # Bonne habitude : `with closing(db.cursor()) as cur:` libère immédiatement le pointeur C sqlite3_stmt
    with closing(db.cursor()) as cur:
        cur.execute(sql, tuple(params))
        lignes = [dict(r) for r in cur.fetchall()]

    return jsonify({
        "operation": "find_many (fetchall)",
        "framework": "Flask (sqlite3 + g.db + closing(cursor))",
        "requete_preparee_sql": sql,
        "parametres_lies_tuple": params,
        "total": len(lignes),
        "data": lignes,
    }), 200


@app.route("/api/sqlite/formations/<int:formation_id>", methods=["GET"])
def obtenir_formation(formation_id: int):
    """FIND_ONE : Lecture d'un seul enregistrement via fetchone() et tuple à 1 élément `(formation_id,)`."""
    db = get_db()
    with closing(db.cursor()) as cur:
        # Attention : la virgule dans `(formation_id,)` est obligatoire pour créer un tuple Python !
        cur.execute(
            "SELECT id, code_interne, titre, salle, duree_jours, budget_dzd FROM formations_lab WHERE id = ?",
            (formation_id,),
        )
        ligne = cur.fetchone()

    if ligne is None:
        return jsonify({"erreur": f"Aucune formation trouvée avec id={formation_id}"}), 404

    return jsonify({
        "operation": "find_one (fetchone)",
        "formation": dict(ligne),
    }), 200


@app.route("/api/sqlite/formations", methods=["POST"])
def creer_formation():
    """INSERT_ONE : Insertion paramétrée nommée (`:nom`) dans une transaction atomique."""
    corps = request.get_json(silent=True) or {}
    code_interne = str(corps.get("code_interne", "")).strip()
    titre = str(corps.get("titre", "")).strip()
    salle = str(corps.get("salle", "Salle A")).strip()
    duree_jours = int(corps.get("duree_jours", 5))
    budget_dzd = float(corps.get("budget_dzd", 40000.0))

    if not code_interne or len(titre) < 3:
        return jsonify({"erreur": "Les champs 'code_interne' et 'titre' (min 3 car.) sont requis."}), 422

    db = get_db()
    try:
        with db:  # Transaction ACID : COMMIT automatique à la sortie du bloc, ou ROLLBACK si exception
            with closing(db.cursor()) as cur:
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
    except sqlite3.IntegrityError as exc:
        return jsonify({
            "erreur": "Violation de contrainte d'intégrité SQLite (UNIQUE ou CHECK)",
            "detail_sqlite": str(exc),
        }), 409

    with closing(db.cursor()) as cur:
        cur.execute("SELECT * FROM formations_lab WHERE id = ?", (nouvel_id,))
        ligne = cur.fetchone()

    return jsonify({
        "operation": "insert_one (lastrowid)",
        "statut": "Formation insérée avec transaction ACID",
        "formation": dict(ligne),
    }), 201


@app.route("/api/sqlite/formations/<int:formation_id>", methods=["PATCH"])
def modifier_formation(formation_id: int):
    """UPDATE : Mise à jour avec vérification de `cur.rowcount`."""
    corps = request.get_json(silent=True) or {}
    nouvelle_salle = str(corps.get("salle", "Amphithéâtre")).strip()
    db = get_db()
    with db:
        with closing(db.cursor()) as cur:
            cur.execute(
                "UPDATE formations_lab SET salle = ? WHERE id = ?",
                (nouvelle_salle, formation_id),
            )
            lignes_modifiees = cur.rowcount

    if lignes_modifiees == 0:
        return jsonify({"erreur": f"Formation id={formation_id} introuvable (rowcount=0)"}), 404

    with closing(db.cursor()) as cur:
        cur.execute("SELECT * FROM formations_lab WHERE id = ?", (formation_id,))
        ligne = cur.fetchone()

    return jsonify({
        "operation": "update (rowcount)",
        "rowcount": lignes_modifiees,
        "formation": dict(ligne),
    }), 200


@app.route("/api/sqlite/formations/<int:formation_id>", methods=["DELETE"])
def supprimer_formation(formation_id: int):
    """DELETE : Suppression sécurisée avec vérification de `cur.rowcount`."""
    db = get_db()
    with db:
        with closing(db.cursor()) as cur:
            cur.execute("DELETE FROM formations_lab WHERE id = ?", (formation_id,))
            lignes_supprimees = cur.rowcount

    if lignes_supprimees == 0:
        return jsonify({"erreur": f"Formation id={formation_id} introuvable (rowcount=0)"}), 404

    return jsonify({
        "operation": "delete (rowcount)",
        "rowcount": lignes_supprimees,
        "message": f"Formation #{formation_id} supprimée définitivement.",
    }), 200


if __name__ == "__main__":
    initialiser_schema_et_donnees()
    print("=== DÉMONSTRATION COMPLÈTE SQLITE3 SOUS FLASK (FIND_MANY, FIND_ONE, INSERT, UPDATE, DELETE) ===")
    with app.test_client() as client:
        # 1. FIND_MANY (fetchall)
        r_many = client.get("/api/sqlite/formations?salle=Salle%20A&tri=duree_jours&ordre=desc").get_json()
        print(f"1. FIND_MANY (fetchall) : {r_many['total']} lignes | SQL = {r_many['requete_preparee_sql']}")

        # 2. FIND_ONE (fetchone)
        r_one = client.get("/api/sqlite/formations/1").get_json()
        print(f"2. FIND_ONE  (fetchone) : ID #1 -> {r_one['formation']['code_interne']} ({r_one['formation']['titre']})")

        # 3. Neutralisation d'une attaque par Injection SQL
        payload_injection = "Salle A' OR '1'='1"
        r_inj = client.get("/api/sqlite/formations", query_string={"salle": payload_injection}).get_json()
        print(f"3. ANTI-SQLi (?)        : ?salle=\"{payload_injection}\" -> {r_inj['total']} ligne retournée (Injection neutralisée !)")

        # 4. INSERT_ONE (:nom + lastrowid)
        r_post = client.post(
            "/api/sqlite/formations",
            json={
                "code_interne": "FLASK-404",
                "titre": "Atelier Pratique SQLite & Protection SQLi",
                "salle": "Laboratoire 1",
                "duree_jours": 5,
                "budget_dzd": 49000.0,
            },
        )
        new_id = r_post.get_json()["formation"]["id"]
        print(f"4. INSERT_ONE (:nom)    : HTTP {r_post.status_code} | cur.lastrowid = {new_id}")

        # 5. UPDATE (cur.rowcount)
        r_patch = client.patch(f"/api/sqlite/formations/{new_id}", json={"salle": "Salle Conférence"}).get_json()
        print(f"5. UPDATE (rowcount)    : cur.rowcount = {r_patch['rowcount']} | Nouvelle salle = {r_patch['formation']['salle']}")

    if "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
            if _s.connect_ex(("127.0.0.1", port)) == 0:
                _s2 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                _s2.bind(("127.0.0.1", 0))
                port = _s2.getsockname()[1]
                _s2.close()
        print("\n" + "=" * 76)
        print(f"[SERVEUR WSGI FLASK ACTIF] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Testez FIND_MANY : http://127.0.0.1:{port}/api/sqlite/formations")
        print(f"  -> Testez FIND_ONE  : http://127.0.0.1:{port}/api/sqlite/formations/1")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
