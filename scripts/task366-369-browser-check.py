#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 366-369 (перенос в kip8): browser-check — пакет:
#   366 — баннер недоставленных показаний (замена текста; далее в 367
#         убран вовсе) + server_busy повторяем; серверный дедуп архива
#         (FlowmeterArchive.gs — обновлён пользователем в Apps Script);
#   367 — баннера НЕТ, вместо него жёлто-оранжевый (#f5a623) цвет
#         ЗНАЧЕНИЙ карточек с недоставленными показаниями, зелёный
#         после доставки; недельные/месячные красные по календарю;
#   368 — показания №3/№11/№9 за ПЕРИОД двух дат (дефолт — закрытая
#         неделя пн–вс / прошлый месяц), красный по ЗАКРЫТЫМ
#         периодам, подписи-диапазоны, реальный ввод → payload;
#   369 — КИП ИОС: свайп кнопки «Проекты» (в любую сторону) открывает
#         «Проекты по статусу» (группы по столбцу «Статус проекта»).
# Контексты: десктоп 1280 тёмная (расходомеры + проекты), мобайл 375.
# + 0 JS-ошибок; скриншот-пруфы. kip8: localStorage БЕЗ префикса.
import datetime
import json
import sys
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8969
TODAY = datetime.date.today()

def monday_of(d):
    return d - datetime.timedelta(days=d.weekday())

MON = monday_of(TODAY)
W_START = MON - datetime.timedelta(days=7)   # закрытая неделя: пн
W_END = MON - datetime.timedelta(days=1)     # закрытая неделя: вс
W2_START = MON - datetime.timedelta(days=14)
W2_END = MON - datetime.timedelta(days=8)

def month_first(d):
    return d.replace(day=1)

def prev_month_bounds(d):
    first = month_first(d)
    last = first - datetime.timedelta(days=1)
    return month_first(last), last

M_START, M_END = prev_month_bounds(TODAY)
M2_START, M2_END = prev_month_bounds(M_START)

def mdy(d):
    return '%d/%d/%d' % (d.month, d.day, d.year)

def iso(d):
    return '%d-%02d-%02d' % (d.year, d.month, d.day)

YESTERDAY = TODAY - datetime.timedelta(days=1)
D3 = TODAY - datetime.timedelta(days=3)

def meter(i, hoz, param, dprev, dcurr, prev, curr, period):
    return {'id': i, 'hoz': hoz, 'param': param, 'datePrev': mdy(dprev),
            'dateCurr': mdy(dcurr), 'prev': prev, 'curr': curr, 'unit': 'м³',
            'temp': None, 'gcal': None, 'period': period,
            'modRole': 'Админ', 'modName': 'user@test.local',
            'modDisplayName': 'user@test.local', 'modTimestamp': None}

MOCK_METERS = [
    meter(2,  'Хозрасчёт №2',  'Расход воды речной в корпус 114',
          YESTERDAY, YESTERDAY, 383181.0, 383291.0, 'Ежедневно'),
    meter(4,  'Хозрасчёт №4',  'Расход воздуха технологического в корпус 114',
          D3, D3, 655000.0, 679700.0, 'Ежедневно'),
    meter(3,  'Хозрасчёт №3',  'Расход воды пожарохозяйственной (ПХВ) в корпус 114',
          W_START, W_END, 381484.0, 381485.0, 'Еженедельно'),
    meter(9,  'Хозрасчёт №9',  'Расход азота в корпус 114',
          M_START, M_END, 8544.5, 8545.5, 'Ежемесячно'),
    meter(11, 'Хозрасчёт №11', 'Расход воды речной в корпус 116',
          W2_START, W2_END, 105240.0, 105241.0, 'Еженед.'),
    meter(5,  'Хозрасчёт №5',  'Расход пара в корпус 114',
          M2_START, M2_END, 1234.0, 1240.0, 'Ежемес.'),
    meter(12, 'Хозрасчёт №12', 'Расход воздуха технологического в корпус 116',
          YESTERDAY, YESTERDAY, 109634.0, 110393.0, 'Ежедневно'),
]

ARCH_3 = [
    {'meterId': 3, 'prev': 381484.0, 'curr': 381485.0, 'consumption': 1.0,
     'datePrev': mdy(W_START), 'dateCurr': mdy(W_END), 'temp': None, 'gcal': None,
     'entryType': 'сутки', 'comment': '', 'anomaly': ''},
]

