#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 346 (перенос в kip8): SW-бамп kipia-v429 → v430 (index.html
# менялся — device в verifyOTP, тост evicted, бейдж админ-панели).
# Порядок замен в tests/ ВАЖЕН: СНАЧАЛА guard-ы v430 → v431, ЗАТЕМ
# ассерты v429 → v430. Исторические записи не переписываются.
# Запуск из корня репо kip8.
import glob

# 1. sw.js — CACHE_VERSION
sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v429'"
new = "CACHE_VERSION = 'kipia-v430'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v429'
assert 'kipia-v430' not in sw, 'sw.js: v430 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v429 -> kipia-v430')

# 2. tests/*.js — guard v430→v431, затем ассерты v429→v430
changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v430')
    s = s.replace('kipia-v430', 'kipia-v431')
    n_assert = s.count('kipia-v429')
    s = s.replace('kipia-v429', 'kipia-v430')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v429→v430: %d, guard v430→v431: %d)' % (f, a, g))
