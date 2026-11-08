import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_2_DATA = {
    "day_number": 2,
    "folder": "day_2",
    "badge": "Jour 2 • Design RESTful & Flask",
    "title": "Conception RESTful (Modèle de Richardson, Versioning), Pagination, Tri, Filtrage & Middlewares Flask",
    "goal": "Concevoir des URI conformes aux standards RESTful, maîtriser le cycle WSGI de Flask, implémenter la pagination, le filtrage multi-critères et le tri dynamique sur une collection, et mettre en place des middlewares d'audit (@app.before_request / @app.after_request).",
    "starter_filename": "day_2/03_pagination_filtrage_tri.py",
    "files": [
        "day_2/01_serveur_minimal_flask.py",
        "day_2/02_routes_et_parametres.py",
        "day_2/03_pagination_filtrage_tri.py",
        "day_2/04_middlewares_et_audit_log.py",
    ],
    "lessons": [
        {
            "id": "d2-l1",
            "file": "day_2/01_serveur_minimal_flask.py",
            "title": "2.1 — Règles d'Or du Design d'API RESTful (Modèle de Maturité de Richardson, Nommage & Versioning `/api/v1`)",
            "duration": "55 min",
            "analogy": {
                "title": "Organiser les rayons d'une bibliothèque par noms de collections plutôt que par phrases d'action",
                "text": "Une erreur fréquente chez les débutants consiste à nommer les URLs comme des fonctions : `/getAllFormations`, `/createNewFormation`, `/deleteFormationById?id=4`. Dans une architecture **RESTful**, l'URL désigne **exclusivement la Ressource (un nom au pluriel : `/api/v1/formations`)**, et c'est la **Méthode HTTP (`GET`, `POST`, `PUT`, `DELETE`)** qui indique l'action !"
            },
            "explanation": [
                "**1. Le Modèle de Maturité de Richardson (Les 4 niveaux d'une API REST)** :\n  - **Niveau 0 (Le marécage du POX / RPC)** : Une seule URL (`POST /api`) à laquelle on envoie des commandes diverses.\n  - **Niveau 1 (Les Ressources)** : Chaque entité métier possède sa propre URI (`/api/formations`, `/api/formations/12`, `/api/stagiaires`).\n  - **Niveau 2 (Les Verbes & Codes HTTP)** : Utilisation rigoureuse de `GET`, `POST`, `PUT`, `PATCH`, `DELETE` et des codes de statut (`200`, `201`, `400`, `401`, `404`, `429`). C'est le standard industriel visé.\n  - **Niveau 3 (HATEOAS)** : La réponse JSON inclut des liens (`links`) vers les actions suivantes possibles.",
                "**2. Les 5 conventions de nommage d'URI en entreprise** :\n  1. **Toujours des noms au pluriel en minuscules** : `/api/v1/formations` (jamais `/api/Formation` ni `/api/get_formations`).\n  2. **Séparer les mots composés par un tiret `-` (kebab-case)** : `/api/v1/sessions-formation`.\n  3. **Hiérarchie pour les sous-ressources** : `/api/v1/formations/12/stagiaires` (les stagiaires inscrits à la formation n°12).\n  4. **Versioning explicite (`/api/v1/...`)** : Permet de faire évoluer l'API vers `/api/v2/...` dans le futur sans casser les applications clientes existantes.\n  5. **Cycle WSGI dans Flask** : `app = Flask(__name__)` crée une application conforme au standard Python **WSGI (Web Server Gateway Interface)** qui traduit chaque requête HTTP en appel de fonction Python."
            ],
            "code": _read("01_serveur_minimal_flask.py"),
            "line_explanations": [
                {"lines": "5", "text": "Importation du constructeur `Flask` et du sérialiseur JSON `jsonify`."},
                {"lines": "7", "text": "Création de l'instance WSGI Flask."},
                {"lines": "9-15", "text": "Déclaration explicite de la route `/api/bonjour` restreinte à la méthode `GET`, retournant un objet JSON et le code `200`."},
                {"lines": "17-18", "text": "Lancement du serveur de développement local sur `0.0.0.0:5001`."}
            ],
            "sandbox_preset": {
                "label": "Tester la route GET /api/sandbox/bonjour",
                "method": "GET",
                "url": "/api/sandbox/bonjour",
                "body": ""
            },
            "vscode_instructions": {
                "filename": "day_2/01_serveur_minimal_flask.py",
                "steps": [
                    "Ouvrir `day_2/01_serveur_minimal_flask.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_2/01_serveur_minimal_flask.py`."
                ]
            }
        },
        {
            "id": "d2-l2",
            "file": "day_2/02_routes_et_parametres.py",
            "title": "2.2 — Routage Dynamique, Convertisseurs de Types (`<int:id>`) & Objet Contextuel `request`",
            "duration": "55 min",
            "analogy": {
                "title": "Le contrôleur de guichet qui filtre automatiquement le format du numéro de dossier",
                "text": "Si un guichet attend un numéro de dossier entier (`/api/formations/42`) et qu'un visiteur demande `/api/formations/bonjour`, le routeur de Flask rejette automatiquement la demande en `404` grâce au convertisseur de type `<int:id>`, avant même d'exécuter votre fonction Python."
            },
            "explanation": [
                "**1. Les convertisseurs de route intégrés à Flask** :\n  - `<nom>` ou `<string:nom>` : Capture toute chaîne de caractères (sans slash `/`).\n  - `<int:id>` : Capture uniquement un entier positif et le convertit directement en `int` Python.\n  - `<float:montant>` : Capture un nombre décimal.\n  - `<uuid:jeton_id>` : Capture uniquement un identifiant UUID valide.",
                "**2. Anatomie complète de l'objet `request` dans Flask** :\n  - `request.method` : `'GET'`, `'POST'`, `'PUT'`, `'DELETE'`.\n  - `request.path` : Le chemin appelé (ex. `'/api/calcul-tva'`).\n  - `request.args` : Dictionnaire des paramètres de requête après `?` (`request.args.get('ht', 1000)`).\n  - `request.headers` : Dictionnaire insensible à la casse des en-têtes HTTP (`request.headers.get('Authorization')`).\n  - `request.remote_addr` : Adresse IP du client appelant.\n  - `request.get_json(silent=True)` : Charge utile JSON désérialisée."
            ],
            "code": _read("02_routes_et_parametres.py"),
            "line_explanations": [
                {"lines": "12-17", "text": "Capture du paramètre de chemin `<prenom>` injecté directement comme argument de `saluer_stagiaire(prenom)`."},
                {"lines": "20-29", "text": "Extraction des paramètres de requête `?ht=...&taux=...` via `request.args.get()` avec valeurs par défaut."}
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
                    "Exécuter `.venv/bin/python day_2/02_routes_et_parametres.py`."
                ]
            }
        },
        {
            "id": "d2-l3",
            "file": "day_2/03_pagination_filtrage_tri.py",
            "title": "2.3 — Pagination (`page`, `limit`), Filtrage Multi-Critères & Tri Dynamique sur une Collection",
            "duration": "65 min",
            "analogy": {
                "title": "Ne jamais envoyer l'annuaire téléphonique entier quand le client cherche une seule page",
                "text": "Imaginez une table contenant 250 000 factures ou formations. Si `GET /api/v1/formations` renvoie les 250 000 lignes en un seul bloc JSON de 80 Mo, la mémoire du serveur explose et l'application mobile du client gèle. En production, **toute route retournant une collection doit impérativement implémenter la Pagination, le Filtrage et le Tri**."
            },
            "explanation": [
                "**1. Algorithme de Pagination par `page` et `limit` (Offset / Limit)** :\n  - Le client demande `?page=2&limit=10` (page n°2, à raison de 10 éléments par page).\n  - On borne toujours `limit` côté serveur (`limit = min(50, max(1, limit))`) pour empêcher un client malveillant de demander `?limit=9999999` !\n  - L'indice de départ (`offset`) vaut `debut = (page - 1) * limit` et l'indice de fin vaut `fin = debut + limit`.\n  - En Python, le découpage de liste `resultats[debut:fin]` (ou en SQL `LIMIT ? OFFSET ?`) extrait exactement la page demandée.",
                "**2. Enveloppe de métadonnées de pagination (`meta`)** : Pour que l'interface cliente puisse afficher les boutons *« Page précédente / Page 2 sur 5 / Page suivante »*, l'API renvoie systématiquement `total_elements`, `total_pages`, `page_actuelle` et `a_page_suivante`.",
                "**3. Sécurisation du Tri Dynamique (`?tri=duree_jours&ordre=desc`)** : On valide toujours que le champ demandé figure dans une **liste blanche (whitelist)** autorisée (`('id', 'duree_jours', 'titre')`) avant de trier."
            ],
            "code": _read("03_pagination_filtrage_tri.py"),
            "line_explanations": [
                {"lines": "22-29", "text": "Étape 1 (Filtrage) : Sélectionne uniquement les enregistrements respectant `min_jours` et `salle`."},
                {"lines": "32-36", "text": "Étape 2 (Tri) : Vérifie que `champ_tri` est autorisé, puis trie par ordre croissant (`asc`) ou décroissant (`desc`)."},
                {"lines": "39-45", "text": "Étape 3 (Pagination) : Calcule `total_pages` avec `math.ceil()`, puis découpe la tranche `resultats[debut:fin]`."},
                {"lines": "47-57", "text": "Retourne l'enveloppe normalisée contenant les compteurs de pagination dans `meta` et les enregistrements dans `data`."}
            ],
            "sandbox_preset": {
                "label": "Tester la Pagination & le Tri : GET /api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc",
                "method": "GET",
                "url": "/api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc",
                "body": ""
            },
            "python_runner": {
                "prompt": "Testez l'algorithme complet de filtrage, tri et pagination sur un catalogue en Python :",
                "initial_code": '''import math

catalogue = [
    {"id": i, "titre": f"Module API #{i}", "jours": (i % 5) + 1}
    for i in range(1, 15)  # 14 formations au total
]

page = 2
limit = 4
total = len(catalogue)
total_pages = math.ceil(total / limit)
debut = (page - 1) * limit
tranche = catalogue[debut : debut + limit]

print(f"Page {page}/{total_pages} (Total: {total} éléments) :")
for item in tranche:
    print(" -", item)'''
            },
            "vscode_instructions": {
                "filename": "day_2/03_pagination_filtrage_tri.py",
                "steps": [
                    "Ouvrir `day_2/03_pagination_filtrage_tri.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_2/03_pagination_filtrage_tri.py` et tester différentes combinaisons de `?page=`, `?limit=`, `?salle=` et `?tri=`."
                ]
            }
        },
        {
            "id": "d2-l4",
            "file": "day_2/04_middlewares_et_audit_log.py",
            "title": "2.4 — Middlewares Flask (`@app.before_request`, `@app.after_request`), `X-Request-ID` & Journalisation d'Audit",
            "duration": "50 min",
            "analogy": {
                "title": "Le portique d'entrée et de sortie qui horodate chaque passage dans l'immeuble",
                "text": "Au lieu de copier-coller du code de chronométrage, de traçabilité et d'en-têtes de sécurité dans chacune de vos 50 fonctions de routes, un **Middleware** s'exécute automatiquement en amont (`@app.before_request`) et en aval (`@app.after_request`) de **toutes** les requêtes du serveur."
            },
            "explanation": [
                "**1. Le contexte global de requête `g` dans Flask** : `from flask import g` fournit un objet temporaire propre à la requête en cours. Ce qu'on stocke dans `g.heure_debut` ou `g.request_id` dans `@app.before_request` est accessible dans la route et dans `@app.after_request`, puis détruit à la fin de la requête.",
                "**2. L'en-tête de corrélation `X-Request-ID`** : En architecture distribuée, chaque requête reçoit un identifiant unique (`req-a1b2c3d4`). Si un client rencontre une erreur, il communique cet identifiant à l'équipe technique qui retrouve immédiatement la ligne exacte dans les journaux du serveur.",
                "**3. En-têtes de sécurité systématiques** : `X-Content-Type-Options: nosniff` interdit au navigateur de deviner le type MIME et force le respect strict de `application/json`."
            ],
            "code": _read("04_middlewares_et_audit_log.py"),
            "line_explanations": [
                {"lines": "11-15", "text": "`@app.before_request` démarre un chronomètre haute précision (`time.perf_counter()`) et génère un `X-Request-ID` unique dans `g`."},
                {"lines": "18-29", "text": "`@app.after_request` calcule la durée d'exécution en millisecondes, injecte `X-Request-ID` et `X-Response-Time-Ms` dans les Headers HTTP, et écrit une trace d'audit."}
            ],
            "vscode_instructions": {
                "filename": "day_2/04_middlewares_et_audit_log.py",
                "steps": [
                    "Ouvrir `day_2/04_middlewares_et_audit_log.py`.",
                    "Exécuter `.venv/bin/python day_2/04_middlewares_et_audit_log.py` et observer les lignes `[AUDIT]` dans le terminal à chaque requête."
                ]
            }
        }
    ]
}
