"""
Évaluations formatives approfondies (Jour 0 à Jour 5) — Volume III : Édition Tornado.
Chaque question contient une justification méthodique sans prérequis implicite.
"""

QUIZZES = {
    0: {
        "title": "Évaluation Jour 0 : Fondations Python, Exceptions & Décorateurs",
        "description": "Validation des structures de données Python, de l'accès défensif `.get()`, de la gestion d'exceptions `try/except` et du mécanisme des décorateurs `@`.",
        "questions": [
            {
                "id": "q0-1",
                "question": "Pourquoi préfère-t-on écrire `corps.get(\"duree_jours\", 5)` plutôt que `corps[\"duree_jours\"]` lors de la lecture d'un dictionnaire issu d'un client API ?",
                "options": [
                    "Parce que .get() renvoie la valeur par défaut (5) si la clé est absente, tandis que corps['duree_jours'] lève une exception KeyError qui provoque un crash HTTP 500",
                    "Parce que les crochets [ ] sont interdits en Python 3",
                    "Parce que .get() chiffre automatiquement la donnée",
                    "Il n'y a aucune différence de comportement"
                ],
                "correct_index": 0,
                "explanation": "Un client externe peut toujours omettre un champ JSON. L'accès direct par crochets `d['cle']` lève une exception fatale `KeyError`, alors que `d.get('cle', defaut)` permet une programmation défensive sûre."
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
                "question": "Quel est le rôle exact d'un décorateur `@mon_decorateur` placé au-dessus d'une méthode `def get(self):` d'un `RequestHandler` Tornado ?",
                "options": [
                    "Envelopper la méthode dans une fonction d'ordre supérieur pour exécuter du code avant ou après elle (vérification de Bearer Token, contrôle RBAC, chronométrage)",
                    "Transformer la méthode en commentaire ignoré par Python",
                    "Supprimer la méthode de la mémoire vive",
                    "Créer une table SQL portant le nom de la fonction"
                ],
                "correct_index": 0,
                "explanation": "La syntaxe `@mon_decorateur` est un sucre syntaxique pour `get = mon_decorateur(get)`. Elle permet de protéger des méthodes `RequestHandler` (`@exiger_role`, `@tornado.web.authenticated`)."
            },
            {
                "id": "q0-4",
                "question": "Dans une API Tornado, pourquoi intercepte-t-on `ValueError` avec `try / except` lors de la conversion `int(self.get_query_argument('page', '1'))` ?",
                "options": [
                    "Pour renvoyer proprement une erreur HTTP 400 Bad Request au client si celui-ci envoie ?page=abc au lieu de laisser le serveur planter en HTTP 500",
                    "Pour accélérer la vitesse du processeur",
                    "Parce que la fonction int() ne fonctionne qu'à l'intérieur d'un bloc try",
                    "Pour convertir automatiquement 'abc' en 100"
                ],
                "correct_index": 0,
                "explanation": "Une erreur causée par une entrée invalide du client doit toujours être capturée (`try/except`) et traduite en erreur `4xx` (`400` ou `422`), jamais en crash `500 Internal Server Error`."
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
                "explanation": "Selon la norme RFC 3986, la partie située après `?` est la **Query String** (lue dans Tornado via `self.get_query_argument('salle')`), tandis que `/v1/formations` est le **Path**."
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
                "question": "En Python/Tornado, quelle est la différence exacte entre `json.dumps(data)` et `tornado.escape.json_decode(body)` ?",
                "options": [
                    "json.dumps() sérialise un objet Python en chaîne JSON, tandis que json_decode() (ou json.loads()) désérialise des octets/chaîne JSON en objet Python (dict/list)",
                    "json.dumps() supprime les données et json_decode() les sauvegarde sur disque",
                    "json.dumps() lit un fichier SQLite",
                    "L'un est réservé à GET et l'autre à DELETE"
                ],
                "correct_index": 0,
                "explanation": "`dumps` (*dump string*) convertit `dict -> str JSON` ; `tornado.escape.json_decode(self.request.body)` (ou `json.loads`) convertit `bytes/str JSON -> dict`."
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
        "title": "Évaluation Jour 2 : Maturité REST, RequestHandler, Pagination & Hooks Tornado",
        "description": "Validation du nommage RESTful, de `RequestHandler`, du routage Regex, de la pagination Offset/Limit et des hooks `prepare` / `on_finish`.",
        "questions": [
            {
                "id": "q2-1",
                "question": "Selon les standards d'architecture REST (Niveau 2 de Richardson), comment doit-on concevoir l'endpoint permettant de supprimer la formation n°42 dans Tornado ?",
                "options": [
                    "Méthode def delete(self, id) sur l'URI nominale au pluriel : DELETE /api/formations/42",
                    "Méthode def get(self) sur l'URI : GET /api/supprimerFormation?id=42",
                    "Méthode def post(self) sur l'URI : POST /api/delete_formation_42",
                    "Méthode def put(self) sur l'URI : PUT /api/formations/42/erase"
                ],
                "correct_index": 0,
                "explanation": "En REST, l'URI désigne la ressource par un **nom au pluriel** (`/api/formations/42`) et la méthode HTTP (`DELETE` -> `def delete(self, id)`) exprime l'action à accomplir."
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
                "question": "À quoi sert l'en-tête `X-Request-ID` généré dans la méthode `prepare(self)` d'un `BaseHandler` Tornado ?",
                "options": [
                    "À attribuer un identifiant unique (UUID) à chaque requête pour corréler facilement la réponse reçue par le client avec les journaux d'audit écrits dans on_finish(self)",
                    "À remplacer le mot de passe de l'utilisateur",
                    "À compresser le corps JSON",
                    "À indiquer la version de Python installée"
                ],
                "correct_index": 0,
                "explanation": "Le `X-Request-ID` (ou *Correlation ID*) stocké dans `self.request_id` permet de retrouver instantanément la trace exacte d'une requête dans des millions de lignes de logs."
            },
            {
                "id": "q2-5",
                "question": "Quelle est la différence exacte entre `([0-9]+)`, `:id` et `{id}` lorsqu'on définit un paramètre dynamique de chemin ?",
                "options": [
                    "([0-9]+) (ou (?P<id>[0-9]+)) est la syntaxe de groupe de capture Regex du routeur Tornado, :id est la syntaxe de Postman et Express.js, et {id} est la syntaxe d'OpenAPI 3.0 / Swagger",
                    ":id est obligatoire dans tornado.web.Application",
                    "<int:id> est la seule syntaxe reconnue par Tornado",
                    "On doit écrire littéralement ([0-9]+) dans la commande curl"
                ],
                "correct_index": 0,
                "explanation": "Tornado route les URLs via des expressions régulières Python (`r'/api/formations/([0-9]+)'`) et passe chaque groupe capturé en paramètre à `def get(self, formation_id):`."
            },
            {
                "id": "q2-6",
                "question": "Lorsqu'un utilisateur soumet un formulaire HTML `<form method=\"POST\" action=\"/formations\">`, comment lit-on les champs dans Tornado et quelle est la particularité syntaxique de `tornado.template` ?",
                "options": [
                    "On lit les champs du formulaire avec self.get_body_argument('champ') (et self.request.files pour multipart/form-data), et les blocs {% for %} / {% if %} de tornado.template se ferment tous par {% end %}",
                    "Tornado ne supporte pas la méthode POST avec les formulaires HTML",
                    "Il faut utiliser self.get_query_argument() pour lire un corps POST",
                    "tornado.template bloque la méthode POST"
                ],
                "correct_index": 0,
                "explanation": "Un `<form method='POST'>` encode les champs `<input name='...'>` en `application/x-www-form-urlencoded`, que Tornado lit via `self.get_body_argument('nom_du_champ')`, tandis que `tornado.template` ferme ses blocs par `{% end %}`."
            }
        ]
    },
    3: {
        "title": "Évaluation Jour 3 : Validation RFC 7807, Idempotence, PUT vs PATCH & SQLite",
        "description": "Validation des codes 400 vs 422, de l'idempotence (`Idempotency-Key`), de `write_error` et des requêtes SQL paramétrées.",
        "questions": [
            {
                "id": "q3-1",
                "question": "Quelle est la différence précise entre les codes HTTP `400 Bad Request` et `422 Unprocessable Entity` ?",
                "options": [
                    "400 indique une erreur de syntaxe brute (JSON mal formé levant json.JSONDecodeError), tandis que 422 indique un JSON syntaxiquement valide mais violant les règles métier (ex: duree_jours = -5)",
                    "400 est une erreur serveur et 422 est un succès",
                    "422 signifie que le serveur est éteint",
                    "Il n'y a aucune différence"
                ],
                "correct_index": 0,
                "explanation": "`400` rejette une trame ou un JSON illisible par `tornado.escape.json_decode` ; `422` indique que le serveur a bien décodé le JSON mais que les valeurs des champs ne respectent pas le contrat métier."
            },
            {
                "id": "q3-2",
                "question": "Quelle est la différence entre les méthodes `def put(self, id)` et `def patch(self, id)` sur `/api/formations/1`, et pourquoi `POST` utilise-t-il `Idempotency-Key` ?",
                "options": [
                    "PUT remplace intégralement la ressource (idempotent), PATCH modifie partiellement les champs fournis, et Idempotency-Key empêche un POST répété de créer des doublons en cas de coupure réseau",
                    "PUT supprime la ressource et PATCH la crée",
                    "POST est naturellement idempotent sans en-tête",
                    "PATCH sert uniquement à lire des données comme GET"
                ],
                "correct_index": 0,
                "explanation": "`PUT` remplace l'état complet (idempotent). `PATCH` applique un delta partiel. Comme `POST` n'est pas idempotent, l'en-tête `Idempotency-Key` garantit qu'un réessai réseau ne duplique pas l'opération."
            },
            {
                "id": "q3-3",
                "question": "Pourquoi surcharge-t-on `write_error(self, status_code, **kwargs)` et configure-t-on `default_handler_class` dans une API Tornado ?",
                "options": [
                    "Pour garantir que l'API renvoie TOUJOURS du JSON structuré RFC 7807 (et jamais une page HTML d'erreur par défaut) même sur une URL inconnue (404), un verbe non supporté (405) ou une exception imprévue (500)",
                    "Pour désactiver toutes les vérifications de sécurité",
                    "Pour transformer toutes les erreurs 404 en 200 OK",
                    "Pour supprimer la base de données en cas d'erreur"
                ],
                "correct_index": 0,
                "explanation": "Par défaut, `RequestHandler.write_error` renvoie une page HTML `<html><title>404: Not Found</title>...`. Surcharger `write_error` et `default_handler_class` assure un contrat 100% JSON."
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
        "title": "Évaluation Jour 4 : Secrets, Tokens, Refresh/RBAC (401 vs 403), Rate Limit, Webhooks & Cookies Signés",
        "description": "Validation complète de l'architecture de sécurité dans Tornado : cryptographie, Bearer Tokens, RBAC, Rate Limiting, Webhooks HMAC et `set_secure_cookie`.",
        "questions": [
            {
                "id": "q4-1",
                "question": "Pourquoi ne faut-il JAMAIS stocker d'information confidentielle (ex: mot de passe ou numéro de carte) à l'intérieur du Payload d'un Bearer Token (JWT) ou d'un cookie signé ?",
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
                "question": "Dans un contrôle d'accès par rôle (RBAC), quelle est la distinction exacte entre `401 Unauthorized` et `403 Forbidden` ?",
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
                    "Parce que Tornado refuse les jetons de plus de 300 secondes",
                    "Pour doubler la taille des messages HTTP"
                ],
                "correct_index": 0,
                "explanation": "L'`Access Token` voyage sur chaque requête mais expire très vite (5 min). Le `Refresh Token` ne sort que rarement (uniquement vers `/api/auth/refresh`) et peut être révoqué en base."
            },
            {
                "id": "q4-4",
                "question": "Quel code HTTP et quels en-têtes une API Tornado renvoie-t-elle lorsqu'un client dépasse son quota de Rate Limiting dans `prepare(self)` ?",
                "options": [
                    "Statut 429 Too Many Requests avec les en-têtes X-RateLimit-Limit, X-RateLimit-Remaining: 0 et Retry-After (suivi de self.finish() pour couper le traitement)",
                    "Statut 403 Forbidden avec l'en-tête Content-Length",
                    "Statut 500 Internal Server Error",
                    "Statut 204 No Content"
                ],
                "correct_index": 0,
                "explanation": "Le code `429 Too Many Requests` accompagné de `Retry-After` (secondes à attendre) permet aux clients automatisés de mettre en pause leurs appels proprement."
            },
            {
                "id": "q4-5",
                "question": "Comment votre `RequestHandler` Tornado vérifie-t-il qu'un Webhook entrant (`POST /api/webhooks/paiement`) provient bien du partenaire bancaire et non d'un pirate ?",
                "options": [
                    "En recalculant l'empreinte HMAC-SHA256 sur les octets bruts du corps (self.request.body) avec le WEBHOOK_SECRET partagé et en la comparant en temps constant (hmac.compare_digest) à l'en-tête X-Webhook-Signature",
                    "En faisant confiance à tout message JSON contenant 'statut': 'paye'",
                    "En vérifiant uniquement l'en-tête User-Agent",
                    "En demandant à l'utilisateur de saisir son mot de passe"
                ],
                "correct_index": 0,
                "explanation": "La signature `HMAC-SHA256` calculée sur `self.request.body` avec un secret partagé garantit à la fois l'identité de l'émetteur du Webhook et l'intégrité du message."
            },
            {
                "id": "q4-6",
                "question": "En gestion d'API (API Management), qu'est-ce qu'une vulnérabilité BOLA (*Broken Object Level Authorization*, n°1 du Top 10 OWASP API) ?",
                "options": [
                    "Une faille d'Autorisation (AuthZ) où un utilisateur authentifié (ex: stagiaire #101) parvient à lire ou modifier les données d'un autre utilisateur (#102) simplement en changeant l'ID dans l'URL (/api/dossiers/102)",
                    "Une erreur de syntaxe dans un fichier JSON",
                    "Un problème de connexion au serveur DNS",
                    "Le fait d'utiliser le port 8888 en développement"
                ],
                "correct_index": 0,
                "explanation": "Vérifier uniquement que le jeton est valide (`AuthN`) ne suffit pas ! Le serveur doit impérativement vérifier l'**Autorisation au niveau de l'objet (`AuthZ`)** : `dossier.proprietaire == self.current_user['sub']`."
            },
            {
                "id": "q4-7",
                "question": "Pourquoi est-il recommandé de stocker un jeton de session Web dans un Cookie avec les drapeaux `HttpOnly`, `Secure` et `SameSite=Strict` plutôt que dans `window.localStorage` ?",
                "options": [
                    "Parce que le drapeau HttpOnly interdit toute lecture du cookie par JavaScript (document.cookie -> protection anti-XSS), Secure impose HTTPS, et SameSite=Strict bloque l'envoi inter-sites (protection anti-CSRF)",
                    "Parce que localStorage est limité à 2 caractères maximum",
                    "Parce que les cookies sont exécutés comme du code Python dans le navigateur",
                    "Parce que localStorage supprime automatiquement la base de données SQLite"
                ],
                "correct_index": 0,
                "explanation": "Contrairement à `localStorage` qui est lisible par n'importe quel script JavaScript injecté (faille XSS), un cookie `HttpOnly` est totalement isolé du DOM JavaScript et géré uniquement par la couche réseau HTTP du navigateur."
            },
            {
                "id": "q4-8",
                "question": "Quelle est la différence de sécurité entre un cookie ordinaire créé par `self.set_cookie('role', 'admin')` et un cookie signé créé par `self.set_secure_cookie('session', ...)` dans Tornado ?",
                "options": [
                    "Un cookie ordinaire est stocké en texte clair et peut être modifié librement par l'utilisateur dans son navigateur (F12), tandis que set_secure_cookie signe la valeur et l'horodatage par HMAC-SHA256 avec cookie_secret (toute altération fait que get_secure_cookie renvoie None)",
                    "Il n'y a aucune différence, les deux sont chiffrés par la carte graphique",
                    "self.set_cookie() ne fonctionne qu'avec Internet Explorer",
                    "self.set_secure_cookie() envoie un SMS à l'administrateur"
                ],
                "correct_index": 0,
                "explanation": "Un cookie non signé ne doit jamais servir à stocker une identité ou un rôle ! Seul `self.set_secure_cookie` (avec `cookie_secret` configuré sur `tornado.web.Application`) garantit que le client n'a pas modifié sa valeur."
            }
        ]
    },
    5: {
        "title": "Évaluation Jour 5 : Client Asynchrone Résilient, Routage Modulaire, Tests & Production Tornado",
        "description": "Validation d'`AsyncHTTPClient` avec Timeouts, de l'architecture modulaire, des sondes Healthcheck, d'`AsyncHTTPTestCase` et du déploiement multi-instances `HTTPServer(xheaders=True)` derrière Nginx.",
        "questions": [
            {
                "id": "q5-1",
                "question": "Pourquoi un serveur Tornado doit-il privilégier `AsyncHTTPClient` avec un paramètre `request_timeout` explicite lors d'un appel vers une API externe ?",
                "options": [
                    "Pour ne pas bloquer l'Event-Loop (IOLoop) pendant l'attente réseau et éviter que le serveur ne reste figé indéfiniment si le partenaire distant ne répond plus (Cascading Failure)",
                    "Pour compresser automatiquement la réponse JSON",
                    "Parce que Python refuse d'exécuter une requête sans timeout",
                    "Pour contourner le Rate Limiting du serveur distant"
                ],
                "correct_index": 0,
                "explanation": "Sur l'`IOLoop` asynchrone de Tornado, `await AsyncHTTPClient().fetch(req)` libère la boucle d'événements pour traiter les autres clients en parallèle, et `request_timeout` protège contre les connexions pendantes."
            },
            {
                "id": "q5-2",
                "question": "Quel est le rôle des routes `/api/health/live` (*Liveness*) et `/api/health/ready` (*Readiness*) dans une architecture de production ?",
                "options": [
                    "Permettre aux répartiteurs de charge (Nginx / Load Balancers / Kubernetes) de vérifier automatiquement si le processus Tornado répond (live) et si ses dépendances comme la base de données sont prêtes (ready)",
                    "Afficher la liste des mots de passe des administrateurs",
                    "Générer des Bearer Tokens pour les stagiaires",
                    "Remplacer la base de données SQLite"
                ],
                "correct_index": 0,
                "explanation": "Les sondes de santé (*Healthchecks*) permettent à l'infrastructure de redémarrer automatiquement un conteneur bloqué (`live`) ou de ne lui envoyer du trafic que lorsque la base de données est joignable (`ready`)."
            },
            {
                "id": "q5-3",
                "question": "Comment déploie-t-on une API Tornado en production pour exploiter tous les cœurs CPU et sécuriser le trafic HTTPS ?",
                "options": [
                    "En exécutant plusieurs instances de processus Tornado (ex: ports 8001 à 8004 avec HTTPServer(app, xheaders=True) et debug=False) placées derrière un Reverse Proxy Nginx qui gère le TLS/HTTPS et la répartition de charge",
                    "En activant debug=True sur Internet sans Reverse Proxy",
                    "En ouvrant les fichiers .py directement dans le navigateur sans serveur",
                    "Tornado ne peut gérer qu'un seul client à la fois"
                ],
                "correct_index": 0,
                "explanation": "En production, **Nginx** gère le TLS/HTTPS et les fichiers statiques, puis répartit les requêtes (`upstream`) vers plusieurs processus **Tornado (`HTTPServer`)** tournant chacun sur un cœur CPU avec sa propre `IOLoop`."
            },
            {
                "id": "q5-4",
                "question": "Quel est l'avantage d'utiliser `tornado.testing.AsyncHTTPTestCase` et `self.fetch()` pour tester ses `RequestHandlers` Tornado ?",
                "options": [
                    "Il démarre automatiquement l'Application Tornado sur un port éphémère isolé et exécute des requêtes HTTP (GET, POST, PUT, DELETE) en quelques millisecondes sur une IOLoop de test dédiée",
                    "Il génère automatiquement l'interface graphique CSS",
                    "Il remplace Nginx en production",
                    "Il chiffre la base de données SQLite"
                ],
                "correct_index": 0,
                "explanation": "`AsyncHTTPTestCase` permet d'automatiser la vérification de tous les cas nominaux (`200`, `201`) et de tous les cas d'erreur (`401`, `403`, `422`, `429`) à chaque modification du code."
            },
            {
                "id": "q5-5",
                "question": "Quelle est la différence exacte entre la spécification `OpenAPI 3.0` (`/api/openapi.json`) et `Swagger UI` (`/api/docs`) ?",
                "options": [
                    "OpenAPI 3.0 est le contrat formel normalisé (JSON/YAML) décrivant les routes, schémas et sécurités de l'API, tandis que Swagger UI est le portail Web interactif qui lit ce contrat pour offrir les boutons 'Authorize' et 'Try it out'",
                    "OpenAPI est un serveur de base de données SQL et Swagger UI est un pare-feu Linux",
                    "Swagger UI ne fonctionne qu'avec le langage Java",
                    "OpenAPI 3.0 interdit l'utilisation des jetons Bearer JWT"
                ],
                "correct_index": 0,
                "explanation": "Le document `openapi.json` est la source de vérité machine-lisible (utilisable par Swagger UI, Postman et les générateurs de code), et Swagger UI en est la visualisation interactive dans le navigateur."
            },
            {
                "id": "q5-6",
                "question": "Lorsqu'on déploie 4 instances Tornado (`127.0.0.1:8001` à `8004`) derrière un répartiteur de charge Nginx, comment Nginx traite-t-il les fichiers `/static/` et pourquoi active-t-on `xheaders=True` sur `tornado.httpserver.HTTPServer` ?",
                "options": [
                    "Nginx sert directement /static/ depuis le disque via le noyau Linux (sendfile on) sans solliciter Python, et xheaders=True permet à Tornado de peupler self.request.remote_ip avec la vraie IP du client issue de X-Forwarded-For au lieu de 127.0.0.1",
                    "Nginx envoie chaque fichier CSS aux 4 instances Tornado simultanément pour les fusionner",
                    "xheaders=True sert à compiler les fichiers CSS en Python",
                    "Nginx ne peut répartir la charge qu'entre 2 instances maximum"
                ],
                "correct_index": 0,
                "explanation": "Grâce à `location /static/ { alias ...; sendfile on; }`, Nginx décharge à 100 % Python des fichiers statiques. Et pour les routes dynamiques (`proxy_pass http://isgp_tornado_cluster`), `HTTPServer(app, xheaders=True)` restitue la vraie IP cliente (`self.request.remote_ip`) et le protocole (`self.request.protocol`)."
            },
            {
                "id": "q5-7",
                "question": "Pourquoi voit-on presque toujours `/api/v1` pendant des années dans les grandes APIs mondiales, et dans quel cas précis doit-on créer `/api/v2` ?",
                "options": [
                    "Parce que 90 % des évolutions (ajouter un champ JSON optionnel ou une nouvelle route) sont rétrocompatibles (Non-Breaking) et restent dans /api/v1 ; on ne crée /api/v2 qu'en cas de Rupture de Contrat (Breaking Change : suppression/renommage de clé ou changement de type)",
                    "Parce que le protocole HTTP interdit d'utiliser des chiffres supérieurs à 1 dans une URL",
                    "Parce qu'il faut créer une nouvelle version (/api/v2, /api/v3...) chaque fois que l'on corrige un bug SQL",
                    "Parce que Tornado ne peut enregistrer qu'une seule route à la fois"
                ],
                "correct_index": 0,
                "explanation": "Selon la Loi de Postel (*Tolerant Reader*), les clients existants ignorent les nouveaux champs JSON qu'ils ne connaissent pas (`v1` évolue donc sans casser). En revanche, changer `duree: 5` en `duree: {'valeur': 5}` est un *Breaking Change* qui impose de monter une sous-table `/api/v2`."
            },
            {
                "id": "q5-8",
                "question": "Lorsqu'on déploie `/api/v2/formations` en production, comment gère-t-on `/api/v1/formations` selon la norme IETF RFC 8594 ?",
                "options": [
                    "On maintient /api/v1 et /api/v2 en parallèle pendant une période de transition, en injectant sur /api/v1 les en-têtes HTTP 'Deprecation: true', 'Sunset: <Date>' et 'Link: rel=\"successor-version\"' avant de renvoyer '410 Gone' après la date Sunset",
                    "On supprime immédiatement /api/v1 le jour même de la sortie de /api/v2 sans prévenir les clients",
                    "On redirige toutes les requêtes /api/v1 avec un code 500 Internal Server Error",
                    "On renomme la base de données SQLite en v2.db"
                ],
                "correct_index": 0,
                "explanation": "La coexistence de deux sous-tables de routage (`v1` et `v2`) accompagnée des en-têtes `Deprecation` et `Sunset` (RFC 8594) laisse aux applications mobiles et partenaires le temps de migrer vers `v2` sans interruption de service."
            }
        ]
    }
}
