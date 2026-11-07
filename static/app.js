// ============================================================================
// ISGP — Documentation & Laboratoire d'APIs (Python & Flask)
// ============================================================================

let COURSE_DATA = {
  days: [],
  glossary: [],
  quizzes: {}
};

let STATE = {
  activeTab: "course",
  activeDay: 0,
  activeLessonId: "d0-l1",
  activeQuizDay: 0,
  expandedDays: new Set([0]),
  sidebarHidden: false,
  deferredPwaPrompt: null
};

window.addEventListener("DOMContentLoaded", async () => {
  registerServiceWorker();
  setupPwaInstallPrompt();
  await loadCourseData();
  updateCurlPreview();
  refreshLiveTables();
});

// ============================================================================
// 1. CHARGEMENT DES DONNÉES DU COURS
// ============================================================================
async function loadCourseData() {
  try {
    const res = await fetch("/api/course-data");
    const data = await res.json();
    COURSE_DATA = data;
    renderDaysSidebar();
    renderActiveLesson();
    renderFilesTree();
    renderGlossary();
    renderQuizSelector();
    renderQuiz(STATE.activeQuizDay);
  } catch (err) {
    console.error("Erreur lors du chargement des données :", err);
    showToast("Mode hors-ligne : données chargées depuis le cache local.");
  }
}

// ============================================================================
// 2. SOMMAIRE RÉTRACTABLE & NAVIGATION PAR ONGLETS
// ============================================================================
function toggleCourseSidebar() {
  STATE.sidebarHidden = !STATE.sidebarHidden;
  const layout = document.getElementById("course-layout");
  const btn = document.getElementById("toggle-sidebar-btn");
  if (layout) {
    layout.classList.toggle("sidebar-hidden", STATE.sidebarHidden);
  }
  if (btn) {
    btn.textContent = STATE.sidebarHidden ? "Afficher le sommaire" : "Masquer le sommaire";
  }
}

function switchTab(tabName) {
  STATE.activeTab = tabName;
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tab === tabName);
  });
  document.querySelectorAll(".tab-section").forEach((sec) => {
    sec.classList.toggle("active", sec.id === `tab-${tabName}`);
  });
  if (tabName === "sandbox") {
    updateCurlPreview();
    refreshLiveTables();
  }
}

// ============================================================================
// 3. RENDU DU SUPPORT DE COURS (DOSSIERS day_0/ À day_5/)
// ============================================================================
function toggleDayGroup(dayNumber) {
  if (STATE.expandedDays.has(dayNumber)) {
    STATE.expandedDays.delete(dayNumber);
  } else {
    STATE.expandedDays.add(dayNumber);
  }
  renderDaysSidebar();
}

function renderDaysSidebar() {
  const container = document.getElementById("days-nav-container");
  if (!container) return;

  container.innerHTML = COURSE_DATA.days
    .map((day) => {
      const isDayActive = day.day_number === STATE.activeDay;
      const isExpanded = STATE.expandedDays.has(day.day_number);
      const lessonsHtml = day.lessons
        .map((lesson) => {
          const isLessonActive = lesson.id === STATE.activeLessonId;
          return `
            <button class="lesson-nav-btn ${isLessonActive ? "active" : ""}"
                    onclick="selectLesson(${day.day_number}, '${lesson.id}')">
              <span>${escapeHtml(lesson.title)}</span>
              <span class="muted-small">${escapeHtml(lesson.duration)}</span>
            </button>
          `;
        })
        .join("");

      return `
        <div class="day-group ${isExpanded ? "" : "collapsed"}">
          <div class="day-group-header ${isDayActive ? "active-day" : ""}"
               onclick="toggleDayGroup(${day.day_number})">
            <span class="day-header-left">
              <span class="day-chevron">&#9662;</span>
              <span>${escapeHtml(day.badge)}</span>
            </span>
            <code>${escapeHtml(day.folder)}/</code>
          </div>
          <div class="day-lessons-list">${lessonsHtml}</div>
        </div>
      `;
    })
    .join("");
}

