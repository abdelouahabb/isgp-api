import os

BASE_DIR = os.path.dirname(__file__)

def _read(filename):
    with open(os.path.join(BASE_DIR, filename), encoding="utf-8") as f:
        return f.read().strip()

DAY_5_DATA = {
    "day_number": 5,
    "folder": "day_5",
    "badge": "Jour 5 • Architecture, Versioning, Tests & Production WSGI",
    "title": "Architecture Modulaire (Blueprints & Versioning v1/v2), Client Résilient, Tests Automatisés, OpenAPI 3.0 & Pagination Haute Performance",
    "goal": "Savoir consommer une API de manière résiliente (Timeouts, Retries), découper une grande API en modules (Blueprints, Application Factory, Versioning v1/v2 RFC 8594, Healthchecks), automatiser les tests avec test_client(), publier le contrat OpenAPI 3.0 et maîtriser la pagination (Offset vs Cursor) en production WSGI.",
    "starter_filename": "day_5/03_architecture_blueprints.py",
    "files": [
        "day_5/01_client_python_auth.py",
        "day_5/03_architecture_blueprints.py",
        "day_5/04_tests_et_production.py",
        "day_5/05_swagger_openapi_ui.py",
        "day_5/02_pagination_filtrage_production.py",
    ],
    "lessons": [
        {
            "id": "d5-l1",
            "file": "day_5/01_client_python_auth.py",
            "title": "5.1 — Ingénierie du Client HTTP Résilient : Timeouts, Gestion d'Erreurs & Exponential Backoff",
            "duration": "55 min",
            "analogy": {
                "title": "Ne jamais appeler le réseau sans chronomètre (Timeout)",
                "text": "Lorsqu'un worker Gunicorn de votre service A interroge en synchrone l'API d'un service B — passerelle monétique, moteur fiscal ou référentiel externe —, une congestion réseau peut figer le pair distant sans jamais clôturer le socket TCP.\n\nSi votre client Python invoque `urlopen()` ou `requests.get()` **sans paramètre `timeout` explicite**, le worker WSGI demeure suspendu indéfiniment sur l'appel système de lecture. En quelques instants, l'ensemble du pool de workers Gunicorn se retrouve immobilisé et votre propre serveur cesse de répondre à ses usagers : c'est le phénomène classique de **panne en cascade** (*Cascading Failure*)."
            },
            "explanation": [
                "**Bornage temporel obligatoire des sockets sortants (`timeout`).** Tout appel réseau synchrone exécuté au sein d'un worker Flask doit impérativement imposer un délai maximal, que ce soit via `urllib.request.urlopen(..., timeout=5.0)` ou le tuple connexion/lecture `requests.get(..., timeout=(2.0, 5.0))`. Passé cette échéance, Python relâche immédiatement le descripteur TCP et lève une exception contrôlée, préservant la capacité de traitement des workers Gunicorn.",
                "**Capture structurée des codes d'erreur `4xx` et `5xx` via `HTTPError`.** Dans la bibliothèque standard Python, `urllib.request` lève automatiquement `urllib.error.HTTPError` dès que le serveur distant émet un statut supérieur ou égal à `400`. L'encapsulation dans un bloc `try / except` permet d'extraire à la fois `err.code` et le flux `err.read()`, afin de désérialiser proprement le diagnostic RFC 7807 retourné par le partenaire.",
                "**Recul exponentiel (`Exponential Backoff`) face aux pannes transitoires.** Lorsqu'une dépendance externe répond par `502 Bad Gateway`, `503 Service Unavailable` ou `504 Gateway Timeout`, marteler sa route dans une boucle immédiate amplifie l'effondrement du service distant. Un client résilient espace ses tentatives selon une progression géométrique (`1 s`, `2 s`, `4 s`, `8 s`) assortie d'une légère gigue aléatoire (*jitter*), ou respecte scrupuleusement l'en-tête `Retry-After` en présence d'un statut `429`.",
                "**Discipline équivalente côté navigateur avec `fetch` et `AbortSignal.timeout()`.** Les clients frontaux JavaScript consommant votre API Flask obéissent aux mêmes impératifs de résilience : chaque appel `fetch()` doit transmettre le jeton dans `Authorization: 'Bearer ' + token`, vérifier explicitement `response.ok` et armer un coupe-circuit `signal: AbortSignal.timeout(5000)` pour éviter de geler l'interface utilisateur."
            ],
            "code": _read("01_client_python_auth.py"),
            "line_explanations": [
                {"lines": "12-28", "text": "Fonction générique `appeler_api_json` imposant un `timeout=5.0` et capturant `urllib.error.HTTPError` pour extraire le statut et le JSON d'erreur."},
                {"lines": "31-37", "text": "Étape 1 : Authentification `POST /api/sandbox/auth/token` pour obtenir l'`access_token`."},
                {"lines": "40-45", "text": "Étape 2 : Appel `GET /api/sandbox/auth/profil` en injectant l'en-tête `Authorization: Bearer <mon_token>`."}
            ],
            "python_runner": {
                "prompt": "Exécutez ce client résilient en direct contre le serveur du laboratoire (`day_5/01_client_python_auth.py`) :",
                "initial_code": _read("01_client_python_auth.py")
            },
            "vscode_instructions": {
                "filename": "day_5/01_client_python_auth.py",
                "steps": [
                    "Ouvrir `day_5/01_client_python_auth.py` dans l'éditeur.",
                    "Exécuter `.venv/bin/python day_5/01_client_python_auth.py` pendant que le serveur principal tourne."
                ]
            }
        },
        {
            "id": "d5-l2",
            "file": "day_5/03_architecture_blueprints.py",
            "title": "5.2 — Architecture Modulaire (`Blueprints`), Cycle de Vie d'API (`/api/v1` vs `/api/v2`, Breaking Changes, RFC 8594) & Sondes `/api/health`",
            "duration": "75 min",
            "analogy": {
                "title": "Pourquoi voit-on presque toujours `/api/v1` et si rarement `/api/v2` ?",
                "text": "Une interrogation légitime revient chez de nombreux architectes : pourquoi la majorité des grandes plateformes mondiales — OpenAI `/v1/chat/completions`, Stripe `/v1/charges` ou Kubernetes `/apis/apps/v1` — conservent-elles le préfixe `v1` durant près d'une décennie tout en l'imposant dès le premier jour ? L'explication réside d'abord dans la **Loi de Postel (`Tolerant Reader`)** : enrichir une réponse JSON d'un nouvel attribut ou publier une route inédite constitue une évolution rétrocompatible que les clients existants tolèrent sans la moindre modification, permettant à `v1` de mûrir pendant des années.\n\nLe segment `/api/v1` joue néanmoins le rôle d'**assurance-vie architecturale** dès qu'une refonte impose une rupture de contrat, comme remplacer l'entier `\"duree\": 5` par l'objet structuré `\"duree\": {\"valeur\": 5, \"unite\": \"jours\"}`. Grâce aux `Blueprints` de Flask, l'équipe monte alors `/api/v2` en parallèle au sein du même serveur Gunicorn sans briser les dizaines de milliers de terminaux mobiles déjà déployés."
            },
            "explanation": [
                "**Frontière exacte entre évolution rétrocompatible (`v1`) et rupture de contrat (`v2`).** Ajouter une clé supplémentaire dans un objet JSON de sortie, exposer un nouvel endpoint (`GET /api/v1/certificats`) ou introduire un filtre optionnel (`?lang=fr`) préserve intégralement les intégrations existantes et s'opère directement dans `/api/v1`. En revanche, supprimer ou renommer un attribut (`intitule` vers `titre`), modifier le type d'une propriété ou exiger un champ obligatoire inédit en entrée d'un `POST` constitue un *Breaking Change* qui impose l'ouverture d'une branche `/api/v2`.",
                "**Coexistence par `Blueprints` Flask et signalisation d'obsolescence RFC 8594.** On ne débranche jamais brutalement `/api/v1` le jour du lancement de `/api/v2` : les deux modules (`formations_v1_bp` et `formations_v2_bp`) sont enregistrés côte à côte par `app.register_blueprint()` au-dessus de la même couche métier. Pendant toute la période de transition, un crochet `@formations_v1_bp.after_request` injecte les en-têtes normatifs IETF **RFC 8594** — `Deprecation: true`, la date d'extinction `Sunset` au-delà de laquelle la route renverra `410 Gone`, et `Link: </api/v2/formations>; rel=\"successor-version\"`.",
                "**Comparaison des quatre stratégies industrielles de versionnement.** Le préfixe d'URI (`/api/v1/...`) domine plus de 80 % des architectures REST car il est immédiatement lisible dans les journaux d'accès, les navigateurs et les blocs `location` de Nginx. Les alternatives consistent à figer le contrat par en-tête daté (`Stripe-Version: 2026-11-01`), à négocier un type MIME vendeur (`Accept: application/vnd.isgp.v2+json`), ou à passer un paramètre `?version=2` — cette dernière option étant déconseillée car elle fragmente les clés de cache HTTP.",
                "**Patron Application Factory (`create_app()`) et sondes d'orchestration `/api/health`.** Encapsuler l'instanciation de Flask et le montage des Blueprints dans une fabrique `def create_app():` élimine les importations circulaires et permet d'instancier à la demande une application isolée pour les tests ou pour Gunicorn (`gunicorn \"app:create_app()\"`). On y rattache systématiquement deux sondes distinctes : `/api/health/live` (*Liveness*) atteste que l'interpréteur Python répond, tandis que `/api/health/ready` (*Readiness*) valide la connectivité SQLite/SQL avant que l'équilibreur de charge n'achemine du trafic."
            ],
            "code": _read("03_architecture_blueprints.py"),
            "line_explanations": [
                {"lines": "18-22", "text": "Source de données métier unique (`CATALOGUE_METIER`) partagée entre le portail Web Jinja2, l'API `v1` et l'API `v2`."},
                {"lines": "25-40", "text": "Blueprint Web Jinja2 `web_bp` (`/portail`) servant le template `day_5/templates/portail_blueprint.html`."},
                {"lines": "46-66", "text": "Blueprint `formations_v1_bp` (`/api/v1/formations`) conservant le schéma plat historique (`duree: 5`) et injectant les en-têtes RFC 8594 (`Deprecation: true`, `Sunset`, `Link`)."},
                {"lines": "73-98", "text": "Blueprint `formations_v2_bp` (`/api/v2/formations`) exposant le nouveau schéma structuré (`duree: {valeur, unite, heures_pedagogiques}`, enveloppe `meta` + `data` + `links`)."},
                {"lines": "102-128", "text": "Blueprint `sante_bp` (`/api/health/live` & `/ready`) et fonction `create_app()` enregistrant les Blueprints et la racine `GET /`."}
            ],
            "sandbox_preset": {
                "label": "Comparer API v1 (Dépréciée RFC 8594) vs API v2 : GET /api/v1/sandbox/formations",
                "method": "GET",
                "url": "/api/v1/sandbox/formations",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez `day_5/03_architecture_blueprints.py` pour comparer en direct les en-têtes et schémas JSON de `/api/v1/formations` et `/api/v2/formations` :",
                "initial_code": _read("03_architecture_blueprints.py")
            },
            "vscode_instructions": {
                "filename": "day_5/03_architecture_blueprints.py",
                "steps": [
                    "Ouvrir `day_5/03_architecture_blueprints.py` dans l'éditeur.",
                    "Comparer la structure du champ `duree` entre `lister_formations_v1()` (entier `5`) et `lister_formations_v2()` (objet structuré) et observer les en-têtes `Deprecation` et `Sunset`."
                ]
            }
        },
        {
            "id": "d5-l3",
            "file": "day_5/04_tests_et_production.py",
            "title": "5.3 — Tests Automatisés (`test_client`), Spécification OpenAPI & Déploiement Production WSGI (`Gunicorn`)",
            "duration": "65 min",
            "analogy": {
                "title": "Pourquoi `app.run()` est strictement interdit en production",
                "text": "Dès que vous exécutez `python app.py`, Werkzeug affiche un avertissement explicite : *\"WARNING: This is a development server. Do not use it in a production deployment.\"* Ce serveur embarqué privilégie le rechargement à chaud et l'inspection locale, mais il n'est ni dimensionné pour absorber des centaines de sockets concurrents ni durci contre les attaques par épuisement lent de connexions (*Slowloris*).\n\nEn exploitation réelle, l'application Flask est systématiquement orchestrée par un **serveur WSGI pré-forké industriel tel que Gunicorn** (ou uWSGI), lui-même abrité derrière un **proxy inverse frontal** (**Nginx**, **Caddy** ou **Cloudflare**)."
            },
            "explanation": [
                "**Topologie de production à trois étages (`Nginx -> Gunicorn -> Flask`).** En périphérie, le proxy inverse **Nginx** ou **Caddy** assure la terminaison TLS/HTTPS, la compression Gzip/Brotli, le service des actifs statiques et la mise en tampon des clients lents. Il relaie ensuite les requêtes propres vers le processus maître **Gunicorn**, qui supervise plusieurs processus **Workers** parallèles (`gunicorn -w 4 -b 127.0.0.1:8000 \"app:create_app()\"`) invoquant chacun votre objet appelable Flask selon le protocole **WSGI (`PEP 3333`)** : si un worker exécute une requête SQL lourde, les trois autres continuent de servir les clients sans latence.",
                "**Qualification automatisée en mémoire vive avec `app.test_client()`.** Vérifier manuellement trente endpoints à la souris après chaque remaniement est lent et faillible. La méthode native `app.test_client()` instancie le client de test Werkzeug (`werkzeug.test.Client`) qui synthétise un dictionnaire `environ` WSGI complet et invoque directement les routes, middlewares et gestionnaires d'erreurs Flask en mémoire vive en quelques millisecondes — sans ouvrir le moindre port TCP — pour valider par `assert` chaque code HTTP et chaque clé JSON.",
                "**Publication formelle du contrat par spécification OpenAPI 3.0.** Au-delà des tests internes, industrialiser une API implique d'exposer un descripteur lisible par machine (`openapi.json` ou `openapi.yaml`). Ce contrat recense de manière exhaustive les chemins, verbes, schémas d'entrée/sortie et exigences d'authentification afin d'aligner automatiquement les équipes clientes et les passerelles d'entreprise."
            ],
            "code": _read("04_tests_et_production.py"),
            "line_explanations": [
                {"lines": "15-22", "text": "Route API JSON `POST /api/calcul-taxe` lisant `request.get_json()` et validant `montant_ht` (`422` si négatif)."},
                {"lines": "26-34", "text": "Route Formulaire HTML `POST /formulaire-taxe` lisant `request.form.get('montant_ht', type=float)` et rendant `day_5/templates/resultat_taxe.html`."},
                {"lines": "43-56", "text": "Tests 1 et 2 : Vérification automatisée par `assert` de la route API JSON (`client.post(..., json={...})`)."},
                {"lines": "58-63", "text": "Test 3 : Vérification automatisée de la soumission du formulaire HTML (`client.post(..., data={...})`) et du rendu Jinja2."}
            ],
            "python_runner": {
                "prompt": "Exécutez la suite de tests automatisés `app.test_client()` en direct :",
                "initial_code": _read("04_tests_et_production.py")
            },
            "vscode_instructions": {
                "filename": "day_5/04_tests_et_production.py",
                "steps": [
                    "Ouvrir `day_5/04_tests_et_production.py` dans l'éditeur.",
                    "Ajouter un 3ème test vérifiant le comportement si le corps JSON est vide `{}`."
                ]
            }
        },
        {
            "id": "d5-l4",
            "file": "day_5/05_swagger_openapi_ui.py",
            "title": "5.4 — Documentation Interactive & Contrat d'API : Swagger UI (`/api/docs`) & OpenAPI 3.0 (`/api/openapi.json`)",
            "duration": "60 min",
            "analogy": {
                "title": "Les plans d'architecte cotés (OpenAPI) et la maquette interactive 3D visitable (Swagger UI)",
                "text": "Une API dépourvue de documentation synchronisée se transforme vite en boîte noire opaque, condamnant les équipes mobiles et les partenaires à deviner par essais successifs l'orthographe des attributs JSON ou le format des en-têtes requis.\n\nLa spécification internationale **OpenAPI 3.0** joue le rôle de plan d'architecte coté (au format JSON ou YAML), tandis que **Swagger UI** en projette instantanément une maquette interactive navigable dans le navigateur où tout intégrateur peut inspecter les schémas et actionner les boutons **« Authorize »** et **« Try it out »** en direct."
            },
            "explanation": [
                "**Clarification terminologique entre la norme `OpenAPI` et l'outillage `Swagger`.** Jusqu'en 2015, le standard portait le nom *Swagger 2.0* avant d'être confié à l'OpenAPI Initiative (Linux Foundation) sous l'appellation officielle **OpenAPI Specification (`OAS 3.0` / `3.1`)**, matérialisée par le fichier `/api/openapi.json`. Le terme **Swagger** désigne désormais la suite d'outils gravitant autour de cette norme : **Swagger UI** pour le portail d'exploration interactif `/api/docs`, **Swagger Editor** pour la rédaction assistée et **Swagger Codegen** pour la génération automatique de SDK clients.",
                "**Architecture en cinq sections d'un contrat OpenAPI 3.0.** Un descripteur conforme s'articule autour de `openapi` et `info` (version sémantique et identité du service), du tableau `servers` listant les environnements Werkzeug local et Gunicorn de production, et de l'arbre `paths` décrivant chaque URI paramétrée `{id}`, ses verbes, son `requestBody` et ses `responses`. Pour bannir toute redondance, `components.schemas` factorise les modèles métier référencés par `$ref` (`Formation`, `ErreurRFC7807`), tandis que `components.securitySchemes` active le cadenas **« Authorize »** pour injecter `BearerAuth` ou `ApiKeyAuth`.",
                "**Arbitrage méthodologique en entreprise : `Code-First` face à `Design-First`.** Dans l'approche *Code-First*, le développeur annote ses vues et schémas Python à l'aide d'extensions Flask dédiées telles que `Flask-Smorest`, `APIFlask` ou `Flasgger`, qui synthétisent dynamiquement `/api/openapi.json`. Dans l'approche *Design-First* (*Contract-First*), les architectes valident d'abord le fichier `openapi.yaml` en amont du sprint, ce qui permet aux équipes Frontend/Mobile et Backend Flask de développer en parallèle sur un contrat figé."
            ],
            "code": _read("05_swagger_openapi_ui.py"),
            "line_explanations": [
                {"lines": "31-52", "text": "En-tête du contrat OpenAPI 3.0.3 (`info`, `servers`, `tags`) définissant l'identité et les environnements de l'API."},
                {"lines": "55-68", "text": "`securitySchemes` configure les deux cadenas d'authentification dans Swagger UI : `BearerAuth` (`Authorization: Bearer`) et `ApiKeyAuth` (`X-API-Key`)."},
                {"lines": "69-100", "text": "`components.schemas` centralise les schémas JSON (`Formation`, `FormationInput`, `ErreurRFC7807`) référencés ensuite par `$ref`."},
                {"lines": "103-191", "text": "`paths` documente chaque route, ses paramètres (`in: query`, `in: path`), le `requestBody` et les réponses HTTP (`200`, `201`, `401`, `404`, `422`)."},
                {"lines": "197-212", "text": "Routes Flask `/api/openapi.json` (contrat machine) et `/api/docs` (interface graphique interactive **Swagger UI**)."}
            ],
            "sandbox_preset": {
                "label": "Inspecter le Contrat OpenAPI 3.0 : GET /api/openapi.json",
                "method": "GET",
                "url": "/api/openapi.json",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez le générateur et validateur de contrat OpenAPI 3.0 (`day_5/05_swagger_openapi_ui.py`) :",
                "initial_code": _read("05_swagger_openapi_ui.py")
            },
            "vscode_instructions": {
                "filename": "day_5/05_swagger_openapi_ui.py",
                "steps": [
                    "Ouvrir `day_5/05_swagger_openapi_ui.py` dans VS Code ou Antigravity IDE.",
                    "Ouvrir également le portail interactif réel du laboratoire sur `http://127.0.0.1:5000/api/docs` pour tester Swagger UI en direct."
                ]
            }
        },
        {
            "id": "d5-l5",
            "file": "day_5/02_pagination_filtrage_production.py",
            "title": "5.5 — Ingénierie de Collection en Production (100 % Flask) : Pagination `Offset/Limit` vs `Cursor (Keyset)`, Filtrage & Tri Sécurisé",
            "duration": "55 min",
            "analogy": {
                "title": "Feuilleter un annuaire par numéro de page (Offset) vs Reprendre exactement après le dernier numéro lu (Curseur)",
                "text": "Lorsqu'une table SQLite ou PostgreSQL capitalise 500 000 écritures comptables et qu'un client sollicite `GET /api/v1/factures` sans garde-fou, le worker Gunicorn tente de matérialiser 500 000 objets Python, alloue 250 Mo de JSON et s'écroule par dépassement mémoire (*Out Of Memory*).\n\nÀ l'échelle industrielle, toute collection choisit délibérément entre deux patrons de découpage : la pagination **`Offset/Limit`** (`?page=2&per_page=20`), idéale pour les tableaux de bord numérotés de taille modérée, et la pagination par **`Curseur / Keyset`** (`?after_id=1042&limit=20`), indispensable pour maintenir un temps de réponse constant `O(1)` sur plusieurs millions de lignes."
            },
            "explanation": [
                "**Coût asymptotique `O(N)` de la pagination classique `Offset / Limit`.** La formule `offset = (page - 1) * per_page` traduite en `SELECT * FROM formations LIMIT 20 OFFSET 20` offre l'avantage ergonomique d'un accès direct aux numéros de pages (« Page 1, 2... 15 »). En contrepartie, une requête `OFFSET 500000` contraint le moteur SQL à balayer et écarter séquentiellement 500 000 enregistrements en mémoire avant de livrer les 20 suivants, dégradant linéairement la latence au fil de la profondeur.",
                "**Latence constante `O(1)` de la pagination par `Curseur / Keyset`.** Au lieu de sauter un volume arbitraire de lignes, le client renvoie le curseur du dernier élément reçu (`?after_id=1042&limit=20`), ce qui génère la requête `SELECT * FROM formations WHERE id > 1042 ORDER BY id ASC LIMIT 20`. Appuyé sur l'arbre `B-Tree` de l'index primaire `id`, le moteur relationnel se positionne instantanément en moins d'une milliseconde même au millionième enregistrement et élimine tout décalage ou doublon lorsqu'une insertion survient entre deux pages.",
                "**Verrouillage par liste blanche du tri dynamique (`CHAMPS_TRI_AUTORISES`).** Supporter une convention expressive comme `?sort=-tarif_dzd` (décroissant) ou `?sort=duree_jours` (croissant) interdit formellement d'interpoler le paramètre brut dans une clause SQL `ORDER BY`, où les marqueurs `?` ne peuvent pas substituer des noms d'identifiants. La vue Flask sépare le préfixe `-` puis vérifie l'appartenance stricte du nom de colonne à l'ensemble figé `CHAMPS_TRI_AUTORISES = {'id', 'duree_jours', 'tarif_dzd', 'titre'}`, rejetant toute clé étrangère au contrat avec un statut `422`."
            ],
            "code": _read("02_pagination_filtrage_production.py"),
            "line_explanations": [
                {"lines": "23-24", "text": "Liste blanche stricte `CHAMPS_TRI_AUTORISES` protégeant le tri dynamique contre toute injection ou `KeyError`."},
                {"lines": "28-70", "text": "Route `GET /api/v1/catalogue/offset` : filtrage multi-critères (`domaine`, `duree_min`), tri sécurisé (`?sort=-tarif_dzd`) et enveloppe `meta` / `data` / `links`."},
                {"lines": "74-94", "text": "Route `GET /api/v1/catalogue/cursor` : pagination par curseur (`?after_id=2&limit=2`) renvoyant `meta.next_cursor`."}
            ],
            "sandbox_preset": {
                "label": "Tester la Pagination v2 : GET /api/v2/sandbox/formations?page=1&per_page=2",
                "method": "GET",
                "url": "/api/v2/sandbox/formations?page=1&per_page=2",
                "body": ""
            },
            "python_runner": {
                "prompt": "Exécutez le comparatif entre Pagination Offset/Limit (avec tri `-tarif_dzd`) et Pagination par Curseur (`after_id`) en Flask :",
                "initial_code": _read("02_pagination_filtrage_production.py")
            },
            "vscode_instructions": {
                "filename": "day_5/02_pagination_filtrage_production.py",
                "steps": [
                    "Ouvrir `day_5/02_pagination_filtrage_production.py` dans l'éditeur.",
                    "Tester le comportement si un client envoie un champ de tri non autorisé comme `?sort=mot_de_passe` (`422`)."
                ]
            }
        }
    ]
}
