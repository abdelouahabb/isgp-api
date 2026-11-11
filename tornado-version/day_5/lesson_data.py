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
                "text": (
                    "Au cœur d'un démon événementiel **Tornado**, une unique boucle `IOLoop` orchestre de façon coopérative des milliers de sockets TCP concurrents sur un seul fil d'exécution. "
                    "Si un `RequestHandler` commet l'erreur d'invoquer un client synchrone tel que `requests.get()` ou `urllib.request.urlopen()` vers un service partenaire qui met trois secondes à répondre, **l'intégralité de l'`IOLoop` demeure paralysée pendant trois secondes pour tous les utilisateurs connectés**.\n\n"
                    "Pour préserver une réactivité sub-milliseconde, Tornado embarque nativement son propre moteur client non bloquant **`tornado.httpclient.AsyncHTTPClient`**, qui cède coopérativement la main via `await client.fetch(...)` pendant l'attente réseau."
                )
            },
            "explanation": [
                (
                    "**Bornage temporel obligatoire par `connect_timeout` et `request_timeout` dans `AsyncHTTPClient`.** "
                    "Chaque instance `HTTPRequest` soumise à `AsyncHTTPClient` doit fixer explicitement deux garde-fous distincts : `connect_timeout=2.0` pour plafonner la résolution DNS et la poignée de main TCP/TLS initiale, et `request_timeout=5.0` pour borner la durée totale de réception de la réponse complète afin d'éviter toute accumulation infinie de coroutines suspendues."
                ),
                (
                    "**Inspection explicite des réponses d'erreur amont grâce à `raise_error=False`.** "
                    "Par défaut, `await client.fetch(req)` lève une exception `tornado.httpclient.HTTPClientError` dès que le serveur interrogé répond par un code `>= 400`. "
                    "Passer `raise_error=False` restitue proprement l'objet `HTTPResponse` (`reponse.code`, `reponse.headers`, `reponse.body`), permettant à votre passerelle Tornado de distinguer finement un `404` métier d'une défaillance `503` ou d'un timeout réseau `599`."
                ),
                (
                    "**Recul exponentiel non bloquant (*Exponential Backoff*) via `await asyncio.sleep()`.** "
                    "Face aux pannes transitoires (`429`, `502`, `503`, `504`), la coroutine espace ses tentatives de réessai au moyen de **`await asyncio.sleep(delai)`** (et jamais `time.sleep()`, qui gèlerait le thread de l'`IOLoop`), libérant immédiatement le processeur pour servir les autres requêtes entrantes."
                )
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
                "text": (
                    "Dans les grandes plateformes mondiales, une branche `/api/v1` demeure active durant cinq à dix ans grâce à la **Loi de Postel (*Tolerant Reader*)** : ajouter un attribut JSON inédit ou exposer une nouvelle route constitue une évolution purement additive que les clients existants tolèrent sans broncher.\n\n"
                    "Préfixer ses routes par `/api/v1` dès le premier jour n'en demeure pas moins une assurance-vie architecturale décisive : le jour où une refonte structurelle impose une **rupture de contrat (*Breaking Change*)** telle que le remplacement d'un entier `\"duree\": 5` par un objet `{\"valeur\": 5, \"unite\": \"jours\"}`, il suffit dans Tornado de concaténer `API_V1_ROUTES + API_V2_ROUTES` au sein de `create_app()` pour servir simultanément les deux générations de clients."
                )
            },
            "explanation": [
                (
                    "**Composition modulaire de sous-tables de routage dans la fabrique `create_app()`.** "
                    "Dans Tornado, le routage s'exprime comme une structure de données Python explicite — une liste de tuples `(regex, HandlerClass)` ou d'instances `tornado.routing.Rule`. "
                    "Chaque domaine fonctionnel (`WEB_ROUTES`, `API_V1_ROUTES`, `API_V2_ROUTES`, `HEALTH_ROUTES`) exporte sa propre sous-table autonome, que la fabrique `create_app()` assemble proprement lors de l'instanciation de `tornado.web.Application`."
                ),
                (
                    "**Coexistence contrôlée `/api/v1` + `/api/v2` et signalisation de fin de vie RFC 8594.** "
                    "Pendant la fenêtre de migration, `FormationsV1Handler` et `FormationsV2Handler` partagent le même socle métier SQL tout en projetant chacun son contrat JSON respectif, tandis que `FormationsV1Handler.set_default_headers()` injecte automatiquement les en-têtes normalisés **IETF RFC 8594** (`Deprecation: true`, `Sunset: Thu, 31 Dec 2026 23:59:59 GMT` et `Link: </api/v2/formations>; rel=\"successor-version\"`)."
                ),
                (
                    "**Sondes d'exploitation différenciées : *Liveness* (`/api/health/live`) et *Readiness* (`/api/health/ready`).** "
                    "Pour piloter un répartiteur Nginx ou un orchestrateur Kubernetes sans fausses alertes, `LivenessProbeHandler` atteste uniquement que la boucle `IOLoop` du processus n'est pas bloquée (`200 OK`), tandis que `ReadinessProbeHandler` vérifie activement la joignabilité du moteur SQLite/PostgreSQL avant d'autoriser le routage du trafic client."
                )
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
                "text": (
                    "À la différence de Flask (simple application WSGI tributaire de Gunicorn) ou de FastAPI (application ASGI tributaire d'Uvicorn), **Tornado embarque nativement son propre serveur HTTP industriel haute concurrence (`tornado.httpserver.HTTPServer`)** forgé dès l'origine pour absorber le problème C10K.\n\n"
                    "Pour exploiter l'ensemble des cœurs physiques d'un serveur Linux malgré le verrou global *GIL* de CPython, l'architecture de référence déploie une flotte de processus indépendants `HTTPServer(app, xheaders=True)` (un démon par cœur sur `127.0.0.1:8001..8004`) orchestrés en amont par un répartiteur **Nginx**."
                )
            },
            "explanation": [
                (
                    "**Topologie de production `Nginx -> Cluster HTTPServer(xheaders=True)` multi-processus.** "
                    "En frontal public, **Nginx** assure la terminaison cryptographique TLS, décharge les actifs `/static/` directement depuis le cache noyau via `sendfile on`, et distribue les requêtes dynamiques en `least_conn` vers les instances Tornado locales. "
                    "Sur chaque nœud Python, l'activation impérative de **`xheaders=True`** ordonne à `HTTPServer` d'interpréter `X-Forwarded-For` et `X-Forwarded-Proto` afin que `self.request.remote_ip` et `self.request.protocol` restituent la véritable adresse IP cliente aux journaux d'audit et au limiteur de débit."
                ),
                (
                    "**Harnais de test d'intégration isolé avec `tornado.testing.AsyncHTTPTestCase`.** "
                    "Dérivée de `unittest.TestCase`, la classe native `AsyncHTTPTestCase` instancie automatiquement une boucle `IOLoop` dédiée et monte votre `make_app()` sur un port TCP éphémère libre à chaque test : un simple appel `self.fetch('/api/calcul-taxe', method='POST', body=...)` traverse ainsi toute la pile HTTP réelle en quelques millisecondes."
                )
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
                "text": (
                    "La spécification **OpenAPI 3.0** joue pour une API Tornado le rôle exact des plans d'architecte cotés et normalisés d'un ouvrage d'art : elle décrit sans la moindre ambiguïté chaque route, chaque type de champ JSON et chaque schéma d'authentification dans un document lisible par les machines.\n\n"
                    "Branché directement sur ce contrat vivant (`/api/openapi.json`), le portail **Swagger UI (`/api/docs`)** projette une maquette interactive navigable où les équipes frontales, mobiles et partenaires peuvent s'authentifier via **« Authorize »** et éprouver chaque endpoint en direct via **« Try it out »**."
                )
            },
            "explanation": [
                (
                    "**Séparation architecturale entre le contrat formel (`OpenApiSpecHandler`) et le portail visuel (`SwaggerUiHandler`).** "
                    "Dans Tornado, `OpenApiSpecHandler` sérialise sur `/api/openapi.json` le dictionnaire conforme à la norme **OpenAPI 3.0.3** via `self.write()`, tandis que `SwaggerUiHandler` sert sur `/api/docs` une enveloppe HTML légère initialisant `SwaggerUIBundle` sur cette URL de spécification, sans aucune dépendance lourde ni introspection magique opaque."
                ),
                (
                    "**Traduction normative entre groupes Regex Tornado et modèles d'URI OpenAPI (RFC 6570).** "
                    "Alors que `tornado.web.Application` identifie et valide un paramètre dynamique au moyen d'une expression régulière Python telle que `r'/api/v1/formations/([0-9]+)'`, la section `paths` du contrat OpenAPI 3.0 doit impérativement exprimer cette même route selon la grammaire universelle à accolades `'/api/v1/formations/{id}'` couplée à un descripteur `in: 'path'`."
                )
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
                "text": (
                    "Sur une API **Tornado** de production desservant des tables de plusieurs millions d'enregistrements, extraire et sérialiser des volumes non bornés bloquerait immédiatement l'`IOLoop`. "
                    "Deux stratégies complémentaires gouvernent le découpage des collections à grande échelle.\n\n"
                    "La pagination **`Offset/Limit`** (`?page=2&per_page=20`) permet de sauter directement vers un numéro de page précis dans une grille d'administration, tandis que la pagination par **`Curseur / Keyset`** (`?after_id=1042&limit=20`) exploite directement l'arbre B-Tree de la clé primaire pour garantir un temps de réponse constant `O(1)` même au fond d'un historique massif."
                )
            },
            "explanation": [
                (
                    "**Pagination par décalage `Offset / Limit` (`CatalogueOffsetHandler`) et coût linéaire `O(N)`.** "
                    "Calculer `offset = (page - 1) * per_page` pour exécuter `SELECT * FROM formations LIMIT ? OFFSET ?` offre une ergonomie idéale pour afficher des sélecteurs de pages numérotés, mais oblige le moteur SQL à parcourir puis ignorer séquentiellement les `offset` premières lignes sur les très grands volumes."
                ),
                (
                    "**Pagination par curseur `Keyset` en temps constant `O(1)` (`CatalogueCursorHandler`).** "
                    "En transmettant le dernier identifiant observé via `self.get_query_argument('after_id', '0')`, la requête préparée `SELECT * FROM formations WHERE id > ? ORDER BY id ASC LIMIT ?` positionne instantanément sa tête de lecture dans l'index B-Tree de la clé primaire et restitue `meta.next_cursor` sans jamais subir de dérive lors d'insertions concurrentes."
                ),
                (
                    "**Verrouillage du tri dynamique par liste blanche (`CHAMPS_TRI_AUTORISES`).** "
                    "Parce qu'un marqueur paramétré `?` SQLite ne peut se substituer à un identifiant de colonne dans une clause `ORDER BY`, tout paramètre `?sort=-tarif_dzd` est dépouillé de son préfixe de signe puis validé strictement contre l'ensemble figé `CHAMPS_TRI_AUTORISES = {'id', 'duree_jours', 'tarif_dzd', 'titre'}`, rejetant tout écart par un code `422`."
                )
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
