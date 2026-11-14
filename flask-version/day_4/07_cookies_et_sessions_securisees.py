# Fichier : day_4/07_cookies_et_sessions_securisees.py
# Exécution : .venv/bin/python day_4/07_cookies_et_sessions_securisees.py
# Objectif : Maîtriser la gestion et la sécurité des Cookies en API & Web avec Flask :
#   1. Cookie standard non signé (request.cookies / response.set_cookie) -> Préférences UI uniquement
#   2. Les 3 drapeaux de sécurité obligatoires : HttpOnly (anti-XSS), Secure (HTTPS), SameSite (anti-CSRF)
#   3. Cookie de Session signé cryptographiquement par HMAC (flask.session + app.secret_key)
#   4. Révocation propre d'un cookie (response.delete_cookie -> Max-Age=0)

import os
import sys
from flask import Flask, jsonify, make_response, render_template, request, session
from itsdangerous import URLSafeTimedSerializer, BadSignature

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))

# Clé secrète serveur obligatoire pour signer cryptographiquement le cookie 'session'
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cle-secrete-hmac-cookies-isgp-2026")

# Configuration de sécurité globale des cookies de session Flask en production
app.config.update(
    SESSION_COOKIE_NAME="isgp_session",
    SESSION_COOKIE_HTTPONLY=True,   # Interdit la lecture par JavaScript (document.cookie) -> Anti-XSS
    SESSION_COOKIE_SECURE=False,    # Mettre True en production HTTPS (transmis uniquement sur TLS)
    SESSION_COOKIE_SAMESITE="Lax",  # Bloque l'envoi inter-sites non sollicité -> Anti-CSRF
)

signataire_jeton = URLSafeTimedSerializer(app.secret_key)


# 1. CONNEXION : Émettre un cookie HttpOnly sécurisé + une session signée + un cookie de préférence
@app.route("/api/auth/cookie-login", methods=["POST"])
def connexion_par_cookie():
    corps = request.get_json(silent=True) or {}
    identifiant = str(corps.get("identifiant", "stagiaire_isgp")).strip()
    theme_choisi = str(corps.get("theme", "institutionnel")).strip()

    # A. Écriture dans la session Flask (automatiquement signée par HMAC avec app.secret_key)
    session["utilisateur"] = identifiant
    session["role"] = "auditeur_securite"

    # B. Génération d'un jeton signé stocké dans un cookie dédié HttpOnly
    jeton_signe = signataire_jeton.dumps({"sub": identifiant, "scope": "api:read"})

    reponse = make_response(jsonify({
        "statut": "Authentifié par Cookies sécurisés",
        "utilisateur": identifiant,
        "cookies_emis": ["isgp_session (Signé HMAC + HttpOnly)", "isgp_auth_token (HttpOnly + SameSite=Strict)", "isgp_theme (Préférence UI)"],
    }), 200)

    # C. Cookie sensible d'authentification : HttpOnly=True + SameSite='Strict' obligatoires !
    reponse.set_cookie(
        key="isgp_auth_token",
        value=jeton_signe,
        max_age=3600,          # Expire dans 1 heure (3600 secondes)
        httponly=True,         # Bouclier anti-XSS : inaccessible via document.cookie en JS
        secure=False,          # Mettre True en production (exige HTTPS)
        samesite="Strict",     # Bouclier anti-CSRF : jamais envoyé depuis un site externe
        path="/",
    )

    # D. Cookie de préférence visuelle non sensible (lisible par le JS frontal si besoin)
    reponse.set_cookie("isgp_theme", theme_choisi, max_age=86400 * 30, httponly=False, samesite="Lax")
    return reponse


# 2. INSPECTION : Lire et vérifier les cookies reçus dans l'en-tête HTTP 'Cookie'
@app.route("/api/auth/cookie-inspect", methods=["GET"])
def inspecter_cookies():
    jeton_cookie = request.cookies.get("isgp_auth_token")
    theme = request.cookies.get("isgp_theme", "clair")
    utilisateur_session = session.get("utilisateur")

    if not jeton_cookie or not utilisateur_session:
        return jsonify({"erreur": "Aucun cookie d'authentification valide reçu (401)"}), 401

    try:
        charge_jeton = signataire_jeton.loads(jeton_cookie, max_age=3600)
    except BadSignature:
        return jsonify({"erreur": "Cookie isgp_auth_token falsifié ou expiré (401)"}), 401

    return jsonify({
        "authentifie": True,
        "session_signee_hmac": {"utilisateur": utilisateur_session, "role": session.get("role")},
        "cookie_httponly_decode": charge_jeton,
        "cookie_preference_theme": theme,
        "en_tete_cookie_brut": request.headers.get("Cookie", ""),
    }), 200


# 3. PORTAIL WEB JINJA2 PROTÉGÉ PAR LES COOKIES
@app.route("/portail-cookies", methods=["GET"])
def portail_html_cookies():
    if "utilisateur" not in session:
        return jsonify({"erreur": "Session absente"}), 401
    return render_template(
        "portail_cookies.html",
        utilisateur=session["utilisateur"],
        role=session.get("role", "invité"),
        theme=request.cookies.get("isgp_theme", "institutionnel"),
    ), 200


# 4. DÉCONNEXION : Purger la session et forcer l'expiration immédiate des cookies (Max-Age=0)
@app.route("/api/auth/cookie-logout", methods=["POST"])
def deconnexion_cookies():
    session.clear()
    reponse = make_response(jsonify({"statut": "Déconnecté — Cookies révoqués (Max-Age=0)"}), 200)
    reponse.delete_cookie("isgp_auth_token", path="/")
    reponse.delete_cookie("isgp_theme", path="/")
    return reponse


# 5. PORTAIL WEB INTERACTIF SUR GET / (Testeur des cookies HttpOnly, SameSite et Session)
@app.route("/", methods=["GET"])
def index_cookies():
    return render_template("index_07_cookies.html"), 200


if __name__ == "__main__":
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        print("=== 1. CONNEXION (POST /api/auth/cookie-login) -> EN-TÊTES Set-Cookie ===")
        r_login = client.post("/api/auth/cookie-login", json={"identifiant": "yasmine.merabet", "theme": "sombre"})
        for sc in r_login.headers.getlist("Set-Cookie"):
            print("  Set-Cookie :", sc)

        print("\n=== 2. REQUÊTE AUTHENTIFIÉE AUTOMATIQUEMENT PAR COOKIES (GET /api/auth/cookie-inspect) ===")
        r_insp = client.get("/api/auth/cookie-inspect")
        print("  Statut :", r_insp.status_code, "| JSON :", r_insp.get_json())

        print("\n=== 3. DÉCONNEXION ET RÉVOCATION (POST /api/auth/cookie-logout) ===")
        r_out = client.post("/api/auth/cookie-logout")
        print("  Après logout -> GET /api/auth/cookie-inspect :", client.get("/api/auth/cookie-inspect").status_code)
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
