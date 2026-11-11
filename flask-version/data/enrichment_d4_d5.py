"""
Manuel de Référence Approfondi — Enrichissement des Chapitres (Jours 4 et 5).
Fournit pour chaque chapitre les clés structurelles context, deep_sections,
architecture_diagram, reference_table, pitfalls et practical_exercises.
"""

ENRICHMENT_D4_D5 = {
    # =========================================================================
    # JOUR 4 — CHAPITRE 4.1 : CRYPTOGRAPHIE APPLIQUÉE, VARIABLES D'ENVIRONNEMENT & API KEYS
    # =========================================================================
    "d4-l1": {
        "context": (
            "Dès qu'un service HTTP Flask dépasse le cadre d'un prototype local pour exposer des actifs critiques — dossiers "
            "administratifs, écritures comptables ou opérations de provisionnement — l'absence de contrôle cryptographique rigoureux "
            "transforme chaque route Werkzeug en vecteur d'exfiltration directe. L'analyse post-mortem des incidents de sécurité "
            "industriels démontre que les compromissions découlent rarement d'une cryptanalyse mathématique avancée, mais presque "
            "systématiquement de trois défauts d'ingénierie élémentaires dans le code applicatif.\n\n"
            "La première défaillance consiste à confondre la représentation syntaxique d'un flux d'octets (encodage `Base64`), la "
            "condensation unidirectionnelle d'un secret (`PBKDF2-HMAC-SHA256` ou `scrypt`) et le chiffrement symétrique authentifié "
            "(`AES-GCM`). La deuxième réside dans l'inclusion littérale de clés d'API ou de `SECRET_KEY` Flask au sein des modules Python "
            "versionnés sous Git, inscrivant de façon indélébile ces secrets dans le graphe d'objets du dépôt. La troisième provient de "
            "l'évaluation naïve d'égalité via l'opérateur Python `==`, dont le court-circuit lexicographique crée un canal auxiliaire "
            "exploitable par attaque temporelle (*Timing Side-Channel Attack*). Ce chapitre pose les fondations cryptographiques et "
            "système indispensables à la sécurisation d'une architecture WSGI en production."
        ),
        "deep_sections": [
            {
                "heading": "1. Taxonomie cryptographique : Encodage, Dérivation lente (`scrypt` / `PBKDF2`) et Signature `HMAC`",
                "body": (
                    "#### Représentation Base64 vs Condensation irréversible\n\n"
                    "L'encodage (`UTF-8`, `Base64URL` défini par la RFC 4648) est une bijection publique dépourvue de toute propriété de "
                    "confidentialité ou d'intégrité : son unique rôle dans Werkzeug et HTTP consiste à projeter des séquences d'octets arbitraires "
                    "dans un alphabet ASCII sûr pour le transport textuel (en-têtes WSGI `environ` ou corps JSON). À l'inverse, une fonction de "
                    "hachage cryptographique telle que `SHA-256` projette un message de longueur arbitraire vers un condensat fixe de 256 bits "
                    "avec résistance aux préimages et aux collisions. Toutefois, la rapidité intrinsèque de `SHA-256` sur matériel spécialisé "
                    "(plusieurs dizaines de milliards de condensats par seconde sur GPU moderne) interdit formellement son usage direct sur des "
                    "mots de passe humains à faible entropie.\n\n"
                    "> « Les vérificateurs DOIVENT stocker les secrets mémorisés sous une forme résistante aux attaques hors ligne en utilisant "
                    "une fonction de dérivation de clé salée et coûteuse en mémoire ou en calcul. » — NIST Special Publication 800-63B, Section 5.1.1.2\n\n"
                    "#### Dérivation de clé dans Werkzeug (`scrypt` et `hashlib.pbkdf2_hmac`)\n\n"
                    "Depuis Werkzeug 3.0, `werkzeug.security.generate_password_hash()` délègue par défaut la dérivation à `hashlib.scrypt` "
                    "(paramètres `n=32768, r=8, p=1`, imposant une empreinte mémoire vive dissuasive contre le parallélisme massif sur ASIC/GPU) "
                    "ou à `hashlib.pbkdf2_hmac('sha256', password, salt, iterations=600000)`. Chaque appel génère via `secrets.token_bytes(16)` un "
                    "sel cryptographique unique incorporé dans la chaîne sérialisée retournée en base SQL, neutralisant intégralement les tables "
                    "arc-en-ciel (*Rainbow Tables*) précalculées. Quant au code d'authentification de message `HMAC` (RFC 2104), il combine une "
                    "clé secrète serveur et une charge utile au sein d'une double passe de hachage `H((K ^ opad) || H((K ^ ipad) || m))` afin de "
                    "certifier l'authenticité et l'intégrité d'un message sans jamais exposer la clé."
                )
            },
            {
                "heading": "2. Isolation des secrets d'exécution selon Twelve-Factor App (`os.environ` et `app.config`)",
                "body": (
                    "#### Séparation stricte entre code immuable et contexte de déploiement\n\n"
                    "Le troisième axiome de la méthodologie industrielle *Twelve-Factor App* impose une frontière étanche entre l'artefact logiciel "
                    "et sa configuration sensible. Toute chaîne secrète (`SECRET_KEY` Flask, URI PostgreSQL avec mot de passe, clé privée de "
                    "signature) inscrite dans un module Python survit dans l'historique des blobs Git (`git log -S`) même après un commit de "
                    "suppression ultérieur. Au démarrage du processus maître Gunicorn, les secrets doivent être injectés dans le bloc d'environnement "
                    "POSIX du processus par l'orchestrateur (`systemd` via `EnvironmentFile=`, Kubernetes `Secret`, ou HashiCorp Vault), puis "
                    "récupérés dans l'usine applicative Flask via `os.environ`.\n\n"
                    "```python\n"
                    "import os\n"
                    "from flask import Flask\n\n"
                    "def create_app() -> Flask:\n"
                    "    app = Flask(__name__)\n"
                    "    secret = os.environ.get(\"FLASK_SECRET_KEY\")\n"
                    "    if not secret or len(secret) < 32:\n"
                    "        raise RuntimeError(\"FLASK_SECRET_KEY absente ou entropie insuffisante (< 256 bits).\")\n"
                    "    app.config[\"SECRET_KEY\"] = secret\n"
                    "    return app\n"
                    "```\n\n"
                    "> [!WARNING] Proscrire les valeurs par défaut silencieuses en production\n"
                    "> L'idiome `os.environ.get('SECRET_KEY', 'dev-secret')` constitue une vulnérabilité critique si la variable d'environnement "
                    "est accidentellement omise lors du déploiement : tous les workers Gunicorn signent alors les sessions et jetons avec une clé "
                    "publique connue. Exigez un échec immédiat au démarrage (*Fail-Fast*) hors mode développement explicite."
                )
            },
            {
                "heading": "3. Authentification Machine-to-Machine (`X-API-Key`) et comparaison en temps constant (`hmac.compare_digest`)",
                "body": (
                    "#### Transport dans les en-têtes HTTP et hachage côté stockage\n\n"
                    "Dans une intégration serveur-à-serveur dépourvue d'interaction utilisateur (collecteur comptable, passerelle logistique), "
                    "l'appelant transmet une clé à haute entropie générée par `secrets.token_urlsafe(32)` dans un en-tête HTTP dédié tel que "
                    "`X-API-Key`. Transmettre un secret dans la *query string* (`GET /api/v1/export?api_key=...`) expose irrémédiablement la clé "
                    "en clair dans `environ['QUERY_STRING']`, les journaux `access.log` de Nginx, les mandataires TLS d'entreprise et l'en-tête "
                    "`Referer`. Sur le serveur Flask, une clé d'API permanente doit être stockée en base SQL sous forme d'empreinte `SHA-256` "
                    "(l'entropie de 256 bits aléatoires suffisant ici à rendre toute recherche exhaustive infaisable sans dérivation lente).\n\n"
                    "#### Élimination du canal auxiliaire temporel avec `hmac.compare_digest`\n\n"
                    "En CPython, l'opérateur `a == b` sur deux objets `str` ou `bytes` exécute `memcmp` avec arrêt immédiat au premier octet "
                    "divergent. Sur un réseau local ou par échantillonnage statistique de milliers de requêtes WSGI, un attaquant mesure la "
                    "différence de quelques dizaines de nanosecondes induite par un préfixe exact et reconstruit séquentiellement une clé de 32 "
                    "caractères en `32 x 256` essais au lieu de `256^32`. La primitive standard `hmac.compare_digest(a, b)` accumule un OU "
                    "exclusif bit à bit (`result |= x ^ y`) sur l'intégralité des séquences de même longueur.\n\n"
                    "```python\n"
                    "import hashlib, hmac\n"
                    "from flask import request, abort\n\n"
                    "def verifier_cle_partenaire(empreinte_attendue_hex: str) -> None:\n"
                    "    cle_brute = request.headers.get(\"X-API-Key\", \"\")\n"
                    "    empreinte_recue = hashlib.sha256(cle_brute.encode(\"utf-8\")).hexdigest()\n"
                    "    if not hmac.compare_digest(empreinte_recue, empreinte_attendue_hex):\n"
                    "        abort(401, description=\"Cle d'API absente ou invalide.\")\n"
                    "```\n\n"
                    "> [!TIP] Normalisation préalable de longueur par hachage\n"
                    "> Même `hmac.compare_digest` doit retourner immédiatement `False` lorsque les deux tampons n'ont pas la même taille en octets, "
                    "révélant la longueur exacte du secret. Comparer les condensats hexadécimaux `SHA-256` (toujours 64 octets ASCII) garantit une "
                    "durée d'exécution invariante quelle que soit la taille de l'entrée fournie par l'attaquant."
                )
            }
        ],
        "architecture_diagram": (
            "FLUX DE VÉRIFICATION D'IDENTITÉ MACHINE (X-API-KEY) & MOT DE PASSE SALÉ\n"
            "========================================================================\n\n"
            "  [1] VÉRIFICATION D'UNE CLÉ D'API EN TEMPS CONSTANT :\n"
            "  Client HTTP                                     Serveur Flask\n"
            "  En-tête : X-API-Key: isgp-live-98a7...  ----->  cle_client = request.headers.get('X-API-Key')\n"
            "                                                  cle_serveur = os.environ.get('PARTNER_API_KEY')\n"
            "                                                        |\n"
            "                                                  hmac.compare_digest(cle_client, cle_serveur)\n"
            "                                                  (Durée d'exécution constante : 0 fuite temporelle)\n\n"
            "  [2] STOCKAGE IRRÉVERSIBLE D'UN MOT DE PASSE UTILISATEUR (PBKDF2 / SCRYPT) :\n"
            "  Mot de passe clair : \"Formation2026!\"\n"
            "        +\n"
            "  Sel aléatoire (16 octets) : \"8f3d9a1c...\"\n"
            "        |\n"
            "        v  (600 000 itérations de hachage SHA-256)\n"
            "  Empreinte stockée en BDD : \"scrypt:32768:8:1$8f3d9a1c$e4b9012f8a...\" (Irréversible)"
        ),
        "reference_table": {
            "title": "Comparatif des Mécanismes Cryptographiques en Architecture API",
            "headers": ["Mécanisme Cryptographique", "Réversibilité", "Clé Secrète Requise ?", "Fonction Python Standard / Werkzeug", "Cas d'Usage en Architecture API"],
            "rows": [
                ["Encodage Base64", "Oui (immédiate, publique)", "Non", "`base64.urlsafe_b64encode()`", "Transport de données binaires ou JSON dans un en-tête HTTP"],
                ["Hachage rapide (SHA-256)", "Non (irréversible)", "Non", "`hashlib.sha256(data).hexdigest()`", "Empreinte d'intégrité d'un fichier ou d'une clé d'API haute entropie"],
                ["Hachage lent salé (PBKDF2 / Scrypt)", "Non (irréversible + lent)", "Non (Sel aléatoire inclus)", "`generate_password_hash()` / `check_password_hash()`", "Stockage sécurisé des mots de passe humains en base de données"],
                ["Signature HMAC-SHA256", "Non (vérification par recalcul)", "Oui (Clé secrète serveur)", "`hmac.new(key, msg, hashlib.sha256)`", "Signature de jetons JWT/Bearer et authentification de Webhooks"],
                ["Comparaison à temps constant", "N/A (Opérateur booléen)", "N/A", "`hmac.compare_digest(val1, val2)`", "Comparaison sécurisée de deux secrets (contre les Timing Attacks)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Stocker les mots de passe avec `hashlib.md5()` ou `sha256()` sans sel",
                "good": "Utiliser une fonction de dérivation lente avec salage automatique (`generate_password_hash`)",
                "why": "Les cartes graphiques (GPU) calculent plus de 50 milliards d'empreintes SHA-256 par seconde et cassent les mots de passe courants instantanément sans sel ni itérations lentes."
            },
            {
                "bad": "Passer la clé d'API dans les paramètres de requête URL (`GET /api/rapports?api_key=secret123`)",
                "good": "Transmettre systématiquement les clés et jetons dans les en-têtes HTTP (`X-API-Key` ou `Authorization`)",
                "why": "Les URLs complètes sont archivées en clair dans les fichiers `access.log` de tous les serveurs mandataires et dans l'historique navigateur."
            },
            {
                "bad": "Écrire `SECRET_KEY = 'mon_secret_de_prod'` directement dans `app.py` et pousser sur Git",
                "good": "Lire les secrets exclusivement depuis l'environnement système via `os.environ.get('FLASK_SECRET_KEY')`",
                "why": "Tout secret commité dans Git reste lisible indéfiniment dans l'historique `git log -p` même après suppression."
            }
        ],
        "practical_exercises": [
            "Générez deux empreintes successives du même mot de passe `\"Bootcamp2026\"` avec `generate_password_hash(\"Bootcamp2026\")` et affichez-les : expliquez pourquoi les deux chaînes obtenues sont totalement différentes et comment `check_password_hash()` parvient malgré tout à valider les deux.",
            "Créez un dictionnaire serveur associant trois clés d'API (stockées sous forme d'empreintes SHA-256) à trois noms d'applications partenaires, puis écrivez une route `/api/partenaire/commandes` qui identifie quel partenaire appelle l'API."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.2 : JETONS SIGNÉS (BEARER TOKENS / JWT) & EXPIRATION
    # =========================================================================
    "d4-l2": {
        "context": (
            "Lorsqu'un client lourd mobile ou une interface monopage (SPA React/Vue) dialogue avec une grappe de conteneurs Flask "
            "déployée derrière un répartiteur de charge L7 (Nginx, Envoy ou HAProxy), le paradigme historique des sessions en mémoire "
            "locale du processus WSGI s'effondre. Comme Gunicorn orchestre plusieurs processus travailleurs isolés (`pre-fork workers`) "
            "répartis sur différentes machines virtuelles sans mémoire vive partagée, conserver un dictionnaire Python d'identifiants de "
            "session en RAM provoquerait des rejets aléatoires dès qu'une requête subséquente atterrirait sur un worker distinct.\n\n"
            "L'architecture REST résout cette contrainte d'échelle horizontale par le transport d'état certifié côté client (*Stateless "
            "Token Authentication*). À l'issue d'une vérification initiale des identifiants sur `POST /api/v1/auth/login`, le serveur "
            "émet un jeton porteur signé cryptographiquement (`JWT` selon la RFC 7519 ou jeton horodaté `itsdangerous` natif à Flask). "
            "Chaque worker Gunicorn peut dès lors valider l'authenticité et la fraîcheur temporelle de ce jeton de manière autonome en "
            "temps constant CPU, sans aucune lecture SQL ou réseau intermédiaire."
        ),
        "deep_sections": [
            {
                "heading": "1. Anatomie binaire d'un jeton signé : `JWT` (RFC 7519) et `itsdangerous.URLSafeTimedSerializer`",
                "body": (
                    "#### Structure tripartite et sérialisation déterministe\n\n"
                    "Un *JSON Web Token* conforme à la RFC 7519 concatène trois segments encodés en `Base64URL` sans bourrage (`=`), séparés par "
                    "le délimiteur ASCII `.` : l'en-tête JOSE (`Header`, déclarant par exemple `{\"alg\": \"HS256\", \"typ\": \"JWT\"}`), la "
                    "charge utile des assertions d'identité (`Payload` ou *Claims* normalisés tels que `sub`, `iat`, `exp`, `iss`, `aud`), et le "
                    "code d'authentification `HMAC-SHA256` calculé sur la chaîne `ASCII(Base64URL(Header) + '.' + Base64URL(Payload))` à l'aide "
                    "de `app.config['SECRET_KEY']`.\n\n"
                    "Dans l'écosystème natif Pallets (Flask / Werkzeug), la bibliothèque `itsdangerous` applique exactement le même principe "
                    "mathématique via `URLSafeTimedSerializer`. Elle sérialise le dictionnaire Python en JSON compact, lui adjoint un horodatage "
                    "binaire sur 64 bits encodé en Base64URL par `TimestampSigner`, puis dérive une clé de signature dédiée via `HMAC` combinant "
                    "`SECRET_KEY` et un espace de noms logique (`salt`).\n\n"
                    "```python\n"
                    "from flask import current_app\n"
                    "from itsdangerous import URLSafeTimedSerializer\n\n"
                    "def emettre_bearer_token(user_id: str, role: str) -> str:\n"
                    "    s = URLSafeTimedSerializer(current_app.config[\"SECRET_KEY\"], salt=\"bearer-access-v1\")\n"
                    "    return s.dumps({\"sub\": user_id, \"role\": role})\n"
                    "```"
                )
            },
            {
                "heading": "2. Théorème fondamental d'audit : Signature d'intégrité (`JWS`) vs Chiffrement de confidentialité (`JWE`)",
                "body": (
                    "#### Visibilité publique de la charge utile encodée en Base64URL\n\n"
                    "L'erreur d'architecture la plus répandue lors des revues de sécurité consiste à supposer qu'un jeton signé dissimule son "
                    "contenu. Un jeton `JWS` (RFC 7515) ou un jeton `itsdangerous` garantit exclusivement l'**intégrité** et l'**authenticité de "
                    "l'émetteur**, nullement la **confidentialité**. Quiconque intercepte la chaîne dans les outils de développement du "
                    "navigateur ou dans un journal de débogage peut exécuter `base64.urlsafe_b64decode()` et lire intégralement le JSON des "
                    "*claims* sans disposer de `SECRET_KEY`.\n\n"
                    "> [!IMPORTANT] Interdiction absolue de données sensibles dans le Payload\n"
                    "> Ne sérialisez jamais de secret métier, d'identifiant bancaire, de jeton amont tiers ou de données personnelles "
                    "réglementées à l'intérieur d'un jeton signé non chiffré (`JWS` / `itsdangerous`). Limitez strictement la charge utile au "
                    "sujet technique opaque (`sub`), aux rôles (`role`) et aux portées d'autorisation (`scopes`).\n\n"
                    "En revanche, toute altération d'un seul bit du segment `Payload` par un attaquant (par exemple remplacer `\"lecteur\"` par "
                    "`\"admin\"` puis ré-encoder en Base64URL) produit un condensat `HMAC-SHA256` divergent lors du recalcul serveur via "
                    "`hmac.compare_digest`. Sans connaissance des 256 bits d'entropie de `SECRET_KEY`, forger une signature valide demeure "
                    "calculatoirement infaisable. Notez également que dans les implémentations JWT externes (`PyJWT`), l'algorithme attendu doit "
                    "toujours être figé explicitement côté serveur (`algorithms=['HS256']`) afin de prévenir l'attaque historique `alg: none`."
                )
            },
            {
                "heading": "3. Protocole de transport `RFC 6750` (`Authorization: Bearer`) et hiérarchie d'exceptions temporelles",
                "body": (
                    "#### Sémantique d'en-tête HTTP et exigence TLS\n\n"
                    "La norme IETF RFC 6750 normalise la présentation d'un jeton d'accès dans l'en-tête de requête HTTP `Authorization` sous le "
                    "schéma `Bearer` (*au porteur*) : la simple détention du jeton confère les privilèges qui y sont attachés, sans preuve de "
                    "possession cryptographique additionnelle au niveau socket. Le transport en clair sur HTTP non chiffré expose par conséquent "
                    "le jeton à une capture passive immédiate ; TLS 1.2+ constitue un prérequis non négociable.\n\n"
                    "> « Tout détenteur d'un jeton porteur (Bearer Token) peut l'utiliser pour accéder aux ressources associées sans démontrer la "
                    "possession d'une clé cryptographique. » — IETF RFC 6750, Section 1.2\n\n"
                    "```http\n"
                    "GET /api/v1/profil HTTP/1.1\n"
                    "Host: api.isgp.dz\n"
                    "Authorization: Bearer eyJzdWIiOiJhbWluZSIsInJvbGUiOiJhZG1pbiJ9.Z5x8Qw.7kL9p_2mXv...\n\n"
                    "HTTP/1.1 401 Unauthorized\n"
                    "WWW-Authenticate: Bearer realm=\"isgp-api\", error=\"invalid_token\", error_description=\"Token expired\"\n"
                    "Content-Type: application/problem+json\n"
                    "```\n\n"
                    "#### Ordre d'interception dans `itsdangerous` (`SignatureExpired` hérite de `BadSignature`)\n\n"
                    "Lors de l'appel à `serializer.loads(token, max_age=900)`, `itsdangerous` valide d'abord le `HMAC` en temps constant avant de "
                    "soustraire l'horodatage signé à l'horloge monotone/UTC du serveur. Dans l'arbre d'héritage Python d'`itsdangerous`, la "
                    "classe `SignatureExpired` est une sous-classe directe de `BadSignature`. Un bloc `try / except` doit donc impérativement "
                    "capturer `SignatureExpired` en premier lieu pour restituer un code diagnostic distinct permettant au client frontal de "
                    "déclencher silencieusement son flux de rafraîchissement."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE VIE D'UN JETON SIGNÉ STATELESS (BEARER TOKEN / JWT)\n"
            "============================================================\n\n"
            "  [ÉTAPE 1 : CONNEXION INITIALE (POST /api/login)]\n"
            "  Client Mobile / Web                              Serveur Flask (Stateless)\n"
            "  {\"username\": \"amine\", \"password\": \"...\"}  -----> 1. Vérifie check_password_hash()\n"
            "                                                   2. Crée Payload {\"sub\": \"amine\", \"role\": \"admin\"}\n"
            "                                                   3. Signe avec SECRET_KEY + Timestamp actuel\n"
            "  Stocke le token en mémoire               <-----  200 OK : {\"access_token\": \"eyJ...Signature\"}\n\n"
            "  [ÉTAPE 2 : REQUÊTE SUR ROUTE PROTÉGÉE (GET /api/profil)]\n"
            "  En-tête HTTP :\n"
            "  Authorization: Bearer eyJ...Signature     -----> 1. Extrait la chaîne après \"Bearer \"\n"
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
            "Prenez un jeton généré par la route `POST /api/login`, modifiez un seul caractère au milieu de la chaîne, puis envoyez-le dans `Authorization: Bearer ...` : observez comment le serveur détecte l'altération.",
            "Modifiez la route `/api/profil-protege` pour renvoyer également dans la réponse JSON le nombre de secondes restantes avant l'expiration du jeton (en passant `return_timestamp=True` à `serializer.loads()`)."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.3 : AUTHENTIFICATION (AUTHN / 401) VS AUTORISATION (AUTHZ / 403, RBAC, SCOPES, BOLA)
    # =========================================================================
    "d4-l3": {
        "context": (
            "En architecture de sécurité des systèmes distribués, l'amalgame entre **Authentification (`AuthN`)** et **Autorisation "
            "(`AuthZ`)** constitue la cause racine de la vulnérabilité classée au premier rang mondial du référentiel **OWASP API "
            "Security Top 10 (2023)** : *API1:2023 — Broken Object Level Authorization (`BOLA`)*, historiquement désignée sous "
            "l'acronyme *IDOR* (*Insecure Direct Object Reference*).\n\n"
            "Une multitude de services Flask en production valident scrupuleusement la signature cryptographique du jeton `Bearer` "
            "entrant (`AuthN`), puis exécutent aveuglément une requête SQL `SELECT` ou `DELETE` paramétrée par l'identifiant `<int:id>` "
            "extrait de l'URI Werkzeug, sans jamais démontrer que le sujet identifié (`sub`) détient un droit d'accès légitime sur cet "
            "enregistrement précis (`AuthZ`). Ce chapitre formalise la disjonction protocolaire entre `401 Unauthorized` et `403 "
            "Forbidden` selon la RFC 9110, articule les trois strates d'autorisation modernes (**RBAC**, **Scopes OAuth 2.0** et "
            "**propriété d'objet Anti-BOLA**) et détaille l'isolation mémoire de l'identité courante via les proxies `ContextVar` de "
            "Flask (`flask.g`)."
        ),
        "deep_sections": [
            {
                "heading": "1. Disjonction sémantique `RFC 9110` : `AuthN` (`401 Unauthorized`) vs `AuthZ` (`403 Forbidden`)",
                "body": (
                    "#### Pourquoi `401 Unauthorized` signifie en réalité *Unauthenticated*\n\n"
                    "Malgré son libellé historique hérité de HTTP/1.0, le code `401 Unauthorized` défini à la section 15.5.2 de la RFC 9110 "
                    "signale exclusivement un défaut d'**authentification (`AuthN`)** : la requête est dépourvue d'informations d'identification "
                    "valides (en-tête `Authorization` omis, signature `HMAC` corrompue ou jeton expiré). La norme exige d'ailleurs que toute "
                    "réponse `401` comporte au moins un en-tête `WWW-Authenticate` précisant le défi d'authentification attendu (par exemple "
                    "`Bearer realm=\"isgp-api\"`), invitant le client à renouveler son jeton ou à solliciter une reconnexion.\n\n"
                    "> « Le code d'état 403 (Forbidden) indique que le serveur a compris la requête mais refuse de l'exécuter. Contrairement à "
                    "401, l'authentification du client est connue et une nouvelle authentification ne modifiera pas la décision de refus. » — "
                    "IETF RFC 9110, Section 15.5.4\n\n"
                    "Lorsque l'étape `AuthN` réussit et résout l'identité `sub=\"yasmine\"`, le pipeline entre dans la phase d'**autorisation "
                    "(`AuthZ`)**. Si les règles métier interdisent l'opération sollicitée, émettre un `401` constitue un bogue grave côté "
                    "client : les intercepteurs HTTP des applications React ou mobiles interprètent `401` comme une expiration de session et "
                    "déclenchent en boucle un appel `POST /api/v1/auth/refresh` inutile, voire purgent la session locale de l'utilisateur. Seul "
                    "`403 Forbidden` traduit fidèlement un refus de privilège définitif pour l'identité courante."
                )
            },
            {
                "heading": "2. Défense en profondeur `AuthZ` : Matrice RBAC, Portées OAuth 2.0 (`Scopes`) et Prédicat Anti-BOLA",
                "body": (
                    "#### Les trois plans orthogonaux de décision d'accès\n\n"
                    "Une architecture d'autorisation robuste évalue séquentiellement trois prédicats orthogonaux avant d'autoriser une mutation "
                    "ou une projection SQL. Le premier plan est le contrôle d'accès basé sur les rôles (**RBAC**, *Role-Based Access Control*), "
                    "qui gouverne l'accès fonctionnel aux routes (*Function-Level Authorization* — défense contre OWASP API5:2023 `BFLA`) selon "
                    "le statut organisationnel du sujet (`lecteur`, `formateur`, `admin`).\n\n"
                    "Le deuxième plan évalue les **portées déléguées (`Scopes` OAuth 2.0, RFC 6749 Section 3.3)** portées par le jeton lui-même "
                    "(par exemple `bulletins:read` sans `bulletins:write`). Un administrateur qui génère un jeton restreint pour un connecteur "
                    "de reporting limite ainsi la surface d'impact du jeton selon le principe du moindre privilège : l'autorisation effective "
                    "est l'intersection des droits du compte humain et des *scopes* accordés au jeton.\n\n"
                    "Le troisième plan, le plus critique, applique le **contrôle au niveau de l'instance d'objet (`Anti-BOLA`)** directement sur "
                    "la ligne chargée depuis la base relationnelle ou dans la clause `WHERE` SQL. Lorsqu'un étudiant authentifié appelle "
                    "`GET /api/v1/bulletins/8492`, le serveur doit vérifier explicitement `bulletin.etudiant_id == g.identite['sub']` (sauf "
                    "dérogation explicite de rôle `admin`), faute de quoi une simple boucle `for id in range(1, 100000)` permet d'exfiltrer "
                    "l'intégralité de la table."
                )
            },
            {
                "heading": "3. Propagation d'identité sans fuite inter-requêtes via `flask.g` et `ContextVar` (`LocalProxy`)",
                "body": (
                    "#### Isolation mémoire sous Gunicorn `sync` et `gthread`\n\n"
                    "Stocker l'utilisateur authentifié dans une variable globale de module Python (`UTILISATEUR_COURANT = payload`) provoquerait "
                    "une collision catastrophique de sessions entre requêtes concurrentes dès que Gunicorn s'exécute en mode multi-threads "
                    "(`--worker-class gthread --threads 8`) ou asynchrone. Depuis Flask 2.2+ et Werkzeug 2.2+, les objets `flask.g`, `request` "
                    "et `current_app` sont implémentés comme des mandataires `werkzeug.local.LocalProxy` adossés aux variables de contexte "
                    "natives `contextvars.ContextVar` de Python (PEP 567).\n\n"
                    "```python\n"
                    "from flask import g, abort\n\n"
                    "def charger_bulletin_securise(bulletin_id: int) -> dict:\n"
                    "    if \"bulletins:read\" not in g.identite.get(\"scopes\", ()):\n"
                    "        abort(403, description=\"Portee OAuth 'bulletins:read' requise.\")\n"
                    "    row = db_fetch_bulletin(bulletin_id)\n"
                    "    if row is None:\n"
                    "        abort(404)\n"
                    "    if g.identite[\"role\"] != \"admin\" and row[\"owner_sub\"] != g.identite[\"sub\"]:\n"
                    "        abort(403, description=\"Violation Anti-BOLA : acces interdit au dossier d'un tiers.\")\n"
                    "    return row\n"
                    "```\n\n"
                    "> [!IMPORTANT] Cycle de vie borné du contexte de requête Flask\n"
                    "> À chaque requête WSGI entrante (`Flask.wsgi_app`), Flask pousse un `RequestContext` isolé dans une `ContextVar` dédiée au "
                    "thread ou à la coroutine en cours, puis le détruit systématiquement dans le bloc `finally` en fin de requête. Tout attribut "
                    "attaché à `g.identite` est par construction invisible des autres threads du worker et purgé avant le traitement de la "
                    "requête HTTP suivante."
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
                "bad": "Masquer le bouton « Supprimer » dans l'interface React/mobile sans vérifier le rôle et le propriétaire côté serveur Flask",
                "good": "Appliquer systématiquement les contrôles `AuthZ` (RBAC, Scopes et Anti-BOLA) dans le code Python du serveur",
                "why": "Un attaquant utilise `curl` directement et contourne totalement l'interface graphique du navigateur."
            },
            {
                "bad": "Vérifier que le jeton est valide sur `GET /api/bulletins/<id>` sans vérifier à qui appartient le bulletin `<id>`",
                "good": "Comparer systématiquement `identite['sub'] == bulletin['owner']` (ou `identite['role'] == 'admin'`)",
                "why": "L'absence de contrôle de propriété sur l'objet (BOLA / IDOR) permet à tout utilisateur connecté d'aspirer les dossiers de tous les autres utilisateurs."
            }
        ],
        "practical_exercises": [
            "Utilisez le laboratoire ou `curl` pour tester les 4 profils de jetons sur `/api/sandbox/authz-demo` (`anonyme`, `etudiant_lecture`, `formateur_restreint`, `admin_complet`) en faisant varier l'action (`lecture` vs `ecriture`) et la cible (`propre_dossier` vs `dossier_tiers`).",
            "Écrivez une fonction de contrôle `verifier_acces_document(identite_jeton, document)` qui autorise la lecture si l'utilisateur est propriétaire du document, s'il appartient au même département avec le rôle `manager`, ou s'il est `admin`."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.4 : ROTATION ACCESS / REFRESH TOKENS & DÉCORATEUR @EXIGER_ROLE
    # =========================================================================
    "d4-l4": {
        "context": (
            "La validation purement cryptographique d'un jeton d'accès sans état (*Stateless Access Token*) introduit un compromis "
            "fondamental entre latence de vérification et capacité de révocation immédiate. Un jeton d'accès valable trente jours "
            "évite toute friction ergonomique, mais laisse un employé révoqué ou un attaquant ayant dérobé le jeton opérer librement "
            "sur l'ensemble des workers Gunicorn jusqu'à l'échéance mathématique du champ `exp`. Inversement, abaisser la durée de vie "
            "à dix minutes sans mécanisme de renouvellement transparent forcerait l'utilisateur à ressaisir son secret six fois par heure.\n\n"
            "Le standard **OAuth 2.0 (RFC 6749, Section 1.5)** ainsi que son profil de sécurité **RFC 9700 (OAuth 2.0 Security Best "
            "Current Practice)** résolvent cette tension architecturale en scindant le cycle de session en deux artefacts aux "
            "propriétés distinctes : un **`Access Token` éphémère** vérifié exclusivement en mémoire vive sur les routes métier, et un "
            "**`Refresh Token` à long terme** confiné à l'unique route de renouvellement et soumis à une rotation atomique avec "
            "révocation côté serveur. Ce chapitre formalise également la factorisation transversale de ces contrôles dans Flask via des "
            "fabriques de décorateurs préservant la table de routage Werkzeug grâce à `@functools.wraps`."
        ),
        "deep_sections": [
            {
                "heading": "1. Séparation cryptographique des domaines : `Access Token` éphémère vs `Refresh Token` révocable",
                "body": (
                    "#### Dérivation de sous-clés indépendantes par `salt` dans `itsdangerous`\n\n"
                    "Lors d'une authentification initiale sur `POST /api/v1/auth/login`, le serveur émet une paire de jetons aux horizons "
                    "temporels asymétriques. L'`Access Token` (TTL de 300 à 900 secondes) accompagne chaque appel métier dans l'en-tête "
                    "`Authorization: Bearer` ; sa vérification ne sollicite aucune entrée/sortie réseau ou disque. Le `Refresh Token` (TTL de "
                    "7 à 30 jours, doté d'un identifiant unique `jti` généré via `secrets.token_hex(16)`) n'est jamais présenté aux endpoints "
                    "métier : il est réservé aux routes d'infrastructure `/api/v1/auth/refresh` et `/api/v1/auth/revoke`.\n\n"
                    "Pour interdire mathématiquement toute substitution croisée (*Token Confusion Attack*, où un attaquant injecterait son "
                    "`Refresh Token` de 30 jours dans l'en-tête `Bearer` d'une route métier), `itsdangerous` dérive deux clés `HMAC` distinctes "
                    "à partir de la même `SECRET_KEY` en isolant le paramètre `salt` (`salt='access-v1'` contre `salt='refresh-v1'`). Un "
                    "`Refresh Token` soumis au vérificateur d'accès échoue ainsi instantanément avec `BadSignature`."
                )
            },
            {
                "heading": "2. Révocation atomique (`Redis SETEX`) et détection de réutilisation (*Refresh Token Rotation*)",
                "body": (
                    "#### Confinement de l'état de session au seul point de renouvellement\n\n"
                    "Concentrer la consultation d'état sur `POST /api/v1/auth/refresh` préserve 99 % du trafic API de toute lecture en base de "
                    "données tout en rétablissant une révocation forte à l'échelle de quelques minutes. Lorsqu'un utilisateur se déconnecte ou "
                    "qu'un administrateur suspend un compte, l'identifiant `jti` (ou le condensat `SHA-256` du `Refresh Token`) est inscrit dans "
                    "un magasin clé-valeur partagé entre tous les workers Gunicorn — typiquement **Redis** via `SETEX revoked:<jti> <ttl_restant> 1`, "
                    "dont l'expiration automatique empêche toute croissance non bornée de la mémoire.\n\n"
                    "> « Les serveurs d'autorisation DOIVENT soit utiliser des jetons de rafraîchissement liés cryptographiquement au client, "
                    "soit appliquer la rotation des jetons de rafraîchissement à chaque échange. » — IETF RFC 9700, Section 4.14.2\n\n"
                    "Dans un schéma de **rotation stricte**, chaque appel valide à `/api/v1/auth/refresh` invalide immédiatement le `Refresh "
                    "Token` entrant et délivre simultanément un nouvel `Access Token` et un nouveau `Refresh Token` appartenant à la même lignée "
                    "(`family_id`). Si un `Refresh Token` déjà consommé est présenté une seconde fois, le serveur détecte une compromission "
                    "(vol du jeton en parallèle du client légitime) et révoque instantanément toute la famille de jetons associée."
                )
            },
            {
                "heading": "3. Fabriques de décorateurs Flask (`@exiger_role`) et invariant Werkzeug `@functools.wraps`",
                "body": (
                    "#### Mécanisme interne d'enregistrement dans `app.url_map` et `app.view_functions`\n\n"
                    "Dupliquer la logique d'extraction d'en-tête `Bearer`, de désérialisation `itsdangerous` et de contrôle RBAC en tête de "
                    "chaque fonction de vue enfreint l'orthogonalité architecturale et introduit un risque élevé d'oubli sur de nouvelles routes. "
                    "Python résout ce besoin par une fermeture lexicale à trois niveaux (*Parameterized Decorator Factory*) qui intercepte "
                    "l'appel WSGI avant l'exécution de la vue et peuple `flask.g.identite`.\n\n"
                    "```python\n"
                    "from functools import wraps\n"
                    "from flask import request, g, current_app, abort\n"
                    "from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature\n\n"
                    "def exiger_role(*roles_autorises: str):\n"
                    "    def decorateur(vue_cible):\n"
                    "        @wraps(vue_cible)\n"
                    "        def wrapper(*args, **kwargs):\n"
                    "            auth = request.headers.get(\"Authorization\", \"\")\n"
                    "            if not auth.startswith(\"Bearer \"):\n"
                    "                abort(401, description=\"Jeton Bearer manquant.\")\n"
                    "            s = URLSafeTimedSerializer(current_app.config[\"SECRET_KEY\"], salt=\"access-v1\")\n"
                    "            try:\n"
                    "                g.identite = s.loads(auth[7:].strip(), max_age=900)\n"
                    "            except SignatureExpired:\n"
                    "                abort(401, description=\"Access token expire.\")\n"
                    "            except BadSignature:\n"
                    "                abort(401, description=\"Signature de jeton invalide.\")\n"
                    "            if roles_autorises and g.identite.get(\"role\") not in roles_autorises:\n"
                    "                abort(403, description=\"Role insuffisant pour cette ressource.\")\n"
                    "            return vue_cible(*args, **kwargs)\n"
                    "        return wrapper\n"
                    "    return decorateur\n"
                    "```\n\n"
                    "> [!WARNING] Collision d'endpoints Flask en l'absence de `@functools.wraps`\n"
                    "> Lorsque `@app.get('/chemin')` enregistre une vue sans paramètre `endpoint=` explicite, Flask indexe son dictionnaire "
                    "interne `app.view_functions` par la chaîne `f.__name__`. Omettre `@wraps(vue_cible)` laisse `wrapper.__name__ == 'wrapper'` "
                    "sur toutes les vues protégées : dès l'import de la seconde route décorée, Flask interrompt le démarrage du worker avec "
                    "`AssertionError: View function mapping is overwriting an existing endpoint function: wrapper`."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE ROTATION ACCESS TOKEN / REFRESH TOKEN & RÉVOCATION\n"
            "===========================================================\n\n"
            "  Client                                      Serveur Flask\n"
            "  1. POST /api/auth/login              -----> Vérifie identifiants\n"
            "     Reçoit Access (15m) + Refresh (7j)<----- Signe Access (salt='access') & Refresh (salt='refresh')\n"
            "        |\n"
            "  2. GET /api/formations (Pendant 15m) -----> @exiger_role vérifie Access Token -> 200 OK\n"
            "        |\n"
            "  3. [16 minutes plus tard : Access Token expiré -> 401 SignatureExpired]\n"
            "        |\n"
            "  4. POST /api/auth/refresh            -----> 1. Vérifie signature avec salt='refresh'\n"
            "     (Envoie le Refresh Token)                2. Vérifie Refresh NOT IN REVOKED_TOKENS\n"
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
                "bad": "Oublier `@wraps(f)` de `functools` lors de l'écriture d'un décorateur Flask personnalisé",
                "good": "Toujours décorer la fonction interne `wrapper` avec `@wraps(f)`",
                "why": "Flask enregistre chaque route sous le nom `f.__name__` ; sans `@wraps(f)`, toutes les fonctions décorées s'appellent `wrapper` et provoquent une `AssertionError` au démarrage."
            }
        ],
        "practical_exercises": [
            "Implémentez la **rotation complète du Refresh Token** dans `POST /api/auth/refresh` : chaque fois qu'un `Refresh Token` est utilisé pour obtenir un nouvel `Access Token`, ajoutez immédiatement l'ancien `Refresh Token` dans `REVOKED_TOKENS` et renvoyez à la fois un nouvel `Access Token` et un nouveau `Refresh Token`.",
            "Enrichissez le décorateur `@exiger_role` pour qu'il injecte automatiquement le dictionnaire `identite` décodé dans `flask.g.utilisateur_courant`, afin que la route puisse l'utiliser sans redécoder le jeton."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.5 : LIMITATION DE DÉBIT (RATE LIMITING / 429) & QUOTAS
    # =========================================================================
    "d4-l5": {
        "context": (
            "Une architecture d'authentification et d'autorisation irréprochable ne protège nullement un service WSGI contre "
            "l'épuisement de ses ressources physiques (concurrence des processus Gunicorn, pool de descripteurs PostgreSQL, bande "
            "passante sortante) ni contre l'explosion des coûts d'infrastructure facturés à la requête (passerelles SMS, moteurs "
            "d'inférence LLM, APIs bancaires). Qu'il s'agisse d'une attaque par dictionnaire distribué sur `POST /api/v1/auth/login` "
            "ou d'une régression logicielle chez un partenaire exécutant une boucle infinie non temporisée, l'absence de régulation de "
            "cadence (*Rate Limiting* — classée **OWASP API4:2023 Unrestricted Resource Consumption**) entraîne la famine immédiate des "
            "consommateurs légitimes.\n\n"
            "L'ingénierie de résilience impose dès lors un mécanisme de contrôle d'admission déterministe adossé au code d'état HTTP "
            "**`429 Too Many Requests` (RFC 6585)**, combinant un algorithme de comptage temporel précis, une signalisation proactive "
            "de rétro-pression (*Backpressure*) via l'en-tête `Retry-After`, et une gestion cohérente de l'état partagé entre les "
            "workers pre-fork de Gunicorn."
        ),
        "deep_sections": [
            {
                "heading": "1. Modèles algorithmiques de régulation : Fenêtre Fixe, Journal Glissant (*Sliding Window Log*) et Seau à Jetons",
                "body": (
                    "#### Anomalie aux frontières de la fenêtre fixe vs exactitude de la fenêtre glissante\n\n"
                    "Le compteur à fenêtre fixe (*Fixed Window Counter*), qui incrémente une clé indexée sur la minute entière "
                    "`int(time.time() // 60)`, souffre d'une vulnérabilité structurelle aux frontières d'intervalle : sous un quota nominal de "
                    "100 requêtes par minute, un client émettant une rafale de 100 appels à `14:00:59.500` suivie de 100 appels à "
                    "`14:01:00.100` impose 200 requêtes en 600 millisecondes au pool WSGI, doublant le débit crête toléré.\n\n"
                    "Le journal à fenêtre glissante (*Sliding Window Log*), mis en œuvre via `collections.deque` en mémoire locale ou un "
                    "ensemble trié Redis (`ZREMRANGEBYSCORE` + `ZCARD` exécutés atomiquement dans un script Lua), conserve l'horodatage exact "
                    "`t` de chaque requête acceptée. À l'instant `T`, toute entrée antérieure à `T - W` est purgée avant l'évaluation du "
                    "cardinal restant, garantissant mathématiquement le respect du plafond sur tout intervalle glissant `[T - W, T]`. Quant à "
                    "l'algorithme du **Seau à Jetons (*Token Bucket*)**, privilégié par Nginx (`limit_req_zone`) et Envoy, il dissocie le débit "
                    "moyen de régénération `R` (jetons/seconde) de la capacité d'absorption de rafale `B` (*burst*), lissant le trafic légitime "
                    "sans pénaliser les chargements initiaux d'interfaces riches.\n\n"
                    "> [!WARNING] Incohérence des compteurs en RAM sous Gunicorn pre-fork\n"
                    "> Lorsque Gunicorn démarre `--workers 4`, l'appel système `fork()` dote chaque processus enfant d'un espace d'adressage "
                    "Python privé. Un dictionnaire `HISTORIQUE_APPELS` stocké en mémoire globale de module autorise de facto jusqu'à `4 * "
                    "Quota` requêtes selon l'ordonnancement des sockets par le noyau Linux. En production multi-workers ou multi-nœuds, "
                    "externalisez systématiquement l'état des compteurs dans Redis (`Flask-Limiter` avec backend `redis://`)."
                )
            },
            {
                "heading": "2. Contrat HTTP de rétro-pression : `429 Too Many Requests`, `Retry-After` et en-têtes de télémétrie",
                "body": (
                    "#### Coopération protocolaire avec les SDK consommateurs\n\n"
                    "Rejeter un dépassement de cadence avec `500 Internal Server Error` fausse les sondes d'alerte SRE, tandis que `403 "
                    "Forbidden` indique à tort un défaut permanent d'habilitation. La RFC 6585 introduit le statut `429 Too Many Requests` "
                    "spécifiquement pour ordonner au client de ralentir ses émissions tout en lui fournissant dans `Retry-After` (RFC 9110, "
                    "Section 10.2.3) le délai minimal d'attente exprimé en secondes entières avant nouvelle tentative.\n\n"
                    "> « Les réponses utilisant le code d'état 429 DEVRAIENT inclure un en-tête Retry-After indiquant combien de temps attendre "
                    "avant d'effectuer une nouvelle requête. » — IETF RFC 6585, Section 4\n\n"
                    "```http\n"
                    "HTTP/1.1 429 Too Many Requests\n"
                    "Content-Type: application/problem+json\n"
                    "Retry-After: 18\n"
                    "X-RateLimit-Limit: 60\n"
                    "X-RateLimit-Remaining: 0\n"
                    "X-RateLimit-Reset: 1762884018\n\n"
                    "{\"type\": \"https://api.isgp.dz/errors/rate-limit-exceeded\", \"title\": \"Too Many Requests\", \"status\": 429}\n"
                    "```\n\n"
                    "Exposer les en-têtes `X-RateLimit-Limit`, `X-RateLimit-Remaining` et `X-RateLimit-Reset` (ou les nouveaux champs unifiés "
                    "`RateLimit` et `RateLimit-Policy` en cours de standardisation IETF) sur les réponses `200 OK` permet en outre aux clients "
                    "batch d'autoréguler préventivement leur cadence (*Client-Side Pacing*) avant même d'atteindre le seuil de coupure."
                )
            },
            {
                "heading": "3. Clé de partitionnement du quota : Identité authentifiée vs `request.remote_addr` sous `ProxyFix`",
                "body": (
                    "#### Pièges du NAT d'entreprise et usurpation de `X-Forwarded-For`\n\n"
                    "Le choix du discriminant de comptage gouverne à la fois l'équité métier et la résistance au contournement. Sur les routes "
                    "authentifiées, partitionner le compteur par identifiant cryptographique vérifié (`g.identite['sub']` ou empreinte de "
                    "`X-API-Key`) offre une isolation granulaire par client et permet d'appliquer des paliers contractuels différenciés "
                    "(`Standard` contre `Entreprise`) indépendamment de la topologie réseau.\n\n"
                    "Sur les endpoints publics sensibles tels que `POST /api/v1/auth/login`, le serveur doit se replier sur l'adresse IP "
                    "cliente. Toutefois, derrière un proxy inverse Nginx, la connexion TCP directe reçue par Gunicorn provient toujours de "
                    "`127.0.0.1` (ou de l'IP interne du pod Ingress), ce qui regrouperait tous les utilisateurs mondiaux dans le même quota "
                    "unique ! À l'inverse, lire directement `request.headers.get('X-Forwarded-For')` sans filtrage permet à un attaquant "
                    "d'envoyer un en-tête forgé aléatoire à chaque requête pour contourner indéfiniment le limiteur.\n\n"
                    "```python\n"
                    "from werkzeug.middleware.proxy_fix import ProxyFix\n\n"
                    "# Fait confiance exactement a 1 saut proxy amont (Nginx) pour resoudre request.remote_addr\n"
                    "app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)\n"
                    "```\n\n"
                    "> [!TIP] Seuils adaptatifs face aux passerelles CGNAT et campus\n"
                    "> Cinq cents collaborateurs d'un même ministère ou campus universitaire partagent fréquemment une unique adresse IPv4 "
                    "publique sortante (NAT). Sur `/login`, combinez un plafond large par adresse IP avec un plafond strict sur le couple "
                    "`(ip_cliente, identifiant_cible)` afin de bloquer le *Credential Stuffing* sans verrouiller l'établissement entier."
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
                "bad": "En production multi-processus (Gunicorn à 4 workers), stocker uniquement le compteur en RAM Python locale",
                "good": "En production distribuée, centraliser les compteurs dans un store partagé atomique comme **Redis** ou Nginx",
                "why": "Chaque worker Gunicorn ayant sa propre mémoire RAM isolée, un compteur en mémoire locale permettrait au client d'effectuer `4 x Quota` requêtes."
            }
        ],
        "practical_exercises": [
            "Adaptez l'algorithme de Rate Limiting du chapitre pour appliquer un **quota différencié par niveau d'abonnement** : `5 requêtes/min` si l'en-tête `X-Plan` vaut `standard`, et `20 requêtes/min` s'il vaut `premium`.",
            "Ajoutez un nettoyage périodique automatique des clés clientes inactives depuis plus de 60 secondes afin que le dictionnaire `HISTORIQUE_APPELS` ne grossisse pas indéfiniment en mémoire."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.6 : SÉCURITÉ PÉRIMÉTRIQUE : CORS, SIGNATURES WEBHOOK HMAC & TAILLE MAXIMALE (413)
    # =========================================================================
    "d4-l6": {
        "context": (
            "Lorsqu'un service Flask franchit l'étape du déploiement en environnement réel, trois mécanismes de frontière gouvernent "
            "son interaction avec les moteurs de navigation Web, les prestataires événementiels tiers et les couches d'entrée/sortie "
            "WSGI. Premièrement, la politique d'isolation inter-origines (**CORS**, *Cross-Origin Resource Sharing*) explique pourquoi "
            "un endpoint irréprochable sous `curl` échoue instantanément lorsqu'une application React hébergée sur un sous-domaine "
            "distinct tente d'en lire la réponse dans Chromium ou Gecko.\n\n"
            "Deuxièmement, l'architecture orientée événements par **Webhooks entrants** (notifications asynchrones de paiement Stripe, "
            "Chargily ou événements GitHub) inverse la topologie client-serveur et impose de certifier cryptographiquement l'origine "
            "de chaque requête `POST` sur le flux brut d'octets `wsgi.input`. Troisièmement, la défense de la mémoire vive des workers "
            "Gunicorn exige de borner en amont le volume des charges utiles entrantes via `MAX_CONTENT_LENGTH` (`413 Content Too "
            "Large`) avant toute allocation de tampon Python."
        ),
        "deep_sections": [
            {
                "heading": "1. Modèle de sécurité navigateur : *Same-Origin Policy* (RFC 6454), `CORS` et négociation *Preflight* `OPTIONS`",
                "body": (
                    "#### Pourquoi CORS protège le navigateur de l'utilisateur et n'affecte jamais `curl`\n\n"
                    "Conformément à la RFC 6454, une origine Web est le triplet strict `(schéma, hôte, port)`. Par défaut, la *Same-Origin "
                    "Policy* (SOP) interdit au moteur JavaScript d'une page chargée depuis `https://portail.isgp.dz:443` de lire le corps HTTP "
                    "renvoyé par `https://api.isgp.dz:443`, afin d'empêcher un onglet malveillant d'exploiter l'ambiance réseau ou les cookies "
                    "du poste client. Un outil en ligne de commande tel que `curl` ou un worker Python backend n'exécutant aucun code tiers non "
                    "fiable pour le compte d'un internaute, il ignore légitimement ces en-têtes.\n\n"
                    "> « Le protocole CORS ne remplace jamais l'authentification côté serveur ; il indique uniquement au navigateur quelles "
                    "origines frontales sont autorisées à lire la réponse HTTP via l'API Fetch ou XMLHttpRequest. » — Fetch Living Standard "
                    "(WHATWG), Section 3.2\n\n"
                    "Dès qu'une requête inter-origines emploie une méthode mutative (`PUT`, `PATCH`, `DELETE`), un type MIME structuré "
                    "`Content-Type: application/json` ou un en-tête `Authorization`, le navigateur émet préalablement une requête silencieuse "
                    "**Preflight `OPTIONS`** munie des en-têtes `Origin`, `Access-Control-Request-Method` et `Access-Control-Request-Headers`. "
                    "Le serveur Flask (ou l'extension `Flask-CORS`) doit valider l'origine contre une liste blanche explicite, répondre `204 No "
                    "Content` avec `Access-Control-Allow-Origin: https://portail.isgp.dz` ainsi que **`Vary: Origin`** (indispensable pour "
                    "éviter qu'un CDN intermédiaire ne serve en cache l'autorisation d'une origine A à une origine B)."
                )
            },
            {
                "heading": "2. Authentification de Webhooks entrants : `HMAC-SHA256` sur flux WSGI brut (`request.get_data()`) et anti-rejeu",
                "body": (
                    "#### Invariance binaire du corps HTTP face au parseur JSON\n\n"
                    "Un Webhook remplace avantageusement l'interrogation périodique (*Polling*) par une notification HTTP `POST` poussée par le "
                    "prestataire externe dès la réalisation d'un événement métier. Comme la route réceptrice `/api/v1/webhooks/paiement` est "
                    "exposée sur Internet public, l'émetteur prouve son identité en signant la charge utile brute à l'aide d'un secret partagé "
                    "`WEBHOOK_SECRET` et d'un horodatage anti-rejeu.\n\n"
                    "```python\n"
                    "import hashlib, hmac, time\n"
                    "from flask import request, current_app, abort\n\n"
                    "def verifier_signature_webhook() -> None:\n"
                    "    ts_str = request.headers.get(\"X-Webhook-Timestamp\", \"0\")\n"
                    "    sig_recue = request.headers.get(\"X-Webhook-Signature\", \"\")\n"
                    "    if abs(time.time() - int(ts_str)) > 300:\n"
                    "        abort(401, description=\"Fenetre temporelle Webhook depassee (anti-replay).\")\n"
                    "    corps_brut: bytes = request.get_data(cache=True)\n"
                    "    message = ts_str.encode(\"ascii\") + b\".\" + corps_brut\n"
                    "    attendu = \"sha256=\" + hmac.new(\n"
                    "        current_app.config[\"WEBHOOK_SECRET\"].encode(\"utf-8\"), message, hashlib.sha256\n"
                    "    ).hexdigest()\n"
                    "    if not hmac.compare_digest(sig_recue, attendu):\n"
                    "        abort(401, description=\"Signature HMAC du Webhook invalide.\")\n"
                    "```\n\n"
                    "> [!IMPORTANT] Calculer le HMAC exclusivement sur `request.get_data(cache=True)`\n"
                    "> Ne recalculez jamais une signature de Webhook sur `json.dumps(request.get_json()).encode()` ! La désérialisation puis "
                    "resérialisation JSON en Python altère les espaces séparateurs, l'échappement Unicode (`\\u00e9` vs UTF-8 direct) ou la "
                    "précision flottante, modifiant complètement le condensat `SHA-256`. `request.get_data(cache=True)` lit les octets exacts "
                    "du flux WSGI `environ['wsgi.input']` tout en conservant le tampon en cache pour un `request.get_json()` ultérieur."
                )
            },
            {
                "heading": "3. Protection mémoire contre l'épuisement RAM (`OOM Killer`) via `MAX_CONTENT_LENGTH` (`413`)",
                "body": (
                    "#### Coupe-circuit au niveau du parseur de flux Werkzeug\n\n"
                    "Lorsqu'une vue Flask invoque `request.get_json()` ou `request.form`, Werkzeug lit l'intégralité du flux réseau entrant "
                    "dans le tas (*heap*) du processus Python avant d'instancier l'arbre d'objets dictionnaires/listes (dont l'empreinte en "
                    "mémoire CPython représente couramment 3 à 5 fois la taille du texte JSON brut). Sans borne explicite, quatre requêtes "
                    "simultanées envoyant chacune 500 Mo suffisent à saturer la RAM d'une instance cloud et à déclencher l'*Out-Of-Memory "
                    "Killer* du noyau Linux sur les workers Gunicorn.\n\n"
                    "En déclarant `app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024` (1 Mio pour une API transactionnelle JSON) doublé de "
                    "`client_max_body_size 1m;` dans la configuration frontale Nginx, Werkzeug inspecte immédiatement `Content-Length` (et "
                    "compte les octets lus en transfert `Transfer-Encoding: chunked`) pour lever l'exception `RequestEntityTooLarge`, "
                    "convertie nativement en réponse HTTP **`413 Content Too Large` (RFC 9110, Section 15.5.14)** avant toute saturation."
                )
            }
        ],
        "architecture_diagram": (
            "DOUBLE MÉCANISME : PREFLIGHT CORS (NAVIGATEUR) & SIGNATURE HMAC (WEBHOOK)\n"
            "=========================================================================\n\n"
            "  [A] PRÉ-VÉRIFICATION CORS PAR LE NAVIGATEUR WEB :\n"
            "  Navigateur (https://portail.isgp.dz)             Serveur API (https://api.isgp.dz)\n"
            "  1. OPTIONS /api/formations               ----->  Vérifie si Origin est dans ORIGINES_AUTORISEES\n"
            "     Origin: https://portail.isgp.dz       <-----  204 No Content + Access-Control-Allow-Origin\n"
            "  2. POST /api/formations (+ JSON + Auth)  ----->  Exécute la route métier -> 201 Created\n\n"
            "  [B] VÉRIFICATION CRYPTOGRAPHIQUE D'UN WEBHOOK DE PAIEMENT :\n"
            "  Serveur de Paiement                              Serveur API Flask\n"
            "  Corps brut : b'{\"id\":101,\"statut\":\"paye\"}'       corps_brut = request.get_data()\n"
            "  Header X-Webhook-Signature: sha256=9f8a.. -----> Attendu = HMAC(WEBHOOK_SECRET, corps_brut)\n"
            "                                                   hmac.compare_digest(Recu, Attendu) -> 200 OK"
        ),
        "reference_table": {
            "title": "Mécanismes de Sécurité Périmétrique (`CORS`, `Webhooks`, `MAX_CONTENT_LENGTH`)",
            "headers": ["Mécanisme Périmétrique", "En-têtes HTTP Impliqués", "Code HTTP d'Erreur", "Menace Neutralisée"],
            "rows": [
                ["Politique `CORS` stricte", "`Origin`, `Access-Control-Allow-Origin`, `Access-Control-Allow-Headers`", "Blocage côté navigateur", "Appel malveillant de l'API depuis un site tiers non autorisé"],
                ["Signature de Webhook `HMAC`", "`X-Webhook-Signature` (ex: `sha256=...`)", "`401 Unauthorized`", "Falsification d'événements asynchrones (faux paiements, faux statuts)"],
                ["Plafond `MAX_CONTENT_LENGTH`", "`Content-Length`", "`413 Payload Too Large`", "Saturation de la mémoire vive (RAM) par envoi de charges géantes"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Configurer `Access-Control-Allow-Origin: *` (joker universel) sur une API privée",
                "good": "Maintenir une **liste blanche explicite** des domaines frontaux autorisés (`https://portail.isgp.dz`)",
                "why": "Le joker `*` autorise n'importe quel site Internet visité par l'utilisateur à interroger l'API depuis son navigateur."
            },
            {
                "bad": "Calculer le HMAC d'un Webhook après avoir parsé le JSON (`json.dumps(request.get_json())`)",
                "good": "Calculer systématiquement le HMAC sur la séquence d'octets brute exacte retournée par `request.get_data()`",
                "why": "Un seul espace ou retour à la ligne différent entre le formateur JSON de l'émetteur et celui de Python modifie totalement le hash SHA-256."
            }
        ],
        "practical_exercises": [
            "Écrivez un script Python ou une commande `curl` qui calcule la signature HMAC-SHA256 d'un corps JSON `{\"transaction_id\": \"TX-900\", \"montant\": 45000}` avec le secret `whsec_isgp_secret_2026` et appelle `/api/webhooks/paiement`.",
            "Ajoutez la protection contre les **attaques par rejeu (*Replay Attacks*)** sur le Webhook : exigez un en-tête `X-Webhook-Timestamp`, incluez-le dans le calcul HMAC (`timestamp + \".\" + body`), et rejetez tout Webhook dont l'horodatage a plus de 5 minutes d'écart avec l'heure actuelle."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.7 : GESTION ET SÉCURITÉ DES COOKIES EN API/WEB (HTTPONLY, SECURE, SAMESITE, SESSION HMAC)
    # =========================================================================
    "d4-l7": {
        "context": (
            "Lors de la conception d'une application Web adossée à une API Flask (*Backend-for-Frontend* ou portail hybride), le choix "
            "du support de persistance côté navigateur pour le jeton d'authentification constitue un point de rupture majeur lors des "
            "audits d'intrusion. La pratique consistant à persister un jeton Bearer dans `window.localStorage` ou `sessionStorage` "
            "expose l'intégralité du parc d'utilisateurs à une compromission totale à la moindre vulnérabilité **XSS (*Cross-Site "
            "Scripting*)** — qu'elle provienne d'une injection DOM ou de la compromission d'une dépendance JavaScript tierce (`npm`), "
            "car l'espace `localStorage` est intégralement lisible par tout code exécuté dans l'origine.\n\n"
            "L'ingénierie de sécurité conforme aux recommandations OWASP privilégie l'isolation du secret d'authentification hors de "
            "portée du moteur JavaScript grâce aux **Cookies HTTP blindés (`RFC 6265`)**, gouvernés par le triptyque d'attributs "
            "**`HttpOnly`**, **`Secure`** et **`SameSite`**, ainsi qu'au mécanisme interne de session signée de Flask "
            "(`SecureCookieSessionInterface` reposant sur `itsdangerous`)."
        ),
        "deep_sections": [
            {
                "heading": "1. Protocole d'état HTTP `RFC 6265` : Cycle `Set-Cookie`, `request.cookies` et préfixe `__Host-`",
                "body": (
                    "#### Gestion native par la pile réseau du navigateur\n\n"
                    "Contrairement à l'en-tête `Authorization` qui exige une instrumentation explicite de chaque appel `fetch()`, le mécanisme "
                    "des cookies opère directement dans la couche transport HTTP de l'agent utilisateur. Lorsqu'une vue Flask invoque "
                    "`response.set_cookie(...)`, Werkzeug sérialise un en-tête `Set-Cookie` ordonnant au navigateur d'enregistrer le couple "
                    "clé-valeur dans son magasin interne isolé. Sur chaque requête ultérieure dont le domaine et le chemin correspondent, le "
                    "navigateur injecte automatiquement l'en-tête `Cookie`, désérialisé paresseusement par Werkzeug dans le dictionnaire "
                    "immuable `request.cookies`.\n\n"
                    "```http\n"
                    "HTTP/1.1 200 OK\n"
                    "Set-Cookie: __Host-isgp_auth=eyJzdWIiOiJ5YXNtaW5lIn0.Z5yA1w.9pQ2...; Path=/; Max-Age=3600; HttpOnly; Secure; SameSite=Strict\n"
                    "Content-Type: application/json\n"
                    "```\n\n"
                    "Pour ordonner la destruction immédiate d'un cookie lors d'une déconnexion (`POST /api/v1/auth/logout`), "
                    "`response.delete_cookie('__Host-isgp_auth', path='/')` réémet un en-tête `Set-Cookie` porteur des mêmes attributs `Path` "
                    "et `Domain` accompagnés de `Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT`. Le préfixe normatif **`__Host-`** "
                    "(RFC 6265bis) renforce encore cette garantie : le navigateur rejette le cookie s'il ne possède pas simultanément `Secure`, "
                    "`Path=/` et l'absence totale d'attribut `Domain`, empêchant ainsi un sous-domaine compromis d'écraser le cookie de "
                    "session principal (*Cookie Tossing Attack*)."
                )
            },
            {
                "heading": "2. Triptyque défensif obligatoire : `HttpOnly` (Anti-XSS), `Secure` (TLS) et `SameSite` (Anti-CSRF)",
                "body": (
                    "#### Neutralisation conjointe de l'exfiltration DOM et de la falsification inter-sites\n\n"
                    "Aucun cookie porteur d'identité ne peut être émis en production sans ses trois attributs de confinement. Le drapeau "
                    "**`HttpOnly`** soustrait intégralement le cookie à l'API DOM `document.cookie` : même en présence d'une exécution de "
                    "script arbitraire (XSS), l'attaquant ne peut pas lire ni exfiltrer la chaîne brute du jeton hors du navigateur. Le "
                    "drapeau **`Secure`** interdit quant à lui toute transmission du cookie sur un socket TCP en clair (`http://`), prévenant "
                    "l'interception passive ou la rétrogradation protocolaire sur un réseau sans fil non fiable.\n\n"
                    "> « L'attribut SameSite permet aux serveurs de déclarer qu'un cookie ne doit pas être envoyé lors de requêtes "
                    "inter-sites, offrant une défense robuste en profondeur contre les attaques Cross-Site Request Forgery (CSRF). » — "
                    "IETF Draft RFC 6265bis, Section 5.4.7\n\n"
                    "Parce que le navigateur attache automatiquement les cookies, un site malveillant `evil.example` visité par un utilisateur "
                    "authentifié pouvait historiquement déclencher à son insu une requête mutative `POST https://api.isgp.dz/virement` "
                    "(**CSRF**). L'attribut **`SameSite=Strict`** bloque l'envoi du cookie sur toute requête initiée depuis un site tiers, "
                    "tandis que **`SameSite=Lax`** l'autorise uniquement lors d'une navigation descendante de premier niveau avec méthode "
                    "sûre (`GET`), bloquant tous les `POST`/`FETCH` inter-sites."
                )
            },
            {
                "heading": "3. Architecture interne de `flask.session` : `SecureCookieSessionInterface` et compression `itsdangerous`",
                "body": (
                    "#### Différence fondamentale entre `response.set_cookie` brut et `flask.session` signé\n\n"
                    "Un cookie ordinaire posé via `response.set_cookie('theme', 'sombre')` circule en texte clair non authentifié : l'utilisateur "
                    "peut en réécrire librement la valeur depuis l'inspecteur du navigateur, ce qui le restreint aux seules préférences "
                    "cosmétiques. À l'inverse, l'objet contextuel `flask.session` (un proxy `ContextVar` vers un `CallbackDict` qui ne "
                    "régénère l'en-tête `Set-Cookie` que lorsque `session.modified` passe à `True`) s'appuie par défaut sur "
                    "`SecureCookieSessionInterface`.\n\n"
                    "```python\n"
                    "app.config.update(\n"
                    "    SESSION_COOKIE_NAME=\"__Host-isgp_session\",\n"
                    "    SESSION_COOKIE_HTTPONLY=True,\n"
                    "    SESSION_COOKIE_SECURE=True,\n"
                    "    SESSION_COOKIE_SAMESITE=\"Lax\",\n"
                    "    PERMANENT_SESSION_LIFETIME=3600,\n"
                    ")\n"
                    "```\n\n"
                    "> [!IMPORTANT] Confidentialité et limite des 4096 octets de `flask.session`\n"
                    "> Lors de la sérialisation d'une réponse, Flask convertit `session` en JSON compact, compresse le tampon via `zlib` s'il "
                    "excède le seuil d'efficacité (reconnaissable au point initial `.eJw...` de la chaîne), l'encode en `Base64URL` et y appose "
                    "un `HMAC-SHA1`/`SHA256` dérivé de `app.secret_key` via `URLSafeTimedSerializer(salt='cookie-session')`. Comme pour un JWT, "
                    "la session cliente Flask est **infalsifiable mais lisible par le client** et plafonnée à **4 Kio** par la RFC 6265 : ne "
                    "stockez jamais de secrets serveur dans `session` !"
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE DE SÉCURITÉ DES COOKIES : HTTPONLY (ANTI-XSS) + SAMESITE (ANTI-CSRF)\n"
            "=================================================================================\n\n"
            "  Serveur Flask (POST /api/auth/cookie-login)\n"
            "       |\n"
            "       |  Set-Cookie: isgp_auth_token=eyJ...Sig; Max-Age=3600; HttpOnly; Secure; SameSite=Strict\n"
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
            "  Serveur Flask vérifie la signature HMAC (app.secret_key) ---> 200 OK"
        ),
        "reference_table": {
            "title": "Matrice de Sécurité des Attributs d'un Cookie HTTP (`Set-Cookie`)",
            "headers": ["Attribut `Set-Cookie`", "Paramètre Flask (`set_cookie`)", "Attaque Neutralisée", "Comportement du Navigateur"],
            "rows": [
                ["`HttpOnly`", "`httponly=True`", "**XSS** (*Cross-Site Scripting* — vol de jeton via JS)", "Rend le cookie totalement invisible pour `document.cookie` en JavaScript"],
                ["`Secure`", "`secure=True`", "**Sniffing réseau / MitM** sur Wi-Fi public", "Ne transmet le cookie que sur un canal chiffré `https://`"],
                ["`SameSite=Strict` / `Lax`", "`samesite=\"Strict\"` ou `\"Lax\"`", "**CSRF** (*Cross-Site Request Forgery*)", "Interdit l'envoi automatique du cookie lors de requêtes `POST` déclenchées depuis un site tiers"],
                ["`Max-Age` / `Expires`", "`max_age=3600` (ou `delete_cookie`)", "Persistance infinie sur un poste partagé", "Détruit automatiquement le cookie après `N` secondes (`Max-Age=0` pour révocation immédiate)"],
                ["Signature HMAC (`session`)", "`app.secret_key = os.environ[...]`", "**Falsification client** (élévation de privilèges dans F12)", "Toute modification d'un octet du cookie invalide la signature HMAC côté serveur"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Stocker le rôle en clair dans un cookie non signé (`reponse.set_cookie('role', 'admin')`) et lui faire confiance",
                "good": "Toujours signer cryptographiquement les cookies d'identité via `flask.session` ou `URLSafeTimedSerializer` avec `app.secret_key`",
                "why": "Un cookie non signé est un simple texte que l'utilisateur peut modifier en 5 secondes dans les outils de développement (F12) de son navigateur."
            },
            {
                "bad": "Oublier `httponly=True` sur un cookie contenant un jeton JWT ou un identifiant de session",
                "good": "Activer systématiquement `httponly=True` et `SESSION_COOKIE_HTTPONLY = True`",
                "why": "Sans `HttpOnly`, n'importe quel script JavaScript tiers chargé dans la page peut lire `document.cookie` et dérober la session."
            }
        ],
        "practical_exercises": [
            "Dans le Client HTTP ou avec `curl -i -X POST http://127.0.0.1:5000/api/sandbox/cookies/login`, inspectez les en-têtes `Set-Cookie` retournés par le serveur et vérifiez la présence de `HttpOnly` et `SameSite`.",
            "Appelez ensuite `GET /api/sandbox/cookies/inspect` puis `POST /api/sandbox/cookies/logout` pour observer le cycle complet d'émission, de vérification HMAC et de révocation (`Max-Age=0`)."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.1 : CONSOMMER UNE API TIERCE (CLIENT HTTP RÉSILIENT, TIMEOUTS & RETRIES)
    # =========================================================================
    "d5-l1": {
        "context": (
            "Au sein d'un système d'information distribué ou d'une topologie orientée microservices, une application Flask agit rarement "
            "en vase clos : le traitement synchrone d'une requête entrante requiert fréquemment d'interroger en aval des services HTTP "
            "tiers — cotation interbancaire, vérification d'identité régalienne, passerelle de paiement ou moteur d'expédition. Or, le "
            "premier axiome des systèmes distribués (formalisé par Peter Deutsch et analysé en détail par Martin Kleppmann) rappelle "
            "que le réseau de transport IP n'offre aucune garantie de latence bornée.\n\n"
            "Dans le modèle d'exécution synchrone de WSGI (`PEP 3333`), chaque requête active immobilise un worker `sync` ou un thread "
            "d'exécution `gthread` de Gunicorn jusqu'à sa complétion. Si un appel HTTP sortant est invoqué sans échéance stricte "
            "(`timeout`), un simple engorgement chez un prestataire secondaire fige en quelques secondes l'intégralité du pool de "
            "workers de votre propre serveur, provoquant une **panne en cascade (*Cascading Failure*)** sur toutes vos routes, y "
            "compris celles qui ne dépendent nullement du partenaire défaillant."
        ),
        "deep_sections": [
            {
                "heading": "1. Famine des workers Gunicorn (*Thread/Worker Starvation*) et tuple `(connect_timeout, read_timeout)`",
                "body": (
                    "#### Mécanique d'effondrement d'un serveur WSGI synchrone sans `timeout`\n\n"
                    "Supposons un déploiement Gunicorn configuré avec `--workers 4 --threads 2`, offrant une capacité maximale de 8 requêtes "
                    "simultanées. Lorsqu'un partenaire distant subit une saturation de son pool SQL, son répartiteur frontal continue "
                    "souvent d'acquitter la poignée de main TCP (`SYN` / `SYN-ACK` / `ACK`), mais son application ne renvoie plus aucun octet "
                    "HTTP. Un appel Python `urllib.request.urlopen(url)` ou `requests.get(url)` dépourvu d'argument `timeout` suspend alors le "
                    "thread sur l'appel système `recv()` jusqu'à l'expiration du noyau Linux (`net.ipv4.tcp_retries2`, soit plus de 120 "
                    "secondes). Huit requêtes entrantes sur cette route suffisent à saturer 100 % de la capacité Gunicorn : au bout de 30 "
                    "secondes, le processus maître Gunicorn tue les workers muets (`CRITICAL WORKER TIMEOUT`), aggravant l'instabilité.\n\n"
                    "> [!WARNING] Différencier systématiquement délai d'établissement TCP et délai de lecture\n"
                    "> Dans `requests` et `urllib3`, passez toujours un tuple `timeout=(connect_timeout, read_timeout)` tel que `timeout=(1.5, "
                    "3.0)` plutôt qu'un flottant unique. Un `connect_timeout` court (`1.5s`) détecte quasi instantanément un hôte injoignable "
                    "ou un pare-feu muet, tandis que `read_timeout` (`3.0s`) borne l'attente du premier octet de réponse applicative."
                )
            },
            {
                "heading": "2. Réessai borné avec *Exponential Backoff + Full Jitter*, Idempotence et codes `502` vs `504`",
                "body": (
                    "#### Discrimination des erreurs transitoires et prévention des tempêtes de réessais (*Retry Storms*)\n\n"
                    "Un client HTTP résilient distingue rigoureusement les rejets déterministes (`400`, `401`, `403`, `404`, `422`), qu'il est "
                    "absurde de rejouer, des défaillances transitoires d'infrastructure (`TimeoutError`, `502`, `503`, `504`). Même sur ces "
                    "dernières, seuls les appels intrinsèquement **idempotents** (`GET`, `HEAD`, `PUT`, `DELETE`, ou un `POST` protégé par un "
                    "en-tête `Idempotency-Key`) peuvent être réessayés automatiquement sans risquer une double facturation.\n\n"
                    "Afin d'éviter que des centaines de workers ne frappent simultanément un partenaire convalescent (*Thundering Herd*), "
                    "l'intervalle d'attente suit une progression exponentielle bruitée (*Full Jitter*) : `d_k = random(0, min(D_max, "
                    "b * 2**k))`. Si toutes les tentatives échouent, votre passerelle Flask ne doit jamais émettre `500 Internal Server "
                    "Error` — qui imputerait l'incident à un bogue interne Python dans vos métriques Prometheus — mais traduire la cause amont "
                    "selon la RFC 9110.\n\n"
                    "> « Le code 502 (Bad Gateway) indique que le serveur agissant comme passerelle a reçu une réponse invalide du serveur "
                    "amont, tandis que 504 (Gateway Timeout) indique qu'il n'a pas reçu de réponse à temps. » — IETF RFC 9110, Sections 15.6.3 "
                    "& 15.6.5"
                )
            },
            {
                "heading": "3. Réutilisation des sockets TCP/TLS (*Keep-Alive*) via `requests.Session` et `urllib3.HTTPAdapter`",
                "body": (
                    "#### Coût caché des poignées de main TLS répétées à chaque appel\n\n"
                    "Appeler la fonction de haut niveau `requests.get(url)` à l'intérieur d'une vue Flask ouvre à chaque requête un nouveau "
                    "socket éphémère, exécute la négociation TCP en trois temps (1 RTT), négocie la session cryptographique TLS 1.3 (1 RTT "
                    "supplémentaire et vérifications de chaîne X.509 coûteuses en CPU), puis referme immédiatement la connexion — risquant en "
                    "prime d'épuiser les ports locaux en état `TIME_WAIT` sous forte charge.\n\n"
                    "En instanciant un objet persistant `requests.Session()` monté avec un `HTTPAdapter` de `urllib3`, chaque worker Gunicorn "
                    "maintient un **pool de connexions HTTP/1.1 Keep-Alive** pré-établies vers le partenaire (`pool_connections`, "
                    "`pool_maxsize`), réduisant la latence médiane d'appel de 60 à 75 %.\n\n"
                    "```python\n"
                    "import requests\n"
                    "from requests.adapters import HTTPAdapter\n"
                    "from urllib3.util.retry import Retry\n\n"
                    "def creer_session_partenaire() -> requests.Session:\n"
                    "    session = requests.Session()\n"
                    "    strategie_retry = Retry(\n"
                    "        total=2,\n"
                    "        backoff_factor=0.25,\n"
                    "        status_forcelist=(502, 503, 504),\n"
                    "        allowed_methods=frozenset({\"GET\", \"HEAD\", \"PUT\", \"DELETE\"}),\n"
                    "    )\n"
                    "    adaptateur = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=strategie_retry)\n"
                    "    session.mount(\"https://\", adaptateur)\n"
                    "    return session\n"
                    "```\n\n"
                    "> [!TIP] Sécurité thread de `requests.Session` sous Gunicorn `gthread`\n"
                    "> Le gestionnaire de pool `urllib3.PoolManager` sous-jacent à `requests.Session` est protégé par verrous et sûr en lecture "
                    "concurrente multi-threads dès lors que les en-têtes ou cookies par défaut de l'instance `Session` ne sont plus mutés après "
                    "l'initialisation dans `create_app()`."
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE D'UN APPEL SORTANT RÉSILIENT (TIMEOUT + RETRY BACKOFF)\n"
            "===================================================================\n\n"
            "  Client Mobile          Votre API Flask (Passerelle)            API Partenaire Externe\n"
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
            "headers": ["Situation Rencontrée en Aval (Partenaire)", "Exception Python (`urllib`)", "Faut-il Réessayer (`Retry`) ?", "Code HTTP Renvoyé par Votre API"],
            "rows": [
                ["Partenaire répond `200 OK` avec JSON valide", "Aucune", "Non (Succès immédiat)", "`200 OK`"],
                ["Partenaire ne répond pas dans le délai `timeout`", "`TimeoutError` / `socket.timeout`", "Oui (2 à 3 fois max avec Backoff)", "`504 Gateway Timeout` (ou `200` dégradé avec cache)"],
                ["Partenaire répond `500`, `502` ou `503`", "`HTTPError` (`e.code >= 500`)", "Oui (Erreur transitoire serveur)", "`502 Bad Gateway`"],
                ["Partenaire répond `400`, `401`, `403` ou `404`", "`HTTPError` (`400 <= e.code < 500`)", "Non (Échec déterministe immédiat)", "`502 Bad Gateway` (ou code métier approprié)"],
                ["Partenaire renvoie du HTML au lieu de JSON", "`json.JSONDecodeError`", "Non", "`502 Bad Gateway`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Appeler `urlopen(url)` ou `requests.get(url)` sans l'argument `timeout=...` à l'intérieur d'une route Flask",
                "good": "Toujours imposer un `timeout` court (ex: `timeout=2.5`) sur tout appel réseau sortant",
                "why": "Sans `timeout`, la lenteur d'un partenaire externe bloque tous les workers de votre serveur Flask et provoque une panne en cascade (*Cascading Failure*)."
            },
            {
                "bad": "Faire un `Retry` automatique sur une opération de paiement (`POST`) sans clé d'idempotence",
                "good": "Ne réessayer automatiquement que les requêtes idempotentes (`GET`, `PUT`, `DELETE`) ou munies d'une `Idempotency-Key`",
                "why": "Si la 1re requête avait abouti mais que seule la réponse s'est perdue sur le réseau, réessayer un `POST` non idempotent exécute l'opération deux fois."
            }
        ],
        "practical_exercises": [
            "Ajoutez un **cache de secours en mémoire (`FALLBACK_CACHE`)** à la fonction `appeler_api_externe()` : chaque fois qu'un appel réussit, sauvegardez la réponse en mémoire ; si le partenaire tombe en panne plus tard, renvoyez la dernière valeur connue avec un champ `\"mode_degrade\": True` au lieu d'une erreur `502`.",
            "Implémentez un disjoncteur simple (**Circuit Breaker**) : si 5 appels consécutifs vers le partenaire échouent, ouvrez le circuit pendant 30 secondes pour échouer instantanément sans même attendre les 2 secondes de `timeout`."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.2 : ARCHITECTURE MODULAIRE, BLUEPRINTS & CYCLE DE VIE API (/api/v1 vs /api/v2)
    # =========================================================================
    "d5-l2": {
        "context": (
            "À mesure qu'un système backend s'étend au-delà de quelques dizaines d'endpoints, deux problèmes d'architecture "
            "structurels menacent sa maintenabilité à long terme. Sur le plan interne, concentrer les routes, les middlewares et "
            "l'instance globale `app = Flask(__name__)` dans un module monolithique provoque inévitablement des cycles d'importation "
            "Python (`ImportError: cannot import name 'app' from partially initialized module`) et interdit d'instancier plusieurs "
            "configurations isolées lors des campagnes de tests.\n\n"
            "Sur le plan externe du contrat distribué, faire évoluer le schéma JSON d'une API déjà consommée par des dizaines de "
            "milliers de terminaux mobiles iOS/Android ou de partenaires B2B impose une discipline stricte de gestion du cycle de vie. "
            "Ce chapitre démontre comment conjuguer le découpage modulaire par **`Blueprints`** et l'**Application Factory "
            "(`create_app`)** de Flask avec la théorie de compatibilité ascendante (*Tolerant Reader*), le versionnement d'URI "
            "(`/api/v1` contre `/api/v2`) et la signalisation normative de fin de vie selon la **RFC 8594 (`Sunset`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Longévité de `/api/v1` : Principe de robustesse de Postel, *Tolerant Reader* et ruptures de contrat",
                "body": (
                    "#### Évolutions additives (*Non-Breaking*) contre mutations incompatibles (*Breaking Changes*)\n\n"
                    "L'observation des grandes plateformes industrielles (OpenAI `/v1/`, Kubernetes `/api/v1`, Stripe `/v1/`) révèle qu'une "
                    "version majeure `/v1` demeure stable durant cinq à dix ans. Cette longévité s'explique par le patron *Tolerant Reader* "
                    "dérivé du principe de robustesse de Jon Postel (RFC 761) : un désérialiseur client correctement conçu extrait uniquement "
                    "les clés JSON dont il a besoin et ignore silencieusement toute clé supplémentaire apparue ultérieurement. Dès lors, "
                    "enrichir une réponse d'un nouvel attribut (`\"certifiant\": true`), publier un nouvel endpoint ou introduire un paramètre "
                    "de requête optionnel muni d'une valeur serveur par défaut constituent des **évolutions additives rétrocompatibles** qui "
                    "s'intègrent directement dans `/api/v1`.\n\n"
                    "À l'inverse, quatre opérations brisent immédiatement les clients compilés existants et imposent l'ouverture d'un espace "
                    "de noms `/api/v2` : supprimer ou renommer une propriété JSON existante (`intitule` vers `titre`), muter le type scalaire "
                    "d'un champ (`\"duree\": 5` devenant un sous-objet `{\"valeur\": 5, \"unite\": \"jours\"}`), rendre obligatoire un champ "
                    "d'entrée `POST`/`PUT` auparavant facultatif, ou substituer un objet enveloppe `{\"meta\": ..., \"data\": [...]}` à un "
                    "tableau JSON racine `[...]`. Préfixer toute route par `/api/v1` dès le premier jour agit comme une assurance "
                    "architecturale : le jour où une refonte structurelle survient, `/api/v2` est monté en parallèle sur le même serveur WSGI "
                    "sans casser les clients historiques."
                )
            },
            {
                "heading": "2. Coexistence multi-versions par `Blueprint` et protocole d'extinction `RFC 8594` (`Deprecation` & `Sunset`)",
                "body": (
                    "#### Signalisation HTTP automatisée avant retrait définitif (`410 Gone`)\n\n"
                    "Dans Flask, faire cohabiter deux contrats publics sans dupliquer les requêtes SQL ni les règles métier consiste à "
                    "attacher deux `Blueprints` distincts (`formations_v1_bp` sous `/api/v1/formations` et `formations_v2_bp` sous "
                    "`/api/v2/formations`) au-dessus d'une couche de service Python unique : seule la fonction finale de projection "
                    "dictionnaire/JSON diffère entre les deux modules. Durant la fenêtre de migration contractuelle (typiquement 6 à 12 mois), "
                    "un crochet `@formations_v1_bp.after_request` injecte sur chaque réponse `v1` les en-têtes normalisés par l'IETF.\n\n"
                    "> « Le champ d'en-tête de réponse HTTP Sunset indique qu'une URI est susceptible de cesser de répondre à un instant précis "
                    "dans le futur, permettant aux clients automatisés d'anticiper leur migration. » — IETF RFC 8594, Section 3\n\n"
                    "```http\n"
                    "HTTP/1.1 200 OK\n"
                    "Content-Type: application/json\n"
                    "Deprecation: @1767225599\n"
                    "Sunset: Thu, 31 Dec 2026 23:59:59 GMT\n"
                    "Link: <https://api.isgp.dz/api/v2/formations>; rel=\"successor-version\"\n"
                    "```\n\n"
                    "Une fois l'échéance `Sunset` échue et le volume d'appels résiduels tombé à zéro dans la télémétrie d'accès, les routes "
                    "`/api/v1` ne sont pas détruites silencieusement (ce qui produirait un `404 Not Found` ambigu), mais remplacées par un "
                    "gestionnaire léger retournant **`410 Gone` (RFC 9110, Section 15.5.11)** accompagné de l'en-tête `Link` vers `v2`."
                )
            },
            {
                "heading": "3. Enregistrement différé des `Blueprints`, *Application Factory* (`create_app`) et sondes Kubernetes",
                "body": (
                    "#### Mécanique interne de `app.register_blueprint()` et `current_app`\n\n"
                    "Contrairement à une instance `Flask` complète, un objet `Blueprint('formations_v2', __name__)` est un enregistreur "
                    "paresseux d'opérations différées : chaque décorateur `@bp.get(...)` empile une fonction lambda dans `bp.deferred_functions` "
                    "sans requérir l'existence d'une application. Ce n'est qu'à l'exécution de `create_app(config_override)` que la fabrique "
                    "instancie `Flask(__name__)`, charge la configuration, lie les extensions et invoque `app.register_blueprint(...)` pour "
                    "compiler les règles `werkzeug.routing.Rule` dans `app.url_map`. À l'intérieur des modules métiers, toute référence à la "
                    "configuration transite par le proxy `ContextVar` `flask.current_app`, éliminant définitivement les importations circulaires.\n\n"
                    "```python\n"
                    "from flask import Blueprint, Flask, jsonify\n\n"
                    "sante_bp = Blueprint(\"sante\", __name__, url_prefix=\"/api/health\")\n\n"
                    "@sante_bp.get(\"/live\")\n"
                    "def liveness_probe():\n"
                    "    return jsonify(status=\"alive\"), 200\n\n"
                    "@sante_bp.get(\"/ready\")\n"
                    "def readiness_probe():\n"
                    "    db_ok = verifier_ping_sql_rapide()\n"
                    "    return (jsonify(status=\"ready\"), 200) if db_ok else (jsonify(status=\"degraded\"), 503)\n"
                    "```\n\n"
                    "> [!IMPORTANT] Dissocier impérativement *Liveness* (`/live`) et *Readiness* (`/ready`)\n"
                    "> Si votre sonde `livenessProbe` Kubernetes interroge PostgreSQL et que la base redémarre pendant 15 secondes, l'orchestrateur "
                    "croira vos conteneurs Gunicorn figés et tuera tous vos pods simultanément (*CrashLoopBackOff*). `/live` vérifie uniquement "
                    "que la boucle Python du worker répond (`200`), tandis que `/ready` vérifie les dépendances aval et renvoie `503` pour "
                    "retirer temporairement le pod du répartiteur de charge sans le redémarrer."
                )
            }
        ],
        "architecture_diagram": (
            "COEXISTENCE MULTI-VERSIONS (/api/v1 DÉPRÉCIÉE + /api/v2) VIA BLUEPRINTS FLASK\n"
            "=============================================================================\n\n"
            "  Clients Historiques (App Mobile v1)            Nouveaux Clients (Portail Web / App v2)\n"
            "  GET /api/v1/formations                         GET /api/v2/formations\n"
            "            |                                              |\n"
            "            v                                              v\n"
            "  +--------------------------------------------------------------------------+\n"
            "  | APPLICATION FACTORY : create_app()                                       |\n"
            "  |                                                                          |\n"
            "  |  [Blueprint formations_v1_bp]               [Blueprint formations_v2_bp] |\n"
            "  |  url_prefix='/api/v1/formations'            url_prefix='/api/v2/...'     |\n"
            "  |  + Headers RFC 8594 :                       + Enveloppe normalisée :     |\n"
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
            "Dans le Sandbox HTTP ou avec `curl -i http://127.0.0.1:5000/api/v1/sandbox/formations`, inspectez les en-têtes HTTP de dépréciation (`Deprecation`, `Sunset`, `Link`), puis appelez `/api/v2/sandbox/formations` pour comparer la transformation du champ `duree`.",
            "Ajoutez un décorateur ou middleware qui lit l'en-tête `Accept-Version: v2` ou `X-API-Version: 2.0` et aiguille automatiquement le format de sortie."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.3 : TESTS AUTOMATISÉS (TEST_CLIENT), OPENAPI 3.0 & DÉPLOIEMENT WSGI (GUNICORN)
    # =========================================================================
    "d5-l3": {
        "context": (
            "Livrer en continu les évolutions d'une API critique sans introduire de régression contractuelle ni de vulnérabilité "
            "d'exécution exige d'industrialiser la chaîne d'ingénierie autour de trois disciplines complémentaires. Premièrement, la "
            "validation manuelle sporadique via `curl` doit céder la place à une suite déterministe de **tests d'intégration en mémoire "
            "vive (`app.test_client()`)** exécutée automatiquement à chaque *commit* CI/CD.\n\n"
            "Deuxièmement, la diffusion formelle des schémas d'entrée/sortie vers les équipes consommatrices requiert un contrat "
            "calculable conforme à la spécification **OpenAPI**. Troisièmement, la mise en ligne sur infrastructure Linux impose de "
            "remplacer le serveur de développement Werkzeug (`app.run()`) par une topologie de production à trois étages — **mandataire "
            "inverse Nginx, orchestrateur WSGI pre-fork Gunicorn (`PEP 3333`) et travailleurs Flask** — capable d'absorber la "
            "concurrence matérielle, les clients lents et les pannes de processus."
        ),
        "deep_sections": [
            {
                "heading": "1. Harnais de test WSGI sans socket réseau : `app.test_client()` et `EnvironBuilder`",
                "body": (
                    "#### Exécution déterministe sub-milliseconde du pipeline Flask complet\n\n"
                    "Plutôt que d'ouvrir un port TCP éphémère sujet aux conflits d'ordonnancement en intégration continue, `app.test_client()` "
                    "instancie `FlaskClient` (sous-classe de `werkzeug.test.Client`). Chaque appel `client.post('/api/v1/formations', "
                    "json={...}, headers={...})` mobilise `werkzeug.test.EnvironBuilder` pour synthétiser en mémoire vive un dictionnaire WSGI "
                    "`environ` strictement conforme à la PEP 3333, invoque directement `app.wsgi_app(environ, start_response)`, traverse "
                    "l'intégralité des crochets `before_request`, des décorateurs d'autorisation, des requêtes SQL transactionnelles et des "
                    "gestionnaires d'erreurs, puis restitue un objet `TestResponse` inspectable en moins d'une milliseconde.\n\n"
                    "```python\n"
                    "def test_creation_formation_refusee_sans_role_admin(app):\n"
                    "    app.config.update(TESTING=True)\n"
                    "    with app.test_client() as client:\n"
                    "        resp = client.post(\n"
                    "            \"/api/v1/formations\",\n"
                    "            json={\"intitule\": \"Audit WSGI\", \"tarif_dzd\": -500},\n"
                    "            headers={\"Authorization\": f\"Bearer {jeton_lecteur}\"},\n"
                    "        )\n"
                    "        assert resp.status_code == 403\n"
                    "        assert resp.mimetype == \"application/problem+json\"\n"
                    "```\n\n"
                    "Une couverture industrielle rigoureuse vérifie systématiquement, pour chaque route, le chemin nominal (*Happy Path*) "
                    "ainsi que la matrice complète des chemins d'échec (*Unhappy Paths* : `400` JSON tronqué, `401` signature invalide, `403` "
                    "violation RBAC/BOLA, `404` entité absente et `422` invariant métier violé)."
                )
            },
            {
                "heading": "2. Protocole `WSGI` (`PEP 3333`) et modèle de concurrence *Pre-Fork* de Gunicorn (`sync` vs `gthread`)",
                "body": (
                    "#### Contrat d'interface synchrone entre serveur HTTP et cadre applicatif Python\n\n"
                    "La spécification **PEP 3333 (*Python Web Server Gateway Interface v1.0.1*)** découple les serveurs d'entrée/sortie réseau "
                    "des frameworks applicatifs Python autour d'une signature minimale `def application(environ: dict, start_response: "
                    "Callable) -> Iterable[bytes]`. Le serveur WSGI peuple `environ` avec les variables CGI/HTTP (`REQUEST_METHOD`, "
                    "`PATH_INFO`, `HTTP_AUTHORIZATION`, le flux binaire `wsgi.input`) et transmet le rappel `start_response` à l'objet "
                    "`Flask`.\n\n"
                    "> « L'interface WSGI exige que l'application soit un objet appelable acceptant deux arguments positionnels : un "
                    "dictionnaire d'environnement CGI et une fonction start_response initiant l'envoi du statut et des en-têtes HTTP. » — "
                    "Python Enhancement Proposal 3333\n\n"
                    "Pour contourner le verrou global de l'interpréteur CPython (**GIL**, *Global Interpreter Lock*), **Gunicorn** implémente "
                    "l'architecture Unix *Pre-Fork Worker Model*. Un processus **Master** unique lie le socket d'écoute (`127.0.0.1:8000` ou "
                    "socket de domaine Unix `unix:/run/isgp.sock`), puis invoque `os.fork()` pour engendrer `W = 2 * N_CPU + 1` "
                    "processus travailleurs autonomes supervisés par signaux POSIX. Sur des charges dominées par le calcul CPU, la classe par "
                    "défaut `--worker-class sync` isole chaque requête dans son propre processus ; sur des APIs fortement liées aux entrées/"
                    "sorties réseau ou SQL (où le GIL est relâché durant les appels système `recv`/`poll`), `--worker-class gthread --workers "
                    "4 --threads 4` multiplie la concurrence utile à empreinte RAM constante."
                )
            },
            {
                "heading": "3. Topologie de production à trois étages (`Nginx -> Gunicorn -> Flask`) et danger RCE de `debug=True`",
                "body": (
                    "#### Tamponnage anti-Slowloris sur Nginx et recyclage mémoire Gunicorn\n\n"
                    "Le serveur intégré `app.run()` de Werkzeug n'est qu'un harnais local de prototypage dépourvu de durcissement réseau. "
                    "Exposer directement des workers Gunicorn `sync` sur Internet public sans mandataire inverse les rendrait quant à eux "
                    "immédiatement vulnérables à une attaque **Slowloris** : un assaillant ouvrant 8 connexions TCP sur réseau mobile lent et "
                    "envoyant un octet d'en-tête toutes les dix secondes immobiliserait 100 % des workers pendant de longues minutes.\n\n"
                    "Placé en frontal sur `:443`, **Nginx** assure la terminaison cryptographique TLS 1.3, absorbe intégralement les requêtes "
                    "clientes lentes en mémoire tampon avant de les relayer en une milliseconde sur le socket Unix local de Gunicorn, et "
                    "compresse les réponses JSON (`gzip` / `zstd`).\n\n"
                    "```bash\n"
                    "gunicorn \"wsgi:create_app()\" \\\n"
                    "  --bind unix:/run/isgp-api/gunicorn.sock \\\n"
                    "  --worker-class gthread --workers 4 --threads 4 \\\n"
                    "  --timeout 30 --keep-alive 5 \\\n"
                    "  --max-requests 2000 --max-requests-jitter 200\n"
                    "```\n\n"
                    "> [!WARNING] Interdiction absolue du débogueur interactif Werkzeug en production (`RCE`)\n"
                    "> Activer `debug=True` enveloppe l'application dans `werkzeug.debug.DebuggedApplication`, qui expose une console "
                    "d'évaluation Python interactive sur chaque page d'exception `500`. Même protégée par un code PIN à 9 chiffres, toute fuite "
                    "locale de fichiers (`/proc/self/cgroup`, adresse MAC, `machine-id` par traversée de chemin) permet à un attaquant de "
                    "recalculer le PIN Werkzeug et d'obtenir une **exécution de code arbitraire à distance (`RCE`)** sur le serveur."
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE DE DÉPLOIEMENT DE PRODUCTION LINUX (NGINX + GUNICORN + FLASK)\n"
            "==========================================================================\n\n"
            "  Internet (HTTPS :443)\n"
            "        |\n"
            "        v\n"
            "  +-------------------------------------------------------------------+\n"
            "  | 1. NGINX (Reverse Proxy)                                          |\n"
            "  |    - Terminaison SSL/TLS (Certificats HTTPS)                      |\n"
            "  |    - Protection anti-DDoS / Limite de taille / Compression Gzip   |\n"
            "  +-------------------------------------------------------------------+\n"
            "        |  (Proxy Pass HTTP interne : 127.0.0.1:8000 ou Socket Unix)\n"
            "        v\n"
            "  +-------------------------------------------------------------------+\n"
            "  | 2. GUNICORN (Serveur WSGI — Processus Master)                     |\n"
            "  |    Commande : gunicorn --workers 4 --bind 127.0.0.1:8000 wsgi:app |\n"
            "  +-------------------------------------------------------------------+\n"
            "     |                  |                  |                  |\n"
            "     v                  v                  v                  v\n"
            "  [Worker 1]         [Worker 2]         [Worker 3]         [Worker 4]\n"
            "  Instance Flask     Instance Flask     Instance Flask     Instance Flask\n"
            "     \\                  |                  |                  /\n"
            "      +-----------------+------------------+-----------------+\n"
            "                                   |\n"
            "                                   v\n"
            "                    [ Base de Données SQL / Redis ]"
        ),
        "reference_table": {
            "title": "Comparatif : Serveur de Développement (`app.run`) vs Serveur WSGI Production (`Gunicorn + Nginx`)",
            "headers": ["Critère d'Exploitation", "Serveur de Dev (`python app.py`)", "Serveur WSGI Production (`Gunicorn + Nginx`)"],
            "rows": [
                ["Vocation", "Développement local et débogage sur le poste du développeur", "Production haute disponibilité exposée aux utilisateurs réels"],
                ["Parallélisme multi-cœurs", "Non (1 seul processus Python limité par le GIL)", "Oui (`N` processus Workers indépendants répartis sur tous les cœurs CPU)"],
                ["Résilience aux crashs", "Un crash bloque le serveur", "Le processus Master Gunicorn redémarre automatiquement tout worker défaillant"],
                ["Sécurité HTTPS & Slowloris", "Faible (Non conçu pour l'exposition directe sur Internet)", "Maximale (Déléguée à Nginx en frontal + `--timeout` sur Gunicorn)"],
                ["Mode Debug (`debug=True`)", "Activé en local (Rechargement auto)", "**Strictement interdit en prod** (Permettrait l'exécution de code arbitraire !)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Exposer directement `python app.py` avec `debug=True` sur un serveur de production",
                "good": "Toujours forcer `debug=False` et utiliser un serveur WSGI (`gunicorn --workers 4 --timeout 30 \"app:create_app()\"`) derrière Nginx",
                "why": "Le débogueur interactif Werkzeug de `debug=True` permet d'exécuter des commandes Python arbitraires depuis un navigateur en cas d'erreur 500."
            },
            {
                "bad": "N'écrire des tests automatisés que pour les cas de succès (`200 OK`)",
                "good": "Tester systématiquement les cas d'erreur (`400`, `401`, `403`, `404`, `422`) avec `app.test_client()`",
                "why": "Les régressions de sécurité et les crashs en production surviennent presque toujours sur les entrées invalides ou non autorisées."
            }
        ],
        "practical_exercises": [
            "Enrichissez la fonction `executer_suite_de_tests()` pour ajouter un 5e test automatisé qui vérifie qu'un appel `POST /api/v1/formations` avec un `tarif_dzd` négatif est bien rejeté avec un code `422`.",
            "Complétez le dictionnaire `generer_spec_openapi()` pour documenter le schéma du corps JSON requis par la méthode `POST /api/v1/formations` (`requestBody.content.application/json.schema`)."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.4 : DOCUMENTATION INTERACTIVE SWAGGER UI & CONTRAT OPENAPI 3.0
    # =========================================================================
    "d5-l4": {
        "context": (
            "Au sein d'une organisation où un noyau backend Python/Flask dessert simultanément des applications mobiles natives "
            "(Swift/Kotlin), des frontaux TypeScript et des intégrateurs externes, la synchronisation informelle des contrats d'interface "
            "par messagerie ou documentation statique dérive inévitablement par rapport au code réellement déployé (*Documentation "
            "Drift*). Dès qu'une propriété JSON change de cardinalité ou de contrainte de validation dans une vue Flask sans mise à "
            "jour immédiate du référentiel partagé, l'intégration inter-équipes se rompt en production.\n\n"
            "L'industrie logicielle résout cette divergence structurelle grâce à la **Spécification OpenAPI 3.0 / 3.1 (OAS)** gouvernée "
            "par la Linux Foundation, couplée aux moteurs de rendu interactifs tels que **Swagger UI** et aux frameworks déclaratifs de "
            "l'écosystème Flask (**APIFlask**, **Flask-Smorest**). Exposée sous forme de graphe JSON calculable sur `/api/openapi.json`, "
            "cette description formelle érige le contrat HTTP en artefact d'ingénierie vérifiable par machine."
        ),
        "deep_sections": [
            {
                "heading": "1. Gouvernance normative : De Swagger 2.0 à `OpenAPI 3.1` (`JSON Schema Draft 2020-12`)",
                "body": (
                    "#### Dissociation entre grammaire formelle OAS et outillage d'exploitation Swagger\n\n"
                    "Une confusion terminologique fréquente assimile la norme ouverte à l'éditeur commercial historique. Depuis le transfert du "
                    "standard à l'*OpenAPI Initiative* sous l'égide de la Linux Foundation fin 2015, **`OpenAPI Specification` (OAS 3.0.3 puis "
                    "OAS 3.1.0)** désigne exclusivement la grammaire normative du document de contrat (`openapi.json` ou `openapi.yaml`), "
                    "tandis que **`Swagger`** désigne une famille d'outils consommateurs de ce contrat (`Swagger UI` pour l'exploration "
                    "interactive dans le navigateur, `Swagger Editor` et `OpenAPI Generator` pour la synthèse automatique de SDK clients typés).\n\n"
                    "> « Un document OpenAPI permet de décrire l'intégralité d'une API HTTP de sorte que les humains comme les ordinateurs "
                    "puissent découvrir et comprendre les capacités du service sans accès au code source ni inspection du trafic réseau. » — "
                    "OpenAPI Specification v3.1.0, Section 1\n\n"
                    "L'évolution majeure d'**OpenAPI 3.1** réside dans son alignement mathématique intégral à 100 % sur **JSON Schema Draft "
                    "2020-12** : là où OpenAPI 3.0 imposait encore la propriété propriétaire `nullable: true`, OpenAPI 3.1 unifie le typage "
                    "optionnel via les tableaux de types standards `\"type\": [\"string\", \"null\"]`, éliminant toute friction avec les "
                    "validateurs JSON Schema modernes et `Pydantic v2`."
                )
            },
            {
                "heading": "2. Topologie d'un document OpenAPI : Modèles d'URI `RFC 6570`, pointeurs `$ref` et `securitySchemes`",
                "body": (
                    "#### Factorisation des schémas et différences syntaxiques avec `werkzeug.routing`\n\n"
                    "L'arbre d'un contrat OpenAPI s'articule autour de cinq clés racines déterministes (`openapi`, `info`, `servers`, `paths`, "
                    "`components`). Une subtilité récurrente en Flask concerne la notation des segments dynamiques d'URI : alors que le routeur "
                    "interne de Werkzeug emploie des convertisseurs typés entre chevrons (`/api/v1/formations/<int:id>`), la section `paths` "
                    "d'OpenAPI obéit strictement aux **URI Templates de la RFC 6570** entre accolades (`/api/v1/formations/{id}`), le typage "
                    "entier étant déporté dans `parameters[*].schema`.\n\n"
                    "```json\n"
                    "{\n"
                    "  \"openapi\": \"3.1.0\",\n"
                    "  \"paths\": {\n"
                    "    \"/api/v1/formations/{id}\": {\n"
                    "      \"get\": {\n"
                    "        \"security\": [{\"BearerAuth\": []}],\n"
                    "        \"parameters\": [{\"name\": \"id\", \"in\": \"path\", \"required\": true, \"schema\": {\"type\": \"integer\"}}],\n"
                    "        \"responses\": {\n"
                    "          \"200\": {\"content\": {\"application/json\": {\"schema\": {\"$ref\": \"#/components/schemas/Formation\"}}}}\n"
                    "        }\n"
                    "      }\n"
                    "    }\n"
                    "  }\n"
                    "}\n"
                    "```\n\n"
                    "Afin d'éviter toute duplication des structures d'entités ou de l'enveloppe d'erreur RFC 9457 (`ProblemDetails`), les "
                    "modèles canoniques sont déclarés une unique fois sous `components.schemas` et référencés à travers tout le document par "
                    "des **JSON Pointers (RFC 6901)** de la forme `{\"$ref\": \"#/components/schemas/Formation\"}`. De même, "
                    "`components.securitySchemes` déclare les protocoles d'authentification (`http` `bearer` ou `apiKey` dans `X-API-Key`), "
                    "activant automatiquement l'injection des en-têtes depuis la modale **Authorize** de Swagger UI."
                )
            },
            {
                "heading": "3. Stratégies d'intégration dans Flask : Exposition native, Introspection (`APIFlask`) et *Contract-First*",
                "body": (
                    "#### Génération par schémas de validation Python contre gouvernance *Design-First*\n\n"
                    "Contrairement à certains cadres couplés à un unique moteur de sérialisation, Flask laisse à l'architecte le choix entre "
                    "trois modalités d'industrialisation OpenAPI. Sur un microservice sobre sans dépendances lourdes, exposer directement le "
                    "dictionnaire sur `GET /api/openapi.json` et monter les actifs statiques de `SwaggerUIBundle` sur `/api/docs` offre une "
                    "maîtrise totale du contrat généré.\n\n"
                    "À l'échelle de plusieurs dizaines de routes, les surcouches spécialisées **APIFlask** et **Flask-Smorest** éliminent tout "
                    "risque de désynchronisation (*Code-First Introspection*) : les décorateurs `@app.input(FormationInSchema)` et "
                    "`@app.output(FormationOutSchema)` (adossés à `Marshmallow` ou `Pydantic`) valident automatiquement la charge utile entrante "
                    "(renvoyant `422` en cas d'écart) et compilent à la volée l'arbre `openapi.json` exact à partir des mêmes classes Python.\n\n"
                    "> [!TIP] Confinement périmétrique de `/api/docs` et `/api/openapi.json` en production\n"
                    "> Si une API est exclusivement interne (administration, finance B2B fermée), exposer publiquement `/api/openapi.json` "
                    "offre à un attaquant la cartographie exhaustive de vos routes, paramètres et modèles internes (*OWASP API9:2023 Improper "
                    "Inventory Management*). Restreignez l'accès aux routes documentaires par authentification ou filtrage réseau VPN sur les "
                    "environnements de production non publics."
                )
            }
        ],
        "architecture_diagram": (
            "ÉCOSYSTÈME OPENAPI 3.0 : UN SEUL CONTRAT POUR TOUS LES OUTILS\n"
            "=============================================================\n\n"
            "                    +-------------------------------------+\n"
            "                    |   Serveur Flask (/api/openapi.json) |\n"
            "                    |   Contrat OpenAPI 3.0.3 (JSON/YAML) |\n"
            "                    +------------------+------------------+\n"
            "                                       |\n"
            "         +-----------------------------+-----------------------------+\n"
            "         |                             |                             |\n"
            "         v                             v                             v\n"
            "  +--------------+             +---------------+             +---------------+\n"
            "  |  SWAGGER UI  |             |  POSTMAN /    |             | OPENAPI       |\n"
            "  |  (/api/docs) |             |  INSOMNIA     |             | GENERATOR     |\n"
            "  |  Portail Web |             |  Import 1-clic|             | Génère les SDK|\n"
            "  |  Interactif  |             |  Collection   |             | Mobile & Web  |\n"
            "  +--------------+             +---------------+             +---------------+"
        ),
        "reference_table": {
            "title": "Structure de Référence d'un Document OpenAPI 3.0 (`openapi.json`)",
            "headers": ["Clé Racine OpenAPI 3.0", "Rôle dans le Contrat", "Exemple de Contenu", "Impact Visuel dans Swagger UI (`/api/docs`)"],
            "rows": [
                ["`openapi` & `info`", "Version de la norme et identité de l'API", "`\"openapi\": \"3.0.3\", \"info\": {\"title\": \"...\", \"version\": \"1.0.0\"}`", "Affiche l'en-tête principal, le badge de version et la description"],
                ["`servers`", "Liste des URLs de base cibles", "`[{\"url\": \"http://127.0.0.1:5000\"}]`", "Alimente la liste déroulante *Servers* pour choisir où envoyer les requêtes"],
                ["`paths`", "Catalogue des routes et méthodes HTTP", "`\"/api/v1/formations/{id}\": {\"get\": {...}}`", "Crée les bandeaux colorés dépliables (`GET` bleu, `POST` vert, `PUT` orange, `DELETE` rouge)"],
                ["`components.schemas`", "Modèles de données JSON réutilisables (`$ref`)", "`\"Formation\": {\"type\": \"object\", \"properties\": {...}}`", "Alimente la section *Schemas* en bas de page et pré-remplit les exemples *Try it out*"],
                ["`components.securitySchemes`", "Définition des mécanismes d'authentification", "`\"BearerAuth\": {\"type\": \"http\", \"scheme\": \"bearer\"}`", "Affiche le bouton cadenas vert **« Authorize »** en haut à droite et sur chaque route protégée"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écrire `/api/v1/formations/<int:id>` (syntaxe Flask) à l'intérieur du fichier `openapi.json`",
                "good": "Toujours utiliser la syntaxe entre accolades `/api/v1/formations/{id}` dans la section `paths` d'OpenAPI 3.0",
                "why": "La norme OpenAPI (RFC 6570) ne reconnaît que `{id}` pour relier l'URL au paramètre `{\"name\": \"id\", \"in\": \"path\"}` dans Swagger UI."
            },
            {
                "bad": "Laisser la documentation Swagger accessible publiquement en production sur une API interne critique sans authentification si elle expose l'architecture interne",
                "good": "Protéger l'accès à `/api/docs` sur les APIs privées d'administration ou la réserver au réseau interne / portail développeur",
                "why": "Sur une API privée non destinée au public, exposer `/api/openapi.json` facilite la phase de reconnaissance d'un attaquant."
            }
        ],
        "practical_exercises": [
            "Ouvrez le portail Swagger UI intégré à ce laboratoire (`/api/docs`), cliquez sur le bouton cadenas **« Authorize »**, entrez la clé `isgp-secret-2026` dans `ApiKeyAuth`, puis testez la route `GET /api/sandbox/admin-stats` avec **« Try it out »**.",
            "Dans `day_5/05_swagger_openapi_ui.py`, ajoutez la documentation de la méthode `DELETE /api/v1/formations/{id}` sous la clé `paths[\"/api/v1/formations/{id}\"]` avec les réponses `200` et `404`."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.5 : INGÉNIERIE DE COLLECTION EN PRODUCTION (PAGINATION OFFSET VS CURSOR, FILTRAGE & TRI SÉCURISÉ)
    # =========================================================================
    "d5-l5": {
        "context": (
            "Sur un jeu d'essai local de dix enregistrements, une requête `SELECT * FROM inscriptions` sérialisée par `jsonify()` "
            "s'exécute en moins d'une milliseconde. Après vingt-quatre mois d'exploitation transactionnelle, lorsque la même table "
            "héberge cinq millions de lignes, exposer une collection non bornée déclenche une catastrophe en chaîne : le pilote SQL "
            "matérialise l'intégralité du curseur dans le tas CPython du worker Gunicorn, la sérialisation JSON monopolise le GIL "
            "pendant plusieurs secondes et le processus finit abattu par l'*OOM Killer* Linux.\n\n"
            "L'ingénierie des endpoints de collection à grande échelle repose dès lors sur trois invariants de conception : le "
            "plafonnement défensif des fenêtres de lecture, le passage d'une pagination naïve **`OFFSET / LIMIT`** en `O(N)` à une "
            "**pagination par curseur indexé (*Keyset / Seek Pagination*)** sur arbre B-Tree en temps quasi constant `O(log N)` quasi constant "
            "(`O(1)`), et la sécurisation stricte du tri dynamique contre l'injection SQL structurelle dans les clauses `ORDER BY`."
        ),
        "deep_sections": [
            {
                "heading": "1. Dégradation linéaire `O(N)` et dérive transactionnelle de `LIMIT / OFFSET`",
                "body": (
                    "#### Coût disque caché du balayage d'index et instabilité sous écritures concurrentes\n\n"
                    "La pagination numérotée classique (`GET /api/v1/inscriptions?page=2500&per_page=20`) traduit les paramètres d'URL en "
                    "`LIMIT 20 OFFSET 49980`. Une idée reçue tenace suppose que le moteur relationnel (PostgreSQL, SQLite, MySQL/InnoDB) saute "
                    "gratuitement à la ligne 49 980. En réalité, comme les feuilles d'un index B-Tree ne stockent pas le rang absolu de chaque "
                    "tuple visible par la transaction MVCC courante, le moteur d'exécution doit parcourir séquentiellement, filtrer et "
                    "compter les **49 980 premières entrées** avant de les jeter pour ne restituer que les 20 suivantes : la latence croît "
                    "linéairement en `O(OFFSET)` jusqu'à saturer le cache de pages.\n\n"
                    "De surcroît, `OFFSET` souffre d'une anomalie de cohérence en temps réel (*Page Drift*) : si un nouvel élément est inséré "
                    "en tête d'un tri décroissant pendant que l'utilisateur consulte la page 1, tous les rangs se décalent d'une unité vers le "
                    "bas, faisant réapparaître le 20e élément de la page 1 en première position de la page 2. Dans tous les cas, la vue Flask "
                    "doit imposer un bornage strict `per_page = min(100, max(1, request.args.get('per_page', 20, type=int)))` pour neutraliser "
                    "toute tentative de déni de service du type `?per_page=10000000`."
                )
            },
            {
                "heading": "2. Pagination *Keyset / Seek* par curseur B-Tree en `O(1)` et clé composite de départage",
                "body": (
                    "#### Traversée directe d'arbre B-Tree par prédicat `WHERE` indexé\n\n"
                    "Pour garantir un temps de réponse invariant inférieur à 2 millisecondes aussi bien au début qu'au cinquante-millionième "
                    "enregistrement, les APIs industrielles (Stripe, GitHub, Slack) substituent au numéro de page un **curseur d'ancrage** "
                    "encodant la position exacte du dernier élément reçu (`?after_id=1042&limit=20` ou un jeton opaque `Base64URL`). La "
                    "requête paramétrée devient un positionnement direct (*Index Seek*) dans l'arbre B-Tree de la clé primaire.\n\n"
                    "```sql\n"
                    "-- Complexite O(log N) ~ O(1) via l'index composite (date_creation, id)\n"
                    "SELECT id, titre, date_creation, tarif_dzd\n"
                    "FROM formations\n"
                    "WHERE (date_creation, id) > (:last_date, :last_id)\n"
                    "ORDER BY date_creation ASC, id ASC\n"
                    "LIMIT :limit;\n"
                    "```\n\n"
                    "> [!IMPORTANT] Toujours adjoindre une colonne unique de départage (*Tie-Breaker*)\n"
                    "> Si le curseur ne porte que sur un horodatage `date_creation` non unique, deux formations créées dans la même "
                    "milliseconde partageront la même valeur : filtrer par `WHERE date_creation > :last_date` sauterait définitivement les "
                    "homonymes temporels ! La comparaison lexicographique de n-uplets SQL `(date_creation, id) > (?, ?)` appuyée par un index "
                    "composite `(date_creation, id)` garantit un ordre total déterministe sans jamais perdre ni dupliquer aucune ligne."
                )
            },
            {
                "heading": "3. Filtrage paramétré et neutralisation de l'injection SQL sur `ORDER BY` par liste blanche",
                "body": (
                    "#### Limite structurelle des marqueurs liés (`?` / `%s`) face aux identifiants SQL\n\n"
                    "Dans le protocole de requêtes préparées de `sqlite3` ou `psycopg`, les marqueurs de liaison (`?` ou `:val`) lient "
                    "exclusivement des **littéraux de valeur** dans les prédicats (`WHERE domaine = ? AND tarif_dzd >= ?`) : la grammaire SQL "
                    "interdit formellement de paramétrer un identifiant structurel tel qu'un nom de table, un nom de colonne ou le mot-clé "
                    "directionnel `ASC`/`DESC`. Tenter de contourner cette règle par interpolation `f\"ORDER BY {request.args.get('sort')}\"` "
                    "introduit une **injection SQL d'ordre 1** exploitable par sous-requête booléenne (`?sort=(CASE WHEN ...)`).\n\n"
                    "```python\n"
                    "COLONNES_TRI_SURES = {\n"
                    "    \"id\": \"id\",\n"
                    "    \"tarif_dzd\": \"tarif_dzd\",\n"
                    "    \"duree_jours\": \"duree_jours\",\n"
                    "    \"titre\": \"titre\",\n"
                    "}\n\n"
                    "def construire_clause_order_by(param_sort: str) -> str:\n"
                    "    direction = \"DESC\" if param_sort.startswith(\"-\") else \"ASC\"\n"
                    "    cle_cliente = param_sort.lstrip(\"+-\")\n"
                    "    colonne_sql = COLONNES_TRI_SURES.get(cle_cliente)\n"
                    "    if colonne_sql is None:\n"
                    "        abort(422, description=f\"Critere de tri '{cle_cliente}' non autorise.\")\n"
                    "    return f\"{colonne_sql} {direction}, id {direction}\"\n"
                    "```\n\n"
                    "> [!TIP] Traduction par dictionnaire figé plutôt que simple validation\n"
                    "> Résoudre `colonne_sql = COLONNES_TRI_SURES.get(cle_cliente)` garantit que la chaîne concaténée dans la requête SQL "
                    "provient à 100 % d'une constante littérale écrite par le développeur dans le code source Python, et jamais d'un tampon "
                    "d'entrée issu de `request.args`, satisfaisant ainsi les analyseurs statiques de sécurité (`Bandit` / `Semgrep`)."
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
                ["Complexité algorithmique SQL", "`O(N)` — Ralentit à mesure que `OFFSET` augmente", "`O(1)` — Temps constant ultra-rapide via l'index B-Tree"],
                ["Saut direct vers une page (`Page 14`)", "Oui (idéal pour les grilles Web numérotées)", "Non (navigation séquentielle *Suivant / Précédent*)"],
                ["Stabilité en cas d'insertion temps réel", "Risque de décalage (un élément peut apparaître 2 fois)", "100 % stable (ancré sur l'identifiant unique `after_id`)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Accepter le paramètre `?per_page=` ou `?limit=` du client sans imposer de plafond maximum côté serveur",
                "good": "Toujours borner la limite : `per_page = min(50, max(1, request.args.get('per_page', 20, type=int)))`",
                "why": "Sans plafond `min(50, ...)`, un attaquant peut envoyer `?per_page=99999999` et provoquer un déni de service par saturation RAM."
            },
            {
                "bad": "Injecter directement le paramètre `?sort=` dans une requête SQL sans validation",
                "good": "Valider systématiquement la clé de tri contre un `set` Python (`CHAMPS_TRI_AUTORISES`) et renvoyer `422` en cas d'écart",
                "why": "C'est le seul moyen d'autoriser un tri dynamique tout en garantissant l'impossibilité absolue d'une injection SQL."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_5/02_pagination_filtrage_production.py` et observez comment `next_cursor` dans `/api/v1/catalogue/cursor` permet de parcourir toute la collection de 2 en 2 jusqu'à ce que `next_cursor` vaille `None`.",
            "Ajoutez un paramètre `?fields=id,titre` (*Sparse Fieldsets*) qui permet au client de ne recevoir que les colonnes demandées pour économiser la bande passante mobile."
        ]
    }
}
