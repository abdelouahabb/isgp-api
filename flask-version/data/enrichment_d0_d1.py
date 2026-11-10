"""
Manuel de Référence Approfondi — Enrichissement des Chapitres (Jours 0 et 1).
Fournit pour chaque chapitre :
- context : exposé complet de la problématique d'ingénierie
- deep_sections : sous-chapitres de cours détaillés (fondements théoriques et mécanismes internes)
- architecture_diagram : schéma ASCII de flux mémoire ou réseau
- reference_table : tableau de synthèse technique
- pitfalls : anti-patterns de production vs standards industriels
- practical_exercises : exercices progressifs de révision post-bootcamp
"""

ENRICHMENT_D0_D1 = {
    # =========================================================================
    # JOUR 0 — CHAPITRE 0.1 : VARIABLES, MÉMOIRE & TYPES PRIMITIFS
    # =========================================================================
    "d0-l1": {
        "context": (
            "Avant même d'écrire une seule ligne de serveur Web ou de parler de réseau, tout service informatique "
            "manipule des informations en mémoire vive (RAM) : le nom d'un client, le montant d'une facture, le statut "
            "d'une réservation ou la date d'expiration d'un jeton.\n"
            "Dans une API Web, une erreur sur la nature exacte d'une donnée (confondre le texte `\"500\"` avec le nombre "
            "entier `500`, ou confondre une chaîne vide `\"\"` avec l'absence de valeur `None`) provoque immédiatement "
            "des bugs critiques chez les applications clientes (applications mobiles Android/iOS, frontaux React/Vue ou "
            "systèmes bancaires partenaires). Ce premier chapitre établit des fondations rigoureuses sur la gestion de "
            "la mémoire et le typage en Python dans la perspective directe des échanges JSON."
        ),
        "deep_sections": [
            {
                "heading": "1. Comment Python stocke une variable en mémoire vive (Modèle Objet & Références)",
                "body": (
                    "Lorsqu'on écrit `duree_jours = 5` en Python, le signe `=` ne désigne pas une égalité mathématique "
                    "mais une **opération d'affectation** (assignation).\n"
                    "- Python commence par évaluer l'expression située **à droite** du signe `=` : il alloue un objet de type "
                    "`int` contenant la valeur `5` dans la mémoire vive (RAM).\n"
                    "- Ensuite, il crée l'étiquette `duree_jours` (située **à gauche**) et la relie par une référence mémoire "
                    "vers cet objet.\n"
                    "- En Python, **le type est attaché à la valeur en mémoire et non au nom de la variable** : c'est ce qu'on "
                    "appelle le **typage dynamique fort**. « Dynamique » signifie que vous n'avez pas besoin de déclarer `int duree_jours` "
                    "à l'avance ; « Fort » signifie que Python refuse d'additionner implicitement un texte et un nombre (`\"5\" + 2` "
                    "déclenche immédiatement une erreur `TypeError`, contrairement à JavaScript qui produirait `\"52\"`)."
                )
            },
            {
                "heading": "2. Pourquoi le contrat de type est vital dans une API Web (Sérialisation JSON)",
                "body": (
                    "Une API Web communique avec l'extérieur via le format universel **JSON (JavaScript Object Notation)**. "
                    "Or, le standard JSON (RFC 8259) ne reconnaît que **4 types scalaires primitifs** :\n"
                    "1. Les chaînes de caractères (`string`) entourées obligatoirement de guillemets doubles `\"...\"`.\n"
                    "2. Les nombres (`number`), qu'ils soient entiers (`int`) ou décimaux (`float`).\n"
                    "3. Les booléens (`boolean`) écrits en minuscules `true` ou `false`.\n"
                    "4. La valeur nulle (`null`) représentant l'absence explicite de donnée.\n"
                    "Chaque fois que votre serveur Flask renvoie une réponse, il traduit automatiquement vos types Python "
                    "(`str`, `int`, `float`, `bool`, `None`) vers leurs équivalents JSON. Comprendre cette correspondance "
                    "garantit que votre API respecte son contrat d'interface."
                )
            },
            {
                "heading": "3. L'inspection et la validation défensive des types avec `type()` et `isinstance()`",
                "body": (
                    "Lorsqu'un client externe envoie des données à votre API, rien ne garantit qu'il a respecté la documentation : "
                    "il peut envoyer `{\"duree_jours\": \"cinq\"}` au lieu d'un entier `5`. Pour vérifier le type d'une variable "
                    "dans le code d'une API, on privilégie toujours la fonction native `isinstance(valeur, type_attendu)`.\n"
                    "- Attention à une subtilité célèbre de Python : la classe `bool` hérite historiquement de `int` (`isinstance(True, int)` "
                    "vaut `True` !). Lors d'une validation stricte d'un entier provenant d'un JSON, on vérifie donc "
                    "`isinstance(val, int) and not isinstance(val, bool)`."
                )
            }
        ],
        "architecture_diagram": (
            "ESPACE DES NOMS PYTHON (Variables)          MÉMOIRE VIVE (Objets Typés en RAM)          TRADUCTION RÉSEAU (JSON)\n"
            "----------------------------------          ----------------------------------          ------------------------\n"
            "organisme       ------------------------->  Objet <class 'str'>   \"ISGP\"          ===>  \"ISGP\"   (string)\n"
            "duree_jours     ------------------------->  Objet <class 'int'>   5               ===>  5        (number)\n"
            "taux_reussite   ------------------------->  Objet <class 'float'> 98.5            ===>  98.5     (number)\n"
            "est_ouverte     ------------------------->  Objet <class 'bool'>  True            ===>  true     (boolean)\n"
            "prerequis       ------------------------->  Objet <NoneType>      None            ===>  null     (null)"
        ),
        "reference_table": {
            "title": "Table de Correspondance Officielle : Types Python ↔ Types JSON (RFC 8259)",
            "headers": ["Type Python", "Exemple en Python", "Équivalent JSON", "Exemple en JSON", "Usage typique dans une API"],
            "rows": [
                ["`str`", "`\"Alger\"` ou `'Alger'`", "`string`", "`\"Alger\"` (guillemets doubles)", "Identifiants, titres, messages, dates ISO 8601"],
                ["`int`", "`200`, `42`, `-5`", "`number`", "`200`, `42`, `-5`", "Clés primaires (`id`), compteurs, codes HTTP, pagination"],
                ["`float`", "`19.0`, `98.45`", "`number`", "`19.0`, `98.45`", "Montants financiers, taux, coordonnées GPS, durées"],
                ["`bool`", "`True` / `False` (Majuscule)", "`boolean`", "`true` / `false` (minuscule)", "Drapeaux d'état (`actif`, `certifie`, `has_next`)"],
                ["`None`", "`None`", "`null`", "`null`", "Champ optionnel non renseigné (ex: `date_fin: null`)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Renvoyer des nombres sous forme de chaînes : `{\"id\": \"1\", \"duree\": \"5\"}`",
                "good": "Respecter les types natifs : `{\"id\": 1, \"duree\": 5}`",
                "why": "Si l'API renvoie `\"5\"` en texte, une application cliente faisant `duree + 1` en JavaScript obtiendra `\"51\"` au lieu de `6`."
            },
            {
                "bad": "Utiliser la chaîne `\"None\"` ou `\"null\"` pour indiquer l'absence de valeur",
                "good": "Utiliser le mot-clé Python `None` (sans guillemets)",
                "why": "`\"None\"` avec guillemets est une chaîne de 4 caractères (évaluée comme vraie !), tandis que `None` devient `null` en JSON."
            },
            {
                "bad": "Écrire `true` ou `false` en minuscules dans un fichier `.py`",
                "good": "Écrire `True` et `False` avec une majuscule initiale en Python",
                "why": "En Python, `true` sans majuscule déclenche une erreur `NameError: name 'true' is not defined`. C'est `json.dumps()` qui le convertit en `true` minuscule."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur Python ci-dessus, créez une variable `prix_ht = 1500.50` (`float`) et une variable `exonere_tva = False` (`bool`), puis affichez leurs types respectifs avec `type()`.",
            "Testez la différence entre `100 + 50` et `\"100\" + \"50\"` avec `print()` pour observer l'addition arithmétique face à la concaténation de chaînes.",
            "Utilisez `isinstance(True, bool)` et `isinstance(100, (int, float))` pour vérifier comment valider un montant numérique en Python."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.2 : LISTES, DICTIONNAIRES & STRUCTURES IMBRIQUÉES
    # =========================================================================
    "d0-l2": {
        "context": (
            "Une API réelle ne renvoie jamais une valeur isolée comme le chiffre `42` tout seul : elle renvoie des "
            "**documents structurés** (par exemple la fiche complète d'une formation avec son identifiant, son titre, "
            "sa salle et la liste des stagiaires inscrits).\n"
            "En Python, toute la représentation des données d'une API repose sur l'alliance de deux structures "
            "fondamentales : le **Dictionnaire (`dict`)** pour représenter une entité par ses attributs nommés, et la "
            "**Liste (`list`)** pour représenter une collection ordonnée d'entités. Maîtriser la lecture défensive et "
            "l'imbrication de ces deux structures représente 70 % du travail quotidien de manipulation de données dans Flask."
        ),
        "deep_sections": [
            {
                "heading": "1. Anatomie interne d'un Dictionnaire Python (`dict` — Table de Hachage)",
                "body": (
                    "Un dictionnaire Python (`{ \"cle\": valeur }`) est implémenté en mémoire sous forme de **table de hachage "
                    "(Hash Table)**.\n"
                    "- Cela signifie que rechercher une valeur par sa clé (`formation[\"titre\"]`) est **instantané** "
                    "(complexité constante `O(1)`), qu'il y ait 3 clés ou 1 000 000 de clés dans le dictionnaire !\n"
                    "- Chaque clé d'un dictionnaire est **unique** : si vous définissez deux fois la clé `\"salle\"`, la seconde "
                    "valeur écrase silencieusement la première.\n"
                    "- Dans le contexte d'une API REST, les clés d'un dictionnaire destiné à être converti en JSON doivent "
                    "toujours être des chaînes de caractères en `snake_case` (ex: `\"duree_jours\"`, `\"cree_par\"`)."
                )
            },
            {
                "heading": "2. Programmation Défensive : Pourquoi `.get()` évite les pannes serveur HTTP 500",
                "body": (
                    "Lorsqu'un client envoie une requête `POST` avec un objet JSON à votre serveur Flask, Python le transforme "
                    "en dictionnaire `corps`. Que se passe-t-il si vous écrivez `salle = corps[\"salle\"]` et que le client a "
                    "oublié d'inclure le champ `\"salle\"` dans son JSON ?\n"
                    "- Python lève immédiatement une exception fatale **`KeyError: 'salle'`**, qui interrompt votre fonction "
                    "et renvoie une erreur brute **`500 Internal Server Error`** au client !\n"
                    "- À l'inverse, la méthode **`corps.get(\"salle\", \"Salle A\")`** vérifie proprement si la clé existe : "
                    "si elle est présente, elle renvoie sa valeur ; si elle est absente, elle renvoie la valeur de repli "
                    "(`\"Salle A\"` ou `None` par défaut) sans jamais faire planter le serveur."
                )
            },
            {
                "heading": "3. Les Listes (`list`) et le patron universel « Liste de Dictionnaires »",
                "body": (
                    "Une liste Python (`[elem0, elem1, elem2]`) est un tableau dynamique ordonné :\n"
                    "- L'indice du premier élément est toujours **`0`** (décalage mémoire zéro depuis le début du tableau), "
                    "et l'indice **`-1`** pointe toujours sur le **dernier élément** de la liste.\n"
                    "- Lorsque vous interrogez une base de données SQL (`SELECT * FROM formations`), le résultat est toujours "
                    "transformé en une **Liste de Dictionnaires** : chaque élément de la liste `[...]` correspond à une ligne "
                    "de la table, et chaque dictionnaire `{...}` contient les colonnes de cette ligne."
                )
            }
        ],
        "architecture_diagram": (
            "TABLE SQL / COLLECTION API : formations (Liste Python [ ... ])\n"
            "+-------------------------------------------------------------------------+\n"
            "| Indice [0] -> Dictionnaire { \"id\": 1, \"titre\": \"API REST\", \"jours\": 5 } |\n"
            "| Indice [1] -> Dictionnaire { \"id\": 2, \"titre\": \"Sécurité\", \"jours\": 3 } |\n"
            "| Indice [2] -> Dictionnaire { \"id\": 3, \"titre\": \"SQLite\",   \"jours\": 2 } |\n"
            "+-------------------------------------------------------------------------+\n"
            "  Accès direct : formations[1][\"titre\"]  ===>  \"Sécurité\"\n"
            "  Accès sûr    : formations[1].get(\"salle\", \"Non attribuée\")"
        ),
        "reference_table": {
            "title": "Opérations Essentielles sur les Listes et Dictionnaires en Développement d'API",
            "headers": ["Structure", "Opération", "Syntaxe Python", "Comportement & Complexité", "Cas d'usage API"],
            "rows": [
                ["`dict`", "Lecture sûre avec défaut", "`d.get(\"cle\", defaut)`", "Ne lève jamais `KeyError` (`O(1)`)", "Lire un paramètre JSON optionnel"],
                ["`dict`", "Vérifier présence d'une clé", "`\"titre\" in d`", "Renvoie `True` ou `False` (`O(1)`)", "Valider les champs obligatoires d'un `POST`"],
                ["`dict`", "Ajout / Modification", "`d[\"statut\"] = \"actif\"`", "Crée ou écrase la clé", "Enrichir une réponse avec un horodatage"],
                ["`list`", "Ajout en fin de collection", "`liste.append(item)`", "Ajoute à l'indice `len(liste)`", "Ajouter un enregistrement ou une erreur de validation"],
                ["`list`", "Découpage (Slicing)", "`liste[offset : offset + limit]`", "Extrait une sous-liste sans erreur si hors bornes", "Implémenter la pagination `?page=1&limit=10`"],
                ["`list`", "Filtrage (Compréhension)", "`[x for x in liste if x[\"id\"] == 1]`", "Crée une nouvelle liste filtrée", "Filtrer une collection par critère"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Accéder aux données entrées par l'utilisateur avec `corps[\"champ\"]`",
                "good": "Utiliser `corps.get(\"champ\")` ou vérifier `if \"champ\" not in corps:`",
                "why": "Protège le serveur contre les exceptions non gérées `KeyError` lorsqu'un client envoie un JSON incomplet."
            },
            {
                "bad": "Chercher le 1er élément d'une liste avec `liste[1]` ou sans vérifier si la liste est vide",
                "good": "Vérifier `if liste:` avant de lire `liste[0]`",
                "why": "L'indexation commence à `0` ; en outre, lire `liste[0]` sur une liste vide `[]` provoque un crash `IndexError: list index out of range`."
            },
            {
                "bad": "Renvoyer une liste brute `[...]` à la racine d'une réponse API JSON",
                "good": "Envelopper la liste dans un dictionnaire : `{\"total\": len(items), \"items\": [...]}`",
                "why": "Un dictionnaire racine permet d'ajouter ultérieurement des métadonnées (`page`, `total_pages`) sans casser le contrat JSON des clients."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur Python ci-dessus, ajoutez un 4ème stagiaire avec `.append()` comprenant une clé `\"certifie\": True`, puis affichez le nombre total de stagiaires avec `len()`.",
            "Écrivez une boucle `for` qui affiche uniquement les stagiaires dont le `\"service\"` est `\"Sécurité\"` ou `\"Réseau\"`.",
            "Testez `stagiaires[0].get(\"telephone\", \"Non renseigné\")` pour vérifier le comportement de la valeur par défaut."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.3 : FONCTIONS, PARAMÈTRES, RETURN & TUPLES FLASK
    # =========================================================================
    "d0-l3": {
        "context": (
            "Dans un serveur Web Flask, **chaque route d'API est une fonction Python** : lorsqu'un client appelle "
            "`GET /api/formations`, Flask exécute la fonction rattachée à cette URL et utilise la valeur renvoyée par "
            "l'instruction **`return`** pour construire la réponse HTTP envoyée sur le réseau.\n"
            "Une incompréhension fréquente chez les débutants consiste à confondre `print()` (qui écrit uniquement "
            "dans la console noire de l'administrateur) et `return` (qui transmet la donnée au programme appelant). "
            "Ce chapitre détaille le cycle d'appel d'une fonction, les paramètres par défaut et la syntaxe des tuples "
            "de retour `(reponse_json, code_statut_http)`."
        ),
        "deep_sections": [
            {
                "heading": "1. Anatomie complète d'une Fonction Python (`def`, Paramètres, Portée locale)",
                "body": (
                    "Une fonction est une unité logique autonome définie par quatre éléments :\n"
                    "1. Le mot-clé **`def`** suivi du nom de la fonction en `snake_case` (ex: `calculer_facture`).\n"
                    "2. La **signature entre parenthèses** `(montant_ht, taux_tva=0.19)` : les variables listées ici sont les "
                    "**paramètres**. Lorsqu'un paramètre possède une valeur par défaut (`=0.19`), il devient optionnel lors de l'appel.\n"
                    "3. Le **bloc indenté de 4 espaces** après les deux-points `:` : toutes les variables créées à l'intérieur "
                    "de ce bloc sont des **variables locales** (isolées en mémoire : elles sont détruites dès que la fonction se termine).\n"
                    "4. L'instruction **`return`** : elle interrompt immédiatement la fonction et restitue l'objet résultat à l'appelant."
                )
            },
            {
                "heading": "2. Le patron « Early Return » (Sortie Anticipée) dans les contrôleurs d'API",
                "body": (
                    "Puisque l'instruction `return` arrête instantanément l'exécution de la fonction, les ingénieurs API "
                    "l'utilisent pour valider les entrées dès les premières lignes (principe des *Guard Clauses* ou sorties anticipées) :\n"
                    "- Ligne 1 : Si le jeton d'authentification est absent → `return {\"erreur\": \"Non authentifié\"}, 401` (la fonction s'arrête ici !).\n"
                    "- Ligne 2 : Si le montant est négatif → `return {\"erreur\": \"Montant invalide\"}, 422` (la fonction s'arrête ici !).\n"
                    "- Ligne 3 : Traitement nominal et `return {\"resultat\": ...}, 200`.\n"
                    "Ce style évite d'imbriquer 5 niveaux de `if / else` et rend le code d'une route API limpide à auditer."
                )
            },
            {
                "heading": "3. Retourner plusieurs valeurs avec un Tuple `(corps, code_http)`",
                "body": (
                    "Comment une fonction de route Flask peut-elle renvoyer **à la fois** le dictionnaire JSON ET le code de "
                    "statut HTTP (`200`, `201`, `400`, `404`) ?\n"
                    "En Python, séparer deux valeurs par une virgule après `return` (`return dictionnaire, 201`) construit "
                    "automatiquement un **Tuple** `(dictionnaire, 201)` (une séquence immuable de 2 éléments). L'appelant peut "
                    "alors décompacter ces deux valeurs en une seule ligne : `corps, statut = construire_reponse_api(...)`."
                )
            }
        ],
        "architecture_diagram": (
            "REQUÊTE CLIENT HTTP               FONCTION PYTHON (Route Flask)                SORTIE\n"
            "-------------------               -----------------------------                ------\n"
            "POST /api/formations   ======>    def creer_formation(titre):                  \n"
            "                                      print(\"Log interne\")       --------->   Terminal du serveur uniquement\n"
            "                                      if not titre:                            \n"
            "                                          return {\"err\": ...}, 400 =========>  Réponse HTTP 400 envoyée au client\n"
            "                                      return {\"ok\": titre}, 201   =========>  Réponse HTTP 201 envoyée au client"
        ),
        "reference_table": {
            "title": "Comparaison Technique : `print()` vs `return` et Formes de Retour Flask",
            "headers": ["Instruction / Syntaxe", "Destinataire de la donnée", "Interrompt la fonction ?", "Valeur reçue par Flask", "Résultat pour le client HTTP"],
            "rows": [
                ["`print(donnees)`", "Terminal local (`stdout`)", "Non (continue à la ligne suivante)", "`None` (si aucun `return` suit)", "Crash **`500 Internal Server Error`** (`TypeError: view function did not return a response`)"],
                ["`return jsonify(d)`", "Moteur Flask → Client HTTP", "Oui (immédiatement)", "Objet `Response` (`200 OK` par défaut)", "Réponse JSON avec statut **`200 OK`**"],
                ["`return jsonify(d), 201`", "Moteur Flask → Client HTTP", "Oui (immédiatement)", "Tuple `(Response, 201)`", "Réponse JSON avec statut **`201 Created`**"],
                ["`return jsonify(err), 401, headers`", "Moteur Flask → Client HTTP", "Oui (immédiatement)", "Tuple `(Response, int, dict)`", "Réponse JSON `401` + en-têtes personnalisés"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Terminer une fonction de route par `print(resultat)` en oubliant `return`",
                "good": "Toujours terminer chaque branche d'exécution par `return jsonify(...), code_http`",
                "why": "Une fonction sans `return` renvoie `None`, ce que Flask refuse avec une erreur 500."
            },
            {
                "bad": "Écrire du code après une instruction `return` dans le même bloc (code mort)",
                "good": "Placer les opérations préparatoires avant `return`",
                "why": "Toute ligne située après `return` dans le même bloc d'indentation n'est jamais exécutée."
            },
            {
                "bad": "Utiliser une liste ou un dictionnaire modifiable comme valeur par défaut : `def f(items=[]):`",
                "good": "Utiliser `None` par défaut : `def f(items=None): items = items or []`",
                "why": "En Python, une liste par défaut `[]` dans `def` est créée une seule fois et partagée entre tous les appels successifs !"
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur ci-dessus, appelez `construire_reponse_api(\"\", 3)` et observez comment le premier `if` déclenche un retour anticipé avec le code `400`.",
            "Ajoutez une règle dans `construire_reponse_api` qui renvoie le code `422` si `duree_jours` est supérieur à `30`.",
            "Décompactez le tuple retourné dans deux variables `corps, code = construire_reponse_api(\"Docker\", 4)` et affichez-les séparément."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.4 : EXCEPTIONS (TRY/EXCEPT) & DÉCORATEURS (@)
    # =========================================================================
    "d0-l4": {
        "context": (
            "En lisant le code d'une application Flask ou FastAPI, deux constructions Python reviennent sur presque "
            "chaque route :\n"
            "1. Les blocs de gestion d'erreurs **`try / except`**.\n"
            "2. Les lignes commençant par le symbole arobase **`@`** (comme `@app.route(\"/api/formations\")` ou "
            "`@exiger_role(\"admin\")`), appelées **Décorateurs**.\n"
            "Trop souvent, les formations débutants demandent d'écrire `@app.route(...)` « par cœur » sans expliquer "
            "ce que fait réellement Python sous le capot. Ce chapitre lève totalement le voile sur les exceptions et "
            "les décorateurs afin qu'aucune syntaxe de Flask ne ressemble à de la magie."
        ),
        "deep_sections": [
            {
                "heading": "1. Anatomie d'une Exception et pourquoi un serveur Web ne doit jamais s'arrêter",
                "body": (
                    "Dans un script personnel, si une erreur survient (par exemple `int(\"abc\")` ou une division par zéro), "
                    "le programme affiche un *Traceback* et s'arrête. Mais sur un serveur d'API qui dessert 500 utilisateurs "
                    "simultanés, l'erreur de saisie d'un client ne doit jamais faire tomber le service ni exposer vos chemins "
                    "de fichiers internes !\n"
                    "Le bloc **`try / except`** fonctionne comme un filet de sécurité ciblé :\n"
                    "- Python exécute les instructions du bloc `try:`.\n"
                    "- Si tout se passe bien, le bloc `except:` est totalement ignoré.\n"
                    "- Si une exception du type spécifié (`ValueError`, `KeyError`) se produit à n'importe quelle ligne du `try:`, "
                    "Python saute immédiatement dans le bloc `except:` correspondant, où vous pouvez renvoyer une réponse "
                    "propre **`400 Bad Request`** en JSON."
                )
            },
            {
                "heading": "2. Comment fonctionne réellement un Décorateur `@` en Python (Fonctions d'ordre supérieur)",
                "body": (
                    "En Python, **une fonction est un objet comme un autre** : on peut passer une fonction en argument à une "
                    "autre fonction, et une fonction peut créer et retourner une nouvelle fonction.\n"
                    "Un **décorateur** est simplement une fonction `decorateur(fonction_cible)` qui enveloppe `fonction_cible` "
                    "dans une fonction interne `enveloppe(*args, **kwargs)` pour exécuter du code **avant** et/ou **après** elle.\n"
                    "Écrire :\n"
                    "`@journaliser_appel`\n"
                    "`def traiter_paiement(m): ...`\n"
                    "est strictement équivalent à écrire :\n"
                    "`traiter_paiement = journaliser_appel(traiter_paiement)`.\n"
                    "C'est grâce à ce mécanisme que `@app.route(\"/api/...\")` enregistre votre fonction dans le dictionnaire "
                    "des URLs de Flask, et que `@exiger_role(\"admin\")` vérifie le Bearer Token avant même d'entrer dans votre route !"
                )
            },
            {
                "heading": "3. Le rôle de `*args`, `**kwargs` et `@wraps` dans un décorateur professionnel",
                "body": (
                    "Pour qu'un décorateur puisse envelopper n'importe quelle fonction (qu'elle prenne 0, 1 ou 5 paramètres), "
                    "sa fonction interne utilise la signature universelle `def enveloppe(*args, **kwargs):` :\n"
                    "- `*args` capture tous les arguments positionnels dans un tuple.\n"
                    "- `**kwargs` capture tous les arguments nommés dans un dictionnaire.\n"
                    "- En outre, dans Flask, on place toujours `@wraps(fonction_cible)` (du module standard `functools`) "
                    "au-dessus de `def enveloppe` afin que la fonction décorée conserve son vrai nom (`__name__`), ce que "
                    "Flask exige lorsque vous décorez plusieurs routes."
                )
            }
        ],
        "architecture_diagram": (
            "APPEL CLIENT : traiter_paiement(15000)\n"
            "       |\n"
            "       v\n"
            "+-------------------------------------------------------------------+\n"
            "| DÉCORATEUR (@journaliser_appel -> fonction 'enveloppe')           |\n"
            "|  1. Code AVANT : Vérifie le Token / Démarre le chronomètre        |\n"
            "|     (Si Token invalide -> return 401 immédiatement sans entrer !) |\n"
            "|  2. Appel de la fonction d'origine :                              |\n"
            "|     +-------------------------------------------------------+     |\n"
            "|     | fonction_cible : traiter_paiement(15000)              |     |\n"
            "|     |  -> Exécute la logique métier et renvoie le résultat  |     |\n"
            "|     +-------------------------------------------------------+     |\n"
            "|  3. Code APRÈS : Mesure la durée en ms / Ajoute un log d'audit    |\n"
            "|  4. Retourne le résultat final à l'appelant                       |\n"
            "+-------------------------------------------------------------------+"
        ),
        "reference_table": {
            "title": "Exceptions Standards Python et Traduction en Codes de Statut HTTP",
            "headers": ["Exception Python", "Cause technique déclenchante", "Exemple concret", "Code HTTP à renvoyer dans l'API"],
            "rows": [
                ["`ValueError`", "Conversion impossible d'une valeur", "`int(\"abc\")` sur `?page=abc`", "**`400 Bad Request`** ou **`422`**"],
                ["`KeyError`", "Clé absente dans un dictionnaire", "`corps[\"titre\"]` sur un JSON `{}`", "**`400 Bad Request`** (champ manquant)"],
                ["`TypeError`", "Opération sur un type incompatible", "`None + 5` ou `len(5)`", "**`400`** (si entrée client) ou **`500`** (si bug interne)"],
                ["`sqlite3.IntegrityError`", "Violation d'une contrainte SQL (`UNIQUE`, `NOT NULL`)", "Créer un email déjà existant", "**`409 Conflict`** ou **`422 Unprocessable Entity`**"],
                ["`SignatureExpired`", "Durée de vie d'un Token dépassée (`itsdangerous`)", "`signer.loads(token, max_age=300)`", "**`401 Unauthorized`**"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Utiliser un `except Exception: pass` silencieux qui masque toutes les erreurs",
                "good": "Cibler l'exception précise (`except (ValueError, TypeError):`) et renvoyer un message explicite",
                "why": "Un `except: pass` avale même les fautes de frappe dans votre code, rendant les bugs impossibles à diagnostiquer."
            },
            {
                "bad": "Renvoyer `str(exception)` brut d'une erreur SQL ou système au client en production",
                "good": "Journaliser l'erreur technique en interne et renvoyer un message générique propre au client",
                "why": "Afficher l'erreur brute révèle la structure de vos tables SQL et les chemins de votre serveur aux attaquants."
            },
            {
                "bad": "Oublier `return fonction_cible(*args, **kwargs)` à l'intérieur de l'enveloppe d'un décorateur",
                "good": "Toujours capturer et retourner le résultat de la fonction enveloppée",
                "why": "Si l'enveloppe ne retourne pas le résultat de la route, Flask recevra `None` et lèvera une erreur 500."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur ci-dessus, appelez `convertir_parametre_entier(\"-5\")` et modifiez la fonction pour qu'elle rejette également les nombres négatifs ou nuls.",
            "Créez un second décorateur `@verifier_montant_positif` qui renvoie `{\"erreur\": \"Montant <= 0 interdit\"}` si l'argument passé à `traiter_paiement` est inférieur ou égal à 0.",
            "Observez comment l'ordre des `print()` prouve que le décorateur s'exécute avant et après la fonction décorée."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.1 : HTML VS SOAP/XML VS REST/JSON
    # =========================================================================
    "d1-l1": {
        "context": (
            "Pourquoi toutes les banques, les opérateurs télécoms, les ministères et les plateformes numériques "
            "construisent-ils aujourd'hui leurs systèmes autour d'**APIs** plutôt que de simples sites Web ?\n"
            "Lorsqu'une organisation développe un site Web traditionnel (monolithe HTML), les données de la base et "
            "leur mise en page graphique (couleurs, tableaux HTML, polices) sont fusionnées côté serveur. Ce modèle "
            "s'effondre dès qu'il faut connecter une application mobile iOS/Android, un guichet automatique ou le "
            "système informatique d'un partenaire externe. Ce chapitre retrace l'évolution architecturale des services "
            "Web et démontre concrètement pourquoi le couple **REST / JSON** s'est imposé comme le standard universel."
        ),
        "deep_sections": [
            {
                "heading": "1. Le problème du Couplage Fort (Serveur HTML) face au Découplage (Architecture API)",
                "body": (
                    "Dans une architecture Web classique des années 1990-2000, le serveur exécute la requête SQL et injecte "
                    "les résultats directement dans une page `<html><body><div class=\"card\">...</div></body></html>`.\n"
                    "- **Inconvénient majeur** : Un programme tiers (par exemple le logiciel de comptabilité d'un partenaire "
                    "ou une application mobile native Swift/Kotlin) ne sait pas interpréter des balises visuelles `<div>` ou "
                    "`<span class=\"text-blue\">`. Si un développeur Web modifie la mise en page HTML, toute l'intégration "
                    "partenaire casse instantanément.\n"
                    "- **La révolution de l'API (Application Programming Interface)** : Le serveur métier ne produit plus aucun "
                    "HTML. Il expose uniquement des **données pures et structurées (JSON)** selon un contrat stable. Le site Web, "
                    "l'application mobile et les serveurs partenaires deviennent tous de simples **clients** qui consomment "
                    "exactement la même API."
                )
            },
            {
                "heading": "2. Comparaison Technique : SOAP/XML (1ère génération) vs REST/JSON (Standard actuel)",
                "body": (
                    "Historiquement, deux grandes familles de services Web se sont succédé :\n"
                    "- **SOAP (Simple Object Access Protocol)** : Né à la fin des années 1990, SOAP encapsule chaque message "
                    "dans une enveloppe **XML** verbeuse (`<soap:Envelope><soap:Header/><soap:Body>...</soap:Body></soap:Envelope>`). "
                    "Il n'utilise HTTP que comme un simple tunnel (souvent uniquement via `POST` sur une seule URL) et impose un "
                    "fichier de contrat complexe appelé **WSDL**. Bien qu'encore présent dans certains systèmes bancaires "
                    "historiques, SOAP génère des messages 3 à 5 fois plus lourds que JSON et nécessite des analyseurs XML coûteux en CPU.\n"
                    "- **REST (Representational State Transfer)** : Formalisé par Roy Fielding (co-auteur de la spécification HTTP) "
                    "en 2000, REST propose d'utiliser **pleinement les mécanismes natifs de HTTP** (les URLs pour identifier les "
                    "ressources, les verbes `GET/POST/PUT/DELETE` pour exprimer l'action, et les codes `200/400/404` pour le statut) "
                    "en transportant les données au format **JSON**, léger et directement convertible en dictionnaire Python ou objet JavaScript."
                )
            },
            {
                "heading": "3. Quand utiliser REST/JSON, GraphQL ou gRPC ?",
                "body": (
                    "Bien que **REST/JSON** couvre plus de 85 % des besoins en entreprise, deux autres technologies complètent "
                    "l'écosystème moderne :\n"
                    "- **GraphQL** : Créé par Meta pour les écrans mobiles complexes devant agréger 10 sources de données en une "
                    "seule requête en choisissant exactement les champs voulus.\n"
                    "- **gRPC (Protocol Buffers sur HTTP/2)** : Créé par Google pour la communication interne ultra-rapide (binaire) "
                    "entre deux microservices backend qui s'appellent des milliers de fois par seconde.\n"
                    "Pour toute API publique, partenaire, mobile ou Web d'entreprise, **REST/JSON** demeure le choix de référence "
                    "pour sa simplicité, sa lisibilité, sa compatibilité universelle et sa mise en cache HTTP native."
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE MONOLITHE HTML (Couplage fort)           ARCHITECTURE CENTRÉE API REST (Découplage total)\n"
            "-------------------------------------------           ------------------------------------------------\n"
            "[Base SQL] -> [Serveur] --(HTML+CSS)--> Navigateur    [Base SQL] -> [Serveur API Flask] ===(JSON Pur)==+--> Portail Web (PWA/React)\n"
            "                  |                                                                                    +--> Application Mobile (iOS/Android)\n"
            "                  +--(HTML inutilisable !)--> App Mobile / Partenaire                                  +--> Serveur Partenaire / Script Python"
        ),
        "reference_table": {
            "title": "Comparatif Architectural des Paradigmes de Services Web",
            "headers": ["Critère", "Site Web HTML", "Service Web SOAP / XML", "API REST / JSON", "gRPC (Protobuf)"],
            "rows": [
                ["**Destinataire**", "Humain (Navigateur Web)", "Machine à Machine (M2M)", "Machine à Machine & Frontaux Web/Mobile", "Microservices internes"],
                ["**Format des données**", "HTML (Présentation visuelle)", "XML strict (`<soap:Envelope>`)", "JSON léger (`{\"cle\": valeur}`)", "Binaire (Protocol Buffers)"],
                ["**Usage de HTTP**", "`GET` et formulaires `POST`", "Tunnel `POST` unique (ignore les verbes HTTP)", "Natif (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`)", "HTTP/2 multiplexé"],
                ["**Poids réseau & CPU**", "Élevé (HTML + CSS + Images)", "Élevé (Balises XML ouvrantes/fermantes)", "Très faible (Compact et natif)", "Minimal (Binaire compressé)"],
                ["**Contrat d'interface**", "Aucun (Visuel)", "Fichier `WSDL` / `XSD`", "Spécification **OpenAPI 3.0 (Swagger)**", "Fichier `.proto`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Extraire des données d'un serveur interne en faisant du *Web Scraping* (analyse du HTML)",
                "good": "Exposer une route d'API JSON dédiée (`/api/v1/formations`) pour les échanges entre logiciels",
                "why": "Le moindre changement esthétique dans une page HTML casse immédiatement un script de scraping, alors qu'un contrat JSON est stable."
            },
            {
                "bad": "Mélanger du code HTML (`<b>Erreur</b>`) à l'intérieur des valeurs d'une réponse JSON",
                "good": "Renvoyer uniquement des données brutes propres dans le JSON et laisser le client gérer l'affichage",
                "why": "Une application mobile native ou un script Python n'affiche pas de HTML et verrait les balises `<b>` brutes à l'écran."
            }
        ],
        "practical_exercises": [
            "Exécutez le script `day_1/01_html_vs_json.py` ci-dessus et comparez le nombre exact d'octets entre la réponse HTML, l'enveloppe SOAP/XML et la charge utile REST/JSON.",
            "Ajoutez un champ `\"lieu\": \"Alger\"` dans `reponse_rest_json` et vérifiez que sa taille reste inférieure à la moitié de la trame SOAP."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.2 : PILE RÉSEAU (DNS, IP, PORT TCP, TLS) & URI RFC 3986
    # =========================================================================
    "d1-l2": {
        "context": (
            "Lorsqu'un client exécute `fetch(\"https://api.isgp.dz:8443/v1/formations?salle=Alger\")` ou que vous "
            "lancez `app.run(host=\"0.0.0.0\", port=5000)`, que se passe-t-il réellement sur la carte réseau de "
            "l'ordinateur ?\n"
            "Sans comprendre la différence entre une **adresse IP** (`127.0.0.1` vs `0.0.0.0` vs `192.168.1.x`), un "
            "**numéro de Port TCP** (`:5000`, `:443`) et les segments d'une **URI**, un développeur est incapable de "
            "diagnostiquer des erreurs classiques comme `Connection refused`, `Address already in use` ou `Name or "
            "service not known`. Ce chapitre décortique la pile réseau et l'anatomie d'une URI sans aucun prérequis."
        ),
        "deep_sections": [
            {
                "heading": "1. Du Nom de Domaine au Processus Python : DNS → Adresse IP → Port TCP",
                "body": (
                    "Pour acheminer une requête d'un ordinateur A vers un serveur B, le réseau traverse trois couches d'adressage :\n"
                    "1. **Le DNS (*Domain Name System*)** : Les humains retiennent des noms (`api.isgp.dz`), mais les routeurs "
                    "réseau ne connaissent que des adresses numériques **IP**. Le DNS traduit le nom de domaine en adresse IP "
                    "(ex: `196.20.45.12`). Sur votre propre machine, le nom spécial **`localhost`** est toujours traduit "
                    "instantanément en **`127.0.0.1`** (l'adresse de bouclage interne ou *loopback*).\n"
                    "2. **L'Adresse IP (*Internet Protocol*)** : Elle identifie **une machine physique ou virtuelle unique** "
                    "sur le réseau. C'est l'adresse postale de l'immeuble.\n"
                    "3. **Le Port TCP (*Transmission Control Protocol* — numéroté de 1 à 65535)** : Sur un même serveur "
                    "(une seule adresse IP), plusieurs logiciels tournent en même temps (PostgreSQL, Nginx, SSH, Flask). "
                    "Le numéro de **Port** est le numéro de guichet qui indique au système d'exploitation à quel processus "
                    "exact remettre les paquets entrants (ex: port `5000` pour Flask)."
                )
            },
            {
                "heading": "2. La différence cruciale entre `127.0.0.1` et `0.0.0.0` dans `app.run()`",
                "body": (
                    "Lorsque vous démarrez votre serveur Flask, le paramètre `host` détermine quelles cartes réseau ont le "
                    "droit de lui parler :\n"
                    "- **`host=\"127.0.0.1\"` (Boucle locale fermée)** : Seuls les programmes tournant **sur le même ordinateur** "
                    "peuvent interroger votre API. Vos collègues connectés au même Wi-Fi de la salle de formation recevront "
                    "`Connection refused`.\n"
                    "- **`host=\"0.0.0.0\"` (Toutes les interfaces réseau)** : Dit au système d'exploitation d'écouter à la fois "
                    "sur `127.0.0.1` ET sur l'adresse IP du réseau local (ex: `192.168.1.15`). C'est indispensable pour partager "
                    "votre API sur un réseau local ou depuis un conteneur Docker."
                )
            },
            {
                "heading": "3. Anatomie chirurgicale d'une URI selon le standard RFC 3986",
                "body": (
                    "Chaque partie d'une URL (`https://api.isgp.dz:8443/api/v1/formations?salle=Alger&page=2#section`) est "
                    "exploitée différemment par votre serveur Flask :\n"
                    "- **`scheme` (`https`)** : Le protocole utilisé (`http` en clair ou `https` chiffré par TLS).\n"
                    "- **`authority` (`api.isgp.dz:8443`)** : Le nom d'hôte (`hostname`) et le port TCP (`port`).\n"
                    "- **`path` (`/api/v1/formations`)** : Le chemin hiérarchique qui détermine quelle fonction `@app.route(...)` "
                    "sera exécutée par Flask.\n"
                    "- **`query` (`salle=Alger&page=2`)** : Située après `?`, contient les paramètres clé=valeur séparés par `&`, "
                    "accessibles dans Flask via `request.args`."
                )
            }
        ],
        "architecture_diagram": (
            "ANATOMIE D'UNE URI (RFC 3986) :\n"
            "  https://api.isgp.dz:8443/api/v1/formations?salle=Alger&page=2#details\n"
            "  \\___/   \\_________/ \\__/\\________________/ \\________________/ \\_____/\n"
            "    |          |        |          |                  |            |\n"
            "  Scheme     Host     Port       Path           Query String    Fragment\n"
            " (TLS/HTTP) (DNS/IP)  (TCP)  (@app.route)      (request.args)  (Navigateur)\n\n"
            "PILE RÉSEAU D'UN APPEL API :\n"
            "  [1. Résolution DNS]  --->  [2. Connexion TCP (IP:Port)]  --->  [3. Handshake TLS]  --->  [4. Requête HTTP]"
        ),
        "reference_table": {
            "title": "Ports Réseau Standards et Adresses IP Spéciales à Connaître",
            "headers": ["Port / Adresse", "Nom Standard", "Service ou Signification Technique"],
            "rows": [
                ["`127.0.0.1` (`localhost`)", "Loopback (Boucle locale)", "Désigne toujours la machine locale elle-même (sans sortir sur la carte Wi-Fi/Ethernet)"],
                ["`0.0.0.0`", "Any Interface (Écoute globale)", "Indique au serveur d'écouter sur toutes les adresses IP de la machine (locale + LAN)"],
                ["Port `:80`", "HTTP par défaut", "Port implicite d'une URL `http://...` (non chiffré)"],
                ["Port `:443`", "HTTPS par défaut", "Port implicite d'une URL `https://...` (chiffré par TLS/SSL)"],
                ["Port `:5000` / `:8000`", "Ports de développement Python", "Ports utilisateurs (> 1024, ne nécessitent pas les droits administrateur `root`)",],
                ["Port `:5432` / `:3306`", "PostgreSQL / MySQL", "Ports d'écoute des serveurs de bases de données SQL"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Laisser `app.run()` par défaut (`127.0.0.1`) dans un conteneur Docker ou pour un test en salle",
                "good": "Spécifier `app.run(host=\"0.0.0.0\", port=5000)`",
                "why": "Dans un conteneur ou sur un réseau local, écouter uniquement sur `127.0.0.1` rejette toute connexion venant de l'extérieur."
            },
            {
                "bad": "Lancer deux fois `python app.py` sur le même port `5000` (`OSError: [Errno 98] Address already in use`)",
                "good": "Arrêter le premier processus (`Ctrl+C`) ou choisir un port libre (`port=5001`)",
                "why": "Un numéro de port TCP sur une même adresse IP ne peut être attribué qu'à un seul serveur à la fois."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_1/03_analyseur_uri_et_reseau.py` ci-dessus et modifiez l'URL analysée pour observer comment `urlsplit` et `parse_qs` extraient les paramètres multiples.",
            "Supprimez `:8443` de l'URI dans le script et observez quelle valeur prend `composants.port` (`None`, car le port implicite de `https` est `443`)."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.3 : TRAME BRUTE HTTP/1.1 & EN-TÊTES STRATÉGIQUES
    # =========================================================================
    "d1-l3": {
        "context": (
            "Une fois la connexion TCP établie entre le client et le serveur, quels octets exacts sont envoyés sur "
            "le câble réseau ?\n"
            "Contrairement à une idée reçue, HTTP/1.1 n'est pas un format binaire mystérieux : c'est un **protocole "
            "purement textuel** composé de lignes séparées par des retours à la ligne (`\\r\\n`). Savoir lire une "
            "trame HTTP brute et comprendre le rôle exact des **En-têtes (`Headers`)** et des **Codes de Statut** "
            "transforme votre façon de concevoir et de déboguer une API."
        ),
        "deep_sections": [
            {
                "heading": "1. Pourquoi HTTP est un protocole « Sans État » (Stateless) ?",
                "body": (
                    "Le protocole HTTP est dit **Stateless (sans état)** : chaque requête envoyée par un client est "
                    "**totalement indépendante** des requêtes précédentes.\n"
                    "- Le serveur ne conserve aucune « mémoire implicite » de qui a envoyé la requête précédente.\n"
                    "- Conséquence fondamentale pour nos APIs : **chaque requête HTTP doit contenir dans ses en-têtes toutes "
                    "les informations nécessaires à son traitement** (son jeton d'authentification `Authorization: Bearer ...`, "
                    "le format de son corps `Content-Type: application/json`, et le format de réponse attendu `Accept: application/json`)."
                )
            },
            {
                "heading": "2. La frontière physique entre les En-têtes (`Headers`) et le Corps (`Body`) : `\\r\\n\\r\\n`",
                "body": (
                    "Lorsque le serveur Flask lit les octets qui arrivent sur le socket TCP, comment sait-il où s'arrêtent "
                    "les en-têtes de métadonnées et où commence le JSON du corps de la requête ?\n"
                    "- Chaque ligne d'en-tête se termine par la séquence `CR+LF` (`\\r\\n`).\n"
                    "- La fin du bloc des en-têtes est marquée par **une ligne strictement vide** (soit deux retours à la "
                    "ligne consécutifs : `\\r\\n\\r\\n`).\n"
                    "- Ensuite, le serveur lit exactement le nombre d'octets indiqué par l'en-tête **`Content-Length`**. "
                    "Attention : `Content-Length` compte les **octets UTF-8** (`len(texte.encode('utf-8'))`) et non le nombre "
                    "de caractères `len(texte)` (car un caractère accentué comme `é` occupe 2 octets en UTF-8 !)."
                )
            },
            {
                "heading": "3. Taxonomie Complète des Codes de Statut HTTP (RFC 9110)",
                "body": (
                    "Le code à 3 chiffres situé sur la première ligne de la réponse (`HTTP/1.1 201 Created`) est le premier "
                    "élément inspecté par tout programme client :\n"
                    "- **Plage `2xx` (Succès)** : `200 OK` (succès avec corps JSON), `201 Created` (nouvelle ressource créée), "
                    "`204 No Content` (succès sans corps, typique d'un `DELETE`).\n"
                    "- **Plage `3xx` (Redirection & Cache)** : `301 Moved Permanently`, `304 Not Modified` (la version en cache du client est toujours à jour).\n"
                    "- **Plage `4xx` (Erreur commise par le Client)** : Le serveur fonctionne parfaitement, mais la demande du client est refusée (`400`, `401`, `403`, `404`, `405`, `409`, `413`, `422`, `429`).\n"
                    "- **Plage `5xx` (Défaillance du Serveur)** : Le client a envoyé une requête valide, mais le serveur a subi une panne interne (`500`, `502`, `503`, `504`)."
                )
            }
        ],
        "architecture_diagram": (
            "TRAME DE REQUÊTE HTTP/1.1 BRUTE (Octets envoyés par le Client sur le Socket TCP)\n"
            "+------------------------------------------------------------------------------+\n"
            "| POST /api/v1/formations HTTP/1.1\\r\\n          <-- 1. REQUEST LINE            |\n"
            "| Host: api.isgp.dz\\r\\n                         <-- 2. HEADERS (Métadonnées)   |\n"
            "| Authorization: Bearer eyJhbGci...\\r\\n                                        |\n"
            "| Content-Type: application/json; charset=utf-8\\r\\n                            |\n"
            "| Content-Length: 49\\r\\n                                                       |\n"
            "| \\r\\n                                          <-- 3. LIGNE VIDE OBLIGATOIRE  |\n"
            "| {\"titre\": \"Sécurité des APIs\", \"jours\": 5}    <-- 4. BODY (49 octets UTF-8)  |\n"
            "+------------------------------------------------------------------------------+"
        ),
        "reference_table": {
            "title": "Référentiel Complet des Codes de Statut HTTP Indispensables en Ingénierie d'API",
            "headers": ["Code HTTP", "Nom Officiel", "Catégorie", "Signification exacte et quand le renvoyer"],
            "rows": [
                ["**`200 OK`**", "OK", "2xx Succès", "Requête `GET`, `PUT` ou `PATCH` réussie avec corps JSON en réponse"],
                ["**`201 Created`**", "Created", "2xx Succès", "Nouvelle ressource créée avec succès suite à un `POST`"],
                ["**`204 No Content`**", "No Content", "2xx Succès", "Action réussie (souvent `DELETE`) ne renvoyant aucun corps"],
                ["**`400 Bad Request`**", "Bad Request", "4xx Client", "Syntaxe JSON mal formée ou paramètre d'URL illisible"],
                ["**`401 Unauthorized`**", "Unauthorized", "4xx Client", "**Échec AuthN** : Jeton/Clé API absent, expiré ou signature invalide"],
                ["**`403 Forbidden`**", "Forbidden", "4xx Client", "**Échec AuthZ** : Client authentifié, mais rôle/scope insuffisant"],
                ["**`404 Not Found`**", "Not Found", "4xx Client", "URL inexistante ou identifiant de ressource (`id=999`) introuvable"],
                ["**`405 Method Not Allowed`**", "Method Not Allowed", "4xx Client", "L'URL existe mais n'accepte pas ce verbe HTTP (ex: `DELETE` sur `/login`)"],
                ["**`409 Conflict`**", "Conflict", "4xx Client", "Conflit d'état (ex: doublon d'adresse e-mail ou de matricule unique)"],
                ["**`413 Payload Too Large`**", "Payload Too Large", "4xx Client", "Corps de la requête dépassant la taille maximale autorisée (`MAX_CONTENT_LENGTH`)"],
                ["**`422 Unprocessable Entity`**", "Unprocessable Content", "4xx Client", "JSON bien formé mais violant une règle métier (ex: `duree_jours = -3`)"],
                ["**`429 Too Many Requests`**", "Too Many Requests", "4xx Client", "Quota de **Rate Limiting** dépassé sur la fenêtre de temps"],
                ["**`500 Internal Server Error`**", "Internal Server Error", "5xx Serveur", "Exception Python non gérée côté serveur (bug du code backend)"],
                ["**`502 / 503 / 504`**", "Bad Gateway / Unavailable / Timeout", "5xx Serveur", "Serveur en maintenance, base de données injoignable ou timeout amont"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Renvoyer `200 OK` pour tout, même en cas d'erreur : `return jsonify({\"success\": false, \"error\": \"Introuvable\"}), 200`",
                "good": "Utiliser le vrai code de statut HTTP correspondant : `return jsonify({\"erreur\": \"Introuvable\"}), 404`",
                "why": "Le *200 OK avec erreur cachée* est le pire anti-pattern REST : les outils de monitoring, proxies et clients HTTP croient que l'appel a réussi !"
            },
            {
                "bad": "Oublier l'en-tête `Content-Type: application/json` lors d'un `POST`",
                "good": "Toujours spécifier `Content-Type: application/json` dès qu'un corps JSON est envoyé",
                "why": "Sans cet en-tête, `request.get_json()` dans Flask ignore le corps ou renvoie une erreur `415 Unsupported Media Type`."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_1/04_trame_http_et_headers.py` et vérifiez pourquoi `'Sécurité'` (8 caractères) occupe 10 octets en UTF-8 dans `Content-Length`.",
            "Dans le Client HTTP, testez la route `/api/sandbox/status-demo/429` puis `/api/sandbox/status-demo/403`."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.4 : MÉTHODES HTTP, IDEMPOTENCE & SÉRIALISATION JSON
    # =========================================================================
    "d1-l4": {
        "context": (
            "Sur un réseau réel (4G/5G mobile, Wi-Fi d'entreprise, liaison interbancaire), les coupures de connexion "
            "sont quotidiennes. Si un client envoie une requête HTTP et que la connexion coupe juste avant de recevoir "
            "la réponse, **le client peut-il renvoyer automatiquement la même requête sans risque ?**\n"
            "La réponse à cette question fondamentale d'architecture s'appelle **l'Idempotence**. Ce chapitre explique "
            "la sémantique mathématique des 5 verbes HTTP (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) et les règles "
            "d'or de la sérialisation JSON (`json.dumps` / `json.loads`)."
        ),
        "deep_sections": [
            {
                "heading": "1. Propriétés Mathématiques des Verbes HTTP : Méthodes Sûres (Safe) vs Idempotentes",
                "body": (
                    "La norme RFC 9110 classe les méthodes HTTP selon deux critères décisifs pour la fiabilité réseau :\n"
                    "- **Méthode Sûre (*Safe*)** : Une méthode qui fait uniquement de la **lecture** et ne modifie jamais "
                    "l'état du serveur (`GET`, `HEAD`, `OPTIONS`).\n"
                    "- **Méthode Idempotente (*Idempotent*)** : Une opération que l'on peut exécuter **1 fois, 2 fois ou "
                    "100 fois de suite avec les mêmes paramètres en obtenant toujours exactement le même état final sur le serveur**.\n"
                    "  - `GET /formations/1` est idempotent (et sûr).\n"
                    "  - `PUT /formations/1` (remplacer la fiche n°1 par `{ \"titre\": \"A\" }`) est **idempotent** : l'exécuter "
                    "5 fois laisse la fiche n°1 avec le titre `\"A\"`.\n"
                    "  - `DELETE /formations/1` est **idempotent** : après 1 ou 5 suppressions, la fiche n°1 est supprimée.\n"
                    "  - **`POST /formations` N'EST PAS IDEMPOTENT** : l'exécuter 3 fois crée **3 formations distinctes** "
                    "(`#1`, `#2`, `#3`) ou débite 3 fois une carte bancaire !"
                )
            },
            {
                "heading": "2. Sérialisation (`dumps`) et Désérialisation (`loads`) en Python",
                "body": (
                    "Une carte réseau ne sait pas transporter un objet `dict` de la RAM Python : elle ne transporte que des "
                    "séquences d'octets textuels.\n"
                    "- **Sérialiser (`json.dumps(dictionnaire)`)** : Transforme l'objet mémoire Python en une chaîne de "
                    "caractères formatée selon la norme JSON. Le paramètre `ensure_ascii=False` empêche l'échappement "
                    "`\\u00e9` et préserve les caractères accentués ou arabes en UTF-8 natif.\n"
                    "- **Désérialiser (`json.loads(chaine_json)`)** : Analyse (*parse*) la chaîne de texte reçue du réseau "
                    "pour reconstruire le dictionnaire ou la liste en mémoire Python."
                )
            },
            {
                "heading": "3. Structure d'Enveloppe JSON et Format International des Dates (ISO 8601)",
                "body": (
                    "Dans une API d'entreprise, on sépare systématiquement :\n"
                    "- La clé **`\"meta\"`** : informations techniques sur la réponse (version de l'API, horodatage UTC au "
                    "format international **ISO 8601 `YYYY-MM-DDTHH:MM:SSZ`**, pagination).\n"
                    "- La clé **`\"data\"`** : le contenu métier proprement dit.\n"
                    "Pourquoi le format ISO 8601 (`2026-11-08T17:30:00Z`) est-il obligatoire ? Parce qu'il se trie par "
                    "ordre alphabétique aussi bien que chronologique et élimine toute ambiguïté de fuseau horaire grâce au suffixe `Z` (*Zulu / UTC*)."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE SÉRIALISATION / DÉSÉRIALISATION ENTRE DEUX SYSTÈMES :\n"
            "  [Mémoire Serveur Python]                [Câble Réseau HTTP]                [Mémoire Client (Python/JS)]\n"
            "   dict {'actif': True, 'fin': None}  -->  json.dumps().encode('utf-8')  -->  json.loads() / JSON.parse()\n"
            "                                       \"{\\\"actif\\\": true, \\\"fin\\\": null}\""
        ),
        "reference_table": {
            "title": "Matrice de Sémantique et d'Idempotence des Méthodes HTTP (RFC 9110)",
            "headers": ["Méthode HTTP", "Action CRUD", "Corps (Body) en Requête ?", "Sûre (Safe) ?", "Idempotente ?", "Réessai automatique sans risque en cas de coupure ?"],
            "rows": [
                ["**`GET`**", "Lire (Read)", "Non (Jamais)", "**Oui**", "**Oui**", "**Oui** (100% sûr)"],
                ["**`PUT`**", "Remplacer intégralement", "Oui (JSON complet)", "Non", "**Oui**", "**Oui** (Écrase avec le même état final)"],
                ["**`DELETE`**", "Supprimer (Delete)", "Non", "Non", "**Oui**", "**Oui** (L'élément reste supprimé)"],
                ["**`PATCH`**", "Modifier partiellement", "Oui (Champs modifiés)", "Non", "Selon implémentation", "Prudence (Idempotent si affectation de valeur)"],
                ["**`POST`**", "Créer / Traiter", "Oui (JSON)", "Non", "**NON !**", "**NON** (Risque de doublon sauf avec `Idempotency-Key`)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Utiliser une route `GET /api/formations/supprimer?id=1` qui modifie ou supprime des données",
                "good": "Respecter la méthode `DELETE /api/formations/1` pour toute suppression",
                "why": "Les navigateurs, robots d'indexation et proxys préchargent parfois les liens `GET` automatiquement : si votre `GET` supprime des données, votre base sera vidée par accident !"
            },
            {
                "bad": "Confondre `json.load(fichier)` (sans `s`) et `json.loads(chaine)` (avec `s` = *string*)",
                "good": "Utiliser `json.loads()` et `json.dumps()` pour les chaînes de caractères réseau",
                "why": "`load` et `dump` sans `s` lisent/écrivent un fichier sur disque, tandis que `loads` et `dumps` opèrent sur des chaînes en mémoire."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_1/02_serialisation_json.py` et vérifiez que `None` est devenu `null` et `True` est devenu `true` dans la chaîne JSON.",
            "Ajoutez une clé `\"modules\": [\"HTTP\", \"Flask\", \"Sécurité\"]` dans le dictionnaire Python, sérialisez-le, puis relisez le 2ème module après `json.loads()`."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.5 : MAÎTRISER CURL, POSTMAN, HTTPIE & REST CLIENT
    # =========================================================================
    "d1-l5": {
        "context": (
            "Comment tester et déboguer une API qui exige une méthode `POST` ou `DELETE`, un corps JSON et un en-tête "
            "`Authorization: Bearer <token>` alors que la barre d'adresse d'un navigateur Web (Chrome, Firefox, Edge) "
            "ne sait envoyer que des requêtes `GET` sans en-têtes personnalisés ?\n"
            "Un développeur d'API ne travaille jamais à l'aveugle : il utilise des **clients d'inspection HTTP**. "
            "En production sur un serveur Linux distant (via SSH) ou dans un script d'intégration continue, **`curl`** "
            "est le standard absolu. Sur son poste de développement, il le complète avec **Postman** (ou Bruno/Insomnia), "
            "**HTTPie** et les fichiers **`.http`**. Ce chapitre vous rend autonome sur chacun de ces outils."
        ),
        "deep_sections": [
            {
                "heading": "1. Pourquoi `curl` est le couteau suisse universel de tout ingénieur Backend",
                "body": (
                    "Créé en 1997 par Daniel Stenberg, **`curl` (*Client for URL*)** est préinstallé sur la quasi-totalité "
                    "des serveurs Linux, macOS, Windows 10/11 et conteneurs Docker de la planète.\n"
                    "- Lorsqu'une API tombe en panne en production à 2h du matin, vous vous connectez au serveur en ligne de "
                    "commande : vous n'avez pas d'interface graphique Postman sur le serveur. Avec `curl -i` ou `curl -v`, "
                    "vous forgez n'importe quelle requête HTTP en quelques secondes et inspectez les octets exacts renvoyés par Flask.\n"
                    "- De plus, toute commande `curl` peut être copiée-collée dans un ticket d'incident, dans une documentation "
                    "technique ou dans un script de test automatisé."
                )
            },
            {
                "heading": "2. Décoder la sortie de `curl -v` (Mode Verbeux) : les symboles `*`, `>` et `<`",
                "body": (
                    "Lorsque vous lancez `curl -v http://127.0.0.1:5000/api/sandbox/bonjour`, `curl` préfixe chaque ligne "
                    "de diagnostic par un symbole précis :\n"
                    "- Les lignes commençant par **`*`** décrivent le travail interne de `curl` (résolution DNS, connexion TCP "
                    "vers `127.0.0.1` port `5000`, négociation TLS).\n"
                    "- Les lignes commençant par **`>`** montrent la **Requête HTTP sortante** envoyée par `curl` vers le serveur "
                    "(`> GET /api/sandbox/bonjour HTTP/1.1`, `> Host: 127.0.0.1:5000`, `> Accept: */*`).\n"
                    "- Les lignes commençant par **`<`** montrent les **En-têtes de la Réponse HTTP entrante** renvoyés par le "
                    "serveur Flask (`< HTTP/1.1 200 OK`, `< Content-Type: application/json`)."
                )
            },
            {
                "heading": "3. Structurer ses tests en équipe avec Postman, HTTPie et VS Code REST Client (`.http`)",
                "body": (
                    "Pour organiser des dizaines de routes au quotidien, trois outils complètent `curl` :\n"
                    "- **Postman / Bruno / Insomnia** : Permettent de regrouper toutes les routes du projet dans une **Collection** "
                    "et d'utiliser des variables comme `{{base_url}}` et `{{bearer_token}}`.\n"
                    "- **HTTPie (`http`)** : Un client en ligne de commande pensé pour JSON (`http POST :5000/api/formations titre=\"Flask\" duree:=5`), qui colore automatiquement la sortie.\n"
                    "- **Fichiers `.http` (REST Client dans VS Code)** : Un simple fichier texte versionné dans Git où chaque "
                    "requête est séparée par `###` et exécutable d'un clic directement dans l'éditeur de code."
                )
            }
        ],
        "architecture_diagram": (
            "LECTURE D'UNE TRACE DIAGNOSTIC 'curl -v' :\n"
            "  * Trying 127.0.0.1:5000...                  <-- [*] Connexion TCP ouverte par curl\n"
            "  * Connected to 127.0.0.1 (127.0.0.1) port 5000\n"
            "  > POST /api/sandbox/auth/token HTTP/1.1     <-- [>] En-têtes ENVOYÉS par le client\n"
            "  > Host: 127.0.0.1:5000\n"
            "  > Content-Type: application/json\n"
            "  > Content-Length: 52\n"
            "  <\n"
            "  < HTTP/1.1 200 OK                           <-- [<] En-têtes REÇUS depuis Flask\n"
            "  < Content-Type: application/json\n"
            "  {\"access_token\": \"eyJ...\"}                  <-- Corps JSON de la réponse"
        ),
        "reference_table": {
            "title": "Synthèse des Commandes `curl` les Plus Utilisées au Quotidien",
            "headers": ["Objectif de test", "Commande `curl` complète", "Options clés utilisées"],
            "rows": [
                ["**Lire + voir les Headers**", "`curl -i http://127.0.0.1:5000/api/sandbox/formations`", "`-i` (inclut statut + en-têtes)"],
                ["**Créer en `POST` JSON**", "`curl -i -X POST -H \"Content-Type: application/json\" -d '{\"titre\":\"API\"}' http://127.0.0.1:5000/api/sandbox/formations`", "`-X POST`, `-H`, `-d`"],
                ["**Raccourci JSON moderne**", "`curl -i --json '{\"titre\":\"API\"}' http://127.0.0.1:5000/api/sandbox/formations`", "`--json` (`curl 7.82+`)"],
                ["**Modifier (`PUT` / `PATCH`)**", "`curl -i -X PATCH -H \"Content-Type: application/json\" -d '{\"salle\":\"B\"}' http://127.0.0.1:5000/api/sandbox/formations/1`", "`-X PATCH`"],
                ["**Supprimer (`DELETE`)**", "`curl -i -X DELETE http://127.0.0.1:5000/api/sandbox/formations/1`", "`-X DELETE`"],
                ["**Envoyer un `Bearer Token`**", "`curl -i -H \"Authorization: Bearer <TOKEN>\" http://127.0.0.1:5000/api/sandbox/auth/profil`", "`-H \"Authorization: Bearer ...\"`"],
                ["**Diagnostic complet**", "`curl -v --connect-timeout 3 -m 10 http://127.0.0.1:5000/api/sandbox/bonjour`", "`-v`, `--connect-timeout`, `-m`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écrire `curl -X POST -d '{\"titre\": \"API\"}' URL` en oubliant `-H \"Content-Type: application/json\"`",
                "good": "Toujours ajouter `-H \"Content-Type: application/json\"` (ou utiliser `--json`)",
                "why": "Par défaut, `-d` dans `curl` envoie l'en-tête `application/x-www-form-urlencoded` (formulaire HTML) et non `application/json` !"
            },
            {
                "bad": "Passer une URL contenant `&` sans guillemets dans le terminal : `curl http://localhost:5000/api?page=1&limit=2`",
                "good": "Toujours entourer l'URL de guillemets doubles : `curl \"http://localhost:5000/api?page=1&limit=2\"`",
                "why": "Dans un terminal Linux/macOS/Windows, le caractère `&` hors guillemets coupe la commande et met `curl` en arrière-plan en ignorant `&limit=2` !"
            }
        ],
        "practical_exercises": [
            "Exécutez le script `day_1/05_outils_curl_postman_httpie.py` ci-dessus pour observer la sortie réelle des 3 commandes `curl -i`.",
            "Ouvrez l'onglet **curl & Postman** dans la barre supérieure et testez les commandes de l'aide-mémoire interactif.",
            "Téléchargez la Collection Postman (`.json`) et le fichier `.http` depuis l'onglet **curl & Postman**."
        ]
    }
}
