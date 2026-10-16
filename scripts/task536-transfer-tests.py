#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 536 — перенос из kip8test в kip8 (по образцу
task535-transfer-tests.py — swap_sw, УРОК 527: SW-секция вырезается
по ПОСЛЕДНЕМУ разделителю перед маркером SW — rindex):
  1) index.html — /tmp/kip8_index_transfer.html (prepare-kip8-transfer.py
     запускается ЗДЕСЬ ЖЕ, в kip8test; дифф = контент Task 536: клиент
     без серверного канала погоды);
  2) scripts/WorkSchedule.gs — копия kip8test (серверная погода
     УДАЛЕНА: getWeather/_parseMeteoinfo/_parseOpenMeteo/
     authorizeWeather);
  3) scripts/Code.gs — ТОЧЕЧНЫЙ патч (репозитории дрейфанули, целиком
     НЕ копируем): роутинг case 'workSchedule.getWeather' → заметка
     Task 536;
  4) тесты test-task530/532/533/534/535/536.js (адаптированные под
     Task 536; SW-хвост → единый kip8-блок v546/гвард v547);
  5) бамп SW kip8 v545 → v546: ГВАРДЫ v546 → v547 первыми (во всех,
     КРОМЕ перенесённых), АССЕРТЫ v545 → v546, sw.js CACHE_VERSION,
     регистрация test-task536.js.
