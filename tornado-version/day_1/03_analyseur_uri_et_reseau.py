# Fichier : day_1/03_analyseur_uri_et_reseau.py
# Exécution : .venv/bin/python day_1/03_analyseur_uri_et_reseau.py
# Objectif : Décoder une URI complète (RFC 3986) et ses paramètres de requête en Python / Tornado

from urllib.parse import urlparse, parse_qs
from tornado.httputil import url_concat

# Construction propre d'une URL avec paramètres via tornado.httputil.url_concat
uri_base = "https://api.isgp.dz:8443/api/v1/formations"
uri_complete = url_concat(uri_base, {"ville": "Alger", "domaine": "securite", "page": 2}) + "#resultats"

analyse = urlparse(uri_complete)
parametres = parse_qs(analyse.query)

print("=== 1. DÉCOUPAGE NORMALISÉ D'UNE URI (RFC 3986) ===")
print("URI Complète       :", uri_complete)
print("Protocole (Scheme) :", analyse.scheme)      # https
print("Hôte (Hostname)    :", analyse.hostname)    # api.isgp.dz
print("Port TCP           :", analyse.port)        # 8443
print("Chemin (Path)      :", analyse.path)        # /api/v1/formations
print("Requête (Query)    :", analyse.query)       # ville=Alger&domaine=securite&page=2
print("Fragment (Anchor)  :", analyse.fragment)    # resultats

print("\n=== 2. DICTIONNAIRE DES PARAMÈTRES DE REQUÊTE (lu par self.get_query_argument) ===")
for cle, valeurs in parametres.items():
    print(f"- {cle} : {valeurs[0]}")
