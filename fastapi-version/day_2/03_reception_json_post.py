# Fichier : day_2/03_reception_json_post.py
# Exécution : .venv/bin/python day_2/03_reception_json_post.py
# Objectif : Valider et désérialiser un corps JSON POST avec Pydantic v2 (BaseModel, Field) dans FastAPI.

import sys
import uvicorn
from fastapi import FastAPI, Response, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="ISGP - Réception JSON POST avec Pydantic v2", version="1.0.0")

INSCRIPTIONS = []


class InscriptionPayload(BaseModel):
    stagiaire: str = Field(..., min_length=3, max_length=80)
    code_formation: str = Field(..., pattern=r"^[A-Z]{3}-\d{3}$")
    duree_jours: int = Field(default=5, ge=1, le=30)


@app.post("/api/v1/inscriptions", status_code=status.HTTP_201_CREATED)
async def creer_inscription(payload: InscriptionPayload, response: Response):
    enregistrement = {"id": len(INSCRIPTIONS) + 1, **payload.model_dump()}
    INSCRIPTIONS.append(enregistrement)
    response.headers["Location"] = f"/api/v1/inscriptions/{enregistrement['id']}"
    return {"statut": "cree", "data": enregistrement}


if __name__ == "__main__":
    if "--serve" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8001)
    else:
        client = TestClient(app)
        rep_ok = client.post(
            "/api/v1/inscriptions",
            json={"stagiaire": "Yasmine Merabet", "code_formation": "FAP-201", "duree_jours": 5},
        )
        print("POST valide (201)   :", rep_ok.status_code, rep_ok.json())
        rep_err = client.post(
            "/api/v1/inscriptions",
            json={"stagiaire": "Y", "code_formation": "invalide", "duree_jours": 99},
        )
        print("POST invalide (422) :", rep_err.status_code, rep_err.json())
