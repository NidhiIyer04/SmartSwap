const CACHE_NAME = 'smartswapml-v1';
const urlsToCache = [
  '/',
  '/css/style.css',
  '/js/app.js',
  '/js/api.js',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
