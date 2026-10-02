#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 460-462: обновление промтов ОБОИХ репо (kip8test + kip8) после
# ПЕРЕНОСА партии 460+461+462 в боевой kip8 (2dc2346, SW kipia-v499).
# Паттерн task462-update-prompt (демот версии) + task459-prompt-update
# (точечные замены). Заодно ЛАТАЕМ устаревшие строки kip8test (сессии
# 460/461 прерывались: «Текущая версия кэша» и «Инкрементируй»
# остались на v683 — факт: v686).
import io
import os
import sys

K8T = '/home/z/my-project/kip8test'
K8 = '/home/z/my-project/kip8'
P_T = os.path.join(K8T, 'Системный_промт_для_приложения_КИПиА.md')
P_8 = os.path.join(K8, 'Системный_промт_для_приложения_КИПиА.md')
PREV_MARK = '> **Версия документа (предыдущая):**'

V460_8 = """> **Версия документа:** 2026-10-02 (post-Task 460-462: ПЕРЕНОС ПАРТИИ Tasks 460+461+462 из kip8test@92d54d7 в боевой kip8 ОДНИМ инкрементом SW kipia-v498→v499 — регламент Task 441 (партия = один инкремент, прецедент 259-262). СОСТАВ ПАРТИИ: Task 460 — НОВЫЙ раздел «Плановые мероприятия» в «Документации ИОС» (статичная таблица ПО ОБРАЗЦУ «Пример таблицы мероприятий.xlsx»: шапка «Мероприятия» rowspan 2 + «2026 год» colspan 12 + 12 месяцев (опечатка «Феф.» → «Фев.»), группы «В начале месяца» 3 / «В конце месяца» 5, 96 пустых ячеек; кнопка planEventsMenuBtn, закрепление subsection-cell, крошки, сайдбар, CSS обе темы); Task 461 — форма СИЗ («Работники»): подсказки наименований datalist #wsPpeNameList ДИНАМИЧЕСКИ из листа «СИЗ» табель_КИП_ИОС (WorkSchedule._fillPpeNameOptions при каждом открытии шторки: уникальные без повторов, регистр не важен — первое написание, trim, сортировка localeCompare 'ru'; пустой лист — запасной статичный набор 8 позиций; свободный ввод сохранён); Task 462 — доступ к разделу «Плановые мероприятия»: ОТДЕЛЬНОЕ право plan.events в матрице KIP8_Access (заявка: «в таблице matrix нужно добавить новый столбец для определения доступа к данному разделу»): колонка добавлена одноразовым идемпотентным RoleMatrixTask462Init.gs (копия-эталон в scripts/; серверный шаг УЖЕ ВЫПОЛНЕН пользователем 02.10.2026 — Apps Script/матрица одни на оба репо, RoleMatrix.gs читает колонки динамически, серверный код НЕ менялся; сам init-скрипт из облачного проекта Apps Script можно УДАЛИТЬ — он одноразовый, копия в репо); клиент: _PLAN_EVENTS_PAGES ['plan-events'] (убран из _KIP_IOS_PAGES), PLAN_EVENTS в init() + 4 уровня легаси-карты, _applyServerAccess: _drop + perm('plan.events'), ПЕРЕХОДНЫЙ hasOwnProperty-фоллбек (матрица без колонки → поведение 460), found=false → fail-closed, flowmeter-ветка только ['docs-ios'], право самодостаточно. МЕТОД (scripts/task460-462-transfer.py, паттерн 292/441-459): index.html — kip8test@92d54d7 + 15 де-изоляций (якоря 459 скопированы ТОЧНО), «дифф диффов» (репо-дифф 59 == эталону kip8test@3923f6a↔kip8@HEAD, дифф задач 302 идентичен, kip8test-упоминаний 4 исторических, kipia-test-v 0); .gs: WorkSchedule/PPEInit/RoleMatrix/RoleMatrixGate синхронны (партия не трогала), Code.gs — kip8-версия, RoleMatrixTask462Init.gs скопирован; тесты 170 test-*.js с маппингом kipia-test-v686→kipia-v499 (498)/v687→v500 (123)/негативы партии v683+v684+v685→v498 (5: test-task460 ×1 / test-task461 ×3 / test-task462 ×1 — «версии до партии» в kip8)/v681→v496/v680→v495/v679→v494/исторические→v481+v478, test-task344 v498→v499 (3), run-all +344+438–462. ПРОГОН: 5113 passed / 0 failed (171 файл = паритет kip8test 5107/0 + 6 task344). SMOKE task460-462-smoke-k8.py 41/41 (порт 8994, ключи kip8 без префикса: план ✓ — таблица образца полностью [шапка/rowspan 2/colspan 12/группы/8 мероприятий/96 пустых/рамки/#1e293b/зебра/жирные группы], крошки/сайдбар/закрепление; план ✗ — кнопка+сайдбар скрыты, прямой переход «Нет доступа», хаб ЖИВ; переходный без колонки — виден; легаси без getMyAccess — виден; «КИП8»+план ✓ — самодостаточно, хаба нет; datalist СИЗ 9 записей → 5 уникальных [повторы/регистр/пробелы/сортировка]; мобайл 375 — кнопка хаба + горизонтальный скролл; 0 JS ×7). CI 4/4 (CI Tests / Sync content to kip8-desktop / pages build / Build Desktop App), прод kip8 sw.js → CACHE_VERSION kipia-v499 + маркеры партии в разметке (curl); десктоп-зеркало автосинк c2f21e1. DEPLOY-Task460/461/462 — скопированы (серверных шагов НЕ требуется: матрица уже обновлена пользователем). ПОДВОДНЫЕ КАМНИ: (а) вывод перенос-скрипта НЕ в пайп head — SIGPIPE убивает скрипт на середине (повтор полным прогоном); (б) экранирование кавычек в Python-строках smoke-скрипта — тройные кавычки без бэкслэшей; (в) маркер чека test-task460 — голый SW_SRC.indexOf("…"), НЕ «CACHE_VERSION = '…'». ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 SW `kipia-v499` (guard v500), тесты 5113/0 (171 тест-файл); kip8test @92d54d7, SW `kipia-test-v686` (guard v687), тесты 5107/0: партия 460-462 выкачена в ОБОИХ репо; десктопы — CI-автосинк при пуше index.html. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 463 (в обоих репо).)"""

