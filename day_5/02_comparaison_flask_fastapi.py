# Fichier : day_5/02_comparaison_flask_fastapi.py
# Objectif : Comparer l'approche explicite synchrone (Flask / WSGI)
#            et l'approche déclarative typée (FastAPI / ASGI + Pydantic).

# ================= 1. IMPLÉMENTATION EXPLICITE EN FLASK (WSGI) =================
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api/formations", methods=["POST"])
def creer_flask():
    corps = request.get_json(silent=True) or {}
    if not isinstance(corps.get("titre"), str) or len(corps["titre"].strip()) < 3:
        return jsonify({"erreur": "Champ 'titre' invalide"}), 422
    duree = corps.get("duree_jours", 5)
    return jsonify({"cree": corps["titre"].strip(), "duree_jours": duree}), 201


# ================= 2. ÉQUIVALENT DÉCLARATIF EN FASTAPI (ASGI) =================
# from fastapi import FastAPI, Header, HTTPException
# from pydantic import BaseModel, Field
#
# app_fast = FastAPI(title="ISGP API", version="1.0.0")  # Génère /docs (Swagger) et /openapi.json
#
# class FormationSchema(BaseModel):
#     titre: str = Field(..., min_length=3)
#     duree_jours: int = Field(default=5, ge=1, le=30)
#
# @app_fast.post("/api/formations", status_code=201)
# async def creer_fastapi(formation: FormationSchema, x_api_key: str = Header(...)):
#     # Si le JSON entrant ne respecte pas FormationSchema, FastAPI renvoie
#     # automatiquement une erreur HTTP 422 détaillée avant même d'entrer dans la fonction !
#     return {"cree": formation.titre, "duree_jours": formation.duree_jours}
