#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 497 SMOKE kip8: проверка ПЕРЕНОСА (kipia-v520→v521) в БОЕВОЙ
# kip8. СТАТИКА ×8 (sw.js: v521 + комментарий 497 + v520 нет;
# index.html: блок Task 497 в init — после _restoreCache(silent) ДО
# _loadFallback, условие FlowFav.count()>0 && _METERS.length>0;
# renderList: hasFav497/favEmpty497, «Нет избранных…» через
# favEmpty497, ветки loading/error живы, HTML заглушек прежний) +
# БРАУЗЕР (мобайл 375 тёмная, flowmeter.list с ОТЛОЖЕННЫМ ответом:
# (1) FlowFav {1,3} + кэш → ДО ответа 2 карточки из кэша (111,11),
# заглушек нет, счётчик 2; ПОСЛЕ — серверные 999,99; (2) без кэша →
# «Загрузка данных…», не «Нет избранных»; (3) без избранного →
# вкладка «Все», заглушка как прежде) + 0 JS-ошибок.
# Порт 9007; ключи БЕЗ префикса (kip8); скриншоты в
# download/kip8-task497-smoke/.
import json
import os
import time
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 9007
K8 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(K8), 'download', 'kip8-task497-smoke')
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
          (('  [' + str(extra)[:200] + ']') if (extra and not ok) else ''))


def shot(page, name):
    try:
        page.screenshot(path=os.path.join(SHOT_DIR, name), full_page=False)
    except Exception as e:
        print('  (скриншот %s не сохранён: %s)' % (name, e))


def mk(id_, hoz, curr, prev):
    return {'id': id_, 'hoz': hoz,
            'param': 'Расход пара в корпус %d' % id_,
            'datePrev': '10/1/2026', 'dateCurr': '10/5/2026',
            'prev': prev, 'curr': curr, 'unit': 'т',
            'temp': None, 'gcal': 60.46, 'period': 'Ежедневно',
            'modRole': 'Админ', 'modName': 'smoke', 'modTimestamp': None}


CACHE_METERS = [mk(1, 'Хозрасчёт №1', 111.11, 110.11),
                mk(2, 'Хозрасчёт №2', 222.22, 220.22),
                mk(3, 'Хозрасчёт №3', 333.33, 330.33),
                mk(4, 'Хозрасчёт №4', 444.44, 440.44)]
SERVER_METERS = [mk(1, 'Хозрасчёт №1', 999.99, 900.11),
                 mk(2, 'Хозрасчёт №2', 888.88, 880.22),
                 mk(3, 'Хозрасчёт №3', 777.77, 770.33),
                 mk(4, 'Хозрасчёт №4', 666.66, 660.44)]
FAV_JSON = json.dumps({'1': '2026-10-01T00:00:00.000Z',
                       '3': '2026-10-02T00:00:00.000Z'})
FAV_ORDER = json.dumps(['1', '3'])


def mock_response(action):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local',
                                     'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'flowmeter.view': True,
                                'workschedule.view': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    return {'ok': True, 'data': {'ok': True}}


def setup_routes(ctx, pending):
    def handle(route, request):
        url = request.url
        action = ''
        if 'action=' in url:
            action = unquote(url.split('action=')[1].split('&')[0])
        if action == 'flowmeter.list':
            pending.append(route)
            return
        route.fulfill(status=200,
                      content_type='application/json; charset=utf-8',
                      body=json.dumps(mock_response(action),
                                      ensure_ascii=False).encode('utf-8'))

    def block_external(route):
        route.fulfill(status=404, content_type='text/plain',
                      body='not found (smoke t497 k8)')

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)


def release(pending, meters):
    body = json.dumps({'ok': True, 'data': {'meters': meters}},
                      ensure_ascii=False).encode('utf-8')
    for r in pending:
        try:
            r.fulfill(status=200, content_type='application/json; charset=utf-8',
                      body=body)
        except Exception as e:
            print('  (release: %s)' % e)
    pending.clear()


def flow_state(page):
    return page.evaluate(r"""(() => {
        const btns = document.querySelectorAll('.flow-tab[data-flow-tab]');
        let allOn = true, favOn = true, n = 0;
        btns.forEach(b => {
            n++;
            const on = b.classList.contains('active');
            if (b.getAttribute('data-flow-tab') === 'fav') { if (!on) favOn = false; }
            else { if (!on) allOn = false; }
        });
        const list = document.getElementById('flowList');
        const txt = list ? list.textContent : '';
        return {
            n, allOn, favOn,
            cards: document.querySelectorAll('#flowList .flow-card').length,
            favCount: (document.getElementById('flowFavCount') || {}).textContent,
            noFavStub: txt.indexOf('Нет избранных расходомеров') !== -1,
            loading: txt.indexOf('Загрузка данных') !== -1,
            hasCacheVals: txt.indexOf('111,11') !== -1 || txt.indexOf('333,33') !== -1,
            hasServerVals: txt.indexOf('999,99') !== -1 || txt.indexOf('777,77') !== -1
        };
    })()""")


