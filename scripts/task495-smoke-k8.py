#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 495 SMOKE kip8: проверка ПЕРЕНОСА (kipia-v518→v519) в БОЕВОЙ
# kip8. СТАТИКА ×7 (sw.js: v519 + комментарий 495 + v518 нет;
# index.html: «Тип датчика»/чип/подсказка шага отсутствуют ВЕЗДЕ,
# панель ts-calc-inset + 3 поля ts-calc-field + CSS углубления +
# мёртвые правила чипа сняты) + БРАУЗЕР (мобайл 375 тёмная: датчик
# 50М — чипа/текстов НЕТ, панель таблицы 1px/без градиента/тени
# только inset, ППР по-прежнему 2px/градиент/внешняя тень, поля
# 19px/52px, кнопка вне панели, «Рассчитать» строит таблицу; ТП
# tc_K; светлая; десктоп 1280; крупный план панели таблицы).
# Порт 9007; скриншоты в download/kip8-task495-smoke/.
import json
import os
import sys
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 9007
K8 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(K8), 'download', 'kip8-task495-smoke')
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
                      body='not found (smoke t495)')

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)


STATE_JS = r"""(() => {
    const t = document.getElementById('tempTableFormPanel');
    const p = document.getElementById('tempCustomCalcPanel');
    if (!t || !p) return {table: !!t, ppr: !!p};
    const tst = getComputedStyle(t);
    const pst = getComputedStyle(p);
    const inpCol = t.closest('.conv-col-input');
    const btn = inpCol ? inpCol.querySelector('.converter-convert-btn') : null;
    const fields = t.querySelectorAll('.ts-calc-field');
    const fs = fields.length ? getComputedStyle(fields[0]) : null;
    const mn = document.getElementById('temp_sensor_min');
    const mnst = mn ? getComputedStyle(mn) : null;
    return {
        table: true, ppr: true,
        chip: !!document.getElementById('tempSensorViewChip'),
        colText: inpCol ? inpCol.textContent : '',
        tBorderW: tst.borderWidth,
        tBgImage: tst.backgroundImage,
        tShadow: tst.boxShadow,
        pBorderW: pst.borderWidth,
        pBgImage: pst.backgroundImage,
        pShadow: pst.boxShadow,
        fieldsN: fields.length,
        fFont: fs ? fs.fontSize : null,
        fWeight: fs ? fs.fontWeight : null,
        fHeight: fields[0] ? Math.round(fields[0].getBoundingClientRect().height) : null,
        fColor: fs ? fs.color : null,
        mnFont: mnst ? mnst.fontSize : null,
        mnHeight: mn ? Math.round(mn.getBoundingClientRect().height) : null,
        stepVal: (document.getElementById('temp_sensor_step') || {}).value,
        btnOutside: btn ? !t.contains(btn) : null,
        btnText: btn ? btn.textContent.trim() : null,
        title: (document.getElementById('tempSensorViewTitle') || {}).textContent,
        resShown: (r => r ? r.style.display : null)(
            document.getElementById('tempSensorResults')),
        resLen: (r => r ? r.innerHTML.length : 0)(
            document.getElementById('tempSensorResults'))
    };
})()"""


def shadows_only_inset(shadow):
    if not shadow or shadow == 'none':
        return False
    parts = [s.strip() for s in shadow.split('),') if s.strip()]
    ok = True
    for i, part in enumerate(parts):
        pp = part + (')' if i < len(parts) - 1 else '')
        if 'inset' not in pp:
            ok = False
    return ok


def open_sensor(page, key):
    page.evaluate("openTempSensor('%s')" % key)
    page.wait_for_timeout(500)


