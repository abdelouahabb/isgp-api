"""
================================================================================
LABORATOIRE SQLITE & SÉCURITÉ SQL — ÉDITION FASTAPI (ASGI & PYDANTIC V2)
================================================================================
Ce script autonome illustre l'intégration professionnelle de SQLite3 dans une
API REST FastAPI sans aucune dépendance externe supplémentaire (sqlite3 inclus) :
  1. Injection de dépendance `Depends(get_db)` avec `yield` et fermeture garantie (`finally`)
  2. Paramètre `check_same_thread=False` + `PRAGMA journal_mode = WAL` pour le pool de threads ASGI
  3. Validation amont Pydantic v2 (`Field`) combinée aux requêtes préparées (`?` et `:nom`)
  4. Neutralisation d'une attaque par Injection SQL (`' OR '1'='1`)
  5. Liste blanche (Allowlist) pour sécuriser les identifiants SQL (`ORDER BY`)
================================================================================
"""

import os
import socket as _sock
import sqlite3
import sys
import tempfile
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="ISGP — Laboratoire SQLite3 & Sécurité SQL (FastAPI)")
DB_FILE = os.path.join(tempfile.gettempdir(), "isgp_sqlite_lab_fastapi.db")


# ==============================================================================
# 1. INJECTION DE DÉPENDANCE SQLITE DANS FASTAPI (Depends + yield)
# ==============================================================================
def get_db():
    """
    Générateur d'injection de dépendance FastAPI :
    - `check_same_thread=False` est indispensable car FastAPI exécute les routes `def`
      dans un pool de threads AnyIO.
    - Le bloc `finally` garantit la fermeture de la connexion même si une HTTPException survient.
    """
    conn = sqlite3.connect(DB_FILE, timeout=5.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()


def initialiser_schema_et_donnees():
    conn = sqlite3.connect(DB_FILE)
    with conn:
        conn.execute("DROP TABLE IF EXISTS formations_lab")
        conn.execute(
            """
            CREATE TABLE formations_lab (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_interne TEXT NOT NULL UNIQUE,
                titre TEXT NOT NULL,
                salle TEXT NOT NULL,
                duree_jours INTEGER NOT NULL CHECK(duree_jours BETWEEN 1 AND 30),
                budget_dzd REAL NOT NULL DEFAULT 0.0
            )
            """
        )
        donnees_initiales = [
            ("API-101", "Architecture REST & FastAPI ASGI", "Salle A", 5, 45000.0),
            ("SEC-202", "Sécurité des APIs, JWT & Requêtes Préparées", "Salle B", 4, 52000.0),
            ("SQL-303", "Persistance SQLite WAL & Modélisation Relationnelle", "Salle A", 3, 38000.0),
        ]
        conn.executemany(
            """
            INSERT INTO formations_lab (code_interne, titre, salle, duree_jours, budget_dzd)
            VALUES (?, ?, ?, ?, ?)
            """,
            donnees_initiales,
        )
    conn.close()


# ==============================================================================
# 2. SCHÉMA PYDANTIC V2 & ROUTES API AVEC REQUÊTES PARAMÉTRÉES (`?` ET `:nom`)
# ==============================================================================
class FormationCreate(BaseModel):
    code_interne: str = Field(..., min_length=3, max_length=20, examples=["FAST-404"])
    titre: str = Field(..., min_length=3, max_length=120, examples=["Atelier Pratique SQLite & Protection SQLi"])
    salle: str = Field(default="Salle A", max_length=40)
    duree_jours: int = Field(default=5, ge=1, le=30)
    budget_dzd: float = Field(default=40000.0, ge=0.0)


COLONNES_TRI_AUTORISEES = {
    "id": "id",
    "duree_jours": "duree_jours",
    "budget_dzd": "budget_dzd",
    "titre": "titre",
}


@app.get("/api/sqlite/formations")
def lister_formations(
    salle: Optional[str] = Query(default=None, description="Filtrer par salle (lié via `?`)"),
    min_jours: int = Query(default=1, ge=1, le=30),
    tri: str = Query(default="id"),
    ordre: str = Query(default="asc"),
    db: sqlite3.Connection = Depends(get_db),
):
    colonne_sure = COLONNES_TRI_AUTORISEES.get(tri, "id")
    direction_sure = "DESC" if ordre.lower() == "desc" else "ASC"

    sql = "SELECT id, code_interne, titre, salle, duree_jours, budget_dzd FROM formations_lab WHERE duree_jours >= ?"
    params = [min_jours]

    if salle:
        sql += " AND salle = ?"
        params.append(salle)

    sql += f" ORDER BY {colonne_sure} {direction_sure}"
    lignes = db.execute(sql, tuple(params)).fetchall()

    return {
        "framework": "FastAPI (sqlite3 + Depends(get_db))",
        "requete_preparee_sql": sql,
        "parametres_lies_tuple": params,
        "total": len(lignes),
        "data": [dict(r) for r in lignes],
    }


@app.post("/api/sqlite/formations", status_code=201)
def creer_formation(payload: FormationCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        with db:
            cur = db.execute(
                """
                INSERT INTO formations_lab (code_interne, titre, salle, duree_jours, budget_dzd)
                VALUES (:code_interne, :titre, :salle, :duree_jours, :budget_dzd)
                """,
                payload.model_dump(),
            )
            nouvel_id = cur.lastrowid
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "erreur": "Violation de contrainte d'intégrité SQLite (UNIQUE ou CHECK)",
                "detail_sqlite": str(exc),
            },
        )

    ligne = db.execute("SELECT * FROM formations_lab WHERE id = ?", (nouvel_id,)).fetchone()
    return {
        "statut": "Formation insérée avec validation Pydantic v2 + transaction ACID",
        "formation": dict(ligne),
    }


