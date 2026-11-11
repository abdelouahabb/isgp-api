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
                "text": (
                    "Lorsqu'un client soumet un document JSON entaché de trois anomalies simultanées — intitulé trop court, durée négative et type incohérent —, une API sommaire se contente de rejeter l'appel par un message opaque `{\"erreur\": \"Données invalides\"}`, condamnant l'utilisateur à tâtonner essai après essai.\n\n"
                    "Avec **FastAPI et le moteur Rust `pydantic-core` de Pydantic v2**, chaque classe `BaseModel` inspecte l'intégralité des attributs en une seule passe et permet de formater toute `RequestValidationError` selon le standard international **RFC 7807 / RFC 9457 (`Problem Details for HTTP APIs`)** sous le statut `422 Unprocessable Entity`."
                )
            },
            "explanation": [
                "**Validation systématique côté serveur (*Never Trust User Input*).** Aussi sophistiqués que soient les contrôles visuels d'une interface React ou mobile, tout attaquant ou script défaillant peut contourner le navigateur et frapper directement la socket HTTP avec `curl` en transmettant `{\"duree_jours\": -999, \"titre\": \"\"}`. La validation stricte à l'entrée du backend FastAPI via Pydantic v2 constitue par conséquent un rempart de sécurité non négociable.",
                "**Architecture déclarative à quatre niveaux de Pydantic v2 (`BaseModel`, `Field`, `@field_validator`, RFC 7807).** Le schéma combine le typage Python natif (`titre: str`, `duree_jours: int`) avec les contraintes numériques et lexicales de `Field(min_length=3, max_length=120, ge=1, le=30)` évaluées à vitesse native en Rust, puis exécute les invariants métier personnalisés décorés par `@field_validator('titre')` (normalisation `.strip()`, rejet de chaînes blanches). En enregistrant `@app.exception_handler(RequestValidationError)`, toutes les violations collectées dans `exc.errors()` sont restituées dans une enveloppe RFC 7807 normalisée (`type`, `title`, `status`, `champs_en_erreur`, `detail`).",
                "**Frontière sémantique entre `400 Bad Request` et `422 Unprocessable Entity`.** Le code `400 Bad Request` sanctionne une corruption syntaxique de bas niveau qui empêche l'analyseur JSON de décoder les octets reçus (accolade fermante omise, séquence UTF-8 illégale), tandis que le code `422 Unprocessable Entity` indique que l'arbre syntaxique JSON est parfaitement lisible mais que les valeurs portées violent les contraintes du contrat métier Pydantic."
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
                "text": (
                    "Lors d'une revue d'architecture ou d'un entretien d'ingénierie senior, deux problématiques de mutation séparent immédiatement les implémentations fragiles des systèmes distribués de grade bancaire.\n\n"
                    "La première consiste à distinguer sans ambiguïté le remplacement intégral d'un enregistrement (`PUT`) de sa mise à jour différentielle (`PATCH`) sans écraser accidentellement des colonnes par `None` ; la seconde consiste à garantir qu'un téléphone mobile subissant une coupure 4G au milieu d'un `POST` puisse réémettre sa requête sans débiter ni inscrire deux fois l'utilisateur."
                )
            },
            "explanation": [
                "**Remplacement complet (`PUT`) face à la mutation différentielle (`PATCH`, RFC 5789) dans Pydantic v2.** Une route `@app.put('/api/v1/formations/{id}')` exige un modèle exhaustif `FormationComplete` qui substitue l'état entier de la ressource ciblée, alors qu'une route `@app.patch('/api/v1/formations/{id}')` reçoit un modèle `FormationPartielle` aux attributs optionnels et invoque **`payload.model_dump(exclude_unset=True)`**. Ce paramètre crucial demande à Pydantic v2 d'extraire uniquement le sous-ensemble exact des clés présentes dans le JSON entrant (`model_fields_set`), préservant ainsi toutes les autres colonnes de l'entité.",
                "**Déduplication transactionnelle de `POST` par en-tête `Idempotency-Key`.** Parce que la méthode `POST` n'est pas idempotente par nature, une perte du paquet de réponse `201 Created` sur un réseau radio incite le client à rejouer l'envoi au risque de créer un doublon critique. Exiger un identifiant UUID généré côté client via `Header(default=None, alias='Idempotency-Key')` permet au serveur d'indexer l'empreinte de la réponse initiale en mémoire ou dans Redis : tout rejeu porteur de la même clé restitue immédiatement le résultat mis en cache sans réexécuter l'écriture en base."
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
                "text": (
                    "Qu'un client interroge une URI inexistante (`404`), emploie un verbe interdit (`405`) ou déclenche accidentellement une division par zéro au cœur d'un calcul métier (`500`), un SDK mobile qui attend du JSON ne doit jamais recevoir une page HTML brute ou du texte brut.\n\n"
                    "En production, une API FastAPI branche des gestionnaires globaux **`@app.exception_handler(...)`** sur la couche Starlette afin de garantir que 100 % des sorties anormales respectent un contrat JSON uniforme tout en confinant strictement les traces d'exécution internes (*stacktraces*) aux journaux privés du serveur."
                )
            },
            "explanation": [
                "**Aiguillage centralisé des erreurs par `@app.exception_handler(ExcType)`.** L'architecture d'exceptions de Starlette et FastAPI dispatche toute anomalie levée durant le cycle ASGI vers le gestionnaire enregistré pour la classe d'exception correspondante (`StarletteHTTPException`, `RequestValidationError`, `Exception` ou toute classe métier dédiée), permettant de construire en un point unique une `JSONResponse` conforme au schéma d'erreur de l'organisation.",
                "**Normalisation des rejets de routage (`404`/`405`) et confinement des pannes internes (`500`).** Brancher `@app.exception_handler(StarletteHTTPException)` enrichit uniformément les erreurs `404 Not Found` et `405 Method Not Allowed` avec le chemin et le verbe demandés, tandis que le filet ultime `@app.exception_handler(Exception)` intercepte les défaillances imprévues (`ZeroDivisionError`, verrouillage SQL), consigne la pile d'appels complète dans les journaux d'exploitation et ne renvoie au client qu'un message `500 Internal Server Error` assaini de toute fuite d'infrastructure."
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
                "text": (
                    "L'**Injection SQL (SQLi)** figure invariablement parmi les vulnérabilités les plus dévastatrices des systèmes d'information : elle survient dès qu'un programme assemble une instruction SQL par concaténation de chaînes (`+` ou `f-string`), permettant à la saisie d'un attaquant de muter la grammaire même de la requête exécutée par le moteur relationnel.\n\n"
                    "En associant systématiquement les **requêtes paramétrées (`?`)** à l'injection de dépendances génératrices **`Depends(get_db)`** articulées autour de `yield`, FastAPI garantit simultanément l'immunité structurelle contre toute injection SQL et la libération déterministe du descripteur de fichier SQLite (`finally: conn.close()`)."
                )
            },
            "explanation": [
                "**Séparation stricte entre arbre syntaxique SQL et données par liaison de paramètres (`?`).** Écrire `db.execute(f\"SELECT * FROM formations WHERE salle = '{salle}'\")` autorise une charge malveillante telle que `' OR '1'='1` à altérer l'arbre logique `WHERE` et à exfiltrer la table entière. À l'inverse, l'appel paramétré `db.execute(\"SELECT * FROM formations WHERE salle = ?\", (salle,))` ordonne au moteur C SQLite de compiler d'abord le plan d'exécution immuable avec un marqueur de liaison `?`, puis d'y injecter les octets de `salle` comme un simple scalaire littéral inerte incapable de modifier la commande SQL.",
                "**Gestion transactionnelle ACID et libération déterministe par générateur `Depends(get_db)`.** Déclarer une dépendance génératrice `def get_db():` structurée autour de `try: yield conn finally: conn.close()` confie à FastAPI l'ouverture d'une connexion isolée avant l'exécution de la route et garantit l'exécution du bloc `finally` après l'envoi de la réponse HTTP, y compris lorsqu'une `HTTPException` ou une erreur SQL interrompt la fonction. Chaque écriture (`INSERT`, `UPDATE`, `DELETE`) est scellée durablement sur disque de manière atomique par `db.commit()`."
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
