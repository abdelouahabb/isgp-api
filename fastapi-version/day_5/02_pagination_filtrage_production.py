import os
# Fichier : day_5/02_pagination_filtrage_production.py
# Exécution : .venv/bin/python day_5/02_pagination_filtrage_production.py
# Objectif : Ingénierie Avancée d'une API FastAPI de Production (100 % FastAPI ASGI & Pydantic v2) :
#   1. Pagination par Offset/Limit (?page=1&per_page=2) avec enveloppe normalisée (meta, data, links)
#   2. Pagination Haute Performance par Curseur (?after_id=2&limit=2) pour les grands volumes SQL
#   3. Filtrage multi-critères (?domaine=Securite&duree_min=4) & Tri sécurisé par liste blanche (Whitelist)

import sys
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.testclient import TestClient

app = FastAPI(title="ISGP - Pagination Offset/Limit vs Cursor (FastAPI ASGI)", version="1.0.0")

CATALOGUE_FORMATIONS = [
    {"id": 1, "titre": "Architecture API REST & FastAPI", "domaine": "Backend", "duree_jours": 5, "tarif_dzd": 65000},
    {"id": 2, "titre": "Jinja2Templates & Formulaires Web", "domaine": "Web", "duree_jours": 3, "tarif_dzd": 45000},
    {"id": 3, "titre": "Persistance SQLite & Transactions ACID", "domaine": "Data", "duree_jours": 4, "tarif_dzd": 55000},
    {"id": 4, "titre": "Sécurité JWT, Cookies HttpOnly & RBAC", "domaine": "Securite", "duree_jours": 5, "tarif_dzd": 70000},
    {"id": 5, "titre": "Déploiement Nginx, Uvicorn & Load Balancing", "domaine": "DevOps", "duree_jours": 4, "tarif_dzd": 60000},
]

# Liste blanche stricte des champs autorisés pour le tri (empêche toute injection dans ORDER BY)
CHAMPS_TRI_AUTORISES = {"id", "duree_jours", "tarif_dzd", "titre"}


# 1. RECHERCHE MULTI-CRITÈRES, TRI SÉCURISÉ ET PAGINATION OFFSET/LIMIT
@app.get("/api/v1/catalogue/offset")
async def rechercher_avec_pagination_offset(
    domaine: Optional[str] = Query(default=None, description="Filtrer par domaine métier"),
    duree_min: int = Query(default=1, ge=1, le=30, description="Durée minimale en jours"),
    sort: str = Query(default="id", description="Champ de tri (préfixer par '-' pour décroissant)"),
    page: int = Query(default=1, ge=1, description="Numéro de page (>= 1)"),
    per_page: int = Query(default=2, ge=1, le=20, description="Nombre d'éléments par page (1 à 20)"),
):
    domaine_propre = (domaine or "").strip()
    tri = sort.strip()

    # Gestion du tri décroissant (ex: ?sort=-tarif_dzd) avec validation par liste blanche
    ordre_inverse = tri.startswith("-")
    cle_tri = tri.lstrip("-")
    if cle_tri not in CHAMPS_TRI_AUTORISES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "erreur": f"Champ de tri '{cle_tri}' interdit",
                "champs_autorises": sorted(CHAMPS_TRI_AUTORISES),
            },
        )

    # Filtrage métier
    resultats = [
        f for f in CATALOGUE_FORMATIONS
        if f["duree_jours"] >= duree_min and (not domaine_propre or f["domaine"].lower() == domaine_propre.lower())
    ]
    resultats.sort(key=lambda x: x[cle_tri], reverse=ordre_inverse)

    # Découpage de la fenêtre Offset / Limit
    total = len(resultats)
    offset = (page - 1) * per_page
    tranche = resultats[offset : offset + per_page]

    return {
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
    }


# 2. PAGINATION PAR CURSEUR (?after_id=2&limit=2) : Temps constant O(1) sur des millions de lignes SQL
@app.get("/api/v1/catalogue/cursor")
async def lister_avec_pagination_curseur(
    after_id: int = Query(default=0, ge=0, description="Dernier ID vu par le client"),
    limit: int = Query(default=2, ge=1, le=20, description="Nombre d'éléments à charger"),
):
    # Équivalent SQL : SELECT * FROM formations WHERE id > ? ORDER BY id ASC LIMIT ?
    suivants = [f for f in CATALOGUE_FORMATIONS if f["id"] > after_id][:limit]
    prochain_curseur = suivants[-1]["id"] if len(suivants) == limit else None

    return {
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
    }


if __name__ == "__main__":
    client = TestClient(app)
    print("=== 1. PAGINATION OFFSET/LIMIT + TRI DÉCROISSANT (?sort=-tarif_dzd&page=1&per_page=2) ===")
    r1 = client.get("/api/v1/catalogue/offset?sort=-tarif_dzd&page=1&per_page=2")
    print(r1.json())

    print("\n=== 2. PAGINATION PAR CURSEUR HAUTE PERFORMANCE (?after_id=2&limit=2) ===")
    r2 = client.get("/api/v1/catalogue/cursor?after_id=2&limit=2")
    print(r2.json())
    if "--once" not in sys.argv:
        import uvicorn
        port = int(os.environ.get("PORT", 8001))
        print("\n" + "=" * 76)
        print(f"[BOUCLE ASGI UVICORN / FASTAPI ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Interface Swagger UI interactive : http://127.0.0.1:{port}/docs")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur ASGI.")
        print("=" * 76)
        uvicorn.run(app, host="0.0.0.0", port=port)
