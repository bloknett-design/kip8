#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 527 — перенос тестов kip8test → kip8:
  1) test-task526.js — берём АДАПТИРОВАННУЮ версию kip8test (viewBox,
     нет #xxFigRes, 350px, гвард .gf-resg) и заменяем SW-секцию на
     конвенцию kip8 (assert kipia-v536 — бампнется скриптом до v537);
  2) test-task527.js — копия kip8test с SW-секцией конвенции kip8
     (assert kipia-v537 + гвард kipia-v536, как новый тест Task 526);
  3) бамп SW kip8 v536→v537 (гварды v537→v538 первыми, ассерты
     v536→v537, sw.js CACHE_VERSION, регистрация в run-all.js).
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


# ---------- 1. test-task526.js (адаптированная структура) ----------
src = read(T + '/tests/test-task526.js')

# SW-секция kip8test (два теста: CACHE_VERSION + гвард) → конвенция kip8
sw_start = src.index("// ============================================================")
sw_marker = src.index("5. SW", sw_start)
sw_block = src[sw_start:]
assert "kipia-test-v740" in sw_block, "SW-блок kip8test не найден"
new_sw = """// ============================================================
// 5. SW — версия кэша бампнута (index.html менялся)
// ============================================================
describe('Task 526 — SW: версия кэша', () => {

    test('SW: кэш поднят до kipia-v536 (Task 526)', () => {
        assertTrue(SW_SRC.indexOf('kipia-v536') !== -1,
            'SW несёт версию kipia-v536');
        assertTrue(SW_SRC.indexOf('kipia-v535') === -1,
            'прежней версии kipia-v535 нет');
    });
});
"""
src = src[:sw_start] + new_sw
src = src.replace('//   SW: kipia-test-v740.', '//   SW: kipia-v536.')
write(K + '/tests/test-task526.js', src)
print('[1] kip8/tests/test-task526.js — адаптация Task 527 перенесена, SW-секция в конвенции kip8 (v536 → бампнется)')

# ---------- 2. test-task527.js (новый, конвенция kip8) ----------
src = read(T + '/tests/test-task527.js')
sw_start = src.index("// ============================================================")
sw_marker = src.index("5. SW", sw_start)
new_sw = """// ============================================================
// 5. SW — версия кэша бампнута (index.html менялся)
// ============================================================
describe('Task 527 — SW: версия кэша', () => {

    test('SW: кэш поднят до kipia-v537 (Task 527)', () => {
        assertTrue(SW_SRC.indexOf('kipia-v537') !== -1,
            'SW несёт версию kipia-v537');
        assertTrue(SW_SRC.indexOf('kipia-v536') === -1,
            'прежней версии kipia-v536 нет');
    });
});
"""
src = src[:sw_start] + new_sw
src = src.replace('//   SW: kipia-test-v740.', '//   SW: kipia-v537.')
write(K + '/tests/test-task527.js', src)
print('[2] kip8/tests/test-task527.js — создан (SW-секция kip8: v537)')

# ---------- 3. бамп SW kip8 v536 → v537 ----------
OWN = ['test-task527.js']
changed = {}


def bump(path, old, new, label):
    s = read(path)
    n = s.count(old)
    if n == 0:
        return
    write(path, s.replace(old, new))
    changed[os.path.basename(path)] = changed.get(os.path.basename(path), 0) + n
    print('  %s: %s ×%d' % (os.path.basename(path), label, n))


tests_dir = os.path.join(K, 'tests')
files = sorted(f for f in os.listdir(tests_dir) if f.endswith('.js'))

print('Шаг 3а — ГАРДЫ v537 → v538 (кроме НОВОГО):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v537', 'kipia-v538', 'гард')

print('Шаг 3б — АССЕРТЫ v536 → v537:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v536', 'kipia-v537', 'ассерт')

print('Шаг 3в — sw.js CACHE_VERSION v536 → v537:')
sw_path = os.path.join(K, 'sw.js')
sw = read(sw_path)
if sw.count("const CACHE_VERSION = 'kipia-v536'") != 1:
    print('ОШИБКА: CACHE_VERSION v536 не найден')
    sys.exit(1)
write(sw_path, sw.replace("const CACHE_VERSION = 'kipia-v536'",
                          "const CACHE_VERSION = 'kipia-v537'"))
print('  sw.js: CACHE_VERSION v537')

print('Шаг 3г — регистрация test-task527.js в run-all.js:')
ra_path = os.path.join(tests_dir, 'run-all.js')
ra = read(ra_path)
if "require('./test-task527.js')" in ra:
    print('  уже зарегистрирован')
else:
    anchor = "require('./test-task526.js');"
    if ra.count(anchor) != 1:
        print('ОШИБКА: якорь run-all не найден')
        sys.exit(1)
    ra = ra.replace(anchor, anchor + "\n// Task 527 (зеркало kip8test): подписи размеров вне фигур,\n"
                                   "// данные расчёта — в картинке под фигурой, рамка 350px.\n"
                                   "// SW v537.\n"
                                   "require('./test-task527.js');")
    write(ra_path, ra)
    print('  зарегистрирован после test-task526.js')

print('')
print('Итого файлов: %d, замен: %d' % (len(changed), sum(changed.values())))
print('OK')
