import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_5_DATA = {
    "day_number": 5,
    "folder": "day_5",
    "badge": "Jour 5 • AsyncHTTPClient, Architecture Modulaire, Tests & Production Tornado",
    "title": "Client Asynchrone (AsyncHTTPClient), Architecture Modulaire & Versioning v1/v2, Tests (AsyncHTTPTestCase), OpenAPI 3.0 & Pagination Haute Performance",
    "goal": "Savoir consommer une API sans bloquer l'IOLoop grâce à tornado.httpclient.AsyncHTTPClient (connect_timeout, request_timeout), découper une grande API Tornado en tables de routes modulaires (Versioning v1/v2 RFC 8594, Healthchecks), automatiser les tests avec tornado.testing.AsyncHTTPTestCase, publier le contrat OpenAPI 3.0 et maîtriser la pagination (Offset vs Cursor) en production multi-processus.",
    "starter_filename": "day_5/03_architecture_blueprints.py",
    "files": [
        "day_5/01_client_python_auth.py",
        "day_5/03_architecture_blueprints.py",
        "day_5/04_tests_et_production.py",
        "day_5/05_swagger_openapi_ui.py",
        "day_5/02_pagination_filtrage_production.py",
    ],
    "lessons": [
        {
            "id": "d5-l1",
            "file": "day_5/01_client_python_auth.py",
            "title": "5.1 — Client HTTP Non-Bloquant : `tornado.httpclient.AsyncHTTPClient`, Timeouts (`connect_timeout`, `request_timeout`) & Résilience",
            "duration": "55 min",
            "analogy": {
                "title": "Pourquoi un serveur Tornado ne doit jamais appeler requests.get() ou urlopen() dans l'IOLoop",
                "text": "Dans un serveur événementiel comme **Tornado**, une seule boucle `IOLoop` gère des milliers de connexions simultanées. Si l'un de vos `RequestHandler` appelle `requests.get()` (synchrone) vers une API partenaire qui met 3 secondes à répondre, **toute l'IOLoop est figée pendant 3 secondes pour tous les autres utilisateurs** !\nC'est pourquoi Tornado intègre son propre client HTTP asynchrone non-bloquant : **`tornado.httpclient.AsyncHTTPClient`**, qui suspend uniquement la coroutine en cours (`await client.fetch(...)`) pendant que l'`IOLoop` continue de servir les autres clients."
            },
            "explanation": [
                "**Règle d'or n°1 — Toujours utiliser `AsyncHTTPClient` avec `connect_timeout` et `request_timeout`** :\n  - `connect_timeout=2.0` : Temps maximal accordé pour établir la connexion TCP/TLS.\n  - `request_timeout=5.0` : Temps maximal total pour recevoir la réponse HTTP complète.",
                "**Règle d'or n°2 — `raise_error=False` pour inspecter proprement les statuts `4xx` et `5xx`** :\n  - Par défaut, `await client.fetch(req)` lève `tornado.httpclient.HTTPClientError` si le statut est `>= 400`. En passant `raise_error=False`, vous récupérez l'objet `HTTPResponse` (`reponse.code`, `reponse.body`, `reponse.headers`) sans exception non gérée.",
                "**Règle d'or n°3 — *Exponential Backoff* face aux erreurs temporaires (`429`, `502`, `503`, `504`)** :\n  - En cas de `503` ou `429`, suspendre la coroutine avec `await asyncio.sleep(delai)` (et **jamais** `time.sleep()`, qui bloquerait l'`IOLoop` !)."
            ],
            "code": _read("01_client_python_auth.py"),
            "line_explanations": [
                {"lines": "49-70", "text": "Fonction asynchrone `appeler_api_tornado` utilisant `AsyncHTTPClient` et `HTTPRequest(..., connect_timeout=2.0, request_timeout=5.0)` avec `raise_error=False`."},
                {"lines": "81-87", "text": "Étape 1 : Authentification non-bloquante `POST /api/sandbox/auth/token` pour obtenir l'`access_token`."},
                {"lines": "90-95", "text": "Étape 2 : Appel `GET /api/sandbox/auth/profil` en injectant l'en-tête `Authorization: Bearer <mon_token>`."}
            ],
            "python_runner": {
                "prompt": "Exécutez ce client asynchrone Tornado (`AsyncHTTPClient`) en direct :",
                "initial_code": _read("01_client_python_auth.py")
            },
            "vscode_instructions": {
                "filename": "day_5/01_client_python_auth.py",
                "steps": [
                    "Ouvrir `day_5/01_client_python_auth.py` dans l'éditeur.",
                    "Exécuter `.venv/bin/python day_5/01_client_python_auth.py`."
                ]
            }
        },
        {
            "id": "d5-l2",
            "file": "day_5/03_architecture_blueprints.py",
            "title": "5.2 — Architecture Modulaire Tornado (Tables de Routes), Cycle de Vie d'API (`/api/v1` vs `/api/v2`, RFC 8594) & Sondes `/api/health`",
            "duration": "75 min",
            "analogy": {
                "title": "Pourquoi voit-on presque toujours `/api/v1` et si rarement `/api/v2` ?",
                "text": "1. **La Loi de Postel (*Tolerant Reader*)** : Ajouter un nouveau champ JSON ou une nouvelle route est une **évolution rétrocompatible (*Non-Breaking Change*)**. Les clients existants ignorent simplement les clés qu'ils ne connaissent pas, ce qui permet de faire évoluer `v1` pendant des années.\n2. **L'Assurance-Vie Architecturale** : Si un jour vous devez modifier le **type** d'un champ existant (ex: remplacer `\"duree\": 5` par `\"duree\": {\"valeur\": 5, \"unite\": \"jours\"}`), c'est une **rupture de contrat (*Breaking Change*)**. Dans Tornado, il suffit alors de concaténer `API_V1_ROUTES + API_V2_ROUTES` dans `create_app()` pour servir simultanément les deux versions !"
            },
            "explanation": [
                "**1. Découpage modulaire des routes dans Tornado (`WEB_ROUTES + API_V1_ROUTES + API_V2_ROUTES + HEALTH_ROUTES`)** :\n  - Dans Tornado, une table de routage n'est qu'une simple liste Python de tuples `(regex, HandlerClass)` (ou d'objets `tornado.routing.Rule`).\n  - Chaque sous-module du projet exporte sa propre liste de routes, et la fabrique `create_app()` les assemble dans `tornado.web.Application`.",
                "**2. Coexistence de `/api/v1` et `/api/v2` & En-têtes de Dépréciation RFC 8594** :\n  - Dans `FormationsV1Handler.set_default_headers(self)`, on injecte les en-têtes officiels **IETF RFC 8594** :\n    - `Deprecation: true`\n    - `Sunset: Thu, 31 Dec 2026 23:59:59 GMT`\n    - `Link: </api/v2/formations>; rel=\"successor-version\"`",
                "**3. Sondes de Supervision (`/api/health/live` & `/api/health/ready`)** :\n  - `LivenessProbeHandler` (`/api/health/live`) vérifie que l'`IOLoop` Tornado répond (`200 OK`).\n  - `ReadinessProbeHandler` (`/api/health/ready`) vérifie que la base SQLite/SQL est prête avant que Nginx n'envoie du trafic."
            ],
            "code": _read("03_architecture_blueprints.py"),
            "line_explanations": [
                {"lines": "24-28", "text": "Source de données métier unique (`CATALOGUE_METIER`) partagée entre le portail Web, l'API `v1` et l'API `v2`."},
                {"lines": "32-42", "text": "`PortailWebHandler` et `WEB_ROUTES` (`/portail`) servant le template `day_5/templates/portail_blueprint.html`."},
                {"lines": "46-64", "text": "`FormationsV1Handler` (`/api/v1/formations`) conservant le schéma plat historique (`duree: 5`) et injectant les en-têtes RFC 8594 dans `set_default_headers()`."},
                {"lines": "68-92", "text": "`FormationsV2Handler` (`/api/v2/formations`) exposant le nouveau schéma structuré (`duree: {valeur, unite, heures_pedagogiques}`)."},
                {"lines": "96-119", "text": "`HEALTH_ROUTES` (`/api/health/live` & `/ready`) et `create_app()` assemblant toutes les tables de routes dans `tornado.web.Application`."}
            ],
            "sandbox_preset": {
                "label": "Comparer API v1 (Dépréciée RFC 8594) vs API v2 : GET /api/v1/sandbox/formations",
                "method": "GET",
                "url": "/api/v1/sandbox/formations",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_5/03_architecture_blueprints.py` pour comparer en direct les en-têtes et schémas JSON de `/api/v1/formations` et `/api/v2/formations` :",
                "initial_code": _read("03_architecture_blueprints.py")
            },
            "vscode_instructions": {
                "filename": "day_5/03_architecture_blueprints.py",
                "steps": [
                    "Ouvrir `day_5/03_architecture_blueprints.py` dans l'éditeur.",
                    "Comparer `FormationsV1Handler` et `FormationsV2Handler` et observer les en-têtes `Deprecation` et `Sunset`."
                ]
            }
        },
        {
            "id": "d5-l3",
            "file": "day_5/04_tests_et_production.py",
            "title": "5.3 — Tests Automatisés (`tornado.testing.AsyncHTTPTestCase`) & Déploiement Production (`HTTPServer` + `xheaders=True`)",
            "duration": "65 min",
            "analogy": {
                "title": "Un serveur HTTP C10k intégré : pourquoi Tornado n'a pas besoin de Gunicorn en production",
                "text": "Contrairement à Flask (qui est uniquement un framework WSGI et dépend de Gunicorn) ou FastAPI (qui dépend d'Uvicorn), **Tornado inclut son propre serveur HTTP industriel haute performance (`tornado.httpserver.HTTPServer`)**.\nEn production, on déploie plusieurs instances `HTTPServer(app, xheaders=True)` (une par cœur CPU sur les ports `8001..8004`, ou via `server.start(0)`) directement derrière un **Reverse Proxy Nginx** !"
            },
            "explanation": [
                "**1. Architecture de Déploiement Tornado en Production (`Client -> Nginx -> 4 instances Tornado HTTPServer`)** :\n  - **Reverse Proxy (`Nginx`)** : Gère TLS/HTTPS, sert `/static/` directement via `sendfile` et répartit la charge (`least_conn`) vers `127.0.0.1:8001..8004`.\n  - **Paramètre critique `xheaders=True` sur `HTTPServer`** : Indique à `tornado.httpserver.HTTPServer` de lire `X-Forwarded-For` et `X-Forwarded-Proto` transmis par Nginx afin que `self.request.remote_ip` et `self.request.protocol` reflètent la véritable adresse IP et le vrai protocole du client !",
                "**2. Tester son API automatiquement avec `tornado.testing.AsyncHTTPTestCase`** :\n  - Tornado fournit la classe **`tornado.testing.AsyncHTTPTestCase`** (basée sur `unittest.TestCase`).\n  - Il suffit de surcharger `def get_app(self): return make_app()` : chaque test dispose alors de `self.fetch('/ma-route', method='POST', body=...)` qui démarre une `IOLoop` isolée sur un port éphémère et retourne la réponse en quelques millisecondes !"
            ],
            "code": _read("04_tests_et_production.py"),
            "line_explanations": [
                {"lines": "16-25", "text": "`CalculTaxeApiHandler` : route API JSON `POST /api/calcul-taxe` validant `montant_ht` (`422` si négatif)."},
                {"lines": "29-41", "text": "`CalculTaxeFormulaireHandler` : route Formulaire HTML `POST /formulaire-taxe` lisant `self.get_body_argument('montant_ht')` et rendant `resultat_taxe.html`."},
                {"lines": "54-88", "text": "`TestCalculateurFiscalTornado(tornado.testing.AsyncHTTPTestCase)` : exécute 3 tests automatisés (`self.fetch`) couvrant le JSON nominal (`200`), l'erreur métier (`422`) et le formulaire HTML."}
            ],
            "python_runner": {
                "prompt": "Exécutez la suite de tests officielle `tornado.testing.AsyncHTTPTestCase` en direct :",
                "initial_code": _read("04_tests_et_production.py")
            },
            "vscode_instructions": {
                "filename": "day_5/04_tests_et_production.py",
                "steps": [
                    "Ouvrir `day_5/04_tests_et_production.py` dans l'éditeur.",
                    "Exécuter `.venv/bin/python day_5/04_tests_et_production.py`."
                ]
            }
        },
        {
            "id": "d5-l4",
            "file": "day_5/05_swagger_openapi_ui.py",
            "title": "5.4 — Documentation Interactive & Contrat d'API dans Tornado : Swagger UI (`/api/docs`) & OpenAPI 3.0 (`/api/openapi.json`)",
            "duration": "60 min",
            "analogy": {
                "title": "Les plans d'architecte cotés (OpenAPI) et la maquette interactive 3D visitable (Swagger UI)",
                "text": "La norme mondiale **OpenAPI 3.0** est le plan d'architecte formel (en JSON ou YAML) de votre API Tornado, et **Swagger UI** est le portail Web généré à partir de ce plan, permettant à tout développeur de cliquer sur **« Try it out »** ou **« Authorize »** directement dans son navigateur."
            },
            "explanation": [
                "**1. Différence entre `OpenAPI 3.0` et `Swagger UI` dans Tornado** :\n  - `OpenApiSpecHandler` (`/api/openapi.json`) : Retourne le dictionnaire Python conforme à la spécification **OpenAPI 3.0.3** via `self.write(construire_contrat_openapi())`.\n  - `SwaggerUiHandler` (`/api/docs`) : Rend le template `swagger_ui.html` qui charge l'interface graphique interactive pointant vers `/api/openapi.json`.",
                "**2. Correspondance entre les routes Regex Tornado et les chemins OpenAPI 3.0** :\n  - Dans `tornado.web.Application`, la route s'écrit avec un groupe Regex : `r'/api/v1/formations/([0-9]+)'`.\n  - Dans le contrat OpenAPI `paths`, cette même route se documente avec la notation standard RFC 6570 entre accolades : `'/api/v1/formations/{id}'` (`in: 'path'`)."
            ],
            "code": _read("05_swagger_openapi_ui.py"),
            "line_explanations": [
                {"lines": "32-55", "text": "En-tête du contrat OpenAPI 3.0.3 (`info`, `servers` sur le port `8888`, `tags`)."},
                {"lines": "57-71", "text": "`securitySchemes` configure les deux cadenas d'authentification dans Swagger UI : `BearerAuth` et `ApiKeyAuth`."},
                {"lines": "195-210", "text": "`OpenApiSpecHandler` (`/api/openapi.json`) et `SwaggerUiHandler` (`/api/docs`)."},
                {"lines": "215-232", "text": "`FormationsListHandler` et `FormationDetailHandler` implémentant les routes documentées."}
            ],
            "sandbox_preset": {
                "label": "Inspecter le Contrat OpenAPI 3.0 : GET /api/openapi.json",
                "method": "GET",
                "url": "/api/openapi.json",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez le générateur et validateur de contrat OpenAPI 3.0 Tornado (`day_5/05_swagger_openapi_ui.py`) :",
                "initial_code": _read("05_swagger_openapi_ui.py")
            },
            "vscode_instructions": {
                "filename": "day_5/05_swagger_openapi_ui.py",
                "steps": [
                    "Ouvrir `day_5/05_swagger_openapi_ui.py` dans VS Code ou Antigravity IDE.",
                    "Ouvrir le portail interactif réel du laboratoire sur `http://127.0.0.1:8888/api/docs`."
                ]
            }
        },
        {
            "id": "d5-l5",
            "file": "day_5/02_pagination_filtrage_production.py",
            "title": "5.5 — Ingénierie de Collection en Production (100 % Tornado) : Pagination `Offset/Limit` vs `Cursor (Keyset)`, Filtrage & Tri Sécurisé",
            "duration": "55 min",
            "analogy": {
                "title": "Feuilleter un annuaire par numéro de page (Offset) vs Reprendre exactement après le dernier numéro lu (Curseur)",
                "text": "En production avec **Tornado**, toute route qui retourne une collection doit **obligatoirement** être paginée selon deux stratégies : **`Offset/Limit`** (`?page=2&per_page=20` pour les tableaux avec numéros de pages) ou **`Cursor / Keyset`** (`?after_id=1042&limit=20` pour des performances constantes $O(1)$ sur des millions de lignes sans jamais bloquer l'`IOLoop`)."
            },
            "explanation": [
                "**1. Pagination par `Offset / Limit` (`CatalogueOffsetHandler`)** :\n  - Formule mathématique : `offset = (page - 1) * per_page` (`SELECT * FROM formations LIMIT 20 OFFSET 20`).\n  - Idéal pour afficher des numéros de pages dans un tableau d'administration.",
                "**2. Pagination Haute Performance par `Curseur / Keyset` (`CatalogueCursorHandler`)** :\n  - Le client passe l'identifiant du dernier élément reçu (`self.get_query_argument('after_id', '0')`) : `SELECT * FROM formations WHERE id > ? ORDER BY id ASC LIMIT ?`.\n  - S'exécute en **temps constant ($O(1)$)** grâce à l'index sur la clé primaire `id`.",
                "**3. Tri Dynamique Sécurisé par Liste Blanche (`CHAMPS_TRI_AUTORISES`)** :\n  - Validation stricte de `cle_tri` contre `CHAMPS_TRI_AUTORISES = {'id', 'duree_jours', 'tarif_dzd', 'titre'}` avant tout tri (`422` sinon)."
            ],
            "code": _read("02_pagination_filtrage_production.py"),
            "line_explanations": [
                {"lines": "26", "text": "Liste blanche stricte `CHAMPS_TRI_AUTORISES` protégeant le tri dynamique contre toute injection."},
                {"lines": "30-74", "text": "`CatalogueOffsetHandler` : filtrage multi-critères (`domaine`, `duree_min`), tri sécurisé (`?sort=-tarif_dzd`) et enveloppe `meta` / `data` / `links`."},
                {"lines": "78-96", "text": "`CatalogueCursorHandler` : pagination par curseur (`?after_id=2&limit=2`) renvoyant `meta.next_cursor`."}
            ],
            "sandbox_preset": {
                "label": "Tester la Pagination v2 : GET /api/v2/sandbox/formations?page=1&per_page=2",
                "method": "GET",
                "url": "/api/v2/sandbox/formations?page=1&per_page=2",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez le comparatif entre Pagination Offset/Limit et Pagination par Curseur (`after_id`) en Tornado :",
                "initial_code": _read("02_pagination_filtrage_production.py")
            },
            "vscode_instructions": {
                "filename": "day_5/02_pagination_filtrage_production.py",
                "steps": [
                    "Ouvrir `day_5/02_pagination_filtrage_production.py` dans l'éditeur.",
                    "Tester le comportement si un client envoie un champ de tri non autorisé comme `?sort=mot_de_passe` (`422`)."
                ]
            }
        }
    ]
}
