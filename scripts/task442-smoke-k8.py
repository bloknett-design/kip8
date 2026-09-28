#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 442: SMOKE браузер kip8 после переноса (порт 8944) —
# приложение грузится, печать: без значков/столбца кодов, контур
# выходных, жирные даты; PDF/Excel скачивания; 0 JS-ошибок.
import datetime
import json
import os
import re
import zipfile
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8944
TODAY = datetime.date.today()
TODAY_ISO = '%04d-%02d-%02d' % (TODAY.year, TODAY.month, TODAY.day)

EMPLOYEES = [
  {'таб_номер': '0871', 'ФИО': 'Федосов А. В.', 'тип': 'сменный', 'смена': 1,
   'шаблон_ротации': 1, 'старт_цикла': TODAY_ISO,
   'дата_приёма': '2024-03-15', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА 5 разряд', 'группа_допуска': 'IV',
   'комментарий': ''},
]
CODES = [
  {'code': 'Д8', 'name': 'День, плановая дневная 8-часовая смена',
   'color': '#FFF9C4', 'short': 'день 8ч'},
  {'code': 'д', 'name': 'День, работа в выходные', 'color': '#FFD54F',
   'short': 'день в выходной'},
  {'code': 'ОТ', 'name': 'Отпуск', 'color': '#ECEFF1', 'short': 'отпуск'},
  {'code': '', 'name': 'Выходной, плановый выходной день',
   'color': '#EEF0F2', 'short': 'выходной'},
  {'code': 'И', 'name': 'Инструктаж', 'color': '#90CAF9',
   'short': 'инструктаж'},
]


def fresh_entries():
    out = []
    dim = (datetime.date(TODAY.year, TODAY.month % 12 + 1, 1) -
           datetime.timedelta(days=1)).day
    for day in range(1, dim + 1):
        iso_ = '%04d-%02d-%02d' % (TODAY.year, TODAY.month, day)
        if day <= 5:
            out.append({'дата': iso_, 'таб_номер': '0871', 'статус': 'Д8',
                        'переработка': 0, 'праздник': 0, 'источник': 'авто'})
        if day == 6:
            out.append({'дата': iso_, 'таб_номер': '0871', 'статус': 'д',
                        'переработка': 1, 'праздник': 0, 'источник': 'руч'})
        if day == 9:
            out.append({'дата': iso_, 'таб_номер': '0871', 'статус': 'ОТ',
                        'переработка': 0, 'праздник': 0, 'источник': 'руч'})
    return out


ENTRIES = fresh_entries()
INSTR = [
    {'id': 600, 'таб_номер': '0871', 'тип': 'инструктаж',
     'тема': 'Повторный инструктаж по охране труда',
     'дата_начала': TODAY_ISO, 'дата_окончания': TODAY_ISO,
     'длительность_дней': 1, 'комментарий': '',
     'дата_проведения': TODAY_ISO, 'выполнение': 1, 'просрочен': 0},
]

PASS = 0
FAIL = 0
SHOTS = '/home/z/my-project/download/screenshots-task442'
os.makedirs(SHOTS, exist_ok=True)


def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(('  + ' if ok else '  X ') + name +
          (('  [' + str(extra)[:200] + ']') if (extra and not ok) else ''))


def api_response(action):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local',
                'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'calc.view': True, 'library.view': True,
                                'kipios.view': True,
                                'workschedule.view': True,
                                'workschedule.edit': True,
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
        return {'ok': True, 'data': {
            'trainings': [dict(r) for r in INSTR], 'instrList': [],
            'instrAll': [dict(r) for r in INSTR], 'eventsAll': []}}
    if action == 'workSchedule.listVacations':
        return {'ok': True, 'data': {'vacations': []}}
    if action == 'workSchedule.listPpe':
        return {'ok': True, 'data': {'ppe': []}}
    if action == 'workSchedule.listEntries':
        return {'ok': True, 'data': {'entries': [dict(e) for e in ENTRIES]}}
    if action == 'prodCalendar.getMonth':
        return {'ok': True, 'data': {'workdays': 22, 'weekends': 8,
                'shortdays': 0, 'holidays': [], 'transfers': []}}
    return {'ok': True, 'data': {'ok': True}}


