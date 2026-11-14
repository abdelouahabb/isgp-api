# Fichier : zero_to_hero/etape_01_hello_world.py
# Etape 1/6 : Serveur minimal FastAPI combinant Site Web HTML (Jinja2) et API JSON
import asyncio
import os
import sys
import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))

app = FastAPI(
    title="Portail Web & API Catalogue Formations ISGP - Etape 01",
    version="0.1.0",
    description="Etape 1 : Premier serveur ASGI combinant page HTML et API REST JSON.",
)


@app.get("/", response_class=HTMLResponse, summary="Page d'accueil HTML du portail ISGP")
async def page_accueil(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="etape_01_hello.html",
        context={"titre_page": "Portail Formations ISGP - Etape 01 : Hello World"},
    )


@app.get("/api/bonjour", summary="Salutation JSON typee du service API")
async def api_bonjour() -> dict[str, str | int]:
    return {
        "institut": "ISGP",
        "etape": 1,
        "statut": "operationnel",
        "message": "Bienvenue sur l'API REST FastAPI du catalogue des formations ISGP.",
    }


async def _auto_test() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        rep_html = await client.get("/")
        assert rep_html.status_code == 200 and "text/html" in rep_html.headers["content-type"]
        rep_json = await client.get("/api/bonjour")
        assert rep_json.status_code == 200 and rep_json.json()["institut"] == "ISGP"
        rep_docs = await client.get("/docs")
        assert rep_docs.status_code == 200
        print("[OK] Etape 01 validee : GET / (HTML), GET /api/bonjour (JSON) et GET /docs.")


if __name__ == "__main__":
    if "--once" in sys.argv:
        asyncio.run(_auto_test())
    else:
        uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8001)))
