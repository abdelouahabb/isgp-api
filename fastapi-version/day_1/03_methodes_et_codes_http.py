# Fichier : day_1/03_methodes_et_codes_http.py
# Exécution : .venv/bin/python day_1/03_methodes_et_codes_http.py
# Objectif : Illustrer la matrice des méthodes HTTP (GET, POST, PUT, PATCH, DELETE)
#            et les codes de statut RFC 9110 avec FastAPI (status.HTTP_200_OK, 201, 204, 404, 422).

from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="ISGP - Méthodes HTTP & Codes de Statut", version="1.0.0")

BASE_FORMATIONS = {
    1: {"id": 1, "titre": "Ingénierie FastAPI & ASGI", "duree_jours": 5},
}


class FormationComplete(BaseModel):
    titre: str = Field(..., min_length=3)
    duree_jours: int = Field(..., ge=1, le=30)


class FormationPartielle(BaseModel):
    titre: Optional[str] = Field(None, min_length=3)
    duree_jours: Optional[int] = Field(None, ge=1, le=30)


@app.get("/api/v1/formations/{formation_id}", status_code=status.HTTP_200_OK)
async def lire_formation(formation_id: int):
    if formation_id not in BASE_FORMATIONS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formation introuvable")
    return BASE_FORMATIONS[formation_id]


@app.post("/api/v1/formations", status_code=status.HTTP_201_CREATED)
async def creer_formation(payload: FormationComplete, response: Response):
    nouvel_id = max(BASE_FORMATIONS.keys(), default=0) + 1
    BASE_FORMATIONS[nouvel_id] = {"id": nouvel_id, **payload.model_dump()}
    response.headers["Location"] = f"/api/v1/formations/{nouvel_id}"
    return BASE_FORMATIONS[nouvel_id]


@app.put("/api/v1/formations/{formation_id}", status_code=status.HTTP_200_OK)
async def remplacer_formation(formation_id: int, payload: FormationComplete):
    BASE_FORMATIONS[formation_id] = {"id": formation_id, **payload.model_dump()}
    return BASE_FORMATIONS[formation_id]


@app.patch("/api/v1/formations/{formation_id}", status_code=status.HTTP_200_OK)
async def modifier_formation(formation_id: int, payload: FormationPartielle):
    if formation_id not in BASE_FORMATIONS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formation introuvable")
    for cle, val in payload.model_dump(exclude_unset=True).items():
        BASE_FORMATIONS[formation_id][cle] = val
    return BASE_FORMATIONS[formation_id]


@app.delete("/api/v1/formations/{formation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def supprimer_formation(formation_id: int):
    if formation_id not in BASE_FORMATIONS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formation introuvable")
    del BASE_FORMATIONS[formation_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    client = TestClient(app)
    print("=== MATRICE DES VERBES ET CODES HTTP DANS FASTAPI ===")
    print("1. GET existant (200)   :", client.get("/api/v1/formations/1").status_code)
    print("2. GET inexistant (404) :", client.get("/api/v1/formations/99").status_code)
    print("3. POST valide (201)    :", client.post("/api/v1/formations", json={"titre": "Sécurité JWT", "duree_jours": 3}).status_code)
    print("4. POST invalide (422)  :", client.post("/api/v1/formations", json={"titre": "AB", "duree_jours": 99}).status_code)
    print("5. PATCH partiel (200)  :", client.patch("/api/v1/formations/1", json={"duree_jours": 4}).json())
    print("6. DELETE (204)         :", client.delete("/api/v1/formations/2").status_code)
