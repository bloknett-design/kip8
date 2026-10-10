#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 494 (kip8) — окна истории sw.js: комментарий Task 494 (3 строки,
~190 симв. перед CACHE_VERSION) отодвинул якоря; фактические дистанции
(kip8-геометрия): 486@4410, 485@5152, 483@5491, 484@5586, 481@6605,
480@6849, 479@6863, 478@7443 — 11 ассертов за окнами (перебор 5-143).
Расширения (запас ~400):
  7300 → 7700 (478, 479, 481-w1400, 482)
  6800 → 7200 (480, 481-w700, 482-481/480)
  6600 → 7000 (481-комментарий; 482-482 НЕ трогаем — там запас)
  5400 → 5800 (483), 5500 → 5900 (484), 5100 → 5500 (485),
  4400 → 4800 (486)
Якоря 474/472/471/461 (8505/9014/9566/12019) — в окнах 8800/9100/
9800/12400, расширений не требуют.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(ROOT, 'tests')

REPL = [
    ('test-task478.js', 'i - 7300', 'i - 7700'),
    ('test-task479.js', 'i - 7300', 'i - 7700'),
    ('test-task480.js', 'i - 6800', 'i - 7200'),
    ('test-task481.js', 'i - 6600', 'i - 7000'),
    ('test-task481.js', 'i - 6800', 'i - 7200'),
    ('test-task481.js', 'i - 7300', 'i - 7700'),
    ('test-task482.js', 'i - 6800', 'i - 7200'),
    ('test-task482.js', 'i - 7300', 'i - 7700'),
    ('test-task483.js', 'i - 5400', 'i - 5800'),
    ('test-task484.js', 'i - 5500', 'i - 5900'),
    ('test-task485.js', 'i - 5100', 'i - 5500'),
    ('test-task486.js', 'i - 4400', 'i - 4800'),
]

ok = True
for fn, old, new in REPL:
    p = os.path.join(TESTS, fn)
    with io.open(p, encoding='utf-8') as f:
        src = f.read()
    n = src.count('Math.max(0, %s)' % old)
    if n != 1:
        print('FAIL %s: %r найдено %d, ожидалось 1' % (fn, old, n))
        ok = False
        continue
    src = src.replace('Math.max(0, %s)' % old, 'Math.max(0, %s)' % new, 1)
    with io.open(p, 'w', encoding='utf-8') as f:
        f.write(src)
    print('OK   %s: %s → %s' % (fn, old.replace('i - ', ''), new.replace('i - ', '')))

print('RESULT: %s' % ('OK' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
