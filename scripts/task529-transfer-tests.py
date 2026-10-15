#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 529 — перенос из kip8test в kip8 (по образцу
task528-transfer-tests.py; УРОК 527: SW-секция вырезается по
ПОСЛЕДНЕМУ разделителю перед «5. SW» — rindex):
  1) index.html — /tmp/kip8_index_transfer.html (prepare-kip8-transfer.py
     уже выполнен в kip8test; дифф 763 строки = ровно контент Task 529:
     CSS 185 + HTML 17 + хук 6 + JS-модуль 555);
  2) test-task529.js — копия kip8test с SW-секцией kip8 в ПОСТ-БАМП
     состоянии (assert kipia-v539, гвард kipia-v538 отсутствует);
  3) бамп SW kip8 v538 → v539: ГВАРДЫ v539 → v540 первыми (во всех,
     КРОМЕ перенесённого файла — он уже пост-бамп), АССЕРТЫ v538 →
     v539, sw.js CACHE_VERSION, регистрация test-task529.js.
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


SW_529 = """// ============================================================
// 5. SW — версия кэша бампнута (index.html менялся — Task 529)
// ============================================================
describe('Task 529 — SW: версия кэша', () => {

    test('SW: кэш поднят до kipia-v539 (Task 529)', () => {
        assertTrue(SW_SRC.indexOf('kipia-v539') !== -1,
            'SW несёт версию kipia-v539');
        assertTrue(SW_SRC.indexOf('kipia-v538') === -1,
            'прежней версии kipia-v538 нет (бамп v538 → v539)');
    });
});
"""

# ---------- 1. index.html ----------
src = read('/tmp/kip8_index_transfer.html')
write(K + '/index.html', src)
print('[1] kip8/index.html — перенесён из /tmp/kip8_index_transfer.html')

# ---------- 2. test-task529.js (новый) ----------
src = read(T + '/tests/test-task529.js')
assert 'kipia-test-v742' in src, 'test-task529.js: SW-блок kip8test не найден'
src = swap_sw(src, SW_529)
src = src.replace('//   SW: kipia-test-v742.', '//   SW: kipia-v539.')
write(K + '/tests/test-task529.js', src)
print('[2] kip8/tests/test-task529.js — создан (SW-секция kip8: v539)')

# ---------- 3. бамп SW kip8 v538 → v539 ----------
OWN = ['test-task529.js']
changed = {}


def bump(path, old, new):
    s = read(path)
    n = s.count(old)
    if n == 0:
        return
    write(path, s.replace(old, new))
    changed[os.path.basename(path)] = changed.get(os.path.basename(path), 0) + n


tests_dir = os.path.join(K, 'tests')
files = sorted(f for f in os.listdir(tests_dir) if f.endswith('.js'))

print('Шаг 3а — ГВАРДЫ v539 → v540 (кроме перенесённого):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v539', 'kipia-v540')

print('Шаг 3б — АССЕРТЫ v538 → v539:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v538', 'kipia-v539')

print('Шаг 3в — sw.js CACHE_VERSION v538 → v539:')
sw_path = os.path.join(K, 'sw.js')
sw = read(sw_path)
if sw.count("const CACHE_VERSION = 'kipia-v538'") != 1:
    print('ОШИБКА: CACHE_VERSION v538 не найден')
    sys.exit(1)
write(sw_path, sw.replace("const CACHE_VERSION = 'kipia-v538'",
                          "const CACHE_VERSION = 'kipia-v539'"))
print('  sw.js: CACHE_VERSION v539')

print('Шаг 3г — регистрация test-task529.js в run-all.js:')
ra_path = os.path.join(tests_dir, 'run-all.js')
ra = read(ra_path)
if "require('./test-task529.js')" in ra:
    print('  уже зарегистрирован')
else:
    anchor = "require('./test-task528.js');"
    if ra.count(anchor) != 1:
        print('ОШИБКА: якорь run-all не найден')
        sys.exit(1)
    ra = ra.replace(anchor, anchor + "\n// Task 529 (зеркало kip8test): LCD-окно «пейджер» в баре крошек\n"
                                   "// Табеля — матрица 96×17, время/дата/день недели, календарь,\n"
                                   "// сообщения в две строки. SW v539.\n"
                                   "require('./test-task529.js');")
    write(ra_path, ra)
    print('  зарегистрирован после test-task528.js')

print('Итог:', changed)
