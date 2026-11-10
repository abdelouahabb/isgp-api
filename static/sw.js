const CACHE_NAME = "isgp-api-trilogy-v43";
const IS_GH_PAGES_SW = false;

const CORE_RELATIVE_ASSETS = [
  "./",
  "./manifest.json",
  "./static/icon.svg",
  "./static/styles.css",
  "./static/app.js",
  "./static/mermaid.min.js"
];

const WARMUP_RELATIVE_ASSETS = IS_GH_PAGES_SW
  ? [
      "./index.html",
      "./static/gh-pages-shim.js",
      "./cours/flask/index.html",
      "./cours/fastapi/index.html",
      "./cours/tornado/index.html",
      "./static-data/flask/course-data.json",
      "./static-data/flask/architecture-lab.json",
      "./static-data/flask/sqlite-state.json",
      "./static-data/flask/advanced-state.json",
      "./static-data/flask/nginx-state.json",
      "./static-data/fastapi/course-data.json",
      "./static-data/fastapi/architecture-lab.json",
      "./static-data/fastapi/sqlite-state.json",
      "./static-data/fastapi/advanced-state.json",
      "./static-data/fastapi/nginx-state.json",
      "./static-data/tornado/course-data.json",
      "./static-data/tornado/architecture-lab.json",
      "./static-data/tornado/sqlite-state.json",
      "./static-data/tornado/advanced-state.json",
      "./static-data/tornado/nginx-state.json",
      "./api/openapi.json"
    ]
  : [
      "./cours/flask",
      "./cours/fastapi",
      "./cours/tornado",
      "./api/course-data?framework=flask",
      "./api/course-data?framework=fastapi",
      "./api/course-data?framework=tornado",
      "./api/nginx-cluster/state?framework=flask",
      "./api/sqlite-lab/state?framework=flask",
      "./api/advanced-lab/state?framework=flask"
    ];

function resolveScopeUrls(relList) {
  const base = self.registration ? self.registration.scope : self.location.href;
  return relList.map((rel) => new URL(rel, base).href);
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(resolveScopeUrls(CORE_RELATIVE_ASSETS)))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)));
      await self.clients.claim();
      // Pré-chargement non-bloquant des 3 frameworks pour lecture 100 % hors-ligne immédiate
      const cache = await caches.open(CACHE_NAME);
      await Promise.allSettled(
        resolveScopeUrls(WARMUP_RELATIVE_ASSETS).map(async (u) => {
          const resp = await fetch(u);
          if (resp && resp.ok) {
            await cache.put(u, resp.clone());
          }
        })
      );
    })()
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  // Ne jamais intercepter un flux SSE continu
  if (
    url.pathname.endsWith("/api/classroom/stream") ||
    (event.request.headers.get("accept") || "").includes("text/event-stream")
  ) {
    return;
  }

  const isApiQuery = url.pathname.includes("/api/");

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(async () => {
        const exact = await caches.match(event.request);
        if (exact) return exact;
        if (!isApiQuery) {
          const clean = await caches.match(event.request, { ignoreSearch: true });
          if (clean) return clean;
        }
        return Response.error();
      })
  );
});
