#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 382 — перенос из kip8test 811d963 (заявка: «В мобильной версии,
# на странице итогов учёта, в таблице вкладки месяц изначальную ширину
# столбца с фамилиями сотрудников сделай по ширине текста в ячейках
# как на вкладке год»). Зоны Task 382 (побайтово = дифф kip8test
# e2eddb0→811d963, index.html, 6 хунков):
#   1) CSS-комментарий Task 334-блока — «ПОСЛЕ 42%-й доли» →
#      «ПОСЛЕ базовой ширины» (доля стала фолбэком переменной);
#   2) базовое правило месяца .ws-tt-table:not(.ws-tt-year)
#      th/td.ws-tt-emp — width: 42% → var(--ws-tt-emp-w, 42%)
#      (по тексту, «как в году»; фолбэк — прежняя доля; эллипсис
#      остался) + комментарий Task 382 перед правилом;
#   3) комментарий Task 336 — «ПОСЛЕ базового правила ширины …
#      перебивает базовую ширину (Task 382 — var(--ws-tt-emp-w, 42%))»;
#   4) fonts.ready — вызов _measureTtEmpFullW (после _barExpSyncAll —
#      окно 600 символов теста 378 не сдвинуто);
#   5) НОВЫЙ метод _measureTtEmpFullW после _measureEmpNarrowW
#      (max «№ таб.+5+ФИО»/«Сотрудник» + 16 + 2 → --ws-tt-emp-w
#      на body; при активном сужении data-full-обмен + inline-№таб.;
#      невидимый контейнер пропускается; шторка⇄страница max; дедуп);
#   6) _reapplyEmpNarrow — вызов _measureTtEmpFullW (typeof-guard —
#      VM-моки не падают; после КАЖДОГО рендера итогов).
# Каскад сохранён: late-правило .ws-narrow ПОСЛЕ базового (сужение
# при прокрутке живо), fixed-раскладка/равные данные/год-авто/
# десктоп-скрытие НЕ тронуты. sw.js — ОТДЕЛЬНЫМ скриптом
# (task382-bump-sw.py: kipia-v458 → v459).
# Проверки: якорь уникален до замены; повторный запуск падает
# БЕЗ записи файла (dup-детект не срабатывает — якорь уже заменён,
# «not found»).
import sys, io

PATH = 'index.html'
src = io.open(PATH, encoding='utf-8').read()
orig = src
applied = []

def edit(old, new, label):
    global src
    i = src.find(old)
    if i == -1:
        print('FAIL not found: ' + label); sys.exit(1)
    if src.find(old, i + 1) != -1:
        print('FAIL dup: ' + label); sys.exit(1)
    src = src[:i] + new + src[i + len(old):]
    applied.append(label)


# ============================================================
# Правка 1: комментарий Task 334-блока (ранний мобильный блок)
# ============================================================
edit(
'        .ws-grid.ws-narrow td.ws-emp-col .ws-emp-pos { display: none; }\n\n        /* 4) СУЖЕНИЕ колонки сотрудников таблиц итогов (шторка и\n           страница): класс .ws-narrow на .ws-tt-table; ширина —\n           по сокращённому тексту (Task 336, переменная\n           --ws-tt-emp-nw меряется JS; для МЕСЯЧНОЙ таблицы\n           срабатывает правило ПОСЛЕ 42%-й доли — см. ниже) */\n        .ws-tt-table.ws-narrow th.ws-tt-emp,\n        .ws-tt-table.ws-narrow td.ws-tt-emp {\n            width: var(--ws-tt-emp-nw, 48px);\n        }\n        .ws-tt-table.ws-narrow .ws-tt-tabno { display: none; }\n\n',
'        .ws-grid.ws-narrow td.ws-emp-col .ws-emp-pos { display: none; }\n\n        /* 4) СУЖЕНИЕ колонки сотрудников таблиц итогов (шторка и\n           страница): класс .ws-narrow на .ws-tt-table; ширина —\n           по сокращённому тексту (Task 336, переменная\n           --ws-tt-emp-nw меряется JS; для МЕСЯЧНОЙ таблицы\n           срабатывает правило ПОСЛЕ базовой ширины — см. ниже) */\n        .ws-tt-table.ws-narrow th.ws-tt-emp,\n        .ws-tt-table.ws-narrow td.ws-tt-emp {\n            width: var(--ws-tt-emp-nw, 48px);\n        }\n        .ws-tt-table.ws-narrow .ws-tt-tabno { display: none; }\n\n',
     '1: комментарий Task 334-блока (ранний мобильный блок)')

