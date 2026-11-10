import sys
"""
Jour 5 — Script 05 : Documentation Interactive Swagger UI (/api/docs) & Contrat OpenAPI 3.0 (/api/openapi.json)
=================================================================================================================
Objectif :
1. Comprendre la différence entre la spécification OpenAPI 3.0 (le contrat JSON/YAML) et Swagger UI (le portail Web interactif).
2. Construire un contrat OpenAPI 3.0.3 complet incluant :
   - Les routes et paramètres ({id} entre accolades selon le standard RFC 6570)
   - Les schémas de données réutilisables (components.schemas & $ref)
   - Les schémas de sécurité (BearerAuth JWT & ApiKeyAuth X-API-Key pour le bouton "Authorize")
3. Exposer /api/openapi.json et l'interface interactive Swagger UI sur /api/docs dans Flask.
"""

import json
import os
from flask import Flask, jsonify, render_template, request

RACINE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, template_folder=os.path.join(RACINE_PROJET, "templates"))

# Base de données simulée en mémoire
FORMATIONS = [
    {"id": 1, "code": "API-101", "titre": "Fondamentaux REST & HTTP", "duree_jours": 3, "tarif_dzd": 45000},
    {"id": 2, "code": "API-202", "titre": "Sécurité JWT, OAuth2 & OpenAPI", "duree_jours": 5, "tarif_dzd": 75000},
]


