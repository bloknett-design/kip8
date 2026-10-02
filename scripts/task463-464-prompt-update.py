#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 463-464: обновление промтов ОБОИХ репо (kip8test + kip8) после
# ПЕРЕНОСА партии 463+464 в боевой kip8 (SW kipia-v500).
# Паттерн task460-462-prompt-update.py (демот версии + точечные замены).
import io
import os
import sys

K8T = '/home/z/my-project/kip8test'
K8 = '/home/z/my-project/kip8'
P_T = os.path.join(K8T, 'Системный_промт_для_приложения_КИПиА.md')
P_8 = os.path.join(K8, 'Системный_промт_для_приложения_КИПиА.md')
PREV_MARK = '> **Версия документа (предыдущая):**'

V_8 = """> **Версия документа:** 2026-10-02 (post-Task 463-464: ПЕРЕНОС ПАРТИИ Tasks 463+464 из kip8test@de669b9f в боевой kip8 ОДНИМ инкрементом SW kipia-v499→v500 — регламент Task 441 (партия = один инкремент, прецедент 259-262/460-462). СОСТАВ ПАРТИИ: Task 463 — «Плановые мероприятия» ИНТЕРАКТИВНЫ: клик по ячейке месяца → диалог подтверждения (наименование + месяц + дата выполнения, по умолчанию сегодня) → ЗЕЛЁНАЯ галочка (SVG polyline #43a047/#2e7d32, title «Выполнено dd.mm.yyyy») вместо тусклого крестика; отметка (наименование + дата) → архив файла Мероприятия_КИП_ИОС (лист «Архив»: id/дата_выполнения/мероприятие/год/месяц/email/время_отметки; создаётся одноразовым идемпотентным PlanEventsInit.gs — planEventsDeploy); сервер PlanEvents.gs: planEvents.list (отметки года) + planEvents.mark (ИДЕМПОТЕНТНО: запись (год, месяц, мероприятие) уже есть → already:true без дубля; валидация; аудит PLAN_EVENTS_MARK; доступ plan.events через rmRequirePerm fail-closed); кнопка «Обновить» #peRefreshBtn; наименования читаются из DOM (.pe-name) — один источник истины; Year плана 2026. Task 464 — ПОЛИРОВКА по заявке: (1) подсказка над таблицей УДАЛЕНА; (2) ширина колонки мероприятий ПО ТЕКСТУ (.pe-col-name width:auto + .pe-name/.pe-th-name nowrap); (3) кнопка «Подтвердить» (была «Отметить»), «Отмена» слегка красная (.pe-dialog .kip-dialog-cancel.pe-cancel-red); (4) клик по ОТМЕЧЕННОЙ ячейке → _editDialog «Изменение отметки» (дата prefill, [Отмена][Удалить отметку — pe-unmark-btn красная][Сохранить дату]) → planEvents.update (правка B дата_выполнения + G время_отметки у всех строк ключа; not_found если записи нет) / planEvents.unmark (deleteRow всех строк ключа С КОНЦА — идексы; идемпотентно removed:false); (5) МОБАЙЛ <= 1023px: полоса .pe-month-bar + select#peMonthSel (опции MONTHS, по умолчанию ТЕКУЩИЙ месяц; на десктопе display:none), _tagColumns (классы pe-mo-1..12 на th/td, разметка 96 ячеек не тронута) + _applyMonth (pe-mo-off всем кроме выбранного; CSS media скрывает); компактность: .pe-table width:100% + white-space:normal (десктопный nowrap 352+46px НЕ ВЛЕЗАЛ в 375px) + col.pe-col-month width:0 (col span=12 резервировал пустые слоты скрытых месяцев — «пустой столбец» справа, найдено VLM); SRV_VER '464'. МЕТОД (scripts/task463-464-transfer.py, паттерн 292/441-459/460-462): index.html — kip8test@de669b9f + 15 де-изоляций (якоря 459/460-462 скопированы ТОЧНО), «дифф диффов» (репо-дифф 59 == эталону kip8test@67c0139e↔kip8@11617e1, дифф задач 669 идентичен, kip8test-упоминаний 5 = 4 исторических + 1 комментарий PlanEventsData про общий бэкенд, kipia-test-v 0); .gs: WorkSchedule/PPEInit/RoleMatrix/RoleMatrixGate синхронны (партия не трогала), PlanEvents.gs + PlanEventsInit.gs скопированы, Code.gs — kip8-версия + 4 case planEvents.* перед default + шапка сигнатур; тесты с маппингом kipia-test-v688→kipia-v500 (504)/v689→kipia-v501 (123 guards)/v687→kipia-v499 (2 — негативы партии «версии до партии»)/v685+v684+v683→v498/исторические→v496+v495+v494+v481+v478, test-task344 v499→v500 (3), run-all +344+438–464. ПРОГОН: 5195 passed / 0 failed = паритет kip8test 5189/0 + 6 task344. SMOKE task463-464-smoke-k8.py 30/30 (порт 8997, ключи kip8 без префикса: A — план ✓ таблица/2 отметки сервера/подсказки нет/nowrap/селектор скрыт; B — диалог [Отмена pe-cancel-red][Подтвердить] → mark payload → галочка+title+тост; C — «Изменение отметки» 3 кнопки prefill → update → title 25.03.2026; D — «Удалить отметку» → unmark без date → крестик+тост; E — мобайл 375 светлая: селектор=текущий месяц, один столбец, влезает, декабрь+отметка; F — план ✗ кнопка скрыта/«Нет доступа»/хаб жив; 0 JS ×6). DEPLOY-Task463/464 — скопированы (ШАГИ СЕРВЕРА Task 463 УЖЕ ВЫПОЛНЕНЫ пользователем — лист «Архив» создан, отметки работают; для Task 464 — обновить PlanEvents.gs + 2 case в Code.gs + New version, см. DEPLOY-Task464). ПОДВОДНЫЕ КАМНИ: (а) проверки скрытия раздела в smoke — СТИЛЬ display, не отсутствие элемента (кнопка остаётся в DOM; noAccessScreen, не noAccess); (б) тесты-негативы «версии до партии» в kip8 — v499, а не v498 (до партии 463+464 кип8 был v499). ТЕКУЩЕЕ СОСТОЯНИЕ: kip8 SW `kipia-v500` (guard v501), тесты 5195/0 (173 тест-файла); kip8test @de669b9f, SW `kipia-test-v688` (guard v689), тесты 5189/0: партия 463-464 выкачена в ОБОИХ репо; десктопы — CI-автосинк при пуше index.html. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 465 (в обоих репо).)"""

