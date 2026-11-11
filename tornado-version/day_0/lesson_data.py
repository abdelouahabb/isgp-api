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
                "text": (
                    "Lorsqu'un processus Python démarre sur un serveur Linux, le noyau du système d'exploitation lui attribue un segment isolé de **mémoire vive (RAM)** appelé le tas (*heap*). "
                    "Contrairement aux langages compilés de bas niveau où une variable désigne directement une boîte mémoire d'une taille figée à l'avance, une variable Python agit comme une étiquette symbolique reliée par un pointeur mémoire vers un objet complet doté d'une valeur, d'un compteur de références et d'un descripteur de **type** explicite.\n\n"
                    "Comprendre cette architecture mémoire constitue le socle de toute ingénierie d'API Web avec Tornado. "
                    "Sur le câble réseau, une URL ou un en-tête HTTP circule exclusivement sous forme de séquences d'octets textuels décodés en chaînes `str`, tandis que la logique métier, les calculs financiers et la sérialisation JSON exigent une distinction stricte entre textes, entiers `int`, flottants `float`, booléens `bool` et marqueur d'absence `None`."
                )
            },
            "explanation": [
                (
                    "**Mécanisme d'affectation par référence et volatilité de la RAM.** "
                    "L'opérateur `=` n'exprime pas une équation algébrique mais une séquence d'allocation en deux temps : l'interpréteur CPython évalue d'abord intégralement l'expression située à droite (`duree_jours * heures_par_jour`), alloue en mémoire vive une structure `PyObject` contenant le résultat `30`, puis attache le nom symbolique `total_heures` à l'adresse de cet objet. "
                    "Parce que toute la mémoire vive est volatile par construction électronique, l'arrêt du processus Python ou une coupure d'alimentation détruit instantanément ces structures, ce qui justifiera le recours à un moteur transactionnel sur disque au Jour 3."
                ),
                (
                    "**Correspondance bijective entre les cinq types primitifs Python et la grammaire JSON (RFC 8259).** "
                    "Tout contrat d'échange RESTful repose sur cinq types scalaires fondamentaux que `RequestHandler.write()` traduit nativement vers le standard JSON : la chaîne Unicode `str` entourée de guillemets pour les textes et horodatages ISO 8601, l'entier de précision arbitraire `int` pour les clés primaires, codes de statut HTTP et montants exprimés en centimes, le nombre binaire à virgule flottante IEEE 754 `float` pour les grandeurs continues, le booléen `bool` (`True` ou `False` avec majuscule en Python, sérialisé en `true` ou `false` en JSON), ainsi que le singleton `None` qui matérialise l'absence explicite de valeur (`null` sur le réseau)."
                ),
                (
                    "**Typage dynamique fort et conversion explicite des entrées réseau.** "
                    "Python applique un typage dynamique (aucune déclaration préalable de type sur l'identifiant) mais **strictement fort** : il refuse toute coercition implicite silencieuse entre texte et nombre afin de prévenir les corruptions de calcul. "
                    "Dans un `RequestHandler` Tornado, un paramètre extrait de la chaîne de requête tel que `self.get_query_argument('places', '15')` est toujours restitué sous forme de chaîne `\"15\"` ; additionner `\"15\" + \"5\"` concatène les caractères en `\"155\"`, d'où l'obligation absolue de convertir explicitement l'entrée via `int(...)` ou `float(...)` avant toute opération arithmétique."
                )
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
                "text": (
                    "Dans un système d'information d'entreprise, une donnée métier n'existe jamais de manière atomique et isolée : un dossier de formation regroupe un identifiant unique, un intitulé, un quota de places, la fiche signalétique d'un formateur (elle-même dotée d'un nom et d'un grade) ainsi que la séquence ordonnée des stagiaires inscrits.\n\n"
                    "Aussi bien en mémoire Python que dans le format d'échange JSON sur le fil réseau, toute cette richesse documentaire s'exprime par la composition récursive de deux structures complémentaires : le **dictionnaire (`dict`)** qui associe des attributs nommés à leurs valeurs, et la **liste (`list`)** qui ordonne des collections homogènes d'entités."
                )
            },
            "explanation": [
                (
                    "**Indexation en temps constant `O(1)` par table de hachage (`dict`).** "
                    "Contrairement à un tableau positionnel où la signification d'une donnée dépend d'un numéro de colonne fragile, un dictionnaire Python calcule l'empreinte de hachage (`hash()`) de chaque clé pour localiser sa valeur instantanément en mémoire vive, quelle que soit la taille de l'objet. "
                    "Dans Tornado, cette structure joue un rôle architectural privilégié : transmettre un `dict` directement à `self.write(payload)` déclenche sa sérialisation automatique en JSON UTF-8 accompagnée de l'en-tête normatif `Content-Type: application/json; charset=UTF-8`."
                ),
                (
                    "**Lecture défensive par `.get()` face aux charges utiles incomplètes.** "
                    "Lorsqu'un client HTTP soumet un corps JSON partiel et que le serveur évalue l'accès direct `corps[\"salle\"]`, l'absence de la clé provoque immédiatement la levée d'une exception non interceptée `KeyError`, que Tornado traduit en panne serveur `500 Internal Server Error`. "
                    "L'idiome défensif `corps.get(\"salle\", \"Salle A\")` interroge la table de hachage sans jamais lever d'exception : il restitue la valeur fournie par le client si la clé est présente, ou se replie gracieusement sur la valeur par défaut spécifiée."
                ),
                (
                    "**Collections dynamiques (`list`), découpage et enveloppe racine dans Tornado.** "
                    "Une liste Python maintient en mémoire un tableau contigu de références ordonnées dès l'indice `0`, supportant le comptage en temps constant via `len(collection)`, l'ajout amorti en fin de séquence via `.append(item)` et le filtrage déclaratif par compréhension `[f for f in formations if f[\"places\"] >= 15]`. "
                    "Pour prévenir d'anciennes vulnérabilités d'interception JSON côté navigateur (*JSON Hijacking*) et favoriser l'extensibilité des contrats, `RequestHandler.write()` refuse les listes nues à la racine et impose de les encapsuler dans un dictionnaire porteur de métadonnées tel que `{\"total\": len(items), \"data\": items}`."
                )
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
                "text": (
                    "Une fonction bien conçue matérialise une frontière contractuelle étanche à l'intérieur d'un logiciel : sa signature déclare explicitement les paramètres qu'elle exige en entrée, son corps encapsule la transformation métier à l'abri du reste du système, et son instruction `return` garantit la structure exacte de la valeur restituée.\n\n"
                    "En architecture backend avec Tornado, cette séparation revêt une importance capitale : les calculs fiscaux, les règles d'éligibilité et la validation des données résident dans des fonctions Python pures et testables en quelques microsecondes, que les méthodes `get()` ou `post()` d'un `RequestHandler` se contentent d'orchestrer et d'exposer sur le réseau HTTP."
                )
            },
            "explanation": [
                (
                    "**Séparation stricte entre sortie standard (`print`) et transmission de valeur (`return` / `self.write`).** "
                    "L'instruction `print()` écrit uniquement une chaîne de diagnostic sur le descripteur de fichier `stdout` du terminal serveur destiné à l'administrateur système ; pas un seul octet n'atteint le socket TCP du client distant. "
                    "Seule l'instruction `return` restitue l'objet calculé à l'appelant Python, lequel est ensuite poussé dans le tampon réseau de la connexion HTTP par `self.write(facture)` au sein du `RequestHandler` Tornado."
                ),
                (
                    "**Flexibilité contractuelle par paramètres à valeur par défaut.** "
                    "Définir une signature telle que `def calculer_ttc(prix_ht, taux=0.19):` permet de stabiliser le cas nominal tout en autorisant les surcharges ponctuelles : un appel `calculer_ttc(1000)` applique automatiquement le taux légal standard de 19 %, tandis que `calculer_ttc(1000, 0.09)` substitue un taux réduit sans dupliquer la logique de calcul. "
                    "On veillera toujours à n'utiliser que des objets immuables (`None`, `int`, `float`, `str`, `tuple`) comme valeurs par défaut afin d'éviter tout partage accidentel d'état mutable entre deux appels successifs."
                ),
                (
                    "**Isolation de la portée locale (*Stack Frame*) et sûreté sur boucle événementielle.** "
                    "Chaque invocation de fonction alloue un cadre d'exécution privé (*frame*) où résident ses variables locales telles que `tva` et `prix_total`, lesquelles sont automatiquement réclamées par le ramasse-miettes dès l'exécution de `return`. "
                    "Sur un serveur asynchrone Tornado traitant des milliers de requêtes entrelacées sur une même `IOLoop`, confiner les calculs dans des variables locales plutôt que dans des variables globales garantit qu'aucune requête concurrente ne corrompt les montants d'un autre client."
                )
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
                "text": (
                    "Dans un immeuble industriel alimenté en haute tension, on ne laisse jamais un court-circuit localisé dans une prise faire fondre le transformateur général de tout le bâtiment : un **disjoncteur différentiel (`try / except`)** isole immédiatement la branche défaillante tout en maintenant le reste de l'installation sous tension.\n\n"
                    "Parallèlement, plutôt que de poster un vigile à l'intérieur même de chaque bureau pour contrôler les badges tout en interrompant le travail des ingénieurs, l'architecte installe un **sas périphérique unifié (`@decorateur`)** devant la porte : quiconque sollicite l'exécution d'une méthode HTTP doit d'abord franchir ce sas d'inspection (authentification, vérification de rôle ou chronométrage d'audit) avant d'atteindre le cœur métier."
                )
            },
            "explanation": [
                (
                    "**Continuité de service de l'`IOLoop` par interception ciblée des exceptions (`try / except`).** "
                    "Sur Internet, un démon Tornado reçoit en permanence des requêtes malformées : paramètres alphabétiques là où un entier est attendu (`?page=abc`), charges JSON tronquées ou contraintes SQL violées. "
                    "Sans interception ciblée (`try: ... except ValueError:`), la remontée de l'exception interrompt brutalement le `RequestHandler` par un code générique `500 Internal Server Error` ; en capturant explicitement l'exception attendue, le contrôleur préserve la propreté de ses journaux et restitue un diagnostic client exact `400 Bad Request` ou `422 Unprocessable Entity`."
                ),
                (
                    "**Fonctions d'ordre supérieur et mécanique interne des décorateurs (`@`) sur `RequestHandler`.** "
                    "Parce que les fonctions et méthodes sont des objets de première classe en Python, un décorateur n'est aucune magie syntaxique : la notation `@journaliser_execution` placée au-dessus de `def traiter_inscription(...)` réassigne simplement la fonction à une enveloppe `enveloppe(*args, **kwargs)` qui exécute un pré-traitement et un post-traitement autour de l'appel original. "
                    "Dans l'architecture orientée objet de Tornado, où chaque route est une classe héritant de `tornado.web.RequestHandler`, des décorateurs tels que `@tornado.web.authenticated` ou `@exiger_role('admin')` interceptent l'argument `self` pour inspecter `self.request.headers`, peupler `self.current_user` et court-circuiter la requête en `401` ou `403` avant même que le corps de `get()` ou `delete()` ne soit invoqué."
                )
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
