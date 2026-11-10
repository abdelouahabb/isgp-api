# ISGP — Trilogie d'Ingénierie : Développement d'APIs et Services Web en Python (Flask, FastAPI & Tornado)

Plateforme Web Progressive (**PWA**) et manuel de référence complet dédié à la conception, la persistance, la sécurisation, le streaming temps réel et le déploiement en cluster d'APIs Web en Python selon les trois grands paradigmes industriels :

1. **Volume I — Édition Flask & Gunicorn (`WSGI Synchrone`)** : `/cours/flask` (`flask-version/`)
2. **Volume II — Édition FastAPI & Uvicorn (`ASGI Asynchrone & Pydantic v2`)** : `/cours/fastapi` (`fastapi-version/`)
3. **Volume III — Édition Tornado (`IOLoop Non-Bloquant C10K & RequestHandler`)** : `/cours/tornado` (`tornado-version/`)

---

## Contenu de Chaque Édition (Symétrie Complète sur les 3 Frameworks)

- **Support de Cours Progressif (Jours 0 à 5 — 30 Chapitres)** : Fondations Python, pile réseau TCP/TLS/URI/HTTP, sérialisation JSON, validation, formulaires, authentification (`X-API-Key`, `Bearer HMAC/JWT`, cookies `HttpOnly` / `Secure` / `SameSite`), RBAC, Rate-Limiting (`429`), erreurs normalisées `RFC 7807`, versioning `v1`/`v2` (`RFC 8594` `Deprecation`/`Sunset`) et tests automatisés.
- **Manuel de Référence I — Persistance SQLite3, Curseurs & Sécurité SQL (9 Chapitres + Serveur Live)** :
  - Mode `WAL` & Pragmas de production (`foreign_keys = ON`, `busy_timeout`), `find_one` (`fetchone` + tuple `(id,)`), `find_many` (`fetchall`, `fetchmany`, itérateur), `insert` (`lastrowid` & `RETURNING *`), `executemany`, `autocommit` (`PEP 249`), fermeture déterministe via `contextlib.closing(conn.cursor())`.
  - Philosophie comparée des curseurs : **Flask** (`flask.g` + ORM `SQLAlchemy`) vs **FastAPI** (`Depends(get_db)` + `aiosqlite` / `SQLModel AsyncSession`) vs **Tornado** (`IOLoop.run_in_executor` sans *Lazy Loading* bloquant).
  - Comparatif architectural `sqlite3` standard vs **`APSW`** (*Another Python SQLite Wrapper*) et portabilité `PEP 249` (`?` vs `%s`).
- **Manuel de Référence II — Temps Réel, Streaming Multipart, Tâches `202` & Cache `ETag` (9 Chapitres + 4 Labos + Serveur Live)** :
  - **Temps Réel** : Short Polling vs Long-Polling vs **SSE (`text/event-stream`, `Last-Event-ID`, `X-Accel-Buffering: no`)** vs **WebSockets (`RFC 6455`, `HTTP 101`)**.
  - **Téléversement Binaire & Sécurité** : `multipart/form-data` (`RFC 7578`) vs inflation `+33 %` du Base64-dans-JSON, plafond `413`, inspection des *Magic Bytes* réels (`%PDF-`, PNG vs `.exe` `MZ` -> `415`), protection *Path Traversal* (`UUID4` + `secure_filename`) et streaming à mémoire constante (`FileStorage.stream` / `UploadFile` / `@tornado.web.stream_request_body`).
  - **Asynchrone & Observabilité** : Découplage `HTTP 202 Accepted` + `Location`, corrélation de bout en bout `X-Request-ID` et chronométrage monotone `time.perf_counter()` (`X-Process-Time-Ms`).
  - **Cache HTTP & Concurrence Optimiste** : `Cache-Control`, validation `ETag` / `If-None-Match` (`304 Not Modified`, 0 octet transféré) et prévention du *Lost Update* via `If-Match` (`412 Precondition Failed`).
- **Déploiement Cluster Nginx (4 Nœuds) & Délégation Binaire C/Noyau** :
  - Load Balancing (`round_robin`, `least_conn`, `ip_hash`, `weight`) et tolérance aux pannes (*Zero-Downtime Failover*).
  - Délégation des uploads lents à Nginx (`client_max_body_size` segmenté, `client_body_in_file_only clean`, `X-Uploaded-File-Path $request_body_file`) et téléchargements privés authentifiés via `X-Accel-Redirect` (`internal; sendfile on;`).
- **Laboratoires Interactifs Intégrés** : Client HTTP & Inspecteur serveur, laboratoire `curl` / Postman / Swagger UI (`/api/docs`), Atelier d'exécution Python en direct dans le navigateur, **57 fiches de référentiel** (incluant OpenSSL & Linux) et **53 questions d'évaluation corrigées** par framework.

---

## Installation & Démarrage Rapide

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

---

## Structure du Dépôt

```text
isgp-api/
├── app.py                   # Portail unifié, Sandbox HTTP, Simulateurs SQLite / Temps Réel / Nginx & Exécuteur Python
├── requirements.txt         # Dépendances Python (Flask, FastAPI, Uvicorn, Tornado, HTTPX)
├── static/                  # Styles CSS, logique interactive JS (app.js), Mermaid, Service Worker PWA (sw.js)
├── templates/               # Portail comparatif de la trilogie (landing.html) et vues partagées
├── flask-version/           # Volume I : 30 leçons, day_0..day_5, sqlite_api_lab.py, advanced_realtime_cache_lab.py, deploy_nginx_cluster/
├── fastapi-version/         # Volume II : 30 leçons, day_0..day_5, sqlite_api_lab.py, advanced_realtime_cache_lab.py, deploy_nginx_cluster/
└── tornado-version/         # Volume III : 30 leçons, day_0..day_5, sqlite_api_lab.py, advanced_realtime_cache_lab.py, deploy_nginx_cluster/
```
