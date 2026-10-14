#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 526 — бамп SW-версий в тестах kip8 (v535→v536) + регистрация
нового теста (по образцу task525-bump-sw.py, зеркало kip8test):
  1) ГАРДЫ 'kipia-v536' → 'kipia-v537' — во всех файлах, КРОМЕ
     нового test-task526.js (гварды «двойного бампа нет» в старых
     файлах смотрят на одну версию ВПЕРЁД — двигаются ПЕРВЫМИ,
     до АССЕРТОВ, иначе ассерты уже-bumped попадут под гвард);
  2) АССЕРТЫ 'kipia-v535' → 'kipia-v536' — во всех старых файлах;
  3) sw.js: CACHE_VERSION v535 → v536 (менялся index.html —
     анимированные пояснительные схемы геометрии);
  4) регистрация test-task526.js в tests/run-all.js.
"""
import io
import os

ROOT = '/home/z/my-project/kip8'
OWN = ['test-task526.js']

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

print('Шаг 1 — ГАРДЫ v536 → v537 (кроме НОВОГО):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v536', 'kipia-v537', 'гард')

print('Шаг 2 — АССЕРТЫ v535 → v536:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v535', 'kipia-v536', 'ассерт')

print('Шаг 3 — sw.js: CACHE_VERSION v535 → v536:')
sw_path = os.path.join(ROOT, 'sw.js')
sw = io.open(sw_path, encoding='utf-8').read()
if sw.count('kipia-v535') == 1:
    sw = sw.replace("const CACHE_VERSION = 'kipia-v535'",
                    "const CACHE_VERSION = 'kipia-v536'")
    io.open(sw_path, 'w', encoding='utf-8').write(sw)
    print('  sw.js: CACHE_VERSION = kipia-v536')
elif sw.count('kipia-v536') == 1:
    print('  sw.js: уже kipia-v536 (пропуск)')
else:
    raise SystemExit('sw.js: неожиданное состояние версий')

print('Шаг 4 — регистрация НОВОГО теста в run-all.js:')
run_all = os.path.join(tests_dir, 'run-all.js')
src = io.open(run_all, encoding='utf-8').read()
if "require('./test-task526.js');" in src:
    print('  уже зарегистрирован')
elif "require('./test-task525.js');" in src:
    anchor = "require('./test-task525.js');\n"
    add = ("// Task 526: Геометрия — пояснительные картинки заменены\n"
           "// анимированными «живыми» схемами в рамках с непрозрачным\n"
           "// фоном (светлая — бежево-бело-молочная #F7F2E6, тёмная —\n"
           "// графитово-синяя #17222E): реальные пропорции, размеры с\n"
           "// фактическими значениями, живой расчёт, точные стрелки.\n"
           "// SW v536.\n")
    src = src.replace(anchor, anchor + add +
                      "require('./test-task526.js');\n", 1)
    io.open(run_all, 'w', encoding='utf-8').write(src)
    print('  зарегистрирован после test-task525.js')
else:
    raise SystemExit('run-all.js: якорь test-task525 не найден')

total = sum(changed.values())
print('ИТОГО замен в тестах: %d' % total)
