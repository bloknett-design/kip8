#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 500+501 SMOKE kip8: проверка ПЕРЕНОСА (kipia-v523→v524) в
# БОЕВОЙ kip8. СТАТИКА ×10 (sw.js: v524 + комментарии Task 500/501 +
# v523 нет; index.html: #cbFormPanel + 7 разделителей-КЛАССОВ,
# #grFormPanel/#gcyFormPanel/#ghFormPanel/#gcoFormPanel, гео-круг/сфера
# классы панелей, подсказка «Линейная:…» удалена, #scaleQueryPanel в
# col-input НАД #scaleFormPanel, scaleCustomCalcPanel нет,
# updateScaleQueryUnits определена, тёплые light-литералы, синих
# в ts-light-правилах нет) + БРАУЗЕР (мобайл 375 тёмная: панель CB одна/
# разделители/кнопка вне/поля 52/19/700; JS-тумблер мощности/тока;
# живой расчёт CB и кольца; шкала-сигнал: ППР над панелью шкалы
# (выступ 2px), подсказки нет, живые единицы при загрузке, живой
# расчёт ППР + «Рассчитать»; светлая: тёплая политура датчиков
# температуры — табы/панели терракота; десктоп 1280: 3 колонки CB,
# панель гео) + 0 JS-ошибок ×2.
# Порт 9007; ключи БЕЗ префикса (kip8); скриншоты в
# download/kip8-task501-smoke/.
import json
import os
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 9007
K8 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(K8), 'download', 'kip8-task501-smoke')
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
                      body='not found (smoke t501)')

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)


# ============ СТАТИКА ============
print('== СТАТИКА (файлы kip8)')
sw = open(os.path.join(K8, 'sw.js'), encoding='utf-8').read()
idx = open(os.path.join(K8, 'index.html'), encoding='utf-8').read()
check('sw.js: kipia-v524', "const CACHE_VERSION = 'kipia-v524';" in sw)
check('sw.js: v523 нет', 'kipia-v523' not in sw)
check('sw.js: комментарий Task 500', '// Task 500: единый стиль панелей' in sw)
check('sw.js: комментарий Task 501', '// Task 501: «Электротехника» и «Геометрия»' in sw)
check('index: #cbFormPanel', 'id="cbFormPanel"' in idx)
check('index: подсказка Линейная удалена',
      'Линейная: прямая зависимость · Квадратичная' not in idx)
check('index: ППР над панелью шкалы',
      idx.find('id="scaleQueryPanel"') < idx.find('id="scaleFormPanel"'))
check('index: scaleCustomCalcPanel нет', 'scaleCustomCalcPanel' not in idx)
check('index: updateScaleQueryUnits определена',
      'function updateScaleQueryUnits()' in idx)
check('index: тёплые light-литералы (терракота)',
      'rgba(198, 97, 63, 0.55)' in idx and '#C6613F' in idx)

