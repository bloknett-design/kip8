#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 498 SMOKE kip8: проверка ПЕРЕНОСА (kipia-v521→v522) в БОЕВОЙ
# kip8. СТАТИКА ×8 (sw.js: v522 + комментарий 498 + v521 нет;
# index.html: коэффициенты pt1391 3.969e-3/-5.841e-7/-4.330e-12 +
# C-член; строка формулы 100П; заголовок только тип (t498);
# подсказки tempQueryTempRange/tempQueryValRange + fmtI498/fmtM498;
# HTML div.ts-calc-range ×2; CSS #tempSensorViewTitle 21px;
# хук крошек updateDesktopBreadcrumb(null, l498)) +
# БРАУЗЕР (мобайл 375 тёмная: 50М заголовок «50М (Cu50)
# α = 0,00428 °C⁻¹» + подсказки «−50…200 °C»/«39,3…92,8 Ом»;
# 100П «17,2444…395,16 Ом» (новая формула!) + живой расчёт
# −100→59,6393; ТХА (K) «ТХА (K)» + мВ; светлая 50П; десктоп 1280:
# 21px + крошки с α) + 0 JS-ошибок.
# Порт 9007; ключи БЕЗ префикса (kip8); скриншоты в
# download/kip8-task498-smoke/.
import os
from playwright.sync_api import sync_playwright

PORT = 9007
K8 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(K8), 'download', 'kip8-task498-smoke')
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
    return {'ok': True, 'data': {'ok': True}}


def setup_routes(ctx):
    import json
    from urllib.parse import unquote

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
                      body='not found (smoke t498)')

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)


TITLE_JS = r"""(() => {
    const t = document.getElementById('tempSensorViewTitle');
    const tr = document.getElementById('tempQueryTempRange');
    const vr = document.getElementById('tempQueryValRange');
    const cs = t ? getComputedStyle(t) : null;
    const csR = tr ? getComputedStyle(tr) : null;
    return {
        title: t ? t.textContent : null,
        fs: cs ? cs.fontSize : null,
        tr: tr ? tr.textContent : null,
        vr: vr ? vr.textContent : null,
        trVisible: tr ? (tr.offsetHeight > 0 && tr.offsetWidth > 0) : false,
        vrVisible: vr ? (vr.offsetHeight > 0 && vr.offsetWidth > 0) : false,
        trFs: csR ? csR.fontSize : null,
        trColor: csR ? csR.color : null
    };
})()"""


def open_sensor(page, key):
    page.evaluate("openTempSensor('%s')" % key)
    page.wait_for_timeout(600)


