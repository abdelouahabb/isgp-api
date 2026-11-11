"""
Manuel de Référence Approfondi — Volume II : FastAPI, ASGI & Pydantic v2 (Jours 0 et 1).
Ouvrage d'ingénierie logicielle couvrant :
- context : problématique architecturale et enjeux de production
- deep_sections : monographies techniques approfondies (CPython, mémoire, ASGI, HTTP/1.1, RFC)
- architecture_diagram : topologie mémoire ou trame réseau ASCII
- reference_table : matrice de synthèse normative
- pitfalls : anti-patterns de production vs standards industriels
- practical_exercises : travaux pratiques progressifs post-bootcamp
"""

ENRICHMENT_D0_D1 = {
    # =========================================================================
    # JOUR 0 — CHAPITRE 0.1 : VARIABLES, MÉMOIRE & TYPES PRIMITIFS
    # =========================================================================
    "d0-l1": {
        "context": (
            "Avant d'ouvrir la moindre socket TCP ou d'orchestrer des coroutines asynchrones dans Uvicorn, tout service "
            "backend manipule de l'état en mémoire vive (RAM) : l'identifiant d'un dossier stagiaire, le montant hors "
            "taxes d'une convention, l'indicateur booléen d'ouverture d'une session ou l'échéance horodatée d'un jeton "
            "d'accès. À l'échelle d'une architecture distribuée, la rigueur avec laquelle ces grandeurs sont représentées "
            "en mémoire détermine directement la fiabilité du contrat exposé aux systèmes consommateurs.\n\n"
            "Dans une API REST industrielle, la moindre confusion sur la nature physique d'une donnée — transmettre la "
            "chaîne de caractères `\"500\"` au lieu de l'entier `500`, assimiler une chaîne vide `\"\"` à l'absence de "
            "valeur `None`, ou calculer une taxe financière en virgule flottante binaire approximative — déclenche "
            "immédiatement des défaillances en cascade chez les clients typés statiquement (applications mobiles Swift "
            "ou Kotlin, frontaux TypeScript, progiciels comptables Java). Ce chapitre inaugural pose les fondations du "
            "modèle mémoire de CPython et de l'algèbre des types qui gouverne FastAPI et le moteur Rust `pydantic-core`."
        ),
        "deep_sections": [
            {
                "heading": "1. Modèle mémoire de CPython : Structures `PyObject`, références et typage dynamique fort",
                "body": (
                    "Dans des langages compilés de bas niveau comme C ou Rust, déclarer `int32_t duree_jours = 5;` "
                    "réserve directement un emplacement fixe de quatre octets sur la pile d'exécution (*stack*) dont le "
                    "nom est résolu à la compilation. Python adopte un paradigme radicalement différent, conçu pour la "
                    "souplesse d'introspection : **toute valeur en Python est un objet alloué sur le tas mémoire (*heap*)**, "
                    "représenté au sein de l'interpréteur CPython par une structure C nommée `PyObject`.\n\n"
                    "#### Anatomie d'une affectation et comptage de références\n\n"
                    "Lorsque l'interpréteur exécute l'instruction `duree_jours = 5`, le symbole `=` ne traduit nullement "
                    "une égalité algébrique mais orchestre une séquence d'allocation et de liaison en trois temps. "
                    "CPython évalue d'abord intégralement l'expression située à droite de l'opérateur, matérialise sur "
                    "le tas un objet contenant son compteur de références (`ob_refcnt`), un pointeur vers son descripteur "
                    "de type (`ob_type` pointant vers `&PyLong_Type`) ainsi que sa charge utile entière `5`, puis inscrit "
                    "l'identifiant symbolique `duree_jours` dans le dictionnaire de l'espace de noms courant en le faisant "
                    "pointer vers l'adresse mémoire de ce `PyObject`.\n\n"
                    "```python — Inspection de l'identité mémoire et du descripteur de type CPython\n"
                    "duree_jours = 5\n"
                    "alias_duree = duree_jours\n"
                    "print(type(duree_jours))          # <class 'int'> (porté par l'objet en RAM, pas par le nom)\n"
                    "print(id(duree_jours) == id(alias_duree))  # True : deux étiquettes vers le même PyObject\n"
                    "```\n\n"
                    "#### Typage dynamique fort et annotations PEP 484 dans FastAPI\n\n"
                    "Parce que le descripteur `ob_type` réside dans l'objet en RAM et non sur l'étiquette lexicale, "
                    "Python pratique un **typage dynamique** : un même nom pourrait techniquement être relié plus tard à "
                    "une chaîne. Mais Python applique simultanément un **typage fort** : l'interpréteur refuse toute "
                    "opération implicite ambiguë entre types hétérogènes. Évaluer `\"5\" + 2` lève instantanément une "
                    "exception `TypeError`, là où JavaScript convertirait silencieusement l'entier pour produire `\"52\"`.\n\n"
                    "> « Les annotations de type ne modifient pas à elles seules l'exécution dynamique de Python, mais elles offrent aux frameworks et analyseurs statiques un métalangage formel inspectable à l'exécution. » — PEP 484 (Type Hints, Guido van Rossum)\n\n"
                    "C'est précisément cette introspection à l'exécution (`__annotations__`) qu'exploite **FastAPI** : "
                    "lorsque vous annotez `duree_jours: int = 5`, FastAPI lit ce contrat au démarrage du serveur Uvicorn "
                    "et compile un schéma de validation dans `pydantic-core` (écrit en Rust) capable de convertir ou "
                    "rejeter les octets entrants à plusieurs centaines de milliers d'opérations par seconde."
                )
            },
            {
                "heading": "2. Isomorphisme et frictions entre scalaires Python et primitives JSON (RFC 8259)",
                "body": (
                    "Dès qu'une donnée quitte la mémoire vive d'un worker Uvicorn pour traverser une connexion réseau, "
                    "les pointeurs C de `PyObject` ne peuvent plus exister : l'état doit être projeté vers une séquence "
                    "linéaire d'octets UTF-8 conforme à la grammaire universelle **JSON (*JavaScript Object Notation*, "
                    "IETF RFC 8259)**. Or, l'alphabet scalaire de JSON est volontairement minimaliste afin d'être "
                    "compris sans ambiguïté aussi bien par un microcontrôleur C embarqué que par un navigateur Web.\n\n"
                    "#### Les quatre types scalaires normatifs de la RFC 8259\n\n"
                    "La grammaire JSON ne reconnaît que quatre primitives élémentaires : la chaîne Unicode `string` "
                    "délimitée exclusivement par des guillemets doubles `\"...\"` (les apostrophes simples Python `'...'` "
                    "y sont illégales), le type numérique unifié `number` couvrant indifféremment entiers `int` et "
                    "flottants `float` en base 10, le booléen `boolean` orthographié en minuscules strictes `true` ou "
                    "`false`, et enfin le littéral `null` traduisant le singleton Python `None`.\n\n"
                    "```json — Charge utile JSON conforme à la RFC 8259 émise par FastAPI\n"
                    "{\n"
                    "  \"organisme\": \"ISGP\",\n"
                    "  \"duree_jours\": 5,\n"
                    "  \"taux_reussite\": 98.5,\n"
                    "  \"est_ouverte\": true,\n"
                    "  \"prerequis\": null\n"
                    "}\n"
                    "```\n\n"
                    "> [!WARNING] Précision monétaire IEEE 754 : `float` binaire contre entiers en centimes\n"
                    "> En Python comme dans tous les processeurs conformes à la norme IEEE 754 sur 64 bits, un `float` représente une fraction binaire et non décimale : l'expression `0.1 + 0.2` produit `0.30000000000000004`. Dans une API bancaire ou fiscale FastAPI, on représente toujours les montants soit en **unité entière minimale** (`montant_centimes: int = 150050`), soit via `decimal.Decimal` sérialisé explicitement par Pydantic v2."
                )
            },
            {
                "heading": "3. Introspection défensive à l'exécution (`isinstance`) et piège d'héritage `bool` / `int`",
                "body": (
                    "Lorsqu'un flux réseau externe pénètre dans un composant Python — qu'il provienne d'une Query String "
                    "d'URL où tout arrive sous forme de `str`, ou d'un parseur JSON générique `json.loads()` —, "
                    "l'ingénieur ne présume jamais que le client a respecté la documentation publiée. Un partenaire "
                    "défaillant peut parfaitement expédier `{\"duree_jours\": \"cinq\"}` ou `{\"duree_jours\": true}` "
                    "là où votre calcul attendait l'entier `5`.\n\n"
                    "#### Privilégier `isinstance()` sur `type() ==` et déjouer la sous-classe `bool`\n\n"
                    "Pour contrôler dynamiquement le type d'une référence en Python pur, la primitive canonique est "
                    "`isinstance(valeur, (int, float))` plutôt qu'une égalité rigide `type(valeur) == int`, car "
                    "`isinstance` respecte le polymorphisme d'héritage orienté objet. Il subsiste toutefois une "
                    "particularité historique célèbre héritée de Python 2.3 qu'il faut absolument connaître lors de "
                    "l'écriture de validateurs personnalisés : **en Python, la classe `bool` est une sous-classe directe "
                    "de `int`**, où `True` vaut numériquement `1` et `False` vaut `0`.\n\n"
                    "```python — Subtilité d'héritage CPython entre bool et int\n"
                    "print(issubclass(bool, int))                         # True !\n"
                    "print(isinstance(True, int))                         # True (piège classique en validation JSON)\n"
                    "est_entier_strict = isinstance(val, int) and not isinstance(val, bool)\n"
                    "```\n\n"
                    "> [!TIP] Mode strict (`strict=True`) dans Pydantic v2 et FastAPI\n"
                    "> Par défaut, FastAPI applique une coercition pragmatique idéale pour les paramètres d'URL (`\"5\"` reçu dans `/formations/5` devient l'entier `5`). Sur un corps JSON critique où vous souhaitez refuser que `\"5\"` ou `True` soit converti silencieusement en `5`, Pydantic v2 offre `Field(strict=True)` ou `ConfigDict(strict=True)` exécuté directement dans le noyau Rust."
                )
            }
        ],
        "architecture_diagram": (
            "ESPACE DES NOMS PYTHON (Variables)          MÉMOIRE VIVE (Objets PyObject en RAM)       TRADUCTION RÉSEAU (JSON)\n"
            "----------------------------------          -------------------------------------       ------------------------\n"
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
                ["`float`", "`19.0`, `98.45`", "`number`", "`19.0`, `98.45`", "Taux statistiques, coordonnées GPS, mesures physiques"],
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
                "why": "En Python, `true` sans majuscule déclenche une erreur `NameError: name 'true' is not defined`. C'est le sérialiseur JSON qui le convertit en `true` minuscule."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur Python ci-dessus, créez une variable `prix_ht_centimes = 150050` (`int`) et un drapeau `exonere_tva = False` (`bool`), puis inspectez leurs descripteurs mémoire avec `type()` et `id()`.",
            "Comparez sur la sortie standard le résultat de `100 + 50` face à `\"100\" + \"50\"` afin de visualiser concrètement l'opposition entre addition entière et concaténation UTF-8.",
            "Écrivez une expression booléenne combinant `isinstance(val, int)` et `not isinstance(val, bool)` puis vérifiez qu'elle accepte `42` tout en rejetant `True`."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.2 : LISTES, DICTIONNAIRES & STRUCTURES IMBRIQUÉES
    # =========================================================================
    "d0-l2": {
        "context": (
            "Aucun service Web de production ne se borne à échanger un entier solitaire sur le réseau : une réponse "
            "métier transporte toujours des **agrégats hiérarchiques**, tels que le dossier complet d'une session de "
            "formation associant ses métadonnées administratives, les coordonnées de son intervenant et le tableau "
            "ordonné des participants inscrits.\n\n"
            "En Python comme dans la grammaire RFC 8259 de JSON, l'intégralité de la modélisation documentaire repose "
            "sur la composition récursive de deux structures de données natives : le **Dictionnaire (`dict`)** qui "
            "représente une entité par ses attributs nommés en temps constant, et la **Liste (`list`)** qui maintient "
            "une séquence ordonnée d'éléments. Maîtriser l'architecture interne de ces conteneurs et leur parcours "
            "défensif constitue le socle direct sur lequel s'appuient les modèles imbriqués de Pydantic v2."
        ),
        "deep_sections": [
            {
                "heading": "1. Mécanique interne d'un Dictionnaire CPython (`dict` — Table de Hachage Compacte)",
                "body": (
                    "Contrairement à une liste associative naïve qui parcourrait ses paires une à une de gauche à droite, "
                    "le type `dict` de Python (`{\"titre\": \"API REST\", \"jours\": 5}`) est implémenté en langage C "
                    "sous la forme d'une **table de hachage à adressage ouvert (*Compact Open-Addressing Hash Table*)**, "
                    "repensée depuis Python 3.6 par Raymond Hettinger pour allier vitesse d'accès et préservation de "
                    "l'ordre d'insertion des clés.\n\n"
                    "#### Fonction de hachage SipHash, complexité `O(1)` et unicité des clés\n\n"
                    "Lorsque votre code évalue `formation[\"titre\"]`, CPython calcule en quelques nanosecondes "
                    "l'empreinte entière 64 bits `hash(\"titre\")` via l'algorithme cryptographiquement salé *SipHash* "
                    "(qui protège les serveurs Web contre les attaques par collision de hachage *HashDoS*), applique un "
                    "masque binaire pour trouver directement l'alvéole correspondante en RAM et restitue le pointeur de "
                    "la valeur. Que le dictionnaire comporte trois attributs ou un million d'entrées en cache, le temps "
                    "de recherche demeure **strictement constant en moyenne (`O(1)`)**.\n\n"
                    "> [!IMPORTANT] Unicité des clés et convention `snake_case` dans les contrats REST\n"
                    "> Par construction mathématique d'une table de hachage, chaque clé d'un dictionnaire est unique : déclarer deux fois la clé `\"salle\"` dans un même littéral `{...}` écrase silencieusement la première valeur par la seconde. Dans l'écosystème Python et FastAPI, les clés JSON et attributs Pydantic adoptent uniformément la casse `snake_case` (`duree_jours`, `cree_le`), quitte à exposer un `validation_alias` ou `serialization_alias` `camelCase` si un client JavaScript historique l'exige."
                )
            },
            {
                "heading": "2. Programmation défensive : lecture par `.get()` face aux exceptions fatales `KeyError`",
                "body": (
                    "Lorsqu'un programme manipule un dictionnaire issu d'une source externe — réponse d'une API "
                    "partenaire, configuration dynamique ou charge utile JSON non contrainte —, la présence effective "
                    "de chaque clé optionnelle n'est jamais garantie. Tenter de résoudre une clé absente par l'opérateur "
                    "d'indexation directe `corps[\"salle\"]` déclenche instantanément au cœur de CPython une exception "
                    "**`KeyError: 'salle'`**. Si cette exception n'est pas interceptée, elle traverse la pile ASGI "
                    "d'Uvicorn et inflige à l'appelant une panne brutale **`500 Internal Server Error`**.\n\n"
                    "```python — Contraste entre indexation fragile et lecture défensive .get()\n"
                    "corps_client = {\"titre\": \"Sécurité des APIs\", \"duree_jours\": 4}\n"
                    "\n"
                    "# Approche fragile : lève KeyError('salle') -> Crash HTTP 500 si non géré\n"
                    "# salle = corps_client[\"salle\"]\n"
                    "\n"
                    "# Approche défensive : restitue 'Amphithéâtre A' en O(1) sans jamais lever d'exception\n"
                    "salle = corps_client.get(\"salle\", \"Amphithéâtre A\")\n"
                    "# Navigation sécurisée dans un sous-objet potentiellement absent :\n"
                    "ville = (corps_client.get(\"localisation\") or {}).get(\"ville\", \"Alger\")\n"
                    "```\n\n"
                    "Notez dans la dernière ligne l'idiome industriel `(d.get(\"sous_objet\") or {}).get(...)` : si un "
                    "client envoie explicitement `{\"localisation\": null}` en JSON, `d.get(\"localisation\", {})` "
                    "renverrait `None` (puisque la clé existe et vaut `None` !), alors que l'opérateur court-circuit "
                    "`or {}` garantit dans tous les cas un dictionnaire vide sur lequel chaîner le second `.get()`."
                )
            },
            {
                "heading": "3. Tableaux dynamiques (`list`), découpage mémoire (*Slicing*) et patron « Liste de Dictionnaires »",
                "body": (
                    "Le type `list` de Python (`[elem0, elem1, elem2]`) n'est pas une liste chaînée dispersée en RAM, "
                    "mais un **tableau dynamique contigu de pointeurs `PyObject*`** sur-alloué de manière géométrique "
                    "afin que `liste.append(item)` s'exécute en temps amorti `O(1)`. L'adressage par décalage nul "
                    "(*zero-based indexing*) place invariablement le premier élément à `liste[0]` et le dernier à "
                    "`liste[-1]`, tandis que l'opérateur de tranche **`liste[offset : offset + limit]`** extrait une "
                    "sous-liste bornée sans jamais lever `IndexError` même lorsque `offset + limit` dépasse la fin du "
                    "tableau — une propriété précieuse pour paginer une collection en mémoire.\n\n"
                    "#### Le patron universel « Liste de Dictionnaires » entre SQL et JSON\n\n"
                    "Dans 95 % des routes de collection d'une API FastAPI, le flux de données emprunte une forme "
                    "canonique appelée **Liste de Dictionnaires (`list[dict[str, Any]]`)** ou **Liste de Modèles "
                    "(`list[FormationOut]`)**. Lorsque le connecteur SQLite ou PostgreSQL exécute `SELECT id, titre, "
                    "duree_jours FROM formations`, l'ensemble des lignes retournées forme la liste externe `[...]`, "
                    "tandis que chaque ligne individuelle est projetée en un dictionnaire `{...}` associant le nom de "
                    "colonne à sa valeur scalaire, prêt à être validé et sérialisé vers le réseau."
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
                ["`dict`", "Ajout / Modification", "`d[\"statut\"] = \"actif\"`", "Crée ou écrase la clé (`O(1)`)", "Enrichir une réponse avec un horodatage"],
                ["`list`", "Ajout en fin de collection", "`liste.append(item)`", "Ajoute à l'indice `len(liste)` (`O(1)` amorti)", "Accumuler les erreurs de validation RFC 7807"],
                ["`list`", "Découpage (Slicing)", "`liste[offset : offset + limit]`", "Extrait une sous-liste sans erreur si hors bornes", "Implémenter la pagination `?page=1&limit=10`"],
                ["`list`", "Filtrage (Compréhension)", "`[x for x in liste if x[\"id\"] == 1]`", "Crée une nouvelle liste filtrée (`O(N)`)", "Filtrer une collection par critère"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Accéder aux données dynamiques entrées par l'utilisateur avec `corps[\"champ\"]`",
                "good": "Utiliser `corps.get(\"champ\")` ou un schéma déclaratif Pydantic `BaseModel`",
                "why": "Protège le serveur contre les exceptions non gérées `KeyError` lorsqu'un client envoie un JSON incomplet."
            },
            {
                "bad": "Chercher le 1er élément d'une liste avec `liste[1]` ou sans vérifier si la liste est vide",
                "good": "Vérifier `if liste:` avant de lire `liste[0]`",
                "why": "L'indexation commence à `0` ; en outre, lire `liste[0]` sur une liste vide `[]` provoque un crash `IndexError: list index out of range`."
            },
            {
                "bad": "Renvoyer une liste brute `[...]` à la racine d'une réponse API JSON",
                "good": "Envelopper la liste dans un dictionnaire : `{\"meta\": {\"total\": len(items)}, \"data\": [...]}`",
                "why": "Un dictionnaire racine permet d'ajouter ultérieurement des métadonnées (`page`, `next_cursor`) sans casser le contrat JSON des clients."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur Python ci-dessus, ajoutez un quatrième stagiaire à la collection à l'aide de `.append()` en y intégrant un booléen `\"certifie\": True`, puis affichez la cardinalité totale avec `len()`.",
            "Rédigez une compréhension de liste qui extrait uniquement les stagiaires rattachés aux services `\"Sécurité\"` ou `\"Réseau\"` sans muter la liste originale.",
            "Expérimentez l'expression `(stagiaires[0].get(\"coordonnees\") or {}).get(\"telephone\", \"Non renseigné\")` pour vérifier sa résilience face aux clés absentes ou nulles."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.3 : FONCTIONS, PARAMÈTRES, RETURN & STATUTS FASTAPI
    # =========================================================================
    "d0-l3": {
        "context": (
            "Au sein d'une application FastAPI, **chaque endpoint réseau se ramène exactement à une fonction Python** : "
            "lorsqu'une requête `GET /api/v1/formations` franchit le socket d'Uvicorn, le routeur Starlette résout les "
            "paramètres déclarés dans la signature de la fonction associée, l'exécute, puis capture l'objet restitué par "
            "l'instruction **`return`** pour forger la réponse HTTP JSON expédiée au client.\n\n"
            "Une confusion conceptuelle persistante chez les développeurs novices assimile l'écriture sur la console "
            "d'administration (`print()`) et la restitution d'une valeur au cadre appelant (`return`). Ce chapitre "
            "décortique la mécanique de la pile d'appels (*call stack*), l'introspection de signature par `inspect.signature`, "
            "le patron industriel des clauses de garde (*Guard Clauses*) et l'orchestration des statuts HTTP dans FastAPI."
        ),
        "deep_sections": [
            {
                "heading": "1. Cadres d'exécution (*Stack Frames*), signature typée et piège des défauts mutables",
                "body": (
                    "Chaque invocation d'une fonction définie par `def` (ou d'une coroutine définie par `async def`) "
                    "alloue en mémoire une structure isolée appelée **cadre d'exécution (*Frame Object*)**. Ce cadre "
                    "lie les arguments reçus aux noms des paramètres déclarés entre parenthèses, héberge toutes les "
                    "variables locales créées dans le bloc indenté, puis se détruit intégralement dès que l'instruction "
                    "`return` restitue le contrôle à l'appelant — ou à la fin du bloc en renvoyant implicitement `None`.\n\n"
                    "#### Comment FastAPI lit vos signatures avec `inspect.signature()`\n\n"
                    "Contrairement aux frameworks anciens où une route recevait un unique objet `request` fourre-tout, "
                    "FastAPI inspecte au démarrage l'objet Python `inspect.signature(votre_fonction)`. Un paramètre sans "
                    "valeur par défaut (`montant_ht: float`) est automatiquement enregistré comme **obligatoire** dans le "
                    "contrat OpenAPI, tandis qu'un paramètre doté d'une valeur par défaut (`taux_tva: float = 0.19`) "
                    "devient **optionnel**.\n\n"
                    "> [!WARNING] L'erreur classique en Python : la valeur par défaut mutable (`def f(items=[]):`)\n"
                    "> En Python, les expressions de valeurs par défaut dans `def` sont évaluées **une seule fois au chargement du fichier `.py`**, et non à chaque appel ! Écrire `def ajouter_tag(tag: str, liste: list = []):` partage exactement la même liste en RAM entre tous les clients successifs du serveur. On utilise toujours `liste: list | None = None` suivi de `if liste is None: liste = []`."
                )
            },
            {
                "heading": "2. Clauses de garde (*Early Return* & `HTTPException`) dans les contrôleurs d'API",
                "body": (
                    "Puisque l'instruction `return` — tout comme la levée d'une exception `raise HTTPException(...)` — "
                    "interrompt à l'instant même l'exécution de la fonction, l'ingénierie logicielle moderne proscrit "
                    "les pyramides illisibles de `if / else` imbriqués sur cinq niveaux d'indentation (*Arrow Anti-Pattern*). "
                    "On structure systématiquement chaque contrôleur selon le patron des **clauses de garde (*Guard Clauses*)**.\n\n"
                    "```python — Contrôleur FastAPI structuré par clauses de garde (Early Exit)\n"
                    "@app.post(\"/api/v1/factures\", status_code=201)\n"
                    "def emettre_facture(client_actif: bool, montant_ht: float):\n"
                    "    if not client_actif:\n"
                    "        raise HTTPException(status_code=403, detail=\"Compte client suspendu\")\n"
                    "    if montant_ht <= 0:\n"
                    "        raise HTTPException(status_code=422, detail=\"Le montant HT doit être strictement positif\")\n"
                    "\n"
                    "    # Chemin nominal (Happy Path) aligné au premier niveau d'indentation :\n"
                    "    montant_ttc = round(montant_ht * 1.19, 2)\n"
                    "    return {\"montant_ht\": montant_ht, \"montant_ttc\": montant_ttc, \"devise\": \"DZD\"}\n"
                    "```\n\n"
                    "En éliminant dès les premières lignes les préconditions invalides par sortie anticipée, le chemin "
                    "nominal (*Happy Path*) demeure parfaitement plat, linéaire et immédiatement auditable lors d'une "
                    "revue de sécurité."
                )
            },
            {
                "heading": "3. Décompactage de Tuples en Python pur face au contrat de réponse FastAPI",
                "body": (
                    "En Python standard, séparer plusieurs expressions par des virgules derrière `return` (`return corps, 201`) "
                    "construit un **Tuple immuable** `(corps, 201)` que le code appelant peut décompacter en une ligne "
                    "élégante : `donnees, code_http = construire_reponse_api(\"Docker\", 4)`. Attention cependant à ne "
                    "pas transposer aveuglément cette habitude issue de Flask directement dans une route FastAPI !\n\n"
                    "> [!IMPORTANT] Statut HTTP nominal dans FastAPI vs Tuple Flask\n"
                    "> Dans Flask, écrire `return jsonify(d), 201` interprétait le tuple comme `(corps, code_http)`. Dans **FastAPI**, si une route exécute `return d, 201`, FastAPI considère que vous souhaitez sérialiser un tableau JSON à deux éléments `[{...}, 201]` avec le statut `200 OK` ! Dans FastAPI, le code nominal se déclare toujours dans le décorateur `@app.post(\"/url\", status_code=status.HTTP_201_CREATED)` (ou dynamiquement via `response.status_code = ...` / `JSONResponse`), et `return` ne renvoie que l'objet métier pur."
                )
            }
        ],
        "architecture_diagram": (
            "REQUÊTE CLIENT HTTP               FONCTION PYTHON (Route FastAPI)              SORTIE\n"
            "-------------------               -------------------------------              ------\n"
            "POST /api/formations   ======>    @app.post(\"/api/formations\", status_code=201)\n"
            "                                  def creer_formation(titre: str):             \n"
            "                                      print(\"Log interne\")       --------->   Terminal du serveur uniquement\n"
            "                                      if not titre:                            \n"
            "                                          raise HTTPException(400) =========>  Réponse HTTP 400 envoyée au client\n"
            "                                      return {\"ok\": titre}        =========>  Réponse HTTP 201 envoyée au client"
        ),
        "reference_table": {
            "title": "Comparaison Technique : `print()` vs `return` et Formes de Retour FastAPI",
            "headers": ["Instruction / Syntaxe", "Destinataire de la donnée", "Interrompt la fonction ?", "Valeur reçue par FastAPI", "Résultat pour le client HTTP"],
            "rows": [
                ["`print(donnees)`", "Terminal local (`stdout`)", "Non (continue à la ligne suivante)", "`None` (si aucun `return` suit)", "Réponse JSON **`null`** (aucune donnée transmise au client)"],
                ["`return d`", "Moteur FastAPI → Client HTTP", "Oui (immédiatement)", "Dict / BaseModel (`200 OK` par défaut)", "Réponse JSON avec statut **`200 OK`**"],
                ["`@app.post(..., status_code=201)` + `return d`", "Moteur FastAPI → Client HTTP", "Oui (immédiatement)", "Dict / BaseModel (`201 Created`)", "Réponse JSON avec statut **`201 Created`**"],
                ["`return JSONResponse(content=err, status_code=401, headers=...)`", "Moteur FastAPI → Client HTTP", "Oui (immédiatement)", "Objet `JSONResponse`", "Réponse JSON `401` + en-têtes personnalisés"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Terminer une fonction de route par `print(resultat)` en oubliant `return`",
                "good": "Toujours terminer chaque branche d'exécution par `return resultat` ou `raise HTTPException(...)`",
                "why": "Une fonction sans `return` renvoie `None`, ce que FastAPI sérialise en littéral JSON `null`."
            },
            {
                "bad": "Écrire du code après une instruction `return` dans le même bloc (code mort)",
                "good": "Placer les opérations préparatoires avant `return`",
                "why": "Toute ligne située après `return` dans le même bloc d'indentation n'est jamais atteinte par l'interpréteur."
            },
            {
                "bad": "Utiliser une liste ou un dictionnaire modifiable comme valeur par défaut : `def f(items=[]):`",
                "good": "Utiliser `None` par défaut : `def f(items: list | None = None): items = items if items is not None else []`",
                "why": "En Python, une liste par défaut `[]` dans `def` est instanciée une seule fois au chargement et partagée entre tous les appels !"
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur ci-dessus, invoquez `construire_reponse_api(\"\", 3)` et vérifiez comment la première clause de garde court-circuite l'exécution en restituant immédiatement le code `400`.",
            "Enrichissez `construire_reponse_api` d'une seconde clause de garde renvoyant le code `422` lorsque `duree_jours` excède le plafond métier de `30` jours.",
            "Décompactez le tuple retourné dans deux variables distinctes `corps, code = construire_reponse_api(\"Docker & Kubernetes\", 4)` puis affichez-les séparément."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.4 : EXCEPTIONS (TRY/EXCEPT) & DÉCORATEURS (@)
    # =========================================================================
    "d0-l4": {
        "context": (
            "Quiconque ouvre le code source d'un microservice FastAPI en production rencontre dès les dix premières "
            "lignes deux idiomes fondamentaux du langage Python : les mécanismes d'interception structurée d'erreurs "
            "**`try / except`** (prolongés par `@app.exception_handler`) et les annotations précédées du symbole arobase "
            "**`@`** telles que `@app.get(\"/api/formations\")`, appelées **Décorateurs**.\n\n"
            "Apprendre à recopier `@app.post(...)` comme une incantation opaque interdit de comprendre comment FastAPI "
            "construit sa table de routage ASGI ou pourquoi l'oubli d'une métadonnée sur un décorateur artisanal brise "
            "la validation Pydantic. Ce chapitre démonte pièce par pièce le déroulement de pile (*stack unwinding*) des "
            "exceptions CPython ainsi que les fermetures lexicales (*closures*) qui animent les décorateurs."
        ),
        "deep_sections": [
            {
                "heading": "1. Déroulement de pile (*Stack Unwinding*) et isolation des pannes par `try / except / finally`",
                "body": (
                    "Lorsqu'une opération illégale survient au cœur d'une fonction — tentative de convertir `int(\"abc\")`, "
                    "division par zéro, violation d'unicité SQLite —, CPython interrompt immédiatement la ligne en cours, "
                    "instancie un objet dérivé de `BaseException` et entame une **remontée de la pile d'appels (*Stack "
                    "Unwinding*)** cadre par cadre à la recherche d'un gestionnaire `except` compatible.\n\n"
                    "Sur un script local mono-utilisateur, laisser l'exception atteindre le sommet du programme affiche un "
                    "*Traceback* et termine le processus. Sur un worker Uvicorn desservant cinq cents connexions simultanées, "
                    "une telle défaillance non maîtrisée coupe la requête avec une erreur `500` et risque, si le serveur est "
                    "mal configuré en mode débogage, de divulguer l'arborescence interne de vos fichiers.\n\n"
                    "#### Cible précise de capture et garantie de nettoyage `finally`\n\n"
                    "Un bloc `try` professionnel restreint toujours sa zone de surveillance au strict minimum d'instructions "
                    "susceptibles d'échouer et nomme explicitement la classe d'exception attendue (`except ValueError as err:`), "
                    "tandis qu'une clause éventuelle `finally:` garantit l'exécution inconditionnelle du nettoyage (fermeture "
                    "d'un descripteur de fichier ou d'une transaction SQL), qu'une erreur ait eu lieu ou non."
                )
            },
            {
                "heading": "2. Démystification mécanique des Décorateurs `@` : fonctions de première classe et *Closures*",
                "body": (
                    "En Python, une déclaration `def traiter_paiement(montant):` ne crée pas une construction figée du "
                    "compilateur : elle instancie en RAM un objet de type `function` tout aussi manipulable qu'un entier "
                    "ou un dictionnaire. Dès lors, une fonction dite **d'ordre supérieur** peut accepter `fonction_cible` "
                    "en paramètre, définir une fonction interne `enveloppe` qui capture `fonction_cible` dans sa fermeture "
                    "lexicale (*closure*), et retourner cette enveloppe enrichie.\n\n"
                    "> « La syntaxe `@decorateur` placée au-dessus d'une définition `def f():` n'est qu'un sucre syntaxique formellement équivalent à l'affectation post-définition `f = decorateur(f)`. » — PEP 318 (Decorators for Functions and Methods)\n\n"
                    "```python — Équivalence exacte exécutée par Python lors du chargement du module\n"
                    "# Écriture idiomatique avec le sucre syntaxique @ :\n"
                    "@journaliser_appel\n"
                    "def traiter_paiement(montant: int) -> dict:\n"
                    "    return {\"statut\": \"valide\", \"montant\": montant}\n"
                    "\n"
                    "# Traduction interne strictement identique effectuée par l'interpréteur :\n"
                    "traiter_paiement = journaliser_appel(traiter_paiement)\n"
                    "```\n\n"
                    "#### Ce que fait réellement `@app.get(\"/api/formations\")` dans FastAPI\n\n"
                    "Notez une subtilité architecturale décisive : dans FastAPI, `@app.get(\"/api/formations\")` ne remplace "
                    "même pas votre fonction par une enveloppe lourde ! Il lit votre fonction originale, inspecte ses "
                    "annotations de type Python via `get_typed_signature()`, compile un objet `APIRoute` (contenant le "
                    "modèle Pydantic d'entrée, le `response_model` et l'arbre `Dependant`), l'ajoute à `app.routes`, puis "
                    "**retourne votre fonction originale intacte** afin qu'elle demeure appelable telle quelle dans vos tests unitaires."
                )
            },
            {
                "heading": "3. Signature polymorphe `*args, **kwargs`, `@functools.wraps` et introspection FastAPI",
                "body": (
                    "Lorsque vous écrivez vous-même un décorateur transversal (par exemple pour instrumenter le temps CPU "
                    "d'une fonction métier), sa fonction interne `enveloppe(*args, **kwargs)` utilise l'opérateur de "
                    "regroupement positionnel `*args` (tuple) et nommé `**kwargs` (dictionnaire) afin d'accepter n'importe "
                    "quelle arité de paramètres et de les relayer intégralement à `fonction_cible(*args, **kwargs)`.\n\n"
                    "> [!IMPORTANT] Pourquoi `@functools.wraps(fonction_cible)` est vital avec FastAPI\n"
                    "> Sans `@wraps(fonction_cible)`, la fonction retournée perd le nom (`__name__`), la docstring (`__doc__`) et surtout la signature typée (`__wrapped__`) de la fonction d'origine : `inspect.signature` ne verrait plus que `(*args, **kwargs)` et FastAPI croirait que votre route attend deux paramètres de requête littéraux nommés `args` et `kwargs` ! `@wraps` pose l'attribut `__wrapped__` suivi automatiquement par `inspect.signature` — même si, dans FastAPI, on préférera presque toujours **`Depends()`** aux décorateurs manuels sur les routes."
                )
            }
        ],
        "architecture_diagram": (
            "APPEL CLIENT : traiter_paiement(15000)\n"
            "       |\n"
            "       v\n"
            "+-------------------------------------------------------------------+\n"
            "| DÉCORATEUR (@journaliser_appel -> fonction 'enveloppe')           |\n"
            "|  1. Code AVANT : Vérifie le contexte / Démarre perf_counter()     |\n"
            "|     (Si précondition violée -> sortie immédiate sans entrer !)    |\n"
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
                "good": "Cibler l'exception précise (`except (ValueError, TypeError):`) et renvoyer un diagnostic explicite",
                "why": "Un `except: pass` avale même les erreurs de syntaxe de noms (`NameError`) dans votre code, rendant les pannes indétectables."
            },
            {
                "bad": "Renvoyer `str(exception)` brut d'une erreur SQL ou système au client en production",
                "good": "Journaliser l'erreur technique en interne et renvoyer un message générique assorti d'un `request_id`",
                "why": "Afficher l'erreur brute révèle la structure de vos tables SQL et l'arborescence interne de votre serveur."
            },
            {
                "bad": "Oublier `return fonction_cible(*args, **kwargs)` à l'intérieur de l'enveloppe d'un décorateur",
                "good": "Toujours capturer, journaliser puis retourner explicitement le résultat de la fonction enveloppée",
                "why": "Si l'enveloppe omet `return`, l'appelant (ou FastAPI) reçoit `None` au lieu du dictionnaire métier."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur ci-dessus, invoquez `convertir_parametre_entier(\"-5\")` puis adaptez la fonction afin qu'elle lève et intercepte proprement une `ValueError` sur tout entier inférieur ou égal à zéro.",
            "Écrivez un second décorateur `@verifier_montant_positif` muni de `@wraps` qui court-circuite `traiter_paiement` en retournant `{\"erreur\": \"Montant <= 0 interdit\"}` dès que l'argument est négatif ou nul.",
            "Superposez les deux décorateurs au-dessus de `traiter_paiement` et analysez l'ordre d'emboîtement des traces sur la sortie standard."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.1 : HTML VS SOAP/XML VS REST/JSON
    # =========================================================================
    "d1-l1": {
        "context": (
            "Pourquoi l'intégralité des infrastructures bancaires modernes, des opérateurs télécoms, des portails "
            "ministériels et des plateformes cloud s'articule-t-elle aujourd'hui autour d'**APIs découplées** plutôt "
            "que de serveurs Web monolithiques rendant des pages HTML ?\n\n"
            "Tant qu'une application Web se contente d'interroger sa base relationnelle pour fondre immédiatement les "
            "lignes SQL dans un gabarit graphique (`<html><body><div class=\"card\">...</div></body></html>`), ses "
            "données demeurent prisonnières de leur habillage visuel. Ce modèle s'effondre dès qu'il faut raccorder une "
            "application mobile native iOS ou Android, un terminal de paiement électronique ou le système d'information "
            "d'un partenaire institutionnel. Ce chapitre retrace la généalogie des architectures distribuées sur le Web "
            "et démontre par la mesure d'octets pourquoi le couple **REST / JSON** s'est imposé face à **SOAP / XML**, "
            "tout en situant **GraphQL** et **gRPC**."
        ),
        "deep_sections": [
            {
                "heading": "1. Du couplage monolithique HTML à l'architecture orientée contrat (API-First)",
                "body": (
                    "Dans le modèle Web classique issu de la fin des années 1990 (CGI, PHP historique, JSP, monolithes "
                    "MVC), le serveur fusionne dans la même réponse HTTP le **fond métier** (le solde d'un compte, la "
                    "capacité restante d'une salle) et la **forme typographique** (couleurs, grilles CSS, balises DOM). "
                    "Pour l'œil humain derrière un navigateur, le résultat est immédiatement lisible ; pour un programme "
                    "client écrit en Kotlin, Swift ou Python, ce flux HTML est un bruit syntaxique inexploitable.\n\n"
                    "Si un développeur externe tente malgré tout d'extraire ces valeurs par analyse du HTML (*Web "
                    "Scraping*), la moindre refonte esthétique décidée par un intégrateur graphique — transformer un "
                    "`<table>` en grille `<div class=\"flex-row\">` — brise instantanément la chaîne de production du "
                    "partenaire.\n\n"
                    "#### La séparation canonique du contrat de données\n\n"
                    "L'architecture centrée **API (*Application Programming Interface*)** opère une scission radicale : "
                    "le serveur backend FastAPI renonce à toute mise en page par défaut et n'expose que des **structures "
                    "de données pures, typées et versionnées (JSON)**. Dès lors, le portail Web React/Vue, l'application "
                    "mobile native, l'automate batch nocturne et la passerelle partenaire deviennent des consommateurs "
                    "égaux face à une source de vérité unique, gouvernée par un contrat formel OpenAPI 3.1."
                )
            },
            {
                "heading": "2. Archéologie et confrontation : SOAP/XML (WS-*) face à l'architecture REST/JSON",
                "body": (
                    "Deux philosophies majeures d'interopérabilité machine-à-machine se sont affrontées au tournant des "
                    "années 2000. La première génération industrielle, **SOAP (*Simple Object Access Protocol*)**, a "
                    "transposé le modèle d'appel de procédures distantes (RPC) dans une enveloppe **XML** rigide "
                    "accompagnée d'un contrat **WSDL (*Web Services Description Language*)** et d'une pile d'extensions "
                    "complexe (*WS-Security*, *WS-Addressing*).\n\n"
                    "Dans SOAP, le protocole HTTP est rabaissé au rang de simple tuyau aveugle : que l'on souhaite lire "
                    "une météo, supprimer un dossier ou virer des fonds, tout transite généralement par `POST /ws` avec "
                    "`200 OK` même en cas de faute applicative (`<soap:Fault>`), obligeant les pare-feux, proxys et "
                    "clients à parser un arbre DOM XML trois à cinq fois plus volumineux que la donnée utile.\n\n"
                    "> « REST n'est pas un protocole supplémentaire empilé par-dessus HTTP, mais un ensemble coordonné de contraintes architecturales conçu pour exploiter pleinement la sémantique native du Web à l'échelle planétaire. » — Roy Thomas Fielding, Thèse de doctorat (UC Irvine, Chapitre 5, 2000)\n\n"
                    "```http — Contraste d'empreinte réseau : lecture REST/JSON face à un tunnel SOAP\n"
                    "GET /api/v1/meteo?ville=Alger HTTP/1.1\n"
                    "Host: api.isgp.dz\n"
                    "Accept: application/json\n"
                    "\n"
                    "HTTP/1.1 200 OK\n"
                    "Content-Type: application/json; charset=utf-8\n"
                    "\n"
                    "{\"ville\": \"Alger\", \"temperature_c\": 24, \"statut\": \"Ensoleillé\"}\n"
                    "```\n\n"
                    "En réhabilitant les URIs pour nommer les ressources, les verbes HTTP (`GET`, `POST`, `PUT`, "
                    "`PATCH`, `DELETE`) pour exprimer l'intention, les codes d'état (`200`, `201`, `404`, `422`) pour "
                    "qualifier l'issue et les en-têtes pour piloter le cache HTTP natif, **REST associé à JSON** a divisé "
                    "par quatre la consommation de bande passante et le coût CPU de désérialisation."
                )
            },
            {
                "heading": "3. Arbitrage contemporain : quand retenir REST/JSON, GraphQL ou gRPC ?",
                "body": (
                    "En ingénierie contemporaine, aucun paradigme n'est dogmatique : le choix résulte d'un arbitrage "
                    "entre lisibilité universelle, latence réseau et topologie des consommateurs. **REST/JSON** demeure "
                    "le standard hégémonique (plus de 85 % des APIs publiques et d'entreprise) chaque fois que l'on "
                    "recherche une compatibilité immédiate avec tous les langages, une observabilité limpide avec `curl`, "
                    "la mise en cache HTTP standard (`304 Not Modified`, CDN) et la validation automatique par OpenAPI 3.1 "
                    "dans FastAPI.\n\n"
                    "#### Les créneaux spécialisés de GraphQL et gRPC\n\n"
                    "Lorsque des écrans mobiles riches doivent agréger en un seul aller-retour réseau des projections "
                    "très variables d'un graphe d'entités sans subir ni sur-téléchargement (*over-fetching*) ni cascade "
                    "de requêtes (*under-fetching*), **GraphQL** (introduit par Meta en 2015, intégrable sur FastAPI via "
                    "*Strawberry*) apporte une souplesse de sélection côté client, au prix d'une complexification du "
                    "cache HTTP et du contrôle de débit.\n\n"
                    "À l'autre extrémité du spectre, pour les communications internes **Est-Ouest** à très haute "
                    "fréquence entre microservices d'un même centre de données (dizaines de milliers d'appels par "
                    "seconde), **gRPC** combine le multiplexage binaire **HTTP/2** et la sérialisation compacte "
                    "**Protocol Buffers (`.proto`)** afin de minimiser la latence inter-processus."
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE MONOLITHE HTML (Couplage fort)           ARCHITECTURE CENTRÉE API REST (Découplage total)\n"
            "-------------------------------------------           ------------------------------------------------\n"
            "[Base SQL] -> [Serveur] --(HTML+CSS)--> Navigateur    [Base SQL] -> [Serveur FastAPI] ===(JSON Pur)===+--> Portail Web (PWA/React)\n"
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
                ["**Contrat d'interface**", "Aucun (Visuel)", "Fichier `WSDL` / `XSD`", "Spécification **OpenAPI 3.1 (Swagger)**", "Fichier `.proto`"]
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
            "Exécutez le script `day_1/01_html_vs_json.py` ci-dessus afin de mesurer au niveau de l'octet près l'écart de charge utile entre le document HTML Jinja2, l'enveloppe SOAP/XML et la réponse REST/JSON de FastAPI.",
            "Enrichissez le dictionnaire retourné par la route REST d'un attribut `\"lieu\": \"Alger\"` et constatez que son empreinte totale demeure plus de deux fois inférieure au prologue XML minimal de SOAP."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.2 : PILE RÉSEAU (DNS, IP, PORT TCP, TLS) & URI RFC 3986
    # =========================================================================
    "d1-l2": {
        "context": (
            "Lorsqu'un client JavaScript exécute `fetch(\"https://api.isgp.dz:8443/v1/formations?salle=Alger\")` ou "
            "qu'un ingénieur démarre `uvicorn.run(app, host=\"0.0.0.0\", port=8000)`, quels mécanismes physiques et "
            "noyau s'enclenchent sur les interfaces réseau des deux machines ?\n\n"
            "Sans une compréhension rigoureuse de la séparation entre **résolution DNS**, **interface IP d'écoute** "
            "(`127.0.0.1` face à `0.0.0.0`), **descripteur de Port TCP** (`:8000`, `:443`), **poignée de main TLS** et "
            "**grammaire d'URI RFC 3986**, le moindre incident de déploiement Docker ou cloud (`Connection refused`, "
            "`Errno 98 Address already in use`, `Temporary failure in name resolution`) demeure une énigme opaque. "
            "Ce chapitre descend dans la pile TCP/IP jusqu'au socket d'écoute ASGI d'Uvicorn."
        ),
        "deep_sections": [
            {
                "heading": "1. Traversée de la pile réseau : du résolveur DNS au descripteur de Socket TCP d'Uvicorn",
                "body": (
                    "Pour acheminer une requête applicative d'un terminal client jusqu'au processus Python qui héberge "
                    "votre instance `FastAPI()`, le système d'exploitation franchit quatre strates protocolaires "
                    "successives. La première est l'annuaire distribué **DNS (*Domain Name System*)** : les routeurs IP "
                    "ne sachant commuter que des adresses binaires (IPv4 sur 32 bits comme `196.20.45.12` ou IPv6 sur "
                    "128 bits), le client interroge un résolveur DNS pour convertir le nom d'hôte `api.isgp.dz` en "
                    "enregistrement `A`/`AAAA`. Sur la machine locale, le nom réservé **`localhost`** court-circuite le "
                    "réseau externe via `/etc/hosts` et pointe vers l'interface virtuelle de bouclage **`127.0.0.1`** (*loopback*).\n\n"
                    "#### Démultiplexage par Port TCP (1 à 65535) et tunnel cryptographique TLS 1.3\n\n"
                    "Une fois la machine cible atteinte grâce à son **Adresse IP**, il reste à désigner lequel des "
                    "dizaines de démons actifs sur ce serveur (PostgreSQL sur `:5432`, SSH sur `:22`, Nginx sur `:443`, "
                    "Uvicorn sur `:8000`) doit recevoir les octets. C'est le rôle du **numéro de Port TCP** codé sur "
                    "16 bits : le noyau Linux maintient une table associant chaque couple `(IP, Port)` au descripteur "
                    "de fichier (*socket fd*) d'un processus unique, réalise la poignée de main TCP en trois temps "
                    "(*SYN → SYN-ACK → ACK*), puis, lorsque le schéma est `https`, exécute le *Handshake* **TLS 1.3** "
                    "qui authentifie le certificat X.509 du serveur et dérive une clé symétrique éphémère (ECDHE + AES-GCM) "
                    "avant que le premier caractère HTTP ne circule."
                )
            },
            {
                "heading": "2. Topologie d'écoute dans `uvicorn.run()` : `127.0.0.1` (Loopback) contre `0.0.0.0` (Toutes interfaces)",
                "body": (
                    "Un serveur possède toujours plusieurs interfaces réseau logiques : au minimum la boucle interne "
                    "`lo` (`127.0.0.1`) et une carte Ethernet ou virtuelle `eth0` (par exemple `192.168.1.15` sur un "
                    "réseau local ou `172.17.0.2` à l'intérieur d'un conteneur Docker). Lorsque Uvicorn invoque l'appel "
                    "système POSIX `bind(host, port)`, la valeur choisie pour `host` dicte la frontière physique de "
                    "visibilité de votre API.\n\n"
                    "```bash — Contraste entre écoute locale isolée et écoute conteneur/LAN\n"
                    "# 1. Développement isolé (seuls les processus de la même machine accèdent au port 8000) :\n"
                    "uvicorn main:app --host 127.0.0.1 --port 8000\n"
                    "\n"
                    "# 2. Conteneur Docker ou exposition LAN / Reverse Proxy distant (INADDR_ANY) :\n"
                    "uvicorn main:app --host 0.0.0.0 --port 8000\n"
                    "```\n\n"
                    "> [!IMPORTANT] Le piège numéro 1 des conteneurs Docker : `host=\"127.0.0.1\"`\n"
                    "> À l'intérieur d'un conteneur Docker, `127.0.0.1` désigne la boucle fermée privée du conteneur lui-même ! Si vous lancez Uvicorn sur `127.0.0.1` dans votre `Dockerfile`, même avec `-p 8000:8000`, le pont réseau de l'hôte sera refoulé par `Connection reset / refused`. Dans un conteneur, Uvicorn doit **toujours** se lier à `--host 0.0.0.0`."
                )
            },
            {
                "heading": "3. Décomposition chirurgicale d'une URI selon la norme IETF RFC 3986",
                "body": (
                    "La spécification **IETF RFC 3986 (*Uniform Resource Identifier : Generic Syntax*)**, co-rédigée par "
                    "Tim Berners-Lee et Roy Fielding, découpe toute adresse telle que "
                    "`https://api.isgp.dz:8443/api/v1/formations?salle=Alger&page=2#details` en cinq composants que "
                    "le serveur Uvicorn et le routeur FastAPI exploitent à des niveaux distincts.\n\n"
                    "> « Un identifiant de ressource uniforme (URI) est une séquence compacte de caractères qui identifie une ressource abstraite ou physique selon une syntaxe hiérarchique générique. » — IETF RFC 3986, Section 1.1\n\n"
                    "#### Correspondance exacte entre RFC 3986 et dictionnaire ASGI `scope`\n\n"
                    "Lorsqu'Uvicorn parse la requête entrante, le **`scheme`** (`https` ou `http`) renseigne "
                    "`scope[\"scheme\"]` ; l'**`authority`** regroupe l'hôte et le port TCP (`scope[\"server\"]` et "
                    "l'en-tête obligatoire `Host`) ; le **`path`** hiérarchique (`/api/v1/formations`) est déposé "
                    "décodé dans `scope[\"path\"]` où Starlette sélectionne la route `@app.get(...)` et extrait les "
                    "`Path(...)` ; la **`query`** située après `?` est remise sous forme d'octets bruts dans "
                    "`scope[\"query_string\"]` (`b\"salle=Alger&page=2\"`) pour alimenter vos paramètres `Query(...)` ; "
                    "enfin, le **`fragment`** introduit par `#` (`#details`) est une ancre purement locale que les "
                    "navigateurs retranchent **avant** d'émettre la requête TCP et que le serveur HTTP ne reçoit jamais."
                )
            }
        ],
        "architecture_diagram": (
            "ANATOMIE D'UNE URI (RFC 3986) :\n"
            "  https://api.isgp.dz:8443/api/v1/formations?salle=Alger&page=2#details\n"
            "  \\___/   \\_________/ \\__/\\________________/ \\________________/ \\_____/\n"
            "    |          |        |          |                  |            |\n"
            "  Scheme     Host     Port       Path           Query String    Fragment\n"
            " (TLS/HTTP) (DNS/IP)  (TCP)   (@app.get)       (Query params)  (Navigateur)\n\n"
            "PILE RÉSEAU D'UN APPEL API :\n"
            "  [1. Résolution DNS]  --->  [2. Connexion TCP (IP:Port)]  --->  [3. Handshake TLS]  --->  [4. Requête HTTP]"
        ),
        "reference_table": {
            "title": "Ports Réseau Standards et Adresses IP Spéciales à Connaître",
            "headers": ["Port / Adresse", "Nom Standard", "Service ou Signification Technique"],
            "rows": [
                ["`127.0.0.1` (`localhost`)", "Loopback (Boucle locale)", "Désigne toujours la machine locale elle-même (sans sortir sur la carte Wi-Fi/Ethernet)"],
                ["`0.0.0.0`", "Any Interface (Écoute globale)", "Indique au serveur d'écouter sur toutes les adresses IP de la machine (locale + LAN + Docker)"],
                ["Port `:80`", "HTTP par défaut", "Port implicite d'une URL `http://...` (non chiffré)"],
                ["Port `:443`", "HTTPS par défaut", "Port implicite d'une URL `https://...` (chiffré par TLS/SSL)"],
                ["Port `:8000` / `:8080`", "Ports de développement ASGI", "Ports utilisateurs (> 1024, ne nécessitent pas les droits administrateur `root`)"],
                ["Port `:5432` / `:6379`", "PostgreSQL / Redis", "Ports d'écoute standards des bases SQL et caches mémoire"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Laisser `uvicorn` sur `127.0.0.1` dans un conteneur Docker ou pour un test en salle",
                "good": "Spécifier `uvicorn.run(app, host=\"0.0.0.0\", port=8000)`",
                "why": "Dans un conteneur ou sur un réseau local, écouter uniquement sur `127.0.0.1` rejette toute connexion venant de l'extérieur."
            },
            {
                "bad": "Lancer deux fois le serveur sur le même port `8000` (`OSError: [Errno 98] Address already in use`)",
                "good": "Arrêter le premier processus (`Ctrl+C`) ou choisir un port libre (`port=8001`)",
                "why": "Un numéro de port TCP sur une même adresse IP ne peut être attribué qu'à un seul descripteur d'écoute principal à la fois."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_1/03_analyseur_uri_et_reseau.py` ci-dessus puis ajoutez dans l'URI un second paramètre répété (`&tag=python&tag=asgi`) afin d'observer comment `parse_qs` regroupe automatiquement les valeurs multiples dans une liste.",
            "Retirez le segment `:8443` de l'URI analysée et vérifiez que `composants.port` évalue `None`, confirmant que le client HTTP déduit implicitement le port `443` à partir du schéma `https`."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.3 : TRAME BRUTE HTTP/1.1 & EN-TÊTES STRATÉGIQUES
    # =========================================================================
    "d1-l3": {
        "context": (
            "Une fois le canal TCP ouvert entre le client et le processus Uvicorn, quelle séquence exacte d'octets "
            "franchit la carte réseau ? Contrairement aux protocoles binaires propriétaires, **HTTP/1.1 (IETF RFC 9112)** "
            "est un protocole textuel structuré autour de lignes ASCII séparées par la séquence `CR+LF` (`\\r\\n`).\n\n"
            "Être capable de lire et de forger mentalement une trame HTTP brute — sa ligne de départ, ses en-têtes de "
            "gouvernance, sa frontière vide `\\r\\n\\r\\n` et le décompte exact d'octets UTF-8 de son corps — distingue "
            "immédiatement l'architecte d'API capable de diagnostiquer des anomalies subtiles de troncature JSON, de "
            "négociation MIME ou de sémantique de codes d'état (RFC 9110)."
        ),
        "deep_sections": [
            {
                "heading": "1. L'invariant d'absence d'état (*Statelessness*) et l'autonomie des requêtes HTTP",
                "body": (
                    "La contrainte architecturale cardinale du protocole HTTP (RFC 9110, Section 3.3) est d'être "
                    "**sans état (*Stateless*)** : au niveau protocolaire, chaque requête reçue par le serveur est un "
                    "événement intégralement autonome, dépourvu de toute mémoire implicite des requêtes précédentes "
                    "émises par le même client sur la même connexion TCP persistante (*Keep-Alive*).\n\n"
                    "> « Chaque requête du client vers le serveur doit contenir l'intégralité de l'information nécessaire à la compréhension de la requête, sans pouvoir tirer parti d'un contexte stocké sur le serveur. » — Roy T. Fielding, Architectural Styles and the Design of Network-based Software Architectures (2000)\n\n"
                    "Cette propriété explique simultanément l'exigence de rigueur des en-têtes HTTP et la scalabilité "
                    "horizontale native de FastAPI : puisque la requête transporte sa propre preuve d'identité "
                    "(`Authorization: Bearer ...`), la nature de sa charge (`Content-Type: application/json`) et ses "
                    "préférences de retour (`Accept: application/json`), un répartiteur de charge Nginx peut envoyer "
                    "la requête n°1 au Worker Uvicorn A et la requête n°2 au Worker Uvicorn B sans aucune perte de contexte."
                )
            },
            {
                "heading": "2. Délimitation physique `\\r\\n\\r\\n` et calcul d'octets UTF-8 (`Content-Length`)",
                "body": (
                    "Lorsqu'Uvicorn (via son analyseur C ultra-rapide `httptools`) lit le flux continu d'octets arrivant "
                    "sur le socket TCP, comment distingue-t-il la fin des métadonnées d'en-tête du premier octet de la "
                    "charge utile JSON ? La norme RFC 9112 impose un marqueur physique immuable : chaque ligne d'en-tête "
                    "s'achève par deux octets `0x0D 0x0A` (`\\r\\n`), et la fin du bloc d'en-têtes est scellée par une "
                    "**ligne strictement vide**, soit quatre octets consécutifs **`\\r\\n\\r\\n`**.\n\n"
                    "```http — Anatomie exacte d'une trame HTTP/1.1 sur le fil TCP (octets explicites)\n"
                    "POST /api/v1/formations HTTP/1.1\\r\\n\n"
                    "Host: api.isgp.dz\\r\\n\n"
                    "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...\\r\\n\n"
                    "Content-Type: application/json; charset=utf-8\\r\\n\n"
                    "Content-Length: 44\\r\\n\n"
                    "\\r\\n\n"
                    "{\"titre\": \"Sécurité des APIs\", \"jours\": 5}\n"
                    "```\n\n"
                    "> [!WARNING] `Content-Length` mesure des octets UTF-8, jamais un nombre de caractères !\n"
                    "> En encodage UTF-8, les caractères ASCII occupent 1 octet, mais les lettres accentuées françaises (`é`, `à`, `ê`) occupent **2 octets**, les caractères arabes **2 octets** et certains symboles techniques **3 à 4 octets**. Le mot `\"Sécurité\"` compte 8 caractères (`len(s) == 8`), mais pèse **10 octets** sur le réseau (`len(s.encode(\"utf-8\")) == 10`). Si un client forge un `Content-Length` basé sur `len(s)`, Uvicorn tronquera les 2 derniers octets `\"5}` du JSON et lèvera une erreur `400/422 JSON decode error` !"
                )
            },
            {
                "heading": "3. Taxonomie sémantique des codes de statut HTTP (IETF RFC 9110)",
                "body": (
                    "Les trois chiffres de la ligne de statut (`HTTP/1.1 201 Created`) constituent le premier signal "
                    "inspecté par tout programme consommateur, proxy inverse, CDN ou sonde Prometheus avant même "
                    "d'analyser le corps JSON. La norme RFC 9110 répartit cet espace en cinq classes sémantiques strictes.\n\n"
                    "#### Responsabilité partagée entre client (`4xx`) et serveur (`5xx`)\n\n"
                    "La classe **`2xx` (Succès)** confirme que l'intention a abouti : `200 OK` accompagne une lecture ou "
                    "mise à jour dotée d'un corps, `201 Created` scelle l'allocation d'une nouvelle ressource (idéalement "
                    "assortie de l'en-tête `Location`), `202 Accepted` accuse réception d'un traitement asynchrone différé, "
                    "et `204 No Content` clôt une suppression réussie sans octets superflus. La classe **`3xx`** pilote "
                    "les redirections (`303 See Other` après formulaire) et l'économie de bande passante par cache "
                    "conditionnel (`304 Not Modified`).\n\n"
                    "La frontière opérationnelle la plus scrutée en production sépare la classe **`4xx` (Erreur du Client)** "
                    "de la classe **`5xx` (Défaillance du Serveur)** : un pic de `400/401/403/404/422/429` indique que "
                    "votre API FastAPI fonctionne parfaitement et repousse des requêtes mal formées ou non autorisées, "
                    "tandis qu'une seule alerte `500/502/503/504` signale une panne interne de votre code ou de votre "
                    "base de données exigeant une intervention d'astreinte immédiate."
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
                ["**`413 Payload Too Large`**", "Content Too Large", "4xx Client", "Corps de la requête dépassant la taille maximale autorisée"],
                ["**`422 Unprocessable Entity`**", "Unprocessable Content", "4xx Client", "JSON bien formé mais violant le contrat Pydantic (ex: `duree_jours = -3`)"],
                ["**`429 Too Many Requests`**", "Too Many Requests", "4xx Client", "Quota de **Rate Limiting** dépassé sur la fenêtre de temps"],
                ["**`500 Internal Server Error`**", "Internal Server Error", "5xx Serveur", "Exception Python non gérée côté serveur (bug du code backend)"],
                ["**`502 / 503 / 504`**", "Bad Gateway / Unavailable / Timeout", "5xx Serveur", "Serveur en maintenance, base de données injoignable ou timeout amont"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Renvoyer `200 OK` pour tout, même en cas d'erreur : `return {\"success\": False, \"error\": \"Introuvable\"}`",
                "good": "Utiliser le vrai code de statut HTTP correspondant : `raise HTTPException(status_code=404, detail=\"Introuvable\")`",
                "why": "Le *200 OK avec erreur cachée* aveugle totalement les tableaux de bord Prometheus/Grafana, les proxys Nginx et les clients HTTP !"
            },
            {
                "bad": "Oublier l'en-tête `Content-Type: application/json` lors d'un `POST`",
                "good": "Toujours spécifier `Content-Type: application/json` dès qu'un corps JSON est envoyé",
                "why": "Sans cet en-tête, FastAPI ne peut identifier le corps JSON et rejette la requête avec `422` ou `415 Unsupported Media Type`."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_1/04_trame_http_et_headers.py` et vérifiez par le calcul pourquoi la chaîne `'Sécurité'` (8 caractères Unicode) pèse exactement 10 octets en UTF-8 dans l'en-tête `Content-Length`.",
            "Dans le Client HTTP du laboratoire, éprouvez successivement `/api/sandbox/status-demo/429` puis `/api/sandbox/status-demo/403` afin d'observer la structure des en-têtes retournés."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.4 : MÉTHODES HTTP, IDEMPOTENCE & SÉRIALISATION JSON
    # =========================================================================
    "d1-l4": {
        "context": (
            "Sur toute liaison réseau réelle — antenne mobile 4G/5G saturée, Wi-Fi d'entreprise ou interconnexion "
            "interbancaire —, des paquets TCP sont régulièrement perdus en transit. Lorsqu'une application cliente "
            "émet une requête HTTP et subit une expiration de délai (*Timeout*) juste avant de recevoir l'accusé du "
            "serveur, une question architecturale décisive se pose : **le client peut-il rejouer automatiquement la "
            "même requête sans provoquer de corruption métier ni de double facturation ?**\n\n"
            "La propriété formelle qui gouverne cette décision s'appelle **l'Idempotence** (IETF RFC 9110, Section 9.2.2). "
            "Ce chapitre établit les garanties algébriques des cinq méthodes CRUD (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) "
            "et détaille le pipeline de sérialisation JSON haute performance de Pydantic v2 (`pydantic-core` en Rust)."
        ),
        "deep_sections": [
            {
                "heading": "1. Algèbre des méthodes HTTP (RFC 9110) : Sûreté (*Safe*) et Idempotence (*Idempotent*)",
                "body": (
                    "La spécification RFC 9110 ne définit pas les verbes HTTP comme de simples étiquettes arbitraires, "
                    "mais comme des contrats mathématiques engageant la responsabilité des proxys, navigateurs et SDK "
                    "clients en cas de défaillance réseau. Deux axiomes structurent cette classification.\n\n"
                    "> « Une méthode de requête est dite idempotente si l'effet attendu sur le serveur de multiples requêtes identiques avec cette méthode est le même que l'effet d'une unique requête de ce type. » — IETF RFC 9110 (HTTP Semantics, Section 9.2.2)\n\n"
                    "#### Conséquences concrètes pour `GET`, `PUT`, `DELETE`, `PATCH` et `POST`\n\n"
                    "Les méthodes **`GET`**, **`HEAD`** et **`OPTIONS`** sont dites **Sûres (*Safe*)** : elles sont "
                    "purement consultatives et ne modifient aucun état métier côté serveur (un simple compteur de logs "
                    "technique ne constituant pas une mutation d'état client). Toute méthode sûre est *ipso facto* "
                    "**Idempotente**.\n\n"
                    "Plus subtil : **`PUT /formations/1`** (remplacer intégralement l'état de la formation n°1 par "
                    "`{\"titre\": \"Architecture ASGI\", \"salle\": \"B\"}`) et **`DELETE /formations/1`** ne sont "
                    "évidemment **pas sûrs** puisqu'ils mutent la base SQL, mais ils sont **strictement idempotents** ! "
                    "Exécuter cinq fois le même `PUT` laisse l'enregistrement `#1` dans le même état final ; exécuter "
                    "cinq fois `DELETE /formations/1` aboutit toujours à l'absence de l'enregistrement `#1` (quand bien "
                    "même le premier appel renvoie `204 No Content` et les quatre suivants `404 Not Found` : l'idempotence "
                    "porte sur l'**état du serveur** et non sur l'identité du code de statut retourné).\n\n"
                    "À l'inverse, **`POST /formations`** n'est **ni sûr, ni idempotent** : rejouer trois fois la même "
                    "requête `POST` insère trois lignes distinctes `#1`, `#2`, `#3` ou débite trois fois une carte "
                    "bancaire, sauf si l'architecte introduit un mécanisme explicite de déduplication par `Idempotency-Key`."
                )
            },
            {
                "heading": "2. Sérialisation JSON : de `json.dumps` standard au moteur Rust `pydantic-core` de Pydantic v2",
                "body": (
                    "Un descripteur de socket réseau ne transporte que des tampons d'octets (`bytes`). Transformer un "
                    "graphe d'objets Python résidant en RAM en séquence textuelle UTF-8 s'appelle la **sérialisation** ; "
                    "l'opération inverse, qui reconstruit et valide des objets typés à partir d'octets entrants, est la "
                    "**désérialisation**.\n\n"
                    "Dans la bibliothèque standard Python, `json.dumps(obj, ensure_ascii=False)` et `json.loads(texte)` "
                    "assurent cette conversion générique sur des `dict` et `list`. Dans **FastAPI avec Pydantic v2**, "
                    "cette étape franchit un saut quantique d'ingénierie : toute la logique de parsing JSON, de contrôle "
                    "de contraintes et de sérialisation est déléguée à **`pydantic-core`**, une bibliothèque compilée "
                    "en **Rust** (basée sur `jiter`) directement reliée aux structures C de CPython.\n\n"
                    "```python — Validation et sérialisation directe en Rust avec Pydantic v2\n"
                    "# Désérialisation + validation en une seule passe Rust depuis les octets réseau :\n"
                    "enveloppe = EnveloppeReponseAPI.model_validate_json(octets_entrants)\n"
                    "\n"
                    "# Sérialisation directe en chaîne JSON UTF-8 (5x à 20x plus rapide que json.dumps) :\n"
                    "flux_json = enveloppe.model_dump_json(indent=2)\n"
                    "```\n\n"
                    "> [!TIP] Éviter le double parsing JSON grâce à `model_validate_json`\n"
                    "> Exécuter `MonModele.model_validate(json.loads(texte))` oblige Python à allouer d'abord tous les dictionnaires intermédiaires en RAM avant de les revalider. Appeler directement `MonModele.model_validate_json(texte)` (ce que FastAPI fait sur les corps de requête) parse les octets JSON et construit l'instance validée en une passe unique côté Rust !"
                )
            },
            {
                "heading": "3. Enveloppe contractuelle (`meta` + `data`) et normalisation temporelle ISO 8601 UTC",
                "body": (
                    "Concevoir un schéma de réponse durable commande de séparer systématiquement les **métadonnées "
                    "techniques d'enveloppe (`meta`)** de la **charge métier (`data`)**. L'objet `meta` centralise la "
                    "version du contrat, l'identifiant de trace `request_id`, les compteurs de pagination et l'horodatage "
                    "serveur, laissant la clé `data` accueillir l'entité ou le tableau d'entités sans jamais polluer "
                    "les attributs du domaine.\n\n"
                    "#### Pourquoi l'horodatage ISO 8601 en UTC (`Z`) est un invariant non négociable\n\n"
                    "Transmettre une date ambiguë comme `\"08/11/2026 17:30\"` provoque des bogues insolubles entre "
                    "un client américain (qui lit le 11 août), un serveur algérien (`UTC+1`, sans heure d'été) et un "
                    "partenaire européen (`UTC+1` ou `UTC+2` selon la saison). La norme **ISO 8601 / RFC 3339 en temps "
                    "universel coordonné (`2026-11-08T16:30:00Z`)**, générée en Python 3.11+ via "
                    "`datetime.now(timezone.utc)`, possède deux vertus mathématiques décisives : elle est **dépourvue "
                    "de toute ambiguïté de fuseau** grâce au suffixe `Z` (*Zulu Time*), et son ordre de tri "
                    "alphabétique ASCII coïncide exactement avec son ordre chronologique."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE SÉRIALISATION / DÉSÉRIALISATION ENTRE DEUX SYSTÈMES (PYDANTIC V2 / JSON) :\n"
            "  [Mémoire Serveur FastAPI]               [Câble Réseau HTTP]                [Mémoire Client (Python/TS)]\n"
            "   BaseModel(actif=True, fin=None)  -->  model_dump_json().encode()    -->  model_validate_json() / JSON.parse()\n"
            "                                       \"{\\\"actif\\\": true, \\\"fin\\\": null}\""
        ),
        "reference_table": {
            "title": "Matrice de Sémantique et d'Idempotence des Méthodes HTTP (RFC 9110)",
            "headers": ["Méthode HTTP", "Action CRUD", "Corps (Body) en Requête ?", "Sûre (Safe) ?", "Idempotente ?", "Réessai automatique sans risque en cas de coupure ?"],
            "rows": [
                ["**`GET`**", "Lire (Read)", "Non (Jamais)", "**Oui**", "**Oui**", "**Oui** (100% sûr)"],
                ["**`PUT`**", "Remplacer intégralement", "Oui (JSON complet)", "Non", "**Oui**", "**Oui** (Écrase avec le même état final)"],
                ["**`DELETE`**", "Supprimer (Delete)", "Non", "Non", "**Oui**", "**Oui** (L'élément reste supprimé)"],
                ["**`PATCH`**", "Modifier partiellement", "Oui (Champs modifiés)", "Non", "Selon implémentation", "Oui si affectation de valeur (`exclude_unset=True`)"],
                ["**`POST`**", "Créer / Traiter", "Oui (JSON)", "Non", "**NON !**", "**NON** (Risque de doublon sauf avec `Idempotency-Key`)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Utiliser une route `GET /api/formations/supprimer?id=1` qui modifie ou supprime des données",
                "good": "Respecter la méthode `DELETE /api/formations/1` pour toute suppression",
                "why": "Les navigateurs, extensions d'antivirus et proxys préchargent parfois les liens `GET` par anticipation : un `GET` destructeur viderait votre base par accident !"
            },
            {
                "bad": "Confondre `json.load(fichier)` (sans `s`) et `json.loads(chaine)` (avec `s` = *string*)",
                "good": "Utiliser `model_validate_json()` / `json.loads()` et `model_dump_json()` / `json.dumps()` pour les flux réseau",
                "why": "`load` et `dump` sans `s` lisent/écrivent un descripteur de fichier disque, tandis que `loads` et `dumps` opèrent sur des chaînes en RAM."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_1/02_serialisation_json.py` et vérifiez dans la trace générée par Pydantic v2 que les types Python `None` et `True` ont été projetés en `null` et `true` accompagnés d'un horodatage ISO 8601 UTC.",
            "Ajoutez un champ `modules: list[str] = [\"HTTP/1.1\", \"ASGI\", \"Pydantic v2\"]` au modèle `DonneesFormation`, sérialisez l'enveloppe avec `.model_dump_json(indent=2)` puis revalidez la chaîne avec `.model_validate_json()`."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.5 : MAÎTRISER CURL, POSTMAN, HTTPIE & REST CLIENT
    # =========================================================================
    "d1-l5": {
        "context": (
            "Comment auditer, reproduire et diagnostiquer un endpoint FastAPI qui exige un verbe `POST` ou `PATCH`, "
            "un corps JSON typé, un en-tête `Authorization: Bearer <token>` et une clé `Idempotency-Key`, alors que "
            "la barre d'adresse de Chrome ou Firefox est structurellement limitée aux seules requêtes `GET` nues ?\n\n"
            "Un ingénieur backend ne débogue jamais son réseau à l'aveugle : il instrumente ses échanges à l'aide de "
            "**clients d'inspection HTTP dédiés**. Sur un serveur Linux de production joint en SSH, dans un conteneur "
            "Kubernetes ou au sein d'un pipeline GitLab CI, **`curl`** constitue l'étalon universel ; sur le poste de "
            "travail, il s'articule avec **Postman** (ou Bruno/Insomnia), **HTTPie** et les cahiers de requêtes "
            "versionnés **`.http`** ainsi que le portail **Swagger UI (`/docs`)** intégré à FastAPI."
        ),
        "deep_sections": [
            {
                "heading": "1. Pourquoi `curl` demeure l'instrument roi de l'ingénierie de production et d'astreinte",
                "body": (
                    "Créé en 1997 par Daniel Stenberg autour de la bibliothèque C `libcurl`, **`curl` (*Client for URL*)** "
                    "est présent par défaut sur la quasi-totalité des distributions Linux, macOS, Windows 10/11 et images "
                    "Docker alpines ou Debian. Lorsqu'une anomalie survient à deux heures du matin entre un proxy inverse "
                    "Nginx et un worker Uvicorn interne non exposé sur Internet, aucune interface graphique ne peut "
                    "franchir le bastion SSH : seule une commande `curl -i` exécutée directement depuis l'hôte permet "
                    "d'interroger `http://127.0.0.1:8000/api/health/ready` et d'observer la réponse exacte à la "
                    "microseconde près.\n\n"
                    "Au-delà du diagnostic d'urgence, une commande `curl` possède une vertu d'ingénierie irremplaçable : "
                    "**elle est purement textuelle, déterministe et reproductible**. Collée dans un rapport d'incident, "
                    "une revue de code Git ou une documentation partenaire, elle permet à n'importe quel collègue de "
                    "rejouer à l'identique les octets exacts envoyés sur le fil — d'où le fait que Swagger UI (`/docs`) "
                    "dans FastAPI génère automatiquement la commande `curl` équivalente sous chaque test *Try it out*."
                )
            },
            {
                "heading": "2. Lecture forensique d'une trace `curl -v` : décoder les préfixes `*`, `>` et `<`",
                "body": (
                    "Lorsque le commutateur `-i` (qui n'affiche que les en-têtes de la réponse reçue) ne suffit pas à "
                    "comprendre pourquoi le serveur rejette un appel, le mode verbeux **`curl -v`** dévoile l'intégralité "
                    "du cycle de vie réseau en préfixant chaque ligne par l'un de trois marqueurs directionnels stricts.\n\n"
                    "```text — Autopsie complète d'un échange HTTP/1.1 capturé par curl -v\n"
                    "* Trying 127.0.0.1:8000...\n"
                    "* Connected to 127.0.0.1 (127.0.0.1) port 8000 (#0)\n"
                    "> POST /api/sandbox/auth/token HTTP/1.1\n"
                    "> Host: 127.0.0.1:8000\n"
                    "> User-Agent: curl/8.5.0\n"
                    "> Accept: application/json\n"
                    "> Content-Type: application/json\n"
                    "> Content-Length: 52\n"
                    ">\n"
                    "< HTTP/1.1 200 OK\n"
                    "< date: Wed, 11 Nov 2026 16:45:00 GMT\n"
                    "< server: uvicorn\n"
                    "< content-type: application/json\n"
                    "<\n"
                    "{\"access_token\": \"eyJ...\", \"token_type\": \"bearer\"}\n"
                    "```\n\n"
                    "Les lignes introduites par l'astérisque **`*`** journalisent les opérations internes de `libcurl` "
                    "(résolution DNS, ouverture du socket TCP vers `127.0.0.1:8000`, validation du certificat TLS). "
                    "Les lignes précédées du chevron sortant **`>`** reproduisent fidèlement les en-têtes **émis par le "
                    "client vers le serveur**, tandis que les lignes précédées du chevron entrant **`<`** exposent la "
                    "ligne de statut et les en-têtes **renvoyés par Uvicorn/FastAPI** avant le corps JSON.\n\n"
                    "> [!TIP] Le raccourci moderne `--json` depuis `curl 7.82+`\n"
                    "> Historiquement, l'option `-d '{...}'` de `curl` positionne par défaut `Content-Type: application/x-www-form-urlencoded`, provoquant une erreur `422` sur une route JSON FastAPI si l'on oublie `-H \"Content-Type: application/json\"`. Depuis `curl 7.82`, le drapeau unique `--json '{\"titre\": \"API\"}'` force simultanément `POST`, `Content-Type: application/json` et `Accept: application/json`."
                )
            },
            {
                "heading": "3. Outillage collaboratif : Collections Postman/Bruno, syntaxe `HTTPie` et fichiers `.http`",
                "body": (
                    "Au quotidien, lors du développement itératif d'une API comptant cinquante endpoints, trois familles "
                    "d'outils viennent épauler `curl` et le portail `/docs` de FastAPI. Les ateliers graphiques "
                    "**Postman**, **Bruno** et **Insomnia** organisent les requêtes en collections arborescentes munies "
                    "de variables d'environnement (`{{base_url}}`, `{{bearer_token}}`) et de scripts post-réponse "
                    "capables de capturer automatiquement le jeton renvoyé par `/auth/token` pour l'injecter dans toutes "
                    "les requêtes suivantes.\n\n"
                    "En ligne de commande interactive, **`HTTPie` (`http`)** offre une ergonomie remarquable dédiée à "
                    "JSON : taper `http POST :8000/api/formations titre=\"FastAPI\" duree_jours:=5` distingue par `=` "
                    "les chaînes et par `:=` les entiers ou booléens natifs tout en colorant syntaxiquement la réponse. "
                    "Enfin, les fichiers **`.http`** (extension *REST Client* de VS Code / Antigravity IDE) permettent "
                    "de consigner toutes les requêtes de recette séparées par `###` dans un simple fichier texte commité "
                    "dans Git, garantissant que la suite d'exemples évolue au même rythme que les branches du code Python."
                )
            }
        ],
        "architecture_diagram": (
            "LECTURE D'UNE TRACE DIAGNOSTIC 'curl -v' :\n"
            "  * Trying 127.0.0.1:8000...                  <-- [*] Connexion TCP ouverte par curl\n"
            "  * Connected to 127.0.0.1 (127.0.0.1) port 8000\n"
            "  > POST /api/sandbox/auth/token HTTP/1.1     <-- [>] En-têtes ENVOYÉS par le client\n"
            "  > Host: 127.0.0.1:8000\n"
            "  > Content-Type: application/json\n"
            "  > Content-Length: 52\n"
            "  <\n"
            "  < HTTP/1.1 200 OK                           <-- [<] En-têtes REÇUS depuis FastAPI/Uvicorn\n"
            "  < content-type: application/json\n"
            "  {\"access_token\": \"eyJ...\"}                  <-- Corps JSON de la réponse"
        ),
        "reference_table": {
            "title": "Synthèse des Commandes `curl` les Plus Utilisées au Quotidien",
            "headers": ["Objectif de test", "Commande `curl` complète", "Options clés utilisées"],
            "rows": [
                ["**Lire + voir les Headers**", "`curl -i \"http://127.0.0.1:8000/api/sandbox/formations\"`", "`-i` (inclut statut + en-têtes)"],
                ["**Créer en `POST` JSON**", "`curl -i -X POST -H \"Content-Type: application/json\" -d '{\"titre\":\"API\"}' \"http://127.0.0.1:8000/api/sandbox/formations\"`", "`-X POST`, `-H`, `-d`"],
                ["**Raccourci JSON moderne**", "`curl -i --json '{\"titre\":\"API\"}' \"http://127.0.0.1:8000/api/sandbox/formations\"`", "`--json` (`curl 7.82+`)"],
                ["**Modifier (`PUT` / `PATCH`)**", "`curl -i -X PATCH -H \"Content-Type: application/json\" -d '{\"salle\":\"B\"}' \"http://127.0.0.1:8000/api/sandbox/formations/1\"`", "`-X PATCH`"],
                ["**Supprimer (`DELETE`)**", "`curl -i -X DELETE \"http://127.0.0.1:8000/api/sandbox/formations/1\"`", "`-X DELETE`"],
                ["**Envoyer un `Bearer Token`**", "`curl -i -H \"Authorization: Bearer <TOKEN>\" \"http://127.0.0.1:8000/api/sandbox/auth/profil\"`", "`-H \"Authorization: Bearer ...\"`"],
                ["**Diagnostic complet**", "`curl -v --connect-timeout 3 -m 10 \"http://127.0.0.1:8000/api/sandbox/bonjour\"`", "`-v`, `--connect-timeout`, `-m`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écrire `curl -X POST -d '{\"titre\": \"API\"}' URL` en oubliant `-H \"Content-Type: application/json\"`",
                "good": "Toujours ajouter `-H \"Content-Type: application/json\"` (ou utiliser `--json`)",
                "why": "Par défaut, `-d` dans `curl` envoie l'en-tête `application/x-www-form-urlencoded` (formulaire HTML) et non `application/json` !"
            },
            {
                "bad": "Passer une URL contenant `&` sans guillemets dans le terminal : `curl http://localhost:8000/api?page=1&limit=2`",
                "good": "Toujours entourer l'URL de guillemets doubles : `curl \"http://localhost:8000/api?page=1&limit=2\"`",
                "why": "Dans un interpréteur Bash/Zsh, le caractère `&` hors guillemets détache la commande en arrière-plan et tronque `&limit=2` !"
            }
        ],
        "practical_exercises": [
            "Exécutez le script `day_1/05_outils_curl_postman_httpie.py` ci-dessus afin d'inspecter sur les quatre scénarios la correspondance entre options `curl -i` et traitement côté FastAPI (`Query`, `Header`, `BaseModel`, `Form`).",
            "Ouvrez l'onglet **curl & Postman** dans la barre supérieure et lancez le scénario de chronométrage détaillé (`-w`) pour observer le temps `TTFB`.",
            "Téléchargez la Collection Postman (`.json`) et le cahier `.http` depuis l'onglet **curl & Postman** afin d'inspecter leur structure JSON et texte."
        ]
    }
}
