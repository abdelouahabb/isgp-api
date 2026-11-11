import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_5_DATA = {
    "day_number": 5,
    "folder": "day_5",
    "badge": "Jour 5 • APIRouter, Versioning, TestClient & Production ASGI",
    "title": "Architecture Modulaire (APIRouter & Versioning v1/v2), Client Asynchrone Résilient, TestClient, OpenAPI 3.1 Natif & Production Uvicorn",
    "goal": "Savoir consommer une API de manière résiliente (Timeouts, Exponential Backoff, httpx.AsyncClient), découper une grande API en modules (APIRouter, Application Factory, Versioning v1/v2 RFC 8594, Healthchecks), automatiser les tests avec TestClient(app), personnaliser le contrat OpenAPI 3.1 natif (/docs, /redoc, /openapi.json) et maîtriser la pagination (Offset vs Cursor) en production ASGI Uvicorn.",
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
            "title": "5.1 — Ingénierie du Client HTTP Résilient (`httpx.AsyncClient` & `urllib.request`) : Timeouts, Gestion d'Erreurs & Exponential Backoff",
            "duration": "55 min",
            "analogy": {
                "title": "Ne jamais appeler le réseau sans chronomètre (Timeout)",
                "text": (
                    "Lorsqu'un microservice FastAPI A interroge l'API d'un service externe B — passerelle monétique, registre gouvernemental ou fournisseur de notifications —, le lien inter-réseaux peut subir une perte de paquets silencieuse où le serveur B accepte la connexion TCP mais fige l'écriture de la réponse.\n\n"
                    "Si le client HTTP Python invoque cette ressource distante **sans paramètre `timeout` explicite**, la coroutine ou le thread appelant demeure suspendu indéfiniment dans l'attente d'octets qui n'arriveront jamais, propageant de proche en proche une **panne en cascade (*Cascading Failure*)** à travers tout le système d'information."
                )
            },
            "explanation": [
                "**Obligation absolue d'un `timeout` borné sur tout appel réseau sortant.** Qu'on emploie le client asynchrone `httpx.AsyncClient(timeout=5.0)` au cœur d'une route `async def` ou la bibliothèque standard `urllib.request.urlopen(..., timeout=5.0)` dans un script autonome, chaque opération d'entrée/sortie réseau doit imposer une échéance stricte afin de libérer les descripteurs de sockets et de restituer rapidement un code `504 Gateway Timeout` en cas d'engorgement amont.",
                "**Préservation de la boucle d'événements ASGI (`httpx.AsyncClient` vs `requests`).** Appeler une bibliothèque synchrone bloquante telle que `requests.get()` à l'intérieur d'une coroutine `async def` FastAPI gèle intégralement le thread unique de l'Event Loop `asyncio`/`uvloop` d'Uvicorn, paralysant simultanément des centaines d'autres clients connectés au même worker. L'instruction non bloquante `await client.get(...)` de `httpx.AsyncClient` rend immédiatement la main à l'ordonnanceur ASGI durant toute l'attente réseau.",
                "**Recul exponentiel (*Exponential Backoff*) face aux pannes transitoires (`429`, `502`, `503`, `504`).** Lorsqu'un partenaire amont traverse une micro-coupure et renvoie `503 Service Unavailable`, marteler sa socket en boucle immédiate aggrave sa saturation : l'algorithme d'*Exponential Backoff* espace géométriquement les tentatives (`1s`, `2s`, `4s` assortis d'un léger aléa *Jitter*, ou selon la directive exacte de l'en-tête `Retry-After` sur un `429`) tout en s'abstenant de tout réessai sur les erreurs déterministes `4xx`."
            ],
            "code": _read("01_client_python_auth.py"),
            "line_explanations": [
                {"lines": "47-69", "text": "Fonction synchrone `appeler_api_urllib_avec_backoff` illustrant le `timeout=5.0` et l'Exponential Backoff (`2 ** (tentative - 1)`) sur les codes `429/502/503/504`."},
                {"lines": "72-91", "text": "Client asynchrone `httpx.AsyncClient(..., timeout=5.0)` exécutant successivement `POST /api/sandbox/auth/token` puis `GET /api/sandbox/auth/profil` avec l'en-tête `Authorization: Bearer`."}
            ],
            "python_runner": {
                "prompt": "Exécutez ce client résilient asynchrone (`httpx.AsyncClient` + FastAPI) :",
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
            "title": "5.2 — Architecture Modulaire (`APIRouter`), Cycle de Vie d'API (`/api/v1` vs `/api/v2`, Breaking Changes, RFC 8594) & Sondes `/api/health`",
            "duration": "75 min",
            "analogy": {
                "title": "Pourquoi voit-on presque toujours `/api/v1` et si rarement `/api/v2` ?",
                "text": (
                    "Une interrogation revient invariablement en comité d'architecture : pourquoi la quasi-totalité des grandes plateformes mondiales (OpenAI `/v1/chat/completions`, Stripe `/v1/charges`, Kubernetes `/apis/apps/v1`) demeurent-elles sur le préfixe `v1` pendant cinq à dix ans, tout en exigeant pourtant sa présence dès le premier jour de mise en ligne ?\n\n"
                    "La réponse tient à la conjugaison de la **Loi de Postel (*Tolerant Reader*)** — selon laquelle tout ajout de champ JSON ou de route optionnelle constitue une évolution rétrocompatible qui ne brise jamais les clients existants — et d'une **assurance-vie architecturale** : le jour où une refonte structurelle impose de transformer l'entier `\"duree\": 5` en objet `\"duree\": {\"valeur\": 5, \"unite\": \"jours\"}`, disposer de `/api/v1` dès l'origine permet de monter un second **`APIRouter(prefix='/api/v2/formations')`** côte à côte sans interrompre le parc mobile en service."
                )
            },
            "explanation": [
                "**Frontière entre évolution additive (*Non-Breaking*) et rupture de contrat (*Breaking Change*).** Enrichir une réponse JSON d'un nouvel attribut, exposer un nouvel endpoint ou introduire un paramètre `Query` facultatif muni d'une valeur par défaut préserve intégralement la compatibilité ascendante au sein de `/api/v1`. À l'inverse, renommer ou supprimer une clé JSON (`intitule` vers `titre`), muter le type d'un champ scalaire en sous-objet structuré ou rendre obligatoire un nouvel attribut d'entrée brise les désérialiseurs clients et impose l'ouverture d'une branche `/api/v2`.",
                "**Coexistence multi-versions par `APIRouter` et cycle de dépréciation normatif RFC 8594.** Dans FastAPI, la classe **`APIRouter(prefix='/api/v1/formations', tags=['...'])`** — équivalent modulaire et typé des `Blueprints` de Flask — permet de brancher simultanément `formations_v1_router` et `formations_v2_router` sur la même source de données via `application.include_router(...)`. Marquer l'ancienne branche avec `deprecated=True` la signale visuellement dans Swagger UI tandis que l'injection des en-têtes IETF RFC 8594 (`Deprecation: true`, `Sunset: Thu, 31 Dec 2026 23:59:59 GMT` et `Link: </api/v2/formations>; rel=\"successor-version\"`) automatise le préavis de migration.",
                "**Patron *Application Factory* (`create_app()`) et sondes d'orchestration (`/live` vs `/ready`).** Encapsuler la construction de l'instance `FastAPI` dans une fabrique `def create_app() -> FastAPI:` élimine les importations circulaires et facilite l'instanciation isolée dans les suites de tests. Les deux sondes de supervision découplent le diagnostic d'infrastructure : `/api/health/live` (*Liveness*) atteste que la boucle d'événements du worker Uvicorn répond, tandis que `/api/health/ready` (*Readiness*) valide la connectivité effective au moteur SQL avant que Nginx ou Kubernetes n'y achemine du trafic."
            ],
            "code": _read("03_architecture_blueprints.py"),
            "line_explanations": [
                {"lines": "22-26", "text": "Source de données métier unique (`CATALOGUE_METIER`) partagée entre le portail Web Jinja2Templates, l'API `v1` et l'API `v2`."},
                {"lines": "29-42", "text": "`web_router = APIRouter(prefix='/portail')` servant le template `day_5/templates/portail_blueprint.html` via `Jinja2Templates`."},
                {"lines": "47-63", "text": "`formations_v1_router = APIRouter(prefix='/api/v1/formations')` avec `deprecated=True` et en-têtes RFC 8594 (`Deprecation: true`, `Sunset`, `Link`)."},
                {"lines": "69-90", "text": "`formations_v2_router = APIRouter(prefix='/api/v2/formations')` exposant le nouveau schéma structuré (`duree: {valeur, unite, heures_pedagogiques}`, enveloppe `meta` + `data`)."},
                {"lines": "93-116", "text": "`sante_router` (`/api/health/live` & `/ready`) et `create_app()` assemblant les 4 routeurs avec `application.include_router(...)`."}
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
                    "Comparer la structure du champ `duree` entre `lister_formations_v1()` (entier `5`) et `lister_formations_v2()` (objet structuré) et observer les en-têtes `Deprecation` et `Sunset`."
                ]
            }
        },
        {
            "id": "d5-l3",
            "file": "day_5/04_tests_et_production.py",
            "title": "5.3 — Tests Automatisés (`TestClient`), Validation Pydantic & Déploiement Production ASGI (`Uvicorn` / `Gunicorn UvicornWorker`)",
            "duration": "65 min",
            "analogy": {
                "title": "Pourquoi le mode `--reload` est réservé au développement et comment déployer en production ASGI",
                "text": (
                    "Sur le poste d'un développeur, lancer `uvicorn app:app --reload` offre un retour visuel immédiat en scrutant les modifications du système de fichiers au sein d'un processus unique non durci.\n\n"
                    "En production, cet observateur de fichiers est proscrit : l'exploitation industrielle déploie un pool de processus **Workers ASGI** indépendants (`uvicorn app:app --workers 4` ou `gunicorn -k uvicorn.workers.UvicornWorker -w 4`) abrités derrière un **Reverse Proxy Nginx** chargé de la terminaison cryptographique TLS/HTTPS, du filtrage périmétrique et de la répartition de charge."
                )
            },
            "explanation": [
                "**Topologie de production à trois étages (`Nginx -> Workers ASGI Uvicorn -> FastAPI`).** En première ligne, le proxy inverse **Nginx** (ou Caddy/Traefik) absorbe le trafic Internet sur `:443`, négocie TLS 1.3, compresse les flux en Gzip/Brotli et distribue les requêtes sur un cluster local `upstream`. En deuxième ligne, le gestionnaire de processus (`Uvicorn --workers N` ou `Gunicorn + UvicornWorker`) exploite tous les cœurs physiques du processeur en dotant chaque processus Python de sa propre boucle d'événements C `uvloop` ultra-rapide dans laquelle s'exécutent l'application **FastAPI** et le moteur Rust `pydantic-core`.",
                "**Vérification de non-régression en mémoire vive avec `TestClient(app)`.** Adossé au transport `ASGITransport` de `httpx`, `client = TestClient(app)` injecte des requêtes synthétiques `GET`, `POST`, `PUT` ou `DELETE` directement dans le canal ASGI de l'application sans ouvrir le moindre port TCP sur le système d'exploitation, permettant d'valider en quelques millisecondes dans un pipeline CI/CD aussi bien les cas nominaux (`200`, `201`) que les rejets Pydantic (`422`) et les vues `Jinja2Templates`."
            ],
            "code": _read("04_tests_et_production.py"),
            "line_explanations": [
                {"lines": "17-29", "text": "Modèle Pydantic `CalculTaxePayload(montant_ht: float = Field(..., ge=0))` et route `@app.post('/api/calcul-taxe')`."},
                {"lines": "33-56", "text": "Routes Formulaire HTML `/formulaire-taxe` lisant `montant_ht: float = Form(...)` et rendant `day_5/templates/resultat_taxe.html` via `Jinja2Templates`."},
                {"lines": "60-79", "text": "Suite de tests automatisés `TestClient(app)` vérifiant le `200 OK` JSON, le rejet automatique `422` par Pydantic sur un montant négatif, et le rendu du formulaire HTML Jinja2."}
            ],
            "python_runner": {
                "prompt": "Exécutez la suite de tests automatisés `TestClient(app)` en direct :",
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
            "title": "5.4 — Documentation Interactive & Contrat OpenAPI 3.1 Natif dans FastAPI : `/docs` (Swagger UI), `/redoc` (ReDoc) & `/openapi.json`",
            "duration": "60 min",
            "analogy": {
                "title": "Les plans d'architecte générés automatiquement à partir de vos modèles Pydantic",
                "text": (
                    "Dans les frameworks Web de génération précédente, maintenir une documentation d'API obligeait à rédiger à la main des centaines de lignes YAML ou JSON qui divergeaient du code réel dès la première livraison urgente.\n\n"
                    "En faisant des annotations de type Python la source unique de vérité, **FastAPI synthétise automatiquement 100 % du contrat normatif OpenAPI 3.1.0 (`/openapi.json`), le banc d'essai interactif Swagger UI (`/docs`) et la documentation éditoriale ReDoc (`/redoc`)** par simple introspection de vos classes Pydantic `BaseModel`, de vos paramètres `{id}: int` et de vos dépendances `Security(...)`."
                )
            },
            "explanation": [
                "**Trinité documentaire native exposée par toute instance `FastAPI()`.** Sans configuration tierce, le framework sert simultanément le schéma machine **`/openapi.json`** conforme à OpenAPI 3.1.0 et JSON Schema Draft 2020-12 (exploitable pour générer automatiquement des SDK TypeScript, Kotlin ou Swift), l'interface interactive **`/docs`** (Swagger UI munie de *Try it out* et du cadenas d'authentification *Authorize*) ainsi que le portail **`/redoc`** structuré en trois colonnes pour l'intégration partenaire.",
                "**Enrichissement sémantique du contrat par métadonnées déclaratives et `Security(...)`.** La précision du contrat OpenAPI s'affine directement dans le code Python : le constructeur `FastAPI(title=..., version=..., openapi_tags=...)` structure l'en-tête global, les arguments de route (`response_model`, `status_code=201`, `summary`, `responses={422: {'model': ErreurRFC7807}}`) publient le catalogue exact des réponses possibles, les dépendances `APIKeyHeader` et `HTTPBearer` injectées via `Security(...)` activent la boîte de dialogue d'authentification dans Swagger UI, et la surcharge `get_openapi(...)` permet d'y greffer la topologie des `servers` de production."
            ],
            "code": _read("05_swagger_openapi_ui.py"),
            "line_explanations": [
                {"lines": "23-47", "text": "Déclaration de `APIKeyHeader`, `HTTPBearer` et des schémas Pydantic v2 `Formation`, `FormationInput` et `ErreurRFC7807`."},
                {"lines": "54-66", "text": "Configuration de `FastAPI` avec `docs_url='/docs'`, `redoc_url='/redoc'`, `openapi_url='/openapi.json'` et `openapi_tags`."},
                {"lines": "76-123", "text": "Routes métier documentées déclarativement par `response_model`, `tags`, `summary`, `responses` et `Security(api_key_header)`."},
                {"lines": "129-159", "text": "Fonction `construire_contrat_openapi()` utilisant `get_openapi(...)` pour enrichir les `servers` et `securitySchemes`."}
            ],
            "sandbox_preset": {
                "label": "Inspecter le Contrat OpenAPI : GET /api/openapi.json",
                "method": "GET",
                "url": "/api/openapi.json",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_5/05_swagger_openapi_ui.py` pour inspecter le schéma OpenAPI généré automatiquement par FastAPI :",
                "initial_code": _read("05_swagger_openapi_ui.py")
            },
            "vscode_instructions": {
                "filename": "day_5/05_swagger_openapi_ui.py",
                "steps": [
                    "Ouvrir `day_5/05_swagger_openapi_ui.py` dans VS Code ou Antigravity IDE.",
                    "Ouvrir également le portail interactif réel du laboratoire sur `http://127.0.0.1:8000/api/docs` pour tester Swagger UI en direct."
                ]
            }
        },
        {
            "id": "d5-l5",
            "file": "day_5/02_pagination_filtrage_production.py",
            "title": "5.5 — Ingénierie de Collection en Production (100 % FastAPI) : Pagination `Offset/Limit` vs `Cursor (Keyset)`, Filtrage & Tri Sécurisé",
            "duration": "55 min",
            "analogy": {
                "title": "Feuilleter un annuaire par numéro de page (Offset) vs Reprendre exactement après le dernier numéro lu (Curseur)",
                "text": (
                    "Lorsqu'une table SQLite ou PostgreSQL accumule 500 000 écritures de facturation et qu'un client appelle `GET /api/v1/factures` sans garde-fou, le worker ASGI tente d'instancier un demi-million d'objets Python en RAM et de sérialiser 250 Mo de JSON d'un seul tenant, provoquant son élimination immédiate par le noyau Linux (*OOM Killer*).\n\n"
                    "En ingénierie de production FastAPI, toute collection est strictement bornée via `Query(ge=1, le=20)` et servie selon l'un des deux patrons canoniques d'accès aux données : la pagination par décalage **`Offset/Limit`** (`?page=2&per_page=20`) pour les tableaux d'administration numérotés, ou la pagination par **`Curseur / Keyset`** (`?after_id=1042&limit=20`) pour maintenir une latence constante `O(1)` sur plusieurs dizaines de millions de lignes."
                )
            },
            "explanation": [
                "**Pagination `Offset / Limit` (`?page=2&per_page=20`) et coût linéaire sur les grands volumes.** La formule `offset = (page - 1) * per_page` traduite en `SELECT * FROM formations LIMIT 20 OFFSET 20` offre l'avantage ergonomique d'un accès direct à n'importe quel numéro de page dans un back-office Web. Elle présente toutefois une dégradation algorithmique `O(N)` à haute profondeur : sur `OFFSET 500000`, le moteur SQL doit balayer et écarter en mémoire les 500 000 premiers enregistrements avant de livrer les 20 suivants, tout en exposant le flux aux décalages si une ligne est insérée entre deux lectures.",
                "**Pagination haute performance par `Curseur / Keyset` (`?after_id=1042&limit=20`).** Au lieu de compter des lignes à sauter, le client renvoie le curseur du dernier enregistrement observé afin d'exécuter `SELECT * FROM formations WHERE id > ? ORDER BY id ASC LIMIT ?` : en s'appuyant directement sur l'arbre **B-Tree** de l'index de clé primaire `id`, le moteur relationnel positionne sa tête de lecture en **temps logarithmique/constant (`O(1)` pratique, sous la milliseconde)**, que le client lise la première ou la cent-millième tranche.",
                "**Validation par liste blanche stricte (`CHAMPS_TRI_AUTORISES`) sur les clauses `ORDER BY`.** Comme les marqueurs paramétrés `?` lient exclusivement des valeurs scalaires et ne peuvent jamais substituer un identifiant de colonne SQL, supporter une syntaxe telle que `?sort=-tarif_dzd` impose de valider la clé extraite contre un ensemble Python immuable `CHAMPS_TRI_AUTORISES = {'id', 'duree_jours', 'tarif_dzd', 'titre'}` et de rejeter tout écart par `HTTPException(status_code=422)` avant toute construction de requête."
            ],
            "code": _read("02_pagination_filtrage_production.py"),
            "line_explanations": [
                {"lines": "22-23", "text": "Liste blanche stricte `CHAMPS_TRI_AUTORISES` protégeant le tri dynamique contre toute injection."},
                {"lines": "27-74", "text": "Route `@app.get('/api/v1/catalogue/offset')` avec paramètres bornés par `Query(ge=1, le=20)`, tri sécurisé (`?sort=-tarif_dzd`) et enveloppe `meta` / `data` / `links`."},
                {"lines": "78-99", "text": "Route `@app.get('/api/v1/catalogue/cursor')` implémentant la pagination par curseur (`?after_id=2&limit=2`) et retournant `meta.next_cursor`."}
            ],
            "sandbox_preset": {
                "label": "Tester la Pagination v2 : GET /api/v2/sandbox/formations?page=1&per_page=2",
                "method": "GET",
                "url": "/api/v2/sandbox/formations?page=1&per_page=2",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez le comparatif entre Pagination Offset/Limit (avec tri `-tarif_dzd`) et Pagination par Curseur (`after_id`) en FastAPI :",
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
