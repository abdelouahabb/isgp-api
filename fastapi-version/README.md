# ISGP — Volume II : Développement d'APIs et services web (Édition FastAPI & Uvicorn — ASGI & Pydantic v2)

Application Web Progressive (**PWA**) et laboratoire interactif dédié au **Volume II — Édition FastAPI & Uvicorn (ASGI, Pydantic v2, Starlette, APIRouter, Depends, TestClient)** pour le séminaire de formation de 5 jours **« Développement d'APIs et services web »**.

La plateforme est conçue selon une approche **sans prérequis implicite** : chaque notion (variables Python, annotations de types, protocole HTTP, sérialisation JSON, routage FastAPI `@app.get`/`@app.post`, validation déclarative `BaseModel` Pydantic v2, persistance SQLite ACID, injection de dépendances `Depends()` et sécurité par en-têtes/tokens) est décomposée méthodiquement et accompagnée d'environnements d'exécution intégrés.

---

## Démarrage du Serveur

```bash
/home/abdelouahab/isgp-api/.venv/bin/python app.py
```

Le serveur écoute par défaut sur `http://0.0.0.0:8000` :
- **Accès local (poste formateur)** : `http://127.0.0.1:8000`
- **Accès réseau local (postes participants)** : utiliser l'adresse IP locale affichée dans l'en-tête de l'application (`http://<ip-locale>:8000`).

---

## Architecture Fonctionnelle (Volume II — FastAPI & Uvicorn)

1. **Support de Cours Structuré (Jour 0 à Jour 5)** :
   - **Jour 0 — Mise à niveau Python & Type Hints** : Variables, listes `[ ]`, dictionnaires `{ }`, fonctions annotées `def (id: int) -> dict:` et prise en main de **VS Code / Antigravity IDE**.
   - **Jour 1 — Architecture Web, HTTP & JSON** : Modèle Client/Serveur, structure d'une URI, méthodes HTTP (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), codes de statut (`200`, `201`, `400`, `404`, `422`, `500`) et format `JSON`.
   - **Jour 2 — Premiers Services Web avec FastAPI & Uvicorn (ASGI)** : Serveur ASGI Uvicorn, décorateurs `@app.get`/`@app.post`, paramètres de chemin typés `{id}: int`, paramètres Query `Query(...)`, modèles Pydantic `BaseModel`, middlewares `@app.middleware("http")` et formulaires `Form(...)` / `Jinja2Templates`.
   - **Jour 3 — API CRUD Complète, Validation Pydantic & SQLite** : Validation stricte Pydantic v2 (`Field(ge=1, le=30)`, `@field_validator`, `422 Unprocessable Entity`), opérations CRUD SQLite, idempotence (`PUT`, `PATCH`, `Idempotency-Key`), transactions ACID et gestionnaires `@app.exception_handler`.
   - **Jour 4 — Sécurité d'API & Injection `Depends()`** : Secrets `.env`, `Header(alias="X-API-Key")` + `hmac.compare_digest`, jetons Bearer signés (`HTTPBearer`), Rate Limiting `429`, RBAC & Scopes via `Depends(exiger_role("admin"))`, CORS (`CORSMiddleware`), Webhooks HMAC et Cookies `HttpOnly`.
   - **Jour 5 — Architecture Modulaire `APIRouter`, Tests `TestClient` & Production ASGI** : Client Python résilient (`httpx.AsyncClient`), pagination Offset vs Cursor, routeurs modulaires `APIRouter` (`/api/v1` déprécié RFC 8594 vs `/api/v2`), tests automatisés `TestClient(app)`, documentation native OpenAPI 3.1 (`/docs`, `/redoc`) et déploiement Cluster Nginx + 4 instances Uvicorn.

2. **Synchronisation Formateur / Participants en Temps Réel** :
   - Accès via la **Console Formateur** (code d'accès par défaut : `isgp`).
   - Diffusion automatique du chapitre actif, publication de consignes de session et partage de code en direct via Server-Sent Events (SSE).

3. **Client de Test HTTP & Analyse d'Exécution Serveur** :
   - Interface de test permettant d'émettre des requêtes HTTP réelles vers les routes de démonstration (`/api/sandbox/...`) et d'inspecter simultanément la requête `curl`, le gestionnaire FastAPI exécuté côté serveur et la réponse JSON.

4. **Atelier d'Exécution Python & Ressources Téléchargeables** :
   - Exécuteur Python côté serveur intégré aux chapitres (exécutant tous les scripts `day_0/` à `day_5/` avec `TestClient(app)`) et téléchargement direct des fichiers sources `.py`.
