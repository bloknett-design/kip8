#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 370: SW-бамп kipia-v446 → v447 (index.html менялся — цвет
# недоставленных показаний ярче и ближе к жёлтому: #ffc400 тёмная /
# #cc9900 светлая, было #f5a623 / #c96e00; заявка пользователя внести
# сразу и в тестовый, и в боевой проекты — kip8test менялся
# синхронно).
# Порядок замен в tests/ ВАЖЕН (урок Task 361):
# СНАЧАЛА guard-ы «v447 не существует» → v448, ЗАТЕМ ассерты
# v446 → v447. Запуск из корня репо kip8.
import glob

# 1. sw.js — CACHE_VERSION
sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v446'"
new = "CACHE_VERSION = 'kipia-v447'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v446'
assert 'kipia-v447' not in sw, 'sw.js: v447 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v446 -> kipia-v447')

# 2. tests/*.js — guard v447→v448, затем ассерты v446→v447
changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v447')
    s = s.replace('kipia-v447', 'kipia-v448')
    n_assert = s.count('kipia-v446')
    s = s.replace('kipia-v446', 'kipia-v447')
    # сообщения guard-ов — под новую цель v448 (косметика)
    s = s.replace('v447 ещё не существует', 'v448 ещё не существует')
    s = s.replace('v446 ещё не существует', 'v448 ещё не существует')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v446→v447: %d, guard v447→v448: %d)' % (f, a, g))

# 3. контроль: v447 в sw.js ровно один
assert sw.count('kipia-v447') == 1
print('OK: единственный kipia-v447 в sw.js')