УРОК Task 534: скрипт НЕ идемпотентен по бампу — при сбое
git checkout -- . и ОДИН чистый запуск.
"""
import io
import os
import subprocess
import sys

T = '/home/z/my-project/kip8test'
K = '/home/z/my-project/kip8'


def read(p):
    return io.open(p, encoding='utf-8').read()


def write(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


def swap_sw(src, new_sw):
    """Заменяет хвост файла начиная с разделителя ПЕРЕД SW-секцией
    (rindex — УРОК Task 527; маркеры: «// E. SW», «// D. SW»)."""
    for marker in ('// E. SW', '// D. SW'):
        if marker in src:
            sw_start = src.rindex('// ===========', 0, src.index(marker))
            return src[:sw_start] + new_sw
    raise ValueError('SW-секция не найдена')


# kip8-блоки SW: ЧИСЛО ТЕСТОВ = хвосту kip8test (ПАРИТЕТ счётчиков,
# УРОК Task 536: единый 1-тестовый блок срезал 5 тестов — 7023≠7028)
_SW_HEAD = """// ============================================================
// SW — версия кеша (зеркало kip8test, Task 536)
// ============================================================"""

SW_530 = _SW_HEAD + """
describe('Task 530 — SW: версия кеша', () => {

    test('sw.js: CACHE_VERSION = kipia-v546', () => {
        const m = SW_SRC.match(/const CACHE_VERSION = '(kipia-v\\d+)'/);
        assertTrue(m !== null, 'CACHE_VERSION найден');
        assertEqual(m[1], 'kipia-v546',
            'SW поднят до v546 (Task 536: серверная погода удалена)');
        assertTrue(m[1] !== 'kipia-v540', 'старая версия v540 не осталась');
    });

});
"""

SW_532 = _SW_HEAD + """
describe('Task 532 — SW: версия кеша', () => {

    test('sw.js: CACHE_VERSION = kipia-v546', () => {
        const m = SW_SRC.match(/const CACHE_VERSION = '(kipia-v\\d+)'/);
        assertTrue(m !== null, 'CACHE_VERSION найден');
        assertEqual(m[1], 'kipia-v546',
            'SW поднят до v546 (Task 536: серверная погода удалена)');
        assertTrue(m[1] !== 'kipia-v541', 'старая версия v541 не осталась');
    });

    test('sw.js: нет забегания вперёд (v547 не должно быть)', () => {
        assertFalse(SW_SRC.indexOf('kipia-v547') !== -1,
            'двойной бамп не сделан');
    });

});
"""

SW_533 = _SW_HEAD + """
describe('Task 533 E: SW — версия кеша', () => {

    test('sw.js: CACHE_VERSION = kipia-v546', () => {
        const i = SW_SRC.indexOf("const CACHE_VERSION = 'kipia-v546'");
        assertTrue(i !== -1,
            'версия v546 (Task 536: серверная погода удалена)');
    });

    test('sw.js: нет забегания вперёд (v547 не должно быть)', () => {
        assertTrue(SW_SRC.indexOf('kipia-v547') === -1,
            'v547 в sw.js отсутствует (гварды живут только в тестах)');
    });

    test('index.html: версия промта/кеша согласована (v546 в тестах)', () => {
        // ассерты текущей версии расставлены бампом по всем тестам
        const dir = fs.readdirSync(path.join(__dirname));
        const t533 = fs.readFileSync(path.join(__dirname, 'test-task533.js'), 'utf8');
        assertTrue(t533.indexOf('kipia-v546') !== -1, 'этот тест знает v546');
        assertTrue(dir.indexOf('test-task533.js') !== -1, 'файл на месте');
    });

});
"""

SW_534 = _SW_HEAD + """
describe('Task 534 D: SW — версия кеша', () => {

    test('sw.js: CACHE_VERSION = kipia-v546', () => {
        const i = SW_SRC.indexOf("const CACHE_VERSION = 'kipia-v546'");
        assertTrue(i !== -1,
            'версия v546 (Task 536: серверная погода удалена)');
    });

    test('sw.js: нет забегания вперёд (v547 не должно быть)', () => {
        assertTrue(SW_SRC.indexOf('kipia-v547') === -1,
            'v547 в sw.js отсутствует (гварды живут только в тестах)');
    });

    test('index.html: версия согласована (v546 в этом тесте)', () => {
        const t534 = fs.readFileSync(path.join(__dirname, 'test-task534.js'), 'utf8');
        assertTrue(t534.indexOf('kipia-v546') !== -1, 'этот тест знает v546');
        const dir = fs.readdirSync(path.join(__dirname));
        assertTrue(dir.indexOf('test-task534.js') !== -1, 'файл на месте');
    });

});
"""

SW_535 = _SW_HEAD + """
describe('Task 535 E: SW — версия кеша', () => {

    test('SW: kipia-v546, забегания вперёд нет (v547)', () => {
        assertTrue(SW_SRC.indexOf("const CACHE_VERSION = 'kipia-v546'") !== -1,
            'CACHE_VERSION = kipia-v546');
        assertTrue(SW_SRC.indexOf('kipia-v547') === -1, 'v547 не появилась');
        assertTrue(SW_SRC.indexOf('kipia-v545') === -1, 'v545 убрана');
    });

});
"""

SW_536 = _SW_HEAD + """
describe('Task 536 E: SW — версия кеша', () => {

    test('SW: kipia-v546, забегания вперёд нет (v547)', () => {
        assertTrue(SW_SRC.indexOf("const CACHE_VERSION = 'kipia-v546'") !== -1,
            'CACHE_VERSION = kipia-v546');
        assertTrue(SW_SRC.indexOf('kipia-v547') === -1, 'v547 не появилась');
        assertTrue(SW_SRC.indexOf('kipia-v545') === -1, 'v545 убрана');
    });

});
"""


# ---------- 0. prepare-kip8-transfer.py (изоляты kip8test → kip8) ----------
r = subprocess.run([sys.executable, T + '/scripts/prepare-kip8-transfer.py'],
                   capture_output=True, text=True)
print(r.stdout[-700:])
if r.returncode != 0:
    print('ОШИБКА prepare-kip8-transfer.py:\n' + r.stderr[-800:])
    sys.exit(1)

# ---------- 1. index.html ----------
html = read('/tmp/kip8_index_transfer.html')
write(K + '/index.html', html)
print('[1] kip8/index.html — перенесён (дифф = контент Task 536, '
      'только клиент: серверный канал погоды удалён)')

# ---------- 2. WorkSchedule.gs ----------
write(K + '/scripts/WorkSchedule.gs', read(T + '/scripts/WorkSchedule.gs'))
print('[2] kip8/scripts/WorkSchedule.gs — перенесён (серверная погода '
      'УДАЛЕНА: −290 строк)')

# ---------- 3. Code.gs — точечный патч роутинга ----------
cg_path = K + '/scripts/Code.gs'
cg = read(cg_path)
OLD_CASE = ('      // Task 530: погода Кемерово с meteoinfo.ru (кэш скрипта 30 мин)\n'
            "      case 'workSchedule.getWeather':\n"
            '        return _json(WorkSchedule.getWeather(payload));\n')
NEW_CASE = ('      // Task 536: роутинг workSchedule.getWeather УДАЛЁН — серверная\n'
            '      // погода (UrlFetchApp) не работала (нет области\n'
            '      // script.external_request); погода идёт напрямую из браузера\n'
            '      // (open-meteo.com → wttr.in, клиент WsLcdClock в index.html).\n')
if OLD_CASE in cg:
    assert cg.count(OLD_CASE) == 1
    cg = cg.replace(OLD_CASE, NEW_CASE, 1)
    write(cg_path, cg)
    print('[3] kip8/scripts/Code.gs — роутинг getWeather УДАЛЁН (точечный патч)')
else:
    if NEW_CASE in cg:
        print('[3] kip8/scripts/Code.gs — уже пропатчен (идемпотентный повтор)')
    else:
        print('ОШИБКА: блок роутинга getWeather в kip8/Code.gs не найден')
        sys.exit(1)

# ---------- 4. тесты: SW-хвост → kip8-блоки (ЧИСЛО ТЕСТОВ = хвосту
# kip8test — ПАРИТЕТ счётчиков, УРОК Task 536) ----------
SPECS = [
    ('test-task530.js', SW_530),
    ('test-task532.js', SW_532),
    ('test-task533.js', SW_533),
    ('test-task534.js', SW_534),
    ('test-task535.js', SW_535),
    ('test-task536.js', SW_536),
]
for name, block in SPECS:
    src = read(T + '/tests/' + name)
    src = swap_sw(src, block)
    # версии kip8test → kip8 в шапках (SW-хвост уже заменён);
    # смещение версий: kip8test vN ↔ kip8 v(N−203)
    for old, new in [('kipia-test-v750', 'kipia-v547'),
                     ('kipia-test-v749', 'kipia-v546'),
                     ('kipia-test-v748', 'kipia-v545'),
                     ('kipia-test-v747', 'kipia-v544'),
                     ('kipia-test-v744', 'kipia-v541'),
                     ('kipia-test-v743', 'kipia-v540')]:
        src = src.replace(old, new)
    assert 'kipia-test-v' not in src, name + ': остатки kipia-test-v!'
    write(K + '/tests/' + name, src)
    print('[4] kip8/tests/%s — перенесён (SW-хвост: kip8 v546)' % name)

# ---------- 5. бамп SW kip8 v545 → v546 ----------
OWN = [name for name, _ in SPECS]
changed = {}


def bump(path, old, new):
    s = read(path)
    n = s.count(old)
    if n == 0:
        return
    write(path, s.replace(old, new))
    changed[os.path.basename(path)] = changed.get(
        os.path.basename(path), 0) + n


tests_dir = os.path.join(K, 'tests')
files = sorted(f for f in os.listdir(tests_dir) if f.endswith('.js'))

print('Шаг 5а — ГВАРДЫ v546 → v547 (кроме перенесённых):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v546', 'kipia-v547')

print('Шаг 5б — АССЕРТЫ v545 → v546:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v545', 'kipia-v546')

print('Шаг 5в — sw.js CACHE_VERSION v545 → v546:')
sw_path = os.path.join(K, 'sw.js')
sw = read(sw_path)
if sw.count("const CACHE_VERSION = 'kipia-v546'") == 1:
    print('  уже v546 (повторный запуск — ОСТАНОВИТЬСЯ, см. УРОК Task 534)')
    sys.exit(1)
elif sw.count("const CACHE_VERSION = 'kipia-v545'") == 1:
    write(sw_path, sw.replace("const CACHE_VERSION = 'kipia-v545'",
                              "const CACHE_VERSION = 'kipia-v546'"))
    print('  sw.js: CACHE_VERSION v546')
else:
    print('ОШИБКА: CACHE_VERSION v545/v546 не найден')
    sys.exit(1)

print('Шаг 5г — регистрация test-task536.js в run-all.js:')
ra_path = os.path.join(tests_dir, 'run-all.js')
ra = read(ra_path)
if "require('./test-task536.js')" in ra:
    print('  уже зарегистрирован')
else:
    anchor = "require('./test-task535.js');"
    if ra.count(anchor) != 1:
        print('ОШИБКА: якорь run-all (535) не найден')
        sys.exit(1)
    ra = ra.replace(anchor, anchor +
                    "\n// Task 536 (зеркало kip8test): серверная погода УДАЛЕНА —\n"
                    "// WorkSchedule.gs без getWeather/парсеров/authorizeWeather,\n"
                    "// Code.gs без роутинга; клиент — open-meteo → wttr.in.\n"
                    "require('./test-task536.js');")
    write(ra_path, ra)
    print('  зарегистрирован после test-task535.js')

total = sum(changed.values())
print('Итого замен в старых тестах: %d (файлов: %d)' % (total, len(changed)))
print('OK — перенос завершён')
