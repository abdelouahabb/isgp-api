"""
================================================================================
MANUEL & LABORATOIRE SQLITE3 — ÉDITION FASTAPI (ASGI, Depends & contextlib.closing)
================================================================================
Ce script autonome de référence illustre toutes les opérations SQLite3 dans une
API REST FastAPI sans dépendance externe supplémentaire (sqlite3 inclus) :
  1. Injection `Depends(get_db)` avec `yield`, `finally: conn.close()` et `check_same_thread=False`
  2. Pragmas de production (`journal_mode=WAL`, `synchronous=NORMAL`, `foreign_keys=ON`, `busy_timeout=5000`)
  3. Fermeture explicite et déterministe du curseur avec `contextlib.closing(conn.cursor())`
  4. CRUD Complet :
     - `find_many` (`fetchall()` / `fetchmany()`) avec filtres `?` et liste blanche `ORDER BY`
     - `find_one` (`fetchone()`) avec gestion du tuple à 1 élément `(id,)` et statut 404
     - `insert_one` avec marqueurs nommés `:nom`, `payload.model_dump()`, et `cur.lastrowid`
     - `insert_many` en lot atomique avec `cur.executemany()`
     - `update` et `delete` avec inspection de `cur.rowcount`
================================================================================
"""

from contextlib import closing
import os
import socket as _sock
import sqlite3
import sys
import tempfile
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI(title="ISGP — Manuel & Laboratoire SQLite3 (FastAPI)")
DB_FILE = os.path.join(tempfile.gettempdir(), "isgp_sqlite_lab_fastapi.db")