function selectLesson(dayNumber, lessonId) {
  STATE.activeDay = dayNumber;
  STATE.activeLessonId = lessonId;
  STATE.expandedDays.add(dayNumber);
  renderDaysSidebar();
  renderActiveLesson();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderActiveLesson() {
  const dayObj =
    COURSE_DATA.days.find((d) => d.day_number === STATE.activeDay) || COURSE_DATA.days[0];
  if (!dayObj) return;

  const lesson =
    dayObj.lessons.find((l) => l.id === STATE.activeLessonId) || dayObj.lessons[0];

  const filePath = lesson.file || dayObj.starter_filename;
  const fileBasename = filePath.split("/").pop();

  const banner = document.getElementById("day-header-banner");
  banner.innerHTML = `
    <div>
      <div class="day-banner-meta">${escapeHtml(dayObj.badge)} — Dossier : ${escapeHtml(dayObj.folder)}/</div>
      <h2>${escapeHtml(dayObj.title)}</h2>
      <p><strong>Objectif :</strong> ${escapeHtml(dayObj.goal)}</p>
    </div>
    <div class="btn-group">
      <a class="btn-secondary" href="/api/day-file/${dayObj.day_number}/${encodeURIComponent(fileBasename)}?download=1" download>
        Télécharger ${escapeHtml(filePath)}
      </a>
      <button class="btn-primary" onclick="openDayQuiz(${dayObj.day_number})">
        Évaluation Jour ${dayObj.day_number}
      </button>
    </div>
  `;

  const detailContainer = document.getElementById("lesson-detail-container");

  const explanationsHtml = (lesson.explanation || [])
    .map((item) => `<div class="explanation-item">${formatRichText(item)}</div>`)
    .join("");

  const lineExplainHtml = (lesson.line_explanations || [])
    .map(
      (le) => `
      <div class="line-explain-item">
        <span class="line-badge">Ligne ${escapeHtml(le.lines)}</span>
        <div>${formatRichText(le.text)}</div>
      </div>
    `
    )
    .join("");

  let runnerHtml = "";
  if (lesson.python_runner) {
    runnerHtml = `
      <div class="interactive-try-box">
        <div class="label-row">
          <h4>Exécution Directe Python (<code>${escapeHtml(filePath)}</code>)</h4>
          <button class="btn-primary btn-sm" onclick="runLessonPython('${lesson.id}')">
            Exécuter le code
          </button>
        </div>
        <p class="muted-small" style="margin-top:0;">${escapeHtml(lesson.python_runner.prompt)}</p>
        <textarea id="lesson-runner-code-${lesson.id}" rows="10" class="code-textarea">${escapeHtml(lesson.python_runner.initial_code)}</textarea>
        <div style="margin-top:8px;">
          <pre id="lesson-runner-output-${lesson.id}" class="terminal-output">Cliquez sur « Exécuter le code » pour afficher la sortie standard.</pre>
        </div>
      </div>
    `;
  }

  let sandboxPresetHtml = "";
  if (lesson.sandbox_preset) {
    const p = lesson.sandbox_preset;
    const headersJson = JSON.stringify(p.headers || {}).replace(/"/g, "&quot;");
    const bodyEscaped = JSON.stringify(p.body || "");
    sandboxPresetHtml = `
      <div class="interactive-try-box">
        <div class="label-row">
          <h4>Test de l'Endpoint dans le Client HTTP</h4>
          <button class="btn-primary btn-sm" onclick='launchSandboxFromLesson(${JSON.stringify(p.method)}, ${JSON.stringify(p.url)}, ${bodyEscaped}, ${headersJson})'>
            ${escapeHtml(p.label)}
          </button>
        </div>
        <p class="muted-small" style="margin:0;">
          Exécute la requête <code>${escapeHtml(p.method)} ${escapeHtml(p.url)}</code> dans l'inspecteur HTTP et affiche la réponse et la trace serveur.
        </p>
      </div>
    `;
  }

  let vscodeHtml = "";
  if (lesson.vscode_instructions) {
    const stepsHtml = lesson.vscode_instructions.steps
      .map((s) => `<li>${formatRichText(s)}</li>`)
      .join("");
    vscodeHtml = `
      <div class="vscode-box">
        <div class="label-row">
          <h4>Exécution Locale — VS Code / Antigravity IDE (<code>${escapeHtml(lesson.vscode_instructions.filename)}</code>)</h4>
          <button class="btn-secondary btn-sm" onclick="copyLessonCode()">Copier le code source</button>
        </div>
        <ol style="margin:6px 0 0 0; padding-left:20px; font-size:13px; color:#374151;">
          ${stepsHtml}
        </ol>
      </div>
    `;
  }

  const { prev, next } = getAdjacentLessons(dayObj.day_number, lesson.id);

  detailContainer.innerHTML = `
    <article class="lesson-card">
      <div class="lesson-title-row">
        <h3>${escapeHtml(lesson.title)}</h3>
        <div class="btn-group">
          <span class="category-tag">Fichier : ${escapeHtml(filePath)}</span>
          <span class="category-tag">Durée : ${escapeHtml(lesson.duration)}</span>
        </div>
      </div>

      ${
        lesson.analogy
          ? `
        <div class="analogy-box">
          <h4>Analogie Fonctionnelle — ${escapeHtml(lesson.analogy.title)}</h4>
          <p>${formatRichText(lesson.analogy.text)}</p>
        </div>
      `
          : ""
      }

      <div class="explanation-box">
        <h4>Présentation Méthodique (Sans Prérequis)</h4>
        ${explanationsHtml}
      </div>

      <div class="code-walkthrough-grid">
        <div class="code-panel">
          <div class="panel-bar">
            <span>Fichier : ${escapeHtml(filePath)}</span>
            <button class="btn-xs" onclick="copyLessonCode()">Copier</button>
          </div>
          <pre id="active-lesson-code" class="code-block">${escapeHtml(lesson.code)}</pre>
        </div>

        <div class="line-explain-panel">
          <div class="panel-bar">
            <span>Analyse Détaillée Ligne par Ligne</span>
          </div>
          <div class="line-explain-list">
            ${lineExplainHtml}
          </div>
        </div>
      </div>

      ${sandboxPresetHtml}
      ${runnerHtml}
      ${vscodeHtml}

      <div class="lesson-footer-nav">
        ${
          prev
            ? `<button class="btn-secondary" onclick="selectLesson(${prev.day}, '${prev.id}')">Chapitre précédent</button>`
            : `<span></span>`
        }
        ${
          next
            ? `<button class="btn-primary" onclick="selectLesson(${next.day}, '${next.id}')">Chapitre suivant</button>`
            : `<button class="btn-primary" onclick="openDayQuiz(${dayObj.day_number})">Accéder à l'évaluation du module</button>`
        }
      </div>
    </article>
  `;
}

function getAdjacentLessons(dayNum, lessonId) {
  const flat = [];
  COURSE_DATA.days.forEach((d) => {
    d.lessons.forEach((l) => flat.push({ day: d.day_number, id: l.id }));
  });
  const idx = flat.findIndex((item) => item.id === lessonId);
  return {
    prev: idx > 0 ? flat[idx - 1] : null,
    next: idx >= 0 && idx < flat.length - 1 ? flat[idx + 1] : null
  };
}

function copyLessonCode() {
  const el = document.getElementById("active-lesson-code");
  if (el) copyText(el.innerText);
}

async function runLessonPython(lessonId) {
  const codeEl = document.getElementById(`lesson-runner-code-${lessonId}`);
  const outEl = document.getElementById(`lesson-runner-output-${lessonId}`);
  if (!codeEl || !outEl) return;

  outEl.textContent = "Exécution en cours...";
  try {
    const res = await fetch("/api/python/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: codeEl.value })
    });
    const data = await res.json();
    if (data.error) {
      outEl.style.color = "#fca5a5";
      outEl.textContent = (data.output ? data.output + "\n" : "") + "Erreur d'exécution :\n" + data.error;
    } else {
      outEl.style.color = "#e2e8f0";
      outEl.textContent = data.output || "(Exécution terminée sans sortie sur stdout)";
    }
  } catch (e) {
    outEl.textContent = "Erreur lors de l'exécution du script.";
  }
}

// ============================================================================
// 4. ARBORESCENCE DES DOSSIERS day_0/ À day_5/ (ATELIER PYTHON)
// ============================================================================
function renderFilesTree() {
  const container = document.getElementById("project-files-tree");
  if (!container) return;

  container.innerHTML = COURSE_DATA.days
    .map((day) => {
      const filesList = (day.files || [])
        .map((fp) => {
          const base = fp.split("/").pop();
          return `
            <div class="file-item-row">
              <span>${escapeHtml(fp)}</span>
              <div class="btn-group">
                <button class="btn-xs" onclick="loadDayFileToStudio(${day.day_number}, '${escapeHtml(base)}')">Charger dans l'éditeur</button>
                <a class="btn-xs" href="/api/day-file/${day.day_number}/${encodeURIComponent(base)}?download=1" download>Télécharger</a>
              </div>
            </div>
          `;
        })
        .join("");

      return `
        <div class="folder-card">
          <div class="folder-card-title">
            <span>Dossier : ${escapeHtml(day.folder)}/</span>
            <span class="muted-small">${escapeHtml(day.badge)}</span>
          </div>
          ${filesList}
        </div>
      `;
    })
    .join("");
}

async function loadDayFileToStudio(dayNum, filename) {
  try {
    const res = await fetch(`/api/day-file/${dayNum}/${encodeURIComponent(filename)}`);
    const data = await res.json();
    if (data.code) {
      document.getElementById("studio-python-editor").value = data.code;
      showToast(`Fichier ${data.path} chargé dans l'éditeur.`);
    }
  } catch (e) {
    showToast("Impossible de charger le fichier.");
  }
}

