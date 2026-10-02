#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 463-464 SMOKE (kip8): перенос партии из kip8test@de669b9f —
#   Task 463: «Плановые мероприятия» — интерактивные отметки +
#   архив файла Мероприятия_КИП_ИОС (PlanEvents.gs);
#   Task 464: полировка — правка даты/снятие отметки, «Подтвердить»
#   + красная «Отмена», ширина колонки по тексту, мобильная
#   компактность (селектор месяца + один столбец).
# Ключи kip8 БЕЗ префикса kip8test: (де-изоляция переноса).
# КОНТЕКСТ (мок-сервер, порт 8997, STATEFUL update/unmark):
#   A: «КИП ИОС», plan.events ✓ — раздел: таблица, 2 отметки с
#      сервера (94 крестика + 2 галочки), подсказки НЕТ, колонка
#      nowrap, селектор месяца скрыт на десктопе;
#   B: диалог [Отмена pe-cancel-red][Подтвердить] → mark → галочка
#      + title + тост;
#   C: клик по отмеченной → «Изменение отметки» (3 кнопки, дата
#      prefill) → смена даты → update → title обновился;
#   D: «Удалить отметку» → unmark → крестик + тост «Отметка снята»;
#   E: мобайл 375 — селектор = текущий месяц, виден один столбец
#      месяца, таблица влезает, выбор «Декабрь» + отметка;
#   F: «КИП ИОС», plan.events ✗ — раздел скрыт, хаб «Документация
#      ИОС» ЖИВ, прямой переход → «Нет доступа»;
#   0 JS-ошибок во всех контекстах; скриншоты в
#   download/kip8-task463-464-transfer/.
import datetime
import json
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8997

PASS = 0
FAIL = 0
SHOT_DIR = '/home/z/my-project/download/kip8-task463-464-transfer'
os.makedirs(SHOT_DIR, exist_ok=True)

STATE = {
    'marks': [],
    'next_id': 1,
    'log': [],
    'perms': {'kipios.view': True, 'plan.events': True},
}


def today_iso():
    return datetime.date.today().isoformat()


def api_response(action, body):
    st = STATE
    st['log'].append({'action': action, 'body': body})
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local',
                'role': 'КИП ИОС'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'КИП ИОС', 'found': True,
                'permissions': dict(st['perms'])}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'planEvents.list':
        return {'ok': True, 'data': {'marks': st['marks'], 'srvVer': '464'}}
    if action == 'planEvents.mark':
        year, month, event, date = (body.get('year'), body.get('month'),
                                    body.get('event'), body.get('date'))
        for m in st['marks']:
            if (m['год'] == year and m['месяц'] == month and
                    m['мероприятие'] == event):
                return {'ok': True, 'data': {'mark': m, 'already': True}}
        m = {'id': st['next_id'], 'дата_выполнения': date,
             'мероприятие': event, 'год': year, 'месяц': month}
        st['next_id'] += 1
        st['marks'].append(m)
        return {'ok': True, 'data': {'mark': m, 'already': False}}
    if action == 'planEvents.update':
        year, month, event, date = (body.get('year'), body.get('month'),
                                    body.get('event'), body.get('date'))
        for m in st['marks']:
            if (m['год'] == year and m['месяц'] == month and
                    m['мероприятие'] == event):
                m['дата_выполнения'] = date
                return {'ok': True, 'data': {'mark': m}}
        return {'ok': False, 'error': 'not_found',
                'message': 'Отметка не найдена — нажмите «Обновить»'}
    if action == 'planEvents.unmark':
        year, month, event = (body.get('year'), body.get('month'),
                              body.get('event'))
        for m in st['marks']:
            if (m['год'] == year and m['месяц'] == month and
                    m['мероприятие'] == event):
                st['marks'].remove(m)
                return {'ok': True, 'data': {'removed': True}}
        return {'ok': True, 'data': {'removed': False}}
    return {'ok': True, 'data': {'ok': True}}


def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(('  + ' if ok else '  X ') + name +
          (('  [' + str(extra)[:200] + ']') if (extra and not ok) else ''))


