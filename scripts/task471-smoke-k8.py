#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 471: SMOKE переноса в kip8 (порт 8997, ключи localStorage БЕЗ
# префикса kip8test:) — «Плановые мероприятия»: кнопка «◀» слева от
# «2026 год» (активна при архиве за предыдущие годы, клик → 2025 →
# возврат 2026); месяцы шапки кликабельны (подсветка выбранного);
# динамичное окно: «Работы на следующий месяц» — интерфейс ввода
# (Ноябрь 2026; Декабрь → Январь 2027), «Работы на месяц» — перечень
# с кнопками Выполнено/Частично/Не выполнено (planWorks.setStatus),
# «Мероприятия» — снова описание; раскладка Task 468 и мобайл
# Task 464 живы; 0 JS-ошибок.
import json
import os
import threading
from datetime import date
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8997
SHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'download', 'kip8-task471')

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
        return {'ok': True, 'data': {'years': [2025], 'srvVer': '471'}}
    if action == 'planWorks.list':
        y, m = body.get('year'), body.get('month')
        works = []
        if y == 2026 and m == CUR_MONTH:
            works = [{'id': 101, 'год': y, 'месяц': m,
                      'работа': 'Проверка датчиков давления КИП',
                      'статус': '', 'дата_статуса': ''},
                     {'id': 102, 'год': y, 'месяц': m,
                      'работа': 'Ревизия импульсных линий',
                      'статус': 'частично', 'дата_статуса': '2026-10-01'}]
        elif y == 2026 and m == 11:
            works = [{'id': 201, 'год': y, 'месяц': m,
                      'работа': 'Плановая поверка манометров',
                      'статус': '', 'дата_статуса': ''}]
        elif y == 2027 and m == 1:
            works = [{'id': 301, 'год': y, 'месяц': m,
                      'работа': 'Подготовка к отопительному сезону',
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


def calls(action):
    return [b for (a, b) in API_CALLS if a == action]


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
            "localStorage.setItem('kip8_session_token','sm-k471');" +
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

        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('plan-events')")
        page.wait_for_timeout(1400)

        st = page.evaluate("""(() => {
            const dv = document.getElementById('peDescView');
            const wv = document.getElementById('peWorksView');
            const btn = document.getElementById('pePrevYearBtn');
            const label = document.getElementById('peYearLabel');
            const selTh = document.querySelector('tr.pe-head-months th.pe-mo-sel');
            return {descHidden: dv ? dv.hidden : null,
                    worksHidden: wv ? wv.hidden : null,
                    btnDisabled: btn ? btn.disabled : null,
                    label: label ? label.textContent : '',
                    selMonth: selTh ? selTh.textContent.trim() : ''};})()""")
        check('описание раздела видно (Task 469 жив)',
              st['descHidden'] is False and st['worksHidden'] is True, st)
        check('подпись «2026 год», кнопка годов АКТИВНА (архив 2025)',
              st['label'] == '2026 год' and st['btnDisabled'] is False, st)
        check('текущий месяц подсвечен', st['selMonth'] != '', st)
        check('planEvents.years запрошен (мок-архив 2025)',
              len(calls('planEvents.years')) >= 1)

        # Кнопка годов: 2026 → 2025 → 2026
        API_CALLS.clear()
        page.evaluate("document.getElementById('pePrevYearBtn').click()")
        page.wait_for_timeout(600)
        st = page.evaluate("""(() => ({
            label: document.getElementById('peYearLabel').textContent}))()""")
        check('клик «◀»: шапка «2025 год»', st['label'] == '2025 год', st)
        check('отметки перезагружены за 2025',
              any(c.get('year') == 2025 for c in calls('planEvents.list')))
        page.evaluate("document.getElementById('pePrevYearBtn').click()")
        page.wait_for_timeout(600)
        st = page.evaluate("""(() => ({
            label: document.getElementById('peYearLabel').textContent}))()""")
        check('повторный клик: возврат «2026 год»', st['label'] == '2026 год', st)

        # «Работы на следующий месяц» — интерфейс ввода (Ноябрь 2026)
        API_CALLS.clear()
        page.evaluate("""(() => {
            const tds = document.querySelectorAll('#peTable tbody td.pe-name');
            for (const td of tds) {
                if ((td.textContent || '').trim() === 'Работы на следующий месяц') {
                    td.click(); return;}}})()""")
        page.wait_for_timeout(800)
        st = page.evaluate("""(() => {
            const wv = document.getElementById('peWorksView');
            const items = wv ? [...wv.querySelectorAll('.pe-work-item')].map(it => ({
                text: (it.querySelector('.pe-work-text') || {}).textContent || '',
                del: !!it.querySelector('.pe-work-del')})) : [];
            return {hidden: wv ? wv.hidden : null,
                    title: wv ? ((wv.querySelector('.pe-desc-title') || {}).textContent || '') : '',
                    target: wv ? ((wv.querySelector('.pe-works-target') || {}).textContent || '') : '',
                    hasInput: !!document.getElementById('peWorkInput'),
                    items: items};})()""")
        check('вид ввода: заголовок + Ноябрь 2026 (тек. месяц + 1)',
              st['title'] == 'Работы на следующий месяц' and
              'Ноябрь 2026' in st['target'], st)
        check('интерфейс ввода: поле описания есть', st['hasInput'], st)
        check('работа мока в перечне', len(st['items']) >= 1, st['items'])
        page.fill('#peWorkInput', 'Продувка импульсных линий РО-1')
        page.click('#peWorkAddBtn')
        page.wait_for_timeout(800)
        added = calls('planWorks.add')
        check('planWorks.add ушёл с текстом работы',
              len(added) == 1 and 'Продувка' in added[0].get('work', ''), added)

        # «Мероприятия» — снова описание
        page.evaluate("document.querySelector('#peTable th.pe-th-name').click()")
        page.wait_for_timeout(400)
        st = page.evaluate("""(() => ({
            desc: !document.getElementById('peDescView').hidden,
            works: document.getElementById('peWorksView').hidden}))()""")
        check('«Мероприятия»: снова описание раздела',
              st['desc'] is True and st['works'] is True, st)

        # «Работы на месяц» — перечень + статусы
        API_CALLS.clear()
        page.evaluate("""(() => {
            const tds = document.querySelectorAll('#peTable tbody td.pe-name');
            for (const td of tds) {
                if ((td.textContent || '').trim() === 'Работы на месяц') {
                    td.click(); return;}}})()""")
        page.wait_for_timeout(800)
        st = page.evaluate("""(() => {
            const wv = document.getElementById('peWorksView');
            const items = wv ? [...wv.querySelectorAll('.pe-work-item')].map(it => ({
                stBtns: [...it.querySelectorAll('.pe-work-st-btn')].map(b => ({
                    st: b.getAttribute('data-st'),
                    sel: b.classList.contains('st-sel')})),
                status: (it.querySelector('.pe-work-status') || {}).textContent || ''})) : [];
            return {title: wv ? ((wv.querySelector('.pe-desc-title') || {}).textContent || '') : '',
                    target: wv ? ((wv.querySelector('.pe-works-target') || {}).textContent || '') : '',
                    items: items};})()""")
        check('вид перечня: заголовок + Октябрь 2026 (текущий месяц)',
              st['title'] == 'Работы на месяц' and
              'Октябрь 2026' in st['target'], st)
        check('3 кнопки статуса у работ', all(
              [b['st'] for b in it['stBtns']] ==
              ['выполнено', 'частично', 'не выполнено'] for it in st['items']),
              st['items'])
        page.evaluate("""(() => {
            const it = document.querySelector('#peWorksView .pe-work-item');
            it.querySelector('.pe-work-st-btn[data-st="выполнено"]').click();})()""")
        page.wait_for_timeout(800)
        sts = calls('planWorks.setStatus')
        check('planWorks.setStatus {выполнено, дата сегодня}',
              len(sts) == 1 and sts[0].get('status') == 'выполнено' and
              sts[0].get('date') == TODAY_ISO, sts)
        st = page.evaluate("""(() => {
            const it = document.querySelector('#peWorksView .pe-work-item');
            return {status: (it.querySelector('.pe-work-status') || {}).textContent || '',
                    sel: it.querySelector('.pe-work-st-btn').classList.contains('st-sel')};})()""")
        check('бейдж «Выполнено — дата» + подсветка кнопки',
              'Выполнено' in st['status'] and st['sel'], st)

        # Месяцы шапки: Декабрь + «следующий месяц» → Январь 2027
        page.evaluate("""(() => {
            const tds = document.querySelectorAll('#peTable tbody td.pe-name');
            for (const td of tds) {
                if ((td.textContent || '').trim() === 'Работы на следующий месяц') {
                    td.click(); return;}}})()""")
        page.wait_for_timeout(600)
        page.evaluate("""(() => {
            const ths = document.querySelectorAll('tr.pe-head-months th');
            if (ths[11]) ths[11].click();})()""")
        page.wait_for_timeout(800)
        st = page.evaluate("""(() => ({
            target: ((document.querySelector('#peWorksView .pe-works-target') || {}).textContent || ''),
            sel: (document.querySelector('tr.pe-head-months th.pe-mo-sel') || {}).textContent || ''}))()""")
        check('Декабрь + «следующий месяц» → Январь 2027 (переход года)',
              'Январь 2027' in st['target'], st)
        check('подсветка шапки — «Дек.»', st['sel'] == 'Дек.', st)

        # Раскладка 468 жива
        g = page.evaluate("""(() => {
            const lay = document.querySelector('#page-plan-events .pe-layout');
            const card = lay.querySelector('.pe-card');
            const desc = lay.querySelector('.pe-desc-card');
            return {dir: getComputedStyle(lay).flexDirection,
                    cardL: card.getBoundingClientRect().left,
                    descL: desc.getBoundingClientRect().left};})()""")
        check('раскладка Task 468 жива (строка, окно справа)',
              g['dir'] == 'row' and g['descL'] > g['cardL'], g)

        # Мобайл Task 464 жив
        page.set_viewport_size({'width': 375, 'height': 800})
        page.wait_for_timeout(500)
        m = page.evaluate("""(() => {
            let visible = 0;
            document.querySelectorAll('#peTable tbody td.pe-m').forEach(td => {
                if (getComputedStyle(td).display !== 'none'
                    && td.getBoundingClientRect().width > 0) visible++;
            });
            const bar = document.querySelector('.pe-month-bar');
            return {visible: visible,
                    barVisible: getComputedStyle(bar).display !== 'none'};})()""")
        check('мобайл Task 464: 10 видимых ячеек (один месяц)',
              m['visible'] == 10 and m['barVisible'], m)
        check('0 JS-ошибок', not js_errors, js_errors[:3])

        try:
            os.makedirs(SHOT_DIR, exist_ok=True)
            page.screenshot(path=os.path.join(SHOT_DIR, 'smoke-k8-471.png'))
        except Exception as e:
            print('  (скриншот не сохранён: %s)' % e)
        browser.close()
    server.shutdown()

    print()
    print('ИТОГ: %d OK, %d FAIL' % (PASS, FAIL))
    if FAIL:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
