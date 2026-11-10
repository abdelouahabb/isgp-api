import hmac
import json
import os
import queue
import re
import signal
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime
from flask import Flask, Response, jsonify, make_response, redirect, render_template, render_template_string, request, send_from_directory, session
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

app = Flask(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VALID_FRAMEWORKS = ("flask", "fastapi", "tornado")


def _load_framework_bundle(fw: str) -> dict:
    fw_dir = os.path.join(ROOT_DIR, f"{fw}-version")
    loader_code = (
        "import json\n"
        "from data.curriculum import DAYS_CURRICULUM, STARTER_FILES_CONTENT\n"
        "from data.glossary import GLOSSARY_TERMS\n"
        "from data.quizzes import QUIZZES\n"
        "print(json.dumps({\n"
        "    'days': DAYS_CURRICULUM,\n"
        "    'starter_files': {str(k): v for k, v in STARTER_FILES_CONTENT.items()},\n"
        "    'glossary': GLOSSARY_TERMS,\n"
        "    'quizzes': {int(k) if str(k).isdigit() else k: v for k, v in QUIZZES.items()},\n"
        "}))\n"
    )
    out = subprocess.check_output([sys.executable, "-c", loader_code], cwd=fw_dir, text=True)
    return json.loads(out)


FRAMEWORK_BUNDLES = {fw: _load_framework_bundle(fw) for fw in VALID_FRAMEWORKS}


def _resolve_active_framework() -> str:
    fw = (
        request.args.get("framework")
        or request.headers.get("X-Active-Framework")
        or session.get("active_framework")
        or "flask"
    ).strip().lower()
    return fw if fw in VALID_FRAMEWORKS else "flask"

DB_PATH = os.path.join(os.path.dirname(__file__), "sandbox_isgp.db")
TEACHER_PIN = os.environ.get("TEACHER_PIN", "isgp")

# Secrets chargés depuis les variables d'environnement (avec valeurs par défaut pour le laboratoire local)
API_SECRET_KEY = os.environ.get("API_SECRET_KEY", "secret-signature-interne-isgp-2026")
PARTNER_API_KEY = os.environ.get("PARTNER_API_KEY", "isgp-secret-2026")
TOKEN_EXPIRATION_SECONDS = 300  # 5 minutes

app.secret_key = API_SECRET_KEY
app.config.update(
    SESSION_COOKIE_NAME="isgp_session",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

token_signer = URLSafeTimedSerializer(API_SECRET_KEY)

# État en mémoire du Rate Limiter (Fenêtre glissante : 3 requêtes max / 20 secondes)
RATE_LIMIT_MAX = 3
RATE_LIMIT_WINDOW = 20
RATE_LIMIT_HISTORY = {}  # client_key -> [timestamp1, timestamp2, ...]


# ==============================================================================
# 1. INITIALISATION DE LA BASE DE DONNÉES SQLITE PARTAGÉE
# ==============================================================================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS formations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            formateur TEXT DEFAULT 'Équipe ISGP',
            duree_jours INTEGER DEFAULT 5,
            salle TEXT DEFAULT 'Salle A',
            cree_par TEXT DEFAULT 'Système'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS wall_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            auteur TEXT NOT NULL,
            message TEXT NOT NULL,
            endpoint_utilise TEXT DEFAULT 'POST /api/sandbox/wall',
            horodatage TEXT NOT NULL
        )
        """
    )
    count = conn.execute("SELECT COUNT(*) FROM formations").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO formations (titre, formateur, duree_jours, salle, cree_par) VALUES (?, ?, ?, ?, ?)",
            [
                ("Développement d'APIs et services web (Flask)", "Formateur ISGP", 5, "Labo 1", "Initialisation"),
                ("Initiation Python & Format JSON", "Formateur ISGP", 2, "Salle 102", "Initialisation"),
                ("Sécurité REST : Tokens, Secrets & Rate Limiting", "Formateur ISGP", 3, "Salle 204", "Initialisation"),
            ],
        )
    wall_count = conn.execute("SELECT COUNT(*) FROM wall_messages").fetchone()[0]
    if wall_count == 0:
        conn.execute(
            "INSERT INTO wall_messages (auteur, message, horodatage) VALUES (?, ?, ?)",
            (
                "Formateur ISGP",
                "Séminaire initialisé. Envoyez une requête POST sur /api/sandbox/wall pour publier dans ce journal.",
                datetime.now().strftime("%H:%M:%S"),
            ),
        )
    conn.commit()
    conn.close()


init_db()


# ==============================================================================
# 2. ÉTAT TEMPS RÉEL DE LA SALLE DE CLASSE (FORMATEUR <-> PARTICIPANTS)
# ==============================================================================
CLASSROOM_STATE = {
    "version": 1,
    "sync_enabled": True,
    "active_day": 0,
    "active_lesson_id": "d0-l1",
    "active_tab": "course",
    "teacher_banner": "Séminaire de 5 jours — Aucun prérequis technique n'est supposé. Chaque concept est détaillé étape par étape.",
    "shared_live_code": (
        "# Code partagé en direct par le formateur\n"
        "from flask import Flask, jsonify\n\n"
        "app = Flask(__name__)\n\n"
        "@app.route('/api/test')\n"
        "def test():\n"
        "    return jsonify({'statut': 'opérationnel'})\n"
    ),
    "shared_sandbox_preset": {
        "method": "GET",
        "url": "/api/sandbox/formations",
        "body": "",
    },
    "students": {},
    "updated_at": time.time(),
}

SSE_SUBSCRIBERS = []


def broadcast_classroom_state():
    CLASSROOM_STATE["version"] += 1
    CLASSROOM_STATE["updated_at"] = time.time()
    cutoff = time.time() - 7200
    CLASSROOM_STATE["students"] = {
        k: v for k, v in CLASSROOM_STATE["students"].items() if v.get("updated_at", 0) > cutoff
    }
    payload = f"data: {json.dumps(CLASSROOM_STATE, ensure_ascii=False)}\n\n"
    dead_queues = []
    for q in SSE_SUBSCRIBERS:
        try:
            q.put_nowait(payload)
        except queue.Full:
            dead_queues.append(q)
    for q in dead_queues:
        if q in SSE_SUBSCRIBERS:
            SSE_SUBSCRIBERS.remove(q)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ==============================================================================
# 3. ROUTES PRINCIPALES DE LA PWA, PORTAIL TRILOGIE (/) & COURS PAR FRAMEWORK
# ==============================================================================
def _render_framework_course_page(framework: str):
    fw = framework.lower().strip()
    if fw not in VALID_FRAMEWORKS:
        return redirect("/")
    session["active_framework"] = fw
    local_ip = get_local_ip()

    tpl_path = os.path.join(ROOT_DIR, f"{fw}-version", "templates", "index.html")
    if not os.path.isfile(tpl_path):
        tpl_path = os.path.join(ROOT_DIR, "templates", "index.html")

    with open(tpl_path, encoding="utf-8") as f:
        raw_html = f.read()

    switcher_bar = f"""
    <div class="trilogy-switcher-bar">
      <div class="trilogy-switcher-left">
        <a href="/" class="trilogy-home-link">
          &larr; Portail d'Accueil Trilogie
        </a>
        <span style="color: #64748b;">|</span>
        <span style="color: #94a3b8; font-weight: 500;">Édition :</span>
        <a href="/cours/flask" class="trilogy-fw-pill {'active-flask' if fw == 'flask' else ''}">
          Vol. I — Flask (WSGI)
        </a>
        <a href="/cours/fastapi" class="trilogy-fw-pill {'active-fastapi' if fw == 'fastapi' else ''}">
          Vol. II — FastAPI (ASGI)
        </a>
        <a href="/cours/tornado" class="trilogy-fw-pill {'active-tornado' if fw == 'tornado' else ''}">
          Vol. III — Tornado (IOLoop)
        </a>
      </div>
      <div style="color: #94a3b8; font-size: 12px;">
        Framework actif : <strong style="color: #f8fafc; text-transform: uppercase;">{fw}</strong> &bull; <code>{fw}-version/</code>
      </div>
    </div>
    <script>window.ACTIVE_FRAMEWORK = "{fw}";</script>
    """
    raw_html = raw_html.replace("<body>", "<body>\n" + switcher_bar, 1)
    return render_template_string(raw_html, local_ip=local_ip, active_framework=fw)


@app.route("/")
def index():
    requested_fw = request.args.get("framework", "").strip().lower()
    if requested_fw in VALID_FRAMEWORKS:
        return _render_framework_course_page(requested_fw)
    local_ip = get_local_ip()
    return render_template("landing.html", local_ip=local_ip)


@app.route("/cours/<framework>")
def cours_par_framework(framework):
    return _render_framework_course_page(framework)


@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json", mimetype="application/manifest+json")


@app.route("/sw.js")
def service_worker():
    response = send_from_directory("static", "sw.js", mimetype="application/javascript")
    response.headers["Cache-Control"] = "no-cache"
    return response


@app.route("/api/course-data")
def get_course_data():
    fw = _resolve_active_framework()
    bundle = FRAMEWORK_BUNDLES.get(fw, FRAMEWORK_BUNDLES["flask"])
    return jsonify(
        {
            "framework": fw,
            "days": bundle["days"],
            "glossary": bundle["glossary"],
            "quizzes": bundle["quizzes"],
            "classroom": CLASSROOM_STATE,
            "server_ip": get_local_ip(),
        }
    )


@app.route("/api/download/day/<int:day_id>")
def download_starter_file(day_id):
    fw = _resolve_active_framework()
    bundle = FRAMEWORK_BUNDLES.get(fw, FRAMEWORK_BUNDLES["flask"])
    starters = bundle["starter_files"]
    code = starters.get(str(day_id), starters.get("0", ""))
    filename = f"isgp_{fw}_jour{day_id}_starter.py"
    for d in bundle["days"]:
        if d["day_number"] == day_id:
            filename = os.path.basename(d["starter_filename"])
            break
    return Response(
        code,
        mimetype="text/x-python",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/api/day-file/<int:day_id>/<path:filename>")
@app.route("/api/day-file/day_<int:day_id>/<path:filename>")
def get_day_file(day_id, filename):
    if day_id not in (0, 1, 2, 3, 4, 5):
        return jsonify({"erreur": "Jour invalide"}), 404
    fw = _resolve_active_framework()
    folder = os.path.join(ROOT_DIR, f"{fw}-version", f"day_{day_id}")
    if not os.path.isdir(folder):
        folder = os.path.join(ROOT_DIR, f"day_{day_id}")
    safe_name = os.path.basename(filename)
    full_path = os.path.join(folder, safe_name)
    if not os.path.isfile(full_path):
        return jsonify({"erreur": "Fichier introuvable"}), 404
    if request.args.get("download") == "1":
        return send_from_directory(folder, safe_name, as_attachment=True)
    with open(full_path, encoding="utf-8") as f:
        return jsonify({"framework": fw, "path": f"{fw}-version/day_{day_id}/{safe_name}", "code": f.read()})


# ==============================================================================
# 4. SYNCHRONISATION SALLE DE CLASSE (FORMATEUR <-> PARTICIPANTS)
# ==============================================================================
@app.route("/api/classroom/state", methods=["GET"])
def get_classroom_state():
    return jsonify(CLASSROOM_STATE)


@app.route("/api/classroom/stream")
def classroom_stream():
    def event_stream():
        q = queue.Queue(maxsize=30)
        SSE_SUBSCRIBERS.append(q)
        try:
            yield f"data: {json.dumps(CLASSROOM_STATE, ensure_ascii=False)}\n\n"
            while True:
                try:
                    msg = q.get(timeout=20)
                    yield msg
                except queue.Empty:
                    yield ": keepalive\n\n"
        finally:
            if q in SSE_SUBSCRIBERS:
                SSE_SUBSCRIBERS.remove(q)

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/classroom/update", methods=["POST"])
def update_classroom():
    data = request.get_json() or {}
    pin = data.get("pin", "")
    if pin != TEACHER_PIN:
        return jsonify({"erreur": "Code PIN formateur incorrect (par défaut : isgp)"}), 403

    for field in [
        "sync_enabled",
        "active_day",
        "active_lesson_id",
        "active_tab",
        "teacher_banner",
        "shared_live_code",
        "shared_sandbox_preset",
    ]:
        if field in data:
            CLASSROOM_STATE[field] = data[field]

    broadcast_classroom_state()
    return jsonify({"statut": "synchronisé", "state": CLASSROOM_STATE}), 200


@app.route("/api/classroom/student-status", methods=["POST"])
def update_student_status():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()[:40]
    status = data.get("status", "ok")
    if not name:
        return jsonify({"erreur": "Veuillez indiquer votre nom ou prénom"}), 400

    CLASSROOM_STATE["students"][name] = {
        "name": name,
        "status": status,
        "day": data.get("day", CLASSROOM_STATE["active_day"]),
        "updated_at": time.time(),
        "time_str": datetime.now().strftime("%H:%M"),
    }
    broadcast_classroom_state()
    return jsonify({"statut": "enregistré", "students": CLASSROOM_STATE["students"]}), 200


# ==============================================================================
# 5. SANDBOX HTTP ÉDUCATIF (AVEC TRACE D'EXÉCUTION ADAPTÉE AU FRAMEWORK ACTIF)
# ==============================================================================
def _adapt_trace_for_framework(fw, payload, handler_code, trace_steps):
    if fw == "fastapi":
        if isinstance(payload, dict) and payload.get("message") == "Service Flask ISGP opérationnel":
            payload = dict(payload, message="Service FastAPI ISGP opérationnel")
        code = handler_code
        code = re.sub(r'@app\.route\("([^"]+)",\s*methods=\["GET"\]\)', r'@app.get("\1")', code)
        code = re.sub(r'@app\.route\("([^"]+)",\s*methods=\["POST"\]\)', r'@app.post("\1")', code)
        code = re.sub(r'@app\.route\("([^"]+)",\s*methods=\["PUT"\]\)', r'@app.put("\1")', code)
        code = re.sub(r'@app\.route\("([^"]+)",\s*methods=\["DELETE"\]\)', r'@app.delete("\1")', code)
        code = re.sub(r'@app\.route\("([^"]+)"\)', r'@app.get("\1")', code)
        code = code.replace("<int:code>", "{code}").replace("<int:id>", "{id}")
        code = re.sub(r"^def ", "async def ", code, flags=re.MULTILINE)
        code = code.replace("request.args.get", "request.query_params.get")
        code = code.replace("request.get_json()", "await request.json()")
        code = code.replace("Service Flask ISGP opérationnel", "Service FastAPI ISGP opérationnel")
        code = code.replace("jsonify(", "JSONResponse(content=")
        steps = [
            s.replace("@app.route déclenche la fonction Python", "Le routeur ASGI FastAPI déclenche la coroutine")
            .replace("jsonify()", "JSONResponse / Pydantic v2")
            .replace("request.args.get", "Query(...) / request.query_params.get")
            .replace("request.get_json()", "Schéma Pydantic / await request.json()")
            for s in trace_steps
        ]
        return payload, code, steps

    if fw == "tornado":
        if isinstance(payload, dict) and payload.get("message") == "Service Flask ISGP opérationnel":
            payload = dict(payload, message="Service Tornado ISGP opérationnel")
        code = handler_code
        code = re.sub(
            r'@app\.route\("([^"]+)",\s*methods=\["(GET|POST|PUT|DELETE)"\]\)\ndef\s+\w+\(([^)]*)\):',
            lambda m: f'# Route Tornado : (r"{m.group(1)}", SandboxHandler)\nclass SandboxHandler(tornado.web.RequestHandler):\n    async def {m.group(2).lower()}(self{", " + m.group(3) if m.group(3) else ""}):',
            code,
        )
        code = re.sub(
            r'@app\.route\("([^"]+)"\)\ndef\s+\w+\(([^)]*)\):',
            lambda m: f'# Route Tornado : (r"{m.group(1)}", SandboxHandler)\nclass SandboxHandler(tornado.web.RequestHandler):\n    async def get(self{", " + m.group(2) if m.group(2) else ""}):',
            code,
        )
        code = code.replace("request.args.get", "self.get_query_argument")
        code = code.replace("request.get_json()", "tornado.escape.json_decode(self.request.body)")
        code = code.replace("request.headers.get", "self.request.headers.get")
        code = code.replace("Service Flask ISGP opérationnel", "Service Tornado ISGP opérationnel")
        code = code.replace("return jsonify(", "self.write(")
        code = code.replace("jsonify(", "self.write(")
        steps = [
            s.replace("Le décorateur @app.route déclenche la fonction Python", "L'IOLoop Tornado déclenche la méthode de classe RequestHandler")
            .replace("jsonify()", "self.write() (Tornado JSON)")
            .replace("request.args.get", "self.get_query_argument")
            .replace("request.get_json()", "tornado.escape.json_decode(self.request.body)")
            for s in trace_steps
        ]
        return payload, code, steps

    return payload, handler_code, trace_steps


def make_traced_response(payload, status_code, handler_code, trace_steps, extra_headers=None):
    fw = (request.headers.get("X-Active-Framework") or _resolve_active_framework()).strip().lower()
    payload, handler_code, trace_steps = _adapt_trace_for_framework(fw, payload, handler_code, trace_steps)
    resp = jsonify(payload)
    resp.status_code = status_code
    resp.headers["X-Flask-Handler-Code"] = json.dumps(handler_code)
    resp.headers["X-Flask-Trace-Steps"] = json.dumps(trace_steps)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    if extra_headers:
        for k, v in extra_headers.items():
            resp.headers[k] = str(v)
    return resp


@app.route("/api/sandbox/bonjour", methods=["GET"])
def sandbox_bonjour():
    handler_code = (
        '@app.route("/api/sandbox/bonjour", methods=["GET"])\n'
        "def sandbox_bonjour():\n"
        "    return jsonify({\n"
        '        "message": "Service Flask ISGP opérationnel",\n'
        '        "protocole": "HTTP/1.1",\n'
        '        "format": "JSON"\n'
        "    }), 200"
    )
    steps = [
        "1. Réception de la requête GET sur la route '/api/sandbox/bonjour'.",
        "2. Le décorateur @app.route déclenche la fonction Python sandbox_bonjour().",
        "3. Construction du dictionnaire Python de réponse.",
        "4. Sérialisation via jsonify() avec le code de statut HTTP 200 OK.",
    ]
    return make_traced_response(
        {
            "message": "Service Flask ISGP opérationnel",
            "protocole": "HTTP/1.1",
            "format": "JSON",
            "heure_serveur": datetime.now().strftime("%H:%M:%S"),
        },
        200,
        handler_code,
        steps,
    )


@app.route("/api/sandbox/meteo", methods=["GET"])
def sandbox_meteo():
    ville = request.args.get("ville", "Alger")
    donnees_villes = {
        "alger": {"temp": 24, "ciel": "Ensoleillé", "humidite": 55},
        "oran": {"temp": 26, "ciel": "Dégagé", "humidite": 60},
        "constantine": {"temp": 19, "ciel": "Nuageux", "humidite": 48},
        "annaba": {"temp": 25, "ciel": "Brise marine", "humidite": 65},
    }
    info = donnees_villes.get(ville.lower(), {"temp": 22, "ciel": "Variable", "humidite": 50})
    handler_code = (
        '@app.route("/api/sandbox/meteo", methods=["GET"])\n'
        "def sandbox_meteo():\n"
        '    ville = request.args.get("ville", "Alger")\n'
        "    return jsonify({\n"
        '        "ville": ville,\n'
        f'        "temperature_celsius": {info["temp"]},\n'
        f'        "condition": "{info["ciel"]}"\n'
        "    }), 200"
    )
    steps = [
        f"1. Réception de GET /api/sandbox/meteo avec le paramètre ?ville={ville}.",
        f"2. request.args.get('ville') extrait la valeur '{ville}'.",
        "3. Recherche des relevés dans le dictionnaire Python du serveur.",
        "4. Envoi de la réponse JSON (200 OK).",
    ]
    return make_traced_response(
        {
            "ville": ville,
            "temperature_celsius": info["temp"],
            "condition": info["ciel"],
            "humidite_pourcent": info["humidite"],
            "unite": "Celsius",
        },
        200,
        handler_code,
        steps,
    )


@app.route("/api/sandbox/calcul-tva", methods=["GET"])
def sandbox_calcul_tva():
    try:
        ht = float(request.args.get("ht", 1000))
        taux = float(request.args.get("taux", 19))
    except ValueError:
        return make_traced_response(
            {"erreur": "Les paramètres 'ht' et 'taux' doivent être des valeurs numériques."},
            400,
            '# Erreur de conversion float(request.args.get("ht")) -> 400 Bad Request',
            ["1. Paramètre non numérique détecté dans ?ht= ou ?taux=.", "2. Retour immédiat 400 Bad Request."],
        )

    tva = round(ht * (taux / 100.0), 2)
    ttc = round(ht + tva, 2)
    handler_code = (
        '@app.route("/api/sandbox/calcul-tva", methods=["GET"])\n'
        "def sandbox_calcul_tva():\n"
        '    ht = float(request.args.get("ht", 1000))\n'
        '    taux = float(request.args.get("taux", 19))\n'
        "    tva = round(ht * (taux / 100), 2)\n"
        '    return jsonify({"prix_ht": ht, "taux_tva": taux, "montant_tva": tva, "prix_ttc": ht + tva}), 200'
    )
    steps = [
        f"1. Extraction des paramètres de requête : ht={ht}, taux={taux}.",
        f"2. Calcul en Python : TVA = {ht} * ({taux}/100) = {tva}.",
        f"3. Calcul du montant TTC = {ttc}.",
        "4. Sérialisation du dictionnaire en JSON (200 OK).",
    ]
    return make_traced_response(
        {"prix_ht": ht, "taux_tva_pourcent": taux, "montant_tva": tva, "prix_ttc": ttc, "devise": "DZD"},
        200,
        handler_code,
        steps,
    )


@app.route("/api/sandbox/status-demo/<int:code>", methods=["GET"])
def sandbox_status_demo(code):
    descriptions = {
        200: ("200 OK", "Succès standard : la requête a été traitée normalement."),
        201: ("201 Created", "Création réussie : une nouvelle ressource a été enregistrée."),
        400: ("400 Bad Request", "Requête invalide : champ obligatoire manquant ou JSON mal formé."),
        401: ("401 Unauthorized", "Non authentifié : Bearer Token ou Clé API manquant, expiré ou invalide."),
        403: ("403 Forbidden", "Accès interdit : droits insuffisants pour cette ressource."),
        404: ("404 Not Found", "Ressource introuvable : cette route ou cet ID n'existe pas."),
        429: ("429 Too Many Requests", "Quota dépassé (Rate Limiting) : trop de requêtes envoyées sur la période."),
        500: ("500 Internal Server Error", "Erreur interne du serveur : exception non gérée côté Python."),
    }
    titre, explication = descriptions.get(code, (f"{code} Custom", "Code de statut HTTP personnalisé."))
    handler_code = (
        '@app.route("/api/sandbox/status-demo/<int:code>")\n'
        "def sandbox_status_demo(code):\n"
        f'    return jsonify({{"code_http": {code}, "nom_officiel": "{titre}"}}), {code}'
    )
    steps = [
        f"1. Capture du paramètre de chemin <int:code> = {code}.",
        f"2. Sélection de la définition normalisée du code {code}.",
        f"3. Retour du tuple (jsonify(...), {code}) fixant le statut HTTP de la réponse.",
    ]
    return make_traced_response(
        {"code_http": code, "nom_officiel": titre, "explication": explication},
        code if code in descriptions else 200,
        handler_code,
        steps,
    )


# ==============================================================================
# 6. CŒUR D'API : SECRETS, BEARER TOKENS SIGNÉS, X-API-KEY & RATE LIMITING (429)
# ==============================================================================
@app.route("/api/sandbox/auth/token", methods=["POST"])
def sandbox_auth_token():
    corps = request.get_json(silent=True) or {}
    identifiant = str(corps.get("identifiant", "")).strip()
    mot_de_passe = str(corps.get("mot_de_passe", "")).strip()

    comptes_demo = {
        "stagiaire": {
            "role": "stagiaire",
            "scopes": ["formations:read", "profil:read"],
        },
        "directeur": {
            "role": "admin",
            "scopes": ["formations:read", "formations:write", "audit:admin"],
        },
    }

    if identifiant not in comptes_demo or mot_de_passe != "isgp2026":
        handler_code = (
            "corps = request.get_json()\n"
            'if identifiant not in ("stagiaire", "directeur") or mot_de_passe != "isgp2026":\n'
            '    return jsonify({"erreur": "401 Unauthorized (Échec AuthN)"}), 401'
        )
        steps = [
            "1. Réception de POST /api/sandbox/auth/token.",
            "2. Vérification des identifiants fournis (Authentification / AuthN).",
            "3. ÉCHEC AuthN : Identifiant ou mot de passe incorrect -> 401 Unauthorized.",
        ]
        return make_traced_response(
            {
                "erreur": "Identifiants invalides (401 Unauthorized — Échec d'Authentification).",
                "comptes_disponibles_pour_demo": [
                    {"identifiant": "stagiaire", "mot_de_passe": "isgp2026", "role": "stagiaire (lecture seule)"},
                    {"identifiant": "directeur", "mot_de_passe": "isgp2026", "role": "admin (tous les droits)"},
                ],
            },
            401,
            handler_code,
            steps,
            extra_headers={"WWW-Authenticate": 'Bearer realm="ISGP-API"'},
        )

    infos_compte = comptes_demo[identifiant]
    charge_utile = {
        "utilisateur": identifiant,
        "role": infos_compte["role"],
        "scopes": infos_compte["scopes"],
        "emis_a": datetime.now().strftime("%H:%M:%S"),
    }
    token = token_signer.dumps(charge_utile)
    secret_masque = API_SECRET_KEY[:6] + "..." + API_SECRET_KEY[-4:]

    handler_code = (
        'API_SECRET_KEY = os.environ.get("API_SECRET_KEY")\n'
        "signer = URLSafeTimedSerializer(API_SECRET_KEY)\n\n"
        '@app.route("/api/sandbox/auth/token", methods=["POST"])\n'
        "def emettre_token():\n"
        f'    payload = {{"utilisateur": "{identifiant}", "role": "participant_isgp"}}\n'
        "    token = signer.dumps(payload)  # Signé avec API_SECRET_KEY\n"
        '    return jsonify({"access_token": token, "token_type": "Bearer", "expires_in": 300}), 200'
    )
    steps = [
        f"1. Authentification réussie pour l'identifiant '{identifiant}'.",
        f"2. Chargement du secret serveur via os.environ.get('API_SECRET_KEY') ({secret_masque}).",
        "3. Signature cryptographique (HMAC) de la charge utile et de l'horodatage.",
        "4. Émission du Bearer Token temporaire (valide 300 secondes).",
    ]
    return make_traced_response(
        {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in_seconds": TOKEN_EXPIRATION_SECONDS,
            "en_tete_a_envoyer": f"Authorization: Bearer {token}",
            "contenu_signe_dans_le_token": charge_utile,
            "secret_serveur_utilise_masque": secret_masque,
        },
        200,
        handler_code,
        steps,
    )


@app.route("/api/sandbox/auth/profil", methods=["GET"])
def sandbox_auth_profil():
    auth_header = request.headers.get("Authorization", "").strip()
    if not auth_header.startswith("Bearer "):
        handler_code = (
            'auth_header = request.headers.get("Authorization", "")\n'
            'if not auth_header.startswith("Bearer "):\n'
            '    return jsonify({"erreur": "En-tête Authorization: Bearer <token> manquant"}), 401'
        )
        steps = [
            "1. Inspection de l'en-tête HTTP 'Authorization'.",
            f"2. Valeur reçue : '{auth_header or '(aucune)'}'.",
            "3. Absence du préfixe 'Bearer <token>' -> Rejet 401 Unauthorized.",
        ]
        return make_traced_response(
            {
                "erreur": "Accès refusé (401) : En-tête 'Authorization: Bearer <token>' requis.",
                "procedure": "1) Appelez POST /api/sandbox/auth/token pour obtenir un access_token, 2) Placez-le dans le champ Bearer Token.",
            },
            401,
            handler_code,
            steps,
            extra_headers={"WWW-Authenticate": 'Bearer realm="ISGP-API"'},
        )

    token = auth_header.split(" ", 1)[1].strip()
    try:
        donnees_jeton = token_signer.loads(token, max_age=TOKEN_EXPIRATION_SECONDS)
        handler_code = (
            'token = request.headers.get("Authorization").split(" ")[1]\n'
            "# Vérifie la signature cryptographique (SECRET_KEY) et l'âge (< 300s)\n"
            "donnees = signer.loads(token, max_age=300)\n"
            'return jsonify({"acces": "Autorisé", "profil": donnees}), 200'
        )
        steps = [
            "1. Extraction du jeton depuis l'en-tête 'Authorization: Bearer ...'.",
            "2. Recalcul de la signature HMAC avec API_SECRET_KEY : signature authentique.",
            "3. Contrôle d'expiration (max_age=300s) : jeton en cours de validité.",
            "4. Accès accordé aux données protégées (200 OK).",
        ]
        return make_traced_response(
            {
                "acces": "Autorisé via Bearer Token signé",
                "verification_signature_hmac": "Valide",
                "profil_decode": donnees_jeton,
                "ressource_protegee": {
                    "environnement": "Production ISGP",
                    "droits": ["lecture_catalogue", "ecriture_formations"],
                },
            },
            200,
            handler_code,
            steps,
        )
    except SignatureExpired:
        return make_traced_response(
            {"erreur": "Accès refusé (401) : Le Bearer Token a expiré (durée max : 300s). Régénérez un nouveau token."},
            401,
            "except SignatureExpired:\n    return jsonify({'erreur': 'Token expiré'}), 401",
            ["1. Signature valide mais la durée de vie de 300s est dépassée.", "2. Rejet 401 Unauthorized."],
            extra_headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="Token expired"'},
        )
    except BadSignature:
        return make_traced_response(
            {
                "erreur": "Accès refusé (401) : Signature du Bearer Token invalide ! Le jeton a été modifié ou forgé sans la SECRET_KEY."
            },
            401,
            "except BadSignature:\n    return jsonify({'erreur': 'Signature invalide (Token altéré)'}), 401",
            [
                "1. Vérification cryptographique HMAC avec API_SECRET_KEY.",
                "2. ÉCHEC : La signature du token ne correspond pas aux données !",
                "3. Tentative de falsification ou token mal formé bloquée (401 Unauthorized).",
            ],
            extra_headers={"WWW-Authenticate": 'Bearer error="invalid_token", error_description="Bad signature"'},
        )


@app.route("/api/sandbox/authz-demo", methods=["GET"])
def sandbox_authz_demo():
    auth_header = request.headers.get("Authorization", "").strip()
    # ÉTAPE 1 : AUTHENTIFICATION (AuthN — Qui êtes-vous ?)
    if not auth_header.startswith("Bearer "):
        handler_code = (
            "# ÉTAPE 1 : AUTHENTIFICATION (AuthN)\n"
            'auth = request.headers.get("Authorization", "")\n'
            'if not auth.startswith("Bearer "):\n'
            '    return jsonify({"etape": "AuthN", "erreur": "401 Unauthorized : Identité inconnue"}), 401'
        )
        steps = [
            "1. [AuthN — Authentification] Recherche du jeton dans 'Authorization: Bearer <token>'.",
            "2. Aucun jeton fourni : le serveur ne sait pas QUI appelle la route.",
            "3. Rejet immédiat en HTTP 401 Unauthorized (défaut d'Authentification).",
        ]
        return make_traced_response(
            {
                "statut_http": 401,
                "etape_bloquee": "1. Authentification (AuthN — 'Qui êtes-vous ?')",
                "erreur": "401 Unauthorized : Aucun Bearer Token fourni. Votre identité est inconnue.",
                "comment_tester": "Générez un token pour 'stagiaire' (qui donnera 403 Forbidden) ou 'directeur' (qui donnera 200 OK).",
            },
            401,
            handler_code,
            steps,
            extra_headers={"WWW-Authenticate": 'Bearer realm="ISGP-API"'},
        )

    token = auth_header.split(" ", 1)[1].strip()
    try:
        identite = token_signer.loads(token, max_age=TOKEN_EXPIRATION_SECONDS)
    except (BadSignature, SignatureExpired):
        return make_traced_response(
            {
                "statut_http": 401,
                "etape_bloquee": "1. Authentification (AuthN)",
                "erreur": "401 Unauthorized : Jeton expiré ou signature falsifiée.",
            },
            401,
            "identite = signer.loads(token, max_age=300)  # -> 401 si invalide",
            ["1. [AuthN] Jeton invalide ou expiré -> 401 Unauthorized."],
        )

    # ÉTAPE 2 : AUTORISATION (AuthZ — Quels sont vos droits / rôles / scopes ?)
    utilisateur = identite.get("utilisateur", "inconnu")
    role = identite.get("role", "stagiaire")
    scopes = identite.get("scopes", [])

    if role != "admin" or "audit:admin" not in scopes:
        handler_code = (
            "# ÉTAPE 1 : AuthN réussie -> identite connue ('stagiaire')\n"
            "# ÉTAPE 2 : AUTORISATION (AuthZ — Vérification du Rôle et du Scope)\n"
            'if identite["role"] != "admin" or "audit:admin" not in identite["scopes"]:\n'
            '    return jsonify({"etape": "AuthZ", "erreur": "403 Forbidden : Droits insuffisants"}), 403'
        )
        steps = [
            f"1. [AuthN — Authentification RÉUSSIE] Jeton valide : vous êtes bien identifié comme '{utilisateur}'.",
            f"2. [AuthZ — Autorisation] Lecture de vos droits dans le token : role='{role}', scopes={scopes}.",
            "3. ÉCHEC AuthZ : Cette route exige role='admin' et le scope 'audit:admin'.",
            "4. Rejet en HTTP 403 Forbidden (Identité connue, mais permission refusée !).",
        ]
        return make_traced_response(
            {
                "statut_http": 403,
                "etape_1_authentification_authn": f"RÉUSSIE (Identité prouvée : '{utilisateur}')",
                "etape_2_autorisation_authz": "REFUSÉE (403 Forbidden — Droits insuffisants)",
                "droits_actuels_du_token": {"role": role, "scopes": scopes},
                "droits_requis_par_la_route": {"role": "admin", "scope_requis": "audit:admin"},
                "astuce_pour_obtenir_200": "Appelez POST /api/sandbox/auth/token avec {\"identifiant\": \"directeur\", \"mot_de_passe\": \"isgp2026\"}",
            },
            403,
            handler_code,
            steps,
        )

    handler_code = (
        "# ÉTAPE 1 (AuthN) : Jeton valide ('directeur')\n"
        "# ÉTAPE 2 (AuthZ) : role == 'admin' et 'audit:admin' in scopes\n"
        'return jsonify({"acces": "Autorisé (AuthN + AuthZ OK)", "journal_audit": [...]}), 200'
    )
    steps = [
        f"1. [AuthN — Authentification RÉUSSIE] Identité vérifiée : '{utilisateur}'.",
        f"2. [AuthZ — Autorisation RÉUSSIE] Rôle '{role}' et scope 'audit:admin' présents.",
        "3. Accès accordé à la ressource critique (200 OK).",
    ]
    return make_traced_response(
        {
            "statut_http": 200,
            "etape_1_authentification_authn": f"RÉUSSIE ('{utilisateur}')",
            "etape_2_autorisation_authz": "RÉUSSIE (Rôle 'admin' + Scope 'audit:admin' vérifiés)",
            "registre_audit_confidentiel": [
                {"evenement": "Rotation des clés HMAC", "statut": "Succès"},
                {"evenement": "Audit sécurité OWASP API", "statut": "Conforme"},
            ],
        },
        200,
        handler_code,
        steps,
    )


@app.route("/api/sandbox/admin-stats", methods=["GET"])
def sandbox_admin_stats():
    cle_recue = request.headers.get("X-API-Key", "")

    if not hmac.compare_digest(cle_recue, PARTNER_API_KEY):
        handler_code = (
            'PARTNER_API_KEY = os.environ.get("PARTNER_API_KEY")\n'
            'cle_recue = request.headers.get("X-API-Key", "")\n'
            "if not hmac.compare_digest(cle_recue, PARTNER_API_KEY):\n"
            '    return jsonify({"erreur": "Clé API invalide ou absente"}), 401'
        )
        steps = [
            "1. Lecture de l'en-tête HTTP 'X-API-Key'.",
            f"2. Comparaison en temps constant (hmac.compare_digest) : clé reçue '{cle_recue or '(vide)'}' invalide.",
            "3. Rejet immédiat avec le statut 401 Unauthorized.",
        ]
        return make_traced_response(
            {
                "erreur": "Accès refusé (401 Unauthorized) : Clé 'X-API-Key' manquante ou invalide dans les Headers.",
                "attendu_pour_demo": "X-API-Key: isgp-secret-2026",
            },
            401,
            handler_code,
            steps,
        )

    handler_code = (
        'PARTNER_API_KEY = os.environ.get("PARTNER_API_KEY")\n'
        'cle_recue = request.headers.get("X-API-Key", "")\n'
        "if hmac.compare_digest(cle_recue, PARTNER_API_KEY):\n"
        '    return jsonify({"acces": "Autorisé via X-API-Key", "stagiaires_certifies": 148}), 200'
    )
    steps = [
        "1. Lecture de l'en-tête HTTP 'X-API-Key'.",
        "2. Validation via hmac.compare_digest avec le secret PARTNER_API_KEY de l'environnement.",
        "3. Envoi des données administrateur (200 OK).",
    ]
    return make_traced_response(
        {
            "acces": "Authentifié via en-tête X-API-Key",
            "organisme": "ISGP",
            "stagiaires_certifies_annee": 148,
            "taux_validation": "98.4%",
        },
        200,
        handler_code,
        steps,
    )


@app.route("/api/sandbox/ratelimit-demo", methods=["GET"])
def sandbox_ratelimit_demo():
    ip_client = request.remote_addr or "127.0.0.1"
    maintenant = time.time()

    # Purge des appels plus anciens que la fenêtre glissante (20s)
    appels_recents = [t for t in RATE_LIMIT_HISTORY.get(ip_client, []) if maintenant - t < RATE_LIMIT_WINDOW]

    if len(appels_recents) >= RATE_LIMIT_MAX:
        attente = max(1, int(RATE_LIMIT_WINDOW - (maintenant - appels_recents[0])) + 1)
        RATE_LIMIT_HISTORY[ip_client] = appels_recents
        handler_code = (
            f"# Plafond atteint : {len(appels_recents)} / {RATE_LIMIT_MAX} requêtes en {RATE_LIMIT_WINDOW}s\n"
            "if len(appels_recents) >= RATE_LIMIT_MAX:\n"
            '    resp = jsonify({"erreur": "429 Too Many Requests (Rate Limit atteint)"})\n'
            f'    resp.headers["Retry-After"] = "{attente}"\n'
            "    return resp, 429"
        )
        steps = [
            f"1. Vérification du compteur Rate Limit pour l'IP {ip_client}.",
            f"2. {len(appels_recents)} requêtes déjà effectuées dans les {RATE_LIMIT_WINDOW} dernières secondes (Plafond = {RATE_LIMIT_MAX}).",
            f"3. BLOCAGE : Retour du statut HTTP 429 Too Many Requests (Retry-After: {attente}s).",
        ]
        return make_traced_response(
            {
                "erreur": "429 Too Many Requests — Quota de requêtes dépassé (Rate Limit).",
                "politique": f"Maximum {RATE_LIMIT_MAX} requêtes par fenêtre de {RATE_LIMIT_WINDOW} secondes.",
                "requetes_restantes": 0,
                "reessayer_dans_secondes": attente,
            },
            429,
            handler_code,
            steps,
            extra_headers={
                "X-RateLimit-Limit": str(RATE_LIMIT_MAX),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(attente),
                "Retry-After": str(attente),
            },
        )

    appels_recents.append(maintenant)
    RATE_LIMIT_HISTORY[ip_client] = appels_recents
    restant = RATE_LIMIT_MAX - len(appels_recents)
    reset_dans = max(1, int(RATE_LIMIT_WINDOW - (maintenant - appels_recents[0])))

    handler_code = (
        f"# Appel #{len(appels_recents)}/{RATE_LIMIT_MAX} autorisé dans la fenêtre de {RATE_LIMIT_WINDOW}s\n"
        "appels_recents.append(time.time())\n"
        f'resp.headers["X-RateLimit-Limit"] = "{RATE_LIMIT_MAX}"\n'
        f'resp.headers["X-RateLimit-Remaining"] = "{restant}"\n'
        "return resp, 200"
    )
    steps = [
        f"1. Contrôle du Rate Limiter pour l'IP {ip_client} (fenêtre glissante de {RATE_LIMIT_WINDOW}s).",
        f"2. Requête #{len(appels_recents)} sur {RATE_LIMIT_MAX} autorisées -> Quota restant : {restant}.",
        "3. Ajout des en-têtes HTTP X-RateLimit-Limit, X-RateLimit-Remaining et X-RateLimit-Reset.",
        "4. Réponse 200 OK (cliquez encore pour atteindre la limite et déclencher le code 429 !).",
    ]
    return make_traced_response(
        {
            "statut": "Requête acceptée par le Rate Limiter",
            "appel_numero": len(appels_recents),
            "limite_par_fenetre": RATE_LIMIT_MAX,
            "fenetre_secondes": RATE_LIMIT_WINDOW,
            "requetes_restantes_avant_blocage_429": restant,
            "reinitialisation_dans_secondes": reset_dans,
        },
        200,
        handler_code,
        steps,
        extra_headers={
            "X-RateLimit-Limit": str(RATE_LIMIT_MAX),
            "X-RateLimit-Remaining": str(restant),
            "X-RateLimit-Reset": str(reset_dans),
        },
    )


# --- CRUD COMPLET SUR /api/sandbox/formations (AVEC SQLITE) ---
@app.route("/api/sandbox/formations", methods=["GET", "POST"])
def sandbox_formations():
    conn = get_db()
    if request.method == "GET":
        rows = conn.execute("SELECT * FROM formations ORDER BY id ASC").fetchall()
        conn.close()
        liste = [dict(r) for r in rows]

        # Filtrage optionnel (?salle=...)
        salle_filtre = request.args.get("salle")
        if salle_filtre:
            liste = [f for f in liste if salle_filtre.lower() in str(f.get("salle", "")).lower()]

        # Tri optionnel sécurisé (?tri=id|duree_jours|titre & ?ordre=asc|desc)
        champ_tri = request.args.get("tri", "id")
        if champ_tri not in ("id", "duree_jours", "titre"):
            champ_tri = "id"
        ordre_desc = request.args.get("ordre", "asc").lower() == "desc"
        liste = sorted(liste, key=lambda f: f.get(champ_tri, 0), reverse=ordre_desc)

        # Pagination optionnelle (?page=1&limit=10)
        total_items = len(liste)
        page = max(1, request.args.get("page", 1, type=int))
        limit = min(50, max(1, request.args.get("limit", 10, type=int)))
        offset = (page - 1) * limit
        tranche = liste[offset : offset + limit]
        total_pages = max(1, (total_items + limit - 1) // limit)

        handler_code = (
            '@app.route("/api/sandbox/formations", methods=["GET"])\n'
            "def lister_formations():\n"
            '    page = max(1, request.args.get("page", 1, type=int))\n'
            '    limit = min(50, max(1, request.args.get("limit", 10, type=int)))\n'
            "    offset = (page - 1) * limit\n"
            '    return jsonify({"meta": {...}, "total": total_items, "formations": liste[offset:offset+limit]}), 200'
        )
        steps = [
            "1. Réception d'une requête HTTP GET sur /api/sandbox/formations.",
            f"2. Lecture SQLite ({total_items} formations correspondantes) + tri sur '{champ_tri}' ({'DESC' if ordre_desc else 'ASC'}).",
            f"3. Découpage de la page {page}/{total_pages} (limit={limit}, offset={offset}) -> {len(tranche)} élément(s).",
            "4. Envoi de la réponse JSON structurée (meta + formations) avec le code 200 OK.",
        ]
        return make_traced_response(
            {
                "meta": {
                    "total_items": total_items,
                    "page": page,
                    "limit": limit,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                },
                "total": total_items,
                "formations": tranche,
            },
            200,
            handler_code,
            steps,
        )

    corps = request.get_json(silent=True)
    if not corps or not str(corps.get("titre", "")).strip():
        conn.close()
        handler_code = (
            "corps = request.get_json()\n"
            'if not corps or "titre" not in corps:\n'
            '    return jsonify({"erreur": "Le champ \'titre\' est obligatoire !"}), 400'
        )
        steps = [
            "1. Réception d'une requête POST sur /api/sandbox/formations.",
            "2. Lecture du Body avec request.get_json().",
            "3. ERREUR : Le champ obligatoire 'titre' est manquant ou vide.",
            "4. Arrêt immédiat et renvoi du code 400 Bad Request.",
        ]
        return make_traced_response(
            {
                "erreur": "Le champ 'titre' est obligatoire dans le corps JSON.",
                "exemple_attendu": {"titre": "Nouvelle Formation", "duree_jours": 5, "salle": "Salle B"},
            },
            400,
            handler_code,
            steps,
        )

    titre = str(corps["titre"]).strip()
    formateur = str(corps.get("formateur", "Participant ISGP")).strip()
    duree = int(corps.get("duree_jours", 5))
    salle = str(corps.get("salle", "Salle A")).strip()
    cree_par = str(corps.get("cree_par", "API Sandbox")).strip()

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO formations (titre, formateur, duree_jours, salle, cree_par) VALUES (?, ?, ?, ?, ?)",
        (titre, formateur, duree, salle, cree_par),
    )
    conn.commit()
    new_id = cur.lastrowid
    nouvelle = dict(conn.execute("SELECT * FROM formations WHERE id = ?", (new_id,)).fetchone())
    conn.close()

    handler_code = (
        '@app.route("/api/sandbox/formations", methods=["POST"])\n'
        "def creer_formation():\n"
        "    corps = request.get_json()\n"
        '    cur.execute("INSERT INTO formations (titre, duree_jours, salle) VALUES (?, ?, ?)", ...)\n'
        "    conn.commit()\n"
        '    return jsonify({"message": "Formation créée", "formation": nouvelle}), 201'
    )
    steps = [
        "1. Réception de POST /api/sandbox/formations avec un corps JSON valide.",
        f"2. Validation réussie : titre = '{titre}'.",
        f"3. Insertion SQL paramétrée dans SQLite -> Nouvel ID généré : #{new_id}.",
        "4. Envoi de la ressource créée avec le code HTTP 201 Created.",
    ]
    return make_traced_response(
        {"message": "Formation créée avec succès dans SQLite", "formation": nouvelle},
        201,
        handler_code,
        steps,
    )


@app.route("/api/sandbox/formations/<int:formation_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def sandbox_formation_detail(formation_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM formations WHERE id = ?", (formation_id,)).fetchone()

    if not row:
        conn.close()
        handler_code = (
            f'row = conn.execute("SELECT * FROM formations WHERE id = ?", ({formation_id},)).fetchone()\n'
            "if not row:\n"
            f'    return jsonify({{"erreur": "Formation ID {formation_id} introuvable"}}), 404'
        )
        steps = [
            f"1. Recherche de la formation ID #{formation_id} dans SQLite.",
            "2. Aucun enregistrement ne correspond à cet ID.",
            "3. Renvoi immédiat du code HTTP 404 Not Found.",
        ]
        return make_traced_response(
            {"erreur": f"Aucune formation trouvée avec l'ID {formation_id}."},
            404,
            handler_code,
            steps,
        )

    actuelle = dict(row)

    if request.method == "GET":
        conn.close()
        handler_code = (
            '@app.route("/api/sandbox/formations/<int:id>", methods=["GET"])\n'
            "def obtenir_formation(id):\n"
            '    row = conn.execute("SELECT * FROM formations WHERE id = ?", (id,)).fetchone()\n'
            "    return jsonify(dict(row)), 200"
        )
        steps = [
            f"1. Capture du paramètre d'URL <int:id> = {formation_id}.",
            f"2. Lecture de la fiche #{formation_id} ('{actuelle['titre']}') dans SQLite.",
            "3. Envoi du dictionnaire en JSON avec le code 200 OK.",
        ]
        return make_traced_response(actuelle, 200, handler_code, steps)

    if request.method in ("PUT", "PATCH"):
        corps = request.get_json(silent=True) or {}
        nouveau_titre = str(corps.get("titre", actuelle["titre"])).strip()
        nouveau_formateur = str(corps.get("formateur", actuelle["formateur"])).strip()
        nouvelle_duree = int(corps.get("duree_jours", actuelle["duree_jours"]))
        nouvelle_salle = str(corps.get("salle", actuelle["salle"])).strip()

        conn.execute(
            "UPDATE formations SET titre = ?, formateur = ?, duree_jours = ?, salle = ? WHERE id = ?",
            (nouveau_titre, nouveau_formateur, nouvelle_duree, nouvelle_salle, formation_id),
        )
        conn.commit()
        maj = dict(conn.execute("SELECT * FROM formations WHERE id = ?", (formation_id,)).fetchone())
        conn.close()

        handler_code = (
            '@app.route("/api/sandbox/formations/<int:id>", methods=["PUT"])\n'
            "def modifier_formation(id):\n"
            "    corps = request.get_json()\n"
            '    conn.execute("UPDATE formations SET titre=?, salle=? WHERE id=?", ...)\n'
            "    conn.commit()\n"
            "    return jsonify(maj), 200"
        )
        steps = [
            f"1. Réception de PUT /api/sandbox/formations/{formation_id}.",
            "2. Fusion des nouvelles valeurs envoyées dans le JSON avec les valeurs existantes.",
            f"3. Exécution de UPDATE dans SQLite pour l'ID #{formation_id}.",
            "4. Retour de la fiche mise à jour avec le code 200 OK.",
        ]
        return make_traced_response(
            {"message": f"Formation #{formation_id} mise à jour avec succès", "formation": maj},
            200,
            handler_code,
            steps,
        )

    conn.execute("DELETE FROM formations WHERE id = ?", (formation_id,))
    conn.commit()
    conn.close()
    handler_code = (
        '@app.route("/api/sandbox/formations/<int:id>", methods=["DELETE"])\n'
        "def supprimer_formation(id):\n"
        '    conn.execute("DELETE FROM formations WHERE id = ?", (id,))\n'
        "    conn.commit()\n"
        '    return jsonify({"message": "Supprimée"}), 200'
    )
    steps = [
        f"1. Réception de DELETE /api/sandbox/formations/{formation_id}.",
        f"2. Vérification que la formation #{formation_id} existe.",
        f"3. Suppression définitive dans SQLite (DELETE FROM formations WHERE id = {formation_id}).",
        "4. Confirmation JSON avec le code 200 OK.",
    ]
    return make_traced_response(
        {"message": f"La formation #{formation_id} ('{actuelle['titre']}') a été supprimée."},
        200,
        handler_code,
        steps,
    )


# --- JOURNAL PARTAGÉ DE LA SALLE (/api/sandbox/wall) ---
@app.route("/api/sandbox/wall", methods=["GET", "POST"])
def sandbox_wall():
    conn = get_db()
    if request.method == "GET":
        rows = conn.execute("SELECT * FROM wall_messages ORDER BY id DESC LIMIT 30").fetchall()
        conn.close()
        messages = [dict(r) for r in rows]
        handler_code = (
            '@app.route("/api/sandbox/wall", methods=["GET"])\n'
            "def lire_mur():\n"
            '    rows = conn.execute("SELECT * FROM wall_messages ORDER BY id DESC").fetchall()\n'
            "    return jsonify(messages), 200"
        )
        steps = [
            "1. Lecture des entrées du journal partagé dans SQLite.",
            f"2. {len(messages)} entrée(s) récupérée(s) et renvoyée(s) en JSON (200 OK).",
        ]
        return make_traced_response({"total": len(messages), "messages": messages}, 200, handler_code, steps)

    corps = request.get_json(silent=True) or {}
    auteur = str(corps.get("auteur", "")).strip()
    message = str(corps.get("message", "")).strip()
    if not auteur or not message:
        conn.close()
        return make_traced_response(
            {
                "erreur": "Les champs 'auteur' et 'message' sont obligatoires.",
                "exemple": {"auteur": "Amine", "message": "Requête POST validée."},
            },
            400,
            'if not auteur or not message:\n    return jsonify({"erreur": "Champs requis"}), 400',
            ["1. Vérification du JSON envoyé.", "2. Champ 'auteur' ou 'message' manquant -> 400 Bad Request."],
        )

    horodatage = datetime.now().strftime("%H:%M:%S")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO wall_messages (auteur, message, horodatage) VALUES (?, ?, ?)",
        (auteur[:40], message[:280], horodatage),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    broadcast_classroom_state()

    handler_code = (
        '@app.route("/api/sandbox/wall", methods=["POST"])\n'
        "def poster_message():\n"
        "    corps = request.get_json()\n"
        '    cur.execute("INSERT INTO wall_messages (auteur, message, horodatage) VALUES (?, ?, ?)", ...)\n'
        "    return jsonify(nouveau_message), 201"
    )
    steps = [
        f"1. Réception du message de '{auteur}' via POST /api/sandbox/wall.",
        "2. Sauvegarde dans la table SQLite 'wall_messages'.",
        "3. Diffusion temps réel aux postes connectés.",
        "4. Réponse 201 Created.",
    ]
    return make_traced_response(
        {
            "statut": "Enregistré dans le journal partagé",
            "entree": {"id": new_id, "auteur": auteur, "message": message, "horodatage": horodatage},
        },
        201,
        handler_code,
        steps,
    )


@app.route("/api/sandbox/reset", methods=["POST"])
def sandbox_reset():
    RATE_LIMIT_HISTORY.clear()
    conn = get_db()
    conn.execute("DELETE FROM formations")
    conn.execute("DELETE FROM wall_messages")
    conn.execute("DELETE FROM sqlite_sequence")
    conn.commit()
    conn.close()
    init_db()
    broadcast_classroom_state()
    return jsonify({"message": "Base SQLite et compteurs Rate Limit réinitialisés."}), 200


# ==============================================================================
# 7. EXÉCUTEUR PYTHON PÉDAGOGIQUE INTÉGRÉ & SIMULATEUR DE BOUCLE D'ÉVÉNEMENTS LIVE
# ==============================================================================
LIVE_PYTHON_PROCESS = {
    "proc": None,
    "tmp_path": None,
    "logs": [],
    "port": None,
    "routes": [],
    "fw": "flask",
    "lock": threading.Lock(),
}


def _prepare_runner_dir(fw: str) -> str:
    runner_dir = os.path.join(tempfile.gettempdir(), f"isgp_runner_{fw}")
    tpl_dir = os.path.join(runner_dir, "templates")
    os.makedirs(tpl_dir, exist_ok=True)
    fw_root = os.path.join(ROOT_DIR, f"{fw}-version")
    for day_idx in range(6):
        day_tpl = os.path.join(fw_root, f"day_{day_idx}", "templates")
        if os.path.isdir(day_tpl):
            for fname in os.listdir(day_tpl):
                src = os.path.join(day_tpl, fname)
                dst = os.path.join(tpl_dir, fname)
                if os.path.isfile(src) and not os.path.exists(dst):
                    with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
                        fdst.write(fsrc.read())
    return runner_dir


def _stop_live_python_process():
    with LIVE_PYTHON_PROCESS["lock"]:
        proc = LIVE_PYTHON_PROCESS.get("proc")
        tmp_path = LIVE_PYTHON_PROCESS.get("tmp_path")
        if proc is not None and proc.poll() is None:
            try:
                proc.send_signal(signal.SIGINT)
                proc.wait(timeout=0.6)
            except Exception:
                try:
                    proc.terminate()
                    proc.wait(timeout=0.4)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        LIVE_PYTHON_PROCESS["proc"] = None
        LIVE_PYTHON_PROCESS["tmp_path"] = None


def _find_available_port(preferred_port: int) -> int:
    for candidate in range(preferred_port, preferred_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if s.connect_ex(("127.0.0.1", candidate)) != 0:
                return candidate
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _extract_routes_and_port(code: str, output_text: str, fw: str, default_port: int = None):
    port = default_port or {"tornado": 8889, "fastapi": 8001, "flask": 5001}.get(fw, 5001)
    m_banner = re.findall(r"Serveur en écoute sur http://(?:127\.0\.0\.1|0\.0\.0\.0):(\d+)", output_text)
    if m_banner:
        port = int(m_banner[-1])
    else:
        m_all = re.findall(r"http://(?:127\.0\.0\.1|0\.0\.0\.0):(\d+)", output_text)
        if m_all:
            port = int(m_all[-1])

    raw_routes = []
    # Tornado routes: (r"/api/...", Handler)
    for m in re.finditer(r'\(\s*r"(/[^"]*)"', code):
        raw_routes.append(m.group(1))
    # FastAPI routes: @app.get("/api/...") or @router_v1.get("/...")
    for m in re.finditer(r'@(?:app|router\w*)\.(?:get|post|put|patch|delete)\(\s*"(/[^"]*)"', code):
        raw_routes.append(m.group(1))
    # Flask routes: @app.route("/api/...") or @bp_v1.route("/...")
    for m in re.finditer(r'@(?:app|bp\w*)\.route\(\s*"(/[^"]*)"', code):
        raw_routes.append(m.group(1))

    clean_routes = []
    for r in raw_routes:
        r_clean = r.replace("([^/]+)", "Yasmine").replace("([0-9]+)", "1")
        r_clean = re.sub(r"<int:[^>]+>", "1", r_clean)
        r_clean = re.sub(r"<[^>]+>", "Yasmine", r_clean)
        r_clean = re.sub(r"\{[^}]*id[^}]*\}", "1", r_clean)
        r_clean = re.sub(r"\{[^}]+\}", "Yasmine", r_clean)
        if r_clean not in clean_routes:
            clean_routes.append(r_clean)

    if fw == "fastapi" and "/docs" not in clean_routes:
        clean_routes.append("/docs")

    return port, clean_routes[:6]


@app.route("/api/python/run", methods=["POST"])
def run_python_snippet():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not code.strip():
        return jsonify({"output": "", "error": "Le code est vide."}), 400

    fw = _resolve_active_framework()
    if "import tornado" in code or "from tornado" in code:
        fw = "tornado"
    elif "from fastapi" in code or "import fastapi" in code:
        fw = "fastapi"
    elif "from flask" in code or "import flask" in code:
        fw = "flask"

    _stop_live_python_process()

    try:
        runner_dir = _prepare_runner_dir(fw)
        with tempfile.NamedTemporaryFile("w", suffix=".py", dir=runner_dir, delete=False, encoding="utf-8") as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        preferred_port = {"tornado": 8889, "fastapi": 8001, "flask": 5001}.get(fw, 5001)
        assigned_port = _find_available_port(preferred_port)

        proc = subprocess.Popen(
            [sys.executable, "-u", tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=runner_dir,
            env={
                "PATH": os.environ.get("PATH", ""),
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUNBUFFERED": "1",
                "PORT": str(assigned_port),
            },
        )

        logs = []
        LIVE_PYTHON_PROCESS.update({
            "proc": proc,
            "tmp_path": tmp_path,
            "logs": logs,
            "fw": fw,
            "port": None,
            "routes": [],
        })

        def _reader_thread():
            try:
                for line in iter(proc.stdout.readline, ""):
                    if not line:
                        break
                    logs.append(line)
            except Exception:
                pass

        t = threading.Thread(target=_reader_thread, daemon=True)
        t.start()

        # Attendre jusqu'à 1.6s pour laisser le script finir (s'il est synchrone) ou démarrer sa boucle (IOLoop / Uvicorn / Flask)
        deadline = time.time() + 1.6
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            joined = "".join(logs)
            if any(marker in joined for marker in ("[BOUCLE ", "[SERVEUR ", "Uvicorn running on", "Running on http://")):
                time.sleep(0.25)
                break
            time.sleep(0.08)

        output_so_far = "".join(logs)
        is_running = proc.poll() is None

        if is_running:
            port, routes = _extract_routes_and_port(code, output_so_far, fw, default_port=assigned_port)
            LIVE_PYTHON_PROCESS["port"] = port
            LIVE_PYTHON_PROCESS["routes"] = routes
            return jsonify({
                "running": True,
                "pid": proc.pid,
                "port": port,
                "routes": routes,
                "framework": fw,
                "output": output_so_far,
                "error": "",
                "exit_code": 0,
            })

        exit_code = proc.returncode or 0
        _stop_live_python_process()
        return jsonify({
            "running": False,
            "output": output_so_far if exit_code == 0 else "",
            "error": output_so_far if exit_code != 0 else "",
            "exit_code": exit_code,
        })
    except Exception as exc:
        _stop_live_python_process()
        return jsonify({"running": False, "output": "", "error": str(exc), "exit_code": 1})


@app.route("/api/python/status", methods=["GET"])
def get_python_runner_status():
    proc = LIVE_PYTHON_PROCESS.get("proc")
    is_running = proc is not None and proc.poll() is None
    return jsonify({
        "running": is_running,
        "pid": proc.pid if is_running else None,
        "port": LIVE_PYTHON_PROCESS.get("port"),
        "routes": LIVE_PYTHON_PROCESS.get("routes", []),
        "framework": LIVE_PYTHON_PROCESS.get("fw", "flask"),
        "output": "".join(LIVE_PYTHON_PROCESS.get("logs", [])),
        "exit_code": 0 if is_running else (proc.returncode if proc else 0),
    })


@app.route("/api/python/probe", methods=["POST"])
def probe_live_python_server():
    proc = LIVE_PYTHON_PROCESS.get("proc")
    if proc is None or proc.poll() is not None:
        return jsonify({"erreur": "Aucune boucle serveur n'est actuellement active. Cliquez d'abord sur « Démarrer / Exécuter »."}), 400

    data = request.get_json(silent=True) or {}
    path = str(data.get("path", "/")).strip() or "/"
    if not path.startswith("/"):
        path = "/" + path
    port = LIVE_PYTHON_PROCESS.get("port") or 8889
    target_url = f"http://127.0.0.1:{port}{path}"

    try:
        req = urllib.request.Request(target_url, method="GET")
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            status_code = resp.status
            body = resp.read().decode("utf-8", errors="replace")
            content_type = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        status_code = e.code
        body = e.read().decode("utf-8", errors="replace")
        content_type = e.headers.get("Content-Type", "") if e.headers else ""
    except Exception as exc:
        return jsonify({"erreur": f"Erreur lors de l'appel à {target_url} : {exc}"}), 502

    time.sleep(0.15)
    LIVE_PYTHON_PROCESS["logs"].append(
        f"\n>>> [CLIENT SIMULATEUR -> GET {target_url}] Statut HTTP {status_code} ({content_type})\n"
        f"{body[:600].strip()}\n"
    )
    return jsonify({
        "running": proc.poll() is None,
        "status_code": status_code,
        "target_url": target_url,
        "response_body": body[:1000],
        "output": "".join(LIVE_PYTHON_PROCESS.get("logs", [])),
    })


@app.route("/api/python/stop", methods=["POST"])
def stop_python_snippet():
    proc = LIVE_PYTHON_PROCESS.get("proc")
    if proc is not None and proc.poll() is None:
        try:
            proc.send_signal(signal.SIGINT)
            proc.wait(timeout=0.5)
        except Exception:
            pass
    time.sleep(0.15)
    final_output = "".join(LIVE_PYTHON_PROCESS.get("logs", []))
    if "[Arrêt SIGINT / Ctrl+C envoyé depuis le simulateur]" not in final_output:
        final_output += "\n[SIMULATEUR] Signal SIGINT (Ctrl+C) envoyé : boucle serveur arrêtée proprement.\n"
    _stop_live_python_process()
    return jsonify({
        "running": False,
        "output": final_output,
        "exit_code": 0,
    })


# ==============================================================================
# 8. EXÉCUTEUR CURL EN DIRECT & EXPORT POSTMAN / REST CLIENT (.http)
# ==============================================================================
import shlex

@app.route("/api/curl/run", methods=["POST"])
def run_curl_command():
    data = request.get_json(silent=True) or {}
    raw_cmd = (data.get("command") or "").strip()
    if not raw_cmd:
        return jsonify({"output": "", "error": "Commande curl vide."}), 400

    # Normalisation des retours à la ligne (continuation backslash \)
    normalized = raw_cmd.replace("\\\r\n", " ").replace("\\\n", " ")
    try:
        tokens = shlex.split(normalized)
    except ValueError as err:
        return jsonify({"output": "", "error": f"Erreur de syntaxe des guillemets : {err}"}), 400

    if not tokens or tokens[0] != "curl":
        return jsonify({"output": "", "error": "La commande doit commencer par 'curl'."}), 400

    # Sécurité : autoriser uniquement les options d'inspection HTTP et les URLs locales
    safe_args = ["curl", "-sS"]
    has_i_or_v = any(t in ("-i", "--include", "-v", "--verbose", "-I", "--head") for t in tokens[1:])
    if not has_i_or_v:
        safe_args.append("-i")

    i = 1
    while i < len(tokens):
        tok = tokens[i]
        if tok in (
            "-i", "--include", "-v", "--verbose", "-s", "--silent", "-S",
            "-I", "--head", "-G", "--get", "-k", "--insecure", "-L", "--location"
        ):
            safe_args.append(tok)
            i += 1
        elif tok in (
            "-X", "--request", "-H", "--header", "-d", "--data", "--data-raw",
            "--data-urlencode", "--json", "-F", "--form", "-w", "--write-out", "-A", "--user-agent",
            "-u", "--user", "-m", "--max-time", "--connect-timeout"
        ):
            if i + 1 >= len(tokens):
                return jsonify({"output": "", "error": f"Argument manquant après '{tok}'."}), 400
            if tok in ("-F", "--form") and "@" in tokens[i + 1]:
                return jsonify({"output": "", "error": "Lecture de fichier local (@fichier) désactivée dans le bac à sable web."}), 400
            safe_args.extend([tok, tokens[i + 1]])
            i += 2
        elif tok.startswith("http://127.0.0.1:5000") or tok.startswith("http://localhost:5000") or tok.startswith("/api/"):
            url_target = tok if tok.startswith("http") else f"http://127.0.0.1:5000{tok}"
            safe_args.append(url_target)
            i += 1
        else:
            return jsonify({
                "output": "",
                "error": f"Argument ou URL externe non exécutable dans le bac à sable local : '{tok}'. Copiez cette commande dans votre terminal système ou ciblez http://127.0.0.1:5000/api/..."
            }), 400

    safe_args.extend(["-w", "\n\n--- [Statut HTTP: %{http_code} | Temps: %{time_total}s | Octets reçus: %{size_download}] ---"])

    try:
        proc = subprocess.run(
            safe_args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5
        )
        out_lines = [
            line for line in proc.stdout.splitlines()
            if not line.startswith("X-Flask-Handler-Code:") and not line.startswith("X-Flask-Trace-Steps:")
        ]
        out = "\n".join(out_lines)
        if proc.stderr:
            err_lines = [
                line for line in proc.stderr.splitlines()
                if "X-Flask-Handler-Code:" not in line and "X-Flask-Trace-Steps:" not in line
            ]
            out = (out + "\n" + "\n".join(err_lines)).strip()
        return jsonify({"output": out, "executed": " ".join(safe_args[:-2])}), 200
    except Exception as exc:
        return jsonify({"output": "", "error": str(exc)}), 500


@app.route("/api/download/postman-collection")
def download_postman_collection():
    collection = {
        "info": {
            "name": "ISGP Bootcamp — Développement d'APIs et Services Web (Flask)",
            "_postman_id": "isgp-api-bootcamp-2026",
            "description": "Collection officielle d'exercices et de tests HTTP pour le Bootcamp ISGP (CRUD, Pagination, X-API-Key, Bearer Token, Rate Limiting 429).",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "variable": [
            {"key": "base_url", "value": "http://127.0.0.1:5000", "type": "string"},
            {"key": "bearer_token", "value": "", "type": "string"},
            {"key": "api_key", "value": "isgp-secret-2026", "type": "string"}
        ],
        "item": [
            {
                "name": "1. GET — Lister les formations (avec Pagination & Tri)",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Accept", "value": "application/json"}],
                    "url": {
                        "raw": "{{base_url}}/api/sandbox/formations?page=1&limit=5&tri=duree_jours&ordre=desc",
                        "host": ["{{base_url}}"],
                        "path": ["api", "sandbox", "formations"],
                        "query": [
                            {"key": "page", "value": "1"},
                            {"key": "limit", "value": "5"},
                            {"key": "tri", "value": "duree_jours"},
                            {"key": "ordre", "value": "desc"}
                        ]
                    }
                }
            },
            {
                "name": "2. POST — Créer une nouvelle formation (201 Created)",
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "titre": "Sécurité des APIs & Tests Postman",
                            "formateur": "Intervenant ISGP",
                            "duree_jours": 5,
                            "salle": "Salle B"
                        }, indent=2, ensure_ascii=False)
                    },
                    "url": {"raw": "{{base_url}}/api/sandbox/formations", "host": ["{{base_url}}"], "path": ["api", "sandbox", "formations"]}
                }
            },
            {
                "name": "3. PUT — Mettre à jour la formation #1",
                "request": {
                    "method": "PUT",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "titre": "Architecture API REST & Flask (Niveau Avancé)",
                            "duree_jours": 5,
                            "salle": "Salle Conférence"
                        }, indent=2, ensure_ascii=False)
                    },
                    "url": {"raw": "{{base_url}}/api/sandbox/formations/1", "host": ["{{base_url}}"], "path": ["api", "sandbox", "formations", "1"]}
                }
            },
            {
                "name": "4. PATCH — Modification partielle de la formation #1",
                "request": {
                    "method": "PATCH",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({"salle": "Amphithéâtre ISGP"}, indent=2, ensure_ascii=False)
                    },
                    "url": {"raw": "{{base_url}}/api/sandbox/formations/1", "host": ["{{base_url}}"], "path": ["api", "sandbox", "formations", "1"]}
                }
            },
            {
                "name": "5. Auth Machine — GET /admin-stats avec X-API-Key",
                "request": {
                    "method": "GET",
                    "header": [{"key": "X-API-Key", "value": "{{api_key}}"}],
                    "url": {"raw": "{{base_url}}/api/sandbox/admin-stats", "host": ["{{base_url}}"], "path": ["api", "sandbox", "admin-stats"]}
                }
            },
            {
                "name": "6. Auth Token (Étape 1) — POST /auth/token (Émettre un Bearer Token)",
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}, indent=2)
                    },
                    "url": {"raw": "{{base_url}}/api/sandbox/auth/token", "host": ["{{base_url}}"], "path": ["api", "sandbox", "auth/token"]}
                }
            },
            {
                "name": "7. Auth Token (Étape 2) — GET /auth/profil avec Authorization: Bearer",
                "request": {
                    "method": "GET",
                    "header": [{"key": "Authorization", "value": "Bearer {{bearer_token}}"}],
                    "url": {"raw": "{{base_url}}/api/sandbox/auth/profil", "host": ["{{base_url}}"], "path": ["api", "sandbox", "auth", "profil"]}
                }
            },
            {
                "name": "8. Rate Limiting — GET /ratelimit-demo (Tester 4 fois pour déclencher 429)",
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": {"raw": "{{base_url}}/api/sandbox/ratelimit-demo", "host": ["{{base_url}}"], "path": ["api", "sandbox", "ratelimit-demo"]}
                }
            }
        ]
    }
    return Response(
        json.dumps(collection, indent=2, ensure_ascii=False),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=isgp_api_bootcamp.postman_collection.json"}
    )


@app.route("/api/download/http-requests")
def download_http_requests_file():
    content = """# ============================================================================
# ISGP — Fichier de requêtes HTTP pour VS Code / Antigravity (Extension REST Client)
# Instructions : Ouvrez ce fichier (.http) dans VS Code et cliquez sur "Send Request"
#                au-dessus de chaque bloc séparé par ###
# ============================================================================

@baseUrl = http://127.0.0.1:5000
@apiKey = isgp-secret-2026

### 1. Vérifier l'état du service (GET 200 OK)
GET {{baseUrl}}/api/sandbox/bonjour
Accept: application/json

### 2. Lister les formations avec Pagination, Filtrage et Tri
GET {{baseUrl}}/api/sandbox/formations?page=1&limit=3&tri=duree_jours&ordre=desc
Accept: application/json

### 3. Créer une nouvelle formation (POST 201 Created)
POST {{baseUrl}}/api/sandbox/formations
Content-Type: application/json

{
  "titre": "Tests d'APIs avec curl et REST Client",
  "formateur": "Formateur ISGP",
  "duree_jours": 4,
  "salle": "Labo 2"
}

### 4. Modifier partiellement la formation #1 (PATCH 200 OK)
PATCH {{baseUrl}}/api/sandbox/formations/1
Content-Type: application/json

{
  "salle": "Salle Conférence A"
}

### 5. Authentification par Clé API (X-API-Key)
GET {{baseUrl}}/api/sandbox/admin-stats
X-API-Key: {{apiKey}}

### 6. Obtenir un Bearer Token signé (POST /auth/token)
POST {{baseUrl}}/api/sandbox/auth/token
Content-Type: application/json

{
  "identifiant": "stagiaire",
  "mot_de_passe": "isgp2026"
}

### 7. Tester le Rate Limiter (Exécuter 4 fois en moins de 20s -> HTTP 429)
GET {{baseUrl}}/api/sandbox/ratelimit-demo
"""
    return Response(
        content,
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=isgp_api_bootcamp.http"}
    )


def build_sandbox_openapi_spec():
    """Construit la spécification officielle OpenAPI 3.0.3 de toutes les routes du laboratoire ISGP."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "ISGP — API Laboratoire Bootcamp (REST, AuthN/AuthZ, SQLite & Rate Limit)",
            "version": "1.0.0",
            "description": (
                "Spécification officielle **OpenAPI 3.0.3** des routes d'entraînement du Bootcamp ISGP. "
                "Utilisez le bouton **Authorize** ci-dessous pour configurer votre jeton `Bearer` "
                "(obtenu via `POST /api/sandbox/auth/token`) ou la clé `X-API-Key: isgp-secret-2026`, "
                "puis cliquez sur **Try it out** sur n'importe quelle route."
            ),
            "contact": {"name": "ISGP — Développement d'APIs et services web"},
        },
        "servers": [
            {"url": "http://127.0.0.1:5000", "description": "Serveur Laboratoire Local"}
        ],
        "tags": [
            {"name": "1. Diagnostic & Calculs", "description": "Routes de test et paramètres Query String"},
            {"name": "2. Catalogue Formations (CRUD SQLite)", "description": "Opérations GET, POST, PUT, PATCH, DELETE avec Pagination et Idempotence"},
            {"name": "3. Authentification (AuthN — 401)", "description": "Émission et vérification de Bearer Tokens signés et X-API-Key"},
            {"name": "4. Autorisation (AuthZ — 403, RBAC, Scopes, BOLA)", "description": "Contrôle des rôles, scopes OAuth2 et propriété d'objet"},
            {"name": "5. Résilience & Quotas (429)", "description": "Limitation de débit (Rate Limiting) par fenêtre glissante"},
        ],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT / TimedSerializer",
                    "description": "Collez ici le jeton `access_token` obtenu depuis `POST /api/sandbox/auth/token`.",
                },
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "Clé d'API machine-à-machine. Valeur de démonstration : `isgp-secret-2026`",
                },
            },
            "schemas": {
                "Formation": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "titre": {"type": "string", "example": "Architecture API REST & Flask"},
                        "formateur": {"type": "string", "example": "Équipe Pédagogique ISGP"},
                        "duree_jours": {"type": "integer", "example": 5},
                        "salle": {"type": "string", "example": "Salle A"},
                    },
                },
                "FormationCreateInput": {
                    "type": "object",
                    "required": ["titre", "duree_jours"],
                    "properties": {
                        "titre": {"type": "string", "minLength": 3, "example": "Sécurité des APIs & OpenAPI 3.0"},
                        "formateur": {"type": "string", "example": "Intervenant ISGP"},
                        "duree_jours": {"type": "integer", "minimum": 1, "maximum": 30, "example": 5},
                        "salle": {"type": "string", "example": "Salle B"},
                    },
                },
                "LoginInput": {
                    "type": "object",
                    "required": ["identifiant", "mot_de_passe"],
                    "properties": {
                        "identifiant": {
                            "type": "string",
                            "enum": ["stagiaire", "formateur", "directeur"],
                            "example": "stagiaire",
                            "description": "Comptes disponibles : stagiaire (rôle stagiaire), formateur (rôle formateur), directeur (rôle admin)",
                        },
                        "mot_de_passe": {"type": "string", "example": "isgp2026"},
                    },
                },
            },
        },
        "paths": {
            "/api/sandbox/bonjour": {
                "get": {
                    "tags": ["1. Diagnostic & Calculs"],
                    "summary": "Vérifier la disponibilité du serveur (Healthcheck simple)",
                    "responses": {"200": {"description": "Service opérationnel"}},
                }
            },
            "/api/sandbox/calcul-tva": {
                "get": {
                    "tags": ["1. Diagnostic & Calculs"],
                    "summary": "Calculer un montant TTC via Query Parameters (?ht=...&taux=...)",
                    "parameters": [
                        {"name": "ht", "in": "query", "schema": {"type": "number", "default": 2500}, "description": "Montant Hors Taxes"},
                        {"name": "taux", "in": "query", "schema": {"type": "number", "default": 19}, "description": "Taux de TVA (%)"},
                    ],
                    "responses": {"200": {"description": "Détail du calcul HT, TVA et TTC"}},
                }
            },
            "/api/sandbox/formations": {
                "get": {
                    "tags": ["2. Catalogue Formations (CRUD SQLite)"],
                    "summary": "Lister les formations (avec Pagination, Filtrage et Tri)",
                    "parameters": [
                        {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                        {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 10}},
                        {"name": "salle", "in": "query", "schema": {"type": "string"}, "description": "Filtrer par salle (ex: Salle A)"},
                        {"name": "min_jours", "in": "query", "schema": {"type": "integer"}, "description": "Durée minimale en jours"},
                        {"name": "tri", "in": "query", "schema": {"type": "string", "enum": ["id", "duree_jours", "titre"], "default": "id"}},
                        {"name": "ordre", "in": "query", "schema": {"type": "string", "enum": ["asc", "desc"], "default": "asc"}},
                    ],
                    "responses": {"200": {"description": "Enveloppe paginée {meta, data}"}},
                },
                "post": {
                    "tags": ["2. Catalogue Formations (CRUD SQLite)"],
                    "summary": "Créer une nouvelle formation (Validation RFC 7807 + Idempotency-Key)",
                    "parameters": [
                        {
                            "name": "Idempotency-Key",
                            "in": "header",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Clé UUID optionnelle évitant les doublons en cas de réessai réseau",
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/FormationCreateInput"}}},
                    },
                    "responses": {
                        "201": {"description": "Formation créée en base SQLite"},
                        "422": {"description": "Erreur de validation métier (Format RFC 7807)"},
                    },
                },
            },
            "/api/sandbox/formations/{formation_id}": {
                "get": {
                    "tags": ["2. Catalogue Formations (CRUD SQLite)"],
                    "summary": "Consulter une formation par son ID",
                    "parameters": [{"name": "formation_id", "in": "path", "required": True, "schema": {"type": "integer", "default": 1}}],
                    "responses": {"200": {"description": "Formation trouvée"}, "404": {"description": "Formation introuvable"}},
                },
                "put": {
                    "tags": ["2. Catalogue Formations (CRUD SQLite)"],
                    "summary": "Remplacer ou modifier une formation existante",
                    "parameters": [{"name": "formation_id", "in": "path", "required": True, "schema": {"type": "integer", "default": 1}}],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/FormationCreateInput"}}},
                    },
                    "responses": {"200": {"description": "Formation mise à jour"}, "404": {"description": "Formation introuvable"}},
                },
                "patch": {
                    "tags": ["2. Catalogue Formations (CRUD SQLite)"],
                    "summary": "Modifier partiellement certains champs d'une formation",
                    "parameters": [{"name": "formation_id", "in": "path", "required": True, "schema": {"type": "integer", "default": 1}}],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"type": "object", "example": {"salle": "Salle Conférence"}}}},
                    },
                    "responses": {"200": {"description": "Modification partielle appliquée"}, "404": {"description": "Formation introuvable"}},
                },
                "delete": {
                    "tags": ["2. Catalogue Formations (CRUD SQLite)"],
                    "summary": "Supprimer une formation par son ID",
                    "parameters": [{"name": "formation_id", "in": "path", "required": True, "schema": {"type": "integer", "default": 1}}],
                    "responses": {"200": {"description": "Formation supprimée"}, "404": {"description": "Formation introuvable"}},
                },
            },
            "/api/sandbox/auth/token": {
                "post": {
                    "tags": ["3. Authentification (AuthN — 401)"],
                    "summary": "Émettre un Bearer Token signé (stagiaire, formateur ou directeur)",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoginInput"}}},
                    },
                    "responses": {
                        "200": {"description": "Jeton signé émis avec rôle et scopes OAuth2"},
                        "401": {"description": "Identifiants invalides"},
                    },
                }
            },
            "/api/sandbox/auth/profil": {
                "get": {
                    "tags": ["3. Authentification (AuthN — 401)"],
                    "summary": "Consulter le profil décodé depuis le Bearer Token",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {"description": "Identité vérifiée avec succès"},
                        "401": {"description": "Jeton manquant, expiré ou signature invalide"},
                    },
                }
            },
            "/api/sandbox/admin-stats": {
                "get": {
                    "tags": ["3. Authentification (AuthN — 401)"],
                    "summary": "Consulter les statistiques partenaires (Protégé par X-API-Key)",
                    "security": [{"ApiKeyAuth": []}],
                    "responses": {
                        "200": {"description": "Clé X-API-Key valide (comparaison hmac.compare_digest)"},
                        "401": {"description": "Clé X-API-Key absente ou invalide"},
                    },
                }
            },
            "/api/sandbox/authz-demo": {
                "get": {
                    "tags": ["4. Autorisation (AuthZ — 403, RBAC, Scopes, BOLA)"],
                    "summary": "Démonstration complète : 401 (AuthN) vs 403 (AuthZ : RBAC, Scopes & Anti-BOLA)",
                    "security": [{"BearerAuth": []}],
                    "parameters": [
                        {
                            "name": "dossier_cible",
                            "in": "query",
                            "schema": {"type": "string", "enum": ["stagiaire", "formateur"]},
                            "description": "Tester l'accès à un dossier pour observer la protection Anti-BOLA (OWASP #1)",
                        }
                    ],
                    "responses": {
                        "200": {"description": "AuthN réussie ET AuthZ réussie (rôle admin ou propriétaire légitime)"},
                        "401": {"description": "Échec AuthN : Appelant non authentifié"},
                        "403": {"description": "Échec AuthZ : Identité connue mais rôle/scope insuffisant ou tentative BOLA bloquée"},
                    },
                }
            },
            "/api/sandbox/formulaire-formation": {
                "post": {
                    "tags": ["2. Catalogue Formations (CRUD SQLite)"],
                    "summary": "Créer une formation via Formulaire HTML (request.form) ou JSON (Hybride)",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/x-www-form-urlencoded": {
                                "schema": {"$ref": "#/components/schemas/FormationCreateInput"}
                            },
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/FormationCreateInput"}
                            },
                        },
                    },
                    "responses": {
                        "201": {"description": "Formation créée (via request.form ou request.get_json)"},
                        "422": {"description": "Champ obligatoire manquant"},
                    },
                }
            },
            "/api/sandbox/ratelimit-demo": {
                "get": {
                    "tags": ["5. Résilience & Quotas (429)"],
                    "summary": "Tester le limiteur de débit (Max 3 requêtes / 20 secondes)",
                    "responses": {
                        "200": {"description": "Requête acceptée (voir en-tête X-RateLimit-Remaining)"},
                        "429": {"description": "Quota dépassé (Too Many Requests + en-tête Retry-After)"},
                    },
                }
            },
        },
    }


