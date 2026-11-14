# Zero to Hero Tornado — Etape 1/6 : Hello World (Site Web HTML + API JSON)
# Execution : .venv/bin/python tornado-version/zero_to_hero/etape_01_hello_world.py

import asyncio
import os
import sys
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.netutil
import tornado.web

DOSSIER = os.path.dirname(os.path.abspath(__file__))


class AccueilHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("etape_01_hello.html", titre_page="Portail Formations ISGP — Etape 1", organisme="ISGP")


class BonjourApiHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"etape": 1, "service": "Portail & API Catalogue ISGP", "moteur": "Tornado IOLoop", "statut": "operationnel"})


def make_app():
    return tornado.web.Application(
        [(r"/", AccueilHandler), (r"/api/bonjour", BonjourApiHandler)],
        template_path=os.path.join(DOSSIER, "templates"),
    )


async def main():
    port_cible = int(os.environ.get("PORT", 8889))
    try:
        sockets = tornado.netutil.bind_sockets(port_cible, "127.0.0.1")
    except OSError:
        sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(make_app())
    server.add_sockets(sockets)

    client = tornado.httpclient.AsyncHTTPClient()
    r_html = await client.fetch(f"http://127.0.0.1:{port}/")
    r_json = await client.fetch(f"http://127.0.0.1:{port}/api/bonjour")
    assert r_html.code == 200 and "text/html" in r_html.headers["Content-Type"]
    assert r_json.code == 200 and tornado.escape.json_decode(r_json.body)["etape"] == 1
    print(f"[ETAPE 1 OK] Site Web : http://127.0.0.1:{port}/ | API JSON : http://127.0.0.1:{port}/api/bonjour")
    if "--once" in sys.argv:
        server.stop()
        return
    print("Serveur Tornado actif (Ctrl+C pour arreter).")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
