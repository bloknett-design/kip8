#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 405-406: SW-бамп kipia-v476 → v477 (боевой kip8; index.html и
# WorkSchedule.gs менялись — разделение таблицы инструктажей +
# раскладка карточки). Порядок замен в tests/ ВАЖЕН (конвенция):
#   СНАЧАЛА kipia-v477 → kipia-v478 — ВСЕ guard-ы «отсутствует»
#   (включая перенесённые из kip8test с маппингом v634→v477)
#   переезжают на новую несуществующую v478;
#   ЗАТЕМ kipia-v476 → kipia-v477 — ассерты «присутствует» едут на
#   текущую.
# Скрипт запускается из /home/z/my-project/kip8.
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v476'"
new = "CACHE_VERSION = 'kipia-v477'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v476'
assert 'kipia-v477' not in sw, 'sw.js: v477 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v476 -> kipia-v477')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    # 1) guards «v477 отсутствует» → «v478 отсутствует» (все формы)
    n_guard = s.count('kipia-v477')
    s = s.replace('kipia-v477', 'kipia-v478')
    # 2) ассерты «v476 присутствует» → «v477 присутствует»
    n_assert = s.count('kipia-v476')
    s = s.replace('kipia-v476', 'kipia-v477')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v476->v477: %d, guard v477->v478: %d)' % (f, a, g))