@app.route("/api/openapi.json", methods=["GET"])
def api_openapi_json():
    """Expose le contrat OpenAPI 3.0.3 en direct."""
    handler_code = (
        '@app.route("/api/openapi.json", methods=["GET"])\n'
        "def api_openapi_json():\n"
        "    return jsonify(build_sandbox_openapi_spec()), 200"
    )
    steps = [
        "1. Génération du contrat normalisé OpenAPI 3.0.3 (info, servers, paths, components).",
        "2. Exposition des schémas de sécurité BearerAuth (JWT) et ApiKeyAuth (X-API-Key).",
        "3. Envoi du document JSON consommé par Swagger UI (/api/docs) et Postman (200 OK).",
    ]
    return make_traced_response(build_sandbox_openapi_spec(), 200, handler_code, steps)


@app.route("/api/download/openapi-spec", methods=["GET"])
def download_openapi_spec():
    """Télécharge le contrat OpenAPI 3.0.3 sous forme de fichier .json."""
    return Response(
        json.dumps(build_sandbox_openapi_spec(), indent=2, ensure_ascii=False),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=isgp_api_bootcamp.openapi.json"},
    )


@app.route("/api/docs", methods=["GET"])
def swagger_ui_portal():
    """Portail interactif Swagger UI rendu via le template Jinja2 templates/swagger_ui.html."""
    return render_template(
        "swagger_ui.html",
        page_title="Swagger UI — ISGP API Bootcamp (OpenAPI 3.0.3)",
        header_title="ISGP — Portail Interactif Swagger UI (OpenAPI 3.0.3)",
        openapi_url="/api/openapi.json",
        demo_api_key="isgp-secret-2026",
    )


