import os

BASE_DIR = os.path.dirname(__file__)


def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()


DAY_2_DATA = {
    "day_number": 2,
    "folder": "day_2",
    "badge": "Jour 2 • Design RESTful, Flask, Templates Jinja2 & Formulaires Web",
    "title": "Prise en Main de Flask : Serveur WSGI, Templates Jinja2 (render_template), Formulaires HTML (request.form), Routage, Pagination & Middlewares",
    "goal": "Comprendre le cycle WSGI de Flask, séparer proprement la logique Python des pages HTML grâce au moteur de templates Jinja2 (render_template), traiter les formulaires HTML (request.form et request.files), maîtriser les paramètres de route (<variable> vs :variable vs {variable}), implémenter la pagination/filtrage/tri et mettre en place des middlewares d'audit.",
    "starter_filename": "day_2/05_jinja_et_formulaires_html.py",
    "files": [
        "day_2/01_serveur_minimal_flask.py",
        "day_2/02_routes_et_parametres.py",
        "day_2/05_jinja_et_formulaires_html.py",
        "day_2/03_pagination_filtrage_tri.py",
        "day_2/04_middlewares_et_audit_log.py",
    ],
    "lessons": [
        {
            "id": "d2-l1",
            "file": "day_2/01_serveur_minimal_flask.py",
            "title": "2.1 — Premiers Pas avec Flask : Serveur WSGI, Rendu de Templates Jinja2 (`render_template`) vs API REST (`jsonify`) & Modèle de Richardson",
            "duration": "55 min",
            "analogy": {
                "title": "Organiser les rayons d'une bibliothèque par noms de collections plutôt que par phrases d'action",
                "text": "Une erreur fréquente chez les débutants consiste à nommer les URLs comme des fonctions : `/getAllFormations`, `/createNewFormation`, `/deleteFormationById?id=4`, ou à coder du HTML en dur dans Python.\nDans Flask, les pages Web résident dans le dossier **`templates/`** et sont rendues via **`render_template('accueil.html', ...)`**, tandis que les routes d'API RESTful désignent **exclusivement la Ressource (un nom au pluriel : `/api/v1/modules`)** et renvoient du JSON via **`jsonify(...)`**."
            },
            "explanation": [
                "**1. Comment Flask sert à la fois des pages Web (`render_template`) et des APIs JSON (`jsonify`)** :\n  - **Pour une page Web destinée à un navigateur** : On ne met jamais de balises HTML dans le fichier `.py`. On place le fichier HTML dans `day_2/templates/accueil.html` et on appelle `render_template('accueil.html', organisme='ISGP', modules=...)`.\n  - **Pour un endpoint d'API REST** : On appelle `jsonify({'message': '...', 'statut': 'actif'}), 200` qui sérialise le dictionnaire Python en JSON UTF-8 avec l'en-tête `Content-Type: application/json`.",
                "**2. Le Modèle de Maturité de Richardson (Les 4 niveaux d'une API REST)** :\n  - **Niveau 0 (Le marécage du POX / RPC)** : Une seule URL (`POST /api`) à laquelle on envoie des commandes diverses.\n  - **Niveau 1 (Les Ressources)** : Chaque entité métier possède sa propre URI (`/api/formations`, `/api/formations/12`, `/api/stagiaires`).\n  - **Niveau 2 (Les Verbes & Codes HTTP)** : Utilisation rigoureuse de `GET`, `POST`, `PUT`, `PATCH`, `DELETE` et des codes de statut (`200`, `201`, `400`, `401`, `404`, `429`). C'est le standard industriel visé.\n  - **Niveau 3 (HATEOAS)** : La réponse JSON inclut des liens (`links`) vers les actions suivantes possibles.",
                "**3. Les 5 conventions de nommage d'URI en entreprise** :\n  1. **Toujours des noms au pluriel en minuscules** : `/api/v1/formations` (jamais `/api/Formation` ni `/api/get_formations`).\n  2. **Séparer les mots composés par un tiret `-` (kebab-case)** : `/api/v1/sessions-formation`.\n  3. **Hiérarchie pour les sous-ressources** : `/api/v1/formations/12/stagiaires`.\n  4. **Versioning explicite (`/api/v1/...`)** : Permet de faire évoluer l'API vers `/api/v2/...` sans casser les clients existants.\n  5. **Cycle WSGI dans Flask** : `app = Flask(__name__)` crée une application conforme au standard Python **WSGI (Web Server Gateway Interface)**."
            ],
            "code": _read("01_serveur_minimal_flask.py"),
            "line_explanations": [
                {"lines": "11-12", "text": "Création de l'instance WSGI Flask pointant vers le sous-dossier `day_2/templates/`."},
                {"lines": "24-32", "text": "Route Web `/accueil` : appelle `render_template('accueil.html', ...)` pour injecter les variables Python dans le gabarit HTML Jinja2 (zéro HTML codé en dur)."},
                {"lines": "36-43", "text": "Route API `/api/bonjour` : retourne un dictionnaire converti en JSON par `jsonify()` avec le code HTTP `200`."},
                {"lines": "47-52", "text": "Route RESTful de collection `/api/v1/modules` (nom au pluriel + version `/api/v1`)."},
                {"lines": "55-68", "text": "Exécution immédiate comparant la sortie HTML Jinja2 (`/accueil`) et la sortie API JSON (`/api/bonjour`)."}
            ],
            "sandbox_preset": {
                "label": "Tester la route GET /api/sandbox/bonjour",
                "method": "GET",
                "url": "/api/sandbox/bonjour",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_2/01_serveur_minimal_flask.py` pour observer le rendu du template Jinja2 (`day_2/templates/accueil.html`) et la réponse JSON (`/api/bonjour`) :",
                "initial_code": _read("01_serveur_minimal_flask.py")
            },
            "vscode_instructions": {
                "filename": "day_2/01_serveur_minimal_flask.py",
                "steps": [
                    "Inspecter `day_2/01_serveur_minimal_flask.py` et son template HTML `day_2/templates/accueil.html`.",
                    "Exécuter `.venv/bin/python day_2/01_serveur_minimal_flask.py` (ou ajouter `--serve` pour démarrer sur le port 5001)."
                ]
            }
        },
        {
            "id": "d2-l2",
            "file": "day_2/02_routes_et_parametres.py",
            "title": "2.2 — Routage Dynamique (`<variable>` vs `:variable` vs `{variable}`), Convertisseurs `<int:id>` & Objet `request`",
            "duration": "55 min",
            "analogy": {
                "title": "Le contrôleur de guichet qui filtre automatiquement le format du numéro de dossier",
                "text": "Si un guichet attend un numéro de dossier entier (`/api/v1/stagiaires/1`) et qu'un visiteur demande `/api/v1/stagiaires/bonjour`, le routeur de Flask rejette automatiquement la demande en `404` grâce au convertisseur de type `<int:stagiaire_id>`, avant même d'exécuter votre fonction Python."
            },
            "explanation": [
                "**1. Les convertisseurs de route intégrés à Flask (`<convertisseur:variable>`)** :\n  - `<nom>` ou `<string:nom>` : Capture toute chaîne de caractères (sans slash `/`).\n  - `<int:id>` : Capture uniquement un entier positif et le convertit directement en `int` Python.\n  - `<float:montant>` : Capture un nombre décimal.\n  - `<uuid:jeton_id>` : Capture uniquement un identifiant UUID valide.",
                "**2. Distinction cruciale : `<variable>` (Flask) vs `:variable` (Postman / Express.js) vs `{variable}` (OpenAPI / FastAPI)** :\n  - **`<variable>` ou `<int:id>`** : Syntaxe officielle de **Flask / Werkzeug** et **Django** côté serveur Python (`@app.route('/api/v1/stagiaires/<int:stagiaire_id>')`).\n  - **`:variable` (ex. `:id`)** : Syntaxe utilisée dans **Postman** (onglet *Path Variables*), **Express.js (Node.js)**, **Ruby on Rails** ou **Gin (Go)** (`/api/v1/stagiaires/:id`). **Attention** : écrire `:id` dans une route Flask ne crée PAS de variable (Flask cherche alors le texte littéral `':id'`) !\n  - **`{variable}` (ex. `{id}`)** : Syntaxe standard **OpenAPI 3.0 / Swagger**, **FastAPI** et des **f-strings Python** (`/api/v1/stagiaires/{id}`).\n  - **Dans `curl` ou le navigateur** : On n'écrit jamais de variable générique, on envoie toujours la **valeur réelle** (`/api/v1/stagiaires/1`).",
                "**3. Anatomie complète de l'objet `request` dans Flask** :\n  - `request.method` : `'GET'`, `'POST'`, `'PUT'`, `'DELETE'`.\n  - `request.path` : Le chemin appelé (ex. `'/api/calcul-tva'`).\n  - `request.args` : Dictionnaire des paramètres de requête après `?` (`request.args.get('ht', default=1000.0, type=float)`).\n  - `request.form` : Dictionnaire des champs d'un formulaire HTML `<form method='POST'>`.\n  - `request.headers` : Dictionnaire insensible à la casse des en-têtes HTTP.\n  - `request.get_json(silent=True)` : Charge utile JSON désérialisée."
            ],
            "code": _read("02_routes_et_parametres.py"),
            "line_explanations": [
                {"lines": "23-32", "text": "Paramètre de chemin `<prenom>` : Flask injecte la valeur capturée comme argument de `saluer_stagiaire(prenom)`."},
                {"lines": "36-41", "text": "Convertisseur typé `<int:stagiaire_id>` retournant la ressource en JSON (`/api/v1/stagiaires/1`)."},
                {"lines": "45-50", "text": "Même paramètre `<int:stagiaire_id>` utilisé pour rendre la fiche HTML Jinja2 `day_2/templates/fiche_stagiaire.html` via `render_template()`."},
                {"lines": "54-64", "text": "Extraction typée des paramètres de requête `?ht=...&taux=...` via `request.args.get(..., type=float)`."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/calcul-tva?ht=2500&taux=19",
                "method": "GET",
                "url": "/api/sandbox/calcul-tva?ht=2500&taux=19",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_2/02_routes_et_parametres.py` pour tester `<prenom>`, `<int:stagiaire_id>` (Jinja2 + JSON) et `request.args` :",
                "initial_code": _read("02_routes_et_parametres.py")
            },
            "vscode_instructions": {
                "filename": "day_2/02_routes_et_parametres.py",
                "steps": [
                    "Ouvrir `day_2/02_routes_et_parametres.py` et son template `day_2/templates/fiche_stagiaire.html`.",
                    "Exécuter `.venv/bin/python day_2/02_routes_et_parametres.py`."
                ]
            }
        },
        {
            "id": "d2-l5",
            "file": "day_2/05_jinja_et_formulaires_html.py",
            "title": "2.3 — Moteur de Templates Jinja2 (`render_template`) & Traitement des Formulaires Web HTML (`request.form` / `request.files`)",
            "duration": "65 min",
            "analogy": {
                "title": "Séparer le moule d'imprimerie (Template Jinja2 .html) des données de l'ordinateur (Python) et du bordereau papier rempli par l'usager (<form>)",
                "text": "Écrire des chaînes HTML directement dans un fichier Python (`return '<h1>' + titre + '</h1>'`) est une mauvaise pratique majeure : le code devient illisible et vulnérable aux failles d'injection JavaScript (**XSS**).\nDans Flask, les pages Web résident dans le dossier **`templates/`** et utilisent le moteur **Jinja2** (`render_template('formations.html', ...)`). Et lorsqu'un utilisateur soumet un formulaire HTML `<form method='POST'>`, le navigateur n'envoie **pas** du JSON, mais des données de formulaire que Flask lit dans **`request.form`** (et **`request.files`** pour les pièces jointes) !"
            },
            "explanation": [
                "**1. Pourquoi il ne faut jamais coder du HTML en dur dans Python : Le Moteur `Jinja2` (`render_template`)** :\n  - Flask intègre nativement **Jinja2**, qui charge les fichiers `.html` du dossier `templates/` et remplace dynamiquement trois types de balises :\n    1. **`{{ variable }}`** : Affiche la valeur d'une variable Python en **échappant automatiquement** les caractères `<`, `>`, `&` pour bloquer toute attaque **XSS (*Cross-Site Scripting*)**.\n    2. **`{% for elem in liste %} ... {% endfor %}`** : Répète un bloc HTML (ex: générer une ligne `<tr>` par formation).\n    3. **`{% if condition %} ... {% endif %}`** : Affiche un bloc d'alerte ou d'erreur uniquement si la condition est vraie.\n    4. **`{# commentaire #}`** : Commentaire Jinja2 invisible dans le code source HTML envoyé au navigateur.",
                "**2. Comment un Formulaire HTML (`<form method='POST'>`) envoie ses données à Flask (`request.form` vs `request.get_json()`)** :\n  - Lorsqu'un utilisateur clique sur le bouton `<button type='submit'>` d'un formulaire HTML `<form method='POST' action='/formations'>`, le navigateur regroupe tous les champs possédant un attribut **`name='...'`** (`<input name='titre'>`, `<select name='salle'>`) et les envoie avec l'en-tête **`Content-Type: application/x-www-form-urlencoded`** (sous la forme `titre=API+Flask&duree_jours=5&salle=Salle+A`).\n  - **Piège critique** : Sur une soumission de formulaire HTML classique, **`request.get_json()` renvoie `None`** ! Il faut impérativement lire les champs dans **`request.form.get('titre')`** et **`request.form.get('duree_jours', type=int)`**.",
                "**3. Upload de Fichiers (`<input type='file'>`) avec `enctype='multipart/form-data'` et `request.files`** :\n  - Si le formulaire comporte un champ fichier (PDF, image, Excel), la balise `<form>` doit déclarer `enctype='multipart/form-data'`.\n  - Côté Flask, les champs texte restent dans `request.form`, tandis que le fichier binaire est récupéré dans **`request.files.get('document_pdf')`** et son nom doit toujours être nettoyé avec **`werkzeug.utils.secure_filename()`**."
            ],
            "code": _read("05_jinja_et_formulaires_html.py"),
            "line_explanations": [
                {"lines": "17-18", "text": "Configuration explicite du dossier `day_2/templates/` contenant le gabarit Jinja2 `formations.html`."},
                {"lines": "39-44", "text": "Détection intelligente du format d'entrée : `request.form` si l'appel provient d'un formulaire HTML (`application/x-www-form-urlencoded`), ou `request.get_json()` s'il provient d'un client API JSON."},
                {"lines": "45-57", "text": "Extraction et validation serveur des champs `titre`, `duree_jours` et `salle` soumis par le formulaire."},
                {"lines": "77-83", "text": "`render_template('formations.html', ...)` injecte les variables Python dans le template Jinja2 sans aucune chaîne HTML codée en dur dans Python."},
                {"lines": "89-109", "text": "Traitement d'un formulaire `multipart/form-data` combinant `request.form` (texte) et `request.files` (fichier PDF) sécurisé par `secure_filename()`."}
            ],
            "sandbox_preset": {
                "label": "Tester POST /api/sandbox/formulaire-formation (request.form)",
                "method": "POST",
                "url": "/api/sandbox/formulaire-formation",
                "body": "titre=Atelier+Jinja2&formateur=ISGP&duree_jours=4&salle=Salle+B"
            },
            "python_runner": {
                "prompt": "Exécutez le test complet de soumission de formulaire HTML (`request.form` + rendu Jinja2 `day_2/templates/formations.html`) et d'upload `multipart/form-data` (`request.files`) :",
                "initial_code": _read("05_jinja_et_formulaires_html.py")
            },
            "vscode_instructions": {
                "filename": "day_2/05_jinja_et_formulaires_html.py",
                "steps": [
                    "Inspecter le fichier de template Jinja2 `day_2/templates/formations.html` et le script `day_2/05_jinja_et_formulaires_html.py`.",
                    "Ouvrir l'atelier interactif réel dans votre navigateur sur `http://127.0.0.1:5000/sandbox/formulaire-jinja` pour soumettre de vraies formations via `<form method='POST'>`."
                ]
            }
        },
        {
            "id": "d2-l3",
            "file": "day_2/03_pagination_filtrage_tri.py",
            "title": "2.4 — Pagination (`page`, `limit`), Filtrage Multi-Critères & Tri Dynamique sur une Collection",
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
            "title": "2.5 — Middlewares Flask (`@app.before_request`, `@app.after_request`), `X-Request-ID` & Journalisation d'Audit",
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
