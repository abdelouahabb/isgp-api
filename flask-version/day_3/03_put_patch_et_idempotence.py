import os
# Fichier : day_3/03_put_patch_et_idempotence.py
# Exécution : .venv/bin/python day_3/03_put_patch_et_idempotence.py
# Objectif : Différencier PUT (remplacement complet) de PATCH (modification partielle)
#            et sécuriser POST contre les doublons avec l'en-tête Idempotency-Key.

from flask import Flask, jsonify, request

app = Flask(__name__)

formations = {
    1: {"id": 1, "titre": "Architecture des APIs REST", "duree_jours": 5, "salle": "Salle A"}
}
# Cache des clés d'idempotence déjà traitées : {"cle-unique-client": reponse_memorisee}
cles_idempotence = {}

# 1. POST SÉCURISÉ PAR IDEMPOTENCY-KEY (Évite les créations en doublon si le réseau coupe)
@app.route("/api/v1/formations", methods=["POST"])
def creer_avec_idempotence():
    cle_idem = request.headers.get("Idempotency-Key", "").strip()
    if cle_idem and cle_idem in cles_idempotence:
        # La requête a déjà été traitée : on renvoie exactement le résultat initial sans recréer !
        precedente = cles_idempotence[cle_idem]
        return jsonify({"rejoue_sans_doublon": True, "formation": precedente}), 200

    corps = request.get_json(silent=True) or {}
    if "titre" not in corps:
        return jsonify({"erreur": "Le champ 'titre' est requis"}), 400

    nouvel_id = max(formations.keys(), default=0) + 1
    nouvelle = {
        "id": nouvel_id,
        "titre": corps["titre"],
        "duree_jours": int(corps.get("duree_jours", 5)),
        "salle": corps.get("salle", "Salle A")
    }
    formations[nouvel_id] = nouvelle
    if cle_idem:
        cles_idempotence[cle_idem] = nouvelle
    return jsonify({"rejoue_sans_doublon": False, "formation": nouvelle}), 201


# 2. PUT : REMPLACEMENT INTÉGRAL (Tous les champs doivent être fournis)
@app.route("/api/v1/formations/<int:id>", methods=["PUT"])
def remplacer_formation_put(id):
    if id not in formations:
        return jsonify({"erreur": "Introuvable"}), 404
    corps = request.get_json(silent=True) or {}
    if not all(k in corps for k in ("titre", "duree_jours", "salle")):
        return jsonify({"erreur": "PUT exige tous les champs : titre, duree_jours, salle"}), 400

    formations[id] = {
        "id": id,
        "titre": corps["titre"],
        "duree_jours": int(corps["duree_jours"]),
        "salle": corps["salle"]
    }
    return jsonify({"methode": "PUT (remplacement complet)", "formation": formations[id]}), 200


# 3. PATCH : MODIFICATION PARTIELLE (Seuls les champs envoyés sont modifiés)
@app.route("/api/v1/formations/<int:id>", methods=["PATCH"])
def modifier_partiellement_patch(id):
    if id not in formations:
        return jsonify({"erreur": "Introuvable"}), 404
    corps = request.get_json(silent=True) or {}
    actuelle = formations[id]
    for champ in ("titre", "duree_jours", "salle"):
        if champ in corps:
            actuelle[champ] = corps[champ]
    return jsonify({"methode": "PATCH (mise à jour partielle)", "formation": actuelle}), 200

if __name__ == "__main__":
    with app.test_client() as client:
        r1 = client.post("/api/v1/formations", json={"titre": "Audit API"}, headers={"Idempotency-Key": "idem-001"})
        r2 = client.post("/api/v1/formations", json={"titre": "Audit API"}, headers={"Idempotency-Key": "idem-001"})
        print("1. Premier POST (201) :", r1.status_code, r1.get_json())
        print("2. Rejeu idempotent (200 sans doublon) :", r2.status_code, r2.get_json())
        r_patch = client.patch("/api/v1/formations/1", json={"salle": "Amphithéâtre"})
        print("3. PATCH partiel (200) :", r_patch.status_code, r_patch.get_json())
    if os.environ.get("ISGP_WEB_RUNNER") != "1" and "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        print("\n" + "=" * 76)
        print(f"[SERVEUR WSGI FLASK ACTIF] Serveur en écoute sur http://127.0.0.1:{port}")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print(f"  -> Testez les routes en direct sur http://127.0.0.1:{port} (navigateur, curl, Postman)")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
