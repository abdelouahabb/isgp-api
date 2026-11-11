"""
Manuel de Référence Approfondi — Enrichissement des Chapitres (Jours 0 et 1).
Volume I — Architecture & Ingénierie des APIs Web avec Python, Flask et WSGI.

Fournit pour chaque chapitre :
- context : exposé complet de la problématique d'ingénierie en prose éditoriale
- deep_sections : sous-chapitres de référence (fondements théoriques, mécanique mémoire/réseau et production)
- architecture_diagram : schéma ASCII de flux mémoire ou réseau
- reference_table : tableau de synthèse technique
- pitfalls : anti-patterns de production vs standards industriels
- practical_exercises : travaux pratiques progressifs de révision post-bootcamp
"""

ENRICHMENT_D0_D1 = {
    # =========================================================================
    # JOUR 0 — CHAPITRE 0.1 : VARIABLES, MÉMOIRE & TYPES PRIMITIFS
    # =========================================================================
    "d0-l1": {
        "context": (
            "Avant même d'ouvrir une prise réseau (socket TCP) ou d'écrire une route HTTP, tout service backend "
            "est d'abord un processus système qui alloue, inspecte et transforme des structures d'octets en mémoire "
            "vive (RAM). Qu'il s'agisse du montant hors taxes d'un marché public, de l'identifiant d'un stagiaire, "
            "du statut booléen d'une inscription ou de l'absence explicite d'une date de clôture, chaque donnée "
            "possède une représentation physique et sémantique stricte au sein de l'interpréteur CPython.\n\n"
            "Dans une architecture orientée API, la moindre confusion sur la nature d'une valeur franchit immédiatement "
            "la frontière du serveur pour contaminer l'ensemble du système d'information. Renvoyer la chaîne de caractères "
            "`\"500\"` au lieu de l'entier `500`, ou substituer une chaîne vide `\"\"` au marqueur d'absence `None`, "
            "suffit à provoquer des erreurs d'exécution fatales dans une application mobile Kotlin/Swift, des concaténations "
            "arithmétiques aberrantes dans un frontal JavaScript ou le rejet d'un lot comptable par un partenaire bancaire. "
            "Ce chapitre inaugural pose les bases rigoureuses du modèle objet de Python et de sa projection directe vers "
            "la grammaire universelle d'échange JSON."
        ),
        "deep_sections": [
            {
                "heading": "1. Modèle mémoire de CPython : Objets sur le tas (Heap), Références et Typage Dynamique Fort",
                "body": (
                    "Contrairement aux langages compilés proches du matériel comme C ou Rust, où une variable désigne "
                    "directement une boîte mémoire de taille fixe attachée à un type déclaré statiquement, Python repose "
                    "sur un **modèle intégralement orienté objet fondé sur des références**. Lorsque l'interpréteur CPython "
                    "exécute l'instruction `duree_jours = 5`, le symbole `=` ne traduit aucune égalité algébrique : il "
                    "orchestre une séquence d'allocation puis de liaison de nom dans l'espace des noms courant.\n\n"
                    "#### Mécanique interne d'une affectation en mémoire vive\n\n"
                    "CPython commence toujours par évaluer intégralement l'expression située **à droite** de l'opérateur `=`. "
                    "Il alloue sur le tas mémoire (*heap*) une structure C interne baptisée `PyObject`, qui embarque trois "
                    "informations indissociables : un compteur de références (`ob_refcnt`) destiné au ramasse-miettes "
                    "(*garbage collector*), un pointeur vers le descripteur de son type (`ob_type`, ici `<class 'int'>`), "
                    "et la valeur utile (`5`). Ce n'est qu'une fois cet objet matérialisé en RAM que Python inscrit le nom "
                    "`duree_jours` dans le dictionnaire de la portée locale et fait pointer cette étiquette vers l'adresse "
                    "mémoire du `PyObject` fraîchement créé.\n\n"
                    "```python — Inspection de l'identité mémoire et du type attaché à l'objet\n"
                    "duree_jours = 5\n"
                    "print(id(duree_jours), type(duree_jours))  # Adresse en RAM + <class 'int'>\n"
                    "\n"
                    "# Réaffecter la variable déplace l'étiquette vers un NOUVEL objet immuable :\n"
                    "duree_jours = duree_jours + 2\n"
                    "print(id(duree_jours), duree_jours)        # Nouvelle adresse en RAM, valeur 7\n"
                    "```\n\n"
                    "Cette architecture explique pourquoi le typage de Python est qualifié simultanément de **dynamique** "
                    "et de **fort**. Il est dynamique parce que le type appartient à l'objet en mémoire et jamais à "
                    "l'étiquette : rien n'interdit à une même variable de désigner successivement un entier puis une chaîne, "
                    "bien que la lisibilité industrielle commande d'éviter cette pratique. Mais il est **fort** parce que "
                    "l'interpréteur refuse catégoriquement toute coercition implicite hasardeuse entre types incompatibles.\n\n"
                    "> [!IMPORTANT] Typage fort face aux entrées réseau non fiables\n"
                    "> En Python, l'expression `\"500\" + 25` lève immédiatement une exception `TypeError: can only concatenate str (not \"int\") to str`, là où JavaScript produirait silencieusement la chaîne `\"50025\"`. Ce refus strict constitue votre premier rempart contre la corruption silencieuse des calculs financiers ou statistiques dans un serveur Flask."
                )
            },
            {
                "heading": "2. Du modèle objet Python au contrat réseau JSON (Norme IETF RFC 8259)",
                "body": (
                    "Lorsqu'une API Web publie une information sur le réseau, les structures internes `PyObject` de la RAM "
                    "ne peuvent évidemment pas traverser une carte Ethernet. Elles doivent être projetées dans un format "
                    "textuel interopérable compris aussi bien par un microservice Go, un navigateur Web qu'un terminal de "
                    "paiement : le standard **JSON (*JavaScript Object Notation*)**, normalisé par l'IETF sous la référence "
                    "**RFC 8259**.\n\n"
                    "> « JSON est un format textuel d'échange de données structurées, totalement indépendant des langages de programmation, fondé sur un sous-ensemble restreint de primitives universelles. » — IETF RFC 8259, Section 1\n\n"
                    "#### Correspondance stricte des quatre types scalaires\n\n"
                    "La grammaire RFC 8259 ne reconnaît que quatre types scalaires élémentaires, auxquels s'ajoutent deux "
                    "conteneurs composés (l'objet `{...}` et le tableau `[...]`). En Python, le type `str` (séquence immuable "
                    "de points de code Unicode UTF-8) se traduit en `string` JSON obligatoirement délimitée par des guillemets "
                    "doubles `\"...\"`. Les types numériques `int` (entiers à précision arbitraire en Python) et `float` "
                    "(nombres à virgule flottante double précision IEEE 754 sur 64 bits) convergent tous deux vers le type "
                    "unique `number` de JSON. Le type logique `bool` (`True` et `False` avec majuscule initiale en Python) "
                    "devient `boolean` en minuscules (`true` et `false`), tandis que le singleton `None` (unique instance de "
                    "`NoneType`) se traduit par le littéral `null`.\n\n"
                    "```json — Représentation normalisée RFC 8259 sur le fil réseau\n"
                    "{\n"
                    "  \"organisme\": \"ISGP\",\n"
                    "  \"duree_jours\": 5,\n"
                    "  \"taux_reussite\": 98.5,\n"
                    "  \"est_ouverte\": true,\n"
                    "  \"prerequis\": null\n"
                    "}\n"
                    "```\n\n"
                    "> [!WARNING] Précision flottante IEEE 754 et calculs monétaires\n"
                    "> Les nombres `float` étant codés en base 2 selon la norme IEEE 754, l'addition `0.1 + 0.2` produit en mémoire `0.30000000000000004`. Pour la facturation ou la comptabilité dans une API professionnelle, on privilégie donc soit le stockage des montants en **centimes entiers (`int`)**, soit le module standard `decimal.Decimal` sérialisé de manière contrôlée."
                )
            },
            {
                "heading": "3. Inspection défensive et subtilités d'héritage avec `isinstance()`",
                "body": (
                    "Dès qu'un serveur Flask s'ouvre aux requêtes `POST` ou `PUT` provenant d'Internet, il doit considérer "
                    "que le client peut violer la documentation à tout instant : envoyer `{\"duree_jours\": \"cinq\"}` au "
                    "lieu de l'entier `5`, ou transmettre `{\"duree_jours\": true}` par erreur de sérialisation côté frontal. "
                    "Pour valider rigoureusement le type d'une valeur reçue après désérialisation JSON, les ingénieurs Python "
                    "préfèrent systématiquement l'appel `isinstance(valeur, type_attendu)` à la comparaison fragile `type(valeur) == int`.\n\n"
                    "#### Le piège historique de `bool` sous-classe de `int`\n\n"
                    "Une particularité célèbre du langage Python, héritée de Python 2.3 pour préserver la rétrocompatibilité "
                    "des opérations logiques, réside dans le fait que la classe `bool` hérite directement de la classe `int` : "
                    "en interne, `True` vaut numériquement `1` et `False` vaut `0`. Par conséquent, l'expression "
                    "`isinstance(True, int)` renvoie `True` ! Si votre validateur d'API se contente de tester "
                    "`if isinstance(duree, int):`, un client malveillant ou bogué envoyant `{\"duree_jours\": true}` "
                    "franchira le contrôle de validation sans encombre.\n\n"
                    "```python — Validation stricte d'un entier JSON excluant les booléens\n"
                    "def est_entier_strict(valeur) -> bool:\n"
                    "    return isinstance(valeur, int) and not isinstance(valeur, bool)\n"
                    "\n"
                    "print(est_entier_strict(5))     # True  -> Entier légitime\n"
                    "print(est_entier_strict(True))  # False -> Booléen démasqué et rejeté\n"
                    "```\n\n"
                    "> [!TIP] Paramètres d'URL et conversion explicite\n"
                    "> Gardez toujours à l'esprit une asymétrie fondamentale entre le corps JSON et l'URL : un corps JSON possède ses types primitifs (`5`, `true`, `null`), tandis que tout paramètre extrait d'une URL (`?page=2&actif=true`) arrive initialement sous forme de chaîne `str` brute (`\"2\"`, `\"true\"`) qu'il vous appartient de convertir et valider explicitement."
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
            "Dans l'exécuteur interactif ci-dessus, déclarez une variable `prix_ht = 1500.50` (`float`) et un drapeau `exonere_tva = False` (`bool`), puis inspectez leur classe exacte et leur identifiant mémoire avec `type()` et `id()`.",
            "Comparez le comportement de l'opérateur `+` entre `100 + 50` et `\"100\" + \"50\"`, puis vérifiez l'exception levée lorsque vous tentez d'évaluer `\"100\" + 50` sans conversion explicite.",
            "Écrivez une fonction prédicat `valider_duree(val)` qui accepte un entier strictement positif tout en rejetant explicitement le booléen `True` malgré l'héritage `issubclass(bool, int)`."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.2 : LISTES, DICTIONNAIRES & STRUCTURES IMBRIQUÉES
    # =========================================================================
    "d0-l2": {
        "context": (
            "Une API professionnelle ne transporte pratiquement jamais un scalaire isolé : elle expose des **agrégats "
            "métier hiérarchisés**, tels qu'une session de formation rattachée à son intervenant, sa salle d'affectation, "
            "ses métadonnées de pagination et la collection ordonnée des participants inscrits.\n\n"
            "En Python, l'intégralité de cette modélisation repose sur la combinaison symbiotique de deux structures de "
            "données natives de la bibliothèque standard : le **dictionnaire (`dict`)**, qui associe des attributs nommés "
            "à leurs valeurs en temps constant, et la **liste (`list`)**, qui maintient une séquence indexée d'éléments. "
            "Parce que ces deux conteneurs correspondent trait pour trait à l'objet `{...}` et au tableau `[...]` de la "
            "norme JSON, maîtriser leur mécanique mémoire et leur parcours défensif représente plus des deux tiers du "
            "code métier écrit au sein d'un contrôleur Flask."
        ),
        "deep_sections": [
            {
                "heading": "1. Architecture interne du dictionnaire Python (`dict`) : Table de hachage et complexité `O(1)`",
                "body": (
                    "Sous son apparente simplicité syntaxique `{ \"cle\": valeur }`, le type `dict` de CPython est l'une "
                    "des tables de hachage (*hash tables* compactes à adressage ouvert) les plus optimisées de l'industrie "
                    "logicielle. Depuis Python 3.7, le dictionnaire garantit en outre par spécification officielle la "
                    "**préservation de l'ordre d'insertion des clés**, ce qui assure une sérialisation JSON déterministe et "
                    "prévisible d'un appel à l'autre.\n\n"
                    "#### Fonctionnement de la résolution de clé par hachage\n\n"
                    "Lorsque vous évaluez `formation[\"titre\"]`, Python ne parcourt jamais les clés une par une comme il le "
                    "ferait dans une liste. Il calcule instantanément l'empreinte numérique `hash(\"titre\")`, en déduit "
                    "l'indice exact du compartiment (*bucket*) en mémoire vive et restitue le pointeur vers la valeur en "
                    "**temps constant amorti `O(1)`**. Que votre dictionnaire compte quatre attributs ou un million d'entrées "
                    "en cache mémoire, le temps d'accès demeure de l'ordre de quelques dizaines de nanosecondes.\n\n"
                    "Cette mécanique implique deux règles structurelles directes pour vos APIs : chaque clé d'un même "
                    "dictionnaire est **strictement unique** (définir deux fois `\"salle\"` écrase silencieusement la première "
                    "occurrence), et dans tout dictionnaire destiné à une réponse REST, les clés doivent être des chaînes "
                    "normalisées en `snake_case` (`\"duree_jours\"`, `\"date_ouverture\"`) afin de garantir une convention "
                    "uniforme sur l'ensemble du contrat d'interface."
                )
            },
            {
                "heading": "2. Lecture défensive des charges utiles : `d[cle]` face à `d.get(cle, defaut)`",
                "body": (
                    "La source numéro un d'erreurs `500 Internal Server Error` dans les APIs Flask débutantes réside dans "
                    "l'accès direct par crochets sur des données fournies par un client externe. Lorsqu'une requête `POST` "
                    "ou `PATCH` transmet un corps JSON désérialisé dans la variable `corps`, rien ne garantit que "
                    "l'appelant a renseigné tous les attributs optionnels — ni même les attributs obligatoires.\n\n"
                    "```python — Contraste entre accès cassant et lecture défensive\n"
                    "corps_client = {\"titre\": \"Architecture REST\"}  # Champ 'salle' absent du JSON\n"
                    "\n"
                    "# Approche fragile : lève KeyError: 'salle' -> Crash HTTP 500 !\n"
                    "# salle = corps_client[\"salle\"]\n"
                    "\n"
                    "# Approche défensive : renvoie la valeur de repli sans exception\n"
                    "salle = corps_client.get(\"salle\", \"Salle non attribuée\")\n"
                    "```\n\n"
                    "Lorsque l'interpréteur rencontre `corps_client[\"salle\"]` sur une clé absente, il lève immédiatement "
                    "une exception non gérée `KeyError` qui interrompt brutalement le traitement de la requête. À l'inverse, "
                    "la méthode `corps_client.get(\"salle\", \"Salle non attribuée\")` interroge la table de hachage en "
                    "toute sécurité : si la clé est présente, sa valeur est retournée ; si elle est absente, Python renvoie "
                    "proprement le second argument (ou `None` si aucun défaut n'est précisé).\n\n"
                    "> [!WARNING] Subtilité lorsque la clé existe mais vaut explicitement `null` en JSON\n"
                    "> Si le client envoie explicitement `{\"salle\": null}` dans son JSON, la clé `\"salle\"` **existe** bien dans le dictionnaire avec la valeur `None` ! Dès lors, `corps.get(\"salle\", \"Salle A\")` renverra `None` et non `\"Salle A\"`. Pour couvrir à la fois l'absence de clé et la valeur `null`, utilisez l'idiome idiomatique : `salle = corps.get(\"salle\") or \"Salle A\"`."
                )
            },
            {
                "heading": "3. Tableaux dynamiques (`list`) et patron universel « Liste de Dictionnaires »",
                "body": (
                    "En mémoire CPython, une liste (`list`) n'est pas une liste chaînée lente, mais un **tableau dynamique "
                    "contigu de pointeurs** (`PyObject**`). L'accès par indice (`formations[0]` pour le premier élément, "
                    "`formations[-1]` pour le dernier) s'effectue par simple arithmétique d'adresses en temps constant `O(1)`, "
                    "tandis que l'ajout en fin de séquence via `.append(element)` bénéficie d'une pré-allocation géométrique "
                    "qui maintient un coût amorti quasi instantané.\n\n"
                    "#### Isomorphisme entre tables relationnelles SQL et collections JSON\n\n"
                    "Dans toute architecture Web adossée à une base de données relationnelle (SQLite, PostgreSQL, MySQL), "
                    "le résultat d'une requête `SELECT id, titre, duree_jours FROM formations` se matérialise côté Python "
                    "sous la forme canonique d'une **liste de dictionnaires**. La liste externe préserve l'ordre exact "
                    "imposé par la clause `ORDER BY`, tandis que chaque dictionnaire interne représente un enregistrement "
                    "autonome dont les clés reprennent les noms des colonnes SQL.\n\n"
                    "```python — Filtrage déclaratif et découpage de page (Slicing)\n"
                    "formations_longues = [f for f in formations if f.get(\"duree_jours\", 0) >= 4]\n"
                    "page_courante = formations_longues[offset : offset + limit]\n"
                    "```\n\n"
                    "> [!TIP] Le découpage par tranche (`slicing`) ne lève jamais `IndexError`\n"
                    "> Alors que `formations[50]` provoque un crash `IndexError` si la liste ne contient que 3 éléments, l'opérateur de tranche `formations[50:60]` renvoie gracieusement une liste vide `[]`. Cette propriété rend le *slicing* Python naturellement robuste pour paginer des collections en mémoire."
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
            "Dans l'exécuteur Python ci-dessus, enrichissez la collection de stagiaires avec un quatrième dictionnaire via `.append()` incluant un booléen `\"certifie\": True`, puis affichez la cardinalité totale avec `len()`.",
            "Rédigez une compréhension de liste qui extrait uniquement les stagiaires rattachés au service `\"Sécurité\"` ou `\"Réseau\"`, puis comparez sa concision avec une boucle `for` impérative.",
            "Expérimentez la différence de comportement entre `stagiaires[0].get(\"telephone\", \"Non renseigné\")` lorsque la clé est absente et lorsque la clé vaut explicitement `None`."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.3 : FONCTIONS, PARAMÈTRES, RETURN & TUPLES FLASK
    # =========================================================================
    "d0-l3": {
        "context": (
            "Au sein du framework Flask, **chaque point de terminaison (endpoint) HTTP est matérialisé par une "
            "fonction Python ordinaire** — appelée *View Function* dans la terminologie WSGI. Lorsqu'une requête "
            "`GET /api/v1/formations` franchit le socket réseau, le routeur invoque la fonction associée et utilise "
            "exclusivement l'objet restitué par l'instruction **`return`** pour forger la réponse HTTP renvoyée au client.\n\n"
            "Chez les ingénieurs qui découvrent le développement backend après avoir pratiqué des scripts d'analyse "
            "en ligne de commande, la confusion entre `print()` (écriture locale sur le descripteur système `stdout` "
            "du serveur) et `return` (transfert mémoire du résultat à l'appelant) constitue un obstacle récurrent. "
            "Ce chapitre dissèque le cadre d'exécution d'une fonction (*stack frame*), les valeurs par défaut, le "
            "patron des clauses de garde (*Early Return*) et le décompactage des tuples `(corps, statut_http)` propre à Flask."
        ),
        "deep_sections": [
            {
                "heading": "1. Cadre de pile (Stack Frame), Portée Locale et Sémantique de `return`",
                "body": (
                    "Déclarer une fonction avec le mot-clé `def calculer_facture(montant_ht, taux_tva=0.19):` compile un "
                    "objet code réutilisable dont les paramètres dotés d'une valeur par défaut (`taux_tva=0.19`) deviennent "
                    "facultatifs lors de l'invocation. À chaque appel effectif de cette fonction, la machine virtuelle "
                    "Python alloue un **cadre d'exécution isolé sur la pile d'appels (*Call Stack Frame*)**.\n\n"
                    "#### Isolation mémoire des requêtes concurrentes\n\n"
                    "Toutes les variables créées à l'intérieur du bloc indenté (`tva`, `montant_ttc`, `reponse`) résident "
                    "exclusivement dans cet espace local éphémère. Dès que l'instruction `return` est atteinte — ou que la "
                    "fin du bloc est franchie — le cadre de pile est détruit et ses variables locales deviennent éligibles "
                    "à la libération mémoire. Sur un serveur Web multi-threads traitant simultanément cinquante requêtes "
                    "clientes, cette isolation garantit que le calcul fiscal du client A n'écrase jamais les variables "
                    "locales du client B.\n\n"
                    "> [!WARNING] Oublier `return` équivaut à retourner `None`\n"
                    "> Toute fonction Python qui s'achève sans rencontrer d'instruction `return` explicite restitue implicitement l'objet singleton `None`. Si une route Flask se termine par `print(resultat)` sans `return`, le moteur WSGI reçoit `None` et déclenche immédiatement une erreur `500 Internal Server Error` accompagnée du diagnostic : `TypeError: The view function did not return a valid response`."
                )
            },
            {
                "heading": "2. Le patron architectural « Guard Clauses & Early Return » dans les contrôleurs d'API",
                "body": (
                    "Parce que l'instruction `return` interrompt à la microseconde même l'exécution de la fonction englobante, "
                    "les architectes backend l'utilisent systématiquement pour aplatir la structure logique de leurs routes. "
                    "Au lieu d'empiler quatre ou cinq niveaux de blocs `if / else` imbriqués (l'anti-pattern dit du *Code "
                    "Flèche* ou *Arrow Anti-Pattern*), on place en tête de fonction une série de **clauses de garde (*Guard "
                    "Clauses*)** qui rejettent immédiatement les cas invalides.\n\n"
                    "```python — Contrôleur API structuré par sorties anticipées (Early Return)\n"
                    "def creer_session(jeton_client, titre, duree_jours):\n"
                    "    if not jeton_client:\n"
                    "        return {\"erreur\": \"Authentification requise\"}, 401\n"
                    "    if not titre or len(titre.strip()) < 3:\n"
                    "        return {\"erreur\": \"Intitulé trop court\"}, 422\n"
                    "    if not (1 <= duree_jours <= 30):\n"
                    "        return {\"erreur\": \"Durée hors bornes [1..30]\"}, 422\n"
                    "\n"
                    "    # Chemin nominal (Happy Path) aligné sans indentation parasite :\n"
                    "    return {\"titre\": titre.strip(), \"duree_jours\": duree_jours}, 201\n"
                    "```\n\n"
                    "Cette organisation linéaire offre une lisibilité d'audit remarquable : le lecteur vérifie d'un seul "
                    "coup d'œil toutes les préconditions de sécurité et de validation en haut de la fonction, puis lit le "
                    "traitement métier nominal (*Happy Path*) au premier niveau d'indentation, avec la certitude mathématique "
                    "que toutes les données manipulées en aval sont saines."
                )
            },
            {
                "heading": "3. Retours composites par Tuples immuables `(corps, code_http, en_tetes)`",
                "body": (
                    "Une réponse HTTP complète ne se résume pas à un corps JSON : elle doit impérativement fixer un code "
                    "de statut numérique précis (`200`, `201`, `400`, `404`, `422`) et parfois injecter des en-têtes "
                    "additionnels tels que `Location` ou `Retry-After`. Or, en Python, une instruction `return` ne renvoie "
                    "toujours qu'une seule référence d'objet.\n\n"
                    "L'élégance syntaxique de Python consiste à construire automatiquement un **tuple immuable** dès que "
                    "plusieurs expressions sont séparées par des virgules : écrire `return jsonify(payload), 201` retourne "
                    "en réalité l'objet unique `(Response, 201)` de type `<class 'tuple'>`. Le cœur de Flask inspecte la "
                    "valeur reçue de votre fonction et décompacte nativement trois signatures normalisées : `(response, status)`, "
                    "`(response, headers)` ou le triplet complet `(response, status, headers)`.\n\n"
                    "> [!IMPORTANT] Interdiction absolue des valeurs par défaut mutables (`def f(items=[])`)\n"
                    "> En Python, les expressions de valeurs par défaut dans la signature `def` sont évaluées **une seule fois au moment du chargement du module**, et non à chaque appel ! Écrire `def ajouter_erreur(msg, liste=[]):` crée une unique liste partagée en mémoire entre toutes les requêtes HTTP successives de tous vos clients. Utilisez toujours le marqueur immuable `None` : `def ajouter_erreur(msg, liste=None): liste = [] if liste is None else liste`."
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
            "Dans l'exécuteur ci-dessus, invoquez `construire_reponse_api(\"\", 3)` et vérifiez que la première clause de garde court-circuite immédiatement le reste de la fonction avec le code `400`.",
            "Enrichissez `construire_reponse_api` d'une seconde clause de garde renvoyant un tuple `(dictionnaire_erreur, 422)` dès que `duree_jours` excède `30` jours.",
            "Décompactez l'appel nominal dans deux variables distinctes via `corps, statut = construire_reponse_api(\"Docker & Linux\", 4)` et inspectez `type(construire_reponse_api(\"Docker\", 4))`."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.4 : EXCEPTIONS (TRY/EXCEPT) & DÉCORATEURS (@)
    # =========================================================================
    "d0-l4": {
        "context": (
            "Quiconque ouvre le code source d'une API industrielle écrite avec Flask ou FastAPI observe immédiatement "
            "deux idiomes omniprésents : les blocs d'interception **`try / except`** et les annotations précédées du "
            "symbole arobase **`@`** telles que `@app.route(\"/api/v1/formations\")` ou `@exiger_role(\"admin\")`.\n\n"
            "Beaucoup de supports d'initiation présentent les décorateurs `@` comme des incantations magiques à recopier "
            "sans chercher à les comprendre. En ingénierie logicielle, aucune brique critique de routage ou d'authentification "
            "ne doit demeurer une boîte noire. Ce chapitre démonte pièce par pièce le mécanisme de remontée des exceptions "
            "sur la pile d'appels ainsi que les fermetures lexicales (*closures*) qui animent chaque décorateur Python."
        ),
        "deep_sections": [
            {
                "heading": "1. Propagation des Exceptions et résilience continue d'un démon réseau",
                "body": (
                    "Dans un script exécuté ponctuellement sur le poste d'un analyste, une opération illégale telle que "
                    "`int(\"abc\")` ou l'ouverture d'un fichier introuvable interrompt le processus en affichant une trace "
                    "d'exécution (*Traceback*). Sur un serveur d'API desservant plusieurs centaines d'utilisateurs simultanés, "
                    "une telle défaillance non maîtrisée entraîne deux conséquences graves : la requête échoue brutalement "
                    "en `500 Internal Server Error`, et si le serveur est mal configuré, le message d'erreur risque de "
                    "divulguer des chemins système ou des fragments de requêtes SQL à un attaquant.\n\n"
                    "#### Interception chirurgicale par classe d'exception\n\n"
                    "Lorsqu'une anomalie survient dans un bloc `try:`, la machine virtuelle suspend immédiatement la ligne "
                    "fautive et remonte la pile d'appels à la recherche d'une clause `except` compatible avec la classe de "
                    "l'exception levée (`ValueError`, `KeyError`, `sqlite3.IntegrityError`). Cibler précisément la classe "
                    "attendue — plutôt que d'écrire un `except Exception:` aveugle — permet de traduire fidèlement chaque "
                    "incident technique en son équivalent sémantique HTTP : une erreur `ValueError` lors du décodage d'un "
                    "paramètre client devient un `400 Bad Request`, tandis qu'une violation d'unicité `IntegrityError` "
                    "devient un `409 Conflict`."
                )
            },
            {
                "heading": "2. Démystifier les Décorateurs `@` : Fonctions de première classe et Fermetures (Closures)",
                "body": (
                    "En Python, **les fonctions sont des citoyens de première classe (*first-class objects*)** : au même "
                    "titre qu'un entier ou un dictionnaire, une fonction peut être stockée dans une variable, passée en "
                    "argument à une autre fonction, ou fabriquée dynamiquement puis retournée par une fonction englobante.\n\n"
                    "Un **décorateur** n'est rien d'autre qu'un sucre syntaxique élégant (introduit par la PEP 318) pour "
                    "une fonction d'ordre supérieur qui prend une fonction `cible` en entrée et retourne une fonction "
                    "`enveloppe` enrichie. Poser `@journaliser_appel` au-dessus de `def traiter_paiement(montant):` demande "
                    "exactement à l'interpréteur d'exécuter, dès le chargement du fichier, la réaffectation suivante :\n\n"
                    "```python — Équivalence stricte du sucre syntaxique @decorateur\n"
                    "# Syntaxe déclarative avec @ :\n"
                    "@journaliser_appel\n"
                    "def traiter_paiement(montant):\n"
                    "    return {\"montant\": montant, \"statut\": \"valide\"}\n"
                    "\n"
                    "# Ce que Python exécute réellement en coulisses :\n"
                    "traiter_paiement = journaliser_appel(traiter_paiement)\n"
                    "```\n\n"
                    "Ce mécanisme fonde toute l'architecture transversale de Flask : `@app.route(\"/api/...\")` inspecte "
                    "votre fonction et l'inscrit dans la table de routage `app.url_map`, tandis qu'un décorateur de sécurité "
                    "`@exiger_role(\"admin\")` intercepte l'appel entrant, vérifie la signature cryptographique du jeton "
                    "`Bearer` et court-circuite immédiatement l'exécution avec un code `401` ou `403` sans même invoquer "
                    "votre fonction métier si les droits font défaut."
                )
            },
            {
                "heading": "3. Signature universelle `(*args, **kwargs)` et préservation des métadonnées via `@wraps`",
                "body": (
                    "Pour qu'un même décorateur d'audit ou d'authentification puisse habiller indifféremment une route sans "
                    "argument (`def lister():`) et une route dynamique (`def modifier(formation_id, mode=\"complet\"):`), "
                    "sa fonction interne `enveloppe` adopte la signature variadique universelle `def enveloppe(*args, **kwargs):`. "
                    "L'opérateur `*args` regroupe tous les arguments positionnels dans un tuple, et `**kwargs` rassemble "
                    "tous les arguments nommés dans un dictionnaire avant de les retransmettre intacts à `fonction_cible(*args, **kwargs)`.\n\n"
                    "> [!IMPORTANT] Pourquoi `@functools.wraps(fonction_cible)` est obligatoire dans Flask\n"
                    "> Lorsqu'un décorateur remplace `lister_formations` et `creer_formation` par sa propre fonction interne `enveloppe`, l'attribut d'introspection `__name__` des deux fonctions devient identique : `\"enveloppe\"`. Or, Flask utilise `fonction.__name__` comme identifiant unique d'endpoint dans sa table de routage ! Sans `@wraps(fonction_cible)` (importé depuis le module standard `functools`) pour recopier le nom et la docstring d'origine sur l'enveloppe, Flask lève au démarrage dès la seconde route décorée : `AssertionError: View function mapping is overwriting an existing endpoint function: enveloppe`."
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
            "Dans l'exécuteur ci-dessus, appelez `convertir_parametre_entier(\"-5\")` et renforcez la fonction pour qu'elle lève ou traite explicitement tout entier inférieur ou égal à zéro avec un message d'erreur adapté.",
            "Écrivez un décorateur `@verifier_montant_positif` muni de `@wraps` qui inspecte le premier argument positionnel et court-circuite l'appel en renvoyant `{\"erreur\": \"Montant strictement positif requis\"}, 422` si la valeur est négative ou nulle.",
            "Empilez `@journaliser_appel` au-dessus de `@verifier_montant_positif` sur une même fonction et observez l'ordre exact d'entrée et de sortie des deux enveloppes."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.1 : HTML VS SOAP/XML VS REST/JSON
    # =========================================================================
    "d1-l1": {
        "context": (
            "Pourquoi l'architecture des systèmes d'information contemporains — banques centrales, opérateurs "
            "télécoms, plateformes ministérielles, hôpitaux et géants du Cloud — s'articule-t-elle intégralement "
            "autour d'**APIs découplées** plutôt que d'applications Web monolithiques traditionnelles ?\n\n"
            "Dans un serveur Web de première génération, la requête SQL métier et l'habillage graphique (tableaux "
            "HTML, feuilles de style CSS, mise en page visuelle) étaient intimement fusionnés au sein de la même "
            "réponse serveur. Ce couplage fort devient intenable dès lors que la même donnée métier doit irriguer "
            "simultanément un portail navigateur React/Vue, une application native iOS/Android, un automate bancaire "
            "et le progiciel comptable d'une institution partenaire. Ce chapitre retrace la généalogie industrielle "
            "des services Web — du monolithe HTML à SOAP/XML, puis de REST/JSON jusqu'à GraphQL et gRPC — pour "
            "établir sur des critères d'ingénierie objectifs les raisons de l'hégémonie du couple HTTP/JSON."
        ),
        "deep_sections": [
            {
                "heading": "1. Du couplage présentationnel (Monolithe HTML) au contrat de données pur (API-First)",
                "body": (
                    "Lorsqu'un serveur Web classique interroge sa base relationnelle et incorpore directement les valeurs "
                    "dans un flux `<html><body><div class=\"carte-meteo\">24 °C</div></body></html>`, il destine sa "
                    "réponse exclusivement au moteur de rendu graphique d'un navigateur piloté par un être humain. Si une "
                    "application mobile native Swift ou le serveur Python d'un partenaire tente d'exploiter cette page, "
                    "il est réduit à pratiquer du *Web Scraping* : analyser péniblement des balises visuelles qui peuvent "
                    "changer du jour au lendemain lors d'une simple refonte esthétique du site.\n\n"
                    "L'architecture **centrée API (*API-First*)** opère une séparation chirurgicale des responsabilités. "
                    "Le serveur backend renonce à toute opinion graphique pour devenir une **source de vérité métier pure** "
                    "qui n'émet que des structures de données normalisées et versionnées. Dès lors, le portail Web interne "
                    "n'est plus privilégié : il devient un simple consommateur parmi d'autres au même titre que l'application "
                    "mobile ou les systèmes partenaires, tous reliés au même contrat JSON stable et gouverné."
                )
            },
            {
                "heading": "2. Généalogie des Services Web : L'ère SOAP/WSDL face à la révolution REST de Roy Fielding",
                "body": (
                    "À la charnière des années 1998–2002, la première tentative d'industrialisation des échanges "
                    "machine-à-machine a donné naissance au protocole **SOAP (*Simple Object Access Protocol*)** et à son "
                    "langage de contrat **WSDL (*Web Services Description Language*)**. Inspiré de l'appel de procédures "
                    "distantes (RPC / CORBA), SOAP enferme chaque appel dans une enveloppe XML rigide avec espaces de noms "
                    "(`xmlns:soap`), en reléguant HTTP au rang de simple tuyau de transport opaque : la quasi-totalité des "
                    "opérations — y compris de simples lectures — transitent par `POST` sur un unique point d'entrée, en "
                    "ignorant les codes de statut et le cache HTTP.\n\n"
                    "> « REST est un style architectural pensé pour les systèmes hypermédias distribués à l'échelle d'Internet : au lieu de dissimuler une couche RPC derrière un tunnel, il aligne le modèle applicatif sur la sémantique native du protocole HTTP. » — Roy Thomas Fielding, Thèse de doctorat (UC Irvine, 2000), Chapitre 5\n\n"
                    "#### Surcharge réseau et coût CPU comparés sur le fil\n\n"
                    "En 2000, Roy Fielding — l'un des principaux auteurs de la spécification HTTP/1.1 — démontre dans sa "
                    "thèse fondatrice qu'Internet possède déjà toute la machinerie nécessaire : les **URI** pour nommer les "
                    "ressources, les **verbes HTTP** (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) pour qualifier l'intention, "
                    "les **codes de statut** pour exprimer l'issue et les **en-têtes** pour gouverner la sécurité et le cache. "
                    "Associé à **JSON**, REST divise par trois à cinq la taille des charges utiles sur le réseau et élimine "
                    "la surcharge mémoire et CPU des parseurs DOM XML (ainsi que la surface d'attaque liée aux entités "
                    "externes XML ou failles *XXE*).\n\n"
                    "```xml — Enveloppe SOAP 1.1 verbeuse vs Charge utile REST/JSON équivalente\n"
                    "<!-- SOAP/XML : ~260 octets d'enveloppe protocolaire -->\n"
                    "<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\n"
                    "  <soap:Body><m:GetMeteoResponse xmlns:m=\"urn:isgp:meteo\">\n"
                    "    <m:Ville>Alger</m:Ville><m:TempC>24</m:TempC>\n"
                    "  </m:GetMeteoResponse></soap:Body>\n"
                    "</soap:Envelope>\n"
                    "\n"
                    "// REST/JSON : 31 octets utiles, directement natifs en Python et JS\n"
                    "{\"ville\": \"Alger\", \"temp_c\": 24}\n"
                    "```"
                )
            },
            {
                "heading": "3. Arbitrage architectural moderne : REST/JSON, GraphQL et gRPC",
                "body": (
                    "Dans un écosystème d'entreprise mature, l'ingénieur ne choisit pas un protocole par effet de mode "
                    "mais selon la topologie du trafic. **REST/JSON** couvre aujourd'hui plus de 85 % des APIs publiques, "
                    "partenaires (B2B) et frontales (Nord-Sud) grâce à son universalité absolue, sa lisibilité immédiate "
                    "avec `curl`, son intégration native aux pare-feux applicatifs et sa compatibilité naturelle avec les "
                    "réseaux de diffusion de contenu (CDN) et caches HTTP.\n\n"
                    "Deux paradigmes spécialisés complètent ce paysage pour des contraintes particulières. **GraphQL** "
                    "(conçu par Meta en 2015) répond aux écrans mobiles complexes qui doivent agréger en un seul aller-retour "
                    "réseau des champs issus d'une dizaine d'entités liées sans subir d'*over-fetching*, au prix toutefois "
                    "de la perte du cache HTTP standard et d'une complexité accrue de protection contre les requêtes "
                    "imbriquées coûteuses. **gRPC** (conçu par Google sur HTTP/2 avec sérialisation binaire *Protocol "
                    "Buffers*), quant à lui, excelle dans le trafic interne **Est-Ouest** à très haute fréquence entre "
                    "microservices backend, où le gain de latence sub-milliseconde prime sur la lisibilité humaine.\n\n"
                    "> [!NOTE] Cohabitation harmonieuse en entreprise\n"
                    "> Les grandes plateformes financières et Cloud combinent couramment ces approches : elles exposent une façade **REST/JSON documentée en OpenAPI 3.0** vers leurs clients externes et applications mobiles (trafic Nord-Sud), tout en faisant dialoguer certains moteurs internes de calcul intensif en **gRPC** derrière leur passerelle d'API."
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
            "Exécutez le script `day_1/01_html_vs_json.py` ci-dessus et relevez le ratio exact d'octets transférés entre le document HTML Jinja2, l'enveloppe SOAP/XML et la représentation REST/JSON.",
            "Enrichissez le dictionnaire métier avec un attribut `\"humidite_pct\": 68` et observez comment la route `jsonify()` expose automatiquement la nouvelle propriété sans aucune balise supplémentaire."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.2 : PILE RÉSEAU (DNS, IP, PORT TCP, TLS) & URI RFC 3986
    # =========================================================================
    "d1-l2": {
        "context": (
            "Lorsqu'une application cliente invoque `https://api.isgp.dz:8443/api/v1/formations?salle=Alger` ou "
            "qu'un administrateur démarre un démon Python avec `app.run(host=\"0.0.0.0\", port=5000)`, une "
            "chorégraphie précise s'exécute à travers les couches du noyau du système d'exploitation avant même "
            "que le premier octet n'atteigne Flask.\n\n"
            "Ignorer ce qui distingue l'adresse de bouclage `127.0.0.1` de l'interface joker `0.0.0.0`, confondre "
            "résolution DNS et routage IP, ou méconnaître le rôle d'un port TCP condamne le développeur à tâtonner "
            "aveuglément devant les incidents les plus courants de la production : `Connection refused`, `Address "
            "already in use`, `Temporary failure in name resolution` ou inaccessibilité d'un conteneur Docker. Ce "
            "chapitre ouvre le capot de la pile TCP/IP et dissèque la grammaire formelle d'une URI selon la **RFC 3986**."
        ),
        "deep_sections": [
            {
                "heading": "1. Traversée de la pile réseau : Résolution DNS, Routage IP, Socket TCP et Tunnel TLS",
                "body": (
                    "Avant qu'une requête HTTP puisse être émise, le système client doit établir un canal bidirectionnel "
                    "fiable et chiffré jusqu'au processus exact qui héberge votre application Python sur la machine distante. "
                    "Cette liaison s'opère en quatre temps séquentiels à travers les couches réseau.\n\n"
                    "#### Du nom symbolique au descripteur de fichier du processus Python\n\n"
                    "Tout commence par la **résolution DNS (*Domain Name System*)** : les routeurs Internet ne sachant "
                    "acheminer des paquets que vers des adresses numériques IPv4 ou IPv6, le résolveur du système traduit "
                    "le nom mémorisable `api.isgp.dz` en adresse IP (par exemple `196.20.45.12`). Sur la machine locale, "
                    "le fichier `/etc/hosts` court-circuite le réseau pour associer immédiatement `localhost` à l'adresse "
                    "de bouclage **`127.0.0.1`**. Vient ensuite la **poignée de main TCP en trois temps (*Three-Way "
                    "Handshake* : `SYN` → `SYN-ACK` → `ACK`)** dirigée vers le couple `(Adresse IP, Port TCP)` : alors que "
                    "l'adresse IP désigne le serveur cible, l'entier sur 16 bits du **Port TCP** (`1` à `65535`) permet au "
                    "noyau Linux d'aiguiller les segments entrants vers le bon processus parmi PostgreSQL (`:5432`), Nginx "
                    "(`:443`), SSH (`:22`) ou votre serveur Flask (`:5000`).\n\n"
                    "Enfin, dès lors que le schéma est `https://`, une **négociation cryptographique TLS 1.3** s'engage "
                    "immédiatement par-dessus la connexion TCP ouverte : le serveur présente son certificat X.509 pour "
                    "prouver son identité, et les deux parties dérivent une clé symétrique éphémère (AES-GCM ou ChaCha20) "
                    "qui chiffre intégralement l'URL complète, les en-têtes `Authorization` et le corps JSON contre toute "
                    "écoute clandestine sur le réseau."
                )
            },
            {
                "heading": "2. Interfaces d'écoute du noyau : pourquoi `127.0.0.1` et `0.0.0.0` changent tout en déploiement",
                "body": (
                    "Lorsqu'un serveur appelle la primitive système `bind(host, port)`, il indique au noyau du système "
                    "d'exploitation sur quelle interface réseau virtuelle ou physique il accepte de recevoir des connexions "
                    "entrantes. Cette distinction explique à elle seule 90 % des échecs de connexion lors du passage d'un "
                    "poste local vers un réseau d'entreprise ou un conteneur Docker.\n\n"
                    "Attacher Flask à **`host=\"127.0.0.1\"`** (comportement par défaut de `app.run()` par mesure de "
                    "prudence) restreint l'écoute à la seule interface virtuelle de bouclage interne (*loopback*, `lo`). "
                    "Les paquets ne franchissent jamais la carte Wi-Fi ou Ethernet : seuls les processus s'exécutant sur "
                    "le même système (ou dans le même espace de noms réseau) peuvent joindre le port `5000`. À l'inverse, "
                    "spécifier la méta-adresse **`host=\"0.0.0.0\"`** (`INADDR_ANY`) ordonne au noyau d'attacher le socket "
                    "à **toutes les interfaces IPv4 actives de la machine** simultanément.\n\n"
                    "> [!IMPORTANT] Conteneurs Docker et exposition réseau\n"
                    "> Chaque conteneur Docker possède sa propre interface de bouclage `127.0.0.1` isolée de la machine hôte ! Si Gunicorn ou Flask écoute sur `127.0.0.1:5000` à l'intérieur d'un conteneur, même avec `-p 5000:5000`, la machine hôte recevra `Connection reset by peer`. Dans un conteneur, le démon applicatif doit impérativement écouter sur `0.0.0.0`."
                )
            },
            {
                "heading": "3. Anatomie formelle d'une URI selon le standard IETF RFC 3986",
                "body": (
                    "La norme **RFC 3986** (*Uniform Resource Identifier : Generic Syntax*), corédigée par Tim Berners-Lee "
                    "et Roy Fielding, découpe toute adresse Web en cinq segments syntaxiques précis que Python analyse "
                    "nativement via `urllib.parse.urlsplit()` et que Flask expose séparément dans l'objet `request`.\n\n"
                    "```text — Décomposition structurelle RFC 3986 et mappage Flask\n"
                    "https://api.isgp.dz:8443/api/v1/formations?salle=Alger&page=2#details\n"
                    "|--1--| |-------2------| |-------3-------| |--------4-------| |--5--|\n"
                    "1. scheme    -> request.scheme   ('https')\n"
                    "2. authority -> request.host     ('api.isgp.dz:8443' ; port implicite : 80 ou 443)\n"
                    "3. path      -> request.path     ('/api/v1/formations' -> résolu par @app.route)\n"
                    "4. query     -> request.args     ({'salle': 'Alger', 'page': '2'})\n"
                    "5. fragment  -> [JAMAIS transmis sur le câble TCP au serveur HTTP !]\n"
                    "```\n\n"
                    "> [!NOTE] Encodage pourcent (`Percent-Encoding`) et rôle local du fragment `#`\n"
                    "> Une URI ne pouvant contenir que des caractères ASCII sûrs sans espaces, tout caractère réservé ou accentué dans la Query String est encodé sous forme d'octets UTF-8 précédés de `%` (par exemple `Labo 1` devient `Labo%201` ou `Labo+1`). Quant au **fragment** situé après `#` (`#details`), il est dépouillé par le navigateur client avant l'envoi sur le socket TCP : votre serveur Flask ne le recevra jamais."
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
                ["Port `:5000` / `:8000`", "Ports de développement Python", "Ports utilisateurs (> 1024, ne nécessitent pas les droits administrateur `root`)"],
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
            "Exécutez `day_1/03_analyseur_uri_et_reseau.py` ci-dessus, puis ajoutez un paramètre répété `?domaine=reseau&domaine=securite` pour observer comment `parse_qs()` regroupe naturellement les valeurs multiples dans une liste Python.",
            "Retirez le port explicite `:8443` de l'URI analysée et vérifiez que l'attribut `.port` vaut alors `None`, signifiant que le client doit appliquer le port standard implicite du schéma (`443` pour `https`, `80` pour `http`)."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.3 : TRAME BRUTE HTTP/1.1 & EN-TÊTES STRATÉGIQUES
    # =========================================================================
    "d1-l3": {
        "context": (
            "Une fois la poignée de main TCP achevée entre le client et le serveur, quels octets exacts circulent "
            "réellement dans le descripteur du socket ? Pour beaucoup de développeurs habitués aux bibliothèques de "
            "haut niveau, le protocole HTTP demeure une abstraction floue cachée derrière `fetch()` ou `requests.get()`.\n\n"
            "Or, la longévité exceptionnelle de **HTTP/1.1** (formalisé par les normes **RFC 9110** pour la sémantique "
            "et **RFC 9112** pour la syntaxe sur le fil) tient précisément à la limpidité de sa structure textuelle. "
            "Être capable de lire à l'œil nu une trame brute séparée par `\\r\\n`, de comprendre pourquoi `Content-Length` "
            "compte des octets UTF-8 et non des caractères, et de maîtriser la sémantique exacte des en-têtes et codes "
            "de statut transforme définitivement votre capacité à concevoir et diagnostiquer des APIs en production."
        ),
        "deep_sections": [
            {
                "heading": "1. L'invariant d'absence d'état (Statelessness) et l'autonomie de chaque requête HTTP",
                "body": (
                    "La pierre angulaire architecturale du protocole HTTP — reprise et renforcée par le style REST — est "
                    "son caractère **sans état (*Stateless*)**. Aux yeux du protocole, deux requêtes émises à dix millisecondes "
                    "d'intervalle par le même client sont deux événements strictement indépendants : le serveur ne conserve "
                    "aucune mémoire conversationnelle implicite entre deux appels sur ses travailleurs WSGI.\n\n"
                    "> « Chaque requête du client vers le serveur doit contenir l'intégralité de l'information nécessaire à la compréhension de la requête, sans pouvoir s'appuyer sur un contexte stocké sur le serveur. » — Roy T. Fielding, Architectural Styles and the Design of Network-based Software Architectures, §5.1.3\n\n"
                    "Cette contrainte, loin d'être une limitation, est le secret de la **scalabilité horizontale** des APIs "
                    "modernes : parce que chaque requête embarque dans ses propres en-têtes sa preuve d'identité "
                    "(`Authorization: Bearer ...`), la description de son format (`Content-Type: application/json`) et ses "
                    "préférences de réponse (`Accept: application/json`), un répartiteur de charge Nginx peut distribuer la "
                    "première requête d'un client vers le Serveur 1 et la suivante vers le Serveur 4 sans aucune perte de contexte."
                )
            },
            {
                "heading": "2. Délimitation binaire sur le socket TCP : `CRLF` (`\\r\\n\\r\\n`) et calcul UTF-8 de `Content-Length`",
                "body": (
                    "Le protocole TCP ne transporte pas des « messages » découpés d'avance, mais un **flux continu d'octets "
                    "(*byte stream*)**. Lorsqu'un travailleur Gunicorn ou Werkzeug lit les octets qui arrivent par petits "
                    "blocs sur la carte réseau, il suit l'automate syntaxique strict de la **RFC 9112**. La première ligne "
                    "(*Start-Line*) annonce la méthode, la cible et la version (`POST /api/v1/formations HTTP/1.1\\r\\n`), "
                    "suivie des lignes d'en-têtes `Cle: Valeur\\r\\n` (dont les noms sont insensibles à la casse selon le "
                    "standard). La frontière physique marquant la fin des métadonnées et le début immédiat du corps utile "
                    "est matérialisée par **une séquence vide `\\r\\n\\r\\n`** (deux couples *Carriage Return + Line Feed*, "
                    "octets hexadécimaux `0D 0A 0D 0A`).\n\n"
                    "```http — Anatomie exacte d'une requête HTTP/1.1 sur le fil TCP\n"
                    "POST /api/v1/formations HTTP/1.1\n"
                    "Host: api.isgp.dz\n"
                    "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbWluZSJ9.sig\n"
                    "Content-Type: application/json; charset=utf-8\n"
                    "Accept: application/json\n"
                    "Content-Length: 49\n"
                    "\n"
                    "{\"titre\": \"Sécurité des APIs\", \"jours\": 5}\n"
                    "```\n\n"
                    "> [!WARNING] `Content-Length` mesure des octets UTF-8, jamais `len(str)` !\n"
                    "> Une fois la séquence `\\r\\n\\r\\n` franchie, le parseur HTTP lit exactement le nombre d'**octets** annoncé par `Content-Length`. Or en encodage UTF-8, un caractère ASCII (`a`) pèse 1 octet, une lettre accentuée latine (`é`) pèse 2 octets, une lettre arabe (`م`) pèse 2 octets et certains symboles pèsent 4 octets. En Python, la taille réseau exacte vaut toujours `len(chaine.encode(\"utf-8\"))` et non `len(chaine)` : sous-estimer `Content-Length` tronque le JSON final et provoque un rejet `400 Bad Request` !"
                )
            },
            {
                "heading": "3. Sémantique contractuelle des familles d'en-têtes et taxonomie des codes RFC 9110",
                "body": (
                    "Dans une architecture professionnelle, les en-têtes HTTP constituent le **plan de contrôle (*Control "
                    "Plane*)** tandis que le corps JSON constitue le **plan de données (*Data Plane*)**. Six familles "
                    "d'en-têtes gouvernent ce dialogue : la négociation de représentation (`Content-Type` pour qualifier ce "
                    "qui est envoyé, `Accept` pour réclamer le format de retour), l'authentification (`Authorization`, "
                    "`WWW-Authenticate`, `X-API-Key`), la régulation de débit (`X-RateLimit-*`, `Retry-After`), la "
                    "traçabilité distribuée (`X-Request-ID`), la gouvernance du cache (`Cache-Control`, `ETag`) et le "
                    "cloisonnement navigateur (`Origin`, `Access-Control-Allow-*`).\n\n"
                    "De même, le code numérique à trois chiffres de la ligne de statut (`HTTP/1.1 422 Unprocessable Content`) "
                    "permet à tous les équipements intermédiaires — passerelles d'API, sondes Prometheus, SDK mobiles — de "
                    "prendre des décisions automatiques sans inspecter votre JSON métier. La classe **`2xx`** certifie que "
                    "l'intention du client a abouti (`200 OK`, `201 Created`, `204 No Content`) ; la classe **`3xx`** pilote "
                    "les redirections et la validation de cache (`304 Not Modified`) ; la classe **`4xx`** impute "
                    "explicitement le refus à la requête du client (qui ne doit pas la rejouer telle quelle) ; enfin, la "
                    "classe **`5xx`** signale une défaillance interne du serveur ou d'une dépendance amont, autorisant "
                    "les politiques de réessai contrôlé."
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
            "Exécutez `day_1/04_trame_http_et_headers.py` et vérifiez l'écart exact entre `len('Sécurité')` (nombre de points de code Unicode) et `len('Sécurité'.encode('utf-8'))` (taille réelle inscrite dans `Content-Length`).",
            "Dans le Client HTTP intégré, appelez successivement `/api/sandbox/status-demo/201`, `/api/sandbox/status-demo/403` et `/api/sandbox/status-demo/429` en observant les en-têtes HTTP associés à chaque statut."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.4 : MÉTHODES HTTP, IDEMPOTENCE & SÉRIALISATION JSON
    # =========================================================================
    "d1-l4": {
        "context": (
            "Sur un réseau distribué réel — couverture cellulaire 4G/5G fluctuante, tunnel VPN inter-sites ou liaison "
            "interbancaire — la perte d'un paquet d'acquittement TCP en fin de transaction est un événement banal. "
            "Lorsqu'un client émet une requête HTTP et que la connexion s'interrompt avant la réception de la ligne de "
            "statut, une question critique d'ingénierie se pose immédiatement : **le client peut-il rejouer "
            "automatiquement la même requête sans provoquer d'effet secondaire catastrophique ?**\n\n"
            "La réponse formelle à ce problème d'incertitude réseau s'appelle **l'Idempotence**. Ce chapitre expose "
            "les garanties algébriques attachées aux cinq méthodes HTTP fondamentales (`GET`, `PUT`, `DELETE`, `PATCH`, "
            "`POST`) par la norme **RFC 9110**, puis établit les conventions industrielles de sérialisation JSON "
            "(`json.dumps` / `json.loads`), d'enveloppes structurées et d'horodatage UTC ISO 8601."
        ),
        "deep_sections": [
            {
                "heading": "1. Algèbre des verbes HTTP (RFC 9110) : Méthodes Sûres (Safe) et Méthodes Idempotentes",
                "body": (
                    "La spécification **RFC 9110** (Section 9.2) ne définit pas les verbes HTTP comme de simples étiquettes "
                    "arbitraires, mais comme des **contrats comportementaux sur les effets de bord** que les proxys, les "
                    "navigateurs et les bibliothèques clientes sont autorisés à exploiter automatiquement.\n\n"
                    "> « Une méthode de requête est dite \"idempotente\" si l'effet escompté sur le serveur de multiples requêtes identiques avec cette méthode est le même que l'effet d'une unique requête de ce type. » — IETF RFC 9110, Section 9.2.2\n\n"
                    "#### Conséquences opérationnelles de `GET`, `PUT`, `DELETE`, `PATCH` et `POST`\n\n"
                    "Les méthodes **sûres (*Safe*)** — telles que `GET`, `HEAD` et `OPTIONS` — s'engagent à n'opérer aucune "
                    "mutation d'état métier sur le serveur : l'observation ne modifie pas la ressource. Toute méthode sûre "
                    "est par définition idempotente. Plus subtil est le cas de **`PUT /api/v1/formations/1`** et **`DELETE "
                    "/api/v1/formations/1`** : ces deux méthodes modifient bien la base de données (elles ne sont donc pas "
                    "*Safe*), mais elles sont **idempotentes**. Écraser une ou dix fois l'enregistrement `#1` par le même "
                    "état cible laisse la base dans un état final rigoureusement identique ; de même, supprimer une seconde "
                    "fois l'enregistrement `#1` renvoie peut-être `404` au lieu de `200`, mais l'état du serveur demeure "
                    "inchangé (la ressource `#1` est absente).\n\n"
                    "À l'opposé exact se dresse **`POST /api/v1/formations`**, qui n'est **ni sûr ni idempotent** : soumettre "
                    "trois fois la même requête `POST` ordonne la création de trois enregistrements distincts (`#101`, `#102`, "
                    "`#103`) ou déclenche trois débits bancaires consécutifs. Quant à **`PATCH`** (RFC 5789), il est idempotent "
                    "lorsqu'il affecte une valeur absolue (`{\"salle\": \"Amphi B\"}`), mais cesse de l'être s'il exprime "
                    "une opération relative telle qu'incrémenter un compteur (`{\"ajouter_places\": 5}`)."
                )
            },
            {
                "heading": "2. Pipeline de sérialisation (`json.dumps`) et désérialisation (`json.loads`) en UTF-8",
                "body": (
                    "Dans la bibliothèque standard Python, le module `json` assure la traduction bidirectionnelle entre les "
                    "structures mémoire (`dict`, `list`) et les chaînes textuelles conformes à la RFC 8259. Les fonctions "
                    "terminées par la lettre **`s`** (*string*) — **`json.dumps()`** (*dump string*) et **`json.loads()`** "
                    "(*load string*) — opèrent directement sur des chaînes en mémoire vive, par opposition à `json.dump()` "
                    "et `json.load()` qui lisent ou écrivent un descripteur de fichier sur disque.\n\n"
                    "```python — Sérialisation UTF-8 fidèle sans échappement ASCII superflu\n"
                    "import json\n"
                    "\n"
                    "enveloppe = {\"organisme\": \"ISGP\", \"intitule\": \"Sécurité des APIs\", \"ouvert\": True}\n"
                    "trame_json = json.dumps(enveloppe, ensure_ascii=False)\n"
                    "octets_reseau = trame_json.encode(\"utf-8\")\n"
                    "```\n\n"
                    "> [!TIP] Le paramètre `ensure_ascii=False` en contexte francophone et arabophone\n"
                    "> Par prudence historique, `json.dumps()` active par défaut `ensure_ascii=True`, ce qui convertit chaque caractère accentué ou arabe en séquence d'échappement hexadécimale de 6 octets (`\"S\\u00e9curit\\u00e9\"`), alourdissant inutilement le trafic et dégradant la lisibilité dans les journaux. En UTF-8 moderne (et nativement dans `jsonify()` de Flask 2.3+), l'encodage direct des caractères Unicode préserve à la fois la compacité et la clarté."
                )
            },
            {
                "heading": "3. Architecture d'enveloppe JSON (`meta` / `data`) et horodatage international ISO 8601",
                "body": (
                    "Exposer directement un tableau nu `[ {...}, {...} ]` à la racine d'un endpoint de collection constitue "
                    "une dette technique classique : six mois plus tard, lorsqu'il devient nécessaire d'ajouter le nombre "
                    "total de pages ou un curseur de continuation sans casser les clients existants, il est impossible "
                    "d'attacher une propriété à un tableau JSON ! En structurant dès l'origine vos réponses autour d'un "
                    "objet racine scindé entre **`\"meta\"`** (version du contrat, horodatage serveur, compteurs de pagination, "
                    "`request_id`) et **`\"data\"`** (l'entité ou la liste d'entités métier), vous garantissez l'extensibilité "
                    "durable de votre contrat.\n\n"
                    "La même rigueur s'impose pour le transport du temps. JSON ne possédant aucun type natif pour les dates, "
                    "l'industrie bannit formellement les formats régionaux ambigus tels que `\"08/11/2026\"` (interprété "
                    "comme le 8 novembre à Alger et Paris, mais comme le 11 août à New York). Toute date-heure exposée par "
                    "une API doit impérativement suivre la norme **ISO 8601 / RFC 3339 en temps universel coordonné (UTC)** "
                    "avec le suffixe `Z` (*Zulu Time*), telle que `\"2026-11-08T17:30:00Z\"` : non seulement elle élimine "
                    "tout bogue de fuseau horaire ou de changement d'heure d'été, mais son ordre lexicographique coïncide "
                    "exactement avec l'ordre chronologique."
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
            "Exécutez `day_1/02_serialisation_json.py` et vérifiez comment le singleton `None` et le booléen `True` ont été traduits en `null` et `true` au sein de la chaîne sérialisée.",
            "Ajoutez une liste `\"modules\": [\"HTTP/1.1\", \"Flask WSGI\", \"Sécurité JWT\"]` dans la section `data`, sérialisez l'enveloppe complète, puis désérialisez-la avec `json.loads()` pour extraire le deuxième module."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.5 : MAÎTRISER CURL, POSTMAN, HTTPIE & REST CLIENT
    # =========================================================================
    "d1-l5": {
        "context": (
            "Comment auditer, reproduire et diagnostiquer un endpoint qui exige une méthode `PATCH` ou `DELETE`, "
            "un corps JSON précis et un en-tête cryptographique `Authorization: Bearer <token>`, alors que la barre "
            "d'adresse d'un navigateur Web est structurellement cantonnée à émettre de simples requêtes `GET` "
            "dépourvues d'en-têtes personnalisés ?\n\n"
            "Un ingénieur backend ne devine jamais ce qui transite sur le fil réseau : il l'instrumente à l'aide de "
            "**clients d'inspection HTTP dédiés**. Sur un serveur Linux de production accessible uniquement en SSH ou "
            "au sein d'un pipeline CI/CD GitLab, l'utilitaire **`curl`** règne sans partage ; sur le poste de travail "
            "de l'équipe, il s'articule avec les collections collaboratives **Postman / Bruno**, la concision de "
            "**HTTPie** et les cahiers de requêtes versionnés **`.http`**. Ce chapitre vous donne la maîtrise "
            "opérationnelle de cette chaîne d'outillage."
        ),
        "deep_sections": [
            {
                "heading": "1. Pourquoi `curl` demeure l'instrument chirurgical irremplaçable en production",
                "body": (
                    "Créé en 1997 par l'ingénieur suédois Daniel Stenberg, **`curl` (*Client for URL*)** s'appuie sur la "
                    "bibliothèque C `libcurl` déployée aujourd'hui sur plusieurs milliards d'appareils, de la moindre "
                    "image Alpine Linux minimale aux routeurs industriels en passant par macOS et Windows 11. Lorsqu'un "
                    "incident critique éclate à deux heures du matin entre deux conteneurs situés dans un sous-réseau privé "
                    "sans interface graphique, ni Postman ni Chrome ne sont disponibles au bout de votre session SSH.\n\n"
                    "En quelques secondes au clavier, `curl` permet de forger n'importe quelle trame HTTP/1.1 ou HTTP/2 "
                    "exactement telle que vous l'avez conçue, sans cache fantôme, sans redirection silencieuse non désirée "
                    "et sans politique CORS navigateur venant brouiller le diagnostic. Mieux encore : une commande `curl` "
                    "est du **pur texte reproductible** que l'on consigne dans un rapport post-mortem, une spécification "
                    "technique ou un test d'intégration Bash."
                )
            },
            {
                "heading": "2. Lecture d'une trace `curl -v` : interpréter les préfixes directionnels `*`, `>` et `<`",
                "body": (
                    "Tandis que l'option `-i` (`--include`) affiche sobrement la ligne de statut et les en-têtes de la "
                    "réponse au-dessus du corps JSON, le drapeau **`-v` (`--verbose`)** ouvre une sonde complète sur chaque "
                    "couche protocolaire traversée. Pour lire instantanément sa sortie sans confusion, il suffit de "
                    "connaître la convention de ses trois marqueurs de marge.\n\n"
                    "```bash — Anatomie directionnelle d'une session diagnostique curl -v\n"
                    "$ curl -v --json '{\"identifiant\":\"stagiaire\",\"mot_de_passe\":\"isgp2026\"}' \\\n"
                    "    \"http://127.0.0.1:5000/api/sandbox/auth/token\"\n"
                    "*   Trying 127.0.0.1:5000...\n"
                    "* Connected to 127.0.0.1 (127.0.0.1) port 5000 (#0)\n"
                    "> POST /api/sandbox/auth/token HTTP/1.1\n"
                    "> Host: 127.0.0.1:5000\n"
                    "> Content-Type: application/json\n"
                    "> Accept: application/json\n"
                    "> Content-Length: 53\n"
                    "<\n"
                    "< HTTP/1.1 200 OK\n"
                    "< Content-Type: application/json\n"
                    "{\"access_token\": \"eyJ...\"}\n"
                    "```\n\n"
                    "Les lignes introduites par l'astérisque **`*`** documentent le cycle interne du moteur réseau `libcurl` "
                    "(résolution DNS, adresse IP retenue, ouverture du socket TCP, vérification du certificat TLS). Les "
                    "lignes précédées du chevron sortant **`>`** reproduisent octet pour octet les en-têtes HTTP émis par "
                    "le client vers Flask. Enfin, les lignes marquées du chevron entrant **`<`** révèlent la ligne de statut "
                    "et les en-têtes bruts renvoyés par le serveur WSGI avant l'impression du corps de réponse.\n\n"
                    "> [!WARNING] Deux pièges classiques du shell avec `curl`\n"
                    "> Premièrement, utiliser `-d '{\"cle\": 1}'` sans préciser `-H \"Content-Type: application/json\"` (ou le raccourci moderne `--json`) amène `curl` à déclarer par défaut `application/x-www-form-urlencoded`, ce qui fait que `request.get_json()` renvoie `None` côté Flask ! Deuxièmement, entourez **toujours** vos URLs de guillemets doubles `\"http://...?page=1&limit=5\"` : sans guillemets, le shell Bash interprète l'esperluette `&` comme une mise en tâche de fond et tronque tous les paramètres suivants."
                )
            },
            {
                "heading": "3. Industrialisation en équipe : Collections Postman/Bruno, HTTPie et fichiers `.http`",
                "body": (
                    "Lorsqu'un projet dépasse une vingtaine de routes et implique des équipes frontales et d'assurance "
                    "qualité, trois outils complémentaires prennent le relais au quotidien. Les environnements graphiques "
                    "**Postman**, **Bruno** ou **Insomnia** organisent le catalogue d'endpoints en *Collections* assorties "
                    "de variables dynamiques (`{{base_url}}`, `{{bearer_token}}`) permettant de basculer en un clic de "
                    "`http://127.0.0.1:5000` vers la pré-production `https://staging-api.isgp.dz`.\n\n"
                    "En ligne de commande locale, **HTTPie** (`http POST :5000/api/v1/formations titre=\"Flask\" duree_jours:=5`) "
                    "offre une ergonomie remarquable : l'opérateur `=` produit une chaîne JSON, l'opérateur `:=` produit un "
                    "type JSON natif (entier, booléen, liste), et la réponse s'affiche automatiquement indentée avec "
                    "coloration syntaxique. Enfin, les fichiers texte **`.http`** (exploités par l'extension *REST Client* "
                    "dans VS Code et Antigravity IDE) permettent de conserver vos scénarios de requêtes séparés par `###` "
                    "directement dans le dépôt Git au même niveau que le code Python qu'ils valident."
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
            "Exécutez le script `day_1/05_outils_curl_postman_httpie.py` ci-dessus afin d'inspecter en direct les réponses réelles des commandes `curl -i` émises contre le serveur du laboratoire.",
            "Basculez dans l'onglet **curl & Postman** de la barre supérieure pour tester les scénarios d'authentification et de chronométrage `-w`, puis téléchargez la Collection Postman et le fichier `.http` de référence."
        ]
    }
}
