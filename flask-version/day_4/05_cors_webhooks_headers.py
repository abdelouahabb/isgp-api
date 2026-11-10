import sys
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
    with app.test_client() as client:
        corps = json.dumps({"facture_id": "FAC-2026-09", "montant_dzd": 45000}).encode("utf-8")
        sig = "sha256=" + hmac.new(WEBHOOK_SECRET.encode("utf-8"), corps, hashlib.sha256).hexdigest()
        r_ok = client.post(
            "/api/webhooks/paiement",
            data=corps,
            headers={"Content-Type": "application/json", "X-Webhook-Signature": sig, "Origin": "https://portail.isgp.dz"},
        )
        print("1. Webhook signé valide (200) :", r_ok.status_code, r_ok.get_json())
        print("2. En-têtes CORS & Sécurité :", {k: v for k, v in r_ok.headers.items() if k.startswith(("Access-Control", "X-"))})
    if "--once" not in sys.argv:
        import socket as _sock
        port = int(os.environ.get("PORT", 5001))
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
            if _s.connect_ex(("127.0.0.1", port)) == 0:
                _s2 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                _s2.bind(("127.0.0.1", 0))
                port = _s2.getsockname()[1]
                _s2.close()
        print("\n" + "=" * 76)
        print(f"[SERVEUR WSGI FLASK ACTIF] Serveur en écoute sur http://127.0.0.1:{port}")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print(f"  -> Testez les routes en direct sur http://127.0.0.1:{port} (navigateur, curl, Postman)")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
