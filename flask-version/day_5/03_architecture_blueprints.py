# Fichier : day_5/03_architecture_blueprints.py
# Exécution : .venv/bin/python day_5/03_architecture_blueprints.py
# Objectif : Structurer une API Flask modulaire et comprendre le Versioning (/api/v1 vs /api/v2) :
#   1. Blueprint Web Jinja2 (/portail -> day_5/templates/portail_blueprint.html)
#   2. Blueprint API v1 (/api/v1/formations) : Schéma plat historique + En-têtes de Dépréciation (RFC 8594)
#   3. Blueprint API v2 (/api/v2/formations) : Nouveau schéma avec Rupture de Contrat (Breaking Change)
#   4. Blueprint Supervision (/api/health/live & /api/health/ready) + Application Factory (create_app)

import os
import sys
import time
from flask import Blueprint, Flask, jsonify, render_template

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DEMARRAGE_SERVEUR = time.time()

# SOURCE DE DONNÉES MÉTIER PARTAGÉE ENTRE v1, v2 ET LE PORTAIL WEB
CATALOGUE_METIER = [
    {"id": 1, "code": "ISGP-API-101", "titre": "Architecture API REST & Flask", "jours": 5, "tarif_dzd": 65000},
    {"id": 2, "code": "ISGP-WEB-202", "titre": "Templates Jinja2 & Formulaires", "jours": 3, "tarif_dzd": 45000},
    {"id": 3, "code": "ISGP-SEC-303", "titre": "Sécurité JWT, OAuth2 & WAF", "jours": 4, "tarif_dzd": 60000},
]

# 1. BLUEPRINT WEB (Jinja2) : Sert les pages HTML depuis day_5/templates/
web_bp = Blueprint(
    "portail_web",
    __name__,
    url_prefix="/portail",
    template_folder=os.path.join(DOSSIER_COURANT, "templates"),
)


@web_bp.route("", methods=["GET"])
def afficher_portail():
    titres = [f["titre"] for f in CATALOGUE_METIER]
    return render_template(
        "portail_blueprint.html",
        titre="Portail des Formations ISGP (Blueprint Web Jinja2)",
        items=titres,
    ), 200


# 2. BLUEPRINT API v1 (/api/v1/formations) : Contrat historique maintenu pour les anciens clients
#    Pourquoi v1 est en phase de dépréciation ? Parce que "duree" y était un simple entier (5),
#    et la racine renvoyait une liste plate sans enveloppe de pagination.
formations_v1_bp = Blueprint("formations_v1", __name__, url_prefix="/api/v1/formations")


@formations_v1_bp.after_request
def avertir_depreciation_v1(response):
    # Norme IETF RFC 8594 : Avertit les clients que v1 reste active mais sera éteinte à une date précise
    response.headers["X-API-Version"] = "1.0"
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "Thu, 31 Dec 2026 23:59:59 GMT"
    response.headers["Link"] = '</api/v2/formations>; rel="successor-version"'
    return response


@formations_v1_bp.route("", methods=["GET"])
def lister_formations_v1():
    # Schéma v1 (Historique) : "intitule" (str) et "duree" (int)
    format_v1 = [
        {"id": f["id"], "intitule": f["titre"], "duree": f["jours"], "prix": f["tarif_dzd"]}
        for f in CATALOGUE_METIER
    ]
    return jsonify({"version": "v1", "items": format_v1}), 200


# 3. BLUEPRINT API v2 (/api/v2/formations) : Nouveau contrat avec Breaking Changes assumés
#    - "intitule" est renommé en "titre"
#    - "duree" n'est plus un entier (5), mais un objet structuré {"valeur": 5, "unite": "jours", "heures": 35}
#    - Ajout d'une enveloppe normalisée {"meta": ..., "data": ..., "links": ...}
formations_v2_bp = Blueprint("formations_v2", __name__, url_prefix="/api/v2/formations")


@formations_v2_bp.after_request
def marquer_version_v2(response):
    response.headers["X-API-Version"] = "2.0"
    return response


@formations_v2_bp.route("", methods=["GET"])
def lister_formations_v2():
    format_v2 = [
        {
            "id": f["id"],
            "code_catalogue": f["code"],
            "titre": f["titre"],
            "duree": {"valeur": f["jours"], "unite": "jours", "heures_pedagogiques": f["jours"] * 7},
            "tarification": {"montant_ht": f["tarif_dzd"], "devise": "DZD"},
            "links": {"self": f"/api/v2/formations/{f['id']}"},
        }
        for f in CATALOGUE_METIER
    ]
    return jsonify({
        "meta": {"version": "v2", "total": len(format_v2), "retrocompatible_v1": False},
        "data": format_v2,
    }), 200


# 4. BLUEPRINT SUPERVISION : Sondes de santé (/api/health/live & /api/health/ready)
sante_bp = Blueprint("sante", __name__, url_prefix="/api/health")


@sante_bp.route("/live", methods=["GET"])
def liveness_probe():
    return jsonify({"statut": "UP", "uptime_secondes": round(time.time() - DEMARRAGE_SERVEUR, 1)}), 200


@sante_bp.route("/ready", methods=["GET"])
def readiness_probe():
    db_connectee = True
    return jsonify({"pret": db_connectee, "dependances": {"sqlite": "OK"}}), (200 if db_connectee else 503)


# 5. APPLICATION FACTORY : Assemblage simultané de v1, v2, Web et Santé dans le même serveur
def create_app():
    application = Flask(__name__, template_folder=os.path.join(DOSSIER_COURANT, "templates"))
    application.register_blueprint(web_bp)
    application.register_blueprint(formations_v1_bp)
    application.register_blueprint(formations_v2_bp)
    application.register_blueprint(sante_bp)

    @application.route("/", methods=["GET"])
    def index_blueprints():
        return render_template("index_03_blueprints.html"), 200

    return application


app = create_app()

if __name__ == "__main__":
    with app.test_client() as client:
        assert client.get("/").status_code == 200
        print("=== 1. BLUEPRINT API v1 (AVEC EN-TÊTES DE DÉPRÉCIATION RFC 8594) ===")
        r1 = client.get("/api/v1/formations")
        print("Headers v1 :", {k: r1.headers[k] for k in ("X-API-Version", "Deprecation", "Sunset", "Link")})
        print("JSON v1    :", r1.get_json()["items"][0])

        print("\n=== 2. BLUEPRINT API v2 (NOUVEAU SCHÉMA ENRICHI COEXISTANT) ===")
        r2 = client.get("/api/v2/formations")
        print("Headers v2 :", {"X-API-Version": r2.headers["X-API-Version"]})
        print("JSON v2    :", r2.get_json()["data"][0])
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
