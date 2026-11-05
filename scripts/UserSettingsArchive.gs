// ============================================================
// UserSettingsArchive.gs — Настройки пользователя: серверный
// архив по email (Task 551)
// ============================================================
// Разворачивать в ТОМ ЖЕ Apps Script-проекте, где Code.gs,
// Utils.gs, Sessions.gs (проект развёртывания AKfycbyt… —
// ОДИН бэкенд на kip8 и kip8test).
//
// В Code.gs (doPost) добавить два case (см. scripts/Code.gs —
// эталон уже обновлён):
//   case 'userSettings.get':
//     return _json(UserSettingsArchive.getMySettings(payload));
//   case 'userSettings.save':
//     return _json(UserSettingsArchive.saveMySettings(payload));
//
// ЗАЧЕМ (заявка Task 551): «На андроид приложение хранит всю
// информацию в браузере chrome? если очистить данные браузера,
// то приложение "обнуляется". Как обойти этот момент?»
// Данные разделов живут в Google Sheets и при очистке браузера
// НЕ теряются; теряются localStorage: токен сессии (повторный
// вход по OTP — неизбежно) и НАСТРОКИ (тема, вид табеля,
// избранное и пр.). Этот модуль хранит настройки на сервере
// по email: клиент (KipSettingsSync в index.html) после входа
// восстанавливает их в localStorage, при изменении — сохраняет.
// Очистка браузера = только повторный вход, настройки вернутся.
//
// ЭНДПОИНТЫ (через KipAuth.api клиента):
//   userSettings.get — свои настройки (email из сессии):
//     {token}
//     → {ok, data: {srvVer, settings: {ключ: строка, …}}}
//     Листа/строки нет → settings: {} (тихая деградация: клиент
//     живёт с локальными/умолчаниями и сохранит их при первом
//     изменении или watchdog-снапшоте).
//   userSettings.save — сохранить свои настройки:
//     {token, settings: {ключ: строка, …}}
//     → {ok, data: {saved: true, keys: N}}
//     Валидация: settings — ОБЪЕКТ; ключи — ТОЛЬКО из белого
//     списка ALLOWED_KEYS (совпадает с KipSettingsSync.KEYS
//     клиента) или с префиксом из ALLOWED_PREFIXES; значения —
//     строки ≤ MAX_VALUE_LEN; суммарный размер ≤ MAX_TOTAL_LEN.
//     НЕИЗВЕСТНЫЕ ключи молча отбрасываются (клиент не может
//     протащить произвольные данные), лимиты — отказ с кодом
//     (пользователь видит понятную ошибку в консоли).
//
// ХРАНИЛИЩЕ — НОВАЯ СТРАНИЦА (лист) «Настройки» в файле
// KIP8_Access (тот же ID, что RoleMatrix.gs /
// SessionsDevicePolicy.gs / MinesweeperArchive.gs — Task 546):
// лист создаётся userSettingsInit() (разовый запуск из
// редактора) ИЛИ лениво при первом обращении к API; повторные
// запуски идемпотентны. Диагностика — userSettingsStatus().
//
//   Лист «Настройки» (стиль листов users/sessions/«Сапёр»):
//     Строка 1: титул (объединена A1:D1, шапка)
//     Строка 2: описание/правила (объединена A2:D2)
//     Строка 3: заголовки (закреплено 3 строки)
//     Строка 4+: данные (ОДНА строка НА ПОЛЬЗОВАТЕЛЯ, upsert):
//     A: email      — ключ строки (из сессии; малые буквы)
//     B: имя        — снимок из листа users (человеку читать)
//     C: данные     — JSON {ключ: строка} (формат '@')
//     D: обновлено  — ISO timestamp (текст, формат '@')
//
// ПРИНЦИП ДОСТУПА: настройки есть у КАЖДОГО вошедшего (любая
// роль, включая «Общий доступ» после входа). Гейт — сама сессия:
// Sessions.getCurrentUser(token) (бросает no_session → отказ).
// Матрица прав НЕ гейтится: персонального права «настройки» в
// KIP8_Access нет и не нужно — пользователь видит/меняет
// ТОЛЬКО свою строку (email из сессии, не из payload —
// подделать чужой email нельзя).
//
// ПОДГОТОВЛЕННЫЕ ОБЛАСТИ: upsert под LockService.getScriptLock()
// (параллельные сохранения не портят строку); каждая запись
// журналируется в audit_log (Utils.audit, код
// USER_SETTINGS_SAVE — БЕЗ самих настроек, только их число:
// приватность). Текстовые колонки — формат '@' (Task 304);
// значения, начинающиеся с '=+-@', экранируются апострофом.
//
// РАСШИРЕНИЕ В БУДУЩЕЕ: новые настройки — новыми КЛЮЧАМИ в JSON
// (колонки не трогаем); инкрементировать SCHEMA_VERSION при
// изменении структуры ЛИСТА.
// ============================================================

