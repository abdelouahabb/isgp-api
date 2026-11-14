import os
import sys
# Fichier : day_2/03_pagination_filtrage_tri.py
# Exécution : .venv/bin/python day_2/03_pagination_filtrage_tri.py
# Exemple d'appel :
#   http://127.0.0.1:5001/api/v1/formations?page=1&limit=2&salle=Salle+A&tri=duree_jours&ordre=desc

import math
from flask import Flask, jsonify, render_template, request

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))

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


@app.route("/", methods=["GET"])
def index_pagination():
    return render_template("index_03_pagination.html"), 200


if __name__ == "__main__":
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        rep = client.get("/api/v1/formations?page=1&limit=2&salle=Salle+A&tri=duree_jours&ordre=desc")
        print("Statut HTTP :", rep.status_code)
        print("Réponse paginée :", rep.get_json())
    if "--once" not in sys.argv:
        import socket as _sock
        port = int(os.environ.get("PORT", 5001))
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
            if _s.connect_ex(("127.0.0.1", port)) == 0:
                _s2 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                _s2.bind(("127.0.0.1", 0))
                port = _s2.getsockname()[1]
                _s2.close()
        print("\n" + "=" * 76)
        print(f"[SERVEUR WSGI FLASK ACTIF] Serveur en écoute sur http://127.0.0.1:{port}")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print(f"  -> Testez les routes en direct sur http://127.0.0.1:{port} (navigateur, curl, Postman)")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
