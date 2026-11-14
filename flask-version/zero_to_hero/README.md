# Parcours Progressif Zero-to-Hero — Portail Web & API Catalogue Formations ISGP (Flask & Gunicorn)

Ce dossier propose un **fil rouge cumulatif en 6 étapes** faisant évoluer la **même application métier** (*Portail Web & API du Catalogue des Formations ISGP*), depuis un serveur minimaliste de 45 lignes jusqu'à une architecture modulaire de production dotée de persistance SQLite WAL, d'authentification hybride (Cookies signés + Bearer HMAC), de contrôle d'accès par rôles (RBAC), de limitation de débit (HTTP 429) et d'une documentation interactive **OpenAPI 3.1.0 / Swagger UI**.

Chaque étape respecte deux principes d'ingénierie fondamentaux :
1. **Zéro HTML codé en dur dans Python** : toutes les interfaces Web (`GET /`) sont rendues proprement via des gabarits Jinja2 situés dans `templates/` avec échappement automatique anti-XSS (`{{ ... }}`).
2. **Double exposition Site Web + API REST** : chaque page `GET /` expose et consomme en direct les routes JSON (`/api/...`) du serveur via l'API standard `fetch()` du navigateur.

---

## Progression Pédagogique des 6 Étapes

| Étape | Script Python | Template Jinja2 (`GET /`) | Capacités ajoutées sur le socle cumulatif |
| :--- | :--- | :--- | :--- |
| **Étape 1** | `etape_01_hello_world.py` | `templates/etape_01_hello.html` | Premier serveur WSGI Flask (~45 lignes) : route Web `GET /` et première route JSON `GET /api/bonjour` (`jsonify`) interrogée en direct par un bouton `fetch()`. |
| **Étape 2** | `etape_02_routes_et_site_catalogue.py` | `templates/etape_02_catalogue.html` | Routage RESTful `/api/v1/formations` (filtrage `?domaine=&q=`, tri sécurisé par liste blanche `?tri=` et pagination `?page=&limit=`) + consultation unitaire `/api/v1/formations/<int:formation_id>`. |
| **Étape 3** | `etape_03_crud_et_validation_rfc7807.py` | `templates/etape_03_crud.html` | Cycle CRUD complet (`POST`, `PUT`, `PATCH`, `DELETE`) et validation stricte côté serveur retournant le format normalisé **RFC 7807** (`422 Unprocessable Entity`, `Content-Type: application/problem+json`) avec bannière d'erreur interactive. |
| **Étape 4** | `etape_04_persistance_sqlite_wal.py` | `templates/etape_04_sqlite.html` | Remplacement du stockage en mémoire par **SQLite 3** configuré pour la concurrence (`PRAGMA journal_mode=WAL`, `foreign_keys=ON`, `busy_timeout=5000`), rattaché proprement au cycle de vie WSGI via `flask.g` et `@app.teardown_appcontext`. |
| **Étape 5** | `etape_05_securite_auth_rbac_cookies.py` | `templates/etape_05_securite.html` | Authentification hybride par cookies de session signés (`HttpOnly`, `SameSite=Lax`) et jetons Bearer signés (`itsdangerous` / `hmac.compare_digest`), décorateur RBAC `@functools.wraps` (`401` + `WWW-Authenticate` vs `403` `stagiaire` vs `admin`), et quota par fenêtre glissante (`429 Too Many Requests` + `Retry-After`). |
| **Étape 6** | `etape_06_hero_complet_swagger.py` | `templates/etape_06_hero.html` & `etape_06_swagger_ui.html` | Architecture finale **Blueprints** + **Application Factory `create_app()`**, middlewares d'audit (`X-Request-ID`, `X-Response-Time-Ms`, `X-Content-Type-Options: nosniff`), sonde `/health`, contrat **OpenAPI 3.1.0** (`/api/openapi.json`) et portail **Swagger UI** (`/api/docs`). |

---

## Commandes d'Exécution

### 1. Lancer une étape en mode serveur interactif (Port 5001 par défaut)

Depuis la racine du dépôt :

```bash
.venv/bin/python flask-version/zero_to_hero/etape_01_hello_world.py
.venv/bin/python flask-version/zero_to_hero/etape_02_routes_et_site_catalogue.py
.venv/bin/python flask-version/zero_to_hero/etape_03_crud_et_validation_rfc7807.py
.venv/bin/python flask-version/zero_to_hero/etape_04_persistance_sqlite_wal.py
.venv/bin/python flask-version/zero_to_hero/etape_05_securite_auth_rbac_cookies.py
.venv/bin/python flask-version/zero_to_hero/etape_06_hero_complet_swagger.py
```

Puis ouvrez `http://127.0.0.1:5001` (et `http://127.0.0.1:5001/api/docs` à l'étape 6). Pour choisir un autre port TCP :

```bash
PORT=5050 .venv/bin/python flask-version/zero_to_hero/etape_06_hero_complet_swagger.py
```

### 2. Exécuter l'auto-vérification automatisée (`--once`)

Chaque étape embarque une suite d'assertions `app.test_client()` vérifiant à la fois le rendu HTML (`GET /`) et les contrats JSON (`/api/...`) sans bloquer le terminal :

```bash
for f in flask-version/zero_to_hero/etape_*.py; do .venv/bin/python "$f" --once; done
```

### 3. Déploiement Multi-Workers WSGI avec Gunicorn (Étape 6)

En production, le serveur de développement Werkzeug (`app.run()`) cède la place au serveur d'application pré-forké **Gunicorn** invoquant directement la fabrique `create_app()` :

```bash
cd flask-version
../.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 "zero_to_hero.etape_06_hero_complet_swagger:create_app()"
```

---

## Identifiants de Démonstration (Étapes 5 et 6)

- **Compte Stagiaire (lecture seule, rejeté en `403` sur les écritures)** : `stagiaire` / `isgp-stagiaire-2026`
- **Compte Administrateur (accès complet CRUD)** : `admin` / `isgp-admin-2026`
