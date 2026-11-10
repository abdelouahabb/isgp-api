import sys
# Fichier : day_1/01_html_vs_json.py
# Exécution : .venv/bin/python day_1/01_html_vs_json.py
# Objectif : Comparer les 3 formats du Web dans Tornado (tornado.web.RequestHandler) :
#   1. Page Web HTML rendue via le moteur tornado.template (self.render -> day_1/templates/meteo.html)
#   2. Service Web Historique SOAP (XML verbeux avec self.set_header)
#   3. API Web Moderne REST (JSON léger sérialisé automatiquement par self.write(dict))

import asyncio
import os
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.netutil
import tornado.web

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))

# Données métier partagées (indépendantes du format de sortie)
DONNEES_METEO = {
    "ville": "Alger",
    "temperature_celsius": 24,
    "condition": "Ensoleillé",
    "humidite_pourcent": 55,
}


# 1. APPROCHE WEB CLASSIQUE (HTML rendu par tornado.template — Zéro HTML codé en dur dans Python)
class MeteoHtmlHandler(tornado.web.RequestHandler):
    def get(self):
        # self.render() compile et injecte le dictionnaire dans day_1/templates/meteo.html
        self.render("meteo.html", meteo=DONNEES_METEO)


# 2. APPROCHE HISTORIQUE SOAP / XML (Verbeuse, stricte, utilisée en banque/télécom)
class MeteoSoapHandler(tornado.web.RequestHandler):
    def get(self):
        flux_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetMeteoResponse xmlns="http://isgp.dz/ws/meteo">
      <Ville>{DONNEES_METEO['ville']}</Ville>
      <TemperatureCelsius>{DONNEES_METEO['temperature_celsius']}</TemperatureCelsius>
      <Condition>{DONNEES_METEO['condition']}</Condition>
      <HumiditePourcent>{DONNEES_METEO['humidite_pourcent']}</HumiditePourcent>
    </GetMeteoResponse>
  </soap:Body>
</soap:Envelope>"""
        self.set_header("Content-Type", "application/xml; charset=UTF-8")
        self.write(flux_xml)


# 3. APPROCHE API MODERNE REST / JSON (self.write(dict) sérialise automatiquement en JSON !)
class MeteoJsonHandler(tornado.web.RequestHandler):
    def get(self):
        # Dans Tornado, passer un dict Python à self.write() applique automatiquement :
        # - json.dumps(DONNEES_METEO)
        # - Content-Type: application/json; charset=UTF-8
        self.write(DONNEES_METEO)


def make_app():
    return tornado.web.Application(
        [
            (r"/meteo/html", MeteoHtmlHandler),
            (r"/meteo/soap", MeteoSoapHandler),
            (r"/api/v1/meteo", MeteoJsonHandler),
        ],
        template_path=os.path.join(DOSSIER_COURANT, "templates"),
    )


async def comparer_trois_formats():
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
    rep_html = await client.fetch(f"http://127.0.0.1:{port}/meteo/html")
    rep_soap = await client.fetch(f"http://127.0.0.1:{port}/meteo/soap")
    rep_json = await client.fetch(f"http://127.0.0.1:{port}/api/v1/meteo")

    print(f"1. HTML (tornado.template) : {len(rep_html.body)} octets | Content-Type: {rep_html.headers['Content-Type']}")
    print(f"2. SOAP (Enveloppe XML)    : {len(rep_soap.body)} octets | Content-Type: {rep_soap.headers['Content-Type']}")
    print(f"3. REST (self.write dict)  : {len(rep_json.body)} octets | Content-Type: {rep_json.headers['Content-Type']}")
    print("\nPayload REST/JSON décodé via tornado.escape.json_decode :")
    print(tornado.escape.json_decode(rep_json.body))
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
        asyncio.run(comparer_trois_formats())
    except KeyboardInterrupt:
        print("\n[IOLOOP TORNADO] Arrêt propre demandé par l'utilisateur (Ctrl+C).")
