#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 447-SMOKE (kip8): кнопка «Талоны» + отчёт по талонам питания
# после переноса 447 из kip8test (SW kipia-v485→v486). Ключи kip8 —
# БЕЗ префикса kip8test. Порт 8958.
#   A: приложение + график + кнопка «Талоны» ВИДНА (edit);
#   B: страница отчёта — явки 5/3/2 (итоги шахматки), предзаполнение;
#   C: ручная правка +3 — чипы/итог ТОЧЕЧНО, бейдж;
#   D: предпросмотр строгой формы — правленое значение 8, Итого 10/13,
#      только «Печать»/«Отмена», «A4 · книжная»; закрытие — стиль снят;
#   E: зритель (view, без edit) — кнопка СКРЫТА, прямой URL — редирект;
#   F: мобайл 375 — страница + скролл-обёртка;
#   G: 0 JS-ошибок ×3 контекста.
import datetime
import json
import re
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8958
ROOT = '/home/z/my-project/kip8'
TODAY = datetime.date.today()
CUR_Y, CUR_M = TODAY.year, TODAY.month
MONTHS_RU = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
             'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
MONTH_NAME = MONTHS_RU[CUR_M - 1]

EMPLOYEES = [
  {'таб_номер': '0871', 'ФИО': 'Федосов А. В.', 'тип': 'сменный', 'смена': 1,
   'шаблон_ротации': 1, 'старт_цикла': '%04d-%02d-01' % (CUR_Y, CUR_M),
   'дата_приёма': '2024-03-15', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА 5 разряд', 'группа_допуска': 'IV',
   'комментарий': ''},
  {'таб_номер': '0955', 'ФИО': 'Петров П. П.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 0, 'старт_цикла': '',
   'дата_приёма': '2023-11-05', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Электромонтёр', 'группа_допуска': 'III',
   'комментарий': ''},
  {'таб_номер': '0377', 'ФИО': 'Яковлев Я. Я.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 0, 'старт_цикла': '',
   'дата_приёма': '2025-01-20', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Инженер КИПиА', 'группа_допуска': '',
   'комментарий': ''},
]
CODES = [
  {'code': 'Д8', 'name': 'День 8-час (7:30–16:30)', 'color': '#FFF9C4',
   'short': 'день 8ч'},
  {'code': 'Н', 'name': 'Ночь (12-час)', 'color': '#B0BEC5', 'short': 'ночь 12ч'},
]
PATTERNS = []


def month_entries(y, m):
    out = []
    for d in range(1, 6):
        out.append({'дата': '%04d-%02d-%02d' % (y, m, d), 'таб_номер': '0871',
                    'статус': 'Д8', 'переработка': 0, 'праздник': 0,
                    'источник': 'авто'})
    for d in range(1, 4):
        out.append({'дата': '%04d-%02d-%02d' % (y, m, d), 'таб_номер': '0955',
                    'статус': 'Д8', 'переработка': 0, 'праздник': 0,
                    'источник': 'авто'})
    for d in range(2, 4):
        out.append({'дата': '%04d-%02d-%02d' % (y, m, d), 'таб_номер': '0377',
                    'статус': 'Н', 'переработка': 0, 'праздник': 0,
                    'источник': 'авто'})
    return out


PASS = 0
FAIL = 0
OUT = '/home/z/my-project/download/kip8-task447-transfer'
import os
os.makedirs(OUT, exist_ok=True)


def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(('  + ' if ok else '  X ') + name +
          (('  [' + str(extra)[:230] + ']') if (extra and not ok) else ''))


def api_response(action, body, perms):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local',
                'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': perms}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'workSchedule.getStatusCodes':
        return {'ok': True, 'data': {'codes': CODES}}
    if action == 'workSchedule.listEmployees':
        return {'ok': True, 'data': {'employees': EMPLOYEES}}
    if action == 'workSchedule.getPatterns':
        return {'ok': True, 'data': {'patterns': PATTERNS}}
    if action == 'workSchedule.listTrainings':
        return {'ok': True, 'data': {'trainings': [], 'instrList': [],
                'instrAll': [], 'eventsAll': []}}
    if action == 'workSchedule.listVacations':
        return {'ok': True, 'data': {'vacations': []}}
    if action == 'workSchedule.listPpe':
        return {'ok': True, 'data': {'ppe': []}}
    if action == 'workSchedule.listEntries':
        year = body.get('year') or CUR_Y
        month = body.get('month') or CUR_M
        try:
            y = int(year)
            m = int(month)
        except Exception:
            y, m = CUR_Y, CUR_M
        return {'ok': True, 'data': {'entries': month_entries(y, m)}}
    if action == 'prodCalendar.getMonth':
        return {'ok': True, 'data': {'workdays': 22, 'weekends': 8,
                'shortdays': 0, 'holidays': [], 'transfers': []}}
    return {'ok': True, 'data': {'ok': True}}


