#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 551 browser-check: настройки пользователя переживают
# очистку данных браузера — серверная синхронизация
# (KipSettingsSync + UserSettingsArchive). Заявка:
#   «На андроид приложение хранит всю информацию в браузере chrome?
#    если очистить данные браузера, то приложение "обнуляется".
#    Как обойти этот момент?»
# Сценарий (полная симуляция заявки):
#  A) «очистка данных браузера»: localStorage пуст (токен/кэш роли/
#     настройки удалены init-script'ом) → экран входа активен,
#     app-theme отсутствует, тема не тёмная;
#     НО локальная правка ДО входа (app-theme=light поверх
#     серверного dark) не перетирается (сервер не выигрывает);
#  B) вход по OTP (мок sendOTP/verifyOTP): токен в LS,
#     KipSettingsSync._restored=true, userSettings.get вызван;
#  C) настройки восстановлены с сервера: вид табеля shift,
#     крест 1, LCD-настройки, закреплённые, избранное приборов;
#     app-theme остался light (локальная правка — приоритет),
#     data-theme=light;
#  D) toggleTheme() → debounce 3 с → userSettings.save вызван с
#     app-theme=dark (тёмная тема ушла на сервер);
#  E) 0 JS-ошибок; скриншоты (вход, дашборд после входа).
import json
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8999
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(REPO), 'download', 'kip8-task551')
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
          (('  [' + str(extra)[:240] + ']') if (extra and not ok) else ''))


def shot(page, name):
    try:
        page.screenshot(path=os.path.join(SHOT_DIR, name))
    except Exception as e:
        print('  (скриншот %s не сохранён: %s)' % (name, e))


# Серверные настройки пользователя (лист «Настройки», email из
# сессии): тёмная тема, сменный вид табеля, крест включён,
# LCD-информер, закреплённые, избранное приборов, реестр авто-«д»/«н»
SERVER_SETTINGS = {
    'app-theme': 'dark',
    'kip8_ws_view_v1': 'shift',
    'kip8_ws_cross_v1': '1',
    'kip8_ws_lcd_set_v1': '{"weather":true,"feedInt":60,"feedMs":8,"wthrMin":30}',
    'buoy_calib_method': 'without_buoy',
    'pinnedSubsections': '["dashboard"]',
    'kip8_device_fav_v1': '{"123":1}',
    'kip8_device_fav_notes_v1': '{"123":{"text":"резерв"}}',
    'ws_auto_dn_keys': '{"2026-11":{"023|12":1}}',
    'kip8_whats_new_read_v3.0.0': '1',
}

CALLS = []