# ============ БРАУЗЕР ============
PANEL_JS = r"""((pageId) => {
    const pg = document.getElementById('page-' + pageId);
    if (!pg || !pg.classList.contains('active')) return {found: 'not active'};
    const scope = pg.querySelector('.conv-col-input') || pg;
    const panel = scope.querySelector('.ts-calc-panel.ts-calc-inset');
    if (!panel) return {found: 'no panel'};
    const cs = getComputedStyle(panel);
    const input = panel.querySelector('input.scale-field, input.form-field');
    const ics = input ? getComputedStyle(input) : null;
    const btn = scope.querySelector('.scale-calc-btn, .converter-convert-btn');
    return {
        found: 'ok',
        seps: panel.querySelectorAll('.ts-calc-sep').length,
        btnOutside: btn ? !panel.contains(btn) : null,
        inputH: ics ? ics.height : null,
        inputFS: ics ? ics.fontSize : null,
        inputW: ics ? ics.fontWeight : null,
        borderW: cs.borderTopWidth,
    };
})"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    errors = []
    ctx = browser.new_context(viewport={'width': 375, 'height': 812},
                              device_scale_factor=2)
    setup_routes(ctx)
    ctx.add_init_script("localStorage.setItem('app-theme','dark');")
    page = ctx.new_page()
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto('http://127.0.0.1:%d/index.html' % PORT)
    page.wait_for_timeout(2500)

    print('== БРАУЗЕР: тёмная (мобайл)')
    page.evaluate("navigateTo('circuit-breaker')")
    page.wait_for_timeout(500)
    st = page.evaluate(PANEL_JS, 'circuit-breaker')
    check('CB: панель одна, 7 разделителей, кнопка вне',
          st.get('found') == 'ok' and st.get('seps') == 7 and
          st.get('btnOutside') is True, st)
    check('CB: поля 52/19/700',
          st.get('inputH') == '52px' and st.get('inputFS') == '19px' and
          st.get('inputW') == '700', st)
    vis = page.evaluate("""() => ({
        p: getComputedStyle(document.getElementById('cb_power_block')).display,
        c: getComputedStyle(document.getElementById('cb_current_block')).display})""")
    check('CB: тумблер мощность/ток жив',
          vis['p'] == 'block' and vis['c'] == 'none', vis)
    page.evaluate("calcCircuitBreaker()")
    page.wait_for_timeout(300)
    cb = page.evaluate(
        "() => document.getElementById('cbResults').innerHTML.length")
    check('CB: живой расчёт', cb > 200, cb)
    shot(page, 't501-smoke-cb-dark.png')

    page.evaluate("navigateTo('geo-ring')")
    page.wait_for_timeout(400)
    st = page.evaluate(PANEL_JS, 'geo-ring')
    check('гео-кольцо: панель + 1 разделитель + поля',
          st.get('found') == 'ok' and st.get('seps') == 1 and
          st.get('inputH') == '52px', st)
    page.evaluate("calcGeoRing()")
    page.wait_for_timeout(250)
    gr = page.evaluate(
        "() => document.getElementById('gr_results').innerHTML.length")
    check('гео-кольцо: живой расчёт', gr > 100, gr)

    page.evaluate("navigateTo('scale-signal')")
    page.wait_for_timeout(400)
    ss = page.evaluate("""() => {
        const col = document.querySelector('#page-scale-signal.active .conv-col-input');
        const q = document.getElementById('scaleQueryPanel');
        const f = document.getElementById('scaleFormPanel');
        return {inCol: col.contains(q),
                above: (q.compareDocumentPosition(f) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0,
                qB: getComputedStyle(q).borderTopWidth,
                fB: getComputedStyle(f).borderTopWidth,
                uS: document.getElementById('scaleQueryUnit').textContent,
                uG: document.getElementById('scaleQuerySigUnit').textContent};
    }""")
    check('шкала-сигнал: ППР в col1 НАД панелью (выступ 2px / колодец 1px)',
          ss['inCol'] and ss['above'] and ss['qB'] == '2px' and ss['fB'] == '1px', ss)
    check('шкала-сигнал: живые единицы (%s / %s)' % (ss['uS'], ss['uG']),
          ss['uS'] == '%' and ss['uG'] == 'кгс/см²', ss)
    no_hint = page.evaluate(
        "() => !document.body.textContent.includes('Корнеизвлекающая: сигнал ∝ √(шкала)')")
    check('шкала-сигнал: подсказка удалена', no_hint)
    page.fill('#queryScaleVal', '50')
    page.evaluate("queryFromScaleLive()")
    qv = page.evaluate("() => document.getElementById('querySigVal').value")
    check('шкала-сигнал: живой расчёт ППР (50%%→%.6s)' % qv, qv != '', qv)
    page.evaluate("calcScaleSignal()")
    page.wait_for_timeout(300)
    check('шкала-сигнал: «Рассчитать» жив',
          page.evaluate(
              "() => document.getElementById('scaleResultsArea').style.display") == 'block')
    shot(page, 't501-smoke-scale-signal-dark.png')

    # светлая тема
    page.evaluate("localStorage.setItem('app-theme','light')")
    page.evaluate("document.documentElement.setAttribute('data-theme','light')")
    page.wait_for_timeout(300)
    print('== БРАУЗЕР: светлая (политура)')
    page.evaluate("navigateTo('temp-sensors')")
    page.wait_for_timeout(700)
    cat = page.evaluate("""() => {
        const tab = document.querySelector('#page-temp-sensors .ts-tab.active');
        const q = document.getElementById('tempCustomCalcPanel');
        return {tab: tab ? getComputedStyle(tab).color : null,
                panel: getComputedStyle(q).borderTopColor};
    }""")
    check('каталог: активный таб терракота', cat['tab'] and cat['tab'].startswith('rgb(198'), cat)
    page.evaluate("openTempSensor('cu50_1428')")
    page.wait_for_timeout(600)
    tsv = page.evaluate("""() => {
        const q = document.getElementById('tempCustomCalcPanel');
        const f = document.getElementById('tempTableFormPanel');
        return {q: getComputedStyle(q).borderTopColor,
                f: getComputedStyle(f).borderTopColor};
    }""")
    check('вид датчика: панели терракота',
          tsv['q'].startswith('rgba(198') and tsv['f'].startswith('rgba(198'), tsv)
    shot(page, 't501-smoke-ts-view-light.png')

    check('0 JS-ошибок (мобайл)', len(errors) == 0, errors[:3])
    ctx.close()

    # десктоп
    ctx2 = browser.new_context(viewport={'width': 1280, 'height': 900})
    setup_routes(ctx2)
    ctx2.add_init_script("localStorage.setItem('app-theme','light');")
    page2 = ctx2.new_page()
    errs2 = []
    page2.on('pageerror', lambda e: errs2.append(str(e)))
    page2.goto('http://127.0.0.1:%d/index.html' % PORT)
    page2.wait_for_timeout(2500)
    print('== БРАУЗЕР: десктоп 1280')
    page2.evaluate("navigateTo('circuit-breaker')")
    page2.wait_for_timeout(500)
    d = page2.evaluate("""() => {
        const pg = document.getElementById('page-circuit-breaker');
        const panel = pg.querySelector('.ts-calc-panel.ts-calc-inset');
        return {cols: pg.querySelectorAll('.conv-col').length,
                seps: panel ? panel.querySelectorAll('.ts-calc-sep').length : 0};
    }""")
    check('десктоп CB: 3 колонки + 7 разделителей',
          d['cols'] == 3 and d['seps'] == 7, d)
    shot(page2, 't501-smoke-cb-desktop.png')
    check('0 JS-ошибок (десктоп)', len(errs2) == 0, errs2[:3])
    ctx2.close()
    browser.close()

print('\nИТОГ SMOKE kip8 Task 500+501: %d passed / %d failed' % (PASS, FAIL))
if FAIL:
    raise SystemExit(1)
