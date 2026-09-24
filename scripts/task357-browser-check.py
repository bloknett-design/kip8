#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 348: browser-check — расходомеры хозрасчётные:
#   1) форма ввода показаний: поле «Дата за предыдущие сутки» по
#      умолчанию = ПРЕДЫДУЩИЕ сутки (при сохранении введённых данных
#      без выбора даты — сохраняется дата предыдущих суток);
#      редактирование предзаполняется СУЩЕСТВУЮЩЕЙ датой записи;
#   2) цвет показаний в списке карточек: зелёный → КРАСНЫЙ «пора
#      вводить новые данные»: «Ежедневно» — с 6:00 нет данных за
#      предыдущие сутки (зелёный до 6:00 следующих суток после
#      ввода); «Еженедельно»/«Ежемесячно» — прошла календарная
#      неделя/месяц. Смена цвета БЕЗ перезагрузки: минутный таймер.
#
# Контексты:
#   1. DESKTOP + ТЁМНАЯ + Clock API (фикс. 10.09.2026):
#      старт 04:30 (до 6:00) → классы/цвета → fast_forward до 07:00
#      → КРАСНЫЙ у ежедневного (таймер сам перерисовал!) →
#      «Ввести показания» → дата=вчера → сохранение → payload
#      dateCurr='9/9/2026' (ЗАЯВКА №1) → карточка снова ЗЕЛЁНАЯ →
#      «Изменить показания» → дата записи (не «сегодня»).
#   2. DESKTOP + СВЕТЛАЯ (реальное время): цвета по темам —
#      зелёный #5ab870 / красный #c0392b.
#   3. MOBILE + ТЁМНАЯ (реальное время): список + форма ввода
#      (дата=вчера) — скриншот.
#   + 0 JS-ошибок во всех контекстах; скриншоты-пруфы.
import datetime
import json
from playwright.sync_api import sync_playwright

PORT = 8949
BASE = 'http://127.0.0.1:%d' % PORT

