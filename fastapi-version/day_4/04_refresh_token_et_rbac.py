# Fichier : day_4/04_refresh_token_et_rbac.py
# Exécution : .venv/bin/python day_4/04_refresh_token_et_rbac.py
# Objectif : Implémenter l'injection de dépendances Depends(exiger_role("admin")) pour le contrôle
#            d'accès RBAC (401 vs 403), le renouvellement par Refresh Token et la révocation (Blacklist).

import os
import sys
from typing import Optional
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.testclient import TestClient
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import BaseModel

app = FastAPI(title="ISGP - Refresh Token & RBAC via Depends()", version="1.0.0")
SECRET_KEY = os.environ.get("API_SECRET_KEY", "secret-signature-isgp-2026")
access_signer = URLSafeTimedSerializer(SECRET_KEY, salt="access-token")
refresh_signer = URLSafeTimedSerializer(SECRET_KEY, salt="refresh-token")

# Liste noire (Blacklist) des jetons révoqués lors d'une déconnexion (Logout)
jetons_revoques: set[str] = set()


class LoginPayload(BaseModel):
    identifiant: str = "stagiaire"


class RefreshPayload(BaseModel):
    refresh_token: str


# 1. USINE DE DÉPENDANCE FASTAPI POUR L'AUTHENTIFICATION ET LE CONTRÔLE DE RÔLE (RBAC)
def exiger_role(role_minimum: Optional[str] = None):
    async def dependance_rbac(authorization: Optional[str] = Header(default=None)) -> dict:
        auth = authorization or ""
        if not auth.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="401 Unauthorized : Bearer Token manquant")

        token = auth.split(" ", 1)[1].strip()
        if token in jetons_revoques:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="401 Unauthorized : Ce jeton a été révoqué (déconnecté)")

        try:
            utilisateur = access_signer.loads(token, max_age=300)
        except SignatureExpired:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="401 Unauthorized : Access Token expiré. Utilisez /api/auth/refresh")
        except BadSignature:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="401 Unauthorized : Signature du jeton invalide")

        # Vérification du Rôle (RBAC) : 403 Forbidden si authentifié mais droits insuffisants !
        if role_minimum and utilisateur.get("role") != role_minimum:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"403 Forbidden : Rôle '{role_minimum}' requis (votre rôle : '{utilisateur.get('role')}')",
            )
        return utilisateur

    return dependance_rbac


# 2. LOGIN : Émet un Access Token (5 min) ET un Refresh Token (7 jours)
@app.post("/api/auth/login")
async def login(corps: LoginPayload):
    identifiant = corps.identifiant
    role = "admin" if identifiant == "directeur" else "stagiaire"
    payload = {"sub": identifiant, "role": role}
    return {
        "access_token": access_signer.dumps(payload),
        "refresh_token": refresh_signer.dumps(payload),
        "token_type": "Bearer",
        "access_expires_in": 300,
        "refresh_expires_in": 604800,
    }


# 3. REFRESH : Échange un Refresh Token valide contre un nouvel Access Token neuf
@app.post("/api/auth/refresh")
async def rafraichir_token(corps: RefreshPayload):
    try:
        payload = refresh_signer.loads(corps.refresh_token, max_age=604800)
        nouvel_access = access_signer.dumps(payload)
        return {"access_token": nouvel_access, "expires_in": 300}
    except (BadSignature, SignatureExpired):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh Token invalide ou expiré")


# 4. ROUTE RÉSERVÉE AU RÔLE 'admin' VIA Depends(exiger_role("admin")) (Démontre 401 vs 403)
@app.get("/api/admin/audit")
async def consulter_audit_admin(utilisateur: dict = Depends(exiger_role("admin"))):
    return {"acces": "Autorisé (Admin)", "operateur": utilisateur["sub"]}


if __name__ == "__main__":
    if "--serve" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8001)
    else:
        client = TestClient(app)
        tok_stagiaire = client.post("/api/auth/login", json={"identifiant": "stagiaire"}).json()["access_token"]
        tok_directeur = client.post("/api/auth/login", json={"identifiant": "directeur"}).json()["access_token"]

        print("1. Sans jeton (401)         :", client.get("/api/admin/audit").status_code)
        print("2. Jeton stagiaire (403)    :", client.get("/api/admin/audit", headers={"Authorization": f"Bearer {tok_stagiaire}"}).status_code)
        r_adm = client.get("/api/admin/audit", headers={"Authorization": f"Bearer {tok_directeur}"})
        print("3. Jeton directeur (200)    :", r_adm.status_code, r_adm.json())