if __name__ == "__main__":
    initialiser_schema_et_donnees()
    print("=== DÉMONSTRATION SQLITE3 SOUS FASTAPI (DEPENDS(get_db) + `?` & `:nom`) ===")
    client = TestClient(app)

    r1 = client.get("/api/sqlite/formations?salle=Salle%20A&tri=duree_jours&ordre=desc").json()
    print(f"1. SELECT paramétré (?) : {r1['total']} lignes | SQL = {r1['requete_preparee_sql']}")
    print(f"   Paramètres liés      : {r1['parametres_lies_tuple']}")

    payload_injection = "Salle A' OR '1'='1"
    r_inj = client.get("/api/sqlite/formations", params={"salle": payload_injection}).json()
    print(f"\n2. Test anti-Injection SQL avec ?salle=\"{payload_injection}\" :")
    print(f"   -> Lignes retournées : {r_inj['total']} (Attendu: 0 — l'injection est traitée comme un simple texte littéral !)")

    r_post = client.post(
        "/api/sqlite/formations",
        json={
            "code_interne": "FAST-404",
            "titre": "Atelier Pratique SQLite & Protection SQLi",
            "salle": "Laboratoire 1",
            "duree_jours": 5,
            "budget_dzd": 49000.0,
        },
    )
    print(f"\n3. INSERT paramétré (:nom) -> Statut HTTP {r_post.status_code} | ID créé = {r_post.json()['formation']['id']}")

    if "--once" not in sys.argv:
        import uvicorn
        port = int(os.environ.get("PORT", 8001))
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
            if _s.connect_ex(("127.0.0.1", port)) == 0:
                _s2 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                _s2.bind(("127.0.0.1", 0))
                port = _s2.getsockname()[1]
                _s2.close()
        print("\n" + "=" * 76)
        print(f"[BOUCLE ASGI UVICORN / FASTAPI ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Testez : http://127.0.0.1:{port}/api/sqlite/formations")
        print(f"  -> Interface Swagger UI : http://127.0.0.1:{port}/docs")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur ASGI.")
        print("=" * 76)
        uvicorn.run(app, host="0.0.0.0", port=port)
