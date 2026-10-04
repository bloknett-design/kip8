#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 475-477 SMOKE (kip8, ПЕРЕНОС партии этапов 1-3 оптимизации):
# браузерная проверка перенесённого кода в БОЕВОМ репозитории
# (ключи БЕЗ префикса kip8test:, кэши kipia-v510 / kipia-data-v1,
# БД kip8-cache-v1 — как в маппинге переноса).
#
# Сценарии (порт 8990, мок Apps Script как в task475/477-browser-check
# из kip8test, адаптация под kip8):
#   A  онлайн-первая-загрузка: SW kipia-v510 контролирует, precache,
#      DATA-кэш kipia-data-v1, «Приборы» рендерятся онлайн;
#   B  ПОЛНЫЙ ОФЛАЙН: reload → мгновенно из кэша SW, «Приборы» без
#      сети из DATA-кэша, 0 JS-ошибок; скриншот;
#   C  МЕДЛЕННАЯ СЕТЬ (CDP 4 с + 50 Кбит/с): reload быстрее сети
#      (SWR не ждёт сеть); скриншот;
#   D  ОФЛАЙН-ВЕТКА ВХОДА (Task 475): токен без кэша роли + Apps
#      Script abort → ГОСТЕВОЙ режим + тост + автоповтор; оживание
#      (online) → повтор входа, роль Админ;
#   E  KipPreload (Task 477, Админ): после входа ВСЕ данные фоном
#      (счётчики мока: WS ×7, CJ ×2, FM ×1, PE ×1) + KipDB
#      kip8-cache-v1 с копиями ws/cj/fm/pe ДО открытия разделов;
#   F  ГОСТЬ: предзагрузка не запускается (0 серверных экшенов
#      данных после входа);
#   G  logout (Task 476): KipDB ЧИСТ + KipPreload остановлен.
import json
import os
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8990
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(REPO), 'download',
                        'kip8-task475-477-transfer')
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
    print(('  ✓ ' if ok else '  ✗ ') + name +
          (('  [' + str(extra) + ']') if (extra and not ok) else ''))


def serve():
    os.chdir(REPO)

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

    httpd = HTTPServer(('127.0.0.1', PORT), QuietHandler)
    httpd.serve_forever()


WS_CODES = [{'code': 'Д', 'name': 'День', 'color': '#FFE082'},
             {'code': '', 'name': 'Выходной', 'color': '#EEF0F2'}]
WS_EMP = [{'таб_номер': '001', 'ФИО': 'Иванов И. И.', 'тип': 'сменный'}]


def attach(page, ctx, theme='dark', tag='t475k8', with_token=True,
           save_data=False):
    js_errors = []
    page.on('pageerror', lambda e: js_errors.append(str(e)))
    page.on('dialog', lambda d: d.accept())

    state = {'apps_ok': True, 'actions': {}}

    def handle(route, request):
        url = request.url
        action = ''
        if 'action=' in url:
            action = unquote(url.split('action=')[1].split('&')[0])
        if not state['apps_ok']:
            return route.abort()
        state['actions'][action] = state['actions'].get(action, 0) + 1
        if action == 'getCurrentUser':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'userId': 1, 'email': 'user@test.local',
                        'role': 'Админ'}}, ensure_ascii=False))
        if action == 'getMyAccess':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'role': 'Админ', 'found': True,
                        'permissions': {'calc.view': True, 'library.view': True,
                            'kipios.view': True, 'secret.view': True, 'whatsnew.view': True,
                            'charts.view': True, 'flowmeter.view': True,
                            'workschedule.view': True, 'workschedule.edit': True,
                            'plan.events': True}}}, ensure_ascii=False))
        if action == 'heartbeat':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'ok': True}}, ensure_ascii=False))
        if action == 'logout':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'ok': True}}, ensure_ascii=False))
        if action == 'workSchedule.getStatusCodes':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'codes': WS_CODES}}, ensure_ascii=False))
        if action == 'workSchedule.getPatterns':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'patterns': []}}, ensure_ascii=False))
        if action == 'workSchedule.listEmployees':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'employees': WS_EMP}}, ensure_ascii=False))
        if action == 'workSchedule.listEntries':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'entries': [
                    {'дата': '2026-10-01', 'таб_номер': '001', 'статус': 'Д'}]}},
                    ensure_ascii=False))
        if action == 'workSchedule.listTrainings':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'trainings': [], 'instrList': [],
                    'instrAll': [], 'eventsAll': []}}, ensure_ascii=False))
        if action == 'workSchedule.listVacations':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'vacations': []}}, ensure_ascii=False))
        if action == 'workSchedule.listPpe':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'ppe': []}}, ensure_ascii=False))
        if action == 'cableJournal.list':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'items': [], 'cols': []}},
                    ensure_ascii=False))
        if action == 'cableJournal.getColumns':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'cols': []}}, ensure_ascii=False))
        if action == 'flowmeter.list':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'items': []}}, ensure_ascii=False))
        if action == 'planEvents.years':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'years': [2026]}}, ensure_ascii=False))
        if action == 'planEvents.list':
            return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                body=json.dumps({'ok': True, 'data': {'marks': []}}, ensure_ascii=False))
        return route.fulfill(status=200, content_type='application/json; charset=utf-8',
                             body=json.dumps({'ok': True, 'data': {'ok': True}},
                                             ensure_ascii=False))

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)

    def block_external(route):
        route.fulfill(status=404, content_type='text/plain',
                      body='not found (t475k8-%s)' % tag)

    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)
    init = "try{localStorage.clear()}catch(e){};"
    if save_data:
        init += ("try{Object.defineProperty(navigator.connection,'saveData',"
                 "{get:()=>true});}catch(e){};")
    init += "localStorage.setItem('app-theme','%s');" % theme
    if with_token:
        init += "localStorage.setItem('kip8_session_token','bc-%s');" % tag
    ctx.add_init_script(init)
    return js_errors, state


