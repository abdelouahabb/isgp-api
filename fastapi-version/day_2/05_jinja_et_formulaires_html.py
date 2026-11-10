import sys
"""
Jour 2 — Script 05 : Moteur Jinja2Templates & Formulaires Web HTML (Form / File / UploadFile)
=============================================================================================
Objectif :
1. Remplacer tout HTML codé en dur dans Python par des fichiers de templates Jinja2 (.html dans templates/).
2. Maîtriser la syntaxe Jinja2 : variables {{ ... }} (avec protection automatique Anti-XSS), boucles {% for %} et conditions {% if %}.
3. Comprendre comment un formulaire HTML (<form method="POST">) transmet ses données en 'application/x-www-form-urlencoded'
   et comment FastAPI les extrait avec `Form(...)` (et `UploadFile = File(...)` pour les fichiers 'multipart/form-data').
4. Concevoir un service Web hybride capable de répondre à la fois à un formulaire HTML (Jinja2Templates) et à un client API (JSON).
"""

import os
import re
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient

# FastAPI utilise Jinja2Templates pointant vers le sous-dossier "templates/"
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="ISGP - Jinja2Templates & Formulaires FastAPI", version="1.0.0")
templates = Jinja2Templates(directory=os.path.join(DOSSIER_COURANT, "templates"))

# Base de données en mémoire pour la démonstration
FORMATIONS = [
    {"id": 1, "titre": "Architecture API REST & FastAPI", "duree_jours": 5, "salle": "Salle A"},
    {"id": 2, "titre": "Jinja2Templates & Formulaires Web", "duree_jours": 3, "salle": "Salle B"},
]


def nettoyer_nom_fichier(nom_brut: str) -> str:
    """Nettoie le nom d'un fichier téléversé pour empêcher toute attaque Path Traversal (../)."""
    base = os.path.basename(nom_brut or "fichier.bin")
    nettoye = re.sub(r"[^A-Za-z0-9._-]", "_", base).strip("._")
    return nettoye or "document_securise.pdf"


# =====================================================================
# 1. ROUTE WEB HYBRIDE : AFFICHAGE JINJA2 (GET) + FORMULAIRE HTML (POST)
# =====================================================================
@app.get("/formations", response_class=HTMLResponse)
async def afficher_catalogue_formations(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="formations.html",
        context={
            "titre_page": "Catalogue & Inscription des Formations ISGP",
            "formations": FORMATIONS,
            "erreurs": [],
            "message_confirmation": None,
        },
    )


@app.post("/formations")
async def soumettre_formation(request: Request):
    erreurs = []
    message_confirmation = None

    # DISTINCTION FONDAMENTALE DANS FASTAPI :
    # - Si Content-Type est application/json, on lit await request.json()
    # - Si c'est un formulaire HTML (application/x-www-form-urlencoded), on lit await request.form() (ou Form(...))
    content_type = request.headers.get("content-type", "")
    est_json = "application/json" in content_type
    if est_json:
        source = await request.json()
    else:
        form_data = await request.form()
        source = dict(form_data)

    titre = str(source.get("titre", "")).strip()
    salle = str(source.get("salle", "Salle A")).strip() or "Salle A"
    try:
        duree_jours = int(source.get("duree_jours", 0))
    except (TypeError, ValueError):
        duree_jours = 0

    if len(titre) < 3:
        erreurs.append("Le champ 'titre' doit contenir au moins 3 caractères.")
    if not (1 <= duree_jours <= 30):
        erreurs.append("Le champ 'duree_jours' doit être un entier compris entre 1 et 30.")

    if not erreurs:
        nouvelle = {
            "id": len(FORMATIONS) + 1,
            "titre": titre,
            "duree_jours": duree_jours,
            "salle": salle,
        }
        FORMATIONS.append(nouvelle)
        message_confirmation = f"La formation « {titre} » a été enregistrée avec l'ID #{nouvelle['id']}."

        if est_json or "application/json" in request.headers.get("accept", ""):
            return JSONResponse(status_code=status.HTTP_201_CREATED, content={"statut": "cree", "formation": nouvelle})
    else:
        if est_json or "application/json" in request.headers.get("accept", ""):
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"erreurs": erreurs})

    return templates.TemplateResponse(
        request=request,
        name="formations.html",
        context={
            "titre_page": "Catalogue & Inscription des Formations ISGP",
            "formations": FORMATIONS,
            "erreurs": erreurs,
            "message_confirmation": message_confirmation,
        },
        status_code=(status.HTTP_422_UNPROCESSABLE_ENTITY if erreurs else status.HTTP_200_OK),
    )


# =====================================================================
# 2. TRAITEMENT D'UN FORMULAIRE MULTIPART AVEC FICHIER (Form + UploadFile)
# =====================================================================
@app.post("/formations/upload-syllabus", status_code=status.HTTP_201_CREATED)
async def uploader_syllabus(
    code_formation: str = Form(default="API-101"),
    document_pdf: UploadFile = File(...),
):
    """Traite un formulaire <form enctype='multipart/form-data'> via Form(...) et UploadFile = File(...)."""
    if not document_pdf or not document_pdf.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aucun fichier fourni dans 'document_pdf'")

    nom_securise = nettoyer_nom_fichier(document_pdf.filename)
    contenu_octets = await document_pdf.read()

    return {
        "statut": "Syllabus reçu via multipart/form-data (FastAPI UploadFile)",
        "code_formation": code_formation,
        "nom_fichier_securise": nom_securise,
        "taille_octets": len(contenu_octets),
        "content_type_recu": document_pdf.content_type,
    }


# =====================================================================
# 3. DÉMONSTRATION AUTOMATISÉE (SOUMISSION DE FORMULAIRE + RENDU JINJA2)
# =====================================================================
if __name__ == "__main__":
    import io

    client = TestClient(app)
    print("=== 1. TEST SOUMISSION D'UN FORMULAIRE HTML (Form / request.form) ===")
    rep_form = client.post(
        "/formations",
        data={"titre": "Sécurité OAuth2 & Formulaires", "duree_jours": "4", "salle": "Salle C"},
    )
    html_rendu = rep_form.text
    print("Statut HTTP :", rep_form.status_code)
    print("Type MIME   :", rep_form.headers["content-type"])
    print("Extrait du HTML généré par Jinja2Templates (day_2/templates/formations.html) :")
    for ligne in html_rendu.splitlines():
        if "Sécurité OAuth2" in ligne or 'class="succes"' in ligne:
            print("  ->", ligne.strip())

    print("\n=== 2. TEST UPLOAD DE FICHIER MULTIPART (UploadFile = File(...)) ===")
    rep_upload = client.post(
        "/formations/upload-syllabus",
        data={"code_formation": "API-202"},
        files={"document_pdf": ("programme_isgp 2026.pdf", io.BytesIO(b"%PDF-1.4 Programme officiel du bootcamp ISGP"), "application/pdf")},
    )
    print("Réponse JSON upload :", rep_upload.json())
    if "--once" not in sys.argv:
        import uvicorn
        port = int(os.environ.get("PORT", 8001))
        print("\n" + "=" * 76)
        print(f"[BOUCLE ASGI UVICORN / FASTAPI ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Interface Swagger UI interactive : http://127.0.0.1:{port}/docs")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur ASGI.")
        print("=" * 76)
        uvicorn.run(app, host="0.0.0.0", port=port)
