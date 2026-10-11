#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 499 (kip8): бамп версии SW в тестах + перенос test-task499.js.

sw.js уже kipia-v523. Порядок: СНАЧАЛА гарды v523→v524, затем ассерты
v522→v523. Замер: v522 в тестах kip8 = 633 (632 в test-*.js + 1
истор. комментарий регистрации 498 в run-all.js — КАМЕНЬ из 498:
после бампа ВОССТАНОВИТЬ к v522); v523 = 153 (гарды).

test-task499.js копируется ИЗ kip8test@44f1e3f0 с MAP:
  kipia-test-v723 → kipia-v523 (ассерты), kipia-test-v724 → kipia-v524
  (гард); шапка «D. SW kipia-test-v723 (guard v724)» → v523/v524.
Регистрация в run-all.js — ПОСЛЕ бампа.
"""
import io
import glob

T = '/home/z/my-project/kip8/tests'
SRC = '/home/z/my-project/kip8test/tests/test-task499.js'

# ---- (1) бамп ----
files = sorted(glob.glob(T + '/test-*.js')) + [T + '/run-all.js']
OLD_ASSERT = 'kipia-v522'
NEW_ASSERT = 'kipia-v523'
OLD_GUARD = 'kipia-v523'
NEW_GUARD = 'kipia-v524'

total_guard = total_assert = 0
for f in files:
    s = io.open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count(OLD_GUARD)
    if n_guard:
        s = s.replace(OLD_GUARD, NEW_GUARD)
        total_guard += n_guard
    n_assert = s.count(OLD_ASSERT)
    if n_assert:
        s = s.replace(OLD_ASSERT, NEW_ASSERT)
        total_assert += n_assert
    if s != orig:
        io.open(f, 'w', encoding='utf-8').write(s)

print('Гардов v523→v524: %d' % total_guard)
print('Ассертов v522→v523: %d' % total_assert)
assert total_guard == 153, 'гардов %d ≠ 153' % total_guard
assert total_assert == 633, 'ассертов %d ≠ 633' % total_assert

left = 0
for f in files:
    left += io.open(f, encoding='utf-8').read().count('kipia-v522')
assert left == 1, 'осталось v522: %d (ожидание: 1 — истор. run-all)' % left
print('Контроль: v522 остался только в run-all (истор. комментарий).')

# ---- (2) восстановление истор. комментария 498 в run-all ----
f = T + '/run-all.js'
s = io.open(f, encoding='utf-8').read()
old_hist = '// SW kipia-v523 (MAP kipia-test-v722).'
assert s.count(old_hist) == 1, 'истор. комментарий 498 не найден'
s = s.replace(old_hist, '// SW kipia-v522 (MAP kipia-test-v722).')
io.open(f, 'w', encoding='utf-8').write(s)
print('run-all.js: истор. комментарий 498 восстановлен (v522/v722).')

# ---- (3) копирование нового теста с MAP ----
s = io.open(SRC, encoding='utf-8').read()
assert s.count('kipia-test-v723') >= 3, 'исходник v723?'
assert s.count('kipia-test-v724') == 1, 'гард v724?'
s = s.replace('kipia-test-v724', 'kipia-v524')
s = s.replace('kipia-test-v723', 'kipia-v523')
s = s.replace('//   D. SW kipia-test-v723 (guard v724).',
              '//   D. SW kipia-v523 (guard v524).')
io.open(T + '/test-task499.js', 'w', encoding='utf-8').write(s)
print('test-task499.js скопирован с MAP (v523/v524).')

# ---- (4) регистрация в run-all ----
f = T + '/run-all.js'
s = io.open(f, encoding='utf-8').read()
old = "require('./test-task498.js');"
assert s.count(old) == 1
s = s.replace(old, old + "\nrequire('./test-task499.js');\n// SW kipia-v523 (MAP kipia-test-v723).")
io.open(f, 'w', encoding='utf-8').write(s)
print('run-all.js: зарегистрирован test-task499.js.')
