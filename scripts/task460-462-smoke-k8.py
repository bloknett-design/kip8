#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 460-462 SMOKE (kip8): перенос партии из kip8test@92d54d7 —
#   Task 460: раздел «Плановые мероприятия» (таблица образца);
#   Task 461: форма СИЗ — datalist #wsPpeNameList динамически;
#   Task 462: доступ к разделу по праву plan.events матрицы.
# Ключи kip8 БЕЗ префикса kip8test: (де-изоляция переноса).
# КОНТЕКСТ (мок-сервер, порт 8994):
#   A: «КИП ИОС», plan.events ✓ — кнопка на «Документации ИОС»,
#      страница, крошки, сайдбар, ТАБЛИЦА ОБРАЗЦА (шапка/группы/
#      8 мероприятий/96 пустых ячеек/рамки/зебра/закрепление);
#   B: «КИП ИОС», plan.events ✗ — ВСЁ скрыто, прямой переход →
#      «Нет доступа», хаб ЖИВ;
#   C: ПЕРЕХОДНЫЙ — матрица без колонки plan.events: раздел виден
#      (фоллбек Task 460);
#   D: легаси — сервер без getMyAccess: раздел виден по легаси-карте;
#   E: «КИП8» + plan.events ✓ (без КИП ИОС/расходомеров) — право
#      самодостаточно, хаба «Документация ИОС» нет;
#   F: Task 461 — «Работники» → карточка → «+ СИЗ»: datalist из 9
#      записей → РОВНО 5 уникальных (повторы/регистр/пробелы);
#   G: мобайл 375 — кнопка хаба открывает страницу, сетка шире
#      экрана (горизонтальный скролл);
#   0 JS-ошибок во всех контекстах; скриншоты в
#   download/kip8-task460-462-transfer/.
import datetime
import json
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8994
TODAY = datetime.date.today()
TODAY_ISO = '%04d-%02d-%02d' % (TODAY.year, TODAY.month, TODAY.day)
NOWY = TODAY.year

PASS = 0
FAIL = 0
SHOTS = '/home/z/my-project/download/kip8-task460-462-transfer'
os.makedirs(SHOTS, exist_ok=True)

MONTHS_SAMPLE = ['Янв.', 'Фев.', 'Мар.', 'Апр.', 'Май', 'Июн.',
                 'Июл.', 'Авг.', 'Сен.', 'Окт.', 'Ноя', 'Дек.']
GROUPS_SAMPLE = [
    ('В начале месяца', ['Проверка электроинструмента (приспособлений)',
                         'Проверка СИЗ в электроустановках',
                         'Проверка огнетушителей']),
    ('В конце месяца', ['График смен на следующий месяц',
                        'Отчёт по талонам',
                        'Выписка из ППР на следующий месяц',
                        'Журнал учёта электрооборудования',
                        'Отчёт по графику ППР']),
]
ALL_ACTS = GROUPS_SAMPLE[0][1] + GROUPS_SAMPLE[1][1]
EXPECTED_DYNAMIC = ['Ботинки', 'Каска защитная', 'Очки закрытые',
                    'Перчатки нитриловые', 'Противогаз']

# 2 работника; СИЗ 9 записей → 5 уникальных наименований (повторы
# каски ×3 у двух работников, перчатки в 2 регистрах, ботинки с
# пробелами, одно пустое наименование)
EMPLOYEES = [
  {'таб_номер': '0871', 'ФИО': 'Федосов А. В.', 'тип': 'сменный', 'смена': 1,
   'шаблон_ротации': 1, 'старт_цикла': TODAY_ISO,
   'дата_приёма': '2024-03-15', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА 5 разряд', 'группа_допуска': 'IV',
   'комментарий': ''},
  {'таб_номер': '0872', 'ФИО': 'Галкин Д. Н.', 'тип': 'дневной', 'смена': '',
   'шаблон_ротации': '', 'старт_цикла': '',
   'дата_приёма': '2025-01-20', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Мастер КИПиА', 'группа_допуска': 'IV',
   'комментарий': ''},
]

