# Fichier : day_5/01_client_python_auth.py
# Exécution : .venv/bin/python day_5/01_client_python_auth.py
# Objectif : Construire un client HTTP Python résilient (Timeouts, Exponential Backoff sur 429/503,
#            gestion des codes 401/403 et Bearer Token) avec httpx.AsyncClient / urllib.request et FastAPI.

import asyncio
import json
import time
import urllib.error
import urllib.request
from typing import Optional
import httpx
from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel

BASE_URL = "http://127.0.0.1:8000"

# Serveur FastAPI cible embarqué pour démontrer le cycle complet d'authentification et de résilience
app = FastAPI(title="ISGP - Serveur Cible pour Client Python Résilient", version="1.0.0")


class LoginRequest(BaseModel):
    identifiant: str
    mot_de_passe: str


@app.post("/api/sandbox/auth/token")
async def emettre_token(payload: LoginRequest):
    if payload.identifiant == "stagiaire" and payload.mot_de_passe == "isgp2026":
        return {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.isgp_stagiaire_2026",
            "token_type": "Bearer",
            "expires_in": 300,
        }
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")


@app.get("/api/sandbox/auth/profil")
async def lire_profil(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer Token requis")
    return {
        "utilisateur": "stagiaire",
        "organisme": "ISGP",
        "role": "ingenieur_api_fastapi",
        "statut_verification": "Jeton Bearer authentifié avec succès",
    }


def appeler_api_urllib_avec_backoff(url: str, method: str = "GET", headers: Optional[dict] = None, payload: Optional[dict] = None, timeout: float = 5.0, max_essais: int = 3):
    """Client HTTP standard (urllib.request) avec Timeout obligatoire et Exponential Backoff (429/503)."""
    entetes = {"Accept": "application/json"}
    if headers:
        entetes.update(headers)
    corps_octets = json.dumps(payload).encode("utf-8") if payload is not None else None
    if corps_octets is not None:
        entetes["Content-Type"] = "application/json"

    for tentative in range(1, max_essais + 1):
        requete = urllib.request.Request(url, data=corps_octets, headers=entetes, method=method)
        try:
            with urllib.request.urlopen(requete, timeout=timeout) as reponse:
                return reponse.status, json.loads(reponse.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code in (429, 502, 503, 504) and tentative < max_essais:
                delai = 2 ** (tentative - 1)
                time.sleep(delai)
                continue
            return err.code, json.loads(err.read().decode("utf-8") or "{}")


async def executer_client_asynchrone():
    # Utilisation de httpx.AsyncClient + ASGITransport avec Timeout explicite de 5.0 secondes
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=BASE_URL, timeout=5.0) as client:
        # 1. Authentification initiale pour obtenir le Bearer Token
        rep_login = await client.post(
            "/api/sandbox/auth/token",
            json={"identifiant": "stagiaire", "mot_de_passe": "isgp2026"},
        )
        mon_token = rep_login.json()["access_token"]
        print(f"1. [HTTP {rep_login.status_code}] Jeton Bearer obtenu : {mon_token[:32]}...")

        # 2. Appel de la route protégée en injectant l'en-tête Authorization
        rep_profil = await client.get(
            "/api/sandbox/auth/profil",
            headers={"Authorization": f"Bearer {mon_token}"},
        )
        print(f"2. [HTTP {rep_profil.status_code}] Profil sécurisé reçu :")
        print(json.dumps(rep_profil.json(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(executer_client_asynchrone())
