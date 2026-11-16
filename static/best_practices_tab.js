// ============================================================================
// ISGP API Engineering Trilogy — Onglet Synthese Generale & Bonnes Pratiques
// Couvre Flask (WSGI), FastAPI (ASGI) et Tornado (IOLoop Async Non-Bloquant)
// ============================================================================

(function () {
  "use strict";

  const BP_STATE = {
    category: "Tous",
    search: "",
    fwOverride: null,
    presetKey: "bad_rpc_user",
    linterMethod: "POST",
    linterUri: "/API/createUser?admin_token=sec_9981",
    linterStatus: "200",
    linterSample: JSON.stringify(
      {
        success: false,
        error: "Email déjà utilisé",
        password_hash: "$2b$12$K8H1x...",
        date_creation: "14/11/26",
        prix_formation: 149.99
      },
      null,
      2
    )
  };

  const BP_CATEGORIES = [
    "Tous",
    "Nommage & URI",
    "Verbes & Statuts",
    "Payloads & Pagination",
    "Idempotence & Concurrence",
    "Performance & Versioning"
  ];

  function detectFramework() {
    if (BP_STATE.fwOverride) return BP_STATE.fwOverride;
    const raw = (
      window.ACTIVE_FRAMEWORK ||
      (typeof STATE !== "undefined" ? STATE?.framework : "") ||
      "flask"
    )
      .toString()
      .toLowerCase();
    if (raw.includes("fast")) return "fastapi";
    if (raw.includes("tornado")) return "tornado";
    return "flask";
  }

  function fwLabel(fw) {
    if (fw === "fastapi") return "FastAPI (ASGI / Pydantic)";
    if (fw === "tornado") return "Tornado (Async IOLoop)";
    return "Flask (WSGI / Blueprint)";
  }

  function escHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  const HTTP_MATRIX = [
    {
      verb: "GET",
      safe: "Oui",
      idempotent: "Oui",
      body: "Interdit / Ignoré",
      success: "200 OK, 304 Not Modified",
      errors: "400, 401, 403, 404, 429, 500, 503",
      idiom: {
        flask: "@bp.get('/formations/<int:id>') -> jsonify(dto), 200",
        fastapi: "@router.get('/formations/{id}', response_model=FormationOut)",
        tornado: "async def get(self, id: str): self.write({'data': dto})"
      }
    },
    {
      verb: "POST",
      safe: "Non",
      idempotent: "Non (sauf Idempotency-Key)",
      body: "Requis (DTO création / commande)",
      success: "201 Created + Location, 202 Accepted + Job URL",
      errors: "400, 401, 403, 409, 415, 422, 429, 500, 502",
      idiom: {
        flask: "@bp.post('/formations') -> jsonify(dto), 201, {'Location': url}",
        fastapi: "@router.post('/formations', status_code=201) + response.headers['Location']",
        tornado: "self.set_status(201); self.set_header('Location', url); self.write(dto)"
      }
    },
    {
      verb: "PUT",
      safe: "Non",
      idempotent: "Oui",
      body: "Requis (Représentation intégrale)",
      success: "200 OK (avec DTO), 204 No Content",
      errors: "400, 401, 403, 404, 409, 412 (If-Match), 415, 422",
      idiom: {
        flask: "@bp.put('/formations/<int:id>') -> vérification If-Match + remplacement",
        fastapi: "@router.put('/formations/{id}', response_model=FormationOut)",
        tornado: "async def put(self, id: str): vérification ETag + remplacement complet"
      }
    },
    {
      verb: "PATCH",
      safe: "Non",
      idempotent: "Non par défaut (Oui si JSON Merge Patch)",
      body: "Requis (Sous-ensemble explicite de champs)",
      success: "200 OK (avec DTO mis à jour), 204 No Content",
      errors: "400, 401, 403, 404, 409, 412, 415, 422",
      idiom: {
        flask: "@bp.patch('/formations/<int:id>') -> fusion des clés présentes uniquement",
        fastapi: "payload.model_dump(exclude_unset=True) dans @router.patch(...)",
        tornado: "async def patch(self, id: str): mise à jour sélective des colonnes autorisées"
      }
    },
    {
      verb: "DELETE",
      safe: "Non",
      idempotent: "Oui",
      body: "Absent / Déconseillé",
      success: "204 No Content, 202 Accepted (suppression différée)",
      errors: "401, 403, 404, 409 (contrainte FK), 412, 429, 500",
      idiom: {
        flask: "@bp.delete('/formations/<int:id>') -> return '', 204",
        fastapi: "@router.delete('/formations/{id}', status_code=204) -> return Response(status_code=204)",
        tornado: "self.set_status(204); self.finish()"
      }
    },
    {
      verb: "HEAD",
      safe: "Oui",
      idempotent: "Oui",
      body: "Interdit (en-têtes seuls en réponse)",
      success: "200 OK, 304 Not Modified (sans corps)",
      errors: "401, 403, 404, 429, 500, 503",
      idiom: {
        flask: "Géré nativement sur @bp.get(...) ou @bp.route(..., methods=['HEAD'])",
        fastapi: "@router.head('/formations/{id}') -> Response(headers={'ETag': tag})",
        tornado: "async def head(self, id: str): self.set_header('ETag', tag); self.finish()"
      }
    },
    {
      verb: "OPTIONS",
      safe: "Oui",
      idempotent: "Oui",
      body: "Absent",
      success: "204 No Content + Allow / Access-Control-Allow-*",
      errors: "400, 403 (origine CORS refusée), 500",
      idiom: {
        flask: "flask-cors avec origines explicites ou after_request contrôlé",
        fastapi: "CORSMiddleware(allow_origins=['https://portail.isgp.dz'], ...)",
        tornado: "def options(self, *args): self.set_status(204); self.finish()"
      }
    }
  ];

  const STATUS_CATALOG = [
    { code: "200 OK", role: "Lecture, remplacement ou fusion réussie avec représentation dans le corps." },
    { code: "201 Created + Location", role: "Ressource créée avec URI canonique renvoyée dans l'en-tête Location." },
    { code: "202 Accepted + Job URL", role: "Traitement asynchrone enregistré ; suivi d'avancement sur /api/v1/jobs/{id}." },
    { code: "204 No Content", role: "Suppression ou mise à jour exécutée avec succès sans charge utile de retour." },
    { code: "304 Not Modified", role: "Cache client toujours valide selon If-None-Match / ETag ; économie de bande passante." },
    { code: "400 Bad Request", role: "Syntaxe HTTP ou JSON malformée, paramètres de requête illisibles." },
    { code: "401 Unauthorized", role: "Identité absente, jeton expiré ou signature invalide (+ en-tête WWW-Authenticate)." },
    { code: "403 Forbidden", role: "Identité connue mais droits RBAC ou propriété d'objet (anti-BOLA) insuffisants." },
    { code: "404 Not Found", role: "Ressource inexistante ou masquée volontairement pour prévenir l'énumération." },
    { code: "409 Conflict", role: "Conflit d'état métier : doublon d'unicité (email/code) ou transition interdite." },
    { code: "412 Precondition Failed", role: "Échec de concurrence optimiste : la version If-Match ne correspond plus à l'ETag actuel." },
    { code: "415 Unsupported Media Type", role: "En-tête Content-Type absent ou non supporté (ex. text/plain au lieu d'application/json)." },
    { code: "422 Unprocessable Entity", role: "JSON syntaxiquement valide mais violant les contraintes métier ou le schéma DTO." },
    { code: "429 Too Many Requests", role: "Quota dépassé ; accompagner impérativement de l'en-tête Retry-After." },
    { code: "500 / 502 / 503", role: "Défaillance interne contrôlée (500), passerelle amont en échec (502) ou maintenance / base indisponible (503)." }
  ];

  const ENDPOINT_PATTERNS = [
    {
      id: 1,
      category: "Nommage & URI",
      title: "Verbes RPC dans l'URL vs Ressources nominales au pluriel & verbes HTTP",
      rationale: "Une URI identifie un nom de ressource stable (collection ou instance), jamais une procédure. L'intention d'action appartient exclusivement à la méthode HTTP afin de préserver la sémantique des caches, proxies et clients OpenAPI.",
      badEndpoint: "POST /createUser   |   GET /deleteFormation?id=3",
      badCode: "# Anti-pattern RPC : un robot d'indexation ou prefetcher suivant\n# GET /deleteFormation?id=3 déclenche une suppression destructive !\n@app.route('/deleteFormation', methods=['GET'])\ndef delete_formation_rpc():\n    db.execute('DELETE FROM formations WHERE id = ?', (request.args['id'],))\n    return 'Supprimé'",
      goodEndpoint: "POST /api/v1/utilisateurs   |   DELETE /api/v1/formations/3",
      fw: {
        flask: "@api_v1.post('/utilisateurs')\ndef creer_utilisateur():\n    dto = valider_creation_utilisateur(request.get_json(silent=True))\n    user = repo.inserer_utilisateur(dto)\n    return jsonify(user), 201, {'Location': f\"/api/v1/utilisateurs/{user['id']}\"}",
        fastapi: "@router.post('/utilisateurs', response_model=UtilisateurOut, status_code=201)\nasync def creer_utilisateur(payload: UtilisateurIn, response: Response):\n    user = await repo.inserer_utilisateur(payload)\n    response.headers['Location'] = f'/api/v1/utilisateurs/{user.id}'\n    return user",
        tornado: "class FormationsItemHandler(BaseApiHandler):\n    async def delete(self, formation_id: str):\n        supprime = await self.repo.supprimer_formation(int(formation_id))\n        if not supprime:\n            return self.write_problem(404, 'Formation introuvable')\n        self.set_status(204)\n        await self.finish()"
      }
    },
    {
      id: 2,
      category: "Verbes & Statuts",
      title: "200 OK masquant une erreur vs Statuts sémantiques & RFC 7807 Problem Details",
      rationale: "Renvoyer HTTP 200 avec {\"success\": false} aveugle les passerelles API, fausse les métriques SLI/SLO Prometheus et empêche les SDK clients de distinguer succès et échec. Utilisez le code HTTP exact couplé au format normalisé RFC 7807 (application/problem+json).",
      badEndpoint: "HTTP/1.1 200 OK   ->   {\"success\": false, \"error\": \"Solde insuffisant\"}",
      badCode: "# Trompe la supervision : 100 % de codes 200 alors que la base échoue\nreturn jsonify({'success': False, 'error': str(exc)}), 200",
      goodEndpoint: "HTTP/1.1 422 Unprocessable Entity   (Content-Type: application/problem+json)",
      fw: {
        flask: "def problem_response(status: int, title: str, detail: str, instance: str):\n    body = {'type': f'https://api.isgp.dz/erreurs/{status}', 'title': title,\n            'status': status, 'detail': detail, 'instance': instance}\n    return Response(json.dumps(body), status=status, mimetype='application/problem+json')",
        fastapi: "@app.exception_handler(ErreurMetierISGP)\nasync def problem_handler(req: Request, exc: ErreurMetierISGP):\n    return JSONResponse(status_code=exc.status, media_type='application/problem+json',\n        content={'type': exc.uri, 'title': exc.title, 'status': exc.status,\n                 'detail': exc.detail, 'instance': str(req.url.path)})",
        tornado: "def write_problem(self, status: int, title: str, detail: str = ''):\n    self.set_status(status)\n    self.set_header('Content-Type', 'application/problem+json; charset=utf-8')\n    self.finish({'type': f'https://api.isgp.dz/erreurs/{status}', 'title': title,\n                 'status': status, 'detail': detail, 'instance': self.request.path})"
      }
    },
    {
      id: 3,
      category: "Payloads & Pagination",
      title: "Tableaux JSON nus non bornés vs Enveloppe paginée {meta, data, links} & plafond strict",
      rationale: "Un SELECT * sérialisé en liste JSON racine sature la RAM du worker Python (OOM), bloque la boucle d'événements et verrouille l'évolution du contrat. Encapsulez systématiquement les collections avec un plafond serveur (limit <= 100).",
      badEndpoint: "GET /stagiaires   ->   [{...}, {...}, ... 50 000 lignes brutes]",
      badCode: "rows = db.execute('SELECT * FROM stagiaires').fetchall()\nreturn jsonify([dict(r) for r in rows])  # Risque critique de saturation mémoire",
      goodEndpoint: "GET /api/v1/stagiaires?limit=25&offset=0   (plafond forcé limit <= 100)",
      fw: {
        flask: "limit = min(max(request.args.get('limit', 25, type=int), 1), 100)\noffset = max(request.args.get('offset', 0, type=int), 0)\nitems, total = repo.lister_stagiaires(limit=limit, offset=offset)\nreturn jsonify({'meta': {'total': total, 'limit': limit, 'offset': offset},\n                'data': items, 'links': {'next': f'/api/v1/stagiaires?limit={limit}&offset={offset+limit}'}})",
        fastapi: "@router.get('/stagiaires', response_model=PageStagiaires)\nasync def lister(limit: int = Query(25, ge=1, le=100), offset: int = Query(0, ge=0)):\n    items, total = await repo.lister_stagiaires(limit=limit, offset=offset)\n    return {'meta': {'total': total, 'limit': limit, 'offset': offset}, 'data': items,\n            'links': {'self': f'/api/v1/stagiaires?limit={limit}&offset={offset}'}}",
        tornado: "limit = min(max(int(self.get_query_argument('limit', '25')), 1), 100)\noffset = max(int(self.get_query_argument('offset', '0')), 0)\nitems, total = await self.repo.lister_stagiaires(limit, offset)\nself.write({'meta': {'total': total, 'limit': limit, 'offset': offset},\n            'data': items, 'links': {'self': self.request.uri}})"
      }
    },
    {
      id: 4,
      category: "Nommage & URI",
      title: "Imbrication excessive d'URI vs Profondeur maximale 2 niveaux & filtres de collection",
      rationale: "Au-delà de /ressource/{id}/sous-ressource, les URL deviennent rigides, imposent de connaître toute la hiérarchie parente et compliquent le routage. Exposez la ressource cible au premier rang dès qu'elle possède son propre identifiant métier.",
      badEndpoint: "GET /ecoles/1/departements/2/sessions/4/stagiaires/9/notes",
      badCode: "# Couplage extrême : impossible de consulter une note par son ID\n# ou de lister toutes les notes d'un stagiaire toutes sessions confondues.",
      goodEndpoint: "GET /api/v1/sessions/4/notes?stagiaire_id=9   |   GET /api/v1/notes/842",
      fw: {
        flask: "@api_v1.get('/sessions/<int:session_id>/notes')\ndef notes_de_session(session_id: int):\n    stagiaire_id = request.args.get('stagiaire_id', type=int)\n    return jsonify({'data': repo.chercher_notes(session_id=session_id, stagiaire_id=stagiaire_id)})",
        fastapi: "@router.get('/sessions/{session_id}/notes')\nasync def notes_de_session(session_id: int, stagiaire_id: int | None = Query(None)):\n    return {'data': await repo.chercher_notes(session_id=session_id, stagiaire_id=stagiaire_id)}",
        tornado: "class SessionNotesHandler(BaseApiHandler):\n    async def get(self, session_id: str):\n        stagiaire = self.get_query_argument('stagiaire_id', default=None)\n        data = await self.repo.chercher_notes(int(session_id), int(stagiaire) if stagiaire else None)\n        self.write({'data': data})"
      }
    }
  ];

  ENDPOINT_PATTERNS.push(
    {
      id: 5,
      category: "Payloads & Pagination",
      title: "Secrets ou données sensibles dans la Query String GET vs En-têtes & corps POST sous TLS",
      rationale: "Une URL complète est journalisée en clair dans les fichiers access.log Nginx, l'historique navigateur, les en-têtes Referer et les outils APM. Aucun jeton, mot de passe ou identifiant personnel sensible ne doit transiter en paramètre d'URL.",
      badEndpoint: "GET /api/v1/rapports?api_key=sk_live_98a1&nin=19841609912",
      badCode: "# Fuite immédiate dans /var/log/nginx/access.log et proxies d'entreprise\napi_key = request.args.get('api_key')\nnin = request.args.get('nin')",
      goodEndpoint: "POST /api/v1/rapports/recherches   +   Authorization: Bearer <token>",
      fw: {
        flask: "@api_v1.post('/rapports/recherches')\ndef rechercher_dossier():\n    jeton = extraire_bearer_token(request.headers.get('Authorization', ''))\n    criteres = request.get_json(silent=True) or {}\n    return jsonify({'data': service.rechercher_confidentiel(jeton, criteres['nin'])}), 200",
        fastapi: "@router.post('/rapports/recherches')\nasync def rechercher_dossier(\n    criteres: RechercheConfidentielleIn,\n    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)\n):\n    return {'data': await service.rechercher_confidentiel(creds.credentials, criteres.nin)}",
        tornado: "class RapportsRechercheHandler(BaseApiHandler):\n    async def post(self):\n        jeton = self.require_bearer_token()\n        criteres = self.parse_json_body()\n        res = await self.service.rechercher_confidentiel(jeton, criteres['nin'])\n        self.write({'data': res})"
      }
    },
    {
      id: 6,
      category: "Verbes & Statuts",
      title: "Confusion PUT vs PATCH (écrasement accidentel à NULL) vs Sémantique stricte",
      rationale: "PUT exige une représentation intégrale et remplace toute la ressource ; l'utiliser pour modifier un seul attribut écrase les champs omis à NULL. Pour une modification ciblée, utilisez PATCH en n'appliquant que les clés effectivement présentes dans le JSON.",
      badEndpoint: "PUT /api/v1/formations/12   corps: {\"tarif_centimes\": 95000}",
      badCode: "# Catastrophe : intitule et duree_jours deviennent NULL en base !\ndb.execute('UPDATE formations SET intitule=?, duree_jours=?, tarif_centimes=? WHERE id=?',\n           (data.get('intitule'), data.get('duree_jours'), data.get('tarif_centimes'), 12))",
      goodEndpoint: "PATCH /api/v1/formations/12   (fusion explicite des champs fournis)",
      fw: {
        flask: "@api_v1.patch('/formations/<int:fid>')\ndef modifier_partiel(fid: int):\n    payload = request.get_json(silent=True) or {}\n    champs = {k: payload[k] for k in ('intitule', 'duree_jours', 'tarif_centimes') if k in payload}\n    if not champs:\n        return problem_response(422, 'Aucun champ modifiable fourni', '', request.path)\n    return jsonify(repo.mettre_a_jour_colonnes(fid, champs)), 200",
        fastapi: "@router.patch('/formations/{fid}', response_model=FormationOut)\nasync def modifier_partiel(fid: int, payload: FormationPatchIn):\n    delta = payload.model_dump(exclude_unset=True)\n    if not delta:\n        raise HTTPException(status_code=422, detail='Aucun champ fourni dans le delta PATCH')\n    return await repo.mettre_a_jour_colonnes(fid, delta)",
        tornado: "async def patch(self, fid: str):\n    payload = self.parse_json_body()\n    autorises = {'intitule', 'duree_jours', 'tarif_centimes'}\n    delta = {k: v for k, v in payload.items() if k in autorises}\n    if not delta:\n        return self.write_problem(422, 'Delta PATCH vide ou invalide')\n    self.write(await self.repo.mettre_a_jour_colonnes(int(fid), delta))"
      }
    },
    {
      id: 7,
      category: "Idempotence & Concurrence",
      title: "POST critique non idempotent (double facturation sur retry) vs En-tête Idempotency-Key",
      rationale: "Sur réseau mobile instable, un client qui perd la réponse TCP rejoue sa requête POST. Sans clé d'idempotence mémorisée côté serveur avec empreinte du corps, une inscription ou un paiement est exécuté deux fois.",
      badEndpoint: "POST /api/v1/paiements   (sans clé de déduplication)",
      badCode: "# Si le client relance après une coupure Wi-Fi, un second débit est créé\ntx = passerelle.debiter(payload['montant_centimes'])\ndb.inserer_paiement(tx)",
      goodEndpoint: "POST /api/v1/paiements   +   Idempotency-Key: 7c9e6679-7425-40de-944b-e07fc1f90ae7",
      fw: {
        flask: "idem_key = request.headers.get('Idempotency-Key', '').strip()\nif not idem_key:\n    return problem_response(400, 'En-tête Idempotency-Key obligatoire', '', request.path)\ncached = repo.lire_reponse_idempotente(idem_key, hash_corps(request.data))\nif cached:\n    return Response(cached['body'], status=cached['status'], mimetype='application/json')",
        fastapi: "@router.post('/paiements', status_code=201)\nasync def creer_paiement(payload: PaiementIn, idempotency_key: str = Header(..., min_length=16)):\n    existant = await repo.verifier_idempotence(idempotency_key, payload)\n    if existant:\n        return existant\n    resultat = await service.executer_et_memoriser(idempotency_key, payload)\n    return resultat",
        tornado: "idem_key = self.request.headers.get('Idempotency-Key', '').strip()\nif len(idem_key) < 16:\n    return self.write_problem(400, 'Idempotency-Key requise (16 caractères min)')\nditto = await self.repo.verifier_idempotence(idem_key, self.request.body)\nif ditto:\n    self.set_status(ditto['status']); return self.finish(ditto['body'])"
      }
    },
    {
      id: 8,
      category: "Payloads & Pagination",
      title: "Exposition brute des lignes SQL (fuite interne) vs Projection DTO par liste blanche",
      rationale: "Convertir directement une ligne SQLite ou un modèle ORM en dictionnaire JSON expose les condensats de mot de passe, notes internes d'audit et clés étrangères techniques dès qu'une colonne est ajoutée en base (OWASP API3).",
      badEndpoint: "return jsonify(dict(sqlite_row))   ->   expose password_hash, note_jury_interne",
      badCode: "row = db.execute('SELECT * FROM utilisateurs WHERE id = ?', (uid,)).fetchone()\nreturn jsonify(dict(row))  # Fuite immédiate de password_hash et totp_secret !",
      goodEndpoint: "Projection SQL explicite + sérialiseur DTO à liste blanche stricte",
      fw: {
        flask: "CHAMPS_PUBLICS = ('id', 'nom_complet', 'email', 'structure', 'cree_le')\ndef projeter_utilisateur_public(row) -> dict:\n    return {cle: row[cle] for cle in CHAMPS_PUBLICS}",
        fastapi: "class UtilisateurPublicOut(BaseModel):\n    id: int\n    nom_complet: str\n    email: EmailStr\n    structure: str\n    cree_le: datetime\n# FastAPI filtre automatiquement tout champ hors UtilisateurPublicOut",
        tornado: "def serialiser_utilisateur_public(row: dict) -> dict:\n    return {\n        'id': row['id'], 'nom_complet': row['nom_complet'],\n        'email': row['email'], 'structure': row['structure'], 'cree_le': row['cree_le']\n    }"
      }
    },
    {
      id: 9,
      category: "Verbes & Statuts",
      title: "Création en 200 sans Location & DELETE bavard vs 201 Created + Location & 204 No Content",
      rationale: "Lors d'une création synchrone, HTTP 201 accompagné de l'en-tête Location indique immédiatement au client l'URI canonique de la ressource créée. Lors d'une suppression définitive, HTTP 204 évite d'envoyer un JSON artificiel inutile.",
      badEndpoint: "POST /inscriptions -> 200 OK \"Inscription OK\"  |  DELETE -> 200 {\"deleted\": true}",
      badCode: "@app.post('/inscriptions')\ndef add_ins():\n    new_id = repo.creer(request.json)\n    return jsonify({'msg': 'OK'}), 200  # Ni ressource créée ni URI Location",
      goodEndpoint: "POST -> 201 Created + Location: /api/v1/inscriptions/48   |   DELETE -> 204 No Content",
      fw: {
        flask: "@api_v1.post('/inscriptions')\ndef creer_inscription():\n    ins = service.inscrire(request.get_json())\n    resp = jsonify({'data': ins})\n    resp.status_code = 201\n    resp.headers['Location'] = f\"/api/v1/inscriptions/{ins['id']}\"\n    return resp",
        fastapi: "@router.post('/inscriptions', status_code=201)\nasync def creer_inscription(payload: InscriptionIn, response: Response):\n    ins = await service.inscrire(payload)\n    response.headers['Location'] = f'/api/v1/inscriptions/{ins.id}'\n    return {'data': ins}",
        tornado: "async def post(self):\n    ins = await self.service.inscrire(self.parse_json_body())\n    self.set_status(201)\n    self.set_header('Location', f\"/api/v1/inscriptions/{ins['id']}\")\n    self.write({'data': ins})"
      }
    }
  );

  ENDPOINT_PATTERNS.push(
    {
      id: 10,
      category: "Idempotence & Concurrence",
      title: "Traitement lourd synchrone (504 Gateway Timeout) vs 202 Accepted & ressource Job",
      rationale: "Générer 800 attestations PDF ou consolider un bilan comptable dans le cycle requête-réponse immobilise le worker WSGI/ASGI et provoque une coupure 504 sur le proxy. Basculez vers le patron asynchrone 202 Accepted avec URL d'état.",
      badEndpoint: "POST /api/v1/attestations/lot   (bloque 42 secondes -> 504 Gateway Timeout)",
      badCode: "# Immobilise le worker Gunicorn pendant 42s ; aucune reprise sur incident\npdfs = generer_toutes_les_attestations_lourdes(session_id)\nreturn send_file(pdfs)",
      goodEndpoint: "POST /api/v1/attestations/lots -> 202 Accepted + Location: /api/v1/jobs/jb_904",
      fw: {
        flask: "@api_v1.post('/attestations/lots')\ndef lancer_generation_lot():\n    job_id = file_travaux.planifier('generation_pdf', request.get_json())\n    return jsonify({'job_id': job_id, 'statut': 'EN_ATTENTE',\n                    'suivi_url': f'/api/v1/jobs/{job_id}'}), 202, {'Location': f'/api/v1/jobs/{job_id}'}",
        fastapi: "@router.post('/attestations/lots', status_code=202)\nasync def lancer_generation(payload: LotPdfIn, bg: BackgroundTasks, response: Response):\n    job_id = await repo.creer_job('EN_ATTENTE')\n    bg.add_task(executer_generation_lot, job_id, payload)\n    response.headers['Location'] = f'/api/v1/jobs/{job_id}'\n    return {'job_id': job_id, 'statut': 'EN_ATTENTE', 'suivi_url': f'/api/v1/jobs/{job_id}'}",
        tornado: "async def post(self):\n    job_id = await self.repo.creer_job('EN_ATTENTE')\n    tornado.ioloop.IOLoop.current().spawn_callback(self.worker.generer_lot, job_id)\n    self.set_status(202)\n    self.set_header('Location', f'/api/v1/jobs/{job_id}')\n    self.write({'job_id': job_id, 'statut': 'EN_ATTENTE'})"
      }
    },
    {
      id: 11,
      category: "Payloads & Pagination",
      title: "Tri ou filtre dynamique concaténé en SQL vs Liste blanche stricte des colonnes & sens",
      rationale: "Les marqueurs SQL paramétrés (?) protègent les valeurs, jamais les identifiants de colonnes dans ORDER BY. Concaténer request.args['sort'] ouvre une injection SQL directe : traduisez toujours via un dictionnaire fermé.",
      badEndpoint: "GET /api/v1/formations?sort=tarif;DROP TABLE formations--",
      badCode: "# Injection SQL critique sur clause ORDER BY non paramétrable par ?\nsort_col = request.args.get('sort', 'id')\ndb.execute(f'SELECT * FROM formations ORDER BY {sort_col}')",
      goodEndpoint: "GET /api/v1/formations?sort=-tarif_centimes   (mapping par dictionnaire fermé)",
      fw: {
        flask: "COLONNES_TRI = {'tarif_centimes': 'tarif_centimes', 'intitule': 'intitule', 'date': 'cree_le'}\nraw = request.args.get('sort', 'date')\ndirection = 'DESC' if raw.startswith('-') else 'ASC'\ncol_sql = COLONNES_TRI.get(raw.lstrip('-'))\nif not col_sql:\n    return problem_response(400, 'Critère de tri non autorisé', raw, request.path)",
        fastapi: "TriFormation = Literal['intitule', '-intitule', 'tarif_centimes', '-tarif_centimes']\n@router.get('/formations')\nasync def lister_formations(sort: TriFormation = 'intitule'):\n    col = sort.lstrip('-')\n    sens = 'DESC' if sort.startswith('-') else 'ASC'\n    return {'data': await repo.lister_trie(col, sens)}",
        tornado: "COLONNES_TRI = {'intitule': 'intitule', 'tarif_centimes': 'tarif_centimes'}\nraw = self.get_query_argument('sort', 'intitule')\nsens = 'DESC' if raw.startswith('-') else 'ASC'\ncol = COLONNES_TRI.get(raw.lstrip('-'))\nif not col:\n    return self.write_problem(400, 'Colonne de tri refusée')"
      }
    },
    {
      id: 12,
      category: "Performance & Versioning",
      title: "Rupture silencieuse de contrat d'API vs Versioning explicite & en-têtes Sunset (RFC 8594)",
      rationale: "Renommer un champ JSON en production casse instantanément les applications mobiles non mises à jour. Versionnez les changements incompatibles (/api/v1 -> /api/v2) et annoncez l'extinction progressive via Deprecation et Sunset.",
      badEndpoint: "Renommer \"nom\" en \"nom_complet\" directement sur /api/formations",
      badCode: "# Casse immédiate des intégrations partenaires RH et applications mobiles\nreturn {'nom_complet': u.nom}  # L'ancien champ 'nom' a disparu sans préavis",
      goodEndpoint: "/api/v1 maintenu avec Deprecation + Sunset  |  /api/v2 introduit proprement",
      fw: {
        flask: "@api_v1.after_request\ndef signaler_fin_v1(resp):\n    resp.headers['Deprecation'] = 'true'\n    resp.headers['Sunset'] = 'Wed, 30 Jun 2027 23:59:59 GMT'\n    resp.headers['Link'] = '</api/v2/formations>; rel=\"successor-version\"'\n    return resp",
        fastapi: "@router_v1.get('/formations')\nasync def lister_v1(response: Response):\n    response.headers['Deprecation'] = 'true'\n    response.headers['Sunset'] = 'Wed, 30 Jun 2027 23:59:59 GMT'\n    response.headers['Link'] = '</api/v2/formations>; rel=\"successor-version\"'\n    return await repo.lister_format_v1()",
        tornado: "class BaseV1Handler(BaseApiHandler):\n    def set_default_headers(self):\n        super().set_default_headers()\n        self.set_header('Deprecation', 'true')\n        self.set_header('Sunset', 'Wed, 30 Jun 2027 23:59:59 GMT')"
      }
    },
    {
      id: 13,
      category: "Performance & Versioning",
      title: "Cascade N+1 d'appels HTTP côté client vs Expansion contrôlée (?include=formateur)",
      rationale: "Afficher 30 sessions en déclenchant 1 requête de liste suivie de 30 requêtes GET /formateurs/{id} pénalise la latence mobile par 31 allers-retours réseau. Offrez une expansion optionnelle bornée adossée à une jointure SQL unique.",
      badEndpoint: "1x GET /sessions + 30x GET /formateurs/{id}   (31 requêtes HTTP en série)",
      badCode: "// Client contraint de boucler sur chaque élément de la liste :\nfor (const s of sessions) {\n  s.formateur = await fetch(`/api/v1/formateurs/${s.formateur_id}`).then(r => r.json());\n}",
      goodEndpoint: "GET /api/v1/sessions?include=formateur   (1 requête HTTP + 1 LEFT JOIN SQL)",
      fw: {
        flask: "inclusions = set(filter(None, request.args.get('include', '').split(',')))\nif not inclusions.issubset({'formateur', 'salle'}):\n    return problem_response(400, 'Relation include non supportée', '', request.path)\nreturn jsonify({'data': repo.lister_sessions(inclure_formateur='formateur' in inclusions)})",
        fastapi: "@router.get('/sessions')\nasync def lister_sessions(include: str | None = Query(None, pattern='^(formateur|salle)(,(formateur|salle))*$')):\n    inc = set(include.split(',')) if include else set()\n    return {'data': await repo.lister_sessions(inclure_formateur='formateur' in inc)}",
        tornado: "inc = set(filter(None, self.get_query_argument('include', '').split(',')))\nif not inc.issubset({'formateur', 'salle'}):\n    return self.write_problem(400, 'Paramètre include invalide')\nself.write({'data': await self.repo.lister_sessions('formateur' in inc)})"
      }
    },
    {
      id: 14,
      category: "Verbes & Statuts",
      title: "Absence de validation MIME (Content-Type ignoré) vs Rejet strict 415 Unsupported Media Type",
      rationale: "Accepter un corps JSON envoyé sous text/plain affaiblit la protection preflight CORS des navigateurs et provoque des erreurs de décodage ambiguës. Exigez application/json sur toute route recevant une charge utile.",
      badEndpoint: "POST /api/v1/formations avec Content-Type: text/plain accepté silencieusement",
      badCode: "# Décodage forcé même si le client envoie un formulaire HTML ou text/plain\ndata = json.loads(request.data.decode('utf-8'))",
      goodEndpoint: "Vérification stricte Content-Type: application/json -> sinon 415 Unsupported Media Type",
      fw: {
        flask: "@api_v1.before_request\ndef verifier_mime_json():\n    if request.method in ('POST', 'PUT', 'PATCH') and not request.is_json:\n        return problem_response(415, 'Type MIME non supporté', 'Utilisez application/json', request.path)",
        fastapi: "@app.middleware('http')\nasync def enforce_json_mime(req: Request, call_next):\n    if req.method in ('POST', 'PUT', 'PATCH'):\n        ct = req.headers.get('content-type', '')\n        if not ct.startswith('application/json'):\n            return JSONResponse(status_code=415, content={'title': 'Content-Type application/json requis'})\n    return await call_next(req)",
        tornado: "def prepare(self):\n    if self.request.method in ('POST', 'PUT', 'PATCH'):\n        ct = self.request.headers.get('Content-Type', '')\n        if not ct.startswith('application/json'):\n            return self.write_problem(415, 'Content-Type application/json obligatoire')"
      }
    },
    {
      id: 15,
      category: "Idempotence & Concurrence",
      title: "Écrasement concurrent silencieux (Lost Update) vs ETag + If-Match (412 Precondition Failed)",
      rationale: "Si deux coordinateurs modifient simultanément le même planning, le dernier enregistrement écrase silencieusement le travail du premier. Émettez un en-tête ETag (version/hash) au GET et exigez If-Match lors du PUT/PATCH.",
      badEndpoint: "Deux PUT concurrents sans numéro de version -> perte silencieuse de mise à jour",
      badCode: "# Aucune vérification de la version lue par l'utilisateur avant modification\ndb.execute('UPDATE formations SET places = ? WHERE id = ?', (places, fid))",
      goodEndpoint: "GET renvoie ETag: \"v4\" -> PATCH exige If-Match: \"v4\" (sinon 412 Precondition Failed)",
      fw: {
        flask: "attendu = request.headers.get('If-Match')\nactuel = f'\"v{formation[\"version\"]}\"'\nif attendu != actuel:\n    return problem_response(412, 'Conflit de version concurrente', 'Rechargez la ressource', request.path)\nrepo.mettre_a_jour_si_version(fid, payload, version=formation['version'])",
        fastapi: "@router.patch('/formations/{fid}')\nasync def maj_optimiste(fid: int, payload: FormationPatchIn, if_match: str = Header(...)):\n    ok = await repo.maj_avec_version(fid, payload, etag_attendu=if_match)\n    if not ok:\n        raise HTTPException(status_code=412, detail='Ressource modifiée par un tiers (ETag obsolète)')\n    return ok",
        tornado: "if_match = self.request.headers.get('If-Match')\nif not if_match:\n    return self.write_problem(428, 'En-tête If-Match requis pour cette modification')\nok = await self.repo.maj_avec_version(int(fid), payload, if_match)\nif not ok:\n    return self.write_problem(412, 'Version ETag périmée')"
      }
    }
  );

  ENDPOINT_PATTERNS.push(
    {
      id: 16,
      category: "Nommage & URI",
      title: "Transition métier forcée dans un GET à effet de bord vs Sous-ressource d'intention POST",
      rationale: "Selon la RFC 9110, GET est strictement Safe : les antivirus d'e-mail, aperçus de messagerie et caches CDN pré-chargent les liens GET sans action humaine. Modélisez toute transition d'état comme une sous-ressource nominale manipulée par POST ou DELETE.",
      badEndpoint: "GET /formations/5?publier=1   |   GET /sessions/8/annuler",
      badCode: "# Un simple aperçu de lien dans Slack ou Outlook publie la formation en prod !\nif request.args.get('publier') == '1':\n    repo.changer_statut(5, 'PUBLIEE')",
      goodEndpoint: "POST /api/v1/formations/5/publication   (et DELETE pour dépublier)",
      fw: {
        flask: "@api_v1.post('/formations/<int:fid>/publication')\ndef publier_formation(fid: int):\n    etat = service.publier_catalogue(fid, auteur_id=g.user_id)\n    return jsonify({'data': etat}), 200",
        fastapi: "@router.post('/formations/{fid}/publication', status_code=200)\nasync def publier_formation(fid: int, user: UserCtx = Depends(require_coordinateur)):\n    return {'data': await service.publier_catalogue(fid, auteur_id=user.id)}",
        tornado: "class FormationPublicationHandler(BaseApiHandler):\n    async def post(self, fid: str):\n        user = self.require_role('coordinateur')\n        etat = await self.service.publier_catalogue(int(fid), user['id'])\n        self.write({'data': etat})"
      }
    },
    {
      id: 17,
      category: "Payloads & Pagination",
      title: "Dates locales ambiguës & montants float IEEE 754 vs ISO 8601 UTC & entiers monétaires",
      rationale: "03/04/26 est interprété différemment entre Europe et États-Unis, et 0.1 + 0.2 vaut 0.30000000000000004 en virgule flottante binaire. Exigez systématiquement l'horodatage ISO 8601 en UTC (suffixe Z) et des montants entiers en sous-unités (centimes) avec code devise ISO 4217.",
      badEndpoint: "{\"date\": \"03/04/26\", \"montant\": 149.99}   (fuseau inconnu + dérive binaire)",
      badCode: "# Erreur d'arrondi comptable : round(19.99 * 3, 2) diverge sur cumul massif\ntotal = sum(float(ligne['montant']) for ligne in lignes)",
      goodEndpoint: "{\"horodatage_utc\": \"2026-04-03T14:30:00Z\", \"montant_centimes\": 1499900, \"devise\": \"DZD\"}",
      fw: {
        flask: "from datetime import datetime, timezone\nnow_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')\nreturn jsonify({'horodatage_utc': now_iso, 'montant_centimes': 1499900, 'devise': 'DZD'})",
        fastapi: "class FactureOut(BaseModel):\n    horodatage_utc: datetime  # Sérialisé en ISO 8601 avec fuseau UTC\n    montant_centimes: int = Field(..., ge=0)\n    devise: Literal['DZD', 'EUR', 'USD'] = 'DZD'",
        tornado: "now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')\nself.write({'horodatage_utc': now_iso, 'montant_centimes': int(centimes), 'devise': 'DZD'})"
      }
    },
    {
      id: 18,
      category: "Nommage & URI",
      title: "Casse mixte, underscores, singulier & slash final aléatoire vs Canon kebab-case pluriel",
      rationale: "Les chemins HTTP sont sensibles à la casse selon la RFC 3986 (/Formations != /formations), et les underscores sont masqués par le soulignement des hyperliens. Standardisez tout le contrat en minuscules, mots séparés par tirets (kebab-case) et noms de collections au pluriel sans slash final.",
      badEndpoint: "GET /API/Get_Demande_Inscription/   (CamelCase + underscore + singulier + slash)",
      badCode: "# Génère des duplications de cache et des redirections 308/301 parasites\n@app.get('/API/Get_Demande_Inscription/')",
      goodEndpoint: "GET /api/v1/demandes-inscription",
      fw: {
        flask: "api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')\n@api_v1.get('/demandes-inscription')\ndef lister_demandes_inscription():\n    return jsonify({'data': repo.lister_demandes(limit=25, offset=0)}), 200",
        fastapi: "router = APIRouter(prefix='/api/v1')\n@router.get('/demandes-inscription')\nasync def lister_demandes_inscription():\n    return {'data': await repo.lister_demandes(limit=25, offset=0)}",
        tornado: "# Routage Tornado explicite sans slash final parasite :\n(r'/api/v1/demandes-inscription', DemandesInscriptionCollectionHandler)"
      }
    },
    {
      id: 19,
      category: "Performance & Versioning",
      title: "Appel E/S synchrone bloquant la boucle async vs Exécution adaptée au moteur d'exécution",
      rationale: "Appeler requests.get() ou time.sleep() dans une coroutine async def FastAPI ou Tornado fige l'unique thread de la boucle d'événements pour tous les clients connectés. Utilisez un client asynchrone natif ou déportez le code bloquant dans un pool de threads.",
      badEndpoint: "async def get(): requests.get('https://partenaire...')  # Gèle toute l'IOLoop !",
      badCode: "# Anti-pattern critique ASGI / Tornado : bloque 100 % des requêtes concurrentes\nasync def verifier_certificat():\n    r = requests.get('https://registre.isgp.dz/verif', timeout=10)\n    return r.json()",
      goodEndpoint: "Client non-bloquant (httpx.AsyncClient / AsyncHTTPClient) ou pool WSGI borné",
      fw: {
        flask: "# En WSGI (Flask/Gunicorn gthread), borner impérativement connect & read timeout :\nsession_http = requests.Session()\nresp = session_http.get(url_partenaire, timeout=(2.0, 5.0))",
        fastapi: "# En ASGI (FastAPI), utiliser httpx.AsyncClient partagé dans lifespan :\nasync def verifier_certificat(client: httpx.AsyncClient = Depends(get_http_client)):\n    resp = await client.get('https://registre.isgp.dz/verif', timeout=5.0)\n    return resp.json()",
        tornado: "# En Tornado, utiliser tornado.httpclient.AsyncHTTPClient ou run_in_executor :\nclient = tornado.httpclient.AsyncHTTPClient()\nresp = await client.fetch('https://registre.isgp.dz/verif', request_timeout=5.0)"
      }
    },
    {
      id: 20,
      category: "Performance & Versioning",
      title: "API muette en production vs Corrélation X-Request-ID & sondes Liveness / Readiness",
      rationale: "Sans identifiant de corrélation propagé dans chaque réponse et chaque ligne de log, diagnostiquer un incident distribué relève de la devinette. Ajoutez X-Request-ID et séparez la sonde de vie (/health/live) de la sonde de disponibilité SQL (/health/ready).",
      badEndpoint: "Aucun X-Request-ID, aucune route /health -> orchestrateur incapable d'isoler un nœud",
      badCode: "except Exception:\n    return 'Erreur serveur', 500  # Aucune trace corrélée pour le support",
      goodEndpoint: "En-tête X-Request-ID systématique + GET /health/live (200) & GET /health/ready (200/503)",
      fw: {
        flask: "@app.before_request\ndef attacher_request_id():\n    g.request_id = request.headers.get('X-Request-ID') or uuid.uuid4().hex\n@app.after_request\ndef propager_request_id(resp):\n    resp.headers['X-Request-ID'] = g.request_id\n    return resp",
        fastapi: "@app.get('/health/ready')\nasync def readiness_probe():\n    ok = await repo.ping_sql()\n    if not ok:\n        return JSONResponse(status_code=503, content={'status': 'DEGRADED', 'db': False})\n    return {'status': 'READY', 'db': True}",
        tornado: "def prepare(self):\n    self.req_id = self.request.headers.get('X-Request-ID') or uuid.uuid4().hex\n    self.set_header('X-Request-ID', self.req_id)"
      }
    }
  );

  const LINTER_PRESETS = {
    bad_rpc_user: {
      label: "[Anti-Pattern 1] POST /API/createUser?admin_token=... (RPC + secret + faux 200)",
      method: "POST",
      uri: "/API/createUser?admin_token=sec_9981",
      status: "200",
      sample: JSON.stringify(
        {
          success: false,
          error: "Email déjà enregistré",
          password_hash: "$2b$12$K8H1x...",
          date_creation: "14/11/26",
          prix_formation: 149.99
        },
        null,
        2
      )
    },
    bad_get_delete: {
      label: "[Anti-Pattern 2] GET /delete_formation?id=7 (Mutation sur GET + underscore)",
      method: "GET",
      uri: "/delete_formation?id=7&secret_key=xyz",
      status: "200",
      sample: JSON.stringify({ status: "error", message: "Suppression refusée" }, null, 2)
    },
    bad_deep_array: {
      label: "[Anti-Pattern 3] GET /ecoles/1/departements/2/sessions/4/stagiaires/9/notes (Imbrication + tableau nu)",
      method: "GET",
      uri: "/ecoles/1/departements/2/sessions/4/stagiaires/9/notes",
      status: "200",
      sample: JSON.stringify(
        [
          { id: 1, note: 16.5, date_eval: "02/05/26", internal_note: "Jury interne" }
        ],
        null,
        2
      )
    },
    bad_singular_post: {
      label: "[Anti-Pattern 4] POST /Formation/Ajouter/ (Majuscules + singulier + 200 sans Location)",
      method: "POST",
      uri: "/Formation/Ajouter/",
      status: "200",
      sample: JSON.stringify({ id: 42, tarif: 89000.5, debut: "19/09/2026" }, null, 2)
    },
    bad_get_side_effect: {
      label: "[Anti-Pattern 5] GET /api/v1/formation/5?publier=1 (Effet de bord dans Query String)",
      method: "GET",
      uri: "/api/v1/formation/5?publier=1",
      status: "201",
      sample: JSON.stringify([{ ok: true }], null, 2)
    },
    good_paginated_list: {
      label: "[Architecture Cible 1] GET /api/v1/formations?limit=20&offset=0 (Collection paginée)",
      method: "GET",
      uri: "/api/v1/formations?limit=20&offset=0",
      status: "200",
      sample: JSON.stringify(
        {
          meta: { total: 48, limit: 20, offset: 0 },
          data: [
            {
              id: 101,
              intitule: "Architecture des APIs Modernes",
              tarif_centimes: 7500000,
              devise: "DZD",
              cree_le: "2026-11-14T09:30:00Z"
            }
          ],
          links: { self: "/api/v1/formations?limit=20&offset=0" }
        },
        null,
        2
      )
    },
    good_post_created: {
      label: "[Architecture Cible 2] POST /api/v1/inscriptions -> 201 Created (Création conforme)",
      method: "POST",
      uri: "/api/v1/inscriptions",
      status: "201",
      sample: JSON.stringify(
        {
          data: {
            id: 509,
            stagiaire_id: 14,
            session_id: 8,
            montant_centimes: 4500000,
            devise: "DZD",
            horodatage_utc: "2026-11-16T14:00:00Z"
          }
        },
        null,
        2
      )
    },
    good_problem_rfc7807: {
      label: "[Architecture Cible 3] DELETE /api/v1/formations/999 -> 404 RFC 7807 Problem Details",
      method: "DELETE",
      uri: "/api/v1/formations/999",
      status: "404",
      sample: JSON.stringify(
        {
          type: "https://api.isgp.dz/erreurs/ressource-introuvable",
          title: "Formation introuvable",
          status: 404,
          detail: "Aucune formation active ne porte l'identifiant 999.",
          instance: "/api/v1/formations/999"
        },
        null,
        2
      )
    }
  };

  function normalizeSlugToPlural(seg) {
    let s = seg
      .replace(/([a-z])([A-Z])/g, "$1-$2")
      .toLowerCase()
      .replace(/_/g, "-")
      .replace(/^(create|delete|update|get|fetch|add|remove|ajouter|supprimer|modifier)-?/, "");
    if (!s) s = "ressources";
    const map = {
      user: "utilisateurs",
      users: "utilisateurs",
      utilisateur: "utilisateurs",
      formation: "formations",
      stagiaire: "stagiaires",
      inscription: "inscriptions",
      commande: "commandes",
      dossier: "dossiers",
      session: "sessions",
      note: "notes"
    };
    if (map[s]) return map[s];
    if (!s.endsWith("s") && !s.endsWith("x") && s !== "publication" && s !== "health") {
      return s + "s";
    }
    return s;
  }

  function evaluateEndpointDesign(methodRaw, uriRaw, statusRaw, sampleRaw) {
    const method = (methodRaw || "GET").toUpperCase().trim();
    const fullUri = (uriRaw || "/").trim();
    const status = parseInt(statusRaw, 10) || 200;
    const [rawPath, rawQuery = ""] = fullUri.split("?");
    const segments = rawPath.split("/").filter(Boolean);

    let parsed = null;
    let jsonValid = true;
    if (sampleRaw.trim() !== "" && status !== 204) {
      try {
        parsed = JSON.parse(sampleRaw);
      } catch (e) {
        jsonValid = false;
      }
    }

    const rpcRegex = /(create|delete|update|get|fetch|add|remove|supprimer|ajouter|modifier)/i;
    const hasRpcVerb = segments.some((s) => rpcRegex.test(s));

    const hasBadCaseOrChar =
      /[A-Z_]/.test(rawPath) || (rawPath.length > 1 && rawPath.endsWith("/")) || rawPath.includes("//");

    const hasVersion = /^\/api\/v\d+\//.test(rawPath) || rawPath.startsWith("/health");

    const domainSegs = segments.filter((s) => s.toLowerCase() !== "api" && !/^v\d+$/i.test(s));
    const resourceSegs = domainSegs.filter((s) => !/^\d+$/.test(s) && !/^\{.*\}$/.test(s));
    const tooDeep = resourceSegs.length > 2;

    const singularNouns = new Set([
      "user", "utilisateur", "formation", "stagiaire", "inscription", "commande", "dossier", "ecole", "session", "note"
    ]);
    const hasSingularResource = resourceSegs.some((s) => singularNouns.has(s.toLowerCase()));

    const secretOrMutationQuery =
      /(token|secret|password|api_key|apikey|jwt|nin)/i.test(rawQuery) ||
      (method === "GET" && /(delete|supprimer|publier|annuler|action)=/i.test(rawQuery));

    const getMutates =
      method === "GET" && (/(delete|supprimer|create|ajouter|update|publier|annuler)/i.test(fullUri) || status === 201);
    const postReturns200 = method === "POST" && status === 200;
    const verbStatusOk = !getMutates && !postReturns200;

    const sampleStr = sampleRaw || "";
    const fake200Error =
      status >= 200 &&
      status < 300 &&
      parsed &&
      !Array.isArray(parsed) &&
      (parsed.success === false ||
        parsed.status === "error" ||
        typeof parsed.error === "string" ||
        typeof parsed.err === "string");

    const rootArrayOnGet = method === "GET" && Array.isArray(parsed);
    const leaksInternal = /(password_hash|password|secret_key|internal_note|totp_secret)/i.test(sampleStr);
    const envelopeAndDtoOk = jsonValid && !rootArrayOnGet && !leaksInternal;

    const ambiguousDate = /\b\d{2}\/\d{2}\/\d{2,4}\b/.test(sampleStr);
    const floatMoney = /"(prix|prix_formation|tarif|montant|amount)"\s*:\s*\d+\.\d+/i.test(sampleStr);
    const typesOk = jsonValid && !ambiguousDate && !floatMoney;

    const rules = [
      {
        id: 1,
        name: "Absence de verbe RPC dans le chemin URI",
        passed: !hasRpcVerb,
        detail: hasRpcVerb
          ? "Segment procédural détecté dans le chemin ; déplacez l'action vers le verbe HTTP."
          : "Chemin strictement orienté ressources nominales."
      },
      {
        id: 2,
        name: "Canon typographique minuscules kebab-case sans slash final",
        passed: !hasBadCaseOrChar,
        detail: hasBadCaseOrChar
          ? "Majuscules, underscores (_) ou barre oblique finale superflue détectés."
          : "Formatage URI canonique respecté."
      },
      {
        id: 3,
        name: "Versioning explicite du contrat (/api/v1/...)",
        passed: hasVersion,
        detail: hasVersion
          ? "Préfixe de version d'API présent."
          : "Préfixe /api/v1 manquant : toute évolution future cassera les clients existants."
      },
      {
        id: 4,
        name: "Profondeur hiérarchique maîtrisée (<= 2 niveaux de ressources)",
        passed: !tooDeep,
        detail: tooDeep
          ? `Imbrication excessive (${resourceSegs.length} niveaux) ; privilégiez une ressource racine filtrée.`
          : "Hiérarchie d'URI concise et découplée."
      },
      {
        id: 5,
        name: "Collections nommées au pluriel",
        passed: !hasSingularResource,
        detail: hasSingularResource
          ? "Nom de ressource au singulier détecté ; standardisez les collections au pluriel."
          : "Collections cohérentes au pluriel."
      },
      {
        id: 6,
        name: "Zéro secret ni mutation cachée dans la Query String",
        passed: !secretOrMutationQuery,
        detail: secretOrMutationQuery
          ? "Secret exposé dans l'URL (journalisé en clair) ou transition d'état passée en paramètre GET."
          : "Paramètres de requête exempts de secrets et d'effets de bord."
      },
      {
        id: 7,
        name: "Alignement sémantique Méthode HTTP / Code de statut",
        passed: verbStatusOk,
        detail: getMutates
          ? "Violation RFC 9110 : GET ne doit jamais muter ni créer d'état serveur."
          : postReturns200
            ? "Un POST de création synchrone doit renvoyer 201 Created (+ Location) ou 202 Accepted."
            : "Couple méthode HTTP et statut de réponse conforme."
      },
      {
        id: 8,
        name: "Statuts d'erreur francs (aucun faux 200 OK, format RFC 7807)",
        passed: !fake200Error && jsonValid,
        detail: !jsonValid
          ? "Échantillon JSON syntaxiquement invalide."
          : fake200Error
            ? "Anti-pattern critique : statut 200 OK transportant un échec métier masqué."
            : "Sémantique d'état HTTP honnête et exploitable."
      },
      {
        id: 9,
        name: "Enveloppe paginée {meta, data, links} & projection DTO sans fuite SQL",
        passed: envelopeAndDtoOk,
        detail: leaksInternal
          ? "Fuite de colonne interne sensible détectée (password_hash / internal_note)."
          : rootArrayOnGet
            ? "Tableau JSON racine non paginé : encapsulez dans {meta, data, links} avec plafond limit."
            : "Structure de charge utile maîtrisée et filtrée."
      },
      {
        id: 10,
        name: "Dates UTC ISO 8601 (suffixe Z) & montants entiers en centimes",
        passed: typesOk,
        detail: ambiguousDate
          ? "Date locale ambiguë (JJ/MM/AA) détectée ; utilisez ISO 8601 UTC (YYYY-MM-DDTHH:MM:SSZ)."
          : floatMoney
            ? "Montant monétaire en float IEEE 754 détecté ; stockez un entier en centimes + devise."
            : "Représentation temporelle et monétaire sans dérive."
      }
    ];

    const score = rules.reduce((acc, r) => acc + (r.passed ? 10 : 0), 0);
    return { score, rules, corrected: buildRefactoredSuggestion(method, fullUri, status, fake200Error, getMutates, resourceSegs, rawQuery) };
  }

  function buildRefactoredSuggestion(method, fullUri, status, fake200Error, getMutates, resourceSegs, rawQuery) {
    let targetMethod = method;
    if (/delete|supprimer/i.test(fullUri)) targetMethod = "DELETE";
    else if (/publier|create|ajouter/i.test(fullUri) && method === "GET") targetMethod = "POST";

    const primaryNoun = resourceSegs.length
      ? normalizeSlugToPlural(resourceSegs[resourceSegs.length - 1])
      : "formations";

    let targetPath = `/api/v1/${primaryNoun}`;
    if (/publier=1/i.test(rawQuery)) {
      targetPath = `/api/v1/${primaryNoun}/5/publication`;
    } else if (targetMethod === "DELETE") {
      targetPath = `/api/v1/${primaryNoun}/7`;
    } else if (targetMethod === "GET") {
      targetPath = `/api/v1/${primaryNoun}?limit=20&offset=0`;
    }

    let targetStatus = status;
    if (fake200Error) targetStatus = 409;
    else if (targetMethod === "DELETE" && status < 400) targetStatus = 204;
    else if (targetMethod === "POST" && status === 200) targetStatus = 201;
    else if (getMutates) targetStatus = 200;

    const cleanSlug = primaryNoun.replace(/-/g, "_");
    return {
      method: targetMethod,
      uri: targetPath,
      status: targetStatus,
      code: {
        flask:
          targetMethod === "DELETE"
            ? `@api_v1.delete('/${primaryNoun}/<int:item_id>')\ndef supprimer_${cleanSlug}(item_id: int):\n    exige_bearer_et_rbac(request)\n    if not repo.supprimer(item_id):\n        return problem_response(404, 'Ressource introuvable', '', request.path)\n    return '', 204`
            : targetMethod === "POST"
              ? `@api_v1.post('${targetPath.replace("/api/v1", "")}')\ndef creer_${cleanSlug}():\n    exige_bearer_et_rbac(request)\n    dto = valider_schema_entree(request.get_json(silent=True))\n    entite = service.executer_creation(dto)\n    return jsonify({'data': entite}), ${targetStatus}, {'Location': f'/api/v1/${primaryNoun}/{entite[\"id\"]}'}`
              : `@api_v1.get('/${primaryNoun}')\ndef lister_${cleanSlug}():\n    limit = min(max(request.args.get('limit', 20, type=int), 1), 100)\n    offset = max(request.args.get('offset', 0, type=int), 0)\n    items, total = repo.lister_pagine(limit=limit, offset=offset)\n    return jsonify({'meta': {'total': total, 'limit': limit, 'offset': offset}, 'data': items}), 200`,
        fastapi:
          targetMethod === "DELETE"
            ? `@router.delete('/${primaryNoun}/{item_id}', status_code=204)\nasync def supprimer_${cleanSlug}(item_id: int, user: UserCtx = Depends(require_auth)):\n    ok = await repo.supprimer(item_id)\n    if not ok:\n        raise ProblemException(404, 'Ressource introuvable')\n    return Response(status_code=204)`
            : targetMethod === "POST"
              ? `@router.post('${targetPath.replace("/api/v1", "")}', status_code=${targetStatus})\nasync def creer_${cleanSlug}(payload: EntreeDTO, response: Response, user: UserCtx = Depends(require_auth)):\n    entite = await service.executer_creation(payload)\n    response.headers['Location'] = f'/api/v1/${primaryNoun}/{entite.id}'\n    return {'data': entite}`
              : `@router.get('/${primaryNoun}')\nasync def lister_${cleanSlug}(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):\n    items, total = await repo.lister_pagine(limit=limit, offset=offset)\n    return {'meta': {'total': total, 'limit': limit, 'offset': offset}, 'data': items}`,
        tornado:
          targetMethod === "DELETE"
            ? `class ${cleanSlug.toUpperCase()}ItemHandler(BaseApiHandler):\n    async def delete(self, item_id: str):\n        self.require_bearer_token()\n        if not await self.repo.supprimer(int(item_id)):\n            return self.write_problem(404, 'Ressource introuvable')\n        self.set_status(204)\n        await self.finish()`
            : targetMethod === "POST"
              ? `class ${cleanSlug.toUpperCase()}CollectionHandler(BaseApiHandler):\n    async def post(self, *args):\n        self.require_bearer_token()\n        dto = self.valider_dto(self.parse_json_body())\n        entite = await self.service.executer_creation(dto)\n        self.set_status(${targetStatus})\n        self.set_header('Location', f\"/api/v1/${primaryNoun}/{entite['id']}\")\n        self.write({'data': entite})`
              : `class ${cleanSlug.toUpperCase()}CollectionHandler(BaseApiHandler):\n    async def get(self):\n        limit = min(max(int(self.get_query_argument('limit', '20')), 1), 100)\n        offset = max(int(self.get_query_argument('offset', '0')), 0)\n        items, total = await self.repo.lister_pagine(limit, offset)\n        self.write({'meta': {'total': total, 'limit': limit, 'offset': offset}, 'data': items})`
      }
    };
  }

  function renderSynthesisSection(fw) {
    const matrixRows = HTTP_MATRIX.map(
      (r) => `
      <tr>
        <td><code>${escHtml(r.verb)}</code></td>
        <td><span class="nt-badge ${r.safe === "Oui" ? "nt-badge-success" : "nt-badge-warn"}">${escHtml(r.safe)}</span></td>
        <td><span class="nt-badge ${r.idempotent.startsWith("Oui") ? "nt-badge-info" : "nt-badge-warn"}">${escHtml(r.idempotent)}</span></td>
        <td>${escHtml(r.body)}</td>
        <td><code>${escHtml(r.success)}</code></td>
        <td><code>${escHtml(r.errors)}</code></td>
        <td><code>${escHtml(r.idiom[fw])}</code></td>
      </tr>`
    ).join("");

    const statusCards = STATUS_CATALOG.map(
      (s) => `
      <div class="nt-card">
        <div><span class="nt-badge nt-badge-info">${escHtml(s.code)}</span></div>
        <p>${escHtml(s.role)}</p>
      </div>`
    ).join("");

    return `
      <div class="nt-hero">
        <div class="nt-hero-top">
          <div>
            <span class="nt-badge nt-badge-info">SYNTHÈSE D'INGÉNIERIE — TRILOGIE PYTHON ISGP</span>
            <h1>Synthèse Générale de l'Architecture d'une API Moderne &amp; Conception d'Endpoints</h1>
          </div>
          <div class="nt-filter-bar" style="margin:0;">
            <span style="font-size:12px;font-weight:700;padding:0 6px;">Moteur actif :</span>
            ${["flask", "fastapi", "tornado"]
              .map(
                (k) =>
                  `<button type="button" class="nt-pill-btn ${fw === k ? "active" : ""}" data-bp-fw="${k}">${escHtml(fwLabel(k))}</button>`
              )
              .join("")}
          </div>
        </div>
        <p>
          Ce référentiel consolide l'ensemble du cycle de vie d'une requête HTTP industrielle : de la terminaison
          cryptographique TLS jusqu'à la transaction ACID, la projection DTO sans fuite et l'observabilité distribuée.
          Tous les extraits s'adaptent dynamiquement au framework sélectionné (<strong>${escHtml(fwLabel(fw))}</strong>).
        </p>
        <div class="nt-kpi-strip">
          <div class="nt-kpi-card">
            <div class="nt-kpi-label">Pipeline Architectural</div>
            <div class="nt-kpi-value">5 Couches</div>
            <div class="nt-kpi-sub">Transport TLS, Contrat URI, Validation, ACID, Observabilité</div>
          </div>
          <div class="nt-kpi-card">
            <div class="nt-kpi-label">Sémantique HTTP</div>
            <div class="nt-kpi-value">7 Verbes &amp; 17 Codes</div>
            <div class="nt-kpi-sub">Conformité RFC 9110, RFC 7807 (Problem JSON) &amp; RFC 8594</div>
          </div>
          <div class="nt-kpi-card">
            <div class="nt-kpi-label">Catalogue Comparatif</div>
            <div class="nt-kpi-value">20 Anti-Patterns</div>
            <div class="nt-kpi-sub">Diagnostic précis et implémentation cible Flask / FastAPI / Tornado</div>
          </div>
          <div class="nt-kpi-card">
            <div class="nt-kpi-label">Atelier Temps Réel</div>
            <div class="nt-kpi-value">10 Règles / 100 pts</div>
            <div class="nt-kpi-sub">Linter d'endpoint interactif avec génération de code corrigé</div>
          </div>
        </div>
      </div>

      <div class="nt-section-block">
        <h2 class="nt-section-title">1. Synthèse Générale : Les 5 Piliers d'une API Industrielle</h2>
        <p class="nt-section-lead">
          Qu'elle soit servie par un pool de workers synchrones WSGI (<code>Flask + Gunicorn</code>), un serveur ASGI à typage déclaratif
          (<code>FastAPI + Uvicorn</code>) ou une boucle d'événements non-bloquante (<code>Tornado IOLoop</code>), une API robuste traverse
          invariablement cinq frontières d'ingénierie strictement découplées.
        </p>
        <div class="mermaid-container">
          <pre class="mermaid">flowchart LR
  C["Client Web ou Mobile"] -->|"1. HTTPS TLS 1.3"| G["Couche 1 : Transport et Reverse Proxy"]
  G -->|"Quotas et X-Request-ID"| R["Couche 2 : Routage et Contrat URI v1"]
  R -->|"Verbe HTTP et MIME JSON"| V["Couche 3 : Validation DTO et Métier"]
  V -->|"Requêtes Paramétrées"| D["Couche 4 : Persistance Transactionnelle ACID"]
  D -->|"Projection Liste Blanche"| O["Couche 5 : Cache ETag et Observabilité"]
  O -->|"200 201 204 ou RFC 7807"| C</pre>
        </div>
        <div class="nt-grid-3" style="margin-top:16px;">
          <div class="nt-card">
            <span class="nt-badge nt-badge-info">Couches 1 &amp; 2 — Périmètre &amp; Contrat URI</span>
            <h3>Transport TLS, Quotas &amp; Sémantique REST</h3>
            <p>Nginx absorbe le chiffrement TLS 1.3, plafonne la taille des corps (<code>413</code>) et applique le rate-limiting (<code>429</code>). Le routeur expose des collections nominales pluriel en <code>kebab-case</code> sous <code>/api/v1</code>.</p>
          </div>
          <div class="nt-card">
            <span class="nt-badge nt-badge-success">Couches 3 &amp; 4 — Domaine &amp; Persistance ACID</span>
            <h3>Validation Stricte, Isolation Métier &amp; SQL Sûr</h3>
            <p>Le schéma d'entrée rejette tout type inattendu (<code>422</code>) avant d'atteindre le service métier. La persistance garantit l'atomicité ACID, les paramètres liés <code>?</code> et le verrouillage optimiste <code>If-Match</code> (<code>412</code>).</p>
          </div>
          <div class="nt-card">
            <span class="nt-badge nt-badge-warn">Couche 5 — Sortie, Cache &amp; Télémétrie</span>
            <h3>Projection DTO, ETag &amp; Corrélation</h3>
            <p>Seuls les champs publics autorisés sont sérialisés. Les réponses attachent <code>ETag</code> / <code>Cache-Control</code>, propagent <code>X-Request-ID</code> dans les journaux JSON et alimentent les sondes <code>/health/live</code> et <code>/health/ready</code>.</p>
          </div>
        </div>

        <h3 style="margin:22px 0 8px 0;font-size:16px;">Matrice de Référence des Verbes HTTP &amp; Idiomes (${escHtml(fwLabel(fw))})</h3>
        <div class="nt-table-wrap">
          <table class="nt-table">
            <thead>
              <tr>
                <th>Verbe</th>
                <th>Safe</th>
                <th>Idempotent</th>
                <th>Corps de Requête</th>
                <th>Statuts de Succès</th>
                <th>Statuts d'Erreur</th>
                <th>Idiome Exact — ${escHtml(fwLabel(fw))}</th>
              </tr>
            </thead>
            <tbody>${matrixRows}</tbody>
          </table>
        </div>

        <h3 style="margin:22px 0 10px 0;font-size:16px;">Référentiel Opérationnel des Codes de Statut HTTP</h3>
        <div class="nt-grid-3">${statusCards}</div>
      </div>`;
  }

  function renderPatternsListHtml(fw) {
    const q = BP_STATE.search.trim().toLowerCase();
    const filtered = ENDPOINT_PATTERNS.filter((item) => {
      const catMatch = BP_STATE.category === "Tous" || item.category === BP_STATE.category;
      if (!catMatch) return false;
      if (!q) return true;
      return (
        item.title.toLowerCase().includes(q) ||
        item.rationale.toLowerCase().includes(q) ||
        item.badEndpoint.toLowerCase().includes(q) ||
        item.goodEndpoint.toLowerCase().includes(q)
      );
    });

    if (!filtered.length) {
      return `<div class="nt-card"><p>Aucun patron ne correspond au filtre actuel.</p></div>`;
    }

    return filtered
      .map(
        (p) => `
      <div class="nt-pair-wrapper">
        <div class="nt-pair-header">
          <h3>#${p.id} — ${escHtml(p.title)}</h3>
          <span class="nt-badge nt-badge-info">${escHtml(p.category)}</span>
        </div>
        <p class="nt-pair-rationale">${escHtml(p.rationale)}</p>
        <div class="nt-compare-pair" style="margin-bottom:0;">
          <div class="nt-card-bad">
            <div><span class="nt-badge nt-badge-danger">ANTI-PATTERN À PROSCRIRE</span></div>
            <h4><code>${escHtml(p.badEndpoint)}</code></h4>
            <div class="nt-code-block">
              <div class="nt-code-header"><span>Implémentation défaillante / risquée</span><span>HTTP / Python</span></div>
              <pre><code>${escHtml(p.badCode)}</code></pre>
            </div>
          </div>
          <div class="nt-card-good">
            <div><span class="nt-badge nt-badge-success">ARCHITECTURE CIBLE RECOMMANDÉE</span></div>
            <h4><code>${escHtml(p.goodEndpoint)}</code></h4>
            <div class="nt-code-block">
              <div class="nt-code-header"><span>Implémentation conforme</span><span>${escHtml(fwLabel(fw))}</span></div>
              <pre><code>${escHtml(p.fw[fw])}</code></pre>
            </div>
          </div>
        </div>
      </div>`
      )
      .join("");
  }

  function renderLinterResultHtml(fw) {
    const res = evaluateEndpointDesign(
      BP_STATE.linterMethod,
      BP_STATE.linterUri,
      BP_STATE.linterStatus,
      BP_STATE.linterSample
    );
    const badgeClass =
      res.score >= 90 ? "nt-badge-success" : res.score >= 60 ? "nt-badge-warn" : "nt-badge-danger";
    const verdict =
      res.score === 100
        ? "Contrat d'endpoint exemplaire — prêt pour la production"
        : res.score >= 70
          ? "Contrat acceptable mais perfectible — corrigez les écarts détectés"
          : "Contrat non conforme — anti-patterns structurels critiques détectés";

    const failed = res.rules.filter((r) => !r.passed);
    const rulesRows = res.rules
      .map(
        (r) => `
      <tr>
        <td><span class="nt-badge ${r.passed ? "nt-badge-success" : "nt-badge-danger"}">${r.passed ? "CONFORME (+10)" : "ÉCART (0)"}</span></td>
        <td><strong>Règle ${r.id} — ${escHtml(r.name)}</strong></td>
        <td>${escHtml(r.detail)}</td>
      </tr>`
      )
      .join("");

    return `
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
        <div>
          <span class="nt-badge ${badgeClass}" style="font-size:13px;padding:5px 12px;">SCORE DE CONFORMITÉ : ${res.score} / 100</span>
          <strong style="margin-left:10px;font-size:14px;">${escHtml(verdict)}</strong>
        </div>
        <span class="nt-badge nt-badge-info">${failed.length} anti-pattern(s) détecté(s) sur 10 règles</span>
      </div>
      <div class="nt-progress-bar">
        <div class="nt-progress-fill" style="width:${res.score}%;"></div>
      </div>
      <div class="nt-table-wrap" style="margin-bottom:16px;">
        <table class="nt-table">
          <thead><tr><th>Diagnostic</th><th>Règle d'Ingénierie Évaluée</th><th>Analyse Détaillée</th></tr></thead>
          <tbody>${rulesRows}</tbody>
        </table>
      </div>
      <div class="nt-card-good">
        <div><span class="nt-badge nt-badge-success">PROPOSITION D'ENDPOINT CORRIGÉ &amp; HANDLER (${escHtml(fwLabel(fw))})</span></div>
        <h4><code>${escHtml(res.corrected.method)} ${escHtml(res.corrected.uri)}  ->  HTTP ${res.corrected.status}</code></h4>
        <div class="nt-code-block">
          <div class="nt-code-header"><span>Squelette serveur conforme généré</span><span>${escHtml(fwLabel(fw))}</span></div>
          <pre><code>${escHtml(res.corrected.code[fw])}</code></pre>
        </div>
      </div>`;
  }

  function renderFullTab(rootEl) {
    const fw = detectFramework();
    const presetOptions = Object.entries(LINTER_PRESETS)
      .map(
        ([k, v]) =>
          `<option value="${escHtml(k)}" ${BP_STATE.presetKey === k ? "selected" : ""}>${escHtml(v.label)}</option>`
      )
      .join("");

    const catButtons = BP_CATEGORIES.map((cat) => {
      const count =
        cat === "Tous"
          ? ENDPOINT_PATTERNS.length
          : ENDPOINT_PATTERNS.filter((p) => p.category === cat).length;
      return `<button type="button" class="nt-pill-btn ${BP_STATE.category === cat ? "active" : ""}" data-bp-cat="${escHtml(cat)}">${escHtml(cat)} (${count})</button>`;
    }).join("");

    rootEl.innerHTML = `
      ${renderSynthesisSection(fw)}

      <div class="nt-section-block">
        <h2 class="nt-section-title">2. Guide Complet : Concevoir le Bon Endpoint (20 Anti-Patterns vs Architecture Cible)</h2>
        <p class="nt-section-lead">
          Filtrez par domaine d'architecture ou recherchez un mot-clé (<code>ETag</code>, <code>Idempotency-Key</code>, <code>RFC 7807</code>, <code>pagination</code>)
          pour comparer chaque erreur classique avec son implémentation de référence en <strong>${escHtml(fwLabel(fw))}</strong>.
        </p>
        <div class="nt-filter-bar" id="bp-cat-bar">
          ${catButtons}
          <input type="search" id="bp-search-input" class="nt-input" style="max-width:260px;margin-left:auto;" placeholder="Filtrer les 20 patrons..." value="${escHtml(BP_STATE.search)}" />
        </div>
        <div id="bp-patterns-container">${renderPatternsListHtml(fw)}</div>
      </div>

      <div class="nt-section-block">
        <h2 class="nt-section-title">3. Atelier Interactif — Auditeur &amp; Linter d'Endpoint (Temps Réel)</h2>
        <p class="nt-section-lead">
          Chargez l'un des 8 scénarios préconfigurés (5 anti-patterns réels et 3 contrats exemplaires) ou saisissez librement votre propre endpoint :
          le moteur vérifie instantanément 10 règles REST/HTTP, calcule un score sur 100 et génère le code cible en <strong>${escHtml(fwLabel(fw))}</strong>.
        </p>
        <div class="nt-sim-box">
          <div class="nt-form-row">
            <div class="nt-field-group" style="grid-column: 1 / -1;">
              <label for="bp-preset-select">Scénarios d'audit préconfigurés (5 mauvais endpoints + 3 bons endpoints)</label>
              <select id="bp-preset-select" class="nt-select">${presetOptions}</select>
            </div>
          </div>
          <div class="nt-form-row">
            <div class="nt-field-group">
              <label for="bp-method-select">Méthode HTTP (method)</label>
              <select id="bp-method-select" class="nt-select">
                ${["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
                  .map((m) => `<option value="${m}" ${BP_STATE.linterMethod === m ? "selected" : ""}>${m}</option>`)
                  .join("")}
              </select>
            </div>
            <div class="nt-field-group" style="grid-column: span 2;">
              <label for="bp-uri-input">Chemin &amp; Query String (uri)</label>
              <input type="text" id="bp-uri-input" class="nt-input" value="${escHtml(BP_STATE.linterUri)}" />
            </div>
            <div class="nt-field-group">
              <label for="bp-status-input">Code Statut HTTP (status_code)</label>
              <input type="number" id="bp-status-input" class="nt-input" min="100" max="599" value="${escHtml(BP_STATE.linterStatus)}" />
            </div>
          </div>
          <div class="nt-field-group">
            <label for="bp-sample-input">Échantillon de corps JSON renvoyé (response_sample)</label>
            <textarea id="bp-sample-input" class="nt-input">${escHtml(BP_STATE.linterSample)}</textarea>
          </div>
          <div id="bp-linter-result" class="nt-result-panel">${renderLinterResultHtml(fw)}</div>
        </div>
      </div>`;

    bindEvents(rootEl);
    if (typeof renderMermaidDiagrams === "function") {
      renderMermaidDiagrams(rootEl);
    }
  }

  function bindEvents(rootEl) {
    rootEl.querySelectorAll("[data-bp-fw]").forEach((btn) => {
      btn.addEventListener("click", () => {
        BP_STATE.fwOverride = btn.getAttribute("data-bp-fw");
        renderFullTab(rootEl);
      });
    });

    rootEl.querySelectorAll("[data-bp-cat]").forEach((btn) => {
      btn.addEventListener("click", () => {
        BP_STATE.category = btn.getAttribute("data-bp-cat");
        rootEl.querySelectorAll("[data-bp-cat]").forEach((b) => {
          b.classList.toggle("active", b.getAttribute("data-bp-cat") === BP_STATE.category);
        });
        const container = rootEl.querySelector("#bp-patterns-container");
        if (container) container.innerHTML = renderPatternsListHtml(detectFramework());
      });
    });

    const searchInput = rootEl.querySelector("#bp-search-input");
    if (searchInput) {
      searchInput.addEventListener("input", () => {
        BP_STATE.search = searchInput.value;
        const container = rootEl.querySelector("#bp-patterns-container");
        if (container) container.innerHTML = renderPatternsListHtml(detectFramework());
      });
    }

    const presetSel = rootEl.querySelector("#bp-preset-select");
    const methodSel = rootEl.querySelector("#bp-method-select");
    const uriInp = rootEl.querySelector("#bp-uri-input");
    const statusInp = rootEl.querySelector("#bp-status-input");
    const sampleInp = rootEl.querySelector("#bp-sample-input");
    const resultPanel = rootEl.querySelector("#bp-linter-result");

    const refreshLinter = () => {
      BP_STATE.linterMethod = methodSel ? methodSel.value : BP_STATE.linterMethod;
      BP_STATE.linterUri = uriInp ? uriInp.value : BP_STATE.linterUri;
      BP_STATE.linterStatus = statusInp ? statusInp.value : BP_STATE.linterStatus;
      BP_STATE.linterSample = sampleInp ? sampleInp.value : BP_STATE.linterSample;
      if (resultPanel) resultPanel.innerHTML = renderLinterResultHtml(detectFramework());
    };

    if (presetSel) {
      presetSel.addEventListener("change", () => {
        const key = presetSel.value;
        const p = LINTER_PRESETS[key];
        if (!p) return;
        BP_STATE.presetKey = key;
        BP_STATE.linterMethod = p.method;
        BP_STATE.linterUri = p.uri;
        BP_STATE.linterStatus = p.status;
        BP_STATE.linterSample = p.sample;
        if (methodSel) methodSel.value = p.method;
        if (uriInp) uriInp.value = p.uri;
        if (statusInp) statusInp.value = p.status;
        if (sampleInp) sampleInp.value = p.sample;
        if (resultPanel) resultPanel.innerHTML = renderLinterResultHtml(detectFramework());
      });
    }

    [methodSel, uriInp, statusInp, sampleInp].forEach((el) => {
      if (!el) return;
      el.addEventListener("input", refreshLinter);
      el.addEventListener("change", refreshLinter);
    });
  }

  let lastObservedGlobalFw = null;

  window.loadBestPracticesTab = function () {
    const rootEl = document.getElementById("bestpractices-tab-root");
    if (!rootEl) return;
    const globalFw = (
      window.ACTIVE_FRAMEWORK ||
      (typeof STATE !== "undefined" ? STATE?.framework : "") ||
      "flask"
    )
      .toString()
      .toLowerCase();
    if (globalFw !== lastObservedGlobalFw) {
      lastObservedGlobalFw = globalFw;
      BP_STATE.fwOverride = null;
    }
    renderFullTab(rootEl);
  };
})();
