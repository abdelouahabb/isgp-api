# Fichier : day_3/04_transactions_et_injection_sql.py
# Exécution : .venv/bin/python day_3/04_transactions_et_injection_sql.py
# Objectif : Démontrer la prévention des Injections SQL par requêtes paramétrées (?)
#            et l'atomicité des transactions ACID SQLite (COMMIT / ROLLBACK) dans FastAPI.

import sqlite3
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI(title="ISGP - Transactions ACID & Prévention Injection SQL", version="1.0.0")

CONN = sqlite3.connect(":memory:", check_same_thread=False)
CONN.row_factory = sqlite3.Row
CONN.execute("CREATE TABLE comptes_budget (id INTEGER PRIMARY KEY, service TEXT, solde INTEGER)")
CONN.execute("INSERT INTO comptes_budget (id, service, solde) VALUES (1, 'Direction Formation', 50000), (2, 'Laboratoire IT', 20000)")
CONN.commit()


class VirementBudget(BaseModel):
    source_id: int
    cible_id: int
    montant: int


@app.get("/api/v1/comptes/recherche")
async def rechercher_service(service: str = Query(...)):
    # SÉCURISÉ : Le tuple (service,) est passé en paramètre lié (?) au moteur SQLite
    lignes = CONN.execute("SELECT * FROM comptes_budget WHERE service = ?", (service,)).fetchall()
    return {"resultats": [dict(r) for r in lignes]}


@app.post("/api/v1/comptes/virement")
async def effectuer_virement_acid(virement: VirementBudget):
    try:
        # Context manager 'with CONN:' : COMMIT automatique si succès, ROLLBACK intégral si exception !
        with CONN:
            src = CONN.execute("SELECT solde FROM comptes_budget WHERE id = ?", (virement.source_id,)).fetchone()
            if not src or src["solde"] < virement.montant:
                raise ValueError("Solde insuffisant : transaction annulée (ROLLBACK)")
            CONN.execute("UPDATE comptes_budget SET solde = solde - ? WHERE id = ?", (virement.montant, virement.source_id))
            CONN.execute("UPDATE comptes_budget SET solde = solde + ? WHERE id = ?", (virement.montant, virement.cible_id))
        return {"statut": "COMMIT_EFFECTUE", "montant": virement.montant}
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


if __name__ == "__main__":
    client = TestClient(app)
    print("=== 1. TEST ANTI-INJECTION SQL (Requête paramétrée ?) ===")
    attaque = "' OR '1'='1"
    rep_sqli = client.get("/api/v1/comptes/recherche", params={"service": attaque})
    print(f"Payload malveillant ({attaque}) -> Résultats retournés :", rep_sqli.json()["resultats"])

    print("\n=== 2. TEST TRANSACTION ACID (COMMIT vs ROLLBACK) ===")
    print("Virement valide (10000) :", client.post("/api/v1/comptes/virement", json={"source_id": 1, "cible_id": 2, "montant": 10000}).json())
    print("Virement excessif (999999) :", client.post("/api/v1/comptes/virement", json={"source_id": 1, "cible_id": 2, "montant": 999999}).json())
