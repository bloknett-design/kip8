#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 555 — бамп SW-версии в kip8 (v560→v561), по образцу
task554-bump-sw-kip8.py (урок Task 529: гварды «следующей версии
нет» двигаются ПЕРВЫМИ, до ассертов — иначе v561 окажется и в
гвардах, и в ассертах, и разделить их будет нельзя):
  1) ГВАРДЫ 'kipia-v561' → 'kipia-v562' — во всех тестах, КРОМЕ
     НОВОГО test-task555.js (его позитивный ассерт v561 — целевая
     версия, двигать нельзя);
  2) АССЕРТЫ 'kipia-v560' → 'kipia-v561' — во всех тестах, кроме
     нового (в нём v560 нет);
  3) sw.js: CACHE_VERSION v560 → v561 (index.html менялся:
     Task 555 — краткое наименование пункта «Список_И_и_ПЗ» в
     начале строк инструктажей/ПЗ карточек работников + снятие
     затухания выполненных строк).
  УРОК Task 551: НЕ добавлять ревизию-комментарий в шапку sw.js —
  «окна истории версий» (Tasks 461–501) замеряются от CACHE_VERSION
  назад; шапку не трогаем.
"""
import io
import os

ROOT = '/home/z/my-project/kip8'
OWN = ['test-task555.js']
CUR = 'kipia-v560'    # текущая версия (до бампа)
NEW = 'kipia-v561'    # целевая версия Task 555
NXT = 'kipia-v562'    # следующая (гварды)

changed = {}

# Шаг 0 — ГВАРДЫ от повторного применения / кривого состояния
sw_path = os.path.join(ROOT, 'sw.js')
sw_src = io.open(sw_path, encoding='utf-8').read()
if sw_src.count("const CACHE_VERSION = '" + NEW + "'") != 0:
    print('  FAIL: %s уже в sw.js — скрипт уже применялся' % NEW)
    raise SystemExit(1)
if sw_src.count("const CACHE_VERSION = '" + CUR + "'") != 1:
    print('  FAIL: CACHE_VERSION %s найден %d раз' %
          (CUR, sw_src.count("const CACHE_VERSION = '" + CUR + "'")))
    raise SystemExit(1)


def bump(path, old, new, label):
    src = io.open(path, encoding='utf-8').read()
    n = src.count(old)
    if n == 0:
        return
    src = src.replace(old, new)
    io.open(path, 'w', encoding='utf-8').write(src)
    changed[os.path.basename(path)] = changed.get(
        os.path.basename(path), 0) + n
    print('  %s: %s ×%d' % (os.path.basename(path), label, n))


tests_dir = os.path.join(ROOT, 'tests')
files = sorted(f for f in os.listdir(tests_dir) if f.endswith('.js'))

print('Шаг 1 — ГВАРДЫ %s → %s (кроме НОВОГО %s):' % (NEW, NXT, OWN))
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), NEW, NXT, 'гард')

print('Шаг 2 — АССЕРТЫ %s → %s (кроме НОВОГО):' % (CUR, NEW))
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), CUR, NEW, 'ассерт')

print('Шаг 3 — sw.js CACHE_VERSION:')
n = sw_src.count(CUR)
sw_src = sw_src.replace(CUR, NEW)
io.open(sw_path, 'w', encoding='utf-8').write(sw_src)
changed['sw.js'] = changed.get('sw.js', 0) + n
print('  sw.js: v560 → v561 ×%d' % n)

print('\nИтого замен: %d в %d файлах' %
      (sum(changed.values()), len(changed)))
