# Fichier : day_5/03_architecture_blueprints.py
# Exécution : .venv/bin/python day_5/03_architecture_blueprints.py
# Objectif : Structurer une API FastAPI modulaire avec APIRouter et comprendre le Versioning (/api/v1 vs /api/v2) :
#   1. APIRouter Web Jinja2Templates (/portail -> day_5/templates/portail_blueprint.html)
#   2. APIRouter API v1 (/api/v1/formations) : Schéma plat historique + En-têtes de Dépréciation (RFC 8594)
#   3. APIRouter API v2 (/api/v2/formations) : Nouveau schéma avec Rupture de Contrat (Breaking Change)
#   4. APIRouter Supervision (/api/health/live & /api/health/ready) + Application Factory (create_app)

import os
import sys
import time
import uvicorn
from fastapi import APIRouter, FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DEMARRAGE_SERVEUR = time.time()
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))

# SOURCE DE DONNÉES MÉTIER PARTAGÉE ENTRE v1, v2 ET LE PORTAIL WEB
CATALOGUE_METIER = [
    {"id": 1, "code": "ISGP-API-101", "titre": "Architecture API REST & FastAPI", "jours": 5, "tarif_dzd": 65000},
    {"id": 2, "code": "ISGP-WEB-202", "titre": "Jinja2Templates & Formulaires", "jours": 3, "tarif_dzd": 45000},
    {"id": 3, "code": "ISGP-SEC-303", "titre": "Sécurité JWT, OAuth2 & WAF", "jours": 4, "tarif_dzd": 60000},
]

# 1. ROUTEUR WEB (Jinja2Templates) : Sert les pages HTML depuis day_5/templates/
web_router = APIRouter(prefix="/portail", tags=["Portail Web HTML"])


@web_router.get("", response_class=HTMLResponse)
async def afficher_portail(request: Request):
    titres = [f["titre"] for f in CATALOGUE_METIER]
    return templates.TemplateResponse(
        request=request,
        name="portail_blueprint.html",
        context={
            "titre": "Portail des Formations ISGP (APIRouter Web Jinja2Templates)",
            "items": titres,
        },
    )


# 2. ROUTEUR API v1 (/api/v1/formations) : Contrat historique maintenu pour les anciens clients
#    Pourquoi v1 est en phase de dépréciation ? Parce que "duree" y était un simple entier (5),
#    et la racine renvoyait une liste plate sans enveloppe de pagination.
formations_v1_router = APIRouter(prefix="/api/v1/formations", tags=["Formations v1 (Dépréciée)"])


@formations_v1_router.get("", deprecated=True)
async def lister_formations_v1(response: Response):
    # Norme IETF RFC 8594 : Avertit les clients que v1 reste active mais sera éteinte à une date précise
    response.headers["X-API-Version"] = "1.0"
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "Thu, 31 Dec 2026 23:59:59 GMT"
    response.headers["Link"] = '</api/v2/formations>; rel="successor-version"'

    format_v1 = [
        {"id": f["id"], "intitule": f["titre"], "duree": f["jours"], "prix": f["tarif_dzd"]}
        for f in CATALOGUE_METIER
    ]
    return {"version": "v1", "items": format_v1}


# 3. ROUTEUR API v2 (/api/v2/formations) : Nouveau contrat avec Breaking Changes assumés
#    - "intitule" est renommé en "titre"
#    - "duree" n'est plus un entier (5), mais un objet structuré {"valeur": 5, "unite": "jours", "heures": 35}
#    - Ajout d'une enveloppe normalisée {"meta": ..., "data": ..., "links": ...}
formations_v2_router = APIRouter(prefix="/api/v2/formations", tags=["Formations v2 (Actuelle)"])


@formations_v2_router.get("")
async def lister_formations_v2(response: Response):
    response.headers["X-API-Version"] = "2.0"
    format_v2 = [
        {
            "id": f["id"],
            "code_catalogue": f["code"],
            "titre": f["titre"],
            "duree": {"valeur": f["jours"], "unite": "jours", "heures_pedagogiques": f["jours"] * 7},
            "tarification": {"montant_ht": f["tarif_dzd"], "devise": "DZD"},
            "links": {"self": f"/api/v2/formations/{f['id']}"},
        }
        for f in CATALOGUE_METIER
    ]
    return {
        "meta": {"version": "v2", "total": len(format_v2), "retrocompatible_v1": False},
        "data": format_v2,
    }


# 4. ROUTEUR SUPERVISION : Sondes de santé (/api/health/live & /api/health/ready)
sante_router = APIRouter(prefix="/api/health", tags=["Supervision & Probes"])


@sante_router.get("/live")
async def liveness_probe():
    return {"statut": "UP", "uptime_secondes": round(time.time() - DEMARRAGE_SERVEUR, 1)}


@sante_router.get("/ready")
async def readiness_probe():
    db_connectee = True
    code = status.HTTP_200_OK if db_connectee else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=code, content={"pret": db_connectee, "dependances": {"sqlite": "OK"}})


# 5. APPLICATION FACTORY : Assemblage simultané de v1, v2, Web et Santé via app.include_router()
def create_app() -> FastAPI:
    application = FastAPI(title="ISGP - Architecture Modulaire APIRouter (v1 & v2)", version="2.0.0")
    application.include_router(web_router)
    application.include_router(formations_v1_router)
    application.include_router(formations_v2_router)
    application.include_router(sante_router)
    return application


app = create_app()

if __name__ == "__main__":
    client = TestClient(app)
    print("=== 1. APIROUTER v1 (AVEC EN-TÊTES DE DÉPRÉCIATION RFC 8594) ===")
    r1 = client.get("/api/v1/formations")
    print("Headers v1 :", {k: r1.headers[k] for k in ("x-api-version", "deprecation", "sunset", "link")})
    print("JSON v1    :", r1.json()["items"][0])

    print("\n=== 2. APIROUTER v2 (NOUVEAU SCHÉMA ENRICHI COEXISTANT) ===")
    r2 = client.get("/api/v2/formations")
    print("Headers v2 :", {"x-api-version": r2.headers["x-api-version"]})
    print("JSON v2    :", r2.json()["data"][0])
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