# ============================================================
# Правка 2: базовое правило месяца — var(--ws-tt-emp-w, 42%)
# ============================================================
edit(
'    .ws-tt-table thead th.ws-tt-emp {\n        background: #1e293b;\n    }\n    [data-theme="light"] .ws-tt-table thead th.ws-tt-emp {\n        background: #bfcad5;\n    }\n    .ws-tt-table:not(.ws-tt-year) th.ws-tt-emp,\n    .ws-tt-table:not(.ws-tt-year) td.ws-tt-emp {\n        width: 42%;          /* мобайл: ФИО + равные столбцы данных */\n        overflow: hidden;\n        text-overflow: ellipsis;\n        white-space: nowrap;\n    }\n    /* Task 336 (заявка: «ширина столбца сотрудников — ПО ШИРИНЕ\n       СОКРАЩЁННОГО ТЕКСТА, так же в таблицах итогов вкладок\n',
'    .ws-tt-table thead th.ws-tt-emp {\n        background: #1e293b;\n    }\n    [data-theme="light"] .ws-tt-table thead th.ws-tt-emp {\n        background: #bfcad5;\n    }\n    /* Task 382 (заявка: «в мобильной версии, на странице итогов\n       учёта, в таблице вкладки месяц ИЗНАЧАЛЬНУЮ ширину столбца\n       с фамилиями — ПО ШИРИНЕ ТЕКСТА в ячейках, как на вкладке\n       год»): доля 42% заменена переменной --ws-tt-emp-w — её\n       меряет JS _measureTtEmpFullW (максимум «№ таб. + 5px маржи\n       + ФИО» строк и заголовка «Сотрудник» + паддинги ячейки\n       8+8 + 2 запас; годовая таблица — авто-раскладка, её колонка\n       и так по тексту — теперь месяц совпадает с ней). Фолбэк 42%\n       — прежняя доля (до замера/VM-моки/скрытый контейнер);\n       fixed-раскладка и равные столбцы данных остаются — делят\n       остаток ширины */\n    .ws-tt-table:not(.ws-tt-year) th.ws-tt-emp,\n    .ws-tt-table:not(.ws-tt-year) td.ws-tt-emp {\n        width: var(--ws-tt-emp-w, 42%);   /* Task 382: по тексту («как в году»); фолбэк — прежняя доля */\n        overflow: hidden;\n        text-overflow: ellipsis;\n        white-space: nowrap;\n    }\n    /* Task 336 (заявка: «ширина столбца сотрудников — ПО ШИРИНЕ\n       СОКРАЩЁННОГО ТЕКСТА, так же в таблицах итогов вкладок\n',
     '2: базовое правило месяца — var(--ws-tt-emp-w, 42%)')

