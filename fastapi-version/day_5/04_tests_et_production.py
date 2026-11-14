# Fichier : day_5/04_tests_et_production.py
# Exécution : .venv/bin/python day_5/04_tests_et_production.py
# Objectif : Tester automatiquement ses routes FastAPI (API JSON Pydantic et Formulaire HTML Jinja2Templates)
#            sans ouvrir de port réseau grâce à TestClient(app), et préparer le déploiement Uvicorn / Gunicorn.

import os
import sys
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="ISGP - Tests Automatisés TestClient & Déploiement ASGI", version="1.0.0")
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))


class CalculTaxePayload(BaseModel):
    montant_ht: float = Field(..., ge=0, description="Montant Hors Taxes (>= 0)")


# 1. ROUTE API JSON (validée automatiquement par Pydantic BaseModel -> 422 si négatif)
@app.post("/api/calcul-taxe")
async def calculer_taxe_api(payload: CalculTaxePayload):
    tva = round(payload.montant_ht * 0.19, 2)
    return {
        "montant_ht": payload.montant_ht,
        "tva_19": tva,
        "montant_ttc": round(payload.montant_ht + tva, 2),
    }


# 2. ROUTES FORMULAIRE HTML + JINJA2TEMPLATES (reçoit application/x-www-form-urlencoded via Form(...))
@app.get("/formulaire-taxe", response_class=HTMLResponse)
async def afficher_formulaire_taxe(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="resultat_taxe.html",
        context={"resultat": None},
    )


@app.post("/formulaire-taxe", response_class=HTMLResponse)
async def calculer_taxe_formulaire(request: Request, montant_ht: float = Form(...)):
    resultat = None
    if montant_ht >= 0:
        tva = round(montant_ht * 0.19, 2)
        resultat = {
            "montant_ht": montant_ht,
            "tva_19": tva,
            "montant_ttc": round(montant_ht + tva, 2),
        }
    return templates.TemplateResponse(
        request=request,
        name="resultat_taxe.html",
        context={"resultat": resultat},
    )


@app.get("/", response_class=HTMLResponse)
async def portail_tests_production(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="portail_04_tests_home.html",
        context={},
    )


# ================= SUITE DE TESTS AUTOMATISÉS (TestClient FastAPI : JSON + FORMULAIRE JINJA2) =================
def executer_tests_automatises():
    client = TestClient(app)
    assert client.get("/").status_code == 200

    # Test 1 : Appel API JSON nominal (json={...} -> Content-Type: application/json)
    rep_ok = client.post("/api/calcul-taxe", json={"montant_ht": 1000})
    assert rep_ok.status_code == 200
    assert rep_ok.json()["montant_ttc"] == 1190.0
    print("[TEST 1 RÉUSSI] POST JSON /api/calcul-taxe (1000 HT -> 1190 TTC) : HTTP 200")

    # Test 2 : Appel API JSON invalide rejeté par Pydantic v2 (422 Unprocessable Entity)
    rep_err = client.post("/api/calcul-taxe", json={"montant_ht": -50})
    assert rep_err.status_code == 422
    print("[TEST 2 RÉUSSI] Rejet d'un montant négatif par Pydantic : HTTP 422 Unprocessable Entity")

    # Test 3 : Soumission d'un Formulaire HTML (data={...} -> Form(...) + rendu Jinja2Templates)
    rep_form = client.post("/formulaire-taxe", data={"montant_ht": "2000"})
    assert rep_form.status_code == 200
    html_rendu = rep_form.text
    assert "2380.0 DZD" in html_rendu
    print("[TEST 3 RÉUSSI] POST Formulaire HTML /formulaire-taxe (Form + Jinja2Templates) : 2380.0 DZD")


if __name__ == "__main__":
    executer_tests_automatises()
    if "--once" not in sys.argv:
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8001)))
