#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 454: SMOKE kip8 (перенос из kip8test@b41be80, SW kipia-v493).
# Заявка: «В отчёте талонов ширину колонки "Должность" сделай по
# ширине большего текста в ней, что бы текст был в одну строку,
# ширину колонки "Ф.И.О" сделай по ширине колонки "Должность", а
# колонку "Роспись о получении" сделай уже на величину увеличения
# колонок "Ф.И.О" и "Должность". Высоту строк с работниками оставь
# шириной в две строки текста в них, а текст выравни по вертикали
# по центру.»
# Ключи kip8 БЕЗ префикса (нет isolateLocalStorage). Порт 8977.
#   A: приложение + «Талоны» (чипы 12ч=3 / 8ч=5);
#   B: ЗАЯВКА — предпросмотр: 6 инлайн-ширин равны (c3==c4 во всех
#      трёх сетках), c7 width:auto ×3, маркеры, ИТОГО 3/5;
#   C: standalone (file://): N в [87..188] и >= замера текста,
#      c3 == c4 == N, «Роспись» = остаток, все должности В ОДНУ
#      строку, высота = 2 строки текста, vertical-align middle;
#   D: PDF = 1 страница A4 с РЕАЛЬНОЙ формой (гвардия 404);
#   E: зритель — кнопка скрыта, URL — редирект;
#   F: 0 JS-ошибок ×2.
import datetime
import json
import os
import re
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8977
TODAY = datetime.date.today()
NOWY = TODAY.year
NOWM = TODAY.month
D = lambda day: '%04d-%02d-%02d' % (NOWY, NOWM, day)

SHOTS = '/home/z/my-project/download/kip8-task454-transfer'
os.makedirs(SHOTS, exist_ok=True)

# Как в browser-check 454: Чирков в обеих группах (t12=1/t8=3),
# Федосов сменный t12=2, Петров t8=2, Яковлев 0/0
EMPLOYEES = [
  {'таб_номер': '0231', 'ФИО': 'Чирков В. А.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 0, 'старт_цикла': '', 'дата_приёма': '2023-05-11',
   'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА 5 разряда', 'группа_допуска': 'IV',
   'комментарий': ''},
  {'таб_номер': '0871', 'ФИО': 'Федосов А. В.', 'тип': 'сменный', 'смена': 1,
   'шаблон_ротации': 1, 'старт_цикла': D(1), 'дата_приёма': '2024-03-15',
   'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Мастер по КИПиА', 'группа_допуска': 'IV',
   'комментарий': ''},
  {'таб_номер': '0955', 'ФИО': 'Петров П. П.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 0, 'старт_цикла': '', 'дата_приёма': '2023-11-05',
   'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Электромонтёр 4 разряда', 'группа_допуска': 'III',
   'комментарий': ''},
  {'таб_номер': '0377', 'ФИО': 'Яковлев Я. Я.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 0, 'старт_цикла': '', 'дата_приёма': '2025-01-20',
   'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Инженер КИПиА', 'группа_допуска': '',
   'комментарий': ''},
]

CODES = [
  {'code': 'Д', 'name': 'День (12-час)', 'color': '#FFE0B2', 'short': 'день'},
  {'code': 'Н', 'name': 'Ночь (12-час)', 'color': '#B0BEC5', 'short': 'ночь'},
  {'code': 'Д8', 'name': 'День 8-час (7:30–16:30)', 'color': '#FFF9C4',
   'short': 'день 8ч'},
]

ENTRIES = []
for i in (1, 2, 3):
    ENTRIES.append({'дата': D(i), 'таб_номер': '0231', 'статус': 'Д8',
                    'переработка': 0, 'праздник': 0, 'источник': 'авто'})
ENTRIES.append({'дата': D(4), 'таб_номер': '0231', 'статус': 'Д',
                'переработка': 0, 'праздник': 0, 'источник': 'авто'})
for i in (1, 2):
    ENTRIES.append({'дата': D(i), 'таб_номер': '0871', 'статус': 'Н',
                    'переработка': 0, 'праздник': 0, 'источник': 'авто'})
