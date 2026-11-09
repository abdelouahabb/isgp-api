const CACHE_NAME = "isgp-api-lab-v17";
const ASSETS_TO_CACHE = [
  "/",
  "/manifest.json",
  "/static/icon.svg",
  "/static/styles.css",
  "/static/app.js",
  "/api/course-data"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  // Ne jamais mettre en cache le flux SSE temps réel ou les requêtes POST/PUT/DELETE
  if (
    event.request.method !== "GET" ||
    url.pathname.startsWith("/api/classroom/") ||
    url.pathname.startsWith("/api/sandbox/")
  ) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
