#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 399: SW-бамп kip8 v474 → v475 (index.html менялся —
# окно мероприятий табеля у уровня «min» больше не показывает
# записи мастеров «Мастер КИПиА»: мероприятия/отпуска/СИЗ
# фильтруются признаком _isMasterKipia, как строки сетки Task 340).
# Порядок замен в tests/ ВАЖЕН (конвенция прежних бампов):
#   СНАЧАЛА v475 → v476 — ВСЕ guard-ы «отсутствует» переезжают на
#   новую несуществующую v476;
#   ЗАТЕМ v474 → v475 — ассерты «присутствует» едут на текущую.
# tests/test-task399.js — НЕ исключён: перенесён в «до-бамп» форме
# (assert v474 + guard v475) — двухшаговый бамп канонизирует его
# (assert v475 + guard v476), паттерн task395/397/398.
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v474'"
new = "CACHE_VERSION = 'kipia-v475'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v474'
assert 'kipia-v475' not in sw, 'sw.js: v475 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v474 -> kipia-v475')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    # 1) guards «v475 отсутствует» → «v476 отсутствует» (все формы)
    n_guard = s.count('kipia-v475')
    s = s.replace('kipia-v475', 'kipia-v476')
    # 2) ассерты «v474 присутствует» → «v475 присутствует»
    n_assert = s.count('kipia-v474')
    s = s.replace('kipia-v474', 'kipia-v475')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v474->v475: %d, guard v475->v476: %d)' % (f, a, g))
