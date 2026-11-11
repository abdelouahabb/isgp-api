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
                "text": (
                    "En ingénierie des systèmes, une confusion récurrente assimile quatre transformations mathématiques aux garanties pourtant radicalement distinctes : l'**encodage** (Base64 ou UTF-8) se borne à convertir des octets dans un alphabet ASCII transportable sans offrir la moindre confidentialité, puisque quiconque peut l'inverser instantanément sans clé ; le **hachage cryptographique** (SHA-256, PBKDF2, Scrypt, Argon2) projette une entrée vers une empreinte irréversible à sens unique, indispensable pour stocker des mots de passe associés à un sel aléatoire (`salt`).\n\n"
                    "À ces deux primitives s'ajoutent le **chiffrement** (AES-GCM, TLS/HTTPS), qui garantit la confidentialité en rendant le message illisible sans clé de déchiffrement, et la **signature cryptographique (HMAC-SHA256)**, qui scelle un message à l'aide d'une `SECRET_KEY` serveur afin de prouver mathématiquement son authenticité et son intégrité à chaque transit réseau."
                )
            },
            "explanation": [
                "**Externalisation absolue des secrets hors du dépôt Git (Twelve-Factor App, Facteur III).** Le code source Python vocationnellement partagé entre développeurs et pipelines CI/CD conserve perpétuellement l'historique de chaque validation dans Git : inscrire `SECRET_KEY = 'mon-secret'` dans un module `.py` compromet définitivement les clés de production. Tout secret cryptographique s'injecte exclusivement au démarrage du processus Uvicorn via la table d'environnement du système d'exploitation (`os.environ.get('API_SECRET_KEY')`).",
                "**Bannissement des secrets dans les URIs au profit exclusif des en-têtes HTTP.** Même lorsque le transport est chiffré de bout en bout par TLS (`https://`), le chemin et la chaîne de requête (`?api_key=...`) sont consignés en texte clair dans les journaux `access.log` des proxys inverses Nginx, dans les sondes d'observabilité et dans l'historique des navigateurs. Les clés d'API et jetons d'accès doivent dès lors voyager exclusivement dans les **en-têtes HTTP (`Headers`)**.",
                "**Injection déclarative de l'authentification M2M via `Header(alias='X-API-Key')` et `Depends()`.** L'architecture de sécurité de FastAPI isole la vérification d'identité machine-à-machine dans une dépendance réutilisable `verifier_cle_api(x_api_key: Optional[str] = Header(default=None, alias='X-API-Key'))` : branchée sur n'importe quelle route ou `APIRouter` via `Depends(verifier_cle_api)`, elle valide l'en-tête avant l'exécution métier et lève `HTTPException(status_code=401)` en cas d'absence ou de discordance.",
                "**Neutralisation des attaques par canal auxiliaire temporel avec `hmac.compare_digest`.** L'opérateur booléen standard `==` compare deux chaînes octet par octet et interrompt l'évaluation dès le premier caractère discordant, créant une fuite temporelle de quelques nanosecondes exploitable statistiquement pour deviner une clé caractère par caractère (*Timing Attack*). La primitive `hmac.compare_digest(a, b)` parcourt l'intégralité des tampons en **temps constant**, rendant le temps de réponse strictement indépendant de la position de l'erreur."
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
                "text": (
                    "Contrairement à une clé d'API statique partagée entre deux serveurs, un jeton d'accès destiné à un opérateur humain doit transporter son identité nominative, son rôle métier et une échéance stricte de validité sans obliger les workers ASGI à interroger une table de sessions centrale à chaque requête.\n\n"
                    "Avec un **Jeton Signé (`Bearer Token` / `JWT`)**, l'utilisateur présente ses identifiants une seule fois sur `POST /api/auth/token` ; le serveur assemble alors un passeport JSON horodaté (`{\"utilisateur\": \"stagiaire\", \"role\": \"participant\"}`), le scelle par une **signature mathématique HMAC-SHA256** calculée avec sa `SECRET_KEY`, et le client le présente ensuite dans l'en-tête `Authorization: Bearer <token>` inspecté par `Depends(extraire_utilisateur_token)`."
                )
            },
            "explanation": [
                "**Structure segmentée d'un jeton signé (JWT RFC 7519 et `URLSafeTimedSerializer`).** Tout jeton signé concatène par des points `.` une charge utile (`Payload`) encodée en Base64URL — rassemblant les déclarations d'identité (*claims* tels que `sub`, `role` et l'horodatage d'émission `iat`) — et un sceau cryptographique calculé selon `HMAC_SHA256(Base64URL(Payload), SECRET_KEY)` que seul un détenteur de la clé secrète serveur peut forger.",
                "**Invariant critique de confidentialité : un jeton signé est lisible en clair (`Signé != Chiffré`).** Le segment `Payload` d'un JWT ou d'un jeton `itsdangerous` n'étant qu'encodé en Base64URL sans chiffrement symétrique, n'importe quel observateur interceptant la chaîne peut décoder et lire ses attributs JSON instantanément : aucun secret (mot de passe, clé privée, donnée bancaire) ne doit jamais y figurer. En revanche, l'intégrité est absolue : modifier un seul bit du rôle invalide le recalcul HMAC côté serveur.",
                "**Validation sans état (*Stateless*) et expiration horodatée via `Depends` et `HTTPBearer`.** À chaque appel entrant, le schéma `HTTPBearer()` extrait le jeton de l'en-tête `Authorization` et la dépendance invoque `signer.loads(token, max_age=300)` : le serveur contrôle simultanément l'authenticité cryptographique (`BadSignature`) et la fraîcheur temporelle (`SignatureExpired`) en mémoire vive, levant `HTTPException(status_code=401)` à la moindre anomalie."
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
                "text": (
                    "En gouvernance d'API (*API Management*), amalgamer **Authentification (`AuthN`)** et **Autorisation (`AuthZ`)** engendre les vulnérabilités d'élévation de privilèges les plus critiques en production. L'**Authentification (`AuthN` — « Qui êtes-vous ? »)** correspond au contrôle du passeport au poste frontière : si le titre est absent, expiré ou falsifié, l'accès est refusé dès le périmètre avec le code **`401 Unauthorized`**.\n\n"
                    "L'**Autorisation (`AuthZ` — « Qu'avez-vous le droit d'accomplir ? »)** intervient une fois l'identité formellement prouvée : un passager muni d'un passeport authentique et d'un billet classe économique qui tente de pénétrer dans le cockpit est parfaitement identifié par la sécurité, mais son profil lui interdit cet espace, déclenchant le statut **`403 Forbidden`**."
                )
            },
            "explanation": [
                "**Sémantique normative RFC 9110 entre `401 Unauthorized` (`AuthN`) et `403 Forbidden` (`AuthZ`).** Malgré l'ambiguïté historique de son intitulé anglais, le code `401 Unauthorized` désigne exclusivement un défaut d'**authentification** (preuve d'identité absente, clé erronée, signature HMAC corrompue ou jeton expiré, invitant le client à se reconnecter), tandis que le code `403 Forbidden` atteste que l'identité du demandeur est connue et vérifiée mais que ses habilitations interdisent l'opération sollicitée.",
                "**Défense en profondeur de l'autorisation : `RBAC`, `Scopes` OAuth2 et contrôle de propriété anti-`BOLA`.** Une politique d'autorisation robuste superpose trois verrous complémentaires dans le graphe `Depends()` de FastAPI : le contrôle par rôle métier (**RBAC** : `stagiaire`, `formateur`, `admin`), les permissions déléguées granulaires du jeton (**Scopes OAuth2** tels que `dossiers:read` vs `dossiers:write`) et la vérification systématique d'appartenance de l'enregistrement ciblé (**Object Ownership**) indispensable pour parer la faille mondiale n°1 de l'OWASP API Security Top 10 (**BOLA — Broken Object Level Authorization**, où un utilisateur authentifié `amine` tente de lire `/api/v1/dossiers/102` appartenant à `sara`)."
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
                "text": (
                    "Émettre un jeton d'accès unique valable trente jours expose l'organisation à un risque majeur : en cas d'exfiltration sur un réseau compromis, l'assaillant conserve le contrôle du compte pendant un mois entier sans possibilité de révocation *stateless*. À l'inverse, expirer le jeton toutes les cinq minutes en exigeant la ressaisie du mot de passe rend l'application inutilisable.\n\n"
                    "Les standards industriels OAuth 2.0 et OpenID Connect résolvent ce dilemme par une **architecture asymétrique à deux jetons** : un **`Access Token` éphémère (5 à 15 minutes)** présenté à chaque appel métier et vérifié en RAM pure, associé à un **`Refresh Token` de longue durée (7 à 30 jours)** conservé dans un coffre sécurisé et transmis exclusivement à l'endpoint `/api/auth/refresh` pour obtenir silencieusement un nouvel `Access Token`."
                )
            },
            "explanation": [
                "**Séparation cryptographique des domaines d'usage (`salt='access-token'` vs `salt='refresh-token'`).** Afin d'interdire mathématiquement à un attaquant de présenter un `Refresh Token` de longue durée en guise d'`Access Token` sur une route métier, les deux jetons sont signés avec des sels cryptographiques distincts : la dépendance `AuthN` rejette par `401 Unauthorized` tout jeton absent, falsifié ou signé avec un mauvais sel, puis la couche `AuthZ` oppose `403 Forbidden` si le rôle porté est insuffisant.",
                "**Usine de dépendances paramétrée `Depends(exiger_role('admin'))` dans FastAPI.** Plutôt que d'écrire des décorateurs `@wraps` opaques manipulant un contexte global, l'idiome architectural de FastAPI consiste à concevoir une fonction d'ordre supérieur `def exiger_role(role_minimum: str)` retournant une sous-dépendance typée `dependance_rbac`. L'annotation `utilisateur: dict = Depends(exiger_role('admin'))` dans la signature d'une route exécute toute la chaîne de contrôle `401`/`403`, documente le verrou dans OpenAPI et livre directement l'identité vérifiée en paramètre.",
                "**Révocation d'urgence et rotation d'état par liste d'opposition (`Blacklist`).** En confinant le contrôle d'état (ensemble mémoire `jetons_revoques` ou clés à expiration automatique TTL dans Redis) au seul endpoint peu fréquent `/api/auth/refresh`, l'architecture préserve la vélocité *stateless* de 99 % du trafic métier tout en permettant d'invalider instantanément une session lors d'une déconnexion ou d'une alerte de sécurité."
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
                "text": (
                    "Une authentification irréprochable ne protège nullement la disponibilité physique d'un serveur : un client partenaire légitime ayant oublié un délai d'attente dans une boucle `while True:`, ou un bot menant une attaque par dictionnaire sur `/api/auth/token`, peut saturer l'ensemble des connexions SQLite/PostgreSQL en envoyant dix mille requêtes par seconde.\n\n"
                    "Le **Rate Limiting (Limitation de débit)** agit comme un disjoncteur volumétrique par client (`request.client.host` ou identité du jeton) qui absorbe les cadences normales et coupe court à toute rafale abusive avec le code normalisé **`429 Too Many Requests`**."
                )
            },
            "explanation": [
                "**Arbitrage algorithmique entre Fenêtre Fixe, Fenêtre Glissante (*Sliding Window*) et Seau à Jetons (*Token Bucket*).** Alors qu'un simple compteur par minute calendaire (*Fixed Window*) souffre d'un doublement de trafic aux frontières de minutes, le journal à **Fenêtre Glissante (*Sliding Window Log*)** conserve les horodatages exacts des appels récents et élague dynamiquement ceux antérieurs à `T - fenetre` pour garantir un plafond mathématiquement exact, tandis que le **Seau à Jetons (*Token Bucket*)** tolère de brèves rafales (*bursts*) tout en lissant le débit moyen.",
                "**Signalisation de contre-pression (*Backpressure*) par les en-têtes `X-RateLimit-*` et `Retry-After`.** Un limiteur de débit bien conçu informe proactivement les SDK consommateurs de l'état de leur enveloppe sur chaque réponse HTTP via `X-RateLimit-Limit` (plafond nominal) et `X-RateLimit-Remaining` (crédit résiduel), puis joint obligatoirement l'en-tête RFC 6585 `Retry-After` sur toute `JSONResponse(status_code=429)` afin d'indiquer le nombre exact de secondes de mise en sommeil requis avant le prochain essai."
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
                "text": (
                    "Comment un système d'inscription est-il averti à la seconde même où un paiement par carte CIB, Edahabia ou Stripe est confirmé chez l'opérateur monétique ? Plutôt que d'épuiser le réseau en interrogeant la banque toutes les deux secondes (*Polling*), les architectures événementielles inversent le flux : c'est le serveur de la banque qui déclenche une requête `POST` signée vers notre endpoint dès la validation de la transaction, selon le patron du **Webhook**.\n\n"
                    "Parallèlement, lorsqu'un frontal Web légitime hébergé sur un domaine distinct interroge l'API, le périmètre ASGI doit orchestrer explicitement la politique d'origines croisées via **`CORSMiddleware`** tout en protégeant la RAM contre les charges surdimensionnées (`413`)."
                )
            },
            "explanation": [
                "**Authentification cryptographique d'un Webhook par `HMAC-SHA256` sur `await request.body()`.** Comme l'URL d'un récepteur de Webhook est exposée sur Internet, le prestataire émetteur calcule une empreinte `HMAC-SHA256` sur les octets bruts exacts de la charge utile à l'aide d'un secret partagé (`WEBHOOK_SECRET`) et la transmet dans `X-Webhook-Signature`. Côté FastAPI, la route lit impérativement le tampon binaire intact via **`corps_brut = await request.body()`** — sans jamais re-sérialiser un dictionnaire Python — et valide le sceau en temps constant avec `hmac.compare_digest`.",
                "**Délégation du protocole CORS et des requêtes *Preflight* `OPTIONS` à `CORSMiddleware`.** Pour lever sélectivement la politique de même origine (*Same-Origin Policy*) des navigateurs sans ouvrir de brèche universelle `*`, l'enregistrement `app.add_middleware(CORSMiddleware, allow_origins=ORIGINES_AUTORISEES, allow_methods=[...], allow_headers=[...])` répond automatiquement aux sondes préalables `OPTIONS` et injecte `Access-Control-Allow-Origin` uniquement pour les domaines frontaux homologués.",
                "**Protection de l'empreinte mémoire des workers ASGI (`413 Payload Too Large`).** Contrôler la taille du flux entrant (`len(corps_brut) > MAX_BODY_BYTES`, doublé en amont par `client_max_body_size` dans Nginx) avorte immédiatement par un statut `413 Payload Too Large` toute tentative de déni de service par saturation de la RAM avant même l'invocation de l'analyseur JSON."
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
                "text": (
                    "Où une application Web servie dans un navigateur (SPA React/Vue ou portail Jinja2) doit-elle conserver son jeton d'authentification ? L'entreposer dans `window.localStorage` expose l'ensemble du parc utilisateurs : la moindre vulnérabilité XSS dans une dépendance JavaScript tierce permet d'exécuter `localStorage.getItem('token')` et d'exfiltrer silencieusement toutes les sessions actives.\n\n"
                    "À l'inverse, un **Cookie HTTP blindé par les attributs `httponly=True`, `secure=True` et `samesite='strict'`** demeure confiné dans le coffre réseau interne du navigateur, totalement inaccessible au moteur JavaScript (`document.cookie`), tandis que sa signature HMAC (`URLSafeTimedSerializer`) garantit son intégrité côté FastAPI."
                )
            },
            "explanation": [
                "**Émission sur `Response` (`set_cookie`) et extraction déclarative (`Cookie(default=None)`).** Lors de l'authentification (`POST /api/auth/cookie-login`), injecter `response: Response` dans la signature FastAPI permet d'inscrire l'en-tête `Set-Cookie` via `response.set_cookie(key='isgp_auth_token', value=jeton_signe, httponly=True, samesite='strict')`. Aux requêtes ultérieures, le navigateur joint automatiquement l'en-tête `Cookie`, que FastAPI désérialise et valide déclarativement via `isgp_auth_token: Optional[str] = Cookie(default=None)`.",
                "**Triptyque de défense navigateur : `HttpOnly`, `Secure` et `SameSite`.** Chaque attribut neutralise une classe d'attaque distincte : **`HttpOnly`** soustrait le cookie à l'API DOM `document.cookie` pour bloquer le vol de session par XSS ; **`Secure`** interdit toute transmission sur un lien HTTP en clair pour prévenir l'interception réseau ; et **`SameSite='strict'` (ou `'lax'`)** empêche un domaine tiers malveillant (`evil.com`) de déclencher à l'insu de l'utilisateur une mutation authentifiée (*Cross-Site Request Forgery — CSRF*).",
                "**Destruction déterministe de session par expiration immédiate (`delete_cookie`).** Appeler `response.delete_cookie('isgp_auth_token', path='/')` sur la route de déconnexion émet une directive `Set-Cookie` assortie de `Max-Age=0`, ordonnant au navigateur de purger instantanément le secret de son magasin persistant."
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
