# ISGP — Volume I : Ingénierie des APIs REST & Services Web avec Python, Flask & Gunicorn

Plateforme pédagogique et référentiel d'exécution pour le séminaire **« Développement d'APIs et services web »** (Institut Supérieur de Gestion et de Planification — **ISGP**), dédiés à l'écosystème **Python, Flask (WSGI), Jinja2, SQLite WAL et Gunicorn**.

L'ouvrage combine un traité conceptuel approfondi, un **parcours cumulatif en 6 étapes (`zero_to_hero/`)** faisant évoluer la même application du premier *Hello World* jusqu'à la mise en production, ainsi que **30 laboratoires thématiques (`day_0/` à `day_5/`)** exposant simultanément des interfaces Web HTML Jinja2 (`GET /`) et des contrats d'API RESTful JSON (`/api/...`).

---

## Démarrage Rapide

Depuis la racine du dépôt (`/home/abdelouahab/isgp-api`) :

```bash
# 1. Lancer la plateforme pédagogique interactive principale (Port 5000)
.venv/bin/python app.py

# 2. Lancer n'importe quel laboratoire autonome (Port 5001 par défaut)
.venv/bin/python flask-version/zero_to_hero/etape_06_hero_complet_swagger.py

# 3. Exécuter les auto-tests intégrés d'un script sans bloquer le terminal (--once)
.venv/bin/python flask-version/day_3/02_api_crud_sqlite.py --once
```

En production sous **Gunicorn** (serveur WSGI multi-workers) :

```bash
cd flask-version
../.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 "zero_to_hero.etape_06_hero_complet_swagger:create_app()"
```

---

## Architecture Pédagogique du Volume I (`flask-version/`)

### 1. Chapitre 0 — Traité Fondamental avant Python (`data/chapter_0_literature.py`)
Avant la première ligne de code Python, le **Chapitre 0** pose les fondations architecturales durables :
- **Histoire intellectuelle et découplage** : de la crise des monolithes à la dissimulation de l'information (*Information Hiding*, Parnas 1972) et aux quatre familles d'APIs.
- **Grand Traité du Vocabulaire** : URI (RFC 3986), méthodes HTTP et idempotence (RFC 9110), négociation MIME, enveloppes de pagination et erreurs normalisées RFC 7807.
- **Contrats vs Documentation** : distinction rigoureuse entre spécification **OpenAPI 3.0 / 3.1** et suite logicielle **Swagger** (*Swagger UI*, *Editor*, *Codegen*), approches *Contract-First* et *Code-First*, cycle de dépréciation RFC 8594 (`Deprecation`, `Sunset`, `410 Gone`).
- **Topologies Réseau & Sécurité** : flux **Nord-Sud** (API Gateway, WAF, Rate-Limiting) face aux flux **Est-Ouest** (mTLS, Zero-Trust, SPIFFE), rôles et flux **OAuth 2.0 / PKCE / OIDC** et échange de jetons RFC 8693.

---

### 2. Parcours Cumulatif en 6 Étapes (`zero_to_hero/`)
Ce fil rouge pédagogique construit pas à pas le **Portail Web & API du Catalogue des Formations ISGP** sur une base de code évolutive unique, où chaque gabarit Jinja2 (`GET /`) consomme en direct l'API JSON via `fetch()` :

1. **`etape_01_hello_world.py`** : Serveur minimaliste (~45 lignes) — page Jinja2 `GET /` interrogeant `GET /api/bonjour` (`jsonify`).
2. **`etape_02_routes_et_site_catalogue.py`** : Routage RESTful `/api/v1/formations`, filtrage multi-critères (`?domaine=&q=`), tri sécurisé (`?tri=`), pagination et consultation unitaire `<int:formation_id>`.
3. **`etape_03_crud_et_validation_rfc7807.py`** : Opérations `POST`, `PUT`, `PATCH`, `DELETE` et validation stricte retournant `422` au format normalisé **RFC 7807** (`application/problem+json`).
4. **`etape_04_persistance_sqlite_wal.py`** : Persistance relationnelle **SQLite 3** (`PRAGMA journal_mode=WAL`, `foreign_keys=ON`, `busy_timeout=5000`) gérée dans `flask.g` et `@app.teardown_appcontext`.
5. **`etape_05_securite_auth_rbac_cookies.py`** : Authentification hybride par cookies signés (`HttpOnly`, `SameSite=Lax`) et jetons Bearer HMAC (`hmac.compare_digest`), décorateur RBAC (`401` + `WWW-Authenticate` vs `403`) et limitation de débit `429` (`Retry-After`).
6. **`etape_06_hero_complet_swagger.py`** : Architecture finale en **Blueprints** + **Application Factory `create_app()`**, middlewares d'audit (`X-Request-ID`, `X-Response-Time-Ms`), sonde `/health`, contrat **OpenAPI 3.1.0** (`/api/openapi.json`) et portail **Swagger UI** (`/api/docs`).

