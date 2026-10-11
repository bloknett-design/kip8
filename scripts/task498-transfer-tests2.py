#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 498 (kip8): бамп версии SW в тестах + перенос test-task498.js.

sw.js уже kipia-v522. Порядок: СНАЧАЛА гарды v522→v523, затем ассерты
v521→v522. Замер: v521 в тестах kip8 = 628 (626 ассертов + 2 в
run-all.js: строка регистрации 497 — комментарий становится верным
после бампа, восстановления не требует), v522 = 151 гард.

test-task498.js копируется ИЗ kip8test@7b9cadf6 с MAP:
  kipia-test-v722 → kipia-v522 (ассерты), kipia-test-v723 → kipia-v523
  (гард); шапка «D. SW kipia-test-v722 (guard v723)» → v522/v523.
Регистрация в run-all.js — ПОСЛЕ бампа.
"""
import io
import glob
import shutil

T = '/home/z/my-project/kip8/tests'
SRC = '/home/z/my-project/kip8test/tests/test-task498.js'

# ---- (1) бамп ----
files = sorted(glob.glob(T + '/test-*.js')) + [T + '/run-all.js']
OLD_ASSERT = 'kipia-v521'
NEW_ASSERT = 'kipia-v522'
OLD_GUARD = 'kipia-v522'
NEW_GUARD = 'kipia-v523'

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

print('Гардов v522→v523: %d' % total_guard)
print('Ассертов v521→v522: %d' % total_assert)
assert total_guard == 151, 'гардов %d ≠ 151' % total_guard
assert total_assert == 628, 'ассертов %d ≠ 628' % total_assert

left = 0
for f in files:
    left += io.open(f, encoding='utf-8').read().count('kipia-v521')
assert left == 0, 'остались v521: %d' % left
print('Контроль: v521 в тестах нет.')

# ---- (2) копирование нового теста с MAP ----
s = io.open(SRC, encoding='utf-8').read()
assert s.count('kipia-test-v722') >= 3, 'исходник v722?'
assert s.count('kipia-test-v723') == 1
s = s.replace('kipia-test-v723', 'kipia-v523')
s = s.replace('kipia-test-v722', 'kipia-v522')
s = s.replace('//   D. SW kipia-test-v722 (guard v723).',
              '//   D. SW kipia-v522 (guard v523).')
io.open(T + '/test-task498.js', 'w', encoding='utf-8').write(s)
print('test-task498.js скопирован с MAP (v522/v523).')

# ---- (3) регистрация в run-all ----
f = T + '/run-all.js'
s = io.open(f, encoding='utf-8').read()
old = "require('./test-task497.js');"
assert s.count(old) == 1
s = s.replace(old, old + "\nrequire('./test-task498.js');\n// SW kipia-v522 (MAP kipia-test-v722).")
io.open(f, 'w', encoding='utf-8').write(s)
print('run-all.js: зарегистрирован test-task498.js.')
