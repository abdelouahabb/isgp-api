# Fichier : day_1/01_html_vs_json.py
# Exécution : python day_1/01_html_vs_json.py

# 1. Réponse d'un serveur Web classique (HTML destiné à l'affichage visuel)
reponse_site_html = """
<html>
  <body>
    <h1>Bulletin Météo Alger : 24°C</h1>
  </body>
</html>
"""

# 2. Réponse d'une API REST (JSON structuré exploitable par tout logiciel)
reponse_api_json = {
    "ville": "Alger",
    "temperature_celsius": 24,
    "condition": "Ensoleillé",
    "humidite_pourcent": 55
}

print("--- 1. HTML (Couche de présentation) ---")
print(reponse_site_html.strip())

print("\n--- 2. Données d'API (Structure pure) ---")
print(reponse_api_json)
