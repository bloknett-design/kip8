#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 468: обновление системного промта kip8 (post-Task 468 — перенос
# из kip8test@68e8fdbc, SW kipia-v503→v504, клиент-only).
import io
import sys

PATH = 'Системный_промт_для_приложения_КИПиА.md'
with io.open(PATH, encoding='utf-8') as f:
    src = f.read()

CUR_MARK = '> **Версия документа:** 2026-10-03 (post-Task 467: ПЕРЕНОС из kip8test@ac074a2d'
PREV_MARK = '> **Версия документа (предыдущая):**'

NEW_LINE3 = '> **Версия документа:** 2026-10-03 (post-Task 468: ПЕРЕНОС из kip8test@68e8fdbc в боевой kip8 ОДНИМ инкрементом SW kipia-v503→v504 — КЛИЕНТ-ONLY, серверных шагов НЕТ; заявка: «Ширину столбца "Мероприятия" сделай по самому длинному тексту, всю таблицу — влево экрана, а справа от таблицы на всё оставшееся место размести окно с Описанием раздела и его функционала.»): СУТЬ: (1) .pe-table min-width: 100% УДАЛЁН — ширина строго width: max-content (столбец «Мероприятия» по самому длинному наименованию); (2) НОВЫЙ .pe-layout (flex-строка, отступ 0 12px перенесён с .pe-card) → карточка таблицы слева (.pe-layout .pe-card { flex: 0 0 auto }) + НОВОЕ окно описания справа (aside.pe-desc-card { flex: 1 1 280px } — на всю остаточную ширину): «Описание раздела» + «Функционал» (5 пунктов: отметка/хранение в архиве/правка/обновление/мобильная версия — фактический функционал Task 460/463/464); (3) @media < 1200px — описание ПОД таблицей; мобильный вид Task 464 (≤1023px) НЕ ТРОНУТ; светлая тема окна описания. JS отметок (PlanEventsData/диалоги/кнопка «Обновить») НЕ ТРОНУТ. ПЕРЕНОС: scripts/task468-transfer.py (де-изоляция ×15, «дифф диффов»: репо-дифф 59 == эталону kip8test@fce2a778↔kip8@83aa340, дифф задач 121 идентичен; .gs не тронуты — синхронны, Code.gs kip8-версия жива); тесты kip8 5285/0 = паритет 5279 + 6 task344 (маппинг v692→v504 (516)/v693→v505 (123)/негатив партии v691→v503 (1: test-task468)/негатив 467 v690→v502 (1)/негативы 466 v689→v501 (2)/исторические; test-task344 v503→v504; run-all +468; test-task468.js ×21 пришёл из kip8test автоматически; фикс окна комментария Task 461 2000→2500 пришёл из kip8test — комментарий Task 468 в шапке sw.js отодвинул комментарий Task 461 (расстояние ~2100)). ПОДВОДНЫЕ КАМНИ: (а) перенос-скрипт ОДНОРАЗОВЫЙ — повторный прогон вставляет ДУБЛИКАТ require в run-all.js (норма: git checkout -- . и один чистый прогон, exit 0); (б) test-task468.js в kip8: негатив партии v503 (indexOf === -1) — «версии до Task 468 нет» — остаётся kipia-v503 после переноса 469. SMOKE task468-smoke-k8.py 14/14 (порт 8997, ключи БЕЗ префикса: flex row/карточка слева/карточка обнимает таблицу cardW-tabW<=3/окно до правого края ±2/заголовок + 5 пунктов/nowrap ≤ 40/1100px колонка + desc под таблицей/375px Task 464 жив: полоса месяца/один столбец/перенос normal/desc под таблицей/нет переполнения; 0 JS). Браузер kip8test task468-browser-check.py 31/31 (1600/1100/375/светлая тема) + VLM ×2 (десктоп + узкий/мобайл — без дефектов). DEPLOY-Task468-plan-events-layout-desc-window.md (КЛИЕНТ-ONLY — серверных шагов НЕТ). ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 SW `kipia-v504` (guard v505), тесты 5285/0; kip8test @68e8fdbc SW `kipia-test-v692` (guard v693), тесты 5279/0 — Task 468 выкачан в ОБОИХ репо, открытых хвостов нет; десктопы — CI-автосинк (Sync content to kip8-desktop + Build Desktop App success). СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 469 (в обоих репо).'

if CUR_MARK not in src:
    print('ОШИБКА: не найдена строка версии post-467')
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

# (в) «Текущая версия кэша» v503 → v504
old_cache = '> **Текущая версия кэша:** `kipia-v503`'
new_cache = '> **Текущая версия кэша:** `kipia-v504`'
if old_cache not in src:
    print('ОШИБКА: не найдена строка текущей версии кэша')
    sys.exit(1)
src = src.replace(old_cache, new_cache, 1)

# (г) строка «Инкрементируй» — следующие версии
old_inc = 'Формат: `kipia-test-v691` → `kipia-test-v692` (для kip8test) или `kipia-v502` → `kipia-v503` (для kip8)'
new_inc = 'Формат: `kipia-test-v692` → `kipia-test-v693` (для kip8test) или `kipia-v503` → `kipia-v504` (для kip8)'
if old_inc not in src:
    print('ОШИБКА: не найдена строка «Инкрементируй»')
    sys.exit(1)
src = src.replace(old_inc, new_inc, 1)

# (д) ожидание тестов 5264/5258 → 5285/5279
old_exp = '# Ожидается: 5264 passed, 0 failed (kip8; в kip8test — 5258 passed, 0 failed)'
new_exp = '# Ожидается: 5285 passed, 0 failed (kip8; в kip8test — 5279 passed, 0 failed)'
if old_exp not in src:
    print('ОШИБКА: не найдена строка ожидания тестов')
    sys.exit(1)
src = src.replace(old_exp, new_exp, 1)

# (е) контроль
assert src.count(NEW_LINE3) == 1
assert src.count(PREV_MARK) <= n_prev_before + 1

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(src)
print('OK: промт kip8 обновлён до post-Task 468')
print('  предыдущих строк: %d (было %d)' % (src.count(PREV_MARK), n_prev_before))
