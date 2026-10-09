#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 487-489 SMOKE (kip8) — перенос партии: проверки из
# kip8test browser-check 487/488/489, АДАПТАЦИЯ kip8: ключи
# localStorage БЕЗ префикса, порт 9002, + блок 0 СТАТИКА.
#   0) статика: SW kipia-v515 + перенос-метка «Task 487-489» +
#      3 комментария партии + де-изоляция + маркеры 487/488/489;
#   A) табель (487+488): КЛИК по И-ячейке (выполнено=1) — окно
#      мероприятий справочное: БЕЗ маркера ws-done-chk, БЕЗ кнопок
#      (✓/✎/✕), строка = свотч+код+название, подстрока дата·ФИО;
#      окно кодов открыто, кловер активен; десктоп-ХОВЕР (487):
#      окно БЕЗ клика, кловер тих; уход курсора закрыл (grace);
#      пустая ячейка ховером молчит; ПЗ-строка без маркера/кнопок;
#   B) «Работники» (489): сводка краткое; карточка — ПОЛНОЕ ФИО +
#      «Дата рождения» ПОСЛЕДНЯЯ (15.03.1985); легаси — краткое,
#      строки нет;
#   C) форма правки (489): Фамилия/Имя/Отчество/Дата рождения,
#      единое ФИО удалено, префилл частями;
#   D) добавить (489): поля живы и пусты;
#   E) «Скачать архив» (488+489): zip валиден, CT-first,
#      docProps, bookViews, 12 частей, защит нет; лист
#      «Работники» — ПОЛНОЕ ФИО (легаси краткое); «Отпуска» —
#      краткое. 0 JS-ошибок, скриншоты.
import calendar
import datetime
import json
import os
import re
import threading
import zipfile
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 9002
TODAY = datetime.date.today()
Y, M = TODAY.year, TODAY.month
DIM = calendar.monthrange(Y, M)[1]
REPO = '/home/z/my-project/kip8'
SHOT_DIR = os.path.join(os.path.dirname(REPO), 'download',
                        'kip8-task487-489-transfer')
os.makedirs(SHOT_DIR, exist_ok=True)

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


def shot(page, name):
    try:
        page.screenshot(path=os.path.join(SHOT_DIR, name))
    except Exception as e:
        print('  (скриншот %s не сохранён: %s)' % (name, e))


def d(off):
    dd = max(1, min(DIM, TODAY.day + off))
    return '%04d-%02d-%02d' % (Y, M, dd)


def dnum(off):
    return int(d(off).split('-')[2])


