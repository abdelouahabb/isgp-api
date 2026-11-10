"""
Générateur de build statique autonome pour GitHub Pages (https://abdelouahabb.github.io/isgp-api/).
Pré-rend toutes les pages HTML, les schémas JSON des 3 frameworks (Flask, FastAPI, Tornado),
la documentation OpenAPI / Swagger UI et les scripts Python téléchargeables dans dist/,
sans modifier le fonctionnement dynamique local de app.py.
"""

import json
import re
import shutil
from pathlib import Path

import app as unified_app

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def rewrite_html_for_static_depth(html: str, rel_root: str) -> str:
    """
    Convertit les chemins absolus racine (/static/..., /cours/..., /api/docs...) en chemins
    relatifs exacts par rapport à la profondeur du fichier HTML dans dist/, et injecte
    le shim d'autonomie client-side (static/gh-pages-shim.js).
    """
    prefix = rel_root.rstrip("/")

    replacements = [
        ('href="/"', f'href="{prefix}/index.html"'),
        ('href="/manifest.json"', f'href="{prefix}/manifest.json"'),
        ('href="/cours/flask"', f'href="{prefix}/cours/flask/index.html"'),
        ('href="/cours/fastapi"', f'href="{prefix}/cours/fastapi/index.html"'),
        ('href="/cours/tornado"', f'href="{prefix}/cours/tornado/index.html"'),
        ('href="/api/docs"', f'href="{prefix}/api/docs/index.html"'),
        ('href="/api/openapi.json"', f'href="{prefix}/api/openapi.json"'),
        ('href="/sandbox/formulaire-jinja"', f'href="{prefix}/sandbox/formulaire-jinja/index.html"'),
        ('href="/api/download/openapi-spec"', f'href="{prefix}/downloads/isgp_api_bootcamp.openapi.json"'),
        ('href="/api/download/postman-collection"', f'href="{prefix}/downloads/isgp_postman_collection.json"'),
        ('href="/api/download/http-requests"', f'href="{prefix}/downloads/isgp_requetes.http"'),
        ('url: "/api/openapi.json"', f'url: "{prefix}/api/openapi.json"'),
    ]
    for old, new in replacements:
        html = html.replace(old, new)

    # Réécriture des balises /static/... (styles.css, app.js, mermaid.min.js, icon.svg)
    html = re.sub(r'(href|src)="/static/([^"]+)"', rf'\1="{prefix}/static/\2"', html)

    # Remplacement de l'adresse IP locale de développement sur la bannière d'accueil
    html = re.sub(
        r"Serveur Unifié Actif : <code>http://[^<]+</code>",
        "Édition Interactive GitHub Pages (Autonome dans le Navigateur)",
        html,
    )

    # Injection du drapeau GitHub Pages et du shim avant static/app.js (ou avant </head> si pas d'app.js)
    shim_tag = (
        f'<script>window.ISGP_GH_PAGES = true; window.ISGP_REL_ROOT = "{rel_root}";</script>\n'
        f'  <script src="{prefix}/static/gh-pages-shim.js?v=38"></script>'
    )
    if "/static/app.js" in html:
        html = re.sub(
            r'(<script src="[^"]*static/app\.js[^"]*"></script>)',
            shim_tag + "\n  \\1",
            html,
            count=1,
        )
    else:
        html = html.replace("</head>", f"  {shim_tag}\n</head>", 1)

    return html


