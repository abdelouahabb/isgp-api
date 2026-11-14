# Fichier : day_4/06_authn_vs_authz_scopes.py
# Exécution : .venv/bin/python day_4/06_authn_vs_authz_scopes.py
# Objectif : Maîtriser la différence fondamentale en API Management avec FastAPI entre :
#            1. AUTHENTIFICATION (AuthN) -> "Qui êtes-vous ?"       -> Échec = 401 Unauthorized
#            2. AUTORISATION     (AuthZ) -> "Quels sont vos droits ?" -> Échec = 403 Forbidden
#            (Contrôle par Rôle RBAC, par Permissions/Scopes OAuth2 et par Propriété BOLA)

import os
import sys
from typing import Optional
from fastapi import Depends, FastAPI, Header, HTTPException, Path, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SECRET_KEY = "secret-api-management-isgp-2026"
signer = URLSafeTimedSerializer(SECRET_KEY)

# Base de données simulée de dossiers confidentiels (chaque dossier appartient à un propriétaire)
DOSSIERS = {
    101: {"id": 101, "proprietaire": "amine", "note_evaluation": 17.5},
    102: {"id": 102, "proprietaire": "sara", "note_evaluation": 18.0},
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


# Application FastAPI illustrant la protection anti-BOLA et la vérification des Scopes
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="ISGP - AuthN (401) vs AuthZ (403, Scopes, Anti-BOLA)", version="1.0.0")
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))


async def extraire_jeton(authorization: Optional[str] = Header(default=None)) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.split(" ", 1)[1].strip()


@app.get("/api/v1/dossiers/{dossier_id}")
async def lire_dossier(dossier_id: int = Path(...), token: Optional[str] = Depends(extraire_jeton)):
    dossier = DOSSIERS.get(dossier_id)
    if not dossier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dossier introuvable")
    code, msg = verifier_authn_et_authz(token, scope_requis="dossiers:read", ressource_proprietaire=dossier["proprietaire"])
    if code != 200:
        raise HTTPException(status_code=code, detail=msg)
    return {"message": msg, "dossier": dossier}


@app.get("/", response_class=HTMLResponse)
async def portail_scopes(request: Request):
    tok_amine = signer.dumps({"sub": "amine", "role": "stagiaire", "scopes": ["formations:read", "dossiers:read"]})
    tok_admin = signer.dumps({"sub": "directeur", "role": "admin", "scopes": ["formations:read", "dossiers:read", "audit:admin"]})
    return templates.TemplateResponse(
        request=request,
        name="portail_06_scopes.html",
        context={"token_amine": tok_amine, "token_admin": tok_admin},
    )


if __name__ == "__main__":
    # Émission de 2 jetons avec des rôles et des scopes différents
    token_amine = signer.dumps({
        "sub": "amine",
        "role": "stagiaire",
        "scopes": ["formations:read", "dossiers:read"],
    })
    token_directeur = signer.dumps({
        "sub": "directeur",
        "role": "admin",
        "scopes": ["formations:read", "formations:write", "audit:admin"],
    })

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

    client = TestClient(app)
    assert client.get("/").status_code == 200
    print("\n=== 6. TEST FASTAPI ANTI-BOLA SUR /api/v1/dossiers/102 ===")
    print("Amine sur dossier 102 (Sara) ->", client.get("/api/v1/dossiers/102", headers={"Authorization": f"Bearer {token_amine}"}).status_code)
    print("Amine sur dossier 101 (Amine)->", client.get("/api/v1/dossiers/101", headers={"Authorization": f"Bearer {token_amine}"}).status_code)
    if "--once" not in sys.argv:
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8001)))
