# Fichier : day_0/02_listes_et_dictionnaires.py
# Exécution : python day_0/02_listes_et_dictionnaires.py

# 1. Dictionnaire structurant un enregistrement (Clé : Valeur)
stagiaire = {
    "id": 1,
    "nom": "Merabet",
    "prenom": "Yasmine",
    "competences": ["Python", "HTTP"]
}

# 2. Accès en lecture via la clé
print("Prénom :", stagiaire["prenom"])

# 3. Ajout ou modification d'un attribut
stagiaire["ville"] = "Alger"
print("Enregistrement complet :", stagiaire)

# 4. Liste de dictionnaires (structure standard d'une collection JSON)
catalogue_formations = [
    {"code": "API-101", "titre": "Architecture des APIs REST", "places": 15},
    {"code": "FLK-202", "titre": "Services Web avec Flask", "places": 12}
]
catalogue_formations.append({"code": "SEC-303", "titre": "Sécurité, Tokens & Rate Limiting", "places": 20})

for f in catalogue_formations:
    print("-", f["code"], ":", f["titre"], "(Places:", f["places"], ")")
