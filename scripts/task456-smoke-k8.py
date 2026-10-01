#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 456 SMOKE (kip8): авто-«д»/«н» в шахматке — замещение
# отпуска сменного персонала (перенос из kip8test@712706d).
# Ключи kip8 БЕЗ префикса kip8test: (де-изоляция). Мок на порту
# 8981, 4 сменных работника (отпускник цикл 4 «Д Н В В» с «ОТ»
# весь месяц + 2 кандидата цикл 8 + 1 с иной фазой, записи
# плановых смен):
#   A — сетка/месяц, «ОТ» отпускника ≥ 20;
#   B — ЗАЯВКА: DOM ↔ модель _autoDnPlan 1:1 (ключи/тексты/фоны),
#       у отпускника авто нет, записи «Д» не тронуты, есть «д»+«н»;
#   C — попап «Авто… замещение отпуска…», Esc; правка «Д» поверх
#       авто: ws-pending, авто снят, план пересчитан, _PENDING;
#   D — зритель: авто-коды видны;
#   E — мобайл 375: авто на месте; 0 JS-ошибок ×3.
import calendar
import datetime
import json
import os
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8981
TODAY = datetime.date.today()
NOWY = TODAY.year
NOWM = TODAY.month
DIM = calendar.monthrange(NOWY, NOWM)[1]
MD = lambda y, m, d: '%04d-%02d-%02d' % (y, m, d)

TAB_A = '0441'
TAB_B = '0442'
TAB_C = '0443'
TAB_D = '0444'

SHOTS = '/home/z/my-project/download/kip8-task456-transfer'
os.makedirs(SHOTS, exist_ok=True)

PAT_A = {'id': 1, 'name': 'День/ночь 12ч (Д Н В В)', 'cycle': 4,
         'days': [{'day': 1, 'status': 'Д'}, {'day': 2, 'status': 'Н'},
                  {'day': 3, 'status': ''}, {'day': 4, 'status': ''}]}
PAT_BC = {'id': 2, 'name': 'Смена 8 дней (В В В Д Н В В В)', 'cycle': 8,
          'days': [{'day': 1, 'status': ''}, {'day': 2, 'status': ''},
                   {'day': 3, 'status': ''}, {'day': 4, 'status': 'Д'},
                   {'day': 5, 'status': 'Н'}, {'day': 6, 'status': ''},
                   {'day': 7, 'status': ''}, {'day': 8, 'status': ''}]}
START_A = datetime.date(2024, 1, 1)
START_BC = datetime.date(2024, 1, 1)
START_D = datetime.date(2024, 1, 3)

EMPLOYEES = [
  {'таб_номер': TAB_A, 'ФИО': 'Отпускников О. О.', 'тип': 'сменный',
   'смена': 1, 'шаблон_ротации': 1, 'старт_цикла': START_A.isoformat(),
   'дата_приёма': '2023-05-11', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА 5 разряда', 'группа_допуска': 'IV',
   'комментарий': ''},
  {'таб_номер': TAB_B, 'ФИО': 'Белов Б. Б.', 'тип': 'сменный',
   'смена': 2, 'шаблон_ротации': 2, 'старт_цикла': START_BC.isoformat(),
   'дата_приёма': '2022-02-01', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Электромонтёр 4 разряда', 'группа_допуска': 'III',
   'комментарий': ''},
  {'таб_номер': TAB_C, 'ФИО': 'Чернов Ч. Ч.', 'тип': 'сменный',
   'смена': 3, 'шаблон_ротации': 2, 'старт_цикла': START_BC.isoformat(),
   'дата_приёма': '2021-08-16', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Приборист 5 разряда', 'группа_допуска': 'IV',
   'комментарий': ''},
  {'таб_номер': TAB_D, 'ФИО': 'Дубов Д. Д.', 'тип': 'сменный',
   'смена': 4, 'шаблон_ротации': 2, 'старт_цикла': START_D.isoformat(),
   'дата_приёма': '2024-03-01', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Электрогазосварщик 4 разряда', 'группа_допуска': 'III',
   'комментарий': ''},
]

CODES = [
  {'code': 'Д8', 'name': 'День 8-час (7:30–16:30)', 'color': '#FFF9C4',
   'short': 'день 8ч'},
  {'code': 'Д', 'name': 'День (12-час, 7:30–19:30)', 'color': '#FFE082',
   'short': 'день 12ч'},
  {'code': 'Н', 'name': 'Ночь (12-час, 19:30–7:30)', 'color': '#B0BEC5',
   'short': 'ночь 12ч'},
  {'code': 'д', 'name': 'День в выходной/праздник (12ч, 7:30–19:30)',
   'color': '#FFD54F', 'short': 'день в выходной'},
  {'code': 'н', 'name': 'Ночь в выходной/праздник (12ч, 19:30–7:30)',
   'color': '#78909C', 'short': 'ночь в выходной'},
  {'code': 'ОТ', 'name': 'Отпуск', 'color': '#ECEFF1', 'short': 'отпуск'},
]