Consultez [zero_to_hero/README.md](zero_to_hero/README.md) pour le détail des commandes et des identifiants de test.

---

### 3. Laboratoires Thématiques Journaliers (`day_0/` à `day_5/`)
Chaque module journalier regroupe ses scripts `.py`, ses templates HTML Jinja2 dédiés (`templates/`) et ses métadonnées pédagogiques synchronisées (`lesson_data.py`) :

- **`day_0/` — Mise à niveau Python pour les APIs (4 scripts)** : Types scalaires compatibles JSON (`01`), listes et dictionnaires imbriqués (`02`), fonctions pures (`03`), gestion d'exceptions et décorateurs `@wraps` (`04`).
- **`day_1/` — Protocoles Web, URI, Trames HTTP/1.1 & JSON (5 scripts)** : Comparateur live HTML Jinja2 vs SOAP/XML vs REST/JSON (`01`), sérialisation UTF-8 ISO 8601 (`02`), décodage d'URI RFC 3986 (`03`), radiographie d'une trame HTTP/1.1 brute (`04`) et maîtrise de `curl` (`05`).
- **`day_2/` — Fondamentaux Flask, Routage, Pagination, Middlewares & Jinja2 (5 scripts)** : Serveur minimal hybride (`01`), paramètres `<int:id>` et `request.args` (`02`), filtrage/tri/pagination (`03`), middlewares `@before_request`/`@after_request` et `X-Request-ID` (`04`), formulaires HTML `request.form` et téléversement `request.files` sécurisé (`05`).
- **`day_3/` — Ingénierie CRUD, Validation RFC 7807, Idempotence & SQLite (4 scripts)** : Validation stricte en mémoire (`01`), CRUD relationnel SQLite paramétré `?` anti-injection SQL (`02`), `PUT` vs `PATCH` et déduplication `POST` par `Idempotency-Key` (`03`), gestionnaires d'erreurs JSON globaux `@app.errorhandler` (`04`).
- **`day_4/` — Sécurité Industrielle des APIs & Sessions Web (7 scripts)** : Secrets d'environnement et `X-API-Key` en temps constant (`01`), jetons Bearer signés `itsdangerous` (`02`), Rate Limiting `429` par fenêtre glissante (`03`), Refresh Token et RBAC `401` vs `403` (`04`), CORS strict et signature Webhook HMAC-SHA256 (`05`), distinction AuthN / AuthZ / Scopes OAuth2 / Anti-BOLA (`06`), cookies `HttpOnly`, `SameSite` et sessions signées (`07`).
- **`day_5/` — Clients Résilients, Blueprints, Tests Automatisés & OpenAPI (5 scripts)** : Client Python authentifié avec gestion d'erreurs (`01`), pagination de production Offset vs Curseur Keyset (`02`), architecture modulaire Blueprints et coexistence `v1`/`v2` RFC 8594 (`03`), suite de tests automatisés `app.test_client()` (`04`), contrat OpenAPI 3.0.3 et portail Swagger UI `/api/docs` (`05`).

---

### 4. Référentiel Technique & Déploiement Cluster
- **`data/glossary.py`** : 69 monographies de référence couvrant OpenSSL, l'administration réseau Linux (`ss`, `dig`, `nc`, `jq`), HTTP/MIME, SQLite WAL, la sécurité OAuth2/mTLS et Gunicorn/Nginx.
- **`deploy_nginx_cluster/`** : Configuration prête à l'emploi d'un cluster multi-instances Flask/Gunicorn derrière un répartiteur de charge Nginx.
