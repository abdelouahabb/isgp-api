import sys
import os
"""
Jour 5 — Script 05 : Génération Automatique OpenAPI 3.1 (/openapi.json), Swagger UI (/docs) & ReDoc (/redoc)
=============================================================================================================
Objectif :
1. Comprendre comment FastAPI génère automatiquement le contrat OpenAPI 3.1.0 à partir des modèles Pydantic v2,
   des annotations de type (`{id}: int`, `Query(...)`) et des dépendances de sécurité (`APIKeyHeader`, `HTTPBearer`).
2. Personnaliser les métadonnées OpenAPI (`title`, `version`, `openapi_tags`, `servers`, `custom_openapi`) dans FastAPI.
3. Exposer nativement `/docs` (Swagger UI), `/redoc` (ReDoc) et `/openapi.json` (ainsi que `/api/openapi.json` et `/api/docs`).
"""

import json
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Path, Query, Security, status
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
from fastapi.security import APIKeyHeader, HTTPBearer
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

# =====================================================================
# 1. SCHÉMAS PYDANTIC V2 & SÉCURITÉ DÉCLARATIVE (GÉNÈRENT LE CONTRAT OPENAPI)
# =====================================================================
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False, description="Clé d'API partenaire (ex: isgp-secret-2026)")
bearer_scheme = HTTPBearer(auto_error=False, description="Entrez votre jeton signé (sans le mot 'Bearer').")


class Formation(BaseModel):
    id: int = Field(..., examples=[1])
    code: str = Field(..., examples=["API-101"])
    titre: str = Field(..., examples=["Fondamentaux REST & FastAPI"])
    duree_jours: int = Field(..., ge=1, le=30, examples=[5])
    tarif_dzd: int = Field(..., ge=0, examples=[75000])


class FormationInput(BaseModel):
    code: str = Field(..., examples=["API-303"])
    titre: str = Field(..., min_length=3, examples=["Architecture Microservices ASGI"])
    duree_jours: int = Field(..., ge=1, le=30, examples=[4])
    tarif_dzd: int = Field(..., ge=0, examples=[60000])


class ErreurRFC7807(BaseModel):
    type: str = Field(default="https://api.isgp.dz/errors/validation")
    title: str = Field(default="Erreur de validation métier")
    status: int = Field(default=422)
    detail: str = Field(default="Le champ duree_jours doit être >= 1.")


TAGS_METADATA = [
    {"name": "Formations", "description": "Opérations CRUD sur le catalogue des formations ISGP"},
    {"name": "Sécurité", "description": "Routes protégées par Bearer Token ou X-API-Key"},
]

app = FastAPI(
    title="API Catalogue Formations ISGP",
    version="1.0.0",
    description=(
        "Contrat officiel OpenAPI généré automatiquement par FastAPI & Pydantic v2. "
        "Permet de tester les routes via Swagger UI (`/docs`) et ReDoc (`/redoc`), "
        "et de s'authentifier via le bouton cadenas 'Authorize'."
    ),
    contact={"name": "Direction des Systèmes d'Information ISGP"},
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

FORMATIONS = [
    {"id": 1, "code": "API-101", "titre": "Fondamentaux REST & HTTP", "duree_jours": 3, "tarif_dzd": 45000},
    {"id": 2, "code": "API-202", "titre": "Sécurité JWT, OAuth2 & OpenAPI", "duree_jours": 5, "tarif_dzd": 75000},
]


# =====================================================================
# 2. ROUTES MÉTIER TYPÉES (AUTO-DOCUMENTÉES DANS /openapi.json ET /docs)
# =====================================================================
@app.get(
    "/api/v1/formations",
    response_model=list[Formation],
    tags=["Formations"],
    summary="Lister toutes les formations du catalogue",
)
async def lister_formations(
    min_jours: int = Query(default=1, ge=1, le=30, description="Filtrer par durée minimale en jours"),
):
    return [f for f in FORMATIONS if f["duree_jours"] >= min_jours]


@app.post(
    "/api/v1/formations",
    response_model=Formation,
    status_code=status.HTTP_201_CREATED,
    tags=["Formations", "Sécurité"],
    summary="Créer une nouvelle formation (Protégé par X-API-Key)",
    responses={401: {"description": "Clé X-API-Key manquante ou invalide"}, 422: {"model": ErreurRFC7807}},
)
async def creer_formation(
    payload: FormationInput,
    x_api_key: Optional[str] = Security(api_key_header),
    _bearer: Optional[object] = Security(bearer_scheme),
):
    if x_api_key != "isgp-secret-2026":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clé X-API-Key manquante ou invalide")
    nouvel_id = max((f["id"] for f in FORMATIONS), default=0) + 1
    nouvelle = {"id": nouvel_id, **payload.model_dump()}
    FORMATIONS.append(nouvelle)
    return nouvelle


@app.get(
    "/api/v1/formations/{id}",
    response_model=Formation,
    tags=["Formations"],
    summary="Consulter une formation par son identifiant unique",
    responses={404: {"description": "Formation introuvable"}},
)
async def obtenir_formation(id: int = Path(..., ge=1, description="Identifiant unique de la formation (ex: 1)")):
    for f in FORMATIONS:
        if f["id"] == id:
            return f
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Formation #{id} introuvable")


# =====================================================================
# 3. PERSONNALISATION DU SCHÉMA OPENAPI (SERVEURS & SECURITY SCHEMES)
# =====================================================================
def construire_contrat_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=TAGS_METADATA,
        servers=[
            {"url": "http://127.0.0.1:8000", "description": "Serveur de développement Uvicorn ASGI"},
            {"url": "https://api.isgp.dz", "description": "Serveur de production"},
        ],
    )
    schema.setdefault("components", {}).setdefault("securitySchemes", {}).update({
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Entrez votre jeton signé (sans le mot 'Bearer').",
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Clé d'API partenaire (ex: isgp-secret-2026).",
        },
    })
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = construire_contrat_openapi


@app.get("/api/openapi.json", include_in_schema=False)
async def openapi_json_alias():
    return app.openapi()


@app.get("/api/docs", include_in_schema=False)
async def swagger_ui_alias():
    return RedirectResponse(url="/docs")


# =====================================================================
# 4. DÉMONSTRATION AUTOMATISÉE DU CONTRAT OPENAPI NATIF FASTAPI
# =====================================================================
if __name__ == "__main__":
    client = TestClient(app)
    resp_spec = client.get("/openapi.json")
    spec = resp_spec.json()
    print("=== CONTRAT OPENAPI GÉNÉRÉ AUTOMATIQUEMENT PAR FASTAPI ===")
    print(f"Titre de l'API      : {spec['info']['title']} (v{spec['info']['version']})")
    print(f"Version OpenAPI     : {spec['openapi']}")
    print(f"Portails natifs     : Swagger UI (/docs) | ReDoc (/redoc) | Schéma (/openapi.json)")
    print(f"Schémas de sécurité : {list(spec['components']['securitySchemes'].keys())}")
    print(f"Modèles Pydantic    : {list(spec['components']['schemas'].keys())}")
    print("Routes documentées  :")
    for chemin, methodes in spec["paths"].items():
        for verbe, details in methodes.items():
            print(f"  - {verbe.upper():6s} {chemin:26s} -> {details['summary']}")
    print("\nExtrait JSON de /components/securitySchemes :")
    print(json.dumps(spec["components"]["securitySchemes"], indent=2, ensure_ascii=False))
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