@app.route("/sandbox/formulaire-jinja", methods=["GET", "POST"])
def sandbox_formulaire_jinja():
    """Atelier interactif illustrant le traitement d'un formulaire HTML (request.form) et le rendu Jinja2."""
    erreurs = []
    message_succes = None
    raw_form_payload = None
    valeurs_saisies = {}

    if request.method == "POST":
        raw_form_payload = request.get_data(as_text=True)
        titre = request.form.get("titre", "").strip()
        formateur = request.form.get("formateur", "Intervenant ISGP").strip() or "Intervenant ISGP"
        salle = request.form.get("salle", "Salle A").strip() or "Salle A"
        duree_str = request.form.get("duree_jours", "")
        valeurs_saisies = {
            "titre": titre,
            "formateur": formateur,
            "duree_jours": duree_str,
            "salle": salle,
        }

        try:
            duree_jours = int(duree_str)
        except (TypeError, ValueError):
            duree_jours = 0

        if len(titre) < 3:
            erreurs.append("L'intitulé de la formation ('titre') doit comporter au moins 3 caractères.")
        if not (1 <= duree_jours <= 30):
            erreurs.append("La durée ('duree_jours') doit être un entier compris entre 1 et 30 jours.")

        if not erreurs:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO formations (titre, formateur, duree_jours, salle) VALUES (?, ?, ?, ?)",
                (titre, formateur, duree_jours, salle),
            )
            conn.commit()
            new_id = cur.lastrowid
            conn.close()
            message_succes = f"La formation « {titre} » a été ajoutée en base SQLite (ID #{new_id}) via request.form !"
            valeurs_saisies = {}

    conn = get_db()
    rows = conn.execute("SELECT * FROM formations ORDER BY id DESC").fetchall()
    conn.close()
    formations = [dict(r) for r in rows]

    status_code = 422 if erreurs else (201 if message_succes else 200)
    return render_template(
        "demo_formulaire_jinja.html",
        formations=formations,
        erreurs=erreurs,
        message_succes=message_succes,
        raw_form_payload=raw_form_payload,
        valeurs_saisies=valeurs_saisies,
    ), status_code


