# Fichier : day_5/01_client_python_auth.py
# Exécution : .venv/bin/python day_5/01_client_python_auth.py
# Objectif : Construire un client HTTP Python résilient (Timeouts, gestion des codes 401/429 et Bearer Token)

import json
import time
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:5000"

def appeler_api_json(url, method="GET", headers=None, payload=None, timeout=5.0):
    """Client HTTP générique avec Timeout obligatoire et gestion structurée des erreurs HTTP."""
    entetes = {"Accept": "application/json"}
    if headers:
        entetes.update(headers)
    corps_octets = None
    if payload is not None:
        corps_octets = json.dumps(payload).encode("utf-8")
        entetes["Content-Type"] = "application/json"

    requete = urllib.request.Request(url, data=corps_octets, headers=entetes, method=method)
    try:
        with urllib.request.urlopen(requete, timeout=timeout) as reponse:
            return reponse.status, json.loads(reponse.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        corps_erreur = json.loads(err.read().decode("utf-8") or "{}")
        return err.code, corps_erreur

# 1. Authentification initiale pour obtenir le Bearer Token
statut_login, rep_login = appeler_api_json(
    f"{BASE_URL}/api/sandbox/auth/token",
    method="POST",
    payload={"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}
)
mon_token = rep_login["access_token"]
print(f"1. [HTTP {statut_login}] Jeton Bearer obtenu : {mon_token[:32]}...")

# 2. Appel de la route protégée en injectant l'en-tête Authorization
statut_profil, rep_profil = appeler_api_json(
    f"{BASE_URL}/api/sandbox/auth/profil",
    headers={"Authorization": f"Bearer {mon_token}"}
)
print(f"2. [HTTP {statut_profil}] Profil sécurisé reçu :")
print(json.dumps(rep_profil, indent=2, ensure_ascii=False))
