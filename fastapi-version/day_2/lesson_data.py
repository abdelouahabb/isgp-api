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
                "text": (
                    "Une dérive courante lors de la création d'un premier service Web consiste à baptiser les URLs comme des appels de procédures RPC (`/getAllFormations`, `/createNewFormation`, `/deleteFormationById?id=4`) ou à concaténer du balisage HTML brut au cœur des contrôleurs Python.\n\n"
                    "Une architecture FastAPI sépare strictement ces préoccupations : les vues destinées au navigateur résident dans le répertoire **`templates/`** et sont compilées via **`Jinja2Templates`**, tandis que les endpoints RESTful désignent **exclusivement des noms de ressources au pluriel (`/api/v1/modules`)**, confient l'action au verbe HTTP et délèguent à FastAPI la sérialisation JSON native du dictionnaire ou du modèle Pydantic retourné."
                )
            },
            "explanation": [
                "**Dualité de rendu dans FastAPI : vues `Jinja2Templates` et réponses `JSONResponse` natives.** Lorsqu'une route vise un opérateur humain dans un navigateur, on déclare `@app.get('/accueil', response_class=HTMLResponse)` et l'on invoque `templates.TemplateResponse(request=request, name='accueil.html', context={...})` afin d'injecter proprement l'état Python dans un gabarit HTML isolé. Lorsqu'il s'agit au contraire d'un endpoint d'API REST, retourner directement un `dict`, une `list` ou une instance `BaseModel` déclenche le pipeline interne `jsonable_encoder` de FastAPI qui émet automatiquement un flux UTF-8 assorti de l'en-tête `content-type: application/json`.",
                "**Échelle architecturale du Modèle de Maturité de Richardson (Niveaux 0 à 3).** Ce référentiel évalue la fidélité d'une API aux principes du Web : le Niveau 0 réduit HTTP à un simple tunnel `POST /api` transportant des commandes disparates, et le Niveau 1 introduit des URIs distinctes par ressource (`/api/formations/12`) sans encore exploiter les méthodes HTTP. Le **Niveau 2**, cible industrielle de référence avec FastAPI, combine des URIs nominales avec la sémantique exacte des décorateurs `@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete` et des codes de statut (`200`, `201`, `401`, `404`, `422`, `429`), tandis que le Niveau 3 (HATEOAS) y adjoint des liens hypermédias de transition d'état.",
                "**Gouvernance de nommage des URIs et exécution sur le standard ASGI.** Une URI professionnelle utilise exclusivement des substantifs au pluriel en minuscules séparés par des traits d'union (`/api/v1/sessions-formation`), exprime l'appartenance par imbrication hiérarchique (`/api/v1/formations/12/stagiaires`) et ancre dès le premier jour un préfixe de version `/api/v1/`. Sous le capot, l'instruction `app = FastAPI()` instancie une application conforme à la spécification **ASGI 3.0 (*Asynchronous Server Gateway Interface*)** que le serveur **Uvicorn** pilote sur une boucle d'événements asynchrone haute performance."
            ],
            "code": _read("01_serveur_minimal_fastapi.py"),
            "line_explanations": [
                {"lines": "16-18", "text": "Création de l'application ASGI `FastAPI` et initialisation de `Jinja2Templates` pointant vers `day_2/templates/`."},
                {"lines": "31-42", "text": "Route Web `@app.get('/accueil', response_class=HTMLResponse)` : appelle `templates.TemplateResponse(...)` pour injecter le contexte dans `accueil.html`."},
                {"lines": "46-53", "text": "Route API `@app.get('/api/bonjour')` : retourne un dictionnaire Python converti nativement en JSON par FastAPI."},
                {"lines": "57-62", "text": "Route RESTful de collection `@app.get('/api/v1/modules')`."},
                {"lines": "65-71", "text": "Portail Web interactif `@app.get('/', response_class=HTMLResponse)` interrogeant `/api/bonjour` et `/api/v1/modules` via `fetch()`."},
                {"lines": "74-86", "text": "Démarrage via `uvicorn.run(...)` ou test immédiat en mémoire via `TestClient(app)`."}
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
                "text": (
                    "Lorsqu'un guichet administratif attend un numéro matricule strictement numérique (`/api/v1/stagiaires/1`) et qu'un visiteur présente un libellé alphabétique (`/api/v1/stagiaires/bonjour`), un filtrage rigoureux doit bloquer la demande avant même qu'elle n'atteigne le service d'instruction.\n\n"
                    "Grâce à l'introspection des **annotations de type Python (*Type Hints*)**, FastAPI compile un validateur Pydantic v2 pour chaque paramètre `stagiaire_id: int` : toute valeur incompatible est instantanément rejetée avec le statut `422 Unprocessable Entity` et un rapport d'erreur structuré, sans qu'une seule ligne de votre fonction métier ne soit exécutée."
                )
            },
            "explanation": [
                "**Extraction et coercition déclaratives des paramètres de chemin (`{variable}` et `Path`).** Déclarer `@app.get('/api/v1/stagiaires/{stagiaire_id}')` associé à la signature `stagiaire_id: int = Path(..., ge=1)` ordonne à Starlette d'extraire le segment dynamique de l'URL et à `pydantic-core` de convertir cette chaîne en entier Python `>= 1` tout en inscrivant automatiquement la contrainte dans le contrat OpenAPI 3.1 (`/docs`).",
                "**Harmonisation syntaxique entre écosystèmes : `{id}` (FastAPI / OpenAPI) vs `<int:id>` (Flask) vs `:id` (Postman).** Les accolades `{stagiaire_id}` constituent la norme officielle de FastAPI, de Starlette, des f-strings Python et de la spécification RFC 6570 / OpenAPI 3.1, là où Flask et Werkzeug employaient historiquement des chevrons typés `<int:id>` et où Postman ainsi qu'Express.js utilisent le préfixe deux-points `:id` pour matérialiser leurs variables de chemin. Sur le fil réseau réel (`curl` ou navigateur), ces marqueurs disparaissent toujours au profit de la valeur concrète (`/api/v1/stagiaires/1`).",
                "**Validation des critères de Query String (`Query`) et accès bas niveau à `Request`.** Tout paramètre de fonction absent du modèle de chemin est résolu automatiquement dans la chaîne de requête après `?` : écrire `ht: float = Query(default=1000.0, gt=0)` et `taux: float = Query(default=19.0, ge=0, le=100)` élimine tout parsing manuel sujet aux oublis. Lorsque l'inspection brute du transport s'avère nécessaire, injecter `request: Request` offre un accès direct aux métadonnées ASGI (`request.method`, `request.headers`, `request.client`) ainsi qu'aux coroutines de lecture de flux `await request.body()`, `await request.json()` et `await request.form()`."
            ],
            "code": _read("02_routes_et_parametres.py"),
            "line_explanations": [
                {"lines": "30-38", "text": "Paramètre de chemin `{prenom}` validé par `Path(..., min_length=2)` et injecté dans `saluer_stagiaire(prenom: str)`."},
                {"lines": "42-50", "text": "Paramètre typé `{stagiaire_id}: int = Path(..., ge=1)` retournant la ressource en JSON ou levant `HTTPException(status_code=404)`."},
                {"lines": "54-66", "text": "Même paramètre `{stagiaire_id}: int` utilisé pour rendre la fiche HTML Jinja2 `day_2/templates/fiche_stagiaire.html` via `templates.TemplateResponse`."},
                {"lines": "70-81", "text": "Extraction et validation déclarative des Query Parameters `?ht=...&taux=...` via `Query(default=..., gt=0)`."},
                {"lines": "84-90", "text": "Portail Web interactif sur `GET /` (`portail_02_routes.html`) exposant l'ensemble des routes paramétrées."}
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
                "text": (
                    "Assembler des fragments HTML par concaténation de chaînes directement dans un contrôleur Python (`return '<h1>' + titre + '</h1>'`) constitue un anti-pattern critique : la lisibilité s'effondre dès la première table dynamique et la moindre saisie utilisateur non filtrée ouvre une brèche d'exécution JavaScript (**XSS — Cross-Site Scripting**).\n\n"
                    "Dans FastAPI, la présentation Web est isolée dans le dossier **`templates/`** sous l'égide de **`Jinja2Templates`**. Parallèlement, lorsqu'un opérateur humain valide un formulaire `<form method='POST'>`, le navigateur n'expédie pas un objet JSON mais un flux encodé en `application/x-www-form-urlencoded` (ou `multipart/form-data` pour les pièces jointes), que FastAPI analyse via **`Form(...)`** et **`UploadFile = File(...)`** grâce au parseur de flux `python-multipart`."
                )
            },
            "explanation": [
                "**Isolation de la couche de présentation et auto-échappement anti-XSS avec `Jinja2Templates`.** Le moteur `Jinja2Templates` compile les gabarits `.html` du répertoire `templates/` en séparant la structure documentaire des données Python : les interpolations `{{ variable }}` convertissent automatiquement les caractères réservés `<`, `>`, `&`, `\"` en entités HTML inoffensives pour neutraliser toute injection XSS, tandis que les directives `{% for elem in liste %}` et `{% if condition %}` pilotent le rendu itératif et conditionnel.",
                "**Différence protocolaire entre soumission HTML (`Form(...)`) et charge utile API (`BaseModel`).** Lors du clic sur le bouton `submit` d'un élément `<form method='POST' action='/formations'>`, le navigateur collecte tous les champs munis d'un attribut `name='...'` et les sérialise sous l'en-tête `Content-Type: application/x-www-form-urlencoded` (`titre=Atelier&duree_jours=4`). FastAPI exige alors des descripteurs explicites `titre: str = Form(...)` (ou `await request.form()`) au lieu d'un `BaseModel` JSON, faute de quoi la négociation de format échouerait.",
                "**Transfert binaire asynchrone (`multipart/form-data`) via `UploadFile` et hygiène du système de fichiers.** Dès qu'un formulaire inclut un sélecteur `<input type='file'>`, l'attribut `enctype='multipart/form-data'` découpe la trame HTTP en sections séparées par une frontière unique (*boundary*). Côté serveur, `UploadFile = File(...)` encapsule un `SpooledTemporaryFile` qui garde les petits fichiers en RAM et déverse automatiquement les gros volumes sur disque sans saturer la boucle `asyncio`, à condition de toujours assainir `document_pdf.filename` (`os.path.basename` + liste blanche) contre toute traversée d'arborescence (*Path Traversal* `../../`)."
            ],
            "code": _read("05_jinja_et_formulaires_html.py"),
            "line_explanations": [
                {"lines": "21-23", "text": "Initialisation de `FastAPI` et de `Jinja2Templates` pointant vers `day_2/templates/`."},
                {"lines": "42-70", "text": "Routes `/formations` (GET et POST) gérant aussi bien un formulaire HTML (`await request.form()`) qu'un appel API JSON (`await request.json()`)."},
                {"lines": "100-110", "text": "`templates.TemplateResponse(request=request, name='formations.html', ...)` rend le gabarit Jinja2 avec le code HTTP approprié (`200` ou `422`)."},
                {"lines": "116-134", "text": "Route `POST /formations/upload-syllabus` combinant `Form(...)` et `UploadFile = File(...)` avec nettoyage anti-Path Traversal du nom de fichier."},
                {"lines": "137-143", "text": "Portail Web interactif sur `GET /` (`portail_05_formulaires.html`) testant `POST /formations` et l'upload multipart."}
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
                "text": (
                    "Considérez une table de production contenant 250 000 inscriptions ou écritures comptables : si un appel `GET /api/v1/formations` charge l'intégralité de la table en RAM Python pour expédier un bloc JSON monolithique de 80 Mo, la mémoire des workers Uvicorn sature en quelques requêtes concurrentes pendant que l'interface mobile du client fige son thread principal.\n\n"
                    "En ingénierie backend, **aucune route exposant une collection n'est mise en production sans un triptyque défensif composé d'une Pagination bornée, d'un Filtrage sélectif et d'un Tri contrôlé par liste blanche**."
                )
            },
            "explanation": [
                "**Plafonnement déclaratif de la pagination par `Query(ge=1, le=50)`.** Annoter la signature d'un endpoint avec `page: int = Query(default=1, ge=1)` et `limit: int = Query(default=3, ge=1, le=50)` délègue à Pydantic le rejet automatique (`422 Unprocessable Entity`) de toute requête malveillante telle que `?limit=9999999` ou `?page=0`. Une fois la cardinalité totale mesurée sur le sous-ensemble filtré, le décalage mémoire se calcule par `debut = (page - 1) * limit` et extrait exactement la fenêtre `resultats[debut : debut + limit]`.",
                "**Verrouillage statique et dynamique du tri grâce au type `typing.Literal`.** Typer les critères d'ordonnancement avec `tri: Literal['id', 'duree_jours', 'titre'] = Query(default='id')` et `ordre: Literal['asc', 'desc'] = Query(default='asc')` procure un double bénéfice architectural : `pydantic-core` bloque à la frontière toute tentative d'interroger un attribut interne sensible ou une colonne SQL arbitraire, et Swagger UI génère automatiquement une liste déroulante fermée des valeurs permises.",
                "**Validation structurelle d'une charge utile `POST` par schéma `BaseModel`.** Déclarer un paramètre `payload: FormationCreation` sur une route `@app.post('/api/v1/formations', status_code=status.HTTP_201_CREATED)` déclenche la lecture asynchrone du flux HTTP, le parsing JSON et la vérification simultanée de toutes les contraintes `Field(min_length=3, ge=1, le=30)` avant même l'entrée dans le corps de la fonction."
            ],
            "code": _read("03_pagination_filtrage_tri.py"),
            "line_explanations": [
                {"lines": "31-35", "text": "Modèle Pydantic `FormationCreation` définissant les contraintes sur `code`, `titre`, `duree_jours` et `salle`."},
                {"lines": "38-46", "text": "Signature déclarative avec `Query(ge=1, le=50)` et `Literal['id', 'duree_jours', 'titre']`."},
                {"lines": "48-74", "text": "Filtrage, tri dynamique et découpage de la page avec retour de l'enveloppe normalisée `meta` + `data`."},
                {"lines": "77-83", "text": "Route `@app.post('/api/v1/formations', status_code=status.HTTP_201_CREATED)` validant automatiquement le corps JSON via `FormationCreation`."},
                {"lines": "86-92", "text": "Portail Web interactif sur `GET /` (`portail_03_pagination.html`) pilotant la recherche, le tri et la création via `fetch()`."}
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
                "text": (
                    "Dupliquer des instructions de chronométrage, de génération d'identifiant de trace et d'injection d'en-têtes de durcissement dans cinquante routes métier viole le principe de responsabilité unique et garantit des oublis lors des évolutions futures.\n\n"
                    "Un **Middleware ASGI** (`@app.middleware('http')`) agit comme une enveloppe concentrique placée à l'entrée du serveur : chaque requête entrante et chaque réponse sortante traversent obligatoirement cette coroutine autour du point de pivot `await call_next(request)`."
                )
            },
            "explanation": [
                "**Modèle en couches concentriques (*Onion Architecture*) autour de `await call_next(request)`.** Là où les frameworks WSGI historiques dissociaient deux crochets séparés (`before_request` et `after_request`), FastAPI unifie le cycle de vie au sein d'une seule coroutine asynchrone : les instructions placées avant `reponse = await call_next(request)` s'exécutent sur la requête entrante (démarrage de `time.perf_counter()`, inspection d'en-têtes), puis l'exécution reprend exactement à la ligne suivante dès que la route aval a produit son objet `Response`.",
                "**Isolation concurrente par requête avec `request.state` et corrélation `X-Request-ID`.** Sur une boucle d'événements `asyncio` traitant de multiples coroutines entrelacées, stocker un identifiant de requête dans une variable globale Python provoquerait des collisions immédiates entre clients concurrents. L'espace de noms `request.state` (équivalent ASGI sûr de l'objet `flask.g` de Flask) attache les métadonnées telles que `request.state.request_id` directement au dictionnaire `scope` propre à la requête en cours, permettant de propager l'en-tête `X-Request-ID` jusque dans la réponse HTTP et les journaux d'audit.",
                "**Durcissement systématique des réponses HTTP (`Security Headers`).** La phase retour du middleware garantit qu'aucune route, même nouvellement ajoutée, n'omet les directives de protection navigateur telles que `X-Content-Type-Options: nosniff`, qui interdit tout *MIME-sniffing* heuristique et impose le respect strict du type `application/json` déclaré par le serveur."
            ],
            "code": _read("04_middlewares_et_audit_log.py"),
            "line_explanations": [
                {"lines": "22-27", "text": "Phase aller du middleware `@app.middleware('http')` : démarre `time.perf_counter()` et stocke l'ID de corrélation dans `request.state.request_id`."},
                {"lines": "30", "text": "`reponse = await call_next(request)` passe le relais à la route FastAPI ciblée et attend sa réponse de manière asynchrone."},
                {"lines": "33-39", "text": "Phase retour : calcule la durée en ms, injecte `X-Request-ID`, `X-Response-Time-Ms` et `X-Content-Type-Options: nosniff`, puis écrit la trace `[AUDIT ASGI]`."},
                {"lines": "51-57", "text": "Portail Web interactif sur `GET /` (`portail_04_middlewares.html`) affichant en direct les en-têtes injectés par le middleware."}
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
