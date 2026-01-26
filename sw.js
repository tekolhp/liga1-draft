const CACHE_NAME = 'liga1-images-v2';
const IMAGE_CACHE_DURATION = 7 * 24 * 60 * 60 * 1000; // 7 dias em ms

self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Só cacheia imagens do Google Drive
  if (url.hostname === 'drive.google.com' &&
      (url.pathname.includes('/thumbnail') || url.pathname.includes('/uc'))) {

    event.respondWith(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((cachedResponse) => {

          // Se tem no cache, verifica se ainda é válido
          if (cachedResponse) {
            const cachedDate = new Date(cachedResponse.headers.get('sw-cached-date'));
            const now = new Date();

            // Se ainda está dentro do período de cache, retorna do cache
            if (now - cachedDate < IMAGE_CACHE_DURATION) {
              console.log('[Service Worker] Serving from cache:', url.href);
              return cachedResponse;
            }
          }

          // Caso contrário, faz fetch e cacheia
          console.log('[Service Worker] Fetching and caching:', url.href);
          return fetch(event.request).then((networkResponse) => {
            // Só cacheia respostas bem-sucedidas
            if (networkResponse && networkResponse.status === 200) {
              // Clona a resposta e adiciona header com data do cache
              const responseToCache = networkResponse.clone();
              const headers = new Headers(responseToCache.headers);
              headers.append('sw-cached-date', new Date().toISOString());

              const newResponse = new Response(responseToCache.body, {
                status: responseToCache.status,
                statusText: responseToCache.statusText,
                headers: headers
              });

              cache.put(event.request, newResponse.clone());
              return networkResponse;
            }
            return networkResponse;
          }).catch((error) => {
            console.error('[Service Worker] Fetch failed:', error);
            // Se falhar e tem cache antigo, retorna mesmo que expirado
            if (cachedResponse) {
              console.log('[Service Worker] Serving stale cache due to network error');
              return cachedResponse;
            }
            throw error;
          });
        });
      })
    );
  }
});
