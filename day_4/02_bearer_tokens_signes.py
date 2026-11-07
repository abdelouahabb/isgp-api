# Fichier : day_4/02_bearer_tokens_signes.py
# Exécution : .venv/bin/python day_4/02_bearer_tokens_signes.py

import os
from flask import Flask, jsonify, request
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

app = Flask(__name__)
SECRET_KEY = os.environ.get("API_SECRET_KEY", "secret-signature-isgp-2026")
signer = URLSafeTimedSerializer(SECRET_KEY)

# 1. ROUTE DE CONNEXION : Émission du Bearer Token signé
@app.route("/api/auth/token", methods=["POST"])
def generer_token():
    corps = request.get_json(silent=True) or {}
    if corps.get("identifiant") != "stagiaire" or corps.get("mot_de_passe") != "isgp2026":
        return jsonify({"erreur": "Identifiants invalides"}), 401

    charge_utile = {"utilisateur": corps["identifiant"], "role": "participant_isgp"}
    token = signer.dumps(charge_utile)
    return jsonify({
        "access_token": token,
        "token_type": "Bearer",
        "expires_in_seconds": 300
    }), 200

# 2. ROUTE PROTÉGÉE : Vérification de la signature et de l'expiration du Token
@app.route("/api/auth/profil", methods=["GET"])
def profil_protege():
    entete_auth = request.headers.get("Authorization", "")
    if not entete_auth.startswith("Bearer "):
        return jsonify({"erreur": "En-tête 'Authorization: Bearer <token>' requis"}), 401

    token = entete_auth.split(" ", 1)[1].strip()
    try:
        donnees_utilisateur = signer.loads(token, max_age=300)  # Expire après 300s (5 min)
        return jsonify({"acces": "Token vérifié", "profil": donnees_utilisateur}), 200
    except SignatureExpired:
        return jsonify({"erreur": "Le jeton (Token) a expiré"}), 401
    except BadSignature:
        return jsonify({"erreur": "Signature du jeton invalide (jeton falsifié)"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
