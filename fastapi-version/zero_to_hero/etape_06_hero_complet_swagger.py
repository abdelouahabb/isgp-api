# Fichier : zero_to_hero/etape_06_hero_complet_swagger.py
# Etape 6/6 (Hero) : APIRouter, Lifespan, SQLite WAL, RBAC, Middleware X-Process-Time-Ms & OpenAPI 3.1
import asyncio
import base64
from collections import deque
from collections.abc import AsyncIterator, Callable, Generator
from contextlib import asynccontextmanager
import hashlib
import hmac
import json
import math
import os
import sqlite3
import sys
import time
from typing import Literal
import httpx
import uvicorn
from fastapi import APIRouter, Cookie, Depends, FastAPI, HTTPException, Path, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
CHEMIN_DB = os.path.join(DOSSIER_COURANT, "zero_to_hero_isgp.db")
CLE_SECRETE_HMAC = os.environ.get("ISGP_SECRET_KEY", "cle-hmac-isgp-hero-final-2026-securisee").encode("utf-8")
NOM_COOKIE_SESSION = "isgp_session_signee"
LIMITE_FENETRE_REQUETES = 20
DUREE_FENETRE_SECONDES = 10.0
HISTORIQUE_CLIENTS: dict[str, deque[float]] = {}
HORODATAGE_DEMARRAGE = time.monotonic()

templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))
schema_bearer = HTTPBearer(auto_error=False)

COMPTES_DEMO: dict[str, dict[str, str]] = {
    "admin": {"mot_de_passe": "isgp-admin-2026", "role": "admin"},
    "lecteur": {"mot_de_passe": "isgp-lecteur-2026", "role": "lecteur"},
}

DomaineISGP = Literal["Architecture SI", "Cybersecurite", "Management Public", "Data & IA"]


