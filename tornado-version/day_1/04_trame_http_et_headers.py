# Fichier : day_1/04_trame_http_et_headers.py
# Exécution : .venv/bin/python day_1/04_trame_http_et_headers.py
# Objectif : Comparer la trame brute HTTP/1.1 d'un appel API JSON (tornado.escape.json_decode(self.request.body))
#            et la trame brute HTTP/1.1 d'un Formulaire Web HTML (self.get_body_argument).

import json
from urllib.parse import urlencode


def construire_trame_http(methode, chemin, hote, content_type, corps_texte, headers_extra=None):
    """Construit la trame texte exacte envoyée sur le socket TCP selon la RFC 9112."""
    lignes = [
        f"{methode} {chemin} HTTP/1.1",
        f"Host: {hote}",
        "User-Agent: ISGP-TornadoInspector/1.0",
    ]
    if headers_extra:
        for k, v in headers_extra.items():
            lignes.append(f"{k}: {v}")
    if corps_texte:
        lignes.append(f"Content-Type: {content_type}")
        lignes.append(f"Content-Length: {len(corps_texte.encode('utf-8'))}")
    # En HTTP/1.1, une ligne vide (\r\n\r\n) sépare TOUJOURS les Headers du Body !
    return "\r\n".join(lignes) + "\r\n\r\n" + corps_texte


# 1. Trame envoyée par un Client API Moderne (JSON -> lu par tornado.escape.json_decode(self.request.body))
donnees_formation = {"titre": "Ingénierie des APIs REST Tornado", "duree_jours": 5, "salle": "Salle A"}
trame_api_json = construire_trame_http(
    methode="POST",
    chemin="/api/v1/formations",
    hote="127.0.0.1:8888",
    content_type="application/json; charset=utf-8",
    corps_texte=json.dumps(donnees_formation, ensure_ascii=False),
    headers_extra={"Accept": "application/json", "Authorization": "Bearer eyJhbGci..."},
)

# 2. Trame envoyée par un Formulaire HTML <form method="POST"> (lu par self.get_body_argument dans Tornado)
trame_formulaire_html = construire_trame_http(
    methode="POST",
    chemin="/sandbox/formulaire-jinja",
    hote="127.0.0.1:8888",
    content_type="application/x-www-form-urlencoded",
    corps_texte=urlencode(donnees_formation),
    headers_extra={"Accept": "text/html"},
)

print("=== 1. TRAME HTTP/1.1 D'UN APPEL API JSON (lu via json_decode(self.request.body)) ===")
print(trame_api_json)
print("\n=== 2. TRAME HTTP/1.1 D'UN FORMULAIRE HTML <form method='POST'> (lu via self.get_body_argument) ===")
print(trame_formulaire_html)
