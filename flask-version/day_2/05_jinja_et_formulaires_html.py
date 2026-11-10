import sys
"""
Jour 2 — Script 05 : Moteur de Templates Jinja2 (render_template) & Formulaires Web HTML (request.form / request.files)
=======================================================================================================================
Objectif :
1. Remplacer tout HTML codé en dur dans Python par des fichiers de templates Jinja2 (.html dans le dossier templates/).
2. Maîtriser la syntaxe Jinja2 : variables {{ ... }} (avec protection automatique Anti-XSS), boucles {% for %} et conditions {% if %}.
3. Comprendre comment un formulaire HTML (<form method="POST">) transmet ses données en 'application/x-www-form-urlencoded'
   et comment Flask les extrait avec 'request.form' (et 'request.files' pour les fichiers 'multipart/form-data').
4. Concevoir un service Web hybride capable de répondre à la fois à un formulaire HTML (Jinja2) et à un client API (JSON).
"""

import os
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

# Flask cherche automatiquement les fichiers .html dans le sous-dossier "templates/"
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))

# Base de données en mémoire pour la démonstration
FORMATIONS = [
    {"id": 1, "titre": "Architecture API REST & Flask", "duree_jours": 5, "salle": "Salle A"},
    {"id": 2, "titre": "Templates Jinja2 & Formulaires Web", "duree_jours": 3, "salle": "Salle B"},
]


# =====================================================================
# 1. ROUTE WEB HYBRIDE : FORMULAIRE HTML (request.form) + RENDU JINJA2
# =====================================================================
@app.route("/formations", methods=["GET", "POST"])
def gerer_formations():
    erreurs = []
    message_confirmation = None

    if request.method == "POST":
        # DISTINCTION FONDAMENTALE :
        # - Si le client est un formulaire HTML (<form method="POST">), les données sont dans request.form
        # - Si le client est une application mobile / API (Content-Type: application/json), elles sont dans request.get_json()
        if request.is_json:
            source = request.get_json(silent=True) or {}
        else:
            # request.form lit les champs <input name="..."> envoyés en application/x-www-form-urlencoded
            source = request.form

        titre = str(source.get("titre", "")).strip()
        salle = str(source.get("salle", "Salle A")).strip() or "Salle A"
        try:
            duree_jours = int(source.get("duree_jours", 0))
        except (TypeError, ValueError):
            duree_jours = 0

        # Validation métier identique pour le formulaire Web et pour l'API JSON
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

            # Si le client est un programme API (Accept: application/json ou corps JSON), on renvoie du JSON :
            if request.is_json or "application/json" in request.headers.get("Accept", ""):
                return jsonify({"statut": "cree", "formation": nouvelle}), 201
        else:
            if request.is_json or "application/json" in request.headers.get("Accept", ""):
                return jsonify({"erreurs": erreurs}), 422

    # Rendu du fichier HTML day_2/templates/formations.html via le moteur Jinja2 :
    # Zéro HTML écrit en dur dans le code Python !
    return render_template(
        "formations.html",
        titre_page="Catalogue & Inscription des Formations ISGP",
        formations=FORMATIONS,
        erreurs=erreurs,
        message_confirmation=message_confirmation,
    ), (422 if erreurs else 200)


# =====================================================================
# 2. TRAITEMENT D'UN FORMULAIRE MULTIPART AVEC FICHIER (request.files)
# =====================================================================
@app.route("/formations/upload-syllabus", methods=["POST"])
def uploader_syllabus():
    """Traite un formulaire <form enctype='multipart/form-data'> contenant texte + fichier."""
    code_formation = request.form.get("code_formation", "API-101")
    fichier = request.files.get("document_pdf")

    if not fichier or not fichier.filename:
        return jsonify({"erreur": "Aucun fichier fourni dans le champ 'document_pdf'"}), 400

    # Règle de sécurité absolue : toujours nettoyer le nom du fichier avec secure_filename()
    # pour empêcher l'attaque Path Traversal (ex: filename = "../../etc/passwd")
    nom_securise = secure_filename(fichier.filename)
    contenu_octets = fichier.read()

    return jsonify({
        "statut": "Syllabus reçu via multipart/form-data",
        "code_formation": code_formation,
        "nom_fichier_securise": nom_securise,
        "taille_octets": len(contenu_octets),
        "content_type_recu": fichier.content_type,
    }), 201


# =====================================================================
# 3. DÉMONSTRATION AUTOMATISÉE (SOUMISSION DE FORMULAIRE + RENDU JINJA2)
# =====================================================================
if __name__ == "__main__":
    import io

    with app.test_client() as client:
        print("=== 1. TEST SOUMISSION D'UN FORMULAIRE HTML (request.form) ===")
        # data={...} (sans json=...) simule exactement un <form method="POST"> HTML (application/x-www-form-urlencoded)
        rep_form = client.post(
            "/formations",
            data={"titre": "Sécurité OAuth2 & Formulaires", "duree_jours": "4", "salle": "Salle C"},
        )
        html_rendu = rep_form.get_data(as_text=True)
        print("Statut HTTP :", rep_form.status_code)
        print("Type MIME   :", rep_form.content_type)
        print("Extrait du HTML généré par le template Jinja2 (day_2/templates/formations.html) :")
        for ligne in html_rendu.splitlines():
            if "Sécurité OAuth2" in ligne or "class=\"succes\"" in ligne:
                print("  ->", ligne.strip())

        print("\n=== 2. TEST UPLOAD DE FICHIER MULTIPART (request.files) ===")
        rep_upload = client.post(
            "/formations/upload-syllabus",
            data={
                "code_formation": "API-202",
                "document_pdf": (io.BytesIO(b"%PDF-1.4 Programme officiel du bootcamp ISGP"), "programme_isgp 2026.pdf"),
            },
            content_type="multipart/form-data",
        )
        print("Réponse JSON upload :", rep_upload.get_json())
    if "--once" not in sys.argv:
        import socket as _sock
        port = int(os.environ.get("PORT", 5001))
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
            if _s.connect_ex(("127.0.0.1", port)) == 0:
                _s2 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                _s2.bind(("127.0.0.1", 0))
                port = _s2.getsockname()[1]
                _s2.close()
        print("\n" + "=" * 76)
        print(f"[SERVEUR WSGI FLASK ACTIF] Serveur en écoute sur http://127.0.0.1:{port}")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print(f"  -> Testez les routes en direct sur http://127.0.0.1:{port} (navigateur, curl, Postman)")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
