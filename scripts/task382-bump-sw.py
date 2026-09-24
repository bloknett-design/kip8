#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 382: SW-бамп kipia-v458 → v459 (index.html менялся — перенос из
# kip8test 811d963: мобильная страница итогов, вкладка «Месяц» —
# ИЗНАЧАЛЬНАЯ ширина столбца с фамилиями ПО ШИРИНЕ ТЕКСТА, как на
# вкладке «Год»; переменная --ws-tt-emp-w, мерит _measureTtEmpFullW).
# Порядок замен в tests/ ВАЖЕН: СНАЧАЛА guard-ы v459 → v460 (guards
# смотрят на новую несуществующую), ЗАТЕМ ассерты v458 → v459.
# Перенос тестов Task 382 (test-task382.js + адаптации 325/327/329)
# делается ОТДЕЛЬНЫМ копированием с маппингом версий.
import glob

sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v458'"
new = "CACHE_VERSION = 'kipia-v459'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v458'
assert 'kipia-v459' not in sw, 'sw.js: v459 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v458 -> kipia-v459')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v459')
    s = s.replace('kipia-v459', 'kipia-v460')
    n_assert = s.count('kipia-v458')
    s = s.replace('kipia-v458', 'kipia-v459')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v458→v459: %d, guard v459→v460: %d)' % (f, a, g))
