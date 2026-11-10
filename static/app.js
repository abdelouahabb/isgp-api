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
  activeDay: -1,
  activeLessonId: "c0-l1",
  activeQuizDay: 8,
  expandedDays: new Set([-1]),
  sidebarHidden: false,
  deferredPwaPrompt: null
};

window.addEventListener("DOMContentLoaded", async () => {
  applyTheme(getCurrentTheme(), false);
  initMermaidEngine();
  registerServiceWorker();
  setupPwaInstallPrompt();
  await loadCourseData();
  renderCurlCheatsheet();
  updateCurlPreview();
  refreshLiveTables();
});

// ============================================================================
// 0. GESTION DU MODE NUIT / MODE CLAIR (SANS FLASH + RE-RENDU MERMAID)
// ============================================================================
function getCurrentTheme() {
  const saved = localStorage.getItem("isgp-theme");
  if (saved === "dark" || saved === "light") return saved;
  return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function getThemeButtonInnerHtml(theme) {
  if (theme === "dark") {
    return (
      '<svg viewBox="0 0 24 24" aria-hidden="true">' +
      '<circle cx="12" cy="12" r="4"></circle>' +
      '<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"></path>' +
      "</svg><span>Mode Clair</span>"
    );
  }
  return (
    '<svg viewBox="0 0 24 24" aria-hidden="true">' +
    '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>' +
    "</svg><span>Mode Nuit</span>"
  );
}

function applyTheme(theme, persist = true) {
  const normalized = theme === "dark" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", normalized);
  if (persist) {
    try {
      localStorage.setItem("isgp-theme", normalized);
    } catch (e) {}
  }
  const metaTheme = document.querySelector('meta[name="theme-color"]');
  if (metaTheme) {
    metaTheme.setAttribute("content", normalized === "dark" ? "#080d19" : "#2563eb");
  }
  document.querySelectorAll(".theme-toggle-btn").forEach((btn) => {
    btn.innerHTML = getThemeButtonInnerHtml(normalized);
    btn.setAttribute(
      "title",
      normalized === "dark" ? "Basculer vers le Mode Clair" : "Basculer vers le Mode Nuit"
    );
  });
}

async function toggleTheme() {
  const next = getCurrentTheme() === "dark" ? "light" : "dark";
  applyTheme(next, true);
  initMermaidEngine();
  const activeSec = document.getElementById(`tab-${STATE.activeTab}`) || document;
  await renderMermaidDiagrams(activeSec);
  showToast(next === "dark" ? "Mode Nuit activé" : "Mode Clair activé");
}

function initMermaidEngine() {
  if (typeof mermaid !== "undefined") {
    const isDark = getCurrentTheme() === "dark";
    mermaid.initialize({
      startOnLoad: false,
      theme: "base",
      securityLevel: "loose",
      themeVariables: isDark
        ? {
            darkMode: true,
            background: "transparent",
            primaryColor: "#172554",
            primaryTextColor: "#f1f5f9",
            primaryBorderColor: "#60a5fa",
            lineColor: "#94a3b8",
            secondaryColor: "#1e293b",
            tertiaryColor: "#0f172a",
            actorBkg: "#1e293b",
            actorBorder: "#60a5fa",
            actorTextColor: "#f8fafc",
            actorLineColor: "#64748b",
            signalColor: "#cbd5e1",
            signalTextColor: "#f8fafc",
            labelBoxBkgColor: "#1e293b",
            labelBoxBorderColor: "#475569",
            labelTextColor: "#f8fafc",
            loopTextColor: "#e2e8f0",
            noteBkgColor: "#1e3a5f",
            noteBorderColor: "#60a5fa",
            noteTextColor: "#f8fafc",
            clusterBkg: "#0b1324",
            clusterBorder: "#33476b",
            titleColor: "#f8fafc",
            edgeLabelBackground: "#0f172a",
            fontFamily: "Inter, system-ui, -apple-system, sans-serif",
            fontSize: "14px"
          }
        : {
            darkMode: false,
            background: "transparent",
            primaryColor: "#eff6ff",
            primaryTextColor: "#0f172a",
            primaryBorderColor: "#2563eb",
            lineColor: "#475569",
            secondaryColor: "#f8fafc",
            tertiaryColor: "#f1f5f9",
            actorBkg: "#eff6ff",
            actorBorder: "#2563eb",
            actorTextColor: "#0f172a",
            noteBkgColor: "#fef9c3",
            noteBorderColor: "#eab308",
            noteTextColor: "#0f172a",
            clusterBkg: "#f8fafc",
            clusterBorder: "#cbd5e1",
            edgeLabelBackground: "#ffffff",
            fontFamily: "Inter, system-ui, -apple-system, sans-serif",
            fontSize: "14px"
          }
    });
  }
}

async function renderMermaidDiagrams(rootEl) {
  if (typeof mermaid === "undefined") return;
  const scope = rootEl || document;
  const blocks = Array.from(scope.querySelectorAll("pre.mermaid"));
  if (!blocks.length) return;

  blocks.forEach((el) => {
    if (!el.getAttribute("data-mermaid-src")) {
      el.setAttribute("data-mermaid-src", el.textContent.trim());
    }
    if (el.getAttribute("data-processed")) {
      el.removeAttribute("data-processed");
      el.textContent = el.getAttribute("data-mermaid-src");
    }
  });

  try {
    await mermaid.run({ nodes: blocks });
  } catch (err) {
    console.warn("Avertissement rendu Mermaid :", err);
  }
}

// ============================================================================
// 1. CHARGEMENT DES DONNÉES DU COURS
// ============================================================================
function getActiveFramework() {
  return window.ACTIVE_FRAMEWORK || "flask";
}

async function loadCourseData() {
  try {
    const fw = encodeURIComponent(getActiveFramework());
    const res = await fetch(`/api/course-data?framework=${fw}`);
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
  if (tabName === "curl") {
    renderCurlCheatsheet();
  }
  if (tabName === "nginx") {
    loadNginxClusterTab();
  }
  if (tabName === "sqlite") {
    loadSqliteLabTab();
  }
  if (tabName === "realtime") {
    loadAdvancedRealtimeTab();
  }
  if (tabName === "architecture") {
    loadArchitectureTab();
  }
  const activeSec = document.getElementById(`tab-${tabName}`);
  if (activeSec) {
    setTimeout(() => renderMermaidDiagrams(activeSec), 20);
  }
}

// ============================================================================
// 3. RENDU DU SUPPORT DE COURS (DOSSIERS day_0/ À day_5/)
// ============================================================================
function toggleDayGroup(dayNumber) {
  if (STATE.expandedDays.has(dayNumber)) {
    STATE.expandedDays.delete(dayNumber);
  } else {
    STATE.expandedDays.clear();
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
              <span>${formatInlineText(lesson.title)}</span>
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
            <code>${escapeHtml(day.sidebar_tag || (day.folder + "/"))}</code>
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
  STATE.expandedDays.clear();
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

  const filePath = lesson.file || dayObj.starter_filename || "";
  const fileBasename = filePath ? filePath.split("/").pop() : "";
  const quizTargetId = dayObj.quiz_id !== undefined ? dayObj.quiz_id : dayObj.day_number;

  const banner = document.getElementById("day-header-banner");
  if (dayObj.is_literature_chapter) {
    banner.innerHTML = `
      <div>
        <div class="day-banner-meta">${escapeHtml(dayObj.badge)} — Lecture Fondamentale (Avant Python)</div>
        <h2>${formatInlineText(dayObj.title)}</h2>
        <p><strong>Objectif :</strong> ${formatInlineText(dayObj.goal)}</p>
      </div>
      <div class="btn-group">
        <button class="btn-secondary" onclick="switchTab('architecture')">
          Ouvrir les Labos Interactifs OAuth2 &amp; Swagger
        </button>
        <button class="btn-primary" onclick="openDayQuiz(${quizTargetId})">
          Évaluation Chapitre 0
        </button>
      </div>
    `;
  } else {
    banner.innerHTML = `
      <div>
        <div class="day-banner-meta">${escapeHtml(dayObj.badge)} — Dossier : ${escapeHtml(dayObj.folder)}/</div>
        <h2>${formatInlineText(dayObj.title)}</h2>
        <p><strong>Objectif :</strong> ${formatInlineText(dayObj.goal)}</p>
      </div>
      <div class="btn-group">
        <a class="btn-secondary" href="/api/day-file/${dayObj.day_number}/${encodeURIComponent(fileBasename)}?download=1&framework=${encodeURIComponent(getActiveFramework())}" download>
          Télécharger ${escapeHtml(filePath)}
        </a>
        <button class="btn-primary" onclick="openDayQuiz(${quizTargetId})">
          Évaluation Jour ${dayObj.day_number}
        </button>
      </div>
    `;
  }

  const detailContainer = document.getElementById("lesson-detail-container");

  const contextHtml = lesson.context
    ? `
      <div class="doc-context-box">
        <h4>${lesson.is_literature ? "1. Histoire, Philosophie &amp; Mise en Situation" : "1. Contexte &amp; Problématique d'Ingénierie"}</h4>
        <div class="doc-context-text">${formatRichText(lesson.context)}</div>
      </div>
    `
    : "";

  const deepSectionsHtml =
    lesson.deep_sections && lesson.deep_sections.length
      ? `
      <div class="deep-sections-wrapper">
        ${lesson.deep_sections
          .map(
            (sec) => `
          <div class="deep-section-card">
            <h5>${formatInlineText(sec.heading)}</h5>
            <div class="deep-section-body">${formatRichText(sec.body)}</div>
          </div>
        `
          )
          .join("")}
      </div>
    `
      : "";

  const explanationsHtml = (lesson.explanation || [])
    .map((item) => `<div class="explanation-item">${formatRichText(item)}</div>`)
    .join("");

  const mermaidHtml =
    lesson.mermaid_diagram && lesson.mermaid_diagram.code
      ? `
      <div class="mermaid-container">
        <div class="mermaid-title">Diagramme d'Architecture &amp; Séquence — ${escapeHtml(lesson.mermaid_diagram.title)}</div>
        <pre class="mermaid">${escapeHtml(lesson.mermaid_diagram.code)}</pre>
      </div>
    `
      : "";

  const archDiagramHtml = lesson.architecture_diagram
    ? `
      <div class="arch-diagram-box">
        <h4>Schéma d'Architecture &amp; Flux d'Exécution</h4>
        <pre class="arch-diagram-pre">${escapeHtml(lesson.architecture_diagram)}</pre>
      </div>
    `
    : "";

  const refTableHtml =
    lesson.reference_table && lesson.reference_table.headers
      ? `
      <div class="ref-table-box">
        <h4>${formatInlineText(lesson.reference_table.title || "Tableau de Synthèse & Référence Technique")}</h4>
        <table class="data-table">
          <thead>
            <tr>
              ${lesson.reference_table.headers.map((h) => `<th>${formatInlineText(h)}</th>`).join("")}
            </tr>
          </thead>
          <tbody>
            ${(lesson.reference_table.rows || [])
              .map(
                (row) => `
              <tr>
                ${row.map((cell) => `<td>${formatInlineText(cell)}</td>`).join("")}
              </tr>
            `
              )
              .join("")}
          </tbody>
        </table>
      </div>
    `
      : "";

  const pitfallsHtml =
    lesson.pitfalls && lesson.pitfalls.length
      ? `
      <div class="pitfalls-box">
        <h4>Erreurs Fréquentes en Production (Anti-Patterns) vs Standards Industriels</h4>
        <div class="pitfalls-grid">
          ${lesson.pitfalls
            .map(
              (pf) => `
            <div class="pitfall-row">
              <div class="pitfall-bad">
                <div class="pitfall-tag">[Anti-Pattern — À proscrire]</div>
                <div>${formatInlineText(pf.bad)}</div>
              </div>
              <div class="pitfall-good">
                <div class="pitfall-tag">[Standard de Production]</div>
                <div>${formatInlineText(pf.good)}</div>
              </div>
              <div class="pitfall-why">
                <div class="pitfall-tag">[Justification Technique]</div>
                <div>${formatInlineText(pf.why)}</div>
              </div>
            </div>
          `
            )
            .join("")}
        </div>
      </div>
    `
      : "";

  const exercisesHtml =
    lesson.practical_exercises && lesson.practical_exercises.length
      ? `
      <div class="exercises-box">
        <h4>${lesson.is_literature ? "Questions de Réflexion &amp; Passerelle vers la Suite" : "Travaux Pratiques &amp; Exercices d'Approfondissement Post-Bootcamp"}</h4>
        <ol style="margin:8px 0 0 0; padding-left:22px; font-size:15.5px; color:var(--text-secondary); line-height:1.7;">
          ${lesson.practical_exercises.map((ex) => `<li style="margin-bottom:8px;">${formatRichText(ex)}</li>`).join("")}
        </ol>
      </div>
    `
      : "";

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
          <h4>Exécution Directe &amp; Simulateur de Boucle Serveur (<code>${escapeHtml(filePath)}</code>)</h4>
          <div class="btn-group">
            <button class="btn-primary btn-sm" onclick="runLessonPython('${lesson.id}')">
              Démarrer / Exécuter le code
            </button>
            <button id="lesson-runner-stop-${lesson.id}" class="btn-secondary btn-sm" style="display:none; background:#fee2e2; color:#991b1b; border-color:#fca5a5;" onclick="stopLivePythonServer('${lesson.id}')">
              Envoyer Ctrl+C (Arrêter la boucle)
            </button>
          </div>
        </div>
        <p class="muted-small" style="margin-top:0;">${formatInlineText(lesson.python_runner.prompt)}</p>
        <textarea id="lesson-runner-code-${lesson.id}" rows="10" class="code-textarea">${escapeHtml(lesson.python_runner.initial_code)}</textarea>
        <div id="lesson-runner-livebar-${lesson.id}" style="display:none; margin-top:8px; padding:10px 12px; background:#064e3b; color:#ecfdf5; border:1px solid #10b981; border-radius:4px; font-size:13.5px;"></div>
        <div style="margin-top:8px;">
          <pre id="lesson-runner-output-${lesson.id}" class="terminal-output">Cliquez sur « Démarrer / Exécuter le code » pour lancer le script ou démarrer la boucle serveur interactive.</pre>
        </div>
      </div>
    `;
  }

  let sandboxPresetHtml = "";
  if (lesson.sandbox_preset) {
    const p = lesson.sandbox_preset;
    const headersJson = JSON.stringify(p.headers || {}).replace(/"/g, "&quot;");
    const bodyEscaped = JSON.stringify(p.body || "");

    // Construction automatique de la commande curl correspondante
    let lessonCurl = `curl -i -X ${p.method} "http://127.0.0.1:5000${p.url}"`;
    if (p.headers) {
      Object.entries(p.headers).forEach(([k, v]) => {
        lessonCurl += ` \\\n  -H "${k}: ${v}"`;
      });
    }
    if ((p.method === "POST" || p.method === "PUT" || p.method === "PATCH") && p.body) {
      const compactBody = p.body.replace(/\s*\n\s*/g, " ").trim();
      const isJsonBody = compactBody.startsWith("{") || compactBody.startsWith("[");
      if (isJsonBody) {
        lessonCurl += ` \\\n  -H "Content-Type: application/json" \\\n  -d '${compactBody}'`;
      } else {
        lessonCurl += ` \\\n  -H "Content-Type: application/x-www-form-urlencoded" \\\n  -d "${compactBody}"`;
      }
    }
    const lessonCurlEscaped = JSON.stringify(lessonCurl);

    const extraLiveLinkHtml =
      lesson.id === "d2-l5"
        ? `<a href="/sandbox/formulaire-jinja" target="_blank" class="btn-secondary btn-sm" style="text-decoration:none; display:inline-flex; align-items:center;">Ouvrir le Formulaire Jinja2 Live</a>`
        : lesson.id === "d5-l4"
        ? `<a href="/api/docs" target="_blank" class="btn-secondary btn-sm" style="text-decoration:none; display:inline-flex; align-items:center;">Ouvrir Swagger UI Live</a>`
        : "";

    sandboxPresetHtml = `
      <div class="interactive-try-box">
        <div class="label-row">
          <h4>Test de l'Endpoint (<code>curl</code>, Postman &amp; Client HTTP)</h4>
          <div class="btn-group">
            ${extraLiveLinkHtml}
            <button class="btn-secondary btn-sm" onclick='launchCurlLabFromLesson(${lessonCurlEscaped})'>
              Exécuter avec curl
            </button>
            <button class="btn-primary btn-sm" onclick='launchSandboxFromLesson(${JSON.stringify(p.method)}, ${JSON.stringify(p.url)}, ${bodyEscaped}, ${headersJson})'>
              ${escapeHtml(p.label)}
            </button>
          </div>
        </div>
        <p class="muted-small" style="margin:0 0 8px 0;">
          Commande <code>curl</code> équivalente à exécuter dans votre terminal ou dans l'onglet <strong>curl &amp; Postman</strong> :
        </p>
        <pre class="code-block-mini" style="margin:0;">${escapeHtml(lessonCurl)}</pre>
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
        <ol style="margin:8px 0 0 0; padding-left:22px; font-size:15.5px; color:#374151; line-height:1.7;">
          ${stepsHtml}
        </ol>
      </div>
    `;
  }

  const { prev, next } = getAdjacentLessons(dayObj.day_number, lesson.id);

  const codeWalkthroughHtml =
    lesson.code && lesson.code.trim()
      ? `
      <div class="code-walkthrough-grid">
        <div class="code-panel">
          <div class="panel-bar">
            <span>${lesson.artifact_title ? escapeHtml(lesson.artifact_title) : "Fichier : " + escapeHtml(filePath)}</span>
            <button class="btn-xs" onclick="copyLessonCode()">Copier</button>
          </div>
          <pre id="active-lesson-code" class="code-block">${escapeHtml(lesson.code)}</pre>
        </div>

        <div class="line-explain-panel">
          <div class="panel-bar">
            <span>${lesson.is_literature ? "Lecture Annotée Section par Section" : "Analyse Détaillée Ligne par Ligne"}</span>
          </div>
          <div class="line-explain-list">
            ${lineExplainHtml}
          </div>
        </div>
      </div>
    `
      : "";

  detailContainer.innerHTML = `
    <article class="lesson-card">
      <div class="lesson-title-row">
        <h3>${formatInlineText(lesson.title)}</h3>
        <div class="btn-group">
          <span class="category-tag">${lesson.is_literature ? "Prologue Littéraire — Culture &amp; Jargon" : "Fichier : " + escapeHtml(filePath)}</span>
          <span class="category-tag">${lesson.is_literature ? "Lecture : " : "Durée : "}${escapeHtml(lesson.duration)}</span>
        </div>
      </div>

      ${contextHtml}

      ${
        lesson.analogy
          ? `
        <div class="analogy-box">
          <h4>Modèle Mental &amp; Analogie Fonctionnelle — ${formatInlineText(lesson.analogy.title)}</h4>
          <div class="analogy-text">${formatRichText(lesson.analogy.text)}</div>
        </div>
      `
          : ""
      }

      ${deepSectionsHtml}

      <div class="explanation-box">
        <h4>${lesson.is_literature ? "Points Clés à Retenir (Synthèse Fondamentale)" : "Synthèse Méthodique &amp; Règles d'Ingénierie"}</h4>
        ${explanationsHtml}
      </div>

      ${mermaidHtml || archDiagramHtml}
      ${refTableHtml}
      ${pitfallsHtml}

      ${codeWalkthroughHtml}

      ${sandboxPresetHtml}
      ${runnerHtml}
      ${vscodeHtml}
      ${exercisesHtml}

      <div class="lesson-footer-nav">
        ${
          prev
            ? `<button class="btn-secondary" onclick="selectLesson(${prev.day}, '${prev.id}')">Chapitre précédent</button>`
            : `<span></span>`
        }
        ${
          next
            ? `<button class="btn-primary" onclick="selectLesson(${next.day}, '${next.id}')">Chapitre suivant</button>`
            : `<button class="btn-primary" onclick="openDayQuiz(${quizTargetId})">Accéder à l'évaluation du module</button>`
        }
      </div>
    </article>
  `;
  renderMermaidDiagrams(detailContainer);
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

let LIVE_PYTHON_POLL_TIMER = null;

function _clearLivePythonPoll() {
  if (LIVE_PYTHON_POLL_TIMER) {
    clearInterval(LIVE_PYTHON_POLL_TIMER);
    LIVE_PYTHON_POLL_TIMER = null;
  }
}

function _renderLiveLoopBar(targetId, data) {
  const barEl = document.getElementById(`lesson-runner-livebar-${targetId}`) || document.getElementById("studio-runner-livebar");
  const stopBtn = document.getElementById(`lesson-runner-stop-${targetId}`) || document.getElementById("studio-runner-stop");
  if (!barEl) return;

  if (!data || !data.running) {
    barEl.style.display = "none";
    if (stopBtn) stopBtn.style.display = "none";
    _clearLivePythonPoll();
    return;
  }

  if (stopBtn) stopBtn.style.display = "inline-flex";
  barEl.style.display = "block";
  const port = data.port || 8889;
  const routes = Array.isArray(data.routes) && data.routes.length > 0 ? data.routes : ["/"];
  const routeBtns = routes
    .map(
      (r) =>
        `<button class="btn-xs" style="background:#047857; color:#ffffff; border:1px solid #34d399; padding:3px 9px; border-radius:4px; cursor:pointer; font-family:monospace;" onclick="probeLivePythonServer('${escapeHtml(r)}', '${targetId}')">GET ${escapeHtml(r)}</button>`
    )
    .join(" ");

  barEl.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:8px;">
      <div>
        <strong style="color:#6ee7b7;">[BOUCLE SERVEUR EN ÉCOUTE ACTIVE]</strong>
        <span style="margin-left:8px; font-family:monospace;">PID #${data.pid} • http://127.0.0.1:${port}</span>
      </div>
      <div style="display:flex; gap:6px; align-items:center;">
        <a href="http://127.0.0.1:${port}${escapeHtml(routes[0])}" target="_blank" style="color:#a7f3d0; text-decoration:underline; font-size:12.5px; font-weight:600;">
          Ouvrir http://127.0.0.1:${port}${escapeHtml(routes[0])} dans un onglet
        </a>
        <button class="btn-xs" style="background:#991b1b; color:#ffffff; border:1px solid #f87171; padding:3px 9px; border-radius:4px; cursor:pointer;" onclick="stopLivePythonServer('${targetId}')">
          Envoyer Ctrl+C (SIGINT)
        </button>
      </div>
    </div>
    <div style="display:flex; align-items:center; flex-wrap:wrap; gap:6px;">
      <span style="font-size:12.5px; color:#d1fae5;">Envoyer une requête en direct à la boucle :</span>
      ${routeBtns}
    </div>
  `;
}

function _startLivePythonPoll(targetId, outEl, statusEl) {
  _clearLivePythonPoll();
  LIVE_PYTHON_POLL_TIMER = setInterval(async () => {
    try {
      const res = await fetch("/api/python/status");
      const data = await res.json();
      if (outEl && data.output) {
        outEl.textContent = data.output;
        outEl.scrollTop = outEl.scrollHeight;
      }
      if (!data.running) {
        _renderLiveLoopBar(targetId, { running: false });
        if (statusEl) statusEl.textContent = "Boucle arrêtée (Code 0)";
      }
    } catch (e) {
      _clearLivePythonPoll();
    }
  }, 1200);
}

async function probeLivePythonServer(path, targetId) {
  const outEl =
    document.getElementById(`lesson-runner-output-${targetId}`) ||
    (targetId === "sqlite" ? document.getElementById("sqlite-standalone-output") : null) ||
    (targetId === "realtime" ? document.getElementById("realtime-standalone-output") : null) ||
    document.getElementById("studio-python-output");
  try {
    const res = await fetch("/api/python/probe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path })
    });
    const data = await res.json();
    if (outEl && data.output) {
      outEl.style.color = "#e2e8f0";
      outEl.textContent = data.output;
      outEl.scrollTop = outEl.scrollHeight;
    }
  } catch (e) {
    showToast("Erreur lors de l'appel à la boucle active.");
  }
}

async function stopLivePythonServer(targetId) {
  const outEl =
    document.getElementById(`lesson-runner-output-${targetId}`) ||
    (targetId === "sqlite" ? document.getElementById("sqlite-standalone-output") : null) ||
    (targetId === "realtime" ? document.getElementById("realtime-standalone-output") : null) ||
    document.getElementById("studio-python-output");
  const statusEl = document.getElementById("studio-run-status");
  _clearLivePythonPoll();
  try {
    const res = await fetch("/api/python/stop", { method: "POST" });
    const data = await res.json();
    _renderLiveLoopBar(targetId, { running: false });
    if (statusEl) statusEl.textContent = "Boucle arrêtée par Ctrl+C (SIGINT)";
    if (outEl && data.output) {
      outEl.textContent = data.output;
      outEl.scrollTop = outEl.scrollHeight;
    }
    showToast("Signal Ctrl+C (SIGINT) envoyé : boucle serveur arrêtée.");
  } catch (e) {
    showToast("Erreur lors de l'arrêt du serveur.");
  }
}

async function runLessonPython(lessonId) {
  const codeEl = document.getElementById(`lesson-runner-code-${lessonId}`);
  const outEl = document.getElementById(`lesson-runner-output-${lessonId}`);
  if (!codeEl || !outEl) return;

  _clearLivePythonPoll();
  outEl.textContent = "Démarrage du script Python / Boucle serveur en cours...";
  try {
    const fw = getActiveFramework();
    const res = await fetch(`/api/python/run?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ code: codeEl.value })
    });
    const data = await res.json();
    _renderLiveLoopBar(lessonId, data);
    if (data.error) {
      outEl.style.color = "#fca5a5";
      outEl.textContent = (data.output ? data.output + "\n" : "") + "Erreur d'exécution :\n" + data.error;
    } else {
      outEl.style.color = "#e2e8f0";
      outEl.textContent = data.output || "(Exécution terminée sans sortie sur stdout)";
      outEl.scrollTop = outEl.scrollHeight;
      if (data.running) {
        _startLivePythonPoll(lessonId, outEl, null);
      }
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

  const fw = encodeURIComponent(getActiveFramework());
  const refFiles = [
    {
      name: "sqlite_api_lab.py",
      label: "sqlite_api_lab.py — Référence SQLite3 WAL, Curseurs & Sécurité SQL"
    },
    {
      name: "advanced_realtime_cache_lab.py",
      label: "advanced_realtime_cache_lab.py — SSE, Upload Streaming, Jobs 202 & ETag 304/412"
    }
  ];
  const refCardHtml = `
    <div class="folder-card" style="border-left: 4px solid #0f766e;">
      <div class="folder-card-title">
        <span>Laboratoires de Référence Transversaux</span>
        <span class="muted-small">SQLite3 &amp; Temps Réel / Cache</span>
      </div>
      ${refFiles
        .map(
          (rf) => `
          <div class="file-item-row">
            <span>${escapeHtml(rf.label)}</span>
            <div class="btn-group">
              <button class="btn-xs" onclick="loadReferenceFileToStudio('${escapeHtml(rf.name)}')">Charger dans l'éditeur</button>
              <a class="btn-xs" href="/api/reference-file/${encodeURIComponent(rf.name)}?download=1&framework=${fw}" download>Télécharger</a>
            </div>
          </div>
        `
        )
        .join("")}
    </div>
  `;

  container.innerHTML =
    refCardHtml +
    COURSE_DATA.days
      .filter((day) => day.files && day.files.length > 0)
      .map((day) => {
        const filesList = (day.files || [])
          .map((fp) => {
            const base = fp.split("/").pop();
            return `
              <div class="file-item-row">
                <span>${escapeHtml(fp)}</span>
                <div class="btn-group">
                  <button class="btn-xs" onclick="loadDayFileToStudio(${day.day_number}, '${escapeHtml(base)}')">Charger dans l'éditeur</button>
                  <a class="btn-xs" href="/api/day-file/${day.day_number}/${encodeURIComponent(base)}?download=1&framework=${fw}" download>Télécharger</a>
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

async function loadReferenceFileToStudio(filename) {
  try {
    const fw = encodeURIComponent(getActiveFramework());
    const res = await fetch(`/api/reference-file/${encodeURIComponent(filename)}?framework=${fw}`);
    const data = await res.json();
    if (data.code) {
      document.getElementById("studio-python-editor").value = data.code;
      showToast(`Fichier ${data.path} chargé dans l'éditeur.`);
    }
  } catch (e) {
    showToast("Impossible de charger le fichier de référence.");
  }
}

async function loadDayFileToStudio(dayNum, filename) {
  try {
    const fw = encodeURIComponent(getActiveFramework());
    const res = await fetch(`/api/day-file/${dayNum}/${encodeURIComponent(filename)}?framework=${fw}`);
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

async function quickGenerateAndInjectToken(identifiant = "stagiaire") {
  try {
    const res = await fetch("/api/sandbox/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifiant, mot_de_passe: "isgp2026" })
    });
    const data = await res.json();
    if (data.access_token) {
      document.getElementById("http-header-bearer").value = data.access_token;
      updateCurlPreview();
      showToast(`Bearer Token '${identifiant}' généré et injecté dans Authorization.`);
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
  if ((method === "POST" || method === "PUT" || method === "PATCH") && body) {
    const isJsonBody = body.startsWith("{") || body.startsWith("[");
    if (isJsonBody) {
      cmd += ` \\\n  -H "Content-Type: application/json" \\\n  -d '${body.replace(/\n/g, " ")}'`;
    } else {
      cmd += ` \\\n  -H "Content-Type: application/x-www-form-urlencoded" \\\n  -d "${body.replace(/\n/g, " ")}"`;
    }
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

  const headers = {
    "X-Active-Framework": getActiveFramework()
  };
  if (bearer) {
    headers["Authorization"] = bearer.startsWith("Bearer ") ? bearer : `Bearer ${bearer}`;
  }
  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  const fetchOptions = { method, headers };
  if (method === "POST" || method === "PUT" || method === "PATCH") {
    const isFormEncoded = bodyText && !bodyText.startsWith("{") && !bodyText.startsWith("[") && bodyText.includes("=");
    if (isFormEncoded) {
      headers["Content-Type"] = "application/x-www-form-urlencoded";
      fetchOptions.body = bodyText;
    } else {
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
      "x-api-version",
      "deprecation",
      "sunset",
      "link",
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
conn.execute("INSERT INTO formations (titre, jours) VALUES ('Architecture API REST Python', 5)")
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

  let barEl = document.getElementById("studio-runner-livebar");
  if (!barEl && outEl && outEl.parentElement) {
    barEl = document.createElement("div");
    barEl.id = "studio-runner-livebar";
    barEl.style.cssText =
      "display:none; margin-bottom:8px; padding:10px 12px; background:#064e3b; color:#ecfdf5; border:1px solid #10b981; border-radius:4px; font-size:13.5px;";
    outEl.parentElement.insertBefore(barEl, outEl);
  }

  _clearLivePythonPoll();
  statusEl.textContent = "Démarrage en cours...";
  outEl.textContent = "Démarrage du script Python / Boucle serveur en cours...";
  try {
    const fw = getActiveFramework();
    const res = await fetch(`/api/python/run?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ code })
    });
    const data = await res.json();
    _renderLiveLoopBar("studio", data);
    if (data.running) {
      statusEl.textContent = `Boucle active (PID #${data.pid} • Port :${data.port})`;
      outEl.style.color = "#e2e8f0";
      outEl.textContent = data.output || "";
      outEl.scrollTop = outEl.scrollHeight;
      _startLivePythonPoll("studio", outEl, statusEl);
    } else {
      statusEl.textContent = data.exit_code === 0 ? "Code retour : 0 (Succès)" : `Code retour : ${data.exit_code}`;
      if (data.error) {
        outEl.style.color = "#fca5a5";
        outEl.textContent = (data.output ? data.output + "\n" : "") + data.error;
      } else {
        outEl.style.color = "#e2e8f0";
        outEl.textContent = data.output || "(Exécution terminée sans sortie sur stdout)";
      }
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
          <h3>${formatInlineText(item.term)}</h3>
          <span class="category-tag">${escapeHtml(item.category)}</span>
        </div>
        <p style="margin:0; font-weight:600; color:#111827;">${formatInlineText(item.short)}</p>
        <div class="glossary-analogy">
          <strong>Analogie :</strong> ${formatInlineText(item.analogy)}
        </div>
        <div style="margin:0; font-size:15px; color:#374151; line-height:1.65;">${formatRichText(item.explanation)}</div>
        <pre class="code-block" style="font-size:13.5px; padding:12px; border-radius:4px;">${escapeHtml(item.code_example)}</pre>
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
  const quizLabels = {
    8: "Chapitre 0 — Littérature, Jargon, OAuth2 & Swagger",
    0: "Jour 0 — Fondations Python",
    1: "Module Jour 1",
    2: "Module Jour 2",
    3: "Module Jour 3",
    4: "Module Jour 4",
    5: "Module Jour 5",
    6: "Spécial SQLite & Sécurité SQL",
    7: "Spécial Temps Réel, Upload & Cache"
  };
  sel.innerHTML = [8, 0, 1, 2, 3, 4, 5, 6, 7]
    .filter((d) => COURSE_DATA.quizzes && COURSE_DATA.quizzes[d])
    .map(
      (d) => `
      <button class="btn-chip ${STATE.activeQuizDay === d ? "btn-primary" : ""}"
              onclick="openDayQuiz(${d})">
        ${quizLabels[d] || "Module " + d}
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
      <h3 style="margin:0 0 4px 0;">${formatInlineText(quiz.title)}</h3>
      <p class="muted-small" style="margin:0;">${formatInlineText(quiz.description)}</p>
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
                  ${formatInlineText(opt)}
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

function formatInlineText(str) {
  const raw = String(str ?? "")
    .replace(/\$\\rightarrow\$/g, "→")
    .replace(/\\rightarrow/g, "→");

  // 1. Extraire et protéger tous les blocs `code` par des jetons temporaires
  //    afin que les expressions **gras (`code`)** ou *italique* englobant du code fonctionnent toujours.
  const codeBlocks = [];
  const tokenized = raw.replace(/`([^`]+)`/g, (_, codeContent) => {
    const idx = codeBlocks.length;
    codeBlocks.push(`<code>${escapeHtml(codeContent)}</code>`);
    return `\x00CODE${idx}\x00`;
  });

  // 2. Échapper le HTML et formater le gras (**...**) et l'italique (*...*) sur la ligne entière
  let formatted = escapeHtml(tokenized)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*\n]+?)\*/g, "<em>$1</em>")
    .replace(/ -&gt; /g, " &rarr; ");

  // 3. Réinjecter les blocs <code>...</code> protégés
  return formatted.replace(/\x00CODE(\d+)\x00/g, (_, idx) => codeBlocks[Number(idx)] || "");
}

function formatRichText(str) {
  const lines = String(str ?? "").split("\n");
  if (lines.length === 1) {
    return formatInlineText(lines[0]);
  }
  return lines
    .map((line, idx) => {
      if (!line.trim()) return "";
      if (/^\s{4,}-\s+/.test(line)) {
        return `<div class="rich-line-sub2">&ndash; ${formatInlineText(line.replace(/^\s+-\s+/, ""))}</div>`;
      }
      if (/^\s*-\s+/.test(line)) {
        return `<div class="rich-line-sub">&bull; ${formatInlineText(line.replace(/^\s*-\s+/, ""))}</div>`;
      }
      if (/^\s*\d+\.\s+/.test(line)) {
        return `<div class="rich-line-sub">${formatInlineText(line.trim())}</div>`;
      }
      return `<div class="${idx === 0 ? "rich-line-main" : "rich-line-p"}">${formatInlineText(line)}</div>`;
    })
    .join("");
}

// ============================================================================
// 10. LABORATOIRE CURL, POSTMAN & HTTPIE
// ============================================================================
const CURL_PRESETS = {
  get_list: `curl -i -X GET "http://127.0.0.1:5000/api/sandbox/formations?page=1&limit=2&tri=duree_jours&ordre=desc" \\\n  -H "Accept: application/json"`,
  post_create: `curl -i -X POST "http://127.0.0.1:5000/api/sandbox/formations" \\\n  -H "Content-Type: application/json" \\\n  -d '{"titre": "Tests Automatisés avec curl", "formateur": "Formateur ISGP", "duree_jours": 4, "salle": "Labo 2"}'`,
  put_update: `curl -i -X PUT "http://127.0.0.1:5000/api/sandbox/formations/1" \\\n  -H "Content-Type: application/json" \\\n  -d '{"titre": "Architecture API REST & Python (Complet)", "duree_jours": 5, "salle": "Salle Conférence"}'`,
  patch_partial: `curl -i -X PATCH "http://127.0.0.1:5000/api/sandbox/formations/1" \\\n  -H "Content-Type: application/json" \\\n  -d '{"salle": "Amphithéâtre Principal"}'`,
  apikey_auth: `curl -i -X GET "http://127.0.0.1:5000/api/sandbox/admin-stats" \\\n  -H "X-API-Key: isgp-secret-2026"`,
  bearer_issue: `curl -i -X POST "http://127.0.0.1:5000/api/sandbox/auth/token" \\\n  -H "Content-Type: application/json" \\\n  -d '{"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}'`,
  ratelimit_429: `curl -i -X GET "http://127.0.0.1:5000/api/sandbox/ratelimit-demo"`,
  verbose_trace: `curl -v -X GET "http://127.0.0.1:5000/api/sandbox/bonjour"`
};

function loadCurlPreset(key) {
  const input = document.getElementById("curl-lab-input");
  if (!input || !CURL_PRESETS[key]) return;
  input.value = CURL_PRESETS[key];
  executeLiveCurlCommand();
}

function launchCurlLabFromLesson(curlCmd) {
  switchTab("curl");
  const input = document.getElementById("curl-lab-input");
  if (input) {
    input.value = curlCmd;
    executeLiveCurlCommand();
  }
}

async function executeLiveCurlCommand() {
  const input = document.getElementById("curl-lab-input");
  const output = document.getElementById("curl-lab-output");
  if (!input || !output) return;

  output.style.color = "#e2e8f0";
  output.textContent = "Exécution de la commande curl en cours...";
  try {
    const res = await fetch("/api/curl/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: input.value })
    });
    const data = await res.json();
    if (data.error) {
      output.style.color = "#fca5a5";
      output.textContent = "Erreur :\n" + data.error;
    } else {
      output.style.color = "#e2e8f0";
      output.textContent = data.output || "(Aucune sortie)";
    }
  } catch (err) {
    output.style.color = "#fca5a5";
    output.textContent = "Erreur lors de l'exécution de curl.";
  }
}

const CURL_CHEATSHEET_ITEMS = [
  // ================= 1. INSPECTION & DIAGNOSTIC HTTP =================
  {
    category: "1. Inspection & Diagnostic HTTP",
    badge: "GET simple",
    title: "1.1 — Requête GET minimale (Corps uniquement)",
    desc: "Interroge une URL en GET et affiche uniquement le corps JSON sur la sortie standard (sans les en-têtes HTTP).",
    cmd: `curl "http://127.0.0.1:5000/api/sandbox/bonjour"`,
    liveRunnable: true
  },
  {
    category: "1. Inspection & Diagnostic HTTP",
    badge: "-i / --include",
    title: "1.2 — Inspecter la Ligne de Statut et les En-têtes HTTP (-i)",
    desc: "Affiche la ligne HTTP/1.1 200 OK et tous les en-têtes (Content-Type, X-RateLimit-*, Date) au-dessus du corps JSON.",
    cmd: `curl -i "http://127.0.0.1:5000/api/sandbox/formations"`,
    liveRunnable: true
  },
  {
    category: "1. Inspection & Diagnostic HTTP",
    badge: "-I / --head",
    title: "1.3 — Requête HEAD : récupérer uniquement les En-têtes (-I)",
    desc: "Vérifie si une route répond (200 OK), sa taille (Content-Length) et son type MIME sans télécharger le corps JSON.",
    cmd: `curl -I "http://127.0.0.1:5000/api/sandbox/formations"`,
    liveRunnable: true
  },
  {
    category: "1. Inspection & Diagnostic HTTP",
    badge: "-v / --verbose",
    title: "1.4 — Diagnostic Réseau Complet en Mode Verbeux (-v)",
    desc: "Affiche la connexion TCP, la requête brute envoyée (lignes '>'), et la réponse brute reçue (lignes '<'). Indispensable en débogage.",
    cmd: `curl -v "http://127.0.0.1:5000/api/sandbox/bonjour"`,
    liveRunnable: true
  },
  {
    category: "1. Inspection & Diagnostic HTTP",
    badge: "-G --data-urlencode",
    title: "1.5 — Paramètres d'URL (Query String) avec encodage automatique (-G)",
    desc: "Combine -G et --data-urlencode pour encoder proprement les espaces et caractères spéciaux dans l'URL (?salle=Labo%201&page=1).",
    cmd: `curl -i -G "http://127.0.0.1:5000/api/sandbox/formations" \\\n  --data-urlencode "salle=Labo 1" \\\n  --data-urlencode "page=1" \\\n  --data-urlencode "limit=2"`,
    liveRunnable: true
  },
  {
    category: "1. Inspection & Diagnostic HTTP",
    badge: "Accept / User-Agent",
    title: "1.6 — Personnaliser le User-Agent (-A) et la Négociation de Contenu (Accept)",
    desc: "Spécifie l'identifiant du logiciel client (-A) et exige explicitement le format JSON via l'en-tête Accept.",
    cmd: `curl -i -A "ISGP-Audit-Client/1.0" \\\n  -H "Accept: application/json" \\\n  "http://127.0.0.1:5000/api/sandbox/meteo?ville=Alger"`,
    liveRunnable: true
  },

  // ================= 2. OPÉRATIONS CRUD & ENVOI JSON =================
  {
    category: "2. Opérations CRUD & Envoi JSON",
    badge: "POST JSON (-d)",
    title: "2.1 — Créer une ressource avec POST et un Corps JSON (-X POST -H -d)",
    desc: "La commande standard universelle pour envoyer un dictionnaire JSON à une route POST et recevoir 201 Created.",
    cmd: `curl -i -X POST "http://127.0.0.1:5000/api/sandbox/formations" \\\n  -H "Content-Type: application/json" \\\n  -d '{"titre": "Microservices Python", "formateur": "ISGP", "duree_jours": 5, "salle": "Salle C"}'`,
    liveRunnable: true
  },
  {
    category: "2. Opérations CRUD & Envoi JSON",
    badge: "--json (curl 7.82+)",
    title: "2.2 — Syntaxe Moderne Raccourcie (--json)",
    desc: "Depuis curl 7.82+, l'option --json configure automatiquement -X POST, Content-Type: application/json et Accept: application/json.",
    cmd: `curl -i --json '{"titre": "Créé avec --json", "duree_jours": 3, "salle": "Labo 1"}' \\\n  "http://127.0.0.1:5000/api/sandbox/formations"`,
    liveRunnable: true
  },
  {
    category: "2. Opérations CRUD & Envoi JSON",
    badge: "PUT (Remplacement)",
    title: "2.3 — Mise à jour intégrale et idempotente d'une ressource (-X PUT)",
    desc: "Remplace les données de la ressource ciblée (/formations/1) par le nouveau JSON fourni.",
    cmd: `curl -i -X PUT "http://127.0.0.1:5000/api/sandbox/formations/1" \\\n  -H "Content-Type: application/json" \\\n  -d '{"titre": "Architecture API REST & Sécurité", "duree_jours": 5, "salle": "Salle Conférence"}'`,
    liveRunnable: true
  },
  {
    category: "2. Opérations CRUD & Envoi JSON",
    badge: "PATCH (Partiel)",
    title: "2.4 — Modification partielle d'un seul champ (-X PATCH)",
    desc: "Modifie uniquement le champ 'salle' de la formation #1 sans toucher à son titre ni à sa durée.",
    cmd: `curl -i -X PATCH "http://127.0.0.1:5000/api/sandbox/formations/1" \\\n  -H "Content-Type: application/json" \\\n  -d '{"salle": "Amphithéâtre ISGP"}'`,
    liveRunnable: true
  },
  {
    category: "2. Opérations CRUD & Envoi JSON",
    badge: "DELETE",
    title: "2.5 — Supprimer une ressource par son identifiant (-X DELETE)",
    desc: "Envoie une requête DELETE sur l'URI de la ressource ciblée.",
    cmd: `curl -i -X DELETE "http://127.0.0.1:5000/api/sandbox/formations/999"`,
    liveRunnable: true
  },
  {
    category: "2. Opérations CRUD & Envoi JSON",
    badge: "Idempotency-Key",
    title: "2.6 — Requête POST critique protégée contre les doublons (Idempotency-Key)",
    desc: "Envoie une clé d'idempotence unique dans les en-têtes pour garantir qu'un réessai réseau ne crée pas de doublon.",
    cmd: `curl -i -X POST "http://127.0.0.1:5000/api/sandbox/wall" \\\n  -H "Content-Type: application/json" \\\n  -H "Idempotency-Key: tx-2026-99812" \\\n  -d '{"auteur": "Stagiaire ISGP", "message": "Test curl validé avec succès."}'`,
    liveRunnable: true
  },

  // ================= 3. AUTHENTIFICATION & SÉCURITÉ =================
  {
    category: "3. Authentification & Sécurité",
    badge: "X-API-Key",
    title: "3.1 — Authentification Machine-à-Machine par Clé API (X-API-Key)",
    desc: "Transmet la clé secrète dans l'en-tête HTTP X-API-Key (ne jamais la passer dans l'URL !).",
    cmd: `curl -i -X GET "http://127.0.0.1:5000/api/sandbox/admin-stats" \\\n  -H "X-API-Key: isgp-secret-2026"`,
    liveRunnable: true
  },
  {
    category: "3. Authentification & Sécurité",
    badge: "Login -> Token",
    title: "3.2 — Émission d'un Bearer Token signé (POST /auth/token)",
    desc: "Envoie les identifiants JSON en POST pour obtenir un jeton signé temporaire (access_token).",
    cmd: `curl -i -X POST "http://127.0.0.1:5000/api/sandbox/auth/token" \\\n  -H "Content-Type: application/json" \\\n  -d '{"identifiant": "stagiaire", "mot_de_passe": "isgp2026"}'`,
    liveRunnable: true
  },
  {
    category: "3. Authentification & Sécurité",
    badge: "Bearer Token",
    title: "3.3 — Appeler une route protégée avec Authorization: Bearer <token>",
    desc: "Présente le jeton signé dans l'en-tête standard RFC 6750 Authorization: Bearer.",
    cmd: `curl -i -X GET "http://127.0.0.1:5000/api/sandbox/auth/profil" \\\n  -H "Authorization: Bearer <COLLER_VOTRE_TOKEN_ICI>"`,
    liveRunnable: true
  },
  {
    category: "3. Authentification & Sécurité",
    badge: "-u (Basic Auth)",
    title: "3.4 — Authentification HTTP Basic (-u identifiant:mot_de_passe)",
    desc: "L'option -u encode automatiquement 'identifiant:mot_de_passe' en Base64 dans l'en-tête 'Authorization: Basic ...'.",
    cmd: `curl -v -u "stagiaire:isgp2026" "http://127.0.0.1:5000/api/sandbox/bonjour"`,
    liveRunnable: true
  },
  {
    category: "3. Authentification & Sécurité",
    badge: "CORS Preflight",
    title: "3.5 — Tester la politique CORS d'une API (Requête OPTIONS Preflight)",
    desc: "Simule la vérification CORS d'un navigateur Web en envoyant les en-têtes Origin et Access-Control-Request-Method.",
    cmd: `curl -i -X OPTIONS "http://127.0.0.1:5000/api/sandbox/formations" \\\n  -H "Origin: http://localhost:3000" \\\n  -H "Access-Control-Request-Method: POST"`,
    liveRunnable: true
  },
  {
    category: "3. Authentification & Sécurité",
    badge: "-k / --insecure",
    title: "3.6 — Ignorer un certificat HTTPS/TLS auto-signé en test local (-k)",
    desc: "Permet d'interroger un serveur HTTPS de développement local dont le certificat n'est pas signé par une autorité publique.",
    cmd: `curl -k -i "https://localhost:8443/api/health/live"`,
    liveRunnable: false
  },

  // ================= 4. FICHIERS, FORMULAIRES & TÉLÉCHARGEMENT =================
  {
    category: "4. Fichiers, Formulaires & Téléchargement",
    badge: "-d @fichier.json",
    title: "4.1 — Envoyer un fichier JSON stocké sur le disque (-d @payload.json)",
    desc: "Le préfixe @ indique à curl de lire le contenu du fichier payload.json comme corps de requête (évite tout problème de guillemets).",
    cmd: `curl -i -X POST "http://127.0.0.1:5000/api/sandbox/formations" \\\n  -H "Content-Type: application/json" \\\n  -d @payload.json`,
    liveRunnable: false
  },
  {
    category: "4. Fichiers, Formulaires & Téléchargement",
    badge: "-F (Multipart Upload)",
    title: "4.2 — Uploader un fichier PDF/Image (multipart/form-data avec -F)",
    desc: "L'option -F construit une requête multipart/form-data permettant d'envoyer un fichier binaire (@rapport.pdf) et des champs texte.",
    cmd: `curl -i -X POST "http://127.0.0.1:5000/api/upload" \\\n  -F "fichier=@rapport_isgp.pdf" \\\n  -F "description=Support de cours"`,
    liveRunnable: false
  },
  {
    category: "4. Fichiers, Formulaires & Téléchargement",
    badge: "-L -o (Download)",
    title: "4.3 — Télécharger un fichier (-o) en suivant les redirections 301/302 (-L)",
    desc: "Télécharge la Collection Postman de l'API et l'enregistre dans le fichier local collection.json.",
    cmd: `curl -L -o collection.json "http://127.0.0.1:5000/api/download/postman-collection"`,
    liveRunnable: false
  },
  {
    category: "4. Fichiers, Formulaires & Téléchargement",
    badge: "-c / -b (Cookies)",
    title: "4.4 — Sauvegarder (-c) et réutiliser (-b) les Cookies de session HTTP",
    desc: "Enregistre les cookies Set-Cookie reçus lors du login dans cookies.txt (-c) puis les renvoie aux appels suivants (-b).",
    cmd: `# 1. Sauvegarder les cookies dans cookies.txt :\ncurl -c cookies.txt -X POST "http://127.0.0.1:5000/login" -d "user=stagiaire"\n\n# 2. Renvoyer les cookies sauvegardés :\ncurl -b cookies.txt "http://127.0.0.1:5000/espace-membre"`,
    liveRunnable: false
  },

  // ================= 5. PERFORMANCE, TIMEOUTS, RETRIES & SCRIPTING =================
  {
    category: "5. Performance, Timeouts, Retries & Scripting",
    badge: "Timeouts (-m)",
    title: "5.1 — Imposer des Timeouts stricts de connexion et d'exécution (--connect-timeout / -m)",
    desc: "Abandonne si la connexion TCP dépasse 2 secondes (--connect-timeout 2) ou si la réponse totale dépasse 5 secondes (-m 5).",
    cmd: `curl -i --connect-timeout 2 -m 5 "http://127.0.0.1:5000/api/sandbox/calcul-tva?ht=2500&taux=19"`,
    liveRunnable: true
  },
  {
    category: "5. Performance, Timeouts, Retries & Scripting",
    badge: "Chronométrage (-w)",
    title: "5.2 — Mesurer la latence détaillée (DNS, TCP, TTFB, Temps Total avec -w)",
    desc: "Affiche une ventilation chronométrique précise de la requête grâce aux variables de formatage --write-out (-w).",
    cmd: `curl -s -w "\\nCode HTTP : %{http_code}\\nTemps DNS : %{time_namelookup}s\\nTemps TCP : %{time_connect}s\\nTemps TTFB: %{time_starttransfer}s\\nTotal     : %{time_total}s\\n" \\\n  "http://127.0.0.1:5000/api/sandbox/formations"`,
    liveRunnable: true
  },
  {
    category: "5. Performance, Timeouts, Retries & Scripting",
    badge: "Pipe JSON (jq / python)",
    title: "5.3 — Formater et filtrer la sortie JSON en terminal (| python3 -m json.tool ou | jq)",
    desc: "Utilise -s (silencieux) pour envoyer le JSON brut dans le formateur intégré de Python ou dans l'outil jq.",
    cmd: `# Avec le module standard Python (installé partout) :\ncurl -s "http://127.0.0.1:5000/api/sandbox/formations" | python3 -m json.tool\n\n# Avec jq (extraire uniquement les titres des formations) :\ncurl -s "http://127.0.0.1:5000/api/sandbox/formations" | jq '.formations[].titre'`,
    liveRunnable: false
  },
  {
    category: "5. Performance, Timeouts, Retries & Scripting",
    badge: "Chaînage Auth -> API",
    title: "5.4 — Script Bash : Capturer le Bearer Token dans une variable et appeler une route protégée",
    desc: "Automatise en une seule ligne l'obtention du jeton sur /auth/token, son extraction et son injection dans Authorization: Bearer.",
    cmd: `TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/api/sandbox/auth/token" \\\n  -H "Content-Type: application/json" \\\n  -d '{"identifiant":"stagiaire","mot_de_passe":"isgp2026"}' \\\n  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")\n\ncurl -i -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:5000/api/sandbox/auth/profil"`,
    liveRunnable: false
  }
];

let FILTERED_CHEATSHEET = [];

function renderCurlCheatsheet() {
  const grid = document.getElementById("curl-cheatsheet-grid");
  if (!grid) return;

  const q = (document.getElementById("curl-cheatsheet-search")?.value || "").toLowerCase().trim();
  const cat = document.getElementById("curl-cheatsheet-category")?.value || "ALL";

  FILTERED_CHEATSHEET = CURL_CHEATSHEET_ITEMS.filter((item) => {
    const matchCat = cat === "ALL" || item.category === cat;
    const matchQ =
      !q ||
      item.title.toLowerCase().includes(q) ||
      item.badge.toLowerCase().includes(q) ||
      item.desc.toLowerCase().includes(q) ||
      item.cmd.toLowerCase().includes(q);
    return matchCat && matchQ;
  });

  if (FILTERED_CHEATSHEET.length === 0) {
    grid.innerHTML = `<div class="card"><p class="muted-small">Aucune commande curl ne correspond à ce filtre.</p></div>`;
    return;
  }

  grid.innerHTML = FILTERED_CHEATSHEET.map((item, idx) => {
    const testBtn = item.liveRunnable
      ? `<button class="btn-primary btn-xs" onclick="runCheatsheetItem(${idx})">Tester en direct</button>`
      : `<span class="category-tag">Terminal Système</span>`;
    return `
      <div class="glossary-card">
        <div class="glossary-top">
          <h4>${escapeHtml(item.title)}</h4>
          <span class="category-tag">${escapeHtml(item.badge)}</span>
        </div>
        <p class="glossary-short">${escapeHtml(item.desc)}</p>
        <pre class="code-block-mini" style="margin-top: auto;">${escapeHtml(item.cmd)}</pre>
        <div class="label-row" style="margin-top: 6px; margin-bottom: 0;">
          <span class="muted-small">${escapeHtml(item.category)}</span>
          <div class="btn-group">
            <button class="btn-xs" onclick="copyCheatsheetItem(${idx})">Copier</button>
            ${testBtn}
          </div>
        </div>
      </div>
    `;
  }).join("");
}

function copyCheatsheetItem(idx) {
  const item = FILTERED_CHEATSHEET[idx];
  if (item) copyText(item.cmd);
}

function runCheatsheetItem(idx) {
  const item = FILTERED_CHEATSHEET[idx];
  if (!item) return;
  const input = document.getElementById("curl-lab-input");
  if (input) {
    input.value = item.cmd;
    window.scrollTo({ top: 0, behavior: "smooth" });
    executeLiveCurlCommand();
  }
}

// ============================================================================
// 10. LABORATOIRE NGINX LOAD BALANCER & 4 INSTANCES PAR FRAMEWORK
// ============================================================================
async function loadNginxClusterTab() {
  try {
    const fw = getActiveFramework();
    const res = await fetch(`/api/nginx-cluster/state?framework=${encodeURIComponent(fw)}`, {
      headers: { "X-Active-Framework": fw }
    });
    const data = await res.json();
    if (data.files) {
      const confEl = document.getElementById("code-nginx-conf");
      const pyEl = document.getElementById("code-nginx-flask");
      const shEl = document.getElementById("code-nginx-sh");
      const dcEl = document.getElementById("code-nginx-compose");
      if (confEl) confEl.textContent = data.files.nginx_conf;
      if (pyEl) pyEl.textContent = data.files.instance_py;
      if (shEl) shEl.textContent = data.files.start_sh;
      if (dcEl) dcEl.textContent = data.files.docker_compose;
    }
    if (data.state) {
      renderNginxClusterUI(data.state);
    }
  } catch (err) {
    console.error("Erreur lors du chargement du cluster Nginx :", err);
  }
}

function renderNginxClusterUI(state) {
  const summaryEl = document.getElementById("nginx-summary-banner");
  const gridEl = document.getElementById("nginx-nodes-grid");
  const logsEl = document.getElementById("nginx-live-logs");
  const algoEl = document.getElementById("nginx-algo-select");

  if (algoEl && state.algorithm) {
    algoEl.value = state.algorithm;
  }

  const totalDynamic = state.dynamic_requests_proxied || 0;
  const totalStatic = state.static_requests_served || 0;
  const totalOffload = state.uploads_offloaded || 0;
  const total413 = state.rejected_413_edge || 0;
  const totalXAccel = state.x_accel_downloads || 0;
  const upCount = state.nodes.filter((n) => n.status === "UP").length;

  if (summaryEl) {
    summaryEl.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(205px, 1fr)); gap: 10px;">
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #1e3a5f; padding: 12px 14px; border-radius: 4px;">
          <div style="font-size: 12.5px; color: #1e3a5f; font-weight: 700; text-transform: uppercase;">Fichiers Statiques (/static/)</div>
          <div style="font-size: 22px; font-weight: 700; color: #0f172a; margin: 4px 0;">${totalStatic} servis par Nginx</div>
          <div style="font-size: 13px; color: #334155;">0% CPU Python sollicité (<code>sendfile on</code>)</div>
        </div>
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #15803d; padding: 12px 14px; border-radius: 4px;">
          <div style="font-size: 12.5px; color: #14532d; font-weight: 700; text-transform: uppercase;">Requêtes API Dynamiques (/api/)</div>
          <div style="font-size: 22px; font-weight: 700; color: #0f172a; margin: 4px 0;">${totalDynamic} réparties</div>
          <div style="font-size: 13px; color: #14532d;">Instances actives : <strong>${upCount} / 4 UP</strong></div>
        </div>
        <div style="background: #faf5ff; border: 1px solid #e9d5ff; border-left: 4px solid #7c3aed; padding: 12px 14px; border-radius: 4px;">
          <div style="font-size: 12.5px; color: #581c87; font-weight: 700; text-transform: uppercase;">Délégation Fichiers Nginx</div>
          <div style="font-size: 16px; font-weight: 700; color: #0f172a; margin: 4px 0;">
            ${totalOffload} Offloads | ${totalXAccel} X-Accel | ${total413} Bloqués 413
          </div>
          <div style="font-size: 12.5px; color: #4c1d95;"><code>$request_body_file</code> &amp; <code>client_max_body_size</code></div>
        </div>
        <div style="background: ${state.errors_502 > 0 ? '#fef2f2' : '#f8fafc'}; border: 1px solid ${state.errors_502 > 0 ? '#fecaca' : '#e2e8f0'}; border-left: 4px solid ${state.errors_502 > 0 ? '#b91c1c' : '#64748b'}; padding: 12px 14px; border-radius: 4px;">
          <div style="font-size: 12.5px; color: #334155; font-weight: 700; text-transform: uppercase;">Tolérance aux Pannes (Failover)</div>
          <div style="font-size: 22px; font-weight: 700; color: #0f172a; margin: 4px 0;">${state.errors_502} erreur(s) 502</div>
          <div style="font-size: 13px; color: #475569;">502 uniquement si les 4 instances tombent simultanément</div>
        </div>
      </div>
    `;
  }

  if (gridEl) {
    gridEl.innerHTML = state.nodes
      .map((n) => {
        const isUp = n.status === "UP";
        const pct = totalDynamic > 0 ? Math.round((n.requests / totalDynamic) * 100) : 0;
        const borderColor = isUp ? "#15803d" : "#b91c1c";
        const bgBadge = isUp ? "#dcfce7" : "#fee2e2";
        const colorBadge = isUp ? "#14532d" : "#7f1d1d";
        return `
          <div style="background: #ffffff; border: 1px solid #cbd5e1; border-top: 4px solid ${borderColor}; border-radius: 4px; padding: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <strong style="font-size: 15.5px; color: #0f172a;">${escapeHtml(n.id)}</strong>
              <span style="background: ${bgBadge}; color: ${colorBadge}; font-weight: 700; font-size: 12px; padding: 2px 8px; border-radius: 4px;">
                ${isUp ? "UP (Actif)" : "DOWN (En Panne)"}
              </span>
            </div>
            <div style="font-family: monospace; font-size: 13px; color: #334155; margin-bottom: 8px;">
              <div>Adresse : <strong>${escapeHtml(n.addr)}</strong></div>
              <div>Processus : <code>PID ${n.pid}</code> | Poids : <code>weight=${n.weight}</code></div>
            </div>
            <div style="margin: 10px 0;">
              <div style="display: flex; justify-content: space-between; font-size: 13.5px; font-weight: 600; margin-bottom: 4px;">
                <span>Requêtes traitées : ${n.requests}</span>
                <span>${pct}%</span>
              </div>
              <div style="height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden;">
                <div style="width: ${pct}%; height: 100%; background: ${isUp ? '#1e3a5f' : '#94a3b8'};"></div>
              </div>
            </div>
            <button
              class="${isUp ? 'btn-secondary' : 'btn-primary'} btn-sm"
              style="width: 100%; margin-top: 6px;"
              onclick="toggleNginxNode(${n.port})"
            >
              ${isUp ? "Simuler Panne (Arrêter :" + n.port + ")" : "Redémarrer l'Instance (:" + n.port + ")"}
            </button>
          </div>
        `;
      })
      .join("");
  }

  if (logsEl) {
    logsEl.textContent = (state.logs || []).join("\n");
  }
}

async function simulateNginxTraffic(type, count) {
  const algo = document.getElementById("nginx-algo-select")?.value || "round_robin";
  const clientIp = document.getElementById("nginx-client-ip")?.value || "197.204.12.88";
  if (count === 0) {
    return;
  }
  try {
    const fw = getActiveFramework();
    const res = await fetch(`/api/nginx-cluster/simulate?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ type, count, algorithm: algo, client_ip: clientIp })
    });
    const data = await res.json();
    if (data.state) {
      renderNginxClusterUI(data.state);
    }
  } catch (err) {
    showToast("Erreur lors de la simulation Nginx : " + err.message);
  }
}

async function toggleNginxNode(port) {
  try {
    const fw = getActiveFramework();
    const res = await fetch(`/api/nginx-cluster/toggle-node?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ port })
    });
    const data = await res.json();
    if (data.state) {
      renderNginxClusterUI(data.state);
    }
  } catch (err) {
    showToast("Erreur lors du changement d'état du nœud : " + err.message);
  }
}

async function resetNginxCluster() {
  try {
    const fw = getActiveFramework();
    const res = await fetch(`/api/nginx-cluster/reset?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "X-Active-Framework": fw }
    });
    const data = await res.json();
    if (data.state) {
      renderNginxClusterUI(data.state);
      showToast("Cluster Nginx et compteurs des 4 instances réinitialisés.");
    }
  } catch (err) {
    showToast("Erreur lors de la réinitialisation : " + err.message);
  }
}

function copyTextById(elementId) {
  const el = document.getElementById(elementId);
  if (el) {
    copyText(el.textContent);
  }
}

// ============================================================================
// 11. LABORATOIRE INTERACTIF SQLITE3, REQUÊTES PRÉPARÉES (? vs %s) & SÉCURITÉ
// ============================================================================
async function loadSqliteLabTab() {
  try {
    const fw = getActiveFramework();
    const res = await fetch(`/api/sqlite-lab/state?framework=${encodeURIComponent(fw)}`, {
      headers: { "X-Active-Framework": fw }
    });
    const data = await res.json();

    const metaEl = document.getElementById("sqlite-engine-meta");
    if (metaEl) {
      metaEl.innerHTML = `
        <span><strong>Moteur C embarqué :</strong> SQLite <code>v${escapeHtml(data.sqlite_version)}</code></span>
        <span>|</span>
        <span><strong>DB-API 2.0 paramstyle :</strong> <code>${escapeHtml(data.paramstyle)}</code> (<code>?</code> positionnel &amp; <code>:nom</code> nommé)</span>
        <span>|</span>
        <span><strong>PRAGMA journal_mode :</strong> <code>${escapeHtml(String(data.journal_mode).toUpperCase())}</code></span>
        <span>|</span>
        <span><strong>Fichier autonome :</strong> <code>${escapeHtml(data.script_path)}</code></span>
      `;
    }

    const handlerEl = document.getElementById("sqlite-lab-handler-code");
    if (handlerEl && data.handler_snippet) {
      handlerEl.textContent = data.handler_snippet;
    }

    const scriptEl = document.getElementById("sqlite-standalone-code");
    if (scriptEl && data.script_code) {
      scriptEl.value = data.script_code;
    }

    renderSqliteLabRows(data.rows || []);
    await runSqliteLabCompare();
  } catch (err) {
    console.error("Erreur chargement laboratoire SQLite :", err);
  }
}

function renderSqliteLabRows(rows) {
  const tbody = document.getElementById("sqlite-live-table-body");
  if (!tbody) return;
  if (!rows.length) {
    tbody.innerHTML = `<tr><td colspan="5" class="muted-small">Aucune ligne présente dans la table formations.</td></tr>`;
    return;
  }
  tbody.innerHTML = rows.map((r) => `
    <tr>
      <td><code>#${r.id}</code></td>
      <td><strong>${escapeHtml(r.titre)}</strong></td>
      <td>${escapeHtml(r.formateur)}</td>
      <td><code>${r.duree_jours} j</code></td>
      <td><span class="status-pill status-neutral">${escapeHtml(r.salle)}</span></td>
    </tr>
  `).join("");
}

function setSqliteFilterPreset(salleVal) {
  const input = document.getElementById("sqlite-filter-salle");
  if (input) {
    input.value = salleVal;
    runSqliteLabCompare();
  }
}

async function runSqliteLabCompare() {
  const salle = document.getElementById("sqlite-filter-salle")?.value ?? "Salle A";
  const tri = document.getElementById("sqlite-filter-tri")?.value ?? "id";
  const fw = getActiveFramework();
  try {
    const res = await fetch(`/api/sqlite-lab/execute?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ action: "select_compare", salle, tri })
    });
    const data = await res.json();

    const safeBox = document.getElementById("sqlite-safe-result");
    if (safeBox) {
      safeBox.innerHTML = `
        <div style="font-size:12.5px; margin-bottom:6px; color:#065f46;">
          <strong>Requête compilée (AST figé) :</strong><br/>
          <code>${escapeHtml(data.safe_sql)}</code>
        </div>
        <div style="font-size:12.5px; margin-bottom:8px; color:#065f46;">
          <strong>Tuple lié (<code>sqlite3_bind_text</code>) :</strong>
          <code>${escapeHtml(JSON.stringify(data.safe_params))}</code>
        </div>
        <div style="font-size:12.5px; font-weight:700; color:#047857; margin-bottom:4px;">
          Résultat : ${data.safe_rows.length} ligne(s) retournée(s)
          ${data.injection_detected ? " — Attaque SQLi neutralisée (traitée comme littéral) !" : ""}
        </div>
        <pre class="code-block-mini" style="margin:0; max-height:140px; overflow-y:auto;">${escapeHtml(JSON.stringify(data.safe_rows, null, 2))}</pre>
      `;
    }

    const unsafeBox = document.getElementById("sqlite-unsafe-result");
    if (unsafeBox) {
      unsafeBox.innerHTML = `
        <div style="font-size:12.5px; margin-bottom:6px; color:#991b1b;">
          <strong>Chaîne concaténée (f-string vulnérable) :</strong><br/>
          <code>${escapeHtml(data.unsafe_sql)}</code>
        </div>
        <div style="font-size:12.5px; font-weight:700; color:#b91c1c; margin-bottom:4px;">
          ${data.unsafe_error
            ? `Erreur syntaxique SQL provoquée : ${escapeHtml(data.unsafe_error)}`
            : `Résultat : ${data.unsafe_rows.length} ligne(s) retournée(s) ${data.injection_detected ? "(FUITE DE TOUTE LA TABLE PAR INJECTION SQL !)" : ""}`
          }
        </div>
        <pre class="code-block-mini" style="margin:0; max-height:140px; overflow-y:auto;">${escapeHtml(JSON.stringify(data.unsafe_rows, null, 2))}</pre>
      `;
    }

    const handlerEl = document.getElementById("sqlite-lab-handler-code");
    if (handlerEl && data.handler_snippet) {
      handlerEl.textContent = data.handler_snippet;
    }
    if (data.rows) {
      renderSqliteLabRows(data.rows);
    }
  } catch (err) {
    showToast("Erreur lors du test SQLite : " + err.message);
  }
}

async function runSqliteLabInsert() {
  const titre = document.getElementById("sqlite-insert-titre")?.value || "Sécurité SQLite & Requêtes Préparées";
  const formateur = document.getElementById("sqlite-insert-formateur")?.value || "Intervenant ISGP";
  const salle = document.getElementById("sqlite-insert-salle")?.value || "Salle A";
  const duree = parseInt(document.getElementById("sqlite-insert-duree")?.value || "4", 10);
  const fw = getActiveFramework();

  try {
    const res = await fetch(`/api/sqlite-lab/execute?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({
        action: "insert_named",
        titre,
        formateur,
        salle,
        duree_jours: duree
      })
    });
    const data = await res.json();
    const txOut = document.getElementById("sqlite-tx-output");
    if (txOut) {
      txOut.textContent = `${data.explanation}\n\nSQL : ${data.sql_executed}\nParamètres : ${JSON.stringify(data.bound_params)}`;
    }
    const handlerEl = document.getElementById("sqlite-lab-handler-code");
    if (handlerEl && data.handler_snippet) {
      handlerEl.textContent = data.handler_snippet;
    }
    if (data.rows) {
      renderSqliteLabRows(data.rows);
    }
    showToast(`Ligne #${data.lastrowid} insérée dans SQLite avec COMMIT.`);
  } catch (err) {
    showToast("Erreur lors de l'insertion SQLite : " + err.message);
  }
}

async function runSqliteLabRollback() {
  const fw = getActiveFramework();
  try {
    const res = await fetch(`/api/sqlite-lab/execute?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ action: "rollback_demo" })
    });
    const data = await res.json();
    const txOut = document.getElementById("sqlite-tx-output");
    if (txOut) {
      txOut.textContent = `${data.explanation}\n\nTrace Transactionnelle :\n${data.sql_executed}`;
    }
    showToast("Démonstration ROLLBACK ACID exécutée.");
  } catch (err) {
    showToast("Erreur lors du test ROLLBACK : " + err.message);
  }
}

async function runSqliteLabFindOne(idVal) {
  const fw = getActiveFramework();
  const targetId = idVal !== undefined ? idVal : parseInt(document.getElementById("sqlite-findone-id")?.value || "1", 10);
  try {
    const res = await fetch(`/api/sqlite-lab/execute?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ action: "find_one", id: targetId })
    });
    const data = await res.json();
    const txOut = document.getElementById("sqlite-tx-output");
    if (txOut) {
      txOut.textContent = `${data.explanation}\n\nSQL : ${data.sql_executed}\nTuple lié : (${targetId},)\nRésultat fetchone() : ${JSON.stringify(data.row)}`;
    }
    const handlerEl = document.getElementById("sqlite-lab-handler-code");
    if (handlerEl && data.handler_snippet) {
      handlerEl.textContent = data.handler_snippet;
    }
    showToast(data.found ? `fetchone() -> Formation #${targetId} trouvée (200 OK)` : `fetchone() -> None (404 Not Found)`);
  } catch (err) {
    showToast("Erreur lors du test find_one : " + err.message);
  }
}

async function runSqliteStandaloneServer() {
  const textarea = document.getElementById("sqlite-standalone-code");
  const out = document.getElementById("sqlite-standalone-output");
  if (!textarea || !out) return;
  _clearLivePythonPoll();
  out.textContent = "Démarrage du serveur SQLite autonome et exécution des auto-tests...";
  try {
    const fw = getActiveFramework();
    const res = await fetch(`/api/python/run?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ code: textarea.value })
    });
    const data = await res.json();
    _renderLiveLoopBar("sqlite", data);
    if (data.running) {
      out.textContent = data.output || "(Boucle serveur SQLite démarrée)";
      _startLivePythonPoll("sqlite", out, null);
    } else if (data.error) {
      out.textContent = `[Erreur d'exécution — Code ${data.exit_code}]\n${data.error}`;
    } else {
      out.textContent = data.output || "(Aucune sortie console)";
    }
  } catch (err) {
    out.textContent = "Erreur réseau : " + err.message;
  }
}

// ============================================================================
// 12. LABORATOIRE AVANCÉ : TEMPS RÉEL (SSE/WS), MULTIPART, JOBS 202 & ETAG
// ============================================================================
let _activeSseSource = null;
let _jobsPollTimer = null;
let _clientRememberedEtag = "";

async function loadAdvancedRealtimeTab() {
  const fw = getActiveFramework();
  try {
    const res = await fetch(`/api/advanced-lab/state?framework=${encodeURIComponent(fw)}`, {
      headers: { "X-Active-Framework": fw }
    });
    const data = await res.json();
    const pathEl = document.getElementById("realtime-standalone-path");
    if (pathEl && data.script_path) {
      pathEl.textContent = data.script_path;
    }
    const codeEl = document.getElementById("realtime-standalone-code");
    if (codeEl && data.script_code && !codeEl.dataset.edited) {
      codeEl.value = data.script_code;
    }
    if (data.etag && !_clientRememberedEtag) {
      _clientRememberedEtag = data.etag;
    }
    renderAdvancedEtagState(data.etag, data.resource, null);
    renderAdvancedJobsRows(data.jobs || []);
  } catch (err) {
    console.error("Erreur lors du chargement de l'onglet Temps Réel & Cache :", err);
  }
}

function stopLiveSseDemo() {
  if (_activeSseSource) {
    _activeSseSource.close();
    _activeSseSource = null;
  }
  const statusEl = document.getElementById("realtime-sse-status");
  if (statusEl) {
    statusEl.textContent = "Flux SSE arrêté.";
  }
}

function startLiveSseDemo() {
  stopLiveSseDemo();
  const fw = getActiveFramework();
  const outEl = document.getElementById("realtime-sse-output");
  const statusEl = document.getElementById("realtime-sse-status");
  if (!outEl) return;

  outEl.textContent = `[Connexion EventSource ouverte] GET /api/advanced-lab/sse-demo?framework=${fw}\nAccept: text/event-stream\n------------------------------------------------------------\n`;
  if (statusEl) {
    statusEl.textContent = "Canal HTTP text/event-stream actif (réception des trames en direct)...";
  }

  const es = new EventSource(`/api/advanced-lab/sse-demo?framework=${encodeURIComponent(fw)}`);
  _activeSseSource = es;

  es.addEventListener("telemetry", (ev) => {
    let parsed = null;
    try {
      parsed = JSON.parse(ev.data);
    } catch (e) {
      parsed = { message: ev.data };
    }
    const rawWire = `id: ${ev.lastEventId || "sse"}\nevent: telemetry\ndata: ${ev.data}\n\n`;
    outEl.textContent += rawWire;
    outEl.scrollTop = outEl.scrollHeight;
    if (parsed && parsed.id_trame === 5) {
      es.close();
      _activeSseSource = null;
      if (statusEl) {
        statusEl.textContent = "5/5 trames SSE reçues proprement (Last-Event-ID mémorisé : " + (ev.lastEventId || "sse-5") + ").";
      }
      showToast("Flux SSE terminé avec succès (5 événements reçus).");
    }
  });

  es.onerror = () => {
    es.close();
    _activeSseSource = null;
    if (statusEl) {
      statusEl.textContent = "Connexion SSE fermée par le serveur en fin de séquence.";
    }
  };
}

async function runMultipartInspector(scenario) {
  const fw = getActiveFramework();
  const wireEl = document.getElementById("realtime-multipart-wire");
  const verdictEl = document.getElementById("realtime-multipart-verdict");
  try {
    const res = await fetch(`/api/advanced-lab/multipart-inspect?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ scenario })
    });
    const data = await res.json();
    if (wireEl) {
      wireEl.textContent = data.wire_frame || "";
    }
    if (verdictEl) {
      const ok = data.http_status === 201;
      const bg = ok ? "#f0fdf4" : "#fef2f2";
      const border = ok ? "#15803d" : "#b91c1c";
      const textCol = ok ? "#14532d" : "#7f1d1d";
      verdictEl.innerHTML = `
        <div style="background:${bg}; border:1px solid ${border}; border-left:5px solid ${border}; padding:12px 14px; border-radius:4px; color:${textCol};">
          <div style="font-weight:700; font-size:14.5px; margin-bottom:6px;">Code HTTP simulé : ${data.http_status} — ${escapeHtml(data.verdict)}</div>
          <div style="font-size:13px; line-height:1.55;">
            <strong>Nom brut envoyé par le client :</strong> <code>${escapeHtml(data.raw_filename)}</code><br/>
            <strong>Nom stocké après UUID + secure_filename :</strong> <code>${escapeHtml(data.sanitized_filename)}</code><br/>
            <strong>MIME déclaré vs Magic Bytes inspectés :</strong> <code>${escapeHtml(data.claimed_mime)}</code> | Octets d'en-tête réels : <code>[${escapeHtml(data.magic_bytes_hex)}]</code> | Taille : <strong>${(data.size_bytes / 1024).toFixed(1)} Ko</strong>
          </div>
        </div>
      `;
    }
    showToast(`Inspection Multipart -> HTTP ${data.http_status}`);
  } catch (err) {
    showToast("Erreur lors de l'inspection Multipart : " + err.message);
  }
}

function renderAdvancedJobsRows(jobs) {
  const tbody = document.getElementById("realtime-jobs-tbody");
  if (!tbody) return;
  if (!jobs || jobs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="muted-small" style="text-align:center; padding:12px;">Aucune tâche d'arrière-plan lancée pour l'instant. Cliquez sur « Déclencher POST -> 202 Accepted » ci-dessus.</td></tr>`;
    return;
  }
  tbody.innerHTML = jobs
    .map((j) => {
      const done = j.progression >= 100;
      const badgeBg = done ? "#dcfce7" : "#dbeafe";
      const badgeCol = done ? "#14532d" : "#1e3a8a";
      return `
        <tr>
          <td><code>${escapeHtml(j.job_id)}</code></td>
          <td><code>${escapeHtml(j.request_id || "-")}</code></td>
          <td>${escapeHtml(j.sujet)}</td>
          <td><span style="font-size:12px; color:#334155;">${escapeHtml(j.moteur)}</span></td>
          <td>
            <span style="background:${badgeBg}; color:${badgeCol}; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:700;">
              ${escapeHtml(j.statut)}
            </span>
          </td>
          <td>${j.resultat ? `<code>${escapeHtml(j.resultat)}</code>` : `<span class="muted-small">Calcul en cours...</span>`}</td>
        </tr>
      `;
    })
    .join("");
}

async function pollAsyncJobsTable() {
  const fw = getActiveFramework();
  try {
    const res = await fetch(`/api/advanced-lab/jobs?framework=${encodeURIComponent(fw)}`, {
      headers: { "X-Active-Framework": fw }
    });
    const data = await res.json();
    const jobs = data.jobs || [];
    renderAdvancedJobsRows(jobs);
    const anyRunning = jobs.some((j) => j.progression < 100);
    if (!anyRunning && _jobsPollTimer) {
      clearInterval(_jobsPollTimer);
      _jobsPollTimer = null;
    }
  } catch (err) {
    if (_jobsPollTimer) {
      clearInterval(_jobsPollTimer);
      _jobsPollTimer = null;
    }
  }
}

async function triggerAsyncJob202() {
  const fw = getActiveFramework();
  const sujetInput = document.getElementById("realtime-job-sujet");
  const sujet = sujetInput?.value || "Génération PDF & Signature SHA-256 des Attestations ISGP";
  const bannerEl = document.getElementById("realtime-job-202-banner");
  try {
    const res = await fetch(`/api/advanced-lab/jobs?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ sujet })
    });
    const data = await res.json();
    if (bannerEl) {
      bannerEl.innerHTML = `
        <div style="background:#eff6ff; border:1px solid #93c5fd; border-left:5px solid #1d4ed8; padding:10px 14px; border-radius:4px; margin-bottom:10px; font-size:13.5px; color:#1e3a8a;">
          <strong>Réponse HTTP immédiate : ${data.http_status} Accepted</strong> |
          En-tête <code>Location: ${escapeHtml(data.location)}</code> |
          Corrélation <code>X-Request-ID: ${escapeHtml(data.request_id)}</code><br/>
          <span style="color:#334155;">Le worker HTTP est déjà libre pour d'autres clients pendant que la tâche progresse de 0% à 100% ci-dessous :</span>
        </div>
      `;
    }
    await pollAsyncJobsTable();
    if (_jobsPollTimer) clearInterval(_jobsPollTimer);
    _jobsPollTimer = setInterval(pollAsyncJobsTable, 550);
    showToast(`HTTP 202 Accepted -> ${data.job?.job_id}`);
  } catch (err) {
    showToast("Erreur lors du lancement de la tâche 202 : " + err.message);
  }
}

function renderAdvancedEtagState(serverEtag, resource, actionResult) {
  const clientEtagInput = document.getElementById("realtime-client-etag");
  if (clientEtagInput && _clientRememberedEtag && !clientEtagInput.dataset.manual) {
    clientEtagInput.value = _clientRememberedEtag;
  }
  const serverBox = document.getElementById("realtime-etag-server-box");
  if (serverBox && resource) {
    serverBox.innerHTML = `
      <div style="font-size:13px; line-height:1.6;">
        <strong>Ressource Serveur (#${resource.id}) :</strong> ${escapeHtml(resource.titre)}<br/>
        <strong>Salle :</strong> <code>${escapeHtml(resource.salle)}</code> |
        <strong>Places :</strong> <code>${resource.places}</code> |
        <strong>Version métier :</strong> <code>v${resource.version_metier}</code><br/>
        <strong>ETag Serveur actuel (SHA-256) :</strong> <code style="background:#fef3c7; color:#92400e; font-weight:700; padding:2px 6px;">${escapeHtml(serverEtag || "")}</code><br/>
        <span class="muted-small">${escapeHtml(resource.derniere_modification || "")}</span>
      </div>
    `;
  }
  const logBox = document.getElementById("realtime-etag-http-log");
  if (logBox && actionResult) {
    const code = actionResult.http_status;
    let color = "#1e3a8a";
    let bg = "#eff6ff";
    if (code === 304 || code === 200) {
      color = "#14532d";
      bg = "#f0fdf4";
    } else if (code === 412 || code === 428) {
      color = "#7f1d1d";
      bg = "#fef2f2";
    }
    logBox.innerHTML = `
      <div style="background:${bg}; border:1px solid ${color}; border-left:5px solid ${color}; padding:12px 14px; border-radius:4px; color:${color};">
        <div style="font-weight:700; font-size:14.5px; margin-bottom:4px;">HTTP ${code} — ${escapeHtml(actionResult.status_text || "")}</div>
        <div style="font-size:13px; margin-bottom:8px;">${escapeHtml(actionResult.explanation || "")}</div>
        ${actionResult.bytes_transferred !== undefined ? `<div style="font-size:12.5px;"><strong>Octets de corps JSON transférés sur le réseau :</strong> <code>${actionResult.bytes_transferred} octets</code></div>` : ""}
        ${actionResult.request_headers ? `<pre class="code-block-mini" style="margin-top:8px; margin-bottom:0;">Requête -> ${escapeHtml(JSON.stringify(actionResult.request_headers))}\nRéponse <- ${escapeHtml(JSON.stringify(actionResult.response_headers || {}))}</pre>` : ""}
      </div>
    `;
  }
}

async function runEtagAction(mode) {
  const fw = getActiveFramework();
  const clientInput = document.getElementById("realtime-client-etag");
  const salleInput = document.getElementById("realtime-etag-salle");
  const placesInput = document.getElementById("realtime-etag-places");
  const currentClientEtag = (clientInput?.value || _clientRememberedEtag || "").trim();

  const payload = { mode };
  if (mode === "get_conditional") {
    payload.if_none_match = currentClientEtag;
  } else if (mode === "put_if_match") {
    payload.if_match = currentClientEtag;
    payload.salle = salleInput?.value || "Salle Cybersécurité Oran";
    payload.places = parseInt(placesInput?.value || "35", 10);
  }

  try {
    const res = await fetch(`/api/advanced-lab/etag?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    // Si le client fait un GET frais, un GET 200 mis à jour ou un PUT 200 réussi, son cache local mémorise le nouvel ETag.
    // En revanche, si c'est le Collègue B qui modifie le serveur en arrière-plan ("simulate_concurrent_writer")
    // ou si le PUT échoue en 412, le client garde exprès son ancien ETag en main jusqu'à ce qu'il refasse un GET !
    if (mode === "get_fresh" || (mode === "get_conditional" && data.http_status === 200) || (mode === "put_if_match" && data.http_status === 200)) {
      _clientRememberedEtag = data.etag;
      if (clientInput) {
        clientInput.dataset.manual = "";
        clientInput.value = data.etag;
      }
    }
    renderAdvancedEtagState(data.etag, data.resource, data);
    showToast(`Simulation ETag -> HTTP ${data.http_status}`);
  } catch (err) {
    showToast("Erreur lors du test ETag : " + err.message);
  }
}

async function runAdvancedStandaloneServer() {
  const textarea = document.getElementById("realtime-standalone-code");
  const out = document.getElementById("realtime-standalone-output");
  if (!textarea || !out) return;
  _clearLivePythonPoll();
  out.textContent = "Démarrage du laboratoire autonome Temps Réel, Upload & Cache...";
  try {
    const fw = getActiveFramework();
    const res = await fetch(`/api/python/run?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ code: textarea.value })
    });
    const data = await res.json();
    _renderLiveLoopBar("realtime", data);
    if (data.running) {
      out.textContent = data.output || "(Boucle serveur Temps Réel & Cache démarrée)";
      _startLivePythonPoll("realtime", out, null);
    } else if (data.error) {
      out.textContent = `[Erreur d'exécution — Code ${data.exit_code}]\n${data.error}`;
    } else {
      out.textContent = data.output || "(Aucune sortie console)";
    }
  } catch (err) {
    out.textContent = "Erreur réseau : " + err.message;
  }
}

// ============================================================================
// 13. ONGLET ARCHITECTURE, CONTRATS API, NORD-SUD / EST-OUEST, OAUTH2 & SWAGGER
// ============================================================================
let _architectureTabInitialized = false;

async function loadArchitectureTab() {
  if (!_architectureTabInitialized) {
    _architectureTabInitialized = true;
    await Promise.all([
      runArchitectureOauthSim("pkce_north_south", true),
      loadArchitectureOpenApiCompare(getActiveFramework(), true)
    ]);
  }
}

async function runArchitectureOauthSim(scenario, silent = false) {
  const fw = getActiveFramework();
  const out = document.getElementById("arch-oauth-sim-output");
  if (!out) return;

  document.querySelectorAll(".arch-oauth-scenario-btn").forEach((btn) => {
    const active = btn.dataset.scenario === scenario;
    btn.classList.toggle("btn-primary", active);
    btn.classList.toggle("btn-secondary", !active);
  });

  try {
    const res = await fetch(`/api/architecture-lab/oauth-flow?framework=${encodeURIComponent(fw)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Active-Framework": fw },
      body: JSON.stringify({ scenario })
    });
    const data = await res.json();
    const isOk = data.http_status >= 200 && data.http_status < 300;
    const badgeColor = isOk ? "#15803d" : "#b91c1c";
    const badgeBg = isOk ? "#f0fdf4" : "#fef2f2";
    const checksHtml = (data.security_checks || [])
      .map((c) => `<li style="margin-bottom:5px; line-height:1.5;">${escapeHtml(c)}</li>`)
      .join("");

    out.innerHTML = `
      <div style="background:${badgeBg}; border:1px solid ${badgeColor}; border-left:5px solid ${badgeColor}; padding:12px 14px; border-radius:6px; margin-bottom:12px;">
        <div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:8px; margin-bottom:6px;">
          <strong style="color:${badgeColor}; font-size:14.5px;">HTTP ${data.http_status} — ${escapeHtml(data.verdict || "")}</strong>
          <span class="badge-pill" style="background:${badgeColor}; color:#fff; border:none;">${escapeHtml(data.grant_type || "")}</span>
        </div>
        <div style="font-size:13px; color:#1e293b;"><strong>Flux réseau inspecté :</strong> ${escapeHtml(data.direction || "")}</div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(290px, 1fr)); gap:12px;">
        <div>
          <div style="font-size:12.5px; font-weight:700; color:#334155; margin-bottom:6px;">Jeton JWT décodé (Header + Claims OAuth2 / RFC 8693)</div>
          <pre class="code-block-mini" style="margin:0; max-height:280px; overflow:auto;">// Header JWS\n${escapeHtml(JSON.stringify(data.jwt_header || {}, null, 2))}\n\n// Payload (Claims)\n${escapeHtml(JSON.stringify(data.jwt_payload || {}, null, 2))}</pre>
        </div>
        <div>
          <div style="font-size:12.5px; font-weight:700; color:#334155; margin-bottom:6px;">Chaîne de contrôle Zero-Trust côté Resource Server</div>
          <ul style="margin:0; padding:12px 16px 12px 28px; background:#f8fafc; border:1px solid #cbd5e1; border-radius:6px; font-size:13px; color:#1e293b;">
            ${checksHtml}
          </ul>
        </div>
      </div>
    `;
    if (!silent) {
      showToast(`Simulation OAuth2 (${scenario}) -> HTTP ${data.http_status}`);
    }
  } catch (err) {
    out.innerHTML = `<div style="color:#b91c1c;">Erreur lors de la simulation OAuth2 : ${escapeHtml(err.message)}</div>`;
  }
}

async function loadArchitectureOpenApiCompare(targetFw, silent = false) {
  const fw = getActiveFramework();
  const chosen = (targetFw || fw || "flask").toLowerCase();
  const yamlBox = document.getElementById("arch-openapi-yaml-code");
  const metaBox = document.getElementById("arch-openapi-fw-meta");
  const codeBox = document.getElementById("arch-openapi-fw-code");
  if (!yamlBox || !metaBox || !codeBox) return;

  document.querySelectorAll(".arch-openapi-fw-btn").forEach((btn) => {
    const active = btn.dataset.fw === chosen;
    btn.classList.toggle("btn-primary", active);
    btn.classList.toggle("btn-secondary", !active);
  });

  try {
    const res = await fetch(
      `/api/architecture-lab/openapi-compare?target_fw=${encodeURIComponent(chosen)}&framework=${encodeURIComponent(fw)}`,
      { headers: { "X-Active-Framework": fw } }
    );
    const data = await res.json();
    yamlBox.textContent = data.openapi_yaml || "";
    const detail = data.framework_detail || {};
    metaBox.innerHTML = `
      <div style="font-weight:700; color:#0f172a; margin-bottom:4px;">${escapeHtml(detail.approach || "")}</div>
      <div style="font-size:13px; color:#334155; line-height:1.55;">${escapeHtml(detail.philosophy || "")}</div>
    `;
    codeBox.textContent = detail.code || "";
    if (!silent) {
      showToast(`Comparatif OpenAPI 3.1 -> ${chosen.toUpperCase()}`);
    }
  } catch (err) {
    codeBox.textContent = "Erreur de chargement : " + err.message;
  }
}
