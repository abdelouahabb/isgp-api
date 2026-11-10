# Fichier : day_0/03_fonctions.py
# Exécution : python day_0/03_fonctions.py

def calculer_ttc(prix_ht):
    tva = prix_ht * 0.19
    prix_total = prix_ht + tva
    return {
        "prix_ht": prix_ht,
        "tva_19": round(tva, 2),
        "prix_ttc": round(prix_total, 2)
    }

facture = calculer_ttc(1000)
print("Facture calculée :", facture)
