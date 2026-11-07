# Fichier : day_3/01_api_crud_memoire.py
# Exécution : .venv/bin/python day_3/01_api_crud_memoire.py

from flask import Flask, jsonify, request

app = Flask(__name__)

formations = [
    {"id": 1, "titre": "Architecture des APIs REST", "duree_jours": 5, "salle": "Salle A"},
    {"id": 2, "titre": "Python pour l'Entreprise", "duree_jours": 3, "salle": "Salle B"}
]

@app.route("/api/formations", methods=["GET"])
def lister_formations():
    return jsonify({"total": len(formations), "donnees": formations}), 200

@app.route("/api/formations", methods=["POST"])
def creer_formation():
    corps = request.get_json(silent=True)
    if not corps or "titre" not in corps:
        return jsonify({"erreur": "Le champ 'titre' est obligatoire"}), 400

    nouvel_id = max([f["id"] for f in formations], default=0) + 1
    nouvelle = {
        "id": nouvel_id,
        "titre": corps["titre"],
        "duree_jours": int(corps.get("duree_jours", 5)),
        "salle": corps.get("salle", "Salle Principale")
    }
    formations.append(nouvelle)
    return jsonify({"message": "Formation créée", "formation": nouvelle}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
