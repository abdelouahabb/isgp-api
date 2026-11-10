# ISGP — Trilogie d'Ingénierie : Développement d'APIs et Services Web en Python (Flask, FastAPI & Tornado)

Plateforme Web Progressive (**PWA**) et manuel de référence complet dédié aux fondations architecturales, aux contrats OpenAPI/Swagger, à la sécurité Zero-Trust (**Nord-Sud vs Est-Ouest, OAuth 2.0 / OIDC / RFC 8693**), à la persistance, au streaming temps réel et au déploiement en cluster d'APIs Web en Python selon les trois grands paradigmes industriels :

1. **Volume I — Édition Flask & Gunicorn (`WSGI Synchrone`)** : `/cours/flask` (`flask-version/`)
2. **Volume II — Édition FastAPI & Uvicorn (`ASGI Asynchrone & Pydantic v2`)** : `/cours/fastapi` (`fastapi-version/`)
3. **Volume III — Édition Tornado (`IOLoop Non-Bloquant C10K & RequestHandler`)** : `/cours/tornado` (`tornado-version/`)

- **Portail Interactif en Ligne (GitHub Pages)** : `https://abdelouahabb.github.io/isgp-api/`

---

## Contenu de Chaque Édition (Symétrie Complète sur les 3 Frameworks)

- **Support de Cours Progressif (Jours 0 à 5 — 30 Chapitres)** : Fondations Python, pile réseau TCP/TLS/URI/HTTP, sérialisation JSON, validation, formulaires, authentification (`X-API-Key`, `Bearer HMAC/JWT`, cookies `HttpOnly` / `Secure` / `SameSite`), RBAC, Rate-Limiting (`429`), erreurs normalisées `RFC 7807`, versioning `v1`/`v2` (`RFC 8594` `Deprecation`/`Sunset`) et tests automatisés.
- **Manuel de Référence I — Architecture API, Contrats, Nord-Sud vs Est-Ouest, OAuth 2.0 & Swagger (9 Chapitres + 2 Labos Interactifs)** :
  - **Fondations & Lexique de Précision** : Qu'est-ce qu'une API réellement (frontière de découplage OS Syscalls, PEP 249 In-Process, IPC, REST vs gRPC vs GraphQL vs Webhooks vs WebSockets) et définition rigoureuse des 12 termes clés (Ressource vs Représentation, Endpoint vs Route, Idempotence & `Idempotency-Key`, Statelessness, `400` vs `422`, `406` vs `415`, Pagination Cursor vs Offset, SLI/SLO/SLA).
  - **Contrat d'API vs Documentation d'API** : Spécification exécutable par machine (`OpenAPI 3.1`, `JSON Schema`, `Protobuf`, CI Spectral & Schemathesis) vs portail DX humain généré automatiquement pour éliminer le *Documentation Drift* ; *Contract-First* vs *Code-First*, Loi de Postel et gestion des *Breaking Changes*.
  - **Communications Nord-Sud vs Est-Ouest & Opérations Authentifiées Déléguées** : Topologie verticale externe (WAF, TLS public, API Gateway *Phantom Token*) vs maillage latéral interne (*Fan-Out*, budgets de latence, fin du *Castle-and-Moats* -> **Zero-Trust**), **OAuth 2.0 (`RFC 6749`)** vs **OpenID Connect (`ID Token` vs `Access Token`)**, **PKCE (`RFC 7636`)**, prévention de la faille du *Confused Deputy* via **mTLS (`SPIFFE`) + OAuth 2.0 Token Exchange (`RFC 8693` claim `act`)**, et `client_credentials` M2M.
  - **Qu'est-ce que Swagger ?** : Histoire complète (`2010` création -> `2015` don à la Linux Foundation sous le nom **OpenAPI Initiative**) et distinction exacte entre la norme ouverte **OpenAPI (`OAS 3.1`)** et la suite d'outils logiciels **Swagger** (`Swagger Editor`, `Swagger UI`, `Swagger Codegen`).
