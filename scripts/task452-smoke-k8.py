#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 452: SMOKE kip8 (перенос из kip8test@27bad2d, SW kipia-v491).
# Заявка: «В разделе талоны, дни переработки должны учитываться при
# учёте количества дней явки и соответственно количества выданных
# талонов... у Чиркова в сентябре 2026 года стоят шесть 12 часовых
# смен, а в отчёте они не учлись... 7,2 и 8 это 8 часовые талоны,
# 12 это 12 часовые талоны.»
# Ключи kip8 БЕЗ префикса (нет isolateLocalStorage). Порт 8973.
#   A: страница «Талоны»: чипы 11/6, Чирков (дневной) t12=8/t8=3/
#      дней 11 (переработка учтена), Петров 0/3/3, Итого 11/6;
#   B: предпросмотр: Чирков ДВАЖДЫ (авто), 96/24 ч, ИТОГО 11/6;
#      PDF = 1 страница;
#   C: зритель — гейты; D: 0 JS-ошибок ×2.
import datetime
import json
import os
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8973
TODAY = datetime.date.today()
NOWY = TODAY.year
NOWM = TODAY.month
D = lambda day: '%04d-%02d-%02d' % (NOWY, NOWM, day)

SHOTS = '/home/z/my-project/download/kip8-task452-transfer'
os.makedirs(SHOTS, exist_ok=True)

EMPLOYEES = [
  {'таб_номер': '0231', 'ФИО': 'Чирков В. А.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 0, 'старт_цикла': '', 'дата_приёма': '2023-05-11',
   'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА 5 разряда', 'группа_допуска': 'IV',
   'комментарий': ''},
  {'таб_номер': '0871', 'ФИО': 'Федосов А. В.', 'тип': 'сменный', 'смена': 1,
   'шаблон_ротации': 1, 'старт_цикла': D(1), 'дата_приёма': '2024-03-15',
   'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА 5 разряда', 'группа_допуска': 'IV',
   'комментарий': ''},
  {'таб_номер': '0955', 'ФИО': 'Петров П. П.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 0, 'старт_цикла': '', 'дата_приёма': '2023-11-05',
   'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Электромонтёр 4 разряда', 'группа_допуска': 'III',
   'комментарий': ''},
]

CODES = [
  {'code': 'Д', 'name': 'День (12-час)', 'color': '#FFE0B2', 'short': 'день'},
  {'code': 'Н', 'name': 'Ночь (12-час)', 'color': '#B0BEC5', 'short': 'ночь'},
  {'code': 'Д8', 'name': 'День 8-час (7:30–16:30)', 'color': '#FFF9C4',
   'short': 'день 8ч'},
  {'code': 'д', 'name': 'Переработка день', 'color': '#FFCDD2',
   'short': 'перер. день'},
  {'code': '', 'name': 'Выходной', 'color': '#EEF0F2', 'short': 'выходной'},
]

ENTRIES = []
for i in range(1, 7):
    ENTRIES.append({'дата': D(i), 'таб_номер': '0231', 'статус': 'Д',
                    'переработка': 0, 'праздник': 0, 'источник': 'авто'})
for i in (7, 8):
    ENTRIES.append({'дата': D(i), 'таб_номер': '0231', 'статус': 'д',
                    'переработка': 1, 'праздник': 1, 'источник': 'руч',
                    'часы': 12})
for i in (9, 10, 11):
    ENTRIES.append({'дата': D(i), 'таб_номер': '0231', 'статус': 'Д8',
                    'переработка': 0, 'праздник': 0, 'источник': 'авто'})
for i in (1, 2, 3):
    ENTRIES.append({'дата': D(i), 'таб_номер': '0871', 'статус': 'Н',
                    'переработка': 0, 'праздник': 0, 'источник': 'авто'})
for i in (2, 3):
    ENTRIES.append({'дата': D(i), 'таб_номер': '0955', 'статус': 'Д8',
                    'переработка': 0, 'праздник': 0, 'источник': 'авто'})
ENTRIES.append({'дата': D(7), 'таб_номер': '0955', 'статус': 'д',
                'переработка': 1, 'праздник': 1, 'источник': 'руч',
                'часы': 8})

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
          (('  [' + str(extra)[:230] + ']') if (extra and not ok) else ''))


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
        return {'ok': True, 'data': {'entries': [dict(e) for e in ENTRIES]}}
    if action == 'prodCalendar.getMonth':
        return {'ok': True, 'data': {'workdays': 22, 'weekends': 8,
                'shortdays': 0, 'holidays': [], 'transfers': []}}
    return {'ok': True, 'data': {'ok': True}}


def attach(page, ctx, theme, tag, editor=True):
    js_errors = []
    page.on('pageerror', lambda e: js_errors.append(str(e)))
    page.on('dialog', lambda dlg: dlg.accept())
    # kip8: ключи БЕЗ префикса kip8test: (нет isolateLocalStorage)
    ctx.add_init_script(
        "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
        "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
        "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
        "localStorage.setItem('kip8_session_token','smoke-t452-%s');" % tag +
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
                      body='not found (t452k8-%s)' % tag)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)
    return js_errors


