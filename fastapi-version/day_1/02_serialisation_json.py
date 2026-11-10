import sys
import os
# Fichier : day_1/02_serialisation_json.py
# Exécution : .venv/bin/python day_1/02_serialisation_json.py
# Objectif : Structurer une enveloppe JSON professionnelle avec Pydantic v2 et FastAPI (ISO 8601)

from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field


# 1. Définition déclarative des schémas de réponse avec Pydantic v2
class MetaReponse(BaseModel):
    api_version: str = "1.0"
    horodatage_iso8601: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    statut_succes: bool = True


class DonneesFormation(BaseModel):
    id: int
    intitule: str
    organisme: str = "ISGP"
    prerequis_exiges: Optional[str] = None
    methodes_idempotentes: list[str]
    methodes_non_idempotentes: list[str]


class EnveloppeReponseAPI(BaseModel):
    meta: MetaReponse
    data: DonneesFormation


app = FastAPI(title="ISGP - Sérialisation JSON & Pydantic v2", version="1.0.0")


@app.get("/api/v1/enveloppe", response_model=EnveloppeReponseAPI)
async def obtenir_enveloppe_normalisee():
    return EnveloppeReponseAPI(
        meta=MetaReponse(),
        data=DonneesFormation(
            id=101,
            intitule="Développement d'APIs et services web avec FastAPI",
            organisme="ISGP",
            prerequis_exiges=None,
            methodes_idempotentes=["GET", "PUT", "DELETE"],
            methodes_non_idempotentes=["POST"],
        ),
    )


if __name__ == "__main__":
    client = TestClient(app)
    rep = client.get("/api/v1/enveloppe")
    objet_pydantic = EnveloppeReponseAPI.model_validate(rep.json())

    # 2. Sérialisation Pydantic v2 (model_dump_json -> Chaîne JSON UTF-8)
    texte_json = objet_pydantic.model_dump_json(indent=2)
    print("=== ENVELOPPE JSON NORMALISÉE (Pydantic model_dump_json) ===")
    print(texte_json)

    # 3. Désérialisation et validation (model_validate_json -> Modèle Python typé)
    retour_modele = EnveloppeReponseAPI.model_validate_json(texte_json)
    print("\n=== LECTURE EN PYTHON (Pydantic model_validate_json) ===")
    print("Horodatage UTC :", retour_modele.meta.horodatage_iso8601)
    print("Méthodes idempotentes :", retour_modele.data.methodes_idempotentes)
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