def goto_app(page):
    t0 = time.time()
    page.goto('http://localhost:%d/index.html' % PORT,
              wait_until='domcontentloaded')
    return time.time() - t0


IDB_KEYS_JS = """async () => {
    return await new Promise(res => {
        try {
            const rq = indexedDB.open('kip8-cache-v1');
            rq.onsuccess = () => {
                const db = rq.result;
                try {
                    const tx = db.transaction('kv', 'readonly');
                    const g = tx.objectStore('kv').getAllKeys();
                    g.onsuccess = () => res(g.result || []);
                    g.onerror = () => res([]);
                } catch (e) { res(['ERR:' + e.message]); }
            };
            rq.onerror = () => res(['OPEN_ERR']);
        } catch (e) { res(['TRY_ERR:' + e.message]); }
    });
}"""


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ============ A. Онлайн-первая-загрузка ============
        print('A. Онлайн: первая загрузка + SW kipia-v510')
        ctxA = browser.new_context(viewport={'width': 1280, 'height': 900})
        pageA = ctxA.new_page()
        errsA, stA = attach(pageA, ctxA)
        tA = goto_app(pageA)
        pageA.wait_for_timeout(3000)
        check('A: приложение загружено (%.2f с)' % tA, tA < 8)
        sw = pageA.evaluate("""async () => {
            const reg = await navigator.serviceWorker.ready;
            const keys = await caches.keys();
            const c = await caches.open('kipia-v510');
            const k = await c.keys();
            return {controlled: !!navigator.serviceWorker.controller,
                    caches: keys, entries: k.length};
        }""")
        check('A: SW контролирует страницу', sw['controlled'])
        check('A: кэш kipia-v510 создан', 'kipia-v510' in sw['caches'], sw['caches'])
        check('A: precache наполнен (>= 20)', sw['entries'] >= 20, sw['entries'])
        check('A: DATA-кэш kipia-data-v1 создан', 'kipia-data-v1' in sw['caches'])
        pageA.evaluate("navigateTo('kip-ios')")
        pageA.wait_for_timeout(1000)
        pageA.evaluate("navigateTo('devices')")
        pageA.wait_for_timeout(2500)
        nA = pageA.evaluate(
            "document.querySelectorAll('.dev-card, .device-card, #devList > *').length")
        check('A: раздел «Приборы» рендерится онлайн', (nA or 0) > 0, nA)
        dataA = pageA.evaluate("""async () => {
            const c = await caches.open('kipia-data-v1');
            const r = await c.match('/data/devices.json');
            return r ? (await r.text()).length : 0;
        }""")
        check('A: devices.json в персистентном DATA-кэше', dataA > 100000, dataA)

        # ============ B. Полный офлайн ============
        print('B. ПОЛНЫЙ ОФЛАЙН: reload + «Приборы»')
        ctxA.set_offline(True)
        tB = goto_app(pageA)
        check('B: офлайн reload мгновенно (< 2.5 с): %.2f с' % tB, tB < 2.5)
        vis = pageA.evaluate("""(() => {
            const d = document.getElementById('page-dashboard');
            const ls = document.getElementById('loginScreen');
            return {dash: !!(d && d.classList.contains('active')),
                    login: !!(ls && ls.classList.contains('active'))};
        })()""")
        check('B: дашборд открыт, экрана входа нет',
              vis['dash'] and not vis['login'], vis)
        pageA.evaluate("navigateTo('kip-ios')")
        pageA.wait_for_timeout(600)
        pageA.evaluate("navigateTo('devices')")
        pageA.wait_for_timeout(2000)
        nB = pageA.evaluate(
            "document.querySelectorAll('.dev-card, .device-card, #devList > *').length")
        check('B: «Приборы» без сети (из кэша устройства)', (nB or 0) > 0, nB)
        check('B: 0 JS-ошибок', len(errsA) == 0, errsA[:3])
        pageA.screenshot(path=os.path.join(SHOT_DIR, '01-offline-devices.png'))
        ctxA.set_offline(False)

        # ============ C. Медленная сеть ============
        print('C. МЕДЛЕННАЯ СЕТЬ (CDP: 4 с, 50 Кбит/с)')
        cdp = ctxA.new_cdp_session(pageA)
        cdp.send('Network.enable')
        cdp.send('Network.emulateNetworkConditions', {
            'offline': False, 'latency': 4000,
            'downloadThroughput': 50 * 1024 / 8, 'uploadThroughput': 50 * 1024 / 8})
        tC = goto_app(pageA)
        check('C: reload БЫСТРЕЕ сети (< 2.5 с при сети 4 с): %.2f с' % tC, tC < 2.5)
        pageA.wait_for_timeout(1500)
        pageA.screenshot(path=os.path.join(SHOT_DIR, '02-slownet-dashboard.png'))
        cdp.send('Network.emulateNetworkConditions', {
            'offline': False, 'latency': 0, 'downloadThroughput': -1,
            'uploadThroughput': -1})

        # ============ D. Офлайн-ветка входа ============
        print('D. ОФЛАЙН-ВЕТКА ВХОДА: токен без кэша роли + AS недоступен')
        ctxD = browser.new_context(viewport={'width': 1280, 'height': 900})
        pageD = ctxD.new_page()
        errsD, stD = attach(pageD, ctxD)
        stD['apps_ok'] = False
        goto_app(pageD)
        pageD.wait_for_timeout(3500)
        visD = pageD.evaluate("""(() => {
            const d = document.getElementById('page-dashboard');
            const ls = document.getElementById('loginScreen');
            return {dash: !!(d && d.classList.contains('active')),
                    login: !!(ls && ls.classList.contains('active'))};
        })()""")
        check('D: ГОСТЕВОЙ режим (не экран входа)', visD['dash'] and not visD['login'],
              visD)
        retryD = pageD.evaluate(
            "(typeof KipAuth !== 'undefined') && !!KipAuth._offlineRetryTimer")
        check('D: автоповтор входа запущен (_offlineRetryTimer)', retryD)
        toastD = pageD.evaluate("""(() => {
            const els = document.querySelectorAll('.toast, [class*=toast]');
            for (const el of els) if (el.textContent.indexOf('гостевой режим') !== -1) return true;
            return document.body.textContent.indexOf('гостевой режим') !== -1;
        })()""")
        check('D: тост «гостевой режим» показан', toastD)
        pageD.screenshot(path=os.path.join(SHOT_DIR, '03-offline-guest.png'))
        # Оживание: AS доступен + событие online → повтор входа
        stD['apps_ok'] = True
        pageD.evaluate("window.dispatchEvent(new Event('online'))")
        pageD.wait_for_timeout(2500)
        stD2 = pageD.evaluate("""(() => {
            return {role: (typeof KipAuth !== 'undefined' && KipAuth._cachedRole) || null,
                    retryStopped: (typeof KipAuth !== 'undefined' && !KipAuth._offlineRetryTimer)};
        })()""")
        check('D: после оживания — вход выполнен (роль Админ)',
              stD2['role'] == 'Админ', stD2)
        check('D: автоповтор остановлен', stD2['retryStopped'])
        check('D: 0 JS-ошибок', len(errsD) == 0, errsD[:3])

        # ============ E. KipPreload (Админ) ============
        print('E. KipPreload: фоновая предзагрузка по правам роли (Админ)')
        tE0 = time.time()
        while time.time() - tE0 < 60:
            stE = pageD.evaluate(
                "(typeof KipPreload !== 'undefined') ? KipPreload._state() : null")
            if stE and stE.get('done', 0) >= 13 and not stE.get('active'):
                break
            pageD.wait_for_timeout(2000)
        stE = pageD.evaluate(
            "(typeof KipPreload !== 'undefined') ? KipPreload._state() : null")
        check('E: очередь предзагрузки выполнена (done>=13, fail=0)',
              stE and stE['done'] >= 13 and stE['fail'] == 0, stE)
        wsN = sum(v for k, v in stD['actions'].items() if k.startswith('workSchedule.'))
        check('E: WS-экшены предзагружены (>= 7)', wsN >= 7, stD['actions'])
        check('E: CJ-экшены предзагружены (>= 2)',
              stD['actions'].get('cableJournal.list', 0) +
              stD['actions'].get('cableJournal.getColumns', 0) >= 2)
        check('E: FM предзагружен', stD['actions'].get('flowmeter.list', 0) >= 1)
        check('E: PE предзагружен', stD['actions'].get('planEvents.list', 0) >= 1)
        idbE = pageD.evaluate(IDB_KEYS_JS)
        for k in ('kip8_ws_cache_v1', 'kip8_cj_cache_v1',
                  'kip8_flow_cache_v1', 'kip8_pe_marks_v1'):
            check('E: KipDB содержит копию %s' % k, k in idbE, idbE)
        pageD.screenshot(path=os.path.join(SHOT_DIR, '04-preload-idb.png'))

        # ============ F. Гость: предзагрузки нет ============
        print('F. ГОСТЬ (без токена): предзагрузка не запускается')
        ctxF = browser.new_context(viewport={'width': 1280, 'height': 900})
        pageF = ctxF.new_page()
        errsF, stF = attach(pageF, ctxF, with_token=False)
        goto_app(pageF)
        pageF.wait_for_timeout(8000)
        stF_state = pageF.evaluate(
            "(typeof KipPreload !== 'undefined') ? KipPreload._state() : null")
        dataF = sum(v for k, v in stF['actions'].items()
                    if k.startswith('workSchedule.') or k in
                    ('cableJournal.list', 'flowmeter.list', 'planEvents.years'))
        check('F: предзагрузка не стартовала (started=false)',
              stF_state and not stF_state['started'], stF_state)
        check('F: 0 серверных экшенов данных', dataF == 0, stF['actions'])

        # ============ G. logout: чистка KipDB (Task 476) ============
        print('G. LOGOUT: чистка локальных копий')
        pageD.evaluate(
            "(typeof KipAuth !== 'undefined') && KipAuth.logout && KipAuth.logout()")
        pageD.wait_for_timeout(2500)
        idbG = pageD.evaluate(IDB_KEYS_JS)
        check('G: KipDB чист после logout', idbG == [], idbG)
        stG = pageD.evaluate(
            "(typeof KipPreload !== 'undefined') ? KipPreload._state() : null")
        check('G: KipPreload остановлен (started=false)',
              stG and not stG['started'], stG)
        lsG = pageD.evaluate("""(() => {
            try { return [localStorage.getItem('kip8_ws_cache_v1'),
                          localStorage.getItem('kip8_cj_cache_v1')]; } catch (e) { return ['ERR']; }
        })()""")
        check('G: LS-копии серверных данных удалены', lsG == [None, None], lsG)
        check('G: 0 JS-ошибок (D+E+G)', len(errsD) == 0, errsD[:3])

        browser.close()
    print()
    print('ИТОГ: %d passed, %d failed' % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == '__main__':
    t = threading.Thread(target=serve, daemon=True)
    t.start()
    time.sleep(0.5)
    raise SystemExit(main())