V_T = """> **Версия документа:** 2026-10-02 (post-Task 463-464 ПЕРЕНОС: партия 463+464 перенесена из kip8test@de669b9f в боевой kip8 ОДНИМ инкрементом SW kipia-v499→v500 — регламент Task 441; команда на перенос дана в заявке Task 464: «И перенеси изменения в боевой kip8»; сервер Apps Script уже развёрнут пользователем по Task 463 (лист «Архив» создан, отметки работают), для Task 464 пользователю нужно обновить PlanEvents.gs + 2 case в Code.gs + New version — см. DEPLOY-Task464). МЕТОД: scripts/task463-464-transfer.py в kip8 (де-изоляция ×15 + «дифф диффов»: репо-дифф 59 == эталону kip8test@67c0139e↔kip8@11617e1, дифф задач 669 идентичен; kip8test-упоминаний 5 = 4 исторических + 1 комментарий PlanEventsData); тесты kip8 5195/0 = паритет 5189 + 6 task344 (маппинг v688→v500 (504)/v689→v501 (123)/негативы партии v687→v499 (2)); SMOKE task463-464-smoke-k8.py 30/30 (порт 8997, ключи без префикса); Code.gs kip8 + 4 case planEvents.*/шапка, PlanEvents.gs + PlanEventsInit.gs скопированы. ПОДВОДНЫЕ КАМНИ: скрытие раздела в smoke — СТИЛЬ display (элемент остаётся в DOM), экран noAccessScreen. ТЕКУЩЕЕ СОСТОЯНИЕ: kip8test SW `kipia-test-v688` (guard v689), тесты 5189/0; kip8 SW `kipia-v500` (guard v501), тесты 5195/0 (паритет + 6 task344) — партия 463-464 выкачена в ОБОИХ репо; десктопы — CI-автосинк. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 465 (в обоих репо)."""


def rd(p):
    return io.open(p, encoding='utf-8').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


