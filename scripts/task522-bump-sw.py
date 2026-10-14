#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 522 (kip8, зеркало kip8test Task 522) — бамп SW-версий (v531→v532)
+ регистрация нового теста (по образцу task521-bump-sw.py):
  1) ГАРДЫ 'kipia-v532' → 'kipia-v533' — во всех файлах, КРОМЕ
     перенесённого test-task522.js (его v532 — актуальный ассерт,
     v533 — собственный гвард);
  2) АССЕРТЫ 'kipia-v531' → 'kipia-v532' — во всех старых файлах;
  3) sw.js: CACHE_VERSION v531 → v532 (index.html перенесён скриптом
     prepare-kip8-transfer.py — дифф = ровно переносимый контент
     Task 522, 184 строки: секция «Статус дня» в окне ячейки);
  4) регистрация test-task522.js в tests/run-all.js ПОСЛЕ бампа.
"""
import io
import os
import sys

ROOT = '/home/z/my-project/kip8'
OWN = ['test-task522.js']

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

print('Шаг 1 — ГАРДЫ v532 → v533 (кроме ПЕРЕНЕСЁННОГО):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v532', 'kipia-v533', 'гард')

print('Шаг 2 — АССЕРТЫ v531 → v532:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v531', 'kipia-v532', 'ассерт')

print('Шаг 3 — sw.js: CACHE_VERSION v531 → v532:')
sw_path = os.path.join(ROOT, 'sw.js')
sw = io.open(sw_path, encoding='utf-8').read()
if sw.count('kipia-v531') != 1:
    fails.append('sw.js: упоминаний v531 = %d (ожидалось 1)' % sw.count('kipia-v531'))
else:
    sw = sw.replace("const CACHE_VERSION = 'kipia-v531'",
                    "const CACHE_VERSION = 'kipia-v532'")
    io.open(sw_path, 'w', encoding='utf-8').write(sw)
    print('  sw.js: CACHE_VERSION = kipia-v532')

print('Шаг 4 — регистрация НОВОГО теста в run-all.js:')
run_all = os.path.join(tests_dir, 'run-all.js')
src = io.open(run_all, encoding='utf-8').read()
if "require('./test-task522.js');" in src:
    print('  уже зарегистрирован')
elif "require('./test-task521.js');" in src:
    anchor = "require('./test-task521.js');\n"
    add = ("// Task 522: Табель — окно ячейки: секция «Статус дня» — справка\n"
           "// по коду «д»/«н» дневного персонала + «Время работы: N ч» из\n"
           "// колонки K; ховер открывает окно и без мероприятий (зеркало\n"
           "// kip8test Task 522). SW v532.\n"
           "require('./test-task522.js');\n")
    src = src.replace(anchor, anchor + add, 1)
    io.open(run_all, 'w', encoding='utf-8').write(src)
    print('  зарегистрирован после test-task521.js')
else:
    fails.append('run-all.js: якорь test-task521 не найден')

# санитарная сверка
sw = io.open(sw_path, encoding='utf-8').read()
if 'kipia-v533' in sw:
    fails.append('sw.js содержит v533 (двойной бамп)')
if 'kipia-v531' in sw:
    fails.append('sw.js содержит v531 после бампа')

print()
print('Итого замен в тестах: %d в %d файлах' % (sum(changed.values()), len(changed)))
if fails:
    print('ПРОВАЛЕНО: %d' % len(fails))
    for f in fails:
        print(' - ' + f)
    sys.exit(1)
print('БУМП ЗАВЕРШЁН')
