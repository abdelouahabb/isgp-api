"""
Jour 5 — Script 05 : Documentation Interactive Swagger UI (/api/docs) & Contrat OpenAPI 3.0 (/api/openapi.json) avec Tornado
============================================================================================================================
Objectif :
1. Comprendre la différence entre la spécification OpenAPI 3.0 (le contrat JSON/YAML) et Swagger UI (le portail Web interactif).
2. Construire un contrat OpenAPI 3.0.3 complet incluant :
   - Les routes et paramètres ({id} entre accolades selon le standard RFC 6570, correspondant au groupe Regex ([0-9]+) de Tornado)
   - Les schémas de données réutilisables (components.schemas & $ref)
   - Les schémas de sécurité (BearerAuth JWT & ApiKeyAuth X-API-Key pour le bouton "Authorize")
3. Exposer /api/openapi.json et l'interface interactive Swagger UI sur /api/docs dans Tornado.
"""

import asyncio
import json
import os
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.netutil
import tornado.web

RACINE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Base de données simulée en mémoire
FORMATIONS = [
    {"id": 1, "code": "API-101", "titre": "Fondamentaux REST & HTTP", "duree_jours": 3, "tarif_dzd": 45000},
    {"id": 2, "code": "API-202", "titre": "Sécurité JWT, OAuth2 & OpenAPI (Tornado)", "duree_jours": 5, "tarif_dzd": 75000},
]


# =====================================================================
# 1. DÉFINITION DU CONTRAT OPENAPI 3.0.3 (ANCIENNEMENT SWAGGER)
# =====================================================================
def construire_contrat_openapi():
    """Retourne le dictionnaire Python conforme à la norme OpenAPI 3.0.3."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "API Catalogue Formations ISGP (Édition Tornado)",
            "version": "1.0.0",
            "description": (
                "Contrat officiel OpenAPI 3.0 de l'API Tornado des formations ISGP. "
                "Permet de tester les routes via Swagger UI (bouton 'Try it out') "
                "et de s'authentifier via le bouton cadenas 'Authorize'."
            ),
            "contact": {"name": "Direction des Systèmes d'Information ISGP"},
        },
        "servers": [
            {"url": "http://127.0.0.1:8888", "description": "Serveur Tornado de développement local"},
            {"url": "https://api.isgp.dz", "description": "Serveur de production"},
        ],
        "tags": [
            {"name": "Formations", "description": "Opérations CRUD sur le catalogue des formations"},
            {"name": "Sécurité", "description": "Routes protégées par Bearer Token ou X-API-Key"},
        ],
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
                        "titre": {"type": "string", "minLength": 3, "example": "Architecture Microservices Tornado"},
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
# 2. HANDLERS EXPOSANT LE CONTRAT (/api/openapi.json) ET SWAGGER UI (/api/docs)
# =====================================================================
class OpenApiSpecHandler(tornado.web.RequestHandler):
    def get(self):
        """Expose le contrat machine OpenAPI 3.0 au format JSON."""
        self.write(construire_contrat_openapi())


class SwaggerUiHandler(tornado.web.RequestHandler):
    def get(self):
        """Sert le portail interactif Swagger UI via le template templates/swagger_ui.html."""
        self.render(
            "swagger_ui.html",
            page_title="Swagger UI — API Catalogue ISGP (Tornado)",
            header_title="ISGP — Portail Interactif Swagger UI (OpenAPI 3.0.3 • Tornado)",
            openapi_url="/api/openapi.json",
            demo_api_key="isgp-secret-2026",
        )


# =====================================================================
# 3. HANDLERS MÉTIER DOCUMENTÉS PAR LE CONTRAT OPENAPI
# =====================================================================
class FormationsListHandler(tornado.web.RequestHandler):
    def get(self):
        min_jours = int(self.get_query_argument("min_jours", "1"))
        resultat = [f for f in FORMATIONS if f["duree_jours"] >= min_jours]
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(resultat, ensure_ascii=False))


class FormationDetailHandler(tornado.web.RequestHandler):
    def get(self, id_str):
        fid = int(id_str)
        for f in FORMATIONS:
            if f["id"] == fid:
                self.write(f)
                return
        self.set_status(404)
        self.write({"erreur": f"Formation #{fid} introuvable"})


def make_app():
    return tornado.web.Application(
        [
            (r"/api/openapi.json", OpenApiSpecHandler),
            (r"/api/docs", SwaggerUiHandler),
            (r"/api/v1/formations", FormationsListHandler),
            (r"/api/v1/formations/([0-9]+)", FormationDetailHandler),
        ],
        template_path=os.path.join(RACINE_PROJET, "templates"),
    )


async def _demo():
    app = make_app()
    sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    client = tornado.httpclient.AsyncHTTPClient()

    resp_spec = await client.fetch(f"http://127.0.0.1:{port}/api/openapi.json")
    spec = tornado.escape.json_decode(resp_spec.body)
    print("=== CONTRAT OPENAPI 3.0 GÉNÉRÉ AVEC SUCCÈS PAR TORNADO ===")
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
    server.stop()


if __name__ == "__main__":
    asyncio.run(_demo())