CODES = [
  {'code': 'Д8', 'name': 'День 8-час (7:30–16:30)', 'color': '#FFF9C4',
   'short': 'день 8ч'},
  {'code': '', 'name': 'Выходной', 'color': '#EEF0F2', 'short': 'выходной'},
]

PATTERNS = [
  {'id': 1, 'name': 'Сменный сутки/двое', 'cycle': 4, 'description': '',
   'days': [{'day': 1, 'status': 'Д'}, {'day': 2, 'status': 'Н'},
            {'day': 3, 'status': ''}, {'day': 4, 'status': ''}]},
]

PPE_STATE = [
  {'id': 11, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд', 'наименование': 'Каска защитная',
   'дата_выдачи': '2026-08-17', 'дата_изготовления': '',
   'срок_годности': '2 года', 'дата_окончания': '2028-08-17',
   'примечание': ''},
  {'id': 12, 'таб_номер': '0872', 'работник': 'Галкин Д. Н.',
   'должность': 'Мастер КИПиА', 'наименование': 'Каска защитная',
   'дата_выдачи': '2026-06-01', 'дата_изготовления': '',
   'срок_годности': '2 года', 'дата_окончания': '2028-06-01',
   'примечание': ''},
  {'id': 13, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд', 'наименование': 'Каска защитная',
   'дата_выдачи': '2025-03-10', 'дата_изготовления': '',
   'срок_годности': 'До износа', 'дата_окончания': 'До износа',
   'примечание': 'старая, списана'},
  {'id': 14, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд', 'наименование': 'Перчатки нитриловые',
   'дата_выдачи': '2026-09-01', 'дата_изготовления': '',
   'срок_годности': '1 год', 'дата_окончания': '2027-09-01',
   'примечание': ''},
  {'id': 15, 'таб_номер': '0872', 'работник': 'Галкин Д. Н.',
   'должность': 'Мастер КИПиА', 'наименование': 'перчатки нитриловые',
   'дата_выдачи': '2026-09-05', 'дата_изготовления': '',
   'срок_годности': '1 год', 'дата_окончания': '2027-09-05',
   'примечание': ''},
  {'id': 16, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд', 'наименование': '  Ботинки  ',
   'дата_выдачи': '2026-02-11', 'дата_изготовления': '',
   'срок_годности': '1 год', 'дата_окончания': '2027-02-11',
   'примечание': ''},
  {'id': 17, 'таб_номер': '0872', 'работник': 'Галкин Д. Н.',
   'должность': 'Мастер КИПиА', 'наименование': 'Очки закрытые',
   'дата_выдачи': '2026-04-14', 'дата_изготовления': '',
   'срок_годности': 'До износа', 'дата_окончания': 'До износа',
   'примечание': ''},
  {'id': 18, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд', 'наименование': 'Противогаз',
   'дата_выдачи': '2026-01-20', 'дата_изготовления': '2025-01-15',
   'срок_годности': '3 года', 'дата_окончания': '2028-01-15',
   'примечание': ''},
  {'id': 19, 'таб_номер': '0872', 'работник': 'Галкин Д. Н.',
   'должность': 'Мастер КИПиА', 'наименование': '',
   'дата_выдачи': '', 'дата_изготовления': '',
   'срок_годности': '', 'дата_окончания': '', 'примечание': ''},
]


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


def api_response(action, body, role, perms, no_matrix):
    if no_matrix and action == 'getMyAccess':
        # «старый сервер» без getMyAccess — клиент уходит в легаси-карту
        return {'ok': False, 'error': 'Unknown action'}
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local',
                'role': role}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': role, 'found': True,
                'permissions': perms}}
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
            'trainings': [], 'instrList': [], 'instrAll': [],
            'eventsAll': []}}
    if action == 'workSchedule.listVacations':
        return {'ok': True, 'data': {'vacations': []}}
    if action == 'workSchedule.listPpe':
        return {'ok': True, 'data': {'ppe': [dict(r) for r in PPE_STATE]}}
    if action == 'workSchedule.listEntries':
        return {'ok': True, 'data': {'entries': [dict(e) for e in ENTRIES]}}
    if action == 'prodCalendar.getMonth':
        return {'ok': True, 'data': {'workdays': 22, 'weekends': 8,
                'shortdays': 0, 'holidays': [], 'transfers': []}}
    return {'ok': True, 'data': {'ok': True}}


