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
                "text": (
                    "Lorsqu'un véhicule passe au contrôle technique réglementaire avec des freins usés, un phare défectueux et un pneu lisse, l'inspecteur ne se contente pas de griffonner « Véhicule refusé » en vous forçant à revenir trois fois pour découvrir chaque anomalie une par une.\n\n"
                    "De la même manière, face à un formulaire JSON entaché de plusieurs erreurs, une API Tornado de qualité industrielle applique la norme internationale **RFC 7807 / RFC 9457 (*Problem Details for HTTP APIs*)** : elle inspecte l'intégralité des champs soumis et restitue en un seul aller-retour un rapport structuré par attribut avec `self.set_status(422)` et `Content-Type: application/problem+json`."
                )
            },
            "explanation": [
                (
                    "**Invariant du *Zero-Trust* applicatif sur les entrées clientes (*Never Trust User Input*).** "
                    "Quelle que soit la sophistication des contrôles de surface codés dans une interface React ou mobile, tout attaquant ou script automatisé peut solliciter directement votre socket Tornado via `curl` en injectant `{\"duree_jours\": -999, \"titre\": \"\"}`. "
                    "La validation défensive exhaustive côté serveur à l'entrée de `def post(self):` et `def put(self):` constitue par conséquent le seul rempart garantissant l'intégrité du modèle métier."
                ),
                (
                    "**Entonnoir de validation en quatre strates dans un `RequestHandler` Tornado.** "
                    "Un pipeline de validation robuste vérifie successivement la **validité syntaxique JSON** des octets `self.request.body` via `tornado.escape.json_decode` protégé par `try / except ValueError`, la **présence effective** des attributs requis après élagage des espaces `.strip()`, la **conformité stricte des types** (en distinguant notamment `int` de `bool`), puis le respect des **invariants du domaine métier** tels qu'une durée comprise entre `1` et `30` jours et un intitulé de `3` à `120` caractères."
                ),
                (
                    "**Frontière sémantique entre `400 Bad Request` et `422 Unprocessable Content`.** "
                    "Le code `400 Bad Request` sanctionne une défaillance de transport ou de syntaxe empêchant l'analyseur JSON de construire un dictionnaire cohérent (accolade manquante, octets UTF-8 tronqués), tandis que le code `422 Unprocessable Entity` atteste que l'arbre JSON a été parfaitement décodé mais que ses valeurs transgressent les règles métier de l'application."
                )
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
                "text": (
                    "Au sein d'une classe `FormationItemHandler` héritant de `RequestHandler`, les méthodes `def put(self, id_str):` et `def patch(self, id_str):` expriment deux contrats de mise à jour radicalement différents : réécrire intégralement une fiche cartonnée neuve ou ne rectifier qu'une seule ligne au stylo sans effacer le reste.\n\n"
                    "En parallèle, sur la route de création `FormationsIdempotentHandler.post(self)`, l'inspection préalable de l'en-tête `Idempotency-Key` agit comme un numéro de quittance bancaire unique qui neutralise toute duplication accidentelle lorsqu'un client mobile rejoue sa requête après une micro-coupure radio."
                )
            },
            "explanation": [
                (
                    "**Opposition contractuelle entre remplacement intégral (`def put`) et mutation partielle (`def patch`, RFC 5789).** "
                    "Appeler `PUT /api/v1/formations/1` ordonne au serveur de substituer à l'enregistrement `#1` la représentation complète fournie dans la requête, exigeant par conséquent la présence de tous les attributs obligatoires (`titre`, `duree_jours`, `salle`). "
                    "À l'inverse, `PATCH /api/v1/formations/1` transporte un différentiel partiel tel que `{\"salle\": \"Amphi ISGP\"}` : seules les clés explicitement présentes dans le dictionnaire reçu sont modifiées, préservant intactes toutes les autres colonnes."
                ),
                (
                    "**Idempotence synthétique de `POST` par mémorisation d'`Idempotency-Key`.** "
                    "Pour sécuriser les créations critiques (paiements, inscriptions officielles) face aux coupures d'accusés de réception TCP, le client génère un UUID v4 unique transmis dans `self.request.headers.get('Idempotency-Key')` avant sa première tentative. "
                    "Le serveur associe cette clé à la réponse produite dans un magasin atomique : si le client réémet le même `POST` avec la même clé, Tornado restitue instantanément l'enregistrement mis en cache sans exécuter de seconde écriture."
                )
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
                "text": (
                    "Dans sa configuration d'usine héritée des serveurs Web classiques, Tornado réagit à une route introuvable (`404`), à un verbe non supporté (`405`) ou à une exception imprévue (`500`) en émettant une page HTML minimale `<html><title>404: Not Found</title>...</html>`, faisant aussitôt échouer l'appel `response.json()` de vos applications clientes.\n\n"
                    "Pour garantir un contrat machine-à-machine infaillible, une API REST Tornado redéfinit **`write_error(self, status_code, **kwargs)`** dans sa classe racine `JsonApiBaseHandler` et branche **`default_handler_class=NotFoundJsonHandler`** au niveau de `tornado.web.Application`."
                )
            },
            "explanation": [
                (
                    "**Unification du formatage d'incidents dans `RequestHandler.write_error(self, status_code, **kwargs)`.** "
                    "Qu'une anomalie provienne d'une levée volontaire `raise tornado.web.HTTPError(code)`, d'un verbe HTTP absent de la classe (`405 Method Not Allowed`) ou d'une exception Python non interceptée telle que `ZeroDivisionError` transmise via `kwargs['exc_info']`, Tornado converge systématiquement vers `self.write_error()`. "
                    "Surcharger cette méthode dans `JsonApiBaseHandler` garantit que tous les codes `4xx` et `5xx` restituent un document JSON normalisé via `self.finish({...})` sans jamais divulguer la pile d'exécution interne au client."
                ),
                (
                    "**Capture des routes orphelines par `default_handler_class` sur `tornado.web.Application`.** "
                    "Lorsqu'une URL entrante ne satisfait aucune expression régulière enregistrée dans la table de routage, aucun contrôleur métier n'est sélectionné ; configurer `default_handler_class=NotFoundJsonHandler` (sous-classe de `JsonApiBaseHandler` levant `HTTPError(404)` dans `prepare()`) assure que même les adresses inexistantes empruntent votre formateur JSON unifié."
                )
            ],
            "code": _read("04_gestion_erreurs_globale.py"),
            "line_explanations": [
                {"lines": "18-46", "text": "`JsonApiBaseHandler.write_error` : intercepte les codes `404`, `405` et `>= 500` (avec inspection de `kwargs.get('exc_info')` côté serveur) et renvoie une réponse JSON via `self.finish({...})`."},
                {"lines": "49-52", "text": "`NotFoundJsonHandler` : utilisé comme `default_handler_class` pour intercepter toute URL inconnue en JSON."},
                {"lines": "67-76", "text": "Enregistrement de `default_handler_class=NotFoundJsonHandler` dans `tornado.web.Application`."}
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
                "text": (
                    "L'**Injection SQL (SQLi)** figure depuis deux décennies parmi les vulnérabilités les plus dévastatrices des systèmes d'information. "
                    "Elle apparaît dès qu'un développeur assemble dynamiquement une instruction SQL par concaténation ou `f-string` avec une saisie externe : en soumettant la chaîne `\"Alger' OR '1'='1\"`, l'attaquant brise les guillemets littéraux et réécrit la logique booléenne du moteur relationnel.\n\n"
                    "Séparer physiquement la compilation de l'arbre syntaxique SQL de la liaison des paramètres (`?`) rend cette attaque structurellement impossible, quel que soit le contenu envoyé sur le réseau."
                )
            },
            "explanation": [
                (
                    "**Éradication structurelle des injections SQL par requêtes préparées (`?` en DB-API 2.0).** "
                    "Toute interpolation directe telle que `conn.execute(f\"SELECT * FROM formations WHERE salle = '{salle}'\")` doit être bannie sans exception au profit de la liaison paramétrée `conn.execute(\"SELECT * FROM formations WHERE salle = ?\", (salle,))`. "
                    "Avec le marqueur positionnel `?`, le moteur C de SQLite compile et fige l'arbre syntaxique abstrait (AST) de la requête avant d'injecter le tuple `(salle,)` via `sqlite3_bind_text` comme un pur scalaire inerte incapable d'altérer la grammaire SQL."
                ),
                (
                    "**Politique de sécurité de `RequestHandler.write()` face aux tableaux JSON racine.** "
                    "Afin de prévenir les anciennes attaques d'exfiltration *JSON Hijacking* sur les constructeurs `Array` des navigateurs et d'encourager des contrats extensibles, la méthode `self.write()` de Tornado accepte nativement un `dict` mais lève une `TypeError` si on lui soumet une `list` brute, incitant à structurer chaque collection sous une enveloppe dictionnaire `{\"total\": len(lignes), \"data\": lignes}`."
                )
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
