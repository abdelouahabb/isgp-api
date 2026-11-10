"""
Diagrammes d'architecture et de séquence Mermaid.js pour l'ensemble des 29 chapitres du Bootcamp ISGP (Jours 0 à 5).
Chaque diagramme respecte strictement la grammaire Mermaid 10.x (étiquettes entre guillemets doubles).
"""

MERMAID_DIAGRAMS = {
    # =========================================================================
    # JOUR 0 : FONDATIONS PYTHON POUR L'INGÉNIERIE D'API
    # =========================================================================
    "d0-l1": {
        "title": "Correspondance des Types Python (RAM) et Sérialisation JSON (RFC 8259)",
        "code": """flowchart LR
    subgraph Python["Espace Mémoire Python (Serveur Flask)"]
        P1["str : 'Alger'"]
        P2["int / float : 5, 19.5"]
        P3["bool : True / False"]
        P4["NoneType : None"]
    end
    subgraph JSON["Flux Réseau JSON (UTF-8)"]
        J1["string : \\"Alger\\""]
        J2["number : 5, 19.5"]
        J3["boolean : true / false"]
        J4["null : null"]
    end
    P1 -->|"jsonify() / json.dumps()"| J1
    P2 -->|"jsonify() / json.dumps()"| J2
    P3 -->|"jsonify() / json.dumps()"| J3
    P4 -->|"jsonify() / json.dumps()"| J4"""
    },
    "d0-l2": {
        "title": "Structure d'une Réponse d'API : Enveloppe Dictionnaire { } et Collection Liste [ ]",
        "code": """flowchart TD
    Root["Enveloppe Racine (dict Python / Objet JSON { })"]
    Meta["Clé 'meta' (dict { } : page, total, version)"]
    Data["Clé 'data' (list [ ] : Collection d'enregistrements)"]
    Item1["Élément 0 (dict { } : id=1, titre='API REST')"]
    Item2["Élément 1 (dict { } : id=2, titre='Flask & Jinja2')"]
    Item3["Élément 2 (dict { } : id=3, titre='Sécurité JWT')"]
    Root --> Meta
    Root --> Data
    Data --> Item1
    Data --> Item2
    Data --> Item3"""
    },
    "d0-l3": {
        "title": "Découpage Modulaire : Route HTTP vs Fonction Métier Pure",
        "code": """sequenceDiagram
    participant C as Client HTTP
    participant R as Route Flask (@app.route)
    participant F as Fonction Métier Pure (calculer_ttc)
    C->>R: GET /api/calcul-tva?ht=1000
    R->>R: Extrait et valide prix_ht = 1000.0
    R->>F: Appelle calculer_ttc(1000.0)
    F-->>R: Retourne dict {"prix_ht": 1000, "tva_19": 190, "prix_ttc": 1190}
    R-->>C: HTTP 200 OK (JSON)"""
    },
    "d0-l4": {
        "title": "Mécanisme d'Enveloppement d'un Décorateur Python (@) et Gestion d'Exception",
        "code": """sequenceDiagram
    participant Appel as Appelant / Serveur WSGI
    participant Deco as Décorateur (@journaliser / @app.route)
    participant Func as Fonction Métier (traiter_inscription)
    Appel->>Deco: 1. Requête entrante (*args, **kwargs)
    Deco->>Deco: 2. Pré-traitement (Chronomètre, Vérification Auth)
    alt Entrée Valide
        Deco->>Func: 3. Exécute la fonction cible
        Func-->>Deco: 4. Retourne le résultat métier
        Deco-->>Appel: 5. Post-traitement (Audit Log) + Réponse 200 OK
    else Exception ValueError / KeyError interceptée (try/except)
        Deco-->>Appel: Capture l'erreur sans crash -> Réponse 400 / 422 JSON
    end"""
    },

    # =========================================================================
    # JOUR 1 : ARCHITECTURE DES SERVICES WEB, HTTP/1.1, JSON & CURL
    # =========================================================================
    "d1-l1": {
        "title": "Architecture Découplée : Rendu Serveur Jinja2 (HTML) vs Services Web (SOAP/XML & REST/JSON)",
        "code": """flowchart LR
    subgraph Clients["Consommateurs Hétérogènes"]
        Browser["Navigateur Web Humain"]
        Mobile["Application Mobile iOS/Android"]
        Partner["Système Bancaire / Partenaire"]
    end
    subgraph FlaskApp["Serveur Python Flask + SQLite"]
        Jinja["Moteur Jinja2 (render_template)"]
        REST["API REST (jsonify)"]
        SOAP["Passerelle SOAP (XML)"]
        DB[("Base SQLite / PostgreSQL")]
    end
    Browser -->|"GET /formations (Accept: text/html)"| Jinja
    Mobile -->|"GET /api/v1/formations (Accept: application/json)"| REST
    Partner -->|"POST /ws/meteo (application/soap+xml)"| SOAP
    Jinja --> DB
    REST --> DB
    SOAP --> DB"""
    },
    "d1-l2": {
        "title": "Les 4 Étapes Réseau d'un Appel d'API (DNS, TCP Handshake, TLS 1.3 & Requête HTTP)",
        "code": """sequenceDiagram
    participant Client as Client API (curl / Mobile)
    participant DNS as Résolveur DNS
    participant Server as Serveur API (192.168.1.50:443)
    Client->>DNS: 1. Résolution de 'api.isgp.dz'
    DNS-->>Client: Adresse IP : 192.168.1.50
    Client->>Server: 2. Poignée de main TCP (SYN -> SYN/ACK -> ACK) sur Port 443
    Client->>Server: 3. Négociation Cryptographique TLS 1.3 (Certificat + Clé de session AES-GCM)
    Client->>Server: 4. Envoi de la Trame HTTP Chiffrée (GET /api/v1/formations?page=1)
    Server-->>Client: 5. Réponse HTTP/1.1 200 OK (Payload JSON)"""
    },
    "d1-l3": {
        "title": "Anatomie d'une Trame HTTP/1.1 : Appel API JSON vs Soumission de Formulaire HTML",
        "code": """flowchart TD
    subgraph Frame["Structure Normalisée d'une Trame HTTP/1.1 (RFC 9112)"]
        SL["1. Start Line : POST /api/v1/formations HTTP/1.1"]
        HD["2. En-têtes (Headers) : Host, Authorization, Content-Type, Content-Length"]
        CRLF["3. Ligne Vide Obligatoire (\\r\\n\\r\\n)"]
        BD["4. Corps du Message (Body / Payload)"]
        SL --> HD --> CRLF --> BD
    end
    BD -->|"Content-Type: application/json"| JSONBody["Corps JSON : {'titre': 'Flask'} -> lu par request.get_json()"]
    BD -->|"Content-Type: application/x-www-form-urlencoded"| FormBody["Corps Formulaire : titre=Flask&duree=5 -> lu par request.form"]"""
    },
    "d1-l4": {
        "title": "Matrice de Sémantique et d'Idempotence des Verbes HTTP (RFC 9110)",
        "code": """flowchart LR
    Verbes["Méthodes HTTP/1.1"]
    subgraph Safe["Sûres (Lecture seule) & Idempotentes"]
        GET["GET / HEAD / OPTIONS"]
    end
    subgraph IdemWrite["Non Sûres mais Idempotentes (N appels = 1 seul effet)"]
        PUT["PUT (Remplacement complet)"]
        DEL["DELETE (Suppression)"]
    end
    subgraph NonIdem["Non Idempotentes (Risque de doublon en cas de retry)"]
        POST["POST (Création -> Sécuriser avec Idempotency-Key)"]
        PATCH["PATCH (Modification partielle)"]
    end
    Verbes --> Safe
    Verbes --> IdemWrite
    Verbes --> NonIdem"""
    },
    "d1-l5": {
        "title": "Outillage de Diagnostic d'API : curl, Postman, HTTPie & Swagger UI",
        "code": """flowchart LR
    subgraph Tools["Outils d'Inspection & Test HTTP"]
        Curl["Terminal : curl -i -X POST -H -d"]
        Postman["Graphique : Postman / Bruno / Insomnia"]
        RestClient["IDE : Fichier .http (VS Code / Antigravity)"]
        Swagger["Navigateur : Swagger UI (/api/docs)"]
    end
    subgraph Target["Serveur Flask Local (127.0.0.1:5000)"]
        API["Endpoints /api/sandbox/..."]
    end
    Curl -->|"Inspection brute Status + Headers"| API
    Postman -->|"Collections & Variables {{token}}"| API
    RestClient -->|"Tests versionnés dans Git"| API
    Swagger -->|"Contrat OpenAPI 3.0 interactif"| API"""
    },

    # =========================================================================
    # JOUR 2 : DESIGN RESTFUL, FLASK, TEMPLATES JINJA2 & FORMULAIRES HTML
    # =========================================================================
    "d2-l1": {
        "title": "Cycle WSGI de Flask : Servir une Page Web Jinja2 (render_template) vs une Route API REST (jsonify)",
        "code": """sequenceDiagram
    participant Nav as Navigateur / Client API
    participant WSGI as Serveur WSGI (Flask App)
    participant Tpl as Dossier templates/ (Jinja2 .html)
    alt Route Web HTML (GET /accueil)
        Nav->>WSGI: GET /accueil (Accept: text/html)
        WSGI->>Tpl: render_template("accueil.html", modules=...)
        Tpl-->>WSGI: HTML compilé (variables {{ }} échappées anti-XSS)
        WSGI-->>Nav: HTTP 200 OK (Content-Type: text/html; charset=utf-8)
    else Route API REST (GET /api/v1/modules)
        Nav->>WSGI: GET /api/v1/modules (Accept: application/json)
        WSGI->>WSGI: jsonify({"total": 5, "data": [...]})
        WSGI-->>Nav: HTTP 200 OK (Content-Type: application/json)
    end"""
    },
    "d2-l2": {
        "title": "Routage Dynamique Flask (<int:id>) vs Notations Postman (:id) et OpenAPI ({id})",
        "code": """flowchart TD
    Req["Requête entrante : GET /api/v1/stagiaires/42?ht=2500&taux=19"]
    Router["Routeur Werkzeug / Flask : @app.route('/api/v1/stagiaires/<int:stagiaire_id>')"]
    Conv{"Valeur '42' convertible en int ?"}
    Handler["Fonction Python : obtenir_stagiaire(stagiaire_id=42)"]
    Args["Lecture Query String : request.args.get('ht', type=float) -> 2500.0"]
    Err404["Rejet automatique : HTTP 404 Not Found"]
    Req --> Router --> Conv
    Conv -->|"Oui (int = 42)"| Handler --> Args
    Conv -->|"Non (ex: /stagiaires/abc)"| Err404"""
    },
    "d2-l5": {
        "title": "Cycle Complet d'un Formulaire Web HTML (<form method='POST'>) et du Rendu Serveur Jinja2",
        "code": """sequenceDiagram
    participant User as Navigateur Utilisateur
    participant Flask as Route Flask (/formations)
    participant DB as Base SQLite
    participant Jinja as Template Jinja2 (templates/formations.html)
    User->>Flask: 1. GET /formations (Demande la page du formulaire)
    Flask->>DB: SELECT * FROM formations
    Flask->>Jinja: render_template("formations.html", formations=...)
    Jinja-->>User: 2. Page HTML contenant <form method="POST"> + Tableau {% for f in formations %}
    User->>Flask: 3. POST /formations (Content-Type: application/x-www-form-urlencoded : titre=Flask&duree_jours=5)
    Flask->>Flask: 4. Extraction via request.form.get("titre") et validation serveur
    Flask->>DB: 5. INSERT INTO formations (?, ?, ?)
    Flask->>Jinja: 6. render_template("formations.html", message_confirmation=..., formations=...)
    Jinja-->>User: 7. Page HTML mise à jour (HTTP 200/201)"""
    },
    "d2-l3": {
        "title": "Pipeline de Traitement d'une Collection : 1. Filtrage -> 2. Tri Sécurisé -> 3. Pagination (Offset/Limit)",
        "code": """flowchart LR
    Raw[("Collection Complète\n(ex: 10 000 lignes)")]
    Step1["1. Filtrage (WHERE)\n?salle=Salle+A&min_jours=3"]
    Step2["2. Tri sur Liste Blanche (ORDER BY)\n?tri=duree_jours&ordre=desc"]
    Step3["3. Découpage Page (LIMIT / OFFSET)\n?page=2&limit=10 -> offset = (2-1)*10 = 10"]
    Out["Enveloppe JSON :\nmeta (total_pages, has_next) + data (10 éléments)"]
    Raw --> Step1 --> Step2 --> Step3 --> Out"""
    },
    "d2-l4": {
        "title": "Cycle d'Exécution des Middlewares Flask (@app.before_request & @app.after_request)",
        "code": """sequenceDiagram
    participant C as Client HTTP
    participant Before as @app.before_request
    participant Route as Route Métier (@app.route)
    participant After as @app.after_request
    C->>Before: 1. Requête entrante
    Before->>Before: Démarre g.heure_debut = perf_counter() et génère g.request_id (UUID)
    Before->>Route: 2. Passe le relais à la route cible
    Route-->>After: 3. Objet Response généré
    After->>After: 4. Calcule durée (ms), injecte X-Request-ID, X-Response-Time-Ms, X-Content-Type-Options: nosniff
    After->>After: 5. Écrit la ligne [AUDIT] dans les logs serveur
    After-->>C: 6. Réponse HTTP enrichie envoyée au client"""
    },

    # =========================================================================
    # JOUR 3 : INGÉNIERIE CRUD, VALIDATION RFC 7807, IDEMPOTENCE & SQLITE
    # =========================================================================
    "d3-l1": {
        "title": "Entonnoir de Validation Serveur en 4 Niveaux et Réponse Normalisée RFC 7807 (422)",
        "code": """flowchart TD
    In["POST /api/v1/formations (Payload entrant)"]
    L1{"1. Syntaxe JSON valide ?\nisinstance(corps, dict)"}
    L2{"2. Champs requis présents ?\n'titre' non vide après .strip()"}
    L3{"3. Types conformes ?\n'duree_jours' convertible en int"}
    L4{"4. Règles métier respectées ?\n1 <= duree_jours <= 30"}
    OK["Insertion en base + HTTP 201 Created"]
    E400["HTTP 400 Bad Request\n(JSON malformé)"]
    E422["HTTP 422 Unprocessable Entity\nFormat RFC 7807 (application/problem+json)"]
    In --> L1
    L1 -->|"Non"| E400
    L1 -->|"Oui"| L2
    L2 -->|"Non"| E422
    L2 -->|"Oui"| L3
    L3 -->|"Non"| E422
    L3 -->|"Oui"| L4
    L4 -->|"Non"| E422
    L4 -->|"Oui"| OK"""
    },
    "d3-l2": {
        "title": "Mécanisme de Protection Anti-Doublon sur POST par En-tête Idempotency-Key",
        "code": """sequenceDiagram
    participant Mobile as Client Mobile (Réseau 4G instable)
    participant API as Serveur Flask + Cache Idempotence
    participant DB as Base SQLite
    Mobile->>API: 1. POST /api/commandes (Header Idempotency-Key: idem-9988)
    API->>API: Clé 'idem-9988' absente du cache
    API->>DB: INSERT INTO commandes (Crée la commande #101)
    API->>API: Mémorise cache["idem-9988"] = Commande #101
    API--xMobile: Réponse 201 perdue (Coupure réseau 4G !)
    Note over Mobile,API: Le téléphone rejoue automatiquement la même requête POST :
    Mobile->>API: 2. Retry POST /api/commandes (Header Idempotency-Key: idem-9988)
    API->>API: Clé 'idem-9988' trouvée dans le cache ! (Aucun nouvel INSERT)
    API-->>Mobile: HTTP 200/201 : Renvoie la Commande #101 existante (rejoue_sans_doublon: true)"""
    },
    "d3-l3": {
        "title": "Interception Globale des Exceptions (@app.errorhandler) : Zéro Page HTML d'Erreur en API",
        "code": """flowchart LR
    Req["Requête Client API"] --> Flask["Exécution Route Flask"]
    Flask -->|"URL inconnue"| H404["@app.errorhandler(404)\n-> JSON 404 Not Found"]
    Flask -->|"Verbe interdit"| H405["@app.errorhandler(405)\n-> JSON 405 Method Not Allowed"]
    Flask -->|"Crash Python imprévu\n(ZeroDivisionError, SQLiteError)"| H500["@app.errorhandler(Exception)\n1. Log technique interne\n2. JSON 500 générique sans fuite de code"]"""
    },
    "d3-l4": {
        "title": "Parade contre l'Injection SQL : Compilation Séparée des Requêtes Paramétrées (?)",
        "code": """sequenceDiagram
    participant Attacker as Client (Entrée : "' OR '1'='1")
    participant Flask as Route Flask (sqlite3)
    participant Engine as Moteur SQLite (Arbre AST SQL)
    Attacker->>Flask: Envoie salle = "' OR '1'='1"
    Flask->>Engine: 1. Envoie le squelette SQL : SELECT * FROM formations WHERE salle = ?
    Engine->>Engine: 2. Compile le plan d'exécution SQL (structure verrouillée)
    Flask->>Engine: 3. Lie le paramètre tuple ("' OR '1'='1",) comme littéral texte inerte
    Engine-->>Flask: 4. Cherche une salle nommée littéralement "' OR '1'='1'" -> 0 résultat (Attaque neutralisée)"""
    },

    # =========================================================================
    # JOUR 4 : SÉCURITÉ API (AUTHN 401, AUTHZ 403, JWT, RATE LIMITING 429, CORS)
    # =========================================================================
    "d4-l1": {
        "title": "Vérification d'une Clé API (X-API-Key) en Temps Constant (hmac.compare_digest)",
        "code": """flowchart LR
    Env[("Variables d'Environnement\n(.env / os.environ['PARTNER_API_KEY'])")]
    Client["Requête Client\nHeader X-API-Key: ..."]
    Comp["Comparaison en Temps Constant\nhmac.compare_digest(cle_recue, cle_attendue)"]
    Env --> Comp
    Client --> Comp
    Comp -->|"True"| OK["HTTP 200 OK\nAccès Partenaire Autorisé"]
    Comp -->|"False"| Err401["HTTP 401 Unauthorized\n(Protection contre Timing Attack)"]"""
    },
    "d4-l2": {
        "title": "Cycle de Vie d'un Bearer Token Signé (JWT / TimedSerializer HMAC-SHA256)",
        "code": """sequenceDiagram
    participant C as Client API
    participant Auth as POST /api/auth/token
    participant Resource as GET /api/auth/profil
    C->>Auth: 1. Envoie {"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}
    Auth->>Auth: 2. Vérifie le mot de passe + Signe le payload (sub, role, exp) avec SECRET_KEY (HMAC-SHA256)
    Auth-->>C: 3. Retourne {"access_token": "eyJ..."} (200 OK)
    C->>Resource: 4. Appelle GET /api/auth/profil avec Header "Authorization: Bearer eyJ..."
    Resource->>Resource: 5. Recalcule la signature HMAC avec SECRET_KEY et vérifie la date d'expiration (max_age=300s)
    Resource-->>C: 6. Signature valide -> Retourne le profil JSON (200 OK)"""
    },
    "d4-l3": {
        "title": "Chaîne de Sécurité Complet : Authentification (401) -> Rôle/Scopes (403) -> Propriété Anti-BOLA (403)",
        "code": """flowchart TD
    Req["Requête sur GET /api/dossiers/42"]
    Step1{"Étape 1 : AuthN (Qui êtes-vous ?)\nToken Bearer présent, signé et non expiré ?"}
    Step2{"Étape 2 : AuthZ RBAC / Scopes\nRôle autorisé ou scope 'dossiers:read' présent ?"}
    Step3{"Étape 3 : AuthZ Anti-BOLA (OWASP #1)\ndossier.proprietaire == user.sub OU user.role == 'admin' ?"}
    E401["HTTP 401 Unauthorized\nHeader WWW-Authenticate: Bearer"]
    E403A["HTTP 403 Forbidden\n(Rôle ou Scope insuffisant)"]
    E403B["HTTP 403 Forbidden\n(Tentative d'accès BOLA bloquée)"]
    OK["HTTP 200 OK\nAccès légitime accordé"]
    Req --> Step1
    Step1 -->|"Non"| E401
    Step1 -->|"Oui"| Step2
    Step2 -->|"Non"| E403A
    Step2 -->|"Oui"| Step3
    Step3 -->|"Non"| E403B
    Step3 -->|"Oui"| OK"""
    },
    "d4-l4": {
        "title": "Architecture à Double Jeton : Access Token (Courte Durée) & Refresh Token (Révocable)",
        "code": """sequenceDiagram
    participant C as Application Cliente
    participant API as Serveur API (/api/v1/...)
    participant Auth as Serveur d'Authentification (/auth/refresh)
    C->>Auth: 1. Login initial -> Reçoit Access Token (15 min) + Refresh Token (7 jours, jti unique)
    C->>API: 2. Appels métiers avec Access Token (rapide, sans requête BDD)
    Note over C,API: Au bout de 15 minutes, l'Access Token expire (HTTP 401) :
    C->>Auth: 3. POST /auth/refresh (avec le Refresh Token)
    Auth->>Auth: 4. Vérifie que le 'jti' du Refresh Token n'est pas dans la Blacklist
    Auth-->>C: 5. Émet un nouvel Access Token neuf de 15 minutes"""
    },
    "d4-l5": {
        "title": "Algorithme de Rate Limiting par Fenêtre Glissante (Sliding Window) & Statut 429",
        "code": """flowchart TD
    Req["Nouvelle requête du client (IP / Clé API)"]
    Purge["1. Purge les horodatages vieux de plus de 20 secondes\n(now - t > 20s)"]
    Check{"2. Nombre de requêtes dans la fenêtre\nlen(historique) >= Quota Max (3) ?"}
    Allow["3a. Ajoute 'now' à l'historique\nInjecte X-RateLimit-Remaining\n-> HTTP 200 OK"]
    Block["3b. Rejette immédiatement l'appel\nInjecte Retry-After: 14\n-> HTTP 429 Too Many Requests"]
    Req --> Purge --> Check
    Check -->|"Non (< 3)"| Allow
    Check -->|"Oui (>= 3)"| Block"""
    },
    "d4-l6": {
        "title": "Sécurité Périmétrique : Requête Pré-vol CORS (OPTIONS) et Vérification Webhook HMAC-SHA256",
        "code": """sequenceDiagram
    participant Browser as Navigateur (Origine: https://portail.isgp.dz)
    participant API as Serveur API Flask (https://api.isgp.dz)
    participant Partner as Serveur Partenaire (Webhook)
    Browser->>API: 1. Pré-vol automatique : OPTIONS /api/formations (Origin: https://portail.isgp.dz)
    API-->>Browser: 2. 204 No Content (Access-Control-Allow-Origin: https://portail.isgp.dz)
    Browser->>API: 3. Requête réelle : POST /api/formations (avec Authorization: Bearer)
    API-->>Browser: 4. Réponse JSON 201 Created
    Partner->>API: 5. POST /webhooks/paiement (Body brut + Header X-Webhook-Signature: sha256=...)
    API->>API: 6. Recalcule HMAC-SHA256 sur request.get_data() avec WEBHOOK_SECRET"""
    },
    "d4-l7": {
        "title": "Sécurité des Cookies HTTP : Boucliers HttpOnly (Anti-XSS), SameSite (Anti-CSRF) & Signature HMAC (session)",
        "code": """sequenceDiagram
    participant Browser as Navigateur (Coffre-Fort Réseau HTTP)
    participant JS as Script JavaScript (DOM / Risque XSS)
    participant API as Serveur Flask (secret_key HMAC)
    Browser->>API: 1. POST /api/auth/cookie-login (Identifiants)
    API-->>Browser: 2. 200 OK + Set-Cookie: isgp_auth_token=...; HttpOnly; Secure; SameSite=Strict
    Note over Browser,JS: Drapeau HttpOnly actif :
    JS->>Browser: 3. Tentative de lecture : document.cookie
    Browser--xJS: 4. Accès REFUSÉ au cookie isgp_auth_token (Protection Anti-XSS !)
    Browser->>API: 5. GET /api/auth/cookie-inspect (Envoi auto de l'en-tête Cookie)
    API->>API: 6. Vérifie la signature HMAC avec app.secret_key
    API-->>Browser: 7. HTTP 200 OK (Session authentifiée)"""
    },

    # =========================================================================
    # JOUR 5 : ARCHITECTURE MODULAIRE, TESTS, OPENAPI/SWAGGER & PAGINATION PRODUCTION
    # =========================================================================
    "d5-l1": {
        "title": "Stratégie d'Appel Résilient : Timeout Strict et Recul Exponentiel (Exponential Backoff)",
        "code": """sequenceDiagram
    participant Client as Client Python Résilient (timeout=5s)
    participant Remote as API Partenaire Distante
    Client->>Remote: Tentative #1 : GET /api/ressource (timeout=5.0s)
    Remote-->>Client: HTTP 503 Service Unavailable (Surcharge temporaire)
    Note over Client: Attente exponentielle : 2^0 = 1 seconde
    Client->>Remote: Tentative #2 : GET /api/ressource (timeout=5.0s)
    Remote-->>Client: HTTP 503 Service Unavailable
    Note over Client: Attente exponentielle : 2^1 = 2 secondes
    Client->>Remote: Tentative #3 : GET /api/ressource (timeout=5.0s)
    Remote-->>Client: HTTP 200 OK (Succès récupéré sans panne en cascade)"""
    },
    "d5-l2": {
        "title": "Coexistence Multi-Versions (/api/v1 Dépréciée RFC 8594 + /api/v2) & Application Factory (create_app)",
        "code": """flowchart TD
    Factory["Application Factory : create_app()"]
    BP_Web["Blueprint Web Jinja2\nurl_prefix='/portail'\nRendu HTML (templates/)"]
    BP_V1["Blueprint API v1 (Dépréciée RFC 8594)\nurl_prefix='/api/v1/formations'\nHeaders: Deprecation: true, Sunset: 31 Dec 2026\nSchéma plat: {'duree': 5}"]
    BP_V2["Blueprint API v2 (Nouveau Contrat)\nurl_prefix='/api/v2/formations'\nBreaking Change: {'duree': {'valeur': 5, 'unite': 'jours'}}"]
    BP_Health["Blueprint Supervision\nurl_prefix='/api/health'\n(/live & /ready)"]
    DB[("Couche Métier & Base SQLite Unique\n(Partagée entre v1, v2 et Web)")]
    Factory -->|"register_blueprint()"| BP_Web
    Factory -->|"register_blueprint()"| BP_V1
    Factory -->|"register_blueprint()"| BP_V2
    Factory -->|"register_blueprint()"| BP_Health
    BP_Web --> DB
    BP_V1 --> DB
    BP_V2 --> DB"""
    },
    "d5-l3": {
        "title": "Pipeline d'Assurance Qualité (app.test_client) & Déploiement Production WSGI",
        "code": """flowchart LR
    Code["Code Flask\n(Routes JSON + Formulaires Jinja2)"]
    Test["Tests Automatisés en Mémoire\nclient = app.test_client()\nassert status_code == 200 / 422"]
    Nginx["Reverse Proxy Nginx\n(TLS 1.3 + Fichiers /static/)"]
    Gunicorn["Serveur WSGI Gunicorn\n(4 Workers Processus Python)"]
    Code --> Test -->|"Tests validés"| Gunicorn
    Nginx -->|"proxy_pass"| Gunicorn"""
    },
    "d5-l4": {
        "title": "Écosystème OpenAPI 3.0 : Du Contrat Unique (/api/openapi.json) à Swagger UI et Postman",
        "code": """flowchart LR
    Spec["Contrat Officiel Unique\nGET /api/openapi.json\n(OpenAPI 3.0.3)"]
    SwaggerUI["Portail Interactif Swagger UI\nGET /api/docs\n(Boutons Authorize & Try it out)"]
    Postman["Import Automatique\nCollections Postman / Insomnia"]
    Codegen["Génération de SDK Clients\n(TypeScript, Android, Python)"]
    Spec --> SwaggerUI
    Spec --> Postman
    Spec --> Codegen"""
    },
    "d5-l5": {
        "title": "Ingénierie de Collection en Production : Pagination Offset/Limit O(N) vs Curseur Keyset O(1) & Tri par Liste Blanche",
        "code": """flowchart TD
    Req["Requête GET de Collection\n(?sort=-tarif_dzd & paramètres de pagination)"]
    Whitelist{"1. Validation de 'sort'\ndans CHAMPS_TRI_AUTORISES ?"}
    Err422["HTTP 422 Unprocessable Entity\n(Bloque toute injection ORDER BY)"]
    Mode{"2. Stratégie de Pagination"}
    Offset["Pagination Offset / Limit\n(?page=2&per_page=20)\nSQL: LIMIT 20 OFFSET 20\nIdéal pour pages numérotées (1, 2, 3...)"]
    Cursor["Pagination Curseur / Keyset\n(?after_id=1042&limit=20)\nSQL: WHERE id > 1042 LIMIT 20\nTemps constant O(1) sur des millions de lignes"]
    Req --> Whitelist
    Whitelist -->|"Non"| Err422
    Whitelist -->|"Oui"| Mode
    Mode -->|"Numéros de pages"| Offset
    Mode -->|"Flux haute volumétrie"| Cursor"""
    },
}
