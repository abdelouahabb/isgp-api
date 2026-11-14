# Zero to Hero Tornado — Etape 6/6 : Application Finale "Hero" (Portail Web + SQLite WAL + Securite + OpenAPI 3.0 & Swagger UI)
# Execution : .venv/bin/python tornado-version/zero_to_hero/etape_06_hero_complet_swagger.py
# Couronnement du parcours : assemble dans une architecture Tornado complete :
#   - Portail Web HTML interactif (GET /) + Swagger UI (GET /api/docs) + Contrat OpenAPI 3.0.3 (GET /api/openapi.json)
#   - Sonde de sante (/health) + Journalisation d'audit structuree (log_function)
#   - SQLite3 WAL non-bloquant (ThreadPoolExecutor), Validation RFC 7807, Cookies HttpOnly, Bearer HMAC-SHA256, RBAC & 429

import asyncio
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import json
import math
import os
import sqlite3
import sys
import time
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

DOSSIER = os.path.dirname(os.path.abspath(__file__))
CHEMIN_DB = os.path.join(DOSSIER, "zero_to_hero_isgp.db")
DB_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="sqlite-hero")
DEMARRAGE = time.time()

SECRET_HMAC = os.environ.get("ISGP_HMAC_SECRET", "cle-hmac-sha256-zero-to-hero-isgp-2026")
COOKIE_SECRET = os.environ.get("ISGP_COOKIE_SECRET", "cle-cookie-signe-tornado-isgp-2026")

COMPTES_ISGP = {
    "stagiaire": {"mot_de_passe": "isgp2026", "role": "stagiaire"},
    "admin": {"mot_de_passe": "admin2026", "role": "admin"},
}

LIMITE_FENETRE = 15
DUREE_FENETRE_SEC = 15
FENETRES_QUOTA = {}
DOMAINES_VALIDES = {"Architecture", "Backend", "Data", "Securite", "DevOps"}
COLONNES_TRI = {"id": "id", "titre": "titre", "duree_jours": "duree_jours", "tarif_dzd": "tarif_dzd"}


