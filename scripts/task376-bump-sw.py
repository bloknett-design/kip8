#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 376: SW-бамп kipia-v452 → v453 (перенос из kip8test fadcacb).
# Порядок замен в tests/ ВАЖЕН: СНАЧАЛА guard-ы v453 → v454,
# ЗАТЕМ ассерты v452 → v453.
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v452'"
new = "CACHE_VERSION = 'kipia-v453'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v452'
assert 'kipia-v453' not in sw, 'sw.js: v453 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v452 -> kipia-v453')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v453')
    s = s.replace('kipia-v453', 'kipia-v454')
    n_assert = s.count('kipia-v452')
    s = s.replace('kipia-v452', 'kipia-v453')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v452→v453: %d, guard v453→v454: %d)' % (f, a, g))