# --- Мок: сотрудники НОВОЙ раскладки (489) + тренинги (488) ---
CODES = [
  {'code': 'Д', 'name': 'День (12-час)', 'color': '#FFE082'},
  {'code': 'Н', 'name': 'Ночь (12-час)', 'color': '#B0BEC5'},
  {'code': 'И', 'name': 'Инструктаж', 'color': '#B3E5FC'},
  {'code': 'ОБ', 'name': 'Обучение', 'color': '#D1C4E9'},
  {'code': 'ПЗ', 'name': 'Проверка знаний', 'color': '#FFCDD2'},
]
EMPLOYEES = [
  {'таб_номер': '2741', 'ФИО': 'Хадасевич А. С.',
   'ФИО_полное': 'Хадасевич Александр Сергеевич',
   'фамилия': 'Хадасевич', 'имя': 'Александр', 'отчество': 'Сергеевич',
   'тип': 'сменный', 'смена': 1, 'шаблон_ротации': 1,
   'старт_цикла': '%04d-%02d-01' % (Y, M), 'дата_приёма': '2014-09-01',
   'дата_рождения': '1985-03-15', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА', 'комментарий': ''},
  {'таб_номер': '0292', 'ФИО': 'Чикризов Ю.',
   'тип': 'сменный', 'смена': 3, 'шаблон_ротации': 1,
   'старт_цикла': '%04d-%02d-02' % (Y, M), 'дата_приёма': '2020-08-03',
   'в_архиве': 0, 'должность': 'Слесарь КИПиА', 'комментарий': ''},
]
PATTERNS = [
  {'id': 1, 'name': 'Сменный сутки/двое', 'cycle': 4, 'description': '',
   'days': [{'day': 1, 'status': 'Д'}, {'day': 2, 'status': 'Н'},
            {'day': 3, 'status': ''}, {'day': 4, 'status': ''}]},
]
ENTRIES = [
  {'id': 1, 'дата': d(-6), 'таб_номер': '2741', 'статус': 'Д',
   'источник': 'авто'},
]
TRAININGS = [
  {'id': 100, 'тема': 'Повторный инструктаж по охране труда',
   'тип': 'инструктаж', 'дата_начала': d(-5), 'дата_окончания': d(-5),
   'таб_номер': '2741', 'подразделение': '', 'выполнение': 1,
   'просрочен': 0},
  {'id': 101, 'тема': 'Проверка знаний до 1000В', 'тип': 'проверка_знаний',
   'дата_начала': d(-3), 'дата_окончания': d(-3), 'таб_номер': '2741',
   'подразделение': '', 'выполнение': 0, 'просрочен': 1},
]
PPE = []
VACATIONS = [
  {'id': 21, 'таб_номер': '2741', 'часть': 1,
   'дата_начала': '%04d-%02d-05' % (Y, M),
   'дата_окончания': '%04d-%02d-14' % (Y, M),
   'дней': 10, 'комментарий': ''},
]


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
        return {'ok': True, 'data': {'trainings': TRAININGS}}
    if action == 'workSchedule.listPpe':
        return {'ok': True, 'data': {'ppe': PPE}}
    if action == 'workSchedule.listEntries':
        return {'ok': True, 'data': {'entries': ENTRIES}}
    if action == 'workSchedule.listVacations':
        return {'ok': True, 'data': {'vacations': VACATIONS}}
    return {'ok': True, 'data': {'ok': True}}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


POPUP_STATE_JS = r"""(() => {
    const evp = document.getElementById('wsEventsPopup');
    const pop = document.getElementById('wsCellPopup');
    const rows = evp ? [...evp.querySelectorAll('.ws-popup-row.ws-popup-event')] : [];
    return {
        active: !!(evp && evp.classList.contains('active')),
        codesActive: !!(pop && pop.classList.contains('active')),
        closerActive: !!(document.getElementById('wsPopupCloser') &&
            document.getElementById('wsPopupCloser').classList
                .contains('active')),
        sub: evp ? (evp.querySelector('.ws-events-sub') || {}).textContent
            || '' : '',
        rows: rows.map(r => ({
            code: r.querySelector('.ws-popup-code') ?
                  r.querySelector('.ws-popup-code').textContent.trim() : '',
            name: r.querySelector('.ws-popup-name') ?
                  r.querySelector('.ws-popup-name').textContent.trim() : '',
            hasChk: !!r.querySelector('.ws-done-chk'),
            anyChk: r.innerHTML.indexOf('ws-done-chk') !== -1,
            hasToggle: !!r.querySelector(
                '[onclick*="toggleTrainingDone"]'),
            hasEdit: !!r.querySelector('[title="Редактировать"]'),
            hasDel: !!r.querySelector('[title="Удалить"]'),
            swatch: !!r.querySelector('.ws-popup-swatch')
        }))};})"""

HOVERWIRED_JS = r"""(() => {
    const cells = [...document.querySelectorAll('#wsGridWrap td.ws-cell')];
    return {total: cells.length,
            enter: cells.filter(c => (c.getAttribute('onmouseenter') || '')
                .indexOf('onCellHover') !== -1).length,
            leave: cells.filter(c => (c.getAttribute('onmouseleave') || '')
                .indexOf('onCellLeave') !== -1).length};})"""

MARK_JS = r"""(([t, dn]) => {
    document.querySelectorAll('[data-testid="hc"]')
        .forEach(c => c.removeAttribute('data-testid'));
    const emp = document.querySelector('td.ws-emp-col[data-tab="' + t + '"]');
    const td = emp.closest('tr').querySelector('td[data-day="' + dn + '"]');
    td.setAttribute('data-testid', 'hc');
    return !!td;})"""

GRID_JS = r"""(() => {
    const cells = [...document.querySelectorAll('td.ws-emp-col')];
    return cells.map(c => c.textContent.trim().slice(0, 60));
})"""

CARD_JS = r"""(() => {
    const body = document.getElementById('wsWorkersBody');
    const card = body ? body.querySelector('.ws-wcard') : null;
    const head = card ? card.querySelector('.ws-whead-name') : null;
    const fields = card ? [...card.querySelectorAll('.ws-emp-field')] : [];
    const last = fields.length ? fields[fields.length - 1] : null;
    return {
        head: head ? head.textContent.trim() : '',
        fields: fields.map(f => ({
            k: f.querySelector('.ws-emp-k') ?
               f.querySelector('.ws-emp-k').textContent.trim() : '',
            v: f.querySelector('.ws-emp-v') ?
               f.querySelector('.ws-emp-v').textContent.trim() : ''
        })),
        lastK: last && last.querySelector('.ws-emp-k') ?
               last.querySelector('.ws-emp-k').textContent.trim() : ''
    };})"""

SUMMARY_JS = r"""(() => {
    const t = document.querySelector('.ws-wgen-table');
    if (!t) return {rows: 0, fio: []};
    return {
        rows: t.querySelectorAll('tbody tr').length,
        fio: [...t.querySelectorAll('tbody tr td.ws-wgen-fio')]
            .map(td => td.textContent.trim())
    };})"""

FORM_JS = r"""(() => {
    const g = id => { const e = document.getElementById(id);
        return e ? {live: true, value: e.value} : {live: false, value: ''}; };
    return {
        fam: g('wsEmpFam'), name: g('wsEmpName'), patr: g('wsEmpPatr'),
        birth: g('wsEmpBirth'), fio: g('wsEmpFio'),
        sheet: !!document.getElementById('wsEmpSheet')
    };})"""


def validate_xlsx(path):
    res = {}
    try:
        zf = zipfile.ZipFile(path)
        names = zf.namelist()
        res['zip_ok'] = True
        res['parts'] = len(names)
        res['parts_ok'] = (len(names) == 12)
        res['ct_first'] = (names[0] == '[Content_Types].xml')
        res['docprops'] = ('docProps/core.xml' in names and
                           'docProps/app.xml' in names)
        wb = zf.read('xl/workbook.xml').decode('utf-8')
        res['bookviews'] = ('<bookViews>' in wb)
        res['no_sheet_protect'] = all(
            'sheetProtection' not in zf.read(n).decode('utf-8', 'ignore')
            for n in names if n.startswith('xl/worksheets/'))
        rels = zf.read('xl/_rels/workbook.xml.rels').decode('utf-8')
        rmap = dict(re.findall(
            r'Id="(rId\d+)"[^>]*Target="(worksheets/[^"]+)"', rels))
        sheets = {}
        for m in re.finditer(
                r'<sheet[^>]*name="([^"]+)"[^>]*r:id="(rId\d+)"', wb):
            sheets[m.group(1)] = 'xl/' + rmap.get(m.group(2), '')
        res['sheets'] = sheets
    except Exception as e:
        res['error'] = str(e)
    return res


def sheet_text(path, sheet_file):
    zf = zipfile.ZipFile(path)
    xml = zf.read(sheet_file).decode('utf-8')
    return ''.join(re.findall(r'<t[^>]*>([^<]*)</t>', xml))


def open_grid(page):
    page.goto('http://localhost:%d/index.html' % PORT)
    page.wait_for_timeout(2500)
    page.evaluate("navigateTo('work-schedule')")
    page.wait_for_timeout(1800)
    page.wait_for_timeout(3500)   # 486: тихое обновление (4 с)


def setup_routes(ctx):
    def handle(route, request):
        action = ''
        if 'action=' in request.url:
            action = unquote(
                request.url.split('action=')[1].split('&')[0])
        body = {}
        if request.post_data:
            try:
                body = json.loads(request.post_data)
            except Exception:
                body = {}
        return route.fulfill(status=200,
            content_type='application/json; charset=utf-8',
            body=json.dumps(mock_response(action, body),
                            ensure_ascii=False))
    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    ctx.route('**raw.githubusercontent.com/**', lambda r: r.fulfill(
        status=404, content_type='text/plain', body='nf'))


def seed_ls():
    # kip8: ключи БЕЗ префикса (isolateLocalStorage отсутствует)
    return ("try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
            "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
            "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
            "localStorage.setItem('kip8_session_token','bc-t489');" +
            "localStorage.setItem('app-theme','dark');")


def main():
    os.chdir(REPO)

    # ==============================================================
    print('== 0: СТАТИКА переноса (файлы kip8) ==')
    sw = open('sw.js', encoding='utf-8').read()
    check('0: SW CACHE_VERSION = kipia-v515',
          "const CACHE_VERSION = 'kipia-v515';" in sw)
    check('0: SW перенос-метка «Task 487-489 (kip8test@58965654)»',
          '// Task 487-489 (перенос партии из kip8test@58965654):'
          in sw)
    check('0: SW kipia-v514 не осталось', 'kipia-v514' not in sw)
    check('0: SW комментарий 487 (окно справочное)',
          'Task 487: Табель — окно «Мероприятия в этот день»' in sw)
    check('0: SW комментарий 488 (маркер + xlsx)',
          'Task 488: (1) заявка «кнопка отметки осталась»' in sw and
          'простой редактируемый xlsx' in sw)
    check('0: SW комментарий 489 (ФИО + дата_рождения)',
          'Task 489: справочник «Сотрудники» (табель_КИП_ИОС)' in sw)
    check('0: персистентные кэши живы',
          "const IMAGE_CACHE_VERSION = 'kipia-images-v3';" in sw and
          "const DATA_CACHE_VERSION = 'kipia-data-v1';" in sw)
    idx = open('index.html', encoding='utf-8').read()
    check('0: index.html — ховер 487 (onCellHover/_openHoverPopup)',
          'onCellHover' in idx and '_openHoverPopup' in idx)
    check('0: index.html — xlsx 488 (_wsXlsDocProps)',
          '_wsXlsDocProps' in idx)
    check('0: index.html — сотрудники 489 (поля формы)',
          'wsEmpFam' in idx and 'wsEmpBirth' in idx and
          'wsEmpFio' not in idx.replace('wsEmpFioLegacy', 'X'))
    check('0: index.html — де-изоляция (DB_NAME kip8-cache-v1)',
          "var DB_NAME = 'kip8-cache-v1';" in idx and
          'isolateLocalStorage' not in idx)
    gs = open('scripts/WorkSchedule.gs', encoding='utf-8').read()
    check('0: WorkSchedule.gs — _employeesColMap + splitInit',
          '_employeesColMap' in gs and 'employeesSplitInit' in gs)

    server = HTTPServer(('127.0.0.1', PORT), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ==========================================================
        print('== A: табель — окно мероприятий (487+488) ==')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 720},
                                  accept_downloads=True)
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda dg: dg.accept())
        ctx.add_init_script(seed_ls())
        setup_routes(ctx)
        open_grid(page)

        wired = page.evaluate(HOVERWIRED_JS)
        check('A: все ячейки несут onmouseenter/onmouseleave',
              wired['total'] > 50 and wired['enter'] == wired['total']
              and wired['leave'] == wired['total'], wired)

        # A1: КЛИК по И-ячейке (выполнено=1) — оба окна, БЕЗ маркера
        page.evaluate(MARK_JS, ['2741', dnum(-5)])
        page.click('[data-testid="hc"]')
        page.wait_for_timeout(350)
        ps = page.evaluate(POPUP_STATE_JS)
        check('A: клик: окно мероприятий открыто', ps['active'], ps)
        check('A: клик: окно кодов открыто', ps['codesActive'], ps)
        check('A: клик: кловер активен', ps['closerActive'], ps)
        r_i = [r for r in ps['rows'] if r['code'] == 'И']
        check('A: строка И БЕЗ маркера ws-done-chk (заявка 488)',
              r_i and not r_i[0]['hasChk'] and not r_i[0]['anyChk'], ps)
        check('A: строка И БЕЗ кнопок (✓-клик/✎/✕)',
              r_i and not r_i[0]['hasToggle'] and not r_i[0]['hasEdit']
              and not r_i[0]['hasDel'], ps)
        check('A: строка И: свотч + код + название',
              r_i and r_i[0]['swatch'] and r_i[0]['code'] == 'И' and
              'инструктаж' in r_i[0]['name'].lower(), ps)
        check('A: подстрока «дата · ФИО» жива',
              'Хадасевич' in ps['sub'] and '.' in ps['sub'], ps['sub'])
        page.keyboard.press('Escape')
        page.wait_for_timeout(600)          # анти-дребезг 400 мс
        # УРОК 487: мышь после клика НЕПОДВИЖНА — page.hover по той
        # же точке событий НЕ даёт; увести и вернуть
        page.mouse.move(10, 300)
        page.wait_for_timeout(150)

        # A2: ХОВЕР (487) — окно БЕЗ клика, кловер тих
        page.evaluate(MARK_JS, ['2741', dnum(-5)])
        page.hover('[data-testid="hc"]')
        page.wait_for_timeout(300)
        ps1 = page.evaluate(POPUP_STATE_JS)
        check('A: ховер: окно открылось БЕЗ клика', ps1['active'], ps1)
        check('A: ховер: кловер НЕ активен', not ps1['closerActive'], ps1)
        r_i1 = [r for r in ps1['rows'] if r['code'] == 'И']
        check('A: ховер: строка И без маркера и кнопок',
              r_i1 and not r_i1[0]['hasChk'] and
              not r_i1[0]['hasToggle'] and not r_i1[0]['hasEdit'], ps1)
        shot(page, 'a-hover-popup.png')
        page.mouse.move(10, 300)
        page.wait_for_timeout(600)
        ps2 = page.evaluate(POPUP_STATE_JS)
        check('A: уход курсора: окно закрылось (grace 350 мс)',
              not ps2['active'], ps2)

        # A3: пустая ячейка — ховер молчит
        page.evaluate(MARK_JS, ['2741', dnum(10)])
        page.hover('[data-testid="hc"]')
        page.wait_for_timeout(300)
        ps3 = page.evaluate(POPUP_STATE_JS)
        check('A: пустая ячейка: ховер окно НЕ открывает',
              not ps3['active'], ps3)

        # A4: ПЗ-ячейка (не выполнено, просрочено) — без маркера
        page.evaluate(MARK_JS, ['2741', dnum(-3)])
        page.hover('[data-testid="hc"]')
        page.wait_for_timeout(300)
        ps4 = page.evaluate(POPUP_STATE_JS)
        r_pz = [r for r in ps4['rows'] if r['code'] == 'ПЗ']
        check('A: строка ПЗ без маркера и кнопок',
              r_pz and not r_pz[0]['hasChk'] and not r_pz[0]['hasToggle'],
              ps4)
        page.mouse.move(10, 300)
        page.wait_for_timeout(600)

        # A5: шахматка — ФИО КРАТКОЕ (489: полное НЕ в сетке)
        grid = page.evaluate(GRID_JS)
        check('A: шахматка: Хадасевич — КРАТКОЕ «Хадасевич А. С.»',
              any('Хадасевич А. С.' in g for g in grid), grid[:6])
        check('A: шахматка: ПОЛНОЕ имя НЕ показывается',
              not any('Александр Сергеевич' in g for g in grid))
        check('A: JS-ошибок нет (A)', not js_errors, js_errors[:4])
        shot(page, 'a-grid-short-fio.png')
        ctx.close()

        # ==========================================================
        print('== B-E: «Работники» (489) + архив (488) ==')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 720},
                                  accept_downloads=True)
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda dg: dg.accept())
        ctx.add_init_script(seed_ls())
        setup_routes(ctx)
        open_grid(page)

        try:
            page.click('#wsWorkersBtn', timeout=6000)
            page.wait_for_timeout(1600)
            summ = page.evaluate(SUMMARY_JS)
            check('B: сводка «Общая»: строки есть',
                  summ.get('rows', 0) >= 2, summ)
            check('B: сводка: ФИО КРАТКОЕ (полного нет)',
                  'Хадасевич А. С.' in summ.get('fio', []) and
                  'Хадасевич Александр Сергеевич' not in
                  summ.get('fio', []), summ)

            page.click('button[title="Хадасевич А. С."]', timeout=6000)
            page.wait_for_timeout(1200)
            card = page.evaluate(CARD_JS)
            check('B: карточка: шапка — ПОЛНОЕ ФИО',
                  card.get('head') ==
                  'Хадасевич Александр Сергеевич · таб. №2741',
                  card.get('head'))
            fields = card.get('fields', [])
            keys = [f['k'] for f in fields]
            check('B: «Дата рождения» — ПОСЛЕДНЯЯ строка профиля',
                  keys and keys[-1] == 'Дата рождения', keys)
            birth = [f for f in fields if f['k'] == 'Дата рождения']
            check('B: дата рождения дд.мм.гггг (15.03.1985)',
                  birth and birth[0]['v'] == '15.03.1985', fields)
            shot(page, 'b-card-full-fio-birth.png')

            page.click('button[title="Чикризов Ю."]', timeout=6000)
            page.wait_for_timeout(1200)
            card2 = page.evaluate(CARD_JS)
            check('B: легаси-карточка: краткое ФИО (фолбэк)',
                  card2.get('head') == 'Чикризов Ю. · таб. №0292',
                  card2.get('head'))
            keys2 = [f['k'] for f in card2.get('fields', [])]
            check('B: легаси: строки «Дата рождения» НЕТ',
                  'Дата рождения' not in keys2, keys2)
        except Exception as e:
            check('B: «Работники»: карточка', False, str(e))

        # C: форма правки — части + дата рождения
        try:
            page.click('button[title="Хадасевич А. С."]', timeout=6000)
            page.wait_for_timeout(1000)
            page.click('.ws-emp-editdata', timeout=6000)
            page.wait_for_timeout(900)
            form = page.evaluate(FORM_JS)
            check('C: поля Фамилия/Имя/Отчество живы',
                  form.get('fam', {}).get('live') and
                  form.get('name', {}).get('live') and
                  form.get('patr', {}).get('live'), form)
            check('C: поле «Дата рождения» живо',
                  form.get('birth', {}).get('live'), form)
            check('C: единое поле ФИО УДАЛЕНО',
                  not form.get('fio', {}).get('live'), form)
            check('C: префилл частями (Хадасевич/Александр/Сергеевич)',
                  form.get('fam', {}).get('value') == 'Хадасевич' and
                  form.get('name', {}).get('value') == 'Александр' and
                  form.get('patr', {}).get('value') == 'Сергеевич', form)
            check('C: префилл даты рождения = 1985-03-15',
                  form.get('birth', {}).get('value') == '1985-03-15',
                  form)
            shot(page, 'c-edit-form-parts.png')
            page.evaluate('WorkSchedule.closeEmployeeForm()')
            page.wait_for_timeout(500)
        except Exception as e:
            check('C: «Правка данных…»: форма', False, str(e))

        # D: добавить — поля живы и пусты
        try:
            page.click('button.ws-wtab-general', timeout=6000)
            page.wait_for_timeout(700)
            page.click('#wsWorkersAddBtn', timeout=6000)
            page.wait_for_timeout(900)
            form = page.evaluate(FORM_JS)
            check('D: ТРИ поля имени живы и ПУСТЫ',
                  form.get('fam', {}).get('live') and
                  form.get('fam', {}).get('value') == '' and
                  form.get('name', {}).get('value') == '' and
                  form.get('patr', {}).get('value') == '', form)
            check('D: поле «Дата рождения» живо и пусто',
                  form.get('birth', {}).get('live') and
                  form.get('birth', {}).get('value') == '', form)
            shot(page, 'd-add-form.png')
            page.evaluate('WorkSchedule.closeEmployeeForm()')
            page.wait_for_timeout(500)
        except Exception as e:
            check('D: «Добавить работника»', False, str(e))

        # E: архив — простой xlsx + лист «Работники» полное ФИО
        try:
            page.click('button.ws-wtab-general', timeout=6000)
            page.wait_for_timeout(700)
            btn = page.locator('#wsWorkersArchiveBtn')
            check('E: кнопка «Скачать архив» видна', btn.count() > 0)
            with page.expect_download(timeout=15000) as dl_info:
                btn.first.click()
            dl = dl_info.value
            path = os.path.join(SHOT_DIR, 'dl-archive.xlsx')
            dl.save_as(path)
            check('E: архив скачался с именем *.xlsx',
                  dl.suggested_filename.endswith('.xlsx'),
                  dl.suggested_filename)
            res = validate_xlsx(path)
            check('E: zip валиден', res.get('zip_ok'), res)
            check('E: CT — ПЕРВОЙ записью', res.get('ct_first'), res)
            check('E: docProps (core+app)', res.get('docprops'), res)
            check('E: bookViews', res.get('bookviews'), res)
            check('E: 12 частей', res.get('parts_ok'), res)
            check('E: защит листов НЕТ',
                  res.get('no_sheet_protect'), res)
            sheets = res.get('sheets', {})
            check('E: лист «Работники» в книге',
                  'Работники' in sheets, sheets)
            wtxt = sheet_text(path, sheets.get('Работники', ''))
            check('E: лист «Работники»: ПОЛНОЕ имя',
                  'Хадасевич Александр Сергеевич' in wtxt, wtxt[:200])
            check('E: лист «Работники»: краткое НЕ выгружается',
                  'Хадасевич А. С.' not in wtxt)
            check('E: лист «Работники»: легаси — как прежде краткое',
                  'Чикризов Ю.' in wtxt)
            vtxt = sheet_text(path, sheets.get('Отпуска', ''))
            check('E: лист «Отпуска»: КРАТКОЕ ФИО',
                  'Хадасевич А. С.' in vtxt, vtxt[:200])
            check('E: лист «Отпуска»: полное НЕ выгружается',
                  'Александр Сергеевич' not in vtxt)
            shot(page, 'e-workers-page.png')
        except Exception as e:
            check('E: архив: скачивание', False, str(e))

        check('JS-ошибок нет (B-E)', not js_errors, js_errors[:5])
        ctx.close()
        browser.close()

    print('\nИТОГ: %d passed, %d failed' % (PASS, FAIL))
    if FAIL:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
