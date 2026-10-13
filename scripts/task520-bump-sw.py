#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 520 (kip8, зеркало kip8test 3cea3dc6) — бамп SW-версий (v529→v530)
+ регистрация нового теста (по образцу task518-bump-sw.py):
  1) ГАРДЫ 'kipia-v530' → 'kipia-v531' — во всех файлах, КРОМЕ
     перенесённых test-task520.js / test-task394.js / test-task504.js
     (их v530 — актуальный ассерт, v531 — собственный гвард);
  2) АССЕРТЫ 'kipia-v529' → 'kipia-v530' — во всех старых файлах;
  3) sw.js: CACHE_VERSION v529 → v530 (index.html перенесён скриптом
     prepare-kip8-transfer.py — первый реальный прогон обновления
     Task 519: дифф с kip8 = ровно переносимый контент);
  4) регистрация test-task520.js в tests/run-all.js ПОСЛЕ бампа.
"""
import io
import os
import sys

ROOT = '/home/z/my-project/kip8'
OWN = ['test-task520.js', 'test-task394.js', 'test-task504.js']

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

print('Шаг 1 — ГАРДЫ v530 → v531 (кроме ПЕРЕНЕСЁННЫХ):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v530', 'kipia-v531', 'гард')

print('Шаг 2 — АССЕРТЫ v529 → v530:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v529', 'kipia-v530', 'ассерт')

print('Шаг 3 — sw.js: CACHE_VERSION v529 → v530:')
sw_path = os.path.join(ROOT, 'sw.js')
sw = io.open(sw_path, encoding='utf-8').read()
if sw.count('kipia-v529') != 1:
    fails.append('sw.js: упоминаний v529 = %d (ожидалось 1)' % sw.count('kipia-v529'))
else:
    sw = sw.replace("const CACHE_VERSION = 'kipia-v529'",
                    "const CACHE_VERSION = 'kipia-v530'")
    io.open(sw_path, 'w', encoding='utf-8').write(sw)
    print('  sw.js: CACHE_VERSION = kipia-v530')

print('Шаг 4 — регистрация НОВОГО теста в run-all.js:')
run_all = os.path.join(tests_dir, 'run-all.js')
src = io.open(run_all, encoding='utf-8').read()
if "require('./test-task520.js');" in src:
    print('  уже зарегистрирован')
elif "require('./test-task518.js');" in src:
    anchor = "require('./test-task518.js');\n"
    add = ("// Task 520 (зеркало kip8test 3cea3dc6): окно мероприятий\n"
           "// Табеля — формат строки СИЗ месяца упрощён (наименование ·\n"
           "// ФИО) + НОВАЯ группа «Просроченная выдача СИЗ за всё время»\n"
           "// (мм.гггг красным, сортировка по фамилиям). SW v530.\n"
           "require('./test-task520.js');\n")
    src = src.replace(anchor, anchor + add, 1)
    io.open(run_all, 'w', encoding='utf-8').write(src)
    print('  зарегистрирован после test-task518.js')
else:
    fails.append('run-all.js: якорь test-task518 не найден')

# санитарная сверка
sw = io.open(sw_path, encoding='utf-8').read()
if 'kipia-v531' in sw:
    fails.append('sw.js содержит v531 (двойной бамп)')
if 'kipia-v529' in sw:
    fails.append('sw.js содержит v529 после бампа')

print()
print('Итого замен в тестах: %d в %d файлах' % (sum(changed.values()), len(changed)))
if fails:
    print('ПРОВАЛЕНО: %d' % len(fails))
    for f in fails:
        print(' - ' + f)
    sys.exit(1)
print('БУМП ЗАВЕРШЁН')