def main():
    # ============ СТАТИКА ============
    sw = open(os.path.join(K8, 'sw.js'), encoding='utf-8').read()
    idx = open(os.path.join(K8, 'index.html'), encoding='utf-8').read()
    check('S1: sw.js — kipia-v522', "const CACHE_VERSION = 'kipia-v522';" in sw)
    check('S2: sw.js — v521 НЕ выпущена', 'kipia-v521' not in sw)
    check('S3: sw.js — комментарий Task 498',
          'Task 498: «Датчики температуры»' in sw)
    check('S4: index — коэффициенты А.2 (3.969e-3/-5.841e-7/-4.330e-12)',
          'A=3.969e-3, B=-5.841e-7, C=-4.330e-12' in idx)
    check('S5: index — C-член в pt1391 ниже 0',
          idx.count('C*(t-100)*t*t*t') == 2)
    check('S6: index — заголовок t498 + подсказки + крошки l498',
          'title.textContent=t498' in idx and
          'tempQueryTempRange' in idx and 'tempQueryValRange' in idx and
          'updateDesktopBreadcrumb(null, l498)' in idx)
    check('S7: index — HTML div.ts-calc-range ×2',
          idx.count('class="ts-calc-range"') == 2)
    check('S8: index — CSS #tempSensorViewTitle 21px',
          '#tempSensorViewTitle { font-size: 21px; }' in idx)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ============ БРАУЗЕР: мобайл 375 тёмная ============
        ctx = browser.new_context(viewport={'width': 375, 'height': 720},
                                  is_mobile=True, has_touch=True)
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        setup_routes(ctx)
        ctx.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t498-a');" +
            "localStorage.setItem('app-theme','dark');")
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('temp-sensors')")
        page.wait_for_timeout(600)

        card_range = page.evaluate(
            "(() => { const c = document.querySelector('.ts-card-range');"
            " return c ? c.textContent : null; })()")
        check('B0: каталог — карточка «НСХ: −50…200 °C» (пределы живы)',
              card_range == 'НСХ: −50…200 °C', card_range)

        open_sensor(page, 'cu50_1428')
        st = page.evaluate(TITLE_JS)
        check('B1: 50М заголовок «50М (Cu50) α = 0,00428 °C⁻¹»',
              st['title'] == '50М (Cu50) α = 0,00428 °C⁻¹', st['title'])
        fs_px = float(str(st['fs']).replace('px', '')) if st['fs'] else 0
        check('B2: шрифт заголовка ≥ 15px (крупнее прежнего ~13-14)',
              fs_px >= 15, st['fs'])
        check('B3: подсказки «−50…200 °C» / «39,3…92,8 Ом»',
              st['tr'] == '−50…200 °C' and st['vr'] == '39,3…92,8 Ом',
              (st['tr'], st['vr']))
        check('B4: подсказки видимы, 11px',
              st['trVisible'] and st['vrVisible'] and st['trFs'] == '11px')
        shot(page, 'a-mobile-50m.png')

        open_sensor(page, 'pt100_1391')
        st2 = page.evaluate(TITLE_JS)
        check('B5: 100П «100П (Pt100) α = 0,00391 °C⁻¹»',
              st2['title'] == '100П (Pt100) α = 0,00391 °C⁻¹', st2['title'])
        check('B6: 100П подсказка «17,2444…395,16 Ом» (новая формула)',
              st2['vr'] == '17,2444…395,16 Ом', st2['vr'])
        page.fill('#tempQueryTemp', '-100')
        page.wait_for_timeout(400)
        v = page.evaluate("document.getElementById('tempQueryVal').value")
        check('B7: живой расчёт 100П: −100 → 59,6393 (А.2 ГОСТ)',
              v == '59,6393', v)
        shot(page, 'b-mobile-100p.png')

        open_sensor(page, 'tc_K')
        st3 = page.evaluate(TITLE_JS)
        check('B8: ТХА (K) — только имя',
              st3['title'] == 'ТХА (K)', st3['title'])
        check('B9: ТХА подсказки °C/мВ',
              st3['tr'] == '−270…1372 °C' and
              st3['vr'] == '−6,4577…54,8864 мВ', (st3['tr'], st3['vr']))
        shot(page, 'c-mobile-tc-k.png')
        ctx.close()

        # ============ светлая ============
        ctx = browser.new_context(viewport={'width': 375, 'height': 720},
                                  is_mobile=True, has_touch=True)
        page = ctx.new_page()
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        setup_routes(ctx)
        ctx.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t498-b');" +
            "localStorage.setItem('app-theme','light');")
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'pt50_1391')
        st4 = page.evaluate(TITLE_JS)
        check('B10: светлая 50П заголовок + подсказки читаемы',
              st4['title'] == '50П (Pt50) α = 0,00391 °C⁻¹' and
              st4['trVisible'] and st4['vrVisible'],
              (st4['title'], st4['tr']))
        shot(page, 'd-light-50p.png')
        ctx.close()

        # ============ десктоп 1280 ============
        ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = ctx.new_page()
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        setup_routes(ctx)
        ctx.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t498-c');" +
            "localStorage.setItem('app-theme','dark');")
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'cu100_1426')
        st5 = page.evaluate(TITLE_JS)
        check('B11: десктоп 21px', st5['fs'] == '21px', st5['fs'])
        check('B12: десктоп крошки …100М (Cu100) α = 0,00426 °C⁻¹',
              st5['title'] is not None and
              st5['title'].endswith('100М (Cu100) α = 0,00426 °C⁻¹'),
              st5['title'])
        check('B13: десктоп подсказки (78,7…185,2 Ом)',
              st5['vr'] == '78,7…185,2 Ом', st5['vr'])
        shot(page, 'e-desktop-1280.png')
        ctx.close()
        browser.close()

    print('—' * 60)
    print('ИТОГО SMOKE: %d OK, %d FAIL' % (PASS, FAIL))
    print('JS-ошибок: %d' % len(js_errors))
    for e in js_errors[:5]:
        print('  JS: ' + e[:200])
    raise SystemExit(1 if (FAIL or js_errors) else 0)


if __name__ == '__main__':
    main()
