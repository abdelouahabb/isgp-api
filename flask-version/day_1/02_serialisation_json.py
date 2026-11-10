# Fichier : day_1/02_serialisation_json.py
# Exécution : python day_1/02_serialisation_json.py
# Objectif : Structurer une enveloppe JSON professionnelle (data, meta, ISO 8601)

import json
from datetime import datetime, timezone

# 1. Enveloppe de réponse JSON normalisée (Standard d'architecture API)
enveloppe_reponse_api = {
    "meta": {
        "api_version": "1.0",
        "horodatage_iso8601": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "statut_succes": True
    },
    "data": {
        "id": 101,
        "intitule": "Développement d'APIs et services web",
        "organisme": "ISGP",
        "prerequis_exiges": None,
        "methodes_idempotentes": ["GET", "PUT", "DELETE"],
        "methodes_non_idempotentes": ["POST"]
    }
}

# 2. Sérialisation (Dictionnaire Python -> Chaîne JSON UTF-8)
texte_json = json.dumps(enveloppe_reponse_api, indent=2, ensure_ascii=False)
print("=== ENVELOPPE JSON NORMALISÉE (json.dumps) ===")
print(texte_json)

# 3. Désérialisation (Chaîne JSON -> Dictionnaire Python)
retour_dict = json.loads(texte_json)
print("\n=== LECTURE EN PYTHON (json.loads) ===")
print("Horodatage UTC :", retour_dict["meta"]["horodatage_iso8601"])
print("Méthodes idempotentes :", retour_dict["data"]["methodes_idempotentes"])
