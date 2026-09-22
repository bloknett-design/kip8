#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 390 — ПЕРЕНОС из kip8test в боевой kip8.
#
# index.html уже пропатчен scripts/task390-patch.py (репо kip8test,
# применён из корня kip8) — якоря совпали все.
#
# Этот скрипт — ТЕСТЫ + SW (порядок ВАЖЕН):
#   1) СНАЧАЛА бамп живых тестов kip8: guard kipia-v466 → kipia-v467,
#      ассерты kipia-v465 → kipia-v466 (+ sw.js kipia-v465 → v466);
#   2) ПОТОМ копия tests/test-task390.js из kip8test с маппингом
#      kipia-test-v618 → kipia-v466 (ассерты «присутствует»),
#      kipia-test-v619 → kipia-v467 (guard «отсутствует»)
#      (копия ПОСЛЕ бампа — иначе generic-бамп испортит её v466);
#   3) run-all.js — require('./test-task390.js') после task389.
#
# Адаптации живых тестов (task385/388/389) — отдельным шагом:
# python3 ../kip8test/scripts/task390-adapt-tests.py (из корня kip8).
#
# Итог: kip8 = kip8test (Task 390) + репо-специфика; версии SW:
# kip8test kipia-test-v618 ↔ kip8 kipia-v466.

import glob
import os

SRC_TEST390 = '/home/z/my-project/kip8test/tests/test-task390.js'
NEW_V = 'kipia-v466'      # kip8 после переноса (v465 + задача 390)
NEW_GUARD = 'kipia-v467'  # guard-версия

# ---------- 1) бамп живых тестов kip8 (guard первым!) ----------
changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count(NEW_V)          # kipia-v466 (guard-ы «отсутствует»)
    s = s.replace(NEW_V, NEW_GUARD)   # → v467
    n_assert = s.count('kipia-v465')  # ассерты «присутствует»
    s = s.replace('kipia-v465', NEW_V)
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests/ бамп: файлов %d' % len(changed))
for f, a, g in changed[:8]:
    print('  %s (ассерты v465→v466: %d, guard v466→v467: %d)' % (f, a, g))
if len(changed) > 8:
    print('  … и ещё %d файлов' % (len(changed) - 8))

# ---------- 2) sw.js — бамп ----------
sw = open('sw.js', encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v465'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v465'
assert "CACHE_VERSION = 'kipia-v466'" not in sw, 'sw.js: v466 уже был (двойной бамп?)'
sw = sw.replace(old, "CACHE_VERSION = 'kipia-v466'")
open('sw.js', 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v465 -> kipia-v466')

# ---------- 3) копия test-task390.js с маппингом версий ----------
s = open(SRC_TEST390, encoding='utf-8').read()
n1 = s.count('kipia-test-v618')
n2 = s.count('kipia-test-v619')
s = s.replace('kipia-test-v618', NEW_V)
s = s.replace('kipia-test-v619', NEW_GUARD)
with open('tests/test-task390.js', 'w', encoding='utf-8') as out:
    out.write(s)
print('tests/test-task390.js: скопирован (v618→v466: %d, guard v619→v467: %d)' % (n1, n2))

# ---------- 4) run-all.js — require test-task390 ----------
ra = 'tests/run-all.js'
s = open(ra, encoding='utf-8').read()
anchor = "require('./test-task389.js');"
line = "// Task 390: «Общая» вкладка — строки штата/текущего момента по\n" \
       "// категориям (мастера/дневные/сменные), выделенная шапка, примыкание\n" \
       "// ярлыков к окну, светлые тёплые ярлыки в тёмной теме\n" \
       "require('./test-task390.js');"
assert s.count(anchor) == 1, 'run-all.js: якорь task389 не найден'
assert "test-task390" not in s, 'run-all.js: task390 уже вставлен'
s = s.replace(anchor, anchor + '\n' + line)
open(ra, 'w', encoding='utf-8').write(s)
print('run-all.js: require test-task390.js добавлен (после task389)')

print('OK: перенос Task 390 (тесты + SW) завершён.')
