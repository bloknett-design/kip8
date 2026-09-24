#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 391 — ПЕРЕНОС из kip8test в боевой kip8.
#
# index.html уже пропатчен ../kip8test/scripts/task391-patch.py
# (из корня kip8) — все 7 якорей совпали.
#
# Этот скрипт — ТЕСТЫ + SW (порядок ВАЖЕН):
#   1) СНАЧАЛА бамп живых тестов kip8: guard kipia-v467 → kipia-v468,
#      ассерты kipia-v466 → kipia-v467 (+ sw.js kipia-v466 → v467);
#   2) ПОТОМ копия tests/test-task391.js из kip8test с маппингом
#      kipia-test-v619 → kipia-v467 (ассерты «присутствует»),
#      kipia-test-v620 → kipia-v468 (guard «отсутствует»)
#      (копия ПОСЛЕ бампа — иначе generic-бамп испортит её v467);
#   3) run-all.js — require('./test-task391.js') после task390.
#
# Адаптации живых тестов (task386/388/389/390) — отдельным шагом:
# python3 ../kip8test/scripts/task391-adapt-tests.py (из корня kip8).
#
# Итог: kip8 = kip8test (Task 391) + репо-специка; версии SW:
# kip8test kipia-test-v619 ↔ kip8 kipia-v467.

import glob

SRC_TEST391 = '/home/z/my-project/kip8test/tests/test-task391.js'
NEW_V = 'kipia-v467'      # kip8 после переноса (v466 + задача 391)
NEW_GUARD = 'kipia-v468'  # guard-версия

# ---------- 1) бамп живых тестов kip8 (guard первым!) ----------
changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count(NEW_V)          # kipia-v467 (guard-ы «отсутствует»)
    s = s.replace(NEW_V, NEW_GUARD)   # → v468
    n_assert = s.count('kipia-v466')  # ассерты «присутствует»
    s = s.replace('kipia-v466', NEW_V)
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests/ бамп: файлов %d' % len(changed))
for f, a, g in changed[:8]:
    print('  %s (ассерты v466→v467: %d, guard v467→v468: %d)' % (f, a, g))
if len(changed) > 8:
    print('  … и ещё %d файлов' % (len(changed) - 8))

# ---------- 2) sw.js — бамп ----------
sw = open('sw.js', encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v466'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v466'
assert "CACHE_VERSION = 'kipia-v467'" not in sw, 'sw.js: v467 уже был (двойной бамп?)'
sw = sw.replace(old, "CACHE_VERSION = 'kipia-v467'")
open('sw.js', 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v466 -> kipia-v467')

# ---------- 3) копия test-task391.js с маппингом версий ----------
s = open(SRC_TEST391, encoding='utf-8').read()
n1 = s.count('kipia-test-v619')
n2 = s.count('kipia-test-v620')
s = s.replace('kipia-test-v620', NEW_GUARD)   # guard ПЕРВЫМ (v620→v468)
s = s.replace('kipia-test-v619', NEW_V)       # затем ассерты (v619→v467)
with open('tests/test-task391.js', 'w', encoding='utf-8') as out:
    out.write(s)
print('tests/test-task391.js: скопирован (v619→v467: %d, guard v620→v468: %d)' % (n1, n2))

# ---------- 4) run-all.js — require test-task391 ----------
ra = 'tests/run-all.js'
s = open(ra, encoding='utf-8').read()
anchor = "require('./test-task390.js');"
line = "// Task 391: строки шапки — формат в скобках «(N) ((N) мастера…)»;\n" \
       "// шрифт крупнее/ярче (14px/600/0.95); кнопка «Добавить работника» —\n" \
       "// акцентная в стиле сайта (синий/оранжевый по теме)\n" \
       "require('./test-task391.js');"
assert s.count(anchor) == 1, 'run-all.js: якорь task390 не найден'
assert "test-task391" not in s, 'run-all.js: task391 уже вставлен'
s = s.replace(anchor, anchor + '\n' + line)
open(ra, 'w', encoding='utf-8').write(s)
print('run-all.js: require test-task391.js добавлен (после task390)')

print('OK: перенос Task 391 (тесты + SW) завершён.')
