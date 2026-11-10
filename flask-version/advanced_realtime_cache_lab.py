"""
================================================================================
MANUEL & LABORATOIRE AVANCÉ — ÉDITION FLASK (WSGI)
Temps Réel (SSE), Upload Multipart Sécurisé, Tâches 202 Accepted & Cache ETag
================================================================================
Ce script autonome de référence illustre 5 briques d'architecture de production
sous Flask (WSGI) sans aucune dépendance externe supplémentaire :
  1. Middleware d'Observabilité (`@app.before_request` / `@app.after_request`) :
     Injection d'un identifiant de corrélation `X-Request-ID` et mesure `X-Process-Time-Ms`.
  2. Cache HTTP & Concurrence Optimiste (`ETag` SHA-256) :
     - Lecture conditionnelle `If-None-Match` -> `HTTP 304 Not Modified` (0 octet transféré)
     - Écriture protégée `If-Match` -> `HTTP 412 Precondition Failed` (anti Lost-Update)
  3. Tâches d'Arrière-Plan (`HTTP 202 Accepted` + `ThreadPoolExecutor`) :
     Délégation non-bloquante d'un traitement long avec URL de suivi `/api/lab/jobs/<id>`.
  4. Upload `multipart/form-data` sécurisé :
     Plafond `MAX_CONTENT_LENGTH` (`413`), nettoyage `secure_filename` et vérification Magic Bytes.
  5. Flux Temps Réel `Server-Sent Events` (`text/event-stream`) :
     Générateur Python `yield` compatible WSGI natif.
================================================================================
"""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import socket as _sock
import sys
import time
import uuid
from flask import Flask, Response, g, jsonify, request, stream_with_context
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Protection mémoire anti-DoS : rejette automatiquement tout corps > 2 Mo avec HTTP 413
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

# Pool de threads dédié aux tâches d'arrière-plan (évite de bloquer le worker HTTP WSGI)
BACKGROUND_POOL = ThreadPoolExecutor(max_workers=2)
JOBS_STORE = {}

# Ressource métier en mémoire pour démontrer ETag (304) et Verrouillage Optimiste (412)
DOCUMENT_CATALOGUE = {
    "id": 1,
    "titre": "Référentiel Architecture API ISGP",
    "version_metier": 1,
    "salle": "Amphithéâtre Alger",
    " places": 40,
}
DOCUMENT_CATALOGUE.pop(" places", None)
DOCUMENT_CATALOGUE["places"] = 40


def calculer_etag(ressource: dict) -> str:
    """Calcule une empreinte déterministe SHA-256 courte encadrée de guillemets (RFC 9110)."""
    canonique = json.dumps(ressource, sort_keys=True, ensure_ascii=False).encode("utf-8")
    digest = hashlib.sha256(canonique).hexdigest()[:16]
    return f'"{digest}"'


# ==============================================================================
# 1. MIDDLEWARE D'OBSERVABILITÉ : CORRÉLATION X-Request-ID & CHRONOMÉTRAGE
# ==============================================================================
@app.before_request
def tracer_debut_requete():
    """S'exécute AVANT chaque route : récupère ou génère un X-Request-ID unique."""
    g.start_perf = time.perf_counter()
    g.request_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:10]}"


@app.after_request
def injecter_entetes_observabilite(response):
    """S'exécute APRÈS chaque route : ajoute la durée exacte et l'ID de corrélation."""
    duree_ms = round((time.perf_counter() - getattr(g, "start_perf", time.perf_counter())) * 1000.0, 2)
    response.headers["X-Request-ID"] = getattr(g, "request_id", "inconnu")
    response.headers["X-Process-Time-Ms"] = str(duree_ms)
    return response


# ==============================================================================
# 2. CACHE HTTP CONDITIONNEL (ETag -> 304) & CONCURRENCE OPTIMISTE (If-Match -> 412)
# ==============================================================================
@app.route("/api/lab/catalogue", methods=["GET"])
def lire_catalogue_avec_etag():
    etag_actuel = calculer_etag(DOCUMENT_CATALOGUE)
    etag_client = request.headers.get("If-None-Match")

    # Si le client possède déjà exactement cette version en cache -> 304 sans corps !
    if etag_client == etag_actuel:
        resp_304 = Response(status=304)
        resp_304.headers["ETag"] = etag_actuel
        resp_304.headers["Cache-Control"] = "private, max-age=30, must-revalidate"
        return resp_304

    resp = jsonify(DOCUMENT_CATALOGUE)
    resp.headers["ETag"] = etag_actuel
    resp.headers["Cache-Control"] = "private, max-age=30, must-revalidate"
    return resp, 200


