#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 534 — перенос из kip8test в kip8 (по образцу
task531-transfer-tests.py — swap_sw, УРОК 527: SW-секция вырезается
по ПОСЛЕДНЕМУ разделителю перед маркером SW — rindex):
  1) index.html — /tmp/kip8_index_transfer.html (prepare-kip8-transfer.py
     уже выполнен в kip8test; дифф 316 строк = контент Task 534:
     канал 2 wttr.in + подсказка authorizeWeather + календарь
     левый край/без подписей/шрифт месяца);
  2) scripts/WorkSchedule.gs — копия kip8test (authorizeWeather()
     + diag 90; дифф 83 строки — ровно Task 534);
  3) test-task534.js (НОВЫЙ) + test-task533.js + test-task532.js —
     копии kip8test, SW-хвост заменён на единый kip8-блок
     (assert kipia-v544 + гвард v545; УРОК Task 533: в SW-блоках
     перенесённых тестов был регэксп kipia-test-v\\d+ и старые
     версии — swap хвоста снимает вопрос целиком), строка
     заголовка «… SW — kipia-test-v747» → «kipia-v544»;
  4) бамп SW kip8 v543 → v544: ГВАРДЫ v544 → v545 первыми (во всех,
     КРОМЕ перенесённых файлов), АССЕРТЫ v543 → v544, sw.js
     CACHE_VERSION, регистрация test-task534.js.
Идемпотентен: повторный запуск перезаписывает те же файлы.
"""
import io
import os
import sys

T = '/home/z/my-project/kip8test'
K = '/home/z/my-project/kip8'


def read(p):
    return io.open(p, encoding='utf-8').read()


def write(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


def swap_sw(src, new_sw):
    """Заменяет хвост файла начиная с разделителя ПЕРЕД SW-секцией
    (rindex — УРОК Task 527; маркеры: «// E. SW» (532/533),
    «// D. SW» (534))."""
    for marker in ('// E. SW', '// D. SW'):
        if marker in src:
            sw_start = src.rindex('// ===========', 0, src.index(marker))
            return src[:sw_start] + new_sw
    raise ValueError('SW-секция не найдена')


def sw_block(desc_title, note, fname=None):
    third = ''
    if fname:
        # третий тест — как в оригиналах kip8test (533/534): файл
        # на месте и знает текущую версию (паритет счётчика тестов)
        third = """
    test('файл на месте и знает текущую версию (v544)', () => {
        const dir = fs.readdirSync(path.join(__dirname));
        const self = fs.readFileSync(path.join(__dirname, '""" + fname + """'), 'utf8');
        assertTrue(self.indexOf('kipia-v544') !== -1, 'этот тест знает v544');
        assertTrue(dir.indexOf('""" + fname + """') !== -1, 'файл на месте');
    });

"""
    return """// ============================================================
// SW — версия кэша (зеркало kip8test, Task 534)
// ============================================================
describe('""" + desc_title + """', () => {

    test('sw.js: CACHE_VERSION = kipia-v544', () => {
        const m = SW_SRC.match(/const CACHE_VERSION = '(kipia-v\\d+)'/);
        assertTrue(m !== null, 'CACHE_VERSION найден');
        assertEqual(m[1], 'kipia-v544', 'SW поднят до v544 (""" + note + """)');
        assertTrue(m[1] !== 'kipia-v543', 'старая версия v543 не осталась');
    });

    test('sw.js: нет забегания вперёд (v545 не должно быть)', () => {
        assertTrue(SW_SRC.indexOf('kipia-v545') === -1,
            'v545 в sw.js отсутствует (гварды живут только в тестах)');
    });
""" + third + """
});
"""


# ---------- 1. index.html ----------
html = read('/tmp/kip8_index_transfer.html')
write(K + '/index.html', html)
print('[1] kip8/index.html — перенесён (дифф 316 строк = Task 534, '
      'только клиент)')

# ---------- 2. WorkSchedule.gs (сервер: authorizeWeather + diag 90) ----------
write(K + '/scripts/WorkSchedule.gs', read(T + '/scripts/WorkSchedule.gs'))
print('[2] kip8/scripts/WorkSchedule.gs — перенесён (authorizeWeather() '
      '+ diag 60→90; дифф 83 строки)')

# ---------- 3. тесты: SW-хвост → единый kip8-блок (v544 + гвард v545) ----------
SPECS = [
    ('test-task534.js', 'Task 534 D: SW — версия кэша',
     'Task 534: wttr.in + подсказка + календарь', 'test-task534.js'),
    ('test-task533.js', 'Task 533 E: SW — версия кэша',
     'Task 534: wttr.in + подсказка + календарь', 'test-task533.js'),
    ('test-task532.js', 'Task 532 E: SW — версия кэша',
     'Task 534: wttr.in + подсказка + календарь', None),
]
for name, title, note, fname in SPECS:
    src = read(T + '/tests/' + name)
    src = swap_sw(src, sw_block(title, note, fname))
    # строки заголовка в шапке файла: версии kip8test → kip8
    # (в SW-хвосте их уже нет — swap; в шапке остаются упоминания)
    src = src.replace('kipia-test-v747', 'kipia-v544')
    src = src.replace('kipia-test-v748', 'kipia-v545')
    src = src.replace('kipia-test-v744', 'kipia-v543')
    assert 'kipia-test-v' not in src, name + ': остатки kipia-test-v!'
    write(K + '/tests/' + name, src)
    print('[3] kip8/tests/%s — SW-хвост: kip8 v544 (гвард v545)' % name)

# ---------- 4. бамп SW kip8 v543 → v544 ----------
OWN = ['test-task534.js', 'test-task533.js', 'test-task532.js']
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

print('Шаг 4а — ГВАРДЫ v544 → v545 (кроме перенесённых):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v544', 'kipia-v545')

print('Шаг 4б — АССЕРТЫ v543 → v544:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v543', 'kipia-v544')

print('Шаг 4в — sw.js CACHE_VERSION v543 → v544:')
sw_path = os.path.join(K, 'sw.js')
sw = read(sw_path)
if sw.count("const CACHE_VERSION = 'kipia-v544'") == 1:
    print('  уже v544 (идемпотентный перезапуск)')
elif sw.count("const CACHE_VERSION = 'kipia-v543'") == 1:
    write(sw_path, sw.replace("const CACHE_VERSION = 'kipia-v543'",
                              "const CACHE_VERSION = 'kipia-v544'"))
    print('  sw.js: CACHE_VERSION v544')
else:
    print('ОШИБКА: CACHE_VERSION v543/v544 не найден')
    sys.exit(1)

print('Шаг 4г — регистрация test-task534.js в run-all.js:')
ra_path = os.path.join(tests_dir, 'run-all.js')
ra = read(ra_path)
if "require('./test-task534.js')" in ra:
    print('  уже зарегистрирован')
else:
    anchor = "require('./test-task533.js');"
    if ra.count(anchor) != 1:
        print('ОШИБКА: якорь run-all (533) не найден')
        sys.exit(1)
    ra = ra.replace(anchor, anchor +
                    "\n// Task 534 (зеркало kip8test): LCD-информер — ДВА прямых канала\n"
                    "// погоды (open-meteo → wttr.in → сервер) + подсказка authorizeWeather;\n"
                    "// календарь: строки головы по левому краю, подписи убраны, шрифт\n"
                    "// месяца мельче года.\n"
                    "require('./test-task534.js');")
    write(ra_path, ra)
    print('  зарегистрирован после test-task533.js')

total = sum(changed.values())
print('Итого замен в старых тестах: %d (файлов: %d)' % (total, len(changed)))
print('OK — перенос завершён')
