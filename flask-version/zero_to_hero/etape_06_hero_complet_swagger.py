# Fichier : zero_to_hero/etape_06_hero_complet_swagger.py
# Étape 6/6 (Application Finale Hero) : Blueprints, Application Factory create_app(), SQLite WAL,
# Cookies HttpOnly + Bearer HMAC RBAC, Rate-Limiting 429, Audit Middleware, /health & OpenAPI 3.1.0 / Swagger UI
# Exécution : .venv/bin/python flask-version/zero_to_hero/etape_06_hero_complet_swagger.py
# Production : gunicorn -w 4 -b 0.0.0.0:8000 "zero_to_hero.etape_06_hero_complet_swagger:create_app()"

import functools
import hmac
import json
import math
import os
import sqlite3
import sys
import time
import uuid
from flask import Blueprint, Flask, Response, current_app, g, jsonify, render_template, request, session
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DB_DEFAUT = os.path.join(DOSSIER_COURANT, "isgp_zero_to_hero.db")
DEMARRAGE = time.time()

COMPTES = {
    "stagiaire": {"secret": "isgp-stagiaire-2026", "role": "stagiaire"},
    "admin": {"secret": "isgp-admin-2026", "role": "admin"},
}
CHAMPS_TRI = {"id", "duree_jours", "tarif_dzd", "titre"}
FENETRE_RL_SEC = 15
QUOTA_MAX_REQUETES = 20
historique_ip = {}


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE_PATH"], timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.execute("PRAGMA busy_timeout=5000;")
        g.db = conn
    return g.db


def erreur_rfc7807(status, title, detail, erreurs=None):
    probleme = {
        "type": "https://api.isgp.dz/erreurs/catalogue",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path,
    }
    if erreurs:
        probleme["errors"] = erreurs
    return Response(json.dumps(probleme, ensure_ascii=False), status=status, mimetype="application/problem+json")


def obtenir_signataire():
    return URLSafeTimedSerializer(current_app.secret_key, salt="hero-bearer-hmac")


def verifier_rate_limit():
    ip = request.remote_addr or "127.0.0.1"
    maintenant = time.time()
    recents = [t for t in historique_ip.get(ip, []) if maintenant - t < FENETRE_RL_SEC]
    if len(recents) >= QUOTA_MAX_REQUETES:
        attente = max(1, int(FENETRE_RL_SEC - (maintenant - recents[0])) + 1)
        rep = erreur_rfc7807(429, "Quota depasse", f"Reessayez dans {attente} secondes.")
        rep.headers["Retry-After"] = str(attente)
        rep.headers["X-RateLimit-Remaining"] = "0"
        return rep
    recents.append(maintenant)
    historique_ip[ip] = recents
    g.rl_restant = QUOTA_MAX_REQUETES - len(recents)
    return None


def exiger_role(*roles_autorises):
    def decorateur(vue):
        @functools.wraps(vue)
        def enveloppe(*args, **kwargs):
            identite = None
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                try:
                    identite = obtenir_signataire().loads(auth.split(" ", 1)[1].strip(), max_age=900)
                except (BadSignature, SignatureExpired):
                    rep = erreur_rfc7807(401, "Jeton invalide", "Bearer Token expire ou falsifie.")
                    rep.headers["WWW-Authenticate"] = 'Bearer realm="ISGP-Hero"'
                    return rep
            elif "utilisateur" in session:
                identite = {"sub": session["utilisateur"], "role": session.get("role", "stagiaire")}

            if not identite:
                rep = erreur_rfc7807(401, "Non authentifie", "Authentification Bearer ou Session requise.")
                rep.headers["WWW-Authenticate"] = 'Bearer realm="ISGP-Hero"'
                return rep

            if roles_autorises and identite.get("role") not in roles_autorises:
                return erreur_rfc7807(403, "Acces refuse (RBAC)", f"Role requis : {roles_autorises}.")

            g.identite = identite
            return vue(*args, **kwargs)
        return enveloppe
    return decorateur


