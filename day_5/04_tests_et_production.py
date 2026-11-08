# Fichier : day_5/04_tests_et_production.py
# Exécution : .venv/bin/python day_5/04_tests_et_production.py
# Objectif : Tester automatiquement ses routes API sans démarrer de serveur réseau
#            grâce à app.test_client() et comprendre le déploiement WSGI (Gunicorn).

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api/calcul-taxe", methods=["POST"])
def calculer_taxe():
    corps = request.get_json(silent=True) or {}
    montant_ht = corps.get("montant_ht")
    if not isinstance(montant_ht, (int, float)) or montant_ht < 0:
        return jsonify({"erreur": "Le champ 'montant_ht' doit être un nombre positif"}), 422
    tva = round(montant_ht * 0.19, 2)
    return jsonify({"montant_ht": montant_ht, "tva_19": tva, "montant_ttc": round(montant_ht + tva, 2)}), 200

# ================= SUITE DE TESTS AUTOMATISÉS D'API =================
def executer_tests_automatises():
    # test_client() simule des requêtes HTTP en mémoire (ultra-rapide, sans ouvrir de port TCP)
    client = app.test_client()

    # Test 1 : Cas nominal (200 OK)
    rep_ok = client.post("/api/calcul-taxe", json={"montant_ht": 1000})
    assert rep_ok.status_code == 200, f"Attendu 200, reçu {rep_ok.status_code}"
    donnees = rep_ok.get_json()
    assert donnees["montant_ttc"] == 1190.0, "Calcul TTC incorrect"
    print("[TEST 1 RÉUSSI] POST /api/calcul-taxe (1000 HT -> 1190 TTC) : HTTP 200")

    # Test 2 : Cas d'erreur de validation (422 Unprocessable Entity)
    rep_err = client.post("/api/calcul-taxe", json={"montant_ht": -50})
    assert rep_err.status_code == 422, f"Attendu 422, reçu {rep_err.status_code}"
    print("[TEST 2 RÉUSSI] Rejet d'un montant négatif : HTTP 422 Unprocessable Entity")

if __name__ == "__main__":
    executer_tests_automatises()
    # EN PRODUCTION : Ne jamais utiliser app.run() !
    # Commande de déploiement WSGI : gunicorn -w 4 -b 0.0.0.0:8000 day_5.04_tests_et_production:app
