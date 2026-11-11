import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_3_DATA = {
    "day_number": 3,
    "folder": "day_3",
    "badge": "Jour 3 • CRUD, Validation, Idempotence & SQLite",
    "title": "Ingénierie CRUD : Validation RFC 7807, PUT vs PATCH, Idempotency-Key, Gestion Globale des Erreurs & SQLite ACID",
    "goal": "Implémenter une validation stricte des entrées avec retour RFC 7807 (422), maîtriser PUT vs PATCH et la sécurisation de POST par Idempotency-Key, intercepter globalement toutes les erreurs en JSON (@app.errorhandler), et gérer la persistance SQLite protégée contre l'injection SQL.",
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
            "title": "3.1 — Validation Stricte des Charges Utiles JSON & Format d'Erreur Normalisé RFC 7807 (`422 Unprocessable Entity`)",
            "duration": "60 min",
            "analogy": {
                "title": "Le contrôle technique qui liste précisément chaque anomalie constatée",
                "text": "Lorsqu'un client soumet une charge utile JSON entachée de trois anomalies simultanées — intitulé trop court, durée négative et salle absente —, une implémentation approximative se contente d'un laconique `{\"erreur\": \"Données invalides\"}` qui oblige l'appelant à tâtonner à l'aveugle. Une API Flask de qualité industrielle applique le standard **RFC 7807 (`Problem Details for HTTP APIs`)** afin de restituer en un seul aller-retour la cartographie exhaustive des champs en échec accompagnée du code `422 Unprocessable Entity`."
            },
            "explanation": [
                "**Principe fondamental de défiance côté serveur (`Never Trust User Input`).** Toute validation exécutée dans un navigateur par JavaScript ou HTML5 relève uniquement du confort ergonomique et se contourne en une seconde à l'aide d'un appel `curl` ou d'un script Python forgeant `{\"duree_jours\": -999, \"titre\": \"\"}`. Le worker Flask constitue l'unique frontière d'intégrité fiable et doit systématiquement contrôler chaque octet entrant avant toute écriture métier.",
                "**Pipeline de validation défensive en quatre paliers dans Flask.** La vérification débute par la conformité structurelle du corps via `corps = request.get_json(silent=True)` et `isinstance(corps, dict)`, puis contrôle la présence effective des attributs obligatoires nettoyés par `.strip()`. Elle s'assure ensuite de la convertibilité stricte des types numériques (`int`, `float`) avant d'évaluer les invariants du domaine métier, tels qu'une durée bornée entre `1` et `30` jours ou un intitulé compris entre `3` et `120` caractères.",
                "**Distinction sémantique entre `400 Bad Request` et `422 Unprocessable Entity`.** Le statut `400 Bad Request` sanctionne une défaillance syntaxique de bas niveau — par exemple une chaîne JSON tronquée dépourvue d'accolade fermante que Werkzeug ne parvient même pas à décoder. À l'inverse, `422 Unprocessable Entity` atteste que l'arbre JSON est syntaxiquement valide, mais qu'une ou plusieurs valeurs violent les règles métier recensées dans l'objet `champs_en_erreur` au format RFC 7807."
            ],
            "code": _read("01_api_crud_memoire.py"),
            "line_explanations": [
                {"lines": "13-29", "text": "Fonction dédiée `valider_payload_formation(corps)` qui accumule toutes les anomalies par nom de champ dans le dictionnaire `erreurs`."},
                {"lines": "37-46", "text": "Si au moins une anomalie est détectée, retourne immédiatement un objet conforme à la RFC 7807 (`type`, `title`, `status`, `champs_en_erreur`) avec le statut `422`."},
                {"lines": "48-56", "text": "Si la validation réussit, nettoie les chaînes (`.strip()`), insère l'entité et renvoie `201 Created`."}
            ],
            "sandbox_preset": {
                "label": "Tester la création : POST /api/sandbox/formations",
                "method": "POST",
                "url": "/api/sandbox/formations",
                "body": '{\n  "titre": "Sécurité des Services Web & Tokens",\n  "formateur": "Intervenant ISGP",\n  "duree_jours": 4,\n  "salle": "Laboratoire 2"\n}'
            },
            "vscode_instructions": {
                "filename": "day_3/01_api_crud_memoire.py",
                "steps": [
                    "Ouvrir `day_3/01_api_crud_memoire.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_3/01_api_crud_memoire.py` et tester un `POST` avec une durée négative pour observer la réponse RFC 7807."
                ]
            }
        },
        {
            "id": "d3-l2",
            "file": "day_3/03_put_patch_et_idempotence.py",
            "title": "3.2 — `PUT` (Remplacement Intégral) vs `PATCH` (Modification Partielle) & Sécurisation de `POST` par `Idempotency-Key`",
            "duration": "60 min",
            "analogy": {
                "title": "Remplacer toute une fiche (PUT) vs Corriger une seule ligne au stylo (PATCH) vs Numéro de transaction unique (Idempotency-Key)",
                "text": "En revue d'architecture comme lors d'un audit de système critique, deux décisions de conception révèlent immédiatement la rigueur d'un ingénieur API. La première consiste à séparer sans ambiguïté le remplacement intégral d'un enregistrement par **`PUT`** de sa retouche chirurgicale par **`PATCH`** ; la seconde consiste à immuniser les créations **`POST`** contre les micro-coupures des réseaux mobiles grâce à un jeton de déduplication **`Idempotency-Key`**."
            },
            "explanation": [
                "**Remplacement intégral `PUT` face à la modification partielle `PATCH` (RFC 5789).** Invoquer `PUT /api/v1/formations/1` ordonne l'écrasement complet de l'état de la ressource cible : le client doit transmettre l'intégralité des attributs contractuels (`titre`, `duree_jours`, `salle`), faute de quoi la requête est rejetée ou réinitialise les colonnes omises. À l'opposé, `PATCH /api/v1/formations/1` n'accepte qu'un fragment différentiel comme `{\"salle\": \"Amphi B\"}` et mute exclusivement les clés présentes dans le dictionnaire JSON sans altérer les autres colonnes.",
                "**Déduplication des requêtes `POST` par en-tête `Idempotency-Key`.** Lorsqu'une application mobile expédie `POST /api/commandes`, que le worker Flask valide la transaction SQL mais que la liaison radio 4G s'interrompt avant la réception de l'accusé `201 Created`, le client rejoue légitimement son `POST`. En exigeant un identifiant unique `Idempotency-Key: cmd-2026-xyz` dans `request.headers`, le serveur persiste l'empreinte de la réponse initiale et restitue exactement l'entité déjà créée lors des rejeux ultérieurs sans jamais facturer ni insérer de doublon.",
                "**Cohérence multi-workers du registre d'idempotence en production.** Si un simple dictionnaire Python suffit à illustrer l'algorithme dans un processus unique, un déploiement industriel sous Gunicorn répartit les requêtes sur plusieurs workers indépendants en mémoire. Les clés d'idempotence doivent alors être stockées dans une table SQL munie d'une contrainte `UNIQUE` ou dans un cache partagé Redis assorti d'une durée de rétention (`TTL`)."
            ],
            "code": _read("03_put_patch_et_idempotence.py"),
            "line_explanations": [
                {"lines": "17-22", "text": "Contrôle de l'en-tête `Idempotency-Key` sur `POST` : si la clé a déjà été traitée, renvoie immédiatement l'objet précédemment créé (`rejoue_sans_doublon: True`) sans réinsérer."},
                {"lines": "41-55", "text": "Implémentation stricte de `PUT` : exige la présence de tous les attributs (`titre`, `duree_jours`, `salle`) et remplace l'enregistrement complet."},
                {"lines": "59-68", "text": "Implémentation de `PATCH` : met à jour uniquement les clés présentes dans le JSON envoyé."}
            ],
            "python_runner": {
                "prompt": "Simulez un client qui envoie 2 fois le même POST avec la même Idempotency-Key suite à une coupure réseau :",
                "initial_code": '''cache_idempotence = {}
base_commandes = []

def post_commande(cle_idempotence, donnees):
    if cle_idempotence in cache_idempotence:
        print(f"[REJEU DÉTECTÉ : {cle_idempotence}] Aucun doublon créé, renvoi de la commande existante.")
        return cache_idempotence[cle_idempotence]

    nouvelle = {"id": len(base_commandes) + 1, **donnees}
    base_commandes.append(nouvelle)
    cache_idempotence[cle_idempotence] = nouvelle
    print(f"[CRÉATION : {cle_idempotence}] Nouvelle commande enregistrée :", nouvelle)
    return nouvelle

# Premier envoi par le client
post_commande("idem-998877", {"formation": "API Flask", "montant": 45000})
# Deuxième envoi (retry réseau avec la même clé)
post_commande("idem-998877", {"formation": "API Flask", "montant": 45000})
print("Total commandes en base :", len(base_commandes))'''
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
            "title": "3.3 — Gestionnaires d'Erreurs Globaux (`@app.errorhandler`) : Zéro Page HTML d'Erreur dans une API",
            "duration": "50 min",
            "analogy": {
                "title": "Un traducteur diplomatique qui répond toujours dans la langue attendue (JSON), même en cas d'incident",
                "text": "Par défaut, lorsqu'un client interroge une route inexistante (`404`) ou emploie un verbe interdit (`405`), Werkzeug génère une **page HTML d'erreur** (`<!doctype html><title>404 Not Found</title>...`). Or, l'application mobile ou le microservice appelant invoque immédiatement `reponse.json()` et s'interrompt sur une exception de désérialisation : une API Flask industrielle doit **intercepter 100 % des exceptions HTTP et Python afin de garantir une enveloppe JSON uniforme en toute circonstance**."
            },
            "explanation": [
                "**Interception déclarative des exceptions HTTP Werkzeug via `@app.errorhandler`.** Chaque fois que le routeur `url_map` échoue à résoudre un chemin ou rejette une méthode HTTP, Werkzeug lève une sous-classe de `HTTPException` telle que `NotFound` (`404`) ou `MethodNotAllowed` (`405`). En enregistrant `@app.errorhandler(404)` et `@app.errorhandler(405)` sur l'application Flask, le développeur substitue aux gabarits HTML natifs une réponse `jsonify(...)` propre documentant le chemin et la méthode mis en cause.",
                "**Filet de sécurité global `@app.errorhandler(Exception)` et confinement des traces.** Toute défaillance non anticipée au cœur d'une vue — division par zéro, clé manquante ou indisponibilité momentanée de SQLite — remonte la pile d'appels jusqu'au gestionnaire générique `@app.errorhandler(Exception)`. Celui-ci consigne la pile d'exécution complète (*stack trace*) dans les journaux internes de Gunicorn pour l'équipe d'exploitation, tout en ne renvoyant au client externe qu'un message `500 Internal Server Error` épuré qui ne divulgue ni chemin système, ni requête SQL, ni secret applicatif.",
                "**Désactivation impérative du débogueur interactif Werkzeug en production.** Activer `debug=True` expose en cas d'exception la console interactive Werkzeug dans le navigateur, offrant potentiellement l'exécution arbitraire de code Python sur l'hôte. Sous Gunicorn, `DEBUG` demeure strictement fixé à `False` afin que seuls vos gestionnaires JSON `@app.errorhandler` gouvernent la surface d'erreur publique."
            ],
            "code": _read("04_gestion_erreurs_globale.py"),
            "line_explanations": [
                {"lines": "11-17", "text": "Intercepte toute erreur `404` sur le serveur et retourne un objet JSON indiquant le chemin et la méthode appelés."},
                {"lines": "20-24", "text": "Intercepte toute erreur `405 Method Not Allowed` en JSON."},
                {"lines": "27-36", "text": "Filet de sécurité global : journalise l'exception côté serveur et renvoie un JSON `500` générique et sécurisé au client."}
            ],
            "vscode_instructions": {
                "filename": "day_3/04_gestion_erreurs_globale.py",
                "steps": [
                    "Ouvrir `day_3/04_gestion_erreurs_globale.py`.",
                    "Exécuter `.venv/bin/python day_3/04_gestion_erreurs_globale.py` et appeler `http://127.0.0.1:5001/api/v1/division?a=10&b=0` pour voir comment le crash `ZeroDivisionError` est converti en JSON propre."
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
                "text": "L'**Injection SQL** figure invariablement parmi les vulnérabilités les plus destructrices du référentiel OWASP. Elle survient dès qu'un développeur assemble une requête par concaténation ou *f-string* avec une entrée non fiable : en soumettant la chaîne `\"Alger' OR '1'='1\"`, un attaquant altère l'arbre syntaxique de l'instruction SQL et parvient à contourner l'authentification, exfiltrer des tables entières ou détruire le schéma."
            },
            "explanation": [
                "**Neutralisation structurelle de l'injection SQL par requêtes paramétrées (`?`).** Au lieu d'interpoler une variable Python dans la chaîne SQL (`f\"... WHERE salle = '{salle}'\"`), l'interface `DB-API 2.0` (`PEP 249`) du module `sqlite3` impose l'usage de marqueurs positionnels `?` : `conn.execute(\"SELECT * FROM formations WHERE salle = ?\", (salle,))`. Le moteur SQLite analyse et compile d'abord le plan d'exécution immuable de la requête, puis lie la valeur de `salle` dans un tampon de données séparé où les apostrophes ou mots-clés tels que `DROP TABLE` demeurent strictement inertes.",
                "**Garanties transactionnelles ACID par `conn.commit()` et `conn.rollback()`.** Toute écriture relationnelle (`INSERT`, `UPDATE`, `DELETE`) s'inscrit dans une transaction respectant l'Atomicité, la Cohérence, l'Isolation et la Durabilité. Lorsque plusieurs tables doivent évoluer de concert, `conn.commit()` scelle l'ensemble sur disque de manière indivisible, tandis que `conn.rollback()` restaure intégralement l'état antérieur si une exception survient à mi-parcours.",
                "**Gestion propre des connexions SQLite au fil des requêtes WSGI.** Comme chaque requête HTTP sous Gunicorn peut être servie par un thread ou un processus distinct, une API Flask ouvre une connexion dédiée au début du traitement (ou via un gestionnaire de contexte `with sqlite3.connect(...) as conn:`), configure `sqlite3.Row` pour accéder aux colonnes par nom et referme systématiquement le descripteur de fichier en fin de cycle."
            ],
            "code": _read("02_api_crud_sqlite.py"),
            "line_explanations": [
                {"lines": "24-40", "text": "Initialisation du schéma SQLite avec clé primaire auto-incrémentée (`INTEGER PRIMARY KEY AUTOINCREMENT`)."},
                {"lines": "47-72", "text": "Route Web Jinja2 `/formations-sqlite` : traite le formulaire HTML (`request.form`) par requête `INSERT` paramétrée `?` et rend `day_3/templates/catalogue_sqlite.html`."},
                {"lines": "84-101", "text": "Route API `POST /api/formations` hybride (`request.get_json()` ou `request.form`) avec requête paramétrée `?` et retour `201 Created`."},
                {"lines": "105-131", "text": "Routes `PUT` et `DELETE` paramétrées avec `?` et vérification de `cur.rowcount`."}
            ],
            "sandbox_preset": {
                "label": "Tester PUT /api/sandbox/formations/1 sur la base SQLite",
                "method": "PUT",
                "url": "/api/sandbox/formations/1",
                "body": '{\n  "titre": "Architecture des APIs REST (Niveau Avancé)",\n  "salle": "Amphithéâtre ISGP"\n}'
            },
            "python_runner": {
                "prompt": "Comparez l'effet d'une tentative d'Injection SQL sur une requête vulnérable vs une requête paramétrée avec ? :",
                "initial_code": '''import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE utilisateurs (id INT, login TEXT, role TEXT)")
conn.execute("INSERT INTO utilisateurs VALUES (1, 'admin', ' direction'), (2, 'amine', 'stagiaire')")

# Entrée malveillante envoyée par un attaquant :
entree_pirate = "' OR '1'='1"

# 1. REQUÊTE PARAMÉTRÉE SÉCURISÉE AVEC ? :
lignes_sures = conn.execute("SELECT * FROM utilisateurs WHERE login = ?", (entree_pirate,)).fetchall()
print("1. Résultat avec requête paramétrée (?) :", lignes_sures, "-> Attaque neutralisée !")'''
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
