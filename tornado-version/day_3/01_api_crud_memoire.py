import os
# Fichier : day_3/01_api_crud_memoire.py
# Exécution : .venv/bin/python day_3/01_api_crud_memoire.py
# Objectif : Validation stricte des champs entrants dans un RequestHandler Tornado
#            et réponses d'erreur normalisées RFC 7807 (self.set_status(422))

import asyncio
import json
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

formations = [
    {"id": 1, "titre": "Architecture des APIs REST Tornado", "duree_jours": 5, "salle": "Salle A"},
    {"id": 2, "titre": "Python Asynchrone pour l'Entreprise", "duree_jours": 3, "salle": "Salle B"},
]


def valider_payload_formation(corps):
    """Vérifie le schéma, les types et les bornes métier du JSON reçu."""
    erreurs = {}
    if not isinstance(corps, dict):
        return {"_corps": "Un objet JSON valide est requis."}

    titre = str(corps.get("titre", "")).strip()
    if len(titre) < 3 or len(titre) > 120:
        erreurs["titre"] = "Le titre est obligatoire et doit contenir entre 3 et 120 caractères."

    try:
        duree = int(corps.get("duree_jours", 5))
        if duree < 1 or duree > 30:
            erreurs["duree_jours"] = "La durée doit être comprise entre 1 et 30 jours."
    except (ValueError, TypeError):
        erreurs["duree_jours"] = "La durée doit être un nombre entier."

    return erreurs


class FormationsCollectionHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"total": len(formations), "donnees": formations})

    def post(self):
        try:
            corps = tornado.escape.json_decode(self.request.body or b"{}")
        except ValueError:
            corps = None

        erreurs = valider_payload_formation(corps)
        if erreurs:
            # Format d'erreur structuré selon le standard RFC 7807 (Problem Details)
            self.set_status(422)
            self.set_header("Content-Type", "application/problem+json; charset=UTF-8")
            self.write({
                "type": "https://isgp.dz/erreurs/validation-echouee",
                "title": "Données d'entrée invalides",
                "status": 422,
                "champs_en_erreur": erreurs,
            })
            return

        nouvel_id = max([f["id"] for f in formations], default=0) + 1
        nouvelle = {
            "id": nouvel_id,
            "titre": str(corps["titre"]).strip(),
            "duree_jours": int(corps.get("duree_jours", 5)),
            "salle": str(corps.get("salle", "Salle Principale")).strip(),
        }
        formations.append(nouvelle)
        self.set_status(201)
        self.write({"message": "Formation créée", "formation": nouvelle})


def make_app():
    return tornado.web.Application([(r"/api/v1/formations", FormationsCollectionHandler)])


async def _demo():
    app = make_app()
    app.settings["log_function"] = lambda h: print(
        f"[IOLOOP TORNADO] HTTP {h.get_status()} | {h.request.method} {h.request.uri} ({h.request.remote_ip}) | {round(1000.0 * h.request.request_time(), 2)} ms"
    )
    bind_port = int(os.environ.get("PORT", 8889))
    try:
        sockets = tornado.netutil.bind_sockets(bind_port, "127.0.0.1")
    except OSError:
        sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    print("=== 1. TEST POST INVALIDE -> ERREUR RFC 7807 (422 Unprocessable Entity) ===")
    r_err = await client.fetch(
        f"http://127.0.0.1:{port}/api/v1/formations",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"titre": "AB", "duree_jours": -5}),
        raise_error=False,
    )
    print("Statut :", r_err.code, "| Payload :", tornado.escape.json_decode(r_err.body))

    print("\n=== 2. TEST POST VALIDE -> 201 Created ===")
    r_ok = await client.fetch(
        f"http://127.0.0.1:{port}/api/v1/formations",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"titre": "Sécurité des Services Web Tornado", "duree_jours": 4, "salle": "Labo 2"}),
    )
    print("Statut :", r_ok.code, "| Payload :", tornado.escape.json_decode(r_ok.body))
    if "--once" in sys.argv:
        server.stop()
    else:
        print("\n" + "=" * 76)
        print(f"[BOUCLE IOLOOP TORNADO ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print("  -> La boucle d'événements IOLoop reste ouverte en mode interactif !")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print(f"  -> Testez les routes en direct : http://127.0.0.1:{port} (navigateur, curl, Postman)")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement la boucle IOLoop.")
        print("=" * 76)
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(_demo())
    except KeyboardInterrupt:
        print("\n[IOLOOP TORNADO] Arrêt propre demandé par l'utilisateur (Ctrl+C).")