// ============================================================================
// 5. CLIENT HTTP & INSPECTEUR SERVEUR FLASK
// ============================================================================
function onMethodChange() {
  updateCurlPreview();
}

function loadSandboxPreset(method, url, body, headers = {}) {
  document.getElementById("http-method").value = method;
  document.getElementById("http-url").value = url;
  document.getElementById("http-body").value = body || "";
  if (headers["X-API-Key"] !== undefined) {
    document.getElementById("http-header-apikey").value = headers["X-API-Key"] || "";
  }
  if (headers["Authorization"] !== undefined) {
    document.getElementById("http-header-bearer").value = headers["Authorization"].replace(/^Bearer\s+/i, "");
  }
  updateCurlPreview();
  sendSandboxRequest();
}

async function quickGenerateAndInjectToken() {
  try {
    const res = await fetch("/api/sandbox/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifiant: "stagiaire", mot_de_passe: "isgp2026" })
    });
    const data = await res.json();
    if (data.access_token) {
      document.getElementById("http-header-bearer").value = data.access_token;
      updateCurlPreview();
      showToast("Bearer Token signé généré et injecté dans le champ Authorization.");
    }
  } catch (e) {
    showToast("Erreur lors de la génération du jeton.");
  }
}

function launchSandboxFromLesson(method, url, body, headers = {}) {
  switchTab("sandbox");
  loadSandboxPreset(method, url, body, headers);
}

