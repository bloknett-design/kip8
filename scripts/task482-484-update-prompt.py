#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 482-484: обновление системных промтов ОБОИХ репозиториев
# (post-Task 482-484 ПЕРЕНОС партии из kip8test@6ec17fbd (@ac339739
# Task 482 + @3edb79ce Task 483 + @6ec17fbd Task 484) в kip8 одним
# инкрементом SW kipia-v511→v512; команда пользователя из заявки
# Task 484: «И затем перенеси изменения в kip8»).
# Обновляет ОБА файла:
#   kip8/Системный_промт_для_приложения_КИПиА.md — версия + поля
#   (кэш v512, формат инкрементов v512→v513 / kip8test v708→v709,
#   факт-строка тестов 5899/192, ожидание 5899/5895);
#   kip8test/... — зеркальная запись переноса + «в kip8 — 5899» +
#   формат kip8-стороны v512→v513.
# ПОДВОДНЫЙ КАМЕНЬ (Task 475-482): «самая старая предыдущая» =
# ПОСЛЕДНЯЯ по позиции (rindex), не первая.
import io
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CUR_MARK = '> **Версия документа:**'
PREV_MARK = '> **Версия документа (предыдущая):**'

NEW_LINE3_K8 = ('> **Версия документа:** 2026-10-07 (post-Task 482-484 '
                'ПЕРЕНОС: партия перенесена из kip8test@6ec17fbd (@ac339739 '
                'Task 482 «табель — кап раскрытия окон бара + рамки бейджей '
                'И/ПЗ + галочка отметки в попапе ячейки» + @3edb79ce Task 483 '
                '«Графики КИП ИОС/Приборы — таблица+диаграмма „как в Excel“ + '
                'вычисляемые тренды ППР (ppr_chart в devices.json)» + '
                '@6ec17fbd Task 484 «Графики КИП ИОС/Блокировки — тот же вид '
                'и тот же подсчёт + удаление старого _renderPPRChart») в '
                'боевой kip8 ОДНИМ инкрементом SW kipia-v511→v512 — команда '
                'пользователя из заявки Task 484: «И затем перенеси изменения '
                'в kip8»; регламент Task 441 (партия = один инкремент). '
                'Состав партии (КЛИЕНТ-ONLY + ДАННЫЕ, Apps Script не тронут, '
                'серверных шагов НЕТ): Task 482 — index.html (кап окон '
                '«Мероприятия»/«Нормы» _barExpMaxH + рамки бейджей И/ПЗ '
                'evStateCls ws-ev-done/ws-ev-late + галочка ws-done-chk в '
                'попапе ячейки); Task 483 — charts-desktop.js '
                '(_renderDevicesPPR: таблица «Вид обслуживания × месяцы '
                'I–XII» с пастелями листа «Диаграммы» + сгруппированная '
                'диаграмма, выровненная по колонкам; данные ppr_chart '
                'считает sync-devices.py по листу «Приборы»: «Наличие в '
                'ППР»=«Есть», К/П/ТО; заШитые _PPR_DEVICES удалены) + '
                'data/devices.json (+61 строка блока); Task 484 — '
                'charts-desktop.js (вкладка «Блокировки» рендерится ТЕМ ЖЕ '
                '_renderDevicesPPR с noun «БЛОКИРОВОК», серии Кр/ТО; '
                'sync-lockouts.py parse_ppr_chart по исходному листу '
                '«Блокировки»: «Наличие в перечне и в ППР»=«Есть», '
                'регистронезависимое совпадение «Кр» через type_norm; '
                'старый _renderPPRChart + _niceMax + заШитые _PPR_LOCKOUTS '
                '+ их CSS УДАЛЕНЫ ~12,4 КБ; сводная статистика и Топ-10 '
                'вкладки не рендерятся) + data/lockouts.json (+43 строки '
                'блока; итоги Кр 503/ТО 1509). ПЕРЕНОС: scripts/'
                'task482-484-transfer.py (261 проверка OK) — де-изоляция ×16 '
                'rep1/17 якорей (те же из 478-481), «дифф диффов» сходится; '
                'sw.js — шапка kip8 + перенос-метка «Task 482-484 (перенос '
                'партии из kip8test@6ec17fbd)» + 3 комментария партии '
                'ДОСЛОВНО + v512, ТЕЛО от IMAGE-якоря идентично; окна: '
                'дистанции 474/472/471/461/473 = 3306/3815/4367/6820/3440 '
                'против окон 4000/4500/5000/7600/4600 (запасы 633+); '
                'маппинг тестов: v708→v512 (×581) / v709→v513 guards (×143) '
                '/ негативы партии v705+v706+v707→v511 / негативы 478-481 '
                'v701-v704→v510; точечные fixes шапок/имён 478-481 + '
                'партии; test-task480 kip8-АДАПТАЦИЯ (README-тесты исключены '
                '— их в kip8 никогда не было, cron-мапа на kip8-расписания '
                'PROD на 2 ч раньше TEST); повтор фиксов 475-477/474; '
                'test-task344 v511→v512; run-all +482/483/484. ДАННЫЕ: '
                'ручной прогон sync-devices.py + sync-lockouts.py в kip8 — '
                'data/devices.json и data/lockouts.json байт-в-байт == '
                'kip8test HEAD (ppr_chart доставлен сразу; SWR text-compare '
                'подхватит, DATA_REFRESHED сбросит кэши разделов; дальше '
                'кроны 04:00/01:10 UTC). Тесты kip8 5899/0 = паритет 5895 '
                '+ 6 task344 − 2 README-теста. SMOKE task482-484-smoke-k8.py '
                '57/57 (порт 8996, ключи БЕЗ префикса, UA kip8-desktop): '
                'статика переноса (SW v512 + марка партии + кэши v3/v1 + '
                'де-изоляция DB_NAME/isolateLocalStorage) + графики (483 '
                'титул ПРИБОРОВ/значения == ppr_chart/итоги К 350-П 84-ТО '
                '2977; 484 титул БЛОКИРОВОК/значения/итоги Кр 503-ТО 1509/'
                'диаграмма 12+12/выравнивание ±3px/G «убрано лишнее»/'
                'фолбэк/светлая) + табель 482 (кап окна vh−10/скролл '
                'внутри/рамки бейджей зел-красн-обычн/галочка в попапе '
                'рядом с ✎/✕); 0 JS ×4; VLM ×3 — дефектов нет. ТЕКУЩЕЕ '
                'СОСТОЯНИЕ: kip8 SW `kipia-v512` (guard v513), тесты '
                '5899/0; kip8test SW `kipia-test-v708` (guard v709), тесты '
                '5895/0 — партия выкачана в ОБОИХ репо, открытых хвостов '
                'нет; десктопы — CI-автосинк. Пользователям kip8: '
                'Ctrl+Shift+R ×1-2. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 485 (в обоих '
                'репо).')

