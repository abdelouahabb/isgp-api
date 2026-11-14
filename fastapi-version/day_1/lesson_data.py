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
    "goal": "Comprendre l'évolution historique des services Web (HTML, SOAP/XML, REST/JSON, GraphQL, gRPC), décoder la pile réseau (DNS, IP, Port TCP, TLS), inspecter une trame HTTP brute, maîtriser la propriété d'idempotence des verbes HTTP et structurer des enveloppes JSON professionnelles avec FastAPI et Pydantic v2.",
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
                    "Au cours de la première décennie du Web, les serveurs d'application généraient exclusivement des documents **HTML** destinés à être interprétés visuellement par la rétine humaine dans un navigateur. Dès que des systèmes bancaires, des opérateurs télécoms ou des applications mobiles natives ont dû interroger ces serveurs par programme, le couplage entre données métier et balises de mise en page s'est révélé intenable : modifier une simple classe CSS ou imbriquer une balise `<div>` brisait instantanément les automates clients.\n\n"
                    "C'est pour abolir cette fragilité structurelle qu'a émergé l'ingénierie des **Services Web** et des **APIs**, où le serveur n'expose plus une représentation graphique, mais un contrat de données pur, typé et indépendant de tout écran."
                )
            },
            "explanation": [
                "**Interopérabilité machine-à-machine (M2M) indépendante du langage.** Un service Web au sens architectural désigne un composant logiciel accessible sur un réseau IP qui échange des messages normalisés selon une grammaire universelle : un progiciel écrit en Java ou C#, une application mobile Kotlin ou Swift et un script d'automatisation Linux peuvent ainsi dialoguer sans friction avec un backend Python propulsé par FastAPI et Uvicorn.",
                "**Positionnement architectural de SOAP/XML, REST/JSON, GraphQL et gRPC.** Alors que le protocole historique **SOAP** des années 2000 encapsulait chaque appel dans une enveloppe XML verbeuse régie par un contrat WSDL sur un tunnel `POST` unique, le style architectural **REST** formalisé par Roy Fielding exploite nativement la sémantique du protocole HTTP — verbes d'action, codes d'état à trois chiffres, en-têtes de cache — alliée à la compacité de **JSON**, propulsant aujourd'hui plus de 85 % des APIs d'entreprise. Les architectures **GraphQL** (requêtage déclaratif de graphes sur `/graphql`) et **gRPC** (sérialisation binaire Protocol Buffers multiplexée sur HTTP/2 entre microservices internes) complètent cet écosystème sur des créneaux spécialisés.",
                "**Découplage strict entre noyau métier ASGI et canaux de présentation.** En exposant le domaine métier sous la forme d'une API REST JSON validée par Pydantic v2 dans FastAPI, l'organisation isole durablement sa logique transactionnelle de ses interfaces visuelles : une seule source de vérité serveur alimente simultanément le portail Web React ou Jinja2, les applications mobiles iOS/Android et les systèmes d'information partenaires."
            ],
            "code": _read("01_html_vs_json.py"),
            "line_explanations": [
                {"lines": "16-18", "text": "Création de l'instance `FastAPI` et configuration de `Jinja2Templates` pointant vers `day_1/templates/` (zéro HTML codé en dur dans Python)."},
                {"lines": "30-37", "text": "Approche Web classique : `@app.get('/meteo/html', response_class=HTMLResponse)` et `templates.TemplateResponse(...)` injectent les données dans le gabarit Jinja2 `meteo.html`."},
                {"lines": "41-54", "text": "Enveloppe SOAP/XML historique : structure hiérarchique verbeuse (`<soap:Envelope>`, `<soap:Body>`) retournée via `Response(media_type='application/xml')`."},
                {"lines": "58-61", "text": "Approche API REST moderne dans FastAPI : retourner un dictionnaire Python le sérialise automatiquement en `JSONResponse` (`application/json`)."},
                {"lines": "65-71", "text": "Portail Web interactif sur `GET /` (`portail_html_vs_json.html`) interrogeant en direct les trois formats via `fetch()`."},
                {"lines": "74-86", "text": "Exécution comparative automatique via `TestClient(app)` mesurant la taille exacte en octets et le `Content-Type` des trois formats."}
            ],
            "sandbox_preset": {
                "label": "Tester une réponse REST/JSON réelle : GET /api/sandbox/meteo?ville=Alger",
                "method": "GET",
                "url": "/api/sandbox/meteo?ville=Alger",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez day_1/01_html_vs_json.py pour comparer l'empreinte en octets de HTML (Jinja2Templates), SOAP/XML et REST/JSON (FastAPI) :",
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
                    "Lorsqu'une application cliente invoque `https://api.isgp.dz:8443/api/v1/formations?ville=Alger`, une séquence ordonnée de quatre négociations réseau s'accomplit au niveau du noyau du système d'exploitation en quelques millisecondes, bien avant que la boucle d'événements ASGI d'Uvicorn et votre route Python FastAPI ne reçoivent le premier octet.\n\n"
                    "Comprendre cette pile protocolaire permet de diagnostiquer immédiatement en production si une défaillance provient d'un nom de domaine introuvable (DNS), d'un pare-feu ou processus éteint (Port TCP), d'un certificat expiré (TLS) ou d'une route applicative absente (`404`)."
                )
            },
            "explanation": [
                "**Séquence d'établissement d'un appel réseau (DNS, Socket TCP, TLS et HTTP).** Le client interroge d'abord le résolveur **DNS** pour traduire le nom symbolique `api.isgp.dz` en adresse **IP** routable (tandis qu'en local `localhost` pointe directement sur la boucle interne `127.0.0.1`), puis réalise la poignée de main TCP en trois temps (*SYN, SYN-ACK, ACK*) vers le couple `IP:Port` cible (`80` pour HTTP, `443` pour HTTPS, `8000` par défaut pour Uvicorn). Si le schéma est `https://`, une négociation cryptographique **TLS 1.3** établit des clés de session symétriques authentifiées par certificat X.509 avant que la requête HTTP en clair ne soit injectée dans ce tunnel chiffré vers Uvicorn.",
                "**Grammaire formelle d'une URI selon la norme IETF RFC 3986.** Une adresse Web se décompose en cinq segments normalisés aux rôles distincts : le `scheme` (`http` ou `https`) fixe le protocole de transport, l'`authority` (`api.isgp.dz:8443`) désigne l'hôte et le port TCP d'écoute, le `path` hiérarchique (`/api/v1/formations`) guide le routeur Starlette/FastAPI vers l'endpoint visé, et la `query` introduite par `?` (`ville=Alger&page=2`) transmet les critères de filtrage et de pagination sous forme de paires clé-valeur séparées par `&`, tandis que le `fragment` après `#` demeure strictement local au navigateur client."
            ],
            "code": _read("03_analyseur_uri_et_reseau.py"),
            "line_explanations": [
                {"lines": "5-6", "text": "`urlparse` et `parse_qs` (`urllib.parse`) + imports FastAPI (`FastAPI`, `HTTPException`, `Response`, `status`, `TestClient`)."},
                {"lines": "10-24", "text": "Découpage RFC 3986 de l'URI en 6 composants normalisés et extraction des paramètres de requête après `?`."},
                {"lines": "27-57", "text": "Démonstration FastAPI : routes `@app.get` (`status.HTTP_200_OK`), `@app.post` (`status.HTTP_201_CREATED` + en-tête `Location`) et `@app.delete` (`status.HTTP_204_NO_CONTENT`)."}
            ],
            "python_runner": {
                "prompt": "Exécutez l'analyseur d'URI RFC 3986 et la simulation des codes HTTP FastAPI (200, 201, 204) :",
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
                    "Nombre de développeurs consomment des bibliothèques de haut niveau pendant des années sans jamais inspecter les octets réels qui transitent sur le descripteur de socket TCP. Or, HTTP/1.1 (RFC 9112) est un **protocole textuel lisible à l'œil nu**, dont l'élégance tient à une structure invariable en trois zones physiques.\n\n"
                    "Qu'il s'agisse d'une requête émise par `curl` ou d'une réponse forgée par Uvicorn, chaque message commence par une ligne de départ, déroule ses en-têtes de métadonnées, marque une ligne strictement vide (`\\r\\n\\r\\n`), puis déverse les octets éventuels de la charge utile."
                )
            },
            "explanation": [
                "**Structure tripartite d'une trame HTTP/1.1 et délimiteur `\\r\\n\\r\\n`.** Tout message HTTP s'ouvre sur une *Start Line* (`POST /api/v1/formations HTTP/1.1` à l'aller, `HTTP/1.1 201 Created` au retour), suivie d'une collection d'en-têtes `Nom: Valeur` terminés chacun par `CR+LF` (`\\r\\n`). Une séquence vide obligatoire de quatre octets (`\\r\\n\\r\\n`) matérialise la frontière physique exacte entre ces métadonnées de contrôle et le flux d'octets du corps (`Body`), dont la longueur en octets UTF-8 est annoncée par `Content-Length`.",
                "**Gouvernance protocolaire par les familles d'en-têtes HTTP dans FastAPI.** L'analyseur C `httptools` d'Uvicorn transmet les en-têtes dans le dictionnaire ASGI `scope[\"headers\"]`, où FastAPI pilote automatiquement le traitement : `Content-Type` oriente le décodage du corps vers Pydantic `BaseModel` (`application/json`) ou vers `python-multipart` et `Form(...)` (`application/x-www-form-urlencoded`), `Authorization` et `X-API-Key` alimentent les dépendances de sécurité `Security(...)`, `X-Request-ID` assure la corrélation distribuée des journaux, `X-RateLimit-*` et `Retry-After` régulent la pression client, tandis que `Cache-Control`, `ETag` et `Access-Control-Allow-Origin` gouvernent respectivement les caches intermédiaires et la politique CORS des navigateurs."
            ],
            "code": _read("04_trame_http_et_headers.py"),
            "line_explanations": [
                {"lines": "12-26", "text": "Construction d'une trame brute HTTP/1.1 avec ligne de départ (`POST ... HTTP/1.1`), en-têtes (`Host`, `Content-Type`, `Content-Length`) et ligne vide obligatoire (`\\r\\n\\r\\n`)."},
                {"lines": "29-38", "text": "Trame 1 (API JSON sur port `8000`) : `Content-Type: application/json; charset=utf-8` — validée automatiquement par un modèle Pydantic `BaseModel` dans FastAPI."},
                {"lines": "40-48", "text": "Trame 2 (Formulaire HTML `<form method='POST'>`) : `Content-Type: application/x-www-form-urlencoded` — extraite par `Form(...)` dans FastAPI."},
                {"lines": "56-91", "text": "Vérification en direct avec FastAPI (`BaseModel` vs `Form(...)` + `Header(...)`) et `TestClient`."}
            ],
            "python_runner": {
                "prompt": "Générez la trame HTTP/1.1 brute et observez comment FastAPI reçoit un corps JSON (BaseModel) vs un Formulaire HTML (Form) :",
                "initial_code": _read("04_trame_http_et_headers.py")
            },
            "vscode_instructions": {
                "filename": "day_1/04_trame_http_et_headers.py",
                "steps": [
                    "Ouvrir `day_1/04_trame_http_et_headers.py` dans l'éditeur.",
                    "Exécuter `.venv/bin/python day_1/04_trame_http_et_headers.py` et observer la séparation entre la ligne de requête, les en-têtes et le corps JSON."
                ]
            }
        },
        {
            "id": "d1-l4",
            "file": "day_1/02_serialisation_json.py",
            "title": "1.4 — Sémantique des Méthodes HTTP, Idempotence (`GET`, `PUT`, `PATCH`, `POST`, `DELETE`) & Sérialisation Pydantic v2",
            "duration": "60 min",
            "analogy": {
                "title": "Appuyer plusieurs fois sur le bouton d'appel d'un ascenseur (Idempotent) vs Payer deux fois par carte (Non-Idempotent)",
                "text": (
                    "Que vous pressiez une seule fois ou dix fois consécutives le bouton d'appel d'un ascenseur au troisième étage, l'état final du système demeure rigoureusement identique : la cabine se stabilise au troisième palier. En algèbre comme en architecture des systèmes distribués, cette invariance par répétition porte le nom d'**idempotence** (`f(f(x)) = f(x)`).\n\n"
                    "À l'opposé, soumettre deux fois un ordre de virement bancaire dépourvu de clé de déduplication débite deux fois le compte du donneur d'ordre : sur des réseaux mobiles ou interbancaires sujets aux micro-coupures, maîtriser la frontière entre verbes HTTP idempotents et non idempotents conditionne directement la fiabilité financière d'une API."
                )
            },
            "explanation": [
                "**Classification normative des méthodes HTTP : sûreté (*Safe*) et idempotence (RFC 9110).** Une méthode est dite *sûre* lorsqu'elle garantit l'absence de toute mutation d'état sur le serveur (`GET`, `HEAD`, `OPTIONS`), et *idempotente* lorsque la répétition identique d'une requête produit exactement le même état serveur qu'une exécution unique : `GET`, le remplacement intégral `PUT /formations/1` et la suppression `DELETE /formations/1` sont tous trois idempotents et peuvent être rejoués automatiquement par un proxy ou un SDK mobile après une perte de connexion. À l'inverse, `POST /formations` n'est ni sûr ni idempotent — trois envois créent trois enregistrements distincts sauf implémentation explicite d'un en-tête `Idempotency-Key` — tandis que `PATCH` réalise une mutation partielle rendue idempotente lorsqu'elle affecte des valeurs déterministes via `payload.model_dump(exclude_unset=True)`.",
                "**Enveloppes JSON contractuelles et moteur de sérialisation Rust Pydantic v2.** Structurer toute réponse d'entreprise autour d'un couple normalisé `meta` (version du contrat, pagination, horodatage UTC au format international ISO 8601 `YYYY-MM-DDTHH:MM:SSZ`) et `data` (entité ou collection métier) offre une extensibilité durable sans rupture de schéma. Dans FastAPI, déclarer `response_model=EnveloppeReponseAPI` délègue la validation et la sérialisation JSON UTF-8 (`.model_dump_json()` / `.model_validate_json()`) directement au noyau compilé en Rust `pydantic-core`, conjuguant sûreté de typage statique et débit maximal."
            ],
            "code": _read("02_serialisation_json.py"),
            "line_explanations": [
                {"lines": "11-31", "text": "Définition des modèles Pydantic v2 `MetaReponse`, `DonneesFormation` et `EnveloppeReponseAPI` avec horodatage UTC ISO 8601 (`Field(default_factory=...)`)."},
                {"lines": "36-48", "text": "Route FastAPI `@app.get('/api/v1/enveloppe', response_model=EnveloppeReponseAPI)` garantissant par contrat la structure exacte de sortie."},
                {"lines": "51-64", "text": "Sérialisation via `model_dump_json(indent=2)` et désérialisation/validation via `model_validate_json()`."}
            ],
            "sandbox_preset": {
                "label": "Tester les codes HTTP (200, 201, 400, 401, 404, 429) : GET /api/sandbox/status-demo/429",
                "method": "GET",
                "url": "/api/sandbox/status-demo/429",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez day_1/02_serialisation_json.py pour générer une enveloppe JSON typée avec Pydantic v2 et horodatage ISO 8601 :",
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
            "title": "1.5 — Tester & Diagnostiquer une API : Maîtriser `curl`, Postman, HTTPie et REST Client (`.http`)",
            "duration": "65 min",
            "analogy": {
                "title": "Pourquoi un navigateur Web classique (Chrome/Firefox) ne suffit plus pour tester une API ?",
                "text": (
                    "Saisir une URL dans la barre d'adresse d'un navigateur graphique ne déclenche qu'un seul type d'interaction réseau : une requête **`GET`** dépourvue de corps JSON et incapable d'injecter à la demande des en-têtes d'authentification `Authorization: Bearer` ou `X-API-Key`.\n\n"
                    "Pour éprouver rigoureusement les mutations **`POST`**, **`PUT`**, **`PATCH`** et **`DELETE`**, forger des en-têtes cryptographiques et auditer les codes de statut exacts (`201`, `401`, `422`, `429`), l'ingénieur backend s'appuie sur une chaîne d'instrumentation dédiée associant l'outil universel en ligne de commande **`curl`** (ou **`HTTPie`**), les environnements collaboratifs (**`Postman`**, **`Bruno`**, **`Insomnia`**) et le portail **Swagger UI (`/docs`)** généré nativement par FastAPI."
                )
            },
            "explanation": [
                "**Omniprésence opérationnelle de `curl` en production et en diagnostic SSH.** Sur une machine virtuelle Linux distante jointe en SSH, à l'intérieur d'un conteneur Docker minimaliste ou dans un pipeline CI/CD, aucune interface graphique n'est disponible : `curl` permet alors de forger n'importe quelle trame HTTP avec une précision chirurgicale grâce à ses commutateurs fondamentaux (`-i` pour afficher le statut et les en-têtes reçus, `-v` pour inspecter le dialogue TCP bidirectionnel `>` et `<`, `-X` pour fixer le verbe HTTP, `-H` pour injecter les en-têtes `Content-Type` ou `Authorization`, `-d` ou `--json` pour transmettre la charge utile, `-s` pour chaîner la sortie vers `jq`, et `-w` pour chronométrer la latence exacte).",
                "**Gouvernance des collections d'équipe avec Postman, Bruno et Insomnia.** Les clients graphiques d'inspection structurent l'ensemble des endpoints d'un projet au sein de **Collections** versionnées accompagnées de **Variables d'Environnement** dynamiques (`{{base_url}}`, `{{access_token}}`), permettant aux équipes QA et Backend de basculer instantanément leurs campagnes de tests d'un serveur local Uvicorn (`http://127.0.0.1:8000`) vers une passerelle de pré-production (`https://staging-api.isgp.dz`) tout en gérant finement l'encodage `raw JSON`.",
                "**Ergonomie moderne en terminal (`HTTPie`) et tests déclaratifs versionnés (`.http`).** En complément de `curl`, l'utilitaire Python `HTTPie` accélère l'écriture interactive en terminal en distinguant nativement chaînes et types JSON (`http POST :8000/api/formations titre=\"FastAPI\" duree_jours:=5`), tandis que les fichiers `.http` de l'extension REST Client dans VS Code ou Antigravity IDE permettent d'archiver les scénarios de requêtes directement dans le dépôt Git au plus près du code source FastAPI."
            ],
            "code": _read("05_outils_curl_postman_httpie.py"),
            "line_explanations": [
                {"lines": "22-31", "text": "Route FastAPI `GET /api/sandbox/formations` avec paramètres de requête typés `Query(1, ge=1)`."},
                {"lines": "34-38", "text": "Route protégée par en-tête `Header(default=None, alias='X-API-Key')`."},
                {"lines": "41-45", "text": "Route `POST /api/sandbox/auth/token` validant le corps JSON via le modèle Pydantic `IdentifiantsIn`."},
                {"lines": "48-58", "text": "Route `POST /api/sandbox/formulaire-formation` lisant les champs `application/x-www-form-urlencoded` via `Form(...)`."}
            ],
            "sandbox_preset": {
                "label": "Tester dans le Client HTTP ou ouvrir l'onglet 'curl & Postman'",
                "method": "POST",
                "url": "/api/sandbox/auth/token",
                "body": '{\n  "identifiant": "stagiaire",\n  "mot_de_passe": "isgp2026"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez ces 4 scénarios `curl -i` contre l'application FastAPI et inspectez les en-têtes HTTP bruts retournés :",
                "initial_code": _read("05_outils_curl_postman_httpie.py")
            },
            "vscode_instructions": {
                "filename": "day_1/05_outils_curl_postman_httpie.py",
                "steps": [
                    "Ouvrir un terminal et tester directement : `curl -i http://127.0.0.1:8000/api/sandbox/formations`.",
                    "Rendez-vous également dans l'onglet dédié **curl & Postman** en haut de l'application pour exécuter des commandes `curl` interactives et télécharger la Collection Postman du bootcamp."
                ]
            }
        }
    ]
}