# ============================================================
# Правка 3: комментарий Task 336 (порядок late-правила)
# ============================================================
edit(
'    }\n    /* Task 336 (заявка: «ширина столбца сотрудников — ПО ШИРИНЕ\n       СОКРАЩЁННОГО ТЕКСТА, так же в таблицах итогов вкладок\n       месяц и год»): суженная ширина колонки «Сотрудник» итогов —\n       переменная --ws-tt-emp-nw (меряет JS _measureEmpNarrowW —\n       максимум «Сотр»/4 букв фамилии + паддинги 16 + 2). Правило —\n       ОБЯЗАТЕЛЬНО ПОСЛЕ базовой 42%-й доли (специфичность\n       (0,3,1) равна — побеждает ПОЗДНИЙ): месячная таблица\n       (fixed-раскладка) раньше НЕ сужалась — 42% из базового\n       правила перекрывало узкую ширину из раннего Task 334-блока,\n       колонка оставалась широкой при прокрутке. Теперь явная\n       узкая ширина перебивает долю — сужается и месяц, и год */\n    .ws-tt-table.ws-narrow th.ws-tt-emp,\n    .ws-tt-table.ws-narrow td.ws-tt-emp {\n        width: var(--ws-tt-emp-nw, 48px);\n    }\n    [data-theme="light"] .ws-tt-table th.ws-tt-emp,\n    [data-theme="light"] .ws-tt-table td.ws-tt-emp {\n',
'    }\n    /* Task 336 (заявка: «ширина столбца сотрудников — ПО ШИРИНЕ\n       СОКРАЩЁННОГО ТЕКСТА, так же в таблицах итогов вкладок\n       месяц и год»): суженная ширина колонки «Сотрудник» итогов —\n       переменная --ws-tt-emp-nw (меряет JS _measureEmpNarrowW —\n       максимум «Сотр»/4 букв фамилии + паддинги 16 + 2). Правило —\n       ОБЯЗАТЕЛЬНО ПОСЛЕ базового правила ширины (специфичность\n       (0,3,1) равна — побеждает ПОЗДНИЙ): месячная таблица\n       (fixed-раскладка) раньше НЕ сужалась — базовая ширина\n       перекрывала узкую ширину из раннего Task 334-блока,\n       колонка оставалась широкой при прокрутке. Теперь явная\n       узкая ширина перебивает базовую ширину (Task 382 —\n       var(--ws-tt-emp-w, 42%)) — сужается и месяц, и год */\n    .ws-tt-table.ws-narrow th.ws-tt-emp,\n    .ws-tt-table.ws-narrow td.ws-tt-emp {\n        width: var(--ws-tt-emp-nw, 48px);\n    }\n    [data-theme="light"] .ws-tt-table th.ws-tt-emp,\n    [data-theme="light"] .ws-tt-table td.ws-tt-emp {\n',
     '3: комментарий Task 336 (порядок late-правила)')

# ============================================================
# Правка 4: fonts.ready — _measureTtEmpFullW
# ============================================================
edit(
'                    // Task 336: суженная ширина (по сокращённому тексту)\n                    // — тот же повторный замер после загрузки шрифта\n                    try { if (self._measureEmpNarrowW) self._measureEmpNarrowW(); } catch (e) {}\n                    // Task 378: шрифт меняет перенос текста окон бара —\n                    // пересчёт значков раскрытия\n                    try { if (self._barExpSyncAll) self._barExpSyncAll(); } catch (e) {}\n                });\n            }\n\n            // Task 314: локальная копия данных — МГНОВЕННОЕ открытие\n            // без сети (заявка: «открывался моментально без ожидания\n            // подгрузки»). _restoreCachedView поднимает из localStorage\n',
'                    // Task 336: суженная ширина (по сокращённому тексту)\n                    // — тот же повторный замер после загрузки шрифта\n                    try { if (self._measureEmpNarrowW) self._measureEmpNarrowW(); } catch (e) {}\n                    // Task 378: шрифт меняет перенос текста окон бара —\n                    // пересчёт значков раскрытия\n                    try { if (self._barExpSyncAll) self._barExpSyncAll(); } catch (e) {}\n                    // Task 382: полная ширина колонки «Сотрудник»\n                    // итогов (месяц, мобайл) — тоже зависит от шрифта\n                    try { if (self._measureTtEmpFullW) self._measureTtEmpFullW(); } catch (e) {}\n                });\n            }\n\n            // Task 314: локальная копия данных — МГНОВЕННОЕ открытие\n            // без сети (заявка: «открывался моментально без ожидания\n            // подгрузки»). _restoreCachedView поднимает из localStorage\n',
     '4: fonts.ready — _measureTtEmpFullW')

