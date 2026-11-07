# Fichier : day_1/02_serialisation_json.py
# Exécution : python day_1/02_serialisation_json.py

import json

# 1. Dictionnaire Python (utilise True et None)
donnees_python = {
    "formation": "Développement d'APIs et services web",
    "organisme": "ISGP",
    "certifiante": True,
    "prerequis": None,
    "jours": 5,
    "methodes_http": ["GET", "POST", "PUT", "DELETE"]
}

# 2. Sérialisation (Dictionnaire Python -> Chaîne JSON réseau)
texte_json = json.dumps(donnees_python, indent=2, ensure_ascii=False)
print("=== FLUX JSON GÉNÉRÉ (json.dumps) ===")
print(texte_json)

# 3. Désérialisation (Chaîne JSON -> Dictionnaire Python)
retour_dict = json.loads(texte_json)
print("\n=== LECTURE EN PYTHON (json.loads) ===")
print("Organisme :", retour_dict["organisme"])
print("Méthodes supportées :", retour_dict["methodes_http"])
