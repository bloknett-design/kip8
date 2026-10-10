#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 496 SMOKE kip8: проверка ПЕРЕНОСА (kipia-v519→v520) в БОЕВОЙ
# kip8. СТАТИКА ×6 (sw.js: v520 + комментарий 496 + v519 нет;
# index.html: tempQueryEnterBlur + stopPropagation, ППР done×2 /
# next-тегов нет, границы — блок таблицы next×2 жив, глобальный
# Enter-переход жив) + БРАУЗЕР (мобайл 375 тёмная: датчик 50М —
# enterkeyhint done, Enter закрывает (body), НЕ перескакивает в
# tempQueryVal; поле значения — тоже; живой расчёт 55 → R;
# границы: блок таблицы Enter перескакивает min→max как прежде;
# ТП tc_K; светлая; десктоп 1280) + 0 JS-ошибок.
# Порт 9007; скриншоты в download/kip8-task496-smoke/.
import json
import os
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 9007
K8 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(K8), 'download', 'kip8-task496-smoke')
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


def setup_routes(ctx):
    def handle(route, request):
        url = request.url
        action = ''
        if 'action=' in url:
            action = unquote(url.split('action=')[1].split('&')[0])
        route.fulfill(status=200,
                      content_type='application/json; charset=utf-8',
                      body=json.dumps(mock_response(action),
                                      ensure_ascii=False).encode('utf-8'))

    def block_external(route):
        route.fulfill(status=404, content_type='text/plain',
                      body='not found (smoke t496)')

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)


ATTRS_JS = r"""(() => {
    const t = document.getElementById('tempQueryTemp');
    const v = document.getElementById('tempQueryVal');
    if (!t || !v) return {t: !!t, v: !!v};
    return {
        t: true, v: true,
        tHint: t.getAttribute('enterkeyhint'),
        vHint: v.getAttribute('enterkeyhint'),
        tKd: t.getAttribute('onkeydown'),
        vKd: v.getAttribute('onkeydown'),
        fn: typeof window.tempQueryEnterBlur,
        tVal: t.value, vVal: v.value,
        label: (document.getElementById('tempQueryValLabel') || {}).textContent
    };
})()"""


def open_sensor(page, key):
    page.evaluate("openTempSensor('%s')" % key)
    page.wait_for_timeout(500)


