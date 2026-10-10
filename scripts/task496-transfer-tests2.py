#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 496 — перенос ТЕСТОВ, шаг 2 (после бампа, который уже применён):
#   1) восстановить в run-all.js ТРИ исторических комментария
#      (493 «SW kipia-v519 (MAP из kip8test v717)», 494 «SW kipia-v519
#      (MAP из kip8test v718)», 495 «SW kipia-v519. Адаптации…») —
#      ассерт-пасс v519→v520 переписал их (урок Task 495: комментарии
#      истории восстанавливаются);
#   2) зарегистрировать test-task496.js (комментарий — уже v520,
#      бампов больше не будет);
#   3) контроли.
# (task496-transfer-tests.py выполнил: копию с MAP, бамп гардов
#  v520→v521 ×149 и ассертов v519→v520 ×621 = 618 тестов + 3
#  комментария run-all.)
import io

RUN_ALL = '/home/z/my-project/kip8/tests/run-all.js'
ra = io.open(RUN_ALL, encoding='utf-8').read()

# ---------- 1. Восстановление исторических комментариев ----------
pairs = [
    ("// полные имена. SW kipia-v520 (MAP из kip8test v717).",
     "// полные имена. SW kipia-v519 (MAP из kip8test v717)."),
    ("// SW kipia-v520 (MAP из kip8test v718).",
     "// SW kipia-v519 (MAP из kip8test v718)."),
    ("// SW kipia-v520. Адаптации: 372/373 (чип), 494 (граница чанка).",
     "// SW kipia-v519. Адаптации: 372/373 (чип), 494 (граница чанка)."),
]
for bad, good in pairs:
    assert ra.count(bad) == 1, 'не найден: %r (%d)' % (bad, ra.count(bad))
    ra = ra.replace(bad, good)
print('run-all.js: 3 исторических комментария (493/494/495) восстановлены '
      '(SW kipia-v519)')

# ---------- 2. Регистрация 496 ----------
REG_OLD = "require('./test-task495.js');"
REG_NEW = ("require('./test-task495.js');\n\n"
           "// Task 496 (ПЕРЕНОС из kip8test@a3006907): ППР — Enter\n"
           "// («Готово») закрывает клавиатуру, не перескакивает:\n"
           "// enterkeyhint done + tempQueryEnterBlur (preventDefault +\n"
           "// stopPropagation + blur). SW kipia-v520. MAP kipia-test-v720\n"
           "// → kipia-v520. Границы: блок таблицы (next×2) и глобальный\n"
           "// Enter-переход — не тронуты.\n"
           "require('./test-task496.js');")
assert ra.count(REG_OLD) == 1
assert "test-task496" not in ra
ra = ra.replace(REG_OLD, REG_NEW)
io.open(RUN_ALL, 'w', encoding='utf-8').write(ra)
print('run-all.js: test-task496.js зарегистрирован (комментарий SW kipia-v520)')

# ---------- 3. Контроли ----------
ra2 = io.open(RUN_ALL, encoding='utf-8').read()
assert ra2.count('kipia-v520') == 2  # комментарий 496: SW + MAP (упоминается дважды)
assert ra2.count('kipia-v519') == 3  # исторические 493/494/495
assert ra2.count('kipia-v521') == 0
assert "require('./test-task496.js');" in ra2
import glob
tests_v521 = sum(io.open(f, encoding='utf-8').read().count('kipia-v521')
                 for f in glob.glob('/home/z/my-project/kip8/tests/test-*.js'))
new = io.open('/home/z/my-project/kip8/tests/test-task496.js',
              encoding='utf-8').read()
assert tests_v521 == 150  # 149 гардов + 1 в новом тесте
assert new.count("const CACHE_VERSION = 'kipia-v520';") == 2
assert new.count('kipia-v521') == 1 and new.count('kipia-v519') == 1
print('Контроли: run-all v520×1/v519×3; гарды v521×150 (149+новый); '
      'новый тест финален. Всё ок.')