function formatSandboxJson() {
  const el = document.getElementById("http-body");
  if (!el || !el.value.trim()) return;
  try {
    const parsed = JSON.parse(el.value);
    el.value = JSON.stringify(parsed, null, 2);
    updateCurlPreview();
  } catch (e) {
    showToast("Erreur de syntaxe JSON : vérifiez les guillemets doubles et les virgules.");
  }
}

function updateCurlPreview() {
  const method = document.getElementById("http-method")?.value || "GET";
  const url = document.getElementById("http-url")?.value || "/api/sandbox/formations";
  const bearer = document.getElementById("http-header-bearer")?.value.trim() || "";
  const apiKey = document.getElementById("http-header-apikey")?.value.trim() || "";
  const body = document.getElementById("http-body")?.value.trim() || "";
  const fullUrl = window.location.origin + url;

  let cmd = `curl -X ${method} "${fullUrl}"`;
  if (bearer) {
    cmd += ` \\\n  -H "Authorization: Bearer ${bearer}"`;
  }
  if (apiKey) {
    cmd += ` \\\n  -H "X-API-Key: ${apiKey}"`;
  }
  if ((method === "POST" || method === "PUT") && body) {
    cmd += ` \\\n  -H "Content-Type: application/json" \\\n  -d '${body.replace(/\n/g, " ")}'`;
  }

  const previewEl = document.getElementById("http-curl-preview");
  if (previewEl) previewEl.textContent = cmd;
}