def attach(page, ctx, theme, tag, role='КИП ИОС', perms=None,
           no_matrix=False):
    """Мок API + тема + токен. perms — права матрицы (dict)."""
    if perms is None:
        perms = {}
    js_errors = []
    page.on('pageerror', lambda e: js_errors.append(str(e)))
    page.on('dialog', lambda dlg: dlg.accept())
    # kip8: ключи БЕЗ префикса kip8test: (де-изоляция переноса)
    ctx.add_init_script(
        "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
        "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
        "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
        "localStorage.setItem('kip8_session_token','sm-t460-%s');" % tag +
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
        resp = api_response(action, body, role, perms, no_matrix)
        return route.fulfill(status=200,
                             content_type='application/json; charset=utf-8',
                             body=json.dumps(resp, ensure_ascii=False))

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)

    def block_external(route):
        route.fulfill(status=404, content_type='text/plain',
                      body='not found (t460-%s)' % tag)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)
    return js_errors


def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(('  + ' if ok else '  X ') + name +
          (('  [' + str(extra)[:230] + ']') if (extra and not ok) else ''))


def shot(page, name):
    try:
        page.screenshot(path=os.path.join(SHOTS, name))
    except Exception as e:
        print('  (скриншот %s не сохранён: %s)' % (name, e))


def hub_button(page):
    """Видимость кнопки «Плановые мероприятия» на «Документации ИОС»."""
    return page.evaluate("""(() => {
        const b = document.getElementById('planEventsMenuBtn');
        return b ? b.style.display !== 'none' : null;})()""")


def sidebar_item(page):
    """Видимость пункта «Плановые мероприятия» в сайдбаре."""
    return page.evaluate("""(() => {
        const items = document.querySelectorAll('.sidebar-item');
        for (const it of items) {
            const oc = it.getAttribute('onclick') || '';
            if (oc.indexOf("navigateTo('plan-events')") !== -1) {
                return {vis: it.style.display !== 'none',
                        txt: it.innerText.trim()};
            }
        }
        return null;})()""")


DATALIST_JS = """(function(){
    var sheet = document.getElementById('wsPpeSheet');
    var dl = document.getElementById('wsPpeNameList');
    var opts = dl ? dl.querySelectorAll('option') : [];
    var vals = [];
    for (var i = 0; i < opts.length; i++)
        vals.push(opts[i].value !== undefined ? opts[i].value
                                               : (opts[i].getAttribute('value') || ''));
    return {
        open: sheet.classList.contains('active'),
        vals: vals,
        input: document.getElementById('wsPpeName').value
    };
})"""