# =====================================================================
# 1. DÉFINITION DU CONTRAT OPENAPI 3.0.3 (ANCIENNEMENT SWAGGER)
# =====================================================================
def construire_contrat_openapi():
    """Retourne le dictionnaire Python conforme à la norme OpenAPI 3.0.3."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "API Catalogue Formations ISGP",
            "version": "1.0.0",
            "description": (
                "Contrat officiel OpenAPI 3.0 de l'API des formations ISGP. "
                "Permet de tester les routes via Swagger UI (bouton 'Try it out') "
                "et de s'authentifier via le bouton cadenas 'Authorize'."
            ),
            "contact": {"name": "Direction des Systèmes d'Information ISGP"},
        },
        "servers": [
            {"url": "http://127.0.0.1:5000", "description": "Serveur de développement local"},
            {"url": "https://api.isgp.dz", "description": "Serveur de production"},
        ],
        "tags": [
            {"name": "Formations", "description": "Opérations CRUD sur le catalogue des formations"},
            {"name": "Sécurité", "description": "Routes protégées par Bearer Token ou X-API-Key"},
        ],
        # Définition des modèles JSON réutilisables ($ref) et des cadenas "Authorize"
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Entrez votre jeton signé (sans le mot 'Bearer').",
                },
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "Clé d'API partenaire (ex: isgp-secret-2026).",
                },
            },
            "schemas": {
                "Formation": {
                    "type": "object",
                    "required": ["id", "code", "titre", "duree_jours", "tarif_dzd"],
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "code": {"type": "string", "example": "API-101"},
                        "titre": {"type": "string", "example": "Fondamentaux REST & HTTP"},
                        "duree_jours": {"type": "integer", "minimum": 1, "maximum": 30, "example": 5},
                        "tarif_dzd": {"type": "integer", "minimum": 0, "example": 75000},
                    },
                },
                "FormationInput": {
                    "type": "object",
                    "required": ["code", "titre", "duree_jours", "tarif_dzd"],
                    "properties": {
                        "code": {"type": "string", "example": "API-303"},
                        "titre": {"type": "string", "minLength": 3, "example": "Architecture Microservices"},
                        "duree_jours": {"type": "integer", "minimum": 1, "maximum": 30, "example": 4},
                        "tarif_dzd": {"type": "integer", "minimum": 0, "example": 60000},
                    },
                },
                "ErreurRFC7807": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "example": "https://api.isgp.dz/errors/validation"},
                        "title": {"type": "string", "example": "Erreur de validation métier"},
                        "status": {"type": "integer", "example": 422},
                        "detail": {"type": "string", "example": "Le champ duree_jours doit être >= 1."},
                    },
                },
            },
        },
        # Documentation exhaustive des routes (Noter la syntaxe {id} d'OpenAPI !)
        "paths": {
            "/api/v1/formations": {
                "get": {
                    "tags": ["Formations"],
                    "summary": "Lister toutes les formations du catalogue",
                    "parameters": [
                        {
                            "name": "min_jours",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 1},
                            "description": "Filtrer par durée minimale en jours",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Liste des formations retournée avec succès",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Formation"},
                                    }
                                }
                            },
                        }
                    },
                },
                "post": {
                    "tags": ["Formations", "Sécurité"],
                    "summary": "Créer une nouvelle formation (Protégé par X-API-Key)",
                    "security": [{"ApiKeyAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/FormationInput"}
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Formation créée avec succès",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Formation"}
                                }
                            },
                        },
                        "401": {"description": "Clé X-API-Key manquante ou invalide"},
                        "422": {
                            "description": "Violation des règles de validation métier",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErreurRFC7807"}
                                }
                            },
                        },
                    },
                },
            },
            "/api/v1/formations/{id}": {
                "get": {
                    "tags": ["Formations"],
                    "summary": "Consulter une formation par son identifiant unique",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                            "description": "Identifiant unique de la formation (ex: 1)",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Détail de la formation",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Formation"}
                                }
                            },
                        },
                        "404": {"description": "Formation introuvable"},
                    },
                }
            },
        },
    }


# =====================================================================
# 2. ROUTES EXPOSANT LE CONTRAT (/api/openapi.json) ET SWAGGER UI (/api/docs)
# =====================================================================
@app.route("/api/openapi.json", methods=["GET"])
def openapi_json():
    """Expose le contrat machine OpenAPI 3.0 au format JSON."""
    return jsonify(construire_contrat_openapi()), 200


@app.route("/api/docs", methods=["GET"])
def swagger_ui():
    """Sert le portail interactif Swagger UI via le template Jinja2 templates/swagger_ui.html."""
    return render_template(
        "swagger_ui.html",
        page_title="Swagger UI — API Catalogue ISGP",
        header_title="ISGP — Portail Interactif Swagger UI (OpenAPI 3.0.3)",
        openapi_url="/api/openapi.json",
        demo_api_key="isgp-secret-2026",
    )


# =====================================================================
# 3. ROUTES MÉTIER DOCUMENTÉES PAR LE CONTRAT OPENAPI
# =====================================================================
@app.route("/api/v1/formations", methods=["GET"])
def lister_formations():
    min_jours = request.args.get("min_jours", default=1, type=int)
    resultat = [f for f in FORMATIONS if f["duree_jours"] >= min_jours]
    return jsonify(resultat), 200


@app.route("/api/v1/formations/<int:id>", methods=["GET"])
def obtenir_formation(id):
    for f in FORMATIONS:
        if f["id"] == id:
            return jsonify(f), 200
    return jsonify({"erreur": f"Formation #{id} introuvable"}), 404


# =====================================================================
# 4. DÉMONSTRATION AUTOMATISÉE DU CONTRAT OPENAPI
# =====================================================================
if __name__ == "__main__":
    with app.test_client() as client:
        resp_spec = client.get("/api/openapi.json")
        spec = resp_spec.get_json()
        print("=== CONTRAT OPENAPI 3.0 GÉNÉRÉ AVEC SUCCÈS ===")
        print(f"Titre de l'API      : {spec['info']['title']} (v{spec['info']['version']})")
        print(f"Version OpenAPI     : {spec['openapi']}")
        print(f"Schémas de sécurité : {list(spec['components']['securitySchemes'].keys())}")
        print(f"Modèles de données  : {list(spec['components']['schemas'].keys())}")
        print("Routes documentées  :")
        for chemin, methodes in spec["paths"].items():
            for verbe, details in methodes.items():
                print(f"  - {verbe.upper():6s} {chemin:26s} -> {details['summary']}")
        print("\nExtrait JSON de /components/securitySchemes :")
        print(json.dumps(spec["components"]["securitySchemes"], indent=2, ensure_ascii=False))
    if os.environ.get("ISGP_WEB_RUNNER") != "1" and "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        print("\n" + "=" * 76)
        print(f"[SERVEUR WSGI FLASK ACTIF] Serveur en écoute sur http://127.0.0.1:{port}")
        print("  -> Placez vos points d'arrêt (breakpoints) dans VS Code / Antigravity")
        print(f"  -> Testez les routes en direct sur http://127.0.0.1:{port} (navigateur, curl, Postman)")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
