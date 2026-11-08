# Fichier : day_1/01_html_vs_json.py
# Exécution : python day_1/01_html_vs_json.py
# Objectif : Comparer les 3 formats historiques du Web (HTML, SOAP/XML, REST/JSON)

# 1. Page Web Classique (HTML) : Couplée à l'affichage visuel humain
reponse_html = """
<html>
  <body>
    <div class="carte-meteo">
      <h1>Ville : Alger</h1>
      <p>Température : 24 °C (Ensoleillé)</p>
    </div>
  </body>
</html>
"""

# 2. Service Web Historique SOAP (XML) : Verbeux, strict, utilisé en banque/télécom
enveloppe_soap_xml = """
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetMeteoResponse xmlns="http://isgp.dz/ws/meteo">
      <Ville>Alger</Ville>
      <TemperatureCelsius>24</TemperatureCelsius>
      <Condition>Ensoleillé</Condition>
    </GetMeteoResponse>
  </soap:Body>
</soap:Envelope>
"""

# 3. API Web Moderne REST (JSON) : Léger, lisible, universellement supporté
reponse_rest_json = {
    "ville": "Alger",
    "temperature_celsius": 24,
    "condition": "Ensoleillé",
    "humidite_pourcent": 55
}

print(f"Taille HTML     : {len(reponse_html.strip())} octets")
print(f"Taille SOAP/XML : {len(enveloppe_soap_xml.strip())} octets")
print(f"Taille REST/JSON: {len(str(reponse_rest_json))} octets")
print("\nDonnées REST/JSON prêtes pour tout client :", reponse_rest_json)
