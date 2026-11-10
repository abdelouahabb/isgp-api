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
                "text": "Les débutants confondent souvent quatre concepts pourtant très différents :\n1. **Encodage (Base64 / UTF-8)** : Traduire des données dans un alphabet transportable. **Aucune sécurité** : n'importe qui peut décoder du Base64 instantanément sans clé.\n2. **Hachage (SHA-256, Scrypt, Bcrypt)** : Empreinte à **sens unique** (irréversible). Utilisé pour stocker les mots de passe en base : on ne stocke jamais un mot de passe en clair, seulement son empreinte hachée avec un sel (`salt`).\n3. **Chiffrement (AES, TLS/HTTPS)** : Rendre un message illisible sauf pour celui qui possède la clé de déchiffrement (réversible avec clé).\n4. **Signature Cryptographique (HMAC-SHA256)** : Attacher un sceau mathématique calculé avec une `SECRET_KEY` pour prouver que le message n'a pas été modifié en route."
            },
            "explanation": [
                "**Règle n°1 — Zéro secret dans le code source (Facteur III de Twelve-Factor App)** : Le code Python est partagé dans Git. On injecte toujours les secrets via les **variables d'environnement du système** (`os.environ.get('API_SECRET_KEY')`).",
                "**Règle n°2 — Ne jamais transmettre de secret dans l'URL (`?api_key=...`)** : Même en HTTPS, l'URL complète est enregistrée en clair dans les fichiers journaux (`access.log`) des proxys et serveurs web. Les secrets voyagent exclusivement dans les **en-têtes HTTP (`self.request.headers`)**.",
                "**Authentification Machine-à-Machine par `X-API-Key`** : Dans un `RequestHandler` Tornado, on lit `self.request.headers.get('X-API-Key', '')` et on compare cette clé avec `hmac.compare_digest(a, b)`.",
                "**Pourquoi `hmac.compare_digest` au lieu de `==` ? (Attaque Temporelle / Timing Attack)** : L'opérateur `==` s'arrête dès le premier caractère différent. `hmac.compare_digest` prend exactement le même temps quelle que soit la position de l'erreur."
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
                "text": "Une clé API fixe ne porte ni l'identité d'un utilisateur humain, ni son rôle, ni de date d'expiration. Avec un **Jeton Signé (Bearer Token / JWT)** :\n1. L'utilisateur présente son identifiant et son mot de passe une seule fois sur `POST /api/auth/token` (`AuthTokenHandler`).\n2. Le serveur Tornado fabrique un badge numérique contenant `{\"utilisateur\": \"stagiaire\", \"role\": \"participant\"}` + l'heure d'émission, et y appose une **signature mathématique HMAC**.\n3. À chaque requête suivante, le client présente ce jeton dans `Authorization: Bearer <token>`."
            },
            "explanation": [
                "**Structure interne d'un Jeton Signé (JWT / `itsdangerous`)** : Un jeton est constitué de segments séparés par des points `.` :\n  - **`Payload` (Charge utile encodée en Base64URL)** : Contient les revendications (*claims*) : identifiant (`sub`), rôle (`role`), horodatage d'émission (`iat`).\n  - **`Signature` (HMAC-SHA256)** : `HMAC_SHA256(Base64(Payload), SECRET_KEY)`.",
                "**Piège critique à connaître absolument — Un Token est SIGNÉ, mais PAS CHIFFRÉ !** : Le `Payload` est simplement encodé en Base64. N'importe qui interceptant le jeton peut lire le dictionnaire JSON qu'il contient ! Il ne faut donc **JAMAIS** mettre de mot de passe ou de donnée secrète à l'intérieur d'un Token. En revanche, personne ne peut **modifier** son contenu sans connaître la `SECRET_KEY` du serveur.",
                "**Vérification de l'expiration (`max_age=300`)** : Lors de l'appel à `signer.loads(token, max_age=300)`, le serveur vérifie d'abord la signature cryptographique (`BadSignature`), puis l'âge du jeton (`SignatureExpired`)."
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
                "text": "En gestion d'API (*API Management*), confondre **Authentification** et **Autorisation** est l'erreur d'architecture la plus fréquente :\n1. **L'Authentification (`AuthN` — *Authentication* — « Qui êtes-vous ? »)** : Vous présentez votre passeport au poste frontière. Si vous n'avez pas de passeport ou s'il est faux, vous êtes refoulé dès l'entrée : **`401 Unauthorized`**.\n2. **L'Autorisation (`AuthZ` — *Authorization* — « Qu'avez-vous le droit de faire ? »)** : Votre passeport est valide (vous êtes authentifié !), mais vous tentez d'entrer dans le cockpit avec un billet passager. L'agent sait qui vous êtes, mais votre profil ne vous donne pas ce droit : **`403 Forbidden`**."
            },
            "explanation": [
                "**1. Pourquoi HTTP `401` s'appelle-t-il *Unauthorized* alors qu'il désigne l'Authentification (`AuthN`) ?**\n  - **`401 Unauthorized` = Défaut d'Authentification (`AuthN`)** : L'identité de l'appelant est inconnue ou non prouvée.\n  - **`403 Forbidden` = Défaut d'Autorisation (`AuthZ`)** : L'authentification a **réussi**, mais les permissions sont insuffisantes.",
                "**2. Les 3 piliers de l'Autorisation (`AuthZ`) en API Management** :\n  - **Pilier A — `RBAC` (*Role-Based Access Control*)** : Droits accordés selon le rôle métier (`stagiaire`, `formateur`, `admin`).\n  - **Pilier B — `Scopes` / Permissions granulaires (Standard OAuth2)** : Liste explicite de permissions (`[\"formations:read\", \"formations:write\", \"audit:admin\"]`).\n  - **Pilier C — Contrôle de Propriété (*Object Ownership*) & Protection contre la faille `BOLA` (*Broken Object Level Authorization*)** : La faille n°1 mondiale du classement **OWASP API Security Top 10** ! Toujours vérifier `dossier.proprietaire == utilisateur_connecte` (ou `role == 'admin'`)."
            ],
            "code": _read("06_authn_vs_authz_scopes.py"),
            "line_explanations": [
                {"lines": "20-29", "text": "**Étape 1 (`AuthN`)** : Vérifie la présence, l'expiration et la signature du jeton. En cas d'échec, renvoie `401 Unauthorized`."},
                {"lines": "38-43", "text": "**Étape 2A (`AuthZ — RBAC`)** : Vérifie si le rôle du jeton correspond au `role_requis` (`403 Forbidden` sinon)."},
                {"lines": "45-50", "text": "**Étape 2B (`AuthZ — Scopes OAuth2`)** : Vérifie que la permission granulaire exigée (`scope_requis`) figure dans la liste `scopes` du jeton (`403` sinon)."},
                {"lines": "52-57", "text": "**Étape 2C (`AuthZ — Anti-BOLA`)** : Vérifie que l'utilisateur connecté est bien le propriétaire légitime de l'enregistrement demandé (`403` sinon)."}
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
                "text": "La solution industrielle standard (OAuth2 / OpenID Connect) repose sur un **couple de jetons** :\n- **`Access Token` (durée très courte : 5 à 15 min)** : envoyé à chaque appel d'API.\n- **`Refresh Token` (durée longue : 7 à 30 jours)** : stocké en lieu sûr et envoyé uniquement à la route `/api/auth/refresh` pour obtenir silencieusement un nouvel `Access Token` frais sans redemander le mot de passe !"
            },
            "explanation": [
                "**1. Factoriser la sécurité avec un décorateur `@exiger_role('admin')` sur les méthodes Tornado** : Dans un `RequestHandler` Tornado, le premier argument d'une méthode est `self`. Le décorateur `enveloppe(self, *args, **kwargs)` lit `self.request.headers`, vérifie le jeton, affecte **`self.current_user = utilisateur`** (la propriété standard de Tornado représentant l'utilisateur connecté !) et appelle la méthode cible.",
                "**2. Révocation de jeton (Blacklist / Déconnexion)** : Le serveur maintient en mémoire rapide (ou Redis) un ensemble (`set`) des jetons révoqués (`jetons_revoques`)."
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
                "text": "Le **Rate Limiting (Limitation de débit)** impose un quota strict par client (`self.request.remote_ip`, clé API ou utilisateur) et rejette immédiatement l'excédent avec `self.set_status(429)` (**`429 Too Many Requests`**)."
            },
            "explanation": [
                "**Les 3 algorithmes classiques de Rate Limiting** :\n  1. **Fenêtre Fixe (*Fixed Window*)** : Un compteur par minute calendaire.\n  2. **Fenêtre Glissante (*Sliding Window Log*)** : Le serveur conserve les horodatages exacts (`time.time()`) des requêtes récentes et purge ceux qui datent de plus de `N` secondes.\n  3. **Seau à Jetons (*Token Bucket*)** : Autorise de courts pics de trafic (*bursts*) tout en limitant la moyenne.",
                "**Les En-têtes HTTP standards de Rate Limiting (`self.set_header`)** :\n  - `X-RateLimit-Limit: 3`\n  - `X-RateLimit-Remaining: 1`\n  - `Retry-After: 20`"
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
                "text": "Un **Webhook** est une requête `POST` envoyée automatiquement par un partenaire externe (banque, passerelle de paiement) vers votre serveur dès qu'un événement survient.\nDans Tornado, on vérifie son authenticité en calculant le `HMAC-SHA256` sur `self.request.body`, on configure CORS dans `set_default_headers()` + `def options(self):`, et on plafonne la taille des requêtes avec `HTTPServer(app, max_body_size=...)`."
            },
            "explanation": [
                "**1. Authentifier un Webhook entrant par Signature `HMAC-SHA256` sur `self.request.body`** :\n  - Le partenaire signe les octets bruts du corps JSON avec `WEBHOOK_SECRET` et envoie `X-Webhook-Signature: sha256=...`.\n  - Votre `RequestHandler` Tornado recalcule le HMAC sur `self.request.body` et compare les deux signatures avec `hmac.compare_digest`.",
                "**2. Configurer CORS proprement dans Tornado (`set_default_headers` et `def options`)** :\n  - `set_default_headers(self)` inspecte `self.request.headers.get('Origin')` et n'ajoute `Access-Control-Allow-Origin` que si l'origine figure dans la liste blanche `ORIGINES_AUTORISEES`.\n  - `def options(self, *args, **kwargs):` répond `204 No Content` aux requêtes *Preflight* `OPTIONS` envoyées par les navigateurs avant un `POST`/`PUT`/`DELETE`.",
                "**3. Protection contre la saturation mémoire (`max_body_size`)** : En configurant `tornado.httpserver.HTTPServer(app, max_body_size=1 * 1024 * 1024)`, le serveur HTTP de Tornado rejette à la source tout flux dépassant 1 Mo avant qu'il ne sature la RAM."
            ],
            "code": _read("05_cors_webhooks_headers.py"),
            "line_explanations": [
                {"lines": "23-37", "text": "`SecureCorsBaseHandler` : applique la liste blanche CORS dans `set_default_headers()` et implémente `options()` (`204 No Content`)."},
                {"lines": "41-59", "text": "`WebhookPaiementHandler.post` : vérifie la signature `HMAC-SHA256` calculée sur `self.request.body`."},
                {"lines": "70", "text": "`HTTPServer(app, max_body_size=1 * 1024 * 1024)` plafonne la taille maximale du corps HTTP à 1 Mo."}
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
                "text": "Contrairement à d'autres frameworks qui nécessitent des bibliothèques externes pour signer leurs cookies, **Tornado intègre nativement depuis sa création un mécanisme cryptographique de cookies signés et horodatés (format v2 `2|1:0|timestamp|name|value|hmac_sha256`)**.\nIl suffit de déclarer `cookie_secret='...'` dans `tornado.web.Application` pour disposer de **`self.set_secure_cookie(...)`** et **`self.get_secure_cookie(...)`** !"
            },
            "explanation": [
                "**1. Anatomie d'un Cookie Signé Tornado (`self.set_secure_cookie` / `self.get_secure_cookie`)** :\n  - Lorsque vous appelez `self.set_secure_cookie('isgp_session', valeur, expires_days=1, httponly=True, samesite='Strict')`, Tornado génère une valeur au format :\n    `2|1:0|10:<timestamp>|12:isgp_session|84:<base64_payload>|<signature_hmac_sha256>`.\n  - Lors de la lecture avec `self.get_secure_cookie('isgp_session', max_age_days=1)`, Tornado vérifie la signature HMAC-SHA256 et le timestamp : si un seul bit a été modifié par le client ou si le cookie est expiré, `get_secure_cookie()` retourne automatiquement `None` !",
                "**2. Les 3 Drapeaux de Sécurité Obligatoires sur tout Cookie Sensible** :\n  - **`httponly=True` — Bouclier Anti-XSS** : Interdit à JavaScript (`document.cookie`) de lire le cookie.\n  - **`secure=True` — Bouclier Réseau TLS** : Transmet le cookie uniquement sur HTTPS.\n  - **`samesite='Strict'` ou `'Lax'` — Bouclier Anti-CSRF** : Empêche l'envoi inter-sites non sollicité.",
                "**3. Cookie Standard (`self.set_cookie` / `self.get_cookie`) vs Cookie Signé (`self.set_secure_cookie`)** :\n  - `self.set_cookie('isgp_theme', 'sombre')` écrit un cookie en clair (réservé aux préférences visuelles non sensibles).\n  - `self.clear_cookie('isgp_session', path='/')` révoque immédiatement le cookie en forçant une date d'expiration passée."
            ],
            "code": _read("07_cookies_et_sessions_securisees.py"),
            "line_explanations": [
                {"lines": "35-43", "text": "`self.set_secure_cookie('isgp_session', ...)` signe en HMAC-SHA256 avec `cookie_secret` et active `httponly=True` et `samesite='Strict'`."},
                {"lines": "60-66", "text": "`self.get_secure_cookie('isgp_session', max_age_days=1)` vérifie l'authenticité cryptographique et l'âge du cookie."},
                {"lines": "97-100", "text": "`self.clear_cookie(...)` révoque immédiatement les cookies côté navigateur."},
                {"lines": "104-113", "text": "Configuration de `cookie_secret=COOKIE_SECRET` dans `tornado.web.Application`."}
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