def E(date, tab, st):
    return {'дата': date, 'таб_номер': tab, 'статус': st,
            'переработка': 0, 'праздник': 0, 'источник': 'авто'}


def planned(date, emp):
    if emp['шаблон_ротации'] == 1:
        pat, start = PAT_A, START_A
    else:
        pat, start = PAT_BC, (START_D if emp['таб_номер'] == TAB_D
                              else START_BC)
    delta = (date - start).days
    if delta < 0:
        return ''
    doc = delta % pat['cycle'] + 1
    for d in pat['days']:
        if d['day'] == doc:
            return d['status']
    return ''


ENTRIES = []
for d in range(1, DIM + 1):
    dt = datetime.date(NOWY, NOWM, d)
    ENTRIES.append(E(dt.isoformat(), TAB_A, 'ОТ'))
    for emp in EMPLOYEES[1:]:
        st = planned(dt, emp)
        if st:
            ENTRIES.append(E(dt.isoformat(), emp['таб_номер'], st))

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
        return {'ok': True, 'data': {'patterns': [PAT_A, PAT_BC]}}
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
        "localStorage.setItem('kip8_session_token','sm-t456-%s');" % tag +
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
                      body='not found (t456k8-%s)' % tag)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)
    return js_errors


GRID_STATE_JS = (
    "(function(){"
    "var plan = (typeof WorkSchedule !== 'undefined' && WorkSchedule._autoDnPlan)"
    " ? WorkSchedule._autoDnPlan() : null;"
    "var cells = {}, styles = {};"
    "document.querySelectorAll('td.ws-cell.ws-auto-dn').forEach(function(td){"
    "var m = (td.getAttribute('onclick')||'').match(/'([^']+)','([^']+)'/);"
    "if (!m) return;"
    "var k = m[1] + '|' + m[2];"
    "cells[k] = (td.textContent || '').trim();"
    "styles[k] = td.getAttribute('style') || '';});"
    "var pending = Object.keys((WorkSchedule._PENDING)||{}).length;"
    "return {plan: plan, cells: cells, styles: styles,"
    " pending: pending};})()")


