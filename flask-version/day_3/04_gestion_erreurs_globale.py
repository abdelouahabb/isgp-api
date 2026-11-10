import os
# Fichier : day_3/04_gestion_erreurs_globale.py
# Exécution : .venv/bin/python day_3/04_gestion_erreurs_globale.py
# Objectif : Intercepter globalement les erreurs 400, 404, 405 et 500 pour ne JAMAIS
#            renvoyer une page HTML d'erreur par défaut à un client d'API JSON.

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

# 1. INTERCEPTEUR 404 : Route inexistante
@app.errorhandler(404)
def erreur_404_json(erreur):
    return jsonify({
        "erreur": "Ressource ou route introuvable (404 Not Found)",
        "chemin_demande": request.path,
        "methode": request.method
    }), 404

# 2. INTERCEPTEUR 405 : Méthode HTTP non autorisée sur cette route (ex: DELETE sur /bonjour)
@app.errorhandler(405)
def erreur_405_json(erreur):
    return jsonify({
        "erreur": f"La méthode {request.method} n'est pas autorisée sur la route {request.path} (405 Method Not Allowed)"
    }), 405

# 3. INTERCEPTEUR GLOBAL D'EXCEPTIONS : Garantit du JSON même en cas de crash imprévu (500)
@app.errorhandler(Exception)
def erreur_interne_json(erreur):
    if isinstance(erreur, HTTPException):
        return jsonify({"erreur": erreur.description, "code": erreur.code}), erreur.code
    # En production, on journalise l'exception complète côté serveur sans exposer le code interne au client
    print(f"[ERREUR CRITIQUE SERVEUR] {type(erreur).__name__}: {erreur}")
    return jsonify({
        "erreur": "Erreur interne du serveur (500 Internal Server Error)",
        "conseil": "Veuillez communiquer l'horodatage à l'administrateur."
    }), 500

@app.route("/api/v1/division", methods=["GET"])
def calculer_division():
    a = float(request.args.get("a", 100))
    b = float(request.args.get("b", 0))  # Si b=0 -> ZeroDivisionError intercepté proprement en JSON !
    return jsonify({"resultat": a / b}), 200

if __name__ == "__main__":
    with app.test_client() as client:
        r_404 = client.get("/api/v1/route-inconnue")
        print("1. Erreur 404 en JSON :", r_404.status_code, r_404.get_json())
        r_405 = client.delete("/api/v1/division")
        print("2. Erreur 405 en JSON :", r_405.status_code, r_405.get_json())
        r_500 = client.get("/api/v1/division?a=100&b=0")
        print("3. Exception 500 interceptée en JSON :", r_500.status_code, r_500.get_json())
    if os.environ.get("ISGP_WEB_RUNNER") != "1" and "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        print("\n" + "=" * 76)
        print(f"[SERVEUR WSGI FLASK ACTIF] Serveur en écoute sur http://127.0.0.1:{port}")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print(f"  -> Testez les routes en direct sur http://127.0.0.1:{port} (navigateur, curl, Postman)")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
