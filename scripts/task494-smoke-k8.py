#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 494 SMOKE kip8: проверка переноса (kipia-v517→v518) в БОЕВОЙ
# kip8. СТАТИКА ×7 (sw.js: версия v518 + комментарий 494 + v517 нет;
# index.html: заголовок/подсказка панели удалены + ts-calc-field у
# обоих полей + CSS выступа + media-override) + БРАУЗЕР (мобайл 375
# тёмная: датчик 50М — панель без заголовка/подсказки, 2px/градиент/
# inset-тень, поля 19px/52px/700/белый, живой расчёт; ТП tc_K —
# подпись Термо-ЭДС; светлая тема; десктоп 1280).
# Порт 9007; скриншоты в download/kip8-task494-smoke/.
import json
import os
import re
import sys
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 9007
K8 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(K8), 'download', 'kip8-task494-smoke')
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
                      body='not found (smoke t494)')

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)


PANEL_JS = r"""(() => {
    const p = document.getElementById('tempCustomCalcPanel');
    if (!p) return {panel: false};
    const st = getComputedStyle(p);
    const t = document.getElementById('tempQueryTemp');
    const v = document.getElementById('tempQueryVal');
    const tst = t ? getComputedStyle(t) : null;
    return {
        panel: true,
        titleText: p.textContent.indexOf('Расчёт произвольных значений') !== -1,
        hintText: p.textContent.indexOf('Введите значение в любое поле') !== -1,
        borderWidth: st.borderWidth,
        boxShadow: st.boxShadow,
        bgImage: st.backgroundImage,
        valLabelText: (document.getElementById('tempQueryValLabel')||{}).textContent,
        fieldsN: p.querySelectorAll('.ts-calc-field').length,
        tFont: tst ? tst.fontSize : null,
        tWeight: tst ? tst.fontWeight : null,
        tColor: tst ? tst.color : null,
        tHeight: t ? Math.round(t.getBoundingClientRect().height) : null,
        tValue: t ? t.value : null,
        vValue: v ? v.value : null
    };
})()"""


def open_sensor(page, key):
    page.evaluate("openTempSensor('%s')" % key)
    page.wait_for_timeout(500)