NEW_LINE3_K8T = ('> **Версия документа:** 2026-10-07 (post-Task 482-484 '
                 'ПЕРЕНОС: партия Tasks 482+483+484 (выполнены в kip8test '
                 '@ac339739/@3edb79ce/@6ec17fbd) перенесена в боевой kip8 '
                 'ОДНИМ инкрементом SW kipia-v511→v512 — команда '
                 'пользователя из заявки Task 484: «И затем перенеси '
                 'изменения в kip8»; регламент Task 441). В kip8: '
                 'де-изоляция ×17 (те же якоря из 478-481), «дифф диффов» '
                 'сходится, sw.js — шапка kip8 + перенос-метка + 3 '
                 'комментария партии дословно + ТЕЛО идентично; маппинг '
                 'тестов v708→v512/v709→v513/негативы v705-v707→v511; '
                 'test-task480-адаптация kip8 (README-тесты исключены, cron '
                 'на kip8-расписания); test-task344 v511→v512; run-all '
                 '+482/483/484; данные ppr_chart доставлены ручным прогоном '
                 'sync-devices.py + sync-lockouts.py (байт-в-байт == '
                 'kip8test HEAD); тесты kip8 5899/0 = паритет 5895 + 6 '
                 'task344 − 2 README-теста; SMOKE 57/57 (порт 8996) + VLM '
                 '×3. СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 485 (в обоих репо).')


