# Fichier : day_2/01_serveur_minimal_flask.py
# Exécution : .venv/bin/python day_2/01_serveur_minimal_flask.py
# Objectif : Comprendre comment Flask sert à la fois :
#   1. Des pages Web HTML via le moteur de templates Jinja2 (render_template -> day_2/templates/accueil.html)
#   2. Des routes d'API RESTful normalisées en JSON (jsonify -> /api/v1/...)

import os
import sys
from flask import Flask, jsonify, render_template

# Configuration du dossier "templates/" contenant les fichiers HTML Jinja2
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))

MODULES_BOOTCAMP = [
    "Jour 1 : Architecture Web, HTTP/1.1, JSON & curl",
    "Jour 2 : Flask, Routage RESTful, Templates Jinja2 & Formulaires HTML",
    "Jour 3 : Ingénierie CRUD, Validation RFC 7807 & SQLite ACID",
    "Jour 4 : Sécurité API (AuthN 401, AuthZ 403, JWT, Rate Limiting 429)",
    "Jour 5 : Client Résilient, Blueprints, Tests & Swagger OpenAPI 3.0",
]


# 1. ROUTE WEB HTML : Rendu via le template Jinja2 (day_2/templates/accueil.html)
#    Zéro HTML écrit en dur dans le code Python !
@app.route("/accueil", methods=["GET"])
def page_accueil_jinja():
    return render_template(
        "accueil.html",
        organisme="ISGP",
        intitule="Développement d'APIs et services web",
        version_api="v1.0",
        modules=MODULES_BOOTCAMP,
    ), 200


# 2. ROUTE API REST : Retourne un objet JSON léger avec le code HTTP 200 OK
@app.route("/api/bonjour", methods=["GET"])
def dire_bonjour():
    return jsonify({
        "message": "Service Flask opérationnel",
        "organisme": "ISGP",
        "statut": "actif",
        "version": "v1.0",
    }), 200


# 3. COLLECTION RESTFUL (Niveau 2 de Richardson : nom au pluriel + versioning /api/v1)
@app.route("/api/v1/modules", methods=["GET"])
def lister_modules_api():
    return jsonify({
        "total": len(MODULES_BOOTCAMP),
        "data": MODULES_BOOTCAMP,
    }), 200


if __name__ == "__main__":
    # Si on lance avec '--serve', démarre le serveur HTTP sur le port 5001
    if "--serve" in sys.argv:
        app.run(host="0.0.0.0", port=5001, debug=True)
    else:
        # Sinon, exécute une démonstration immédiate des 2 modes (Jinja2 HTML vs API JSON)
        with app.test_client() as client:
            rep_html = client.get("/accueil")
            print("=== 1. RENDU DU TEMPLATE JINJA2 (GET /accueil -> day_2/templates/accueil.html) ===")
            print(rep_html.get_data(as_text=True).strip())

            rep_json = client.get("/api/bonjour")
            print("\n=== 2. RÉPONSE API JSON (GET /api/bonjour -> jsonify) ===")
            print("Statut HTTP :", rep_json.status_code, "| Content-Type :", rep_json.content_type)
            print("Payload JSON :", rep_json.get_json())
