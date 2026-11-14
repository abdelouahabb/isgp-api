# Fichier : zero_to_hero/etape_04_persistance_sqlite_wal.py
# Etape 4/6 : Persistance SQLite ACID (WAL, foreign_keys, busy_timeout) via Depends(get_db)
import asyncio
from collections.abc import Generator
import math
import os
import sqlite3
import sys
from typing import Literal
import httpx
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
CHEMIN_DB = os.path.join(DOSSIER_COURANT, "zero_to_hero_isgp.db")
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))

app = FastAPI(
    title="Portail Web & API Catalogue Formations ISGP - Etape 04",
    version="0.4.0",
    description="Etape 4 : Base SQLite en mode WAL injectee par Depends(get_db) sur routes sync def.",
)

DomaineISGP = Literal["Architecture SI", "Cybersecurite", "Management Public", "Data & IA"]


class FormationEntree(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    code: str = Field(..., pattern=r"^ISGP-[A-Z]{3}-\d{3}$")
    intitule: str = Field(..., min_length=5, max_length=120)
    domaine: DomaineISGP
    duree_jours: int = Field(..., ge=1, le=30)
    tarif_dzd: int = Field(..., ge=10000, le=900000)


class FormationPatch(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    code: str | None = Field(default=None, pattern=r"^ISGP-[A-Z]{3}-\d{3}$")
    intitule: str | None = Field(default=None, min_length=5, max_length=120)
    domaine: DomaineISGP | None = None
    duree_jours: int | None = Field(default=None, ge=1, le=30)
    tarif_dzd: int | None = Field(default=None, ge=10000, le=900000)


class FormationSortie(FormationEntree):
    id: int


def _ouvrir_connexion_sqlite() -> sqlite3.Connection:
    conn = sqlite3.connect(CHEMIN_DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


def initialiser_base_sqlite() -> None:
    conn = _ouvrir_connexion_sqlite()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS formations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL,
                    intitule TEXT NOT NULL,
                    domaine TEXT NOT NULL,
                    duree_jours INTEGER NOT NULL,
                    tarif_dzd INTEGER NOT NULL
                )
                """
            )
            nb = conn.execute("SELECT COUNT(*) FROM formations").fetchone()[0]
            if nb == 0:
                conn.executemany(
                    "INSERT INTO formations (code, intitule, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
                    [
                        ("ISGP-API-201", "Architecture REST & FastAPI", "Architecture SI", 5, 95000),
                        ("ISGP-SEC-305", "Securite des APIs, OAuth2 & Zero-Trust", "Cybersecurite", 4, 88000),
                        ("ISGP-GOV-110", "Pilotage de la Transformation Numerique Publique", "Management Public", 3, 72000),
                        ("ISGP-DAT-240", "Ingenierie des Donnees & SQLite WAL", "Data & IA", 5, 99000),
                    ],
                )
    finally:
        conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = _ouvrir_connexion_sqlite()
    try:
        yield conn
    finally:
        conn.close()


initialiser_base_sqlite()


@app.exception_handler(RequestValidationError)
async def gestionnaire_validation_rfc7807(request: Request, exc: RequestValidationError) -> JSONResponse:
    erreurs = [
        {"champ": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        media_type="application/problem+json",
        content={
            "type": "https://isgp.dz/erreurs/validation-contrat",
            "title": "Violation du contrat de donnees Pydantic v2",
            "status": 422,
            "detail": f"{len(erreurs)} champ(s) invalide(s).",
            "instance": str(request.url.path),
            "errors": erreurs,
        },
    )


@app.get("/", response_class=HTMLResponse, summary="Portail Web SQLite WAL du catalogue ISGP")
def page_sqlite(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="etape_04_sqlite.html",
        context={"titre_page": "Portail Formations ISGP - Etape 04 : SQLite WAL & Depends(get_db)"},
    )


@app.get("/api/bonjour", summary="Salutation JSON du service")
def api_bonjour() -> dict[str, str | int]:
    return {"institut": "ISGP", "etape": 4, "statut": "operationnel", "moteur": "SQLite WAL"}


@app.get("/api/v1/sqlite-pragmas", summary="Inspecter les pragmas SQLite actifs")
def inspecter_pragmas(db: sqlite3.Connection = Depends(get_db)) -> dict:
    jm = db.execute("PRAGMA journal_mode;").fetchone()[0]
    fk = db.execute("PRAGMA foreign_keys;").fetchone()[0]
    bt = db.execute("PRAGMA busy_timeout;").fetchone()[0]
    return {"journal_mode": jm, "foreign_keys": fk, "busy_timeout": bt, "fichier": os.path.basename(CHEMIN_DB)}


@app.get("/api/v1/formations", summary="Lister, filtrer, trier et paginer depuis SQLite")
def lister_formations(
    domaine: str | None = Query(default=None),
    recherche: str | None = Query(default=None),
    tri: Literal["id", "tarif_dzd", "duree_jours"] = Query(default="id"),
    page: int = Query(default=1, ge=1),
    taille: int = Query(default=10, ge=1, le=50),
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    clauses: list[str] = []
    params: list[object] = []
    if domaine:
        clauses.append("LOWER(domaine) = LOWER(?)")
        params.append(domaine)
    if recherche:
        clauses.append("(LOWER(intitule) LIKE LOWER(?) OR LOWER(code) LIKE LOWER(?))")
        motif = f"%{recherche}%"
        params.extend([motif, motif])
    where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    colonne_tri = {"id": "id", "tarif_dzd": "tarif_dzd", "duree_jours": "duree_jours"}[tri]
    total = db.execute(f"SELECT COUNT(*) FROM formations {where_sql}", params).fetchone()[0]
    decalage = (page - 1) * taille
    lignes = db.execute(
        f"SELECT id, code, intitule, domaine, duree_jours, tarif_dzd FROM formations {where_sql} ORDER BY {colonne_tri} ASC LIMIT ? OFFSET ?",
        [*params, taille, decalage],
    ).fetchall()
    return {
        "meta": {"page": page, "taille": taille, "total_elements": total, "total_pages": max(1, math.ceil(total / taille))},
        "data": [dict(r) for r in lignes],
    }


@app.get("/api/v1/formations/{formation_id}", response_model=FormationSortie)
def obtenir_formation(formation_id: int = Path(..., ge=1), db: sqlite3.Connection = Depends(get_db)) -> dict:
    ligne = db.execute("SELECT * FROM formations WHERE id = ?", (formation_id,)).fetchone()
    if not ligne:
        raise HTTPException(status_code=404, detail=f"Formation #{formation_id} introuvable.")
    return dict(ligne)


@app.post("/api/v1/formations", response_model=FormationSortie, status_code=status.HTTP_201_CREATED)
def creer_formation(payload: FormationEntree, db: sqlite3.Connection = Depends(get_db)) -> dict:
    with db:
        cur = db.execute(
            "INSERT INTO formations (code, intitule, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
            (payload.code, payload.intitule, payload.domaine, payload.duree_jours, payload.tarif_dzd),
        )
        nouvel_id = cur.lastrowid
    return dict(db.execute("SELECT * FROM formations WHERE id = ?", (nouvel_id,)).fetchone())


@app.put("/api/v1/formations/{formation_id}", response_model=FormationSortie)
def remplacer_formation(
    payload: FormationEntree,
    formation_id: int = Path(..., ge=1),
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    obtenir_formation(formation_id, db)
    with db:
        db.execute(
            "UPDATE formations SET code = ?, intitule = ?, domaine = ?, duree_jours = ?, tarif_dzd = ? WHERE id = ?",
            (payload.code, payload.intitule, payload.domaine, payload.duree_jours, payload.tarif_dzd, formation_id),
        )
    return dict(db.execute("SELECT * FROM formations WHERE id = ?", (formation_id,)).fetchone())


@app.patch("/api/v1/formations/{formation_id}", response_model=FormationSortie)
def modifier_partiellement_formation(
    payload: FormationPatch,
    formation_id: int = Path(..., ge=1),
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    actuel = obtenir_formation(formation_id, db)
    actuel.update(payload.model_dump(exclude_unset=True))
    with db:
        db.execute(
            "UPDATE formations SET code = ?, intitule = ?, domaine = ?, duree_jours = ?, tarif_dzd = ? WHERE id = ?",
            (actuel["code"], actuel["intitule"], actuel["domaine"], actuel["duree_jours"], actuel["tarif_dzd"], formation_id),
        )
    return dict(db.execute("SELECT * FROM formations WHERE id = ?", (formation_id,)).fetchone())


@app.delete("/api/v1/formations/{formation_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer_formation(formation_id: int = Path(..., ge=1), db: sqlite3.Connection = Depends(get_db)) -> Response:
    obtenir_formation(formation_id, db)
    with db:
        db.execute("DELETE FROM formations WHERE id = ?", (formation_id,))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _auto_test() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/")).status_code == 200
        pragmas = (await client.get("/api/v1/sqlite-pragmas")).json()
        assert pragmas["journal_mode"].lower() == "wal" and pragmas["foreign_keys"] == 1
        rep_post = await client.post(
            "/api/v1/formations",
            json={"code": "ISGP-SQL-499", "intitule": "Test Transaction SQLite WAL", "domaine": "Data & IA", "duree_jours": 3, "tarif_dzd": 79000},
        )
        assert rep_post.status_code == 201
        fid = rep_post.json()["id"]
        rep_patch = await client.patch(f"/api/v1/formations/{fid}", json={"tarif_dzd": 84000})
        assert rep_patch.status_code == 200 and rep_patch.json()["tarif_dzd"] == 84000
        assert (await client.delete(f"/api/v1/formations/{fid}")).status_code == 204
        print("[OK] Etape 04 validee : SQLite WAL, foreign_keys=ON, busy_timeout=5000 et Depends(get_db).")


if __name__ == "__main__":
    if "--once" in sys.argv:
        asyncio.run(_auto_test())
    else:
        uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8001)))
