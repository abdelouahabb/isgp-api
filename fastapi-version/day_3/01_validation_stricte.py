# Fichier : day_3/01_validation_stricte.py
# Exécution : .venv/bin/python day_3/01_validation_stricte.py
# Objectif : Validation stricte Pydantic v2 (BaseModel, Field(ge=1, le=30), @field_validator) & 422 RFC 7807.

import importlib.util
import os
from fastapi.testclient import TestClient

_spec = importlib.util.spec_from_file_location(
    "crud_memoire", os.path.join(os.path.dirname(__file__), "01_api_crud_memoire.py")
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
app = _mod.app

if __name__ == "__main__":
    client = TestClient(app)
    r_ok = client.post("/api/v1/formations", json={"titre": "Architecture FastAPI", "duree_jours": 5})
    r_ko = client.post("/api/v1/formations", json={"titre": "X", "duree_jours": 45})
    print("Valide (201)   :", r_ok.status_code, r_ok.json())
    print("Invalide (422) :", r_ko.status_code, r_ko.json()["champs_en_erreur"])
