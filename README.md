# ISGP — Trilogie d'Ingénierie : Développement d'APIs et Services Web en Python (Flask, FastAPI & Tornado)

Plateforme Web Progressive (**PWA** installable, mode hors-ligne intégral, plein écran paysage, mode nuit/clair, recherche plein texte et export PDF) et **monographie de référence technique (102 chapitres — plus de 855 000 caractères de littérature d'ingénierie)** dédiée aux fondations architecturales, aux contrats OpenAPI/Swagger, à la sécurité Zero-Trust (**Nord-Sud vs Est-Ouest, OAuth 2.0 / OIDC / RFC 8693**), à la persistance, au streaming temps réel, à la création de sites Web exposant des APIs et au déploiement en cluster selon les trois grands paradigmes industriels Python :

1. **Volume I — Édition Flask & Gunicorn (`WSGI Synchrone — PEP 3333`)** : `/cours/flask` (`flask-version/`)
2. **Volume II — Édition FastAPI & Uvicorn (`ASGI 3.0 Asynchrone & Pydantic v2`)** : `/cours/fastapi` (`fastapi-version/`)
3. **Volume III — Édition Tornado (`IOLoop Non-Bloquant C10K & RequestHandler`)** : `/cours/tornado` (`tornado-version/`)

- **Portail Interactif en Ligne (GitHub Pages)** : `https://abdelouahabb.github.io/isgp-api/`

---

## Stratégie Pédagogique « Zero to Hero » : Bâtir l'API ET le Site Web qui l'Expose

Dans chaque volume (`flask-version/zero_to_hero/`, `fastapi-version/zero_to_hero/`, `tornado-version/zero_to_hero/`), un **fil rouge progressif en 6 étapes cumulatives** fait grandir la **même application** (*Portail Web & API Catalogue Formations ISGP*) depuis un simple *Hello World* jusqu'à une architecture complète de production, en exposant à chaque étape à la fois les **endpoints REST JSON** et le **site Web HTML (`GET /`)** qui les consomme :

1. **`etape_01_hello_world.py`** : Serveur minimaliste exposant la page d'accueil HTML (`GET /`) et le premier endpoint JSON (`GET /api/bonjour`).
2. **`etape_02_routes_et_site_catalogue.py`** : Paramètres de chemin et de requête, filtrage, tri et site catalogue interactif consommant `/api/v1/formations`.
3. **`etape_03_crud_et_validation_rfc7807.py`** : Cycle complet `GET / POST / PUT / PATCH / DELETE`, validation stricte et erreurs normalisées `RFC 7807 / 9457` (`422`), pilotés depuis l'interface Web.
4. **`etape_04_persistance_sqlite_wal.py`** : Persistance transactionnelle `SQLite3` en mode `WAL` (`foreign_keys=ON`, `busy_timeout=5000`) adaptée au modèle d'exécution de chaque framework (`flask.g`, `Depends(get_db)`, `IOLoop.run_in_executor`).
5. **`etape_05_securite_auth_rbac_cookies.py`** : Authentification par cookies signés `HttpOnly` / `SameSite`, jetons `Bearer` signés `HMAC-SHA256` (`hmac.compare_digest`), séparation `401` vs `403` RBAC et limitation de débit `429` (`Retry-After`).
6. **`etape_06_hero_complet_swagger.py`** : Application finale industrialisée combinant portail Web complet (`GET /`), contrat **OpenAPI (`3.0.3` / `3.1.0`)** sur `/api/openapi.json`, console interactive **Swagger UI** sur `/api/docs`, sonde `/health` et journalisation d'audit.

Chaque script s'exécute aussi bien en mode serveur interactif qu'en auto-test automatisé (`--once`).

---

## Contenu Complet de Chaque Volume (Symétrie Totale sur les 3 Frameworks)

- **Chapitre 0 — Traité Fondamental & Grand Vocabulaire des APIs (Avant Python — 4 Chapitres de Littérature)** :
  - **0.1 — Qu'est-ce qu'une API ?** : *Information Hiding* de David Parnas (1972), Mandat API de Jeff Bezos (2002), thèse REST de Roy Fielding (2000), les 4 strates d'interfaces (Syscalls OS, PEP 249 In-Process, IPC local, APIs réseau) et comparaison de REST, gRPC, GraphQL, Webhooks et SSE/WebSockets.
  - **0.2 — Le Grand Traité du Vocabulaire** : Ressource vs Représentation, URI vs Endpoint vs Route, Headers vs Payload, Sérialisation, `400` vs `422`, Content Negotiation (`406`/`415`), Statelessness, Idempotence & `Idempotency-Key`, Pagination `Offset` vs `Keyset Cursor`, Webhooks, SDK, Reverse Proxy, Rate-Limiting & Backpressure (`429`), Latence `p99` et `SLI / SLO / SLA`.
  - **0.3 — Contrats d'API, Documentation Vivante & Histoire de Swagger face à OpenAPI** : Contrat formel exécutable vs documentation humaine (*Documentation Drift*), *Contract-First* vs *Code-First*, Loi de Postel (`RFC 761`), cycle de dépréciation `RFC 8594` (`Deprecation` / `Sunset`), et histoire exacte de Tony Tam (`2010`) jusqu'à l'**OpenAPI Initiative (`2015`, Linux Foundation)**.
  - **0.4 — Géopolitique du Réseau : Flux Nord-Sud vs Est-Ouest, Zero-Trust & Délégation OAuth 2.0** : Topologie verticale Nord-Sud vs éventail latéral Est-Ouest (*Fan-Out*), fin du *Castle-and-Moats* vers **Zero-Trust (`NIST SP 800-207`)**, **OAuth 2.0 (`RFC 6749` + `PKCE RFC 7636`)** vs **OpenID Connect (`ID Token` vs `Access Token`)**, faille du *Confused Deputy* (Norm Hardy, 1988) et **mTLS + Token Exchange (`RFC 8693` claim `act`)**.
- **Monographie & Code Source Progressif (Jours 0 à 5 — 30 Chapitres exécutables exposant API + Site Web HTML)** : Fondations Python, pile TCP/TLS/URI/HTTP, sérialisation JSON, templates Web & formulaires, CRUD SQLite ACID, sécurité multicouche (`X-API-Key`, `Bearer`, cookies `HttpOnly`, RBAC, `429`, CORS, Webhooks signés), résilience sortante, versioning `v1`/`v2`, pagination par curseur B-Tree `O(1)` et OpenAPI/Swagger UI.
- **Trois Manuels Opérationnels Transversaux + Laboratoires Live** :
  1. **Architecture API, Nord-Sud / Est-Ouest, OAuth 2.0 / RFC 8693 & Swagger** (9 chapitres + 2 simulateurs).
  2. **Persistance SQLite3 WAL, Curseurs PEP 249 & Prévention SQLi** (9 chapitres + serveur SQLite live).
  3. **Temps Réel (SSE / WebSockets), Upload Multipart Magic Bytes, Jobs `202` & Cache `ETag` (`304` / `412`)** (9 chapitres + 4 laboratoires).
- **Cluster Nginx 4 Nœuds, Référentiel & Évaluation** : Simulateur Load Balancer (`round_robin`, `least_conn`, `ip_hash`, `$request_body_file`, `X-Accel-Redirect`), **69 fiches de référentiel** en prose éditoriale et **62 questions corrigées** par framework.

---

## Installation & Démarrage Rapide

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Le portail unifié écoute sur `http://127.0.0.1:5000` :
- **Portail de sélection des 3 volumes** : `http://127.0.0.1:5000/`
- **Volume I (Flask WSGI)** : `http://127.0.0.1:5000/cours/flask`
- **Volume II (FastAPI ASGI)** : `http://127.0.0.1:5000/cours/fastapi`
- **Volume III (Tornado IOLoop)** : `http://127.0.0.1:5000/cours/tornado`
- **Console OpenAPI / Swagger UI** : `http://127.0.0.1:5000/api/docs`

### Génération Statique Autonome pour GitHub Pages

```bash
.venv/bin/python build_gh_pages.py
```

---

## Structure du Dépôt

```text
isgp-api/
├── app.py                   # Serveur unifié, Sandbox HTTP, Atelier Python Live, ZIP Zero-to-Hero & Simulateurs
├── build_gh_pages.py        # Compilateur statique autonome vers dist/ pour GitHub Pages
├── requirements.txt         # Dépendances Python (Flask, FastAPI, Uvicorn, Tornado, HTTPX)
├── static/                  # Typographie éditoriale + impression PDF (styles.css), moteur JS (app.js), shim GitHub Pages, PWA (sw.js)
├── templates/               # Portail comparatif de la trilogie (landing.html) et vues partagées
├── flask-version/           # Volume I : Chap. 0 + Jours 0..5 (34 chap.), zero_to_hero/ (6 étapes), 69 fiches, 62 quiz
├── fastapi-version/         # Volume II : Chap. 0 + Jours 0..5 (34 chap.), zero_to_hero/ (6 étapes), 69 fiches, 62 quiz
└── tornado-version/         # Volume III : Chap. 0 + Jours 0..5 (34 chap.), zero_to_hero/ (6 étapes), 69 fiches, 62 quiz
```
