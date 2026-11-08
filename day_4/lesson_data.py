import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_4_DATA = {
    "day_number": 4,
    "folder": "day_4",
    "badge": "Jour 4 • Secrets, Tokens, RBAC & Rate Limit",
    "title": "Sécurité & Résilience des APIs : Secrets, Jetons Signés (JWT/Bearer), Refresh Tokens, RBAC, Rate Limiting et Webhooks",
    "goal": "Maîtriser l'architecture de sécurité complète d'une API : distinguer encodage, hachage, chiffrement et signature HMAC ; isoler les secrets hors du code ; émettre et vérifier des Bearer Tokens ; implémenter le cycle Access/Refresh Token et le contrôle d'accès par rôle (RBAC : 401 vs 403) ; protéger le serveur par Rate Limiting (429) et authentifier les Webhooks entrants.",
    "starter_filename": "day_4/02_bearer_tokens_signes.py",
    "files": [
        "day_4/01_secrets_et_api_key.py",
        "day_4/02_bearer_tokens_signes.py",
        "day_4/06_authn_vs_authz_scopes.py",
        "day_4/04_refresh_token_et_rbac.py",
        "day_4/03_rate_limiting_429.py",
        "day_4/05_cors_webhooks_headers.py",
    ],
    "lessons": [
        {
            "id": "d4-l1",
            "file": "day_4/01_secrets_et_api_key.py",
            "title": "4.1 — Fondations Cryptographiques, Gestion des Secrets (`os.environ`) & Clés API (`X-API-Key`)",
            "duration": "60 min",
            "analogy": {
                "title": "Distinguer les 4 opérations fondamentales de sécurité informatique",
                "text": "Les débutants confondent souvent quatre concepts pourtant très différents :\n1. **Encodage (Base64 / UTF-8)** : Traduire des données dans un alphabet transportable. **Aucune sécurité** : n'importe qui peut décoder du Base64 instantanément sans clé.\n2. **Hachage (SHA-256, Scrypt, Bcrypt)** : Empreinte à **sens unique** (irréversible). Utilisé pour stocker les mots de passe en base : on ne stocke jamais un mot de passe en clair, seulement son empreinte hachée avec un sel (`salt`).\n3. **Chiffrement (AES, TLS/HTTPS)** : Rendre un message illisible sauf pour celui qui possède la clé de déchiffrement (réversible avec clé).\n4. **Signature Cryptographique (HMAC-SHA256)** : Attacher un sceau mathématique calculé avec une `SECRET_KEY` pour prouver que le message n'a pas été modifié en route."
            },
            "explanation": [
                "**Règle n°1 — Zéro secret dans le code source (Facteur III de Twelve-Factor App)** : Le code Python est partagé dans Git. Si vous écrivez `SECRET_KEY = 'mon-secret'` dans un fichier `.py`, toute personne ayant accès au dépôt Git possède les clés de production. On injecte toujours les secrets via les **variables d'environnement du système** (`os.environ.get('API_SECRET_KEY')`).",
                "**Règle n°2 — Ne jamais transmettre de secret dans l'URL (`?api_key=...`)** : Même en HTTPS, l'URL complète est enregistrée en clair dans les fichiers journaux (`access.log`) des proxys, pare-feux, serveurs web et dans l'historique du navigateur. Les secrets voyagent exclusivement dans les **en-têtes HTTP (`Headers`)**.",
                "**Authentification Machine-à-Machine par `X-API-Key`** : Pour authentifier un serveur partenaire ou un script automatisé, le client envoie `X-API-Key: <cle>`. Le serveur compare cette clé avec `hmac.compare_digest(a, b)`.",
                "**Pourquoi `hmac.compare_digest` au lieu de `==` ? (Attaque Temporelle / Timing Attack)** : L'opérateur `==` compare les caractères un par un et s'arrête dès la première différence (en quelques nanosecondes). En mesurant le temps de réponse sur des milliers d'essais, un attaquant peut deviner la clé caractère par caractère. `hmac.compare_digest` prend exactement le même temps quelle que soit la position de l'erreur."
            ],
            "code": _read("01_secrets_et_api_key.py"),
            "line_explanations": [
                {"lines": "11-12", "text": "`os.environ.get(...)` lit les secrets depuis la mémoire du système d'exploitation."},
                {"lines": "17", "text": "`request.headers.get('X-API-Key', '')` extrait la clé transmise dans l'en-tête HTTP."},
                {"lines": "20-23", "text": "`hmac.compare_digest` vérifie l'égalité en temps constant et renvoie `401 Unauthorized` si la clé est absente ou erronée."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/admin-stats (X-API-Key)",
                "method": "GET",
                "url": "/api/sandbox/admin-stats",
                "headers": {"X-API-Key": "isgp-secret-2026"},
                "body": ""
            },
            "python_runner": {
                "prompt": "Expérimentez le hachage de mot de passe (avec sel) et la comparaison en temps constant d'une clé API :",
                "initial_code": '''import os
import hmac
import hashlib

# 1. Hachage sécurisé d'un mot de passe avec sel aléatoire (PBKDF2-HMAC-SHA256)
mot_de_passe_clair = "isgp2026"
sel = os.urandom(16)
empreinte = hashlib.pbkdf2_hmac("sha256", mot_de_passe_clair.encode(), sel, 100_000)
print("Sel aléatoire (hex) :", sel.hex())
print("Empreinte stockée en base (irréversible) :", empreinte.hex()[:36] + "...")

# 2. Vérification d'une clé API en temps constant
os.environ["ISGP_API_SECRET"] = "sk_live_98f7a6b5c4d3e2f1"
secret_serveur = os.environ.get("ISGP_API_SECRET")
cle_client = "sk_live_98f7a6b5c4d3e2f1"
print("Clé API valide (temps constant) :", hmac.compare_digest(cle_client, secret_serveur))'''
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
            "title": "4.2 — Anatomie des Jetons Signés (`Bearer Token` / JWT) : Émission, Signature HMAC & Expiration",
            "duration": "65 min",
            "analogy": {
                "title": "Le badge électronique temporaire infalsifiable",
                "text": "Une clé API fixe ne porte ni l'identité d'un utilisateur humain, ni son rôle, ni de date d'expiration. Avec un **Jeton Signé (Bearer Token / JWT)** :\n1. L'utilisateur présente son identifiant et son mot de passe une seule fois sur `POST /api/auth/token`.\n2. Le serveur fabrique un badge numérique contenant `{\"utilisateur\": \"stagiaire\", \"role\": \"participant\"}` + l'heure d'émission, et y appose une **signature mathématique HMAC** calculée avec sa `SECRET_KEY`.\n3. À chaque requête suivante, le client présente ce jeton dans l'en-tête `Authorization: Bearer <token>`. Le serveur n'a même plus besoin d'interroger sa base de données : il lui suffit de recalculer la signature mathématique pour savoir immédiatement que le badge est authentique et non expiré !"
            },
            "explanation": [
                "**Structure interne d'un Jeton Signé (JWT / `itsdangerous`)** : Un jeton est constitué de segments séparés par des points `.` :\n  - **`Payload` (Charge utile encodée en Base64URL)** : Contient les revendications (*claims*) : identifiant (`sub`), rôle (`role`), horodatage d'émission (`iat`).\n  - **`Signature` (HMAC-SHA256)** : `HMAC_SHA256(Base64(Payload), SECRET_KEY)`.",
                "**Piège critique à connaître absolument — Un Token est SIGNÉ, mais PAS CHIFFRÉ !** : Le `Payload` d'un JWT ou d'un jeton `itsdangerous` est simplement encodé en Base64. N'importe qui interceptant le jeton peut lire le dictionnaire JSON qu'il contient ! Il ne faut donc **JAMAIS** mettre de mot de passe, de numéro de carte bancaire ou de donnée secrète à l'intérieur d'un Token. En revanche, personne ne peut **modifier** son contenu (par exemple changer `\"role\": \"stagiaire\"` en `\"role\": \"admin\"`) sans connaître la `SECRET_KEY` du serveur.",
                "**Vérification de l'expiration (`max_age=300`)** : Lors de l'appel à `signer.loads(token, max_age=300)`, le serveur vérifie d'abord la signature cryptographique (`BadSignature`), puis soustrait l'horodatage intégré au jeton de l'heure actuelle (`SignatureExpired` si > 300 secondes)."
            ],
            "code": _read("02_bearer_tokens_signes.py"),
            "line_explanations": [
                {"lines": "9-10", "text": "`URLSafeTimedSerializer(SECRET_KEY)` initialise le moteur de signature HMAC-SHA1/SHA256 avec le secret du serveur."},
                {"lines": "19-20", "text": "`signer.dumps(charge_utile)` sérialise le dictionnaire en JSON, l'encode en Base64URL, ajoute l'horodatage et signe l'ensemble."},
                {"lines": "30-34", "text": "Extrait le jeton de l'en-tête standard `Authorization: Bearer <token>`."},
                {"lines": "36-41", "text": "`signer.loads(token, max_age=300)` distingue explicitement un jeton expiré (`SignatureExpired`) d'un jeton falsifié (`BadSignature`)."}
            ],
            "sandbox_preset": {
                "label": "1. Émettre un Bearer Token : POST /api/sandbox/auth/token",
                "method": "POST",
                "url": "/api/sandbox/auth/token",
                "body": '{\n  "identifiant": "stagiaire",\n  "mot_de_passe": "isgp2026"\n}'
            },
            "python_runner": {
                "prompt": "Inspectez l'anatomie d'un jeton signé et observez pourquoi son contenu est lisible mais infalsifiable :",
                "initial_code": '''import base64
from itsdangerous import URLSafeTimedSerializer, BadSignature

SECRET_SERVEUR = "cle-secrete-inconnue-du-client-2026"
signer = URLSafeTimedSerializer(SECRET_SERVEUR)

# 1. Émission du jeton signé
token = signer.dumps({"utilisateur": "amine", "role": "stagiaire"})
print("1. Jeton complet :", token)

# 2. Découpage des segments (Payload.Timestamp.Signature)
segments = token.split(".")
payload_b64 = segments[0]
# Ajout du padding '=' requis par Base64 standard
payload_clair = base64.urlsafe_b64decode(payload_b64 + "===").decode("utf-8")
print("2. Preuve que le Payload est lisible sans clé :", payload_clair)

# 3. Tentative de falsification d'un caractère
token_falsifie = token[:-1] + ("A" if token[-1] != "A" else "B")
try:
    signer.loads(token_falsifie, max_age=300)
except BadSignature:
    print("3. SÉCURITÉ : Signature invalide détectée ! Jeton rejeté (401 Unauthorized).")'''
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
                "**1. Pourquoi HTTP `401` s'appelle-t-il *Unauthorized* alors qu'il désigne l'Authentification (`AuthN`) ?** C'est une subtilité historique de la norme RFC 9110 :\n  - **`401 Unauthorized` = Défaut d'Authentification (`AuthN`)** : L'identité de l'appelant est inconnue (aucun jeton fourni, `X-API-Key` erronée, signature HMAC invalide ou jeton expiré). Solution pour le client : s'authentifier ou rafraîchir son jeton.\n  - **`403 Forbidden` = Défaut d'Autorisation (`AuthZ`)** : L'authentification a **réussi** (le serveur connaît l'identité exacte de l'utilisateur), mais ses permissions sont insuffisantes. Se reconnecter avec le même compte ne changera rien !",
                "**2. Les 3 piliers de l'Autorisation (`AuthZ`) en API Management** :\n  - **Pilier A — `RBAC` (*Role-Based Access Control*)** : Droits accordés selon le rôle métier de l'utilisateur (`stagiaire`, `formateur`, `admin`). Exemple : seul le rôle `admin` peut supprimer une formation.\n  - **Pilier B — `Scopes` / Permissions granulaires (Standard OAuth2)** : Un jeton d'accès ne donne pas forcément tous les droits du compte ! Il contient une liste explicite de permissions (`scopes`: `[\"formations:read\", \"formations:write\", \"audit:admin\"]`). Si une application mobile dispose uniquement du scope `formations:read`, elle recevra `200 OK` sur `GET /formations` mais `403 Forbidden` sur `POST /formations`.\n  - **Pilier C — Contrôle de Propriété (*Object Ownership*) & Protection contre la faille `BOLA` (*Broken Object Level Authorization*)** : La faille n°1 mondiale du classement **OWASP API Security Top 10** ! Même si `amine` est authentifié (`AuthN` OK) et possède le rôle `stagiaire` et le scope `dossiers:read`, il ne doit **jamais** pouvoir consulter le dossier confidentiel de `sara` en changeant simplement l'ID dans l'URL (`GET /api/dossiers/102`). L'API doit toujours vérifier : `dossier.proprietaire == utilisateur_connecte` (ou `role == 'admin'`)."
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
                    "Cliquez sur « Générer & injecter un Token (stagiaire) » puis rappelez `GET /api/sandbox/authz-demo` -> observez `403 Forbidden (AuthN réussie, mais Échec AuthZ)`.",
                    "Dans `POST /api/sandbox/auth/token`, remplacez `\"stagiaire\"` par `\"directeur\"` pour obtenir un jeton `admin`, puis rappelez `GET /api/sandbox/authz-demo` -> observez `200 OK (AuthN + AuthZ validées)` !"
                ]
            }
        },
        {
            "id": "d4-l4",
            "file": "day_4/04_refresh_token_et_rbac.py",
            "title": "4.4 — Cycle Access / Refresh Token, Révocation (Blacklist) & Décorateur `@exiger_role`",
            "duration": "65 min",
            "analogy": {
                "title": "Pourquoi avoir deux jetons (Access Token court + Refresh Token long) ?",
                "text": "Si vous donnez à un utilisateur un jeton valable 30 jours et que ce jeton est volé, l'attaquant a accès au compte pendant un mois entier ! À l'inverse, si le jeton expire toutes les 5 minutes, l'utilisateur devra retaper son mot de passe 200 fois par jour.\nLa solution industrielle standard (OAuth2 / OpenID Connect) repose sur un **couple de jetons** :\n- **`Access Token` (durée très courte : 5 à 15 min)** : envoyé à chaque appel d'API.\n- **`Refresh Token` (durée longue : 7 à 30 jours)** : stocké en lieu sûr et envoyé uniquement à la route `/api/auth/refresh` pour obtenir silencieusement un nouvel `Access Token` frais sans redemander le mot de passe !"
            },
            "explanation": [
                "**Distinction vitale : Authentification (`401 Unauthorized`) vs Autorisation (`403 Forbidden`)** :\n  - **`401 Unauthorized` (Qui êtes-vous ?)** : Le client n'a pas envoyé de jeton, ou son jeton est expiré / falsifié / révoqué. Le serveur ne connaît pas l'identité de l'appelant.\n  - **`403 Forbidden` (Vous n'avez pas les droits !)** : Le jeton est parfaitement valide — le serveur sait exactement que vous êtes `stagiaire` — mais la route demandée exige le rôle `admin`. Se ré-authentifier ne changera rien.",
                "**Factoriser la sécurité avec un décorateur `@exiger_role('admin')`** : Plutôt que de copier-coller 25 lignes de vérification de jeton au début de chaque route, on crée un décorateur paramétré (étudié au Jour 0.4) qui vérifie le jeton, contrôle le rôle, attache l'utilisateur à `g.utilisateur` et bloque l'accès si nécessaire.",
                "**Révocation de jeton (Blacklist / Déconnexion)** : Comme un jeton signé est autonome (*stateless*), comment l'invalider avant son expiration si l'utilisateur clique sur « Se déconnecter » ? Le serveur maintient en mémoire rapide (ou Redis) un ensemble (`set`) des identifiants de jetons révoqués (`jetons_revoques`)."
            ],
            "code": _read("04_refresh_token_et_rbac.py"),
            "line_explanations": [
                {"lines": "13-14", "text": "Utilisation de deux sels cryptographiques distincts (`salt='access-token'` vs `'refresh-token'`) pour empêcher l'utilisation d'un Refresh Token comme Access Token."},
                {"lines": "20-49", "text": "Décorateur `@exiger_role(role_minimum)` gérant successivement le `401` (absence, révocation, expiration, signature) puis le `403` (rôle insuffisant)."},
                {"lines": "52-65", "text": "Route `/api/auth/login` émettant simultanément l'`access_token` (300s) et le `refresh_token` (7 jours)."},
                {"lines": "68-77", "text": "Route `/api/auth/refresh` vérifiant le `refresh_token` et délivrant un nouvel `access_token`."}
            ],
            "python_runner": {
                "prompt": "Simulez le contrôle d'accès par rôle (RBAC : 401 vs 403 vs 200) et le renouvellement par Refresh Token :",
                "initial_code": '''from itsdangerous import URLSafeTimedSerializer

SECRET = "secret-rbac-isgp-2026"
access_signer = URLSafeTimedSerializer(SECRET, salt="access")
refresh_signer = URLSafeTimedSerializer(SECRET, salt="refresh")

def verifier_acces_route_admin(token_recu):
    if not token_recu:
        return 401, "401 Unauthorized : Aucun jeton fourni"
    try:
        user = access_signer.loads(token_recu, max_age=300)
    except Exception:
        return 401, "401 Unauthorized : Jeton invalide ou expiré"
    if user.get("role") != "admin":
        return 403, f"403 Forbidden : Rôle 'admin' requis (rôle actuel : '{user.get('role')}')"
    return 200, f"200 OK : Bienvenue dans l'espace d'administration, {user.get('sub')}"

token_stagiaire = access_signer.dumps({"sub": "amine", "role": "stagiaire"})
token_directeur = access_signer.dumps({"sub": "directeur", "role": "admin"})

print("Appel sans jeton      ->", verifier_acces_route_admin(None))
print("Appel avec Stagiaire  ->", verifier_acces_route_admin(token_stagiaire))
print("Appel avec Directeur  ->", verifier_acces_route_admin(token_directeur))'''
            },
            "vscode_instructions": {
                "filename": "day_4/04_refresh_token_et_rbac.py",
                "steps": [
                    "Ouvrir `day_4/04_refresh_token_et_rbac.py` dans l'éditeur.",
                    "Étudier la structure du décorateur `@exiger_role('admin')` aux lignes 20 à 49."
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
                "text": "Même avec une authentification parfaite, un client légitime dont le script contient une boucle `while True:` sans pause, ou un attaquant lançant une attaque par force brute sur `/api/auth/token`, peut envoyer 10 000 requêtes par seconde et faire tomber la base de données pour tous les autres utilisateurs.\nLe **Rate Limiting (Limitation de débit)** impose un quota strict par client (par IP, par clé API ou par utilisateur) et rejette immédiatement l'excédent avec le code **`429 Too Many Requests`**."
            },
            "explanation": [
                "**Les 3 algorithmes classiques de Rate Limiting** :\n  1. **Fenêtre Fixe (*Fixed Window*)** : Un compteur par minute calendaire (ex: `14h01`). Très simple, mais souffre d'un effet de bord aux frontières : un client peut envoyer 100 requêtes à `14h00m59s` et 100 requêtes à `14h01m01s` (soit 200 requêtes en 2 secondes).\n  2. **Fenêtre Glissante (*Sliding Window Log*)** : Le serveur conserve les horodatages exacts (`time.time()`) des requêtes récentes et purge ceux qui datent de plus de `N` secondes. Précision mathématique parfaite.\n  3. **Seau à Jetons (*Token Bucket*)** : Un seau virtuel contient `N` jetons et se recharge à vitesse constante (ex: 1 jeton toutes les 5 secondes). Autorise de courts pics de trafic (*bursts*) tout en limitant la moyenne.",
                "**Les En-têtes HTTP standards de Rate Limiting** : Une API professionnelle informe toujours le client de l'état de son quota :\n  - `X-RateLimit-Limit: 3` (plafond autorisé par fenêtre)\n  - `X-RateLimit-Remaining: 1` (requêtes restantes avant blocage)\n  - `Retry-After: 18` (nombre exact de secondes à attendre avant de réessayer lorsque le statut `429` est déclenché)."
            ],
            "code": _read("03_rate_limiting_429.py"),
            "line_explanations": [
                {"lines": "10-12", "text": "Définit la politique : maximum `3` requêtes sur une fenêtre glissante de `20` secondes par adresse IP."},
                {"lines": "20", "text": "Liste en compréhension filtrant uniquement les horodatages datant de moins de 20 secondes."},
                {"lines": "23-34", "text": "Si le quota est atteint (`>= 3`), calcule le temps d'attente exact et renvoie `429 Too Many Requests` avec `Retry-After`."},
                {"lines": "37-44", "text": "Enregistre l'horodatage courant et renseigne `X-RateLimit-Limit` et `X-RateLimit-Remaining`."}
            ],
            "sandbox_preset": {
                "label": "Tester le Rate Limiter (Cliquez 4 fois !) : GET /api/sandbox/ratelimit-demo",
                "method": "GET",
                "url": "/api/sandbox/ratelimit-demo",
                "body": ""
            },
            "python_runner": {
                "prompt": "Comparez le comportement du limiteur à Fenêtre Glissante sur une rafale d'appels :",
                "initial_code": '''LIMITE = 3
FENETRE = 20
historique = []

def simuler_requete(instant_seconde):
    global historique
    # Purge des appels plus anciens que 20 secondes
    historique = [t for t in historique if instant_seconde - t < FENETRE]
    if len(historique) >= LIMITE:
        retry_after = FENETRE - (instant_seconde - historique[0])
        print(f"[t={instant_seconde:02d}s] -> HTTP 429 Too Many Requests (Retry-After: {retry_after}s)")
        return
    historique.append(instant_seconde)
    restant = LIMITE - len(historique)
    print(f"[t={instant_seconde:02d}s] -> HTTP 200 OK (X-RateLimit-Remaining: {restant})")

# Rafale à t=1s, 2s, 3s, 4s puis nouvel essai à t=22s
for t in [1, 2, 3, 4, 22]:
    simuler_requete(t)'''
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
            "title": "4.6 — Sécurité Périmétrique : CORS, Signatures de Webhooks (`HMAC-SHA256`) & Protection `413`",
            "duration": "55 min",
            "analogy": {
                "title": "L'API inversée (Webhook) et le contrôle des origines (CORS)",
                "text": "Jusqu'ici, c'est toujours le client qui interrogeait notre serveur. Mais comment être prévenu en temps réel lorsqu'un paiement bancaire est validé chez un prestataire externe (CIB / Edahabia / Stripe) ? Au lieu d'interroger la banque toutes les secondes (*Polling*), c'est la banque qui envoie une requête `POST` automatique vers notre serveur dès que l'événement survient : c'est un **Webhook** (ou *Callback HTTP*)."
            },
            "explanation": [
                "**Authentifier un Webhook entrant par Signature `HMAC-SHA256`** : Puisque l'URL de votre Webhook (`POST /api/webhooks/paiement`) est accessible sur Internet, comment être certain que la requête provient réellement de votre partenaire bancaire et non d'un pirate qui simule un paiement réussi ?\n  1. Le partenaire calcule une empreinte `HMAC-SHA256` sur les octets bruts du corps JSON (`request.get_data()`) avec un secret partagé (`WEBHOOK_SECRET`).\n  2. Il place cette empreinte dans l'en-tête `X-Webhook-Signature: sha256=...`.\n  3. Votre serveur recalcule le HMAC sur les octets reçus et compare les deux signatures avec `hmac.compare_digest`.",
                "**Comprendre CORS (*Cross-Origin Resource Sharing*)** : Par sécurité, les navigateurs web interdisent à un site `https://site-a.com` de lire les réponses d'une API située sur `https://api-b.com`, sauf si l'API renvoie explicitement l'en-tête `Access-Control-Allow-Origin: https://site-a.com`. Attention : ne mettez jamais `*` (*wildcard*) sur une API privée !",
                "**Protection contre la saturation mémoire (`413 Payload Too Large`)** : En configurant `app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024` (1 Mo), Flask rejette immédiatement avec le code `413` toute tentative d'envoi d'un corps JSON géant visant à saturer la RAM du serveur."
            ],
            "code": _read("05_cors_webhooks_headers.py"),
            "line_explanations": [
                {"lines": "14", "text": "`MAX_CONTENT_LENGTH` plafonne la taille du corps HTTP entrant à 1 Mo (protection anti-DoS mémoire)."},
                {"lines": "20-30", "text": "Hook `@app.after_request` appliquant la liste blanche CORS et les en-têtes de sécurité (`X-Content-Type-Options: nosniff`, `Cache-Control: no-store`)."},
                {"lines": "35-46", "text": "Vérifie la signature `HMAC-SHA256` calculée sur les octets bruts du corps (`request.get_data()`) avant de traiter l'événement Webhook."}
            ],
            "python_runner": {
                "prompt": "Simulez l'émission d'un Webhook signé par un partenaire bancaire et sa vérification par votre API :",
                "initial_code": '''import hmac
import hashlib
import json

WEBHOOK_SECRET = "whsec_isgp_partenaire_2026"

# 1. Le partenaire bancaire prépare l'événement JSON et le signe en HMAC-SHA256
evenement = {"evenement": "paiement.reussi", "facture_id": "FAC-2026-089", "montant_dzd": 45000}
corps_octets = json.dumps(evenement).encode("utf-8")

signature_emetteur = "sha256=" + hmac.new(
    WEBHOOK_SECRET.encode("utf-8"), corps_octets, hashlib.sha256
).hexdigest()

print("Corps brut envoyé :", corps_octets.decode("utf-8"))
print("En-tête X-Webhook-Signature :", signature_emetteur)

# 2. Votre serveur API recalcule la signature à la réception
signature_attendue = "sha256=" + hmac.new(
    WEBHOOK_SECRET.encode("utf-8"), corps_octets, hashlib.sha256
).hexdigest()

est_authentique = hmac.compare_digest(signature_emetteur, signature_attendue)
print("Webhook authentifié avec succès :", est_authentique)'''
            },
            "vscode_instructions": {
                "filename": "day_4/05_cors_webhooks_headers.py",
                "steps": [
                    "Ouvrir `day_4/05_cors_webhooks_headers.py` dans l'éditeur.",
                    "Observer comment `request.get_data()` récupère les octets bruts exacts pour calculer le HMAC-SHA256."
                ]
            }
        }
    ]
}
