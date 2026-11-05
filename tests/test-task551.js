// tests/test-task551.js
// Task 551 — заявка пользователя: «На андроид приложение хранит
// всю информацию в браузере chrome? если очистить данные браузера,
// то приложение "обнуляется". Как обойти этот момент?»
//
// ЧТО ПРОВЕРЯЕТСЯ:
//   SRC (index.html):
//     — модуль KipSettingsSync: белый список KEYS (14 ключей) +
//       префикс «что нового»; заявка-цитата в комментарии;
//     — restore(): пишет ТОЛЬКО ОТСУТСТВУЮЩИЕ ключи (сервер не
//       перетирает локальные), живое применение темы/вида,
//       сброс ленивых кэшей избранного, тост;
//     — save(): debounce 3 с, watchdog 60 с (страховка писателей
//       без хука), гость не сохраняет;
//     — KipAuth._syncUserSettings: гвард typeof + РОВНО 5 вызовов
//       во всех путях входа (verifyOTP / bootstrap быстрый +
//       медленный / офлайн-повтор / фоновая проверка);
//     — РОВНО 6 хуков scheduleSave у писателей настроек (тема,
//       вид табеля, крест, LCD-информер, метод буёв, реестр
//       авто-«д»/«н»);
//     — НЕ синхронизируются: токен сессии, кэши серверных данных,
//       телефонный справочник (Task 537 уже синхронит), счёт
//       «Сапёра» (Task 546 уже хранит).
//   SRC (UserSettingsArchive.gs / Code.gs):
//     — лист «Настройки» в KIP8_Access, гейт — Sessions.
//       getCurrentUser (сама сессия, email только из сессии);
//     — белый список ALLOWED_KEYS — ЗЕРКАЛО клиента;
//     — роуты userSettings.get / userSettings.save в doPost.
//   VM (сервер): нет токена/битый → no_session; пусто → {};
//     upsert по email (одна строка на пользователя); email из
//     сессии, payload не может подделать; неизвестные ключи
//     отбрасываются; лимиты значений/суммы; аудит без содержимого
//     настроек; ленивое создание листа (шапка/закрепление);
//     init/status идемпотентны; битый JSON — тихо.
//   VM (клиент): _collect (строки + префикс); restore в пустой LS
//     (запись + тема + тост); локальные НЕ перетираются; мусор
//     сервера не пишется; сброс кэшей KipFav; вид табеля
//     применяется; сбой api — тихо, повтор при следующем входе;
//     save собирает и шлёт; гость молчит; debounce один таймер;
//     watchdog ловит изменение снапшота.
//   Санитар: заявка-цитата в обоих исходниках; DEPLOY-док со
//     списком шагов Apps Script; SW-версия репо-детект (гвард
//     следующей версии).
//
// Запуск: через tests/run-all.js (require './test-task551.js').

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { test, describe, assertTrue, assertFalse, assertEqual } = require('./test-helpers.js');

const ROOT = path.join(__dirname, '..');
const INDEX_SRC = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const SW_SRC = fs.readFileSync(path.join(ROOT, 'sw.js'), 'utf8');
const USA_GS_SRC = fs.readFileSync(path.join(ROOT, 'scripts', 'UserSettingsArchive.gs'), 'utf8');
const CODE_SRC = fs.readFileSync(path.join(ROOT, 'scripts', 'Code.gs'), 'utf8');
const DEPLOY_SRC = fs.readFileSync(path.join(ROOT, 'DEPLOY-Task551-user-settings-server-sync.md'), 'utf8');

// Репо-детект (как Task 546): kip8 → kipia-vNNN, kip8test →
// kipia-test-vNNN; неизвестный префикс → SW-ассерты пропускаются
const PFX_MATCH = INDEX_SRC.match(/const PB_FAV_KEY = '(\w+?)_phonebook_favorites'/);
const PFX = PFX_MATCH ? PFX_MATCH[1] : null;
const SW_EXPECTED = { kip8test: 'kipia-test-v758', kip8: 'kipia-v559' }[PFX] || null;
const SW_NEXT = { kip8test: 'kipia-test-v759', kip8: 'kipia-v560' }[PFX] || null;

// ============================================================
// Вырезка объекта по балансу фигурных скобок (как Task 550)
// ============================================================
function extractBalanced(src, startMarker) {
    const start = src.indexOf(startMarker);
    if (start === -1) return null;
    const braceStart = src.indexOf('{', start);
    let depth = 0;
    for (let i = braceStart; i < src.length; i++) {
        if (src[i] === '{') depth++;
        else if (src[i] === '}') {
            depth--;
            if (depth === 0) return src.slice(start, i + 1);
        }
    }
    return null;
}

const KSS_SRC = extractBalanced(INDEX_SRC, 'var KipSettingsSync = {');
assertTrue(!!KSS_SRC, 'KipSettingsSync вырезан из index.html');

// Белый список клиента: KEYS[...]
function clientKeys() {
    const m = KSS_SRC.match(/KEYS:\s*\[([\s\S]*?)\]/);
    const out = [];
    const re = /'([^']+)'/g;
    let mm;
    while ((mm = re.exec(m[1])) !== null) out.push(mm[1]);
    return out;
}

// Белый список сервера: ALLOWED_KEYS { 'k': true, ... }
function serverKeys() {
    const m = USA_GS_SRC.match(/ALLOWED_KEYS:\s*\{([\s\S]*?)\n\s*\}/);
    const out = [];
    const re = /'([^']+)':\s*true/g;
    let mm;
    while ((mm = re.exec(m[1])) !== null) out.push(mm[1]);
    return out;
}