for i in (5, 6):
    ENTRIES.append({'дата': D(i), 'таб_номер': '0955', 'статус': 'Д8',
                    'переработка': 0, 'праздник': 0, 'источник': 'авто'})

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
        "localStorage.setItem('kip8_session_token','smoke-t454-%s');" % tag +
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
                      body='not found (t454k8-%s)' % tag)
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
    return {chips: chips};
})"""

PREV_JS = """(function(){
    var ov = document.getElementById('wsTalonsPrevModal');
    if (!ov) return null;
    var fr = ov.querySelector('iframe');
    return {srcdoc: fr ? fr.srcdoc : ''};
})"""

MEASURE_JS = """(function(){
    var out = {};
    var table = document.querySelector('table.wst-rep-table');
    if (!table) return null;
    out.tableW = Math.round(table.getBoundingClientRect().width * 10) / 10;
    var trs = table.querySelectorAll('tbody tr');
    var dataRow = null;
    for (var i = 0; i < trs.length; i++) {
        if (trs[i].className.indexOf('wst-r-group') === -1) {
            dataRow = trs[i]; break;
        }
    }
    if (!dataRow) return out;
    var tds = dataRow.querySelectorAll('td');
    out.cellW = [];
    for (var j = 0; j < tds.length; j++) {
        out.cellW.push(Math.round(tds[j].getBoundingClientRect().width * 10) / 10);
    }
    var cs = getComputedStyle(tds[0]);
    out.vAlign = cs.verticalAlign;
    out.tdH = Math.round(tds[0].getBoundingClientRect().height * 10) / 10;
    out.lineH = parseFloat(cs.lineHeight) || 0;
    out.pos = [];
    document.querySelectorAll('td.wst-r-pos').forEach(function(td){
        var range = document.createRange();
        range.selectNodeContents(td);
        var rects = range.getClientRects();
        var lines = 0;
        for (var k = 0; k < rects.length; k++) {
            if (rects[k].width > 1) lines++;
        }
        out.pos.push({t: td.textContent.trim(), lines: lines});
    });
    var cv = document.createElement('canvas');
    var ctx = cv.getContext('2d');
    ctx.font = '11pt Times New Roman, Times, serif';
    var m = 0;
    out.pos.forEach(function(p){
        var w = ctx.measureText(p.t).width;
        if (w > m) m = w;
    });
    out.valW = Math.round(m * 10) / 10;
    return out;
})"""


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # ===== десктоп 1280 светлая, Админ =====
        print('=== Контекст: десктоп светлая — динамическая сетка печати ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        js_errors = attach(page, ctx, 'light', 'desktop')
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2500)
        check('A1: приложение загрузилось, график открыт',
              page.evaluate("(function(){return !!document.querySelector(" +
              "'.ws-grid');})()"))
        page.click('#wsTalonsBtn')
        page.wait_for_timeout(1500)
        g = page.evaluate(TALONS_JS)
        check('A2: «Талоны»: чипы 12ч=3 / 8ч=5',
              bool(g and g['chips'].get('12 ч. талонов') == '3' and
              g['chips'].get('8 ч. талонов') == '5'),
              g['chips'] if g else None)
        page.screenshot(path=SHOTS + '/01-k8-talons.png')

        page.click('.wst-print-btn')
        page.wait_for_timeout(1500)
        prev = page.evaluate(PREV_JS)
        sd = prev['srcdoc'] if prev else ''
        check('B1: предпросмотр открыт, маркеры формы на месте',
              bool(sd) and all(s in sd for s in
              ['>ОТЧЕТ<', '>12 часовые<', '>8 часовые<',
               'Чирков В. А.', 'Слесарь по КИП и А']))
        widths = re.findall(r'style="width:(\d+)px"', sd)
        check('B2: 6 инлайн-ширин c3/c4 (три сетки), ВСЕ РАВНЫ',
              len(widths) == 6 and len(set(widths)) == 1, widths)
        check('B3: c7 «Роспись» = width:auto ×3',
              sd.count('style="width:auto"') == 3,
              sd.count('style="width:auto"'))
        check('B4: ИТОГО по группам: 12ч=3, 8ч=5',
              re.search(r'ИТОГО: 12 часовые</td><td class="wst-t-val">3</td>',
                        sd) is not None and
              re.search(r'8 часовые</td><td class="wst-t-val">5</td>',
                        sd) is not None)
        n_px = int(widths[0]) if widths else 0
        page.screenshot(path=SHOTS + '/02-k8-preview.png')
        page.click('.wspprev-cancel')
        page.wait_for_timeout(300)

        # standalone → замеры (file://, паттерн 449-451)
        with open(SHOTS + '/_standalone-k8.html', 'w',
                  encoding='utf-8') as f:
            f.write(sd)
        pg = ctx.new_page()
        pg.goto('file://' + SHOTS + '/_standalone-k8.html')
        pg.emulate_media(media='print')
        pg.wait_for_timeout(600)
        m = pg.evaluate(MEASURE_JS)
        check('C1: таблица замерена', bool(m and m.get('cellW')), m)
        if m and m.get('cellW'):
            check('C2: N в [87..188] и >= замера текста должностей',
                  87 <= n_px <= 188 and n_px >= m['valW'],
                  (n_px, m['valW']))
            check('C3: «Ф.И.О.» == «Должность» == N (±2px)',
                  abs(m['cellW'][2] - n_px) <= 2 and
                  abs(m['cellW'][3] - n_px) <= 2, (m['cellW'], n_px))
            check('C4: «Роспись» = ОСТАТОК сетки (±2px)',
                  abs(m['cellW'][6] - (m['tableW'] - sum(m['cellW'][0:6])))
                  <= 2, (m['cellW'], m['tableW']))
            check('C5: ВСЕ должности — В ОДНУ строку',
                  all(p['lines'] == 1 for p in m['pos']),
                  [(p['t'], p['lines']) for p in m['pos']])
            check('C6: высота строки = ДВЕ строки текста (2.5em, НЕ 6мм)',
                  m['tdH'] >= 2 * m['lineH'] and 36 <= m['tdH'] <= 45,
                  (m['tdH'], m['lineH']))
            check('C7: текст по вертикали ПО ЦЕНТРУ',
                  m['vAlign'] == 'middle', m['vAlign'])
        pg.pdf(path=SHOTS + '/k8-talons-a4.pdf', format='A4',
               margin={'top': '12mm', 'bottom': '12mm',
                       'left': '10mm', 'right': '10mm'})
        pg.close()
        try:
            import pypdf
            rd = pypdf.PdfReader(SHOTS + '/k8-talons-a4.pdf')
            n_pages = len(rd.pages)
            pdf_text = rd.pages[0].extract_text() or ''
        except Exception as e:
            n_pages = 'pypdf error: %s' % e
            pdf_text = ''
        check('D1: PDF = 1 страница A4 с РЕАЛЬНОЙ формой (гвардия 404)',
              n_pages == 1 and 'Наименование предприятия' in pdf_text and
              'Чирков' in pdf_text, (n_pages, pdf_text[:80]))
        check('F1: 0 JS-ошибок (десктоп)', len(js_errors) == 0, js_errors[:3])
        ctx.close()

        # ===== зритель =====
        print('=== Контекст: зритель — гейты ===')
        ctx2 = browser.new_context(viewport={'width': 1280, 'height': 900})
        page2 = ctx2.new_page()
        js2 = attach(page2, ctx2, 'dark', 'viewer', editor=False)
        page2.goto('http://localhost:%d/index.html' % PORT)
        page2.wait_for_timeout(2500)
        page2.evaluate("navigateTo('work-schedule')")
        page2.wait_for_timeout(2000)
        btn2 = page2.evaluate("(function(){var b = document.getElementById(" +
                              "'wsTalonsBtn'); return !b ? null : " +
                              "(b.offsetParent !== null);})()")
        check('E1: зрителю кнопка «Талоны» СКРЫТА',
              btn2 is False or btn2 is None, btn2)
        page2.evaluate("navigateTo('ws-talons')")
        page2.wait_for_timeout(800)
        active = page2.evaluate("(function(){var p = document.getElementById(" +
                                "'page-ws-talons'); return p ? " +
                                "p.classList.contains('active') : false;})()")
        check('E2: прямой URL — редирект, страница не активна',
              active is False)
        check('F2: 0 JS-ошибок (зритель)', len(js2) == 0, js2[:3])
        ctx2.close()

        browser.close()
    print('\n=== Итог: %d/%d (пас/фал) ===' % (PASS, PASS + FAIL))
    return 0 if FAIL == 0 else 1


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        SimpleHTTPRequestHandler.end_headers(self)


if __name__ == '__main__':
    import threading
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        code = main()
    finally:
        server.shutdown()
    raise SystemExit(code)
