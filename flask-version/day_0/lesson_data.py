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
                "text": "Lorsqu'un interpréteur Python exécute un module ou démarre un worker WSGI sous Gunicorn, il évalue les instructions séquentiellement et alloue en **mémoire vive (`RAM`)** des objets typés référencés par des noms symboliques. Maîtriser la nature exacte de chaque type en mémoire est indispensable en ingénierie d'API : sur le réseau HTTP, tout paramètre extrait d'une URL ou d'un en-tête par Werkzeug arrive initialement sous forme de chaîne de caractères (`str`) et exige une conversion explicite vers un type numérique (`int` ou `float`) avant tout traitement arithmétique ou métier."
            },
            "explanation": [
                "**Allocation en mémoire vive et cycle de vie d'un worker WSGI.** L'opérateur d'affectation `=` évalue d'abord intégralement l'expression située à droite avant de lier la référence de l'objet produit au nom situé à gauche (`total_heures = duree_jours * heures_par_jour`). Tant que le processus Python demeure actif, ces structures résident en RAM, mais le moindre arrêt ou recyclage d'un worker Gunicorn libère intégralement cette mémoire volatile, d'où l'obligation d'adosser une API de production à un moteur de base de données relationnel.",
                "**Correspondance stricte entre types primitifs Python et sérialisation JSON.** Cinq types fondamentaux structurent les échanges dans Flask : `str` encode du texte Unicode UTF-8 sérialisé entre guillemets JSON, `int` représente un entier de précision arbitraire idéal pour les identifiants primaires, les codes HTTP et les montants monétaires en centimes, `float` modélise un nombre décimal IEEE 754, `bool` exprime les états logiques `True` ou `False` traduits en `true` ou `false`, et le singleton `None` désigne l'absence de valeur convertie en `null` par `jsonify()`.",
                "**Typage fort et désambiguïsation des entrées réseau.** Python applique un typage dynamique mais fort qui refuse d'additionner implicitement du texte et des nombres : l'expression `\"25\" + \"5\"` réalise une concaténation lexicographique donnant `\"255\"`, tandis que `25 + 5` effectue une addition entière produisant `30`. Comme la passerelle WSGI (`PEP 3333`) expose la `QUERY_STRING` sous forme textuelle, le développeur doit convertir explicitement les entrées via `int()`, `float()` ou l'argument `type=` de `request.args.get()`."
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
                "text": "Dans un système d'information réel, une donnée métier n'existe jamais de manière isolée : une session de formation agrège un intitulé, une durée, un formateur disposant de ses propres attributs et une collection ordonnée de participants inscrits. En Python comme dans le format d'échange JSON exploité par Flask et Werkzeug, cette hiérarchie documentaire s'exprime naturellement en **imbriquant des dictionnaires `{ }` et des listes `[ ]`**."
            },
            "explanation": [
                "**Complexité constante des dictionnaires par table de hachage.** En Python, un `dict` (`{ }`) s'appuie sur une table de hachage interne qui résout l'accès à une clé en temps moyen constant `O(1)`, quelle que soit la taille de la structure. Au lieu de mémoriser un indice de colonne fragile comme dans un tableau positionnel, le développeur interroge explicitement la propriété nommée `stagiaire[\"prenom\"]`, ce qui garantit une correspondance bijective immédiate avec les objets JSON manipulés par Flask.",
                "**Lecture défensive par `.get()` face aux charges utiles incomplètes.** Lorsqu'un client HTTP soumet un corps JSON partiel à `request.get_json()` et que la vue exécute `corps[\"salle\"]`, l'interpréteur lève une exception `KeyError` non interceptée qui provoque une réponse brutale `500 Internal Server Error`. L'appel sécurisé `corps.get(\"salle\", \"Salle A\")` consulte la table de hachage sans jamais lever d'exception et retourne une valeur par défaut maîtrisée dès que l'attribut est absent.",
                "**Séquences dynamiques et filtrage déclaratif des listes.** Une `list` (`[ ]`) maintient en mémoire une collection ordonnée et mutable dont la taille s'obtient instantanément par `len(ma_liste)` et qui s'enrichit en fin de séquence via `ma_liste.append(element)`. Lorsqu'une route Flask doit extraire un sous-ensemble d'enregistrements avant sérialisation, la compréhension de liste `[f for f in formations if f[\"places\"] >= 15]` condense l'itération et le prédicat de filtrage en une seule expression atomique et performante."
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
                "text": "Une fonction matérialise un **contrat d'interface déterministe** qui spécifie avec précision les paramètres exigés en entrée et la structure de données garantie en sortie via `return`. Dans une architecture Flask conforme au standard WSGI (`PEP 3333`), chaque route HTTP enregistrée sur l'application n'est rien d'autre qu'une fonction Python dite *vue* (*view function*) dont la valeur de retour est transformée par Werkzeug en réponse réseau."
            },
            "explanation": [
                "**Séparation stricte entre sortie standard `print()` et valeur de retour `return`.** L'instruction `print()` écrit uniquement une trace textuelle sur le descripteur `stdout` du worker Gunicorn ou du terminal local, totalement invisible pour le client HTTP distant. Seule l'instruction `return` interrompt immédiatement l'exécution de la fonction pour remettre l'objet résultant à l'appelant — ou au moteur de dispatch Flask chargé d'émettre la trame HTTP sur le socket réseau.",
                "**Flexibilité contractuelle par paramètres à valeur par défaut.** Une signature telle que `def calculer_ttc(prix_ht, taux=0.19):` rend le second argument optionnel lors de l'invocation tout en documentant explicitement la règle métier nominale. L'appelant peut ainsi écrire `calculer_ttc(1000)` pour appliquer automatiquement la fiscalité à 19 %, ou surcharger ponctuellement ce comportement par `calculer_ttc(1000, 0.09)` sans dupliquer la logique de calcul.",
                "**Isolation mémoire par portée lexicale locale.** Toute variable instanciée dans le corps d'une fonction (`tva`, `prix_total`) réside dans un cadre d'exécution (*stack frame*) strictement local qui est détruit dès le franchissement du `return`. Ce cloisonnement lexical protège l'application contre les effets de bord accidentels et garantit que deux appels successifs d'une vue Flask ne polluent pas leurs variables intermédiaires respectives."
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
                "text": "Deux mécanismes du langage Python soutiennent l'intégralité de l'architecture interne de Flask. D'une part, la structure **`try / except`** opère comme un disjoncteur sélectif : lorsqu'une conversion de type, une lecture JSON ou une requête SQL échoue, elle intercepte proprement l'exception avant qu'elle ne remonte jusqu'au serveur WSGI.\n\nD'autre part, le **décorateur `@`** agit comme un sas de contrôle placé en amont et en aval d'une fonction : tout appel ciblant la vue traverse d'abord cette enveloppe d'ordre supérieur, qui orchestre aussi bien l'enregistrement dans la table de routage Werkzeug (`@app.route`) que le filtrage cryptographique (`@exiger_role`) ou le contrôle de quota."
            },
            "explanation": [
                "**Confinement des anomalies d'exécution par interception ciblée `try / except`.** Sur Internet, les clients soumettent fréquemment des paramètres malformés tels que `?page=abc` au lieu d'un entier valide ou des corps JSON tronqués. Sans capture explicite, `int('abc')` propage une exception `ValueError` jusqu'à la couche WSGI qui répond par une erreur générique `500 Internal Server Error`, alors qu'un bloc `try / except ValueError:` isole la défaillance et restitue un diagnostic contrôlé `400 Bad Request`.",
                "**Fonctions d'ordre supérieur et mécanique interne du décorateur `@`.** En Python, les fonctions sont des objets de première classe pouvant être transmis en argument à une fonction enveloppante (*wrapper*) et retournés enrichis d'un pré-traitement et d'un post-traitement. Annoter `def traiter_inscription(...)` par `@journaliser_execution` équivaut exactement à réaffecter `traiter_inscription = journaliser_execution(traiter_inscription)`, ce qui permet d'instrumenter la journalisation, le chronométrage ou l'authentification sans altérer la lisibilité du code métier.",
                "**Exploitation des décorateurs dans le routage et la sécurité Flask.** Flask s'appuie directement sur ce patron syntaxique : `@app.route('/api/formations')` inscrit la fonction de vue dans la `Map` d'URLs de Werkzeug au démarrage du processus, tandis que des décorateurs personnalisés s'exécutent à chaque requête entrante pour valider un jeton Bearer avant d'autoriser l'invocation de la vue."
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
