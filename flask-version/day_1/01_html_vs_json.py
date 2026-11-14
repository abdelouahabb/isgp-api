import sys
# Fichier : day_1/01_html_vs_json.py
# Exécution : .venv/bin/python day_1/01_html_vs_json.py
# Objectif : Comparer les 3 formats du Web dans Flask :
#   1. Page Web HTML rendue proprement via un template Jinja2 (day_1/templates/meteo.html)
#   2. Service Web Historique SOAP (XML verbeux)
#   3. API Web Moderne REST (JSON léger via jsonify)

import os
from flask import Flask, Response, jsonify, render_template

# Flask charge automatiquement les fichiers HTML depuis le sous-dossier "templates/"
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))

# Données métier partagées (indépendantes du format de sortie)
DONNEES_METEO = {
    "ville": "Alger",
    "temperature_celsius": 24,
    "condition": "Ensoleillé",
    "humidite_pourcent": 55,
}


# 1. APPROCHE WEB CLASSIQUE (HTML rendu par Jinja2 — Zéro HTML codé en dur dans Python)
@app.route("/meteo/html", methods=["GET"])
def meteo_page_html():
    # render_template() injecte le dictionnaire dans le fichier day_1/templates/meteo.html
    return render_template("meteo.html", meteo=DONNEES_METEO), 200


# 2. APPROCHE HISTORIQUE SOAP / XML (Verbeuse, stricte, utilisée en banque/télécom)
@app.route("/meteo/soap", methods=["GET"])
def meteo_enveloppe_soap():
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
    return Response(flux_xml, status=200, mimetype="application/xml")


# 3. APPROCHE API MODERNE REST / JSON (Légère, découplée, universelle)
@app.route("/api/v1/meteo", methods=["GET"])
def meteo_api_json():
    return jsonify(DONNEES_METEO), 200


# 4. PORTAIL WEB INTERACTIF SUR GET / (Expose et interroge les 3 routes via fetch)
@app.route("/", methods=["GET"])
def portail_comparateur():
    return render_template("index_01_formats.html", meteo=DONNEES_METEO), 200


if __name__ == "__main__":
    # Comparaison automatique des 3 formats grâce au client de test intégré à Flask
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        rep_html = client.get("/meteo/html")
        rep_soap = client.get("/meteo/soap")
        rep_json = client.get("/api/v1/meteo")

        print(f"1. HTML (Template Jinja2) : {len(rep_html.data)} octets | Content-Type: {rep_html.content_type}")
        print(f"2. SOAP (Enveloppe XML)   : {len(rep_soap.data)} octets | Content-Type: {rep_soap.content_type}")
        print(f"3. REST (Payload JSON)    : {len(rep_json.data)} octets | Content-Type: {rep_json.content_type}")
        print("\nPayload REST/JSON prêt pour tout client (Web, Mobile, Python) :")
        print(rep_json.get_json())
    if "--once" not in sys.argv:
        import socket as _sock
        port = int(os.environ.get("PORT", 5001))
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
            if _s.connect_ex(("127.0.0.1", port)) == 0:
                _s2 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                _s2.bind(("127.0.0.1", 0))
                port = _s2.getsockname()[1]
                _s2.close()
        print("\n" + "=" * 76)
        print(f"[SERVEUR WSGI FLASK ACTIF] Serveur en écoute sur http://127.0.0.1:{port}")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print(f"  -> Testez les routes en direct sur http://127.0.0.1:{port} (navigateur, curl, Postman)")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
