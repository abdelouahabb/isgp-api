"""
Jour 2 — Script 05 : Moteur de Templates Tornado (self.render) & Formulaires Web HTML (self.get_body_argument / self.request.files)
===================================================================================================================================
Objectif :
1. Remplacer tout HTML codé en dur dans Python par des fichiers de templates Tornado (.html dans le dossier templates/).
2. Maîtriser la syntaxe tornado.template : variables {{ ... }} (échappement Anti-XSS automatique), boucles {% for ... %} ... {% end %} et conditions {% if ... %} ... {% end %}.
3. Comprendre comment un formulaire HTML (<form method="POST">) transmet ses données en 'application/x-www-form-urlencoded'
   et comment Tornado les extrait avec 'self.get_body_argument()' (et 'self.request.files' pour les fichiers 'multipart/form-data').
4. Concevoir un RequestHandler hybride capable de répondre à la fois à un formulaire HTML (self.render) et à un client API (self.write).
"""

import asyncio
import os
import re
import urllib.parse
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.netutil
import tornado.web

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))

# Base de données en mémoire pour la démonstration
FORMATIONS = [
    {"id": 1, "titre": "Architecture API REST & Tornado", "duree_jours": 5, "salle": "Salle A"},
    {"id": 2, "titre": "Templates Tornado & Formulaires Web", "duree_jours": 3, "salle": "Salle B"},
]


def nettoyer_nom_fichier(nom_brut):
    """Nettoie le nom d'un fichier uploadé pour bloquer toute attaque Path Traversal (../../etc/passwd)."""
    base = os.path.basename(nom_brut or "")
    return re.sub(r"[^A-Za-z0-9_.-]", "_", base)


# =====================================================================
# 1. HANDLER WEB HYBRIDE : FORMULAIRE HTML (self.get_body_argument) + RENDU TEMPLATE
# =====================================================================
class FormationsHybrideHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "formations.html",
            titre_page="Catalogue & Inscription des Formations ISGP (Tornado)",
            formations=FORMATIONS,
            erreurs=[],
            message_confirmation=None,
        )

    def post(self):
        erreurs = []
        message_confirmation = None
        content_type = self.request.headers.get("Content-Type", "")
        est_json = "application/json" in content_type

        # DISTINCTION FONDAMENTALE DANS TORNADO :
        # - Si le client est une API JSON, on décode self.request.body via tornado.escape.json_decode()
        # - Si le client est un formulaire HTML (<form method="POST">), on utilise self.get_body_argument()
        if est_json:
            source = tornado.escape.json_decode(self.request.body or b"{}")
            titre = str(source.get("titre", "")).strip()
            salle = str(source.get("salle", "Salle A")).strip() or "Salle A"
            duree_brute = source.get("duree_jours", 0)
        else:
            titre = self.get_body_argument("titre", "").strip()
            salle = self.get_body_argument("salle", "Salle A").strip() or "Salle A"
            duree_brute = self.get_body_argument("duree_jours", "0")

        try:
            duree_jours = int(duree_brute)
        except (TypeError, ValueError):
            duree_jours = 0

        if len(titre) < 3:
            erreurs.append("Le champ 'titre' doit contenir au moins 3 caractères.")
        if not (1 <= duree_jours <= 30):
            erreurs.append("Le champ 'duree_jours' doit être un entier compris entre 1 et 30.")

        veut_json = est_json or "application/json" in self.request.headers.get("Accept", "")

        if not erreurs:
            nouvelle = {
                "id": len(FORMATIONS) + 1,
                "titre": titre,
                "duree_jours": duree_jours,
                "salle": salle,
            }
            FORMATIONS.append(nouvelle)
            message_confirmation = f"La formation « {titre} » a été enregistrée avec l'ID #{nouvelle['id']}."
            if veut_json:
                self.set_status(201)
                self.write({"statut": "cree", "formation": nouvelle})
                return
        else:
            self.set_status(422)
            if veut_json:
                self.write({"erreurs": erreurs})
                return

        self.render(
            "formations.html",
            titre_page="Catalogue & Inscription des Formations ISGP (Tornado)",
            formations=FORMATIONS,
            erreurs=erreurs,
            message_confirmation=message_confirmation,
        )


# =====================================================================
# 2. TRAITEMENT D'UN FORMULAIRE MULTIPART AVEC FICHIER (self.request.files)
# =====================================================================
class UploadSyllabusHandler(tornado.web.RequestHandler):
    def post(self):
        """Traite un formulaire <form enctype='multipart/form-data'> contenant texte + fichier."""
        code_formation = self.get_body_argument("code_formation", "API-101")
        fichiers = self.request.files.get("document_pdf", [])

        if not fichiers:
            self.set_status(400)
            self.write({"erreur": "Aucun fichier fourni dans le champ 'document_pdf'"})
            return

        # Dans Tornado, chaque fichier de self.request.files['champ'] est un dict :
        # {"filename": "...", "body": b"...", "content_type": "..."}
        fichier_info = fichiers[0]
        nom_securise = nettoyer_nom_fichier(fichier_info["filename"])
        contenu_octets = fichier_info["body"]

        self.set_status(201)
        self.write({
            "statut": "Syllabus reçu via multipart/form-data (self.request.files)",
            "code_formation": code_formation,
            "nom_fichier_securise": nom_securise,
            "taille_octets": len(contenu_octets),
            "content_type_recu": fichier_info.get("content_type", "application/pdf"),
        })


def make_app():
    return tornado.web.Application(
        [
            (r"/formations", FormationsHybrideHandler),
            (r"/formations/upload-syllabus", UploadSyllabusHandler),
        ],
        template_path=os.path.join(DOSSIER_COURANT, "templates"),
    )


async def _demo():
    app = make_app()
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    print("=== 1. TEST SOUMISSION D'UN FORMULAIRE HTML (self.get_body_argument) ===")
    form_body = urllib.parse.urlencode({
        "titre": "Sécurité OAuth2 & Formulaires Tornado",
        "duree_jours": "4",
        "salle": "Salle C",
    })
    rep_form = await client.fetch(
        f"http://127.0.0.1:{port}/formations",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=form_body,
    )
    html_rendu = rep_form.body.decode("utf-8")
    print("Statut HTTP :", rep_form.code)
    print("Type MIME   :", rep_form.headers["Content-Type"])
    print("Extrait du HTML généré par tornado.template (day_2/templates/formations.html) :")
    for ligne in html_rendu.splitlines():
        if "Sécurité OAuth2" in ligne or 'class="succes"' in ligne:
            print("  ->", ligne.strip())

    print("\n=== 2. TEST UPLOAD DE FICHIER MULTIPART (self.request.files) ===")
    boundary = "----TornadoBootcampBoundary2026"
    multipart_body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="code_formation"\r\n\r\n'
        "API-202\r\n"
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="document_pdf"; filename="../../programme_isgp 2026.pdf"\r\n'
        "Content-Type: application/pdf\r\n\r\n"
        "%PDF-1.4 Programme officiel du bootcamp ISGP Tornado\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")
    rep_upload = await client.fetch(
        f"http://127.0.0.1:{port}/formations/upload-syllabus",
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        body=multipart_body,
    )
    print("Réponse JSON upload :", tornado.escape.json_decode(rep_upload.body))
    server.stop()


if __name__ == "__main__":
    asyncio.run(_demo())