def proj(pid, name, num, status, dep, date):
    return {'ID': str(pid), '№': str(pid), 'Наименование проекта': name,
            '№ проекта': num, 'Файл проекта': '', 'Дата утв.': date,
            'Отделение': dep, 'Статус проекта': status, 'Данные статуса': '',
            'Примечание': '', 'Жёлтым отмечены приоритетные проекты': ''}

MOCK_PROJECTS = {'projects': [
    proj(1, 'Реконструкция котельной', 'П-101', 'Выполнен', 'ТЭЦ', '2020-01-15'),
    proj(2, 'Насосная станция №2', 'П-102', 'Новый', 'ТЭЦ', '2023-05-05'),
    proj(3, 'Вентиляция корпуса 114', 'П-103', 'Выполнен', 'КО', '2019-02-02'),
    proj(4, 'Азотная станция', 'П-104', 'Остановлен', 'КО', '2021-03-03'),
    proj(5, 'Реконструкция ВОК', 'П-105', 'Новый', 'ВОК', '2022-02-02'),
    proj(6, 'Склад реагентов', 'П-106', 'Отменен', 'ВОК', '2018-04-04'),
    proj(7, 'Кислородная станция', 'П-107', 'Выполнен', 'ТЭЦ', '2024-01-01'),
    proj(8, 'Паропровод корпуса 116', 'П-108', 'Действующий', 'КО', '2024-06-06'),
    proj(9, 'Старый проект без статуса', 'П-109', '', 'КОС', '2015-07-07'),
]}

STATE = {'role': 'Админ', 'online': True}
CAPTURED = []

