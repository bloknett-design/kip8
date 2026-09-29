#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 443 SMOKE (kip8 после переноса): приложение kip8 грузится,
# карточка работника — блок СИЗ с «изгот.», шторка «+ СИЗ…» с полем
# «Дата изготовления» и ПРИОРИТОМ расчёта (изготовление + срок),
# submit уходит с дата_изготовления, 0 JS-ошибок. Ключи kip8 — БЕЗ
# префикса kip8test:. Порт 8947, мок-сервер.
import datetime
import json
import os
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8947
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
  {'code': 'Д8', 'name': 'День 8-час', 'color': '#FFF9C4', 'short': 'день 8ч'},
  {'code': '', 'name': 'Выходной', 'color': '#EEF0F2', 'short': 'выходной'},
]
PATTERNS = [
  {'id': 1, 'name': 'Сменный сутки/двое', 'cycle': 4, 'description': '',
   'days': [{'day': 1, 'status': 'Д'}, {'day': 2, 'status': 'Н'},
            {'day': 3, 'status': ''}, {'day': 4, 'status': ''}]},
]
PPE = [
  {'id': 11, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд',
   'наименование': 'Фильтрующая коробка противогаза',
   'дата_выдачи': '2026-08-17', 'дата_изготовления': '2025-01-15',
   'срок_годности': '2 года', 'дата_окончания': '2027-01-15',
   'примечание': 'банка №2'},
]
API_CALLS = []
PASS = 0
FAIL = 0
SHOTS = '/home/z/my-project/download/screenshots-task443'
os.makedirs(SHOTS, exist_ok=True)


def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(('  + ' if ok else '  X ') + name +
          (('  [' + str(extra)[:220] + ']') if (extra and not ok) else ''))


def api_response(action, body):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'u@t.l',
                'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'workschedule.view': True,
                                'workschedule.edit': True}}}
    if action == 'workSchedule.listEmployees':
        return {'ok': True, 'data': {'employees': EMPLOYEES}}
    if action == 'workSchedule.getPatterns':
        return {'ok': True, 'data': {'patterns': PATTERNS}}
    if action == 'workSchedule.getStatusCodes':
        return {'ok': True, 'data': {'codes': CODES}}
    if action == 'workSchedule.listPpe':
        return {'ok': True, 'data': {'ppe': [dict(r) for r in PPE]}}
    if action == 'workSchedule.addPpe':
        return {'ok': True, 'data': {'id': 99}}
    return {'ok': True, 'data': {'ok': True}}


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        ctx.add_init_script(
            "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
            "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
            "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
            "localStorage.setItem('kip8_session_token','bc-t443k8');" +
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
            if action.startswith('workSchedule.'):
                API_CALLS.append({'action': action, 'body': body})
            return route.fulfill(
                status=200, content_type='application/json; charset=utf-8',
                body=json.dumps(api_response(action, body),
                                ensure_ascii=False))
        ctx.route('**/exec?**', handle)
        ctx.route('**script.google.com/**', handle)
        ctx.route('**raw.githubusercontent.com/**',
                  lambda r: r.fulfill(status=404, body='x'))
        ctx.route('**calendar.legalic.ru/**',
                  lambda r: r.fulfill(status=404, body='x'))

        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2500)
        check('S1: kip8 грузится, график открыт',
              page.evaluate("(function(){return !!document.querySelector(" +
              "'.ws-grid');})()"))
        page.click('#wsWorkersBtn')
        page.wait_for_timeout(1000)
        page.click('button[title="Федосов А. В."]')
        page.wait_for_timeout(900)
        c = page.evaluate("""(function(){
            var txt = document.getElementById('wsWorkersBody').textContent || '';
            return { sec: txt.indexOf('СИЗ · средства индивидуальной защиты') !== -1,
                     izgot: txt.indexOf('изгот. 15.01.2025') !== -1,
                     till: txt.indexOf('до 15.01.2027') !== -1 };
        })()""")
        check('S2: блок СИЗ в карточке с «изгот. 15.01.2025» и «до 15.01.2027»',
              c['sec'] and c['izgot'] and c['till'], c)
        page.click('.ws-emp-addppe')
        page.wait_for_timeout(700)
        e = page.evaluate("""(function(){
            var mfg = document.getElementById('wsPpeManufactured');
            var issued = document.getElementById('wsPpeIssued');
            var term = document.getElementById('wsPpeTerm');
            return {
                open: document.getElementById('wsPpeSheet')
                    .classList.contains('active'),
                mfg: !!mfg, type: mfg ? mfg.type : '',
                order: !!(issued && mfg && term &&
                    issued.compareDocumentPosition(mfg) & 4 &&
                    mfg.compareDocumentPosition(term) & 4)
            };
        })()""")
        check('S3: шторка открыта, поле «Дата изготовления» (date) между '
              'датой выдачи и сроком',
              e['open'] and e['mfg'] and e['type'] == 'date' and e['order'], e)
        page.fill('#wsPpeName', 'Коробка запасная')
        page.fill('#wsPpeIssued', '2026-08-17')
        page.fill('#wsPpeManufactured', '2025-01-15')
        page.select_option('#wsPpeTerm', '2 года')
        page.wait_for_timeout(400)
        h = page.evaluate(
            "document.getElementById('wsPpeExpiryInfo').textContent")
        check('S4: ПРИОРИТЕТ — «15.01.2027 (от даты изготовления — '
              'заполнится автоматически)»',
              '15.01.2027' in h and 'от даты изготовления' in h, h)
        n_add = len([x for x in API_CALLS
                     if x['action'] == 'workSchedule.addPpe'])
        page.click('#wsPpeSubmitBtn')
        page.wait_for_timeout(1500)
        adds = [x for x in API_CALLS if x['action'] == 'workSchedule.addPpe']
        check('S5: addPpe с payload дата_изготовления=2025-01-15',
              len(adds) == n_add + 1 and
              adds[-1]['body'].get('дата_изготовления') == '2025-01-15',
              adds[-1]['body'] if adds else None)
        page.screenshot(path=SHOTS + '/05-kip8-ppe-443.png')
        check('S6: 0 JS-ошибок', js_errors == [], js_errors[:3])
        ctx.close()
        browser.close()
    print('\n===== SMOKE ИТОГ: %d OK / %d FAIL =====' % (PASS, FAIL))
    return 1 if FAIL else 0


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
