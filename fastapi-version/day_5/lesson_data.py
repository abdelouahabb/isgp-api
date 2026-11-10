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
                "text": "Lorsqu'un serveur A appelle l'API d'un serveur B (par exemple une passerelle de paiement ou un service partenaire), le réseau peut ralentir ou le serveur B peut geler sans fermer la connexion TCP.\nSi votre client Python appelle une API distante **sans paramètre `timeout`**, votre coroutine ou votre worker restera bloqué en attendant une réponse qui ne viendra jamais : c'est une **panne en cascade** (*Cascading Failure*)."
            },
            "explanation": [
                "**Règle d'or n°1 — Toujours imposer un `timeout` explicite** : Que ce soit avec `httpx.AsyncClient(timeout=5.0)` (recommandé dans une route `async def` FastAPI pour ne pas bloquer l'Event Loop ASGI) ou `urllib.request.urlopen(..., timeout=5.0)`, un appel réseau doit toujours abandonner proprement au bout de quelques secondes.",
                "**Règle d'or n°2 — Pourquoi utiliser `httpx.AsyncClient` plutôt que `requests` dans FastAPI ?** : `requests.get()` est synchrone et bloquant ; appelé à l'intérieur d'une route `async def`, il fige la boucle d'événements d'Uvicorn. `await client.get(...)` via `httpx.AsyncClient` libère la boucle ASGI pendant l'attente réseau !",
                "**Règle d'or n°3 — *Exponential Backoff* face aux erreurs temporaires (`429`, `502`, `503`, `504`)** : Si l'API distante renvoie `503 Service Unavailable`, on applique un **recul exponentiel** : attendre `1s` avant le 1er réessai, puis `2s`, puis `4s` (ou lire l'en-tête `Retry-After` en cas de `429`)."
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
                "text": "Une question revient systématiquement chez les ingénieurs : *« Pourquoi 90 % des APIs mondiales (OpenAI `/v1/chat/completions`, Stripe `/v1/charges`, Kubernetes `/apis/apps/v1`) restent-elles sur `v1` pendant 5 à 10 ans, et pourquoi met-on quand même `/v1` dès le premier jour ? »*\nLa réponse tient en deux principes fondamentaux :\n1. **La Loi de Postel (*Tolerant Reader*)** : Ajouter un nouveau champ JSON ou une nouvelle route est une **évolution rétrocompatible (*Non-Breaking Change*)**. Les clients existants ignorent simplement les clés qu'ils ne connaissent pas.\n2. **L'Assurance-Vie Architecturale** : Si un jour vous devez modifier le **type** d'un champ existant (ex: remplacer `\"duree\": 5` par `\"duree\": {\"valeur\": 5, \"unite\": \"jours\"}`) ou renommer une clé, c'est une **rupture de contrat (*Breaking Change*)**. Avoir placé `/api/v1` dès le Jour 1 vous permet alors de monter un second **`APIRouter(prefix='/api/v2/formations')`** en parallèle sans faire planter les applications mobiles déjà installées !"
            },
            "explanation": [
                "**1. Évolution Rétrocompatible (*Non-Breaking* -> rester en `v1`) vs Rupture de Contrat (*Breaking Change* -> créer `v2`)** :\n  - **Rétrocompatible (Rester en `/api/v1`)** : Ajouter un nouveau champ dans la réponse JSON, ajouter une nouvelle route (`GET /api/v1/certificats`), ou ajouter un paramètre de requête optionnel (`?lang=fr`).\n  - **Rupture de Contrat (Exige `/api/v2`)** : Supprimer ou renommer un champ JSON (`intitule` -> `titre`), changer le type d'une clé (`duree: 5` (int) -> `duree: {valeur: 5, unite: 'jours'}` (dict)), ou rendre obligatoire un nouveau champ à l'entrée d'un `POST`.",
                "**2. Coexistence de `/api/v1` et `/api/v2` grâce à `APIRouter` de FastAPI & Dépréciation RFC 8594** :\n  - Dans FastAPI, **`APIRouter(prefix='/api/v1/formations', tags=['...'])`** est l'équivalent moderne et typé des `Blueprints` de FastAPI.\n  - Les deux routeurs (`formations_v1_router` et `formations_v2_router`) sont assemblés dans `create_app()` via **`application.include_router(...)`**.\n  - Sur la route `v1`, on ajoute `deprecated=True` dans `@formations_v1_router.get('', deprecated=True)` (ce qui la barre visuellement dans Swagger UI !) et on injecte les en-têtes officiels de dépréciation (**Norme IETF RFC 8594**) :\n    - `Deprecation: true`\n    - `Sunset: Thu, 31 Dec 2026 23:59:59 GMT`\n    - `Link: </api/v2/formations>; rel=\"successor-version\"`",
                "**3. Le patron *Application Factory* (`create_app()`) & Sondes de Supervision (`/api/health/live` & `/ready`)** :\n  - `def create_app() -> FastAPI:` assemble tous les `APIRouter` (`web_router`, `formations_v1_router`, `formations_v2_router`, `sante_router`).\n  - `/api/health/live` (*Liveness*) vérifie que le worker Uvicorn tourne (`200 OK`), tandis que `/api/health/ready` (*Readiness*) vérifie que la base SQLite/SQL est joignable avant que Nginx n'envoie du trafic."
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
                "text": "En développement local, on lance `uvicorn app:app --reload` pour redémarrer automatiquement à chaque modification de fichier.\nEn production, on désactive `--reload` et on déploie plusieurs processus **Workers ASGI** (`uvicorn app:app --workers 4` ou `gunicorn -k uvicorn.workers.UvicornWorker -w 4`) derrière un **Reverse Proxy Nginx** qui gère TLS/HTTPS et la répartition de charge."
            },
            "explanation": [
                "**Architecture de Déploiement en Production (`Client -> Nginx -> Uvicorn Workers (ASGI) -> FastAPI`)** :\n  1. **Reverse Proxy (`Nginx` / `Caddy`)** : Gère le chiffrement HTTPS (TLS), les certificats SSL, la compression Gzip et répartit la charge (`upstream`).\n  2. **Serveur d'Application ASGI (`Uvicorn` / `Gunicorn + UvicornWorker`)** : Démarre plusieurs processus Python dotés chacun d'une boucle d'événements asynchrone `uvloop` ultra-performante (`uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4`).\n  3. **Application FastAPI (`app`)** : Exécute votre logique métier asynchrone et la validation Pydantic v2.",
                "**Tester son API automatiquement sans ouvrir de port réseau (`from fastapi.testclient import TestClient`)** : `client = TestClient(app)` utilise `httpx` en mémoire pour exécuter des requêtes `GET`, `POST`, `PUT`, `DELETE` en quelques millisecondes et vérifier par `assert` le code HTTP (`200`, `422`) et le JSON ou HTML retourné."
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
                "text": "Contrairement aux frameworks anciens où il faut rédiger manuellement des centaines de lignes de dictionnaire JSON ou YAML pour documenter l'API, **FastAPI génère automatiquement 100 % du contrat OpenAPI 3.1 (`/openapi.json`), le portail interactif Swagger UI (`/docs`) et le portail de lecture ReDoc (`/redoc`)** directement à partir de vos modèles Pydantic `BaseModel`, de vos annotations `{id}: int` et de vos dépendances `Security(...)` !"
            },
            "explanation": [
                "**1. Les 3 URLs natives générées automatiquement par toute instance `FastAPI()`** :\n  - **`/openapi.json`** : Le contrat machine officiel conforme à la spécification **OpenAPI 3.1.0**, généré par introspection des modèles Pydantic (`Formation`, `FormationInput`, `ErreurRFC7807`).\n  - **`/docs`** : Le portail interactif **Swagger UI** permettant de tester chaque route (*« Try it out »*) et de s'authentifier via le bouton cadenas **« Authorize »**.\n  - **`/redoc`** : La documentation **ReDoc** organisée en 3 colonnes pour une lecture claire par les équipes partenaires.",
                "**2. Comment enrichir la génération automatique OpenAPI dans FastAPI** :\n  - Paramètres de `FastAPI(title=..., version=..., description=..., openapi_tags=...)`.\n  - Paramètres des décorateurs de route : `response_model=list[Formation]`, `status_code=201`, `tags=['Formations']`, `summary='...'`, `responses={401: ..., 422: {'model': ErreurRFC7807}}`.\n  - Dépendances de sécurité `APIKeyHeader(name='X-API-Key')` et `HTTPBearer()` injectées via `Security(...)` : ajoutent automatiquement le bouton cadenas **Authorize** dans Swagger UI !\n  - Surcharge optionnelle de `app.openapi = construire_contrat_openapi` via `get_openapi(...)` pour ajouter la liste des `servers` de production."
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
                "text": "Si votre table SQLite/PostgreSQL contient 500 000 formations ou factures et qu'un client appelle `GET /api/v1/factures` sans limite, le serveur tente de charger 500 000 lignes en RAM, sérialise 250 Mo de JSON et s'effondre par saturation mémoire (*Out Of Memory*).\nEn production FastAPI, toute route qui retourne une collection doit **obligatoirement** être paginée et bornée avec `Query(ge=1, le=20)` selon deux stratégies : **`Offset/Limit`** (`?page=2&per_page=20`) ou **`Cursor / Keyset`** (`?after_id=1042&limit=20` pour des performances constantes $O(1)$ sur des millions de lignes)."
            },
            "explanation": [
                "**1. Pagination par `Offset / Limit` (`?page=2&per_page=20`) avec `Query(ge=1, le=20)`** :\n  - Formule mathématique : `offset = (page - 1) * per_page` (`SELECT * FROM formations LIMIT 20 OFFSET 20`).\n  - **Avantage** : Permet d'afficher des boutons « Page 1, 2, 3... 15 » dans une interface d'administration.\n  - **Limite à grande échelle** : Sur `OFFSET 500000`, le moteur SQL doit quand même parcourir et jeter les 500 000 premières lignes avant de renvoyer les 20 suivantes !",
                "**2. Pagination Haute Performance par `Curseur / Keyset` (`?after_id=1042&limit=20`)** :\n  - Au lieu de sauter un nombre de lignes, le client passe l'identifiant du dernier élément reçu : `SELECT * FROM formations WHERE id > 1042 ORDER BY id ASC LIMIT 20`.\n  - **Avantage décisif** : Grâce à l'index sur la clé primaire `id`, la requête SQL s'exécute en **temps constant ($O(1)$, moins d'une milliseconde)** même à la 100 000e page.",
                "**3. Tri Dynamique Sécurisé par Liste Blanche (`CHAMPS_TRI_AUTORISES`)** :\n  - Pour supporter `?sort=-tarif_dzd` (tri décroissant) ou `?sort=duree_jours` (tri croissant), on valide toujours `cle_tri` contre `CHAMPS_TRI_AUTORISES = {'id', 'duree_jours', 'tarif_dzd', 'titre'}` et on lève `HTTPException(status_code=422)` sinon."
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
