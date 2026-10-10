#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 490-492 SMOKE kip8: проверка переноса партии 490+491+492
# (kipia-v515→v516) в БОЕВОЙ kip8. СТАТИКА ×10 (sw.js: версия+метка+
# 3 комментария; index.html: де-изоляция, маркеры партии) + БРАУЗЕР
# (мобайл 375 тёмная/светлая, избранное+автотаб, расходомеры
# хозрасчётные автотаб, десктоп 1280). КЛЮЧИ localStorage БЕЗ
# префикса kip8test: (де-изоляция) — отличие от kip8test-проверок.
# Порт 9007; скриншоты в download/kip8-task490-492-smoke/.
import json
import os
import re
import sys
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 9007
K8 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(K8), 'download',
                        'kip8-task490-492-smoke')
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
        page.screenshot(path=os.path.join(SHOT_DIR, name),
                        full_page=False)
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
                      body='not found (smoke k8 t490-492)')

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)


# ==================== СТАТИКА ====================
print('=== СТАТИКА (sw.js + index.html) ===')
sw = open(os.path.join(K8, 'sw.js'), encoding='utf-8').read()
idx = open(os.path.join(K8, 'index.html'), encoding='utf-8').read()
check('S1: sw.js CACHE_VERSION = kipia-v516',
      "const CACHE_VERSION = 'kipia-v516';" in sw)
check('S2: sw.js перенос-метка партии',
      '// Task 490-492 (перенос партии из kip8test@ae8cbd34):' in sw)
check('S3: sw.js kipia-v515 не осталось', 'kipia-v515' not in sw)
check('S4: sw.js 3 комментария партии (490/491/492)',
      sw.count('// Task 490:') == 1 and sw.count('// Task 491:') == 1
      and sw.count('// Task 492:') == 1 and
      'ts-bottom-bar' in sw and 'смещены ВНИЗ' in sw)
check('S5: index.html де-изоляция — блока isolateLocalStorage нет',
      'isolateLocalStorage' not in idx and
      "var DB_NAME = 'kip8-cache-v1';" in idx and
      "'kip8_phonebook_favorites'" in idx and
      'kip8test_devices_cache' not in idx)
check('S6: index.html маркеры 492 (нижний бар)',
      'tsBottomBar' in idx and 'ts-bottom-bar' in idx)
check('S7: index.html маркеры 491/492 (feat + автотаб)',
      'ts-card-feat' in idx and 'setTempSensorsTab' in idx and
      'targetTab491' in idx)
check('S8: index.html пары ТС (каталог 50М×2, 100М×2)',
      idx.count('cu50_1428') >= 1 and idx.count('cu50_1426') >= 1 and
      idx.count('cu100_1428') >= 1 and idx.count('cu100_1426') >= 1)
check('S9: index.html kipia-test-v нет; kip8test ×6 (историкалы)',
      idx.count('kipia-test-v') == 0 and idx.count('kip8test') == 6)
check('S10: index.html WorkSchedule.gs-якоря живы (486-489)',
      'silentRefresh' in idx and 'onCellHover' in idx and
      '_wsXlsDocProps' in idx)

# ==================== БРАУЗЕР ====================
BAR_JS = r"""(() => {
    const bar = document.getElementById('tsBottomBar');
    const top = document.querySelector('.ts-tabs');
    if (!bar) return {bar: false};
    const bst = getComputedStyle(bar);
    const btns = [...bar.querySelectorAll('.ts-tab')];
    const page = document.querySelector('.ts-page');
    return {
        bar: true, barDisplay: bst.display, barPosition: bst.position,
        barBottom: bst.bottom, barZ: bst.zIndex,
        topDisplay: top ? getComputedStyle(top).display : 'none-el',
        pagePadBottom: page ? getComputedStyle(page).paddingBottom : null,
        btnN: btns.length,
        btnActive: btns.map(b => b.classList.contains('active')),
        btnFont: btns.map(b => getComputedStyle(b).fontSize),
        allCount: (document.getElementById('tsAllCountMob')||{}).textContent,
        favCount: (document.getElementById('tsFavCountMob')||{}).textContent,
        barRect: (r => ({t: Math.round(r.top), h: Math.round(r.height)}))(bar.getBoundingClientRect())
    };
})()"""

