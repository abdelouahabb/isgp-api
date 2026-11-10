"""
================================================================================
MANUEL & LABORATOIRE AVANCÉ — ÉDITION TORNADO (IOLoop, WebSocketHandler & Streaming)
================================================================================
Ce script autonome de référence illustre les 5 briques où l'architecture
non-bloquante de Tornado (`IOLoop`) exprime toute sa puissance :
  1. Hooks d'Observabilité (`prepare()` / `on_finish()` dans un `BaseObservedHandler`) :
     Corrélation `X-Request-ID` et chronométrage `X-Process-Time-Ms`.
  2. Cache HTTP & Concurrence Optimiste (`ETag` SHA-256) :
     - Lecture conditionnelle `If-None-Match` -> `HTTP 304 Not Modified`
     - Écriture protégée `If-Match` -> `HTTP 412 Precondition Failed`
  3. Tâches d'Arrière-Plan sans Thread (`IOLoop.current().spawn_callback`) :
     Planification immédiate d'une coroutine après `202 Accepted` sur l'IOLoop.
  4. Upload en Streaming Pur Zéro-RAM (`@tornado.web.stream_request_body`) :
     Traitement bloc par bloc dans `data_received(chunk)` sans charger le corps en RAM !
  5. Temps Réel C10K : `tornado.websocket.WebSocketHandler` (`/ws/live`) + SSE (`self.flush()`).
================================================================================
"""

import asyncio
import hashlib
import json
import os
import re
import sys
import time
import uuid
import tornado.escape
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.web
import tornado.websocket

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # Plafond 2 Mo configuré sur HTTPServer(max_body_size=...)
JOBS_STORE = {}
ACTIVE_WS_CLIENTS = set()

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


# ==============================================================================
# 1. CLASSE DE BASE D'OBSERVABILITÉ : X-Request-ID & X-Process-Time-Ms
# ==============================================================================
class BaseObservedHandler(tornado.web.RequestHandler):
    """Injecte automatiquement X-Request-ID et mesure le temps de traitement."""

    def prepare(self):
        self._t0 = time.perf_counter()
        self.request_id = self.request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:10]}"
        self.set_header("X-Request-ID", self.request_id)
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def write_observed_json(self, payload: dict, status_code: int = 200):
        duree_ms = round((time.perf_counter() - self._t0) * 1000.0, 2)
        self.set_header("X-Process-Time-Ms", str(duree_ms))
        self.set_status(status_code)
        self.write(json.dumps(payload, ensure_ascii=False))


# ==============================================================================
# 2. CACHE HTTP (ETag -> 304) & CONCURRENCE OPTIMISTE (If-Match -> 412)
# ==============================================================================
class CatalogueEtagHandler(BaseObservedHandler):
    # Désactive compute_etag automatique de Tornado pour illustrer le contrôle explicite :
    def compute_etag(self):
        return None

    async def get(self):
        etag_actuel = calculer_etag(DOCUMENT_CATALOGUE)
        self.set_header("ETag", etag_actuel)
        self.set_header("Cache-Control", "private, max-age=30, must-revalidate")

        if self.request.headers.get("If-None-Match") == etag_actuel:
            duree_ms = round((time.perf_counter() - self._t0) * 1000.0, 2)
            self.set_header("X-Process-Time-Ms", str(duree_ms))
            self.set_status(304)
            return

        self.write_observed_json(DOCUMENT_CATALOGUE, 200)

    async def put(self):
        etag_actuel = calculer_etag(DOCUMENT_CATALOGUE)
        if_match = self.request.headers.get("If-Match")

        if not if_match:
            self.write_observed_json({"erreur": "En-tête If-Match obligatoire.", "etag_actuel": etag_actuel}, 428)
            return

        if if_match != etag_actuel:
            self.write_observed_json({
                "erreur": "Conflit de version (412 Precondition Failed) : ressource modifiée par un tiers !",
                "votre_if_match_obsolete": if_match,
                "etag_actuel_serveur": etag_actuel,
            }, 412)
            return

        corps = tornado.escape.json_decode(self.request.body or b"{}")
        if "salle" in corps:
            DOCUMENT_CATALOGUE["salle"] = str(corps["salle"])
        if "places" in corps:
            DOCUMENT_CATALOGUE["places"] = int(corps["places"])
        DOCUMENT_CATALOGUE["version_metier"] += 1

        self.set_header("ETag", calculer_etag(DOCUMENT_CATALOGUE))
        self.write_observed_json(DOCUMENT_CATALOGUE, 200)


# ==============================================================================
# 3. TÂCHE D'ARRIÈRE-PLAN SUR L'IOLOOP (spawn_callback -> 202 Accepted)
# ==============================================================================
async def _generer_rapport_ioloop(job_id: str, sujet: str):
    JOBS_STORE[job_id]["statut"] = "RUNNING"
    await asyncio.sleep(0.15)  # Rend la main à l'IOLoop pendant l'attente !
    JOBS_STORE[job_id]["statut"] = "COMPLETED"
    JOBS_STORE[job_id]["resultat"] = {
        "fichier_genere": f"rapport_{job_id}.pdf",
        "sujet": sujet,
        "taille_octets": 148920,
    }


