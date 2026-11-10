// ============================================================================
// ISGP — Couche d'Autonomie Statique pour GitHub Pages (Zéro Serveur Python)
// S'active UNIQUEMENT lorsque window.ISGP_GH_PAGES === true.
// En exécution locale (.venv/bin/python app.py), ce fichier n'est pas chargé.
// ============================================================================
(function () {
  if (!window.ISGP_GH_PAGES) return;

  const SITE_ROOT = new URL(window.ISGP_REL_ROOT || "./", window.location.href).href.replace(/\/$/, "");
  const origFetch = window.fetch.bind(window);

  // Réécriture du chemin du Service Worker (/sw.js -> <SITE_ROOT>/sw.js) pour le mode PWA hors-ligne sous GitHub Pages
  if ("serviceWorker" in navigator) {
    const origRegister = navigator.serviceWorker.register.bind(navigator.serviceWorker);
    navigator.serviceWorker.register = function (scriptUrl, opts) {
      if (typeof scriptUrl === "string" && (scriptUrl === "/sw.js" || scriptUrl.endsWith("/sw.js"))) {
        return origRegister(`${SITE_ROOT}/sw.js`, Object.assign({ scope: `${SITE_ROOT}/` }, opts || {}));
      }
      return origRegister(scriptUrl, opts);
    };
  }

  // Réécriture automatique des liens dynamiques injectés par app.js (téléchargements .py, Swagger, Jinja2)
  function rewriteHref(href) {
    if (!href || !href.startsWith("/")) return href;
    if (href === "/") return SITE_ROOT + "/index.html";
    if (href.startsWith("/cours/")) {
      const fw = href.split("/")[2]?.split("?")[0] || "flask";
      return `${SITE_ROOT}/cours/${fw}/index.html`;
    }
    if (href === "/api/docs") return `${SITE_ROOT}/api/docs/index.html`;
    if (href === "/api/openapi.json") return `${SITE_ROOT}/api/openapi.json`;
    if (href === "/sandbox/formulaire-jinja") return `${SITE_ROOT}/sandbox/formulaire-jinja/index.html`;
    if (href.startsWith("/api/download/openapi-spec")) return `${SITE_ROOT}/downloads/isgp_api_bootcamp.openapi.json`;
    if (href.startsWith("/api/download/postman-collection")) return `${SITE_ROOT}/downloads/isgp_postman_collection.json`;
    if (href.startsWith("/api/download/http-requests")) return `${SITE_ROOT}/downloads/isgp_requetes.http`;
    const mDay = href.match(/^\/api\/day-file\/(\d+)\/([^?]+)(?:\?(.*))?$/);
    if (mDay) {
      const params = new URLSearchParams(mDay[3] || "");
      const fw = params.get("framework") || window.ACTIVE_FRAMEWORK || "flask";
      return `${SITE_ROOT}/files/${fw}/day_${mDay[1]}/${decodeURIComponent(mDay[2])}`;
    }
    const mRef = href.match(/^\/api\/reference-file\/([^?]+)(?:\?(.*))?$/);
    if (mRef) {
      const params = new URLSearchParams(mRef[2] || "");
      const fw = params.get("framework") || window.ACTIVE_FRAMEWORK || "flask";
      return `${SITE_ROOT}/files/${fw}/ref/${decodeURIComponent(mRef[1])}`;
    }
    return href;
  }

  function patchAnchors(root) {
    (root || document).querySelectorAll("a[href^='/']").forEach((a) => {
      const raw = a.getAttribute("href");
      const next = rewriteHref(raw);
      if (next !== raw) a.setAttribute("href", next);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    patchAnchors(document);
    const obs = new MutationObserver((mutations) => {
      for (const m of mutations) {
        m.addedNodes.forEach((n) => {
          if (n.nodeType === 1) {
            if (n.tagName === "A") patchAnchors(n.parentElement || document);
            else patchAnchors(n);
          }
        });
      }
    });
    obs.observe(document.body, { childList: true, subtree: true });
  });

  // ==========================================================================
  // ÉTATS EN MÉMOIRE POUR LES SIMULATEURS INTERACTIFS CÔTÉ NAVIGATEUR
  // ==========================================================================
  function defaultFormations() {
    return [
      { id: 1, titre: "Architecture API REST & Micro-Frameworks", formateur: "Dr. Karim Benali", duree_jours: 5, salle: "Salle A" },
      { id: 2, titre: "Sécurité OAuth2, JWT, HMAC & Rate Limiting", formateur: "Mme. Nadia Mansouri", duree_jours: 4, salle: "Salle Cybersécurité" },
      { id: 3, titre: "Persistance SQLite WAL, Curseurs & PostgreSQL", formateur: "M. Yacine Toumi", duree_jours: 3, salle: "Labo Données" },
      { id: 4, titre: "Déploiement Nginx, Streaming & Cache ETag", formateur: "Dr. Amine Rahmani", duree_jours: 5, salle: "Amphithéâtre Alger" }
    ];
  }

  let sandboxFormations = defaultFormations();
  let sandboxNextId = 5;
  let rateLimitRemaining = 5;
  let issuedTokens = {};

  let sqliteRows = defaultFormations();
  let sqliteNextId = 5;
  const sqliteStateCache = {};
  const nginxStateCache = {};
  const advStateCache = {};

  let advCatalogue = {
    id: 1,
    titre: "Architecture Critique & Haute Disponibilité ISGP",
    version_metier: 1,
    salle: "Amphithéâtre Alger",
    places: 40,
    derniere_modification: "Initialisation système (GitHub Pages)"
  };
  let advJobs = [];

  function simpleHashHex(str) {
    let h1 = 0xdeadbeef ^ str.length;
    let h2 = 0x41c6ce57 ^ str.length;
    for (let i = 0; i < str.length; i++) {
      const ch = str.charCodeAt(i);
      h1 = Math.imul(h1 ^ ch, 2654435761);
      h2 = Math.imul(h2 ^ ch, 1597334677);
    }
    h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
    h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
    return ((h2 >>> 0).toString(16).padStart(8, "0") + (h1 >>> 0).toString(16).padStart(8, "0")).slice(0, 16);
  }

  function computeEtag(doc) {
    return `"${simpleHashHex(JSON.stringify(doc))}"`;
  }

  function jsonResponse(payload, status = 200, extraHeaders = {}) {
    const statusTexts = {
      200: "OK",
      201: "Created",
      202: "Accepted",
      204: "No Content",
      304: "Not Modified",
      400: "Bad Request",
      401: "Unauthorized",
      403: "Forbidden",
      404: "Not Found",
      412: "Precondition Failed",
      413: "Content Too Large",
      415: "Unsupported Media Type",
      422: "Unprocessable Entity",
      428: "Precondition Required",
      429: "Too Many Requests",
      502: "Bad Gateway"
    };
    const headers = new Headers({
      "Content-Type": "application/json",
      ...extraHeaders
    });
    return new Response(status === 204 || status === 304 ? null : JSON.stringify(payload), {
      status,
      statusText: statusTexts[status] || "OK",
      headers
    });
  }

  function tracedResponse(payload, status, handlerCode, steps, extraHeaders = {}) {
    return jsonResponse(payload, status, {
      "X-Flask-Handler-Code": JSON.stringify(handlerCode),
      "X-Flask-Trace-Steps": JSON.stringify(steps),
      ...extraHeaders
    });
  }

  // ==========================================================================
  // POLYFILL EVENTSOURCE POUR LE FLUX SSE EN MODE GITHUB PAGES STATIQUE
  // ==========================================================================
  const NativeEventSource = window.EventSource;
  window.EventSource = function (url, opts) {
    if (typeof url === "string" && url.includes("/api/advanced-lab/sse-demo")) {
      const u = new URL(url, window.location.origin);
      const fw = u.searchParams.get("framework") || window.ACTIVE_FRAMEWORK || "flask";
      const fwMech = {
        flask: "Flask Response(stream_with_context(yield))",
        fastapi: "FastAPI StreamingResponse(async generator)",
        tornado: "Tornado RequestHandler + await self.flush()"
      }[fw] || "SSE Stream";
      const listeners = {};
      let timer = null;
      let idx = 0;
      const etapes = [
        "Connexion HTTP persistante ouverte (Content-Type: text/event-stream)",
        "Collecte des métriques CPU / Latence SQLite WAL...",
        "Vérification des quotas Rate-Limiter par fenêtre glissante...",
        "Synchronisation du cache ETag des 4 nœuds upstream...",
        "Flux temps réel terminé proprement (reconnexion auto via Last-Event-ID si coupure)."
      ];
      const fakeEs = {
        addEventListener(type, cb) {
          listeners[type] = listeners[type] || [];
          listeners[type].push(cb);
        },
        close() {
          if (timer) clearInterval(timer);
          timer = null;
        }
      };
      timer = setInterval(() => {
        idx += 1;
        if (idx > etapes.length) {
          fakeEs.close();
          return;
        }
        const now = new Date().toTimeString().split(" ")[0] + "." + String(Date.now() % 1000).padStart(3, "0");
        const evObj = {
          lastEventId: `sse-${idx}`,
          data: JSON.stringify({
            id_trame: idx,
            moteur: fwMech,
            message: etapes[idx - 1],
            horodatage: now
          })
        };
        (listeners["telemetry"] || []).forEach((fn) => fn(evObj));
      }, 360);
      return fakeEs;
    }
    return new NativeEventSource(url, opts);
  };

  // ==========================================================================
  // INTERCEPTEUR UNIVERSEL FETCH POUR TOUTES LES ROUTES /api/* EN STATIQUE
  // ==========================================================================
  window.fetch = async function (input, init = {}) {
    const rawUrl = typeof input === "string" ? input : input.url;
    const parsed = new URL(rawUrl, window.location.origin);
    const path = parsed.pathname;
    const method = (init.method || (typeof input !== "string" && input.method) || "GET").toUpperCase();

    if (!path.startsWith("/api/")) {
      return origFetch(input, init);
    }

    const reqHeaders = new Headers(init.headers || {});
    const fw = parsed.searchParams.get("framework") || reqHeaders.get("X-Active-Framework") || window.ACTIVE_FRAMEWORK || "flask";
    let bodyObj = {};
    if (init.body && typeof init.body === "string") {
      try {
        bodyObj = JSON.parse(init.body);
      } catch (e) {
        const sp = new URLSearchParams(init.body);
        sp.forEach((v, k) => {
          bodyObj[k] = v;
        });
      }
    }

    // 1. Données complètes du cours (30 leçons, 57 fiches glossaire, 53 questions quiz)
    if (path === "/api/course-data") {
      return origFetch(`${SITE_ROOT}/static-data/${fw}/course-data.json`);
    }

    // 2. Contrat OpenAPI
    if (path === "/api/openapi.json") {
      return origFetch(`${SITE_ROOT}/api/openapi.json`);
    }

    // 3. Chargement des fichiers .py dans l'Atelier Python
    const mDay = path.match(/^\/api\/day-file\/(\d+)\/(.+)$/);
    if (mDay) {
      const dayNum = mDay[1];
      const fname = decodeURIComponent(mDay[2]);
      const r = await origFetch(`${SITE_ROOT}/files/${fw}/day_${dayNum}/${fname}`);
      const code = await r.text();
      return jsonResponse({ path: `${fw}-version/day_${dayNum}/${fname}`, code });
    }
    const mRef = path.match(/^\/api\/reference-file\/(.+)$/);
    if (mRef) {
      const fname = decodeURIComponent(mRef[1]);
      const r = await origFetch(`${SITE_ROOT}/files/${fw}/ref/${fname}`);
      const code = await r.text();
      return jsonResponse({ framework: fw, path: `${fw}-version/${fname}`, code });
    }

    // 4. Simulateur Cluster Nginx (4 nœuds + Offload $request_body_file + 413 + X-Accel-Redirect)
    if (path.startsWith("/api/nginx-cluster/")) {
      if (!nginxStateCache[fw]) {
        const r = await origFetch(`${SITE_ROOT}/static-data/${fw}/nginx-state.json`);
        nginxStateCache[fw] = await r.json();
      }
      const bundle = nginxStateCache[fw];
      const st = bundle.state;
      const nowStr = new Date().toTimeString().split(" ")[0];
      const fwLabel = { flask: "Flask/Gunicorn", fastapi: "FastAPI/Uvicorn", tornado: "Tornado HTTPServer" }[fw] || fw;

      if (path.endsWith("/state")) {
        return jsonResponse(bundle);
      }
      if (path.endsWith("/toggle-node")) {
        const port = Number(bodyObj.port || 0);
        st.nodes.forEach((n) => {
          if (n.port === port) {
            n.status = n.status === "UP" ? "DOWN" : "UP";
            st.logs.unshift(
              `[${nowStr}] [NGINX HEALTHCHECK] Instance ${n.id} (${n.addr}) marquée ${n.status} ` +
                (n.status === "DOWN"
                  ? "(max_fails=3 atteint -> trafic basculé automatiquement)"
                  : "(réintégrée dans le pool upstream)")
            );
          }
        });
        st.logs = st.logs.slice(0, 35);
        return jsonResponse({ state: st });
      }
      if (path.endsWith("/reset")) {
        st.rr_index = 0;
        st.static_requests_served = 0;
        st.dynamic_requests_proxied = 0;
        st.uploads_offloaded = 0;
        st.rejected_413_edge = 0;
        st.x_accel_downloads = 0;
        st.errors_502 = 0;
        st.nodes.forEach((n, idx) => {
          n.status = "UP";
          n.requests = 0;
          n.active_conns = idx % 2;
        });
        st.logs = [`[${nowStr}] [RESET] Compteurs remis à zéro et les 4 instances ${fwLabel} (:8001..8004) sont UP.`];
        return jsonResponse({ state: st });
      }
      if (path.endsWith("/simulate")) {
        const reqType = bodyObj.type || "dynamic";
        const count = Math.min(20, Math.max(1, Number(bodyObj.count || 1)));
        const algo = bodyObj.algorithm || st.algorithm || "round_robin";
        const clientIp = bodyObj.client_ip || "197.204.12.88";
        st.algorithm = algo;
        for (let i = 0; i < count; i++) {
          if (reqType === "static") {
            const p = i % 2 === 0 ? "/static/styles.css" : "/static/app.js";
            st.static_requests_served += 1;
            st.logs.unshift(`${clientIp} - [${nowStr}] "GET ${p} HTTP/1.1" status=200 served_by=Nginx-Direct-Static-Sendfile (0 instance ${fwLabel} sollicitée) total_time=0.0004s`);
          } else if (reqType === "upload_413") {
            st.rejected_413_edge = (st.rejected_413_edge || 0) + 1;
            st.logs.unshift(`${clientIp} - [${nowStr}] "POST /api/v1/upload-offload HTTP/1.1 (Content-Length: 62914560)" status=413 edge_shield="client_max_body_size 25M exceeded" (0 octet transmis à ${fwLabel} !) total_time=0.0001s`);
          } else {
            const upNodes = st.nodes.filter((n) => n.status === "UP");
            const routePath = reqType === "upload_offload" ? "/api/v1/upload-offload" : reqType === "x_accel" ? "/api/v1/exports/certificat_2026" : "/api/v1/formations";
            if (!upNodes.length) {
              st.errors_502 += 1;
              st.logs.unshift(`${clientIp} - [${nowStr}] "GET ${routePath} HTTP/1.1" status=502 error="no live upstreams while connecting to upstream isgp_${fw}_cluster"`);
              continue;
            }
            let chosen = upNodes[st.rr_index % upNodes.length];
            if (algo === "least_conn") {
              chosen = upNodes.reduce((a, b) => (a.active_conns <= b.active_conns ? a : b));
              chosen.active_conns = (chosen.active_conns + 1) % 4;
            } else if (algo === "ip_hash") {
              const sum = Array.from(clientIp).reduce((acc, c) => acc + c.charCodeAt(0), 0);
              chosen = upNodes[sum % upNodes.length];
            } else if (algo === "weighted") {
              const pool = [];
              upNodes.forEach((n) => {
                for (let w = 0; w < (n.weight || 1); w++) pool.push(n);
              });
              chosen = pool[st.rr_index % pool.length];
              st.rr_index += 1;
            } else {
              st.rr_index += 1;
            }
            chosen.requests += 1;
            st.dynamic_requests_proxied += 1;
            if (reqType === "upload_offload") {
              st.uploads_offloaded = (st.uploads_offloaded || 0) + 1;
              st.logs.unshift(`${clientIp} - [${nowStr}] "POST ${routePath} HTTP/1.1 (18 Mo Mobile 4G absorbés par Nginx C)" status=201 spool=/var/spool/isgp_nginx_uploads/${1000 + st.uploads_offloaded} body_sent_to_python=0B upstream_node=${chosen.addr} (${chosen.id}) upstream_time=0.0009s`);
            } else if (reqType === "x_accel") {
              st.x_accel_downloads = (st.x_accel_downloads || 0) + 1;
              st.logs.unshift(`${clientIp} - [${nowStr}] "GET ${routePath} HTTP/1.1" status=200 auth_by=${chosen.addr} (0.0006s) -> X-Accel-Redirect=/_protected_exports/certificat_2026.pdf (18 Mo streamés par Nginx sendfile internal !)`);
            } else {
              st.logs.unshift(`${clientIp} - [${nowStr}] "GET ${routePath} HTTP/1.1" status=200 upstream_node=${chosen.addr} (${chosen.id}, PID ${chosen.pid}) upstream_time=0.008s`);
            }
          }
        }
        st.logs = st.logs.slice(0, 35);
        return jsonResponse({ state: st });
      }
    }

    // 5. Laboratoire SQLite3 & Anti-SQLi
    if (path.startsWith("/api/sqlite-lab/")) {
      if (!sqliteStateCache[fw]) {
        const r = await origFetch(`${SITE_ROOT}/static-data/${fw}/sqlite-state.json`);
        sqliteStateCache[fw] = await r.json();
      }
      const base = sqliteStateCache[fw];
      if (path.endsWith("/state")) {
        return jsonResponse({ ...base, rows: sqliteRows });
      }
      const act = bodyObj.action || "compare";
      if (act === "compare") {
        const salle = String(bodyObj.salle ?? "Salle A");
        const inj = salle.includes("'") || /or\s+1\s*=\s*1/i.test(salle);
        const safeRows = sqliteRows.filter((r) => r.salle === salle);
        const unsafeRows = inj ? sqliteRows : safeRows;
        return jsonResponse({
          safe_sql: "SELECT id, titre, formateur, duree_jours, salle FROM formations WHERE salle = ? ORDER BY id ASC",
          bound_params: [salle],
          safe_rows: safeRows,
          unsafe_sql: `SELECT id, titre, formateur, duree_jours, salle FROM formations WHERE salle = '${salle}' ORDER BY id ASC`,
          unsafe_rows: unsafeRows,
          unsafe_error: null,
          injection_detected: inj,
          rows: sqliteRows,
          handler_snippet: base.handler_snippet
        });
      }
      if (act === "find_one") {
        const id = Number(bodyObj.id || 1);
        const row = sqliteRows.find((r) => r.id === id) || null;
        return jsonResponse({
          found: Boolean(row),
          row,
          sql_executed: "SELECT id, titre, formateur, duree_jours, salle FROM formations WHERE id = ?",
          explanation: row
            ? `fetchone() a trouvé la formation #${id} via l'index primaire en liant le tuple à 1 élément (${id},).`
            : `fetchone() a renvoyé None -> l'API retourne proprement HTTP 404 Not Found.`,
          handler_snippet: base.handler_snippet
        });
      }
      if (act === "insert_named") {
        const item = {
          id: sqliteNextId++,
          titre: bodyObj.titre || "Nouvelle Formation SQLite",
          formateur: bodyObj.formateur || "Intervenant ISGP",
          duree_jours: Number(bodyObj.duree_jours || 4),
          salle: bodyObj.salle || "Salle A"
        };
        sqliteRows.push(item);
        return jsonResponse({
          lastrowid: item.id,
          sql_executed: "INSERT INTO formations (titre, formateur, duree_jours, salle) VALUES (:titre, :formateur, :duree_jours, :salle)",
          bound_params: item,
          explanation: `Insertion paramétrée validée par COMMIT atomique (cur.lastrowid = ${item.id}).`,
          rows: sqliteRows,
          handler_snippet: base.handler_snippet
        });
      }
      if (act === "rollback_demo") {
        return jsonResponse({
          sql_executed: "BEGIN IMMEDIATE;\nINSERT INTO formations (...) VALUES (...);\n-- Violation CHECK (duree_jours = -5 <= 0) !\nROLLBACK; -- Table intégralement préservée !",
          explanation: "Atomicité ACID démontrée : l'exception IntegrityError déclenche automatiquement ROLLBACK à la sortie du bloc 'with conn:'."
        });
      }
    }

    // 6. Laboratoire Avancé : Temps Réel, Multipart, Tâches 202 & Cache ETag
    if (path.startsWith("/api/advanced-lab/")) {
      if (!advStateCache[fw]) {
        const r = await origFetch(`${SITE_ROOT}/static-data/${fw}/advanced-state.json`);
        advStateCache[fw] = await r.json();
      }
      const base = advStateCache[fw];
      if (path.endsWith("/state")) {
        return jsonResponse({
          ...base,
          etag: computeEtag(advCatalogue),
          resource: { ...advCatalogue },
          jobs: advJobs
        });
      }
      if (path.endsWith("/multipart-inspect")) {
        const scen = bodyObj.scenario || "valid_pdf";
        const boundary = "----ISGPFormBoundary9f8e7d6c5b";
        let rawName = "support_architecture_api_2026.pdf";
        let hexHead = "25 50 44 46 2D 31 2E 37";
        let simSize = 128500;
        let code = 201;
        let verdict = "ACCEPTÉ — HTTP 201 Created. Signature binaire %PDF- authentique vérifiée en streaming.";
        if (scen === "traversal_pdf") {
          rawName = "../../../etc/cron.d/backdoor_cours.pdf";
          simSize = 48200;
          verdict = "ACCEPTÉ — HTTP 201 Created. Attaque Path Traversal neutralisée ('../../../etc/cron.d/backdoor_cours.pdf' -> nom plat UUID).";
        } else if (scen === "spoofed_exe") {
          rawName = "facture_fournisseur.pdf";
          hexHead = "4D 5A 90 00 03 00 00 00";
          simSize = 112400;
          code = 415;
          verdict = "REJETÉ — HTTP 415 Unsupported Media Type ! Le client déclare 'application/pdf', mais les Magic Bytes réels [4D 5A] correspondent à un exécutable Windows 'MZ' !";
        } else if (scen === "oversized") {
          rawName = "archive_complete_4k.pdf";
          simSize = 15 * 1024 * 1024;
          code = 413;
          verdict = "REJETÉ — HTTP 413 Content Too Large (15 Mo > plafond autorisé de 2 Mo).";
        }
        const cleanBase = rawName.split("/").pop().replace(/[^a-zA-Z0-9._-]/g, "_") || "document.pdf";
        const sanitized = `${simpleHashHex(String(Date.now())).slice(0, 8)}_${cleanBase}`;
        const wire =
          `POST /api/lab/upload HTTP/1.1\r\nHost: api.isgp.dz\r\nContent-Length: ${simSize}\r\n` +
          `Content-Type: multipart/form-data; boundary=${boundary}\r\n\r\n--${boundary}\r\n` +
          `Content-Disposition: form-data; name="document"; filename="${rawName}"\r\nContent-Type: application/pdf\r\n\r\n` +
          `<FLUX BINAIRE BRUT : Magic Bytes Hex = [${hexHead}]>\r\n--${boundary}--\r\n`;
        return jsonResponse({
          scenario: scen,
          http_status: code,
          verdict,
          raw_filename: rawName,
          sanitized_filename: sanitized,
          claimed_mime: "application/pdf",
          magic_bytes_hex: hexHead,
          size_bytes: simSize,
          wire_frame: wire
        });
      }
      if (path.endsWith("/jobs")) {
        if (method === "GET") return jsonResponse({ jobs: advJobs });
        const jobId = "job-" + simpleHashHex(String(Date.now())).slice(0, 8);
        const reqId = "req-" + simpleHashHex(jobId).slice(0, 8);
        const engine = {
          flask: "ThreadPoolExecutor (Worker WSGI)",
          fastapi: "BackgroundTasks (ASGI Post-Response)",
          tornado: "IOLoop.current().spawn_callback()"
        }[fw] || "Background Worker";
        const entry = {
          job_id: jobId,
          sujet: bodyObj.sujet || "Export PDF Certificats Promotion 2026",
          moteur: engine,
          request_id: reqId,
          statut: "PENDING (0%)",
          progression: 0,
          resultat: null
        };
        advJobs.unshift(entry);
        advJobs = advJobs.slice(0, 8);
        setTimeout(() => { entry.progression = 35; entry.statut = "RUNNING — Requête SQLite par lots (35%)"; }, 650);
        setTimeout(() => { entry.progression = 75; entry.statut = "RUNNING — Signature PDF SHA-256 (75%)"; }, 1350);
        setTimeout(() => { entry.progression = 100; entry.statut = "COMPLETED (100%)"; entry.resultat = `/downloads/${jobId}.pdf (184 Ko)`; }, 2050);
        return jsonResponse({
          http_status: 202,
          location: `/api/advanced-lab/jobs/${jobId}`,
          request_id: reqId,
          job: entry
        }, 202);
      }
      if (path.endsWith("/etag")) {
        const mode = bodyObj.mode || "get_fresh";
        const reqId = "req-" + simpleHashHex(String(Date.now())).slice(0, 10);
        const curEtag = computeEtag(advCatalogue);
        const bodyBytes = new TextEncoder().encode(JSON.stringify(advCatalogue)).length;
        if (mode === "get_fresh") {
          return jsonResponse({
            http_status: 200,
            status_text: "200 OK (Payload complet transféré + ETag émis)",
            request_headers: { Accept: "application/json", "X-Request-ID": reqId },
            response_headers: { ETag: curEtag, "Cache-Control": "private, max-age=30, must-revalidate", "X-Request-ID": reqId, "X-Process-Time-Ms": "0.45" },
            bytes_transferred: bodyBytes,
            etag: curEtag,
            resource: { ...advCatalogue },
            explanation: `1er appel GET : toute la ressource (${bodyBytes} octets) est sérialisée avec ETag: ${curEtag}.`
          });
        }
        if (mode === "get_conditional") {
          const inm = (bodyObj.if_none_match || "").trim();
          if (inm === curEtag) {
            return jsonResponse({
              http_status: 304,
              status_text: "304 Not Modified (Zéro octet de corps transféré !)",
              request_headers: { "If-None-Match": inm, "X-Request-ID": reqId },
              response_headers: { ETag: curEtag, "Cache-Control": "private, max-age=30, must-revalidate", "X-Request-ID": reqId, "X-Process-Time-Ms": "0.12" },
              bytes_transferred: 0,
              etag: curEtag,
              resource: { ...advCatalogue },
              explanation: `If-None-Match (${inm}) == ETag serveur (${curEtag}) -> HTTP 304 avec 0 octet de corps JSON !`
            });
          }
          return jsonResponse({
            http_status: 200,
            status_text: "200 OK (Cache client obsolète -> Nouveau payload)",
            request_headers: { "If-None-Match": inm || "(absent)", "X-Request-ID": reqId },
            response_headers: { ETag: curEtag, "X-Request-ID": reqId },
            bytes_transferred: bodyBytes,
            etag: curEtag,
            resource: { ...advCatalogue },
            explanation: `ETag client différent de ${curEtag} -> renvoi de la nouvelle représentation (${bodyBytes} octets).`
          });
        }
        if (mode === "simulate_concurrent_writer") {
          advCatalogue.places = Math.max(10, (advCatalogue.places + 5) % 90);
          advCatalogue.version_metier += 1;
          advCatalogue.derniere_modification = "Modifié par Collègue B à " + new Date().toTimeString().split(" ")[0];
          const newEtag = computeEtag(advCatalogue);
          return jsonResponse({
            http_status: 200,
            status_text: "Modification concurrente effectuée par Collègue B",
            etag: newEtag,
            resource: { ...advCatalogue },
            explanation: `Collègue B a modifié la fiche ! L'ETag serveur est passé de ${curEtag} à ${newEtag}. Un PUT avec votre ancien ETag renverra 412 !`
          });
        }
        const ifMatch = (bodyObj.if_match || "").trim();
        if (!ifMatch) {
          return jsonResponse({
            http_status: 428,
            status_text: "428 Precondition Required (If-Match manquant)",
            etag: curEtag,
            resource: { ...advCatalogue },
            bytes_transferred: 96,
            explanation: "En-tête If-Match obligatoire pour modifier cette ressource."
          });
        }
        if (ifMatch !== curEtag) {
          return jsonResponse({
            http_status: 412,
            status_text: "412 Precondition Failed — ÉCRASEMENT CONCURRENT (LOST UPDATE) ÉVITÉ !",
            request_headers: { "If-Match": ifMatch, "X-Request-ID": reqId },
            response_headers: { ETag: curEtag, "X-Request-ID": reqId },
            bytes_transferred: 164,
            etag: curEtag,
            resource: { ...advCatalogue },
            explanation: `Protection Optimiste réussie ! Votre If-Match (${ifMatch}) != ETag actuel (${curEtag}). L'écriture obsolète est bloquée en HTTP 412.`
          });
        }
        advCatalogue.salle = bodyObj.salle || advCatalogue.salle;
        advCatalogue.places = Number(bodyObj.places || advCatalogue.places);
        advCatalogue.version_metier += 1;
        advCatalogue.derniere_modification = "Mise à jour validée (If-Match OK) à " + new Date().toTimeString().split(" ")[0];
        const nextEtag = computeEtag(advCatalogue);
        return jsonResponse({
          http_status: 200,
          status_text: "200 OK (If-Match valide -> Ressource mise à jour)",
          request_headers: { "If-Match": ifMatch, "X-Request-ID": reqId },
          response_headers: { ETag: nextEtag, "X-Request-ID": reqId },
          bytes_transferred: new TextEncoder().encode(JSON.stringify(advCatalogue)).length,
          etag: nextEtag,
          resource: { ...advCatalogue },
          explanation: `Précondition validée -> nouvel ETag = ${nextEtag}.`
        });
      }
    }

    // 7. Sandbox HTTP, Versioning v1/v2 & Laboratoire curl
    if (path === "/api/sandbox/reset") {
      sandboxFormations = defaultFormations();
      rateLimitRemaining = 5;
      return jsonResponse({ message: "Sandbox réinitialisé." });
    }
    if (path === "/api/v1/sandbox/formations") {
      return tracedResponse(
        {
          version: "v1",
          items: sandboxFormations.map((f) => ({ id: f.id, intitule: f.titre, duree: f.duree_jours, salle: f.salle }))
        },
        200,
        '# Contrat v1 (Déprécié selon RFC 8594)\nresp.headers["Deprecation"] = "true"\nresp.headers["Sunset"] = "Thu, 31 Dec 2026 23:59:59 GMT"',
        ["1. Réception GET /api/v1/sandbox/formations", "2. Injection des en-têtes RFC 8594 Deprecation & Sunset", "3. Sérialisation du contrat plat historique v1"],
        {
          "X-API-Version": "1.0",
          Deprecation: "true",
          Sunset: "Thu, 31 Dec 2026 23:59:59 GMT",
          Link: '</api/v2/sandbox/formations>; rel="successor-version"'
        }
      );
    }
    if (path === "/api/v2/sandbox/formations") {
      return tracedResponse(
        {
          meta: { version: "v2", total_items: sandboxFormations.length },
          data: sandboxFormations.map((f) => ({
            id: f.id,
            titre: f.titre,
            duree: { valeur: f.duree_jours, unite: "jours", heures_pedagogiques: f.duree_jours * 7 },
            localisation: { salle: f.salle, campus: "ISGP Alger" }
          }))
        },
        200,
        '# Contrat v2 enrichi\nreturn {"meta": {...}, "data": [...]}',
        ["1. Réception GET /api/v2/sandbox/formations", "2. Structuration enveloppe meta/data", "3. Réponse HTTP 200 OK"],
        { "X-API-Version": "2.0" }
      );
    }
    if (path === "/api/sandbox/bonjour") {
      return tracedResponse(
        { message: "Bienvenue sur l'API ISGP (Simulation Interactive GitHub Pages)", statut: "opérationnel", framework: fw },
        200,
        '@app.get("/api/sandbox/bonjour")\ndef bonjour():\n    return {"message": "Bienvenue sur l\'API ISGP"}',
        ["1. Routage GET /api/sandbox/bonjour", "2. Sérialisation JSON UTF-8", "3. Envoi 200 OK"]
      );
    }
    if (path === "/api/sandbox/auth/token" && method === "POST") {
      const user = bodyObj.identifiant || "stagiaire";
      const role = user === "admin" ? "administrateur" : "lecteur";
      const tok = `isgp.${btoa(JSON.stringify({ sub: user, role })).replace(/=+$/, "")}.sig_${simpleHashHex(user)}`;
      issuedTokens[tok] = { sub: user, role };
      return tracedResponse(
        { access_token: tok, token_type: "Bearer", expires_in: 3600, role },
        200,
        '# Émission d\'un jeton signé HMAC-SHA256\ntoken = generer_jeton_hmac(identifiant, role)',
        ["1. Vérification des identifiants POST /auth/token", "2. Signature HMAC-SHA256 du payload", "3. Émission Bearer Token (200 OK)"]
      );
    }
    if (path === "/api/sandbox/auth/profil") {
      const auth = reqHeaders.get("Authorization") || "";
      const tok = auth.replace(/^Bearer\s+/i, "").trim();
      if (!tok) {
        return tracedResponse(
          { type: "https://api.isgp.dz/erreurs/non-authentifie", title: "Authentification requise (401)", status: 401 },
          401,
          'if not auth_header.startswith("Bearer "):\n    return problem_details(401)',
          ["1. Inspection de l'en-tête Authorization", "2. Jeton absent -> Rejet HTTP 401 Unauthorized"],
          { "WWW-Authenticate": 'Bearer realm="ISGP-API"' }
        );
      }
      const claims = issuedTokens[tok] || { sub: "stagiaire", role: "lecteur" };
      return tracedResponse(
        { utilisateur: claims.sub, role: claims.role, authentifie: true },
        200,
        'claims = verifier_signature_hmac(token)\nreturn {"utilisateur": claims["sub"], "role": claims["role"]}',
        ["1. Extraction du Bearer Token", "2. Vérification de signature en temps constant", "3. Accès autorisé (200 OK)"]
      );
    }
    if (path === "/api/sandbox/authz-demo") {
      const auth = reqHeaders.get("Authorization") || "";
      const tok = auth.replace(/^Bearer\s+/i, "").trim();
      if (!tok) {
        return tracedResponse({ title: "401 Unauthorized — Aucun jeton fourni", status: 401 }, 401, "# 401 AuthN", ["1. Jeton manquant -> 401"]);
      }
      const claims = issuedTokens[tok] || { sub: "stagiaire", role: "lecteur" };
      if (claims.role !== "administrateur") {
        return tracedResponse(
          { title: "403 Forbidden — Rôle insuffisant (lecteur != administrateur)", status: 403, votre_role: claims.role },
          403,
          'if claims["role"] != "administrateur":\n    return problem_details(403)',
          ["1. Authentification réussie (identité connue)", "2. Contrôle RBAC : rôle 'lecteur' != 'administrateur'", "3. Rejet HTTP 403 Forbidden"]
        );
      }
      return tracedResponse({ message: "Accès administrateur accordé", role: claims.role }, 200, "# 200 AuthZ OK", ["1. Rôle administrateur validé -> 200 OK"]);
    }
    if (path === "/api/sandbox/admin-stats") {
      if (reqHeaders.get("X-API-Key") !== "isgp-secret-2026") {
        return tracedResponse({ title: "Clé X-API-Key absente ou invalide", status: 401 }, 401, 'if not hmac.compare_digest(api_key, SECRET): abort(401)', ["1. Vérification X-API-Key -> Échec (401)"]);
      }
      return tracedResponse({ formations_actives: sandboxFormations.length, noeuds_cluster: 4, statut: "nominal" }, 200, "# X-API-Key valide -> 200 OK", ["1. X-API-Key validée -> 200 OK"]);
    }
    if (path === "/api/sandbox/ratelimit-demo") {
      if (rateLimitRemaining <= 0) {
        return tracedResponse(
          { title: "Quota dépassé (429 Too Many Requests)", status: 429, retry_after_seconds: 60 },
          429,
          "if compteur > QUOTA_MAX:\n    return problem_details(429), 429",
          ["1. Compteur de requêtes > limite autorisée", "2. Rejet HTTP 429 Too Many Requests + Retry-After"],
          { "X-RateLimit-Limit": "5", "X-RateLimit-Remaining": "0", "Retry-After": "60" }
        );
      }
      rateLimitRemaining -= 1;
      return tracedResponse(
        { message: "Requête acceptée sous quota", requetes_restantes: rateLimitRemaining },
        200,
        "compteur += 1\nresp.headers['X-RateLimit-Remaining'] = str(restant)",
        ["1. Vérification du quota glissant", `2. Crédits restants : ${rateLimitRemaining}/5`],
        { "X-RateLimit-Limit": "5", "X-RateLimit-Remaining": String(rateLimitRemaining) }
      );
    }
    if (path === "/api/sandbox/formations") {
      if (method === "GET") {
        return tracedResponse(
          { total: sandboxFormations.length, formations: sandboxFormations },
          200,
          'cur.execute("SELECT * FROM formations ORDER BY id ASC")\nreturn {"formations": cur.fetchall()}',
          ["1. Lecture paramétrée des formations", "2. Sérialisation JSON (200 OK)"]
        );
      }
      if (method === "POST") {
        const titre = String(bodyObj.titre || "").trim();
        const duree = Number(bodyObj.duree_jours ?? 3);
        if (titre.length < 3 || Number.isNaN(duree) || duree < 1) {
          return tracedResponse(
            { type: "https://api.isgp.dz/erreurs/validation", title: "Erreur de validation métier (422)", status: 422, detail: "titre >= 3 caractères et duree_jours >= 1 requis." },
            422,
            "# Validation métier -> 422 Unprocessable Entity",
            ["1. Parsing JSON", "2. Règle métier violée -> Rejet 422"]
          );
        }
        const created = {
          id: sandboxNextId++,
          titre,
          formateur: bodyObj.formateur || "Intervenant ISGP",
          duree_jours: duree,
          salle: bodyObj.salle || "Salle A"
        };
        sandboxFormations.push(created);
        return tracedResponse(created, 201, "cur.execute('INSERT INTO formations ...', params)\nreturn created, 201", ["1. Validation réussie", `2. Insertion #${created.id} -> HTTP 201 Created`]);
      }
    }
    const mFormId = path.match(/^\/api\/sandbox\/formations\/(\d+)$/);
    if (mFormId) {
      const id = Number(mFormId[1]);
      const idx = sandboxFormations.findIndex((f) => f.id === id);
      if (idx === -1) {
        return tracedResponse({ title: `Formation #${id} introuvable`, status: 404 }, 404, "if row is None: abort(404)", [`1. Recherche #${id} -> None`, "2. Réponse HTTP 404 Not Found"]);
      }
      if (method === "GET") {
        return tracedResponse(sandboxFormations[idx], 200, "row = find_one_formation(conn, id)", [`1. Formation #${id} trouvée -> 200 OK`]);
      }
      if (method === "DELETE") {
        const removed = sandboxFormations.splice(idx, 1)[0];
        return tracedResponse({ message: `Formation #${id} supprimée`, element: removed }, 200, "cur.execute('DELETE FROM formations WHERE id = ?', (id,))", [`1. Suppression #${id} validée`]);
      }
      if (method === "PUT" || method === "PATCH") {
        sandboxFormations[idx] = { ...sandboxFormations[idx], ...bodyObj, id };
        return tracedResponse(sandboxFormations[idx], 200, "cur.execute('UPDATE formations SET ... WHERE id = ?', params)", [`1. Mise à jour #${id} -> 200 OK`]);
      }
    }

    // 8. Simulateur curl côté navigateur
    if (path === "/api/curl/run") {
      const cmd = String(bodyObj.command || "");
      const urlMatch = cmd.match(/https?:\/\/[^\s"']+/);
      const methodMatch = cmd.match(/-X\s+([A-Z]+)/i);
      const simMethod = methodMatch ? methodMatch[1].toUpperCase() : cmd.includes("-I") ? "HEAD" : cmd.includes("-d ") ? "POST" : "GET";
      const targetPath = urlMatch ? new URL(urlMatch[0]).pathname + new URL(urlMatch[0]).search : "/api/sandbox/bonjour";
      const subRes = await window.fetch(targetPath, { method: simMethod === "HEAD" ? "GET" : simMethod });
      const subText = await subRes.text();
      let pretty = subText;
      try {
        pretty = JSON.stringify(JSON.parse(subText), null, 2);
      } catch (e) {}
      const hdrs = `HTTP/1.1 ${subRes.status} ${subRes.statusText}\nContent-Type: application/json\nX-Simulated-Mode: GitHub-Pages-Browser-Engine\n`;
      const out = cmd.includes("-I") ? hdrs : cmd.includes("-i") || cmd.includes("-v") ? `${hdrs}\n${pretty}` : pretty;
      return jsonResponse({ output: out });
    }

    // 9. Laboratoire Architecture : Nord-Sud vs Est-Ouest, OAuth 2.0 / RFC 8693 & OpenAPI/Swagger
    if (path.startsWith("/api/architecture-lab/")) {
      const r = await origFetch(`${SITE_ROOT}/static-data/${fw}/architecture-lab.json`);
      const archData = await r.json();
      if (path === "/api/architecture-lab/oauth-flow" && method === "POST") {
        const scenario = String(bodyObj.scenario || "pkce_north_south");
        const scenarios = archData.oauth_scenarios || {};
        const chosen = scenarios[scenario] || scenarios["pkce_north_south"] || {};
        return jsonResponse({ scenario, framework: fw, ...chosen }, 200);
      }
      if (path === "/api/architecture-lab/openapi-compare") {
        let selectedFw = (parsed.searchParams.get("target_fw") || fw || "flask").toLowerCase();
        if (!["flask", "fastapi", "tornado"].includes(selectedFw)) selectedFw = fw;
        const bundle = archData.openapi_bundle || {};
        return jsonResponse({
          selected_framework: selectedFw,
          openapi_yaml: bundle.openapi_yaml || "",
          framework_detail: (bundle.frameworks || {})[selectedFw] || {}
        }, 200);
      }
    }

    // 10. Atelier d'exécution Python (Mode GitHub Pages Statique)
    if (path.startsWith("/api/python/")) {
      if (path.endsWith("/stop") || path.endsWith("/status")) {
        return jsonResponse({ running: false, output: "Mode statique GitHub Pages." });
      }
      const codeStr = String(bodyObj.code || "");
      return jsonResponse({
        running: false,
        exit_code: 0,
        output:
          `[Aperçu Statique GitHub Pages — Édition ${fw.toUpperCase()}]\n` +
          `--------------------------------------------------------------------\n` +
          `GitHub Pages héberge des fichiers statiques (HTML/CSS/JS) et ne peut\n` +
          `pas ouvrir de vrais processus Python ou sockets TCP côté serveur.\n\n` +
          `Pour exécuter ce script (${codeStr.split("\\n").length} lignes) avec la vraie boucle\n` +
          `d'événements ${fw.toUpperCase()} et SQLite3 natif sur votre poste :\n\n` +
          `  git clone https://github.com/abdelouahabb/isgp-api.git\n` +
          `  cd isgp-api\n` +
          `  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt\n` +
          `  .venv/bin/python app.py\n` +
          `--------------------------------------------------------------------\n` +
          `Astuce : Tous les autres simulateurs (Client HTTP, SQLite Anti-SQLi,\n` +
          `SSE, Multipart Magic Bytes, Jobs 202, ETag 304/412 et Cluster Nginx)\n` +
          `sont 100 % interactifs directement ici dans votre navigateur !`
      });
    }

    return jsonResponse({ message: "Route simulée en mode statique GitHub Pages", path }, 200);
  };
})();