@app.route("/api/sandbox/formulaire-formation", methods=["POST"])
def api_sandbox_formulaire_formation():
    """Endpoint démontrant la lecture de données de formulaire (request.form) vs JSON."""
    content_type = request.headers.get("Content-Type", "")
    if request.is_json:
        source = request.get_json(silent=True) or {}
        mode_detecte = "Payload JSON (request.get_json)"
    else:
        source = request.form
        mode_detecte = "Formulaire HTML (request.form — application/x-www-form-urlencoded)"

    titre = str(source.get("titre", "")).strip()
    formateur = str(source.get("formateur", "Intervenant ISGP")).strip() or "Intervenant ISGP"
    salle = str(source.get("salle", "Salle A")).strip() or "Salle A"
    try:
        duree_jours = int(source.get("duree_jours", 5))
    except (TypeError, ValueError):
        duree_jours = 5

    handler_code = (
        '@app.route("/api/sandbox/formulaire-formation", methods=["POST"])\n'
        "def traiter_formulaire():\n"
        '    # Lecture via request.form (ou request.get_json en mode hybride)\n'
        '    titre = request.form.get("titre", "").strip()\n'
        '    duree_jours = request.form.get("duree_jours", default=5, type=int)\n'
        '    salle = request.form.get("salle", "Salle A").strip()'
    )

    if len(titre) < 3:
        steps = [
            f"1. Réception d'un formulaire HTTP ({content_type or 'application/x-www-form-urlencoded'}).",
            "2. Lecture de request.form.get('titre') : titre absent ou trop court (< 3 caractères).",
            "3. Rejet avec le statut 422 Unprocessable Entity.",
        ]
        return make_traced_response(
            {
                "erreur": "Champ de formulaire 'titre' manquant ou trop court dans request.form.",
                "astuce_curl": 'curl -i -X POST http://127.0.0.1:5000/api/sandbox/formulaire-formation -d "titre=Flask+Jinja2&duree_jours=4&salle=Salle+B"',
                "champs_recus_dans_request_form": dict(request.form),
            },
            422,
            handler_code,
            steps,
        )

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO formations (titre, formateur, duree_jours, salle) VALUES (?, ?, ?, ?)",
        (titre, formateur, duree_jours, salle),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    steps = [
        f"1. Décodage du corps ({mode_detecte}).",
        f"2. Extraction de titre='{titre}', duree_jours={duree_jours}, salle='{salle}'.",
        f"3. Insertion SQL paramétrée réussie (ID #{new_id}) et retour 201 Created.",
    ]
    return make_traced_response(
        {
            "message": "Formulaire HTML traité avec succès via request.form",
            "mode_detecte": mode_detecte,
            "content_type_recu": content_type,
            "donnees_extraites_de_request_form": {
                "id": new_id,
                "titre": titre,
                "formateur": formateur,
                "duree_jours": duree_jours,
                "salle": salle,
            },
        },
        201,
        handler_code,
        steps,
    )


