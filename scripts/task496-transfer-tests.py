#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 496 — перенос ТЕСТОВ из kip8test в kip8.
# 1) test-task496.js — MAP версий kipia-test-vXXX → kipia-vXXX
#    (+ голые v719/v720/v721 → v519/v520/v521 в комментариях);
# 2) бамп: СНАЧАЛА гарды kipia-v520→kipia-v521 (149), затем
#    ассерты kipia-v519→kipia-v520 (618); НОВЫЙ тест — исключён
#    (уже финальные v520/v521/v519);
# 3) восстановить комментарий 495 в run-all.js («SW kipia-v519…» —
#    задел ассерт-пассом; урок Task 495);
# 4) регистрация test-task496.js в run-all.js (ПОСЛЕ бампа — чтобы
#    комментарий 496 «SW kipia-v520» не задел гард-пасс).
import io
import glob

SRC = '/home/z/my-project/kip8test/tests/test-task496.js'
DST = '/home/z/my-project/kip8/tests/test-task496.js'
T = '/home/z/my-project/kip8/tests'
RUN_ALL = T + '/run-all.js'

# ---------- 1. Копия с MAP ----------
s = io.open(SRC, encoding='utf-8').read()
assert 'kip8test' not in s, 'в тесте есть упоминания kip8test — ручная адаптация'
s = s.replace('kipia-test-v', 'kipia-v')       # kipia-test-v720 → kipia-v520 и т.д.
s = s.replace('v719', 'v519').replace('v720', 'v520').replace('v721', 'v521')
assert "const CACHE_VERSION = 'kipia-v520';" in s
assert s.count('kipia-v521') == 1 and s.count('kipia-v519') == 1
assert s.count('v719') == 0 and s.count('v720') == 0 and s.count('v721') == 0
io.open(DST, 'w', encoding='utf-8').write(s)
print('test-task496.js скопирован с MAP (v720/v721/v719 → v520/v521/v519)')

# ---------- 2. Бамп гардов/ассертов (без нового теста) ----------
SKIP = DST
files = [f for f in sorted(glob.glob(T + '/test-*.js')) + [RUN_ALL]
         if f != SKIP]
OLD_ASSERT, NEW_ASSERT = 'kipia-v519', 'kipia-v520'
OLD_GUARD, NEW_GUARD = 'kipia-v520', 'kipia-v521'
tg = ta = touched = 0
for f in files:
    src = io.open(f, encoding='utf-8').read()
    orig = src
    ng = src.count(OLD_GUARD)
    if ng:
        src = src.replace(OLD_GUARD, NEW_GUARD); tg += ng
    na = src.count(OLD_ASSERT)
    if na:
        src = src.replace(OLD_ASSERT, NEW_ASSERT); ta += na
    if src != orig:
        io.open(f, 'w', encoding='utf-8').write(src)
        touched += 1
print('бамп: гардов v520→v521 %d (ож. 149), ассертов v519→v520 %d (ож. 618), '
      'файлов %d' % (tg, ta, touched))
assert tg == 149 and ta == 618, 'счётчики бампа не сошлись'
left = sum(io.open(f, encoding='utf-8').read().count('kipia-v519')
           for f in files)
assert left == 0, 'остался v519 в старых тестах: %d' % left

# ---------- 3. Восстановить комментарий 495 в run-all ----------
ra = io.open(RUN_ALL, encoding='utf-8').read()
bad = "// SW kipia-v520. Адаптации: 372/373 (чип), 494 (граница чанка)."
good = "// SW kipia-v519. Адаптации: 372/373 (чип), 494 (граница чанка)."
if bad in ra:
    ra = ra.replace(bad, good)
    print('комментарий 495 в run-all.js восстановлен (SW kipia-v519)')
else:
    assert good in ra, 'комментарий 495 не найден ни в каком виде'

# ---------- 4. Регистрация (после бампа) ----------
REG_OLD = "require('./test-task495.js');"
REG_NEW = ("require('./test-task495.js');\n\n"
           "// Task 496: ППР — Enter («Готово») закрывает клавиатуру:\n"
           "// enterkeyhint done + tempQueryEnterBlur (preventDefault +\n"
           "// stopPropagation + blur). SW kipia-v520. MAP kipia-test-v720\n"
           "// → kipia-v520. Границы: блок таблицы (next×2) и глобальный\n"
           "// Enter-переход — не тронуты.\n"
           "require('./test-task496.js');")
assert ra.count(REG_OLD) == 1, 'якорь регистрации 495: %d' % ra.count(REG_OLD)
assert "test-task496" not in ra
ra = ra.replace(REG_OLD, REG_NEW)
io.open(RUN_ALL, 'w', encoding='utf-8').write(ra)
print('run-all.js: test-task496.js зарегистрирован (комментарий v520)')

# ---------- Контроли ----------
new = io.open(DST, encoding='utf-8').read()
assert new.count("const CACHE_VERSION = 'kipia-v520';") == 2
assert new.count('kipia-v521') == 1 and new.count('kipia-v519') == 1
ra2 = io.open(RUN_ALL, encoding='utf-8').read()
assert "require('./test-task496.js');" in ra2
assert 'SW kipia-v519. Адаптации: 372/373' in ra2
print('Контроли: MAP-версии финальные, регистрация жива, комментарий 495 '
      'восстановлен. Всё ок.')
