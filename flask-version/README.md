# ISGP — Plateforme Pédagogique : Développement d'APIs et services web

Application Web Progressive (**PWA**) développée avec **Python & Flask** pour le séminaire de formation de 5 jours **« Développement d'APIs et services web »**.

La plateforme est conçue selon une approche **sans prérequis implicite** : chaque notion (variables Python, structures de données, protocole HTTP, sérialisation JSON, routage Flask, opérations CRUD, persistance SQLite et authentification par en-têtes) est décomposée méthodiquement et accompagnée d'environnements d'exécution intégrés.

---

## Démarrage du Serveur

```bash
.venv/bin/python app.py
```

Le serveur écoute par défaut sur `http://0.0.0.0:5000` :
- **Accès local (poste formateur)** : `http://127.0.0.1:5000`
- **Accès réseau local (postes participants)** : utiliser l'adresse IP locale affichée dans l'en-tête de l'application (`http://<ip-locale>:5000`).

---

## Architecture Fonctionnelle

1. **Support de Cours Structuré (Jour 0 à Jour 5)** :
   - **Jour 0 — Mise à niveau** : Variables, listes `[ ]`, dictionnaires `{ }`, fonctions `def`/`return` et prise en main de **VS Code / Antigravity IDE**.
   - **Jour 1 — Architecture Web, HTTP & JSON** : Modèle Client/Serveur, structure d'une URL, méthodes HTTP (`GET`, `POST`, `PUT`, `DELETE`), codes de statut (`200`, `201`, `400`, `404`, `500`) et format `JSON`.
   - **Jour 2 — Premiers Services Web avec Flask** : Cycle de vie d'une application Flask, décorateur `@app.route`, fonction `jsonify()`, paramètres de chemin (`<id>`) et paramètres de requête (`request.args`).
   - **Jour 3 — API CRUD Complète** : Lecture du corps de requête via `request.get_json()`, validation des entrées, implémentation des opérations de lecture, création, modification et suppression.
   - **Jour 4 — Persistance SQLite & Sécurité** : Stockage relationnel embarqué avec `sqlite3` et contrôle d'accès par clé d'API (`X-API-Key`) dans les en-têtes HTTP.
   - **Jour 5 — Intégration Cliente & Synthèse** : Consommation d'API depuis un client Python (`urllib`) ou Web (`fetch`), et mise en perspective avec **FastAPI**.

2. **Synchronisation Formateur / Participants en Temps Réel** :
   - Accès via le bouton **Console Formateur** (code d'accès par défaut : `isgp`).
   - Diffusion automatique du chapitre actif, publication de consignes de session et partage de code en direct via Server-Sent Events (SSE).
   - Remontée d'état des participants (*Notion acquise*, *Exercice validé (IDE)*, *Demande d'assistance*).

3. **Client de Test HTTP & Analyse d'Exécution Serveur** :
   - Interface de test permettant d'émettre des requêtes HTTP réelles vers les routes de démonstration (`/api/sandbox/...`) et d'inspecter simultanément la requête `curl`, le gestionnaire Python exécuté côté serveur et la réponse JSON.

4. **Atelier d'Exécution Python & Ressources Téléchargeables** :
   - Exécuteur Python côté serveur intégré aux chapitres et téléchargement direct des fichiers sources `.py` pour exécution locale dans **VS Code** ou **Antigravity IDE**.
