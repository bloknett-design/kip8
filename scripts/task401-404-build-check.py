#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Сборка сводного браузер-чека переноса Task 401-404 в kip8:
# база — task404-browser-check.py из kip8test + блок годовой шторки
# Task 401 (из task401-browser-check.py) + ключи localStorage БЕЗ
# префикса kip8test (репо kip8) + порт 9008 + имена пруфов
# task401-404k8-*.png.
import io

SRC = '../kip8test/scripts/task404-browser-check.py'
DST = 'scripts/task401-404-browser-check.py'

s = io.open(SRC, encoding='utf-8').read()

# --- шапка-док ---
old_head = s.split('import datetime')[0]
new_head = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 401-404-transfer: СВОДНЫЙ browser-check переноса задач из
# kip8test в kip8 (боевой сайт): 401 (годовая шторка итогов на всю
# ширину + подстрока «дней/часов» + итоговые столбцы), 402 (тип
# работника третьей строкой ячейки + «группа_допуска»), 403 («разряд»
# → «р.» и без группы в столбце ФИО; попап без СИЗ; ярлыки по тексту),
# 404 (три колонки карточки; кнопки ✎/✕ рядом; окно мероприятий без
# отпусков). База — моки task404-browser-check (kip8test); ключи
# localStorage БЕЗ префикса (репо kip8); порт 9008.
"""
s = new_head + 'import datetime' + s.split('import datetime', 1)[1]

# --- порт ---
s = s.replace("PORT = 8905", "PORT = 9008")

# --- localStorage: без префикса kip8test (репо kip8) ---
old_ls = ("        \"localStorage.setItem('kip8test:kip8_session_token','bc-t403-%s');\" % tag +\n"
          "        \"localStorage.setItem('kip8test:app-theme','%s');\" % theme)")
new_ls = ("        \"localStorage.setItem('kip8_session_token','bc-t401-404k8-%s');\" % tag +\n"
          "        \"localStorage.setItem('app-theme','%s');\" % theme)")
assert s.count(old_ls) == 1, 'якорь localStorage не найден'
s = s.replace(old_ls, new_ls)
# служебные ключи кэша — без префикса (в kip8 isolate-блока нет)
s = s.replace("try{localStorage.removeItem('kip8test:kip8_ws_cache_v1')}catch(e){};",
              "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};")
s = s.replace("try{localStorage.removeItem('kip8test:kip8_my_access')}catch(e){};",
              "try{localStorage.removeItem('kip8_my_access')}catch(e){};")
assert 'kip8test:' not in s, 'остались префиксные ключи kip8test:'

# --- контекст 1: добавить блок годовой шторки Task 401 ---
anchor = """    # 2) попап по клику на ячейку — БЕЗ СИЗ
    page.click(\"td.ws-emp-col[data-tab='017']\")"""
insert = """    # 2) Task 401: годовая шторка итогов — на всю ширину правее ФИО
    page.click('#wsTotalsBtn')
    page.wait_for_timeout(600)
    page.wait_for_selector('#wsTtTabYear:not([hidden])', timeout=4000)
    page.click('#wsTtTabYear')
    page.wait_for_selector('#wsTotalsPanel .ws-tt-table.ws-tt-year', timeout=8000)
    page.wait_for_timeout(700)
    m = page.evaluate(MEASURE_JS)
    check('Y1: класс ws-tt-yearfull на странице', m['yearfull'])
    check('Y2: ширина шторки = рабочая область − ФИО (±4px)',
          abs(m['drawerW'] - (m['bodyW'] - m['empW'])) <= 4,
          (m['drawerW'], m['bodyW'], m['empW']))
    check('Y3: левый край шторки = правый край столбца ФИО (±3px)',
          abs(m['drawerL'] - m['empR']) <= 3, (m['drawerL'], m['empR']))
    check('Y4: шапка двухстрочная + подстрока «дней/часов» (colspan 12)',
          m['theadRows'] == 2 and m['subText'] == 'дней/часов' and
          m['subColspan'] == '12',
          (m['theadRows'], m['subText'], m['subColspan']))
    page.screenshot(path='task401-404k8-proof-year-dark.png', full_page=False)
    # закрыть шторку (возврат к сетке для попап-чека)
    page.click('#wsTotalsBtn')
    page.wait_for_timeout(800)

    # 3) попап по клику на ячейку — БЕЗ СИЗ
    page.click(\"td.ws-emp-col[data-tab='017']\")"""
assert s.count(anchor) == 1
s = s.replace(anchor, insert)

# --- MEASURE_JS: добавить определение (годовая шторка) ---
anchor2 = "CARD_COLS_JS = \"\"\"(function(){"
measure = """MEASURE_JS = \"\"\"(function(){
    var body = document.getElementById('wsWsBody');
    var drawer = document.getElementById('wsTotalsDrawer');
    var page = document.getElementById('page-work-schedule');
    var gridWrap = document.getElementById('wsGridWrap');
    var panel = document.getElementById('wsTotalsPanel');
    var empTh = gridWrap ? gridWrap.querySelector('.ws-grid thead th.ws-emp-col') : null;
    var table = panel ? panel.querySelector('.ws-tt-table.ws-tt-year') : null;
    var sub = panel ? panel.querySelector('th.ws-tt-sub') : null;
    var thead = panel ? panel.querySelector('.ws-tt-table.ws-tt-year thead') : null;
    var dR = drawer ? drawer.getBoundingClientRect() : {width: 0, left: 0, right: 0};
    var bR = body ? body.getBoundingClientRect() : {width: 0, right: 0};
    var eR = empTh ? empTh.getBoundingClientRect() : {width: 0, right: 0};
    return {
        bodyW: bR.width, bodyR: bR.right,
        drawerW: dR.width, drawerL: dR.left, drawerR: dR.right,
        empW: eR.width, empR: eR.right,
        yearfull: !!(page && page.classList.contains('ws-tt-yearfull')),
        theadRows: thead ? thead.querySelectorAll('tr').length : 0,
        subText: sub ? sub.textContent : null,
        subColspan: sub ? sub.getAttribute('colspan') : null
    };
})()\"\"\"

""" + anchor2
assert s.count(anchor2) == 1
s = s.replace(anchor2, measure)

# --- имена пруфов ---
s = s.replace('task404-proof-', 'task401-404k8-proof-')

io.open(DST, 'w', encoding='utf-8').write(s)
print('%s: собран (порт 9008, ключи kip8, + блок годовой шторки 401)' % DST)
