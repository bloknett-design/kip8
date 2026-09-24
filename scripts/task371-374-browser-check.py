#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 371-374 (перенос в kip8): browser-check — пакет «Датчики
# температуры» в боевом репозитории:
#   1. десктоп 1280 тёмная: страница карточек — 8 ТС + 9 ТП (ТХК (L)
#      с хромель-копель −200…800); табы «Все 17 / Избранные 0»;
#      бейджей ТС/ТП на карточках НЕТ; звёзды есть; клик ☆ → ★,
#      счётчик «Избранные 1», таб «Избранные» фильтрует.
#   2. страница датчика ТХК (L): панель «Расчёт произвольных значений»
#      НАД формой выбора диапазона/шага (видна СРАЗУ); живой расчёт
#      t=100 → 6,862 мВ; «Рассчитать» → таблица E(t) БЕЗ кнопки
#      «Копировать» (Task 374), кнопок в результатах 0.
#   3. ТС 50М: «Рассчитать» → таблица R(t), R(50)=60,7, кнопки нет.
#   4. Соседний раздел «Шкала-сигнал» — своя кнопка «Копировать»
#      ОСТАЛАСЬ (не тронута).
#   5. светлая тема: ТХА (K) — таблица без кнопки, E(100)=4,096.
#   6. мобайл 375: карточки СТОЛБИКОМ по одной в строке.
# + 0 JS-ошибок; скриншот-пруфы (desktop/light/mobile).
import json
import sys
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8976

def mock_response(action, body):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local', 'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'flowmeter.view': True, 'workschedule.view': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    return {'ok': True, 'data': {'ok': True}}

PASS = 0
FAIL = 0
def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok: PASS += 1
    else: FAIL += 1
    print(('  ✓ ' if ok else '  ✗ ') + name + (('  [' + str(extra) + ']') if (extra and not ok) else ''))

def parse_ru(s):
    s = str(s).replace('\u00a0', '').replace(',', '.')
    try: return float(s)
    except Exception: return None