def mock_response(action, body):
    CALLS.append(action)
    if action == 'sendOTP':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'verifyOTP':
        return {'ok': True, 'data': {'token': 'bc-t551k', 'userId': 1,
                                     'email': 'user@test.local',
                                     'role': 'КИП8 pro'}}
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local',
                                     'role': 'КИП8 pro'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'КИП8 pro', 'found': True,
                'permissions': {'workschedule.view': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'userSettings.get':
        return {'ok': True, 'data': {'srvVer': '551',
                                     'settings': SERVER_SETTINGS}}
    if action == 'userSettings.save':
        return {'ok': True, 'data': {'saved': True, 'keys': 99}}
    return {'ok': True, 'data': {'ok': True}}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def ls_get(page, key):
    return page.evaluate("((k)=>{try{return localStorage.getItem(k)}" +
                         "catch(e){return null}})(%s)" % json.dumps(key))


def main():
    os.chdir(REPO)
    server = HTTPServer(('127.0.0.1', PORT), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda dg: dg.accept())

        # ===== «Очистка данных браузера»: ключей нет вовсе =====
        # (плюс локальная правка темы ДО входа — light: сервер
        # предложит dark, но локальное значение должно победить)
        ctx.add_init_script(
            "try{localStorage.clear()}catch(e){};" +
            "try{localStorage.setItem('app-theme','light')}catch(e){};")

        def handle(route, request):
            action = ''
            if 'action=' in request.url:
                action = unquote(request.url.split('action=')[1].split('&')[0])
            body = {}
            if request.post_data:
                try:
                    body = json.loads(request.post_data)
                except Exception:
                    body = {}
            return route.fulfill(status=200,
                content_type='application/json; charset=utf-8',
                body=json.dumps(mock_response(action, body), ensure_ascii=False))

        ctx.route('**/exec?**', handle)
        ctx.route('**script.google.com/**', handle)
        ctx.route('**raw.githubusercontent.com/**', lambda r: r.fulfill(
            status=404, content_type='text/plain', body='nf'))
        ctx.route('**calendar.legalic.ru/**', lambda r: r.fulfill(
            status=404, content_type='text/plain', body='nf'))
        ctx.route('**isdayoff.ru**', lambda r: r.fulfill(
            status=404, content_type='text/plain', body='nf'))

        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(1800)

        # ===== A: «данные браузера очищены» =====
        print('== A: после очистки данных браузера ==')
        check('A: токена нет (localStorage чист)',
              ls_get(page, 'kip8_session_token') is None,
              ls_get(page, 'kip8_session_token'))
        check('A: кэша роли нет', ls_get(page, 'kip8_cached_role') is None)
        check('A: гостевой режим (кнопка «Войти в аккаунт»)',
              page.evaluate("!!document.getElementById('guestLoginBtn')"))
        check('A: локальная тема light (правка до входа)',
              ls_get(page, 'app-theme') == 'light', ls_get(page, 'app-theme'))

        # ===== B: вход по OTP =====
        print('== B: вход по OTP (мок) ==')
        # сайдбар может быть вне вьюпорта — программный клик
        page.evaluate(
            "document.getElementById('guestLoginBtn').click()")
        page.wait_for_timeout(600)
        page.wait_for_selector('#authEmail', state='visible',
                               timeout=10000)
        shot(page, '01-login-screen.png')
        page.fill('#authEmail', 'user@test.local')
        page.click('#authSendBtn')
        page.wait_for_timeout(700)
        for i, d in enumerate('123456'):
            page.fill('#otp%d' % (i + 1), d)
        page.click('#authVerifyBtn')
        page.wait_for_timeout(2800)
        check('B: токен сессии сохранён',
              ls_get(page, 'kip8_session_token') == 'bc-t551k',
              ls_get(page, 'kip8_session_token'))
        check('B: KipSettingsSync._restored = true',
              page.evaluate("typeof KipSettingsSync!=='undefined' && " +
                            "KipSettingsSync._restored") is True)
        nget = CALLS.count('userSettings.get')
        check('B: userSettings.get вызван после входа', nget >= 1, nget)
        shot(page, '02-dashboard-after-login.png')

        # ===== C: настройки восстановлены с сервера =====
        print('== C: восстановление настроек ==')
        check('C: вид табеля shift', ls_get(page, 'kip8_ws_view_v1') == 'shift',
              ls_get(page, 'kip8_ws_view_v1'))
        check('C: перекрёстная подсветка 1',
              ls_get(page, 'kip8_ws_cross_v1') == '1',
              ls_get(page, 'kip8_ws_cross_v1'))
        check('C: LCD-информер (JSON)',
              'weather' in (ls_get(page, 'kip8_ws_lcd_set_v1') or ''),
              ls_get(page, 'kip8_ws_lcd_set_v1'))
        check('C: закреплённые подразделы',
              (ls_get(page, 'pinnedSubsections') or '') == '["dashboard"]',
              ls_get(page, 'pinnedSubsections'))
        check('C: избранное приборов',
              (ls_get(page, 'kip8_device_fav_v1') or '') == '{"123":1}',
              ls_get(page, 'kip8_device_fav_v1'))
        check('C: заметки приборов',
              'резерв' in (ls_get(page, 'kip8_device_fav_notes_v1') or ''),
              ls_get(page, 'kip8_device_fav_notes_v1'))
        check('C: реестр авто-«д»/«н»',
              '2026-11' in (ls_get(page, 'ws_auto_dn_keys') or ''),
              ls_get(page, 'ws_auto_dn_keys'))
        check('C: «что нового» прочитано',
              ls_get(page, 'kip8_whats_new_read_v3.0.0') == '1')
        # локальная правка ДО входа не перетерта сервером:
        check('C: локальная тема light НЕ перетёрта (сервер предлагал dark)',
              ls_get(page, 'app-theme') == 'light', ls_get(page, 'app-theme'))
        check('C: data-theme=light (локальная победила)',
              page.evaluate("document.documentElement.getAttribute(" +
                            "'data-theme')") == 'light')

        # ===== D: изменение настройки → сохранение на сервер =====
        print('== D: toggleTheme → userSettings.save (debounce 3 с) ==')
        saves_before = CALLS.count('userSettings.save')
        page.evaluate("typeof toggleTheme === 'function' && toggleTheme()")
        page.wait_for_timeout(3600)
        saves_after = CALLS.count('userSettings.save')
        check('D: userSettings.save вызван после смены темы',
              saves_after == saves_before + 1,
              '%d → %d' % (saves_before, saves_after))
        check('D: тема в LS теперь dark', ls_get(page, 'app-theme') == 'dark')
        check('D: data-theme=dark применён живьём',
              page.evaluate("document.documentElement.getAttribute(" +
                            "'data-theme')") == 'dark')
        shot(page, '03-dashboard-dark-theme.png')

        # ===== E: 0 JS-ошибок =====
        print('== E: JS-ошибки ==')
        check('E: 0 JS-ошибок', len(js_errors) == 0, js_errors[:5])

        browser.close()
        server.shutdown()

    print('\nИтог: %d OK, %d FAIL' % (PASS, FAIL))
    if FAIL:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
