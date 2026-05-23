// Service Worker for КИП ИОС PWA
// Caches static assets for offline use

const CACHE_NAME = 'kip-ios-v1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/styles.css',
    '/app.js',
    '/manifest.json',
    '/icon.png',
    '/offline.html',
    '/logo.png',
    // External CDN resources - cached via opaque responses
    'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',
    'https://cdn.jsdelivr.net/npm/@fontsource/inter@4.5.15/index.min.css'
];

// Install event: cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Caching static assets...');
                return cache.addAll(STATIC_ASSETS);
            })
            .catch((err) => {
                console.warn('[SW] Failed to cache some assets:', err);
                // Continue even if some CDN resources fail (opaque responses may fail)
                return Promise.resolve();
            })
    );
    // Activate immediately
    self.skipWaiting();
});

// Activate event: clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME)
                    .map((name) => {
                        console.log('[SW] Deleting old cache:', name);
                        return caches.delete(name);
                    })
            );
        }).then(() => {
            // Take control of all clients immediately
            return self.clients.claim();
        })
    );
});

// Fetch event: serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Strategy: Cache First for static assets, Network First for API/external
    if (isStaticAsset(url)) {
        event.respondWith(cacheFirst(request));
    } else if (isExternalResource(url)) {
        event.respondWith(networkFirst(request));
    } else {
        // Default: try cache, then network
        event.respondWith(cacheFirst(request));
    }
});

function isStaticAsset(url) {
    const staticExtensions = ['.html', '.css', '.js', '.json', '.png', '.jpg', '.svg', '.woff', '.woff2'];
    return staticExtensions.some(ext => url.pathname.endsWith(ext));
}

function isExternalResource(url) {
    return url.hostname !== self.location.hostname && 
           !url.hostname.includes('cdn.jsdelivr.net');
}

// Cache First strategy: serve from cache, fallback to network
async function cacheFirst(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            // Return cached response and update cache in background
            updateCache(request);
            return cachedResponse;
        }
        // Not in cache: fetch from network
        const networkResponse = await fetch(request);
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.warn('[SW] Cache first failed:', error);
        // Return offline fallback if available
        if (request.mode === 'navigate') {
            return caches.match('/offline.html');
        }
        return caches.match('/index.html');
    }
}

// Network First strategy: try network, fallback to cache
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.warn('[SW] Network first failed, trying cache:', error);
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match('/index.html');
        }
        throw error;
    }
}

// Background cache update
async function updateCache(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
    } catch (error) {
        // Silently fail - we already have cached version
    }
}

// Message handler for skipWaiting
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