var UserSettingsArchive = {

  // Таблица KIP8_Access — тот же ID, что RoleMatrix.gs /
  // SessionsDevicePolicy.gs / MinesweeperArchive.gs (Task 546)
  SPREADSHEET_ID: '1TmmNZLUArWH38F6NX0gMGar8LMNMQomm_FaGZv9osyk',

  // Новая страница (лист) в KIP8_Access
  SHEET: 'Настройки',

  // Версия структуры листа (инкрементировать при расширении)
  SCHEMA_VERSION: 1,

  // Task 537-паттерн: версия серверного кода (клиент отличает
  // старый Apps Script: нет action → «Unknown action» — тихая
  // деградация на локальные настройки, без потери данных)
  SRV_VER: '551',

  // Заголовки листа (строка 3; данные — со строки 4)
  HEADERS: ['email', 'имя', 'данные', 'обновлено'],

  // Колонки текстового формата '@' (Task 304): все четыре
  TEXT_COLS: [1, 2, 3, 4],

  // Позиции колонок (1-based; чтение позиционное)
  COL: { EMAIL: 1, NAME: 2, DATA: 3, UPDATED: 4 },

  // ============================================================
  // БЕЛЫЙ СПИСОК ключей — зеркало KipSettingsSync.KEYS клиента
  // (index.html). НЕ синхронизируем: токен сессии (приватность),
  // кэши серверных данных (перекачаются сами), телефонный
  // справочник (PhonebookArchive Task 537 уже синхронит),
  // счёт «Сапёра» (MinesweeperArchive Task 546 уже хранит).
  // ============================================================
  ALLOWED_KEYS: {
    'app-theme': true,                // тема (light/dark)
    'kip8_ws_view_v1': true,          // вид табеля (full/shift/day)
    'kip8_ws_cross_v1': true,         // перекрёстная подсветка (1/0)
    'kip8_ws_lcd_set_v1': true,       // настройки LCD-информера (JSON)
    'buoy_calib_method': true,        // метод калибровки буёв
    'ws_auto_dn_keys': true,          // реестр авто-«д»/«н» (JSON)
    'pinnedSubsections': true,        // закреплённые подразделы
    'kip8_temp_fav_v1': true,         // избранное ТС/ТП
    'kip8_device_fav_v1': true,       // избранное приборов
    'kip8_fav_order_v1': true,        // порядок избранного приборов
    'kip8_device_fav_notes_v1': true, // заметки приборов
    'kip8_flow_fav_v1': true,         // избранное расходомеров
    'kip8_flow_fav_order_v1': true,   // порядок избранного расходомеров
    'kip8_detail_panel_width': true   // ширина панели деталей
  },

  // Префиксы ключей (динамический суффикс-версия «что нового»)
  ALLOWED_PREFIXES: ['kip8_whats_new_read_v'],

  // Лимиты валидации (отклоняем, а не режем молча)
  MAX_VALUE_LEN: 16384,   // 16 КБ на значение (кэши не входят)
  MAX_TOTAL_LEN: 131072,  // 128 КБ на все значения (JSON-строка)
  MAX_NAME: 200,

  // Цвет шапки — как у листов архивов (единый вид)
  HEADER_BG: '#1F4E5F',

  // ============================================================
  // userSettings.get — свои настройки (по email из сессии)
  // ============================================================
  // payload: {token}
  // returns: {ok: true, data: {srvVer, settings: {…}}} |
  //          {ok: false, error: 'no_session' | …}
  getMySettings: function(payload) {
    var g = this._requireSession(payload.token);
    if (g.error) return g.error;
    var email = this._normEmail(g.user.email);

    var settings = {};
    try {
      var ss = this._getSS();
      if (ss) {
        var sheet = ss.getSheetByName(this.SHEET);
        if (sheet) {
          var raw = this._readCell(sheet, email, this.COL.DATA);
          if (raw) {
            var parsed = this._parseJson(raw);
            if (parsed && typeof parsed === 'object' &&
                    !Array.isArray(parsed)) {
              settings = parsed;
            }
          }
        }
      }
    } catch (e) {
      // Таблица/лист недоступны → пустые настройки (тихая
      // деградация: клиент живёт локально и сохранит позже)
    }

    return { ok: true, data: { srvVer: this.SRV_VER,
                               settings: settings } };
  },

  // ============================================================
  // userSettings.save — сохранить свои настройки (upsert)
  // ============================================================
  // payload: {token, settings: {ключ: строка, …}}
  // returns: {ok: true, data: {saved: true, keys: N}} |
  //          {ok: false, error, message}
  saveMySettings: function(payload) {
    var g = this._requireSession(payload.token);
    if (g.error) return g.error;
    var email = this._normEmail(g.user.email);

    var v = this._validateSettings(payload.settings);
    if (!v.ok) return { ok: false, error: v.error,
                        message: v.message };

    var ss = this._getSS();
    if (!ss) return this._ssError();
    var sheet = ss.getSheetByName(this.SHEET);
    if (!sheet) return this._sheetError();

    var lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      var row = this._findRow(sheet, email);
      var name = this._userName(email);
      var json = JSON.stringify(v.settings);
      if (row > 0) {
        sheet.getRange(row, this.COL.NAME, 1, 1)
             .setValue(this._escCell(name));
        sheet.getRange(row, this.COL.DATA, 1, 1)
             .setValue(this._escCell(json));
        sheet.getRange(row, this.COL.UPDATED, 1, 1)
             .setValue(this._escCell(this._isoNow()));
      } else {
        sheet.appendRow([email, this._escCell(name),
                         this._escCell(json),
                         this._escCell(this._isoNow())]);
      }
      try {
        Utils.audit(g.user.email, 'USER_SETTINGS_SAVE', '', '',
          'Настройки интерфейса: ' + v.keys + ' кл. (содержимое не ' +
          'пишется — приватность)');
      } catch (e) { /* ignore */ }
      return { ok: true, data: { saved: true, keys: v.keys } };
    } finally {
      lock.releaseLock();
    }
  },

  // ============================================================
  // Валидация настроек: объект; ключи — белый список/префиксы;
  // значения — строки ≤ MAX_VALUE_LEN; сумма ≤ MAX_TOTAL_LEN.
  // Неизвестные ключи молча отбрасываются (клиент не может
  // протащить произвольные данные), лимиты — отказ с кодом.
  // ============================================================
  _validateSettings: function(s) {
    if (!s || typeof s !== 'object' || Array.isArray(s)) {
      return { ok: false, error: 'invalid_settings',
        message: 'Настройки — объект {ключ: строка}' };
    }
    var out = {};
    var total = 0;
    var keys = 0;
    for (var k in s) {
      if (!s.hasOwnProperty(k)) continue;
      if (!this._isAllowedKey(k)) continue;   // неизвестное — мимо
      var v = s[k];
      if (typeof v !== 'string') {
        return { ok: false, error: 'invalid_value',
          message: 'Значение настройки «' + k + '» — строка' };
      }
      if (v.length > this.MAX_VALUE_LEN) {
        return { ok: false, error: 'value_too_large',
          message: 'Значение «' + k + '» больше ' +
                   this.MAX_VALUE_LEN + ' символов' };
      }
      out[k] = v;
      total += k.length + v.length;
      keys++;
      if (total > this.MAX_TOTAL_LEN) {
        return { ok: false, error: 'settings_too_large',
          message: 'Суммарный размер настроек больше ' +
                   this.MAX_TOTAL_LEN + ' символов' };
      }
    }
    return { ok: true, settings: out, keys: keys };
  },

  // Ключ из белого списка ИЛИ начинается с разрешённого префикса
  _isAllowedKey: function(k) {
    k = String(k || '');
    if (this.ALLOWED_KEYS[k]) return true;
    for (var i = 0; i < this.ALLOWED_PREFIXES.length; i++) {
      if (k.indexOf(this.ALLOWED_PREFIXES[i]) === 0) return true;
    }
    return false;
  },

  // Гейт: ЛЮБАЯ валидная сессия (настройки — у каждого
  // вошедшего; email только из сессии — подделать нельзя)
  _requireSession: function(token) {
    try {
      if (typeof Sessions === 'undefined' ||
              !Sessions.getCurrentUser) {
        return { error: { ok: false, error: 'no_session' } };
      }
      var user = Sessions.getCurrentUser(token);
      return { user: user };
    } catch (e) {
      return { error: { ok: false, error: 'no_session' } };
    }
  },

  // Таблица KIP8_Access: открыть по ID; лист «Настройки» —
  // самовосстановление (идемпотентное создание при отсутствии)
  _getSS: function() {
    try {
      var ss = SpreadsheetApp.openById(this.SPREADSHEET_ID);
      if (!ss) return null;
      this._ensureSheet(ss);
      return ss;
    } catch (e) {
      return null;
    }
  },

  // Лист «Настройки»: создать, если нет (под блокировкой —
  // параллельные вызовы не создадут два листа). Порядок:
  // закрепление СТРОК ДО объединений (урок RoleMatrixInit v3),
  // объединение строк 1–2 — на всю ширину БЕЗ закрепления
  // колонок (урок v4)
  _ensureSheet: function(ss) {
    var sheet = ss.getSheetByName(this.SHEET);
    if (sheet) return sheet;

    var lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      // перепроверка под замком — параллельный вызов мог создать
      sheet = ss.getSheetByName(this.SHEET);
      if (sheet) return sheet;

      sheet = ss.insertSheet(this.SHEET);
      sheet.setFrozenRows(3);

      sheet.getRange(1, 1, 1, this.COL.UPDATED).merge();
      sheet.getRange(2, 1, 1, this.COL.UPDATED).merge();

      sheet.getRange(1, 1).setValue(
        'НАСТРОЙКИ ИНТЕРФЕЙСА — архив пользователей (по email)')
        .setBackground(this.HEADER_BG)
        .setFontColor('#FFFFFF').setFontWeight('bold');
      sheet.getRange(2, 1).setValue(
        'Одна строка на пользователя: JSON настроек (тема, вид ' +
        'табеля, избранное и пр.). Привязка к email из сессии; ' +
        'через API пользователь видит и меняет только свою строку. ' +
        'Структура v' + this.SCHEMA_VERSION + ': расширение — ' +
        'новыми ключами JSON, колонки не сдвигать.')
        .setFontStyle('italic');

      sheet.getRange(3, 1, 1, this.COL.UPDATED)
           .setValues([this.HEADERS]);
      sheet.getRange(3, 1, 1, this.COL.UPDATED)
        .setBackground(this.HEADER_BG)
        .setFontColor('#FFFFFF').setFontWeight('bold');

      // текстовые колонки — формат '@' (Task 304) на весь столбец
      for (var c = 0; c < this.TEXT_COLS.length; c++) {
        sheet.getRange(4, this.TEXT_COLS[c],
                       sheet.getMaxRows(), 1).setNumberFormat('@');
      }
      // ширины колонок — читаемость человеком
      var widths = [190, 170, 620, 170];
      for (var w = 0; w < widths.length; w++) {
        sheet.setColumnWidth(w + 1, widths[w]);
      }

      try {
        Utils.audit('', 'USER_SETTINGS_CREATED', '', '',
          'Создан лист «' + this.SHEET + '» в KIP8_Access');
      } catch (e) { /* ignore */ }
      return sheet;
    } finally {
      lock.releaseLock();
    }
  },

  // Строка пользователя по email (данные со строки 4); нет — 0
  _findRow: function(sheet, email) {
    var lastRow = sheet.getLastRow();
    if (lastRow < 4) return 0;
    var vals = sheet.getRange(4, this.COL.EMAIL,
                              lastRow - 3, 1).getValues();
    for (var i = 0; i < vals.length; i++) {
      if (this._normEmail(vals[i][0]) === email) return 4 + i;
    }
    return 0;
  },

  // Значение колонки строки пользователя (без полного чтения
  // листа — по найденной строке); нет строки — null
  _readCell: function(sheet, email, col) {
    var row = this._findRow(sheet, email);
    if (!row) return null;
    var v = sheet.getRange(row, col, 1, 1).getValue();
    return (v === '' || v === null || v === undefined)
      ? null : String(v);
  },

  // JSON без исключений (битая строка → null)
  _parseJson: function(raw) {
    try {
      return JSON.parse(raw);
    } catch (e) {
      return null;
    }
  },

  // Имя пользователя из листа users (KIP8_Access) — снимок для
  // чтения человеком (паттерн MinesweeperArchive Task 546);
  // нет имени — пусто (клиент показывает email)
  _userName: function(email) {
    try {
      if (typeof Utils !== 'undefined' && Utils.getRows) {
        var users = Utils.getRows('users');
        for (var i = 0; i < users.length; i++) {
          var u = users[i] || {};
          if (this._normEmail(u.email) === email) {
            return this._clip(String(u.name || ''), this.MAX_NAME);
          }
        }
      }
    } catch (e) { /* тихо — имя опционально */ }
    return '';
  },

  // email из сессии → малые буквы без пробелов
  _normEmail: function(v) {
    return String(v || '').trim().toLowerCase();
  },

  _clip: function(s, max) {
    s = String(s || '').trim();
    return s.length > max ? s.slice(0, max) : s;
  },

  // Защита от формул: '=+-@' в начале — ведущий апостроф (при
  // чтении апостроф не возвращается)
  _escCell: function(s) {
    s = String(s === undefined || s === null ? '' : s);
    return /^[=+\-@]/.test(s) ? "'" + s : s;
  },

  // ISO timestamp (время скрипта; формат '@' хранит текстом)
  _isoNow: function() {
    return Utilities.formatDate(new Date(),
                                Session.getScriptTimeZone(),
                                "yyyy-MM-dd'T'HH:mm:ss");
  },

  // Понятная ошибка «таблица недоступна»
  _ssError: function() {
    return { ok: false, error: 'archive_unavailable',
             message: 'Таблица KIP8_Access недоступна — проверьте ' +
                      'доступ владельца Apps Script-проекта' };
  },

  // Понятная ошибка «лист не создан» (после _getSS почти
  // невозможна — самовосстановление; страховка)
  _sheetError: function() {
    return { ok: false, error: 'sheet_unavailable',
             message: 'Лист «' + this.SHEET + '» не найден в ' +
                      'KIP8_Access — запустите ' +
                      'userSettingsInit() в Apps Script' };
  }
};

