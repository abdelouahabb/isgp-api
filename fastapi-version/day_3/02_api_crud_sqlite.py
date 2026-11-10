# Fichier : day_3/02_api_crud_sqlite.py
# Exécution : .venv/bin/python day_3/02_api_crud_sqlite.py
# Objectif : Persistance relationnelle SQLite complète (GET, POST, PUT, DELETE) avec FastAPI :
#   - Requêtes paramétrées (?) neutralisant 100% des Injections SQL
#   - Route Web Jinja2Templates + Formulaire HTML (Form(...) -> day_3/templates/catalogue_sqlite.html)
#   - Routes API REST JSON (Pydantic BaseModel + Depends(get_db))

import os
import sqlite3
import sys
from typing import Optional
import uvicorn
from fastapi import Depends, FastAPI, Form, HTTPException, Path, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="ISGP - API CRUD SQLite & Jinja2Templates", version="1.0.0")
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))
DB_FILE = os.path.join(DOSSIER_COURANT, "day_3_formations.db")


def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS formations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            duree_jours INTEGER DEFAULT 5,
            salle TEXT DEFAULT 'Salle A'
        )
    """)
    nb = conn.execute("SELECT COUNT(*) FROM formations").fetchone()[0]
    if nb == 0:
        conn.execute(
            "INSERT INTO formations (titre, duree_jours, salle) VALUES (?, ?, ?)",
            ("Architecture des APIs REST & SQLite", 5, "Salle A"),
        )
    conn.commit()
    conn.close()


init_db()


class FormationSQLiteIn(BaseModel):
    titre: str = Field(..., min_length=3, max_length=120)
    duree_jours: int = Field(default=5, ge=1, le=30)
    salle: str = Field(default="Salle A")


class FormationSQLiteUpdate(BaseModel):
    titre: Optional[str] = Field(default=None, min_length=3, max_length=120)
    salle: Optional[str] = Field(default=None)


# 1. ROUTE WEB JINJA2 + FORMULAIRE HTML (<form method="POST"> -> Form(...) -> SQLite)
@app.get("/formations-sqlite", response_class=HTMLResponse)
async def afficher_catalogue_sqlite(request: Request, db: sqlite3.Connection = Depends(get_db)):
    lignes = db.execute("SELECT * FROM formations ORDER BY id ASC").fetchall()
    return templates.TemplateResponse(
        request=request,
        name="catalogue_sqlite.html",
        context={"formations": [dict(r) for r in lignes], "message": None},
    )


@app.post("/formations-sqlite", response_class=HTMLResponse)
async def ajouter_via_formulaire_sqlite(
    request: Request,
    titre: str = Form(...),
    duree_jours: int = Form(default=5),
    salle: str = Form(default="Salle A"),
    db: sqlite3.Connection = Depends(get_db),
):
    message = None
    titre_propre = titre.strip()
    salle_propre = salle.strip() or "Salle A"
    if len(titre_propre) >= 3:
        cur = db.execute(
            "INSERT INTO formations (titre, duree_jours, salle) VALUES (?, ?, ?)",
            (titre_propre, duree_jours, salle_propre),
        )
        db.commit()
        message = f"Formation '{titre_propre}' insérée dans SQLite (ID #{cur.lastrowid})"

    lignes = db.execute("SELECT * FROM formations ORDER BY id ASC").fetchall()
    return templates.TemplateResponse(
        request=request,
        name="catalogue_sqlite.html",
        context={"formations": [dict(r) for r in lignes], "message": message},
    )


# 2. ROUTES API REST JSON (GET, POST, PUT, DELETE)
@app.get("/api/formations")
async def lister(db: sqlite3.Connection = Depends(get_db)):
    lignes = db.execute("SELECT * FROM formations ORDER BY id ASC").fetchall()
    return [dict(r) for r in lignes]


@app.post("/api/formations", status_code=status.HTTP_201_CREATED)
async def creer_formation_sqlite(payload: FormationSQLiteIn, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute(
        "INSERT INTO formations (titre, duree_jours, salle) VALUES (?, ?, ?)",
        (payload.titre.strip(), payload.duree_jours, payload.salle.strip()),
    )
    db.commit()
    new_id = cur.lastrowid
    return {"id": new_id, "titre": payload.titre.strip(), "duree_jours": payload.duree_jours, "salle": payload.salle.strip()}


@app.put("/api/formations/{id}")
async def modifier_formation(
    payload: FormationSQLiteUpdate,
    id: int = Path(..., ge=1),
    db: sqlite3.Connection = Depends(get_db),
):
    actuelle = db.execute("SELECT * FROM formations WHERE id = ?", (id,)).fetchone()
    if not actuelle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Formation ID {id} introuvable")

    titre = payload.titre if payload.titre is not None else actuelle["titre"]
    salle = payload.salle if payload.salle is not None else actuelle["salle"]
    db.execute("UPDATE formations SET titre = ?, salle = ? WHERE id = ?", (titre, salle, id))
    db.commit()
    return {"message": "Mise à jour effectuée", "id": id, "titre": titre, "salle": salle}


@app.delete("/api/formations/{id}")
async def supprimer_formation(id: int = Path(..., ge=1), db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("DELETE FROM formations WHERE id = ?", (id,))
    db.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Formation ID {id} introuvable")
    return {"message": f"Formation ID {id} supprimée"}


if __name__ == "__main__":
    client = TestClient(app)
    print("=== 1. AJOUT VIA FORMULAIRE HTML (POST /formations-sqlite -> Form FastAPI) ===")
    rep_form = client.post(
        "/formations-sqlite",
        data={"titre": "Sécurité SQL & Jinja2", "duree_jours": "4", "salle": "Salle B"},
    )
    for l in rep_form.text.splitlines():
        if "notification-succes" in l or "Sécurité SQL" in l:
            print("  ->", l.strip())

    print("\n=== 2. LECTURE DU CATALOGUE SQLITE (GET /api/formations -> JSON) ===")
    print(client.get("/api/formations").json())
    if "--once" not in sys.argv:
        import uvicorn
        import socket as _sock
        port = int(os.environ.get("PORT", 8001))
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
            if _s.connect_ex(("127.0.0.1", port)) == 0:
                _s2 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                _s2.bind(("127.0.0.1", 0))
                port = _s2.getsockname()[1]
                _s2.close()
        print("\n" + "=" * 76)
        print(f"[BOUCLE ASGI UVICORN / FASTAPI ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Interface Swagger UI interactive : http://127.0.0.1:{port}/docs")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur ASGI.")
        print("=" * 76)
        uvicorn.run(app, host="0.0.0.0", port=port)
