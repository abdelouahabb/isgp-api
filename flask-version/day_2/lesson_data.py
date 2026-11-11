import os

BASE_DIR = os.path.dirname(__file__)


def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()


DAY_2_DATA = {
    "day_number": 2,
    "folder": "day_2",
    "badge": "Jour 2 • Design RESTful, Flask, Templates Jinja2 & Formulaires Web",
    "title": "Prise en Main de Flask : Serveur WSGI, Templates Jinja2 (render_template), Formulaires HTML (request.form), Routage, Pagination & Middlewares",
    "goal": "Comprendre le cycle WSGI de Flask, séparer proprement la logique Python des pages HTML grâce au moteur de templates Jinja2 (render_template), traiter les formulaires HTML (request.form et request.files), maîtriser les paramètres de route (<variable> vs :variable vs {variable}), implémenter la pagination/filtrage/tri et mettre en place des middlewares d'audit.",
    "starter_filename": "day_2/05_jinja_et_formulaires_html.py",
    "files": [
        "day_2/01_serveur_minimal_flask.py",
        "day_2/02_routes_et_parametres.py",
        "day_2/05_jinja_et_formulaires_html.py",
        "day_2/03_pagination_filtrage_tri.py",
        "day_2/04_middlewares_et_audit_log.py",
    ],
    "lessons": [
        {
            "id": "d2-l1",
            "file": "day_2/01_serveur_minimal_flask.py",
            "title": "2.1 — Premiers Pas avec Flask : Serveur WSGI, Rendu de Templates Jinja2 (`render_template`) vs API REST (`jsonify`) & Modèle de Richardson",
            "duration": "55 min",
            "analogy": {
                "title": "Organiser les rayons d'une bibliothèque par noms de collections plutôt que par phrases d'action",
                "text": "Une erreur récurrente chez les débutants consiste à baptiser les URLs comme des appels de procédures RPC (`/getAllFormations`, `/createNewFormation`, `/deleteFormationById?id=4`) ou à concaténer des chaînes HTML directement dans le code Python.\n\nDans une architecture Flask bien conçue, les vues destinées aux navigateurs délèguent le rendu aux gabarits du répertoire **`templates/`** via **`render_template('accueil.html', ...)`**, tandis que les routes d'API RESTful ciblent **exclusivement des noms de ressources au pluriel (`/api/v1/modules`)** et émettent une charge utile normalisée grâce à **`jsonify(...)`**."
            },
            "explanation": [
                "**Dualité native de Flask : rendu HTML Jinja2 et sérialisation API `jsonify()`.** Lorsqu'un point d'entrée sert une interface humaine, Flask s'interdit tout HTML codé en dur dans le fichier `.py` et invoque `render_template('accueil.html', organisme='ISGP', modules=...)` qui retourne un flux `text/html; charset=utf-8`. Lorsqu'il expose un contrat machine-à-machine, l'appel `jsonify({'message': '...', 'statut': 'actif'}), 200` instancie un objet `Response` Werkzeug encodé en UTF-8 et muni automatiquement de l'en-tête `Content-Type: application/json`.",
                "**Échelle de maturité de Leonard Richardson (Niveaux 0 à 3).** Le niveau 0 (*Swamp of POX*) concentre toutes les opérations sur un tunnel unique `POST /api`, tandis que le niveau 1 introduit des URIs distinctes par entité métier (`/api/formations`, `/api/formations/12`). Le **niveau 2**, cible industrielle de référence, combine ces ressources avec la sémantique exacte des verbes HTTP (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) et des codes de statut (`200`, `201`, `400`, `404`, `429`), avant un éventuel niveau 3 (*HATEOAS*) enrichissant les réponses de liens hypermédias de navigation.",
                "**Conventions industrielles de nommage d'URI et interface WSGI (`PEP 3333`).** Une taxonomie d'URI rigoureuse emploie exclusivement des substantifs pluriels en minuscules séparés par des tirets *kebab-case* (`/api/v1/sessions-formation`), exprime l'appartenance par imbrication hiérarchique (`/api/v1/formations/12/stagiaires`) et préfixe le contrat d'une version explicite (`/api/v1/...`). Sous le capot, `app = Flask(__name__)` instancie un objet appelable (*callable*) strictement conforme à la spécification Python **WSGI (`PEP 3333`)**, prêt à être orchestré par Gunicorn."
            ],
            "code": _read("01_serveur_minimal_flask.py"),
            "line_explanations": [
                {"lines": "11-12", "text": "Création de l'instance WSGI Flask pointant vers le sous-dossier `day_2/templates/`."},
                {"lines": "24-32", "text": "Route Web `/accueil` : appelle `render_template('accueil.html', ...)` pour injecter les variables Python dans le gabarit HTML Jinja2 (zéro HTML codé en dur)."},
                {"lines": "36-43", "text": "Route API `/api/bonjour` : retourne un dictionnaire converti en JSON par `jsonify()` avec le code HTTP `200`."},
                {"lines": "47-52", "text": "Route RESTful de collection `/api/v1/modules` (nom au pluriel + version `/api/v1`)."},
                {"lines": "55-68", "text": "Exécution immédiate comparant la sortie HTML Jinja2 (`/accueil`) et la sortie API JSON (`/api/bonjour`)."}
            ],
            "sandbox_preset": {
                "label": "Tester la route GET /api/sandbox/bonjour",
                "method": "GET",
                "url": "/api/sandbox/bonjour",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_2/01_serveur_minimal_flask.py` pour observer le rendu du template Jinja2 (`day_2/templates/accueil.html`) et la réponse JSON (`/api/bonjour`) :",
                "initial_code": _read("01_serveur_minimal_flask.py")
            },
            "vscode_instructions": {
                "filename": "day_2/01_serveur_minimal_flask.py",
                "steps": [
                    "Inspecter `day_2/01_serveur_minimal_flask.py` et son template HTML `day_2/templates/accueil.html`.",
                    "Exécuter `.venv/bin/python day_2/01_serveur_minimal_flask.py` (ou ajouter `--serve` pour démarrer sur le port 5001)."
                ]
            }
        },
        {
            "id": "d2-l2",
            "file": "day_2/02_routes_et_parametres.py",
            "title": "2.2 — Routage Dynamique (`<variable>` vs `:variable` vs `{variable}`), Convertisseurs `<int:id>` & Objet `request`",
            "duration": "55 min",
            "analogy": {
                "title": "Le contrôleur de guichet qui filtre automatiquement le format du numéro de dossier",
                "text": "Lorsqu'un guichet administratif exige un numéro de dossier numérique (`/api/v1/stagiaires/1`) et qu'un usager présente la mention alphabétique `/api/v1/stagiaires/bonjour`, le routeur `MapAdapter` de Werkzeug écarte immédiatement la requête avec un code `404 Not Found` grâce au convertisseur typé `<int:stagiaire_id>`, avant même que l'interpréteur Python n'invoque votre fonction de vue."
            },
            "explanation": [
                "**Convertisseurs de chemin intégrés au moteur de routage Werkzeug.** Chaque règle enregistrée dans `app.url_map` accepte la syntaxe `<convertisseur:nom>` pour filtrer et typer à la volée les segments dynamiques de l'URI : `<string:nom>` (implicite par défaut) capture tout texte hors barre oblique `/`, `<int:id>` exige un entier positif et transmet directement un `int` Python à la vue, `<float:montant>` valide un nombre décimal, et `<uuid:jeton_id>` impose le format canonique d'un identifiant universel RFC 4122.",
                "**Désambiguïsation syntaxique entre `<variable>`, `:variable` et `{variable}`.** Les chevrons `<int:stagiaire_id>` constituent la syntaxe exclusive de **Flask et Werkzeug** côté serveur Python ; écrire `:id` dans `@app.route()` est une erreur classique héritée de **Postman** ou **Express.js** qui oblige Flask à chercher la chaîne littérale `':id'`. De leur côté, les accolades `{id}` relèvent de la spécification **OpenAPI 3.0**, de FastAPI et des *f-strings* Python, tandis qu'une commande `curl` réelle transmet toujours la valeur concrète `/api/v1/stagiaires/1`.",
                "**Encapsulation du contexte WSGI par le proxy local `flask.request`.** Pour chaque requête traitée par un worker ou un thread Gunicorn, Flask lie un *ContextVar* isolé derrière l'objet `request`. La vue inspecte ainsi sans conflit de concurrence le verbe HTTP (`request.method`), le chemin (`request.path`), les paramètres d'URL typés (`request.args.get('ht', default=1000.0, type=float)`), les champs de formulaire (`request.form`), les en-têtes insensibles à la casse (`request.headers`) et la charge JSON (`request.get_json(silent=True)`)."
            ],
            "code": _read("02_routes_et_parametres.py"),
            "line_explanations": [
                {"lines": "23-32", "text": "Paramètre de chemin `<prenom>` : Flask injecte la valeur capturée comme argument de `saluer_stagiaire(prenom)`."},
                {"lines": "36-41", "text": "Convertisseur typé `<int:stagiaire_id>` retournant la ressource en JSON (`/api/v1/stagiaires/1`)."},
                {"lines": "45-50", "text": "Même paramètre `<int:stagiaire_id>` utilisé pour rendre la fiche HTML Jinja2 `day_2/templates/fiche_stagiaire.html` via `render_template()`."},
                {"lines": "54-64", "text": "Extraction typée des paramètres de requête `?ht=...&taux=...` via `request.args.get(..., type=float)`."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/calcul-tva?ht=2500&taux=19",
                "method": "GET",
                "url": "/api/sandbox/calcul-tva?ht=2500&taux=19",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_2/02_routes_et_parametres.py` pour tester `<prenom>`, `<int:stagiaire_id>` (Jinja2 + JSON) et `request.args` :",
                "initial_code": _read("02_routes_et_parametres.py")
            },
            "vscode_instructions": {
                "filename": "day_2/02_routes_et_parametres.py",
                "steps": [
                    "Ouvrir `day_2/02_routes_et_parametres.py` et son template `day_2/templates/fiche_stagiaire.html`.",
                    "Exécuter `.venv/bin/python day_2/02_routes_et_parametres.py`."
                ]
            }
        },
        {
            "id": "d2-l5",
            "file": "day_2/05_jinja_et_formulaires_html.py",
            "title": "2.3 — Moteur de Templates Jinja2 (`render_template`) & Traitement des Formulaires Web HTML (`request.form` / `request.files`)",
            "duration": "65 min",
            "analogy": {
                "title": "Séparer le moule d'imprimerie (Template Jinja2 .html) des données de l'ordinateur (Python) et du bordereau papier rempli par l'usager (<form>)",
                "text": "Concaténer des balises HTML directement dans une fonction Python (`return '<h1>' + titre + '</h1>'`) constitue une dérive architecturale majeure qui rend le code illisible et ouvre immédiatement la porte aux injections JavaScript (**XSS**).\n\nFlask résout ce problème à la racine en isolant la présentation dans le dossier **`templates/`** propulsé par le moteur **Jinja2** (`render_template('formations.html', ...)`). Parallèlement, lorsqu'un visiteur valide un formulaire `<form method='POST'>`, le navigateur n'expédie pas une chaîne JSON mais un flux encodé que Werkzeug analyse dans **`request.form`** pour les champs texte et dans **`request.files`** pour les pièces jointes binaires."
            },
            "explanation": [
                "**Compilation des gabarits Jinja2 et échappement automatique anti-XSS.** Le moteur **Jinja2** intégré à Flask compile chaque fichier `.html` du dossier `templates/` en bytecode Python et évalue quatre constructions complémentaires : `{{ variable }}` injecte une expression en convertissant automatiquement `<`, `>`, `&` et `\"` en entités HTML inoffensives contre le *Cross-Site Scripting*, `{% for elem in liste %} ... {% endfor %}` itère sur les collections, `{% if condition %} ... {% endif %}` pilote l'affichage conditionnel, et `{# commentaire #}` documente le gabarit côté serveur sans rien transmettre sur le réseau.",
                "**Décodage des formulaires `application/x-www-form-urlencoded` dans `request.form`.** Lorsqu'un utilisateur soumet une balise `<form method='POST' action='/formations'>`, le navigateur sérialise tous les contrôles dotés d'un attribut `name` sous la forme `titre=API+Flask&duree_jours=5&salle=Salle+A` avec l'en-tête `Content-Type: application/x-www-form-urlencoded`. Sur une telle requête, `request.get_json(silent=True)` retourne légitimement `None` : la vue doit extraire les valeurs depuis la structure `ImmutableMultiDict` de Werkzeug via `request.form.get('titre')` et `request.form.get('duree_jours', type=int)`.",
                "**Flux `multipart/form-data` et assainissement par `secure_filename()`.** Dès qu'un formulaire embarque un champ `<input type='file'>`, l'attribut `enctype='multipart/form-data'` découpe le corps HTTP en sections délimitées par une frontière (*boundary*). Werkzeug maintient alors les champs scalaires dans `request.form` et expose chaque fichier sous forme d'objet `FileStorage` dans `request.files`, dont le nom d'origine doit impérativement être neutralisé par `werkzeug.utils.secure_filename()` pour bloquer toute traversée d'arborescence (`../../etc/passwd`)."
            ],
            "code": _read("05_jinja_et_formulaires_html.py"),
            "line_explanations": [
                {"lines": "17-18", "text": "Configuration explicite du dossier `day_2/templates/` contenant le gabarit Jinja2 `formations.html`."},
                {"lines": "39-44", "text": "Détection intelligente du format d'entrée : `request.form` si l'appel provient d'un formulaire HTML (`application/x-www-form-urlencoded`), ou `request.get_json()` s'il provient d'un client API JSON."},
                {"lines": "45-57", "text": "Extraction et validation serveur des champs `titre`, `duree_jours` et `salle` soumis par le formulaire."},
                {"lines": "77-83", "text": "`render_template('formations.html', ...)` injecte les variables Python dans le template Jinja2 sans aucune chaîne HTML codée en dur dans Python."},
                {"lines": "89-109", "text": "Traitement d'un formulaire `multipart/form-data` combinant `request.form` (texte) et `request.files` (fichier PDF) sécurisé par `secure_filename()`."}
            ],
            "sandbox_preset": {
                "label": "Tester POST /api/sandbox/formulaire-formation (request.form)",
                "method": "POST",
                "url": "/api/sandbox/formulaire-formation",
                "body": "titre=Atelier+Jinja2&formateur=ISGP&duree_jours=4&salle=Salle+B"
            },
            "python_runner": {
                "prompt": "Exécutez le test complet de soumission de formulaire HTML (`request.form` + rendu Jinja2 `day_2/templates/formations.html`) et d'upload `multipart/form-data` (`request.files`) :",
                "initial_code": _read("05_jinja_et_formulaires_html.py")
            },
            "vscode_instructions": {
                "filename": "day_2/05_jinja_et_formulaires_html.py",
                "steps": [
                    "Inspecter le fichier de template Jinja2 `day_2/templates/formations.html` et le script `day_2/05_jinja_et_formulaires_html.py`.",
                    "Ouvrir l'atelier interactif réel dans votre navigateur sur `http://127.0.0.1:5000/sandbox/formulaire-jinja` pour soumettre de vraies formations via `<form method='POST'>`."
                ]
            }
        },
        {
            "id": "d2-l3",
            "file": "day_2/03_pagination_filtrage_tri.py",
            "title": "2.4 — Pagination (`page`, `limit`), Filtrage Multi-Critères & Tri Dynamique sur une Collection",
            "duration": "65 min",
            "analogy": {
                "title": "Ne jamais envoyer l'annuaire téléphonique entier quand le client cherche une seule page",
                "text": "Supposons qu'une table métier rassemble 250 000 factures ou inscriptions : si l'endpoint `GET /api/v1/formations` matérialise et sérialise l'intégralité des 250 000 lignes en un bloc JSON de 80 Mo, le worker Gunicorn sature la RAM du serveur tandis que l'interface mobile du client se fige. En ingénierie de production, **toute route exposant une collection applique systématiquement le triptyque Filtrage, Tri contrôlé et Pagination bornée**."
            },
            "explanation": [
                "**Bornage défensif et découpage arithmétique par `page` et `limit`.** Lorsque le client sollicite `?page=2&limit=10`, la vue Flask verrouille d'abord les bornes par `limit = min(50, max(1, limit))` afin d'interdire tout déni de service par `?limit=9999999`. Le décalage initial se calcule par `debut = (page - 1) * limit` et la borne supérieure par `fin = debut + limit`, ce qui permet d'extraire la fenêtre exacte en mémoire via `resultats[debut:fin]` ou en SQL par `LIMIT ? OFFSET ?`.",
                "**Contrat de navigation dans l'enveloppe de métadonnées `meta`.** Un tableau de résultats isolé ne suffit jamais à piloter les contrôles graphiques d'une interface React, Vue ou mobile. L'API joint donc systématiquement un bloc `meta` renseignant `total_elements`, `total_pages` (obtenu par `math.ceil(total / limit)`), `page_actuelle` et l'indicateur booléen `a_page_suivante`.",
                "**Validation par liste blanche du critère de tri dynamique.** Accepter aveuglément un paramètre `?tri=...` expose la vue à des exceptions `KeyError` en Python ou à des injections syntaxiques dans une clause `ORDER BY` SQL. Avant tout appel à `sorted()` ou au moteur relationnel, le serveur vérifie impérativement que la colonne demandée appartient à un tuple immuable de champs autorisés tel que `('id', 'duree_jours', 'titre')`."
            ],
            "code": _read("03_pagination_filtrage_tri.py"),
            "line_explanations": [
                {"lines": "22-29", "text": "Étape 1 (Filtrage) : Sélectionne uniquement les enregistrements respectant `min_jours` et `salle`."},
                {"lines": "32-36", "text": "Étape 2 (Tri) : Vérifie que `champ_tri` est autorisé, puis trie par ordre croissant (`asc`) ou décroissant (`desc`)."},
                {"lines": "39-45", "text": "Étape 3 (Pagination) : Calcule `total_pages` avec `math.ceil()`, puis découpe la tranche `resultats[debut:fin]`."},
                {"lines": "47-57", "text": "Retourne l'enveloppe normalisée contenant les compteurs de pagination dans `meta` et les enregistrements dans `data`."}
            ],
            "sandbox_preset": {
                "label": "Tester la Pagination & le Tri : GET /api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc",
                "method": "GET",
                "url": "/api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc",
                "body": ""
            },
            "python_runner": {
                "prompt": "Testez l'algorithme complet de filtrage, tri et pagination sur un catalogue en Python :",
                "initial_code": '''import math

catalogue = [
    {"id": i, "titre": f"Module API #{i}", "jours": (i % 5) + 1}
    for i in range(1, 15)  # 14 formations au total
]

page = 2
limit = 4
total = len(catalogue)
total_pages = math.ceil(total / limit)
debut = (page - 1) * limit
tranche = catalogue[debut : debut + limit]

print(f"Page {page}/{total_pages} (Total: {total} éléments) :")
for item in tranche:
    print(" -", item)'''
            },
            "vscode_instructions": {
                "filename": "day_2/03_pagination_filtrage_tri.py",
                "steps": [
                    "Ouvrir `day_2/03_pagination_filtrage_tri.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_2/03_pagination_filtrage_tri.py` et tester différentes combinaisons de `?page=`, `?limit=`, `?salle=` et `?tri=`."
                ]
            }
        },
        {
            "id": "d2-l4",
            "file": "day_2/04_middlewares_et_audit_log.py",
            "title": "2.5 — Middlewares Flask (`@app.before_request`, `@app.after_request`), `X-Request-ID` & Journalisation d'Audit",
            "duration": "50 min",
            "analogy": {
                "title": "Le portique d'entrée et de sortie qui horodate chaque passage dans l'immeuble",
                "text": "Plutôt que de dupliquer le chronométrage, la génération d'identifiants de trace et l'injection d'en-têtes défensifs dans cinquante fonctions de vue distinctes, Flask expose des **crochets de cycle de vie (`request hooks`)** qui enveloppent transversalement tout le pipeline WSGI en amont (`@app.before_request`) et en aval (`@app.after_request`) de chaque requête traitée."
            },
            "explanation": [
                "**Isolation par requête de l'espace de noms contextuel `flask.g`.** L'objet proxy `g` (*application context globals*) alloue un conteneur éphémère strictement rattaché au cycle de vie de la requête HTTP courante. Les attributs déposés dès l'entrée dans `@app.before_request`, comme `g.heure_debut = time.perf_counter()` ou `g.request_id`, restent accessibles dans la vue métier puis dans `@app.after_request`, avant d'être automatiquement purgés à la clôture du contexte WSGI.",
                "**Traçabilité distribuée de bout en bout par `X-Request-ID`.** Dans un écosystème où un appel traverse successivement Nginx, plusieurs workers Gunicorn et une base de données, affecter un identifiant unique tel que `req-a1b2c3d4` à chaque requête permet une corrélation instantanée. Lorsqu'un client rapporte une anomalie en communiquant l'en-tête `X-Request-ID` reçu dans la réponse, l'équipe d'exploitation isole en une seconde la ligne correspondante dans les journaux d'audit.",
                "**Durcissement systématique des réponses dans `@app.after_request`.** Le crochet `@app.after_request` reçoit l'instance `Response` construite par la vue juste avant sa remise au serveur WSGI, ce qui permet d'y greffer globalement `X-Response-Time-Ms` et des en-têtes de sécurité. En particulier, `X-Content-Type-Options: nosniff` interdit aux navigateurs toute détection heuristique (*MIME sniffing*) et impose le respect strict du type `application/json` déclaré."
            ],
            "code": _read("04_middlewares_et_audit_log.py"),
            "line_explanations": [
                {"lines": "11-15", "text": "`@app.before_request` démarre un chronomètre haute précision (`time.perf_counter()`) et génère un `X-Request-ID` unique dans `g`."},
                {"lines": "18-29", "text": "`@app.after_request` calcule la durée d'exécution en millisecondes, injecte `X-Request-ID` et `X-Response-Time-Ms` dans les Headers HTTP, et écrit une trace d'audit."}
            ],
            "vscode_instructions": {
                "filename": "day_2/04_middlewares_et_audit_log.py",
                "steps": [
                    "Ouvrir `day_2/04_middlewares_et_audit_log.py`.",
                    "Exécuter `.venv/bin/python day_2/04_middlewares_et_audit_log.py` et observer les lignes `[AUDIT]` dans le terminal à chaque requête."
                ]
            }
        }
    ]
}
