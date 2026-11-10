# Fichier : day_2/02_routes_et_parametres.py
# Exécution : .venv/bin/python day_2/02_routes_et_parametres.py
# Objectif : Maîtriser les paramètres de chemin (<variable>, <int:id>), la différence avec
#            :variable (Postman/Express) et {variable} (OpenAPI/FastAPI), les paramètres de
#            requête (?ht=2500&taux=19 via request.args) et le rendu Jinja2 dynamique.

import os
import sys
from flask import Flask, jsonify, render_template, request

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))

STAGIAIRES = {
    1: {"id": 1, "prenom": "Yasmine", "nom": "Merabet", "specialite": "Architecture API & Sécurité"},
    2: {"id": 2, "prenom": "Amine", "nom": "Benali", "specialite": "Python, Flask & Bases SQL"},
}


# 1. PARAMÈTRE DE CHEMIN TEXTE (<prenom>) : Syntaxe à chevrons propre à Flask / Werkzeug
#    Attention :
#    - Flask / Django utilisent : <prenom> ou <int:stagiaire_id>
#    - Postman / Express.js utilisent : :prenom ou :stagiaire_id
#    - OpenAPI 3.0 / FastAPI utilisent : {prenom} ou {stagiaire_id}
@app.route("/api/saluer/<prenom>", methods=["GET"])
def saluer_stagiaire(prenom):
    return jsonify({
        "message": f"Bienvenue au séminaire API, {prenom}",
        "longueur_chaine": len(prenom),
        "syntaxe_route_flask": "/api/saluer/<prenom>",
        "equivalent_postman_express": "/api/saluer/:prenom",
        "equivalent_openapi_fastapi": "/api/saluer/{prenom}",
    }), 200


# 2. CONVERTISSEUR TYPÉ (<int:stagiaire_id>) : Rejette automatiquement tout texte non entier en 404
@app.route("/api/v1/stagiaires/<int:stagiaire_id>", methods=["GET"])
def obtenir_stagiaire_json(stagiaire_id):
    stagiaire = STAGIAIRES.get(stagiaire_id)
    if not stagiaire:
        return jsonify({"erreur": f"Stagiaire #{stagiaire_id} introuvable"}), 404
    return jsonify({"data": stagiaire}), 200


# 3. ROUTE WEB DYNAMIQUE JINJA2 : Injecte le stagiaire dans day_2/templates/fiche_stagiaire.html
@app.route("/stagiaires/<int:stagiaire_id>/fiche", methods=["GET"])
def afficher_fiche_stagiaire_html(stagiaire_id):
    stagiaire = STAGIAIRES.get(stagiaire_id)
    if not stagiaire:
        return jsonify({"erreur": f"Stagiaire #{stagiaire_id} introuvable"}), 404
    return render_template("fiche_stagiaire.html", stagiaire=stagiaire), 200


# 4. PARAMÈTRES DE REQUÊTE APRÈS '?' (Query String lue via request.args)
@app.route("/api/calcul-tva", methods=["GET"])
def calculer_tva():
    prix_ht = request.args.get("ht", default=1000.0, type=float)
    taux = request.args.get("taux", default=19.0, type=float)
    montant_tva = prix_ht * (taux / 100.0)
    return jsonify({
        "prix_ht": prix_ht,
        "taux_tva": taux,
        "montant_tva": round(montant_tva, 2),
        "prix_ttc": round(prix_ht + montant_tva, 2),
    }), 200


if __name__ == "__main__":
    with app.test_client() as client:
        print("=== 1. TEST PARAMÈTRE DE CHEMIN (<prenom>) ===")
        print(client.get("/api/saluer/Yasmine").get_json())

        print("\n=== 2. TEST CONVERTISSEUR <int:stagiaire_id> + RENDU JINJA2 ===")
        print(client.get("/stagiaires/1/fiche").get_data(as_text=True).strip())

        print("\n=== 3. TEST QUERY PARAMETERS (?ht=2500&taux=19 via request.args) ===")
        print(client.get("/api/calcul-tva?ht=2500&taux=19").get_json())
    if os.environ.get("ISGP_WEB_RUNNER") != "1" and "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        print("\n" + "=" * 76)
        print(f"[SERVEUR WSGI FLASK ACTIF] Serveur en écoute sur http://127.0.0.1:{port}")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print(f"  -> Testez les routes en direct sur http://127.0.0.1:{port} (navigateur, curl, Postman)")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
