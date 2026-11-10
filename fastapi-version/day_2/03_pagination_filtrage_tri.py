import os
# Fichier : day_2/03_pagination_filtrage_tri.py
# Exécution : .venv/bin/python day_2/03_pagination_filtrage_tri.py
# Objectif : Implémenter la pagination, le filtrage, le tri dynamique avec Query(...)
#            et la réception d'un corps JSON typé avec Pydantic BaseModel dans FastAPI.

import math
import sys
from typing import Literal, Optional
import uvicorn
from fastapi import FastAPI, Query, Response, status
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="ISGP - Pagination, Filtrage, Tri & Réception JSON", version="1.0.0")

CATALOGUE = [
    {"id": 1, "code": "API-101", "titre": "Fondamentaux HTTP & REST", "duree_jours": 2, "salle": "Salle A"},
    {"id": 2, "code": "FAP-201", "titre": "Développement API avec FastAPI & ASGI", "duree_jours": 5, "salle": "Salle A"},
    {"id": 3, "code": "SQL-202", "titre": "Persistance SQLite & Transactions", "duree_jours": 3, "salle": "Salle B"},
    {"id": 4, "code": "SEC-301", "titre": "Sécurité, Bearer Tokens & HMAC", "duree_jours": 4, "salle": "Labo 1"},
    {"id": 5, "code": "OPS-302", "titre": "Rate Limiting & Résilience", "duree_jours": 2, "salle": "Labo 1"},
    {"id": 6, "code": "PRO-401", "titre": "Architecture APIRouter & Production", "duree_jours": 5, "salle": "Salle B"},
]


class FormationCreation(BaseModel):
    code: str = Field(..., min_length=3, max_length=15, examples=["FAP-305"])
    titre: str = Field(..., min_length=3, max_length=120)
    duree_jours: int = Field(..., ge=1, le=30)
    salle: str = Field(default="Salle A")


@app.get("/api/v1/formations")
async def rechercher_formations(
    salle: Optional[str] = Query(default=None, description="Filtrer par salle (ex: Salle A)"),
    min_jours: int = Query(default=1, ge=1, le=30, description="Durée minimale en jours"),
    tri: Literal["id", "duree_jours", "titre"] = Query(default="id", description="Champ de tri"),
    ordre: Literal["asc", "desc"] = Query(default="asc", description="Sens du tri"),
    page: int = Query(default=1, ge=1, description="Numéro de page"),
    limit: int = Query(default=3, ge=1, le=50, description="Éléments par page"),
):
    # 1. FILTRAGE
    salle_filtre = (salle or "").strip()
    resultats = [
        f for f in CATALOGUE
        if f["duree_jours"] >= min_jours
        and (not salle_filtre or f["salle"].lower() == salle_filtre.lower())
    ]

    # 2. TRI DYNAMIQUE
    resultats.sort(key=lambda x: x[tri], reverse=(ordre == "desc"))

    # 3. PAGINATION
    total_elements = len(resultats)
    total_pages = max(1, math.ceil(total_elements / limit))
    debut = (page - 1) * limit
    tranche_page = resultats[debut : debut + limit]

    return {
        "meta": {
            "page_actuelle": page,
            "elements_par_page": limit,
            "total_elements": total_elements,
            "total_pages": total_pages,
            "a_page_suivante": page < total_pages,
            "a_page_precedente": page > 1,
        },
        "data": tranche_page,
    }


@app.post("/api/v1/formations", status_code=status.HTTP_201_CREATED)
async def ajouter_formation(payload: FormationCreation, response: Response):
    nouvel_id = max((f["id"] for f in CATALOGUE), default=0) + 1
    nouvelle = {"id": nouvel_id, **payload.model_dump()}
    CATALOGUE.append(nouvelle)
    response.headers["Location"] = f"/api/v1/formations/{nouvel_id}"
    return {"statut": "cree", "data": nouvelle}


if __name__ == "__main__":
    client = TestClient(app)
    print("=== 1. TEST PAGINATION, FILTRAGE ET TRI (Query FastAPI) ===")
    rep = client.get("/api/v1/formations?page=1&limit=2&salle=Salle+A&tri=duree_jours&ordre=desc")
    print("Statut HTTP :", rep.status_code)
    print("Meta        :", rep.json()["meta"])
    print("Data        :", rep.json()["data"])

    print("\n=== 2. TEST RÉCEPTION JSON POST (Pydantic BaseModel) ===")
    rep_post = client.post(
        "/api/v1/formations",
        json={"code": "FAP-305", "titre": "Injection de Dépendances FastAPI", "duree_jours": 3, "salle": "Salle A"},
    )
    print("Statut POST :", rep_post.status_code, "| Location :", rep_post.headers.get("location"))
    print("Payload     :", rep_post.json())
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
