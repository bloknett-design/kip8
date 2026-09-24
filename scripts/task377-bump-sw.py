#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 377 ПЕРЕНОС: SW-бамп kip8 kipia-v453 → v454. Порядок замен в
# tests/ ВАЖЕН: СНАЧАЛА guard-ы v454 → v455, ЗАТЕМ ассерты v453 → v454.
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v453'"
new = "CACHE_VERSION = 'kipia-v454'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v453'
assert 'kipia-v454' not in sw, 'sw.js: v454 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v453 -> kipia-v454')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v454')
    s = s.replace('kipia-v454', 'kipia-v455')
    n_assert = s.count('kipia-v453')
    s = s.replace('kipia-v453', 'kipia-v454')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed[:5]:
    print('  %s (ассерты v453→v454: %d, guard v454→v455: %d)' % (f, a, g))
print('  ... всего %d файлов' % len(changed))
