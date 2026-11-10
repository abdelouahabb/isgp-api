"""
Manuel de Référence Approfondi — Enrichissement des Chapitres (Jours 2 et 3) — Volume III : Édition Tornado.
"""

ENRICHMENT_D2_D3 = {
    # =========================================================================
    # JOUR 2 — CHAPITRE 2.1 : SERVEUR MINIMAL TORNADO, IOLOOP & TABLE DE ROUTAGE
    # =========================================================================
    "d2-l1": {
        "context": (
            "Après avoir compris les fondations Python (Jour 0) et le protocole réseau HTTP/JSON (Jour 1), nous "
            "construisons notre premier serveur d'API avec **Tornado (`tornado.web.Application`, `RequestHandler`, `IOLoop`)**.\n"
            "Pourquoi Tornado est-il un framework d'exception pour maîtriser l'ingénierie des APIs et des services temps réel ? "
            "Parce qu'il repose sur une architecture **orientée objet (`RequestHandler`)** et une **boucle d'événements non bloquante (`IOLoop`)** "
            "capable de maintenir des dizaines de milliers de connexions simultanées (problème C10k). "
            "Ce chapitre explique comment un script Python devient un **démon réseau asynchrone en écoute permanente**, "
            "comment fonctionne l'`IOLoop`, et comment Tornado aiguille chaque URL vers le bon `RequestHandler`."
        ),
        "deep_sections": [
            {
                "heading": "1. Du Script Éphémère au Serveur Event-Loop : le rôle de `tornado.ioloop.IOLoop`",
                "body": (
                    "Un script Python classique exécute ses lignes de haut en bas puis s'arrête : son processus disparaît "
                    "de la mémoire.\n"
                    "Un serveur Web Tornado, au contraire, reste **en éveil 24h/24** grâce à sa boucle d'événements (`IOLoop`) :\n"
                    "- Lorsque vous appelez `app.listen(8888, address=\"0.0.0.0\")`, Tornado demande au système d'exploitation "
                    "Linux/Windows d'ouvrir un **Socket TCP non bloquant** attaché au port `8888`.\n"
                    "- L'instruction `tornado.ioloop.IOLoop.current().start()` démarre la boucle `epoll`/`kqueue`.\n"
                    "- Dès qu'un client se connecte, Tornado instancie la classe `RequestHandler` associée à l'URL, exécute la méthode "
                    "correspondant au verbe HTTP (`def get(self):`, `def post(self):`), envoie la trame HTTP de réponse, puis "
                    "traite immédiatement l'événement suivant."
                )
            },
            {
                "heading": "2. Architecture Orientée Objet : Pourquoi chaque route est une classe `RequestHandler` ?",
                "body": (
                    "Contrairement aux micro-frameworks basés sur de simples fonctions décorées, Tornado structure chaque route "
                    "autour d'une classe héritant de **`tornado.web.RequestHandler`** :\n"
                    "- Chaque verbe HTTP correspond à une méthode dédiée : `def get(self):`, `def post(self):`, `def put(self):`, "
                    "`def patch(self):`, `def delete(self):`, `def options(self):`.\n"
                    "- Pour chaque requête entrante, Tornado crée une **nouvelle instance isolée** de votre classe `RequestHandler` : "
                    "l'objet `self` contient `self.request` (en-têtes, corps, IP) et toutes les méthodes de réponse (`self.write`, "
                    "`self.set_status`, `self.set_header`, `self.render`)."
                )
            },
            {
                "heading": "3. Pourquoi `self.write(dictionnaire)` sérialise automatiquement en JSON ?",
                "body": (
                    "Dans une méthode `RequestHandler` de Tornado, passer un dictionnaire Python `dict` à **`self.write({...})`** "
                    "accomplit automatiquement 3 opérations indispensables :\n"
                    "1. Il sérialise votre dictionnaire Python en chaîne JSON UTF-8 valide.\n"
                    "2. Il écrit les octets dans le tampon de sortie de la requête.\n"
                    "3. Il injecte automatiquement l'en-tête officiel **`Content-Type: application/json; charset=UTF-8`**."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE D'AIGUILLAGE D'UNE REQUÊTE DANS TORNADO (IOLOOP & APPLICATION)\n"
            "  Client HTTP (GET /api/v1/sante)\n"
            "        |\n"
            "        v\n"
            "  [Socket TCP Non-Bloquant :8888 (HTTPServer + IOLoop)]\n"
            "        |  (Lit la trame HTTP et construit HTTPServerRequest)\n"
            "        v\n"
            "  [app = tornado.web.Application([...])] ---> Parcourt les tuples Regex :\n"
            "                                                - (r'/api/v1/sante',      SanteHandler)\n"
            "                                                - (r'/api/v1/formations', FormationsHandler)\n"
            "        |\n"
            "        v\n"
            "  Instancie SanteHandler ---> appelle handler.get() ---> self.write({...}) ---> HTTP/1.1 200 OK (application/json)"
        ),
        "reference_table": {
            "title": "Composants Fondamentaux d'une Application Tornado Minimale",
            "headers": ["Élément de code", "Rôle technique exact", "Que se passe-t-il si on l'omet ?"],
            "rows": [
                ["`class MonHandler(tornado.web.RequestHandler):`", "Définit le contrôleur orienté objet d'un endpoint", "Impossible de traiter les verbes HTTP `get()` / `post()`"],
                ["`tornado.web.Application([(r\"/url\", MonHandler)])`", "Enregistre la table de routage Regex de l'application", "Aucune route n'est exposée (`404 Not Found`)"],
                ["`self.write(dictionnaire)`", "Sérialise le `dict` en JSON + ajoute `Content-Type: application/json; charset=UTF-8`", "Si on écrit une chaîne `str`, l'en-tête sera `text/html` au lieu de `application/json`"],
                ["`tornado.ioloop.IOLoop.current().start()`", "Démarre la boucle d'événements asynchrone en écoute", "Le script se termine immédiatement sans écouter les clients"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Nommer son propre fichier `tornado.py` dans le dossier de travail",
                "good": "Nommer ses fichiers `app.py`, `serveur.py` ou `01_serveur_minimal_tornado.py`",
                "why": "Si votre fichier s'appelle `tornado.py`, l'instruction `import tornado.web` importera votre propre fichier au lieu de la bibliothèque Tornado (`ModuleNotFoundError`) !"
            },
            {
                "bad": "Passer une liste brute `self.write([1, 2, 3])` directement à `self.write()`",
                "good": "Toujours passer un dictionnaire `self.write({\"data\": [1, 2, 3]})`",
                "why": "Tornado lève `TypeError: Lists not accepted for security reasons` si vous passez une `list` à `self.write()`."
            }
        ],
        "practical_exercises": [
            "Exécutez le code dans l'atelier ci-dessus pour inspecter la table de routage de `tornado.web.Application`.",
            "Ajoutez un 3ème handler `VersionHandler` associé à `(r\"/api/v1/version\", VersionHandler)` dans l'exécuteur et vérifiez la réponse JSON."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.2 : MATURITÉ REST (RICHARDSON), ROUTAGE REGEX & ARGUMENTS D'URL
    # =========================================================================
    "d2-l2": {
        "context": (
            "N'importe qui peut créer une URL `/api/faireQuelqueChose` qui renvoie du JSON, mais cela n'en fait pas "
            "une API **RESTful** professionnelle.\n"
            "Comment les géants technologiques (Stripe, GitHub, Twilio, Google Cloud) nomment-ils leurs URLs pour "
            "qu'un développeur externe comprenne intuitivement toute l'API en 5 minutes ? Et comment extraire "
            "proprement un identifiant d'entité (`/formations/42`) par expression régulière ou un critère de recherche "
            "(`?salle=Alger`) dans Tornado ? Ce chapitre formalise le **Modèle de Maturité de Richardson** et l'extraction "
            "des paramètres dans `RequestHandler`."
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
                    "(`/api/v1/formations/42`) et la **méthode du `RequestHandler`** exprime l'action (`get` pour lire, `post` pour créer, `put`/`patch` "
                    "pour modifier, `delete` pour supprimer), tandis que la réponse utilise le code de statut exact (`200`, `201`, `404`, `422`).\n"
                    "- **Niveau 3 (HATEOAS)** : La réponse JSON inclut en plus des liens de navigation (`\"links\": {\"self\": \"/api/v1/formations/42\"}`)."
                )
            },
            {
                "heading": "2. Path Parameters (Groupes Regex `([0-9]+)`) vs Query Parameters (`self.get_query_argument`)",
                "body": (
                    "Quand faut-il mettre un paramètre dans le chemin (`/formations/42`) et quand faut-il le mettre après `?` (`?salle=Alger`) ?\n"
                    "- **Paramètre de Chemin (`Path Parameter` : `r\"/api/formations/([0-9]+)\"`)** : Utilisé pour "
                    "**identifier de manière unique une ressource précise**. Dans Tornado, chaque groupe entre parenthèses `(...)` "
                    "de l'expression régulière est passé en argument à `def get(self, formation_id: str):`. Si l'identifiant n'existe pas "
                    "en base, le handler renvoie **`404 Not Found`**.\n"
                    "- **Paramètre de Requête (`Query Parameter` : `/api/formations?salle=Alger&duree_min=3`)** : Utilisé pour "
                    "**filtrer, trier, rechercher ou paginer** une collection via `self.get_query_argument('salle', None)`. Si aucune formation "
                    "ne correspond au filtre `?salle=Oran`, ce n'est **pas** une erreur `404` : la collection renvoie **`200 OK` avec une liste vide `[]`** !"
                )
            },
            {
                "heading": "3. Lecture défensive avec `self.get_query_argument('cle', default)`",
                "body": (
                    "Dans une URL (`?duree_min=3`), tout paramètre est initialement reçu sous forme de chaîne de caractères `\"3\"`.\n"
                    "- Si vous appelez `self.get_query_argument(\"ht\")` **sans second argument**, Tornado lève automatiquement "
                    "une exception `tornado.web.MissingArgumentError` (qui renvoie `HTTP 400 Bad Request`) si le client omet `?ht=`.\n"
                    "- Si le paramètre est optionnel, passez toujours une valeur par défaut : `self.get_query_argument(\"taux\", \"19.0\")`, "
                    "puis convertissez-la dans un bloc `try: float(...) except ValueError:`."
                )
            },
            {
                "heading": "4. Pourquoi voit-on `([0-9]+)`, `:variable`, `<variable>` et `{variable}` selon les outils et frameworks ?",
                "body": (
                    "En lisant des documentations d'API ou en utilisant Postman, les développeurs rencontrent quatre notations "
                    "différentes pour représenter une **variable de chemin (Path Parameter)** :\n"
                    "1. **`([0-9]+)` ou `(?P<id>[0-9]+)` (Syntaxe Regex Tornado)** :\n"
                    "   - Tornado utilise toute la puissance du module `re` de Python : `(r\"/api/formations/([0-9]+)\", FormationHandler)`. "
                    "Le motif `[0-9]+` garantit dès le routeur que seuls des chiffres sont acceptés !\n"
                    "2. **`<int:id>` (Syntaxe Flask / Django)** : Spécifique à Werkzeug/Flask.\n"
                    "3. **`:variable` (Syntaxe Postman, Express.js / Node.js)** :\n"
                    "   - Dans **Postman**, taper `http://127.0.0.1:8888/api/formations/:id` active automatiquement la clé `id` dans *Path Variables*.\n"
                    "4. **`{variable}` (Syntaxe OpenAPI 3.0 / Swagger & FastAPI)** :\n"
                    "   - Standard IETF RFC 6570 *URI Template* : `/api/formations/{id}`."
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
            "  - Dans le code serveur Tornado : (r\"/api/v1/formations/([0-9]+)\", Handler)   <-- Groupe Regex ([0-9]+)\n"
            "  - Dans l'interface Postman     : GET http://.../api/v1/formations/:id        <-- Deux-points :id\n"
            "  - Dans OpenAPI / Swagger       : GET /api/v1/formations/{id}                 <-- Accolades {...}\n"
            "  - Dans curl / Navigateur       : curl http://.../api/v1/formations/42        <-- Valeur réelle 42"
        ),
        "reference_table": {
            "title": "Synthèse : Lecture dans `RequestHandler` & Notations des Variables d'URL",
            "headers": ["Élément / Syntaxe", "Où est-il utilisé ?", "Exemple concret", "Comportement & Règle d'or"],
            "rows": [
                ["`([0-9]+)` / `(?P<id>[0-9]+)`", "**Tornado (`tornado.web.Application`)**", "`(r'/api/formations/([0-9]+)', Handler)`", "Valide le format par Regex et passe la chaîne capturée à `def get(self, id):`"],
                ["`:variable` (ex. `:id`)", "**Postman**, Express.js (Node), Rails", "`/api/formations/:id`", "Crée une variable de chemin dans Postman, mais **n'est pas reconnu par Tornado** !"],
                ["`{variable}` (ex. `{id}`)", "**OpenAPI 3.0 (Swagger)**, FastAPI", "`/api/formations/{id}`", "Standard officiel de documentation d'API (RFC 6570)"],
                ["`self.get_query_argument`", "Query String (après `?`)", "`GET /api/formations?salle=Alger&page=2`", "`int(self.get_query_argument(\"page\", \"1\"))`"],
                ["`self.request.headers`", "En-têtes HTTP (`Headers`)", "`X-API-Key: secret`", "`self.request.headers.get(\"X-API-Key\", \"\")`"],
                ["`tornado.escape.json_decode`", "Corps (`self.request.body`)", "`{\"titre\": \"Tornado\", \"jours\": 5}`", "`corps = tornado.escape.json_decode(self.request.body)`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écrire `(r'/api/formations/:id', Handler)` ou `<int:id>` dans une route Tornado",
                "good": "Toujours utiliser une expression régulière `(r'/api/formations/([0-9]+)', Handler)` dans Tornado",
                "why": "Le routeur Tornado est basé sur `re.compile()` : seuls les groupes entre parenthèses `(...)` extraient les paramètres d'URL."
            },
            {
                "bad": "Mettre des verbes d'action dans les URLs : `/api/creer_formation`, `/api/listerFormations`",
                "good": "Utiliser uniquement des noms de ressources au pluriel (`/api/formations`) et laisser `def post` / `def get` définir l'action",
                "why": "Respecter le Niveau 2 de Richardson évite la prolifération de centaines d'URLs incohérentes."
            },
            {
                "bad": "Renvoyer `404 Not Found` lorsqu'une recherche filtrée `GET /api/formations?salle=Tamanrasset` ne trouve aucun résultat",
                "good": "Renvoyer `200 OK` avec `{\"total\": 0, \"formations\": []}`",
                "why": "`404` sur une collection ferait croire au client que la route `/api/formations` n'existe plus."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur ci-dessus, observez les appels simulés sur `/api/v1/stagiaires/2` et `/api/v1/calcul-tva?ht=2500&taux=19`.",
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
            "un fichier JSON de 800 Mo, de bloquer l'`IOLoop` Tornado et de faire s'écrouler le serveur (*Out Of Memory / OOM*). "
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
                "heading": "2. Pourquoi borner impérativement `page` et `limit` côté serveur (Protection Anti-DoS)",
                "body": (
                    "Si vous écrivez simplement `limit = int(self.get_query_argument('limit', '10'))`, qu'arrive-t-il si un "
                    "utilisateur malveillant appelle `?page=-5&limit=999999999` ?\n"
                    "- Un `page` négatif produirait un `offset` négatif incohérent.\n"
                    "- Un `limit` de 1 milliard contournerait toute votre protection de pagination !\n"
                    "On encadre donc toujours les deux valeurs par `max()` et `min()` :\n"
                    "- `page = max(1, int(self.get_query_argument(\"page\", \"1\")))` (au minimum page 1).\n"
                    "- `limit = min(50, max(1, int(self.get_query_argument(\"limit\", \"10\"))))` (entre 1 et 50 éléments maximum par appel)."
                )
            },
            {
                "heading": "3. Validation par Liste Blanche (Whitelist) du Tri Dynamique (`?tri=...&ordre=...`)",
                "body": (
                    "Pour permettre au client de trier les résultats (`?tri=duree_jours&ordre=desc`), le serveur ne doit "
                    "**jamais** utiliser directement la chaîne envoyée par le client comme nom de clé ou colonne SQL sans vérification.\n"
                    "On définit un tuple immuable de colonnes autorisées :\n"
                    "`CHAMPS_TRI_AUTORISES = (\"id\", \"duree_jours\", \"titre\")`.\n"
                    "Si `champ_tri not in CHAMPS_TRI_AUTORISES`, le `RequestHandler` rejette immédiatement la requête avec un code "
                    "**`400 Bad Request`** en indiquant la liste des colonnes autorisées."
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
            "title": "Structure Standard de l'Objet `meta` de Pagination dans une Réponse JSON Tornado",
            "headers": ["Clé JSON dans `meta`", "Type", "Formule de calcul en Python", "Utilité pour l'interface cliente (Web / Mobile)"],
            "rows": [
                ["`total_items`", "`int`", "`len(resultats_filtres)` ou `SELECT COUNT(*)`", "Afficher « 48 formations trouvées »"],
                ["`page`", "`int`", "`max(1, int(self.get_query_argument('page', '1')))`", "Mettre en surbrillance le numéro de page courant"],
                ["`limit`", "`int`", "`min(50, max(1, int(self.get_query_argument('limit', '10'))))`", "Connaître la taille de tranche appliquée"],
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
    # JOUR 2 — CHAPITRE 2.4 : HOOKS DE CYCLE DE VIE (PREPARE / ON_FINISH)
    # =========================================================================
    "d2-l4": {
        "context": (
            "Lorsqu'une API compte 50 `RequestHandlers`, comment mesurer le temps d'exécution exact en millisecondes de chaque "
            "appel, attribuer un numéro de suivi unique (`X-Request-ID`) et ajouter des en-têtes de sécurité sans "
            "copier-coller les mêmes lignes dans les 50 classes ?\n"
            "Dans Tornado, la réponse architecturale consiste à définir une classe parente **`BaseHandler(tornado.web.RequestHandler)`** "
            "qui surcharge les méthodes de cycle de vie **`set_default_headers(self)`**, **`prepare(self)`** et **`on_finish(self)`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Les 4 phases du Cycle de Vie d'un `RequestHandler` dans Tornado",
                "body": (
                    "Chaque requête HTTP qui franchit la porte de Tornado traverse séquentiellement quatre méthodes sur une nouvelle instance de `RequestHandler` :\n"
                    "1. **`set_default_headers(self)`** : Appelée dès l'initialisation du handler pour poser les en-têtes de sécurité systématiques "
                    "(`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, CORS).\n"
                    "2. **`prepare(self)`** : S'exécute **avant** la méthode `get()`/`post()`. Idéale pour démarrer un chronomètre haute précision "
                    "(`self.heure_debut = time.perf_counter()`), extraire ou générer `self.request_id`, ou bloquer une requête non autorisée "
                    "(si `prepare(self)` appelle `self.finish(...)`, Tornado s'arrête immédiatement et n'appelle pas `get()` !).\n"
                    "3. **Méthode HTTP (`def get(self)` / `def post(self)`)** : Exécute la logique métier et appelle `self.write({...})`.\n"
                    "4. **`on_finish(self)`** : S'exécute **après** l'envoi complet de la réponse au client. Idéale pour écrire le journal "
                    "d'audit structuré et libérer les ressources."
                )
            },
            {
                "heading": "2. Pourquoi stocker l'état de la requête sur `self` est 100 % isolé dans Tornado ?",
                "body": (
                    "Comment transmettre l'heure de début `heure_debut` mesurée dans `prepare(self)` à la méthode `get(self)` et à `on_finish(self)` ?\n"
                    "- **Danger d'une variable globale** : Sur un serveur asynchrone où deux clients A et B appellent l'API en même temps, "
                    "une variable globale `HEURE_DEBUT` serait écrasée par le client B !\n"
                    "- **La solution `self` du `RequestHandler`** : Tornado instancie un **nouvel objet `RequestHandler` distinct pour chaque requête HTTP**. "
                    "Tout attribut attaché à `self` (`self.request_id`, `self.heure_debut`, `self.current_user`) est donc strictement isolé "
                    "pour cette requête unique et détruit automatiquement par le ramasse-miettes Python après `on_finish()`."
                )
            },
            {
                "heading": "3. L'importance industrielle du `X-Request-ID` (Correlation ID)",
                "body": (
                    "Lorsqu'un client partenaire vous signale : *« J'ai reçu une erreur hier à 14h12 »*, chercher dans un "
                    "fichier de log contenant 500 000 lignes est un cauchemar.\n"
                    "Avec un identifiant unique **`X-Request-ID`** (par exemple `req-8f91a2b3c4d5` généré par `uuid.uuid4()`) "
                    "renvoyé dans les en-têtes HTTP de chaque réponse ET inscrit dans chaque ligne de log d'audit, il suffit "
                    "d'un simple `grep req-8f91a2b3c4d5 app.log` pour retrouver instantanément toute l'exécution correspondante."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE VIE COMPLET D'UNE REQUÊTE DANS UN BASEHANDLER TORNADO :\n\n"
            "  Requête HTTP Entrante -> Nouvelle instance du RequestHandler (self)\n"
            "          |\n"
            "          v\n"
            "  +------------------------------------------------------------------+\n"
            "  | 1. set_default_headers(self) & prepare(self)                     |\n"
            "  |    -> self.heure_debut = time.perf_counter()                     |\n"
            "  |    -> self.request_id  = \"req-a1b2c3d4\"                          |\n"
            "  |    -> self.set_header(\"X-Request-ID\", self.request_id)           |\n"
            "  +------------------------------------------------------------------+\n"
            "          |\n"
            "          v\n"
            "  +------------------------------------------------------------------+\n"
            "  | 2. Méthode Métier : def get(self) / def post(self)               |\n"
            "  |    -> Exécute le calcul / SQL et appelle self.write({...})       |\n"
            "  +------------------------------------------------------------------+\n"
            "          |\n"
            "          v  (Envoi de la réponse HTTP au client)\n"
            "  +------------------------------------------------------------------+\n"
            "  | 3. on_finish(self)                                               |\n"
            "  |    -> Calcule duree_ms = (perf_counter() - self.heure_debut)*1000|\n"
            "  |    -> Écrit la ligne [AUDIT] structurée dans les logs serveur    |\n"
            "  +------------------------------------------------------------------+"
        ),
        "reference_table": {
            "title": "Comparatif des Méthodes de Cycle de Vie d'un `RequestHandler` Tornado",
            "headers": ["Méthode Tornado", "Moment d'exécution", "Peut modifier les Headers HTTP ?", "Usage typique"],
            "rows": [
                ["`set_default_headers(self)`", "À l'instanciation du handler (et réinitialisation d'erreur)", "Oui (`self.set_header(...)`)", "En-têtes de sécurité (`nosniff`, `DENY`) et CORS"],
                ["`prepare(self)`", "Avant `get()` / `post()` (peut être `async def`)", "Oui (`self.set_header(...)`)", "Chronométrage, `X-Request-ID`, AuthN, Rate Limiting (`self.finish()` pour stopper)"],
                ["`on_finish(self)`", "Après l'envoi complet de la réponse au client", "**Non** (la réponse est déjà partie sur le réseau !)", "Journalisation d'audit (`[AUDIT]`), métriques Prometheus, nettoyage"],
                ["`write_error(self, status_code, **kwargs)`", "Lors d'un `send_error()` ou d'une exception non gérée", "Oui", "Formater toutes les erreurs HTTP (404, 405, 500) en JSON"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Appeler `self.set_header('X-Response-Time-Ms', ...)` à l'intérieur de `on_finish(self)`",
                "good": "Poser les en-têtes dans `set_default_headers()`, `prepare()` ou avant la fin de `get()`/`post()`",
                "why": "`on_finish(self)` s'exécute **après** que les octets HTTP ont été envoyés sur le socket réseau : modifier un en-tête dans `on_finish` n'a plus aucun effet sur la réponse reçue par le client."
            },
            {
                "bad": "Utiliser `time.time()` pour mesurer des durées d'exécution de quelques millisecondes",
                "good": "Utiliser l'horloge monotone haute précision `time.perf_counter()`",
                "why": "`time.perf_counter()` offre une résolution à la nanoseconde et n'est jamais faussé par les ajustements d'horloge NTP du système."
            }
        ],
        "practical_exercises": [
            "Exécutez le script `day_2/04_middlewares_et_audit_log.py` dans l'atelier ci-dessus pour observer l'injection automatique de `X-Request-ID` et `X-Response-Time-Ms`.",
            "Observez comment l'en-tête personnalisé `X-Request-ID: trace-client-personnalise-777` envoyé par le client est conservé de bout en bout par `prepare(self)`."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.5 : MOTEUR TORNADO.TEMPLATE & FORMULAIRES WEB HTML (GET_BODY_ARGUMENT / REQUEST.FILES)
    # =========================================================================
    "d2-l5": {
        "context": (
            "Un service Web complet en entreprise ne se limite pas toujours à des échanges JSON entre machines : "
            "très souvent, l'application Tornado doit aussi afficher un **portail d'administration**, une **page de connexion** "
            "ou un **formulaire de saisie** pour des opérateurs humains.\n"
            "Or, deux erreurs reviennent constamment chez les développeurs :\n"
            "1. **Coder du HTML en dur dans les fichiers Python (`self.write(f\"<h1>{titre}</h1>\")`)**, ce qui mélange la logique "
            "métier et la présentation tout en ouvrant une faille critique d'injection JavaScript (**XSS — Cross-Site Scripting**).\n"
            "2. **Essayer de lire un formulaire HTML `<form method=\"POST\">` avec `json_decode(self.request.body)`**, qui lève "
            "`JSONDecodeError` car un navigateur soumettant un formulaire HTML n'envoie **pas** du JSON, mais le format "
            "`application/x-www-form-urlencoded` lu par **`self.get_body_argument(...)`** (ou `multipart/form-data` lu par **`self.request.files`**) !"
        ),
        "deep_sections": [
            {
                "heading": "1. Le Moteur `tornado.template` (`self.render`) et la protection automatique Anti-XSS",
                "body": (
                    "Dans Tornado, on ne construit **jamais** une page HTML par concaténation de chaînes dans le fichier `.py`. "
                    "Tous les fichiers HTML sont placés dans le dossier configuré via **`template_path`** et rendus par **`self.render(\"fichier.html\", ...)`** :\n"
                    "- **Les expressions `{{ variable }}`** : Évaluent une expression Python (`{{ f[\"titre\"] }}`) et l'insèrent dans la page.\n"
                    "- **Sécurité automatique contre les failles XSS (*Auto-Escaping*)** : Si un attaquant saisit `<script>alert('Piraté')</script>` "
                    "comme titre de formation, **Tornado échappe automatiquement** les caractères spéciaux en `&lt;script&gt;...`, neutralisant l'attaque.\n"
                    "- **Les structures de contrôle `{% ... %}` et fermeture universelle `{% end %}`** : Dans `tornado.template`, toutes les boucles "
                    "(`{% for f in formations %}`) et toutes les conditions (`{% if erreurs %}`) se ferment avec le mot-clé unique **`{% end %}`**."
                )
            },
            {
                "heading": "2. Anatomie d'un Formulaire HTML (`<form method=\"POST\">`) : `self.get_body_argument` vs `json_decode`",
                "body": (
                    "Comprenons exactement ce qu'envoie un navigateur Web lorsqu'un utilisateur remplit un formulaire `<form method=\"POST\" action=\"/formations\">` :\n"
                    "- Chaque champ `<input name=\"titre\">`, `<input name=\"duree_jours\">`, `<select name=\"salle\">` est identifié par son attribut **`name=\"...\"`**.\n"
                    "- Au clic sur `<button type=\"submit\">`, le navigateur assemble une chaîne de paires `cle=valeur` séparées par `&` :\n"
                    "  `titre=Architecture+API&duree_jours=5&salle=Salle+A`\n"
                    "  accompagnée de l'en-tête HTTP : **`Content-Type: application/x-www-form-urlencoded`**.\n"
                    "- Côté Tornado (dans `def post(self):`) :\n"
                    "  - **`self.get_body_argument(\"titre\", \"\")`** extrait et décode proprement chaque champ du formulaire HTML.\n"
                    "  - **`tornado.escape.json_decode(self.request.body)`** est réservé aux requêtes `Content-Type: application/json`."
                )
            },
            {
                "heading": "3. Envoi de Fichiers (`multipart/form-data` -> `self.request.files`) et Redirection `self.redirect()`",
                "body": (
                    "Deux mécanismes complémentaires sont indispensables pour maîtriser les formulaires en production :\n"
                    "1. **Upload de fichiers (`enctype=\"multipart/form-data\"`)** : Dès qu'un formulaire contient `<input type=\"file\" name=\"document_pdf\">`, "
                    "on ajoute `enctype=\"multipart/form-data\"` sur la balise `<form>`. Tornado place alors les fichiers binaires dans la liste "
                    "**`self.request.files.get(\"document_pdf\", [])`**, où chaque élément est un dictionnaire `{\"filename\": ..., \"body\": bytes, \"content_type\": ...}`. "
                    "Il est obligatoire d'assainir `filename` (`os.path.basename` + regex) pour bloquer toute attaque *Path Traversal* (`../../etc/passwd`).\n"
                    "2. **Le Patron `PRG` (*Post / Redirect / Get*)** : Après un `POST` réussi depuis un navigateur, appeler `self.redirect(\"/formations\")` "
                    "(code HTTP `302`) évite que l'utilisateur ne soumette le formulaire une seconde fois en appuyant sur `F5`."
                )
            }
        ],
        "architecture_diagram": (
            "COMPARAISON DES 3 FORMATS D'ENVOI POST ET LEUR LECTURE DANS TORNADO\n"
            "===================================================================\n\n"
            "  [1] FORMULAIRE HTML CLASSIQUE (<form method=\"POST\">)\n"
            "      Header  : Content-Type: application/x-www-form-urlencoded\n"
            "      Body    : titre=API+Tornado&duree_jours=5&salle=Salle+A\n"
            "      Tornado : self.get_body_argument(\"titre\")  |  Réponse : self.render(\"...\") ou self.redirect()\n\n"
            "  [2] FORMULAIRE HTML AVEC FICHIER (<form method=\"POST\" enctype=\"multipart/form-data\">)\n"
            "      Header  : Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...\n"
            "      Tornado : Texte -> self.get_body_argument(\"...\")  +  Fichier -> self.request.files[\"document_pdf\"][0]\n\n"
            "  [3] CLIENT API / FETCH JAVASCRIPT / MOBILE\n"
            "      Header  : Content-Type: application/json\n"
            "      Body    : {\"titre\": \"API Tornado\", \"duree_jours\": 5, \"salle\": \"Salle A\"}\n"
            "      Tornado : tornado.escape.json_decode(self.request.body)  |  Réponse : self.set_status(201); self.write({...})"
        ),
        "reference_table": {
            "title": "Tableau Comparatif : Formulaires Web HTML (`get_body_argument` / `self.render`) vs API JSON (`json_decode`)",
            "headers": ["Caractéristique", "Formulaire HTML Classique", "Formulaire avec Fichier (Upload)", "Requête API REST (JSON)"],
            "rows": [
                ["En-tête `Content-Type`", "`application/x-www-form-urlencoded`", "`multipart/form-data`", "`application/json`"],
                ["Méthode de lecture Tornado", "`self.get_body_argument('champ', '')`", "`self.get_body_argument` + `self.request.files['fichier']`", "`tornado.escape.json_decode(self.request.body)`"],
                ["Attribut HTML obligatoire", "`<input name=\"champ\">` (`name` et non `id`)", "`<form enctype=\"multipart/form-data\">`", "Clé de l'objet JSON `{\"champ\": ...}`"],
                ["Méthode de réponse Tornado", "`self.render('page.html', ...)` ou `self.redirect()`", "`self.render()` ou `self.write()`", "`self.set_status(201); self.write({...})`"],
                ["Commande `curl` équivalente", "`curl -X POST -d \"titre=Tornado&jours=5\" URL`", "`curl -X POST -F \"doc=@cours.pdf\" URL`", "`curl -X POST -H \"Content-Type: application/json\" -d '{...}' URL`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écrire du HTML en dur dans Python (`self.write(f'<h1>Bonjour {nom}</h1>')`) au lieu d'utiliser `self.render()`",
                "good": "Placer tout le HTML dans `templates/fichier.html` et utiliser `self.render('fichier.html', nom=nom)`",
                "why": "La concaténation HTML dans Python rend le code ingérable et expose l'application aux injections JavaScript (XSS), alors que `tornado.template` échappe automatiquement `{{ nom }}`."
            },
            {
                "bad": "Fermer une boucle avec `{% endfor %}` ou `{% endif %}` dans un template Tornado natif",
                "good": "Toujours fermer les blocs `{% for %}` et `{% if %}` avec `{% end %}` dans `tornado.template`",
                "why": "Le moteur `tornado.template` utilise le mot-clé universel `{% end %}` (`ParseError: unknown operator: 'endfor'`)."
            },
            {
                "bad": "Appeler `tornado.escape.json_decode(self.request.body)` pour lire un `<form method=\"POST\">` HTML standard",
                "good": "Utiliser `self.get_body_argument(...)` pour un formulaire HTML",
                "why": "Un formulaire HTML envoie `application/x-www-form-urlencoded`, donc `json_decode` lèverait `JSONDecodeError`."
            }
        ],
        "practical_exercises": [
            "Ouvrez l'atelier interactif réel sur `/sandbox/formulaire-jinja` (bouton ci-dessous ou dans la barre d'outils), soumettez une nouvelle formation via le formulaire HTML et observez la trame `application/x-www-form-urlencoded` reçue.",
            "Testez également un envoi invalide (durée négative ou titre d'une seule lettre) pour observer comment la boucle `{% for err in erreurs %} ... {% end %}` affiche les erreurs côté serveur."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.1 : CRUD MÉMOIRE, VALIDATION & RFC 7807 (400 vs 422)
    # =========================================================================
    "d3-l1": {
        "context": (
            "Jusqu'ici, notre serveur répondait principalement à des requêtes de consultation (`GET`). Dès que l'on "
            "autorise les clients à **créer (`POST`)**, **modifier (`PUT`/`PATCH`)** et **supprimer (`DELETE`)** des "
            "données (les 4 opérations **CRUD**), une règle cardinale de sécurité entre en jeu : **Ne jamais faire "
            "confiance aux données envoyées par le client (*Never Trust User Input*)**.\n"
            "Un client peut envoyer un JSON cassé, oublier un champ obligatoire, envoyer un texte à la place d'un "
            "nombre ou tenter de créer une formation de `-15` jours. Ce chapitre enseigne comment valider rigoureusement "
            "les payloads entrants dans Tornado et structurer les réponses d'erreur selon la norme internationale **RFC 7807 (Problem Details)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Lecture sécurisée du Corps JSON avec `tornado.escape.json_decode(self.request.body)`",
                "body": (
                    "Dans un `RequestHandler` Tornado, les octets bruts du corps de la requête sont stockés dans `self.request.body`. "
                    "Lorsque vous appelez `tornado.escape.json_decode(self.request.body)` sur un JSON mal formé (par exemple une virgule en trop), "
                    "Python lève `json.JSONDecodeError`.\n"
                    "En encapsulant cet appel dans une méthode helper `lire_json()` avec `try / except (json.JSONDecodeError, TypeError, ValueError):` :\n"
                    "- Si le corps est vide ou syntaxiquement invalide, la fonction ne plante pas et renvoie `None`.\n"
                    "- Vous pouvez alors tester `if not isinstance(corps, dict):` et renvoyer vous-même une réponse JSON "
                    "explicite avec `self.set_status(400)` (**`400 Bad Request`**)."
                )
            },
            {
                "heading": "2. Pourquoi collecter TOUTES les erreurs de validation plutôt que de s'arrêter à la première ?",
                "body": (
                    "Imaginez un formulaire de création comportant 5 champs dont 3 sont erronés. Si votre API s'arrête dès "
                    "le 1er champ invalide, l'utilisateur corrige le 1er champ, renvoie la requête, découvre que le 2ème est "
                    "faux, corrige le 2ème, renvoie la requête et découvre que le 3ème est faux !\n"
                    "En accumulant toutes les anomalies dans une liste **`erreurs = []`** (comme dans la fonction "
                    "`valider_payload_formation` de notre script), votre API renvoie en un seul appel la liste exhaustive "
                    "des champs en erreur avec le code **`422 Unprocessable Entity`**."
                )
            },
            {
                "heading": "3. Le Standard International RFC 7807 (`Problem Details for HTTP APIs`)",
                "body": (
                    "Pour éviter que chaque équipe n'invente son propre format d'erreur (`{\"err\": ...}`, `{\"message\": ...}`, "
                    "`{\"fault\": ...}`), l'IETF a publié la norme **RFC 7807 / RFC 9457**. Une erreur normalisée contient :\n"
                    "- `type` : URI identifiant la catégorie d'erreur (ex: `https://api.isgp.dz/erreurs/validation`).\n"
                    "- `title` : Résumé lisible du problème.\n"
                    "- `status` : Répétition du code HTTP numérique (`422`).\n"
                    "- `errors` : Liste détaillée des champs invalides (`[{\"champ\": \"duree_jours\", \"message\": \"...\"}]`)."
                )
            }
        ],
        "architecture_diagram": (
            "ENTONNOIR DE VALIDATION DÉFENSIVE D'UNE REQUÊTE POST / PUT DANS TORNADO :\n\n"
            "  Requête POST entrante (self.request.body)\n"
            "        |\n"
            "        +---> 1. Le Body est-il un objet JSON syntaxiquement valide (tornado.escape.json_decode) ?\n"
            "        |        NON ---> self.set_status(400) : HTTP 400 Bad Request (Syntaxe illisible)\n"
            "        |\n"
            "        +---> 2. Les champs respectent-ils les types et bornes métier (len >= 3, 1 <= duree <= 30) ?\n"
            "        |        NON ---> self.set_status(422) : HTTP 422 Unprocessable Entity (Format RFC 7807 + liste 'errors')\n"
            "        |\n"
            "        v     3. OUI ---> Insertion en base + self.set_status(201) + self.set_header('Location', ...)"
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
                "bad": "Supposer que parce que le Frontend JavaScript valide le formulaire, le Backend Tornado n'a pas besoin de valider",
                "good": "Toujours appliquer 100 % des validations de types et de bornes dans le Backend Python",
                "why": "Un attaquant utilise `curl` ou un script Python pour appeler directement votre API en contournant totalement l'interface Web !"
            },
            {
                "bad": "Laisser `200 OK` sur un `POST` qui crée un nouvel enregistrement",
                "good": "Appeler `self.set_status(201)` accompagné de `self.set_header('Location', f'/api/formations/{new_id}')`",
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
            "1. **Quelle est la différence exacte entre `PUT` (`def put`) et `PATCH` (`def patch`) pour modifier une ressource existante ?**\n"
            "2. **Comment empêcher qu'un client qui clique deux fois sur « Payer » (ou dont le réseau 4G coupe et "
            "réessaie automatiquement son `POST`) ne soit débité deux fois ?**\n"
            "Ce chapitre apporte la réponse complète et l'implémentation de référence en Python/Tornado."
        ),
        "deep_sections": [
            {
                "heading": "1. Remplacement Intégral (`def put`) vs Modification Partielle (`def patch` — RFC 5789)",
                "body": (
                    "Supposons que la formation `#1` contienne : `{\"id\": 1, \"titre\": \"Tornado\", \"duree_jours\": 5, \"salle\": \"Labo 1\"}`.\n"
                    "- **Avec `PUT /api/v1/formations/1` (`def put(self, formation_id)`)** : La sémantique officielle de `PUT` est « **Remplacer l'intégralité "
                    "de la fiche #1 par le document fourni** ». Le client doit donc envoyer **tous les champs obligatoires** "
                    "(`titre`, `duree_jours`, `salle`). Tout champ non fourni est réinitialisé à sa valeur par défaut.\n"
                    "- **Avec `PATCH /api/v1/formations/1` (`def patch(self, formation_id)`)** : La sémantique de `PATCH` est « **Appliquer une modification "
                    "partielle** ». Si vous voulez uniquement déménager la formation dans la `\"Salle B\"`, vous envoyez "
                    "uniquement `{\"salle\": \"Salle B\"}` : le serveur conserve le `titre` et la `duree_jours` intacts !"
                )
            },
            {
                "heading": "2. Le problème critique de la non-idempotence de `POST` sur les réseaux instables",
                "body": (
                    "Imaginez le scénario réel suivant :\n"
                    "1. Une application mobile envoie `POST /api/v1/paiements` (`{\"montant\": 25000}`).\n"
                    "2. Le serveur Tornado reçoit la requête, débite les 25 000 DZD et renvoie `201 Created`.\n"
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
                    "2. Lors du 1er appel, le `RequestHandler` vérifie `self.request.headers.get('Idempotency-Key')` dans son cache d'idempotence. Comme "
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
            "title": "Comparatif Technique : `POST` vs `PUT` vs `PATCH` dans Tornado",
            "headers": ["Critère", "`POST /api/formations` (`def post`)", "`PUT /api/formations/1` (`def put`)", "`PATCH /api/formations/1` (`def patch`)"],
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
                "good": "Dans `def patch(self, id):`, ne mettre à jour une clé que `if cle in corps:`",
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
    # JOUR 3 — CHAPITRE 3.3 : GESTIONNAIRES D'ERREURS GLOBAUX (WRITE_ERROR & DEFAULT_HANDLER_CLASS)
    # =========================================================================
    "d3-l3": {
        "context": (
            "Par défaut, lorsqu'un client appelle une URL qui n'existe pas (`/api/introuvable`), utilise une méthode HTTP non implémentée "
            "(`DELETE /api/catalogue`) ou déclenche une exception non gérée, Tornado renvoie **une page Web HTML** "
            "(`<html><title>404: Not Found</title><body>404: Not Found</body></html>`) !\n"
            "Or, le programme client qui consomme votre API s'attend à recevoir du JSON et exécute `response.json()` : "
            "en recevant le caractère `<` de `<html>`, le client plante avec une erreur fatale "
            "`SyntaxError: Unexpected token '<'` ! Ce chapitre montre comment surcharger `write_error` et `default_handler_class` "
            "pour garantir un contrat **100 % JSON en toutes circonstances**."
        ),
        "deep_sections": [
            {
                "heading": "1. Intercepter toutes les erreurs HTTP dans `BaseJSONHandler.write_error(self, status_code, **kwargs)`",
                "body": (
                    "Dans Tornado, chaque fois qu'une erreur HTTP survient (que ce soit un verbe non supporté `405 Method Not Allowed`, "
                    "un appel à `self.send_error(400)` ou une exception Python imprévue `500`), Tornado appelle la méthode "
                    "**`write_error(self, status_code: int, **kwargs)`** du `RequestHandler`.\n"
                    "En surchargeant `write_error` dans votre classe de base `BaseJSONHandler`, vous remplacez la page HTML par défaut "
                    "par un dictionnaire JSON RFC 7807 (`application/problem+json`) contenant `status`, `title`, `detail` et `instance` (`self.request.path`)."
                )
            },
            {
                "heading": "2. Intercepter les URLs inconnues (`404`) avec `default_handler_class`",
                "body": (
                    "Lorsqu'une requête ne correspond à aucune expression régulière de `tornado.web.Application`, aucun de vos handlers "
                    "métier n'est trouvé.\n"
                    "En passant **`default_handler_class=NotFoundJSONHandler`** (une sous-classe de `BaseJSONHandler` dont `prepare(self)` "
                    "appelle `raise tornado.web.HTTPError(404)`) aux paramètres de `tornado.web.Application`, même les URLs totalement "
                    "inconnues passent par `write_error(404)` et retournent un JSON propre !"
                )
            },
            {
                "heading": "3. Masquage des erreurs `500` (`exc_info`) et Corrélation (`X-Request-ID`)",
                "body": (
                    "Que se passe-t-il si un bug imprévu (une division par zéro ou une base SQL momentanément verrouillée) "
                    "survient au milieu d'une méthode `get(self)` en production ?\n"
                    "Tornado capture l'exception et appelle `write_error(500, exc_info=sys.exc_info())` :\n"
                    "1. Vous enregistrez la trace complète du bug dans les journaux internes du serveur avec `self.request_id`.\n"
                    "2. Vous renvoyez au client un JSON propre **`500 Internal Server Error`** qui ne divulgue **aucun secret "
                    "ni chemin de fichier interne**."
                )
            }
        ],
        "architecture_diagram": (
            "COMPORTEMENT PAR DÉFAUT DE TORNADO vs SURCHARGE WRITE_ERROR & DEFAULT_HANDLER_CLASS :\n\n"
            "  Client appelle GET /api/url-inconnue\n"
            "     |\n"
            "     +---> [Sans default_handler_class] ---> Renvoie \"<html><title>404: Not Found</title>\" ---> CRASH JSON.parse() Client !\n"
            "     |\n"
            "     +---> [Avec NotFoundJSONHandler]   ---> Appelle write_error(404) ---> {\"status\": 404, \"title\": \"Not Found\", ...}\n"
            "                                             (Content-Type: application/problem+json) ---> Géré proprement par le Client !"
        ),
        "reference_table": {
            "title": "Mécanismes Globaux de Gestion d'Erreurs dans une API Tornado",
            "headers": ["Mécanisme Tornado", "Déclencheur", "Information utile à inclure dans le JSON de retour"],
            "rows": [
                ["`raise tornado.web.HTTPError(400, reason=...)`", "Requête mal formée", "`status: 400`, `detail: \"Syntaxe de requête ou JSON invalide\"`"],
                ["`default_handler_class=NotFoundJSONHandler`", "URL inconnue (`404`)", "`status: 404`, `instance: self.request.path`, `detail: \"Route introuvable\"`"],
                ["`write_error(405)`", "Verbe HTTP non implémenté sur ce Handler", "`status: 405`, `method: self.request.method`, `detail: \"Méthode non autorisée\"`"],
                ["`write_error(500, exc_info=...)`", "Bug Python non intercepté (`500`)", "`status: 500`, `request_id: self.request_id` (sans Traceback !)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Laisser `debug=True` actif dans `tornado.web.Application` sur un serveur exposé sur Internet",
                "good": "Toujours forcer `debug=False` en production et surcharger `write_error`",
                "why": "Le mode `debug=True` affiche la pile d'exécution complète (Traceback) en cas d'erreur 500, exposant la structure interne du code."
            },
            {
                "bad": "Surcharger `write_error` dans ses handlers mais oublier `default_handler_class` sur `Application`",
                "good": "Toujours configurer `default_handler_class=NotFoundJSONHandler` dans `tornado.web.Application`",
                "why": "Sans `default_handler_class`, les URLs qui ne matchent aucune regex sont traitées par le `ErrorHandler` interne de Tornado qui renvoie du HTML."
            }
        ],
        "practical_exercises": [
            "Exécutez le script dans l'atelier ci-dessus pour vérifier que les erreurs `404`, `405` et `500` renvoient toutes `Content-Type: application/problem+json`.",
            "Testez `GET /api/sandbox/formations/999` dans le Client HTTP pour observer une réponse `404` en JSON."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.4 : PERSISTANCE SQLITE3, ACID & INJECTIONS SQL
    # =========================================================================
    "d3-l4": {
        "context": (
            "Stocker les données dans une liste Python `FORMATIONS = [...]` présente une limite rédhibitoire : la "
            "liste réside en mémoire vive (RAM). Dès que vous redémarrez le serveur Tornado ou qu'une coupure électrique "
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
                    "anonyme `(1, 'API Tornado', 5)`. En activant `sqlite3.Row`, chaque ligne se comporte comme un dictionnaire "
                    "convertible instantanément par `dict(row)` -> `{\"id\": 1, \"titre\": \"API Tornado\", \"duree_jours\": 5}` !"
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
                    "- Plutôt que de laisser cette exception provoquer une erreur `500`, le `RequestHandler` intercepte `except sqlite3.IntegrityError:` "
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
            "title": "Correspondance Opérations CRUD ↔ Méthodes Tornado ↔ Commandes SQL Paramétrées",
            "headers": ["Opération CRUD", "Route & Méthode Tornado", "Requête SQLite Paramétrée (`sqlite3`)", "Méthode de lecture résultat"],
            "rows": [
                ["**Create** (Créer)", "`POST /api/formations` (`def post`)", "`cur.execute(\"INSERT INTO formations (titre, salle) VALUES (?, ?)\", (t, s))` + `conn.commit()`", "`new_id = cur.lastrowid`"],
                ["**Read All** (Lister)", "`GET /api/formations` (`def get`)", "`conn.execute(\"SELECT * FROM formations LIMIT ? OFFSET ?\", (limit, offset))`", "`[dict(r) for r in cur.fetchall()]`"],
                ["**Read One** (Lire 1)", "`GET /api/formations/([0-9]+)` (`def get`)", "`conn.execute(\"SELECT * FROM formations WHERE id = ?\", (id,))`", "`row = cur.fetchone()` (`404` si `None`)"],
                ["**Update** (Modifier)", "`PUT /api/formations/([0-9]+)` (`def put`)", "`conn.execute(\"UPDATE formations SET titre = ?, salle = ? WHERE id = ?\", (t, s, id))` + `conn.commit()`", "`cur.rowcount`"],
                ["**Delete** (Supprimer)", "`DELETE /api/formations/([0-9]+)` (`def delete`)", "`conn.execute(\"DELETE FROM formations WHERE id = ?\", (id,))` + `conn.commit()`", "`200 OK` ou `204 No Content`"]
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