# ==============================================================================
# 1. INJECTION DE DÉPENDANCE SQLITE3, PRAGMAS & FERMETURE GARANTIE
# ==============================================================================
def get_db():
    """Générateur d'injection FastAPI : 1 connexion isolée par requête HTTP."""
    conn = sqlite3.connect(DB_FILE, timeout=5.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    try:
        yield conn
    finally:
        conn.close()


def initialiser_schema_et_donnees():
    conn = sqlite3.connect(DB_FILE)
    with conn:
        with closing(conn.cursor()) as cur:
            cur.execute("DROP TABLE IF EXISTS formations_lab")
            cur.execute(
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
            lot_initial = [
                ("API-101", "Architecture REST & FastAPI ASGI", "Salle A", 5, 45000.0),
                ("SEC-202", "Sécurité des APIs, JWT & Requêtes Préparées", "Salle B", 4, 52000.0),
                ("SQL-303", "Persistance SQLite WAL & Modélisation Relationnelle", "Salle A", 3, 38000.0),
            ]
            cur.executemany(
                """
                INSERT INTO formations_lab (code_interne, titre, salle, duree_jours, budget_dzd)
                VALUES (?, ?, ?, ?, ?)
                """,
                lot_initial,
            )
    conn.close()


# ==============================================================================
# 2. MODÈLES PYDANTIC & OPÉRATIONS FIND_MANY, FIND_ONE, INSERT, UPDATE, DELETE
# ==============================================================================
class FormationCreate(BaseModel):
    code_interne: str = Field(..., min_length=3, max_length=20, examples=["FAST-404"])
    titre: str = Field(..., min_length=3, max_length=120, examples=["Atelier Pratique SQLite & Protection SQLi"])
    salle: str = Field(default="Salle A", max_length=40)
    duree_jours: int = Field(default=5, ge=1, le=30)
    budget_dzd: float = Field(default=40000.0, ge=0.0)


class FormationPatch(BaseModel):
    salle: str = Field(..., min_length=2, max_length=40)


COLONNES_TRI_AUTORISEES = {
    "id": "id",
    "duree_jours": "duree_jours",
    "budget_dzd": "budget_dzd",
    "titre": "titre",
}


@app.get("/api/sqlite/formations")
def lister_formations(
    salle: Optional[str] = Query(default=None),
    min_jours: int = Query(default=1, ge=1, le=30),
    tri: str = Query(default="id"),
    ordre: str = Query(default="asc"),
    db: sqlite3.Connection = Depends(get_db),
):
    """FIND_MANY : Lecture multiple via fetchall() avec fermeture déterministe du curseur."""
    colonne_sure = COLONNES_TRI_AUTORISEES.get(tri, "id")
    direction_sure = "DESC" if ordre.lower() == "desc" else "ASC"

    sql = "SELECT id, code_interne, titre, salle, duree_jours, budget_dzd FROM formations_lab WHERE duree_jours >= ?"
    params = [min_jours]
    if salle:
        sql += " AND salle = ?"
        params.append(salle)
    sql += f" ORDER BY {colonne_sure} {direction_sure}"

    with closing(db.cursor()) as cur:
        cur.execute(sql, tuple(params))
        lignes = [dict(r) for r in cur.fetchall()]

    return {
        "operation": "find_many (fetchall)",
        "framework": "FastAPI (sqlite3 + Depends(get_db) + closing(cursor))",
        "requete_preparee_sql": sql,
        "parametres_lies_tuple": params,
        "total": len(lignes),
        "data": lignes,
    }


@app.get("/api/sqlite/formations/{formation_id}")
def obtenir_formation(formation_id: int, db: sqlite3.Connection = Depends(get_db)):
    """FIND_ONE : Lecture d'un seul enregistrement via fetchone() et tuple `(formation_id,)`."""
    with closing(db.cursor()) as cur:
        cur.execute(
            "SELECT id, code_interne, titre, salle, duree_jours, budget_dzd FROM formations_lab WHERE id = ?",
            (formation_id,),
        )
        ligne = cur.fetchone()

    if ligne is None:
        raise HTTPException(status_code=404, detail=f"Aucune formation trouvée avec id={formation_id}")

    return {
        "operation": "find_one (fetchone)",
        "formation": dict(ligne),
    }


@app.post("/api/sqlite/formations", status_code=201)
def creer_formation(payload: FormationCreate, db: sqlite3.Connection = Depends(get_db)):
    """INSERT_ONE : Insertion avec marqueurs nommés `:nom` et transaction ACID `with db:`."""
    try:
        with db:
            with closing(db.cursor()) as cur:
                cur.execute(
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

    with closing(db.cursor()) as cur:
        cur.execute("SELECT * FROM formations_lab WHERE id = ?", (nouvel_id,))
        ligne = cur.fetchone()

    return {
        "operation": "insert_one (lastrowid)",
        "statut": "Formation insérée avec validation Pydantic v2 + transaction ACID",
        "formation": dict(ligne),
    }


@app.patch("/api/sqlite/formations/{formation_id}")
def modifier_formation(formation_id: int, payload: FormationPatch, db: sqlite3.Connection = Depends(get_db)):
    """UPDATE : Mise à jour partielle et vérification de `cur.rowcount`."""
    with db:
        with closing(db.cursor()) as cur:
            cur.execute(
                "UPDATE formations_lab SET salle = ? WHERE id = ?",
                (payload.salle, formation_id),
            )
            lignes_modifiees = cur.rowcount

    if lignes_modifiees == 0:
        raise HTTPException(status_code=404, detail=f"Formation id={formation_id} introuvable (rowcount=0)")

    with closing(db.cursor()) as cur:
        cur.execute("SELECT * FROM formations_lab WHERE id = ?", (formation_id,))
        ligne = cur.fetchone()

    return {
        "operation": "update (rowcount)",
        "rowcount": lignes_modifiees,
        "formation": dict(ligne),
    }


@app.delete("/api/sqlite/formations/{formation_id}")
def supprimer_formation(formation_id: int, db: sqlite3.Connection = Depends(get_db)):
    """DELETE : Suppression avec vérification de `cur.rowcount`."""
    with db:
        with closing(db.cursor()) as cur:
            cur.execute("DELETE FROM formations_lab WHERE id = ?", (formation_id,))
            lignes_supprimees = cur.rowcount

    if lignes_supprimees == 0:
        raise HTTPException(status_code=404, detail=f"Formation id={formation_id} introuvable (rowcount=0)")

    return {
        "operation": "delete (rowcount)",
        "rowcount": lignes_supprimees,
        "message": f"Formation #{formation_id} supprimée définitivement.",
    }


if __name__ == "__main__":
    initialiser_schema_et_donnees()
    print("=== DÉMONSTRATION COMPLÈTE SQLITE3 SOUS FASTAPI (FIND_MANY, FIND_ONE, INSERT, UPDATE, DELETE) ===")
    client = TestClient(app)

    r_many = client.get("/api/sqlite/formations?salle=Salle%20A&tri=duree_jours&ordre=desc").json()
    print(f"1. FIND_MANY (fetchall) : {r_many['total']} lignes | SQL = {r_many['requete_preparee_sql']}")

    r_one = client.get("/api/sqlite/formations/1").json()
    print(f"2. FIND_ONE  (fetchone) : ID #1 -> {r_one['formation']['code_interne']} ({r_one['formation']['titre']})")

    payload_injection = "Salle A' OR '1'='1"
    r_inj = client.get("/api/sqlite/formations", params={"salle": payload_injection}).json()
    print(f"3. ANTI-SQLi (?)        : ?salle=\"{payload_injection}\" -> {r_inj['total']} ligne retournée (Injection neutralisée !)")

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
    new_id = r_post.json()["formation"]["id"]
    print(f"4. INSERT_ONE (:nom)    : HTTP {r_post.status_code} | cur.lastrowid = {new_id}")

    r_patch = client.patch(f"/api/sqlite/formations/{new_id}", json={"salle": "Salle Conférence"}).json()
    print(f"5. UPDATE (rowcount)    : cur.rowcount = {r_patch['rowcount']} | Nouvelle salle = {r_patch['formation']['salle']}")

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
        print(f"  -> Testez FIND_MANY : http://127.0.0.1:{port}/api/sqlite/formations")
        print(f"  -> Testez FIND_ONE  : http://127.0.0.1:{port}/api/sqlite/formations/1")
        print(f"  -> Interface Swagger UI : http://127.0.0.1:{port}/docs")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur ASGI.")
        print("=" * 76)
        uvicorn.run(app, host="0.0.0.0", port=port)
