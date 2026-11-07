# Fichier : day_3/02_api_crud_sqlite.py
# Exécution : .venv/bin/python day_3/02_api_crud_sqlite.py

import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_FILE = "day_3_formations.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS formations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            duree_jours INTEGER DEFAULT 5,
            salle TEXT DEFAULT 'Salle A'
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/api/formations", methods=["GET"])
def lister():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    lignes = conn.execute("SELECT * FROM formations ORDER BY id ASC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in lignes]), 200

@app.route("/api/formations/<int:id>", methods=["PUT"])
def modifier_formation(id):
    corps = request.get_json(silent=True) or {}
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
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
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute("DELETE FROM formations WHERE id = ?", (id,))
    conn.commit()
    supprime = cur.rowcount > 0
    conn.close()
    if not supprime:
        return jsonify({"erreur": f"Formation ID {id} introuvable"}), 404
    return jsonify({"message": f"Formation ID {id} supprimée"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
