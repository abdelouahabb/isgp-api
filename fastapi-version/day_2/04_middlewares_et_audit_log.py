import os
# Fichier : day_2/04_middlewares_et_audit_log.py
# Exécution : .venv/bin/python day_2/04_middlewares_et_audit_log.py
# Objectif : Implémenter un Middleware ASGI (@app.middleware("http")) dans FastAPI
#            pour chronométrer chaque requête, injecter X-Request-ID et journaliser l'audit.

import sys
import time
import uuid
import uvicorn
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI(title="ISGP - Middleware ASGI & Audit Log", version="1.0.0")


# MIDDLEWARE ASGI : Enveloppe le cycle complet (AVANT et APRÈS `await call_next(request)`)
@app.middleware("http")
async def middleware_audit_et_tracabilite(request: Request, call_next):
    # 1. PHASE AVANT REQUÊTE (équivalent @app.before_request + stockage dans request.state)
    heure_debut = time.perf_counter()
    request_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:8]}"
    request.state.request_id = request_id

    # 2. EXÉCUTION ASYNCHRONE DE LA ROUTE CIBLÉE
    reponse = await call_next(request)

    # 3. PHASE APRÈS REQUÊTE (équivalent @app.after_request)
    duree_ms = round((time.perf_counter() - heure_debut) * 1000, 2)
    reponse.headers["X-Request-ID"] = request_id
    reponse.headers["X-Response-Time-Ms"] = str(duree_ms)
    reponse.headers["X-Content-Type-Options"] = "nosniff"

    print(f"[AUDIT ASGI] {request.method} {request.url.path} -> HTTP {reponse.status_code} ({duree_ms} ms) [ID: {request_id}]")
    return reponse


@app.get("/api/v1/statut")
async def verifier_statut(request: Request):
    return {
        "service": "ISGP FastAPI Core (ASGI)",
        "request_id": request.state.request_id,
        "statut": "opérationnel",
    }


if __name__ == "__main__":
    client = TestClient(app)
    rep = client.get("/api/v1/statut", headers={"X-Request-ID": "req-isgp-2026"})
    print("En-têtes injectés par le middleware ASGI :", dict(rep.headers))
    print("Corps JSON :", rep.json())
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
