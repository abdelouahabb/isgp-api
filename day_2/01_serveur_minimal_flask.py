# Fichier : day_2/01_serveur_minimal_flask.py
# Exécution : .venv/bin/python day_2/01_serveur_minimal_flask.py
# Test : http://127.0.0.1:5001/api/bonjour

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/bonjour", methods=["GET"])
def dire_bonjour():
    return jsonify({
        "message": "Service Flask opérationnel",
        "organisme": "ISGP",
        "statut": "actif"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
