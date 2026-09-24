#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 381 (перенос в kip8): SW-бамп kipia-v457 → v458 (index.html
# менялся — итоги: фон как до белого + зебра; значки раскрытия
# приколоты при прокрутке; мероприятия — общий фон окна). Порядок
# замен в tests/ ВАЖЕН: СНАЧАЛА guard-ы v458 → v459, ЗАТЕМ ассерты
# v457 → v458. Тесты Task 381 копируются ПОСЛЕ запуска (их ассерты
# v458/guard v459 уже актуальны).
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v457'"
new = "CACHE_VERSION = 'kipia-v458'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v457'
assert 'kipia-v458' not in sw, 'sw.js: v458 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v457 -> kipia-v458')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v458')
    s = s.replace('kipia-v458', 'kipia-v459')
    n_assert = s.count('kipia-v457')
    s = s.replace('kipia-v457', 'kipia-v458')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v457→v458: %d, guard v458→v459: %d)' % (f, a, g))
