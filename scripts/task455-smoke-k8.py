#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 455 SMOKE (kip8): месяц отчёта «Талонов» = МЕСЯЦ ОТКРЫТОЙ
# ШАХМАТКИ. Ключи kip8 БЕЗ префикса kip8test: (де-изоляция). Мок на
# порту 8979, записи ДВУХ месяцев:
#   A — сетка текущая; B — «Талоны» по текущему (без listEntries);
#   C — селект → прошлый месяц → отчёт по нему (шапка/значения/чипы);
#   D — предпросмотр «за <прошлый> <год> г.»; E — «Обновить данные»
#       → listEntries месяца сетки + тост; F — зритель (редирект);
#   G — мобайл 375 (месяц сетки через evaluate); 0 JS ×2.
import datetime
import json
import os
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8979
TODAY = datetime.date.today()
NOWY = TODAY.year
NOWM = TODAY.month
PM = NOWM - 1 if NOWM > 1 else 12
PMY = NOWY if NOWM > 1 else NOWY - 1
MD = lambda y, m, d: '%04d-%02d-%02d' % (y, m, d)
MONTHS = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
          'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
CUR_NAME = '%s %d г.' % (MONTHS[NOWM - 1], NOWY)
PM_NAME = '%s %d г.' % (MONTHS[PM - 1], PMY)

TAB_CH = '0231'   # Чирков, дневной
TAB_FD = '0871'   # Федосов, сменный

SHOTS = '/home/z/my-project/download/kip8-task455-transfer'
os.makedirs(SHOTS, exist_ok=True)

EMPLOYEES = [
  {'таб_номер': TAB_CH, 'ФИО': 'Чирков В. А.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 0, 'старт_цикла': '', 'дата_приёма': '2023-05-11',
   'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА 5 разряда', 'группа_допуска': 'IV',
   'комментарий': ''},
  {'таб_номер': TAB_FD, 'ФИО': 'Федосов А. С.', 'тип': 'сменный', 'смена': 3,
   'шаблон_ротации': 0, 'старт_цикла': '', 'дата_приёма': '2022-02-01',
   'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Электромонтёр 4 разряда', 'группа_допуска': 'III',
   'комментарий': ''},
]

CODES = [
  {'code': 'Д', 'name': 'День (12-час)', 'color': '#FFE0B2', 'short': 'день 12ч'},
  {'code': 'Д8', 'name': 'День 8-час (7:30–16:30)', 'color': '#FFF9C4',
   'short': 'день 8ч'},
  {'code': 'Н', 'name': 'Ночь (12-час)', 'color': '#C5E1F5', 'short': 'ночь'},
]


def E(date, tab, st):
    return {'дата': date, 'таб_номер': tab, 'статус': st,
            'переработка': 0, 'праздник': 0, 'источник': 'авто'}


ENTRIES = {
    (NOWY, NOWM): [
        E(MD(NOWY, NOWM, 1), TAB_CH, 'Д8'),
        E(MD(NOWY, NOWM, 2), TAB_CH, 'Д8'),          # Чирков: t8=2
        E(MD(NOWY, NOWM, 1), TAB_FD, 'Д'),           # Федосов: t12=1
    ],
    (PMY, PM): [
        E(MD(PMY, PM, 1), TAB_CH, 'Д8'),
        E(MD(PMY, PM, 2), TAB_CH, 'Д8'),
        E(MD(PMY, PM, 3), TAB_CH, 'Д8'),             # Чирков: t8=3
        E(MD(PMY, PM, 4), TAB_FD, 'Д'),
        E(MD(PMY, PM, 5), TAB_FD, 'Н'),              # Федосов: t12=2
    ],
}

MOCK = {'list_entries_calls': []}
PASS = 0
FAIL = 0


def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(('  + ' if ok else '  X ') + name +
          (('  [' + str(extra)[:250] + ']') if (extra and not ok) else ''))


