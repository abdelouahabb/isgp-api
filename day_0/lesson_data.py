import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_0_DATA = {
    "day_number": 0,
    "folder": "day_0",
    "badge": "Jour 0 • Mise à Niveau",
    "title": "Fondations Python & Éditeur (Zéro Prérequis)",
    "goal": "Aligner l'ensemble des participants sur un socle commun avant d'aborder le réseau : variables, listes, dictionnaires, fonctions et exécution de scripts dans le dossier day_0/.",
    "starter_filename": "day_0/02_listes_et_dictionnaires.py",
    "files": [
        "day_0/01_variables_et_types.py",
        "day_0/02_listes_et_dictionnaires.py",
        "day_0/03_fonctions.py",
    ],
    "lessons": [
        {
            "id": "d0-l1",
            "file": "day_0/01_variables_et_types.py",
            "title": "0.1 — Variables, Chaînes & Nombres",
            "duration": "30 min",
            "analogy": {
                "title": "Les dossiers étiquetés en mémoire",
                "text": "Un script Python est exécuté séquentiellement de haut en bas. Pour conserver une donnée en mémoire vive et la réutiliser dans la suite du traitement, on lui attribue un identifiant nommé : c'est une **Variable**."
            },
            "explanation": [
                "**Affectation (`=`)** : En Python, l'opérateur `=` stocke la valeur située à droite dans le nom de variable situé à gauche.",
                "**Les trois types scalaires élémentaires** :\n  1. **Chaîne de caractères (`str`)** : délimitée par des guillemets doubles `\"...\"` ou simples `'...'`.\n  2. **Nombre (`int` / `float`)** : saisi directement sans guillemets (`5`, `19.5`).\n  3. **Booléen (`bool`)** : prend exclusivement la valeur `True` (vrai) ou `False` (faux)."
            ],
            "code": _read("01_variables_et_types.py"),
            "line_explanations": [
                {"lines": "1-4", "text": "`# ...` : Commentaires de documentation ignorés par l'interpréteur Python."},
                {"lines": "5-9", "text": "Déclaration des variables : chaînes (`str`), entiers (`int`) et booléen (`True`)."},
                {"lines": "11", "text": "Calcul arithmétique stocké dans la variable `total_heures`."},
                {"lines": "13-16", "text": "`print(...)` écrit le contenu des variables sur la sortie standard (terminal)."}
            ],
            "python_runner": {
                "prompt": "Modifiez les valeurs du fichier day_0/01_variables_et_types.py ci-dessous et cliquez sur « Exécuter » :",
                "initial_code": _read("01_variables_et_types.py")
            },
            "vscode_instructions": {
                "filename": "day_0/01_variables_et_types.py",
                "steps": [
                    "Ouvrir le dossier du projet dans **VS Code** ou **Antigravity IDE**.",
                    "Ouvrir le fichier `day_0/01_variables_et_types.py` dans l'explorateur à gauche.",
                    "Dans le terminal intégré (`Ctrl + ù`), exécuter : `python day_0/01_variables_et_types.py`."
                ]
            }
        },
        {
            "id": "d0-l2",
            "file": "day_0/02_listes_et_dictionnaires.py",
            "title": "0.2 — Listes `[ ]` et Dictionnaires `{ }`",
            "duration": "45 min",
            "analogy": {
                "title": "Registre indexé vs Fiche signalétique",
                "text": "Une **Liste `[ ]`** regroupe des éléments selon un ordre séquentiel (indexés à partir de 0). Un **Dictionnaire `{ }`** structure une entité sous forme de paires `\"clé\": valeur`. L'intégralité des échanges JSON d'une API REST repose sur la combinaison de dictionnaires et de listes."
            },
            "explanation": [
                "**Le Dictionnaire `{ }`** : associe une clé textuelle unique à une valeur (`stagiaire[\"prenom\"]`).",
                "**La Liste `[ ]`** : permet de stocker une collection ordonnée d'éléments, notamment une liste de dictionnaires représentant les lignes d'une table."
            ],
            "code": _read("02_listes_et_dictionnaires.py"),
            "line_explanations": [
                {"lines": "5-10", "text": "Déclaration d'un dictionnaire comportant 4 clés, dont `competences` associée à une liste."},
                {"lines": "13", "text": "Extraction de la valeur associée à la clé `\"prenom\"`."},
                {"lines": "16", "text": "Insertion dynamique d'une nouvelle clé `\"ville\"` dans le dictionnaire."},
                {"lines": "20-27", "text": "Création d'une liste de dictionnaires, ajout d'un élément via `.append()` et parcours avec une boucle `for`."}
            ],
            "python_runner": {
                "prompt": "Exécutez et modifiez le script day_0/02_listes_et_dictionnaires.py :",
                "initial_code": _read("02_listes_et_dictionnaires.py")
            },
            "vscode_instructions": {
                "filename": "day_0/02_listes_et_dictionnaires.py",
                "steps": [
                    "Ouvrir le fichier `day_0/02_listes_et_dictionnaires.py` dans votre éditeur.",
                    "Exécuter `python day_0/02_listes_et_dictionnaires.py` dans le terminal."
                ]
            }
        },
        {
            "id": "d0-l3",
            "file": "day_0/03_fonctions.py",
            "title": "0.3 — Fonctions (`def` et `return`)",
            "duration": "40 min",
            "analogy": {
                "title": "L'unité de traitement paramétrée",
                "text": "Une **fonction** reçoit des arguments en entrée entre parenthèses, exécute une séquence d'instructions indentée, et restitue un résultat structuré à l'appelant via l'instruction **`return`**."
            },
            "explanation": [
                "**Rôle dans Flask** : Dans un serveur Flask, chaque route HTTP est rattachée à une fonction Python dont la valeur de retour (`return`) forme la réponse envoyée au client.",
                "**Règle d'indentation** : En Python, le bloc d'instructions appartenant à la fonction est obligatoirement indenté de 4 espaces."
            ],
            "code": _read("03_fonctions.py"),
            "line_explanations": [
                {"lines": "4", "text": "`def` déclare la fonction `calculer_ttc` prenant le paramètre `prix_ht`."},
                {"lines": "5-6", "text": "Calcul de la TVA (19 %) et du montant TTC à l'intérieur du bloc indenté."},
                {"lines": "7-11", "text": "`return { ... }` restitue un dictionnaire contenant les résultats calculés."},
                {"lines": "13-14", "text": "Appel de la fonction avec l'argument `1000` et affichage du dictionnaire retourné."}
            ],
            "python_runner": {
                "prompt": "Exécutez et adaptez le fichier day_0/03_fonctions.py :",
                "initial_code": _read("03_fonctions.py")
            },
            "vscode_instructions": {
                "filename": "day_0/03_fonctions.py",
                "steps": [
                    "Ouvrir `day_0/03_fonctions.py`.",
                    "Exécuter `python day_0/03_fonctions.py`."
                ]
            }
        }
    ]
}
