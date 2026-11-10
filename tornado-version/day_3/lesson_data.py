import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_3_DATA = {
    "day_number": 3,
    "folder": "day_3",
    "badge": "Jour 3 • CRUD Tornado, Validation RFC 7807, Idempotence & SQLite",
    "title": "Ingénierie CRUD avec Tornado : Validation RFC 7807, PUT vs PATCH, Idempotency-Key, write_error() & SQLite ACID",
    "goal": "Implémenter une validation stricte des entrées avec retour RFC 7807 (422) dans un RequestHandler, maîtriser def put() vs def patch() et la sécurisation de POST par Idempotency-Key, intercepter globalement toutes les erreurs en JSON via write_error() et default_handler_class, et gérer la persistance SQLite protégée contre l'injection SQL.",
    "starter_filename": "day_3/02_api_crud_sqlite.py",
    "files": [
        "day_3/01_api_crud_memoire.py",
        "day_3/03_put_patch_et_idempotence.py",
        "day_3/04_gestion_erreurs_globale.py",
        "day_3/02_api_crud_sqlite.py",
    ],
    "lessons": [
        {
            "id": "d3-l1",
            "file": "day_3/01_api_crud_memoire.py",
            "title": "3.1 — Validation Stricte des Charges Utiles JSON & Format d'Erreur Normalisé RFC 7807 (`self.set_status(422)`)",
            "duration": "60 min",
            "analogy": {
                "title": "Le contrôle technique qui liste précisément chaque anomalie constatée",
                "text": "Si un client soumet un formulaire JSON comportant 3 erreurs (titre trop court, durée négative, salle manquante), une API médiocre répond simplement `{\"erreur\": \"Données invalides\"}` sans dire quel champ pose problème. Une API professionnelle applique le standard international **RFC 7807 (`Problem Details for HTTP APIs`)** en retournant le détail exact par champ avec `self.set_status(422)` et `Content-Type: application/problem+json`."
            },
            "explanation": [
                "**1. Pourquoi ne jamais faire confiance au client (`Never Trust User Input`)** : Même si votre interface Web possède des contrôles JavaScript, n'importe qui peut appeler votre API directement avec `curl` ou un script Python en envoyant `{\"duree_jours\": -999, \"titre\": \"\"}`. La validation côté serveur dans `def post(self):` est **obligatoire**.",
                "**2. Les 4 niveaux de validation d'un Payload JSON dans Tornado** :\n  1. **Présence et syntaxe JSON** : `corps = tornado.escape.json_decode(self.request.body)` dans un bloc `try / except ValueError`.\n  2. **Champs obligatoires** : Le champ requis est-il présent et non vide après `.strip()` ?\n  3. **Contrôle de type** : `duree_jours` est-il bien convertible en entier `int` ?\n  4. **Contraintes métier (Domain Validation)** : `duree_jours` est-il compris entre `1` et `30` ? Le titre fait-il entre `3` et `120` caractères ?",
                "**3. Différence entre `400 Bad Request` et `422 Unprocessable Entity`** :\n  - `400` : Le JSON est syntaxiquement cassé (`ValueError` lors de `json_decode`).\n  - `422` : Le JSON est syntaxiquement valide, mais ses valeurs violent les règles métier (ex. durée de `-5` jours)."
            ],
            "code": _read("01_api_crud_memoire.py"),
            "line_explanations": [
                {"lines": "22-39", "text": "Fonction dédiée `valider_payload_formation(corps)` qui accumule toutes les anomalies par nom de champ dans le dictionnaire `erreurs`."},
                {"lines": "46-63", "text": "Dans `FormationsCollectionHandler.post`, décode `self.request.body` et retourne un objet conforme à la RFC 7807 avec `self.set_status(422)` si une anomalie est détectée."},
                {"lines": "65-74", "text": "Si la validation réussit, insère l'entité, appelle `self.set_status(201)` et sérialise la réponse avec `self.write(...)`."}
            ],
            "sandbox_preset": {
                "label": "Tester la création : POST /api/sandbox/formations",
                "method": "POST",
                "url": "/api/sandbox/formations",
                "body": '{\n  "titre": "Sécurité des Services Web & Tokens",\n  "formateur": "Intervenant ISGP",\n  "duree_jours": 4,\n  "salle": "Laboratoire 2"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez `day_3/01_api_crud_memoire.py` pour observer le rejet RFC 7807 (422) puis la création (201) :",
                "initial_code": _read("01_api_crud_memoire.py")
            },
            "vscode_instructions": {
                "filename": "day_3/01_api_crud_memoire.py",
                "steps": [
                    "Ouvrir `day_3/01_api_crud_memoire.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_3/01_api_crud_memoire.py`."
                ]
            }
        },
        {
            "id": "d3-l2",
            "file": "day_3/03_put_patch_et_idempotence.py",
            "title": "3.2 — `def put(self, id)` (Remplacement Intégral) vs `def patch(self, id)` (Modification Partielle) & `Idempotency-Key`",
            "duration": "60 min",
            "analogy": {
                "title": "Remplacer toute une fiche (PUT) vs Corriger une seule ligne au stylo (PATCH) vs Numéro de transaction unique (Idempotency-Key)",
                "text": "Dans un `RequestHandler` Tornado, les méthodes `def put(self, id_str):` et `def patch(self, id_str):` cohabitent proprement dans la même classe `FormationItemHandler`.\nEt sur `FormationsIdempotentHandler.post(self)`, la vérification de l'en-tête `Idempotency-Key` empêche toute création en doublon en cas de coupure réseau."
            },
            "explanation": [
                "**1. `def put(self, id)` vs `def patch(self, id)` (RFC 5789)** :\n  - **`PUT /api/v1/formations/1`** effectue un **remplacement complet** de l'enregistrement n°1. Le client doit envoyer l'intégralité des champs de la ressource (`titre`, `duree_jours`, `salle`).\n  - **`PATCH /api/v1/formations/1`** effectue une **mise à jour partielle**. Le client peut envoyer uniquement `{\"salle\": \"Amphi ISGP\"}` : seule la colonne `salle` est modifiée !",
                "**2. Rendre `POST` idempotent grâce à l'en-tête `Idempotency-Key` (Standard Stripe / Adyen / Banques)** :\n  - Le client génère un identifiant unique (`Idempotency-Key: idem-2026-001`) lu via `self.request.headers.get('Idempotency-Key')`.\n  - Le serveur mémorise la réponse associée à cette clé : si le client renvoie la même clé suite à un timeout réseau, Tornado lui renvoie la réponse mémorisée (`200 OK`) sans recréer l'objet !"
            ],
            "code": _read("03_put_patch_et_idempotence.py"),
            "line_explanations": [
                {"lines": "23-31", "text": "Contrôle de l'en-tête `Idempotency-Key` dans `post(self)` : si la clé a déjà été traitée, renvoie immédiatement l'objet précédemment créé (`rejoue_sans_doublon: True`)."},
                {"lines": "53-70", "text": "Méthode `def put(self, id_str):` : exige la présence de tous les attributs (`titre`, `duree_jours`, `salle`) et remplace l'enregistrement complet."},
                {"lines": "72-83", "text": "Méthode `def patch(self, id_str):` : met à jour uniquement les clés présentes dans le JSON envoyé."}
            ],
            "python_runner": {
                "prompt": "Exécutez `day_3/03_put_patch_et_idempotence.py` pour observer la protection anti-doublon Idempotency-Key et PATCH :",
                "initial_code": _read("03_put_patch_et_idempotence.py")
            },
            "vscode_instructions": {
                "filename": "day_3/03_put_patch_et_idempotence.py",
                "steps": [
                    "Ouvrir `day_3/03_put_patch_et_idempotence.py` dans l'éditeur.",
                    "Exécuter `.venv/bin/python day_3/03_put_patch_et_idempotence.py`."
                ]
            }
        },
        {
            "id": "d3-l3",
            "file": "day_3/04_gestion_erreurs_globale.py",
            "title": "3.3 — Gestion Globale des Erreurs dans Tornado : `write_error(self, status_code, **kwargs)` & `default_handler_class`",
            "duration": "50 min",
            "analogy": {
                "title": "Un traducteur diplomatique qui répond toujours dans la langue attendue (JSON), même en cas d'incident",
                "text": "Par défaut, lorsqu'un client appelle une URL inexistante (`404`), utilise une méthode non implémentée (`405`) ou déclenche une exception Python (`500`), Tornado génère une page HTML `<html><title>404: Not Found</title>...</html>`.\nDans une API REST Tornado professionnelle, on surcharge **`write_error(self, status_code, **kwargs)`** dans une classe de base `JsonApiBaseHandler` et on configure **`default_handler_class=NotFoundJsonHandler`** dans `tornado.web.Application` !"
            },
            "explanation": [
                "**1. La méthode `write_error(self, status_code, **kwargs)` de `tornado.web.RequestHandler`** :\n  - Chaque fois qu'une exception `tornado.web.HTTPError(code)` ou une exception Python non gérée (`ZeroDivisionError`, `KeyError`, etc.) survient pendant `prepare()` ou `get()/post()`, Tornado appelle automatiquement `self.write_error(status_code, **kwargs)`.\n  - En la surchargeant dans `JsonApiBaseHandler`, vous garantissez que `400`, `404`, `405` et `500` renvoient **toujours du JSON propre** via `self.finish({...})`.",
                "**2. Le paramètre `default_handler_class` de `tornado.web.Application`** :\n  - Lorsqu'aucune expression régulière de la table de routage ne correspond à l'URL demandée, Tornado délègue la requête à `default_handler_class` (`NotFoundJsonHandler`), qui lève `raise tornado.web.HTTPError(404)` et déclenche votre `write_error(404)` en JSON !"
            ],
            "code": _read("04_gestion_erreurs_globale.py"),
            "line_explanations": [
                {"lines": "17-45", "text": "`JsonApiBaseHandler.write_error` : intercepte les codes `404`, `405` et `>= 500` (avec inspection de `kwargs.get('exc_info')` côté serveur) et renvoie une réponse JSON via `self.finish({...})`."},
                {"lines": "49-51", "text": "`NotFoundJsonHandler` : utilisé comme `default_handler_class` pour intercepter toute URL inconnue en JSON."},
                {"lines": "61-64", "text": "Enregistrement de `default_handler_class=NotFoundJsonHandler` dans `tornado.web.Application`."}
            ],
            "python_runner": {
                "prompt": "Exécutez `day_3/04_gestion_erreurs_globale.py` pour tester les réponses JSON sur 404, 405 et 500 (ZeroDivisionError) :",
                "initial_code": _read("04_gestion_erreurs_globale.py")
            },
            "vscode_instructions": {
                "filename": "day_3/04_gestion_erreurs_globale.py",
                "steps": [
                    "Ouvrir `day_3/04_gestion_erreurs_globale.py`.",
                    "Exécuter `.venv/bin/python day_3/04_gestion_erreurs_globale.py`."
                ]
            }
        },
        {
            "id": "d3-l4",
            "file": "day_3/02_api_crud_sqlite.py",
            "title": "3.4 — Persistance Relationnelle SQLite, Transactions ACID & Parade contre l'Injection SQL (`?`)",
            "duration": "65 min",
            "analogy": {
                "title": "Séparer le plan d'exécution SQL des données saisies par l'utilisateur",
                "text": "L'**Injection SQL** fait partie des failles de sécurité les plus critiques au monde (OWASP Top 10). Elle survient lorsqu'un développeur construit sa requête SQL en collant directement la variable du client avec un `+` ou une `f-string`. Si le client envoie `\"Alger' OR '1'='1\"`, il détourne l'ordre SQL et peut lire ou détruire toute la base !"
            },
            "explanation": [
                "**1. Pourquoi les Requêtes Paramétrées (`?`) neutralisent 100% des Injections SQL** :\n  - **DANGEREUX (À proscrire absolument)** : `conn.execute(f\"SELECT * FROM formations WHERE salle = '{salle}'\")`.\n  - **SÉCURISÉ (Requête paramétrée)** : `conn.execute(\"SELECT * FROM formations WHERE salle = ?\", (salle,))`.\n  - Avec le point d'interrogation `?`, le moteur SQLite compile d'abord la structure de l'ordre SQL, puis insère la valeur de `salle` comme une simple donnée inerte.",
                "**2. Sécurité JSON de `self.write()` sur les listes dans Tornado** :\n  - Par sécurité historique contre le détournement de tableaux JSON, `self.write()` dans Tornado accepte directement un `dict`, mais refuse une `list` brute (sauf si on l'enveloppe dans un `dict` `{'data': [...]}` ou si on sérialise explicitement avec `json.dumps([...])` + `self.set_header('Content-Type', 'application/json; charset=UTF-8')`)."
            ],
            "code": _read("02_api_crud_sqlite.py"),
            "line_explanations": [
                {"lines": "30-46", "text": "Initialisation du schéma SQLite avec clé primaire auto-incrémentée (`INTEGER PRIMARY KEY AUTOINCREMENT`)."},
                {"lines": "53-81", "text": "`CatalogueSqlitePageHandler` : traite le formulaire HTML (`self.get_body_argument`) par requête `INSERT` paramétrée `?` et rend `day_3/templates/catalogue_sqlite.html`."},
                {"lines": "85-120", "text": "`FormationsSqliteApiHandler` : gère `GET /api/formations` et `POST /api/formations` avec requête paramétrée `?` et retour `201 Created`."},
                {"lines": "124-152", "text": "`FormationSqliteDetailHandler` : gère `PUT` et `DELETE` sur `/api/formations/([0-9]+)` avec vérification de `cur.rowcount`."}
            ],
            "sandbox_preset": {
                "label": "Tester PUT /api/sandbox/formations/1 sur la base SQLite",
                "method": "PUT",
                "url": "/api/sandbox/formations/1",
                "body": '{\n  "titre": "Architecture des APIs REST Tornado (Niveau Avancé)",\n  "salle": "Amphithéâtre ISGP"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez `day_3/02_api_crud_sqlite.py` pour tester l'insertion SQLite paramétrée et la lecture JSON :",
                "initial_code": _read("02_api_crud_sqlite.py")
            },
            "vscode_instructions": {
                "filename": "day_3/02_api_crud_sqlite.py",
                "steps": [
                    "Ouvrir `day_3/02_api_crud_sqlite.py` dans l'éditeur.",
                    "Exécuter `.venv/bin/python day_3/02_api_crud_sqlite.py`."
                ]
            }
        }
    ]
}
