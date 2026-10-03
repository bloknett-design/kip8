#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 467: обновление системного промта kip8 (post-Task 467 — перенос
# из kip8test@ac074a2d, SW kipia-v502→v503, клиент-only).
import io
import sys

PATH = 'Системный_промт_для_приложения_КИПиА.md'
with io.open(PATH, encoding='utf-8') as f:
    src = f.read()

CUR_MARK = '> **Версия документа:** 2026-10-03 (post-Task 466: ПЕРЕНОС из kip8test@986db19b'
PREV_MARK = '> **Версия документа (предыдущая):**'

NEW_LINE3 = '> **Версия документа:** 2026-10-03 (post-Task 467: ПЕРЕНОС из kip8test@ac074a2d в боевой kip8 ОДНИМ инкрементом SW kipia-v502→v503 — КЛИЕНТ-ONLY, серверных шагов НЕТ; заявка: «В окне предпросмотра печати списка мероприятий, лист со списком смещён вправо за границу окна предпросмотра.»): ПРИЧИНА: iframe предпросмотра списка мероприятий наследовал альбомные 1063px из базового .wspprev-frame (Task 430 — печать ГРАФИКА), а _eventsPrevFit масштабирует КНИЖНЫЙ лист W=794 и режет paper overflow:hidden по 794px → лист (body display:flex justify-content:center центрировал его в viewport 1063px, отступ ~134px) уезжал вправо, правый край срезался границей окна. ФИКС (приём Task 449 wst-prev-frame — талоны прошли тот же путь): НОВЫЙ класс wsev-prev-frame: CSS-правило .wspprev-frame.wsev-prev-frame { width: 794px } (после базового — каскад перекрывает 1063px) + в _openEventsPreview frame.className = \'wspprev-frame wsev-prev-frame\' (комментарии Task 467 в CSS и JS); диалог/кнопки «Печать/Сохранить PDF/Сохранить Excel/Отмена»/генераторы PDF-Excel НЕ ТРОНУТЫ; график (1063px, базовый класс) и талоны (wst-prev-frame) — НЕ ТРОНУТЫ; свап значков окна мероприятий (Task 466) жив — печать слева 27px, раскрытие в углу 3px. ПЕРЕНОС: scripts/task467-transfer.py (де-изоляция ×15, «дифф диффов»: репо-дифф 59 == эталону kip8test@d8030094↔kip8@867d4df, дифф задач 15 идентичен; .gs не тронуты — синхронны, Code.gs kip8-версия жива); тесты kip8 5264/0 = паритет 5258 + 6 task344 (маппинг v691→v503 (513)/v692→v504 (123)/негатив партии v690→v502 (1: test-task467)/негативы партии 466 v689→v501 (2)/v687→v499 (2)/исторические; test-task344 v502→v503; run-all +467; test-task467.js ×14 пришёл из kip8test автоматически). ПОДВОДНЫЕ КАМНИ: (а) перенос-скрипт ОДНОРАЗОВЫЙ — повторный прогон на применённом состоянии вставляет ДУБЛИКАТ require в run-all.js (норма: git checkout -- . и один прогон; первый прогон чистый exit 0); (б) test-task467.js в kip8: негатив партии v502 (indexOf === -1) — «версии до Task 467 нет» — остаётся kipia-v502 после переноса 468. SMOKE task467-smoke-k8.py 8/8 (порт 8997, ключи БЕЗ префикса: свап 466 жив — печать 3/28 слева + раскрытие 3/3 в углу, зазор 3, 22×22; диалог от ЛЕВОГО значка — кнопки 4 + лист «Мероприятия»; ФИКС 467: iframe CSS 794px + viewport 794, лист left≈0/right≈794/ширина ~794, визуальный правый край ≤ paper.right+2, paper==794; Esc снимает диалог+инжект; 0 JS). Браузер kip8test task467-browser-check.py 21/21 (широкий 1600 + узкий 800: scale 0.929 жив) + пиксельная симметрия 403/403 + VLM ×1 (лист целиком, таблица видна). DEPLOY-Task467-events-preview-sheet-fit.md (КЛИЕНТ-ONLY — серверных шагов НЕТ). ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 SW `kipia-v503` (guard v504), тесты 5264/0; kip8test @ac074a2d SW `kipia-test-v691` (guard v692), тесты 5258/0 — Task 467 выкачан в ОБОИХ репо, открытых хвостов нет; десктопы — CI-автосинк (Sync content to kip8-desktop + Build Desktop App success). СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 468 (в обоих репо).'

if CUR_MARK not in src:
    print('ОШИБКА: не найдена строка версии post-466')
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

# (в) «Текущая версия кэша» v502 → v503
old_cache = '> **Текущая версия кэша:** `kipia-v502`'
new_cache = '> **Текущая версия кэша:** `kipia-v503`'
if old_cache not in src:
    print('ОШИБКА: не найдена строка текущей версии кэша')
    sys.exit(1)
src = src.replace(old_cache, new_cache, 1)

# (г) строка «Инкрементируй» — следующие версии
old_inc = 'Формат: `kipia-test-v690` → `kipia-test-v691` (для kip8test) или `kipia-v501` → `kipia-v502` (для kip8)'
new_inc = 'Формат: `kipia-test-v691` → `kipia-test-v692` (для kip8test) или `kipia-v502` → `kipia-v503` (для kip8)'
if old_inc not in src:
    print('ОШИБКА: не найдена строка «Инкрементируй»')
    sys.exit(1)
src = src.replace(old_inc, new_inc, 1)

# (д) ожидание тестов 5250/5244 → 5264/5258
old_exp = '# Ожидается: 5250 passed, 0 failed (kip8; в kip8test — 5244 passed, 0 failed)'
new_exp = '# Ожидается: 5264 passed, 0 failed (kip8; в kip8test — 5258 passed, 0 failed)'
if old_exp not in src:
    print('ОШИБКА: не найдена строка ожидания тестов')
    sys.exit(1)
src = src.replace(old_exp, new_exp, 1)

# (е) контроль
assert src.count(NEW_LINE3) == 1
assert src.count(PREV_MARK) <= n_prev_before + 1

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(src)
print('OK: промт kip8 обновлён до post-Task 467')
print('  предыдущих строк: %d (было %d)' % (src.count(PREV_MARK), n_prev_before))
