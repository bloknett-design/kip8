#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 380 (перенос в kip8): SW-бамп kipia-v456 → v457 (index.html
# менялся — окно «Мероприятия»: фон строк по сроку; мобайл: запрет
# выделения текста в шахматке/итогах). Порядок замен в tests/ ВАЖЕН:
# СНАЧАЛА guard-ы v457 → v458, ЗАТЕМ ассерты v456 → v457.
# test-task380.js переносится ПОСЛЕ запуска (с маппингом версий).
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v456'"
new = "CACHE_VERSION = 'kipia-v457'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v456'
assert 'kipia-v457' not in sw, 'sw.js: v457 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v456 -> kipia-v457')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v457')
    s = s.replace('kipia-v457', 'kipia-v458')
    n_assert = s.count('kipia-v456')
    s = s.replace('kipia-v456', 'kipia-v457')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v456→v457: %d, guard v457→v458: %d)' % (f, a, g))