# ============================================================
# Правка 5: НОВЫЙ метод _measureTtEmpFullW
# ============================================================
edit(
"            var tw = maxW(document.getElementById('wsTtBody'));\n            var pw = maxW(document.getElementById('wsTtPageBody'));\n            if (tw < pw) tw = pw;\n            if (tw > 0) setVar('--ws-tt-emp-nw', Math.ceil(tw + 16 + 2) + 'px');\n        },\n\n        // Task 315: окно 2 бара — данные ВСЕХ мероприятий открытого\n        // месяца (заявка: «второе окно с данными всех мероприятий на\n        // открытый месяц, между кнопками и окном времени и\n        // праздников»). Источник — слой мероприятий _TRAININGS (лист\n        // «Инструктажи»): в окно попадают записи, ПЕРЕСЕКАЮЩИЕ месяц\n        // (дата_начала..дата_окончания; ISO-строки сравниваются\n",
"            var tw = maxW(document.getElementById('wsTtBody'));\n            var pw = maxW(document.getElementById('wsTtPageBody'));\n            if (tw < pw) tw = pw;\n            if (tw > 0) setVar('--ws-tt-emp-nw', Math.ceil(tw + 16 + 2) + 'px');\n        },\n\n        // Task 382 (заявка: «в мобильной версии, на странице\n        // итогов учёта, в таблице вкладки месяц изначальную ширину\n        // столбца с фамилиями — ПО ШИРИНЕ ТЕКСТА в ячейках, как на\n        // вкладке год»): замер ПОЛНОЙ (изначальной) ширины колонки\n        // «Сотрудник» таблиц итогов. Годовая таблица — авто-раскладка\n        // (колонка и так по тексту); месячная — fixed, её колонка\n        // получает ту же «естественную» ширину через переменную\n        // --ws-tt-emp-w: максимум по строкам (№ таб. + 5px маржи +\n        // ФИО) и заголовку «Сотрудник» + паддинги ячейки 8+8 + 2px\n        // запас (границы border-collapse + субпиксельность).\n        // Приём — как у _measureEmpNarrowW: спаны inline, их rect =\n        // ширина текста (эллипсис/ширина колонки не искажают замер);\n        // при АКТИВНОМ сужении текст временно возвращается к\n        // data-full, скрытый таб. номер показывается на время замера\n        // (инлайн-стиль), один reflow — всё возвращается. Результат —\n        // на body (наследуют и шторка, и страница итогов);\n        // невидимый контейнер (rect = 0) пропускается. Вызывается из\n        // _reapplyEmpNarrow (после КАЖДОГО рендера итогов — месяц и\n        // год зовут его последними) и по document.fonts.ready\n        // (поздний шрифт меняет ширину текста)\n        _measureTtEmpFullW: function() {\n            if (typeof document === 'undefined' || !document.body\n                    || !document.body.style\n                    || !document.body.style.setProperty) return;\n            var setVar = function(name, wpx) {\n                if (wpx <= 0) return;\n                if (document.body.style.getPropertyValue(name) === wpx) return;\n                document.body.style.setProperty(name, wpx);\n            };\n            // ширина прямоугольника inline-спана = ширина его текста\n            var spanW = function(el) {\n                if (!el || !el.getBoundingClientRect) return 0;\n                try {\n                    var r = el.getBoundingClientRect();\n                    return r ? r.width : 0;\n                } catch (e) { return 0; }\n            };\n            // максимум «естественной» ширины содержимого колонки\n            var maxW = function(container) {\n                if (!container || !container.querySelectorAll) return 0;\n                try {\n                    if (container.getBoundingClientRect\n                            && container.getBoundingClientRect().width <= 0) return 0;\n                } catch (e) { return 0; }\n                var spans = container.querySelectorAll('[data-s4]');\n                var olds = [], tabnos = [], oldD = [], i;\n                // 1) временно: ПОЛНЫЙ текст спанов + видимый № таб.\n                for (i = 0; i < spans.length; i++) {\n                    var full = spans[i].getAttribute\n                        ? (spans[i].getAttribute('data-full') || '') : '';\n                    olds.push(spans[i].textContent);\n                    if (full) spans[i].textContent = full;\n                }\n                var tnos = container.querySelectorAll('.ws-tt-tabno');\n                for (i = 0; i < tnos.length; i++) {\n                    if (!tnos[i].style) continue;\n                    tabnos.push(tnos[i]);\n                    oldD.push(tnos[i].style.display);\n                    tnos[i].style.display = 'inline';\n                }\n                // 2) один reflow — строки (№ таб. + 5px маржи + ФИО)\n                // и заголовок «Сотрудник» (как в авто-раскладке года)\n                var w = 0;\n                var cells = container.querySelectorAll('td.ws-tt-emp');\n                for (i = 0; i < cells.length; i++) {\n                    var cw = 0;\n                    var tno = cells[i].querySelector\n                        ? cells[i].querySelector('.ws-tt-tabno') : null;\n                    var nm = cells[i].querySelector\n                        ? cells[i].querySelector('.ws-tt-name') : null;\n                    if (tno) cw += spanW(tno) + 5;\n                    if (nm) cw += spanW(nm);\n                    if (cw > w) w = cw;\n                }\n                var heads = container.querySelectorAll('.ws-tt-emp-head');\n                for (i = 0; i < heads.length; i++) {\n                    var hw = spanW(heads[i]);\n                    if (hw > w) w = hw;\n                }\n                // 3) вернуть текст и инлайн-стили № таб.\n                for (i = 0; i < spans.length; i++) {\n                    spans[i].textContent = olds[i];\n                }\n                for (i = 0; i < tabnos.length; i++) {\n                    tabnos[i].style.display = oldD[i];\n                }\n                return w;\n            };\n            // итоги: шторка ИЛИ страница (меряется видимая)\n            var tw = maxW(document.getElementById('wsTtBody'));\n            var pw = maxW(document.getElementById('wsTtPageBody'));\n            if (tw < pw) tw = pw;\n            if (tw > 0) setVar('--ws-tt-emp-w', Math.ceil(tw + 16 + 2) + 'px');\n        },\n\n        // Task 315: окно 2 бара — данные ВСЕХ мероприятий открытого\n        // месяца (заявка: «второе окно с данными всех мероприятий на\n        // открытый месяц, между кнопками и окном времени и\n        // праздников»). Источник — слой мероприятий _TRAININGS (лист\n        // «Инструктажи»): в окно попадают записи, ПЕРЕСЕКАЮЩИЕ месяц\n        // (дата_начала..дата_окончания; ISO-строки сравниваются\n",
     '5: НОВЫЙ метод _measureTtEmpFullW')

