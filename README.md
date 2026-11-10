# ISGP — Trilogie Pédagogique : Développement d'APIs et services web (Flask, FastAPI & Tornado)

Plateforme Web Progressive (**PWA**) et manuel d'ingénierie de 5 jours (**Jour 0 à Jour 5**) dédiés à la conception, la sécurisation et la mise en production d'APIs REST en Python selon les trois grands paradigmes de micro-frameworks :

1. **Volume I — Édition Flask & Gunicorn (`WSGI Synchrone`)** : `/cours/flask` (`flask-version/`)
2. **Volume II — Édition FastAPI & Uvicorn (`ASGI Asynchrone & Pydantic v2`)** : `/cours/fastapi` (`fastapi-version/`)
3. **Volume III — Édition Tornado (`IOLoop Non-Bloquant & RequestHandler`)** : `/cours/tornado` (`tornado-version/`)

---

## Démarrage du Portail Unifié

```bash
.venv/bin/python app.py
```

Le serveur écoute par défaut sur `http://0.0.0.0:5000` :
- **Portail de sélection des 3 éditions** : `http://127.0.0.1:5000/`
- **Volume I (Flask)** : `http://127.0.0.1:5000/cours/flask`
- **Volume II (FastAPI)** : `http://127.0.0.1:5000/cours/fastapi`
- **Volume III (Tornado)** : `http://127.0.0.1:5000/cours/tornado`

---

## Structure du Dépôt (Sans Duplication)

```text
isgp-api/
├── app.py                   # Serveur unifié (Portail, Sandbox HTTP, Simulateur Nginx, Exécuteur Python)
├── requirements.txt         # Dépendances unifiées (Flask, FastAPI, Uvicorn, Tornado, HTTPX)
├── static/                  # Ressources statiques partagées (CSS, JS, Mermaid, Service Worker PWA)
├── templates/               # Portail d'accueil (landing.html) et gabarits partagés du bac à sable
├── flask-version/           # Volume I : 30 chapitres, scripts day_0..day_5 et cluster Nginx Flask
├── fastapi-version/         # Volume II : 30 chapitres, scripts day_0..day_5 et cluster Nginx FastAPI
└── tornado-version/         # Volume III : 30 chapitres, scripts day_0..day_5 et cluster Nginx Tornado
```
