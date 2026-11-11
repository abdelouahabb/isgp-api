"""
Manuel de Référence Approfondi — Enrichissement des Chapitres (Jours 4 et 5) — Volume III : Édition Tornado.
Fournit pour chaque chapitre :
- context : exposé complet de la problématique d'ingénierie
- deep_sections : sous-chapitres de cours détaillés (fondements théoriques et mécanismes internes)
- architecture_diagram : schéma ASCII de flux mémoire ou réseau
- reference_table : tableau de synthèse technique
- pitfalls : anti-patterns de production vs standards industriels
- practical_exercises : exercices progressifs de révision post-bootcamp
"""

ENRICHMENT_D4_D5 = {
    # =========================================================================
    # JOUR 4 — CHAPITRE 4.1 : CRYPTOGRAPHIE APPLIQUÉE, VARIABLES D'ENVIRONNEMENT & API KEYS
    # =========================================================================
    "d4-l1": {
        "context": (
            "Dès qu'une interface de programmation dépasse le stade du prototype expérimental, elle devient le gardien "
            "direct d'actifs critiques de l'institution : dossiers académiques nominatifs, écritures comptables, "
            "attestations officielles ou opérations d'administration système. Exposer de tels `RequestHandlers` sur un "
            "réseau TCP/IP sans architecture cryptographique rigoureuse revient à raccorder directement les tables de "
            "la base de données à Internet sans contrôle d'identité ni preuve d'intégrité.\n\n"
            "Or, les audits post-incident en entreprise révèlent une constante saisissante : l'immense majorité des "
            "compromissions d'APIs ne résulte pas d'une cassure mathématique d'AES ou de SHA-256, mais d'erreurs "
            "fondamentales d'ingénierie logicielle. Des développeurs confondent régulièrement la représentation "
            "textuelle réversible (`Base64`) avec le hachage irréversible (`PBKDF2`), figent des clés maîtresses en "
            "clair dans l'historique immuable de Git, bloquent l'`IOLoop` asynchrone de Tornado pendant le calcul "
            "intensif des mots de passe, ou comparent des secrets avec l'opérateur `==` vulnérable aux attaques "
            "temporelles (*Timing Side-Channel Attacks*). Ce chapitre établit les fondations cryptographiques et "
            "opérationnelles exigées sur tout serveur Tornado de production."
        ),
        "deep_sections": [
            {
                "heading": "1. Taxonomie cryptographique : Encodage, Hachage lent salé (`PBKDF2`) et Signature `HMAC` sous `IOLoop`",
                "body": (
                    "En ingénierie des systèmes sûrs, quatre transformations mathématiques distinctes remplissent des "
                    "contrats orthogonaux qu'il est impératif de ne jamais substituer l'une à l'autre. Leur maîtrise "
                    "conditionne aussi bien la confidentialité des données au repos que la disponibilité du moteur "
                    "événementiel de Tornado sous forte charge.\n\n"
                    "#### Encodage de transport (`Base64`, `UTF-8`, `Percent-Encoding`) : zéro confidentialité\n\n"
                    "Un schéma d'encodage comme `Base64` (RFC 4648) n'est pas un algorithme cryptographique et ne fait "
                    "intervenir aucun secret. Son unique rôle consiste à projeter une séquence arbitraire d'octets "
                    "binaires sur un alphabet restreint de 64 caractères ASCII imprimables afin qu'elle traverse sans "
                    "altération des protocoles textuels tels que les en-têtes HTTP ou les documents JSON. Toute entité "
                    "interceptant la chaîne invoque `base64.urlsafe_b64decode()` et retrouve instantanément l'intégralité "
                    "du texte clair en temps constant.\n\n"
                    "#### Fonctions de hachage rapide (`SHA-256`) vs dérivation lente salée (`PBKDF2-HMAC-SHA256`)\n\n"
                    "Une fonction de hachage cryptographique projette un message de longueur arbitraire vers un condensat "
                    "(*digest*) de taille fixe (32 octets, soit 64 chiffres hexadécimaux pour `SHA-256`) de manière "
                    "mathématiquement irréversible (*preimage resistance*). Toutefois, `SHA-256` a été conçu pour être "
                    "extrêmement rapide sur silicium : une grappe moderne de cartes graphiques (GPU) évalue plusieurs "
                    "dizaines de milliards de condensats `SHA-256` par seconde et épuise en quelques minutes tout "
                    "dictionnaire de mots de passe humains non salés ou précalculés dans des *Rainbow Tables*.\n\n"
                    "Pour protéger des mots de passe humains en base de données, la norme NIST SP 800-132 impose deux "
                    "contre-mesures conjointes : l'adjonction d'un **sel cryptographiquement aléatoire unique par "
                    "enregistrement** (`secrets.token_bytes(16)`), qui garantit que deux utilisateurs choisissant le "
                    "même mot de passe produisent deux condensats radicalement différents, et l'application d'une "
                    "**fonction de dérivation de clé volontairement coûteuse en CPU** telle que `PBKDF2-HMAC-SHA256` "
                    "(600 000 itérations recommandées par l'OWASP), `scrypt` ou `Argon2id`.\n\n"
                    "> [!WARNING] Protection de l'IOLoop Tornado face au coût CPU de PBKDF2\n"
                    "> Par conception, 600 000 itérations de `hashlib.pbkdf2_hmac` consomment entre 150 et 350 "
                    "millisecondes de calcul arithmétique pur sur un cœur CPU. Dans un serveur Tornado mono-thread, "
                    "exécuter cet appel directement sur le fil de l'`IOLoop` gèle l'intégralité des sockets `epoll` "
                    "pendant un tiers de seconde : dix connexions simultanées sur `/api/auth/login` suffisent alors à "
                    "paralyser le serveur pendant plus de trois secondes (déni de service asymétrique). En production, "
                    "déportez systématiquement la dérivation `PBKDF2` ou `Argon2` dans un pool de threads dédié via "
                    "`await IOLoop.current().run_in_executor(AUTH_EXECUTOR, verifier_mot_de_passe, clair, stocke)`.\n\n"
                    "#### Code d'authentification de message (`HMAC`, RFC 2104)\n\n"
                    "Contrairement au hachage nu où n'importe qui peut recalculer le condensat d'un message modifié, "
                    "la construction `HMAC` (*Hash-based Message Authentication Code*) mêle cryptographiquement le "
                    "message à une **clé secrète détenue par le serveur** à travers deux passes de hachage imbriquées. "
                    "Elle fournit simultanément une preuve d'intégrité (aucun bit n'a été altéré sur le réseau) et une "
                    "preuve d'authenticité (seul un détenteur de la clé secrète a pu forger cette étiquette).\n\n"
                    "> « HMAC can be used in combination with any iterated cryptographic hash function. The cryptographic "
                    "strength of HMAC depends upon the cryptographic strength of the underlying hash function, the size "
                    "of its hash output, and on the size and quality of the key. » — IETF RFC 2104, Section 1 (Krawczyk, Bellare & Canetti, 1997)"
                )
            },
            {
                "heading": "2. Gouvernance des secrets selon Twelve-Factor App : isolation par `os.environ`",
                "body": (
                    "Le code source applicatif d'une plateforme Tornado a vocation à être cloné sur les postes d'ingénierie, "
                    "inspecté par des analyseurs statiques en intégration continue (CI/CD) et répliqué sur des dépôts "
                    "Git distribués. Inscrire une clé cryptographique (`cookie_secret`, `JWT_SECRET_KEY`, identifiants "
                    "PostgreSQL ou jeton d'API partenaire) sous forme de constante littérale dans un module `.py` constitue "
                    "une vulnérabilité structurelle permanente : même si un commit ultérieur supprime la ligne fautive, "
                    "l'objet blob contenant le secret demeure intégralement extractible dans le graphe d'historique Git "
                    "via `git log -S` ou `git rev-list --all`.\n\n"
                    "#### Injection par l'environnement du processus système (`os.environ`)\n\n"
                    "Le troisième axiome de la méthodologie industrielle *Twelve-Factor App* stipule une séparation "
                    "hermétique entre le code immuable et la configuration d'exécution dépendante du déploiement. "
                    "Lorsqu'un gestionnaire de services Linux (`systemd`), un orchestrateur Kubernetes ou un démon Docker "
                    "instancie un processus Python Tornado, le noyau Linux peuple en mémoire le bloc d'environnement "
                    "privé du processus (`environ`), exposé en Python par le mapping `os.environ`.\n\n"
                    "```python — Chargement défensif des secrets au démarrage de l'application Tornado\n"
                    "import os\n"
                    "import secrets\n\n"
                    "def charger_secret_obligatoire(nom_variable: str, mode_dev: bool = False) -> bytes:\n"
                    "    valeur = os.environ.get(nom_variable)\n"
                    "    if valeur and len(valeur) >= 32:\n"
                    "        return valeur.encode(\"utf-8\")\n"
                    "    if mode_dev:\n"
                    "        return secrets.token_bytes(32)\n"
                    "    raise RuntimeError(\n"
                    "        f\"Demarrage refuse : variable critique {nom_variable} absente ou entropie < 32 octets.\"\n"
                    "    )\n"
                    "```\n\n"
                    "> [!IMPORTANT] Politique Fail-Fast au démarrage de Tornado\n"
                    "> En production (`mode_dev=False`), n'acceptez jamais une valeur par défaut statique telle que "
                    "`os.environ.get(\"SECRET_KEY\", \"dev-secret\")`. Si un opérateur déploie accidentellement un "
                    "conteneur en omettant d'injecter le secret depuis Vault ou Kubernetes Secrets, l'application "
                    "démarrerait silencieusement avec une clé publique connue de tous, permettant la forge immédiate "
                    "de jetons administrateur et de cookies `set_secure_cookie`. L'absence du secret doit provoquer un "
                    "arrêt immédiat (`RuntimeError`) avant même l'appel à `app.listen()`."
                )
            },
            {
                "heading": "3. Authentification Machine-to-Machine (`X-API-Key`) et neutralisation des Timing Attacks (`hmac.compare_digest`)",
                "body": (
                    "Dans les échanges automatisés de serveur à serveur (*Machine-to-Machine* ou *M2M*) — par exemple "
                    "lorsque le progiciel comptable d'une filiale synchronise chaque nuit les écritures de facturation "
                    "avec votre API Tornado — il n'existe aucun navigateur ni opérateur humain pour accomplir un flux "
                    "interactif de connexion. L'architecture standard consiste à provisionner pour chaque système "
                    "partenaire une **clé d'API à haute entropie** (`secrets.token_urlsafe(32)`, soit 256 bits d'aléa "
                    "cryptographique) transportée exclusivement dans un en-tête HTTP dédié tel que `X-API-Key`.\n\n"
                    "#### Pourquoi l'URL est un canal proscrit pour les secrets\n\n"
                    "Transmettre une clé secrète dans la chaîne de requête (`GET /api/v1/rapports?api_key=isgp_live_...`) "
                    "expose irrémédiablement le secret en texte clair dans au moins quatre couches d'infrastructure : "
                    "les journaux d'accès `access.log` des répartiteurs Nginx et des passerelles CDN, les journaux "
                    "automatiques `tornado.access` du serveur Python, l'historique local des outils de diagnostic, et "
                    "l'en-tête HTTP `Referer` potentiellement fuité vers des ressources externes. À l'inverse, un "
                    "en-tête HTTP `X-API-Key` circule à l'intérieur du tunnel chiffré TLS 1.3 et n'est jamais journalisé "
                    "par défaut par les serveurs mandataires.\n\n"
                    "#### Mécanique micro-architecturale de l'attaque temporelle (*Timing Side-Channel*) et `hmac.compare_digest`\n\n"
                    "L'opérateur d'égalité natif `==` de Python sur les objets `str` et `bytes` est optimisé pour la "
                    "vitesse d'exécution générale : sa boucle C interne compare les octets séquentiellement de l'indice "
                    "`0` à `N-1` et retourne `False` **dès le premier octet divergent** (court-circuit logique). Cette "
                    "optimisation crée un canal auxiliaire temporel mesurable. Un attaquant soumettant des dizaines de "
                    "milliers de requêtes concurrentes vers une `IOLoop` Tornado très réactive observe statistiquement "
                    "qu'un candidat dont le premier octet est exact met quelques dizaines de nanosecondes supplémentaires "
                    "avant d'être rejeté ; il verrouille ainsi le premier caractère, puis le second, réduisant une "
                    "complexité exponentielle `256^32` à une complexité linéaire triviale `256 * 32`.\n\n"
                    "```python — Vérification M2M à temps constant et dérivation asynchrone dans Tornado\n"
                    "import hashlib, hmac, os, secrets\n"
                    "from concurrent.futures import ThreadPoolExecutor\n"
                    "import tornado.ioloop\n"
                    "import tornado.web\n\n"
                    "CRYPTO_POOL = ThreadPoolExecutor(max_workers=4)\n\n"
                    "def verifier_pbkdf2(clair: str, empreinte_stockee: str) -> bool:\n"
                    "    _, algo, iter_s, sel_hex, hash_hex = empreinte_stockee.split(\"$\")\n"
                    "    calcule = hashlib.pbkdf2_hmac(\n"
                    "        algo, clair.encode(\"utf-8\"), bytes.fromhex(sel_hex), int(iter_s)\n"
                    "    ).hex()\n"
                    "    return hmac.compare_digest(calcule, hash_hex)\n\n"
                    "class RapportPartenaireHandler(tornado.web.RequestHandler):\n"
                    "    def prepare(self) -> None:\n"
                    "        cle_recue = self.request.headers.get(\"X-API-Key\", \"\")\n"
                    "        cle_attendue = os.environ.get(\"PARTNER_API_KEY\", \"\")\n"
                    "        if not cle_attendue or not hmac.compare_digest(\n"
                    "            cle_recue.encode(\"utf-8\"), cle_attendue.encode(\"utf-8\")\n"
                    "        ):\n"
                    "            self.set_status(401)\n"
                    "            self.finish({\"erreur\": \"Cle d'API absente ou invalide\"})\n"
                    "```\n\n"
                    "La primitive standard `hmac.compare_digest(a, b)` exécute en langage C une accumulation bit à bit "
                    "(`XOR` suivi d'un `OR` cumulatif sur chaque octet) sur toute la longueur des tampons lorsque leurs "
                    "tailles coïncident, sans aucun branchement conditionnel dépendant des valeurs secrètes. Le temps CPU "
                    "consommé devient rigoureusement indépendant de la position du premier octet erroné, neutralisant "
                    "à la racine toute tentative d'inférence statistique par mesure de latence."
                )
            }
        ],
        "architecture_diagram": (
            "FLUX DE VÉRIFICATION D'IDENTITÉ MACHINE (X-API-KEY) & MOT DE PASSE SALÉ\n"
            "========================================================================\n\n"
            "  [1] VÉRIFICATION D'UNE CLÉ D'API EN TEMPS CONSTANT :\n"
            "  Client HTTP                                     Serveur Tornado (RequestHandler)\n"
            "  En-tête : X-API-Key: isgp-live-98a7...  ----->  cle_client = self.request.headers.get('X-API-Key')\n"
            "                                                  cle_serveur = os.environ.get('PARTNER_API_KEY')\n"
            "                                                        |\n"
            "                                                  hmac.compare_digest(cle_client, cle_serveur)\n"
            "                                                  (Durée d'exécution constante : 0 fuite temporelle)\n\n"
            "  [2] STOCKAGE IRRÉVERSIBLE D'UN MOT DE PASSE UTILISATEUR (PBKDF2-HMAC-SHA256) :\n"
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
                ["Hachage lent salé (PBKDF2)", "Non (irréversible + lent)", "Non (Sel aléatoire inclus)", "`hashlib.pbkdf2_hmac('sha256', ...)`", "Stockage sécurisé des mots de passe humains en base de données"],
                ["Signature HMAC-SHA256", "Non (vérification par recalcul)", "Oui (Clé secrète serveur)", "`hmac.new(key, msg, hashlib.sha256)`", "Signature de jetons JWT/Bearer, `set_secure_cookie` et Webhooks"],
                ["Comparaison à temps constant", "N/A (Opérateur booléen)", "N/A", "`hmac.compare_digest(val1, val2)`", "Comparaison sécurisée de deux secrets (contre les Timing Attacks)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Stocker les mots de passe avec `hashlib.md5()` ou `sha256()` sans sel",
                "good": "Utiliser une fonction de dérivation lente avec salage automatique (`hashlib.pbkdf2_hmac` avec 600 000 itérations)",
                "why": "Les cartes graphiques (GPU) calculent plus de 50 milliards d'empreintes SHA-256 par seconde et cassent les mots de passe courants instantanément sans sel ni itérations lentes."
            },
            {
                "bad": "Passer la clé d'API dans les paramètres de requête URL (`GET /api/rapports?api_key=secret123`)",
                "good": "Transmettre systématiquement les clés et jetons dans les en-têtes HTTP (`X-API-Key` ou `Authorization`)",
                "why": "Les URLs complètes sont archivées en clair dans les fichiers `access.log` de tous les serveurs mandataires et dans l'historique navigateur."
            },
            {
                "bad": "Écrire `SECRET_KEY = 'mon_secret_de_prod'` directement dans `app.py` et pousser sur Git",
                "good": "Lire les secrets exclusivement depuis l'environnement système via `os.environ.get('TORNADO_COOKIE_SECRET')`",
                "why": "Tout secret commité dans Git reste lisible indéfiniment dans l'historique `git log -p` même après suppression."
            }
        ],
        "practical_exercises": [
            "Générez deux empreintes successives du même mot de passe `\"Bootcamp2026\"` à l'aide de la fonction `hacher_mot_de_passe(\"Bootcamp2026\")` puis inspectez leur structure interne séparée par `$` : démontrez comment l'extraction du sel hexadécimal embarqué permet à `verifier_mot_de_passe()` de recomposer exactement le même condensat sans jamais connaître le mot de passe initial en base.",
            "Concevez dans Tornado un registre serveur associant les condensats `SHA-256` de trois clés d'API à trois profils d'applications partenaires, puis implémentez un `RequestHandler` qui identifie le partenaire appelant dans `prepare(self)` via `hmac.compare_digest` sans jamais conserver les clés partenaires en clair en mémoire."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.2 : JETONS SIGNÉS (BEARER TOKENS / JWT) & EXPIRATION
    # =========================================================================
    "d4-l2": {
        "context": (
            "Lorsqu'un opérateur humain interagit avec votre plateforme depuis une application mobile native ou une "
            "interface monopage (SPA React ou Vue), l'architecture d'authentification doit concilier ergonomie, "
            "sécurité et élasticité horizontale. Exiger la saisie du mot de passe à chaque action est inacceptable, "
            "tandis que conserver ce mot de passe en mémoire sur le terminal client multiplie la surface de compromission.\n\n"
            "Historiquement, les frameworks Web monolithiques maintenaient un dictionnaire de sessions en mémoire vive "
            "serveur. Mais dès que l'on déploie un cluster de quatre à cinquante processus Tornado indépendants derrière "
            "un répartiteur Nginx pour exploiter tous les cœurs CPU, la mémoire RAM locale n'est plus partagée : une "
            "requête routée vers le nœud `8002` ignorerait tout d'une session ouverte une seconde plus tôt sur le nœud "
            "`8001`. L'industrie résout cette contrainte d'échelle par l'authentification **sans état (*Stateless*) par "
            "jeton signé (`Bearer Token` / `JWT`)** : après vérification initiale des identifiants, le serveur émet un "
            "titre d'identité auto-porteur, horodaté et cryptographiquement scellé par signature `HMAC`, vérifiable en "
            "quelques microsecondes par n'importe quel nœud Tornado sans aucun appel réseau ni lecture SQL."
        ),
        "deep_sections": [
            {
                "heading": "1. Structure binaire et cryptographique d'un jeton signé (`Header.Payload.Signature`, RFC 7519)",
                "body": (
                    "Qu'il suive le standard interopérable **JSON Web Token (JWT, RFC 7519)** ou le format compact "
                    "`URLSafeTimedSerializer` de la bibliothèque `itsdangerous`, un jeton signé repose sur l'assemblage "
                    "déterministe de segments sérialisés en `Base64URL` (variante sans caractères `+`, `/` ni remplissage "
                    "`=` afin d'être sûre dans les en-têtes et URLs) séparés par le délimiteur ASCII point (`.`).\n\n"
                    "#### Les trois segments canoniques du format JWT\n\n"
                    "Le premier segment, appelé **`Header` (JOSE Header)**, encode un objet JSON minimal déclarant le "
                    "type de jeton et l'algorithme cryptographique employé, typiquement `{\"alg\": \"HS256\", \"typ\": \"JWT\"}` "
                    "pour `HMAC-SHA256`. Le deuxième segment, nommé **`Payload` (ensemble de *Claims*)**, transporte les "
                    "assertions métier et temporelles : l'identifiant canonique du sujet (`sub`), ses attributs "
                    "d'habilitation (`role`, `scopes`), l'horodatage Unix d'émission (`iat` — *Issued At*), l'identifiant "
                    "unique du jeton (`jti`) et surtout la borne stricte d'expiration (`exp` — *Expiration Time*).\n\n"
                    "Le troisième segment constitue le sceau d'intégrité : le serveur concatène les représentations "
                    "`Base64URL` exactes des deux premiers segments jointes par un point, puis évalue "
                    "`HMAC_SHA256(ascii(b64_header + \".\" + b64_payload), SECRET_KEY)`. Parce que seule la grappe de "
                    "serveurs Tornado détient `SECRET_KEY` dans son espace `os.environ`, aucun client externe ne peut "
                    "produire une signature valide pour un `Payload` arbitraire.\n\n"
                    "> « JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred "
                    "between two parties. The claims in a JWT are encoded as a JSON object that is used as the payload "
                    "of a JSON Web Signature (JWS) structure, enabling the claims to be digitally signed or integrity "
                    "protected with a Message Authentication Code (MAC). » — IETF RFC 7519, Section 1 (Jones, Bradley & Sakimura, 2015)"
                )
            },
            {
                "heading": "2. L'invariant fondamental `Signé != Chiffré` : transparence du Payload et infalsifiabilité",
                "body": (
                    "La confusion entre **signature cryptographique (JWS)** et **chiffrement (JWE)** figure parmi les "
                    "causes les plus répandues de fuites de données sensibles dans les architectures d'API modernes. "
                    "Un jeton signé garantit l'**intégrité** et l'**authenticité de l'émetteur**, mais il n'offre "
                    "strictement **aucune confidentialité** vis-à-vis du porteur ou d'un observateur détenant le jeton.\n\n"
                    "#### Démonstration d'inspection immédiate sans clé secrète\n\n"
                    "Puisque le segment `Payload` est simplement converti en JSON puis encodé en `Base64URL`, n'importe "
                    "quel script client, extension de navigateur ou opérateur réseau ayant capturé le jeton peut en "
                    "extraire instantanément le contenu lisible sans posséder la `SECRET_KEY` du serveur. Il est donc "
                    "formellement interdit d'embarquer dans les *claims* d'un jeton un condensat de mot de passe, un "
                    "numéro fiscal confidentiel, des coordonnées bancaires ou un secret interne d'infrastructure.\n\n"
                    "```http — Inspection d'un jeton Bearer circulant dans un en-tête HTTP\n"
                    "GET /api/v1/auth/profil HTTP/1.1\n"
                    "Host: api.isgp.dz\n"
                    "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbWluZSIsInJvbGUiOiJsZWN0ZXVyIiwiZXhwIjoxNzYzNzQwODAwfQ.9vK8z_SignatureHMAC\n"
                    "```\n\n"
                    "#### Pourquoi la falsification d'élévation de privilèges échoue mathématiquement\n\n"
                    "Si le `Payload` est lisible par l'utilisateur, qu'est-ce qui empêche un attaquant de décoder le "
                    "deuxième segment, de remplacer `\"role\": \"lecteur\"` par `\"role\": \"admin\"`, de ré-encoder ce "
                    "JSON modifié en `Base64URL` et de le renvoyer au serveur Tornado ? L'effet d'avalanche de `SHA-256` : "
                    "la modification d'un seul bit dans le `Payload` bouleverse environ 50 % des bits du condensat "
                    "`HMAC-SHA256` recalculé par Tornado à la réception. Ne connaissant pas `SECRET_KEY`, l'attaquant est "
                    "incapable de calculer la nouvelle signature correspondante ; `hmac.compare_digest` constate la "
                    "divergence et le `RequestHandler` rejette immédiatement la requête avec `401 Unauthorized`.\n\n"
                    "> [!IMPORTANT] Ordre d'interception des exceptions temporelles et cryptographiques\n"
                    "> Dans `itsdangerous` (comme dans `PyJWT` où `ExpiredSignatureError` hérite de `InvalidTokenError`), "
                    "`SignatureExpired` est une sous-classe directe de `BadSignature`. Dans vos blocs `try / except` "
                    "Tornado, interceptez toujours `SignatureExpired` **avant** `BadSignature` : inverser cet ordre "
                    "masquerait les expirations légitimes sous des alertes de falsification cryptographique et priverait "
                    "le client du signal précis lui indiquant de déclencher son flux de rafraîchissement."
                )
            },
            {
                "heading": "3. Protocole `Authorization: Bearer` (RFC 6750) et extraction sans blocage dans Tornado",
                "body": (
                    "La spécification **IETF RFC 6750** normalise le transport des jetons d'accès dans HTTP/1.1 et HTTP/2 "
                    "au moyen de l'en-tête `Authorization: Bearer <token>`. Le qualificatif anglais *Bearer* signifie "
                    "littéralement « titre au porteur » : à l'image d'un billet de banque ou d'un ticket de transport "
                    "magnétique, la simple détention du jeton suffit à prouver le droit d'accès, sans qu'aucune "
                    "signature supplémentaire de la requête courante ne soit exigée. Ce modèle impose par conséquent "
                    "l'usage exclusif de **TLS (`https://`)** en production afin qu'aucun équipement intermédiaire ne "
                    "puisse capturer le jeton en transit.\n\n"
                    "#### Validation CPU pure en microsecondes sur l'IOLoop\n\n"
                    "Contrairement à `PBKDF2` qui est délibérément ralenti par 600 000 itérations lors du `POST /login` "
                    "initial, la vérification d'un jeton signé sur les milliers de requêtes suivantes n'exécute **qu'une "
                    "seule passe `HMAC-SHA256`** sur quelques centaines d'octets, soit moins de 5 microsecondes sur un "
                    "processeur moderne. Cette propriété s'harmonise idéalement avec l'architecture non bloquante de "
                    "Tornado : la validation dans `prepare(self)` ou `get_current_user(self)` s'effectue intégralement "
                    "dans le cache L1 du processeur sans jamais solliciter le disque, le réseau ni la base SQL.\n\n"
                    "```python — Validation stricte d'un en-tête RFC 6750 dans un RequestHandler Tornado\n"
                    "from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature\n"
                    "import tornado.web\n\n"
                    "class ProfilProtegeHandler(tornado.web.RequestHandler):\n"
                    "    def prepare(self) -> None:\n"
                    "        entete = self.request.headers.get(\"Authorization\", \"\")\n"
                    "        schema, _, jeton = entete.partition(\" \")\n"
                    "        if schema.lower() != \"bearer\" or not jeton.strip():\n"
                    "            self.set_header(\"WWW-Authenticate\", 'Bearer realm=\"api.isgp.dz\"')\n"
                    "            self.set_status(401)\n"
                    "            self.finish({\"erreur\": \"Jeton Bearer requis dans l'en-tete Authorization\"})\n"
                    "            return\n"
                    "        serialiseur = URLSafeTimedSerializer(self.settings[\"jwt_secret\"], salt=\"access-v1\")\n"
                    "        try:\n"
                    "            self.current_user = serialiseur.loads(jeton.strip(), max_age=900)\n"
                    "        except SignatureExpired:\n"
                    "            self.set_header(\"WWW-Authenticate\", 'Bearer error=\"invalid_token\", error_description=\"Token expired\"')\n"
                    "            self.set_status(401)\n"
                    "            self.finish({\"erreur\": \"Le jeton d'acces a expire\"})\n"
                    "        except BadSignature:\n"
                    "            self.set_header(\"WWW-Authenticate\", 'Bearer error=\"invalid_token\"')\n"
                    "            self.set_status(401)\n"
                    "            self.finish({\"erreur\": \"Signature du jeton invalide ou altérée\"})\n"
                    "```\n\n"
                    "> [!TIP] Usage de `str.partition(\" \")` et conformité `WWW-Authenticate`\n"
                    "> Préférez `entete.partition(\" \")` à `entete.split(\" \")` lors de l'analyse de l'en-tête "
                    "`Authorization` : `partition` ne lève jamais `ValueError` sur une chaîne malformée et résiste aux "
                    "espaces parasites. De plus, adjoindre l'en-tête normalisé `WWW-Authenticate: Bearer ...` sur toute "
                    "réponse `401` assure une conformité stricte avec les RFC 9110 et 6750, permettant aux clients HTTP "
                    "industriels d'automatiser la détection d'expiration."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE VIE D'UN JETON SIGNÉ STATELESS (BEARER TOKEN / JWT) DANS TORNADO\n"
            "=========================================================================\n\n"
            "  [ÉTAPE 1 : CONNEXION INITIALE (POST /api/auth/token -> TokenIssueHandler)]\n"
            "  Client Mobile / Web                              Serveur Tornado (Stateless)\n"
            "  {\"identifiant\": \"amine\", \"mot_de_passe\": \"...\"} -> 1. Vérifie le mot de passe\n"
            "                                                   2. Crée Payload {\"sub\": \"amine\", \"role\": \"admin\"}\n"
            "                                                   3. Signe avec SECRET_KEY + Timestamp actuel\n"
            "  Stocke le token en mémoire               <-----  200 OK : {\"access_token\": \"eyJ...Signature\"}\n\n"
            "  [ÉTAPE 2 : REQUÊTE SUR ROUTE PROTÉGÉE (GET /api/auth/profil -> ProfilHandler)]\n"
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
                ["En-tête `Authorization` absent ou sans préfixe `Bearer `", "Aucune (rejet pré-vérification)", "`401 Unauthorized`", "Le client n'a fourni aucune preuve d'identité valide", "Rediriger vers l'écran de connexion (`/api/auth/token`)"],
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
            "Générez un jeton valide via `POST /api/auth/token`, décodez son segment central avec `base64.urlsafe_b64decode` pour observer vos *claims* en clair, puis altérez un unique caractère du segment central avant de l'envoyer dans `Authorization: Bearer ...` afin de constater le rejet `401 BadSignature` par Tornado.",
            "Étendez `ProfilProtegeHandler` en utilisant `loads(jeton, max_age=900, return_timestamp=True)` afin d'inclure dans la réponse JSON l'horodatage ISO-8601 exact d'émission du jeton ainsi que le nombre de secondes restantes avant expiration."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.3 : AUTHENTIFICATION (AUTHN / 401) VS AUTORISATION (AUTHZ / 403, RBAC, SCOPES, BOLA)
    # =========================================================================
    "d4-l3": {
        "context": (
            "Dans la gouvernance des systèmes distribués (*API Management*), l'amalgame conceptuel et logiciel entre "
            "l'**Authentification (`AuthN`)** et l'**Autorisation (`AuthZ`)** engendre la vulnérabilité numéro un "
            "mondiale recensée par le référentiel **OWASP API Security Top 10 (2023)** : les défaillances de contrôle "
            "d'accès au niveau des objets (**API1:2023 — BOLA**, *Broken Object Level Authorization*) et au niveau des "
            "fonctions (**API5:2023 — BFLA**, *Broken Function Level Authorization*).\n\n"
            "Une proportion alarmante d'APIs en production se contente de valider la signature cryptographique du jeton "
            "`Bearer` à l'entrée du `RequestHandler`, puis exécute aveuglément la requête SQL demandée (`SELECT` ou "
            "`DELETE WHERE id = ?`) sans jamais confronter l'identité authentifiée à la propriété réelle de "
            "l'enregistrement ciblé. Il suffit alors à n'importe quel abonné légitime d'incrémenter l'identifiant dans "
            "l'URL pour exfiltrer l'intégralité de la base client. Ce chapitre instaure une frontière sémantique et "
            "architecturale étanche entre la preuve d'identité (`401`) et l'évaluation des permissions (`403`) à "
            "travers une défense en profondeur à trois étages : **RBAC**, **Scopes OAuth2** et **invariant Anti-BOLA**."
        ),
        "deep_sections": [
            {
                "heading": "1. Sémantique protocolaire stricte : `AuthN` (`401 Unauthorized`) contre `AuthZ` (`403 Forbidden`)",
                "body": (
                    "Malgré un accident historique de nommage dans la spécification HTTP/1.0 perpétué pour des raisons "
                    "de compatibilité ascendante dans la **RFC 9110**, les codes `401` et `403` traduisent deux états "
                    "automates mutuellement exclusifs que vos `RequestHandlers` Tornado ne doivent jamais intervertir, "
                    "sous peine de briser les machines à états des applications frontales et mobiles.\n\n"
                    "#### `401 Unauthorized` : échec d'Authentification (`AuthN` — « Qui êtes-vous ? »)\n\n"
                    "Le serveur émet `401` exclusivement lorsqu'il est incapable d'établir avec certitude l'identité de "
                    "l'appelant : l'en-tête `Authorization` est absent, la signature `HMAC` est corrompue ou la fenêtre "
                    "temporelle `exp` est échue. Sémantiquement, `401` signifie *Unauthenticated* et porte une promesse "
                    "conditionnelle : si le client renouvelle sa requête en fournissant des informations d'authentification "
                    "fraîches ou valides (via `/api/auth/refresh` ou une reconnexion), l'opération a une chance d'aboutir.\n\n"
                    "#### `403 Forbidden` : échec d'Autorisation (`AuthZ` — « Avez-vous cette habilitation ? »)\n\n"
                    "À l'inverse, le code `403` atteste que l'étape `AuthN` a **pleinement réussi** : Tornado a vérifié "
                    "la signature du jeton et sait pertinemment que l'appelant est `stagiaire_101`. Cependant, le moteur "
                    "de politique d'accès refuse à cette identité précise le droit d'invoquer cette méthode ou de toucher "
                    "cet objet métier. Renvoyer `401` à la place de `403` provoquerait un bogue grave côté client : "
                    "l'intercepteur HTTP de l'application mobile croirait son jeton expiré, appellerait `/api/auth/refresh` "
                    "en boucle infinie, ou déconnecterait brutalement un utilisateur pourtant légitimement connecté.\n\n"
                    "> « The 401 (Unauthorized) status code indicates that the request has not been applied because it "
                    "lacks valid authentication credentials for the target resource. [...] The 403 (Forbidden) status code "
                    "indicates that the server understood the request but refuses to authorize it. Re-authenticating will "
                    "make no difference. » — IETF RFC 9110, Sections 15.5.2 & 15.5.4 (Fielding, Nottingham & Reschke, 2022)"
                )
            },
            {
                "heading": "2. Défense en profondeur `AuthZ` : la triade RBAC, Scopes OAuth2 et propriété d'objet (Anti-BOLA)",
                "body": (
                    "Dans un système d'information de grade industriel, l'autorisation ne se réduit jamais à un simple "
                    "booléen `is_admin`. Elle s'articule comme un entonnoir de filtrage progressif où chaque requête "
                    "authentifiée doit franchir trois barrières orthogonales avant d'atteindre la couche de persistance.\n\n"
                    "#### Premier étage : contrôle d'accès basé sur les rôles (`RBAC` — *Role-Based Access Control*)\n\n"
                    "Le modèle `RBAC` gouverne l'accès aux **catégories de fonctionnalités** (*Function-Level Authorization*) "
                    "en rattachant chaque compte utilisateur à un profil organisationnel (`stagiaire`, `formateur`, "
                    "`auditeur`, `admin`). Par exemple, seule l'appartenance aux rôles `formateur` ou `admin` autorise "
                    "l'invocation de `POST /api/v1/formations`, tandis que la purge définitive `DELETE` demeure "
                    "strictement réservée au rôle `admin`. Ce contrôle neutralise la faille OWASP API5:2023 (`BFLA`).\n\n"
                    "#### Deuxième étage : restriction de délégation par `Scopes` OAuth2 (RFC 6749)\n\n"
                    "Un même administrateur peut émettre un jeton dédié à un script d'export nocturne de statistiques. "
                    "Si ce script se fait compromettre, il serait catastrophique qu'il hérite de la totalité des pouvoirs "
                    "destructeurs du compte `admin`. Les **`Scopes`** (`[\"formations:read\", \"rapports:export\"]`) "
                    "appliquent le **principe du moindre privilège au jeton lui-même** : ils définissent le sous-ensemble "
                    "maximal d'actions que ce porteur spécifique est autorisé à accomplir au nom de l'utilisateur.\n\n"
                    "#### Troisième étage : contrôle au niveau de l'instance d'objet (`Anti-BOLA` / OWASP API1:2023)\n\n"
                    "Même lorsque le rôle (`stagiaire`) et le scope (`dossiers:read`) autorisent l'appel de la route "
                    "générique `GET /api/v1/dossiers/([0-9]+)`, il reste à prouver la relation légitime entre l'appelant "
                    "et **l'enregistrement précis** désigné par l'identifiant capturé. C'est ici que réside la faille "
                    "`BOLA` (anciennement nommée `IDOR` — *Insecure Direct Object Reference*) : le `RequestHandler` doit "
                    "charger les métadonnées de l'objet (ou intégrer `AND proprietaire_id = ?` directement dans la clause "
                    "`WHERE` SQL) pour vérifier que `self.current_user[\"sub\"] == dossier[\"proprietaire\"]`, sauf "
                    "dérogation explicite pour un rôle d'encadrement habilité.\n\n"
                    "> [!WARNING] Discrétion d'énumération : `403 Forbidden` vs `404 Not Found` sur BOLA\n"
                    "> Sur des ressources hautement confidentielles (dossiers médicaux, enquêtes disciplinaires, comptes "
                    "privés), renvoyer `403 Forbidden` sur `GET /api/dossiers/9842` révèle à l'attaquant que le dossier "
                    "`9842` existe bel et bien en base, facilitant le dénombrement. La RFC 9110 (Section 15.5.4) "
                    "autorise explicitement un serveur qui souhaite dissimuler l'existence même d'une ressource non "
                    "autorisée à répondre `404 Not Found` lorsque la requête `SELECT ... WHERE id = ? AND proprietaire = ?` "
                    "ne ramène aucune ligne."
                )
            },
            {
                "heading": "3. Architecture du contexte d'identité dans Tornado : `get_current_user` et `self.current_user`",
                "body": (
                    "Le cycle de vie interne de `tornado.web.RequestHandler` possède une intégration native de premier "
                    "ordre pour transporter le contexte de sécurité à travers toutes les étapes d'une requête : la "
                    "propriété mémoïsée `self.current_user` couplée à la méthode surchargeable `get_current_user(self)`. "
                    "Lors du premier accès à `self.current_user` (ou lorsque vous l'assignez explicitement dans "
                    "`prepare(self)` ou un décorateur), Tornado met en cache le dictionnaire d'identité pour toute la "
                    "durée de vie de l'instance `RequestHandler` — laquelle, rappelons-le, est instanciée fraîchement "
                    "pour chaque requête HTTP entrante et détruite sitôt `on_finish()` terminé, garantissant une "
                    "isolation mémoire absolue entre deux requêtes concurrentes sur l'`IOLoop`.\n\n"
                    "```python — Pipeline multicouche AuthN + RBAC + Scopes + Anti-BOLA dans Tornado\n"
                    "class DossierStagiaireHandler(BaseAPIHandler):\n"
                    "    def get(self, dossier_id: str) -> None:\n"
                    "        identite = self.current_user  # Peuplé et vérifié en amont (AuthN)\n"
                    "        if identite is None:\n"
                    "            self.repondre_erreur(401, \"Authentification Bearer requise\")\n"
                    "            return\n\n"
                    "        # Niveau 1 & 2 (AuthZ fonctionnelle : RBAC + Scopes OAuth2)\n"
                    "        if identite.get(\"role\") not in {\"stagiaire\", \"admin\"}:\n"
                    "            self.repondre_erreur(403, \"Role non habilite pour ce module\")\n"
                    "            return\n"
                    "        if \"dossiers:read\" not in identite.get(\"scopes\", []):\n"
                    "            self.repondre_erreur(403, \"Scope 'dossiers:read' manquant sur ce jeton\")\n"
                    "            return\n\n"
                    "        # Niveau 3 (AuthZ sur l'instance d'objet : parade Anti-BOLA)\n"
                    "        dossier = DEPOT_DOSSIERS.get(int(dossier_id))\n"
                    "        if not dossier:\n"
                    "            self.repondre_erreur(404, \"Dossier introuvable\")\n"
                    "            return\n"
                    "        est_proprietaire = (dossier[\"proprietaire\"] == identite[\"sub\"])\n"
                    "        est_admin = (identite[\"role\"] == \"admin\")\n"
                    "        if not (est_proprietaire or est_admin):\n"
                    "            self.repondre_erreur(403, \"Acces interdit au dossier d'un tiers (Anti-BOLA)\")\n"
                    "            return\n\n"
                    "        self.write({\"statut\": \"ok\", \"dossier\": dossier})\n"
                    "```\n\n"
                    "En structurant systématiquement vos gestionnaires autour d'une classe mère `BaseAPIHandler` qui "
                    "résout `self.current_user` dès `prepare(self)`, vous éliminez le risque d'oublier la validation "
                    "cryptographique sur un nouvel endpoint et concentrez le code métier de `get()`, `put()` ou `delete()` "
                    "sur l'expression limpide des invariants d'autorisation et de propriété."
                )
            }
        ],
        "architecture_diagram": (
            "PIPELINE DÉCISIONNEL : AUTHENTIFICATION (401) VS AUTORISATION (403)\n"
            "===================================================================\n\n"
            "  Requête HTTP : GET /api/dossiers/102\n"
            "        |\n"
            "        v\n"
            "  +-------------------------------------------------------------------+\n"
            "  | ÉTAPE 1 : AUTHENTIFICATION (AuthN — Qui est l'appelant ?)         |\n"
            "  | Le jeton Bearer est-il présent, authentique (HMAC) et non expiré ?|\n"
            "  +-------------------------------------------------------------------+\n"
            "        | NON                                     | OUI (ex: sub=\"stagiaire_101\", role=\"stagiaire\")\n"
            "        v                                         v\n"
            "  [ 401 UNAUTHORIZED ]            +-------------------------------------------------------------------+\n"
            "  \"Identité inconnue ou expirée.  | ÉTAPE 2 : AUTORISATION (AuthZ — A-t-il le droit d'agir ?)         |\n"
            "   Veuillez vous authentifier.\"   | 2a. RBAC   : Le rôle est-il autorisé sur cette route ?            |\n"
            "                                  | 2b. SCOPES : Le jeton possède-t-il le scope 'dossiers:read' ?     |\n"
            "                                  | 2c. BOLA   : Est-il propriétaire ('stagiaire_101' == '102') ?     |\n"
            "                                  +-------------------------------------------------------------------+\n"
            "                                        | NON                                     | OUI\n"
            "                                        v                                         v\n"
            "                                  [ 403 FORBIDDEN ]                         [ 200 OK / ACTION EXÉCUTÉE ]\n"
            "                                  \"Identité reconnue (stagiaire_101), mais\n"
            "                                   droits insuffisants pour cet objet.\""
        ),
        "reference_table": {
            "title": "Matrice de Séparation : Authentification (`AuthN`) vs Autorisation (`AuthZ`) vs Anti-BOLA",
            "headers": ["Dimension Comparée", "Authentification (`AuthN`)", "Autorisation (`AuthZ`)", "Protection Anti-BOLA (OWASP #1)"],
            "rows": [
                ["Question posée par le serveur", "« Qui êtes-vous ? Prouvez votre identité. »", "« Avez-vous la permission d'exécuter cette action ? »", "« Cet enregistrement précis vous appartient-il ? »"],
                ["Éléments inspectés", "En-tête `Authorization: Bearer`, signature HMAC, expiration `exp`", "Attributs `role` (RBAC) et `scopes` (OAuth2) du jeton", "Comparaison `self.current_user['sub'] == ressource['proprietaire']`"],
                ["Code HTTP en cas d'échec", "`401 Unauthorized` (+ en-tête `WWW-Authenticate`)", "`403 Forbidden`", "`403 Forbidden` (ou `404` pour masquer l'existence)"],
                ["Action corrective côté client", "Se connecter (`POST /api/auth/login`) ou rafraîchir le jeton", "Demander une élévation de privilèges à l'administrateur", "Aucune : accès illégitime aux données d'un tiers bloqué"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Renvoyer `401 Unauthorized` lorsqu'un utilisateur connecté avec le rôle `stagiaire` tente d'accéder à `/api/admin`",
                "good": "Renvoyer `401` uniquement si l'identité est absente/invalide, et `403 Forbidden` si les permissions sont insuffisantes",
                "why": "Les applications frontales interprètent `401` comme une expiration de session et déconnectent l'utilisateur ou bouclent sur `/refresh`."
            },
            {
                "bad": "Masquer le bouton « Supprimer » dans l'interface React/mobile sans vérifier le rôle et le propriétaire côté serveur Tornado",
                "good": "Appliquer systématiquement les contrôles `AuthZ` (RBAC, Scopes et Anti-BOLA) dans le code Python du `RequestHandler`",
                "why": "Un attaquant utilise `curl` directement et contourne totalement l'interface graphique du navigateur."
            },
            {
                "bad": "Vérifier que le jeton est valide sur `GET /api/dossiers/([0-9]+)` sans vérifier à qui appartient le dossier",
                "good": "Comparer systématiquement `self.current_user['sub'] == dossier['proprietaire']` (ou `self.current_user['role'] == 'admin'`)",
                "why": "L'absence de contrôle de propriété sur l'objet (BOLA / IDOR) permet à tout utilisateur connecté d'aspirer les dossiers de tous les autres utilisateurs."
            }
        ],
        "practical_exercises": [
            "Exécutez le module `day_4/04_refresh_token_et_rbac.py` et tracez les cinq réponses protocolaires couvrant `200 OK`, `401 Unauthorized` et `403 Forbidden` afin de vérifier expérimentalement la frontière entre `AuthN`, `RBAC` et `Anti-BOLA`.",
            "Implémentez un prédicat d'autorisation métier `autoriser_lecture_note(identite, note)` combinant modèles RBAC et ABAC (*Attribute-Based Access Control*) : l'accès est accordé si l'appelant est l'auteur de la note, s'il possède le rôle `responsable_pedagogique` rattaché au même `departement_id` que la note, ou s'il détient le rôle global `admin`."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.4 : ROTATION ACCESS / REFRESH TOKENS & DÉCORATEUR @EXIGER_ACCES
    # =========================================================================
    "d4-l4": {
        "context": (
            "L'authentification purement *Stateless* étudiée au chapitre 4.2 révèle un compromis architectural "
            "fondamental dès qu'elle affronte les exigences opérationnelles d'une grande organisation : l'impossibilité "
            "de révoquer instantanément un jeton autonome sans réintroduire un état partagé côté serveur. Si l'on "
            "accorde à un `Access Token` une durée de validité de trente jours pour épargner aux utilisateurs mobiles "
            "des reconnexions répétées, le vol d'un téléphone ou le départ d'un collaborateur laisse une fenêtre de "
            "compromission active d'un mois entier. Inversement, abaisser cette validité à dix minutes restaure la "
            "sécurité mais détruit l'expérience utilisateur si l'application réclame le mot de passe quatre fois par heure.\n\n"
            "La norme OAuth 2.0 (RFC 6749 / RFC 9700) résout élégamment cette tension en dissociant le **transport "
            "haute fréquence** du **renouvellement contrôlé** grâce à une architecture asymétrique à deux jetons : "
            "un `Access Token` éphémère vérifié en mémoire vive pure sur 99 % du trafic, épaulé par un `Refresh Token` "
            "à longue durée de vie, isolé par domaine cryptographique (`salt`), révocable par identifiant `jti` et "
            "orchestré dans Tornado par des décorateurs déclaratifs sur les méthodes `RequestHandler`."
        ),
        "deep_sections": [
            {
                "heading": "1. Architecture bi-jeton (`Access` court Stateless vs `Refresh` long Stateful) et isolation par `salt`",
                "body": (
                    "Lorsqu'un client valide ses identifiants primaires sur `POST /api/v1/auth/login`, le gestionnaire "
                    "`LoginHandler` émet simultanément une paire de jetons aux propriétés temporelles et architecturales "
                    "strictement complémentaires.\n\n"
                    "#### L'`Access Token` (5 à 15 minutes) : vitesse maximale sur le chemin critique\n\n"
                    "Ce jeton accompagne chaque appel aux routes métier (`/api/v1/formations`, `/api/v1/dossiers/101`). "
                    "Sa validation demeure intégralement *Stateless* (un unique calcul `HMAC-SHA256` en RAM dans le "
                    "processus Tornado courant). Ainsi, 99 % des requêtes de votre cluster s'exécutent à pleine vitesse "
                    "sans jamais interroger de base de sessions externe. En cas d'exfiltration accidentelle d'un journal "
                    "réseau, son utilité pour un attaquant s'éteint d'elle-même au bout de quelques minutes.\n\n"
                    "#### Le `Refresh Token` (7 à 30 jours) : renouvellement silencieux et séparation de domaine\n\n"
                    "Conservé dans un coffre sécurisé du terminal (*Keychain* iOS, *Keystore* Android ou cookie `HttpOnly` "
                    "restreint à `Path=/api/v1/auth/refresh`), le `Refresh Token` n'est **jamais transmis aux routes "
                    "métier**. Il ne sort sur le réseau qu'une fois toutes les quinze minutes à destination exclusive de "
                    "`POST /api/v1/auth/refresh`. Pour interdire mathématiquement toute attaque par confusion de type de "
                    "jeton (*Token Substitution Attack*), les deux jetons doivent impérativement être signés sous deux "
                    "espaces cryptographiques distincts — soit par deux clés secrètes indépendantes, soit par dérivation "
                    "de domaine via des paramètres `salt` disjoints (`salt=\"isgp-access-v1\"` contre "
                    "`salt=\"isgp-refresh-v1\"`). Un `Refresh Token` présenté frauduleusement dans `Authorization: Bearer` "
                    "sur une route métier échoue alors dès la vérification `HMAC` avec `BadSignature`."
                )
            },
            {
                "heading": "2. Révocation par `jti` dans Redis, rotation atomique et détection de réutilisation",
                "body": (
                    "Parce que le `Refresh Token` n'est sollicité qu'une seule fois par quart d'heure et par utilisateur "
                    "actif, le serveur Tornado peut s'autoriser sur l'unique endpoint `/api/v1/auth/refresh` une lecture "
                    "réseau ultra-rapide (moins d'une milliseconde vers un cluster **Redis** via `redis.asyncio`) sans "
                    "dégrader la scalabilité globale de l'API.\n\n"
                    "#### Liste de révocation indexée par `jti` (*JWT ID*) avec expiration automatique (`TTL`)\n\n"
                    "Chaque `Refresh Token` embarque lors de sa création un identifiant universellement unique "
                    "`jti = secrets.token_hex(16)`. Lorsqu'un utilisateur se déconnecte explicitement (`POST /api/v1/auth/revoke`) "
                    "ou qu'un administrateur suspend un compte compromis, le serveur inscrit la clé `revoked:jti:<id>` "
                    "dans Redis en lui associant un délai d'expiration (`EXPIRE` / `TTL`) égal au temps de vie restant du "
                    "jeton. La mémoire de Redis demeure ainsi naturellement bornée : dès que le jeton aurait de toute "
                    "façon expiré mathématiquement, Redis purge automatiquement l'entrée de sa table de hachage.\n\n"
                    "> [!IMPORTANT] Rotation des Refresh Tokens et détection de vol (RFC 9700)\n"
                    "> Les meilleures pratiques modernes de sécurité OAuth 2.0 (RFC 9700, *OAuth 2.0 Security Best Current "
                    "Practice*) recommandent la **rotation à usage unique** (*Refresh Token Rotation*) : chaque appel "
                    "réussi à `/api/v1/auth/refresh` invalide immédiatement le `jti` du `Refresh Token` entrant et émet "
                    "un couple `{nouvel_access, nouveau_refresh}` rattaché à une même lignée (`family_id`). Si un `jti` "
                    "déjà consommé est présenté une seconde fois, le serveur a la preuve formelle qu'un doublon du jeton "
                    "a été dérobé et utilisé en parallèle : il révoque alors instantanément toute la lignée `family_id`, "
                    "éjectant simultanément le pirate et forçant une ré-authentification saine de l'utilisateur légitime."
                )
            },
            {
                "heading": "3. Ingénierie d'une fabrique de décorateurs compatibles `async def` (`@exiger_acces`) pour Tornado",
                "body": (
                    "Répéter manuellement l'extraction de l'en-tête `Authorization`, le décodage cryptographique et les "
                    "assertions de rôles ou de scopes en tête de cent méthodes `get()`, `post()`, `put()` et `delete()` "
                    "dégrade la lisibilité du code et garantit tôt ou tard un oubli humain lors d'une maintenance urgente. "
                    "En Python, une **usine à décorateurs paramétrée** permet d'exprimer la politique de sécurité de "
                    "manière déclarative directement au-dessus de chaque verbe HTTP du `RequestHandler`.\n\n"
                    "#### Compatibilité transparente avec les coroutines `async def` de Tornado\n\n"
                    "Une subtilité technique majeure distingue Tornado des frameworks synchrones : les méthodes d'un "
                    "`RequestHandler` peuvent être définies aussi bien de façon synchrone (`def get(self):`) que sous "
                    "forme de coroutines natives (`async def get(self):`) lorsqu'elles exécutent des appels `await`. "
                    "Si un décorateur enveloppe une coroutine sans propager `await` (ou si la fonction enveloppe est "
                    "`async def` et supporte `inspect.iscoroutinefunction`), Tornado doit pouvoir attendre la complétion "
                    "de la coroutine avant d'invoquer `self.finish()`. Définir l'enveloppe interne en `async def` et "
                    "inspecter le résultat avec `inspect.isawaitable()` garantit un fonctionnement universel sur tous les "
                    "gestionnaires Tornado.\n\n"
                    "```python — Usine à décorateurs asynchrone @exiger_acces pour RequestHandler Tornado\n"
                    "from functools import wraps\n"
                    "import inspect\n"
                    "from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature\n\n"
                    "def exiger_acces(roles_autorises: tuple[str, ...] = (), scope_requis: str | None = None):\n"
                    "    def decorateur(methode_http):\n"
                    "        @wraps(methode_http)\n"
                    "        async def enveloppe(self, *args, **kwargs):\n"
                    "            schema, _, jeton = self.request.headers.get(\"Authorization\", \"\").partition(\" \")\n"
                    "            if schema.lower() != \"bearer\" or not jeton:\n"
                    "                self.set_status(401)\n"
                    "                self.finish({\"erreur\": \"Authentification Bearer requise\"})\n"
                    "                return\n"
                    "            srv = URLSafeTimedSerializer(self.settings[\"jwt_secret\"], salt=\"access-token\")\n"
                    "            try:\n"
                    "                payload = srv.loads(jeton.strip(), max_age=900)\n"
                    "            except SignatureExpired:\n"
                    "                self.set_status(401)\n"
                    "                self.finish({\"erreur\": \"Access token expire — appelez /api/auth/refresh\"})\n"
                    "                return\n"
                    "            except BadSignature:\n"
                    "                self.set_status(401)\n"
                    "                self.finish({\"erreur\": \"Signature du jeton invalide\"})\n"
                    "                return\n"
                    "            if roles_autorises and payload.get(\"role\") not in roles_autorises:\n"
                    "                self.set_status(403)\n"
                    "                self.finish({\"erreur\": \"Role insuffisant pour cette ressource\"})\n"
                    "                return\n"
                    "            if scope_requis and scope_requis not in payload.get(\"scopes\", []):\n"
                    "                self.set_status(403)\n"
                    "                self.finish({\"erreur\": f\"Scope requis manquant : {scope_requis}\"})\n"
                    "                return\n"
                    "            self.current_user = payload\n"
                    "            resultat = methode_http(self, *args, **kwargs)\n"
                    "            if inspect.isawaitable(resultat):\n"
                    "                await resultat\n"
                    "        return enveloppe\n"
                    "    return decorateur\n"
                    "```\n\n"
                    "Grâce à `@wraps(methode_http)` du module standard `functools`, l'enveloppe préserve fidèlement "
                    "`__name__`, `__doc__` et `__wrapped__`, ce qui permet aux générateurs d'introspection OpenAPI et aux "
                    "traceurs de performance de continuer à identifier précisément chaque méthode décorée."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE ROTATION ACCESS TOKEN / REFRESH TOKEN & RÉVOCATION DANS TORNADO\n"
            "========================================================================\n\n"
            "  Client                                      Serveur Tornado\n"
            "  1. POST /api/auth/login              -----> LoginHandler vérifie identifiants\n"
            "     Reçoit Access (15m) + Refresh (7j)<----- Signe Access (salt='access') & Refresh (salt='refresh')\n"
            "        |\n"
            "  2. GET /api/dossiers/101 (Pendant 15m) ---> @exiger_acces vérifie Access Token -> 200 OK\n"
            "        |\n"
            "  3. [16 minutes plus tard : Access Token expiré -> 401 SignatureExpired]\n"
            "        |\n"
            "  4. POST /api/auth/refresh            -----> RefreshHandler :\n"
            "     (Envoie le Refresh Token)                1. Vérifie signature avec salt='refresh'\n"
            "                                              2. Vérifie jti NOT IN REFRESH_TOKENS_REVOQUES\n"
            "     Reçoit un nouvel Access (15m)     <----- 3. Émet un nouvel Access Token frais"
        ),
        "reference_table": {
            "title": "Comparaison Technique : `Access Token` vs `Refresh Token`",
            "headers": ["Propriété Technique", "`Access Token` (Jeton d'accès)", "`Refresh Token` (Jeton de renouvellement)"],
            "rows": [
                ["Durée de vie typique (`max_age`)", "Courte : 5 à 15 minutes (`300` à `900` s)", "Longue : 7 à 30 jours (`604800` à `2592000` s)"],
                ["Sel cryptographique (`salt`)", "`\"access-token\"`", "`\"refresh-token\"` (Empêche l'utilisation croisée)"],
                ["Routes où il est accepté", "Toutes les routes métier protégées (`/api/...`)", "Uniquement `POST /api/auth/refresh` et `/api/auth/revoke`"],
                ["Mode de validation", "100% Stateless (Calcul HMAC en RAM)", "Stateful léger (HMAC + vérification de non-révocation `jti` en Redis/BDD)"],
                ["Impact en cas de fuite", "Limité à quelques minutes", "Élevé, mais neutralisable immédiatement par révocation serveur"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Signer l'`Access Token` et le `Refresh Token` avec exactement la même clé et le même `salt` sans champ `type`",
                "good": "Isoler cryptographiquement les deux jetons via des `salt` distincts (`salt='access-token'` vs `salt='refresh-token'`)",
                "why": "Sans séparation de sel ou de type, un attaquant pourrait envoyer le `Refresh Token` (valable 30 jours) directement dans `Authorization: Bearer` sur les routes métier."
            },
            {
                "bad": "Oublier `@wraps(methode)` de `functools` lors de l'écriture d'un décorateur personnalisé",
                "good": "Toujours décorer la fonction interne `enveloppe` avec `@wraps(methode)`",
                "why": "Préserve le nom exact et les métadonnées d'introspection de la méthode décorée."
            }
        ],
        "practical_exercises": [
            "Implémentez dans `RefreshHandler.post` la **rotation stricte à usage unique** accompagnée d'une détection de compromission : associez un `family_id` lors du login initial, inscrivez chaque `jti` utilisé dans un dictionnaire `JTI_CONSOMMES`, et si un `jti` déjà consommé est rejoué, invalidez immédiatement l'intégralité du `family_id`.",
            "Vérifiez que votre décorateur `@exiger_acces` fonctionne de manière transparente à la fois sur une méthode synchrone `def get(self)` et sur une coroutine `async def post(self)` effectuant un `await asyncio.sleep(0.01)`."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.5 : LIMITATION DE DÉBIT (RATE LIMITING / 429) & QUOTAS
    # =========================================================================
    "d4-l5": {
        "context": (
            "L'authentification et l'autorisation protègent la confidentialité et l'intégrité des données, mais elles ne "
            "protègent nullement la **disponibilité opérationnelle** du serveur ni la maîtrise de ses coûts d'infrastructure. "
            "Sur Internet, deux menaces volumétriques pèsent en permanence sur une boucle événementielle Tornado : "
            "les attaques automatisées par dictionnaire ou bourrage d'identifiants (*Credential Stuffing*) visant "
            "`POST /api/v1/auth/login`, et le phénomène du « voisin bruyant » (*Noisy Neighbor*), lorsqu'un script "
            "partenaire pourtant dûment authentifié entre accidentellement dans une boucle `while True:` sans temporisation "
            "et inonde le serveur de milliers de requêtes par seconde.\n\n"
            "Sans régulation du flux en amont, un unique consommateur défaillant monopolise le temps CPU de sérialisation "
            "JSON, épuise le pool de connexions PostgreSQL et allonge la latence de l'`IOLoop` pour l'ensemble des "
            "autres usagers légitimes. L'ingénierie de la **limitation de débit (*Rate Limiting*)**, greffée dès le "
            "crochet `prepare(self)` de Tornado et adossée au statut normalisé **`429 Too Many Requests` (RFC 6585)**, "
            "érige une vanne de régulation mathématique qui garantit l'équité de service."
        ),
        "deep_sections": [
            {
                "heading": "1. Algorithmique du contrôle d'admission : Fixed Window, Sliding Window Log (`collections.deque`) et Token Bucket",
                "body": (
                    "Concevoir un limiteur de débit exige de choisir un compromis précis entre l'exactitude mathématique "
                    "du lissage temporel et l'empreinte mémoire par client actif.\n\n"
                    "#### Fenêtre fixe (*Fixed Window Counter*) et l'anomalie de rafale aux frontières\n\n"
                    "L'approche la plus élémentaire consiste à indexer un compteur entier sur la minute courante "
                    "(`int(time.time() // 60)`). Bien qu'elle ne consomme qu'un entier de 8 octets par client, elle "
                    "souffre d'un défaut géométrique bien connu : pour un plafond nominal de 100 requêtes par minute, "
                    "un client émettant 100 appels à `14:00:59.500` puis 100 autres à `14:01:00.100` respecte "
                    "individuellement chacune des deux fenêtres civiles tout en infligeant à votre serveur Tornado une "
                    "pointe réelle de **200 requêtes en 600 millisecondes**, soit le double exact de la capacité dimensionnée.\n\n"
                    "#### Journal à fenêtre glissante (*Sliding Window Log*) en `O(1)` amorti\n\n"
                    "L'algorithme implémenté dans notre laboratoire élimine tout artefact de frontière en conservant "
                    "pour chaque clé cliente une file à double entrée `collections.deque` ordonnée chronologiquement "
                    "des horodatages monotones (`time.monotonic()`) de ses requêtes acceptées. Lorsqu'une requête se "
                    "présente à l'instant `T` pour une fenêtre glissante `W = 20.0` secondes, une boucle `while q and q[0] <= T - W: q.popleft()` "
                    "évacue en tête de file les entrées périmées. Si `len(q)` atteint le plafond `MAX_REQ`, la requête "
                    "est immédiatement rejetée sans être enregistrée. Chaque horodatage n'entrant et ne sortant de la "
                    "`deque` qu'une seule fois, le coût algorithmique par requête est en temps constant **`O(1)` amorti**.\n\n"
                    "#### Seau à jetons (*Token Bucket*) et tolérance contrôlée aux rafales (*Bursts*)\n\n"
                    "Sur les passerelles industrielles à très grande échelle (Nginx `limit_req`, Envoy, AWS API Gateway), "
                    "le modèle privilégié est le **Seau à Jetons** : chaque client dispose d'un réservoir virtuel de "
                    "capacité maximale `B` (*burst*) qui se régénère continûment à la vitesse `R` jetons par seconde "
                    "(`jetons = min(B, jetons + (T - T_prec) * R)`). Il ne requiert que deux nombres flottants par "
                    "client en mémoire tout en autorisant une application Web qui charge simultanément quatre composants "
                    "graphiques au démarrage à consommer une brève rafale légitime sans subir de faux positifs `429`."
                )
            },
            {
                "heading": "2. Contrat protocolaire RFC 6585 : `429 Too Many Requests`, `Retry-After` et court-circuit `prepare(self)`",
                "body": (
                    "Rejeter un dépassement de cadence ne doit jamais ressembler à une panne serveur (`500`) ni à une "
                    "révocation définitive de droits (`403`). La **RFC 6585 (Section 4)** consacre le code **`429 Too "
                    "Many Requests`** à la signalisation explicite d'une contre-pression (*backpressure*) temporaire "
                    "invitant le client coopératif à ralentir sa cadence d'émission.\n\n"
                    "> « The 429 status code indicates that the user has sent too many requests in a given amount of time "
                    "(\"rate limiting\"). The response representations SHOULD include details explaining the condition, "
                    "and MAY include a Retry-After header indicating how long to wait before making a new request. » "
                    "— IETF RFC 6585, Section 4 (Nottingham & Fielding, 2012)\n\n"
                    "#### Interception précoce dans `prepare(self)` et observabilité des quotas\n\n"
                    "Dans le cycle interne `RequestHandler._execute()` de Tornado, `prepare(self)` s'exécute **avant** "
                    "l'invocation de `get()`, `post()` ou tout accès à la base de données. Appeler `self.set_status(429)` "
                    "suivi de `self.finish(...)` à l'intérieur de `prepare(self)` positionne le drapeau interne "
                    "`self._finished = True`, ce qui court-circuite instantanément le reste du cycle HTTP : la requête "
                    "excédentaire est écartée en quelques microsecondes sans gaspiller ni CPU métier ni connexion SQL.\n\n"
                    "```http — Réponse HTTP 429 auto-descriptive émise par Tornado\n"
                    "HTTP/1.1 429 Too Many Requests\n"
                    "Content-Type: application/problem+json; charset=UTF-8\n"
                    "X-RateLimit-Limit: 3\n"
                    "X-RateLimit-Remaining: 0\n"
                    "X-RateLimit-Reset: 1763741218\n"
                    "Retry-After: 14\n\n"
                    "{\"type\": \"https://api.isgp.dz/erreurs/quota-depasse\", \"title\": \"Too Many Requests\", \"status\": 429, \"retry_after_seconds\": 14}\n"
                    "```\n\n"
                    "Avec `Sliding Window Log`, le délai exact de libération du prochain créneau se déduit algébriquement "
                    "du plus ancien horodatage encore présent en tête de la file : "
                    "`retry_after = max(1, math.ceil(W - (T - file_client[0])))`. Les SDK industriels (Stripe, OpenAI, "
                    "boto3) lisent nativement cet en-tête `Retry-After` et suspendent leur coroutine exactement pendant "
                    "la durée prescrite au lieu d'aggraver la congestion par des réessais aveugles immédiats."
                )
            },
            {
                "heading": "3. Clé de partitionnement (`remote_ip` sous `xheaders=True` vs identité métier) et état distribué Redis",
                "body": (
                    "La pertinence d'un limiteur de débit dépend directement du discriminateur utilisé pour partitionner "
                    "les compteurs. Sur les endpoints publics pré-authentification (`/api/v1/auth/login`, catalogue "
                    "ouvert), le seul identifiant disponible est l'adresse réseau `self.request.remote_ip`. Toutefois, "
                    "deux subtilités d'infrastructure majeures doivent être anticipées.\n\n"
                    "#### Restitution de l'adresse IP réelle derrière Nginx et piège du NAT d'entreprise\n\n"
                    "Dès que Tornado opère derrière un répartiteur Nginx local, la socket TCP provient de `127.0.0.1`. "
                    "Omettre `xheaders=True` lors de l'instanciation de `tornado.httpserver.HTTPServer(app, xheaders=True)` "
                    "ferait partager un **unique compteur global `127.0.0.1`** à l'ensemble de la planète ! De plus, "
                    "même avec `xheaders=True`, trois cents étudiants d'un campus universitaire ou employés d'un ministère "
                    "sortant derrière un même routeur NAT partagent la même IP publique. Dès qu'une route est authentifiée, "
                    "indexez donc prioritairement vos quotas sur l'identifiant logique vérifié (`sub` du jeton Bearer ou "
                    "empreinte de la `X-API-Key`), ce qui permet en outre d'appliquer des paliers tarifaires différenciés.\n\n"
                    "> [!IMPORTANT] Du dictionnaire RAM mono-processus au script Lua atomique dans Redis\n"
                    "> Un dictionnaire Python en mémoire vive est parfaitement cohérent au sein d'un processus Tornado "
                    "unique (puisque l'`IOLoop` mono-thread exécute `prepare()` sans préemption concurrente entre deux "
                    "lignes synchrones). En revanche, lorsque vous déployez 4 processus Tornado derrière Nginx en "
                    "production, quatre dictionnaires RAM isolés laisseraient passer `4 * Quota` requêtes. En production "
                    "multi-nœuds, déportez l'état de la fenêtre glissante dans **Redis** (`ZREMRANGEBYSCORE` + `ZCARD` + "
                    "`ZADD` encapsulés dans un script `EVAL` Lua atomique interrogé en `async/await`), garantissant une "
                    "comptabilité globale exacte à l'échelle de tout le cluster."
                )
            }
        ],
        "architecture_diagram": (
            "ALGORITHME DE FENÊTRE GLISSANTE DANS PREPARE(SELF) (QUOTA = 3 REQ / 20s)\n"
            "========================================================================\n\n"
            "  Instant actuel : T = 100.0s  |  Fenêtre active : [80.0s ---> 100.0s]\n\n"
            "  Historique du client avant nettoyage : [ 65.0s,  85.0s,  90.0s,  96.0s ]\n"
            "                                           ^^^^^\n"
            "  1. Purge des entrées < 80.0s         : Exclut 65.0s -> Reste [ 85.0s, 90.0s, 96.0s ] (Taille = 3)\n"
            "  2. Vérification (Taille >= Quota 3)  : QUOTA ATTEINT !\n"
            "  3. Calcul de Retry-After             : 20 - (100.0 - 85.0) = 5 secondes\n"
            "  4. Réponse Tornado (self.finish)     : 429 Too Many Requests (Header Retry-After: 5)"
        ),
        "reference_table": {
            "title": "En-têtes HTTP Standards de Limitation de Débit (`Rate Limiting`)",
            "headers": ["En-tête HTTP / Code", "Valeur Exemple", "Présence", "Signification pour le Client Consommateur"],
            "rows": [
                ["Code `429 Too Many Requests`", "`429`", "Uniquement lors du dépassement", "La requête est refusée temporairement pour cause de dépassement de cadence"],
                ["`X-RateLimit-Limit`", "`3`", "Sur toutes les réponses (`200` et `429`)", "Plafond maximal de requêtes autorisées par fenêtre"],
                ["`X-RateLimit-Remaining`", "`0` à `3`", "Sur toutes les réponses (`200` et `429`)", "Nombre d'appels restants avant déclenchement du `429`"],
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
                "bad": "En production multi-instances (4 instances Tornado), stocker uniquement le compteur en RAM Python locale",
                "good": "En production distribuée, centraliser les compteurs dans un store partagé atomique comme **Redis** ou `limit_req_zone` de Nginx",
                "why": "Chaque processus Tornado ayant sa propre mémoire RAM isolée, un compteur en mémoire locale permettrait au client d'effectuer `4 x Quota` requêtes."
            }
        ],
        "practical_exercises": [
            "Faites évoluer le limiteur à fenêtre glissante basé sur `collections.deque` et `time.monotonic()` pour appliquer une politique de quotas différenciée selon le profil extrait d'un jeton signé : `5 requêtes / 60 s` pour le palier `standard` contre `30 requêtes / 60 s` pour le palier `entreprise`.",
            "Enregistrez une tâche périodique non bloquante avec `tornado.ioloop.PeriodicCallback(purger_clients_inactifs, 60_000)` qui supprime du dictionnaire en mémoire toute entrée cliente dont la `deque` est vide après élagage, prévenant ainsi toute fuite graduelle de mémoire vive face à des millions d'adresses IP éphémères."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.6 : SÉCURITÉ PÉRIMÉTRIQUE : CORS, SIGNATURES WEBHOOK HMAC & TAILLE MAXIMALE (413)
    # =========================================================================
    "d4-l6": {
        "context": (
            "Lorsqu'une API Tornado quitte l'environnement contrôlé des tests en ligne de commande pour intégrer un "
            "écosystème hétérogène d'entreprise, trois frontières périmétriques entrent immédiatement en jeu. "
            "D'abord, une application frontale React servie sur `https://portail.isgp.dz` se voit brutalement interdire "
            "par le navigateur la lecture des réponses de `https://api.isgp.dz` tant que le protocole de négociation "
            "inter-origines **`CORS` (*Cross-Origin Resource Sharing*)** n'est pas rigoureusement implémenté.\n\n"
            "Ensuite, l'intégration d'architectures événementielles asynchrones inverse les rôles : ce sont désormais "
            "des plateformes externes (passerelles monétiques Chargily ou Stripe, forges GitLab, opérateurs SMS) qui "
            "appellent vos endpoints publics de **Webhooks**, exigeant une preuve cryptographique `HMAC-SHA256` sur "
            "les octets bruts du réseau pour déjouer les notifications falsifiées et le rejeu. Enfin, le serveur HTTP "
            "doit borner strictement l'allocation des tampons d'entrée (`max_body_size` / **`413 Content Too Large`**) "
            "afin qu'une charge utile disproportionnée ne puisse jamais provoquer un épuisement mémoire (*Out-Of-Memory*) "
            "du processus Python."
        ),
        "deep_sections": [
            {
                "heading": "1. Mécanique navigateur de la *Same-Origin Policy* (`SOP`), négociation `CORS` et `def options(self)`",
                "body": (
                    "Contrairement à une idée reçue tenace, **`CORS` n'est pas un pare-feu protégeant le serveur contre "
                    "`curl`** (un script Python ou `curl` ignore totalement les en-têtes `CORS`). `CORS` (spécification "
                    "WHATWG Fetch) est un **protocole d'assouplissement sélectif** de la **Politique de Même Origine "
                    "(*Same-Origin Policy* — SOP)** imposée par les navigateurs Web pour protéger l'utilisateur final.\n\n"
                    "#### Pourquoi la SOP existe et comment se définit une Origine (RFC 6454)\n\n"
                    "Deux URLs ne partagent la même origine que si le triplet `(schéma, hôte, port)` concorde "
                    "intégralement : `http://localhost:3000` et `http://localhost:8888` sont deux origines étrangères "
                    "à cause du port, tout comme `https://portail.isgp.dz` et `https://api.isgp.dz` à cause du sous-domaine. "
                    "Sans la SOP, une page malveillante ouverte dans un onglet voisin pourrait exécuter en arrière-plan "
                    "`fetch('https://intranet-rh.entreprise.dz/bulletins')` et lire vos données confidentielles en "
                    "profitant de la session active de votre navigateur.\n\n"
                    "#### Le ballet protocolaire du *Preflight* `OPTIONS` dans Tornado\n\n"
                    "Dès qu'un script JavaScript frontal tente d'émettre une requête « non simple » — typiquement une "
                    "méthode mutatrice (`PUT`, `PATCH`, `DELETE`), un corps `Content-Type: application/json` ou un "
                    "en-tête `Authorization: Bearer ...` — le moteur du navigateur suspend l'appel métier et émet "
                    "automatiquement en éclaireur une requête de **pré-vérification (*Preflight*)** de verbe `OPTIONS` "
                    "accompagnée des en-têtes `Origin` et `Access-Control-Request-Headers`.\n\n"
                    "```python — Implémentation sécurisée du contrat CORS par liste blanche dans Tornado\n"
                    "ORIGINES_AUTORISEES = frozenset({\"https://portail.isgp.dz\", \"http://localhost:3000\"})\n\n"
                    "class BaseCORSHandler(tornado.web.RequestHandler):\n"
                    "    def set_default_headers(self) -> None:\n"
                    "        origine = self.request.headers.get(\"Origin\", \"\")\n"
                    "        if origine in ORIGINES_AUTORISEES:\n"
                    "            self.set_header(\"Access-Control-Allow-Origin\", origine)\n"
                    "            self.set_header(\"Vary\", \"Origin\")\n"
                    "            self.set_header(\"Access-Control-Allow-Credentials\", \"true\")\n"
                    "            self.set_header(\"Access-Control-Allow-Methods\", \"GET, POST, PUT, PATCH, DELETE, OPTIONS\")\n"
                    "            self.set_header(\"Access-Control-Allow-Headers\", \"Content-Type, Authorization, X-API-Key\")\n"
                    "            self.set_header(\"Access-Control-Max-Age\", \"600\")\n\n"
                    "    def options(self, *args, **kwargs) -> None:\n"
                    "        self.set_status(204)\n"
                    "        self.finish()\n"
                    "```\n\n"
                    "> [!IMPORTANT] Rôle critique de l'en-tête `Vary: Origin`\n"
                    "> Lorsque `Access-Control-Allow-Origin` reflète dynamiquement une origine issue d'une liste blanche "
                    "(au lieu d'une valeur statique), vous devez impérativement émettre `Vary: Origin`. Sans cet "
                    "indicateur, un cache intermédiaire CDN ou proxy d'entreprise pourrait mémoriser la réponse servie "
                    "à `https://portail.isgp.dz` et la rejouer avec le mauvais en-tête `Access-Control-Allow-Origin` à "
                    "une autre application autorisée, provoquant des pannes CORS intermittentes redoutables à diagnostiquer."
                )
            },
            {
                "heading": "2. Authentification des Webhooks entrants : `HMAC-SHA256` sur `self.request.body` et anti-rejeu",
                "body": (
                    "Dans une architecture pilotée par événements (*Event-Driven Architecture*), remplacer le scrutage "
                    "périodique (*polling*) par un **Webhook** élimine 99 % du trafic réseau inutile : dès qu'un virement "
                    "d'inscription est confirmé, le serveur du prestataire monétique émet une requête `POST` vers votre "
                    "endpoint Tornado `/api/v1/webhooks/paiement`. Parce que cet endpoint doit être joignable par un "
                    "serveur externe sur Internet, sa sécurité repose intégralement sur la **vérification d'une signature "
                    "`HMAC-SHA256` calculée avec un secret partagé (`WEBHOOK_SECRET`)**.\n\n"
                    "#### Pourquoi re-sérialiser le JSON brise irrémédiablement la vérification HMAC\n\n"
                    "La fonction de hachage `SHA-256` opère sur une **séquence exacte d'octets (`bytes`)**, et non sur "
                    "une équivalence sémantique d'objets JSON. Les deux séquences `b'{\"id\":1,\"ok\":true}'` et "
                    "`b'{\"ok\": true, \"id\": 1}'` représentent le même dictionnaire Python après `json.loads()`, mais "
                    "leurs condensats `HMAC-SHA256` n'ont aucun bit en commun. Dans Tornado, vous devez donc calculer "
                    "le `HMAC` directement sur **`self.request.body`** (les octets bruts lus sur la socket TCP par "
                    "`HTTP1Connection`) **avant** tout appel à `tornado.escape.json_decode()`.\n\n"
                    "#### Protection contre les attaques par rejeu (*Replay Attacks*) par liaison temporelle\n\n"
                    "Une signature valide sur le seul corps HTTP reste vulnérable au rejeu : si un attaquant capture un "
                    "Webhook légitime créditant un portefeuille de 10 000 DZD et le renvoie cinquante fois, la signature "
                    "demeure mathématiquement exacte ! Le standard industriel popularisé par Stripe lie donc l'horodatage "
                    "au message signé (`message_signe = timestamp_bytes + b\".\" + self.request.body`), rejette tout "
                    "écart horaire supérieur à 300 secondes (`abs(time.time() - int(ts)) > 300`), et mémorise l'`event_id` "
                    "traité pour garantir l'**idempotence**.\n\n"
                    "```python — Validation cryptographique complète d'un Webhook avec fenêtre anti-rejeu\n"
                    "import hashlib, hmac, time\n"
                    "import tornado.escape, tornado.web\n\n"
                    "EVENEMENTS_TRAITES: set[str] = set()\n\n"
                    "class PaiementWebhookHandler(tornado.web.RequestHandler):\n"
                    "    def post(self) -> None:\n"
                    "        ts_str = self.request.headers.get(\"X-Webhook-Timestamp\", \"\")\n"
                    "        sig_recue = self.request.headers.get(\"X-Webhook-Signature\", \"\")\n"
                    "        if not ts_str.isdigit() or abs(time.time() - int(ts_str)) > 300:\n"
                    "            self.set_status(401)\n"
                    "            self.finish({\"erreur\": \"Horodatage Webhook absent ou hors fenetre de tolerance (300s)\"})\n"
                    "            return\n"
                    "        secret = self.settings[\"webhook_secret\"].encode(\"utf-8\")\n"
                    "        charge_signee = ts_str.encode(\"ascii\") + b\".\" + self.request.body\n"
                    "        sig_attendue = \"sha256=\" + hmac.new(secret, charge_signee, hashlib.sha256).hexdigest()\n"
                    "        if not hmac.compare_digest(sig_recue, sig_attendue):\n"
                    "            self.set_status(401)\n"
                    "            self.finish({\"erreur\": \"Signature cryptographique Webhook invalide\"})\n"
                    "            return\n"
                    "        evenement = tornado.escape.json_decode(self.request.body)\n"
                    "        if evenement[\"event_id\"] in EVENEMENTS_TRAITES:\n"
                    "            self.write({\"statut\": \"deja_traite_idempotent\"})\n"
                    "            return\n"
                    "        EVENEMENTS_TRAITES.add(evenement[\"event_id\"])\n"
                    "        self.write({\"statut\": \"accepte\"})\n"
                    "```"
                )
            },
            {
                "heading": "3. Défense mémoire des tampons réseau Tornado : `max_body_size`, `max_buffer_size` et statut `413`",
                "body": (
                    "Dans le modèle par défaut de Tornado, le parseur bas niveau `tornado.http1connection.HTTP1Connection` "
                    "accumule l'intégralité des octets du corps de la requête entrante dans un tampon en mémoire vive "
                    "(`IOStream`) avant d'instancier le `RequestHandler` et d'exposer le résultat sous `self.request.body`. "
                    "Cette conception garantit que `prepare()` et `post()` accèdent au corps sans `await`, mais crée un "
                    "vecteur évident d'épuisement de RAM si aucune borne stricte n'est imposée.\n\n"
                    "#### Double ligne de défense : plafond global `HTTPServer` et plafond granulaire métier\n\n"
                    "Au niveau transport, `tornado.httpserver.HTTPServer` applique par défaut une limite globale "
                    "`max_body_size` de 100 Mo — une valeur adaptée au téléversement de fichiers mais beaucoup trop "
                    "permissive pour une API JSON pure où une charge légitime dépasse rarement 64 Ko : vingt connexions "
                    "malveillantes poussant chacune 95 Mo d'accolades JSON imbriquées suffiraient à engloutir près de "
                    "2 Go de RAM et à déclencher le tueur de processus Linux (*OOM Killer*).\n\n"
                    "> [!TIP] Configuration industrielle de `max_body_size` et `@stream_request_body`\n"
                    "> Pour une API REST JSON, abaissez le plafond global dès l'instanciation du serveur via "
                    "`HTTPServer(app, xheaders=True, max_body_size=1_048_576)` (1 Mo) et affinez par route sensible dans "
                    "`prepare(self)` en renvoyant **`413 Content Too Large`** (dénomination actualisée de `413 Payload "
                    "Too Large` dans la RFC 9110, Section 15.5.14) dès que `len(self.request.body)` excède le budget de "
                    "l'endpoint (par exemple 16 Ko sur `/login`). Si une route spécifique doit accepter des archives PDF "
                    "ou vidéo de plusieurs centaines de mégaoctets, décorez uniquement sa classe avec "
                    "`@tornado.web.stream_request_body` pour traiter les fragments au fil de l'eau dans "
                    "`data_received(self, chunk)` sans jamais les accumuler en mémoire vive."
                )
            }
        ],
        "architecture_diagram": (
            "DOUBLE MÉCANISME : PREFLIGHT CORS (NAVIGATEUR) & SIGNATURE HMAC (WEBHOOK)\n"
            "=========================================================================\n\n"
            "  [A] PRÉ-VÉRIFICATION CORS PAR LE NAVIGATEUR WEB :\n"
            "  Navigateur (https://portail.isgp.dz)             Serveur Tornado (https://api.isgp.dz)\n"
            "  1. OPTIONS /api/formations               ----->  def options(self) vérifie ORIGINES_AUTORISEES\n"
            "     Origin: https://portail.isgp.dz       <-----  204 No Content + Access-Control-Allow-Origin\n"
            "  2. POST /api/formations (+ JSON + Auth)  ----->  def post(self) -> 201 Created\n\n"
            "  [B] VÉRIFICATION CRYPTOGRAPHIQUE D'UN WEBHOOK DE PAIEMENT :\n"
            "  Serveur de Paiement                              Serveur API Tornado\n"
            "  Corps brut : b'{\"id\":101,\"statut\":\"paye\"}'       corps_brut = self.request.body\n"
            "  Header X-Webhook-Signature: sha256=9f8a.. -----> Attendu = HMAC(WEBHOOK_SECRET, corps_brut)\n"
            "                                                   hmac.compare_digest(Recu, Attendu) -> 200 OK"
        ),
        "reference_table": {
            "title": "Mécanismes de Sécurité Périmétrique (`CORS`, `Webhooks`, `413 Payload Too Large`)",
            "headers": ["Mécanisme Périmétrique", "En-têtes HTTP Impliqués", "Code HTTP d'Erreur", "Menace Neutralisée"],
            "rows": [
                ["Politique `CORS` stricte", "`Origin`, `Access-Control-Allow-Origin`, `Access-Control-Allow-Headers`", "Blocage côté navigateur", "Appel malveillant de l'API depuis un site tiers non autorisé"],
                ["Signature de Webhook `HMAC`", "`X-Webhook-Signature` (ex: `sha256=...`)", "`401 Unauthorized`", "Falsification d'événements asynchrones (faux paiements, faux statuts)"],
                ["Plafond de taille du Body", "`Content-Length`", "`413 Payload Too Large`", "Saturation de la mémoire vive (RAM) par envoi de charges géantes"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Configurer `Access-Control-Allow-Origin: *` (joker universel) sur une API privée",
                "good": "Maintenir une **liste blanche explicite** des domaines frontaux autorisés (`https://portail.isgp.dz`)",
                "why": "Le joker `*` autorise n'importe quel site Internet visité par l'utilisateur à interroger l'API depuis son navigateur."
            },
            {
                "bad": "Calculer le HMAC d'un Webhook après avoir parsé le JSON (`json.dumps(json_decode(self.request.body))`)",
                "good": "Calculer systématiquement le HMAC sur la séquence d'octets brute exacte `self.request.body`",
                "why": "Un seul espace ou retour à la ligne différent entre le formateur JSON de l'émetteur et celui de Python modifie totalement le hash SHA-256."
            }
        ],
        "practical_exercises": [
            "Exécutez le module `day_4/05_cors_webhooks_headers.py` et inspectez successivement les en-têtes d'un pré-vol `OPTIONS` accepté, la vérification `HMAC-SHA256` sur octets bruts et l'interception `413` sur dépassement de charge.",
            "Implémentez la défense complète contre les **attaques par rejeu (*Replay Attacks*)** en couplant l'en-tête `X-Webhook-Timestamp` à `self.request.body` dans le calcul `HMAC`, puis démontrez par un test unitaire qu'un Webhook authentique capturé il y a 10 minutes est systématiquement rejeté."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.7 : GESTION ET SÉCURITÉ DES COOKIES DANS TORNADO (HTTPONLY, SECURE, SAMESITE, SET_SECURE_COOKIE)
    # =========================================================================
    "d4-l7": {
        "context": (
            "Lorsqu'une application Web s'exécute dans un navigateur, une question d'architecture cruciale surgit lors "
            "de chaque revue de sécurité : dans quel espace mémoire du client faut-il conserver le titre de session ou "
            "le jeton d'accès de l'utilisateur ? De nombreux didacticiels grand public persistent à conseiller "
            "`window.localStorage`. Or, le référentiel OWASP proscrit formellement `localStorage` et `sessionStorage` "
            "pour tout secret d'authentification : à la moindre injection **XSS (*Cross-Site Scripting*)** dans un "
            "composant graphique ou une bibliothèque NPM tierce, une unique instruction JavaScript lit l'intégralité "
            "de `localStorage` et exfiltre silencieusement les jetons de tous les visiteurs.\n\n"
            "Tornado résout nativement ce dilemme grâce à une implémentation cryptographique exemplaire des **Cookies "
            "HTTP (RFC 6265)** : le mécanisme de cookies signés et horodatés v2 (`self.set_secure_cookie` et "
            "`self.get_secure_cookie` adossés à `cookie_secret`), verrouillé au niveau du moteur réseau du navigateur "
            "par le triptyque défensif **`HttpOnly`**, **`Secure`** et **`SameSite`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Protocole d'état HTTP (RFC 6265) : cycle `Set-Cookie`, transport automatique `Cookie` et `clear_cookie`",
                "body": (
                    "Contrairement à l'en-tête `Authorization: Bearer` que le code applicatif JavaScript doit lire en "
                    "mémoire et injecter manuellement sur chaque appel `fetch()`, le sous-système de cookies est géré "
                    "directement par la pile réseau native C++ du navigateur, en dehors du moteur d'exécution JavaScript.\n\n"
                    "#### Émission serveur, persistance isolée et destruction explicite\n\n"
                    "À l'issue d'une authentification valide sur `POST /api/v1/auth/cookie-login`, le `RequestHandler` "
                    "invoque `self.set_secure_cookie(\"isgp_session\", charge_json, expires_days=1, httponly=True, "
                    "secure=True, samesite=\"Strict\")`, ce qui ajoute un en-tête `Set-Cookie` à la réponse HTTP. "
                    "Sur toutes les requêtes ultérieures ciblant le même domaine et un chemin compatible, le navigateur "
                    "attache automatiquement l'en-tête `Cookie: isgp_session=...`, que Tornado décode et vérifie via "
                    "`self.get_secure_cookie(\"isgp_session\", max_age_days=1)`. Enfin, lors de la déconnexion, "
                    "`self.clear_cookie(\"isgp_session\")` émet un `Set-Cookie` portant une valeur vide et une date "
                    "`Expires` reculée d'un an dans le passé, ordonnant au navigateur la purge immédiate de son coffre.\n\n"
                    "```http — En-tête Set-Cookie blindé émis par Tornado (Format signé v2)\n"
                    "HTTP/1.1 200 OK\n"
                    "Set-Cookie: isgp_session=\"2|1:0|10:1763741500|12:isgp_session|24:eyJzdWIiOiJhbWluZSJ9|a8f9...hmac\"; Path=/; HttpOnly; Secure; SameSite=Strict\n"
                    "```"
                )
            },
            {
                "heading": "2. Le blindage périmétrique navigateur : `HttpOnly` (Anti-XSS), `Secure` (TLS) et `SameSite` (Anti-CSRF)",
                "body": (
                    "Émettre un cookie de session sans ses trois attributs de confinement revient à laisser le coffre "
                    "ouvert aux scripts tiers ou aux attaques réseau. Chacun des trois drapeaux neutralise une classe "
                    "d'attaque distincte du modèle de menace Web.\n\n"
                    "#### `HttpOnly` contre l'exfiltration XSS et `Secure` contre l'écoute passive\n\n"
                    "L'attribut `httponly=True` ordonne au navigateur de cloisonner hermétiquement le cookie hors du "
                    "DOM : tout appel à `document.cookie` depuis la console ou depuis un script XSS malveillant omet "
                    "totalement ce cookie. Parallèlement, `secure=True` interdit au navigateur de transmettre le cookie "
                    "sur une liaison `http://` en clair, prévenant toute interception (*Man-in-the-Middle*) lors d'une "
                    "redirection initiale sur un réseau Wi-Fi non fiable.\n\n"
                    "#### `SameSite` contre la falsification de requête inter-sites (*CSRF*)\n\n"
                    "Puisque le navigateur attache automatiquement les cookies, un site piégé `evil.example` visité par "
                    "un administrateur connecté pouvait autrefois soumettre à son insu un `<form method=\"POST\" "
                    "action=\"https://api.isgp.dz/virement\">`. L'attribut `samesite=\"Strict\"` coupe ce vecteur à la "
                    "racine : le navigateur refuse catégoriquement d'adjoindre le cookie dès que la requête est initiée "
                    "depuis un contexte inter-sites externe (tandis que `samesite=\"Lax\"` ne l'autorise que sur les "
                    "navigations de premier niveau sûres en `GET`)."
                )
            },
            {
                "heading": "3. Mécanique cryptographique interne de Tornado : format signé v2 (`_create_signature_v2`) et rotation de clés",
                "body": (
                    "Tornado distingue rigoureusement deux primitives sur `RequestHandler` : `self.set_cookie(nom, val)` "
                    "écrit une chaîne brute modifiable en trois secondes dans l'inspecteur F12 du navigateur (réservée "
                    "aux préférences cosmétiques comme `theme=sombre`), tandis que `self.set_secure_cookie(nom, val)` "
                    "mobilise le moteur cryptographique interne `tornado.web.create_signed_value`.\n\n"
                    "#### Anatomie du format signé v2 et immunité contre l'échange de cookies\n\n"
                    "Le format v2 de Tornado (`2|1:0|10:<timestamp>|12:<nom_cookie>|<len>:<b64_val>|<hmac_sha256>`) "
                    "encode chaque champ avec un préfixe de longueur explicite et **inclut le nom même du cookie** ainsi "
                    "que l'horodatage dans le calcul `HMAC-SHA256` dérivé de `cookie_secret`. Inclure le nom du cookie "
                    "dans la signature déjoue une attaque subtile : un utilisateur ne peut pas copier la valeur signée "
                    "d'un cookie secondaire `avatar=\"admin\"` pour la coller dans le cookie `role`. En cas d'altération "
                    "d'un seul bit ou de dépassement de `max_age_days` (31 jours par défaut), `get_secure_cookie()` "
                    "échoue en temps constant via `hmac.compare_digest` et retourne sobrement `None`.\n\n"
                    "> [!TIP] Rotation de `cookie_secret` sans déconnexion de masse en production\n"
                    "> Tornado accepte pour `cookie_secret` un dictionnaire versionné de clés "
                    "`{1: \"ancienne_cle...\", 2: \"nouvelle_cle...\"}` accompagné du réglage `key_version=2` dans "
                    "`Application(..., cookie_secret=CLES, key_version=2)`. Le préfixe `1:2|` du format v2 indique "
                    "alors la version de clé utilisée : Tornado signe tous les nouveaux cookies avec la clé `2`, tout en "
                    "continuant à valider sans coupure les sessions existantes signées avec la clé `1` le temps de la transition."
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE DE SÉCURITÉ DES COOKIES TORNADO : HTTPONLY + SAMESITE + SET_SECURE_COOKIE\n"
            "======================================================================================\n\n"
            "  Serveur Tornado (POST /api/auth/cookie-login)\n"
            "       |\n"
            "       |  self.set_secure_cookie('isgp_session', ..., httponly=True, secure=True, samesite='Strict')\n"
            "       v\n"
            "  +-----------------------------------------------------------------------------+\n"
            "  | Coffre-Fort Réseau du Navigateur (Isolé du DOM JavaScript)                  |\n"
            "  |                                                                             |\n"
            "  |  1. Script XSS malveillant appelle document.cookie  ---> BLOQUÉ (HttpOnly)  |\n"
            "  |  2. Site tiers evil.com tente un POST CSRF          ---> BLOQUÉ (SameSite)  |\n"
            "  |  3. Connexion non chiffrée http://                  ---> BLOQUÉ (Secure)    |\n"
            "  +-----------------------------------------------------------------------------+\n"
            "       |\n"
            "       |  Requête légitime même origine : Cookie: isgp_session=\"2|1:0|...\"\n"
            "       v\n"
            "  Serveur Tornado : self.get_secure_cookie('isgp_session') vérifie HMAC (cookie_secret) ---> 200 OK"
        ),
        "reference_table": {
            "title": "Matrice de Sécurité des Attributs d'un Cookie HTTP dans Tornado",
            "headers": ["Attribut / Méthode", "Paramètre Tornado", "Attaque Neutralisée", "Comportement du Navigateur / Serveur"],
            "rows": [
                ["`HttpOnly`", "`httponly=True`", "**XSS** (*Cross-Site Scripting* — vol de jeton via JS)", "Rend le cookie totalement invisible pour `document.cookie` en JavaScript"],
                ["`Secure`", "`secure=True`", "**Sniffing réseau / MitM** sur Wi-Fi public", "Ne transmet le cookie que sur un canal chiffré `https://`"],
                ["`SameSite=Strict` / `Lax`", "`samesite=\"Strict\"` ou `\"Lax\"`", "**CSRF** (*Cross-Site Request Forgery*)", "Interdit l'envoi automatique du cookie lors de requêtes `POST` déclenchées depuis un site tiers"],
                ["`clear_cookie`", "`self.clear_cookie(\"isgp_session\")`", "Persistance infinie sur un poste partagé", "Ordonne au navigateur de supprimer immédiatement le cookie"],
                ["Signature HMAC (`set_secure_cookie`)", "`cookie_secret=os.environ[...]`", "**Falsification client** (élévation de privilèges dans F12)", "Toute modification d'un octet du cookie fait que `get_secure_cookie()` retourne `None`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Stocker le rôle en clair dans un cookie non signé (`self.set_cookie('role', 'admin')`) et lui faire confiance",
                "good": "Toujours signer cryptographiquement les cookies d'identité via `self.set_secure_cookie` avec `cookie_secret`",
                "why": "Un cookie non signé est un simple texte que l'utilisateur peut modifier en 5 secondes dans les outils de développement (F12) de son navigateur."
            },
            {
                "bad": "Oublier `httponly=True` sur un cookie contenant un jeton JWT ou une session signée",
                "good": "Activer systématiquement `httponly=True` lors de l'appel à `self.set_secure_cookie`",
                "why": "Sans `HttpOnly`, n'importe quel script JavaScript tiers chargé dans la page peut lire `document.cookie` et dérober la session."
            }
        ],
        "practical_exercises": [
            "Interrogez `POST http://127.0.0.1:8888/api/sandbox/cookies/login` avec `curl -i` afin d'analyser structurellement les six segments séparés par `|` du format signé v2 de Tornado ainsi que les directives `HttpOnly` et `SameSite`.",
            "Configurez une `tornado.web.Application` munie d'un dictionnaire `cookie_secret={1: \"cle_v1...\", 2: \"cle_v2...\"}` et `key_version=2`, puis démontrez qu'un cookie précédemment signé sous la version `1` continue d'être accepté sans erreur par `get_secure_cookie()`."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.1 : CONSOMMER UNE API TIERCE (ASYNCHTTPCLIENT RÉSILIENT, TIMEOUTS & RETRIES)
    # =========================================================================
    "d5-l1": {
        "context": (
            "Dans un système d'information réel structuré en microservices ou interconnecté à des partenaires "
            "institutionnels, votre serveur Tornado agit rarement en vase clos : au cours du traitement d'une requête "
            "entrante, il devient lui-même **client HTTP en aval** pour consulter un cours de change bancaire, valider "
            "un identifiant fiscal auprès d'un registre national ou ordonner l'expédition d'un courriel transactionnel.\n\n"
            "C'est précisément sur ces appels sortants que surviennent les pannes en cascade (*Cascading Failures*) "
            "les plus destructrices sur une architecture événementielle. Invoquer un client synchrone tel que "
            "`requests.get()` ou `urllib.request.urlopen()` à l'intérieur d'un `RequestHandler` gèle le descripteur "
            "de thread unique de l'`IOLoop` : pendant qu'un serveur partenaire ralenti met dix secondes à répondre, "
            "plus aucune des mille autres connexions ouvertes sur votre nœud Tornado ne reçoit le moindre octet ! "
            "Ce chapitre détaille l'ingénierie des appels sortants non bloquants via **`tornado.httpclient.AsyncHTTPClient`**, "
            "encadrés par des budgets temporels stricts et un recul exponentiel avec gigue (*Jitter*)."
        ),
        "deep_sections": [
            {
                "heading": "1. Mécanique des pannes en cascade et multiplexage `epoll` d'`AsyncHTTPClient`",
                "body": (
                    "Lorsqu'un client synchrone classique émet une requête TCP sortante, le noyau Linux endort le "
                    "processus appelant sur l'appel système `recv()` jusqu'à l'arrivée des paquets distants. Dans un "
                    "processus Tornado mono-thread, endormir le thread principal revient à arrêter le cœur même de "
                    "`IOLoop` : les acceptations de sockets `accept()`, les lectures d'en-têtes et même la sonde "
                    "`/api/health/live` cessent instantanément de répondre, poussant l'orchestrateur à abattre le conteneur.\n\n"
                    "#### Suspension coopérative de coroutine et double garde-fou temporel\n\n"
                    "À l'inverse, `tornado.httpclient.AsyncHTTPClient` ouvre une socket cliente en mode **`O_NONBLOCK`**, "
                    "l'enregistre auprès du même sélecteur noyau `epoll` que le serveur entrant, puis **suspend "
                    "uniquement la coroutine courante** à l'instruction `await client.fetch(requete)`. Le fil d'exécution "
                    "retourne aussitôt à l'`IOLoop` pour servir des milliers d'autres usagers jusqu'à ce que le noyau "
                    "signale la disponibilité de la réponse aval ou l'échéance d'un chronomètre interne (`connect_timeout` "
                    "pour la poignée de main TCP/TLS et `request_timeout` pour le transfert complet).\n\n"
                    "> [!WARNING] Obligation absolue de borner `connect_timeout` et `request_timeout`\n"
                    "> Même en mode asynchrone non bloquant, laisser un `fetch()` sans budget temporel strict accumule "
                    "des coroutines et des tampons mémoire suspendus lorsqu'un partenaire subit une partition réseau "
                    "silencieuse (*blackhole TCP*). Spécifiez systématiquement des délais courts adaptés au budget de "
                    "latence interactif (par exemple `connect_timeout=1.5` et `request_timeout=3.0` secondes)."
                )
            },
            {
                "heading": "2. Résilience par recul exponentiel avec gigue (*Exponential Backoff & Jitter*) et traduction `502` / `504`",
                "body": (
                    "Tous les échecs d'une dépendance externe ne appellent pas la même réaction algorithmique. Une "
                    "erreur `4xx` (`400`, `401`, `404`, `422`) exprime un rejet déterministe du contrat : réessayer "
                    "immédiatement est pur gaspillage. En revanche, une expiration de délai (`599` interne Tornado / "
                    "`TimeoutError`) ou une erreur `502`, `503`, `504` trahit fréquemment une micro-congestion réseau "
                    "transitoire qu'un nouvel essai espacé résout avec succès.\n\n"
                    "#### Prévenir l'effet de troupeau (*Thundering Herd*) par `await asyncio.sleep` et gigue aléatoire\n\n"
                    "Si cinq cents coroutines échouent au même instant `T` face à un partenaire surchargé et réessaient "
                    "toutes exactement à `T + 1.000s`, elles lui infligent une seconde vague synchronisée qui l'achève. "
                    "On combine donc une progression géométrique (`base * 2 ** essai`) à une **gigue aléatoire "
                    "(*Full Jitter*)** via `random.uniform`, en suspendant la coroutine exclusivement avec **`await "
                    "asyncio.sleep(delai)`** — et jamais `time.sleep()`, qui gèlerait l'`IOLoop`.\n\n"
                    "```python — Appel sortant résilient non bloquant avec AsyncHTTPClient dans Tornado\n"
                    "import asyncio, random\n"
                    "from tornado.httpclient import AsyncHTTPClient, HTTPRequest\n\n"
                    "async def interroger_partenaire_resilient(url: str) -> tuple[int, bytes]:\n"
                    "    client = AsyncHTTPClient()\n"
                    "    for essai in range(3):\n"
                    "        req = HTTPRequest(url=url, method=\"GET\", connect_timeout=1.5, request_timeout=2.5)\n"
                    "        rep = await client.fetch(req, raise_error=False)\n"
                    "        if 200 <= rep.code < 300:\n"
                    "            return 200, rep.body\n"
                    "        if 400 <= rep.code < 500:\n"
                    "            return 502, b'{\"erreur\": \"Rejet deterministe du partenaire amont\"}'\n"
                    "        if essai < 2:\n"
                    "            plafond = 0.2 * (2 ** essai)\n"
                    "            await asyncio.sleep(random.uniform(plafond / 2, plafond))\n"
                    "    statut_passerelle = 504 if rep.code == 599 else 502\n"
                    "    return statut_passerelle, b'{\"erreur\": \"Partenaire externe indisponible\"}'\n"
                    "```\n\n"
                    "Passer `raise_error=False` à `client.fetch()` est une idiomatique Tornado précieuse : au lieu de "
                    "lever une exception coûteuse sur chaque code non-`2xx`, Tornado retourne proprement un objet "
                    "`HTTPResponse` dont `rep.code == 599` identifie sans ambiguïté un dépassement de délai (traduit "
                    "vers le client final en **`504 Gateway Timeout`**), tandis qu'un `5xx` distant ou un corps JSON "
                    "illisible se traduit sémantiquement en **`502 Bad Gateway`**."
                )
            },
            {
                "heading": "3. Moteur `SimpleAsyncHTTPClient` vs `CurlAsyncHTTPClient`, pool `max_clients` et idempotence",
                "body": (
                    "Sous le capot, `AsyncHTTPClient()` est une fabrique configurée à l'échelle de l'`IOLoop` qui "
                    "s'appuie par défaut sur `SimpleAsyncHTTPClient` (implémentation pure Python légère et sans "
                    "dépendance C externe) et bride par sécurité la concurrence sortante simultanée à `max_clients=10` "
                    "(les requêtes excédentaires patientant proprement dans une file interne bornée).\n\n"
                    "#### Dimensionnement de haute charge et règle d'idempotence sur les réessais\n\n"
                    "Pour une passerelle Tornado d'agrégation appelée à maintenir plusieurs centaines de requêtes "
                    "sortantes en parallèle vers des moteurs internes rapides, relevez ce plafond dès l'amorçage du "
                    "processus via `AsyncHTTPClient.configure(None, max_clients=100)` (ou activez "
                    "`tornado.curl_httpclient.CurlAsyncHTTPClient` adossé à `libcurl` C pour le multiplexage HTTP/2 "
                    "et les proxys d'entreprise). Enfin, n'appliquez **jamais** de boucle de `Retry` automatique sur "
                    "une mutation `POST` non idempotente (comme un débit bancaire) dépourvue d'en-tête `Idempotency-Key` : "
                    "un `Timeout` à la lecture de la réponse ne prouve nullement que le partenaire n'a pas déjà exécuté "
                    "la transaction !"
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE D'UN APPEL SORTANT NON BLOQUANT (ASYNCHTTPCLIENT + RETRY BACKOFF)\n"
            "==============================================================================\n\n"
            "  Client Mobile          Votre API Tornado (Async Handler)       API Partenaire Externe\n"
            "       |                              |                                    |\n"
            "       |--- GET /api/devises -------->|                                    |\n"
            "       |                              |--- Essai 1 (request_timeout=2s) -->|\n"
            "       |                              |<-- [HTTP 503 / Timeout] -----------X\n"
            "       |                              |    await asyncio.sleep(0.2s)       |\n"
            "       |                              |--- Essai 2 (request_timeout=2s) -->|\n"
            "       |                              |<-- 200 OK (Taux EUR/DZD) ----------|\n"
            "       |<-- 200 OK (Enrichi) ---------|                                    |\n\n"
            "  (Si les 3 essais échouent par Timeout ---> Votre API répond 504 Gateway Timeout)"
        ),
        "reference_table": {
            "title": "Matrice de Gestion des Pannes lors d'un Appel HTTP vers un Partenaire Externe",
            "headers": ["Situation Rencontrée en Aval (Partenaire)", "Code / Exception Tornado", "Faut-il Réessayer (`Retry`) ?", "Code HTTP Renvoyé par Votre API"],
            "rows": [
                ["Partenaire répond `200 OK` avec JSON valide", "`resp.code == 200`", "Non (Succès immédiat)", "`200 OK`"],
                ["Partenaire ne répond pas dans `request_timeout`", "`HTTPClientError(599)` / `TimeoutError`", "Oui (2 à 3 fois max avec Backoff)", "`504 Gateway Timeout` (ou `200` dégradé avec cache)"],
                ["Partenaire répond `500`, `502` ou `503`", "`resp.code >= 500`", "Oui (Erreur transitoire serveur)", "`502 Bad Gateway`"],
                ["Partenaire répond `400`, `401`, `403` ou `404`", "`400 <= resp.code < 500`", "Non (Échec déterministe immédiat)", "`502 Bad Gateway` (ou code métier approprié)"],
                ["Partenaire renvoie du HTML au lieu de JSON", "`json.JSONDecodeError`", "Non", "`502 Bad Gateway`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Appeler `time.sleep(2)` ou `requests.get(url)` de manière synchrone à l'intérieur d'un `RequestHandler` Tornado",
                "good": "Utiliser `async def get(self):`, `await AsyncHTTPClient().fetch(req)` et `await asyncio.sleep(...)`",
                "why": "Un appel bloquant gèle l'`IOLoop` Tornado et bloque toutes les autres requêtes concurrentes du processus."
            },
            {
                "bad": "Faire un `Retry` automatique sur une opération de paiement (`POST`) sans clé d'idempotence",
                "good": "Ne réessayer automatiquement que les requêtes idempotentes (`GET`, `PUT`, `DELETE`) ou munies d'une `Idempotency-Key`",
                "why": "Si la 1re requête avait abouti mais que seule la réponse s'est perdue sur le réseau, réessayer un `POST` non idempotent exécute l'opération deux fois."
            }
        ],
        "practical_exercises": [
            "Exécutez le module `day_5/01_client_python_auth.py` pour observer en temps réel comment `AsyncHTTPClient(..., raise_error=False)` absorbe deux erreurs transitoires `503` grâce à `await asyncio.sleep()` sans jamais figer la boucle d'événements.",
            "Enrichissez votre client sortant d'un automate **Circuit Breaker** à trois états (`CLOSED`, `OPEN`, `HALF_OPEN`) : au bout de cinq échecs consécutifs vers le partenaire, basculez en état `OPEN` pendant 30 secondes afin de retourner immédiatement `503` en microsecondes sans saturer le réseau aval."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.2 : ARCHITECTURE MODULAIRE, SOUS-TABLES DE ROUTAGE & CYCLE DE VIE API (/api/v1 vs /api/v2)
    # =========================================================================
    "d5-l2": {
        "context": (
            "Lorsqu'une plateforme Tornado passe de dix routes expérimentales à cent cinquante `RequestHandlers` "
            "maintenus par plusieurs équipes d'ingénierie, deux défis d'architecture logicielle deviennent "
            "déterminants. Le premier concerne la **modularité interne** : comment structurer le routage, l'injection "
            "de configuration et les sondes d'orchestration sans transformer `app.py` en un monolithe indéchiffrable ?\n\n"
            "Le second touche à la **gouvernance temporelle des contrats publics** : pourquoi la quasi-totalité des "
            "grandes plateformes mondiales (Stripe, OpenAI, Kubernetes) exposent-elles `/v1/` pendant près d'une "
            "décennie sans créer `/v2/` chaque trimestre, tout en rendant obligatoire ce préfixe `/api/v1` dès la "
            "première mise en ligne ? Ce chapitre formalise l'assemblage modulaire par **Application Factory "
            "(`create_app`)**, le principe de robustesse de Postel (*Tolerant Reader*) et le cycle protocolaire "
            "normalisé de dépréciation **IETF RFC 8594 (`Deprecation` et `Sunset`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Gouvernance des contrats : Loi de Postel, évolutions additives (`/api/v1`) vs ruptures (`/api/v2`)",
                "body": (
                    "Une interface REST publique constitue un engagement contractuel envers des clients dont vous ne "
                    "maîtrisez pas le calendrier de mise à jour (applications mobiles installées sur des centaines de "
                    "milliers de téléphones ou connecteurs ERP d'entreprises partenaires). Si l'on observe que `/api/v1` "
                    "perdure cinq à dix ans en production, c'est parce qu'une conception disciplinée permet de réaliser "
                    "plus de **90 % des évolutions métier de manière purement additive et rétrocompatible**.\n\n"
                    "> « Be conservative in what you do, be liberal in what you accept from others. » "
                    "— Jon Postel, IETF RFC 761 (Principe de robustesse / Patron *Tolerant Reader* de Martin Fowler)\n\n"
                    "#### Frontière formelle entre changement additif et *Breaking Change*\n\n"
                    "Conformément au patron *Tolerant Reader*, ajouter une nouvelle clé JSON dans une réponse existante "
                    "(par exemple `\"certifiant\": true`), exposer un nouvel endpoint (`GET /api/v1/certificats`) ou "
                    "accepter un paramètre de requête facultatif muni d'une valeur par défaut ne brise aucun client `v1` "
                    "existant : un désérialiseur bien écrit ignore les clés inconnues. À l'inverse, supprimer ou "
                    "renommer un attribut (`intitule` remplacé par `titre`), muter le type structurel d'un champ "
                    "(transformer l'entier `\"duree\": 5` en objet `{\"valeur\": 5, \"unite\": \"jours\"}`) ou rendre "
                    "obligatoire un nouveau champ en entrée constitue une **rupture de contrat (*Breaking Change*)**. "
                    "Présence vitale dès le Jour 1, le préfixe `/api/v1` agit alors comme une police d'assurance : il "
                    "permet de monter `/api/v2` en parallèle sur le même serveur Tornado sans casser une seule "
                    "application mobile en circulation."
                )
            },
            {
                "heading": "2. Coexistence multi-versions dans Tornado et protocole officiel d'extinction IETF RFC 8594 (`Sunset`)",
                "body": (
                    "Lorsqu'une rupture de schéma justifie l'ouverture de `/api/v2`, l'ingénierie de production proscrit "
                    "toute coupure brutale de `/api/v1`. Les deux versions cohabitent durant une fenêtre de migration "
                    "annoncée (six à douze mois) en partageant strictement la **même couche de services métier et la "
                    "même base SQL** : seuls les adaptateurs de sérialisation des deux `RequestHandlers` diffèrent.\n\n"
                    "#### Signalisation machine-lisible de fin de vie dans `set_default_headers(self)`\n\n"
                    "Plutôt que d'espérer que tous les développeurs partenaires lisent une lettre d'information, les "
                    "spécifications **IETF RFC 8594 (`Sunset`)** et **`Deprecation`** injectent l'avis d'extinction "
                    "directement dans les en-têtes HTTP de chaque réponse `v1`, permettant aux passerelles et journaux "
                    "clients de remonter des alertes proactives automatisées.\n\n"
                    "```http — En-têtes normalisés RFC 8594 émis par FormationsV1Handler\n"
                    "HTTP/1.1 200 OK\n"
                    "Content-Type: application/json; charset=UTF-8\n"
                    "Deprecation: true\n"
                    "Sunset: Thu, 31 Dec 2026 23:59:59 GMT\n"
                    "Link: </api/v2/formations>; rel=\"successor-version\"\n"
                    "```\n\n"
                    "Une fois l'échéance `Sunset` échue et le trafic résiduel tombé à zéro dans les métriques d'accès, "
                    "les routes `/api/v1/*` ne sont pas remplacées par un `404 Not Found` ambigu, mais par un gestionnaire "
                    "dédié renvoyant **`410 Gone`** (RFC 9110, Section 15.5.11), qui atteste formellement que la "
                    "ressource a existé autrefois mais a été définitivement retirée au profit de `/api/v2`."
                )
            },
            {
                "heading": "3. Sous-tables de routage modulaires, *Application Factory* (`create_app`) et sondes Kubernetes",
                "body": (
                    "Contrairement aux micro-frameworks reposant sur un singleton global décoré à l'importation, "
                    "Tornado représente nativement sa table de routage comme une **structure de données pure** : une "
                    "séquence ordonnée de tuples `(motif_regex, ClasseHandler, dict_init)` ou d'objets `tornado.web.URLSpec`. "
                    "Chaque domaine fonctionnel (`routes_v1.py`, `routes_v2.py`, `routes_health.py`) expose ainsi une "
                    "fonction pure retournant sa sous-liste de routes, assemblée proprement par concaténation dans une "
                    "fabrique **`create_app(settings_override=None) -> tornado.web.Application`**.\n\n"
                    "#### Distinction vitale entre sonde *Liveness* (`/live`) et sonde *Readiness* (`/ready`)\n\n"
                    "En environnement conteneurisé (Kubernetes, Docker Swarm, Cloud Run) ou derrière Nginx Plus, toute "
                    "application Tornado industrielle expose deux sondes de santé aux sémantiques strictement distinctes.\n\n"
                    "> [!IMPORTANT] Ne jamais interroger la base de données dans la sonde Liveness (`/api/health/live`)\n"
                    "> La sonde **Liveness (`/api/health/live`)** répond à l'unique question : « Le processus Python et "
                    "son `IOLoop` sont-ils vivants (non bloqués en interblocage) ? » en renvoyant immédiatement `200 OK` "
                    "en mémoire. La sonde **Readiness (`/api/health/ready`)**, quant à elle, exécute un `SELECT 1` rapide "
                    "et renvoie `503 Service Unavailable` si PostgreSQL est en maintenance afin que le répartiteur suspende "
                    "temporairement l'envoi de trafic. Si vous mettiez le test SQL dans `/live`, une brève panne de base "
                    "de données pousserait Kubernetes à redémarrer en boucle tous vos conteneurs Tornado pourtant sains !"
                )
            }
        ],
        "architecture_diagram": (
            "COEXISTENCE MULTI-VERSIONS (/api/v1 DÉPRÉCIÉE + /api/v2) DANS TORNADO\n"
            "=====================================================================\n\n"
            "  Clients Historiques (App Mobile v1)            Nouveaux Clients (Portail Web / App v2)\n"
            "  GET /api/v1/formations                         GET /api/v2/formations\n"
            "            |                                              |\n"
            "            v                                              v\n"
            "  +--------------------------------------------------------------------------+\n"
            "  | APPLICATION FACTORY : create_app() -> tornado.web.Application            |\n"
            "  |                                                                          |\n"
            "  |  [FormationsV1Handler]                      [FormationsV2Handler]        |\n"
            "  |  r'/api/v1/formations'                      r'/api/v2/formations'        |\n"
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
            }
        ],
        "practical_exercises": [
            "Interrogez `GET http://127.0.0.1:8888/api/v1/sandbox/formations` avec `curl -i` pour relever le trio d'en-têtes `Deprecation`, `Sunset` et `Link`, puis comparez l'arbre JSON retourné par `/api/v2/sandbox/formations`.",
            "Exécutez `day_5/03_architecture_blueprints.py` et ajoutez un gestionnaire `GoneV0Handler` monté sur `r\"/api/v0/.*\"` qui renvoie `410 Gone` accompagné d'un en-tête `Link` pointant vers `/api/v2/formations`."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.3 : TESTS AUTOMATISÉS (TORNADO.TESTING), OPENAPI 3.0 & DÉPLOIEMENT CLUSTER NGINX
    # =========================================================================
    "d5-l3": {
        "context": (
            "Livrer en production une plateforme Tornado critique exige de franchir le fossé qui sépare un script "
            "fonctionnant sur le poste d'un développeur d'un système distribué auditable, vérifiable automatiquement "
            "et capable de saturer l'ensemble des cœurs matériels d'un serveur Linux multiprocesseur.\n\n"
            "Trois disciplines d'ingénierie industrielle convergent à ce stade : le harnais de **tests d'intégration "
            "asynchrones (`tornado.testing.AsyncHTTPTestCase`)** qui valide en quelques centaines de millisecondes "
            "les chemins nominaux comme les contrats d'erreur sur une boucle événementielle dédiée ; la publication "
            "d'un **schéma formel OpenAPI 3.0** ; et la topologie de **déploiement multi-processus derrière Nginx "
            "(`HTTPServer(app, xheaders=True)`)** permettant de contourner le verrou global de l'interpréteur Python "
            "(*GIL — Global Interpreter Lock*)."
        ),
        "deep_sections": [
            {
                "heading": "1. Harnais de test isolé avec `tornado.testing.AsyncHTTPTestCase` et `@gen_test`",
                "body": (
                    "Vérifier manuellement cent routes avec `curl` est incompatible avec l'intégration continue moderne. "
                    "Tornado intègre dans sa bibliothèque standard la classe **`tornado.testing.AsyncHTTPTestCase`** "
                    "(héritant de `unittest.TestCase`), qui orchestre pour chaque méthode `test_*` un cycle d'isolation "
                    "hermétique : instanciation d'une nouvelle `asyncio` / `IOLoop` vierge, ouverture d'un `HTTPServer` "
                    "lié à un port TCP éphémère alloué par le noyau (`127.0.0.1:0` évitant toute collision de port en CI "
                    "parallèle), exécution de requêtes HTTP réelles de bout en bout via `self.fetch(\"/api/...\")`, puis "
                    "fermeture propre de toutes les sockets dans `tearDown()`.\n\n"
                    "```python — Suite d'intégration complète avec AsyncHTTPTestCase\n"
                    "import tornado.escape, tornado.testing\n\n"
                    "class CatalogueAPITest(tornado.testing.AsyncHTTPTestCase):\n"
                    "    def get_app(self):\n"
                    "        return create_app({\"testing\": True, \"jwt_secret\": \"cle-test-ci-32-octets-minimum!!\"})\n\n"
                    "    def test_creation_formation_et_rejet_422(self):\n"
                    "        rep_invalide = self.fetch(\n"
                    "            \"/api/v1/formations\", method=\"POST\", body=b'{\"duree\": -3}',\n"
                    "            headers={\"Content-Type\": \"application/json\"}\n"
                    "        )\n"
                    "        self.assertEqual(rep_invalide.code, 422)\n"
                    "        self.assertIn(\"application/problem+json\", rep_invalide.headers[\"Content-Type\"])\n"
                    "```\n\n"
                    "> [!TIP] Symétrie des assertions : cas nominaux et matrice des Unhappy Paths\n"
                    "> Une suite professionnelle ne se limite jamais au code `200 OK` : pour chaque `RequestHandler`, "
                    "exigez la vérification du **statut HTTP**, du **`Content-Type`** et du **corps désérialisé** sur "
                    "l'ensemble des cas de rejet (`400` JSON tronqué, `401` sans jeton, `403` BOLA, `404` et `422`)."
                )
            },
            {
                "heading": "2. Contrat formel `OpenAPI 3.0` exposé sur `/api/openapi.json` comme source unique de vérité",
                "body": (
                    "Dans une architecture découplée, le code Python de vos `RequestHandlers` demeure invisible pour les "
                    "équipes iOS, Android ou partenaires externes. Publier sur un endpoint dédié (`GET /api/openapi.json`) "
                    "un document conforme à la norme **OpenAPI Specification 3.0 (OAS)** transforme la documentation "
                    "en artefact exécutable : ce graphe JSON déclare de manière déterministe les serveurs cibles, les "
                    "chemins paramétrés, les schémas de validation JSON Schema des charges utiles, les réponses RFC 7807 "
                    "et les mécanismes d'authentification (`securitySchemes`), permettant aussi bien la génération "
                    "automatique de SDK clients typés que la validation contractuelle en pipeline CI/CD."
                )
            },
            {
                "heading": "3. Topologie Linux de production : contourner le GIL CPython par `Nginx -> N x Tornado HTTPServer(xheaders=True)`",
                "body": (
                    "Bien qu'un unique processus Tornado maintienne sans effort dix mille connexions `epoll` concurrentes "
                    "en attente d'entrées-sorties, l'interpréteur standard CPython impose un verrou d'exclusion mutuelle "
                    "sur l'exécution du bytecode Python : le **GIL (*Global Interpreter Lock*)**. Un processus Tornado "
                    "unique ne peut donc saturer **qu'un seul cœur physique CPU** lors du parsing JSON ou du chiffrement "
                    "HMAC. Sur un serveur Linux doté de 4 ou 8 cœurs vCPU, la topologie officielle de production déploie "
                    "**une flotte de `N` processus Tornado indépendants** (un par cœur CPU, écoutant en boucle locale "
                    "`127.0.0.1:8001` à `800N`, supervisés par `systemd` ou Kubernetes) en aval d'un proxy inverse **Nginx**.\n\n"
                    "```text — Bloc amont Nginx de répartition vers un cluster de 4 processus Tornado\n"
                    "upstream isgp_tornado_cluster {\n"
                    "    least_conn;\n"
                    "    server 127.0.0.1:8001 max_fails=3 fail_timeout=10s;\n"
                    "    server 127.0.0.1:8002 max_fails=3 fail_timeout=10s;\n"
                    "    server 127.0.0.1:8003 max_fails=3 fail_timeout=10s;\n"
                    "    server 127.0.0.1:8004 max_fails=3 fail_timeout=10s;\n"
                    "    keepalive 64;\n"
                    "}\n"
                    "```\n\n"
                    "#### Rôle de Nginx en frontal et impératif de sécurité `xheaders=True`\n\n"
                    "Nginx assure en langage C natif la terminaison cryptographique **TLS 1.3**, l'amortissement des "
                    "clients lents (*Slowloris*), la diffusion directe des actifs statiques par appel noyau zéro-copie "
                    "(`sendfile on`) et l'injection des en-têtes `X-Real-IP`, `X-Forwarded-For` et `X-Forwarded-Proto`. "
                    "Côté Python, instancier **`HTTPServer(app, xheaders=True)`** instruit Tornado de substituer ces "
                    "en-têtes dans `self.request.remote_ip` et `self.request.protocol`.\n\n"
                    "> [!WARNING] Confinement réseau strict des ports internes Tornado (`127.0.0.1`)\n"
                    "> N'activez `xheaders=True` que lorsque vos processus Tornado écoutent exclusivement sur l'interface "
                    "privée `address=\"127.0.0.1\"` (ou un sous-réseau privé filtré n'acceptant que Nginx). Si le port "
                    "`8001` était directement joignable depuis Internet avec `xheaders=True`, n'importe quel attaquant "
                    "pourrait forger `X-Forwarded-For: 1.2.3.4` dans `curl` pour usurper son adresse IP et contourner "
                    "intégralement vos journaux d'audit et votre limiteur de débit !"
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE DE DÉPLOIEMENT DE PRODUCTION LINUX (NGINX + CLUSTER 4 INSTANCES TORNADO)\n"
            "=====================================================================================\n\n"
            "  Internet (HTTPS :443)\n"
            "        |\n"
            "        v\n"
            "  +-------------------------------------------------------------------+\n"
            "  | 1. NGINX (Reverse Proxy & Load Balancer)                          |\n"
            "  |    - Terminaison SSL/TLS + Fichiers /static/ (sendfile on)        |\n"
            "  |    - Injecte X-Real-IP, X-Forwarded-For, X-Forwarded-Proto        |\n"
            "  +-------------------------------------------------------------------+\n"
            "        |  (upstream isgp_tornado_cluster : ports 8001 à 8004)\n"
            "     +--+---------------+------------------+------------------+\n"
            "     |                  |                  |                  |\n"
            "     v                  v                  v                  v\n"
            "  [Node 1 :8001]     [Node 2 :8002]     [Node 3 :8003]     [Node 4 :8004]\n"
            "  HTTPServer         HTTPServer         HTTPServer         HTTPServer\n"
            "  (xheaders=True)    (xheaders=True)    (xheaders=True)    (xheaders=True)\n"
            "  IOLoop Cœur 1      IOLoop Cœur 2      IOLoop Cœur 3      IOLoop Cœur 4\n"
            "     \\                  |                  |                  /\n"
            "      +-----------------+------------------+-----------------+\n"
            "                                   |\n"
            "                                   v\n"
            "                    [ Base de Données SQL / Redis ]"
        ),
        "reference_table": {
            "title": "Comparatif : Instance Unique de Dev vs Cluster Tornado Production (`Nginx + 4 x HTTPServer`)",
            "headers": ["Critère d'Exploitation", "Serveur de Dev (`python app.py`)", "Cluster Production (`Nginx + 4 instances Tornado`)"],
            "rows": [
                ["Vocation", "Développement local et débogage sur le poste du développeur", "Production haute disponibilité exposée aux utilisateurs réels"],
                ["Parallélisme multi-cœurs", "Non (1 seul processus Python sur 1 cœur CPU)", "Oui (`N` processus Tornado indépendants dotés chacun de leur `IOLoop`)"],
                ["Restitution de l'IP cliente", "Directe (`127.0.0.1`)", "Automatique via `HTTPServer(app, xheaders=True)` lisant `X-Forwarded-For`"],
                ["Fichiers statiques (`/static/`)", "Servis par Python (`StaticFileHandler`)", "Servis directement par le noyau Linux via Nginx (`sendfile on`)"],
                ["Mode Debug (`debug=True`)", "Activé en local (`autoreload`)", "**Strictement `debug=False` en prod**"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Oublier `xheaders=True` sur `tornado.httpserver.HTTPServer` lorsque Tornado est placé derrière Nginx",
                "good": "Toujours instancier `tornado.httpserver.HTTPServer(app, xheaders=True)` derrière un Reverse Proxy de confiance",
                "why": "Sans `xheaders=True`, `self.request.remote_ip` vaut toujours `127.0.0.1` (l'IP de Nginx), ce qui fausse les logs d'audit et bloque tout le monde au même quota de Rate Limiting !"
            },
            {
                "bad": "N'écrire des tests automatisés que pour les cas de succès (`200 OK`)",
                "good": "Tester systématiquement les cas d'erreur (`400`, `401`, `403`, `404`, `422`) avec `AsyncHTTPTestCase`",
                "why": "Les régressions de sécurité et les crashs en production surviennent presque toujours sur les entrées invalides ou non autorisées."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_5/04_tests_et_production.py` pour lancer les six tests `AsyncHTTPTestCase` et observer comment `self.fetch(..., headers={\"X-Forwarded-For\": \"41.107.12.8\"})` valide le comportement exact de `xheaders=True`.",
            "Ajoutez une procédure d'arrêt gracieux (*Graceful Shutdown*) capturant `SIGTERM` : appelez `server.stop()` pour cesser d'accepter de nouvelles connexions Nginx, laissez `asyncio.sleep(2)` aux coroutines en vol pour achever leurs transactions SQL, puis arrêtez l'`IOLoop`."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.4 : DOCUMENTATION INTERACTIVE SWAGGER UI & CONTRAT OPENAPI 3.0
    # =========================================================================
    "d5-l4": {
        "context": (
            "Lorsque l'équipe Backend Python développe une API Tornado consommée simultanément par des équipes "
            "Mobiles (Swift/Kotlin), un portail Frontend (React/TypeScript) et des intégrateurs externes, la "
            "synchronisation documentaire devient rapidement le premier goulot d'étranglement organisationnel. Tout "
            "document statique rédigé sous Word, Confluence ou PDF diverge inévitablement du code réel dès la "
            "première semaine d'itération agile.\n\n"
            "L'industrie logicielle a éliminé cette dérive grâce à l'adoption universelle de la norme **OpenAPI "
            "Specification 3.0 (OAS)** couplée au portail d'exploration interactif **Swagger UI (`/api/docs`)**. "
            "Servi directement par deux `RequestHandlers` légers au sein même de votre application Tornado, ce "
            "contrat déclaratif unifie la lecture humaine, l'exécution de requêtes réelles authentifiées depuis le "
            "navigateur et la génération automatisée de code client."
        ),
        "deep_sections": [
            {
                "heading": "1. Généalogie et distinction rigoureuse : norme `OpenAPI Specification (OAS)` contre outillage `Swagger`",
                "body": (
                    "Dans les revues d'architecture comme en entretien d'ingénierie senior, employer indifféremment les "
                    "termes *OpenAPI* et *Swagger* trahit une approximation historique qu'il convient de dissiper.\n\n"
                    "#### De Swagger 2.0 à la gouvernance ouverte de la Linux Foundation (OAS 3.0 / 3.1)\n\n"
                    "Conçu en 2010 par Tony Tam puis acquis par SmartBear Software, le format s'appelait initialement "
                    "*Swagger Specification* (versions 1.2 puis 2.0). En novembre 2015, SmartBear a transféré la "
                    "propriété intellectuelle du standard à l'**OpenAPI Initiative**, consortium neutre hébergé par la "
                    "Linux Foundation réunissant Google, Microsoft, IBM et Stripe. Depuis la version 3.0, une séparation "
                    "stricte prévaut : **`OpenAPI` (`3.0.3` / `3.1.0`)** désigne exclusivement la **grammaire normative "
                    "ouverte** du fichier de contrat (`openapi.json` ou `openapi.yaml`), tandis que **`Swagger`** "
                    "désigne la **famille d'outils logiciels** exploitant cette grammaire — notamment **`Swagger UI`** "
                    "(le portail Web interactif), **`Swagger Editor`** (l'éditeur validant) et **`OpenAPI Generator`** "
                    "(le compilateur générant automatiquement les SDK clients et collections Postman)."
                )
            },
            {
                "heading": "2. Anatomie structurelle d'un graphe OpenAPI 3.0.3 : `paths` RFC 6570, pointeurs `$ref` et `securitySchemes`",
                "body": (
                    "Un document conforme à `openapi: \"3.0.3\"` modélise l'intégralité de la surface réseau d'une API "
                    "Tornado sous la forme d'un arbre déclaratif régi par JSON Schema.\n\n"
                    "#### Discordance syntaxique entre expressions régulières Tornado et gabarits d'URI OpenAPI (`{id}`)\n\n"
                    "Un point d'attention crucial concerne la notation des segments variables d'URL : alors que le "
                    "routeur interne de Tornado compile des groupes de capture PCRE tels que `r\"/api/v1/formations/([0-9]+)\"`, "
                    "la norme OpenAPI impose strictement les **gabarits d'URI RFC 6570 entre accolades** "
                    "(`\"/api/v1/formations/{id}\"`), reliés à une entrée `{\"name\": \"id\", \"in\": \"path\", "
                    "\"required\": true, \"schema\": {\"type\": \"integer\"}}`. Inscrire une regex Python brute dans "
                    "`paths` briserait le formulaire de saisie interactif *Try it out* de Swagger UI.\n\n"
                    "#### Factorisation DRY par `$ref` et activation du coffre `Authorize` (`securitySchemes`)\n\n"
                    "Plutôt que de dupliquer trente fois la définition des champs d'une ressource `Formation` ou d'une "
                    "enveloppe d'erreur `ProblemDetails` RFC 7807, on les centralise dans `components.schemas` et on les "
                    "référence par pointeur JSON `{\"$ref\": \"#/components/schemas/Formation\"}`. Parallèlement, la "
                    "section `components.securitySchemes` déclare vos protocoles d'authentification (`http` `bearer` JWT "
                    "ou `apiKey` dans `X-API-Key`), ce qui matérialise automatiquement le bouton cadenas **« Authorize »** "
                    "dans Swagger UI et injecte l'en-tête cryptographique sur tous les essais interactifs.\n\n"
                    "```json — Extrait canonique components.securitySchemes dans openapi.json\n"
                    "{\n"
                    "  \"components\": {\n"
                    "    \"securitySchemes\": {\n"
                    "      \"BearerAuth\": {\"type\": \"http\", \"scheme\": \"bearer\", \"bearerFormat\": \"JWT\"},\n"
                    "      \"ApiKeyAuth\": {\"type\": \"apiKey\", \"in\": \"header\", \"name\": \"X-API-Key\"}\n"
                    "    }\n"
                    "  }\n"
                    "}\n"
                    "```"
                )
            },
            {
                "heading": "3. Intégration zéro-dépendance dans Tornado : le tandem `OpenAPISpecHandler` et `SwaggerUIHandler`",
                "body": (
                    "Contrairement aux frameworks lourds nécessitant des plugins opaques souvent incompatibles avec les "
                    "mises à jour majeures de Python, la philosophie minimaliste et explicite de Tornado permet "
                    "d'embarquer un portail OpenAPI de grade industriel en moins de trente lignes de Python standard.\n\n"
                    "#### Architecture à deux endpoints découplés (`/api/openapi.json` et `/api/docs`)\n\n"
                    "Le premier gestionnaire, `OpenAPISpecHandler`, expose le dictionnaire Python (ou le fichier YAML "
                    "validé au démarrage) sur `GET /api/openapi.json` via `self.write(SPEC)`. Le second, `SwaggerUIHandler`, "
                    "sert sur `GET /api/docs` une page HTML5 épurée instanciant `SwaggerUIBundle({url: '/api/openapi.json'})`. "
                    "Cette approche *Contract-First* garantit un contrôle chirurgical sur chaque exemple, chaque code "
                    "d'erreur et chaque en-tête documenté, sans aucune surcharge d'introspection au fil de l'`IOLoop`.\n\n"
                    "> [!IMPORTANT] Gouvernance d'exposition de `/api/docs` en environnement de production\n"
                    "> Sur une API publique destinée à des développeurs tiers, exposer `/api/docs` publiquement est un "
                    "atout majeur d'adoption. En revanche, sur une API interne d'administration critique, l'exposition "
                    "anonyme de `/api/openapi.json` livre sur un plateau la cartographie complète de vos endpoints et "
                    "paramètres à un attaquant en phase de reconnaissance : restreignez alors `/api/docs` et "
                    "`/api/openapi.json` au réseau privé VPN ou protégez-les derrière un contrôle d'accès dans Nginx."
                )
            }
        ],
        "architecture_diagram": (
            "ÉCOSYSTÈME OPENAPI 3.0 : UN SEUL CONTRAT POUR TOUS LES OUTILS\n"
            "=============================================================\n\n"
            "                    +---------------------------------------+\n"
            "                    | Serveur Tornado (/api/openapi.json)   |\n"
            "                    | Contrat OpenAPI 3.0.3 (JSON/YAML)     |\n"
            "                    +-------------------+-------------------+\n"
            "                                        |\n"
            "         +------------------------------+-----------------------------+\n"
            "         |                              |                             |\n"
            "         v                              v                             v\n"
            "  +--------------+              +---------------+             +---------------+\n"
            "  |  SWAGGER UI  |              |  POSTMAN /    |             | OPENAPI       |\n"
            "  |  (/api/docs) |              |  INSOMNIA     |             | GENERATOR     |\n"
            "  |  Portail Web |              |  Import 1-clic|             | Génère les SDK|\n"
            "  |  Interactif  |              |  Collection   |             | Mobile & Web  |\n"
            "  +--------------+              +---------------+             +---------------+"
        ),
        "reference_table": {
            "title": "Structure de Référence d'un Document OpenAPI 3.0 (`openapi.json`)",
            "headers": ["Clé Racine OpenAPI 3.0", "Rôle dans le Contrat", "Exemple de Contenu", "Impact Visuel dans Swagger UI (`/api/docs`)"],
            "rows": [
                ["`openapi` & `info`", "Version de la norme et identité de l'API", "`\"openapi\": \"3.0.3\", \"info\": {\"title\": \"...\", \"version\": \"1.0.0\"}`", "Affiche l'en-tête principal, le badge de version et la description"],
                ["`servers`", "Liste des URLs de base cibles", "`[{\"url\": \"http://127.0.0.1:8888\"}]`", "Alimente la liste déroulante *Servers* pour choisir où envoyer les requêtes"],
                ["`paths`", "Catalogue des routes et méthodes HTTP", "`\"/api/v1/formations/{id}\": {\"get\": {...}}`", "Crée les bandeaux colorés dépliables (`GET` bleu, `POST` vert, `PUT` orange, `DELETE` rouge)"],
                ["`components.schemas`", "Modèles de données JSON réutilisables (`$ref`)", "`\"Formation\": {\"type\": \"object\", \"properties\": {...}}`", "Alimente la section *Schemas* en bas de page et pré-remplit les exemples *Try it out*"],
                ["`components.securitySchemes`", "Définition des mécanismes d'authentification", "`\"BearerAuth\": {\"type\": \"http\", \"scheme\": \"bearer\"}`", "Affiche le bouton cadenas vert **« Authorize »** en haut à droite et sur chaque route protégée"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écrire `/api/v1/formations/([0-9]+)` (syntaxe Regex Tornado) à l'intérieur du fichier `openapi.json`",
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
            "Ouvrez le portail Swagger UI du laboratoire (`/api/docs`), déverrouillez le coffre **« Authorize »** avec la clé `isgp-secret-2026` dans `ApiKeyAuth`, puis exécutez `GET /api/sandbox/admin-stats` via **« Try it out »** en observant la commande `curl` générée.",
            "Enrichissez `day_5/05_swagger_openapi_ui.py` en documentant l'opération `DELETE /api/v1/formations/{id}` assortie de la sécurité `BearerAuth` et des réponses référencées `204`, `401`, `403` et `404`."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.5 : INGÉNIERIE DE COLLECTION EN PRODUCTION (PAGINATION OFFSET VS CURSOR, FILTRAGE & TRI SÉCURISÉ)
    # =========================================================================
    "d5-l5": {
        "context": (
            "Sur une base d'essai contenant dix enregistrements, l'instruction naïve `SELECT * FROM inscriptions` "
            "s'exécute en moins d'une milliseconde. Deux ans après la mise en production, lorsque la même table "
            "totalise **cinq millions de lignes**, cette même requête déclenche une catastrophe en chaîne : le moteur "
            "SQL sature ses entrées-sorties disque, Python alloue plusieurs gigaoctets de dictionnaires en RAM et la "
            "sérialisation JSON monolithique fige l'`IOLoop` Tornado pendant plusieurs secondes, provoquant l'expiration "
            "en cascade de toutes les autres connexions actives.\n\n"
            "Ce chapitre de synthèse clôt le Volume III en réunissant les quatre techniques d'ingénierie de données "
            "indispensables aux collections à fort volume : la pagination classique bornée **`Offset / Limit`**, la "
            "pagination haute performance par **Curseur (`Keyset / Seek Pagination`) en temps constant `O(1)`** sur "
            "arbre B-Tree, le filtrage déclaratif multi-critères et le **tri dynamique blindé par liste blanche** "
            "contre toute injection SQL."
        ),
        "deep_sections": [
            {
                "heading": "1. Pagination `Offset / Limit` (`?page=2&per_page=20`) : plafonnement défensif et dérive `O(N)`",
                "body": (
                    "L'approche la plus familière pour découper une collection destinée à une grille d'administration "
                    "numérotée traduit le couple `(page, per_page)` en décalage arithmétique `offset = (page - 1) * per_page` "
                    "transmis à `LIMIT ? OFFSET ?`. Deux garde-fous logiciels sont ici impératifs : borner strictement "
                    "la taille de tranche demandée (`per_page = min(50, max(1, per_page_brut))`) afin qu'aucun client ne "
                    "puisse réclamer `?per_page=5000000`, et déporter l'exécution SQL sur un `ThreadPoolExecutor` via "
                    "`run_in_executor` (ou un pilote asynchrone natif `asyncpg`) pour préserver la fluidité de l'`IOLoop`.\n\n"
                    "#### Pourquoi `OFFSET` dégrade dramatiquement les performances à grande profondeur\n\n"
                    "Sur le plan physique du moteur relationnel (PostgreSQL, MySQL ou SQLite), une clause `OFFSET 500000 "
                    "LIMIT 20` n'effectue **aucun saut magique** : le planificateur SQL doit parcourir, matérialiser, "
                    "vérifier la visibilité transactionnelle MVCC et compter séquentiellement les **500 000 premières "
                    "lignes** uniquement pour les jeter avant de retourner les 20 suivantes ! Outre ce coût linéaire "
                    "`O(N)`, toute insertion concurrente en tête de table pendant qu'un utilisateur navigue de la page 1 "
                    "à la page 2 décale l'ensemble des indices d'un cran, faisant apparaître un doublon sur la page suivante.\n\n"
                    "> « OFFSET tells the database to skip the first N rows—yet the database still has to fetch and count "
                    "those N rows from disk or index before discarding them. » — Markus Winand, *SQL Performance Explained*"
                )
            },
            {
                "heading": "2. Pagination par Curseur (`Keyset / Seek Pagination`) : traversée d'index B-Tree en temps `O(1)`",
                "body": (
                    "Pour les flux continus mobiles, les historiques financiers et les synchronisations massives de "
                    "données, les architectures à très fort trafic (Stripe, GitHub, Slack) abandonnent `OFFSET` au "
                    "profit de la **Pagination par Curseur (*Keyset / Seek Method*)**. Au lieu d'un numéro de page "
                    "abstrait, le client transmet la clé d'ancrage du dernier enregistrement reçu : "
                    "`GET /api/v1/catalogue/cursor?after_id=1042&limit=20`.\n\n"
                    "```sql — Saut direct logarithmique/constant dans l'arbre B-Tree de la clé primaire\n"
                    "SELECT id, titre, domaine, duree_jours, tarif_dzd\n"
                    "FROM formations\n"
                    "WHERE id > ?\n"
                    "ORDER BY id ASC\n"
                    "LIMIT ?;\n"
                    "```\n\n"
                    "#### Astuce industrielle `LIMIT + 1` pour calculer `has_more` sans requête `COUNT(*)`\n\n"
                    "Grâce au prédicat `WHERE id > ? ORDER BY id ASC`, le moteur SQL descend directement les trois ou "
                    "quatre niveaux de l'index **B-Tree** de la clé primaire jusqu'au nœud `1043` et lit uniquement "
                    "20 feuilles contiguës : le temps de réponse demeure inférieur à la milliseconde (`O(log N)` de "
                    "descente B-Tree, soit pratiquement **`O(1)` constant** en latence), que vous lisiez le début ou le "
                    "cinquante-millionième élément ! De plus, en demandant `limit + 1` lignes à SQLite/PostgreSQL puis "
                    "en ne renvoyant que `lignes[:limit]`, vous déterminez instantanément s'il reste une page suivante "
                    "(`has_more = len(lignes) > limit`) sans jamais payer le coût prohibitif d'un `SELECT COUNT(*)` global."
                )
            },
            {
                "heading": "3. Filtrage dynamique composé et tri sécurisé par liste blanche (`CHAMPS_TRI_AUTORISES`)",
                "body": (
                    "Exposer le filtrage multi-critères (`?domaine=Securite&duree_min=3`) et le tri paramétrable "
                    "(`?sort=-tarif_dzd`) introduit une frontière critique de sécurité SQL que tout ingénieur backend "
                    "doit maîtriser sans hésitation.\n\n"
                    "#### Limite structurelle des marqueurs liés (`?`) face aux identifiants SQL (`ORDER BY`)\n\n"
                    "Dans le protocole de préparation des requêtes SQL (`sqlite3`, `psycopg`), les paramètres liés (`?` "
                    "ou `$1`) ne peuvent se substituer **qu'à des littéraux de valeurs** dans les prédicats `WHERE "
                    "domaine = ? AND duree_jours >= ?`. La grammaire SQL interdit qu'un marqueur lié représente un "
                    "**identifiant de colonne** ou le mot-clé directionnel **`ASC` / `DESC`** dans `ORDER BY`. Tenter "
                    "de contourner cette règle par interpolation directe `f\"ORDER BY {self.get_query_argument('sort')}\"` "
                    "ouvre instantanément une **injection SQL critique** (par exemple via `?sort=id;(SELECT ...)` ou des "
                    "exfiltrations booléennes dans `CASE WHEN`).\n\n"
                    "```python — Validation stricte par table de correspondance figée (Whitelist) dans Tornado\n"
                    "COLONNES_TRI_SURES = {\n"
                    "    \"id\": \"id\",\n"
                    "    \"duree_jours\": \"duree_jours\",\n"
                    "    \"tarif_dzd\": \"tarif_dzd\",\n"
                    "    \"titre\": \"titre\",\n"
                    "}\n\n"
                    "def resoudre_clause_tri(param_sort: str) -> str:\n"
                    "    direction = \"DESC\" if param_sort.startswith(\"-\") else \"ASC\"\n"
                    "    nom_public = param_sort.lstrip(\"+-\")\n"
                    "    colonne_sql = COLONNES_TRI_SURES.get(nom_public)\n"
                    "    if colonne_sql is None:\n"
                    "        raise ValueError(f\"Critere de tri non autorise : {nom_public}\")\n"
                    "    return f\"{colonne_sql} {direction}, id ASC\"\n"
                    "```\n\n"
                    "> [!IMPORTANT] Déterminisme total du tri par clé de départage (`Tie-Breaker`)\n"
                    "> Remarquez l'ajout systématique de `, id ASC` à la fin de `ORDER BY` : si trente formations "
                    "partagent exactement le même `tarif_dzd`, l'ordre relatif de ces ex-aequo en SQL n'est **pas "
                    "déterministe** d'une page à l'autre sans colonne de départage unique ! Adjoindre la clé primaire "
                    "`id` en critère secondaire garantit un ordre mathématiquement total et exempt de tout saut ou "
                    "doublon lors de la pagination."
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
                "good": "Toujours borner la limite : `per_page = min(50, max(1, int(self.get_query_argument('per_page', '20'))))`",
                "why": "Sans plafond `min(50, ...)`, un attaquant peut envoyer `?per_page=99999999` et provoquer un déni de service par saturation RAM."
            },
            {
                "bad": "Injecter directement le paramètre `?sort=` dans une requête SQL sans validation",
                "good": "Valider systématiquement la clé de tri contre un `set` Python (`CHAMPS_TRI_AUTORISES`) et renvoyer `422` en cas d'écart",
                "why": "C'est le seul moyen d'autoriser un tri dynamique tout en garantissant l'impossibilité absolue d'une injection SQL."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_5/02_pagination_filtrage_production.py` et parcourez la collection de proche en proche sur `/api/v1/catalogue/cursor` à l'aide de `next_cursor` en observant la technique `limit + 1` qui évite tout `SELECT COUNT(*)`.",
            "Implémentez la projection partielle de champs (*Sparse Fieldsets*, `?fields=id,titre,tarif_dzd`) validée contre une liste blanche de colonnes autorisées afin de réduire de 70 % le volume JSON transmis aux terminaux mobiles sur réseau cellulaire contraint."
        ]
    }
}
