# Fichier : day_3/01_api_crud_memoire.py
# Exécution : .venv/bin/python day_3/01_api_crud_memoire.py
# Objectif : Validation déclarative stricte avec Pydantic v2 (BaseModel, Field, @field_validator)
#            et réponses d'erreur normalisées 422 Unprocessable Entity (RFC 7807 Problem Details).

import sys
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="ISGP - Validation Stricte Pydantic v2 & RFC 7807", version="1.0.0")

formations = [
    {"id": 1, "titre": "Architecture des APIs REST & FastAPI", "duree_jours": 5, "salle": "Salle A"},
    {"id": 2, "titre": "Python & Pydantic v2 pour l'Entreprise", "duree_jours": 3, "salle": "Salle B"},
]


# 1. SCHÉMA PYDANTIC V2 : Typage strict, bornes Field(ge=1, le=30) et @field_validator personnalisé
class FormationCreation(BaseModel):
    titre: str = Field(..., min_length=3, max_length=120, description="Intitulé officiel de la formation")
    duree_jours: int = Field(default=5, ge=1, le=30, description="Durée en jours ouvrés (1 à 30)")
    salle: str = Field(default="Salle Principale", min_length=2, max_length=60)

    @field_validator("titre")
    @classmethod
    def nettoyer_et_valider_titre(cls, valeur: str) -> str:
        nettoye = valeur.strip()
        if len(nettoye) < 3:
            raise ValueError("Le titre ne peut pas contenir uniquement des espaces (min 3 caractères).")
        return nettoye


# 2. ENVELOPPE D'ERREUR RFC 7807 (Problem Details) SUR TOUTE ERREUR DE VALIDATION 422
@app.exception_handler(RequestValidationError)
async def formater_erreur_rfc7807(request: Request, exc: RequestValidationError):
    champs_en_erreur = {}
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []) if x != "body") or "_corps"
        champs_en_erreur[loc] = err.get("msg", "Valeur invalide")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "https://isgp.dz/erreurs/validation-echouee",
            "title": "Données d'entrée invalides (Validation Pydantic v2)",
            "status": 422,
            "instance": str(request.url.path),
            "champs_en_erreur": champs_en_erreur,
            "detail": exc.errors(),
        },
    )


@app.get("/api/v1/formations")
async def lister_formations():
    return {"total": len(formations), "donnees": formations}


@app.post("/api/v1/formations", status_code=status.HTTP_201_CREATED)
async def creer_formation(payload: FormationCreation):
    nouvel_id = max([f["id"] for f in formations], default=0) + 1
    nouvelle = {
        "id": nouvel_id,
        "titre": payload.titre,
        "duree_jours": payload.duree_jours,
        "salle": payload.salle.strip(),
    }
    formations.append(nouvelle)
    return {"message": "Formation créée", "formation": nouvelle}


if __name__ == "__main__":
    if "--serve" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8001)
    else:
        client = TestClient(app)
        print("=== 1. TEST CRÉATION VALIDE (201 Created) ===")
        rep_ok = client.post("/api/v1/formations", json={"titre": "Sécurité OAuth2 & JWT", "duree_jours": 4, "salle": "Labo 1"})
        print("Statut :", rep_ok.status_code, "| Réponse :", rep_ok.json())

        print("\n=== 2. TEST VALIDATION ÉCHOUÉE (422 Unprocessable Entity - RFC 7807) ===")
        rep_ko = client.post("/api/v1/formations", json={"titre": "AB", "duree_jours": 99})
        print("Statut :", rep_ko.status_code)
        print("Problem Details RFC 7807 :", rep_ko.json())