def attach(page, ctx, theme, tag):
    js_errors = []
    page.on('pageerror', lambda e: js_errors.append(str(e)))
    page.on('dialog', lambda dlg: dlg.accept())
    # Ключи kip8 БЕЗ префикса (де-изоляция)
    ctx.add_init_script(
        "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
        "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
        "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
        "localStorage.setItem('kip8_session_token','sm-k463-%s');" % tag +
        "localStorage.setItem('app-theme','%s');" % theme)

    def handle(route, request):
        action = ''
        if 'action=' in request.url:
            action = unquote(request.url.split('action=')[1].split('&')[0])
        body = {}
        if request.post_data:
            try:
                body = json.loads(request.post_data)
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
                      body='not found (k463-%s)' % tag)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)
    return js_errors


def shot(page, name):
    try:
        page.screenshot(path=os.path.join(SHOT_DIR, name))
    except Exception as e:
        print('  (скриншот %s не сохранён: %s)' % (name, e))


def open_plan_events(page):
    page.goto('http://localhost:%d/index.html' % PORT)
    page.wait_for_timeout(2500)
    page.evaluate("navigateTo('plan-events')")
    page.wait_for_timeout(700)


def toast_text(page):
    return page.evaluate("""(() => {
        const t = document.getElementById('toast');
        const m = document.getElementById('toastMessage');
        return {shown: !!(t && t.classList.contains('show')),
                text: m ? m.textContent : ''};})()""")


def cell_by_event_month(page, event, month):
    return page.evaluate("""(([ev, mn]) => {
        const rows = document.querySelectorAll('#peTable tbody tr.pe-row');
        for (const tr of rows) {
            const nm = tr.querySelector('td.pe-name');
            if (!nm || nm.textContent.trim() !== ev) continue;
            const td = tr.querySelectorAll('td.pe-m')[mn - 1];
            if (!td) return null;
            return {done: td.classList.contains('pe-m-done'),
                    cross: !!td.querySelector('.pe-ic-cross'),
                    check: !!td.querySelector('.pe-ic-check'),
                    visible: !!td.offsetParent,
                    title: td.getAttribute('title') || '',
                    ws: getComputedStyle(td.closest('tr').querySelector('.pe-name')).whiteSpace};
        }
        return null;})""", [event, month])


def click_cell(page, event, month):
    page.evaluate("""(([ev, mn]) => {
        const rows = document.querySelectorAll('#peTable tbody tr.pe-row');
        for (const tr of rows) {
            const nm = tr.querySelector('td.pe-name');
            if (!nm || nm.textContent.trim() !== ev) continue;
            const td = tr.querySelectorAll('td.pe-m')[mn - 1];
            if (td) td.click();
        }})""", [event, month])


