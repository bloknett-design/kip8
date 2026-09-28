#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 441-transfer: SMOKE боевого kip8 после переноса партии 438-441
# (порт 8942, мок-сервер). Полная проверка партии — в kip8test
# (task438/439/440/441-browser-check.py, 39+41+49+26 проверок);
# здесь — что де-изоляция не сломала прод: приложение грузится,
# печать открывается, коды — ОДИН столбец, PDF/Excel скачиваются.
import datetime
import json
import os
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8942
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
  {'code': 'Д8', 'name': 'День 8ч', 'color': '#FFF9C4', 'short': 'день 8ч'},
  {'code': 'д', 'name': 'День в выходной', 'color': '#FFD54F',
   'short': 'день в выходной'},
  {'code': 'ОТ', 'name': 'Отпуск', 'color': '#ECEFF1', 'short': 'отпуск'},
  {'code': '', 'name': 'Выходной', 'color': '#EEF0F2', 'short': 'выходной'},
  {'code': 'И', 'name': 'Инструктаж', 'color': '#90CAF9',
   'short': 'инструктаж'},
]
PATTERNS = [
  {'id': 1, 'name': 'Сменный сутки/двое', 'cycle': 4, 'description': '',
   'days': [{'day': 1, 'status': 'Д'}, {'day': 2, 'status': 'Н'},
            {'day': 3, 'status': ''}, {'day': 4, 'status': ''}]},
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
SHOTS = '/home/z/my-project/download/screenshots-task441'
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
        return {'ok': True, 'data': {'patterns': PATTERNS}}
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
            "try{localStorage.clear();}catch(e){};"
            "localStorage.setItem('kip8_session_token','bc-t441k8');"
            "localStorage.setItem('app-theme','dark');")

        def handle(route, request):
            url = request.url
            action = ''
            if 'action=' in url:
                action = unquote(url.split('action=')[1].split('&')[0])
            resp = api_response(action)
            return route.fulfill(status=200,
                                 content_type='application/json; charset=utf-8',
                                 body=json.dumps(resp, ensure_ascii=False))

        ctx.route('**/exec?**', handle)
        ctx.route('**script.google.com/**', handle)
        ctx.route('**raw.githubusercontent.com/**',
                  lambda r: r.fulfill(status=404, body='nf'))
        ctx.route('**calendar.legalic.ru/**',
                  lambda r: r.fulfill(status=404, body='nf'))

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
        g = page.evaluate("""(function(){
            var ov = document.getElementById('wsPrintPrevModal');
            if (!ov) return null;
            var f = ov.querySelector('.wspprev-frame');
            try {
                var d = f.contentDocument;
                var sheet = d && d.getElementById('wsPrintSheet');
                if (!sheet) return null;
                var cols = sheet.querySelector('.wsp-legend-cols');
                var lgs = cols.querySelectorAll('.wsp-lg');
                var lefts = [];
                for (var i = 0; i < lgs.length; i++)
                    lefts.push(lgs[i].getBoundingClientRect().left);
                return {
                    tracks: d.defaultView.getComputedStyle(cols)
                        .gridTemplateColumns.split(' ').length,
                    n: lgs.length,
                    spread: lefts.length
                        ? Math.max.apply(null, lefts) -
                          Math.min.apply(null, lefts) : null
                };
            } catch (e) { return 'err'; }
        })()""")
        check('S3: kip8 — коды ОДНИМ столбцом (1 трек, разброс ≤1px)',
              g and g['tracks'] == 1 and g['spread'] <= 1 and g['n'] == 4,
              g)
        page.screenshot(path=SHOTS + '/04-kip8-print-onecol.png')
        try:
            with page.expect_download(timeout=30000) as dl_info:
                page.click('.wspprev-pdf')
            dl = dl_info.value
            pdf = '/tmp/t441-k8.pdf'
            dl.save_as(pdf)
            raw = open(pdf, 'rb').read()
            check('S4: kip8 — PDF скачан (%PDF-1.4, DCTDecode, 842×595)',
                  raw[:8] == b'%PDF-1.4' and b'/DCTDecode' in raw and
                  b'MediaBox [0 0 842 595]' in raw,
                  dl.suggested_filename)
        except Exception as e:
            check('S4: kip8 — PDF', False, str(e)[:200])
        try:
            with page.expect_download(timeout=30000) as dl_info:
                page.click('.wspprev-xlsx')
            dl = dl_info.value
            check('S5: kip8 — Excel скачан (.xlsx)',
                  dl.suggested_filename.endswith('.xlsx'),
                  dl.suggested_filename)
        except Exception as e:
            check('S5: kip8 — Excel', False, str(e)[:200])
        check('S6: kip8 — JS-ошибок нет', js_errors == [], js_errors[:3])
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