def main():
    # ============ СТАТИКА ============
    sw = open(os.path.join(K8, 'sw.js'), encoding='utf-8').read()
    idx = open(os.path.join(K8, 'index.html'), encoding='utf-8').read()
    check('sw.js: CACHE_VERSION = kipia-v520 (один инкремент)',
          "const CACHE_VERSION = 'kipia-v520';" in sw and
          'kipia-v519' not in sw)
    i = sw.find("const CACHE_VERSION = 'kipia-v520';")
    ctx = sw[max(0, i - 900):i]
    check('sw.js: комментарий Task 496 (ППР/клавиатура)',
          'Task 496' in ctx and 'произвольного расчёта' in ctx and
          'tempQueryEnterBlur' in ctx)

    ppr = idx[idx.find('<!-- Task 373:'):idx.find('id="tempTableFormPanel"')]
    check('index.html: ППР — done×2, next-тегов НЕТ',
          ppr.count('enterkeyhint="done">') == 2 and
          'enterkeyhint="next">' not in ppr)
    check('index.html: ППР — onkeydown tempQueryEnterBlur ×2',
          ppr.count('onkeydown="tempQueryEnterBlur(event,this)"') == 2)
    fn = idx[idx.find('function tempQueryEnterBlur'):
             idx.find('function tempQueryFromTemp')]
    check('index.html: хелпер stopPropagation + blur + preventDefault',
          'stopPropagation' in fn and 'blur' in fn and
          'preventDefault' in fn)
    tbl = idx[idx.find('id="tempTableFormPanel"'):
              idx.find('onclick="calcTempSensor()"')]
    check('index.html: ГРАНИЦЫ — блок таблицы next×2 жив',
          tbl.count('enterkeyhint="next">') == 2 and
          'tempQueryEnterBlur' not in tbl)
    glob = idx[idx.find('// Обработчик Enter/Next на клавиатуре'):
               idx.find('// Обработчик Enter/Next на клавиатуре') + 1400]
    check('index.html: ГРАНИЦЫ — глобальный Enter-переход жив',
          'fields[idx + 1].focus();' in glob and 'tempQuery' not in glob)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ============ 1. МОБАЙЛ 375, тёмная, 50М (ТС) ============
        ctxm = browser.new_context(viewport={'width': 375, 'height': 720},
                                   is_mobile=True, has_touch=True)
        page = ctxm.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        setup_routes(ctxm)
        ctxm.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t496-a');" +
            "localStorage.setItem('app-theme','dark');")
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'cu50_1428')
        st = page.evaluate(ATTRS_JS)
        check('A: оба поля ППР — enterkeyhint="done"',
              st['tHint'] == 'done' and st['vHint'] == 'done')
        check('B: onkeydown tempQueryEnterBlur на обоих',
              st['tKd'] == 'tempQueryEnterBlur(event,this)' and
              st['vKd'] == 'tempQueryEnterBlur(event,this)')
        check('C: tempQueryEnterBlur — глобальная', st['fn'] == 'function')

        page.click('#tempQueryTemp')
        page.wait_for_timeout(300)
        page.keyboard.press('Enter')
        page.wait_for_timeout(400)
        ae = page.evaluate(
            "document.activeElement && (document.activeElement.id || 'BODY')")
        check('D: Enter в поле температуры — клавиатура ЗАКРЫЛАСЬ (body), '
              'перескока в tempQueryVal НЕТ', ae == 'BODY', ae)
        shot(page, 'a-mobile-dark-after-enter.png')

        page.fill('#tempQueryTemp', '55')
        page.wait_for_timeout(400)
        st2 = page.evaluate(ATTRS_JS)
        check('E: живой расчёт жив (55 → R)',
              st2['vVal'] not in ('', None) and
              float(str(st2['vVal']).replace(',', '.')) > 0, st2['vVal'])
        shot(page, 'b-mobile-dark-live-calc.png')

        page.click('#tempQueryVal')
        page.keyboard.press('Enter')
        page.wait_for_timeout(400)
        ae2 = page.evaluate(
            "document.activeElement && (document.activeElement.id || 'BODY')")
        check('F: Enter в поле значения — фокус снят (body)', ae2 == 'BODY', ae2)

        # границы: блок таблицы перескакивает как прежде
        page.click('#temp_sensor_min')
        page.wait_for_timeout(300)
        page.keyboard.press('Enter')
        page.wait_for_timeout(400)
        ae3 = page.evaluate(
            "document.activeElement && (document.activeElement.id || 'BODY')")
        check('G: границы — блок таблицы: Enter min→max как прежде',
              ae3 == 'temp_sensor_max', ae3)
        ctxm.close()

        # ============ 2. ТП ТХА (K) ============
        ctxm = browser.new_context(viewport={'width': 375, 'height': 720},
                                    is_mobile=True, has_touch=True)
        page = ctxm.new_page()
        js_errors2 = []
        page.on('pageerror', lambda e: js_errors2.append(str(e)))
        setup_routes(ctxm)
        ctxm.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t496-b');" +
            "localStorage.setItem('app-theme','dark');")
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'tc_K')
        st3 = page.evaluate(ATTRS_JS)
        check('H: ТХА (K) — done×2 + onkeydown×2',
              st3['tHint'] == 'done' and st3['vKd'] is not None and
              'tempQueryEnterBlur' in str(st3['vKd']))
        page.click('#tempQueryTemp')
        page.keyboard.press('Enter')
        page.wait_for_timeout(400)
        ae4 = page.evaluate(
            "document.activeElement && (document.activeElement.id || 'BODY')")
        check('I: ТХА (K) — Enter закрывает (не перескакивает)',
              ae4 == 'BODY', ae4)
        page.fill('#tempQueryTemp', '300')
        page.wait_for_timeout(400)
        st4 = page.evaluate(ATTRS_JS)
        check('J: ТХА (K) — живой расчёт (300 → мВ)',
              st4['vVal'] not in ('', None) and
              float(str(st4['vVal']).replace(',', '.')) > 0, st4['vVal'])
        shot(page, 'c-mobile-dark-tc.png')
        ctxm.close()

        # ============ 3. СВЕТЛАЯ ============
        ctxm = browser.new_context(viewport={'width': 375, 'height': 720},
                                    is_mobile=True, has_touch=True)
        page = ctxm.new_page()
        js_errors3 = []
        page.on('pageerror', lambda e: js_errors3.append(str(e)))
        setup_routes(ctxm)
        ctxm.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t496-c');" +
            "localStorage.setItem('app-theme','light');")
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'cu50_1428')
        st5 = page.evaluate(ATTRS_JS)
        check('K: светлая — атрибуты живы',
              st5['tHint'] == 'done' and 'tempQueryEnterBlur' in str(st5['vKd']))
        page.click('#tempQueryVal')
        page.keyboard.press('Enter')
        page.wait_for_timeout(400)
        ae5 = page.evaluate(
            "document.activeElement && (document.activeElement.id || 'BODY')")
        check('L: светлая — Enter закрывает клавиатуру', ae5 == 'BODY', ae5)
        shot(page, 'd-mobile-light.png')
        ctxm.close()

        # ============ 4. ДЕСКТОП 1280 ============
        ctxm = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = ctxm.new_page()
        js_errors4 = []
        page.on('pageerror', lambda e: js_errors4.append(str(e)))
        setup_routes(ctxm)
        ctxm.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t496-d');" +
            "localStorage.setItem('app-theme','dark');")
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'cu50_1428')
        st6 = page.evaluate(ATTRS_JS)
        check('M: десктоп — атрибуты живы (done + onkeydown)',
              st6['tHint'] == 'done' and
              'tempQueryEnterBlur' in str(st6['tKd']))
        page.click('#tempQueryTemp')
        page.keyboard.press('Enter')
        page.wait_for_timeout(400)
        ae6 = page.evaluate(
            "document.activeElement && (document.activeElement.id || 'BODY')")
        check('N: десктоп — Enter снимает фокус', ae6 == 'BODY', ae6)
        shot(page, 'e-desktop.png')
        ctxm.close()

        browser.close()

    print('---')
    print('ИТОГ SMOKE Task 496 (kip8): %d passed, %d failed' % (PASS, FAIL))
    print('JS-ошибок: %d' % (len(js_errors) + len(js_errors2) +
                             len(js_errors3) + len(js_errors4)))
    for e in (js_errors + js_errors2 + js_errors3 + js_errors4)[:5]:
        print('  JS: ' + e[:200])
    raise SystemExit(0 if (FAIL == 0 and not js_errors and not js_errors2 and
                           not js_errors3 and not js_errors4) else 1)


main()
