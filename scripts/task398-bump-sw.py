#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 398: SW-бамп kip8 v473 → v474 (index.html менялся —
# универсальное правило [hidden]{display:none!important}: атрибут
# hidden вновь сильнее авторских display-правил; заявка — кнопка
# «Работники» в табеле видна роли КИП ИОС при уровне min).
# Порядок замен в tests/ ВАЖЕН (конвенция прежних бампов):
#   СНАЧАЛА v474 → v475 — ВСЕ guard-ы «отсутствует» переезжают на
#   новую несуществующую v475;
#   ЗАТЕМ v473 → v474 — ассерты «присутствует» едут на текущую.
# tests/test-task398.js — НЕ исключён: перенесён в «до-бамп» форме
# (assert v473 + guard v474) — двухшаговый бамп канонизирует его
# (assert v474 + guard v475), паттерн task395/397.
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v473'"
new = "CACHE_VERSION = 'kipia-v474'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v473'
assert 'kipia-v474' not in sw, 'sw.js: v474 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v473 -> kipia-v474')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    # 1) guards «v474 отсутствует» → «v475 отсутствует» (все формы)
    n_guard = s.count('kipia-v474')
    s = s.replace('kipia-v474', 'kipia-v475')
    # 2) ассерты «v473 присутствует» → «v474 присутствует»
    n_assert = s.count('kipia-v473')
    s = s.replace('kipia-v473', 'kipia-v474')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v473->v474: %d, guard v474->v475: %d)' % (f, a, g))
