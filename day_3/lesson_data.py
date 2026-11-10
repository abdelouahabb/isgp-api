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
                "text": "Si un client soumet un formulaire JSON comportant 3 erreurs (titre trop court, durée négative, salle manquante), une API médiocre répond simplement `{\"erreur\": \"Données invalides\"}` sans dire quel champ pose problème. Une API professionnelle applique le standard international **RFC 7807 (`Problem Details for HTTP APIs`)** en retournant le détail exact par champ avec le code `400` ou `422 Unprocessable Entity`."
            },
            "explanation": [
                "**1. Pourquoi ne jamais faire confiance au client (`Never Trust User Input`)** : Même si votre interface Web possède des contrôles JavaScript, n'importe qui peut appeler votre API directement avec `curl` ou un script Python en envoyant `{\"duree_jours\": -999, \"titre\": \"\"}`. La validation côté serveur est **obligatoire**.",
                "**2. Les 4 niveaux de validation d'un Payload JSON** :\n  1. **Présence et syntaxe JSON** : `corps = request.get_json(silent=True)` est-il bien un dictionnaire Python (`isinstance(corps, dict)`) ?\n  2. **Champs obligatoires** : Le champ requis est-il présent et non vide après `.strip()` ?\n  3. **Contrôle de type** : `duree_jours` est-il bien convertible en entier `int` ?\n  4. **Contraintes métier (Domain Validation)** : `duree_jours` est-il compris entre `1` et `30` ? Le titre fait-il entre `3` et `120` caractères ?",
                "**3. Différence entre `400 Bad Request` et `422 Unprocessable Entity`** :\n  - `400` : Le JSON est syntaxiquement cassé (accolade manquante) ou la requête est incompréhensible.\n  - `422` : Le JSON est syntaxiquement valide, mais ses valeurs violent les règles métier (ex. durée de `-5` jours)."
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
                "text": "En entretien technique comme en conception d'API, deux questions distinguent immédiatement un développeur averti :\n1. Quelle est la différence exacte entre `PUT` et `PATCH` ?\n2. Comment empêcher qu'un client dont la connexion 4G clignote ne crée 2 fois la même commande en rejouant son `POST` ?"
            },
            "explanation": [
                "**1. `PUT` vs `PATCH` (RFC 5789)** :\n  - **`PUT /api/v1/formations/1`** effectue un **remplacement complet** de l'enregistrement n°1. Le client doit envoyer l'intégralité des champs de la ressource (`titre`, `duree_jours`, `salle`). Si un champ est omis, il est soit rejeté (`400`), soit écrasé par sa valeur vide.\n  - **`PATCH /api/v1/formations/1`** effectue une **mise à jour partielle**. Le client peut envoyer uniquement `{\"salle\": \"Amphi B\"}` : seule la colonne `salle` est modifiée, le `titre` et la `duree_jours` restent intacts !",
                "**2. Rendre `POST` idempotent grâce à l'en-tête `Idempotency-Key` (Standard Stripe / Adyen / Banques)** :\n  - Par nature, `POST` n'est pas idempotent. Si un client mobile envoie `POST /api/commandes`, que le serveur crée la commande, mais que le Wi-Fi coupe avant que le téléphone ne reçoive la réponse `201`, le téléphone va renvoyer la requête `POST`.\n  - Pour éviter de créer un doublon, le client génère un identifiant unique (`Idempotency-Key: cmd-2026-xyz`) dans les Headers. Le serveur mémorise la réponse associée à cette clé : si le client renvoie la même clé, le serveur lui redonne la réponse déjà enregistrée sans recréer l'objet !"
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
                "text": "Par défaut, lorsqu'un client appelle une URL qui n'existe pas (`404`) ou utilise la mauvaise méthode HTTP (`405`), Flask renvoie une **page Web HTML** (`<!doctype html><title>404 Not Found</title>...`). Or, l'application mobile ou le script qui appelle votre API s'attend à recevoir du **JSON** (`reponse.json()`) et plante sur une erreur de décodage ! Une API professionnelle doit **intercepter 100% des erreurs pour les formater en JSON**."
            },
            "explanation": [
                "**1. Le décorateur `@app.errorhandler(code_ou_exception)`** : Permet de remplacer les pages d'erreur HTML par défaut de Flask par des réponses JSON uniformes.",
                "**2. Les 3 gestionnaires indispensables** :\n  - `@app.errorhandler(404)` : Route introuvable.\n  - `@app.errorhandler(405)` : Méthode HTTP non autorisée sur cette route (ex. faire un `DELETE` sur `/api/login`).\n  - `@app.errorhandler(Exception)` : Filet de sécurité ultime qui capture toute erreur Python imprévue (`ZeroDivisionError`, `KeyError`, panne base de données), écrit la trace technique dans les logs du serveur pour le développeur, et renvoie au client un JSON `500 Internal Server Error` propre **sans jamais divulguer le code source ni les mots de passe dans le message d'erreur**."
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
                "text": "L'**Injection SQL** fait partie des failles de sécurité les plus critiques au monde (OWASP Top 10). Elle survient lorsqu'un développeur construit sa requête SQL en collant directement la variable du client avec un `+` ou une `f-string`. Si le client envoie `\"Alger' OR '1'='1\"`, il détourne l'ordre SQL et peut lire ou détruire toute la base !"
            },
            "explanation": [
                "**1. Pourquoi les Requêtes Paramétrées (`?`) neutralisent 100% des Injections SQL** :\n  - **DANGEREUX (À proscrire absolument)** : `conn.execute(f\"SELECT * FROM formations WHERE salle = '{salle}'\")`.\n  - **SÉCURISÉ (Requête paramétrée)** : `conn.execute(\"SELECT * FROM formations WHERE salle = ?\", (salle,))`.\n  - Avec le point d'interrogation `?`, le moteur SQLite compile d'abord la structure de l'ordre SQL, puis insère la valeur de `salle` comme une simple donnée inerte : même si elle contient des guillemets ou `DROP TABLE`, elle ne sera jamais exécutée comme une commande !",
                "**2. Transactions ACID (`conn.commit()` et `conn.rollback()`)** : En SQLite, toute modification (`INSERT`, `UPDATE`, `DELETE`) ouvre une transaction. Si plusieurs tables doivent être mises à jour ensemble, `conn.commit()` valide l'ensemble d'un seul bloc atomique, tandis que `conn.rollback()` annule tout en cas d'erreur à mi-chemin."
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
