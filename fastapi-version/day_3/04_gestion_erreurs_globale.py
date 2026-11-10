# Fichier : day_3/04_gestion_erreurs_globale.py
# Exécution : .venv/bin/python day_3/04_gestion_erreurs_globale.py
# Objectif : Intercepter globalement les erreurs 404, 405 et 500 avec @app.exception_handler
#            dans FastAPI/Starlette pour toujours renvoyer un JSON structuré.

import sys
import uvicorn
from fastapi import FastAPI, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="ISGP - Gestionnaires d'Exceptions Globaux (@app.exception_handler)", version="1.0.0")


# 1. INTERCEPTEUR HTTP (404 Not Found, 405 Method Not Allowed, etc.)
@app.exception_handler(StarletteHTTPException)
async def erreur_http_json(request: Request, exc: StarletteHTTPException):
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return JSONResponse(
            status_code=404,
            content={
                "erreur": "Ressource ou route introuvable (404 Not Found)",
                "chemin_demande": request.url.path,
                "methode": request.method,
            },
        )
    if exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        return JSONResponse(
            status_code=405,
            content={
                "erreur": f"La méthode {request.method} n'est pas autorisée sur la route {request.url.path} (405 Method Not Allowed)",
            },
        )
    return JSONResponse(status_code=exc.status_code, content={"erreur": str(exc.detail), "code": exc.status_code})


# 2. INTERCEPTEUR GLOBAL D'EXCEPTIONS : Garantit du JSON même en cas de crash imprévu (500)
@app.exception_handler(Exception)
async def erreur_interne_json(request: Request, exc: Exception):
    print(f"[ERREUR CRITIQUE SERVEUR ASGI] {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "erreur": "Erreur interne du serveur (500 Internal Server Error)",
            "conseil": "Veuillez communiquer l'horodatage à l'administrateur.",
        },
    )


@app.get("/api/v1/division")
async def calculer_division(a: float = Query(default=100.0), b: float = Query(default=0.0)):
    # Si b=0 -> ZeroDivisionError intercepté proprement en JSON par @app.exception_handler(Exception) !
    return {"resultat": a / b}


if __name__ == "__main__":
    if "--serve" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8001)
    else:
        # raise_server_exceptions=False permet à TestClient de retourner la réponse 500 JSON générée par l'exception_handler
        client = TestClient(app, raise_server_exceptions=False)
        print("1. Test 404 JSON :", client.get("/route-inconnue").status_code, client.get("/route-inconnue").json())
        print("2. Test 405 JSON :", client.delete("/api/v1/division").status_code, client.delete("/api/v1/division").json())
        print("3. Test 500 JSON :", client.get("/api/v1/division?a=100&b=0").status_code, client.get("/api/v1/division?a=100&b=0").json())