GEOM_JS = """(function(){
    var ov = document.getElementById('wsPrintPrevModal');
    if (!ov) return null;
    var f = ov.querySelector('.wspprev-frame');
    try {
        var d = f.contentDocument;
        var sheet = d && d.getElementById('wsPrintSheet');
        if (!sheet) return null;
        var cs = function(el){ return d.defaultView.getComputedStyle(el); };
        var ths = sheet.querySelectorAll('thead .wsp-day');
        var byDay = {};
        for (var i = 0; i < ths.length; i++)
            byDay[ths[i].textContent.replace(/[^0-9]/g, '')] = ths[i];
        var t5 = byDay['5'], t1 = byDay['1'];
        var rows = sheet.querySelectorAll('tbody tr');
        var cells = rows[rows.length - 1].querySelectorAll('td.wsp-cell');
        return {
            nLegend: sheet.querySelectorAll('.wsp-legend').length,
            nBadges: sheet.querySelectorAll('.wsp-ev').length,
            mev: !!sheet.querySelector('.wsp-mev'),
            satCls: t5 ? t5.className : '',
            satFw: t5 ? cs(t5).fontWeight : '',
            satBt: t5 ? cs(t5).borderTopWidth : '',
            dayFw: t1 ? cs(t1).fontWeight : '',
            cell5: cells[4] ? cells[4].className : '',
            cell5Bl: cells[4] ? cs(cells[4]).borderLeftWidth : ''
        };
    } catch (e) { return 'err: ' + e; }
})"""


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900},
                                  accept_downloads=True)
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda dlg: dlg.accept())
        ctx.add_init_script(
            "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
            "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
            "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
            "localStorage.setItem('kip8_session_token','bc-t442k8');" +
            "localStorage.setItem('app-theme','dark');")

        def handle(route, request):
            url = request.url
            action = ''
            if 'action=' in url:
                action = unquote(url.split('action=')[1].split('&')[0])
            resp = api_response(action)
            return route.fulfill(
                status=200, content_type='application/json; charset=utf-8',
                body=json.dumps(resp, ensure_ascii=False))

        ctx.route('**/exec?**', handle)
        ctx.route('**script.google.com/**', handle)

        def block_external(route):
            route.fulfill(status=404, content_type='text/plain',
                          body='not found')
        ctx.route('**raw.githubusercontent.com/**', block_external)
        ctx.route('**calendar.legalic.ru/**', block_external)

        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2500)
        check('S1: kip8 — график работы открыт',
              page.evaluate("(function(){return !!document.querySelector(" +
              "'.ws-grid');})()"))

        page.click('#wsPrintBtn')
        page.wait_for_timeout(1500)
        check('S2: диалог предпросмотра открыт',
              page.evaluate("!!document.getElementById('wsPrintPrevModal')"))
        page.wait_for_timeout(800)
        g = page.evaluate(GEOM_JS)
        check('S3: легенды кодов и бейджей НЕТ',
              g and g.get('nLegend') == 0 and g.get('nBadges') == 0, g)
        check('S4: мероприятия живы', g and g.get('mev'), g)
        check('S5: контур выходных (Сб 5-го: классы+верх 2px)',
              g and 'wsp-off-edge-l' in str(g.get('satCls')) and
              g.get('satBt') == '2px',
              (g and g.get('satCls'), g and g.get('satBt')))
        check('S6: даты: выходные 700 / будни 400',
              g and g.get('satFw') == '700' and g.get('dayFw') == '400',
              (g and g.get('satFw'), g and g.get('dayFw')))
        check('S7: тело — клетка Сб в полосе с краем 2px',
              g and 'wsp-cell-off' in str(g.get('cell5')) and
              g.get('cell5Bl') == '2px',
              (g and g.get('cell5'), g and g.get('cell5Bl')))
        page.screenshot(path=SHOTS + '/05-kip8-print.png')

        # PDF
        try:
            with page.expect_download(timeout=30000) as dl_info:
                page.click('.wspprev-pdf')
            dl = dl_info.value
            p = '/tmp/t442k8.pdf'
            dl.save_as(p)
            raw = open(p, 'rb').read()
            check('S8: PDF — %PDF-1.4 + DCTDecode + 842×595',
                  raw[:8] == b'%PDF-1.4' and b'/DCTDecode' in raw and
                  b'MediaBox [0 0 842 595]' in raw)
        except Exception as e:
            check('S8: PDF', False, str(e)[:180])

        # Excel
        try:
            with page.expect_download(timeout=30000) as dl_info:
                page.click('.wspprev-xlsx')
            dl = dl_info.value
            p = '/tmp/t442k8.xlsx'
            dl.save_as(p)
            z = zipfile.ZipFile(p)
            sheet = z.read('xl/worksheets/sheet1.xml').decode('utf-8')
            styles = z.read('xl/styles.xml').decode('utf-8')
            check('S9: Excel — «Коды:» нет, medium-контур, regDate',
                  '>Коды:<' not in sheet and
                  '<borders count="13">' in styles and
                  'FF8F99A3' in styles and '<fonts count="7">' in styles)
        except Exception as e:
            check('S9: Excel', False, str(e)[:180])

        check('S10: JS-ошибок нет', js_errors == [], js_errors[:3])
        ctx.close()
        browser.close()

    print('\n===== ИТОГ SMOKE kip8: %d OK / %d FAIL =====' % (PASS, FAIL))
    return 1 if FAIL else 0


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    import threading
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    try:
        code = main()
    finally:
        server.shutdown()
    raise SystemExit(code)