def mock_response(action, body):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local', 'role': STATE['role']}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': STATE['role'], 'found': True,
                'permissions': {'kipios.view': True, 'flowmeter.view': True,
                                 'workschedule.view': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'flowmeter.list':
        return {'ok': True, 'data': {'meters': json.loads(json.dumps(MOCK_METERS))}}
    if action == 'flowmeter.getValidationRules':
        return {'ok': True, 'data': {'rules': []}}
    if action == 'flowmeter.getRecentAllMeters':
        return {'ok': True, 'data': {'records': []}}
    if action == 'flowmeter.archive':
        pid = (body or {}).get('id')
        return {'ok': True, 'data': {'records': ARCH_3 if pid == 3 else []}}
    if action == 'flowmeter.updateReading':
        CAPTURED.append(body)
        pid = body.get('id') if body else None
        for m in MOCK_METERS:
            if m['id'] == pid:
                m['prev'] = body.get('prev', m['prev'])
                m['curr'] = body.get('curr', m['curr'])
                m['datePrev'] = body.get('datePrev', m['datePrev'])
                m['dateCurr'] = body.get('dateCurr', m['dateCurr'])
                m['modTimestamp'] = datetime.datetime.now().isoformat()
                break
        return {'ok': True, 'data': {'id': pid}}
    return {'ok': True, 'data': {'ok': True}}

PASS = 0
FAIL = 0
def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok: PASS += 1
    else: FAIL += 1
    print(('  ✓ ' if ok else '  ✗ ') + name + (('  [' + str(extra) + ']') if (extra and not ok) else ''))

VAL_COLOR = """(function(id){
    var card = document.querySelector('.flow-card[data-flow-id="' + id + '"]');
    if (!card) return null;
    var v = card.querySelector('.flow-summary-val');
    return v ? getComputedStyle(v).color : null;
})"""

CARD_DATE = """(function(id){
    var card = document.querySelector('.flow-card[data-flow-id="' + id + '"]');
    if (!card) return null;
    var el = card.querySelector('.flow-summary-date-inline');
    return el ? el.textContent : null;
})"""

ACTIVE_PAGE = "(function(){var a=document.querySelector('.page-content.active');" \
              "return a?a.id.replace('page-',''):null;})()"

def swipe(page, selector, direction):
    box = page.locator(selector).bounding_box()
    cx = box['x'] + box['width'] / 2
    cy = box['y'] + box['height'] / 2
    page.mouse.move(cx, cy)
    page.mouse.down()
    target = cx + direction * box['width'] * 0.5
    for i in range(1, 11):
        page.mouse.move(cx + direction * (target - cx) * i / 10.0, cy)
    page.mouse.up()

with sync_playwright() as p:
    browser = p.chromium.launch()

    # ================= Контекст 1: десктоп 1280, тёмная, Админ =================
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
    page = ctx.new_page()
    js_errors = []
    page.on('pageerror', lambda e: js_errors.append(str(e)))
    page.on('dialog', lambda d: d.accept())

    def handle(route, request):
        url = request.url
        action = ''
        if 'action=' in url:
            action = unquote(url.split('action=')[1].split('&')[0])
        if '/data/projects.json' in url:
            route.fulfill(status=200, content_type='application/json; charset=utf-8',
                          body=json.dumps(MOCK_PROJECTS, ensure_ascii=False).encode('utf-8'))
            return
        if not STATE['online'] and 'action=flowmeter.updateReading' in url:
            route.abort()
            return
        pd = request.post_data
        body = None
        if pd:
            try: body = json.loads(pd)
            except Exception: body = None
        route.fulfill(status=200, content_type='application/json; charset=utf-8',
                      body=json.dumps(mock_response(action, body), ensure_ascii=False).encode('utf-8'))
    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    ctx.route('**/data/projects.json**', handle)
    def block_external(route):
        route.fulfill(status=404, content_type='text/plain', body='not found (browser-check t366-369-kip8)')
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)

    # kip8: localStorage БЕЗ префикса (изоляция только в kip8test)
    ctx.add_init_script(
        "localStorage.setItem('kip8_session_token','bc-k8-pkg-a');" +
        "localStorage.setItem('app-theme','dark');")
    page.goto('http://localhost:%d/index.html' % PORT)
    page.wait_for_timeout(2500)
    check('A: страница загрузилась', page.evaluate("document.title==='КИПиА'"))

    # ===== Блок расходомеров (Tasks 366/367/368) =====
    page.evaluate("navigateTo('flowmeter-data')")
    page.wait_for_timeout(1500)
    check('B: список расходомеров отрисован (7 карточек)',
          page.evaluate("document.querySelectorAll('.flow-card').length") == 7)
    GREEN = 'rgb(90, 184, 112)'
    RED = 'rgb(255, 92, 71)'
    PENDING = 'rgb(245, 166, 35)'   # #f5a623 (Task 367)
    check('C: №2 суточный (вчера) — ЗЕЛЁНЫЙ', page.evaluate(VAL_COLOR, 2) == GREEN,
          page.evaluate(VAL_COLOR, 2))
    check('D: №4 суточный (3 дня назад) — КРАСНЫЙ', page.evaluate(VAL_COLOR, 4) == RED,
          page.evaluate(VAL_COLOR, 4))
    check('E: №3 недельный (данные = закрытая неделя) — ЗЕЛЁНЫЙ (368)',
          page.evaluate(VAL_COLOR, 3) == GREEN, page.evaluate(VAL_COLOR, 3))
    check('F: №11 недельный (неделя старее закрытой) — КРАСНЫЙ (368)',
          page.evaluate(VAL_COLOR, 11) == RED, page.evaluate(VAL_COLOR, 11))
    check('G: №9 месячный (данные = прошлый месяц) — ЗЕЛЁНЫЙ (368)',
          page.evaluate(VAL_COLOR, 9) == GREEN, page.evaluate(VAL_COLOR, 9))
    check('H: №5 «Ежемес.» (календарный месяц прошёл) — КРАСНЫЙ (367)',
          page.evaluate(VAL_COLOR, 5) == RED, page.evaluate(VAL_COLOR, 5))
    rng3 = 'за %02d.%02d–%02d.%02d.%d г.' % (W_START.day, W_START.month, W_END.day, W_END.month, W_END.year)
    check('I: №3 подпись-диапазон «%s» (368)' % rng3,
          page.evaluate(CARD_DATE, 3) == rng3, page.evaluate(CARD_DATE, 3))
    # Баннера недоставленных НЕТ (366 → 367: убран вовсе)
    check('J: баннера недоставленных показаний НЕТ (367)',
          page.evaluate("document.querySelector('.flow-outbox-banner') === null"))

    # Форма №3: период двух дат, дефолт = закрытая неделя (368)
    page.evaluate("FlowmeterData.openDetail(3)")
    page.wait_for_timeout(700)
    page.evaluate("FlowmeterData.openInput(false)")
    page.wait_for_timeout(400)
    check('K: №3 подписи «Период с» / «по» (368)',
          page.evaluate("(document.getElementById('flowInputDateLabel')||{}).textContent") == 'Период с' and
          page.evaluate("(document.getElementById('flowInputDateEndLabel')||{}).textContent") == 'по')
    check('L: №3 дефолты = закрытая неделя %s … %s' % (iso(W_START), iso(W_END)),
          page.evaluate("document.getElementById('flowInputDate').value") == iso(W_START) and
          page.evaluate("document.getElementById('flowInputDateEnd').value") == iso(W_END),
          page.evaluate("document.getElementById('flowInputDate').value") + ' … ' +
          page.evaluate("document.getElementById('flowInputDateEnd').value"))
    page.evaluate("FlowmeterData.closeInput()")
    page.evaluate("closeDetailPanel()")

    # Реальный ввод №11 (красный): период закрытой недели уходит на сервер (368)
    page.evaluate("FlowmeterData.openDetail(11)")
    page.wait_for_timeout(400)
    page.evaluate("FlowmeterData.openInput(false)")
    page.wait_for_timeout(400)
    page.fill('#flowInputField', '105240,0')
    page.click('.flow-input-submit')
    page.wait_for_timeout(1800)
    cap = CAPTURED[-1] if CAPTURED else None
    check('M: №11 payload: datePrev/dateCurr = границы закрытой недели (368)',
          cap is not None and cap.get('datePrev') == mdy(W_START) and cap.get('dateCurr') == mdy(W_END), cap)
    check('N: №11 после ввода за закрытую неделю — ЗЕЛЁНЫЙ (368)',
          page.evaluate(VAL_COLOR, 11) == GREEN, page.evaluate(VAL_COLOR, 11))
    page.evaluate("FlowmeterData.closeInput()")
    page.evaluate("closeDetailPanel()")

    # Offline-ввод №4 → жёлто-оранжевый pending (367), затем доставка → зелёный
    STATE['online'] = False
    page.evaluate("FlowmeterData.openDetail(4)")
    page.wait_for_timeout(400)
    page.evaluate("FlowmeterData.openInput(false)")
    page.wait_for_timeout(400)
    page.fill('#flowInputField', '679700,0')
    page.click('.flow-input-submit')
    page.wait_for_timeout(1500)
    check('O: №4 offline-ввод — ЗНАЧЕНИЕ жёлто-оранжевое #f5a623 (367)',
          page.evaluate(VAL_COLOR, 4) == PENDING, page.evaluate(VAL_COLOR, 4))
    page.evaluate("FlowmeterData.closeInput()")
    page.evaluate("closeDetailPanel()")
    STATE['online'] = True
    page.evaluate("FlowmeterData._flushOutbox()")
    page.wait_for_timeout(1500)
    check('P: №4 после доставки — снова ЗЕЛЁНЫЙ (367)',
          page.evaluate(VAL_COLOR, 4) == GREEN, page.evaluate(VAL_COLOR, 4))
    check('Q: 0 JS-ошибок (расходомеры)', len(js_errors) == 0, js_errors[:3])

    # ===== Блок проектов (Task 369) =====
    page.evaluate("navigateTo('kip-ios')")
    page.wait_for_timeout(600)
    check('R: кнопка «Проекты» внутри свайп-ячейки #projectSwipeCell (369)',
          page.evaluate("(function(){var b=document.getElementById('projectsEntryBtn');" \
                       "return !!b && !!b.closest('#projectSwipeCell');})()"))
    check('S: две подложки «По статусу» (лево/право)',
          page.evaluate("Array.from(document.querySelectorAll(" \
              "'#projectSwipeCell .dev-swipe-bg span')).map(function(e){return e.textContent;})" \
              ".join('|')") == 'По статусу|По статусу')
    swipe(page, '#projectsEntryBtn', -1)
    page.wait_for_timeout(700)
    check('T: свайп влево → открылась projects-status',
          page.evaluate(ACTIVE_PAGE) == 'projects-status', page.evaluate(ACTIVE_PAGE))
    page.wait_for_timeout(800)
    titles = page.evaluate("Array.from(document.querySelectorAll(" \
        "'.page-content.active .project-sorted-list .pb-section-title-text'))" \
        ".map(function(e){return e.textContent;})")
    check('U: группы по «Статусу проекта» — Новый→Выполнен→Остановлен→Отменен→Действующий→(без статуса)',
          titles == ['Новый', 'Выполнен', 'Остановлен', 'Отменен', 'Действующий', '(без статуса)'],
          str(titles))
    counts = page.evaluate("Array.from(document.querySelectorAll(" \
        "'.page-content.active .project-sorted-list .pb-section-title-count'))" \
        ".map(function(e){return e.textContent;})")
    check('V: счётчики групп 2/3/1/1/1/1', counts == ['2', '3', '1', '1', '1', '1'], str(counts))
    page.screenshot(path='scripts/task366-369-proof-flow-projects.png')

    # группа «Выполнен» → project-group с годами
    page.evaluate("var t=Array.from(document.querySelectorAll(" \
        "'.project-sorted-list .pb-section-title')).filter(function(e){return " \
        "e.textContent.indexOf('Выполнен')===0;})[0]; t.dispatchEvent(new Event('click',{bubbles:true}))")
    page.wait_for_timeout(600)
    check('W: группа «Выполнен» → project-group с 3 карточками и годами',
          page.evaluate(ACTIVE_PAGE) == 'project-group' and
          page.evaluate("document.querySelectorAll('#projectGroupList .project-card').length") == 3 and
          sorted(page.evaluate("Array.from(document.querySelectorAll(" \
              "'#projectGroupList .pb-section-title-text'))" \
              ".map(function(e){return e.textContent;})")) == ['2019', '2020', '2024'])

    # возврат: ТАП → «По отделениям» (не сломано)
    page.evaluate("navigateTo('kip-ios')")
    page.wait_for_timeout(500)
    page.click('#projectsEntryBtn')
    page.wait_for_timeout(600)
    check('X: тап без свайпа → projects-prod (как раньше)',
          page.evaluate(ACTIVE_PAGE) == 'projects-prod', page.evaluate(ACTIVE_PAGE))
    prod_titles = page.evaluate("Array.from(document.querySelectorAll(" \
        "'.page-content.active .project-sorted-list .pb-section-title-text'))" \
        ".map(function(e){return e.textContent;})")
    check('Y: «По отделениям» — группы КО/ВОК/ТЭЦ/КОС',
          set(prod_titles) == {'КО', 'ВОК', 'ТЭЦ', 'КОС'}, str(prod_titles))

    # свайп вправо → тоже «По статусу»
    page.evaluate("navigateTo('kip-ios')")
    page.wait_for_timeout(500)
    swipe(page, '#projectsEntryBtn', +1)
    page.wait_for_timeout(700)
    check('Z: свайп вправо → тоже projects-status',
          page.evaluate(ACTIVE_PAGE) == 'projects-status', page.evaluate(ACTIVE_PAGE))
    check('AA: 0 JS-ошибок (проекты)', len(js_errors) == 0, js_errors[:3])
    ctx.close()

    # ================= Контекст 2: мобайл 375 =================
    ctx2 = browser.new_context(viewport={'width': 375, 'height': 700})
    page2 = ctx2.new_page()
    js_errors2 = []
    page2.on('pageerror', lambda e: js_errors2.append(str(e)))
    page2.on('dialog', lambda d: d.accept())
    ctx2.route('**/exec?**', handle)
    ctx2.route('**script.google.com/**', handle)
    ctx2.route('**/data/projects.json**', handle)
    ctx2.route('**raw.githubusercontent.com/**', block_external)
    ctx2.route('**calendar.legalic.ru/**', block_external)
    ctx2.add_init_script(
        "localStorage.setItem('kip8_session_token','bc-k8-pkg-m');" +
        "localStorage.setItem('app-theme','dark');")
    page2.goto('http://localhost:%d/index.html' % PORT)
    page2.wait_for_timeout(2500)
    page2.evaluate("navigateTo('kip-ios')")
    page2.wait_for_timeout(600)
    swipe(page2, '#projectsEntryBtn', -1)
    page2.wait_for_timeout(700)
    check('AB: мобайл — свайп влево → projects-status',
          page2.evaluate(ACTIVE_PAGE) == 'projects-status', page2.evaluate(ACTIVE_PAGE))
    page2.wait_for_timeout(800)
    m_titles = page2.evaluate("Array.from(document.querySelectorAll(" \
        "'.page-content.active .project-sorted-list .pb-section-title-text'))" \
        ".map(function(e){return e.textContent;})")
    check('AC: мобайл — все 6 групп читаются', m_titles ==
          ['Новый', 'Выполнен', 'Остановлен', 'Отменен', 'Действующий', '(без статуса)'], str(m_titles))
    page2.screenshot(path='scripts/task366-369-proof-mobile.png')
    page2.evaluate("navigateTo('flowmeter-data')")
    page2.wait_for_timeout(1500)
    # №11/№4 тронуты вводом в контексте 1 (мок-стейт общий) — проверяем
    # нетронутые: №3 зелёный (данные закрытой недели), №5 «Ежемес.» красный
    check('AD: мобайл — расходомеры живы, №3 зелёный / №5 красный',
          page2.evaluate(VAL_COLOR, 3) == GREEN and page2.evaluate(VAL_COLOR, 5) == RED,
          str(page2.evaluate(VAL_COLOR, 3)) + ' / ' + str(page2.evaluate(VAL_COLOR, 5)))
    check('AE: 0 JS-ошибок (мобайл)', len(js_errors2) == 0, js_errors2[:3])
    ctx2.close()

    browser.close()

print('\nИтог: %d passed, %d failed' % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
