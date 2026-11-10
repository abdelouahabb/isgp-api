# Fichier : day_0/04_exceptions_et_decorateurs.py
# Exécution : .venv/bin/python day_0/04_exceptions_et_decorateurs.py

import time

# ==============================================================================
# 1. GESTION DES EXCEPTIONS (try / except) : EMPÊCHER LE PROGRAMME DE PLANTER
# ==============================================================================
def convertir_en_entier_securise(valeur_texte: str, valeur_par_defaut: int = 1) -> dict:
    try:
        resultat = int(valeur_texte)
        return {"succes": True, "valeur": resultat}
    except ValueError:
        # Au lieu de faire planter le serveur ASGI, on capture l'erreur proprement
        return {
            "succes": False,
            "erreur": f"'{valeur_texte}' n'est pas un nombre entier valide.",
            "valeur_retenue": valeur_par_defaut,
        }


print("=== 1. TEST DE GESTION D'ERREUR (try / except) ===")
print("Entrée valide '42'   ->", convertir_en_entier_securise("42"))
print("Entrée invalide 'abc'->", convertir_en_entier_securise("abc"))


# ==============================================================================
# 2. COMPRENDRE LES DÉCORATEURS (@) : LE MÉCANISME AU CŒUR DE FASTAPI (@app.get)
# ==============================================================================
def journaliser_execution(fonction_originale):
    """
    Un décorateur est une fonction qui prend une fonction en entrée
    et retourne une fonction 'enveloppée' (wrapper) enrichie d'un comportement.
    C'est exactement ainsi que fonctionnent @app.get("/...") et @app.post("/...") dans FastAPI.
    """
    def enveloppe(*args, **kwargs):
        debut = time.time()
        print(f"[AUDIT ASGI] Appel de la fonction '{fonction_originale.__name__}'...")
        resultat = fonction_originale(*args, **kwargs)
        duree_ms = round((time.time() - debut) * 1000, 2)
        print(f"[AUDIT ASGI] Terminé en {duree_ms} ms -> Résultat : {resultat}")
        return resultat
    return enveloppe


@journaliser_execution
def traiter_inscription(nom_stagiaire: str, formation: str) -> dict:
    return {"stagiaire": nom_stagiaire, "formation": formation, "statut": "inscrit"}


print("\n=== 2. TEST DU DÉCORATEUR (@journaliser_execution) ===")
traiter_inscription("Yasmine Merabet", "Architecture API REST & FastAPI")