// ============================================================
// 1. SRC: модуль KipSettingsSync (клиент)
// ============================================================
describe('Task 551 — SRC: KipSettingsSync (клиент)', () => {

    test('SRC: заявка-цитата в комментарии модуля', () => {
        const i = INDEX_SRC.indexOf('var KipSettingsSync = {');
        assertTrue(i !== -1, 'модуль есть');
        const head = INDEX_SRC.slice(Math.max(0, i - 3500), i);
        assertTrue(head.indexOf('очистить данные браузера') !== -1,
            'цитата заявки в шапке модуля');
        assertTrue(head.indexOf('"обнуляется"') !== -1 ||
                   head.indexOf('«обнуляется»') !== -1,
            'слово «обнуляется» из заявки');
    });

    test('SRC: белый список KEYS — 14 ключей настроек', () => {
        const keys = clientKeys();
        assertEqual(keys.length, 14, 'ровно 14 ключей: ' + keys.length);
        ['app-theme', 'kip8_ws_view_v1', 'kip8_ws_cross_v1',
         'kip8_ws_lcd_set_v1', 'buoy_calib_method', 'ws_auto_dn_keys',
         'pinnedSubsections', 'kip8_temp_fav_v1', 'kip8_device_fav_v1',
         'kip8_fav_order_v1', 'kip8_device_fav_notes_v1',
         'kip8_flow_fav_v1', 'kip8_flow_fav_order_v1',
         'kip8_detail_panel_width'].forEach(function (k) {
            assertTrue(keys.indexOf(k) !== -1, 'ключ ' + k);
        });
    });

    test('SRC: префикс «что нового» (динамическая версия ключа)', () => {
        assertTrue(KSS_SRC.indexOf("'kip8_whats_new_read_v'") !== -1,
            'префикс в KEY_PREFIXES');
    });

    test('SRC: НЕ синхронизируются токен/кэши/чужие архивы', () => {
        const keys = clientKeys();
        ['kip8_session_token', 'kip8_cached_role', 'kip8_ws_cache_v1',
         'kip8_phonebook_favorites', 'kip8_phonebook_notes',
         'msBestResults', 'kip8_ws_weather_v1', 'ws_pcal_settings_v1']
            .forEach(function (k) {
                assertTrue(keys.indexOf(k) === -1,
                    'ключ ' + k + ' не входит (приватность/кэш/чужой архив)');
            });
    });

    test('SRC: restore — ТОЛЬКО отсутствующие ключи (сервер не перетирает)', () => {
        const i = KSS_SRC.indexOf('restore: function()');
        assertTrue(i !== -1, 'restore есть');
        const body = KSS_SRC.slice(i, i + 2200);
        assertTrue(body.indexOf("cur === null") !== -1,
            'запись только когда локального значения нет');
        assertTrue(body.indexOf('_isKnownKey') !== -1,
            'фильтр неизвестных ключей сервера');
        assertTrue(body.indexOf("_restored = true") !== -1,
            'однократность успешного restore');
    });

    test('SRC: живое применение — тема/вид/сброс ленивых кэшей', () => {
        const i = KSS_SRC.indexOf('_applyRestored: function');
        assertTrue(i !== -1, '_applyRestored есть');
        const body = KSS_SRC.slice(i, i + 3000);
        assertTrue(body.indexOf("data-theme") !== -1, 'тема применяется');
        assertTrue(body.indexOf('_applyView') !== -1, 'вид табеля применяется');
        assertTrue(body.indexOf('KipFav') !== -1 && body.indexOf('_data = null') !== -1,
            'сброс ленивого кэша избранного');
        assertTrue(body.indexOf('showToast') !== -1, 'тост о восстановлении');
    });

    test('SRC: save — debounce 3 с + watchdog 60 с', () => {
        assertEqual((KSS_SRC.match(/SAVE_DEBOUNCE_MS:\s*3000/) || []).length, 1,
            'debounce 3 с');
        assertEqual((KSS_SRC.match(/WATCHDOG_MS:\s*60000/) || []).length, 1,
            'watchdog 60 с');
        const i = KSS_SRC.indexOf('save: function()');
        assertTrue(KSS_SRC.slice(i, i + 700).indexOf("if (!token) return") !== -1,
            'гость не сохраняет');
    });

    test('SRC: KipAuth._syncUserSettings — гвард typeof', () => {
        const i = INDEX_SRC.indexOf('_syncUserSettings: function()');
        assertTrue(i !== -1, 'метод есть');
        const body = INDEX_SRC.slice(i, i + 700);
        assertTrue(body.indexOf("typeof KipSettingsSync !== 'undefined'") !== -1,
            'гвард typeof — старый index.html не падает');
        assertTrue(body.indexOf('KipSettingsSync.restore()') !== -1,
            'вызывает restore');
    });

    test('SRC: РОВНО 5 вызовов _syncUserSettings — все пути входа', () => {
        const calls = (INDEX_SRC.match(/self\._syncUserSettings\(\);/g) || []).length;
        assertEqual(calls, 5, '5 путей: verifyOTP, bootstrap ×2, офлайн-повтор, фоновая проверка: ' + calls);
        // каждый вызов — сразу после закрепления хранилища (метка
        // пути входа), комментарий Task 551 — в 1+ строках
        const pairs = (INDEX_SRC.match(/self\._requestPersistentStorage\(\);\s*\n(\s*\/\/[^\n]*\n)+\s*self\._syncUserSettings\(\);/g) || []).length;
        assertEqual(pairs, 5, 'вызовы стоят сразу после закрепления хранилища: ' + pairs);
    });

    test('SRC: РОВНО 6 хуков scheduleSave у писателей настроек', () => {
        const hooks = (INDEX_SRC.match(/KipSettingsSync\.scheduleSave\(\);/g) || []).length;
        assertEqual(hooks, 6, 'тема, вид, крест, LCD, буи, реестр авто-«д»/«н»: ' + hooks);
        // каждый хук — под меткой Task 551
        const labeled = (INDEX_SRC.match(/\/\/ Task 551[^\n]*\n(\s*\/\/[^\n]*\n)*\s*if \(typeof KipSettingsSync/g) || []).length;
        assertEqual(labeled, 6, 'все хуки с комментарием Task 551: ' + labeled);
    });

    test('SRC: хук в toggleTheme (тема)', () => {
        const i = INDEX_SRC.indexOf('function toggleTheme()');
        const body = INDEX_SRC.slice(i, i + 700);
        assertTrue(body.indexOf("localStorage.setItem('app-theme'") !== -1,
            'тема пишется в LS');
        assertTrue(body.indexOf('KipSettingsSync.scheduleSave();') !== -1,
            'хук сохранения на сервер');
    });

    test('SRC: хук в selectCalibMethod (метод калибровки буёв)', () => {
        const i = INDEX_SRC.indexOf('function selectCalibMethod(m)');
        const body = INDEX_SRC.slice(i, i + 500);
        assertTrue(body.indexOf("'buoy_calib_method'") !== -1, 'ключ метода');
        assertTrue(body.indexOf('KipSettingsSync.scheduleSave();') !== -1, 'хук');
    });

    test('SRC: хук в toggleCross (перекрёстная подсветка)', () => {
        const i = INDEX_SRC.indexOf('toggleCross: function()');
        const body = INDEX_SRC.slice(i, i + 900);
        assertTrue(body.indexOf("'kip8_ws_cross_v1'") !== -1, 'ключ креста');
        assertTrue(body.indexOf('KipSettingsSync.scheduleSave();') !== -1, 'хук');
    });

    test('SRC: хук в cycleView (вид табеля)', () => {
        const i = INDEX_SRC.indexOf('cycleView: function()');
        const body = INDEX_SRC.slice(i, i + 1600);
        assertTrue(body.indexOf("'kip8_ws_view_v1'") !== -1, 'ключ вида');
        assertTrue(body.indexOf('KipSettingsSync.scheduleSave();') !== -1, 'хук');
    });

    test('SRC: хук в WsLcdClock._setSave (настройки информера)', () => {
        const i = INDEX_SRC.indexOf('_setSave: function(s)');
        const body = INDEX_SRC.slice(i, i + 500);
        assertTrue(body.indexOf('this._SET_KEY') !== -1, 'ключ информера');
        assertTrue(body.indexOf('KipSettingsSync.scheduleSave();') !== -1, 'хук');
    });

    test('SRC: хук в _autoDnKeysSave (реестр авто-«д»/«н»)', () => {
        const i = INDEX_SRC.indexOf('_autoDnKeysSave: function(mk)');
        const body = INDEX_SRC.slice(i, i + 1100);
        assertTrue(body.indexOf("'ws_auto_dn_keys'") !== -1, 'ключ реестра');
        assertTrue(body.indexOf('KipSettingsSync.scheduleSave();') !== -1, 'хук');
        assertTrue(body.indexOf('надгробия Task 458') !== -1,
            'комментарий: защита «в»-надгробий');
    });
});

// ============================================================
// 2. SRC: сервер (UserSettingsArchive.gs + Code.gs)
// ============================================================
describe('Task 551 — SRC: сервер UserSettingsArchive.gs', () => {

    test('SRC: лист «Настройки» в KIP8_Access (тот же ID)', () => {
        assertEqual((USA_GS_SRC.match(/SHEET: 'Настройки'/) || []).length, 1,
            'имя листа');
        assertEqual((USA_GS_SRC.match(/1TmmNZLUArWH38F6NX0gMGar8LMNMQomm_FaGZv9osyk/) || []).length, 1,
            'ID таблицы KIP8_Access (как RoleMatrix/Сапёр)');
        assertEqual((USA_GS_SRC.match(/HEADERS: \['email', 'имя', 'данные', 'обновлено'\]/) || []).length, 1,
            'заголовки листа');
    });

    test('SRC: белый список сервера — ЗЕРКАЛО клиента', () => {
        const c = clientKeys().sort().join('|');
        const s = serverKeys().sort().join('|');
        assertEqual(s, c, 'сервер и клиент синхронизируют одни и те же ключи');
    });

    test('SRC: гейт — Sessions.getCurrentUser (сама сессия)', () => {
        const i = USA_GS_SRC.indexOf('_requireSession: function(token)');
        assertTrue(i !== -1, 'гейт есть');
        const body = USA_GS_SRC.slice(i, i + 700);
        assertTrue(body.indexOf('Sessions.getCurrentUser') !== -1,
            'сессия проверяется через Sessions');
        assertTrue(body.indexOf('no_session') !== -1, 'отказ без сессии');
    });

    test('SRC: лимиты валидации — значение 16 КБ / сумма 128 КБ', () => {
        assertEqual((USA_GS_SRC.match(/MAX_VALUE_LEN: 16384/) || []).length, 1,
            'лимит значения');
        assertEqual((USA_GS_SRC.match(/MAX_TOTAL_LEN: 131072/) || []).length, 1,
            'лимит суммы');
    });

    test('SRC: аудит USER_SETTINGS_SAVE БЕЗ содержимого настроек', () => {
        const i = USA_GS_SRC.indexOf("Utils.audit(g.user.email, 'USER_SETTINGS_SAVE'");
        assertTrue(i !== -1, 'код аудита есть');
        const body = USA_GS_SRC.slice(i, i + 400);
        assertTrue(body.indexOf('приватность') !== -1,
            'комментарий: содержимое не пишется');
    });

    test('SRC: роуты userSettings.get/save в Code.gs', () => {
        assertEqual((CODE_SRC.match(/case 'userSettings\.get':/) || []).length, 1,
            'роут get');
        assertEqual((CODE_SRC.match(/case 'userSettings\.save':/) || []).length, 1,
            'роут save');
        assertEqual((CODE_SRC.match(/UserSettingsArchive\.getMySettings\(payload\)/) || []).length, 1,
            'делегация get');
        assertEqual((CODE_SRC.match(/UserSettingsArchive\.saveMySettings\(payload\)/) || []).length, 1,
            'делегация save');
        assertTrue(CODE_SRC.indexOf('Task 551') !== -1,
            'метка задачи в маршрутизации');
    });

    test('SRC: init/status — идемпотентные диагностические функции', () => {
        assertEqual((USA_GS_SRC.match(/function userSettingsInit\(\)/) || []).length, 1,
            'userSettingsInit');
        assertEqual((USA_GS_SRC.match(/function userSettingsStatus\(\)/) || []).length, 1,
            'userSettingsStatus');
    });
});

// ============================================================
// 3. VM: сервер UserSettingsArchive.gs (мок GAS)
// ============================================================

class MockSheet551 {
    constructor(name, rows) {
        this._name = name;
        this.rows = rows || [];
        this.frozenRows = 0;
        this.formats = {};
        this.merges = [];
        this.widths = {};
    }
    getName() { return this._name; }
    getLastRow() { return this.rows.length; }
    getMaxRows() { return Math.max(this.rows.length, 200); }
    appendRow(row) { this.rows.push(row.slice()); return this; }
    setFrozenRows(n) { this.frozenRows = n; return this; }
    setColumnWidth(c, px) { this.widths[c] = px; return this; }
    getRange(row, col, numRows, numCols) {
        numRows = numRows || 1; numCols = numCols || 1;
        const self = this;
        return {
            getValues() {
                const out = [];
                for (let r = row; r < row + numRows; r++) {
                    const line = [];
                    for (let c = col; c < col + numCols; c++) {
                        const rr = self.rows[r - 1];
                        line.push(rr ? (rr[c - 1] === undefined ? '' : rr[c - 1]) : '');
                    }
                    out.push(line);
                }
                return out;
            },
            getValue() {
                const rr = self.rows[row - 1];
                return rr ? (rr[col - 1] === undefined ? '' : rr[col - 1]) : '';
            },
            setValue(v) {
                while (self.rows.length < row) self.rows.push([]);
                if (!self.rows[row - 1]) self.rows[row - 1] = [];
                self.rows[row - 1][col - 1] = v;
                return this;
            },
            setValues(vals) {
                for (let i = 0; i < vals.length; i++) {
                    const r = row + i;
                    while (self.rows.length < r) self.rows.push([]);
                    for (let c = 0; c < vals[i].length; c++) {
                        self.rows[r - 1][col - 1 + c] = vals[i][c];
                    }
                }
                return this;
            },
            setNumberFormat(f) { self.formats[row + ',' + col] = f; return this; },
            setBackground() { return this; },
            setFontColor() { return this; },
            setFontWeight() { return this; },
            setFontStyle() { return this; },
            merge() { self.merges.push(row + ':' + col); return this; }
        };
    }
}

class MockSS551 {
    constructor(name, id) {
        this._name = name;
        this._id = id;
        this.sheets = [];
    }
    getName() { return this._name; }
    getId() { return this._id; }
    getUrl() { return 'https://docs.google.com/spreadsheets/d/' + this._id + '/edit'; }
    getSheets() { return this.sheets.slice(); }
    getSheetByName(n) {
        for (const s of this.sheets) if (s.getName() === n) return s;
        return null;
    }
    insertSheet(name) {
        const s = new MockSheet551(name, []);
        this.sheets.push(s);
        return s;
    }
}

function isoOf551(d) {
    const p = n => (n < 10 ? '0' + n : '' + n);
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) +
           'T' + p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds());
}

