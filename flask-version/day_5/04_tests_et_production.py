# Fichier : day_5/04_tests_et_production.py
# Exécution : .venv/bin/python day_5/04_tests_et_production.py
# Objectif : Tester automatiquement ses routes (API JSON et Formulaire HTML Jinja2)
#            sans ouvrir de port réseau grâce à app.test_client().

import os
from flask import Flask, jsonify, render_template, request

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))


# 1. ROUTE API JSON (reçoit application/json via request.get_json)
@app.route("/api/calcul-taxe", methods=["POST"])
def calculer_taxe_api():
    corps = request.get_json(silent=True) or {}
    montant_ht = corps.get("montant_ht")
    if not isinstance(montant_ht, (int, float)) or montant_ht < 0:
        return jsonify({"erreur": "Le champ 'montant_ht' doit être un nombre positif"}), 422
    tva = round(montant_ht * 0.19, 2)
    return jsonify({"montant_ht": montant_ht, "tva_19": tva, "montant_ttc": round(montant_ht + tva, 2)}), 200


# 2. ROUTE FORMULAIRE HTML + JINJA2 (reçoit application/x-www-form-urlencoded via request.form)
@app.route("/formulaire-taxe", methods=["GET", "POST"])
def calculer_taxe_formulaire():
    resultat = None
    if request.method == "POST":
        montant_ht = request.form.get("montant_ht", type=float)
        if montant_ht is not None and montant_ht >= 0:
            tva = round(montant_ht * 0.19, 2)
            resultat = {"montant_ht": montant_ht, "tva_19": tva, "montant_ttc": round(montant_ht + tva, 2)}
    return render_template("resultat_taxe.html", resultat=resultat), 200


# ================= SUITE DE TESTS AUTOMATISÉS (JSON + FORMULAIRE JINJA2) =================
def executer_tests_automatises():
    client = app.test_client()

    # Test 1 : Appel API JSON nominal (json={...} -> Content-Type: application/json)
    rep_ok = client.post("/api/calcul-taxe", json={"montant_ht": 1000})
    assert rep_ok.status_code == 200
    assert rep_ok.get_json()["montant_ttc"] == 1190.0
    print("[TEST 1 RÉUSSI] POST JSON /api/calcul-taxe (1000 HT -> 1190 TTC) : HTTP 200")

    # Test 2 : Appel API JSON invalide (422 Unprocessable Entity)
    rep_err = client.post("/api/calcul-taxe", json={"montant_ht": -50})
    assert rep_err.status_code == 422
    print("[TEST 2 RÉUSSI] Rejet d'un montant négatif : HTTP 422 Unprocessable Entity")

    # Test 3 : Soumission d'un Formulaire HTML (data={...} -> request.form + rendu Jinja2)
    rep_form = client.post("/formulaire-taxe", data={"montant_ht": "2000"})
    assert rep_form.status_code == 200
    html_rendu = rep_form.get_data(as_text=True)
    assert "2380.0 DZD" in html_rendu
    print("[TEST 3 RÉUSSI] POST Formulaire HTML /formulaire-taxe (request.form + Jinja2) : 2380.0 DZD")


if __name__ == "__main__":
    executer_tests_automatises()
    # EN PRODUCTION : Ne jamais utiliser app.run() !
    # Commande de déploiement WSGI : gunicorn -w 4 -b 0.0.0.0:8000 day_5.04_tests_et_production:app
