import sys
import os
# Fichier : day_1/05_outils_curl_postman_httpie.py
# Exécution : .venv/bin/python day_1/05_outils_curl_postman_httpie.py
# Objectif : Comprendre les commandes 'curl' équivalentes et les exécuter contre une API FastAPI :
#   1. Les requêtes GET avec Query Parameters (?page=1&limit=2)
#   2. Les en-têtes d'authentification (-H 'X-API-Key: ...')
#   3. L'envoi d'un Payload JSON (-H 'Content-Type: application/json' -d '{...}')
#   4. L'envoi d'un Formulaire HTML (-d 'cle=valeur' en application/x-www-form-urlencoded)

from typing import Optional
from fastapi import FastAPI, Form, Header, HTTPException, Query, status
from fastapi.testclient import TestClient
from pydantic import BaseModel

BASE_URL = "http://127.0.0.1:8000"

app = FastAPI(title="ISGP - Laboratoire cURL & FastAPI", version="1.0.0")


class IdentifiantsIn(BaseModel):
    identifiant: str
    mot_de_passe: str


@app.get("/api/sandbox/formations")
async def lister_formations(page: int = Query(1, ge=1), limit: int = Query(2, ge=1, le=50)):
    catalogue = [
        {"id": 1, "titre": "Architecture API REST & FastAPI", "duree_jours": 5},
        {"id": 2, "titre": "Sécurité OAuth2, JWT & RBAC", "duree_jours": 3},
        {"id": 3, "titre": "Déploiement Uvicorn & Nginx", "duree_jours": 4},
    ]
    debut = (page - 1) * limit
    return {"page": page, "limit": limit, "items": catalogue[debut : debut + limit]}


@app.get("/api/sandbox/admin-stats")
async def stats_admin(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
    if x_api_key != "isgp-secret-2026":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clé API invalide ou absente")
    return {"statut": "autorise", "serveur": "Uvicorn/ASGI", "formations_actives": 3}


@app.post("/api/sandbox/auth/token", status_code=status.HTTP_201_CREATED)
async def generer_token(creds: IdentifiantsIn):
    if creds.identifiant == "stagiaire" and creds.mot_de_passe == "isgp2026":
        return {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.isgp_demo", "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants incorrects")


@app.post("/api/sandbox/formulaire-formation", status_code=status.HTTP_201_CREATED)
async def soumettre_formulaire(
    titre: str = Form(...),
    formateur: str = Form(...),
    duree_jours: int = Form(...),
    salle: str = Form(...),
):
    return {
        "mode_reception": "Form(application/x-www-form-urlencoded)",
        "formation_creee": {"titre": titre, "formateur": formateur, "duree_jours": duree_jours, "salle": salle},
    }


def simuler_commande_curl(client: TestClient, titre: str, commande_curl: str, response):
    print("=" * 74)
    print(f"TEST : {titre}")
    print(f"COMMANDE : {commande_curl}")
    print("-" * 74)
    print(f"HTTP/1.1 {response.status_code} {response.reason_phrase}")
    for k, v in response.headers.items():
        print(f"{k}: {v}")
    print()
    print(response.text)
    print()


if __name__ == "__main__":
    client = TestClient(app)

    # 1. Requête GET avec '-i' (inclut la Status Line et les Headers HTTP de réponse)
    simuler_commande_curl(
        client,
        "1. GET avec inspection des en-têtes (-i) et paramètres d'URL",
        f"curl -s -i '{BASE_URL}/api/sandbox/formations?page=1&limit=2'",
        client.get("/api/sandbox/formations?page=1&limit=2"),
    )

    # 2. Requête Authentifiée par Clé API (-H 'X-API-Key: ...')
    simuler_commande_curl(
        client,
        "2. GET protégé par en-tête de sécurité (-H 'X-API-Key: isgp-secret-2026')",
        f"curl -s -i -H 'X-API-Key: isgp-secret-2026' '{BASE_URL}/api/sandbox/admin-stats'",
        client.get("/api/sandbox/admin-stats", headers={"X-API-Key": "isgp-secret-2026"}),
    )

    # 3. Requête POST envoyant un Payload JSON (-X POST -H 'Content-Type: application/json' -d '{...}')
    simuler_commande_curl(
        client,
        "3. POST envoyant un corps JSON (validé par Pydantic BaseModel côté FastAPI)",
        f"curl -s -i -X POST -H 'Content-Type: application/json' -d '{{\"identifiant\": \"stagiaire\", \"mot_de_passe\": \"isgp2026\"}}' '{BASE_URL}/api/sandbox/auth/token'",
        client.post("/api/sandbox/auth/token", json={"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}),
    )

    # 4. Requête POST envoyant des données de Formulaire HTML (-d 'cle=valeur' -> application/x-www-form-urlencoded)
    simuler_commande_curl(
        client,
        "4. POST simulant un Formulaire HTML <form> (lu par Form(...) côté FastAPI)",
        f"curl -s -i -X POST -d 'titre=Atelier+Curl+Formulaire&formateur=ISGP&duree_jours=3&salle=Salle+B' '{BASE_URL}/api/sandbox/formulaire-formation'",
        client.post(
            "/api/sandbox/formulaire-formation",
            data={"titre": "Atelier Curl Formulaire", "formateur": "ISGP", "duree_jours": 3, "salle": "Salle B"},
        ),
    )
    if "--once" not in sys.argv:
        import uvicorn
        port = int(os.environ.get("PORT", 8001))
        print("\n" + "=" * 76)
        print(f"[BOUCLE ASGI UVICORN / FASTAPI ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Interface Swagger UI interactive : http://127.0.0.1:{port}/docs")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur ASGI.")
        print("=" * 76)
        uvicorn.run(app, host="0.0.0.0", port=port)