async function sendSandboxRequest() {
  updateCurlPreview();
  const method = document.getElementById("http-method").value;
  const url = document.getElementById("http-url").value.trim();
  const bearer = document.getElementById("http-header-bearer")?.value.trim() || "";
  const apiKey = document.getElementById("http-header-apikey")?.value.trim() || "";
  const bodyText = document.getElementById("http-body").value.trim();

  const headers = {};
  if (bearer) {
    headers["Authorization"] = bearer.startsWith("Bearer ") ? bearer : `Bearer ${bearer}`;
  }
  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  const fetchOptions = { method, headers };
  if (method === "POST" || method === "PUT") {
    headers["Content-Type"] = "application/json";
    if (bodyText) {
      try {
        JSON.parse(bodyText);
      } catch (e) {
        showToast("Attention : le corps JSON transmis est mal formé.");
      }
      fetchOptions.body = bodyText;
    }
  }

  const startTime = performance.now();
  try {
    const res = await fetch(url, fetchOptions);
    const elapsed = Math.round(performance.now() - startTime);

    const badgeEl = document.getElementById("http-status-badge");
    badgeEl.textContent = `HTTP ${res.status} ${res.statusText}`;
    badgeEl.className = "status-pill " + (res.status < 300 ? "status-2xx" : res.status < 500 ? "status-4xx" : "status-5xx");

    document.getElementById("http-time-meta").textContent = `Temps de réponse : ${elapsed} ms`;

    const headerKeys = [
      "content-type",
      "x-ratelimit-limit",
      "x-ratelimit-remaining",
      "x-ratelimit-reset",
      "retry-after",
      "www-authenticate"
    ];
    const headerLines = [];
    headerKeys.forEach((k) => {
      const val = res.headers.get(k);
      if (val !== null) {
        headerLines.push(`${k}: ${val}`);
      }
    });
    const respHeadersEl = document.getElementById("http-response-headers");
    if (respHeadersEl) {
      respHeadersEl.textContent = headerLines.join("\n") || "content-type: application/json";
    }

    const handlerHeader = res.headers.get("X-Flask-Handler-Code");
    const stepsHeader = res.headers.get("X-Flask-Trace-Steps");

    if (handlerHeader) {
      document.getElementById("flask-handler-code").textContent = JSON.parse(handlerHeader);
    }
    if (stepsHeader) {
      const steps = JSON.parse(stepsHeader);
      document.getElementById("flask-trace-steps").innerHTML = steps
        .map((s) => `<div class="trace-step">${escapeHtml(s)}</div>`)
        .join("");
    }

    const data = await res.json();
    document.getElementById("http-response-json").textContent = JSON.stringify(data, null, 2);

    if (data && data.access_token && document.getElementById("http-header-bearer")) {
      document.getElementById("http-header-bearer").value = data.access_token;
      updateCurlPreview();
      showToast("Bearer Token reçu et automatiquement injecté dans le champ Authorization.");
    }

    await refreshLiveTables();
  } catch (err) {
    document.getElementById("http-response-json").textContent = "Erreur lors de l'appel HTTP : " + err.message;
  }
}

async function refreshLiveTables() {
  try {
    const formRes = await fetch("/api/sandbox/formations");
    const formData = await formRes.json();

    const tableContainer = document.getElementById("live-formations-table");
    if (tableContainer && formData.formations) {
      tableContainer.innerHTML = `
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Intitulé</th>
              <th>Intervenant</th>
              <th>Durée</th>
              <th>Salle</th>
              <th>Opérations</th>
            </tr>
          </thead>
          <tbody>
            ${formData.formations
              .map(
                (f) => `
              <tr>
                <td><strong>#${f.id}</strong></td>
                <td>${escapeHtml(f.titre)}</td>
                <td>${escapeHtml(f.formateur || "")}</td>
                <td>${f.duree_jours} j</td>
                <td>${escapeHtml(f.salle)}</td>
                <td>
                  <button class="btn-xs" onclick="loadSandboxPreset('GET', '/api/sandbox/formations/${f.id}', '')">GET</button>
                  <button class="btn-xs" onclick="loadSandboxPreset('DELETE', '/api/sandbox/formations/${f.id}', '')">DELETE</button>
                </td>
              </tr>
            `
              )
              .join("")}
          </tbody>
        </table>
      `;
    }
  } catch (e) {
    // Mode hors ligne
  }
}

async function resetSandboxDB() {
  await fetch("/api/sandbox/reset", { method: "POST" });
  await refreshLiveTables();
  showToast("Base de données SQLite et compteurs Rate Limit réinitialisés.");
}