V460_T = """> **Версия документа:** 2026-10-02 (post-Task 460-462 ПЕРЕНОС: партия 460+461+462 перенесена из kip8test@92d54d7 в боевой kip8 ОДНИМ инкрементом SW kipia-v498→v499 — регламент Task 441; заявка Task 462: «После реализации и проверки определения доступа, дам команду для переноса изменений в боевой kip8» — пользователь подтвердил запуск RoleMatrixTask462Init.gs (колонка plan.events в matrix, галочки) и работу доступа («Создал, проверил, всё работает»), после чего дал команду на перенос; скрипт из облачного проекта Apps Script можно удалить — одноразовый, копия-эталон в scripts/ обоих репо). МЕТОД: scripts/task460-462-transfer.py в kip8 (де-изоляция ×15 + «дифф диффов»: репо-дифф 59 == эталону kip8test@3923f6a↔kip8@HEAD, дифф задач 302 идентичен); тесты kip8 5113/0 = паритет 5107 + 6 task344 (маппинг v686→v499 (498)/v687→v500 (123)/негативы партии v683+v684+v685→v498 (5)); SMOKE task460-462-smoke-k8.py 41/41 (порт 8994, ключи без префикса); CI 4/4, прод kip8 sw.js kipia-v499 (curl), десктоп-зеркало c2f21e1; серверный шаг Task 462 уже выполнен (общий Apps Script). ПОДВОДНЫЕ КАМНИ: (а) вывод перенос-скрипта НЕ в пайп head — SIGPIPE; (б) устаревшие строки промта kip8test (v683 в «Текущая версия кэша»/«Инкрементируй» — прерванные сессии 460/461) вычищены этой правкой до v686. ТЕКУЩЕЕ СОСТОЯНИЕ: kip8test SW `kipia-test-v686` (guard v687), тесты 5107/0; kip8 @2dc2346, SW `kipia-v499` (guard v500), тесты 5113/0 (паритет + 6 task344) — партия 460-462 выкачена в ОБОИХ репо; десктопы — CI-автосинк. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 463 (в обоих репо)."""


def rd(p):
    return io.open(p, encoding='utf-8').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


def demote_and_set_line3(path, cur_mark, new_line3, label):
    """Строка 3 → новая; старая строка 3 → «предыдущая» (старая
    «предыдущая» удаляется). Паттерн task462-update-prompt.py."""
    src = rd(path)
    if cur_mark not in src:
        print('ОШИБКА [%s]: не найдена текущая строка версии %r'
              % (label, cur_mark[:50]))
        sys.exit(1)
    i3 = src.index(cur_mark)
    i3end = src.index('\n', i3)
    old_line3 = src[i3:i3end]
    if PREV_MARK in src:
        iprev = src.index(PREV_MARK)
        iprev_end = src.index('\n', iprev)
        src = src[:iprev] + src[iprev_end + 1:]
    new_prev = PREV_MARK + ' ' + old_line3[len('> **Версия документа:** '):]
    src = src[:i3] + new_line3 + '\n' + new_prev + src[i3end:]
    wr(path, src)
    print('OK [%s]: строка 3 → post-Task 460-462 (+демот прежней)'
          % label)


