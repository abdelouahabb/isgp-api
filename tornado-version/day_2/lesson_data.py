import os

BASE_DIR = os.path.dirname(__file__)


def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()


DAY_2_DATA = {
    "day_number": 2,
    "folder": "day_2",
    "badge": "Jour 2 • Design RESTful, Tornado IOLoop, RequestHandler & Formulaires Web",
    "title": "Prise en Main de Tornado : Event-Loop IOLoop, Classes RequestHandler, Templates (self.render), Formulaires (self.get_body_argument), Routage Regex, Pagination & Cycle prepare/on_finish",
    "goal": "Comprendre l'architecture événementielle non-bloquante de Tornado (IOLoop + HTTPServer), structurer ses routes en classes RequestHandler orientées objet, séparer la logique Python des pages HTML via tornado.template (self.render), traiter les formulaires HTML (self.get_body_argument et self.request.files), maîtriser le routage par expressions régulières, implémenter la pagination/filtrage/tri et mettre en place des hooks d'audit (prepare / on_finish).",
    "starter_filename": "day_2/05_jinja_et_formulaires_html.py",
    "files": [
        "day_2/01_serveur_minimal_tornado.py",
        "day_2/02_routes_et_parametres.py",
        "day_2/05_jinja_et_formulaires_html.py",
        "day_2/03_pagination_filtrage_tri.py",
        "day_2/04_middlewares_et_audit_log.py",
    ],
    "lessons": [
        {
            "id": "d2-l1",
            "file": "day_2/01_serveur_minimal_tornado.py",
            "title": "2.1 — Premiers Pas avec Tornado : `tornado.web.Application`, `RequestHandler`, Templates (`self.render`) vs JSON (`self.write`) & Modèle de Richardson",
            "duration": "55 min",
            "analogy": {
                "title": "Un guichet orienté objet (RequestHandler) où chaque verbe HTTP est une méthode de classe",
                "text": "Contrairement aux micro-frameworks basés sur des fonctions décorées, **Tornado** structure chaque ressource autour d'une **classe Python héritant de `tornado.web.RequestHandler`**. Si un client envoie un `GET`, Tornado appelle `def get(self):`. S'il envoie un `POST`, Tornado appelle `def post(self):`.\nLes pages Web résident dans le dossier **`templates/`** et sont rendues via **`self.render('accueil.html', ...)`**, tandis que les routes d'API RESTful renvoient du JSON nativement en passant un dictionnaire à **`self.write({...})`**."
            },
            "explanation": [
                "**1. Comment Tornado sert à la fois des pages Web (`self.render`) et des APIs JSON (`self.write`)** :\n  - **Pour une page Web destinée à un navigateur** : On place le fichier HTML dans `day_2/templates/accueil.html` (configuré via `template_path=...` dans `tornado.web.Application`) et on appelle `self.render('accueil.html', organisme='ISGP', modules=...)`.\n  - **Pour un endpoint d'API REST** : Lorsqu'on passe un `dict` Python à **`self.write({'message': '...', 'statut': 'actif'})`**, Tornado le sérialise automatiquement en JSON UTF-8 et injecte l'en-tête `Content-Type: application/json; charset=UTF-8` !",
                "**2. Le Modèle de Maturité de Richardson (Les 4 niveaux d'une API REST)** :\n  - **Niveau 0 (RPC)** : Une seule URL (`POST /api`) à laquelle on envoie des commandes diverses.\n  - **Niveau 1 (Les Ressources)** : Chaque entité métier possède sa propre URI (`/api/formations`, `/api/formations/12`).\n  - **Niveau 2 (Les Verbes & Codes HTTP)** : Dans un `RequestHandler` Tornado, les méthodes `get()`, `post()`, `put()`, `patch()`, `delete()` et `self.set_status(code)` implémentent naturellement le Niveau 2 de Richardson.\n  - **Niveau 3 (HATEOAS)** : La réponse JSON inclut des liens (`links`) vers les actions suivantes possibles.",
                "**3. La boucle d'événements non-bloquante `tornado.ioloop.IOLoop`** :\n  - Contrairement à un serveur synchrone qui bloque un thread par client, Tornado repose sur **`epoll` (Linux) / `kqueue` (BSD)** via sa boucle d'événements **`IOLoop`**, capable de maintenir des dizaines de milliers de connexions simultanées (problème C10k)."
            ],
            "code": _read("01_serveur_minimal_tornado.py"),
            "line_explanations": [
                {"lines": "29-37", "text": "`AccueilHandler` : la méthode `get(self)` appelle `self.render('accueil.html', ...)` pour compiler et servir le gabarit `tornado.template`."},
                {"lines": "41-48", "text": "`BonjourApiHandler` : passer un `dict` à `self.write({...})` génère automatiquement une réponse JSON (`application/json; charset=UTF-8`, statut `200`)."},
                {"lines": "52-57", "text": "`ModulesCollectionHandler` : expose la collection RESTful `/api/v1/modules`."},
                {"lines": "60-68", "text": "`make_app()` instancie `tornado.web.Application` avec la table de routage `(regex, HandlerClass)` et `template_path`."},
                {"lines": "71-96", "text": "Démonstration asynchrone non-bloquante (`AsyncHTTPClient`) ou démarrage du serveur avec `app.listen(8889)` et `IOLoop.current().start()`."}
            ],
            "sandbox_preset": {
                "label": "Tester la route GET /api/sandbox/bonjour",
                "method": "GET",
                "url": "/api/sandbox/bonjour",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_2/01_serveur_minimal_tornado.py` pour observer le rendu du template Tornado (`day_2/templates/accueil.html`) et la réponse JSON (`/api/bonjour`) :",
                "initial_code": _read("01_serveur_minimal_tornado.py")
            },
            "vscode_instructions": {
                "filename": "day_2/01_serveur_minimal_tornado.py",
                "steps": [
                    "Inspecter `day_2/01_serveur_minimal_tornado.py` et son template HTML `day_2/templates/accueil.html`.",
                    "Exécuter `.venv/bin/python day_2/01_serveur_minimal_tornado.py` (ou ajouter `--serve` pour démarrer sur le port 8889)."
                ]
            }
        },
        {
            "id": "d2-l2",
            "file": "day_2/02_routes_et_parametres.py",
            "title": "2.2 — Routage par Expressions Régulières (`r'/api/v1/stagiaires/([0-9]+)'`), `self.get_query_argument` & Objet `self.request`",
            "duration": "55 min",
            "analogy": {
                "title": "Le filtre par expression régulière qui capture et valide l'identifiant dès la table de routage",
                "text": "Dans **Tornado**, la table de routage utilise la puissance native des **Expressions Régulières Python (`re`)**. Chaque groupe entre parenthèses `(...)` dans le motif d'URL est automatiquement extrait et passé comme argument à la méthode `def get(self, ...)` du `RequestHandler` !"
            },
            "explanation": [
                "**1. Les groupes capturants Regex dans le routeur Tornado** :\n  - `r'/api/saluer/([^/]+)'` : Capture toute séquence de caractères jusqu'au prochain `/` et la passe en argument `def get(self, prenom):`.\n  - `r'/api/v1/stagiaires/([0-9]+)'` : Capture **uniquement des chiffres** (`0-9`). Si un client appelle `/api/v1/stagiaires/abc`, l'expression régulière ne correspond pas et Tornado renvoie immédiatement `404 Not Found` !",
                "**2. Comparaison des 4 syntaxes de paramètres de chemin en ingénierie d'API** :\n  - **`([0-9]+)` / `(?P<id>[0-9]+)`** : Syntaxe par expression régulière de **Tornado** et `re` Python.\n  - **`<int:id>`** : Syntaxe à chevrons de **Flask / Werkzeug**.\n  - **`:id`** : Syntaxe de **Postman** et **Express.js**.\n  - **`{id}`** : Syntaxe standard **OpenAPI 3.0 / Swagger** et **FastAPI**.",
                "**3. Anatomie complète de la requête dans un `RequestHandler` Tornado** :\n  - `self.request.method` : `'GET'`, `'POST'`, `'PUT'`, `'DELETE'`.\n  - `self.request.path` : Le chemin appelé (ex. `'/api/calcul-tva'`).\n  - `self.get_query_argument('ht', '1000.0')` : Extrait un paramètre de la Query String après `?`.\n  - `self.get_body_argument('titre', '')` : Extrait un champ de formulaire envoyé dans le corps `POST`.\n  - `self.request.headers` : Dictionnaire `HTTPHeaders` insensible à la casse.\n  - `tornado.escape.json_decode(self.request.body)` : Charge utile JSON désérialisée."
            ],
            "code": _read("02_routes_et_parametres.py"),
            "line_explanations": [
                {"lines": "27-37", "text": "`SaluerStagiaireHandler` : le groupe regex `([^/]+)` est injecté dans `def get(self, prenom):`."},
                {"lines": "41-50", "text": "`StagiaireJsonHandler` : le groupe regex `([0-9]+)` garantit que `stagiaire_id_str` ne contient que des chiffres avant conversion `int()`."},
                {"lines": "54-62", "text": "`FicheStagiaireHtmlHandler` : utilise le même groupe regex pour rendre le gabarit `fiche_stagiaire.html` via `self.render()`."},
                {"lines": "66-76", "text": "`CalculTvaHandler` : lit les paramètres `?ht=...&taux=...` via `self.get_query_argument(...)`."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/calcul-tva?ht=2500&taux=19",
                "method": "GET",
                "url": "/api/sandbox/calcul-tva?ht=2500&taux=19",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_2/02_routes_et_parametres.py` pour tester les groupes Regex Tornado, `self.render` et `self.get_query_argument` :",
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
            "title": "2.3 — Moteur `tornado.template` (`self.render`) & Traitement des Formulaires Web HTML (`self.get_body_argument` / `self.request.files`)",
            "duration": "65 min",
            "analogy": {
                "title": "Compiler le gabarit HTML en bytecode Python (tornado.template) et décoder les formulaires via self.get_body_argument",
                "text": "Le moteur **`tornado.template`** compile directement vos fichiers `.html` en fonctions Python en mémoire, ce qui le rend extrêmement rapide tout en échappant automatiquement les variables `{{ ... }}` contre les failles **XSS**.\nLorsqu'un utilisateur soumet un formulaire HTML `<form method='POST'>`, Tornado extrait les champs texte via **`self.get_body_argument('nom_champ')`** et les fichiers joints (`multipart/form-data`) via **`self.request.files`**."
            },
            "explanation": [
                "**1. Syntaxe du moteur natif `tornado.template` (`self.render`)** :\n  - **`{{ expression }}`** : Évalue n'importe quelle expression Python (ex: `{{ f['titre'] }}`) et applique automatiquement `tornado.escape.xhtml_escape` pour bloquer toute injection **XSS**.\n  - **`{% for f in formations %} ... {% end %}`** : Boucle Tornado (notez que dans Tornado, tous les blocs se ferment simplement par **`{% end %}`** !).\n  - **`{% if condition %} ... {% end %}`** : Affichage conditionnel.\n  - **`{# commentaire #}`** : Commentaire supprimé lors de la compilation du template.",
                "**2. Comment Tornado distingue un Formulaire HTML (`self.get_body_argument`) d'un appel API JSON (`json_decode`)** :\n  - Un formulaire `<form method='POST'>` envoie `Content-Type: application/x-www-form-urlencoded`. On lit ses champs avec **`self.get_body_argument('titre', '')`**.\n  - Un client API envoie `Content-Type: application/json`. On décode alors les octets de `self.request.body` avec **`tornado.escape.json_decode(self.request.body)`**.",
                "**3. Upload de Fichiers (`enctype='multipart/form-data'`) avec `self.request.files`** :\n  - Dans Tornado, `self.request.files['document_pdf']` retourne une liste de dictionnaires représentant chaque fichier téléversé : `{'filename': '...', 'body': b'...', 'content_type': 'application/pdf'}`.\n  - On nettoie systématiquement `filename` (`os.path.basename` + filtrage Regex) pour empêcher toute attaque *Path Traversal* (`../../etc/passwd`)."
            ],
            "code": _read("05_jinja_et_formulaires_html.py"),
            "line_explanations": [
                {"lines": "37-45", "text": "`FormationsHybrideHandler.get` : affiche la page HTML initiale via `self.render('formations.html', ...)`."},
                {"lines": "56-65", "text": "Détection du format : `tornado.escape.json_decode(self.request.body)` si `application/json`, sinon `self.get_body_argument(...)` pour un formulaire HTML."},
                {"lines": "97-103", "text": "Rendu du gabarit `day_2/templates/formations.html` après validation des champs."},
                {"lines": "109-132", "text": "`UploadSyllabusHandler.post` : lit les fichiers binaires depuis `self.request.files.get('document_pdf', [])` et nettoie le nom du fichier."}
            ],
            "sandbox_preset": {
                "label": "Tester POST /api/sandbox/formulaire-formation (Formulaire HTML)",
                "method": "POST",
                "url": "/api/sandbox/formulaire-formation",
                "body": "titre=Atelier+Tornado&formateur=ISGP&duree_jours=4&salle=Salle+B"
            },
            "python_runner": {
                "prompt": "Exécutez le test complet de soumission de formulaire HTML (`self.get_body_argument` + `self.render`) et d'upload `multipart/form-data` (`self.request.files`) :",
                "initial_code": _read("05_jinja_et_formulaires_html.py")
            },
            "vscode_instructions": {
                "filename": "day_2/05_jinja_et_formulaires_html.py",
                "steps": [
                    "Inspecter le template Tornado `day_2/templates/formations.html` (fermeture des blocs par `{% end %}`) et `day_2/05_jinja_et_formulaires_html.py`.",
                    "Ouvrir l'atelier interactif sur `http://127.0.0.1:8888/sandbox/formulaire-jinja`."
                ]
            }
        },
        {
            "id": "d2-l3",
            "file": "day_2/03_pagination_filtrage_tri.py",
            "title": "2.4 — Pagination (`page`, `limit`), Filtrage Multi-Critères & Tri Dynamique avec `self.get_query_argument`",
            "duration": "65 min",
            "analogy": {
                "title": "Ne jamais bloquer l'IOLoop en sérialisant 250 000 lignes d'un seul bloc",
                "text": "Dans une architecture événementielle comme **Tornado**, sérialiser un tableau JSON de 80 Mo bloquerait l'`IOLoop` pendant plusieurs centaines de millisecondes. En production, **toute route retournant une collection doit impérativement implémenter la Pagination, le Filtrage et le Tri**."
            },
            "explanation": [
                "**1. Algorithme de Pagination par `page` et `limit` (Offset / Limit)** :\n  - Lecture sécurisée via `self.get_query_argument('page', '1')` et `self.get_query_argument('limit', '3')`.\n  - Plafonnement obligatoire : `limit = min(50, max(1, int(...)))`.\n  - Découpage de la tranche : `debut = (page - 1) * limit`, `fin = debut + limit`.",
                "**2. Enveloppe de métadonnées de pagination (`meta`)** : Retourne `total_elements`, `total_pages`, `page_actuelle` et `a_page_suivante`.",
                "**3. Sécurisation du Tri Dynamique (`?tri=duree_jours&ordre=desc`)** : Validation par **liste blanche (whitelist)** (`('id', 'duree_jours', 'titre')`)."
            ],
            "code": _read("03_pagination_filtrage_tri.py"),
            "line_explanations": [
                {"lines": "28-36", "text": "Étape 1 (Filtrage) : Extrait `salle` et `min_jours` via `self.get_query_argument()` et filtre la collection."},
                {"lines": "39-43", "text": "Étape 2 (Tri) : Vérifie que `champ_tri` appartient à la liste blanche, puis trie par ordre croissant ou décroissant."},
                {"lines": "46-53", "text": "Étape 3 (Pagination) : Calcule `total_pages` avec `math.ceil()` et découpe `resultats[debut:fin]`."},
                {"lines": "55-65", "text": "`self.write({...})` sérialise l'enveloppe `{meta, data}` en JSON."}
            ],
            "sandbox_preset": {
                "label": "Tester la Pagination & le Tri : GET /api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc",
                "method": "GET",
                "url": "/api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_2/03_pagination_filtrage_tri.py` pour tester la pagination, le filtrage et le tri avec Tornado :",
                "initial_code": _read("03_pagination_filtrage_tri.py")
            },
            "vscode_instructions": {
                "filename": "day_2/03_pagination_filtrage_tri.py",
                "steps": [
                    "Ouvrir `day_2/03_pagination_filtrage_tri.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_2/03_pagination_filtrage_tri.py`."
                ]
            }
        },
        {
            "id": "d2-l4",
            "file": "day_2/04_middlewares_et_audit_log.py",
            "title": "2.5 — Cycle de Vie d'un `RequestHandler` Tornado (`set_default_headers`, `prepare`, `on_finish`) & Journalisation d'Audit",
            "duration": "50 min",
            "analogy": {
                "title": "La classe de base BaseAuditHandler dont héritent tous les contrôleurs de l'API",
                "text": "Dans Tornado, au lieu d'enregistrer des fonctions globales, on crée une **classe de base `BaseAuditHandler(tornado.web.RequestHandler)`** qui surcharge trois méthodes du cycle de vie : **`set_default_headers(self)`**, **`prepare(self)`** (exécutée avant la méthode HTTP) et **`on_finish(self)`** (exécutée après l'envoi de la réponse au client)."
            },
            "explanation": [
                "**1. Ordre exact d'exécution des hooks d'un `RequestHandler` Tornado** :\n  1. `initialize(self, **kwargs)` : Reçoit les paramètres passés dans la table de routage.\n  2. `set_default_headers(self)` : Positionne les en-têtes par défaut (`X-Content-Type-Options: nosniff`, CORS) au début du traitement.\n  3. `prepare(self)` : S'exécute **avant** `get()`, `post()`, `put()`, `delete()`. Idéal pour démarrer un chronomètre (`self.heure_debut`), générer `self.request_id` ou vérifier un jeton global.\n  4. `get(self)` / `post(self)` / ... : Exécute la logique métier de la route.\n  5. `on_finish(self)` : S'exécute **après** que la réponse HTTP a été envoyée sur le socket réseau. Idéal pour écrire les logs d'audit et libérer des ressources.",
                "**2. Stockage d'état par requête sur `self`** : Comme Tornado instancie **un nouvel objet `RequestHandler` par requête HTTP**, vous pouvez stocker `self.heure_debut`, `self.request_id` ou `self.current_user` directement sur `self` sans aucun conflit entre requêtes concurrentes !"
            ],
            "code": _read("04_middlewares_et_audit_log.py"),
            "line_explanations": [
                {"lines": "20-23", "text": "`set_default_headers(self)` injecte systématiquement `X-Content-Type-Options: nosniff`."},
                {"lines": "25-29", "text": "`prepare(self)` démarre `time.perf_counter()` et attribue un identifiant de corrélation `X-Request-ID` sur `self.request_id`."},
                {"lines": "31-37", "text": "`on_finish(self)` calcule la durée totale de traitement et journalise la requête avec `self.get_status()`."},
                {"lines": "40-48", "text": "`StatutHandler(BaseAuditHandler)` hérite automatiquement de tout le comportement d'audit et de sécurité."}
            ],
            "python_runner": {
                "prompt": "Exécutez `day_2/04_middlewares_et_audit_log.py` pour observer le cycle `prepare()` -> `get()` -> `on_finish()` :",
                "initial_code": _read("04_middlewares_et_audit_log.py")
            },
            "vscode_instructions": {
                "filename": "day_2/04_middlewares_et_audit_log.py",
                "steps": [
                    "Ouvrir `day_2/04_middlewares_et_audit_log.py`.",
                    "Exécuter `.venv/bin/python day_2/04_middlewares_et_audit_log.py` et observer la trace `[AUDIT TORNADO]` générée par `on_finish()`."
                ]
            }
        }
    ]
}