TALONS_JS = """(function(){
    var body = document.getElementById('wsTalonsBody');
    if (!body) return null;
    var chips = {};
    body.querySelectorAll('.wst-chip').forEach(function(ch){
        var t = ch.textContent.replace(/\\s+/g,' ').trim();
        var m = t.match(/^([^:]+):\\s*(.+)$/);
        if (m) chips[m[1]] = m[2];
    });
    var table = body.querySelector('.wst-table');
    var rows = [];
    if (table) {
        table.querySelectorAll('tbody tr').forEach(function(tr){
            var tds = tr.querySelectorAll('td');
            var byCat = {};
            tr.querySelectorAll('input[data-cat]').forEach(function(inp){
                byCat[inp.getAttribute('data-cat')] = inp.value;
            });
            rows.push({fio: tds[2].textContent.trim(),
                       days: tds[4].textContent.trim(), cats: byCat});
        });
    }
    var foot = table ? table.querySelectorAll('tfoot td') : [];
    var footVals = [];
    foot.forEach(function(td){ footVals.push(td.textContent.trim()); });
    return {chips: chips, rows: rows, foot: footVals};
})"""


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        print('=== kip8 SMOKE Task 452: десктоп (Админ, edit) ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        js_errors = attach(page, ctx, 'dark', 'desktop')
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2500)
        sw = page.evaluate("navigator.serviceWorker.getRegistration()" +
                           ".then(function(r){return r ? r.active ? " +
                           "r.active.scriptURL : '' : '';})")
        page.evaluate("WorkSchedule.openTalonsPage()")
        page.wait_for_timeout(1500)
        g = page.evaluate(TALONS_JS)
        check('A1: страница «Талоны» (kip8, ключи без префикса)',
              bool(g and g['rows']))
        if g:
            check('A2: чипы 12ч=11 / 8ч=6',
                  g['chips'].get('12 ч. талонов') == '11' and
                  g['chips'].get('8 ч. талонов') == '6', g['chips'])
            # алфавит: П < Ф < Ч — Чирков третий
            chir = g['rows'][2]
            check('A3: Чирков (дневной) t12=8/t8=3 — ОБЕ категории авто',
                  chir['cats'].get('t12') == '8' and
                  chir['cats'].get('t8') == '3', chir['cats'])
            check('A4: Чирков дней = 11 (переработка в днях явки)',
                  chir['days'] == '11', chir['days'])
            petr = g['rows'][0]
            check('A5: Петров t8=3/t12=0, дней 3',
                  petr['cats'].get('t8') == '3' and
                  petr['cats'].get('t12') == '0' and petr['days'] == '3',
                  petr)
            check('A6: Итого 11/6, ячейка дней ПУСТА',
                  g['foot'] == ['Итого', '', '11', '6'], g['foot'])
        page.screenshot(path=SHOTS + '/01-talons-k8.png')

        # B: предпросмотр + PDF
        page.click('.wst-print-btn')
        page.wait_for_timeout(1500)
        prev = page.evaluate("""(function(){
            var ov = document.getElementById('wsTalonsPrevModal');
            if (!ov) return null;
            var fr = ov.querySelector('iframe');
            return fr ? fr.srcdoc : '';
        })()""")
        check('B1: предпросмотр открыт', bool(prev))
        if prev:
            check('B2: Чирков ДВАЖДЫ (авто по дням)',
                  prev.count('Чирков В. А.') == 2, prev.count('Чирков В. А.'))
            check('B3: часы 96 (8×12) и 24 (3×8)',
                  '>96</td>' in prev and '>24</td>' in prev)
            import re as _re
            check('B4: ИТОГО 11/6 (шт.)',
                  _re.search(r'ИТОГО: 12 часовые</td><td class="wst-t-val">11</td>', prev)
                  is not None and
                  _re.search(r'8 часовые</td><td class="wst-t-val">6</td>', prev)
                  is not None)
            check('B5: «Слесарь по КИП и А» (должность без разряда)',
                  'Слесарь по КИП и А</td>' in prev and 'разряда' not in prev)
            with open(SHOTS + '/_standalone.html', 'w',
                      encoding='utf-8') as f:
                f.write(prev)
            pg = ctx.new_page()
            pg.goto('http://localhost:%d/_standalone.html' % PORT)
            pg.emulate_media(media='print')
            pg.pdf(path=SHOTS + '/k8-talons-a4.pdf', format='A4',
                   margin={'top': '12mm', 'bottom': '12mm',
                           'left': '10mm', 'right': '10mm'})
            pg.close()
            try:
                import pypdf
                n_pages = len(pypdf.PdfReader(SHOTS + '/k8-talons-a4.pdf').pages)
            except Exception as e:
                n_pages = 'pypdf error: %s' % e
            check('B6: PDF = РОВНО 1 страница A4', n_pages == 1, n_pages)
            page.screenshot(path=SHOTS + '/02-preview-k8.png')
        check('D1: 0 JS-ошибок (десктоп)', len(js_errors) == 0, js_errors[:3])
        ctx.close()

        print('=== kip8 SMOKE Task 452: зритель ===')
        ctx2 = browser.new_context(viewport={'width': 1280, 'height': 900})
        page2 = ctx2.new_page()
        js2 = attach(page2, ctx2, 'dark', 'viewer', editor=False)
        page2.goto('http://localhost:%d/index.html' % PORT)
        page2.wait_for_timeout(2500)
        page2.evaluate("navigateTo('work-schedule')")
        page2.wait_for_timeout(2000)
        page2.evaluate("navigateTo('ws-talons')")
        page2.wait_for_timeout(800)
        active = page2.evaluate("(function(){var p = document.getElementById(" +
                                "'page-ws-talons'); return p ? " +
                                "p.classList.contains('active') : false;})()")
        check('C1: зритель — редирект с «Талонов»', active is False)
        check('D2: 0 JS-ошибок (зритель)', len(js2) == 0, js2[:3])
        ctx2.close()
        browser.close()
    print('\n=== Итог SMOKE kip8: %d/%d ===' % (PASS, PASS + FAIL))
    return 0 if FAIL == 0 else 1


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        SimpleHTTPRequestHandler.end_headers(self)


if __name__ == '__main__':
    import threading
    os.chdir('/home/z/my-project/kip8')
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        code = main()
    finally:
        server.shutdown()
    raise SystemExit(code)
