# Fichier : day_5/02_comparaison_flask_fastapi.py

# ================= IMPLÉMENTATION EXPLICITE EN FLASK =================
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api/formations", methods=["POST"])
def creer_flask():
    data = request.get_json()
    return jsonify({"cree": data["titre"]}), 201


# ================= ÉQUIVALENT DÉCLARATIF EN FASTAPI =================
# from fastapi import FastAPI
# from pydantic import BaseModel
#
# app_fast = FastAPI()
#
# class FormationSchema(BaseModel):
#     titre: str
#     duree_jours: int = 5
#
# @app_fast.post("/api/formations", status_code=201)
# def creer_fastapi(formation: FormationSchema):
#     return {"cree": formation.titre}