UA_ANDROID = ('Mozilla/5.0 (Linux; Android 13; Pixel 7) '
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Mobile Safari/537.36')
UA_DESKTOP = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36')

STATE = {'meters': [], 'fixed': False}
REQUESTS = {}
RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((ok, name, detail))
    print('  [%s] %s%s' % ('PASS' if ok else 'FAIL', name,
                           (' — ' + detail) if detail and not ok else ''))


# ---------- Python-зеркало FlowmeterData._isOverdue ----------
def is_overdue(period, date_curr, now):
    if not date_curr:
        return True
    try:
        p = str(date_curr).split('/')
        if len(p) != 3:
            return True
        y, m, d = int(p[2]), int(p[0]), int(p[1])
        dt = datetime.date(y, m, d)
    except Exception:
        return True
    # Нормализация: now может быть datetime.datetime ИЛИ datetime.date
    # (сравнивать date с datetime напрямую нельзя — TypeError).
    is_dt = isinstance(now, datetime.datetime)
    now_d = now.date() if is_dt else now
    hour = now.hour if is_dt else 0
    per = (period or '').lower()
    if 'недел' in per:
        return (dt - datetime.timedelta(days=dt.weekday())) < \
               (now_d - datetime.timedelta(days=now_d.weekday()))
    if 'месяч' in per:
        return (y * 12 + m - 1) < (now_d.year * 12 + now_d.month - 1)
    anchor = datetime.date(now_d.year, now_d.month, now_d.day)
    if hour < 6:
        anchor -= datetime.timedelta(days=1)
    anchor -= datetime.timedelta(days=1)
    return dt < anchor


def mdy(d):
    return '%d/%d/%d' % (d.month, d.day, d.year)


def days_ago(n, today):
    return today - datetime.timedelta(days=n)


def base_meter(mid, hoz, period, date_prev, date_curr, prev=100.0, curr=105.0,
               mod_name=None, mod_ts=None):
    return {'id': mid, 'hoz': hoz, 'param': 'Расход тестовый %s' % hoz,
            'unit': 'м3', 'period': period,
            'datePrev': date_prev, 'dateCurr': date_curr,
            'prev': prev, 'curr': curr, 'temp': None, 'gcal': None,
            'modRole': 'Админ' if mod_name else None, 'modName': mod_name,
            'modDisplayName': mod_name, 'modTimestamp': mod_ts}


def build_meters_fixed():
    """Фикстура для контекста с Clock (10.09.2026, чт недели 07–13.09)."""
    return [
        # A: ежедневно, 9/8 — ЗЕЛЁНЫЙ до 6:00 (ожидание 9/8), КРАСНЫЙ после
        base_meter(101, '№A', 'Ежедневно', '9/7/2026', '9/8/2026'),
        # B: еженедельно, та же неделя (9/8) — ЗЕЛЁНЫЙ
        base_meter(102, '№B', 'Еженедельно', '9/1/2026', '9/8/2026'),
        # C: еженедельно, прошлая неделя (28.08–03.09) — КРАСНЫЙ
        base_meter(103, '№C', 'Еженедельно', '8/21/2026', '8/28/2026'),
        # D: ежемесячно, текущий месяц — ЗЕЛЁНЫЙ
        base_meter(104, '№D', 'Ежемесячно', '9/1/2026', '9/2/2026'),
        # E: ежемесячно, август прошёл — КРАСНЫЙ
        base_meter(105, '№E', 'Ежемесячно', '8/10/2026', '8/31/2026'),
        # F: ежедневно, за вчера уже есть (9/9) — ЗЕЛЁНЫЙ всегда
        base_meter(106, '№F', 'Ежедневно', '9/8/2026', '9/9/2026'),
        # G: данных нет — КРАСНЫЙ
        base_meter(107, '№G', 'Ежедневно', None, None),
        # H: ежедневно, старые данные + свежий modTimestamp того же юзера
        # → «Изменить показания» → предзаполнение датой записи 9/3
        base_meter(108, '№H', 'Ежедневно', '9/2/2026', '9/3/2026',
                   mod_name='user@test.local', mod_ts='2026-09-10T06:50:00'),
    ]


def build_meters_relative(now):
    """Фикстура для контекстов с реальным временем (детерминированная)."""
    today = datetime.date(now.year, now.month, now.day)
    return [
        base_meter(201, '№A', 'Ежедневно', mdy(days_ago(2, today)), mdy(days_ago(1, today))),
        base_meter(202, '№B', 'Ежедневно', mdy(days_ago(6, today)), mdy(days_ago(5, today))),
        base_meter(203, '№C', 'Еженедельно', mdy(days_ago(22, today)), mdy(days_ago(21, today))),
        base_meter(204, '№D', 'Еженедельно', mdy(days_ago(1, today)), mdy(today)),
        base_meter(205, '№E', 'Ежемесячно', mdy(days_ago(46, today)), mdy(days_ago(45, today))),
        base_meter(206, '№F', 'Ежемесячно', mdy(days_ago(1, today)), mdy(today)),
        base_meter(207, '№G', 'Ежедневно', None, None),
    ]


def mock_response(action):
    if action == 'sendOTP':
        return {'ok': True, 'data': {'sent': True}}
    if action == 'verifyOTP':
        return {'ok': True, 'data': {'token': 't348', 'role': 'Админ',
                                     'userId': 7, 'email': 'user@test.local'}}
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 7, 'email': 'user@test.local', 'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'admin.panel': True, 'flowmeter.input': True,
                                'flowmeter.view': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'flowmeter.list':
        return {'ok': True, 'data': {'meters': STATE['meters']}}
    if action == 'flowmeter.getRecentAllMeters':
        return {'ok': True, 'data': {'records': []}}
    if action == 'flowmeter.getValidationRules':
        return {'ok': True, 'data': {'rules': []}}
    if action == 'flowmeter.getValidationHelp':
        return {'ok': True, 'data': {'help': []}}
    if action == 'flowmeter.archive':
        return {'ok': True, 'data': {'records': []}}
    if action == 'flowmeter.updateReading':
        # Stateful: применяем запись к мок-состоянию (сервер)
        pl = REQUESTS.get('flowmeter.updateReading', {})
        try:
            mid = int(pl.get('id'))
            for m in STATE['meters']:
                if m['id'] == mid:
                    m['datePrev'] = pl.get('datePrev') or m['datePrev']
                    m['dateCurr'] = pl.get('dateCurr') or m['dateCurr']
                    m['prev'] = float(pl.get('prev', 0) or 0)
                    m['curr'] = float(pl.get('curr', 0) or 0)
                    m['modName'] = 'user@test.local'
                    m['modDisplayName'] = 'user@test.local'
                    m['modRole'] = 'Админ'
                    m['modTimestamp'] = datetime.datetime.now().isoformat()
        except Exception:
            pass
        return {'ok': True, 'data': {'id': pl.get('id')}}
    return {'ok': False, 'error': 'Unknown action: ' + action}


def route_all(ctx):
    def handle(route, request):
        url = request.url
        action = 'unknown'
        for part in url.split('?')[1].split('&') if '?' in url else []:
            if part.startswith('action='):
                action = part.split('=')[1]
        try:
            payload = json.loads(request.post_data or '{}')
        except Exception:
            payload = {}
        REQUESTS[action] = payload
        route.fulfill(status=200, content_type='application/json; charset=utf-8',
                      body=json.dumps(mock_response(action), ensure_ascii=False).encode('utf-8'))
    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)

    def block_external(route):
        route.fulfill(status=404, content_type='text/plain', body='not found (t348)')
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)


