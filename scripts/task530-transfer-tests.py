#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 530 — перенос из kip8test в kip8 (по образцу
task529-transfer-tests.py; УРОК 527: SW-секция вырезается по
ПОСЛЕДНЕМУ разделителю перед «5. SW» — rindex):
  1) index.html — /tmp/kip8_index_transfer.html (prepare-kip8-transfer.py
     уже выполнен в kip8test; дифф 610 строк = контент Task 530:
     CSS рамка-выступ/прямые углы + HTML 205×17 + JS-модуль);
     WorkSchedule.gs скопирован напрямую (репо синхронны), Code.gs —
     точечная правка роутинга (файлы репо косметически различаются);
  2) test-task530.js + test-task529.js — копии kip8test с SW-секцией
     kip8 в ПОСТ-БАМП состоянии (assert kipia-v540, гварда kip8
     «старой версии нет» → v539);
  3) бамп SW kip8 v539 → v540: ГВАРДЫ v540 → v541 первыми (во всех,
     КРОМЕ перенесённых файлов — они уже пост-бамп), АССЕРТЫ v539 →
     v540, sw.js CACHE_VERSION, регистрация test-task530.js;
  4) DEPLOY-Task530 — копия (в kip8 важен: есть СЕРВЕРНАЯ часть).
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
    (rindex — УРОК Task 527; маркер «// 5. SW» у 529, «// E. SW» у 530)."""
    for marker in ('// 5. SW', '// E. SW'):
        if marker in src:
            sw_start = src.rindex('// ===========', 0, src.index(marker))
            return src[:sw_start] + new_sw
    raise ValueError('SW-секция не найдена')


SW_530 = """// ============================================================
// 5. SW — версия кэша (зеркало kip8test, Task 530)
// ============================================================
describe('Task 530 — SW: версия кэша', () => {

    test('sw.js: CACHE_VERSION = kipia-v540', () => {
        const m = SW_SRC.match(/const CACHE_VERSION = '(kipia-v\\d+)'/);
        assertTrue(m !== null, 'CACHE_VERSION найден');
        assertEqual(m[1], 'kipia-v540', 'SW поднят до v540 (Task 530)');
    });

});
"""

# ---------- 1. index.html ----------
html = read('/tmp/kip8_index_transfer.html')
write(K + '/index.html', html)
print('[1] kip8/index.html — перенесён (дифф 610 строк = Task 530)')

# ---------- 2. тесты: SW-секции kip8 в пост-бамп состоянии ----------
for name in ('test-task530.js', 'test-task529.js'):
    src = read(T + '/tests/' + name)
    assert 'kipia-test-v743' in src, name + ': SW-блок kip8test не найден'
    src = swap_sw(src, SW_530)
    src = src.replace('//   SW: kipia-test-v743.', '//   SW: kipia-v540.')
    # «старой версии нет» — на kip8 это v539 (предыдущая версия kip8)
    src = src.replace('kipia-test-v742', 'kipia-v539')
    write(K + '/tests/' + name, src)
    print('[2] kip8/tests/%s — SW-секция kip8: v540' % name)

# ---------- 3. бамп SW kip8 v539 → v540 ----------
OWN = ['test-task530.js', 'test-task529.js']
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

print('Шаг 3а — ГВАРДЫ v540 → v541 (кроме перенесённых):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v540', 'kipia-v541')

print('Шаг 3б — АССЕРТЫ v539 → v540:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v539', 'kipia-v540')

print('Шаг 3в — sw.js CACHE_VERSION v539 → v540:')
sw_path = os.path.join(K, 'sw.js')
sw = read(sw_path)
if sw.count("const CACHE_VERSION = 'kipia-v539'") != 1:
    print('ОШИБКА: CACHE_VERSION v539 не найден')
    sys.exit(1)
write(sw_path, sw.replace("const CACHE_VERSION = 'kipia-v539'",
                          "const CACHE_VERSION = 'kipia-v540'"))
print('  sw.js: CACHE_VERSION v540')

print('Шаг 3г — регистрация test-task530.js в run-all.js:')
ra_path = os.path.join(tests_dir, 'run-all.js')
ra = read(ra_path)
if "require('./test-task530.js')" in ra:
    print('  уже зарегистрирован')
else:
    anchor = "require('./test-task529.js');"
    if ra.count(anchor) < 1:
        print('ОШИБКА: якорь run-all (529) не найден')
        sys.exit(1)
    ra = ra.replace(anchor, anchor + "\n// Task 530 (зеркало kip8test): LCD-окно — рамка-выступ,\n"
                                   "// одна строка данных, погода meteoinfo.ru, ровная сетка,\n"
                                   "// реальные сообщения. SW v540.\n"
                                   "require('./test-task530.js');", 1)
    write(ra_path, ra)
    print('  зарегистрирован после test-task529.js')

# ---------- 4. DEPLOY-документ ----------
dep = read(T + '/DEPLOY-Task530-lcd-weather-even-grid.md')
write(K + '/DEPLOY-Task530-lcd-weather-even-grid.md', dep)
print('[4] DEPLOY-Task530 — скопирован')

print('Итог:', changed)
