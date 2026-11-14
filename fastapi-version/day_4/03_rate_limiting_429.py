import os
# Fichier : day_4/03_rate_limiting_429.py
# Exécution : .venv/bin/python day_4/03_rate_limiting_429.py
# Objectif : Implémenter un Rate Limiter par fenêtre glissante (429 Too Many Requests + Retry-After) dans FastAPI.

import sys
import time
import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="ISGP - Rate Limiting & 429 Too Many Requests", version="1.0.0")
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))

# Configuration du Rate Limiter : max 3 requêtes par tranche de 20 secondes par IP
LIMITE_REQUETES = 3
FENETRE_SECONDES = 20
historique_ip: dict[str, list[float]] = {}


@app.get("/api/catalogue-protege")
async def catalogue_avec_ratelimit(request: Request, response: Response):
    ip_client = (request.client.host if request.client else None) or "127.0.0.1"
    maintenant = time.time()

    # 1. Conserver uniquement les appels effectués durant les 20 dernières secondes
    appels_recents = [t for t in historique_ip.get(ip_client, []) if maintenant - t < FENETRE_SECONDES]

    # 2. Vérifier si le plafond est atteint
    if len(appels_recents) >= LIMITE_REQUETES:
        attente = int(FENETRE_SECONDES - (maintenant - appels_recents[0])) + 1
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "erreur": "Quota de requêtes dépassé (429 Too Many Requests)",
                "limite": f"{LIMITE_REQUETES} requêtes par {FENETRE_SECONDES} secondes",
                "reessayer_dans_secondes": attente,
            },
            headers={
                "Retry-After": str(attente),
                "X-RateLimit-Limit": str(LIMITE_REQUETES),
                "X-RateLimit-Remaining": "0",
            },
        )

    # 3. Enregistrer l'appel actuel et calculer le quota restant
    appels_recents.append(maintenant)
    historique_ip[ip_client] = appels_recents
    restant = LIMITE_REQUETES - len(appels_recents)

    response.headers["X-RateLimit-Limit"] = str(LIMITE_REQUETES)
    response.headers["X-RateLimit-Remaining"] = str(restant)
    return {"message": "Requête acceptée", "quota_restant": restant}


@app.get("/", response_class=HTMLResponse)
async def portail_ratelimit(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="portail_03_ratelimit.html",
        context={},
    )


if __name__ == "__main__":
    client = TestClient(app)
    assert client.get("/").status_code == 200
    for i in range(1, 5):
        r = client.get("/api/catalogue-protege")
        print(f"Appel #{i} -> HTTP {r.status_code} | Remaining={r.headers.get('x-ratelimit-remaining')} | {r.json()}")
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
