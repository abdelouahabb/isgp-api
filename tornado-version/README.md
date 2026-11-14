# ISGP — Volume III — Edition Tornado (Event-Loop Asynchrone, Portail Web HTML & API REST)

Plateforme pedagogique et corpus d'exercices progressifs dedies au framework **Tornado** (`tornado.web.Application`, `tornado.web.RequestHandler`, `tornado.ioloop.IOLoop`, `tornado.escape.json_decode`, `self.set_secure_cookie` / `self.get_secure_cookie`, `tornado.template`, `tornado.httpclient.AsyncHTTPClient`, `tornado.testing.AsyncHTTPTestCase`).

Chaque serveur HTTP du cursus expose simultanement ses routes **API JSON** et un **Portail Web HTML interactif sur `GET /`** (rendu via `tornado.template`, port `8889` par defaut ou variable `PORT`).

---

## 1. Architecture Pedagogique du Volume III

### A. Chapitre 0 — Traite Fondamental avant Python (`data/chapter_0_literature.py`)
Monographie architecturale precedant l'ecriture du code :
- Histoire intellectuelle des APIs, philosophie du decouplage et familles d'interfaces (Syscalls POSIX, DB-API 2.0, REST, GraphQL, gRPC, Webhooks, WebSockets).
- Grand traite du vocabulaire normatif HTTP/1.1, URI, MIME, idempotence et erreurs structurees **RFC 7807**.
- Gouvernance des contrats **OpenAPI 3.0 / 3.1** vs documentation interactive **Swagger UI** et cycle **Sunset RFC 8594**.
- Topologies reseau **Nord-Sud vs Est-Ouest**, **Zero-Trust / mTLS** et architecture **OAuth 2.0 / OIDC / PKCE**.

### B. Parcours Progressif Cumulatif "Zero to Hero" (`zero_to_hero/`)
Fil conducteur en **6 etapes cumulatives** faisant evoluer la meme application (*Portail Web & API Catalogue Formations ISGP*), enseignant conjointement la construction d'APIs REST et de sites Web HTML qui consomment ces APIs :
1. **`etape_01_hello_world.py`** : Serveur minimal unifiant `GET /` (`templates/etape_01_hello.html`) et `GET /api/bonjour`.
2. **`etape_02_routes_et_site_catalogue.py`** : Routage Regex `([0-9]+)`, filtrage `?domaine=&tri=`, pagination et vue detail dynamique (`templates/etape_02_catalogue.html`).
3. **`etape_03_crud_et_validation_rfc7807.py`** : Mutations `POST`, `PUT`, `PATCH`, `DELETE` et validation stricte `422` `application/problem+json` avec banniere d'erreur en direct (`templates/etape_03_crud.html`).
4. **`etape_04_persistance_sqlite_wal.py`** : Persistance relationnelle `sqlite3` (`PRAGMA journal_mode=WAL`, `foreign_keys=ON`, `busy_timeout=5000`) deportee hors de l'`IOLoop` via `run_in_executor(ThreadPoolExecutor)` (`templates/etape_04_sqlite.html`).
5. **`etape_05_securite_auth_rbac_cookies.py`** : Cookies signes Tornado (`set_secure_cookie`, `HttpOnly`, `SameSite=Lax`), jetons Bearer `HMAC-SHA256` (`hmac.compare_digest`), `401` (`WWW-Authenticate`) vs `403` RBAC (`stagiaire` / `admin`) et quota glissant `429` (`Retry-After`) (`templates/etape_05_securite.html`).
6. **`etape_06_hero_complet_swagger.py`** : Application finale Hero integrant le contrat `/api/openapi.json`, **Swagger UI (`/api/docs`)**, la sonde `/health`, le journal d'audit (`log_function`) et le portail complet (`templates/etape_06_hero.html`).

---

## 2. Repertoire des 30 Scripts par Journee (`day_0/` a `day_5/`)

- **`day_0/` — Mise a Niveau Python pour les APIs**
  - `01_variables_et_types.py` : Types scalaires compatibles JSON (`str`, `int`, `float`, `bool`, `None`) et f-strings.
  - `02_listes_et_dictionnaires.py` : Collections imbriquees et lecture defensive `.get()`.
  - `03_fonctions.py` : Fonctions metier, parametres par defaut et validation.
  - `04_exceptions_et_decorateurs.py` : Gestion d'erreurs `try / except` et decorateurs Python.

