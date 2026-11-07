import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_5_DATA = {
    "day_number": 5,
    "folder": "day_5",
    "badge": "Jour 5 • Intégration & FastAPI",
    "title": "Consommation Cliente d'une API Sécurisée & Comparaison avec FastAPI",
    "goal": "Assembler l'ensemble des briques (CRUD SQLite, Authentification par Token, Rate Limiting, Consommation cliente Python/Web) et mettre en perspective Flask avec FastAPI.",
    "starter_filename": "day_5/01_client_python_auth.py",
    "files": [
        "day_5/01_client_python_auth.py",
        "day_5/02_comparaison_flask_fastapi.py",
    ],
    "lessons": [
        {
            "id": "d5-l1",
            "file": "day_5/01_client_python_auth.py",
            "title": "5.1 — Consommer une API Protégée depuis un Client Python ou JavaScript (`fetch`)",
            "duration": "50 min",
            "analogy": {
                "title": "Le client automatisé qui s'authentifie et présente son jeton",
                "text": "Un client d'API complet réalise deux opérations : il appelle d'abord `POST /api/auth/token` pour obtenir son `Bearer Token`, puis il inclut ce jeton dans l'en-tête `Authorization` de ses requêtes métier."
            },
            "explanation": [
                "**Depuis un script Python** : Utilisation de `urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})`.",
                "**Depuis une interface Web / PWA (JavaScript)** : Utilisation de `fetch(url, { headers: { 'Authorization': 'Bearer ' + token } })`."
            ],
            "code": _read("01_client_python_auth.py"),
            "line_explanations": [
                {"lines": "9-18", "text": "Première requête `POST` envoyant les identifiants JSON pour récupérer le jeton signé `access_token`."},
                {"lines": "21-26", "text": "Seconde requête `GET` incluant l'en-tête `Authorization: Bearer <mon_token>` pour accéder à la ressource protégée."}
            ],
            "python_runner": {
                "prompt": "Exécutez ce scénario complet en direct (`day_5/01_client_python_auth.py`) :",
                "initial_code": _read("01_client_python_auth.py")
            },
            "vscode_instructions": {
                "filename": "day_5/01_client_python_auth.py",
                "steps": [
                    "Ouvrir `day_5/01_client_python_auth.py` dans l'éditeur.",
                    "Exécuter `.venv/bin/python day_5/01_client_python_auth.py` pendant que le serveur principal tourne."
                ]
            }
        },
        {
            "id": "d5-l2",
            "file": "day_5/02_comparaison_flask_fastapi.py",
            "title": "5.2 — Mise en Perspective Architecturale : Flask vs FastAPI",
            "duration": "40 min",
            "analogy": {
                "title": "Contrôle explicite (Flask) vs Validation déclarative par typage (FastAPI)",
                "text": "Ayant maîtrisé l'intégralité des mécanismes HTTP, JSON, Headers, Tokens et Rate Limiting de manière explicite avec **Flask**, la lecture et l'utilisation de **FastAPI** deviennent immédiates."
            },
            "explanation": [
                "**En Flask** : Vous contrôlez explicitement l'extraction du JSON (`request.get_json()`), des en-têtes (`request.headers`) et la sérialisation (`jsonify()`).",
                "**En FastAPI** : La validation des schémas JSON s'appuie sur les annotations de types Python (`Pydantic`) et génère automatiquement une spécification OpenAPI interactive (`/docs`)."
            ],
            "code": _read("02_comparaison_flask_fastapi.py"),
            "line_explanations": [
                {"lines": "8-11", "text": "Dans Flask, l'extraction du corps de requête et le formatage de la réponse sont explicites."},
                {"lines": "20-26", "text": "Dans FastAPI, la classe `FormationSchema` valide automatiquement les types des champs entrants."}
            ],
            "vscode_instructions": {
                "filename": "day_5/02_comparaison_flask_fastapi.py",
                "steps": [
                    "Consulter `day_5/02_comparaison_flask_fastapi.py` pour comparer la syntaxe Flask et FastAPI."
                ]
            }
        }
    ]
}
