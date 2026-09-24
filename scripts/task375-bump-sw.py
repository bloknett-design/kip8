#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 375 (перенос в kip8): SW-бамп kipia-v451 → v452. Порядок замен
# в tests/ ВАЖЕН (урок Task 361): СНАЧАЛА guard-ы «v452 не существует»
# → v453, ЗАТЕМ ассерты v451 → v452. Запуск из корня репо kip8.
import glob

# 1. sw.js — CACHE_VERSION
sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v451'"
new = "CACHE_VERSION = 'kipia-v452'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v451'
assert 'kipia-v452' not in sw, 'sw.js: v452 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v451 -> kipia-v452')

# 2. tests/*.js — guard v452→v453, затем ассерты v451→v452
changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v452')
    s = s.replace('kipia-v452', 'kipia-v453')
    n_assert = s.count('kipia-v451')
    s = s.replace('kipia-v451', 'kipia-v452')
    s = s.replace('v452 ещё не существует', 'v453 ещё не существует')
    s = s.replace('v451 ещё не существует', 'v453 ещё не существует')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v451→v452: %d, guard v452→v453: %d)' % (f, a, g))

# 3. контроль: v452 в sw.js ровно один
assert sw.count('kipia-v452') == 1
print('OK: единственный kipia-v452 в sw.js')
