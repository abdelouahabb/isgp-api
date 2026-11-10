# Fichier : day_4/01_secrets_et_api_key.py
# Exécution : .venv/bin/python day_4/01_secrets_et_api_key.py
# Objectif : Protéger une route FastAPI par clé API (Header(alias="X-API-Key")) et comparaison
#            cryptographique en temps constant (hmac.compare_digest) via Depends().

import hmac
import os
import sys
from typing import Optional
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.testclient import TestClient

app = FastAPI(title="ISGP - Secrets & Authentification X-API-Key", version="1.0.0")

# 1. Lecture des secrets depuis les variables d'environnement du système
API_SECRET_KEY = os.environ.get("API_SECRET_KEY", "cle-signature-interne-isgp-2026")
PARTNER_API_KEY = os.environ.get("PARTNER_API_KEY", "isgp-secret-2026")


# 2. Dépendance d'authentification réutilisable (Depends)
async def verifier_cle_api(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> str:
    cle_recue = x_api_key or ""
    # 3. Comparaison en temps constant (protège contre les attaques temporelles / Timing Attacks)
    if not hmac.compare_digest(cle_recue, PARTNER_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Accès non autorisé (401). En-tête X-API-Key manquant ou invalide.",
        )
    return cle_recue


@app.get("/api/admin/statistiques")
async def stats_confidentielles(_cle: str = Depends(verifier_cle_api)):
    return {
        "acces": "Autorisé via X-API-Key (Depends + hmac.compare_digest)",
        "stagiaires_certifies": 148,
    }


if __name__ == "__main__":
    client = TestClient(app)
    print("1. Appel sans clé (401) :", client.get("/api/admin/statistiques").status_code, client.get("/api/admin/statistiques").json())
    r_ok = client.get("/api/admin/statistiques", headers={"X-API-Key": "isgp-secret-2026"})
    print("2. Appel avec X-API-Key (200) :", r_ok.status_code, r_ok.json())
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
