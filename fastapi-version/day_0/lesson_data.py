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
                    "Lorsqu'un interpréteur CPython exécute un module, il compile d'abord le code source en bytecode puis évalue chaque instruction séquentiellement de haut en bas. Créer une variable revient à allouer une structure typée (`PyObject`) en **mémoire vive (RAM)** et à y attacher une étiquette symbolique dans l'espace de noms courant.\n\n"
                    "Saisir la nature physique exacte — le **type** — de chaque valeur logée en mémoire constitue le premier réflexe d'un ingénieur d'API : tout paramètre qui franchit une socket réseau dans une URL ou un en-tête HTTP arrive initialement sous forme d'octets décodés en texte (`str`), et doit être validé puis converti explicitement en type numérique (`int` ou `float`) ou booléen (`bool`) avant le moindre traitement métier."
                )
            },
            "explanation": [
                "**Affectation par référence et volatilité de la RAM.** En Python, l'opérateur `=` ne pose pas une équation algébrique mais exécute une affectation directionnelle : l'interpréteur évalue intégralement l'expression située à droite (`duree_jours * heures_par_jour`), alloue en mémoire vive un objet immuable contenant le résultat `30`, puis relie le nom `total_heures` à l'adresse de cet objet. Dès que le processus serveur Uvicorn s'arrête ou redémarre, toutes les pages de mémoire vive associées sont restituées au système d'exploitation, ce qui justifiera le recours à une base transactionnelle sur disque au Jour 3.",
                "**Correspondance stricte entre types scalaires Python et primitives JSON (RFC 8259).** Tout contrat d'échange REST repose sur cinq types scalaires Python que le moteur Rust `pydantic-core` de FastAPI sérialise nativement sur le réseau : `str` produit une chaîne UTF-8 entre guillemets doubles (`\"ISGP\"`), `int` produit un nombre entier exact utilisé pour les identifiants primaires, les compteurs et les montants exprimés en centimes (`200`), `float` représente une grandeur décimale IEEE 754 (`19.5`), `bool` traduit les états logiques `True` et `False` en littéraux JSON minuscules `true` et `false`, tandis que le singleton `None` matérialise l'absence explicite de valeur sous la forme `null`.",
                "**Typage dynamique fort et coercition contrôlée des entrées réseau.** Contrairement aux langages à coercition implicite laxiste, Python applique un typage fort qui interdit de combiner sans conversion une représentation textuelle et une grandeur arithmétique : l'expression `\"25\" + \"5\"` réalise une concaténation lexicographique produisant `\"255\"`, tandis que `25 + 5` additionne deux entiers en `30` et que `\"25\" + 5` lève immédiatement une exception `TypeError`. Dans une architecture FastAPI, cette frontière est franchie proprement par conversion explicite (`int(\"25\")`, `float(\"19.5\")`) ou déclarativement via les annotations de type inspectées par Pydantic v2."
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
                    "Dans un système d'information d'entreprise, une donnée métier ne voyage jamais à l'état d'atome isolé : une session de formation possède un intitulé, une durée, un formateur — lui-même décrit par son identité et son grade — ainsi qu'une séquence ordonnée de stagiaires inscrits.\n\n"
                    "En mémoire Python comme sur le fil réseau JSON, toute cette richesse relationnelle s'exprime par la composition récursive de deux structures complémentaires : le **Dictionnaire (`dict`, noté `{ }`)** qui modélise une entité unique par ses attributs nommés, et la **Liste (`list`, notée `[ ]`)** qui ordonne une collection homogène d'entités."
                )
            },
            "explanation": [
                "**Indexation en temps constant `O(1)` par table de hachage (`dict`).** Le dictionnaire Python constitue la structure native miroir d'un objet JSON : l'interpréteur calcule l'empreinte de hachage (`hash()`) de chaque clé textuelle pour localiser instantanément le pointeur de la valeur associée en mémoire vive, indépendamment de la taille du dictionnaire. Plutôt que de manipuler des indices numériques fragiles comme une colonne anonyme n°2, le code métier désigne explicitement chaque propriété par son nom sémantique (`stagiaire[\"prenom\"]`).",
                "**Lecture défensive par `.get()` face aux charges utiles partielles.** Lorsqu'un client externe transmet un document JSON incomplet ou omet un attribut facultatif, un accès direct par crochets `corps[\"salle\"]` lève immédiatement une exception non gérée `KeyError` qui avorte le traitement de la requête par une erreur serveur `500 Internal Server Error`. L'invocation défensive `corps.get(\"salle\", \"Salle A\")` interroge la table de hachage sans jamais lever d'exception : elle restitue la valeur présente ou se replie gracieusement sur la valeur par défaut spécifiée.",
                "**Tableaux dynamiques (`list`) et transformations déclaratives en mémoire.** Une liste Python maintient en mémoire un vecteur contigu de références ordonnées dont la cardinalité s'obtient en `O(1)` via `len(ma_liste)` et qui s'étend en fin de séquence en temps amorti constant par `ma_liste.append(element)`. Pour projeter ou filtrer une collection issue d'une requête métier avant sa sérialisation par FastAPI, les compréhensions de liste comme `[f for f in formations if f[\"places\"] >= 15]` expriment la sélection en une seule construction atomique, lisible et optimisée au niveau du bytecode CPython."
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
                    "En ingénierie logicielle, une fonction matérialise une **frontière contractuelle stricte** : sa signature déclare exactement les paramètres qu'elle exige en entrée, son corps encapsule la transformation métier à l'abri du reste du programme, et son instruction `return` scelle la structure garantie en sortie.\n\n"
                    "Ce modèle est identique à celui d'une architecture FastAPI : chaque route HTTP exposée sur le réseau n'est rien d'autre qu'une fonction Python dont les paramètres d'entrée proviennent de la requête HTTP et dont la valeur de retour devient le corps JSON de la réponse."
                )
            },
            "explanation": [
                "**Distinction vitale entre écriture console (`print`) et restitution réseau (`return`).** L'appel `print()` se contente de formater des caractères vers le descripteur de sortie standard (`stdout`) du processus serveur pour les journaux d'exploitation : le client HTTP distant n'en reçoit pas le moindre octet. Seule l'instruction `return` clôt immédiatement le cadre d'exécution (*stack frame*) de la fonction et transmet l'objet Python résultant au moteur ASGI de FastAPI, qui se charge alors de le sérialiser en flux JSON UTF-8 sur la connexion TCP.",
                "**Signature explicite et arguments optionnels à valeur par défaut.** Définir une signature telle que `def calculer_ttc(prix_ht: float, taux: float = 0.19):` permet de rendre un comportement paramétrable sans alourdir les cas nominaux : un appel `calculer_ttc(1000)` applique automatiquement le taux légal par défaut de 19 %, tandis qu'un appel explicite `calculer_ttc(1000, 0.09)` lui substitue un taux réduit. FastAPI exploite exactement cette mécanique d'introspection sur les valeurs par défaut pour distinguer dans OpenAPI 3.1 les paramètres HTTP obligatoires des filtres facultatifs.",
                "**Isolation mémoire de la portée locale (*Lexical Scope*) face à la concurrence.** Toute variable instanciée à l'intérieur du bloc indenté d'une fonction (`tva`, `prix_total`) réside dans un dictionnaire local propre à cet appel précis et disparaît dès que `return` est franchi. Sur un serveur asynchrone Uvicorn traitant des centaines de requêtes simultanées, cette isolation garantit que le calcul de facturation du client A ne peut jamais contaminer ni écraser les variables intermédiaires du client B."
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
                    "Deux constructions du langage Python forment l'ossature de la totalité des serveurs FastAPI en production. La première, le bloc **`try / except`**, agit exactement comme un disjoncteur différentiel divisionnaire : lorsqu'une conversion de type échoue ou qu'une contrainte de base de données est violée sur une requête précise, il isole l'incident localement et renvoie une réponse contrôlée sans jamais provoquer l'extinction générale du serveur.\n\n"
                    "La seconde, le **Décorateur `@`**, opère comme un portique d'enregistrement et de contrôle placé devant l'entrée d'une salle : il enveloppe une fonction métier pour l'inscrire dans une table de routage ou greffer un traitement transversal — chronométrage d'audit, vérification de politique, enregistrement d'endpoint `@app.get` — sans polluer la logique interne de la fonction."
                )
            },
            "explanation": [
                "**Résilience transactionnelle et traduction des exceptions en codes HTTP (`try / except`).** Sur un réseau ouvert, les applications clientes transmettent inévitablement des charges utiles altérées, des paramètres mal typés (`?page=abc`) ou des clés dupliquées. Laisser une exception Python (`ValueError`, `KeyError`, `sqlite3.IntegrityError`) remonter sans interception force le serveur ASGI à avorter la requête par un code générique `500 Internal Server Error` ; l'encapsuler dans une clause `except ValueError:` ciblée permet au contraire de qualifier sémantiquement le rejet par un statut `400 Bad Request` ou `422 Unprocessable Content` accompagné d'un diagnostic JSON exploitable.",
                "**Fonctions d'ordre supérieur et mécanique interne des décorateurs (`@`).** En Python, toute fonction est un objet de première classe pouvant être transmis en argument à une autre fonction ou encapsulé dans une fermeture lexicale (*closure*). Placer `@journaliser_execution` au-dessus de `def traiter_inscription(...)` exécute à la définition du module la réaffectation `traiter_inscription = journaliser_execution(traiter_inscription)` : c'est exactement ce mécanisme d'ordre supérieur qu'exploitent `@app.get('/api/...')`, `@app.post('/api/...')` et `@app.middleware('http')` dans FastAPI pour inspecter la signature typée de vos routes et bâtir l'arbre de routage ASGI ainsi que le schéma OpenAPI 3.1."
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
