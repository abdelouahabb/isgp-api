# ISGP — Volume III — Édition Tornado (Event-Loop Asynchrone & RequestHandler)

Plateforme pédagogique interactive et fichiers d'exercices structurés par journée de formation (`day_0/` à `day_5/`), dédiée au framework **Tornado (`tornado.web.Application`, `tornado.web.RequestHandler`, `tornado.ioloop.IOLoop`, `tornado.escape.json_decode`, `self.set_secure_cookie` / `self.get_secure_cookie`, `tornado.template`, `tornado.testing`)**.

---

## 1. Structure des Dossiers d'Exercices (VS Code / Antigravity IDE)

Chaque journée de formation possède son propre dossier contenant des scripts Python autonomes, exécutables directement dans le terminal ou depuis votre éditeur :

- **`day_0/` — Mise à Niveau Python**
  - `01_variables_et_types.py` : Variables, types (`str`, `int`, `float`, `bool`, `None`) et f-strings.
  - `02_listes_et_dictionnaires.py` : Listes, dictionnaires imbriqués et accès sécurisé `.get()` dans un `RequestHandler`.
  - `03_fonctions_et_modules.py` : Fonctions, paramètres par défaut et retours multiples.
  - `04_exceptions_et_decorateurs.py` : Gestion d'erreurs `try / except` et compréhension de l'héritage `RequestHandler` et des décorateurs Python.

- **`day_1/` — Fondamentaux Web, HTTP, URI & JSON**
  - `01_html_vs_json.py` : Comparaison entre un handler Tornado renvoyant une page HTML (`self.render`) et un handler renvoyant un flux JSON (`self.write(dict)`).
  - `02_serialisation_json.py` : Sérialisation et désérialisation (`tornado.escape.json_decode` / `json.dumps` / `self.write`).
  - `03_analyseur_uri_et_reseau.py` : Décomposition d'une URI (`urllib.parse`), DNS, Socket TCP et `IOLoop` Tornado.
  - `04_trame_http_et_headers.py` : Anatomie d'une trame HTTP brute, méthodes CRUD et en-têtes (`self.request.headers`, `self.set_header`).
  - `05_outils_curl_postman_httpie.py` : Guide pratique et automatisation des tests avec `curl`, Postman, HTTPie et fichiers `.http`.

- **`day_2/` — Premiers Serveurs Tornado, `RequestHandler`, Routage Regex & Templates**
  - `01_serveur_minimal_tornado.py` : Premier serveur `tornado.web.Application`, `RequestHandler` et sonde de santé `/api/sante`.
  - `02_routes_et_parametres.py` : Groupes de capture Regex d'URL (`r"/api/stagiaires/([0-9]+)"`) et Query Strings (`self.get_query_argument()`).
  - `03_pagination_filtrage_tri.py` : Filtrage multicritères, tri validé par liste blanche et pagination (`page`, `limit`).
  - `04_middlewares_et_audit_log.py` : Cycle de vie Tornado (`prepare()` et `on_finish()`), `X-Request-ID` et chronométrage.
  - `05_jinja_et_formulaires_html.py` : Moteur `tornado.template` (`self.render`), formulaires HTML (`self.get_body_argument`) et upload (`self.request.files`).

- **`day_3/` — APIs RESTful CRUD, SQLite, Idempotence & Gestion Globale d'Erreurs**
  - `01_api_crud_memoire.py` : Opérations CRUD complètes en mémoire (`GET`, `POST`, `PUT`, `DELETE`).
  - `02_api_crud_sqlite.py` : Persistance SQLite ACID avec requêtes paramétrées `?` (anti-injection SQL).
  - `03_put_patch_et_idempotence.py` : Différence entre `PUT` et `PATCH` + clé d'idempotence (`Idempotency-Key`).
  - `04_gestion_erreurs_globale.py` : Validation métier (`422`) et surcharge de `write_error(status_code, **kwargs)` dans un `BaseAPIHandler`.

- **`day_4/` — Sécurité : Secrets, API Keys, Bearer Tokens, Quotas (`429`), RBAC, CORS & Secure Cookies**
  - `01_secrets_et_api_key.py` : Variables d'environnement et authentification `X-API-Key` en temps constant (`hmac.compare_digest`).
  - `02_bearer_tokens_signes.py` : Émission et vérification de `Bearer Tokens` signés avec expiration (`401 Unauthorized`).
  - `03_rate_limiting_429.py` : Limitation de débit par IP (`429 Too Many Requests`, `X-RateLimit-*`, `Retry-After`).
  - `04_refresh_token_et_rbac.py` : Architecture `Access Token` + `Refresh Token` (révocable) et contrôle d'accès par rôle (`RBAC` — `403 Forbidden`).
  - `05_cors_webhooks_headers.py` : En-têtes de sécurité OWASP, pré-vérification `CORS` (`def options(self)`) et vérification HMAC-SHA256 des Webhooks.
  - `07_cookies_et_sessions_securisees.py` : Cookies signés et horodatés nativement par Tornado (`cookie_secret`, `self.set_secure_cookie`, `self.get_secure_cookie`) et double soumission CSRF (`_xsrf`).

- **`day_5/` — Consommation d'API (`AsyncHTTPClient`), Comparatif, Routage Modulaire (`URLSpec`), Tests & Production**
  - `01_client_python_auth.py` : Client asynchrone non-bloquant `tornado.httpclient.AsyncHTTPClient` (agrégation parallèle `asyncio.gather`).
  - `02_pagination_filtrage_production.py` : Comparaison architecturale **Flask (WSGI)** vs **FastAPI (ASGI)** vs **Tornado (`IOLoop` & `RequestHandler`)**.
  - `03_architecture_blueprints.py` : Découpage modulaire d'une grande application avec `tornado.web.URLSpec` et sous-modules de routes.
  - `04_tests_et_production.py` : Suite de tests automatisés (`tornado.testing.AsyncHTTPTestCase`), sondes `/health` et serveur multi-processus (`HTTPServer(xheaders=True)`).
  - `05_swagger_openapi_ui.py` : Contrat OpenAPI 3.0.3 (`/api/openapi.json`) et portail interactif Swagger UI (`/api/docs`).

---

## 2. Démarrer la Plateforme Interactive (Port 8888)

```bash
python app.py
```

Puis ouvrez **http://localhost:8888** dans votre navigateur.
