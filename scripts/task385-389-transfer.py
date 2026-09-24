#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Tasks 385–389 — ПЕРЕНОС из kip8test в боевой kip8 (команда
# пользователя: «Перенеси все изменения в боевой kip8»).
#
# index.html/scripts/*.gs уже пропатчены последовательным применением
# scripts/task{385,386,387,388,389}-patch.py (репо kip8test) —
# якоря совпали все (0 несовпадений), итоговый дифф kip8↔kip8test
# по index.html = 55 репо-специфичных строк (ключи localStorage без
# префикса, isolateLocalStorage, комментарии kip8/kip8test).
#
# Этот скрипт — ТЕСТЫ + SW:
#   1) tests/ — синхронизация из kip8test (все файлы, включая новые
#      test-task385..389.js) с маппингом версий:
#        kipia-test-v617 → kipia-v465 (ассерты «присутствует»)
#        kipia-test-v618 → kipia-v466 (guard-ы «отсутствует»)
#   2) run-all.js — вставка kip8-специфичного require('./test-task344.js')
#      (после require('./test-task343.js'), как было);
#   3) tests/test-task344.js (только kip8) — бамп kipia-v460→v465,
#      guard kipia-v461→v466;
#   4) sw.js — CACHE_VERSION kipia-v460 → kipia-v465.
#
# Итог: kip8 = kip8test (Task 389) + репо-специфика; версии SW:
# kip8test kipia-test-v617 ↔ kip8 kipia-v465.

import glob
import os

SRC_TESTS = '/home/z/my-project/kip8test/tests'
NEW_V = 'kipia-v465'      # kip8 после переноса (v460 + 5 задач)
NEW_GUARD = 'kipia-v466'  # guard-версия

def map_versions(s):
    n1 = s.count('kipia-test-v617')
    s = s.replace('kipia-test-v617', NEW_V)
    n2 = s.count('kipia-test-v618')
    s = s.replace('kipia-test-v618', NEW_GUARD)
    return s, n1, n2

# ---------- 1) tests/ из kip8test ----------
copied = []
for f in sorted(glob.glob(os.path.join(SRC_TESTS, '*.js'))):
    name = os.path.basename(f)
    s = open(f, encoding='utf-8').read()
    s, n1, n2 = map_versions(s)
    with open(os.path.join('tests', name), 'w', encoding='utf-8') as out:
        out.write(s)
    copied.append((name, n1, n2))
print('tests/ синхронизировано файлов: %d' % len(copied))
for name, n1, n2 in copied:
    if n1 or n2:
        print('  %s (v617→v465: %d, guard v618→v466: %d)' % (name, n1, n2))

# ---------- 2) run-all.js — kip8-специфичный task344 ----------
ra = 'tests/run-all.js'
s = open(ra, encoding='utf-8').read()
anchor = "require('./test-task343.js');"
line = "require('./test-task344.js');"
assert s.count(anchor) == 1, 'run-all.js: якорь task343 не найден'
assert line not in s, 'run-all.js: task344 уже вставлен'
s = s.replace(anchor, anchor + '\n' + line)
open(ra, 'w', encoding='utf-8').write(s)
print('run-all.js: require test-task344.js восстановлен (kip8-специфика)')

# ---------- 3) test-task344.js (только kip8) — бамп ----------
t344 = 'tests/test-task344.js'
s = open(t344, encoding='utf-8').read()
n460 = s.count('kipia-v460')
n461 = s.count('kipia-v461')
assert n460 > 0, 'test-task344.js: kipia-v460 не найден'
s = s.replace('kipia-v461', NEW_GUARD)   # СНАЧАЛА guard (порядок бампов)
s = s.replace('kipia-v460', NEW_V)
open(t344, 'w', encoding='utf-8').write(s)
print('test-task344.js: ассерты v460→v465: %d, guard v461→v466: %d' % (n460, n461))

# ---------- 4) sw.js — бамп ----------
sw = open('sw.js', encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v460'"
new = "CACHE_VERSION = 'kipia-v465'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v460'
assert "CACHE_VERSION = 'kipia-v465'" not in sw, 'sw.js: v465 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open('sw.js', 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v460 -> kipia-v465')

print('OK: перенос 385–389 (тесты + SW) завершён.')
