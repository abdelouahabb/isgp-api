import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_1_DATA = {
    "day_number": 1,
    "folder": "day_1",
    "badge": "Jour 1 • Protocoles & Architecture Web",
    "title": "Ingénierie des Services Web : Paradigmes (SOAP vs REST), Pile Réseau, Trames HTTP/1.1, Idempotence & JSON",
    "goal": "Comprendre l'évolution historique des services Web (HTML, SOAP/XML, REST/JSON, GraphQL, gRPC), décoder la pile réseau (DNS, IP, Port TCP, TLS), inspecter une trame HTTP brute, maîtriser la propriété d'idempotence des verbes HTTP et structurer des enveloppes JSON professionnelles avec Tornado.",
    "starter_filename": "day_1/04_trame_http_et_headers.py",
    "files": [
        "day_1/01_html_vs_json.py",
        "day_1/03_analyseur_uri_et_reseau.py",
        "day_1/04_trame_http_et_headers.py",
        "day_1/02_serialisation_json.py",
        "day_1/05_outils_curl_postman_httpie.py",
    ],
    "lessons": [
        {
            "id": "d1-l1",
            "file": "day_1/01_html_vs_json.py",
            "title": "1.1 — Évolution & Paradigmes des Services Web : Du Monolithe HTML à SOAP/XML, REST/JSON, GraphQL & gRPC",
            "duration": "55 min",
            "analogy": {
                "title": "L'affiche imprimée (HTML), l'acte notarié scellé (SOAP/XML) et le colis modulaire standardisé (REST/JSON)",
                "text": (
                    "Durant la première décennie du Web, les serveurs d'entreprise se comportaient comme des imprimeries : ils exécutaient une requête SQL puis fusionnaient directement les chiffres obtenus dans une page **HTML** truffée de balises graphiques destinées à la rétine humaine. "
                    "Mais dès qu'un système bancaire partenaire, un terminal mobile natif ou un automate industriel a dû interroger ces mêmes serveurs par programme, le couplage entre fond métier et forme visuelle est devenu intenable : la moindre refonte esthétique d'une balise `<div>` brisait instantanément les intégrations clientes.\n\n"
                    "Pour affranchir l'échange de données de toute couche de présentation, l'industrie a d'abord conçu **SOAP/XML**, comparable à un acte notarié solennel enfermé dans de lourdes enveloppes protocolaires rigides, avant de converger massivement vers **REST/JSON**, véritable conteneur intermodal léger qui exploite nativement la sémantique du protocole HTTP."
                )
            },
            "explanation": [
                (
                    "**Interopérabilité machine-à-machine (M2M) et neutralité technologique d'un Service Web.** "
                    "Au sens strict de l'ingénierie des systèmes distribués, un Service Web expose des capacités métier sur un réseau IP au moyen de messages structurés totalement indépendants du langage d'implémentation ou du système d'exploitation. "
                    "Grâce à ce découplage contractuel, un progiciel comptable écrit en Java ou C#, une application mobile Kotlin/Swift et un frontal React consomment simultanément la même instance Python Tornado sans jamais connaître l'organisation interne de ses classes ni de ses tables SQL."
                ),
                (
                    "**Panorama architectural des quatre paradigmes industriels (SOAP, REST, GraphQL, gRPC).** "
                    "Alors que **SOAP** (années 2000) tunnelise des enveloppes XML verbeuses régies par des contrats WSDL/XSD sur un point d'entrée unique au prix d'une empreinte réseau et CPU élevée, l'architecture **REST** formalisée par Roy Fielding en 2000 aligne directement les opérations sur les primitives natives de HTTP (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`, codes de statut et cache) couplées à la légèreté de **JSON**, propulsant aujourd'hui plus de 85 % des APIs d'entreprise. "
                    "En complément ciblé, **GraphQL** répond aux besoins d'agrégation granulaire des interfaces mobiles complexes sur un graphe unique, tandis que **gRPC** sérialise des trames binaires *Protocol Buffers* sur HTTP/2 multiplexé pour les communications Est-Ouest à ultra-basse latence entre microservices internes."
                ),
                (
                    "**Polymorphisme de représentation au sein d'un `RequestHandler` Tornado.** "
                    "Une même donnée métier en mémoire Python peut être projetée sous trois représentations distinctes selon les méthodes invoquées sur le contrôleur Tornado : `self.render('meteo.html', meteo=...)` compile et restitue une vue HTML destinée aux navigateurs via `tornado.template`, l'association `self.set_header('Content-Type', 'application/xml; charset=UTF-8')` suivie de `self.write(flux_xml)` émet une enveloppe SOAP/XML conforme aux systèmes patrimoniaux, tandis que l'appel idiomatique `self.write(DONNEES_METEO)` sur un dictionnaire Python sérialise nativement la charge utile en JSON UTF-8 et positionne automatiquement l'en-tête `Content-Type: application/json; charset=UTF-8`."
                )
            ],
            "code": _read("01_html_vs_json.py"),
            "line_explanations": [
                {"lines": "26-29", "text": "`MeteoHtmlHandler` : `self.render('meteo.html', meteo=DONNEES_METEO)` injecte le dictionnaire dans le gabarit HTML `tornado.template`."},
                {"lines": "33-47", "text": "`MeteoSoapHandler` : définit `self.set_header('Content-Type', 'application/xml; charset=UTF-8')` et écrit l'enveloppe XML verbeuse."},
                {"lines": "51-56", "text": "`MeteoJsonHandler` : passer un `dict` Python à `self.write(DONNEES_METEO)` le sérialise automatiquement en JSON (`application/json; charset=UTF-8`)."},
                {"lines": "59-67", "text": "`make_app()` configure `tornado.web.Application` en associant chaque expression régulière d'URL à sa classe `RequestHandler`."},
                {"lines": "70-86", "text": "Test asynchrone non-bloquant avec `tornado.httpclient.AsyncHTTPClient` mesurant la taille exacte en octets et le `Content-Type` des 3 formats."}
            ],
            "sandbox_preset": {
                "label": "Tester une réponse REST/JSON réelle : GET /api/sandbox/meteo?ville=Alger",
                "method": "GET",
                "url": "/api/sandbox/meteo?ville=Alger",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez day_1/01_html_vs_json.py pour comparer l'empreinte en octets de HTML, SOAP/XML et REST/JSON dans Tornado :",
                "initial_code": _read("01_html_vs_json.py")
            },
            "vscode_instructions": {
                "filename": "day_1/01_html_vs_json.py",
                "steps": [
                    "Ouvrir `day_1/01_html_vs_json.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_1/01_html_vs_json.py`."
                ]
            }
        },
        {
            "id": "d1-l2",
            "file": "day_1/03_analyseur_uri_et_reseau.py",
            "title": "1.2 — La Pile Réseau Décodée (DNS, IP, Port TCP, TLS) & Anatomie d'une URI (RFC 3986)",
            "duration": "55 min",
            "analogy": {
                "title": "L'annuaire téléphonique (DNS), le bâtiment (IP), le guichet (Port) et le couloir sécurisé (TLS)",
                "text": (
                    "Lorsqu'une application cliente invoque `https://api.isgp.dz:8443/api/v1/formations?ville=Alger`, aucune donnée applicative ne part immédiatement sur le fil : le système d'exploitation traverse d'abord quatre couches réseau rigoureusement ordonnées en quelques millisecondes.\n\n"
                    "Il consulte l'annuaire **DNS** pour convertir le nom lisible en adresse numérique **IP** identifiant l'immeuble serveur sur Internet, frappe au numéro de guichet **Port TCP** correspondant au processus Tornado en écoute, scelle un tunnel chiffré **TLS** contre toute écoute clandestine, puis dépose enfin la trame HTTP dans le descripteur de socket surveillé par la boucle d'événements `IOLoop`."
                )
            },
            "explanation": [
                (
                    "**Séquence d'établissement d'une session réseau avant notification de l'`IOLoop`.** "
                    "Tout appel d'API débute par la résolution **DNS** traduisant un nom d'hôte tel que `api.isgp.dz` en adresse routable IPv4 ou IPv6 (tandis que `localhost` court-circuite la carte physique vers la boucle locale `127.0.0.1`), suivie de la poignée de main **TCP en trois temps** (`SYN`, `SYN-ACK`, `ACK`) vers le couple `IP:Port` cible (`80` en HTTP, `443` en HTTPS, `8888` par convention historique pour Tornado en développement). "
                    "Lorsque le schéma est `https://`, une négociation cryptographique **TLS 1.3** authentifie le certificat X.509 du serveur et dérive les clés symétriques de session avant que le premier octet de la requête HTTP ne parvienne au démon non bloquant `tornado.httpserver.HTTPServer`."
                ),
                (
                    "**Décomposition syntaxique normalisée d'une URI selon la RFC 3986.** "
                    "Une URI se découpe en cinq segments formels exploités distinctement par Tornado : le `scheme` (`http` ou `https`, exposé dans `self.request.protocol`) fixe le protocole de transport, l'autorité `hostname:port` (`self.request.host`) désigne le point d'ancrage réseau, et le `path` hiérarchique (`/api/v1/formations`, lu via `self.request.path`) est soumis au routeur d'expressions régulières de `tornado.web.Application`. "
                    "En aval du point d'interrogation `?`, la `query string` transporte les critères non hiérarchiques de filtrage ou de pagination (assemblés proprement côté client par `tornado.httputil.url_concat` et décodés côté serveur par `self.get_query_argument`), tandis que le `fragment` final après `#` demeure strictement confiné au navigateur client sans jamais franchir le socket TCP."
                )
            ],
            "code": _read("03_analyseur_uri_et_reseau.py"),
            "line_explanations": [
                {"lines": "5-6", "text": "`urlparse` / `parse_qs` (`urllib.parse`) et `url_concat` (`tornado.httputil`) permettent de construire et d'analyser rigoureusement toute URI."},
                {"lines": "9-10", "text": "`url_concat` assemble proprement l'URL et ses paramètres de requête avec encodage automatique."},
                {"lines": "15-22", "text": "Inspection individuelle du schéma (`https`), de l'hôte, du port TCP (`8443`), du chemin (`/api/v1/formations`) et de la query string."},
                {"lines": "24-26", "text": "Parcours des paramètres de filtrage extraits (accessibles dans un `RequestHandler` via `self.get_query_argument(cle)`)."}
            ],
            "python_runner": {
                "prompt": "Exécutez l'analyseur d'URI RFC 3986 avec tornado.httputil.url_concat :",
                "initial_code": _read("03_analyseur_uri_et_reseau.py")
            },
            "vscode_instructions": {
                "filename": "day_1/03_analyseur_uri_et_reseau.py",
                "steps": [
                    "Ouvrir `day_1/03_analyseur_uri_et_reseau.py` dans l'éditeur.",
                    "Exécuter `.venv/bin/python day_1/03_analyseur_uri_et_reseau.py`."
                ]
            }
        },
        {
            "id": "d1-l3",
            "file": "day_1/04_trame_http_et_headers.py",
            "title": "1.3 — Radiographie d'une Trame HTTP/1.1 Brute & Rôle Stratégique des En-têtes (Headers)",
            "duration": "60 min",
            "analogy": {
                "title": "Ouvrir l'enveloppe réseau au microscope",
                "text": (
                    "Nombre de développeurs manipulent quotidiennement des frameworks Web de haut niveau tout en considérant le flux réseau comme une boîte noire impénétrable. "
                    "Pourtant, le protocole **HTTP/1.1** codifié par les RFC 9110 et 9112 demeure d'une élégante lisibilité : il s'agit d'un protocole textuel structuré en lignes ASCII terminées par `\\r\\n`, où chaque message entrant ou sortant respecte invariablement la même anatomie tripartite."
                )
            },
            "explanation": [
                (
                    "**Architecture tripartite d'un message HTTP/1.1 décodé par `HTTPConnection` dans Tornado.** "
                    "Lorsque l'`IOStream` non bloquant de Tornado accumule les octets arrivant sur le socket, son analyseur syntaxique découpe d'abord la **ligne de départ** (`POST /api/v1/formations HTTP/1.1` côté requête exposant `method`, `uri` et `version` sur `self.request`, ou `HTTP/1.1 201 Created` côté réponse pilotée par `self.set_status(201)`), puis parcourt les paires d'**en-têtes HTTP** insensibles à la casse stockées dans `self.request.headers` et émises via `self.set_header()`. "
                    "Une séquence délimitrice stricte de quatre octets **`\\r\\n\\r\\n`** (deux retours chariot / sauts de ligne consécutifs formant une ligne vide) marque la frontière physique au-delà de laquelle commence le **corps binaire (`self.request.body`)**, lu sur exactement `Content-Length` octets."
                ),
                (
                    "**Six familles stratégiques d'en-têtes gouvernant le comportement d'une API Tornado.** "
                    "Les métadonnées HTTP pilotent toute l'intelligence transversale du serveur sans polluer la charge utile métier : la **négociation de représentation** (`Content-Type: application/json` orientant vers `tornado.escape.json_decode(self.request.body)` par opposition à `application/x-www-form-urlencoded` destiné à `self.get_body_argument`), le **transport des preuves d'identité** (`Authorization: Bearer` ou `X-API-Key`), la **signalisation des quotas de débit** (`X-RateLimit-*` et `Retry-After`), la **corrélation distribuée** (`X-Request-ID` injecté dans `prepare()`), la **validation de cache** (`Cache-Control` et l'empreinte `Etag` calculée nativement par Tornado sur les réponses `GET`), ainsi que le **contrôle d'origine navigateur CORS** (`Access-Control-Allow-Origin` posé dans `set_default_headers()`)."
                )
            ],
            "code": _read("04_trame_http_et_headers.py"),
            "line_explanations": [
                {"lines": "10-24", "text": "Construction d'une trame brute HTTP/1.1 avec ligne de départ (`POST ... HTTP/1.1`), en-têtes (`Host`, `Content-Type`, `Content-Length`) et ligne vide obligatoire (`\\r\\n\\r\\n`)."},
                {"lines": "27-36", "text": "Trame 1 (API JSON) : `Content-Type: application/json; charset=utf-8` — décodée par `tornado.escape.json_decode(self.request.body)`."},
                {"lines": "38-46", "text": "Trame 2 (Formulaire HTML `<form method='POST'>`) : `Content-Type: application/x-www-form-urlencoded` — décodée par `self.get_body_argument(...)` dans Tornado."}
            ],
            "python_runner": {
                "prompt": "Générez et inspectez la trame HTTP/1.1 brute exacte envoyée vers un serveur Tornado :",
                "initial_code": _read("04_trame_http_et_headers.py")
            },
            "vscode_instructions": {
                "filename": "day_1/04_trame_http_et_headers.py",
                "steps": [
                    "Ouvrir `day_1/04_trame_http_et_headers.py` dans l'éditeur.",
                    "Exécuter `.venv/bin/python day_1/04_trame_http_et_headers.py` et observer la séparation entre la ligne de requête, les en-têtes et le corps."
                ]
            }
        },
        {
            "id": "d1-l4",
            "file": "day_1/02_serialisation_json.py",
            "title": "1.4 — Sémantique des Méthodes HTTP, Idempotence (`GET`, `PUT`, `PATCH`, `POST`, `DELETE`) & Ingénierie JSON",
            "duration": "60 min",
            "analogy": {
                "title": "Appuyer plusieurs fois sur le bouton d'appel d'un ascenseur (Idempotent) vs Payer deux fois par carte (Non-Idempotent)",
                "text": (
                    "Que vous pressiez une seule fois ou dix fois nerveusement le bouton d'appel d'un ascenseur au troisième étage, l'état final du système mécanique demeure rigoureusement identique : la cabine converge vers le troisième palier. "
                    "En informatique distribuée, cette invariance de l'état face à la répétition d'un même message porte le nom mathématique d'**idempotence**.\n\n"
                    "À l'inverse, valider deux fois un ordre de virement dépourvu d'identifiant de déduplication débite deux fois le compte client : sur des réseaux mobiles ou interbancaires sujets aux micro-coupures d'accusés de réception TCP, distinguer les méthodes intrinsèquement idempotentes des opérations non idempotentes conditionne toute la fiabilité d'une API."
                )
            },
            "explanation": [
                (
                    "**Invariants de sûreté (*Safety*) et d'idempotence (*Idempotency*) des méthodes `RequestHandler` (RFC 9110).** "
                    "Tornado associe chaque verbe HTTP à une méthode dédiée dont le contrat mathématique engage votre architecture : `def get(self)` est à la fois **sûre** (aucun effet de bord sur l'état persisté) et **idempotente**, tandis que `def put(self, id)` (remplacement intégral d'une ressource connue) et `def delete(self, id)` (retrait d'une ressource identifiée) modifient l'état serveur tout en demeurant **strictement idempotentes** en cas de rejeu réseau automatique. "
                    "À l'opposé, `def post(self)` n'est **ni sûre ni idempotente** par nature (chaque exécution crée une nouvelle entité ou déclenche une transaction supplémentaire, sauf implémentation explicite d'un en-tête `Idempotency-Key`), et `def patch(self, id)` applique une mutation partielle qui reste idempotente dès lors qu'elle exprime des affectations de valeurs absolues plutôt que des incréments relatifs."
                ),
                (
                    "**Pipeline de désérialisation et sérialisation JSON dans Tornado (`tornado.escape` et `self.write`).** "
                    "À la réception d'une requête entrante, l'utilitaire `tornado.escape.json_decode(self.request.body)` décode la séquence d'octets UTF-8 du tampon réseau et reconstruit l'arbre de dictionnaires et listes en mémoire Python. "
                    "Dans le sens retour, invoquer `self.write(enveloppe_dict)` sur un dictionnaire structurant `meta` (version, horodatage UTC ISO 8601) et `data` déclenche automatiquement l'encodage JSON UTF-8 dans le tampon d'écriture de la requête tout en positionnant l'en-tête normalisé `Content-Type: application/json; charset=UTF-8`."
                )
            ],
            "code": _read("02_serialisation_json.py"),
            "line_explanations": [
                {"lines": "10-25", "text": "Construction d'une enveloppe JSON professionnelle séparant `meta` (version, moteur Tornado, date UTC ISO 8601) et `data` (données métiers)."},
                {"lines": "28", "text": "`json.dumps(..., ensure_ascii=False)` formate l'enveloppe JSON avec indentation pour l'inspection."},
                {"lines": "33-37", "text": "`tornado.escape.json_decode(...)` reconstruit le dictionnaire Python exactement comme lors de la lecture de `self.request.body`."}
            ],
            "sandbox_preset": {
                "label": "Tester les codes HTTP (200, 201, 400, 401, 404, 429) : GET /api/sandbox/status-demo/429",
                "method": "GET",
                "url": "/api/sandbox/status-demo/429",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez day_1/02_serialisation_json.py pour manipuler une enveloppe JSON avec tornado.escape.json_decode :",
                "initial_code": _read("02_serialisation_json.py")
            },
            "vscode_instructions": {
                "filename": "day_1/02_serialisation_json.py",
                "steps": [
                    "Ouvrir `day_1/02_serialisation_json.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_1/02_serialisation_json.py`."
                ]
            }
        },
        {
            "id": "d1-l5",
            "file": "day_1/05_outils_curl_postman_httpie.py",
            "title": "1.5 — Tester & Diagnostiquer une API Tornado : Maîtriser `curl`, Postman, HTTPie et REST Client (`.http`)",
            "duration": "65 min",
            "analogy": {
                "title": "Pourquoi un navigateur Web classique (Chrome/Firefox) ne suffit plus pour tester une API ?",
                "text": (
                    "Saisir une adresse dans la barre d'URL d'un navigateur graphique grand public n'exécute qu'une fraction infime du protocole HTTP : le navigateur émet exclusivement une requête `GET`, dépourvue de corps JSON et incapable d'injecter à la demande vos en-têtes d'authentification `Authorization: Bearer` ou `X-API-Key`.\n\n"
                    "Pour éprouver les méthodes de mutation (`POST`, `PUT`, `PATCH`, `DELETE`), forger des charges utiles précises et inspecter au caractère près la signature `Server: TornadoServer` ainsi que les empreintes `Etag` calculées par Tornado, l'ingénieur backend s'équipe d'instruments d'inspection dédiés : **`curl`** et **`HTTPie`** au terminal système, complétés par **`Postman`**, **`Bruno`** ou les fichiers versionnés **`.http`** sur son poste de développement."
                )
            },
            "explanation": [
                (
                    "**Instrumentation en ligne de commande par `curl` face à un démon `TornadoServer`.** "
                    "Omniprésent sur chaque conteneur Docker et serveur Linux accessible en SSH, `curl` permet de façonner chirurgicalement la trame HTTP : `-i` inclut la ligne de statut et les en-têtes de réponse (`Server`, `Etag`, `Content-Type`), `-v` dévoile l'intégralité du dialogue TCP/TLS sortant (`>`) et entrant (`<`), `-s` supprime la jauge de progression parasite dans les tubes Unix, `-X` sélectionne le verbe routé vers la méthode correspondante du `RequestHandler`, `-H` injecte un en-tête lu par `self.request.headers`, `-d` fournit le corps brut reçu dans `self.request.body`, et `-w` mesure au millième de seconde la latence réseau complète."
                ),
                (
                    "**Industrialisation collaborative des campagnes de tests avec Postman, Bruno et Insomnia.** "
                    "Sur des APIs exposant plusieurs dizaines d'endpoints sécurisés, les clients graphiques structurent les scénarios de recette en **collections exportables** assorties de **variables d'environnement** dynamiques telles que `{{base_url}}` (`http://127.0.0.1:8888`) et `{{access_token}}`, permettant de basculer instantanément du serveur Tornado local à la pré-production tout en réinjectant automatiquement les jetons émis."
                ),
                (
                    "**Ergonomie JSON native (`HTTPie`) et tests versionnés au plus près du code (`.http`).** "
                    "Pour accélérer les essais interactifs en console, `HTTPie` offre une grammaire concise distinguant nativement les chaînes (`titre=\"Tornado\"`) des littéraux numériques JSON (`duree_jours:=5`) avec coloration syntaxique automatique, tandis que l'extension *REST Client* exécute directement des fichiers texte `.http` archivés dans le dépôt Git à côté des `RequestHandlers` Python."
                )
            ],
            "code": _read("05_outils_curl_postman_httpie.py"),
            "line_explanations": [
                {"lines": "19-61", "text": "Démarre automatiquement un serveur Tornado non-bloquant de démonstration si le port 8888 n'est pas déjà actif."},
                {"lines": "86-89", "text": "Test 1 : `curl -s -i` interroge la route paginée et affiche l'en-tête `Server: TornadoServer` ainsi que l'`Etag` calculé par Tornado."},
                {"lines": "92-95", "text": "Test 2 : L'option `-H 'X-API-Key: isgp-secret-2026'` injecte l'en-tête d'authentification lu par `self.request.headers.get('X-API-Key')`."},
                {"lines": "98-107", "text": "Test 3 : `-X POST -H 'Content-Type: application/json' -d '{...}'` envoie un corps JSON décodé par `tornado.escape.json_decode(self.request.body)`."},
                {"lines": "110-118", "text": "Test 4 : `-X POST -d 'titre=...&duree_jours=3'` envoie un formulaire HTML lu par `self.get_body_argument(...)`."}
            ],
            "sandbox_preset": {
                "label": "Tester dans le Client HTTP ou ouvrir l'onglet 'curl & Postman'",
                "method": "POST",
                "url": "/api/sandbox/auth/token",
                "body": '{\n  "identifiant": "stagiaire",\n  "mot_de_passe": "isgp2026"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez ces 4 vraies commandes `curl -i` contre le serveur Tornado et inspectez les en-têtes HTTP bruts retournés :",
                "initial_code": _read("05_outils_curl_postman_httpie.py")
            },
            "vscode_instructions": {
                "filename": "day_1/05_outils_curl_postman_httpie.py",
                "steps": [
                    "Ouvrir un terminal et tester directement : `curl -i http://127.0.0.1:8888/api/sandbox/formations`.",
                    "Rendez-vous également dans l'onglet dédié **curl & Postman** en haut de l'application pour exécuter des commandes `curl` interactives et télécharger la Collection Postman du bootcamp."
                ]
            }
        }
    ]
}
