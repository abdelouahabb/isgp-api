import os
# Fichier : day_3/03_put_patch_et_idempotence.py
# Exécution : .venv/bin/python day_3/03_put_patch_et_idempotence.py
# Objectif : Différencier def put(self, id) (remplacement complet) de def patch(self, id) (modification partielle)
#            dans Tornado et sécuriser POST contre les doublons avec l'en-tête Idempotency-Key.

import asyncio
import json
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web

formations = {
    1: {"id": 1, "titre": "Architecture des APIs REST Tornado", "duree_jours": 5, "salle": "Salle A"}
}
# Cache des clés d'idempotence déjà traitées : {"cle-unique-client": reponse_memorisee}
cles_idempotence = {}


# 1. POST SÉCURISÉ PAR IDEMPOTENCY-KEY (Évite les créations en doublon si le réseau coupe)
class FormationsIdempotentHandler(tornado.web.RequestHandler):
    def post(self):
        cle_idem = self.request.headers.get("Idempotency-Key", "").strip()
        if cle_idem and cle_idem in cles_idempotence:
            # La requête a déjà été traitée : on renvoie exactement le résultat initial sans recréer !
            precedente = cles_idempotence[cle_idem]
            self.write({"rejoue_sans_doublon": True, "formation": precedente})
            return

        corps = tornado.escape.json_decode(self.request.body or b"{}")
        if "titre" not in corps:
            self.set_status(400)
            self.write({"erreur": "Le champ 'titre' est requis"})
            return

        nouvel_id = max(formations.keys(), default=0) + 1
        nouvelle = {
            "id": nouvel_id,
            "titre": corps["titre"],
            "duree_jours": int(corps.get("duree_jours", 5)),
            "salle": corps.get("salle", "Salle A"),
        }
        formations[nouvel_id] = nouvelle
        if cle_idem:
            cles_idempotence[cle_idem] = nouvelle
        self.set_status(201)
        self.write({"rejoue_sans_doublon": False, "formation": nouvelle})


# 2. PUT (Remplacement intégral) vs PATCH (Modification partielle) dans le même RequestHandler Tornado
class FormationItemHandler(tornado.web.RequestHandler):
    def put(self, id_str):
        fid = int(id_str)
        if fid not in formations:
            self.set_status(404)
            self.write({"erreur": "Introuvable"})
            return
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        if not all(k in corps for k in ("titre", "duree_jours", "salle")):
            self.set_status(400)
            self.write({"erreur": "PUT exige tous les champs : titre, duree_jours, salle"})
            return

        formations[fid] = {
            "id": fid,
            "titre": corps["titre"],
            "duree_jours": int(corps["duree_jours"]),
            "salle": corps["salle"],
        }
        self.write({"methode": "PUT (remplacement complet)", "formation": formations[fid]})

    def patch(self, id_str):
        fid = int(id_str)
        if fid not in formations:
            self.set_status(404)
            self.write({"erreur": "Introuvable"})
            return
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        actuelle = formations[fid]
        for champ in ("titre", "duree_jours", "salle"):
            if champ in corps:
                actuelle[champ] = corps[champ]
        self.write({"methode": "PATCH (mise à jour partielle)", "formation": actuelle})


class PortailIdempotenceHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("portail_d3_03.html")


def make_app():
    dossier = os.path.dirname(os.path.abspath(__file__))
    return tornado.web.Application(
        [
            (r"/", PortailIdempotenceHandler),
            (r"/api/v1/formations", FormationsIdempotentHandler),
            (r"/api/v1/formations/([0-9]+)", FormationItemHandler),
        ],
        template_path=os.path.join(dossier, "templates"),
    )


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

    print("=== 1. TEST POST AVEC IDEMPOTENCY-KEY (2 ENVOIS IDENTIQUES) ===")
    for essai in (1, 2):
        r = await client.fetch(
            f"http://127.0.0.1:{port}/api/v1/formations",
            method="POST",
            headers={"Content-Type": "application/json", "Idempotency-Key": "idem-2026-001"},
            body=json.dumps({"titre": "Sécurité Tornado"}),
        )
        print(f"  Envoi #{essai} (HTTP {r.code}) ->", tornado.escape.json_decode(r.body))

    print("\n=== 2. TEST PATCH PARTIEL SUR LA FORMATION #1 ===")
    r_patch = await client.fetch(
        f"http://127.0.0.1:{port}/api/v1/formations/1",
        method="PATCH",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"salle": "Amphi ISGP"}),
    )
    print("  PATCH (HTTP", r_patch.code, ") ->", tornado.escape.json_decode(r_patch.body))
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
