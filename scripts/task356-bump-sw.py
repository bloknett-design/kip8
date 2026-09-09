#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 356 (kip8): SW-бамп kipia-v432 → v433 (index.html менялся —
# шахматка табеля: точка «·» убрана и в ПУСТЫХ ячейках БЕЗ кодов
# событий на рабочих днях; бейджи, коды смен/неявок и планы «ОТ» —
# прежний вид). Зеркало task356-bump-sw.py из kip8test.
# Порядок замен в tests/ ВАЖЕН: СНАЧАЛА guard-ы v433 → v434, ЗАТЕМ
# ассерты v432 → v433.
# Запуск из корня репо kip8.
# NOTE: test-task356.js кладётся ПОСЛЕ этого скрипта (guard v434 в
# нём уже актуален), поэтому скрипт его не тронет.
import glob

# 1. sw.js — CACHE_VERSION
sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v432'"
new = "CACHE_VERSION = 'kipia-v433'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v432'
assert 'kipia-v433' not in sw, 'sw.js: v433 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v432 -> kipia-v433')

# 2. tests/*.js — guard v433→v434, затем ассерты v432→v433
changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v433')
    s = s.replace('kipia-v433', 'kipia-v434')
    n_assert = s.count('kipia-v432')
    s = s.replace('kipia-v432', 'kipia-v433')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v432→v433: %d, guard v433→v434: %d)' % (f, a, g))
