#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 466: обновление системного промта kip8 (post-Task 466 — перенос
# из kip8test@986db19b, SW kipia-v501→v502, клиент-only).
import io
import sys

PATH = 'Системный_промт_для_приложения_КИПиА.md'
with io.open(PATH, encoding='utf-8') as f:
    src = f.read()

CUR_MARK = '> **Версия документа:** 2026-10-03 (post-Task 465: ПЕРЕНОС из kip8test@fe34a7b1'
PREV_MARK = '> **Версия документа (предыдущая):**'

NEW_LINE3 = '> **Версия документа:** 2026-10-03 (post-Task 466: ПЕРЕНОС из kip8test@986db19b в боевой kip8 ОДНИМ инкрементом SW kipia-v501→v502 — КЛИЕНТ-ONLY, серверных шагов НЕТ; заявка: «В окне мероприятий поменяй местами значки раскрытия окна и печати мероприятий.»): КЛИЕНТ (index.html): CSS-only свап — правило #wsEventsPanel .ws-bar-exp { right: 27px } (Task 465) УДАЛЕНО (раскрытие возвращается в самый угол на базовые 2px CSS + 1px рамка окна = 3px от ВНЕШНЕГО края, как в окне норм), вместо него #wsEventsPanel .ws-bar-print { right: 27px } — печать теперь СЛЕВА (пара [печать][раскрытие], зазор 3px, 22+3+22+2px от правой грани); JS-логика НЕ ТРОНУТА (оба значка absolute внутри скроллера с общим приколом translateY(scrollTop) — порядок задаётся только CSS): размеры 22×22, _barExpSync создаёт печать только для wsEventsPanel, клик → printEventsList, диалог «Печать/Сохранить PDF/Сохранить Excel/Отмена» с предпросмотром, сброс margin-top, плашки 52/26px, окно норм — всё живо; обновлены комментарии CSS ×3 + JS ×2 (маркеры Task 466, «печать СЛЕВА от раскрытия»); sw.js: строка Task 465 «справа от раскрытия» → «слева» + комментарий Task 466 + v502. ПЕРЕНОС: scripts/task466-transfer.py (де-изоляция ×15, «дифф диффов»: репо-дифф 59 == эталону kip8test@b7504f2f↔kip8@097d9ac, дифф задач 33 идентичен; .gs не тронуты — синхронны, Code.gs kip8-версия жива); тесты kip8 5250/0 = паритет 5244 + 6 task344 (маппинг v690→v502 (510)/v691→v503 (123)/негативы партии v689→v501 (2: test-task465 + test-task466)/v687→v499 (2)/исторические; test-task344 v501→v502; run-all +466; test-task466.js ×12 + адаптация test-task465.js позиционного теста пришли из kip8test автоматически). ПОДВОДНЫЕ КАМНИ: (а) перенос-скрипт ОДНОРАЗОВЫЙ — повторный прогон на уже применённом состоянии падает на якорях v501/«справа от раскрытия» (норма: git checkout -- . + rm несопровождаемых и один прогон; первый прогон упал на сверхстрогом ассерте «слева от раскрытия == 2» — в kip8 фраза 1: комментарий Task 466 говорит «печать слева (27px)» без литеральной фразы — ассерт исправлен на == 1 + негатив «справа нет»); (б) test-task465.js в kip8: негатив партии v501 (indexOf === -1) — «версии до Task 466 нет», как и в test-task466.js — оба остаются kipia-v501 после переноса 467. SMOKE task466-smoke-k8.py 8/8 (порт 8997, ключи БЕЗ префикса: пара печать 3/28 слева + раскрытие 3/3 в углу + expBefore, зазор 3, окно норм один значок 3/3, диалог от ЛЕВОГО значка — кнопки 4 + «A4 · книжная» + wsev-sheet + инжект, Esc снимает, раскрытие в углу работает ws-bar-open, 0 JS). Браузер kip8test task466-browser-check.py 16/16 + VLM ×1 (принтер левее, шеврон у края). DEPLOY-Task466-timesheet-bar-icons-swapped.md скопирован (КЛИЕНТ-ONLY — серверных шагов НЕТ). ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 SW `kipia-v502` (guard v503), тесты 5250/0; kip8test @986db19b SW `kipia-test-v690` (guard v691), тесты 5244/0 — Task 466 выкачан в ОБОИХ репо, открытых хвостов нет; десктопы — CI-автосинк. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 467 (в обоих репо).'

if CUR_MARK not in src:
    print('ОШИБКА: не найдена строка версии post-465')
    sys.exit(1)

n_prev_before = src.count(PREV_MARK)

i3 = src.index(CUR_MARK)
i3end = src.index('\n', i3)
old_line3 = src[i3:i3end]

# (а) удалить самую старую строку «предыдущая» (при переполнении —
# логика task464: последняя prev-строка файла, включая застывший
# исторический снимок ниже активной цепочки)
if src.count(PREV_MARK) > 2:
    iprev = src.rindex(PREV_MARK)
    iprev_end = src.index('\n', iprev)
    src = src[:iprev] + src[iprev_end + 1:]

# (б) строка 3 → новая версия + «предыдущая» из старой строки 3
new_prev = PREV_MARK + ' ' + old_line3[len('> **Версия документа:** '):]
src = src[:i3] + NEW_LINE3 + '\n' + new_prev + src[i3end:]

# (в) «Текущая версия кэша» v501 → v502
old_cache = '> **Текущая версия кэша:** `kipia-v501`'
new_cache = '> **Текущая версия кэша:** `kipia-v502`'
if old_cache not in src:
    print('ОШИБКА: не найдена строка текущей версии кэша')
    sys.exit(1)
src = src.replace(old_cache, new_cache, 1)

# (г) строка «Инкрементируй» — следующие версии
old_inc = 'Формат: `kipia-test-v689` → `kipia-test-v690` (для kip8test) или `kipia-v500` → `kipia-v501` (для kip8)'
new_inc = 'Формат: `kipia-test-v690` → `kipia-test-v691` (для kip8test) или `kipia-v501` → `kipia-v502` (для kip8)'
if old_inc not in src:
    print('ОШИБКА: не найдена строка «Инкрементируй»')
    sys.exit(1)
src = src.replace(old_inc, new_inc, 1)

# (д) ожидание тестов 5238/5232 → 5250/5244
old_exp = '# Ожидается: 5238 passed, 0 failed (kip8; в kip8test — 5232 passed, 0 failed)'
new_exp = '# Ожидается: 5250 passed, 0 failed (kip8; в kip8test — 5244 passed, 0 failed)'
if old_exp not in src:
    print('ОШИБКА: не найдена строка ожидания тестов')
    sys.exit(1)
src = src.replace(old_exp, new_exp, 1)

# (е) контроль
assert src.count(NEW_LINE3) == 1
assert src.count(PREV_MARK) <= n_prev_before + 1

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(src)
print('OK: промт kip8 обновлён до post-Task 466')
print('  предыдущих строк: %d (было %d)' % (src.count(PREV_MARK), n_prev_before))
