#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 490-492-transfer ЧАСТЬ 2b: пост-merge патч — восстановление
# после конфликтных хунк (keep-ours сохранил СТАРЫЕ строки внутри
# группированных diff3-хунков, где имя теста + i-строка + окно
# шли подряд):
#   (1) живые i-строки v515 → v516 в 480/481/482 (5 вхождений;
#       v515 в sw.js больше нет — ассерты сломались бы);
#   (2) 481: w700 6600 → 6800 (теirs-значение, kip8 480@6474 < 6800);
#   (3) 482: каскадные мета-литералы под ФИНАЛЬНЫЕ kip8-значения:
#       s480 'i - 6600' → 'i - 6800' (окно 480 после §5.1),
#       s481 'i - 6500' → 'i - 7300' (w1400 481; theirs применился
#       чисто), ctx 481 остаётся 6600 (kip8 481@6230 > theirs 6000).
# После: node tests/run-all.js (ожидание 6128/0).
import io
import os
import sys

K8 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
T8 = os.path.join(K8, 'tests')
fail = []


def chk(cond, msg):
    if cond:
        print('OK: %s' % msg)
    else:
        fail.append(msg)
        print('FAIL: %s' % msg)


def rd(p):
    return io.open(p, encoding='utf-8').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


def rep1(path, old, new, tag, cnt=1):
    s = rd(path)
    n = s.count(old)
    if n != cnt:
        fail.append('[%s] вхождений %d, ожидалось %d' % (tag, n, cnt))
        print('FAIL [%s]: вхождений %d, ожидалось %d' % (tag, n, cnt))
        return
    wr(path, s.replace(old, new))
    print('OK [%s]' % tag)


# 1. Живые i-строки v515 → v516 (конфликтные хунки keep-ours)
for name, cnt in (('test-task480.js', 1), ('test-task481.js', 2),
                  ('test-task482.js', 2)):
    rep1(os.path.join(T8, name),
         'const CACHE_VERSION = \'kipia-v515\'',
         'const CACHE_VERSION = \'kipia-v516\'',
         '%s: i-строки v515→v516' % name, cnt)

# 2. 481: w700 6600 → 6800 (ctx остаётся 6600 — различаем по
#    имени переменной)
rep1(os.path.join(T8, 'test-task481.js'),
     'const w700 = SW_SRC.slice(Math.max(0, i - 6600), i);',
     'const w700 = SW_SRC.slice(Math.max(0, i - 6800), i);',
     '481: w700 6600→6800')

# 3. 482: каскадные мета-литералы под финальные kip8-значения
# 3a. s480: значение 6800 (= theirs) — строка становится идентичной
#     theirs (литерал + сообщение)
rep1(os.path.join(T8, 'test-task482.js'),
     "assertTrue(s480.indexOf('i - 6600') !== -1, "
     "'test-task480: окно 3200');",
     "assertTrue(s480.indexOf('i - 6800') !== -1, "
     "'test-task480: окно 6800 (Task 492)');",
     '482: мета s480 6600→6800')
# 3b. s481: ctx 6600 (kip8-геометрия) + w1400 7300
rep1(os.path.join(T8, 'test-task482.js'),
     "assertTrue(s481.indexOf('i - 6600') !== -1 &&\n"
     "                   s481.indexOf('i - 6500') !== -1,\n"
     "            'test-task481: окна 3200/4100');",
     "assertTrue(s481.indexOf('i - 6600') !== -1 &&\n"
     "                   s481.indexOf('i - 7300') !== -1,\n"
     "            'test-task481: окна 6600 (kip8-геометрия)/7300');",
     '482: мета s481 6500→7300')

# 4. Контроль: живых v515-ассертов нет (везде кроме негативов
#    новых тестов 490/491/492 — те проверяют ОТСУТСТВИЕ v515 ✓)
for f in sorted(os.listdir(T8)):
    if not (f.startswith('test-') and f.endswith('.js')):
        continue
    s = rd(os.path.join(T8, f))
    live = s.count("CACHE_VERSION = 'kipia-v515'")
    if live and f not in ('test-task490.js', 'test-task491.js',
                          'test-task492.js'):
        fail.append('%s: живой v515-ассерт ×%d' % (f, live))
        print('FAIL: %s: живой v515-ассерт ×%d' % (f, live))
chk(not fail, 'живых v515-ассертов нет (негативы 490/491/492 — легитимны)')

print('\n===== ЧАСТЬ 2b ЗАВЕРШЕНА: %d FAIL =====' % len(fail))
for m in fail:
    print('FAIL: %s' % m)
if fail:
    sys.exit(1)
print('Дальше: node tests/run-all.js (ожидание 6128/0)')
