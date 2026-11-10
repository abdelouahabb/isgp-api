# Fichier : day_4/07_cookies_et_sessions_securisees.py
# Exécution : .venv/bin/python day_4/07_cookies_et_sessions_securisees.py
# Objectif : Maîtriser la gestion et la sécurité des Cookies en API & Web avec FastAPI :
#   1. Cookie standard non signé (Cookie(None) / response.set_cookie) -> Préférences UI uniquement
#   2. Les 3 drapeaux de sécurité obligatoires : httponly=True (anti-XSS), secure=True (HTTPS), samesite="strict" (anti-CSRF)
#   3. Cookie de Session signé cryptographiquement par HMAC (URLSafeTimedSerializer)
#   4. Révocation propre d'un cookie (response.delete_cookie -> Max-Age=0)

import os
import sys
from typing import Optional
import uvicorn
from fastapi import Cookie, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient
from itsdangerous import BadSignature, URLSafeTimedSerializer
from pydantic import BaseModel

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="ISGP - Cookies HttpOnly & Sessions Signées FastAPI", version="1.0.0")
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))

# Clé secrète serveur obligatoire pour signer cryptographiquement les cookies
SECRET_KEY = os.environ.get("FASTAPI_SECRET_KEY", "cle-secrete-hmac-cookies-isgp-2026")
signataire_session = URLSafeTimedSerializer(SECRET_KEY, salt="isgp-session-cookie")
signataire_jeton = URLSafeTimedSerializer(SECRET_KEY, salt="isgp-auth-cookie")


class CookieLoginPayload(BaseModel):
    identifiant: str = "stagiaire_isgp"
    theme: str = "institutionnel"


# 1. CONNEXION : Émettre un cookie HttpOnly sécurisé + un cookie de session signé + un cookie de préférence
@app.post("/api/auth/cookie-login")
async def connexion_par_cookie(corps: CookieLoginPayload, response: Response):
    identifiant = corps.identifiant.strip()
    theme_choisi = corps.theme.strip()

    # A. Cookie de session signé par HMAC (URLSafeTimedSerializer)
    valeur_session = signataire_session.dumps({"utilisateur": identifiant, "role": "auditeur_securite"})
    response.set_cookie(
        key="isgp_session",
        value=valeur_session,
        max_age=3600,
        httponly=True,
        secure=False,      # Mettre True en production HTTPS
        samesite="lax",
        path="/",
    )

    # B. Cookie sensible d'authentification : httponly=True + samesite="strict" obligatoires !
    jeton_signe = signataire_jeton.dumps({"sub": identifiant, "scope": "api:read"})
    response.set_cookie(
        key="isgp_auth_token",
        value=jeton_signe,
        max_age=3600,
        httponly=True,     # Bouclier anti-XSS : inaccessible via document.cookie en JS
        secure=False,      # Mettre True en production (exige HTTPS)
        samesite="strict", # Bouclier anti-CSRF : jamais envoyé depuis un site externe
        path="/",
    )

    # C. Cookie de préférence visuelle non sensible (lisible par le JS frontal si besoin)
    response.set_cookie("isgp_theme", theme_choisi, max_age=86400 * 30, httponly=False, samesite="lax", path="/")

    return {
        "statut": "Authentifié par Cookies sécurisés (FastAPI)",
        "utilisateur": identifiant,
        "cookies_emis": [
            "isgp_session (Signé HMAC + HttpOnly)",
            "isgp_auth_token (HttpOnly + SameSite=strict)",
            "isgp_theme (Préférence UI)",
        ],
    }


# 2. INSPECTION : Lire et vérifier les cookies reçus via le paramètre déclaratif Cookie(None)
@app.get("/api/auth/cookie-inspect")
async def inspecter_cookies(
    request: Request,
    isgp_auth_token: Optional[str] = Cookie(default=None),
    isgp_session: Optional[str] = Cookie(default=None),
    isgp_theme: str = Cookie(default="clair"),
):
    if not isgp_auth_token or not isgp_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Aucun cookie d'authentification valide reçu (401)",
        )

    try:
        charge_jeton = signataire_jeton.loads(isgp_auth_token, max_age=3600)
        charge_session = signataire_session.loads(isgp_session, max_age=3600)
    except BadSignature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cookie isgp_auth_token ou isgp_session falsifié ou expiré (401)",
        )

    return {
        "authentifie": True,
        "session_signee_hmac": charge_session,
        "cookie_httponly_decode": charge_jeton,
        "cookie_preference_theme": isgp_theme,
        "en_tete_cookie_brut": request.headers.get("cookie", ""),
    }


# 3. PORTAIL WEB JINJA2 PROTÉGÉ PAR LES COOKIES
@app.get("/portail-cookies", response_class=HTMLResponse)
async def portail_html_cookies(
    request: Request,
    isgp_session: Optional[str] = Cookie(default=None),
    isgp_theme: str = Cookie(default="institutionnel"),
):
    if not isgp_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session absente")
    try:
        sess = signataire_session.loads(isgp_session, max_age=3600)
    except BadSignature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session invalide")

    return templates.TemplateResponse(
        request=request,
        name="portail_cookies.html",
        context={
            "utilisateur": sess["utilisateur"],
            "role": sess.get("role", "invité"),
            "theme": isgp_theme,
        },
    )


# 4. DÉCONNEXION : Purger la session et forcer l'expiration immédiate des cookies (Max-Age=0)
@app.post("/api/auth/cookie-logout")
async def deconnexion_cookies(response: Response):
    response.delete_cookie("isgp_session", path="/")
    response.delete_cookie("isgp_auth_token", path="/")
    response.delete_cookie("isgp_theme", path="/")
    return {"statut": "Déconnecté — Cookies révoqués (Max-Age=0)"}


if __name__ == "__main__":
    client = TestClient(app)
    print("=== 1. CONNEXION (POST /api/auth/cookie-login) -> EN-TÊTES Set-Cookie ===")
    r_login = client.post("/api/auth/cookie-login", json={"identifiant": "yasmine.merabet", "theme": "sombre"})
    for sc in r_login.headers.get_list("set-cookie"):
        print("  Set-Cookie :", sc)

    print("\n=== 2. REQUÊTE AUTHENTIFIÉE AUTOMATIQUEMENT PAR COOKIES (GET /api/auth/cookie-inspect) ===")
    r_insp = client.get("/api/auth/cookie-inspect")
    print("  Statut :", r_insp.status_code, "| JSON :", r_insp.json())

    print("\n=== 3. DÉCONNEXION ET RÉVOCATION (POST /api/auth/cookie-logout) ===")
    client.post("/api/auth/cookie-logout")
    print("  Après logout -> GET /api/auth/cookie-inspect :", client.get("/api/auth/cookie-inspect").status_code)
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