- **`day_1/` — Protocoles Web, URI, Trames HTTP/1.1, JSON & Outils**
  - `01_html_vs_json.py` : Comparateur Tornado en direct (`GET /`, `/meteo/html`, `/meteo/soap`, `/api/v1/meteo`).
  - `02_serialisation_json.py` : Enveloppes JSON normalisees (`json.dumps` & `tornado.escape.json_decode`).
  - `03_analyseur_uri_et_reseau.py` : Decomposition RFC 3986 (`urllib.parse` & `tornado.httputil.url_concat`).
  - `04_trame_http_et_headers.py` : Anatomie d'une trame HTTP/1.1 brute (JSON vs Formulaire HTML).
  - `05_outils_curl_postman_httpie.py` : Automatisation des essais HTTP avec `curl`, Postman et HTTPie.

- **`day_2/` — Serveurs Tornado, Routage Regex, Pagination, Hooks & Templates**
  - `01_serveur_minimal_tornado.py` : Premier serveur `Application` & `RequestHandler` (`GET /`, `/accueil`, `/api/bonjour`, `/api/v1/modules`).
  - `02_routes_et_parametres.py` : Groupes capturants Regex et Query Parameters (`self.get_query_argument`).
  - `03_pagination_filtrage_tri.py` : Filtrage, tri par liste blanche et pagination (`GET /`, `/api/v1/formations`).
  - `04_middlewares_et_audit_log.py` : Cycle `set_default_headers()`, `prepare()` et `on_finish()` avec `X-Request-ID`.
  - `05_jinja_et_formulaires_html.py` : Controleur hybride HTML/JSON (`self.get_body_argument`) et upload multipart (`self.request.files`).

- **`day_3/` — Ingenierie CRUD, SQLite, Idempotence & Erreurs Globales**
  - `01_api_crud_memoire.py` : Validation entrante et reponses `422` RFC 7807 (`application/problem+json`).
  - `02_api_crud_sqlite.py` : Persistance SQLite parametree `?` (anti-injection SQL) avec interface Web et JSON.
  - `03_put_patch_et_idempotence.py` : Distinction `PUT` vs `PATCH` et protection `POST` par `Idempotency-Key`.
  - `04_gestion_erreurs_globale.py` : Surcharge de `write_error()` et `default_handler_class` (`404`, `405`, `500` JSON).

- **`day_4/` — Securite : API Keys, Bearer HMAC, Rate Limiting, RBAC, CORS & Cookies Signes**
  - `01_secrets_et_api_key.py` : Variables d'environnement et authentification `X-API-Key` (`hmac.compare_digest`).
  - `02_bearer_tokens_signes.py` : Emission et verification de jetons `Bearer` horodates (`401`).
  - `03_rate_limiting_429.py` : Limiteur de debit a fenetre glissante (`429 Too Many Requests`, `Retry-After`).
  - `04_refresh_token_et_rbac.py` : Double jeton (`Access` + `Refresh`), liste de revocation et decorateur `@exiger_role`.
  - `05_cors_webhooks_headers.py` : Liste blanche CORS (`options()`), `max_body_size` et verification HMAC-SHA256 de Webhooks.
  - `06_authn_vs_authz_scopes.py` : Laboratoire AuthN (`401`) vs AuthZ (`403` RBAC, Scopes OAuth2 et protection Anti-BOLA).
  - `07_cookies_et_sessions_securisees.py` : Cookies signes natifs Tornado (`set_secure_cookie`, `HttpOnly`, `SameSite`).

- **`day_5/` — Client Asynchrone, Pagination Production, Modularite, Tests & OpenAPI**
  - `01_client_python_auth.py` : Consommation non-bloquante via `tornado.httpclient.AsyncHTTPClient`.
  - `02_pagination_filtrage_production.py` : Comparatif `Offset/Limit` vs pagination haute performance par `Curseur (Keyset)`.
  - `03_architecture_blueprints.py` : Architecture modulaire par domaine, coexistence `/api/v1` (RFC 8594 `Sunset`) et `/api/v2`, sondes `/api/health/*`.
  - `04_tests_et_production.py` : Suite automatisee `tornado.testing.AsyncHTTPTestCase` et deploiement `HTTPServer(xheaders=True)`.
  - `05_swagger_openapi_ui.py` : Contrat OpenAPI 3.0.3 (`/api/openapi.json`), portail Swagger UI (`/api/docs`) et accueil Web (`GET /`).

---

## 3. Execution Interactive et Verification Automatique

```bash
# Lancer une etape Zero-to-Hero ou un serveur de journee sur http://127.0.0.1:8889/
.venv/bin/python tornado-version/zero_to_hero/etape_06_hero_complet_swagger.py
.venv/bin/python tornado-version/day_5/05_swagger_openapi_ui.py

# Executer l'auto-test non-bloquant (--once) sur n'importe quel script
.venv/bin/python tornado-version/zero_to_hero/etape_06_hero_complet_swagger.py --once
```
