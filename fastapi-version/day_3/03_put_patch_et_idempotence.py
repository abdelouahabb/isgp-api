import os
# Fichier : day_3/03_put_patch_et_idempotence.py
# Exécution : .venv/bin/python day_3/03_put_patch_et_idempotence.py
# Objectif : Différencier PUT (remplacement complet) de PATCH (modification partielle avec exclude_unset=True)
#            et sécuriser POST contre les doublons avec l'en-tête Idempotency-Key dans FastAPI.

import sys
from typing import Optional
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Path, Response, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="ISGP - PUT vs PATCH & Idempotency-Key", version="1.0.0")

formations = {
    1: {"id": 1, "titre": "Architecture des APIs REST & FastAPI", "duree_jours": 5, "salle": "Salle A"}
}
# Cache des clés d'idempotence déjà traitées : {"cle-unique-client": reponse_memorisee}
cles_idempotence = {}


class FormationComplete(BaseModel):
    titre: str = Field(..., min_length=3)
    duree_jours: int = Field(default=5, ge=1, le=30)
    salle: str = Field(default="Salle A")


class FormationPartielle(BaseModel):
    titre: Optional[str] = Field(default=None, min_length=3)
    duree_jours: Optional[int] = Field(default=None, ge=1, le=30)
    salle: Optional[str] = Field(default=None)


# 1. POST SÉCURISÉ PAR IDEMPOTENCY-KEY (Évite les créations en doublon si le réseau coupe)
@app.post("/api/v1/formations", status_code=status.HTTP_201_CREATED)
async def creer_avec_idempotence(
    payload: FormationComplete,
    response: Response,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
):
    cle_idem = (idempotency_key or "").strip()
    if cle_idem and cle_idem in cles_idempotence:
        # La requête a déjà été traitée : on renvoie exactement le résultat initial sans recréer !
        response.status_code = status.HTTP_200_OK
        return {"rejoue_sans_doublon": True, "formation": cles_idempotence[cle_idem]}

    nouvel_id = max(formations.keys(), default=0) + 1
    nouvelle = {
        "id": nouvel_id,
        "titre": payload.titre,
        "duree_jours": payload.duree_jours,
        "salle": payload.salle,
    }
    formations[nouvel_id] = nouvelle
    if cle_idem:
        cles_idempotence[cle_idem] = nouvelle
    return {"rejoue_sans_doublon": False, "formation": nouvelle}


# 2. PUT : REMPLACEMENT INTÉGRAL (Tous les champs du schéma FormationComplete sont appliqués)
@app.put("/api/v1/formations/{id}")
async def remplacer_formation_put(payload: FormationComplete, id: int = Path(..., ge=1)):
    if id not in formations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Introuvable")
    formations[id] = {
        "id": id,
        "titre": payload.titre,
        "duree_jours": payload.duree_jours,
        "salle": payload.salle,
    }
    return {"methode": "PUT (remplacement complet)", "formation": formations[id]}


# 3. PATCH : MODIFICATION PARTIELLE (payload.model_dump(exclude_unset=True) ne touche qu'aux champs envoyés)
@app.patch("/api/v1/formations/{id}")
async def modifier_partiellement_patch(payload: FormationPartielle, id: int = Path(..., ge=1)):
    if id not in formations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Introuvable")
    actuelle = formations[id]
    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        actuelle[champ] = valeur
    return {"methode": "PATCH (mise à jour partielle)", "formation": actuelle}


if __name__ == "__main__":
    client = TestClient(app)
    print("=== 1. TEST POST AVEC IDEMPOTENCY-KEY (Pas de doublon au 2e envoi) ===")
    r1 = client.post("/api/v1/formations", json={"titre": "Sécurité JWT", "duree_jours": 3}, headers={"Idempotency-Key": "idem-001"})
    r2 = client.post("/api/v1/formations", json={"titre": "Sécurité JWT", "duree_jours": 3}, headers={"Idempotency-Key": "idem-001"})
    print("1er appel (201) :", r1.status_code, r1.json())
    print("2e appel  (200) :", r2.status_code, r2.json())

    print("\n=== 2. TEST PATCH PARTIEL (exclude_unset=True) ===")
    r_patch = client.patch("/api/v1/formations/1", json={"salle": "Amphithéâtre Alger"})
    print("PATCH /api/v1/formations/1 :", r_patch.json())
    if os.environ.get("ISGP_WEB_RUNNER") != "1" and "--once" not in sys.argv:
        import uvicorn
        port = int(os.environ.get("PORT", 8001))
        print("\n" + "=" * 76)
        print(f"[BOUCLE ASGI UVICORN / FASTAPI ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Interface Swagger UI interactive : http://127.0.0.1:{port}/docs")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur ASGI.")
        print("=" * 76)
        uvicorn.run(app, host="0.0.0.0", port=port)
