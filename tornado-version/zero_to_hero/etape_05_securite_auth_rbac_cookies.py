# Zero to Hero Tornado — Etape 5/6 : Securite API (Cookies Signes, Bearer HMAC-SHA256, RBAC 401/403 & Rate-Limit 429)
# Execution : .venv/bin/python tornado-version/zero_to_hero/etape_05_securite_auth_rbac_cookies.py
# Evolution depuis l'Etape 4 : ajout de set_secure_cookie (HttpOnly, SameSite=Lax), jetons Bearer HMAC-SHA256
# verifies via hmac.compare_digest, distinction 401 (WWW-Authenticate) vs 403 RBAC et quota glissant 429.

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
DB_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="sqlite-sec")

SECRET_HMAC = os.environ.get("ISGP_HMAC_SECRET", "cle-hmac-sha256-zero-to-hero-isgp-2026")
COOKIE_SECRET = os.environ.get("ISGP_COOKIE_SECRET", "cle-cookie-signe-tornado-isgp-2026")

COMPTES_ISGP = {
    "stagiaire": {"mot_de_passe": "isgp2026", "role": "stagiaire"},
    "admin": {"mot_de_passe": "admin2026", "role": "admin"},
}

LIMITE_FENETRE = 8
DUREE_FENETRE_SEC = 15
FENETRES_QUOTA = {}

DOMAINES_VALIDES = {"Architecture", "Backend", "Data", "Securite", "DevOps"}


def signer_jeton_hmac(identifiant, role, ttl_sec=600):
    corps = json.dumps({"sub": identifiant, "role": role, "exp": int(time.time()) + ttl_sec}, separators=(",", ":")).encode("utf-8")
    b64 = base64.urlsafe_b64encode(corps).decode("ascii").rstrip("=")
    sig = hmac.new(SECRET_HMAC.encode("utf-8"), b64.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{b64}.{sig}"


def verifier_jeton_hmac(jeton):
    if not jeton or "." not in jeton:
        return None, "Format de jeton Bearer invalide."
    b64, sig_recue = jeton.rsplit(".", 1)
    sig_attendue = hmac.new(SECRET_HMAC.encode("utf-8"), b64.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig_recue, sig_attendue):
        return None, "Signature HMAC-SHA256 invalide."
    remplissage = "=" * (-len(b64) % 4)
    charge = json.loads(base64.urlsafe_b64decode(b64 + remplissage).decode("utf-8"))
    if charge.get("exp", 0) < time.time():
        return None, "Jeton Bearer expire."
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
                    ("ISGP-301", "Securite API : HMAC, Cookies Signes & RBAC", "Securite", 5, 72000),
                ],
            )
        conn.commit()


async def executer_db(fn, *args):
    return await tornado.ioloop.IOLoop.current().run_in_executor(DB_EXECUTOR, fn, *args)


class BaseSecuriseeHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("X-Content-Type-Options", "nosniff")

    def repondre_probleme(self, status, title, detail, errors=None):
        self.set_status(status)
        corps = {"type": "https://api.isgp.dz/problems/security", "title": title, "status": status, "detail": detail, "instance": self.request.path}
        if errors:
            corps["errors"] = errors
        self.write(corps)
        self.set_header("Content-Type", "application/problem+json; charset=UTF-8")

    def prepare(self):
        if not self.request.path.startswith("/api/"):
            return
        seau = self.request.headers.get("X-Client-Bucket") or self.request.remote_ip or "127.0.0.1"
        maintenant = time.time()
        recents = [t for t in FENETRES_QUOTA.get(seau, []) if maintenant - t < DUREE_FENETRE_SEC]
        if len(recents) >= LIMITE_FENETRE:
            attente = max(1, int(DUREE_FENETRE_SEC - (maintenant - recents[0])) + 1)
            self.set_header("Retry-After", str(attente))
            self.set_header("X-RateLimit-Limit", str(LIMITE_FENETRE))
            self.set_header("X-RateLimit-Remaining", "0")
            self.repondre_probleme(429, "Quota depasse (429 Too Many Requests)", f"Limite de {LIMITE_FENETRE} appels / {DUREE_FENETRE_SEC}s atteinte.")
            self.finish()
            return
        recents.append(maintenant)
        FENETRES_QUOTA[seau] = recents
        self.set_header("X-RateLimit-Limit", str(LIMITE_FENETRE))
        self.set_header("X-RateLimit-Remaining", str(LIMITE_FENETRE - len(recents)))

    def extraire_identite(self):
        entete = self.request.headers.get("Authorization", "")
        if entete.startswith("Bearer "):
            charge, err = verifier_jeton_hmac(entete.split(" ", 1)[1].strip())
            if err:
                return None, err
            charge["canal"] = "Bearer HMAC-SHA256"
            return charge, None
        brut = self.get_secure_cookie("isgp_session", max_age_days=1)
        if brut:
            data = tornado.escape.json_decode(brut)
            data["canal"] = "Cookie Signe Tornado (HttpOnly, SameSite=Lax)"
            return data, None
        return None, "Aucune preuve d'identite fournie (Bearer ou Cookie)."

    def exiger_acces(self, role_requis=None):
        identite, err = self.extraire_identite()
        if not identite:
            self.set_header("WWW-Authenticate", 'Bearer realm="ISGP-API"')
            self.repondre_probleme(401, "Authentification requise (401)", err)
            return None
        if role_requis and identite.get("role") != role_requis:
            self.repondre_probleme(403, "Acces refuse RBAC (403 Forbidden)", f"Role '{role_requis}' requis (votre role : '{identite.get('role')}').")
            return None
        return identite


class AccueilSecuriteHandler(BaseSecuriseeHandler):
    def get(self):
        self.render("etape_05_securite.html", titre_page="Portail Formations ISGP — Etape 5 (Auth, Cookies, RBAC & 429)")


class AuthBearerHandler(BaseSecuriseeHandler):
    def post(self):
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        ident = str(corps.get("identifiant", "")).strip()
        mdp = str(corps.get("mot_de_passe", ""))
        fiche = COMPTES_ISGP.get(ident)
        if not fiche or not hmac.compare_digest(mdp, fiche["mot_de_passe"]):
            self.set_header("WWW-Authenticate", 'Bearer realm="ISGP-API"')
            return self.repondre_probleme(401, "Identifiants invalides", "Compte ou mot de passe incorrect.")
        jeton = signer_jeton_hmac(ident, fiche["role"])
        self.write({"access_token": jeton, "token_type": "Bearer", "role": fiche["role"], "expires_in": 600})


class AuthCookieLoginHandler(BaseSecuriseeHandler):
    def post(self):
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        ident = str(corps.get("identifiant", "")).strip()
        mdp = str(corps.get("mot_de_passe", ""))
        fiche = COMPTES_ISGP.get(ident)
        if not fiche or not hmac.compare_digest(mdp, fiche["mot_de_passe"]):
            return self.repondre_probleme(401, "Identifiants invalides", "Echec d'ouverture de session cookie.")
        valeur = json.dumps({"sub": ident, "role": fiche["role"]})
        self.set_secure_cookie("isgp_session", valeur, expires_days=1, httponly=True, samesite="Lax", path="/")
        self.write({"statut": "Session Cookie HttpOnly activee", "sub": ident, "role": fiche["role"]})


class AuthLogoutHandler(BaseSecuriseeHandler):
    def post(self):
        self.clear_cookie("isgp_session", path="/")
        self.write({"statut": "Cookie isgp_session revoque"})


class AuthSessionInspectHandler(BaseSecuriseeHandler):
    def get(self):
        identite = self.exiger_acces()
        if identite:
            self.write({"authentifie": True, "identite": identite})