def replace_exact(path, old, new, label):
    src = rd(path)
    n = src.count(old)
    if n != 1:
        print('ОШИБКА [%s]: вхождений %d (ожидалось 1): %r'
              % (label, n, old[:70]))
        sys.exit(1)
    wr(path, src.replace(old, new, 1))
    print('OK [%s]: %s' % (label, new[:60]))


INC_OLD = ('2. **Инкрементируй `CACHE_VERSION`** при изменении любых '
           'файлов приложения (HTML/CSS/JS/data). Формат: '
           '`kipia-test-v683` → `kipia-test-v684` (для kip8test) или '
           '`kipia-v498` → `kipia-v499` (для kip8)')
INC_NEW = ('2. **Инкрементируй `CACHE_VERSION`** при изменении любых '
           'файлов приложения (HTML/CSS/JS/data). Формат: '
           '`kipia-test-v686` → `kipia-test-v687` (для kip8test) или '
           '`kipia-v499` → `kipia-v500` (для kip8)')

# ---------------- kip8 ----------------
demote_and_set_line3(P_8, '> **Версия документа:** 2026-10-01 (post-Task 459',
                     V460_8, 'kip8')
replace_exact(P_8, '> **Текущая версия кэша:** `kipia-v498`',
              '> **Текущая версия кэша:** `kipia-v499`',
              'kip8: версия кэша v499')
replace_exact(P_8, INC_OLD, INC_NEW, 'kip8: Инкрементируй v686→v687/v499→v500')
replace_exact(
    P_8,
    '# Ожидается: 5029 passed, 0 failed (kip8; в kip8test — 5023 '
    'passed, 0 failed)',
    '# Ожидается: 5113 passed, 0 failed (kip8; в kip8test — 5107 '
    'passed, 0 failed)',
    'kip8: Ожидается 5113/5107')

# ---------------- kip8test ----------------
demote_and_set_line3(P_T, '> **Версия документа:** 2026-10-02 (post-Task 462',
                     V460_T, 'kip8test')
# ЛАТКА устаревших строк (сессии 460/461 прерывались — осталось v683)
replace_exact(P_T, '> **Текущая версия кэша:** `kipia-test-v683`',
              '> **Текущая версия кэша:** `kipia-test-v686`',
              'kip8test: версия кэша v683→v686 (латка прерванных сессий)')
replace_exact(P_T, INC_OLD, INC_NEW,
              'kip8test: Инкрементируй v683→v684 латаем на v686→v687')
replace_exact(
    P_T,
    '# Ожидается: 5107 passed, 0 failed (kip8test; в kip8 — 5029 '
    'passed, 0 failed)',
    '# Ожидается: 5107 passed, 0 failed (kip8test; в kip8 — 5113 '
    'passed, 0 failed)',
    'kip8test: Ожидается 5107/5113')

# ---------------- проверки ----------------
for path, checks in (
    (P_8, [('post-Task 460-462', 1),
           ('Версия документа (предыдущая):** 2026-10-01 (post-Task 459', 1),
           ('kipia-v499', None), ('5113 passed', None),
           ('kipia-v500', None)]),
    (P_T, [('post-Task 460-462 ПЕРЕНОС', 1),
           ('Версия документа (предыдущая):** 2026-10-02 (post-Task 462', 1),
           ('kipia-test-v686', None), ('5113 passed', None),
           ('kipia-test-v683` → `kipia-test-v684', 0)]),
):
    src = rd(path)
    for marker, cnt in checks:
        c = src.count(marker)
        if cnt is not None and c != cnt:
            print('ОШИБКА [%s]: маркер %r найден %d раз (ожидалось %s)'
                  % (os.path.basename(os.path.dirname(path)), marker[:50],
                     c, cnt))
            sys.exit(1)
        if cnt is None and c == 0:
            print('ОШИБКА [%s]: маркер не найден: %r'
                  % (os.path.basename(os.path.dirname(path)), marker[:50]))
            sys.exit(1)
print('OK: промты post-Task 460-462 (перенос) ОБОИХ репо обновлены')