// ============================================================================
// 6. ATELIER PYTHON INTERACTIF
// ============================================================================
const STUDIO_TEMPLATES = {
  dict: `# Fichier : day_0/02_listes_et_dictionnaires.py
stagiaires = [
    {"id": 1, "nom": "Amine", "service": "Développement"},
    {"id": 2, "nom": "Sara", "service": "Réseau"}
]

stagiaires.append({"id": 3, "nom": "Karim", "service": "Sécurité"})

for s in stagiaires:
    print(f"ID #{s['id']} : {s['nom']} ({s['service']})")
`,
  json: `# Fichier : day_1/02_serialisation_json.py
import json

catalogue = {
    "organisme": "ISGP",
    "formation": "Développement d'APIs et services web",
    "prerequis": None,
    "active": True
}

en_json = json.dumps(catalogue, indent=2, ensure_ascii=False)
print("Flux JSON généré :")
print(en_json)
`,
  sqlite: `# Création et interrogation d'une base SQLite en mémoire
import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row
conn.execute("CREATE TABLE formations (id INTEGER PRIMARY KEY, titre TEXT, jours INTEGER)")
conn.execute("INSERT INTO formations (titre, jours) VALUES ('Flask API REST', 5)")
conn.execute("INSERT INTO formations (titre, jours) VALUES ('Secrets, Tokens & Rate Limit', 3)")
conn.commit()

lignes = conn.execute("SELECT * FROM formations").fetchall()
print("Enregistrements extraits :", [dict(r) for r in lignes])
`,
  call_api: `# Fichier : day_5/01_client_python_auth.py
import urllib.request
import json

BASE_URL = "http://127.0.0.1:5000"

payload = json.dumps({"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}).encode("utf-8")
req_token = urllib.request.Request(
    f"{BASE_URL}/api/sandbox/auth/token",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)
res_token = json.loads(urllib.request.urlopen(req_token).read().decode("utf-8"))
token = res_token["access_token"]
print("1. Bearer Token obtenu :", token[:35] + "...")

req_profil = urllib.request.Request(
    f"{BASE_URL}/api/sandbox/auth/profil",
    headers={"Authorization": f"Bearer {token}"}
)
res_profil = json.loads(urllib.request.urlopen(req_profil).read().decode("utf-8"))
print("2. Profil sécurisé :", json.dumps(res_profil, indent=2, ensure_ascii=False))
`
};

function loadStudioTemplate(key) {
  const editor = document.getElementById("studio-python-editor");
  if (editor && STUDIO_TEMPLATES[key]) {
    editor.value = STUDIO_TEMPLATES[key];
    runStudioPython();
  }
}

async function runStudioPython() {
  const code = document.getElementById("studio-python-editor").value;
  const outEl = document.getElementById("studio-python-output");
  const statusEl = document.getElementById("studio-run-status");

  statusEl.textContent = "Exécution en cours...";
  outEl.textContent = "Exécution en cours...";
  try {
    const res = await fetch("/api/python/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code })
    });
    const data = await res.json();
    statusEl.textContent = data.exit_code === 0 ? "Code retour : 0 (Succès)" : `Code retour : ${data.exit_code}`;
    if (data.error) {
      outEl.style.color = "#fca5a5";
      outEl.textContent = (data.output ? data.output + "\n" : "") + data.error;
    } else {
      outEl.style.color = "#e2e8f0";
      outEl.textContent = data.output || "(Exécution terminée sans sortie sur stdout)";
    }
  } catch (e) {
    statusEl.textContent = "Erreur";
    outEl.textContent = "Impossible de joindre le service d'exécution Python.";
  }
}

// ============================================================================
// 7. RÉFÉRENTIEL DES CONCEPTS
// ============================================================================
function renderGlossary() {
  const grid = document.getElementById("glossary-grid");
  if (!grid) return;

  const query = (document.getElementById("glossary-search")?.value || "").toLowerCase().trim();
  const cat = document.getElementById("glossary-category")?.value || "ALL";

  const filtered = (COURSE_DATA.glossary || []).filter((item) => {
    const matchCat = cat === "ALL" || item.category === cat;
    const matchText =
      !query ||
      item.term.toLowerCase().includes(query) ||
      item.short.toLowerCase().includes(query) ||
      item.explanation.toLowerCase().includes(query) ||
      item.analogy.toLowerCase().includes(query);
    return matchCat && matchText;
  });

  if (filtered.length === 0) {
    grid.innerHTML = `<div class="card"><p>Aucun concept ne correspond aux critères de recherche.</p></div>`;
    return;
  }

  grid.innerHTML = filtered
    .map(
      (item) => `
      <div class="glossary-card">
        <div class="glossary-card-top">
          <h3>${escapeHtml(item.term)}</h3>
          <span class="category-tag">${escapeHtml(item.category)}</span>
        </div>
        <p style="margin:0; font-weight:600; color:#111827;">${escapeHtml(item.short)}</p>
        <div class="glossary-analogy">
          <strong>Analogie :</strong> ${escapeHtml(item.analogy)}
        </div>
        <p style="margin:0; font-size:13px; color:#374151; white-space:pre-line;">${formatRichText(item.explanation)}</p>
        <pre class="code-block" style="font-size:12px; padding:10px; border-radius:4px;">${escapeHtml(item.code_example)}</pre>
      </div>
    `
    )
    .join("");
}

