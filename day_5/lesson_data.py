import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_5_DATA = {
    "day_number": 5,
    "folder": "day_5",
    "badge": "Jour 5 • Architecture, Tests, Production & FastAPI",
    "title": "Architecture Modulaire (Blueprints), Client Résilient, Tests Automatisés, Mise en Production WSGI & FastAPI",
    "goal": "Savoir consommer une API de manière résiliente (Timeouts, Retries), découper une grande API en modules (Blueprints, Application Factory, Healthchecks), automatiser les tests avec test_client(), déployer en production avec un serveur WSGI (Gunicorn) et comparer Flask avec FastAPI.",
    "starter_filename": "day_5/03_architecture_blueprints.py",
    "files": [
        "day_5/01_client_python_auth.py",
        "day_5/03_architecture_blueprints.py",
        "day_5/04_tests_et_production.py",
        "day_5/05_swagger_openapi_ui.py",
        "day_5/02_comparaison_flask_fastapi.py",
    ],
    "lessons": [
        {
            "id": "d5-l1",
            "file": "day_5/01_client_python_auth.py",
            "title": "5.1 — Ingénierie du Client HTTP Résilient : Timeouts, Gestion d'Erreurs & Exponential Backoff",
            "duration": "55 min",
            "analogy": {
                "title": "Ne jamais appeler le réseau sans chronomètre (Timeout)",
                "text": "Lorsqu'un serveur A appelle l'API d'un serveur B (par exemple une passerelle de paiement ou un service partenaire), le réseau peut ralentir ou le serveur B peut geler sans fermer la connexion TCP.\nSi votre client Python appelle `urlopen()` ou `requests.get()` **sans paramètre `timeout`**, votre processus restera bloqué indéfiniment en attendant une réponse qui ne viendra jamais ! En quelques minutes, tous les processus de votre serveur A seront figés : c'est une **panne en cascade** (*Cascading Failure*)."
            },
            "explanation": [
                "**Règle d'or n°1 — Toujours imposer un `timeout` explicite** : Que ce soit avec `urllib.request.urlopen(..., timeout=5.0)` ou `requests.get(..., timeout=(2.0, 5.0))`, un appel réseau doit toujours abandonner proprement au bout de quelques secondes.",
                "**Règle d'or n°2 — Intercepter les codes `4xx` et `5xx` (`HTTPError`)** : En Python, `urllib.request` lève une exception `urllib.error.HTTPError` dès que le statut HTTP est `>= 400`. Il faut l'intercepter par `try / except` pour lire le corps JSON d'erreur (`err.read()`).",
                "**Règle d'or n°3 — *Exponential Backoff* face aux erreurs temporaires (`429`, `502`, `503`, `504`)** : Si l'API distante renvoie `503 Service Unavailable`, il ne faut surtout pas réessayer immédiatement en boucle (ce qui aggraverait sa panne). On applique un **recul exponentiel** : attendre `1s` avant le 1er réessai, puis `2s`, puis `4s`, puis `8s` (ou lire l'en-tête `Retry-After` en cas de `429`).",
                "**Depuis un navigateur Web / PWA (JavaScript `fetch`)** : Utiliser `AbortSignal.timeout(5000)` et passer l'en-tête `Authorization: 'Bearer ' + token`."
            ],
            "code": _read("01_client_python_auth.py"),
            "line_explanations": [
                {"lines": "12-28", "text": "Fonction générique `appeler_api_json` imposant un `timeout=5.0` et capturant `urllib.error.HTTPError` pour extraire le statut et le JSON d'erreur."},
                {"lines": "31-37", "text": "Étape 1 : Authentification `POST /api/sandbox/auth/token` pour obtenir l'`access_token`."},
                {"lines": "40-45", "text": "Étape 2 : Appel `GET /api/sandbox/auth/profil` en injectant l'en-tête `Authorization: Bearer <mon_token>`."}
            ],
            "python_runner": {
                "prompt": "Exécutez ce client résilient en direct contre le serveur du laboratoire (`day_5/01_client_python_auth.py`) :",
                "initial_code": _read("01_client_python_auth.py")
            },
            "vscode_instructions": {
                "filename": "day_5/01_client_python_auth.py",
                "steps": [
                    "Ouvrir `day_5/01_client_python_auth.py` dans l'éditeur.",
                    "Exécuter `.venv/bin/python day_5/01_client_python_auth.py` pendant que le serveur principal tourne."
                ]
            }
        },
        {
            "id": "d5-l2",
            "file": "day_5/03_architecture_blueprints.py",
            "title": "5.2 — Architecture Modulaire (`Blueprints`), Cycle de Vie d'API (`/api/v1` vs `/api/v2`, Breaking Changes, RFC 8594) & Sondes `/api/health`",
            "duration": "75 min",
            "analogy": {
                "title": "Pourquoi voit-on presque toujours `/api/v1` et si rarement `/api/v2` ?",
                "text": "Une question revient systématiquement chez les ingénieurs : *« Pourquoi 90 % des APIs mondiales (OpenAI `/v1/chat/completions`, Stripe `/v1/charges`, Kubernetes `/apis/apps/v1`) restent-elles sur `v1` pendant 5 à 10 ans, et pourquoi met-on quand même `/v1` dès le premier jour ? »*\nLa réponse tient en deux principes fondamentaux :\n1. **La Loi de Postel (*Tolerant Reader*)** : Ajouter un nouveau champ JSON ou une nouvelle route est une **évolution rétrocompatible (*Non-Breaking Change*)**. Les clients existants ignorent simplement les clés qu'ils ne connaissent pas, ce qui permet de faire évoluer `v1` pendant des années sans jamais créer de `v2`.\n2. **L'Assurance-Vie Architecturale** : Si un jour vous devez modifier le **type** d'un champ existant (ex: remplacer `\"duree\": 5` par `\"duree\": {\"valeur\": 5, \"unite\": \"jours\"}`) ou renommer une clé, c'est une **rupture de contrat (*Breaking Change*)**. Avoir placé `/api/v1` dès le Jour 1 vous permet alors de monter un second Blueprint `/api/v2` en parallèle sans faire planter les 50 000 applications mobiles déjà installées !"
            },
            "explanation": [
                "**1. Évolution Rétrocompatible (*Non-Breaking* -> rester en `v1`) vs Rupture de Contrat (*Breaking Change* -> créer `v2`)** :\n  - **Rétrocompatible (Rester en `/api/v1`)** : Ajouter un nouveau champ dans la réponse JSON, ajouter une nouvelle route (`GET /api/v1/certificats`), ou ajouter un paramètre de requête optionnel (`?lang=fr`).\n  - **Rupture de Contrat (Exige `/api/v2`)** : Supprimer ou renommer un champ JSON (`intitule` -> `titre`), changer le type d'une clé (`duree: 5` (int) -> `duree: {valeur: 5, unite: 'jours'}` (dict)), ou rendre obligatoire un nouveau champ à l'entrée d'un `POST`.",
                "**2. Coexistence de `/api/v1` et `/api/v2` grâce aux `Blueprints` Flask & Dépréciation RFC 8594** :\n  - On ne coupe **jamais** `/api/v1` du jour au lendemain lors de la sortie de `/api/v2` ! Les deux Blueprints (`formations_v1_bp` et `formations_v2_bp`) tournent **simultanément** dans `create_app()` en interrogeant la même couche métier.\n  - Sur le Blueprint `v1`, un hook `@formations_v1_bp.after_request` injecte les en-têtes officiels de dépréciation (**Norme IETF RFC 8594**) :\n    - `Deprecation: true` (signale que `v1` est obsolète)\n    - `Sunset: Thu, 31 Dec 2026 23:59:59 GMT` (date exacte d'extinction où `v1` renverra `410 Gone`)\n    - `Link: </api/v2/formations>; rel=\"successor-version\"` (indique l'URL de migration)",
                "**3. Les 4 Stratégies de Versionnement dans l'Industrie** :\n  - **Dans le chemin d'URI (`/api/v1/...`, `/api/v2/...`)** : Standard adopté par 80 % des APIs REST (OpenAI, Twilio, PayPal). Immédiatement lisible dans les logs, le navigateur et le routage Nginx (`location /api/v1/`).\n  - **Par en-tête de date (`X-API-Version: 2026-11-01` ou `Stripe-Version`)** : Utilisé par Stripe et GitHub pour figer le contrat à la date d'inscription du client tout en gardant une URL unique.\n  - **Par négociation de type MIME (`Accept: application/vnd.isgp.v2+json`)** : Approche REST pure (Content Negotiation).\n  - **Par paramètre de requête (`?version=2`)** : Simple mais déconseillé (complique la mise en cache HTTP).",
                "**4. Le patron *Application Factory* (`create_app()`) & Sondes de Supervision (`/api/health/live` & `/ready`)** :\n  - `def create_app():` assemble proprement tous les Blueprints (`web_bp`, `formations_v1_bp`, `formations_v2_bp`, `sante_bp`) sans variable globale circulaire.\n  - `/api/health/live` (*Liveness*) vérifie que le processus Python tourne (`200 OK`), tandis que `/api/health/ready` (*Readiness*) vérifie que la base SQLite/SQL est joignable avant que Nginx n'envoie du trafic."
            ],
            "code": _read("03_architecture_blueprints.py"),
            "line_explanations": [
                {"lines": "17-22", "text": "Source de données métier unique (`CATALOGUE_METIER`) partagée entre le portail Web Jinja2, l'API `v1` et l'API `v2`."},
                {"lines": "24-40", "text": "Blueprint Web Jinja2 `web_bp` (`/portail`) servant le template `day_5/templates/portail_blueprint.html`."},
                {"lines": "45-64", "text": "Blueprint `formations_v1_bp` (`/api/v1/formations`) conservant le schéma plat historique (`duree: 5`) et injectant les en-têtes RFC 8594 (`Deprecation: true`, `Sunset`, `Link`)."},
                {"lines": "69-95", "text": "Blueprint `formations_v2_bp` (`/api/v2/formations`) exposant le nouveau schéma structuré (`duree: {valeur, unite, heures_pedagogiques}`, enveloppe `meta` + `data` + `links`)."},
                {"lines": "98-118", "text": "Blueprint `sante_bp` (`/api/health/live` & `/ready`) et fonction `create_app()` enregistrant les 4 Blueprints en parallèle."}
            ],
            "sandbox_preset": {
                "label": "Comparer API v1 (Dépréciée RFC 8594) vs API v2 : GET /api/v1/sandbox/formations",
                "method": "GET",
                "url": "/api/v1/sandbox/formations",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_5/03_architecture_blueprints.py` pour comparer en direct les en-têtes et schémas JSON de `/api/v1/formations` et `/api/v2/formations` :",
                "initial_code": _read("03_architecture_blueprints.py")
            },
            "vscode_instructions": {
                "filename": "day_5/03_architecture_blueprints.py",
                "steps": [
                    "Ouvrir `day_5/03_architecture_blueprints.py` dans l'éditeur.",
                    "Comparer la structure du champ `duree` entre `lister_formations_v1()` (entier `5`) et `lister_formations_v2()` (objet structuré) et observer les en-têtes `Deprecation` et `Sunset`."
                ]
            }
        },
        {
            "id": "d5-l3",
            "file": "day_5/04_tests_et_production.py",
            "title": "5.3 — Tests Automatisés (`test_client`), Spécification OpenAPI & Déploiement Production WSGI (`Gunicorn`)",
            "duration": "65 min",
            "analogy": {
                "title": "Pourquoi `app.run()` est strictement interdit en production",
                "text": "Lorsque vous lancez `python app.py`, Flask affiche un avertissement rouge : *\"WARNING: This is a development server. Do not use it in a production deployment.\"*\nPourquoi ? Parce que le serveur intégré de Flask est conçu pour le débogage local : il traite les requêtes simplement et n'est ni dimensionné ni durci pour encaisser des centaines de connexions concurrentes ou résister aux attaques réseau lentes (*Slowloris*).\nEn production, on place toujours un **serveur WSGI industriel** (**Gunicorn** ou **uWSGI**) devant Flask, lui-même protégé par un **Reverse Proxy** (**Nginx**, **Caddy** ou **Cloudflare**)."
            },
            "explanation": [
                "**Architecture de Déploiement en Production (`Client -> Nginx -> Gunicorn -> Flask`)** :\n  1. **Reverse Proxy (`Nginx` / `Caddy`)** : Gère le chiffrement HTTPS (TLS), les certificats SSL, la compression Gzip et bloque les connexions malformées.\n  2. **Serveur d'Application WSGI (`Gunicorn`)** : Démarre plusieurs processus Python parallèles appelés **Workers** (`gunicorn -w 4 -b 0.0.0.0:8000 app:app`). Si un worker traite un calcul long, les 3 autres workers continuent de répondre instantanément aux autres clients !\n  3. **Application Flask (`app`)** : Exécute votre logique métier Python.",
                "**Tester son API automatiquement sans serveur réseau (`app.test_client()`)** : Tester manuellement 30 routes à la souris après chaque modification du code est lent et source d'oublis. Flask fournit `app.test_client()`, qui simule des requêtes HTTP (`GET`, `POST`, `PUT`, `DELETE`) directement en mémoire en quelques millisecondes et permet de vérifier par `assert` que le statut HTTP et le JSON retourné sont exacts.",
                "**Documenter le contrat avec OpenAPI 3.0 (Swagger)** : Une API professionnelle publie un fichier descriptif standardisé (`openapi.json` ou `openapi.yaml`) qui liste chaque URL, chaque méthode, les en-têtes requis et le schéma JSON exact des requêtes et réponses."
            ],
            "code": _read("04_tests_et_production.py"),
            "line_explanations": [
                {"lines": "13-20", "text": "Route API JSON `POST /api/calcul-taxe` lisant `request.get_json()` et validant `montant_ht` (`422` si négatif)."},
                {"lines": "24-32", "text": "Route Formulaire HTML `POST /formulaire-taxe` lisant `request.form.get('montant_ht', type=float)` et rendant `day_5/templates/resultat_taxe.html`."},
                {"lines": "36-46", "text": "Tests 1 et 2 : Vérification automatisée par `assert` de la route API JSON (`client.post(..., json={...})`)."},
                {"lines": "49-53", "text": "Test 3 : Vérification automatisée de la soumission du formulaire HTML (`client.post(..., data={...})`) et du rendu Jinja2."}
            ],
            "python_runner": {
                "prompt": "Exécutez la suite de tests automatisés `app.test_client()` en direct :",
                "initial_code": _read("04_tests_et_production.py")
            },
            "vscode_instructions": {
                "filename": "day_5/04_tests_et_production.py",
                "steps": [
                    "Ouvrir `day_5/04_tests_et_production.py` dans l'éditeur.",
                    "Ajouter un 3ème test vérifiant le comportement si le corps JSON est vide `{}`."
                ]
            }
        },
        {
            "id": "d5-l4",
            "file": "day_5/05_swagger_openapi_ui.py",
            "title": "5.4 — Documentation Interactive & Contrat d'API : Swagger UI (`/api/docs`) & OpenAPI 3.0 (`/api/openapi.json`)",
            "duration": "60 min",
            "analogy": {
                "title": "Les plans d'architecte cotés (OpenAPI) et la maquette interactive 3D visitable (Swagger UI)",
                "text": "Une API sans documentation à jour est une boîte noire inutilisable : les développeurs frontaux (React, Mobile) et les partenaires passent alors des heures à deviner les noms des champs JSON ou les en-têtes requis.\nLa norme mondiale **OpenAPI 3.0** est le plan d'architecte formel (en JSON ou YAML) de votre API, et **Swagger UI** est le portail Web généré automatiquement à partir de ce plan, permettant à n'importe quel développeur de lire le contrat et de cliquer sur **« Try it out »** ou **« Authorize »** directement dans son navigateur !"
            },
            "explanation": [
                "**1. Quelle est la différence exacte entre `Swagger` et `OpenAPI` ?**\n  - Jusqu'en 2015, la norme s'appelait *Swagger 2.0*.\n  - Depuis la version `3.0`, la **norme officielle** (gérée par la Linux Foundation / OpenAPI Initiative) s'appelle **OpenAPI Specification (OAS 3.0 / 3.1)** : c'est le fichier de contrat `/api/openapi.json` ou `openapi.yaml`.\n  - **Swagger** (SmartBear) désigne désormais les **outils** qui exploitent ce fichier : **Swagger UI** (portail Web interactif `/api/docs`), **Swagger Editor** (éditeur YAML/JSON avec aperçu temps réel) et **Swagger Codegen** (générateur automatique de SDK clients).",
                "**2. Les 5 blocs fondamentaux d'un document OpenAPI 3.0** :\n  - `openapi: '3.0.3'` & `info` : Titre, version sémantique (`1.0.0`) et description de l'API.\n  - `servers` : Liste des URLs de base (Développement local `http://127.0.0.1:5000`, Production `https://api.isgp.dz`).\n  - `paths` : Liste toutes les routes (`/api/v1/formations`, `/api/v1/formations/{id}` avec accolades `{id}`), leurs verbes HTTP (`get`, `post`, `put`, `delete`), paramètres (`query`, `path`, `header`), corps attendus (`requestBody`) et codes de retour (`responses`).\n  - `components.schemas` : Dictionnaire des modèles JSON réutilisables via `$ref: '#/components/schemas/Formation'` (évite toute duplication).\n  - `components.securitySchemes` : Configure le célèbre bouton cadenas **« Authorize »** de Swagger UI pour tester les routes protégées par **`BearerAuth` (JWT)** ou **`ApiKeyAuth` (`X-API-Key`)**.",
                "**3. Les deux approches en entreprise : *Code-First* vs *Design-First (Contract-First)*** :\n  - **Code-First** : On écrit le code Python (Flask avec `Flasgger` / `Flask-Smorest` / `APIFlask`, ou FastAPI) et le serveur génère automatiquement `/api/openapi.json`.\n  - **Design-First** : L'architecte rédige d'abord le contrat `openapi.yaml` dans Swagger Editor ; l'équipe Mobile/React et l'équipe Backend Python peuvent alors travailler simultanément sans s'attendre."
            ],
            "code": _read("05_swagger_openapi_ui.py"),
            "line_explanations": [
                {"lines": "26-50", "text": "En-tête du contrat OpenAPI 3.0.3 (`info`, `servers`, `tags`) définissant l'identité et les environnements de l'API."},
                {"lines": "52-66", "text": "`securitySchemes` configure les deux cadenas d'authentification dans Swagger UI : `BearerAuth` (`Authorization: Bearer`) et `ApiKeyAuth` (`X-API-Key`)."},
                {"lines": "67-102", "text": "`components.schemas` centralise les schémas JSON (`Formation`, `FormationInput`, `ErreurRFC7807`) référencés ensuite par `$ref`."},
                {"lines": "104-190", "text": "`paths` documente chaque route, ses paramètres (`in: query`, `in: path`), le `requestBody` et les réponses HTTP (`200`, `201`, `401`, `404`, `422`)."},
                {"lines": "196-225", "text": "Routes Flask `/api/openapi.json` (contrat machine) et `/api/docs` (interface graphique interactive **Swagger UI**)."}
            ],
            "sandbox_preset": {
                "label": "Inspecter le Contrat OpenAPI 3.0 : GET /api/openapi.json",
                "method": "GET",
                "url": "/api/openapi.json",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez le générateur et validateur de contrat OpenAPI 3.0 (`day_5/05_swagger_openapi_ui.py`) :",
                "initial_code": _read("05_swagger_openapi_ui.py")
            },
            "vscode_instructions": {
                "filename": "day_5/05_swagger_openapi_ui.py",
                "steps": [
                    "Ouvrir `day_5/05_swagger_openapi_ui.py` dans VS Code ou Antigravity IDE.",
                    "Ouvrir également le portail interactif réel du laboratoire sur `http://127.0.0.1:5000/api/docs` pour tester Swagger UI en direct."
                ]
            }
        },
        {
            "id": "d5-l5",
            "file": "day_5/02_comparaison_flask_fastapi.py",
            "title": "5.5 — Perspective Architecturale : Flask (WSGI Explicite) vs FastAPI (ASGI Déclaratif & Pydantic)",
            "duration": "45 min",
            "analogy": {
                "title": "Boîte de vitesses manuelle (Flask) vs Boîte séquentielle pilotée par ordinateur (FastAPI)",
                "text": "Maintenant que vous maîtrisez chaque rouage interne d'une API (extraction du JSON, en-têtes HTTP, codes 200/201/401/403/422/429, signatures HMAC, Bearer Tokens et SQLite) grâce à l'approche explicite de **Flask**, vous êtes capable de comprendre instantanément **FastAPI** sans que rien ne vous paraisse « magique »."
            },
            "explanation": [
                "**Flask (Standard WSGI — Synchrone & Explicite)** :\n  - Contrôle total et transparent : vous voyez exactement d'où viennent les octets (`request.get_json()`, `request.headers`, `request.args`) et comment la réponse est construite (`jsonify()`).\n  - Idéal pour comprendre les fondations HTTP, construire des microservices maîtrisés, ou coupler une API avec des templates HTML/PWA.",
                "**FastAPI (Standard ASGI — Asynchrone & Déclaratif via Pydantic)** :\n  - S'appuie sur les **annotations de type Python** (`titre: str`, `duree_jours: int`) et la bibliothèque **Pydantic** pour valider automatiquement le JSON entrant et renvoyer `422 Unprocessable Entity` si un type est incorrect.\n  - Génère automatiquement l'interface interactive **Swagger UI (`/docs`)** et le schéma **OpenAPI (`/openapi.json`)** à partir des classes Python.\n  - S'exécute sur un serveur **ASGI** (**Uvicorn**) permettant de gérer nativement les fonctions asynchrones (`async def` / `await`) et les WebSockets à très haute concurrence.",
                "**Conclusion du Bootcamp** : Un ingénieur qui comprend le protocole HTTP, l'architecture REST, la sérialisation JSON, les transactions SQL et la sécurité par Tokens/Rate-Limit peut passer de Flask à FastAPI, Django REST Framework, Express.js ou Go en quelques heures, car **les fondamentaux d'ingénierie des APIs sont universels**."
            ],
            "code": _read("02_comparaison_flask_fastapi.py"),
            "line_explanations": [
                {"lines": "10-16", "text": "En Flask, la lecture du JSON (`request.get_json()`) et la validation conditionnelle du schéma sont écrites explicitement par le développeur."},
                {"lines": "25-27", "text": "En FastAPI, le modèle `FormationSchema(BaseModel)` déclare les contraintes de types et de bornes via `Pydantic`."},
                {"lines": "29-33", "text": "FastAPI valide les entrées avant d'exécuter la fonction et documente automatiquement la route dans `/docs`."}
            ],
            "python_runner": {
                "prompt": "Simulez le mécanisme de validation déclarative par annotations de types (inspiré de Pydantic / FastAPI) en pur Python :",
                "initial_code": '''def valider_par_annotations(schema_types, donnees_json):
    erreurs = []
    for champ, type_attendu in schema_types.items():
        if champ not in donnees_json:
            erreurs.append({"champ": champ, "erreur": "Champ obligatoire manquant"})
        elif not isinstance(donnees_json[champ], type_attendu):
            erreurs.append({
                "champ": champ,
                "erreur": f"Type attendu: {type_attendu.__name__}, reçu: {type(donnees_json[champ]).__name__}"
            })
    return (len(erreurs) == 0), erreurs

SCHEMA_FORMATION = {"titre": str, "duree_jours": int}

print("Test 1 (Valide)   :", valider_par_annotations(SCHEMA_FORMATION, {"titre": "API", "duree_jours": 5}))
print("Test 2 (Invalide) :", valider_par_annotations(SCHEMA_FORMATION, {"titre": "API", "duree_jours": "cinq"}))'''
            },
            "vscode_instructions": {
                "filename": "day_5/02_comparaison_flask_fastapi.py",
                "steps": [
                    "Consulter `day_5/02_comparaison_flask_fastapi.py` pour comparer côte à côte l'écriture d'une route POST en Flask et en FastAPI."
                ]
            }
        }
    ]
}
