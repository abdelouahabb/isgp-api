import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_2_DATA = {
    "day_number": 2,
    "folder": "day_2",
    "badge": "Jour 2 • Premiers Services Flask",
    "title": "Implémentation d'un Serveur Web et Routage Dynamique avec Flask",
    "goal": "Configurer un environnement virtuel Python, instancier une application Flask, déclarer des routes HTTP, sérialiser les réponses avec jsonify() et extraire les paramètres d'URL.",
    "starter_filename": "day_2/02_routes_et_parametres.py",
    "files": [
        "day_2/01_serveur_minimal_flask.py",
        "day_2/02_routes_et_parametres.py",
    ],
    "lessons": [
        {
            "id": "d2-l1",
            "file": "day_2/01_serveur_minimal_flask.py",
            "title": "2.1 — Structure Minimale d'une Application Flask",
            "duration": "50 min",
            "analogy": {
                "title": "Standard téléphonique et table d'aiguillage",
                "text": "`app = Flask(__name__)` initialise le serveur HTTP. Chaque décorateur `@app.route('/...')` enregistre une règle d'aiguillage associant un chemin URL à une fonction Python dédiée."
            },
            "explanation": [
                "**Clarté architecturale de Flask** : Une API fonctionnelle s'écrit en quelques lignes explicites, permettant de maîtriser précisément le cycle de traitement d'une requête.",
                "**Sérialisation avec `jsonify()`** : Convertit automatiquement un dictionnaire ou une liste Python en réponse HTTP valide dotée de l'en-tête `Content-Type: application/json`."
            ],
            "code": _read("01_serveur_minimal_flask.py"),
            "line_explanations": [
                {"lines": "5", "text": "Importation de la classe `Flask` et de la fonction de sérialisation `jsonify`."},
                {"lines": "7", "text": "Instanciation de l'application serveur Flask dans la variable `app`."},
                {"lines": "9", "text": "Association de la route HTTP `GET /api/bonjour` à la fonction `dire_bonjour()`."},
                {"lines": "10-15", "text": "Retourne un dictionnaire converti en JSON accompagné du code de statut HTTP `200`."},
                {"lines": "17-18", "text": "Démarrage du serveur sur le port `5001` avec rechargement automatique (`debug=True`)."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/bonjour",
                "method": "GET",
                "url": "/api/sandbox/bonjour",
                "body": ""
            },
            "vscode_instructions": {
                "filename": "day_2/01_serveur_minimal_flask.py",
                "steps": [
                    "Ouvrir le fichier `day_2/01_serveur_minimal_flask.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_2/01_serveur_minimal_flask.py` dans le terminal.",
                    "Ouvrir `http://127.0.0.1:5001/api/bonjour` dans le navigateur."
                ]
            }
        },
        {
            "id": "d2-l2",
            "file": "day_2/02_routes_et_parametres.py",
            "title": "2.2 — Paramètres de Chemin (`<id>`) et Paramètres de Requête (`?ht=1000`)",
            "duration": "60 min",
            "analogy": {
                "title": "Identifiant de dossier vs Critères de filtrage",
                "text": "On distingue deux modes de transmission de paramètres dans une URL :\n1. **Paramètre de chemin (Path Parameter)** : `/api/stagiaires/42` désigne une ressource unique.\n2. **Paramètre de requête (Query Parameter)** : `/api/calcul-tva?ht=2000&taux=19` fournit des paramètres de calcul ou de filtre."
            },
            "explanation": [
                "**1. Capture dans le chemin (`<...>`)** : `@app.route('/api/saluer/<prenom>')` extrait le segment d'URL et l'injecte en paramètre de la fonction Python. Le préfixe `<int:id>` valide automatiquement qu'il s'agit d'un entier.",
                "**2. Lecture après `?` (`request.args`)** : `request.args.get('ht', 1000)` récupère la valeur du paramètre `ht` ou applique la valeur par défaut `1000` s'il est omis."
            ],
            "code": _read("02_routes_et_parametres.py"),
            "line_explanations": [
                {"lines": "12-13", "text": "Le segment dynamique `<prenom>` est transmis comme argument à `saluer_stagiaire(prenom)`."},
                {"lines": "22-23", "text": "`request.args.get('ht', 1000)` lit le paramètre d'URL `?ht=...` et le convertit en nombre flottant."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/calcul-tva?ht=2500&taux=19",
                "method": "GET",
                "url": "/api/sandbox/calcul-tva?ht=2500&taux=19",
                "body": ""
            },
            "vscode_instructions": {
                "filename": "day_2/02_routes_et_parametres.py",
                "steps": [
                    "Ouvrir `day_2/02_routes_et_parametres.py`.",
                    "Exécuter `.venv/bin/python day_2/02_routes_et_parametres.py`.",
                    "Tester `http://127.0.0.1:5001/api/saluer/Amine` et `http://127.0.0.1:5001/api/calcul-tva?ht=5000&taux=9`."
                ]
            }
        }
    ]
}