PERMS_EDIT = {'workschedule.view': True, 'workschedule.edit': True}
PERMS_VIEW = {'workschedule.view': True, 'workschedule.edit': False}


def attach(page, ctx, tag, perms):
    js_errors = []
    page.on('pageerror', lambda e: js_errors.append(str(e)))
    page.on('dialog', lambda dlg: dlg.accept())
    # КЛЮЧИ kip8 — БЕЗ префикса kip8test:
    ctx.add_init_script(
        "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
        "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
        "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
        "localStorage.setItem('kip8_session_token','bc-t447k8-%s');" % tag +
        "localStorage.setItem('app-theme','dark');")

    def handle(route, request):
        url = request.url
        action = ''
        if 'action=' in url:
            action = unquote(url.split('action=')[1].split('&')[0])
        pd_ = request.post_data
        body = {}
        if pd_:
            try:
                body = json.loads(pd_)
            except Exception:
                body = {}
        resp = api_response(action, body, perms)
        return route.fulfill(status=200,
                             content_type='application/json; charset=utf-8',
                             body=json.dumps(resp, ensure_ascii=False))

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)

    def block_external(route):
        route.fulfill(status=404, content_type='text/plain',
                      body='not found (t447k8-%s)' % tag)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)
    return js_errors


def row_days(page):
    return page.evaluate("""(function(){
        var out = [];
        var rows = document.querySelectorAll('#wsTalonsBody tbody tr');
        for (var i = 0; i < rows.length; i++) {
            var tds = rows[i].querySelectorAll('td');
            out.push({tab: tds[1].textContent.trim(),
                      days: tds[4].textContent.trim(),
                      tal: rows[i].querySelector('input.wst-count') ?
                           rows[i].querySelector('input.wst-count').value : ''});
        }
        return out;})()""")


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        print('=== kip8 SMOKE: десктоп (edit) ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        js_errors = attach(page, ctx, 'desktop', PERMS_EDIT)
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2500)
        check('A1: график открыт (kip8)',
              page.evaluate("(function(){return !!document.querySelector(" +
              "'.ws-grid');})()"))
        sw = page.evaluate("(function(){var m = " +
              "document.documentElement.innerHTML.match(/CACHE_VERSION/);" +
              "return !!m;})()")
        check('A2: kip8 страница загружена', sw)
        btn = page.evaluate("(function(){var b = document." +
              "getElementById('wsTalonsBtn'); return b ? {hidden: b.hidden} " +
              ": null;})()")
        check('A3: кнопка «Талоны» ВИДНА (edit)', btn and
              btn['hidden'] is False, btn)
        page.click('#wsTalonsBtn')
        page.wait_for_timeout(1000)
        title = page.evaluate("(function(){var t = document." +
              "querySelector('#wsTalonsBody .wst-title'); return t ? " +
              "t.textContent.trim() : '';})()")
        check('B1: заголовок «Отчёт по талонам питания — %s %d г.»'
              % (MONTH_NAME, CUR_Y),
              title == 'Отчёт по талонам питания — %s %d г.'
              % (MONTH_NAME, CUR_Y), title)
        rows = row_days(page)
        check('B2: явки из итогов 5/3/2, талоны предзаполнены',
              [(r['days'], r['tal']) for r in rows] ==
              [('5', '5'), ('3', '3'), ('2', '2')], rows)
        page.fill('input.wst-count[data-tab="0871"]', '8')
        page.wait_for_timeout(300)
        st = page.evaluate("""(function(){return {
            chip: (document.getElementById('wstTotalTalonsChip')||{})
                .textContent,
            tot: (document.getElementById('wstTotalTalons')||{})
                .textContent,
            edit: (document.getElementById('wstEditCount')||{})
                .textContent};})()""")
        check('C1: правка +3 — чип «Талонов: 13» (8+3+2), итог 13, '
              '«Правок: 1»',
              st['chip'] == '13' and st['tot'] == '13' and
              st['edit'] == '1', st)
        page.click('.wst-print-btn')
        page.wait_for_timeout(1200)
        check('D1: предпросмотр открыт + инжект-стиль книжной @page',
              page.evaluate("(function(){return !!document." +
              "getElementById('wsTalonsPrevModal') && !!document." +
              "getElementById('wsTalonsPrintStyle');})()"))
        prows = page.evaluate("""(function(){
            var f = document.querySelector('#wsTalonsPrevModal iframe');
            var out = [];
            f.contentDocument.querySelectorAll('.wst-rep-table tr').
            forEach(function(tr){
                var cells = [];
                tr.querySelectorAll('th,td').forEach(function(c){
                    cells.push(c.textContent.trim());});
                out.push(cells);});
            return out;})()""")
        check('D2: строгая форма — правленое значение 8, Итого 10/13',
              len(prows) == 5 and prows[1][4:6] == ['5', '8'] and
              prows[4] == ['Итого', '10', '13'], prows)
        foot = page.evaluate("(function(){var out = []; document." +
              "querySelectorAll('#wsTalonsPrevModal .wspprev-btn')." +
              "forEach(function(b){out.push(b.textContent.trim());});" +
              "return out;})()")
        check('D3: только «Печать»/«Отмена» (без PDF/Excel)',
              foot == ['Печать', 'Отмена'], foot)
        page.keyboard.press('Escape')
        page.wait_for_timeout(500)
        check('D4: закрытие — диалог и инжект-стиль СНЯТЫ',
              page.evaluate("(function(){return !document.getElementById(" +
              "'wsTalonsPrevModal') && !document.getElementById(" +
              "'wsTalonsPrintStyle');})()"))
        page.screenshot(path=OUT + '/01-kip8-talons.png')
        check('G1: 0 JS-ошибок (десктоп)', js_errors == [], js_errors[:3])
        ctx.close()

        print('=== kip8 SMOKE: зритель (view) ===')
        ctx2 = browser.new_context(viewport={'width': 1280, 'height': 900})
        page2 = ctx2.new_page()
        js_errors2 = attach(page2, ctx2, 'viewer', PERMS_VIEW)
        page2.goto('http://localhost:%d/index.html' % PORT)
        page2.wait_for_timeout(2500)
        page2.evaluate("navigateTo('work-schedule')")
        page2.wait_for_timeout(2500)
        btn2 = page2.evaluate("(function(){var b = document." +
              "getElementById('wsTalonsBtn'); return b ? {hidden: b.hidden} " +
              ": null;})()")
        check('E1: зритель — кнопка СКРЫТА', btn2 and
              btn2['hidden'] is True, btn2)
        page2.evaluate("navigateTo('ws-talons')")
        page2.wait_for_timeout(600)
        act = page2.evaluate("(function(){return {t: document." +
              "getElementById('page-ws-talons').classList.contains('active')," +
              "w: document.getElementById('page-work-schedule').classList." +
              "contains('active')};})()")
        check('E2: прямой URL — редирект в табель',
              act['t'] is False and act['w'] is True, act)
        check('G2: 0 JS-ошибок (зритель)', js_errors2 == [], js_errors2[:3])
        ctx2.close()

        print('=== kip8 SMOKE: мобайл 375 ===')
        ctx3 = browser.new_context(viewport={'width': 375, 'height': 812})
        page3 = ctx3.new_page()
        js_errors3 = attach(page3, ctx3, 'mobile', PERMS_EDIT)
        page3.goto('http://localhost:%d/index.html' % PORT)
        page3.wait_for_timeout(2500)
        page3.evaluate("navigateTo('work-schedule')")
        page3.wait_for_timeout(2500)
        page3.click('#wsTalonsBtn')
        page3.wait_for_timeout(1200)
        rows3 = row_days(page3)
        check('F1: мобайл — страница отчёта, явки 5/3/2',
              [r['days'] for r in rows3] == ['5', '3', '2'], rows3)
        scroll = page3.evaluate("(function(){var s = document." +
              "querySelector('#wsTalonsBody .wst-tscroll'); return s ? " +
              "getComputedStyle(s).overflowX : '';})()")
        check('F2: скролл-обёртка таблицы', scroll in ('auto', 'scroll'),
              scroll)
        page3.screenshot(path=OUT + '/02-kip8-mobile.png')
        check('G3: 0 JS-ошибок (мобайл)', js_errors3 == [], js_errors3[:3])
        ctx3.close()

        browser.close()

    print()
    print('ИТОГ: %d passed, %d failed' % (PASS, FAIL))
    if FAIL:
        raise SystemExit(1)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kw):
        super().__init__(*args, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    srv = HTTPServer(('127.0.0.1', PORT), Handler)
    import threading
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        main()
    finally:
        srv.shutdown()
