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
    "goal": "Comprendre l'évolution historique des services Web (HTML, SOAP/XML, REST/JSON, GraphQL, gRPC), décoder la pile réseau (DNS, IP, Port TCP, TLS), inspecter une trame HTTP brute, maîtriser la propriété d'idempotence des verbes HTTP et structurer des enveloppes JSON professionnelles.",
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
                "**1. Qu'est-ce qu'un Service Web (Web Service) au sens strict ?** Un système logiciel conçu pour permettre l'interaction machine-à-machine (M2M) à travers un réseau IP en échangeant des messages structurés indépendants du langage de programmation (un client Java ou C# peut interroger un serveur Python).",
                "**2. Les 4 grandes architectures d'APIs et Services Web en entreprise** :\n  - **SOAP (Simple Object Access Protocol — années 2000)** : Protocole très strict basé exclusivement sur **XML** avec un contrat formel **WSDL**. Toujours présent dans les systèmes interbancaires, la monétique et les télécoms historiques, mais lourd en bande passante et complexe à analyser.\n  - **REST (Representational State Transfer — Roy Fielding, 2000)** : Style d'architecture qui exploite nativement le protocole **HTTP** (ses méthodes `GET`, `POST`, `PUT`, `DELETE`, ses codes d'état `200`, `404`, ses en-têtes) combiné au format léger **JSON**. Aujourd'hui, **plus de 85 % des APIs publiques et d'entreprise sont des APIs REST/JSON**.\n  - **GraphQL (Meta, 2015)** : Permet au client de demander exactement la liste des champs souhaités sur un point d'entrée unique (`POST /graphql`), utile pour des interfaces mobiles très complexes.\n  - **gRPC (Google, HTTP/2 + Protocol Buffers)** : Format binaire ultra-rapide utilisé pour la communication interne à très haute fréquence entre microservices.",
                "**3. Pourquoi le découplage API / Interface (Frontend) est devenu la norme** : En exposant votre cœur métier sous forme d'API REST Python, vous séparez la donnée de l'affichage. Votre API unique alimente simultanément le site Web, l'application mobile Android/iOS, les partenaires externes et les outils d'automatisation."
            ],
            "code": _read("01_html_vs_json.py"),
            "line_explanations": [
                {"lines": "6-14", "text": "Flux HTML : la donnée métier (`Alger`, `24`) est noyée dans des balises visuelles (`<div>`, `<h1>`)."},
                {"lines": "17-27", "text": "Enveloppe SOAP/XML : structure hiérarchique stricte (`<soap:Envelope>`, `<soap:Body>`) avec espaces de noms (`xmlns`), beaucoup plus volumineuse en octets."},
                {"lines": "30-35", "text": "Objet REST/JSON : concis, typé (chaînes, nombres entiers) et directement convertible en dictionnaire Python ou objet JavaScript."},
                {"lines": "37-40", "text": "Comparaison de l'empreinte réseau en octets des trois formats pour une même information."}
            ],
            "sandbox_preset": {
                "label": "Tester une réponse REST/JSON réelle : GET /api/sandbox/meteo?ville=Alger",
                "method": "GET",
                "url": "/api/sandbox/meteo?ville=Alger",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez day_1/01_html_vs_json.py pour comparer l'empreinte en octets de HTML, SOAP/XML et REST/JSON :",
                "initial_code": _read("01_html_vs_json.py")
            },
            "vscode_instructions": {
                "filename": "day_1/01_html_vs_json.py",
                "steps": [
                    "Ouvrir `day_1/01_html_vs_json.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `python day_1/01_html_vs_json.py`."
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
                "text": "Lorsqu'un client appelle `https://api.isgp.dz:8443/api/v1/formations?ville=Alger`, quatre opérations réseau invisibles se succèdent en quelques millisecondes avant même que votre code Python Flask ne soit touché."
            },
            "explanation": [
                "**1. Les 4 étapes réseau d'un appel d'API** :\n  1. **Résolution DNS (Domain Name System)** : Les routeurs réseau ne comprennent que les adresses IP numériques (ex. `192.168.0.101`). Le client interroge le serveur DNS pour traduire le nom de domaine `api.isgp.dz` en adresse IP. En local, `localhost` est immédiatement traduit en `127.0.0.1` (boucle locale / loopback).\n  2. **Connexion TCP sur le Port cible (`IP:Port`)** : Le client ouvre un canal fiable (Socket TCP) vers l'adresse IP et le **Port** (par défaut `80` pour HTTP, `443` pour HTTPS, `5000` pour Flask en développement).\n  3. **Poignée de main TLS (si `https://`)** : Le client et le serveur négocient une clé de chiffrement symétrique pour que personne sur le Wi-Fi ou les routeurs intermédiaires ne puisse lire vos tokens ou vos données JSON.\n  4. **Transmission de la requête HTTP** : Une fois le tunnel ouvert, le client envoie la requête HTTP.",
                "**2. Découpage normalisé d'une URI selon le standard RFC 3986** :\n  - **`scheme` (Protocole)** : `http` (en clair, réservé au développement local) ou `https` (chiffré TLS, obligatoire en production).\n  - **`hostname` + `port` (Autorité)** : `api.isgp.dz:8443` ou `127.0.0.1:5000`.\n  - **`path` (Chemin hiérarchique de la ressource)** : `/api/v1/formations` (identifie la collection ciblée et la version `v1`).\n  - **`query` (Chaîne de requête après `?`)** : `ville=Alger&domaine=securite&page=2` (paires `clé=valeur` séparées par `&`, servant au filtrage et à la pagination).\n  - **`fragment` (après `#`)** : Non envoyé au serveur HTTP (utilisé uniquement côté navigateur)."
            ],
            "code": _read("03_analyseur_uri_et_reseau.py"),
            "line_explanations": [
                {"lines": "5", "text": "`urlparse` et `parse_qs` sont les outils standards de Python (`urllib.parse`) pour analyser rigoureusement n'importe quelle URL."},
                {"lines": "9-10", "text": "`urlparse` découpe l'URI en 6 composants normalisés ; `parse_qs` convertit la chaîne après `?` en dictionnaire Python."},
                {"lines": "13-18", "text": "Inspection individuelle du schéma (`https`), de l'hôte, du port TCP (`8443`), du chemin (`/api/v1/formations`) et de la query string."},
                {"lines": "20-22", "text": "Parcours des paramètres de filtrage extraits."}
            ],
            "python_runner": {
                "prompt": "Exécutez l'analyseur d'URI RFC 3986 et testez avec vos propres URLs et paramètres :",
                "initial_code": _read("03_analyseur_uri_et_reseau.py")
            },
            "vscode_instructions": {
                "filename": "day_1/03_analyseur_uri_et_reseau.py",
                "steps": [
                    "Ouvrir `day_1/03_analyseur_uri_et_reseau.py` dans l'éditeur.",
                    "Exécuter `python day_1/03_analyseur_uri_et_reseau.py`."
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
                "**1. Les 3 étages d'un message HTTP brut** :\n  - **Étage 1 — La Ligne de Départ (Start Line)** :\n    - Dans une Requête : `POST /api/v1/formations HTTP/1.1` (Méthode + Chemin + Version).\n    - Dans une Réponse : `HTTP/1.1 201 Created` (Version + Code à 3 chiffres + Raison).\n  - **Étage 2 — Les En-têtes HTTP (`Headers`)** : Une série de lignes `Nom-En-Tete: Valeur` contenant toutes les métadonnées de contrôle (sécurité, format, taille, cache, quotas).\n  - **La Ligne Vide Obligatoire (`\\r\\n\\r\\n`)** : Sépare strictement les en-têtes du corps du message.\n  - **Étage 3 — Le Corps (`Body / Payload`)** : Optionnel (présent sur `POST`, `PUT`, `PATCH` et dans les réponses), contient la chaîne JSON.",
                "**2. Les 6 familles d'En-têtes HTTP qu'un concepteur d'API doit maîtriser** :\n  - **Négociation de contenu (`Content Negotiation`)** :\n    - `Content-Type: application/json` : Indique au destinataire comment décoder le Body actuel.\n    - `Accept: application/json` : Le client indique au serveur sous quel format il souhaite recevoir la réponse.\n  - **Authentification & Autorisation** :\n    - `Authorization: Bearer <token>` ou `X-API-Key: <secret>`.\n    - `WWW-Authenticate: Bearer` : Renvoyé par le serveur avec un code `401` pour indiquer comment s'authentifier.\n  - **Contrôle de Débit (Rate Limiting)** :\n    - `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`.\n  - **Traçabilité & Corrélation** :\n    - `X-Request-ID: req-98412` : Identifiant unique de la requête permettant de retrouver instantanément la trace d'un appel dans les logs du serveur.\n  - **Cache & Performance** :\n    - `Cache-Control: no-store` (données sensibles) ou `max-age=3600` (catalogue statique), `ETag`.\n  - **Sécurité Navigateur (CORS)** :\n    - `Access-Control-Allow-Origin: *` : Autorise une application Web hébergée sur un autre domaine à lire la réponse de l'API."
            ],
            "code": _read("04_trame_http_et_headers.py"),
            "line_explanations": [
                {"lines": "7-14", "text": "Construction de la Request Line (`POST /api/v1/formations HTTP/1.1`) et des en-têtes standards (`Host`, `User-Agent`, `Accept`)."},
                {"lines": "17-19", "text": "Calcul exact de `Content-Length` en octets UTF-8 (et non en nombre de caractères, car un caractère accentué comme `'é'` occupe 2 octets en UTF-8 !)."},
                {"lines": "21", "text": "`\\r\\n\\r\\n` matérialise la ligne vide normalisée qui sépare l'enveloppe (Headers) de la charge utile (Body JSON)."}
            ],
            "python_runner": {
                "prompt": "Générez et inspectez la trame HTTP/1.1 brute exacte envoyée sur un socket réseau :",
                "initial_code": _read("04_trame_http_et_headers.py")
            },
            "vscode_instructions": {
                "filename": "day_1/04_trame_http_et_headers.py",
                "steps": [
                    "Ouvrir `day_1/04_trame_http_et_headers.py` dans l'éditeur.",
                    "Exécuter `python day_1/04_trame_http_et_headers.py` et observer la séparation entre la ligne de requête, les en-têtes et le corps JSON."
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
                "**1. Méthodes Sûres (`Safe`) vs Méthodes Idempotentes (`Idempotent`) — Le cœur du standard HTTP (RFC 9110)** :\n  - **`GET` (Lire)** : **Sûre** (ne modifie aucun état sur le serveur) ET **Idempotente** (l'appeler 10 fois renvoie la même ressource sans effet secondaire).\n  - **`PUT` (Remplacer intégralement une ressource connue, ex. `PUT /formations/1`)** : Non sûre (elle modifie la base), mais **Idempotente** : envoyer 1 fois ou 5 fois `{ \"titre\": \"Nouveau\", \"salle\": \"B\" }` sur `/formations/1` aboutit exactement au même état final.\n  - **`DELETE` (Supprimer une ressource connue, ex. `DELETE /formations/1`)** : **Idempotente** : après 1 appel ou 5 appels, la ressource n°1 n'existe plus dans la base.\n  - **`POST` (Créer une ressource ou déclencher un traitement)** : **NI sûre, NI idempotente** ! Envoyer 3 fois `POST /formations` crée **3 formations en doublon** avec 3 IDs différents (`#1`, `#2`, `#3`). C'est pourquoi, si la connexion réseau coupe pendant un `POST`, un client peut rejouer la requête en toute sécurité uniquement si l'API gère un en-tête `Idempotency-Key` (que nous coderons au Jour 3) !\n  - **`PATCH` (Modification partielle)** : Modifie uniquement un sous-ensemble de champs (ex. changer uniquement la salle sans toucher aux autres colonnes).",
                "**2. Bonnes pratiques d'ingénierie JSON en entreprise** :\n  - **Enveloppe structurée (`meta` + `data`)** : Séparer la donnée métier (`data`) des métadonnées techniques (`meta` : version d'API, pagination, horodatage).\n  - **Dates au format international ISO 8601 (`YYYY-MM-DDTHH:MM:SSZ`)** : Ne jamais envoyer `\"07/11/2026\"` (ambigu entre le 7 novembre en Algérie/Europe et le 11 juillet aux USA). Toujours utiliser `\"2026-11-07T16:30:00Z\"`."
            ],
            "code": _read("02_serialisation_json.py"),
            "line_explanations": [
                {"lines": "8-22", "text": "Construction d'une enveloppe JSON professionnelle séparant `meta` (version, date UTC ISO 8601) et `data` (données métiers)."},
                {"lines": "25", "text": "`json.dumps(..., ensure_ascii=False)` garantit que les caractères accentués français/arabes restent lisibles en UTF-8."},
                {"lines": "30-32", "text": "`json.loads(...)` reconstruit le dictionnaire imbriqué côté récepteur."}
            ],
            "sandbox_preset": {
                "label": "Tester les codes HTTP (200, 201, 400, 401, 404, 429) : GET /api/sandbox/status-demo/429",
                "method": "GET",
                "url": "/api/sandbox/status-demo/429",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez day_1/02_serialisation_json.py pour générer une enveloppe JSON avec horodatage ISO 8601 :",
                "initial_code": _read("02_serialisation_json.py")
            },
            "vscode_instructions": {
                "filename": "day_1/02_serialisation_json.py",
                "steps": [
                    "Ouvrir `day_1/02_serialisation_json.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `python day_1/02_serialisation_json.py`."
                ]
            }
        },
        {
            "id": "d1-l5",
            "file": "day_1/05_outils_curl_postman_httpie.py",
            "title": "1.5 — Tester & Diagnostiquer une API : Maîtriser `curl`, Postman, HTTPie et REST Client (`.http`)",
            "duration": "65 min",
            "analogy": {
                "title": "Pourquoi un navigateur Web classique (Chrome/Firefox) ne suffit plus pour tester une API ?",
                "text": "Lorsque vous tapez une URL dans la barre d'adresse d'un navigateur, celui-ci ne sait faire qu'une seule chose : envoyer une requête **`GET`**, sans corps JSON et sans en-tête d'authentification `Authorization: Bearer` ou `X-API-Key`.\nPour tester les méthodes **`POST`**, **`PUT`**, **`PATCH`**, **`DELETE`**, injecter des en-têtes de sécurité et inspecter les codes de statut exacts (`201`, `401`, `422`, `429`), tout ingénieur API utilise quotidiennement deux grandes familles d'outils : **la ligne de commande universelle (`curl` / `HTTPie`)** et **les clients graphiques (`Postman` / `Bruno` / `Insomnia` / `VS Code REST Client`)**."
            },
            "explanation": [
                "**1. `curl` (*Client for URL*) — L'outil universel installé sur tous les serveurs Linux, macOS et Windows** :\n  Pourquoi `curl` est-il l'outil numéro 1 en ingénierie d'API ? Parce qu'en production, sur un serveur distant connecté en SSH ou dans un conteneur Docker, vous n'avez ni écran graphique ni Postman ! Savoir forger une requête `curl` en 10 secondes est une compétence fondamentale.\n  **Les 7 options (`flags`) essentielles de `curl` à connaître par cœur** :\n  - **`-i` (`--include`)** : Affiche la ligne de statut (`HTTP/1.1 200 OK`) ET les **en-têtes HTTP de la réponse** au-dessus du corps JSON. Indispensable pour voir `X-RateLimit-Remaining` ou `Content-Type`.\n  - **`-v` (`--verbose`)** : Mode diagnostic complet : affiche les lignes envoyées par le client (préfixées par `>`) et les lignes reçues du serveur (préfixées par `<`).\n  - **`-s` (`--silent`)** : Masque la barre de progression pour pouvoir chaîner la sortie vers un formateur JSON (`curl -s http://... | python3 -m json.tool` ou `| jq`).\n  - **`-X <METHODE>` (`--request`)** : Définit le verbe HTTP : `-X GET`, `-X POST`, `-X PUT`, `-X PATCH`, `-X DELETE`.\n  - **`-H \"Nom: Valeur\"` (`--header`)** : Ajoute un en-tête HTTP (répétable plusieurs fois : `-H \"Content-Type: application/json\" -H \"Authorization: Bearer <token>\"`).\n  - **`-d '<json>'` (`--data`)** : Définit le corps (`Body / Payload`) de la requête.\n  - **`-w \"\\nHTTP: %{http_code} | Temps: %{time_total}s\\n\"`** : Affiche le code de statut exact et la latence réseau en fin d'exécution.",
                "**2. `Postman` (ainsi que `Bruno` et `Insomnia`) — L'atelier graphique d'équipe** :\n  - Permet d'organiser toutes les requêtes d'un projet dans une **Collection** partageable (fichier `.json`).\n  - Gère des **Variables d'Environnement** (`{{base_url}}`, `{{access_token}}`) pour basculer en un clic de `http://127.0.0.1:5000` (Développement) vers `https://api.isgp.dz` (Production).\n  - Dans Postman, pour envoyer un JSON sur un `POST` ou `PUT` : sélectionnez l'onglet **Body** → cochez **raw** → choisissez **JSON** dans la liste déroulante (ce qui ajoute automatiquement l'en-tête `Content-Type: application/json`).",
                "**3. `HTTPie` (`http`) & `VS Code REST Client` (`.http`) — Les alternatives modernes** :\n  - **`HTTPie`** simplifie la syntaxe JSON en terminal : `http POST :5000/api/formations titre=\"Flask\" duree_jours:=5`.\n  - **Fichiers `.http` (extension REST Client dans VS Code / Antigravity)** : Permet d'écrire ses requêtes HTTP dans un simple fichier texte versionné dans Git avec le code source Python !"
            ],
            "code": _read("05_outils_curl_postman_httpie.py"),
            "line_explanations": [
                {"lines": "20-23", "text": "`curl -s -i` interroge la route paginée en affichant les en-têtes HTTP de réponse (`HTTP/1.1 200 OK`, `Content-Type`, etc.)."},
                {"lines": "26-29", "text": "L'option `-H 'X-API-Key: isgp-secret-2026'` injecte l'en-tête d'authentification requis par le serveur."},
                {"lines": "32-41", "text": "Combinaison standard `-X POST -H 'Content-Type: application/json' -d '{...}'` pour envoyer un corps JSON et obtenir un Bearer Token."}
            ],
            "sandbox_preset": {
                "label": "Tester dans le Client HTTP ou ouvrir l'onglet 'curl & Postman'",
                "method": "POST",
                "url": "/api/sandbox/auth/token",
                "body": '{\n  "identifiant": "stagiaire",\n  "mot_de_passe": "isgp2026"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez ces 3 vraies commandes `curl -i` contre le serveur Flask et inspectez les en-têtes HTTP bruts retournés :",
                "initial_code": _read("05_outils_curl_postman_httpie.py")
            },
            "vscode_instructions": {
                "filename": "day_1/05_outils_curl_postman_httpie.py",
                "steps": [
                    "Ouvrir un terminal et tester directement : `curl -i http://127.0.0.1:5000/api/sandbox/formations`.",
                    "Rendez-vous également dans l'onglet dédié **curl & Postman** en haut de l'application pour exécuter des commandes `curl` interactives et télécharger la Collection Postman du bootcamp."
                ]
            }
        }
    ]
}
