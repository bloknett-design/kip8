#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 344: SW-бамп kipia-v428 → v429 (kipia-v429).
# index.html изменился (восстановление после инцидента «общий вход
# kip8 ↔ kip8test») — кэш SW обязан инвалидироваться, иначе клиенты
# продолжат получать испорченный index.html из кэша v428.
# Порядок замен в tests/ ВАЖЕН: СНАЧАЛА guard-ы v429 → v430
# (чтобы старые «ложный инкремент»-guards смотрели на новую
# несуществующую версию), ЗАТЕМ ассерты v428 → v429.
# Исторические записи (worklog.md, DEPLOY-*.md, scripts/*.py) не
# переписываются. Запуск из корня репо kip8.
import glob

# 1. sw.js — CACHE_VERSION
sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v428'"
new = "CACHE_VERSION = 'kipia-v429'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v428'
assert 'kipia-v429' not in sw, 'sw.js: v429 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('sw.js: CACHE_VERSION kipia-v428 -> kipia-v429')

# 2. tests/*.js — guard v429→v430, затем ассерты v428→v429
changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v429')
    s = s.replace('kipia-v429', 'kipia-v430')
    n_assert = s.count('kipia-v428')
    s = s.replace('kipia-v428', 'kipia-v429')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v428→v429: %d, guard v429→v430: %d)' % (f, a, g))