def update(path, new_line3, replaces, checks):
    with io.open(path, encoding='utf-8') as f:
        src = f.read()
    if new_line3[:90] in src:
        print('SKIP (уже применено): %s' % os.path.basename(path))
        return
    # (а) удалить самую старую строку «предыдущая» (ПОСЛЕДНЯЯ по позиции)
    if src.count(PREV_MARK) > 2:
        iprev = src.rindex(PREV_MARK)
        iprev_end = src.index('\n', iprev)
        src = src[:iprev] + src[iprev_end + 1:]
    # (б) строка 3 → новая версия; старая → «предыдущая»
    i3 = src.index(CUR_MARK)
    i3end = src.index('\n', i3)
    old_line3 = src[i3:i3end]
    new_prev = PREV_MARK + ' ' + old_line3[len('> **Версия документа:** '):]
    src = src[:i3] + new_line3 + '\n' + new_prev + src[i3end:]
    # (в) поля
    for old, new in replaces:
        if old not in src:
            print('ОШИБКА (%s): не найдено %r' % (os.path.basename(path),
                                                  old[:70]))
            sys.exit(1)
        src = src.replace(old, new, 1)
    # проверки
    for marker, cnt in checks:
        c = src.count(marker)
        if cnt is not None and c != cnt:
            print('ОШИБКА (%s): маркер %r найден %d раз (ожидалось %s)'
                  % (os.path.basename(path), marker[:60], c, cnt))
            sys.exit(1)
        if cnt is None and c == 0:
            print('ОШИБКА (%s): маркер не найден: %r'
                  % (os.path.basename(path), marker[:60]))
            sys.exit(1)
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(src)
    print('OK: %s обновлён' % os.path.basename(path))


# --- kip8 ---
update(
    os.path.join(BASE, 'kip8', 'Системный_промт_для_приложения_КИПиА.md'),
    NEW_LINE3_K8,
    [
        ('> **Текущая версия кэша:** `kipia-v511`',
         '> **Текущая версия кэша:** `kipia-v512`'),
        ('Формат: `kipia-test-v705` → `kipia-test-v706` (для kip8test) или '
         '`kipia-v511` → `kipia-v512` (для kip8)',
         'Формат: `kipia-test-v708` → `kipia-test-v709` (для kip8test) или '
         '`kipia-v512` → `kipia-v513` (для kip8)'),
        ('# Ожидается: 5781 passed, 0 failed (kip8; в kip8test — 5777 '
         'passed, 0 failed)',
         '# Ожидается: 5899 passed, 0 failed (kip8; в kip8test — 5895 '
         'passed, 0 failed)'),
        ('(`tests/`, 5781 тестов, 190 тест-файлов, `node tests/run-all.js`)',
         '(`tests/`, 5899 тестов, 192 тест-файлов, `node tests/run-all.js`)'),
    ],
    [
        ('post-Task 482-484 ПЕРЕНОС', 1),
        ('kipia-v512', None),
        ('5899 passed, 0 failed (kip8', 1),
        ('СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 485', 1),
        ('ppr_chart', None),
    ])

# --- kip8test ---
update(
    os.path.join(BASE, 'kip8test', 'Системный_промт_для_приложения_КИПиА.md'),
    NEW_LINE3_K8T,
    [
        ('Формат: `kipia-test-v708` → `kipia-test-v709` (для kip8test) или '
         '`kipia-v511` → `kipia-v512` (для kip8)',
         'Формат: `kipia-test-v708` → `kipia-test-v709` (для kip8test) или '
         '`kipia-v512` → `kipia-v513` (для kip8)'),
        ('# Ожидается: 5895 passed, 0 failed (kip8test; в kip8 — 5781 '
         'passed, 0 failed)',
         '# Ожидается: 5895 passed, 0 failed (kip8test; в kip8 — 5899 '
         'passed, 0 failed)'),
    ],
    [
        ('post-Task 482-484 ПЕРЕНОС', 1),
        ('в kip8 — 5899', 1),
        # ×2: новая строка 3 + прежняя post-484 (тоже «485») в «предыдущей»
        ('СЛЕДУЮЩИЙ НОМЕР ЗАДАЧИ: 485', 2),
        ('kipia-test-v708', None),
    ])

print('OK: промты ОБОИХ репо обновлены — post-Task 482-484 ПЕРЕНОС '
      '(kip8 v512 5899/0; kip8test v708 5895/0; следующий 485)')
