// ============================================================
// Service Worker для КИПиА — стратегия network-first
// ============================================================
// КАК ОБНОВИТЬ САЙТ: увеличьте CACHE_VERSION ниже.
//   'kipia-v2' → 'kipia-v3' → 'kipia-v4' и т.д.
// При смене версии SW удалит ВСЕ старые кэши и закэширует
// свежие версии файлов из ASSETS.
// ============================================================

const CACHE_VERSION = 'kipia-v2';
const CACHE_NAME = CACHE_VERSION;

// Файлы для пред-кэширования при установке SW.
// Эти ресурсы будут доступны в офлайне сразу после первой загрузки.
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './images/icon-192.png',
  './images/icon-512.png',
  './images/icon-192-maskable.png',
  './images/icon-512-maskable.png',
  './images/icon.png',
  './images/1000\u0412.png',
  './images/4\u0440.png',
  './images/5\u0440.png',
  './images/6\u0440.png',
  './data/exam-tickets.json'
];

// ============================================================
// Утилита: получить "чистый" ключ кэша (URL без query-параметров)
// ============================================================
// ВАЖНО: index.html использует cache-busting для data/exam-tickets.json
// через ?v=t<timestamp>. Это создаёт новый URL при каждой перезагрузке
// страницы. Если использовать event.request как ключ кэша напрямую,
// Cache Storage будет расти бесконечно, а в офлайне запрос с новым
// timestamp не найдёт закэшированную версию.
//
// Решение: для локальных GET-запросов ключом кэша служит URL БЕЗ query.
//   fetch(event.request)              ← оригинальный запрос (с ?v=t123, для сервера)
//   cache.put(cacheKey, response)     ← ключ без query (для стабильности кэша)
//   caches.match(cacheKey)            ← поиск по ключу без query
function makeCacheKey(request) {
  const url = new URL(request.url);
  // Для локальных запросов отбрасываем search (всё после '?')
  if (url.origin === self.location.origin) {
    // Новый Request с тем же методом, но URL без query.
    // headers не копируются — для кэша они не нужны.
    return new Request(url.pathname, { method: request.method });
  }
  // Для внешних ресурсов (шрифты, CDN) — ключом служит полный URL,
  // потому что query часто содержит аутентификационные токены или
  // версии, которые являются частью идентичности ресурса.
  return request;
}

// ============================================================
// Install — пред-кэширование основных файлов
// ============================================================
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  // Немедленно активировать новый SW, не дожидаясь закрытия старых вкладок
  self.skipWaiting();
});

// ============================================================
// Activate — удалить старые кэши + очистить «осиротевшие» записи
// ============================================================
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => {
        // 1. Удалить все кэши с другими именами (старые версии)
        const deleteOldCaches = Promise.all(
          keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
        );
        return deleteOldCaches.then(() => {
          // 2. В текущем кэше удалить записи, которых больше нет в ASSETS
          //    (например, устаревшие ?v=t1234567890 от предыдущей версии SW)
          return caches.open(CACHE_NAME).then(cache => {
            return cache.keys().then(requests => {
              return Promise.all(requests.map(req => {
                // Нормализуем текущий ключ так же, как makeCacheKey
                const normalizedKey = makeCacheKey(req);
                const normalizedUrl = new URL(normalizedKey.url);
                // Список допустимых путей из ASSETS (без './' префикса и query)
                const validPaths = ASSETS.map(a => a.replace(/^\.\//, '/'));
                // Если запись не входит в ASSETS — удаляем
                const matches = validPaths.some(p => normalizedUrl.pathname === p);
                if (!matches) {
                  return cache.delete(req);
                }
                return Promise.resolve();
              }));
            });
          });
        });
      })
      .then(() => self.clients.claim())  // Захватить контроль над всеми вкладками
  );
});

// ============================================================
// Fetch — стратегия NETWORK-FIRST
// ============================================================
// Локальные файлы:
//   1. Идём в сеть (с оригинальным запросом, включая cache-busting query).
//   2. При успехе — обновляем кэш по нормализованному ключу (без query).
//   3. При ошибке сети — отдаём из кэша по нормализованному ключу.
//
// Внешние ресурсы (шрифты, CDN):
//   1. Идём в сеть с оригинальным запросом.
//   2. При успехе — кэшируем по полному URL (query сохраняется).
//   3. При ошибке — отдаём из кэша по полному URL.
self.addEventListener('fetch', event => {
  const request = event.request;

  // Только GET-запросы кэшируем
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  const isLocal = url.origin === self.location.origin;

  // ===== Внешние ресурсы (шрифты Google, CDN) =====
  if (!isLocal) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // ===== Локальные файлы (HTML, CSS-in-HTML, JS-in-HTML, JSON, images) =====
  const cacheKey = makeCacheKey(request);

  event.respondWith(
    fetch(request)
      .then(response => {
        if (response.ok) {
          // Обновляем кэш по нормализованному ключу (без ?v=...)
          // Важно: response.clone() нужен, т.к. сам response пойдёт в браузер.
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(cacheKey, clone));
        }
        return response;
      })
      .catch(() => {
        // Нет сети — отдаём из кэша по нормализованному ключу
        return caches.match(cacheKey).then(cached => {
          if (cached) return cached;
          // Если кэша нет — пытаемся найти по полному URL (на случай,
          // если какая-то старая запись осталась без нормализации)
          return caches.match(request).then(fallback => {
            return fallback || new Response('Offline', {
              status: 503,
              statusText: 'Service Unavailable',
              headers: { 'Content-Type': 'text/plain; charset=utf-8' }
            });
          });
        });
      })
  );
});
