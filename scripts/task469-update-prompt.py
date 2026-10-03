#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 469: обновление системного промта kip8 (post-Task 469 — перенос
# из kip8test@d56a2ea3, SW kipia-v504→v505, клиент-only).
import io
import sys

PATH = 'Системный_промт_для_приложения_КИПиА.md'
with io.open(PATH, encoding='utf-8') as f:
    src = f.read()

CUR_MARK = '> **Версия документа:** 2026-10-03 (post-Task 468: ПЕРЕНОС'
PREV_MARK = '> **Версия документа (предыдущая):**'

NEW_LINE3 = '> **Версия документа:** 2026-10-03 (post-Task 469: ПЕРЕНОС из kip8test@d56a2ea3 в боевой kip8 ОДНИМ инкрементом SW kipia-v504→v505 — КЛИЕНТ-ONLY, серверных шагов НЕТ; заявка: «Перепиши описание раздела на "Периодические работы на участке КИП ИОС, выполняемые в начале и в конце каждого месяца. Функционал: Отметка выполнения — …, Хранение отметок — …, Правка отметки — …, Обновление — …"»): СУТЬ (окно «Описание раздела» Task 468 — переписан только ТЕКСТ, раскладка/стили/JS не менялись): (1) вводный абзац — «Периодические работы на участке КИП ИОС, выполняемые в начале и в конце каждого месяца.» (точный текст заявки); (2) «Хранение отметок» сокращён — «отметки записываются в архив.»; (3) пункт «Мобильная версия» УДАЛЕН — 5 → 4 пункта функционала (отметка выполнения/хранение/правка/обновление — дословно из заявки); «Мероприятия_КИП_ИОС» остаётся идентификатором в JS, из текста описания убран. ПЕРЕНОС: scripts/task469-transfer.py (де-изоляция ×15, «дифф диффов»: репо-дифф 59 == эталону kip8test@235f4f0e↔kip8@7564816, дифф задач 15 идентичен; .gs не тронуты — синхронны, Code.gs kip8-версия жива); тесты kip8 5310/0 = паритет 5304 + 6 task344 (маппинг v693→v505 (519)/v694→v506 (123)/негатив партии v692→v504 (1: test-task469)/негатив 468 v691→v503 (1)/негативы 467/466; test-task344 v504→v505; run-all +469). ПОДВОДНЫЕ КАМНИ: (а) перенос-скрипт ОДНОРАЗОВЫЙ; (б) НОВЫЙ: IMAGE_CACHE_VERSION в kip8 — kipia-images-v3 БЕЗ суффикса -test- (в kip8test kipia-images-test-v3) — в перенос-скрипт добавлен маппинг; без него test-task469 падал (5309/1) — при переносах новых ассертов на версии кэша картинок проверять суффикс; (в) test-task468.js адаптирован в kip8test под 469 (5→4 пункта) и пришёл с переносом автоматически. SMOKE task469-smoke-k8.py 19/19 (порт 8997: раскладка Task 468 жива — карточка слева обнимает таблицу cardW-tabW<=3, окно справа до правого края ±2; точный лид заявки, 4 пункта, «Хранение отметок» сокращён, старые фрагменты отсутствуют; 1100px колонка; 375px Task 464 жив: полоса месяца/один столбец/описание под таблицей; 0 JS). DEPLOY-Task469-plan-events-description-rewrite.md (КЛИЕНТ-ONLY — серверных шагов НЕТ). ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 SW `kipia-v505` (guard v506), тесты 5310/0; kip8test @d56a2ea3 SW `kipia-test-v693` (guard v694), тесты 5304/0 — Task 469 выкачан в ОБОИХ репо, открытых хвостов нет; десктопы — CI-автосинк (Sync content to kip8-desktop + Build Desktop App success). СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 470 (в обоих репо).'

if CUR_MARK not in src:
    print('ОШИБКА: не найдена строка версии post-468')
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

# (в) «Текущая версия кэша» v504 → v505
old_cache = '> **Текущая версия кэша:** `kipia-v504`'
new_cache = '> **Текущая версия кэша:** `kipia-v505`'
if old_cache not in src:
    print('ОШИБКА: не найдена строка текущей версии кэша')
    sys.exit(1)
src = src.replace(old_cache, new_cache, 1)

# (г) строка «Инкрементируй» — следующие версии
old_inc = 'Формат: `kipia-test-v692` → `kipia-test-v693` (для kip8test) или `kipia-v503` → `kipia-v504` (для kip8)'
new_inc = 'Формат: `kipia-test-v693` → `kipia-test-v694` (для kip8test) или `kipia-v504` → `kipia-v505` (для kip8)'
if old_inc not in src:
    print('ОШИБКА: не найдена строка «Инкрементируй»')
    sys.exit(1)
src = src.replace(old_inc, new_inc, 1)

# (д) ожидание тестов 5285/5279 → 5310/5304
old_exp = '# Ожидается: 5285 passed, 0 failed (kip8; в kip8test — 5279 passed, 0 failed)'
new_exp = '# Ожидается: 5310 passed, 0 failed (kip8; в kip8test — 5304 passed, 0 failed)'
if old_exp not in src:
    print('ОШИБКА: не найдена строка ожидания тестов')
    sys.exit(1)
src = src.replace(old_exp, new_exp, 1)

# (е) контроль
assert src.count(NEW_LINE3) == 1
assert src.count(PREV_MARK) <= n_prev_before + 1

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(src)
print('OK: промт kip8 обновлён до post-Task 469')
print('  предыдущих строк: %d (было %d)' % (src.count(PREV_MARK), n_prev_before))
