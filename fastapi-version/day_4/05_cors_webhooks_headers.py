# Fichier : day_4/05_cors_webhooks_headers.py
# Exécution : .venv/bin/python day_4/05_cors_webhooks_headers.py
# Objectif : Configurer CORSMiddleware, limiter la taille maximale du Payload (413 Payload Too Large)
#            et vérifier la signature cryptographique HMAC-SHA256 d'un Webhook entrant (await request.body()).

import hashlib
import hmac
import json
import os
import sys
from typing import Optional
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

app = FastAPI(title="ISGP - CORSMiddleware, Webhooks HMAC & En-têtes de Sécurité", version="1.0.0")

MAX_BODY_BYTES = 1 * 1024 * 1024  # 1 Mo
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "whsec_isgp_partenaire_2026")
ORIGINES_AUTORISEES = ["http://localhost:3000", "https://portail.isgp.dz"]

# 1. CONFIGURATION CORSMiddleware NATIVE DE FASTAPI / STARLETTE
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINES_AUTORISEES,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Webhook-Signature"],
)


# 2. MIDDLEWARE DE DURCISSEMENT HTTP (X-Content-Type-Options, X-Frame-Options, Cache-Control)
@app.middleware("http")
async def durcir_entetes_securite(request: Request, call_next):
    reponse = await call_next(request)
    reponse.headers["X-Content-Type-Options"] = "nosniff"
    reponse.headers["X-Frame-Options"] = "DENY"
    reponse.headers["Cache-Control"] = "no-store"
    return reponse


# 3. RÉCEPTION SÉCURISÉE D'UN WEBHOOK (Vérification HMAC-SHA256 sur `await request.body()`)
@app.post("/api/webhooks/paiement")
async def recevoir_webhook_paiement(
    request: Request,
    x_webhook_signature: Optional[str] = Header(default=None, alias="X-Webhook-Signature"),
):
    corps_brut = await request.body()  # Octets exacts reçus sur le socket ASGI
    if len(corps_brut) > MAX_BODY_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Payload supérieur à 1 Mo")

    signature_recue = x_webhook_signature or ""
    signature_calculee = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        corps_brut,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature_recue, signature_calculee):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature Webhook invalide (401 Unauthorized)")

    evenement = json.loads(corps_brut.decode("utf-8") or "{}")
    return {"statut": "Webhook authentifié et traité", "evenement": evenement}


if __name__ == "__main__":
    if "--serve" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8001)
    else:
        client = TestClient(app)
        charge_json = b'{"facture_id": "FAC-2026-09", "montant_dzd": 45000}'
        sig = "sha256=" + hmac.new(WEBHOOK_SECRET.encode("utf-8"), charge_json, hashlib.sha256).hexdigest()

        r_ok = client.post(
            "/api/webhooks/paiement",
            content=charge_json,
            headers={"Content-Type": "application/json", "X-Webhook-Signature": sig, "Origin": "https://portail.isgp.dz"},
        )
        print("1. Webhook HMAC valide (200) :", r_ok.status_code, r_ok.json())
        print("2. En-tête CORS Access-Control-Allow-Origin :", r_ok.headers.get("access-control-allow-origin"))
        r_ko = client.post("/api/webhooks/paiement", content=charge_json, headers={"X-Webhook-Signature": "sha256=faux"})
        print("3. Webhook HMAC falsifié (401) :", r_ko.status_code, r_ko.json())