def open_plan_events(page):
    page.evaluate("navigateTo('docs-ios')")
    page.wait_for_timeout(400)
    page.evaluate("navigateTo('plan-events')")
    page.wait_for_timeout(500)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # ===== A: колонка есть, галка ✓ + таблица образца =====
        print('=== Контекст A: «КИП ИОС», plan.events ✓ — раздел + таблица ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        jsA = attach(page, ctx, 'dark', 'a', role='КИП ИОС',
                     perms={'kipios.view': True, 'plan.events': True})
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('docs-ios')")
        page.wait_for_timeout(400)
        check('A1: кнопка «Плановые мероприятия» на хабе ВИДНА',
              hub_button(page) is True)
        pe_txt = page.evaluate("""(() => {
            const b = document.getElementById('planEventsMenuBtn');
            return b ? b.innerText.replace(/\\s+/g,' ').trim() : '';})()""")
        check('A2: label/sublabel кнопки — «Плановые мероприятия»',
              pe_txt.startswith('Плановые мероприятия') and
              'Периодические работы по месяцам года' in pe_txt, pe_txt)
        a3_js = (
            '''!!document.querySelector('.subsection-cell'''
            '''[data-subsection-key="plan-events"]')'''
        )
        check('A3: закрепление на главной (subsection-cell)',
              page.evaluate(a3_js))
        page.evaluate("navigateTo('plan-events')")
        page.wait_for_timeout(500)
        check('A4: страница открывается',
              page.evaluate("!!document.querySelector('#page-plan-events.active')"))
        crumbs = page.evaluate("""(() => {
            const t = document.querySelector('#page-plan-events .page-inline-header-title');
            return t ? t.innerText.replace(/\\s+/g, ' ').trim() : '';})()""")
        check('A5: крошки «... Документация ИОС / Плановые мероприятия»',
              'Документация ИОС' in crumbs and
              'Плановые мероприятия' in crumbs, crumbs)
        side = sidebar_item(page)
        check('A6: пункт сайдбара виден', side and side['vis'], side)

        tbl = page.evaluate("""(() => {
            const pageEl = document.getElementById('page-plan-events');
            const table = pageEl.querySelector('table.pe-table');
            if (!table) return null;
            const res = {};
            const ths = Array.from(table.querySelectorAll('thead th'))
                .map(th => th.textContent.trim());
            res.head = ths;
            res.nameRowspan = table.querySelector('th.pe-th-name').rowSpan;
            res.yearColspan = table.querySelector('th.pe-th-year').colSpan;
            res.groups = Array.from(table.querySelectorAll('tr.pe-group td'))
                .map(td => td.textContent.trim());
            res.acts = Array.from(table.querySelectorAll('td.pe-name'))
                .map(td => td.textContent.trim());
            res.emptyCnt = table.querySelectorAll('td.pe-m').length;
            res.emptyTexts = Array.from(table.querySelectorAll('td.pe-m'))
                .map(td => td.textContent.trim()).filter(t => t !== '').length;
            const m = table.querySelector('td.pe-m');
            const cs = getComputedStyle(m);
            res.border = cs.borderTopWidth !== '0px' &&
                         cs.borderTopStyle !== 'none';
            const th = table.querySelector('thead th');
            res.thBg = getComputedStyle(th).backgroundColor;
            const rows = Array.from(table.querySelectorAll('tr.pe-row'));
            res.zebra = rows.length >= 2 &&
                getComputedStyle(rows[0].querySelector('td')).backgroundColor !==
                getComputedStyle(rows[1].querySelector('td')).backgroundColor;
            res.rowCnt = rows.length;
            const g = table.querySelector('tr.pe-group td');
            res.groupBold = getComputedStyle(g).fontWeight;
            return res;})()""")
        check('A7: шапка «Мероприятия» + «2026 год» + 12 месяцев',
              tbl['head'][0] == 'Мероприятия' and
              tbl['head'][1] == '2026 год' and
              tbl['head'][2:] == MONTHS_SAMPLE, tbl['head'])
        check('A8: «Фев.» — опечатки образца «Феф.» нет',
              tbl['head'][3] == 'Фев.' and 'Феф.' not in tbl['head'],
              tbl['head'][2:5])
        check('A9: «Мероприятия» rowspan 2, «2026 год» colspan 12',
              tbl['nameRowspan'] == 2 and tbl['yearColspan'] == 12,
              (tbl['nameRowspan'], tbl['yearColspan']))
        check('A10: группы «В начале месяца» / «В конце месяца»',
              tbl['groups'] == [GROUPS_SAMPLE[0][0], GROUPS_SAMPLE[1][0]],
              tbl['groups'])
        check('A11: 8 мероприятий в порядке образца',
              tbl['acts'] == ALL_ACTS, tbl['acts'])
        check('A12: 96 ПУСТЫХ ячеек месяцев',
              tbl['emptyCnt'] == 96 and tbl['emptyTexts'] == 0,
              (tbl['emptyCnt'], tbl['emptyTexts']))
        check('A13: сетка с рамками, шапка стальная #1e293b, зебра 8 строк',
              tbl['border'] and tbl['thBg'] == 'rgb(30, 41, 59)' and
              tbl['zebra'] and tbl['rowCnt'] == 8,
              (tbl['border'], tbl['thBg'], tbl['zebra'], tbl['rowCnt']))
        check('A14: группы — жирный текст',
              tbl['groupBold'] == '700' or tbl['groupBold'] == 'bold',
              tbl['groupBold'])
        shot(page, '01-plan-events-table.png')
        check('A15: 0 JS-ошибок', len(jsA) == 0, jsA[:3])
        ctx.close()

        # ===== B: колонка есть, галка ✗ =====
        print('=== Контекст B: «КИП ИОС», plan.events ✗ — раздел СКРЫТ ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        jsB = attach(page, ctx, 'dark', 'b', role='КИП ИОС',
                     perms={'kipios.view': True, 'plan.events': False})
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('docs-ios')")
        page.wait_for_timeout(400)
        check('B1: кнопка на хабе СКРЫТА', hub_button(page) is False)
        check('B2: хаб «Документация ИОС» сам ОТКРЫТ (право снято не '
              'ломает хаб)',
              page.evaluate("!!document.querySelector('#page-docs-ios.active')"))
        side = sidebar_item(page)
        check('B3: пункт сайдбара СКРЫТ', side and not side['vis'], side)
        page.evaluate("navigateTo('plan-events')")
        page.wait_for_timeout(500)
        noacc = page.evaluate("""(() => {
            const el = document.getElementById('noAccessScreen');
            const pageEl = document.getElementById('page-plan-events');
            return {no: el && el.style.display !== 'none',
                    act: pageEl && pageEl.classList.contains('active')};})()""")
        check('B4: прямой переход → «Нет доступа», страница НЕ активна',
              noacc['no'] and not noacc['act'], noacc)
        shot(page, '02-access-denied.png')
        check('B5: 0 JS-ошибок', len(jsB) == 0, jsB[:3])
        ctx.close()

        # ===== C: ПЕРЕХОДНЫЙ — колонки в матрице ещё нет =====
        print('=== Контекст C: матрица БЕЗ колонки plan.events (фоллбек 460) ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        jsC = attach(page, ctx, 'dark', 'c', role='КИП ИОС',
                     perms={'kipios.view': True})  # ключа plan.events НЕТ
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('docs-ios')")
        page.wait_for_timeout(400)
        check('C1: раздел ВИДЕН (переходный фоллбек Task 460)',
              hub_button(page) is True)
        page.evaluate("navigateTo('plan-events')")
        page.wait_for_timeout(500)
        check('C2: страница открывается',
              page.evaluate("!!document.querySelector('#page-plan-events.active')"))
        check('C3: 0 JS-ошибок', len(jsC) == 0, jsC[:3])
        ctx.close()

        # ===== D: легаси — сервер без getMyAccess =====
        print('=== Контекст D: getMyAccess недоступен → легаси-карта ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        jsD = attach(page, ctx, 'dark', 'd', role='КИП ИОС',
                     perms={'kipios.view': True}, no_matrix=True)
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('docs-ios')")
        page.wait_for_timeout(400)
        check('D1: раздел ВИДЕН по легаси-карте (КИП ИОС)',
              hub_button(page) is True)
        page.evaluate("navigateTo('plan-events')")
        page.wait_for_timeout(500)
        check('D2: страница открывается',
              page.evaluate("!!document.querySelector('#page-plan-events.active')"))
        check('D3: 0 JS-ошибок', len(jsD) == 0, jsD[:3])
        ctx.close()

        # ===== E: право самодостаточно =====
        print('=== Контекст E: «КИП8» + plan.events ✓ — право самодостаточно ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        jsE = attach(page, ctx, 'dark', 'e', role='КИП8',
                     perms={'calc.view': True, 'library.view': True,
                            'whatsnew.view': True, 'plan.events': True})
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('docs')")
        page.wait_for_timeout(400)
        hub_hidden = page.evaluate("""(() => {
            const btns = document.querySelectorAll('#page-docs .menu-btn');
            for (const b of btns) {
                if ((b.getAttribute('onclick')||'').indexOf('docs-ios') !== -1)
                    return b.style.display === 'none';
            }
            return true;})()""")
        check('E1: хаба «Документация ИОС» НЕТ (права нет)', hub_hidden)
        page.evaluate("navigateTo('plan-events')")
        page.wait_for_timeout(500)
        check('E2: раздел ОТКРЫВАЕТСЯ по праву plan.events (самодостаточно)',
              page.evaluate("!!document.querySelector('#page-plan-events.active')"))
        side = sidebar_item(page)
        check('E3: пункт сайдбара виден', side and side['vis'], side)
        shot(page, '03-standalone-permission.png')
        check('E4: 0 JS-ошибок', len(jsE) == 0, jsE[:3])
        ctx.close()

        # ===== F: Task 461 — datalist СИЗ динамический =====
        print('=== Контекст F: форма СИЗ — динамический datalist (Task 461) ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        jsF = attach(page, ctx, 'dark', 'f', role='Админ',
                     perms={'calc.view': True, 'library.view': True,
                            'kipios.view': True, 'plan.events': True,
                            'workschedule.view': True,
                            'workschedule.edit': True,
                            'flowmeter.view': True})
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2500)
        check('F1: приложение загрузилось, график открыт',
              page.evaluate("(function(){return !!document.querySelector(" +
              "'.ws-grid');})()"))
        page.click('#wsWorkersBtn')
        page.wait_for_timeout(900)
        page.click('button[title="Федосов А. В."]')
        page.wait_for_timeout(900)
        page.click('.ws-emp-addppe')
        page.wait_for_timeout(700)
        b = page.evaluate(DATALIST_JS)
        check('F2: шторка «Новое СИЗ» открыта', b['open'])
        check('F3: datalist ДИНАМИЧЕСКИЙ: 9 записей с повторами → '
              'РОВНО 5 уникальных наименований',
              len(b['vals']) == 5, b['vals'])
        check('F4: все разные СИЗ, БЕЗ повторения (заявка Task 461)',
              b['vals'] == EXPECTED_DYNAMIC, b['vals'])
        kas = b['vals'].count('Каска защитная')
        per = sum(1 for v in b['vals'] if v.lower() == 'перчатки нитриловые')
        check('F5: каска ×3 записи → одна строка; перчатки в 2 регистрах '
              '→ одна', kas == 1 and per == 1, (kas, per, b['vals']))
        check('F6: пробелы обрезаны («  Ботинки  » → «Ботинки»), пустое '
              'имя не попало',
              'Ботинки' in b['vals'] and
              all(v == v.strip() and v for v in b['vals']), b['vals'])
        check('F7: сортировка по алфавиту',
              b['vals'] == sorted(b['vals'],
                                  key=lambda x: x.lower()), b['vals'])
        shot(page, '04-ppe-datalist.png')
        check('F8: 0 JS-ошибок', len(jsF) == 0, jsF[:3])
        ctx.close()

        # ===== G: мобайл 375 =====
        print('=== Контекст G: мобайл 375 — кнопка хаба + скролл таблицы ===')
        ctx = browser.new_context(viewport={'width': 375, 'height': 812})
        page = ctx.new_page()
        jsG = attach(page, ctx, 'dark', 'g', role='КИП ИОС',
                     perms={'kipios.view': True, 'plan.events': True})
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('docs-ios')")
        page.wait_for_timeout(400)
        page.click('#planEventsMenuBtn')
        page.wait_for_timeout(600)
        check('G1: мобайл — кнопка «Документации ИОС» открывает страницу',
              page.evaluate("!!document.querySelector('#page-plan-events.active')"))
        scroll = page.evaluate("""(() => {
            const w = document.querySelector('#page-plan-events .pe-grid-wrap');
            if (!w) return null;
            return {sw: w.scrollWidth, cw: w.clientWidth};})()""")
        check('G2: сетка шире экрана — горизонтальная прокрутка',
              scroll and scroll['sw'] > scroll['cw'], scroll)
        shot(page, '05-mobile-plan-events.png')
        check('G3: 0 JS-ошибок (мобайл)', len(jsG) == 0, jsG[:3])
        ctx.close()

        browser.close()

    print('-' * 60)
    print('ИТОГ Task 460-462 SMOKE (kip8): %d passed / %d failed'
          % (PASS, FAIL))
    return 0 if FAIL == 0 else 1


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    try:
        code = main()
    finally:
        server.shutdown()
    raise SystemExit(code)
