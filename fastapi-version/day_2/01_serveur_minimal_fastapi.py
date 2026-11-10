# Fichier : day_2/01_serveur_minimal_fastapi.py
# Exécution : .venv/bin/python day_2/01_serveur_minimal_fastapi.py
# Objectif : Comprendre comment FastAPI (ASGI + Uvicorn) sert à la fois :
#   1. Des pages Web HTML via Jinja2Templates (day_2/templates/accueil.html)
#   2. Des routes d'API RESTful normalisées en JSON (sérialisation native Pydantic -> /api/v1/...)

import os
import sys
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

# Configuration du dossier "templates/" contenant les fichiers HTML Jinja2
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="ISGP - Serveur Minimal FastAPI (ASGI)", version="1.0.0")
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))

MODULES_BOOTCAMP = [
    "Jour 1 : Architecture Web, HTTP/1.1, JSON & curl",
    "Jour 2 : FastAPI (ASGI), Routage RESTful, Jinja2Templates & Formulaires HTML",
    "Jour 3 : Ingénierie CRUD, Validation Pydantic v2 (422) & SQLite ACID",
    "Jour 4 : Sécurité API (AuthN 401, AuthZ 403, JWT, Depends, Rate Limiting 429)",
    "Jour 5 : Client Résilient, APIRouter, TestClient & Swagger OpenAPI 3.1",
]


# 1. ROUTE WEB HTML : Rendu via Jinja2Templates (day_2/templates/accueil.html)
#    Zéro HTML écrit en dur dans le code Python !
@app.get("/accueil", response_class=HTMLResponse)
async def page_accueil_jinja(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="accueil.html",
        context={
            "organisme": "ISGP",
            "intitule": "Développement d'APIs et services web (FastAPI & ASGI)",
            "version_api": "v1.0",
            "modules": MODULES_BOOTCAMP,
        },
    )


# 2. ROUTE API REST : Retourne un dictionnaire Python converti nativement en JSON par FastAPI
@app.get("/api/bonjour")
async def dire_bonjour():
    return {
        "message": "Service FastAPI (ASGI) opérationnel",
        "organisme": "ISGP",
        "statut": "actif",
        "version": "v1.0",
    }


# 3. COLLECTION RESTFUL (Niveau 2 de Richardson : nom au pluriel + versioning /api/v1)
@app.get("/api/v1/modules")
async def lister_modules_api():
    return {
        "total": len(MODULES_BOOTCAMP),
        "data": MODULES_BOOTCAMP,
    }


if __name__ == "__main__":
    # Sinon, exécute une démonstration immédiate des 2 modes (Jinja2 HTML vs API JSON) via TestClient
    client = TestClient(app)
    rep_html = client.get("/accueil")
    print("=== 1. RENDU DU TEMPLATE JINJA2 (GET /accueil -> day_2/templates/accueil.html) ===")
    print(rep_html.text.strip())

    rep_json = client.get("/api/bonjour")
    print("\n=== 2. RÉPONSE API JSON (GET /api/bonjour -> FastAPI JSONResponse) ===")
    print("Statut HTTP :", rep_json.status_code, "| Content-Type :", rep_json.headers["content-type"])
    print("Payload JSON :", rep_json.json())
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