- **Manuel de Référence II — Persistance SQLite3, Curseurs & Sécurité SQL (9 Chapitres + Serveur Live)** :
  - Mode `WAL` & Pragmas de production (`foreign_keys = ON`, `busy_timeout`), `find_one` (`fetchone` + tuple `(id,)`), `find_many` (`fetchall`, `fetchmany`, itérateur), `insert` (`lastrowid` & `RETURNING *`), `executemany`, `autocommit` (`PEP 249`), fermeture déterministe via `contextlib.closing(conn.cursor())`.
  - Philosophie comparée des curseurs : **Flask** (`flask.g` + ORM `SQLAlchemy`) vs **FastAPI** (`Depends(get_db)` + `aiosqlite` / `SQLModel AsyncSession`) vs **Tornado** (`IOLoop.run_in_executor` sans *Lazy Loading* bloquant), comparatif `sqlite3` vs **`APSW`**.
- **Manuel de Référence III — Temps Réel, Streaming Multipart, Tâches `202` & Cache `ETag` (9 Chapitres + 4 Labos + Serveur Live)** :
  - **Temps Réel** : Short Polling vs Long-Polling vs **SSE (`text/event-stream`, `Last-Event-ID`, `X-Accel-Buffering: no`)** vs **WebSockets (`RFC 6455`, `HTTP 101`)**.
  - **Téléversement Binaire & Sécurité** : `multipart/form-data` (`RFC 7578`) vs Base64 (`+33 %`), plafond `413`, inspection des *Magic Bytes* réels (`%PDF-`, PNG vs `.exe` `MZ` -> `415`), protection *Path Traversal* et streaming à mémoire constante.
  - **Asynchrone, Observabilité & Cache HTTP** : `HTTP 202 Accepted` + `Location`, `X-Request-ID`, `ETag` / `If-None-Match` (`304 Not Modified`) et concurrence optimiste `If-Match` (`412 Precondition Failed`).
- **Déploiement Cluster Nginx (4 Nœuds) & Délégation Binaire C/Noyau** :
  - Load Balancing (`round_robin`, `least_conn`, `ip_hash`, `weight`), *Zero-Downtime Failover*, bouclier `413` segmenté, `$request_body_file` et téléchargements privés `X-Accel-Redirect` (`internal; sendfile on;`).
- **Laboratoires Interactifs Intégrés** : Client HTTP & Inspecteur serveur, laboratoire `curl` / Postman / Swagger UI (`/api/docs`), Atelier Python en direct, **69 fiches de référentiel** et **62 questions d'évaluation corrigées** (9 modules) par framework.

---

## Installation & Démarrage Rapide (Mode Serveur Python Unifié)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Le portail unifié écoute sur `http://127.0.0.1:5000` :
- **Portail de sélection des 3 éditions** : `http://127.0.0.1:5000/`
- **Volume I (Flask WSGI)** : `http://127.0.0.1:5000/cours/flask`
- **Volume II (FastAPI ASGI)** : `http://127.0.0.1:5000/cours/fastapi`
- **Volume III (Tornado IOLoop)** : `http://127.0.0.1:5000/cours/tornado`
- **Documentation OpenAPI / Swagger UI** : `http://127.0.0.1:5000/api/docs`

### Génération Statique pour GitHub Pages

```bash
.venv/bin/python build_gh_pages.py
```

---

## Structure du Dépôt

```text
isgp-api/
├── app.py                   # Portail unifié, Sandbox HTTP, Simulateurs Architecture / OAuth2 / SQLite / Temps Réel / Nginx
├── build_gh_pages.py        # Générateur de build statique autonome vers dist/ pour GitHub Pages
├── requirements.txt         # Dépendances Python (Flask, FastAPI, Uvicorn, Tornado, HTTPX)
├── static/                  # Styles CSS, logique interactive JS (app.js), shim GitHub Pages, Mermaid, Service Worker PWA
├── templates/               # Portail comparatif de la trilogie (landing.html) et vues partagées
├── flask-version/           # Volume I : 30 leçons, day_0..day_5, 3 manuels de réf., 69 fiches, 62 quiz, deploy_nginx_cluster/
├── fastapi-version/         # Volume II : 30 leçons, day_0..day_5, 3 manuels de réf., 69 fiches, 62 quiz, deploy_nginx_cluster/
└── tornado-version/         # Volume III : 30 leçons, day_0..day_5, 3 manuels de réf., 69 fiches, 62 quiz, deploy_nginx_cluster/
```
