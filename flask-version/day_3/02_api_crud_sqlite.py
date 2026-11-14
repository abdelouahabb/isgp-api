# Fichier : day_3/02_api_crud_sqlite.py
# Exécution : .venv/bin/python day_3/02_api_crud_sqlite.py
# Objectif : Persistance relationnelle SQLite complète (GET, POST, PUT, DELETE) :
#   - Requêtes paramétrées (?) neutralisant 100% des Injections SQL
#   - Route Web Jinja2 + Formulaire HTML (request.form -> day_3/templates/catalogue_sqlite.html)
#   - Routes API REST JSON (request.get_json -> jsonify)

import os
import sqlite3
import sys
from flask import Flask, jsonify, render_template, request

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))
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
            ("Architecture des APIs REST & SQLite", 5, "Salle A"),
        )
    conn.commit()
    conn.close()


init_db()


# 1. ROUTE WEB JINJA2 + FORMULAIRE HTML (<form method="POST"> -> request.form -> SQLite)
@app.route("/formations-sqlite", methods=["GET", "POST"])
def page_catalogue_sqlite():
    message = None
    if request.method == "POST":
        # Lecture des champs du formulaire HTML via request.form
        titre = request.form.get("titre", "").strip()
        duree_jours = request.form.get("duree_jours", default=5, type=int)
        salle = request.form.get("salle", "Salle A").strip() or "Salle A"
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
    # Rendu via le template day_3/templates/catalogue_sqlite.html (zéro HTML en dur !)
    return render_template(
        "catalogue_sqlite.html",
        formations=[dict(r) for r in lignes],
        message=message,
    ), 200


# 2. ROUTES API REST JSON (GET, POST, PUT, DELETE)
@app.route("/api/formations", methods=["GET"])
def lister():
    conn = get_db()
    lignes = conn.execute("SELECT * FROM formations ORDER BY id ASC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in lignes]), 200


@app.route("/api/formations", methods=["POST"])
def creer_formation_sqlite():
    # Accepte aussi bien un corps JSON (request.get_json) qu'un formulaire (request.form)
    source = (request.get_json(silent=True) or {}) if request.is_json else request.form
    titre = str(source.get("titre", "")).strip()
    if len(titre) < 3:
        return jsonify({"erreur": "Le champ 'titre' (min 3 caractères) est requis"}), 422
    duree_jours = int(source.get("duree_jours", 5))
    salle = str(source.get("salle", "Salle A")).strip()

    conn = get_db()
    cur = conn.execute(
        "INSERT INTO formations (titre, duree_jours, salle) VALUES (?, ?, ?)",
        (titre, duree_jours, salle),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return jsonify({"id": new_id, "titre": titre, "duree_jours": duree_jours, "salle": salle}), 201


@app.route("/api/formations/<int:id>", methods=["PUT"])
def modifier_formation(id):
    corps = request.get_json(silent=True) or {}
    conn = get_db()
    actuelle = conn.execute("SELECT * FROM formations WHERE id = ?", (id,)).fetchone()
    if not actuelle:
        conn.close()
        return jsonify({"erreur": f"Formation ID {id} introuvable"}), 404

    titre = corps.get("titre", actuelle["titre"])
    salle = corps.get("salle", actuelle["salle"])
    conn.execute("UPDATE formations SET titre = ?, salle = ? WHERE id = ?", (titre, salle, id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Mise à jour effectuée", "id": id, "titre": titre, "salle": salle}), 200


@app.route("/api/formations/<int:id>", methods=["DELETE"])
def supprimer_formation(id):
    conn = get_db()
    cur = conn.execute("DELETE FROM formations WHERE id = ?", (id,))
    conn.commit()
    supprime = cur.rowcount > 0
    conn.close()
    if not supprime:
        return jsonify({"erreur": f"Formation ID {id} introuvable"}), 404
    return jsonify({"message": f"Formation ID {id} supprimée"}), 200


@app.route("/", methods=["GET"])
def index_crud_sqlite():
    return render_template("index_02_crud_sqlite.html"), 200


if __name__ == "__main__":
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        print("=== 1. AJOUT VIA FORMULAIRE HTML (POST /formations-sqlite -> request.form) ===")
        rep_form = client.post(
            "/formations-sqlite",
            data={"titre": "Sécurité SQL & Jinja2", "duree_jours": "4", "salle": "Salle B"},
        )
        for l in rep_form.get_data(as_text=True).splitlines():
            if "notification-succes" in l or "Sécurité SQL" in l:
                print("  ->", l.strip())

        print("\n=== 2. LECTURE DU CATALOGUE SQLITE (GET /api/formations -> JSON) ===")
        print(client.get("/api/formations").get_json())
    if "--once" not in sys.argv:
        import socket as _sock
        port = int(os.environ.get("PORT", 5001))
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
            if _s.connect_ex(("127.0.0.1", port)) == 0:
                _s2 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                _s2.bind(("127.0.0.1", 0))
                port = _s2.getsockname()[1]
                _s2.close()
        print("\n" + "=" * 76)
        print(f"[SERVEUR WSGI FLASK ACTIF] Serveur en écoute sur http://127.0.0.1:{port}")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print(f"  -> Testez les routes en direct sur http://127.0.0.1:{port} (navigateur, curl, Postman)")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
