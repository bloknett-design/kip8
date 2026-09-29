#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 446 SMOKE (kip8 после переноса): листы Excel-архива
# Отпуска/Инструктажи/СИЗ/Мероприятия без колонок id/«Таб. №»,
# «Инструктажи» по фамилиям, зебра по группам строк, 0 JS-ошибок.
# Ключи kip8 — БЕЗ префикса kip8test:. Порт 8956, мок-сервер.
import datetime
import io
import json
import os
import re
import zipfile
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8956
ROOT = '/home/z/my-project/kip8'
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
  {'таб_номер': '0377', 'ФИО': 'Яковлев Я. Я.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': 0, 'старт_цикла': '',
   'дата_приёма': '2025-01-20', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Инженер КИПиА', 'группа_допуска': '',
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
# П(17) < Ф(22): Петров выше Федосова; Петров 702 — дата следующего
# года (фамилия первична); 703 — позапрошлый год (вне листа)
INSTR_ALL = [
    {'id': 700, 'таб_номер': '0871', 'тип': 'проверка_знаний',
     'тема': 'Проверка знаний до 1000 В',
     'дата_начала': D(NOWY, '03-15'), 'дата_окончания': D(NOWY, '03-15'),
     'длительность_дней': 1, 'комментарий': '',
     'дата_проведения': D(NOWY, '03-15'), 'выполнение': 1, 'просрочен': 0},
    {'id': 701, 'таб_номер': '0871', 'тип': 'инструктаж',
     'тема': 'Повторный инструктаж по охране труда',
     'дата_начала': D(NOWY - 1, '06-10'), 'дата_окончания': D(NOWY - 1, '06-10'),
     'длительность_дней': 1, 'комментарий': '',
     'дата_проведения': D(NOWY - 1, '06-10'), 'выполнение': 1, 'просрочен': 0},
    {'id': 702, 'таб_номер': '0955', 'тип': 'инструктаж',
     'тема': 'Повторный инструктаж по пожарной безопасности',
     'дата_начала': D(NOWY + 1, '03-02'), 'дата_окончания': D(NOWY + 1, '03-02'),
     'длительность_дней': 1, 'комментарий': 'план',
     'дата_проведения': D(NOWY + 1, '03-02'), 'выполнение': 0, 'просрочен': 0},
    {'id': 703, 'таб_номер': '0955', 'тип': 'инструктаж',
     'тема': 'Очень старый инструктаж',
     'дата_начала': D(NOWY - 2, '01-15'), 'дата_окончания': D(NOWY - 2, '01-15'),
     'длительность_дней': 1, 'комментарий': '',
     'дата_проведения': D(NOWY - 2, '01-15'), 'выполнение': 1, 'просрочен': 1},
]
INSTR_LIST = [
  {'название': 'Повторный инструктаж по охране труда', 'вид': 'инструктаж',
   'периодичность': 6, 'основание': '', 'сокращение': 'Инстр. ОТ'},
]
EVENTS_ALL = [
    {'id': 801, 'таб_номер': '0871', 'тип': 'обучение',
     'тема': 'Курс по АСУ ТП',
     'дата_начала': D(NOWY, '09-03'), 'дата_окончания': D(NOWY, '09-05'),
     'длительность_дней': 3, 'комментарий': 'центр'},
    {'id': 802, 'таб_номер': '0955', 'тип': 'прогул', 'тема': 'Прогул',
     'дата_начала': D(NOWY - 1, '05-05'), 'дата_окончания': D(NOWY - 1, '05-05'),
     'длительность_дней': 1, 'комментарий': ''},
    {'id': 803, 'таб_номер': '0377', 'тип': 'обучение',
     'тема': 'Обучение через границу года',
     'дата_начала': D(NOWY - 1, '12-29'), 'дата_окончания': D(NOWY, '01-05'),
     'длительность_дней': 8, 'комментарий': ''},
]
VAC_BY_YEAR = {
    NOWY - 1: [{'id': 41, 'таб_номер': '0871', 'часть': 1,
                'дата_начала': D(NOWY - 1, '07-01'),
                'дата_окончания': D(NOWY - 1, '07-14'),
                'дней': 14, 'комментарий': ''}],
    NOWY: [{'id': 42, 'таб_номер': '0955', 'часть': 1,
            'дата_начала': D(NOWY, '06-01'),
            'дата_окончания': D(NOWY, '06-10'),
            'дней': 10, 'комментарий': ''}],
}
PPE_STATE = [
  {'id': 11, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд',
   'наименование': 'Фильтрующая коробка противогаза',
   'дата_выдачи': D(NOWY, '08-17'), 'дата_изготовления': D(NOWY - 2, '01-15'),
   'срок_годности': '2 года', 'дата_окончания': D(NOWY, '01-15'),
   'примечание': 'банка №2'},
  {'id': 12, 'таб_номер': '0955', 'работник': 'Петров П. П.',
   'должность': 'Электромонтёр', 'наименование': 'Очки закрытые',
   'дата_выдачи': '', 'дата_изготовления': '',
   'срок_годности': 'До износа', 'дата_окончания': 'До износа',
   'примечание': ''},
]
PASS = 0
FAIL = 0
OUT = '/home/z/my-project/download/kip8-task446-transfer'
os.makedirs(OUT, exist_ok=True)


def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(('  + ' if ok else '  X ') + name +
          (('  [' + str(extra)[:220] + ']') if (extra and not ok) else ''))


def fresh_entries():
    out = []
    dim = (datetime.date(TODAY.year, TODAY.month % 12 + 1, 1) -
           datetime.timedelta(days=1)).day
    for day in range(1, dim + 1):
        iso_ = '%04d-%02d-%02d' % (TODAY.year, TODAY.month, day)
        if day <= 5:
            out.append({'дата': iso_, 'таб_номер': '0871', 'статус': 'Д8',
                        'переработка': 0, 'праздник': 0, 'источник': 'авто'})
    return out


ENTRIES = fresh_entries()


def api_response(action, body):
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
        return {'ok': True, 'data': {
            'trainings': [], 'instrList': [dict(x) for x in INSTR_LIST],
            'instrAll': [dict(r) for r in INSTR_ALL],
            'eventsAll': [dict(r) for r in EVENTS_ALL]}}
    if action == 'workSchedule.listVacations':
        year = body.get('year')
        year = int(year) if year else None
        vacs = VAC_BY_YEAR.get(year, []) if year else []
        return {'ok': True, 'data': {'vacations': [dict(v) for v in vacs]}}
    if action == 'workSchedule.listPpe':
        return {'ok': True, 'data': {'ppe': [dict(r) for r in PPE_STATE]}}
    if action == 'workSchedule.listEntries':
        return {'ok': True, 'data': {'entries': [dict(e) for e in ENTRIES]}}
    if action == 'prodCalendar.getMonth':
        return {'ok': True, 'data': {'workdays': 22, 'weekends': 8,
                'shortdays': 0, 'holidays': [], 'transfers': []}}
    return {'ok': True, 'data': {'ok': True}}


COLS = 'ABCDEFGH'


def parse_rows(xml):
    out = []
    for rm in re.finditer(r'<row r="(\d+)">(.*?)</row>', xml, re.S):
        cells = {}
        for cm in re.finditer(
                r'<c r="([A-Z]+)(\d+)"([^>]*?)(?:/>|>(.*?)</c>)',
                rm.group(2), re.S):
            col, attrs, inner = cm.group(1), cm.group(3), cm.group(4)
            m = re.search(r'<t[^>]*>([^<]*)</t>', inner or '')
            val = m.group(1) if m else None
            st = re.search(r's="(\d+)"', attrs)
            cells[col] = (val, st.group(1) if st else None)
        out.append((int(rm.group(1)), cells))
    return out


def sheet_report(zf, n):
    xml = zf.read('xl/worksheets/sheet%d.xml' % n).decode('utf-8')
    rows = parse_rows(xml)
    headers, names, fills, ncells = [], [], [], []
    ncols, person_col = 0, None
    for idx, (rnum, cells) in enumerate(rows):
        if idx == 0:
            for col in COLS:
                if col in cells:
                    headers.append(cells[col][0])
                    ncols += 1
                else:
                    break
            for ci, h in enumerate(headers):
                if h in ('ФИО', 'Работник'):
                    person_col = COLS[ci]
                    break
            continue
        fills.append(any(v[1] == '2' for v in cells.values()))
        ncells.append(len(cells))
        nm = cells.get(person_col) if person_col else None
        names.append((nm[0] if nm else None) or '')
    return dict(headers=headers, names=names, fills=fills, ncells=ncells,
                ncols=ncols, xml=xml)


def expected_zebra(nms):
    out, on, prev = [], True, None
    for nm in nms:
        if nm != prev:
            on = not on
            prev = nm
        out.append(on)
    return out


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
            "localStorage.setItem('kip8_session_token','bc-t446k8');" +
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
                          body='not found (t446k8)')
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
        check('S2: вкладка «Общая», кнопка «Скачать архив»',
              page.evaluate("(function(){var b = " +
              "document.getElementById('wsWorkersArchiveBtn'); return !!b &&" +
              " b.textContent.trim() === 'Скачать архив';})()"))

        with page.expect_download(timeout=8000) as dl_info:
            page.click('#wsWorkersArchiveBtn')
        dl = dl_info.value
        fpath = OUT + '/kip8-' + dl.suggested_filename
        dl.save_as(fpath)
        with open(fpath, 'rb') as f:
            zf = zipfile.ZipFile(io.BytesIO(f.read()))
        check('S3: скачан .xlsx (ZIP 10 частей)',
              re.match(r'^Архив_по_работникам_\d{4}-\d{2}-\d{2}\.xlsx$',
                       dl.suggested_filename) is not None and
              len(zf.namelist()) == 10, dl.suggested_filename)
        wbxml = zf.read('xl/workbook.xml').decode('utf-8')
        order = [m for m in re.findall(r'name="([^"]+)"', wbxml)]
        check('S4: workbook.xml — 5 листов по порядку',
              [n for n in order if n in ('Работники', 'Отпуска',
              'Инструктажи', 'СИЗ', 'Мероприятия')] ==
              ['Работники', 'Отпуска', 'Инструктажи', 'СИЗ', 'Мероприятия'])

        s1, s2 = sheet_report(zf, 1), sheet_report(zf, 2)
        s3, s4, s5 = sheet_report(zf, 3), sheet_report(zf, 4), sheet_report(zf, 5)
        check('S5: листы 2-5 БЕЗ id/«Таб. №» (работник — первой колонкой)',
              s2['headers'][0] == 'ФИО' and s3['headers'][0] == 'ФИО' and
              s4['headers'][0] == 'Работник' and s5['headers'][0] == 'ФИО' and
              all('id' not in r['headers'] and 'Таб. №' not in r['headers']
                  for r in (s2, s3, s4, s5)),
              (s2['headers'], s3['headers'], s4['headers'], s5['headers']))
        check('S6: лист «Работники» — «Таб. №» жив',
              s1['headers'][0] == 'Таб. №', s1['headers'])
        check('S7: «Инструктажи» — по фамилиям (Петров → Федосов×2)',
              s3['names'] == ['Петров П. П.', 'Федосов А. В.',
                              'Федосов А. В.'], s3['names'])
        for tag, rep in (('1 Работники', s1), ('2 Отпуска', s2),
                         ('3 Инструктажи', s3), ('4 СИЗ', s4),
                         ('5 Мероприятия', s5)):
            check('S8-%s: зебра групп по фамилиям' % tag,
                  rep['fills'] == expected_zebra(rep['names']),
                  (rep['names'], rep['fills']))
        check('S9: «СИЗ» — залитая строка Петрова: ВСЕ 8 ячеек (полоса '
              'без «дыр», пустое примечание — ячейка со стилем)',
              s4['fills'][1] and s4['ncells'][1] == 8,
              (s4['fills'], s4['ncells']))
        styles = zf.read('xl/styles.xml').decode('utf-8')
        check('S10: styles — fills 4 + FFF2F2F2 + cellXfs 3',
              '<fills count="4">' in styles and 'FFF2F2F2' in styles and
              '<cellXfs count="3">' in styles)
        page.wait_for_timeout(500)
        toast = page.evaluate(
            "document.getElementById('toastMessage') ? " +
            "document.getElementById('toastMessage').textContent : ''")
        check('S11: тост «Архив скачан — …»',
              toast.startswith('Архив скачан') and '3 инструктажа' in toast,
              toast)
        page.screenshot(path=OUT + '/01-kip8-archive.png')
        check('S12: 0 JS-ошибок', js_errors == [], js_errors[:3])
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
    os.chdir(ROOT)
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    import threading
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    try:
        code = main()
    finally:
        server.shutdown()
    raise SystemExit(code)