def ui_login(page, email='user@test.local', code='1'):
    page.evaluate("KipAuth._showLoginScreen()")
    page.wait_for_selector('#loginScreen', state='visible')
    page.fill('#authEmail', email)
    page.click('#authSendBtn')
    page.wait_for_selector('#authStep2.active', timeout=5000)
    for i in range(1, 7):
        page.fill('#otp%d' % i, code)
    # 6-я цифра запускает АВТОпроверку через 200 мс (setupOtpInputs
    # в index.html) — клик по кнопке «Войти» гоняется с автосабмитом
    # (флейк: побеждает то одно, то другое). Надёжно: дождаться, пока
    # экран входа закроется (класс active снят); если автосабмит не
    # случился — дожать кнопкой.
    try:
        page.wait_for_function(
            "!document.getElementById('loginScreen').classList.contains('active')",
            timeout=5000)
    except Exception:
        page.click('#authVerifyBtn', timeout=5000)
        page.wait_for_timeout(700)


def card_class(page, mid):
    return page.evaluate(
        "document.querySelector('.flow-card[data-flow-id=\"%d\"] .flow-summary-val').className" % mid)


def card_color(page, mid):
    return page.evaluate(
        "getComputedStyle(document.querySelector('.flow-card[data-flow-id=\"%d\"] .flow-summary-val')).color" % mid)


def due(page, mid):
    return 'flow-summary-val-due' in card_class(page, mid)


