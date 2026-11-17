#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 553/554 — геометрическая проверка kip8 (повтор VLM-заметок):
# шапки карточек работника НЕ обрезаны, кнопки действий шапки
# (+ Отпуск… / + Мероприятие…) НЕ перекрывают заголовки. Сценарий
# тот же (работники 017, месяц 05/2026) — код мока как в
# task554-browser-check.py. Перенос ДЛИННЫХ СЛОВ по буквам в узких
# колонках — ПРЕЖНЕЕ поведение Task 415 (overflow-wrap), НЕ дефект.
import json
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8991
Y, M = 2026, 5
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
          (('  [' + str(extra)[:240] + ']') if (extra and not ok) else ''))


CODES = [
  {'code': 'Д', 'name': 'День (12-час)', 'color': '#FFE082'},
  {'code': 'Н', 'name': 'Ночь (12-час)', 'color': '#B0BEC5'},
]
EMPLOYEES = [
  {'таб_номер': '017', 'ФИО': 'Иванов Иван Иванович', 'тип': 'дневной',
   'смена': None, 'шаблон_ротации': None, 'старт_цикла': None,
   'дата_приёма': '2024-03-15', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Инженер КИПиА', 'комментарий': ''},
]
PATTERNS = [
  {'id': 1, 'name': 'Сменный сутки/двое', 'cycle': 4, 'description': '',
   'days': [{'day': 1, 'status': 'Д'}, {'day': 2, 'status': 'Н'},
            {'day': 3, 'status': ''}, {'day': 4, 'status': ''}]},
]
NOTE_101 = 'протокол № 12, ведёт Иванов А.А.'


def T(tid, tab, tip, tema, d, comment, done, late):
    return {'id': tid, 'таб_номер': tab, 'тип': tip, 'тема': tema,
            'дата_начала': d, 'дата_окончания': d,
            'длительность_дней': 1, 'комментарий': comment,
            'дата_проведения': d, 'выполнение': done, 'просрочен': late}


TRAININGS = [
  T(101, '017', 'инструктаж',
    'Повторный инструктаж по рабочим инструкциям ОТ',
    '2026-03-15', NOTE_101, 0, 0),
  T(102, '017', 'проверка_знаний',
    'Периодическая проверка знаний на допуск к самостоятельной работе',
    '2026-05-20', '', 0, 1),
]
INSTR_ALL = list(TRAININGS)
ENTRIES = []
VACATIONS = []
PPE = []


def mock_response(action, body):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local',
                                     'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'workschedule.view': True,
                                'workschedule.edit': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'workSchedule.getStatusCodes':
        return {'ok': True, 'data': {'codes': CODES}}
    if action == 'workSchedule.listEmployees':
        return {'ok': True, 'data': {'employees': EMPLOYEES}}
    if action == 'workSchedule.getPatterns':
        return {'ok': True, 'data': {'patterns': PATTERNS}}
    if action == 'workSchedule.listTrainings':
        return {'ok': True, 'data': {'trainings': TRAININGS,
                'instrList': [], 'instrAll': INSTR_ALL,
                'eventsAll': []}}
    if action == 'workSchedule.listPpe':
        return {'ok': True, 'data': {'ppe': PPE}}
    if action == 'workSchedule.listVacations':
        return {'ok': True, 'data': {'vacations': VACATIONS}}
    if action == 'workSchedule.listEntries':
        return {'ok': True, 'data': {'entries': ENTRIES}}
    if action == 'workSchedule.setTrainingDone':
        rid = int(body.get('id', 0) or 0)
        val = int(body.get('выполнение', 0) or 0)
        if rid == 101 and val == 1:
            return {'ok': True, 'data': {
                'id': 101, 'выполнение': 1, 'просрочен': 0,
                'srvVer': '554', 'autoNote': '',
                'created': [
                    {'id': 1021, 'таб_номер': '017', 'тип': 'инструктаж',
                     'тема': 'Повторный инструктаж по инструкции № 9-ОГЭ',
                     'дата_начала': '2026-06-15', 'дата_окончания': '2026-06-15',
                     'длительность_дней': 1, 'комментарий': NOTE_101,
                     'дата_проведения': '2026-06-15', 'выполнение': 0,
                     'просрочен': 0},
                    {'id': 1022, 'таб_номер': '017', 'тип': 'инструктаж',
                     'тема': 'Повторный инструктаж по рабочим инструкциям ОТ',
                     'дата_начала': '2026-09-15', 'дата_окончания': '2026-09-15',
                     'длительность_дней': 1, 'комментарий': NOTE_101,
                     'дата_проведения': '2026-09-15', 'выполнение': 0,
                     'просрочен': 0}
                ],
                'updated': [], 'skipped': []}}
        return {'ok': True, 'data': {'id': rid,
                'выполнение': val, 'просрочен': 0}}
    return {'ok': True, 'data': {'ok': True}}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


# Геометрия шапок ВСЕХ карточек работника: заголовки не обрезаны,
# кнопки не перекрывают заголовки и не вылезают за карточку
GEOM = """(() => {
    const cards = Array.from(document.querySelectorAll('.ws-wcard'));
    const out = [];
    cards.forEach(c => {
        const head = c.querySelector('.ws-whead');
        if (!head) return;
        const titles = Array.from(head.querySelectorAll('.ws-whead-t'));
        const btns = Array.from(head.querySelectorAll('.ws-whead-a'));
        const cr = c.getBoundingClientRect();
        titles.forEach(t => {
            const r = t.getBoundingClientRect();
            const clipped = (t.scrollHeight > t.clientHeight + 2) ||
                            (t.scrollWidth > t.clientWidth + 2);
            btns.forEach(b => {
                const br = b.getBoundingClientRect();
                const ov = Math.max(0, Math.min(r.right, br.right) -
                                    Math.max(r.left, br.left)) *
                           Math.max(0, Math.min(r.bottom, br.bottom) -
                                    Math.max(r.top, br.top));
                if (ov > 1) out.push({ head: t.textContent.trim().slice(0, 40),
                    btn: (b.textContent || '').trim().slice(0, 30),
                    overlap: Math.round(ov) });
            });
            if (clipped) out.push({ head: t.textContent.trim().slice(0, 40),
                                    clipped: true });
            const tr = t.getBoundingClientRect();
            if (tr.right > cr.right + 1 || tr.bottom > cr.bottom + 1)
                out.push({ head: t.textContent.trim().slice(0, 40),
                            outsideCard: true });
        });
        btns.forEach(b => {
            const br = b.getBoundingClientRect();
            if (br.right > cr.right + 1 || br.bottom > cr.bottom + 1)
                out.push({ btn: (b.textContent || '').trim().slice(0, 30),
                           outsideCard: true });
        });
    });
    return { cards: cards.length, issues: out };})()"""


def main():
    os.chdir(REPO)
    server = HTTPServer(('127.0.0.1', PORT), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda dg: dg.accept())
        ctx.add_init_script(
            "try{localStorage.clear()}catch(e){};" +
            "try{localStorage.setItem('kip8_session_token','bc-geom')}catch(e){};" +
            "try{localStorage.setItem('app-theme','dark')}catch(e){};")

        def handle(route, request):
            action = ''
            if 'action=' in request.url:
                action = unquote(request.url.split('action=')[1].split('&')[0])
            body = {}
            if request.post_data:
                try:
                    body = json.loads(request.post_data)
                except Exception:
                    body = {}
            return route.fulfill(status=200,
                content_type='application/json; charset=utf-8',
                body=json.dumps(mock_response(action, body), ensure_ascii=False))

        ctx.route('**/exec?**', handle)
        ctx.route('**script.google.com/**', handle)
        ctx.route('**raw.githubusercontent.com/**', lambda r: r.fulfill(
            status=404, content_type='text/plain', body='nf'))
        ctx.route('**calendar.legalic.ru/**', lambda r: r.fulfill(
            status=404, content_type='text/plain', body='nf'))
        ctx.route('**isdayoff.ru**', lambda r: r.fulfill(
            status=404, content_type='text/plain', body='nf'))

        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(1500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2500)
        page.select_option('#wsMonthSel', str(M))
        page.select_option('#wsYearSel', str(Y))
        page.wait_for_timeout(2000)

        page.click('#wsWorkersBtn')
        page.wait_for_timeout(900)
        page.evaluate("WorkSchedule.selectWorkersTab('017')")
        page.wait_for_timeout(700)

        print('== A: геометрия шапок карточек (до отметки) ==')
        geom = page.evaluate(GEOM)
        check('A: карточки отрисованы (>= 4)',
              (geom or {}).get('cards', 0) >= 4, geom)
        check('A: нет обрезанных заголовков / перекрытий кнопок',
              not (geom or {}).get('issues'), (geom or {}).get('issues'))

        # отметка выполнения → созданные записи → геометрия снова
        page.evaluate("""(() => {
            const rows = Array.from(
                document.querySelectorAll('.ws-wcard .ws-popup-row.ws-popup-event'));
            const row = rows.find(r =>
                (r.textContent || '').indexOf('15.03.2026') !== -1);
            const chk = row && row.querySelector('.ws-done-chk');
            if (chk) chk.click();
            return !!chk;})()""")
        page.wait_for_timeout(1200)

        print('== B: геометрия шапок карточек (после отметки — 3 примечания) ==')
        geom2 = page.evaluate(GEOM)
        check('B: нет обрезанных заголовков / перекрытий кнопок',
              not (geom2 or {}).get('issues'), (geom2 or {}).get('issues'))
        check('B: 0 JS-ошибок', not js_errors, js_errors[:3])

        browser.close()
        server.shutdown()

    print('\nИТОГО: %d/%d (pass/total), FAIL=%d' %
          (PASS, PASS + FAIL, FAIL))
    raise SystemExit(1 if FAIL else 0)


if __name__ == '__main__':
    main()
