# Fichier : day_4/06_authn_vs_authz_scopes.py
# Exécution : .venv/bin/python day_4/06_authn_vs_authz_scopes.py
# Objectif : Maîtriser la différence fondamentale en API Management entre :
#            1. AUTHENTIFICATION (AuthN) -> "Qui êtes-vous ?"       -> Échec = 401 Unauthorized
#            2. AUTORISATION     (AuthZ) -> "Quels sont vos droits ?" -> Échec = 403 Forbidden
#            (Contrôle par Rôle RBAC, par Permissions/Scopes OAuth2 et par Propriété BOLA)

import os
import sys
from flask import Flask, jsonify, render_template, request
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))

SECRET_KEY = "secret-api-management-isgp-2026"
signer = URLSafeTimedSerializer(SECRET_KEY)

# Base de données simulée de dossiers confidentiels (chaque dossier appartient à un propriétaire)
DOSSIERS = {
    101: {"id": 101, "proprietaire": "amine", "note_evaluation": 17.5},
    102: {"id": 102, "proprietaire": "sara",  "note_evaluation": 18.0},
}


def verifier_authn_et_authz(token, scope_requis=None, role_requis=None, ressource_proprietaire=None):
    # =========================================================================
    # ÉTAPE 1 : AUTHENTIFICATION (AuthN) — Prouver l'identité de l'appelant
    # =========================================================================
    if not token:
        return 401, "401 Unauthorized [Échec AuthN] : Aucun jeton d'identité fourni."
    try:
        identite = signer.loads(token, max_age=300)
    except SignatureExpired:
        return 401, "401 Unauthorized [Échec AuthN] : Le jeton a expiré."
    except BadSignature:
        return 401, "401 Unauthorized [Échec AuthN] : Signature falsifiée."

    utilisateur = identite["sub"]
    role = identite["role"]
    scopes = identite.get("scopes", [])

    # =========================================================================
    # ÉTAPE 2 : AUTORISATION (AuthZ) — Vérifier les permissions de l'identité connue
    # =========================================================================
    # A. Contrôle par Rôle (RBAC : Role-Based Access Control)
    if role_requis and role != role_requis:
        return 403, (
            f"403 Forbidden [AuthN OK='{utilisateur}', Échec AuthZ RBAC] : "
            f"Rôle '{role_requis}' requis, mais votre rôle est '{role}'."
        )

    # B. Contrôle par Permission granulaire (OAuth2 Scopes)
    if scope_requis and scope_requis not in scopes:
        return 403, (
            f"403 Forbidden [AuthN OK='{utilisateur}', Échec AuthZ Scope] : "
            f"Scope '{scope_requis}' absent de votre jeton ({scopes})."
        )

    # C. Contrôle de Propriété de l'Objet (Protection anti-BOLA / OWASP API #1)
    if ressource_proprietaire and utilisateur != ressource_proprietaire and role != "admin":
        return 403, (
            f"403 Forbidden [AuthN OK='{utilisateur}', Échec AuthZ BOLA] : "
            f"Ce dossier appartient à '{ressource_proprietaire}', accès interdit."
        )

    return 200, f"200 OK [AuthN='{utilisateur}' + AuthZ Validée] : Accès accordé."


def extraire_bearer():
    auth = request.headers.get("Authorization", "")
    return auth.split(" ", 1)[1].strip() if auth.startswith("Bearer ") else None


@app.route("/api/auth/tokens-demo", methods=["GET"])
def tokens_demo():
    return jsonify({
        "amine": signer.dumps({"sub": "amine", "role": "stagiaire", "scopes": ["formations:read", "dossiers:read"]}),
        "directeur": signer.dumps({"sub": "directeur", "role": "admin", "scopes": ["formations:read", "formations:write", "audit:admin"]}),
    }), 200


@app.route("/api/dossiers/<int:dossier_id>", methods=["GET"])
def consulter_dossier(dossier_id):
    dossier = DOSSIERS.get(dossier_id)
    if not dossier:
        return jsonify({"erreur": "Dossier introuvable"}), 404
    code, msg = verifier_authn_et_authz(extraire_bearer(), scope_requis="dossiers:read", ressource_proprietaire=dossier["proprietaire"])
    if code != 200:
        return jsonify({"statut": code, "diagnostic": msg}), code
    return jsonify({"statut": 200, "diagnostic": msg, "dossier": dossier}), 200


@app.route("/api/admin/audit", methods=["GET"])
def consulter_audit_scopes():
    code, msg = verifier_authn_et_authz(extraire_bearer(), role_requis="admin", scope_requis="audit:admin")
    return jsonify({"statut": code, "diagnostic": msg}), code


@app.route("/", methods=["GET"])
def index_scopes():
    return render_template("index_06_scopes.html"), 200


if __name__ == "__main__":
    token_amine = signer.dumps({"sub": "amine", "role": "stagiaire", "scopes": ["formations:read", "dossiers:read"]})
    token_directeur = signer.dumps({"sub": "directeur", "role": "admin", "scopes": ["formations:read", "formations:write", "audit:admin"]})

    print("=== 1. TEST SANS JETON (Échec AuthN -> 401) ===")
    print(verifier_authn_et_authz(None, scope_requis="formations:read")[1])
    print("\n=== 2. AMINE TENTE DE SUPPRIMER UNE FORMATION (AuthN OK, Échec AuthZ Scope -> 403) ===")
    print(verifier_authn_et_authz(token_amine, scope_requis="formations:write")[1])
    print("\n=== 3. AMINE TENTE DE LIRE LE DOSSIER DE SARA (AuthN OK, Échec AuthZ BOLA -> 403) ===")
    print(verifier_authn_et_authz(token_amine, scope_requis="dossiers:read", ressource_proprietaire="sara")[1])
    print("\n=== 4. AMINE LIT SON PROPRE DOSSIER (AuthN OK + AuthZ OK -> 200) ===")
    print(verifier_authn_et_authz(token_amine, scope_requis="dossiers:read", ressource_proprietaire="amine")[1])
    print("\n=== 5. LE DIRECTEUR ACCÈDE À L'AUDIT ADMIN (AuthN OK + AuthZ Admin OK -> 200) ===")
    print(verifier_authn_et_authz(token_directeur, role_requis="admin", scope_requis="audit:admin")[1])

    with app.test_client() as client:
        assert client.get("/").status_code == 200
        assert client.get("/api/dossiers/101").status_code == 401
        assert client.get("/api/dossiers/102", headers={"Authorization": f"Bearer {token_amine}"}).status_code == 403
        assert client.get("/api/dossiers/101", headers={"Authorization": f"Bearer {token_amine}"}).status_code == 200

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
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
