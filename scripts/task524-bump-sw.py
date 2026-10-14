#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 524 — бамп SW-версий в тестах kip8 (v533→v534) + регистрация
нового теста (по образцу task523-bump-sw.py, зеркало kip8test):
  1) ГАРДЫ 'kipia-v534' → 'kipia-v535' — во всех файлах, КРОМЕ
     нового test-task524.js (гварды «двойного бампа нет» в старых
     файлах смотрят на одну версию ВПЕРЁД — двигаются ПЕРВЫМИ,
     до АССЕРТОВ, иначе ассерты уже-bumped попадут под гвард);
  2) АССЕРТЫ 'kipia-v533' → 'kipia-v534' — во всех старых файлах;
  3) sw.js: CACHE_VERSION v533 → v534 (менялся index.html — канон
     справочника «Коды_статусов»);
  4) регистрация test-task524.js в tests/run-all.js.
"""
import io
import os

ROOT = '/home/z/my-project/kip8'
OWN = ['test-task524.js']

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

print('Шаг 1 — ГАРДЫ v534 → v535 (кроме НОВОГО):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v534', 'kipia-v535', 'гард')

print('Шаг 2 — АССЕРТЫ v533 → v534:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v533', 'kipia-v534', 'ассерт')

print('Шаг 3 — sw.js: CACHE_VERSION v533 → v534:')
sw_path = os.path.join(ROOT, 'sw.js')
sw = io.open(sw_path, encoding='utf-8').read()
if sw.count('kipia-v533') == 1:
    sw = sw.replace("const CACHE_VERSION = 'kipia-v533'",
                    "const CACHE_VERSION = 'kipia-v534'")
    io.open(sw_path, 'w', encoding='utf-8').write(sw)
    print('  sw.js: CACHE_VERSION = kipia-v534')
elif sw.count('kipia-v534') == 1:
    print('  sw.js: уже kipia-v534 (пропуск)')
else:
    raise SystemExit('sw.js: неожиданное состояние версий')

print('Шаг 4 — регистрация НОВОГО теста в run-all.js:')
run_all = os.path.join(tests_dir, 'run-all.js')
src = io.open(run_all, encoding='utf-8').read()
if "require('./test-task524.js');" in src:
    print('  уже зарегистрирован')
elif "require('./test-task523.js');" in src:
    anchor = "require('./test-task523.js');\n"
    add = ("// Task 524: наименования кодов «д»/«н» справочника\n"
           "// «Коды_статусов» — убран хвост «в комментарии» (канон\n"
           "// index.html + StatusCodesInit.gs; продолжительность —\n"
           "// временами L/M, Task 523). «ОВ» не тронут. SW v534.\n")
    src = src.replace(anchor, anchor + add +
                      "require('./test-task524.js');\n", 1)
    io.open(run_all, 'w', encoding='utf-8').write(src)
    print('  зарегистрирован после test-task523.js')
else:
    raise SystemExit('run-all.js: якорь test-task523 не найден')

total = sum(changed.values())
print('ИТОГО замен в тестах: %d' % total)
