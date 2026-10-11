#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 499 SMOKE kip8: проверка ПЕРЕНОСА (kipia-v522→v523) в БОЕВОЙ
# kip8. СТАТИКА ×8 (sw.js: v523 + комментарий 499 + v522 нет;
# index.html: формула 5.2.3 ГОСТ (4.28e-3/-6.2032e-7/8.5154e-10 +
# B*t*(t+6.7)); каталог rng499 (−180…200 / −50…200);
# плейсхолдеры полей tInp.placeholder=fmtI499 / vInp.placeholder=
# fmtM499; «Например:» в панели нет; ts-calc-range в index нет;
# бледный ::placeholder жив) + БРАУЗЕР (мобайл 375 тёмная: 50М
# плейсхолдеры «−180…200 °C»/«10,2642…92,8 Ом» + живой расчёт по
# ГОСТ −180→10,2642, −50→39,2275 + инверсия; 100П «17,2444…395,16 Ом»
# (инвариант 498) + живой расчёт −100→59,6393; ТХА (K) мВ; карточки
# каталога −180…200; светлая 50М; десктоп 1280: 21px + крошки) +
# 0 JS-ошибок.
# Порт 9007; ключи БЕЗ префикса (kip8); скриншоты в
# download/kip8-task499-smoke/.
import os
from playwright.sync_api import sync_playwright

PORT = 9007
K8 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(K8), 'download', 'kip8-task499-smoke')
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
                      body='not found (smoke t499)')

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)


FIELDS_JS = r"""(() => {
    const t = document.getElementById('tempQueryTemp');
    const v = document.getElementById('tempQueryVal');
    const title = document.getElementById('tempSensorViewTitle');
    const phT = t ? getComputedStyle(t, '::placeholder') : null;
    const phV = v ? getComputedStyle(v, '::placeholder') : null;
    return {
        title: title ? title.textContent : null,
        fs: title ? getComputedStyle(title).fontSize : null,
        phT: t ? t.placeholder : null,
        phV: v ? v.placeholder : null,
        phTColor: phT ? phT.color : null,
        phVColor: phV ? phV.color : null,
        divRanges: document.querySelectorAll('.ts-calc-range').length,
        valLabel: (document.getElementById('tempQueryValLabel') || {}).textContent
    };
})()"""


def open_sensor(page, key):
    page.evaluate("openTempSensor('%s')" % key)
    page.wait_for_timeout(600)


