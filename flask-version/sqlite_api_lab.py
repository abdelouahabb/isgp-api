"""
================================================================================
LABORATOIRE SQLITE & SÉCURITÉ SQL — ÉDITION FLASK (WSGI)
================================================================================
Ce script autonome illustre l'intégration professionnelle de SQLite3 dans une
API REST Flask sans aucune dépendance externe (bibliothèque standard sqlite3) :
  1. Cycle de vie de connexion par requête HTTP via `flask.g` et `@app.teardown_appcontext`
  2. Activation de `PRAGMA journal_mode = WAL` et `PRAGMA foreign_keys = ON`
  3. Requêtes paramétrées positionnelles (`?` — style qmark) et nommées (`:nom` — style named)
  4. Neutralisation d'une attaque par Injection SQL (`' OR '1'='1`)
  5. Liste blanche (Allowlist) pour sécuriser les identifiants SQL (`ORDER BY`)
================================================================================
"""

import os
import socket as _sock
import sqlite3
import sys
import tempfile
from flask import Flask, g, jsonify, request

app = Flask(__name__)
DB_FILE = os.path.join(tempfile.gettempdir(), "isgp_sqlite_lab_flask.db")


# ==============================================================================
# 1. CYCLE DE VIE DE LA CONNEXION SQLITE DANS FLASK (g.db + teardown_appcontext)
# ==============================================================================
def get_db() -> sqlite3.Connection:
    """Ouvre une connexion SQLite attachée au contexte de la requête HTTP courante (g)."""
    if "db" not in g:
        conn = sqlite3.connect(DB_FILE, timeout=5.0)
        # sqlite3.Row permet d'accéder aux colonnes par leur nom et de convertir en dict(row)
        conn.row_factory = sqlite3.Row
        # Bonnes pratiques SQLite pour une API Web :
        conn.execute("PRAGMA journal_mode = WAL;")   # Lectures/écritures concurrentes sans blocage
        conn.execute("PRAGMA foreign_keys = ON;")    # Application stricte des clés étrangères
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """Garantit la fermeture systématique de la connexion SQLite à la fin de chaque requête."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def initialiser_schema_et_donnees():
    """Crée la table et insère un jeu d'essai initial de manière transactionnelle."""
    conn = sqlite3.connect(DB_FILE)
    with conn:  # Le bloc `with conn:` exécute automatiquement COMMIT (ou ROLLBACK si exception)
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
            ("API-101", "Architecture REST & Flask WSGI", "Salle A", 5, 45000.0),
            ("SEC-202", "Sécurité des APIs, JWT & Requêtes Préparées", "Salle B", 4, 52000.0),
            ("SQL-303", "Persistance SQLite WAL & Modélisation Relationnelle", "Salle A", 3, 38000.0),
        ]
        # executemany() compile la requête préparée une seule fois pour tout le lot
        conn.executemany(
            """
            INSERT INTO formations_lab (code_interne, titre, salle, duree_jours, budget_dzd)
            VALUES (?, ?, ?, ?, ?)
            """,
            donnees_initiales,
        )
    conn.close()


# ==============================================================================
# 2. ROUTES API CRUD AVEC REQUÊTES PARAMÉTRÉES (`?` ET `:nom`) + LISTE BLANCHE
# ==============================================================================
COLONNES_TRI_AUTORISEES = {
    "id": "id",
    "duree_jours": "duree_jours",
    "budget_dzd": "budget_dzd",
    "titre": "titre",
}


@app.route("/api/sqlite/formations", methods=["GET"])
def lister_formations():
    """
    Exemple combinant :
    - Marqueurs positionnels `?` (style qmark DB-API 2.0) pour les valeurs de filtrage
    - Liste blanche stricte pour la clause `ORDER BY` (qu'un `?` ne peut pas paramétrer)
    """
    salle = request.args.get("salle")
    min_jours = request.args.get("min_jours", default=1, type=int)
    tri_demande = request.args.get("tri", "id")
    ordre_demande = request.args.get("ordre", "asc").lower()

    # SÉCURITÉ : Les marqueurs `?` ne peuvent remplacer que des VALEURS (littéraux),
    # jamais un nom de colonne ou de table. On utilise donc une liste blanche stricte :
    colonne_sure = COLONNES_TRI_AUTORISEES.get(tri_demande, "id")
    direction_sure = "DESC" if ordre_demande == "desc" else "ASC"

    db = get_db()
    sql = "SELECT id, code_interne, titre, salle, duree_jours, budget_dzd FROM formations_lab WHERE duree_jours >= ?"
    params = [min_jours]

    if salle:
        sql += " AND salle = ?"
        params.append(salle)

    sql += f" ORDER BY {colonne_sure} {direction_sure}"
    lignes = db.execute(sql, tuple(params)).fetchall()

    return jsonify({
        "framework": "Flask (sqlite3 + g.db)",
        "requete_preparee_sql": sql,
        "parametres_lies_tuple": params,
        "total": len(lignes),
        "data": [dict(r) for r in lignes],
    }), 200


@app.route("/api/sqlite/formations", methods=["POST"])
def creer_formation():
    """
    Exemple utilisant les marqueurs nommés `:nom` (style named supporté nativement par sqlite3)
    et une transaction atomique `with db:`.
    """
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
        with db:
            cur = db.execute(
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

    # Attention au piège du tuple à 1 seul élément en Python : `(nouvel_id,)` avec la virgule !
    ligne = db.execute("SELECT * FROM formations_lab WHERE id = ?", (nouvel_id,)).fetchone()
    return jsonify({
        "statut": "Formation insérée avec transaction ACID",
        "formation": dict(ligne),
    }), 201


if __name__ == "__main__":
    initialiser_schema_et_donnees()
    print("=== DÉMONSTRATION SQLITE3 SOUS FLASK (REQUÊTES PRÉPARÉES `?` & `:nom`) ===")
    with app.test_client() as client:
        # 1. Lecture normale
        r1 = client.get("/api/sqlite/formations?salle=Salle%20A&tri=duree_jours&ordre=desc").get_json()
        print(f"1. SELECT paramétré (?) : {r1['total']} lignes | SQL = {r1['requete_preparee_sql']}")
        print(f"   Paramètres liés      : {r1['parametres_lies_tuple']}")

        # 2. Tentative d'Injection SQL classique dans le paramètre ?salle=
        payload_injection = "Salle A' OR '1'='1"
        r_inj = client.get("/api/sqlite/formations", query_string={"salle": payload_injection}).get_json()
        print(f"\n2. Test anti-Injection SQL avec ?salle=\"{payload_injection}\" :")
        print(f"   -> Lignes retournées : {r_inj['total']} (Attendu: 0 — l'injection est traitée comme un simple texte littéral !)")

        # 3. Insertion avec marqueurs nommés (:nom)
        r_post = client.post(
            "/api/sqlite/formations",
            json={
                "code_interne": "FLASK-404",
                "titre": " Atelier Pratique SQLite & Protection SQLi",
                "salle": "Laboratoire 1",
                "duree_jours": 5,
                "budget_dzd": 49000.0,
            },
        )
        print(f"\n3. INSERT paramétré (:nom) -> Statut HTTP {r_post.status_code} | ID créé = {r_post.get_json()['formation']['id']}")

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
        print(f"  -> Testez : http://127.0.0.1:{port}/api/sqlite/formations")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
