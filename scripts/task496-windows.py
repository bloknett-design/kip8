#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 496 — kip8: окна истории sw.js в тестах ПЕРЕНОСА.

Комментарий Task 496 (4 строки, ~249 симв. перед CACHE_VERSION)
отодвинул ВСЕ якоря на +249 (замер scripts/task496-windows-diag.js,
iConst=30853):

  461 12526 (12400 — вылет) | 471 10073 (10600 ✓) | 472 9521
  (9300 — вылет; LIMITS 9900 ✓) | 473 9146 (9000 — вылет) | 474
  9012 (9000 — вылет на 12; LIMITS 8800 — вылет) | 478 7950
  (8400 ✓) | 479 7370 ✓ | 480 7356 (7200 — вылет) | 481 7112
  (7000 — вылет; «золотистого для ТО»@6936, «ГОД»@7045) | 482:
  маркёры до _barExpMaxH@6706 (6600 — вылет), 481/480 (7200 —
  вылет, «Перечень КИП ИОС рабочий»@7321) | 483 5998 (5800 —
  вылет) | 484 6093 (5900 — вылет) | 485 5659 (5500 — вылет) |
  486 4917 (4800 — вылет) | Task 495 504, Task 496 246 ✓.

Расширения (запас 380-740):
  461: 12400 → 13200 | 472: 9300 → 9900 | 473: 9000 → 9700 |
  474: 9000 → 9700 | 480: 7200 → 8100 | 481: собств. 7000 → 7500,
  w700 7200 → 8100 | 482: собств. 6600 → 7400, 481/480 7200 → 8100
  | 483: 5800 → 6700 | 484: 5900 → 6700 | 485: 5500 → 6300 |
  486: 4800 → 5600.
  LIMITS: (i - i461) < 12400 → < 13200 (×7: 474, 476-479, 481, 482);
  (i - i474) < 8800 → < 9600 (×6: 476-479, 481, 482).

КАСКАДЫ (тесты читают литералы окон ДРУГИХ тестов):
  481: s461 'i - 12400' → 'i - 13200'; s472 'i - 9300' →
       'i - 9900'; s474 'i - 9000' → 'i - 9700';
  475: те же три значения (s461/s472/s474);
  482: s480 'i - 7200' → 'i - 8100' (совпадает с own-окном —
       замена по всему файлу ×2); s481 'i - 7000' → 'i - 7500';
  486: s475 "'i - 12400'" → "'i - 13200'"; s481 "'i - 9000'" →
       "'i - 9700'"; s484 'i - 5900' → 'i - 6700'.
  (s471 'i - 10600', s478/s479/s482 'i - 8400' — живы.)
