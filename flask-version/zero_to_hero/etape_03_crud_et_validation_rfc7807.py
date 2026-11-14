# Fichier : zero_to_hero/etape_03_crud_et_validation_rfc7807.py
# Étape 3/6 : Opérations CRUD Complètes (POST, PUT, PATCH, DELETE) & Validation RFC 7807 (422)
# Exécution : .venv/bin/python flask-version/zero_to_hero/etape_03_crud_et_validation_rfc7807.py

import json
import math
import os
import sys
from flask import Flask, Response, jsonify, render_template, request

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))

CATALOGUE = [
    {"id": 1, "code": "API-101", "titre": "Fondamentaux HTTP/1.1 & JSON", "domaine": "Architecture", "duree_jours": 3, "tarif_dzd": 45000},
    {"id": 2, "code": "FLK-201", "titre": "Services Web RESTful avec Flask", "domaine": "Backend", "duree_jours": 5, "tarif_dzd": 65000},
    {"id": 3, "code": "SEC-301", "titre": "Securite API, Cookies & RBAC", "domaine": "Securite", "duree_jours": 4, "tarif_dzd": 70000},
]
CHAMPS_TRI = {"id", "duree_jours", "tarif_dzd", "titre"}


def erreur_rfc7807(status, title, detail, erreurs_champs=None):
    probleme = {
        "type": "https://api.isgp.dz/erreurs/validation-contrat",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.path,
    }
    if erreurs_champs:
        probleme["errors"] = erreurs_champs
    return Response(
        json.dumps(probleme, ensure_ascii=False),
        status=status,
        mimetype="application/problem+json",
    )


def valider_formation(corps, partiel=False):
    if not isinstance(corps, dict):
        return {"_corps": "Un objet JSON valide est requis."}
    erreurs = {}
    if not partiel or "code" in corps:
        code = str(corps.get("code", "")).strip()
        if len(code) < 3 or len(code) > 16:
            erreurs["code"] = "Le code catalogue doit contenir entre 3 et 16 caracteres."
    if not partiel or "titre" in corps:
        titre = str(corps.get("titre", "")).strip()
        if len(titre) < 4 or len(titre) > 120:
            erreurs["titre"] = "Le titre doit contenir entre 4 et 120 caracteres."
    if not partiel or "duree_jours" in corps:
        try:
            j = int(corps.get("duree_jours"))
            if not (1 <= j <= 30):
                erreurs["duree_jours"] = "La duree doit etre comprise entre 1 et 30 jours."
        except (TypeError, ValueError):
            erreurs["duree_jours"] = "La duree doit etre un nombre entier."
    if not partiel or "tarif_dzd" in corps:
        try:
            t = int(corps.get("tarif_dzd"))
            if t < 0:
                erreurs["tarif_dzd"] = "Le tarif en DZD doit etre positif ou nul."
        except (TypeError, ValueError):
            erreurs["tarif_dzd"] = "Le tarif doit etre un entier."
    return erreurs


@app.route("/", methods=["GET"])
def page_crud():
    return render_template("etape_03_crud.html", etape="Etape 3/6 — CRUD Complet & Erreurs RFC 7807"), 200


@app.route("/api/v1/formations", methods=["GET"])
def lister_formations():
    domaine = request.args.get("domaine", "").strip()
    tri = request.args.get("tri", "id").strip()
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(20, max(1, request.args.get("limit", 10, type=int)))
    desc = tri.startswith("-")
    cle = tri.lstrip("-") if tri.lstrip("-") in CHAMPS_TRI else "id"
    items = [f for f in CATALOGUE if not domaine or f["domaine"].lower() == domaine.lower()]
    items.sort(key=lambda x: x[cle], reverse=desc)
    debut = (page - 1) * limit
    return jsonify({
        "meta": {"page": page, "total": len(items), "total_pages": max(1, math.ceil(len(items) / limit))},
        "data": items[debut: debut + limit],
    }), 200


@app.route("/api/v1/formations/<int:formation_id>", methods=["GET"])
def obtenir_formation(formation_id):
    cible = next((f for f in CATALOGUE if f["id"] == formation_id), None)
    if not cible:
        return erreur_rfc7807(404, "Ressource introuvable", f"Aucune formation avec l'ID #{formation_id}.")
    return jsonify({"data": cible}), 200