def demote_and_set_line3(path, cur_mark, new_line3, label):
    src = rd(path)
    if cur_mark not in src:
        print('ОШИБКА [%s]: не найдена текущая строка версии %r'
              % (label, cur_mark[:50]))
        sys.exit(1)
    i3 = src.index(cur_mark)
    i3end = src.index('\n', i3)
    old_line3 = src[i3:i3end]
    n_prev = src.count(PREV_MARK)
    if PREV_MARK in src:
        # удалить самую старую «предыдущую» (храним 2)
        if n_prev > 2:
            iprev = src.rindex(PREV_MARK)
            iprev_end = src.index('\n', iprev)
            src = src[:iprev] + src[iprev_end + 1:]
    new_prev = PREV_MARK + ' ' + old_line3[len('> **Версия документа:** '):]
    src = src[:i3] + new_line3 + '\n' + new_prev + src[i3end:]
    wr(path, src)
    print('OK [%s]: строка 3 → post-Task 463-464 ПЕРЕНОС (+демот прежней)'
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


INC_OLD_8 = ('2. **Инкрементируй `CACHE_VERSION`** при изменении любых '
             'файлов приложения (HTML/CSS/JS/data). Формат: '
             '`kipia-test-v686` → `kipia-test-v687` (для kip8test) или '
             '`kipia-v499` → `kipia-v500` (для kip8)')
INC_NEW_8 = ('2. **Инкрементируй `CACHE_VERSION`** при изменении любых '
             'файлов приложения (HTML/CSS/JS/data). Формат: '
             '`kipia-test-v688` → `kipia-test-v689` (для kip8test) или '
             '`kipia-v500` → `kipia-v501` (для kip8)')

# ---------------- kip8 ----------------
demote_and_set_line3(P_8, '> **Версия документа:** 2026-10-02 (post-Task 460-462',
                     V_8, 'kip8')
replace_exact(P_8, '> **Текущая версия кэша:** `kipia-v499`',
              '> **Текущая версия кэша:** `kipia-v500`',
              'kip8: версия кэша v500')
replace_exact(P_8, INC_OLD_8, INC_NEW_8,
              'kip8: Инкрементируй v688→v689/v500→v501')
replace_exact(
    P_8,
    '# Ожидается: 5113 passed, 0 failed (kip8; в kip8test — 5107 '
    'passed, 0 failed)',
    '# Ожидается: 5195 passed, 0 failed (kip8; в kip8test — 5189 '
    'passed, 0 failed)',
    'kip8: Ожидается 5195/5189')
# эндпоинты: + planEvents.* (после workSchedule)
old_ep = '| `workSchedule.*` | График работы/табель: шахматка / сотрудники / инструктажи / отпуска / СИЗ — `listEntries`/`listEmployees`/`listTrainings`/`listVacations`/`listPpe` (СИЗ, Task 392)/`generateMonth`/`getPatterns`/`getStatusCodes`/`addEmployee`/`updateEmployee` (Task 384)/`dismissEmployee`/`addTraining`/`deleteTraining`/`addVacation`/'
new_ep = old_ep + '\n| `planEvents.list` / `planEvents.mark` / `planEvents.update` / `planEvents.unmark` | «Плановые мероприятия»: отметки года / отметка выполнения (идемпотентно, Task 463) / правка даты / снятие отметки (Task 464; архив файла Мероприятия_КИП_ИОС, лист «Архив»). |'
replace_exact(P_8, old_ep, new_ep, 'kip8: эндпоинты planEvents.*')
# источники данных: + Мероприятия_КИП_ИОС (после матрицы прав)
old_ds = '| **МАТРИЦА ПРАВ** (Task 293-296) | листы matrix/permissions/roles — галочки = права (13 прав × 12 ролей) | `1TmmNZLUArWH38F6NX0gMGar8LMNMQomm_FaGZv9osyk` |'
new_ds = old_ds + '\n| **Мероприятия_КИП_ИОС** (Task 463) | лист «Архив» — отметки выполнения «Плановых мероприятий» (id, дата_выполнения, мероприятие, год, месяц, email, время_отметки) | `1uX8Bz6FBS9HniZfWQnHeeyccTwwjwyvpPFWyFkIclCs` |'
replace_exact(P_8, old_ds, new_ds, 'kip8: источник Мероприятия_КИП_ИОС')
# Apps Script файлы: + PlanEvents.gs / PlanEventsInit.gs
old_gs = '`RoleMatrixInit.gs` (одноразовый init матрицы), `RoleMatrixTask340Init.gs` (одноразовый init уровней view.min),'
new_gs = '`PlanEvents.gs` (Task 463/464: план-мероприятия — отметки/правка/снятие/архив), `PlanEventsInit.gs` (одноразовый init листа «Архив» файла Мероприятия_КИП_ИОС), `RoleMatrixInit.gs` (одноразовый init матрицы), `RoleMatrixTask340Init.gs` (одноразовый init уровней view.min),'
replace_exact(P_8, old_gs, new_gs, 'kip8: Apps Script + PlanEvents.gs')

# ---------------- kip8test ----------------
demote_and_set_line3(P_T, '> **Версия документа:** 2026-10-02 (post-Task 464; заявка',
                     V_T, 'kip8test')
replace_exact(
    P_T,
    '# Ожидается: 5189 passed, 0 failed (kip8test; в kip8 — 5113 '
    'passed, 0 failed)',
    '# Ожидается: 5189 passed, 0 failed (kip8test; в kip8 — 5195 '
    'passed, 0 failed)',
    'kip8test: Ожидается 5189/5195')

# ---------------- проверки ----------------
for path, checks in (
    (P_8, [('post-Task 463-464', 1),
           ('kipia-v500', None), ('5195 passed', None),
           ('planEvents.update` / `planEvents.unmark`', None),
           ('Мероприятия_КИП_ИОС** (Task 463)', None)]),
    (P_T, [('post-Task 463-464 ПЕРЕНОС', 1),
           ('kipia-test-v688', None), ('5195 passed', None)]),
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
print('OK: промты post-Task 463-464 (перенос) ОБОИХ репо обновлены')
