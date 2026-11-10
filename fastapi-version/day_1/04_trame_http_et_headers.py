import sys
import os
# Fichier : day_1/04_trame_http_et_headers.py
# Exécution : .venv/bin/python day_1/04_trame_http_et_headers.py
# Objectif : Comparer la trame brute HTTP/1.1 d'un appel API JSON (modèle Pydantic BaseModel dans FastAPI)
#            et la trame brute HTTP/1.1 d'un Formulaire Web HTML (Form(...) dans FastAPI).

import json
from urllib.parse import urlencode
from fastapi import FastAPI, Form, Header, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel


def construire_trame_http(methode, chemin, hote, content_type, corps_texte, headers_extra=None):
    """Construit la trame texte exacte envoyée sur le socket TCP selon la RFC 9112."""
    lignes = [
        f"{methode} {chemin} HTTP/1.1",
        f"Host: {hote}",
        "User-Agent: ISGP-PedagogicInspector/1.0",
    ]
    if headers_extra:
        for k, v in headers_extra.items():
            lignes.append(f"{k}: {v}")
    if corps_texte:
        lignes.append(f"Content-Type: {content_type}")
        lignes.append(f"Content-Length: {len(corps_texte.encode('utf-8'))}")
    # En HTTP/1.1, une ligne vide (\r\n\r\n) sépare TOUJOURS les Headers du Body !
    return "\r\n".join(lignes) + "\r\n\r\n" + corps_texte


# 1. Trame envoyée par un Client API Moderne (JSON -> validé par BaseModel Pydantic dans FastAPI)
donnees_formation = {"titre": "Ingénierie des APIs REST", "duree_jours": 5, "salle": "Salle A"}
trame_api_json = construire_trame_http(
    methode="POST",
    chemin="/api/v1/formations",
    hote="127.0.0.1:8000",
    content_type="application/json; charset=utf-8",
    corps_texte=json.dumps(donnees_formation, ensure_ascii=False),
    headers_extra={"Accept": "application/json", "Authorization": "Bearer eyJhbGci..."},
)

# 2. Trame envoyée par un Formulaire HTML <form method="POST"> (lu par Form(...) dans FastAPI)
trame_formulaire_html = construire_trame_http(
    methode="POST",
    chemin="/sandbox/formulaire-jinja",
    hote="127.0.0.1:8000",
    content_type="application/x-www-form-urlencoded",
    corps_texte=urlencode(donnees_formation),
    headers_extra={"Accept": "text/html"},
)

print("=== 1. TRAME HTTP/1.1 D'UN APPEL API JSON (validé via BaseModel Pydantic dans FastAPI) ===")
print(trame_api_json)
print("\n=== 2. TRAME HTTP/1.1 D'UN FORMULAIRE HTML <form method='POST'> (lu via Form(...) dans FastAPI) ===")
print(trame_formulaire_html)


# 3. Vérification en direct avec FastAPI + TestClient
app = FastAPI(title="ISGP - Inspection des En-têtes & Corps HTTP", version="1.0.0")


class FormationPayload(BaseModel):
    titre: str
    duree_jours: int
    salle: str


@app.post("/api/v1/formations")
async def recevoir_json(
    payload: FormationPayload,
    request: Request,
    user_agent: str = Header(default="Inconnu"),
):
    return {
        "mode": "application/json (Pydantic BaseModel)",
        "user_agent_recu": user_agent,
        "content_type": request.headers.get("content-type"),
        "donnees_validees": payload.model_dump(),
    }


@app.post("/sandbox/formulaire-jinja")
async def recevoir_formulaire(
    request: Request,
    titre: str = Form(...),
    duree_jours: int = Form(...),
    salle: str = Form(...),
):
    return {
        "mode": "application/x-www-form-urlencoded (FastAPI Form)",
        "content_type": request.headers.get("content-type"),
        "donnees_validees": {"titre": titre, "duree_jours": duree_jours, "salle": salle},
    }


if __name__ == "__main__":
    client = TestClient(app)
    print("\n=== 3. RÉCEPTION PAR FASTAPI (JSON vs FORM) ===")
    r_json = client.post("/api/v1/formations", json=donnees_formation)
    print("Réponse JSON :", r_json.json())
    r_form = client.post("/sandbox/formulaire-jinja", data=donnees_formation)
    print("Réponse Form :", r_form.json())
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
