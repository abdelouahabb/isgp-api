// ============================================================================
// ISGP API Engineering Trilogy — Referentiel Architecture Securite & OWASP 2023
// Support multi-framework dynamique : Flask (WSGI), FastAPI (ASGI), Tornado
// ============================================================================

(function () {
  "use strict";

  var CHECKLIST_STORAGE_KEY = "isgp-sec-checklist-v1";

  var SEC_STATE = {
    owaspFilter: "all",
    frameworkOverride: null,
    lastHostFramework: null,
    simScenario: "bola",
    simMode: "hardened",
    simTargetTrace: "GET /api/v1/dossiers/999 (Session: user_id=42, role=stagiaire)",
    simExecutedCount: 0
  };

  function detectHostFramework() {
    var raw = (
      window.ACTIVE_FRAMEWORK ||
      (typeof STATE !== "undefined" && STATE && STATE.framework) ||
      "flask"
    )
      .toString()
      .toLowerCase();
    if (raw === "fastapi" || raw === "tornado" || raw === "flask") {
      return raw;
    }
    return "flask";
  }

  function getActiveSecFramework() {
    var hostFw = detectHostFramework();
    if (SEC_STATE.lastHostFramework !== hostFw) {
      SEC_STATE.lastHostFramework = hostFw;
      SEC_STATE.frameworkOverride = null;
    }
    return SEC_STATE.frameworkOverride || hostFw;
  }

  function getFrameworkMeta(fw) {
    var map = {
      flask: {
        id: "flask",
        name: "Flask",
        runtime: "Flask 3.x (WSGI / Gunicorn)",
        paradigm: "Décorateurs synchrones, Blueprints & hooks @app.before_request / @app.after_request"
      },
      fastapi: {
        id: "fastapi",
        name: "FastAPI",
        runtime: "FastAPI (ASGI / Uvicorn + Pydantic v2)",
        paradigm: "Injection de dépendances Depends(), modèles Pydantic stricts & middlewares ASGI"
      },
      tornado: {
        id: "tornado",
        name: "Tornado",
        runtime: "Tornado 6.x (IOLoop Asynchrone Non-Bloquant)",
        paradigm: "Sous-classes RequestHandler, prepare(), set_default_headers() & coroutines async/await"
      }
    };
    return map[fw] || map.flask;
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function renderCodeBlock(leftLabel, rightLabel, rawCode) {
    return (
      '<div class="nt-code-block">' +
      '<div class="nt-code-label">' +
      "<span>" + escapeHtml(leftLabel) + "</span>" +
      "<span>" + escapeHtml(rightLabel || "") + "</span>" +
      "</div>" +
      "<pre><code>" + escapeHtml(rawCode) + "</code></pre>" +
      "</div>"
    );
  }

  // ==========================================================================
  // 1. LES 7 BOUCLIERS DE LA DEFENSE EN PROFONDEUR (DEFENSE-IN-DEPTH)
  // ==========================================================================
  var SEVEN_SHIELDS = [
    {
      step: "Bouclier 1",
      title: "Transport TLS 1.3 & Reverse Proxy Nginx",
      code: "TLS 1.3 / HSTS",
      badgeClass: "nt-badge-info",
      summary:
        "Terminaison cryptographique TLS 1.3 en frontal (Nginx / Caddy), désactivation de TLS 1.0/1.1, " +
        "masquage des ports applicatifs internes (liaison locale 127.0.0.1 uniquement) et en-tête HSTS."
    },
    {
      step: "Bouclier 2",
      title: "Quotas, Rate-Limiting & Plafond de Charge Utile",
      code: "HTTP 429 / 413",
      badgeClass: "nt-badge-warn",
      summary:
        "Limitation du débit par IP et par identité (algorithme Token Bucket + en-tête Retry-After), " +
        "plafond strict client_max_body_size / MAX_CONTENT_LENGTH (413) et timeouts de lecture courts."
    },
    {
      step: "Bouclier 3",
      title: "Authentification Cryptographique Forte",
      code: "HTTP 401 + WWW-Authenticate",
      badgeClass: "nt-badge-danger",
      summary:
        "Vérification de l'identité appelante (JWT signé à durée courte, cookie HttpOnly ou mTLS). " +
        "Tout jeton absent, expiré ou à signature invalide est rejeté immédiatement avec WWW-Authenticate."
    },
    {
      step: "Bouclier 4",
      title: "Autorisation RBAC / Scopes & Anti-BOLA",
      code: "HTTP 403 Forbidden",
      badgeClass: "nt-badge-danger",
      summary:
        "Contrôle d'accès fonctionnel (rôles/scopes) doublé d'une vérification systématique d'appartenance " +
        "de la ressource cible (WHERE id = ? AND owner_id = ?) pour neutraliser toute attaque IDOR/BOLA."
    },
    {
      step: "Bouclier 5",
      title: "Validation Stricte du Schéma & Anti-Mass-Assignment",
      code: "HTTP 422 Unprocessable",
      badgeClass: "nt-badge-warn",
      summary:
        "Validation de type, bornes numériques, expressions régulières et liste blanche stricte des " +
        "propriétés autorisées en entrée (rejet des champs non déclarés tels que role ou is_admin)."
    },
    {
      step: "Bouclier 6",
      title: "Requêtes SQL Paramétrées & Filtrage de Sortie",
      code: "Placeholders ? / DTO",
      badgeClass: "nt-badge-success",
      summary:
        "Séparation stricte entre instruction SQL et données via curseurs paramétrés (?) et projection " +
        "explicite des colonnes en sortie (aucune sérialisation brute exposant password_hash ou secrets)."
    },
    {
      step: "Bouclier 7",
      title: "Journalisation d'Audit Structurée & Alerte Temps Réel",
      code: "Audit JSON / SIEM",
      badgeClass: "nt-badge-info",
      summary:
        "Traces JSON horodatées en UTC avec X-Request-ID, identifiant sujet, route, statut HTTP et " +
        "latence, expurgees de tout secret (Authorization, mots de passe, PII) et reliées aux alertes."
    }
  ];

  // ==========================================================================
  // 2. REFERENTIEL COMPLET OWASP API SECURITY TOP 10 (EDITION 2023)
  // ==========================================================================
  var OWASP_TOP_10 = [
    {
      id: "API1:2023",
      family: "access",
      title: "Broken Object Level Authorization (BOLA / IDOR)",
      severity: "Critique",
      httpDefense: "403 Forbidden / 404 Not Found",
      scenario:
        "Un stagiaire authentifié (user_id=42) remplace l'identifiant dans GET /api/v1/dossiers/42 " +
        "par GET /api/v1/dossiers/999. Le serveur vérifie uniquement la validité du jeton JWT sans " +
        "vérifier que le dossier 999 appartient effectivement à l'utilisateur 42, divulguant les " +
        "relevés de notes et coordonnées personnelles d'un tiers.",
      vulnerable:
        "# VULNERABLE : aucune verification d'appartenance (owner_id) sur l'objet demande\n" +
        "row = db.execute(\n" +
        '    "SELECT id, nom, note_finale, iban FROM dossiers WHERE id = ?",\n' +
        "    (dossier_id,)\n" +
        ").fetchone()\n" +
        "return dict(row)  # Fuite directe du dossier d'autrui !",
      fixes: {
        flask:
          "@app.get(\"/api/v1/dossiers/<int:dossier_id>\")\n" +
          "@require_auth\n" +
          "def lire_dossier(dossier_id: int):\n" +
          "    row = g.db.execute(\n" +
          "        \"SELECT id, nom, note_finale FROM dossiers WHERE id = ? AND owner_id = ?\",\n" +
          "        (dossier_id, g.current_user_id),\n" +
          "    ).fetchone()\n" +
          "    if row is None:\n" +
          "        abort(403, description=\"Accès refusé : ce dossier ne vous appartient pas.\")\n" +
          "    return jsonify(dict(row)), 200",
        fastapi:
          "@app.get(\"/api/v1/dossiers/{dossier_id}\", response_model=DossierPublicOut)\n" +
          "def lire_dossier(dossier_id: int, user: UserCtx = Depends(get_current_user), db=Depends(get_db)):\n" +
          "    row = db.execute(\n" +
          "        \"SELECT id, nom, note_finale FROM dossiers WHERE id = ? AND owner_id = ?\",\n" +
          "        (dossier_id, user.id),\n" +
          "    ).fetchone()\n" +
          "    if row is None:\n" +
          "        raise HTTPException(status_code=403, detail=\"Accès interdit sur cette ressource.\")\n" +
          "    return dict(row)",
        tornado:
          "class DossierHandler(AuthenticatedHandler):\n" +
          "    async def get(self, dossier_id: str):\n" +
          "        row = self.db.execute(\n" +
          "            \"SELECT id, nom, note_finale FROM dossiers WHERE id = ? AND owner_id = ?\",\n" +
          "            (int(dossier_id), self.current_user[\"id\"]),\n" +
          "        ).fetchone()\n" +
          "        if row is None:\n" +
          "            raise tornado.web.HTTPError(403, reason=\"Propriété d'objet non autorisée\")\n" +
          "        self.write(dict(row))"
      }
    },
    {
      id: "API2:2023",
      family: "auth",
      title: "Broken Authentication (Jetons faibles, Brute-Force & Expiration)",
      severity: "Critique",
      httpDefense: "401 Unauthorized + WWW-Authenticate",
      scenario:
        "L'endpoint POST /api/v1/auth/login accepte des rafales illimitées d'essais de mots de passe " +
        "(credential stuffing), signe les JWT avec une clé statique faible 'secret123', n'impose aucune " +
        "date d'expiration (exp) et accepte l'algorithme 'none' lors du décodage.",
      vulnerable:
        "# VULNERABLE : secret en dur, pas de claim 'exp', algorithme non verrouille\n" +
        "token = jwt.encode({\"sub\": user_id}, \"secret123\")\n" +
        "# Decodage dangereux sans verification de signature ou d'algorithme :\n" +
        "payload = jwt.decode(token, options={\"verify_signature\": False})",
      fixes: {
        flask:
          "JWT_SECRET = os.environ[\"JWT_SIGNING_KEY\"]  # 256 bits minimum\n\n" +
          "def creer_access_token(user_id: int) -> str:\n" +
          "    now = datetime.now(timezone.utc)\n" +
          "    payload = {\"sub\": str(user_id), \"iat\": now, \"exp\": now + timedelta(minutes=15)}\n" +
          "    return jwt.encode(payload, JWT_SECRET, algorithm=\"HS256\")\n\n" +
          "# Verification stricte avec liste blanche d'algorithme et exigence de exp :\n" +
          "claims = jwt.decode(raw_jwt, JWT_SECRET, algorithms=[\"HS256\"], options={\"require\": [\"exp\", \"sub\"]})",
        fastapi:
          "JWT_SECRET = os.environ[\"JWT_SIGNING_KEY\"]\n" +
          "bearer_scheme = HTTPBearer(auto_error=True)\n\n" +
          "def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):\n" +
          "    try:\n" +
          "        return jwt.decode(\n" +
          "            creds.credentials, JWT_SECRET,\n" +
          "            algorithms=[\"HS256\"], options={\"require\": [\"exp\", \"sub\"]}\n" +
          "        )\n" +
          "    except jwt.PyJWTError:\n" +
          "        raise HTTPException(status_code=401, detail=\"Jeton invalide\", headers={\"WWW-Authenticate\": \"Bearer\"})",
        tornado:
          "class AuthenticatedHandler(tornado.web.RequestHandler):\n" +
          "    def prepare(self):\n" +
          "        auth = self.request.headers.get(\"Authorization\", \"\")\n" +
          "        if not auth.startswith(\"Bearer \"):\n" +
          "            self.set_header(\"WWW-Authenticate\", \"Bearer\")\n" +
          "            raise tornado.web.HTTPError(401, reason=\"Jeton Bearer requis\")\n" +
          "        try:\n" +
          "            self.current_user = jwt.decode(\n" +
          "                auth[7:], os.environ[\"JWT_SIGNING_KEY\"],\n" +
          "                algorithms=[\"HS256\"], options={\"require\": [\"exp\", \"sub\"]}\n" +
          "            )\n" +
          "        except jwt.PyJWTError:\n" +
          "            raise tornado.web.HTTPError(401, reason=\"Jeton expiré ou invalide\")"
      }
    },
    {
      id: "API3:2023",
      family: "access",
      title: "Broken Object Property Level Authorization (Mass Assignment & Fuite)",
      severity: "Élevée",
      httpDefense: "422 Unprocessable Entity + DTO",
      scenario:
        "Lors d'une mise à jour de profil PATCH /api/v1/profil, l'attaquant injecte des propriétés " +
        "internes non prévues par l'interface : {\"nom\": \"Dupont\", \"role\": \"admin\", \"solde_credit\": 99999}. " +
        "Le backend applique dynamiquement tout le dictionnaire JSON sur l'enregistrement SQL.",
      vulnerable:
        "# VULNERABLE : injection directe des cles JSON dans l'objet metier + SELECT *\n" +
        "payload = request.get_json()\n" +
        "for key, val in payload.items():\n" +
        "    setattr(utilisateur, key, val)  # Permet d'ecraser role='admin' !\n" +
        "return utilisateur.__dict__  # Expose aussi password_hash et mfa_secret !",
      fixes: {
        flask:
          "ALLOWED_PROFILE_FIELDS = {\"nom\", \"telephone\", \"organisation\"}\n\n" +
          "@app.patch(\"/api/v1/profil\")\n" +
          "@require_auth\n" +
          "def modifier_profil():\n" +
          "    body = request.get_json(silent=True) or {}\n" +
          "    champs_interdits = set(body.keys()) - ALLOWED_PROFILE_FIELDS\n" +
          "    if champs_interdits:\n" +
          "        return jsonify({\"error\": \"Champs non autorisés\", \"fields\": sorted(champs_interdits)}), 422\n" +
          "    # Seuls nom, telephone, organisation sont mis a jour ; reponse filtree explicitement",
        fastapi:
          "class ProfilUpdateIn(BaseModel):\n" +
          "    model_config = ConfigDict(extra=\"forbid\")  # Rejette 422 tout champ inconnu (role, solde...)\n" +
          "    nom: str = Field(min_length=2, max_length=80)\n" +
          "    telephone: str | None = None\n\n" +
          "class ProfilPublicOut(BaseModel):\n" +
          "    id: int\n" +
          "    nom: str\n" +
          "    telephone: str | None = None  # Masque password_hash par construction",
        tornado:
          "ALLOWED_FIELDS = {\"nom\", \"telephone\"}\n\n" +
          "class ProfilHandler(AuthenticatedHandler):\n" +
          "    async def patch(self):\n" +
          "        body = tornado.escape.json_decode(self.request.body or b\"{}\")\n" +
          "        extra = set(body.keys()) - ALLOWED_FIELDS\n" +
          "        if extra:\n" +
          "            self.set_status(422)\n" +
          "            return self.write({\"error\": \"Propriétés interdites\", \"rejected\": sorted(extra)})\n" +
          "        self.write({\"id\": self.current_user[\"sub\"], \"nom\": body.get(\"nom\")})"
      }
    },
    {
      id: "API4:2023",
      family: "infra",
      title: "Unrestricted Resource Consumption (Absence de Quotas, Pagination & DoS)",
      severity: "Élevée",
      httpDefense: "429 Too Many Requests / 413 Content Too Large",
      scenario:
        "Un attaquant appelle GET /api/v1/stagiaires?limit=10000000 ou envoie un corps JSON de 800 Mo " +
        "sur POST /api/v1/import. Les workers Gunicorn/Uvicorn saturent la RAM (OOM Killer) et la " +
        "base SQLite/PostgreSQL verrouille les lectures pour l'ensemble des utilisateurs légitimes.",
      vulnerable:
        "# VULNERABLE : limit pilote par le client sans borne superieure ni plafond d'octets\n" +
        "limit = int(request.args.get(\"limit\", 1000000))\n" +
        "rows = db.execute(f\"SELECT * FROM stagiaires LIMIT {limit}\").fetchall()",
      fixes: {
        flask:
          "app.config[\"MAX_CONTENT_LENGTH\"] = 1 * 1024 * 1024  # Plafond 1 Mo -> HTTP 413 automatique\n\n" +
          "@app.get(\"/api/v1/stagiaires\")\n" +
          "def lister_stagiaires():\n" +
          "    limit = min(max(request.args.get(\"limit\", 20, type=int), 1), 100)\n" +
          "    offset = max(request.args.get(\"offset\", 0, type=int), 0)\n" +
          "    rows = g.db.execute(\"SELECT id, nom FROM stagiaires LIMIT ? OFFSET ?\", (limit, offset)).fetchall()\n" +
          "    return jsonify({\"limit\": limit, \"offset\": offset, \"data\": [dict(r) for r in rows]}), 200",
        fastapi:
          "@app.get(\"/api/v1/stagiaires\")\n" +
          "def lister_stagiaires(\n" +
          "    limit: int = Query(default=20, ge=1, le=100),  # Plafonne a 100 par Pydantic\n" +
          "    offset: int = Query(default=0, ge=0, le=10000),\n" +
          "    db=Depends(get_db),\n" +
          "):\n" +
          "    rows = db.execute(\"SELECT id, nom FROM stagiaires LIMIT ? OFFSET ?\", (limit, offset)).fetchall()\n" +
          "    return {\"limit\": limit, \"offset\": offset, \"data\": [dict(r) for r in rows]}",
        tornado:
          "# Plafond global de 1 Mo fixe sur le serveur HTTP Tornado :\n" +
          "server = tornado.httpserver.HTTPServer(app, max_body_size=1024 * 1024, body_timeout=10)\n\n" +
          "class StagiairesHandler(BaseHandler):\n" +
          "    async def get(self):\n" +
          "        limit = min(max(int(self.get_argument(\"limit\", \"20\")), 1), 100)\n" +
          "        offset = max(int(self.get_argument(\"offset\", \"0\")), 0)\n" +
          "        rows = self.db.execute(\"SELECT id, nom FROM stagiaires LIMIT ? OFFSET ?\", (limit, offset)).fetchall()\n" +
          "        self.write({\"limit\": limit, \"data\": [dict(r) for r in rows]})"
      }
    },
    {
      id: "API5:2023",
      family: "access",
      title: "Broken Function Level Authorization (BFLA — Escalade Fonctionnelle)",
      severity: "Critique",
      httpDefense: "403 Forbidden (RBAC Explicite)",
      scenario:
        "En inspectant le bundle JavaScript frontal, un utilisateur standard découvre l'endpoint " +
        "administratif DELETE /api/v1/admin/utilisateurs/15 ou GET /api/v1/admin/export-comptable. " +
        "La route vérifie que l'appelant est connecté (@require_auth) mais omet de vérifier son rôle.",
      vulnerable:
        "# VULNERABLE : verifie l'authentification (401) mais ignore le role metier (403)\n" +
        "@app.delete(\"/api/v1/admin/utilisateurs/<int:uid>\")\n" +
        "@require_auth\n" +
        "def purger_utilisateur(uid: int):\n" +
        "    db.execute(\"DELETE FROM utilisateurs WHERE id = ?\", (uid,))",
      fixes: {
        flask:
          "def require_role(*allowed_roles: str):\n" +
          "    def decorator(fn):\n" +
          "        @wraps(fn)\n" +
          "        def wrapper(*args, **kwargs):\n" +
          "            if getattr(g, \"current_role\", None) not in allowed_roles:\n" +
          "                abort(403, description=\"Privilège administrateur requis.\")\n" +
          "            return fn(*args, **kwargs)\n" +
          "        return wrapper\n" +
          "    return decorator\n\n" +
          "@app.delete(\"/api/v1/admin/utilisateurs/<int:uid>\")\n" +
          "@require_auth\n" +
          "@require_role(\"admin\")\n" +
          "def purger_utilisateur(uid: int): ...",
        fastapi:
          "def require_admin(user: UserCtx = Depends(get_current_user)) -> UserCtx:\n" +
          "    if user.role != \"admin\":\n" +
          "        raise HTTPException(status_code=403, detail=\"Rôle administrateur requis.\")\n" +
          "    return user\n\n" +
          "@app.delete(\"/api/v1/admin/utilisateurs/{uid}\", status_code=204)\n" +
          "def purger_utilisateur(uid: int, admin: UserCtx = Depends(require_admin), db=Depends(get_db)):\n" +
          "    db.execute(\"DELETE FROM utilisateurs WHERE id = ?\", (uid,))",
        tornado:
          "class AdminPurgeUserHandler(AuthenticatedHandler):\n" +
          "    async def delete(self, uid: str):\n" +
          "        if self.current_user.get(\"role\") != \"admin\":\n" +
          "            raise tornado.web.HTTPError(403, reason=\"Privilège administrateur requis\")\n" +
          "        self.db.execute(\"DELETE FROM utilisateurs WHERE id = ?\", (int(uid),))\n" +
          "        self.set_status(204)\n" +
          "        self.finish()"
      }
    },
    {
      id: "API6:2023",
      family: "auth",
      title: "Unrestricted Access to Sensitive Business Flows (Scalping & Automatisation)",
      severity: "Élevée",
      httpDefense: "409 Conflict / 429 Quota Métier + Idempotency-Key",
      scenario:
        "Un script automatisé réserve en 400 millisecondes la totalité des 30 places d'une session de " +
        "formation certifiante via POST /api/v1/inscriptions, ou déclenche une double facturation lors " +
        "d'un ré-essai réseau faute de clé d'idempotence et de contrainte d'unicité métier.",
      vulnerable:
        "# VULNERABLE : aucune cle d'idempotence, ni quota par candidat, ni transaction atomique\n" +
        "places = db.execute(\"SELECT places_dispo FROM formations WHERE id = ?\", (fid,)).fetchone()[0]\n" +
        "if places > 0:\n" +
        "    db.execute(\"INSERT INTO inscriptions (user_id, formation_id) VALUES (?, ?)\", (uid, fid))",
      fixes: {
        flask:
          "@app.post(\"/api/v1/inscriptions\")\n" +
          "@require_auth\n" +
          "def inscrire_stagiaire():\n" +
          "    idem_key = request.headers.get(\"Idempotency-Key\", \"\").strip()\n" +
          "    if len(idem_key) < 16:\n" +
          "        return jsonify({\"error\": \"En-tête Idempotency-Key obligatoire\"}), 400\n" +
          "    # Transaction atomique + contrainte UNIQUE(user_id, formation_id) + verification stock SQL :\n" +
          "    cur = g.db.execute(\n" +
          "        \"UPDATE formations SET places_dispo = places_dispo - 1 WHERE id = ? AND places_dispo > 0\",\n" +
          "        (fid,),\n" +
          "    )\n" +
          "    if cur.rowcount == 0:\n" +
          "        return jsonify({\"error\": \"Session complète ou quota atteint\"}), 409",
        fastapi:
          "@app.post(\"/api/v1/inscriptions\", status_code=201)\n" +
          "def inscrire_stagiaire(\n" +
          "    payload: InscriptionIn,\n" +
          "    idempotency_key: str = Header(min_length=16, alias=\"Idempotency-Key\"),\n" +
          "    user: UserCtx = Depends(get_current_user), db=Depends(get_db),\n" +
          "):\n" +
          "    if deja_traitee(db, user.id, idempotency_key):\n" +
          "        return reponse_memorisee(db, user.id, idempotency_key)\n" +
          "    # Verrou atomique SQL + plafond max 2 inscriptions actives par candidat",
        tornado:
          "class InscriptionHandler(AuthenticatedHandler):\n" +
          "    async def post(self):\n" +
          "        idem_key = self.request.headers.get(\"Idempotency-Key\", \"\").strip()\n" +
          "        if len(idem_key) < 16:\n" +
          "            raise tornado.web.HTTPError(400, reason=\"Idempotency-Key requis\")\n" +
          "        # Verification atomique du quota candidat + contrainte UNIQUE SQLite :\n" +
          "        cur = self.db.execute(\n" +
          "            \"UPDATE formations SET places = places - 1 WHERE id = ? AND places > 0\", (fid,)\n" +
          "        )\n" +
          "        if cur.rowcount == 0:\n" +
          "            raise tornado.web.HTTPError(409, reason=\"Plus aucune place disponible\")"
      }
    },
    {
      id: "API7:2023",
      family: "ssrf",
      title: "Server-Side Request Forgery (SSRF vers Métadonnées Cloud & Réseau Interne)",
      severity: "Critique",
      httpDefense: "400 / 422 + Validation DNS & Blocage RFC 1918 / Link-Local",
      scenario:
        "Un endpoint d'import d'avatar POST /api/v1/profil/avatar-url accepte une URL fournie par le " +
        "client. L'attaquant soumet http://169.254.169.254/latest/meta-data/iam/security-credentials/ " +
        "ou http://127.0.0.1:6379/ et exfiltre les clés IAM du serveur Cloud ou interroge Redis interne.",
      vulnerable:
        "# VULNERABLE : requete sortante directe vers une URL arbitraire fournie par le client\n" +
        "avatar_url = request.json[\"avatar_url\"]\n" +
        "resp = urllib.request.urlopen(avatar_url, timeout=5)  # SSRF critique !\n" +
        "return resp.read()",
      fixes: {
        flask:
          "def verifier_url_externe_sure(raw_url: str) -> str:\n" +
          "    parsed = urllib.parse.urlparse(raw_url)\n" +
          "    if parsed.scheme != \"https\" or not parsed.hostname:\n" +
          "        abort(422, description=\"Seul le schéma HTTPS public est autorisé.\")\n" +
          "    for _, _, _, _, sockaddr in socket.getaddrinfo(parsed.hostname, 443):\n" +
          "        ip = ipaddress.ip_address(sockaddr[0])\n" +
          "        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:\n" +
          "            abort(403, description=\"Cible réseau interne interdite (Anti-SSRF).\")\n" +
          "    return raw_url",
        fastapi:
          "def valider_cible_https_publique(raw_url: str) -> str:\n" +
          "    parsed = urllib.parse.urlparse(raw_url)\n" +
          "    if parsed.scheme != \"https\" or parsed.hostname not in {\"cdn.isgp.dz\", \"media.partenaire.dz\"}:\n" +
          "        raise HTTPException(status_code=422, detail=\"Domaine distant hors liste blanche.\")\n" +
          "    ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))\n" +
          "    if ip.is_private or ip.is_loopback or ip.is_link_local:\n" +
          "        raise HTTPException(status_code=403, detail=\"Adresse IP interne bloquée (Anti-SSRF).\")\n" +
          "    return raw_url",
        tornado:
          "ALLOWED_HOSTS = {\"cdn.isgp.dz\", \"media.partenaire.dz\"}\n\n" +
          "async def telecharger_ressource_sure(raw_url: str) -> bytes:\n" +
          "    parsed = urllib.parse.urlparse(raw_url)\n" +
          "    if parsed.scheme != \"https\" or parsed.hostname not in ALLOWED_HOSTS:\n" +
          "        raise tornado.web.HTTPError(422, reason=\"Hôte distant non autorisé\")\n" +
          "    ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname))\n" +
          "    if ip.is_private or ip.is_loopback or ip.is_link_local:\n" +
          "        raise tornado.web.HTTPError(403, reason=\"SSRF bloqué : IP privée ou link-local\")\n" +
          "    client = tornado.httpclient.AsyncHTTPClient()\n" +
          "    resp = await client.fetch(raw_url, follow_redirects=False, request_timeout=4.0)\n" +
          "    return resp.body"
      }
    },
    {
      id: "API8:2023",
      family: "infra",
      title: "Security Misconfiguration (Debug actif, Stacktraces & CORS permissif)",
      severity: "Élevée",
      httpDefense: "Debug=False + Gestionnaire 500 Opaque + CORS Strict",
      scenario:
        "L'API est déployée en production avec debug=True (exposant la console interactive Werkzeug ou " +
        "les traces SQL complètes lors d'une exception 500) et renvoie Access-Control-Allow-Origin: * " +
        "combiné à Access-Control-Allow-Credentials: true.",
      vulnerable:
        "# VULNERABLE : console de debug en production + fuite des chemins systeme et SQL\n" +
        "app.run(host=\"0.0.0.0\", port=5000, debug=True)\n" +
        "# En cas d'erreur : renvoie traceback Python complet et variables locales au client !",
      fixes: {
        flask:
          "app.config.update(DEBUG=False, TESTING=False, PROPAGATE_EXCEPTIONS=False)\n\n" +
          "@app.errorhandler(Exception)\n" +
          "def gerer_erreur_interne(exc: Exception):\n" +
          "    req_id = request.headers.get(\"X-Request-ID\", \"n/a\")\n" +
          "    app.logger.exception(\"Erreur interne [req_id=%s]\", req_id)\n" +
          "    return jsonify({\"error\": \"Erreur interne du serveur\", \"request_id\": req_id}), 500",
        fastapi:
          "# Desactiver Swagger/Redoc publics si API interne + masquer toute stacktrace :\n" +
          "app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)\n\n" +
          "@app.exception_handler(Exception)\n" +
          "async def global_exception_handler(request: Request, exc: Exception):\n" +
          "    logger.exception(\"Erreur non geree sur %s\", request.url.path)\n" +
          "    return JSONResponse(status_code=500, content={\"error\": \"Erreur interne opaque\"})",
        tornado:
          "app = tornado.web.Application(routes, debug=False)  # Jamais debug=True en production\n\n" +
          "class BaseSecureHandler(tornado.web.RequestHandler):\n" +
          "    def write_error(self, status_code: int, **kwargs):\n" +
          "        self.set_header(\"Content-Type\", \"application/json\")\n" +
          "        msg = \"Erreur interne du serveur\" if status_code >= 500 else self._reason\n" +
          "        self.finish({\"status\": status_code, \"error\": msg})"
      }
    },
    {
      id: "API9:2023",
      family: "infra",
      title: "Improper Inventory Management (API Fantôme /api/v1 & Routes de Debug)",
      severity: "Moyenne à Élevée",
      httpDefense: "410 Gone + En-têtes Sunset / Deprecation",
      scenario:
        "L'équipe sécurise /api/v2/auth avec MFA et limitation de débit, mais oublie de désactiver " +
        "l'ancienne /api/v1/auth et un endpoint temporaire /api/debug/dump-env connectés à la même " +
        "base de données de production.",
      vulnerable:
        "# VULNERABLE : ancienne v1 non maintenue et route de diagnostic laissees actives\n" +
        "app.register_blueprint(legacy_v1_bp, url_prefix=\"/api/v1\")  # Sans MFA ni rate-limit\n" +
        "@app.get(\"/api/debug/env\")\n" +
        "def dump_env(): return dict(os.environ)  # Fuite totale des secrets !",
      fixes: {
        flask:
          "# Retrait definitif des versions obsoletes via statut semantique 410 Gone :\n" +
          "@app.route(\"/api/v1/<path:subpath>\", methods=[\"GET\", \"POST\", \"PUT\", \"PATCH\", \"DELETE\"])\n" +
          "def api_v1_retiree(subpath: str):\n" +
          "    resp = jsonify({\"error\": \"API v1 retiree. Migrez vers /api/v2.\"} )\n" +
          "    resp.headers[\"Sunset\"] = \"Wed, 01 Jan 2025 00:00:00 GMT\"\n" +
          "    return resp, 410",
        fastapi:
          "@app.api_route(\"/api/v1/{subpath:path}\", methods=[\"GET\", \"POST\", \"PUT\", \"PATCH\", \"DELETE\"])\n" +
          "async def api_v1_retiree(subpath: str):\n" +
          "    return JSONResponse(\n" +
          "        status_code=410,\n" +
          "        headers={\"Sunset\": \"Wed, 01 Jan 2025 00:00:00 GMT\", \"Link\": \"</api/v2>; rel=successor-version\"},\n" +
          "        content={\"error\": \"Version /api/v1 decommissionnee. Utilisez /api/v2.\"},\n" +
          "    )",
        tornado:
          "class DeprecatedV1Handler(tornado.web.RequestHandler):\n" +
          "    def prepare(self):\n" +
          "        self.set_status(410)\n" +
          "        self.set_header(\"Sunset\", \"Wed, 01 Jan 2025 00:00:00 GMT\")\n" +
          "        self.finish({\"error\": \"Branche /api/v1 desactivee. Utilisez /api/v2.\"})\n" +
          "# Montage explicite dans le routeur : (r\"/api/v1/.*\", DeprecatedV1Handler)"
      }
    },
    {
      id: "API10:2023",
      family: "ssrf",
      title: "Unsafe Consumption of APIs (Webhooks non signés & Réponses Tierces)",
      severity: "Élevée",
      httpDefense: "401 Signature HMAC-SHA256 + Validation Schéma Sortant",
      scenario:
        "Le backend consomme un Webhook de paiement POST /webhooks/paiement sans vérifier la signature " +
        "cryptographique HMAC ni l'horodatage, permettant à un attaquant externe de forger un événement " +
        "{\"facture_id\": 88, \"statut\": \"PAYEE\"} et de valider gratuitement sa commande.",
      vulnerable:
        "# VULNERABLE : confiance aveugle dans un appel Webhook entrant sans signature HMAC\n" +
        "@app.post(\"/webhooks/paiement\")\n" +
        "def webhook_paiement():\n" +
        "    data = request.get_json()\n" +
        "    marquer_facture_payee(data[\"facture_id\"])  # Usurpation triviale !\n" +
        "    return \"ok\", 200",
      fixes: {
        flask:
          "@app.post(\"/webhooks/paiement\")\n" +
          "def webhook_paiement():\n" +
          "    raw_body = request.get_data()  # Octets bruts exacts avant tout parsing JSON\n" +
          "    ts = request.headers.get(\"X-Webhook-Timestamp\", \"0\")\n" +
          "    sig = request.headers.get(\"X-Webhook-Signature\", \"\")\n" +
          "    if abs(time.time() - int(ts)) > 300:\n" +
          "        abort(401, description=\"Horodatage Webhook hors fenetre anti-rejeu (300s).\")\n" +
          "    expected = \"sha256=\" + hmac.new(WEBHOOK_SECRET, ts.encode() + b\".\" + raw_body, hashlib.sha256).hexdigest()\n" +
          "    if not hmac.compare_digest(sig, expected):\n" +
          "        abort(401, description=\"Signature HMAC-SHA256 invalide.\")",
        fastapi:
          "@app.post(\"/webhooks/paiement\")\n" +
          "async def webhook_paiement(\n" +
          "    request: Request,\n" +
          "    x_webhook_timestamp: int = Header(...),\n" +
          "    x_webhook_signature: str = Header(...),\n" +
          "):\n" +
          "    if abs(time.time() - x_webhook_timestamp) > 300:\n" +
          "        raise HTTPException(status_code=401, detail=\"Fenetre anti-rejeu depassee.\")\n" +
          "    raw = await request.body()\n" +
          "    expected = \"sha256=\" + hmac.new(WEBHOOK_SECRET, f\"{x_webhook_timestamp}.\".encode() + raw, hashlib.sha256).hexdigest()\n" +
          "    if not hmac.compare_digest(x_webhook_signature, expected):\n" +
          "        raise HTTPException(status_code=401, detail=\"Signature HMAC invalide.\")",
        tornado:
          "class PaymentWebhookHandler(tornado.web.RequestHandler):\n" +
          "    async def post(self):\n" +
          "        ts = int(self.request.headers.get(\"X-Webhook-Timestamp\", \"0\"))\n" +
          "        sig = self.request.headers.get(\"X-Webhook-Signature\", \"\")\n" +
          "        if abs(time.time() - ts) > 300:\n" +
          "            raise tornado.web.HTTPError(401, reason=\"Rejeu Webhook detecte\")\n" +
          "        msg = f\"{ts}.\".encode() + self.request.body\n" +
          "        expected = \"sha256=\" + hmac.new(WEBHOOK_SECRET, msg, hashlib.sha256).hexdigest()\n" +
          "        if not hmac.compare_digest(sig, expected):\n" +
          "            raise tornado.web.HTTPError(401, reason=\"Signature HMAC invalide\")"
      }
    }
  ];

  // ==========================================================================
  // 3. MATRICE D'AUTHENTIFICATION, CRYPTOGRAPHIE PRATIQUE & EN-TETES HTTP
  // ==========================================================================
  var AUTH_MATRIX = [
    {
      mechanism: "Clé API (X-API-Key / Authorization: ApiKey)",
      idealUse: "Scripts serveur-à-serveur (M2M) simples, intégrations internes à faible surface, quotas partenaires.",
      risks: "Secret longue durée, aucune identité utilisateur fine, fuite fréquente dans un dépôt Git ou bundle JS.",
      storage: "Variables d'environnement serveur ou gestionnaire de secrets (jamais dans un navigateur public).",
      revocation: "Immédiate en base SQL/Redis (stocker uniquement le haché SHA-256 de la clé API, jamais le clair)."
    },
    {
      mechanism: "Cookie de Session Signé (HttpOnly, Secure, SameSite=Lax + CSRF)",
      idealUse: "Applications web monolithiques ou SPA servies sur le même domaine racine (Portail Stagiaires ISGP).",
      risks: "Cross-Site Request Forgery (CSRF) sur mutations POST/PUT/DELETE si SameSite=None ou absence de jeton anti-CSRF.",
      storage: "Cookie navigateur géré par le moteur HTTP avec drapeaux HttpOnly (anti-XSS), Secure (TLS) et SameSite=Lax.",
      revocation: "Immédiate côté serveur (suppression de l'identifiant de session Redis/SQLite ou rotation de clé)."
    },
    {
      mechanism: "Bearer Token / JWT Signé (Access court 5-15 min + Refresh révocable)",
      idealUse: "Architectures microservices sans état (stateless), applications mobiles natives, passerelles multi-backends.",
      risks: "Impossible d'invalider nativement un JWT avant exp sans liste noire ; vol dans localStorage en cas de faille XSS.",
      storage: "Mémoire vive JavaScript (Access Token) + Cookie HttpOnly restreint au chemin /auth/refresh (Refresh Token).",
      revocation: "Expiration très courte de l'Access Token (5-15 min) + table de révocation jti / rotation du Refresh Token."
    },
    {
      mechanism: "OAuth 2.0 + OIDC (Authorization Code + PKCE) / mTLS",
      idealUse: "Délégation d'identité SSO d'entreprise (OIDC + PKCE) et flux inter-services critiques Zero-Trust (mTLS).",
      risks: "Mauvaise validation du paramètre state (CSRF OAuth), URI de redirection ouverte ou omission de code_verifier PKCE.",
      storage: "Serveur Backend-for-Frontend (BFF) pour les jetons OIDC ; magasin matériel PKCS#11 / KMS pour certificats mTLS.",
      revocation: "Endpoint standard RFC 7009 (/oauth/revoke) + listes CRL / OCSP et certificats X.509 à courte durée (24h)."
    }
  ];

  var CRYPTO_GOLDEN_RULES = [
    {
      title: "1. Gestion des Secrets Hors Code Source (os.environ & Entropie)",
      badge: "Zéro Secret en Dur",
      rationale:
        "Interdiction absolue de commiter une clé secrète dans le code Python. Générer au moins 256 bits " +
        "d'entropie via secrets.token_urlsafe(32) et échouer immédiatement au démarrage si la variable manque.",
      snippets: {
        flask:
          "import os, secrets\n" +
          "# Generation hors-ligne : python -c \"import secrets; print(secrets.token_urlsafe(32))\"\n" +
          "app.config[\"SECRET_KEY\"] = os.environ[\"FLASK_SECRET_KEY\"]  # KeyError explicite si oubliee",
        fastapi:
          "from pydantic_settings import BaseSettings\n" +
          "class SecuritySettings(BaseSettings):\n" +
          "    jwt_signing_key: str  # Charge automatiquement JWT_SIGNING_KEY depuis l'environnement\n" +
          "settings = SecuritySettings()",
        tornado:
          "import os\n" +
          "COOKIE_SECRET = os.environ[\"TORNADO_COOKIE_SECRET\"]\n" +
          "app = tornado.web.Application(routes, cookie_secret=COOKIE_SECRET, xsrf_cookies=True)"
      }
    },
    {
      title: "2. Hachage de Mots de Passe (PBKDF2-HMAC-SHA256 / Argon2 + Sel)",
      badge: "Anti-Rainbow-Table",
      rationale:
        "Un condensat rapide (MD5, SHA-256 nu) se casse à plusieurs milliards d'essais/seconde sur GPU. " +
        "Utiliser une fonction de dérivation lente avec sel aléatoire unique de 16 octets par utilisateur.",
      snippets: {
        flask:
          "from werkzeug.security import generate_password_hash, check_password_hash\n" +
          "# Utilise scrypt ou pbkdf2:sha256:600000 avec sel cryptographique unique :\n" +
          "pw_hash = generate_password_hash(mot_de_passe, method=\"pbkdf2:sha256:600000\", salt_length=16)",
        fastapi:
          "import os, hashlib, binascii\n" +
          "def hacher_mot_de_passe(clair: str) -> str:\n" +
          "    sel = os.urandom(16)\n" +
          "    dk = hashlib.pbkdf2_hmac(\"sha256\", clair.encode(\"utf-8\"), sel, 600_000)\n" +
          "    return binascii.hexlify(sel).decode() + \"$\" + binascii.hexlify(dk).decode()",
        tornado:
          "# En boucle asynchrone Tornado, deporter le calcul CPU intensif dans un ThreadPoolExecutor :\n" +
          "pw_hash = await tornado.ioloop.IOLoop.current().run_in_executor(\n" +
          "    None, hashlib.pbkdf2_hmac, \"sha256\", clair.encode(\"utf-8\"), os.urandom(16), 600_000\n" +
          ")"
      }
    },
    {
      title: "3. Comparaison à Temps Constant (hmac.compare_digest)",
      badge: "Anti-Timing-Attack",
      rationale:
        "L'opérateur == s'arrête dès le premier octet différent, permettant à un attaquant de deviner " +
        "une clé API ou un MAC octet par octet en mesurant les écarts de temps de réponse.",
      snippets: {
        flask:
          "import hmac\n" +
          "fournie = request.headers.get(\"X-API-Key\", \"\")\n" +
          "if not hmac.compare_digest(fournie.encode(\"utf-8\"), CLE_ATTENDUE.encode(\"utf-8\")):\n" +
          "    abort(401)",
        fastapi:
          "import hmac\n" +
          "def verifier_cle_api(x_api_key: str = Header(...)):\n" +
          "    if not hmac.compare_digest(x_api_key.encode(), settings.internal_api_key.encode()):\n" +
          "        raise HTTPException(status_code=401, detail=\"Cle API invalide\")",
        tornado:
          "import hmac\n" +
          "fournie = self.request.headers.get(\"X-API-Key\", \"\")\n" +
          "if not hmac.compare_digest(fournie.encode(\"utf-8\"), CLE_ATTENDUE.encode(\"utf-8\")):\n" +
          "    raise tornado.web.HTTPError(401, reason=\"Cle API invalide\")"
      }
    },
    {
      title: "4. Vérification de Signature Webhook (HMAC-SHA256 & Anti-Rejeu)",
      badge: "Intégrité & Fraîcheur",
      rationale:
        "Concaténer l'horodatage X-Webhook-Timestamp et les octets bruts du corps HTTP avant calcul " +
        "HMAC-SHA256, rejeter tout écart > 300 secondes et comparer avec hmac.compare_digest.",
      snippets: {
        flask:
          "raw = request.get_data()  # Octets bruts non re-serialises\n" +
          "mac = hmac.new(SECRET, f\"{ts}.\".encode() + raw, hashlib.sha256).hexdigest()\n" +
          "valide = (abs(time.time() - int(ts)) <= 300) and hmac.compare_digest(sig, f\"sha256={mac}\")",
        fastapi:
          "raw = await request.body()\n" +
          "mac = hmac.new(SECRET, f\"{ts}.\".encode() + raw, hashlib.sha256).hexdigest()\n" +
          "if abs(time.time() - ts) > 300 or not hmac.compare_digest(sig, f\"sha256={mac}\"):\n" +
          "    raise HTTPException(status_code=401, detail=\"Webhook rejete\")",
        tornado:
          "raw = self.request.body\n" +
          "mac = hmac.new(SECRET, f\"{ts}.\".encode() + raw, hashlib.sha256).hexdigest()\n" +
          "if abs(time.time() - ts) > 300 or not hmac.compare_digest(sig, f\"sha256={mac}\"):\n" +
          "    raise tornado.web.HTTPError(401, reason=\"Webhook rejete\")"
      }
    }
  ];

  var SECURITY_HEADERS_ROWS = [
    {
      header: "Strict-Transport-Security",
      value: "max-age=63072000; includeSubDomains; preload",
      role: "Force exclusivement HTTPS pendant 24 mois et neutralise toute attaque SSL-Stripping (MITM)."
    },
    {
      header: "Content-Security-Policy",
      value: "default-src 'none'; frame-ancestors 'none'",
      role: "Pour une API JSON pure : interdit toute exécution de script et tout encadrement iframe (Clickjacking)."
    },
    {
      header: "X-Content-Type-Options",
      value: "nosniff",
      role: "Interdit au navigateur de deviner le type MIME d'une réponse JSON et de l'interpréter comme HTML/JS."
    },
    {
      header: "Cache-Control",
      value: "no-store",
      role: "Empêche les caches partagés ou proxies d'enregistrer sur disque des jetons ou données personnelles."
    },
    {
      header: "Access-Control-Allow-Origin (CORS)",
      value: "https://portail.isgp.dz (Liste blanche explicite)",
      role: "N'autorise que les origines frontales homologuées. Ne jamais combiner '*' avec Allow-Credentials: true."
    }
  ];

  var PERIMETER_MIDDLEWARE = {
    flask:
      "ALLOWED_ORIGINS = {\"https://portail.isgp.dz\", \"https://admin.isgp.dz\"}\n\n" +
      "@app.after_request\n" +
      "def appliquer_bouclier_entetes(resp):\n" +
      "    resp.headers[\"Strict-Transport-Security\"] = \"max-age=63072000; includeSubDomains; preload\"\n" +
      "    resp.headers[\"Content-Security-Policy\"] = \"default-src 'none'; frame-ancestors 'none'\"\n" +
      "    resp.headers[\"X-Content-Type-Options\"] = \"nosniff\"\n" +
      "    resp.headers[\"Cache-Control\"] = \"no-store\"\n" +
      "    origin = request.headers.get(\"Origin\", \"\")\n" +
      "    if origin in ALLOWED_ORIGINS:\n" +
      "        resp.headers[\"Access-Control-Allow-Origin\"] = origin\n" +
      "        resp.headers[\"Vary\"] = \"Origin\"\n" +
      "    return resp",
    fastapi:
      "app.add_middleware(\n" +
      "    CORSMiddleware,\n" +
      "    allow_origins=[\"https://portail.isgp.dz\", \"https://admin.isgp.dz\"],\n" +
      "    allow_credentials=True, allow_methods=[\"GET\", \"POST\", \"PATCH\", \"DELETE\"], allow_headers=[\"Authorization\", \"Content-Type\"],\n" +
      ")\n\n" +
      "@app.middleware(\"http\")\n" +
      "async def security_headers_middleware(request: Request, call_next):\n" +
      "    resp = await call_next(request)\n" +
      "    resp.headers[\"Strict-Transport-Security\"] = \"max-age=63072000; includeSubDomains; preload\"\n" +
      "    resp.headers[\"Content-Security-Policy\"] = \"default-src 'none'; frame-ancestors 'none'\"\n" +
      "    resp.headers[\"X-Content-Type-Options\"] = \"nosniff\"\n" +
      "    resp.headers[\"Cache-Control\"] = \"no-store\"\n" +
      "    return resp",
    tornado:
      "ALLOWED_ORIGINS = {\"https://portail.isgp.dz\", \"https://admin.isgp.dz\"}\n\n" +
      "class HardenedBaseHandler(tornado.web.RequestHandler):\n" +
      "    def set_default_headers(self):\n" +
      "        self.set_header(\"Strict-Transport-Security\", \"max-age=63072000; includeSubDomains; preload\")\n" +
      "        self.set_header(\"Content-Security-Policy\", \"default-src 'none'; frame-ancestors 'none'\")\n" +
      "        self.set_header(\"X-Content-Type-Options\", \"nosniff\")\n" +
      "        self.set_header(\"Cache-Control\", \"no-store\")\n" +
      "        origin = self.request.headers.get(\"Origin\", \"\")\n" +
      "        if origin in ALLOWED_ORIGINS:\n" +
      "            self.set_header(\"Access-Control-Allow-Origin\", origin)\n" +
      "            self.set_header(\"Vary\", \"Origin\")"
  };

  // ==========================================================================
  // 4. DONNEES DU SIMULATEUR INTERACTIF D'ATTAQUE & BLINDAGE
  // ==========================================================================
  var SIM_SCENARIOS = {
    bola: {
      id: "bola",
      label: "1. Attaque BOLA sur /api/v1/dossiers/999",
      owaspRef: "OWASP API1:2023 — Broken Object Level Authorization",
      defaultTrace: "GET /api/v1/dossiers/999 (Jeton valide : sub=42, role=stagiaire)",
      httpRequest:
        "GET /api/v1/dossiers/999 HTTP/1.1\n" +
        "Host: api.isgp.dz\n" +
        "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.sub_42_stagiaire\n" +
        "Accept: application/json",
      vulnerableStatus: "200 OK — FUITE CRITIQUE",
      vulnerableResponse:
        "HTTP/1.1 200 OK\n" +
        "Content-Type: application/json\n\n" +
        "{\n" +
        '  "id": 999,\n' +
        '  "owner_id": 108,\n' +
        '  "nom_complet": "Amira Benali",\n' +
        '  "moyenne_generale": 17.85,\n' +
        '  "iban_remboursement": "DZ59 0002 0018 4491 0009 12"\n' +
        "}",
      hardenedStatus: "403 Forbidden — ATTAQUE BLOQUÉE",
      hardenedResponse:
        "HTTP/1.1 403 Forbidden\n" +
        "Content-Type: application/problem+json\n" +
        "Cache-Control: no-store\n\n" +
        "{\n" +
        '  "type": "https://api.isgp.dz/errors/forbidden-object",\n' +
        '  "title": "Accès refusé à la ressource",\n' +
        '  "status": 403,\n' +
        '  "detail": "Le dossier #999 n\'appartient pas au sujet authentifié (sub=42)."\n' +
        "}",
      analysis:
        "L'attaquant possède un jeton JWT authentique (sub=42) mais énumère l'identifiant séquentiel 999. " +
        "Seul un prédicat SQL couplant l'identifiant d'objet et l'identifiant du propriétaire connecté bloque l'exfiltration.",
      defenseLine: {
        flask:
          'row = g.db.execute("SELECT id, nom FROM dossiers WHERE id = ? AND owner_id = ?", (dossier_id, g.current_user_id)).fetchone()\n' +
          "if row is None:\n" +
          '    abort(403, description="Accès refusé : violation de propriété d\'objet (Anti-BOLA).")',
        fastapi:
          'row = db.execute("SELECT id, nom FROM dossiers WHERE id = ? AND owner_id = ?", (dossier_id, user.id)).fetchone()\n' +
          "if row is None:\n" +
          '    raise HTTPException(status_code=403, detail="Accès interdit : propriétaire non concordant.")',
        tornado:
          'row = self.db.execute("SELECT id, nom FROM dossiers WHERE id = ? AND owner_id = ?", (int(dossier_id), self.current_user["id"])).fetchone()\n' +
          "if row is None:\n" +
          '    raise tornado.web.HTTPError(403, reason="Anti-BOLA : ressource appartenant à un tiers")'
      }
    },
    mass_assignment: {
      id: "mass_assignment",
      label: '2. Mass Assignment PATCH {"role": "admin"}',
      owaspRef: "OWASP API3:2023 — Broken Object Property Level Authorization",
      defaultTrace: 'PATCH /api/v1/utilisateurs/me  Body: {"nom": "Karim", "role": "admin"}',
      httpRequest:
        "PATCH /api/v1/utilisateurs/me HTTP/1.1\n" +
        "Host: api.isgp.dz\n" +
        "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.sub_42_stagiaire\n" +
        "Content-Type: application/json\n\n" +
        '{\n  "nom": "Karim Mansouri",\n  "role": "admin",\n  "quota_export": 999999\n}',
      vulnerableStatus: "200 OK — FUITE CRITIQUE (ESCALADE DE PRIVILÈGES)",
      vulnerableResponse:
        "HTTP/1.1 200 OK\n" +
        "Content-Type: application/json\n\n" +
        "{\n" +
        '  "id": 42,\n' +
        '  "nom": "Karim Mansouri",\n' +
        '  "role": "admin",\n' +
        '  "quota_export": 999999\n' +
        "}",
      hardenedStatus: "422 Unprocessable Entity — ATTAQUE BLOQUÉE",
      hardenedResponse:
        "HTTP/1.1 422 Unprocessable Entity\n" +
        "Content-Type: application/problem+json\n\n" +
        "{\n" +
        '  "title": "Propriétés non autorisées détectées",\n' +
        '  "status": 422,\n' +
        '  "rejected_fields": ["quota_export", "role"],\n' +
        '  "allowed_fields": ["nom", "organisation", "telephone"]\n' +
        "}",
      analysis:
        "En liant aveuglément le corps JSON aux colonnes SQL, le serveur permet l'auto-promotion au rôle 'admin'. " +
        "Le schéma d'entrée doit appliquer une liste blanche stricte et rejeter tout attribut non déclaré en 422.",
      defenseLine: {
        flask:
          'champs_interdits = set(payload.keys()) - {"nom", "telephone", "organisation"}\n' +
          "if champs_interdits:\n" +
          '    return jsonify({"error": "Mass Assignment bloqué", "rejected": sorted(champs_interdits)}), 422',
        fastapi:
          "class UserPatchDTO(BaseModel):\n" +
          '    model_config = ConfigDict(extra="forbid")  # Rejet automatique HTTP 422 sur role / quota_export\n' +
          "    nom: str = Field(min_length=2, max_length=80)\n" +
          "    telephone: str | None = None",
        tornado:
          'extra = set(payload.keys()) - {"nom", "telephone", "organisation"}\n' +
          "if extra:\n" +
          "    self.set_status(422)\n" +
          '    return self.finish({"error": "Champs privilégiés interdits", "rejected": sorted(extra)})'
      }
    },
    webhook_hmac: {
      id: "webhook_hmac",
      label: "3. Usurpation Webhook sans signature HMAC",
      owaspRef: "OWASP API10:2023 — Unsafe Consumption of APIs & Webhooks",
      defaultTrace: 'POST /webhooks/paiement (En-tête X-Webhook-Signature absent ou forgé)',
      httpRequest:
        "POST /webhooks/paiement HTTP/1.1\n" +
        "Host: api.isgp.dz\n" +
        "Content-Type: application/json\n" +
        "X-Webhook-Timestamp: 1700000100\n" +
        "X-Webhook-Signature: sha256=0000deadbeef0000forgedsignature\n\n" +
        '{\n  "event": "invoice.paid",\n  "dossier_id": 42,\n  "montant_dzd": 85000\n}',
      vulnerableStatus: "200 OK — FUITE CRITIQUE (FRAUDE MÉTIER VALIDÉE)",
      vulnerableResponse:
        "HTTP/1.1 200 OK\n" +
        "Content-Type: application/json\n\n" +
        "{\n" +
        '  "accepted": true,\n' +
        '  "dossier_id": 42,\n' +
        '  "nouveau_statut": "INSCRIPTION_PAYEE_CERTIFIEE"\n' +
        "}",
      hardenedStatus: "401 Unauthorized — ATTAQUE BLOQUÉE",
      hardenedResponse:
        "HTTP/1.1 401 Unauthorized\n" +
        "WWW-Authenticate: HMAC-SHA256 realm=\"webhooks\"\n" +
        "Content-Type: application/json\n\n" +
        "{\n" +
        '  "status": 401,\n' +
        '  "error": "Signature HMAC-SHA256 invalide ou horodatage hors tolérance (300s)."\n' +
        "}",
      analysis:
        "Un endpoint Webhook est joignable depuis Internet. Sans validation de la fenêtre temporelle ni vérification " +
        "HMAC-SHA256 à temps constant sur les octets bruts du corps HTTP, n'importe quel tiers peut simuler un paiement.",
      defenseLine: {
        flask:
          'expected = "sha256=" + hmac.new(WEBHOOK_SECRET, ts.encode() + b"." + request.get_data(), hashlib.sha256).hexdigest()\n' +
          "if abs(time.time() - int(ts)) > 300 or not hmac.compare_digest(sig, expected):\n" +
          '    abort(401, description="Signature Webhook invalide ou rejeu détecté.")',
        fastapi:
          'raw = await request.body()\n' +
          'expected = "sha256=" + hmac.new(WEBHOOK_SECRET, f"{ts}.".encode() + raw, hashlib.sha256).hexdigest()\n' +
          "if abs(time.time() - ts) > 300 or not hmac.compare_digest(sig, expected):\n" +
          '    raise HTTPException(status_code=401, detail="Signature HMAC invalide.")',
        tornado:
          'expected = "sha256=" + hmac.new(WEBHOOK_SECRET, f"{ts}.".encode() + self.request.body, hashlib.sha256).hexdigest()\n' +
          "if abs(time.time() - ts) > 300 or not hmac.compare_digest(sig, expected):\n" +
          '    raise tornado.web.HTTPError(401, reason="Signature Webhook rejetée")'
      }
    },
    bruteforce: {
      id: "bruteforce",
      label: "4. Rafale Brute-Force sans Rate-Limiting",
      owaspRef: "OWASP API2:2023 & API4:2023 — Credential Stuffing & Quotas",
      defaultTrace: "POST /api/v1/auth/login (Rafale #84 en 3 secondes depuis 198.51.100.77)",
      httpRequest:
        "POST /api/v1/auth/login HTTP/1.1\n" +
        "Host: api.isgp.dz\n" +
        "X-Forwarded-For: 198.51.100.77\n" +
        "Content-Type: application/json\n\n" +
        '{\n  "email": "direction@isgp.dz",\n  "mot_de_passe": "EssaiDictionnaire_#0084"\n}',
      vulnerableStatus: "200 OK — FUITE CRITIQUE (COMPTE COMPROMIS AU 84e ESSAI)",
      vulnerableResponse:
        "HTTP/1.1 200 OK\n" +
        "Content-Type: application/json\n\n" +
        "{\n" +
        '  "access_token": "eyJhbGciOiJIUzI1NiJ9.admin_direction_compromis",\n' +
        '  "tentatives_precedentes_ignorees": 83\n' +
        "}",
      hardenedStatus: "429 Too Many Requests — ATTAQUE BLOQUÉE",
      hardenedResponse:
        "HTTP/1.1 429 Too Many Requests\n" +
        "Retry-After: 60\n" +
        "X-RateLimit-Limit: 5\n" +
        "X-RateLimit-Remaining: 0\n" +
        "Content-Type: application/json\n\n" +
        "{\n" +
        '  "status": 429,\n' +
        '  "error": "Quota d\'authentification dépassé (max 5 essais / minute). Réessayez dans 60s."\n' +
        "}",
      analysis:
        "Sur un endpoint critique d'authentification ou de réinitialisation OTP, un quota strict (ex. 5 tentatives/minute par IP " +
        "et par identifiant cible) accompagné de l'en-tête standard Retry-After neutralise le credential stuffing.",
      defenseLine: {
        flask:
          "if not token_bucket_allow(key=f\"login:{client_ip}:{email}\", rate=5, per_seconds=60):\n" +
          '    resp = jsonify({"error": "Trop de tentatives d\'authentification"})\n' +
          '    resp.headers["Retry-After"] = "60"\n' +
          "    return resp, 429",
        fastapi:
          "if not token_bucket_allow(key=f\"login:{request.client.host}:{payload.email}\", rate=5, per_seconds=60):\n" +
          "    raise HTTPException(\n" +
          '        status_code=429, detail="Quota dépassé", headers={"Retry-After": "60"}\n' +
          "    )",
        tornado:
          "if not token_bucket_allow(key=f\"login:{self.request.remote_ip}:{email}\", rate=5, per_seconds=60):\n" +
          '    self.set_header("Retry-After", "60")\n' +
          "    self.set_status(429)\n" +
          '    return self.finish({"error": "Trop de tentatives. Réessayez dans 60s."})'
      }
    }
  };

  // ==========================================================================
  // 5. CHECKLIST D'HOMOLOGATION PRE-PRODUCTION (24 CONTROLES EN 4 DOMAINES)
  // ==========================================================================
  var CHECKLIST_DOMAINS = [
    {
      domain: "Identité & Secrets",
      items: [
        { id: "sec-c01", text: "Aucun secret, jeton ou mot de passe en dur dans le dépôt Git (chargement strict via os.environ / gestionnaire de secrets)." },
        { id: "sec-c02", text: "Mots de passe hachés exclusivement via Argon2id, scrypt ou PBKDF2-HMAC-SHA256 (>= 600 000 itérations) avec sel aléatoire de 16 octets." },
        { id: "sec-c03", text: "Jetons JWT signés avec clé >= 256 bits, algorithme explicite verrouillé (algorithms=['HS256'/'RS256']) et durée de vie courte (exp <= 15 min)." },
        { id: "sec-c04", text: "Contrôle d'appartenance systématique sur chaque ressource unitaire (WHERE id = ? AND owner_id = ?) contre les attaques BOLA / IDOR." },
        { id: "sec-c05", text: "Séparation stricte entre authentification (401 + WWW-Authenticate) et autorisation de rôle fonctionnel RBAC (403 Forbidden)." },
        { id: "sec-c06", text: "Comparaison à temps constant via hmac.compare_digest() pour toutes les clés API, jetons CSRF et signatures HMAC." }
      ]
    },
    {
      domain: "Validation & Données",
      items: [
        { id: "sec-c07", text: "Validation stricte des types, longueurs et bornes numériques sur 100 % des paramètres de chemin, query string et corps JSON (HTTP 422)." },
        { id: "sec-c08", text: "Rejet explicite des propriétés JSON non déclarées (extra='forbid' / liste blanche) pour bloquer toute attaque Mass Assignment." },
        { id: "sec-c09", text: "Requêtes SQL intégralement paramétrées (? ou $1) sans aucune concaténation ni f-string contenant des entrées utilisateur." },
        { id: "sec-c10", text: "Modèles de sortie dédiés (DTO de réponse) excluant systématiquement password_hash, sels, secrets MFA et notes internes." },
        { id: "sec-c11", text: "Vérification de l'en-tête Content-Type: application/json (rejet 415 Unsupported Media Type sur types inattendus)." },
        { id: "sec-c12", text: "Validation cryptographique HMAC-SHA256 et fenêtre anti-rejeu (<= 300s) sur tous les Webhooks entrants." }
      ]
    },
    {
      domain: "Réseau, CORS & Quotas",
      items: [
        { id: "sec-c13", text: "Terminaison TLS 1.3 obligatoire en frontal (Nginx / Reverse Proxy) avec redirection HTTPS et en-tête Strict-Transport-Security." },
        { id: "sec-c14", text: "Politique CORS restreinte à une liste blanche explicite d'origines homologuées (interdiction absolue de '*' avec credentials)." },
        { id: "sec-c15", text: "En-têtes de blindage systématiques : X-Content-Type-Options: nosniff, Content-Security-Policy: default-src 'none' et Cache-Control: no-store." },
        { id: "sec-c16", text: "Rate-Limiting actif (429 + Retry-After) différencié sur les routes critiques (/login, /reset-password, /export)." },
        { id: "sec-c17", text: "Plafond strict sur la taille du corps HTTP (MAX_CONTENT_LENGTH / max_body_size -> 413) et plafond de pagination (limit <= 100)." },
        { id: "sec-c18", text: "Protection Anti-SSRF sur tout appel HTTP sortant : schéma HTTPS forcé, liste blanche d'hôtes et blocage des IP privées / 169.254.169.254." }
      ]
    },
    {
      domain: "Production & Audit",
      items: [
        { id: "sec-c19", text: "Mode debug rigoureusement désactivé en production (debug=False) et gestionnaire d'erreur 500 opaque sans stacktrace exposée." },
        { id: "sec-c20", text: "Processus applicatifs (Gunicorn / Uvicorn / Tornado) exécutés sous un compte système non-privilégié (non-root) lié à 127.0.0.1." },
        { id: "sec-c21", text: "Décommissionnement propre des anciennes versions d'API (/api/v1 fantômes -> 410 Gone + Sunset) et suppression des routes de test." },
        { id: "sec-c22", text: "Journalisation d'audit structurée JSON incluant horodatage UTC, X-Request-ID, identifiant sujet, route et code HTTP." },
        { id: "sec-c23", text: "Expurgation automatique des secrets dans les journaux (masquage de Authorization, Cookie, X-API-Key et mots de passe)." },
        { id: "sec-c24", text: "Audit automatisé des dépendances Python (pip-audit / CVE) et tests d'intrusion automatisés BOLA / Mass Assignment dans la CI." }
      ]
    }
  ];

  function loadCheckedSet() {
    try {
      var raw = localStorage.getItem(CHECKLIST_STORAGE_KEY);
      if (!raw) return new Set();
      var parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return new Set(parsed);
    } catch (e) {}
    return new Set();
  }

  function saveCheckedSet(checkedSet) {
    try {
      localStorage.setItem(CHECKLIST_STORAGE_KEY, JSON.stringify(Array.from(checkedSet)));
    } catch (e) {}
  }

  // ==========================================================================
  // RENDU SECTION 0 (HERO) & SECTION 1 (DEFENSE EN PROFONDEUR + MERMAID)
  // ==========================================================================
  function renderHeroAndSection1(fwMeta) {
    var shieldCardsHtml = SEVEN_SHIELDS.map(function (s) {
      return (
        '<div class="nt-card">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">' +
        '<span class="nt-badge">' + escapeHtml(s.step) + "</span>" +
        '<span class="nt-badge ' + s.badgeClass + '">' + escapeHtml(s.code) + "</span>" +
        "</div>" +
        "<h4>" + escapeHtml(s.title) + "</h4>" +
        "<p>" + escapeHtml(s.summary) + "</p>" +
        "</div>"
      );
    }).join("");

    var fwButtons = ["flask", "fastapi", "tornado"].map(function (id) {
      var label = id === "flask" ? "Flask (WSGI)" : id === "fastapi" ? "FastAPI (ASGI)" : "Tornado (Async)";
      var activeCls = fwMeta.id === id ? " active" : "";
      return (
        '<button type="button" class="nt-pill-btn' + activeCls + '" data-sec-fw="' + id + '">' +
        escapeHtml(label) +
        "</button>"
      );
    }).join("");

    return (
      '<div class="nt-hero">' +
      '<div class="nt-hero-top">' +
      "<div>" +
      "<h2>Ingénierie de la Sécurité des APIs &amp; Référentiel OWASP Top 10 (Édition 2023)</h2>" +
      "<p>Architecture de défense en profondeur, parades cryptographiques de production, protection contre les failles d'autorisation (BOLA, BFLA, Mass Assignment, SSRF) et laboratoire d'intrusion adapté dynamiquement au moteur actif : <strong>" +
      escapeHtml(fwMeta.runtime) +
      "</strong>.</p>" +
      "</div>" +
      '<span class="nt-badge nt-badge-info">Profil Actif : ' + escapeHtml(fwMeta.name) + "</span>" +
      "</div>" +
      '<div class="nt-filter-bar" style="margin-bottom:0;">' +
      '<strong style="font-size:12.4px;color:var(--text);margin-right:6px;">Cible des contre-mesures Python :</strong>' +
      fwButtons +
      '<span style="font-size:12px;color:var(--text-muted);margin-left:auto;">' + escapeHtml(fwMeta.paradigm) + "</span>" +
      "</div>" +
      '<div class="nt-kpi-strip">' +
      '<div class="nt-kpi-card"><span class="nt-kpi-label">Couches Défensives</span><strong class="nt-kpi-value">7 Boucliers</strong><span class="nt-kpi-sub">Du proxy TLS 1.3 jusqu\'à l\'audit SIEM</span></div>' +
      '<div class="nt-kpi-card"><span class="nt-kpi-label">Référentiel Mondial</span><strong class="nt-kpi-value">OWASP 2023</strong><span class="nt-kpi-sub">API1:2023 à API10:2023 couverts à 100 %</span></div>' +
      '<div class="nt-kpi-card"><span class="nt-kpi-label">Règles Cryptographiques</span><strong class="nt-kpi-value">PBKDF2 / HMAC</strong><span class="nt-kpi-sub">Zéro secret en dur &amp; temps constant</span></div>' +
      '<div class="nt-kpi-card"><span class="nt-kpi-label">Homologation Prod</span><strong class="nt-kpi-value">24 Contrôles</strong><span class="nt-kpi-sub">Checklist persistante pré-déploiement</span></div>' +
      "</div>" +
      "</div>" +

      '<section class="nt-section-block">' +
      '<h3 class="nt-section-title"><span>1. Architecture Défense en Profondeur : Les 7 Boucliers d\'une API Sécurisée</span><span class="nt-badge nt-badge-info">Zero-Trust Pipeline</span></h3>' +
      '<p class="nt-section-lead">Une API robuste ne repose jamais sur un contrôle unique : chaque requête entrante franchit sept barrières indépendantes. Si un jeton valide est compromis, le contrôle d\'appartenance Anti-BOLA (403), le filtrage de schéma (422), le paramétrage SQL (?) et les quotas (429) contiennent l\'impact.</p>' +
      '<div class="mermaid-container">' +
      '<pre class="mermaid">' +
      "flowchart LR\n" +
      '  CLI["Requête Client HTTPS"] --> B1["1. TLS 1.3 et Reverse Proxy Nginx"]\n' +
      '  B1 --> B2["2. Quotas Rate-Limit 429 et Body 413"]\n' +
      '  B2 --> B3["3. Authentification 401 WWW-Authenticate"]\n' +
      '  B3 --> B4["4. Autorisation RBAC et Anti-BOLA 403"]\n' +
      '  B4 --> B5["5. Validation Stricte et Anti-Mass-Assignment 422"]\n' +
      '  B5 --> B6["6. SQL Paramétré ? et Filtrage DTO Sortie"]\n' +
      '  B6 --> B7["7. Journalisation Audit UTC et Alerte"]\n' +
      '  B7 --> DB["Persistance SQLite et PostgreSQL"]' +
      "</pre>" +
      "</div>" +
      '<div class="nt-grid-3" style="margin-top:16px;">' + shieldCardsHtml + "</div>" +
      "</section>"
    );
  }

  // ==========================================================================
  // RENDU SECTION 2 (OWASP TOP 10 2023) & SECTION 3 (AUTHN, CRYPTO & HEADERS)
  // ==========================================================================
  function renderSection2Owasp(fwMeta) {
    var filters = [
      { key: "all", label: "Tous les 10 Risques (API1 - API10)" },
      { key: "access", label: "Autorisation & Propriétés (API1, API3, API5)" },
      { key: "auth", label: "Authentification & Flux Métier (API2, API6)" },
      { key: "infra", label: "Quotas, Config & Inventaire (API4, API8, API9)" },
      { key: "ssrf", label: "SSRF & APIs Tierces / Webhooks (API7, API10)" }
    ];

    var filterHtml = filters.map(function (f) {
      var cls = SEC_STATE.owaspFilter === f.key ? "nt-pill-btn active" : "nt-pill-btn";
      return (
        '<button type="button" class="' + cls + '" data-owasp-filter="' + f.key + '">' +
        escapeHtml(f.label) +
        "</button>"
      );
    }).join("");

    var visibleItems = OWASP_TOP_10.filter(function (item) {
      return SEC_STATE.owaspFilter === "all" || item.family === SEC_STATE.owaspFilter;
    });

    var cardsHtml = visibleItems.map(function (item) {
      var sevClass = item.severity === "Critique" ? "nt-badge-danger" : "nt-badge-warn";
      var fixCode = item.fixes[fwMeta.id] || item.fixes.flask;
      return (
        '<div class="nt-pair-wrapper" data-owasp-id="' + escapeHtml(item.id) + '">' +
        '<div class="nt-pair-header">' +
        "<h3>" + escapeHtml(item.id + " — " + item.title) + "</h3>" +
        '<div style="display:flex;gap:8px;flex-wrap:wrap;">' +
        '<span class="nt-badge ' + sevClass + '">Sévérité : ' + escapeHtml(item.severity) + "</span>" +
        '<span class="nt-badge nt-badge-info">Défense : ' + escapeHtml(item.httpDefense) + "</span>" +
        "</div>" +
        "</div>" +
        '<p class="nt-pair-rationale"><strong>Scénario d\'attaque concret :</strong> ' + escapeHtml(item.scenario) + "</p>" +
        '<div class="nt-compare-pair" style="margin-bottom:0;">' +
        '<div class="nt-card-bad">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">' +
        "<h4>Implémentation Vulnérable (À Proscrire)</h4>" +
        '<span class="nt-badge nt-badge-danger">Faille Exploitable</span>' +
        "</div>" +
        renderCodeBlock("Anti-Pattern Python", item.id, item.vulnerable) +
        "</div>" +
        '<div class="nt-card-good">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">' +
        "<h4>Parade Blindée en Production (" + escapeHtml(fwMeta.name) + ")</h4>" +
        '<span class="nt-badge nt-badge-success">Conforme OWASP 2023</span>' +
        "</div>" +
        renderCodeBlock("Contre-Mesure " + fwMeta.name, item.httpDefense, fixCode) +
        "</div>" +
        "</div>" +
        "</div>"
      );
    }).join("");

    return (
      '<section class="nt-section-block">' +
      '<h3 class="nt-section-title"><span>2. Référentiel Complet OWASP API Security Top 10 (Édition 2023) &amp; Parades ' +
      escapeHtml(fwMeta.name) +
      '</span><span class="nt-badge nt-badge-danger">' + visibleItems.length + " / 10 affichés</span></h3>" +
      '<p class="nt-section-lead">Chaque risque majeur de l\'édition 2023 de l\'OWASP API Security Top 10 est illustré par son vecteur d\'intrusion réel, le code vulnérable typique et son implémentation défensive exacte dans <strong>' +
      escapeHtml(fwMeta.runtime) +
      "</strong>.</p>" +
      '<div class="nt-filter-bar">' + filterHtml + "</div>" +
      cardsHtml +
      "</section>"
    );
  }

  function renderSection3AuthAndCrypto(fwMeta) {
    var authRowsHtml = AUTH_MATRIX.map(function (row) {
      return (
        "<tr>" +
        "<td><strong>" + escapeHtml(row.mechanism) + "</strong></td>" +
        "<td>" + escapeHtml(row.idealUse) + "</td>" +
        "<td>" + escapeHtml(row.risks) + "</td>" +
        "<td>" + escapeHtml(row.storage) + "</td>" +
        "<td>" + escapeHtml(row.revocation) + "</td>" +
        "</tr>"
      );
    }).join("");

    var cryptoCardsHtml = CRYPTO_GOLDEN_RULES.map(function (rule) {
      var snippet = rule.snippets[fwMeta.id] || rule.snippets.flask;
      return (
        '<div class="nt-card">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">' +
        "<h4>" + escapeHtml(rule.title) + "</h4>" +
        '<span class="nt-badge nt-badge-success">' + escapeHtml(rule.badge) + "</span>" +
        "</div>" +
        "<p>" + escapeHtml(rule.rationale) + "</p>" +
        renderCodeBlock("Règle Cryptographique — " + fwMeta.name, "Stdlib / Production", snippet) +
        "</div>"
      );
    }).join("");

    var headerRowsHtml = SECURITY_HEADERS_ROWS.map(function (h) {
      return (
        "<tr>" +
        "<td><code>" + escapeHtml(h.header) + "</code></td>" +
        "<td><code>" + escapeHtml(h.value) + "</code></td>" +
        "<td>" + escapeHtml(h.role) + "</td>" +
        "</tr>"
      );
    }).join("");

    var mwCode = PERIMETER_MIDDLEWARE[fwMeta.id] || PERIMETER_MIDDLEWARE.flask;

    return (
      '<section class="nt-section-block">' +
      '<h3 class="nt-section-title"><span>3. Comparatif Architectural des Mécanismes d\'Authentification &amp; Cryptographie Pratique</span><span class="nt-badge nt-badge-info">AuthN / AuthZ / Crypto</span></h3>' +
      '<p class="nt-section-lead">Le choix d\'un protocole d\'authentification dépend de la topologie du client (navigateur même origine, application mobile, partenaire serveur-à-serveur) et de l\'exigence de révocation immédiate.</p>' +
      '<div class="nt-table-wrap">' +
      '<table class="nt-table">' +
      "<thead><tr><th>Mécanisme</th><th>Cas d'Usage Idéal</th><th>Risques &amp; Vecteurs</th><th>Stockage Client Recommandé</th><th>Révocation</th></tr></thead>" +
      "<tbody>" + authRowsHtml + "</tbody>" +
      "</table>" +
      "</div>" +

      '<h4 style="margin:22px 0 10px 0;font-size:15.5px;color:var(--text);">Les 4 Règles d\'Or Cryptographiques (' + escapeHtml(fwMeta.name) + ")</h4>" +
      '<div class="nt-grid-2">' + cryptoCardsHtml + "</div>" +

      '<h4 style="margin:22px 0 10px 0;font-size:15.5px;color:var(--text);">En-têtes HTTP de Blindage Périmétrique &amp; Politique CORS Explicite</h4>' +
      '<div class="nt-grid-2">' +
      '<div class="nt-table-wrap" style="margin-top:0;">' +
      '<table class="nt-table">' +
      "<thead><tr><th>En-tête HTTP</th><th>Directive Recommandée</th><th>Protection Assurée</th></tr></thead>" +
      "<tbody>" + headerRowsHtml + "</tbody>" +
      "</table>" +
      "</div>" +
      '<div class="nt-card">' +
      "<h4>Middleware Périmétrique Complet (" + escapeHtml(fwMeta.name) + ")</h4>" +
      "<p>Application centralisée des en-têtes HSTS, CSP stricte API, anti-MIME-sniffing, désactivation du cache sensible et liste blanche CORS stricte.</p>" +
      renderCodeBlock("Middleware Sécurité & CORS — " + fwMeta.name, "Périmètre HTTP", mwCode) +
      "</div>" +
      "</div>" +
      "</section>"
    );
  }

  // ==========================================================================
  // RENDU SECTION 4 (SIMULATEUR D'ATTAQUE) & SECTION 5 (CHECKLIST 24 CONTROLES)
  // ==========================================================================
  function renderSimulatorResultHtml(fwMeta) {
    var sc = SIM_SCENARIOS[SEC_STATE.simScenario] || SIM_SCENARIOS.bola;
    var isHardened = SEC_STATE.simMode === "hardened";
    var statusLabel = isHardened ? sc.hardenedStatus : sc.vulnerableStatus;
    var statusBadgeCls = isHardened ? "nt-badge-success" : "nt-badge-danger";
    var responseCardCls = isHardened ? "nt-card-good" : "nt-card-bad";
    var rawResp = isHardened ? sc.hardenedResponse : sc.vulnerableResponse;
    var defenseCode = sc.defenseLine[fwMeta.id] || sc.defenseLine.flask;

    return (
      '<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:12px;">' +
      "<div><strong>Verdict de l'exécution :</strong> <span>" + escapeHtml(sc.owaspRef) + "</span></div>" +
      '<span class="nt-badge ' + statusBadgeCls + '">' + escapeHtml(statusLabel) + "</span>" +
      "</div>" +
      '<div class="nt-compare-pair">' +
      '<div class="nt-card">' +
      "<h4>Requête HTTP d'Intrusion Émise</h4>" +
      renderCodeBlock("Flux Attaquant -> API", "HTTP/1.1", sc.httpRequest) +
      "</div>" +
      '<div class="' + responseCardCls + '">' +
      "<h4>Réponse du " + (isHardened ? "Serveur Sécurisé" : "Serveur Vulnérable") + "</h4>" +
      renderCodeBlock("Réponse HTTP Interceptée", statusLabel, rawResp) +
      "</div>" +
      "</div>" +
      '<div class="nt-card">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">' +
      "<h4>Diagnostic d'Impact &amp; Ligne de Défense Exacte (" + escapeHtml(fwMeta.name) + ")</h4>" +
      '<span class="nt-badge nt-badge-info">Moteur : ' + escapeHtml(fwMeta.runtime) + "</span>" +
      "</div>" +
      "<p>" + escapeHtml(sc.analysis) + "</p>" +
      renderCodeBlock("Barrière Défensive Exacte — " + fwMeta.name, sc.id.toUpperCase(), defenseCode) +
      "</div>"
    );
  }

  function renderSection4Simulator(fwMeta) {
    var scenarioOptions = Object.keys(SIM_SCENARIOS).map(function (key) {
      var item = SIM_SCENARIOS[key];
      var sel = SEC_STATE.simScenario === key ? " selected" : "";
      return '<option value="' + escapeHtml(key) + '"' + sel + ">" + escapeHtml(item.label) + "</option>";
    }).join("");

    var currentSc = SIM_SCENARIOS[SEC_STATE.simScenario] || SIM_SCENARIOS.bola;
    var traceVal = SEC_STATE.simTargetTrace || currentSc.defaultTrace;

    return (
      '<section class="nt-section-block">' +
      '<h3 class="nt-section-title"><span>4. Simulateur Interactif d\'Attaque &amp; Blindage (BOLA, Mass Assignment, Webhook &amp; Brute-Force)</span><span class="nt-badge nt-badge-warn">Laboratoire Red/Blue Team</span></h3>' +
      '<p class="nt-section-lead">Sélectionnez un vecteur d\'intrusion et comparez le comportement d\'un endpoint non protégé face au serveur blindé dans <strong>' +
      escapeHtml(fwMeta.name) +
      "</strong>.</p>" +
      '<div class="nt-sim-box">' +
      '<div class="nt-form-row">' +
      '<div class="nt-field-group">' +
      '<label for="sec-sim-scenario">Scénario d\'attaque</label>' +
      '<select id="sec-sim-scenario" class="nt-select">' + scenarioOptions + "</select>" +
      "</div>" +
      '<div class="nt-field-group">' +
      '<label for="sec-sim-mode">Posture du serveur cible</label>' +
      '<select id="sec-sim-mode" class="nt-select">' +
      '<option value="vulnerable"' + (SEC_STATE.simMode === "vulnerable" ? " selected" : "") + ">Serveur Vulnérable</option>" +
      '<option value="hardened"' + (SEC_STATE.simMode === "hardened" ? " selected" : "") + ">Serveur Sécurisé</option>" +
      "</select>" +
      "</div>" +
      '<div class="nt-field-group">' +
      '<label for="sec-sim-trace">Vecteur HTTP inspecté</label>' +
      '<input id="sec-sim-trace" type="text" class="nt-input" readonly value="' + escapeHtml(traceVal) + '" />' +
      "</div>" +
      "</div>" +
      '<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">' +
      '<button type="button" id="sec-sim-run-btn" class="btn-primary">Exécuter le Test d\'Intrusion</button>' +
      '<button type="button" id="sec-sim-toggle-mode-btn" class="btn-secondary">Basculer Vulnérable / Sécurisé</button>' +
      "</div>" +
      '<div id="sec-sim-result-panel" class="nt-result-panel">' +
      renderSimulatorResultHtml(fwMeta) +
      "</div>" +
      "</div>" +
      "</section>"
    );
  }

  function renderSection5Checklist() {
    var checkedSet = loadCheckedSet();
    var totalCount = 24;
    var checkedCount = 0;

    var domainsHtml = CHECKLIST_DOMAINS.map(function (group) {
      var itemsHtml = group.items.map(function (ctrl) {
        var isChecked = checkedSet.has(ctrl.id);
        if (isChecked) checkedCount += 1;
        return (
          '<label class="nt-check-item' + (isChecked ? " checked" : "") + '" data-check-id="' + escapeHtml(ctrl.id) + '">' +
          '<input type="checkbox" data-sec-checkbox="' + escapeHtml(ctrl.id) + '"' + (isChecked ? " checked" : "") + " />" +
          "<span>" + escapeHtml(ctrl.text) + "</span>" +
          "</label>"
        );
      }).join("");

      return (
        '<div style="margin-top:16px;">' +
        '<h4 style="margin:0 0 8px 0;font-size:14.6px;color:var(--text);">Domaine : ' + escapeHtml(group.domain) + "</h4>" +
        '<div class="nt-checklist">' + itemsHtml + "</div>" +
        "</div>"
      );
    }).join("");

    var pct = Math.round((checkedCount / totalCount) * 100);
    var readinessBadge = checkedCount === totalCount
      ? '<span class="nt-badge nt-badge-success">Homologué pour la Production (100 %)</span>'
      : '<span class="nt-badge nt-badge-warn">En cours d\'homologation (' + pct + " %)</span>";

    return (
      '<section class="nt-section-block">' +
      '<h3 class="nt-section-title"><span>5. Checklist Interactive d\'Homologation Sécurité Pré-Production (24 Contrôles)</span>' + readinessBadge + "</h3>" +
      '<p class="nt-section-lead">Validez les 24 exigences de sécurité réparties en 4 domaines critiques avant toute exposition publique. Votre avancement est sauvegardé automatiquement dans le navigateur (<code>' +
      escapeHtml(CHECKLIST_STORAGE_KEY) +
      "</code>).</p>" +
      '<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">' +
      '<strong id="sec-checklist-counter" style="font-size:14px;color:var(--text);">' + checkedCount + " / " + totalCount + " contrôles validés</strong>" +
      '<button type="button" id="sec-checklist-reset-btn" class="btn-secondary">Réinitialiser la checklist</button>' +
      "</div>" +
      '<div class="nt-progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="24" aria-valuenow="' + checkedCount + '">' +
      '<div id="sec-checklist-progress-fill" class="nt-progress-fill" style="width:' + pct + '%;"></div>' +
      "</div>" +
      domainsHtml +
      "</section>"
    );
  }

  function bindSecurityTabEvents(rootEl) {
    if (rootEl.getAttribute("data-sec-bound") === "1") return;
    rootEl.setAttribute("data-sec-bound", "1");

    rootEl.addEventListener("click", function (ev) {
      var fwBtn = ev.target.closest("[data-sec-fw]");
      if (fwBtn) {
        SEC_STATE.frameworkOverride = fwBtn.getAttribute("data-sec-fw");
        window.loadSecurityTab();
        return;
      }

      var filterBtn = ev.target.closest("[data-owasp-filter]");
      if (filterBtn) {
        SEC_STATE.owaspFilter = filterBtn.getAttribute("data-owasp-filter") || "all";
        var owaspWrap = rootEl.querySelector("#sec-owasp-wrapper");
        if (owaspWrap) {
          owaspWrap.innerHTML = renderSection2Owasp(getFrameworkMeta(getActiveSecFramework()));
        } else {
          window.loadSecurityTab();
        }
        return;
      }

      if (ev.target.closest("#sec-sim-run-btn")) {
        var scSel = rootEl.querySelector("#sec-sim-scenario");
        var modeSel = rootEl.querySelector("#sec-sim-mode");
        if (scSel) SEC_STATE.simScenario = scSel.value;
        if (modeSel) SEC_STATE.simMode = modeSel.value;
        var scObj = SIM_SCENARIOS[SEC_STATE.simScenario] || SIM_SCENARIOS.bola;
        SEC_STATE.simTargetTrace = scObj.defaultTrace;
        var traceInput = rootEl.querySelector("#sec-sim-trace");
        if (traceInput) traceInput.value = scObj.defaultTrace;
        var panel = rootEl.querySelector("#sec-sim-result-panel");
        if (panel) panel.innerHTML = renderSimulatorResultHtml(getFrameworkMeta(getActiveSecFramework()));
        return;
      }

      if (ev.target.closest("#sec-sim-toggle-mode-btn")) {
        SEC_STATE.simMode = SEC_STATE.simMode === "hardened" ? "vulnerable" : "hardened";
        var modeSelectEl = rootEl.querySelector("#sec-sim-mode");
        if (modeSelectEl) modeSelectEl.value = SEC_STATE.simMode;
        var simPanel = rootEl.querySelector("#sec-sim-result-panel");
        if (simPanel) {
          simPanel.innerHTML = renderSimulatorResultHtml(getFrameworkMeta(getActiveSecFramework()));
        } else {
          window.loadSecurityTab();
        }
        return;
      }

      if (ev.target.closest("#sec-checklist-reset-btn")) {
        saveCheckedSet(new Set());
        var chkWrap = rootEl.querySelector("#sec-checklist-wrapper");
        if (chkWrap) {
          chkWrap.innerHTML = renderSection5Checklist();
        } else {
          window.loadSecurityTab();
        }
      }
    });

    rootEl.addEventListener("change", function (ev) {
      if (ev.target.id === "sec-sim-scenario" || ev.target.id === "sec-sim-mode") {
        var scSel = rootEl.querySelector("#sec-sim-scenario");
        var modeSel = rootEl.querySelector("#sec-sim-mode");
        if (scSel) SEC_STATE.simScenario = scSel.value;
        if (modeSel) SEC_STATE.simMode = modeSel.value;
        var scObj = SIM_SCENARIOS[SEC_STATE.simScenario] || SIM_SCENARIOS.bola;
        SEC_STATE.simTargetTrace = scObj.defaultTrace;
        var traceInput = rootEl.querySelector("#sec-sim-trace");
        if (traceInput) traceInput.value = scObj.defaultTrace;
        var panel = rootEl.querySelector("#sec-sim-result-panel");
        if (panel) panel.innerHTML = renderSimulatorResultHtml(getFrameworkMeta(getActiveSecFramework()));
        return;
      }

      var chk = ev.target.closest("[data-sec-checkbox]");
      if (chk) {
        var id = chk.getAttribute("data-sec-checkbox");
        var set = loadCheckedSet();
        if (chk.checked) set.add(id);
        else set.delete(id);
        saveCheckedSet(set);
        var chkWrap2 = rootEl.querySelector("#sec-checklist-wrapper");
        if (chkWrap2) {
          chkWrap2.innerHTML = renderSection5Checklist();
        } else {
          window.loadSecurityTab();
        }
      }
    });
  }

  window.loadSecurityTab = function () {
    var rootEl = document.getElementById("security-tab-root");
    if (!rootEl) return;

    var fwMeta = getFrameworkMeta(getActiveSecFramework());
    rootEl.innerHTML =
      renderHeroAndSection1(fwMeta) +
      '<div id="sec-owasp-wrapper">' + renderSection2Owasp(fwMeta) + "</div>" +
      renderSection3AuthAndCrypto(fwMeta) +
      renderSection4Simulator(fwMeta) +
      '<div id="sec-checklist-wrapper">' + renderSection5Checklist() + "</div>";

    bindSecurityTabEvents(rootEl);

    if (typeof renderMermaidDiagrams === "function") {
      renderMermaidDiagrams(rootEl);
    }
  };
})();
