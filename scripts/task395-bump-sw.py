#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 395: SW-бамп kipia-v470 → v471 (боевой kip8; index.html
# менялся — кнопка «Работники» по матрице доступа, фон/рамки блоков
# карточек, десктоп-колонки: отпуска под профилем, мероприятия под
# отпусками, СИЗ в верхней правой части).
# Порядок замен в tests/ ВАЖЕН (конвенция прежних бампов):
#   СНАЧАЛА v471 → v472 — ВСЕ guard-ы «отсутствует» переезжают на
#   новую несуществующую v472;
#   ЗАТЕМ v470 → v471 — ассерты «присутствует» едут на текущую.
# ВНИМАНИЕ: test-task395.js НЕ исключаем — его SW-тест перенесён в
# «до-бамп» форме (ассерт v470 + guard v471) двухшаговой заменой
# (guard v471→v472, ассерт v470→v471) приходит в каноническую форму.
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v470'"
new = "CACHE_VERSION = 'kipia-v471'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v470'
assert 'kipia-v471' not in sw, 'sw.js: v471 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v470 -> kipia-v471')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    # 1) guards «v471 отсутствует» → «v472 отсутствует» (все формы)
    n_guard = s.count('kipia-v471')
    s = s.replace('kipia-v471', 'kipia-v472')
    # 2) ассерты «v470 присутствует» → «v471 присутствует»
    n_assert = s.count('kipia-v470')
    s = s.replace('kipia-v470', 'kipia-v471')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v470->v471: %d, guard v471->v472: %d)' % (f, a, g))
