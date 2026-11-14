# Parcours Progressif "Zero to Hero" — Tornado (Portail Web HTML + API REST)

Ce dossier propose un **fil conducteur cumulatif en 6 etapes** sur une meme application metier (**Portail Web & API Catalogue des Formations ISGP**). Chaque etape enrichit le socle precedent afin d'enseigner simultanement la conception d'**APIs REST normalisees** et de **Sites Web HTML (`tornado.template`)** consommant et exposant ces APIs.

---

## Les 6 Etapes Cumulatives

1. **`etape_01_hello_world.py`** (~60 lignes) — *Zero / Hello World*
   - `AccueilHandler` (`GET /`) rendant `templates/etape_01_hello.html` avec interrogation en direct de `GET /api/bonjour` (`BonjourApiHandler`).
2. **`etape_02_routes_et_site_catalogue.py`** — *Routage Regex, Filtrage, Tri, Pagination & Vue Detail*
   - Enrichit l'Etape 1 avec `GET /api/v1/formations` (`?domaine=&tri=&page=&limit=`) et `GET /api/v1/formations/([0-9]+)`, exposes dans `templates/etape_02_catalogue.html`.
3. **`etape_03_crud_et_validation_rfc7807.py`** — *Mutations CRUD & Erreurs RFC 7807 (`application/problem+json`)*
   - Enrichit l'Etape 2 avec `POST`, `PUT`, `PATCH`, `DELETE` et validation stricte renvoyant `422 Unprocessable Entity` conforme RFC 7807 avec banniere interactive dans `templates/etape_03_crud.html`.
4. **`etape_04_persistance_sqlite_wal.py`** — *Persistance Relationnelle SQLite3 WAL Non-Bloquante*
   - Remplace la liste en memoire par `sqlite3` (`PRAGMA journal_mode=WAL`, `foreign_keys=ON`, `busy_timeout=5000`) deporte via `IOLoop.current().run_in_executor(ThreadPoolExecutor, ...)` afin de ne jamais bloquer la boucle d'evenements Tornado (`templates/etape_04_sqlite.html`).
5. **`etape_05_securite_auth_rbac_cookies.py`** — *Securite : Cookies Signes, Bearer HMAC-SHA256, RBAC & Quota 429*
   - Ajoute `set_secure_cookie` (`HttpOnly`, `SameSite=Lax`), les jetons Bearer `HMAC-SHA256` verifies en temps constant (`hmac.compare_digest`), la distinction `401` (`WWW-Authenticate`) vs `403` RBAC (`stagiaire` vs `admin`) et la limitation de debit `429` (`Retry-After`) dans `templates/etape_05_securite.html`.
6. **`etape_06_hero_complet_swagger.py`** — *Application Finale "Hero" & Gouvernance OpenAPI 3.0.3*
   - Couronne l'architecture avec le contrat vivant `/api/openapi.json`, le portail interactif **Swagger UI (`/api/docs`)**, la sonde `/health`, le journal d'audit (`log_function`) et le portail Web complet (`templates/etape_06_hero.html`).

---

## Commandes d'Execution

### Mode interactif (navigateur sur `http://127.0.0.1:8889/`)

```bash
.venv/bin/python tornado-version/zero_to_hero/etape_01_hello_world.py
.venv/bin/python tornado-version/zero_to_hero/etape_02_routes_et_site_catalogue.py
.venv/bin/python tornado-version/zero_to_hero/etape_03_crud_et_validation_rfc7807.py
.venv/bin/python tornado-version/zero_to_hero/etape_04_persistance_sqlite_wal.py
.venv/bin/python tornado-version/zero_to_hero/etape_05_securite_auth_rbac_cookies.py
.venv/bin/python tornado-version/zero_to_hero/etape_06_hero_complet_swagger.py
```

Pour choisir un port personnalise :

```bash
PORT=8890 .venv/bin/python tornado-version/zero_to_hero/etape_06_hero_complet_swagger.py
```

### Mode auto-verification (`--once` avec `AsyncHTTPClient`)

```bash
for s in tornado-version/zero_to_hero/etape_0*.py; do
  .venv/bin/python "$s" --once
done
```
