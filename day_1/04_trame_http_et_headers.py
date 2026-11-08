# Fichier : day_1/04_trame_http_et_headers.py
# Exécution : python day_1/04_trame_http_et_headers.py
# Objectif : Inspecter une trame brute HTTP/1.1 (Request Line, Headers, Body, Status Line)

import json

def construire_requete_http_brute(methode, chemin, hote, headers_extra, corps_dict=None):
    corps_texte = json.dumps(corps_dict, ensure_ascii=False) if corps_dict else ""
    lignes = [
        f"{methode} {chemin} HTTP/1.1",
        f"Host: {hote}",
        "User-Agent: ISGP-PythonClient/1.0",
        "Accept: application/json",
    ]
    for k, v in headers_extra.items():
        lignes.append(f"{k}: {v}")
    if corps_texte:
        lignes.append("Content-Type: application/json; charset=utf-8")
        lignes.append(f"Content-Length: {len(corps_texte.encode('utf-8'))}")
    # En HTTP/1.1, une ligne vide (\r\n\r\n) sépare TOUJOURS les Headers du Body !
    trame = "\r\n".join(lignes) + "\r\n\r\n" + corps_texte
    return trame

trame_post = construire_requete_http_brute(
    methode="POST",
    chemin="/api/v1/formations",
    hote="127.0.0.1:5000",
    headers_extra={"Authorization": "Bearer eyJhbGci...", "X-Request-ID": "req-98412"},
    corps_dict={"titre": "Ingénierie des APIs REST", "duree_jours": 5}
)

print("=== TRAME HTTP/1.1 BRUTE ENVOYÉE SUR LE SOCKET TCP ===")
print(trame_post)
