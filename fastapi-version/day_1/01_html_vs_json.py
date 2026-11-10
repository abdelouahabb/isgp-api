# Fichier : day_1/01_html_vs_json.py
# Exécution : .venv/bin/python day_1/01_html_vs_json.py
# Objectif : Comparer les 3 formats du Web dans FastAPI (ASGI) :
#   1. Page Web HTML rendue proprement via Jinja2Templates (day_1/templates/meteo.html)
#   2. Service Web Historique SOAP (XML verbeux via Response(media_type="application/xml"))
#   3. API Web Moderne REST (JSON léger sérialisé nativement par FastAPI / Pydantic)

import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

# FastAPI charge les fichiers HTML via Jinja2Templates depuis le sous-dossier "templates/"
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="ISGP - Comparateur HTML vs SOAP vs REST JSON", version="1.0.0")
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))

# Données métier partagées (indépendantes du format de sortie)
DONNEES_METEO = {
    "ville": "Alger",
    "temperature_celsius": 24,
    "condition": "Ensoleillé",
    "humidite_pourcent": 55,
}


# 1. APPROCHE WEB CLASSIQUE (HTML rendu par Jinja2Templates — Zéro HTML codé en dur dans Python)
@app.get("/meteo/html", response_class=HTMLResponse)
async def meteo_page_html(request: Request):
    # templates.TemplateResponse injecte request et le contexte dans day_1/templates/meteo.html
    return templates.TemplateResponse(
        request=request,
        name="meteo.html",
        context={"meteo": DONNEES_METEO},
    )


# 2. APPROCHE HISTORIQUE SOAP / XML (Verbeuse, stricte, utilisée en banque/télécom)
@app.get("/meteo/soap")
async def meteo_enveloppe_soap():
    flux_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetMeteoResponse xmlns="http://isgp.dz/ws/meteo">
      <Ville>{DONNEES_METEO['ville']}</Ville>
      <TemperatureCelsius>{DONNEES_METEO['temperature_celsius']}</TemperatureCelsius>
      <Condition>{DONNEES_METEO['condition']}</Condition>
      <HumiditePourcent>{DONNEES_METEO['humidite_pourcent']}</HumiditePourcent>
    </GetMeteoResponse>
  </soap:Body>
</soap:Envelope>"""
    return Response(content=flux_xml, status_code=200, media_type="application/xml")


# 3. APPROCHE API MODERNE REST / JSON (Sérialisation automatique par FastAPI)
@app.get("/api/v1/meteo")
async def meteo_api_json():
    # FastAPI convertit automatiquement tout dict ou BaseModel Pydantic en JSONResponse UTF-8 !
    return DONNEES_METEO


if __name__ == "__main__":
    # Comparaison automatique des 3 formats grâce à TestClient(app) de FastAPI/Starlette
    client = TestClient(app)
    rep_html = client.get("/meteo/html")
    rep_soap = client.get("/meteo/soap")
    rep_json = client.get("/api/v1/meteo")

    print(f"1. HTML (Jinja2Templates) : {len(rep_html.content)} octets | Content-Type: {rep_html.headers['content-type']}")
    print(f"2. SOAP (Enveloppe XML)   : {len(rep_soap.content)} octets | Content-Type: {rep_soap.headers['content-type']}")
    print(f"3. REST (Payload JSON)    : {len(rep_json.content)} octets | Content-Type: {rep_json.headers['content-type']}")
    print("\nPayload REST/JSON prêt pour tout client (Web, Mobile, Python) :")
    print(rep_json.json())
