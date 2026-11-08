# Fichier : day_2/03_pagination_filtrage_tri.py
# Exécution : .venv/bin/python day_2/03_pagination_filtrage_tri.py
# Exemple d'appel :
#   http://127.0.0.1:5001/api/v1/formations?page=1&limit=2&salle=Salle+A&tri=duree_jours&ordre=desc

import math
from flask import Flask, jsonify, request

app = Flask(__name__)

CATALOGUE = [
    {"id": 1, "code": "API-101", "titre": "Fondamentaux HTTP & REST", "duree_jours": 2, "salle": "Salle A"},
    {"id": 2, "code": "FLK-201", "titre": "Développement API avec Flask", "duree_jours": 5, "salle": "Salle A"},
    {"id": 3, "code": "SQL-202", "titre": "Persistance SQLite & Transactions", "duree_jours": 3, "salle": "Salle B"},
    {"id": 4, "code": "SEC-301", "titre": "Sécurité, Bearer Tokens & HMAC", "duree_jours": 4, "salle": "Labo 1"},
    {"id": 5, "code": "OPS-302", "titre": "Rate Limiting & Résilience", "duree_jours": 2, "salle": "Labo 1"},
    {"id": 6, "code": "PRO-401", "titre": "Architecture Blueprints & Production", "duree_jours": 5, "salle": "Salle B"},
]

@app.route("/api/v1/formations", methods=["GET"])
def rechercher_formations():
    # 1. FILTRAGE (Query Params : ?salle=...&min_jours=...)
    salle_filtre = request.args.get("salle", "").strip()
    min_jours = int(request.args.get("min_jours", 1))

    resultats = [
        f for f in CATALOGUE
        if f["duree_jours"] >= min_jours
        and (not salle_filtre or f["salle"].lower() == salle_filtre.lower())
    ]

    # 2. TRI DYNAMIQUE (?tri=duree_jours&ordre=desc)
    champ_tri = request.args.get("tri", "id")
    if champ_tri not in ("id", "duree_jours", "titre"):
        champ_tri = "id"
    inversion = request.args.get("ordre", "asc").lower() == "desc"
    resultats.sort(key=lambda x: x[champ_tri], reverse=inversion)

    # 3. PAGINATION (?page=1&limit=2)
    page = max(1, int(request.args.get("page", 1)))
    limit = min(50, max(1, int(request.args.get("limit", 3))))
    total_elements = len(resultats)
    total_pages = max(1, math.ceil(total_elements / limit))

    debut = (page - 1) * limit
    fin = debut + limit
    tranche_page = resultats[debut:fin]

    return jsonify({
        "meta": {
            "page_actuelle": page,
            "elements_par_page": limit,
            "total_elements": total_elements,
            "total_pages": total_pages,
            "a_page_suivante": page < total_pages,
            "a_page_precedente": page > 1
        },
        "data": tranche_page
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
