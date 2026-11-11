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
                "text": (
                    "À la différence des micro-frameworks qui dispersent les routes sur une multitude de fonctions autonomes décorées, **Tornado** modélise chaque ressource réseau comme un contrôleur orienté objet héritant de **`tornado.web.RequestHandler`**. "
                    "Lorsqu'un paquet `GET` franchit le socket non bloquant, Tornado instancie ce contrôleur et invoque `def get(self):` ; lorsqu'un `POST` arrive sur la même URI, il invoque `def post(self):` sur une instance fraîchement isolée.\n\n"
                    "Cette cohésion architecturale permet de faire cohabiter élégamment le rendu de portails Web compilés depuis `templates/` via **`self.render('accueil.html', ...)`** et l'exposition d'endpoints d'API RESTful haute performance via **`self.write({...})`**."
                )
            },
            "explanation": [
                (
                    "**Dualité native entre gabarits HTML compilés (`self.render`) et sérialisation JSON (`self.write`).** "
                    "Lorsqu'une route s'adresse à un opérateur humain sur navigateur, `self.render('accueil.html', organisme='ISGP', modules=...)` compile le fichier situé dans `template_path` en bytecode Python et émet du `text/html; charset=UTF-8`. "
                    "À l'inverse, dès qu'une méthode d'API transmet un dictionnaire Python `dict` à `self.write({'message': '...', 'statut': 'actif'})`, Tornado le convertit automatiquement en flux JSON UTF-8 et injecte l'en-tête normatif `Content-Type: application/json; charset=UTF-8` sans appel manuel à `json.dumps()`."
                ),
                (
                    "**Alignement structurel de `RequestHandler` sur le Modèle de Maturité de Richardson.** "
                    "Là où le Niveau 0 tunnelise des ordres RPC disparates sur une URL unique et où le Niveau 1 introduit des URIs nominales par ressource (`/api/v1/formations`), Tornado incarne nativement le **Niveau 2 industriel** en associant l'adresse de la ressource à la table de routage `Application` et l'intention métier aux méthodes `get()`, `post()`, `put()`, `patch()`, `delete()` assorties de `self.set_status(code)`, ouvrant la voie aux liens hypermédias `links` du Niveau 3 (HATEOAS)."
                ),
                (
                    "**Multiplexage d'entrées-sorties non bloquantes par `tornado.ioloop.IOLoop` (Architecture C10K).** "
                    "Plutôt que d'immobiliser un thread système coûteux en RAM par client connecté en attente d'octets réseau, Tornado enregistre ses sockets `O_NONBLOCK` auprès des primitives noyau **`epoll` (Linux)** ou **`kqueue` (BSD/macOS)** pilotées par sa boucle événementielle `IOLoop`, lui permettant d'absorber des dizaines de milliers de connexions simultanées au sein d'un processus unique."
                )
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
                "text": (
                    "Dans **Tornado**, la table d'aiguillage d'une `Application` ne s'appuie pas sur un mini-langage propriétaire limité, mais directement sur le moteur d'**expressions régulières compilées (`re`)** de la bibliothèque standard Python.\n\n"
                    "Chaque parenthèse capturante `(...)` inscrite dans le motif d'URL agit simultanément comme un garde-fou syntaxique à la frontière du routeur et comme un extracteur automatique qui injecte la sous-chaîne capturée dans la signature de `def get(self, ...)`."
                )
            },
            "explanation": [
                (
                    "**Filtrage structurel en amont par groupes capturants d'expressions régulières.** "
                    "Un motif tel que `r'/api/saluer/([^/]+)'` isole tout segment non vide jusqu'au séparateur suivant et le transmet en argument positionnel à `def get(self, prenom):`, tandis qu'un motif numérique strict `r'/api/v1/stagiaires/([0-9]+)'` rejette dès le routeur toute requête malformée comme `/api/v1/stagiaires/abc` en émettant un `404 Not Found` avant même d'instancier votre `RequestHandler`."
                ),
                (
                    "**Interopérabilité entre les quatre conventions de variables de chemin de l'écosystème API.** "
                    "Un architecte navigue quotidiennement entre quatre notations désignant le même concept de *Path Parameter* selon l'outil employé : les groupes Regex `([0-9]+)` ou nommés `(?P<id>[0-9]+)` dans le code serveur **Tornado**, les chevrons typés `<int:id>` propres à **Flask/Werkzeug**, le préfixe deux-points `:id` reconnu par l'interface **Postman** et Express.js, ainsi que les accolades normalisées `{id}` exigées par la spécification **OpenAPI 3.0 / RFC 6570**."
                ),
                (
                    "**Inspection exhaustive de `HTTPServerRequest` via `self.request` et les accesseurs Tornado.** "
                    "À l'intérieur de toute méthode d'un `RequestHandler`, Tornado expose la requête décodée à travers une interface cohérente : `self.request.method` et `self.request.path` décrivent la ligne de départ, `self.get_query_argument('ht', '1000.0')` extrait et décode un critère d'URL après `?`, `self.get_body_argument('titre', '')` lit un champ de formulaire `POST`, `self.request.headers` donne accès aux métadonnées HTTP de façon insensible à la casse, et `tornado.escape.json_decode(self.request.body)` désérialise la charge utile JSON."
                )
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
                "text": (
                    "Au lieu d'interpréter lentement les gabarits texte à chaque requête entrante, le moteur natif **`tornado.template`** traduit vos fichiers `.html` directement en fonctions Python compilées en mémoire vive, alliant une vitesse d'exécution remarquable à un échappement automatique des expressions `{{ ... }}` contre toute injection **XSS**.\n\n"
                    "Lorsqu'un opérateur soumet un formulaire Web `<form method='POST'>`, Tornado décode séparément les champs textuels encodés via **`self.get_body_argument('nom_champ')`** et les pièces jointes binaires (`multipart/form-data`) logées dans **`self.request.files`**."
                )
            },
            "explanation": [
                (
                    "**Compilation en mémoire, auto-échappement Anti-XSS et bloc universel `{% end %}` dans `tornado.template`.** "
                    "Dans un gabarit rendu par `self.render()`, toute expression `{{ f['titre'] }}` traverse automatiquement `tornado.escape.xhtml_escape` afin de neutraliser les chevrons `<script>` malveillants en entités HTML inoffensives. "
                    "Les directives de contrôle telles que les boucles `{% for f in formations %}` et les embranchements `{% if condition %}` obéissent à une grammaire épurée propre à Tornado où chaque structure se referme uniformément par l'unique balise **`{% end %}`**, tandis que les annotations `{# commentaire #}` sont éliminées à la compilation."
                ),
                (
                    "**Aiguillage du décodage selon le `Content-Type` : formulaire HTML (`get_body_argument`) contre API JSON (`json_decode`).** "
                    "La soumission native d'un élément `<form method='POST'>` par un navigateur émet un corps encodé en `application/x-www-form-urlencoded` (`titre=Tornado&duree_jours=5`) que Tornado expose via `self.get_body_argument('titre', '')`. "
                    "À l'opposé, un client programmatique annonçant `Content-Type: application/json` transmet un arbre JSON brut dans `self.request.body` qui doit être analysé explicitement par `tornado.escape.json_decode(self.request.body)`."
                ),
                (
                    "**Réception binaire `multipart/form-data` via `self.request.files` et assainissement Anti-Path-Traversal.** "
                    "Dès qu'un formulaire embarque un champ `<input type='file'>` sous `enctype='multipart/form-data'`, Tornado peuple `self.request.files['document_pdf']` avec une liste de descripteurs contenant `filename`, les octets `body` et le `content_type`. "
                    "Avant toute écriture sur le système de fichiers, le contrôleur doit impérativement dépouiller `filename` via `os.path.basename()` et une liste blanche de caractères afin d'interdire toute traversée d'arborescence telle que `../../etc/passwd`."
                )
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
                "text": (
                    "Sur un serveur événementiel monothreadé tel que **Tornado**, la sérialisation JSON est une opération purement processeur (CPU-bound) exécutée sur le fil principal : tenter d'encoder d'un seul tenant 250 000 enregistrements en une chaîne de 80 Mo confisquerait l'`IOLoop` durant plusieurs centaines de millisecondes, gelant instantanément toutes les autres connexions actives.\n\n"
                    "En ingénierie de production, toute route exposant une collection de ressources doit donc imposer par construction le triptyque **Filtrage, Tri sécurisé et Pagination bornée**."
                )
            },
            "explanation": [
                (
                    "**Arithmétique de découpage `Offset / Limit` et bornage défensif des paramètres.** "
                    "À partir des critères extraits via `self.get_query_argument('page', '1')` et `self.get_query_argument('limit', '3')`, le contrôleur impose systématiquement une borne inférieure et un plafond anti-DoS (`page = max(1, ...)` et `limit = min(50, max(1, ...))`) avant de calculer les indices de tranche `debut = (page - 1) * limit` et `fin = debut + limit`."
                ),
                (
                    "**Auto-descriptivité de la collection par l'enveloppe de métadonnées (`meta`).** "
                    "Plutôt que de livrer un tableau muet obligeant l'interface cliente à deviner s'il subsiste d'autres enregistrements, la réponse structure un bloc `meta` exposant `total_elements` (calculé sur l'ensemble filtré avant découpage), `total_pages` (obtenu par plafond entier `math.ceil`), `page_actuelle` et l'indicateur booléen `a_page_suivante`."
                ),
                (
                    "**Protection du tri dynamique (`?tri=...&ordre=...`) par liste blanche stricte.** "
                    "Afin d'empêcher un appelant de provoquer une `KeyError` sur un attribut inexistant ou une injection SQL sur une clause `ORDER BY`, le paramètre `tri` est systématiquement confronté à un tuple immuable de colonnes autorisées `('id', 'duree_jours', 'titre')` avant toute exécution du tri."
                )
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
                "text": (
                    "Dans l'architecture orientée objet de Tornado, la factorisation des préoccupations transversales (sécurité des en-têtes, traçabilité distribuée, chronométrage et journaux d'audit) ne repose pas sur un empilement opaque d'intercepteurs globaux, mais sur l'héritage explicite d'une classe socle **`BaseAuditHandler(tornado.web.RequestHandler)`**.\n\n"
                    "En redéfinissant les points d'ancrage du cycle de vie **`set_default_headers(self)`**, **`prepare(self)`** en amont du verbe HTTP et **`on_finish(self)`** en aval de la transmission réseau, chaque contrôleur métier hérite instantanément d'une instrumentation de niveau bancaire."
                )
            },
            "explanation": [
                (
                    "**Ordonnancement déterministe des cinq jalons du cycle de vie d'un `RequestHandler`.** "
                    "Pour chaque requête entrante, Tornado exécute dans un ordre immuable `initialize(self, **kwargs)` pour injecter la configuration issue de la route, `set_default_headers(self)` pour poser les en-têtes de défense systématiques (`X-Content-Type-Options: nosniff`, CORS), puis `prepare(self)` juste avant la méthode HTTP afin d'initialiser le chronomètre monotone `time.perf_counter()`, d'attacher `X-Request-ID` ou d'interrompre précocement l'appel via `self.finish()`. "
                    "Une fois la méthode métier (`get`, `post`, `put`, `delete`) achevée et les octets poussés vers le socket TCP, Tornado invoque toujours `on_finish(self)` pour consolider l'écriture du journal d'audit et libérer les descripteurs ouverts."
                ),
                (
                    "**Isolation naturelle du contexte de requête sur l'instance éphémère `self`.** "
                    "Parce que Tornado alloue **une nouvelle instance dédiée de `RequestHandler` par transaction HTTP** avant de la confier au ramasse-miettes après `on_finish()`, tous les attributs attachés à `self` (`self.heure_debut`, `self.request_id`, `self.current_user`) demeurent hermétiquement cloisonnés en mémoire, éliminant tout risque de collision entre deux coroutines concurrentes sur l'`IOLoop`."
                )
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