function makeServerEnv551(opts) {
    opts = opts || {};
    const state = { audit: [], now: new Date('2026-11-05T10:00:00') };
    const kip8Access = new MockSS551('KIP8_Access',
        '1TmmNZLUArWH38F6NX0gMGar8LMNMQomm_FaGZv9osyk');
    const files = {};
    files[kip8Access.getId()] = kip8Access;
    const SpreadsheetApp = { openById: (id) => files[id] || null };
    const LockService = {
        getScriptLock: () => ({ waitLock() {}, releaseLock() {} })
    };
    const Session = { getScriptTimeZone: () => 'Asia/Novosibirsk' };
    const Utilities = {
        formatDate: () => isoOf551(state.now)
    };
    const Utils = {
        audit: (email, action, ip, ua, details) => {
            state.audit.push({ email: email, action: action, details: details });
        },
        getRows: () => (opts.users || [
            { email: 'user@example.com', name: 'Иванов Иван' },
            { email: 'other@example.com', name: 'Петров Пётр' }
        ])
    };
    // Гейт Task 551 — сама сессия: email ТОЛЬКО из токена
    const Sessions = {
        getCurrentUser: (token) => {
            if (!token || token === 'bad') throw new Error('no_session');
            const email = opts.user ||
                (token === 'tok2' ? 'other@example.com' : 'user@example.com');
            return { userId: 1, email: email, role: 'КИП8' };
        }
    };
    return { state, kip8Access, SpreadsheetApp, LockService,
             Session, Utilities, Utils, Sessions };
}

