import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_3_DATA = {
    "day_number": 3,
    "folder": "day_3",
    "badge": "Jour 3 • CRUD, Validation Pydantic v2, Idempotence & SQLite",
    "title": "Ingénierie CRUD : Validation Pydantic v2 & RFC 7807 (422), PUT vs PATCH, Idempotency-Key, @app.exception_handler & SQLite ACID",
    "goal": "Implémenter une validation déclarative stricte avec Pydantic v2 (BaseModel, Field, @field_validator) et retour RFC 7807 (422), maîtriser PUT vs PATCH (exclude_unset=True) et la sécurisation de POST par Idempotency-Key, intercepter globalement toutes les erreurs en JSON (@app.exception_handler), et gérer la persistance SQLite avec Depends(get_db).",
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
            "title": "3.1 — Validation Déclarative Pydantic v2 (`BaseModel`, `Field`, `@field_validator`) & Format RFC 7807 (`422 Unprocessable Entity`)",
            "duration": "60 min",
            "analogy": {
                "title": "Le contrôle technique automatisé par schéma (Pydantic v2) qui liste chaque anomalie constatée",
                "text": "Si un client soumet un formulaire JSON comportant 3 erreurs (titre trop court, durée négative, type erroné), une API médiocre répond simplement `{\"erreur\": \"Données invalides\"}`. Avec **FastAPI et Pydantic v2**, votre modèle `BaseModel` valide automatiquement tous les champs en une passe et vous pouvez formater toute `RequestValidationError` selon le standard international **RFC 7807 (`Problem Details for HTTP APIs`)** avec le code `422 Unprocessable Entity`."
            },
            "explanation": [
                "**1. Pourquoi ne jamais faire confiance au client (`Never Trust User Input`)** : Même si votre interface Web possède des contrôles JavaScript, n'importe qui peut appeler votre API directement avec `curl` ou un script Python en envoyant `{\"duree_jours\": -999, \"titre\": \"\"}`. La validation côté serveur via Pydantic est **obligatoire**.",
                "**2. Les 4 piliers de validation dans Pydantic v2 (`from pydantic import BaseModel, Field, field_validator`)** :\n  1. **Typage déclaratif** : `titre: str`, `duree_jours: int` (effectue la coercition ou rejette les types incompatibles).\n  2. **Contraintes `Field(...)`** : `Field(..., min_length=3, max_length=120)` pour les chaînes, `Field(default=5, ge=1, le=30)` pour les bornes numériques (`ge` = `>=`, `le` = `<=`).\n  3. **Validateur métier personnalisé (`@field_validator`)** : Permet d'exécuter une règle métier Python arbitraire (ex: `.strip()` et rejet d'un titre composé uniquement d'espaces).\n  4. **Interception `RequestValidationError` en RFC 7807** : Grâce à `@app.exception_handler(RequestValidationError)`, on enrichit la réponse `422` avec l'enveloppe normalisée `type`, `title`, `status`, `champs_en_erreur` et `detail`.",
                "**3. Différence entre `400 Bad Request` et `422 Unprocessable Entity`** :\n  - `400` : Le JSON est syntaxiquement cassé (accolade manquante) ou la requête est incompréhensible.\n  - `422` : Le JSON est syntaxiquement valide, mais ses valeurs violent le schéma Pydantic (ex. durée de `99` jours)."
            ],
            "code": _read("01_api_crud_memoire.py"),
            "line_explanations": [
                {"lines": "21-33", "text": "Modèle Pydantic v2 `FormationCreation(BaseModel)` combinant `Field(min_length=3, max_length=120)`, `Field(ge=1, le=30)` et `@field_validator('titre')`."},
                {"lines": "37-52", "text": "Gestionnaire `@app.exception_handler(RequestValidationError)` transformant les erreurs Pydantic en enveloppe normalisée RFC 7807 (`422 Unprocessable Entity`)."},
                {"lines": "60-69", "text": "Route `@app.post('/api/v1/formations', status_code=status.HTTP_201_CREATED)` recevant un `payload: FormationCreation` déjà validé et nettoyé."}
            ],
            "sandbox_preset": {
                "label": "Tester la création : POST /api/sandbox/formations",
                "method": "POST",
                "url": "/api/sandbox/formations",
                "body": '{\n  "titre": "Sécurité des Services Web & Tokens",\n  "formateur": "Intervenant ISGP",\n  "duree_jours": 4,\n  "salle": "Laboratoire 2"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez `day_3/01_api_crud_memoire.py` pour tester la validation Pydantic v2 (201 Created vs 422 RFC 7807) :",
                "initial_code": _read("01_api_crud_memoire.py")
            },
            "vscode_instructions": {
                "filename": "day_3/01_api_crud_memoire.py",
                "steps": [
                    "Ouvrir `day_3/01_api_crud_memoire.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_3/01_api_crud_memoire.py` et observer la réponse RFC 7807 générée sur l'entrée invalide."
                ]
            }
        },
        {
            "id": "d3-l2",
            "file": "day_3/03_put_patch_et_idempotence.py",
            "title": "3.2 — `PUT` vs `PATCH` (`model_dump(exclude_unset=True)`) & Sécurisation de `POST` par `Idempotency-Key`",
            "duration": "60 min",
            "analogy": {
                "title": "Remplacer toute une fiche (PUT) vs Corriger une seule ligne au stylo (PATCH) vs Numéro de transaction unique (Idempotency-Key)",
                "text": "En entretien technique comme en conception d'API, deux questions distinguent immédiatement un développeur averti :\n1. Quelle est la différence exacte entre `PUT` et `PATCH` dans FastAPI ?\n2. Comment empêcher qu'un client dont la connexion 4G clignote ne crée 2 fois la même commande en rejouant son `POST` ?"
            },
            "explanation": [
                "**1. `PUT` vs `PATCH` (RFC 5789) avec Pydantic v2** :\n  - **`PUT /api/v1/formations/{id}`** utilise un modèle complet `FormationComplete` : tous les champs sont remplacés.\n  - **`PATCH /api/v1/formations/{id}`** utilise un modèle aux champs `Optional` (`FormationPartielle`) combiné à **`payload.model_dump(exclude_unset=True)`** : seuls les champs explicitement envoyés par le client dans le JSON sont modifiés, les autres colonnes restent intactes !",
                "**2. Rendre `POST` idempotent grâce à l'en-tête `Idempotency-Key` (`Header(alias='Idempotency-Key')`)** :\n  - Par nature, `POST` n'est pas idempotent. Si un client mobile envoie `POST /api/commandes`, que le serveur crée la commande, mais que le Wi-Fi coupe avant que le téléphone ne reçoive la réponse `201`, le téléphone va renvoyer la requête `POST`.\n  - Pour éviter de créer un doublon, le client génère un identifiant unique (`Idempotency-Key: idem-001`) dans les Headers. Le serveur mémorise la réponse associée à cette clé : si le client renvoie la même clé, le serveur lui redonne la réponse déjà enregistrée sans recréer l'objet !"
            ],
            "code": _read("03_put_patch_et_idempotence.py"),
            "line_explanations": [
                {"lines": "20-29", "text": "Modèles Pydantic `FormationComplete` (pour POST/PUT) et `FormationPartielle` (champs `Optional` pour PATCH)."},
                {"lines": "33-53", "text": "Contrôle de `Header(default=None, alias='Idempotency-Key')` sur `POST` : renvoie l'objet mémorisé (`200 OK`) en cas de rejeu réseau."},
                {"lines": "57-68", "text": "Implémentation de `@app.put` : remplacement complet de l'entité."},
                {"lines": "72-80", "text": "Implémentation idiomatique de `@app.patch` : `payload.model_dump(exclude_unset=True)` ne met à jour que les champs réellement transmis."}
            ],
            "python_runner": {
                "prompt": "Exécutez `day_3/03_put_patch_et_idempotence.py` pour tester `Idempotency-Key` et `PATCH` (`exclude_unset=True`) :",
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
            "title": "3.3 — Gestionnaires d'Exceptions Globaux dans FastAPI (`@app.exception_handler`) : Zéro Crash HTML en Production",
            "duration": "50 min",
            "analogy": {
                "title": "Un traducteur diplomatique qui répond toujours dans la langue attendue (JSON), même en cas d'incident",
                "text": "Lorsqu'un client appelle une route inexistante (`404`), utilise une méthode interdite (`405`), ou déclenche une division par zéro imprévue (`500`), une API professionnelle utilise **`@app.exception_handler(...)`** pour garantir que 100 % des erreurs respectent un contrat JSON uniforme sans jamais exposer la trace d'exécution interne (*stacktrace*) au client."
            },
            "explanation": [
                "**1. Le décorateur `@app.exception_handler(ExcType)` dans FastAPI / Starlette** : Permet d'intercepter n'importe quelle classe d'exception (`StarletteHTTPException`, `RequestValidationError`, `Exception` ou vos propres exceptions métier) et de retourner une `JSONResponse` sur mesure.",
                "**2. Les gestionnaires indispensables** :\n  - `@app.exception_handler(StarletteHTTPException)` : Personnalise le JSON des erreurs `404 Not Found` (avec `chemin_demande` et `methode`) et `405 Method Not Allowed`.\n  - `@app.exception_handler(Exception)` : Filet de sécurité ultime qui capture toute erreur Python imprévue (`ZeroDivisionError`, `KeyError`, panne SQL), journalise l'erreur côté serveur, et renvoie au client un JSON `500 Internal Server Error` propre."
            ],
            "code": _read("04_gestion_erreurs_globale.py"),
            "line_explanations": [
                {"lines": "16-35", "text": "`@app.exception_handler(StarletteHTTPException)` intercepte les codes `404` et `405` et retourne une `JSONResponse` enrichie."},
                {"lines": "39-47", "text": "`@app.exception_handler(Exception)` intercepte tout crash non géré (ex: `ZeroDivisionError`), l'écrit dans le journal serveur et retourne un JSON `500` sécurisé."},
                {"lines": "55-64", "text": "Vérification automatisée avec `TestClient(app, raise_server_exceptions=False)` sur `404`, `405` et `500`."}
            ],
            "python_runner": {
                "prompt": "Exécutez `day_3/04_gestion_erreurs_globale.py` pour observer l'interception en JSON des erreurs 404, 405 et 500 :",
                "initial_code": _read("04_gestion_erreurs_globale.py")
            },
            "vscode_instructions": {
                "filename": "day_3/04_gestion_erreurs_globale.py",
                "steps": [
                    "Ouvrir `day_3/04_gestion_erreurs_globale.py`.",
                    "Exécuter `.venv/bin/python day_3/04_gestion_erreurs_globale.py` et observer comment `ZeroDivisionError` est converti en JSON 500 propre."
                ]
            }
        },
        {
            "id": "d3-l4",
            "file": "day_3/02_api_crud_sqlite.py",
            "title": "3.4 — Persistance Relationnelle SQLite avec `Depends(get_db)`, Transactions ACID & Parade contre l'Injection SQL (`?`)",
            "duration": "65 min",
            "analogy": {
                "title": "Séparer le plan d'exécution SQL des données saisies par l'utilisateur et fermer automatiquement la connexion avec yield",
                "text": "L'**Injection SQL** fait partie des failles de sécurité les plus critiques au monde (OWASP Top 10). Elle survient lorsqu'un développeur construit sa requête SQL en collant directement la variable du client avec un `+` ou une `f-string`. En combinant les **requêtes paramétrées (`?`)** et l'injection de dépendance **`Depends(get_db)`** avec `yield`, FastAPI garantit à la fois zéro injection SQL et la fermeture systématique de la connexion (`finally: conn.close()`)."
            },
            "explanation": [
                "**1. Pourquoi les Requêtes Paramétrées (`?`) neutralisent 100% des Injections SQL** :\n  - **DANGEREUX (À proscrire absolument)** : `db.execute(f\"SELECT * FROM formations WHERE salle = '{salle}'\")`.\n  - **SÉCURISÉ (Requête paramétrée)** : `db.execute(\"SELECT * FROM formations WHERE salle = ?\", (salle,))`.\n  - Avec le point d'interrogation `?`, le moteur SQLite compile d'abord la structure de l'ordre SQL, puis insère la valeur de `salle` comme une simple donnée inerte.",
                "**2. Gestion du cycle de vie de la connexion SQLite avec `Depends(get_db)` et `yield`** :\n  - Dans FastAPI, la fonction génératrice `def get_db():` ouvre la connexion SQLite, la fournit à la route via `yield conn`, et exécute automatiquement le bloc `finally: conn.close()` dès que la réponse est envoyée (même si une exception survient) !\n  - Toute modification (`INSERT`, `UPDATE`, `DELETE`) est validée atomiquement par `db.commit()`."
            ],
            "code": _read("02_api_crud_sqlite.py"),
            "line_explanations": [
                {"lines": "24-30", "text": "Dépendance génératrice `get_db()` avec `yield conn` et fermeture garantie dans `finally: conn.close()`."},
                {"lines": "69-99", "text": "Routes Web Jinja2 `/formations-sqlite` (GET et POST) utilisant `Form(...)`, `Depends(get_db)`, une requête `INSERT` paramétrée `?` et `Jinja2Templates`."},
                {"lines": "103-141", "text": "Routes API REST `GET`, `POST`, `PUT`, `DELETE` sur `/api/formations` utilisant `FormationSQLiteIn`, `Depends(get_db)` et des requêtes paramétrées `?`."}
            ],
            "sandbox_preset": {
                "label": "Tester PUT /api/sandbox/formations/1 sur la base SQLite",
                "method": "PUT",
                "url": "/api/sandbox/formations/1",
                "body": '{\n  "titre": "Architecture des APIs REST (Niveau Avancé)",\n  "salle": "Amphithéâtre ISGP"\n}'
            },
            "python_runner": {
                "prompt": "Exécutez `day_3/02_api_crud_sqlite.py` pour tester l'insertion SQLite via `Form(...)` et la lecture JSON via `Depends(get_db)` :",
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
