# Fichier : day_4/06_authn_vs_authz_scopes.py
# Exécution : .venv/bin/python day_4/06_authn_vs_authz_scopes.py
# Objectif : Maîtriser la différence fondamentale en API Management entre :
#            1. AUTHENTIFICATION (AuthN) -> "Qui êtes-vous ?"       -> Échec = 401 Unauthorized
#            2. AUTORISATION     (AuthZ) -> "Quels sont vos droits ?" -> Échec = 403 Forbidden
#            (Contrôle par Rôle RBAC, par Permissions/Scopes OAuth2 et par Propriété BOLA)

import asyncio
import os
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.netutil
import tornado.web
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

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


class PortailAuthzHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("portail_d4_06.html")


class VerifierAccesHandler(tornado.web.RequestHandler):
    def get(self):
        cas = self.get_query_argument("cas", "amine_ok")
        tok_amine = signer.dumps({"sub": "amine", "role": "stagiaire", "scopes": ["formations:read", "dossiers:read"]})
        tok_dir = signer.dumps({"sub": "directeur", "role": "admin", "scopes": ["formations:read", "formations:write", "audit:admin"]})
        grille = {
            "sans_jeton": verifier_authn_et_authz(None, scope_requis="formations:read"),
            "echec_scope": verifier_authn_et_authz(tok_amine, scope_requis="formations:write"),
            "echec_bola": verifier_authn_et_authz(tok_amine, scope_requis="dossiers:read", ressource_proprietaire="sara"),
            "amine_ok": verifier_authn_et_authz(tok_amine, scope_requis="dossiers:read", ressource_proprietaire="amine"),
            "directeur_ok": verifier_authn_et_authz(tok_dir, role_requis="admin", scope_requis="audit:admin"),
        }
        code, message = grille.get(cas, grille["amine_ok"])
        self.set_status(code)
        self.write({"cas": cas, "statut_http": code, "diagnostic": message})


def make_app():
    dossier = os.path.dirname(os.path.abspath(__file__))
    return tornado.web.Application(
        [
            (r"/", PortailAuthzHandler),
            (r"/api/verifier-acces", VerifierAccesHandler),
        ],
        template_path=os.path.join(dossier, "templates"),
    )


async def _demo():
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

    app = make_app()
    bind_port = int(os.environ.get("PORT", 8889))
    try:
        sockets = tornado.netutil.bind_sockets(bind_port, "127.0.0.1")
    except OSError:
        sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()
    r_home = await client.fetch(f"http://127.0.0.1:{port}/")
    assert r_home.code == 200
    if "--once" in sys.argv:
        server.stop()
    else:
        print(f"\n[BOUCLE IOLOOP TORNADO ACTIVE] Serveur AuthN/AuthZ en écoute sur http://127.0.0.1:{port}")
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(_demo())
    except KeyboardInterrupt:
        print("\n[IOLOOP TORNADO] Arrêt propre demandé par l'utilisateur (Ctrl+C).")
