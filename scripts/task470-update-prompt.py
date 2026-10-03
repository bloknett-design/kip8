#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 470: обновление системного промта kip8 (post-Task 470 —
# фиксация переноса из kip8test@059dad05).
import io
import sys

PATH = 'Системный_промт_для_приложения_КИПиА.md'
with io.open(PATH, encoding='utf-8') as f:
    src = f.read()

CUR_MARK = '> **Версия документа:** 2026-10-03 (post-Task 469: ПЕРЕНОС'
PREV_MARK = '> **Версия документа (предыдущая):**'

NEW_LINE3 = '> **Версия документа:** 2026-10-03 (post-Task 470: ПЕРЕНОС из kip8test@059dad05 — таблица «Плановых мероприятий» по заявке: точка «Ноя.» в конце сокращения ноября, мероприятие «Работы на следующий месяц» в группе «В конце месяца», НОВАЯ группа «На текущий месяц» с мероприятием «Работы на месяц» — 10 строк/120 ячеек; отметки Task 463 по наименованию из DOM — новые строки автоматически кликабельны; SW kipia-v505→v506 одним инкрементом, тесты 5334/0 = паритет 5328 + 6 task344 (маппинг v694→v506 (522)/v695→v507 (123)/негативы v693→v505 (1)/v692→v504 (1)/v691→v503 (1)/v690→v502 (1)/v689→v501 (2)/исторические; IMAGE_CACHE_VERSION kipia-images-v3; test-task344 v505→v506; run-all +470); де-изоляция ×15, дифф диффов 59/31 сходится, .gs не тронуты — КЛИЕНТ-ONLY, серверных шагов НЕТ; SMOKE 22/22 (порт 8997: «Ноя.»/3 группы/10 строк/иконки 120/диалог новой строки/раскладка 468 жива/лид 469 жив/1100/375 мобайл 10 ячеек, 0 JS); подводные камни: перенос-скрипт одноразовый (повтор вставил дубль require — убран), комментарий sw.js не должен разрывать фразу «Работы на следующий месяц». СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 471 (в обоих репо).'

if CUR_MARK not in src:
    print('ОШИБКА: не найдена строка версии post-469')
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

# (в) «Текущая версия кэша» v505 → v506
old_cache = '> **Текущая версия кэша:** `kipia-v505`'
new_cache = '> **Текущая версия кэша:** `kipia-v506`'
if old_cache not in src:
    print('ОШИБКА: не найдена строка текущей версии кэша')
    sys.exit(1)
src = src.replace(old_cache, new_cache, 1)

# (г) строка «Инкрементируй» — следующие версии
old_inc = 'Формат: `kipia-test-v693` → `kipia-test-v694` (для kip8test) или `kipia-v504` → `kipia-v505` (для kip8)'
new_inc = 'Формат: `kipia-test-v694` → `kipia-test-v695` (для kip8test) или `kipia-v505` → `kipia-v506` (для kip8)'
if old_inc not in src:
    print('ОШИБКА: не найдена строка «Инкрементируй»')
    sys.exit(1)
src = src.replace(old_inc, new_inc, 1)

# (д) ожидание тестов 5310/5304 → 5334/5328
old_exp = '# Ожидается: 5310 passed, 0 failed (kip8; в kip8test — 5304 passed, 0 failed)'
new_exp = '# Ожидается: 5334 passed, 0 failed (kip8; в kip8test — 5328 passed, 0 failed)'
if old_exp not in src:
    print('ОШИБКА: не найдена строка ожидания тестов')
    sys.exit(1)
src = src.replace(old_exp, new_exp, 1)

# (е) контроль
assert src.count(NEW_LINE3) == 1
assert src.count(PREV_MARK) <= n_prev_before + 1

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(src)
print('OK: промт kip8 обновлён до post-Task 470')
print('  предыдущих строк: %d (было %d)' % (src.count(PREV_MARK), n_prev_before))
