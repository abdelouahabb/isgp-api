# Fichier : day_1/02_serialisation_json.py
# Exécution : .venv/bin/python day_1/02_serialisation_json.py
# Objectif : Structurer une enveloppe JSON professionnelle (data, meta, ISO 8601)
#            avec json.dumps / tornado.escape.json_encode et tornado.escape.json_decode

import json
from datetime import datetime, timezone
import tornado.escape

# 1. Enveloppe de réponse JSON normalisée (Standard d'architecture API)
enveloppe_reponse_api = {
    "meta": {
        "api_version": "1.0",
        "moteur_http": "Tornado Non-Blocking IOLoop",
        "horodatage_iso8601": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "statut_succes": True,
    },
    "data": {
        "id": 101,
        "intitule": "Développement d'APIs et services web (Tornado)",
        "organisme": "ISGP",
        "prerequis_exiges": None,
        "methodes_idempotentes": ["GET", "PUT", "DELETE"],
        "methodes_non_idempotentes": ["POST"],
    },
}

# 2. Sérialisation lisible (json.dumps) et sérialisation compacte Tornado (json_encode)
texte_json = json.dumps(enveloppe_reponse_api, indent=2, ensure_ascii=False)
print("=== ENVELOPPE JSON NORMALISÉE (json.dumps / self.write) ===")
print(texte_json)

# 3. Désérialisation rapide via tornado.escape.json_decode (utilisée sur self.request.body)
retour_dict = tornado.escape.json_decode(texte_json)
print("\n=== LECTURE EN PYTHON (tornado.escape.json_decode) ===")
print("Moteur HTTP           :", retour_dict["meta"]["moteur_http"])
print("Horodatage UTC        :", retour_dict["meta"]["horodatage_iso8601"])
print("Méthodes idempotentes :", retour_dict["data"]["methodes_idempotentes"])
