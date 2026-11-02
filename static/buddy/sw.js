/* Buddy — offline service worker
 *
 * Buddy exists for people whose phone is becoming difficult to use. That
 * means the app has to open when there is no signal: a lift, a basement
 * flat, a hospital car park, a dead battery on a prepaid plan. Without a
 * service worker, "works offline" depends entirely on the browser having
 * cached the page by luck.
 *
 * What is cached: the app shell only — index.html, style.css, app.js,
 * i18n.js, the icons and the manifest. Buddy keeps all of its actual data
 * (contacts, medication schedule, notes) in localStorage, which the
 * service worker never touches.
 *
 * What is not cached: anything cross-origin. The Lora web font comes from
 * Google Fonts, and a stale font is not worth blocking a render for; if
 * it cannot be fetched the page falls back to a system serif.
 *
 * Strategy: stale-while-revalidate for everything same-origin. The cached
 * copy is served immediately — a parent should never wait on a network
 * round trip to open the app — and the network copy refreshes the cache
 * in the background for next time.
 *
 * Bump CACHE when the shell changes. The browser re-checks sw.js on
 * navigation, sees a new version, installs it, and the activate handler
 * drops the old cache.
 */

const CACHE = 'buddy-v1';

const SHELL = [
  './',
  './index.html',
  './style.css',
  './app.js',
  './i18n.js',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE);
      // One asset failing must not break the whole install. A phone that
      // cannot reach the network right now still needs the app itself.
      await Promise.all(
        SHELL.map(async (url) => {
          try {
            await cache.add(new Request(url, { cache: 'reload' }));
          } catch (err) {
            console.warn('[buddy-sw] could not precache', url, err);
          }
        })
      );
      await self.skipWaiting();
    })()
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
      await self.clients.claim();
    })()
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  let url;
  try {
    url = new URL(request.url);
  } catch (err) {
    return;
  }

  // Cross-origin (Google Fonts) stays on the network.
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    (async () => {
      const cache = await caches.open(CACHE);
      const cached = await cache.match(request);

      const network = fetch(request)
        .then((response) => {
          if (response && response.ok && response.type === 'basic') {
            cache.put(request, response.clone());
          }
          return response;
        })
        .catch(() => null);

      if (cached) {
        // Serve instantly, let the refresh land in the background.
        event.waitUntil(network);
        return cached;
      }

      const fresh = await network;
      if (fresh) return fresh;

      // Offline and nothing cached: a navigation still gets the app shell.
      if (request.mode === 'navigate') {
        const shell = await cache.match('./index.html');
        if (shell) return shell;
      }
      return new Response('Buddy is offline and this page is not cached.', {
        status: 503,
        headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      });
    })()
  );
});