@app.route("/api/lab/catalogue", methods=["PUT"])
def modifier_catalogue_avec_if_match():
    """Empêche l'écrasement silencieux (Lost Update) grâce à l'en-tête If-Match."""
    etag_actuel = calculer_etag(DOCUMENT_CATALOGUE)
    if_match = request.headers.get("If-Match")

    if not if_match:
        return jsonify({
            "erreur": "En-tête If-Match obligatoire pour modifier cette ressource critique.",
            "etag_actuel": etag_actuel,
        }), 428  # 428 Precondition Required

    if if_match != etag_actuel:
        return jsonify({
            "erreur": "Conflit de version (412 Precondition Failed) : un autre utilisateur a modifié la ressource entre-temps !",
            "votre_if_match_obsolete": if_match,
            "etag_actuel_serveur": etag_actuel,
        }), 412

    corps = request.get_json(silent=True) or {}
    if "salle" in corps:
        DOCUMENT_CATALOGUE["salle"] = str(corps["salle"])
    if "places" in corps:
        DOCUMENT_CATALOGUE["places"] = int(corps["places"])
    DOCUMENT_CATALOGUE["version_metier"] += 1

    nouvel_etag = calculer_etag(DOCUMENT_CATALOGUE)
    resp = jsonify(DOCUMENT_CATALOGUE)
    resp.headers["ETag"] = nouvel_etag
    return resp, 200


# ==============================================================================
# 3. TÂCHE D'ARRIÈRE-PLAN ASYNCHRONE (HTTP 202 ACCEPTED + POLLING D'ÉTAT)
# ==============================================================================
def _generer_rapport_lourd(job_id: str, sujet: str):
    """Exécuté en arrière-plan dans BACKGROUND_POOL pendant que le client a déjà reçu 202."""
    JOBS_STORE[job_id]["statut"] = "RUNNING"
    time.sleep(0.25)  # Simulation d'export PDF / agrégation analytique
    JOBS_STORE[job_id]["statut"] = "COMPLETED"
    JOBS_STORE[job_id]["resultat"] = {
        "fichier_genere": f"rapport_{job_id}.pdf",
        "sujet": sujet,
        "taille_octets": 148920,
    }


@app.route("/api/lab/rapports", methods=["POST"])
def lancer_generation_rapport():
    corps = request.get_json(silent=True) or {}
    sujet = str(corps.get("sujet", "Audit Annuel APIs")).strip()
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    JOBS_STORE[job_id] = {"job_id": job_id, "statut": "PENDING", "resultat": None}

    # Soumission au pool sans bloquer la réponse HTTP :
    BACKGROUND_POOL.submit(_generer_rapport_lourd, job_id, sujet)

    resp = jsonify({
        "message": "Traitement accepté et planifié en arrière-plan (202 Accepted).",
        "job_id": job_id,
        "status_url": f"/api/lab/jobs/{job_id}",
    })
    resp.headers["Location"] = f"/api/lab/jobs/{job_id}"
    return resp, 202


@app.route("/api/lab/jobs/<job_id>", methods=["GET"])
def consulter_etat_job(job_id: str):
    job = JOBS_STORE.get(job_id)
    if not job:
        return jsonify({"erreur": "Job introuvable"}), 404
    return jsonify(job), 200


# ==============================================================================
# 4. UPLOAD MULTIPART SÉCURISÉ (secure_filename + VÉRIFICATION MAGIC BYTES)
# ==============================================================================
SIGNATURES_MAGIQUES = {
    b"%PDF-": "application/pdf",
    b"\x89PNG\r\n\x1a\n": "image/png",
}


@app.route("/api/lab/upload", methods=["POST"])
def televerser_document():
    if "document" not in request.files:
        return jsonify({"erreur": "Champ multipart 'document' manquant."}), 400

    fichier = request.files["document"]
    nom_brut = fichier.filename or "inconnu.bin"
    # Neutralisation des attaques Path Traversal (ex: "../../etc/passwd" -> "etc_passwd")
    nom_nettoye = secure_filename(nom_brut)

    # Lecture par morceaux (streaming) sans charger un énorme fichier d'un bloc
    premiers_octets = fichier.stream.read(16)
    taille_totale = len(premiers_octets)
    hasher = hashlib.sha256(premiers_octets)
    while chunk := fichier.stream.read(65536):
        taille_totale += len(chunk)
        hasher.update(chunk)

    mime_reel = None
    for sig, mime_nom in SIGNATURES_MAGIQUES.items():
        if premiers_octets.startswith(sig):
            mime_reel = mime_nom
            break

    if mime_reel is None:
        return jsonify({
            "erreur": "Signature binaire (Magic Bytes) rejetée : seuls les vrais fichiers PDF (%PDF-) ou PNG sont acceptés.",
            "nom_nettoye": nom_nettoye,
            "entete_hex_recu": premiers_octets[:8].hex(),
        }), 415  # 415 Unsupported Media Type

    return jsonify({
        "statut": "Fichier validé par lecture en flux (chunked stream)",
        "nom_original": nom_brut,
        "nom_securise": f"{uuid.uuid4().hex[:8]}_{nom_nettoye}",
        "mime_detecte_magic_bytes": mime_reel,
        "taille_octets": taille_totale,
        "sha256": hasher.hexdigest(),
    }), 201