// ============================================================================
// 8. ÉVALUATIONS PAR MODULE
// ============================================================================
function openDayQuiz(dayNum) {
  STATE.activeQuizDay = dayNum;
  switchTab("quiz");
  renderQuizSelector();
  renderQuiz(dayNum);
}

function renderQuizSelector() {
  const sel = document.getElementById("quiz-day-selector");
  if (!sel) return;
  sel.innerHTML = [0, 1, 2, 3, 4, 5]
    .map(
      (d) => `
      <button class="btn-chip ${STATE.activeQuizDay === d ? "btn-primary" : ""}"
              style="${STATE.activeQuizDay === d ? "background:#1e3a5f;color:#fff;border-color:#1e3a5f;" : ""}"
              onclick="openDayQuiz(${d})">
        ${d === 0 ? "Jour 0 — Diagnostic" : "Module Jour " + d}
      </button>
    `
    )
    .join("");
}

function renderQuiz(dayNum) {
  const container = document.getElementById("quiz-container");
  const quiz = COURSE_DATA.quizzes?.[dayNum];
  if (!container || !quiz) return;

  container.innerHTML = `
    <div class="card" style="margin-bottom:14px;">
      <h3 style="margin:0 0 4px 0;">${escapeHtml(quiz.title)}</h3>
      <p class="muted-small" style="margin:0;">${escapeHtml(quiz.description)}</p>
    </div>
    ${quiz.questions
      .map(
        (q, qIdx) => `
        <div class="quiz-question-card" id="quiz-card-${q.id}">
          <h4 style="margin:0 0 10px 0;">Question ${qIdx + 1} — ${formatRichText(q.question)}</h4>
          <div>
            ${q.options
              .map(
                (opt, optIdx) => `
                <button class="quiz-option-btn"
                        id="quiz-opt-${q.id}-${optIdx}"
                        onclick="checkQuizAnswer('${dayNum}', '${q.id}', ${optIdx}, ${q.correct_index})">
                  ${escapeHtml(opt)}
                </button>
              `
              )
              .join("")}
          </div>
          <div id="quiz-feedback-${q.id}" class="quiz-feedback hidden">
            <strong>Justification :</strong> ${formatRichText(q.explanation)}
          </div>
        </div>
      `
      )
      .join("")}
  `;
}

function checkQuizAnswer(dayNum, qId, chosenIdx, correctIdx) {
  const quiz = COURSE_DATA.quizzes?.[dayNum];
  const question = quiz?.questions.find((q) => q.id === qId);
  if (!question) return;

  question.options.forEach((_, idx) => {
    const btn = document.getElementById(`quiz-opt-${qId}-${idx}`);
    if (!btn) return;
    btn.classList.remove("correct", "wrong");
    if (idx === correctIdx) {
      btn.classList.add("correct");
    } else if (idx === chosenIdx) {
      btn.classList.add("wrong");
    }
  });

  const fb = document.getElementById(`quiz-feedback-${qId}`);
  if (fb) fb.classList.remove("hidden");
}

// ============================================================================
// 9. PWA & UTILITAIRES
// ============================================================================
function registerServiceWorker() {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  }
}

function setupPwaInstallPrompt() {
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    STATE.deferredPwaPrompt = e;
    document.getElementById("install-pwa-btn")?.classList.remove("hidden");
  });
}

async function installPWA() {
  if (!STATE.deferredPwaPrompt) return;
  STATE.deferredPwaPrompt.prompt();
  await STATE.deferredPwaPrompt.userChoice;
  STATE.deferredPwaPrompt = null;
  document.getElementById("install-pwa-btn")?.classList.add("hidden");
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast("Copié dans le presse-papiers.");
  });
}

function showToast(msg) {
  const t = document.getElementById("toast-notification");
  if (!t) return;
  t.textContent = msg;
  t.classList.remove("hidden");
  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => t.classList.add("hidden"), 3000);
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatRichText(str) {
  const escaped = escapeHtml(str);
  return escaped
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}