// ============================================================
// userSettingsInit — разовое создание листа «Настройки» в
// KIP8_Access (Task 551)
// ============================================================
// ПОРЯДОК ДЕЙСТВИЙ (см. DEPLOY-Task551-user-settings-server-sync.md):
//   1. Открыть Apps Script Editor (проект AKfycbyt…, где Code.gs)
//   2. + → Создать файл «UserSettingsArchive.gs», вставить содержимое
//   3. В списке функций выбрать userSettingsInit → ▶ Run
//      (первый запуск попросит авторизацию — разрешить)
//   4. В журнале (Ctrl+Enter) — имя/URL таблицы; лист «Настройки»
//      появится в KIP8_Access среди users/sessions/«Сапёр»
//   5. Deploy → Manage deployments → Edit → New version → Deploy
//
// ИДЕМПОТЕНТНО: лист уже есть — ничего не меняет, exists: true.
function userSettingsInit() {
  var ss = UserSettingsArchive._getSS();
  if (!ss) {
    Logger.log('UserSettingsInit: таблица KIP8_Access ' +
               'недоступна — проверьте ID/доступ владельца');
    return { ok: false, error: 'archive_unavailable' };
  }
  var sheet = ss.getSheetByName(UserSettingsArchive.SHEET);
  var out = {
    ok: true,
    exists: true,
    spreadsheet: ss.getName(),
    url: ss.getUrl(),
    sheet: UserSettingsArchive.SHEET,
    rows: sheet ? Math.max(sheet.getLastRow() - 3, 0) : 0
  };
  Logger.log('UserSettingsInit: лист «%s» готов — %s (строк: %s)',
             out.sheet, out.url, out.rows);
  return out;
}

