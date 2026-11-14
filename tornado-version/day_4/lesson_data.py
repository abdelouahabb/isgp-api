import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_4_DATA = {
    "day_number": 4,
    "folder": "day_4",
    "badge": "Jour 4 • Secrets, Tokens, Cookies Signés Tornado & Rate Limit",
    "title": "Sécurité & Résilience des APIs Tornado : Secrets, Jetons Signés (JWT/Bearer), Refresh Tokens, RBAC, Cookies Signés (set_secure_cookie), Rate Limiting et Webhooks",
    "goal": "Maîtriser l'architecture de sécurité complète d'une API Tornado : distinguer encodage, hachage, chiffrement et signature HMAC ; isoler les secrets hors du code ; émettre et vérifier des Bearer Tokens ; implémenter le cycle Access/Refresh Token et le contrôle d'accès par rôle (RBAC : 401 vs 403) ; exploiter les cookies signés natifs de Tornado (cookie_secret & set_secure_cookie) ; protéger le serveur par Rate Limiting (429) et authentifier les Webhooks entrants.",
    "starter_filename": "day_4/02_bearer_tokens_signes.py",
    "files": [
        "day_4/01_secrets_et_api_key.py",
        "day_4/02_bearer_tokens_signes.py",
        "day_4/06_authn_vs_authz_scopes.py",
        "day_4/04_refresh_token_et_rbac.py",
        "day_4/03_rate_limiting_429.py",
        "day_4/05_cors_webhooks_headers.py",
        "day_4/07_cookies_et_sessions_securisees.py",
    ],
    "lessons": [
        {
            "id": "d4-l1",
            "file": "day_4/01_secrets_et_api_key.py",
            "title": "4.1 — Fondations Cryptographiques, Gestion des Secrets (`os.environ`) & Clés API (`X-API-Key` dans Tornado)",
            "duration": "60 min",
            "analogy": {
                "title": "Distinguer les 4 opérations fondamentales de sécurité informatique",
                "text": (
                    "En ingénierie de la sécurité, quatre transformations mathématiques obéissent à des objectifs totalement distincts et ne doivent jamais être substituées l'une à l'autre. "
                    "L'**encodage** (Base64, UTF-8) transpose simplement des octets dans un alphabet imprimable sans la moindre confidentialité, puisque quiconque peut inverser l'opération sans clé. "
                    "Le **hachage cryptographique lent** (PBKDF2, Scrypt, Argon2) projette un mot de passe additionné d'un sel aléatoire (`salt`) vers une empreinte irréversible à sens unique destinée au stockage en base.\n\n"
                    "Le **chiffrement** (AES-GCM, TLS 1.3) rend un flux illisible sur le réseau sauf pour le détenteur légitime de la clé de déchiffrement, tandis que la **signature cryptographique** (HMAC-SHA256) appose un sceau calculé avec une `SECRET_KEY` serveur garantissant au bit près que le message n'a subi aucune altération en transit."
                )
            },
            "explanation": [
                (
                    "**Externalisation stricte des secrets hors du dépôt Git (Facteur III de Twelve-Factor App).** "
                    "Un arbre de code source Python vocationnellement partagé entre développeurs et pipelines CI/CD ne doit contenir aucune clé cryptographique ni mot de passe en dur, car un secret commité demeure extractible à perpétuité via `git log -p`. "
                    "En production, le démon Tornado lit exclusivement ses clés sensibles depuis la mémoire d'environnement du processus système via `os.environ.get('API_SECRET_KEY')`."
                ),
                (
                    "**Bannissement des secrets dans l'URI au profit exclusif des en-têtes HTTP (`self.request.headers`).** "
                    "Même à l'intérieur d'un tunnel chiffré HTTPS, la ligne de requête complète (`GET /api/stats?api_key=...`) est consignée en clair dans les journaux `access.log` des répartiteurs Nginx, passerelles proxy et historiques clients. "
                    "Tout secret d'authentification voyage donc impérativement dans un en-tête dédié tel que `X-API-Key` ou `Authorization`."
                ),
                (
                    "**Authentification machine-à-machine par `X-API-Key` dans un `RequestHandler` Tornado.** "
                    "Pour identifier un serveur partenaire automatisé sans session humaine, le contrôleur extrait `self.request.headers.get('X-API-Key', '')` dès l'entrée de la requête et rejette immédiatement tout appel dépourvu de clé valide par `self.set_status(401)` avant d'exécuter la moindre requête métier."
                ),
                (
                    "**Neutralisation des attaques temporelles (*Timing Attacks*) par `hmac.compare_digest`.** "
                    "Comparer deux secrets avec l'opérateur Python `==` court-circuite l'évaluation dès le premier octet divergent, créant une fuite nanoseconde exploitable statistiquement pour deviner une clé caractère par caractère. "
                    "La primitive standard `hmac.compare_digest(recu, attendu)` inspecte intégralement tous les octets en temps constant, éliminant tout canal auxiliaire temporel."
                )
            ],
            "code": _read("01_secrets_et_api_key.py"),
            "line_explanations": [
                {"lines": "17-18", "text": "`os.environ.get(...)` lit les secrets depuis la mémoire du système d'exploitation."},
                {"lines": "24", "text": "`self.request.headers.get('X-API-Key', '')` extrait la clé transmise dans l'en-tête HTTP."},
                {"lines": "27-32", "text": "`hmac.compare_digest` vérifie l'égalité en temps constant et renvoie `self.set_status(401)` si la clé est absente ou erronée."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/admin-stats (X-API-Key)",
                "method": "GET",
                "url": "/api/sandbox/admin-stats",
                "headers": {"X-API-Key": "isgp-secret-2026"},
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_4/01_secrets_et_api_key.py` pour tester le contrôle X-API-Key en temps constant dans Tornado :",
                "initial_code": _read("01_secrets_et_api_key.py")
            },
            "vscode_instructions": {
                "filename": "day_4/01_secrets_et_api_key.py",
                "steps": [
                    "Ouvrir le fichier `day_4/01_secrets_et_api_key.py` dans l'éditeur.",
                    "Tester `GET /api/sandbox/admin-stats` avec puis sans l'en-tête `X-API-Key` dans le Client HTTP."
                ]
            }
        },
        {
            "id": "d4-l2",
            "file": "day_4/02_bearer_tokens_signes.py",
            "title": "4.2 — Anatomie des Jetons Signés (`Bearer Token` / JWT) : Émission, Signature HMAC & Expiration dans Tornado",
            "duration": "65 min",
            "analogy": {
                "title": "Le badge électronique temporaire infalsifiable",
                "text": (
                    "Une clé API statique ne transporte ni l'identité nominative d'un agent humain, ni son profil d'habilitation, ni d'échéance d'expiration automatique. "
                    "À l'inverse, le modèle du **Jeton Signé au Porteur (*Bearer Token* / JWT)** fonctionne comme un passeport biométrique temporaire délivré au guichet d'accueil.\n\n"
                    "L'utilisateur présente ses identifiants une unique fois à `POST /api/auth/token` (`AuthTokenHandler`) ; Tornado forge alors une charge utile `{\"utilisateur\": \"stagiaire\", \"role\": \"participant\"}` horodatée et scellée par une signature **HMAC-SHA256**, que le client glisse ensuite dans l'en-tête `Authorization: Bearer <token>` de chaque requête ultérieure."
                )
            },
            "explanation": [
                (
                    "**Architecture segmentée d'un jeton signé sans état (JWT RFC 7519 / `itsdangerous`).** "
                    "Un jeton signé concatène par des points `.` une charge utile JSON encodée en Base64URL portant les déclarations d'identité (*claims* : sujet `sub`, rôle `role`, instant d'émission `iat`), suivie d'un sceau d'intégrité calculé par `HMAC_SHA256(Base64URL(Payload), SECRET_KEY)` que n'importe quel nœud Tornado d'un cluster peut vérifier en mémoire vive sans interroger de table SQL de sessions."
                ),
                (
                    "**Distinction vitale entre intégrité et confidentialité : un jeton est signé, jamais chiffré.** "
                    "Parce que le `Payload` d'un JWT ou d'un jeton `URLSafeTimedSerializer` est simplement représenté en Base64URL, tout observateur détenant le jeton peut décoder et lire ses champs JSON instantanément sans clé : il est donc formellement interdit d'y loger un secret ou un mot de passe, tandis que la signature HMAC garantit en revanche qu'aucun attaquant ne peut promouvoir son `role` en `admin` sans invalider le sceau cryptographique."
                ),
                (
                    "**Validation conjointe de l'authenticité et de la fraîcheur temporelle (`max_age`).** "
                    "Lors de l'appel `signer.loads(token, max_age=300)` dans un `RequestHandler`, le vérificateur recalcule d'abord l'empreinte HMAC en temps constant (levant `BadSignature` à la moindre altération d'un bit), puis contrôle l'âge écoulé depuis l'horodatage signé afin de rejeter par `SignatureExpired` (`401 Unauthorized`) tout jeton ayant dépassé sa fenêtre de vie."
                )
            ],
            "code": _read("02_bearer_tokens_signes.py"),
            "line_explanations": [
                {"lines": "16-17", "text": "`URLSafeTimedSerializer(SECRET_KEY)` initialise le moteur de signature HMAC avec le secret du serveur."},
                {"lines": "21-35", "text": "`AuthTokenHandler.post` : décode `self.request.body` et émet le jeton signé `access_token`."},
                {"lines": "39-57", "text": "`ProfilProtegeHandler.get` : extrait `Authorization: Bearer <token>` et distingue un jeton expiré (`SignatureExpired`) d'un jeton falsifié (`BadSignature`)."}
            ],
            "sandbox_preset": {
                "label": "1. Émettre un Bearer Token : POST /api/sandbox/auth/token",
                "method": "POST",
                "url": "/api/sandbox/auth/token",
                "body": '{\n  "identifiant": "stagiaire",\n  "mot_de_passe": "isgp2026"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez `day_4/02_bearer_tokens_signes.py` pour émettre et vérifier un Bearer Token signé dans Tornado :",
                "initial_code": _read("02_bearer_tokens_signes.py")
            },
            "vscode_instructions": {
                "filename": "day_4/02_bearer_tokens_signes.py",
                "steps": [
                    "Ouvrir `day_4/02_bearer_tokens_signes.py` dans l'éditeur.",
                    "Tester `POST /api/sandbox/auth/token` puis appeler `GET /api/sandbox/auth/profil`."
                ]
            }
        },
        {
            "id": "d4-l3",
            "file": "day_4/06_authn_vs_authz_scopes.py",
            "title": "4.3 — Authentification (`AuthN` / `401`) vs Autorisation (`AuthZ` / `403`) : Rôles (`RBAC`), `Scopes` & Faille `BOLA`",
            "duration": "65 min",
            "analogy": {
                "title": "Le contrôle du passeport à l'entrée de l'aéroport (AuthN) vs La carte d'embarquement pour le cockpit (AuthZ)",
                "text": (
                    "En gouvernance d'API (*API Management*), confondre **Authentification (`AuthN`)** et **Autorisation (`AuthZ`)** engendre les brèches de sécurité les plus critiques recensées par l'OWASP. "
                    "L'**Authentification** répond exclusivement à la question « Qui êtes-vous ? » : comme au contrôle frontalier d'un aéroport, un voyageur dépourvu de passeport ou muni d'un titre expiré est refoulé dès la première barrière avec **`401 Unauthorized`**.\n\n"
                    "L'**Autorisation** intervient dans un second temps et répond à la question « Qu'avez-vous le droit d'accomplir ? » : votre passeport est authentique, mais présenter une carte d'embarquement passager pour tenter d'ouvrir la porte blindée du cockpit déclenche un refus définitif **`403 Forbidden`**."
                )
            },
            "explanation": [
                (
                    "**Sémantique normative RFC 9110 entre `401 Unauthorized` (`AuthN`) et `403 Forbidden` (`AuthZ`).** "
                    "Malgré sa dénomination historique trompeuse, le statut HTTP `401 Unauthorized` signale strictement un défaut d'**authentification** (preuve d'identité manquante, expirée ou falsifiée, invitant le client à se reconnecter), tandis que `403 Forbidden` atteste que le serveur a **parfaitement identifié** l'appelant mais lui interdit l'opération demandée faute d'habilitation suffisante."
                ),
                (
                    "**Défense en profondeur de l'Autorisation : RBAC, Scopes OAuth2 et propriété d'objet Anti-BOLA.** "
                    "Un contrôleur Tornado robuste superpose trois verrous d'autorisation complémentaires : le contrôle par rôle métier **RBAC** (`stagiaire`, `formateur`, `admin`), le filtrage par **Scopes OAuth2** délégués au jeton courant (`formations:read`, `audit:admin`), et surtout la vérification systématique de **propriété de l'enregistrement (`dossier['proprietaire'] == self.current_user['sub']`)** qui neutralise la vulnérabilité mondiale n°1 **OWASP API1:2023 (BOLA / IDOR)**."
                )
            ],
            "code": _read("06_authn_vs_authz_scopes.py"),
            "line_explanations": [
                {"lines": "28-38", "text": "**Étape 1 (`AuthN`)** : Vérifie la présence, l'expiration et la signature du jeton. En cas d'échec, renvoie `401 Unauthorized`."},
                {"lines": "47-52", "text": "**Étape 2A (`AuthZ — RBAC`)** : Vérifie si le rôle du jeton correspond au `role_requis` (`403 Forbidden` sinon)."},
                {"lines": "54-59", "text": "**Étape 2B (`AuthZ — Scopes OAuth2`)** : Vérifie que la permission granulaire exigée (`scope_requis`) figure dans la liste `scopes` du jeton (`403` sinon)."},
                {"lines": "61-66", "text": "**Étape 2C (`AuthZ — Anti-BOLA`)** : Vérifie que l'utilisateur connecté est bien le propriétaire légitime de l'enregistrement demandé (`403` sinon)."}
            ],
            "sandbox_preset": {
                "label": "Tester AuthN (401) vs AuthZ (403 / 200) : GET /api/sandbox/authz-demo",
                "method": "GET",
                "url": "/api/sandbox/authz-demo",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez les 5 scénarios illustrant l'Authentification (401) et les 3 niveaux d'Autorisation (403 RBAC, 403 Scope, 403 BOLA et 200 OK) :",
                "initial_code": _read("06_authn_vs_authz_scopes.py")
            },
            "vscode_instructions": {
                "filename": "day_4/06_authn_vs_authz_scopes.py",
                "steps": [
                    "Dans le Client HTTP, appelez `GET /api/sandbox/authz-demo` sans jeton -> observez `401 Unauthorized (Échec AuthN)`.",
                    "Cliquez sur « Générer & injecter un Token (stagiaire) » puis rappelez `GET /api/sandbox/authz-demo` -> observez `403 Forbidden (AuthN réussie, mais Échec AuthZ)`."
                ]
            }
        },
        {
            "id": "d4-l4",
            "file": "day_4/04_refresh_token_et_rbac.py",
            "title": "4.4 — Cycle Access / Refresh Token, Révocation (Blacklist) & Décorateur `@exiger_role` sur `RequestHandler`",
            "duration": "65 min",
            "analogy": {
                "title": "Pourquoi avoir deux jetons (Access Token court + Refresh Token long) ?",
                "text": (
                    "Concilier la rapidité d'une validation cryptographique sans état avec la capacité de révoquer instantanément un compte compromis repose en OAuth2 / OpenID Connect sur une **architecture asymétrique à double jeton**.\n\n"
                    "L'**`Access Token`** à durée de vie très brève (5 à 15 minutes) accompagne chaque appel métier à haute fréquence, tandis que le **`Refresh Token`** à longue validité (7 à 30 jours), signé avec un sel distinct, demeure confiné dans un coffre sécurisé et ne sert qu'à solliciter silencieusement un nouvel `Access Token` auprès de `/api/auth/refresh` après vérification d'une liste de révocation."
                )
            },
            "explanation": [
                (
                    "**Factorisation déclarative du contrôle d'accès par `@exiger_role` et `self.current_user`.** "
                    "Dans un `RequestHandler` Tornado, une usine à décorateurs enveloppant `def methode(self, *args, **kwargs):` inspecte `self.request.headers`, valide la signature avec `salt='access-token'`, peuple la propriété standard **`self.current_user`** de Tornado avec les revendications vérifiées et bloque tout rôle insuffisant en `403` sans polluer la logique métier."
                ),
                (
                    "**Révocation d'urgence par liste noire d'identifiants de jetons (`Token Blacklist`).** "
                    "Lors d'une déconnexion explicite ou d'une alerte de sécurité, l'empreinte ou l'identifiant unique `jti` du `Refresh Token` est inscrit dans un ensemble rapide en mémoire ou dans Redis (`jetons_revoques`), empêchant immédiatement toute régénération ultérieure d'`Access Token`."
                )
            ],
            "code": _read("04_refresh_token_et_rbac.py"),
            "line_explanations": [
                {"lines": "20-21", "text": "Utilisation de deux sels cryptographiques distincts (`salt='access-token'` vs `'refresh-token'`)."},
                {"lines": "28-64", "text": "Décorateur `@exiger_role(role_minimum)` pour méthodes `RequestHandler`, gérant `401` puis `403` et alimentant `self.current_user`."},
                {"lines": "68-80", "text": "`LoginHandler.post` : émet simultanément l'`access_token` (300s) et le `refresh_token` (7 jours)."},
                {"lines": "97-100", "text": "`AuditAdminHandler.get` : décorée par `@exiger_role('admin')`, lit directement `self.current_user['sub']`."}
            ],
            "python_runner": {
                "prompt": "Exécutez `day_4/04_refresh_token_et_rbac.py` pour observer le rejet 403 du stagiaire et l'accès 200 du directeur :",
                "initial_code": _read("04_refresh_token_et_rbac.py")
            },
            "vscode_instructions": {
                "filename": "day_4/04_refresh_token_et_rbac.py",
                "steps": [
                    "Ouvrir `day_4/04_refresh_token_et_rbac.py` dans l'éditeur.",
                    "Étudier comment `@exiger_role('admin')` renseigne `self.current_user` dans Tornado."
                ]
            }
        },
        {
            "id": "d4-l5",
            "file": "day_4/03_rate_limiting_429.py",
            "title": "4.5 — Ingénierie du Rate Limiting dans Tornado : Algorithmes, Quotas & En-têtes (`429 Too Many Requests`)",
            "duration": "60 min",
            "analogy": {
                "title": "Le disjoncteur qui protège l'Event-Loop Tornado contre les rafales abusives",
                "text": (
                    "Même dotée d'une cryptographie irréprochable, une boucle événementielle `IOLoop` exposée sans régulation de cadence peut être asphyxiée par une boucle infinie accidentelle chez un partenaire ou par une attaque de force brute automatisée.\n\n"
                    "Le **Rate Limiting (limitation de débit)** agit dès `prepare(self)` comme une vanne de régulation hydraulique : il comptabilise les requêtes par appelant (`self.request.remote_ip`, clé API ou sujet JWT) et rejette instantanément tout dépassement avec `self.set_status(429)` (**`429 Too Many Requests`**) avant d'atteindre la base SQL."
                )
            },
            "explanation": [
                (
                    "**Compromis algorithmiques entre Fenêtre Fixe, Fenêtre Glissante et Seau à Jetons.** "
                    "Là où un compteur en **fenêtre fixe** souffre d'un doublement de trafic aux frontières de minute, le **journal à fenêtre glissante (*Sliding Window Log*)** purge dynamiquement les horodatages antérieurs à `maintenant - fenetre` pour garantir un plafond mathématiquement exact, tandis que le **seau à jetons (*Token Bucket*)** absorbe de brèves rafales légitimes (*bursts*) tout en lissant le débit moyen."
                ),
                (
                    "**Signalisation contractuelle de la pression serveur via `X-RateLimit-*` et `Retry-After` (RFC 6585).** "
                    "À chaque réponse HTTP, l'injection via `self.set_header()` des compteurs `X-RateLimit-Limit` et `X-RateLimit-Remaining`, complétée en cas de blocage `429` par le délai exact en secondes `Retry-After`, permet aux SDK clients intelligents d'auto-réguler leur cadence sans aveuglement."
                )
            ],
            "code": _read("03_rate_limiting_429.py"),
            "line_explanations": [
                {"lines": "16-18", "text": "Définit la politique : maximum `3` requêtes sur une fenêtre glissante de `20` secondes par `self.request.remote_ip`."},
                {"lines": "26", "text": "Liste en compréhension filtrant uniquement les horodatages datant de moins de 20 secondes."},
                {"lines": "29-39", "text": "Si le quota est atteint (`>= 3`), appelle `self.set_status(429)` et renseigne `Retry-After`."},
                {"lines": "42-48", "text": "Enregistre l'horodatage courant et renseigne `X-RateLimit-Limit` et `X-RateLimit-Remaining`."}
            ],
            "sandbox_preset": {
                "label": "Tester le Rate Limiter (Cliquez 4 fois !) : GET /api/sandbox/ratelimit-demo",
                "method": "GET",
                "url": "/api/sandbox/ratelimit-demo",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_4/03_rate_limiting_429.py` pour envoyer une rafale de 4 requêtes sur Tornado et observer le code 429 :",
                "initial_code": _read("03_rate_limiting_429.py")
            },
            "vscode_instructions": {
                "filename": "day_4/03_rate_limiting_429.py",
                "steps": [
                    "Ouvrir `day_4/03_rate_limiting_429.py` dans l'éditeur.",
                    "Dans le Client HTTP, cliquer 4 fois de suite sur `GET /api/sandbox/ratelimit-demo`."
                ]
            }
        },
        {
            "id": "d4-l6",
            "file": "day_4/05_cors_webhooks_headers.py",
            "title": "4.6 — Sécurité Périmétrique Tornado : CORS (`set_default_headers` + `options`), Webhooks (`HMAC-SHA256`) & `max_body_size`",
            "duration": "55 min",
            "analogy": {
                "title": "L'API inversée (Webhook) et le contrôle des origines (CORS)",
                "text": (
                    "Plutôt que d'interroger frénétiquement un prestataire de paiement toutes les trois secondes, une architecture événementielle reçoit une notification asynchrone poussée directement par le partenaire vers votre serveur : c'est le patron **Webhook**.\n\n"
                    "Dans Tornado, sécuriser cette frontière périmétrique combine trois mécanismes natifs : la vérification `HMAC-SHA256` sur les octets bruts `self.request.body`, le filtrage des domaines navigateurs **CORS** via `set_default_headers()` et `def options(self):`, ainsi que le plafonnement mémoire amont `HTTPServer(app, max_body_size=...)`."
                )
            },
            "explanation": [
                (
                    "**Vérification cryptographique des Webhooks entrants sur les octets bruts `self.request.body`.** "
                    "Avant d'émettre sa notification `POST`, la passerelle partenaire signe la séquence exacte d'octets envoyée sur le câble avec `WEBHOOK_SECRET` dans `X-Webhook-Signature`. "
                    "Votre `RequestHandler` doit impérativement recalculer `hmac.new(..., self.request.body, hashlib.sha256)` avant tout décodage JSON et valider l'égalité via `hmac.compare_digest`, car re-sérialiser un dictionnaire modifierait les espaces et briserait l'empreinte."
                ),
                (
                    "**Implémentation d'une liste blanche CORS stricte dans `set_default_headers()` et `def options(self)`.** "
                    "Face à la politique de même origine (*Same-Origin Policy*) des navigateurs, `set_default_headers(self)` inspecte l'en-tête `Origin` entrant et n'émet `Access-Control-Allow-Origin` que pour les domaines explicitement homologués dans `ORIGINES_AUTORISEES`, tandis que `def options(self, *args, **kwargs):` acquitte les requêtes de pré-vérification (*Preflight*) par un statut `204 No Content`."
                ),
                (
                    "**Protection des tampons `IOStream` contre la saturation RAM via `max_body_size`.** "
                    "Instancier `tornado.httpserver.HTTPServer(app, max_body_size=1 * 1024 * 1024)` ordonne au moteur réseau bas niveau de Tornado de couper ou rejeter dès la lecture socket toute charge utile excédant 1 Mo (`413 Payload Too Large`), protégeant l'espace mémoire du démon avant même l'allocation d'un dictionnaire JSON."
                )
            ],
            "code": _read("05_cors_webhooks_headers.py"),
            "line_explanations": [
                {"lines": "23-38", "text": "`SecureCorsBaseHandler` : applique la liste blanche CORS dans `set_default_headers()` et implémente `options()` (`204 No Content`)."},
                {"lines": "41-60", "text": "`WebhookPaiementHandler.post` : vérifie la signature `HMAC-SHA256` calculée sur `self.request.body`."},
                {"lines": "90", "text": "`HTTPServer(app, max_body_size=1 * 1024 * 1024)` plafonne la taille maximale du corps HTTP à 1 Mo."}
            ],
            "python_runner": {
                "prompt": "Exécutez `day_4/05_cors_webhooks_headers.py` pour tester la vérification HMAC-SHA256 d'un Webhook et les en-têtes CORS dans Tornado :",
                "initial_code": _read("05_cors_webhooks_headers.py")
            },
            "vscode_instructions": {
                "filename": "day_4/05_cors_webhooks_headers.py",
                "steps": [
                    "Ouvrir `day_4/05_cors_webhooks_headers.py` dans l'éditeur.",
                    "Observer comment `self.request.body` fournit les octets bruts exacts pour calculer le HMAC-SHA256."
                ]
            }
        },
        {
            "id": "d4-l7",
            "file": "day_4/07_cookies_et_sessions_securisees.py",
            "title": "4.7 — Cookies Signés Natifs de Tornado (`cookie_secret`, `set_secure_cookie`, `get_secure_cookie`) & Drapeaux `HttpOnly`, `Secure`, `SameSite`",
            "duration": "65 min",
            "analogy": {
                "title": "La spécialité historique de Tornado : les cookies signés et horodatés nativement en HMAC-SHA256",
                "text": (
                    "Alors que la plupart des frameworks Web imposent l'installation d'extensions tierces pour authentifier leurs sessions côté client, **Tornado intègre nativement au cœur de `RequestHandler` depuis ses origines chez FriendFeed un moteur cryptographique de cookies signés et horodatés (format v2)**.\n\n"
                    "Dès lors qu'une clé `cookie_secret` haute entropie est déclarée dans `tornado.web.Application`, les primitives **`self.set_secure_cookie(...)`** et **`self.get_secure_cookie(...)`** scellent l'identité de l'utilisateur dans le coffre réseau isolé du navigateur."
                )
            },
            "explanation": [
                (
                    "**Structure cryptographique v2 de `set_secure_cookie` et `get_secure_cookie`.** "
                    "L'appel `self.set_secure_cookie('isgp_session', valeur, expires_days=1, httponly=True, samesite='Strict')` sérialise une enveloppe tramée `2|1:0|10:<timestamp>|12:isgp_session|84:<base64_payload>|<hmac_sha256>` liant ensemble le nom du cookie, l'instant d'émission et la charge utile. "
                    "À la réception, `self.get_secure_cookie('isgp_session', max_age_days=1)` recalcule le HMAC-SHA256 en temps constant et vérifie l'âge du jeton : la moindre falsification d'un octet dans l'inspecteur navigateur ou le dépassement du délai fait retourner silencieusement `None`."
                ),
                (
                    "**Triptyque défensif obligatoire sur tout cookie d'authentification (`HttpOnly`, `Secure`, `SameSite`).** "
                    "Activer simultanément `httponly=True` soustrait le cookie à l'API DOM `document.cookie` pour bloquer toute exfiltration par injection JavaScript **XSS**, `secure=True` interdit sa transmission hors d'un canal chiffré **HTTPS/TLS**, et `samesite='Strict'` (ou `'Lax'`) empêche le navigateur d'attacher automatiquement la session lors de requêtes forgées depuis un domaine tiers (**CSRF**)."
                ),
                (
                    "**Séparation d'usage entre préférences en clair (`set_cookie`) et révocation immédiate (`clear_cookie`).** "
                    "Les méthodes non signées `self.set_cookie('isgp_theme', 'sombre')` et `self.get_cookie()` demeurent strictement cantonnées aux réglages cosmétiques non privilégiés, tandis que `self.clear_cookie('isgp_session', path='/')` émet une directive `Set-Cookie` expirée dans le passé qui purge instantanément le coffre du navigateur lors de la déconnexion."
                )
            ],
            "code": _read("07_cookies_et_sessions_securisees.py"),
            "line_explanations": [
                {"lines": "35-44", "text": "`self.set_secure_cookie('isgp_session', ...)` signe en HMAC-SHA256 avec `cookie_secret` et active `httponly=True` et `samesite='Strict'`."},
                {"lines": "60-69", "text": "`self.get_secure_cookie('isgp_session', max_age_days=1)` vérifie l'authenticité cryptographique et l'âge du cookie."},
                {"lines": "97-102", "text": "`self.clear_cookie(...)` révoque immédiatement les cookies côté navigateur."},
                {"lines": "110-121", "text": "Configuration de `cookie_secret=COOKIE_SECRET` dans `tornado.web.Application`."}
            ],
            "sandbox_preset": {
                "label": "1. Émettre Cookies Sécurisés (HttpOnly + Session HMAC) : POST /api/sandbox/cookies/login",
                "method": "POST",
                "url": "/api/sandbox/cookies/login",
                "body": '{\n  "identifiant": "yasmine.merabet",\n  "theme": "sombre"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez `day_4/07_cookies_et_sessions_securisees.py` pour inspecter le format v2 du cookie signé Tornado (`set_secure_cookie`) :",
                "initial_code": _read("07_cookies_et_sessions_securisees.py")
            },
            "vscode_instructions": {
                "filename": "day_4/07_cookies_et_sessions_securisees.py",
                "steps": [
                    "Ouvrir `day_4/07_cookies_et_sessions_securisees.py` dans l'éditeur.",
                    "Observer l'en-tête `Set-Cookie: isgp_session=2|1:0|...` généré par `self.set_secure_cookie`."
                ]
            }
        }
    ]
}