def dialog_state(page):
    return page.evaluate("""(() => {
        const ov = document.getElementById('kipDialogOverlay');
        const d = ov ? ov.querySelector('.pe-dialog') : null;
        if (!d) return null;
        const btns = [...d.querySelectorAll('.kip-dialog-btn')].map(b => ({
            text: b.textContent.trim(), cls: b.className}));
        return {title: (d.querySelector('.kip-dialog-title')||{}).textContent || '',
                msg: (d.querySelector('.kip-dialog-msg')||{}).textContent || '',
                date: (d.querySelector('#peDialogDate')||{}).value || '',
                btns: btns};})()""")


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        # ===== A: план ✓ — таблица + отметки сервера + нет подсказки =====
        print('=== Контекст A: план ✓ — раздел, отметки сервера ===')
        STATE['marks'] = [
            {'id': 1, 'дата_выполнения': '2026-02-05', 'мероприятие': 'Проверка огнетушителей', 'год': 2026, 'месяц': 2},
            {'id': 2, 'дата_выполнения': '2026-05-21', 'мероприятие': 'Отчёт по талонам', 'год': 2026, 'месяц': 5},
        ]
        STATE['log'] = []
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        jsA = attach(page, ctx, 'dark', 'a')
        open_plan_events(page)
        check('A1: страница активна',
              page.evaluate("!!document.querySelector('#page-plan-events.active')"))
        signs = page.evaluate("""(() => {
            const all = document.querySelectorAll('#peTable td.pe-m');
            const done = document.querySelectorAll('#peTable td.pe-m.pe-m-done');
            const bar = document.querySelector('.pe-month-bar');
            return {total: all.length, done: done.length,
                    bar: bar ? getComputedStyle(bar).display : 'нет'};})()""")
        check('A2: 96 ячеек, 2 отметки сервера (stateful мок)',
              signs['total'] == 96 and signs['done'] == 2, signs)
        check('A3: подсказки НЕТ (Task 464)',
              page.evaluate("!document.getElementById('peHint')"))
        check('A4: селектор месяца скрыт на десктопе',
              signs['bar'] == 'none', signs)
        c = cell_by_event_month(page, 'Проверка огнетушителей', 2)
        check('A5: галочка февраля + title + nowrap (Task 464)',
              c and c['done'] and 'Выполнено 05.02.2026' in c['title']
              and c['ws'] == 'nowrap', c)
        shot(page, '01-desktop-no-hint.png')

        # ===== B: диалог подтверждения (кнопки Task 464) → mark =====
        click_cell(page, 'Проверка СИЗ в электроустановках', 3)
        page.wait_for_timeout(400)
        dlg = dialog_state(page)
        check('B1: диалог «Отметка выполнения», кнопки [Отмена red][Подтвердить]',
              dlg and 'Отметка выполнения' in dlg['title']
              and len(dlg['btns']) == 2
              and 'pe-cancel-red' in dlg['btns'][0]['cls']
              and dlg['btns'][1]['text'] == 'Подтвердить', dlg and dlg['btns'])
        page.fill('#peDialogDate', '2026-03-11')
        page.click('#kipDialogOverlay .kip-dialog-ok')
        page.wait_for_timeout(700)
        sent = [l['body'] for l in STATE['log'] if l['action'] == 'planEvents.mark']
        check('B2: mark payload {token, year, month, event, date}',
              sent and sent[-1].get('year') == 2026
              and sent[-1].get('month') == 3 and 'token' in sent[-1]
              and sent[-1].get('date') == '2026-03-11', sent[-1] if sent else None)
        c = cell_by_event_month(page, 'Проверка СИЗ в электроустановках', 3)
        check('B3: зелёная галочка + title 11.03.2026',
              c and c['done'] and 'Выполнено 11.03.2026' in c['title'], c)
        t = toast_text(page)
        check('B4: тост «Выполнение отмечено»',
              t['shown'] and 'Выполнение отмечено' in t['text'], t)
        check('B5: 0 JS-ошибок', len(jsA) == 0, jsA[:3])
        ctx.close()

        # ===== C: правка даты (Task 464) =====
        print('=== Контекст C: правка даты отметки ===')
        STATE['log'] = []
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        jsC = attach(page, ctx, 'dark', 'c')
        open_plan_events(page)
        c = cell_by_event_month(page, 'Проверка СИЗ в электроустановках', 3)
        check('C0: отметка B пришла с сервера (stateful)',
              c and c['done'], c)
        click_cell(page, 'Проверка СИЗ в электроустановках', 3)
        page.wait_for_timeout(400)
        dlg = dialog_state(page)
        check('C1: «Изменение отметки» — 3 кнопки, дата prefill 11.03',
              dlg and 'Изменение отметки' in dlg['title']
              and dlg['date'] == '2026-03-11' and len(dlg['btns']) == 3
              and dlg['btns'][1]['text'] == 'Удалить отметку', dlg)
        page.fill('#peDialogDate', '2026-03-25')
        page.click('#kipDialogOverlay .kip-dialog-ok')
        page.wait_for_timeout(700)
        upd = [l['body'] for l in STATE['log'] if l['action'] == 'planEvents.update']
        check('C2: update payload (Task 464)',
              upd and upd[-1].get('date') == '2026-03-25'
              and 'token' in upd[-1], upd[-1] if upd else None)
        c = cell_by_event_month(page, 'Проверка СИЗ в электроустановках', 3)
        check('C3: title обновился «Выполнено 25.03.2026»',
              c and 'Выполнено 25.03.2026' in c['title'], c)
        t = toast_text(page)
        check('C4: тост «Дата отметки обновлена»',
              t['shown'] and 'Дата отметки обновлена' in t['text'], t)
        shot(page, '02-edit-dialog.png')

        # ===== D: снятие отметки (Task 464) =====
        click_cell(page, 'Проверка СИЗ в электроустановках', 3)
        page.wait_for_timeout(400)
        page.click('#kipDialogOverlay .pe-unmark-btn')
        page.wait_for_timeout(700)
        unm = [l['body'] for l in STATE['log'] if l['action'] == 'planEvents.unmark']
        check('D1: unmark payload БЕЗ date',
              unm and 'date' not in unm[-1] and 'token' in unm[-1],
              unm[-1] if unm else None)
        c = cell_by_event_month(page, 'Проверка СИЗ в электроустановках', 3)
        check('D2: ячейка — крестик',
              c and not c['done'] and c['cross'], c)
        t = toast_text(page)
        check('D3: тост «Отметка снята»',
              t['shown'] and 'Отметка снята' in t['text'], t)
        check('D4: 0 JS-ошибок', len(jsC) == 0, jsC[:3])
        ctx.close()

        # ===== E: мобайл 375 — селектор месяца + один столбец =====
        print('=== Контекст E: мобайл 375 — компактность ===')
        STATE['log'] = []
        ctx = browser.new_context(viewport={'width': 375, 'height': 812})
        page = ctx.new_page()
        jsE = attach(page, ctx, 'light', 'e')
        open_plan_events(page)
        cur = datetime.date.today().month
        sel = page.evaluate("""(() => {
            const s = document.getElementById('peMonthSel');
            const bar = document.querySelector('.pe-month-bar');
            return {display: bar ? getComputedStyle(bar).display : '',
                    value: s ? s.value : '', options: s ? s.options.length : 0};})()""")
        check('E1: селектор ВИДЕН (flex) = текущий месяц (%d)' % cur,
              sel['display'] == 'flex' and sel['value'] == str(cur), sel)
        check('E2: 12 опций', sel['options'] == 12, sel)
        vis = page.evaluate("""((cur) => {
            const cells = [...document.querySelectorAll('#peTable td.pe-m')];
            const ths = [...document.querySelectorAll('#peTable tr.pe-head-months th')];
            return {cells: cells.filter(td => td.offsetParent).length,
                    th: ths.filter(th => th.offsetParent).length,
                    cur: cells.filter(td => td.offsetParent && td.classList.contains('pe-mo-' + cur)).length};})""", cur)
        check('E3: видим только ОДИН месяц (шапка 1, ячеек 8)',
              vis['th'] == 1 and vis['cells'] == 8 and vis['cur'] == 8, vis)
        fit = page.evaluate("""(() => {
            const w = document.querySelector('.pe-grid-wrap');
            return {scroll: w.scrollWidth, client: w.clientWidth};})()""")
        check('E4: таблица влезает (scroll<=client)',
              fit['scroll'] <= fit['client'], fit)
        page.select_option('#peMonthSel', '12')
        page.wait_for_timeout(400)
        click_cell(page, 'График смен на следующий месяц', 12)
        page.wait_for_timeout(400)
        dlg = dialog_state(page)
        check('E5: диалог в выбранном месяце (Декабрь)',
              dlg and 'Декабрь' in dlg['msg'], dlg and dlg['msg'])
        page.click('#kipDialogOverlay .kip-dialog-ok')
        page.wait_for_timeout(700)
        c = cell_by_event_month(page, 'График смен на следующий месяц', 12)
        check('E6: декабрьская отметка поставлена',
              c and c['done'], c)
        shot(page, '03-mobile-december.png')
        check('E7: 0 JS-ошибок', len(jsE) == 0, jsE[:3])
        ctx.close()

        # ===== F: план ✗ — доступ снят =====
        print('=== Контекст F: план ✗ — нет доступа ===')
        STATE['perms'] = {'kipios.view': True, 'plan.events': False}
        STATE['marks'] = []
        STATE['log'] = []
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        jsF = attach(page, ctx, 'dark', 'f')
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        hub = page.evaluate("""(() => {
            const b = document.getElementById('planEventsMenuBtn');
            return b ? b.style.display : 'нет элемента';})()""")
        check('F1: кнопка раздела СКРЫТА (style.display none)',
              hub == 'none', hub)
        page.evaluate("navigateTo('plan-events')")
        page.wait_for_timeout(400)
        na = page.evaluate("""(() => {
            const p = document.getElementById('page-plan-events');
            const nd = document.getElementById('noAccessScreen');
            return {active: !!(p && p.classList.contains('active')),
                    noAccess: !!(nd && nd.style.display !== 'none')};})()""")
        check('F2: прямой переход → «Нет доступа», страница НЕ активна',
              (not na['active']) and na['noAccess'], na)
        check('F3: хаб «Документация ИОС» жив',
              page.evaluate("""(() => {
                navigateTo('docs-ios');
                const p = document.getElementById('page-docs-ios');
                return !!(p && p.classList.contains('active'));})()"""))
        check('F4: 0 JS-ошибок', len(jsF) == 0, jsF[:3])
        ctx.close()

        browser.close()

    print('-' * 60)
    print('ИТОГ Task 463-464 SMOKE (kip8): %d passed / %d failed' % (PASS, FAIL))
    return 0 if FAIL == 0 else 1


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


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