# ==============================================================================
# 5. TEMPS RÉEL SOUS FLASK WSGI : SERVER-SENT EVENTS (text/event-stream)
# ==============================================================================
@app.route("/api/lab/sse", methods=["GET"])
def flux_temps_reel_sse():
    """Générateur SSE unidirectionnel compatible avec le modèle synchrone WSGI."""
    def generer_evenements():
        for etape in range(1, 4):
            payload = json.dumps({
                "etape": etape,
                "serveur": "Flask WSGI Generator",
                "horodatage": round(time.time(), 3),
            })
            # Format protocolaire W3C Server-Sent Events : event + id + data + double saut de ligne
            yield f"id: evt-{etape}\nevent: progression\ndata: {payload}\n\n"
            time.sleep(0.08)

    return Response(
        stream_with_context(generer_evenements()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    import io
    print("=== DÉMONSTRATION AVANCÉE SOUS FLASK (MIDDLEWARE, ETAG 304/412, JOB 202, UPLOAD & SSE) ===")
    with app.test_client() as client:
        # 1. Lecture initiale + récupération de l'ETag et du X-Request-ID
        r1 = client.get("/api/lab/catalogue", headers={"X-Request-ID": "trace-isgp-001"})
        etag_v1 = r1.headers["ETag"]
        print(f"1. GET /api/lab/catalogue        -> HTTP {r1.status_code} | ETag={etag_v1} | X-Request-ID={r1.headers['X-Request-ID']} ({r1.headers['X-Process-Time-Ms']} ms)")

        # 2. Revalidation conditionnelle If-None-Match -> 304 Not Modified
        r_304 = client.get("/api/lab/catalogue", headers={"If-None-Match": etag_v1})
        print(f"2. GET avec If-None-Match        -> HTTP {r_304.status_code} (Corps={len(r_304.data)} octets — bande passante économisée !)")

        # 3. Protection contre Lost Update (If-Match obsolète -> 412 Precondition Failed)
        r_412 = client.put("/api/lab/catalogue", headers={"If-Match": '"etag-obsolete"'}, json={"places": 55})
        print(f"3. PUT avec If-Match obsolète    -> HTTP {r_412.status_code} (Écrasement concurrent bloqué !)")

        # 4. Tâche d'arrière-plan 202 Accepted
        r_202 = client.post("/api/lab/rapports", json={"sujet": "Bilan Sécurité API"})
        job_url = r_202.headers["Location"]
        time.sleep(0.3)
        r_job = client.get(job_url).get_json()
        print(f"4. POST /api/lab/rapports        -> HTTP {r_202.status_code} | Polling {job_url} -> statut={r_job['statut']}")

        # 5. Upload Multipart avec vérification Magic Bytes (%PDF-) + Path Traversal neutralisé
        faux_pdf = io.BytesIO(b"%PDF-1.7\nContenu binaire du support ISGP...")
        r_up = client.post(
            "/api/lab/upload",
            data={"document": (faux_pdf, "../../secret/support_cours.pdf")},
            content_type="multipart/form-data",
        )
        print(f"5. POST /api/lab/upload (PDF)    -> HTTP {r_up.status_code} | Nom nettoyé={r_up.get_json()['nom_securise']}")

        # 6. Flux temps réel SSE
        r_sse = client.get("/api/lab/sse")
        nb_blocs = r_sse.get_data(as_text=True).strip().split("\n\n")
        print(f"6. GET /api/lab/sse              -> HTTP {r_sse.status_code} | {len(nb_blocs)} événements SSE reçus")

    if "--once" not in sys.argv:
        port = int(os.environ.get("PORT", 5001))
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
            if _s.connect_ex(("127.0.0.1", port)) == 0:
                _s2 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                _s2.bind(("127.0.0.1", 0))
                port = _s2.getsockname()[1]
                _s2.close()
        print("\n" + "=" * 76)
        print(f"[SERVEUR WSGI FLASK ACTIF] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Catalogue ETag : http://127.0.0.1:{port}/api/lab/catalogue")
        print(f"  -> Flux SSE Live  : http://127.0.0.1:{port}/api/lab/sse")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur Flask.")
        print("=" * 76)
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
