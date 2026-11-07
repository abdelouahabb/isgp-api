import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_1_DATA = {
    "day_number": 1,
    "folder": "day_1",
    "badge": "Jour 1 • Architecture Web & HTTP",
    "title": "Architecture Client/Serveur, Protocole HTTP et Format JSON",
    "goal": "Comprendre les échanges réseau entre systèmes hétérogènes, l'anatomie d'une requête et d'une réponse HTTP (Méthodes, En-têtes, Corps, Codes d'état) et la sérialisation JSON.",
    "starter_filename": "day_1/02_serialisation_json.py",
    "files": [
        "day_1/01_html_vs_json.py",
        "day_1/02_serialisation_json.py",
    ],
    "lessons": [
        {
            "id": "d1-l1",
            "file": "day_1/01_html_vs_json.py",
            "title": "1.1 — Serveur Web HTML vs Service Web (API REST)",
            "duration": "45 min",
            "analogy": {
                "title": "Présentation visuelle vs Échange de données inter-applicatif",
                "text": "Un **site Web traditionnel** génère des pages **HTML** destinées à être affichées à un utilisateur humain. Une **API Web** expose des données brutes structurées en **JSON** destinées à être consommées par n'importe quel logiciel client (application mobile, interface Web, ERP ou service tiers)."
            },
            "explanation": [
                "**Découplage Client / Serveur** : Une API unique écrite en Python/Flask permet d'alimenter simultanément un portail Web, une application mobile Android/iOS et des partenaires externes sans dupliquer la logique métier.",
                "**Cycle Requête / Réponse HTTP** :\n  1. Le **Client** émet une **Requête HTTP** comprenant une méthode, une URL, des en-têtes (`Headers`) et éventuellement un corps (`Body`).\n  2. Le **Serveur** exécute le traitement correspondant.\n  3. Le **Serveur** retourne une **Réponse HTTP** comprenant un code de statut numérique, des en-têtes et la charge utile JSON."
            ],
            "code": _read("01_html_vs_json.py"),
            "line_explanations": [
                {"lines": "4-11", "text": "Le document HTML encapsule la donnée dans des balises de présentation visuelle."},
                {"lines": "14-19", "text": "La charge utile d'une API isole les attributs métiers sous forme de paires clé/valeur typées."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/meteo?ville=Alger",
                "method": "GET",
                "url": "/api/sandbox/meteo?ville=Alger",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez le fichier day_1/01_html_vs_json.py :",
                "initial_code": _read("01_html_vs_json.py")
            },
            "vscode_instructions": {
                "filename": "day_1/01_html_vs_json.py",
                "steps": [
                    "Ouvrir le fichier `day_1/01_html_vs_json.py` dans l'éditeur.",
                    "Exécuter `python day_1/01_html_vs_json.py` dans le terminal."
                ]
            }
        },
        {
            "id": "d1-l2",
            "file": "day_1/02_serialisation_json.py",
            "title": "1.2 — Anatomie d'une URL, Méthodes HTTP, Codes de Statut & Sérialisation JSON",
            "duration": "60 min",
            "analogy": {
                "title": "Adressage réseau, instruction normalisée et code d'acquittement",
                "text": "Dans `http://127.0.0.1:5000/api/stagiaires?ville=Alger` :\n- `http://` désigne le protocole.\n- `127.0.0.1` désigne l'adresse IP de l'hôte.\n- `:5000` désigne le port logique d'écoute du processus Python.\n- `/api/stagiaires` désigne la route (chemin de la ressource).\n- `?ville=Alger` constitue la chaîne de filtrage (Query String)."
            },
            "explanation": [
                "**Les 4 Méthodes HTTP fondamentales (CRUD)** :\n  - **`GET`** : Lecture / consultation d'une ou plusieurs ressources.\n  - **`POST`** : Création d'une nouvelle ressource (données transmises dans le Body JSON).\n  - **`PUT`** : Mise à jour d'une ressource existante identifiée par son ID.\n  - **`DELETE`** : Suppression d'une ressource identifiée par son ID.",
                "**Classification des Codes de Statut HTTP** :\n  - **`200 OK`** : Traitement exécuté avec succès.\n  - **`201 Created`** : Nouvelle ressource créée avec succès (suite à un `POST`).\n  - **`400 Bad Request`** : Requête invalide (champ obligatoire manquant ou JSON mal formé).\n  - **`401 Unauthorized`** : Authentification absente ou invalide (Token ou Clé API rejeté).\n  - **`403 Forbidden`** : Authentifié mais droits insuffisants.\n  - **`404 Not Found`** : Route ou identifiant inexistant.\n  - **`429 Too Many Requests`** : Quota de requêtes dépassé (**Rate Limiting**).\n  - **`500 Internal Server Error`** : Erreur non interceptée côté serveur Python."
            ],
            "code": _read("02_serialisation_json.py"),
            "line_explanations": [
                {"lines": "4", "text": "Importation du module standard `json` inclus dans Python."},
                {"lines": "7-14", "text": "Dictionnaire Python utilisant les mots-clés Python `True` et `None`."},
                {"lines": "17", "text": "`json.dumps(...)` convertit le dictionnaire Python en chaîne JSON (`true`, `null`)."},
                {"lines": "22", "text": "`json.loads(...)` effectue l'opération inverse : convertit une chaîne JSON en dictionnaire Python."}
            ],
            "sandbox_preset": {
                "label": "Tester les codes HTTP : GET /api/sandbox/status-demo/200",
                "method": "GET",
                "url": "/api/sandbox/status-demo/200",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez le fichier day_1/02_serialisation_json.py :",
                "initial_code": _read("02_serialisation_json.py")
            },
            "vscode_instructions": {
                "filename": "day_1/02_serialisation_json.py",
                "steps": [
                    "Ouvrir `day_1/02_serialisation_json.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `python day_1/02_serialisation_json.py`."
                ]
            }
        }
    ]
}