# ==============================================================================
# 10. LABORATOIRE NGINX LOAD BALANCER (4 INSTANCES PAR FRAMEWORK + STATIQUES)
# ==============================================================================
FRAMEWORK_LABELS = {"flask": "Flask", "fastapi": "FastAPI", "tornado": "Tornado"}


def _build_initial_nginx_state(fw: str) -> dict:
    return {
        "framework": fw,
        "algorithm": "round_robin",
        "rr_index": 0,
        "static_requests_served": 0,
        "dynamic_requests_proxied": 0,
        "uploads_offloaded": 0,
        "rejected_413_edge": 0,
        "x_accel_downloads": 0,
        "errors_502": 0,
        "nodes": [
            {"id": f"{fw}-node-1", "port": 8001, "addr": "127.0.0.1:8001", "pid": 24101, "weight": 3, "status": "UP", "requests": 0, "active_conns": 1},
            {"id": f"{fw}-node-2", "port": 8002, "addr": "127.0.0.1:8002", "pid": 24102, "weight": 1, "status": "UP", "requests": 0, "active_conns": 2},
            {"id": f"{fw}-node-3", "port": 8003, "addr": "127.0.0.1:8003", "pid": 24103, "weight": 1, "status": "UP", "requests": 0, "active_conns": 0},
            {"id": f"{fw}-node-4", "port": 8004, "addr": "127.0.0.1:8004", "pid": 24104, "weight": 1, "status": "UP", "requests": 0, "active_conns": 1},
        ],
        "logs": [
            f'[INIT] Nginx Master Process démarré sur 0.0.0.0:80 -> upstream isgp_{fw}_cluster (:8001..8004) + /static/ + Upload Offload ($request_body_file) + X-Accel-Redirect'
        ],
    }


NGINX_CLUSTER_STATES = {fw: _build_initial_nginx_state(fw) for fw in VALID_FRAMEWORKS}


def _read_cluster_file(fw: str, filename: str) -> str:
    fw_path = os.path.join(ROOT_DIR, f"{fw}-version", "deploy_nginx_cluster", filename)
    if os.path.exists(fw_path):
        with open(fw_path, encoding="utf-8") as f:
            return f.read().strip()
    fallback_path = os.path.join(ROOT_DIR, "deploy_nginx_cluster", filename)
    if os.path.exists(fallback_path):
        with open(fallback_path, encoding="utf-8") as f:
            return f.read().strip()
    return ""


@app.route("/api/nginx-cluster/state", methods=["GET"])
def get_nginx_cluster_state():
    fw = _resolve_active_framework()
    state = NGINX_CLUSTER_STATES.get(fw, NGINX_CLUSTER_STATES["flask"])
    return jsonify({
        "framework": fw,
        "state": state,
        "files": {
            "nginx_conf": _read_cluster_file(fw, "nginx_isgp_cluster.conf"),
            "instance_py": _read_cluster_file(fw, f"instance_{fw}.py"),
            "start_sh": _read_cluster_file(fw, "start_4_instances.sh"),
            "docker_compose": _read_cluster_file(fw, "docker-compose.yml"),
        },
    }), 200


@app.route("/api/nginx-cluster/toggle-node", methods=["POST"])
def toggle_nginx_cluster_node():
    fw = _resolve_active_framework()
    state = NGINX_CLUSTER_STATES.get(fw, NGINX_CLUSTER_STATES["flask"])
    data = request.get_json(silent=True) or {}
    port = int(data.get("port", 0))
    now_str = datetime.now().strftime("%H:%M:%S")
    for n in state["nodes"]:
        if n["port"] == port:
            n["status"] = "DOWN" if n["status"] == "UP" else "UP"
            etat_txt = (
                f"[{now_str}] [NGINX HEALTHCHECK] Instance {n['id']} ({n['addr']}) marquée {n['status']} "
                + ("(max_fails=3 atteint -> trafic basculé sur les instances restantes)" if n["status"] == "DOWN" else "(réintégrée dans le pool upstream)")
            )
            state["logs"].insert(0, etat_txt)
            state["logs"] = state["logs"][:35]
            break
    return jsonify({"state": state}), 200


@app.route("/api/nginx-cluster/reset", methods=["POST"])
def reset_nginx_cluster_state():
    fw = _resolve_active_framework()
    state = NGINX_CLUSTER_STATES.get(fw, NGINX_CLUSTER_STATES["flask"])
    fw_label = FRAMEWORK_LABELS.get(fw, "Python")
    state["rr_index"] = 0
    state["static_requests_served"] = 0
    state["dynamic_requests_proxied"] = 0
    state["uploads_offloaded"] = 0
    state["rejected_413_edge"] = 0
    state["x_accel_downloads"] = 0
    state["errors_502"] = 0
    for idx, n in enumerate(state["nodes"]):
        n["status"] = "UP"
        n["requests"] = 0
        n["active_conns"] = idx % 2
    state["logs"] = [
        f"[{datetime.now().strftime('%H:%M:%S')}] [RESET] Compteurs remis à zéro et les 4 instances {fw_label} (8001..8004) sont UP."
    ]
    return jsonify({"state": state}), 200


