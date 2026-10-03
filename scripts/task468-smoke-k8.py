#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 468: SMOKE переноса в kip8 (порт 8997, ключи localStorage БЕЗ
# префикса kip8test:) — раскладка раздела «Плановые мероприятия»:
# таблица влево экрана строго по контенту (столбец «Мероприятия» по
# самому длинному тексту), справа окно «Описание раздела» на всё
# оставшееся место; 1100px — описание под таблицей; 375px —
# мобильный вид Task 464 жив (полоса месяца, один столбец), 0
# JS-ошибок.
import json
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8997
SHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'download', 'kip8-task468')


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
            "localStorage.setItem('kip8_session_token','sm-k468');" +
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

        print('== A: 1600px — таблица влево по контенту, описание справа ==')
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
            const names = [...lay.querySelectorAll('td.pe-name')];
            const maxNameH = names.reduce((m, td) =>
                Math.max(m, td.getBoundingClientRect().height), 0);
            return {open: true,
                    dir: getComputedStyle(lay).flexDirection,
                    layL: lr.left, layR: lr.right, layW: lr.width,
                    cardL: cr.left, cardR: cr.right, cardW: cr.width,
                    descL: dr.left, descR: dr.right, descW: dr.width,
                    tabW: tr.width,
                    maxNameH: maxNameH,
                    title: desc.querySelector('.pe-desc-title').textContent.trim(),
                    items: desc.querySelectorAll('.pe-desc-list li').length,
                    docW: document.documentElement.scrollWidth,
                    winW: window.innerWidth};})()""")
        check('раздел открыт, раскладка на месте', g.get('open'), g)
        check('flex-строка (row), карточка слева, окно справа',
              g.get('dir') == 'row' and g.get('descL', 0) >= g.get('cardR', 0) - 1, g)
        check('карточка обнимает таблицу (cardW - tabW <= 3)',
              g.get('cardW', 9) - g.get('tabW', 0) <= 3, g)
        check('окно описания до правого края раскладки (±2)',
              abs(g.get('descR', 0) - g.get('layR', 0)) <= 2, g)
        check('заголовок «Описание раздела», 5 пунктов',
              g.get('title') == 'Описание раздела' and g.get('items') == 5, g)
        check('наименования в одну строку (maxNameH <= 40)',
              g.get('maxNameH', 99) <= 40, g)
        check('нет переполнения страницы',
              g.get('docW', 9e9) <= g.get('winW', 0) + 1, g)
        try:
            os.makedirs(SHOT_DIR, exist_ok=True)
            page.screenshot(path=os.path.join(SHOT_DIR, 'smoke-k8-desktop.png'))
        except Exception as e:
            print('  (скриншот не сохранён: %s)' % e)

        print('== B: 1100px — описание ПОД таблицей ==')
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

        print('== C: 375px — мобильный вид Task 464 жив ==')
        page.set_viewport_size({'width': 375, 'height': 812})
        page.wait_for_timeout(500)
        m = page.evaluate("""(() => {
            const bar = document.querySelector('#page-plan-events .pe-month-bar');
            const table = document.querySelector('#page-plan-events .pe-table');
            const lay = document.querySelector('#page-plan-events .pe-layout');
            const card = lay.querySelector('.pe-card');
            const desc = lay.querySelector('.pe-desc-card');
            const visMonths = [...table.querySelectorAll('td.pe-m')]
                .filter(td => getComputedStyle(td).display !== 'none'
                    && td.getBoundingClientRect().width > 0).length;
            return {barVisible: bar ? getComputedStyle(bar).display !== 'none' : false,
                    visMonths: visMonths,
                    nameWS: getComputedStyle(table.querySelector('td.pe-name')).whiteSpace,
                    descBelow: desc.getBoundingClientRect().top >=
                               card.getBoundingClientRect().bottom - 1,
                    docW: document.documentElement.scrollWidth,
                    winW: window.innerWidth};})()""")
        check('полоса месяца видна (Task 464)', m.get('barVisible'), m)
        check('один столбец месяца (8 видимых ячеек)',
              m.get('visMonths') == 8, m)
        check('наименования переносятся (normal)', m.get('nameWS') == 'normal', m)
        check('описание под таблицей', m.get('descBelow'), m)
        check('нет переполнения страницы',
              m.get('docW') <= m.get('winW') + 1, m)

        browser.close()
        server.shutdown()

    print('\nИТОГ: %d OK / %d FAIL' % (PASS, FAIL))
    if js_errors:
        print('JS-ОШИБКИ (%d):' % len(js_errors))
        for e in js_errors[:10]:
            print('  ! ' + e[:300])
    else:
        print('JS-ошибок нет (0)')
    raise SystemExit(1 if (FAIL or js_errors) else 0)


if __name__ == '__main__':
    main()