def main():
    # ---------------- СТАТИКА ----------------
    print('== СТАТИКА ==')
    sw = open(os.path.join(K8, 'sw.js'), encoding='utf-8').read()
    idx = open(os.path.join(K8, 'index.html'), encoding='utf-8').read()
    check('sw.js: CACHE_VERSION = kipia-v519 (один инкремент)',
          "const CACHE_VERSION = 'kipia-v519';" in sw)
    check('sw.js: v518 отсутствует', 'kipia-v518' not in sw)
    check('sw.js: комментарий Task 495',
          'Task 495' in sw and 'УГЛУБЛЕНИЯ' in sw)
    check('index.html: «Тип датчика»/чип/подсказка шага удалены ВЕЗДЕ',
          'Тип датчика' not in idx and
          'tempSensorViewChip' not in idx and
          'Шаг расчёта таблицы в градусах Цельсия' not in idx and
          '.ts-view-chip' not in idx)
    check('index.html: панель ts-calc-inset + поля (2 ППР + 3 таблицы)',
          'class="ts-calc-panel ts-calc-inset" id="tempTableFormPanel"' in idx and
          idx.count('class="scale-field ts-calc-field"') == 5)
    check('index.html: CSS углубления (рамка 1px, без градиента, inset)',
          'border: 1px solid rgba(74, 143, 199, 0.32)' in idx and
          '.ts-calc-panel.ts-calc-inset { background-color: rgba(13, 17, 23, 0.55);'
          ' background-image: none;' in idx and
          'inset 0 3px 10px rgba(0, 0, 0, 0.5)' in idx)
    check('index.html: светлая версия углубления',
          '[data-theme="light"] .ts-calc-panel.ts-calc-inset {' in idx and
          'inset 0 2px 8px rgba(21, 54, 83, 0.18)' in idx)

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
            "localStorage.setItem('kip8_session_token','smoke-t495-a');" +
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
        st = page.evaluate(STATE_JS)
        check('чипа/текстов НЕТ (Тип датчика / шаг)',
              st['chip'] is False and
              'Тип датчика' not in st['colText'] and
              'Шаг расчёта таблицы в градусах Цельсия' not in st['colText'],
              st['colText'][:160])
        check('панель таблицы: 1px / без градиента / тени только inset',
              st['tBorderW'] == '1px' and st['tBgImage'] == 'none' and
              shadows_only_inset(st['tShadow']) and 'inset' in st['tShadow'],
              (st['tBorderW'], st['tBgImage'], st['tShadow'][:80]))
        check('ППР не изменился: 2px / градиент / внешняя тень',
              st['pBorderW'] == '2px' and
              'linear-gradient' in st['pBgImage'] and
              'rgb' in st['pShadow'].split('inset')[0],
              (st['pBorderW'], st['pBgImage'][:40]))
        check('поля: 3 шт 19px/52px/700/белый (min/max/шаг)',
              st['fieldsN'] == 3 and st['fFont'] == '19px' and
              st['fHeight'] == 52 and str(st['fWeight']) == '700' and
              st['fColor'] == 'rgb(255, 255, 255)' and
              st['mnHeight'] == 52,
              (st['fieldsN'], st['fFont'], st['fHeight'], st['mnHeight']))
        check('кнопка «Рассчитать» вне панели; заголовок с типом',
              st['btnOutside'] is True and
              'термометр сопротивления' in str(st['title']),
              (st['btnOutside'], st['title']))
        check('дефолты 0/100/10',
              st['stepVal'] == '10', st['stepVal'])
        page.click('#page-temp-sensor-view .conv-col-input '
                   '.converter-convert-btn')
        page.wait_for_timeout(700)
        st2 = page.evaluate(STATE_JS)
        check('«Рассчитать» — таблица построена',
              st2['resShown'] == 'block' and st2['resLen'] > 500,
              (st2['resShown'], st2['resLen']))
        shot(page, 'a-mobile-dark-rtd.png')
        page.evaluate(
            "document.getElementById('tempTableFormPanel')"
            ".scrollIntoView({block:'center'})")
        page.wait_for_timeout(400)
        shot(page, 'e-mobile-dark-table-panel.png')

        open_sensor(page, 'tc_K')
        st3 = page.evaluate(STATE_JS)
        check('ТП: та же геометрия + заголовок «термопара»',
              st3['tBorderW'] == '1px' and st3['tBgImage'] == 'none' and
              shadows_only_inset(st3['tShadow']) and
              'термопара' in str(st3['title']),
              (st3['tBorderW'], st3['title']))
        shot(page, 'b-mobile-dark-tc.png')
        ctx.close()

        print('== БРАУЗЕР: светлая тема ==')
        ctx = browser.new_context(
            viewport={'width': 375, 'height': 720},
            is_mobile=True, has_touch=True, locale='ru-RU')
        setup_routes(ctx)
        ctx.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t495-b');" +
            "localStorage.setItem('app-theme','light');")
        page = ctx.new_page()
        page.on('dialog', lambda d: d.accept())
        page.on('pageerror', lambda e: errors.append('l: ' + str(e)))
        page.goto('http://127.0.0.1:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'cu50_1428')
        st4 = page.evaluate(STATE_JS)
        check('светлая: углубление (1px/тени inset/без градиента)',
              st4['tBorderW'] == '1px' and
              shadows_only_inset(st4['tShadow']) and
              st4['tBgImage'] == 'none',
              (st4['tBorderW'], st4['tShadow'][:60]))
        check('светлая: чипа/текстов НЕТ',
              st4['chip'] is False and 'Тип датчика' not in st4['colText'])
        shot(page, 'c-mobile-light-rtd.png')
        ctx.close()

        print('== БРАУЗЕР: десктоп 1280 ==')
        ctx2 = browser.new_context(viewport={'width': 1280, 'height': 800},
                                   locale='ru-RU')
        setup_routes(ctx2)
        ctx2.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t495-c');" +
            "localStorage.setItem('app-theme','dark');")
        page = ctx2.new_page()
        page.on('dialog', lambda d: d.accept())
        page.on('pageerror', lambda e: errors.append('d: ' + str(e)))
        page.goto('http://127.0.0.1:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        open_sensor(page, 'cu100_1426')
        st5 = page.evaluate(STATE_JS)
        check('десктоп: панель стилизована (1px/inset/19px/52px)',
              st5['tBorderW'] == '1px' and
              shadows_only_inset(st5['tShadow']) and
              st5['fFont'] == '19px' and st5['fHeight'] == 52,
              (st5['tBorderW'], st5['fFont']))
        check('десктоп: ППР по-прежнему выступ (2px)',
              st5['pBorderW'] == '2px', st5['pBorderW'])
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
