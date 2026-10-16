#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 535 — перенос из kip8test в kip8 (по образцу
task534-transfer-tests.py — swap_sw, УРОК 527: SW-секция вырезается
по ПОСЛЕДНЕМУ разделителю перед маркером SW — rindex):
  1) index.html — /tmp/kip8_index_transfer.html (prepare-kip8-transfer.py
     запускается ЗДЕСЬ ЖЕ, в kip8test; дифф = контент Task 535: глиф «Я»,
     день недели/блок погоды правее, календарь высоты, светлая тема);
  2) scripts/WorkSchedule.gs — копия kip8test (authorizeWeather:
     slice 220 + SCOPE + подсказка oauthScopes);
  3) test-task535.js (НОВЫЙ, SW-хвост → единый kip8-блок v545/гвард
     v546) + test-task531.js (АДАПТИРОВАННЫЙ под Task 535 — день
     недели смещён ПРАВЕЕ; SW-хвост → однотестовый kip8-блок v545);
  4) бамп SW kip8 v544 → v545: ГВАРДЫ v545 → v546 первыми (во всех,
     КРОМЕ перенесённых), АССЕРТЫ v544 → v545, sw.js CACHE_VERSION,
     регистрация test-task535.js.
Идемпотентен: повторный запуск перезаписывает те же файлы.
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
    (rindex — УРОК Task 527; маркеры: «// E. SW» (535), «// D. SW»
    (531))."""
    for marker in ('// E. SW', '// D. SW'):
        if marker in src:
            sw_start = src.rindex('// ===========', 0, src.index(marker))
            return src[:sw_start] + new_sw
    raise ValueError('SW-секция не найдена')


SW_535 = """// ============================================================
// E. SW — версия кеша (зеркало kip8test, Task 535)
// ============================================================
describe('Task 535 E: SW — версия кеша', () => {

    test('SW: kipia-v545, забегания вперёд нет (v546)', () => {
        assertTrue(SW_SRC.indexOf("const CACHE_VERSION = 'kipia-v545'") !== -1,
            'CACHE_VERSION = kipia-v545');
        assertTrue(SW_SRC.indexOf('kipia-v546') === -1, 'v546 не появилась');
        assertTrue(SW_SRC.indexOf('kipia-v544') === -1, 'v544 убрана');
    });

});
"""

SW_531 = """// ============================================================
// SW — версия кэша (зеркало kip8test, Task 531)
// ============================================================
describe('Task 531 — SW: версия кэша', () => {

    test('sw.js: CACHE_VERSION = kipia-v545', () => {
        const m = SW_SRC.match(/const CACHE_VERSION = '(kipia-v\\d+)'/);
        assertTrue(m !== null, 'CACHE_VERSION найден');
        assertEqual(m[1], 'kipia-v545',
            'SW поднят до kipia-v545 (index.html менялся — Task 535)');
        assertTrue(m[1] !== 'kipia-v544',
            'старая версия kipia-v544 не осталась');
    });

});
"""

# ---------- 0. prepare-kip8-transfer.py (изоляты kip8test → kip8) ----------
r = subprocess.run([sys.executable, T + '/scripts/prepare-kip8-transfer.py'],
                   capture_output=True, text=True)
print(r.stdout[-600:])
if r.returncode != 0:
    print('ОШИБКА prepare-kip8-transfer.py:\n' + r.stderr[-800:])
    sys.exit(1)

# ---------- 1. index.html ----------
html = read('/tmp/kip8_index_transfer.html')
write(K + '/index.html', html)
print('[1] kip8/index.html — перенесён (дифф = контент Task 535, '
      'только клиент)')

# ---------- 2. WorkSchedule.gs ----------
write(K + '/scripts/WorkSchedule.gs', read(T + '/scripts/WorkSchedule.gs'))
print('[2] kip8/scripts/WorkSchedule.gs — перенесён (authorizeWeather: '
      'slice 220 + SCOPE + oauthScopes-подсказка)')

# ---------- 3. тесты: SW-хвост → kip8-блоки ----------
SPECS = [
    ('test-task535.js', SW_535),
    ('test-task531.js', SW_531),
]
for name, block in SPECS:
    src = read(T + '/tests/' + name)
    src = swap_sw(src, block)
    # версии kip8test → kip8 в шапках (SW-хвост уже заменён)
    src = src.replace('kipia-test-v748', 'kipia-v545')
    src = src.replace('kipia-test-v749', 'kipia-v546')
    src = src.replace('kipia-test-v747', 'kipia-v544')
    src = src.replace('kipia-test-v743', 'kipia-v540')
    assert 'kipia-test-v' not in src, name + ': остатки kipia-test-v!'
    write(K + '/tests/' + name, src)
    print('[3] kip8/tests/%s — SW-хвост: kip8 v545' % name)

# ---------- 4. бамп SW kip8 v544 → v545 ----------
OWN = ['test-task535.js', 'test-task531.js']
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

print('Шаг 4а — ГВАРДЫ v545 → v546 (кроме перенесённых):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v545', 'kipia-v546')

print('Шаг 4б — АССЕРТЫ v544 → v545:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v544', 'kipia-v545')

print('Шаг 4в — sw.js CACHE_VERSION v544 → v545:')
sw_path = os.path.join(K, 'sw.js')
sw = read(sw_path)
if sw.count("const CACHE_VERSION = 'kipia-v545'") == 1:
    print('  уже v545 (идемпотентный перезапуск)')
elif sw.count("const CACHE_VERSION = 'kipia-v544'") == 1:
    write(sw_path, sw.replace("const CACHE_VERSION = 'kipia-v544'",
                              "const CACHE_VERSION = 'kipia-v545'"))
    print('  sw.js: CACHE_VERSION v545')
else:
    print('ОШИБКА: CACHE_VERSION v544/v545 не найден')
    sys.exit(1)

print('Шаг 4г — регистрация test-task535.js в run-all.js:')
ra_path = os.path.join(tests_dir, 'run-all.js')
ra = read(ra_path)
if "require('./test-task535.js')" in ra:
    print('  уже зарегистрирован')
else:
    anchor = "require('./test-task534.js');"
    if ra.count(anchor) != 1:
        print('ОШИБКА: якорь run-all (534) не найден')
        sys.exit(1)
    ra = ra.replace(anchor, anchor +
                    "\n// Task 535 (зеркало kip8test): LCD-информер — глиф «Я» с\n"
                    "// левой ножкой; день недели/блок погоды правее; календарь:\n"
                    "// селекты по высоте кнопок; светлая тема — яркие стрелки;\n"
                    "// сервер authorizeWeather — полный URL + манифест.\n"
                    "require('./test-task535.js');")
    write(ra_path, ra)
    print('  зарегистрирован после test-task534.js')

total = sum(changed.values())
print('Итого замен в старых тестах: %d (файлов: %d)' % (total, len(changed)))
print('OK — перенос завершён')