def _sql_lister(limit):
    with ouvrir_connexion() as conn:
        rows = conn.execute("SELECT * FROM formations ORDER BY id ASC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


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


class FormationsProtegeesHandler(BaseSecuriseeHandler):
    async def get(self):
        limit = min(50, max(1, int(self.get_query_argument("limit", "20"))))
        lignes = await executer_db(_sql_lister, limit)
        self.write({"meta": {"total": len(lignes)}, "data": lignes})

    async def post(self):
        if not self.exiger_acces(role_requis="admin"):
            return
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        code = str(corps.get("code", "")).strip()
        titre = str(corps.get("titre", "")).strip()
        domaine = str(corps.get("domaine", "Securite")).strip()
        jours = int(corps.get("duree_jours", 4))
        tarif = int(corps.get("tarif_dzd", 50000))
        if len(code) < 3 or len(titre) < 4 or domaine not in DOMAINES_VALIDES:
            return self.repondre_probleme(422, "Validation echouee", "Champs formation invalides.")
        try:
            cree = await executer_db(_sql_inserer, code, titre, domaine, jours, tarif)
        except sqlite3.IntegrityError:
            return self.repondre_probleme(409, "Conflit SQLite", "Code deja existant.")
        self.set_status(201)
        self.write({"data": cree})


class FormationProtegeeItemHandler(BaseSecuriseeHandler):
    async def delete(self, id_str):
        if not self.exiger_acces(role_requis="admin"):
            return
        ok = await executer_db(_sql_supprimer, int(id_str))
        if not ok:
            return self.repondre_probleme(404, "Introuvable", f"Formation #{id_str} absente.")
        self.set_status(204)
        self.finish()


def make_app():
    initialiser_db()
    return tornado.web.Application(
        [
            (r"/", AccueilSecuriteHandler),
            (r"/api/v1/auth/token", AuthBearerHandler),
            (r"/api/v1/auth/cookie-login", AuthCookieLoginHandler),
            (r"/api/v1/auth/logout", AuthLogoutHandler),
            (r"/api/v1/auth/session", AuthSessionInspectHandler),
            (r"/api/v1/formations", FormationsProtegeesHandler),
            (r"/api/v1/formations/([0-9]+)", FormationProtegeeItemHandler),
        ],
        template_path=os.path.join(DOSSIER, "templates"),
        cookie_secret=COOKIE_SECRET,
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
    r_html = await client.fetch(f"http://127.0.0.1:{port}/")
    assert r_html.code == 200 and "text/html" in r_html.headers["Content-Type"]
    if "--once" in sys.argv:
        r_401 = await client.fetch(f"http://127.0.0.1:{port}/api/v1/auth/session", headers={"X-Client-Bucket": "t1"}, raise_error=False)
        assert r_401.code == 401 and "Bearer" in r_401.headers.get("WWW-Authenticate", "")
        r_stag = await client.fetch(
            f"http://127.0.0.1:{port}/api/v1/auth/token",
            method="POST",
            headers={"Content-Type": "application/json", "X-Client-Bucket": "t1"},
            body=json.dumps({"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}),
        )
        tok_stag = tornado.escape.json_decode(r_stag.body)["access_token"]
        r_403 = await client.fetch(
            f"http://127.0.0.1:{port}/api/v1/formations",
            method="POST",
            headers={"Authorization": f"Bearer {tok_stag}", "Content-Type": "application/json", "X-Client-Bucket": "t1"},
            body=json.dumps({"code": "NOPE-1", "titre": "Interdit Stagiaire"}),
            raise_error=False,
        )
        assert r_403.code == 403
        r_cookie = await client.fetch(
            f"http://127.0.0.1:{port}/api/v1/auth/cookie-login",
            method="POST",
            headers={"Content-Type": "application/json", "X-Client-Bucket": "t2"},
            body=json.dumps({"identifiant": "admin", "mot_de_passe": "admin2026"}),
        )
        sc = r_cookie.headers["Set-Cookie"]
        assert "HttpOnly" in sc and "SameSite=Lax" in sc
        dernier_code = 200
        for _ in range(LIMITE_FENETRE + 2):
            rr = await client.fetch(f"http://127.0.0.1:{port}/api/v1/formations", headers={"X-Client-Bucket": "t-burst"}, raise_error=False)
            dernier_code = rr.code
            if dernier_code == 429:
                assert "Retry-After" in rr.headers
                break
        assert dernier_code == 429
        print(f"[ETAPE 5 OK] Cookies HttpOnly + Bearer HMAC + 401/403 RBAC + 429 valides sur http://127.0.0.1:{port}/")
        server.stop()
        return

    print(f"[ETAPE 5 OK] Portail Securise : http://127.0.0.1:{port}/ | Session : http://127.0.0.1:{port}/api/v1/auth/session")
    print("Serveur Tornado actif (Ctrl+C pour arreter).")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