def build() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # Désactivation explicite du traitement Jekyll sur GitHub Pages
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    # 1. Copie des ressources statiques partagées et du manifeste PWA adapté aux sous-chemins
    shutil.copytree(ROOT / "static", DIST / "static")
    manifest_data = json.loads((ROOT / "static" / "manifest.json").read_text(encoding="utf-8"))
    manifest_data["start_url"] = "./index.html"
    for icon in manifest_data.get("icons", []):
        if icon.get("src", "").startswith("/"):
            icon["src"] = "." + icon["src"]
    (DIST / "manifest.json").write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")

    client = unified_app.app.test_client()

    # 2. Page d'accueil principale (/) et page de repli 404.html
    landing_raw = client.get("/").get_data(as_text=True)
    landing_static = rewrite_html_for_static_depth(landing_raw, "./")
    (DIST / "index.html").write_text(landing_static, encoding="utf-8")
    (DIST / "404.html").write_text(landing_static, encoding="utf-8")

    # 3. Portail Swagger UI (/api/docs) & OpenAPI (/api/openapi.json)
    (DIST / "api" / "docs").mkdir(parents=True, exist_ok=True)
    openapi_bytes = client.get("/api/download/openapi-spec").get_data()
    (DIST / "api" / "openapi.json").write_bytes(openapi_bytes)

    swagger_raw = client.get("/api/docs").get_data(as_text=True)
    swagger_static = rewrite_html_for_static_depth(swagger_raw, "../../")
    (DIST / "api" / "docs" / "index.html").write_text(swagger_static, encoding="utf-8")

    # 4. Démo Formulaire HTML Jinja2 (/sandbox/formulaire-jinja) avec validation JS côté navigateur
    (DIST / "sandbox" / "formulaire-jinja").mkdir(parents=True, exist_ok=True)
    jinja_raw = client.get("/sandbox/formulaire-jinja").get_data(as_text=True)
    jinja_static = rewrite_html_for_static_depth(jinja_raw, "../../")
    form_intercept_js = """
<script>
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  if (!form) return;
  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const fd = new FormData(form);
    const titre = (fd.get("titre") || "").toString().trim();
    const duree = parseInt((fd.get("duree_jours") || "0").toString(), 10);
    const box = document.createElement("div");
    box.style.cssText = "margin:14px 0; padding:12px 16px; border-radius:6px; font-size:14px;";
    if (titre.length < 3 || isNaN(duree) || duree < 1) {
      box.style.background = "#fef2f2";
      box.style.border = "1px solid #ef4444";
      box.style.color = "#991b1b";
      box.innerHTML = "<strong>Validation échouée (422 simulé) :</strong> intitulé >= 3 caractères et durée >= 1 jour requis.";
    } else {
      box.style.background = "#f0fdf4";
      box.style.border = "1px solid #16a34a";
      box.style.color = "#14532d";
      const encoded = new URLSearchParams(fd).toString();
      box.innerHTML = "<strong>Formulaire validé (Simulation GitHub Pages) !</strong><br/>Trame <code>application/x-www-form-urlencoded</code> reçue : <code>" + encoded + "</code>";
    }
    form.prepend(box);
  });
});
</script>
"""
    jinja_static = jinja_static.replace("</body>", form_intercept_js + "\n</body>", 1)
    (DIST / "sandbox" / "formulaire-jinja" / "index.html").write_text(jinja_static, encoding="utf-8")

    # 5. Téléchargements statiques (OpenAPI, Collection Postman, Fichier .http)
    dl_dir = DIST / "downloads"
    dl_dir.mkdir(parents=True, exist_ok=True)
    (dl_dir / "isgp_api_bootcamp.openapi.json").write_bytes(openapi_bytes)
    (dl_dir / "isgp_postman_collection.json").write_bytes(client.get("/api/download/postman-collection").get_data())
    (dl_dir / "isgp_requetes.http").write_bytes(client.get("/api/download/http-requests").get_data())

    # 6. Pages de cours, bundles JSON et fichiers Python téléchargeables pour les 3 frameworks
    for fw in ("flask", "fastapi", "tornado"):
        # Page HTML /cours/<fw>/index.html
        fw_page_dir = DIST / "cours" / fw
        fw_page_dir.mkdir(parents=True, exist_ok=True)
        fw_html_raw = client.get(f"/cours/{fw}").get_data(as_text=True)
        fw_html_static = rewrite_html_for_static_depth(fw_html_raw, "../../")
        (fw_page_dir / "index.html").write_text(fw_html_static, encoding="utf-8")

        # Données JSON pré-exportées
        data_dir = DIST / "static-data" / fw
        data_dir.mkdir(parents=True, exist_ok=True)
        for endpoint, out_name in (
            (f"/api/course-data?framework={fw}", "course-data.json"),
            (f"/api/nginx-cluster/state?framework={fw}", "nginx-state.json"),
            (f"/api/sqlite-lab/state?framework={fw}", "sqlite-state.json"),
            (f"/api/advanced-lab/state?framework={fw}", "advanced-state.json"),
        ):
            payload = client.get(endpoint).get_json()
            (data_dir / out_name).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

        # Scripts Python des Jours 0..5 + scripts de référence transversaux
        fw_src = ROOT / f"{fw}-version"
        for day_num in range(6):
            src_day = fw_src / f"day_{day_num}"
            dst_day = DIST / "files" / fw / f"day_{day_num}"
            if src_day.is_dir():
                dst_day.mkdir(parents=True, exist_ok=True)
                for item in src_day.iterdir():
                    if item.is_file() and not item.name.endswith((".db", ".db-wal", ".db-shm", ".pyc")):
                        shutil.copy2(item, dst_day / item.name)

        ref_dst = DIST / "files" / fw / "ref"
        ref_dst.mkdir(parents=True, exist_ok=True)
        for ref_name in ("sqlite_api_lab.py", "advanced_realtime_cache_lab.py"):
            ref_src = fw_src / ref_name
            if ref_src.is_file():
                shutil.copy2(ref_src, ref_dst / ref_name)

    total_files = sum(1 for p in DIST.rglob("*") if p.is_file())
    print(f"[OK] Build statique GitHub Pages généré dans {DIST} ({total_files} fichiers).")


if __name__ == "__main__":
    build()