def main():
    srv = HTTPServer(('127.0.0.1', PORT), Handler)
    import threading
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        print('=== SMOKE kip8: десктоп светлая — авто-«д»/«н» (Task 456) ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        js_errors = attach(page, ctx, 'light', 'desktop')
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2500)

        check('A1: приложение загрузилось, шахматка открыта',
              page.evaluate("(function(){return !!document.querySelector(" +
              "'.ws-grid');})()"))
        msel = page.evaluate("(function(){var s=document.getElementById(" +
                             "'wsMonthSel');return s?parseInt(s.value,10):"
                             "null;})()")
        check('A2: сетка на текущем месяце (%d)' % NOWM, msel == NOWM, msel)
        check('A3: у отпускника дни «ОТ» (записи пришли)',
              page.evaluate(
                  "(function(){var n=0;"
                  "document.querySelectorAll('td.ws-cell').forEach(function(td){"
                  "var oc = td.getAttribute('onclick')||'';"
                  "if (oc.indexOf(\"'%s'\") !== -1 && " % TAB_A +
                  "td.textContent.indexOf('ОТ') !== -1) n++;});"
                  "return n;})()") >= 20,
              'записи «ОТ» отпускника в DOM')

        print('--- B (ЗАЯВКА): DOM ↔ модель _autoDnPlan ---')
        st = page.evaluate(GRID_STATE_JS)
        plan = st['plan']
        check('B1: план модели не пуст', plan and len(plan) >= 1, plan)
        if plan:
            check('B2: DOM-ячеек ws-auto-dn = плану',
                  len(st['cells']) == len(plan),
                  'dom=%s plan=%s' % (len(st['cells']), len(plan)))
            mism = [k for k in plan if st['cells'].get(k) != plan[k]]
            check('B3: текст каждой ячейки = код плана', not mism, mism[:4])
            no_bg = [k for k in st['styles']
                     if 'background' not in st['styles'][k]]
            check('B4: inline-фон у всех авто-ячеек', not no_bg, no_bg[:4])
            check('B5: у отпускника авто-кодов нет',
                  not [k for k in plan if k.endswith('|' + TAB_A)])
            vals = list(plan.values())
            check('B6: есть «д» и «н»', 'д' in vals and 'н' in vals,
                  {v: vals.count(v) for v in set(vals)})
        b_day = None
        for d in range(1, DIM + 1):
            dt = datetime.date(NOWY, NOWM, d)
            if planned(dt, EMPLOYEES[1]) == 'Д':
                b_day = dt
                break
        if b_day and plan:
            cell = page.evaluate(
                "(function(){var td = document.querySelector("
                "\"td.ws-cell[onclick*=\\'%s\\'][onclick*=\\'%s\\']\");" % (b_day.isoformat(), TAB_B) +
                "if (!td) return null;"
                "return {text: td.textContent.trim(),"
                "auto: td.classList.contains('ws-auto-dn')};})()")
            check('B7: рабочая запись «Д» Белова %s — без авто'
                  % b_day.isoformat(),
                  cell and cell['text'] == 'Д' and not cell['auto'], cell)
        page.screenshot(path=os.path.join(SHOTS, '01-k8-desktop-grid.png'))

        print('--- C: попап + правка поверх авто ---')
        if plan:
            first_key = sorted(plan.keys())[0]
            iso_d, tab_d = first_key.split('|')
            page.click("td.ws-cell[onclick*=\"%s\"][onclick*=\"%s\"]"
                       % (iso_d, tab_d))
            page.wait_for_timeout(600)
            auto_line = page.evaluate(
                "(function(){var e = document.querySelector("
                "'.ws-popup-auto');"
                "return e ? e.textContent.trim() : null;})()")
            check('C1: строка «Авто: «%s»… замещение отпуска…»'
                  % plan[first_key],
                  auto_line and 'Авто' in auto_line and
                  plan[first_key] in auto_line and
                  'замещение отпуска' in auto_line and
                  'в записи не сохранён' in auto_line, auto_line)
            page.screenshot(path=os.path.join(SHOTS, '02-k8-popup.png'))
            page.keyboard.press('Escape')
            page.wait_for_timeout(400)
            page.click("td.ws-cell[onclick*=\"%s\"][onclick*=\"%s\"]"
                       % (iso_d, tab_d))
            page.wait_for_timeout(600)
            page.click("div.ws-popup-row[onclick=\"WorkSchedule.onPopupStatus("
                       "'Д')\"]")
            page.wait_for_timeout(700)
            st2 = page.evaluate(GRID_STATE_JS)
            cell2 = page.evaluate(
                "(function(){var td = document.querySelector("
                "\"td.ws-cell[onclick*=\\'%s\\'][onclick*=\\'%s\\']\");" % (iso_d, tab_d) +
                "if (!td) return null;"
                "return {text: td.textContent.trim(),"
                "auto: td.classList.contains('ws-auto-dn'),"
                "pending: td.classList.contains('ws-pending')};})()")
            check('C2: правка «Д» поверх авто — ws-pending, авто снят',
                  cell2 and cell2['text'] == 'Д' and cell2['pending'] and
                  not cell2['auto'], cell2)
            check('C3: план пересчитан (ключа нет в _AUTO_DN)',
                  first_key not in (st2['plan'] or {}))
            check('C4: правка в _PENDING', st2['pending'] >= 1)
        check('G1: 0 JS-ошибок (десктоп)', not js_errors, js_errors[:4])
        ctx.close()

        print('=== SMOKE kip8: зритель ===')
        ctx2 = browser.new_context(viewport={'width': 1280, 'height': 900})
        page2 = ctx2.new_page()
        js_errors2 = attach(page2, ctx2, 'light', 'viewer', editor=False)
        page2.goto('http://localhost:%d/index.html' % PORT)
        page2.wait_for_timeout(2500)
        page2.evaluate("navigateTo('work-schedule')")
        page2.wait_for_timeout(2500)
        st3 = page2.evaluate(GRID_STATE_JS)
        check('D1: зритель: авто-ячейки есть',
              len(st3['cells']) >= 1, len(st3['cells']))
        check('D2: зритель: план модели == DOM',
              set(st3['cells'].keys()) == set((st3['plan'] or {}).keys()))
        page2.screenshot(path=os.path.join(SHOTS, '03-k8-viewer.png'))
        check('G2: 0 JS-ошибок (зритель)', not js_errors2, js_errors2[:4])
        ctx2.close()

        print('=== SMOKE kip8: мобайл 375 ===')
        ctx3 = browser.new_context(viewport={'width': 375, 'height': 720})
        page3 = ctx3.new_page()
        js_errors3 = attach(page3, ctx3, 'dark', 'mobile')
        page3.goto('http://localhost:%d/index.html' % PORT)
        page3.wait_for_timeout(2500)
        page3.evaluate("navigateTo('work-schedule')")
        page3.wait_for_timeout(2500)
        st4 = page3.evaluate(GRID_STATE_JS)
        check('E1: мобайл: авто-ячейки есть',
              len(st4['cells']) >= 1, len(st4['cells']))
        page3.screenshot(path=os.path.join(SHOTS, '04-k8-mobile.png'))
        check('G3: 0 JS-ошибок (мобайл)', not js_errors3, js_errors3[:4])
        ctx3.close()

        browser.close()

    print('\n═══════════════════════════════════════════')
    print('  Task 456 SMOKE kip8: %d passed, %d failed' % (PASS, FAIL))
    print('═══════════════════════════════════════════')
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
