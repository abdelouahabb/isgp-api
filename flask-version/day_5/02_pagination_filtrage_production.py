import os
# Fichier : day_5/02_pagination_filtrage_production.py
# Exécution : .venv/bin/python day_5/02_pagination_filtrage_production.py
# Objectif : Ingénierie Avancée d'une API Flask de Production (100 % Flask WSGI) :
#   1. Pagination par Offset/Limit (?page=2&per_page=2) avec enveloppe normalisée (meta, data, links)
#   2. Pagination Haute Performance par Curseur (?after_id=2&limit=2) pour les grands volumes SQL
#   3. Filtrage multi-critères (?domaine=Securite&duree_min=4) & Tri sécurisé par liste blanche (Whitelist)

import sys
from flask import Flask, jsonify, render_template, request

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))

CATALOGUE_FORMATIONS = [
    {"id": 1, "titre": "Architecture API REST & Flask", "domaine": "Backend", "duree_jours": 5, "tarif_dzd": 65000},
    {"id": 2, "titre": "Templates Jinja2 & Formulaires Web", "domaine": "Web", "duree_jours": 3, "tarif_dzd": 45000},
    {"id": 3, "titre": "persistance SQLite & Transactions ACID", "domaine": "Data", "duree_jours": 4, "tarif_dzd": 55000},
    {"id": 4, "titre": "Sécurité JWT, Cookies HttpOnly & RBAC", "domaine": "Securite", "duree_jours": 5, "tarif_dzd": 70000},
    {"id": 5, "titre": "Déploiement Nginx, Gunicorn & Load Balancing", "domaine": "DevOps", "duree_jours": 4, "tarif_dzd": 60000},
]

# Liste blanche stricte des champs autorisés pour le tri (empêche toute injection dans ORDER BY)
CHAMPS_TRI_AUTORISES = {"id", "duree_jours", "tarif_dzd", "titre"}


# 1. RECHERCHE MULTI-CRITÈRES, TRI SÉCURISÉ ET PAGINATION OFFSET/LIMIT
@app.route("/api/v1/catalogue/offset", methods=["GET"])
def rechercher_avec_pagination_offset():
    domaine = request.args.get("domaine", "").strip()
    duree_min = request.args.get("duree_min", 1, type=int)
    tri = request.args.get("sort", "id").strip()
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(20, max(1, request.args.get("per_page", 2, type=int)))

    # Gestion du tri décroissant (ex: ?sort=-tarif_dzd) avec validation par liste blanche
    ordre_inverse = tri.startswith("-")
    cle_tri = tri.lstrip("-")
    if cle_tri not in CHAMPS_TRI_AUTORISES:
        return jsonify({
            "erreur": f"Champ de tri '{cle_tri}' interdit",
            "champs_autorises": sorted(CHAMPS_TRI_AUTORISES),
        }), 422

    # Filtrage métier
    resultats = [
        f for f in CATALOGUE_FORMATIONS
        if f["duree_jours"] >= duree_min and (not domaine or f["domaine"].lower() == domaine.lower())
    ]
    resultats.sort(key=lambda x: x[cle_tri], reverse=ordre_inverse)

    # Découpage de la fenêtre Offset / Limit
    total = len(resultats)
    offset = (page - 1) * per_page
    tranche = resultats[offset: offset + per_page]

    return jsonify({
        "meta": {
            "mode_pagination": "offset_limit",
            "page": page,
            "per_page": per_page,
            "total_items": total,
            "total_pages": max(1, (total + per_page - 1) // per_page),
        },
        "data": tranche,
        "links": {
            "self": f"/api/v1/catalogue/offset?page={page}&per_page={per_page}",
            "next": f"/api/v1/catalogue/offset?page={page + 1}&per_page={per_page}" if offset + per_page < total else None,
        },
    }), 200


# 2. PAGINATION PAR CURSEUR (?after_id=2&limit=2) : Temps constant O(1) sur des millions de lignes SQL
@app.route("/api/v1/catalogue/cursor", methods=["GET"])
def lister_avec_pagination_curseur():
    after_id = request.args.get("after_id", 0, type=int)
    limit = min(20, max(1, request.args.get("limit", 2, type=int)))

    # Équivalent SQL : SELECT * FROM formations WHERE id > ? ORDER BY id ASC LIMIT ?
    suivants = [f for f in CATALOGUE_FORMATIONS if f["id"] > after_id][:limit]
    prochain_curseur = suivants[-1]["id"] if len(suivants) == limit else None

    return jsonify({
        "meta": {
            "mode_pagination": "cursor_keyset",
            "after_id": after_id,
            "limit": limit,
            "next_cursor": prochain_curseur,
        },
        "data": suivants,
        "links": {
            "next": f"/api/v1/catalogue/cursor?after_id={prochain_curseur}&limit={limit}" if prochain_curseur else None,
        },
    }), 200


@app.route("/", methods=["GET"])
def index_pagination_prod():
    return render_template("index_02_pagination_prod.html"), 200


if __name__ == "__main__":
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        print("=== 1. PAGINATION OFFSET/LIMIT + TRI DÉCROISSANT (?sort=-tarif_dzd&page=1&per_page=2) ===")
        r1 = client.get("/api/v1/catalogue/offset?sort=-tarif_dzd&page=1&per_page=2")
        print(r1.get_json())

        print("\n=== 2. PAGINATION PAR CURSEUR HAUTE PERFORMANCE (?after_id=2&limit=2) ===")
        r2 = client.get("/api/v1/catalogue/cursor?after_id=2&limit=2")
        print(r2.get_json())
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
