# Fichier : day_3/01_api_crud_memoire.py
# Exécution : .venv/bin/python day_3/01_api_crud_memoire.py
# Objectif : Validation stricte des champs entrants et réponses d'erreur RFC 7807

from flask import Flask, jsonify, request

app = Flask(__name__)

formations = [
    {"id": 1, "titre": "Architecture des APIs REST", "duree_jours": 5, "salle": "Salle A"},
    {"id": 2, "titre": "Python pour l'Entreprise", "duree_jours": 3, "salle": "Salle B"}
]

def valider_payload_formation(corps):
    """Vérifie le schéma, les types et les bornes métier du JSON reçu."""
    erreurs = {}
    if not isinstance(corps, dict):
        return {"_corps": "Un objet JSON valide est requis."}

    titre = str(corps.get("titre", "")).strip()
    if len(titre) < 3 or len(titre) > 120:
        erreurs["titre"] = "Le titre est obligatoire et doit contenir entre 3 et 120 caractères."

    try:
        duree = int(corps.get("duree_jours", 5))
        if duree < 1 or duree > 30:
            erreurs["duree_jours"] = "La durée doit être comprise entre 1 et 30 jours."
    except (ValueError, TypeError):
        erreurs["duree_jours"] = "La durée doit être un nombre entier."

    return erreurs

@app.route("/api/v1/formations", methods=["GET"])
def lister_formations():
    return jsonify({"total": len(formations), "donnees": formations}), 200

@app.route("/api/v1/formations", methods=["POST"])
def creer_formation():
    corps = request.get_json(silent=True)
    erreurs = valider_payload_formation(corps)
    if erreurs:
        # Format d'erreur structuré inspiré du standard RFC 7807 (Problem Details)
        return jsonify({
            "type": "https://isgp.dz/erreurs/validation-echouee",
            "title": "Données d'entrée invalides",
            "status": 422,
            "champs_en_erreur": erreurs
        }), 422

    nouvel_id = max([f["id"] for f in formations], default=0) + 1
    nouvelle = {
        "id": nouvel_id,
        "titre": str(corps["titre"]).strip(),
        "duree_jours": int(corps.get("duree_jours", 5)),
        "salle": str(corps.get("salle", "Salle Principale")).strip()
    }
    formations.append(nouvelle)
    return jsonify({"message": "Formation créée", "formation": nouvelle}), 201

if __name__ == "__main__":
    import sys
    if "--serve" in sys.argv:
        app.run(host="0.0.0.0", port=5001, debug=True)
    else:
        with app.test_client() as client:
            rep_err = client.post("/api/v1/formations", json={"titre": "AB", "duree_jours": 99})
            print("1. Rejet RFC 7807 (HTTP 422) :", rep_err.status_code, rep_err.get_json())
            rep_ok = client.post("/api/v1/formations", json={"titre": "Sécurité OWASP API", "duree_jours": 4})
            print("2. Création valide (HTTP 201) :", rep_ok.status_code, rep_ok.get_json())
