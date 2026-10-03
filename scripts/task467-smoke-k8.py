#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 467: SMOKE переноса в kip8 (порт 8997, ключи localStorage БЕЗ
# префикса kip8test:): фикс окна предпросмотра печати списка
# мероприятий — лист НЕ смещён вправо за границу окна: iframe
# 794px (класс wsev-prev-frame), лист left≈0/right≤794 в viewport'е
# iframe, визуальные края в границах paper; свап значков 466 жив
# (печать слева 3/28, раскрытие в углу 3/3), кнопки диалога живы,
# 0 JS-ошибок.
import calendar
import datetime
import json
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8997
TODAY = datetime.date.today()
Y, M = TODAY.year, TODAY.month
DIM = calendar.monthrange(Y, M)[1]

SHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'download', 'kip8-task467')

def d(off):
    dd = max(1, min(DIM, TODAY.day + off))
    return '%04d-%02d-%02d' % (Y, M, dd)

CODES = [
  {'code': 'Д', 'name': 'День (12-час)', 'color': '#FFE082'},
  {'code': 'Н', 'name': 'Ночь (12-час)', 'color': '#B0BEC5'},
]
EMPLOYEES = [
  {'таб_номер': '017', 'ФИО': 'Иванов Иван Иванович', 'тип': 'сменный', 'смена': 1,
   'шаблон_ротации': 1, 'старт_цикла': '%04d-%02d-01' % (Y, M),
   'дата_приёма': '2024-03-15', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА', 'комментарий': ''},
  {'таб_номер': '023', 'ФИО': 'Петров Пётр Петрович', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 2, 'старт_цикла': '%04d-%02d-07' % (Y, M),
   'дата_приёма': '2025-01-20', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА', 'комментарий': ''},
]
PATTERNS = [
  {'id': 1, 'name': 'Сменный сутки/двое', 'cycle': 4, 'description': '',
   'days': [{'day': 1, 'status': 'Д'}, {'day': 2, 'status': 'Н'},
            {'day': 3, 'status': ''}, {'day': 4, 'status': ''}]},
]
ENTRIES = [
  {'id': 1, 'дата': d(-6), 'таб_номер': '017', 'статус': 'Д', 'источник': 'авто'},
]
TRAININGS = [
  {'id': 80, 'тема': 'Повторный инструктаж по охране труда', 'тип': 'инструктаж',
   'дата_начала': d(-12), 'дата_окончания': d(-12), 'таб_номер': '017', 'подразделение': ''},
  {'id': 81, 'тема': 'Обучение по новой редакции инструкций', 'тип': 'обучение',
   'дата_начала': d(-9), 'дата_окончания': d(-7), 'таб_номер': '018', 'подразделение': ''},
  {'id': 82, 'тема': 'Целевой инструктаж при допуске к работам повышенной опасности',
   'тип': 'инструктаж', 'дата_начала': d(-1), 'дата_окончания': d(1),
   'таб_номер': '023', 'подразделение': ''},
]
PPE = [
  {'id': 1, 'таб_номер': '017', 'наименование': 'Каска защитная',
   'дата_выдачи': d(-100), 'дата_окончания': d(4), 'состояние': ''},
]

def mock_response(action, body):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local', 'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'workschedule.view': True, 'workschedule.edit': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'workSchedule.getStatusCodes':
        return {'ok': True, 'data': {'codes': CODES}}
    if action == 'workSchedule.listEmployees':
        return {'ok': True, 'data': {'employees': EMPLOYEES}}
    if action == 'workSchedule.getPatterns':
        return {'ok': True, 'data': {'patterns': PATTERNS}}
    if action == 'workSchedule.listTrainings':
        return {'ok': True, 'data': {'trainings': TRAININGS}}
    if action == 'workSchedule.listPpe':
        return {'ok': True, 'data': {'ppe': PPE}}
    if action == 'workSchedule.listEntries':
        if body and body.get('month') == M:
            return {'ok': True, 'data': {'entries': ENTRIES}}
        return {'ok': True, 'data': {'entries': []}}
    if action == 'prodCalendar.getMonth':
        return {'ok': True, 'data': {'workdays': 22, 'weekends': 8, 'shortdays': 0,
                'holidays': [], 'transfers': []}}
    return {'ok': True, 'data': {'ok': True}}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


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
          (('  [' + str(extra)[:220] + ']') if (extra and not ok) else ''))


def main():
    server = HTTPServer(('127.0.0.1', PORT), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1600, 'height': 1000})
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        # kip8: ключи БЕЗ префикса kip8test:
        ctx.add_init_script(
            "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
            "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
            "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
            "localStorage.setItem('kip8_session_token','sm-k467');" +
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
            resp = mock_response(action, body)
            return route.fulfill(status=200,
                                 content_type='application/json; charset=utf-8',
                                 body=json.dumps(resp, ensure_ascii=False))

        ctx.route('**/exec?**', handle)
        ctx.route('**script.google.com/**', handle)
        ctx.route('**raw.githubusercontent.com/**', lambda r: r.fulfill(
            status=404, content_type='text/plain', body='nf'))
        ctx.route('**calendar.legalic.ru/**', lambda r: r.fulfill(
            status=404, content_type='text/plain', body='nf'))

        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(1600)

        print('== 1: свап значков 466 жив + диалог 467 ==')
        g = page.evaluate("""(() => {
            const el = document.getElementById('wsEventsPanel');
            const er = el.getBoundingClientRect();
            const b = el.querySelector('.ws-bar-exp');
            const pr = el.querySelector('.ws-bar-print');
            const br = b ? b.getBoundingClientRect() : null;
            const rr = pr ? pr.getBoundingClientRect() : null;
            return {hasB: !!b, hasP: !!pr,
                bTop: br ? +(br.top - er.top).toFixed(2) : null,
                bRight: br ? +(er.right - br.right).toFixed(2) : null,
                pTop: rr ? +(rr.top - er.top).toFixed(2) : null,
                pRight: rr ? +(er.right - rr.right).toFixed(2) : null,
                pW: rr ? +rr.width.toFixed(1) : null,
                pH: rr ? +rr.height.toFixed(1) : null,
                gap: (br && rr) ? +(br.left - rr.right).toFixed(2) : null};})()""")
        check('окно мероприятий: печать слева 3/28, раскрытие в углу 3/3 (466 жив)',
              g['hasB'] and g['hasP'] and g['bTop'] == 3 and g['bRight'] == 3 and
              g['pTop'] == 3 and g['pRight'] == 28 and g['pW'] == 22 and
              g['pH'] == 22 and g['gap'] == 3, g)

        page.click('#wsEventsPanel .ws-bar-print')
        page.wait_for_timeout(1200)
        st = page.evaluate("""(() => {
            const ov = document.getElementById('wsEventsPrevModal');
            if (!ov) return {open: false};
            const paper = ov.querySelector('.wspprev-paper');
            const frame = ov.querySelector('.wspprev-frame');
            const pr = paper.getBoundingClientRect();
            const doc = frame.contentDocument;
            const sheet = doc ? doc.getElementById('wsPrintSheet') : null;
            const sr = sheet ? sheet.getBoundingClientRect() : null;
            const m = frame.style.transform || '';
            let k = 1;
            const km = /scale\\\\(([0-9.]+)\\\\)/.exec(m);
            if (km) k = parseFloat(km[1]);
            const btns = [...ov.querySelectorAll('.wspprev-btn')]
                .map(b => b.textContent.trim());
            return {open: true, btns: btns,
                    cssW: getComputedStyle(frame).width,
                    clientW: frame.clientWidth,
                    paperW: +pr.width.toFixed(1),
                    paperL: +pr.left.toFixed(1), paperR: +pr.right.toFixed(1),
                    sheetL: sr ? +sr.left.toFixed(1) : null,
                    sheetR: sr ? +sr.right.toFixed(1) : null,
                    sheetW: sr ? +sr.width.toFixed(1) : null,
                    visR: sr ? +(pr.left + sr.right * k).toFixed(1) : null,
                    title: (doc && doc.querySelector('.wsev-title'))
                        ? doc.querySelector('.wsev-title').textContent.trim() : '',
                    inj: !!document.getElementById('wsEventsPrintStyle')};})()""")
        check('диалог открыт; кнопки 4 + лист «Мероприятия»',
              st['open'] and
              st['btns'] == ['Печать', 'Сохранить PDF', 'Сохранить Excel', 'Отмена'] and
              st['title'] == 'Мероприятия', st)
        check('ФИКС 467: iframe CSS 794px + viewport 794',
              st['cssW'] == '794px' and st['clientW'] == 794, st)
        check('ФИКС 467: лист left≈0, right≤795, ширина ~794',
              st['sheetL'] <= 2 and st['sheetR'] <= 795 and
              st['sheetW'] >= 788, st)
        check('ФИКС 467: визуальный правый край листа <= paper.right + 2',
              st['visR'] <= st['paperR'] + 2, st)
        check('paper == 794 (масштаб k=1 на широком вьюпорте)',
              abs(st['paperW'] - 794) <= 1.5, st)
        try:
            os.makedirs(SHOT_DIR, exist_ok=True)
            page.screenshot(path=os.path.join(SHOT_DIR, 'smoke-k8-preview.png'))
        except Exception as e:
            print('  (скриншот не сохранён: %s)' % e)

        print('== 2: закрытие, чистота ==')
        page.keyboard.press('Escape')
        page.wait_for_timeout(500)
        st2 = page.evaluate("""(() => ({
            dlg: !!document.getElementById('wsEventsPrevModal'),
            inj: !!document.getElementById('wsEventsPrintStyle')}))()""")
        check('Esc: диалог + инжект сняты', (not st2['dlg']) and (not st2['inj']), st2)
        check('0 JS-ошибок', not js_errors, js_errors[:3])
        browser.close()
    server.shutdown()
    print()
    print('ИТОГ: %d passed, %d failed' % (PASS, FAIL))
    raise SystemExit(0 if FAIL == 0 else 1)


if __name__ == '__main__':
    main()
