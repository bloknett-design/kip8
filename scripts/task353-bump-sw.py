#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 353 (kip8): SW-бамп kipia-v430 → v431 (перенос из kip8test:
# кнопка «Удалить» + модалка подтверждения в админ-панели, опция
# фильтра журнала ADMIN_DELETE_USER).
# Порядок замен в tests/ ВАЖЕН: СНАЧАЛА guard-ы v431 → v432,
# ЗАТЕМ ассерты v430 → v431. Исторические записи не переписываются.
# Запуск из корня репо kip8. test-task353.js кладётся ПОСЛЕ запуска.
import glob

# 1. sw.js — CACHE_VERSION
sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v430'"
new = "CACHE_VERSION = 'kipia-v431'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v430'
assert 'kipia-v431' not in sw, 'sw.js: v431 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v430 -> kipia-v431')

# 2. tests/*.js — guard v431→v432, затем ассерты v430→v431
changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v431')
    s = s.replace('kipia-v431', 'kipia-v432')
    n_assert = s.count('kipia-v430')
    s = s.replace('kipia-v430', 'kipia-v431')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v430→v431: %d, guard v431→v432: %d)' % (f, a, g))
