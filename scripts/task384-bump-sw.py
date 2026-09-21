#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 384 (перенос из kip8test c0ed8d7 в боевой kip8): SW-бамп
# kipia-v459 → v460 (index.html менялся — карточка сотрудника стала
# центром правки: «Правка данных…», ✎/✕ у отпусков, «+ Мероприятие…»;
# шторки в режимах правки; серверные справочники updateEmployee/
# updateVacation).
# Порядок замен в tests/ ВАЖЕН (конвенция прежних бампов):
#   СНАЧАЛА v460 → v461 — ВСЕ guard-ы «отсутствует» (assertFalse/
#   assertTrue/имена тестов/сообщения) переезжают на новую
#   несуществующую v461;
#   ЗАТЕМ v459 → v460 — ассерты «присутствует» едут на текущую.
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v459'"
new = "CACHE_VERSION = 'kipia-v460'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v459'
assert 'kipia-v460' not in sw, 'sw.js: v460 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v459 -> kipia-v460')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    # 1) guards «v460 отсутствует» → «v461 отсутствует» (все формы:
    #    assertFalse/assertTrue/имена тестов/тексты сообщений)
    n_guard = s.count('kipia-v460')
    s = s.replace('kipia-v460', 'kipia-v461')
    # 2) ассерты «v459 присутствует» → «v460 присутствует»
    n_assert = s.count('kipia-v459')
    s = s.replace('kipia-v459', 'kipia-v460')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v459→v460: %d, guard v460→v461: %d)' % (f, a, g))