"""
import io

T = '/home/z/my-project/kip8/tests'
OK = True


def rep(fname, old, new, cnt=1):
    global OK
    p = T + '/' + fname
    src = io.open(p, encoding='utf-8').read()
    n = src.count(old)
    if n != cnt:
        if n == 0 and src.count(new) == cnt:
            print('  %-18s (уже применено) %r' % (fname, old[:40]))
            return
        print('FAIL %s: %r найдено %d (ожидалось %d)' %
              (fname, old[:56], n, cnt))
        OK = False
        return
    src = src.replace(old, new)
    io.open(p, 'w', encoding='utf-8').write(src)
    print('  %-18s %r x%d' % (fname, old[:46], n))


# --- Собственные окна -----------------------------------------------
rep('test-task461.js', 'SW_SRC.slice(Math.max(0, i - 12400), i)',
    'SW_SRC.slice(Math.max(0, i - 13200), i)')
rep('test-task472.js', 'SW_SRC.slice(Math.max(0, i - 9300), i)',
    'SW_SRC.slice(Math.max(0, i - 9900), i)')
rep('test-task473.js', 'SW_SRC.slice(Math.max(0, i - 9000), i)',
    'SW_SRC.slice(Math.max(0, i - 9700), i)')
rep('test-task474.js', 'SW_SRC.slice(Math.max(0, i - 9000), i)',
    'SW_SRC.slice(Math.max(0, i - 9700), i)')
rep('test-task480.js', 'SW_SRC.slice(Math.max(0, i - 7200), i)',
    'SW_SRC.slice(Math.max(0, i - 8100), i)')
rep('test-task481.js', 'SW_SRC.slice(Math.max(0, i - 7000), i)',
    'SW_SRC.slice(Math.max(0, i - 7500), i)')
rep('test-task481.js', 'SW_SRC.slice(Math.max(0, i - 7200), i)',
    'SW_SRC.slice(Math.max(0, i - 8100), i)')
rep('test-task482.js', 'SW_SRC.slice(Math.max(0, i - 6600), i)',
    'SW_SRC.slice(Math.max(0, i - 7400), i)')
rep('test-task482.js', 'SW_SRC.slice(Math.max(0, i - 7200), i)',
    'SW_SRC.slice(Math.max(0, i - 8100), i)')
rep('test-task483.js', 'SW_SRC.slice(Math.max(0, i - 5800), i)',
    'SW_SRC.slice(Math.max(0, i - 6700), i)')
rep('test-task484.js', 'SW_SRC.slice(Math.max(0, i - 5900), i)',
    'SW_SRC.slice(Math.max(0, i - 6700), i)')
rep('test-task485.js', 'SW_SRC.slice(Math.max(0, i - 5500), i)',
    'SW_SRC.slice(Math.max(0, i - 6300), i)')
rep('test-task486.js', 'SW_SRC.slice(Math.max(0, i - 4800), i)',
    'SW_SRC.slice(Math.max(0, i - 5600), i)')

# --- LIMITS ----------------------------------------------------------
for f in ['test-task474.js', 'test-task476.js', 'test-task477.js',
          'test-task478.js', 'test-task479.js', 'test-task481.js',
          'test-task482.js']:
    rep(f, '(i - i461) < 12400', '(i - i461) < 13200')
for f in ['test-task476.js', 'test-task477.js', 'test-task478.js',
          'test-task479.js', 'test-task481.js', 'test-task482.js']:
    rep(f, '(i - i474) < 8800', '(i - i474) < 9600')

# --- Каскады ---------------------------------------------------------
rep('test-task481.js', "s461.indexOf('i - 12400')", "s461.indexOf('i - 13200')")
rep('test-task481.js', "s472.indexOf('i - 9300')", "s472.indexOf('i - 9900')")
rep('test-task481.js', "s474.indexOf('i - 9000')", "s474.indexOf('i - 9700')")
rep('test-task475.js', "s.indexOf('i - 12400')", "s.indexOf('i - 13200')")
rep('test-task475.js', "s.indexOf('i - 9300')", "s.indexOf('i - 9900')")
rep('test-task475.js', "s.indexOf('i - 9000')", "s.indexOf('i - 9700')")
# 482: 'i - 7200' в 482 — и слайс, и каскад s480 (обе → 8100)
rep('test-task482.js', "s480.indexOf('i - 7200')", "s480.indexOf('i - 8100')")
rep('test-task482.js', "s481.indexOf('i - 7000')", "s481.indexOf('i - 7500')")
# в test-task486.js кавычки ВНУТРИ двойных — простые: s475.indexOf("'i - …'")
rep('test-task486.js', "s475.indexOf(\"'i - 12400'\")",
    "s475.indexOf(\"'i - 13200'\")")
rep('test-task486.js', "s481.indexOf(\"'i - 9000'\")",
    "s481.indexOf(\"'i - 9700'\")")
rep('test-task486.js', "s484.indexOf('i - 5900')", "s484.indexOf('i - 6700')")

print('---')
print('ВСЁ ОК' if OK else 'ЕСТЬ ОШИБКИ')
raise SystemExit(0 if OK else 1)
