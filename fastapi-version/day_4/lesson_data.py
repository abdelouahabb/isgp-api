import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_4_DATA = {
    "day_number": 4,
    "folder": "day_4",
    "badge": "Jour 4 • Secrets, Tokens, Depends(RBAC) & Rate Limit",
    "title": "Sécurité & Résilience des APIs FastAPI : Secrets, Jetons Signés (HTTPBearer), Refresh Tokens, Depends(RBAC), Rate Limiting, CORSMiddleware & Cookies",
    "goal": "Maîtriser l'architecture de sécurité complète d'une API FastAPI : distinguer encodage, hachage, chiffrement et signature HMAC ; protéger les routes avec Header(alias='X-API-Key') et Depends() ; émettre et vérifier des Bearer Tokens ; implémenter le cycle Access/Refresh Token et le contrôle d'accès par rôle via Depends(exiger_role('admin')) ; protéger le serveur par Rate Limiting (429), CORSMiddleware, Webhooks HMAC (await request.body()) et Cookies HttpOnly.",
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
            "title": "4.1 — Fondations Cryptographiques, Gestion des Secrets (`os.environ`) & Clés API (`Header(alias='X-API-Key')` + `Depends`)",
            "duration": "60 min",
            "analogy": {
                "title": "Distinguer les 4 opérations fondamentales de sécurité informatique",
                "text": "Les débutants confondent souvent quatre concepts pourtant très différents :\n1. **Encodage (Base64 / UTF-8)** : Traduire des données dans un alphabet transportable. **Aucune sécurité** : n'importe qui peut décoder du Base64 instantanément sans clé.\n2. **Hachage (SHA-256, Scrypt, Bcrypt)** : Empreinte à **sens unique** (irréversible). Utilisé pour stocker les mots de passe en base : on ne stocke jamais un mot de passe en clair, seulement son empreinte hachée avec un sel (`salt`).\n3. **Chiffrement (AES, TLS/HTTPS)** : Rendre un message illisible sauf pour celui qui possède la clé de déchiffrement (réversible avec clé).\n4. **Signature Cryptographique (HMAC-SHA256)** : Attacher un sceau mathématique calculé avec une `SECRET_KEY` pour prouver que le message n'a pas été modifié en route."
            },
            "explanation": [
                "**Règle n°1 — Zéro secret dans le code source (Facteur III de Twelve-Factor App)** : Le code Python est partagé dans Git. Si vous écrivez `SECRET_KEY = 'mon-secret'` dans un fichier `.py`, toute personne ayant accès au dépôt Git possède les clés de production. On injecte toujours les secrets via les **variables d'environnement du système** (`os.environ.get('API_SECRET_KEY')`).",
                "**Règle n°2 — Ne jamais transmettre de secret dans l'URL (`?api_key=...`)** : Même en HTTPS, l'URL complète est enregistrée en clair dans les fichiers journaux (`access.log`) des proxys, pare-feux, serveurs web et dans l'historique du navigateur. Les secrets voyagent exclusivement dans les **en-têtes HTTP (`Headers`)**.",
                "**Authentification Machine-à-Machine dans FastAPI via `Header(alias='X-API-Key')` et `Depends()`** : Dans FastAPI, on crée une dépendance `verifier_cle_api(x_api_key: Optional[str] = Header(default=None, alias='X-API-Key'))` qui compare la clé avec `hmac.compare_digest(a, b)` et lève `HTTPException(status_code=401)` en cas d'échec.",
                "**Pourquoi `hmac.compare_digest` au lieu de `==` ? (Attaque Temporelle / Timing Attack)** : L'opérateur `==` compare les caractères un par un et s'arrête dès la première différence (en quelques nanosecondes). `hmac.compare_digest` prend exactement le même temps quelle que soit la position de l'erreur."
            ],
            "code": _read("01_secrets_et_api_key.py"),
            "line_explanations": [
                {"lines": "15-16", "text": "`os.environ.get(...)` lit les secrets depuis la mémoire du système d'exploitation."},
                {"lines": "20-28", "text": "Dépendance FastAPI `verifier_cle_api` extrayant `Header(default=None, alias='X-API-Key')` et vérifiant l'égalité en temps constant avec `hmac.compare_digest`."},
                {"lines": "31-36", "text": "Route `@app.get('/api/admin/statistiques')` protégée déclarativement par `_cle: str = Depends(verifier_cle_api)`."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/admin-stats (X-API-Key)",
                "method": "GET",
                "url": "/api/sandbox/admin-stats",
                "headers": {"X-API-Key": "isgp-secret-2026"},
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_4/01_secrets_et_api_key.py` pour tester la protection `Header(alias='X-API-Key')` + `Depends()` :",
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
            "title": "4.2 — Anatomie des Jetons Signés (`Bearer Token` / JWT) : Émission, Signature HMAC, `HTTPBearer` & Expiration",
            "duration": "65 min",
            "analogy": {
                "title": "Le badge électronique temporaire infalsifiable",
                "text": "Une clé API fixe ne porte ni l'identité d'un utilisateur humain, ni son rôle, ni de date d'expiration. Avec un **Jeton Signé (Bearer Token / JWT)** :\n1. L'utilisateur présente son identifiant et son mot de passe une seule fois sur `POST /api/auth/token`.\n2. Le serveur fabrique un badge numérique contenant `{\"utilisateur\": \"stagiaire\", \"role\": \"participant\"}` + l'heure d'émission, et y appose une **signature mathématique HMAC** calculée avec sa `SECRET_KEY`.\n3. À chaque requête suivante, le client présente ce jeton dans l'en-tête `Authorization: Bearer <token>`, injecté dans la route FastAPI via `Depends(extraire_utilisateur_token)` !"
            },
            "explanation": [
                "**Structure interne d'un Jeton Signé (JWT / `itsdangerous`)** : Un jeton est constitué de segments séparés par des points `.` :\n  - **`Payload` (Charge utile encodée en Base64URL)** : Contient les revendications (*claims*) : identifiant (`sub`), rôle (`role`), horodatage d'émission (`iat`).\n  - **`Signature` (HMAC-SHA256)** : `HMAC_SHA256(Base64(Payload), SECRET_KEY)`.",
                "**Piège critique à connaître absolument — Un Token est SIGNÉ, mais PAS CHIFFRÉ !** : Le `Payload` d'un JWT ou d'un jeton `itsdangerous` est simplement encodé en Base64. N'importe qui interceptant le jeton peut lire le dictionnaire JSON qu'il contient ! Il ne faut donc **JAMAIS** mettre de mot de passe ou de donnée secrète à l'intérieur d'un Token. En revanche, personne ne peut **modifier** son contenu sans connaître la `SECRET_KEY` du serveur.",
                "**Vérification par dépendance FastAPI (`Depends`) et `max_age=300`** : Lors de l'appel à `signer.loads(token, max_age=300)`, la dépendance vérifie la signature cryptographique (`BadSignature`) et l'expiration (`SignatureExpired`), et lève `HTTPException(status_code=401)` en cas d'anomalie."
            ],
            "code": _read("02_bearer_tokens_signes.py"),
            "line_explanations": [
                {"lines": "14-17", "text": "Initialisation de `FastAPI`, `URLSafeTimedSerializer(SECRET_KEY)` et `HTTPBearer()`."},
                {"lines": "25-36", "text": "Route `@app.post('/api/auth/token')` validant `ConnexionPayload` et signant la charge utile avec `signer.dumps(...)`."},
                {"lines": "40-52", "text": "Dépendance `extraire_utilisateur_token` vérifiant l'en-tête `Authorization: Bearer <token>`, l'expiration (`SignatureExpired`) et l'intégrité (`BadSignature`)."},
                {"lines": "56-58", "text": "Route protégée `@app.get('/api/auth/profil')` recevant directement `donnees_utilisateur: dict = Depends(extraire_utilisateur_token)`."}
            ],
            "sandbox_preset": {
                "label": "1. Émettre un Bearer Token : POST /api/sandbox/auth/token",
                "method": "POST",
                "url": "/api/sandbox/auth/token",
                "body": '{\n  "identifiant": "stagiaire",\n  "mot_de_passe": "isgp2026"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez `day_4/02_bearer_tokens_signes.py` pour tester l'émission et la vérification d'un Bearer Token dans FastAPI :",
                "initial_code": _read("02_bearer_tokens_signes.py")
            },
            "vscode_instructions": {
                "filename": "day_4/02_bearer_tokens_signes.py",
                "steps": [
                    "Ouvrir `day_4/02_bearer_tokens_signes.py` dans l'éditeur.",
                    "Tester d'abord `POST /api/sandbox/auth/token` puis utiliser le bouton d'injection automatique du Bearer Token dans le Client HTTP pour appeler `GET /api/sandbox/auth/profil`."
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
                "text": "En gestion d'API (*API Management*), confondre **Authentification** et **Autorisation** est l'erreur d'architecture la plus fréquente :\n1. **L'Authentification (`AuthN` — *Authentication* — « Qui êtes-vous ? »)** : Vous présentez votre passeport au poste frontière. La police vérifie que le document est authentique et non expiré. Si vous n'avez pas de passeport ou s'il est faux, vous êtes refoulé dès l'entrée : **`401 Unauthorized`**.\n2. **L'Autorisation (`AuthZ` — *Authorization* — « Qu'avez-vous le droit de faire ? »)** : Votre passeport est valide (vous êtes authentifié !), mais vous tentez d'entrer dans la tour de contrôle ou dans le cockpit de l'avion avec un billet passager économique. L'agent sait parfaitement qui vous êtes, mais votre profil ne vous donne pas ce droit : **`403 Forbidden`**."
            },
            "explanation": [
                "**1. Pourquoi HTTP `401` s'appelle-t-il *Unauthorized* alors qu'il désigne l'Authentification (`AuthN`) ?** C'est une subtilité historique de la norme RFC 9110 :\n  - **`401 Unauthorized` = Défaut d'Authentification (`AuthN`)** : L'identité de l'appelant est inconnue (aucun jeton fourni, `X-API-Key` erronée, signature HMAC invalide ou jeton expiré).\n  - **`403 Forbidden` = Défaut d'Autorisation (`AuthZ`)** : L'authentification a **réussi** (le serveur connaît l'identité exacte de l'utilisateur), mais ses permissions sont insuffisantes.",
                "**2. Les 3 piliers de l'Autorisation (`AuthZ`) en API Management** :\n  - **Pilier A — `RBAC` (*Role-Based Access Control*)** : Droits accordés selon le rôle métier de l'utilisateur (`stagiaire`, `formateur`, `admin`).\n  - **Pilier B — `Scopes` / Permissions granulaires (Standard OAuth2)** : Un jeton d'accès contient une liste explicite de permissions (`scopes`: `[\"formations:read\", \"dossiers:read\"]`).\n  - **Pilier C — Contrôle de Propriété (*Object Ownership*) & Protection contre la faille `BOLA` (*Broken Object Level Authorization*)** : La faille n°1 mondiale du classement **OWASP API Security Top 10** ! Même si `amine` est authentifié (`AuthN` OK) et possède le scope `dossiers:read`, il ne doit **jamais** pouvoir consulter le dossier confidentiel de `sara` en changeant simplement l'ID dans l'URL (`GET /api/v1/dossiers/102`)."
            ],
            "code": _read("06_authn_vs_authz_scopes.py"),
            "line_explanations": [
                {"lines": "21-31", "text": "**Étape 1 (`AuthN`)** : Vérifie la présence, l'expiration et la signature du jeton. En cas d'échec, renvoie `401 Unauthorized`."},
                {"lines": "40-59", "text": "**Étape 2 (`AuthZ`)** : Vérifie successivement le rôle (`RBAC`), le `scope` OAuth2 et la propriété de l'objet (`Anti-BOLA`, `403 Forbidden` sinon)."},
                {"lines": "65-81", "text": "Route FastAPI `@app.get('/api/v1/dossiers/{dossier_id}')` appliquant le contrôle anti-BOLA avant de retourner le dossier."}
            ],
            "sandbox_preset": {
                "label": "Tester AuthN (401) vs AuthZ (403 / 200) : GET /api/sandbox/authz-demo",
                "method": "GET",
                "url": "/api/sandbox/authz-demo",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez les scénarios illustrant l'Authentification (401) et les 3 niveaux d'Autorisation (403 RBAC, 403 Scope, 403 BOLA et 200 OK) :",
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
            "title": "4.4 — Cycle Access / Refresh Token, Révocation (Blacklist) & Injection de Dépendance `Depends(exiger_role('admin'))`",
            "duration": "65 min",
            "analogy": {
                "title": "Pourquoi avoir deux jetons (Access Token court + Refresh Token long) ?",
                "text": "Si vous donnez à un utilisateur un jeton valable 30 jours et que ce jeton est volé, l'attaquant a accès au compte pendant un mois entier ! À l'inverse, si le jeton expire toutes les 5 minutes, l'utilisateur devra retaper son mot de passe 200 fois par jour.\nLa solution industrielle standard (OAuth2 / OpenID Connect) repose sur un **couple de jetons** :\n- **`Access Token` (durée très courte : 5 à 15 min)** : envoyé à chaque appel d'API.\n- **`Refresh Token` (durée longue : 7 à 30 jours)** : stocké en lieu sûr et envoyé uniquement à la route `/api/auth/refresh` pour obtenir silencieusement un nouvel `Access Token` frais !"
            },
            "explanation": [
                "**Distinction vitale : Authentification (`401 Unauthorized`) vs Autorisation (`403 Forbidden`)** :\n  - **`401 Unauthorized` (Qui êtes-vous ?)** : Le client n'a pas envoyé de jeton, ou son jeton est expiré / falsifié / révoqué.\n  - **`403 Forbidden` (Vous n'avez pas les droits !)** : Le jeton est valide (`stagiaire`), mais la route exige le rôle `admin`.",
                "**Factoriser le RBAC dans FastAPI avec une usine de dépendances `Depends(exiger_role('admin'))`** :\n  - Au lieu de créer un décorateur `@wraps(f)` qui manipule `g.utilisateur` comme en Flask, l'idiome FastAPI consiste à écrire une fonction `def exiger_role(role_minimum: str)` qui retourne une dépendance asynchrone `dependance_rbac`.\n  - Dans la route, écrire `utilisateur: dict = Depends(exiger_role('admin'))` exécute automatiquement la vérification `401`/`403` ET injecte le dictionnaire `utilisateur` typé directement en argument !",
                "**Révocation de jeton (Blacklist / Déconnexion)** : Le serveur maintient en mémoire rapide (ou Redis) un ensemble (`set`) des jetons révoqués (`jetons_revoques`)."
            ],
            "code": _read("04_refresh_token_et_rbac.py"),
            "line_explanations": [
                {"lines": "15-16", "text": "Utilisation de deux sels cryptographiques distincts (`salt='access-token'` vs `'refresh-token'`) pour séparer Access et Refresh Tokens."},
                {"lines": "30-55", "text": "Usine de dépendance `exiger_role(role_minimum)` retournant `dependance_rbac` qui lève `HTTPException(401)` ou `HTTPException(403)`."},
                {"lines": "59-79", "text": "Routes `/api/auth/login` (émet le couple Access + Refresh) et `/api/auth/refresh` (renouvelle l'Access Token)."},
                {"lines": "83-85", "text": "Route `@app.get('/api/admin/audit')` protégée par `utilisateur: dict = Depends(exiger_role('admin'))`."}
            ],
            "python_runner": {
                "prompt": "Exécutez `day_4/04_refresh_token_et_rbac.py` pour observer `Depends(exiger_role('admin'))` distinguer 401, 403 et 200 :",
                "initial_code": _read("04_refresh_token_et_rbac.py")
            },
            "vscode_instructions": {
                "filename": "day_4/04_refresh_token_et_rbac.py",
                "steps": [
                    "Ouvrir `day_4/04_refresh_token_et_rbac.py` dans l'éditeur.",
                    "Étudier l'usine de dépendance `exiger_role('admin')` et son injection via `Depends(...)`."
                ]
            }
        },
        {
            "id": "d4-l5",
            "file": "day_4/03_rate_limiting_429.py",
            "title": "4.5 — Ingénierie du Rate Limiting : Algorithmes, Quotas & En-têtes (`429 Too Many Requests`)",
            "duration": "60 min",
            "analogy": {
                "title": "Le disjoncteur qui protège la centrale électrique contre les courts-circuits",
                "text": "Même avec une authentification parfaite, un client légitime dont le script contient une boucle `while True:` sans pause, ou un attaquant lançant une attaque par force brute sur `/api/auth/token`, peut envoyer 10 000 requêtes par seconde et faire tomber la base de données pour tous les autres utilisateurs.\nLe **Rate Limiting (Limitation de débit)** impose un quota strict par client (`request.client.host`) et rejette immédiatement l'excédent avec le code **`429 Too Many Requests`**."
            },
            "explanation": [
                "**Les 3 algorithmes classiques de Rate Limiting** :\n  1. **Fenêtre Fixe (*Fixed Window*)** : Un compteur par minute calendaire.\n  2. **Fenêtre Glissante (*Sliding Window Log*)** : Le serveur conserve les horodatages exacts (`time.time()`) des requêtes récentes et purge ceux qui datent de plus de `N` secondes.\n  3. **Seau à Jetons (*Token Bucket*)** : Autorise de courts pics de trafic (*bursts*) tout en limitant la moyenne.",
                "**Les En-têtes HTTP standards de Rate Limiting dans FastAPI** :\n  - `X-RateLimit-Limit: 3` (plafond autorisé par fenêtre)\n  - `X-RateLimit-Remaining: 1` (requêtes restantes avant blocage)\n  - `Retry-After: 18` (nombre exact de secondes à attendre avant de réessayer lorsque `JSONResponse(status_code=429, headers=...)` est déclenché)."
            ],
            "code": _read("03_rate_limiting_429.py"),
            "line_explanations": [
                {"lines": "13-15", "text": "Définit la politique : maximum `3` requêtes sur une fenêtre glissante de `20` secondes par adresse IP (`request.client.host`)."},
                {"lines": "26-40", "text": "Si le quota est atteint (`>= 3`), retourne une `JSONResponse(status_code=429)` avec les en-têtes `Retry-After`, `X-RateLimit-Limit` et `X-RateLimit-Remaining: 0`."},
                {"lines": "43-49", "text": "Enregistre l'horodatage courant et injecte `X-RateLimit-Limit` et `X-RateLimit-Remaining` sur l'objet `response: Response`."}
            ],
            "sandbox_preset": {
                "label": "Tester le Rate Limiter (Cliquez 4 fois !) : GET /api/sandbox/ratelimit-demo",
                "method": "GET",
                "url": "/api/sandbox/ratelimit-demo",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_4/03_rate_limiting_429.py` pour observer les 3 premiers appels en 200 OK puis le 4e en 429 Too Many Requests :",
                "initial_code": _read("03_rate_limiting_429.py")
            },
            "vscode_instructions": {
                "filename": "day_4/03_rate_limiting_429.py",
                "steps": [
                    "Ouvrir `day_4/03_rate_limiting_429.py` dans l'éditeur.",
                    "Dans le Client HTTP, cliquer 4 fois de suite sur `GET /api/sandbox/ratelimit-demo` pour observer la transition de `200 OK` vers `429 Too Many Requests`."
                ]
            }
        },
        {
            "id": "d4-l6",
            "file": "day_4/05_cors_webhooks_headers.py",
            "title": "4.6 — Sécurité Périmétrique : `CORSMiddleware`, Signatures de Webhooks (`await request.body()` + `HMAC-SHA256`) & Protection `413`",
            "duration": "55 min",
            "analogy": {
                "title": "L'API inversée (Webhook) et le contrôle des origines (CORSMiddleware)",
                "text": "Comment être prévenu en temps réel lorsqu'un paiement bancaire est validé chez un prestataire externe (CIB / Edahabia / Stripe) ? Au lieu d'interroger la banque toutes les secondes (*Polling*), c'est la banque qui envoie une requête `POST` automatique vers notre serveur dès que l'événement survient : c'est un **Webhook**."
            },
            "explanation": [
                "**Authentifier un Webhook entrant par Signature `HMAC-SHA256` sur `await request.body()`** :\n  1. Le partenaire calcule une empreinte `HMAC-SHA256` sur les octets bruts du corps JSON avec un secret partagé (`WEBHOOK_SECRET`).\n  2. Il place cette empreinte dans l'en-tête `X-Webhook-Signature: sha256=...`.\n  3. Côté FastAPI, on récupère les octets bruts exacts avec **`corps_brut = await request.body()`**, on recalcule le HMAC et on compare les deux signatures en temps constant avec `hmac.compare_digest`.",
                "**Configurer CORS dans FastAPI avec `CORSMiddleware`** : `app.add_middleware(CORSMiddleware, allow_origins=ORIGINES_AUTORISEES, allow_methods=[...], allow_headers=[...])` gère automatiquement les requêtes *Preflight* `OPTIONS` et l'en-tête `Access-Control-Allow-Origin`.",
                "**Protection contre la saturation mémoire (`413 Payload Too Large`)** : En vérifiant `len(corps_brut) > MAX_BODY_BYTES`, FastAPI rejette immédiatement avec le code `413` toute tentative d'envoi d'un corps JSON géant."
            ],
            "code": _read("05_cors_webhooks_headers.py"),
            "line_explanations": [
                {"lines": "22-27", "text": "Ajout de `CORSMiddleware` avec liste blanche stricte `allow_origins=ORIGINES_AUTORISEES`."},
                {"lines": "31-37", "text": "Middleware ASGI ajoutant systématiquement `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` et `Cache-Control: no-store`."},
                {"lines": "41-61", "text": "Route Webhook lisant `corps_brut = await request.body()`, contrôlant la taille maximale (`413`) et vérifiant la signature `HMAC-SHA256` avec `hmac.compare_digest`."}
            ],
            "python_runner": {
                "prompt": "Exécutez `day_4/05_cors_webhooks_headers.py` pour tester le Webhook signé HMAC-SHA256 et `CORSMiddleware` :",
                "initial_code": _read("05_cors_webhooks_headers.py")
            },
            "vscode_instructions": {
                "filename": "day_4/05_cors_webhooks_headers.py",
                "steps": [
                    "Ouvrir `day_4/05_cors_webhooks_headers.py` dans l'éditeur.",
                    "Observer comment `await request.body()` récupère les octets bruts exacts sur le flux ASGI pour calculer le HMAC-SHA256."
                ]
            }
        },
        {
            "id": "d4-l7",
            "file": "day_4/07_cookies_et_sessions_securisees.py",
            "title": "4.7 — Gestion & Sécurité des Cookies dans FastAPI : `Cookie(None)`, `response.set_cookie`, Sessions Signées HMAC & `HttpOnly`, `Secure`, `SameSite`",
            "duration": "65 min",
            "analogy": {
                "title": "Le bracelet d'identification scellé au poignet (Cookie HttpOnly Signé) vs le billet posé sur la table (localStorage)",
                "text": "Où une application Web (React, Vue ou Portail Jinja2) doit-elle stocker son jeton d'authentification ?\nSi vous stockez un JWT dans `localStorage.setItem('token', ...)` en JavaScript, la moindre faille XSS peut exécuter `localStorage.getItem('token')` et voler les comptes de tous vos utilisateurs !\nÀ l'inverse, un **Cookie HTTP doté des drapeaux `httponly=True`, `secure=True` et `samesite='strict'`** est géré directement par le moteur réseau du navigateur : **aucun code JavaScript (`document.cookie`) ne peut le lire**, et le serveur le signe cryptographiquement par HMAC (`URLSafeTimedSerializer`)."
            },
            "explanation": [
                "**1. Émission (`response.set_cookie`) et lecture déclarative (`Cookie(default=None)`) dans FastAPI** :\n  - Lors de la connexion (`POST /api/auth/cookie-login`), la route reçoit `response: Response` et appelle `response.set_cookie(key='isgp_auth_token', value=jeton_signe, httponly=True, samesite='strict')`.\n  - Sur les routes protégées, FastAPI extrait automatiquement le cookie déclaré dans la signature : `isgp_auth_token: Optional[str] = Cookie(default=None)`.",
                "**2. Les 3 Drapeaux de Sécurité Obligatoires sur tout Cookie Sensible** :\n  - **`HttpOnly` (`httponly=True`) — Bouclier Anti-XSS** : Interdit totalement à JavaScript (`document.cookie`) d'accéder au cookie.\n  - **`Secure` (`secure=True`) — Bouclier Réseau TLS** : Ordonne au navigateur de ne transmettre le cookie **que** sur une connexion chiffrée **HTTPS**.\n  - **`SameSite` (`samesite='strict'` ou `'lax'`) — Bouclier Anti-CSRF (*Cross-Site Request Forgery*)** : Empêche un site externe malveillant (`evil.com`) de déclencher une requête authentifiée.",
                "**3. Révocation et Déconnexion (`response.delete_cookie('nom', path='/')`)** :\n  - Envoie un en-tête `Set-Cookie` avec **`Max-Age=0`**, ce qui force le navigateur à purger immédiatement le cookie."
            ],
            "code": _read("07_cookies_et_sessions_securisees.py"),
            "line_explanations": [
                {"lines": "23-25", "text": "Initialisation des signataires HMAC `signataire_session` et `signataire_jeton` avec sels distincts."},
                {"lines": "34-65", "text": "Route `POST /api/auth/cookie-login` : émet `isgp_session` (signé HMAC) et `isgp_auth_token` (`httponly=True`, `samesite='strict'`) via `response.set_cookie(...)`."},
                {"lines": "78-107", "text": "Route `GET /api/auth/cookie-inspect` : extrait les cookies via `Cookie(default=None)` et vérifie leurs signatures HMAC."},
                {"lines": "137-142", "text": "Route `POST /api/auth/cookie-logout` : révoque les cookies via `response.delete_cookie(..., path='/')` (`Max-Age=0`)."}
            ],
            "sandbox_preset": {
                "label": "1. Émettre Cookies Sécurisés (HttpOnly + Session HMAC) : POST /api/sandbox/cookies/login",
                "method": "POST",
                "url": "/api/sandbox/cookies/login",
                "body": '{\n  "identifiant": "yasmine.merabet",\n  "theme": "sombre"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez le cycle complet des Cookies sécurisés dans FastAPI (`response.set_cookie`, `Cookie(None)` et `delete_cookie`) :",
                "initial_code": _read("07_cookies_et_sessions_securisees.py")
            },
            "vscode_instructions": {
                "filename": "day_4/07_cookies_et_sessions_securisees.py",
                "steps": [
                    "Ouvrir `day_4/07_cookies_et_sessions_securisees.py` dans l'éditeur.",
                    "Observer les attributs `HttpOnly`, `Max-Age=3600` et `SameSite=strict` générés dans l'en-tête HTTP `Set-Cookie`."
                ]
            }
        }
    ]
}
