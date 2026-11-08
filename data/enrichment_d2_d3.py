"""
Manuel de Référence Approfondi — Enrichissement des Chapitres (Jours 2 et 3).
"""

ENRICHMENT_D2_D3 = {
    # =========================================================================
    # JOUR 2 — CHAPITRE 2.1 : SERVEUR MINIMAL FLASK, WSGI & TABLE DE ROUTAGE
    # =========================================================================
    "d2-l1": {
        "context": (
            "Après avoir compris les fondations Python (Jour 0) et le protocole réseau HTTP/JSON (Jour 1), nous "
            "construisons notre premier serveur d'API avec **Flask**.\n"
            "Pourquoi Flask est-il considéré comme le meilleur framework pour maîtriser l'ingénierie des APIs ? "
            "Parce qu'il repose sur une philosophie minimaliste et explicite : il ne cache rien sous le tapis. "
            "Ce chapitre explique comment un script Python qui se terminait en une milliseconde devient un **démon "
            "réseau en écoute permanente**, comment fonctionne la norme **WSGI**, et comment Flask aiguille chaque "
            "URL vers la bonne fonction grâce à sa table de routage (`url_map`)."
        ),
        "deep_sections": [
            {
                "heading": "1. Du Script Éphémère au Serveur Daemon : le rôle de la boucle d'écoute Socket",
                "body": (
                    "Un script Python classique exécute ses lignes de haut en bas puis s'arrête : son processus disparaît "
                    "de la mémoire.\n"
                    "Un serveur Web, au contraire, doit rester **en éveil 24h/24** pour répondre aux clients à tout instant :\n"
                    "- Lorsque vous appelez `app.run(host=\"0.0.0.0\", port=5000)`, Flask demande au système d'exploitation "
                    "Linux/Windows d'ouvrir un **Socket TCP d'écoute** attaché au port `5000`.\n"
                    "- Il entre alors dans une boucle infinie (`while True:`) qui attend l'arrivée de paquets TCP.\n"
                    "- Dès qu'un client se connecte, le serveur lit la trame HTTP brute, trouve la fonction Python associée "
                    "à l'URL, l'exécute, renvoie la trame HTTP de réponse, puis se remet immédiatement en attente du client suivant."
                )
            },
            {
                "heading": "2. Qu'est-ce que la norme WSGI (Web Server Gateway Interface — PEP 3333) ?",
                "body": (
                    "Dans l'écosystème Python, les serveurs Web (comme Gunicorn, uWSGI ou Werkzeug) et les frameworks "
                    "applicatifs (comme Flask ou Django) parlent une langue commune normalisée appelée **WSGI** :\n"
                    "- Le serveur HTTP reçoit les octets bruts du réseau et les traduit en un dictionnaire Python standardisé "
                    "appelé `environ` (contenant `REQUEST_METHOD`, `PATH_INFO`, `QUERY_STRING`, `HTTP_AUTHORIZATION`).\n"
                    "- Il appelle ensuite votre objet `app = Flask(__name__)` en lui passant ce dictionnaire.\n"
                    "- Flask construit alors l'objet convivial `request`, exécute votre fonction de route, et restitue le "
                    "statut HTTP, les en-têtes et les octets JSON au serveur WSGI."
                )
            },
            {
                "heading": "3. Pourquoi toujours utiliser `jsonify()` plutôt que `json.dumps()` dans une route Flask ?",
                "body": (
                    "Si vous écrivez `return json.dumps({\"statut\": \"OK\"})` dans une route Flask, Flask considère que "
                    "vous renvoyez une simple chaîne de texte HTML et positionne l'en-tête **`Content-Type: text/html; charset=utf-8`** !\n"
                    "La fonction **`jsonify({...})`** de Flask accomplit 3 opérations indispensables :\n"
                    "1. Elle sérialise votre dictionnaire Python en chaîne JSON UTF-8 valide.\n"
                    "2. Elle crée un objet `flask.Response` complet.\n"
                    "3. Elle injecte automatiquement l'en-tête officiel **`Content-Type: application/json`**."
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
            "Exécutez le code dans l'atelier ci-dessus pour inspecter le contenu réel de `app.url_map`.",
            "Ajoutez une 3ème route `@app.route(\"/api/v1/version\", methods=[\"GET\"])` dans l'exécuteur et vérifiez qu'elle apparaît immédiatement dans la table de routage."
        ]
    },

    # =========================================================================
    # JOUR 2 — CHAPITRE 2.2 : MATURITÉ REST (RICHARDSON) & PARAMÈTRES D'URL
    # =========================================================================
    "d2-l2": {
        "context": (
            "N'importe qui peut créer une URL `/api/faireQuelqueChose` qui renvoie du JSON, mais cela n'en fait pas "
            "une API **RESTful** professionnelle.\n"
            "Comment les géants technologiques (Stripe, GitHub, Twilio, Google Cloud) nomment-ils leurs URLs pour "
            "qu'un développeur externe comprenne intuitivement toute l'API en 5 minutes ? Et comment extraire "
            "proprement un identifiant d'entité (`/formations/42`) ou un critère de recherche (`?salle=Alger`) dans "
            "Flask ? Ce chapitre formalise le **Modèle de Maturité de Richardson** et l'anatomie de l'objet `flask.request`."
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
                    "(`/api/v1/formations/42`) et le **verbe HTTP** exprime l'action (`GET` pour lire, `POST` pour créer, `PUT`/`PATCH` "
                    "pour modifier, `DELETE` pour supprimer), tandis que la réponse utilise le code de statut exact (`200`, `201`, `404`, `422`).\n"
                    "- **Niveau 3 (HATEOAS)** : La réponse JSON inclut en plus des liens de navigation (`\"links\": {\"self\": \"/api/v1/formations/42\"}`)."
                )
            },
            {
                "heading": "2. Path Parameters (`<int:id>`) vs Query Parameters (`request.args`) : la règle de décision",
                "body": (
                    "Quand faut-il mettre un paramètre dans le chemin (`/formations/42`) et quand faut-il le mettre après `?` (`?salle=Alger`) ?\n"
                    "- **Paramètre de Chemin (`Path Parameter` : `/api/formations/<int:formation_id>`)** : Utilisé pour "
                    "**identifier de manière unique une ressource précise**. Si l'identifiant n'existe pas, le serveur renvoie "
                    "**`404 Not Found`**. De plus, le convertisseur `<int:...>` de Flask valide automatiquement que la valeur "
                    "est un entier avant même d'appeler votre fonction !\n"
                    "- **Paramètre de Requête (`Query Parameter` : `/api/formations?salle=Alger&duree_min=3`)** : Utilisé pour "
                    "**filtrer, trier, rechercher ou paginer** une collection. Si aucune formation ne correspond au filtre `?salle=Oran`, "
                    "ce n'est **pas** une erreur `404` : la collection existe bien, elle renvoie simplement **`200 OK` avec une liste vide `[]`** !"
                )
            },
            {
                "heading": "3. Le typage automatique avec `request.args.get('cle', defaut, type=int)`",
                "body": (
                    "Dans une URL (`?duree_min=3`), tout paramètre est initialement reçu sous forme de chaîne de caractères "
                    "`\"3\"`.\n"
                    "Au lieu d'écrire un bloc `try: int(...) except ValueError:` sur chaque paramètre de filtre, la méthode "
                    "`request.args.get(\"duree_min\", default=1, type=int)` de Flask tente de convertir la valeur en `int` : "
                    "si le client envoie `?duree_min=abc`, Flask ne plante pas et retourne proprement la valeur `default=1`."
                )
            }
        ],
        "architecture_diagram": (
            "COMPARAISON ARCHITECTURALE : ANTI-PATTERN RPC vs STANDARD REST (NIVEAU 2)\n"
            "  [ANTI-PATTERN RPC]                       [STANDARD RESTFUL (Noms au pluriel + Verbes HTTP)]\n"
            "  GET  /api/getAllFormations       ===>    GET    /api/v1/formations\n"
            "  GET  /api/getFormationById?id=5  ===>    GET    /api/v1/formations/5\n"
            "  POST /api/createNewFormation     ===>    POST   /api/v1/formations\n"
            "  POST /api/updateFormation/5      ===>    PUT    /api/v1/formations/5\n"
            "  GET  /api/deleteFormation?id=5   ===>    DELETE /api/v1/formations/5"
        ),
        "reference_table": {
            "title": "Les Propriétés de l'Objet `flask.request` pour Lire Toute Entrée Client",
            "headers": ["Propriété Flask", "Source dans la trame HTTP", "Exemple d'entrée client", "Syntaxe de lecture sécurisée"],
            "rows": [
                ["Paramètre de fonction", "Chemin URL (`Path`)", "`GET /api/formations/42`", "`def get_one(formation_id):` via `<int:formation_id>`"],
                ["`request.args`", "Query String (après `?`)", "`GET /api/formations?salle=Alger&page=2`", "`request.args.get(\"page\", 1, type=int)`"],
                ["`request.headers`", "En-têtes HTTP (`Headers`)", "`X-API-Key: secret`", "`request.headers.get(\"X-API-Key\", \"\")`"],
                ["`request.get_json()`", "Corps (`Body` JSON)", "`{\"titre\": \"Flask\", \"jours\": 5}`", "`corps = request.get_json(silent=True) or {}`"],
                ["`request.method`", "Request Line (Verbe)", "`POST`, `GET`, `DELETE`", "`if request.method == \"POST\":`"],
                ["`request.remote_addr`", "Socket réseau TCP", "`127.0.0.1` / `192.168.1.25`", "Utilisé pour les journaux d'audit et le Rate Limiting"]
            ]
        },
        "pitfalls": [
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
            "Dans l'exécuteur ci-dessus, modifiez l'appel simulé pour tester `test_request_context('/api/formations?salle=Alger&duree_min=4')`.",
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
                "heading": "2. Pourquoi borner impérativement `page` et `limit` côté serveur (Protection Anti-DoS)",
                "body": (
                    "Si vous écrivez simplement `limit = request.args.get('limit', 10, type=int)`, qu'arrive-t-il si un "
                    "utilisateur malveillant appelle `?page=-5&limit=999999999` ?\n"
                    "- Un `page` négatif produirait un `offset` négatif incohérent.\n"
                    "- Un `limit` de 1 milliard contournerait toute votre protection de pagination !\n"
                    "On encadre donc toujours les deux valeurs par `max()` et `min()` :\n"
                    "- `page = max(1, request.args.get(\"page\", 1, type=int))` (au minimum page 1).\n"
                    "- `limit = min(50, max(1, request.args.get(\"limit\", 10, type=int)))` (entre 1 et 50 éléments maximum par appel)."
                )
            },
            {
                "heading": "3. Validation par Liste Blanche (Whitelist) du Tri Dynamique (`?tri=...&ordre=...`)",
                "body": (
                    "Pour permettre au client de trier les résultats (`?tri=duree_jours&ordre=desc`), le serveur ne doit "
                    "**jamais** utiliser directement la chaîne envoyée par le client comme nom de clé ou colonne SQL sans vérification.\n"
                    "On définit un tuple immuable de colonnes autorisées :\n"
                    "`CHAMPS_TRI_AUTORISES = (\"id\", \"duree_jours\", \"titre\")`.\n"
                    "Si `champ_tri not in CHAMPS_TRI_AUTORISES`, le serveur rejette immédiatement la requête avec un code "
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
    # JOUR 2 — CHAPITRE 2.4 : MIDDLEWARES (@BEFORE_REQUEST / @AFTER_REQUEST)
    # =========================================================================
    "d2-l4": {
        "context": (
            "Lorsqu'une API compte 50 routes, comment mesurer le temps d'exécution exact en millisecondes de chaque "
            "appel, attribuer un numéro de suivi unique (`X-Request-ID`) et ajouter des en-têtes de sécurité sans "
            "copier-coller les mêmes lignes dans les 50 fonctions ?\n"
            "La réponse architecturale s'appelle un **Middleware** (ou *Hook de cycle de vie*). Dans Flask, les "
            "décorateurs **`@app.before_request`** et **`@app.after_request`** permettent d'intercepter 100 % du "
            "trafic à l'entrée et à la sortie du serveur."
        ),
        "deep_sections": [
            {
                "heading": "1. Les 3 phases du Cycle de Vie d'une Requête dans Flask",
                "body": (
                    "Chaque requête HTTP qui franchit la porte de Flask traverse séquentiellement trois étapes :\n"
                    "1. **Phase Prétraitement (`@app.before_request`)** : S'exécute **avant** la fonction de route. Idéal "
                    "pour démarrer un chronomètre haute précision (`time.perf_counter()`), extraire ou générer un `X-Request-ID`, "
                    "ou bloquer globalement une adresse IP bannie (si une fonction `before_request` fait un `return`, Flask "
                    "s'arrête immédiatement et n'appelle même pas la route !).\n"
                    "2. **Phase Métier (View Function / Route Handler)** : Exécute la logique de la route ciblée et produit "
                    "l'objet `Response`.\n"
                    "3. **Phase Post-traitement (`@app.after_request`)** : Reçoit l'objet `reponse` juste avant son départ "
                    "sur le réseau. Permet d'injecter les en-têtes `X-Request-ID`, `X-Response-Time-Ms`, les en-têtes CORS "
                    "et d'écrire une ligne d'audit dans les journaux du serveur. Elle doit **toujours retourner `reponse`**."
                )
            },
            {
                "heading": "2. Pourquoi utiliser `flask.g` plutôt qu'une variable globale Python ?",
                "body": (
                    "Comment transmettre l'heure de début `heure_debut` mesurée dans `@app.before_request` à la fonction "
                    "`@app.after_request` ?\n"
                    "- **Danger d'une variable globale** : Sur un serveur multi-threads où deux clients A et B appellent "
                    "l'API au même instant, une variable globale `HEURE_DEBUT` serait écrasée par le client B pendant que "
                    "la requête du client A est en cours d'exécution (*Race Condition*) !\n"
                    "- **La solution `flask.g`** : L'objet `g` de Flask est un espace mémoire **isolé par requête** (*Context-Local*). "
                    "Ce que la requête du client A écrit dans `g.request_id` et `g.heure_debut` est totalement invisible pour "
                    "le client B et est automatiquement nettoyé dès la fin de la requête."
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
            "Exécutez le script `day_2/04_middlewares_et_audit_log.py` dans l'atelier ci-dessus pour observer l'injection automatique de `X-Request-ID` et `X-Response-Time-Ms`.",
            "Modifiez l'appel simulé dans l'atelier pour passer un en-tête personnalisé `headers={'X-Request-ID': 'trace-isgp-001'}` et vérifiez que le serveur conserve cet identifiant."
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
            "les payloads entrants et structurer les réponses d'erreur selon la norme internationale **RFC 7807 (Problem Details)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Lecture sécurisée du Corps JSON avec `request.get_json(silent=True)`",
                "body": (
                    "Dans Flask, lorsque vous appelez `request.get_json()` sans paramètre sur une requête dont le JSON est "
                    "mal formé (par exemple une virgule en trop), Flask lève une exception interne et renvoie une page d'erreur "
                    "HTML par défaut.\n"
                    "En écrivant **`corps = request.get_json(silent=True)`** :\n"
                    "- Si le corps est absent ou syntaxiquement invalide, la fonction ne plante pas et renvoie proprement `None`.\n"
                    "- Vous pouvez alors tester `if not isinstance(corps, dict):` et renvoyer vous-même une réponse JSON "
                    "explicite avec le code **`400 Bad Request`**."
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
            "Ce chapitre apporte la réponse complète et l'implémentation de référence en Python/Flask."
        ),
        "deep_sections": [
            {
                "heading": "1. Remplacement Intégral (`PUT`) vs Modification Partielle (`PATCH` — RFC 5789)",
                "body": (
                    "Supposons que la formation `#1` contienne : `{\"id\": 1, \"titre\": \"Flask\", \"duree_jours\": 5, \"salle\": \"Labo 1\"}`.\n"
                    "- **Avec `PUT /api/v1/formations/1`** : La sémantique officielle de `PUT` est « **Remplacer l'intégralité "
                    "de la fiche #1 par le document fourni** ». Le client doit donc envoyer **tous les champs obligatoires** "
                    "(`titre`, `duree_jours`, `salle`). Tout champ non fourni est réinitialisé à sa valeur par défaut.\n"
                    "- **Avec `PATCH /api/v1/formations/1`** : La sémantique de `PATCH` est « **Appliquer une modification "
                    "partielle** ». Si vous voulez uniquement déménager la formation dans la `\"Salle B\"`, vous envoyez "
                    "uniquement `{\"salle\": \"Salle B\"}` : le serveur conserve le `titre` et la `duree_jours` intacts !"
                )
            },
            {
                "heading": "2. Le problème critique de la non-idempotence de `POST` sur les réseaux instables",
                "body": (
                    "Imaginez le scénario réel suivant :\n"
                    "1. Une application mobile envoie `POST /api/v1/paiements` (`{\"montant\": 25000}`).\n"
                    "2. Le serveur Flask reçoit la requête, débite les 25 000 DZD et renvoie `201 Created`.\n"
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
            "Exécutez le script dans l'atelier ci-dessus pour observer comment les deux appels `POST` portant la même `Idempotency-Key` produisent une seule transaction.",
            "Dans l'onglet **curl & Postman**, testez la commande `2.4 — PATCH` pour modifier uniquement la salle de la formation `#1`."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.3 : GESTIONNAIRES D'ERREURS GLOBAUX (@ERRORHANDLER)
    # =========================================================================
    "d3-l3": {
        "context": (
            "Par défaut, Flask a été conçu à la fois pour les sites Web HTML et pour les APIs. Conséquence : si un "
            "client appelle une URL qui n'existe pas (`/api/introuvable`) ou utilise une mauvaise méthode HTTP "
            "(`DELETE /api/bonjour`), Flask renvoie **une page Web HTML** (`<!doctype html><title>404 Not Found</title>...`) !\n"
            "Or, le programme client qui consomme votre API s'attend à recevoir du JSON et exécute `response.json()` : "
            "en recevant le caractère `<` de `<!doctype html>`, le client plante avec une erreur fatale "
            "`SyntaxError: Unexpected token '<', \"<!doctype \"... is not valid JSON` ! Ce chapitre montre comment "
            "garantir un contrat **100 % JSON en toutes circonstances**."
        ),
        "deep_sections": [
            {
                "heading": "1. Intercepter les erreurs de routage HTTP (`404 Not Found` et `405 Method Not Allowed`)",
                "body": (
                    "Lorsqu'une requête n'aboutit à aucune fonction `@app.route(...)`, elle est rejetée par le routeur "
                    "Werkzeug avant même d'atteindre votre code métier :\n"
                    "- **Erreur `404 Not Found`** : L'URL demandée n'existe pas dans `app.url_map`.\n"
                    "- **Erreur `405 Method Not Allowed`** : L'URL existe bien dans `app.url_map` (par exemple `/api/catalogue` "
                    "accepte `GET`), mais le client a utilisé un verbe non autorisé (ex: `DELETE /api/catalogue`).\n"
                    "En déclarant `@app.errorhandler(404)` et `@app.errorhandler(405)`, vous remplacez la réponse HTML de "
                    "Werkzeug par un dictionnaire JSON normé indiquant le chemin exact et la méthode en cause."
                )
            },
            {
                "heading": "2. Le Filet de Sécurité Ultime : `@app.errorhandler(Exception)` et Masquage `500`",
                "body": (
                    "Que se passe-t-il si un bug imprévu (une division par zéro ou une base SQL momentanément verrouillée) "
                    "survient au milieu d'une route en production ?\n"
                    "Grâce à `@app.errorhandler(Exception)` :\n"
                    "1. Vous vérifiez d'abord `if isinstance(err, HTTPException): return err` pour laisser passer les erreurs HTTP normales.\n"
                    "2. Vous enregistrez la trace complète du bug dans les journaux internes du serveur (`app.logger.exception(err)`) "
                    "pour que l'équipe technique puisse la corriger.\n"
                    "3. Vous renvoyez au client un JSON propre **`500 Internal Server Error`** qui ne divulgue **aucun secret "
                    "ni chemin de fichier interne**."
                )
            },
            {
                "heading": "3. Traçabilité et Corrélation des Incidents en Production (`X-Request-ID`)",
                "body": (
                    "Lorsqu'un client reçoit une réponse générique `500 Internal Server Error` masquée pour des raisons de sécurité, "
                    "comment l'équipe de support technique retrouve-t-elle l'erreur exacte parmi des millions de lignes de logs serveur ?\n"
                    "- À l'entrée de chaque requête (`@app.before_request`), le serveur génère un identifiant unique `req_id = uuid.uuid4().hex[:8]`.\n"
                    "- En cas d'exception `500`, cet identifiant est inscrit simultanément dans le fichier de log privé **et** dans le JSON "
                    "renvoyé au client (`\"request_id\": \"req-8f2a9c01\"`), permettant un diagnostic instantané sans exposer la pile d'exécution."
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
            "Exécutez le script dans l'atelier ci-dessus pour vérifier que les erreurs `404`, `405` et `500` renvoient toutes `Content-Type: application/json`.",
            "Testez `GET /api/sandbox/formations/999` dans le Client HTTP pour observer une réponse `404` en JSON."
        ]
    },

    # =========================================================================
    # JOUR 3 — CHAPITRE 3.4 : PERSISTANCE SQLITE3, ACID & INJECTIONS SQL
    # =========================================================================
    "d3-l4": {
        "context": (
            "Stocker les données dans une liste Python `FORMATIONS = [...]` présente une limite rédhibitoire : la "
            "liste réside en mémoire vive (RAM). Dès que vous redémarrez le serveur Flask ou qu'une coupure électrique "
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
                    "anonyme `(1, 'API Flask', 5)`. En activant `sqlite3.Row`, chaque ligne se comporte comme un dictionnaire "
                    "convertible instantanément par `dict(row)` -> `{\"id\": 1, \"titre\": \"API Flask\", \"duree_jours\": 5}` !"
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