class RapportsAsyncJobHandler(BaseObservedHandler):
    async def post(self):
        corps = tornado.escape.json_decode(self.request.body or b"{}")
        sujet = str(corps.get("sujet", "Audit Annuel APIs"))
        job_id = f"job-{uuid.uuid4().hex[:8]}"
        JOBS_STORE[job_id] = {"job_id": job_id, "statut": "PENDING", "resultat": None}

        # Fire-and-forget natif Tornado : planifie la coroutine sur l'IOLoop sans bloquer la réponse
        tornado.ioloop.IOLoop.current().spawn_callback(_generer_rapport_ioloop, job_id, sujet)

        self.set_header("Location", f"/api/lab/jobs/{job_id}")
        self.write_observed_json({
            "message": "Traitement planifié sur l'IOLoop via spawn_callback (202 Accepted).",
            "job_id": job_id,
            "status_url": f"/api/lab/jobs/{job_id}",
        }, 202)


class JobStatusHandler(BaseObservedHandler):
    async def get(self, job_id: str):
        job = JOBS_STORE.get(job_id)
        if not job:
            self.write_observed_json({"erreur": "Job introuvable"}, 404)
            return
        self.write_observed_json(job, 200)


# ==============================================================================
# 4. STREAMING D'ENTRÉE ZÉRO-RAM (@tornado.web.stream_request_body)
# ==============================================================================
@tornado.web.stream_request_body
class StreamUploadHandler(BaseObservedHandler):
    """
    Spécialité majeure de Tornado : le corps n'est PAS stocké dans self.request.body !
    Chaque paquet TCP arrive à la volée dans data_received(chunk), permettant de
    hacher ou d'écrire sur disque un fichier de plusieurs Go avec < 64 Ko de RAM.
    """

    def prepare(self):
        super().prepare()
        self._hasher = hashlib.sha256()
        self._octets_recus = 0
        self._entete_binaire = bytearray()
        self._nb_chunks = 0

    def data_received(self, chunk: bytes):
        self._nb_chunks += 1
        self._octets_recus += len(chunk)
        if len(self._entete_binaire) < 16:
            manquant = 16 - len(self._entete_binaire)
            self._entete_binaire.extend(chunk[:manquant])
        self._hasher.update(chunk)

    async def post(self):
        nom_brut = self.request.headers.get("X-Filename", "document.pdf")
        nom_propre = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(nom_brut.replace("\\", "/"))) or "doc.pdf"

        est_pdf = bytes(self._entete_binaire).startswith(b"%PDF-")
        est_png = bytes(self._entete_binaire).startswith(b"\x89PNG\r\n\x1a\n")
        if not (est_pdf or est_png):
            self.write_observed_json({
                "erreur": "Signature binaire (Magic Bytes) rejetée : flux %PDF- ou PNG attendu.",
                "entete_hex_recu": bytes(self._entete_binaire[:8]).hex(),
            }, 415)
            return

        self.write_observed_json({
            "statut": "Flux binaire traité à la volée via @stream_request_body (Zéro tampon RAM)",
            "nom_securise": f"{uuid.uuid4().hex[:8]}_{nom_propre}",
            "mime_detecte_magic_bytes": "application/pdf" if est_pdf else "image/png",
            "taille_octets": self._octets_recus,
            "chunks_tcp_traites": self._nb_chunks,
            "sha256": self._hasher.hexdigest(),
        }, 201)


# ==============================================================================
# 5. TEMPS RÉEL : SSE (self.flush) & WEBSOCKETHANDLER NATIF (RFC 6455)
# ==============================================================================
class SseStreamHandler(tornado.web.RequestHandler):
    async def get(self):
        self.set_header("Content-Type", "text/event-stream; charset=UTF-8")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("X-Accel-Buffering", "no")
        for etape in range(1, 4):
            payload = json.dumps({
                "etape": etape,
                "serveur": "Tornado IOLoop self.flush()",
                "horodatage": round(time.time(), 3),
            })
            self.write(f"id: evt-{etape}\nevent: progression\ndata: {payload}\n\n")
            await self.flush()  # Pousse immédiatement le paquet TCP sans fermer la connexion !
            await asyncio.sleep(0.05)


class LiveWebSocketHandler(tornado.websocket.WebSocketHandler):
    """Handler WebSocket natif Tornado (conçu pour des dizaines de milliers de sockets)."""

    def check_origin(self, origin: str) -> bool:
        return True  # En production : vérifier le domaine exact dans une liste blanche !

    def open(self):
        ACTIVE_WS_CLIENTS.add(self)
        self.write_message(json.dumps({
            "type": "handshake",
            "serveur": "Tornado WebSocketHandler (IOLoop)",
            "clients_actifs": len(ACTIVE_WS_CLIENTS),
            "statut": "101 Switching Protocols",
        }))

    def on_message(self, message: str):
        self.write_message(json.dumps({
            "type": "echo_temps_reel",
            "recu": message,
            "horodatage": round(time.time(), 3),
        }))

    def on_close(self):
        ACTIVE_WS_CLIENTS.discard(self)