class IdentifiantsConnexion(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    identifiant: str = Field(..., min_length=3, max_length=40, examples=["admin"])
    mot_de_passe: str = Field(..., min_length=6, max_length=80, examples=["isgp-admin-2026"])


class FormationEntree(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    code: str = Field(..., pattern=r"^ISGP-[A-Z]{3}-\d{3}$", examples=["ISGP-OAS-601"])
    intitule: str = Field(..., min_length=5, max_length=120, examples=["Gouvernance API & OpenAPI 3.1"])
    domaine: DomaineISGP = Field(..., examples=["Architecture SI"])
    duree_jours: int = Field(..., ge=1, le=30, examples=[5])
    tarif_dzd: int = Field(..., ge=10000, le=900000, examples=[98000])


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
            if conn.execute("SELECT COUNT(*) FROM formations").fetchone()[0] == 0:
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


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    initialiser_base_sqlite()
    application.state.sqlite_pret = True
    yield
    application.state.sqlite_pret = False


TAGS_OPENAPI = [
    {"name": "Portail & Sante", "description": "Portail Web HTML Jinja2, sonde /health et documentation OpenAPI 3.1."},
    {"name": "Authentification & Sessions", "description": "Jetons Bearer HMAC-SHA256 et cookies de session HttpOnly (SameSite=lax)."},
    {"name": "Catalogue Formations", "description": "Operations CRUD SQLite WAL protegees par RBAC et Rate-Limiting."},
]

app = FastAPI(
    title="Portail Web & API Catalogue Formations ISGP - Architecture Hero",
    summary="Application finale du parcours Zero-to-Hero FastAPI, Pydantic v2, SQLite WAL et OpenAPI 3.1.",
    description=(
        "Plateforme complete exposant simultanement un portail Web HTML interactif (`GET /`) "
        "et une API REST versionnee (`/api/v1/...`), documentee par OpenAPI 3.1.0 (`/openapi.json`), "
        "Swagger UI (`/docs`, `/api/docs`) et ReDoc (`/redoc`)."
    ),
    version="1.0.0",
    contact={"name": "Equipe Pedagogique ISGP", "url": "https://isgp.dz"},
    license_info={"name": "Usage Pedagogique ISGP"},
    openapi_tags=TAGS_OPENAPI,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


@app.middleware("http")
async def middleware_chronometrage(request: Request, call_next):
    debut = time.perf_counter()
    reponse = await call_next(request)
    duree_ms = (time.perf_counter() - debut) * 1000.0
    reponse.headers["X-Process-Time-Ms"] = f"{duree_ms:.2f}"
    return reponse


def signer_jeton_hmac(utilisateur: str, role: str, duree_sec: int = 3600) -> str:
    charge = {"sub": utilisateur, "role": role, "exp": int(time.time()) + duree_sec}
    corps_b64 = base64.urlsafe_b64encode(json.dumps(charge, separators=(",", ":")).encode("utf-8")).decode("ascii").rstrip("=")
    sig = hmac.new(CLE_SECRETE_HMAC, corps_b64.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{corps_b64}.{sig}"


def verifier_jeton_hmac(jeton: str) -> dict:
    if "." not in jeton:
        raise ValueError("Format de jeton invalide.")
    corps_b64, sig_recue = jeton.split(".", 1)
    sig_attendue = hmac.new(CLE_SECRETE_HMAC, corps_b64.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig_recue, sig_attendue):
        raise ValueError("Signature HMAC invalide.")
    padding = "=" * (-len(corps_b64) % 4)
    charge = json.loads(base64.urlsafe_b64decode(corps_b64 + padding).decode("utf-8"))
    if charge.get("exp", 0) < int(time.time()):
        raise ValueError("Jeton expire.")
    return charge


def verifier_rate_limit(request: Request, response: Response) -> None:
    ip_client = request.client.host if request.client else "127.0.0.1"
    maintenant = time.monotonic()
    fenetre = HISTORIQUE_CLIENTS.setdefault(ip_client, deque())
    while fenetre and (maintenant - fenetre[0]) > DUREE_FENETRE_SECONDES:
        fenetre.popleft()
    if len(fenetre) >= LIMITE_FENETRE_REQUETES:
        attente = max(1, int(math.ceil(DUREE_FENETRE_SECONDES - (maintenant - fenetre[0]))))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quota de requetes depasse.",
            headers={"Retry-After": str(attente)},
        )
    fenetre.append(maintenant)
    response.headers["X-RateLimit-Remaining"] = str(LIMITE_FENETRE_REQUETES - len(fenetre))


def obtenir_utilisateur_courant(
    cred: HTTPAuthorizationCredentials | None = Depends(schema_bearer),
    cookie_session: str | None = Cookie(default=None, alias=NOM_COOKIE_SESSION),
) -> dict:
    jeton_brut = cred.credentials if cred else cookie_session
    if not jeton_brut:
        raise HTTPException(status_code=401, detail="Authentification requise.", headers={"WWW-Authenticate": "Bearer"})
    try:
        return verifier_jeton_hmac(jeton_brut)
    except ValueError as err:
        raise HTTPException(status_code=401, detail=str(err), headers={"WWW-Authenticate": "Bearer"}) from err


def exiger_role(role_requis: str) -> Callable[[dict], dict]:
    def _rbac(profil: dict = Depends(obtenir_utilisateur_courant)) -> dict:
        if profil.get("role") != role_requis:
            raise HTTPException(status_code=403, detail=f"Role '{role_requis}' requis.")
        return profil

    return _rbac


@app.exception_handler(RequestValidationError)
async def gestionnaire_validation_rfc7807(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        media_type="application/problem+json",
        content={
            "type": "https://isgp.dz/erreurs/validation-contrat",
            "title": "Violation du contrat Pydantic v2",
            "status": 422,
            "detail": f"{len(exc.errors())} erreur(s) detectee(s).",
            "instance": str(request.url.path),
        },
    )


router_systeme = APIRouter(tags=["Portail & Sante"])
router_auth = APIRouter(prefix="/api/v1/auth", tags=["Authentification & Sessions"])
router_formations = APIRouter(prefix="/api/v1/formations", tags=["Catalogue Formations"])


@router_systeme.get("/", response_class=HTMLResponse, summary="Portail Web complet ISGP (Jinja2 + API REST)")
def page_hero(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="etape_06_hero.html",
        context={"titre_page": "Portail Web & API Catalogue Formations ISGP - Architecture Hero"},
    )


@router_systeme.get("/health", summary="Sonde de sante ASGI, SQLite WAL et contrat OpenAPI 3.1")
def sonde_health(db: sqlite3.Connection = Depends(get_db)) -> dict:
    journal = db.execute("PRAGMA journal_mode;").fetchone()[0]
    total = db.execute("SELECT COUNT(*) FROM formations").fetchone()[0]
    return {
        "statut": "sain",
        "journal_mode": journal,
        "formations_en_base": total,
        "openapi_version": app.openapi_version,
        "uptime_secondes": round(time.monotonic() - HORODATAGE_DEMARRAGE, 2),
    }


@router_systeme.get("/api/docs", include_in_schema=False)
async def swagger_ui_alias() -> HTMLResponse:
    return get_swagger_ui_html(openapi_url=app.openapi_url or "/openapi.json", title=f"{app.title} - Swagger UI")


def _verifier_identifiants(payload: IdentifiantsConnexion) -> dict[str, str]:
    compte = COMPTES_DEMO.get(payload.identifiant)
    if not compte or not hmac.compare_digest(payload.mot_de_passe.encode("utf-8"), compte["mot_de_passe"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Identifiants invalides.", headers={"WWW-Authenticate": "Bearer"})
    return {"utilisateur": payload.identifiant, "role": compte["role"]}


@router_auth.post("/token", summary="Obtenir un jeton Bearer HMAC-SHA256")
def emettre_token(payload: IdentifiantsConnexion) -> dict:
    info = _verifier_identifiants(payload)
    return {"access_token": signer_jeton_hmac(info["utilisateur"], info["role"]), "token_type": "bearer", **info}


@router_auth.post("/cookie-login", summary="Ouvrir une session par cookie signe HttpOnly")
def cookie_login(payload: IdentifiantsConnexion, response: Response) -> dict:
    info = _verifier_identifiants(payload)
    response.set_cookie(
        key=NOM_COOKIE_SESSION,
        value=signer_jeton_hmac(info["utilisateur"], info["role"]),
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600,
        path="/",
    )
    return {"session": "ouverte", **info}


@router_auth.post("/cookie-logout", summary="Fermer la session cookie HttpOnly")
def cookie_logout(response: Response) -> dict:
    response.delete_cookie(key=NOM_COOKIE_SESSION, path="/")
    return {"session": "fermee"}


@router_auth.get("/profil", summary="Inspecter l'identite courante")
def profil_courant(profil: dict = Depends(obtenir_utilisateur_courant)) -> dict:
    return {"utilisateur": profil["sub"], "role": profil["role"], "exp": profil["exp"]}


@router_formations.get("", dependencies=[Depends(verifier_rate_limit)], summary="Rechercher et paginer le catalogue")
def lister_formations(
    domaine: str | None = Query(default=None),
    recherche: str | None = Query(default=None),
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
        params.extend([f"%{recherche}%", f"%{recherche}%"])
    where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    total = db.execute(f"SELECT COUNT(*) FROM formations {where_sql}", params).fetchone()[0]
    lignes = db.execute(
        f"SELECT * FROM formations {where_sql} ORDER BY id ASC LIMIT ? OFFSET ?",
        [*params, taille, (page - 1) * taille],
    ).fetchall()
    return {"meta": {"page": page, "taille": taille, "total_elements": total}, "data": [dict(r) for r in lignes]}


@router_formations.get("/{formation_id}", response_model=FormationSortie, summary="Consulter une formation par ID")
def detail_formation(formation_id: int = Path(..., ge=1), db: sqlite3.Connection = Depends(get_db)) -> dict:
    ligne = db.execute("SELECT * FROM formations WHERE id = ?", (formation_id,)).fetchone()
    if not ligne:
        raise HTTPException(status_code=404, detail=f"Formation #{formation_id} introuvable.")
    return dict(ligne)


@router_formations.post("", response_model=FormationSortie, status_code=201, summary="Creer une formation (Admin)")
def creer_formation(
    payload: FormationEntree,
    _admin: dict = Depends(exiger_role("admin")),
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    with db:
        cur = db.execute(
            "INSERT INTO formations (code, intitule, domaine, duree_jours, tarif_dzd) VALUES (?, ?, ?, ?, ?)",
            (payload.code, payload.intitule, payload.domaine, payload.duree_jours, payload.tarif_dzd),
        )
        fid = cur.lastrowid
    return dict(db.execute("SELECT * FROM formations WHERE id = ?", (fid,)).fetchone())


@router_formations.patch("/{formation_id}", response_model=FormationSortie, summary="Modifier partiellement (Admin)")
def patch_formation(
    payload: FormationPatch,
    formation_id: int = Path(..., ge=1),
    _admin: dict = Depends(exiger_role("admin")),
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    actuel = detail_formation(formation_id, db)
    actuel.update(payload.model_dump(exclude_unset=True))
    with db:
        db.execute(
            "UPDATE formations SET code=?, intitule=?, domaine=?, duree_jours=?, tarif_dzd=? WHERE id=?",
            (actuel["code"], actuel["intitule"], actuel["domaine"], actuel["duree_jours"], actuel["tarif_dzd"], formation_id),
        )
    return dict(db.execute("SELECT * FROM formations WHERE id = ?", (formation_id,)).fetchone())


@router_formations.delete("/{formation_id}", status_code=204, summary="Supprimer une formation (Admin)")
def supprimer_formation(
    formation_id: int = Path(..., ge=1),
    _admin: dict = Depends(exiger_role("admin")),
    db: sqlite3.Connection = Depends(get_db),
) -> Response:
    with db:
        cur = db.execute("DELETE FROM formations WHERE id = ?", (formation_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Formation #{formation_id} introuvable.")
    return Response(status_code=204)


app.include_router(router_systeme)
app.include_router(router_auth)
app.include_router(router_formations)
initialiser_base_sqlite()


async def _auto_test() -> None:
    HISTORIQUE_CLIENTS.clear()
    async with lifespan(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            rep_home = await client.get("/")
            assert rep_home.status_code == 200 and "x-process-time-ms" in rep_home.headers
            rep_health = await client.get("/health")
            assert rep_health.status_code == 200 and rep_health.json()["statut"] == "sain"
            rep_oas = await client.get("/openapi.json")
            assert rep_oas.status_code == 200 and rep_oas.json()["openapi"].startswith("3.1")
            assert (await client.get("/docs")).status_code == 200
            assert (await client.get("/api/docs")).status_code == 200
            assert (await client.get("/redoc")).status_code == 200
            tok = (await client.post("/api/v1/auth/token", json={"identifiant": "admin", "mot_de_passe": "isgp-admin-2026"})).json()["access_token"]
            rep_c = await client.post(
                "/api/v1/formations",
                headers={"Authorization": f"Bearer {tok}"},
                json={"code": "ISGP-OAS-699", "intitule": "Architecture Hero Complete", "domaine": "Architecture SI", "duree_jours": 5, "tarif_dzd": 99000},
            )
            assert rep_c.status_code == 201
            await client.delete(f"/api/v1/formations/{rep_c.json()['id']}", headers={"Authorization": f"Bearer {tok}"})
            print("[OK] Etape 06 Hero validee : GET /, /health, APIRouter, Lifespan, OpenAPI 3.1, /docs, /api/docs et /redoc.")


if __name__ == "__main__":
    if "--once" in sys.argv:
        asyncio.run(_auto_test())
    else:
        uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8001)))
