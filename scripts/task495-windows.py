#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 495 — kip8: окна истории sw.js в тестах ПЕРЕНОСА.

Комментарий Task 495 (~287 симв. перед CACHE_VERSION) отодвинул якоря
(замер scripts/task495-windows-diag.js, iConst=30604, для 471/472 —
iVstr=30627, +23):

  461 12277 (12400 ✓) | 471 9824/9847 (9800 — вылетело) | 472
  9272/9295 (9300 ✓ впритык-5, 9100 в LIMITS — вылетело) | 473
  8897 (9000 ✓) | 474 8763 (8800/9000 ✓) | 478 7701 (7700 —
  вылетело на 1!) | 479 7121 ✓ (но нужен 478@7701 в том же окне) |
  480 7107 (7200 ✓) | 481 6863 (7000 ✓; w700 7200 ✓; w1400 7700
  — нужен 478@7701, вылетело) | 482 3884 (6600 ✓) + Task 481/480
  в 7200 ✓, w7700 — нужен 478@7701 (вылетело) | 483 5749 (5800 ✓) |
  484 5844 (5900 ✓) | 485 5410 (5500 ✓) | 486 4668 (4800 ✓) |
  488 3450 (3200 — вылетело) | 493/494/495 (900 ✓).

Расширения (только упавшие, запас 550-760):
  471 own: 9800 → 10600 | 472 ctx471: 9800 → 10600 |
  478/479 own: 7700 → 8400 | 481 w1400: 7700 → 8400 |
  482 w7700: 7700 → 8400 | 488 own: 3200 → 4100 |
  LIMITS 472-строка: 9100 → 9900 (×6: 476-479, 481, 482);
  LIMITS 471-строка: 9800 → 10600 (×7: 474, 476-479, 481, 482).

КАСКАДЫ: 475 (s471/s472-ctx 'i - 9800' → 'i - 10600'), 481 (s471),
  482 (s478/s479/s481 'i - 7700' → 'i - 8400'), 486 (s482 quoted
  "'i - 7700'" → "'i - 8400'"); s461 12400 / s472 9300 / s474 9000 /
  s480 7200 / s484 5900 — живы (окна не менялись).
"""
import io
import sys

T = '/home/z/my-project/kip8/tests'
OK = True


def rep(fname, old, new, cnt=1):
    global OK
    p = T + '/' + fname
    src = io.open(p, encoding='utf-8').read()
    n = src.count(old)
    if n != cnt:
        print('FAIL %s: %r найдено %d (ожидалось %d)' %
              (fname, old[:56], n, cnt))
        OK = False
        return
    src = src.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(src)
    print('  %-18s %r x%d' % (fname, old[:46], n))


L472 = ('(i - i472) < 9100', '(i - i472) < 9900')
L471 = ('(i - i471) < 9800', '(i - i471) < 10600')

# --- Собственные окна -----------------------------------------------
rep('test-task471.js', 'SW_SRC.slice(Math.max(0, i - 9800), i)',
    'SW_SRC.slice(Math.max(0, i - 10600), i)')
rep('test-task472.js', 'SW_SRC.slice(Math.max(0, i - 9800), i)',
    'SW_SRC.slice(Math.max(0, i - 10600), i)')  # ctx471; own 9300 жив
rep('test-task478.js', 'SW_SRC.slice(Math.max(0, i - 7700), i)',
    'SW_SRC.slice(Math.max(0, i - 8400), i)')
rep('test-task479.js', 'SW_SRC.slice(Math.max(0, i - 7700), i)',
    'SW_SRC.slice(Math.max(0, i - 8400), i)')
rep('test-task481.js', 'const w1400 = SW_SRC.slice(Math.max(0, i - 7700), i);',
    'const w1400 = SW_SRC.slice(Math.max(0, i - 8400), i);')
rep('test-task482.js', 'SW_SRC.slice(Math.max(0, i - 7700), i)',
    'SW_SRC.slice(Math.max(0, i - 8400), i)')  # w7700; 6600/7200 живы
rep('test-task488.js', 'SW_SRC.slice(Math.max(0, i - 3200), i)',
    'SW_SRC.slice(Math.max(0, i - 4100), i)')

# --- LIMITS-строки ----------------------------------------------------
for f in ['test-task476.js', 'test-task477.js', 'test-task478.js',
          'test-task479.js', 'test-task481.js', 'test-task482.js']:
    rep(f, L472[0], L472[1])
for f in ['test-task474.js', 'test-task476.js', 'test-task477.js',
          'test-task478.js', 'test-task479.js', 'test-task481.js',
          'test-task482.js']:
    rep(f, L471[0], L471[1])

# --- Каскады -----------------------------------------------------------
rep('test-task475.js',
    "assertTrue(s1.indexOf('i - 9800') !== -1, 'test-task471: 9800 (Task 491)');",
    "assertTrue(s1.indexOf('i - 10600') !== -1, 'test-task471: 10600 (Task 495)');")
rep('test-task475.js',
    "assertTrue(s2.indexOf('i - 9800') !== -1, 'test-task472: 9800 (Task 491)');",
    "assertTrue(s2.indexOf('i - 10600') !== -1, 'test-task472: 10600 (Task 495)');")
rep('test-task481.js',
    "assertTrue(s471.indexOf('i - 9800') !== -1, 'test-task471: окно 9800 (Task 491)');",
    "assertTrue(s471.indexOf('i - 10600') !== -1, 'test-task471: окно 10600 (Task 495)');")
rep('test-task482.js',
    "assertTrue(s478.indexOf('i - 7700') !== -1, 'test-task478: окно 7700 (Task 494)');",
    "assertTrue(s478.indexOf('i - 8400') !== -1, 'test-task478: окно 8400 (Task 495)');")
rep('test-task482.js',
    "assertTrue(s479.indexOf('i - 7700') !== -1, 'test-task479: окно 7700 (Task 494)');",
    "assertTrue(s479.indexOf('i - 8400') !== -1, 'test-task479: окно 8400 (Task 495)');")
rep('test-task482.js',
    "                   s481.indexOf('i - 7700') !== -1,",
    "                   s481.indexOf('i - 8400') !== -1,")
rep('test-task486.js',
    'assertTrue(s482.indexOf("\'i - 7700\'") !== -1, \'каскад 482: 478/479 → 7700 (Task 494)\');',
    'assertTrue(s482.indexOf("\'i - 8400\'") !== -1, \'каскад 482: 478/479 → 8400 (Task 495)\');')

print('RESULT: %s' % ('OK' if OK else 'FAIL'))
sys.exit(0 if OK else 1)
