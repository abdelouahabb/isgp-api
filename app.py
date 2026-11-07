import hmac
import json
import os
import queue
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from flask import Flask, Response, jsonify, render_template, request, send_from_directory
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from data.curriculum import DAYS_CURRICULUM, STARTER_FILES_CONTENT
from data.glossary import GLOSSARY_TERMS
from data.quizzes import QUIZZES

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "sandbox_isgp.db")
TEACHER_PIN = os.environ.get("TEACHER_PIN", "isgp")

# Secrets chargés depuis les variables d'environnement (avec valeurs par défaut pour le laboratoire local)
API_SECRET_KEY = os.environ.get("API_SECRET_KEY", "secret-signature-interne-isgp-2026")
PARTNER_API_KEY = os.environ.get("PARTNER_API_KEY", "isgp-secret-2026")
TOKEN_EXPIRATION_SECONDS = 300  # 5 minutes

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
# 3. ROUTES PRINCIPALES DE LA PWA & CONTENU PÉDAGOGIQUE
# ==============================================================================
@app.route("/")
def index():
    local_ip = get_local_ip()
    return render_template("index.html", local_ip=local_ip)


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
    return jsonify(
        {
            "days": DAYS_CURRICULUM,
            "glossary": GLOSSARY_TERMS,
            "quizzes": QUIZZES,
            "classroom": CLASSROOM_STATE,
            "server_ip": get_local_ip(),
        }
    )


@app.route("/api/download/day/<int:day_id>")
def download_starter_file(day_id):
    code = STARTER_FILES_CONTENT.get(day_id, STARTER_FILES_CONTENT[0])
    filename = f"isgp_jour{day_id}_starter.py"
    for d in DAYS_CURRICULUM:
        if d["day_number"] == day_id:
            filename = os.path.basename(d["starter_filename"])
            break
    return Response(
        code,
        mimetype="text/x-python",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/api/day-file/<int:day_id>/<path:filename>")
def get_day_file(day_id, filename):
    if day_id not in (0, 1, 2, 3, 4, 5):
        return jsonify({"erreur": "Jour invalide"}), 404
    folder = os.path.join(os.path.dirname(__file__), f"day_{day_id}")
    safe_name = os.path.basename(filename)
    full_path = os.path.join(folder, safe_name)
    if not os.path.isfile(full_path):
        return jsonify({"erreur": "Fichier introuvable"}), 404
    if request.args.get("download") == "1":
        return send_from_directory(folder, safe_name, as_attachment=True)
    with open(full_path, encoding="utf-8") as f:
        return jsonify({"path": f"day_{day_id}/{safe_name}", "code": f.read()})


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
# 5. SANDBOX HTTP ÉDUCATIF (ROUTES FLASK AVEC TRACE D'EXÉCUTION SERVEUR)
# ==============================================================================
def make_traced_response(payload, status_code, handler_code, trace_steps, extra_headers=None):
    resp = jsonify(payload)
    resp.status_code = status_code
    resp.headers["X-Flask-Handler-Code"] = json.dumps(handler_code)
    resp.headers["X-Flask-Trace-Steps"] = json.dumps(trace_steps, ensure_ascii=False)
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

    if identifiant != "stagiaire" or mot_de_passe != "isgp2026":
        handler_code = (
            'corps = request.get_json()\n'
            'if corps.get("identifiant") != "stagiaire" or corps.get("mot_de_passe") != "isgp2026":\n'
            '    return jsonify({"erreur": "Identifiants invalides"}), 401'
        )
        steps = [
            "1. Réception de POST /api/sandbox/auth/token.",
            "2. Vérification des identifiants fournis dans le corps JSON.",
            "3. ÉCHEC : Identifiant ou mot de passe incorrect -> 401 Unauthorized.",
        ]
        return make_traced_response(
            {
                "erreur": "Identifiants invalides (401 Unauthorized).",
                "attendu_pour_demo": {"identifiant": "stagiaire", "mot_de_passe": "isgp2026"},
            },
            401,
            handler_code,
            steps,
            extra_headers={"WWW-Authenticate": 'Bearer realm="ISGP-API"'},
        )

    charge_utile = {
        "utilisateur": identifiant,
        "role": "participant_isgp",
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
        handler_code = (
            '@app.route("/api/sandbox/formations", methods=["GET"])\n'
            "def lister_formations():\n"
            '    rows = conn.execute("SELECT * FROM formations").fetchall()\n'
            '    return jsonify({"total": len(rows), "formations": [dict(r) for r in rows]}), 200'
        )
        steps = [
            "1. Réception d'une requête HTTP GET sur /api/sandbox/formations.",
            "2. Connexion à la base SQLite et exécution de 'SELECT * FROM formations'.",
            f"3. Transformation des {len(liste)} lignes SQLite en dictionnaires Python.",
            "4. Envoi de la réponse JSON avec le code 200 OK.",
        ]
        return make_traced_response({"total": len(liste), "formations": liste}, 200, handler_code, steps)

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


@app.route("/api/sandbox/formations/<int:formation_id>", methods=["GET", "PUT", "DELETE"])
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

    if request.method == "PUT":
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
    conn.commit()
    conn.close()
    init_db()
    broadcast_classroom_state()
    return jsonify({"message": "Base SQLite et compteurs Rate Limit réinitialisés."}), 200


# ==============================================================================
# 7. EXÉCUTEUR PYTHON PÉDAGOGIQUE INTÉGRÉ
# ==============================================================================
@app.route("/api/python/run", methods=["POST"])
def run_python_snippet():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    if not code.strip():
        return jsonify({"output": "", "error": "Le code est vide."}), 400

    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        proc = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=3,
            env={"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"},
        )
        os.unlink(tmp_path)
        return jsonify(
            {
                "output": proc.stdout,
                "error": proc.stderr,
                "exit_code": proc.returncode,
            }
        )
    except subprocess.TimeoutExpired:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        return jsonify(
            {
                "output": "",
                "error": "Délai d'exécution dépassé (3s). Si votre script démarre un serveur app.run(), exécutez-le dans le terminal de VS Code / Antigravity IDE.",
                "exit_code": 124,
            }
        )
    except Exception as exc:
        return jsonify({"output": "", "error": str(exc), "exit_code": 1})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