// Диагностика архива (запускать в редакторе; ничего не меняет):
// таблица? лист? строки? заголовки?
function userSettingsStatus() {
  var out = { spreadsheet: false, sheet: false, rows: 0,
              headersOk: null, schemaVersion: null };
  try {
    var ss = SpreadsheetApp.openById(UserSettingsArchive.SPREADSHEET_ID);
    if (!ss) {
      Logger.log('UserSettingsStatus: KIP8_Access не открылся');
      return out;
    }
    out.spreadsheet = true;
    out.url = ss.getUrl();
    var sheet = ss.getSheetByName(UserSettingsArchive.SHEET);
    if (!sheet) {
      Logger.log('UserSettingsStatus: листа «%s» нет — ' +
                 'запустите userSettingsInit()',
                 UserSettingsArchive.SHEET);
      return out;
    }
    out.sheet = true;
    out.rows = Math.max(sheet.getLastRow() - 3, 0);
    if (sheet.getLastRow() >= 3) {
      var hdr = sheet.getRange(3, 1, 1,
                  UserSettingsArchive.COL.UPDATED).getValues()[0];
      out.headersOk = String(hdr.join('|')) ===
                      String(UserSettingsArchive.HEADERS.join('|'));
    }
    out.schemaVersion = UserSettingsArchive.SCHEMA_VERSION;
    Logger.log('UserSettingsStatus: лист=%s строк=%s шапка=%s',
               out.sheet, out.rows, out.headersOk);
  } catch (e) {
    Logger.log('UserSettingsStatus: ошибка (%s)', e);
  }
  return out;
}
