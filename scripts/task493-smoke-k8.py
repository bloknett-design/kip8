#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 493 SMOKE kip8: проверка переноса (kipia-v516→v517) в БОЕВОЙ
# kip8. СТАТИКА ×6 (sw.js: версия v517 + комментарий 493 + v516 нет;
# index.html: кнопка «Табель учёта» + реестр + заголовок полный) +
# БРАУЗЕР (мобайл 375 тёмная: пин без префикса — де-изоляция, кнопка
# на главной «Табель учёта», клик → страница с ПОЛНЫМ заголовком;
# docs-ios кнопка; десктоп 1280).
# Порт 9007; скриншоты в download/kip8-task493-smoke/.
import json
import os
import re
import sys
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 9007
K8 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(K8), 'download', 'kip8-task493-smoke')
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
                      body='not found (smoke t493)')

    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)


PIN_BTN_JS = r"""(() => {
    const items = [...document.querySelectorAll('#pinnedItemsContainer .pinned-item')];
    const out = {count: items.length, items: []};
    items.forEach(el => {
        const label = el.querySelector('.menu-btn-label');
        const st = getComputedStyle(el);
        out.items.push({
            key: el.getAttribute('data-pinned-key'),
            label: label ? label.textContent.trim() : null,
            borderColor: st.borderColor,
            visible: st.display !== 'none' &&
                     el.getBoundingClientRect().width > 0
        });
    });
    return out;
})()"""

STATIC_JS = r"""(() => {
    const btn = document.getElementById('workScheduleMenuBtn');
    const out = {};
    if (btn) {
        const label = btn.querySelector('.menu-btn-label');
        out.btnLabel = label ? label.textContent.trim() : null;
    } else { out.btnLabel = 'NO-BTN'; }
    const hdr = document.querySelector('#page-work-schedule .page-inline-header-title');
    out.pageHeader = hdr ? hdr.textContent.trim() : null;
    out.activePage = (document.querySelector('.page-content.active') || {}).id || null;
    return out;
})()"""


def main():
    # ---------------- СТАТИКА ----------------
    print('== СТАТИКА ==')
    sw = open(os.path.join(K8, 'sw.js'), encoding='utf-8').read()
    idx = open(os.path.join(K8, 'index.html'), encoding='utf-8').read()
    check('sw.js: CACHE_VERSION = kipia-v517 (один инкремент)',
          "const CACHE_VERSION = 'kipia-v517';" in sw)
    check('sw.js: v516 отсутствует', 'kipia-v516' not in sw)
    check('sw.js: комментарий Task 493',
          re.search(r'Task 493[^\n]*\n[^\n]*Табель', sw) is not None)
    check('index.html: кнопка — «Табель учёта»',
          '<div class="menu-btn-label">Табель учёта</div>' in idx)
    check('index.html: реестр — label: \'Табель учёта\'',
          re.search(r"'work-schedule':\s*\{ label: 'Табель учёта',", idx)
          is not None)
    check('index.html: заголовок страницы — полное имя (не тронут)',
          '<div class="page-inline-header-title">'
          'Табель учёта рабочего времени</div>' in idx)

    # ---------------- БРАУЗЕР ----------------
    with sync_playwright() as p:
        browser = p.chromium.launch()
        errors = []

        print('== БРАУЗЕР: мобайл 375 тёмная, пин БЕЗ префикса ==')
        ctx = browser.new_context(
            viewport={'width': 375, 'height': 720},
            is_mobile=True, has_touch=True,
            color_scheme='dark', locale='ru-RU')
        setup_routes(ctx)
        # Де-изоляция: kip8 БЕЗ префикса kip8test:
        ctx.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t493-a');" +
            "localStorage.setItem('app-theme','dark');" +
            "localStorage.setItem('pinnedSubsections', "
            "JSON.stringify(['work-schedule']));")
        page = ctx.new_page()
        page.on('dialog', lambda d: d.accept())
        page.on('pageerror', lambda e: errors.append('m: ' + str(e)))
        page.goto('http://127.0.0.1:%d/index.html' % PORT)
        page.wait_for_timeout(2500)

        pin = page.evaluate(PIN_BTN_JS)
        check('на главной ровно ОДНА закреплённая кнопка',
              pin['count'] == 1, pin)
        ws = next((i for i in pin['items']
                   if i['key'] == 'work-schedule'), None)
        check('кнопка work-schedule закреплена (ключ без префикса)',
              ws is not None)
        if ws:
            check('метка на главной — «Табель учёта»',
                  ws['label'] == 'Табель учёта', ws['label'])
            check('«рабочего времени» на главной НЕТ',
                  'рабочего времени' not in (ws['label'] or ''))
            check('кнопка видима', ws['visible'])
        shot(page, 'a-mobile-dashboard-pin.png')

        if ws:
            page.click('#pinnedItemsContainer .pinned-item')
            page.wait_for_timeout(900)
            st = page.evaluate(STATIC_JS)
            check('клик → открылась #page-work-schedule',
                  st['activePage'] == 'page-work-schedule', st['activePage'])
            check('заголовок страницы — ПОЛНОЕ имя',
                  st['pageHeader'] == 'Табель учёта рабочего времени',
                  st['pageHeader'])
            shot(page, 'b-mobile-work-schedule-page.png')

        page.evaluate("navigateTo('docs-ios')")
        page.wait_for_timeout(600)
        st = page.evaluate(STATIC_JS)
        check('кнопка на docs-ios — «Табель учёта»',
              st['btnLabel'] == 'Табель учёта', st['btnLabel'])
        shot(page, 'c-mobile-docs-ios-btn.png')
        ctx.close()

        print('== БРАУЗЕР: десктоп 1280 ==')
        ctx2 = browser.new_context(viewport={'width': 1280, 'height': 800},
                                   locale='ru-RU')
        setup_routes(ctx2)
        ctx2.add_init_script(
            "localStorage.setItem('kip8_session_token','smoke-t493-d');" +
            "localStorage.setItem('pinnedSubsections', "
            "JSON.stringify(['work-schedule']));")
        page2 = ctx2.new_page()
        page2.on('pageerror', lambda e: errors.append('d: ' + str(e)))
        page2.goto('http://127.0.0.1:%d/index.html' % PORT)
        page2.wait_for_timeout(2500)
        pin2 = page2.evaluate(PIN_BTN_JS)
        ws2 = next((i for i in pin2['items']
                    if i['key'] == 'work-schedule'), None)
        check('десктоп: кнопка закреплена', ws2 is not None)
        if ws2:
            check('десктоп: метка — «Табель учёта»',
                  ws2['label'] == 'Табель учёта', ws2['label'])
        shot(page2, 'd-desktop-dashboard-pin.png')
        ctx2.close()
        browser.close()

    print('== ИТОГ: %d OK, %d FAIL ==' % (PASS, FAIL))
    if errors:
        print('JS-ОШИБКИ (%d):' % len(errors))
        for e in errors[:10]:
            print('  ! ' + str(e)[:300])
    else:
        print('JS-ОШИБКИ: 0')
    return 0 if (FAIL == 0 and not errors) else 1


if __name__ == '__main__':
    sys.exit(main())
