import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_0_DATA = {
    "day_number": 0,
    "folder": "day_0",
    "badge": "Jour 0 • Mise à Niveau",
    "title": "Fondations Python & Ingénierie Logicielle (Zéro Prérequis)",
    "goal": "Maîtriser les fondations indispensables avant d'aborder le réseau : modèle d'exécution mémoire, typage et conversions sécurisées, structures de données imbriquées (listes/dictionnaires), fonctions, gestion des exceptions (try/except) et fonctionnement interne des décorateurs (@).",
    "starter_filename": "day_0/04_exceptions_et_decorateurs.py",
    "files": [
        "day_0/01_variables_et_types.py",
        "day_0/02_listes_et_dictionnaires.py",
        "day_0/03_fonctions.py",
        "day_0/04_exceptions_et_decorateurs.py",
    ],
    "lessons": [
        {
            "id": "d0-l1",
            "file": "day_0/01_variables_et_types.py",
            "title": "0.1 — Modèle d'Exécution Python, Mémoire Vive (RAM) & Typage des Données",
            "duration": "40 min",
            "analogy": {
                "title": "Les cellules nommées de la mémoire vive",
                "text": "Lorsqu'un script Python s'exécute, l'interpréteur lit le fichier séquentiellement de haut en bas. Chaque variable créée alloue un espace en **mémoire vive (RAM)** identifié par un nom. Comprendre la nature exacte (le **type**) de ce qui est stocké dans cet espace est fondamental : dans une API Web, tout ce qui arrive par l'URL arrive sous forme de texte (`str`) et doit souvent être converti explicitement en nombre (`int` ou `float`) avant tout calcul."
            },
            "explanation": [
                "**1. Affectation et cycle de vie en RAM** : L'opérateur `=` évalue d'abord l'expression située à droite, puis associe le résultat au nom situé à gauche (`total_heures = duree_jours * heures_par_jour`). Dès que le processus Python s'arrête, la mémoire vive est libérée (d'où la nécessité d'une base de données au Jour 3).",
                "**2. Les 5 types primitifs incontournables dans une API** :\n  - **`str` (Chaîne de caractères)** : Texte UTF-8 entouré de guillemets (`\"ISGP\"`). En JSON, devient `\"ISGP\"`.\n  - **`int` (Entier)** : Nombre sans décimale (`5`, `200`, `404`). Utilisé pour les identifiants (`id`), les compteurs, les codes HTTP et les montants en centimes.\n  - **`float` (Nombre à virgule flottante)** : Nombre décimal noté avec un point (`19.5`).\n  - **`bool` (Booléen)** : État binaire `True` ou `False` (avec majuscule en Python, converti en `true`/`false` en JSON).\n  - **`None` (Absence de valeur)** : Représente un champ vide ou non renseigné en Python (converti en `null` en JSON).",
                "**3. Piège classique en développement Web : `" + '"25"' + "` vs `25`** : La chaîne `\"25\"` est du texte (`\"25\" + \"5\"` produit `\"255\"`), tandis que `25` est un entier (`25 + 5` produit `30`). On utilise `int(\"25\")` ou `float(\"19.5\")` pour convertir une entrée réseau en nombre."
            ],
            "code": _read("01_variables_et_types.py"),
            "line_explanations": [
                {"lines": "1-4", "text": "En-tête et commentaires (`#`) : ignorés par Python, ils documentent l'objectif et la commande d'exécution du fichier."},
                {"lines": "5-9", "text": "Allocation en mémoire de variables de types distincts : `str` (`organisme`, `ville`), `int` (`duree_jours`, `heures_par_jour`) et `bool` (`session_active`)."},
                {"lines": "11", "text": "Évaluation de la multiplication `5 * 6` et affectation du résultat entier `30` à `total_heures`."},
                {"lines": "13-16", "text": "Écriture formatée des valeurs sur la sortie standard (`stdout`) du terminal."}
            ],
            "python_runner": {
                "prompt": "Exécutez le script et testez la différence entre une chaîne de caractères et un entier converti avec int() :",
                "initial_code": _read("01_variables_et_types.py") + "\n\n# Test de conversion d'un paramètre reçu sous forme de texte :\nparametre_url = \"15\"\nplaces_totales = int(parametre_url) + 5\nprint(\"Places après conversion int() :\", places_totales)"
            },
            "vscode_instructions": {
                "filename": "day_0/01_variables_et_types.py",
                "steps": [
                    "Ouvrir le répertoire du projet dans **VS Code** ou **Antigravity IDE**.",
                    "Sélectionner le fichier `day_0/01_variables_et_types.py` dans l'explorateur.",
                    "Dans le terminal intégré (`Ctrl + ù`), exécuter : `python day_0/01_variables_et_types.py`."
                ]
            }
        },
        {
            "id": "d0-l2",
            "file": "day_0/02_listes_et_dictionnaires.py",
            "title": "0.2 — Structures de Données Imbriquées : Listes `[ ]`, Dictionnaires `{ }` & Lecture Sécurisée `.get()`",
            "duration": "50 min",
            "analogy": {
                "title": "Le registre tabulaire composé de fiches structurées",
                "text": "Dans un système d'information réel, une donnée n'est jamais isolée : une formation possède un intitulé, une durée, un formateur (qui a lui-même un nom et un grade) et une liste de stagiaires inscrits. En Python comme en JSON, cette hiérarchie s'exprime en **imbriquant des Dictionnaires `{ }` et des Listes `[ ]`**."
            },
            "explanation": [
                "**1. Pourquoi le Dictionnaire `{ }` est la pierre angulaire des APIs** : Un dictionnaire fonctionne par **table de hachage** (recherche quasi instantanée par clé). Au lieu de se souvenir que le prénom est dans la colonne n°2, on écrit explicitement `stagiaire[\"prenom\"]`.",
                "**2. Différence critique entre `d[\"cle\"]` et `d.get(\"cle\", valeur_par_defaut)`** :\n  - Si un client envoie un JSON incomplet et que vous écrivez `corps[\"salle\"]`, Python lève une erreur fatale `KeyError: 'salle'` qui interrompt la requête avec une erreur `500`.\n  - En écrivant `corps.get(\"salle\", \"Salle A\")`, Python renvoie la valeur de `\"salle\"` si elle existe, ou `\"Salle A\"` si le client ne l'a pas précisée, **sans jamais planter** !",
                "**3. Manipulation des Listes `[ ]`** :\n  - `len(ma_liste)` retourne le nombre total d'éléments.\n  - `ma_liste.append(element)` ajoute un élément à la fin.\n  - Compréhension de liste : `[f for f in formations if f[\"places\"] >= 15]` filtre une collection en une seule ligne lisible."
            ],
            "code": _read("02_listes_et_dictionnaires.py"),
            "line_explanations": [
                {"lines": "5-10", "text": "Dictionnaire modélisant une entité `stagiaire` dont la clé `\"competences\"` contient elle-même une liste de chaînes."},
                {"lines": "13", "text": "Accès direct à la valeur associée à la clé `\"prenom\"`."},
                {"lines": "16", "text": "Ajout dynamique d'un nouvel attribut `\"ville\"` au dictionnaire existant."},
                {"lines": "20-27", "text": "Modélisation d'une collection d'entités (liste de dictionnaires), ajout via `.append()` et itération avec `for`."}
            ],
            "python_runner": {
                "prompt": "Expérimentez l'accès sécurisé avec .get() et le filtrage d'une liste de dictionnaires :",
                "initial_code": _read("02_listes_et_dictionnaires.py") + "\n\n# Lecture sécurisée avec .get() d'une clé optionnelle :\nsalle = stagiaire.get(\"salle_affectee\", \"Non attribuée\")\nprint(\"\\nSalle affectée (via .get) :\", salle)"
            },
            "vscode_instructions": {
                "filename": "day_0/02_listes_et_dictionnaires.py",
                "steps": [
                    "Ouvrir `day_0/02_listes_et_dictionnaires.py` dans votre éditeur.",
                    "Exécuter `python day_0/02_listes_et_dictionnaires.py`."
                ]
            }
        },
        {
            "id": "d0-l3",
            "file": "day_0/03_fonctions.py",
            "title": "0.3 — Fonctions (`def`, `return`), Paramètres par Défaut & Découpage Modulaire",
            "duration": "45 min",
            "analogy": {
                "title": "Le contrat d'interface d'un composant logiciel",
                "text": "Une fonction définit un **contrat strict** : quelles données elle exige en entrée (ses paramètres) et quelle structure elle garantit en sortie (`return`). En architecture API, chaque endpoint HTTP n'est rien d'autre qu'une fonction Python exposée sur le réseau."
            },
            "explanation": [
                "**1. Différence fondamentale entre `print()` et `return`** :\n  - `print()` affiche du texte dans la console du serveur pour le développeur ; le client réseau ne le voit jamais.\n  - `return` transmet effectivement la donnée de sortie au programme appelant (ou à FastAPI pour la sérialiser et l'envoyer sur le réseau) et **termine immédiatement** l'exécution de la fonction.",
                "**2. Paramètres avec valeur par défaut** : `def calculer_ttc(prix_ht, taux=0.19):` permet d'appeler `calculer_ttc(1000)` (utilise 19% par défaut) ou `calculer_ttc(1000, 0.09)` (applique 9%).",
                "**3. Portée des variables (Locale vs Globale)** : Une variable créée à l'intérieur d'une fonction (`tva`, `prix_total`) est **locale** : elle n'existe que pendant l'exécution de la fonction et n'interfère pas avec le reste du programme."
            ],
            "code": _read("03_fonctions.py"),
            "line_explanations": [
                {"lines": "4", "text": "Signature de la fonction `calculer_ttc` acceptant l'argument `prix_ht`."},
                {"lines": "5-6", "text": "Variables locales `tva` et `prix_total` calculées lors de l'appel."},
                {"lines": "7-11", "text": "L'instruction `return` renvoie un dictionnaire structuré prêt à être sérialisé en JSON."},
                {"lines": "13-14", "text": "Invocation de la fonction et récupération du dictionnaire retourné dans `facture`."}
            ],
            "python_runner": {
                "prompt": "Ajoutez un paramètre optionnel taux_tva=0.19 à la fonction et testez plusieurs appels :",
                "initial_code": _read("03_fonctions.py")
            },
            "vscode_instructions": {
                "filename": "day_0/03_fonctions.py",
                "steps": [
                    "Ouvrir `day_0/03_fonctions.py` et vérifier l'indentation de 4 espaces.",
                    "Exécuter `python day_0/03_fonctions.py`."
                ]
            }
        },
        {
            "id": "d0-l4",
            "file": "day_0/04_exceptions_et_decorateurs.py",
            "title": "0.4 — Gestion des Exceptions (`try / except`) & Comprendre les Décorateurs (`@`)",
            "duration": "55 min",
            "analogy": {
                "title": "Le disjoncteur différentiel (try/except) et le sas de contrôle (Décorateur @)",
                "text": "Deux mécanismes Python reviennent dans 100% des APIs professionnelles :\n1. Le bloc **`try / except`** agit comme un disjoncteur : si une conversion ou une requête échoue, il intercepte l'anomalie sans faire sauter tout le serveur.\n2. Le **Décorateur `@`** agit comme un sas de sécurité placé devant une salle : toute personne voulant entrer dans la fonction doit d'abord traverser le décorateur (qui vérifie par exemple l'URL `@app.route`, le jeton `@token_requis` ou le quota `@rate_limit`)."
            },
            "explanation": [
                "**1. Pourquoi `try / except` est vital dans un service Web** : Les clients d'une API envoient régulièrement des données imprévues (`?page=abc` au lieu de `?page=2`, JSON mal formé, fichier manquant). Sans `try / except`, Python lève une exception non gérée et le serveur renvoie une erreur brutale `500 Internal Server Error`. Avec `try / except ValueError:`, vous interceptez l'erreur et renvoyez proprement un code `400 Bad Request` explicite.",
                "**2. Démystifier le symbole `@` (Décorateur Python)** :\n  - En Python, les fonctions sont des objets comme les autres : une fonction peut recevoir une autre fonction en paramètre et l'entourer d'un pré-traitement et d'un post-traitement.\n  - Écrire `@journaliser_execution` juste au-dessus de `def traiter_inscription(...)` demande simplement à Python d'exécuter automatiquement le code du décorateur avant et après chaque appel de `traiter_inscription`.\n  - C'est exactement ainsi que fonctionnent `@app.get('/api/...')`, `@app.post('/api/...')` et `@app.middleware('http')` dans FastAPI !"
            ],
            "code": _read("04_exceptions_et_decorateurs.py"),
            "line_explanations": [
                {"lines": "8-18", "text": "Le bloc `try` tente `int(valeur_texte)`. Si la chaîne vaut `'abc'`, `except ValueError:` intercepte l'exception et retourne un dictionnaire d'erreur contrôlé."},
                {"lines": "28-40", "text": "Définition d'un décorateur `journaliser_execution` : la fonction interne `enveloppe` démarre un chronomètre, appelle `fonction_originale`, mesure le temps écoulé en millisecondes et affiche une trace d'audit."},
                {"lines": "42-44", "text": "`@journaliser_execution` branche automatiquement ce chronomètre d'audit sur `traiter_inscription` sans polluer le code métier de la fonction."}
            ],
            "python_runner": {
                "prompt": "Exécutez day_0/04_exceptions_et_decorateurs.py pour observer la capture d'exception et le décorateur d'audit en action :",
                "initial_code": _read("04_exceptions_et_decorateurs.py")
            },
            "vscode_instructions": {
                "filename": "day_0/04_exceptions_et_decorateurs.py",
                "steps": [
                    "Ouvrir `day_0/04_exceptions_et_decorateurs.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `python day_0/04_exceptions_et_decorateurs.py` et observer comment le décorateur `@` encadre l'appel de la fonction."
                ]
            }
        }
    ]
}
