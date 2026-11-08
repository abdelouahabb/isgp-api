# Fichier : day_4/05_cors_webhooks_headers.py
# Exécution : .venv/bin/python day_4/05_cors_webhooks_headers.py
# Objectif : Configurer CORS, limiter la taille maximale du Payload (413 Payload Too Large)
#            et vérifier la signature cryptographique HMAC-SHA256 d'un Webhook entrant.

import hashlib
import hmac
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# 1. PROTECTION ANTI-SATURATION MÉMOIRE : Limite la taille maximale du Body à 1 Mo (413 Payload Too Large)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "whsec_isgp_partenaire_2026")
ORIGINES_AUTORISEES = {"http://localhost:3000", "https://portail.isgp.dz"}

# 2. CONFIGURATION CORS STRICTE & EN-TÊTES DE SÉCURITÉ HTTP
@app.after_request
def appliquer_cors_et_headers_securite(reponse):
    origine = request.headers.get("Origin", "")
    if origine in ORIGINES_AUTORISEES:
        reponse.headers["Access-Control-Allow-Origin"] = origine
        reponse.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-API-Key"
        reponse.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    reponse.headers["X-Content-Type-Options"] = "nosniff"
    reponse.headers["X-Frame-Options"] = "DENY"
    reponse.headers["Cache-Control"] = "no-store"
    return reponse

# 3. RÉCEPTION SÉCURISÉE D'UN WEBHOOK (Vérification HMAC-SHA256 du corps brut)
@app.route("/api/webhooks/paiement", methods=["POST"])
def recevoir_webhook_paiement():
    signature_recue = request.headers.get("X-Webhook-Signature", "")
    corps_brut = request.get_data()  # Octets exacts reçus sur le réseau

    # Calcul de l'empreinte HMAC-SHA256 attendue avec le secret partagé
    signature_calculee = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        corps_brut,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature_recue, signature_calculee):
        return jsonify({"erreur": "Signature Webhook invalide (401 Unauthorized)"}), 401

    evenement = request.get_json(silent=True) or {}
    return jsonify({"statut": "Webhook authentifié et traité", "evenement": evenement}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