# ============================================================
# Правка 6: _reapplyEmpNarrow — вызов замерщика
# ============================================================
edit(
"        _reapplyEmpNarrow: function() {\n            // Task 336: ширина суженной колонки — по сокращённому\n            // тексту (толерантно к VM-мокам без метода)\n            if (typeof this._measureEmpNarrowW === 'function') {\n                try { this._measureEmpNarrowW(); } catch (e) {}\n            }\n            var ids = ['wsGridWrap', 'wsTtBody', 'wsTtPageBody'];\n            for (var i = 0; i < ids.length; i++) {\n                var el = document.getElementById(ids[i]);\n                if (el && el.scrollLeft > 0) this._narrowApply(el, true);\n            }\n        },\n",
"        _reapplyEmpNarrow: function() {\n            // Task 336: ширина суженной колонки — по сокращённому\n            // тексту (толерантно к VM-мокам без метода)\n            if (typeof this._measureEmpNarrowW === 'function') {\n                try { this._measureEmpNarrowW(); } catch (e) {}\n            }\n            // Task 382: ПОЛНАЯ (изначальная) ширина колонки\n            // «Сотрудник» итогов — по тексту (толерантно к мокам)\n            if (typeof this._measureTtEmpFullW === 'function') {\n                try { this._measureTtEmpFullW(); } catch (e) {}\n            }\n            var ids = ['wsGridWrap', 'wsTtBody', 'wsTtPageBody'];\n            for (var i = 0; i < ids.length; i++) {\n                var el = document.getElementById(ids[i]);\n                if (el && el.scrollLeft > 0) this._narrowApply(el, true);\n            }\n        },\n",
     '6: _reapplyEmpNarrow — вызов замерщика')

# ============================================================
if src == orig:
    print('FAIL: ни одна правка не применена'); sys.exit(1)
io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK: применено правок %d' % len(applied))
for l in applied:
    print('  + ' + l)
