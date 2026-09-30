#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 453: SMOKE kip8 (перенос из kip8test@c5aa312, SW kipia-v492).
# Заявка: «При попытке установки в ручную статуса "Выходной,
# плановый выходной день" появляется сообщение "Нельзя очистить
# авто-запись. Установите статус вручную.", хотя в таблице
# Коды_статусов этот статус есть, и остальные статусы из этой
# таблицы устанавливаются.»
# Ключи kip8 БЕЗ префикса (нет isolateLocalStorage). Порт 8975.
#   A: график; авто Д8 у Чиркова;
#   B: ЗАЯВКА — «Выходной» поверх авто: pending «.», тост-успех,
#      ячейка пустая с рамкой, «Сохранить (1)»;
#   C: undo — «Удалить запись» снимает правку, снова Д8;
#   D: повтор + «Сохранить» → setManualEntry «.», ячейка пустая
#      ручная; попап «Выходной» АКТИВНА;
#   E: старый сервер (unknown_статус) — тост-подсказка;
#   F: зритель — только окно мероприятий; 0 JS-ошибок ×2.
import datetime
import json
import os
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8975
TODAY = datetime.date.today()
NOWY = TODAY.year
NOWM = TODAY.month
D = lambda day: '%04d-%02d-%02d' % (NOWY, NOWM, day)
TAB = '0231'
DAY9 = D(9)
KEY9 = DAY9 + '|' + TAB
DAY10 = D(10)
KEY10 = DAY10 + '|' + TAB

SHOTS = '/home/z/my-project/download/kip8-task453-transfer'
os.makedirs(SHOTS, exist_ok=True)

EMPLOYEES = [
  {'таб_номер': TAB, 'ФИО': 'Чирков В. А.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 0, 'старт_цикла': '', 'дата_приёма': '2023-05-11',
   'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА 5 разряда', 'группа_допуска': 'IV',
   'комментарий': ''},
]

CODES = [
  {'code': 'Д', 'name': 'День (12-час)', 'color': '#FFE0B2', 'short': 'день'},
  {'code': 'Д8', 'name': 'День 8-час (7:30–16:30)', 'color': '#FFF9C4',
   'short': 'день 8ч'},
  {'code': '', 'name': 'Выходной, плановый выходной день',
   'color': '#EEF0F2', 'short': 'выходной'},
]

MOCK = {
    'entries': [
        {'дата': DAY9, 'таб_номер': TAB, 'статус': 'Д8',
         'переработка': 0, 'праздник': 0, 'источник': 'авто'},
        {'дата': DAY10, 'таб_номер': TAB, 'статус': 'Д8',
         'переработка': 0, 'праздник': 0, 'источник': 'авто'},
    ],
    'reject_dot': False,
    'set_calls': [],
}

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
        return {'ok': True, 'data': {'entries': [dict(e) for e in MOCK['entries']]}}
    if action == 'prodCalendar.getMonth':
        return {'ok': True, 'data': {'workdays': 22, 'weekends': 8,
                'shortdays': 0, 'holidays': [], 'transfers': []}}
    if action == 'workSchedule.setManualEntry':
        MOCK['set_calls'].append(dict(body))
        st = str(body.get('статус', ''))
        if st == '.' and MOCK['reject_dot']:
            return {'ok': False, 'error': 'unknown_статус: .'}
        key = str(body.get('date', '')) + '|' + str(body.get('таб_номер', ''))
        found = None
        for e in MOCK['entries']:
            if e['дата'] + '|' + e['таб_номер'] == key:
                found = e
                break
        rec = {'дата': str(body.get('date', '')),
               'таб_номер': str(body.get('таб_номер', '')),
               'статус': st, 'переработка': int(body.get('переработка') or 0),
               'праздник': 0, 'источник': 'руч',
               'часы': body.get('часы') if body.get('часы') else None}
        if found:
            found.update(rec)
        else:
            MOCK['entries'].append(rec)
        return {'ok': True, 'data': {'date': rec['дата'],
                'таб_номер': rec['таб_номер'], 'статус': st}}
    if action == 'workSchedule.deleteEntry':
        key = str(body.get('date', '')) + '|' + str(body.get('таб_номер', ''))
        MOCK['entries'] = [e for e in MOCK['entries']
                           if e['дата'] + '|' + e['таб_номер'] != key]
        return {'ok': True, 'data': {'ok': True}}
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
    js_errors = []
    page.on('pageerror', lambda e: js_errors.append(str(e)))
    page.on('dialog', lambda dlg: dlg.accept())
    # kip8: ключи БЕЗ префикса kip8test: (нет isolateLocalStorage)
    ctx.add_init_script(
        "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
        "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
        "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
        "localStorage.setItem('kip8_session_token','smoke-t453-%s');" % tag +
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
                      body='not found (t453k8-%s)' % tag)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)
    return js_errors