function loadUSA(env) {
    const factory = new Function(
        'SpreadsheetApp', 'LockService', 'Session', 'Utilities',
        'Utils', 'Sessions', 'Logger',
        USA_GS_SRC + '\nreturn { USA: UserSettingsArchive, ' +
        'init: userSettingsInit, status: userSettingsStatus };');
    return factory(env.SpreadsheetApp, env.LockService, env.Session,
                   env.Utilities, env.Utils, env.Sessions,
                   { log: function () {} });
}

const SAVE_OK = { token: 'tok', settings: {
    'app-theme': 'dark',
    'kip8_ws_view_v1': 'shift',
    'kip8_ws_cross_v1': '1',
    'kip8_ws_lcd_set_v1': '{"weather":true}',
    'buoy_calib_method': 'with_buoy',
    'pinnedSubsections': '["dashboard"]',
    'kip8_device_fav_v1': '{"123":1}',
    'kip8_whats_new_read_v3.0.0': '1'
} };

describe('Task 551 — VM: сервер (гейт сессии)', () => {

    test('VM: нет токена → no_session (get и save)', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        const g = U.USA.getMySettings({ settings: {} });
        assertFalse(g.ok, 'get без токена — отказ');
        assertEqual(g.error, 'no_session', 'код no_session');
        const s = U.USA.saveMySettings({ settings: { 'app-theme': 'dark' } });
        assertFalse(s.ok, 'save без токена — отказ');
        assertEqual(s.error, 'no_session', 'код no_session (save)');
    });

    test('VM: битый токен → no_session (Sessions бросил)', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        const g = U.USA.getMySettings({ token: 'bad' });
        assertFalse(g.ok, 'отказ');
        assertEqual(g.error, 'no_session', 'бросок пойман, не упал наружу');
    });

    test('VM: get при пустом архиве → settings {} (тихая деградация)', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        const g = U.USA.getMySettings({ token: 'tok' });
        assertTrue(g.ok, 'успех');
        assertEqual(g.data.srvVer, '551', 'версия серверного кода');
        assertEqual(JSON.stringify(g.data.settings), '{}', 'пусто, без ошибки');
    });
});

