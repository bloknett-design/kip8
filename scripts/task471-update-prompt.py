#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 471: обновление системного промта kip8 (post-Task 471 ПЕРЕНОС).
import io
import sys

PATH = 'Системный_промт_для_приложения_КИПиА.md'
with io.open(PATH, encoding='utf-8') as f:
    src = f.read()

CUR_MARK = '> **Версия документа:** 2026-10-03 (post-Task 470: ПЕРЕНОС'
PREV_MARK = '> **Версия документа (предыдущая):**'

NEW_LINE3 = '> **Версия документа:** 2026-10-03 (post-Task 471: ПЕРЕНОС из kip8test@bb893f60 — «Плановые мероприятия» по заявке: кнопка просмотра предыдущих годов СЛЕВА от «2026 год» в шапке (активна только при наличии архива за предыдущие годы — planEvents.years; клик — к ближайшему младшему году архива, при исчерпании возврат к текущему), месяцы шапки кликабельны и задают месяц правого окна (подсветка pe-mo-sel + синхронизация с мобайл-селектором Task 464), правое окно ДИНАМИЧНОЕ: «Работы на следующий месяц» — интерфейс ввода работ (поле + «Добавить» + «×»; декабрь → январь следующего года), «Работы на месяц» — перечень работ месяца с отметкой полного/частичного выполнения или невыполнения (planWorks.setStatus, дата сегодня, цветные бейджи), «Мероприятия» (шапка) — снова описание Task 469; отметки/год/месяц из DOM (год payload теперь this._viewYear); ВПЕРВЫЕ с Task 467 СЕРВЕР ТОЖЕ ПЕРЕНЕСЁН: PlanEvents.gs (+planEvents.years +planWorks.list/add/remove/setStatus, лист «Работы на месяц» 8 колонок: id/год/месяц/работа/статус/дата_статуса/email/время_изменения, SRV_VER 471), НОВЫЙ PlanWorksInit.gs (planWorksDeploy — создать лист, идемпотентен), Code.gs kip8-версия +5 case (набор case синхронен с эталоном, порядок исторически свой — Task 286); SW kipia-v506→v507 одним инкрементом, тесты 5378/0 = паритет 5372 + 6 task344 (маппинг v695→v507 (525)/v696→v508 (123)/негативы v694→v506 (2)/v693→v505 (1)/v692→v504 (1)/v691→v503 (1)/v690→v502 (1)/v689→v501 (2)/исторические; test-task344 v506→v507; run-all +471); де-изоляция ×15, дифф диффов 925/59 сходится (дифф задач идентичен); SMOKE task471-smoke-k8.py 21/21 (порт 8997: год 2026→2025→2026/ввод работ Ноябрь 2026/planWorks.add/«Мероприятия» → описание/перечень Октябрь 2026 + setStatus {выполнено, дата сегодня}/Декабрь → Январь 2027/раскладка 468 жива/мобайл Task 464 жив, 0 JS); подводные камни: перенос-скрипт одноразовый (git checkout НЕ убирает неотслеживаемые новые файлы партии — rm + чистый прогон), сравнение case Code.gs — по НАБОРУ не по порядку, test-task471 содержит ДВА вхождения версии-до-партии (ассерт + сообщение). DEPLOY-Task471-plan-events-years-works-month.md — СЕРВЕРНЫЕ ШАГИ Apps Script: 1) заменить PlanEvents.gs; 2) Code.gs +5 case; 3) новая версия развёртывания; 4) PlanWorksInit.gs → planWorksDeploy (лист «Работы на месяц»); 5) клиент — автодеплой (порядок любой — тихая деградация). CI 4/4, прод kipia-v507 (curl: pePrevYearBtn/peWorksView/PlanWorksData на месте). СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 472 (в обоих репо).'

if CUR_MARK not in src:
    print('ОШИБКА: не найдена строка версии post-470')
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

# (в) «Текущая версия кэша» v506 → v507
old_cache = '> **Текущая версия кэша:** `kipia-v506`'
new_cache = '> **Текущая версия кэша:** `kipia-v507`'
if old_cache not in src:
    print('ОШИБКА: не найдена строка текущей версии кэша')
    sys.exit(1)
src = src.replace(old_cache, new_cache, 1)

# (г) строка «Инкрементируй» — следующие версии
old_inc = 'Формат: `kipia-test-v694` → `kipia-test-v695` (для kip8test) или `kipia-v505` → `kipia-v506` (для kip8)'
new_inc = 'Формат: `kipia-test-v695` → `kipia-test-v696` (для kip8test) или `kipia-v506` → `kipia-v507` (для kip8)'
if old_inc not in src:
    print('ОШИБКА: не найдена строка «Инкрементируй»')
    sys.exit(1)
src = src.replace(old_inc, new_inc, 1)

# (д) ожидание тестов 5334/5328 → 5378/5372
old_exp = '# Ожидается: 5334 passed, 0 failed (kip8; в kip8test — 5328 passed, 0 failed)'
new_exp = '# Ожидается: 5378 passed, 0 failed (kip8; в kip8test — 5372 passed, 0 failed)'
if old_exp not in src:
    print('ОШИБКА: не найдена строка ожидания тестов')
    sys.exit(1)
src = src.replace(old_exp, new_exp, 1)

# (е) контроль
assert src.count(NEW_LINE3) == 1
assert src.count(PREV_MARK) <= n_prev_before + 1

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(src)
print('OK: промт kip8 обновлён до post-Task 471')
print('  предыдущих строк: %d (было %d)' % (src.count(PREV_MARK), n_prev_before))