@app.route("/api/nginx-cluster/simulate", methods=["POST"])
def simulate_nginx_cluster_requests():
    fw = _resolve_active_framework()
    state = NGINX_CLUSTER_STATES.get(fw, NGINX_CLUSTER_STATES["flask"])
    fw_label = FRAMEWORK_LABELS.get(fw, "Python")
    data = request.get_json(silent=True) or {}
    req_type = data.get("type", "dynamic")  # "dynamic" (/api/v1/formations) ou "static" (/static/styles.css)
    count = min(20, max(1, int(data.get("count", 1))))
    algorithm = data.get("algorithm", state["algorithm"])
    client_ip = data.get("client_ip", "197.204.12.88").strip() or "197.204.12.88"
    state["algorithm"] = algorithm

    last_decision = None
    now_str = datetime.now().strftime("%H:%M:%S")

    for i in range(count):
        if req_type == "static":
            path = "/static/styles.css" if i % 2 == 0 else "/static/app.js"
            state["static_requests_served"] += 1
            log_line = (
                f'{client_ip} - [{now_str}] "GET {path} HTTP/1.1" status=200 '
                f'served_by=Nginx-Direct-Static-Sendfile (0 instance {fw_label} sollicitée) total_time=0.0004s'
            )
            state["logs"].insert(0, log_line)
            last_decision = {
                "type": "static",
                "path": path,
                "status": 200,
                "handled_by": "Nginx (location /static/ -> sendfile on)",
                "flask_called": False,
                "latency_ms": 0.4,
            }
        elif req_type == "upload_413":
            path = "/api/v1/upload-offload"
            state["rejected_413_edge"] = state.get("rejected_413_edge", 0) + 1
            log_line = (
                f'{client_ip} - [{now_str}] "POST {path} HTTP/1.1 (Content-Length: 62914560)" status=413 '
                f'edge_shield="client_max_body_size 25M exceeded" (0 octet transmis à {fw_label} !) total_time=0.0001s'
            )
            state["logs"].insert(0, log_line)
            last_decision = {
                "type": "upload_413",
                "path": path,
                "status": 413,
                "handled_by": "Bouclier Nginx Edge (client_max_body_size -> 413 en 0.1 ms, 0% RAM Python)",
                "flask_called": False,
                "latency_ms": 0.1,
            }
        else:
            path = (
                "/api/v1/upload-offload"
                if req_type == "upload_offload"
                else ("/api/v1/exports/certificat_2026" if req_type == "x_accel" else "/api/v1/formations")
            )
            up_nodes = [n for n in state["nodes"] if n["status"] == "UP"]
            if not up_nodes:
                state["errors_502"] += 1
                log_line = (
                    f'{client_ip} - [{now_str}] "GET {path} HTTP/1.1" status=502 '
                    f'error="no live upstreams while connecting to upstream isgp_{fw}_cluster"'
                )
                state["logs"].insert(0, log_line)
                last_decision = {
                    "type": req_type,
                    "path": path,
                    "status": 502,
                    "handled_by": f"Erreur 502 Bad Gateway (Les 4 instances {fw_label} sont DOWN !)",
                    "flask_called": False,
                    "latency_ms": 1.2,
                }
                continue

            if algorithm == "least_conn":
                chosen = min(up_nodes, key=lambda n: (n["active_conns"], n["requests"]))
                chosen["active_conns"] = (chosen["active_conns"] + 1) % 4
            elif algorithm == "ip_hash":
                hash_val = sum(ord(c) for c in client_ip)
                chosen = up_nodes[hash_val % len(up_nodes)]
            elif algorithm == "weighted":
                weighted_pool = []
                for n in up_nodes:
                    weighted_pool.extend([n] * n.get("weight", 1))
                idx = state["rr_index"] % len(weighted_pool)
                chosen = weighted_pool[idx]
                state["rr_index"] += 1
            else:
                idx = state["rr_index"] % len(up_nodes)
                chosen = up_nodes[idx]
                state["rr_index"] += 1

            chosen["requests"] += 1
            state["dynamic_requests_proxied"] += 1

            if req_type == "upload_offload":
                state["uploads_offloaded"] = state.get("uploads_offloaded", 0) + 1
                spool_id = 1000 + state["uploads_offloaded"]
                log_line = (
                    f'{client_ip} - [{now_str}] "POST {path} HTTP/1.1 (18 Mo Mobile 4G: 5.8s absorbés par Nginx C)" '
                    f'status=201 spool=/var/spool/isgp_nginx_uploads/{spool_id} body_sent_to_python=0B '
                    f'upstream_node={chosen["addr"]} ({chosen["id"]}) upstream_time=0.0009s total_time=5.801s'
                )
            elif req_type == "x_accel":
                state["x_accel_downloads"] = state.get("x_accel_downloads", 0) + 1
                log_line = (
                    f'{client_ip} - [{now_str}] "GET {path} HTTP/1.1" status=200 '
                    f'auth_by={chosen["addr"]} (upstream_time=0.0006s) -> X-Accel-Redirect=/_protected_exports/certificat_2026.pdf '
                    f'(18 Mo streamés par Nginx sendfile internal !)'
                )
            else:
                log_line = (
                    f'{client_ip} - [{now_str}] "GET {path} HTTP/1.1" status=200 '
                    f'upstream_node={chosen["addr"]} ({chosen["id"]}, PID {chosen["pid"]}) upstream_time=0.008s'
                )
            state["logs"].insert(0, log_line)
            last_decision = {
                "type": req_type,
                "path": path,
                "status": 201 if req_type == "upload_offload" else 200,
                "handled_by": f'{chosen["id"]} ({chosen["addr"]}, PID {chosen["pid"]})',
                "node_port": chosen["port"],
                "flask_called": True,
                "latency_ms": 0.9 if req_type == "upload_offload" else (0.6 if req_type == "x_accel" else 8.2),
            }

    state["logs"] = state["logs"][:35]
    return jsonify({"state": state, "last_decision": last_decision}), 200


# ==============================================================================
# LABORATOIRE DE VERSIONING D'API : /api/v1 (Dépréciée RFC 8594) vs /api/v2
# ==============================================================================

@app.route("/api/v1/sandbox/formations", methods=["GET"])
def sandbox_formations_v1_deprecated():
    """
    Contrat historique v1 (En phase de dépréciation selon IETF RFC 8594) :
    - Schéma plat : "intitule" (str) et "duree" (int)
    - En-têtes HTTP RFC 8594 : Deprecation, Sunset et Link (successor-version)
    """
    db = get_db()
    rows = db.execute("SELECT id, titre, duree_jours, salle FROM formations ORDER BY id ASC").fetchall()
    items_v1 = [
        {
            "id": r["id"],
            "intitule": r["titre"],       # Ancien nom du champ en v1
            "duree": r["duree_jours"],    # Entier simple en v1 (ex: 5)
            "salle": r["salle"],
        }
        for r in rows
    ]
    resp = jsonify({
        "version": "v1",
        "statut_version": "DEPRECATED (Transition vers /api/v2/sandbox/formations)",
        "avertissement_migration": (
            "Cette version v1 reste opérationnelle pour ne pas casser les clients existants, "
            "mais sera éteinte (410 Gone) après la date Sunset. Migrez vers /api/v2/sandbox/formations."
        ),
        "items": items_v1,
    })
    resp.headers["X-API-Version"] = "1.0"
    resp.headers["Deprecation"] = "true"
    resp.headers["Sunset"] = "Thu, 31 Dec 2026 23:59:59 GMT"
    resp.headers["Link"] = '</api/v2/sandbox/formations>; rel="successor-version"'
    return resp, 200


@app.route("/api/v2/sandbox/formations", methods=["GET"])
def sandbox_formations_v2_current():
    """
    Nouveau contrat v2 introduit suite à des Ruptures de Contrat (Breaking Changes) :
    1. 'intitule' est renommé en 'titre'
    2. 'duree' passe d'un entier (5) à un objet structuré {'valeur': 5, 'unite': 'jours', 'heures': 35}
    3. Ajout d'une enveloppe normalisée {'meta': ..., 'data': ..., 'links': ...} avec pagination
    """
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(50, max(1, request.args.get("per_page", 10, type=int)))
    offset = (page - 1) * per_page

    db = get_db()
    total = db.execute("SELECT COUNT(*) AS c FROM formations").fetchone()["c"]
    rows = db.execute(
        "SELECT id, titre, duree_jours, salle FROM formations ORDER BY id ASC LIMIT ? OFFSET ?",
        (per_page, offset),
    ).fetchall()

    data_v2 = [
        {
            "id": r["id"],
            "titre": r["titre"],
            "duree": {
                "valeur": r["duree_jours"],
                "unite": "jours",
                "heures_pedagogiques": r["duree_jours"] * 7,
            },
            "localisation": {"salle": r["salle"], "campus": "ISGP Alger"},
            "links": {"self": f"/api/sandbox/formations/{r['id']}"},
        }
        for r in rows
    ]
    resp = jsonify({
        "meta": {
            "version": "v2",
            "page": page,
            "per_page": per_page,
            "total_items": total,
            "breaking_changes_depuis_v1": [
                "Champ 'intitule' renommé en 'titre'",
                "Champ 'duree' transformé d'un int (5) en objet {'valeur', 'unite', 'heures_pedagogiques'}",
                "Champ 'salle' déplacé dans l'objet 'localisation.salle'",
                "Racine enveloppée dans {'meta', 'data', 'links'}",
            ],
        },
        "data": data_v2,
        "links": {
            "self": f"/api/v2/sandbox/formations?page={page}&per_page={per_page}",
            "predecessor_version": "/api/v1/sandbox/formations",
        },
    })
    resp.headers["X-API-Version"] = "2.0"
    return resp, 200


# ==============================================================================
# LABORATOIRE DES COOKIES SÉCURISÉS (HttpOnly, Secure, SameSite & Session HMAC)
# ==============================================================================

@app.route("/api/sandbox/cookies/login", methods=["POST"])
def sandbox_cookies_login():
    body = request.get_json(silent=True) or {}
    identifiant = str(body.get("identifiant", "stagiaire_isgp")).strip() or "stagiaire_isgp"
    theme = str(body.get("theme", "institutionnel")).strip() or "institutionnel"

    session["utilisateur"] = identifiant
    session["role"] = "auditeur_api"

    signed_cookie_token = token_signer.dumps({"sub": identifiant, "mode": "httponly_cookie"})
    handler_code = (
        '@app.route("/api/sandbox/cookies/login", methods=["POST"])\n'
        "def cookies_login():\n"
        '    resp.set_cookie("isgp_auth_token", token, httponly=True, samesite="Strict", max_age=3600)\n'
        '    return jsonify({"statut": "Cookies sécurisés émis"}), 200'
    )
    steps = [
        f"1. Authentification de '{identifiant}' et génération du jeton signé HMAC.",
        "2. Ajout de l'en-tête Set-Cookie: isgp_auth_token=...; HttpOnly; SameSite=Strict; Max-Age=3600.",
        "3. Retour de la réponse 200 OK avec les cookies stockés dans le navigateur.",
    ]
    resp = make_traced_response(
        {
            "statut": "Cookies sécurisés émis avec succès",
            "utilisateur": identifiant,
            "cookies_emis": [
                {"nom": "isgp_auth_token", "flags": "HttpOnly; SameSite=Strict; Max-Age=3600", "usage": "Jeton d'authentification protégé contre le vol XSS"},
                {"nom": "isgp_session", "flags": "HttpOnly; SameSite=Lax (Signé HMAC)", "usage": "Session signée cryptographiquement (HMAC-SHA256)"},
                {"nom": "isgp_theme", "flags": "SameSite=Lax (Non-HttpOnly)", "usage": "Préférence d'affichage lisible par le front"},
            ],
        },
        200,
        handler_code,
        steps,
    )
    resp.set_cookie("isgp_auth_token", signed_cookie_token, max_age=3600, httponly=True, samesite="Strict", path="/")
    resp.set_cookie("isgp_theme", theme, max_age=86400 * 30, httponly=False, samesite="Lax", path="/")
    return resp


@app.route("/api/sandbox/cookies/inspect", methods=["GET"])
def sandbox_cookies_inspect():
    raw_token = request.cookies.get("isgp_auth_token")
    decoded_token = None
    if raw_token:
        try:
            decoded_token = token_signer.loads(raw_token, max_age=3600)
        except Exception:
            decoded_token = {"erreur": "Signature invalide ou cookie expiré"}

    handler_code = (
        '@app.route("/api/sandbox/cookies/inspect", methods=["GET"])\n'
        "def inspect_cookies():\n"
        '    raw_token = request.cookies.get("isgp_auth_token")\n'
        "    return jsonify(dict(request.cookies)), 200"
    )
    steps = [
        "1. Lecture de l'en-tête HTTP Cookie envoyé automatiquement par le client.",
        "2. Vérification de la signature HMAC du cookie HttpOnly 'isgp_auth_token'.",
        "3. Renvoi de l'état complet des cookies reçus (200 OK).",
    ]
    return make_traced_response(
        {
            "cookies_recus": dict(request.cookies),
            "session_signee_hmac": dict(session),
            "isgp_auth_token_decode": decoded_token,
            "en_tete_http_cookie": request.headers.get("Cookie", "(Aucun en-tête Cookie reçu)"),
        },
        200,
        handler_code,
        steps,
    )


@app.route("/api/sandbox/cookies/logout", methods=["POST"])
def sandbox_cookies_logout():
    session.clear()
    handler_code = (
        '@app.route("/api/sandbox/cookies/logout", methods=["POST"])\n'
        "def logout_cookies():\n"
        '    resp.delete_cookie("isgp_auth_token", path="/")\n'
        '    return jsonify({"statut": "Session purgée"}), 200'
    )
    steps = [
        "1. Purge de la session côté serveur.",
        "2. Émission de Set-Cookie avec Max-Age=0 pour ordonner au navigateur de supprimer isgp_auth_token.",
    ]
    resp = make_traced_response(
        {
            "statut": "Session purgée et cookies révoqués (Set-Cookie avec Max-Age=0)",
        },
        200,
        handler_code,
        steps,
    )
    resp.delete_cookie("isgp_auth_token", path="/")
    resp.delete_cookie("isgp_theme", path="/")
    return resp


# ==============================================================================
# LABORATOIRE INTERACTIF SQLITE3, REQUÊTES PRÉPARÉES (? vs %s) & SÉCURITÉ SQL
# ==============================================================================
def _get_sqlite_lab_handler_snippet(fw: str, mode: str) -> str:
    if fw == "fastapi":
        if mode == "find_one":
            return (
                '@app.get("/api/sqlite/formations/{formation_id}")\n'
                'def obtenir_formation(formation_id: int, db: sqlite3.Connection = Depends(get_db)):\n'
                '    with closing(db.cursor()) as cur:\n'
                '        # Attention : la virgule dans (formation_id,) est obligatoire (tuple à 1 élément)\n'
                '        cur.execute("SELECT id, titre, formateur, duree_jours, salle FROM formations WHERE id = ?", (formation_id,))\n'
                '        row = cur.fetchone()\n'
                '    if row is None:\n'
                '        raise HTTPException(status_code=404, detail="Formation introuvable")\n'
                '    return dict(row)'
            )
        if mode == "insert":
            return (
                '@app.post("/api/sqlite/formations", status_code=201)\n'
                'def creer_formation(payload: FormationCreate, db: sqlite3.Connection = Depends(get_db)):\n'
                '    with db:  # Transaction ACID automatique (COMMIT ou ROLLBACK)\n'
                '        with closing(db.cursor()) as cur:\n'
                '            cur.execute(\n'
                '                "INSERT INTO formations (titre, formateur, duree_jours, salle) "\n'
                '                "VALUES (:titre, :formateur, :duree_jours, :salle)",\n'
                '                payload.model_dump(),\n'
                '            )\n'
                '            new_id = cur.lastrowid\n'
                '    with closing(db.cursor()) as cur:\n'
                '        row = cur.execute("SELECT * FROM formations WHERE id = ?", (new_id,)).fetchone()\n'
                '    return dict(row)'
            )
        return (
            '@app.get("/api/sqlite/formations")\n'
            'def lister_formations(\n'
            '    salle: str = Query(default="Salle A"),\n'
            '    tri: str = Query(default="id"),\n'
            '    db: sqlite3.Connection = Depends(get_db),\n'
            '):\n'
            '    colonne_sure = {"id": "id", "duree_jours": "duree_jours", "titre": "titre"}.get(tri, "id")\n'
            '    sql = f"SELECT id, titre, formateur, duree_jours, salle FROM formations WHERE salle = ? ORDER BY {colonne_sure} ASC"\n'
            '    with closing(db.cursor()) as cur:\n'
            '        rows = cur.execute(sql, (salle,)).fetchall()\n'
            '    return [dict(r) for r in rows]'
        )
    if fw == "tornado":
        if mode == "find_one":
            return (
                'class FormationItemHandler(tornado.web.RequestHandler):\n'
                '    async def get(self, formation_id_str: str):\n'
                '        formation_id = int(formation_id_str)\n'
                '        def _find_one_sync():\n'
                '            conn = ouvrir_connexion_sqlite()\n'
                '            try:\n'
                '                with closing(conn.cursor()) as cur:\n'
                '                    cur.execute("SELECT * FROM formations WHERE id = ?", (formation_id,))\n'
                '                    r = cur.fetchone()\n'
                '                    return dict(r) if r is not None else None\n'
                '            finally:\n'
                '                conn.close()\n'
                '        row = await tornado.ioloop.IOLoop.current().run_in_executor(None, _find_one_sync)\n'
                '        if row is None:\n'
                '            self.set_status(404); self.write({"erreur": "Introuvable"}); return\n'
                '        self.write(row)'
            )
        if mode == "insert":
            return (
                'class FormationsSqliteHandler(tornado.web.RequestHandler):\n'
                '    async def post(self):\n'
                '        corps = tornado.escape.json_decode(self.request.body)\n'
                '        def _insert_sync():\n'
                '            conn = ouvrir_connexion_sqlite()\n'
                '            try:\n'
                '                with conn:\n'
                '                    with closing(conn.cursor()) as cur:\n'
                '                        cur.execute(\n'
                '                            "INSERT INTO formations (titre, formateur, duree_jours, salle) "\n'
                '                            "VALUES (:titre, :formateur, :duree_jours, :salle)",\n'
                '                            corps,\n'
                '                        )\n'
                '                        new_id = cur.lastrowid\n'
                '                with closing(conn.cursor()) as cur:\n'
                '                    return dict(cur.execute("SELECT * FROM formations WHERE id = ?", (new_id,)).fetchone())\n'
                '            finally:\n'
                '                conn.close()\n'
                '        cree = await tornado.ioloop.IOLoop.current().run_in_executor(None, _insert_sync)\n'
                '        self.set_status(201); self.write(cree)'
            )
        return (
            'class FormationsSqliteHandler(tornado.web.RequestHandler):\n'
            '    async def get(self):\n'
            '        salle = self.get_query_argument("salle", default="Salle A")\n'
            '        tri = self.get_query_argument("tri", default="id")\n'
            '        colonne_sure = {"id": "id", "duree_jours": "duree_jours", "titre": "titre"}.get(tri, "id")\n'
            '        sql = f"SELECT id, titre, formateur, duree_jours, salle FROM formations WHERE salle = ? ORDER BY {colonne_sure} ASC"\n'
            '        def _select_sync():\n'
            '            conn = ouvrir_connexion_sqlite()\n'
            '            try:\n'
            '                with closing(conn.cursor()) as cur:\n'
            '                    return [dict(r) for r in cur.execute(sql, (salle,)).fetchall()]\n'
            '            finally:\n'
            '                conn.close()\n'
            '        rows = await tornado.ioloop.IOLoop.current().run_in_executor(None, _select_sync)\n'
            '        self.write({"data": rows})'
        )
    # Flask default
    if mode == "find_one":
        return (
            '@app.route("/api/sqlite/formations/<int:formation_id>", methods=["GET"])\n'
            'def obtenir_formation(formation_id: int):\n'
            '    db = get_db()\n'
            '    with closing(db.cursor()) as cur:\n'
            '        # Attention : la virgule dans (formation_id,) est obligatoire (tuple à 1 élément)\n'
            '        cur.execute("SELECT id, titre, formateur, duree_jours, salle FROM formations WHERE id = ?", (formation_id,))\n'
            '        row = cur.fetchone()\n'
            '    if row is None:\n'
            '        return jsonify({"erreur": "Formation introuvable"}), 404\n'
            '    return jsonify(dict(row)), 200'
        )
    if mode == "insert":
        return (
            '@app.route("/api/sqlite/formations", methods=["POST"])\n'
            'def creer_formation():\n'
            '    corps = request.get_json() or {}\n'
            '    db = get_db()  # Connexion stockée dans flask.g et fermée par @app.teardown_appcontext\n'
            '    with db:       # Transaction ACID automatique (COMMIT ou ROLLBACK)\n'
            '        with closing(db.cursor()) as cur:\n'
            '            cur.execute(\n'
            '                "INSERT INTO formations (titre, formateur, duree_jours, salle) "\n'
            '                "VALUES (:titre, :formateur, :duree_jours, :salle)",\n'
            '                corps,\n'
            '            )\n'
            '            new_id = cur.lastrowid\n'
            '    with closing(db.cursor()) as cur:\n'
            '        row = cur.execute("SELECT * FROM formations WHERE id = ?", (new_id,)).fetchone()\n'
            '    return jsonify(dict(row)), 201'
        )
    return (
        '@app.route("/api/sqlite/formations", methods=["GET"])\n'
        'def lister_formations():\n'
        '    salle = request.args.get("salle", "Salle A")\n'
        '    tri = request.args.get("tri", "id")\n'
        '    colonne_sure = {"id": "id", "duree_jours": "duree_jours", "titre": "titre"}.get(tri, "id")\n'
        '    db = get_db()\n'
        '    sql = f"SELECT id, titre, formateur, duree_jours, salle FROM formations WHERE salle = ? ORDER BY {colonne_sure} ASC"\n'
        '    with closing(db.cursor()) as cur:\n'
        '        rows = cur.execute(sql, (salle,)).fetchall()\n'
        '    return jsonify([dict(r) for r in rows]), 200'
    )