def signer_jeton_hmac(identifiant, role, ttl_sec=900):
    corps = json.dumps({"sub": identifiant, "role": role, "exp": int(time.time()) + ttl_sec}, separators=(",", ":")).encode("utf-8")
    b64 = base64.urlsafe_b64encode(corps).decode("ascii").rstrip("=")
    sig = hmac.new(SECRET_HMAC.encode("utf-8"), b64.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{b64}.{sig}"


def verifier_jeton_hmac(jeton):
    if not jeton or "." not in jeton:
        return None, "Format Bearer invalide."
    b64, sig_recue = jeton.rsplit(".", 1)
    sig_attendue = hmac.new(SECRET_HMAC.encode("utf-8"), b64.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig_recue, sig_attendue):
        return None, "Signature HMAC-SHA256 invalide."
    charge = json.loads(base64.urlsafe_b64decode(b64 + ("=" * (-len(b64) % 4))).decode("utf-8"))
    if charge.get("exp", 0) < time.time():
        return None, "Jeton expire."
    return charge, None


def ouvrir_connexion():
    conn = sqlite3.connect(CHEMIN_DB, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


def initialiser_db():
    with ouvrir_connexion() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS formations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                titre TEXT NOT NULL,
                domaine TEXT NOT NULL,
                duree_jours INTEGER NOT NULL,
                tarif_dzd INTEGER NOT NULL
            )
        """)
        if conn.execute("SELECT COUNT(*) FROM formations").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO formations (code, titre, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
                [
                    ("ISGP-101", "Fondamentaux HTTP/1.1 & Architecture REST", "Architecture", 3, 45000),
                    ("ISGP-201", "Serveurs Asynchrones Tornado & IOLoop", "Backend", 5, 65000),
                    ("ISGP-204", "Persistance SQLite WAL & Integrite ACID", "Data", 4, 55000),
                    ("ISGP-301", "Securite API : HMAC, Cookies Signes & RBAC", "Securite", 5, 72000),
                ],
            )
        conn.commit()


async def executer_db(fn, *args):
    return await tornado.ioloop.IOLoop.current().run_in_executor(DB_EXECUTOR, fn, *args)


def construire_openapi():
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Portail & API Catalogue Formations ISGP — Edition Hero Tornado",
            "version": "6.0.0",
            "description": "Application finale du parcours Zero-to-Hero Tornado : CRUD SQLite WAL, RFC 7807, Cookies HttpOnly, Bearer HMAC-SHA256, RBAC et Rate-Limit.",
        },
        "servers": [{"url": "/", "description": "Instance Tornado courante"}],
        "components": {
            "securitySchemes": {
                "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "HMAC-SHA256"}
            },
            "schemas": {
                "FormationInput": {
                    "type": "object",
                    "required": ["code", "titre", "domaine", "duree_jours", "tarif_dzd"],
                    "properties": {
                        "code": {"type": "string", "example": "ISGP-601"},
                        "titre": {"type": "string", "example": "Architecture Microservices Tornado"},
                        "domaine": {"type": "string", "example": "Architecture"},
                        "duree_jours": {"type": "integer", "example": 5},
                        "tarif_dzd": {"type": "integer", "example": 70000},
                    },
                }
            },
        },
        "paths": {
            "/health": {"get": {"tags": ["Supervision"], "summary": "Sonde de sante applicative et SQLite WAL", "responses": {"200": {"description": "Service operationnel"}}}},
            "/api/v1/auth/token": {
                "post": {
                    "tags": ["Securite"],
                    "summary": "Emettre un jeton Bearer HMAC-SHA256 (stagiaire/isgp2026 ou admin/admin2026)",
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"identifiant": {"type": "string", "example": "admin"}, "mot_de_passe": {"type": "string", "example": "admin2026"}}}}}},
                    "responses": {"200": {"description": "Jeton emis"}, "401": {"description": "Identifiants invalides"}},
                }
            },
            "/api/v1/formations": {
                "get": {"tags": ["Formations"], "summary": "Lister, filtrer et paginer le catalogue SQLite WAL", "responses": {"200": {"description": "Catalogue pagine"}}},
                "post": {
                    "tags": ["Formations"],
                    "summary": "Creer une formation (Role admin requis)",
                    "security": [{"BearerAuth": []}],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/FormationInput"}}}},
                    "responses": {"201": {"description": "Formation creee"}, "401": {"description": "Non authentifie"}, "403": {"description": "Role insuffisant"}, "422": {"description": "Erreur RFC 7807"}},
                },
            },
            "/api/v1/formations/{id}": {
                "get": {"tags": ["Formations"], "summary": "Consulter une formation par ID", "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}], "responses": {"200": {"description": "Detail"}, "404": {"description": "Introuvable"}}},
                "delete": {"tags": ["Formations"], "summary": "Supprimer une formation (Role admin requis)", "security": [{"BearerAuth": []}], "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}], "responses": {"204": {"description": "Supprimee"}, "401": {"description": "Non authentifie"}, "403": {"description": "Interdit"}}},
            },
        },
    }



def _sql_sante():
    with ouvrir_connexion() as conn:
        jm = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        nb = conn.execute("SELECT COUNT(*) FROM formations;").fetchone()[0]
    return {"statut": "UP", "etape": 6, "sqlite_journal_mode": jm, "nb_formations": nb, "uptime_sec": round(time.time() - DEMARRAGE, 2)}


def _sql_lister(domaine, col, desc, limit, offset):
    sens = "DESC" if desc else "ASC"
    with ouvrir_connexion() as conn:
        if domaine:
            total = conn.execute("SELECT COUNT(*) FROM formations WHERE lower(domaine)=lower(?)", (domaine,)).fetchone()[0]
            rows = conn.execute(f"SELECT * FROM formations WHERE lower(domaine)=lower(?) ORDER BY {col} {sens} LIMIT ? OFFSET ?", (domaine, limit, offset)).fetchall()
        else:
            total = conn.execute("SELECT COUNT(*) FROM formations").fetchone()[0]
            rows = conn.execute(f"SELECT * FROM formations ORDER BY {col} {sens} LIMIT ? OFFSET ?", (limit, offset)).fetchall()
    return total, [dict(r) for r in rows]


def _sql_obtenir(fid):
    with ouvrir_connexion() as conn:
        row = conn.execute("SELECT * FROM formations WHERE id=?", (fid,)).fetchone()
        return dict(row) if row else None


def _sql_inserer(code, titre, domaine, jours, tarif):
    with ouvrir_connexion() as conn:
        cur = conn.execute(
            "INSERT INTO formations (code, titre, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
            (code, titre, domaine, jours, tarif),
        )
        conn.commit()
        return dict(conn.execute("SELECT * FROM formations WHERE id=?", (cur.lastrowid,)).fetchone())


def _sql_supprimer(fid):
    with ouvrir_connexion() as conn:
        cur = conn.execute("DELETE FROM formations WHERE id=?", (fid,))
        conn.commit()
        return cur.rowcount > 0


class HeroBaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("X-Content-Type-Options", "nosniff")
        self.set_header("X-Frame-Options", "SAMEORIGIN")

    def repondre_probleme(self, status, title, detail, errors=None):
        self.set_status(status)
        corps = {"type": "https://api.isgp.dz/problems/hero", "title": title, "status": status, "detail": detail, "instance": self.request.path}
        if errors:
            corps["errors"] = errors
        self.write(corps)
        self.set_header("Content-Type", "application/problem+json; charset=UTF-8")

    def prepare(self):
        if not self.request.path.startswith("/api/v1/"):
            return
        seau = self.request.headers.get("X-Client-Bucket") or self.request.remote_ip or "127.0.0.1"
        maintenant = time.time()
        recents = [t for t in FENETRES_QUOTA.get(seau, []) if maintenant - t < DUREE_FENETRE_SEC]
        if len(recents) >= LIMITE_FENETRE:
            attente = max(1, int(DUREE_FENETRE_SEC - (maintenant - recents[0])) + 1)
            self.set_header("Retry-After", str(attente))
            self.repondre_probleme(429, "Quota depasse", "Trop de requetes sur la fenetre glissante.")
            self.finish()
            return
        recents.append(maintenant)
        FENETRES_QUOTA[seau] = recents
        self.set_header("X-RateLimit-Remaining", str(LIMITE_FENETRE - len(recents)))

    def exiger_acces(self, role_requis=None):
        entete = self.request.headers.get("Authorization", "")
        identite = None
        err = "Authentification requise."
        if entete.startswith("Bearer "):
            identite, err = verifier_jeton_hmac(entete.split(" ", 1)[1].strip())
        else:
            brut = self.get_secure_cookie("isgp_session", max_age_days=1)
            if brut:
                identite = tornado.escape.json_decode(brut)
        if not identite:
            self.set_header("WWW-Authenticate", 'Bearer realm="ISGP-API"')
            self.repondre_probleme(401, "Non authentifie (401)", err)
            return None
        if role_requis and identite.get("role") != role_requis:
            self.repondre_probleme(403, "Interdit RBAC (403)", f"Role '{role_requis}' requis.")
            return None
        return identite



class PortailHeroHandler(HeroBaseHandler):
    def get(self):
        self.render("etape_06_hero.html", titre_page="Portail Formations ISGP — Etape 6 (Hero Complet & Swagger)")


class HealthProbeHandler(HeroBaseHandler):
    async def get(self):
        self.write(await executer_db(_sql_sante))


class OpenApiSpecHandler(HeroBaseHandler):
    def get(self):
        self.write(construire_openapi())


class SwaggerDocsHandler(HeroBaseHandler):
    def get(self):
        self.render(
            "etape_06_swagger_ui.html",
            page_title="Swagger UI — API Hero ISGP (Tornado)",
            header_title="ISGP — Documentation Interactive OpenAPI 3.0.3 (Etape 6 Hero)",
            openapi_url="/api/openapi.json",
        )


class HeroTokenHandler(HeroBaseHandler):
    def post(self):
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        ident = str(corps.get("identifiant", "")).strip()
        mdp = str(corps.get("mot_de_passe", ""))
        fiche = COMPTES_ISGP.get(ident)
        if not fiche or not hmac.compare_digest(mdp, fiche["mot_de_passe"]):
            self.set_header("WWW-Authenticate", 'Bearer realm="ISGP-API"')
            return self.repondre_probleme(401, "Identifiants invalides", "Verifiez identifiant / mot_de_passe.")
        self.write({"access_token": signer_jeton_hmac(ident, fiche["role"]), "token_type": "Bearer", "role": fiche["role"]})


class HeroCookieLoginHandler(HeroBaseHandler):
    def post(self):
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        ident = str(corps.get("identifiant", "")).strip()
        mdp = str(corps.get("mot_de_passe", ""))
        fiche = COMPTES_ISGP.get(ident)
        if not fiche or not hmac.compare_digest(mdp, fiche["mot_de_passe"]):
            return self.repondre_probleme(401, "Identifiants invalides", "Ouverture de session refusee.")
        self.set_secure_cookie("isgp_session", json.dumps({"sub": ident, "role": fiche["role"]}), expires_days=1, httponly=True, samesite="Lax", path="/")
        self.write({"statut": "Cookie HttpOnly actif", "sub": ident, "role": fiche["role"]})


class HeroLogoutHandler(HeroBaseHandler):
    def post(self):
        self.clear_cookie("isgp_session", path="/")
        self.write({"statut": "Deconnecte"})


class HeroFormationsHandler(HeroBaseHandler):
    async def get(self):
        domaine = self.get_query_argument("domaine", "").strip()
        tri = self.get_query_argument("tri", "id").strip() or "id"
        page = max(1, int(self.get_query_argument("page", "1")))
        limit = min(50, max(1, int(self.get_query_argument("limit", "20"))))
        col = COLONNES_TRI.get(tri.lstrip("-"), "id")
        total, items = await executer_db(_sql_lister, domaine, col, tri.startswith("-"), limit, (page - 1) * limit)
        self.write({"meta": {"page": page, "limit": limit, "total": total, "total_pages": max(1, math.ceil(total / limit))}, "data": items})

    async def post(self):
        if not self.exiger_acces(role_requis="admin"):
            return
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        code = str(corps.get("code", "")).strip()
        titre = str(corps.get("titre", "")).strip()
        domaine = str(corps.get("domaine", "Architecture")).strip()
        jours = int(corps.get("duree_jours", 5))
        tarif = int(corps.get("tarif_dzd", 60000))
        if len(code) < 3 or len(titre) < 4 or domaine not in DOMAINES_VALIDES or not (1 <= jours <= 30) or tarif < 0:
            return self.repondre_probleme(422, "Validation RFC 7807 echouee", "Verifiez code, titre, domaine, duree_jours et tarif_dzd.")
        try:
            cree = await executer_db(_sql_inserer, code, titre, domaine, jours, tarif)
        except sqlite3.IntegrityError:
            return self.repondre_probleme(409, "Conflit SQLite", "Ce code formation existe deja.")
        self.set_status(201)
        self.write({"data": cree})


class HeroFormationItemHandler(HeroBaseHandler):
    async def get(self, id_str):
        item = await executer_db(_sql_obtenir, int(id_str))
        if not item:
            return self.repondre_probleme(404, "Introuvable", f"Formation #{id_str} absente.")
        self.write({"data": item})

    async def delete(self, id_str):
        if not self.exiger_acces(role_requis="admin"):
            return
        ok = await executer_db(_sql_supprimer, int(id_str))
        if not ok:
            return self.repondre_probleme(404, "Introuvable", f"Formation #{id_str} absente.")
        self.set_status(204)
        self.finish()


def journaliser_audit(handler):
    ms = round(handler.request.request_time() * 1000.0, 2)
    print(f"[AUDIT HERO] HTTP {handler.get_status()} | {handler.request.method} {handler.request.uri} | {ms} ms")


def make_app():
    initialiser_db()
    return tornado.web.Application(
        [
            (r"/", PortailHeroHandler),
            (r"/health", HealthProbeHandler),
            (r"/api/bonjour", HealthProbeHandler),
            (r"/api/openapi.json", OpenApiSpecHandler),
            (r"/api/docs", SwaggerDocsHandler),
            (r"/api/v1/auth/token", HeroTokenHandler),
            (r"/api/v1/auth/cookie-login", HeroCookieLoginHandler),
            (r"/api/v1/auth/logout", HeroLogoutHandler),
            (r"/api/v1/formations", HeroFormationsHandler),
            (r"/api/v1/formations/([0-9]+)", HeroFormationItemHandler),
        ],
        template_path=os.path.join(DOSSIER, "templates"),
        cookie_secret=COOKIE_SECRET,
        log_function=journaliser_audit,
    )


async def main():
    port_cible = int(os.environ.get("PORT", 8889))
    try:
        sockets = tornado.netutil.bind_sockets(port_cible, "127.0.0.1")
    except OSError:
        sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(make_app())
    server.add_sockets(sockets)

    client = tornado.httpclient.AsyncHTTPClient()
    r_home = await client.fetch(f"http://127.0.0.1:{port}/")
    r_docs = await client.fetch(f"http://127.0.0.1:{port}/api/docs")
    r_spec = await client.fetch(f"http://127.0.0.1:{port}/api/openapi.json")
    r_hlth = await client.fetch(f"http://127.0.0.1:{port}/health")
    assert r_home.code == 200 and "text/html" in r_home.headers["Content-Type"]
    assert r_docs.code == 200 and "SwaggerUIBundle" in r_docs.body.decode("utf-8")
    assert tornado.escape.json_decode(r_spec.body)["openapi"] == "3.0.3"
    assert tornado.escape.json_decode(r_hlth.body)["statut"] == "UP"

    if "--once" in sys.argv:
        r_adm = await client.fetch(
            f"http://127.0.0.1:{port}/api/v1/auth/token",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"identifiant": "admin", "mot_de_passe": "admin2026"}),
        )
        tok = tornado.escape.json_decode(r_adm.body)["access_token"]
        r_c = await client.fetch(
            f"http://127.0.0.1:{port}/api/v1/formations",
            method="POST",
            headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
            body=json.dumps({"code": "HERO-TMP-6", "titre": "Validation Hero Complete", "domaine": "Architecture", "duree_jours": 5, "tarif_dzd": 75000}),
        )
        cid = tornado.escape.json_decode(r_c.body)["data"]["id"]
        r_d = await client.fetch(
            f"http://127.0.0.1:{port}/api/v1/formations/{cid}",
            method="DELETE",
            headers={"Authorization": f"Bearer {tok}"},
        )
        assert r_d.code == 204
        print(f"[ETAPE 6 HERO OK] Portail : http://127.0.0.1:{port}/ | Swagger : http://127.0.0.1:{port}/api/docs")
        server.stop()
        return

    print(f"[ETAPE 6 HERO OK] Portail Web : http://127.0.0.1:{port}/ | Swagger UI : http://127.0.0.1:{port}/api/docs | Sante : http://127.0.0.1:{port}/health")
    print("Serveur Tornado actif (Ctrl+C pour arreter).")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
