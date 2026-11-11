"""
Manuel de Référence Approfondi — Volume II : FastAPI, ASGI & Pydantic v2 (Jours 4 et 5).
Ouvrage d'ingénierie logicielle couvrant :
- context : problématique architecturale et enjeux de production
- deep_sections : monographies techniques approfondies (Cryptographie, JWT/JWS, OAuth2/RBAC/BOLA, Rate Limiting, CORS/Webhooks, Cookies, Résilience httpx, APIRouter/RFC 8594, OpenAPI 3.1, Keyset Pagination)
- architecture_diagram : topologie mémoire ou trame réseau ASCII
- reference_table : matrice de synthèse normative
- pitfalls : anti-patterns de production vs standards industriels
- practical_exercises : travaux pratiques progressifs post-bootcamp
"""

ENRICHMENT_D4_D5 = {
    # =========================================================================
    # JOUR 4 — CHAPITRE 4.1 : CRYPTOGRAPHIE APPLIQUÉE, VARIABLES D'ENVIRONNEMENT & API KEYS
    # =========================================================================
    "d4-l1": {
        "context": (
            "Dès qu'un service FastAPI quitte le périmètre d'un bac à sable local pour gérer des dossiers administratifs, "
            "des flux financiers ou des inscriptions certifiantes, chaque route exposée sur le réseau devient une cible "
            "potentielle d'énumération et d'intrusion automatisée.\n\n"
            "Or, l'analyse post-mortem des incidents de sécurité majeurs en entreprise révèle que la compromission "
            "provient rarement d'une faille mathématique dans AES ou SHA-256, mais presque toujours de trois erreurs "
            "d'architecture élémentaires : confondre **encodage de transport** (`Base64`), **dérivation irréversible** "
            "(`PBKDF2` / `scrypt` / `Argon2id`) et **chiffrement** ; commiter des clés secrètes en clair dans "
            "l'historique Git ; ou comparer deux secrets avec l'opérateur Python `==`, exposant le serveur aux "
            "**attaques par canal auxiliaire temporel (*Timing Side-Channel Attacks*)**. Ce chapitre établit le socle "
            "cryptographique rigoureux exigé de tout ingénieur backend."
        ),
        "deep_sections": [
            {
                "heading": "1. Taxonomie formelle : Encodage, Hachage rapide, Dérivation salée lente, Chiffrement et HMAC",
                "body": (
                    "Quatre primitives distinctes interviennent quotidiennement dans l'architecture d'une API et ne "
                    "doivent jamais être substituées l'une à l'autre. L'**encodage (`Base64`, `Base64URL`, `UTF-8`)** "
                    "ne procure **strictement aucune confidentialité** : il s'agit d'une bijection publique traduisant "
                    "des octets arbitraires en caractères ASCII imprimables afin qu'ils traversent sans altération un "
                    "en-tête HTTP ou un champ JSON. Quiconque intercepte une chaîne Base64 la décode en une "
                    "microseconde sans aucune clé.\n\n"
                    "Le **hachage cryptographique rapide (`SHA-256` via `hashlib.sha256`)** est une fonction à sens "
                    "unique déterministe projetant une entrée quelconque vers une empreinte fixe de 256 bits (64 "
                    "chiffres hexadécimaux). S'il convient parfaitement pour vérifier l'intégrité d'une archive ou "
                    "stocker l'empreinte d'une clé d'API à très haute entropie aléatoire (256 bits tirés via "
                    "`secrets.token_urlsafe(32)`), il est **dangereusement trop rapide pour un mot de passe humain** : "
                    "une grappe de processeurs graphiques (GPU) évalue plusieurs dizaines de milliards de condensats "
                    "SHA-256 par seconde et épuise instantanément les dictionnaires courants.\n\n"
                    "#### Dérivation de clé salée (`PBKDF2-HMAC` / `scrypt`) et authentification de message (`HMAC`)\n\n"
                    "Pour protéger un mot de passe choisi par un humain, la norme NIST SP 800-63B impose d'adjoindre un "
                    "**sel aléatoire unique** de 16 octets par utilisateur (`secrets.token_bytes(16)` — ce qui neutralise "
                    "toute table précalculée *Rainbow Table*) et d'appliquer une **fonction de dérivation volontairement "
                    "coûteuse en CPU et en mémoire** telle que `hashlib.scrypt` ou `hashlib.pbkdf2_hmac('sha256', ..., "
                    "600_000)` (ou `Argon2id` en production). Enfin, le **code d'authentification `HMAC-SHA256`** "
                    "combine un message et une **clé secrète serveur** pour produire un sceau d'intégrité infalsifiable "
                    "sans cette clé, tandis que le **chiffrement symétrique authentifié (`AES-GCM`, `Fernet`)** demeure "
                    "seul réversible par le détenteur de la clé de déchiffrement."
                )
            },
            {
                "heading": "2. Méthodologie Twelve-Factor App (Facteur III) : isolation des secrets hors du dépôt Git",
                "body": (
                    "Un dépôt Git conserve par conception la mémoire immuable de chaque ligne ayant existé depuis "
                    "l'initialisation du projet. Inscrire `API_SECRET_KEY = \"isgp-prod-9f8a...\"` dans un module "
                    "Python puis le supprimer dans un commit ultérieur ne répare rien : une simple commande "
                    "`git log -S API_SECRET_KEY -p` restitue le secret en clair à tout développeur, prestataire ou "
                    "robot d'intégration continue ayant accès au code.\n\n"
                    "> « La configuration d'une application — en particulier ses identifiants et clés cryptographiques — varie selon chaque déploiement et doit être strictement séparée du code dans les variables d'environnement. » — The Twelve-Factor App, Facteur III (Config)\n\n"
                    "En production sous Linux, Docker ou Kubernetes, les secrets sont injectés exclusivement au lancement "
                    "du processus Uvicorn et lus en Python via `os.environ[\"API_SECRET_KEY\"]` (ou validés au démarrage "
                    "par `pydantic-settings`), en refusant catégoriquement de démarrer le serveur si la variable est "
                    "absente hors mode développement."
                )
            },
            {
                "heading": "3. Authentification M2M par `Header(alias=\"X-API-Key\")` et temps constant `hmac.compare_digest`",
                "body": (
                    "Pour les intégrations machine-à-machine (*M2M*) entre deux serveurs institutionnels, l'authentification "
                    "par clé d'API transmise dans l'en-tête HTTP `X-API-Key` constitue un patron sobre et robuste, "
                    "encapsulé dans FastAPI par une dépendance `Depends(verifier_api_key)`. Cette clé ne doit **jamais "
                    "figurer dans la Query String** (`?api_key=...`), car les URLs complètes sont journalisées en clair "
                    "dans les fichiers `access.log` des proxys Nginx, des CDN et des sondes réseau.\n\n"
                    "> [!WARNING] Faille par canal auxiliaire : pourquoi `==` trahit vos secrets octet par octet\n"
                    "> En CPython, l'opérateur `a == b` exécute une boucle C (`memcmp` / comparaison préfixe) qui **s'arrête dès le premier octet divergent**. Un attaquant soumettant des milliers de requêtes et mesurant statistiquement le temps de réponse à la nanoseconde identifie l'octet `0` qui retarde légèrement l'échec, puis l'octet `1`, réduisant une recherche exponentielle impossible en une progression linéaire triviale !\n\n"
                    "```python — Dépendance FastAPI résistante aux attaques temporelles (Constant-Time)\n"
                    "import hmac, os\n"
                    "from fastapi import Depends, Header, HTTPException\n\n"
                    "def verifier_api_key(x_api_key: str = Header(..., alias=\"X-API-Key\")) -> str:\n"
                    "    attendu = os.environ.get(\"PARTNER_API_KEY\", \"dev-only-fallback-key\")\n"
                    "    if not hmac.compare_digest(x_api_key.encode(\"utf-8\"), attendu.encode(\"utf-8\")):\n"
                    "        raise HTTPException(status_code=401, detail=\"Clé d'API invalide\")\n"
                    "    return \"partenaire-certifie\"\n"
                    "```\n\n"
                    "La primitive `hmac.compare_digest` parcourt systématiquement tous les octets au moyen d'opérations "
                    "bit-à-bit `XOR` et `OR` sans aucun branchement conditionnel anticipé, rendant le temps CPU "
                    "indépendant de la position de l'erreur."
                )
            }
        ],
        "architecture_diagram": (
            "FLUX DE VÉRIFICATION D'IDENTITÉ MACHINE (X-API-KEY) & MOT DE PASSE SALÉ\n"
            "========================================================================\n\n"
            "  [1] VÉRIFICATION D'UNE CLÉ D'API EN TEMPS CONSTANT :\n"
            "  Client HTTP                                     Serveur FastAPI (Depends)\n"
            "  En-tête : X-API-Key: isgp-live-98a7...  ----->  x_api_key: str = Header(alias='X-API-Key')\n"
            "                                                  cle_serveur = os.environ.get('PARTNER_API_KEY')\n"
            "                                                        |\n"
            "                                                  hmac.compare_digest(x_api_key, cle_serveur)\n"
            "                                                  (Durée d'exécution constante : 0 fuite temporelle)\n\n"
            "  [2] STOCKAGE IRRÉVERSIBLE D'UN MOT DE PASSE UTILISATEUR (PBKDF2 / SCRYPT) :\n"
            "  Mot de passe clair : \"Formation2026!\"\n"
            "        +\n"
            "  Sel aléatoire (16 octets) : \"8f3d9a1c...\"\n"
            "        |\n"
            "        v  (600 000 itérations de hachage SHA-256)\n"
            "  Empreinte stockée en BDD : \"pbkdf2:sha256:600000$8f3d9a1c$e4b9012f8a...\" (Irréversible)"
        ),
        "reference_table": {
            "title": "Comparatif des Mécanismes Cryptographiques en Architecture API",
            "headers": ["Mécanisme Cryptographique", "Réversibilité", "Clé Secrète Requise ?", "Fonction Python Standard", "Cas d'Usage en Architecture API"],
            "rows": [
                ["Encodage Base64", "Oui (immédiate, publique)", "Non", "`base64.urlsafe_b64encode()`", "Transport de données binaires ou JSON dans un en-tête HTTP"],
                ["Hachage rapide (SHA-256)", "Non (irréversible)", "Non", "`hashlib.sha256(data).hexdigest()`", "Empreinte d'intégrité d'un fichier ou d'une clé d'API haute entropie"],
                ["Hachage lent salé (PBKDF2 / Scrypt)", "Non (irréversible + lent)", "Non (Sel aléatoire inclus)", "`hashlib.pbkdf2_hmac('sha256', ...)`", "Stockage sécurisé des mots de passe humains en base de données"],
                ["Signature HMAC-SHA256", "Non (vérification par recalcul)", "Oui (Clé secrète serveur)", "`hmac.new(key, msg, hashlib.sha256)`", "Signature de jetons JWT/Bearer et authentification de Webhooks"],
                ["Comparaison à temps constant", "N/A (Opérateur booléen)", "N/A", "`hmac.compare_digest(val1, val2)`", "Comparaison sécurisée de deux secrets (contre les Timing Attacks)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Stocker les mots de passe avec `hashlib.md5()` ou `sha256()` sans sel",
                "good": "Utiliser une fonction de dérivation lente avec salage automatique (`hashlib.pbkdf2_hmac`, `hashlib.scrypt` ou `Argon2id`)",
                "why": "Les cartes graphiques (GPU) calculent plus de 50 milliards d'empreintes SHA-256 par seconde et cassent les mots de passe courants instantanément sans sel ni itérations lentes."
            },
            {
                "bad": "Passer la clé d'API dans les paramètres de requête URL (`GET /api/rapports?api_key=secret123`)",
                "good": "Transmettre systématiquement les clés et jetons dans les en-têtes HTTP (`Header(alias='X-API-Key')` ou `Authorization`)",
                "why": "Les URLs complètes sont archivées en clair dans les fichiers `access.log` de tous les serveurs mandataires et dans l'historique navigateur."
            },
            {
                "bad": "Écrire `SECRET_KEY = 'mon_secret_de_prod'` directement dans `app.py` et pousser sur Git",
                "good": "Lire les secrets exclusivement depuis l'environnement système via `os.environ.get('API_SECRET_KEY')`",
                "why": "Tout secret commité dans Git reste lisible indéfiniment dans l'historique `git log -p` même après suppression."
            }
        ],
        "practical_exercises": [
            "Calculez deux empreintes successives du même mot de passe `\"Bootcamp2026\"` en tirant à chaque fois un nouveau sel de 16 octets via `secrets.token_bytes(16)` avec `hashlib.pbkdf2_hmac('sha256', ...)` : vérifiez que les deux empreintes diffèrent totalement tout en restant vérifiables lorsqu'on conserve le sel associé.",
            "Construisez un dictionnaire serveur associant trois condensats SHA-256 de clés d'API à trois noms d'institutions partenaires, puis écrivez une dépendance FastAPI `Depends` identifiant en temps constant quel partenaire interroge `/api/v1/partenaire/commandes`."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.2 : JETONS SIGNÉS (BEARER TOKENS / JWT) & EXPIRATION
    # =========================================================================
    "d4-l2": {
        "context": (
            "Lorsqu'un usager s'authentifie depuis une application mobile native ou une interface monopage React/Vue, "
            "exiger la saisie ou la conservation locale de son mot de passe pour chaque requête ultérieure serait une "
            "hérésie ergonomique et sécuritaire.\n\n"
            "Les applications Web monolithiques résolvaient jadis ce besoin par des **sessions avec état (*Stateful "
            "Sessions*)** stockées dans la RAM du serveur. Mais dès qu'une API moderne se déploie horizontalement sur "
            "douze ou cinquante conteneurs FastAPI derrière un répartiteur de charge, synchroniser une table de "
            "sessions à chaque requête introduit un point unique de défaillance et une latence constante. L'industrie "
            "a par conséquent adopté l'authentification **sans état par Jeton Signé (`Bearer Token` / `JWT` RFC 7519)** : "
            "à l'issue d'un unique contrôle des identifiants sur `POST /api/auth/token`, le serveur délivre au client "
            "un **titre d'identité auto-porteur, horodaté et scellé par HMAC**."
        ),
        "deep_sections": [
            {
                "heading": "1. Structure cryptographique d'un jeton signé (`Header.Payload.Signature` / JWS RFC 7515)",
                "body": (
                    "Qu'il s'agisse d'un **JWT (*JSON Web Token*, IETF RFC 7519)** normalisé ou d'un jeton horodaté "
                    "`URLSafeTimedSerializer` (`itsdangerous`), le principe mathématique demeure identique : assembler "
                    "des segments encodés en **Base64URL** (variante de Base64 remplaçant `+` et `/` par `-` et `_` "
                    "sans remplissage `=` pour circuler intact dans tout en-tête HTTP) séparés par le caractère `.`.\n\n"
                    "Le premier segment (**`Header`**) déclare l'algorithme cryptographique employé (typiquement `HS256` "
                    "pour HMAC-SHA256 ou `RS256` pour une signature asymétrique RSA). Le segment central (**`Payload`**) "
                    "transporte les **revendications (*Claims*)** normalisées de l'utilisateur : `sub` (*Subject*, "
                    "identifiant unique du porteur), `role` ou `scopes`, `iat` (*Issued At*, seconde Unix d'émission) "
                    "et `exp` (*Expiration Time*, échéance impérative de validité). Le segment final (**`Signature`**) "
                    "résulte du calcul `HMAC_SHA256(Base64URL(Header) + \".\" + Base64URL(Payload), SECRET_KEY)`, que "
                    "seuls les workers détenteurs de `SECRET_KEY` en mémoire vive peuvent produire ou certifier."
                )
            },
            {
                "heading": "2. L'axiome de transparence : un jeton signé est LISIBLE par tous, mais INFALSIFIABLE (`Signé != Chiffré`)",
                "body": (
                    "La confusion entre signature d'intégrité (**JWS**) et chiffrement de confidentialité (**JWE**) "
                    "constitue l'une des erreurs les plus lourdes en audit de sécurité.\n\n"
                    "> [!IMPORTANT] Transparence totale du Payload Base64URL\n"
                    "> Le `Payload` d'un jeton JWT ou `itsdangerous` n'est **pas chiffré** : n'importe quel développeur, proxy ou script exécutant `base64.urlsafe_b64decode()` lit instantanément `{\"sub\": \"amine\", \"role\": \"lecteur\"}` en clair sans posséder la moindre clé ! Ne glissez **jamais** de mot de passe, de secret métier ou de donnée personnelle sensible dans les *claims* d'un jeton.\n\n"
                    "Si tout le monde peut lire le jeton, qu'est-ce qui empêche un utilisateur malveillant de décoder "
                    "son propre jeton, d'y remplacer `\"role\": \"lecteur\"` par `\"role\": \"admin\"`, puis de le "
                    "ré-encoder en Base64URL ? **L'effet d'avalanche du sceau HMAC-SHA256** : la modification d'un seul "
                    "bit du `Payload` bouleverse radicalement les 256 bits du condensat attendu par le serveur. "
                    "Dépourvu de `SECRET_KEY`, l'attaquant est mathématiquement incapable de calculer la nouvelle "
                    "signature correspondante, et le serveur rejette sa requête à la microseconde par `BadSignature` (`401`)."
                )
            },
            {
                "heading": "3. Protocole de transport RFC 6750 (`Authorization: Bearer`) et hiérarchie d'exceptions temporelles",
                "body": (
                    "La norme **IETF RFC 6750** régit le transport des jetons d'accès dans l'en-tête HTTP "
                    "`Authorization: Bearer <token>`. L'adjectif anglais *Bearer* (« au porteur », comme un billet de "
                    "banque) rappelle que la simple détention du jeton vaut preuve d'identité — ce qui rend le "
                    "chiffrement de transport **HTTPS/TLS** non négociable en production.\n\n"
                    "```http — Présentation normée d'un jeton au porteur selon la RFC 6750\n"
                    "GET /api/v1/auth/profil HTTP/1.1\n"
                    "Host: api.isgp.dz\n"
                    "Authorization: Bearer eyJzdWIiOiJhbWluZSIsInJvbGUiOiJhZG1pbiJ9.Z5x8pA.9k2LmQ...\n"
                    "```\n\n"
                    "Dans FastAPI, le schéma `HTTPBearer()` combiné à `Depends()` extrait automatiquement le jeton, "
                    "alimente le bouton cadenas d'OpenAPI 3.1 et passe la chaîne au vérificateur cryptographique. Lors "
                    "de l'appel à `serializer.loads(token, max_age=900)`, retenez une subtilité d'héritage Python "
                    "essentielle : **`SignatureExpired` hérite de `BadSignature`**. Il faut donc toujours intercepter "
                    "`except SignatureExpired:` **en premier** afin de restituer un diagnostic d'expiration précis au "
                    "client mobile (qui déclenchera alors son flux de rafraîchissement automatique), avant le bloc "
                    "`except BadSignature:` qui signale une altération frauduleuse."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE VIE D'UN JETON SIGNÉ STATELESS (BEARER TOKEN / JWT)\n"
            "============================================================\n\n"
            "  [ÉTAPE 1 : CONNEXION INITIALE (POST /api/auth/token)]\n"
            "  Client Mobile / Web                              Serveur FastAPI (Stateless)\n"
            "  {\"identifiant\": \"amine\", \"mot_de_passe\": \"...\"} -> 1. Vérifie le mot de passe (compare_digest)\n"
            "                                                   2. Crée Payload {\"sub\": \"amine\", \"role\": \"admin\"}\n"
            "                                                   3. Signe avec SECRET_KEY + Timestamp actuel\n"
            "  Stocke le token en mémoire               <-----  200 OK : {\"access_token\": \"eyJ...Signature\"}\n\n"
            "  [ÉTAPE 2 : REQUÊTE SUR ROUTE PROTÉGÉE (GET /api/auth/profil)]\n"
            "  En-tête HTTP :\n"
            "  Authorization: Bearer eyJ...Signature     -----> 1. Depends(verifier_bearer_token) extrait le token\n"
            "                                                   2. Recalcule HMAC(Payload, SECRET_KEY)\n"
            "                                                   3. Vérifie Horodatage <= max_age\n"
            "  Reçoit les données métier                <-----  200 OK (Aucune requête SQL de session requise !)"
        ),
        "reference_table": {
            "title": "États de Validation d'un Jeton Signé (`Bearer Token`)",
            "headers": ["Scénario de Vérification du Jeton", "Exception Levée (`itsdangerous`)", "Code HTTP Standard", "Cause Technique Exacte", "Action Attendue du Client"],
            "rows": [
                ["En-tête `Authorization` absent ou sans préfixe `Bearer `", "Aucune (rejet pré-vérification)", "`401 Unauthorized`", "Le client n'a fourni aucune preuve d'identité valide", "Rediriger vers l'écran de connexion (`/api/login`)"],
                ["Signature valide et âge <= `max_age`", "Aucune (Succès)", "`200 OK`", "Jeton authentique, intègre et non expiré", "Exploiter la réponse JSON normalement"],
                ["Signature valide mais âge > `max_age`", "`SignatureExpired`", "`401 Unauthorized`", "Le jeton a dépassé sa durée de vie autorisée", "Utiliser le `refresh_token` ou demander une reconnexion"],
                ["Payload modifié ou signé avec une mauvaise clé", "`BadSignature`", "`401 Unauthorized`", "Tentative de falsification du Payload ou rotation de `SECRET_KEY`", "Purger le jeton local et forcer la reconnexion"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Stocker des informations confidentielles (mot de passe, clé interne) dans le Payload d'un jeton signé",
                "good": "Ne stocker dans le Payload que les identifiants publics nécessaires au contrôle d'accès (`sub`, `role`, `scopes`)",
                "why": "Un jeton signé est encodé en Base64URL et non chiffré : quiconque possède le jeton peut lire son Payload en clair sans clé."
            },
            {
                "bad": "Émettre des jetons sans date d'expiration (ou valables 1 an)",
                "good": "Imposer une durée de vie courte sur les jetons d'accès (`max_age=900` à `3600` secondes)",
                "why": "Un jeton Stateless ne pouvant pas être annulé sans état serveur, limiter sa durée de vie réduit la fenêtre d'exposition en cas d'interception."
            },
            {
                "bad": "Placer `except BadSignature:` avant `except SignatureExpired:` dans le bloc `try / except`",
                "good": "Toujours placer `except SignatureExpired:` **avant** `except BadSignature:`",
                "why": "`SignatureExpired` est une sous-classe de `BadSignature` ; si `BadSignature` est testé en premier, il capture aussi les jetons expirés."
            }
        ],
        "practical_exercises": [
            "Récupérez un jeton émis par `POST /api/auth/token`, altérez un unique caractère de son segment central, puis soumettez-le dans `Authorization: Bearer ...` afin d'observer la détection immédiate de falsification.",
            "Enrichissez la route protégée pour retourner également le temps de validité restant en secondes en exploitant `return_timestamp=True` sur `serializer.loads()`."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.3 : AUTHENTIFICATION (AUTHN / 401) VS AUTORISATION (AUTHZ / 403, RBAC, SCOPES, BOLA)
    # =========================================================================
    "d4-l3": {
        "context": (
            "En sécurité des systèmes distribués, l'amalgame entre **Authentification (`AuthN`)** et **Autorisation "
            "(`AuthZ`)** engendre la vulnérabilité numéro un mondiale recensée par l'**OWASP API Security Top 10 "
            "(API1:2023)** : *Broken Object Level Authorization (`BOLA` / `IDOR`)*, talonnée par *Broken Function "
            "Level Authorization (`BFLA`)*.\n\n"
            "D'innombrables APIs vérifient scrupuleusement la signature cryptographique du jeton entrant (`AuthN`), "
            "puis exécutent aveuglément `SELECT * FROM bulletins WHERE id = ?` sans jamais contrôler si le porteur "
            "légitime de ce jeton détient le **droit métier (`AuthZ`)** de lire ce dossier précis ! Ce chapitre trace "
            "une frontière chirurgicale entre la preuve d'identité (`401`) et l'habilitation d'accès (`403`) à travers "
            "le graphe de dépendances `Depends()` de FastAPI : **RBAC**, **Scopes OAuth2** et **Propriété d'objet "
            "(Anti-BOLA)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Sémantique RFC 9110 : `401 Unauthorized` (Identité défaillante) face à `403 Forbidden` (Droits insuffisants)",
                "body": (
                    "Bien que la RFC 9110 ait conservé pour des raisons historiques le libellé anglais trompeur "
                    "`401 Unauthorized`, sa définition normative désigne strictement un échec d'**Authentification "
                    "(`AuthN` — « Qui êtes-vous ? »)** : l'appelant n'a présenté aucun titre d'identité, son jeton a "
                    "expiré ou sa signature HMAC est invalide. Accompagné de l'en-tête obligatoire `WWW-Authenticate: "
                    "Bearer`, le code `401` invite le client à se ré-authentifier ou à rafraîchir son jeton.\n\n"
                    "À l'opposé, le code **`403 Forbidden`** scelle un refus d'**Autorisation (`AuthZ` — « Avez-vous "
                    "le droit d'accomplir ce geste sur cette cible ? »)** : le serveur a **parfaitement reconnu "
                    "l'identité** de l'appelant (`yasmine`, stagiaire connectée), mais sa politique de sécurité lui "
                    "interdit la ressource convoitée. Renvoyer `401` au lieu de `403` dégrade gravement les applications "
                    "frontales, qui croient leur jeton expiré et bouclent indéfiniment sur `/auth/refresh` !"
                )
            },
            {
                "heading": "2. Défense en profondeur : la triade RBAC, Scopes OAuth2 et Propriété de Ressource (Anti-BOLA)",
                "body": (
                    "Une gouvernance d'autorisation mature superpose trois filtres orthogonaux dont chacun pare une "
                    "classe d'attaque distincte. Le premier filtre, **RBAC (*Role-Based Access Control*)**, partitionne "
                    "les fonctionnalités macroscopiques selon le statut organisationnel du sujet (`etudiant`, "
                    "`formateur`, `admin`), bloquant par exemple toute route d'administration globale (`BFLA`).\n\n"
                    "Le deuxième filtre, les **Scopes OAuth2 (`SecurityScopes`)**, régit la **délégation à moindre "
                    "privilège** : lorsqu'un administrateur génère un jeton pour un automate d'export comptable, il ne "
                    "lui confère que la permission granulaire `factures:read` sans `factures:write` ni `users:delete` ; "
                    "si ce script est compromis, l'attaquant ne dispose pas des pleins pouvoirs du compte parent.\n\n"
                    "> [!WARNING] OWASP API1:2023 — Broken Object Level Authorization (`BOLA` / `IDOR`)\n"
                    "> Passer avec succès le contrôle RBAC (`role == 'etudiant'`) et le contrôle de Scope (`bulletins:read`) ne suffit **jamais** lorsqu'une route contient un identifiant d'entité tel que `GET /api/v1/bulletins/{etudiant_id}` ! Si le code omet de vérifier en base ou dans le contexte que `current_user['sub'] == etudiant_id` (sauf dérogation explicite `admin`), l'étudiant `yasmine` peut itérer par script sur tous les identifiants de l'école et aspirer l'intégralité des relevés de notes confidentiels."
                )
            },
            {
                "heading": "3. Orchestration par Graphe Orienté Acyclique (DAG) dans FastAPI (`Depends` & `Security`)",
                "body": (
                    "L'un des joyaux architecturaux de FastAPI réside dans son moteur d'injection de dépendances capable "
                    "de résoudre automatiquement un **graphe orienté acyclique (DAG)** de contrôles de sécurité avant "
                    "même d'invoquer la route métier.\n\n"
                    "```python — Chaînage déclaratif AuthN (401) -> AuthZ Scopes/RBAC (403) -> Anti-BOLA\n"
                    "def exiger_scope(scope_requis: str):\n"
                    "    def verifier_authz(user: dict = Depends(verifier_authn)) -> dict:\n"
                    "        if scope_requis not in user.get(\"scopes\", []):\n"
                    "            raise HTTPException(status_code=403, detail=f\"Scope manquant : {scope_requis}\")\n"
                    "        return user\n"
                    "    return verifier_authz\n\n"
                    "@app.get(\"/api/v1/bulletins/{proprietaire}\")\n"
                    "def lire_bulletin(proprietaire: str, user: dict = Depends(exiger_scope(\"bulletins:read\"))):\n"
                    "    if user[\"role\"] != \"admin\" and user[\"sub\"] != proprietaire:\n"
                    "        raise HTTPException(status_code=403, detail=\"Accès interdit au dossier d'un tiers (Anti-BOLA)\")\n"
                    "    return {\"titulaire\": proprietaire, \"moyenne\": 16.4}\n"
                    "```\n\n"
                    "Cette composition garantit mathématiquement l'ordre d'évaluation (`verifier_authn` s'exécute "
                    "toujours avant `verifier_authz`), mutualise le résultat en cache pour la requête courante et "
                    "projette les exigences de scopes directement dans le schéma OpenAPI 3.1."
                )
            }
        ],
        "architecture_diagram": (
            "PIPELINE DÉCISIONNEL : AUTHENTIFICATION (401) VS AUTORISATION (403)\n"
            "===================================================================\n\n"
            "  Requête HTTP : DELETE /api/bulletins/karim\n"
            "        |\n"
            "        v\n"
            "  +-------------------------------------------------------------------+\n"
            "  | ÉTAPE 1 : AUTHENTIFICATION (AuthN — Qui est l'appelant ?)         |\n"
            "  | Le jeton Bearer est-il présent, authentique (HMAC) et non expiré ?|\n"
            "  +-------------------------------------------------------------------+\n"
            "        | NON                                     | OUI (ex: sub=\"yasmine\", role=\"etudiant\")\n"
            "        v                                         v\n"
            "  [ 401 UNAUTHORIZED ]            +-------------------------------------------------------------------+\n"
            "  \"Identité inconnue ou expirée.  | ÉTAPE 2 : AUTORISATION (AuthZ — A-t-elle le droit d'agir ?)       |\n"
            "   Veuillez vous authentifier.\"   | 2a. RBAC   : Le rôle est-il autorisé sur cette route ?            |\n"
            "                                  | 2b. SCOPES : Le jeton possède-t-il le scope 'bulletins:write' ?   |\n"
            "                                  | 2c. BOLA   : Est-elle propriétaire ('yasmine' == 'karim') ?       |\n"
            "                                  +-------------------------------------------------------------------+\n"
            "                                        | NON                                     | OUI\n"
            "                                        v                                         v\n"
            "                                  [ 403 FORBIDDEN ]                         [ 200 OK / ACTION EXÉCUTÉE ]\n"
            "                                  \"Identité reconnue (yasmine), mais\n"
            "                                   droits insuffisants pour cet objet.\""
        ),
        "reference_table": {
            "title": "Matrice de Séparation : Authentification (`AuthN`) vs Autorisation (`AuthZ`) vs Anti-BOLA",
            "headers": ["Dimension Comparée", "Authentification (`AuthN`)", "Autorisation (`AuthZ`)", "Protection Anti-BOLA (OWASP #1)"],
            "rows": [
                ["Question posée par le serveur", "« Qui êtes-vous ? Prouvez votre identité. »", "« Avez-vous la permission d'exécuter cette action ? »", "« Cet enregistrement précis vous appartient-il ? »"],
                ["Éléments inspectés", "En-tête `Authorization: Bearer`, signature HMAC, expiration `exp`", "Attributs `role` (RBAC) et `scopes` (OAuth2) du jeton", "Comparaison `token.sub == ressource.owner_id` en base"],
                ["Code HTTP en cas d'échec", "`401 Unauthorized` (+ en-tête `WWW-Authenticate`)", "`403 Forbidden`", "`403 Forbidden` (ou `404` pour masquer l'existence)"],
                ["Action corrective côté client", "Se connecter (`POST /api/login`) ou rafraîchir le jeton", "Demander une élévation de privilèges à l'administrateur", "Aucune : accès illégitime aux données d'un tiers bloqué"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Renvoyer `401 Unauthorized` lorsqu'un utilisateur connecté avec le rôle `etudiant` tente d'accéder à `/api/admin`",
                "good": "Renvoyer `401` uniquement si l'identité est absente/invalide, et `403 Forbidden` si les permissions sont insuffisantes",
                "why": "Les applications frontales interprètent `401` comme une expiration de session et déconnectent l'utilisateur ou bouclent sur `/refresh`."
            },
            {
                "bad": "Masquer le bouton « Supprimer » dans l'interface React/mobile sans vérifier le rôle et le propriétaire côté serveur FastAPI",
                "good": "Appliquer systématiquement les contrôles `AuthZ` (RBAC, Scopes et Anti-BOLA) dans les dépendances et routes Python du serveur",
                "why": "Un attaquant utilise `curl` directement et contourne totalement l'interface graphique du navigateur."
            },
            {
                "bad": "Vérifier que le jeton est valide sur `GET /api/bulletins/{id}` sans vérifier à qui appartient le bulletin `{id}`",
                "good": "Comparer systématiquement `identite['sub'] == bulletin['owner']` (ou `identite['role'] == 'admin'`)",
                "why": "L'absence de contrôle de propriété sur l'objet (BOLA / IDOR) permet à tout utilisateur connecté d'aspirer les dossiers de tous les autres utilisateurs."
            }
        ],
        "practical_exercises": [
            "Éprouvez dans l'atelier ou via `curl` les quatre profils (`anonyme`, `etudiant_lecture`, `formateur_restreint`, `admin_complet`) sur `/api/sandbox/authz-demo` en croisant l'action (`lecture` / `ecriture`) et la cible (`propre_dossier` / `dossier_tiers`).",
            "Rédigez une dépendance ou fonction métier `verifier_acces_document(identite, document)` autorisant la consultation si l'appelant est propriétaire, s'il dirige le même département (`role == 'manager'`), ou s'il est `admin`."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.4 : ROTATION ACCESS / REFRESH TOKENS & FABRIQUE DEPENDS(EXIGER_ROLE)
    # =========================================================================
    "d4-l4": {
        "context": (
            "L'authentification *Stateless* pure étudiée au Chapitre 4.2 confronte l'architecte à une tension "
            "irréductible entre sécurité et ergonomie : si l'`Access Token` demeure valide trente jours pour éviter "
            "de redemander le mot de passe sur mobile, tout vol de jeton ou départ d'un collaborateur laisse une "
            "fenêtre d'intrusion incontrôlable d'un mois entier ; si à l'inverse il expire au bout de dix minutes, "
            "éjecter l'utilisateur vers l'écran de connexion six fois par heure rend l'application inutilisable.\n\n"
            "Le standard **OAuth 2.0 (IETF RFC 6749)** résout élégamment ce dilemme grâce à une **architecture "
            "asymétrique à double jeton** : un **`Access Token` éphémère** (5 à 15 minutes, vérifié en RAM à vitesse "
            "maximale) doublé d'un **`Refresh Token` de longue durée** (7 à 30 jours, confiné au seul renouvellement "
            "et révocable instantanément par liste noire `jti`), le tout factorisé dans FastAPI par des **fabriques "
            "de dépendances paramétrées `Depends(exiger_role(...))`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Séparation cryptographique de domaine : `Access Token` éphémère contre `Refresh Token`",
                "body": (
                    "À l'issue d'une authentification primaire sur `POST /api/v1/auth/login`, le serveur émet une paire "
                    "de jetons aux responsabilités strictement disjointes. L'**`Access Token`** accompagne chaque appel "
                    "métier (`GET /api/v1/formations`, `POST /api/v1/inscriptions`) : sa durée de vie très brève "
                    "(900 secondes) permet aux workers FastAPI de le valider de manière 100 % *Stateless* par simple "
                    "recalcul HMAC en mémoire vive, sans interroger aucune base de données.\n\n"
                    "Le **`Refresh Token`**, doté d'une échéance longue (7 à 30 jours) et d'un identifiant unique de "
                    "jeton **`jti` (*JWT ID*, `uuid4`)**, est quant à lui **interdit de séjour sur toutes les routes "
                    "métier** : son unique prérogative consiste à appeler `POST /api/v1/auth/refresh` lorsque l'`Access "
                    "Token` expire afin d'en obtenir silencieusement un nouveau.\n\n"
                    "> [!IMPORTANT] Cloisonnement cryptographique par sels distincts (`Domain Separation`)\n"
                    "> Si vous signez les deux jetons avec la même clé et le même contexte sans distinction structurelle, un attaquant présentera directement son `Refresh Token` de 30 jours comme `Access Token` sur vos routes métier ! En signant l'un avec `salt=\"access-token-v1\"` (ou `typ=\"access\"`) et l'autre avec `salt=\"refresh-token-v1\"`, toute tentative de substitution échoue instantanément au niveau cryptographique (`BadSignature`)."
                )
            },
            {
                "heading": "2. Révocation temps réel par liste noire (`jti` sous Redis TTL) et Rotation de Refresh Token",
                "body": (
                    "Puisque le `Refresh Token` n'est sollicité qu'une fois toutes les quinze minutes sur un endpoint "
                    "unique, le serveur peut se permettre d'y effectuer une **vérification d'état ultra-légère** sans "
                    "pénaliser les performances globales des routes métier.\n\n"
                    "Lorsqu'un usager presse « Se déconnecter » ou qu'un administrateur suspend un compte compromis, "
                    "l'identifiant `jti` du `Refresh Token` est inscrit dans un magasin clé-valeur en mémoire (**Redis**) "
                    "assorti d'un délai d'auto-destruction (`EXPIRE / TTL`) égal à sa durée de vie résiduelle. Mieux "
                    "encore, les architectures bancaires appliquent la **Rotation automatique des Refresh Tokens "
                    "(RFC 6819 / OAuth 2.1)** : chaque appel à `/auth/refresh` invalide immédiatement le `Refresh Token` "
                    "entrant et délivre un couple `(nouvel_access, nouveau_refresh)` tout neuf ; si un voleur tente "
                    "ensuite de rejouer l'ancien `Refresh Token` déjà consommé, le serveur détecte l'anomalie et "
                    "révoque par sécurité toute la famille de sessions de l'utilisateur !"
                )
            },
            {
                "heading": "3. Fabriques de dépendances paramétrées dans FastAPI : `Depends(exiger_role(\"admin\"))`",
                "body": (
                    "Dans Flask historique, factoriser un contrôle de rôle reposait sur des décorateurs Python manuels "
                    "(`@exiger_role(\"admin\")` enveloppant la fonction avec `@functools.wraps`). Dans FastAPI, écrire "
                    "un décorateur brut autour d'une route est un anti-pattern : FastAPI inspecte la signature exacte "
                    "des paramètres (`inspect.signature`) pour construire le graphe de validation et le contrat OpenAPI.\n\n"
                    "Le patron idiomatique de FastAPI est la **fabrique de dépendances (*Parameterized Dependency "
                    "Factory*)** : une fonction d'ordre supérieur `def exiger_role(*roles_autorises: str):` qui retourne "
                    "une fonction d'injection typée consommée par `Depends(...)`.\n\n"
                    "```python — Fabrique de dépendances réutilisable sur une route ou un APIRouter entier\n"
                    "def exiger_role(*roles_autorises: str):\n"
                    "    def _controleur(identite: dict = Depends(verifier_access_token)) -> dict:\n"
                    "        if identite.get(\"role\") not in roles_autorises:\n"
                    "            raise HTTPException(status_code=403, detail=\"Rôle insuffisant pour cette action\")\n"
                    "        return identite\n"
                    "    return _controleur\n\n"
                    "@app.delete(\"/api/v1/formations/{id}\")\n"
                    "def supprimer(id: int, admin: dict = Depends(exiger_role(\"admin\", \"directeur\"))):\n"
                    "    return {\"supprime\": id, \"operateur\": admin[\"sub\"]}\n"
                    "```"
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE ROTATION ACCESS TOKEN / REFRESH TOKEN & RÉVOCATION\n"
            "===========================================================\n\n"
            "  Client                                      Serveur FastAPI\n"
            "  1. POST /api/auth/login              -----> Vérifie identifiants\n"
            "     Reçoit Access (15m) + Refresh (7j)<----- Signe Access (salt='access') & Refresh (salt='refresh')\n"
            "        |\n"
            "  2. GET /api/formations (Pendant 15m) -----> Depends(exiger_role) vérifie Access Token -> 200 OK\n"
            "        |\n"
            "  3. [16 minutes plus tard : Access Token expiré -> 401 SignatureExpired]\n"
            "        |\n"
            "  4. POST /api/auth/refresh            -----> 1. Vérifie signature avec salt='refresh'\n"
            "     (Envoie le Refresh Token)                2. Vérifie jti NOT IN REFRESH_BLACKLIST\n"
            "     Reçoit un nouvel Access (15m)     <----- 3. Émet un nouvel Access Token frais"
        ),
        "reference_table": {
            "title": "Comparaison Technique : `Access Token` vs `Refresh Token`",
            "headers": ["Propriété Technique", "`Access Token` (Jeton d'accès)", "`Refresh Token` (Jeton de renouvellement)"],
            "rows": [
                ["Durée de vie typique (`max_age`)", "Courte : 5 à 15 minutes (`300` à `900` s)", "Longue : 7 à 30 jours (`604800` à `2592000` s)"],
                ["Sel cryptographique (`salt`)", "`\"access-token-v1\"`", "`\"refresh-token-v1\"` (Empêche l'utilisation croisée)"],
                ["Routes où il est accepté", "Toutes les routes métier protégées (`/api/...`)", "Uniquement `POST /api/auth/refresh` et `/api/auth/revoke`"],
                ["Mode de validation", "100% Stateless (Calcul HMAC en RAM)", "Stateful léger (HMAC + vérification de non-révocation en Redis/BDD)"],
                ["Impact en cas de fuite", "Limité à quelques minutes", "Élevé, mais neutralisable immédiatement par révocation serveur"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Signer l'`Access Token` et le `Refresh Token` avec exactement la même clé et le même `salt` sans champ `type`",
                "good": "Isoler cryptographiquement les deux jetons via des `salt` distincts (`salt='access-v1'` vs `salt='refresh-v1'`)",
                "why": "Sans séparation de sel ou de type, un attaquant pourrait envoyer le `Refresh Token` (valable 30 jours) directement dans `Authorization: Bearer` sur les routes métier."
            },
            {
                "bad": "Écrire un décorateur Python manuel `@mon_decorateur` qui masque la signature des paramètres à FastAPI au lieu d'utiliser `Depends(...)`",
                "good": "Utiliser une fabrique de dépendances `Depends(exiger_role('admin'))` (ou `dependencies=[Depends(...)]` sur `APIRouter`)",
                "why": "Avec `Depends(...)`, FastAPI intègre automatiquement le schéma de sécurité dans OpenAPI (`/docs`), met en cache l'évaluation par requête et permet le remplacement propre en test via `app.dependency_overrides`."
            }
        ],
        "practical_exercises": [
            "Implémentez la **rotation intégrale du Refresh Token** sur `POST /api/auth/refresh` : chaque renouvellement doit inscrire l'ancien `jti` dans `REVOKED_TOKENS` et retourner simultanément un nouvel `Access Token` et un nouveau `Refresh Token`.",
            "Appliquez `dependencies=[Depends(exiger_role(\"admin\"))]` directement au niveau d'un `APIRouter(prefix=\"/api/v1/admin\")` afin de verrouiller d'un seul geste toutes ses routes."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.5 : LIMITATION DE DÉBIT (RATE LIMITING / 429) & QUOTAS
    # =========================================================================
    "d4-l5": {
        "context": (
            "Une API dotée d'une cryptographie irréprochable demeure mortellement vulnérable si elle n'encadre pas sa "
            "**cadence de consommation**. Trois menaces opérationnelles pèsent en permanence sur un service dépourvu "
            "de régulation : l'attaque par force brute ou *Credential Stuffing* pilonnant `POST /api/auth/login` à "
            "raison de cinq mille essais par minute ; le bogue involontaire d'un script partenaire enfermé dans une "
            "boucle `while True:` sans pause qui confisque la boucle ASGI au détriment de tous les autres usagers "
            "(**Déni de Service — DoS**) ; et enfin le risque **FinOps**, lorsqu'une route invoque en aval une "
            "passerelle SMS ou un modèle d'IA facturé au jeton.\n\n"
            "La **limitation de débit (*Rate Limiting*)** constitue la vanne de régulation indispensable qui impose "
            "un budget d'appels par fenêtre temporelle et oppose aux dépassements le contrat normalisé **`429 Too "
            "Many Requests` (IETF RFC 6585)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Algorithmique de régulation : Fenêtre Fixe, Journal Glissant (*Sliding Window Log*) et Seau à Jetons",
                "body": (
                    "Le choix de l'algorithme de comptage détermine la précision de votre protection face aux rafales "
                    "de trafic. L'approche élémentaire dite à **Fenêtre Fixe (*Fixed Window Counter*)** incrémente un "
                    "entier associé à la minute horaire courante (`14:00`, `14:01`). Elle souffre toutefois d'un défaut "
                    "bien connu aux frontières temporelles : sous une limite de 100 requêtes par minute, un client peut "
                    "expédier 100 appels à `14:00:59` puis 100 appels supplémentaires à `14:01:01`, infligeant **200 "
                    "requêtes en deux secondes** à votre base de données.\n\n"
                    "Le **Journal à Fenêtre Glissante (*Sliding Window Log*)** élimine mathématiquement cet angle mort : "
                    "pour chaque clé cliente, le serveur maintient une file FIFO (`collections.deque`) des horodatages "
                    "monotones de ses appels récents. À l'arrivée d'une requête à l'instant `T`, toutes les entrées "
                    "antérieures à `T - fenetre` sont dépilées en tête ; si la longueur restante atteint le plafond "
                    "`quota`, l'appel est rejeté avec une échéance exacte de libération. Enfin, l'algorithme du **Seau "
                    "à Jetons (*Token Bucket*)**, privilégié par NGINX et AWS API Gateway pour son empreinte mémoire "
                    "`O(1)` par client, remplit continûment un réservoir plafonné à `B` jetons (tolérance de rafale "
                    "*burst*) à une vitesse moyenne de `R` jetons par seconde."
                )
            },
            {
                "heading": "2. Signalisation protocolaire coopérative : `X-RateLimit-*` et `Retry-After` (RFC 6585)",
                "body": (
                    "Un limiteur de débit industriel ne se comporte pas comme un pare-feu muet : il expose en continu "
                    "la télémétrie du quota dans les en-têtes HTTP afin que les SDK partenaires ralentissent "
                    "proactivement leur cadence (*Client-Side Throttling*).\n\n"
                    "```http — Réponse normalisée lors d'un dépassement de cadence (RFC 6585)\n"
                    "HTTP/1.1 429 Too Many Requests\n"
                    "Content-Type: application/problem+json\n"
                    "X-RateLimit-Limit: 60\n"
                    "X-RateLimit-Remaining: 0\n"
                    "X-RateLimit-Reset: 15\n"
                    "Retry-After: 15\n"
                    "```\n\n"
                    "Tandis que `X-RateLimit-Limit` et `X-RateLimit-Remaining` accompagnent chaque réponse `200 OK`, "
                    "l'en-tête normatif **`Retry-After`** devient crucial sur toute réponse `429` : il indique le "
                    "nombre exact de secondes pendant lesquelles le client doit suspendre ses émissions avant sa "
                    "prochaine tentative."
                )
            },
            {
                "heading": "3. Clé de partitionnement (`request.client.host` vs `sub`) et atomicité multi-workers sous Redis",
                "body": (
                    "Sur quel discriminant indexer le compteur de débit ? Sur les endpoints anonymes tels que "
                    "`POST /api/v1/auth/login`, la seule ancre disponible est l'adresse IP source (`request.client.host` "
                    "dans FastAPI, ou la première adresse fiable extraite de `X-Forwarded-For` lorsque Uvicorn est lancé "
                    "avec `--proxy-headers` derrière un proxy Nginx de confiance). Gardez cependant à l'esprit le "
                    "phénomène du **NAT partagé** : cinq cents étudiants connectés au Wi-Fi d'un campus universitaire "
                    "sortent souvent sous une unique adresse IPv4 publique ! Dès que la requête est authentifiée, "
                    "indexez par conséquent le quota sur l'identifiant métier (`X-API-Key` ou claim `sub` du Bearer "
                    "Token), ce qui permet en prime d'appliquer des paliers contractuels (`Standard` vs `Entreprise`).\n\n"
                    "> [!WARNING] Piège du multi-processus : un dictionnaire Python local est divisé par `--workers`\n"
                    "> En production, `uvicorn app:app --workers 4` exécute quatre processus OS dotés de mémoires RAM indépendantes. Un dictionnaire Python local autoriserait en réalité `4 x Quota` appels en répartition *round-robin* ! À l'échelle d'un cluster, l'état du limiteur doit être centralisé dans **Redis** via un script Lua atomique (`INCR` + `PEXPIRE` ou `ZREMRANGEBYSCORE`)."
                )
            }
        ],
        "architecture_diagram": (
            "ALGORITHME DE FENÊTRE GLISSANTE (SLIDING WINDOW LOG — QUOTA = 3 REQ / 60s)\n"
            "==========================================================================\n\n"
            "  Instant actuel : T = 100.0s  |  Fenêtre active : [40.0s ---> 100.0s]\n\n"
            "  Historique du client avant nettoyage : [ 25.0s,  55.0s,  80.0s,  92.0s ]\n"
            "                                           ^^^^^\n"
            "  1. Purge des entrées < 40.0s         : Exclut 25.0s -> Reste [ 55.0s, 80.0s, 92.0s ] (Taille = 3)\n"
            "  2. Vérification (Taille >= Quota 3)  : QUOTA ATTEINT !\n"
            "  3. Calcul de Retry-After             : 60 - (100.0 - 55.0) = 15 secondes\n"
            "  4. Réponse HTTP                      : 429 Too Many Requests (Header Retry-After: 15)"
        ),
        "reference_table": {
            "title": "En-têtes HTTP Standards de Limitation de Débit (`Rate Limiting`)",
            "headers": ["En-tête HTTP / Code", "Valeur Exemple", "Présence", "Signification pour le Client Consommateur"],
            "rows": [
                ["Code `429 Too Many Requests`", "`429`", "Uniquement lors du dépassement", "La requête est refusée temporairement pour cause de dépassement de cadence"],
                ["`X-RateLimit-Limit`", "`60`", "Sur toutes les réponses (`200` et `429`)", "Plafond maximal de requêtes autorisées par fenêtre"],
                ["`X-RateLimit-Remaining`", "`0` à `60`", "Sur toutes les réponses (`200` et `429`)", "Nombre d'appels restants avant déclenchement du `429`"],
                ["`Retry-After`", "`15`", "Sur toutes les réponses `429`", "Délai exact en secondes à attendre avant la prochaine tentative"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Renvoyer `500 Internal Server Error` ou `403 Forbidden` lorsqu'un client dépasse sa cadence d'appel",
                "good": "Utiliser le code sémantique dédié `429 Too Many Requests` accompagné de l'en-tête `Retry-After`",
                "why": "Avec `429` et `Retry-After`, les SDK clients savent qu'il s'agit d'une limite temporaire et mettent automatiquement leurs appels en pause."
            },
            {
                "bad": "En production multi-processus (`uvicorn --workers 4`), stocker uniquement le compteur en RAM Python locale",
                "good": "En production distribuée, centraliser les compteurs dans un magasin partagé atomique comme **Redis** ou en amont dans Nginx",
                "why": "Chaque worker Uvicorn ayant sa propre mémoire RAM isolée, un compteur en mémoire locale permettrait au client d'effectuer `4 x Quota` requêtes."
            }
        ],
        "practical_exercises": [
            "Faites évoluer le limiteur de débit du laboratoire pour appliquer un **quota dynamique par offre commerciale** : `5 requêtes/min` lorsque l'en-tête `X-Plan` vaut `standard`, et `20 requêtes/min` lorsqu'il vaut `premium`.",
            "Implémentez une purge mémoire des clés clientes inactives depuis plus d'une fenêtre complète afin d'éviter toute croissance non bornée du dictionnaire `HISTORIQUE_APPELS`."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.6 : SÉCURITÉ PÉRIMÉTRIQUE : CORS, SIGNATURES WEBHOOK HMAC & TAILLE MAXIMALE (413)
    # =========================================================================
    "d4-l6": {
        "context": (
            "Lors du raccordement réel d'une API FastAPI à son écosystème externe, trois mécanismes de défense "
            "périmétrique entrent immédiatement en scène. Premièrement, la gouvernance **CORS (*Cross-Origin Resource "
            "Sharing*)** : pourquoi un endpoint irréprochable sous `curl` est-il soudainement bloqué par Chrome ou "
            "Firefox dès qu'une application React hébergée sur un autre sous-domaine tente de l'interroger ?\n\n"
            "Deuxièmement, l'authentification cryptographique des **Webhooks (`HMAC-SHA256`)** : lorsqu'une passerelle "
            "de paiement (Stripe, Chargily, PayPal) pousse une notification asynchrone vers votre route publique "
            "`POST /api/webhooks/paiement`, comment prouver mathématiquement que l'événement n'a pas été forgé par un "
            "fraudeur ? Troisièmement, le bouclier volumétrique **`413 Content Too Large`** protégeant la mémoire RAM "
            "des workers ASGI contre les charges utiles géantes."
        ),
        "deep_sections": [
            {
                "heading": "1. Politique de même origine (`SOP`), négociation `CORSMiddleware` et requête Preflight `OPTIONS`",
                "body": (
                    "Pour empêcher qu'un site piégé ouvert dans un onglet voisin ne lise silencieusement vos emails ou "
                    "vos comptes bancaires, tous les navigateurs Web appliquent depuis 1995 la **Same-Origin Policy "
                    "(SOP)** : du code JavaScript exécuté sur l'origine `https://portail.isgp.dz` (triplet *schéma + "
                    "hôte + port*) se voit interdire la lecture des réponses émises par une origine distincte telle que "
                    "`https://api.isgp.dz`, sauf autorisation explicite accordée par le serveur cible via les en-têtes "
                    "**CORS (norme W3C / Fetch Living Standard)**.\n\n"
                    "#### Pourquoi `curl` ignore CORS et comment opère le Preflight `OPTIONS`\n\n"
                    "Les outils en ligne de commande (`curl`), Postman ou les microservices Python ne sont **jamais "
                    "soumis à CORS**, car ils ne détiennent pas le trousseau de cookies ni la session navigateur d'un "
                    "citoyen : CORS protège le navigateur de l'utilisateur, il ne remplace jamais l'authentification du "
                    "serveur ! Dès qu'une requête JavaScript `fetch()` utilise `Content-Type: application/json`, un "
                    "verbe mutatif (`PUT`, `DELETE`) ou un en-tête `Authorization`, le navigateur émet au préalable "
                    "une requête automatique **`OPTIONS` (*Preflight*)**. Dans FastAPI, enregistrer `CORSMiddleware` "
                    "avec une liste blanche stricte `allow_origins=[\"https://portail.isgp.dz\"]` répond à ces "
                    "`OPTIONS` en quelques microsecondes.\n\n"
                    "> [!WARNING] Interdiction normative : `allow_origins=[\"*\"]` avec `allow_credentials=True`\n"
                    "> Le standard Fetch interdit aux navigateurs d'accepter le joker universel `Access-Control-Allow-Origin: *` dès lors que la requête transporte des cookies ou en-têtes d'authentification (`credentials: 'include'`). Sur toute API authentifiée, énumérez toujours explicitement les origines autorisées."
                )
            },
            {
                "heading": "2. Inversion événementielle par Webhooks et signature `HMAC-SHA256` sur octets bruts (`await request.body()`)",
                "body": (
                    "Interroger un prestataire bancaire toutes les deux secondes (*Polling*) pour vérifier si un "
                    "étudiant a réglé ses droits gaspille 99 % des appels à vide. L'architecture événementielle inverse "
                    "le flux : dès que le paiement aboutit, le serveur du prestataire émet de lui-même un rappel HTTP "
                    "`POST` — un **Webhook** — vers votre URL d'écoute. Parce que cette URL doit être joignable depuis "
                    "Internet, son authenticité repose intégralement sur une **signature `HMAC-SHA256`** partagée.\n\n"
                    "```python — Vérification cryptographique d'un Webhook sur le flux d'octets exact dans FastAPI\n"
                    "@app.post(\"/api/v1/webhooks/paiement\")\n"
                    "async def recevoir_webhook(request: Request, x_signature: str = Header(..., alias=\"X-Webhook-Signature\")):\n"
                    "    octets_bruts: bytes = await request.body()  # Lecture intacte AVANT tout parsing JSON !\n"
                    "    attendu = \"sha256=\" + hmac.new(WEBHOOK_SECRET.encode(), octets_bruts, hashlib.sha256).hexdigest()\n"
                    "    if not hmac.compare_digest(x_signature, attendu):\n"
                    "        raise HTTPException(status_code=401, detail=\"Signature Webhook falsifiée\")\n"
                    "    evenement = json.loads(octets_bruts)\n"
                    "    return {\"recu\": True, \"id\": evenement[\"id\"]}\n"
                    "```\n\n"
                    "Retenez cette règle d'or absolue : calculez toujours le HMAC sur **`await request.body()`** et "
                    "**jamais** sur `json.dumps(payload_pydantic)`. Le moindre espace ajouté après `:`, une clé "
                    "réordonnée ou un caractère Unicode échappé différemment modifierait l'empreinte SHA-256 et ferait "
                    "rejeter 100 % des notifications légitimes en production ! En outre, associez un horodatage "
                    "`X-Webhook-Timestamp` signé dans le HMAC (tolérance de 5 minutes) pour déjouer toute **attaque par "
                    "rejeu (*Replay Attack*)**."
                )
            },
            {
                "heading": "3. Défense volumétrique mémoire contre les charges géantes (`413 Content Too Large`)",
                "body": (
                    "L'analyse d'un document JSON exige de matérialiser sa représentation en mémoire vive. Sans plafond "
                    "strict, un assaillant ouvrant dix connexions parallèles expédiant chacune 500 Mo de données "
                    "sature instantanément la RAM du conteneur et déclenche l'arrêt brutal des workers Uvicorn par le "
                    "noyau Linux.\n\n"
                    "La défense industrielle s'opère à double détente : en première ligne dans le proxy inverse Nginx "
                    "via la directive `client_max_body_size 2m;` qui coupe le flux TCP avant même Python, et en "
                    "seconde ligne dans un middleware ASGI inspectant `Content-Length` ainsi que la taille cumulée des "
                    "fragments `receive()` pour opposer immédiatement **`413 Content Too Large` (RFC 9110)** dès que le "
                    "seuil autorisé est franchi."
                )
            }
        ],
        "architecture_diagram": (
            "DOUBLE MÉCANISME : PREFLIGHT CORS (NAVIGATEUR) & SIGNATURE HMAC (WEBHOOK)\n"
            "=========================================================================\n\n"
            "  [A] PRÉ-VÉRIFICATION CORS PAR LE NAVIGATEUR WEB (CORSMiddleware) :\n"
            "  Navigateur (https://portail.isgp.dz)             Serveur API FastAPI (https://api.isgp.dz)\n"
            "  1. OPTIONS /api/formations               ----->  Vérifie si Origin est dans allow_origins\n"
            "     Origin: https://portail.isgp.dz       <-----  200 OK + Access-Control-Allow-Origin\n"
            "  2. POST /api/formations (+ JSON + Auth)  ----->  Exécute la route métier -> 201 Created\n\n"
            "  [B] VÉRIFICATION CRYPTOGRAPHIQUE D'UN WEBHOOK DE PAIEMENT :\n"
            "  Serveur de Paiement                              Serveur API FastAPI\n"
            "  Corps brut : b'{\"id\":101,\"statut\":\"paye\"}'       corps_brut = await request.body()\n"
            "  Header X-Webhook-Signature: sha256=9f8a.. -----> Attendu = HMAC(WEBHOOK_SECRET, corps_brut)\n"
            "                                                   hmac.compare_digest(Recu, Attendu) -> 200 OK"
        ),
        "reference_table": {
            "title": "Mécanismes de Sécurité Périmétrique (`CORS`, `Webhooks`, Plafond Volumétrique)",
            "headers": ["Mécanisme Périmétrique", "En-têtes HTTP Impliqués", "Code HTTP d'Erreur", "Menace Neutralisée"],
            "rows": [
                ["Politique `CORS` stricte", "`Origin`, `Access-Control-Allow-Origin`, `Access-Control-Allow-Headers`", "Blocage côté navigateur", "Appel malveillant de l'API depuis un site tiers non autorisé"],
                ["Signature de Webhook `HMAC`", "`X-Webhook-Signature` (ex: `sha256=...`)", "`401 Unauthorized`", "Falsification d'événements asynchrones (faux paiements, faux statuts)"],
                ["Plafond `TAILLE_MAX_OCTETS`", "`Content-Length`", "`413 Content Too Large`", "Saturation de la mémoire vive (RAM) par envoi de charges géantes"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Configurer `allow_origins=[\"*\"]` (joker universel) sur une API privée d'entreprise",
                "good": "Maintenir une **liste blanche explicite** des domaines frontaux autorisés (`[\"https://portail.isgp.dz\"]`)",
                "why": "Le joker `*` autorise n'importe quel site Internet visité par l'utilisateur à lire les réponses publiques de l'API depuis son navigateur."
            },
            {
                "bad": "Calculer le HMAC d'un Webhook après avoir re-sérialisé le JSON (`json.dumps(await request.json())`)",
                "good": "Calculer systématiquement le HMAC sur la séquence d'octets brute exacte retournée par `await request.body()`",
                "why": "Un seul espace ou ordre de clé différent entre le formateur JSON de l'émetteur et celui de Python modifie totalement le condensat SHA-256."
            }
        ],
        "practical_exercises": [
            "Rédigez un script Python qui forge l'en-tête `X-Webhook-Signature` (`HMAC-SHA256`) sur les octets exacts `b'{\"transaction_id\":\"TX-900\",\"montant\":45000}'` avec le secret du laboratoire et éprouvez la route Webhook.",
            "Étendez la vérification du Webhook pour inclure un en-tête `X-Webhook-Timestamp` dans le message signé (`f\"{timestamp}.\".encode() + body`) et rejeter tout événement vieux de plus de 300 secondes."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.7 : GESTION ET SÉCURITÉ DES COOKIES EN API/WEB (HTTPONLY, SECURE, SAMESITE, SESSION HMAC)
    # =========================================================================
    "d4-l7": {
        "context": (
            "Lorsqu'une application Web React, Vue ou Jinja2 consomme une API FastAPI, une décision d'architecture "
            "détermine sa résistance réelle aux compromissions côté client : **dans quel compartiment du navigateur "
            "conserver le jeton de session de l'usager ?**\n\n"
            "Stocker un JWT sensible dans `window.localStorage` ou `sessionStorage` est formellement proscrit par le "
            "guide **OWASP Application Security Verification Standard (ASVS)** : cet espace étant intégralement "
            "accessible au moteur JavaScript, la moindre vulnérabilité XSS (via une dépendance npm compromise ou un "
            "script tiers) permet d'exfiltrer en une ligne `localStorage.getItem('token')` les sessions de tous les "
            "visiteurs actifs. Ce chapitre expose l'ingénierie des **Cookies HTTP blindés (RFC 6265)** dans FastAPI "
            "via `response.set_cookie(...)`, `Cookie(default=None)` et le triptyque **`HttpOnly`**, **`Secure`** et "
            "**`SameSite`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Cycle protocolaire RFC 6265 : émission `Set-Cookie`, renvoi `Cookie` et purge `Max-Age=0`",
                "body": (
                    "Contrairement à l'en-tête `Authorization: Bearer` que le code applicatif JavaScript doit gérer et "
                    "injecter explicitement sur chaque appel réseau, le mécanisme des **Cookies HTTP (IETF RFC 6265)** "
                    "est piloté nativement par la couche réseau interne du navigateur.\n\n"
                    "Lorsqu'une route d'authentification FastAPI exécute `response.set_cookie(key=\"isgp_session\", "
                    "value=jeton_signe, max_age=3600, httponly=True, secure=True, samesite=\"strict\")`, le serveur "
                    "émet un en-tête `Set-Cookie` qui instruit le navigateur d'archiver ce couple dans son coffre "
                    "isolé. Sur chaque requête ultérieure dirigée vers le domaine et le chemin correspondants, le "
                    "navigateur attache automatiquement l'en-tête `Cookie: isgp_session=...`, lu côté FastAPI par "
                    "simple déclaration `isgp_session: str | None = Cookie(default=None)`. Lors de la déconnexion, "
                    "`response.delete_cookie(key=\"isgp_session\")` expédie un `Set-Cookie` affecté de **`Max-Age=0`**, "
                    "provoquant l'effacement instantané du secret chez le client."
                )
            },
            {
                "heading": "2. Blindage orthogonal : `HttpOnly` (anti-XSS), `Secure` (TLS strict) et `SameSite` (anti-CSRF)",
                "body": (
                    "Un cookie d'authentification dépourvu de ses drapeaux de sécurité est vulnérable sur trois fronts "
                    "distincts ; chacun des trois attributs normatifs verrouille exactement un vecteur d'attaque.\n\n"
                    "```http — En-tête Set-Cookie durci émis par FastAPI en production HTTPS\n"
                    "Set-Cookie: isgp_session=eyJzdWIiOiJhbWluZSJ9.Z5y0AA.7cQ...; HttpOnly; Max-Age=3600; Path=/; SameSite=strict; Secure\n"
                    "```\n\n"
                    "Le drapeau **`HttpOnly` (`httponly=True`)** érige une cloison étanche entre la pile réseau du "
                    "navigateur et le moteur d'exécution JavaScript : l'accès à `document.cookie` retourne une chaîne "
                    "vide, rendant le jeton **impossible à dérober par un script XSS**. Le drapeau **`Secure` "
                    "(`secure=True`)** interdit toute émission du cookie sur un lien `http://` en clair, déjouant "
                    "l'écoute passive sur Wi-Fi public. Enfin, puisque le navigateur attache automatiquement les "
                    "cookies aux requêtes vers votre domaine, il faut contrer l'attaque **CSRF (*Cross-Site Request "
                    "Forgery*)** où un site externe malveillant soumet à l'insu de la victime un formulaire `<form "
                    "method=\"POST\" action=\"https://api.isgp.dz/virements\">` : l'attribut **`SameSite=strict`** "
                    "(ou `lax` lorsqu'on souhaite préserver la session lors d'un clic sur un lien entrant `GET`) "
                    "ordonne au navigateur de ne jamais joindre le cookie sur un `POST` déclenché depuis un domaine tiers."
                )
            },
            {
                "heading": "3. Cookie de préférence en clair contre Cookie de session scellé par HMAC (`SessionMiddleware`)",
                "body": (
                    "L'attribut `HttpOnly` protège le cookie contre un script tiers injecté dans la page, mais ne "
                    "protège nullement le serveur contre **l'utilisateur lui-même**, qui contrôle totalement sa machine "
                    "et peut forger n'importe quel en-tête `Cookie: role=admin` avec `curl` ou l'inspecteur réseau F12.\n\n"
                    "> [!IMPORTANT] Ne jamais accorder de valeur d'identité à un cookie non signé\n"
                    "> Seules des préférences cosmétiques sans impact de sécurité (`theme=sombre`, `lang=fr`) peuvent circuler dans un cookie brut. Tout cookie portant un identifiant d'utilisateur ou un rôle doit impérativement être **signé par HMAC** côté serveur (via `itsdangerous.URLSafeTimedSerializer` ou `starlette.middleware.sessions.SessionMiddleware(app, secret_key=..., https_only=True, same_site=\"strict\")`) afin que la moindre altération d'un bit invalide immédiatement la session."
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE DE SÉCURITÉ DES COOKIES : HTTPONLY (ANTI-XSS) + SAMESITE (ANTI-CSRF)\n"
            "=================================================================================\n\n"
            "  Serveur FastAPI (POST /api/auth/cookie-login)\n"
            "       |\n"
            "       |  Set-Cookie: isgp_auth_token=eyJ...Sig; Max-Age=3600; HttpOnly; Secure; SameSite=strict\n"
            "       v\n"
            "  +-----------------------------------------------------------------------------+\n"
            "  | Coffre-Fort Réseau du Navigateur (Isolé du DOM JavaScript)                  |\n"
            "  |                                                                             |\n"
            "  |  1. Script XSS malveillant appelle document.cookie  ---> BLOQUÉ (HttpOnly)  |\n"
            "  |  2. Site tiers evil.com tente un POST CSRF          ---> BLOQUÉ (SameSite)  |\n"
            "  |  3. Connexion non chiffrée http://                  ---> BLOQUÉ (Secure)    |\n"
            "  +-----------------------------------------------------------------------------+\n"
            "       |\n"
            "       |  Requête légitime même origine : Cookie: isgp_auth_token=eyJ...Sig\n"
            "       v\n"
            "  Serveur FastAPI vérifie la signature HMAC (SECRET_KEY) ---> 200 OK"
        ),
        "reference_table": {
            "title": "Matrice de Sécurité des Attributs d'un Cookie HTTP (`Set-Cookie`)",
            "headers": ["Attribut `Set-Cookie`", "Paramètre FastAPI (`response.set_cookie`)", "Attaque Neutralisée", "Comportement du Navigateur"],
            "rows": [
                ["`HttpOnly`", "`httponly=True`", "**XSS** (*Cross-Site Scripting* — vol de jeton via JS)", "Rend le cookie totalement invisible pour `document.cookie` en JavaScript"],
                ["`Secure`", "`secure=True`", "**Sniffing réseau / MitM** sur Wi-Fi public", "Ne transmet le cookie que sur un canal chiffré `https://`"],
                ["`SameSite=Strict` / `Lax`", "`samesite=\"strict\"` ou `\"lax\"`", "**CSRF** (*Cross-Site Request Forgery*)", "Interdit l'envoi automatique du cookie lors de requêtes `POST` déclenchées depuis un site tiers"],
                ["`Max-Age` / `Expires`", "`max_age=3600` (ou `delete_cookie`)", "Persistance infinie sur un poste partagé", "Détruit automatiquement le cookie après `N` secondes (`Max-Age=0` pour révocation immédiate)"],
                ["Signature HMAC", "`URLSafeTimedSerializer(SECRET_KEY)`", "**Falsification client** (élévation de privilèges dans F12)", "Toute modification d'un octet du cookie invalide la signature HMAC côté serveur"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Stocker le rôle en clair dans un cookie non signé (`response.set_cookie('role', 'admin')`) et lui faire confiance",
                "good": "Toujours signer cryptographiquement les cookies d'identité via `URLSafeTimedSerializer` ou `SessionMiddleware` avec `SECRET_KEY`",
                "why": "Un cookie non signé est un simple texte que l'utilisateur peut modifier en 5 secondes dans les outils de développement (F12) de son navigateur."
            },
            {
                "bad": "Oublier `httponly=True` sur un cookie contenant un jeton JWT ou un identifiant de session",
                "good": "Activer systématiquement `httponly=True`, `secure=True` et `samesite=\"strict\"` (ou `https_only=True` sur `SessionMiddleware`)",
                "why": "Sans `HttpOnly`, n'importe quel script JavaScript tiers chargé dans la page peut lire `document.cookie` et dérober la session."
            }
        ],
        "practical_exercises": [
            "Depuis le Client HTTP intégré ou via `curl -i -X POST http://127.0.0.1:8000/api/sandbox/cookies/login`, inspectez les en-têtes `Set-Cookie` émis par FastAPI et vérifiez la présence de `HttpOnly` et `SameSite`.",
            "Enchaînez ensuite `GET /api/sandbox/cookies/inspect` puis `POST /api/sandbox/cookies/logout` pour observer la validation de signature HMAC suivie de la révocation par `Max-Age=0`."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.1 : CONSOMMER UNE API TIERCE (CLIENT HTTP RÉSILIENT, TIMEOUTS & RETRIES)
    # =========================================================================
    "d5-l1": {
        "context": (
            "Jusqu'à présent, notre serveur FastAPI agissait comme une feuille terminale répondant directement à "
            "partir de sa base locale. Dans un Système d'Information d'entreprise contemporain ou une topologie "
            "orientée microservices, votre API devient presque toujours **elle-même cliente d'autres APIs** au cours "
            "du traitement d'une requête : interroger la Banque Centrale pour convertir une devise, certifier un "
            "numéro fiscal auprès d'un registre ministériel ou solliciter une passerelle d'envoi documentaire.\n\n"
            "Or, le premier axiome des systèmes distribués (*Fallacies of Distributed Computing*, Peter Deutsch) "
            "rappelle que **le réseau n'est jamais fiable** : un routeur intermédiaire perd des paquets, un serveur "
            "partenaire fige ses sockets sous la charge. Appeler une API externe de façon synchrone ou sans `timeout` "
            "strict au sein d'un serveur ASGI Uvicorn déclenche en quelques secondes une **défaillance en cascade "
            "(*Cascading Failure*)** qui paralyse l'intégralité de votre propre plateforme."
        ),
        "deep_sections": [
            {
                "heading": "1. Famine de boucle d'événements ASGI (*Event-Loop Starvation*) et obligation des Timeouts granulaires",
                "body": (
                    "Comprenons au niveau système pourquoi un appel HTTP sortant mal encadré est deux fois plus "
                    "dévastateur dans un serveur asynchrone ASGI que dans un serveur multi-threads classique. Premièrement, "
                    "si un développeur invoque un client synchrone bloquant (`requests.get` ou `urllib.request.urlopen`) "
                    "à l'intérieur d'une coroutine `async def`, il gèle l'unique fil d'exécution de la boucle `uvloop` "
                    "du worker Uvicorn pendant toute la durée de l'échange réseau. Deuxièmement, même avec un client "
                    "asynchrone (`httpx.AsyncClient`), **omettre le `timeout`** (ou conserver un délai trop lâche) "
                    "maintient les descripteurs de fichiers et les tâches en attente lorsqu'un partenaire externe "
                    "accepte le `SYN` TCP mais ne renvoie plus jamais un seul octet (*Blackhole / Hanging Socket*).\n\n"
                    "> [!WARNING] Zéro appel sortant sans `httpx.Timeout` explicite en production\n"
                    "> Tout appel HTTP émis par un backend FastAPI doit utiliser un client asynchrone non bloquant (`await client.get(...)` via `httpx.AsyncClient`) assorti de délais granulaires courts (`httpx.Timeout(2.5, connect=1.0)`), ou s'exécuter dans une route `def` synchrone strictement bornée par `timeout=2.5` afin d'avorter rapidement avant épuisement du pool de threads."
                )
            },
            {
                "heading": "2. Réessai sélectif, Recul Exponentiel avec Aléa (*Exponential Backoff + Full Jitter*) et `502`/`504`",
                "body": (
                    "Lorsqu'un appel vers un partenaire échoue, faut-il retenter immédiatement ? La réponse dépend "
                    "strictement de la classe d'erreur et de l'idempotence du verbe. Une erreur **`4xx`** (`400`, "
                    "`401`, `403`, `404`, `422` — hors `429`) traduit un rejet déterministe du contrat : réessayer est "
                    "inutile et gaspille des ressources. À l'inverse, une micro-coupure réseau (`TimeoutException`, "
                    "`ConnectError`) ou une surcharge transitoire **`502 / 503 / 504`** se résorbe souvent en quelques "
                    "centaines de millisecondes.\n\n"
                    "Sur une opération **idempotente** (`GET`, `PUT`, ou `POST` protégé par `Idempotency-Key`), on "
                    "applique un **Exponential Backoff avec Full Jitter** (`attente = random.uniform(0, base * 2 ** "
                    "essai)`) limité à deux ou trois tentatives : la croissance exponentielle laisse le partenaire "
                    "respirer, tandis que l'aléa (*Jitter*) désynchronise les clients pour éviter un effet de troupeau "
                    "(*Thundering Herd*) à la reprise.\n\n"
                    "#### Traduction sémantique fidèle vers votre propre consommateur (`502` vs `504`)\n\n"
                    "Si toutes les tentatives échouent et qu'aucun cache de repli (*Fallback Cache*) n'est disponible, "
                    "votre API FastAPI ne doit **jamais renvoyer `500 Internal Server Error`** (ce qui déclencherait à "
                    "tort des alertes accusant un bogue de votre propre code Python) : elle agit en passerelle et émet "
                    "**`504 Gateway Timeout`** lorsque le partenaire a dépassé le délai imparti, ou **`502 Bad Gateway`** "
                    "lorsqu'il a répondu par une trame corrompue ou une erreur `5xx`."
                )
            },
            {
                "heading": "3. Réutilisation des sockets TLS (*Connection Pooling*) via `lifespan` et `httpx.AsyncClient`",
                "body": (
                    "Ouvrir et refermer un client HTTP neuf à chaque requête entrante (`async with httpx.AsyncClient() "
                    "as client:` à l'intérieur de la route) oblige le serveur à répéter le *Three-Way Handshake* TCP et "
                    "la négociation cryptographique TLS 1.3 à chaque appel, ajoutant 50 à 150 millisecondes de latence "
                    "inutile et épuisant les ports éphémères Linux (`TIME_WAIT`).\n\n"
                    "```python — Pool de connexions HTTP/1.1 & HTTP/2 partagé sur le cycle de vie FastAPI\n"
                    "from contextlib import asynccontextmanager\n"
                    "import httpx\n"
                    "from fastapi import FastAPI, Request\n\n"
                    "@asynccontextmanager\n"
                    "async def lifespan(app: FastAPI):\n"
                    "    timeout = httpx.Timeout(3.0, connect=1.0)\n"
                    "    async with httpx.AsyncClient(timeout=timeout) as http_client:\n"
                    "        app.state.http_client = http_client\n"
                    "        yield  # Fermeture propre de toutes les connexions Keep-Alive à l'arrêt d'Uvicorn\n"
                    "```\n\n"
                    "En instanciant un unique `httpx.AsyncClient` au démarrage dans le gestionnaire **`lifespan`** de "
                    "FastAPI, toutes les requêtes concurrentes du worker mutualisent un pool de connexions TCP/TLS "
                    "persistantes (*Keep-Alive*), divisant par trois la latence d'intégration."
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE D'UN APPEL SORTANT RÉSILIENT (TIMEOUT + RETRY BACKOFF)\n"
            "===================================================================\n\n"
            "  Client Mobile          Votre API FastAPI (Passerelle)            API Partenaire Externe\n"
            "       |                              |                                    |\n"
            "       |--- GET /api/devises -------->|                                    |\n"
            "       |                              |--- Essai 1 (timeout=2.0s) -------->| (Perte paquet / Lent)\n"
            "       |                              |<-- [TimeoutError après 2.0s] ------X\n"
            "       |                              |    Attente Backoff (0.2s)          |\n"
            "       |                              |--- Essai 2 (timeout=2.0s) -------->|\n"
            "       |                              |<-- 200 OK (Taux EUR/DZD) ----------|\n"
            "       |<-- 200 OK (Enrichi) ---------|                                    |\n\n"
            "  (Si les 3 essais échouent par Timeout ---> Votre API répond 504 Gateway Timeout)"
        ),
        "reference_table": {
            "title": "Matrice de Gestion des Pannes lors d'un Appel HTTP vers un Partenaire Externe",
            "headers": ["Situation Rencontrée en Aval (Partenaire)", "Exception Python (`httpx` / `urllib`)", "Faut-il Réessayer (`Retry`) ?", "Code HTTP Renvoyé par Votre API"],
            "rows": [
                ["Partenaire répond `200 OK` avec JSON valide", "Aucune", "Non (Succès immédiat)", "`200 OK`"],
                ["Partenaire ne répond pas dans le délai `timeout`", "`httpx.TimeoutException` / `TimeoutError`", "Oui (2 à 3 fois max avec Backoff)", "`504 Gateway Timeout` (ou `200` dégradé avec cache)"],
                ["Partenaire répond `500`, `502` ou `503`", "`HTTPStatusError` / `HTTPError` (`>= 500`)", "Oui (Erreur transitoire serveur)", "`502 Bad Gateway`"],
                ["Partenaire répond `400`, `401`, `403` ou `404`", "`HTTPStatusError` / `HTTPError` (`4xx`)", "Non (Échec déterministe immédiat)", "`502 Bad Gateway` (ou code métier approprié)"],
                ["Partenaire renvoie du HTML au lieu de JSON", "`json.JSONDecodeError`", "Non", "`502 Bad Gateway`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Appeler `urlopen(url)` ou `requests.get(url)` sans `timeout` (ou directement dans une coroutine `async def` FastAPI)",
                "good": "Utiliser `httpx.AsyncClient(timeout=2.5)` avec `await` dans `async def` (ou borner strictement `timeout=2.5` dans une route `def`)",
                "why": "Un appel bloquant ou dépourvu de `timeout` fige la boucle d'événements ASGI ou sature le pool de threads, provoquant une panne en cascade (*Cascading Failure*)."
            },
            {
                "bad": "Faire un `Retry` automatique sur une opération de paiement (`POST`) sans clé d'idempotence",
                "good": "Ne réessayer automatiquement que les requêtes idempotentes (`GET`, `PUT`, `DELETE`) ou munies d'une `Idempotency-Key`",
                "why": "Si la 1re requête avait abouti mais que seule la réponse s'est perdue sur le réseau, réessayer un `POST` non idempotent exécute l'opération deux fois."
            }
        ],
        "practical_exercises": [
            "Enrichissez la fonction `appeler_api_externe()` d'un **cache mémoire de secours (`FALLBACK_CACHE`)** : mémorisez la dernière réponse valide reçue et restituez-la accompagnée de `\"mode_degrade\": True` lorsque le service aval est indisponible.",
            "Implémentez un disjoncteur léger (**Circuit Breaker**) qui ouvre le circuit pendant 30 secondes après 5 échecs consécutifs afin d'échouer instantanément (`Fail Fast`) sans immobiliser de sockets."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.2 : ARCHITECTURE MODULAIRE, APIROUTER & CYCLE DE VIE API (/api/v1 vs /api/v2)
    # =========================================================================
    "d5-l2": {
        "context": (
            "Lorsqu'une API franchit le cap des cent routes maintenues par plusieurs équipes, deux problématiques "
            "d'architecture logicielle deviennent décisives. Sur le plan interne, comment découper l'application en "
            "domaines autonomes sans sombrer dans un monolithe `main.py` de six mille lignes ni provoquer des "
            "importations circulaires Python (`ImportError: cannot import name 'app'`) ?\n\n"
            "Sur le plan contractuel externe, comment expliquer ce paradoxe apparent de l'industrie mondiale : presque "
            "toutes les grandes plateformes exposent **`/api/v1/...`** pendant près d'une décennie sans passer à `v2`, "
            "tout en considérant l'inscription du segment `/v1/` dès le premier jour comme une **obligation absolue** ? "
            "Ce chapitre articule les **`APIRouter`** et l'**Application Factory (`create_app`)** de FastAPI avec la "
            "gouvernance d'évolution contractuelle et le standard de dépréciation **IETF RFC 8594 (`Deprecation` & "
            "`Sunset`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Loi de Postel (*Tolerant Reader*) : évolutions additives en `/v1` contre ruptures de contrat (`/v2`)",
                "body": (
                    "Si les APIs de référence demeurent sur `/api/v1` durant de longues années, c'est que l'immense "
                    "majorité des enrichissements métier sont conçus de façon **additive et rétrocompatible "
                    "(*Non-Breaking Changes*)** en vertu du principe de robustesse de Jon Postel.\n\n"
                    "> « Soyez conservateur dans ce que vous émettez, et libéral dans ce que vous acceptez des autres. » — Jon Postel, IETF RFC 761 (Principe du *Tolerant Reader*)\n\n"
                    "Ajouter une nouvelle propriété optionnelle dans une réponse JSON (telle que `\"certifiant\": true`), "
                    "publier un nouvel endpoint `GET /api/v1/certificats` ou introduire un filtre facultatif `?lang=fr` "
                    "muni d'une valeur par défaut **ne brise aucun client existant** : un désérialiseur mobile bien "
                    "conçu ignore simplement les clés supplémentaires qu'il ne connaît pas encore.\n\n"
                    "À l'inverse, quatre modifications constituent des **ruptures franches de contrat (*Breaking "
                    "Changes*)** qui feraient planter instantanément les 50 000 applications mobiles déjà installées : "
                    "supprimer ou renommer une clé JSON (`intitule` remplacé par `titre`), muter le type d'un champ "
                    "(`\"duree\": 5` transformé en objet `{\"valeur\": 5, \"unite\": \"jours\"}`), exiger un nouveau "
                    "champ obligatoire en entrée `POST` sans défaut serveur, ou changer la nature racine du JSON. "
                    "Préfixer vos routes par `/api/v1` dès le Jour 1 agit dès lors comme une **assurance-vie "
                    "architecturale** : le jour où une refonte incompatible s'impose, `/api/v2` est monté côte à côte "
                    "sans interrompre les clients historiques."
                )
            },
            {
                "heading": "2. Coexistence multi-versions et protocole d'extinction graduée IETF RFC 8594 (`Deprecation` & `Sunset`)",
                "body": (
                    "Publier `/api/v2` n'autorise jamais à débrancher `/api/v1` le soir même : en environnement B2B ou "
                    "institutionnel, on ouvre une fenêtre de coexistence de six à douze mois durant laquelle deux "
                    "routeurs FastAPI (`v1_router` et `v2_router`) interrogent exactement la même couche de service SQL "
                    "tout en projetant chacun son propre modèle Pydantic `response_model`.\n\n"
                    "```http — Signalisation normative de fin de vie programmée (IETF RFC 8594 & RFC 8288)\n"
                    "HTTP/1.1 200 OK\n"
                    "Content-Type: application/json\n"
                    "Deprecation: true\n"
                    "Sunset: Thu, 31 Dec 2026 23:59:59 GMT\n"
                    "Link: </api/v2/formations>; rel=\"successor-version\"\n"
                    "```\n\n"
                    "En attachant une dépendance globale `dependencies=[Depends(signaler_depreciation_v1)]` sur "
                    "`formations_v1_router`, chaque réponse `v1` embarque automatiquement les en-têtes standards "
                    "**`Deprecation`** et **`Sunset` (RFC 8594)** ainsi que le lien de migration **`Link` (RFC 8288)**. "
                    "Une fois l'échéance `Sunset` échue et le trafic résiduel tombé à zéro dans vos métriques, les "
                    "routes `v1` répondent **`410 Gone`** (et non `404`), signifiant que la version a été "
                    "intentionnellement retirée du service."
                )
            },
            {
                "heading": "3. Modularité par `APIRouter`, *Application Factory* (`create_app`) et sondes Kubernetes (`Liveness` / `Readiness`)",
                "body": (
                    "Pour structurer proprement un projet FastAPI à grande échelle, chaque sous-domaine fonctionnel "
                    "(`catalogue`, `inscriptions`, `facturation`, `sante`) expose son propre objet **`APIRouter(prefix=..., "
                    "tags=[...])`** totalement indépendant de l'instance principale. Au point d'entrée, une fabrique "
                    "**`def create_app() -> FastAPI:`** instancie le serveur, configure les middlewares et assemble les "
                    "briques par `app.include_router(...)` — éradiquant toute importation circulaire et permettant "
                    "d'instancier des applications isolées à la volée dans chaque test automatisé.\n\n"
                    "Enfin, toute architecture prête pour le Cloud ou Kubernetes distingue deux sondes de santé : la "
                    "sonde **`GET /api/health/live` (*Liveness*)** vérifie uniquement que la boucle d'événements ASGI "
                    "du worker n'est pas interbloquée (`200 OK` immédiat ; en cas d'échec, l'orchestrateur redémarre le "
                    "conteneur), tandis que **`GET /api/health/ready` (*Readiness*)** exécute un `SELECT 1` sur la base "
                    "SQL et renvoie `503 Service Unavailable` si la base est momentanément injoignable, afin que le "
                    "répartiteur de charge cesse d'y router du trafic sans tuer inutilement le processus."
                )
            }
        ],
        "architecture_diagram": (
            "COEXISTENCE MULTI-VERSIONS (/api/v1 DÉPRÉCIÉE + /api/v2) VIA APIROUTER FASTAPI\n"
            "===============================================================================\n\n"
            "  Clients Historiques (App Mobile v1)            Nouveaux Clients (Portail Web / App v2)\n"
            "  GET /api/v1/formations                         GET /api/v2/formations\n"
            "            |                                              |\n"
            "            v                                              v\n"
            "  +--------------------------------------------------------------------------+\n"
            "  | APPLICATION FACTORY : create_app() -> FastAPI()                          |\n"
            "  |                                                                          |\n"
            "  |  [APIRouter formations_v1_router]            [APIRouter formations_v2]   |\n"
            "  |  prefix='/api/v1/formations'                 prefix='/api/v2/formations' |\n"
            "  |  + Headers RFC 8594 (Depends) :              + Enveloppe normalisée :     |\n"
            "  |    Deprecation: true                          {\"meta\": {...},            |\n"
            "  |    Sunset: Thu, 31 Dec 2026...                 \"data\": [{\"duree\": {      |\n"
            "  |  + Schéma plat : {\"duree\": 5}                    \"valeur\": 5, ...}}]}    |\n"
            "  +--------------------------------------------------------------------------+\n"
            "                                    \\          /\n"
            "                                     v        v\n"
            "                      [ Couche Métier & Base SQLite Unique ]"
        ),
        "reference_table": {
            "title": "Comparatif des 4 Stratégies de Versionnement d'API & Gestion des Changements",
            "headers": ["Stratégie / Mécanisme", "Exemple Concret", "Avantages Majeurs", "Usage Industriel"],
            "rows": [
                ["1. Versioning dans l'URI (*Path Versioning*)", "`GET /api/v1/formations` vs `/api/v2/formations`", "Immédiatement visible (logs Nginx, navigateur, `curl`), routage Reverse Proxy trivial", "80 % des APIs REST publiques (OpenAI, Twilio, PayPal, Kubernetes)"],
                ["2. Versioning par En-tête HTTP (*Header*)", "`X-API-Version: 2026-11-01` ou `Stripe-Version`", "URL permanente et immuable, permet un versionnement fin par date", "APIs financières et plateformes (Stripe, GitHub API)"],
                ["3. Négociation MIME (*Accept Header*)", "`Accept: application/vnd.isgp.v2+json`", "Respecte strictement la théorie REST pure (Content Negotiation)", "Systèmes hypermédias stricts"],
                ["4. En-têtes de Dépréciation (RFC 8594)", "`Deprecation: true` + `Sunset: <Date HTTP>`", "Permet aux clients de planifier leur migration de `v1` vers `v2` sans coupure brutale", "Toute API en phase de transition `v1 -> v2`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Créer `/api/v2`, `/api/v3`, `/api/v4` chaque fois qu'on ajoute un simple champ optionnel ou une nouvelle route",
                "good": "Rester sur `/api/v1` pour tous les ajouts rétrocompatibles (*Additive Changes*) et réserver `/api/v2` aux vraies ruptures de contrat (*Breaking Changes*)",
                "why": "Multiplier les versions majeures fragmente la maintenance serveur. Grâce à la Loi de Postel, `v1` peut évoluer par ajouts pendant des années."
            },
            {
                "bad": "Renommer une clé JSON (`intitule` -> `titre`) ou changer son type (`5` -> `{'valeur': 5}`) directement dans `/api/v1`",
                "good": "Conserver l'ancien format sur `/api/v1` (avec les en-têtes `Deprecation` et `Sunset`) et publier la rupture de schéma sur `/api/v2`",
                "why": "Modifier le contrat de `v1` en place provoque le crash immédiat des applications mobiles et scripts clients déjà déployés."
            },
            {
                "bad": "Renvoyer une liste JSON brute `[ {...}, {...} ]` à la racine d'une route de collection",
                "good": "Toujours encapsuler les collections dans un objet JSON `{\"meta\": {\"total\": 2}, \"data\": [ ... ]}` dès la `v1`",
                "why": "Avec un objet racine `{...}`, vous pourrez ajouter plus tard la pagination (`meta.next_cursor`) sans casser la `v1`. Avec une liste brute `[...]`, ajouter des métadonnées oblige à casser la racine et à créer une `v2` !"
            }
        ],
        "practical_exercises": [
            "Depuis le Sandbox HTTP ou avec `curl -i http://127.0.0.1:8000/api/v1/sandbox/formations`, vérifiez la présence des en-têtes `Deprecation`, `Sunset` et `Link`, puis interrogez `/api/v2/sandbox/formations` pour comparer la structure du champ `duree`.",
            "Écrivez une dépendance FastAPI lisant un en-tête optionnel `X-API-Version` afin de journaliser la répartition du trafic par version cliente."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.3 : TESTS AUTOMATISÉS (TESTCLIENT), OPENAPI 3.1 & DÉPLOIEMENT ASGI (UVICORN / GUNICORN)
    # =========================================================================
    "d5-l3": {
        "context": (
            "Comment une équipe d'ingénierie backend déploie-t-elle dix mises en production par semaine sans craindre "
            "qu'une retouche sur un modèle Pydantic ne brise silencieusement la facturation ou le contrôle d'accès "
            "d'une route existante ? Certainement pas en cliquant à la main dans Postman : seule une **suite de tests "
            "d'intégration automatisés** exécutée en quelques centaines de millisecondes à chaque *commit* garantit la "
            "non-régression.\n\n"
            "Une fois ce filet de qualité scellé, comment exposer l'application FastAPI sur un serveur Linux de "
            "production en exploitant tous les cœurs physiques du processeur derrière une terminaison TLS durcie ? "
            "Ce chapitre réunit l'ingénierie de test en mémoire **`TestClient(app)`** (et `dependency_overrides`), la "
            "vérification automatique du contrat **OpenAPI 3.1** et la topologie de déploiement à trois étages "
            "**`Nginx -> Uvicorn / Gunicorn (Workers ASGI) -> FastAPI`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Tests d'intégration ASGI en mémoire vive : `TestClient(app)`, `lifespan` et `dependency_overrides`",
                "body": (
                    "Démarrer un véritable serveur TCP sur un port local pour exécuter ses tests unitaires et "
                    "d'intégration est lent, fragile et sujet aux collisions de ports en intégration continue (CI/CD). "
                    "FastAPI fournit à travers **`fastapi.testclient.TestClient`** (construit sur le transport "
                    "`ASGITransport` de `httpx`) un client capable d'injecter des événements ASGI directement dans la "
                    "mémoire RAM de votre objet `app` sans ouvrir la moindre socket système.\n\n"
                    "#### Couverture symétrique (*Happy* / *Unhappy Paths*) et isolation par `dependency_overrides`\n\n"
                    "Utilisé sous forme de gestionnaire de contexte (`with TestClient(app) as client:` — ce qui "
                    "déclenche proprement les phases d'ouverture et de fermeture du `lifespan` !), chaque test "
                    "professionnel vérifie trois invariants : le **statut HTTP exact** (`resp.status_code`), les "
                    "**en-têtes critiques** (`content-type`, `X-Request-ID`, `Location`) et le **corps désérialisé** "
                    "(`resp.json()`). Surtout, FastAPI permet de substituer chirurgicalement une base SQLite éphémère "
                    "ou un faux service partenaire via **`app.dependency_overrides[get_db] = get_test_db`**, tout en "
                    "consacrant au moins autant de tests aux **cas de rejet (`401`, `403`, `404`, `422`, `429`)** "
                    "qu'au scénario nominal."
                )
            },
            {
                "heading": "2. Vérification programmatique du contrat `OpenAPI 3.1` (`app.openapi()`)",
                "body": (
                    "Dans les projets dépourvus de typage fort, la documentation technique diverge du code réel dès le "
                    "premier correctif d'urgence. Dans FastAPI, la méthode `app.openapi()` synthétise dynamiquement un "
                    "arbre JSON conforme à **OpenAPI 3.1.0** directement à partir de `app.routes`, de vos schémas "
                    "Pydantic v2 et de vos dépendances `Security`.\n\n"
                    "En intégrant un test automatisé qui appelle `GET /openapi.json` et vérifie la présence de vos "
                    "routes versionnées, de leurs `response_model` et de leurs `securitySchemes`, votre pipeline CI/CD "
                    "peut même détecter automatiquement toute rupture involontaire de contrat avant la fusion d'une "
                    "*Pull Request*."
                )
            },
            {
                "heading": "3. Topologie Linux de production : pourquoi bannir `--reload` au profit de `Nginx + Uvicorn Workers`",
                "body": (
                    "L'option `uvicorn main:app --reload` est un outil de confort strictement réservé au poste du "
                    "développeur : elle instancie un surveillant de fichiers coûteux et n'exécute qu'**un seul "
                    "processus Python**, laissant 7 cœurs inactifs sur une machine à 8 processeurs (en raison du *GIL* "
                    "de CPython) et exposant directement Uvicorn sans bouclier frontal.\n\n"
                    "```bash — Lancement industriel multi-workers derrière un proxy inverse HTTPS\n"
                    "# Option A : Gestionnaire multi-processus natif d'Uvicorn (uvloop + httptools)\n"
                    "uvicorn app:create_app --factory --host 127.0.0.1 --port 8000 --workers 4 --proxy-headers\n\n"
                    "# Option B : Superviseur maître Gunicorn pilotant des workers ASGI Uvicorn\n"
                    "gunicorn \"app:create_app()\" -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000\n"
                    "```\n\n"
                    "> [!IMPORTANT] Architecture canonique à trois étages en production\n"
                    "> En première ligne sur les ports `80/443`, **Nginx** (ou Caddy / Traefik / Cloud Load Balancer) assure la terminaison cryptographique **TLS 1.3**, absorbe les clients lents (*Slowloris*), compresse les flux (`gzip`/`zstd`) et sert les actifs `/static/` à vitesse noyau (`sendfile`). En deuxième ligne sur l'interface privée `127.0.0.1:8000`, **Uvicorn multi-workers** (ou **Gunicorn + `UvicornWorker`**) répartit les requêtes sur `N` processus ASGI équipés chacun de sa boucle `uvloop` dédiée exécutant votre application **FastAPI**."
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE DE DÉPLOIEMENT DE PRODUCTION LINUX (NGINX + UVICORN ASGI + FASTAPI)\n"
            "================================================================================\n\n"
            "  Internet (HTTPS :443)\n"
            "        |\n"
            "        v\n"
            "  +-------------------------------------------------------------------+\n"
            "  | 1. NGINX (Reverse Proxy)                                          |\n"
            "  |    - Terminaison SSL/TLS (Certificats HTTPS)                      |\n"
            "  |    - Fichiers /static/ (sendfile on) + Compression Gzip           |\n"
            "  +-------------------------------------------------------------------+\n"
            "        |  (Proxy Pass HTTP interne : upstream isgp_fastapi_cluster)\n"
            "        v\n"
            "  +-------------------------------------------------------------------+\n"
            "  | 2. UVICORN / GUNICORN (Serveur ASGI Multi-Workers)                |\n"
            "  |    Commande : uvicorn app:app --workers 4 --port 8000             |\n"
            "  +-------------------------------------------------------------------+\n"
            "     |                  |                  |                  |\n"
            "     v                  v                  v                  v\n"
            "  [Worker ASGI 1]    [Worker ASGI 2]    [Worker ASGI 3]    [Worker ASGI 4]\n"
            "  Instance FastAPI   Instance FastAPI   Instance FastAPI   Instance FastAPI\n"
            "     \\                  |                  |                  /\n"
            "      +-----------------+------------------+-----------------+\n"
            "                                   |\n"
            "                                   v\n"
            "                    [ Base de Données SQL / Redis ]"
        ),
        "reference_table": {
            "title": "Comparatif : Serveur de Développement (`--reload`) vs Serveur ASGI Production (`Uvicorn Workers + Nginx`)",
            "headers": ["Critère d'Exploitation", "Serveur de Dev (`uvicorn --reload`)", "Serveur ASGI Production (`Uvicorn / Gunicorn + Nginx`)"],
            "rows": [
                ["Vocation", "Développement local et rechargement à chaud", "Production haute disponibilité exposée aux utilisateurs réels"],
                ["Parallélisme multi-cœurs", "Non (1 seul processus Python)", "Oui (`N` processus Workers ASGI indépendants répartis sur tous les cœurs CPU)"],
                ["Boucle d'événements", "1 boucle `asyncio` + surveillance fichiers", "Boucles `uvloop` haute performance sans surveillance disque"],
                ["Sécurité HTTPS & Fichiers statiques", "Faible (Non conçu pour l'exposition directe sur Internet)", "Maximale (Déléguée à Nginx en frontal + `--proxy-headers` sur Uvicorn)"],
                ["Tests automatisés", "Manuels", "Exécutés automatiquement en CI/CD via `TestClient(app)`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Utiliser `--reload` sur un serveur de production",
                "good": "Toujours désactiver `--reload` en production et utiliser `--workers 4 --proxy-headers` derrière Nginx",
                "why": "Le mode `--reload` consomme du CPU/RAM pour surveiller le système de fichiers et ne peut pas être combiné avec `--workers`."
            },
            {
                "bad": "N'écrire des tests automatisés que pour les cas de succès (`200 OK`)",
                "good": "Tester systématiquement les cas d'erreur (`400`, `401`, `403`, `404`, `422`) avec `TestClient(app)`",
                "why": "Les régressions de sécurité et les crashs en production surviennent presque toujours sur les entrées invalides ou non autorisées."
            }
        ],
        "practical_exercises": [
            "Complétez la fonction `executer_suite_de_tests()` dans l'atelier ci-dessus en ajoutant une assertion vérifiant qu'un `POST /api/v1/formations` doté d'un `tarif_dzd` négatif est immédiatement refoulé avec `422`.",
            "Parcourez le dictionnaire retourné par `client.get('/openapi.json').json()` afin d'inspecter les schémas JSON compilés sous `components.schemas`."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.4 : DOCUMENTATION INTERACTIVE SWAGGER UI (/DOCS), REDOC (/REDOC) & OPENAPI 3.1
    # =========================================================================
    "d5-l4": {
        "context": (
            "Dans une organisation où l'équipe Backend Python publie des services consommés simultanément par des "
            "développeurs mobiles Swift/Kotlin, des intégrateurs React/TypeScript et des partenaires institutionnels, "
            "comment transmettre la cartographie exacte des endpoints, les contraintes de chaque attribut et les "
            "mécanismes d'authentification ?\n\n"
            "Maintenir un cahier de spécifications Word ou un fichier YAML édité à la main est voué à l'obsolescence "
            "dès la deuxième semaine du projet (*Documentation Drift*). L'apport décisif de **FastAPI** est d'inverser "
            "ce rapport en érigeant vos annotations de type Python et vos modèles **Pydantic v2** en **source unique "
            "de vérité** générant en temps réel un contrat conforme à **OpenAPI 3.1.0 (JSON Schema Draft 2020-12)** "
            "ainsi que deux portails interactifs natifs : **Swagger UI (`/docs`)** et **ReDoc (`/redoc`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Généalogie normative : `OpenAPI 3.1.0` (JSON Schema 2020-12) face à `Swagger UI` et `ReDoc`",
                "body": (
                    "Une confusion terminologique fréquente mérite d'être dissipée avec rigueur. Créé initialement en "
                    "2010 sous le nom *Swagger*, le format de description a été confié en 2015 à la Fondation Linux "
                    "sous l'égide de l'**OpenAPI Initiative (OAI)**.\n\n"
                    "Aujourd'hui, **OpenAPI 3.1.0** désigne la **spécification formelle du contrat machine** exposée par "
                    "FastAPI sur `/openapi.json` — une version majeure qui s'aligne enfin à 100 % sur le standard "
                    "**JSON Schema Draft 2020-12** (représentant nativement les unions Python `str | None` via "
                    "`anyOf: [{\"type\": \"string\"}, {\"type\": \"null\"}]`). **Swagger UI (`/docs`)** et **ReDoc "
                    "(`/redoc`)** sont quant à eux deux applications clientes JavaScript embarquées par FastAPI qui "
                    "lisent ce même fichier `/openapi.json` : le premier fournit une console d'essai interactive "
                    "(*Try it out*), tandis que le second génère un manuel de référence en trois colonnes prisé pour "
                    "les portails développeurs publics."
                )
            },
            {
                "heading": "2. Enrichissement déclaratif de `paths`, `components.schemas` et du cadenas `Authorize`",
                "body": (
                    "Chaque métadonnée ajoutée dans votre code Python se répercute instantanément dans l'arbre OpenAPI "
                    "sans aucune duplication. Les arguments du constructeur `FastAPI(title=..., version=..., "
                    "openapi_tags=...)` structurent l'en-tête éditorial, tandis que les paramètres du décorateur de "
                    "route — **`response_model=FormationOut`**, `status_code=201`, `summary=...` et le dictionnaire "
                    "`responses={404: {\"model\": ProblemDetail}}` — documentent avec exactitude les schémas de sortie "
                    "d'erreur comme de succès.\n\n"
                    "```python — Connexion automatique du bouton cadenas « Authorize » dans Swagger UI\n"
                    "from fastapi import Depends, FastAPI, Security\n"
                    "from fastapi.security import APIKeyHeader, HTTPBearer\n\n"
                    "api_key_scheme = APIKeyHeader(name=\"X-API-Key\", description=\"Clé partenaire ISGP\")\n"
                    "bearer_scheme = HTTPBearer(description=\"Jeton d'accès signé\")\n\n"
                    "@app.get(\"/api/v1/admin/stats\", tags=[\"Administration\"])\n"
                    "def lire_stats(cle: str = Security(api_key_scheme)):\n"
                    "    return {\"statut\": \"autorise\"}\n"
                    "```\n\n"
                    "Dès qu'une route dépend d'une instance `fastapi.security` (`APIKeyHeader`, `HTTPBearer`, "
                    "`OAuth2PasswordBearer`), FastAPI inscrit automatiquement la définition dans "
                    "`components.securitySchemes` et allume le cadenas **« Authorize »** dans `/docs`, permettant aux "
                    "testeurs d'injecter leur jeton en un clic sur tous leurs appels interactifs."
                )
            },
            {
                "heading": "3. Gouvernance d'exposition en production et génération automatisée de SDK clients",
                "body": (
                    "Au-delà de la lecture humaine, disposer d'un contrat `/openapi.json` strictement typé débloque "
                    "l'automatisation industrielle : des générateurs tels qu'`openapi-typescript`, `orval` ou "
                    "`openapi-generator-cli` compilent en une seconde les interfaces TypeScript, Kotlin ou Swift "
                    "exactement synchronisées avec vos modèles Pydantic v2.\n\n"
                    "> [!TIP] Désactiver ou protéger `/docs` sur les APIs internes d'administration\n"
                    "> Sur une API publique destinée à des partenaires, exposer `/docs` et `/redoc` est un atout majeur. En revanche, sur un microservice interne sensible, laisser `/openapi.json` ouvert sur Internet offre à un attaquant la carte complète de vos routes et paramètres. Il suffit alors de conditionner le constructeur par environnement : `FastAPI(docs_url=None, redoc_url=None, openapi_url=None)` lorsque `ENV == \"production\"`."
                )
            }
        ],
        "architecture_diagram": (
            "ÉCOSYSTÈME OPENAPI 3.1 : UN SEUL CONTRAT GÉNÉRÉ PAR FASTAPI POUR TOUS LES OUTILS\n"
            "================================================================================\n\n"
            "                    +----------------------------------------+\n"
            "                    |   Serveur FastAPI (/openapi.json)      |\n"
            "                    |   Contrat OpenAPI 3.1.0 (Pydantic v2)  |\n"
            "                    +-------------------+--------------------+\n"
            "                                        |\n"
            "         +------------------------------+------------------------------+\n"
            "         |                              |                              |\n"
            "         v                              v                              v\n"
            "  +--------------+              +---------------+              +---------------+\n"
            "  | SWAGGER UI & |              |  POSTMAN /    |              | OPENAPI       |\n"
            "  | REDOC NATIFS |              |  INSOMNIA     |              | GENERATOR     |\n"
            "  | (/docs &     |              |  Import 1-clic|              | Génère les SDK|\n"
            "  |  /redoc)     |              |  Collection   |              | Mobile & Web  |\n"
            "  +--------------+              +---------------+              +---------------+"
        ),
        "reference_table": {
            "title": "Structure de Référence d'un Document OpenAPI 3.1 (`openapi.json`)",
            "headers": ["Clé Racine OpenAPI 3.1", "Rôle dans le Contrat", "Exemple Généré par FastAPI", "Impact Visuel dans Swagger UI (`/docs`)"],
            "rows": [
                ["`openapi` & `info`", "Version de la norme et identité de l'API", "`\"openapi\": \"3.1.0\", \"info\": {\"title\": \"...\", \"version\": \"1.0.0\"}`", "Affiche l'en-tête principal, le badge `OAS 3.1` et la description Markdown"],
                ["`servers`", "Liste des URLs de base cibles", "`[{\"url\": \"https://api.isgp.dz\"}]`", "Alimente la liste déroulante *Servers* pour choisir l'environnement cible"],
                ["`paths`", "Catalogue des routes et méthodes HTTP", "`\"/api/v1/formations/{id}\": {\"get\": {...}}`", "Crée les bandeaux colorés dépliables (`GET` bleu, `POST` vert, `PUT` orange, `DELETE` rouge)"],
                ["`components.schemas`", "Modèles JSON Schema 2020-12 issus de Pydantic v2", "`\"FormationOut\": {\"type\": \"object\", \"properties\": {...}}`", "Alimente la section *Schemas* et pré-remplit les charges utiles *Try it out*"],
                ["`components.securitySchemes`", "Définition des mécanismes `fastapi.security`", "`\"HTTPBearer\": {\"type\": \"http\", \"scheme\": \"bearer\"}`", "Affiche le bouton cadenas vert **« Authorize »** en haut à droite et sur chaque route protégée"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Omettre `response_model=...` et retourner un dictionnaire Python non typé sur une route complexe",
                "good": "Déclarer systématiquement `response_model=FormationOut` (ou annoter le type de retour `-> FormationOut`)",
                "why": "Grâce à `response_model`, FastAPI documente le schéma exact dans `/docs`, valide la sortie et filtre automatiquement tout champ sensible interne (comme `password_hash`) qui aurait fuité !"
            },
            {
                "bad": "Laisser la documentation Swagger accessible publiquement sans protection sur une API interne critique exposant toute la topologie privée",
                "good": "Conditionner `docs_url=None, redoc_url=None, openapi_url=None` en production privée ou protéger `/docs` derrière un réseau interne / authentification",
                "why": "Sur une API privée non destinée à des tiers externes, exposer publiquement `/openapi.json` accélère la phase de reconnaissance d'un assaillant."
            }
        ],
        "practical_exercises": [
            "Ouvrez le portail Swagger UI intégré à ce laboratoire (`/api/docs`), cliquez sur le bouton cadenas **« Authorize »**, renseignez la clé `isgp-secret-2026` dans `ApiKeyAuth`, puis exécutez `GET /api/sandbox/admin-stats` via **« Try it out »**.",
            "Dans `day_5/05_swagger_openapi_ui.py`, enrichissez un modèle Pydantic avec `model_config = ConfigDict(json_schema_extra={\"examples\": [...]})` et vérifiez son apparition dans le schéma généré."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.5 : INGÉNIERIE DE COLLECTION EN PRODUCTION (PAGINATION OFFSET VS CURSOR, FILTRAGE & TRI SÉCURISÉ)
    # =========================================================================
    "d5-l5": {
        "context": (
            "Dans un prototype de démonstration, exécuter `SELECT * FROM inscriptions` sur dix enregistrements "
            "s'achève en moins d'une milliseconde. Deux ans après le déploiement national d'une plateforme, lorsque "
            "les tables d'audit, de transactions ou de candidatures cumulent **dix millions de lignes**, même la "
            "pagination classique par numéro de page (`OFFSET / LIMIT`) finit par mettre à genoux le disque et le "
            "processeur du serveur SQL sur les pages profondes.\n\n"
            "Ce chapitre de synthèse finale déploie les techniques d'ingénierie de données des architectures à très "
            "fort trafic dans FastAPI : confrontation algorithmique entre la dégradation linéaire **`O(N)` d'`OFFSET`** "
            "et le saut en temps constant **`O(1)` de la Pagination par Curseur (*Keyset / Seek Pagination*)**, "
            "construction dynamique de clauses `WHERE` paramétrées et verrouillage du tri `ORDER BY` par liste blanche."
        ),
        "deep_sections": [
            {
                "heading": "1. Pathologie des grandes profondeurs en `Offset / Limit` : coût `O(N)` et dérive d'insertion",
                "body": (
                    "La pagination numérotée (`?page=2&per_page=20`, traduite en SQL par `ORDER BY id ASC LIMIT 20 "
                    "OFFSET 20`) demeure idéale pour les tableaux d'administration de taille modérée où l'opérateur "
                    "souhaite sauter directement à la « Page 12 ». Mais dès que l'on explore des profondeurs élevées "
                    "(par exemple `OFFSET 1000000` lors d'une synchronisation partenaire ou d'un défilement continu), "
                    "deux pathologies sévères apparaissent.\n\n"
                    "Premièrement, **la dégradation linéaire `O(N)`** : un moteur SQLite ou PostgreSQL ne peut pas "
                    "deviner où commence la millionième ligne filtrée sans parcourir l'index, matérialiser et compter "
                    "les **1 000 000 premières lignes** uniquement pour les jeter à la poubelle avant de retourner les "
                    "20 suivantes ! Deuxièmement, **l'anomalie de dérive (*Page Drift*)** : en tri décroissant des "
                    "publications les plus récentes, si un nouvel enregistrement est inséré pendant que le lecteur "
                    "consulte la Page 1, tous les indices se décalent d'un cran vers le bas et le dernier élément de "
                    "la Page 1 réapparaît en doublon en tête de la Page 2."
                )
            },
            {
                "heading": "2. Pagination par Curseur (*Keyset / Seek Pagination*) : traversée d'arbre B-Tree en temps `O(1)`",
                "body": (
                    "Pour garantir une latence sous la milliseconde quelle que soit la volumétrie (1 000 ou 100 "
                    "millions de lignes), Stripe, Slack, GitHub et X/Twitter remplacent le compteur d'`OFFSET` par une "
                    "**ancre de valeur** appelée **curseur** (`?after_id=1042&limit=20`).\n\n"
                    "```sql — Saut direct dans l'index primaire B-Tree sans balayage préalable : O(log N) ~ O(1)\n"
                    "SELECT id, titre, domaine, duree_jours, tarif_dzd\n"
                    "FROM formations\n"
                    "WHERE id > ?\n"
                    "ORDER BY id ASC\n"
                    "LIMIT ?;\n"
                    "-- Astuce pro : demander (limit + 1) lignes en SQL permet de savoir instantanément s'il existe\n"
                    "-- une suite (has_more = len(rows) > limit) sans exécuter de coûteux SELECT COUNT(*) !\n"
                    "```\n\n"
                    "Parce que la clé primaire `id` est organisée sous forme d'**arbre équilibré B-Tree**, le moteur "
                    "SQL descend directement à la feuille `id = 1043` en trois ou quatre comparaisons mémoire et lit "
                    "les `20` entrées contiguës : lire le début ou le cinquante-millionième enregistrement prend "
                    "**exactement le même temps constant** ! La réponse JSON livre alors au client le signet "
                    "`\"next_cursor\": 1062` (ou `null` lorsqu'on atteint la fin du flux), éliminant au passage tout "
                    "doublon en cas d'insertions concurrentes."
                )
            },
            {
                "heading": "3. Prédicats SQL dynamiques paramétrés et immunité `ORDER BY` par Liste Blanche stricte",
                "body": (
                    "Combiner plusieurs filtres optionnels (`?domaine=Securite&duree_min=4&tarif_max=90000`) avec un "
                    "tri dynamique (`?sort=-tarif_dzd`) exige une discipline d'assemblage SQL rigoureuse. Les clauses "
                    "de filtrage s'accumulent dans une liste de fragments statiques (`clauses.append(\"domaine = ?\")`) "
                    "accompagnée d'une liste parallèle de valeurs (`params.append(domaine)`), garantissant que chaque "
                    "donnée cliente demeure liée à un marqueur `?`.\n\n"
                    "> [!WARNING] Les marqueurs `?` sont inopérants dans `ORDER BY` : Liste Blanche obligatoire !\n"
                    "> En SQL standard, un paramètre lié `?` dans `ORDER BY ?` est évalué comme une constante littérale inerte (il ne trie rien !), poussant les imprudents à écrire `f\"ORDER BY {sort}\"` — ce qui ouvre une **Injection SQL critique** permettant d'exécuter des sous-requêtes aveugles.\n\n"
                    "La parade canonique consiste à dissocier en Python le préfixe de direction (`-` traduit par la "
                    "constante serveur `\"DESC\"`, sinon `\"ASC\"`) du nom de colonne, puis à valider ce nom contre un "
                    "dictionnaire ou ensemble figé **`COLONNES_TRI_AUTORISEES = {\"id\", \"duree_jours\", \"tarif_dzd\", "
                    "\"titre\"}`** (ou directement par un type `Literal` dans `Query(...)`) : aucune chaîne issue du "
                    "réseau ne pénètre jamais dans le SQL sans avoir été reconnue à l'identique dans ce référentiel clos."
                )
            }
        ],
        "architecture_diagram": (
            "COMPARAISON SQL : PAGINATION OFFSET O(N) VS PAGINATION CURSEUR KEYSET O(1)\n"
            "==========================================================================\n\n"
            "  [A] OFFSET / LIMIT (?page=5000&per_page=20 -> OFFSET 99980) :\n"
            "  Table SQL : [Ligne 1 .................... Ligne 99980] ---> [Lignes 99981 à 100000]\n"
            "               \\___ Balayage séquentiel coûteux O(N) __/       \\__ Renvoyées (20) __/\n\n"
            "  [B] CURSEUR KEYSET (?after_id=99980&limit=20 -> WHERE id > 99980 LIMIT 20) :\n"
            "  Index B-Tree sur 'id' ----(Saut direct O(1))----> [Lignes 99981 à 100000]\n"
            "                                                     \\__ Renvoyées en < 1ms + next_cursor=100000"
        ),
        "reference_table": {
            "title": "Comparatif Industriel : Pagination `Offset/Limit` vs Pagination par `Curseur (Keyset)`",
            "headers": ["Critère d'Ingénierie", "Pagination `Offset / Limit` (`?page=2&per_page=20`)", "Pagination `Curseur / Keyset` (`?after_id=1042&limit=20`)"],
            "rows": [
                ["Requête SQL sous-jacente", "`SELECT * FROM table ORDER BY id LIMIT ? OFFSET ?`", "`SELECT * FROM table WHERE id > ? ORDER BY id LIMIT ?`"],
                ["Complexité algorithmique SQL", "`O(N)` — Ralentit linéairement à mesure que `OFFSET` augmente", "`O(1)` — Temps constant ultra-rapide via l'index B-Tree"],
                ["Saut direct vers une page (`Page 14`)", "Oui (idéal pour les grilles Web numérotées modérées)", "Non (navigation séquentielle *Suivant* / flux continu)"],
                ["Stabilité en cas d'insertion temps réel", "Risque de dérive (doublons ou sauts d'éléments)", "100 % stable (ancré sur l'identifiant unique `after_id`)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Accepter le paramètre `?per_page=` ou `?limit=` du client sans imposer de plafond maximum côté serveur",
                "good": "Toujours borner la limite déclarativement : `per_page: int = Query(20, ge=1, le=50)`",
                "why": "Sans plafond `le=50`, un attaquant peut envoyer `?per_page=99999999` et provoquer un déni de service par saturation RAM."
            },
            {
                "bad": "Injecter directement le paramètre `?sort=` dans une requête SQL sans validation",
                "good": "Valider systématiquement la clé de tri contre un `set` Python (`CHAMPS_TRI_AUTORISES`) ou `Literal[...]` et renvoyer `422` en cas d'écart",
                "why": "C'est le seul moyen d'autoriser un tri dynamique tout en garantissant l'impossibilité absolue d'une injection SQL."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_5/02_pagination_filtrage_production.py` dans l'atelier ci-dessus et suivez l'enchaînement des valeurs `next_cursor` sur `/api/v1/catalogue/cursor` jusqu'à épuisement de la collection (`next_cursor == None`).",
            "Ajoutez un paramètre optionnel `?fields=id,titre` (*Sparse Fieldsets*) filtré par liste blanche permettant aux terminaux mobiles à bas débit de ne projeter que les attributs strictement nécessaires."
        ]
    }
}
