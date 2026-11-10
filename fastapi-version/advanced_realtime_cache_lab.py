"""
================================================================================
MANUEL & LABORATOIRE AVANCÉ — ÉDITION FASTAPI (ASGI, WebSockets & BackgroundTasks)
================================================================================
Ce script autonome de référence illustre 5 briques d'architecture de production
sous FastAPI (ASGI) :
  1. Middleware HTTP ASGI (`@app.middleware("http")`) :
     Injection d'un identifiant de corrélation `X-Request-ID` et mesure `X-Process-Time-Ms`.
  2. Cache HTTP & Concurrence Optimiste (`ETag` SHA-256) :
     - Lecture conditionnelle `If-None-Match` -> `HTTP 304 Not Modified`
     - Écriture protégée `If-Match` -> `HTTP 412 Precondition Failed`
  3. Tâches d'Arrière-Plan Natives (`BackgroundTasks` -> `HTTP 202 Accepted`) :
     Exécution asynchrone après l'envoi de la réponse HTTP sans bloquer le client.
  4. Upload `UploadFile` en Streaming (`SpooledTemporaryFile`) + Magic Bytes :
     Lecture par blocs de 64 Ko (`await fichier.read(65536)`) et protection Path Traversal.
  5. Temps Réel Bidirectionnel (`@app.websocket("/ws/live")`) & Unidirectionnel (`StreamingResponse` SSE).
================================================================================
"""

import asyncio
import hashlib
import json
import os
import re
import socket as _sock
import sys
import time
import uuid
from typing import Optional
from fastapi import BackgroundTasks, FastAPI, File, Header, HTTPException, Request, Response, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI(title="ISGP — Manuel Avancé Temps Réel, Streaming & Cache (FastAPI)")

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 Mo max
JOBS_STORE = {}

DOCUMENT_CATALOGUE = {
    "id": 1,
    "titre": "Référentiel Architecture API ISGP",
    "version_metier": 1,
    "salle": "Amphithéâtre Alger",
    "places": 40,
}


def calculer_etag(ressource: dict) -> str:
    canonique = json.dumps(ressource, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return f'"{hashlib.sha256(canonique).hexdigest()[:16]}"'


def nettoyer_nom_fichier(nom: str) -> str:
    base = os.path.basename(nom.replace("\\", "/"))
    propre = re.sub(r"[^A-Za-z0-9._-]", "_", base).strip("._")
    return propre or "document.bin"


# ==============================================================================
# 1. MIDDLEWARE ASGI : X-Request-ID & X-Process-Time-Ms
# ==============================================================================
@app.middleware("http")
async def middleware_observabilite(request: Request, call_next):
    debut = time.perf_counter()
    req_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:10]}"
    response = await call_next(request)
    duree_ms = round((time.perf_counter() - debut) * 1000.0, 2)
    response.headers["X-Request-ID"] = req_id
    response.headers["X-Process-Time-Ms"] = str(duree_ms)
    return response


# ==============================================================================
# 2. CACHE HTTP CONDITIONNEL (ETag -> 304) & CONCURRENCE OPTIMISTE (If-Match -> 412)
# ==============================================================================
class CatalogueUpdate(BaseModel):
    salle: Optional[str] = None
    places: Optional[int] = None


@app.get("/api/lab/catalogue")
async def lire_catalogue_avec_etag(
    response: Response,
    if_none_match: Optional[str] = Header(default=None),
):
    etag_actuel = calculer_etag(DOCUMENT_CATALOGUE)
    if if_none_match == etag_actuel:
        return Response(
            status_code=304,
            headers={"ETag": etag_actuel, "Cache-Control": "private, max-age=30, must-revalidate"},
        )
    response.headers["ETag"] = etag_actuel
    response.headers["Cache-Control"] = "private, max-age=30, must-revalidate"
    return DOCUMENT_CATALOGUE


