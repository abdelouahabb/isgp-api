# Fichier : day_1/05_outils_curl_postman_httpie.py
# Exécution : .venv/bin/python day_1/05_outils_curl_postman_httpie.py
# Objectif : Comprendre et exécuter de vraies commandes 'curl' pour inspecter :
#   1. Les requêtes GET avec Query Parameters (?page=1&limit=2)
#   2. Les en-têtes d'authentification (-H 'X-API-Key: ...')
#   3. L'envoi d'un Payload JSON (-H 'Content-Type: application/json' -d '{...}')
#   4. L'envoi d'un Formulaire HTML (-d 'cle=valeur' en application/x-www-form-urlencoded)

import subprocess

BASE_URL = "http://127.0.0.1:5000"


def executer_commande_curl(titre, arguments_curl):
    print("=" * 74)
    print(f"TEST : {titre}")
    print("COMMANDE : " + " ".join(arguments_curl))
    print("-" * 74)
    resultat = subprocess.run(
        arguments_curl, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5
    )
    lignes = [
        l for l in resultat.stdout.splitlines()
        if not l.startswith("X-Flask-Handler-Code:") and not l.startswith("X-Flask-Trace-Steps:")
    ]
    print("\n".join(lignes).strip())
    print()


# 1. Requête GET avec '-i' (inclut la Status Line et les Headers HTTP de réponse)
executer_commande_curl(
    "1. GET avec inspection des en-têtes (-i) et paramètres d'URL",
    ["curl", "-s", "-i", f"{BASE_URL}/api/sandbox/formations?page=1&limit=2"]
)

# 2. Requête Authentifiée par Clé API (-H 'X-API-Key: ...')
executer_commande_curl(
    "2. GET protégé par en-tête de sécurité (-H 'X-API-Key: isgp-secret-2026')",
    ["curl", "-s", "-i", "-H", "X-API-Key: isgp-secret-2026", f"{BASE_URL}/api/sandbox/admin-stats"]
)

# 3. Requête POST envoyant un Payload JSON (-X POST -H 'Content-Type: application/json' -d '{...}')
executer_commande_curl(
    "3. POST envoyant un corps JSON (lu par request.get_json() côté Flask)",
    [
        "curl", "-s", "-i",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", '{"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}',
        f"{BASE_URL}/api/sandbox/auth/token"
    ]
)

# 4. Requête POST envoyant des données de Formulaire HTML (-d 'cle=valeur' -> application/x-www-form-urlencoded)
executer_commande_curl(
    "4. POST simulant un Formulaire HTML <form> (lu par request.form côté Flask)",
    [
        "curl", "-s", "-i",
        "-X", "POST",
        "-d", "titre=Atelier+Curl+Formulaire&formateur=ISGP&duree_jours=3&salle=Salle+B",
        f"{BASE_URL}/api/sandbox/formulaire-formation"
    ]
)
