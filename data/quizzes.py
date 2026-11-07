"""
Évaluations formatives (Jour 0 à Jour 5).
Chaque question contient une justification méthodique sans prérequis implicite.
"""

QUIZZES = {
    0: {
        "title": "Diagnostic & Mise à Niveau (Fondations Python)",
        "description": "Validation des structures de base Python (variables, listes, dictionnaires, fonctions) indispensables avant d'aborder le protocole HTTP.",
        "questions": [
            {
                "id": "q0-1",
                "question": "En Python, quelle syntaxe déclare un Dictionnaire associant la clé \"ville\" à la valeur \"Alger\" ?",
                "options": [
                    '{"ville": "Alger"}',
                    '["ville", "Alger"]',
                    '(ville = Alger)',
                    '<ville>Alger</ville>'
                ],
                "correct_index": 0,
                "explanation": "Un dictionnaire Python est délimité par des accolades `{ }` et associe chaque `\"clé\"` à sa `\"valeur\"` via le séparateur `:`. Cette structure correspond directement au format JSON."
            },
            {
                "id": "q0-2",
                "question": "Quel est le rôle de l'instruction `return` à l'intérieur d'une fonction Python (`def ma_fonction():`) ?",
                "options": [
                    "Restituer le résultat produit par la fonction à l'instruction qui l'a appelée",
                    "Arrêter définitivement le système d'exploitation",
                    "Supprimer toutes les variables en mémoire",
                    "Installer une bibliothèque externe"
                ],
                "correct_index": 0,
                "explanation": "L'instruction `return` transmet la valeur de sortie de la fonction. Dans Flask, la valeur retournée par une fonction de route constitue la réponse HTTP envoyée au client."
            },
            {
                "id": "q0-3",
                "question": "Soit la liste `modules = [\"HTTP\", \"Flask\", \"SQLite\"]`. Quelle est la valeur de `modules[0]` ?",
                "options": [
                    '"HTTP"',
                    '"Flask"',
                    'Une erreur car la numérotation commence à 1',
                    '"SQLite"'
                ],
                "correct_index": 0,
                "explanation": "En Python, l'indexation des séquences commence toujours à `0`. Le premier élément est donc accessible via l'indice `0`."
            }
        ]
    },
    1: {
        "title": "Évaluation Jour 1 : Architecture Web, HTTP & JSON",
        "description": "Validation du modèle Client/Serveur, des méthodes HTTP et de la classification des codes de statut.",
        "questions": [
            {
                "id": "q1-1",
                "question": "Quelle est la distinction fondamentale entre un serveur Web classique et une API Web REST ?",
                "options": [
                    "Le serveur Web classique renvoie du HTML destiné à l'affichage visuel, tandis que l'API renvoie des données structurées (JSON) exploitables par tout système logiciel",
                    "Une API n'utilise pas le protocole HTTP",
                    "Une API est réservée exclusivement aux téléphones mobiles",
                    "Il n'existe aucune différence technique"
                ],
                "correct_index": 0,
                "explanation": "Une API découple les données (JSON) de la couche de présentation, permettant d'alimenter simultanément des interfaces Web, mobiles et des services tiers."
            },
            {
                "id": "q1-2",
                "question": "Quelle méthode HTTP est normalisée pour CRÉER un nouvel enregistrement sur le serveur ?",
                "options": [
                    "POST",
                    "GET",
                    "DELETE",
                    "READ"
                ],
                "correct_index": 0,
                "explanation": "`GET` consulte, **`POST`** crée une ressource à partir du corps JSON transmis, `PUT` met à jour et `DELETE` supprime."
            },
            {
                "id": "q1-3",
                "question": "Que signifie le code de statut HTTP `404 Not Found` ?",
                "options": [
                    "La route URL demandée ou l'identifiant ciblé n'existe pas sur le serveur",
                    "La requête a été traitée avec succès",
                    "Le serveur a bloqué le client pour dépassement de quota (Rate Limit)",
                    "Une erreur de syntaxe Python a interrompu le serveur"
                ],
                "correct_index": 0,
                "explanation": "Le code `404` indique que la ressource demandée par le client est introuvable."
            }
        ]
    },
    2: {
        "title": "Évaluation Jour 2 : Routage et Paramètres avec Flask",
        "description": "Validation du mécanisme `@app.route`, de `jsonify()` et de l'extraction des paramètres d'URL.",
        "questions": [
            {
                "id": "q2-1",
                "question": "Quel est le rôle du décorateur `@app.route(\"/api/bonjour\")` placé au-dessus d'une fonction Python ?",
                "options": [
                    "Enregistrer une règle d'aiguillage dans Flask pour exécuter cette fonction lorsqu'un client appelle l'URL `/api/bonjour`",
                    "Ajouter un commentaire ignoré par l'interpréteur Python",
                    "Télécharger le paquet Flask depuis Internet",
                    "Créer une table dans la base de données"
                ],
                "correct_index": 0,
                "explanation": "Le décorateur `@app.route(...)` lie une URL et une méthode HTTP à la fonction Python qui doit traiter la requête."
            },
            {
                "id": "q2-2",
                "question": "Lors d'un appel sur `/api/formations?ville=Alger`, quelle instruction Flask extrait la valeur `\"Alger\"` ?",
                "options": [
                    'request.args.get("ville")',
                    'request.get_json()',
                    'request.headers.get("ville")',
                    'jsonify("ville")'
                ],
                "correct_index": 0,
                "explanation": "Les paramètres de requête situés après le point d'interrogation `?` dans l'URL sont exposés dans le dictionnaire `request.args`."
            }
        ]
    },
    3: {
        "title": "Évaluation Jour 3 : Opérations CRUD & Persistance SQLite",
        "description": "Validation de la lecture du corps JSON, des codes 201/400 et des requêtes SQLite paramétrées.",
        "questions": [
            {
                "id": "q3-1",
                "question": "Lorsqu'un client transmet un objet JSON via une requête `POST`, quelle méthode Flask le convertit en dictionnaire Python ?",
                "options": [
                    "request.get_json()",
                    "request.args.get()",
                    "jsonify()",
                    "sqlite3.connect()"
                ],
                "correct_index": 0,
                "explanation": "`request.get_json()` lit le corps (`Body`) de la requête HTTP et désérialise le JSON en dictionnaire Python."
            },
            {
                "id": "q3-2",
                "question": "Pourquoi utilise-t-on des points d'interrogation `?` dans `conn.execute(\"SELECT * FROM formations WHERE id = ?\", (id,))` ?",
                "options": [
                    "Pour exécuter une requête paramétrée qui protège la base de données contre les attaques par Injection SQL",
                    "Parce que SQLite ne connaît pas le signe =",
                    "Pour accélérer l'affichage HTML",
                    "Pour chiffrer le disque dur"
                ],
                "correct_index": 0,
                "explanation": "Les requêtes paramétrées séparent strictement l'instruction SQL de la donnée fournie par l'utilisateur, neutralisant ainsi toute tentative d'injection SQL."
            }
        ]
    },
    4: {
        "title": "Évaluation Jour 4 : Cœur d'API — Secrets, Bearer Tokens & Rate Limiting",
        "description": "Validation des mécanismes critiques de sécurité et de contrôle de flux en production.",
        "questions": [
            {
                "id": "q4-1",
                "question": "Quelle est la bonne pratique absolue pour gérer une clé secrète (`SECRET_KEY` ou clé API) dans une application Python ?",
                "options": [
                    "La stocker hors du code source dans une variable d'environnement et la lire avec os.environ.get('API_SECRET_KEY')",
                    "L'écrire directement en clair en haut du fichier app.py et la publier sur GitHub",
                    "La passer dans l'URL sous la forme ?secret=123456",
                    "L'afficher dans les messages d'erreur JSON pour faciliter le débogage"
                ],
                "correct_index": 0,
                "explanation": "Un secret ne doit jamais figurer en dur dans le code source versionné ni dans une URL. Il doit être injecté via l'environnement du serveur (`os.environ`)."
            },
            {
                "id": "q4-2",
                "question": "Comment un client transmet-il un jeton d'accès temporaire (`Bearer Token`) à une API REST ?",
                "options": [
                    "Dans l'en-tête HTTP : Authorization: Bearer <le_jeton_signe>",
                    "Dans le nom du fichier Python",
                    "Dans l'en-tête Content-Type",
                    "Uniquement par courrier électronique"
                ],
                "correct_index": 0,
                "explanation": "Le standard RFC 6750 utilise l'en-tête HTTP `Authorization` suivi du préfixe `Bearer ` et du jeton signé."
            },
            {
                "id": "q4-3",
                "question": "Qu'est-ce qui empêche un client malveillant de modifier le contenu d'un jeton signé (ex. remplacer `\"role\": \"stagiaire\"` par `\"role\": \"admin\"`) ?",
                "options": [
                    "La signature cryptographique calculée avec la SECRET_KEY du serveur : toute modification invalide immédiatement la signature (BadSignature)",
                    "Le fait que le réseau Internet refuse les mots 'admin'",
                    "La taille maximale de l'URL",
                    "Rien, le client peut librement modifier son jeton"
                ],
                "correct_index": 0,
                "explanation": "Seul le serveur possède la `SECRET_KEY` ayant servi à calculer la signature du jeton. Si un seul caractère de la charge utile change, la signature recalculée par le serveur ne correspond plus et la requête est rejetée (`401 Unauthorized`)."
            },
            {
                "id": "q4-4",
                "question": "Quel code de statut HTTP une API renvoie-t-elle lorsqu'un client dépasse le quota de requêtes autorisé par le Rate Limiter ?",
                "options": [
                    "429 Too Many Requests (accompagné des en-têtes X-RateLimit-Remaining: 0 et Retry-After)",
                    "200 OK",
                    "404 Not Found",
                    "301 Moved Permanently"
                ],
                "correct_index": 0,
                "explanation": "Le code **`429 Too Many Requests`** est le standard HTTP indiquant que le client a dépassé la limite de débit (Rate Limit) autorisée sur la fenêtre de temps."
            }
        ]
    },
    5: {
        "title": "Évaluation Jour 5 : Synthèse Architecturale & Consommation d'API",
        "description": "Validation du cycle complet d'intégration cliente.",
        "questions": [
            {
                "id": "q5-1",
                "question": "Dans quel ordre un client automatisé consomme-t-il une API protégée par Bearer Token et Rate Limiting ?",
                "options": [
                    "1) S'authentifier sur POST /api/auth/token -> 2) Conserver l'access_token -> 3) L'envoyer dans l'en-tête Authorization: Bearer <token> en respectant le quota X-RateLimit-Remaining",
                    "Appeler directement les routes protégées sans en-tête et ignorer les erreurs 401 et 429",
                    "Envoyer le mot de passe en clair dans chaque URL GET",
                    "Redémarrer le serveur avant chaque requête"
                ],
                "correct_index": 0,
                "explanation": "Le client obtient d'abord son jeton temporaire signé, l'inclut dans `Authorization: Bearer ...` pour ses appels ultérieurs, et respecte l'en-tête `Retry-After` si un statut `429` survient."
            }
        ]
    }
}
