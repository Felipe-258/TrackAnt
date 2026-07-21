const CACHE_NAME = 'trackant-v1';

const STATIC_ASSETS = [
  '/offline/',
  '/static/ants/css/colony.css',
  '/static/icons/colony/ant.svg',
  '/static/icons/pwa/icon-192.png',
  '/static/icons/pwa/icon-512.png',
];

const CDN_ASSETS = [
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
  'https://cdn.jsdelivr.net/npm/lucide@0.462.0/dist/umd/lucide.min.js',
  'https://unpkg.com/htmx.org@latest/dist/htmx.min.js',
  'https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return Promise.all(
        STATIC_ASSETS.map(function (url) {
          return cache.add(url)['catch'](function () {
            console.warn('SW: failed to cache', url);
          });
        })
      );
    }).then(function () {
      return caches.open(CACHE_NAME).then(function (cache) {
        return Promise.allSettled(
          CDN_ASSETS.map(function (url) {
            return cache.add(url)['catch'](function () {
              console.warn('SW: failed to cache CDN', url);
            });
          })
        );
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (k) { return k !== CACHE_NAME; }).map(function (k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  var request = event.request;
  var url = new URL(request.url);

  if (request.method !== 'GET') return;

  if (url.pathname.startsWith('/api/')) return;

  if (url.pathname.startsWith('/admin/')) return;

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).then(function (response) {
        var clone = response.clone();
        caches.open(CACHE_NAME).then(function (c) { c.put(request, clone); });
        return response;
      })['catch'](function () {
        return caches.match('/offline/');
      })
    );
    return;
  }

  event.respondWith(
    caches.match(request).then(function (cached) {
      if (cached) return cached;
      return fetch(request).then(function (response) {
        if (response.ok && url.protocol.startsWith('http')) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function (c) { c.put(request, clone); });
        }
        return response;
      });
    })
  );
});
