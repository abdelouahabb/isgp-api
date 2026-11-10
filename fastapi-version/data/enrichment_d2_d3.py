"""
Manuel de Référence Approfondi — Enrichissement des Chapitres (Jours 2 et 3).
"""

ENRICHMENT_D2_D3 = {
    # =========================================================================
    # JOUR 2 — CHAPITRE 2.1 : SERVEUR MINIMAL FASTAPI, ASGI, UVICORN & TABLE DE ROUTAGE
    # =========================================================================
    "d2-l1": {
        "context": (
            "Après avoir compris les fondations Python (Jour 0) et le protocole réseau HTTP/JSON (Jour 1), nous "
            "construisons notre premier serveur d'API avec **FastAPI** et **Uvicorn**.\n"
            "Pourquoi FastAPI s'est-il imposé comme le standard moderne pour l'ingénierie des APIs Python ? "
            "Parce qu'il combine la performance asynchrone **ASGI** (Starlette + Uvicorn), la validation automatique "
            "des types par **Pydantic v2** et la génération native de la documentation **OpenAPI 3.1**. "
            "Ce chapitre explique comment un script Python devient un **démon réseau ASGI**, comment fonctionne "
            "le protocole **ASGI**, et comment FastAPI aiguille chaque URL vers la bonne fonction grâce à `app.routes`."
        ),
        "deep_sections": [
            {
                "heading": "1. Du Script Éphémère au Serveur Daemon ASGI : le rôle d'Uvicorn",
                "body": (
                    "Un script Python classique exécute ses lignes de haut en bas puis s'arrête : son processus disparaît "
                    "de la mémoire.\n"
                    "Un serveur Web, au contraire, doit rester **en éveil 24h/24** pour répondre aux clients à tout instant :\n"
                    "- Lorsque vous appelez `uvicorn.run(app, host=\"0.0.0.0\", port=8000)`, Uvicorn ouvre un **Socket TCP "
                    "d'écoute** attaché au port `8000` et démarre une boucle d'événements asynchrone (`asyncio` / `uvloop`).\n"
                    "- Dès qu'un client se connecte, Uvicorn lit la trame HTTP brute, trouve la route correspondante dans "
                    "`app.routes`, exécute votre fonction (`async def` ou `def`), sérialise la réponse JSON et reste disponible pour les autres requêtes concurrentes."
                )
            },
            {
                "heading": "2. Qu'est-ce que la norme ASGI (Asynchronous Server Gateway Interface) ?",
                "body": (
                    "Dans l'écosystème Python moderne, **ASGI** est le successeur asynchrone de la norme historique WSGI :\n"
                    "- Une application ASGI est une coroutine `async def app(scope, receive, send):`.\n"
                    "- Le dictionnaire `scope` contient toutes les métadonnées de la connexion (`type=\"http\"`, `method`, `path`, `query_string`, `headers`).\n"
                    "- Contrairement à WSGI qui bloquait un thread entier à chaque attente réseau ou base de données, ASGI permet "
                    "de traiter des milliers de connexions simultanées (HTTP/1.1, HTTP/2, WebSockets, Server-Sent Events) sans bloquer la boucle d'événements."
                )
            },
            {
                "heading": "3. Sérialisation JSON Automatique dans FastAPI (`return dict` / `BaseModel` vs `HTMLResponse`)",
                "body": (
                    "Dans FastAPI, vous n'avez même pas besoin d'appeler une fonction `jsonify()` :\n"
                    "1. Dès qu'une route `@app.get(...)` ou `@app.post(...)` retourne un `dict`, une `list` ou un modèle Pydantic `BaseModel`, "
                    "FastAPI le convertit automatiquement via `jsonable_encoder` et renvoie un `JSONResponse` avec l'en-tête **`content-type: application/json`**.\n"
                    "2. Lorsque vous souhaitez renvoyer une page Web HTML compilée avec Jinja2, vous utilisez `Jinja2Templates(directory=\"templates\")` "
                    "et `templates.TemplateResponse(request=request, name=\"...\", context={...})` avec `response_class=HTMLResponse`."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE D'AIGUILLAGE D'UNE REQUÊTE DANS FASTAPI (ASGI & APP.ROUTES)\n"
            "  Client HTTP (GET /api/v1/sante)\n"
            "        |\n"
            "        v\n"
            "  [Socket TCP :8000 (Serveur ASGI Uvicorn)]\n"
            "        |  (Construit le dictionnaire ASGI 'scope' + canaux 'receive'/'send')\n"
            "        v\n"
            "  [app = FastAPI()] ---> Consulte app.routes :\n"
            "                           - '/api/v1/sante'      [GET] -> etat_sante()\n"
            "                           - '/api/v1/formations' [GET] -> lister()\n"
            "        |\n"
            "        v\n"
            "  Exécute etat_sante() ---> return {...} ---> JSONResponse 200 OK (content-type: application/json)"
        ),
        "reference_table": {
            "title": "Composants Fondamentaux d'une Application FastAPI Minimale",
            "headers": ["Élément de code", "Rôle technique exact", "Que se passe-t-il si on l'omet ?"],
            "rows": [
                ["`app = FastAPI(title=..., version=...)`", "Instancie l'application ASGI et génère `/openapi.json` et `/docs`", "Impossible de déclarer des routes `@app.get` / `@app.post`"],
                ["`@app.get(\"/url\")` / `@app.post(\"/url\")`", "Enregistre le couple `(URL, Méthode HTTP)` dans `app.routes`", "La fonction reste une fonction Python ordinaire inaccessible par HTTP (`404`)"],
                ["`return {\"statut\": \"OK\"}`", "Sérialise automatiquement en JSON + ajoute `content-type: application/json`", "Si on omet `return`, la fonction renvoie `None` (`null` en JSON)"],
                ["`TestClient(app)`", "Exécute des requêtes HTTP de test en mémoire via ASGI sans ouvrir de port", "Obligé de lancer `uvicorn` manuellement pour tester ses routes"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Nommer son propre fichier `fastapi.py` ou `uvicorn.py` dans le dossier de travail",
                "good": "Nommer ses fichiers `app.py`, `main.py` ou `01_serveur_minimal_fastapi.py`",
                "why": "Si votre fichier s'appelle `fastapi.py`, l'instruction `from fastapi import FastAPI` importera votre propre fichier au lieu de la bibliothèque FastAPI (`ImportError`) !"
            },
            {
                "bad": "Appeler une bibliothèque réseau synchrone bloquante (`time.sleep(5)`) à l'intérieur d'une fonction `async def`",
                "good": "Utiliser `await asyncio.sleep(...)` / `httpx.AsyncClient` dans `async def`, ou déclarer la route avec `def` standard (que FastAPI exécute dans un threadpool)",
                "why": "Un appel bloquant synchrone dans `async def` fige la boucle d'événements `asyncio` d'Uvicorn pour tous les clients !"
            }
        ],
        "practical_exercises": [
            "Exécutez le code dans l'atelier ci-dessus pour inspecter le contenu réel de `app.routes` avec `TestClient(app)`.",
            "Ajoutez une route `@app.get(\"/api/v1/version\")` dans l'exécuteur et vérifiez qu'elle apparaît immédiatement dans la table de routage ASGI."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.2 : MATURITÉ REST (RICHARDSON) & PARAMÈTRES TYPÉS FASTAPI
    # =========================================================================
    "d2-l2": {
        "context": (
            "N'importe qui peut créer une URL `/api/faireQuelqueChose` qui renvoie du JSON, mais cela n'en fait pas "
            "une API **RESTful** professionnelle.\n"
            "Comment les géants technologiques (Stripe, GitHub, Twilio, Google Cloud) nomment-ils leurs URLs pour "
            "qu'un développeur externe comprenne intuitivement toute l'API en 5 minutes ? Et comment extraire "
            "et valider proprement un identifiant d'entité (`/formations/42`) ou un critère de recherche (`?salle=Alger`) dans "
            "FastAPI ? Ce chapitre formalise le **Modèle de Maturité de Richardson** et le système déclaratif de paramètres `Path(...)` et `Query(...)`."
        ),
        "deep_sections": [
            {
                "heading": "1. Le Modèle de Maturité de Richardson (Niveaux 0, 1, 2 et 3)",
                "body": (
                    "Élaboré par Leonard Richardson, ce modèle évalue la qualité architecturale d'une API Web sur 4 niveaux :\n"
                    "- **Niveau 0 (Le marécage du POX / RPC)** : Une seule URL (`POST /api/service`) reçoit des ordres disparates "
                    "(`{\"action\": \"getFormation\"}`, `{\"action\": \"deleteFormation\"}`). Le protocole HTTP est sous-exploité.\n"
                    "- **Niveau 1 (Les Ressources nominales)** : Chaque entité métier possède sa propre adresse URL utilisant "
                    "un **nom au pluriel** (`/api/v1/formations`, `/api/v1/formations/42`), mais on utilise encore souvent `POST` ou `GET` pour tout.\n"
                    "- **Niveau 2 (Verbes HTTP + Codes de Statut — Le Standard Industriel)** : L'URL identifie la ressource "
                    "(`/api/v1/formations/42`) et le **verbe HTTP** exprime l'action (`@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete`), "
                    "tandis que la réponse utilise le code de statut exact (`200`, `201`, `404`, `422`).\n"
                    "- **Niveau 3 (HATEOAS)** : La réponse JSON inclut en plus des liens de navigation (`\"links\": {\"self\": \"/api/v1/formations/42\"}`)."
                )
            },
            {
                "heading": "2. Path Parameters (`{id}: int`) vs Query Parameters (`Query(...)`) : la règle de décision",
                "body": (
                    "Quand faut-il mettre un paramètre dans le chemin (`/formations/42`) et quand faut-il le mettre après `?` (`?salle=Alger`) ?\n"
                    "- **Paramètre de Chemin (`Path Parameter` : `@app.get('/api/formations/{formation_id}')`)** : Utilisé pour "
                    "**identifier de manière unique une ressource précise**. Si l'identifiant n'existe pas en base, la route lève "
                    "`raise HTTPException(status_code=404)`. Grâce à l'annotation `formation_id: int`, FastAPI et Pydantic valident automatiquement "
                    "que la valeur est un entier (et renvoient `422 Unprocessable Entity` si le client envoie `/formations/abc`).\n"
                    "- **Paramètre de Requête (`Query Parameter` : `/api/formations?salle=Alger&duree_min=3`)** : Tout paramètre de la fonction Python "
                    "qui ne figure pas entre `{...}` dans le chemin est automatiquement lu dans la Query String ! Si aucune formation ne correspond au filtre, "
                    "la collection renvoie **`200 OK` avec une liste vide `[]`**."
                )
            },
            {
                "heading": "3. Validation déclarative avec `Path(ge=1)` et `Query(default=..., ge=..., le=...)`",
                "body": (
                    "Au lieu d'écrire manuellement des blocs `try / except ValueError` et des tests `if duree_min < 1:`, FastAPI "
                    "permet de déclarer les contraintes directement dans la signature :\n"
                    "- `stagiaire_id: int = Path(..., ge=1, description=\"ID unique du stagiaire\")`\n"
                    "- `ht: float = Query(1000.0, gt=0, description=\"Montant HT (> 0)\")`\n"
                    "Pydantic convertit la chaîne d'URL en `int`/`float`, vérifie les bornes (`ge`, `le`, `gt`) et documente "
                    "automatiquement ces règles dans Swagger UI (`/docs`)."
                )
            },
            {
                "heading": "4. Pourquoi voit-on `{variable}`, `<variable>` et `:variable` selon les outils et frameworks ?",
                "body": (
                    "En lisant des documentations d'API ou en utilisant différents outils, on rencontre trois notations pour une **variable de chemin** :\n"
                    "1. **`{variable}` (Syntaxe native de FastAPI, Starlette, OpenAPI 3.1 / Swagger, Spring Boot & f-strings Python)** :\n"
                    "   - Utilise des accolades `{...}` côté serveur Python : `@app.get(\"/api/formations/{formation_id}\")`.\n"
                    "   - Le type est déclaré par le *type hint* Python : `def lire(formation_id: int):`.\n"
                    "2. **`<variable>` et `<int:variable>` (Syntaxe historique Flask / Werkzeug & Django)** :\n"
                    "   - Utilise des chevrons `<int:id>`. **Attention** : dans FastAPI, n'utilisez jamais `<int:id>`, utilisez toujours `{id}` avec `id: int` !\n"
                    "3. **`:variable` (Syntaxe Postman, Express.js / Node.js, Ruby on Rails, Go Gin)** :\n"
                    "   - Dans **Postman**, taper `http://127.0.0.1:8000/api/formations/:id` fait apparaître la clé `id` dans la table *Path Variables*."
                )
            }
        ],
        "architecture_diagram": (
            "1. COMPARAISON ARCHITECTURALE : ANTI-PATTERN RPC vs STANDARD REST (NIVEAU 2)\n"
            "  [ANTI-PATTERN RPC]                       [STANDARD RESTFUL (Noms au pluriel + Verbes HTTP)]\n"
            "  GET  /api/getAllFormations       ===>    GET    /api/v1/formations\n"
            "  GET  /api/getFormationById?id=5  ===>    GET    /api/v1/formations/5\n"
            "  POST /api/createNewFormation     ===>    POST   /api/v1/formations\n"
            "  POST /api/updateFormation/5      ===>    PUT    /api/v1/formations/5\n"
            "  GET  /api/deleteFormation?id=5   ===>    DELETE /api/v1/formations/5\n\n"
            "2. TRADUCTION D'UNE VARIABLE DE CHEMIN SELON L'OUTIL :\n"
            "  - Dans le code serveur FastAPI : @app.get(\"/api/v1/formations/{id}\") (id: int) <-- Accolades {...}\n"
            "  - Dans le code serveur Flask   : @app.route(\"/api/v1/formations/<int:id>\")     <-- Chevrons <...>\n"
            "  - Dans l'interface Postman     : GET http://.../api/v1/formations/:id          <-- Deux-points :id\n"
            "  - Dans curl / Navigateur       : curl http://.../api/v1/formations/42          <-- Valeur réelle 42"
        ),
        "reference_table": {
            "title": "Synthèse : Extraction Déclarative dans FastAPI & Notations des Variables d'URL",
            "headers": ["Élément / Syntaxe", "Où est-il utilisé ?", "Exemple concret", "Comportement & Règle d'or"],
            "rows": [
                ["`{id}` + `id: int = Path(...)`", "**FastAPI (Starlette)** & **OpenAPI 3.1**", "`@app.get('/api/formations/{id}')`", "Valide le type (`int`, `float`, `UUID`, `str`) via Pydantic (`422` si invalide)"],
                ["`<int:id>`", "**Flask (Werkzeug)** & Django", "`@app.route('/api/formations/<int:id>')`", "Syntaxe propre à Flask (non reconnue par FastAPI)"],
                ["`:id`", "**Postman**, Express.js (Node), Rails", "`/api/formations/:id`", "Crée une variable de chemin dans Postman"],
                ["`Query(...)`", "Query String (après `?`)", "`page: int = Query(1, ge=1)`", "Extrait, convertit et valide les paramètres `?page=1`"],
                ["`Header(...)`", "En-têtes HTTP (`Headers`)", "`x_api_key: str = Header(alias='X-API-Key')`", "Extrait et valide un en-tête HTTP"],
                ["`payload: BaseModel`", "Corps (`Body` JSON)", "`def creer(payload: FormationCreate):`", "Parse et valide le corps JSON entrant via Pydantic v2"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écrire `@app.get('/api/formations/<int:id>')` ou `:id` dans une route FastAPI",
                "good": "Toujours utiliser les accolades `@app.get('/api/formations/{id}')` avec l'annotation `id: int` dans FastAPI",
                "why": "FastAPI utilise la syntaxe standard OpenAPI `{id}` et délègue la conversion de type à l'annotation Python `id: int`."
            },
            {
                "bad": "Mettre des verbes d'action dans les URLs : `/api/creer_formation`, `/api/listerFormations`",
                "good": "Utiliser uniquement des noms de ressources au pluriel (`/api/formations`) et laisser le décorateur (`@app.post`, `@app.get`) définir l'action",
                "why": "Respecter le Niveau 2 de Richardson évite la prolifération de centaines d'URLs incohérentes."
            },
            {
                "bad": "Renvoyer `404 Not Found` lorsqu'une recherche filtrée `GET /api/formations?salle=Tamanrasset` ne trouve aucun résultat",
                "good": "Renvoyer `200 OK` avec `{\"total\": 0, \"formations\": []}`",
                "why": "`404` sur une collection ferait croire au client que la route `/api/formations` n'existe plus ; une liste vide `[]` indique clairement qu'il n'y a aucun résultat pour ce filtre."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur ci-dessus, observez comment `client.get('/api/v1/stagiaires/abc')` déclenche automatiquement une réponse `422 Unprocessable Entity` générée par Pydantic.",
            "Testez la route réelle `GET /api/sandbox/calcul-tva?ht=2500&taux=19` dans le Client HTTP ou avec `curl`."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.3 : PAGINATION (OFFSET/LIMIT), FILTRAGE & TRI
    # =========================================================================
    "d2-l3": {
        "context": (
            "En développement local, votre table SQLite contient 4 formations : faire `SELECT * FROM formations` et "
            "tout renvoyer d'un bloc prend 1 milliseconde. Mais que se passe-t-il six mois après la mise en production "
            "lorsque la table des transactions ou des journaux contient **2 000 000 de lignes** ?\n"
            "Une requête `GET` sans pagination tentera de charger les 2 millions de lignes en RAM Python, de construire "
            "un fichier JSON de 800 Mo et fera s'écrouler le serveur par manque de mémoire (*Out Of Memory / OOM*). "
            "La **Pagination**, le **Filtrage** et le **Tri sécurisé** sont donc obligatoires sur toute route de collection."
        ),
        "deep_sections": [
            {
                "heading": "1. L'équation mathématique de la Pagination Offset / Limit",
                "body": (
                    "Le standard universel de pagination repose sur deux paramètres passés dans la Query String : **`page`** "
                    "(le numéro de page souhaité, commençant à `1`) et **`limit`** (le nombre d'éléments par page, par exemple `10` ou `20`).\n"
                    "- Pour savoir combien d'éléments sauter depuis le début de la collection (**`offset`**), on applique la formule :\n"
                    "  **`offset = (page - 1) * limit`**\n"
                    "  - Pour la `page=1` avec `limit=10` : `offset = (1 - 1) * 10 = 0` → éléments d'indices `0` à `9`.\n"
                    "  - Pour la `page=2` avec `limit=10` : `offset = (2 - 1) * 10 = 10` → éléments d'indices `10` à `19`.\n"
                    "  - Pour la `page=3` avec `limit=10` : `offset = (3 - 1) * 10 = 20` → éléments d'indices `20` à `29`.\n"
                    "- Pour calculer le nombre total de pages (**`total_pages`**) par division entière par excès (plafond) :\n"
                    "  **`total_pages = max(1, (total_items + limit - 1) // limit)`**."
                )
            },
            {
                "heading": "2. Pourquoi borner impérativement `page` et `limit` côté serveur avec `Query(ge=..., le=...)`",
                "body": (
                    "Si vous déclarez simplement `limit: int = 10` sans bornes, qu'arrive-t-il si un "
                    "utilisateur malveillant appelle `?page=-5&limit=999999999` ?\n"
                    "- Un `page` négatif produirait un `offset` négatif incohérent.\n"
                    "- Un `limit` de 1 milliard contournerait toute votre protection de pagination !\n"
                    "Dans FastAPI, on encadre donc toujours les deux paramètres avec `Query` :\n"
                    "- `page: int = Query(1, ge=1)` (au minimum page 1, sinon `422`).\n"
                    "- `limit: int = Query(10, ge=1, le=50)` (entre 1 et 50 éléments maximum par appel)."
                )
            },
            {
                "heading": "3. Validation par Liste Blanche (Whitelist) du Tri Dynamique (`?tri=...&ordre=...`)",
                "body": (
                    "Pour permettre au client de trier les résultats (`?tri=duree_jours&ordre=desc`), le serveur ne doit "
                    "**jamais** utiliser directement la chaîne envoyée par le client comme nom de clé ou colonne SQL sans vérification.\n"
                    "On définit un tuple immuable de colonnes autorisées :\n"
                    "`CHAMPS_TRI_AUTORISES = (\"id\", \"duree_jours\", \"titre\")`.\n"
                    "Si `tri not in CHAMPS_TRI_AUTORISES`, le serveur rejette immédiatement la requête avec `raise HTTPException(status_code=400, detail=...)`."
                )
            }
        ],
        "architecture_diagram": (
            "PIPELINE DE TRAITEMENT D'UNE COLLECTION REST (GET /api/formations?salle=Alger&tri=duree_jours&ordre=desc&page=2&limit=2)\n\n"
            "  [Collection Complète (N éléments)] \n"
            "          |\n"
            "          v  1. FILTRAGE (?salle=Alger)\n"
            "  [Sous-ensemble filtré (total_items = 5)]\n"
            "          |\n"
            "          v  2. TRI SÉCURISÉ (?tri=duree_jours&ordre=desc via Whitelist)\n"
            "  [Sous-ensemble filtré et trié (5 éléments)]\n"
            "          |\n"
            "          v  3. DÉCOUPAGE PAGINATION (offset = (2-1)*2 = 2, tranche [2 : 4])\n"
            "  [Réponse JSON : {\"meta\": {\"total_items\": 5, \"page\": 2, \"total_pages\": 3, \"has_next\": true}, \"data\": [elem2, elem3]}]"
        ),
        "reference_table": {
            "title": "Structure Standard de l'Objet `meta` de Pagination dans une Réponse JSON",
            "headers": ["Clé JSON dans `meta`", "Type", "Formule de calcul en Python", "Utilité pour l'interface cliente (Web / Mobile)"],
            "rows": [
                ["`total_items`", "`int`", "`len(resultats_filtres)` ou `SELECT COUNT(*)`", "Afficher « 48 formations trouvées »"],
                ["`page`", "`int`", "`max(1, request.args.get('page', 1, type=int))`", "Mettre en surbrillance le numéro de page courant"],
                ["`limit`", "`int`", "`min(50, max(1, request.args.get('limit', 10, type=int)))`", "Connaître la taille de tranche appliquée"],
                ["`total_pages`", "`int`", "`max(1, (total_items + limit - 1) // limit)`", "Générer les boutons de pagination « Page 1 sur 5 »"],
                ["`has_next`", "`bool`", "`page < total_pages`", "Activer ou griser le bouton « Page suivante »"],
                ["`has_prev`", "`bool`", "`page > 1`", "Activer ou griser le bouton « Page précédente »"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Calculer `total_items` APRES avoir découpé la tranche `tranche = resultats[offset:offset+limit]`",
                "good": "Calculer `total_items = len(resultats)` sur les résultats filtrés AVANT le découpage de la page",
                "why": "Sinon `total_items` vaudra toujours `limit` (ex: 2) au lieu du nombre total réel d'enregistrements correspondant à la recherche !"
            },
            {
                "bad": "Trier AVANT de filtrer sur de grands volumes de données",
                "good": "Toujours **Filtrer d'abord**, puis **Trier**, puis **Paginer**",
                "why": "Trier 100 000 lignes pour n'en garder que 10 après filtrage gaspille 99 % du temps processeur."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur Python ci-dessus, testez la pagination sur la `page = 2` puis la `page = 3` avec `limit = 2`.",
            "Cliquez sur le bouton « Tester avec Pagination & Tri » pour exécuter `GET /api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc`."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.4 : MIDDLEWARE HTTP ASYNCHRONE (@APP.MIDDLEWARE("HTTP"))
    # =========================================================================
    "d2-l4": {
        "context": (
            "Lorsqu'une API compte 50 routes, comment mesurer le temps d'exécution exact en millisecondes de chaque "
            "appel, attribuer un numéro de suivi unique (`X-Request-ID`) et ajouter des en-têtes de sécurité sans "
            "copier-coller les mêmes lignes dans les 50 fonctions ?\n"
            "La réponse architecturale s'appelle un **Middleware HTTP**. Dans FastAPI, le décorateur "
            "**`@app.middleware(\"http\")`** permet d'envelopper 100 % du trafic autour de l'instruction `response = await call_next(request)`."
        ),
        "deep_sections": [
            {
                "heading": "1. Les 3 phases du Cycle de Vie d'une Requête dans un Middleware FastAPI",
                "body": (
                    "Chaque requête HTTP qui franchit la porte de FastAPI traverse séquentiellement trois étapes dans `async def middleware(request: Request, call_next):` :\n"
                    "1. **Phase Prétraitement (Avant `await call_next(request)`)** : S'exécute **avant** la fonction de route. Idéal "
                    "pour démarrer un chronomètre haute précision (`time.perf_counter()`), extraire ou générer un `X-Request-ID`, "
                    "ou bloquer globalement une requête (en retournant directement un `JSONResponse`).\n"
                    "2. **Phase Métier (`response = await call_next(request)`)** : Passe le relais au routeur Starlette/FastAPI et attend la réponse de la route ciblée.\n"
                    "3. **Phase Post-traitement (Après `await call_next(request)`)** : Reçoit l'objet `response` juste avant son départ "
                    "sur le réseau. Permet d'injecter les en-têtes `X-Request-ID`, `X-Response-Time-Ms`, `X-Content-Type-Options: nosniff` "
                    "et d'écrire une ligne d'audit dans les journaux du serveur. Elle doit **toujours retourner `response`**."
                )
            },
            {
                "heading": "2. Pourquoi utiliser `request.state` plutôt qu'une variable globale Python ?",
                "body": (
                    "Comment transmettre l'identifiant `request_id` généré dans le middleware à la fonction de route ?\n"
                    "- **Danger d'une variable globale** : Sur un serveur asynchrone où plusieurs requêtes s'exécutent de manière "
                    "concurrente sur la même boucle d'événements, une variable globale serait écrasée par une autre requête (*Race Condition*) !\n"
                    "- **La solution `request.state`** : L'attribut `request.state` de Starlette/FastAPI est un espace mémoire **attaché uniquement à la requête courante**. "
                    "Ce que le middleware écrit dans `request.state.request_id` est isolé pour cette requête et accessible dans la route."
                )
            },
            {
                "heading": "3. L'importance industrielle du `X-Request-ID` (Correlation ID)",
                "body": (
                    "Lorsqu'un client partenaire vous signale : *« J'ai reçu une erreur hier à 14h12 »*, chercher dans un "
                    "fichier de log contenant 500 000 lignes est un cauchemar.\n"
                    "Avec un identifiant unique **`X-Request-ID`** (par exemple `req-8f91a2b3c4d5` généré par `uuid.uuid4()`) "
                    "renvoyé dans les en-têtes HTTP de chaque réponse ET inscrit dans chaque ligne de log serveur, il suffit "
                    "d'un simple `grep req-8f91a2b3c4d5 app.log` pour retrouver instantanément toute l'exécution correspondante."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE VIE COMPLET D'UNE REQUÊTE AVEC @app.middleware(\"http\") FASTAPI :\n\n"
            "  Requête HTTP Entrante\n"
            "          |\n"
            "          v\n"
            "  +------------------------------------------------------------------+\n"
            "  | 1. Avant await call_next(request)                                |\n"
            "  |    -> heure_debut = time.perf_counter()                          |\n"
            "  |    -> request.state.request_id = \"req-a1b2c3d4\"                  |\n"
            "  +------------------------------------------------------------------+\n"
            "          |\n"
            "          v  response = await call_next(request)\n"
            "  +------------------------------------------------------------------+\n"
            "  | 2. Route Métier (@app.get(\"/api/rapports\"))                      |\n"
            "  |    -> Exécute le calcul / SQL et construit l'objet Response      |\n"
            "  +------------------------------------------------------------------+\n"
            "          |\n"
            "          v\n"
            "  +------------------------------------------------------------------+\n"
            "  | 3. Après await call_next(request)                                |\n"
            "  |    -> Calcule duree_ms = (perf_counter() - heure_debut) * 1000   |\n"
            "  |    -> Ajoute Headers : X-Request-ID & X-Response-Time-Ms         |\n"
            "  |    -> Écrit le journal d'audit structuré et return response      |\n"
            "  +------------------------------------------------------------------+\n"
            "          |\n"
            "          v\n"
            "  Réponse HTTP Sortante vers le Client"
        ),
        "reference_table": {
            "title": "Comparatif des Mécanismes d'Interception du Cycle de Vie dans FastAPI",
            "headers": ["Mécanisme FastAPI", "Moment d'exécution", "Arguments reçus", "Valeur de retour attendue"],
            "rows": [
                ["`@app.middleware(\"http\")`", "Autour de chaque requête HTTP (avant et après `call_next`)", "`(request: Request, call_next)`", "**Obligatoirement** un objet `Response`"],
                ["`Depends(...)` (Dépendance)", "Avant l'entrée dans les routes ciblées", "Paramètres HTTP (`Header`, `Query`, `Request`)", "Valeur injectée dans la route (ou `yield` avec nettoyage)"],
                ["`lifespan` (Context Manager)", "Au démarrage et à l'arrêt du serveur ASGI", "`(app: FastAPI)`", "`yield` (initialisation / fermeture globale)"],
                ["`@app.exception_handler(Exc)`", "Lorsqu'une exception HTTP ou métier survient", "`(request: Request, exc: Exc)`", "Un objet `JSONResponse` (ex: RFC 7807)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Oublier l'instruction `return response` à la fin d'une fonction `@app.middleware(\"http\")`",
                "good": "Toujours terminer `@app.middleware(\"http\")` par `return response`",
                "why": "Si le middleware ne retourne pas `response`, Starlette/Uvicorn ne peut envoyer aucune réponse HTTP au client !"
            },
            {
                "bad": "Utiliser `time.time()` pour mesurer des durées d'exécution de quelques millisecondes",
                "good": "Utiliser l'horloge monotone haute précision `time.perf_counter()`",
                "why": "`time.perf_counter()` offre une résolution à la nanoseconde et n'est jamais faussé par les ajustements d'horloge NTP du système."
            }
        ],
        "practical_exercises": [
            "Exécutez le script `day_2/04_middlewares_et_audit_log.py` dans l'atelier ci-dessus pour observer l'injection automatique de `X-Request-ID` et `X-Response-Time-Ms`.",
            "Modifiez l'appel simulé dans l'atelier pour passer un en-tête personnalisé `headers={'X-Request-ID': 'trace-isgp-001'}` et vérifiez que le serveur conserve cet identifiant."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.5 : TEMPLATES JINJA2 (JINJA2TEMPLATES) & FORMULAIRES HTML (FORM / UPLOADFILE)
    # =========================================================================
    "d2-l5": {
        "context": (
            "Un service Web complet en entreprise ne se limite pas toujours à des échanges JSON entre machines : "
            "très souvent, l'application FastAPI doit aussi afficher un **portail d'administration**, une **page de connexion** "
            "ou un **formulaire de saisie** pour des opérateurs humains.\n"
            "Or, deux erreurs reviennent constamment chez les développeurs débutants :\n"
            "1. **Coder du HTML en dur dans les fichiers Python (`return f\"<h1>{titre}</h1>\"`)**, ce qui mélange la logique "
            "métier et la présentation tout en ouvrant une faille critique d'injection JavaScript (**XSS — Cross-Site Scripting**).\n"
            "2. **Essayer de lire un formulaire HTML `<form method=\"POST\">` avec un `BaseModel` JSON**, ce qui échoue "
            "car un navigateur soumettant un formulaire HTML n'envoie **pas** du JSON, mais le format "
            "`application/x-www-form-urlencoded` déclaré avec **`Form(...)`** (ou `multipart/form-data` avec **`UploadFile = File(...)`**) !"
        ),
        "deep_sections": [
            {
                "heading": "1. `Jinja2Templates` de FastAPI et la protection automatique Anti-XSS",
                "body": (
                    "Dans FastAPI, on ne construit **jamais** une page HTML par concaténation de chaînes dans le fichier `.py`. "
                    "Tous les fichiers HTML sont placés dans le dossier dédié **`templates/`** et rendus par **`templates.TemplateResponse(request=request, name=\"fichier.html\", context={...})`** :\n"
                    "- **Les expressions `{{ variable }}`** : Évaluent une variable ou un attribut Python (`{{ f.titre }}`) et l'insèrent dans la page.\n"
                    "- **Sécurité automatique contre les failles XSS (*Auto-Escaping*)** : Si un attaquant saisit `<script>alert('Piraté')</script>` "
                    "comme titre de formation, une f-string Python `f\"<td>{titre}</td>\"` exécuterait le script malveillant dans le navigateur de "
                    "tous les visiteurs ! À l'inverse, **Jinja2 échappe automatiquement** les caractères spéciaux en `&lt;script&gt;...`, neutralisant l'attaque.\n"
                    "- **Les structures de contrôle `{% ... %}`** : Permettent d'écrire des boucles (`{% for f in formations %} ... {% endfor %}`), "
                    "des conditions (`{% if erreurs %} ... {% endif %}`) et de l'héritage de mise en page."
                )
            },
            {
                "heading": "2. Anatomie d'un Formulaire HTML (`<form method=\"POST\">`) : `Form(...)` vs `BaseModel` JSON",
                "body": (
                    "Comprenons exactement ce qu'envoie un navigateur Web lorsqu'un utilisateur remplit un formulaire `<form method=\"POST\" action=\"/formations\">` :\n"
                    "- Chaque champ `<input name=\"titre\">`, `<input name=\"duree_jours\">`, `<select name=\"salle\">` est identifié par son attribut **`name=\"...\"`** "
                    "(attention : l'attribut `id=\"...\"` ne sert qu'au CSS/JavaScript et n'est **jamais** envoyé au serveur !).\n"
                    "- Au clic sur `<button type=\"submit\">`, le navigateur assemble une chaîne de paires `cle=valeur` séparées par `&` :\n"
                    "  `titre=Architecture+API&duree_jours=5&salle=Salle+A`\n"
                    "  accompagnée de l'en-tête HTTP : **`Content-Type: application/x-www-form-urlencoded`**.\n"
                    "- Côté FastAPI :\n"
                    "  - On déclare les champs du formulaire dans la signature de la route avec **`titre: str = Form(...)`** et **`duree_jours: str = Form(...)`** (ou `await request.form()`)."
                )
            },
            {
                "heading": "3. Envoi de Fichiers (`multipart/form-data` -> `UploadFile = File(None)`) et Assainissement du Nom",
                "body": (
                    "Deux mécanismes complémentaires sont indispensables pour maîtriser les formulaires en production :\n"
                    "1. **Upload de fichiers (`enctype=\"multipart/form-data\"`)** : Dès qu'un formulaire contient `<input type=\"file\" name=\"document_pdf\">`, "
                    "on ajoute `enctype=\"multipart/form-data\"` sur la balise `<form>`. FastAPI extrait les champs texte via `Form(...)` et les fichiers "
                    "binaires via **`document_pdf: UploadFile | None = File(default=None)`**. Avant d'enregistrer le fichier sur le disque (`await document_pdf.read()`), il est "
                    "obligatoire d'assainir son nom (`os.path.basename` + filtre alphanumérique) pour bloquer toute attaque *Path Traversal* (`../../etc/passwd`).\n"
                    "2. **Le Patron `PRG` (*Post / Redirect / Get*)** : Après un `POST` réussi depuis un navigateur, renvoyer `RedirectResponse(url=\"/formations\", status_code=303)` "
                    "évite que l'utilisateur ne soumette le formulaire une seconde fois en appuyant sur la touche `F5` (Actualiser)."
                )
            }
        ],
        "architecture_diagram": (
            "COMPARAISON DES 3 FORMATS D'ENVOI POST ET LEUR LECTURE DANS FASTAPI\n"
            "===================================================================\n\n"
            "  [1] FORMULAIRE HTML CLASSIQUE (<form method=\"POST\">)\n"
            "      Header  : Content-Type: application/x-www-form-urlencoded\n"
            "      Body    : titre=API+FastAPI&duree_jours=5&salle=Salle+A\n"
            "      FastAPI : titre: str = Form(...)  |  Réponse : templates.TemplateResponse(...)\n\n"
            "  [2] FORMULAIRE HTML AVEC FICHIER (<form method=\"POST\" enctype=\"multipart/form-data\">)\n"
            "      Header  : Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...\n"
            "      FastAPI : Texte -> Form(...)  +  Fichier -> document_pdf: UploadFile = File(None)\n\n"
            "  [3] CLIENT API / FETCH JAVASCRIPT / MOBILE\n"
            "      Header  : Content-Type: application/json\n"
            "      Body    : {\"titre\": \"API FastAPI\", \"duree_jours\": 5, \"salle\": \"Salle A\"}\n"
            "      FastAPI : payload: FormationCreate (BaseModel)  |  Réponse : JSON 201 Created"
        ),
        "reference_table": {
            "title": "Tableau Comparatif : Formulaires Web HTML (`Form` / `Jinja2Templates`) vs API JSON (`BaseModel`)",
            "headers": ["Caractéristique", "Formulaire HTML Classique", "Formulaire avec Fichier (Upload)", "Requête API REST (JSON)"],
            "rows": [
                ["En-tête `Content-Type`", "`application/x-www-form-urlencoded`", "`multipart/form-data`", "`application/json`"],
                ["Déclaration dans FastAPI", "`champ: str = Form(...)`", "`Form(...)` + `fichier: UploadFile = File(...)`", "`payload: BaseModel`"],
                ["Attribut HTML obligatoire", "`<input name=\"champ\">` (`name` et non `id`)", "`<form enctype=\"multipart/form-data\">`", "Clé de l'objet JSON `{\"champ\": ...}`"],
                ["Réponse FastAPI", "`templates.TemplateResponse(...)` (`HTMLResponse`)", "`TemplateResponse` ou `dict` JSON", "`return {...}` (`status_code=201`)"],
                ["Commande `curl` équivalente", "`curl -X POST -d \"titre=FastAPI&jours=5\" URL`", "`curl -X POST -F \"doc=@cours.pdf\" URL`", "`curl -X POST -H \"Content-Type: application/json\" -d '{...}' URL`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écrire du HTML en dur dans Python (`return HTMLResponse(f'<h1>Bonjour {nom}</h1>')`) au lieu d'utiliser `Jinja2Templates`",
                "good": "Placer tout le HTML dans `templates/fichier.html` et utiliser `templates.TemplateResponse(request, 'fichier.html', {'nom': nom})`",
                "why": "La concaténation HTML dans Python rend le code ingérable et expose l'application aux injections JavaScript (XSS), alors que Jinja2 échappe automatiquement les variables `{{ nom }}`."
            },
            {
                "bad": "Mettre uniquement `<input id=\"titre\">` dans un formulaire HTML en oubliant l'attribut `name=\"titre\"`",
                "good": "Toujours définir l'attribut `name=\"titre\"` sur chaque `<input>`, `<select>` et `<textarea>`",
                "why": "Le navigateur n'envoie au serveur que les champs possédant un attribut `name` ; sans `name`, le champ n'est jamais transmis !"
            },
            {
                "bad": "Utiliser un `BaseModel` JSON standard pour recevoir les données d'un `<form method=\"POST\">` HTML",
                "good": "Utiliser `Form(...)` pour un formulaire HTML (ou inspecter `request.headers.get('content-type')`)",
                "why": "Un formulaire HTML envoie `application/x-www-form-urlencoded` et non `application/json`."
            }
        ],
        "practical_exercises": [
            "Ouvrez l'atelier interactif réel sur `/sandbox/formulaire-jinja` (bouton ci-dessous ou dans la barre d'outils), soumettez une nouvelle formation via le formulaire HTML et observez la trame `application/x-www-form-urlencoded` reçue.",
            "Testez également un envoi invalide (durée négative ou titre d'une seule lettre) pour observer comment la boucle Jinja2 `{% for err in erreurs %}` affiche les erreurs côté serveur."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.1 : CRUD MÉMOIRE, PYDANTIC V2 & RFC 7807 (400 vs 422)
    # =========================================================================
    "d3-l1": {
        "context": (
            "Jusqu'ici, notre serveur répondait principalement à des requêtes de consultation (`GET`). Dès que l'on "
            "autorise les clients à **créer (`POST`)**, **modifier (`PUT`/`PATCH`)** et **supprimer (`DELETE`)** des "
            "données (les 4 opérations **CRUD**), une règle cardinale de sécurité entre en jeu : **Ne jamais faire "
            "confiance aux données envoyées par le client (*Never Trust User Input*)**.\n"
            "Un client peut envoyer un JSON cassé, oublier un champ obligatoire, envoyer un texte à la place d'un "
            "nombre ou tenter de créer une formation de `-15` jours. Ce chapitre enseigne comment valider rigoureusement "
            "les payloads entrants avec **Pydantic v2 (`BaseModel`, `Field`, `@field_validator`)** et structurer les réponses d'erreur selon la norme internationale **RFC 7807 (Problem Details)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Validation Déclarative par Schéma avec Pydantic v2 (`BaseModel` & `Field`)",
                "body": (
                    "Dans FastAPI, on définit la structure exacte attendue d'un corps JSON à l'aide d'une classe héritant de `pydantic.BaseModel` :\n"
                    "- `titre: str = Field(..., min_length=3, max_length=120)` : Champ obligatoire (`...`) de 3 à 120 caractères.\n"
                    "- `duree_jours: int = Field(..., ge=1, le=30)` : Entier obligatoire compris entre `1` et `30` inclus.\n"
                    "- `@field_validator(\"titre\")` : Permet d'exécuter une règle métier personnalisée (ex: `.strip()` et rejet d'une chaîne composée uniquement d'espaces)."
                )
            },
            {
                "heading": "2. Pourquoi collecter TOUTES les erreurs de validation plutôt que de s'arrêter à la première ?",
                "body": (
                    "Imaginez un formulaire de création comportant 5 champs dont 3 sont erronés. Si votre API s'arrête dès "
                    "le 1er champ invalide, l'utilisateur corrige le 1er champ, renvoie la requête, découvre que le 2ème est "
                    "faux, corrige le 2ème, renvoie la requête et découvre que le 3ème est faux !\n"
                    "Pydantic évalue tous les champs du modèle en une seule passe et regroupe toutes les anomalies dans `exc.errors()`, "
                    "permettant de renvoyer la liste exhaustive des champs en erreur avec le code **`422 Unprocessable Entity`**."
                )
            },
            {
                "heading": "3. Le Standard International RFC 7807 (`Problem Details for HTTP APIs`)",
                "body": (
                    "Pour éviter que chaque équipe n'invente son propre format d'erreur (`{\"err\": ...}`, `{\"message\": ...}`, "
                    "`{\"fault\": ...}`), l'IETF a publié la norme **RFC 7807 / RFC 9457** (`media_type=\"application/problem+json\"`). Une erreur normalisée contient :\n"
                    "- `type` : URI identifiant la catégorie d'erreur (ex: `https://api.isgp.dz/erreurs/validation`).\n"
                    "- `title` : Résumé lisible du problème.\n"
                    "- `status` : Répétition du code HTTP numérique (`422`).\n"
                    "- `errors` : Liste détaillée des champs invalides (`[{\"champ\": \"duree_jours\", \"message\": \"...\"}]`)."
                )
            }
        ],
        "architecture_diagram": (
            "ENTONNOIR DE VALIDATION DÉFENSIVE D'UNE REQUÊTE POST / PUT :\n\n"
            "  Requête POST entrante\n"
            "        |\n"
            "        +---> 1. Le Body est-il un objet JSON syntaxiquement valide ?\n"
            "        |        NON ---> Retour immédiat : HTTP 400 Bad Request (Syntaxe illisible)\n"
            "        |\n"
            "        +---> 2. Les champs respectent-ils les types et bornes métier (len >= 3, 1 <= duree <= 30) ?\n"
            "        |        NON ---> Retour immédiat : HTTP 422 Unprocessable Entity (Format RFC 7807 + liste 'errors')\n"
            "        |\n"
            "        v     3. OUI ---> Insertion en base + Retour HTTP 201 Created + En-tête Location"
        ),
        "reference_table": {
            "title": "Distinction Précise des Codes HTTP lors de la Création / Validation (`POST`)",
            "headers": ["Code HTTP", "Situation précise", "Exemple d'entrée client", "Action attendue côté client"],
            "rows": [
                ["**`201 Created`**", "Création réussie de la ressource", "`{\"titre\": \"Architecture API\", \"duree_jours\": 5}`", "Lire la nouvelle ressource créée (et son nouvel `id`)"],
                ["**`400 Bad Request`**", "JSON cassé ou illisible", "`{\"titre\": \"API\",` (accolade fermante oubliée)", "Corriger la syntaxe JSON du programme client"],
                ["**`415 Unsupported Media Type`**", "En-tête `Content-Type` manquant ou erroné", "Envoi en `text/plain` au lieu de `application/json`", "Ajouter `-H \"Content-Type: application/json\"`"],
                ["**`422 Unprocessable Entity`**", "JSON valide mais règles métier violées", "`{\"titre\": \"AB\", \"duree_jours\": -5}`", "Afficher les messages de `errors` sur les champs du formulaire"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Supposer que parce que le Frontend JavaScript valide le formulaire, le Backend FastAPI n'a pas besoin de valider",
                "good": "Toujours appliquer 100 % des validations de types et de bornes dans le Backend Python avec Pydantic",
                "why": "Un attaquant utilise `curl` ou un script Python pour appeler directement votre API en contournant totalement l'interface Web !"
            },
            {
                "bad": "Renvoyer `200 OK` sur un `POST` qui crée un nouvel enregistrement",
                "good": "Renvoyer `201 Created` (`status_code=201`) accompagné de l'en-tête `Location: /api/formations/{new_id}`",
                "why": "`201 Created` indique explicitement qu'un nouvel état a été persisté avec succès."
            }
        ],
        "practical_exercises": [
            "Exécutez le script dans l'atelier ci-dessus pour observer la réponse RFC 7807 complète lorsqu'un client envoie un titre trop court et une durée négative.",
            "Cliquez sur « Tester POST /api/sandbox/formations » pour créer une nouvelle formation dans la base du laboratoire."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.2 : PUT VS PATCH & IDEMPOTENCE POST (IDEMPOTENCY-KEY)
    # =========================================================================
    "d3-l2": {
        "context": (
            "Deux questions d'architecture reviennent systématiquement lors de la conception d'APIs professionnelles "
            "(notamment dans la finance, le e-commerce et l'administration) :\n"
            "1. **Quelle est la différence exacte entre `PUT` et `PATCH` pour modifier une ressource existante ?**\n"
            "2. **Comment empêcher qu'un client qui clique deux fois sur « Payer » (ou dont le réseau 4G coupe et "
            "réessaie automatiquement son `POST`) ne soit débité deux fois ?**\n"
            "Ce chapitre apporte la réponse complète et l'implémentation de référence en Python/FastAPI."
        ),
        "deep_sections": [
            {
                "heading": "1. Remplacement Intégral (`PUT`) vs Modification Partielle (`PATCH` — RFC 5789)",
                "body": (
                    "Supposons que la formation `#1` contienne : `{\"id\": 1, \"titre\": \"FastAPI\", \"duree_jours\": 5, \"salle\": \"Labo 1\"}`.\n"
                    "- **Avec `PUT /api/v1/formations/1`** : La sémantique officielle de `PUT` est « **Remplacer l'intégralité "
                    "de la fiche #1 par le document fourni** ». Le client doit donc envoyer **tous les champs obligatoires** "
                    "(`titre`, `duree_jours`, `salle`). Tout champ non fourni est réinitialisé à sa valeur par défaut.\n"
                    "- **Avec `PATCH /api/v1/formations/1`** : La sémantique de `PATCH` est « **Appliquer une modification "
                    "partielle** ». Si vous voulez uniquement déménager la formation dans la `\"Salle B\"`, vous envoyez "
                    "uniquement `{\"salle\": \"Salle B\"}` : grâce à `payload.model_dump(exclude_unset=True)`, le serveur conserve le `titre` et la `duree_jours` intacts !"
                )
            },
            {
                "heading": "2. Le problème critique de la non-idempotence de `POST` sur les réseaux instables",
                "body": (
                    "Imaginez le scénario réel suivant :\n"
                    "1. Une application mobile envoie `POST /api/v1/paiements` (`{\"montant\": 25000}`).\n"
                    "2. Le serveur FastAPI reçoit la requête, débite les 25 000 DZD et renvoie `201 Created`.\n"
                    "3. Mais au moment où la réponse traverse le tunnel 4G du téléphone, la connexion coupe ! L'application "
                    "mobile reçoit une erreur `Network Timeout`.\n"
                    "4. L'application mobile ne sait pas si le serveur a reçu la requête ou non : elle renvoie donc le même "
                    "`POST /api/v1/paiements` par sécurité. Sans protection, le client est débité **deux fois (50 000 DZD)** !"
                )
            },
            {
                "heading": "3. La solution industrielle : l'en-tête `Idempotency-Key` (Standard IETF / Stripe)",
                "body": (
                    "Pour rendre `POST` idempotent sans jamais créer de doublon :\n"
                    "1. Avant d'envoyer sa requête `POST`, le client génère un identifiant unique (`UUID v4`, ex: `Idempotency-Key: tx-99812-a4b2`).\n"
                    "2. Lors du 1er appel, le serveur vérifie si `tx-99812-a4b2` existe dans son cache d'idempotence. Comme "
                    "elle est nouvelle, il exécute le paiement et **mémorise le résultat exact associé à cette clé**.\n"
                    "3. Si le client renvoie la même requête avec la même `Idempotency-Key: tx-99812-a4b2`, le serveur reconnaît "
                    "la clé, **n'exécute PAS une seconde fois le paiement**, et renvoie immédiatement la réponse initiale mise en cache !"
                )
            }
        ],
        "architecture_diagram": (
            "PROTECTION ANTI-DOUBLON PAR EN-TÊTE 'Idempotency-Key' SUR UN POST :\n\n"
            "  Appel #1 : POST /api/paiements (Header -> Idempotency-Key: uuid-123)\n"
            "     |---> Clé 'uuid-123' inconnue en cache\n"
            "     |---> Exécute la transaction #1 en base SQL\n"
            "     |---> Sauvegarde CACHE['uuid-123'] = Réponse #1\n"
            "     +---> (Coupure réseau 4G avant réception par le téléphone !)\n\n"
            "  Appel #2 (Réessai automatique) : POST /api/paiements (Header -> Idempotency-Key: uuid-123)\n"
            "     |---> Clé 'uuid-123' TROUVÉE dans CACHE !\n"
            "     |---> [AUCUNE écriture en base SQL — Doublon évité !]\n"
            "     +---> Renvoie immédiatement CACHE['uuid-123'] (avec X-Idempotent-Replay: true)"
        ),
        "reference_table": {
            "title": "Comparatif Technique : `POST` vs `PUT` vs `PATCH`",
            "headers": ["Critère", "`POST /api/formations`", "`PUT /api/formations/1`", "`PATCH /api/formations/1`"],
            "rows": [
                ["**Cible URL**", "Collection (`/formations`)", "Ressource précise (`/formations/1`)", "Ressource précise (`/formations/1`)"],
                ["**Rôle sémantique**", "Créer une nouvelle ressource", "Remplacer intégralement la ressource `#1`", "Modifier partiellement certains champs de `#1`"],
                ["**Champs requis dans le JSON**", "Tous les champs obligatoires", "Tous les champs de la ressource", "Uniquement le(s) champ(s) à modifier"],
                ["**Idempotent par nature ?**", "Non (nécessite `Idempotency-Key`)", "**Oui**", "Oui (si mise à jour par valeur fixe)"],
                ["**Code HTTP de succès**", "`201 Created`", "`200 OK`", "`200 OK`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écraser les champs non fournis par `None` lors d'une requête `PATCH`",
                "good": "Dans un `PATCH` FastAPI, utiliser `modifs = payload.model_dump(exclude_unset=True)` pour n'extraire que les champs réellement transmis",
                "why": "Le principe même de `PATCH` est de laisser intacts tous les champs qui ne figurent pas dans le JSON envoyé."
            },
            {
                "bad": "Générer l'`Idempotency-Key` côté serveur au lieu de la faire générer par le client",
                "good": "C'est toujours le **Client** qui génère l'UUID de l'`Idempotency-Key` avant son 1er essai et le réutilise en cas de réessai",
                "why": "Si le serveur générait la clé à chaque requête entrante, il ne pourrait jamais savoir que deux appels successifs correspondent à la même intention du client."
            }
        ],
        "practical_exercises": [
            "Exécutez le script dans l'atelier ci-dessus pour observer comment les deux appels `POST` portant la même `Idempotency-Key` produisent une seule transaction.",
            "Dans l'onglet **curl & Postman**, testez la commande `2.4 — PATCH` pour modifier uniquement la salle de la formation `#1`."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.3 : GESTIONNAIRES D'EXCEPTIONS GLOBAUX (@APP.EXCEPTION_HANDLER)
    # =========================================================================
    "d3-l3": {
        "context": (
            "Pour qu'une API d'entreprise soit prévisible pour les applications mobiles et partenaires, toutes ses "
            "réponses d'erreur (`404 Not Found`, `405 Method Not Allowed`, `422 Unprocessable Entity` et `500 Internal Server Error`) "
            "doivent respecter exactement le même schéma **RFC 7807 (`application/problem+json`)**.\n"
            "De plus, si une erreur imprévue (`ZeroDivisionError`, panne SQL) survient en production, le serveur ne doit "
            "jamais divulguer son code source ou ses chemins internes dans la réponse HTTP. Ce chapitre montre comment "
            "centraliser toutes les erreurs avec **`@app.exception_handler`** dans FastAPI."
        ),
        "deep_sections": [
            {
                "heading": "1. Intercepter les erreurs HTTP et de routage (`@app.exception_handler(StarletteHTTPException)`)",
                "body": (
                    "Lorsqu'une requête cible une URL inconnue (`404`), utilise un verbe non supporté (`405`) ou lève `raise HTTPException(...)` :\n"
                    "- En déclarant `@app.exception_handler(StarletteHTTPException)`, vous interceptez toutes les exceptions HTTP de Starlette et FastAPI.\n"
                    "- Vous retournez alors un `JSONResponse(status_code=exc.status_code, media_type=\"application/problem+json\", content={...})` "
                    "incluant `type`, `title`, `status`, `detail` et `instance` (`request.url.path`)."
                )
            },
            {
                "heading": "2. Le Filet de Sécurité Ultime : `@app.exception_handler(Exception)` et Masquage `500`",
                "body": (
                    "Que se passe-t-il si un bug imprévu (une division par zéro ou une base SQL momentanément verrouillée) "
                    "survient au milieu d'une route en production ?\n"
                    "Grâce à `@app.exception_handler(Exception)` :\n"
                    "1. Vous enregistrez la trace complète du bug dans les journaux internes du serveur avec un identifiant de corrélation `req_id`.\n"
                    "2. Vous renvoyez au client un `JSONResponse` propre **`500 Internal Server Error`** au format RFC 7807 qui ne divulgue **aucun secret "
                    "ni chemin de fichier interne**."
                )
            },
            {
                "heading": "3. Traçabilité et Corrélation des Incidents en Production (`X-Request-ID`)",
                "body": (
                    "Lorsqu'un client reçoit une réponse générique `500 Internal Server Error` masquée pour des raisons de sécurité, "
                    "comment l'équipe de support technique retrouve-t-elle l'erreur exacte parmi des millions de lignes de logs serveur ?\n"
                    "- En cas d'exception `500`, l'identifiant `request_id` est inscrit simultanément dans le fichier de log privé **et** dans le JSON "
                    "renvoyé au client (`\"request_id\": \"req-8f2a9c01\"`), permettant un diagnostic instantané sans exposer la pile d'exécution."
                )
            }
        ],
        "architecture_diagram": (
            "INTERCEPTION GLOBALE DES EXCEPTIONS AVEC @app.exception_handler DANS FASTAPI :\n\n"
            "  Client appelle GET /api/url-inconnue ou POST invalide\n"
            "     |\n"
            "     +---> StarletteHTTPException (404 / 405) ---> @app.exception_handler(StarletteHTTPException)\n"
            "     +---> RequestValidationError (422)       ---> @app.exception_handler(RequestValidationError)\n"
            "     +---> Exception Python imprévue (500)    ---> @app.exception_handler(Exception)\n"
            "                                                     |\n"
            "                                                     v\n"
            "                                          JSONResponse RFC 7807 (application/problem+json)"
        ),
        "reference_table": {
            "title": "Les 3 Gestionnaires `@app.exception_handler` Indispensables dans une API FastAPI",
            "headers": ["Décorateur FastAPI", "Déclencheur", "Information utile à inclure dans le JSON RFC 7807"],
            "rows": [
                ["`@app.exception_handler(StarletteHTTPException)`", "Erreurs `404`, `405`, `HTTPException`", "`status`, `title`, `detail`, `instance: request.url.path`"],
                ["`@app.exception_handler(RequestValidationError)`", "Échec de validation Pydantic (`422`)", "`status: 422`, `errors: exc.errors()`"],
                ["`@app.exception_handler(Exception)`", "Bug Python non intercepté (`500`)", "`status: 500`, `detail: \"Erreur interne (réf: X-Request-ID)\"` (sans Traceback !)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Renvoyer `str(exc)` ou `traceback.format_exc()` dans la réponse JSON `500` en production",
                "good": "Journaliser la trace complète côté serveur et renvoyer uniquement un message générique avec `request_id` au client",
                "why": "Exposer les traces d'exécution Python en production révèle vos bibliothèques, vos requêtes SQL et l'arborescence du serveur."
            },
            {
                "bad": "Oublier `raise_server_exceptions=False` lors du test d'une route `500` avec `TestClient(app)`",
                "good": "Utiliser `TestClient(app, raise_server_exceptions=False)` pour vérifier la réponse HTTP `500` retournée au client",
                "why": "Par défaut, `TestClient(app)` relève l'exception Python directement dans le test pour faciliter le débogage."
            }
        ],
        "practical_exercises": [
            "Exécutez le script dans l'atelier ci-dessus pour vérifier que les erreurs `404`, `405`, `422` et `500` renvoient toutes `application/problem+json`.",
            "Testez `GET /api/sandbox/formations/999` dans le Client HTTP pour observer une réponse `404` en JSON."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.4 : PERSISTANCE SQLITE3, ACID & INJECTIONS SQL
    # =========================================================================
    "d3-l4": {
        "context": (
            "Stocker les données dans une liste Python `FORMATIONS = [...]` présente une limite rédhibitoire : la "
            "liste réside en mémoire vive (RAM). Dès que vous redémarrez le serveur FastAPI/Uvicorn ou qu'une coupure électrique "
            "survient, toutes les formations créées par vos utilisateurs disparaissent !\n"
            "Pour conserver les données de manière durable sur disque dur tout en garantissant l'intégrité des écritures "
            "concurrentes, toute API s'appuie sur un **Système de Gestion de Base de Données Relationnelle (SGBDR)** "
            "interrogé en langage **SQL**. Python intègre nativement le moteur transactionnel **SQLite (`sqlite3`)**, "
            "idéal pour apprendre les patrons d'accès aux bases de données et la prévention des **Injections SQL**."
        ),
        "deep_sections": [
            {
                "heading": "1. Le cycle d'une Transaction SQL (`connect` → `execute` → `commit` / `rollback` → `close`)",
                "body": (
                    "Une base de données relationnelle garantit les propriétés **ACID** (*Atomicité, Cohérence, Isolation, Durabilité*) :\n"
                    "- **Atomicité (`commit` vs `rollback`)** : Imaginez un virement bancaire composé de deux requêtes SQL "
                    "(débiter le compte A, puis créditer le compte B). Si une erreur survient entre les deux, `conn.rollback()` "
                    "annule tout comme si rien ne s'était passé ! Les modifications ne deviennent permanentes sur le disque "
                    "qu'au moment précis de l'appel à **`conn.commit()`**.\n"
                    "- **`conn.row_factory = sqlite3.Row`** : Par défaut, `sqlite3` renvoie chaque ligne sous forme de tuple "
                    "anonyme `(1, 'API FastAPI', 5)`. En activant `sqlite3.Row`, chaque ligne se comporte comme un dictionnaire "
                    "convertible instantanément par `dict(row)` -> `{\"id\": 1, \"titre\": \"API FastAPI\", \"duree_jours\": 5}` !"
                )
            },
            {
                "heading": "2. Anatomie d'une Attaque par Injection SQL (SQLi) et pourquoi `?` la rend impossible",
                "body": (
                    "L'**Injection SQL** est l'une des vulnérabilités les plus destructrices de l'histoire de l'informatique :\n"
                    "- **Code vulnérable (Concaténation `f\"...\"`)** :\n"
                    "  `conn.execute(f\"SELECT * FROM formations WHERE salle = '{salle}'\")`\n"
                    "  Si un attaquant envoie `salle = \"' OR '1'='1\"`, la requête SQL exécutée devient :\n"
                    "  `SELECT * FROM formations WHERE salle = '' OR '1'='1'` !\n"
                    "  Comme `'1'='1'` est toujours vrai, la base de données renvoie **100 % de la table** (ou exécute `DROP TABLE` si `executescript` est utilisé) !\n"
                    "- **Code inviolable (Requête Paramétrée avec `?`)** :\n"
                    "  `conn.execute(\"SELECT * FROM formations WHERE salle = ?\", (salle,))`\n"
                    "  Ici, le moteur SQLite compile d'abord la structure de la commande SQL avec le marqueur `?`, puis "
                    "insère la valeur de `salle` **exclusivement comme une donnée littérale inoffensive**, sans jamais "
                    "l'interpréter comme une instruction SQL."
                )
            },
            {
                "heading": "3. Gestion des contraintes d'intégrité (`sqlite3.IntegrityError`) et code HTTP `409 Conflict`",
                "body": (
                    "Dans un schéma SQL professionnel, on définit des contraintes strictes sur les colonnes : `NOT NULL`, "
                    "`UNIQUE` (ex: le code officiel d'une formation ou l'adresse e-mail d'un étudiant) et `CHECK (duree_jours > 0)`.\n"
                    "- Si un client tente d'insérer une seconde formation avec un code déjà existant, SQLite lève `sqlite3.IntegrityError`.\n"
                    "- Plutôt que de laisser cette exception provoquer une erreur `500`, la route intercepte `except sqlite3.IntegrityError:` "
                    "et renvoie un code sémantique **`409 Conflict`** expliquant clairement quel champ unique est en doublon."
                )
            }
        ],
        "architecture_diagram": (
            "COMPARAISON : CONCATÉNATION VULNÉRABLE vs REQUÊTE PARAMÉTRÉE SÉCURISÉE (?)\n\n"
            "  Entrée malveillante du client : salle = \"' OR '1'='1\"\n"
            "        |\n"
            "        +---> [DANGER : f\"SELECT * FROM formations WHERE salle = '{salle}'\"]\n"
            "        |     Le parseur SQL voit : WHERE salle = '' OR '1'='1'  ---> FUITE TOTALE DE LA BASE !\n"
            "        |\n"
            "        +---> [SÉCURISÉ : execute(\"SELECT * FROM formations WHERE salle = ?\", (salle,))]\n"
            "              Le moteur SQL cherche littéralement une salle nommée \"' OR '1'='1\" ---> 0 résultat (Attaque neutralisée !)"
        ),
        "reference_table": {
            "title": "Correspondance Opérations CRUD ↔ Verbes HTTP ↔ Commandes SQL Paramétrées",
            "headers": ["Opération CRUD", "Route & Verbe HTTP", "Requête SQLite Paramétrée (`sqlite3`)", "Méthode de lecture résultat"],
            "rows": [
                ["**Create** (Créer)", "`POST /api/formations`", "`cur.execute(\"INSERT INTO formations (titre, salle) VALUES (?, ?)\", (t, s))` + `conn.commit()`", "`new_id = cur.lastrowid`"],
                ["**Read All** (Lister)", "`GET /api/formations`", "`conn.execute(\"SELECT * FROM formations LIMIT ? OFFSET ?\", (limit, offset))`", "`[dict(r) for r in cur.fetchall()]`"],
                ["**Read One** (Lire 1)", "`GET /api/formations/<id>`", "`conn.execute(\"SELECT * FROM formations WHERE id = ?\", (id,))`", "`row = cur.fetchone()` (`404` si `None`)"],
                ["**Update** (Modifier)", "`PUT /api/formations/<id>`", "`conn.execute(\"UPDATE formations SET titre = ?, salle = ? WHERE id = ?\", (t, s, id))` + `conn.commit()`", "`cur.rowcount`"],
                ["**Delete** (Supprimer)", "`DELETE /api/formations/<id>`", "`conn.execute(\"DELETE FROM formations WHERE id = ?\", (id,))` + `conn.commit()`", "`200 OK` ou `204 No Content`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Oublier la virgule dans un tuple à 1 seul élément : `conn.execute(\"... WHERE id = ?\", (formation_id))`",
                "good": "Toujours mettre la virgule : `conn.execute(\"... WHERE id = ?\", (formation_id,))`",
                "why": "En Python, `(5)` sans virgule est juste l'entier `5` entre parenthèses, alors que `(5,)` avec virgule est un tuple de 1 élément requis par `sqlite3`."
            },
            {
                "bad": "Oublier `conn.commit()` après un `INSERT`, `UPDATE` ou `DELETE`",
                "good": "Appeler systématiquement `conn.commit()` avant `conn.close()` lors d'une écriture",
                "why": "Sans `conn.commit()`, SQLite annule automatiquement toutes les modifications non validées à la fermeture de la connexion !"
            }
        ],
        "practical_exercises": [
            "Exécutez la démonstration d'Injection SQL dans l'atelier ci-dessus et comparez le nombre de lignes renvoyées entre la requête vulnérable et la requête paramétrée.",
            "Testez le cycle complet `POST` -> `PUT` -> `GET` sur `/api/sandbox/formations` dans l'onglet **Client HTTP & Inspecteur**."
        ]
    }
}
