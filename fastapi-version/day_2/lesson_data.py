import os

BASE_DIR = os.path.dirname(__file__)


def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()


DAY_2_DATA = {
    "day_number": 2,
    "folder": "day_2",
    "badge": "Jour 2 • Design RESTful, FastAPI (ASGI), Jinja2Templates & Formulaires Web",
    "title": "Prise en Main de FastAPI : Serveur ASGI (Uvicorn), Jinja2Templates, Formulaires HTML (Form / UploadFile), Routage Typé, Pagination & Middlewares",
    "goal": "Comprendre l'architecture asynchrone ASGI de FastAPI et Uvicorn, séparer proprement la logique Python des pages HTML grâce à Jinja2Templates, traiter les formulaires HTML (Form(...) et UploadFile = File(...)), maîtriser les paramètres de route typés ({id}: int vs <int:id> vs :id), implémenter la pagination/filtrage/tri avec Query(...) et mettre en place des middlewares ASGI (@app.middleware('http')).",
    "starter_filename": "day_2/05_jinja_et_formulaires_html.py",
    "files": [
        "day_2/01_serveur_minimal_fastapi.py",
        "day_2/02_routes_et_parametres.py",
        "day_2/05_jinja_et_formulaires_html.py",
        "day_2/03_pagination_filtrage_tri.py",
        "day_2/04_middlewares_et_audit_log.py",
    ],
    "lessons": [
        {
            "id": "d2-l1",
            "file": "day_2/01_serveur_minimal_fastapi.py",
            "title": "2.1 — Premiers Pas avec FastAPI : Serveur ASGI (Uvicorn), Rendu Jinja2 (`Jinja2Templates`) vs API REST JSON & Modèle de Richardson",
            "duration": "55 min",
            "analogy": {
                "title": "Organiser les rayons d'une bibliothèque par noms de collections plutôt que par phrases d'action",
                "text": "Une erreur fréquente chez les débutants consiste à nommer les URLs comme des fonctions : `/getAllFormations`, `/createNewFormation`, `/deleteFormationById?id=4`, ou à coder du HTML en dur dans Python.\nDans FastAPI, les pages Web résident dans le dossier **`templates/`** et sont rendues via **`Jinja2Templates`** (`templates.TemplateResponse(request=request, name='accueil.html', context={...})`), tandis que les routes d'API RESTful désignent **exclusivement la Ressource (un nom au pluriel : `/api/v1/modules`)** et renvoient directement un dictionnaire ou un modèle Pydantic converti nativement en JSON."
            },
            "explanation": [
                "**1. Comment FastAPI sert à la fois des pages Web (`Jinja2Templates`) et des APIs JSON** :\n  - **Pour une page Web destinée à un navigateur** : On configure `templates = Jinja2Templates(directory='...')` et on décore la route avec `@app.get('/accueil', response_class=HTMLResponse)` en retournant `templates.TemplateResponse(request=request, name='accueil.html', context={...})`.\n  - **Pour un endpoint d'API REST** : On retourne simplement un dictionnaire Python ou un objet Pydantic `BaseModel` ! FastAPI le sérialise automatiquement en `JSONResponse` UTF-8 avec `Content-Type: application/json`.",
                "**2. Le Modèle de Maturité de Richardson (Les 4 niveaux d'une API REST)** :\n  - **Niveau 0 (Le marécage du POX / RPC)** : Une seule URL (`POST /api`) à laquelle on envoie des commandes diverses.\n  - **Niveau 1 (Les Ressources)** : Chaque entité métier possède sa propre URI (`/api/formations`, `/api/formations/12`, `/api/stagiaires`).\n  - **Niveau 2 (Les Verbes & Codes HTTP)** : Utilisation rigoureuse de `@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete` et des codes de statut (`200`, `201`, `400`, `401`, `404`, `422`, `429`). C'est le standard industriel visé.\n  - **Niveau 3 (HATEOAS)** : La réponse JSON inclut des liens (`links`) vers les actions suivantes possibles.",
                "**3. Les 5 conventions de nommage d'URI et le standard ASGI** :\n  1. **Toujours des noms au pluriel en minuscules** : `/api/v1/formations` (jamais `/api/Formation` ni `/api/get_formations`).\n  2. **Séparer les mots composés par un tiret `-` (kebab-case)** : `/api/v1/sessions-formation`.\n  3. **Hiérarchie pour les sous-ressources** : `/api/v1/formations/12/stagiaires`.\n  4. **Versioning explicite (`/api/v1/...`)** : Permet de faire évoluer l'API vers `/api/v2/...` sans casser les clients existants.\n  5. **Cycle ASGI dans FastAPI & Uvicorn** : `app = FastAPI()` crée une application conforme au standard **ASGI (*Asynchronous Server Gateway Interface*)** exécutée par **Uvicorn** (`uvicorn.run(app, port=8000)`)."
            ],
            "code": _read("01_serveur_minimal_fastapi.py"),
            "line_explanations": [
                {"lines": "15-17", "text": "Création de l'application ASGI `FastAPI` et initialisation de `Jinja2Templates` pointant vers `day_2/templates/`."},
                {"lines": "29-40", "text": "Route Web `@app.get('/accueil', response_class=HTMLResponse)` : appelle `templates.TemplateResponse(...)` pour injecter le contexte dans `accueil.html`."},
                {"lines": "44-51", "text": "Route API `@app.get('/api/bonjour')` : retourne un dictionnaire Python converti nativement en JSON par FastAPI."},
                {"lines": "55-60", "text": "Route RESTful de collection `@app.get('/api/v1/modules')`."},
                {"lines": "63-77", "text": "Démarrage via `uvicorn.run(...)` si `--serve` est fourni, ou test immédiat en mémoire via `TestClient(app)`."}
            ],
            "sandbox_preset": {
                "label": "Tester la route GET /api/sandbox/bonjour",
                "method": "GET",
                "url": "/api/sandbox/bonjour",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_2/01_serveur_minimal_fastapi.py` pour observer le rendu `Jinja2Templates` (`day_2/templates/accueil.html`) et la réponse JSON FastAPI (`/api/bonjour`) :",
                "initial_code": _read("01_serveur_minimal_fastapi.py")
            },
            "vscode_instructions": {
                "filename": "day_2/01_serveur_minimal_fastapi.py",
                "steps": [
                    "Inspecter `day_2/01_serveur_minimal_fastapi.py` et son template HTML `day_2/templates/accueil.html`.",
                    "Exécuter `.venv/bin/python day_2/01_serveur_minimal_fastapi.py` (ou ajouter `--serve` pour démarrer Uvicorn sur le port 8001)."
                ]
            }
        },
        {
            "id": "d2-l2",
            "file": "day_2/02_routes_et_parametres.py",
            "title": "2.2 — Routage Dynamique (`{variable}` vs `<variable>` vs `:variable`), Annotations de Type (`{id}: int`, `Path`, `Query`) & `Request`",
            "duration": "55 min",
            "analogy": {
                "title": "Le contrôleur de guichet qui valide et convertit automatiquement chaque paramètre grâce aux Type Hints Python",
                "text": "Si un guichet attend un numéro de dossier entier (`/api/v1/stagiaires/1`) et qu'un visiteur demande `/api/v1/stagiaires/bonjour`, FastAPI inspecte l'annotation de type Python `stagiaire_id: int` et rejette automatiquement la demande en `422 Unprocessable Entity` avec un diagnostic Pydantic précis, avant même d'exécuter votre fonction Python."
            },
            "explanation": [
                "**1. Les paramètres de chemin typés dans FastAPI (`{variable}` + Type Hints Python + `Path(...)`)** :\n  - `@app.get('/api/saluer/{prenom}')` avec `prenom: str` : capture une chaîne de caractères.\n  - `@app.get('/api/v1/stagiaires/{stagiaire_id}')` avec `stagiaire_id: int = Path(..., ge=1)` : capture uniquement un entier `>= 1`, le convertit en `int` Python et le documente automatiquement dans Swagger UI (`/docs`).",
                "**2. Distinction cruciale : `{variable}` (FastAPI / OpenAPI) vs `<variable>` (Flask) vs `:variable` (Postman / Express.js)** :\n  - **`{variable}` (ex. `{stagiaire_id}`)** : Syntaxe officielle de **FastAPI**, **Starlette**, **OpenAPI 3.1 / Swagger** et des **f-strings Python** (`@app.get('/api/v1/stagiaires/{stagiaire_id}')`).\n  - **`<variable>` ou `<int:id>`** : Syntaxe historique de **Flask / Werkzeug**.\n  - **`:variable` (ex. `:id`)** : Syntaxe utilisée dans **Postman** (onglet *Path Variables*) et **Express.js (Node.js)** (`/api/v1/stagiaires/:id`).\n  - **Dans `curl` ou le navigateur** : On envoie toujours la **valeur réelle** (`/api/v1/stagiaires/1`).",
                "**3. Paramètres de requête déclaratifs (`Query(...)`) et objet `Request` dans FastAPI** :\n  - Au lieu d'extraire manuellement `request.args.get('ht', type=float)`, FastAPI permet de déclarer directement les paramètres de Query String dans la signature de la fonction : `ht: float = Query(default=1000.0, gt=0)`, `taux: float = Query(default=19.0, ge=0, le=100)`.\n  - L'objet `request: Request` (Starlette/FastAPI) donne accès à `request.method`, `request.url.path`, `request.headers`, `request.query_params`, `await request.json()`, `await request.form()` et `await request.body()`."
            ],
            "code": _read("02_routes_et_parametres.py"),
            "line_explanations": [
                {"lines": "26-34", "text": "Paramètre de chemin `{prenom}` validé par `Path(..., min_length=2)` et injecté dans `saluer_stagiaire(prenom: str)`."},
                {"lines": "38-46", "text": "Paramètre typé `{stagiaire_id}: int = Path(..., ge=1)` retournant la ressource en JSON ou levant `HTTPException(status_code=404)`."},
                {"lines": "50-62", "text": "Même paramètre `{stagiaire_id}: int` utilisé pour rendre la fiche HTML Jinja2 `day_2/templates/fiche_stagiaire.html` via `templates.TemplateResponse`."},
                {"lines": "66-77", "text": "Extraction et validation déclarative des Query Parameters `?ht=...&taux=...` via `Query(default=..., gt=0)`."}
            ],
            "sandbox_preset": {
                "label": "Tester GET /api/sandbox/calcul-tva?ht=2500&taux=19",
                "method": "GET",
                "url": "/api/sandbox/calcul-tva?ht=2500&taux=19",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_2/02_routes_et_parametres.py` pour tester `{prenom}`, `{stagiaire_id}: int` (Jinja2Templates + JSON) et `Query(...)` :",
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
            "title": "2.3 — Moteur `Jinja2Templates` & Traitement des Formulaires Web HTML (`Form(...)`, `File(...)`, `UploadFile`)",
            "duration": "65 min",
            "analogy": {
                "title": "Séparer le moule d'imprimerie (Template Jinja2 .html) des données de l'ordinateur (Python) et du bordereau papier rempli par l'usager (<form>)",
                "text": "Écrire des chaînes HTML directement dans un fichier Python (`return '<h1>' + titre + '</h1>'`) est une mauvaise pratique majeure : le code devient illisible et vulnérable aux failles d'injection JavaScript (**XSS**).\nDans FastAPI, les pages Web résident dans le dossier **`templates/`** et utilisent **`Jinja2Templates`**. Et lorsqu'un utilisateur soumet un formulaire HTML `<form method='POST'>`, le navigateur n'envoie **pas** du JSON, mais des données `application/x-www-form-urlencoded` que FastAPI extrait via **`Form(...)`** (et **`UploadFile = File(...)`** pour les pièces jointes via `python-multipart`) !"
            },
            "explanation": [
                "**1. Pourquoi il ne faut jamais coder du HTML en dur dans Python : `Jinja2Templates`** :\n  - FastAPI s'intègre avec **Jinja2** (`from fastapi.templating import Jinja2Templates`), qui charge les fichiers `.html` du dossier `templates/` et remplace dynamiquement trois types de balises :\n    1. **`{{ variable }}`** : Affiche la valeur d'une variable Python en **échappant automatiquement** les caractères `<`, `>`, `&` pour bloquer toute attaque **XSS (*Cross-Site Scripting*)**.\n    2. **`{% for elem in liste %} ... {% endfor %}`** : Répète un bloc HTML (ex: générer une ligne `<tr>` par formation).\n    3. **`{% if condition %} ... {% endif %}`** : Affiche un bloc d'alerte ou d'erreur uniquement si la condition est vraie.",
                "**2. Comment un Formulaire HTML (`<form method='POST'>`) envoie ses données à FastAPI (`Form(...)` vs `BaseModel`)** :\n  - Lorsqu'un utilisateur clique sur le bouton `<button type='submit'>` d'un formulaire HTML `<form method='POST' action='/formations'>`, le navigateur regroupe tous les champs possédant un attribut **`name='...'`** (`<input name='titre'>`, `<select name='salle'>`) et les envoie avec l'en-tête **`Content-Type: application/x-www-form-urlencoded`**.\n  - Dans FastAPI, on les déclare avec `titre: str = Form(...)`, `duree_jours: int = Form(...)` (ou `await request.form()`), tandis qu'un corps JSON est validé par un modèle Pydantic `BaseModel`.",
                "**3. Upload de Fichiers (`<input type='file'>`) avec `enctype='multipart/form-data'` et `UploadFile = File(...)`** :\n  - Si le formulaire comporte un champ fichier (PDF, image, Excel), la balise `<form>` doit déclarer `enctype='multipart/form-data'`.\n  - Côté FastAPI, on déclare `document_pdf: UploadFile = File(...)` et on lit son contenu de manière asynchrone avec `await document_pdf.read()` après avoir nettoyé `document_pdf.filename` contre toute attaque *Path Traversal* (`../`)."
            ],
            "code": _read("05_jinja_et_formulaires_html.py"),
            "line_explanations": [
                {"lines": "19-21", "text": "Initialisation de `FastAPI` et de `Jinja2Templates` pointant vers `day_2/templates/`."},
                {"lines": "39-64", "text": "Routes `/formations` (GET et POST) gérant aussi bien un formulaire HTML (`await request.form()`) qu'un appel API JSON (`await request.json()`)."},
                {"lines": "89-99", "text": "`templates.TemplateResponse(request=request, name='formations.html', ...)` rend le gabarit Jinja2 avec le code HTTP approprié (`200` ou `422`)."},
                {"lines": "105-122", "text": "Route `POST /formations/upload-syllabus` combinant `Form(...)` et `UploadFile = File(...)` avec nettoyage anti-Path Traversal du nom de fichier."}
            ],
            "sandbox_preset": {
                "label": "Tester POST /api/sandbox/formulaire-formation (Form FastAPI)",
                "method": "POST",
                "url": "/api/sandbox/formulaire-formation",
                "body": "titre=Atelier+Jinja2&formateur=ISGP&duree_jours=4&salle=Salle+B"
            },
            "python_runner": {
                "prompt": "Exécutez le test complet de soumission de formulaire HTML (`Form` + rendu `Jinja2Templates`) et d'upload `multipart/form-data` (`UploadFile = File(...)`) :",
                "initial_code": _read("05_jinja_et_formulaires_html.py")
            },
            "vscode_instructions": {
                "filename": "day_2/05_jinja_et_formulaires_html.py",
                "steps": [
                    "Inspecter le fichier de template Jinja2 `day_2/templates/formations.html` et le script `day_2/05_jinja_et_formulaires_html.py`.",
                    "Ouvrir l'atelier interactif réel dans votre navigateur sur `http://127.0.0.1:8000/sandbox/formulaire-jinja` pour soumettre de vraies formations via `<form method='POST'>`."
                ]
            }
        },
        {
            "id": "d2-l3",
            "file": "day_2/03_pagination_filtrage_tri.py",
            "title": "2.4 — Pagination (`page`, `limit`), Filtrage, Tri (`Query`, `Literal`) & Réception JSON (`BaseModel`) dans FastAPI",
            "duration": "65 min",
            "analogy": {
                "title": "Ne jamais envoyer l'annuaire téléphonique entier quand le client cherche une seule page",
                "text": "Imaginez une table contenant 250 000 factures ou formations. Si `GET /api/v1/formations` renvoie les 250 000 lignes en un seul bloc JSON de 80 Mo, la mémoire du serveur explose et l'application mobile du client gèle. En production, **toute route retournant une collection doit impérativement implémenter la Pagination, le Filtrage et le Tri**."
            },
            "explanation": [
                "**1. Validation déclarative de la Pagination avec `Query(ge=1, le=50)`** :\n  - Dans FastAPI, écrire `page: int = Query(default=1, ge=1)` et `limit: int = Query(default=3, ge=1, le=50)` borne automatiquement les paramètres côté serveur ! Si un client malveillant demande `?limit=9999999` ou `?page=0`, FastAPI rejette immédiatement la requête avec `422 Unprocessable Entity`.\n  - L'indice de départ (`offset`) vaut `debut = (page - 1) * limit` et la tranche paginée vaut `resultats[debut : debut + limit]`.",
                "**2. Sécurisation du Tri Dynamique par type `Literal`** :\n  - En annotant `tri: Literal['id', 'duree_jours', 'titre'] = Query(default='id')` et `ordre: Literal['asc', 'desc'] = Query(default='asc')`, FastAPI génère automatiquement une liste déroulante dans Swagger UI et interdit toute valeur hors liste blanche.",
                "**3. Réception et validation d'un corps JSON `POST` avec Pydantic `BaseModel`** :\n  - En déclarant `payload: FormationCreation` dans `@app.post('/api/v1/formations', status_code=status.HTTP_201_CREATED)`, FastAPI désérialise et valide le JSON entrant selon les règles `Field(min_length=3, ge=1, le=30)`."
            ],
            "code": _read("03_pagination_filtrage_tri.py"),
            "line_explanations": [
                {"lines": "24-28", "text": "Modèle Pydantic `FormationCreation` définissant les contraintes sur `code`, `titre`, `duree_jours` et `salle`."},
                {"lines": "31-39", "text": "Signature déclarative avec `Query(ge=1, le=50)` et `Literal['id', 'duree_jours', 'titre']`."},
                {"lines": "41-68", "text": "Filtrage, tri dynamique et découpage de la page avec retour de l'enveloppe normalisée `meta` + `data`."},
                {"lines": "71-76", "text": "Route `@app.post('/api/v1/formations', status_code=status.HTTP_201_CREATED)` validant automatiquement le corps JSON via `FormationCreation`."}
            ],
            "sandbox_preset": {
                "label": "Tester la Pagination & le Tri : GET /api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc",
                "method": "GET",
                "url": "/api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_2/03_pagination_filtrage_tri.py` pour tester la pagination `Query(...)` et la réception `POST` avec `BaseModel` :",
                "initial_code": _read("03_pagination_filtrage_tri.py")
            },
            "vscode_instructions": {
                "filename": "day_2/03_pagination_filtrage_tri.py",
                "steps": [
                    "Ouvrir `day_2/03_pagination_filtrage_tri.py` dans VS Code ou Antigravity IDE.",
                    "Exécuter `.venv/bin/python day_2/03_pagination_filtrage_tri.py`."
                ]
            }
        },
        {
            "id": "d2-l4",
            "file": "day_2/04_middlewares_et_audit_log.py",
            "title": "2.5 — Middlewares ASGI dans FastAPI (`@app.middleware('http')`), `request.state`, `X-Request-ID` & Audit",
            "duration": "50 min",
            "analogy": {
                "title": "Le portique d'entrée et de sortie qui horodate chaque passage dans l'immeuble",
                "text": "Au lieu de copier-coller du code de chronométrage, de traçabilité et d'en-têtes de sécurité dans chacune de vos 50 fonctions de routes, un **Middleware ASGI** (`@app.middleware('http')`) enveloppe chaque requête avant et après `await call_next(request)`."
            },
            "explanation": [
                "**1. Architecture d'un Middleware HTTP dans FastAPI (`@app.middleware('http')`)** :\n  - Contrairement à Flask qui sépare `@app.before_request` et `@app.after_request`, FastAPI utilise une seule coroutine englobante : tout ce qui précède `reponse = await call_next(request)` s'exécute **à l'aller (avant la route)**, et tout ce qui suit s'exécute **au retour (après la route)**.",
                "**2. L'espace de stockage par requête `request.state` et l'en-tête `X-Request-ID`** :\n  - Dans FastAPI/Starlette, on attache les métadonnées de la requête en cours à **`request.state`** (ex: `request.state.request_id = ...`), qui est l'équivalent ASGI moderne de l'objet `g` de FastAPI.\n  - L'identifiant de corrélation `X-Request-ID` est injecté dans la réponse HTTP et dans les journaux d'audit.",
                "**3. En-têtes de sécurité systématiques** : `X-Content-Type-Options: nosniff` interdit au navigateur de deviner le type MIME et force le respect strict de `application/json`."
            ],
            "code": _read("04_middlewares_et_audit_log.py"),
            "line_explanations": [
                {"lines": "16-21", "text": "Phase aller du middleware `@app.middleware('http')` : démarre `time.perf_counter()` et stocke l'ID de corrélation dans `request.state.request_id`."},
                {"lines": "24", "text": "`reponse = await call_next(request)` passe le relais à la route FastAPI ciblée et attend sa réponse de manière asynchrone."},
                {"lines": "27-33", "text": "Phase retour : calcule la durée en ms, injecte `X-Request-ID`, `X-Response-Time-Ms` et `X-Content-Type-Options: nosniff`, puis écrit la trace `[AUDIT ASGI]`."}
            ],
            "python_runner": {
                "prompt": "Exécutez `day_2/04_middlewares_et_audit_log.py` pour observer le middleware ASGI `@app.middleware('http')` en action :",
                "initial_code": _read("04_middlewares_et_audit_log.py")
            },
            "vscode_instructions": {
                "filename": "day_2/04_middlewares_et_audit_log.py",
                "steps": [
                    "Ouvrir `day_2/04_middlewares_et_audit_log.py`.",
                    "Exécuter `.venv/bin/python day_2/04_middlewares_et_audit_log.py` et observer les lignes `[AUDIT ASGI]` et les en-têtes injectés."
                ]
            }
        }
    ]
}
