# Fichier : day_5/01_client_python_auth.py
# Exécution : .venv/bin/python day_5/01_client_python_auth.py

import urllib.request
import json

BASE_URL = "http://127.0.0.1:5000"

# 1. Demander un Bearer Token sur POST /api/sandbox/auth/token
donnees_login = json.dumps({"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}).encode("utf-8")
req_login = urllib.request.Request(
    f"{BASE_URL}/api/sandbox/auth/token",
    data=donnees_login,
    headers={"Content-Type": "application/json"},
    method="POST"
)
reponse_token = json.loads(urllib.request.urlopen(req_login).read().decode("utf-8"))
mon_token = reponse_token["access_token"]
print("1. Jeton Bearer obtenu :", mon_token[:35] + "...")

# 2. Appeler la route protégée en présentant le Bearer Token dans Authorization
req_profil = urllib.request.Request(
    f"{BASE_URL}/api/sandbox/auth/profil",
    headers={"Authorization": f"Bearer {mon_token}"}
)
profil = json.loads(urllib.request.urlopen(req_profil).read().decode("utf-8"))
print("2. Profil sécurisé reçu :", json.dumps(profil, indent=2, ensure_ascii=False))