# =====================================================================
# BLUEPRINT 1 : PORTAIL WEB JINJA2 (GET /)
# =====================================================================
portail_bp = Blueprint("portail_hero", __name__)


@portail_bp.route("/", methods=["GET"])
def page_portail_hero():
    return render_template(
        "etape_06_hero.html",
        titre_portail="Portail Web & API Catalogue des Formations ISGP (Etape 6 Hero)",
    ), 200


# =====================================================================
# BLUEPRINT 2 : AUTHENTIFICATION & CATALOGUE METIER (/api/v1)
# =====================================================================
api_v1_bp = Blueprint("api_v1_hero", __name__, url_prefix="/api/v1")


@api_v1_bp.route("/auth/login", methods=["POST"])
def login():
    corps = request.get_json(silent=True) or {}
    ident = str(corps.get("identifiant", "")).strip()
    mdp = str(corps.get("mot_de_passe", ""))
    compte = COMPTES.get(ident)
    if not compte or not hmac.compare_digest(mdp, compte["secret"]):
        rep = erreur_rfc7807(401, "Echec d'authentification", "Identifiant ou mot de passe incorrect.")
        rep.headers["WWW-Authenticate"] = 'Bearer realm="ISGP-Hero"'
        return rep
    charge = {"sub": ident, "role": compte["role"]}
    session["utilisateur"] = ident
    session["role"] = compte["role"]
    return jsonify({
        "access_token": obtenir_signataire().dumps(charge),
        "token_type": "Bearer",
        "role": compte["role"],
    }), 200


@api_v1_bp.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"statut": "deconnecte"}), 200