GEO_JS = r"""(() => {
    const out = {rtd: [], tc: []};
    const vis = el => {
        if (!el) return null;
        const st = getComputedStyle(el);
        return st.display === 'none' ? null : el.textContent.trim();
    };
    const grab = (box, arr) => {
        [...box.querySelectorAll('.ts-card')].forEach(c => {
            const r = c.getBoundingClientRect();
            const st = getComputedStyle(c);
            const nameEl = c.querySelector('.ts-card-name-main') ||
                           c.querySelector('.ts-card-name');
            const nst = nameEl ? getComputedStyle(nameEl) : null;
            arr.push({
                key: (c.getAttribute('onclick') || '')
                    .replace(/openTempSensor\('|'\)/g, ''),
                feat: c.className.indexOf('ts-card-feat') !== -1,
                name: vis(c.querySelector('.ts-card-name-main')) ||
                      vis(c.querySelector('.ts-card-name')),
                top: Math.round(r.top), left: Math.round(r.left),
                borderWidth: st.borderWidth, boxShadow: st.boxShadow,
                bgImage: st.backgroundImage,
                nameFont: nst ? nst.fontSize : null
            });
        });
    };
    grab(document.getElementById('tsRtdCards'), out.rtd);
    grab(document.getElementById('tsTcCards'), out.tc);
    out.gridCols = getComputedStyle(
        document.getElementById('tsRtdCards')).gridTemplateColumns;
    return out;
})()"""


def ts_tab_state(page):
    return page.evaluate(r"""(() => {
        const btns = document.querySelectorAll('.ts-tab[data-ts-tab]');
        const out = {};
        btns.forEach(b => {
            out[b.getAttribute('data-ts-tab')] =
                b.classList.contains('active') + '/' +
                b.getAttribute('aria-selected');
        });
        return out;
    })()""")


