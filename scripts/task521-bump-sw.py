#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 521 (kip8, зеркало kip8test fc032e1a) — бамп SW-версий (v530→v531)
+ регистрация нового теста (по образцу task520-bump-sw.py):
  1) ГАРДЫ 'kipia-v531' → 'kipia-v532' — во всех файлах, КРОМЕ
     перенесённых test-task521.js / test-task322.js (их v531 —
     актуальный ассерт, v532 — собственный гвард);
  2) АССЕРТЫ 'kipia-v530' → 'kipia-v531' — во всех старых файлах;
  3) sw.js: CACHE_VERSION v530 → v531 (index.html перенесён скриптом
     prepare-kip8-transfer.py — дифф = ровно переносимый контент
     Task 521, 213 строк, только малая форма д/н);
  4) регистрация test-task521.js в tests/run-all.js ПОСЛЕ бампа.
"""
import io
import os
import sys

ROOT = '/home/z/my-project/kip8'
OWN = ['test-task521.js', 'test-task322.js']

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

print('Шаг 1 — ГАРДЫ v531 → v532 (кроме ПЕРЕНЕСЁННЫХ):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v531', 'kipia-v532', 'гард')

print('Шаг 2 — АССЕРТЫ v530 → v531:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v530', 'kipia-v531', 'ассерт')

print('Шаг 3 — sw.js: CACHE_VERSION v530 → v531:')
sw_path = os.path.join(ROOT, 'sw.js')
sw = io.open(sw_path, encoding='utf-8').read()
if sw.count('kipia-v530') != 1:
    fails.append('sw.js: упоминаний v530 = %d (ожидалось 1)' % sw.count('kipia-v530'))
else:
    sw = sw.replace("const CACHE_VERSION = 'kipia-v530'",
                    "const CACHE_VERSION = 'kipia-v531'")
    io.open(sw_path, 'w', encoding='utf-8').write(sw)
    print('  sw.js: CACHE_VERSION = kipia-v531')

print('Шаг 4 — регистрация НОВОГО теста в run-all.js:')
run_all = os.path.join(tests_dir, 'run-all.js')
src = io.open(run_all, encoding='utf-8').read()
if "require('./test-task521.js');" in src:
    print('  уже зарегистрирован')
elif "require('./test-task520.js');" in src:
    anchor = "require('./test-task520.js');\n"
    add = ("// Task 521 (зеркало kip8test fc032e1a): малая форма д/н\n"
           "// Табеля — поля «Время начала/окончания работ» (type=time)\n"
           "// вместо ручного ввода часов; часы переработки считаются\n"
           "// автоматически (полночь +24 ч, живая строка расчёта).\n"
           "// SW v531.\n"
           "require('./test-task521.js');\n")
    src = src.replace(anchor, anchor + add, 1)
    io.open(run_all, 'w', encoding='utf-8').write(src)
    print('  зарегистрирован после test-task520.js')
else:
    fails.append('run-all.js: якорь test-task520 не найден')

# санитарная сверка
sw = io.open(sw_path, encoding='utf-8').read()
if 'kipia-v532' in sw:
    fails.append('sw.js содержит v532 (двойной бамп)')
if 'kipia-v530' in sw:
    fails.append('sw.js содержит v530 после бампа')

print()
print('Итого замен в тестах: %d в %d файлах' % (sum(changed.values()), len(changed)))
if fails:
    print('ПРОВАЛЕНО: %d' % len(fails))
    for f in fails:
        print(' - ' + f)
    sys.exit(1)
print('БУМП ЗАВЕРШЁН')
