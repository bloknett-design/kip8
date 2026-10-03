#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 472: SMOKE переноса в kip8 (порт 8997, ключи localStorage БЕЗ
# префикса kip8test:) — «Плановые мероприятия»: поле ввода работ —
# textarea с авторостом вниз под новые строки (Enter — «Добавить»);
# кликабельные ячейки — вторая рамка-бевел (выпуклость кнопки);
# фон таблицы и окна непрозрачный (обе темы); окно в светлой теме —
# бежевое #f0eee6 (цвет фона бара) с толстой 3px рамкой-выступом;
# раскладка Task 468 и мобайл Task 464 живы; 0 JS-ошибок.
import json
import os
import threading
from datetime import date
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8997
SHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'download', 'kip8-task472')

TODAY_ISO = date.today().isoformat()
CUR_MONTH = date.today().month


def mock_response(action, body):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local', 'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'workschedule.view': True, 'workschedule.edit': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'planEvents.list':
        return {'ok': True, 'data': {'marks': [], 'srvVer': '471'}}
    if action == 'planEvents.years':
        return {'ok': True, 'data': {'years': [], 'srvVer': '471'}}
    if action == 'planWorks.list':
        y, m = body.get('year'), body.get('month')
        works = []
        if y == 2026 and m == (CUR_MONTH + 1 if CUR_MONTH < 12 else 1):
            works = [{'id': 201, 'год': y, 'месяц': m,
                      'работа': 'Плановая поверка манометров',
                      'статус': '', 'дата_статуса': ''}]
        return {'ok': True, 'data': {'works': works, 'srvVer': '471'}}
    if action == 'planWorks.add':
        return {'ok': True, 'data': {'work': {
            'id': 999, 'год': body.get('year'), 'месяц': body.get('month'),
            'работа': body.get('work'), 'статус': '', 'дата_статуса': ''}}}
    if action == 'planWorks.remove':
        return {'ok': True, 'data': {'removed': True}}
    if action == 'planWorks.setStatus':
        return {'ok': True, 'data': {'work': {
            'id': body.get('id'), 'статус': body.get('status'),
            'дата_статуса': body.get('date') or TODAY_ISO}}}
    return {'ok': True, 'data': {'ok': True}}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


PASS = 0
FAIL = 0
API_CALLS = []


def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(('  + ' if ok else '  X ') + name +
          (('  [' + str(extra)[:220] + ']') if (extra and not ok) else ''))


def shot(page, name):
    try:
        os.makedirs(SHOT_DIR, exist_ok=True)
        page.screenshot(path=os.path.join(SHOT_DIR, name))
    except Exception as e:
        print('  (скриншот %s не сохранён: %s)' % (name, e))


def calls(action):
    return [b for (a, b) in API_CALLS if a == action]


