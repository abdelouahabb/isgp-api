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
    with app.test_client() as client:
        r_tok = client.post("/api/auth/token", json={"identifiant": "stagiaire", "mot_de_passe": "isgp2026"})
        tok = r_tok.get_json()["access_token"]
        print("1. Bearer Token émis (200) :", tok[:35] + "...")
        r_prof = client.get("/api/auth/profil", headers={"Authorization": f"Bearer {tok}"})
        print("2. Profil vérifié (200) :", r_prof.status_code, r_prof.get_json())
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