describe('Task 551 — VM: сервер (сохранение и чтение)', () => {

    test('VM: save → строка добавлена; get возвращает настройки', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        const s = U.USA.saveMySettings(SAVE_OK);
        assertTrue(s.ok, 'save ок');
        assertEqual(s.data.saved, true, 'флаг saved');
        assertEqual(s.data.keys, 8, '8 известных ключей');
        const sheet = env.kip8Access.getSheetByName('Настройки');
        assertTrue(!!sheet, 'лист создан лениво');
        assertEqual(sheet.rows.length, 4, 'титул+описание+шапка+1 строка данных');
        assertEqual(sheet.rows[3][0], 'user@example.com', 'email из сессии');
        assertEqual(sheet.rows[3][1], 'Иванов Иван', 'имя-снимок из users');
        const g = U.USA.getMySettings({ token: 'tok' });
        assertEqual(g.data.settings['app-theme'], 'dark', 'тема вернулась');
        assertEqual(g.data.settings['kip8_ws_view_v1'], 'shift', 'вид вернулся');
        assertEqual(g.data.settings['kip8_whats_new_read_v3.0.0'], '1',
            'префиксный ключ прошёл');
    });

    test('VM: повторный save → UPSERT (одна строка на пользователя)', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        U.USA.saveMySettings(SAVE_OK);
        const s2 = U.USA.saveMySettings({ token: 'tok',
            settings: { 'app-theme': 'light' } });
        assertTrue(s2.ok, 'второй save ок');
        const sheet = env.kip8Access.getSheetByName('Настройки');
        assertEqual(sheet.rows.length, 4, 'строка ОБНОВЛЕНА, не добавлена');
        const g = U.USA.getMySettings({ token: 'tok' });
        assertEqual(g.data.settings['app-theme'], 'light', 'новое значение');
        assertEqual(g.data.settings['kip8_ws_view_v1'], undefined,
            'старых ключей нет — JSON заменён целиком');
    });

    test('VM: изоляция — email из сессии, payload не может подделать', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        // tok2 → other@example.com, payload хочет чужой email
        const s = U.USA.saveMySettings({ token: 'tok2', email: 'user@example.com',
            settings: { 'app-theme': 'dark' } });
        assertTrue(s.ok, 'save ок');
        const sheet = env.kip8Access.getSheetByName('Настройки');
        assertEqual(sheet.rows.length, 4, 'строка данных одна (сохранение единственное)');
        assertEqual(sheet.rows[3][0], 'other@example.com',
            'email взят из СЕССИИ, не из payload');
        assertEqual(sheet.rows[3][1], 'Петров Пётр', 'имя-снимок владельца сессии');
        const g2 = U.USA.getMySettings({ token: 'tok2' });
        assertEqual(g2.data.settings['app-theme'], 'dark', 'свои настройки видит');
        const g1 = U.USA.getMySettings({ token: 'tok' });
        assertEqual(g1.data.settings['app-theme'], undefined,
            'чужие настройки НЕ видны');
        // строка «другого» не затирает строку «своего» — две строки
        U.USA.saveMySettings({ token: 'tok', settings: { 'app-theme': 'light' } });
        assertEqual(sheet.rows.length, 5, 'две строки: user + other');
        assertEqual(sheet.rows[4][0], 'user@example.com', 'своя строка добавлена');
        assertEqual(sheet.rows[3][0], 'other@example.com', 'чужая строка не тронута');
    });

    test('VM: неизвестные ключи молча отбрасываются', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        const s = U.USA.saveMySettings({ token: 'tok', settings: {
            'app-theme': 'dark',
            'evil_key': 'x'.repeat(100),
            'kip8_session_token': 'STOLEN'
        } });
        assertTrue(s.ok, 'save ок');
        assertEqual(s.data.keys, 1, 'учтён только известный ключ');
        const g = U.USA.getMySettings({ token: 'tok' });
        assertEqual(g.data.settings['evil_key'], undefined, 'мусор не хранится');
        assertEqual(g.data.settings['kip8_session_token'], undefined,
            'токен в архив не протаскивается');
    });

    test('VM: битый JSON в листе — тихо, как пустые настройки', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        U.USA.saveMySettings(SAVE_OK);
        const sheet = env.kip8Access.getSheetByName('Настройки');
        sheet.rows[3][2] = '{битый json';
        const g = U.USA.getMySettings({ token: 'tok' });
        assertTrue(g.ok, 'не падает');
        assertEqual(JSON.stringify(g.data.settings), '{}', 'пусто');
    });
});