CELL9 = "td.ws-cell[onclick*=\"%s\"][onclick*=\"'%s'\"]" % (DAY9, TAB)
CELL10 = "td.ws-cell[onclick*=\"%s\"][onclick*=\"'%s'\"]" % (DAY10, TAB)
VYH_ROW = ".ws-cell-popup .ws-popup-row[onclick*=\"onPopupStatus('')\"]"
MORE_ROW = ".ws-cell-popup .ws-popup-row.ws-popup-more"


def cell_state(page):
    return page.evaluate(
        "(function(){var el=document.querySelector(%s);"
        "if(!el) return null;"
        "return {txt: el.textContent.replace(/\\s+/g,' ').trim(),"
        " pend: el.classList.contains('ws-pending'),"
        " dot: el.classList.contains('ws-dot-code'),"
        " manual: el.classList.contains('ws-source-manual')};})()"
        % json.dumps(CELL9))


def toasts(page):
    return page.evaluate("window.__toasts || []")


def main():
    srv = HTTPServer(('127.0.0.1', PORT), Handler)
    import threading
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # ===== десктоп 1280 светлая, Админ (edit) =====
        print('=== kip8: десктоп светлая — «Выходной» поверх авто ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        js_errors = attach(page, ctx, 'light', 'desktop')
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2500)
        page.evaluate(
            "window.__toasts=[];"
            "KipToast.show=(function(o){return function(m){"
            "window.__toasts.push(String(m)); try{o(m);}catch(e){}};"
            "})(KipToast.show);")

        check('A1: приложение загрузилось, график открыт',
              page.evaluate("(function(){return !!document.querySelector(" +
              "'.ws-grid');})()"))
        st0 = cell_state(page)
        check('A2: целевая ячейка — авто Д8', bool(st0) and
              st0['txt'] == 'Д8' and not st0['pend'], st0)

        # B: ЗАЯВКА
        page.click(CELL9)
        page.wait_for_timeout(400)
        rows = page.evaluate(
            "(function(){return document.querySelectorAll(%s).length;})()"
            % json.dumps(VYH_ROW))
        check('B1: строка «Выходной» в попапе — одна', rows == 1, rows)
        page.click(VYH_ROW)
        page.wait_for_timeout(600)
        t = toasts(page)
        check('B2: тост «Выходной поставлен поверх авто-записи…»',
              any('Выходной поставлен поверх авто-записи' in x for x in t), t)
        check('B3: НЕТ тоста «Нельзя очистить авто-запись»',
              not any('Нельзя очистить авто-запись' in x for x in t), t)
        p = page.evaluate(
            "(function(){var p=WorkSchedule._PENDING['%s'];"
            "return p?p['статус']:null;})()" % KEY9)
        check('B4: pending = «.»', p == '.', p)
        st1 = cell_state(page)
        check('B5: ячейка пустая с рамкой ws-pending',
              bool(st1) and st1['txt'] == '' and st1['pend'], st1)
        save = page.evaluate("(function(){var b=document.getElementById(" +
                             "'wsSaveBtn');return b?{h:b.hidden," +
                             "t:b.textContent}:null;})()")
        check('B6: «Сохранить (1)» видна',
              bool(save) and not save['h'] and save['t'] == 'Сохранить (1)',
              save)
        page.screenshot(path=SHOTS + '/k8-b-pending.png')

        # C: undo
        page.click(CELL9)
        page.wait_for_timeout(400)
        page.evaluate("(function(){var m=document.querySelectorAll(\"%s\");"
                      "for(var i=0;i<m.length;i++){"
                      "if(m[i].textContent.indexOf('Дополнительно')!==-1){"
                      "m[i].click();break;}}})()" % MORE_ROW)
        page.wait_for_timeout(700)
        page.click('#wsCellDelete')
        page.wait_for_timeout(500)
        t = toasts(page)
        check('C1: тост «Правка снята — снова авто-запись»',
              any('Правка снята — снова авто-запись' in x for x in t), t)
        st2 = cell_state(page)
        check('C2: снова авто Д8', bool(st2) and st2['txt'] == 'Д8', st2)

        # D: повтор + сохранение
        page.click(CELL9)
        page.wait_for_timeout(400)
        page.click(VYH_ROW)
        page.wait_for_timeout(500)
        page.click('#wsSaveBtn')
        page.wait_for_timeout(1800)
        calls = [c for c in MOCK['set_calls']
                 if c.get('статус') == '.' and c.get('date') == DAY9]
        check('D1: setManualEntry «.» вызван', len(calls) == 1,
              MOCK['set_calls'])
        st3 = cell_state(page)
        check('D2: ячейка пустая ручная «.» (без рамки)',
              bool(st3) and st3['txt'] == '' and not st3['pend'] and
              st3['dot'] and st3['manual'], st3)
        t = toasts(page)
        check('D3: «Сохранено записей: 1»',
              any('Сохранено записей: 1' in x for x in t), t)
        page.screenshot(path=SHOTS + '/k8-d-saved.png')

        # E: активность «Выходного» в попапе
        page.click(CELL9)
        page.wait_for_timeout(400)
        act = page.evaluate(
            "(function(){var r=document.querySelector(%s);"
            "return r?r.classList.contains('ws-popup-active'):null;})()"
            % json.dumps(VYH_ROW))
        check('E1: строка «Выходной» АКТИВНА (запись «.»)', act is True, act)

        # ---------- F: старый сервер отклоняет «.» (день 10, авто) ----------
        print('--- F: старый сервер — unknown_статус «.» ---')
        page.keyboard.press('Escape')
        page.wait_for_timeout(300)
        MOCK['reject_dot'] = True
        page.click(CELL10)
        page.wait_for_timeout(400)
        page.click(VYH_ROW)
        page.wait_for_timeout(500)
        p10 = page.evaluate(
            "(function(){var p=WorkSchedule._PENDING['%s'];"
            "return p?p['статус']:null;})()" % KEY10)
        check('F0: день 10 — pending «.» поверх авто', p10 == '.', p10)
        page.wait_for_selector('#wsSaveBtn:not([hidden])',
                               state='visible', timeout=5000)
        page.click('#wsSaveBtn')
        page.wait_for_timeout(1500)
        t = toasts(page)
        check('F1: тост-подсказка (WorkSchedule.gs / Коды_статусов)',
              any('не принят сервером' in x and 'WorkSchedule.gs' in x
                  for x in t), t)
        p10 = page.evaluate(
            "(function(){var p=WorkSchedule._PENDING['%s'];"
            "return p?p['статус']:null;})()" % KEY10)
        check('F2: правка «.» НЕ потеряна (в pending после отказа)',
              p10 == '.', p10)
        check('F3: 0 JS-ошибок (десктоп)', len(js_errors) == 0, js_errors)
        page.screenshot(path=SHOTS + '/k8-f-old-server.png')
        ctx.close()

        # ===== зритель =====
        print('=== kip8: зритель ===')
        ctx2 = browser.new_context(viewport={'width': 1280, 'height': 900})
        page2 = ctx2.new_page()
        js_errors2 = attach(page2, ctx2, 'light', 'viewer', editor=False)
        page2.goto('http://localhost:%d/index.html' % PORT)
        page2.wait_for_timeout(2500)
        page2.evaluate("navigateTo('work-schedule')")
        page2.wait_for_timeout(2500)
        page2.click(CELL9)
        page2.wait_for_timeout(500)
        gates = page2.evaluate(
            "(function(){var e=document.getElementById('wsEventsPopup');"
            "var c=document.getElementById('wsCellPopup');"
            "return {ev: e&&e.classList.contains('active'),"
            " codes: c&&c.classList.contains('active')};})()")
        check('G1: зрителю — только окно мероприятий',
              gates['ev'] is True and gates['codes'] is False, gates)
        check('G2: 0 JS-ошибок (зритель)', len(js_errors2) == 0, js_errors2)
        ctx2.close()
        browser.close()

    srv.shutdown()
    print('=' * 60)
    print('SMOKE TASK 453 kip8: %d/%d (порт %d)' % (PASS, PASS + FAIL, PORT))
    if FAIL:
        raise SystemExit(1)


if __name__ == '__main__':
    os.chdir('/home/z/my-project/kip8')
    main()
