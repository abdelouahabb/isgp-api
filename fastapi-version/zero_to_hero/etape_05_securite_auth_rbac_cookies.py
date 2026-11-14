# Fichier : zero_to_hero/etape_05_securite_auth_rbac_cookies.py
# Etape 5/6 : Cookies signes HttpOnly (SameSite=lax), HTTPBearer HMAC-SHA256, RBAC & Rate-Limit 429
import asyncio
import base64
from collections import deque
from collections.abc import Callable, Generator
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
from fastapi import Cookie, Depends, FastAPI, HTTPException, Path, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
CHEMIN_DB = os.path.join(DOSSIER_COURANT, "zero_to_hero_isgp.db")
CLE_SECRETE_HMAC = os.environ.get("ISGP_SECRET_KEY", "cle-hmac-isgp-zero-to-hero-2026-securisee").encode("utf-8")
NOM_COOKIE_SESSION = "isgp_session_signee"
LIMITE_FENETRE_REQUETES = 6
DUREE_FENETRE_SECONDES = 10.0
HISTORIQUE_CLIENTS: dict[str, deque[float]] = {}

templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))
schema_bearer = HTTPBearer(auto_error=False)

app = FastAPI(
    title="Portail Web & API Catalogue Formations ISGP - Etape 05",
    version="0.5.0",
    description="Etape 5 : Authentification Bearer HMAC & Cookie HttpOnly, RBAC et Rate-Limiting 429.",
)

COMPTES_DEMO: dict[str, dict[str, str]] = {
    "admin": {"mot_de_passe": "isgp-admin-2026", "role": "admin"},
    "lecteur": {"mot_de_passe": "isgp-lecteur-2026", "role": "lecteur"},
}

DomaineISGP = Literal["Architecture SI", "Cybersecurite", "Management Public", "Data & IA"]


class IdentifiantsConnexion(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    identifiant: str = Field(..., min_length=3, max_length=40)
    mot_de_passe: str = Field(..., min_length=6, max_length=80)


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


def signer_jeton_hmac(utilisateur: str, role: str, duree_sec: int = 3600) -> str:
    charge = {"sub": utilisateur, "role": role, "exp": int(time.time()) + duree_sec}
    corps_b64 = base64.urlsafe_b64encode(json.dumps(charge, separators=(",", ":")).encode("utf-8")).decode("ascii").rstrip("=")
    signature = hmac.new(CLE_SECRETE_HMAC, corps_b64.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{corps_b64}.{signature}"


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
            detail="Quota de requetes depasse sur la fenetre glissante.",
            headers={"Retry-After": str(attente), "X-RateLimit-Limit": str(LIMITE_FENETRE_REQUETES), "X-RateLimit-Remaining": "0"},
        )
    fenetre.append(maintenant)
    response.headers["X-RateLimit-Limit"] = str(LIMITE_FENETRE_REQUETES)
    response.headers["X-RateLimit-Remaining"] = str(LIMITE_FENETRE_REQUETES - len(fenetre))


def obtenir_utilisateur_courant(
    cred: HTTPAuthorizationCredentials | None = Depends(schema_bearer),
    cookie_session: str | None = Cookie(default=None, alias=NOM_COOKIE_SESSION),
) -> dict:
    jeton_brut = cred.credentials if cred else cookie_session
    if not jeton_brut:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise (Bearer token ou cookie HttpOnly).",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return verifier_jeton_hmac(jeton_brut)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


def exiger_role(role_requis: str) -> Callable[[dict], dict]:
    def _dependance_rbac(profil: dict = Depends(obtenir_utilisateur_courant)) -> dict:
        if profil.get("role") != role_requis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acces refuse : le role '{role_requis}' est requis (role actuel : '{profil.get('role')}').",
            )
        return profil

    return _dependance_rbac


def _valider_identifiants(payload: IdentifiantsConnexion) -> dict[str, str]:
    compte = COMPTES_DEMO.get(payload.identifiant)
    if not compte or not hmac.compare_digest(payload.mot_de_passe.encode("utf-8"), compte["mot_de_passe"].encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe invalide.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"utilisateur": payload.identifiant, "role": compte["role"]}


@app.exception_handler(RequestValidationError)
async def gestionnaire_validation_rfc7807(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        media_type="application/problem+json",
        content={
            "type": "https://isgp.dz/erreurs/validation-contrat",
            "title": "Violation du contrat Pydantic v2",
            "status": 422,
            "detail": f"{len(exc.errors())} erreur(s) de validation.",
            "instance": str(request.url.path),
        },
    )


