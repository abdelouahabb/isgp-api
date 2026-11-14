# Fichier : zero_to_hero/etape_03_crud_et_validation_rfc7807.py
# Etape 3/6 : CRUD complet (POST, PUT, PATCH exclude_unset, DELETE), Pydantic v2 & RFC 7807
import asyncio
import math
import os
import sys
from typing import Literal
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))

app = FastAPI(
    title="Portail Web & API Catalogue Formations ISGP - Etape 03",
    version="0.3.0",
    description="Etape 3 : Contrats Pydantic v2 (Field, ConfigDict), CRUD complet et erreurs RFC 7807.",
)

DomaineISGP = Literal["Architecture SI", "Cybersecurite", "Management Public", "Data & IA"]


class FormationEntree(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    code: str = Field(..., pattern=r"^ISGP-[A-Z]{3}-\d{3}$", description="Code normalise ISGP-XXX-000")
    intitule: str = Field(..., min_length=5, max_length=120)
    domaine: DomaineISGP
    duree_jours: int = Field(..., ge=1, le=30)
    tarif_dzd: int = Field(..., ge=10000, le=900000)


class FormationPatch(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    code: str | None = Field(default=None, pattern=r"^ISGP-[A-Z]{3}-\d{3}$")
    intitule: str | None = Field(default=None, min_length=5, max_length=120)
    domaine: DomaineISGP | None = None
    duree_jours: int | None = Field(default=None, ge=1, le=30)
    tarif_dzd: int | None = Field(default=None, ge=10000, le=900000)


class FormationSortie(FormationEntree):
    id: int


CATALOGUE_FORMATIONS: list[dict] = [
    {"id": 1, "code": "ISGP-API-201", "intitule": "Architecture REST & FastAPI", "domaine": "Architecture SI", "duree_jours": 5, "tarif_dzd": 95000},
    {"id": 2, "code": "ISGP-SEC-305", "intitule": "Securite des APIs, OAuth2 & Zero-Trust", "domaine": "Cybersecurite", "duree_jours": 4, "tarif_dzd": 88000},
    {"id": 3, "code": "ISGP-GOV-110", "intitule": "Pilotage de la Transformation Numerique Publique", "domaine": "Management Public", "duree_jours": 3, "tarif_dzd": 72000},
]
PROCHAIN_ID = 4


@app.exception_handler(RequestValidationError)
async def gestionnaire_validation_rfc7807(request: Request, exc: RequestValidationError) -> JSONResponse:
    erreurs = [
        {"champ": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"], "type_erreur": err["type"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        media_type="application/problem+json",
        content={
            "type": "https://isgp.dz/erreurs/validation-contrat",
            "title": "Violation du contrat de donnees Pydantic v2",
            "status": 422,
            "detail": f"{len(erreurs)} champ(s) ne respectent pas le schema attendu.",
            "instance": str(request.url.path),
            "errors": erreurs,
        },
    )


@app.exception_handler(HTTPException)
async def gestionnaire_http_rfc7807(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        media_type="application/problem+json",
        content={
            "type": f"https://isgp.dz/erreurs/http-{exc.status_code}",
            "title": "Erreur metier ou ressource introuvable",
            "status": exc.status_code,
            "detail": str(exc.detail),
            "instance": str(request.url.path),
        },
    )


def _trouver_index(formation_id: int) -> int:
    for idx, f in enumerate(CATALOGUE_FORMATIONS):
        if f["id"] == formation_id:
            return idx
    raise HTTPException(status_code=404, detail=f"Formation #{formation_id} introuvable.")


@app.get("/", response_class=HTMLResponse, summary="Portail Web CRUD interactif avec banniere RFC 7807")
async def page_crud(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="etape_03_crud.html",
        context={"titre_page": "Portail Formations ISGP - Etape 03 : CRUD & RFC 7807"},
    )


@app.get("/api/bonjour", summary="Salutation JSON du service")
async def api_bonjour() -> dict[str, str | int]:
    return {"institut": "ISGP", "etape": 3, "statut": "operationnel"}


@app.get("/api/v1/formations", summary="Lister, filtrer, trier et paginer les formations")
async def lister_formations(
    domaine: str | None = Query(default=None),
    recherche: str | None = Query(default=None),
    tri: Literal["id", "tarif_dzd", "duree_jours"] = Query(default="id"),
    page: int = Query(default=1, ge=1),
    taille: int = Query(default=10, ge=1, le=50),
) -> dict:
    resultats = list(CATALOGUE_FORMATIONS)
    if domaine:
        resultats = [f for f in resultats if f["domaine"].lower() == domaine.lower()]
    if recherche:
        terme = recherche.lower()
        resultats = [f for f in resultats if terme in f["intitule"].lower() or terme in f["code"].lower()]
    resultats.sort(key=lambda item: item[tri])
    total = len(resultats)
    debut = (page - 1) * taille
    return {
        "meta": {"page": page, "taille": taille, "total_elements": total, "total_pages": max(1, math.ceil(total / taille))},
        "data": resultats[debut : debut + taille],
    }


@app.get("/api/v1/formations/{formation_id}", response_model=FormationSortie)
async def obtenir_formation(formation_id: int = Path(..., ge=1)) -> dict:
    return CATALOGUE_FORMATIONS[_trouver_index(formation_id)]


@app.post("/api/v1/formations", response_model=FormationSortie, status_code=status.HTTP_201_CREATED)
async def creer_formation(payload: FormationEntree) -> dict:
    global PROCHAIN_ID
    nouvelle = {"id": PROCHAIN_ID, **payload.model_dump()}
    PROCHAIN_ID += 1
    CATALOGUE_FORMATIONS.append(nouvelle)
    return nouvelle


@app.put("/api/v1/formations/{formation_id}", response_model=FormationSortie)
async def remplacer_formation(payload: FormationEntree, formation_id: int = Path(..., ge=1)) -> dict:
    idx = _trouver_index(formation_id)
    CATALOGUE_FORMATIONS[idx] = {"id": formation_id, **payload.model_dump()}
    return CATALOGUE_FORMATIONS[idx]


@app.patch("/api/v1/formations/{formation_id}", response_model=FormationSortie)
async def modifier_partiellement_formation(payload: FormationPatch, formation_id: int = Path(..., ge=1)) -> dict:
    idx = _trouver_index(formation_id)
    modifications = payload.model_dump(exclude_unset=True)
    CATALOGUE_FORMATIONS[idx].update(modifications)
    return CATALOGUE_FORMATIONS[idx]


@app.delete("/api/v1/formations/{formation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def supprimer_formation(formation_id: int = Path(..., ge=1)) -> Response:
    idx = _trouver_index(formation_id)
    CATALOGUE_FORMATIONS.pop(idx)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _auto_test() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/")).status_code == 200
        rep_422 = await client.post("/api/v1/formations", json={"code": "invalide", "duree_jours": 99})
        assert rep_422.status_code == 422 and "application/problem+json" in rep_422.headers["content-type"]
        rep_post = await client.post(
            "/api/v1/formations",
            json={"code": "ISGP-PYT-301", "intitule": "Pydantic v2 Avance", "domaine": "Architecture SI", "duree_jours": 4, "tarif_dzd": 89000},
        )
        assert rep_post.status_code == 201
        fid = rep_post.json()["id"]
        rep_put = await client.put(
            f"/api/v1/formations/{fid}",
            json={"code": "ISGP-PYT-302", "intitule": "Pydantic v2 & RFC 7807", "domaine": "Architecture SI", "duree_jours": 5, "tarif_dzd": 92000},
        )
        assert rep_put.status_code == 200 and rep_put.json()["code"] == "ISGP-PYT-302"
        rep_patch = await client.patch(f"/api/v1/formations/{fid}", json={"tarif_dzd": 96000})
        assert rep_patch.status_code == 200 and rep_patch.json()["tarif_dzd"] == 96000 and rep_patch.json()["duree_jours"] == 5
        rep_del = await client.delete(f"/api/v1/formations/{fid}")
        assert rep_del.status_code == 204
        print("[OK] Etape 03 validee : POST, PUT, PATCH (exclude_unset=True), DELETE et 422 RFC 7807.")


if __name__ == "__main__":
    if "--once" in sys.argv:
        asyncio.run(_auto_test())
    else:
        uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8001)))
