#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 473-474: зеркальное обновление системного промта kip8test
# (post-Task 473-474 ПЕРЕНОС — партия выкачана в kip8@30c4339/7a2412c).
import io
import os
import sys

PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    '..', 'kip8test', 'Системный_промт_для_приложения_КИПиА.md'))
with io.open(PATH, encoding='utf-8') as f:
    src = f.read()

CUR_MARK = '> **Версия документа:** 2026-10-04 (post-Task 474; заявка:'
PREV_MARK = '> **Версия документа (предыдущая):**'

NEW_LINE3 = '> **Версия документа:** 2026-10-04 (post-Task 473-474 ПЕРЕНОС: партия Tasks 473+474 перенесена из kip8test@d9efdd0f в боевой kip8@30c4339 ОДНИМ инкрементом SW kipia-v508→v509 — команда «Перенеси изменения в боевой kip8» получена в заявке Task 474 (473 ждал «по команде» с прошлой сессии; регламент Task 441). Состав: Task 473 — график ППР «Приборы» (charts-desktop.js: корневой фикс невидимости столбцов align-items:flex-end→stretch + значение над КАЖДЫМ столбцом + правая ось 0–50 для К/П); Task 474 — карточка прибора КИП ИОС (index.html: текст Типа ×1.5 — 12→18px; «№ прибора»/«Место установки» ниже от верхней границы карточки — padding-top 2→12px). КЛИЕНТ-ONLY, серверных шагов НЕТ. Перенос: scripts/task473-474-transfer.py в kip8 (де-изоляция ×15, «дифф диффов» сходится — репо-дифф 59 == эталону kip8test@1bf83f0d↔kip8@98797f3, дифф задач 14 идентичен; charts-desktop.js на базе идентичен — простая копия; маппинг тестов v698→v509 (540)/v699→v510 (125)/негативы партии v697+v696→v508/исторические как в 472; адаптация шапки test-task474 «SW: kipia-v508 → v509» + названия v509/v508/v510; test-task344 v508→v509; run-all +473+474); тесты kip8 5467/0 = паритет 5461 + 6 task344; SMOKE task473-474-smoke-k8.py 23/23 (порт 8997: карточка 18px/12px светлая+мобайл; график 35+1 значений/столбцы видимы/правая ось; SW kipia-v509; 0 JS ×3) + VLM ×2. ТЕКУЩЕЕ СОСТОЯНИЕ: kip8test @d9efdd0f SW `kipia-test-v698` (guard v699), тесты 5461/0; kip8 @7a2412c SW `kipia-v509` (guard v510), тесты 5467/0 — партия выкачана в ОБОИХ репо, открытых хвостов нет; десктопы — CI-автосинк. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 475 (в обоих репо).'

if CUR_MARK not in src:
    print('ОШИБКА: не найдена строка версии post-474 (kip8test)')
    sys.exit(1)

n_prev_before = src.count(PREV_MARK)

i3 = src.index(CUR_MARK)
i3end = src.index('\n', i3)
old_line3 = src[i3:i3end]

# (а) удалить самую старую строку «предыдущая» (храним 2 последних)
if src.count(PREV_MARK) > 2:
    iprev = src.rindex(PREV_MARK)
    iprev_end = src.index('\n', iprev)
    src = src[:iprev] + src[iprev_end + 1:]

# (б) строка 3 → новая версия + «предыдущая» из старой строки 3
new_prev = PREV_MARK + ' ' + old_line3[len('> **Версия документа:** '):]
src = src[:i3] + NEW_LINE3 + '\n' + new_prev + src[i3end:]

# (в) ожидание тестов: kip8 5399 → 5467 (перенос партии)
old_exp = '# Ожидается: 5461 passed, 0 failed (kip8test; в kip8 — 5399 passed, 0 failed)'
new_exp = '# Ожидается: 5461 passed, 0 failed (kip8test; в kip8 — 5467 passed, 0 failed)'
if old_exp not in src:
    print('ОШИБКА: не найдена строка ожидания тестов (kip8test)')
    sys.exit(1)
src = src.replace(old_exp, new_exp, 1)

# проверки
checks = [
    ('post-Task 473-474 ПЕРЕНОС', 1),
    ('Версия документа (предыдущая):** 2026-10-04 (post-Task 474; заявка:', 1),
    ('5461 passed, 0 failed (kip8test', 1),
    ('5467 passed, 0 failed', None),
    ('kipia-test-v698', None),
    ('СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 475', None),
]
for marker, cnt in checks:
    c = src.count(marker)
    if cnt is not None and c != cnt:
        print('ОШИБКА: маркер %r найден %d раз (ожидалось %s)' % (marker[:60], c, cnt))
        sys.exit(1)
    if cnt is None and c == 0:
        print('ОШИБКА: маркер не найден: %r' % marker[:60])
        sys.exit(1)
if src.count(PREV_MARK) != n_prev_before:
    print('ОШИБКА: длина цепочки «предыдущих» изменилась (%d → %d)' %
          (n_prev_before, src.count(PREV_MARK)))
    sys.exit(1)

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(src)
print('промт kip8test: post-473-474 ПЕРЕНОС записан (кэш v698, тесты '
      '5461/0 + kip8 5467/0, следующий 475)')
