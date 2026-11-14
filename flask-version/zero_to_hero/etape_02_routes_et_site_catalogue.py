# Fichier : zero_to_hero/etape_02_routes_et_site_catalogue.py
# Étape 2/6 : Routage RESTful, Filtrage (?domaine=&tri=), Pagination & Site Catalogue Interactif
# Exécution : .venv/bin/python flask-version/zero_to_hero/etape_02_routes_et_site_catalogue.py

import math
import os
import sys
from flask import Flask, jsonify, render_template, request

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))

FORMATIONS_INITIALES = [
    {"id": 1, "code": "API-101", "titre": "Fondamentaux HTTP/1.1, URI & JSON", "domaine": "Architecture", "duree_jours": 3, "tarif_dzd": 45000, "salle": "Salle A"},
    {"id": 2, "code": "FLK-201", "titre": "Developpement de Services Web avec Flask", "domaine": "Backend", "duree_jours": 5, "tarif_dzd": 65000, "salle": "Salle A"},
    {"id": 3, "code": "SQL-204", "titre": "Persistance SQLite WAL & Transactions ACID", "domaine": "Data", "duree_jours": 4, "tarif_dzd": 55000, "salle": "Salle B"},
    {"id": 4, "code": "SEC-301", "titre": "Securite API : Cookies, Bearer HMAC & RBAC", "domaine": "Securite", "duree_jours": 5, "tarif_dzd": 75000, "salle": "Labo 1"},
    {"id": 5, "code": "OPS-401", "titre": "Deploiement WSGI Gunicorn, Nginx & OpenAPI", "domaine": "DevOps", "duree_jours": 3, "tarif_dzd": 60000, "salle": "Salle B"},
]

CHAMPS_TRI_AUTORISES = {"id", "duree_jours", "tarif_dzd", "titre"}


@app.route("/", methods=["GET"])
def page_catalogue():
    domaines = sorted({f["domaine"] for f in FORMATIONS_INITIALES})
    return render_template(
        "etape_02_catalogue.html",
        etape="Etape 2/6 — Catalogue Web & API REST Paginée",
        domaines=domaines,
    ), 200


@app.route("/api/bonjour", methods=["GET"])
def api_bonjour():
    return jsonify({"statut": "operationnel", "etape": 2, "organisme": "ISGP"}), 200


@app.route("/api/v1/formations", methods=["GET"])
def lister_formations():
    domaine = request.args.get("domaine", "").strip()
    recherche = request.args.get("q", "").strip().lower()
    tri = request.args.get("tri", "id").strip()
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(20, max(1, request.args.get("limit", 3, type=int)))

    ordre_desc = tri.startswith("-")
    cle_tri = tri.lstrip("-")
    if cle_tri not in CHAMPS_TRI_AUTORISES:
        cle_tri = "id"

    filtrees = [
        f for f in FORMATIONS_INITIALES
        if (not domaine or f["domaine"].lower() == domaine.lower())
        and (not recherche or recherche in f["titre"].lower() or recherche in f["code"].lower())
    ]
    filtrees.sort(key=lambda x: x[cle_tri], reverse=ordre_desc)

    total = len(filtrees)
    total_pages = max(1, math.ceil(total / limit))
    debut = (page - 1) * limit
    tranche = filtrees[debut: debut + limit]

    return jsonify({
        "meta": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "tri": tri,
            "domaine": domaine or "tous",
        },
        "data": tranche,
    }), 200


@app.route("/api/v1/formations/<int:formation_id>", methods=["GET"])
def detail_formation(formation_id):
    for f in FORMATIONS_INITIALES:
        if f["id"] == formation_id:
            return jsonify({"data": f}), 200
    return jsonify({"erreur": f"Formation #{formation_id} introuvable"}), 404


if __name__ == "__main__":
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        r_list = client.get("/api/v1/formations?domaine=Securite&tri=-tarif_dzd&page=1&limit=2")
        assert r_list.status_code == 200 and r_list.get_json()["meta"]["total"] == 1
        r_one = client.get("/api/v1/formations/2")
        assert r_one.status_code == 200 and r_one.get_json()["data"]["code"] == "FLK-201"
        assert client.get("/api/v1/formations/999").status_code == 404
        print("[ETAPE 02 OK] Catalogue filtre/pagine + Detail <int:id> valides.")

    if "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        print(f"[ETAPE 02] Portail Catalogue actif sur http://127.0.0.1:{port}")
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