def api_response(action, body, editor=True):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local',
                'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'calc.view': True, 'library.view': True,
                                'kipios.view': True,
                                'workschedule.view': True,
                                'workschedule.edit': editor,
                                'flowmeter.view': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'workSchedule.getStatusCodes':
        return {'ok': True, 'data': {'codes': CODES}}
    if action == 'workSchedule.listEmployees':
        return {'ok': True, 'data': {'employees': EMPLOYEES}}
    if action == 'workSchedule.getPatterns':
        return {'ok': True, 'data': {'patterns': []}}
    if action == 'workSchedule.listTrainings':
        return {'ok': True, 'data': {'trainings': [], 'instrList': [],
                'instrAll': [], 'eventsAll': []}}
    if action == 'workSchedule.listVacations':
        return {'ok': True, 'data': {'vacations': []}}
    if action == 'workSchedule.listPpe':
        return {'ok': True, 'data': {'ppe': []}}
    if action == 'workSchedule.listEntries':
        y = int(body.get('year') or NOWY)
        m = int(body.get('month') or NOWM)
        MOCK['list_entries_calls'].append({'year': y, 'month': m})
        return {'ok': True, 'data': {'entries':
                [dict(e) for e in ENTRIES.get((y, m), [])]}}
    if action == 'prodCalendar.getMonth':
        return {'ok': True, 'data': {'workdays': 22, 'weekends': 8,
                'shortdays': 0, 'holidays': [], 'transfers': []}}
    return {'ok': True, 'data': {'ok': True}}


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(length).decode('utf-8', 'replace') \
            if length else ''
        try:
            body = json.loads(raw) if raw else {}
        except Exception:
            body = {}
        action = ''
        if 'action=' in self.path:
            action = unquote(self.path.split('action=')[1].split('&')[0])
        resp = api_response(action, body)
        out = json.dumps(resp, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type',
                         'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)


def attach(page, ctx, theme, tag, editor=True):
    # kip8: ключи БЕЗ префикса kip8test: (де-изоляция переноса)
    js_errors = []
    page.on('pageerror', lambda e: js_errors.append(str(e)))
    page.on('dialog', lambda dlg: dlg.accept())
    ctx.add_init_script(
        "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
        "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
        "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
        "localStorage.setItem('kip8_session_token','sm-t455-%s');" % tag +
        "localStorage.setItem('app-theme','%s');" % theme)

    def handle(route, request):
        url = request.url
        action = ''
        if 'action=' in url:
            action = unquote(url.split('action=')[1].split('&')[0])
        pd_ = request.post_data
        body = None
        if pd_:
            try:
                body = json.loads(pd_)
            except Exception:
                body = None
        if body is None:
            body = {}
        resp = api_response(action, body, editor=editor)
        return route.fulfill(status=200,
                             content_type='application/json; charset=utf-8',
                             body=json.dumps(resp, ensure_ascii=False))

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)

    def block_external(route):
        route.fulfill(status=404, content_type='text/plain',
                      body='not found (t455k8-%s)' % tag)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)
    return js_errors


def hook_toasts(page):
    page.evaluate(
        "window.__toasts=[];"
        "KipToast.show=(function(o){return function(m){"
        "window.__toasts.push(String(m)); try{o(m);}catch(e){}};"
        "})(KipToast.show);")


def toasts(page):
    return page.evaluate("window.__toasts || []")


def report_state(page):
    return page.evaluate(
        "(function(){var t=document.querySelector('.wst-title');"
        "function val(tab,cat){var i=document.querySelector("
        "'input.wst-count[data-tab=\"'+tab+'\"][data-cat=\"'+cat+'\"]');"
        "return i?i.value:null;}"
        "function chip(id){var e=document.getElementById(id);"
        "return e?e.textContent:null;}"
        "return {title:t?t.textContent:'',"
        "ch8:val('" + TAB_CH + "','t8'),"
        "fd12:val('" + TAB_FD + "','t12'),"
        "t12:chip('wstTotalT12Chip'),t8:chip('wstTotalT8Chip')};})()")


