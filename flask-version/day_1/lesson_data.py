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
                "text": "Aux origines du Web, les serveurs HTTP restituaient exclusivement des documents **HTML** mis en forme pour la lecture humaine dans un navigateur. Dès que des systèmes bancaires, des opérateurs télécoms ou des applications mobiles ont dû interroger ces serveurs par programme, extraire des données au milieu de balises `<div>` s'est révélé fragile : la moindre refonte graphique brisait l'analyseur syntaxique du client.\n\nLes **Services Web** ont résolu ce couplage en séparant radicalement la représentation visuelle de la donnée brute : là où une route Web classique invoque `render_template()` pour produire une page HTML, une route d'API Flask sérialise directement un dictionnaire métier via `jsonify()` afin d'échanger un contrat stable d'une machine à une autre."
            },
            "explanation": [
                "**Interopérabilité machine-à-machine indépendante du langage.** Au sens strict de l'ingénierie logicielle, un Service Web désigne un composant applicatif exposé sur un réseau TCP/IP qui échange des messages structurés selon des standards ouverts. Grâce à cette neutralité protocolaire, un client mobile écrit en Kotlin ou Swift, un progiciel Java ou un script C# dialogue sans friction avec un backend Python exécuté par Flask et Gunicorn.",
                "**Panorama architectural : de SOAP/XML à REST/JSON, GraphQL et gRPC.** Le protocole historique **SOAP** impose une enveloppe **XML** verbeuse régie par un contrat **WSDL** strict, toujours actif en monétique et télécoms mais coûteux en bande passante. Le style architectural **REST** formalisé par Roy Fielding domine aujourd'hui plus de 85 % des APIs en exploitant nativement la sémantique **HTTP** (`GET`, `POST`, `PUT`, `DELETE`, statuts `200`, `404`) couplée à la légèreté de **JSON**, tandis que **GraphQL** répond aux besoins de requêtage granulaire sur point d'entrée unique et que **gRPC** optimise les flux binaires internes sous HTTP/2 et Protocol Buffers.",
                "**Découplage industriel entre noyau métier et interfaces clientes.** En exposant la logique métier derrière une API REST Flask servie en WSGI, l'organisation mutualise ses règles de gestion, sa sécurité et ses accès aux données au sein d'un socle unique. Ce même serveur alimente simultanément un portail Web React ou Jinja2, des applications mobiles natives Android et iOS, ainsi que les systèmes partenaires B2B sans jamais dupliquer le code serveur."
            ],
            "code": _read("01_html_vs_json.py"),
            "line_explanations": [
                {"lines": "11-12", "text": "Configuration du dossier `day_1/templates/` contenant le fichier HTML Jinja2 `meteo.html` (zéro HTML codé en dur dans Python)."},
                {"lines": "23-26", "text": "Approche Web classique : `render_template('meteo.html', meteo=DONNEES_METEO)` injecte les données dans le gabarit HTML Jinja2."},
                {"lines": "30-43", "text": "Enveloppe SOAP/XML historique : structure hiérarchique verbeuse (`<soap:Envelope>`, `<soap:Body>`) avec espaces de noms (`xmlns`)."},
                {"lines": "47-49", "text": "Approche API REST moderne : `jsonify(DONNEES_METEO)` sérialise directement le dictionnaire en JSON léger (`application/json`)."},
                {"lines": "52-63", "text": "Exécution comparative automatique mesurant la taille exacte en octets et le `Content-Type` des trois formats."}
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
                "text": "Lorsqu'une application cliente invoque `https://api.isgp.dz:8443/api/v1/formations?ville=Alger`, quatre couches protocolaires négocient l'acheminement en quelques millisecondes avant même que le serveur WSGI Gunicorn ne transmette le dictionnaire `environ` à Flask. L'annuaire **DNS** localise l'adresse IP de la machine cible, le protocole **TCP** ouvre un canal numéroté vers le bon processus, la couche **TLS** scelle un tunnel chiffré de bout en bout, et la trame **HTTP** achemine enfin la requête jusqu'au routeur Werkzeug."
            },
            "explanation": [
                "**Séquence d'établissement d'une connexion réseau jusqu'au worker WSGI.** Le client résout d'abord le nom de domaine `api.isgp.dz` en adresse IP numérique via le **DNS** (ou traduit immédiatement `localhost` vers la boucle locale `127.0.0.1`), puis effectue une poignée de main **TCP** en trois temps vers le port d'écoute cible (`80` pour HTTP, `443` pour HTTPS, `5000` pour le serveur de développement Werkzeug ou `8000` pour Gunicorn). Lorsque le schéma est `https://`, une négociation cryptographique **TLS** authentifie le certificat du serveur et établit des clés symétriques éphémères protégeant les en-têtes et le corps JSON contre toute écoute sur le réseau.",
                "**Anatomie normalisée d'une URI selon le standard RFC 3986.** Une *Uniform Resource Identifier* se décompose en segments syntaxiques rigoureux : le `scheme` (`http` ou `https`) fixe le protocole de transport, l'autorité regroupe l'hôte et le `port` (`api.isgp.dz:8443`), et le `path` hiérarchique (`/api/v1/formations`) désigne la collection métier ciblée par la table de routage Flask. À la suite du point d'interrogation `?`, la `query string` (`ville=Alger&domaine=securite&page=2`) véhicule les critères de filtrage et de pagination décodés dans `request.args`, tandis qu'un éventuel `fragment` après `#` demeure strictement confiné au navigateur client sans jamais franchir le réseau.",
                "**Traduction de l'URI dans le dictionnaire d'environnement WSGI (`PEP 3333`).** À la réception des octets HTTP, Gunicorn ou Werkzeug découpe la ligne de requête et peuple les clés normalisées `REQUEST_METHOD`, `PATH_INFO`, `QUERY_STRING` et `SERVER_PORT` du dictionnaire `environ`. Flask enveloppe ensuite cet environnement brut dans son objet `Request` afin d'offrir au développeur un accès typé et sécurisé à chaque composant de l'URI."
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
                "text": "De nombreux développeurs manipulent des frameworks Web sans jamais inspecter les octets réellement transmis sur le socket TCP. Or, HTTP/1.1 demeure un **protocole textuel d'une grande limpidité** dont chaque requête et chaque réponse obéissent invariablement à une architecture en trois étages séparés par une séquence `CRLF` (`\\r\\n`) normalisée."
            },
            "explanation": [
                "**Architecture en trois étages d'un message HTTP/1.1 brut.** Tout message HTTP débute par une *Start Line* (`POST /api/v1/formations HTTP/1.1` à l'aller, `HTTP/1.1 201 Created` au retour), immédiatement suivie d'un bloc d'en-têtes `Nom: Valeur` transportant les métadonnées de contrôle. Une ligne vide obligatoire composée de quatre octets `\\r\\n\\r\\n` matérialise la frontière stricte entre ces en-têtes et le flux d'octets du corps (`wsgi.input` côté Werkzeug), qui véhicule la charge utile JSON ou les champs de formulaire.",
                "**En-têtes de négociation de contenu et d'authentification.** Le couple `Content-Type: application/json` et `Accept: application/json` gouverne la *Content Negotiation* : le premier dicte à `request.get_json()` comment désérialiser le corps entrant, tandis que le second exprime le format attendu en retour. Sur le plan sécuritaire, le client transmet ses preuves d'identité dans `Authorization: Bearer <token>` ou `X-API-Key`, et le serveur accompagne toute réponse `401 Unauthorized` d'un en-tête `WWW-Authenticate` précisant le schéma exigé.",
                "**En-têtes d'exploitation industrielle : quotas, corrélation, cache et CORS.** En production sous Gunicorn et Nginx, les en-têtes pilotent toute la gouvernance opérationnelle sans polluer le schéma JSON métier : `X-RateLimit-Remaining` et `Retry-After` régulent le débit client, `X-Request-ID` assure la corrélation des journaux distribués, `Cache-Control` (`no-store` ou `max-age`) et `ETag` encadrent la mise en cache intermédiaire, tandis que `Access-Control-Allow-Origin` contrôle l'isolation inter-origines des navigateurs."
            ],
            "code": _read("04_trame_http_et_headers.py"),
            "line_explanations": [
                {"lines": "10-23", "text": "Construction d'une trame brute HTTP/1.1 avec ligne de départ (`POST ... HTTP/1.1`), en-têtes (`Host`, `Content-Type`, `Content-Length`) et ligne vide obligatoire (`\\r\\n\\r\\n`)."},
                {"lines": "26-35", "text": "Trame 1 (API JSON) : `Content-Type: application/json; charset=utf-8` — décodée par `request.get_json()` dans Flask."},
                {"lines": "38-45", "text": "Trame 2 (Formulaire HTML `<form method='POST'>`) : `Content-Type: application/x-www-form-urlencoded` — décodée par `request.form` dans Flask."}
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
                "text": "Presser une seule fois ou dix fois le bouton d'appel d'un ascenseur au troisième étage produit rigoureusement le même état final : la cabine rejoint le troisième étage. En mathématiques comme dans la norme HTTP (RFC 9110), cette invariance face à la répétition s'appelle **l'idempotence** ; à l'inverse, rejouer sans précaution un ordre de virement bancaire débite le compte une seconde fois."
            },
            "explanation": [
                "**Méthodes sûres (`Safe`) et méthodes idempotentes au sens de la RFC 9110.** Une méthode `GET` ou `HEAD` est dite à la fois **sûre** (aucune mutation d'état sur le serveur) et **idempotente**. Les méthodes `PUT` (remplacement intégral d'une ressource identifiée telle que `/formations/1`) et `DELETE` (suppression d'une cible connue) modifient bien la base de données, mais demeurent **idempotentes** car l'exécution répétée de la même requête converge toujours vers le même état serveur.",
                "**Non-idempotence native de `POST` et mise à jour partielle `PATCH`.** Contrairement à `PUT`, la méthode `POST` n'est ni sûre ni idempotente : soumettre trois fois `POST /formations` insère trois entités distinctes affectées de clés primaires différentes (`#1`, `#2`, `#3`), ce qui impose un mécanisme `Idempotency-Key` pour tolérer les coupures réseau mobiles. Quant à `PATCH`, il applique un différentiel partiel sur un sous-ensemble d'attributs sans écraser les colonnes omises.",
                "**Enveloppe JSON normalisée et horodatage international ISO 8601.** Une API Flask de niveau industriel sépare systématiquement la charge métier (`data`) des métadonnées techniques (`meta` regroupant version du contrat, pagination et horodatage). Pour éliminer toute ambiguïté régionale entre formats `JJ/MM/AAAA` et `MM/JJ/AAAA`, toutes les dates sont sérialisées en UTC selon la norme **ISO 8601** (`\"2026-11-07T16:30:00Z\"`) avec `ensure_ascii=False` pour préserver l'encodage UTF-8."
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
                "text": "Saisir une adresse dans la barre d'URL d'un navigateur déclenche exclusivement une requête **`GET`**, dépourvue de charge utile JSON et d'en-têtes d'authentification personnalisés tels que `Authorization: Bearer` ou `X-API-Key`.\n\nPour éprouver l'ensemble des verbes **`POST`**, **`PUT`**, **`PATCH`** et **`DELETE`**, injecter des en-têtes cryptographiques et inspecter les codes de statut exacts (`201`, `401`, `422`, `429`) renvoyés par Flask et Gunicorn, l'ingénieur API combine au quotidien **les clients en ligne de commande (`curl`, `HTTPie`)** et **les environnements graphiques ou déclaratifs (`Postman`, `Bruno`, `Insomnia`, fichiers `.http`)**."
            },
            "explanation": [
                "**Diagnostic universel en terminal avec `curl` sur serveur distant ou conteneur.** Présent nativement sur Linux, macOS, Windows et dans la quasi-totalité des images Docker de production, `curl` permet de qualifier un worker Gunicorn directement en session SSH sans interface graphique. La maîtrise combinée de `-i` (affichage des en-têtes de réponse), `-v` (trace bidirectionnelle complète `>` et `<`), `-s` (mode silencieux chaînable vers `jq` ou `python3 -m json.tool`), `-X` (choix du verbe), `-H` (injection d'en-têtes), `-d` (corps de requête) et `-w` (mesure de latence et code HTTP) couvre l'intégralité des besoins d'audit réseau.",
                "**Industrialisation des tests d'équipe avec Postman, Bruno et Insomnia.** Les clients graphiques structurent les appels d'un projet au sein de **Collections** partageables et exploitent des **Variables d'Environnement** (`{{base_url}}`, `{{access_token}}`) pour basculer instantanément du serveur Werkzeug local (`http://127.0.0.1:5000`) vers l'instance de pré-production ou de production. Lors d'un `POST` ou d'un `PUT`, la sélection du mode *Body -> raw -> JSON* sérialise la charge utile tout en positionnant automatiquement l'en-tête `Content-Type: application/json` exigé par `request.get_json()`.",
                "**Productivité moderne au clavier avec HTTPie et les fichiers versionnés `.http`.** L'utilitaire `HTTPie` condense l'écriture des requêtes JSON en terminal grâce à un typage déclaratif distinguant les chaînes (`titre=\"Flask\"`) des entiers natifs (`duree_jours:=5`) avec coloration syntaxique automatique. En complément, l'extension *REST Client* de VS Code ou Antigravity exécute des scénarios décrits dans de simples fichiers texte `.http` versionnés dans Git au plus près des routes Flask qu'ils vérifient."
            ],
            "code": _read("05_outils_curl_postman_httpie.py"),
            "line_explanations": [
                {"lines": "30-33", "text": "Test 1 : `curl -s -i` interroge la route paginée en affichant les en-têtes HTTP de réponse (`HTTP/1.1 200 OK`, `Content-Type`, etc.)."},
                {"lines": "36-39", "text": "Test 2 : L'option `-H 'X-API-Key: isgp-secret-2026'` injecte l'en-tête d'authentification requis par le serveur."},
                {"lines": "42-51", "text": "Test 3 : `-X POST -H 'Content-Type: application/json' -d '{...}'` envoie un corps JSON (lu par `request.get_json()`)."},
                {"lines": "54-62", "text": "Test 4 : `-X POST -d 'titre=...&duree_jours=3'` envoie des données de formulaire HTML en `application/x-www-form-urlencoded` (lues par `request.form`)."}
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