def main():
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import threading
    import os
    os.chdir('/home/z/my-project/kip8')

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass
    httpd = HTTPServer(('127.0.0.1', PORT), Quiet)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    fails = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ================================================
        # Контекст 1: DESKTOP + тёмная + Clock (04:30 → 07:00)
        # ================================================
        print('=== 1. DESKTOP dark + Clock: переход 6:00 + форма + сохранение ===')
        STATE['meters'] = build_meters_fixed()
        STATE['fixed'] = True
        REQUESTS.clear()
        errors = []
        ctx = browser.new_context(user_agent=UA_DESKTOP,
                                  viewport={'width': 1280, 'height': 800})
        # kip8 (прод): БЕЗ изоляции localStorage (isolateLocalStorage —
        # только в kip8test) — ключ темы обычный, 'app-theme'.
        ctx.add_init_script("try{localStorage.setItem('app-theme','dark')}catch(e){}")
        route_all(ctx)
        page = ctx.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.clock.install(time=datetime.datetime(2026, 9, 10, 4, 30, 0))
        page.goto(BASE + '/index.html')
        page.wait_for_timeout(1500)
        ui_login(page)
        page.evaluate("navigateTo('flowmeter-data')")
        page.wait_for_selector('.flow-card[data-flow-id="101"]', timeout=8000)
        page.wait_for_timeout(400)

        print('  -- 04:30 (до 6:00) --')
        check('04:30: A (ежедн., 9/8) ЗЕЛЁНЫЙ (до 6:00 ожидается 9/8)', not due(page, 101))
        check('04:30: B (еженед., текущ. неделя) ЗЕЛЁНЫЙ', not due(page, 102))
        check('04:30: C (еженед., прошлая неделя) КРАСНЫЙ', due(page, 103))
        check('04:30: D (ежемес., текущ. месяц) ЗЕЛЁНЫЙ', not due(page, 104))
        check('04:30: E (ежемес., август) КРАСНЫЙ', due(page, 105))
        check('04:30: F (ежедн., за вчера) ЗЕЛЁНЫЙ', not due(page, 106))
        check('04:30: G (нет данных) КРАСНЫЙ', due(page, 107))
        check('04:30: H (ежедн., 9/3) КРАСНЫЙ', due(page, 108))
        check('Цвет КРАСНОГО в тёмной теме = rgb(231, 76, 60)',
              card_color(page, 103) == 'rgb(231, 76, 60)', card_color(page, 103))
        check('Цвет ЗЕЛЁНОГО = rgb(90, 184, 112)',
              card_color(page, 101) == 'rgb(90, 184, 112)', card_color(page, 101))
        check('Таймер «пора вводить» запущен (число)',
              page.evaluate("typeof FlowmeterData._overdueTimer") == 'number')
        check('Сигнатура состояний посчитана',
              isinstance(page.evaluate("FlowmeterData._overdueSig"), str) and
              page.evaluate("FlowmeterData._overdueSig.length") > 0)
        page.screenshot(path='scripts/task357-proof-dark-before6.png')

        print('  -- fast_forward до 07:00 (переход 6:00) --')
        page.clock.fast_forward(150 * 60 * 1000)
        page.wait_for_timeout(600)
        check('07:00: A (ежедн., 9/8) сам стал КРАСНЫМ (таймер перерисовал)',
              due(page, 101), card_class(page, 101))
        check('07:00: B остался ЗЕЛЁНЫЙ', not due(page, 102))
        check('07:00: F (за вчера 9/9) остался ЗЕЛЁНЫЙ', not due(page, 106))
        check('07:00: E (ежемес.) остался КРАСНЫЙ', due(page, 105))
        page.screenshot(path='scripts/task357-proof-dark-after6.png')

        # --- форма ввода: дефолт = вчера ---
        print('  -- форма «Ввести показания» --')
        page.click('.flow-card[data-flow-id="101"] .flow-card-header')
        page.wait_for_selector('#detailPanel.active', timeout=5000)
        page.wait_for_timeout(500)
        page.click('#detailPanelFooter .flow-input-btn')
        page.wait_for_selector('#flowInputSheet.active', timeout=5000)
        check('Дефолт поля даты = ПРЕДЫДУЩИЕ сутки (2026-09-09)',
              page.evaluate("document.getElementById('flowInputDate').value") == '2026-09-09',
              page.evaluate("document.getElementById('flowInputDate').value"))
        page.screenshot(path='scripts/task357-proof-dark-form.png')

        # --- сохранение: payload dateCurr = вчера, карточка → зелёная ---
        page.fill('#flowInputField', '110,5')
        REQUESTS.pop('flowmeter.updateReading', None)
        page.click('.flow-input-submit')
        page.wait_for_timeout(1500)
        pl = REQUESTS.get('flowmeter.updateReading', {})
        check('Сохранение: на сервер ушла дата ПРЕДЫДУЩИХ суток (9/9/2026)',
              pl.get('dateCurr') == '9/9/2026', 'фактически: %r' % pl.get('dateCurr'))
        check('Сохранение: значение 110.5 ушло на сервер',
              pl.get('curr') == 110.5, 'фактически: %r' % pl.get('curr'))
        check('После сохранения карточка A снова ЗЕЛЁНАЯ (сервер вернул свежие данные)',
              not due(page, 101), card_class(page, 101))
        page.screenshot(path='scripts/task357-proof-dark-saved.png')

        # --- форма правки: предзаполнение датой записи ---
        print('  -- форма «Изменить показания» (дата записи 9/3) --')
        page.click('.flow-card[data-flow-id="108"] .flow-card-header')
        page.wait_for_timeout(500)
        btn_text = page.evaluate(
            "(function(){var b=document.querySelector('#detailPanelFooter .flow-input-btn');"
            " return b?b.textContent:'';})()")
        check('Кнопка «Изменить показания» доступна (та же запись < 1 часа)',
              'Изменить' in btn_text, btn_text.strip()[:40])
        if 'Изменить' in btn_text:
            page.click('#detailPanelFooter .flow-input-btn')
            page.wait_for_selector('#flowInputSheet.active', timeout=5000)
            check('Правка: поле даты = дата записи (2026-09-03), НЕ «сегодня»',
                  page.evaluate("document.getElementById('flowInputDate').value") == '2026-09-03',
                  page.evaluate("document.getElementById('flowInputDate').value"))
            page.click('.flow-input-cancel')
            page.wait_for_timeout(300)
        check('C1: 0 JS-ошибок', len(errors) == 0, '; '.join(errors[:3]))
        ctx.close()

        # ================================================
        # Контекст 2: DESKTOP + светлая (реальное время)
        # ================================================
        print('=== 2. DESKTOP light: цвета по темам ===')
        now_real = datetime.datetime.now()
        STATE['meters'] = build_meters_relative(now_real)
        REQUESTS.clear()
        errors = []
        ctx = browser.new_context(user_agent=UA_DESKTOP,
                                  viewport={'width': 1280, 'height': 800})
        ctx.add_init_script("try{localStorage.setItem('app-theme','light')}catch(e){}")
        route_all(ctx)
        page = ctx.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(BASE + '/index.html')
        page.wait_for_timeout(1500)
        ui_login(page)
        page.evaluate("navigateTo('flowmeter-data')")
        page.wait_for_selector('.flow-card[data-flow-id="201"]', timeout=8000)
        page.wait_for_timeout(400)
        for mid, period, dc in [(201, 'Ежедневно', None), (202, 'Ежедневно', None),
                                (203, 'Еженедельно', None), (204, 'Еженедельно', None),
                                (205, 'Ежемесячно', None), (206, 'Ежемесячно', None),
                                (207, 'Ежедневно', None)]:
            pass
        exp = {201: False, 202: True, 203: True, 204: False, 205: True, 206: False, 207: True}
        for mid, want in exp.items():
            m = [x for x in STATE['meters'] if x['id'] == mid][0]
            py = is_overdue(m['period'], m['dateCurr'], now_real)
            check('Светлая: карточка %d (%s) — %s' %
                  (mid, m['period'], 'КРАСНЫЙ' if want else 'зелёный'),
                  due(page, mid) == want and py == want,
                  'класс: %s / py: %s' % (card_class(page, mid), py))
        check('Светлая: КРАСНЫЙ цвет = rgb(192, 57, 43)',
              card_color(page, 202) == 'rgb(192, 57, 43)', card_color(page, 202))
        check('Светлая: ЗЕЛЁНЫЙ цвет = rgb(90, 184, 112)',
              card_color(page, 201) == 'rgb(90, 184, 112)', card_color(page, 201))
        page.screenshot(path='scripts/task357-proof-light.png')
        check('C2: 0 JS-ошибок', len(errors) == 0, '; '.join(errors[:3]))
        ctx.close()

        # ================================================
        # Контекст 3: MOBILE + тёмная (реальное время)
        # ================================================
        print('=== 3. MOBILE dark: список + форма ввода ===')
        STATE['meters'] = build_meters_relative(now_real)
        REQUESTS.clear()
        errors = []
        ctx = browser.new_context(user_agent=UA_ANDROID,
                                  viewport={'width': 390, 'height': 780},
                                  is_mobile=True, has_touch=True)
        # kip8 (прод): обычный ключ темы, без префикса изоляции
        ctx.add_init_script("try{localStorage.setItem('app-theme','dark')}catch(e){}")
        route_all(ctx)
        page = ctx.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(BASE + '/index.html')
        page.wait_for_timeout(1500)
        ui_login(page)
        page.evaluate("navigateTo('flowmeter-data')")
        page.wait_for_selector('.flow-card[data-flow-id="201"]', timeout=8000)
        page.wait_for_timeout(400)
        check('MOBILE: карточка 202 (ежедн., 5 дн. назад) КРАСНАЯ', due(page, 202))
        check('MOBILE: карточка 204 (еженед., сегодня) зелёная', not due(page, 204))
        page.screenshot(path='scripts/task357-proof-mobile-list.png')
        # форма ввода на мобильном: карточка → детальная страница → нижний бар
        page.click('.flow-card[data-flow-id="202"] .flow-card-header')
        page.wait_for_selector('#page-flowmeter-detail.active', timeout=5000)
        page.wait_for_timeout(600)
        page.click('#flowDetailBottomBar .flow-input-btn')
        page.wait_for_selector('#flowInputSheet.active', timeout=5000)
        y_md = (now_real - datetime.timedelta(days=1))
        y_val = '%04d-%02d-%02d' % (y_md.year, y_md.month, y_md.day)
        got = page.evaluate("document.getElementById('flowInputDate').value")
        check('MOBILE: дефолт даты = предыдущие сутки (%s)' % y_val, got == y_val, got)
        page.screenshot(path='scripts/task357-proof-mobile-form.png')
        check('C3: 0 JS-ошибок', len(errors) == 0, '; '.join(errors[:3]))
        ctx.close()

        browser.close()

    print()
    print('=' * 60)
    for ok, name, detail in RESULTS:
        if not ok:
            print('FAIL: %s%s' % (name, (' — ' + detail) if detail else ''))
    failed = sum(1 for ok, _, _ in RESULTS if not ok)
    total = len(RESULTS)
    print('Итог Task 348 browser-check: %d/%d passed, %d failed' % (total - failed, total, failed))
    return failed


if __name__ == '__main__':
    import sys
    sys.exit(main())