describe('Task 551 — VM: сервер (валидация и лимиты)', () => {

    test('VM: settings не объект → invalid_settings', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        const s = U.USA.saveMySettings({ token: 'tok', settings: 'dark' });
        assertFalse(s.ok, 'отказ');
        assertEqual(s.error, 'invalid_settings', 'код');
        assertTrue(!!s.message, 'пояснение для клиента');
    });

    test('VM: значение не строка → invalid_value', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        const s = U.USA.saveMySettings({ token: 'tok',
            settings: { 'app-theme': 42 } });
        assertFalse(s.ok, 'отказ');
        assertEqual(s.error, 'invalid_value', 'код');
    });

    test('VM: значение больше 16 КБ → value_too_large', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        const s = U.USA.saveMySettings({ token: 'tok',
            settings: { 'kip8_device_fav_v1': 'x'.repeat(16385) } });
        assertFalse(s.ok, 'отказ');
        assertEqual(s.error, 'value_too_large', 'код');
    });

    test('VM: сумма больше 128 КБ → settings_too_large', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        const big = {};
        for (let i = 0; i < 12; i++) {
            big['pinnedSubsections' + (i === 0 ? '' : '')] = undefined;
        }
        // валидные ключи, но большие значения: 9 × 15 КБ > 128 КБ
        const s = U.USA.saveMySettings({ token: 'tok', settings: {
            'app-theme': 'x'.repeat(15000),
            'kip8_ws_view_v1': 'x'.repeat(15000),
            'kip8_ws_cross_v1': 'x'.repeat(15000),
            'kip8_ws_lcd_set_v1': 'x'.repeat(15000),
            'buoy_calib_method': 'x'.repeat(15000),
            'pinnedSubsections': 'x'.repeat(15000),
            'kip8_temp_fav_v1': 'x'.repeat(15000),
            'kip8_device_fav_v1': 'x'.repeat(15000),
            'kip8_flow_fav_v1': 'x'.repeat(15000)
        } });
        assertFalse(s.ok, 'отказ');
        assertEqual(s.error, 'settings_too_large', 'код суммы');
    });

    test('VM: _escCell — защита от формул', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        assertEqual(U.USA._escCell('=cmd()'), "'=cmd()", 'формула экранирована');
        assertEqual(U.USA._escCell('dark'), 'dark', 'обычная строка как есть');
    });
});

describe('Task 551 — VM: сервер (лист, init, аудит)', () => {

    test('VM: ленивое создание листа — закрепление и шапка', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        U.USA.saveMySettings({ token: 'tok', settings: { 'app-theme': 'dark' } });
        const sheet = env.kip8Access.getSheetByName('Настройки');
        assertEqual(sheet.frozenRows, 3, 'закреплено 3 строки (урок v3)');
        assertEqual(sheet.rows[2].join('|'), 'email|имя|данные|обновлено',
            'заголовки в строке 3');
        assertEqual(sheet.merges.length, 2, 'титул и описание объединены');
    });

    test('VM: init идемпотентен — повтор не создаёт второй лист', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        const r1 = U.init();
        assertTrue(r1.ok && r1.exists, 'первый init ок');
        assertEqual(r1.rows, 0, 'строк данных нет');
        const r2 = U.init();
        assertTrue(r2.ok && r2.exists, 'второй init ок');
        const count = env.kip8Access.sheets.filter(
            s => s.getName() === 'Настройки').length;
        assertEqual(count, 1, 'лист один');
    });

    test('VM: status — читает лист и шапку', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        U.USA.saveMySettings(SAVE_OK);
        const st = U.status();
        assertTrue(st.spreadsheet, 'таблица открыта');
        assertTrue(st.sheet, 'лист есть');
        assertEqual(st.rows, 1, 'одна строка данных');
        assertTrue(st.headersOk, 'шапка совпала');
        assertEqual(st.schemaVersion, 1, 'версия схемы');
    });

    test('VM: аудит USER_SETTINGS_SAVE — без содержимого настроек', () => {
        const env = makeServerEnv551();
        const U = loadUSA(env);
        U.USA.saveMySettings(SAVE_OK);
        const rec = env.state.audit.find(a => a.action === 'USER_SETTINGS_SAVE');
        assertTrue(!!rec, 'запись аудита есть');
        assertEqual(rec.email, 'user@example.com', 'email автора');
        assertTrue(rec.details.indexOf('8 кл.') !== -1,
            'число ключей в деталях');
        assertTrue(rec.details.indexOf('app-theme') === -1 &&
                   rec.details.indexOf('dark') === -1,
            'сами настройки в аудит НЕ пишутся (приватность)');
    });
});

// ============================================================
// 4. VM: клиент KipSettingsSync (мок localStorage/KipAuth/DOM)
// ============================================================

function makeClientEnv551(opts) {
    opts = opts || {};
    const store = Object.assign({}, opts.initial || {});
    const apiCalls = [];
    const toasts = [];
    const themeAttrs = [];
    const timers = { timeout: null, interval: null };
    let apiImpl = opts.apiImpl || function () {
        return Promise.resolve({ srvVer: '551',
            settings: opts.serverSettings || {} });
    };
    const state = {
        token: (opts.token !== undefined) ? opts.token : 'tok'
    };
    const ctx = {
        Promise: Promise, JSON: JSON, Math: Math, Date: Date,
        console: { warn: function () {}, log: function () {} },
        localStorage: {
            getItem: k => (k in store ? store[k] : null),
            setItem: (k, v) => { store[k] = String(v); },
            removeItem: k => { delete store[k]; },
            key: i => Object.keys(store)[i] || null,
            get length() { return Object.keys(store).length; }
        },
        KipAuth: {
            getToken: function () { return state.token; },
            api: function (action, payload) {
                apiCalls.push({ action: action, payload: payload });
                return apiImpl(action, payload);
            }
        },
        document: {
            documentElement: {
                setAttribute: function (n, v) { themeAttrs.push([n, v]); }
            }
        },
        showToast: function (msg) { toasts.push(msg); },
        setTimeout: function (fn, ms) {
            timers.timeout = { fn: fn, ms: ms };
            return 1;
        },
        clearTimeout: function () { timers.timeout = null; },
        setInterval: function (fn, ms) {
            timers.interval = { fn: fn, ms: ms };
            return 2;
        },
        clearInterval: function () { timers.interval = null; }
    };
    if (opts.workSchedule) ctx.WorkSchedule = opts.workSchedule;
    if (opts.kipFav) ctx.KipFav = opts.kipFav;
    vm.createContext(ctx);
    vm.runInContext(KSS_SRC + '\nthis.KSS = KipSettingsSync;', ctx,
        { filename: 'index.html-KipSettingsSync' });
    return {
        KSS: ctx.KSS, store: store, apiCalls: apiCalls, toasts: toasts,
        themeAttrs: themeAttrs, timers: timers, state: state,
        setApiImpl: function (fn) { apiImpl = fn; }
    };
}

