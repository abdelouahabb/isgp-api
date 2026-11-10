# Fichier : day_1/02_anatomie_url.py
# Exécution : .venv/bin/python day_1/02_anatomie_url.py
# Objectif : Décoder une URI complète (RFC 3986) via urllib.parse et l'objet Request de FastAPI

from urllib.parse import urlparse, parse_qs
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI(title="ISGP - Anatomie d'une URI (RFC 3986)", version="1.0.0")


@app.get("/api/v1/formations/{formation_id}")
async def inspecter_anatomie_url(
    formation_id: int,
    request: Request,
    ville: str = "Alger",
    domaine: str = "securite",
    page: int = 1,
):
    return {
        "scheme": request.url.scheme,
        "hostname": request.url.hostname,
        "port": request.url.port or (443 if request.url.scheme == "https" else 80),
        "path": request.url.path,
        "path_params": {"formation_id": formation_id},
        "query_string": request.url.query,
        "query_params_types": {"ville": ville, "domaine": domaine, "page": page},
    }


if __name__ == "__main__":
    uri_complete = "https://api.isgp.dz:8443/api/v1/formations/101?ville=Alger&domaine=securite&page=2#resultats"
    analyse = urlparse(uri_complete)
    parametres = parse_qs(analyse.query)

    print("=== 1. DÉCOUPAGE NORMALISÉ D'UNE URI (RFC 3986) ===")
    print("Protocole (Scheme) :", analyse.scheme)
    print("Hôte (Hostname)    :", analyse.hostname)
    print("Port TCP           :", analyse.port)
    print("Chemin (Path)      :", analyse.path)
    print("Requête (Query)    :", analyse.query)
    print("Fragment (Anchor)  :", analyse.fragment)

    print("\n=== 2. INSPECTION FASTAPI (Request.url & Typage Automatique) ===")
    client = TestClient(app, base_url="https://api.isgp.dz:8443")
    rep = client.get("/api/v1/formations/101?ville=Alger&domaine=securite&page=2")
    print("Statut HTTP :", rep.status_code)
    print("Réponse JSON FastAPI :", rep.json())
