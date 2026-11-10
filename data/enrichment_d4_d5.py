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
                    "Un jeton signé standard (comme un **JWT — JSON Web Token**, RFC 7519, ou un jeton signé `itsdangerous` dans l'écosystème Flask) "
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
                "heading": "3. Le protocole d'échange `Authorization: Bearer <token>` et la vérification d'expiration",
                "body": (
                    "Le standard HTTP (RFC 6750) définit la manière exacte dont le client présente son jeton à chaque requête :\n"
                    "- Le client ajoute l'en-tête HTTP : `Authorization: Bearer <jeton_signe>`.\n"
                    "- Le mot-clé `Bearer` signifie littéralement **« Au porteur »** : quiconque détient ce jeton valide est considéré comme authentifié "
                    "(d'où l'obligation absolue d'utiliser HTTPS en production pour empêcher l'écoute réseau).\n"
                    "- Côté Flask, la bibliothèque officielle `itsdangerous.URLSafeTimedSerializer` intègre nativement l'horodatage certifié lors du `dumps()`. "
                    "Lors de la vérification par `loads(jeton, max_age=3600)`, le serveur vérifie simultanément deux choses :\n"
                    "  1. La signature cryptographique est-elle intacte ? (Sinon -> `BadSignature`).\n"
                    "  2. L'âge du jeton est-il inférieur à `max_age` secondes ? (Sinon -> `SignatureExpired`)."
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
                "heading": "3. Implémentation d'un pipeline de sécurité multicouche dans Flask (`g.identite`)",
                "body": (
                    "Dans Flask, l'objet contextuel `flask.g` permet de stocker des données propres à la requête HTTP en cours :\n"
                    "- **Étape 1 (Middleware ou décorateur `@exiger_authn`)** : Extrait le jeton `Bearer`, vérifie la signature cryptographique "
                    "et stocke le Payload vérifié dans `g.identite`. En cas d'échec, coupe immédiatement le cycle avec `401 Unauthorized`.\n"
                    "- **Étape 2 (Vérification RBAC & Scopes)** : Vérifie que `g.identite[\"role\"]` appartient aux rôles autorisés et que le "
                    "scope requis figure dans `g.identite[\"scopes\"]`. En cas d'échec, renvoie `403 Forbidden` en précisant la permission manquante.\n"
                    "- **Étape 3 (Vérification métier Anti-BOLA dans la vue)** : Compare l'identifiant du demandeur (`g.identite[\"sub\"]`) avec "
                    "le champ `owner_id` de l'enregistrement chargé en base de données avant de retourner ou modifier la ressource."
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
                "heading": "3. Factoriser la sécurité avec une usine à décorateurs Python (`@exiger_role`) et `@wraps`",
                "body": (
                    "Copier-coller 25 lignes de lecture d'en-tête `Authorization`, de `try / except SignatureExpired` et de vérification de rôle "
                    "au début de chacune des 80 routes d'une API viole le principe **DRY (*Don't Repeat Yourself*)** et garantit des oublis.\n"
                    "- En Python, un **décorateur paramétré** `@exiger_role(\"admin\", \"formateur\")` est une fonction qui enveloppe la route Flask "
                    "et s'exécute automatiquement **avant** elle.\n"
                    "- **Détail critique propre à Flask (`@wraps(f)`)** : Flask identifie chaque route en interne par le nom de sa fonction Python "
                    "(`f.__name__`). Si votre décorateur retourne une fonction interne `wrapper` sans appliquer `@wraps(f)` du module `functools`, "
                    "toutes vos routes décorées s'appelleront `\"wrapper\"` et Flask lèvera une `AssertionError: View function mapping is overwriting "
                    "an existing endpoint function: wrapper` dès la deuxième route décorée !"
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
                "heading": "1. Comprendre `CORS` (*Cross-Origin Resource Sharing*) et la requête Preflight `OPTIONS`",
                "body": (
                    "Par défaut, tous les navigateurs Web (Chrome, Firefox, Safari) appliquent une règle de sécurité stricte appelée "
                    "**SOP (*Same-Origin Policy* / Politique de même origine)** : un script JavaScript exécuté sur le domaine "
                    "`https://portail.isgp.dz` n'a le droit de lire les réponses d'une API que si elle est hébergée sur la **même origine** "
                    "(même protocole + même domaine + même port).\n"
                    "- Si votre frontal React tourne sur `http://localhost:3000` (ou `https://app.isgp.dz`) et appelle votre API Flask sur "
                    "`http://localhost:5000` (ou `https://api.isgp.dz`), les origines diffèrent : le navigateur bloque la lecture de la réponse, "
                    "**sauf si le serveur Flask inclut explicitement les en-têtes `Access-Control-Allow-Origin`**.\n"
                    "- **Pourquoi `curl` et Postman ne sont jamais bloqués par CORS ?** Parce que CORS est une protection appliquée **exclusivement "
                    "par les navigateurs Web** pour protéger l'utilisateur final contre les sites malveillants.\n"
                    "- **La requête de pré-vérification (`Preflight OPTIONS`)** : Avant d'envoyer une requête `POST`, `PUT`, `DELETE` ou contenant "
                    "`Content-Type: application/json` ou `Authorization`, le navigateur envoie automatiquement une requête silencieuse "
                    "`OPTIONS` pour demander la permission au serveur."
                )
            },
            {
                "heading": "2. Architecture inversée (`Webhooks`) et signature `HMAC-SHA256` sur octets bruts (`request.get_data()`)",
                "body": (
                    "Au lieu que votre serveur interroge une API externe toutes les 5 secondes pour savoir si un étudiant a payé ses frais "
                    "d'inscription (*Polling* inefficace), le prestataire de paiement envoie lui-même une requête `POST /api/webhooks/paiement` "
                    "à votre serveur dès que la transaction aboutit : c'est un **Webhook** (un rappel HTTP serveur-à-serveur).\n"
                    "- **Le risque** : L'URL `/api/webhooks/paiement` étant accessible sur Internet, n'importe qui pourrait envoyer "
                    "`{\"evenement\": \"paiement.reussi\", \"montant\": 50000}` avec `curl` pour valider frauduleusement sa commande.\n"
                    "- **La parade industrielle (`X-Webhook-Signature`)** : Vous partagez un secret unique (`WEBHOOK_SECRET`) avec le prestataire. "
                    "Avant d'envoyer le JSON, le prestataire calcule le `HMAC-SHA256` des **octets bruts exacts** du corps HTTP avec ce secret et "
                    "l'inscrit dans l'en-tête `X-Webhook-Signature`.\n"
                    "- **Règle d'or en Flask** : Vous devez calculer le HMAC sur **`request.get_data()`** (les octets bruts tels qu'ils ont circulé "
                    "sur le réseau) et **JAMAIS** sur `json.dumps(request.get_json())` (car le re-formatage JSON modifierait les espaces ou l'ordre "
                    "des clés et invaliderait la signature)."
                )
            },
            {
                "heading": "3. Protection de la mémoire vive avec `MAX_CONTENT_LENGTH` (`413 Payload Too Large`)",
                "body": (
                    "Lorsque Flask exécute `request.get_json()`, il charge l'intégralité du corps de la requête en mémoire RAM pour le parser.\n"
                    "- Sans limite configurée, un attaquant peut envoyer en une seule requête `POST` un flux de 1,5 Go de texte JSON, provoquant "
                    "un crash immédiat du processus serveur par épuisement mémoire (*Out-Of-Memory Killer* Linux).\n"
                    "- En configurant `app.config[\"MAX_CONTENT_LENGTH\"] = 1 * 1024 * 1024` (ex: 1 Mo pour une API JSON pure), Werkzeug/Flask "
                    "vérifie l'en-tête `Content-Length` et interrompt immédiatement la lecture du flux réseau en renvoyant **`413 Payload Too Large`** "
                    "avant même que la mémoire ne soit saturée."
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
    # JOUR 5 — CHAPITRE 5.1 : CONSOMMER UNE API TIERCE (CLIENT HTTP RÉSILIENT, TIMEOUTS & RETRIES)
    # =========================================================================
    "d5-l1": {
        "context": (
            "Jusqu'ici, votre serveur Flask répondait directement aux clients à partir de ses propres données. "
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
            "Deux questions fondamentales se posent dès qu'une API dépasse le stade du prototype :\n"
            "1. **Comment organiser 150 routes en Python sans transformer `app.py` en un fichier illisible de 6 000 lignes** sujet "
            "aux conflits Git et aux erreurs d'importations circulaires (`ImportError: cannot import name 'app'`) ?\n"
            "2. **Pourquoi voit-on presque toujours `/api/v1/...` dans les APIs mondiales (OpenAI `/v1/`, Stripe `/v1/`, Kubernetes `/v1`) "
            "et si rarement `/api/v2/...` ?** Et si `v2` est si rare, pourquoi est-il pourtant obligatoire de préfixer ses routes par `/api/v1` "
            "dès le premier jour ?\n"
            "Ce chapitre répond en profondeur à ces deux questions d'architecture industrielle à travers les **`Blueprints` Flask**, "
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
                "heading": "2. Comment faire coexister `/api/v1` et `/api/v2` dans Flask et déprécier `v1` (Norme RFC 8594)",
                "body": (
                    "Lorsqu'une version `/api/v2` est créée, on ne coupe **jamais** `/api/v1` brutalement : on ouvre une **période de coexistence et de transition** "
                    "(généralement 6 à 12 mois) :\n"
                    "1. **Deux Blueprints sur la même couche métier** : Dans Flask, `formations_v1_bp` (`url_prefix=\"/api/v1/formations\"`) et `formations_v2_bp` "
                    "(`url_prefix=\"/api/v2/formations\"`) interrogent exactement la même base SQLite/PostgreSQL mais formatent le dictionnaire JSON différemment.\n"
                    "2. **Signalement automatique de fin de vie via `@formations_v1_bp.after_request` (RFC 8594)** : Chaque réponse de `/api/v1` inclut "
                    "trois en-têtes HTTP standards inspectés par les outils de supervision et les passerelles d'API :\n"
                    "   - `Deprecation: true` : Signale officiellement que cette version de l'API est en fin de vie.\n"
                    "   - `Sunset: Thu, 31 Dec 2026 23:59:59 GMT` : Indique la date et l'heure exactes d'extinction définitive.\n"
                    "   - `Link: </api/v2/formations>; rel=\"successor-version\"` : Indique l'URL de la nouvelle version.\n"
                    "3. **Extinction finale (`410 Gone`)** : Une fois la date `Sunset` dépassée et le trafic `v1` tombé à 0 % dans les logs Nginx, "
                    "`/api/v1` renvoie le code HTTP **`410 Gone`** (Ressource définitivement retirée) avec un message pointant vers `/api/v2`."
                )
            },
            {
                "heading": "3. Découpage modulaire (`Blueprint`), *Application Factory* (`create_app`) & Sondes (`Liveness`/`Readiness`)",
                "body": (
                    "Au-delà du versioning, l'industrialisation d'une application Flask repose sur trois piliers :\n"
                    "- **Les `Blueprints` par domaine** : Chaque module (`web_bp`, `formations_v1_bp`, `formations_v2_bp`, `sante_bp`) encapsule ses routes, "
                    "ses templates Jinja2 et ses middlewares sans dépendre d'une variable `app` globale.\n"
                    "- **L'Application Factory (`def create_app(config=None):`)** : Instancie `Flask(__name__)` et appelle `app.register_blueprint(...)`. "
                    "Supprime tout risque d'importation circulaire et permet à `pytest` ou `gunicorn \"app:create_app()\"` de créer des instances à la demande.\n"
                    "- **Les Sondes de Santé (*Healthchecks*)** :\n"
                    "  - `GET /api/health/live` (*Liveness Probe*) : Vérifie uniquement que le processus Python répond (`200 OK`).\n"
                    "  - `GET /api/health/ready` (*Readiness Probe*) : Vérifie que la base de données SQL répond (`200 OK` ou `503 Service Unavailable`)."
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
            "Comment une équipe d'ingénieurs peut-elle déployer une mise à jour de son API le jeudi après-midi "
            "avec la certitude absolue qu'elle n'a cassé aucune des 120 routes existantes ?\n"
            "Tester manuellement chaque route avec `curl` ou Postman après chaque modification de code devient "
            "humainement impossible dès la deuxième semaine d'un projet. Par ailleurs, comment les équipes mobiles "
            "et partenaires découvrent-elles les contrats exacts de vos routes ? Et enfin, pourquoi Flask affiche-t-il "
            "au démarrage l'avertissement rouge : **`WARNING: This is a development server. Do not use it in a production deployment`** ?\n"
            "Ce chapitre réunit les trois piliers de l'industrialisation : **Tests automatisés (`test_client`)**, "
            "**Spécification OpenAPI 3.0 (Swagger)** et **Architecture de déploiement WSGI (`Nginx + Gunicorn`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Tests d'intégration automatisés ultra-rapides avec `app.test_client()`",
                "body": (
                    "Flask intègre nativement un client de test WSGI simulé en mémoire vive accessible via **`client = app.test_client()`** :\n"
                    "- **Zéro serveur réseau à démarrer** : `client.get(\"/api/formations\")` ou `client.post(\"/api/formations\", json={...}, headers={...})` "
                    "construit un environnement WSGI complet en mémoire RAM, traverse tous vos décorateurs, routes et bases de données, "
                    "et retourne l'objet `response` en moins d'une milliseconde.\n"
                    "- **Les 3 assertions indispensables d'un test d'API** :\n"
                    "  1. Vérifier le **code de statut HTTP** : `assert resp.status_code == 201`.\n"
                    "  2. Vérifier les **en-têtes HTTP** : `assert resp.headers[\"Content-Type\"] == \"application/json\"`.\n"
                    "  3. Vérifier la **structure et les valeurs du corps JSON** : `data = resp.get_json(); assert data[\"id\"] > 0`.\n"
                    "- **Règle d'or de qualité logicielle** : Pour chaque route, écrivez au minimum un test du **cas nominal (*Happy Path*)** "
                    "et des tests pour les **cas d'erreur (*Unhappy Paths* : `400`, `401`, `403`, `404`, `422`)**."
                )
            },
            {
                "heading": "2. Le contrat universel `OpenAPI 3.0` (anciennement Swagger) sur `/api/openapi.json`",
                "body": (
                    "Une API sans documentation à jour est une API inutilisable. Le standard mondial pour décrire formellement "
                    "une API REST est la **spécification OpenAPI 3.0 (OAS)** :\n"
                    "- Il s'agit d'un document structuré (en JSON ou YAML), généralement exposé sur `GET /api/openapi.json`, qui décrit "
                    "de manière lisible à la fois par l'humain et par la machine :\n"
                    "  - Les métadonnées de l'API (`info.title`, `info.version`).\n"
                    "  - La liste exhaustive des chemins (`paths`) et méthodes HTTP (`get`, `post`, `delete`).\n"
                    "  - Les paramètres attendus (`parameters`), les schémas des corps JSON (`requestBody`) et des réponses (`responses`).\n"
                    "  - Les schémas de sécurité (`components.securitySchemes`, ex: `bearerAuth`).\n"
                    "- **Bénéfice industriel** : À partir de cet unique fichier `/api/openapi.json`, des outils standards génèrent "
                    "automatiquement un portail interactif (**Swagger UI / Redoc**), une collection Postman prête à l'emploi, ou même "
                    "le code client TypeScript/Kotlin pour les applications mobiles !"
                )
            },
            {
                "heading": "3. Pourquoi `app.run()` est interdit en production : L'architecture `Nginx -> Gunicorn (WSGI) -> Flask`",
                "body": (
                    "Le serveur inclus dans `app.run()` (fourni par Werkzeug) est conçu uniquement pour le confort du développeur sur son poste : "
                    "il recharge le code à chaque sauvegarde, mais il est **lent, vulnérable aux attaques réseau lentes (*Slowloris*) et "
                    "incapable de gérer une forte concurrence**.\n"
                    "En production sur Linux (VM, Docker ou Cloud), une API Python/Flask se déploie selon une architecture à **3 étages** :\n"
                    "1. **Étage 1 — Le Proxy Inverse (`Nginx`, `Caddy`, `Traefik` ou Load Balancer Cloud)** : Placé en première ligne sur les ports "
                    "`80` et `443`, il gère le chiffrement **HTTPS/TLS**, absorbe les connexions clientes lentes, sert les fichiers statiques "
                    "et transmet les requêtes propres via un socket local vers Gunicorn.\n"
                    "2. **Étage 2 — Le Serveur d'Application WSGI (`Gunicorn` ou `uWSGI`)** : C'est le chef d'orchestre Python. Il démarre un "
                    "processus maître (*Master Process*) qui génère plusieurs **processus travailleurs (*Workers*)** en parallèle "
                    "(formule classique : `2 * nombre_coeurs_CPU + 1`, soit 5 workers sur un serveur 2 cœurs). Si un worker plante ou met trop "
                    "de temps, le Master Gunicorn le tue et le recrée instantanément.\n"
                    "3. **Étage 3 — Votre Application Flask (`create_app()`)** : S'exécute à l'intérieur de chaque worker Gunicorn via le protocole "
                    "standard **WSGI (*Web Server Gateway Interface*, PEP 3333)**."
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
            "Dans une entreprise où l'équipe Backend Python développe une API consommée par une équipe Mobile (iOS/Android), "
            "une équipe Frontend (React/Vue) et des partenaires externes, comment communiquer la liste des URLs, les types "
            "de chaque champ JSON et les jetons requis ?\n"
            "Si vous rédigez un document Word ou un fichier PDF, **il devient obsolète dès la semaine suivante** dès qu'un "
            "développeur ajoute ou modifie un champ dans `app.py`.\n"
            "L'industrie mondiale a résolu ce problème grâce au standard **OpenAPI 3.0 (anciennement Swagger)** couplé au "
            "portail Web interactif **Swagger UI (`/api/docs`)** : un contrat unique, lisible à la fois par les machines "
            "et par les humains, permettant de tester chaque route en direct depuis le navigateur."
        ),
        "deep_sections": [
            {
                "heading": "1. Histoire et distinction exacte : `OpenAPI Specification (OAS)` vs `Swagger`",
                "body": (
                    "En entretien comme en réunion d'architecture, il est essentiel de connaître la distinction exacte entre ces deux termes :\n"
                    "- **2010–2015 (*Swagger 1.0 et 2.0*)** : Créé initialement par Tony Tam chez Wordnik puis racheté par SmartBear.\n"
                    "- **Novembre 2015 (Création de l'*OpenAPI Initiative*)** : SmartBear fait don de la spécification à la **Linux Foundation** "
                    "(avec Google, Microsoft, IBM, Stripe). La norme s'appelle désormais officiellement **OpenAPI Specification (OAS 3.0 / 3.1)**.\n"
                    "- **Aujourd'hui** :\n"
                    "  - **`OpenAPI 3.0`** désigne la **règle / la grammaire standard** du fichier de contrat (`openapi.json` ou `openapi.yaml`).\n"
                    "  - **`Swagger`** désigne la **boîte à outils** qui manipule ce fichier :\n"
                    "    1. **`Swagger UI`** : L'application Web HTML/JS qui lit `/api/openapi.json` et génère le portail interactif avec les boutons *« Try it out »* et *« Authorize »*.\n"
                    "    2. **`Swagger Editor`** : L'éditeur avec validation syntaxique en temps réel.\n"
                    "    3. **`Swagger Codegen` / `OpenAPI Generator`** : L'outil qui génère automatiquement le code client (Python, TypeScript, Kotlin, Swift) ou une collection Postman à partir de `openapi.json`."
                )
            },
            {
                "heading": "2. Anatomie chirurgicale d'un contrat OpenAPI 3.0 (`paths`, `$ref`, `securitySchemes`)",
                "body": (
                    "Un document OpenAPI 3.0 (`openapi: \"3.0.3\"`) s'articule autour de cinq sections maîtresses :\n"
                    "1. **`info` & `servers`** : Identifient le titre de l'API, sa version sémantique (`1.0.0`) et les URLs des environnements (Local, Staging, Production).\n"
                    "2. **`paths` (Les routes avec syntaxe `{variable}`)** : Contrairement à Flask qui utilise `<int:id>` et Postman qui utilise `:id`, "
                    "**OpenAPI impose les accolades `{id}`** (`/api/v1/formations/{id}`). Chaque chemin détaille les méthodes (`get`, `post`, `put`, `delete`), "
                    "les `parameters` (`in: \"path\"`, `in: \"query\"`, `in: \"header\"`), le `requestBody` et toutes les `responses` (`200`, `201`, `401`, `403`, `422`).\n"
                    "3. **`components.schemas` et les pointeurs `$ref`** : Au lieu de réécrire 15 fois la structure d'une `Formation` ou d'une `ErreurRFC7807`, "
                    "on la définit une seule fois dans `components.schemas` et on la pointe partout avec `{\"$ref\": \"#/components/schemas/Formation\"}`.\n"
                    "4. **`components.securitySchemes` (Le bouton cadenas *Authorize*)** : C'est cette section qui active le bouton **« Authorize »** en haut à droite "
                    "de Swagger UI pour permettre de saisir un **`Bearer Token` JWT** (`type: \"http\", scheme: \"bearer\"`) ou une **`X-API-Key`** (`type: \"apiKey\", in: \"header\"`)."
                )
            },
            {
                "heading": "3. Comment intégrer Swagger UI dans Flask : Approche Native vs `Flasgger` / `Flask-Smorest`",
                "body": (
                    "Dans l'écosystème Flask, trois approches sont utilisées selon la taille du projet :\n"
                    "1. **Approche Native Explicite (`/api/openapi.json` + `swagger-ui-dist`)** : Comme démontré dans `day_5/05_swagger_openapi_ui.py` et sur "
                    "notre propre serveur (`/api/docs`), il suffit d'une route Flask renvoyant le JSON/YAML OpenAPI et d'une route HTML de 20 lignes "
                    "chargeant `SwaggerUIBundle`. **Avantage** : zéro dépendance externe complexe, compatibilité totale avec toutes les versions de Python.\n"
                    "2. **Extensions Flask dédiées (`Flask-Smorest`, `APIFlask`, `Flasgger`)** : Génèrent automatiquement `openapi.json` à partir de vos "
                    "décorateurs et schémas `Marshmallow` ou `Pydantic`.\n"
                    "3. **Approche *Contract-First* (Industrie bancaire & grands groupes)** : Le fichier `openapi.yaml` est écrit et validé **avant** toute "
                    "ligne de Python, puis versionné dans Git comme source de vérité unique."
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
    # JOUR 5 — CHAPITRE 5.5 : OUVERTURE ARCHITECTURALE : SYNCHRONE (FLASK/WSGI) VS ASYNCHRONE (FASTAPI/ASGI)
    # =========================================================================
    "d5-l5": {
        "context": (
            "Vous maîtrisez désormais l'intégralité du cycle de conception d'une API Web professionnelle avec **Flask** : "
            "protocole HTTP, architecture REST, persistance SQL atomique, authentification par jetons signés, autorisation "
            "RBAC/Scopes/Anti-BOLA, limitation de débit, consommation résiliente et déploiement WSGI.\n"
            "Une question légitime se pose à la sortie de ce bootcamp : **comment ces compétences se transposent-elles "
            "vers les autres frameworks de l'écosystème Python moderne, notamment `FastAPI` ou `Django REST Framework` ?**\n"
            "La bonne nouvelle est que **95% de ce que vous avez appris est universel** : les codes HTTP, les en-têtes, "
            "les transactions SQL, les jetons JWT/HMAC et les règles REST sont strictement identiques quel que soit le langage "
            "ou le framework. Ce chapitre final explique la différence architecturale entre le modèle **Synchrone (`WSGI` / Flask)** "
            "et le modèle **Asynchrone (`ASGI` / FastAPI + Pydantic)** afin que vous puissiez naviguer avec aisance dans les deux mondes."
        ),
        "deep_sections": [
            {
                "heading": "1. Le modèle Synchrone (`WSGI` — Flask, Django) vs le modèle Asynchrone (`ASGI` — FastAPI, Starlette)",
                "body": (
                    "La différence fondamentale entre Flask et FastAPI réside dans la manière dont le serveur gère **le temps d'attente "
                    "des entrées/sorties (`I/O` : attendre une réponse PostgreSQL, attendre une API externe ou un modèle IA)** :\n"
                    "- **Modèle Synchrone (`WSGI` — Flask + Gunicorn)** : Un worker traite une requête du début à la fin de manière séquentielle. "
                    "Si la requête interroge une API externe qui met 500 ms à répondre, le thread/worker attend patiemment pendant ces 500 ms "
                    "avant de passer à la requête suivante. Pour gérer 100 requêtes simultanées, on multiplie les processus et les threads.\n"
                    "- **Modèle Asynchrone (`ASGI` — FastAPI + Uvicorn, mots-clés `async def` et `await`)** : Repose sur une **boucle d'événements "
                    "(*Event Loop* `asyncio`)** inspirée de Node.js et Go. Lorsqu'une route rencontre une opération réseau lente (`await client.get(url)`), "
                    "le worker **ne bloque pas** : il met cette requête en pause et traite immédiatement des centaines d'autres requêtes entrantes "
                    "pendant que la carte réseau attend la réponse !"
                )
            },
            {
                "heading": "2. Validation déclarative par annotations de types Python (`Type Hints` & `Pydantic`)",
                "body": (
                    "Au Jour 2, nous avons écrit manuellement une fonction `valider_payload_formation(data)` pour vérifier que `code` est un `str`, "
                    "que `duree_jours` est un `int` entre 1 et 30, et renvoyer `422` en cas d'erreur.\n"
                    "- Les frameworks de nouvelle génération (ou Flask couplé à **Pydantic** / **Marshmallow**) exploitent les **annotations de types "
                    "natives de Python 3 (`Type Hints`)** : `duree_jours: int`.\n"
                    "- En déclarant une classe héritant de `BaseModel` (ou une `@dataclass` Python standard comme démontré dans le code de ce chapitre), "
                    "le schéma de données sert **simultanément** de :\n"
                    "  1. Validateur automatique des entrées JSON (générant l'erreur `422 Unprocessable Entity` avec le détail exact par champ).\n"
                    "  2. Sérialiseur des sorties JSON.\n"
                    "  3. Générateur automatique du schéma **OpenAPI 3.0 / Swagger UI** sans avoir à l'écrire à la main !"
                )
            },
            {
                "heading": "3. Guide de décision d'architecte : Quand choisir Flask vs FastAPI vs Django REST Framework ?",
                "body": (
                    "En tant qu'ingénieur ou architecte logiciel, le choix de l'outil dépend du profil technique de votre projet :\n"
                    "- **Choisissez `Flask` (`WSGI`)** lorsque : vous construisez un microservice métier clair, une API REST classique adossée à une "
                    "base SQL relationnelle, une application hybride (servant à la fois des pages HTML Jinja2 et une API JSON), ou lorsque votre équipe "
                    "privilégie la simplicité explicite sans la complexité de `async/await`.\n"
                    "- **Choisissez `FastAPI` (`ASGI`)** lorsque : votre API doit maintenir des milliers de connexions simultanées (WebSockets, "
                    "Server-Sent Events, streaming de réponses d'Intelligence Artificielle / LLM), agit comme un orchestrateur appelant de nombreuses "
                    "APIs externes en parallèle (`asyncio.gather`), ou exige une génération automatique stricte de contrats OpenAPI.\n"
                    "- **Choisissez `Django REST Framework (DRF)`** lorsque : vous développez un grand progiciel de gestion (ERP, back-office complet) "
                    "où l'interface d'administration prête à l'emploi de Django et son ORM intégré font gagner des mois de développement."
                )
            }
        ],
        "architecture_diagram": (
            "COMPARAISON D'EXÉCUTION : WORKER SYNCHRONE (WSGI) VS EVENT LOOP ASYNCHRONE (ASGI)\n"
            "=================================================================================\n\n"
            "  [A] MODÈLE SYNCHRONE WSGI (Flask) — 1 Thread traite 1 requête à la fois :\n"
            "  Temps ---> |--- Req A (CPU) ---|........ Attente Réseau/BDD A (200ms) ........|--- Fin A ---|--- Req B ...\n"
            "                                 (Le thread est bloqué en attente d'I/O)\n\n"
            "  [B] MODÈLE ASYNCHRONE ASGI (FastAPI / asyncio) — 1 Boucle d'événements :\n"
            "  Temps ---> |Req A|--> (await I/O A) |Req B|--> (await I/O B) |Req C|--> |Réponse A| |Réponse B|\n"
            "             (Pendant que le réseau travaille pour A, le CPU traite déjà B et C !)"
        ),
        "reference_table": {
            "title": "Panorama des Frameworks d'API Python : `Flask` vs `FastAPI` vs `Django REST Framework`",
            "headers": ["Critère d'Architecture", "Flask (`WSGI`)", "FastAPI (`ASGI`)", "Django REST Framework (`WSGI`/`ASGI`)"],
            "rows": [
                ["Protocole & Serveur de Prod", "WSGI (`Gunicorn` / `uWSGI`)", "ASGI (`Uvicorn` / `Gunicorn + UvicornWorker`)", "WSGI / ASGI (`Gunicorn` / `Uvicorn`)"],
                ["Philosophie", "Micro-framework minimaliste, explicite et très flexible", "Framework orienté API, validation par Type Hints et asynchrone", "Framework « Batteries-Included » (ORM, Admin, Auth inclus)"],
                ["Validation JSON & OpenAPI", "Manuelle ou via extensions (`Pydantic`, `Flask-Smorest`)", "Native et automatique via `Pydantic`", "Native via les `Serializers` DRF"],
                ["Cas d'usage de prédilection", "APIs métier REST, Microservices, Applications Web + API", "Haute concurrence I/O, Streaming IA/LLM, WebSockets, APIs pures", "Grands systèmes d'information avec Back-Office d'administration"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Appeler une fonction bloquante synchrone (`time.sleep(2)` ou `requests.get()`) à l'intérieur d'une route `async def`",
                "good": "Dans une route `async def`, utiliser exclusivement des bibliothèques asynchrones non-bloquantes (`await asyncio.sleep()`, `await httpx.AsyncClient().get()`)",
                "why": "Un appel bloquant dans une fonction `async def` fige la boucle d'événements (*Event Loop*) unique et bloque toutes les autres requêtes simultanées."
            },
            {
                "bad": "Croire que changer de framework oblige à réapprendre la conception d'API",
                "good": "Capitaliser sur les fondamentaux universels (HTTP, REST, codes `2xx`/`4xx`/`5xx`, SQL ACID, JWT/HMAC, RBAC/Anti-BOLA)",
                "why": "95 % de l'ingénierie des APIs repose sur les protocoles standards du Web, qui sont strictement identiques en Flask, FastAPI, Go, Java ou Node.js."
            }
        ],
        "practical_exercises": [
            "Comparez côte à côte la route `POST /api/v1/formations` écrite en Flask au Chapitre 5.3 et sa traduction FastAPI générée dans le code de ce chapitre : identifiez comment chaque étape (lecture JSON, validation `422`, statut `201`) est représentée dans les deux frameworks.",
            "Ajoutez un champ `prerequis: list[str]` au contrat `ContratFormationEntree` et mettez à jour la méthode `.valider()` pour vérifier que `prerequis` est bien une liste de chaînes non vides."
        ]
    }
}
