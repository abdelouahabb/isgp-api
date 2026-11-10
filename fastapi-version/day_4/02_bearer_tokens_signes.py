# Fichier : day_4/02_bearer_tokens_signes.py
# Exécution : .venv/bin/python day_4/02_bearer_tokens_signes.py
# Objectif : Émettre et vérifier un Bearer Token signé avec HTTPBearer / Header et URLSafeTimedSerializer dans FastAPI.

import os
import sys
from typing import Optional
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.testclient import TestClient
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import BaseModel

app = FastAPI(title="ISGP - Bearer Tokens Signés & HTTPBearer", version="1.0.0")
SECRET_KEY = os.environ.get("API_SECRET_KEY", "secret-signature-isgp-2026")
signer = URLSafeTimedSerializer(SECRET_KEY)
schema_bearer = HTTPBearer(auto_error=False)


class ConnexionPayload(BaseModel):
    identifiant: str
    mot_de_passe: str


# 1. ROUTE DE CONNEXION : Émission du Bearer Token signé
@app.post("/api/auth/token")
async def generer_token(corps: ConnexionPayload):
    if corps.identifiant != "stagiaire" or corps.mot_de_passe != "isgp2026":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")

    charge_utile = {"utilisateur": corps.identifiant, "role": "participant_isgp"}
    token = signer.dumps(charge_utile)
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in_seconds": 300,
    }


# 2. DÉPENDANCE DE VÉRIFICATION DU BEARER TOKEN
async def extraire_utilisateur_token(authorization: Optional[str] = Header(default=None)) -> dict:
    entete_auth = authorization or ""
    if not entete_auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="En-tête 'Authorization: Bearer <token>' requis",
        )
    token = entete_auth.split(" ", 1)[1].strip()
    try:
        return signer.loads(token, max_age=300)  # Expire après 300s (5 min)
    except SignatureExpired:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Le jeton (Token) a expiré")
    except BadSignature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature du jeton invalide (jeton falsifié)")


# 3. ROUTE PROTÉGÉE : Vérification automatique par injection de dépendance Depends()
@app.get("/api/auth/profil")
async def profil_protege(donnees_utilisateur: dict = Depends(extraire_utilisateur_token)):
    return {"acces": "Token vérifié", "profil": donnees_utilisateur}


if __name__ == "__main__":
    client = TestClient(app)
    r_tok = client.post("/api/auth/token", json={"identifiant": "stagiaire", "mot_de_passe": "isgp2026"})
    jeton = r_tok.json()["access_token"]
    print("1. Jeton émis :", jeton[:36] + "...")
    r_prof = client.get("/api/auth/profil", headers={"Authorization": f"Bearer {jeton}"})
    print("2. Profil protégé (200) :", r_prof.status_code, r_prof.json())
    r_faux = client.get("/api/auth/profil", headers={"Authorization": f"Bearer {jeton} falsifie"})
    print("3. Jeton falsifié (401) :", r_faux.status_code, r_faux.json())
    if "--once" not in sys.argv:
        import uvicorn
        import socket as _sock
        port = int(os.environ.get("PORT", 8001))
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
            if _s.connect_ex(("127.0.0.1", port)) == 0:
                _s2 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                _s2.bind(("127.0.0.1", 0))
                port = _s2.getsockname()[1]
                _s2.close()
        print("\n" + "=" * 76)
        print(f"[BOUCLE ASGI UVICORN / FASTAPI ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Interface Swagger UI interactive : http://127.0.0.1:{port}/docs")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur ASGI.")
        print("=" * 76)
        uvicorn.run(app, host="0.0.0.0", port=port)