@app.put("/api/lab/catalogue")
async def modifier_catalogue_avec_if_match(
    payload: CatalogueUpdate,
    response: Response,
    if_match: Optional[str] = Header(default=None),
):
    etag_actuel = calculer_etag(DOCUMENT_CATALOGUE)
    if not if_match:
        raise HTTPException(
            status_code=428,
            detail={"erreur": "En-tête If-Match obligatoire.", "etag_actuel": etag_actuel},
        )
    if if_match != etag_actuel:
        raise HTTPException(
            status_code=412,
            detail={
                "erreur": "Conflit de version (412 Precondition Failed) : ressource modifiée par un tiers !",
                "votre_if_match_obsolete": if_match,
                "etag_actuel_serveur": etag_actuel,
            },
        )

    if payload.salle is not None:
        DOCUMENT_CATALOGUE["salle"] = payload.salle
    if payload.places is not None:
        DOCUMENT_CATALOGUE["places"] = payload.places
    DOCUMENT_CATALOGUE["version_metier"] += 1

    response.headers["ETag"] = calculer_etag(DOCUMENT_CATALOGUE)
    return DOCUMENT_CATALOGUE


# ==============================================================================
# 3. TÂCHES D'ARRIÈRE-PLAN NATIVES FASTAPI (BackgroundTasks -> 202 Accepted)
# ==============================================================================
class RapportRequest(BaseModel):
    sujet: str = "Audit Annuel APIs"


async def _generer_rapport_async(job_id: str, sujet: str):
    JOBS_STORE[job_id]["statut"] = "RUNNING"
    await asyncio.sleep(0.15)
    JOBS_STORE[job_id]["statut"] = "COMPLETED"
    JOBS_STORE[job_id]["resultat"] = {
        "fichier_genere": f"rapport_{job_id}.pdf",
        "sujet": sujet,
        "taille_octets": 148920,
    }


@app.post("/api/lab/rapports", status_code=202)
async def lancer_generation_rapport(
    payload: RapportRequest,
    background_tasks: BackgroundTasks,
    response: Response,
):
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    JOBS_STORE[job_id] = {"job_id": job_id, "statut": "PENDING", "resultat": None}
    background_tasks.add_task(_generer_rapport_async, job_id, payload.sujet)
    response.headers["Location"] = f"/api/lab/jobs/{job_id}"
    return {
        "message": "Traitement accepté et confié à BackgroundTasks (202 Accepted).",
        "job_id": job_id,
        "status_url": f"/api/lab/jobs/{job_id}",
    }


@app.get("/api/lab/jobs/{job_id}")
async def consulter_etat_job(job_id: str):
    if job_id not in JOBS_STORE:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return JOBS_STORE[job_id]


# ==============================================================================
# 4. UPLOAD MULTIPART EN STREAMING ASYNCHRONE (UploadFile + Magic Bytes)
# ==============================================================================
SIGNATURES_MAGIQUES = {
    b"%PDF-": "application/pdf",
    b"\x89PNG\r\n\x1a\n": "image/png",
}


@app.post("/api/lab/upload", status_code=201)
async def televerser_document(document: UploadFile = File(...)):
    nom_brut = document.filename or "inconnu.bin"
    nom_nettoye = nettoyer_nom_fichier(nom_brut)

    premiers_octets = await document.read(16)
    taille_totale = len(premiers_octets)
    hasher = hashlib.sha256(premiers_octets)

    while chunk := await document.read(65536):
        taille_totale += len(chunk)
        if taille_totale > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Fichier supérieur à la limite autorisée (2 Mo).")
        hasher.update(chunk)

    mime_reel = next((m for sig, m in SIGNATURES_MAGIQUES.items() if premiers_octets.startswith(sig)), None)
    if mime_reel is None:
        raise HTTPException(
            status_code=415,
            detail={
                "erreur": "Signature Magic Bytes invalide : seuls PDF (%PDF-) et PNG sont autorisés.",
                "entete_hex_recu": premiers_octets[:8].hex(),
            },
        )

    return {
        "statut": "Fichier validé par lecture asynchrone UploadFile",
        "nom_original": nom_brut,
        "nom_securise": f"{uuid.uuid4().hex[:8]}_{nom_nettoye}",
        "mime_detecte_magic_bytes": mime_reel,
        "taille_octets": taille_totale,
        "sha256": hasher.hexdigest(),
    }