@api_v1_bp.route("/formations", methods=["GET"])
def lister_formations():
    blocage = verifier_rate_limit()
    if blocage is not None:
        return blocage
    db = get_db()
    domaine = request.args.get("domaine", "").strip()
    q = request.args.get("q", "").strip().lower()
    tri = request.args.get("tri", "id").strip()
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(50, max(1, request.args.get("limit", 10, type=int)))

    clauses, params = [], []
    if domaine:
        clauses.append("lower(domaine) = lower(?)")
        params.append(domaine)
    if q:
        clauses.append("(lower(titre) LIKE ? OR lower(code) LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])
    where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    sens = "DESC" if tri.startswith("-") else "ASC"
    col = tri.lstrip("-") if tri.lstrip("-") in CHAMPS_TRI else "id"

    total = db.execute(f"SELECT COUNT(*) FROM formations {where_sql}", params).fetchone()[0]
    lignes = db.execute(
        f"SELECT * FROM formations {where_sql} ORDER BY {col} {sens} LIMIT ? OFFSET ?",
        [*params, limit, (page - 1) * limit],
    ).fetchall()
    rep = jsonify({
        "meta": {"page": page, "limit": limit, "total": total, "total_pages": max(1, math.ceil(total / limit))},
        "data": [dict(r) for r in lignes],
    })
    rep.headers["X-RateLimit-Remaining"] = str(getattr(g, "rl_restant", QUOTA_MAX_REQUETES))
    return rep, 200


@api_v1_bp.route("/formations/<int:formation_id>", methods=["GET"])
def obtenir_formation(formation_id):
    ligne = get_db().execute("SELECT * FROM formations WHERE id = ?", (formation_id,)).fetchone()
    if not ligne:
        return erreur_rfc7807(404, "Introuvable", f"Formation #{formation_id} introuvable.")
    return jsonify({"data": dict(ligne)}), 200


@api_v1_bp.route("/formations", methods=["POST"])
@exiger_role("admin")
def creer_formation():
    corps = request.get_json(silent=True) or {}
    code = str(corps.get("code", "")).strip().upper()
    titre = str(corps.get("titre", "")).strip()
    try:
        jours = int(corps.get("duree_jours", 0))
        tarif = int(corps.get("tarif_dzd", -1))
    except (TypeError, ValueError):
        return erreur_rfc7807(422, "Types invalides", "duree_jours et tarif_dzd doivent etre entiers.")
    if len(code) < 3 or len(titre) < 4 or not (1 <= jours <= 30) or tarif < 0:
        return erreur_rfc7807(422, "Validation metier echouee", "Verifiez code, titre, duree_jours (1..30) et tarif_dzd.")
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO formations (code, titre, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
            (code, titre, str(corps.get("domaine", "Backend")).strip() or "Backend", jours, tarif),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return erreur_rfc7807(409, "Conflit SQL", f"Le code {code} existe deja.")
    creee = dict(db.execute("SELECT * FROM formations WHERE id = ?", (cur.lastrowid,)).fetchone())
    return jsonify({"data": creee}), 201


@api_v1_bp.route("/formations/<int:formation_id>", methods=["DELETE"])
@exiger_role("admin")
def supprimer_formation(formation_id):
    db = get_db()
    cur = db.execute("DELETE FROM formations WHERE id = ?", (formation_id,))
    db.commit()
    if cur.rowcount == 0:
        return erreur_rfc7807(404, "Introuvable", f"Formation #{formation_id} introuvable.")
    return jsonify({"statut": "supprime", "id": formation_id}), 200


# =====================================================================
# BLUEPRINT 3 : CONTRAT OPENAPI 3.1.0, SWAGGER UI & SONDE /health
# =====================================================================
docs_sante_bp = Blueprint("docs_sante_hero", __name__)


def construire_contrat_openapi_31():
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "API Catalogue des Formations ISGP — Edition Hero",
            "version": "1.0.0",
            "summary": "Portail Web & API RESTful Flask / Gunicorn (Zero-to-Hero Etape 6)",
        },
        "components": {
            "securitySchemes": {
                "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "HMAC-Signed"},
            },
            "schemas": {
                "FormationInput": {
                    "type": "object",
                    "required": ["code", "titre", "duree_jours", "tarif_dzd"],
                    "properties": {
                        "code": {"type": "string", "examples": ["PRO-601"]},
                        "titre": {"type": "string", "examples": ["Architecture Microservices"]},
                        "domaine": {"type": "string", "examples": ["Architecture"]},
                        "duree_jours": {"type": "integer", "minimum": 1, "maximum": 30},
                        "tarif_dzd": {"type": "integer", "minimum": 0},
                    },
                },
            },
        },
        "paths": {
            "/api/v1/auth/login": {
                "post": {
                    "tags": ["Securite"],
                    "summary": "Authentifier un operateur (stagiaire ou admin) et emettre Session + Bearer Token",
                    "responses": {"200": {"description": "Jeton emis"}, "401": {"description": "Identifiants invalides"}},
                }
            },
            "/api/v1/formations": {
                "get": {
                    "tags": ["Catalogue"],
                    "summary": "Rechercher, filtrer, trier et paginer les formations SQLite WAL",
                    "responses": {"200": {"description": "Enveloppe paginee"}, "429": {"description": "Quota depasse"}},
                },
                "post": {
                    "tags": ["Catalogue", "Securite"],
                    "summary": "Creer une formation dans SQLite (Role admin requis)",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/FormationInput"}}}},
                    "responses": {"201": {"description": "Creee"}, "401": {"description": "Non authentifie"}, "403": {"description": "Role insuffisant"}, "422": {"description": "Erreur RFC 7807"}},
                },
            },
            "/health": {
                "get": {"tags": ["Supervision"], "summary": "Sonde de sante WSGI & SQLite WAL", "responses": {"200": {"description": "Service sain"}}}
            },
        },
    }


@docs_sante_bp.route("/api/openapi.json", methods=["GET"])
def openapi_spec():
    return jsonify(construire_contrat_openapi_31()), 200


@docs_sante_bp.route("/api/docs", methods=["GET"])
def swagger_ui_page():
    return render_template(
        "etape_06_swagger_ui.html",
        page_title="Swagger UI — API Catalogue ISGP (OpenAPI 3.1.0)",
        header_title="ISGP — Documentation Interactive Swagger UI",
        openapi_url="/api/openapi.json",
    ), 200


