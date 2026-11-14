# Fichier : day_5/04_tests_et_production.py
# Exécution : .venv/bin/python day_5/04_tests_et_production.py
# Objectif : Tester automatiquement ses RequestHandlers Tornado (API JSON et Formulaire HTML)
#            avec tornado.testing.AsyncHTTPTestCase et comprendre le déploiement multi-processus HTTPServer.

import asyncio
import json
import os
import sys
import unittest
import urllib.parse
import tornado.escape
import tornado.httpserver
import tornado.netutil
import tornado.testing
import tornado.web

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))


# 1. HANDLER API JSON (reçoit application/json via tornado.escape.json_decode)
class CalculTaxeApiHandler(tornado.web.RequestHandler):
    def post(self):
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        montant_ht = corps.get("montant_ht")
        if not isinstance(montant_ht, (int, float)) or montant_ht < 0:
            self.set_status(422)
            self.write({"erreur": "Le champ 'montant_ht' doit être un nombre positif"})
            return
        tva = round(montant_ht * 0.19, 2)
        self.write({"montant_ht": montant_ht, "tva_19": tva, "montant_ttc": round(montant_ht + tva, 2)})


# 2. HANDLER FORMULAIRE HTML + TORNADO TEMPLATE (reçoit application/x-www-form-urlencoded via self.get_body_argument)
class CalculTaxeFormulaireHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("resultat_taxe.html", resultat=None)

    def post(self):
        resultat = None
        try:
            montant_ht = float(self.get_body_argument("montant_ht", "-1"))
        except ValueError:
            montant_ht = -1
        if montant_ht >= 0:
            tva = round(montant_ht * 0.19, 2)
            resultat = {"montant_ht": montant_ht, "tva_19": tva, "montant_ttc": round(montant_ht + tva, 2)}
        self.render("resultat_taxe.html", resultat=resultat)


class PortailTestsProdHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("portail_d5_04.html")


def make_app():
    return tornado.web.Application(
        [
            (r"/", PortailTestsProdHandler),
            (r"/api/calcul-taxe", CalculTaxeApiHandler),
            (r"/formulaire-taxe", CalculTaxeFormulaireHandler),
        ],
        template_path=os.path.join(DOSSIER_COURANT, "templates"),
    )


# ================= SUITE DE TESTS OFFICIELLE TORNADO (AsyncHTTPTestCase) =================
class TestCalculateurFiscalTornado(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app()

    def test_1_post_json_nominal(self):
        rep = self.fetch(
            "/api/calcul-taxe",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"montant_ht": 1000}),
        )
        self.assertEqual(rep.code, 200)
        self.assertEqual(tornado.escape.json_decode(rep.body)["montant_ttc"], 1190.0)
        print("[TEST 1 RÉUSSI] POST JSON /api/calcul-taxe (1000 HT -> 1190 TTC) : HTTP 200")

    def test_2_post_json_invalide_422(self):
        rep = self.fetch(
            "/api/calcul-taxe",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"montant_ht": -50}),
        )
        self.assertEqual(rep.code, 422)
        print("[TEST 2 RÉUSSI] Rejet d'un montant négatif : HTTP 422 Unprocessable Entity")

    def test_3_post_formulaire_html_template(self):
        rep = self.fetch(
            "/formulaire-taxe",
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=urllib.parse.urlencode({"montant_ht": "2000"}),
        )
        self.assertEqual(rep.code, 200)
        html_rendu = rep.body.decode("utf-8")
        self.assertIn("2380.0 DZD", html_rendu)
        print("[TEST 3 RÉUSSI] POST Formulaire HTML /formulaire-taxe (self.get_body_argument + self.render) : 2380.0 DZD")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCalculateurFiscalTornado)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    if "--once" not in sys.argv:
        async def _serve():
            bind_port = int(os.environ.get("PORT", 8889))
            try:
                sockets = tornado.netutil.bind_sockets(bind_port, "127.0.0.1")
            except OSError:
                sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
            port = sockets[0].getsockname()[1]
            server = tornado.httpserver.HTTPServer(make_app(), xheaders=True)
            server.add_sockets(sockets)
            print(f"\n[BOUCLE IOLOOP TORNADO ACTIVE] Portail Calculateur Fiscal sur http://127.0.0.1:{port}/")
            await asyncio.Event().wait()
        try:
            asyncio.run(_serve())
        except KeyboardInterrupt:
            print("\n[IOLOOP TORNADO] Arrêt propre demandé par l'utilisateur (Ctrl+C).")