def flow_tab_state(page):
    return page.evaluate(r"""(() => {
        const btns = document.querySelectorAll('.flow-tab[data-flow-tab]');
        const out = {n: btns.length};
        btns.forEach(b => {
            if (b.getAttribute('data-flow-tab') === 'fav') {
                out.favOn = b.classList.contains('active');
            } else {
                out.allOn = b.classList.contains('active');
            }
        });
        return out;
    })()""")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ============ 1. МОБАЙЛ 375, тёмная, БЕЗ избранного =============
        ctx = browser.new_context(viewport={'width': 375, 'height': 720},
                                  is_mobile=True, has_touch=True)
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        setup_routes(ctx)
        ctx.add_init_script(
            "localStorage.setItem('kip8_session_token','k8-t490-a');"
            "localStorage.setItem('app-theme','dark');")
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('temp-sensors')")
        page.wait_for_timeout(800)
        check('A: страница «Датчики температуры» активна',
              page.evaluate(
                  "document.getElementById('page-temp-sensors').classList"
                  ".contains('active')"))
        st = ts_tab_state(page)
        check('B: без избранного — вкладка «Все» активна (синхронно)',
              st.get('all', '').startswith('true') and
              st.get('fav', '').startswith('false'), st)
        bar = page.evaluate(BAR_JS)
        check('C: нижний бар ВИДЕН — grid/fixed/bottom 0',
              bar['bar'] and bar['barDisplay'] == 'grid' and
              bar['barPosition'] == 'fixed' and bar['barBottom'] == '0px',
              bar)
        check('D: верхние .ts-tabs на мобильном СКРЫТЫ',
              bar['topDisplay'] == 'none', bar['topDisplay'])
        check('E: 2 кнопки, «Все» active, счётчики 17/0',
              bar['btnN'] == 2 and bar['btnActive'][0] and
              not bar['btnActive'][1] and bar['allCount'] == '17' and
              bar['favCount'] == '0',
              (bar['btnN'], bar['btnActive'], bar['allCount'],
               bar['favCount']))
        geo = page.evaluate(GEO_JS)
        r, t = geo['rtd'], geo['tc']
        check('F: сетка ДВЕ колонки, 8 ТС + 9 ТП',
              len(geo['gridCols'].split()) == 2 and len(r) == 8
              and len(t) == 9,
              (geo['gridCols'], len(r), len(t)))

        def pair_row(i, j):
            a, b = r[i], r[j]
            return abs(a['top'] - b['top']) < 5 and \
                abs(a['left'] - b['left']) > 50
        check('G: пары живы — 50М+50М, 100М+100М, 50П+100П, Pt100+Pt1000',
              pair_row(0, 1) and pair_row(2, 3) and pair_row(4, 5) and
              pair_row(6, 7) and r[0]['name'] == '50М' and
              r[2]['name'] == '100М' and r[4]['name'] == '50П' and
              r[6]['name'] == 'Pt100',
              [(c['name']) for c in r])
        check('H: БЕЗ избранного — 0 feat-классов',
              not any(c['feat'] for c in r + t),
              [(c['name'], c['feat']) for c in r[:4]])
        check('I: у ВСЕХ кнопок шрифт 17px (≤400px, единый)',
              all(c['nameFont'] == '17px' for c in r + t),
              [(c['name'], c['nameFont']) for c in r[:4]])
        check('J: у ВСЕХ кнопок рамка 1px, без тени/градиента',
              all(c['borderWidth'] == '1px' and
                  c['boxShadow'] == 'none' and
                  c['bgImage'] == 'none' for c in r + t),
              [(c['name'], c['borderWidth']) for c in r[:4]])
        # клики по нижнему бару: Избранные (пусто) → Все
        page.click("#tsBottomBar .ts-tab[data-ts-tab='fav']", timeout=4000)
        page.wait_for_timeout(500)
        check('K: клик «Избранные» — пустой блок, кнопка active',
              page.evaluate(
                  "document.querySelector('#tsBottomBar .ts-tab"
                  "[data-ts-tab=\\'fav\\']').classList.contains('active')") and
              page.evaluate(
                  "document.getElementById('tsRtdCards').textContent"
                  ".indexOf('Нет избранных датчиков') !== -1"))
        page.click("#tsBottomBar .ts-tab[data-ts-tab='all']", timeout=4000)
        page.wait_for_timeout(500)
        check('L: клик «Все» — карточки вернулись (8)',
              page.evaluate(
                  "document.querySelectorAll('#tsRtdCards .ts-card')"
                  ".length") == 8)
        shot(page, 'a-mobile-dark-all.png')

        # ============ 2. ИЗБРАННОЕ на мобайле (тот же контекст) =========
        page.click("#tsRtdCards .ts-card:has-text('50М') .ts-card-fav-btn",
                   timeout=4000)
        page.wait_for_timeout(400)
        page.mouse.move(10, 10)   # отвод :hover — покой карточки
        page.wait_for_timeout(200)
        fav_now = page.evaluate(r"""(() => {
            const c = document.querySelector(
                "#tsRtdCards .ts-card[onclick*='cu50_1428']");
            if (!c) return null;
            const st = getComputedStyle(c);
            const nameEl = c.querySelector('.ts-card-name-main') ||
                           c.querySelector('.ts-card-name');
            return {feat: c.className.indexOf('ts-card-feat') !== -1,
                    bw: st.borderWidth, sh: st.boxShadow,
                    bg: st.backgroundImage, bgFull: st.background,
                    fs: nameEl ? getComputedStyle(nameEl).fontSize : null,
                    favCount: document.getElementById('tsFavCountMob').textContent};
        })()""")
        check('M: звезда на 50М → карточка СРАЗУ feat (2px/тень/градиент)',
              fav_now and fav_now['feat'] and fav_now['bw'] == '2px' and
              fav_now['sh'] != 'none' and
              ('linear-gradient' in fav_now['bg'] or
               'linear-gradient' in fav_now['bgFull']),
              fav_now and (fav_now['bw'], fav_now['sh'][:40]))
        check('N: feat-шрифт = общему (17px), счётчик бара = 1',
              fav_now and fav_now['fs'] == '17px' and
              fav_now['favCount'] == '1', fav_now)
        geo2 = page.evaluate(GEO_JS)
        r2 = geo2['rtd']
        check('O: feat ровно 1 (избранная 50М), остальные обычные',
              sum(1 for c in r2 if c['feat']) == 1 and
              all(c['borderWidth'] == '1px' and c['boxShadow'] == 'none'
                  for c in r2 if not c['feat']),
              [(c['name'], c['feat']) for c in r2])
        shot(page, 'b-mobile-fav-feat.png')

        page.reload()
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('temp-sensors')")
        page.wait_for_timeout(800)
        st2 = ts_tab_state(page)
        check('P: РЕЛОАД + избранное → автотаб «Избранные» (бар active)',
              st2.get('fav', '').startswith('true') and
              st2.get('all', '').startswith('false'), st2)
        check('Q: в «Избранных» — 1 карточка 50М с feat-классом',
              page.evaluate(
                  "document.querySelectorAll('#tsRtdCards .ts-card')"
                  ".length") == 1 and
              page.evaluate(
                  "document.querySelector('#tsRtdCards .ts-card')"
                  ".className.indexOf('ts-card-feat') !== -1"))
        bar2 = page.evaluate(BAR_JS)
        check('R: счётчики бара после релоада: 17/1, «Избранные» active',
              bar2['allCount'] == '17' and bar2['favCount'] == '1' and
              bar2['btnActive'][1] and not bar2['btnActive'][0],
              (bar2['allCount'], bar2['favCount'], bar2['btnActive']))
        page.click("#tsBottomBar .ts-tab[data-ts-tab='all']", timeout=4000)
        page.wait_for_timeout(500)
        geo3 = page.evaluate(GEO_JS)
        check('S: «Все» через бар — 8 ТС, feat только у 50М',
              len(geo3['rtd']) == 8 and
              sum(1 for c in geo3['rtd'] if c['feat']) == 1,
              [(c['name'], c['feat']) for c in geo3['rtd']])
        check('T: 0 JS-ошибок (мобайл тёмная)', len(js_errors) == 0,
              js_errors[:3])
        ctx.close()

        # ============ 3. СВЕТЛАЯ тема мобайл (посев избранного) =========
        ctx4 = browser.new_context(viewport={'width': 375, 'height': 720},
                                   is_mobile=True, has_touch=True)
        page4 = ctx4.new_page()
        js_errors4 = []
        page4.on('pageerror', lambda e: js_errors4.append(str(e)))
        page4.on('dialog', lambda d: d.accept())
        setup_routes(ctx4)
        ctx4.add_init_script(
            "localStorage.setItem('kip8_session_token','k8-t490-b');"
            "localStorage.setItem('app-theme','light');"
            "localStorage.setItem('kip8_temp_fav_v1',"
            "'{\\\"cu50_1428\\\":\\\"2026-10-01T00:00:00.000Z\\\"}');")
        page4.goto('http://localhost:%d/index.html' % PORT)
        page4.wait_for_timeout(2500)
        page4.evaluate("navigateTo('temp-sensors')")
        page4.wait_for_timeout(800)
        light = page4.evaluate(r"""(() => {
            const barBtn = document.querySelector(
                "#tsBottomBar .ts-tab[data-ts-tab='all']");
            const c = document.querySelector(
                '#tsRtdCards .ts-card.ts-card-feat');
            const out = {btnColor: barBtn ? getComputedStyle(barBtn).color
                                          : null};
            if (c) {
                const st = getComputedStyle(c);
                out.borderColor = st.borderColor;
                out.bgImage = st.backgroundImage;
                out.boxShadow = st.boxShadow;
            }
            out.favActive = !!(document.querySelector(
                "#tsBottomBar .ts-tab[data-ts-tab='fav']").classList
                .contains('active'));
            return out;
        })()""")
        check('U: светлая — автотаб «Избранные», светлая палитра кнопки',
              light['favActive'] and light['btnColor'] and
              light['btnColor'].startswith('rgba(43, 111, 163'), light)
        check('V: светлая — feat-бордер светлой палитры + градиент/тень',
              light.get('borderColor', '').startswith('rgba(43, 111, 163') and
              'linear-gradient' in light.get('bgImage', '') and
              light.get('boxShadow', 'none') != 'none',
              (light.get('borderColor'), light.get('boxShadow', '')[:40]))
        shot(page4, 'c-mobile-light-fav-feat.png')
        check('W: светлая — 0 JS-ошибок', len(js_errors4) == 0,
              js_errors4[:3])
        ctx4.close()

        # ============ 4. РАСХОДОМЕРЫ хозрасчётные — автотаб =============
        ctx2 = browser.new_context(viewport={'width': 375, 'height': 720},
                                   is_mobile=True, has_touch=True)
        page2 = ctx2.new_page()
        js_errors2 = []
        page2.on('pageerror', lambda e: js_errors2.append(str(e)))
        page2.on('dialog', lambda d: d.accept())
        setup_routes(ctx2)
        ctx2.add_init_script(
            "localStorage.setItem('kip8_session_token','k8-t490-c');"
            "localStorage.setItem('app-theme','dark');"
            "localStorage.setItem('kip8_flow_fav_v1',"
            "'{\"1\":\"2026-10-01T00:00:00.000Z\","
            "\"3\":\"2026-10-02T00:00:00.000Z\"}');"
            "localStorage.setItem('kip8_flow_fav_order_v1',"
            "'[\"1\",\"3\"]');")
        page2.goto('http://localhost:%d/index.html' % PORT)
        page2.wait_for_timeout(2500)
        page2.evaluate("navigateTo('flowmeter-data')")
        page2.wait_for_timeout(1500)
        ftab = flow_tab_state(page2)
        check('X: расходомеры с FlowFav → вкладка «Избранные» АКТИВНА '
              '(все .flow-tab синхронны)',
              ftab['favOn'] and not ftab['allOn'] and ftab['n'] >= 2, ftab)
        check('Y: расходомеры — 0 JS-ошибок', len(js_errors2) == 0,
              js_errors2[:3])
        ctx2.close()

        # ============ 5. ДЕСКТОП 1280 (посев избранного) ================
        ctx5 = browser.new_context(viewport={'width': 1280, 'height': 800})
        page5 = ctx5.new_page()
        js_errors5 = []
        page5.on('pageerror', lambda e: js_errors5.append(str(e)))
        page5.on('dialog', lambda d: d.accept())
        setup_routes(ctx5)
        ctx5.add_init_script(
            "localStorage.setItem('kip8_session_token','k8-t490-d');"
            "localStorage.setItem('app-theme','dark');"
            "localStorage.setItem('kip8_temp_fav_v1',"
            "'{\\\"cu50_1428\\\":\\\"2026-10-01T00:00:00.000Z\\\"}');")
        page5.goto('http://localhost:%d/index.html' % PORT)
        page5.wait_for_timeout(2500)
        page5.evaluate("navigateTo('temp-sensors')")
        page5.wait_for_timeout(800)
        desk = page5.evaluate(r"""(() => {
            const bar = document.getElementById('tsBottomBar');
            const top = document.querySelector('.ts-tabs');
            const cards = [...document.querySelectorAll('#tsRtdCards .ts-card')];
            const out = [];
            cards.forEach(c => {
                const nameEl = c.querySelector('.ts-card-name-main') ||
                               c.querySelector('.ts-card-name');
                out.push({
                    name: nameEl ? nameEl.textContent.trim() : '',
                    feat: c.className.indexOf('ts-card-feat') !== -1,
                    bw: getComputedStyle(c).borderWidth,
                    fs: nameEl ? getComputedStyle(nameEl).fontSize : null,
                    sh: getComputedStyle(c).boxShadow,
                    bg: getComputedStyle(c).backgroundImage
                });
            });
            return {
                barDisplay: bar ? getComputedStyle(bar).display : 'none-el',
                topDisplay: top ? getComputedStyle(top).display : 'none-el',
                cards: out,
                topBtnActive: !!(document.querySelector(
                    ".ts-tabs .ts-tab[data-ts-tab='fav']").classList
                    .contains('active'))
            };
        })()""")
        check('Z: десктоп — нижний бар СКРЫТ, верхние .ts-tabs ВИДНЫ',
              desk['barDisplay'] == 'none' and desk['topDisplay'] == 'flex',
              (desk['barDisplay'], desk['topDisplay']))
        check('AA: десктоп — автотаб «Избранные» и ВЕРХНЕЙ вкладкой',
              desk['topBtnActive'], desk['topBtnActive'])
        check('AB: десктоп — feat-класс в DOM, но рамка 1px (стили mobile)',
              any(c['feat'] for c in desk['cards']) and
              all(c['bw'] == '1px' for c in desk['cards']),
              [(c['name'], c['feat'], c['bw']) for c in desk['cards'][:4]])
        page5.evaluate("setTempSensorsTab('all')")
        page5.wait_for_timeout(400)
        desk_all = page5.evaluate(r"""(() => {
            const cards = [...document.querySelectorAll('#tsRtdCards .ts-card')];
            return cards.map(c => {
                const nameEl = c.querySelector('.ts-card-name-main') ||
                               c.querySelector('.ts-card-name');
                return {
                    name: nameEl ? nameEl.textContent.trim() : '',
                    feat: c.className.indexOf('ts-card-feat') !== -1,
                    fs: nameEl ? getComputedStyle(nameEl).fontSize : null,
                    sh: getComputedStyle(c).boxShadow,
                    bg: getComputedStyle(c).backgroundImage
                };
            });
        })()""")
        check('AC: десктоп — шрифт 17px (база), без тени/градиента',
              len(desk_all) == 8 and
              all(c['fs'] == '17px' and c['sh'] == 'none' and
                  c['bg'] == 'none' for c in desk_all),
              [(c['name'], c['fs']) for c in desk_all[:4]])
        check('AD: десктоп — порядок ТС 50М, 50М, 100М, 100М',
              [c['name'] for c in desk_all[:4]] ==
              ['50М', '50М', '100М', '100М'],
              [c['name'] for c in desk_all])
        shot(page5, 'd-desktop-top-tabs.png')
        check('AE: десктоп — 0 JS-ошибок', len(js_errors5) == 0,
              js_errors5[:3])
        ctx5.close()

        browser.close()

    print('')
    print('ИТОГ: %d passed, %d failed' % (PASS, FAIL))
    if FAIL:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
