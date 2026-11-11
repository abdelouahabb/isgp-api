"""
Manuel de Référence Approfondi — Enrichissement des Chapitres (Jours 0 et 1) — Volume III : Édition Tornado.
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
            "Avant même d'ouvrir un socket TCP non bloquant ou d'enregistrer une route sur la boucle d'événements `IOLoop` "
            "de Tornado, tout démon réseau manipule des structures physiques logées en mémoire vive (RAM) : le matricule d'un "
            "stagiaire, le montant hors taxes d'une convention, l'état d'ouverture d'une session ou l'échéance cryptographique "
            "d'un jeton d'accès. L'ingénierie des systèmes distribués commence invariablement par la maîtrise exacte de la "
            "représentation binaire et sémantique de ces grandeurs élémentaires au sein du processus serveur.\n\n"
            "Dans une architecture d'API Web industrielle, la moindre approximation sur la nature d'une donnée — confondre la "
            "chaîne textuelle `\"500\"` avec l'entier arithmétique `500`, assimiler une chaîne vide `\"\"` à l'absence "
            "explicite de valeur `None`, ou ignorer qu'en Python `bool` dérive historiquement de `int` — se propage "
            "immédiatement à travers la sérialisation JSON vers les applications clientes (terminaux mobiles iOS/Android, "
            "frontaux React/Vue, progiciels comptables partenaires). Ce chapitre inaugural établit les fondations du modèle "
            "objet CPython et du contrat de typage qui gouverne `RequestHandler.write()` dans Tornado."
        ),
        "deep_sections": [
            {
                "heading": "1. Modèle Objet CPython, Références Mémoire (`PyObject`) et Typage Dynamique Fort",
                "body": (
                    "Lorsqu'un développeur écrit l'instruction `duree_jours = 5` dans un module Python, le symbole `=` ne "
                    "traduit nullement une égalité algébrique statique, mais orchestre une **liaison par référence** en deux "
                    "temps au sein du tas mémoire (*heap*) de l'interpréteur CPython. Le moteur évalue d'abord intégralement "
                    "l'expression située à droite de l'opérateur et alloue en RAM une structure C interne appelée `PyObject`. "
                    "Cette structure embarque trois champs indissociables : un compteur de références (`ob_refcnt`) destiné au "
                    "ramasse-miettes automatique, un pointeur vers le descripteur de type (`ob_type`, ici `<class 'int'>`), et "
                    "la charge utile binaire représentant l'entier `5`. Ce n'est qu'une fois cet objet matérialisé que Python "
                    "inscrit l'étiquette symbolique `duree_jours` dans le dictionnaire de l'espace des noms courant et la fait "
                    "pointer vers l'adresse mémoire de ce `PyObject`.\n\n"
                    "#### Conséquence architecturale du typage dynamique fort\n\n"
                    "Contrairement aux langages à boîtes mémoire statiques comme C ou Go, **le type en Python appartient "
                    "exclusivement à l'objet en RAM et jamais au nom de la variable**. Ce modèle est qualifié de **typage "
                    "dynamique fort**. Il est dit *dynamique* parce qu'aucune déclaration préalable de type n'est requise sur "
                    "l'identifiant, mais il demeure rigoureusement *fort* parce que l'interpréteur interdit toute conversion "
                    "implicite silencieuse entre domaines incompatibles : évaluer `\"5\" + 2` lève instantanément une exception "
                    "`TypeError`, là où un moteur permissif comme JavaScript concaténerait silencieusement `\"52\"` au risque "
                    "de fausser un calcul de facturation.\n\n"
                    "```python — Inspection de l'identité mémoire et du descripteur PyObject\n"
                    "duree_jours = 5\n"
                    "print(type(duree_jours), hex(id(duree_jours)))  # <class 'int'> 0x7f...\n"
                    "# Toute entrée issue d'une URL Tornado arrive sous forme de str :\n"
                    "param_brut = \"15\"  # self.get_query_argument('places', '15')\n"
                    "places_totales = int(param_brut) + duree_jours  # 20 (conversion explicite)\n"
                    "```\n\n"
                    "> [!IMPORTANT] Coût mémoire et cycle de vie sur une boucle événementielle Tornado\n"
                    "> Dans un processus Tornado maintenant dix mille connexions ouvertes simultanément sur son `IOLoop`, "
                    "chaque objet retenu inutilement dans une structure globale maintient son compteur `ob_refcnt > 0` et ne "
                    "peut être libéré. Dès que l'exécution d'une requête s'achève dans `on_finish()`, la destruction de "
                    "l'instance éphémère du `RequestHandler` décrémente ces compteurs à zéro et restitue immédiatement la RAM "
                    "au processus."
                )
            },
            {
                "heading": "2. Le Contrat de Sérialisation JSON (RFC 8259) et le Tampon `self.write()` de Tornado",
                "body": (
                    "Deux processus logiciels distants — par exemple votre démon Python Tornado à Alger et une application "
                    "bancaire écrite en Kotlin ou en Go — ne partagent jamais leur mémoire vive : ils ne communiquent qu'en "
                    "s'échangeant des séquences d'octets UTF-8 sur un socket TCP selon la grammaire universelle **JSON "
                    "(*JavaScript Object Notation*, normalisée par l'IETF dans la RFC 8259)**.\n\n"
                    "> « JSON est un format textuel d'échange de données structurées, totalement indépendant des langages de "
                    "programmation, bâti autour de quatre types primitifs scalaires et de deux structures composées. » "
                    "— IETF RFC 8259, Section 1 (The JavaScript Object Notation Data Interchange Format)\n\n"
                    "#### Traduction bijective entre objets Python et représentation sur le fil\n\n"
                    "La grammaire RFC 8259 ne reconnaît exactement que quatre types scalaires primitifs : `string` (séquence "
                    "Unicode obligatoirement délimitée par des guillemets doubles `\"...\"`), `number` (représentation décimale "
                    "unifiant entiers et flottants sans support de `NaN` ni `Infinity`), `boolean` (littéraux en minuscules "
                    "`true` ou `false`), et `null` (marqueur explicite d'absence de valeur). Lorsque votre méthode `get(self)` "
                    "ou `post(self)` transmet un dictionnaire Python à `self.write(payload)`, Tornado invoque en interne "
                    "`tornado.escape.json_encode()`, pousse les octets UTF-8 résultants dans son tampon d'écriture `_write_buffer` "
                    "et positionne automatiquement l'en-tête HTTP `Content-Type: application/json; charset=UTF-8`.\n\n"
                    "#### Exactitude financière : le piège des flottants IEEE 754 (`float`) face aux centimes entiers (`int`)\n\n"
                    "Un point d'attention majeur en production concerne les montants monétaires. Le type `float` de Python "
                    "repose sur la représentation binaire IEEE 754 en base 2, dans laquelle `0.1 + 0.2` produit en réalité "
                    "`0.30000000000000004`. Dans une API de paiement ou de facturation développée avec Tornado, les architectes "
                    "transportent donc les sommes soit sous forme d'entiers exprimés dans la plus petite sous-unité monétaire "
                    "(`montant_centimes: 150050` de type `int`), soit sous forme de chaîne décimale exacte validée par le "
                    "module standard `decimal.Decimal`."
                )
            },
            {
                "heading": "3. Validation Défensive des Types Entrants avec `isinstance()` et l'Héritage `bool < int`",
                "body": (
                    "Dès qu'une API accepte des requêtes `POST`, `PUT` ou `PATCH` issues du réseau externe, rien ne garantit "
                    "que le client a respecté votre documentation OpenAPI : un script mal codé ou un attaquant peut soumettre "
                    "`{\"duree_jours\": \"cinq\"}` ou `{\"duree_jours\": true}` là où votre logique métier attend un entier "
                    "strictement positif. Inspecter défensivement les types reçus après `tornado.escape.json_decode(self.request.body)` "
                    "constitue par conséquent la première barrière d'intégrité de tout `RequestHandler`.\n\n"
                    "#### Pourquoi privilégier `isinstance()` et écarter explicitement `bool`\n\n"
                    "En Python, on préfère systématiquement la primitive `isinstance(valeur, TypeAttendu)` à une comparaison "
                    "rigide `type(valeur) == TypeAttendu`, car `isinstance` respecte le polymorphisme objet et accepte un tuple "
                    "de types autorisés tel que `isinstance(montant, (int, float))`. Toutefois, une particularité historique du "
                    "modèle de classes Python exige une vigilance absolue lors de la validation d'une charge utile JSON : "
                    "depuis Python 2.3, la classe `bool` est implémentée comme une **sous-classe directe de `int`** où `True` "
                    "vaut `1` et `False` vaut `0`.\n\n"
                    "```python — Garde-fou strict d'un entier JSON contre le piège isinstance(True, int)\n"
                    "def est_entier_json_strict(valeur: object) -> bool:\n"
                    "    # En Python, isinstance(True, int) retourne True !\n"
                    "    return isinstance(valeur, int) and not isinstance(valeur, bool)\n"
                    "```\n\n"
                    "> [!WARNING] Rejet immédiat des booléens déguisés en entiers\n"
                    "> Si un validateur Tornado se contente de tester `if isinstance(corps.get('duree_jours'), int):`, un "
                    "client envoyant `{\"duree_jours\": true}` franchira le contrôle avec succès et persistera une formation "
                    "d'une durée de `1` jour en base SQLite ! L'exclusion explicite `not isinstance(val, bool)` verrouille "
                    "définitivement cette ambiguïté."
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
                "why": "En Python, `true` sans majuscule déclenche une erreur `NameError: name 'true' is not defined`. C'est `self.write()` / `json.dumps()` qui le convertit en `true` minuscule."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur Python ci-dessus, déclarez `prix_ht_centimes = 150050` (`int`), `taux_tva = 0.19` (`float`) et `exonere_tva = False` (`bool`), puis inspectez leurs descripteurs de classe respectifs avec `type()` et leurs adresses mémoire avec `hex(id(...))`.",
            "Comparez le résultat de `100 + 50` face à `\"100\" + \"50\"`, puis écrivez une conversion explicite `int(\"100\") + 50` reproduisant le décodage d'un paramètre d'URL `self.get_query_argument()`.",
            "Écrivez un prédicat `est_entier_strict(val)` qui retourne `False` pour `True` tout en retournant `True` pour `42`, en combinant `isinstance(val, int)` et `not isinstance(val, bool)`."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.2 : LISTES, DICTIONNAIRES & STRUCTURES IMBRIQUÉES
    # =========================================================================
    "d0-l2": {
        "context": (
            "Aucune API d'entreprise ne se limite à échanger un scalaire isolé tel que le nombre `42` sans contexte : "
            "les systèmes réels transportent des **agrégats documentaires riches**, comme la fiche complète d'une "
            "session de formation associant ses attributs administratifs, les coordonnées structurées de son intervenant "
            "et la collection paginée des participants inscrits.\n\n"
            "Toute la modélisation des charges utiles en mémoire Python et en JSON repose sur la composition orthogonale "
            "de deux structures de données fondamentales : le **dictionnaire (`dict`)** qui indexe les propriétés d'une "
            "entité par clés nommées en temps constant, et la **liste (`list`)** qui maintient une séquence ordonnée "
            "d'éléments. Maîtriser leur mécanique interne en RAM ainsi que les idiomes de lecture défensive et "
            "d'encapsulation exigés par `RequestHandler.write()` représente le cœur quotidien du développement Tornado."
        ),
        "deep_sections": [
            {
                "heading": "1. Architecture Interne d'un Dictionnaire CPython (`dict` — Table de Hachage Compacte)",
                "body": (
                    "Sous le capot de l'interpréteur CPython (depuis Python 3.6+), un dictionnaire `{ \"cle\": valeur }` est "
                    "implémenté sous la forme d'une **table de hachage compacte à adressage ouvert** conservant l'ordre exact "
                    "d'insertion des clés. Lorsqu'une instruction évalue `formation[\"titre\"]`, Python applique la fonction "
                    "`hash(\"titre\")` pour obtenir un entier 64 bits qui pointe directement vers l'entrée correspondante du "
                    "tableau d'indices en mémoire vive. Cette architecture garantit une complexité algorithmique **constante "
                    "`O(1)` en moyenne** : extraire une clé prend la même fraction de microseconde que le dictionnaire "
                    "comporte trois attributs ou cent mille entrées.\n\n"
                    "#### Unicité des clés et sérialisation directe par `RequestHandler.write()`\n\n"
                    "Dans un dictionnaire, chaque clé immuable est rigoureusement unique : affecter une seconde fois "
                    "`formation[\"salle\"] = \"Amphi B\"` écrase immédiatement la référence précédente en place. Sur le plan du "
                    "protocole HTTP, Tornado accorde au type `dict` un statut de citoyen de première classe : passer un "
                    "dictionnaire à `self.write(formation)` déclenche automatiquement sa conversion JSON UTF-8 et l'émission "
                    "de l'en-tête `Content-Type: application/json; charset=UTF-8` sans aucune étape intermédiaire."
                )
            },
            {
                "heading": "2. Programmation Défensive : Éradiquer les Pannes `HTTP 500` grâce à `.get()`",
                "body": (
                    "Lorsqu'un client distant soumet une requête `POST` à votre serveur Tornado, l'appel "
                    "`corps = tornado.escape.json_decode(self.request.body)` reconstruit un dictionnaire Python fidèle aux "
                    "octets envoyés sur le socket TCP. Que se produit-il à l'instant précis où votre contrôleur exécute "
                    "`salle = corps[\"salle\"]` alors que l'application mobile cliente a omis ce champ optionnel ?\n\n"
                    "#### De l'exception `KeyError` à la résilience contractuelle\n\n"
                    "L'opérateur d'indexation directe `[...]` lève sans préavis une exception `KeyError: 'salle'`. Si celle-ci "
                    "n'est pas interceptée, elle interrompt brutalement le cycle du `RequestHandler`, journalise un *Traceback* "
                    "complet côté serveur et renvoie au client un code alarmant **`500 Internal Server Error`** imputant à tort "
                    "la faute à votre infrastructure. À l'opposé, la méthode **`corps.get(\"salle\", \"Salle A\")`** interroge "
                    "la table de hachage en mode total : elle restitue la valeur associée si la clé figure dans le dictionnaire, "
                    "ou retourne pacifiquement la valeur de repli (`\"Salle A\"`, ou `None` si le second argument est omis) "
                    "sans jamais perturber l'`IOLoop`.\n\n"
                    "```python — Lecture défensive en cascade d'un document JSON imbriqué\n"
                    "# Même si 'formateur' est absent du JSON, aucune KeyError n'est levée :\n"
                    "info_formateur = corps.get(\"formateur\") or {}\n"
                    "grade = info_formateur.get(\"grade\", \"Consultant Senior\")\n"
                    "salle = corps.get(\"salle\", \"Non attribuée\")\n"
                    "```"
                )
            },
            {
                "heading": "3. Tableaux Dynamiques (`list`), Slicing et Invariant de Sécurité `self.write()` dans Tornado",
                "body": (
                    "En mémoire CPython, une liste `[elem0, elem1, elem2]` n'enregistre pas les objets côte à côte par valeur, "
                    "mais maintient un **vecteur contigu de pointeurs** surdimensionné avec réserve de croissance (*over-allocation*), "
                    "ce qui rend l'accès indexé `liste[0]` ou `liste[-1]` (dernier élément) instantané en `O(1)` et l'ajout "
                    "en fin de séquence `liste.append(item)` amorti en temps constant. De plus, l'opérateur de découpage "
                    "*slicing* `liste[offset : offset + limit]` tolère élégamment les bornes dépassant la fin de la liste sans "
                    "jamais lever d'`IndexError`, offrant la brique idéale pour paginer une collection en mémoire.\n\n"
                    "> [!IMPORTANT] Pourquoi Tornado interdit `self.write([ ... ])` sur une liste nue\n"
                    "> Si vous invoquez directement `self.write([{\"id\": 1}, {\"id\": 2}])` dans un `RequestHandler`, Tornado "
                    "lève délibérément `TypeError: Lists not accepted for security reasons`. Historiquement conçue pour "
                    "bloquer la faille *JSON Array Hijacking* sur d'anciens moteurs JavaScript redéfinissant le constructeur "
                    "`Array`, cette garde architecturale impose une excellente discipline d'ingénierie : toujours envelopper "
                    "une collection dans un **dictionnaire racine** tel que `self.write({\"total\": len(items), \"data\": items})`, "
                    "ce qui permet d'enrichir ultérieurement la réponse avec des métadonnées de pagination sans jamais rompre "
                    "la rétrocompatibilité des clients."
                )
            }
        ],
        "architecture_diagram": (
            "TABLE SQL / COLLECTION API : formations (Liste Python [ ... ] enveloppée dans dict)\n"
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
                "bad": "Passer une liste brute `self.write([...])` à la racine d'une réponse Tornado",
                "good": "Envelopper la liste dans un dictionnaire : `self.write({\"total\": len(items), \"items\": [...]})`",
                "why": "Un dictionnaire racine est sérialisé automatiquement par Tornado et permet d'ajouter des métadonnées (`page`, `total_pages`) sans casser le contrat JSON."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur Python ci-dessus, insérez un quatrième dictionnaire stagiaire doté de l'attribut `\"certifie\": True` via `.append()`, puis encapsulez la liste dans une enveloppe `{\"total\": len(stagiaires), \"data\": stagiaires}` prête pour `self.write()`.",
            "Rédigez une compréhension de liste filtrant uniquement les stagiaires rattachés aux services `\"Sécurité\"` ou `\"Réseau\"` sans modifier la collection initiale.",
            "Éprouvez la résilience de `stagiaires[0].get(\"telephone\", \"Non renseigné\")` et comparez son comportement à un accès direct sur une clé absente."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.3 : FONCTIONS, PARAMÈTRES, RETURN & TUPLES D'ÉTAT
    # =========================================================================
    "d0-l3": {
        "context": (
            "Au sein d'une application Tornado maintenable, les classes `RequestHandler` ne contiennent jamais des "
            "centaines de lignes de calculs fiscaux ou d'algorithmes métier mêlés au protocole HTTP : **chaque contrôleur "
            "délègue la logique pure à des fonctions Python découplées**, puis exploite la valeur restituée par "
            "l'instruction **`return`** pour piloter `self.set_status(code)` et `self.write(dictionnaire)`.\n\n"
            "Une confusion conceptuelle persistante chez les développeurs débutants consiste à assimiler `print()` — qui "
            "écrit sur le flux texte local de l'administrateur — à `return` et `self.write()`, seuls capables de "
            "transmettre une donnée structurée vers l'appelant et le tampon socket de Tornado. Ce chapitre dissèque le "
            "cadre d'exécution d'une fonction, le patron des clauses de garde (*Early Return*) et le décompactage de "
            "tuples `(charge_json, statut_http)`."
        ),
        "deep_sections": [
            {
                "heading": "1. Cadre d'Exécution (*Stack Frame*), Portée Locale et Cycle de `return`",
                "body": (
                    "Déclarer une fonction au moyen du mot-clé `def calculer_facture(montant_ht, taux_tva=0.19):` forge un "
                    "composant réutilisable régi par une frontière mémoire stricte. À chaque invocation, la machine virtuelle "
                    "Python pousse sur sa pile d'appels un **cadre d'exécution isolé (*frame*)** contenant uniquement les "
                    "paramètres reçus et les variables locales créées dans le bloc indenté. Si un paramètre déclare une valeur "
                    "par défaut immuable (`=0.19`), l'appelant peut l'omettre dans le cas nominal tout en conservant la "
                    "faculté de la surcharger explicitement.\n\n"
                    "#### Terminaison immédiate et réclamation mémoire\n\n"
                    "Dès que le flux d'exécution rencontre l'instruction `return resultat`, deux phénomènes atomiques se "
                    "produisent : la fonction s'interrompt instantanément (toute instruction placée en dessous dans le même "
                    "bloc constitue du code mort inaccessible) et la référence vers l'objet `resultat` est transmise à "
                    "l'appelant tandis que toutes les variables intermédiaires locales sont désallouées. Sur une boucle "
                    "événementielle `IOLoop` partageant un processus unique entre des milliers d'appels successifs, cette "
                    "automaticité empêche toute fuite d'état d'un client vers le suivant.\n\n"
                    "> [!WARNING] L'anti-pattern classique des valeurs par défaut mutables (`def f(items=[]):`)\n"
                    "> En Python, les expressions par défaut d'une signature `def` sont évaluées **une seule et unique fois au "
                    "chargement du module**, et non à chaque appel de la fonction. Écrire `def ajouter_erreur(msg, liste=[]):` "
                    "partagerait exactement la même liste en RAM entre tous les clients de votre API Tornado ! Adoptez "
                    "invariablement le marqueur immuable `None` : `def ajouter_erreur(msg, liste=None): liste = [] if liste is None else liste`."
                )
            },
            {
                "heading": "2. Le Patron « Early Return » (*Guard Clauses*) dans les Méthodes `RequestHandler`",
                "body": (
                    "Dans les méthodes `def get(self):` ou `def post(self):` d'un `RequestHandler` Tornado, une subtilité "
                    "essentielle distingue `self.write()` de l'instruction `return` du langage Python : **appeler `self.write(d)` "
                    "ajoute simplement des octets dans le tampon mémoire de sortie de la requête sans interrompre l'exécution "
                    "de la méthode Python** ! Si vous écrivez un message d'erreur `400` sans faire suivre cet envoi d'un "
                    "`return` explicite, Python poursuivra sa descente dans le traitement nominal et concaténera un second "
                    "objet JSON invalide à la suite du premier dans le même tampon HTTP.\n\n"
                    "#### Linéariser la validation par sorties anticipées\n\n"
                    "Les ingénieurs expérimentés combinent systématiquement les vérifications de préconditions en tête de "
                    "méthode avec un `return` immédiat (ou `self.finish(err)` suivi de `return`) afin d'aplatir l'arbre "
                    "décisionnel et d'éliminer les pyramides illisibles de `if / else` imbriqués sur cinq niveaux.\n\n"
                    "```python — Clauses de garde linéaires dans un RequestHandler Tornado\n"
                    "def post(self) -> None:\n"
                    "    if not self.request.headers.get(\"Authorization\"):\n"
                    "        self.set_status(401)\n"
                    "        self.write({\"erreur\": \"Authentification requise\"})\n"
                    "        return  # Indispensable pour stopper l'exécution ici !\n"
                    "    if montant <= 0:\n"
                    "        self.set_status(422)\n"
                    "        self.write({\"erreur\": \"Le montant doit être strictement positif\"})\n"
                    "        return\n"
                    "    self.set_status(201)\n"
                    "    self.write({\"statut\": \"confirmé\", \"montant\": montant})\n"
                    "```"
                )
            },
            {
                "heading": "3. Découpler la Logique Métier du Transport HTTP grâce aux Tuples `(corps, code_http)`",
                "body": (
                    "Pour tester unitairement vos règles de gestion en une fraction de milliseconde sans même démarrer de "
                    "serveur HTTP, la fonction métier pure ne doit pas dépendre de `self` ni de `tornado.web`. Comment "
                    "peut-elle dès lors restituer simultanément le dictionnaire de données JSON et le code de statut HTTP "
                    "(`200`, `201`, `400`, `422`) qui en découle ?\n\n"
                    "#### Empaquetage et décompactage (*Tuple Unpacking*)\n\n"
                    "Séparer plusieurs expressions par des virgules après `return` (`return dictionnaire, 201`) construit en "
                    "mémoire un **tuple** immuable `(dictionnaire, 201)`. À la réception, le `RequestHandler` Tornado "
                    "décompacte élégamment cette paire en une seule affectation lisible : "
                    "`corps, statut = construire_reponse_api(titre, duree)`, avant d'appliquer `self.set_status(statut)` puis "
                    "`self.write(corps)`. Ce découpage architectural dit *Clean / Hexagonal* isole intégralement votre domaine "
                    "métier des détails protocolaires de Tornado."
                )
            }
        ],
        "architecture_diagram": (
            "REQUÊTE CLIENT HTTP               MÉTHODE HANDLER TORNADO                      SORTIE\n"
            "-------------------               -----------------------                      ------\n"
            "POST /api/formations   ======>    def post(self):                              \n"
            "                                      print(\"Log interne\")       --------->   Terminal du serveur uniquement\n"
            "                                      if not titre:                            \n"
            "                                          self.set_status(400)                 \n"
            "                                          self.write({\"err\": ...}); return => Réponse HTTP 400 envoyée au client\n"
            "                                      self.set_status(201)                     \n"
            "                                      self.write({\"ok\": titre})  =========>   Réponse HTTP 201 envoyée au client"
        ),
        "reference_table": {
            "title": "Comparaison Technique : `print()` vs `return` vs `self.write()` dans Tornado",
            "headers": ["Instruction / Syntaxe", "Destinataire de la donnée", "Interrompt la méthode ?", "Effet dans Tornado", "Résultat pour le client HTTP"],
            "rows": [
                ["`print(donnees)`", "Terminal local (`stdout`)", "Non (continue à la ligne suivante)", "Aucun octet écrit dans le tampon HTTP", "Réponse vide si `self.write()` n'est jamais appelé"],
                ["`self.write(d)`", "Tampon de sortie Tornado → Client HTTP", "Non (ajouter `return` si sortie anticipée)", "Sérialise `d` en JSON + statut `200 OK` par défaut", "Réponse JSON avec statut **`200 OK`**"],
                ["`self.set_status(201); self.write(d)`", "Tampon de sortie Tornado → Client HTTP", "Non", "Positionne le code `201` + sérialise `d` en JSON", "Réponse JSON avec statut **`201 Created`**"],
                ["`self.finish(d)`", "Tampon de sortie Tornado → Client HTTP", "Ferme immédiatement la connexion HTTP", "Envoie les octets sur l'`IOLoop`", "Idéal dans `prepare(self)` pour court-circuiter une requête"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Appeler `self.set_status(400); self.write(err)` au début d'une méthode sans mettre `return` juste après",
                "good": "Toujours placer `return` après une réponse d'erreur anticipée dans `get()` / `post()`",
                "why": "Contrairement à `return`, `self.write()` n'arrête pas la fonction Python : sans `return`, le code continuerait et écrirait un second JSON à la suite du premier !"
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
            "Dans l'exécuteur ci-dessus, invoquez `construire_reponse_api(\"\", 3)` afin d'observer le déclenchement immédiat de la clause de garde retournant le code `400` sans exécuter la création.",
            "Enrichissez `construire_reponse_api` d'une seconde clause de garde renvoyant le tuple `({\"erreur\": \"Durée maximale plafonnée à 30 jours\"}, 422)` lorsque `duree_jours > 30`.",
            "Décompactez l'appel nominal `corps, statut = construire_reponse_api(\"Architecture Tornado\", 4)` et affichez distinctement le statut numérique et le dictionnaire."
        ]
    },

    # =========================================================================
    # JOUR 0 — CHAPITRE 0.4 : EXCEPTIONS (TRY/EXCEPT) & DÉCORATEURS (@)
    # =========================================================================
    "d0-l4": {
        "context": (
            "En parcourant le code source d'une plateforme Tornado en production, deux idiomes Python structurent "
            "systématiquement la robustesse et la sécurité de chaque `RequestHandler` : les gestionnaires d'exceptions "
            "ciblés **`try / except`** et les décorateurs de méthodes introduits par le symbole arobase **`@`** tels que "
            "`@tornado.web.authenticated` ou `@exiger_role(\"admin\")`.\n\n"
            "Loin d'être des artifices syntaxiques opaques, ces deux constructions reposent sur le mécanisme de remontée "
            "de pile (*stack unwinding*) et sur les fermetures lexicales (*closures*) de Python. Ce chapitre en dévoile "
            "l'anatomie complète, y compris leur interaction avec les coroutines asynchrones `async def` exécutées par "
            "l'`IOLoop` Tornado."
        ),
        "deep_sections": [
            {
                "heading": "1. Remontée de Pile (*Stack Unwinding*) et Isolation des Erreurs par `try / except`",
                "body": (
                    "Dans un script jetable lancé en console, une conversion impossible telle que `int(\"abc\")` interrompt "
                    "légitimement le processus en imprimant un *Traceback*. Sur un démon Tornado multiplexant des milliers de "
                    "clients concurrents sur une unique boucle `IOLoop`, laisser une saisie invalide d'un utilisateur isolé "
                    "provoquer une défaillance non maîtrisée (`500 Internal Server Error`) fausse vos métriques d'exploitation "
                    "et risque, si `debug=True` a été oublié, d'exposer l'arborescence interne de votre code source.\n\n"
                    "#### Granularité chirurgicale de la capture d'exceptions\n\n"
                    "Lorsqu'une instruction échoue à l'intérieur d'un bloc `try:`, la machine virtuelle suspend immédiatement "
                    "la séquence en cours et remonte la pile à la recherche d'une clause `except` correspondant exactement à "
                    "la classe de l'exception levée (`ValueError`, `json.JSONDecodeError`, `sqlite3.IntegrityError`). Si aucune "
                    "anomalie ne survient, le coût d'exécution d'un bloc `try` en Python moderne (3.11+ *zero-cost exceptions*) "
                    "est pratiquement nul. En revanche, on ne capture jamais `except Exception:` à l'aveugle : cibler "
                    "exclusivement l'erreur attendue permet de convertir une entrée client malformée en réponse JSON propre "
                    "`400 Bad Request` tout en laissant remonter les véritables bugs de programmation vers `write_error(500)`."
                )
            },
            {
                "heading": "2. Démystification Complète des Décorateurs `@` : Fermetures Lexicales et Ordre Supérieur",
                "body": (
                    "En Python, les fonctions et méthodes de classes ne sont pas de simples blocs d'instructions figés en "
                    "mémoire morte : ce sont des **objets de première classe (`function` instances)** que l'on peut transmettre "
                    "en argument, stocker dans un dictionnaire ou fabriquer dynamiquement à l'intérieur d'une autre fonction. "
                    "Un **décorateur** est une fonction d'ordre supérieur qui accepte une fonction cible en entrée et retourne "
                    "une nouvelle fonction enveloppante enrichie d'un comportement transversal.\n\n"
                    "```python — Équivalence stricte entre la syntaxe @ et la réassignation d'objet\n"
                    "# Écriture idiomatique avec @ :\n"
                    "@journaliser_appel\n"
                    "def traiter_paiement(montant: float) -> dict:\n"
                    "    return {\"montant\": montant, \"statut\": \"valide\"}\n\n"
                    "# Ce que l'interpréteur Python exécute exactement à la définition :\n"
                    "traiter_paiement = journaliser_appel(traiter_paiement)\n"
                    "```\n\n"
                    "Grâce à sa fermeture lexicale (*closure*), la fonction interne `enveloppe` conserve une référence permanente "
                    "vers la fonction originale : elle peut inspecter les arguments ou les en-têtes HTTP **avant** l'appel, "
                    "décider de court-circuiter totalement l'exécution si le jeton est invalide, ou mesurer la durée écoulée "
                    "**après** l'appel."
                )
            },
            {
                "heading": "3. Décorer une Méthode de `RequestHandler` Tornado (`self`, `*args`, `@wraps` et `async def`)",
                "body": (
                    "Adapter le patron décorateur aux méthodes d'instance `get(self, ...)` ou `delete(self, id)` d'un "
                    "`RequestHandler` Tornado requiert la maîtrise de trois détails d'ingénierie fondamentaux. Tout d'abord, "
                    "le premier paramètre reçu par la fonction interne est toujours **`self`**, c'est-à-dire l'instance "
                    "courante du `RequestHandler` donnant accès à `self.request.headers`, `self.current_user`, `self.set_status()` "
                    "et `self.finish()`. Ensuite, la signature générique `(self, *args, **kwargs)` transfère de façon "
                    "transparente tous les groupes capturants extraits de l'URL par le routeur Regex de Tornado.\n\n"
                    "```python — Squelette industriel d'un décorateur compatible synchrone & async Tornado\n"
                    "from functools import wraps\n"
                    "import inspect\n\n"
                    "def exiger_cle_interne(methode):\n"
                    "    @wraps(methode)  # Préserve __name__, __doc__ et la signature originale\n"
                    "    async def enveloppe(self, *args, **kwargs):\n"
                    "        if self.request.headers.get(\"X-Internal-Token\") != \"secret\":\n"
                    "            self.set_status(401)\n"
                    "            self.finish({\"erreur\": \"Jeton interne invalide\"})\n"
                    "            return\n"
                    "        resultat = methode(self, *args, **kwargs)\n"
                    "        if inspect.isawaitable(resultat):\n"
                    "            return await resultat\n"
                    "        return resultat\n"
                    "    return enveloppe\n"
                    "```\n\n"
                    "> [!TIP] Compatibilité universelle avec les coroutines `async def` de Tornado\n"
                    "> Dans Tornado 6, une méthode de `RequestHandler` peut être soit synchrone (`def get`), soit asynchrone "
                    "(`async def get`). Définir l'enveloppe en `async def` et tester `inspect.isawaitable(resultat)` garantit "
                    "que l'`IOLoop` attendra proprement la fin de la coroutine décorée sans jamais perdre d'exception en vol."
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
            "|     (Si Token invalide -> self.set_status(401) sans entrer !)     |\n"
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
            "title": "Exceptions Standards Python et Traduction en Codes de Statut HTTP dans Tornado",
            "headers": ["Exception Python", "Cause technique déclenchante", "Exemple concret", "Code HTTP à renvoyer dans l'API"],
            "rows": [
                ["`ValueError`", "Conversion impossible d'une valeur", "`int(\"abc\")` sur `?page=abc`", "**`400 Bad Request`** ou **`422`**"],
                ["`json.JSONDecodeError`", "Corps JSON mal formé", "`tornado.escape.json_decode(b\"{bad\")`", "**`400 Bad Request`**"],
                ["`tornado.web.MissingArgumentError`", "Argument requis absent", "`self.get_query_argument(\"ht\")` sans défaut", "**`400 Bad Request`**"],
                ["`sqlite3.IntegrityError`", "Violation d'une contrainte SQL (`UNIQUE`, `NOT NULL`)", "Créer un code déjà existant", "**`409 Conflict`** ou **`422 Unprocessable Entity`**"],
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
                "good": "Journaliser l'erreur technique en interne et renvoyer un message générique propre via `write_error`",
                "why": "Afficher l'erreur brute révèle la structure de vos tables SQL et les chemins de votre serveur aux attaquants."
            },
            {
                "bad": "Oublier `return fonction_cible(*args, **kwargs)` à l'intérieur de l'enveloppe d'un décorateur",
                "good": "Toujours capturer et retourner le résultat (ou `await` si coroutine `async def`) de la méthode enveloppée",
                "why": "Si la méthode décorée est une coroutine `async def`, retourner sa valeur permet à l'`IOLoop` Tornado de l'attendre proprement."
            }
        ],
        "practical_exercises": [
            "Dans l'exécuteur ci-dessus, appelez `convertir_parametre_entier(\"-5\")` puis étendez la validation afin que tout entier inférieur ou égal à zéro retourne un dictionnaire d'erreur structuré.",
            "Rédigez un décorateur `@verifier_montant_positif` muni de `@wraps` qui court-circuite l'appel à `traiter_paiement` en retournant `{\"erreur\": \"Montant <= 0 interdit\"}` avant même d'exécuter le corps métier si le montant est négatif ou nul.",
            "Empilez `@journaliser_execution` et `@verifier_montant_positif` sur la même fonction afin d'observer l'ordre d'imbrication des pré-traitements et post-traitements."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.1 : HTML VS SOAP/XML VS REST/JSON
    # =========================================================================
    "d1-l1": {
        "context": (
            "Pourquoi la quasi-totalité des institutions financières, des opérateurs télécoms, des services publics "
            "numériques et des plateformes logistiques bâtissent-ils aujourd'hui leur système d'information autour "
            "d'**APIs découplées** plutôt que d'applications Web monolithiques ?\n\n"
            "Dans un serveur Web classique des années 1990-2000, les données extraites de la base SQL et leur mise en "
            "forme visuelle (couleurs, grilles CSS, balises HTML) étaient soudées au sein de la même réponse serveur. "
            "Ce couplage fort s'effondre instantanément dès qu'il faut raccorder une application mobile iOS/Android, un "
            "automate bancaire ou le progiciel ERP d'un partenaire. Ce chapitre retrace la généalogie architecturale des "
            "services Web et démontre, octets à l'appui avec Tornado, pourquoi le paradigme **REST / JSON** s'est imposé "
            "comme la *lingua franca* des architectures distribuées."
        ),
        "deep_sections": [
            {
                "heading": "1. Du Monolithe HTML Couplé à l'Architecture Centrée API (Découplage Métier / Présentation)",
                "body": (
                    "Lorsqu'un serveur monolithique traditionnel exécute une requête métier et fusionne immédiatement ses "
                    "résultats dans un document `<html><body><div class=\"carte-meteo\">24 °C</div></body></html>`, il ne "
                    "produit pas de l'information exploitable par une machine : il produit des instructions de dessin pour un "
                    "navigateur graphique. Si le logiciel comptable d'un partenaire ou une application mobile Swift/Kotlin tente "
                    "d'extraire ce chiffre par *Web Scraping*, la moindre modification cosmétique d'une classe CSS par un "
                    "intégrateur Web provoque une rupture immédiate en production.\n\n"
                    "#### Le serveur Tornado comme source de vérité contractuelle\n\n"
                    "L'architecture centrée **API (*Application Programming Interface*)** opère une séparation chirurgicale "
                    "des responsabilités : le backend Tornado expose exclusivement des **représentations de données pures, "
                    "typées et versionnées** via `self.write(dict)`. Dès lors, le portail Web React/Vue, les applications "
                    "mobiles natives et les démons partenaires deviennent tous des consommateurs équivalents interrogeant "
                    "exactement le même contrat JSON stable."
                )
            },
            {
                "heading": "2. Généalogie des Protocoles : SOAP/XML (WSDL) face à la Révolution REST/JSON (Roy Fielding)",
                "body": (
                    "Deux philosophies majeures ont façonné l'histoire de l'intégration machine-à-machine sur IP. Conçu à la "
                    "fin des années 1990 par Microsoft et IBM, **SOAP (*Simple Object Access Protocol*)** considère HTTP comme "
                    "un simple tuyau aveugle : toutes les opérations sont généralement tunnelisées en `POST` vers une unique "
                    "URL, enfermées dans une lourde enveloppe XML (`<soap:Envelope><soap:Body>...</soap:Body></soap:Envelope>`) "
                    "décrite par un contrat rigide **WSDL / XSD**. Bien que toujours présent dans la compensation interbancaire "
                    "historique, SOAP multiplie par trois à cinq le volume réseau et mobilise des analyseurs DOM XML gourmands "
                    "en cycles processeur sur une boucle événementielle.\n\n"
                    "> « REST fournit un ensemble de contraintes architecturales qui, lorsqu'elles sont appliquées dans leur "
                    "globalité, mettent l'accent sur le passage à l'échelle des interactions entre composants et la généralité "
                    "des interfaces. » — Roy Thomas Fielding, Architectural Styles and the Design of Network-based Software "
                    "Architectures (Thèse de doctorat, UC Irvine, Chapitre 5, 2000)\n\n"
                    "En formalisant **REST (*Representational State Transfer*)**, Roy Fielding — co-auteur principal de la "
                    "spécification HTTP/1.1 — a démontré qu'il était inutile de réinventer une couche d'adressage et d'erreur "
                    "à l'intérieur de XML alors que HTTP possède déjà nativement les **URIs** pour identifier les ressources, "
                    "les **méthodes** (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) pour qualifier l'action, les **codes de statut** "
                    "(`200`, `201`, `404`, `422`) pour exprimer l'issue, et les en-têtes `Etag` / `Cache-Control` pour la mise "
                    "en cache. Associé à la compacité de **JSON**, ce modèle réduit drastiquement la latence de sérialisation "
                    "sur l'`IOLoop` de Tornado.\n\n"
                    "```http — Contraste d'empreinte sur le fil : réponse REST/JSON Tornado vs enveloppe SOAP\n"
                    "HTTP/1.1 200 OK\n"
                    "Server: TornadoServer/6.4\n"
                    "Content-Type: application/json; charset=UTF-8\n"
                    "Etag: \"a8f5f167f44f4964e6c998dee827110c\"\n\n"
                    "{\"ville\": \"Alger\", \"temperature_c\": 24.5, \"statut\": \"ensoleille\"}\n"
                    "```"
                )
            },
            {
                "heading": "3. Arbitrage Architectural Moderne : REST/JSON, GraphQL et gRPC dans Tornado",
                "body": (
                    "Dans un écosystème d'entreprise contemporain, le choix du protocole dépend de la topologie du trafic "
                    "(Nord-Sud public contre Est-Ouest interne). **REST/JSON** demeure le standard incontesté pour plus de "
                    "85 % des flux Nord-Sud (APIs publiques, partenaires B2B, portails Web et mobiles) grâce à sa lisibilité "
                    "immédiate sous `curl`, son intégration native au cache HTTP des CDN/proxies et la maturité universelle "
                    "d'OpenAPI 3.0.\n\n"
                    "#### Positionnement ciblé de GraphQL et gRPC\n\n"
                    "Créé par Meta en 2015, **GraphQL** répond aux écrans mobiles agrégeant une dizaine d'entités imbriquées "
                    "en permettant au client de sélectionner champ par champ sa projection sur un endpoint `POST /graphql` "
                    "unique, au prix toutefois d'une complexité accrue de mise en cache HTTP et de prévention des requêtes `N+1`. "
                    "De son côté, **gRPC** (Google) transporte des messages binaires compilés *Protocol Buffers* sur des flux "
                    "HTTP/2 multiplexés : il excelle dans les appels Est-Ouest à ultra-haute fréquence entre microservices "
                    "internes, tandis qu'une passerelle Tornado REST/JSON assure l'exposition claire et gouvernée vers le monde "
                    "extérieur."
                )
            }
        ],
        "architecture_diagram": (
            "ARCHITECTURE MONOLITHE HTML (Couplage fort)           ARCHITECTURE CENTRÉE API REST (Découplage total)\n"
            "-------------------------------------------           ------------------------------------------------\n"
            "[Base SQL] -> [Serveur] --(HTML+CSS)--> Navigateur    [Base SQL] -> [Serveur API Tornado] ==(JSON Pur)==+--> Portail Web (PWA/React)\n"
            "                  |                                                                                     +--> Application Mobile (iOS/Android)\n"
            "                  +--(HTML inutilisable !)--> App Mobile / Partenaire                                   +--> Serveur Partenaire / Script Python"
        ),
        "reference_table": {
            "title": "Comparatif Architectural des Paradigmes de Services Web",
            "headers": ["Critère", "Site Web HTML (`self.render`)", "Service Web SOAP / XML", "API REST / JSON (`self.write`)", "gRPC (Protobuf)"],
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
            "Exécutez `day_1/01_html_vs_json.py` ci-dessus afin de mesurer au moyen d'`AsyncHTTPClient` l'écart exact d'octets entre la page HTML compilée, l'enveloppe SOAP/XML et la charge utile REST/JSON servies par Tornado.",
            "Ajoutez l'attribut `\"humidité_pct\": 62` dans `DONNEES_METEO` et vérifiez que l'empreinte JSON demeure plus de deux fois inférieure à celle de la trame SOAP équivalente."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.2 : PILE RÉSEAU (DNS, IP, PORT TCP, TLS) & URI RFC 3986
    # =========================================================================
    "d1-l2": {
        "context": (
            "Lorsqu'une application cliente invoque `fetch(\"https://api.isgp.dz:8443/v1/formations?salle=Alger\")` ou "
            "qu'un ingénieur démarre un démon via `app.listen(8888, address=\"0.0.0.0\")`, quels mécanismes noyau "
            "entrent exactement en action sur l'interface réseau du système d'exploitation ?\n\n"
            "Tant que la distinction physique entre une **adresse IP** (`127.0.0.1` face à `0.0.0.0` ou `192.168.1.x`), "
            "un **descripteur de Port TCP** (`:8888`, `:443`) et la grammaire normalisée d'une **URI (RFC 3986)** reste "
            "floue, des incidents quotidiens tels que `Connection refused`, `Errno 98: Address already in use` ou "
            "`Temporary failure in name resolution` paraissent insolubles. Ce chapitre met à nu la traversée de la pile "
            "TCP/IP jusqu'au socket d'écoute non bloquant de Tornado."
        ),
        "deep_sections": [
            {
                "heading": "1. Traversée des Couches Réseau : Résolution DNS, Routage IP, Socket TCP et Tunnel TLS",
                "body": (
                    "Acheminer un appel d'API depuis un terminal client jusqu'au processus Python Tornado mobilise quatre "
                    "protocoles superposés de la pile Internet. Tout commence par la **résolution DNS (*Domain Name System*)** : "
                    "parce que les routeurs IP ne commutent que des adresses numériques binaires (32 bits en IPv4 comme "
                    "`196.20.45.12`, 128 bits en IPv6), le résolveur du système d'exploitation traduit le nom symbolique "
                    "`api.isgp.dz` en adresse IP cible, tandis que le nom réservé `localhost` est résolu instantanément par "
                    "`/etc/hosts` vers la boucle interne **`127.0.0.1`** sans solliciter de câble physique.\n\n"
                    "#### Démultiplexage par Port TCP (1 à 65535) et chiffrement TLS\n\n"
                    "Si l'adresse IP désigne l'immeuble serveur, un même hôte Linux exécute simultanément PostgreSQL (`:5432`), "
                    "SSH (`:22`), Nginx (`:443`) et plusieurs instances Tornado (`:8001..8004`). C'est le **numéro de Port TCP** "
                    "(entier non signé sur 16 bits) qui permet au noyau Linux d'aiguiller les segments entrants vers la file "
                    "d'écoute (`accept queue`) du bon processus Python après la poignée de main fiable en trois temps (`SYN`, "
                    "`SYN-ACK`, `ACK`). En production sous `https://`, une poignée de main cryptographique **TLS 1.3** s'intercale "
                    "immédiatement au-dessus de TCP pour authentifier le certificat X.509 du serveur et chiffrer l'intégralité "
                    "de la trame HTTP (URI complète, en-têtes `Authorization` et corps JSON) contre toute interception."
                )
            },
            {
                "heading": "2. Liaison de Socket Système (`bind`) : `127.0.0.1` vs `0.0.0.0` dans `app.listen()`",
                "body": (
                    "Lorsque votre script appelle `app.listen(8888, address=...)`, `tornado.netutil.bind_sockets()` invoque "
                    "l'appel système POSIX `bind()` pour attacher un socket en mode non bloquant (`SOCK_NONBLOCK`) à une "
                    "interface réseau précise de la machine. Le choix de l'adresse de liaison détermine directement le "
                    "périmètre d'exposition réseau de votre démon.\n\n"
                    "```python — Différence de liaison noyau entre boucle locale isolée et écoute globale\n"
                    "# 1. Développement strictement local ou derrière un Nginx sur la même machine :\n"
                    "app.listen(8888, address=\"127.0.0.1\")  # Rejette tout paquet arrivant par eth0/wlan0\n\n"
                    "# 2. Conteneur Docker ou démon exposé sur le réseau local (INADDR_ANY) :\n"
                    "app.listen(8888, address=\"0.0.0.0\")    # Écoute sur toutes les interfaces IPv4 actives\n"
                    "```\n\n"
                    "> [!WARNING] Le piège classique des conteneurs Docker muets\n"
                    "> À l'intérieur d'un conteneur Docker, l'interface `127.0.0.1` est isolée dans l'espace réseau privé "
                    "(*network namespace*) du conteneur lui-même ! Si Tornado écoute sur `127.0.0.1` dans un conteneur, même "
                    "la redirection de port `-p 8888:8888` depuis la machine hôte échouera avec `Connection reset by peer`. "
                    "Dans un conteneur, liez toujours Tornado à `0.0.0.0`, et en production sur machine virtuelle, liez les "
                    "nœuds Tornado à `127.0.0.1:8001..8004` derrière un frontal Nginx seul exposé sur `0.0.0.0:443`."
                )
            },
            {
                "heading": "3. Anatomie Normative d'une URI (RFC 3986) et Accesseurs `HTTPServerRequest` dans Tornado",
                "body": (
                    "Codifiée par Tim Berners-Lee et Roy Fielding dans l'**IETF RFC 3986**, toute URI respecte la grammaire "
                    "`scheme://authority/path?query#fragment`, dont chaque composant possède un point d'entrée dédié sur "
                    "l'objet `self.request` (`tornado.httputil.HTTPServerRequest`) d'un `RequestHandler`.\n\n"
                    "Le `scheme` (`http` ou `https`, lu via `self.request.protocol`) et l'`authority` (`api.isgp.dz:8443`, lue "
                    "via `self.request.host`) identifient le canal et l'hôte virtuel. Le `path` hiérarchique (`/api/v1/formations`, "
                    "exposé purgé de sa query string dans `self.request.path`) est la seule chaîne comparée aux expressions "
                    "régulières de `tornado.web.Application`. En aval du délimiteur `?`, la `query` transporte des paires "
                    "clé-valeur encodées en pourcentage (`%20`) que Tornado décode paresseusement en UTF-8 via "
                    "`self.get_query_argument('salle', default=None)` (ou en liste via `self.get_query_arguments('tag')` "
                    "lorsqu'une clé est répétée `?tag=python&tag=async`). Enfin, le `fragment` situé après `#` est une ancre "
                    "purement locale au navigateur qui n'est **jamais transmise** sur le socket TCP."
                )
            }
        ],
        "architecture_diagram": (
            "ANATOMIE D'UNE URI (RFC 3986) :\n"
            "  https://api.isgp.dz:8443/api/v1/formations?salle=Alger&page=2#details\n"
            "  \\___/   \\_________/ \\__/\\________________/ \\________________/ \\_____/\n"
            "    |          |        |          |                  |            |\n"
            "  Scheme     Host     Port       Path           Query String    Fragment\n"
            " (TLS/HTTP) (DNS/IP)  (TCP) (Routeur Regex)  (get_query_arg)  (Navigateur)\n\n"
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
                ["Port `:8888` / `:8000`", "Ports historiques Tornado / Python", "Ports utilisateurs (> 1024, ne nécessitent pas les droits administrateur `root`)"],
                ["Port `:5432` / `:3306`", "PostgreSQL / MySQL", "Ports d'écoute des serveurs de bases de données SQL"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écouter uniquement sur `address=\"127.0.0.1\"` dans un conteneur Docker ou pour un test en salle",
                "good": "Spécifier `app.listen(8888, address=\"0.0.0.0\")`",
                "why": "Dans un conteneur ou sur un réseau local, écouter uniquement sur `127.0.0.1` rejette toute connexion venant de l'extérieur."
            },
            {
                "bad": "Lancer deux fois `python app.py` sur le même port `8888` (`OSError: [Errno 98] Address already in use`)",
                "good": "Arrêter le premier processus (`Ctrl+C`) ou choisir un port libre (`PORT=8889`)",
                "why": "Un numéro de port TCP sur une même adresse IP ne peut être attribué qu'à un seul serveur à la fois."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_1/03_analyseur_uri_et_reseau.py` ci-dessus, puis ajoutez un caractère accentué et un espace dans le dictionnaire passé à `tornado.httputil.url_concat` pour observer l'encodage RFC 3986 automatique (`%C3%A9`, `+`).",
            "Retirez le segment explicite `:8443` de l'URI analysée et vérifiez que `composants.port` retourne `None`, illustrant la convention du port implicite `443` attaché au schéma `https`."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.3 : TRAME BRUTE HTTP/1.1 & EN-TÊTES STRATÉGIQUES
    # =========================================================================
    "d1-l3": {
        "context": (
            "Une fois la poignée de main TCP achevée entre le client et le démon `tornado.httpserver.HTTPServer`, quels "
            "octets exacts franchissent la carte réseau ? Loin d'être un flux binaire hermétique réservé aux analyseurs "
            "Wireshark, **HTTP/1.1 (IETF RFC 9112)** est un protocole textuel d'une limpidité exemplaire où chaque ligne "
            "de métadonnées est ponctuée par la séquence `CRLF` (`\\r\\n`).\n\n"
            "Comprendre comment l'`IOStream` non bloquant de Tornado détecte la frontière `\\r\\n\\r\\n`, dimensionne sa "
            "lecture d'octets via `Content-Length` et exploite la sémantique sans état (*Stateless*) des en-têtes et "
            "des codes de statut RFC 9110 transforme radicalement votre capacité à diagnostiquer n'importe quelle "
            "anomalie d'intégration en production."
        ),
        "deep_sections": [
            {
                "heading": "1. L'Invariant « Sans État » (*Stateless*) de HTTP et l'Scalabilité Horizontale",
                "body": (
                    "La contrainte architecturale la plus féconde du protocole HTTP réside dans son caractère strictement "
                    "**sans état (*Stateless*)** : au niveau protocolaire, chaque paire requête/réponse constitue une "
                    "transaction autonome et auto-contenue. Le serveur n'entretient aucune mémoire implicite en RAM de la "
                    "requête précédente du même client — un principe que Tornado matérialise physiquement en allouant une "
                    "instance vierge de `RequestHandler` à chaque requête avant de la détruire sitôt `on_finish()` achevé.\n\n"
                    "> [!NOTE] Connexion TCP persistante (`Keep-Alive`) != Session applicative avec état\n"
                    "> Ne confondez jamais la persistance de transport et l'état applicatif : en HTTP/1.1, Tornado maintient "
                    "par défaut le socket TCP ouvert entre deux requêtes consécutives (`Connection: keep-alive`) pour économiser "
                    "le coût d'une nouvelle poignée de main TCP/TLS, mais les deux requêtes HTTP qui empruntent ce même tuyau "
                    "demeurent logiquement indépendantes et peuvent, derrière un répartiteur Nginx, être routées vers deux "
                    "processus Tornado distincts (`:8001` puis `:8003`). Chaque requête doit donc transporter dans ses "
                    "propres en-têtes l'intégralité de son contexte (`Authorization`, `Content-Type`, `Accept`, `X-Request-ID`)."
                )
            },
            {
                "heading": "2. Découpage par `IOStream` : Délimiteur `\\r\\n\\r\\n` et Piège d'Octets UTF-8 de `Content-Length`",
                "body": (
                    "Sur un socket non bloquant, les paquets TCP arrivent par fragments arbitraires au gré du MTU réseau. "
                    "Pour reconstituer un message HTTP/1.1 complet sans jamais bloquer l'`IOLoop`, le composant interne "
                    "`tornado.iostream.IOStream` invoque `read_until(b\"\\r\\n\\r\\n\", max_bytes=max_header_size)`. Cette "
                    "séquence précise de quatre octets (`0x0D 0x0A 0x0D 0x0A`, soit une ligne strictement vide) marque la "
                    "frontière physique universelle entre la fin des en-têtes HTTP et le premier octet du corps de la requête.\n\n"
                    "```http — Anatomie exacte sur le fil d'une requête POST reçue par TornadoServer\n"
                    "POST /api/v1/formations HTTP/1.1\r\n"
                    "Host: api.isgp.dz\r\n"
                    "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...\r\n"
                    "Content-Type: application/json; charset=utf-8\r\n"
                    "Content-Length: 49\r\n"
                    "\r\n"
                    "{\"titre\": \"Sécurité des APIs\", \"jours\": 5}\n"
                    "```\n\n"
                    "#### Pourquoi `Content-Length` mesure des octets (`bytes`) et jamais des caractères (`str`)\n\n"
                    "Sitôt l'en-tête analysé, `HTTP1Connection` lit exactement le nombre d'octets annoncé par `Content-Length` "
                    "via `stream.read_bytes(content_length)` et les dépose dans `self.request.body`. En encodage UTF-8, un "
                    "caractère ASCII standard occupe 1 octet, mais chaque lettre accentuée française (`é`, `è`, `à`, `ê`) est "
                    "codée sur **2 octets** (et un symbole hors BMP sur 4 octets) : la chaîne `\"Sécurité\"` compte 8 caractères "
                    "(`len(s) == 8`) mais pèse **10 octets** sur le réseau (`len(s.encode('utf-8')) == 10`). Un client bas "
                    "niveau qui renseignerait `Content-Length: 8` au lieu de `10` tronquerait les deux derniers octets du JSON "
                    "et déclencherait un `JSONDecodeError` immédiat côté Tornado."
                )
            },
            {
                "heading": "3. Sémantique Normative des Classes de Statut HTTP (RFC 9110) et `self.set_status()`",
                "body": (
                    "Le code numérique à trois chiffres inscrit sur la première ligne de réponse (`HTTP/1.1 201 Created`, "
                    "commandé dans Tornado par `self.set_status(201)`) constitue le contrat de routage primaire de tous les "
                    "équipements intermédiaires (passerelles API, CDN, sondes Prometheus, SDK mobiles).\n\n"
                    "> « Le premier chiffre du code de statut définit la classe de réponse ; les deux derniers n'ont pas de "
                    "rôle de catégorisation mais précisent la condition exacte rencontrée. » — IETF RFC 9110, Section 15 "
                    "(Status Codes)\n\n"
                    "La classe **`2xx`** certifie que l'intention du client a abouti (`200 OK` avec charge utile, `201 Created` "
                    "après persistance d'une nouvelle ressource assortie de l'en-tête `Location`, `204 No Content` après une "
                    "suppression ou un pré-vol CORS sans corps). La classe **`3xx`** gouverne la redirection (`302` via "
                    "`self.redirect()`) et l'économie de bande passante par cache conditionnel (`304 Not Modified` émis "
                    "automatiquement par Tornado lorsque l'`If-None-Match` du client coïncide avec l'`Etag` de la réponse). "
                    "Enfin, la frontière entre **`4xx`** et **`5xx`** sépare la responsabilité contractuelle : un `4xx` atteste "
                    "que le démon Tornado est parfaitement sain mais rejette une requête cliente défectueuse (`400`, `401`, "
                    "`403`, `404`, `405`, `409`, `413`, `422`, `429`), tandis qu'un `5xx` signale une défaillance de "
                    "l'infrastructure serveur ou d'un partenaire amont (`500`, `502`, `503`, `504`) déclenchant les alertes "
                    "d'astreinte."
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
            "headers": ["Code HTTP", "Nom Officiel", "Catégorie", "Signification exacte et quand le renvoyer (`self.set_status`)"],
            "rows": [
                ["**`200 OK`**", "OK", "2xx Succès", "Requête `GET`, `PUT` ou `PATCH` réussie avec corps JSON en réponse"],
                ["**`201 Created`**", "Created", "2xx Succès", "Nouvelle ressource créée avec succès suite à un `POST`"],
                ["**`204 No Content`**", "No Content", "2xx Succès", "Action réussie (souvent `DELETE` ou `OPTIONS`) ne renvoyant aucun corps"],
                ["**`400 Bad Request`**", "Bad Request", "4xx Client", "Syntaxe JSON mal formée ou paramètre d'URL illisible"],
                ["**`401 Unauthorized`**", "Unauthorized", "4xx Client", "**Échec AuthN** : Jeton/Clé API absent, expiré ou signature invalide"],
                ["**`403 Forbidden`**", "Forbidden", "4xx Client", "**Échec AuthZ** : Client authentifié, mais rôle/scope insuffisant"],
                ["**`404 Not Found`**", "Not Found", "4xx Client", "URL inexistante ou identifiant de ressource (`id=999`) introuvable"],
                ["**`405 Method Not Allowed`**", "Method Not Allowed", "4xx Client", "L'URL existe mais le `RequestHandler` n'implémenté pas ce verbe HTTP"],
                ["**`409 Conflict`**", "Conflict", "4xx Client", "Conflit d'état (ex: doublon d'adresse e-mail ou de code unique)"],
                ["**`413 Payload Too Large`**", "Payload Too Large", "4xx Client", "Corps de la requête dépassant la taille maximale autorisée (`max_body_size`)"],
                ["**`422 Unprocessable Entity`**", "Unprocessable Content", "4xx Client", "JSON bien formé mais violant une règle métier (ex: `duree_jours = -3`)"],
                ["**`429 Too Many Requests`**", "Too Many Requests", "4xx Client", "Quota de **Rate Limiting** dépassé sur la fenêtre de temps"],
                ["**`500 Internal Server Error`**", "Internal Server Error", "5xx Serveur", "Exception Python non gérée côté serveur (bug du code backend)"],
                ["**`502 / 503 / 504`**", "Bad Gateway / Unavailable / Timeout", "5xx Serveur", "Serveur en maintenance, base de données injoignable ou timeout amont"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Laisser le statut par défaut `200 OK` même en cas d'erreur : `self.write({\"success\": False, \"error\": \"Introuvable\"})`",
                "good": "Appeler `self.set_status(404)` avant `self.write({\"erreur\": \"Introuvable\"})`",
                "why": "Le *200 OK avec erreur cachée* est le pire anti-pattern REST : les outils de monitoring, proxies et clients HTTP croient que l'appel a réussi !"
            },
            {
                "bad": "Oublier l'en-tête `Content-Type: application/json` lors d'un `POST`",
                "good": "Toujours spécifier `Content-Type: application/json` dès qu'un corps JSON est envoyé",
                "why": "Permet au serveur de distinguer un payload JSON (`self.request.body`) d'un formulaire HTML (`self.get_body_argument`)."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_1/04_trame_http_et_headers.py` et vérifiez par le calcul pourquoi le mot `'Sécurité'` comporte 8 caractères Python mais exige 10 octets dans l'en-tête `Content-Length`.",
            "Interrogez successivement `/api/sandbox/status-demo/429` et `/api/sandbox/status-demo/403` dans le Client HTTP pour comparer la ligne de statut et les en-têtes associés."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.4 : MÉTHODES HTTP, IDEMPOTENCE & SÉRIALISATION JSON
    # =========================================================================
    "d1-l4": {
        "context": (
            "Sur un réseau physique réel — liaison cellulaire 4G/5G fluctuante, Wi-Fi saturé ou interconnexion "
            "interbancaire transfrontalière — la perte d'un paquet TCP contenant l'accusé de réception d'une réponse "
            "HTTP survient quotidiennement. Lorsqu'un client subit un `Request Timeout` sans savoir si Tornado a déjà "
            "exécuté ou non l'opération, **peut-il réémettre automatiquement la même requête sans provoquer de catastrophe "
            "métier ?**\n\n"
            "La réponse formelle à ce problème classique des systèmes distribués repose sur la propriété mathématique "
            "d'**Idempotence** codifiée par la RFC 9110. Ce chapitre établit les invariants exacts des cinq verbes "
            "`RequestHandler` (`get`, `post`, `put`, `patch`, `delete`) et formalise la structuration d'enveloppes JSON "
            "horodatées en UTC ISO 8601."
        ),
        "deep_sections": [
            {
                "heading": "1. Algèbre des Méthodes HTTP (RFC 9110) : Sûreté (*Safe*) et Idempotence (*Idempotent*)",
                "body": (
                    "La norme IETF RFC 9110 distingue deux garanties contractuelles qu'un développeur Tornado s'engage à "
                    "respecter lorsqu'il implémente les méthodes d'un `RequestHandler`. Une méthode est qualifiée de **Sûre "
                    "(*Safe*, Section 9.2.1)** lorsque sa sémantique est exclusivement consultative et ne produit aucune "
                    "mutation d'état observable sur le serveur (`GET`, `HEAD`, `OPTIONS`) — les écritures passives de journaux "
                    "d'accès dans `on_finish()` restant permises.\n\n"
                    "> « Une méthode de requête est dite idempotente si l'effet escompté sur le serveur de plusieurs requêtes "
                    "identiques avec cette méthode est le même que l'effet d'une seule de ces requêtes. » "
                    "— IETF RFC 9110, Section 9.2.2 (Idempotent Methods)\n\n"
                    "#### Conséquence directe sur les politiques de réessai automatique (*Retry*)\n\n"
                    "En notation fonctionnelle, une transformation `f` est idempotente si `f(f(x)) == f(x)`. Ainsi, `def get(self)` "
                    "est à la fois sûre et idempotente. La méthode `def put(self, id)` (remplacer intégralement l'état de la "
                    "ressource `#1` par un document donné) et la méthode `def delete(self, id)` (supprimer la ressource `#1`) ne "
                    "sont pas sûres puisqu'elles modifient la base SQL, mais elles sont **intrinsèquement idempotentes** : "
                    "même si la seconde exécution d'un `DELETE` renvoie `404 Not Found` après un premier `204 No Content`, "
                    "l'état résultant des données sur le serveur demeure identique (la ressource `#1` n'existe plus). À "
                    "l'opposé, **`def post(self)` n'est jamais idempotente par défaut** : rejouer trois fois un `POST` "
                    "suite à un timeout réseau insère trois commandes distinctes ou débite trois fois le client, rendant "
                    "impératif l'emploi d'un en-tête `Idempotency-Key` étudié au Jour 3."
                )
            },
            {
                "heading": "2. Pipeline `tornado.escape` : Encodage et Décodage JSON Haute Performance",
                "body": (
                    "La mémoire vive Python manipule des graphes d'objets typés (`dict`, `list`, `bool`, `None`), tandis que "
                    "l'`IOStream` réseau ne transporte que des tampons d'octets contigus (`bytes`). Le module natif "
                    "`tornado.escape` assure le pont bidirectionnel entre ces deux mondes en s'appuyant sur l'encodeur C "
                    "optimisé du module standard `json`.\n\n"
                    "```python — Symétrie entre désérialisation entrante et sérialisation sortante dans Tornado\n"
                    "# 1. Lecture entrante : accepte directement bytes (UTF-8) ou str\n"
                    "charge_entrante = tornado.escape.json_decode(self.request.body)\n\n"
                    "# 2. Écriture sortante : sérialise en UTF-8 + pose Content-Type: application/json\n"
                    "self.write({\"meta\": {\"version\": \"1.0\"}, \"data\": charge_entrante})\n"
                    "```\n\n"
                    "Notez la distinction fondamentale dans la bibliothèque standard Python entre les fonctions suffixées par "
                    "`s` (*string* en mémoire : `json.dumps()` et `json.loads()`) et leurs homologues sans `s` (`json.dump()` "
                    "et `json.load()`) qui opèrent sur des descripteurs de fichiers disque bloquants — ces derniers ne devant "
                    "jamais être appelés directement sur le thread de l'`IOLoop`."
                )
            },
            {
                "heading": "3. Architecture d'Enveloppe JSON (`meta` / `data`) et Horodatage Universel ISO 8601 UTC",
                "body": (
                    "Sur une API d'entreprise appelée à évoluer sur plusieurs années, retourner des champs métier à plat sans "
                    "séparation structurelle empêche d'introduire proprement la pagination, le temps d'exécution ou les "
                    "avertissements de dépréciation. Le patron d'enveloppe standard compartimente la charge utile en deux "
                    "espaces de noms racine : **`\"meta\"`** pour les métadonnées techniques du transport et **`\"data\"`** "
                    "pour l'entité ou la collection métier.\n\n"
                    "#### L'impératif absolu d'ISO 8601 en temps universel coordonné (`Z`)\n\n"
                    "Ne transmettez jamais de dates ambiguës localisées telles que `\"08/11/2026\"` (interprétée le 8 novembre "
                    "à Alger ou Paris, mais le 11 août à New York !). Toute API professionnelle normalise ses horodatages en "
                    "**UTC selon la norme ISO 8601 / RFC 3339 (`2026-11-08T17:30:00Z`)**, générée en Python moderne via "
                    "`datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')`. Ce format possède la propriété remarquable "
                    "d'être **lexicographiquement triable** : un simple tri alphabétique correspond exactement à l'ordre "
                    "chronologique universel."
                )
            }
        ],
        "architecture_diagram": (
            "CYCLE DE SÉRIALISATION / DÉSÉRIALISATION ENTRE DEUX SYSTÈMES :\n"
            "  [Mémoire Serveur Tornado]               [Câble Réseau HTTP]                [Mémoire Client (Python/JS)]\n"
            "   dict {'actif': True, 'fin': None}  -->  self.write(dict) (UTF-8)     -->  json_decode() / JSON.parse()\n"
            "                                       \"{\\\"actif\\\": true, \\\"fin\\\": null}\""
        ),
        "reference_table": {
            "title": "Matrice de Sémantique et d'Idempotence des Méthodes HTTP (RFC 9110)",
            "headers": ["Méthode HTTP", "Méthode Tornado", "Corps (Body) en Requête ?", "Sûre (Safe) ?", "Idempotente ?", "Réessai automatique sans risque en cas de coupure ?"],
            "rows": [
                ["**`GET`**", "`def get(self)`", "Non (Jamais)", "**Oui**", "**Oui**", "**Oui** (100% sûr)"],
                ["**`PUT`**", "`def put(self, id)`", "Oui (JSON complet)", "Non", "**Oui**", "**Oui** (Écrase avec le même état final)"],
                ["**`DELETE`**", "`def delete(self, id)`", "Non", "Non", "**Oui**", "**Oui** (L'élément reste supprimé)"],
                ["**`PATCH`**", "`def patch(self, id)`", "Oui (Champs modifiés)", "Non", "Selon implémentation", "Prudence (Idempotent si affectation de valeur)"],
                ["**`POST`**", "`def post(self)`", "Oui (JSON)", "Non", "**NON !**", "**NON** (Risque de doublon sauf avec `Idempotency-Key`)"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Utiliser une route `GET /api/formations/supprimer?id=1` qui modifie ou supprime des données",
                "good": "Implémenter la méthode `def delete(self, id):` sur `/api/formations/1` pour toute suppression",
                "why": "Les navigateurs, robots d'indexation et proxys préchargent parfois les liens `GET` automatiquement : si votre `GET` supprime des données, votre base sera vidée par accident !"
            },
            {
                "bad": "Confondre `json.load(fichier)` (sans `s`) et `json.loads(chaine)` / `tornado.escape.json_decode(bytes)`",
                "good": "Utiliser `tornado.escape.json_decode(self.request.body)` ou `json.loads()` pour les flux réseau",
                "why": "`load` et `dump` sans `s` lisent/écrivent un fichier sur disque, tandis que `json_decode`, `loads` et `dumps` opèrent en mémoire."
            }
        ],
        "practical_exercises": [
            "Exécutez `day_1/02_serialisation_json.py` et constatez comment `None` et `True` sont projetés en `null` et `true` conformes à la RFC 8259 tout en préservant les caractères accentués grâce à `ensure_ascii=False`.",
            "Insérez une clé `\"modules\": [\"HTTP/1.1\", \"IOLoop\", \"Sécurité\"]` dans `data`, sérialisez l'enveloppe, puis extrayez le deuxième module après désérialisation par `tornado.escape.json_decode()`."
        ]
    },

    # =========================================================================
    # JOUR 1 — CHAPITRE 1.5 : MAÎTRISER CURL, POSTMAN, HTTPIE & REST CLIENT
    # =========================================================================
    "d1-l5": {
        "context": (
            "Comment éprouver méthodiquement un endpoint Tornado exigeant un verbe `POST` ou `DELETE`, une charge utile "
            "JSON typée et un jeton `Authorization: Bearer <token>`, alors que la barre d'adresse d'un navigateur Web "
            "ne sait émettre que des requêtes `GET` nues ?\n\n"
            "Un ingénieur backend ne développe jamais à l'aveugle derrière une interface graphique intermédiaire qui "
            "pourrait masquer ses propres bugs : il forge et observe directement les trames HTTP. Lors d'un diagnostic "
            "de production en session SSH sur un serveur Linux distant ou dans un pipeline CI/CD, **`curl`** demeure "
            "l'instrument universel absolu ; sur le poste d'ingénierie, il s'articule avec **Postman / Bruno**, **HTTPie** "
            "et les cahiers de requêtes versionnés **`.http`**."
        ),
        "deep_sections": [
            {
                "heading": "1. Pourquoi `curl` Demeure l'Étalon-Or du Diagnostic Réseau en Production",
                "body": (
                    "Initié en 1997 par Daniel Stenberg, **`curl` (*Client for URL*)** équipe nativement chaque distribution "
                    "Linux d'entreprise, macOS, Windows 10/11 et la quasi-totalité des images conteneurisées de production. "
                    "Lorsqu'un incident critique éclate à deux heures du matin derrière un répartiteur Nginx, l'ingénieur "
                    "connecté en SSH ne dispose d'aucune fenêtre graphique : en une seule commande `curl -i` ou `curl -v` "
                    "ciblant `http://127.0.0.1:8001`, il contourne le proxy pour interroger directement le nœud Tornado "
                    "suspect et vérifier en une seconde son code HTTP, sa signature `Server: TornadoServer` et son `Etag`.\n\n"
                    "#### Reproductibilité universelle et partage d'incidents\n\n"
                    "Au-delà du dépannage d'urgence, une commande `curl` constitue la spécification exécutable la plus concise "
                    "au monde : collée dans un rapport d'anomalie, un message d'équipe ou un test d'intégration Bash, elle "
                    "permet à n'importe quel interlocuteur de rejouer exactement la même trame octet pour octet."
                )
            },
            {
                "heading": "2. Radiographier une Session Réseau avec `curl -v` : Les Préfixes `*`, `>` et `<`",
                "body": (
                    "Invoquer le mode verbeux `curl -v` dévoile chronologiquement les trois actes du dialogue entre le client "
                    "et le serveur `HTTPServer` de Tornado au moyen d'un code de préfixes à trois symboles qu'il faut savoir "
                    "lire instantanément.\n\n"
                    "```bash — Lecture d'une trace complète curl -v face à un démon Tornado\n"
                    "$ curl -v --json '{\"identifiant\":\"stagiaire\",\"mot_de_passe\":\"isgp2026\"}' \\\n"
                    "       \"http://127.0.0.1:8888/api/sandbox/auth/token\"\n"
                    "*   Trying 127.0.0.1:8888...\n"
                    "* Connected to 127.0.0.1 (127.0.0.1) port 8888 (#0)\n"
                    "> POST /api/sandbox/auth/token HTTP/1.1\n"
                    "> Host: 127.0.0.1:8888\n"
                    "> Content-Type: application/json\n"
                    "> Accept: application/json\n"
                    "> Content-Length: 54\n"
                    ">\n"
                    "< HTTP/1.1 200 OK\n"
                    "< Server: TornadoServer/6.4\n"
                    "< Content-Type: application/json; charset=UTF-8\n"
                    "< Content-Length: 148\n"
                    "<\n"
                    "{\"access_token\": \"eyJ...\", \"token_type\": \"Bearer\"}\n"
                    "```\n\n"
                    "Les lignes introduites par l'astérisque **`*`** journalisent les opérations internes de la bibliothèque "
                    "`libcurl` (résolution DNS, ouverture du socket TCP, négociation des suites cryptographiques TLS). Les "
                    "lignes précédées du chevron sortant **`>`** exposent les en-têtes exacts émis par le client sur le fil, "
                    "tandis que les lignes marquées du chevron entrant **`<`** restituent la ligne de statut et les en-têtes "
                    "renvoyés par Tornado juste avant l'affichage du corps JSON.\n\n"
                    "> [!TIP] L'option moderne `--json` de `curl` (version 7.82+)\n"
                    "> Historiquement, omettre `-H \"Content-Type: application/json\"` avec `-d '{...}'` piégeait les "
                    "développeurs car `curl` expédiait alors par défaut `application/x-www-form-urlencoded` ! Sur toutes les "
                    "versions récentes de `curl`, le drapeau unique `--json '{...}'` positionne simultanément `-X POST`, "
                    "`Content-Type: application/json` et `Accept: application/json`."
                )
            },
            {
                "heading": "3. Outillage Collaboratif : Collections Postman/Bruno, HTTPie et Fichiers `.http`",
                "body": (
                    "Lorsqu'un projet d'API dépasse la vingtaine de routes sécurisées, taper manuellement les jetons JWT à "
                    "chaque essai ralentit l'équipe. Trois outils complémentaires industrialisent le flux de travail autour "
                    "d'une application Tornado. Les ateliers graphiques tels que **Postman**, **Bruno** ou **Insomnia** "
                    "organisent les appels en **collections structurées** couplées à des **environnements** (`Local :8888`, "
                    "`Staging`, `Production`) capables de capturer automatiquement l'`access_token` d'une réponse login pour "
                    "l'injecter dans `{{bearer_token}}` sur toutes les autres routes.\n\n"
                    "En ligne de commande interactive, **HTTPie (`http`)** remplace avantageusement la syntaxe de guillemets "
                    "imbriqués par une notation typée intuitive (`http POST :8888/api/formations titre=\"Tornado\" duree_jours:=5`) "
                    "avec mise en couleur automatique du JSON retourné. Enfin, l'approche **Tests-as-Code par fichiers `.http`** "
                    "(extension *REST Client* de VS Code / Antigravity IDE) archive vos scénarios de requêtes séparés par `###` "
                    "directement dans le dépôt Git : chaque révision de code (`Pull Request`) embarque ainsi ses propres "
                    "requêtes de vérification dans le même commit que le `RequestHandler` modifié."
                )
            }
        ],
        "architecture_diagram": (
            "LECTURE D'UNE TRACE DIAGNOSTIC 'curl -v' :\n"
            "  * Trying 127.0.0.1:8888...                  <-- [*] Connexion TCP ouverte par curl\n"
            "  * Connected to 127.0.0.1 (127.0.0.1) port 8888\n"
            "  > POST /api/sandbox/auth/token HTTP/1.1     <-- [>] En-têtes ENVOYÉS par le client\n"
            "  > Host: 127.0.0.1:8888\n"
            "  > Content-Type: application/json\n"
            "  > Content-Length: 52\n"
            "  <\n"
            "  < HTTP/1.1 200 OK                           <-- [<] En-têtes REÇUS depuis Tornado\n"
            "  < Content-Type: application/json; charset=UTF-8\n"
            "  {\"access_token\": \"eyJ...\"}                  <-- Corps JSON de la réponse"
        ),
        "reference_table": {
            "title": "Synthèse des Commandes `curl` les Plus Utilisées au Quotidien",
            "headers": ["Objectif de test", "Commande `curl` complète", "Options clés utilisées"],
            "rows": [
                ["**Lire + voir les Headers**", "`curl -i http://127.0.0.1:8888/api/sandbox/formations`", "`-i` (inclut statut + en-têtes)"],
                ["**Créer en `POST` JSON**", "`curl -i -X POST -H \"Content-Type: application/json\" -d '{\"titre\":\"API\"}' http://127.0.0.1:8888/api/sandbox/formations`", "`-X POST`, `-H`, `-d`"],
                ["**Raccourci JSON moderne**", "`curl -i --json '{\"titre\":\"API\"}' http://127.0.0.1:8888/api/sandbox/formations`", "`--json` (`curl 7.82+`)"],
                ["**Modifier (`PUT` / `PATCH`)**", "`curl -i -X PATCH -H \"Content-Type: application/json\" -d '{\"salle\":\"B\"}' http://127.0.0.1:8888/api/sandbox/formations/1`", "`-X PATCH`"],
                ["**Supprimer (`DELETE`)**", "`curl -i -X DELETE http://127.0.0.1:8888/api/sandbox/formations/1`", "`-X DELETE`"],
                ["**Envoyer un `Bearer Token`**", "`curl -i -H \"Authorization: Bearer <TOKEN>\" http://127.0.0.1:8888/api/sandbox/auth/profil`", "`-H \"Authorization: Bearer ...\"`"],
                ["**Diagnostic complet**", "`curl -v --connect-timeout 3 -m 10 http://127.0.0.1:8888/api/sandbox/bonjour`", "`-v`, `--connect-timeout`, `-m`"]
            ]
        },
        "pitfalls": [
            {
                "bad": "Écrire `curl -X POST -d '{\"titre\": \"API\"}' URL` en oubliant `-H \"Content-Type: application/json\"`",
                "good": "Toujours ajouter `-H \"Content-Type: application/json\"` (ou utiliser `--json`)",
                "why": "Par défaut, `-d` dans `curl` envoie l'en-tête `application/x-www-form-urlencoded` (formulaire HTML) et non `application/json` !"
            },
            {
                "bad": "Passer une URL contenant `&` sans guillemets dans le terminal : `curl http://localhost:8888/api?page=1&limit=2`",
                "good": "Toujours entourer l'URL de guillemets doubles : `curl \"http://localhost:8888/api?page=1&limit=2\"`",
                "why": "Dans un terminal Linux/macOS/Windows, le caractère `&` hors guillemets coupe la commande et met `curl` en arrière-plan en ignorant `&limit=2` !"
            }
        ],
        "practical_exercises": [
            "Exécutez `day_1/05_outils_curl_postman_httpie.py` ci-dessus afin d'inspecter les en-têtes `Server: TornadoServer` et `Etag` émis en direct sur les quatre requêtes `curl -i`.",
            "Basculez dans l'onglet **curl & Postman** de la barre supérieure pour éprouver en direct le pré-vol CORS, l'authentification `X-API-Key` et le chronométrage détaillé `-w`.",
            "Téléchargez la Collection Postman (`.json`) et le cahier `.http` depuis l'onglet **curl & Postman** pour examiner leur structure JSON et RFC 9112."
        ]
    }
}
