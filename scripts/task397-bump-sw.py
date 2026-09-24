#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 397: SW-бамп kipia-v472 → v473 (index.html менялся —
# ОБЩЕЕ ПРАВИЛО: кнопка раздела без доступа не отображается).
# Порядок замен в tests/ ВАЖЕН (конвенция прежних бампов):
#   СНАЧАЛА v473 → v474 — ВСЕ guard-ы «отсутствует» переезжают на
#   новую несуществующую v474;
#   ЗАТЕМ v472 → v473 — ассерты «присутствует» едут на текущую.
# ВНИМАНИЕ: test-task397.js НЕ исключаем — перенесён в «до-бамп»
# форме (ассерт v472 + guard v473) — двухшаговой заменой приходит
# в каноническую форму (как task395-bump-sw.py).
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v472'"
new = "CACHE_VERSION = 'kipia-v473'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v472'
assert 'kipia-v473' not in sw, 'sw.js: v473 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v472 -> kipia-v473')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    # 1) guards «v473 отсутствует» → «v474 отсутствует» (все формы)
    n_guard = s.count('kipia-v473')
    s = s.replace('kipia-v473', 'kipia-v474')
    # 2) ассерты «v472 присутствует» → «v473 присутствует»
    n_assert = s.count('kipia-v472')
    s = s.replace('kipia-v472', 'kipia-v473')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v472->v473: %d, guard v473->v474: %d)' % (f, a, g))
