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
                "text": "Au début du Web, les serveurs renvoyaient uniquement des pages **HTML** destinées aux yeux d'un humain. Mais dès qu'une banque, un opérateur télécom ou une application mobile a eu besoin d'interroger le serveur par programme, lire du HTML était inutilisable (si le graphiste changeait une couleur ou une balise `<div>`, le programme client plantait). C'est ainsi que sont nés les **Services Web**."
            },
            "explanation": [
                "**1. Qu'est-ce qu'un Service Web (Web Service) au sens strict ?** Un système logiciel conçu pour permettre l'interaction machine-à-machine (M2M) à travers un réseau IP en échangeant des messages structurés indépendants du langage de programmation (un client Java ou C# peut interroger un serveur Python Tornado).",
                "**2. Les 4 grandes architectures d'APIs et Services Web en entreprise** :\n  - **SOAP (Simple Object Access Protocol — années 2000)** : Protocole très strict basé exclusivement sur **XML** avec un contrat formel **WSDL**. Toujours présent dans les systèmes interbancaires, la monétique et les télécoms historiques, mais lourd en bande passante et complexe à analyser.\n  - **REST (Representational State Transfer — Roy Fielding, 2000)** : Style d'architecture qui exploite nativement le protocole **HTTP** (ses méthodes `GET`, `POST`, `PUT`, `DELETE`, ses codes d'état `200`, `404`, ses en-têtes) combiné au format léger **JSON**. Aujourd'hui, **plus de 85 % des APIs publiques et d'entreprise sont des APIs REST/JSON**.\n  - **GraphQL (Meta, 2015)** : Permet au client de demander exactement la liste des champs souhaités sur un point d'entrée unique (`POST /graphql`), utile pour des interfaces mobiles très complexes.\n  - **gRPC (Google, HTTP/2 + Protocol Buffers)** : Format binaire ultra-rapide utilisé pour la communication interne à très haute fréquence entre microservices.",
                "**3. Comment Tornado gère ces 3 formats dans des classes `RequestHandler`** :\n  - `self.render('meteo.html', meteo=...)` : Compile et sert le gabarit HTML via `tornado.template`.\n  - `self.set_header('Content-Type', 'application/xml')` + `self.write(flux_xml)` : Envoie une enveloppe SOAP/XML.\n  - `self.write(DONNEES_METEO)` : Lorsqu'on passe un `dict` Python à `self.write()`, Tornado le sérialise automatiquement en JSON et injecte `Content-Type: application/json; charset=UTF-8` !"
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
                "text": "Lorsqu'un client appelle `https://api.isgp.dz:8443/api/v1/formations?ville=Alger`, quatre opérations réseau invisibles se succèdent en quelques millisecondes avant même que votre Event-Loop Tornado (`IOLoop`) ne reçoive l'événement socket."
            },
            "explanation": [
                "**1. Les 4 étapes réseau d'un appel d'API** :\n  1. **Résolution DNS (Domain Name System)** : Les routeurs réseau ne comprennent que les adresses IP numériques (ex. `192.168.0.101`). Le client interroge le serveur DNS pour traduire le nom de domaine `api.isgp.dz` en adresse IP. En local, `localhost` est immédiatement traduit en `127.0.0.1` (boucle locale / loopback).\n  2. **Connexion TCP sur le Port cible (`IP:Port`)** : Le client ouvre un canal fiable (Socket TCP) vers l'adresse IP et le **Port** (par défaut `80` pour HTTP, `443` pour HTTPS, `8888` pour Tornado en développement).\n  3. **Poignée de main TLS (si `https://`)** : Le client et le serveur négocient une clé de chiffrement symétrique pour que personne sur le Wi-Fi ou les routeurs intermédiaires ne puisse lire vos tokens ou vos données JSON.\n  4. **Transmission de la requête HTTP** : Une fois le tunnel ouvert, le client envoie la requête HTTP au serveur non-bloquant `tornado.httpserver.HTTPServer`.",
                "**2. Découpage normalisé d'une URI selon le standard RFC 3986** :\n  - **`scheme` (Protocole)** : `http` (en clair, réservé au développement local) ou `https` (chiffré TLS, obligatoire en production).\n  - **`hostname` + `port` (Autorité)** : `api.isgp.dz:8443` ou `127.0.0.1:8888`.\n  - **`path` (Chemin hiérarchique de la ressource)** : `/api/v1/formations` (identifie la collection ciblée et la version `v1`).\n  - **`query` (Chaîne de requête après `?`)** : `ville=Alger&domaine=securite&page=2` (construite côté client avec `tornado.httputil.url_concat` et lue côté serveur avec `self.get_query_argument`).\n  - **`fragment` (après `#`)** : Non envoyé au serveur HTTP (utilisé uniquement côté navigateur)."
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
                "text": "Beaucoup de développeurs utilisent des bibliothèques sans jamais savoir à quoi ressemble véritablement une requête HTTP sur le câble réseau. Or, le protocole HTTP/1.1 est un **protocole purement textuel** : chaque requête et chaque réponse possède exactement la même structure en 3 étages."
            },
            "explanation": [
                "**1. Les 3 étages d'un message HTTP brut décodé par `tornado.httpserver.HTTPServer`** :\n  - **Étage 1 — La Ligne de Départ (Start Line)** :\n    - Dans une Requête : `POST /api/v1/formations HTTP/1.1` (Méthode `self.request.method` + Chemin `self.request.path` + Version `self.request.version`).\n    - Dans une Réponse : `HTTP/1.1 201 Created` (fixé via `self.set_status(201)`).\n  - **Étage 2 — Les En-têtes HTTP (`Headers`)** : Lus via `self.request.headers.get('Nom')` et écrits via `self.set_header('Nom', 'Valeur')`.\n  - **La Ligne Vide Obligatoire (`\\r\\n\\r\\n`)** : Sépare strictement les en-têtes du corps du message.\n  - **Étage 3 — Le Corps (`Body / Payload`)** : Accessible en octets bruts dans `self.request.body`.",
                "**2. Les 6 familles d'En-têtes HTTP qu'un concepteur d'API Tornado doit maîtriser** :\n  - **Négociation de contenu (`Content Negotiation`)** :\n    - `Content-Type: application/json` : Indique que `self.request.body` contient du JSON à décoder via `tornado.escape.json_decode(self.request.body)`.\n    - `Content-Type: application/x-www-form-urlencoded` : Indique un formulaire HTML dont les champs sont lus via `self.get_body_argument('titre')`.\n  - **Authentification & Autorisation** :\n    - `Authorization: Bearer <token>` ou `X-API-Key: <secret>`.\n  - **Contrôle de Débit (Rate Limiting)** :\n    - `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`.\n  - **Traçabilité & Corrélation** :\n    - `X-Request-ID: req-98412` : Injecté dans le hook `prepare(self)` de Tornado.\n  - **Cache & Performance** :\n    - `Cache-Control: no-store` ou `Etag` (calculé automatiquement par Tornado sur les réponses GET !).\n  - **Sécurité Navigateur (CORS)** :\n    - `Access-Control-Allow-Origin` : Configuré dans `set_default_headers(self)` du `RequestHandler`."
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
                "text": "Si vous appuyez 1 fois ou 10 fois sur le bouton pour appeler l'ascenseur au 3e étage, le résultat final est exactement le même : l'ascenseur vient au 3e étage. En mathématiques et en informatique, cette propriété s'appelle **l'Idempotence**. À l'inverse, si vous validez 2 fois un virement bancaire sans précaution, votre compte est débité 2 fois !"
            },
            "explanation": [
                "**1. Méthodes Sûres (`Safe`) vs Méthodes Idempotentes (`Idempotent`) — Implémentées par méthode dans `RequestHandler`** :\n  - **`def get(self):` (Lire)** : **Sûre** (ne modifie aucun état sur le serveur) ET **Idempotente**.\n  - **`def put(self, id):` (Remplacer intégralement une ressource connue)** : Non sûre, mais **Idempotente**.\n  - **`def delete(self, id):` (Supprimer une ressource connue)** : **Idempotente**.\n  - **`def post(self):` (Créer une ressource ou déclencher un traitement)** : **NI sûre, NI idempotente** ! C'est pourquoi, si la connexion réseau coupe pendant un `POST`, un client peut rejouer la requête en toute sécurité uniquement si l'API gère un en-tête `Idempotency-Key` (que nous coderons au Jour 3) !\n  - **`def patch(self, id):` (Modification partielle)** : Modifie uniquement un sous-ensemble de champs.",
                "**2. Sérialisation JSON dans Tornado (`tornado.escape` et `self.write`)** :\n  - **`tornado.escape.json_decode(self.request.body)`** : Désérialise les octets UTF-8 reçus dans la requête en dictionnaire Python.\n  - **`self.write(dictionnaire)`** : Sérialise automatiquement le dictionnaire et positionne `Content-Type: application/json; charset=UTF-8`."
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
                "text": "Lorsque vous tapez une URL dans la barre d'adresse d'un navigateur, celui-ci ne sait faire qu'une seule chose : envoyer une requête **`GET`**, sans corps JSON et sans en-tête d'authentification `Authorization: Bearer` ou `X-API-Key`.\nPour tester les méthodes **`POST`**, **`PUT`**, **`PATCH`**, **`DELETE`**, injecter des en-têtes de sécurité et inspecter l'en-tête `Server: TornadoServer/6.6.1`, tout ingénieur API utilise quotidiennement **la ligne de commande (`curl` / `HTTPie`)** et **les clients graphiques (`Postman` / `Bruno` / `VS Code REST Client`)**."
            },
            "explanation": [
                "**1. `curl` (*Client for URL*) — L'outil universel pour inspecter `TornadoServer`** :\n  **Les 7 options (`flags`) essentielles de `curl` à connaître par cœur** :\n  - **`-i` (`--include`)** : Affiche la ligne de statut (`HTTP/1.1 200 OK`) ET les **en-têtes HTTP de la réponse** (`Server: TornadoServer/6.6.1`, `Etag`, `Content-Type`).\n  - **`-v` (`--verbose`)** : Mode diagnostic complet (`>` requête envoyée, `<` réponse reçue).\n  - **`-s` (`--silent`)** : Masque la barre de progression.\n  - **`-X <METHODE>` (`--request`)** : Définit le verbe HTTP qui déclenchera `def get(self):`, `def post(self):`, `def put(self):` ou `def delete(self):` dans votre `RequestHandler` Tornado.\n  - **`-H \"Nom: Valeur\"` (`--header`)** : Ajoute un en-tête HTTP lu par `self.request.headers.get(...)`.\n  - **`-d '<json>'` (`--data`)** : Définit le corps (`Body / Payload`) de la requête.\n  - **`-w \"\\nHTTP: %{http_code} | Temps: %{time_total}s\\n\"`** : Affiche le code de statut exact et la latence.",
                "**2. `Postman` (ainsi que `Bruno` et `Insomnia`) — L'atelier graphique d'équipe** :\n  - Permet d'organiser toutes les requêtes d'un projet dans une **Collection** partageable (`.json`).\n  - Gère des **Variables d'Environnement** (`{{base_url}} = http://127.0.0.1:8888`, `{{access_token}}`).",
                "**3. `HTTPie` (`http`) & `VS Code REST Client` (`.http`)** :\n  - **`HTTPie`** : `http POST :8888/api/formations titre=\"Tornado\" duree_jours:=5`.\n  - **Fichiers `.http`** : Permettent de versionner les requêtes de test dans Git avec le code source Python."
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