@app.get("/", response_class=HTMLResponse, summary="Portail Web Securite, Cookies HttpOnly & RBAC")
def page_securite(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="etape_05_securite.html",
        context={"titre_page": "Portail Formations ISGP - Etape 05 : Auth, Cookies, RBAC & 429"},
    )


@app.post("/api/v1/auth/token", summary="Emettre un jeton Bearer signe HMAC-SHA256")
def emettre_jeton_bearer(payload: IdentifiantsConnexion) -> dict:
    info = _valider_identifiants(payload)
    jeton = signer_jeton_hmac(info["utilisateur"], info["role"])
    return {"access_token": jeton, "token_type": "bearer", **info}


@app.post("/api/v1/auth/cookie-login", summary="Ouvrir une session via cookie signe HttpOnly (SameSite=lax)")
def connexion_cookie(payload: IdentifiantsConnexion, response: Response) -> dict:
    info = _valider_identifiants(payload)
    jeton = signer_jeton_hmac(info["utilisateur"], info["role"])
    response.set_cookie(
        key=NOM_COOKIE_SESSION,
        value=jeton,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600,
        path="/",
    )
    return {"session": "ouverte", "cookie": NOM_COOKIE_SESSION, **info}


@app.post("/api/v1/auth/cookie-logout", summary="Revoquer le cookie de session HttpOnly")
def deconnexion_cookie(response: Response) -> dict:
    response.delete_cookie(key=NOM_COOKIE_SESSION, path="/")
    return {"session": "fermee"}


@app.get("/api/v1/auth/profil", summary="Consulter le profil courant (Bearer ou Cookie)")
def lire_profil(profil: dict = Depends(obtenir_utilisateur_courant)) -> dict:
    return {"utilisateur": profil["sub"], "role": profil["role"], "exp": profil["exp"]}


@app.get("/api/v1/formations", dependencies=[Depends(verifier_rate_limit)], summary="Lister les formations (protege par Rate-Limit 429)")
def lister_formations(
    taille: int = Query(default=10, ge=1, le=50),
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    lignes = db.execute("SELECT * FROM formations ORDER BY id ASC LIMIT ?", (taille,)).fetchall()
    return {"meta": {"total_elements": len(lignes)}, "data": [dict(r) for r in lignes]}


@app.post("/api/v1/formations", status_code=status.HTTP_201_CREATED, summary="Creer une formation (Role admin requis)")
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


@app.delete("/api/v1/formations/{formation_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer une formation (Role admin requis)")
def supprimer_formation(
    formation_id: int = Path(..., ge=1),
    _admin: dict = Depends(exiger_role("admin")),
    db: sqlite3.Connection = Depends(get_db),
) -> Response:
    with db:
        cur = db.execute("DELETE FROM formations WHERE id = ?", (formation_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Formation #{formation_id} introuvable.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _auto_test() -> None:
    HISTORIQUE_CLIENTS.clear()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/")).status_code == 200
        rep_401 = await client.get("/api/v1/auth/profil")
        assert rep_401.status_code == 401 and "Bearer" in rep_401.headers.get("www-authenticate", "")
        tok_lecteur = (await client.post("/api/v1/auth/token", json={"identifiant": "lecteur", "mot_de_passe": "isgp-lecteur-2026"})).json()["access_token"]
        rep_403 = await client.post(
            "/api/v1/formations",
            headers={"Authorization": f"Bearer {tok_lecteur}"},
            json={"code": "ISGP-SEC-501", "intitule": "Tentative Lecteur", "domaine": "Cybersecurite", "duree_jours": 3, "tarif_dzd": 80000},
        )
        assert rep_403.status_code == 403
        rep_cookie = await client.post("/api/v1/auth/cookie-login", json={"identifiant": "admin", "mot_de_passe": "isgp-admin-2026"})
        assert rep_cookie.status_code == 200 and "HttpOnly" in rep_cookie.headers.get("set-cookie", "")
        rep_201 = await client.post(
            "/api/v1/formations",
            json={"code": "ISGP-SEC-502", "intitule": "Creation Admin Cookie", "domaine": "Cybersecurite", "duree_jours": 4, "tarif_dzd": 91000},
        )
        assert rep_201.status_code == 201
        await client.delete(f"/api/v1/formations/{rep_201.json()['id']}")
        codes = [(await client.get("/api/v1/formations")).status_code for _ in range(LIMITE_FENETRE_REQUETES + 1)]
        assert 429 in codes
        print("[OK] Etape 05 validee : Cookie HttpOnly (SameSite=lax), Bearer HMAC, RBAC (401/403) et 429 Retry-After.")


if __name__ == "__main__":
    if "--once" in sys.argv:
        asyncio.run(_auto_test())
    else:
        uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", 8001)))
