"""
Référentiel des Concepts Fondamentaux pour le Bootcamp ISGP :
Développement d'APIs et Services Web.
Chaque concept est expliqué sans aucun prérequis, avec une analogie fonctionnelle
et un exemple concret en Python / Flask.
"""

GLOSSARY_TERMS = [
    {
        "id": "rate_limiting",
        "term": "Rate Limiting (Limitation de Débit & Code 429)",
        "category": "Sécurité & Architecture API",
        "level": "Cœur d'API",
        "short": "Mécanisme qui limite le nombre de requêtes qu'un client peut envoyer sur une période donnée (ex. 60 requêtes par minute).",
        "analogy": "Comme un distributeur bancaire qui autorise au maximum 3 essais ou un plafond de retrait par heure : si un programme envoie 10 000 demandes par seconde (par erreur ou par attaque), le guichet le bloque temporairement pour ne pas paralyser toute la banque.",
        "explanation": "Sans Rate Limiting, un seul script mal codé (une boucle `while True`) ou un pirate peut faire tomber votre serveur Flask. Le serveur compte les requêtes par adresse IP ou par clé API. Quand le quota est dépassé, il renvoie le code officiel **`429 Too Many Requests`** accompagné des en-têtes `X-RateLimit-Remaining: 0` et `Retry-After`.",
        "code_example": '# Si le client dépasse 5 requêtes en 60 secondes :\nreturn jsonify({\n    "erreur": "Quota dépassé (Rate Limit)",\n    "reessayer_dans_secondes": 20\n}), 429'
    },
    {
        "id": "token_bearer",
        "term": "Token / Bearer Token & JWT (Jeton d'Accès)",
        "category": "Sécurité & Architecture API",
        "level": "Cœur d'API",
        "short": "Un laissez-passer numérique temporaire et signé, remis au client après connexion pour prouver son identité à chaque requête.",
        "analogy": "La carte magnétique d'une chambre d'hôtel : vous montrez votre pièce d'identité une seule fois à la réception (`/api/auth/token`), on vous remet une carte valable 24h (le Token). Ensuite, vous présentez simplement cette carte devant chaque porte (`Authorization: Bearer <token>`).",
        "explanation": "Pourquoi ne pas envoyer son mot de passe à chaque requête ? Parce que ce serait risqué. À la place, le client s'identifie une fois, reçoit un **Token** signé par le secret du serveur avec une date d'expiration, et l'envoie dans l'en-tête HTTP `Authorization: Bearer <votre_token>`.",
        "code_example": '# En-tête HTTP envoyé par le client :\n# Authorization: Bearer eyJhbGciOi...\n\nauth = request.headers.get("Authorization", "")\nif auth.startswith("Bearer "):\n    token = auth.split(" ")[1]'
    },
    {
        "id": "secret_env",
        "term": "Secrets & Variables d'Environnement (.env / os.environ)",
        "category": "Sécurité & Architecture API",
        "level": "Cœur d'API",
        "short": "Pratique fondamentale consistant à stocker les mots de passe, clés de signature et clés d'API hors du code source Python.",
        "analogy": "Vous ne gravez jamais le code de votre coffre-fort sur la façade extérieure de votre maison. Vous le gardez dans une enveloppe scellée à l'intérieur du coffre de la direction (les variables d'environnement du serveur).",
        "explanation": "Règle d'or absolue : **on n'écrit jamais un secret en dur dans `app.py`** (car si vous partagez le code sur GitHub ou par e-mail, tout le monde voit vos mots de passe). On stocke les secrets dans le système ou un fichier `.env` non partagé, et Python les lit avec `os.environ.get('API_SECRET_KEY')`.",
        "code_example": 'import os\n\n# Lecture sécurisée depuis l\'environnement du serveur :\nSECRET_KEY = os.environ.get("API_SECRET_KEY", "cle-dev-locale")\n# Ne jamais écrire un vrai mot de passe de production dans le code !'
    },
    {
        "id": "signature_hmac",
        "term": "Signature Cryptographique & Intégrité (HMAC / Secret)",
        "category": "Sécurité & Architecture API",
        "level": "Cœur d'API",
        "short": "Sceau mathématique calculé avec la clé secrète du serveur qui garantit qu'un Token n'a pas été falsifié par le client.",
        "analogy": "Le cachet de cire officiel d'un ministère sur un diplôme : tout le monde peut lire ce qui est écrit sur le diplôme, mais personne ne peut modifier son nom ou sa note sans briser le cachet, car seul le ministère possède le tampon officiel (`SECRET_KEY`).",
        "explanation": "Dans un jeton signé (comme les tokens Flask `itsdangerous` ou `JWT`), les données (`utilisateur=amine`, `role=admin`) sont accompagnées d'une signature calculée avec `SECRET_KEY`. Si un pirate tente de remplacer `role=stagiaire` par `role=admin` dans son token, la signature ne correspond plus et Flask rejette immédiatement la requête (`401 Unauthorized`).",
        "code_example": 'from itsdangerous import URLSafeTimedSerializer\nsigner = URLSafeTimedSerializer(SECRET_KEY)\ntoken = signer.dumps({"user": "amine", "role": "stagiaire"})\n# Vérification (échoue si modifié ou expiré > 300s) :\ndata = signer.loads(token, max_age=300)'
    },
    {
        "id": "apikey_vs_token",
        "term": "Clé API (X-API-Key) vs Jeton Bearer (Token)",
        "category": "Sécurité & Architecture API",
        "level": "Cœur d'API",
        "short": "La Clé API identifie une application/machine (longue durée), tandis que le Bearer Token identifie un utilisateur connecté (courte durée).",
        "analogy": "La **Clé API** est comme le badge d'accès permanent d'une société de livraison partenaire. Le **Bearer Token** est le ticket nominatif temporaire d'un visiteur valable uniquement pour la journée.",
        "explanation": "- **`X-API-Key`** : Chaîne secrète fixe donnée à un serveur partenaire pour appeler votre API. Simple à utiliser.\n- **`Authorization: Bearer <token>`** : Jeton généré dynamiquement après un login (`/api/auth/token`), qui expire automatiquement (ex. après 15 minutes ou 1 heure) et contient l'identité de l'utilisateur.",
        "code_example": '# Cas 1 : Clé machine-à-machine\ncle = request.headers.get("X-API-Key")\n\n# Cas 2 : Jeton temporaire utilisateur\nauth = request.headers.get("Authorization") # "Bearer <token>"'
    },
    {
        "id": "variable",
        "term": "Variable (Python)",
        "category": "Bases Python",
        "level": "Débutant Absolu",
        "short": "Emplacement nommé dans la mémoire de l'ordinateur permettant de conserver une valeur.",
        "analogy": "Un dossier suspendu dans une armoire sur lequel vous collez une étiquette « Budget_2026 ». Vous pouvez consulter son contenu ou le mettre à jour à tout moment.",
        "explanation": "En programmation, on associe un nom (à gauche) à une valeur (à droite) avec l'opérateur d'affectation `=`. En Python, `=` signifie « stocker la valeur de droite dans la variable de gauche ».",
        "code_example": 'nom_stagiaire = "Amine"\nage = 25\n# Utiliser nom_stagiaire renvoie désormais "Amine"'
    },
    {
        "id": "dictionnaire",
        "term": "Dictionnaire (dict)",
        "category": "Bases Python",
        "level": "Débutant Absolu",
        "short": "Structure de données Python associant des clés uniques à des valeurs (`{clé: valeur}`).",
        "analogy": "Une fiche signalétique structurée où chaque champ possède un intitulé précis (« Nom », « Prénom », « Ville ») associé à sa valeur.",
        "explanation": "Délimité par des accolades `{ }`. C'est la structure fondamentale pour le développement d'APIs en Python car un dictionnaire se convertit directement en objet JSON pour être transmis sur le réseau.",
        "code_example": 'stagiaire = {\n    "nom": "Benali",\n    "prenom": "Sara",\n    "present": True\n}\nprint(stagiaire["prenom"])  # Affiche: Sara'
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
        "term": "Fonction (def)",
        "category": "Bases Python",
        "level": "Débutant Absolu",
        "short": "Bloc d'instructions réutilisable prenant des paramètres en entrée et retournant un résultat via `return`.",
        "analogy": "Une unité de traitement : vous lui fournissez des matières premières (paramètres), elle applique une procédure interne, et restitue le produit fini (`return`).",
        "explanation": "Déclarée avec le mot-clé `def` suivi du nom de la fonction, de parenthèses `()` et de deux-points `:`. Le bloc indenté (décalé de 4 espaces) constitue le corps de la fonction. Dans Flask, chaque route HTTP est rattachée à une fonction.",
        "code_example": 'def saluer(prenom):\n    message = "Bonjour " + prenom\n    return message\n\nresultat = saluer("Karim")  # renvoie "Bonjour Karim"'
    },
    {
        "id": "import",
        "term": "Import / Bibliothèque",
        "category": "Bases Python",
        "level": "Débutant Absolu",
        "short": "Instruction permettant de charger des modules externes ou standards dans un script Python.",
        "analogy": "Importer un équipement spécialisé déjà certifié plutôt que de le reconstruire intégralement à partir de zéro.",
        "explanation": "La syntaxe `from flask import Flask, jsonify, request` charge uniquement les composants nécessaires depuis le framework `flask` installé dans l'environnement virtuel.",
        "code_example": 'from flask import Flask, jsonify, request'
    },
    {
        "id": "decorateur",
        "term": "Décorateur (@app.route)",
        "category": "Flask",
        "level": "Fondamental",
        "short": "Instruction préfixée par `@` qui associe une URL HTTP ou un contrôle de sécurité à une fonction Python.",
        "analogy": "Une règle d'aiguillage placée au-dessus d'une porte de service : « Toute requête entrante adressée à `/api/produits` doit être traitée par la fonction ci-dessous ».",
        "explanation": "Dans Flask, `@app.route('/produits')` enregistre la fonction dans la table de routage du serveur. On utilise aussi des décorateurs pour protéger une route (`@token_requis` ou `@rate_limit`).",
        "code_example": '@app.route("/bonjour")\ndef dire_bonjour():\n    return "Service opérationnel"'
    },
    {
        "id": "api",
        "term": "API (Application Programming Interface)",
        "category": "Architecture Web",
        "level": "Débutant Absolu",
        "short": "Interface normalisée permettant à deux systèmes logiciels d'échanger des données et des traitements via le réseau.",
        "analogy": "Un guichet de liaison standardisé : l'application cliente dépose un bordereau de demande normé (Requête HTTP) et reçoit un colis de données structuré (Réponse JSON) sans dépendre du langage interne du serveur.",
        "explanation": "Contrairement à une page Web HTML destinée à l'affichage humain, une API expose des données structurées (JSON) exploitables simultanément par un frontal Web, une application mobile ou un système tiers.",
        "code_example": '# Site Web HTML : <h1>Météo : 24°C</h1>\n# API Web JSON  : {"ville": "Alger", "temperature": 24}'
    },
    {
        "id": "client_serveur",
        "term": "Architecture Client / Serveur",
        "category": "Architecture Web",
        "level": "Débutant Absolu",
        "short": "Modèle de communication réseau où le Client initie la requête et le Serveur écoute, traite et renvoie la réponse.",
        "analogy": "Un poste téléphonique d'accueil (le Serveur) qui reste en écoute permanente, et un interlocuteur externe (le Client) qui compose le numéro pour formuler une demande précise.",
        "explanation": "Le **Client** peut être un navigateur, une application mobile, l'outil `curl`, Postman ou un script Python. Le **Serveur** est votre application Flask en exécution continue.",
        "code_example": '# Client ---> Requête HTTP (Méthode + URL + Headers + Body) ---> Serveur Flask\n# Client <--- Réponse HTTP (Code Statut + Headers + JSON)   <--- Serveur Flask'
    },
    {
        "id": "http",
        "term": "Protocole HTTP / HTTPS",
        "category": "Architecture Web",
        "level": "Fondamental",
        "short": "Protocole standard de communication régissant le format des requêtes et des réponses sur le Web.",
        "analogy": "Le protocole postal international qui impose la présence d'un destinataire, d'un expéditeur et d'un format d'enveloppe normalisé pour acheminer un pli.",
        "explanation": "HTTP fonctionne selon un cycle strict Requête / Réponse sans état (stateless). HTTPS ajoute une couche de chiffrement TLS afin que les jetons (`Bearer Token`), clés API et données JSON ne puissent pas être interceptés en clair sur le réseau.",
        "code_example": 'GET /api/stagiaires HTTP/1.1\nHost: localhost:5000\nAuthorization: Bearer <token>'
    },
    {
        "id": "verbes_http",
        "term": "Méthodes (Verbes) HTTP",
        "category": "Architecture Web",
        "level": "Fondamental",
        "short": "Indicateur de l'action demandée sur la ressource ciblée : GET (Lecture), POST (Création), PUT (Modification), DELETE (Suppression).",
        "analogy": "Sur un même dossier administratif (`/dossiers/12`), l'action diffère selon l'instruction : consulter (`GET`), ouvrir un nouveau dossier (`POST`), mettre à jour (`PUT`) ou archiver/supprimer (`DELETE`).",
        "explanation": "Une même route URL (ex. `/api/formations`) peut répondre différemment selon la méthode HTTP utilisée :\n- `GET` : Lecture seule\n- `POST` : Création d'une ressource\n- `PUT` : Mise à jour d'une ressource\n- `DELETE` : Suppression d'une ressource",
        "code_example": '@app.route("/formations", methods=["GET", "POST"])'
    },
    {
        "id": "status_code",
        "term": "Codes de Statut HTTP (200, 401, 429, 500...)",
        "category": "Architecture Web",
        "level": "Fondamental",
        "short": "Code numérique à 3 chiffres normalisé indiquant immédiatement le résultat du traitement d'une requête HTTP.",
        "analogy": "Un code d'état standardisé sur un terminal bancaire : transaction acceptée (200), carte non reconnue (401), plafond dépassé (429), incident technique (500).",
        "explanation": "Classification officielle :\n- **2xx (Succès)** : `200 OK` (succès), `201 Created` (ressource créée)\n- **4xx (Erreur côté Client)** : `400 Bad Request` (données invalides), `401 Unauthorized` (jeton/clé manquant ou invalide), `403 Forbidden` (droits insuffisants), `404 Not Found` (introuvable), **`429 Too Many Requests` (Rate Limit dépassé)**\n- **5xx (Erreur côté Serveur)** : `500 Internal Server Error` (exception non gérée dans le code Python)",
        "code_example": 'return jsonify({"erreur": "Quota de requêtes dépassé"}), 429'
    },
    {
        "id": "json",
        "term": "JSON (JavaScript Object Notation)",
        "category": "Données",
        "level": "Fondamental",
        "short": "Format textuel léger et standardisé d'échange de données structurées entre systèmes hétérogènes.",
        "analogy": "Un conteneur maritime standardisé (ISO) : qu'il soit chargé par un camion Python, transporté par un navire HTTP et déchargé par une grue Java ou JavaScript, ses dimensions sont comprises par tous.",
        "explanation": "Syntaxiquement très proche du dictionnaire Python, avec trois règles strictes : les clés et chaînes utilisent exclusivement des guillemets doubles `\" \"`, les booléens s'écrivent en minuscules (`true`/`false`), et la valeur nulle s'écrit `null`.",
        "code_example": '{\n  "organisme": "ISGP",\n  "duree_jours": 5,\n  "actif": true,\n  "modules": ["HTTP", "Flask", "Sécurité"]\n}'
    },
    {
        "id": "ip_localhost",
        "term": "Adresse IP & Localhost (127.0.0.1)",
        "category": "Réseau",
        "level": "Débutant Absolu",
        "short": "Identifiant numérique d'une machine sur un réseau IP. `127.0.0.1` (`localhost`) désigne la machine locale elle-même.",
        "analogy": "L'adresse IP correspond aux coordonnées postales du bâtiment. `127.0.0.1` correspond au circuit interne permettant de tester un équipement sans sortir du bâtiment.",
        "explanation": "En développement local, Flask écoute sur `http://127.0.0.1:5000`. L'option `host='0.0.0.0'` autorise les connexions entrantes depuis les autres postes du réseau local.",
        "code_example": 'if __name__ == "__main__":\n    app.run(host="0.0.0.0", port=5000, debug=True)'
    },
    {
        "id": "port",
        "term": "Port Réseau (ex. :5000)",
        "category": "Réseau",
        "level": "Débutant Absolu",
        "short": "Numéro logique (de 1 à 65535) permettant d'adresser un service logiciel précis sur une même machine.",
        "analogy": "Si l'adresse IP identifie l'immeuble, le numéro de Port identifie le numéro de bureau exact à l'intérieur de cet immeuble.",
        "explanation": "Plusieurs services réseau peuvent coexister sur un même serveur physique (ex. serveur Web sur le port 80/443, PostgreSQL sur 5432, application Flask sur 5000).",
        "code_example": '# Hôte : 127.0.0.1  |  Port : 5000\n# URL  : http://127.0.0.1:5000'
    },
    {
        "id": "headers_body",
        "term": "En-têtes (Headers) & Corps (Body) HTTP",
        "category": "Architecture Web",
        "level": "Fondamental",
        "short": "Les deux sections d'un message HTTP : les métadonnées de contrôle (Headers) et la charge utile applicative (Body).",
        "analogy": "Le bordereau de transport collé sur un pli recommandé (Headers : type de contenu, jeton d'autorisation, quotas Rate Limit) et le document contenu à l'intérieur (Body JSON).",
        "explanation": "Les en-têtes essentiels d'une API :\n- `Content-Type: application/json` (nature du corps envoyé)\n- `Authorization: Bearer <token>` (jeton d'authentification)\n- `X-API-Key: <cle>` (clé d'accès machine)\n- `X-RateLimit-Remaining: 42` (nombre de requêtes restantes autorisées)",
        "code_example": '# Lecture d\'un Header dans Flask :\ntoken = request.headers.get("Authorization")\n# Lecture du Body JSON :\ndonnees = request.get_json()'
    },
    {
        "id": "crud",
        "term": "CRUD (Create, Read, Update, Delete)",
        "category": "Architecture Web",
        "level": "Fondamental",
        "short": "Les quatre opérations élémentaires de gestion de données persistantes : Créer, Lire, Mettre à jour, Supprimer.",
        "analogy": "La gestion d'un registre officiel : immatriculer une entrée (Create), consulter une fiche (Read), rectifier une mention (Update), radier une entrée (Delete).",
        "explanation": "Correspondance directe avec les méthodes HTTP :\n- **C**reate → `POST`\n- **R**ead → `GET`\n- **U**pdate → `PUT`\n- **D**elete → `DELETE`",
        "code_example": '# POST   /api/formations\n# GET    /api/formations\n# PUT    /api/formations/1\n# DELETE /api/formations/1'
    },
    {
        "id": "sqlite",
        "term": "SQLite & Requêtes Paramétrées (?)",
        "category": "Données",
        "level": "Intermédiaire",
        "short": "Moteur de base de données relationnelle SQL stocké dans un fichier unique et intégré nativement à Python (`sqlite3`).",
        "analogy": "Un registre comptable permanent écrit sur disque dur, contrairement aux variables Python qui résident en mémoire vive (RAM) et disparaissent à l'arrêt du processus.",
        "explanation": "Sécurité fondamentale : lors d'une requête SQL, on n'insère jamais une variable directement avec `+` ou `f\"...\"` (risque d'**Injection SQL**). On utilise toujours des marqueurs `?` (requêtes paramétrées).",
        "code_example": '# SÉCURISÉ (Requête paramétrée contre l\'injection SQL) :\nconn.execute("SELECT * FROM formations WHERE id = ?", (id,))'
    }
]
