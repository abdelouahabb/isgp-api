# ISGP — Volume II : Développement d'APIs et Services Web (Édition FastAPI, Pydantic v2 & Uvicorn ASGI)

Plateforme pédagogique et recueil de travaux pratiques exécutables dédiés au **Volume II — Édition FastAPI, Pydantic v2, Starlette & Uvicorn (ASGI)** du séminaire **« Développement d'APIs et services web »**.

Ce volume associe systématiquement **la construction d'APIs REST JSON typées** (contrats Pydantic v2, erreurs RFC 7807, OpenAPI 3.1.0) et **la réalisation de véritables sites Web HTML interactifs** rendus par `Jinja2Templates` sur `GET /`, qui exposent et consomment ces mêmes APIs en direct via `fetch()`.

---

## Démarrage Rapide

### 1. Plateforme Web Principale (PWA Support de Cours, Console Formateur & Sandbox)

Depuis la racine du dépôt (`/home/abdelouahab/isgp-api`) :

```bash
/home/abdelouahab/isgp-api/.venv/bin/python app.py
```

### 2. Parcours Progressif Cumulatif Zero-to-Hero (`fastapi-version/zero_to_hero/`)

Pour lancer en direct l'une des 6 étapes évolutives (Portail Web `GET /` + API REST + Swagger UI `/docs` sur `http://127.0.0.1:8001`) :

```bash
/home/abdelouahab/isgp-api/.venv/bin/python fastapi-version/zero_to_hero/etape_01_hello_world.py
/home/abdelouahab/isgp-api/.venv/bin/python fastapi-version/zero_to_hero/etape_06_hero_complet_swagger.py
```

Ou via la CLI `uvicorn` avec rechargement automatique :

```bash
/home/abdelouahab/isgp-api/.venv/bin/uvicorn etape_06_hero_complet_swagger:app \
  --app-dir fastapi-version/zero_to_hero \
  --host 127.0.0.1 \
  --port 8001 \
  --reload
```

---

## Architecture Pédagogique du Volume II (`fastapi-version/`)

### A. Chapitre 0 — Traité Fondamental d'Ingénierie des APIs (`data/chapter_0_literature.py`)

Monographie conceptuelle étudiée **avant la première ligne de Python** : histoire intellectuelle et philosophie du découplage par les APIs, taxonomie normative du vocabulaire HTTP/REST, distinction entre contrat formel **OpenAPI 3.1** et documentation humaine (**Swagger UI**, **ReDoc**), topologie réseau **Nord-Sud vs Est-Ouest** (API Gateway, mTLS, Zero-Trust) et architecture **OAuth 2.0 / OIDC / PKCE**. Complétée par un référentiel technique de **69 fiches en prose de référence** (`data/glossary.py`).

### B. Fil Conducteur Cumulatif Zero-to-Hero (`zero_to_hero/`)

Six scripts progressifs construisant **la même application métier** (*Portail Web & API Catalogue des Formations ISGP*), chacun doté de son gabarit HTML Jinja2 (`zero_to_hero/templates/`) et d'un banc d'auto-test asynchrone `httpx.AsyncClient` + `ASGITransport` (`--once`) :

1. **`etape_01_hello_world.py`** : Serveur ASGI minimal, page d'accueil `GET /` (`Jinja2Templates`), route typée `GET /api/bonjour` et documentation automatique `/docs`.
2. **`etape_02_routes_et_site_catalogue.py`** : Catalogue filtrable et triable (`Query(...)`), pagination structurée (`meta` / `data`), validation de chemin `Path(..., ge=1)` et fiche détail en direct sur `GET /`.
3. **`etape_03_crud_et_validation_rfc7807.py`** : Contrats Pydantic v2 (`BaseModel`, `Field`, `ConfigDict(extra="forbid")`), opérations `POST`, `PUT`, `PATCH` (`exclude_unset=True`), `DELETE` et gestionnaire global **RFC 7807** (`422 application/problem+json`).
4. **`etape_04_persistance_sqlite_wal.py`** : Persistance transactionnelle `sqlite3` (`PRAGMA journal_mode=WAL`, `foreign_keys=ON`, `busy_timeout=5000`, `check_same_thread=False`) injectée par générateur `Depends(get_db)` (`yield` / `finally`) sur routes synchrones `def`.
5. **`etape_05_securite_auth_rbac_cookies.py`** : Cookies de session signés HMAC (`HttpOnly`, `SameSite="lax"`), jetons `HTTPBearer` HMAC-SHA256 (`hmac.compare_digest`), contrôle d'accès `Depends(exiger_role("admin"))` (`401` + `WWW-Authenticate` vs `403`) et limitation de débit à fenêtre glissante (`429` + `Retry-After`).
6. **`etape_06_hero_complet_swagger.py`** : Architecture complète modulaire (`APIRouter`, cycle de vie `lifespan`, sonde `/health`, middleware `X-Process-Time-Ms`, contrat **OpenAPI 3.1.0** `/openapi.json`, **Swagger UI** `/docs` & `/api/docs`, **ReDoc** `/redoc` et portail Web complet `GET /`).

