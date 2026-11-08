# Fichier : day_5/03_architecture_blueprints.py
# Exécution : .venv/bin/python day_5/03_architecture_blueprints.py
# Objectif : Structurer une API professionnelle avec des Blueprints modulaires,
#            une Application Factory (create_app) et une sonde de santé (/api/health).

import time
from flask import Blueprint, Flask, jsonify

DEMARRAGE_SERVEUR = time.time()

# 1. MODULE MÉTIER 1 : Blueprint dédié au domaine des Formations (/api/v1/formations)
formations_bp = Blueprint("formations", __name__, url_prefix="/api/v1/formations")

@formations_bp.route("", methods=["GET"])
def lister_formations():
    return jsonify({"domaine": "formations", "version": "v1", "items": ["API REST", "Sécurité JWT"]}), 200

# 2. MODULE MÉTIER 2 : Blueprint dédié à la supervision et santé de l'API (/api/health)
sante_bp = Blueprint("sante", __name__, url_prefix="/api/health")

@sante_bp.route("/live", methods=["GET"])
def liveness_probe():
    """Sonde Liveness : indique à l'orchestrateur que le processus Python répond."""
    return jsonify({"statut": "UP", "uptime_secondes": round(time.time() - DEMARRAGE_SERVEUR, 1)}), 200

@sante_bp.route("/ready", methods=["GET"])
def readiness_probe():
    """Sonde Readiness : vérifie que la base de données et les dépendances sont prêtes."""
    db_connectee = True  # Exemple : exécuter 'SELECT 1' sur SQLite/PostgreSQL
    code_http = 200 if db_connectee else 503
    return jsonify({"pret": db_connectee, "dependances": {"sqlite": "OK"}}), code_http

# 3. APPLICATION FACTORY : Assemblage propre de l'application Flask
def create_app():
    application = Flask(__name__)
    application.register_blueprint(formations_bp)
    application.register_blueprint(sante_bp)
    return application

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
