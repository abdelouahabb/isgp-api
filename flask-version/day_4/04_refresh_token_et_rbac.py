# Fichier : day_4/04_refresh_token_et_rbac.py
# Exécution : .venv/bin/python day_4/04_refresh_token_et_rbac.py
# Objectif : Implémenter un décorateur @token_requis, le contrôle d'accès par rôle (RBAC : 401 vs 403),
#            le renouvellement par Refresh Token et la révocation (Blacklist).

import os
import sys
from functools import wraps
from flask import Flask, g, jsonify, render_template, request
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))
SECRET_KEY = os.environ.get("API_SECRET_KEY", "secret-signature-isgp-2026")
access_signer = URLSafeTimedSerializer(SECRET_KEY, salt="access-token")
refresh_signer = URLSafeTimedSerializer(SECRET_KEY, salt="refresh-token")

# Liste noire (Blacklist) des jetons révoqués lors d'une déconnexion (Logout)
jetons_revoques = set()

# 1. DÉCORATEUR D'AUTHENTIFICATION ET DE CONTRÔLE DE RÔLE (RBAC)
def exiger_role(role_minimum=None):
    def decorateur(f):
        @wraps(f)
        def enveloppe(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"erreur": "401 Unauthorized : Bearer Token manquant"}), 401

            token = auth.split(" ", 1)[1].strip()
            if token in jetons_revoques:
                return jsonify({"erreur": "401 Unauthorized : Ce jeton a été révoqué (déconnecté)"}), 401

            try:
                # L'Access Token a une durée de vie courte (ex: 300 secondes)
                utilisateur = access_signer.loads(token, max_age=300)
            except SignatureExpired:
                return jsonify({"erreur": "401 Unauthorized : Access Token expiré. Utilisez /api/auth/refresh"}), 401
            except BadSignature:
                return jsonify({"erreur": "401 Unauthorized : Signature du jeton invalide"}), 401

            # Vérification du Rôle (RBAC) : 403 Forbidden si authentifié mais droits insuffisants !
            if role_minimum and utilisateur.get("role") != role_minimum:
                return jsonify({
                    "erreur": f"403 Forbidden : Rôle '{role_minimum}' requis (votre rôle : '{utilisateur.get('role')}')"
                }), 403

            g.utilisateur = utilisateur
            return f(*args, **kwargs)
        return enveloppe
    return decorateur

# 2. LOGIN : Émet un Access Token (5 min) ET un Refresh Token (7 jours)
@app.route("/api/auth/login", methods=["POST"])
def login():
    corps = request.get_json(silent=True) or {}
    identifiant = corps.get("identifiant", "stagiaire")
    role = "admin" if identifiant == "directeur" else "stagiaire"

    payload = {"sub": identifiant, "role": role}
    return jsonify({
        "access_token": access_signer.dumps(payload),
        "refresh_token": refresh_signer.dumps(payload),
        "token_type": "Bearer",
        "access_expires_in": 300,
        "refresh_expires_in": 604800
    }), 200

# 3. REFRESH : Échange un Refresh Token valide contre un nouvel Access Token neuf
@app.route("/api/auth/refresh", methods=["POST"])
def rafraichir_token():
    corps = request.get_json(silent=True) or {}
    rt = corps.get("refresh_token", "")
    try:
        payload = refresh_signer.loads(rt, max_age=604800)
        nouvel_access = access_signer.dumps(payload)
        return jsonify({"access_token": nouvel_access, "expires_in": 300}), 200
    except (BadSignature, SignatureExpired):
        return jsonify({"erreur": "Refresh Token invalide ou expiré"}), 401

# 4. ROUTE RÉSERVÉE AU RÔLE 'admin' (Démontre 401 vs 403)
@app.route("/api/admin/audit", methods=["GET"])
@exiger_role("admin")
def consulter_audit_admin():
    return jsonify({"acces": "Autorisé (Admin)", "operateur": g.utilisateur["sub"]}), 200


@app.route("/", methods=["GET"])
def index_rbac():
    return render_template("index_04_rbac.html"), 200


if __name__ == "__main__":
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        r_stag = client.post("/api/auth/login", json={"identifiant": "stagiaire"}).get_json()
        r_403 = client.get("/api/admin/audit", headers={"Authorization": f"Bearer {r_stag['access_token']}"})
        print("1. Stagiaire sur route Admin (403 Forbidden) :", r_403.status_code, r_403.get_json())
        r_dir = client.post("/api/auth/login", json={"identifiant": "directeur"}).get_json()
        r_200 = client.get("/api/admin/audit", headers={"Authorization": f"Bearer {r_dir['access_token']}"})
        print("2. Directeur sur route Admin (200 OK) :", r_200.status_code, r_200.get_json())
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
