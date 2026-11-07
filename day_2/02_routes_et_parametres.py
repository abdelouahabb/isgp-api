# Fichier : day_2/02_routes_et_parametres.py
# Exécution : .venv/bin/python day_2/02_routes_et_parametres.py
# Tests :
#   http://127.0.0.1:5001/api/saluer/Amine
#   http://127.0.0.1:5001/api/calcul-tva?ht=2500&taux=19

from flask import Flask, jsonify, request

app = Flask(__name__)

# 1. Paramètre de chemin (<prenom>)
@app.route("/api/saluer/<prenom>", methods=["GET"])
def saluer_stagiaire(prenom):
    return jsonify({
        "message": f"Bienvenue au séminaire API, {prenom}",
        "longueur_chaine": len(prenom)
    }), 200

# 2. Paramètres de requête après ? (request.args)
@app.route("/api/calcul-tva", methods=["GET"])
def calculer_tva():
    prix_ht = float(request.args.get("ht", 1000))
    taux = float(request.args.get("taux", 19))
    montant_tva = prix_ht * (taux / 100)
    return jsonify({
        "prix_ht": prix_ht,
        "taux_tva": taux,
        "montant_tva": round(montant_tva, 2),
        "prix_ttc": round(prix_ht + montant_tva, 2)
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