# ==============================================================================
# 5. TEMPS RÉEL : SSE (StreamingResponse) & WEBSOCKET BIDIRECTIONNEL (RFC 6455)
# ==============================================================================
@app.get("/api/lab/sse")
async def flux_temps_reel_sse():
    async def generer_evenements():
        for etape in range(1, 4):
            payload = json.dumps({
                "etape": etape,
                "serveur": "FastAPI ASGI StreamingResponse",
                "horodatage": round(time.time(), 3),
            })
            yield f"id: evt-{etape}\nevent: progression\ndata: {payload}\n\n"
            await asyncio.sleep(0.05)

    return StreamingResponse(
        generer_evenements(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.websocket("/ws/live")
async def canal_websocket_bidirectionnel(websocket: WebSocket):
    """Poignée de main HTTP 101 Switching Protocols puis échange full-duplex."""
    await websocket.accept()
    await websocket.send_json({"type": "handshake", "serveur": "FastAPI ASGI WebSocket", "statut": "101 Switching Protocols"})
    try:
        while True:
            message_client = await websocket.receive_text()
            await websocket.send_json({
                "type": "echo_temps_reel",
                "recu": message_client,
                "horodatage": round(time.time(), 3),
            })
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    print("=== DÉMONSTRATION AVANCÉE SOUS FASTAPI (MIDDLEWARE, ETAG 304/412, 202, UPLOAD, SSE & WEBSOCKET) ===")
    client = TestClient(app)

    r1 = client.get("/api/lab/catalogue", headers={"X-Request-ID": "trace-isgp-001"})
    etag_v1 = r1.headers["etag"]
    print(f"1. GET /api/lab/catalogue        -> HTTP {r1.status_code} | ETag={etag_v1} | X-Request-ID={r1.headers['x-request-id']} ({r1.headers['x-process-time-ms']} ms)")

    r_304 = client.get("/api/lab/catalogue", headers={"If-None-Match": etag_v1})
    print(f"2. GET avec If-None-Match        -> HTTP {r_304.status_code} (Corps={len(r_304.content)} octets — bande passante économisée !)")

    r_412 = client.put("/api/lab/catalogue", headers={"If-Match": '"etag-obsolete"'}, json={"places": 55})
    print(f"3. PUT avec If-Match obsolète    -> HTTP {r_412.status_code} (Écrasement concurrent bloqué !)")

    r_202 = client.post("/api/lab/rapports", json={"sujet": "Bilan Sécurité API"})
    job_url = r_202.headers["location"]
    r_job = client.get(job_url).json()
    print(f"4. POST /api/lab/rapports        -> HTTP {r_202.status_code} | BackgroundTasks {job_url} -> statut={r_job['statut']}")

    r_up = client.post(
        "/api/lab/upload",
        files={"document": ("../../secret/support_cours.pdf", b"%PDF-1.7\nContenu binaire ISGP...", "application/pdf")},
    )
    print(f"5. POST /api/lab/upload (PDF)    -> HTTP {r_up.status_code} | Nom nettoyé={r_up.json()['nom_securise']}")

    with client.websocket_connect("/ws/live") as ws:
        bienvenue = ws.receive_json()
        ws.send_text("Ping temps réel depuis le client !")
        echo = ws.receive_json()
        print(f"6. WebSocket /ws/live (101)      -> Reçu: '{echo['recu']}' via {bienvenue['serveur']}")

    if "--once" not in sys.argv:
        import uvicorn
        port = int(os.environ.get("PORT", 8001))
        with _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM) as _s:
            if _s.connect_ex(("127.0.0.1", port)) == 0:
                _s2 = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
                _s2.bind(("127.0.0.1", 0))
                port = _s2.getsockname()[1]
                _s2.close()
        print("\n" + "=" * 76)
        print(f"[BOUCLE ASGI UVICORN / FASTAPI ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Catalogue ETag : http://127.0.0.1:{port}/api/lab/catalogue")
        print(f"  -> Flux SSE Live  : http://127.0.0.1:{port}/api/lab/sse")
        print(f"  -> WebSocket Live : ws://127.0.0.1:{port}/ws/live")
        print(f"  -> Swagger UI     : http://127.0.0.1:{port}/docs")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement le serveur ASGI.")
        print("=" * 76)
        uvicorn.run(app, host="0.0.0.0", port=port)
