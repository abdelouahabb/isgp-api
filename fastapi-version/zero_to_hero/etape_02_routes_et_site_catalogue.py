# Fichier : zero_to_hero/etape_02_routes_et_site_catalogue.py
# Etape 2/6 : Catalogue filtrable, triable et pagine (Query, Path) + Portail HTML interactif
import asyncio
import math
import os
import sys
from typing import Literal
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))

app = FastAPI(
    title="Portail Web & API Catalogue Formations ISGP - Etape 02",
    version="0.2.0",
    description="Etape 2 : Filtrage Query, parametre Path valide et pagination REST.",
)

CATALOGUE_FORMATIONS: list[dict] = [
    {"id": 1, "code": "ISGP-API-201", "intitule": "Architecture REST & FastAPI", "domaine": "Architecture SI", "duree_jours": 5, "tarif_dzd": 95000},
    {"id": 2, "code": "ISGP-SEC-305", "intitule": "Securite des APIs, OAuth2 & Zero-Trust", "domaine": "Cybersecurite", "duree_jours": 4, "tarif_dzd": 88000},
    {"id": 3, "code": "ISGP-GOV-110", "intitule": "Pilotage de la Transformation Numerique Publique", "domaine": "Management Public", "duree_jours": 3, "tarif_dzd": 72000},
    {"id": 4, "code": "ISGP-DAT-240", "intitule": "Ingenierie des Donnees & SQLite en Production", "domaine": "Data & IA", "duree_jours": 5, "tarif_dzd": 99000},
    {"id": 5, "code": "ISGP-ARC-310", "intitule": "Microservices Asynchrones & Contrats OpenAPI 3.1", "domaine": "Architecture SI", "duree_jours": 4, "tarif_dzd": 91000},
]


@app.get("/", response_class=HTMLResponse, summary="Portail Web interactif du catalogue ISGP")
async def page_catalogue(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="etape_02_catalogue.html",
        context={"titre_page": "Portail Formations ISGP - Etape 02 : Catalogue & Filtres"},
    )


@app.get("/api/bonjour", summary="Salutation JSON heritee de l'etape 01")
async def api_bonjour() -> dict[str, str | int]:
    return {"institut": "ISGP", "etape": 2, "statut": "operationnel"}


@app.get("/api/v1/formations", summary="Lister, filtrer, trier et paginer les formations")
async def lister_formations(
    domaine: str | None = Query(default=None, description="Filtrer par domaine exact"),
    recherche: str | None = Query(default=None, min_length=1, max_length=80, description="Mot-cle dans l'intitule"),
    tri: Literal["id", "tarif_dzd", "duree_jours"] = Query(default="id", description="Champ de tri croissant"),
    page: int = Query(default=1, ge=1, description="Numero de page (1-indexe)"),
    taille: int = Query(default=5, ge=1, le=20, description="Nombre d'elements par page"),
) -> dict:
    resultats = list(CATALOGUE_FORMATIONS)
    if domaine:
        resultats = [f for f in resultats if f["domaine"].lower() == domaine.lower()]
    if recherche:
        terme = recherche.lower()
        resultats = [f for f in resultats if terme in f["intitule"].lower() or terme in f["code"].lower()]
    resultats.sort(key=lambda item: item[tri])

    total_elements = len(resultats)
    total_pages = max(1, math.ceil(total_elements / taille))
    debut = (page - 1) * taille
    tranche = resultats[debut : debut + taille]
    return {
        "meta": {
            "page": page,
            "taille": taille,
            "total_elements": total_elements,
            "total_pages": total_pages,
            "tri": tri,
        },
        "data": tranche,
    }


@app.get("/api/v1/formations/{formation_id}", summary="Consulter une formation par son identifiant")
async def obtenir_formation(
    formation_id: int = Path(..., ge=1, description="Identifiant entier positif de la formation"),
) -> dict:
    for formation in CATALOGUE_FORMATIONS:
        if formation["id"] == formation_id:
            return formation
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Aucune formation trouvee pour l'identifiant {formation_id}.",
    )


async def _auto_test() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/")).status_code == 200
        rep_liste = await client.get("/api/v1/formations?domaine=Architecture+SI&tri=tarif_dzd&page=1&taille=2")
        assert rep_liste.status_code == 200
        corps = rep_liste.json()
        assert corps["meta"]["total_elements"] == 2 and corps["data"][0]["tarif_dzd"] <= corps["data"][1]["tarif_dzd"]
        rep_detail = await client.get("/api/v1/formations/1")
        assert rep_detail.status_code == 200 and rep_detail.json()["code"] == "ISGP-API-201"
        assert (await client.get("/api/v1/formations/999")).status_code == 404
        assert (await client.get("/api/v1/formations/0")).status_code == 422
        print("[OK] Etape 02 validee : GET /, GET /api/v1/formations (Query/tri/page) et Path ge=1.")


if __name__ == "__main__":
    if "--once" in sys.argv:
        asyncio.run(_auto_test())
    else:
        uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8001)))
