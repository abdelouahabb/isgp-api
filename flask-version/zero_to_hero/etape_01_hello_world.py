# Fichier : zero_to_hero/etape_01_hello_world.py
# Étape 1/6 (Zero / Hello World) : Premier serveur Web HTML (Jinja2) + API JSON (jsonify)
# Exécution : .venv/bin/python flask-version/zero_to_hero/etape_01_hello_world.py

import os
import sys
from flask import Flask, jsonify, render_template

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))


@app.route("/", methods=["GET"])
def page_accueil():
    """Expose le portail Web HTML minimaliste consommant /api/bonjour."""
    return render_template(
        "etape_01_hello.html",
        organisme="Institut Superieur de Gestion et de Planification (ISGP)",
        etape="Etape 1/6 — Hello World Web & API JSON",
    ), 200


@app.route("/api/bonjour", methods=["GET"])
def api_bonjour():
    """Premiere route d'API REST retournant un contrat JSON normalise."""
    return jsonify({
        "statut": "operationnel",
        "etape": 1,
        "organisme": "ISGP",
        "message": "Bienvenue sur l'API du Catalogue des Formations ISGP",
    }), 200


if __name__ == "__main__":
    with app.test_client() as client:
        r_html = client.get("/")
        r_json = client.get("/api/bonjour")
        assert r_html.status_code == 200 and "text/html" in r_html.content_type
        assert r_json.status_code == 200 and r_json.get_json()["statut"] == "operationnel"
        print("[ETAPE 01 OK] GET / (HTML) =", r_html.status_code, "| GET /api/bonjour (JSON) =", r_json.get_json())

    if "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        print(f"[ETAPE 01] Portail Web & API actifs sur http://127.0.0.1:{port}")
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