def make_app():
    return tornado.web.Application([
        (r"/api/lab/catalogue", CatalogueEtagHandler),
        (r"/api/lab/rapports", RapportsAsyncJobHandler),
        (r"/api/lab/jobs/([^/]+)", JobStatusHandler),
        (r"/api/lab/upload", StreamUploadHandler),
        (r"/api/lab/sse", SseStreamHandler),
        (r"/ws/live", LiveWebSocketHandler),
    ])


async def executer_laboratoire_avance():
    app = make_app()
    app.settings["log_function"] = lambda h: print(
        f"[IOLOOP TORNADO] HTTP {h.get_status()} | {h.request.method} {h.request.uri} ({h.request.remote_ip}) | {round(1000.0 * h.request.request_time(), 2)} ms"
    )
    bind_port = int(os.environ.get("PORT", 8889))
    try:
        sockets = tornado.netutil.bind_sockets(bind_port, "127.0.0.1")
    except OSError:
        sockets = tornado.netutil.bind_sockets(0, "127.0.0.1")
    port = sockets[0].getsockname()[1]

    server = tornado.httpserver.HTTPServer(app, max_body_size=MAX_UPLOAD_BYTES)
    server.add_sockets(sockets)

    client = tornado.httpclient.AsyncHTTPClient()
    base = f"http://127.0.0.1:{port}"
    print("=== DÉMONSTRATION AVANCÉE SOUS TORNADO (ETAG 304/412, SPAWN_CALLBACK 202, STREAM UPLOAD, SSE & WS) ===")

    # 1. GET + ETag + X-Request-ID
    r1 = await client.fetch(f"{base}/api/lab/catalogue", headers={"X-Request-ID": "trace-isgp-001"})
    etag_v1 = r1.headers["ETag"]
    print(f"1. GET /api/lab/catalogue        -> HTTP {r1.code} | ETag={etag_v1} | X-Request-ID={r1.headers['X-Request-ID']}")

    # 2. If-None-Match -> 304 Not Modified
    r_304 = await client.fetch(f"{base}/api/lab/catalogue", headers={"If-None-Match": etag_v1}, raise_error=False)
    print(f"2. GET avec If-None-Match        -> HTTP {r_304.code} (Corps={len(r_304.body)} octets — bande passante économisée !)")

    # 3. If-Match obsolète -> 412 Precondition Failed
    r_412 = await client.fetch(
        f"{base}/api/lab/catalogue",
        method="PUT",
        headers={"If-Match": '"etag-obsolete"', "Content-Type": "application/json"},
        body=json.dumps({"places": 55}),
        raise_error=False,
    )
    print(f"3. PUT avec If-Match obsolète    -> HTTP {r_412.code} (Écrasement concurrent bloqué !)")

    # 4. 202 Accepted via IOLoop.spawn_callback
    r_202 = await client.fetch(
        f"{base}/api/lab/rapports",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=json.dumps({"sujet": "Bilan Sécurité API"}),
    )
    job_url = r_202.headers["Location"]
    await asyncio.sleep(0.2)
    r_job = await client.fetch(f"{base}{job_url}")
    print(f"4. POST /api/lab/rapports        -> HTTP {r_202.code} | spawn_callback {job_url} -> statut={tornado.escape.json_decode(r_job.body)['statut']}")

    # 5. @stream_request_body Upload
    r_up = await client.fetch(
        f"{base}/api/lab/upload",
        method="POST",
        headers={"X-Filename": "../../secret/support_cours.pdf", "Content-Type": "application/pdf"},
        body=b"%PDF-1.7\nFlux binaire traite sans tampon RAM...",
    )
    print(f"5. POST /api/lab/upload (Stream) -> HTTP {r_up.code} | Nom nettoyé={tornado.escape.json_decode(r_up.body)['nom_securise']}")

    # 6. Client WebSocket natif Tornado (ws://)
    ws = await tornado.websocket.websocket_connect(f"ws://127.0.0.1:{port}/ws/live")
    msg_accueil = json.loads(await ws.read_message())
    ws.write_message("Ping temps réel sur l'IOLoop !")
    msg_echo = json.loads(await ws.read_message())
    ws.close()
    print(f"6. WebSocket /ws/live (101)      -> Reçu: '{msg_echo['recu']}' via {msg_accueil['serveur']}")

    if "--once" in sys.argv:
        server.stop()
    else:
        print("\n" + "=" * 76)
        print(f"[BOUCLE IOLOOP TORNADO ACTIVE] Serveur en écoute sur http://127.0.0.1:{port}")
        print(f"  -> Catalogue ETag : http://127.0.0.1:{port}/api/lab/catalogue")
        print(f"  -> Flux SSE Live  : http://127.0.0.1:{port}/api/lab/sse")
        print(f"  -> WebSocket Live : ws://127.0.0.1:{port}/ws/live")
        print("  -> Appuyez sur Ctrl+C pour arrêter proprement la boucle IOLoop.")
        print("=" * 76)
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(executer_laboratoire_avance())
    except KeyboardInterrupt:
        print("\n[IOLOOP TORNADO] Arrêt propre demandé par l'utilisateur (Ctrl+C).")
