#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 494 (kip8) — бамп SW-версий в тестах kip8.

Порядок (по прецеденту task493-bump-sw.py из kip8):
  1) guards: kipia-v518 → kipia-v519 (assertFalse «следующей нет»)
  2) asserts: kipia-v517 → kipia-v518 (assertTrue «текущая»)
OWN (tests/test-task494.js) исключён — написан сразу под финальные
v518-ассерты / v519-guard (MAP из kip8test).
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(ROOT, 'tests')
OWN = 'test-task494.js'

def replace_in(path, old, new):
    with io.open(path, encoding='utf-8') as f:
        src = f.read()
    n = src.count(old)
    if n == 0:
        return True
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(src.replace(old, new))
    print('OK   %s: %d × %s → %s' % (os.path.basename(path), n, old, new))
    return True

total_g, total_a = 0, 0
files = sorted(f for f in os.listdir(TESTS)
               if f.endswith('.js') and f != OWN)
# --- 1) guards v518 → v519 ---
for fn in files:
    p = os.path.join(TESTS, fn)
    with io.open(p, encoding='utf-8') as f:
        src = f.read()
    g = src.count('kipia-v518')
    total_g += g
    if g:
        replace_in(p, 'kipia-v518', 'kipia-v519')
# --- 2) asserts v517 → v518 ---
for fn in files:
    p = os.path.join(TESTS, fn)
    with io.open(p, encoding='utf-8') as f:
        src = f.read()
    a = src.count('kipia-v517')
    total_a += a
    if a:
        replace_in(p, 'kipia-v517', 'kipia-v518')
print('GUARDS v518→v519: %d, ASSERTS v517→v518: %d (OWN %s исключён)'
      % (total_g, total_a, OWN))
sys.exit(0)
