"""
Référentiel des Concepts Fondamentaux pour le Bootcamp ISGP :
Développement d'APIs et Services Web.
Chaque concept est expliqué sans aucun prérequis, avec une analogie fonctionnelle
et un exemple concret en Python / Flask.
"""

GLOSSARY_TERMS = [
    {
        "id": "curl_postman_httpie",
        "term": "curl, Postman, HTTPie & REST Client (.http)",
        "category": "Architecture Web",
        "level": "Fondamental",
        "short": "Outils de test et de diagnostic permettant de forger des requêtes HTTP (GET, POST, PUT, PATCH, DELETE, Headers) sans navigateur.",
        "analogy": "Un multimètre d'ingénieur réseau : là où un navigateur classique ne sait envoyer que des requêtes GET simples, curl et Postman permettent de contrôler chaque en-tête, chaque méthode et chaque octet JSON.",
        "explanation": "- **`curl`** : Outil en ligne de commande présent sur tous les serveurs (`-i` pour voir les Headers, `-v` pour le mode verbeux, `-X` pour la méthode, `-H` pour un Header, `-d` pour le corps JSON).\n- **Postman / Bruno / Insomnia** : Interfaces graphiques permettant de sauvegarder des Collections de requêtes.\n- **HTTPie (`http`) & REST Client (`.http`)** : Outils modernes en terminal ou intégrés à VS Code.",
        "code_example": 'curl -i -X POST "http://127.0.0.1:5000/api/sandbox/formations" \\\n  -H "Content-Type: application/json" \\\n  -H "X-API-Key: isgp-secret-2026" \\\n  -d \'{"titre": "API Flask", "duree_jours": 5}\''
    },
    {
        "id": "rate_limiting",
        "term": "Rate Limiting (Limitation de Débit & Code 429)",
        "category": "Sécurité & Architecture API",
        "level": "Cœur d'API",
        "short": "Mécanisme qui limite le nombre de requêtes qu'un client peut envoyer sur une période donnée (ex. 60 requêtes par minute).",
        "analogy": "Comme un distributeur bancaire qui autorise au maximum 3 essais ou un plafond de retrait par heure : si un programme envoie 10 000 demandes par seconde (par erreur ou par attaque), le guichet le bloque temporairement pour ne pas paralyser toute la banque.",
        "explanation": "Sans Rate Limiting, un seul script mal codé (une boucle `while True`) ou un pirate peut faire tomber votre serveur Flask. Le serveur compte les requêtes par adresse IP ou par clé API (Fenêtre Glissante ou Token Bucket). Quand le quota est dépassé, il renvoie le code officiel **`429 Too Many Requests`** accompagné des en-têtes `X-RateLimit-Remaining: 0` et `Retry-After`.",
        "code_example": '# Si le client dépasse 3 requêtes en 20 secondes :\nreturn jsonify({\n    "erreur": "Quota dépassé (Rate Limit)",\n    "reessayer_dans_secondes": 20\n}), 429'
    },
    {
        "id": "token_bearer",
        "term": "Token / Bearer Token & JWT (Jeton d'Accès Signé)",
        "category": "Sécurité & Architecture API",
        "level": "Cœur d'API",
        "short": "Un laissez-passer numérique temporaire et signé (HMAC), remis au client après connexion pour prouver son identité à chaque requête.",
        "analogy": "La carte magnétique d'une chambre d'hôtel : vous montrez votre pièce d'identité une seule fois à la réception (`/api/auth/token`), on vous remet une carte valable 24h (le Token). Ensuite, vous présentez simplement cette carte devant chaque porte (`Authorization: Bearer <token>`).",
        "explanation": "Attention : le contenu (`Payload`) d'un Token JWT ou `itsdangerous` est encodé en Base64 (lisible par tous), mais **signé mathématiquement** avec la `SECRET_KEY` du serveur (infalsifiable). N'y stockez jamais de mot de passe en clair !",
        "code_example": '# En-tête HTTP envoyé par le client :\n# Authorization: Bearer eyJhbGciOi...\n\nauth = request.headers.get("Authorization", "")\nif auth.startswith("Bearer "):\n    token = auth.split(" ")[1]'
    },
    {
        "id": "refresh_token_rbac",
        "term": "Authentification (AuthN / 401) vs Autorisation (AuthZ / 403, RBAC, Scopes & BOLA)",
        "category": "Sécurité & Architecture API",
        "level": "Cœur d'API",
        "short": "AuthN vérifie QUI vous êtes (échec = 401 Unauthorized) ; AuthZ vérifie QUELS sont vos droits sur la ressource (échec = 403 Forbidden).",
        "analogy": "Le passeport contrôlé à l'entrée de l'aéroport est l'Authentification (`AuthN` -> `401` si absent). La carte d'accès réservée aux pilotes pour entrer dans le cockpit est l'Autorisation (`AuthZ` -> `403` si vous êtes un simple passager).",
        "explanation": "- **Authentification (`AuthN`)** : Vérifie l'identité via `Bearer Token` ou `X-API-Key`.\n- **Autorisation (`AuthZ`)** : Trois niveaux complémentaires en API Management :\n  1. **RBAC** : Contrôle par rôle (`stagiaire` vs `admin`).\n  2. **Scopes OAuth2** : Permissions granulaires intégrées au jeton (`formations:read`, `audit:admin`).\n  3. **Propriété de l'objet (Anti-BOLA / OWASP API #1)** : Vérifier que l'enregistrement ciblé appartient bien à l'utilisateur authentifié (`dossier.proprietaire == user.sub`).",
        "code_example": 'if not token_valide:\n    return jsonify({"etape": "AuthN", "erreur": "Non authentifié"}), 401\nif user["role"] != "admin" or "audit:admin" not in user["scopes"]:\n    return jsonify({"etape": "AuthZ", "erreur": "Droits insuffisants"}), 403'
    },
    {
        "id": "secret_env",
        "term": "Secrets & Variables d'Environnement (.env / os.environ)",
        "category": "Sécurité & Architecture API",
        "level": "Cœur d'API",
        "short": "Pratique fondamentale consistant à stocker les mots de passe, clés de signature et clés d'API hors du code source Python.",
        "analogy": "Vous ne gravez jamais le code de votre coffre-fort sur la façade extérieure de votre maison. Vous le gardez dans une enveloppe scellée à l'intérieur du coffre de la direction (les variables d'environnement du serveur).",
        "explanation": "Règle d'or absolue : **on n'écrit jamais un secret en dur dans `app.py`** (car si vous partagez le code sur Git, tout le monde voit vos mots de passe). On stocke les secrets dans l'environnement du système et Python les lit avec `os.environ.get('API_SECRET_KEY')`.",
        "code_example": 'import os\n\n# Lecture sécurisée depuis l\'environnement du serveur :\nSECRET_KEY = os.environ.get("API_SECRET_KEY", "cle-dev-locale")'
    },
    {
        "id": "signature_hmac",
        "term": "Signature Cryptographique HMAC & Webhooks",
        "category": "Sécurité & Architecture API",
        "level": "Cœur d'API",
        "short": "Sceau mathématique calculé avec une clé secrète garantissant qu'un Token ou un Webhook entrant n'a pas été falsifié.",
        "analogy": "Le cachet de cire officiel d'un ministère sur un diplôme : tout le monde peut lire ce qui est écrit sur le diplôme, mais personne ne peut modifier son nom ou sa note sans briser le cachet, car seul le ministère possède le tampon officiel (`SECRET_KEY`).",
        "explanation": "Utilisé à la fois pour signer les Bearer Tokens et pour vérifier l'authenticité des **Webhooks** entrants (`X-Webhook-Signature: sha256=...`). La comparaison doit toujours utiliser `hmac.compare_digest(a, b)` pour contrer les attaques temporelles (*Timing Attacks*).",
        "code_example": 'import hmac, hashlib\nsig = hmac.new(SECRET.encode(), corps_brut, hashlib.sha256).hexdigest()\nest_valide = hmac.compare_digest(sig_recue, sig)'
    },
    {
        "id": "idempotence_put_patch",
        "term": "Idempotence, PUT vs PATCH & Idempotency-Key",
        "category": "Architecture Web",
        "level": "Cœur d'API",
        "short": "Propriété mathématique d'une opération qui produit le même état sur le serveur qu'elle soit exécutée 1 fois ou 10 fois.",
        "analogy": "Appuyer 5 fois sur le bouton d'appel d'un ascenseur au 3ème étage est **idempotent** (l'ascenseur vient une seule fois au 3ème). Appuyer 5 fois sur « Débiter 10 000 DZD » ne l'est pas !",
        "explanation": "- `GET`, `PUT` (remplacement intégral), `DELETE` sont **idempotents**.\n- `PATCH` effectue une modification partielle d'un ou plusieurs champs.\n- `POST` n'est **pas idempotent** par défaut : pour éviter les doublons de paiement en cas de coupure réseau, le client envoie un en-tête `Idempotency-Key: <uuid>`.",
        "code_example": '# En-tête envoyé sur un POST critique :\n# Idempotency-Key: tx-2026-0001\ncle = request.headers.get("Idempotency-Key")'
    },
    {
        "id": "pagination_filtering",
        "term": "Pagination (page/limit), Filtrage & Tri",
        "category": "Architecture Web",
        "level": "Fondamental",
        "short": "Découpage d'une grande collection en tranches via les paramètres d'URL `?page=1&limit=20&tri=duree_jours`.",
        "analogy": "Consulter un catalogue de 50 000 articles par pages de 20 résultats au lieu d'imprimer les 50 000 lignes d'un seul bloc.",
        "explanation": "Formule mathématique du découpage (Offset Pagination) :\n`offset = (page - 1) * limit`\nEn Python : `resultats[offset : offset + limit]`. En SQL : `LIMIT ? OFFSET ?`. L'API retourne une enveloppe contenant `meta` (`total_items`, `total_pages`, `has_next`) et `data`.",
        "code_example": 'page = max(1, request.args.get("page", 1, type=int))\nlimit = min(100, request.args.get("limit", 10, type=int))\noffset = (page - 1) * limit'
    },
    {
        "id": "middlewares_hooks",
        "term": "Middlewares (@before_request / @after_request) & X-Request-ID",
        "category": "Flask",
        "level": "Intermédiaire",
        "short": "Fonctions exécutées automatiquement avant et après chaque route pour la journalisation, le chronométrage et la corrélation.",
        "analogy": "Le portique de sécurité à l'entrée d'un bâtiment qui enregistre l'heure d'arrivée de chaque visiteur (`before_request`) et l'heure de sortie (`after_request`).",
        "explanation": "Permet d'attacher un identifiant unique `X-Request-ID` (UUID) dans le contexte `flask.g`, de mesurer la latence exacte en millisecondes (`X-Response-Time-Ms`) et d'injecter les en-têtes de sécurité ou CORS sans dupliquer de code.",
        "code_example": '@app.before_request\ndef debut():\n    g.start = time.perf_counter()\n\n@app.after_request\ndef fin(reponse):\n    reponse.headers["X-Response-Time-Ms"] = str(round((time.perf_counter()-g.start)*1000, 2))\n    return reponse'
    },
    {
        "id": "wsgi_blueprints",
        "term": "Blueprints, Application Factory & Serveur WSGI (Gunicorn)",
        "category": "Flask",
        "level": "Cœur d'API",
        "short": "Organisation modulaire d'une API Flask (`Blueprint`) et déploiement multi-processus en production (`Gunicorn`).",
        "analogy": "Les `Blueprints` sont les départements spécialisés d'une entreprise, et `Gunicorn` est l'équipe de guichetiers parallèles (Workers) remplaçant le guichet unique d'entraînement (`app.run()`).",
        "explanation": "- **`Blueprint`** : Découpe l'API en fichiers par domaine (`/api/v1/formations`, `/api/health`).\n- **`app.test_client()`** : Exécute des tests automatisés d'API en mémoire sans serveur réseau.\n- **`Gunicorn` (WSGI)** : Serveur de production lançant plusieurs workers Python parallèles derrière un Reverse Proxy Nginx.",
        "code_example": '# Commande de lancement en production (4 workers) :\n# gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"'
    },
    {
        "id": "apikey_vs_token",
        "term": "Clé API (X-API-Key) vs Jeton Bearer (Token)",
        "category": "Sécurité & Architecture API",
        "level": "Cœur d'API",
        "short": "La Clé API identifie une application/machine (longue durée), tandis que le Bearer Token identifie un utilisateur connecté (courte durée).",
        "analogy": "La **Clé API** est comme le badge d'accès permanent d'une société de livraison partenaire. Le **Bearer Token** est le ticket nominatif temporaire d'un visiteur valable uniquement pour la séance.",
        "explanation": "- **`X-API-Key`** : Chaîne secrète fixe donnée à un serveur partenaire pour appeler votre API.\n- **`Authorization: Bearer <token>`** : Jeton généré dynamiquement après un login (`/api/auth/token`), qui expire automatiquement et contient l'identité et le rôle de l'utilisateur.",
        "code_example": '# Cas 1 : Clé machine-à-machine\ncle = request.headers.get("X-API-Key")\n\n# Cas 2 : Jeton temporaire utilisateur\nauth = request.headers.get("Authorization") # "Bearer <token>"'
    },
    {
        "id": "variable",
        "term": "Variable (Python)",
        "category": "Bases Python",
        "level": "Débutant Absolu",
        "short": "Emplacement nommé dans la mémoire de l'ordinateur permettant de conserver une valeur typée.",
        "analogy": "Un dossier suspendu dans une armoire sur lequel vous collez une étiquette « Budget_2026 ». Vous pouvez consulter son contenu ou le mettre à jour à tout moment.",
        "explanation": "En programmation, on associe un nom (à gauche) à une valeur (à droite) avec l'opérateur d'affectation `=`. Les 4 types primitifs compatibles JSON sont `str`, `int`/`float`, `bool` (`True`/`False`) et `None`.",
        "code_example": 'nom_stagiaire = "Amine"\nage = 25\n# Utiliser nom_stagiaire renvoie désormais "Amine"'
    },
    {
        "id": "dictionnaire",
        "term": "Dictionnaire (dict)",
        "category": "Bases Python",
        "level": "Débutant Absolu",
        "short": "Structure de données Python associant des clés uniques à des valeurs (`{clé: valeur}`).",
        "analogy": "Une fiche signalétique structurée où chaque champ possède un intitulé précis (« Nom », « Prénom », « Ville ») associé à sa valeur.",
        "explanation": "Délimité par des accolades `{ }`. C'est la structure fondamentale pour le développement d'APIs en Python car un dictionnaire se convertit directement en objet JSON. Utilisez `.get('cle', defaut)` pour éviter `KeyError`.",
        "code_example": 'stagiaire = {\n    "nom": "Benali",\n    "prenom": "Sara",\n    "present": True\n}\nprint(stagiaire.get("prenom"))  # Affiche: Sara'
    },
    {
        "id": "liste",
        "term": "Liste (list)",
        "category": "Bases Python",
        "level": "Débutant Absolu",
        "short": "Collection ordonnée et modifiable d'éléments indexés à partir de 0.",
        "analogy": "Un registre numéroté ligne par ligne (en informatique, la première ligne porte toujours le numéro 0).",
        "explanation": "Délimitée par des crochets `[ ]`. Lorsqu'une API renvoie une collection d'enregistrements (ex. la liste des formations), elle renvoie généralement une liste contenant plusieurs dictionnaires.",
        "code_example": 'formations = ["Python", "API REST", "Flask"]\nprint(formations[0])  # Affiche le 1er élément : Python'
    },
    {
        "id": "fonction",
        "term": "Fonction (def) & Décorateur (@)",
        "category": "Bases Python",
        "level": "Débutant Absolu",
        "short": "Bloc d'instructions réutilisable prenant des paramètres en entrée et retournant un résultat via `return`.",
        "analogy": "Une unité de traitement : vous lui fournissez des matières premières (paramètres), elle applique une procédure interne, et restitue le produit fini (`return`).",
        "explanation": "Déclarée avec `def`. Un **décorateur (`@`)** est une fonction d'ordre supérieur qui enveloppe une autre fonction pour lui ajouter un comportement (routage `@app.route`, sécurité `@exiger_role`).",
        "code_example": '@app.route("/bonjour")\ndef dire_bonjour():\n    return jsonify({"message": "Service opérationnel"}), 200'
    },
    {
        "id": "api",
        "term": "API REST & Modèle de Maturité de Richardson",
        "category": "Architecture Web",
        "level": "Fondamental",
        "short": "Architecture normalisée où chaque URL identifie une ressource (nom au pluriel) manipulée par les verbes et statuts HTTP.",
        "analogy": "Un guichet de liaison standardisé : l'application cliente dépose un bordereau de demande normé (Requête HTTP) et reçoit un colis de données structuré (Réponse JSON) sans dépendre du langage interne du serveur.",
        "explanation": "Niveaux de Richardson :\n- Niveau 0 : 1 seule URL RPC/SOAP.\n- Niveau 1 : URLs distinctes par ressource (`/api/formations/1`).\n- Niveau 2 : Verbes HTTP (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) + Codes de statut précis (`200`, `201`, `401`, `403`, `422`, `429`).\n- Niveau 3 : HATEOAS (liens hypermédias).",
        "code_example": '# Anti-pattern RPC : POST /api/creerFormation\n# Standard REST    : POST /api/formations  -> 201 Created'
    },
    {
        "id": "status_code",
        "term": "Codes de Statut HTTP & RFC 7807 (Problem Details)",
        "category": "Architecture Web",
        "level": "Fondamental",
        "short": "Code numérique à 3 chiffres normalisé indiquant le résultat d'une requête, complété en cas d'erreur par un JSON RFC 7807.",
        "analogy": "Un code d'état standardisé sur un terminal bancaire : transaction acceptée (200), création validée (201), erreur de saisie (422), carte non reconnue (401), droits insuffisants (403), plafond dépassé (429).",
        "explanation": "Classification essentielle :\n- **2xx** : `200 OK`, `201 Created`, `204 No Content`\n- **4xx** : `400 Bad Request` (JSON cassé), `401 Unauthorized` (non authentifié), `403 Forbidden` (rôle insuffisant), `404 Not Found`, `405 Method Not Allowed`, `413 Payload Too Large`, `422 Unprocessable Entity` (validation métier échouée), `429 Too Many Requests` (Rate Limit)\n- **5xx** : `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout`",
        "code_example": 'return jsonify({\n    "type": "https://api.isgp.dz/erreurs/validation",\n    "title": "Erreur de validation",\n    "status": 422,\n    "errors": [{"champ": "duree_jours", "message": "Doit être >= 1"}]\n}), 422'
    },
    {
        "id": "sqlite",
        "term": "SQLite, Transactions ACID & Requêtes Paramétrées (?)",
        "category": "Données",
        "level": "Intermédiaire",
        "short": "Moteur de base de données relationnelle SQL transactionnel intégré à Python (`sqlite3`).",
        "analogy": "Un registre comptable permanent écrit sur disque dur, protégé par des transactions atomiques (tout réussit avec `commit` ou tout est annulé avec `rollback`).",
        "explanation": "Sécurité fondamentale : lors d'une requête SQL, on n'insère jamais une variable directement avec `+` ou `f\"...\"` (risque critique d'**Injection SQL**). On utilise toujours des marqueurs `?` (requêtes paramétrées).",
        "code_example": '# SÉCURISÉ (Requête paramétrée contre l\'injection SQL) :\nconn.execute("SELECT * FROM formations WHERE id = ?", (id,))'
    }
]