def main():
    # ============ СТАТИКА ============
    sw = open(os.path.join(K8, 'sw.js'), encoding='utf-8').read()
    idx = open(os.path.join(K8, 'index.html'), encoding='utf-8').read()
    panel = idx[idx.find('id="tempCustomCalcPanel"'):idx.find('id="temp_sensor_min"')]
    check('S1: sw.js — kipia-v523', "const CACHE_VERSION = 'kipia-v523';" in sw)
    check('S2: sw.js — v522 НЕ выпущена', 'kipia-v522' not in sw)
    check('S3: sw.js — комментарий Task 499',
          'Task 499: подсказки диапазонов НСХ' in sw)
    check('S4: index — формула 5.2.3 (4.28e-3 / -6.2032e-7 / 8.5154e-10)',
          'let A=4.28e-3, B=-6.2032e-7, C=8.5154e-10' in idx and
          'B*t*(t+6.7)' in idx)
    check('S5: index — каталог rng499 (−180…200 для α 0,00428)',
          'rng499=isCu?((Math.abs(sd.alpha-0.00428)<1e-9)?{min:-180,max:200}:{min:-50,max:200}):{min:-200,max:850}' in idx)
    check('S6: index — плейсхолдеры полей (fmtI499/fmtM499)',
          'tInp.placeholder=fmtI499(rng499.min)' in idx and
          'vInp.placeholder=fmtM499(vmin499)' in idx)
    check('S7: index — «Например:» в панели ППР нет, div-подсказок нет',
          'Например:' not in panel and 'ts-calc-range' not in idx)
    check('S8: index — бледный ::placeholder жив (обе темы)',
          '.ts-calc-field::placeholder { color: rgba(255, 255, 255, 0.4); font-weight: 500; }' in idx and
          '[data-theme="light"] .ts-calc-field::placeholder { color: rgba(20, 20, 19, 0.45); }' in idx)

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
            "localStorage.setItem('kip8_session_token','smoke-t499-a');" +
            "localStorage.setItem('app-theme','dark');")
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('temp-sensors')")
        page.wait_for_timeout(600)

        ranges = page.evaluate(
            "(() => { return Array.from(document.querySelectorAll('.ts-card-range'))"
            ".map(c => c.textContent); })()")
        check('B0: каталог: карточки −180…200 (0,00428) и −50…200 (0,00426)',
              any(r == 'НСХ: −180…200 °C' for r in ranges) and
              any(r == 'НСХ: −50…200 °C' for r in ranges), ranges[:6])

        open_sensor(page, 'cu50_1428')
        st = page.evaluate(FIELDS_JS)
        check('B1: 50М заголовок «50М (Cu50) α = 0,00428 °C⁻¹» (инвариант 498)',
              st['title'] == '50М (Cu50) α = 0,00428 °C⁻¹', st['title'])
        check('B2: плейсхолдеры «−180…200 °C» / «10,2642…92,8 Ом»',
              st['phT'] == '−180…200 °C' and st['phV'] == '10,2642…92,8 Ом',
              (st['phT'], st['phV']))
        check('B3: плейсхолдеры бледные (rgba 0.4), div-подсказок нет',
              st['phTColor'] == 'rgba(255, 255, 255, 0.4)' and
              st['divRanges'] == 0, (st['phTColor'], st['divRanges']))
        shot(page, 'a-mobile-50m.png')

        # живой расчёт по ГОСТ 5.2.3
        page.fill('#tempQueryTemp', '-180')
        page.wait_for_timeout(400)
        v = page.evaluate("document.getElementById('tempQueryVal').value")
        check('B4: 50М t=−180 → 10,2642 Ом (ГОСТ 5.2.3/А.3)', v == '10,2642', v)
        page.fill('#tempQueryTemp', '-50')
        page.wait_for_timeout(400)
        v = page.evaluate("document.getElementById('tempQueryVal').value")
        check('B5: 50М t=−50 → 39,2275 Ом (ГОСТ, не 39,3)', v == '39,2275', v)
        page.fill('#tempQueryVal', '39,2275')
        page.wait_for_timeout(400)
        t = page.evaluate("document.getElementById('tempQueryTemp').value")
        tnum = float(t.replace(',', '.')) if t else None
        check('B6: инверсия: 39,2275 Ом → ≈ −50 °C',
              tnum is not None and abs(tnum + 50) < 0.05, t)
        shot(page, 'b-mobile-50m-calc.png')

        open_sensor(page, 'pt100_1391')
        st2 = page.evaluate(FIELDS_JS)
        check('B7: 100П «100П (Pt100) α = 0,00391 °C⁻¹» + плейсхолдер',
              st2['title'] == '100П (Pt100) α = 0,00391 °C⁻¹' and
              st2['phV'] == '17,2444…395,16 Ом', (st2['title'], st2['phV']))
        page.fill('#tempQueryTemp', '-100')
        page.wait_for_timeout(400)
        v = page.evaluate("document.getElementById('tempQueryVal').value")
        check('B8: 100П: −100 → 59,6393 (А.2 ГОСТ, инвариант 498)',
              v == '59,6393', v)
        shot(page, 'c-mobile-100p.png')

        open_sensor(page, 'tc_K')
        st3 = page.evaluate(FIELDS_JS)
        check('B9: ТХА (K) — только имя + плейсхолдеры °C/мВ',
              st3['title'] == 'ТХА (K)' and
              st3['phT'] == '−270…1372 °C' and
              st3['phV'] == '−6,4577…54,8864 мВ', (st3['title'], st3['phT'], st3['phV']))
        check('B10: подпись поля значения для ТП — Термо-ЭДС',
              st3['valLabel'] == 'Термо-ЭДС E(t), мВ', st3['valLabel'])
        shot(page, 'd-mobile-tc-k.png')
        ctx.close()

        # ============ светлая ============
        ctx = browser.new_context(viewport={'width': 375, 'height': 720},
                                  is_mobile=True, has_touch=True)
        page = ctx.new_page()
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        setup_routes(ctx)
        ctx.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t499-b');" +
            "localStorage.setItem('app-theme','light');")
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'cu50_1428')
        st4 = page.evaluate(FIELDS_JS)
        check('B11: светлая: плейсхолдеры на месте, бледный тёмный цвет',
              st4['phT'] == '−180…200 °C' and
              st4['phTColor'] is not None and
              st4['phTColor'].startswith('rgba(20, 20, 19'),
              (st4['phT'], st4['phTColor']))
        shot(page, 'e-light-50m.png')
        ctx.close()

        # ============ десктоп 1280 ============
        ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = ctx.new_page()
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        setup_routes(ctx)
        ctx.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t499-c');" +
            "localStorage.setItem('app-theme','dark');")
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'cu100_1426')
        st5 = page.evaluate(FIELDS_JS)
        check('B12: десктоп 21px (инвариант 498)', st5['fs'] == '21px', st5['fs'])
        check('B13: десктоп крошки …100М (Cu100) α = 0,00426 °C⁻¹',
              st5['title'] is not None and
              st5['title'].endswith('100М (Cu100) α = 0,00426 °C⁻¹'),
              st5['title'])
        check('B14: десктоп плейсхолдеры 100М (0,00426)',
              st5['phT'] == '−50…200 °C' and st5['phV'] == '78,7…185,2 Ом',
              (st5['phT'], st5['phV']))
        shot(page, 'f-desktop-1280.png')
        ctx.close()
        browser.close()

    print('—' * 60)
    print('ИТОГО: %d OK, %d FAIL' % (PASS, FAIL))
    print('JS-ошибок: %d' % len(js_errors))
    for e in js_errors[:5]:
        print('  JS: ' + e[:200])
    raise SystemExit(1 if (FAIL or js_errors) else 0)


if __name__ == '__main__':
    main()
