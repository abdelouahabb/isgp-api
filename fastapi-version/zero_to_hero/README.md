# Parcours Progressif Zero-to-Hero — FastAPI, Pydantic v2 & Uvicorn

Ce répertoire regroupe les **6 étapes cumulatives** du fil conducteur pédagogique du **Volume II (FastAPI, Pydantic v2, Starlette & Uvicorn)**. Chaque étape fait évoluer **la même application métier** (*Portail Web & API Catalogue des Formations ISGP*) en couplant systématiquement :

1. **Une API REST JSON typée** (`/api/...`) validée par Pydantic v2 et auto-documentée par OpenAPI 3.1.
2. **Un véritable Site Web HTML interactif** servi sur `GET /` via `Jinja2Templates` (`zero_to_hero/templates/*.html`, zéro chaîne HTML codée en dur dans les routes Python), qui consomme en direct les endpoints REST via `fetch()`.

---

## Progression des 6 Étapes

| Étape | Script Python | Template Jinja2 (`GET /`) | Briques Architecturales Ajoutées |
| :--- | :--- | :--- | :--- |
| **01** | `etape_01_hello_world.py` | `templates/etape_01_hello.html` | Serveur ASGI minimal, `GET /` HTML (`Jinja2Templates`), `GET /api/bonjour` typé et Swagger UI `/docs`. |
| **02** | `etape_02_routes_et_site_catalogue.py` | `templates/etape_02_catalogue.html` | Filtrage `Query(...)` (`?domaine=&recherche=&tri=`), pagination (`meta` / `data`), validation `Path(..., ge=1)` et gestion `404`. |
| **03** | `etape_03_crud_et_validation_rfc7807.py` | `templates/etape_03_crud.html` | Modèles Pydantic v2 (`BaseModel`, `Field`, `ConfigDict(extra="forbid")`), `POST`, `PUT`, `PATCH` (`exclude_unset=True`), `DELETE` et erreurs normalisées **RFC 7807** (`422 application/problem+json`). |
| **04** | `etape_04_persistance_sqlite_wal.py` | `templates/etape_04_sqlite.html` | Persistance transactionnelle `sqlite3` (`PRAGMA journal_mode=WAL`, `foreign_keys=ON`, `busy_timeout=5000`, `check_same_thread=False`) injectée par générateur `Depends(get_db)` (`yield` / `finally`) sur routes synchrones `def` exécutées dans le threadpool ASGI. |
| **05** | `etape_05_securite_auth_rbac_cookies.py` | `templates/etape_05_securite.html` | Cookies de session signés HMAC (`HttpOnly=True`, `SameSite="lax"`), jetons `HTTPBearer` HMAC-SHA256 (`hmac.compare_digest`), contrôle d'accès par rôle `Depends(exiger_role("admin"))` (`401` + `WWW-Authenticate` vs `403`) et limitation de débit à fenêtre glissante (`429` + `Retry-After`). |
| **06** | `etape_06_hero_complet_swagger.py` | `templates/etape_06_hero.html` | **Application Hero finale** : découpage modulaire `APIRouter`, cycle de vie `lifespan`, sonde `/health`, middleware `X-Process-Time-Ms`, contrat **OpenAPI 3.1.0** (`/openapi.json`), **Swagger UI** (`/docs` et `/api/docs`) et **ReDoc** (`/redoc`). |

---

## Commandes d'Exécution

### 1. Démarrage interactif d'une étape (Serveur ASGI sur `http://127.0.0.1:8001`)

```bash
/home/abdelouahab/isgp-api/.venv/bin/python fastapi-version/zero_to_hero/etape_01_hello_world.py
/home/abdelouahab/isgp-api/.venv/bin/python fastapi-version/zero_to_hero/etape_06_hero_complet_swagger.py
```

Pour choisir un port personnalisé :

```bash
PORT=8010 /home/abdelouahab/isgp-api/.venv/bin/python fastapi-version/zero_to_hero/etape_06_hero_complet_swagger.py
```

### 2. Démarrage direct via la CLI `uvicorn` (rechargement à chaud en développement)

```bash
/home/abdelouahab/isgp-api/.venv/bin/uvicorn etape_06_hero_complet_swagger:app \
  --app-dir fastapi-version/zero_to_hero \
  --host 127.0.0.1 \
  --port 8001 \
  --reload
```

### 3. Auto-vérification automatisée sans bloquer le terminal (`--once`)

Chaque étape embarque un banc d'essai asynchrone basé sur `httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")` qui valide à la fois le portail HTML (`GET /`) et les contrats JSON (`/api/...`) :

```bash
for f in fastapi-version/zero_to_hero/etape_*.py; do
  /home/abdelouahab/isgp-api/.venv/bin/python "$f" --once
done
```
