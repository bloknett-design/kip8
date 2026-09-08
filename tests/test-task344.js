// tests/test-task344.js
// Task 344 — фикс «общего входа» kip8 ↔ kip8test (заявка пользователя
// 2026-09-08: «установил два приложения… захожу в аккаунт в kip8…
// открываю kip8test, а оно тоже вошло в тот же аккаунт»).
//
// ИНЦИДЕНТ: при переносе Task 341 (коммит e50d394) в kip8 был
// скопирован тестовый index.html ЦЕЛИКОМ — вместе с обёрткой
// isolateLocalStorage() (префикс 'kip8test:' ко ВСЕМ ключам
// localStorage). Оба PWA на одном origin (bloknett-design.github.io),
// хранилище общее: kip8 писал токен в 'kip8test:kip8_session_token' —
// тот же ключ, что читает kip8test → вход в kip8 логинил kip8test.
//
// Регрессия (машино-исполняемый чеклист «после переноса kip8test→kip8»,
// раньше — только ручной grep из системного промта):
//   • в kip8 НЕТ обёртки isolateLocalStorage и литерала 'kip8test:';
//   • тест-ключи kip8test_* переименованы в прод-ключи kip8_*;
//   • KipAuth хранит токен под РОВНО 'kip8_session_token'
//     (VM: setToken/getToken/clearToken на моке localStorage);
//   • SW: CACHE_VERSION = 'kipia-v430' (бамп фикс-деплоя).
//
// Запуск: через tests/run-all.js (require './test-task344.js').

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { test, describe, assertTrue, assertEqual } = require('./test-helpers.js');

const ROOT = path.join(__dirname, '..');
const INDEX_SRC = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const SW_SRC = fs.readFileSync(path.join(ROOT, 'sw.js'), 'utf8');

// ============================================================
// 1. SRC — обёртки изоляции в kip8 быть НЕ должно
// ============================================================
describe('Task 344 — изоляция kip8 ↔ kip8test: SRC', () => {

    test('SRC: обёртка isolateLocalStorage в kip8 отсутствует (0 упоминаний)', () => {
        assertEqual(INDEX_SRC.split('isolateLocalStorage').length - 1, 0,
            'упоминаний isolateLocalStorage');
    });

    test('SRC: префикса "kip8test:" нет ни в каком виде', () => {
        assertTrue(INDEX_SRC.indexOf('kip8test:') === -1,
            "литерал 'kip8test:' (префикс обёртки + конкатенации DEV_CACHE_KEY)");
    });

    test('SRC: тест-ключи kip8test_* и /kip8test/# переименованы в прод', () => {
        ['kip8test_devices_cache',
         'kip8test_phonebook_favorites',
         'kip8test_phonebook_notes',
         'kip8test_phonebook_cache',
         '/kip8test/#'].forEach(function (k) {
            assertTrue(INDEX_SRC.indexOf(k) === -1, 'осталось: ' + k);
        });
        assertTrue(INDEX_SRC.indexOf("'kip8_devices_cache'") !== -1, 'ключ кэша приборов');
        assertTrue(INDEX_SRC.indexOf("'kip8_phonebook_favorites'") !== -1, 'ключ избранного справочника');
        assertTrue(INDEX_SRC.indexOf("'kip8_phonebook_cache'") !== -1, 'ключ кэша справочника');
    });
});

// ============================================================
// 2. KipAuth — токен под непрефиксованным ключом
// ============================================================
describe('Task 344 — KipAuth: токен под ключом без префикса', () => {

    test('VM: setToken/getToken/clearToken — РОВНО "kip8_session_token"', () => {
        const START = INDEX_SRC.indexOf('const KipAuth = {');
        assertTrue(START !== -1, 'модуль KipAuth найден');
        const END = INDEX_SRC.indexOf('\n    };', START);
        assertTrue(END !== -1, 'конец модуля KipAuth найден');
        const slice = INDEX_SRC.slice(START, END + 6) + '\nKipAuth;';
        assertTrue(slice.indexOf('setToken') !== -1, 'в срезе есть setToken');
        assertTrue(slice.indexOf('verifyOTP') !== -1, 'в срезе есть verifyOTP');
        assertTrue(slice.indexOf('_verifySessionInBackground') !== -1,
            'срез до конца модуля');

        // Мок localStorage: фиксируем РОВНО те ключи, что были запрошены.
        const store = {};
        const storage = {
            getItem: function (k) {
                return Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null;
            },
            setItem: function (k, v) { store[k] = String(v); },
            removeItem: function (k) { delete store[k]; }
        };
        const sandbox = {
            localStorage: storage,
            console: { log: function () {}, warn: function () {}, error: function () {} }
        };
        sandbox.window = sandbox;
        const KipAuth = vm.runInNewContext(slice, sandbox);

        KipAuth.setToken('t344-token-abc');
        assertEqual(JSON.stringify(Object.keys(store)), '["kip8_session_token"]',
            'записан РОВНО один ключ — без префикса kip8test:');
        assertEqual(KipAuth.getToken(), 't344-token-abc',
            'getToken читает тот же (непрефиксованный) ключ');

        KipAuth.clearToken();
        assertEqual(JSON.stringify(Object.keys(store)), '[]',
            'clearToken удаляет ключ');
    });

    test('SRC: TOKEN_KEY определён один раз = kip8_session_token', () => {
        assertEqual(INDEX_SRC.split("TOKEN_KEY: 'kip8_session_token'").length - 1, 1,
            'определений TOKEN_KEY');
    });
});

// ============================================================
// 3. SW — бамп инвалидации кэша фикса
// ============================================================
describe('Task 344 — SW-бамп фикса', () => {

    test("SW: CACHE_VERSION = 'kipia-v430' (клиенты забудут испорченный index)", () => {
        assertTrue(SW_SRC.indexOf("CACHE_VERSION = 'kipia-v430'") !== -1,
            'v429 установлен');
        assertTrue(SW_SRC.indexOf('kipia-v428') === -1,
            'v428 не остался (двойной бамп?)');
    });
});
