# Fichier : day_4/03_rate_limiting_429.py
# Exécution : .venv/bin/python day_4/03_rate_limiting_429.py

import time
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuration du Rate Limiter : max 3 requêtes par tranche de 20 secondes par IP
LIMITE_REQUETES = 3
FENETRE_SECONDES = 20
historique_ip = {}  # {"127.0.0.1": [timestamp1, timestamp2, ...]}

@app.route("/api/catalogue-protege", methods=["GET"])
def catalogue_avec_ratelimit():
    ip_client = request.remote_addr or "127.0.0.1"
    maintenant = time.time()

    # 1. Conserver uniquement les appels effectués durant les 20 dernières secondes
    appels_recents = [t for t in historique_ip.get(ip_client, []) if maintenant - t < FENETRE_SECONDES]

    # 2. Vérifier si le plafond est atteint
    if len(appels_recents) >= LIMITE_REQUETES:
        attente = int(FENETRE_SECONDES - (maintenant - appels_recents[0])) + 1
        reponse = jsonify({
            "erreur": "Quota de requêtes dépassé (429 Too Many Requests)",
            "limite": f"{LIMITE_REQUETES} requêtes par {FENETRE_SECONDES} secondes",
            "reessayer_dans_secondes": attente
        })
        reponse.status_code = 429
        reponse.headers["Retry-After"] = str(attente)
        reponse.headers["X-RateLimit-Limit"] = str(LIMITE_REQUETES)
        reponse.headers["X-RateLimit-Remaining"] = "0"
        return reponse

    # 3. Enregistrer l'appel actuel et calculer le quota restant
    appels_recents.append(maintenant)
    historique_ip[ip_client] = appels_recents
    restant = LIMITE_REQUETES - len(appels_recents)

    reponse = jsonify({"message": "Requête acceptée", "quota_restant": restant})
    reponse.headers["X-RateLimit-Limit"] = str(LIMITE_REQUETES)
    reponse.headers["X-RateLimit-Remaining"] = str(restant)
    return reponse, 200

if __name__ == "__main__":
    import sys
    if "--serve" in sys.argv:
        app.run(host="0.0.0.0", port=5001, debug=True)
    else:
        with app.test_client() as client:
            for i in range(1, 5):
                r = client.get("/api/catalogue-protege")
                print(f"Appel #{i} -> HTTP {r.status_code} | X-RateLimit-Remaining={r.headers.get('X-RateLimit-Remaining')} | {r.get_json()}")
