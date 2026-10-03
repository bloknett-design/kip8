#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 470: SMOKE переноса в kip8 (порт 8997, ключи localStorage БЕЗ
# префикса kip8test:) — таблица «Плановых мероприятий»: точка «Ноя.»
# в шапке месяцев, мероприятие «Работы на следующий месяц» в группе
# «В конце месяца», НОВАЯ группа «На текущий месяц» с мероприятием
# «Работы на месяц»; диалог отметки Task 463 на новых строках жив;
# раскладка Task 468 и мобильный вид Task 464 не тронуты; 0 JS-ошибок.
import json
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8997
SHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'download', 'kip8-task470')


def mock_response(action, body):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local', 'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'workschedule.view': True, 'workschedule.edit': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'planEvents.list':
        return {'ok': True, 'data': {'marks': []}}
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
            "localStorage.setItem('kip8_session_token','sm-k470');" +
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
        page.evaluate("navigateTo('plan-events')")
        page.wait_for_timeout(1200)

        print('== A: 1600px — таблица Task 470 + раскладка Task 468 жива ==')
        g = page.evaluate("""(() => {
            const lay = document.querySelector('#page-plan-events .pe-layout');
            if (!lay) return {open: false};
            const card = lay.querySelector('.pe-card');
            const desc = lay.querySelector('.pe-desc-card');
            const table = lay.querySelector('.pe-table');
            const lr = lay.getBoundingClientRect();
            const cr = card.getBoundingClientRect();
            const dr = desc.getBoundingClientRect();
            const tr = table.getBoundingClientRect();
            const months = [...table.querySelectorAll('tr.pe-head-months th')]
                .map(th => th.textContent.trim());
            const groups = [...table.querySelectorAll('tr.pe-group td')]
                .map(td => td.textContent.trim());
            const rows = [...table.querySelectorAll('tbody tr.pe-row')].map(tr => ({
                name: tr.querySelector('td.pe-name').textContent.trim(),
                icons: tr.querySelectorAll('td.pe-m svg').length}));
            const lead = desc.querySelector('.pe-desc-lead');
            return {open: true,
                    dir: getComputedStyle(lay).flexDirection,
                    layR: lr.right, layL: lr.left,
                    cardL: cr.left, cardR: cr.right, cardW: cr.width,
                    descL: dr.left, descR: dr.right,
                    tabW: tr.width,
                    months: months, groups: groups, rows: rows,
                    lead: lead ? lead.textContent.trim() : '',
                    docW: document.documentElement.scrollWidth,
                    winW: window.innerWidth};})()""")
        check('раздел открыт, раскладка на месте', g.get('open'), g)
        check('ноябрь — «Ноя.» с точкой (11-я колонка)',
              len(g.get('months') or []) == 12 and g['months'][10] == 'Ноя.',
              g.get('months'))
        check('сокращения «Ноя» без точки нет',
              all(m != 'Ноя' for m in (g.get('months') or [])), g.get('months'))
        check('3 группы: В начале / В конце / На текущий месяц',
              g.get('groups') == ['В начале месяца', 'В конце месяца',
                                 'На текущий месяц'], g.get('groups'))
        rows = g.get('rows') or []
        check('10 строк мероприятий', len(rows) == 10, len(rows))
        check('9-я строка — «Работы на следующий месяц»',
              len(rows) == 10 and rows[8]['name'] == 'Работы на следующий месяц',
              [r['name'] for r in rows])
        check('10-я строка — «Работы на месяц»',
              len(rows) == 10 and rows[9]['name'] == 'Работы на месяц',
              [r['name'] for r in rows])
        check('иконки-крестики во всех 120 ячейках (Task 463 жив)',
              all(r['icons'] == 12 for r in rows) and len(rows) == 10,
              [(r['name'], r['icons']) for r in rows])
        check('flex-строка, карточка слева, окно справа (Task 468)',
              g.get('dir') == 'row' and g.get('descL', 0) >= g.get('cardR', 0) - 1, g)
        check('карточка прижата влево (±2)', abs(g.get('cardL', -99) - g.get('layL', -1)) <= 2, g)
        check('карточка обнимает таблицу (cardW - tabW <= 3)',
              g.get('cardW', 9) - g.get('tabW', 0) <= 3, g)
        check('окно описания до правого края раскладки (±2)',
              abs(g.get('descR', 0) - g.get('layR', 0)) <= 2, g)
        check('лид Task 469 жив (описание не тронуто)',
              g.get('lead') == 'Периодические работы на участке КИП ИОС, '
              'выполняемые в начале и в конце каждого месяца.', g.get('lead'))
        check('нет переполнения страницы',
              g.get('docW', 9e9) <= g.get('winW', 0) + 1, g)

        print('== B: клик по ячейке новой строки — диалог отметки ==')
        r = page.evaluate("""(() => {
            const tr = [...document.querySelectorAll('#peTable tbody tr.pe-row')]
                .find(r => r.querySelector('td.pe-name').textContent.trim()
                       === 'Работы на месяц');
            if (!tr) return {probe: false};
            tr.querySelectorAll('td.pe-m')[10].click();
            return {probe: true};})()""")
        page.wait_for_timeout(300)
        ds = page.evaluate("""(() => {
            const ov = document.getElementById('kipDialogOverlay');
            if (!ov || !ov.classList.contains('active')) return {open: false};
            return {open: true,
                    title: ov.querySelector('.kip-dialog-title').textContent.trim(),
                    msg: ov.querySelector('.kip-dialog-msg').textContent.trim()};})()""")
        check('клик по «Работы на месяц» (ноябрь) принят', r.get('probe'), r)
        check('диалог «Отметка выполнения»: «Работы на месяц — Ноябрь 2026»',
              ds.get('open') and ds.get('title') == 'Отметка выполнения' and
              ds.get('msg') == 'Работы на месяц — Ноябрь 2026', ds)
        page.evaluate("""(() => {
            const ov = document.getElementById('kipDialogOverlay');
            const b = ov.querySelector('.kip-dialog-cancel');
            if (b) b.click();})()""")
        page.wait_for_timeout(450)

        print('== C: 1100px — описание ПОД таблицей ==')
        page.set_viewport_size({'width': 1100, 'height': 900})
        page.wait_for_timeout(500)
        col = page.evaluate("""(() => {
            const lay = document.querySelector('#page-plan-events .pe-layout');
            const card = lay.querySelector('.pe-card');
            const desc = lay.querySelector('.pe-desc-card');
            return {dir: getComputedStyle(lay).flexDirection,
                    below: desc.getBoundingClientRect().top >=
                           card.getBoundingClientRect().bottom - 1};})()""")
        check('раскладка в колонку (column)', col.get('dir') == 'column', col)
        check('описание под таблицей', col.get('below'), col)

        print('== D: 375px — мобильный вид Task 464 жив ==')
        page.set_viewport_size({'width': 375, 'height': 812})
        page.wait_for_timeout(500)
        m = page.evaluate("""(() => {
            const bar = document.querySelector('#page-plan-events .pe-month-bar');
            const table = document.querySelector('#page-plan-events .pe-table');
            const visMonths = [...table.querySelectorAll('td.pe-m')]
                .filter(td => getComputedStyle(td).display !== 'none'
                    && td.getBoundingClientRect().width > 0).length;
            const lastRow = [...table.querySelectorAll('tbody tr.pe-row')]
                .pop().querySelector('td.pe-name').textContent.trim();
            return {barVisible: bar ? getComputedStyle(bar).display !== 'none' : false,
                    visMonths: visMonths, lastRow: lastRow,
                    docW: document.documentElement.scrollWidth,
                    winW: window.innerWidth};})()""")
        check('полоса месяца видна (Task 464)', m.get('barVisible'), m)
        check('один столбец месяца: 10 видимых ячеек (было 8)',
              m.get('visMonths') == 10, m)
        check('последняя строка — «Работы на месяц»',
              m.get('lastRow') == 'Работы на месяц', m)
        check('нет переполнения страницы',
              m.get('docW', 9e9) <= m.get('winW', 0) + 1, m)

        try:
            os.makedirs(SHOT_DIR, exist_ok=True)
            page.set_viewport_size({'width': 1600, 'height': 1000})
            page.wait_for_timeout(300)
            page.screenshot(path=os.path.join(SHOT_DIR, 'smoke-k8-desktop.png'))
        except Exception as e:
            print('  (скриншот не сохранён: %s)' % e)

        browser.close()
        server.shutdown()

    print('\nSMOKE ИТОГ: %d OK / %d FAIL' % (PASS, FAIL))
    if js_errors:
        print('JS-ОШИБКИ (%d):' % len(js_errors))
        for e in js_errors[:10]:
            print('  ! ' + e[:300])
    else:
        print('JS-ошибок нет (0)')
    raise SystemExit(1 if (FAIL or js_errors) else 0)


if __name__ == '__main__':
    main()
