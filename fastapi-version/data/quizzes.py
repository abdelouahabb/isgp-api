"""
Évaluations formatives approfondies (Jour 0 à Jour 5) — Édition FastAPI & Uvicorn (ASGI & Pydantic).
Chaque question contient une justification méthodique sans prérequis implicite.
"""

QUIZZES = {
    0: {
        "title": "Évaluation Jour 0 : Fondations Python, Exceptions & Décorateurs",
        "description": "Validation des structures de données Python, de l'accès défensif `.get()`, de la gestion d'exceptions `try/except` et du mécanisme des décorateurs `@`.",
        "questions": [
            {
                "id": "q0-1",
                "question": "Pourquoi préfère-t-on écrire `corps.get(\"duree_jours\", 5)` plutôt que `corps[\"duree_jours\"]` lors de la lecture d'un dictionnaire Python ?",
                "options": [
                    "Parce que .get() renvoie la valeur par défaut (5) si la clé est absente, tandis que corps['duree_jours'] lève une exception KeyError qui provoque un crash HTTP 500",
                    "Parce que les crochets [ ] sont interdits en Python 3",
                    "Parce que .get() chiffre automatiquement la donnée",
                    "Il n'y a aucune différence de comportement"
                ],
                "correct_index": 0,
                "explanation": "Un client externe peut toujours omettre un champ JSON. L'accès direct par crochets `d['cle']` lève une exception fatale `KeyError`, alors que `d.get('cle', defaut)` (ou un modèle Pydantic avec valeur par défaut) permet une programmation défensive sûre."
            },
            {
                "id": "q0-2",
                "question": "Que renvoie une fonction Python qui se termine sans instruction `return` explicite ?",
                "options": [
                    "La valeur spéciale None (qui correspond à null en JSON)",
                    "Le nombre entier 0",
                    "Une chaîne de caractères vide \"\"",
                    "Le dictionnaire {}"
                ],
                "correct_index": 0,
                "explanation": "En Python, toute fonction qui atteint sa dernière ligne sans rencontrer `return` retourne implicitement `None`."
            },
            {
                "id": "q0-3",
                "question": "Quel est le rôle exact d'un décorateur `@mon_decorateur` placé au-dessus d'une fonction `def ma_route():` ?",
                "options": [
                    "Envelopper la fonction ma_route dans une fonction d'ordre supérieur pour exécuter du code avant ou après elle (enregistrement de route @app.get, journalisation, chronométrage)",
                    "Transformer la fonction en commentaire ignoré par Python",
                    "Supprimer la fonction de la mémoire vive",
                    "Créer une table SQL portant le nom de la fonction"
                ],
                "correct_index": 0,
                "explanation": "La syntaxe `@mon_decorateur` est un sucre syntaxique pour `ma_route = mon_decorateur(ma_route)`. C'est le mécanisme central de FastAPI (`@app.get`, `@app.post`, `@app.middleware`)."
            },
            {
                "id": "q0-4",
                "question": "Dans une API Web, pourquoi une entrée client invalide (ex: `?page=abc` au lieu d'un entier) ne doit-elle jamais provoquer un code `500 Internal Server Error` ?",
                "options": [
                    "Parce qu'une erreur causée par une donnée invalide du client doit toujours être rejetée proprement avec un code 4xx (400 ou 422 Unprocessable Entity), tandis que 500 signale un bug interne du serveur",
                    "Pour accélérer la vitesse du processeur",
                    "Parce que la fonction int() ne fonctionne qu'à l'intérieur d'un bloc try",
                    "Pour convertir automatiquement 'abc' en 100"
                ],
                "correct_index": 0,
                "explanation": "Dans FastAPI, typer un paramètre `page: int = Query(1)` délègue cette vérification à Pydantic qui renvoie automatiquement un statut `422 Unprocessable Entity` si le client envoie `?page=abc`."
            }
        ]
    },
    1: {
        "title": "Évaluation Jour 1 : Réseau, Anatomie URI, Trame HTTP & JSON",
        "description": "Validation de la pile réseau (DNS/TCP/TLS), du découpage RFC 3986 d'une URI, de la trame brute HTTP/1.1 et de la sérialisation JSON.",
        "questions": [
            {
                "id": "q1-1",
                "question": "Dans l'URI `https://api.isgp.dz:8443/v1/formations?salle=Alger#details`, comment s'appelle la portion `salle=Alger` située après le point d'interrogation `?` ?",
                "options": [
                    "La Query String (chaîne de requête contenant les paramètres de filtrage/pagination)",
                    "Le Path (chemin hiérarchique)",
                    "Le Host (nom d'hôte)",
                    "Le Header d'authentification"
                ],
                "correct_index": 0,
                "explanation": "Selon la norme RFC 3986, la partie située après `?` est la **Query String** (injectée directement dans les arguments typés de la fonction dans FastAPI ou via `request.query_params`), tandis que `/v1/formations` est le **Path**."
            },
            {
                "id": "q1-2",
                "question": "Dans une trame brute HTTP/1.1, qu'est-ce qui sépare obligatoirement le bloc des En-têtes (`Headers`) du Corps du message (`Body` JSON) ?",
                "options": [
                    "Une ligne vide (séquence CR+LF suivie de CR+LF : \\r\\n\\r\\n)",
                    "Le mot-clé END_HEADERS",
                    "Une série de trois tirets ---",
                    "Un point-virgule ;"
                ],
                "correct_index": 0,
                "explanation": "Le protocole HTTP impose une ligne strictement vide (`\\r\\n\\r\\n`) pour marquer la fin des métadonnées (Headers) et le début des octets de la charge utile (Body)."
            },
            {
                "id": "q1-3",
                "question": "Quelle est la différence entre les en-têtes HTTP `Content-Type` et `Accept` envoyés par un client ?",
                "options": [
                    "Content-Type indique le format du corps envoyé par le client (ex: application/json), tandis qu'Accept indique le format de réponse souhaité en retour",
                    "Ils sont strictement identiques",
                    "Accept sert à envoyer le mot de passe et Content-Type sert au Rate Limiting",
                    "Content-Type n'existe que dans les réponses HTML"
                ],
                "correct_index": 0,
                "explanation": "`Content-Type` décrit la charge utile présente dans le message courant ; `Accept` permet la négociation de contenu (*Content Negotiation*) pour la réponse."
            },
            {
                "id": "q1-4",
                "question": "En Python, quelle est la différence exacte entre `json.dumps(data)` et `json.loads(texte)` ?",
                "options": [
                    "json.dumps() sérialise un objet Python en chaîne JSON, tandis que json.loads() désérialise une chaîne JSON en objet Python (dict/list)",
                    "json.dumps() supprime les données et json.loads() les sauvegarde sur disque",
                    "json.dumps() lit un fichier SQLite",
                    "L'un est réservé à GET et l'autre à DELETE"
                ],
                "correct_index": 0,
                "explanation": "`dumps` (*dump string*) convertit `dict -> str JSON` ; `loads` (*load string*) convertit `str JSON -> dict`."
            },
            {
                "id": "q1-5",
                "question": "Dans une commande `curl`, quel est le rôle exact des options `-i`, `-X POST`, `-H` et `-d` ?",
                "options": [
                    "-i affiche la ligne de statut et les en-têtes HTTP de réponse, -X POST choisit la méthode HTTP, -H ajoute un en-tête (Header) et -d envoie le corps (Body JSON)",
                    "-i installe Python, -X supprime le fichier, -H affiche l'aide et -d éteint le serveur",
                    "-i chiffre le disque dur et -d télécharge une base SQLite",
                    "Ces options ne fonctionnent qu'avec le protocole FTP"
                ],
                "correct_index": 0,
                "explanation": "`curl -i -X POST -H 'Content-Type: application/json' -d '{...}' URL` est la commande universelle permettant d'envoyer un Payload JSON et d'inspecter la réponse complète du serveur."
            }
        ]
    },
    2: {
        "title": "Évaluation Jour 2 : Maturité REST, Paramètres Typés, Pagination & Middlewares FastAPI",
        "description": "Validation du nommage RESTful, des paramètres `{id}: int` et `Query(...)`, des formulaires `Form(...)` / `Jinja2Templates` et de `@app.middleware('http')`.",
        "questions": [
            {
                "id": "q2-1",
                "question": "Selon les standards d'architecture REST (Niveau 2 de Richardson), comment doit-on concevoir l'endpoint permettant de supprimer la formation n°42 ?",
                "options": [
                    "Méthode DELETE sur l'URI nominale au pluriel : DELETE /api/formations/42 (@app.delete('/api/formations/{id}'))",
                    "Méthode GET sur l'URI : GET /api/supprimerFormation?id=42",
                    "Méthode POST sur l'URI : POST /api/delete_formation_42",
                    "Méthode PUT sur l'URI : PUT /api/formations/42/erase"
                ],
                "correct_index": 0,
                "explanation": "En REST, l'URI désigne la ressource par un **nom au pluriel** (`/api/formations/42`) et la méthode HTTP (`DELETE`) exprime l'action à accomplir. Une requête `GET` ne doit jamais modifier ou supprimer d'état."
            },
            {
                "id": "q2-2",
                "question": "Dans un système de pagination `Offset / Limit`, si le client demande `?page=3&limit=10`, quelle est la valeur de l'indice de départ (`offset`) ?",
                "options": [
                    "20 (calculé par la formule : (page - 1) * limit = (3 - 1) * 10)",
                    "30",
                    "3",
                    "10"
                ],
                "correct_index": 0,
                "explanation": "La page 1 couvre les indices `0..9` (`offset=0`), la page 2 couvre `10..19` (`offset=10`), et la page 3 commence à l'indice `20` (`offset = (3 - 1) * 10 = 20`)."
            },
            {
                "id": "q2-3",
                "question": "Pourquoi est-il indispensable d'utiliser un tuple de validation (`CHAMPS_TRI_AUTORISES = ('id', 'duree_jours')`) avant d'appliquer un paramètre de tri `?tri=...` ?",
                "options": [
                    "Pour empêcher le client de provoquer un crash KeyError ou une Injection SQL sur la clause ORDER BY en envoyant un nom de champ inexistant ou malveillant",
                    "Pour limiter la taille de l'URL à 20 caractères",
                    "Parce que Python ne sait trier que deux colonnes maximum",
                    "Pour chiffrer les paramètres d'URL"
                ],
                "correct_index": 0,
                "explanation": "Toute entrée utilisateur servant à désigner un nom de colonne ou d'attribut doit être validée contre une **liste blanche (*Whitelist*)** stricte."
            },
            {
                "id": "q2-4",
                "question": "À quoi sert l'en-tête `X-Request-ID` généré dans un middleware `@app.middleware('http')` et attaché à `request.state.request_id` ?",
                "options": [
                    "À attribuer un identifiant unique (UUID) à chaque requête pour corréler facilement la réponse reçue par le client avec les journaux (logs) internes du serveur",
                    "À remplacer le mot de passe de l'utilisateur",
                    "À compresser le corps JSON",
                    "À indiquer la version de Python installée"
                ],
                "correct_index": 0,
                "explanation": "Le `X-Request-ID` (ou *Correlation ID*) permet à l'équipe d'exploitation de retrouver instantanément la trace exacte d'une requête dans des millions de lignes de logs."
            },
            {
                "id": "q2-5",
                "question": "Quelle est la différence exacte entre `{id}`, `<int:id>` et `:id` lorsqu'on définit un paramètre dynamique de chemin ?",
                "options": [
                    "{id} est la syntaxe native de FastAPI et d'OpenAPI 3.0 (complétée par l'annotation Python id: int), <int:id> est la syntaxe de FastAPI/Werkzeug, et :id est la syntaxe de Postman/Express.js",
                    ":id est obligatoire dans @app.get() en FastAPI",
                    "<int:id> est la seule syntaxe reconnue par Starlette dans FastAPI",
                    "On doit écrire littéralement {id} dans la commande curl"
                ],
                "correct_index": 0,
                "explanation": "FastAPI adopte directement le standard OpenAPI `{id}` dans le chemin (`@app.get('/api/formations/{id}')`) et réalise la validation de type grâce aux *type hints* Python (`def lire(id: int):`)."
            },
            {
                "id": "q2-6",
                "question": "Lorsqu'un utilisateur soumet un formulaire HTML `<form method=\"POST\" action=\"/formations\">`, comment déclare-t-on les champs attendus dans une route FastAPI ?",
                "options": [
                    "Avec des paramètres Form(...) (ex: titre: str = Form(...)) car un formulaire HTML envoie ses données en application/x-www-form-urlencoded (et UploadFile = File(None) pour multipart/form-data)",
                    "Avec un modèle BaseModel JSON standard sans Form(...)",
                    "Avec Query(...) dans l'URL",
                    "FastAPI ne supporte pas les formulaires HTML ni Jinja2"
                ],
                "correct_index": 0,
                "explanation": "Un `<form method='POST'>` encode les champs `<input name='...'>` en `application/x-www-form-urlencoded` (ou `multipart/form-data`). Dans FastAPI, on les extrait de manière typée avec `Form(...)` et `File(...)`."
            }
        ]
    },
    3: {
        "title": "Évaluation Jour 3 : Validation Pydantic & RFC 7807, Idempotence, PUT vs PATCH & SQLite",
        "description": "Validation des codes 400 vs 422, des modèles `BaseModel` / `Field`, de l'idempotence (`Idempotency-Key`), de `@app.exception_handler` et des requêtes SQL paramétrées.",
        "questions": [
            {
                "id": "q3-1",
                "question": "Quelle est la différence précise entre les codes HTTP `400 Bad Request` et `422 Unprocessable Entity` ?",
                "options": [
                    "400 indique une erreur de syntaxe brute (JSON mal formé), tandis que 422 indique un JSON syntaxiquement valide mais violant le schéma Pydantic ou les règles métier (ex: duree_jours = -5)",
                    "400 est une erreur serveur et 422 est un succès",
                    "422 signifie que le serveur est éteint",
                    "Il n'y a aucune différence"
                ],
                "correct_index": 0,
                "explanation": "FastAPI et Pydantic utilisent nativement `422 Unprocessable Entity` lorsqu'un JSON valide ne respecte pas les contraintes de types ou les règles `Field(ge=1, le=30)` / `@field_validator`."
            },
            {
                "id": "q3-2",
                "question": "Quelle est la différence entre les méthodes HTTP `PUT` et `PATCH` sur `/api/formations/1`, et pourquoi `POST` utilise-t-il `Idempotency-Key` ?",
                "options": [
                    "PUT remplace intégralement la ressource (idempotent), PATCH modifie partiellement les champs fournis (exclude_unset=True dans Pydantic), et Idempotency-Key empêche un POST répété de créer des doublons",
                    "PUT supprime la ressource et PATCH la crée",
                    "POST est naturellement idempotent sans en-tête",
                    "PATCH sert uniquement à lire des données comme GET"
                ],
                "correct_index": 0,
                "explanation": "`PUT` remplace l'état complet (idempotent). `PATCH` applique un delta partiel (`payload.model_dump(exclude_unset=True)`). Comme `POST` n'est pas idempotent, l'en-tête `Idempotency-Key` garantit qu'un réessai réseau ne duplique pas l'opération."
            },
            {
                "id": "q3-3",
                "question": "Pourquoi configure-t-on `@app.exception_handler(StarletteHTTPException)`, `@app.exception_handler(RequestValidationError)` et `@app.exception_handler(Exception)` dans une API FastAPI ?",
                "options": [
                    "Pour uniformiser toutes les réponses d'erreur (404, 405, 422, 500) au format standardisé RFC 7807 (application/problem+json) sans jamais divulguer la pile d'exécution Python en cas de crash 500",
                    "Pour désactiver toutes les vérifications de sécurité",
                    "Pour transformer toutes les erreurs 404 en 200 OK",
                    "Pour supprimer la base de données en cas d'erreur"
                ],
                "correct_index": 0,
                "explanation": "Les gestionnaires `@app.exception_handler` permettent d'envelopper toutes les erreurs HTTP, les erreurs de validation Pydantic et les exceptions inattendues dans un contrat JSON RFC 7807 homogène."
            },
            {
                "id": "q3-4",
                "question": "Pourquoi utilise-t-on obligatoirement des marqueurs `?` dans `conn.execute(\"SELECT * FROM formations WHERE id = ?\", (id,))` ?",
                "options": [
                    "Pour séparer le code SQL des données utilisateur (requête paramétrée) et neutraliser totalement les attaques par Injection SQL",
                    "Parce que Python interdit les f-strings avec les chaînes contenant le mot SELECT",
                    "Pour afficher des points d'interrogation dans le terminal",
                    "Uniquement pour accélérer l'écriture du code"
                ],
                "correct_index": 0,
                "explanation": "Concaténer une variable dans du SQL avec `f\"...\"` permet à un attaquant d'injecter des commandes SQL (`' OR '1'='1`). Les requêtes paramétrées `?` rendent l'injection SQL impossible."
            },
            {
                "id": "q3-5",
                "question": "Quel type MIME normalisé par l'IETF (RFC 7807) désigne un objet JSON d'erreur standardisé, et quel code HTTP retourne-t-on si le client envoie un `Content-Type` non supporté par la route ?",
                "options": [
                    "Type MIME application/problem+json pour les erreurs RFC 7807, et code HTTP 415 Unsupported Media Type si le Content-Type entrant n'est pas supporté",
                    "Type MIME text/error et code HTTP 200 OK",
                    "Type MIME image/png et code HTTP 302 Found",
                    "Type MIME multipart/form-data et code HTTP 500"
                ],
                "correct_index": 0,
                "explanation": "La RFC 7807 définit le type MIME `application/problem+json` (`type`, `title`, `status`, `detail`), et le code `415 Unsupported Media Type` indique que le format MIME envoyé par le client est refusé."
            }
        ]
    },
    4: {
        "title": "Évaluation Jour 4 : Secrets, Depends(), Bearer Tokens, RBAC (401 vs 403), Rate Limit & Webhooks",
        "description": "Validation complète de l'architecture de sécurité FastAPI : `Depends()`, cryptographie, Bearer Tokens, RBAC, Rate Limiting et Webhooks HMAC.",
        "questions": [
            {
                "id": "q4-1",
                "question": "Pourquoi ne faut-il JAMAIS stocker d'information confidentielle (ex: mot de passe ou numéro de carte) à l'intérieur du Payload d'un Bearer Token (JWT / itsdangerous) ?",
                "options": [
                    "Parce que le Payload d'un jeton signé est simplement encodé en Base64 (lisible par quiconque sans clé) : la signature HMAC empêche la modification mais ne chiffre pas le contenu",
                    "Parce qu'un Token ne peut contenir que des nombres entiers",
                    "Parce que Base64 détruit les caractères alphabétiques",
                    "Parce que le serveur ne peut pas relire le Payload"
                ],
                "correct_index": 0,
                "explanation": "Un jeton signé garantit l'**intégrité** et l'**authenticité** (grâce à la signature HMAC calculée avec `SECRET_KEY`), mais son contenu Base64 est lisible en clair par toute personne possédant le jeton."
            },
            {
                "id": "q4-2",
                "question": "Dans un contrôle d'accès par rôle (RBAC) injecté via `Depends(exiger_role('admin'))`, quelle est la distinction exacte entre `401 Unauthorized` et `403 Forbidden` ?",
                "options": [
                    "401 indique que le client n'est pas authentifié (jeton absent, expiré ou falsifié), tandis que 403 indique que le jeton est valide mais que le rôle de l'utilisateur ('stagiaire') est insuffisant pour la route ('admin')",
                    "401 est pour les erreurs de base de données et 403 pour le Rate Limiting",
                    "403 signifie que le jeton a expiré et qu'il faut utiliser le Refresh Token",
                    "Ils sont interchangeables"
                ],
                "correct_index": 0,
                "explanation": "`401` = défaut d'**Authentification** (« Qui êtes-vous ? »). `403` = défaut d'**Autorisation** (« Nous savons qui vous êtes, mais vous n'avez pas la permission »)."
            },
            {
                "id": "q4-3",
                "question": "Pourquoi utilise-t-on un couple `Access Token` (courte durée : 5 min) + `Refresh Token` (longue durée : 7 jours) plutôt qu'un seul jeton valable 7 jours ?",
                "options": [
                    "Pour limiter drastiquement la fenêtre de vulnérabilité si un Access Token est intercepté, tout en permettant au client de renouveler sa session sur /api/auth/refresh sans redemander le mot de passe",
                    "Pour envoyer deux en-têtes Authorization simultanément à chaque requête GET",
                    "Parce que FastAPI refuse les jetons de plus de 300 secondes",
                    "Pour doubler la taille des messages HTTP"
                ],
                "correct_index": 0,
                "explanation": "L'`Access Token` voyage sur chaque requête mais expire très vite (5 min). Le `Refresh Token` ne sort que rarement (uniquement vers `/api/auth/refresh`) et peut être révoqué en base."
            },
            {
                "id": "q4-4",
                "question": "Quel code HTTP et quels en-têtes une API renvoie-t-elle lorsqu'un client dépasse son quota de Rate Limiting ?",
                "options": [
                    "Statut 429 Too Many Requests avec les en-têtes X-RateLimit-Limit, X-RateLimit-Remaining: 0 et Retry-After",
                    "Statut 403 Forbidden avec l'en-tête Content-Length",
                    "Statut 500 Internal Server Error",
                    "Statut 204 No Content"
                ],
                "correct_index": 0,
                "explanation": "Le code `429 Too Many Requests` accompagné de `Retry-After` (secondes à attendre) permet aux clients automatisés de mettre en pause leurs appels proprement."
            },
            {
                "id": "q4-5",
                "question": "Dans FastAPI, comment votre route vérifie-t-elle qu'un Webhook entrant (`POST /api/webhooks/paiement`) provient bien du partenaire bancaire et non d'un pirate ?",
                "options": [
                    "En recalculant l'empreinte HMAC-SHA256 sur les octets bruts du corps (await request.body()) avec le WEBHOOK_SECRET partagé et en la comparant en temps constant (hmac.compare_digest) à l'en-tête X-Webhook-Signature",
                    "En faisant confiance à tout message JSON contenant 'statut': 'paye'",
                    "En vérifiant uniquement l'en-tête User-Agent",
                    "En demandant à l'utilisateur de saisir son mot de passe"
                ],
                "correct_index": 0,
                "explanation": "La signature `HMAC-SHA256` calculée sur les octets exacts reçus (`await request.body()`) avec un secret partagé garantit à la fois l'identité de l'émetteur du Webhook et l'intégrité du message."
            },
            {
                "id": "q4-6",
                "question": "En gestion d'API (API Management), qu'est-ce qu'une vulnérabilité BOLA (*Broken Object Level Authorization*, n°1 du Top 10 OWASP API) ?",
                "options": [
                    "Une faille d'Autorisation (AuthZ) où un utilisateur authentifié (ex: stagiaire #101) parvient à lire ou modifier les données d'un autre utilisateur (#102) simplement en changeant l'ID dans l'URL (/api/dossiers/102)",
                    "Une erreur de syntaxe dans un fichier JSON",
                    "Un problème de connexion au serveur DNS",
                    "Le fait d'utiliser le port 8000 en développement"
                ],
                "correct_index": 0,
                "explanation": "Vérifier uniquement que le jeton est valide (`AuthN`) ne suffit pas ! Le serveur doit impérativement vérifier l'**Autorisation au niveau de l'objet (`AuthZ`)** : `dossier['proprietaire'] == user['sub']`."
            },
            {
                "id": "q4-7",
                "question": "Pourquoi est-il recommandé de stocker un jeton de session Web dans un Cookie avec les drapeaux `HttpOnly`, `Secure` et `SameSite=strict` plutôt que dans `window.localStorage` ?",
                "options": [
                    "Parce que le drapeau HttpOnly interdit toute lecture du cookie par JavaScript (document.cookie -> protection anti-XSS), Secure impose HTTPS, et SameSite=strict bloque l'envoi inter-sites (protection anti-CSRF)",
                    "Parce que localStorage est limité à 2 caractères maximum",
                    "Parce que les cookies sont exécutés comme du code Python dans le navigateur",
                    "Parce que localStorage supprime automatiquement la base de données SQLite"
                ],
                "correct_index": 0,
                "explanation": "Contrairement à `localStorage` qui est lisible par n'importe quel script JavaScript injecté (faille XSS), un cookie `HttpOnly` est totalement isolé du DOM JavaScript et géré uniquement par la couche réseau HTTP du navigateur."
            },
            {
                "id": "q4-8",
                "question": "Quelle est la différence de sécurité entre un cookie ordinaire créé par `response.set_cookie('role', 'admin')` et un cookie de session signé par HMAC (`URLSafeTimedSerializer` / `SessionMiddleware`) ?",
                "options": [
                    "Un cookie ordinaire est stocké en texte clair et peut être modifié librement par l'utilisateur dans son navigateur (F12), tandis qu'un cookie de session signé est scellé cryptographiquement par HMAC avec SECRET_KEY (infalsifiable)",
                    "Il n'y a aucune différence, les deux sont chiffrés par la carte graphique",
                    "response.set_cookie() ne fonctionne qu'avec Internet Explorer",
                    "Le cookie signé envoie un SMS à l'administrateur"
                ],
                "correct_index": 0,
                "explanation": "Un cookie non signé ne doit jamais servir à stocker une identité ou un rôle ! Seul un cookie signé par HMAC avec `SECRET_KEY` garantit que le client n'a pas modifié sa valeur."
            }
        ]
    },
    5: {
        "title": "Évaluation Jour 5 : Client Résilient, APIRouter, TestClient & Production ASGI",
        "description": "Validation des Timeouts clients (`httpx`), de l'architecture modulaire par `APIRouter`, des sondes Healthcheck, de `TestClient(app)` et du déploiement Uvicorn/Gunicorn.",
        "questions": [
            {
                "id": "q5-1",
                "question": "Pourquoi un client HTTP Python (`httpx` ou `urlopen`) doit-il TOUJOURS définir un paramètre `timeout` explicite lors d'un appel vers une API externe ?",
                "options": [
                    "Pour éviter que la coroutine ou le worker ne reste figé indéfiniment si le serveur distant ne répond plus, ce qui provoquerait une panne en cascade (Cascading Failure)",
                    "Pour compresser automatiquement la réponse JSON",
                    "Parce que Python refuse d'exécuter une requête sans timeout",
                    "Pour contourner le Rate Limiting du serveur distant"
                ],
                "correct_index": 0,
                "explanation": "Sans `timeout`, une connexion réseau pendante bloque la tâche ou le worker indéfiniment. En production, chaque appel réseau externe doit avoir un timeout strict (ex: 3 à 5 secondes)."
            },
            {
                "id": "q5-2",
                "question": "Quel est le rôle des routes `/api/health/live` (*Liveness*) et `/api/health/ready` (*Readiness*) dans une architecture de production ?",
                "options": [
                    "Permettre aux répartiteurs de charge (Load Balancers / Kubernetes / Nginx) de vérifier automatiquement si le processus ASGI répond (live) et si ses dépendances comme la base de données sont prêtes (ready)",
                    "Afficher la liste des mots de passe des administrateurs",
                    "Générer des Bearer Tokens pour les stagiaires",
                    "Remplacer la base de données SQLite"
                ],
                "correct_index": 0,
                "explanation": "Les sondes de santé (*Healthchecks*) permettent à l'infrastructure de redémarrer automatiquement un conteneur bloqué (`live`) ou de ne lui envoyer du trafic que lorsque la base de données est joignable (`ready`)."
            },
            {
                "id": "q5-3",
                "question": "Pourquoi ne doit-on jamais utiliser `uvicorn --reload` en production, et par quelle architecture le remplace-t-on ?",
                "options": [
                    "Le mode --reload surveille le disque et n'utilise qu'un seul processus ; en production, on utilise plusieurs workers ASGI Uvicorn (ou Gunicorn avec UvicornWorker) placés derrière un Reverse Proxy Nginx",
                    "Parce que --reload supprime les fichiers Python au bout de 24 heures",
                    "Parce que Uvicorn ne supporte pas le format JSON",
                    "En production, on ouvre les fichiers .py directement dans le navigateur sans serveur"
                ],
                "correct_index": 0,
                "explanation": "En production, **Nginx** gère le TLS/HTTPS et la protection réseau, puis transmet les requêtes aux **Workers ASGI Uvicorn** (`uvicorn app:app --workers 4` ou `gunicorn -k uvicorn.workers.UvicornWorker`), qui exécutent FastAPI en parallèle."
            },
            {
                "id": "q5-4",
                "question": "Quel est l'avantage d'utiliser `TestClient(app)` (de `fastapi.testclient`) pour tester ses routes FastAPI ?",
                "options": [
                    "Il simule des requêtes HTTP (GET, POST, PUT, DELETE) directement en mémoire via ASGI en quelques millisecondes sans avoir besoin de démarrer Uvicorn sur un port réseau",
                    "Il génère automatiquement l'interface graphique CSS",
                    "Il remplace Nginx en production",
                    "Il chiffre la base de données SQLite"
                ],
                "correct_index": 0,
                "explanation": "`TestClient(app)` (basé sur `httpx` et `ASGITransport`) permet d'automatiser la vérification de tous les cas nominaux (`200`, `201`) et de tous les cas d'erreur (`401`, `403`, `422`, `429`) à chaque modification du code."
            },
            {
                "id": "q5-5",
                "question": "Quelle est la différence exacte entre la spécification `OpenAPI 3.1` (`/openapi.json`) et `Swagger UI` (`/docs`) générés nativement par FastAPI ?",
                "options": [
                    "OpenAPI 3.1 est le contrat formel JSON généré automatiquement par FastAPI à partir des modèles Pydantic et des routes, tandis que Swagger UI (/docs) et ReDoc (/redoc) sont les portails Web interactifs qui lisent ce contrat",
                    "OpenAPI est un serveur de base de données SQL et Swagger UI est un pare-feu Linux",
                    "Swagger UI ne fonctionne qu'avec le langage Java",
                    "OpenAPI 3.1 interdit l'utilisation des jetons Bearer JWT"
                ],
                "correct_index": 0,
                "explanation": "Dans FastAPI, vous n'écrivez jamais le dictionnaire OpenAPI à la main : FastAPI inspecte vos `BaseModel` Pydantic, vos paramètres `Query`/`Path` et vos dépendances `HTTPBearer`/`APIKeyHeader` pour générer `/openapi.json`, `/docs` et `/redoc`."
            },
            {
                "id": "q5-6",
                "question": "Lorsqu'on déploie 4 instances FastAPI/Uvicorn (`127.0.0.1:8001` à `8004`) derrière un répartiteur de charge Nginx, comment Nginx traite-t-il les fichiers `/static/` et comment FastAPI récupère-t-il la vraie IP du client ?",
                "options": [
                    "Nginx sert directement /static/ depuis le disque via le noyau Linux (sendfile on) sans solliciter Python, et Uvicorn (--proxy-headers) / FastAPI lisent l'en-tête X-Forwarded-For injecté par Nginx",
                    "Nginx envoie chaque fichier CSS aux 4 instances FastAPI simultanément pour les fusionner",
                    "ProxyHeadersMiddleware sert à compiler les fichiers CSS en Python",
                    "Nginx ne peut répartir la charge qu'entre 2 instances maximum"
                ],
                "correct_index": 0,
                "explanation": "Grâce à `location /static/ { alias ...; sendfile on; }`, Nginx décharge à 100 % Python des fichiers statiques. Et pour les routes dynamiques (`proxy_pass http://isgp_fastapi_cluster`), `X-Forwarded-For` et `X-Forwarded-Proto` restituent la vraie IP cliente et le schéma HTTPS."
            },
            {
                "id": "q5-7",
                "question": "Pourquoi voit-on presque toujours `/api/v1` pendant des années dans les grandes APIs mondiales, et dans quel cas précis doit-on créer un second `APIRouter` `/api/v2` ?",
                "options": [
                    "Parce que 90 % des évolutions (ajouter un champ optionnel dans un modèle Pydantic ou une nouvelle route) sont rétrocompatibles (Non-Breaking) et restent dans /api/v1 ; on ne crée /api/v2 qu'en cas de Rupture de Contrat (Breaking Change)",
                    "Parce que le protocole HTTP interdit d'utiliser des chiffres supérieurs à 1 dans une URL",
                    "Parce qu'il faut créer une nouvelle version (/api/v2, /api/v3...) chaque fois que l'on corrige un bug SQL",
                    "Parce que FastAPI ne peut inclure qu'un seul APIRouter à la fois"
                ],
                "correct_index": 0,
                "explanation": "Selon la Loi de Postel (*Tolerant Reader*), les clients existants ignorent les nouveaux champs JSON qu'ils ne connaissent pas (`v1` évolue donc sans casser). En revanche, changer `duree: 5` en `duree: {'valeur': 5}` est un *Breaking Change* qui impose d'inclure un second `APIRouter(prefix='/api/v2/formations')`."
            },
            {
                "id": "q5-8",
                "question": "Lorsqu'on déploie `/api/v2/formations` en production, comment gère-t-on `/api/v1/formations` selon la norme IETF RFC 8594 ?",
                "options": [
                    "On maintient router_v1 et router_v2 en parallèle pendant une période de transition, en injectant sur /api/v1 les en-têtes HTTP 'Deprecation: true', 'Sunset: <Date>' et 'Link: rel=\"successor-version\"' avant de renvoyer '410 Gone' après la date Sunset",
                    "On supprime immédiatement /api/v1 le jour même de la sortie de /api/v2 sans prévenir les clients",
                    "On redirige toutes les requêtes /api/v1 avec un code 500 Internal Server Error",
                    "On renomme la base de données SQLite en v2.db"
                ],
                "correct_index": 0,
                "explanation": "La coexistence de deux routeurs (`router_v1` et `router_v2`) accompagnée des en-têtes `Deprecation` et `Sunset` (RFC 8594) laisse aux applications mobiles et partenaires le temps de migrer vers `v2` sans interruption de service."
            }
        ]
    }
}
