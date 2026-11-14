# Fichier : zero_to_hero/etape_05_securite_auth_rbac_cookies.py
# Étape 5/6 : Sécurité Industrielle — Cookies HttpOnly/SameSite, Bearer HMAC, RBAC (401/403) & Rate Limit 429
# Exécution : .venv/bin/python flask-version/zero_to_hero/etape_05_securite_auth_rbac_cookies.py

import functools
import hmac
import os
import sqlite3
import sys
import time
from flask import Flask, g, jsonify, render_template, request, session
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DOSSIER_COURANT, "isgp_zero_to_hero.db")

app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cle-secrete-hmac-isgp-zero-to-hero-2026")
app.config.update(
    SESSION_COOKIE_NAME="isgp_z2h_session",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE="Lax",
)

signataire = URLSafeTimedSerializer(app.secret_key, salt="bearer-hmac-sha256")

COMPTES_UTILISATEURS = {
    "stagiaire": {"secret": "isgp-stagiaire-2026", "role": "stagiaire"},
    "admin": {"secret": "isgp-admin-2026", "role": "admin"},
}

FENETRE_RL_SEC = 15
QUOTA_MAX_REQUETES = 5
historique_ip = {}


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA busy_timeout=5000;")
        g.db = conn
    return g.db


@app.teardown_appcontext
def fermer_db(exception=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS formations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                titre TEXT NOT NULL,
                domaine TEXT NOT NULL DEFAULT 'Backend',
                duree_jours INTEGER NOT NULL CHECK(duree_jours BETWEEN 1 AND 30),
                tarif_dzd INTEGER NOT NULL CHECK(tarif_dzd >= 0)
            )
        """)
        if db.execute("SELECT COUNT(*) FROM formations").fetchone()[0] == 0:
            db.execute(
                "INSERT INTO formations (code, titre, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
                ("SEC-501", "Architecture Securite API & RBAC", "Securite", 5, 75000),
            )
        db.commit()


def verifier_rate_limit():
    ip = request.remote_addr or "127.0.0.1"
    maintenant = time.time()
    recents = [t for t in historique_ip.get(ip, []) if maintenant - t < FENETRE_RL_SEC]
    if len(recents) >= QUOTA_MAX_REQUETES:
        attente = max(1, int(FENETRE_RL_SEC - (maintenant - recents[0])) + 1)
        rep = jsonify({"erreur": "Quota depasse (429 Too Many Requests)", "retry_after_seconds": attente})
        rep.status_code = 429
        rep.headers["Retry-After"] = str(attente)
        rep.headers["X-RateLimit-Remaining"] = "0"
        return rep
    recents.append(maintenant)
    historique_ip[ip] = recents
    g.rl_restant = QUOTA_MAX_REQUETES - len(recents)
    return None


def exiger_role(*roles_autorises):
    """Decorateur RBAC verifiant Bearer Token signe OU Session Cookie HttpOnly (401 vs 403)."""
    def decorateur(vue):
        @functools.wraps(vue)
        def enveloppe(*args, **kwargs):
            identite = None
            entete = request.headers.get("Authorization", "")
            if entete.startswith("Bearer "):
                jeton = entete.split(" ", 1)[1].strip()
                try:
                    identite = signataire.loads(jeton, max_age=600)
                except (BadSignature, SignatureExpired):
                    rep = jsonify({"erreur": "401 Unauthorized : Bearer Token invalide ou expire"})
                    rep.status_code = 401
                    rep.headers["WWW-Authenticate"] = 'Bearer realm="ISGP-API", error="invalid_token"'
                    return rep
            elif "utilisateur" in session:
                identite = {"sub": session["utilisateur"], "role": session.get("role", "stagiaire")}

            if not identite:
                rep = jsonify({"erreur": "401 Unauthorized : Authentification requise (Bearer ou Session)"})
                rep.status_code = 401
                rep.headers["WWW-Authenticate"] = 'Bearer realm="ISGP-API"'
                return rep

            if roles_autorises and identite.get("role") not in roles_autorises:
                return jsonify({
                    "erreur": f"403 Forbidden : Role {roles_autorises} requis (role actuel : {identite.get('role')})"
                }), 403

            g.identite = identite
            return vue(*args, **kwargs)
        return enveloppe
    return decorateur


@app.route("/", methods=["GET"])
def page_securite():
    return render_template("etape_05_securite.html", etape="Etape 5/6 — Securite Auth, RBAC, Cookies & 429"), 200


@app.route("/api/v1/auth/login", methods=["POST"])
def authentifier():
    corps = request.get_json(silent=True) or {}
    login_u = str(corps.get("identifiant", "")).strip()
    secret_fourni = str(corps.get("mot_de_passe", ""))
    compte = COMPTES_UTILISATEURS.get(login_u)
    if not compte or not hmac.compare_digest(secret_fourni, compte["secret"]):
        rep = jsonify({"erreur": "Identifiants invalides (401)"})
        rep.status_code = 401
        rep.headers["WWW-Authenticate"] = 'Bearer realm="ISGP-API"'
        return rep

    charge = {"sub": login_u, "role": compte["role"]}
    session["utilisateur"] = login_u
    session["role"] = compte["role"]
    jeton = signataire.dumps(charge)
    return jsonify({
        "access_token": jeton,
        "token_type": "Bearer",
        "role": compte["role"],
        "session_cookie": "isgp_z2h_session (HttpOnly, SameSite=Lax)",
    }), 200


@app.route("/api/v1/auth/logout", methods=["POST"])
def deconnexion():
    session.clear()
    return jsonify({"statut": "Session revoquee"}), 200


@app.route("/api/v1/formations", methods=["GET"])
@exiger_role("stagiaire", "admin")
def lister_formations_protegees():
    blocage = verifier_rate_limit()
    if blocage is not None:
        return blocage
    lignes = get_db().execute("SELECT * FROM formations ORDER BY id ASC").fetchall()
    rep = jsonify({"operateur": g.identite, "data": [dict(r) for r in lignes]})
    rep.headers["X-RateLimit-Remaining"] = str(getattr(g, "rl_restant", QUOTA_MAX_REQUETES))
    return rep, 200


@app.route("/api/v1/formations", methods=["POST"])
@exiger_role("admin")
def creer_formation_admin():
    corps = request.get_json(silent=True) or {}
    code = str(corps.get("code", "")).strip().upper()
    titre = str(corps.get("titre", "")).strip()
    if len(code) < 3 or len(titre) < 4:
        return jsonify({"erreur": "Code (>=3) et titre (>=4) requis"}), 422
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO formations (code, titre, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
            (code, titre, str(corps.get("domaine", "Securite")), int(corps.get("duree_jours", 4)), int(corps.get("tarif_dzd", 65000))),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"erreur": "Code deja existant"}), 409
    return jsonify({"cree_par": g.identite["sub"], "id": cur.lastrowid}), 201


init_db()

if __name__ == "__main__":
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        r_401 = client.get("/api/v1/formations")
        assert r_401.status_code == 401 and "WWW-Authenticate" in r_401.headers
        tok_stag = client.post("/api/v1/auth/login", json={"identifiant": "stagiaire", "mot_de_passe": "isgp-stagiaire-2026"}).get_json()["access_token"]
        client.post("/api/v1/auth/logout")
        assert client.post("/api/v1/formations", headers={"Authorization": f"Bearer {tok_stag}"}, json={"code": "ADM-01", "titre": "Test RBAC"}).status_code == 403
        tok_adm = client.post("/api/v1/auth/login", json={"identifiant": "admin", "mot_de_passe": "isgp-admin-2026"}).get_json()["access_token"]
        historique_ip.clear()
        statuts = [client.get("/api/v1/formations", headers={"Authorization": f"Bearer {tok_adm}"}).status_code for _ in range(QUOTA_MAX_REQUETES + 1)]
        assert statuts[-1] == 429
        historique_ip.clear()
        print("[ETAPE 05 OK] Cookies HttpOnly + Bearer HMAC + RBAC (401/403) + Rate-Limit 429 valides.")

    if "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        print(f"[ETAPE 05] Portail Securise actif sur http://127.0.0.1:{port}")
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
