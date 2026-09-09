#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 355: SW-бамп kip8 kipia-v431 → v432 (index.html перенесён из
# kip8test — шахматка табеля: точка «·» убрана из нерабочих
# выходных/праздничных ячеек, линии ячеек/шапки ярче, розовый
# выходных пастельнее #f7d9e3 → #f8e2e9).
# Порядок замен в tests/ ВАЖЕН: СНАЧАЛА guard-ы v432 → v433,
# ЗАТЕМ ассерты v431 → v432. Запуск из корня репо kip8.
# NOTE: test-task355.js копируется ПОСЛЕ этого скрипта (guard v433
# в нём уже актуален).
import glob

# 1. sw.js — CACHE_VERSION
sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v431'"
new = "CACHE_VERSION = 'kipia-v432'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v431'
assert 'kipia-v432' not in sw, 'sw.js: v432 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v431 -> kipia-v432')

# 2. tests/*.js — guard v432→v433, затем ассерты v431→v432
changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v432')
    s = s.replace('kipia-v432', 'kipia-v433')
    n_assert = s.count('kipia-v431')
    s = s.replace('kipia-v431', 'kipia-v432')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v431→v432: %d, guard v432→v433: %d)' % (f, a, g))