@app.route("/api/v1/formations", methods=["POST"])
def creer_formation():
    corps = request.get_json(silent=True)
    erreurs = valider_formation(corps, partiel=False)
    if erreurs:
        return erreur_rfc7807(422, "Validation metier echouee", "Certains champs sont invalides.", erreurs)
    nouvelle = {
        "id": max((f["id"] for f in CATALOGUE), default=0) + 1,
        "code": str(corps["code"]).strip().upper(),
        "titre": str(corps["titre"]).strip(),
        "domaine": str(corps.get("domaine", "Backend")).strip() or "Backend",
        "duree_jours": int(corps["duree_jours"]),
        "tarif_dzd": int(corps["tarif_dzd"]),
    }
    CATALOGUE.append(nouvelle)
    return jsonify({"data": nouvelle}), 201


@app.route("/api/v1/formations/<int:formation_id>", methods=["PUT"])
def remplacer_formation(formation_id):
    cible = next((f for f in CATALOGUE if f["id"] == formation_id), None)
    if not cible:
        return erreur_rfc7807(404, "Ressource introuvable", f"Formation #{formation_id} absente.")
    corps = request.get_json(silent=True)
    erreurs = valider_formation(corps, partiel=False)
    if erreurs:
        return erreur_rfc7807(422, "Remplacement PUT invalide", "PUT exige tous les champs valides.", erreurs)
    cible.update({
        "code": str(corps["code"]).strip().upper(),
        "titre": str(corps["titre"]).strip(),
        "domaine": str(corps.get("domaine", cible["domaine"])).strip(),
        "duree_jours": int(corps["duree_jours"]),
        "tarif_dzd": int(corps["tarif_dzd"]),
    })
    return jsonify({"data": cible}), 200


@app.route("/api/v1/formations/<int:formation_id>", methods=["PATCH"])
def modifier_formation_partiel(formation_id):
    cible = next((f for f in CATALOGUE if f["id"] == formation_id), None)
    if not cible:
        return erreur_rfc7807(404, "Ressource introuvable", f"Formation #{formation_id} absente.")
    corps = request.get_json(silent=True)
    erreurs = valider_formation(corps, partiel=True)
    if erreurs:
        return erreur_rfc7807(422, "Modification PATCH invalide", "Champs partiels invalides.", erreurs)
    for champ in ("code", "titre", "domaine"):
        if champ in corps:
            cible[champ] = str(corps[champ]).strip()
    for champ_num in ("duree_jours", "tarif_dzd"):
        if champ_num in corps:
            cible[champ_num] = int(corps[champ_num])
    return jsonify({"data": cible}), 200


@app.route("/api/v1/formations/<int:formation_id>", methods=["DELETE"])
def supprimer_formation(formation_id):
    idx = next((i for i, f in enumerate(CATALOGUE) if f["id"] == formation_id), None)
    if idx is None:
        return erreur_rfc7807(404, "Ressource introuvable", f"Formation #{formation_id} absente.")
    CATALOGUE.pop(idx)
    return jsonify({"statut": "supprime", "id": formation_id}), 200


if __name__ == "__main__":
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        r_422 = client.post("/api/v1/formations", json={"code": "X", "titre": "AB", "duree_jours": 99, "tarif_dzd": -1})
        assert r_422.status_code == 422 and "application/problem+json" in r_422.content_type
        r_201 = client.post("/api/v1/formations", json={"code": "DAT-305", "titre": "Ingenierie SQLite", "domaine": "Data", "duree_jours": 4, "tarif_dzd": 58000})
        assert r_201.status_code == 201
        fid = r_201.get_json()["data"]["id"]
        assert client.patch(f"/api/v1/formations/{fid}", json={"tarif_dzd": 62000}).status_code == 200
        assert client.put(f"/api/v1/formations/{fid}", json={"code": "DAT-305", "titre": "Ingenierie SQLite WAL", "domaine": "Data", "duree_jours": 5, "tarif_dzd": 65000}).status_code == 200
        assert client.delete(f"/api/v1/formations/{fid}").status_code == 200
        print("[ETAPE 03 OK] CRUD complet + Validation RFC 7807 (application/problem+json) valides.")

    if "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        print(f"[ETAPE 03] Portail CRUD & RFC 7807 actif sur http://127.0.0.1:{port}")
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