@app.route("/api/sqlite-lab/state", methods=["GET"])
def api_sqlite_lab_state():
    fw = _resolve_active_framework()
    script_rel = f"{fw}-version/sqlite_api_lab.py"
    script_abs = os.path.join(ROOT_DIR, script_rel)
    script_code = ""
    if os.path.isfile(script_abs):
        with open(script_abs, encoding="utf-8") as f:
            script_code = f.read()

    conn = get_db()
    rows = [dict(r) for r in conn.execute("SELECT id, titre, formateur, duree_jours, salle FROM formations ORDER BY id ASC").fetchall()]
    schema_row = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='formations'").fetchone()
    journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
    fk_mode = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
    conn.close()

    return jsonify({
        "framework": fw,
        "sqlite_version": sqlite3.sqlite_version,
        "paramstyle": sqlite3.paramstyle,
        "journal_mode": journal_mode,
        "foreign_keys": fk_mode,
        "schema_sql": schema_row["sql"] if schema_row else "",
        "rows": rows,
        "script_path": script_rel,
        "script_code": script_code,
        "handler_snippet": _get_sqlite_lab_handler_snippet(fw, "select"),
    }), 200


@app.route("/api/sqlite-lab/execute", methods=["POST"])
def api_sqlite_lab_execute():
    fw = _resolve_active_framework()
    data = request.get_json(silent=True) or {}
    action = data.get("action", "select_compare")

    conn = get_db()
    all_rows = [dict(r) for r in conn.execute("SELECT id, titre, formateur, duree_jours, salle FROM formations ORDER BY id ASC").fetchall()]

    if action == "find_one":
        try:
            target_id = int(data.get("id", 1))
        except (TypeError, ValueError):
            target_id = 1
        sql_one = "SELECT id, titre, formateur, duree_jours, salle FROM formations WHERE id = ?"
        row = conn.execute(sql_one, (target_id,)).fetchone()
        conn.close()
        return jsonify({
            "action": "find_one",
            "framework": fw,
            "sql_executed": sql_one,
            "bound_params": [target_id],
            "found": row is not None,
            "row": dict(row) if row is not None else None,
            "handler_snippet": _get_sqlite_lab_handler_snippet(fw, "find_one"),
            "explanation": (
                f"Exécution de cur.fetchone() avec le tuple à 1 élément ({target_id},) : "
                + (f"Enregistrement #{target_id} trouvé et converti via dict(row) (200 OK)." if row is not None else f"cur.fetchone() a retourné None -> l'API renvoie HTTP 404 Not Found.")
            ),
            "rows": all_rows,
        }), (200 if row is not None else 404)

    if action == "insert_named":
        titre = str(data.get("titre", "Audit SQL & Requêtes Préparées")).strip() or "Audit SQL & Requêtes Préparées"
        formateur = str(data.get("formateur", "Équipe Pédagogique ISGP")).strip() or "Équipe Pédagogique ISGP"
        salle = str(data.get("salle", "Salle A")).strip() or "Salle A"
        try:
            duree_jours = max(1, min(30, int(data.get("duree_jours", 4))))
        except (TypeError, ValueError):
            duree_jours = 4

        params_dict = {
            "titre": titre,
            "formateur": formateur,
            "duree_jours": duree_jours,
            "salle": salle,
        }
        sql_named = (
            "INSERT INTO formations (titre, formateur, duree_jours, salle) "
            "VALUES (:titre, :formateur, :duree_jours, :salle)"
        )
        with conn:
            cur = conn.execute(sql_named, params_dict)
            new_id = cur.lastrowid
        updated_rows = [dict(r) for r in conn.execute("SELECT id, titre, formateur, duree_jours, salle FROM formations ORDER BY id ASC").fetchall()]
        conn.close()
        broadcast_classroom_state()
        return jsonify({
            "action": "insert_named",
            "framework": fw,
            "sql_executed": sql_named,
            "bound_params": params_dict,
            "lastrowid": new_id,
            "handler_snippet": _get_sqlite_lab_handler_snippet(fw, "insert"),
            "explanation": (
                f"Transaction COMMIT réussie : SQLite a lié le dictionnaire nommé (:titre, :formateur, :duree_jours, :salle) "
                f"et généré la clé primaire auto-incrémentée cursor.lastrowid = {new_id}."
            ),
            "rows": updated_rows,
        }), 201

    if action == "rollback_demo":
        # Démonstration d'atomicité sur une copie en mémoire pour montrer le ROLLBACK automatique
        mem = sqlite3.connect(":memory:")
        mem.row_factory = sqlite3.Row
        mem.execute(
            "CREATE TABLE formations (id INTEGER PRIMARY KEY, titre TEXT NOT NULL UNIQUE, duree_jours INTEGER NOT NULL CHECK(duree_jours > 0))"
        )
        mem.execute("INSERT INTO formations (id, titre, duree_jours) VALUES (1, 'Architecture API REST', 5)")
        mem.commit()

        before_count = mem.execute("SELECT COUNT(*) FROM formations").fetchone()[0]
        err_captured = None
        try:
            with mem:
                # 1re opération valide dans la transaction
                mem.execute("INSERT INTO formations (id, titre, duree_jours) VALUES (?, ?, ?)", (2, "Nouvelle Formation Temporaire", 3))
                # 2e opération invalide (violation de la contrainte UNIQUE sur id=1)
                mem.execute("INSERT INTO formations (id, titre, duree_jours) VALUES (?, ?, ?)", (1, "Conflit Clé Primaire", 4))
        except sqlite3.IntegrityError as exc:
            err_captured = str(exc)

        after_count = mem.execute("SELECT COUNT(*) FROM formations").fetchone()[0]
        mem.close()
        conn.close()
        return jsonify({
            "action": "rollback_demo",
            "framework": fw,
            "sql_executed": (
                "BEGIN TRANSACTION;\n"
                "  INSERT INTO formations (id, titre, duree_jours) VALUES (?, ?, ?)  -- (2, 'Nouvelle Formation Temporaire', 3) [OK]\n"
                "  INSERT INTO formations (id, titre, duree_jours) VALUES (?, ?, ?)  -- (1, 'Conflit Clé Primaire', 4) [ERREUR UNIQUE!]\n"
                "ROLLBACK; -- Déclenché automatiquement par la sortie du bloc `with conn:`"
            ),
            "bound_params": {"avant_transaction": before_count, "apres_rollback": after_count, "sqlite_error": err_captured},
            "handler_snippet": _get_sqlite_lab_handler_snippet(fw, "insert"),
            "explanation": (
                f"Atomicité ACID prouvée : la 2e requête a levé sqlite3.IntegrityError ({err_captured}). "
                f"Le gestionnaire de contexte `with conn:` a immédiatement exécuté ROLLBACK : la 1re insertion (id=2) a été annulée "
                f"(nombre de lignes avant = {before_count}, après ROLLBACK = {after_count})."
            ),
            "rows": all_rows,
        }), 200

    # Action par défaut : select_compare (Comparaison Requête Préparée `?` vs Concaténation f-string vulnérable)
    salle_input = str(data.get("salle", "Salle A"))
    tri_input = str(data.get("tri", "id"))
    colonne_sure = {"id": "id", "duree_jours": "duree_jours", "titre": "titre"}.get(tri_input, "id")

    # 1. Exécution SÉCURISÉE via marqueur `?` sur la vraie base
    safe_sql = f"SELECT id, titre, formateur, duree_jours, salle FROM formations WHERE salle = ? ORDER BY {colonne_sure} ASC"
    safe_params = [salle_input]
    safe_rows = [dict(r) for r in conn.execute(safe_sql, (salle_input,)).fetchall()]
    conn.close()

    # 2. Simulation ISOLÉE en mémoire (:memory:) de ce qu'aurait provoqué une f-string vulnérable
    mem = sqlite3.connect(":memory:")
    mem.row_factory = sqlite3.Row
    mem.execute("CREATE TABLE formations (id INTEGER, titre TEXT, formateur TEXT, duree_jours INTEGER, salle TEXT)")
    for r in all_rows:
        mem.execute(
            "INSERT INTO formations VALUES (?, ?, ?, ?, ?)",
            (r["id"], r["titre"], r["formateur"], r["duree_jours"], r["salle"]),
        )
    unsafe_sql = f"SELECT id, titre, formateur, duree_jours, salle FROM formations WHERE salle = '{salle_input}' ORDER BY {colonne_sure} ASC"
    try:
        unsafe_rows = [dict(r) for r in mem.execute(unsafe_sql).fetchall()]
        unsafe_error = None
    except Exception as exc:
        unsafe_rows = []
        unsafe_error = str(exc)
    mem.close()

    injection_detected = len(unsafe_rows) != len(safe_rows) or ("'" in salle_input)
    return jsonify({
        "action": "select_compare",
        "framework": fw,
        "input_salle": salle_input,
        "safe_sql": safe_sql,
        "safe_params": safe_params,
        "safe_rows": safe_rows,
        "unsafe_sql": unsafe_sql,
        "unsafe_rows": unsafe_rows,
        "unsafe_error": unsafe_error,
        "injection_detected": injection_detected,
        "handler_snippet": _get_sqlite_lab_handler_snippet(fw, "select"),
        "rows": all_rows,
    }), 200


# ==============================================================================
# LABORATOIRE AVANCÉ : TEMPS RÉEL (SSE / WEBSOCKETS), MULTIPART, JOBS 202 & ETAG
# ==============================================================================
import hashlib
import uuid
from werkzeug.utils import secure_filename

ADVANCED_CATALOGUE_STATE = {
    "id": 1,
    "titre": "Architecture Critique & Haute Disponibilité ISGP",
    "version_metier": 1,
    "salle": "Amphithéâtre Alger",
    "places": 40,
    "derniere_modification": "Initialisation système",
}
ADVANCED_JOBS_LIST = []
ADVANCED_LOCK = threading.Lock()


def _compute_advanced_etag(doc: dict) -> str:
    canonical = json.dumps(doc, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return f'"{hashlib.sha256(canonical).hexdigest()[:16]}"'


@app.route("/api/reference-file/<path:filename>", methods=["GET"])
def get_reference_lab_file(filename: str):
    """Permet à l'Atelier Python de charger ou télécharger sqlite_api_lab.py et advanced_realtime_cache_lab.py."""
    allowed = ("sqlite_api_lab.py", "advanced_realtime_cache_lab.py")
    safe_name = os.path.basename(filename)
    if safe_name not in allowed:
        return jsonify({"erreur": "Fichier de référence non autorisé"}), 404
    fw = _resolve_active_framework()
    folder = os.path.join(ROOT_DIR, f"{fw}-version")
    full_path = os.path.join(folder, safe_name)
    if not os.path.isfile(full_path):
        return jsonify({"erreur": "Fichier introuvable"}), 404
    if request.args.get("download") == "1":
        return send_from_directory(folder, safe_name, as_attachment=True)
    with open(full_path, encoding="utf-8") as f:
        return jsonify({"framework": fw, "path": f"{fw}-version/{safe_name}", "code": f.read()})


@app.route("/api/advanced-lab/state", methods=["GET"])
def api_advanced_lab_state():
    fw = _resolve_active_framework()
    script_rel = f"{fw}-version/advanced_realtime_cache_lab.py"
    script_abs = os.path.join(ROOT_DIR, script_rel)
    script_code = ""
    if os.path.isfile(script_abs):
        with open(script_abs, encoding="utf-8") as f:
            script_code = f.read()

    with ADVANCED_LOCK:
        doc_copy = dict(ADVANCED_CATALOGUE_STATE)
        etag = _compute_advanced_etag(doc_copy)
        jobs_copy = list(ADVANCED_JOBS_LIST[:8])

    return jsonify({
        "framework": fw,
        "etag": etag,
        "resource": doc_copy,
        "jobs": jobs_copy,
        "script_path": script_rel,
        "script_code": script_code,
    }), 200


@app.route("/api/advanced-lab/etag", methods=["POST"])
def api_advanced_lab_etag():
    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "get_fresh")
    req_id = f"req-{uuid.uuid4().hex[:10]}"
    t0 = time.perf_counter()

    with ADVANCED_LOCK:
        current_etag = _compute_advanced_etag(ADVANCED_CATALOGUE_STATE)

        if mode == "get_fresh":
            body_bytes = len(json.dumps(ADVANCED_CATALOGUE_STATE, ensure_ascii=False).encode("utf-8"))
            elapsed_ms = round((time.perf_counter() - t0) * 1000.0 + 0.42, 2)
            return jsonify({
                "http_status": 200,
                "status_text": "200 OK (Payload complet transféré + ETag émis)",
                "request_headers": {"Accept": "application/json", "X-Request-ID": req_id},
                "response_headers": {
                    "ETag": current_etag,
                    "Cache-Control": "private, max-age=30, must-revalidate",
                    "X-Request-ID": req_id,
                    "X-Process-Time-Ms": str(elapsed_ms),
                },
                "bytes_transferred": body_bytes,
                "etag": current_etag,
                "resource": dict(ADVANCED_CATALOGUE_STATE),
                "explanation": (
                    f"1er appel GET sans cache : le serveur sérialise toute la ressource ({body_bytes} octets) "
                    f"et joint l'empreinte SHA-256 ETag: {current_etag}."
                ),
            }), 200

        if mode == "get_conditional":
            client_etag = str(data.get("if_none_match", "")).strip()
            elapsed_ms = round((time.perf_counter() - t0) * 1000.0 + 0.11, 2)
            if client_etag == current_etag:
                return jsonify({
                    "http_status": 304,
                    "status_text": "304 Not Modified (Zéro octet de corps transféré !)",
                    "request_headers": {"If-None-Match": client_etag, "X-Request-ID": req_id},
                    "response_headers": {
                        "ETag": current_etag,
                        "Cache-Control": "private, max-age=30, must-revalidate",
                        "X-Request-ID": req_id,
                        "X-Process-Time-Ms": str(elapsed_ms),
                    },
                    "bytes_transferred": 0,
                    "etag": current_etag,
                    "resource": dict(ADVANCED_CATALOGUE_STATE),
                    "explanation": (
                        f"Validation de cache réussie : If-None-Match ({client_etag}) == ETag serveur ({current_etag}). "
                        f"Le serveur renvoie HTTP 304 avec 0 octet de corps JSON !"
                    ),
                }), 200
            body_bytes = len(json.dumps(ADVANCED_CATALOGUE_STATE, ensure_ascii=False).encode("utf-8"))
            return jsonify({
                "http_status": 200,
                "status_text": "200 OK (Cache client obsolète -> Nouveau payload + nouvel ETag)",
                "request_headers": {"If-None-Match": client_etag or "(absent)", "X-Request-ID": req_id},
                "response_headers": {
                    "ETag": current_etag,
                    "Cache-Control": "private, max-age=30, must-revalidate",
                    "X-Request-ID": req_id,
                    "X-Process-Time-Ms": str(elapsed_ms),
                },
                "bytes_transferred": body_bytes,
                "etag": current_etag,
                "resource": dict(ADVANCED_CATALOGUE_STATE),
                "explanation": (
                    f"L'ETag du client ({client_etag or 'aucun'}) diffère de l'ETag actuel ({current_etag}) : "
                    f"le serveur renvoie la nouvelle version complète ({body_bytes} octets)."
                ),
            }), 200

        if mode == "simulate_concurrent_writer":
            ADVANCED_CATALOGUE_STATE["places"] = max(10, (ADVANCED_CATALOGUE_STATE["places"] + 5) % 90)
            ADVANCED_CATALOGUE_STATE["version_metier"] += 1
            ADVANCED_CATALOGUE_STATE["derniere_modification"] = f"Modifié par Collègue B à {datetime.now().strftime('%H:%M:%S')}"
            new_etag = _compute_advanced_etag(ADVANCED_CATALOGUE_STATE)
            return jsonify({
                "http_status": 200,
                "status_text": "Modification concurrente effectuée par un autre opérateur (Collègue B)",
                "etag": new_etag,
                "previous_etag_now_stale": current_etag,
                "resource": dict(ADVANCED_CATALOGUE_STATE),
                "explanation": (
                    f"Un autre utilisateur (Collègue B) vient de modifier la ressource sur le serveur ! "
                    f"L'ETag serveur est passé de {current_etag} à {new_etag}. Si vous tentez un PUT avec l'ancien ETag, le serveur renverra 412 !"
                ),
            }), 200

        # mode == "put_if_match"
        if_match = str(data.get("if_match", "")).strip()
        nouvelle_salle = str(data.get("salle", ADVANCED_CATALOGUE_STATE["salle"])).strip() or "Salle A"
        try:
            nouvelles_places = int(data.get("places", ADVANCED_CATALOGUE_STATE["places"]))
        except (TypeError, ValueError):
            nouvelles_places = ADVANCED_CATALOGUE_STATE["places"]

        elapsed_ms = round((time.perf_counter() - t0) * 1000.0 + 0.25, 2)
        if not if_match:
            return jsonify({
                "http_status": 428,
                "status_text": "428 Precondition Required (En-tête If-Match manquant)",
                "request_headers": {"Content-Type": "application/json", "X-Request-ID": req_id},
                "response_headers": {"ETag": current_etag, "X-Request-ID": req_id},
                "bytes_transferred": 98,
                "etag": current_etag,
                "resource": dict(ADVANCED_CATALOGUE_STATE),
                "explanation": "Écriture refusée (428) : l'API exige l'en-tête If-Match contenant l'ETag lu précédemment.",
            }), 200

        if if_match != current_etag:
            return jsonify({
                "http_status": 412,
                "status_text": "412 Precondition Failed — ÉCRASEMENT CONCURRENT (LOST UPDATE) ÉVITÉ !",
                "request_headers": {"If-Match": if_match, "Content-Type": "application/json", "X-Request-ID": req_id},
                "response_headers": {"ETag": current_etag, "X-Request-ID": req_id, "X-Process-Time-Ms": str(elapsed_ms)},
                "bytes_transferred": 164,
                "etag": current_etag,
                "resource": dict(ADVANCED_CATALOGUE_STATE),
                "explanation": (
                    f"Protection Optimiste réussie ! Votre If-Match ({if_match}) ne correspond plus à l'ETag serveur actuel ({current_etag}). "
                    f"Au lieu d'écraser silencieusement le travail de votre collègue, l'API rejette le PUT avec HTTP 412 Precondition Failed."
                ),
            }), 200

        ADVANCED_CATALOGUE_STATE["salle"] = nouvelle_salle
        ADVANCED_CATALOGUE_STATE["places"] = nouvelles_places
        ADVANCED_CATALOGUE_STATE["version_metier"] += 1
        ADVANCED_CATALOGUE_STATE["derniere_modification"] = f"Mise à jour validée (If-Match OK) à {datetime.now().strftime('%H:%M:%S')}"
        new_etag = _compute_advanced_etag(ADVANCED_CATALOGUE_STATE)
        body_bytes = len(json.dumps(ADVANCED_CATALOGUE_STATE, ensure_ascii=False).encode("utf-8"))
        return jsonify({
            "http_status": 200,
            "status_text": "200 OK (If-Match valide -> Ressource mise à jour & nouvel ETag généré)",
            "request_headers": {"If-Match": if_match, "Content-Type": "application/json", "X-Request-ID": req_id},
            "response_headers": {"ETag": new_etag, "X-Request-ID": req_id, "X-Process-Time-Ms": str(elapsed_ms)},
            "bytes_transferred": body_bytes,
            "etag": new_etag,
            "resource": dict(ADVANCED_CATALOGUE_STATE),
            "explanation": f"Précondition vérifiée ({if_match} == ETag serveur). Mise à jour appliquée -> nouvel ETag = {new_etag}.",
        }), 200


