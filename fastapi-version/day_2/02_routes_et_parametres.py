# Fichier : day_2/02_routes_et_parametres.py
# Exécution : .venv/bin/python day_2/02_routes_et_parametres.py
# Objectif : Maîtriser les paramètres de chemin FastAPI ({prenom}, {stagiaire_id}: int), la différence
#            avec <int:id> (Flask) et :id (Postman/Express), les paramètres de requête typés (Query)
#            et le rendu Jinja2Templates dynamique.

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="ISGP - Routage & Paramètres FastAPI", version="1.0.0")
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))

STAGIAIRES = {
    1: {"id": 1, "prenom": "Yasmine", "nom": "Merabet", "specialite": "Architecture API & Sécurité"},
    2: {"id": 2, "prenom": "Amine", "nom": "Benali", "specialite": "Python, FastAPI & Bases SQL"},
}


# 1. PARAMÈTRE DE CHEMIN TEXTE ({prenom}: str) : Syntaxe standard OpenAPI 3.1 / FastAPI
#    Comparaison :
#    - FastAPI / OpenAPI 3.1 utilisent : {prenom} ou {stagiaire_id} avec annotation Python `: int`
#    - Flask / Werkzeug utilisent      : <prenom> ou <int:stagiaire_id>
#    - Postman / Express.js utilisent  : :prenom ou :stagiaire_id
@app.get("/api/saluer/{prenom}")
async def saluer_stagiaire(prenom: str = Path(..., min_length=2, description="Prénom du stagiaire")):
    return {
        "message": f"Bienvenue au séminaire API, {prenom}",
        "longueur_chaine": len(prenom),
        "syntaxe_route_fastapi": "/api/saluer/{prenom}",
        "equivalent_flask_werkzeug": "/api/saluer/<prenom>",
        "equivalent_postman_express": "/api/saluer/:prenom",
    }


# 2. TYPAGE STRICT ({stagiaire_id}: int) : Valide et convertit l'entier (ou renvoie 422 si non-entier)
@app.get("/api/v1/stagiaires/{stagiaire_id}")
async def obtenir_stagiaire_json(stagiaire_id: int = Path(..., ge=1)):
    stagiaire = STAGIAIRES.get(stagiaire_id)
    if not stagiaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stagiaire #{stagiaire_id} introuvable",
        )
    return {"data": stagiaire}


# 3. ROUTE WEB DYNAMIQUE JINJA2 : Injecte le stagiaire dans day_2/templates/fiche_stagiaire.html
@app.get("/stagiaires/{stagiaire_id}/fiche", response_class=HTMLResponse)
async def afficher_fiche_stagiaire_html(request: Request, stagiaire_id: int = Path(..., ge=1)):
    stagiaire = STAGIAIRES.get(stagiaire_id)
    if not stagiaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stagiaire #{stagiaire_id} introuvable",
        )
    return templates.TemplateResponse(
        request=request,
        name="fiche_stagiaire.html",
        context={"stagiaire": stagiaire},
    )


# 4. PARAMÈTRES DE REQUÊTE APRÈS '?' (Query Parameters typés via Query(...) dans la signature)
@app.get("/api/calcul-tva")
async def calculer_tva(
    ht: float = Query(default=1000.0, gt=0, description="Montant Hors Taxes"),
    taux: float = Query(default=19.0, ge=0, le=100, description="Taux de TVA en %"),
):
    montant_tva = ht * (taux / 100.0)
    return {
        "prix_ht": ht,
        "taux_tva": taux,
        "montant_tva": round(montant_tva, 2),
        "prix_ttc": round(ht + montant_tva, 2),
    }


if __name__ == "__main__":
    client = TestClient(app)
    print("=== 1. TEST PARAMÈTRE DE CHEMIN ({prenom}: str) ===")
    print(client.get("/api/saluer/Yasmine").json())

    print("\n=== 2. TEST TYPAGE {stagiaire_id}: int + RENDU JINJA2 ===")
    print(client.get("/stagiaires/1/fiche").text.strip())

    print("\n=== 3. TEST QUERY PARAMETERS (?ht=2500&taux=19 via Query) ===")
    print(client.get("/api/calcul-tva?ht=2500&taux=19").json())
    if "--once" not in sys.argv:
        import uvicorn
        port = int(os.environ.get("PORT", 8001))
        print("\n" + "=" * 76)
        print(f"[BOUCLE ASGI UVICORN / FASTAPI ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Interface Swagger UI interactive : http://127.0.0.1:{port}/docs")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur ASGI.")
        print("=" * 76)
        uvicorn.run(app, host="0.0.0.0", port=port)
