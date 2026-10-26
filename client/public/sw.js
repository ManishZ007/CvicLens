/* Cache only this public fallback shell. Never cache accounts, reports or API responses. */
const SHELL = "civiclens-public-shell-v1";
const PUBLIC_FILES = ["/offline.html", "/icons/icon-192.png", "/icons/icon-512.png"];
self.addEventListener("install", event => {
  event.waitUntil(caches.open(SHELL).then(cache => cache.addAll(PUBLIC_FILES)));
});
self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key =>
    key.startsWith("civiclens-public-shell-") && key !== SHELL).map(key => caches.delete(key)))));
});
self.addEventListener("fetch", event => {
  if (event.request.method !== "GET" || event.request.mode !== "navigate") return;
  if (new URL(event.request.url).origin !== self.location.origin) return;
  event.respondWith(fetch(event.request).catch(async () =>
    (await caches.match("/offline.html")) || new Response("Offline. Reconnect to open CivicLens.", {
      status: 503, headers: { "Content-Type": "text/plain" },
    })));
});
