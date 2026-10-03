#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 472: обновление системного промта kip8 (post-Task 472 ПЕРЕНОС).
import io
import sys

PATH = 'Системный_промт_для_приложения_КИПиА.md'
with io.open(PATH, encoding='utf-8') as f:
    src = f.read()

CUR_MARK = '> **Версия документа:** 2026-10-03 (post-Task 471: ПЕРЕНОС'
PREV_MARK = '> **Версия документа (предыдущая):**'

NEW_LINE3 = '> **Версия документа:** 2026-10-03 (post-Task 472: ПЕРЕНОС из kip8test@65c55058 — «Плановые мероприятия» по заявке: поле ввода работ «на следующий месяц» — textarea с динамическим расширением ВНИЗ под новые строки текста (PlanWorksData._growInput: height:auto → scrollHeight+2px на каждый input; Enter — по-прежнему «Добавить»; кнопка прижата к первой строке), кликабельные ячейки таблицы (td.pe-m месяцы, месяцы шапки, «Мероприятия», строки работ pe-name-click) — вторая внутренняя рамка-бевел inset box-shadow, имитирующая выпуклость кнопки (светлая грань сверху/слева, тёмная снизу/справа; у выбранного месяца слита с полосой; группы без бевела), фон таблицы и окна НЕПРОЗРАЧНЫЙ (var(--card-bg) → #17212e тёмная, карточка #faf9f6 светлая), окно в светлой теме — БЕЖЕВОЕ #f0eee6 (как цвет фона бара --header-bg rgb(240,238,230)) с ТОЛСТОЙ 3px двухтонной рамкой с эффектом выступа (#fffdf7/#c8c2af) и мягкой тенью; КЛИЕНТ-ONLY — Apps Script не менялся, серверных шагов НЕТ (planWorks Task 471 работают как есть); SW kipia-v507→v508 одним инкрементом, тесты 5399/0 = паритет 5393 + 6 task344 (маппинг v696→v508 (531)/v697→v509 (123)/негатив партии 472 v695→v507 (2)/негативы 471 v694→v506 (2)/v693→v505 (1)/v692→v504 (1)/v691→v503 (1)/v690→v502 (1)/v689→v501 (2)/исторические; test-task344 v507→v508; run-all +472; Task 461 дистанция 3325 < 3600), де-изоляция ×15, дифф диффов сходится, SMOKE task472-smoke-k8.py 23/23 (порт 8997: бежевое окно/рамка-выступ 3px/бевел/textarea рост + Enter добавляет/тёмная #17212e/мобайл Task 464 жив, 0 JS), подводные камни: комментарий Task 472 в sw.js не должен вытеснять Task 471 из окна 900 (сжат до ~260 симв.), переключение темы в SMOKE — только toggleTheme() без reload (init-script перезаписывает app-theme). DEPLOY-Task472-plan-events-input-bevel-beige.md (КЛИЕНТ-ONLY — откат: вернуть index.html+sw.js и поднять версию). CI 4/4, прод kipia-v508. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 473 (в обоих репо).'

if CUR_MARK not in src:
    print('ОШИБКА: не найдена строка версии post-471')
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

# (в) «Текущая версия кэша» v507 → v508
old_cache = '> **Текущая версия кэша:** `kipia-v507`'
new_cache = '> **Текущая версия кэша:** `kipia-v508`'
if old_cache not in src:
    print('ОШИБКА: не найдена строка текущей версии кэша')
    sys.exit(1)
src = src.replace(old_cache, new_cache, 1)

# (г) строка «Инкрементируй» — следующие версии
old_inc = 'Формат: `kipia-test-v695` → `kipia-test-v696` (для kip8test) или `kipia-v506` → `kipia-v507` (для kip8)'
new_inc = 'Формат: `kipia-test-v696` → `kipia-test-v697` (для kip8test) или `kipia-v507` → `kipia-v508` (для kip8)'
if old_inc not in src:
    print('ОШИБКА: не найдена строка «Инкрементируй»')
    sys.exit(1)
src = src.replace(old_inc, new_inc, 1)

# (д) ожидание тестов 5378/5372 → 5399/5393
old_exp = '# Ожидается: 5378 passed, 0 failed (kip8; в kip8test — 5372 passed, 0 failed)'
new_exp = '# Ожидается: 5399 passed, 0 failed (kip8; в kip8test — 5393 passed, 0 failed)'
if old_exp not in src:
    print('ОШИБКА: не найдена строка ожидания тестов')
    sys.exit(1)
src = src.replace(old_exp, new_exp, 1)

# (е) контроль
assert src.count(NEW_LINE3) == 1
assert src.count(PREV_MARK) <= n_prev_before + 1

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(src)
print('OK: промт kip8 обновлён до post-Task 472')
print('  предыдущих строк: %d (было %d)' % (src.count(PREV_MARK), n_prev_before))