def main():
    # ============ СТАТИКА ============
    sw = open(os.path.join(K8, 'sw.js'), encoding='utf-8').read()
    idx = open(os.path.join(K8, 'index.html'), encoding='utf-8').read()
    check('sw.js: CACHE_VERSION = kipia-v521 (один инкремент)',
          "const CACHE_VERSION = 'kipia-v521';" in sw and
          'kipia-v520' not in sw)
    i = sw.find("const CACHE_VERSION = 'kipia-v521';")
    ctx = sw[max(0, i - 900):i]
    check('sw.js: комментарий Task 497 (расходомеры/избранное)',
          'Task 497' in ctx and 'Расходомеры хозрасчётные' in ctx and
          'Нет избранных' in ctx)

    # init: блок Task 497 — после _restoreCache(silent), до _loadFallback
    i_restore = idx.find('this._restoreCache(silent);')
    i_block = idx.find('Task 497 (баг-репорт): при наличии избранного')
    i_fallback = idx.find('this._loadFallback(silent);')
    check('index.html: блок Task 497 в init — после _restoreCache, '
          'до _loadFallback',
          -1 < i_restore < i_block < i_fallback)
    init_zone = idx[i_block:i_fallback]
    check('init: условие мгновенного рендера (fav + FlowFav.count>0 + '
          '_METERS + silent)',
          "this._activeTab === 'fav'" in init_zone and
          'FlowFav.count() > 0' in init_zone and
          'this._METERS.length > 0' in init_zone and
          'if (silent &&' in init_zone and
          'this.renderList();' in init_zone)

    # renderList: заглушки
    i_stub = idx.find('var favEmpty497 = isFavTab &&')
    check('renderList: hasFav497 / favEmpty497 объявлены',
          idx.find('var hasFav497 =') != -1 and i_stub != -1)
    stub_zone = idx[i_stub:idx.find('flow-empty-fav-hint') + 40]
    check('renderList: заглушка «Нет избранных…» — через favEmpty497 '
          '(голого isFavTab в регионе НЕТ)',
          'if (favEmpty497) {' in idx and 'if (isFavTab) {' not in stub_zone)
    check('renderList: ветки loading/error живы (else-if)',
          "} else if (this._loadState === 'loading') {" in idx and
          "} else if (this._loadState === 'error') {" in idx)
    check('renderList: HTML заглушек прежний',
          'Нет избранных расходомеров' in idx and
          'flow-loading-dots' in idx and 'Нет связи с сервером' in idx and
          'Нет данных' in idx)

    # ============ БРАУЗЕР ============
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # --- 1. ГЛАВНЫЙ: кэш + избранное (отложенный ответ сервера) ---
        pending1 = []
        ctx1 = browser.new_context(viewport={'width': 375, 'height': 720},
                                   is_mobile=True, has_touch=True)
        page = ctx1.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        setup_routes(ctx1, pending1)
        seed = ("localStorage.setItem('kip8_session_token','smoke-t497-a');" +
                "localStorage.setItem('app-theme','dark');" +
                "localStorage.setItem('kip8_flow_fav_v1'," +
                "'" + FAV_JSON + "');" +
                "localStorage.setItem('kip8_flow_fav_order_v1'," +
                "'" + FAV_ORDER + "');" +
                "localStorage.setItem('kip8_flow_cache_v1'," +
                "'" + json.dumps({'meters': CACHE_METERS,
                                  'ts': int(time.time() * 1000)},
                                 ensure_ascii=False) + "');")
        ctx1.add_init_script(seed)
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('flowmeter-data')")
        page.wait_for_timeout(1000)

        st = flow_state(page)
        check('МОБАЙЛ: вкладка «Избранные» активна (Task 491)',
              st['favOn'] and not st['allOn'], st)
        check('МОБАЙЛ: ДО ответа сервера — 2 карточки ИЗ КЭША',
              st['cards'] == 2, st)
        check('МОБАЙЛ: ДО ответа — НЕТ «Нет избранных» и «Загрузка»',
              not st['noFavStub'] and not st['loading'], st)
        check('МОБАЙЛ: счётчик #flowFavCount = 2, показания кэша 111,11',
              (st['favCount'] or '').strip() == '2' and
              st['hasCacheVals'] and not st['hasServerVals'], st)
        shot(page, 'a-fav-instant-cache.png')
        release(pending1, SERVER_METERS)
        page.wait_for_timeout(1800)
        st2 = flow_state(page)
        check('МОБАЙЛ: ПОСЛЕ ответа — 2 карточки, серверные 999,99',
              st2['cards'] == 2 and st2['hasServerVals'] and
              not st2['hasCacheVals'] and not st2['loading'], st2)
        shot(page, 'b-fav-server-refreshed.png')
        check('МОБАЙЛ (гл. сценарий): 0 JS-ошибок', len(js_errors) == 0,
              js_errors[:3])
        ctx1.close()

        # --- 2. Без кэша: «Загрузка…», не заглушка ---
        pending2 = []
        ctx2 = browser.new_context(viewport={'width': 375, 'height': 720},
                                   is_mobile=True, has_touch=True)
        page2 = ctx2.new_page()
        js_errors2 = []
        page2.on('pageerror', lambda e: js_errors2.append(str(e)))
        page2.on('dialog', lambda d: d.accept())
        setup_routes(ctx2, pending2)
        ctx2.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t497-b');" +
            "localStorage.setItem('app-theme','dark');" +
            "localStorage.setItem('kip8_flow_fav_v1'," +
            "'" + FAV_JSON + "');" +
            "localStorage.setItem('kip8_flow_fav_order_v1'," +
            "'" + FAV_ORDER + "');")
        page2.goto('http://localhost:%d/index.html' % PORT)
        page2.wait_for_timeout(2500)
        page2.evaluate("navigateTo('flowmeter-data')")
        page2.wait_for_timeout(1000)
        stn = flow_state(page2)
        check('БЕЗ КЭША: ДО ответа — «Загрузка данных…», НЕ «Нет '
              'избранных»', stn['loading'] and not stn['noFavStub'], stn)
        shot(page2, 'c-no-cache-loading.png')
        release(pending2, SERVER_METERS)
        page2.wait_for_timeout(1800)
        stn2 = flow_state(page2)
        check('БЕЗ КЭША: ПОСЛЕ ответа — 2 карточки', stn2['cards'] == 2, stn2)
        check('БЕЗ КЭША: 0 JS-ошибок', len(js_errors2) == 0, js_errors2[:3])
        ctx2.close()

        # --- 3. Без избранного: заглушка как прежде ---
        pending3 = []
        ctx3 = browser.new_context(viewport={'width': 375, 'height': 720},
                                   is_mobile=True, has_touch=True)
        page3 = ctx3.new_page()
        js_errors3 = []
        page3.on('pageerror', lambda e: js_errors3.append(str(e)))
        page3.on('dialog', lambda d: d.accept())
        setup_routes(ctx3, pending3)
        ctx3.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t497-c');" +
            "localStorage.setItem('app-theme','dark');")
        page3.goto('http://localhost:%d/index.html' % PORT)
        page3.wait_for_timeout(2500)
        page3.evaluate("navigateTo('flowmeter-data')")
        page3.wait_for_timeout(1000)
        stf = flow_state(page3)
        check('БЕЗ ИЗБРАННОГО: вкладка «Все» (Task 491)',
              stf['allOn'] and not stf['favOn'], stf)
        release(pending3, SERVER_METERS)
        page3.wait_for_timeout(1800)
        stf2 = flow_state(page3)
        check('БЕЗ ИЗБРАННОГО: ПОСЛЕ ответа — 4 карточки',
              stf2['cards'] == 4, stf2)
        page3.click("#flowBottomBar .flow-tab[data-flow-tab='fav']",
                    timeout=4000)
        page3.wait_for_timeout(600)
        stf3 = flow_state(page3)
        check('БЕЗ ИЗБРАННОГО: «Избранные» — заглушка как прежде',
              stf3['noFavStub'] and stf3['cards'] == 0, stf3)
        shot(page3, 'd-no-fav-empty-stub.png')
        check('БЕЗ ИЗБРАННОГО: 0 JS-ошибок', len(js_errors3) == 0,
              js_errors3[:3])
        ctx3.close()

        browser.close()

    print('')
    print('ИТОГ SMOKE kip8 Task 497: %d passed, %d failed' % (PASS, FAIL))
    if FAIL:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
