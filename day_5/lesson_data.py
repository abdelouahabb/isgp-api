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
            "title": "5.2 — Architecture Modulaire : `Blueprints`, Application Factory (`create_app`) & Sondes `/api/health`",
            "duration": "60 min",
            "analogy": {
                "title": "Passer d'un studio d'une seule pièce à un immeuble structuré par étages",
                "text": "Écrire 5 routes dans un seul fichier `app.py` est parfait pour apprendre. Mais une véritable API d'entreprise compte souvent 80 à 200 routes réparties entre plusieurs domaines (authentification, facturation, catalogue, reporting). Si tout est dans `app.py`, le fichier atteint 5 000 lignes et devient impossible à maintenir en équipe.\nEn Flask, on découpe l'API en modules autonomes appelés **`Blueprints`** (Plans d'architecte), que l'on assemble au démarrage dans une fonction **`create_app()`**."
            },
            "explanation": [
                "**Le concept de `Blueprint` Flask** : Un `Blueprint` regroupe les routes d'un même domaine métier avec un préfixe d'URL commun (ex: `url_prefix='/api/v1/formations'`). Chaque domaine vit dans son propre fichier Python (`routes/formations.py`, `routes/auth.py`, `routes/sante.py`).",
                "**Le patron de conception *Application Factory* (`def create_app():`)** : Au lieu de créer la variable globale `app = Flask(__name__)` au sommet du fichier, on l'encapsule dans une fonction `create_app()`. Cela permet d'instancier plusieurs configurations de l'API (une instance connectée à une base de test en mémoire pour les tests automatisés, et une instance connectée à la base de production).",
                "**Versionnement d'API (`/api/v1/...`, `/api/v2/...`)** : Grâce aux Blueprints, vous pouvez maintenir simultanément `v1` (pour vos clients existants) et `v2` (avec un nouveau format JSON) dans la même application sans casser les intégrations existantes.",
                "**Sondes de supervision (*Healthchecks* : `/api/health/live` & `/api/health/ready`)** : En production (Docker, Kubernetes, Load Balancer Nginx/HAProxy), l'infrastructure interroge toutes les 10 secondes deux routes spéciales :\n  - **`/api/health/live` (*Liveness*)** : Vérifie que le processus Python n'est pas gelé (`200 OK`).\n  - **`/api/health/ready` (*Readiness*)** : Vérifie que la base de données répond bien avant d'envoyer du trafic client vers ce serveur (`200 OK` ou `503 Service Unavailable`)."
            ],
            "code": _read("03_architecture_blueprints.py"),
            "line_explanations": [
                {"lines": "12-16", "text": "Création du Blueprint `formations_bp` préfixé automatiquement par `/api/v1/formations`."},
                {"lines": "19-31", "text": "Création du Blueprint `sante_bp` exposant les sondes standards `/api/health/live` et `/api/health/ready`."},
                {"lines": "34-38", "text": "Fonction *Application Factory* `create_app()` enregistrant les Blueprints via `register_blueprint()`."}
            ],
            "python_runner": {
                "prompt": "Testez l'assemblage des Blueprints et interrogez les routes modulaires en mémoire :",
                "initial_code": '''from flask import Blueprint, Flask, jsonify

bp_v1 = Blueprint("v1", __name__, url_prefix="/api/v1")
bp_health = Blueprint("health", __name__, url_prefix="/api/health")

@bp_v1.route("/formations")
def lister():
    return jsonify({"version": "v1", "formations": ["Architecture API", "Sécurité JWT"]})

@bp_health.route("/ready")
def readiness():
    return jsonify({"statut": "READY", "database": "CONNECTED"}), 200

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp_v1)
    app.register_blueprint(bp_health)
    return app

app = create_app()
print("Routes enregistrées dans l'Application Factory :")
for regle in app.url_map.iter_rules():
    if regle.endpoint != "static":
        print(f" - {regle.rule:25s} -> endpoint: {regle.endpoint}")'''
            },
            "vscode_instructions": {
                "filename": "day_5/03_architecture_blueprints.py",
                "steps": [
                    "Ouvrir `day_5/03_architecture_blueprints.py` dans l'éditeur.",
                    "Observer comment `url_prefix` évite de répéter `/api/v1/formations` sur chaque décorateur `@route`."
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
                {"lines": "10-17", "text": "Route `POST /api/calcul-taxe` validant que `montant_ht` est un nombre positif (`422` sinon) et calculant la TVA à 19%."},
                {"lines": "22", "text": "`app.test_client()` crée un client de test interne qui dialogue directement avec Flask en mémoire sans ouvrir de port TCP."},
                {"lines": "25-33", "text": "Vérifie automatiquement par `assert` à la fois le cas nominal (`200 OK`) et le cas d'erreur de validation (`422 Unprocessable Entity`)."},
                {"lines": "38", "text": "Commande standard de mise en production avec **Gunicorn** (4 workers parallèles sur le port 8000)."}
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
            "file": "day_5/02_comparaison_flask_fastapi.py",
            "title": "5.4 — Perspective Architecturale : Flask (WSGI Explicite) vs FastAPI (ASGI Déclaratif & Pydantic)",
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
