#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 518 (kip8, зеркало kip8test 4341b559) — бамп SW-версий (v528→v529)
+ регистрация нового теста (по образцу task513-bump-sw.py):
  1) ГАРДЫ 'kipia-v529' → 'kipia-v530' — во всех файлах,
     КРОМЕ нового test-task518.js (его v529 — актуальный ассерт,
     v530 — его собственный гард);
  2) АССЕРТЫ 'kipia-v528' → 'kipia-v529' — во всех старых файлах;
  3) sw.js: CACHE_VERSION v528 → v529 (менялся index.html);
  4) регистрация test-task518.js в tests/run-all.js ПОСЛЕ бампа.
"""
import io
import os
import sys

ROOT = '/home/z/my-project/kip8'
OWN = ['test-task518.js']

fails = []
changed = {}


def bump(path, old, new, label):
    src = io.open(path, encoding='utf-8').read()
    n = src.count(old)
    if n == 0:
        return
    src = src.replace(old, new)
    io.open(path, 'w', encoding='utf-8').write(src)
    changed[os.path.basename(path)] = changed.get(
        os.path.basename(path), 0) + n
    print('  %s: %s ×%d' % (os.path.basename(path), label, n))


tests_dir = os.path.join(ROOT, 'tests')
files = sorted(f for f in os.listdir(tests_dir) if f.endswith('.js'))

print('Шаг 1 — ГАРДЫ v529 → v530 (кроме НОВОГО):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v529', 'kipia-v530', 'гард')

print('Шаг 2 — АССЕРТЫ v528 → v529:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v528', 'kipia-v529', 'ассерт')

print('Шаг 3 — sw.js: CACHE_VERSION v528 → v529:')
sw_path = os.path.join(ROOT, 'sw.js')
sw = io.open(sw_path, encoding='utf-8').read()
if sw.count('kipia-v528') != 1:
    fails.append('sw.js: упоминаний v528 = %d (ожидалось 1)' % sw.count('kipia-v528'))
else:
    sw = sw.replace("const CACHE_VERSION = 'kipia-v528'",
                    "const CACHE_VERSION = 'kipia-v529'")
    io.open(sw_path, 'w', encoding='utf-8').write(sw)
    print('  sw.js: CACHE_VERSION = kipia-v529')

print('Шаг 4 — регистрация НОВОГО теста в run-all.js:')
run_all = os.path.join(tests_dir, 'run-all.js')
src = io.open(run_all, encoding='utf-8').read()
if "require('./test-task518.js');" in src:
    print('  уже зарегистрирован')
elif "require('./test-task513.js');" in src:
    anchor = "require('./test-task513.js');\n"
    add = ("// Task 518 (зеркало kip8test 4341b559): заявка Cu50 (50 Ом →\n"
           "// −1,2970e−14 °C вместо 0) + аудит всех Инженерных калькуляторов:\n"
           "// гвард номинала и сглаживание в tempCalcInvertValue, якорь\n"
           "// E(0)=0 в calcTcVoltage (scripts/task518-audit.js: 102 пробы,\n"
           "// было 56 находок).\n"
           "// SW v529.\n"
           "require('./test-task518.js');\n")
    src = src.replace(anchor, anchor + add, 1)
    io.open(run_all, 'w', encoding='utf-8').write(src)
    print('  зарегистрирован после test-task513.js')
else:
    fails.append('run-all.js: якорь test-task513 не найден')

# санитарная сверка
sw = io.open(sw_path, encoding='utf-8').read()
if 'kipia-v530' in sw:
    fails.append('sw.js содержит v530 (двойной бамп)')
if 'kipia-v528' in sw:
    fails.append('sw.js содержит v528 после бампа')

print()
print('Итого замен в тестах: %d в %d файлах' % (sum(changed.values()), len(changed)))
if fails:
    print('ПРОВАЛЕНО: %d' % len(fails))
    for f in fails:
        print(' - ' + f)
    sys.exit(1)
print('БУМП ЗАВЕРШЁН')
