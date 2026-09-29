#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 445 SMOKE (kip8 после переноса): вкладка «Общая» раздела
# «Работники» — 6 колонок, «Группа допуска» с датой проверки до
# 1000 В («IV от дд.мм.гггг»), кнопка «Скачать архив», скачивание
# .xlsx с ПЯТЬЮ листами, 0 JS-ошибок. Ключи kip8 — БЕЗ префикса
# kip8test:. Порт 8954, мок-сервер.
import datetime
import io
import json
import os
import re
import zipfile
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8954
TODAY = datetime.date.today()
TODAY_ISO = '%04d-%02d-%02d' % (TODAY.year, TODAY.month, TODAY.day)
NOWY = TODAY.year
D = lambda y, md: '%04d-%s' % (y, md)

EMPLOYEES = [
  {'таб_номер': '0871', 'ФИО': 'Федосов А. В.', 'тип': 'сменный', 'смена': 1,
   'шаблон_ротации': 1, 'старт_цикла': TODAY_ISO,
   'дата_приёма': '2024-03-15', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА 5 разряд', 'группа_допуска': 'IV',
   'комментарий': ''},
  {'таб_номер': '0955', 'ФИО': 'Петров П. П.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 0, 'старт_цикла': '',
   'дата_приёма': '2023-11-05', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Электромонтёр', 'группа_допуска': 'III',
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
INSTR_ALL = [
    {'id': 700, 'таб_номер': '0871', 'тип': 'проверка_знаний',
     'тема': 'Проверка знаний электроустановок до 1000 В',
     'дата_начала': D(NOWY, '03-15'), 'дата_окончания': D(NOWY, '03-15'),
     'длительность_дней': 1, 'комментарий': '',
     'дата_проведения': D(NOWY, '03-15'), 'выполнение': 1, 'просрочен': 0},
    {'id': 701, 'таб_номер': '0955', 'тип': 'инструктаж',
     'тема': 'Повторный инструктаж по охране труда',
     'дата_начала': D(NOWY - 1, '06-10'), 'дата_окончания': D(NOWY - 1, '06-10'),
     'длительность_дней': 1, 'комментарий': '',
     'дата_проведения': D(NOWY - 1, '06-10'), 'выполнение': 1, 'просрочен': 0},
]
EVENTS_ALL = [
    {'id': 801, 'таб_номер': '0871', 'тип': 'обучение',
     'тема': 'Курс по АСУ ТП',
     'дата_начала': D(NOWY, '09-03'), 'дата_окончания': D(NOWY, '09-05'),
     'длительность_дней': 3, 'комментарий': ''},
]
VAC_BY_YEAR = {
    NOWY: [
        {'id': 42, 'таб_номер': '0955', 'часть': 1,
         'дата_начала': D(NOWY, '06-01'), 'дата_окончания': D(NOWY, '06-10'),
         'дней': 10, 'комментарий': ''},
    ],
}
PPE = [
  {'id': 11, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд',
   'наименование': 'Фильтрующая коробка противогаза',
   'дата_выдачи': D(NOWY, '08-17'), 'дата_изготовления': D(NOWY - 2, '01-15'),
   'срок_годности': '2 года', 'дата_окончания': D(NOWY, '01-15'),
   'примечание': ''},
  {'id': 12, 'таб_номер': '0955', 'работник': 'Петров П. П.',
   'должность': 'Электромонтёр', 'наименование': 'Очки закрытые',
   'дата_выдачи': '', 'дата_изготовления': '',
   'срок_годности': 'До износа', 'дата_окончания': 'До износа',
   'примечание': ''},
]
PASS = 0
FAIL = 0
SHOTS = '/home/z/my-project/download/screenshots-task445'
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
    if action == 'workSchedule.listTrainings':
        return {'ok': True, 'data': {'trainings': [],
                'instrList': [], 'instrAll': [dict(r) for r in INSTR_ALL],
                'eventsAll': [dict(r) for r in EVENTS_ALL]}}
    if action == 'workSchedule.listVacations':
        year = body.get('year')
        year = int(year) if year else None
        return {'ok': True, 'data': {'vacations':
                [dict(v) for v in VAC_BY_YEAR.get(year, [])]}}
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
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900},
                                  accept_downloads=True)
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        # КЛЮЧИ kip8 — БЕЗ префикса kip8test:
        ctx.add_init_script(
            "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
            "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
            "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
            "localStorage.setItem('kip8_session_token','bc-t445k8');" +
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
            resp = api_response(action, body)
            return route.fulfill(status=200,
                                 content_type='application/json; charset=utf-8',
                                 body=json.dumps(resp, ensure_ascii=False))

        ctx.route('**/exec?**', handle)
        ctx.route('**script.google.com/**', handle)

        def block_external(route):
            route.fulfill(status=404, content_type='text/plain',
                          body='not found (t445k8)')
        ctx.route('**raw.githubusercontent.com/**', block_external)
        ctx.route('**calendar.legalic.ru/**', block_external)

        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2200)
        check('S1: приложение kip8 грузится, график открыт',
              page.evaluate("(function(){return !!document.querySelector(" +
              "'.ws-grid');})()"))

        page.click('#wsWorkersBtn')
        page.wait_for_timeout(1200)
        g = page.evaluate("""(function(){
            var body = document.getElementById('wsWorkersBody');
            var table = body ? body.querySelector('.ws-wgen-table') : null;
            var ths = table ? table.querySelectorAll('thead th') : [];
            var heads = [];
            for (var i = 0; i < ths.length; i++)
                heads.push(ths[i].textContent.trim());
            var btn = document.getElementById('wsWorkersArchiveBtn');
            var rows = table ? table.querySelectorAll('tbody tr') : [];
            var cells = [];
            for (var r = 0; r < rows.length; r++) {
                var tds = rows[r].querySelectorAll('td');
                var row = [];
                for (var c = 0; c < tds.length; c++)
                    row.push(tds[c].textContent.trim());
                cells.push(row);
            }
            return {heads: heads, cells: cells,
                    btnText: btn ? btn.textContent.trim() : ''};
        })()""")
        check('S2: «Общая» — 6 колонок (Отпуск/Мероприятия/Инструктажи нет)',
              g['heads'] == ['Таб. №', 'ФИО', 'Режим работы', 'Должность',
                             'Группа допуска', 'Дата приёма'], g['heads'])
        fed = next((r for r in g['cells'] if 'Федосов' in r[1]), [])
        petr = next((r for r in g['cells'] if 'Петров' in r[1]), [])
        check('S3: Федосов — «IV от 15.03.%d» (дата проверки справа)' % NOWY,
              fed[4] == 'IV от 15.03.%d' % NOWY, fed)
        check('S4: Петров — «III» без даты', petr[4] == 'III', petr)
        check('S5: кнопка «Скачать архив»', g['btnText'] == 'Скачать архив',
              g['btnText'])

        with page.expect_download(timeout=8000) as dl_info:
            page.click('#wsWorkersArchiveBtn')
        dl = dl_info.value
        fpath = SHOTS + '/kip8-' + dl.suggested_filename
        dl.save_as(fpath)
        with open(fpath, 'rb') as f:
            data = f.read()
        zf = zipfile.ZipFile(io.BytesIO(data))
        wbxml = zf.read('xl/workbook.xml').decode('utf-8')
        names = [m for m in re.findall(r'name="([^"]+)"', wbxml)]
        sheets = [n for n in names if n in
                  ('Работники', 'Отпуска', 'Инструктажи', 'СИЗ',
                   'Мероприятия')]
        check('S6: xlsx скачан, workbook — 5 листов по порядку',
              sheets == ['Работники', 'Отпуска', 'Инструктажи', 'СИЗ',
                         'Мероприятия'], sheets)
        s3 = zf.read('xl/worksheets/sheet3.xml').decode('utf-8')
        s4 = zf.read('xl/worksheets/sheet4.xml').decode('utf-8')
        check('S7: лист «Инструктажи» — проверка до 1000 В и прошлый год',
              ('15.03.%d' % NOWY) in s3 and
              ('10.06.%d' % (NOWY - 1)) in s3, 'даты не найдены')
        check('S8: лист «СИЗ» — «До износа» и коробка противогаза',
              'До износа' in s4 and
              'Фильтрующая коробка противогаза' in s4, 'СИЗ не найдены')
        page.screenshot(path=SHOTS + '/04-kip8-general.png')
        check('S9: 0 JS-ошибок', js_errors == [], js_errors[:3])
        ctx.close()
        browser.close()

    print('\n===== ИТОГ SMOKE kip8: %d OK / %d FAIL =====' % (PASS, FAIL))
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