def main():
    # ---------------- СТАТИКА ----------------
    print('== СТАТИКА ==')
    sw = open(os.path.join(K8, 'sw.js'), encoding='utf-8').read()
    idx = open(os.path.join(K8, 'index.html'), encoding='utf-8').read()
    check('sw.js: CACHE_VERSION = kipia-v518 (один инкремент)',
          "const CACHE_VERSION = 'kipia-v518';" in sw)
    check('sw.js: v517 отсутствует', 'kipia-v517' not in sw)
    check('sw.js: комментарий Task 494',
          'Task 494' in sw and 'tempCustomCalcPanel' in sw)
    check('index.html: заголовок панели удалён',
          '<div class="ts-calc-title">' not in idx)
    # ПОДВОДНЫЙ КАМЕНЬ: текст подсказки жив в ДРУГИХ разделах
    # (шкала-сигнал @~18435, буй — «два других»); проверяем
    # отсутствие ИМЕННО в чанке панели датчиков температуры
    i_p = idx.find('id="tempCustomCalcPanel"')
    i_r = idx.find('id="temp_sensor_min"')
    panel = idx[i_p:i_r] if (i_p != -1 and i_r != -1) else ''
    check('index.html: подсказка панели удалена (в чанке панели)',
          i_p != -1 and 'Введите значение в любое поле' not in panel and
          'ts-calc-hint' not in panel)
    check('index.html: ts-calc-field у обоих полей',
          idx.count('class="scale-field ts-calc-field"') == 2)
    check('index.html: CSS выступа (рамка 2px + градиент + тень)',
          '.ts-calc-panel { padding: 16px; background-color: var(--card-bg);' in idx and
          'border: 2px solid rgba(74, 143, 199, 0.85);' in idx and
          'inset 0 -3px 0 rgba(0, 0, 0, 0.3);' in idx)
    check('index.html: media-override ×2 (19px/52px)',
          idx.count('.ts-calc-field { padding: 10px 14px; '
                    'font-size: 19px; height: 52px; }') == 2)

    # ---------------- БРАУЗЕР ----------------
    with sync_playwright() as p:
        browser = p.chromium.launch()
        errors = []

        print('== БРАУЗЕР: мобайл 375 тёмная ==')
        ctx = browser.new_context(
            viewport={'width': 375, 'height': 720},
            is_mobile=True, has_touch=True,
            color_scheme='dark', locale='ru-RU')
        setup_routes(ctx)
        # Де-изоляция: kip8 БЕЗ префикса kip8test:
        ctx.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t494-a');" +
            "localStorage.setItem('app-theme','dark');")
        page = ctx.new_page()
        page.on('dialog', lambda d: d.accept())
        page.on('pageerror', lambda e: errors.append('m: ' + str(e)))
        page.goto('http://127.0.0.1:%d/index.html' % PORT)
        page.wait_for_timeout(2500)

        page.evaluate("navigateTo('temp-sensors')")
        page.wait_for_timeout(600)
        open_sensor(page, 'cu50_1428')
        check('страница датчика активна',
              page.evaluate(
                  "document.getElementById('page-temp-sensor-view')"
                  ".classList.contains('active')"))
        st = page.evaluate(PANEL_JS)
        check('панель: заголовка/подсказки в DOM НЕТ',
              st['panel'] and not st['titleText'] and not st['hintText'], st)
        check('панель: рамка 2px + градиент + inset-тень',
              st['borderWidth'] == '2px' and
              'linear-gradient' in st['bgImage'] and
              'inset' in st['boxShadow'],
              (st['borderWidth'], st['bgImage'][:40]))
        check('поля: 2 шт, 19px/52px/700/белый',
              st['fieldsN'] == 2 and st['tFont'] == '19px' and
              st['tHeight'] == 52 and str(st['tWeight']) == '700' and
              st['tColor'] == 'rgb(255, 255, 255)',
              (st['fieldsN'], st['tFont'], st['tHeight']))
        check('подпись ТС подставлена',
              st['valLabelText'] == 'Сопротивление R(t), Ом',
              st['valLabelText'])
        page.fill('#tempQueryTemp', '55')
        page.wait_for_timeout(400)
        st2 = page.evaluate(PANEL_JS)
        check('живой расчёт: t=55 → R(t)',
              st2['vValue'] not in (None, '') and
              float(st2['vValue'].replace(',', '.')) > 61,
              (st2['tValue'], st2['vValue']))
        shot(page, 'a-mobile-dark-rtd.png')

        open_sensor(page, 'tc_K')
        st3 = page.evaluate(PANEL_JS)
        check('ТП: подпись «Термо-ЭДС E(t), мВ»',
              st3['valLabelText'] == 'Термо-ЭДС E(t), мВ',
              st3['valLabelText'])
        page.fill('#tempQueryTemp', '300')
        page.wait_for_timeout(400)
        st4 = page.evaluate(PANEL_JS)
        check('живой расчёт ТП: t=300 → E(t)',
              st4['vValue'] not in (None, '') and
              float(st4['vValue'].replace(',', '.')) > 10,
              (st4['tValue'], st4['vValue']))
        shot(page, 'b-mobile-dark-tc.png')
        ctx.close()

        print('== БРАУЗЕР: светлая тема ==')
        ctx = browser.new_context(
            viewport={'width': 375, 'height': 720},
            is_mobile=True, has_touch=True, locale='ru-RU')
        setup_routes(ctx)
        ctx.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t494-b');" +
            "localStorage.setItem('app-theme','light');")
        page = ctx.new_page()
        page.on('dialog', lambda d: d.accept())
        page.on('pageerror', lambda e: errors.append('l: ' + str(e)))
        page.goto('http://127.0.0.1:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'cu50_1428')
        st5 = page.evaluate(PANEL_JS)
        check('светлая: заголовка/подсказки НЕТ, поля тёмные/крупные',
              not st5['titleText'] and not st5['hintText'] and
              st5['tColor'] == 'rgb(20, 20, 19)' and
              st5['tFont'] == '19px', (st5['tColor'], st5['tFont']))
        shot(page, 'c-mobile-light-rtd.png')
        ctx.close()

        print('== БРАУЗЕР: десктоп 1280 ==')
        ctx2 = browser.new_context(viewport={'width': 1280, 'height': 800},
                                   locale='ru-RU')
        setup_routes(ctx2)
        ctx2.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t494-c');" +
            "localStorage.setItem('app-theme','dark');")
        page = ctx2.new_page()
        page.on('dialog', lambda d: d.accept())
        page.on('pageerror', lambda e: errors.append('d: ' + str(e)))
        page.goto('http://127.0.0.1:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'cu100_1426')
        st6 = page.evaluate(PANEL_JS)
        check('десктоп: панель стилизована (2px/градиент/тень/19px)',
              st6['borderWidth'] == '2px' and
              'linear-gradient' in st6['bgImage'] and
              'inset' in st6['boxShadow'] and st6['tFont'] == '19px',
              (st6['borderWidth'], st6['tFont']))
        check('десктоп: заголовка/подсказки НЕТ',
              not st6['titleText'] and not st6['hintText'])
        shot(page, 'd-desktop-dark-rtd.png')
        ctx2.close()
        browser.close()

        check('0 JS-ошибок во всех сессиях', not errors)
        if errors:
            for e in errors[:5]:
                print('  err: %s' % e[:200])

    print('\nИТОГ: %d passed, %d failed' % (PASS, FAIL))
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