with sync_playwright() as p:
    browser = p.chromium.launch()

    # ================= Контекст 1: десктоп 1280, тёмная =================
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
    page = ctx.new_page()
    js_errors = []
    page.on('pageerror', lambda e: js_errors.append(str(e)))
    page.on('dialog', lambda d: d.accept())

    def handle(route, request):
        url = request.url
        action = ''
        if 'action=' in url:
            action = unquote(url.split('action=')[1].split('&')[0])
        route.fulfill(status=200, content_type='application/json; charset=utf-8',
                      body=json.dumps(mock_response(action, None), ensure_ascii=False).encode('utf-8'))
    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    def block_external(route):
        route.fulfill(status=404, content_type='text/plain', body='not found (browser-check t371-374-k8)')
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)

    # kip8: localStorage БЕЗ префикса (изоляция только в kip8test)
    ctx.add_init_script(
        "localStorage.setItem('kip8_session_token','bc-t374-k8-a');" +
        "localStorage.setItem('app-theme','dark');")
    page.goto('http://localhost:%d/index.html' % PORT)
    page.wait_for_timeout(2500)
    check('A: страница загрузилась', page.evaluate("document.title==='КИПиА'"))

    # --- страница карточек (Task 372/373) ---
    page.evaluate("navigateTo('temp-sensors')")
    page.wait_for_timeout(800)
    check('B: страница «Датчики температуры» активна',
          page.evaluate("document.getElementById('page-temp-sensors').classList.contains('active')"))
    check('C: карточек ТС = 8',
          page.evaluate("document.querySelectorAll('#tsRtdCards .ts-card').length") == 8,
          page.evaluate("document.querySelectorAll('#tsRtdCards .ts-card').length"))
    check('D: карточек ТП = 9 (ТХК (L))',
          page.evaluate("document.querySelectorAll('#tsTcCards .ts-card').length") == 9,
          page.evaluate("document.querySelectorAll('#tsTcCards .ts-card').length"))
    check('E: ТХК (L) хромель-копель −200…800',
          page.evaluate("""(function(){
            var cards = document.querySelectorAll('#tsTcCards .ts-card');
            for (var i=0;i<cards.length;i++){
              var t = cards[i].textContent;
              if (t.indexOf('ТХК (L)') !== -1){
                return t.indexOf('хромель-копель') !== -1 && t.indexOf('−200…800') !== -1;
              }
            }
            return false;
          })()"""))
    check('F: табы «Все 17 / Избранные 0»',
          page.evaluate("""(function(){
            var tabs = document.querySelector('#page-temp-sensors .ts-tabs');
            return !!tabs && document.getElementById('tsAllCount').textContent === '17' && document.getElementById('tsFavCount').textContent === '0';
          })()"""))
    check('G: бейджей ТС/ТП на карточках НЕТ (Task 373)',
          page.evaluate("document.querySelectorAll('#page-temp-sensors .ts-card-badge').length") == 0)
    check('H: звёзды на карточках есть',
          page.evaluate("document.querySelectorAll('#page-temp-sensors .ts-card-fav-btn').length") == 17,
          page.evaluate("document.querySelectorAll('#page-temp-sensors .ts-card-fav-btn').length"))

    # --- избранное: клик ☆ → ★, счётчик, фильтр (Task 373) ---
    page.click("#tsTcCards .ts-card:has-text('ТХА (K)') .ts-card-fav-btn")
    page.wait_for_timeout(500)
    check('I: звезда нажата — «Избранные 1»',
          page.evaluate("document.getElementById('tsFavCount').textContent === '1'"),
          page.evaluate("document.getElementById('tsFavCount').textContent"))
    check('J: звезда стала ★',
          page.evaluate("""(function(){
            var cards = document.querySelectorAll('#tsTcCards .ts-card');
            for (var i=0;i<cards.length;i++){
              if (cards[i].textContent.indexOf('ТХА (K)') !== -1){
                return cards[i].querySelector('.ts-card-fav-btn').textContent.indexOf('★') !== -1;
              }
            }
            return false;
          })()"""))
    page.click(".ts-tab[data-ts-tab='fav']")
    page.wait_for_timeout(500)
    check('K: таб «Избранные» — только 1 карточка',
          page.evaluate("document.querySelectorAll('#page-temp-sensors .ts-card').length") == 1,
          page.evaluate("document.querySelectorAll('#page-temp-sensors .ts-card').length"))
    check('L: пустая группа ТС скрыта',
          page.evaluate("""(function(){
            var h = document.getElementById('tsRtdGroupTitle');
            return !h || h.style.display === 'none' || h.offsetParent === null;
          })()"""))
    page.click(".ts-tab[data-ts-tab='all']")
    page.wait_for_timeout(400)

    # --- страница датчика ТХК (L): панель над формой + живой расчёт ---
    page.click("#tsTcCards .ts-card:has-text('ТХК (L)')")
    page.wait_for_timeout(700)
    check('M: страница датчика открыта',
          page.evaluate("document.getElementById('page-temp-sensor-view').classList.contains('active')"))
    check('N: панель «Расчёт произвольных значений» НАД формой (Task 373)',
          page.evaluate("""(function(){
            var panel = document.getElementById('tempCustomCalcPanel');
            var range = document.getElementById('temp_sensor_min');
            return !!panel && !!range && (panel.compareDocumentPosition(range) & Node.DOCUMENT_POSITION_FOLLOWING);
          })()"""))
    check('O: панель видна СРАЗУ (до «Рассчитать»)',
          page.evaluate("document.getElementById('tempCustomCalcPanel').offsetParent !== null"))
    check('P: подпись «Термо-ЭДС E(t), мВ»',
          page.evaluate("document.getElementById('tempQueryValLabel').textContent.indexOf('Термо-ЭДС') !== -1"))
    page.fill("#tempQueryTemp", "100")
    page.wait_for_timeout(500)
    val = parse_ru(page.evaluate("document.getElementById('tempQueryVal').value"))
    check('Q: живой расчёт E(100) ≈ 6,862 мВ', val is not None and abs(val - 6.862) < 0.005, val)
    check('R: звезда в шапке страницы датчика',
          page.evaluate("document.getElementById('tempSensorFavBtn') !== null"))

    # --- Рассчитать → таблица БЕЗ кнопки «Копировать» (Task 374) ---
    page.fill("#temp_sensor_min", "0")
    page.fill("#temp_sensor_max", "100")
    page.fill("#temp_sensor_step", "50")
    page.click("#page-temp-sensor-view button.converter-convert-btn:has-text('Рассчитать')")
    page.wait_for_timeout(700)
    res = page.evaluate("""(function(){
        var r = document.getElementById('tempSensorResults');
        return {
            visible: r.style.display !== 'none',
            table: !!document.getElementById('tempTableContainer'),
            title: r.textContent.indexOf('Таблица значений (шаг 50°C)') !== -1,
            copyBtnText: r.textContent.indexOf('Копировать') !== -1,
            nButtons: r.querySelectorAll('button').length,
            e100: r.textContent.indexOf('6,8617') !== -1
        };
    })()""")
    check('S: результаты показаны', res['visible'])
    check('T: таблица значений есть', res['table'])
    check('U: заголовок таблицы есть', res['title'])
    check('V: кнопки «Копировать» НЕТ (Task 374)', not res['copyBtnText'])
    check('W: кнопок в результатах 0 шт.', res['nButtons'] == 0, res['nButtons'])
    check('X: E(100) ≈ 6,8617 мВ в таблице', res['e100'])
    page.screenshot(path='scripts/task371-374-proof-desktop.png', full_page=False)

    # --- ТС 50М: таблица R(t) без кнопки ---
    page.evaluate("navigateTo('temp-sensors')")
    page.wait_for_timeout(600)
    page.click("#tsRtdCards .ts-card:has-text('50М')")
    page.wait_for_timeout(600)
    page.fill("#temp_sensor_min", "0")
    page.fill("#temp_sensor_max", "100")
    page.fill("#temp_sensor_step", "50")
    page.click("#page-temp-sensor-view button.converter-convert-btn:has-text('Рассчитать')")
    page.wait_for_timeout(700)
    res2 = page.evaluate("""(function(){
        var r = document.getElementById('tempSensorResults');
        return {
            table: !!document.getElementById('tempTableContainer'),
            copyBtnText: r.textContent.indexOf('Копировать') !== -1,
            r50: r.textContent.indexOf('60,7') !== -1,
            rCol: r.textContent.indexOf('R(t), Ом') !== -1
        };
    })()""")
    check('Y: ТС — таблица R(t) есть', res2['table'] and res2['rCol'])
    check('Z: ТС — R(50) = 60,7 Ом', res2['r50'])
    check('AA: ТС — кнопки «Копировать» НЕТ', not res2['copyBtnText'])

    # --- Соседний раздел «Шкала-сигнал»: своя кнопка на месте ---
    page.evaluate("navigateTo('scale-signal')")
    page.wait_for_timeout(700)
    scale_ok = page.evaluate("""(function(){
        var b = document.querySelector('#scaleResultsArea button.query-btn');
        return !!(b && b.textContent.indexOf('Копировать') !== -1 && b.getAttribute('onclick').indexOf('copyScaleTable') !== -1);
    })()""")
    check('AB: «Шкала-сигнал» — своя кнопка «Копировать» на месте', scale_ok)
    check('AC: десктоп — 0 JS-ошибок', len(js_errors) == 0, js_errors[:3])
    ctx.close()

    # ================= Контекст 2: светлая тема =================
    ctx2 = browser.new_context(viewport={'width': 1280, 'height': 800})
    page2 = ctx2.new_page()
    js_errors2 = []
    page2.on('pageerror', lambda e: js_errors2.append(str(e)))
    page2.on('dialog', lambda d: d.accept())
    ctx2.route('**/exec?**', handle)
    ctx2.route('**script.google.com/**', handle)
    ctx2.route('**raw.githubusercontent.com/**', block_external)
    ctx2.route('**calendar.legalic.ru/**', block_external)
    ctx2.add_init_script(
        "localStorage.setItem('kip8_session_token','bc-t374-k8-b');" +
        "localStorage.setItem('app-theme','light');")
    page2.goto('http://localhost:%d/index.html' % PORT)
    page2.wait_for_timeout(2500)
    page2.evaluate("navigateTo('temp-sensors')")
    page2.wait_for_timeout(700)
    page2.click("#tsTcCards .ts-card:has-text('ТХА (K)')")
    page2.wait_for_timeout(600)
    page2.fill("#temp_sensor_min", "0")
    page2.fill("#temp_sensor_max", "100")
    page2.fill("#temp_sensor_step", "50")
    page2.click("#page-temp-sensor-view button.converter-convert-btn:has-text('Рассчитать')")
    page2.wait_for_timeout(700)
    res3 = page2.evaluate("""(function(){
        var r = document.getElementById('tempSensorResults');
        return {
            table: !!document.getElementById('tempTableContainer'),
            copyBtnText: r.textContent.indexOf('Копировать') !== -1,
            e100: r.textContent.indexOf('4,096') !== -1
        };
    })()""")
    check('AD: светлая — таблица есть (ТХА K)', res3['table'])
    check('AE: светлая — кнопки «Копировать» НЕТ', not res3['copyBtnText'])
    check('AF: светлая — E(100) = 4,096 мВ (НИСТ)', res3['e100'])
    page2.screenshot(path='scripts/task371-374-proof-light.png', full_page=False)
    check('AG: светлая — 0 JS-ошибок', len(js_errors2) == 0, js_errors2[:3])
    ctx2.close()

    # ================= Контекст 3: мобайл 375 =================
    ctx3 = browser.new_context(viewport={'width': 375, 'height': 700})
    page3 = ctx3.new_page()
    js_errors3 = []
    page3.on('pageerror', lambda e: js_errors3.append(str(e)))
    page3.on('dialog', lambda d: d.accept())
    ctx3.route('**/exec?**', handle)
    ctx3.route('**script.google.com/**', handle)
    ctx3.route('**raw.githubusercontent.com/**', block_external)
    ctx3.route('**calendar.legalic.ru/**', block_external)
    ctx3.add_init_script(
        "localStorage.setItem('kip8_session_token','bc-t374-k8-c');" +
        "localStorage.setItem('app-theme','dark');")
    page3.goto('http://localhost:%d/index.html' % PORT)
    page3.wait_for_timeout(2500)
    page3.evaluate("navigateTo('temp-sensors')")
    page3.wait_for_timeout(800)
    grid_cols = page3.evaluate("getComputedStyle(document.getElementById('tsRtdCards')).gridTemplateColumns")
    n_tracks = len([c for c in grid_cols.split() if c.replace('.', '').replace('-', '').isdigit()]) if grid_cols != 'none' else 0
    check('AH: мобайл — сетка ОДНА колонка (столбиком)', grid_cols != 'none' and n_tracks <= 1, grid_cols)
    geom = page3.evaluate("""(function(){
            var card = document.querySelector('#tsRtdCards .ts-card');
            var rect = card.getBoundingClientRect();
            return { left: rect.left, right: window.innerWidth - rect.right,
                     width: rect.width, vw: window.innerWidth };
          })()""")
    check('AI: мобайл — карточка на всю строку (отступы ≤ 20px)',
          geom['left'] <= 20 and geom['right'] <= 20 and geom['width'] >= geom['vw'] - 44, geom)
    page3.screenshot(path='scripts/task371-374-proof-mobile.png', full_page=False)
    check('AJ: мобайл — 0 JS-ошибок', len(js_errors3) == 0, js_errors3[:3])
    ctx3.close()

    browser.close()

print('')
print('ИТОГО: %d passed, %d failed (из %d)' % (PASS, FAIL, PASS + FAIL))
sys.exit(0 if FAIL == 0 else 1)
