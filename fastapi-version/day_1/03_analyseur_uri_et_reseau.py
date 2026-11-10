import sys
import os
# Fichier : day_1/03_analyseur_uri_et_reseau.py
# Exécution : .venv/bin/python day_1/03_analyseur_uri_et_reseau.py
# Objectif : Décoder une URI complète (RFC 3986), ses paramètres de requête et les méthodes/codes HTTP dans FastAPI

from urllib.parse import urlparse, parse_qs
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.testclient import TestClient
from pydantic import BaseModel

uri_complete = "https://api.isgp.dz:8443/api/v1/formations?ville=Alger&domaine=securite&page=2#resultats"

analyse = urlparse(uri_complete)
parametres = parse_qs(analyse.query)

print("=== 1. DÉCOUPAGE NORMALISÉ D'UNE URI (RFC 3986) ===")
print("Protocole (Scheme) :", analyse.scheme)      # https
print("Hôte (Hostname)    :", analyse.hostname)    # api.isgp.dz
print("Port TCP           :", analyse.port)        # 8443
print("Chemin (Path)      :", analyse.path)        # /api/v1/formations
print("Requête (Query)    :", analyse.query)       # ville=Alger&domaine=securite&page=2
print("Fragment (Anchor)  :", analyse.fragment)    # resultats

print("\n=== 2. DICTIONNAIRE DES PARAMÈTRES DE REQUÊTE ===")
for cle, valeurs in parametres.items():
    print(f"- {cle} : {valeurs[0]}")


# 3. Démonstration FastAPI : verbes HTTP et codes de statut normalisés (status.HTTP_*)
app = FastAPI(title="ISGP - URI, Méthodes & Codes HTTP", version="1.0.0")
CATALOGUE_DEMO = {1: {"id": 1, "titre": "Architecture FastAPI & ASGI", "ville": "Alger"}}


class FormationIn(BaseModel):
    titre: str
    ville: str = "Alger"


@app.get("/api/v1/formations", status_code=status.HTTP_200_OK)
async def lister_formations(ville: str = "Alger", page: int = 1):
    items = [f for f in CATALOGUE_DEMO.values() if f["ville"].lower() == ville.lower()]
    return {"page": page, "ville": ville, "items": items}


@app.post("/api/v1/formations", status_code=status.HTTP_201_CREATED)
async def creer_formation(payload: FormationIn, response: Response):
    nouvel_id = max(CATALOGUE_DEMO.keys(), default=0) + 1
    CATALOGUE_DEMO[nouvel_id] = {"id": nouvel_id, "titre": payload.titre, "ville": payload.ville}
    response.headers["Location"] = f"/api/v1/formations/{nouvel_id}"
    return CATALOGUE_DEMO[nouvel_id]


@app.delete("/api/v1/formations/{formation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def supprimer_formation(formation_id: int):
    if formation_id not in CATALOGUE_DEMO:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formation introuvable")
    del CATALOGUE_DEMO[formation_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    client = TestClient(app)
    print("\n=== 3. SIMULATION FASTAPI (GET 200, POST 201, DELETE 204) ===")
    r_get = client.get("/api/v1/formations?ville=Alger&page=1")
    print(f"GET /api/v1/formations -> {r_get.status_code} | {r_get.json()}")
    r_post = client.post("/api/v1/formations", json={"titre": "Sécurité OAuth2", "ville": "Alger"})
    print(f"POST /api/v1/formations -> {r_post.status_code} | Location: {r_post.headers.get('location')}")
    r_del = client.delete("/api/v1/formations/2")
    print(f"DELETE /api/v1/formations/2 -> {r_del.status_code} (No Content)")
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
