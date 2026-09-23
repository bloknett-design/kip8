#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 396: SW-бамп kip8 (боевой) kipia-v471 → v472 (перенос из
# kip8test: зебра строк блоков карточки, компактные кнопки в
# верхнем правом углу шапок блоков, оглавления крупнее/ярче +
# другой фон).
# Порядок замен в tests/ ВАЖЕН (конвенция прежних бампов):
#   СНАЧАЛА v472 → v473 — ВСЕ guard-ы «отсутствует» переезжают на
#   новую несуществующую v473;
#   ЗАТЕМ v471 → v472 — ассерты «присутствует» едут на текущую.
# tests/test-task396.js — ИСКЛЮЧЁН: скопирован transfer-скриптом
# уже в канонической пост-бамп форме (assert v472 + guard v473).
import glob

OWN = 'tests/test-task396.js'

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v471'"
new = "CACHE_VERSION = 'kipia-v472'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v471'
assert 'kipia-v472' not in sw, 'sw.js: v472 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v471 -> kipia-v472')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    if f.replace('\\', '/') == OWN:
        continue
    s = open(f, encoding='utf-8').read()
    orig = s
    # 1) guards «v472 отсутствует» → «v473 отсутствует» (все формы)
    n_guard = s.count('kipia-v472')
    s = s.replace('kipia-v472', 'kipia-v473')
    # 2) ассерты «v471 присутствует» → «v472 присутствует»
    n_assert = s.count('kipia-v471')
    s = s.replace('kipia-v471', 'kipia-v472')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v471->v472: %d, guard v472->v473: %d)' % (f, a, g))