def main():
    srv = HTTPServer(('127.0.0.1', PORT), Handler)
    import threading
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        print('=== SMOKE kip8: десктоп светлая ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        js_errors = attach(page, ctx, 'light', 'desktop')
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2500)
        hook_toasts(page)

        check('A1: график открыт',
              page.evaluate("(function(){return !!document.querySelector(" +
              "'.ws-grid');})()"))
        before = len(MOCK['list_entries_calls'])
        page.click('#wsTalonsBtn')
        page.wait_for_timeout(900)
        rs = report_state(page)
        check('B1: шапка — текущий месяц «%s»' % CUR_NAME,
              rs['title'].endswith(CUR_NAME), rs['title'])
        check('B2: значения текущего месяца (Чирков t8=2, Федосов t12=1)',
              rs['ch8'] == '2' and rs['fd12'] == '1', rs)
        check('B3: listEntries при открытии НЕ вызывался',
              len(MOCK['list_entries_calls']) == before)

        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(1200)
        if NOWM == 1:
            page.select_option('#wsYearSel', str(PMY))
            page.wait_for_timeout(1500)
        page.select_option('#wsMonthSel', str(PM))
        page.wait_for_timeout(2000)
        page.click('#wsTalonsBtn')
        page.wait_for_timeout(900)
        rs = report_state(page)
        check('C1: ЗАЯВКА — шапка «%s» (месяц сетки)' % PM_NAME,
              rs['title'].endswith(PM_NAME), rs['title'])
        check('C2: значения прошлого месяца (Чирков t8=3, Федосов t12=2)',
              rs['ch8'] == '3' and rs['fd12'] == '2', rs)
        check('C3: чипы 12ч=2 / 8ч=3 (прошлый месяц)',
              rs['t12'] == '2' and rs['t8'] == '3', rs)
        page.screenshot(path=SHOTS + '/01-k8-talons-prev-month.png',
                        full_page=True)

        page.click('.wst-print-btn')
        page.wait_for_timeout(1500)
        prev = page.evaluate(
            "(function(){var m=document.getElementById("
            "'wsTalonsPrevModal');if(!m) return null;"
            "var h=m.querySelector('.wspprev-sub');"
            "var f=m.querySelector('iframe.wspprev-frame');"
            "return {head:h?h.textContent:'',srcdoc:f?f.srcdoc:''};})()")
        check('D1: предпросмотр — шапка «%s»' % PM_NAME,
              bool(prev) and prev['head'].endswith(PM_NAME),
              prev and prev['head'])
        check('D2: форма — «за %s», текущий месяц НЕ упомянут' % PM_NAME,
              bool(prev) and ('за ' + PM_NAME) in prev['srcdoc'] and
              ('за ' + CUR_NAME) not in prev['srcdoc'])
        page.keyboard.press('Escape')
        page.wait_for_timeout(400)

        before = len(MOCK['list_entries_calls'])
        page.click('.wst-actions button.wst-btn:not(.wst-print-btn):not('
                   '#wstResetBtn)')
        page.wait_for_timeout(2000)
        calls = MOCK['list_entries_calls'][before:]
        check('E1: «Обновить данные» → listEntries месяца СЕТКИ (%d)' % PM,
              any(c['month'] == PM for c in calls), calls)
        t = toasts(page)
        check('E2: тост «Данные графика обновлены»',
              any('Данные графика обновлены' in x for x in t), t)
        check('G1: 0 JS-ошибок (десктоп)', not js_errors, js_errors[:3])
        ctx.close()

        print('=== SMOKE kip8: зритель ===')
        ctx2 = browser.new_context(viewport={'width': 1280, 'height': 900})
        page2 = ctx2.new_page()
        js_errors2 = attach(page2, ctx2, 'light', 'viewer', editor=False)
        page2.goto('http://localhost:%d/index.html' % PORT)
        page2.wait_for_timeout(2500)
        page2.evaluate("navigateTo('work-schedule')")
        page2.wait_for_timeout(2000)
        btn = page2.evaluate(
            "(function(){var b=document.getElementById('wsTalonsBtn');"
            "return b?b.hidden:null;})()")
        check('F1: кнопка «Талоны» скрыта у зрителя', btn is True, btn)
        page2.evaluate("navigateTo('ws-talons')")
        page2.wait_for_timeout(900)
        cur = page2.evaluate(
            "(function(){var el=document.querySelector("
            "'.page-content.active');return el?el.id:'';})()")
        check('F2: прямой URL ws-talons → редирект в табель',
              cur == 'page-work-schedule', cur)
        check('G2: 0 JS-ошибок (зритель)', not js_errors2, js_errors2[:3])
        ctx2.close()

        print('=== SMOKE kip8: мобайл 375 ===')
        ctx3 = browser.new_context(viewport={'width': 375, 'height': 812})
        page3 = ctx3.new_page()
        js_errors3 = attach(page3, ctx3, 'light', 'mobile')
        page3.goto('http://localhost:%d/index.html' % PORT)
        page3.wait_for_timeout(2500)
        page3.evaluate("navigateTo('work-schedule')")
        page3.wait_for_timeout(2000)
        page3.evaluate("WorkSchedule._month=%d;WorkSchedule._year=%d;"
                       "WorkSchedule.loadGrid()" % (PM, PMY))
        page3.wait_for_timeout(2000)
        page3.click('#wsTalonsBtn')
        page3.wait_for_timeout(900)
        rs3 = report_state(page3)
        check('H1: мобайл — шапка «%s» (месяц сетки)' % PM_NAME,
              rs3['title'].endswith(PM_NAME), rs3['title'])
        check('H2: значения прошлого месяца (t8=3 / t12=2)',
              rs3['ch8'] == '3' and rs3['fd12'] == '2', rs3)
        check('G3: 0 JS-ошибок (мобайл)', not js_errors3, js_errors3[:3])
        page3.screenshot(path=SHOTS + '/02-k8-mobile-prev-month.png',
                         full_page=True)
        ctx3.close()

        browser.close()

    print('=' * 60)
    print('ИТОГ Task 455 SMOKE kip8: %d OK, %d FAIL' % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == '__main__':
    raise SystemExit(main())
