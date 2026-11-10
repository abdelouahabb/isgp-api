# Fichier : day_2/04_middlewares_et_cycle_requete.py
# Exécution : .venv/bin/python day_2/04_middlewares_et_cycle_requete.py
# Objectif : Illustrer le cycle de vie d'une requête ASGI avec @app.middleware("http") et request.state.

import time
import uuid
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI(title="ISGP - Cycle de Requête ASGI & Middleware", version="1.0.0")


@app.middleware("http")
async def cycle_requete_asgi(request: Request, call_next):
    debut = time.perf_counter()
    request.state.request_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:8]}"
    response = await call_next(request)
    duree_ms = round((time.perf_counter() - debut) * 1000, 2)
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Response-Time-Ms"] = str(duree_ms)
    return response


@app.get("/api/v1/ping")
async def ping(request: Request):
    return {"pong": True, "request_id": request.state.request_id}


if __name__ == "__main__":
    client = TestClient(app)
    r = client.get("/api/v1/ping")
    print("Statut :", r.status_code, "| X-Request-ID :", r.headers.get("x-request-id"), "| Body :", r.json())
