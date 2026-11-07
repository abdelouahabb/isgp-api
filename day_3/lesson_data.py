import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_3_DATA = {
    "day_number": 3,
    "folder": "day_3",
    "badge": "Jour 3 • API CRUD & SQLite",
    "title": "Conception d'une API CRUD Complète (GET, POST, PUT, DELETE) avec SQLite",
    "goal": "Désérialiser le corps JSON des requêtes entrantes via request.get_json(), valider les données, gérer les erreurs HTTP (400, 404) et persister les enregistrements dans une base SQLite.",
    "starter_filename": "day_3/02_api_crud_sqlite.py",
    "files": [
        "day_3/01_api_crud_memoire.py",
        "day_3/02_api_crud_sqlite.py",
    ],
    "lessons": [
        {
            "id": "d3-l1",
            "file": "day_3/01_api_crud_memoire.py",
            "title": "3.1 — Lecture (`GET`), Création (`POST`) et Validation des Données Entrantes",
            "duration": "60 min",
            "analogy": {
                "title": "Contrôle de conformité d'un formulaire avant enregistrement",
                "text": "Lors d'une requête `POST`, le client transmet un objet JSON dans le corps de la requête (`Body`). Le serveur doit impérativement vérifier la présence et la validité des champs obligatoires avant d'insérer l'enregistrement et de retourner `201 Created`."
            },
            "explanation": [
                "**Lecture du JSON entrant** : `corps = request.get_json(silent=True)` extrait et convertit le corps JSON en dictionnaire Python.",
                "**Validation défensive** : Si le JSON est absent ou qu'un attribut requis (`\"titre\"`) manque, l'API interrompt le traitement et renvoie un statut **`400 Bad Request`** explicite."
            ],
            "code": _read("01_api_crud_memoire.py"),
            "line_explanations": [
                {"lines": "13", "text": "`methods=[\"GET\"]` restreint cette fonction à la consultation de la collection."},
                {"lines": "17-21", "text": "Récupération du corps JSON sur `POST` et rejet immédiat avec code `400` si `\"titre\"` est absent."},
                {"lines": "23-31", "text": "Attribution d'un identifiant incrémental, ajout à la collection et retour du statut `201 Created`."}
            ],
            "sandbox_preset": {
                "label": "Tester POST /api/sandbox/formations",
                "method": "POST",
                "url": "/api/sandbox/formations",
                "body": '{\n  "titre": "Sécurité des Services Web & Tokens",\n  "formateur": "Intervenant ISGP",\n  "duree_jours": 4,\n  "salle": "Laboratoire 2"\n}'
            },
            "vscode_instructions": {
                "filename": "day_3/01_api_crud_memoire.py",
                "steps": [
                    "Ouvrir le fichier `day_3/01_api_crud_memoire.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_3/01_api_crud_memoire.py`."
                ]
            }
        },
        {
            "id": "d3-l2",
            "file": "day_3/02_api_crud_sqlite.py",
            "title": "3.2 — Opérations par Identifiant (`PUT`, `DELETE`) & Persistance SQLite",
            "duration": "60 min",
            "analogy": {
                "title": "Mémoire vive volatile (RAM) vs Stockage permanent sur disque (SQLite)",
                "text": "Une liste Python en mémoire vive est réinitialisée à chaque redémarrage du serveur. Le moteur **SQLite** (`import sqlite3`, inclus nativement dans Python) stocke les tables de manière durable dans un fichier `.db` sur le disque tout en protégeant contre les injections SQL grâce aux requêtes paramétrées `?`."
            },
            "explanation": [
                "**Gestion du code `404 Not Found`** : Lorsqu'un client cible `/api/formations/999`, si la requête SQL `SELECT * FROM formations WHERE id = ?` ne renvoie aucune ligne, l'API retourne obligatoirement le statut `404`.",
                "**Sécurité SQL (Requêtes paramétrées)** : Utilisez toujours des points d'interrogation `?` dans vos requêtes SQLite (`conn.execute('SELECT * FROM formations WHERE id = ?', (id,))`) pour empêcher toute injection SQL."
            ],
            "code": _read("02_api_crud_sqlite.py"),
            "line_explanations": [
                {"lines": "10-21", "text": "Création de la table `formations` dans le fichier SQLite `day_3_formations.db` si elle n'existe pas encore."},
                {"lines": "37-40", "text": "Recherche sécurisée par paramètre `?`. Si l'enregistrement n'existe pas, retour immédiat `404`."},
                {"lines": "42-46", "text": "Mise à jour `UPDATE` suivie de `conn.commit()` pour sauvegarder sur disque."}
            ],
            "sandbox_preset": {
                "label": "Tester PUT /api/sandbox/formations/1",
                "method": "PUT",
                "url": "/api/sandbox/formations/1",
                "body": '{\n  "titre": "Architecture des APIs REST (Niveau Avancé)",\n  "salle": "Amphithéâtre ISGP"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez ce cycle complet SQLite (CREATE, INSERT paramétré, SELECT) directement :",
                "initial_code": '''import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row
conn.execute("CREATE TABLE formations (id INTEGER PRIMARY KEY, titre TEXT, salle TEXT)")

# Insertion sécurisée avec paramètres ?
conn.execute("INSERT INTO formations (titre, salle) VALUES (?, ?)", ("API Flask & Sécurité", "Salle 101"))
conn.execute("INSERT INTO formations (titre, salle) VALUES (?, ?)", ("Tokens & Rate Limiting", "Salle 202"))
conn.commit()

lignes = conn.execute("SELECT * FROM formations").fetchall()
print("Enregistrements SQLite :", [dict(r) for r in lignes])'''
            },
            "vscode_instructions": {
                "filename": "day_3/02_api_crud_sqlite.py",
                "steps": [
                    "Ouvrir `day_3/02_api_crud_sqlite.py` dans l'éditeur.",
                    "Exécuter `.venv/bin/python day_3/02_api_crud_sqlite.py`."
                ]
            }
        }
    ]
}