def click_name(page, text):
    page.evaluate("""(t) => {
        const tds = document.querySelectorAll('#peTable tbody td.pe-name');
        for (const td of tds) {
            if ((td.textContent || '').trim() === t) { td.click(); return true; }
        }
        return false;}""", text)


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
            "localStorage.setItem('kip8_session_token','sm-k472');" +
            "localStorage.setItem('app-theme','light');")

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
            API_CALLS.append((action, dict(body)))
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

        # ===== A: светлая тема — бежевое окно + бевел + рамка-выступ
        print('== A: светлая — бежевое окно, бевел, непрозрачность ==')
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('plan-events')")
        page.wait_for_timeout(1200)
        page.wait_for_timeout(400)
        st = page.evaluate("""(() => {
            const cs = (el) => el ? getComputedStyle(el) : null;
            const card = document.querySelector('#page-plan-events .pe-card');
            const win = document.querySelector('#page-plan-events .pe-desc-card');
            const tdM = document.querySelector('#peTable td.pe-m');
            const thMo = document.querySelector('#peTable tr.pe-head-months th');
            const grp = document.querySelector('#peTable tr.pe-group td');
            const c = cs(card), w = cs(win);
            return {theme: document.documentElement.getAttribute('data-theme'),
                    cardBg: c.backgroundColor, winBg: w.backgroundColor,
                    bw: w.borderTopWidth, bt: w.borderTopColor,
                    bb: w.borderBottomColor, sh: w.boxShadow,
                    tdM: cs(tdM).boxShadow, thMo: cs(thMo).boxShadow,
                    grp: cs(grp).boxShadow};})()""")
        check('тема светлая', st['theme'] == 'light', st['theme'])
        check('окно БЕЖЕВОЕ #f0eee6', st['winBg'] == 'rgb(240, 238, 230)',
              st['winBg'])
        check('карточка непрозрачная #faf9f6',
              st['cardBg'] == 'rgb(250, 249, 246)', st['cardBg'])
        check('фоны без альфы', 'rgba' not in st['winBg'] and
              'rgba' not in st['cardBg'], (st['winBg'], st['cardBg']))
        check('толстая рамка 3px', st['bw'] == '3px', st['bw'])
        check('рамка-выступ: светлее сверху, темнее снизу',
              st['bt'] == 'rgb(255, 253, 247)' and
              st['bb'] == 'rgb(200, 194, 175)', (st['bt'], st['bb']))
        check('бевел ячейки месяца (inset)', 'inset' in st['tdM'], st['tdM'])
        check('бевел месяца шапки (inset)', 'inset' in st['thMo'], st['thMo'])
        check('группа без бевела', st['grp'] == 'none', st['grp'])
        shot(page, 'smoke-k8-light.png')

        # ===== B: textarea с авторостом + Enter
        print('== B: авторост поля + Enter ==')
        click_name(page, 'Работы на следующий месяц')
        page.wait_for_timeout(700)
        inp = page.evaluate("""(() => {
            const ta = document.getElementById('peWorkInput');
            if (!ta) return null;
            const cs = getComputedStyle(ta);
            return {tag: ta.tagName, rows: ta.getAttribute('rows'),
                    h: Math.round(ta.getBoundingClientRect().height),
                    resize: cs.resize, overflow: cs.overflow};})()""")
        check('поле — TEXTAREA rows=1',
              inp and inp['tag'] == 'TEXTAREA' and inp['rows'] == '1', inp)
        check('resize none / overflow hidden',
              inp['resize'] == 'none' and inp['overflow'] == 'hidden',
              (inp['resize'], inp['overflow']))
        h0 = inp['h']
        page.fill('#peWorkInput',
                  'Ревизия запорной арматуры узла подготовки газа с полной '
                  'разборкой приводов, заменой уплотнений и последующей '
                  'опрессовкой системы импульсных линий, проверка '
                  'чувствительности датчиков давления и температуры')
        page.evaluate("document.getElementById('peWorkInput').dispatchEvent("
                      "new Event('input', {bubbles: true}))")
        page.wait_for_timeout(300)
        h1 = page.evaluate("""(() => {
            const ta = document.getElementById('peWorkInput');
            return ta ? Math.round(ta.getBoundingClientRect().height) : 0;})()""")
        check('длинный текст → поле выросло вниз', h1 >= h0 * 1.8, (h0, h1))
        API_CALLS.clear()
        page.press('#peWorkInput', 'Enter')
        page.wait_for_timeout(700)
        added = calls('planWorks.add')
        check('Enter добавляет работу (текст в payload)',
              len(added) == 1 and 'Ревизия' in (added[0].get('work') or ''),
              added)
        shot(page, 'smoke-k8-grow.png')

        # ===== C: тёмная тема — непрозрачность + авторост жив
        # (toggleTheme — без reload: init-script при каждой загрузке
        # перезаписывает app-theme на 'light', а обёртки-префикса
        # kip8test в kip8 нет)
        print('== C: тёмная тема ==')
        page.evaluate("toggleTheme()")
        page.wait_for_timeout(600)
        st = page.evaluate("""(() => {
            const card = document.querySelector('#page-plan-events .pe-card');
            const win = document.querySelector('#page-plan-events .pe-desc-card');
            const tdM = document.querySelector('#peTable td.pe-m');
            return {theme: document.documentElement.getAttribute('data-theme'),
                    cardBg: getComputedStyle(card).backgroundColor,
                    winBg: getComputedStyle(win).backgroundColor,
                    tdM: getComputedStyle(tdM).boxShadow};})()""")
        check('тема тёмная', st['theme'] == 'dark', st['theme'])
        check('карточка непрозрачная #17212e',
              st['cardBg'] == 'rgb(23, 33, 46)', st['cardBg'])
        check('окно непрозрачное #17212e',
              st['winBg'] == 'rgb(23, 33, 46)', st['winBg'])
        check('бевел ячейки (тёмная)', 'inset' in st['tdM'], st['tdM'])
        click_name(page, 'Работы на следующий месяц')
        page.wait_for_timeout(700)
        inp = page.evaluate("""(() => {
            const ta = document.getElementById('peWorkInput');
            return ta ? Math.round(ta.getBoundingClientRect().height) : 0;})()""")
        page.fill('#peWorkInput',
                  'Плановая поверка манометров с оформлением протоколов '
                  'и записью в журнал учёта средств измерений')
        page.evaluate("document.getElementById('peWorkInput').dispatchEvent("
                      "new Event('input', {bubbles: true}))")
        page.wait_for_timeout(300)
        h2 = page.evaluate("""(() => {
            const ta = document.getElementById('peWorkInput');
            return ta ? Math.round(ta.getBoundingClientRect().height) : 0;})()""")
        check('авторост в тёмной теме', h2 > inp, (inp, h2))
        shot(page, 'smoke-k8-dark.png')

        # ===== D: мобайл 375 — Task 464 жив + окно бежевое + авторост
        print('== D: 375px мобайл ==')
        page.set_viewport_size({'width': 375, 'height': 800})
        page.evaluate("toggleTheme()")
        page.wait_for_timeout(600)
        m = page.evaluate("""(() => {
            const rows = document.querySelectorAll('#peTable tbody tr.pe-row');
            let visible = 0;
            rows.forEach(tr => tr.querySelectorAll('td.pe-m').forEach(td => {
                if (getComputedStyle(td).display !== 'none'
                    && td.getBoundingClientRect().width > 0) visible++;
            }));
            const bar = document.querySelector('.pe-month-bar');
            const win = document.querySelector('.pe-desc-card');
            return {visible: visible,
                    bar: getComputedStyle(bar).display !== 'none',
                    winBg: getComputedStyle(win).backgroundColor};})()""")
        check('Task 464: 10 видимых ячеек месяца', m['visible'] == 10,
              m['visible'])
        check('полоса месяца видна', m['bar'], m)
        check('окно бежевое на мобайле',
              m['winBg'] == 'rgb(240, 238, 230)', m['winBg'])
        click_name(page, 'Работы на следующий месяц')
        page.wait_for_timeout(700)
        # база — ОДНА строка: очистим поле от текста секции C
        # (поля не пересоздаются — вид «next» уже был открыт)
        page.fill('#peWorkInput', '')
        page.evaluate("document.getElementById('peWorkInput').dispatchEvent("
                      "new Event('input', {bubbles: true}))")
        page.wait_for_timeout(200)
        h0 = page.evaluate("""(() => {
            const ta = document.getElementById('peWorkInput');
            return ta ? Math.round(ta.getBoundingClientRect().height) : 0;})()""")
        page.fill('#peWorkInput',
                  'Ревизия запорной арматуры узла подготовки газа с полной '
                  'разборкой приводов и заменой уплотнений')
        page.evaluate("document.getElementById('peWorkInput').dispatchEvent("
                      "new Event('input', {bubbles: true}))")
        page.wait_for_timeout(300)
        h1 = page.evaluate("""(() => {
            const ta = document.getElementById('peWorkInput');
            return ta ? Math.round(ta.getBoundingClientRect().height) : 0;})()""")
        check('авторост на мобайле', h1 >= h0 * 1.8, (h0, h1))
        check('0 JS-ошибок во всех сценариях', not js_errors, js_errors[:3])
        shot(page, 'smoke-k8-mobile.png')

        browser.close()
    server.shutdown()

    print()
    print('ИТОГ: %d OK, %d FAIL' % (PASS, FAIL))
    if FAIL:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
