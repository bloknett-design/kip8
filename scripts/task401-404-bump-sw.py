#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 401-404: SW-бамп kip8 kipia-v475 → v476 (перенос задач 401
# (годовая шторка итогов), 402 (тип третьей строкой + группа
# допуска), 403 («разряд»→«р.», попап без СИЗ, GAS-фикс комментария,
# ярлыки, мероприятия над СИЗ), 404 (три колонки, кнопки рядом, окно
# без отпусков)).
# Порядок замен в tests/ ВАЖЕН (конвенция прежних бампов):
#   СНАЧАЛА v476 → v477 — ВСЕ guard-ы «отсутствует» переезжают на
#   новую несуществующую v477 (включая перенесённые из kip8test —
#   они в до-бамп форме: ассерты v475 + guards v476);
#   ЗАТЕМ v475 → v476 — ассерты «присутствует» едут на текущую.
# Итог (каноническая форма): ассерты v476, guards v477.
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v475'"
new = "CACHE_VERSION = 'kipia-v476'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v475'
assert 'kipia-v476' not in sw, 'sw.js: v476 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v475 -> kipia-v476')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    # 1) guards «v476 отсутствует» → «v477 отсутствует» (все формы)
    n_guard = s.count('kipia-v476')
    s = s.replace('kipia-v476', 'kipia-v477')
    # 2) ассерты «v475 присутствует» → «v476 присутствует»
    n_assert = s.count('kipia-v475')
    s = s.replace('kipia-v475', 'kipia-v476')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
