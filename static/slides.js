/* ==========================================================================
   ISGP — Contrôleur Interactif du Support de Présentation (Slides Tornado)
   Navigation clavier/tactile, Vue Grille, Recherche, Plein Écran Paysage & PDF
   ========================================================================== */

(function () {
  "use strict";

  let DECK = { meta: {}, parts: [], slides: [] };
  let currentIdx = 0;
  let touchStartX = null;

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatInlineCode(str) {
    return escapeHtml(str).replace(/`([^`]+)`/g, "<code>$1</code>");
  }

  function highlightFragment(code, lang) {
    const lines = String(code || "").split("\n");
    return lines
      .map((rawLine) => {
        const trimmed = rawLine.trim();
        if (trimmed.startsWith("#") || trimmed.startsWith("//") || trimmed.startsWith("--")) {
          return '<span class="tok-cmt">' + escapeHtml(rawLine) + "</span>";
        }
        let html = escapeHtml(rawLine);
        html = html.replace(/(&quot;[^&]*?&quot;|'[^']*?')/g, '<span class="tok-str">$1</span>');
        if (lang === "python" || !lang) {
          html = html.replace(
            /\b(class|def|async|await|return|import|from|if|elif|else|for|in|try|except|finally|with|as|raise|None|True|False|and|or|not)\b/g,
            '<span class="tok-kw">$1</span>'
          );
          html = html.replace(/(^|\s)(@[A-Za-z0-9_.]+)/g, '$1<span class="tok-dec">$2</span>');
        } else if (lang === "http") {
          html = html.replace(
            /\b(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD|HTTP\/1\.1)\b/g,
            '<span class="tok-kw">$1</span>'
          );
        } else if (lang === "sql") {
          html = html.replace(
            /\b(SELECT|INSERT|INTO|VALUES|UPDATE|SET|DELETE|FROM|WHERE|CREATE|TABLE|IF|NOT|EXISTS|PRIMARY|KEY|PRAGMA|BEGIN|COMMIT|ORDER|BY|LIMIT|OFFSET)\b/gi,
            '<span class="tok-kw">$1</span>'
          );
        }
        return html;
      })
      .join("\n");
  }

  function pad3(n) {
    return String(n).padStart(3, "0");
  }

  function buildSlideInnerHtml(slide, total, forPrint) {
    const hasCode = Boolean(slide.code && slide.code.trim());
    const hasCompare = Boolean(slide.comparison && slide.comparison.left_title);
    const points = Array.isArray(slide.points) ? slide.points : [];

    const pointsHtml = points
      .map(
        (pt, idx) =>
          '<div class="slide-point-card">' +
          '<span class="slide-point-index">' +
          (idx + 1) +
          "</span>" +
          '<div class="slide-point-content">' +
          (pt.label ? "<strong>" + formatInlineCode(pt.label) + " :</strong> " : "") +
          formatInlineCode(pt.text || "") +
          "</div></div>"
      )
      .join("");

    let compareHtml = "";
    if (hasCompare) {
      const c = slide.comparison;
      const leftItems = (c.left_items || [])
        .map((it) => '<div class="slide-compare-item">' + formatInlineCode(it) + "</div>")
        .join("");
      const rightItems = (c.right_items || [])
        .map((it) => '<div class="slide-compare-item">' + formatInlineCode(it) + "</div>")
        .join("");
      compareHtml =
        '<div class="slide-compare-grid">' +
        '<div class="slide-compare-col col-left">' +
        '<h3 class="slide-compare-title">' +
        formatInlineCode(c.left_title) +
        "</h3>" +
        '<div class="slide-compare-items">' +
        leftItems +
        "</div></div>" +
        '<div class="slide-compare-col col-right">' +
        '<h3 class="slide-compare-title">' +
        formatInlineCode(c.right_title) +
        "</h3>" +
        '<div class="slide-compare-items">' +
        rightItems +
        "</div></div></div>";
    }

    let codeHtml = "";
    if (hasCode) {
      const copyBtn = forPrint
        ? ""
        : '<button type="button" class="slide-copy-btn" onclick="window.copyCurrentSlideCode(this)">Copier</button>';
      codeHtml =
        '<div class="slide-code-panel">' +
        '<div class="slide-code-header">' +
        '<span class="slide-code-label">' +
        escapeHtml(slide.code_label || "Fragment de référence") +
        "</span>" +
        '<div class="slide-code-actions">' +
        '<span class="slide-code-lang">' +
        escapeHtml(slide.code_lang || "code") +
        "</span>" +
        copyBtn +
        "</div></div>" +
        '<pre class="slide-code-pre"><code>' +
        highlightFragment(slide.code, slide.code_lang) +
        "</code></pre></div>";
    }

    let bodyHtml = "";
    if (hasCode) {
      bodyHtml =
        '<div class="slide-body layout-split">' +
        '<div class="slide-points-list">' +
        (hasCompare ? compareHtml : "") +
        pointsHtml +
        "</div>" +
        codeHtml +
        "</div>";
    } else if (hasCompare) {
      bodyHtml =
        '<div class="slide-body">' +
        compareHtml +
        (points.length ? '<div class="slide-points-grid">' + pointsHtml + "</div>" : "") +
        "</div>";
    } else {
      bodyHtml =
        '<div class="slide-body"><div class="slide-points-grid">' + pointsHtml + "</div></div>";
    }

    return (
      '<div>' +
      '<div class="slide-meta-row">' +
      '<div class="slide-badges">' +
      '<span class="slide-part-pill">' +
      escapeHtml(slide.part_title) +
      "</span>" +
      '<span class="slide-tag-pill">' +
      escapeHtml(slide.tag) +
      "</span></div>" +
      '<span class="slide-counter-pill">' +
      pad3(slide.number) +
      " / " +
      pad3(total) +
      "</span></div>" +
      '<div class="slide-headline">' +
      "<h1>" +
      formatInlineCode(slide.title) +
      "</h1>" +
      '<p class="slide-subtitle">' +
      formatInlineCode(slide.subtitle) +
      "</p></div>" +
      '<div class="slide-def-box">' +
      '<span class="slide-def-kicker">Définition</span>' +
      '<p class="slide-def-text">' +
      formatInlineCode(slide.definition) +
      "</p></div></div>" +
      bodyHtml +
      (slide.takeaway
        ? '<div class="slide-takeaway-bar"><span class="slide-takeaway-tag">À retenir</span><span>' +
          formatInlineCode(slide.takeaway) +
          "</span></div>"
        : "")
    );
  }

  function renderCurrentSlide() {
    const slides = DECK.slides || [];
    if (!slides.length) return;
    if (currentIdx < 0) currentIdx = 0;
    if (currentIdx >= slides.length) currentIdx = slides.length - 1;

    const slide = slides[currentIdx];
    const stage = document.getElementById("slide-stage");
    if (stage) {
      stage.innerHTML = buildSlideInnerHtml(slide, slides.length, false);
      stage.scrollTop = 0;
    }

    const pct = ((currentIdx + 1) / slides.length) * 100;
    const fill = document.getElementById("deck-progress-fill");
    if (fill) fill.style.width = pct.toFixed(2) + "%";

    const sel = document.getElementById("deck-part-select");
    if (sel && sel.value !== slide.part_id) {
      sel.value = slide.part_id;
    }

    const posLabel = document.getElementById("deck-pos-label");
    if (posLabel) {
      posLabel.textContent = "Diapositive " + (currentIdx + 1) + " sur " + slides.length;
    }

    try {
      history.replaceState(null, "", "#slide-" + (currentIdx + 1));
      localStorage.setItem("isgp-tornado-slide-idx", String(currentIdx));
    } catch (e) {}
  }

  function populatePartsDropdown() {
    const sel = document.getElementById("deck-part-select");
    if (!sel) return;
    sel.innerHTML = (DECK.parts || [])
      .map(
        (p) =>
          '<option value="' +
          escapeHtml(p.part_id) +
          '">' +
          escapeHtml(p.part_title) +
          " (" +
          p.first_slide +
          "–" +
          p.last_slide +
          ")</option>"
      )
      .join("");
    sel.addEventListener("change", () => {
      const part = (DECK.parts || []).find((x) => x.part_id === sel.value);
      if (part) {
        currentIdx = part.first_slide - 1;
        renderCurrentSlide();
      }
    });
  }

  function renderGridCards(query) {
    const container = document.getElementById("deck-grid-cards");
    const countSpan = document.getElementById("deck-grid-count");
    if (!container) return;
    const q = String(query || "").trim().toLowerCase();
    const matches = (DECK.slides || []).filter((s) => {
      if (!q) return true;
      const hay = [
        s.title,
        s.subtitle,
        s.definition,
        s.tag,
        s.part_title,
        s.code,
        s.takeaway,
        ...(s.points || []).map((p) => (p.label || "") + " " + (p.text || "")),
      ]
        .join(" ")
        .toLowerCase();
      return hay.includes(q);
    });
    if (countSpan) {
      countSpan.textContent = matches.length + " / " + (DECK.slides || []).length + " diapositives";
    }
    container.innerHTML = matches
      .map(
        (s) =>
          '<button type="button" class="deck-mini-card ' +
          (s.number - 1 === currentIdx ? "active" : "") +
          '" onclick="window.jumpToSlideNumber(' +
          s.number +
          ')">' +
          '<div class="deck-mini-top"><span>#' +
          pad3(s.number) +
          " • " +
          escapeHtml(s.part_id) +
          "</span><span>" +
          escapeHtml(s.tag) +
          "</span></div>" +
          '<div class="deck-mini-title">' +
          escapeHtml(s.title) +
          "</div>" +
          '<div class="deck-mini-sub">' +
          escapeHtml(s.subtitle) +
          "</div></button>"
      )
      .join("");
  }

  window.prevSlide = function () {
    if (currentIdx > 0) {
      currentIdx -= 1;
      renderCurrentSlide();
    }
  };

  window.nextSlide = function () {
    if (currentIdx < (DECK.slides || []).length - 1) {
      currentIdx += 1;
      renderCurrentSlide();
    }
  };

  window.jumpToSlideNumber = function (num) {
    currentIdx = Math.max(0, Math.min((DECK.slides || []).length - 1, Number(num) - 1));
    window.closeDeckGrid();
    renderCurrentSlide();
  };

  window.toggleDeckGrid = function () {
    const overlay = document.getElementById("deck-grid-overlay");
    if (!overlay) return;
    const opening = overlay.classList.contains("hidden");
    overlay.classList.toggle("hidden", !opening);
    if (opening) {
      const topSearch = document.getElementById("deck-search-input");
      renderGridCards(topSearch ? topSearch.value : "");
    }
  };

  window.closeDeckGrid = function () {
    const overlay = document.getElementById("deck-grid-overlay");
    if (overlay) overlay.classList.add("hidden");
  };

  window.toggleDeckTheme = function () {
    const cur = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem("isgp-slides-theme", next);
    } catch (e) {}
    const btn = document.getElementById("deck-theme-btn");
    if (btn) btn.textContent = next === "dark" ? "Mode Clair" : "Mode Sombre";
  };

  window.toggleDeckFullscreen = async function () {
    try {
      if (!document.fullscreenElement) {
        await document.documentElement.requestFullscreen();
        if (screen.orientation && screen.orientation.lock) {
          try {
            await screen.orientation.lock("landscape");
          } catch (e) {}
        }
      } else {
        await document.exitFullscreen();
      }
    } catch (e) {}
  };

  window.copyCurrentSlideCode = function (btnEl) {
    const s = (DECK.slides || [])[currentIdx];
    if (!s || !s.code || !navigator.clipboard) return;
    navigator.clipboard.writeText(s.code).then(() => {
      if (btnEl) {
        const prev = btnEl.textContent;
        btnEl.textContent = "Copié";
        setTimeout(() => {
          btnEl.textContent = prev;
        }, 1200);
      }
    });
  };

  window.printAllSlides = function () {
    const printRoot = document.getElementById("deck-print-all");
    const slides = DECK.slides || [];
    if (printRoot && !printRoot.hasChildNodes()) {
      printRoot.innerHTML = slides
        .map(
          (s) =>
            '<section class="print-slide-page">' +
            buildSlideInnerHtml(s, slides.length, true) +
            "</section>"
        )
        .join("");
    }
    window.print();
  };

  function bindEvents() {
    const searchInput = document.getElementById("deck-search-input");
    if (searchInput) {
      searchInput.addEventListener("input", () => {
        const overlay = document.getElementById("deck-grid-overlay");
        if (overlay && overlay.classList.contains("hidden") && searchInput.value.trim().length > 0) {
          overlay.classList.remove("hidden");
        }
        renderGridCards(searchInput.value);
      });
    }

    document.addEventListener("keydown", (ev) => {
      const tag = (ev.target && ev.target.tagName) || "";
      if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") {
        if (ev.key === "Escape") {
          ev.target.blur();
          window.closeDeckGrid();
        }
        return;
      }
      if (ev.key === "ArrowRight" || ev.key === "PageDown" || ev.key === " ") {
        ev.preventDefault();
        window.nextSlide();
      } else if (ev.key === "ArrowLeft" || ev.key === "PageUp") {
        ev.preventDefault();
        window.prevSlide();
      } else if (ev.key === "Home") {
        ev.preventDefault();
        currentIdx = 0;
        renderCurrentSlide();
      } else if (ev.key === "End") {
        ev.preventDefault();
        currentIdx = Math.max(0, (DECK.slides || []).length - 1);
        renderCurrentSlide();
      } else if (ev.key === "g" || ev.key === "G") {
        ev.preventDefault();
        window.toggleDeckGrid();
      } else if (ev.key === "f" || ev.key === "F") {
        ev.preventDefault();
        window.toggleDeckFullscreen();
      } else if (ev.key === "t" || ev.key === "T") {
        ev.preventDefault();
        window.toggleDeckTheme();
      } else if (ev.key === "/") {
        ev.preventDefault();
        if (searchInput) searchInput.focus();
      } else if (ev.key === "Escape") {
        window.closeDeckGrid();
      }
    });

    const viewport = document.querySelector(".deck-viewport");
    if (viewport) {
      viewport.addEventListener("touchstart", (ev) => {
        if (ev.changedTouches && ev.changedTouches[0]) {
          touchStartX = ev.changedTouches[0].clientX;
        }
      });
      viewport.addEventListener("touchend", (ev) => {
        if (touchStartX === null || !ev.changedTouches || !ev.changedTouches[0]) return;
        const dx = ev.changedTouches[0].clientX - touchStartX;
        touchStartX = null;
        if (Math.abs(dx) > 55) {
          if (dx < 0) window.nextSlide();
          else window.prevSlide();
        }
      });
    }
  }

  async function initDeck() {
    try {
      const savedTheme = localStorage.getItem("isgp-slides-theme");
      const theme = savedTheme === "light" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", theme);
      const btn = document.getElementById("deck-theme-btn");
      if (btn) btn.textContent = theme === "dark" ? "Mode Clair" : "Mode Sombre";
    } catch (e) {}

    const inlineEl = document.getElementById("slides-deck-data");
    if (inlineEl && inlineEl.textContent.trim()) {
      DECK = JSON.parse(inlineEl.textContent);
    } else {
      const res = await fetch("/api/slides/tornado");
      DECK = await res.json();
    }

    populatePartsDropdown();
    bindEvents();

    const m = (window.location.hash || "").match(/^#slide-(\d+)$/);
    if (m) {
      currentIdx = Math.max(0, parseInt(m[1], 10) - 1);
    } else {
      try {
        const savedIdx = parseInt(localStorage.getItem("isgp-tornado-slide-idx") || "0", 10);
        if (!isNaN(savedIdx) && savedIdx >= 0) currentIdx = savedIdx;
      } catch (e) {}
    }
    renderCurrentSlide();
  }

  document.addEventListener("DOMContentLoaded", initDeck);
})();
