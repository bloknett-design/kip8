#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 528 — перенос тестов kip8test → kip8 (по образцу
task527-transfer-tests.py + task527-transfer-tests-fix.py; УРОК 527:
SW-секция вырезается по ПОСЛЕДНЕМУ разделителю перед «5. SW» (rindex),
а не по первому «// ===»):
  1) index.html — /tmp/kip8_index_transfer.html (prepare-kip8-transfer.py
     уже выполнен в kip8test; дифф 360 строк = ровно контент Task 528);
  2) test-task526.js / test-task527.js — адаптированные версии kip8test,
     SW-секция → конвенция kip8 в ПОСТ-БАМП состоянии (assert kipia-v538,
     гвард kipia-v537 отсутствует);
  3) test-task528.js — копия kip8test с SW-секцией kip8 (assert v538);
  4) бамп SW kip8 v537→v538: ГВАРДЫ v538→v539 первыми (во всех, КРОМЕ
     трёх перенесённых файлов — они уже в пост-бамп состоянии), АССЕРТЫ
     v537→v538, sw.js CACHE_VERSION, регистрация test-task528.js.
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
    """Заменяет хвост файла начиная с разделителя ПЕРЕД секцией «5. SW»
    (rindex — УРОК Task 527: index() резал по первому «// ===»)."""
    marker = src.rindex('// 5. SW')
    sw_start = src.rindex('// ===========', 0, marker)
    return src[:sw_start] + new_sw


SW_526 = """// ============================================================
// 5. SW — версия кэша бампнута (index.html менялся)
// ============================================================
describe('Task 526 — SW: версия кэша', () => {

    test('SW: кэш поднят до kipia-v538 (Task 528)', () => {
        assertTrue(SW_SRC.indexOf('kipia-v538') !== -1,
            'SW несёт версию kipia-v538');
        assertTrue(SW_SRC.indexOf('kipia-v537') === -1,
            'прежней версии kipia-v537 нет');
    });
});
"""

SW_527 = """// ============================================================
// 5. SW — версия кэша бампнута (index.html менялся)
// ============================================================
describe('Task 527 — SW: версия кэша', () => {

    test('SW: кэш поднят до kipia-v538 (Task 528)', () => {
        assertTrue(SW_SRC.indexOf('kipia-v538') !== -1,
            'SW несёт версию kipia-v538');
        assertTrue(SW_SRC.indexOf('kipia-v537') === -1,
            'прежней версии kipia-v537 нет');
    });
});
"""

SW_528 = """// ============================================================
// 5. SW — версия кэша бампнута (index.html менялся)
// ============================================================
describe('Task 528 — SW: версия кэша', () => {

    test('SW: кэш поднят до kipia-v538 (Task 528)', () => {
        assertTrue(SW_SRC.indexOf('kipia-v538') !== -1,
            'SW несёт версию kipia-v538');
        assertTrue(SW_SRC.indexOf('kipia-v537') === -1,
            'прежней версии kipia-v537 нет (бамп v537 → v538)');
    });
});
"""

# ---------- 1. index.html ----------
src = read('/tmp/kip8_index_transfer.html')
write(K + '/index.html', src)
print('[1] kip8/index.html — перенесён из /tmp/kip8_index_transfer.html')

# ---------- 2. test-task526.js / test-task527.js (адаптации Task 528) ----------
for fname, sw in [('test-task526.js', SW_526), ('test-task527.js', SW_527)]:
    src = read(T + '/tests/' + fname)
    assert "kipia-test-v741" in src, fname + ': SW-блок kip8test не найден'
    src = swap_sw(src, sw)
    src = src.replace('//   SW: kipia-test-v741.', '//   SW: kipia-v538.')
    write(K + '/tests/' + fname, src)
    print('[2] kip8/tests/%s — адаптация Task 528 перенесена, SW-секция kip8 (v538)' % fname)

# ---------- 3. test-task528.js (новый) ----------
src = read(T + '/tests/test-task528.js')
assert "kipia-test-v741" in src, 'test-task528.js: SW-блок kip8test не найден'
src = swap_sw(src, SW_528)
src = src.replace('//   SW: kipia-test-v741.', '//   SW: kipia-v538.')
write(K + '/tests/test-task528.js', src)
print('[3] kip8/tests/test-task528.js — создан (SW-секция kip8: v538)')

# ---------- 4. бамп SW kip8 v537 → v538 ----------
OWN = ['test-task526.js', 'test-task527.js', 'test-task528.js']
changed = {}


def bump(path, old, new, label):
    s = read(path)
    n = s.count(old)
    if n == 0:
        return
    write(path, s.replace(old, new))
    changed[os.path.basename(path)] = changed.get(os.path.basename(path), 0) + n


tests_dir = os.path.join(K, 'tests')
files = sorted(f for f in os.listdir(tests_dir) if f.endswith('.js'))

print('Шаг 4а — ГВАРДЫ v538 → v539 (кроме трёх перенесённых):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v538', 'kipia-v539', 'гард')

print('Шаг 4б — АССЕРТЫ v537 → v538:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v537', 'kipia-v538', 'ассерт')

print('Шаг 4в — sw.js CACHE_VERSION v537 → v538:')
sw_path = os.path.join(K, 'sw.js')
sw = read(sw_path)
if sw.count("const CACHE_VERSION = 'kipia-v537'") != 1:
    print('ОШИБКА: CACHE_VERSION v537 не найден')
    sys.exit(1)
write(sw_path, sw.replace("const CACHE_VERSION = 'kipia-v537'",
                          "const CACHE_VERSION = 'kipia-v538'"))
print('  sw.js: CACHE_VERSION v538')

print('Шаг 4г — регистрация test-task528.js в run-all.js:')
ra_path = os.path.join(tests_dir, 'run-all.js')
ra = read(ra_path)
if "require('./test-task528.js')" in ra:
    print('  уже зарегистрирован')
else:
    anchor = "require('./test-task527.js');"
    if ra.count(anchor) != 1:
        print('ОШИБКА: якорь run-all не найден')
        sys.exit(1)
    ra = ra.replace(anchor, anchor + "\n// Task 528 (зеркало kip8test): подписи размеров НАД линиями,\n"
                                   "// d кольца — внутри отверстия, h — над линией зеркала, все\n"
                                   "// результаты в блоке с фигурой, автопрокрутка к фигуре.\n"
                                   "// SW v538.\n"
                                   "require('./test-task528.js');")
    write(ra_path, ra)
    print('  зарегистрирован после test-task527.js')

print('')
print('Итого файлов (бамп): %d, замен: %d' % (len(changed), sum(changed.values())))
print('OK')