@docs_sante_bp.route("/health", methods=["GET"])
@docs_sante_bp.route("/api/health", methods=["GET"])
def sonde_sante():
    mode_wal = get_db().execute("PRAGMA journal_mode;").fetchone()[0]
    return jsonify({
        "statut": "UP",
        "sqlite_journal_mode": mode_wal,
        "uptime_secondes": round(time.time() - DEMARRAGE, 2),
    }), 200


def create_app(db_path=None):
    """Application Factory industrielle prete pour Gunicorn et les tests isoles."""
    application = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))
    application.secret_key = os.environ.get("FLASK_SECRET_KEY", "cle-secrete-hero-isgp-2026")
    application.config.update(
        DATABASE_PATH=db_path or DB_DEFAUT,
        SESSION_COOKIE_NAME="isgp_hero_session",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    @application.before_request
    def avant_requete():
        g.t0 = time.perf_counter()
        g.request_id = request.headers.get("X-Request-ID") or f"hero-{uuid.uuid4().hex[:8]}"

    @application.after_request
    def apres_requete(reponse):
        ms = round((time.perf_counter() - getattr(g, "t0", time.perf_counter())) * 1000, 2)
        reponse.headers["X-Request-ID"] = getattr(g, "request_id", "inconnu")
        reponse.headers["X-Response-Time-Ms"] = str(ms)
        reponse.headers["X-Content-Type-Options"] = "nosniff"
        return reponse

    @application.teardown_appcontext
    def fermer_connexion(exc=None):
        conn = g.pop("db", None)
        if conn is not None:
            conn.close()

    with application.app_context():
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
            db.executemany(
                "INSERT INTO formations (code, titre, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
                [
                    ("API-101", "Fondamentaux HTTP/1.1 & JSON", "Architecture", 3, 45000),
                    ("FLK-201", "Services Web RESTful avec Flask", "Backend", 5, 65000),
                    ("SEC-401", "Securite Bearer HMAC, Cookies & RBAC", "Securite", 5, 75000),
                ],
            )
        db.commit()

    application.register_blueprint(portail_bp)
    application.register_blueprint(api_v1_bp)
    application.register_blueprint(docs_sante_bp)
    return application


app = create_app()

if __name__ == "__main__":
    with app.test_client() as client:
        r_home = client.get("/")
        assert r_home.status_code == 200 and "X-Request-ID" in r_home.headers
        assert client.get("/health").get_json()["statut"] == "UP"
        spec = client.get("/api/openapi.json").get_json()
        assert spec["openapi"] == "3.1.0"
        assert client.get("/api/docs").status_code == 200
        tok_stag = client.post("/api/v1/auth/login", json={"identifiant": "stagiaire", "mot_de_passe": "isgp-stagiaire-2026"}).get_json()["access_token"]
        client.post("/api/v1/auth/logout")
        assert client.post("/api/v1/formations", headers={"Authorization": f"Bearer {tok_stag}"}, json={"code": "HRO-1", "titre": "Interdit", "duree_jours": 3, "tarif_dzd": 50000}).status_code == 403
        tok_adm = client.post("/api/v1/auth/login", json={"identifiant": "admin", "mot_de_passe": "isgp-admin-2026"}).get_json()["access_token"]
        r_new = client.post("/api/v1/formations", headers={"Authorization": f"Bearer {tok_adm}"}, json={"code": "HRO-999", "titre": "Application Hero Complete", "domaine": "Architecture", "duree_jours": 5, "tarif_dzd": 80000})
        assert r_new.status_code == 201
        fid = r_new.get_json()["data"]["id"]
        assert client.delete(f"/api/v1/formations/{fid}", headers={"Authorization": f"Bearer {tok_adm}"}).status_code == 200
        print("[ETAPE 06 HERO OK] Blueprints + Factory + SQLite WAL + RBAC + OpenAPI 3.1.0 + Swagger UI valides.")

    if "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        print(f"[ETAPE 06 HERO] Portail Complet actif sur http://127.0.0.1:{port} (Swagger : /api/docs)")
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