@app.route("/api/advanced-lab/jobs", methods=["GET", "POST"])
def api_advanced_lab_jobs():
    fw = _resolve_active_framework()
    if request.method == "GET":
        with ADVANCED_LOCK:
            return jsonify({"jobs": list(ADVANCED_JOBS_LIST[:8])}), 200

    data = request.get_json(silent=True) or {}
    sujet = str(data.get("sujet", "Export PDF Certificats Promotion 2026")).strip() or "Export PDF Certificats"
    req_id = data.get("request_id") or f"req-{uuid.uuid4().hex[:8]}"
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    engine_label = {
        "flask": "ThreadPoolExecutor (Worker WSGI)",
        "fastapi": "BackgroundTasks (ASGI Post-Response)",
        "tornado": "IOLoop.current().spawn_callback()",
    }.get(fw, "Background Worker")

    job_entry = {
        "job_id": job_id,
        "sujet": sujet,
        "moteur": engine_label,
        "request_id": req_id,
        "statut": "PENDING (0%)",
        "progression": 0,
        "created_at": datetime.now().strftime("%H:%M:%S"),
        "resultat": None,
    }
    with ADVANCED_LOCK:
        ADVANCED_JOBS_LIST.insert(0, job_entry)
        del ADVANCED_JOBS_LIST[10:]

    def _run_bg_job():
        for pct, label in [(35, "RUNNING — Requête SQLite par lots (35%)"), (75, "RUNNING — Génération PDF & Signature SHA-256 (75%)"), (100, "COMPLETED (100%)")]:
            time.sleep(0.75)
            with ADVANCED_LOCK:
                job_entry["progression"] = pct
                job_entry["statut"] = label
                if pct == 100:
                    job_entry["resultat"] = f"/downloads/{job_id}.pdf (184 Ko)"

    threading.Thread(target=_run_bg_job, daemon=True).start()

    return jsonify({
        "http_status": 202,
        "message": "202 Accepted — Tâche acceptée et déléguée en arrière-plan en 0.4 ms !",
        "location": f"/api/advanced-lab/jobs/{job_id}",
        "request_id": req_id,
        "job": job_entry,
    }), 202


@app.route("/api/advanced-lab/multipart-inspect", methods=["POST"])
def api_advanced_lab_multipart_inspect():
    data = request.get_json(silent=True) or {}
    scenario = data.get("scenario", "valid_pdf")
    boundary = "----ISGPFormBoundary9f8e7d6c5b"

    if scenario == "traversal_pdf":
        raw_filename = "../../../etc/cron.d/backdoor_cours.pdf"
        claimed_mime = "application/pdf"
        magic_bytes = b"%PDF-1.7\n%Document officiel ISGP..."
        sim_size = 48_200
    elif scenario == "spoofed_exe":
        raw_filename = "facture_fournisseur.pdf"
        claimed_mime = "application/pdf"
        magic_bytes = b"MZ\x90\x00\x03\x00\x00\x00_EXECUTABLE_WINDOWS_DEGUISE"
        sim_size = 112_400
    elif scenario == "oversized":
        raw_filename = "archive_complete_4k.pdf"
        claimed_mime = "application/pdf"
        magic_bytes = b"%PDF-1.7\n%Archive..."
        sim_size = 15 * 1024 * 1024  # 15 Mo (> limite 2 Mo)
    else:
        raw_filename = "support_architecture_api_2026.pdf"
        claimed_mime = "application/pdf"
        magic_bytes = b"%PDF-1.7\n1 0 obj << /Type /Catalog >>..."
        sim_size = 128_500

    sanitized = secure_filename(raw_filename) or "document.bin"
    final_stored_name = f"{uuid.uuid4().hex[:8]}_{sanitized}"
    hex_head = magic_bytes[:8].hex(" ").upper()

    wire_frame = (
        f"POST /api/lab/upload HTTP/1.1\r\n"
        f"Host: api.isgp.dz\r\n"
        f"Content-Length: {sim_size}\r\n"
        f"Content-Type: multipart/form-data; boundary={boundary}\r\n\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="categorie"\r\n\r\n'
        f"support_pedagogique\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="document"; filename="{raw_filename}"\r\n'
        f"Content-Type: {claimed_mime}\r\n\r\n"
        f"<FLUX BINAIRE BRUT : Premiers octets Hex = [{hex_head}] | ASCII = {repr(magic_bytes[:18])}>\r\n"
        f"--{boundary}--\r\n"
    )

    max_limit = 2 * 1024 * 1024
    if sim_size > max_limit:
        http_code = 413
        verdict = "REJETÉ — HTTP 413 Content Too Large (Protection anti-saturation RAM/Disque : 15 Mo > plafond 2 Mo)"
    elif not (magic_bytes.startswith(b"%PDF-") or magic_bytes.startswith(b"\x89PNG")):
        http_code = 415
        verdict = (
            f"REJETÉ — HTTP 415 Unsupported Media Type ! Le client prétend envoyer '{claimed_mime}' ({raw_filename}), "
            f"mais les Magic Bytes réels [{hex_head}] correspondent à un exécutable 'MZ' (usurpation MIME détectée) !"
        )
    else:
        http_code = 201
        traversal_note = (
            f" Attaque Path Traversal neutralisée ('{raw_filename}' -> '{final_stored_name}')."
            if ".." in raw_filename or "/" in raw_filename
            else ""
        )
        verdict = f"ACCEPTÉ — HTTP 201 Created. Signature binaire %PDF- authentique vérifiée en streaming.{traversal_note}"

    return jsonify({
        "scenario": scenario,
        "http_status": http_code,
        "verdict": verdict,
        "raw_filename": raw_filename,
        "sanitized_filename": final_stored_name,
        "claimed_mime": claimed_mime,
        "magic_bytes_hex": hex_head,
        "size_bytes": sim_size,
        "wire_frame": wire_frame,
    }), 200


@app.route("/api/advanced-lab/sse-demo", methods=["GET"])
def api_advanced_lab_sse_demo():
    fw = _resolve_active_framework()
    fw_mechanism = {
        "flask": "Flask Response(stream_with_context(yield))",
        "fastapi": "FastAPI StreamingResponse(async generator)",
        "tornado": "Tornado RequestHandler + await self.flush()",
    }.get(fw, "SSE Stream")

    def _stream():
        etapes = [
            "Connexion HTTP persistante ouverte (Content-Type: text/event-stream)",
            "Collecte des métriques CPU / Latence SQLite WAL...",
            "Vérification des quotas Rate-Limiter par fenêtre glissante...",
            "Synchronisation du cache ETag des 4 nœuds upstream...",
            "Flux temps réel terminé proprement (reconnexion auto via Last-Event-ID si coupure).",
        ]
        for idx, msg in enumerate(etapes, start=1):
            payload = json.dumps({
                "id_trame": idx,
                "moteur": fw_mechanism,
                "message": msg,
                "horodatage": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            }, ensure_ascii=False)
            yield f"id: sse-{idx}\nevent: telemetry\ndata: {payload}\n\n"
            time.sleep(0.35)

    return Response(
        _stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ==============================================================================
# LABORATOIRE ARCHITECTURE : NORD-SUD vs EST-OUEST, OAUTH 2.0 / RFC 8693 & SWAGGER
# ==============================================================================
def _build_architecture_oauth_scenarios(fw: str) -> dict:
    now_ts = int(time.time())
    fw_label = {"flask": "Flask WSGI", "fastapi": "FastAPI ASGI", "tornado": "Tornado IOLoop"}.get(fw, fw)
    return {
        "pkce_north_south": {
            "http_status": 200,
            "direction": "NORD-SUD (Client Externe SPA/Mobile -> API Gateway -> Service Inscriptions)",
            "grant_type": "authorization_code + PKCE (RFC 7636)",
            "verdict": f"AUTORISÉ (200 OK) — Jeton d'accès OAuth 2.0 scopé vérifié par {fw_label}.",
            "jwt_header": {"alg": "RS256", "typ": "at+jwt", "kid": "isgp-idp-2026-key1"},
            "jwt_payload": {
                "iss": "https://auth.isgp.dz",
                "sub": "user:amine.benali",
                "aud": "https://api.isgp.dz/service-inscriptions",
                "client_id": "isgp-pwa-portal",
                "scope": "formations:read inscriptions:write",
                "iat": now_ts,
                "exp": now_ts + 900,
            },
            "security_checks": [
                "1. PKCE vérifié sur l'Authorization Server : SHA256(code_verifier) == code_challenge (aucun client_secret stocké dans le navigateur).",
                "2. Signature asymétrique RS256 validée via la clé publique JWKS de https://auth.isgp.dz (aucun secret partagé).",
                "3. Audience stricte vérifiée : aud == 'https://api.isgp.dz/service-inscriptions'.",
                "4. Périmètre délégué vérifié : 'inscriptions:write' présent dans scope (l'application n'a jamais vu le mot de passe d'Amine).",
            ],
        },
        "confused_deputy_attack": {
            "http_status": 403,
            "direction": "EST-OUEST ILLÉGITIME (Rejeu direct du jeton Nord-Sud vers Service Paiement)",
            "grant_type": "Anti-Pattern : Blind Token Passthrough (Attaque du Confused Deputy)",
            "verdict": "BLOQUÉ (HTTP 403 Forbidden — Invalid Audience) ! Le jeton destiné au Service Inscriptions est refusé par le Service Paiement.",
            "jwt_header": {"alg": "RS256", "typ": "at+jwt", "kid": "isgp-idp-2026-key1"},
            "jwt_payload": {
                "iss": "https://auth.isgp.dz",
                "sub": "user:amine.benali",
                "aud": "https://api.isgp.dz/service-inscriptions",
                "scope": "formations:read inscriptions:write",
                "exp": now_ts + 900,
            },
            "security_checks": [
                "1. Le Service Inscriptions (ou un service tiers compromis) tente de réutiliser tel quel le jeton Nord-Sud auprès du Service Paiement.",
                "2. Le Service Paiement inspecte la revendication 'aud' : attendue = 'service-paiement', reçue = 'service-inscriptions' !",
                "3. Rejet immédiat HTTP 403 : sans contrôle d'audience ni Token Exchange, n'importe quel microservice interne pourrait débiter l'utilisateur !",
            ],
        },
        "token_exchange_east_west": {
            "http_status": 200,
            "direction": "EST-OUEST DÉLÉGUÉ ZERO-TRUST (Service Inscriptions -> IdP RFC 8693 -> Service Paiement + mTLS)",
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange (RFC 8693 On-Behalf-Of)",
            "verdict": "AUTORISÉ (200 OK) — Délégation traçable : Service Paiement sait QUI est l'utilisateur (sub) ET QUEL microservice agit en son nom (act).",
            "jwt_header": {"alg": "EdDSA", "typ": "at+jwt", "kid": "isgp-mesh-ed25519"},
            "jwt_payload": {
                "iss": "https://auth.isgp.dz",
                "sub": "user:amine.benali",
                "aud": "https://internal.isgp.mesh/service-paiement",
                "scope": "paiement:debit_inscription",
                "act": {
                    "sub": "spiffe://isgp.mesh/ns/prod/sa/service-inscriptions"
                },
                "iat": now_ts,
                "exp": now_ts + 120,
            },
            "security_checks": [
                "1. Transport mTLS vérifié : certificat X.509 client prouve l'identité machine 'service-inscriptions'.",
                "2. Token Exchange RFC 8693 : le jeton a une durée de vie ultra-courte (120 s), une audience dédiée ('service-paiement') et un scope réduit ('paiement:debit_inscription').",
                "3. Traçabilité d'audit double : sub='user:amine.benali' (bénéficiaire) + act.sub='service-inscriptions' (acteur délégué).",
            ],
        },
        "m2m_client_credentials": {
            "http_status": 200,
            "direction": "EST-OUEST MACHINE-TO-MACHINE PUR (Daemon Nocturne de Facturation -> Service Comptabilité)",
            "grant_type": "client_credentials (RFC 6749 §4.4 — Sans utilisateur humain)",
            "verdict": "AUTORISÉ (200 OK) — Authentification directe de service autonome (sub == client_id).",
            "jwt_header": {"alg": "RS256", "typ": "at+jwt", "kid": "isgp-idp-2026-key1"},
            "jwt_payload": {
                "iss": "https://auth.isgp.dz",
                "sub": "service-account:cron-cloture-comptable",
                "aud": "https://internal.isgp.mesh/service-comptabilite",
                "client_id": "cron-cloture-comptable",
                "scope": "rapports:consolider ecritures:exporter",
                "iat": now_ts,
                "exp": now_ts + 300,
            },
            "security_checks": [
                "1. Aucun humain connecté : le démon s'authentifie auprès de l'Authorization Server par clé privée asymétrique (private_key_jwt) ou client_secret.",
                "2. sub identifie directement le compte de service ('service-account:cron-cloture-comptable').",
                "3. Moindre privilège appliqué via scope='rapports:consolider ecritures:exporter' et aud='service-comptabilite'.",
            ],
        },
    }


def _build_openapi_framework_comparison() -> dict:
    openapi_contract = (
        "openapi: 3.1.0\n"
        "info:\n"
        "  title: API Gestion des Formations ISGP\n"
        "  version: 2.1.0\n"
        "components:\n"
        "  securitySchemes:\n"
        "    OAuth2PKCE:\n"
        "      type: oauth2\n"
        "      flows:\n"
        "        authorizationCode:\n"
        "          authorizationUrl: https://auth.isgp.dz/oauth2/authorize\n"
        "          tokenUrl: https://auth.isgp.dz/oauth2/token\n"
        "          scopes:\n"
        "            inscriptions:write: Créer une inscription déléguée\n"
        "  schemas:\n"
        "    InscriptionCreate:\n"
        "      type: object\n"
        "      required: [formation_id, stagiaire_email]\n"
        "      properties:\n"
        "        formation_id: { type: integer, minimum: 1 }\n"
        "        stagiaire_email: { type: string, format: email }\n"
        "paths:\n"
        "  /api/v2/inscriptions:\n"
        "    post:\n"
        "      summary: Inscrire un stagiaire (Contrat strict OAS 3.1)\n"
        "      security:\n"
        "        - OAuth2PKCE: [inscriptions:write]\n"
        "      requestBody:\n"
        "        required: true\n"
        "        content:\n"
        "          application/json:\n"
        "            schema: { $ref: '#/components/schemas/InscriptionCreate' }\n"
        "      responses:\n"
        "        '201': { description: Inscription créée }\n"
        "        '401': { description: Jeton OAuth2 manquant ou expiré }\n"
        "        '403': { description: Scope inscriptions:write absent }\n"
        "        '422': { description: Violation du contrat JSON Schema }"
    )
    return {
        "openapi_yaml": openapi_contract,
        "frameworks": {
            "flask": {
                "approach": "Flask — Approche Explicite / Modulaire (flask-smorest, APIFlask ou Contrat YAML servi par Swagger UI)",
                "philosophy": (
                    "Flask ne génère pas d'OpenAPI par magie implicite dans son noyau minimaliste : en entreprise, "
                    "on utilise soit APIFlask / flask-smorest (décorateurs Marshmallow/Pydantic -> OpenAPI + Swagger UI), "
                    "soit l'approche Contract-First pure où le fichier openapi.yaml validé en CI pilote la route /api/docs."
                ),
                "code": (
                    "from apiflask import APIFlask, Schema\n"
                    "from apiflask.fields import Email, Integer\n"
                    "from apiflask.validators import Range\n\n"
                    "app = APIFlask(__name__, title='API ISGP', version='2.1.0')  # Génère /openapi.json et /docs (Swagger UI) !\n\n"
                    "class InscriptionIn(Schema):\n"
                    "    formation_id = Integer(required=True, validate=Range(min=1))\n"
                    "    stagiaire_email = Email(required=True)\n\n"
                    "@app.post('/api/v2/inscriptions')\n"
                    "@app.input(InscriptionIn)  # Valide le contrat -> 422 auto + documente Swagger UI\n"
                    "@app.doc(security=[{'OAuth2PKCE': ['inscriptions:write']}])\n"
                    "def creer_inscription(json_data):\n"
                    "    return {'statut': 'CONFIRMEE', **json_data}, 201"
                ),
            },
            "fastapi": {
                "approach": "FastAPI — Approche Code-First Native (Annotations Python + Pydantic v2 -> OAS 3.1 & Swagger UI intégrés)",
                "philosophy": (
                    "FastAPI a été bâti directement autour du standard OpenAPI 3.1 : vos modèles Pydantic v2 et vos dépendances "
                    "Security(OAuth2AuthorizationCodeBearer, scopes=...) compilent automatiquement /openapi.json, Swagger UI (/docs) et ReDoc (/redoc) !"
                ),
                "code": (
                    "from fastapi import FastAPI, Security\n"
                    "from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes\n"
                    "from pydantic import BaseModel, EmailStr, Field\n\n"
                    "app = FastAPI(title='API ISGP', version='2.1.0')  # /openapi.json, /docs (Swagger) & /redoc natifs !\n"
                    "oauth2_scheme = OAuth2AuthorizationCodeBearer(\n"
                    "    authorizationUrl='https://auth.isgp.dz/oauth2/authorize',\n"
                    "    tokenUrl='https://auth.isgp.dz/oauth2/token',\n"
                    "    scopes={'inscriptions:write': 'Créer une inscription déléguée'},\n"
                    ")\n\n"
                    "class InscriptionCreate(BaseModel):\n"
                    "    formation_id: int = Field(..., ge=1)\n"
                    "    stagiaire_email: EmailStr\n\n"
                    "@app.post('/api/v2/inscriptions', status_code=201)\n"
                    "async def creer_inscription(\n"
                    "    payload: InscriptionCreate,\n"
                    "    token: str = Security(oauth2_scheme, scopes=['inscriptions:write']),\n"
                    "):\n"
                    "    return {'statut': 'CONFIRMEE', **payload.model_dump()}"
                ),
            },
            "tornado": {
                "approach": "Tornado — Approche Contract-First Haute Performance (openapi.yaml versionné + RequestHandler sans réflexion lourde)",
                "philosophy": (
                    "Sur l'IOLoop Tornado orientée très faible latence, les équipes privilégient souvent le Contract-First : "
                    "le contrat openapi.yaml est rédigé et validé dans Git en premier, servi tel quel sur /openapi.json pour Swagger UI, "
                    "et vérifié à vitesse maximale dans RequestHandler (ou généré hors-boucle via apispec)."
                ),
                "code": (
                    "import json, tornado.web\n\n"
                    "class OpenAPISpecHandler(tornado.web.RequestHandler):\n"
                    "    def get(self):\n"
                    "        # Sert le contrat de référence validé en CI/CD pour Swagger UI (/api/docs)\n"
                    "        self.set_header('Content-Type', 'application/json')\n"
                    "        self.write(CONTRAT_OPENAPI_3_1_DICT)\n\n"
                    "class InscriptionsV2Handler(tornado.web.RequestHandler):\n"
                    "    async def post(self):\n"
                    "        claims = verifier_jeton_oauth2(self.request.headers, required_scope='inscriptions:write')\n"
                    "        corps = json.loads(self.request.body)\n"
                    "        if int(corps.get('formation_id', 0)) < 1 or '@' not in str(corps.get('stagiaire_email', '')):\n"
                    "            self.set_status(422)\n"
                    "            return self.write({'title': 'Violation du contrat InscriptionCreate', 'status': 422})\n"
                    "        self.set_status(201)\n"
                    "        self.write({'statut': 'CONFIRMEE', 'operateur': claims['sub'], **corps})"
                ),
            },
        },
    }


@app.route("/api/architecture-lab/oauth-flow", methods=["POST"])
def api_architecture_oauth_flow():
    fw = _resolve_active_framework()
    data = request.get_json(silent=True) or {}
    scenario = data.get("scenario", "pkce_north_south")
    all_scenarios = _build_architecture_oauth_scenarios(fw)
    chosen = all_scenarios.get(scenario, all_scenarios["pkce_north_south"])
    return jsonify({"scenario": scenario, "framework": fw, **chosen}), 200


@app.route("/api/architecture-lab/openapi-compare", methods=["GET"])
def api_architecture_openapi_compare():
    fw = _resolve_active_framework()
    spec_bundle = _build_openapi_framework_comparison()
    selected_fw = request.args.get("target_fw", fw).strip().lower()
    if selected_fw not in ("flask", "fastapi", "tornado"):
        selected_fw = fw
    return jsonify({
        "selected_framework": selected_fw,
        "openapi_yaml": spec_bundle["openapi_yaml"],
        "framework_detail": spec_bundle["frameworks"][selected_fw],
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