const flush = () => new Promise(r => setTimeout(r, 0));

describe('Task 551 — VM: клиент (_collect)', () => {

    test('VM: _collect — строки LS, отсутствующие не входят', () => {
        const e = makeClientEnv551({ initial: {
            'app-theme': 'dark',
            'kip8_ws_view_v1': 'shift',
            'kip8_session_token': 'SECRET'
        } });
        const c = e.KSS._collect();
        assertEqual(c['app-theme'], 'dark', 'тема');
        assertEqual(c['kip8_ws_view_v1'], 'shift', 'вид');
        assertEqual(c['kip8_ws_cross_v1'], undefined, 'отсутствующий не входит');
        assertEqual(c['kip8_session_token'], undefined,
            'токен НИКОГДА не собирается');
    });

    test('VM: _collect — префиксный ключ «что нового»', () => {
        const e = makeClientEnv551({ initial: {
            'kip8_whats_new_read_v3.0.0': '1',
            'kip8_whats_new_read_v2.9.9': '1',
            'skip_me': 'x'
        } });
        const c = e.KSS._collect();
        assertEqual(c['kip8_whats_new_read_v3.0.0'], '1', 'текущая версия');
        assertEqual(c['kip8_whats_new_read_v2.9.9'], '1', 'старая версия тоже');
        assertEqual(c['skip_me'], undefined, 'посторонний ключ мимо');
    });

    test('VM: _isKnownKey — белый список и префиксы', () => {
        const e = makeClientEnv551();
        assertTrue(e.KSS._isKnownKey('app-theme'), 'известный');
        assertTrue(e.KSS._isKnownKey('kip8_whats_new_read_v9.9.9'),
            'префиксный');
        assertFalse(e.KSS._isKnownKey('kip8_session_token'), 'токен — нет');
        assertFalse(e.KSS._isKnownKey('evil'), 'мусор — нет');
    });
});

describe('Task 551 — VM: клиент (restore после входа)', () => {

    test('VM: пустой LS → все ключи записаны, тема применена, тост', async () => {
        const e = makeClientEnv551({ serverSettings: {
            'app-theme': 'dark',
            'kip8_ws_view_v1': 'shift',
            'kip8_ws_cross_v1': '1',
            'pinnedSubsections': '["dashboard"]'
        } });
        e.KSS.restore();
        await flush();
        assertEqual(e.store['app-theme'], 'dark', 'тема записана');
        assertEqual(e.store['kip8_ws_view_v1'], 'shift', 'вид записан');
        assertEqual(e.store['kip8_ws_cross_v1'], '1', 'крест записан');
        assertEqual(e.apiCalls.length, 1, 'один запрос userSettings.get');
        assertEqual(e.apiCalls[0].action, 'userSettings.get', 'правильный экшен');
        assertEqual(e.apiCalls[0].payload.token, 'tok', 'токен передан');
        assertTrue(e.themeAttrs.some(a => a[0] === 'data-theme' && a[1] === 'dark'),
            'тема применена к DOM');
        assertTrue(e.toasts.length === 1 && /восстановлены/.test(e.toasts[0]),
            'тост о восстановлении');
        assertTrue(e.KSS._restored, 'флаг однократности');
    });

    test('VM: ЛОКАЛЬНЫЕ настройки не перетираются сервером', async () => {
        const e = makeClientEnv551({
            initial: { 'app-theme': 'light' },
            serverSettings: { 'app-theme': 'dark', 'kip8_ws_view_v1': 'day' }
        });
        e.KSS.restore();
        await flush();
        assertEqual(e.store['app-theme'], 'light',
            'локальное значение сохранено (сервер не перетирает)');
        assertEqual(e.store['kip8_ws_view_v1'], 'day',
            'отсутствующий восстановлен');
        assertFalse(e.themeAttrs.some(a => a[1] === 'dark'),
            'чужая тема НЕ применена');
    });

    test('VM: мусор сервера не пишется (белый список клиента)', async () => {
        const e = makeClientEnv551({ serverSettings: {
            'app-theme': 'dark',
            'evil_key': 'x',
            'kip8_session_token': 'STOLEN',
            'app-theme-x': 'y'
        } });
        e.KSS.restore();
        await flush();
        assertEqual(e.store['app-theme'], 'dark', 'известный записан');
        assertEqual(e.store['evil_key'], undefined, 'мусор мимо');
        assertEqual(e.store['kip8_session_token'], undefined,
            'токен из сервера не пишется');
    });

    test('VM: restore без токена — API не дёргается', async () => {
        const e = makeClientEnv551({ token: '' });
        e.KSS.restore();
        await flush();
        assertEqual(e.apiCalls.length, 0, 'тишина (гость)');
        assertFalse(e.KSS._restored, 'флаг не ставится');
    });

    test('VM: сбой API (старый сервер) — тихо, повтор при следующем входе', async () => {
        const e = makeClientEnv551({ apiImpl: function () {
            return Promise.reject(new Error('Unknown action: userSettings.get'));
        } });
        e.KSS.restore();
        await flush();
        assertEqual(e.apiCalls.length, 1, 'попытка была');
        assertFalse(e.KSS._restored, 'флаг НЕ ставится — повтор возможен');
        assertEqual(e.toasts.length, 0, 'без тостов (тихая деградация)');
        // сервер обновили — следующий вход восстанавливает
        e.setApiImpl(function () {
            return Promise.resolve({ srvVer: '551',
                settings: { 'app-theme': 'dark' } });
        });
        e.KSS.restore();
        await flush();
        assertEqual(e.store['app-theme'], 'dark', 'повтор удался');
        assertTrue(e.KSS._restored, 'флаг после успеха');
    });

    test('VM: сброс ленивого кэша KipFav при восстановлении избранного', async () => {
        const kipFav = { _data: { '999': 1 } };
        const e = makeClientEnv551({
            kipFav: kipFav,
            serverSettings: { 'kip8_device_fav_v1': '{"123":1}' }
        });
        e.KSS.restore();
        await flush();
        assertEqual(e.store['kip8_device_fav_v1'], '{"123":1}', 'значение в LS');
        assertEqual(kipFav._data, null,
            'кэш сброшен — модуль перечитает localStorage');
    });

    test('VM: вид табеля применяется к инициализированному WorkSchedule', async () => {
        const applied = [];
        const ws = { _view: 'full', _EMPLOYEES: [{}],
            _applyView: function (o) { applied.push(this._view + '/' + !!o.rerender); } };
        const e = makeClientEnv551({
            workSchedule: ws,
            serverSettings: { 'kip8_ws_view_v1': 'shift' }
        });
        e.KSS.restore();
        await flush();
        assertEqual(ws._view, 'shift', 'вид переключен');
        assertEqual(applied.length, 1, '_applyView вызван');
        assertEqual(applied[0], 'shift/true', 'с перерисовкой');
    });
});

