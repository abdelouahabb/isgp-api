# Fichier : day_4/01_secrets_et_api_key.py
# Exécution : .venv/bin/python day_4/01_secrets_et_api_key.py

import os
import hmac
from flask import Flask, jsonify, request

app = Flask(__name__)

# 1. Lecture des secrets depuis les variables d'environnement du système
API_SECRET_KEY = os.environ.get("API_SECRET_KEY", "cle-signature-interne-isgp-2026")
PARTNER_API_KEY = os.environ.get("PARTNER_API_KEY", "isgp-secret-2026")

@app.route("/api/admin/statistiques", methods=["GET"])
def stats_confidentielles():
    # 2. Lecture de la clé transmise dans l'en-tête HTTP X-API-Key
    cle_recue = request.headers.get("X-API-Key", "")

    # 3. Comparaison en temps constant (protège contre les attaques temporelles)
    if not hmac.compare_digest(cle_recue, PARTNER_API_KEY):
        return jsonify({
            "erreur": "Accès non autorisé (401). En-tête X-API-Key manquant ou invalide."
        }), 401

    return jsonify({
        "acces": "Autorisé via X-API-Key",
        "stagiaires_certifies": 148
    }), 200

if __name__ == "__main__":
    import sys
    if "--serve" in sys.argv:
        app.run(host="0.0.0.0", port=5001, debug=True)
    else:
        with app.test_client() as client:
            r_no_key = client.get("/api/admin/statistiques")
            print("1. Sans X-API-Key (401) :", r_no_key.status_code, r_no_key.get_json())
            r_valid = client.get("/api/admin/statistiques", headers={"X-API-Key": PARTNER_API_KEY})
            print("2. Avec X-API-Key valide (200) :", r_valid.status_code, r_valid.get_json())
