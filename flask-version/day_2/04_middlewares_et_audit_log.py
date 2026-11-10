import os
# Fichier : day_2/04_middlewares_et_audit_log.py
# Exécution : .venv/bin/python day_2/04_middlewares_et_audit_log.py

import time
import uuid
from flask import Flask, g, jsonify, request

app = Flask(__name__)

# 1. MIDDLEWARE AVANT REQUÊTE : S'exécute automatiquement AVANT chaque route
@app.before_request
def initialiser_contexte_requete():
    g.heure_debut = time.perf_counter()
    # Récupère l'ID de corrélation envoyé par le client ou en génère un nouveau
    g.request_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:8]}"

# 2. MIDDLEWARE APRÈS REQUÊTE : S'exécute automatiquement APRÈS chaque route
@app.after_request
def enrichir_et_journaliser_reponse(reponse):
    duree_ms = round((time.perf_counter() - getattr(g, "heure_debut", time.perf_counter())) * 1000, 2)
    request_id = getattr(g, "request_id", "inconnu")

    # Injection d'en-têtes de traçabilité et de sécurité sur TOUTES les réponses
    reponse.headers["X-Request-ID"] = request_id
    reponse.headers["X-Response-Time-Ms"] = str(duree_ms)
    reponse.headers["X-Content-Type-Options"] = "nosniff"

    print(f"[AUDIT] {request.method} {request.path} -> HTTP {reponse.status_code} ({duree_ms} ms) [ID: {request_id}]")
    return reponse

@app.route("/api/v1/statut", methods=["GET"])
def verifier_statut():
    return jsonify({
        "service": "ISGP API Core",
        "request_id": g.request_id,
        "statut": "opérationnel"
    }), 200

if __name__ == "__main__":
    with app.test_client() as client:
        rep = client.get("/api/v1/statut", headers={"X-Request-ID": "req-demo-isgp"})
        print("En-têtes injectés :", dict(rep.headers))
        print("Corps JSON :", rep.get_json())
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
