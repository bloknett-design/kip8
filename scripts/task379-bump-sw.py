#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 379-transfer: SW-бамп kipia-v455 → v456 (index.html менялся —
# шахматка: пустые ячейки светлой темы #FFFFFF; окна бара: раскрытие
# = оверлей вниз поверх бара, габарит бара неизменен). Порядок замен
# в tests/ ВАЖЕН: СНАЧАЛА guard-ы v456 → v457 (guards смотрят на
# новую несуществующую), ЗАТЕМ ассерты v455 → v456. test-task379.js
# копируется из kip8test с маппингом kipia-test-v608 → kipia-v456 /
# v609 → v457 ПОСЛЕ бампа.
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v455'"
new = "CACHE_VERSION = 'kipia-v456'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v455'
assert 'kipia-v456' not in sw, 'sw.js: v456 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v455 -> kipia-v456')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v456')
    s = s.replace('kipia-v456', 'kipia-v457')
    n_assert = s.count('kipia-v455')
    s = s.replace('kipia-v455', 'kipia-v456')
    if s != orig:
        open(f, 'w', encoding='utf-8', newline='').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v455→v456: %d, guard v456→v457: %d)' % (f, a, g))