describe('Task 551 — VM: клиент (save и watchdog)', () => {

    test('VM: save — собирает и отправляет настройки', async () => {
        const e = makeClientEnv551({ initial: {
            'app-theme': 'dark',
            'kip8_ws_view_v1': 'shift'
        } });
        e.KSS.save();
        await flush();
        assertEqual(e.apiCalls.length, 1, 'один запрос');
        assertEqual(e.apiCalls[0].action, 'userSettings.save', 'экшен');
        assertEqual(e.apiCalls[0].payload.settings['app-theme'], 'dark',
            'тема отправлена');
        assertEqual(e.apiCalls[0].payload.settings['kip8_ws_view_v1'], 'shift',
            'вид отправлен');
        assertEqual(e.apiCalls[0].payload.token, 'tok', 'токен передан');
    });

    test('VM: гость (нет токена) — save молчит', async () => {
        const e = makeClientEnv551({ token: '', initial: { 'app-theme': 'dark' } });
        e.KSS.save();
        await flush();
        assertEqual(e.apiCalls.length, 0, 'запросов нет');
    });

    test('VM: scheduleSave — debounce: один таймер на серию вызовов', async () => {
        const e = makeClientEnv551({ initial: { 'app-theme': 'dark' } });
        e.KSS.scheduleSave();
        e.KSS.scheduleSave();
        e.KSS.scheduleSave();
        assertEqual(e.apiCalls.length, 0, 'сохранения ещё нет (ждём 3 с)');
        assertTrue(!!e.timers.timeout, 'таймер взведён');
        assertEqual(e.timers.timeout.ms, 3000, 'задержка 3 с');
        e.timers.timeout.fn();
        await flush();
        assertEqual(e.apiCalls.length, 1, 'РОвно один запрос после отката');
    });

    test('VM: watchdog ловит изменение снапшота', async () => {
        const e = makeClientEnv551({ serverSettings: {} });
        e.KSS.restore();
        await flush();
        assertTrue(!!e.timers.interval, 'watchdog запущен после restore');
        assertEqual(e.timers.interval.ms, 60000, 'интервал 60 с');
        // пользователь меняет тему (писатель без хука — симуляция)
        e.store['app-theme'] = 'dark';
        e.timers.interval.fn();
        await flush();
        const saves = e.apiCalls.filter(c => c.action === 'userSettings.save');
        assertEqual(saves.length, 1, 'watchdog отправил изменение');
        assertEqual(saves[0].payload.settings['app-theme'], 'dark',
            'новая тема ушла на сервер');
        // без изменений — повторной отправки нет
        e.timers.interval.fn();
        await flush();
        const saves2 = e.apiCalls.filter(c => c.action === 'userSettings.save');
        assertEqual(saves2.length, 1, 'снапшот совпал — тишина');
    });

    test('VM: watchdog после выхода (нет токена) — не дёргает API', async () => {
        const e = makeClientEnv551({ serverSettings: {} });
        e.KSS.restore();
        await flush();
        e.state.token = '';
        e.store['app-theme'] = 'dark';
        e.timers.interval.fn();
        await flush();
        const saves = e.apiCalls.filter(c => c.action === 'userSettings.save');
        assertEqual(saves.length, 0, 'выход — сохранений нет');
    });
});

// ============================================================
// 5. Санитар + SW
// ============================================================
describe('Task 551 — санитар', () => {

    test('санитар: заявка-цитата в серверном модуле', () => {
        assertTrue(USA_GS_SRC.indexOf('очистить данные браузера') !== -1,
            'заявка процитирована в UserSettingsArchive.gs');
        assertTrue(USA_GS_SRC.indexOf('"обнуляется"') !== -1,
            'мотив задачи');
    });

    test('санитар: DEPLOY-док со списком шагов Apps Script', () => {
        assertTrue(DEPLOY_SRC.indexOf('UserSettingsArchive.gs') !== -1,
            'файл модуля назван');
        assertTrue(DEPLOY_SRC.indexOf('userSettingsInit') !== -1,
            'шаг запуска init');
        assertTrue(DEPLOY_SRC.indexOf('New version') !== -1 ||
                   DEPLOY_SRC.indexOf('Deploy') !== -1,
            'шаг нового деплоя');
    });

    test('санитар: SW-версия актуальна (репо-детект)', () => {
        if (!SW_EXPECTED) return; // неизвестный репо — пропускаем
        assertTrue(SW_SRC.indexOf(SW_EXPECTED) !== -1,
            'sw.js содержит ' + SW_EXPECTED);
        assertTrue(SW_SRC.indexOf(SW_NEXT) === -1,
            'следующей версии ' + SW_NEXT + ' нет (гвард)');
        // шапка истории sw.js НЕ тронута (окна истории версий
        // Tasks 461–501 не смещаются — практика Task 523+)
        const i = SW_SRC.indexOf("const CACHE_VERSION = '" + SW_EXPECTED + "';");
        assertTrue(i !== -1, 'строка CACHE_VERSION на месте');
        assertTrue(SW_SRC.slice(Math.max(0, i - 400), i)
            .indexOf('Task 551') === -1,
            'новый комментарий в шапку НЕ добавлялся (окна целы)');
    });
});
