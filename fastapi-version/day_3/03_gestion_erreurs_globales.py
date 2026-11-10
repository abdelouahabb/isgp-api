# Fichier : day_3/03_gestion_erreurs_globales.py
# Exécution : .venv/bin/python day_3/03_gestion_erreurs_globales.py
# Objectif : Alias pédagogique pour tester @app.exception_handler(404) et @app.exception_handler(Exception).

import importlib.util
import os
from fastapi.testclient import TestClient

_spec = importlib.util.spec_from_file_location(
    "gestion_erreurs", os.path.join(os.path.dirname(__file__), "04_gestion_erreurs_globale.py")
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
app = _mod.app

if __name__ == "__main__":
    client = TestClient(app, raise_server_exceptions=False)
    print("404 ->", client.get("/introuvable").json())
    print("500 ->", client.get("/api/v1/division?a=10&b=0").json())