### C. Programme Structuré en 6 Modules (`day_0/` à `day_5/` — 30 Scripts Exécutables)

Chaque serveur HTTP FastAPI des modules `day_1` à `day_5` expose un **portail Web interactif sur `GET /`** (`day_X/templates/*.html`) permettant de solliciter ses endpoints REST directement depuis le navigateur en complément de Swagger UI (`/docs`) :

- **`day_0/` — Fondations Python & Annotations de Types (4 scripts)** : Variables, conversions sûres, listes et dictionnaires imbriqués, fonctions typées, gestion d'exceptions et décorateurs `@`.
- **`day_1/` — Protocoles Réseau, HTTP/1.1, URI & Sérialisation JSON (5 scripts)** : Comparateur en direct HTML vs SOAP/XML vs REST/JSON (`01_html_vs_json.py`), sérialisation Pydantic v2 (`02`), analyseur d'URI RFC 3986 (`03`), trames brutes HTTP/1.1 (`04`) et clients d'inspection `curl` / Postman / HTTPie (`05`).
- **`day_2/` — Serveur ASGI FastAPI, Routage Typé, Middlewares & Formulaires Jinja2 (5 scripts)** : Serveur minimal HTML + JSON (`01`), paramètres `Path` et `Query` (`02`), pagination/filtrage/tri (`03`), middleware d'audit `X-Request-ID` & `X-Response-Time-Ms` (`04`), formulaires `Form(...)` et `UploadFile` (`05`).
- **`day_3/` — Ingénierie CRUD, Validation RFC 7807, Idempotence & SQLite (4 scripts)** : Validation Pydantic v2 et erreurs `422` RFC 7807 (`01`), persistance SQLite paramétrée avec `Depends(get_db)` (`02`), `PUT` vs `PATCH` (`exclude_unset=True`) et `Idempotency-Key` (`03`), intercepteurs globaux `@app.exception_handler` (`04`).
- **`day_4/` — Sécurité d'API, Jetons Signés, RBAC, Rate Limiting, Webhooks & Cookies (7 scripts)** : `X-API-Key` et `hmac.compare_digest` (`01`), Bearer tokens signés (`02`), Rate Limiting `429 Retry-After` (`03`), Refresh Tokens et `Depends(exiger_role("admin"))` (`04`), `CORSMiddleware` et Webhooks HMAC (`05`), AuthN `401` vs AuthZ `403` / Scopes / Anti-BOLA (`06`), cookies `HttpOnly` et `SameSite` (`07`).
- **`day_5/` — Client Asynchrone, Pagination Production, `APIRouter`, Tests & OpenAPI 3.1 (5 scripts)** : Client résilient `httpx.AsyncClient` avec Exponential Backoff (`01`), pagination Offset/Limit vs Curseur $O(1)$ (`02`), architecture `APIRouter` v1 dépréciée RFC 8594 vs v2 (`03`), suite `TestClient(app)` (`04`), et personnalisation OpenAPI 3.1 / Swagger UI / ReDoc (`05`).

---

## Vérification Automatisée Intégrale (36 Scripts)

Tous les scripts acceptent l'argument `--once` pour exécuter leurs vérifications internes sans bloquer le terminal :

```bash
for f in fastapi-version/day_{0..5}/0*.py fastapi-version/zero_to_hero/etape_*.py; do
  /home/abdelouahab/isgp-api/.venv/bin/python "$f" --once
done
```
