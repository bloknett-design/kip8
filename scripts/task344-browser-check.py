# -*- coding: utf-8 -*-
# Task 344: browser-check — изоляция входа kip8 ↔ kip8test.
#
# Заявка пользователя (2026-09-08): «установил два приложения kip8 и
# kip8test на один телефон, захожу в аккаунт в kip8, открываю
# kip8test — оно тоже вошло в тот же аккаунт».
#
# Воспроизведение продакшен-раскладки GitHub Pages: ЛОКАЛЬНЫЙ сервер
# ОДНОГО origin (127.0.0.1) с двумя путями:
#     /kip8/     -> репозиторий kip8     (исправленный ПРОД)
#     /kip8test/ -> репозиторий kip8test (тест, обёртка на месте)
# localStorage у одного origin ОБЩИЙ — как на bloknett-design.github.io.
#
# Проверки:
#   • Сценарий пользователя (контекст 1 = «профиль телефона»):
#     A1 kip8: пустое хранилище → гостевой режим «Общий доступ»;
#     A2 kip8: вход (raw-ключи kip8_session_token/kip8_cached_role,
#        как их пишет исправленный kip8) → приложение открыто;
#     A3 kip8: в хранилище РОВНО 'kip8_session_token', НИ ОДНОГО
#        ключа с префиксом 'kip8test:' (сердце бага — раньше kip8
#        писал 'kip8test:kip8_session_token');
#     A4 kip8test (тот же профиль/origin): НЕ видит вход kip8 —
#        гостевой режим, токен пуст; при этом raw-ключ kip8 в общем
#        хранилище ЕСТЬ (shared origin доказан) — это и есть фикс;
#     A5 kip8test: собственная обёртка на месте (патч префиксует
#        его собственные записи — 'kip8test:*');
#     A6 0 JS-ошибок в обоих приложениях.
#   • Обратный сценарий (контекст 2): вход в kip8test (prefixed-ключи)
#     → kip8 в том же профиле остаётся ГОСТЕМ.
#   • Контекст 3 (свежий профиль): kip8 загружается, гостевой режим,
#     приложение живо (страницы рендерятся).
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8964
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_KIP8 = os.path.dirname(HERE)                    # .../kip8
REPO_KIP8TEST = os.path.join(os.path.dirname(REPO_KIP8), 'kip8test')

if not os.path.isdir(REPO_KIP8TEST):
    raise SystemExit('не найден клон kip8test рядом с kip8: ' + REPO_KIP8TEST)

MIME = {
    '.html': 'text/html; charset=utf-8', '.js': 'application/javascript',
    '.json': 'application/json', '.css': 'text/css', '.png': 'image/png',
    '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
    '.webmanifest': 'application/manifest+json', '.txt': 'text/plain'
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        path = unquote(self.path.split('?')[0])
        if path.startswith('/kip8test/'):
            root, rel = REPO_KIP8TEST, path[len('/kip8test'):]
        else:
            root, rel = REPO_KIP8, path[len('/kip8'):] if path.startswith('/kip8/') else path
        if rel in ('', '/'):
            rel = '/index.html'
        fp = os.path.normpath(os.path.join(root, rel.lstrip('/')))
        if not fp.startswith(root) or not os.path.isfile(fp):
            self.send_response(404)
            self.end_headers()
            return
        ext = os.path.splitext(fp)[1].lower()
        with open(fp, 'rb') as f:
            body = f.read()
        self.send_response(200)
        self.send_header('Content-Type', MIME.get(ext, 'application/octet-stream'))
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)


server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
print('сервер http://127.0.0.1:%d  (/kip8/ -> kip8, /kip8test/ -> kip8test)' % PORT)

# Моки Apps Script (по образцу task343-browser-check.py)
ROLE = {'role': 'КИП ИОС'}


def mock_response(action, body):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local',
                                     'role': ROLE['role']}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': ROLE['role'], 'found': True,
                'permissions': {'workschedule.view': True,
                                'workschedule.view.min': False,
                                'workschedule.edit': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    return {'ok': True, 'data': {'ok': True}}


PASS = 0
FAIL = 0


def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(('  ✓ ' if ok else '  ✗ ') + name +
          (('  [' + str(extra) + ']') if (extra and not ok) else ''))


def new_page(ctx, js_errors):
    page = ctx.new_page()
    page.on('pageerror', lambda e: js_errors.append(str(e)))
    return page


def route_mocks(ctx):
    def handle(route, request):
        url = request.url
        action = ''
        if 'action=' in url:
            action = unquote(url.split('action=')[1].split('&')[0])
        pd = request.post_data
        body = None
        if pd:
            try:
                body = json.loads(pd)
            except Exception:
                body = None
        route.fulfill(status=200, content_type='application/json; charset=utf-8',
                      body=json.dumps(mock_response(action, body),
                                      ensure_ascii=False).encode('utf-8'))
    ctx.route('**/exec?**', handle)
    ctx.route('**script.google.com/**', handle)

    def block_external(route):
        route.fulfill(status=404, content_type='text/plain',
                      body='not found (browser-check t344)')
    ctx.route('**raw.githubusercontent.com/**', block_external)
    ctx.route('**calendar.legalic.ru/**', block_external)


URL_KIP8 = 'http://127.0.0.1:%d/kip8/index.html' % PORT
URL_KIP8TEST = 'http://127.0.0.1:%d/kip8test/index.html' % PORT

with sync_playwright() as p:
    browser = p.chromium.launch()

    # ========= Контекст 1: сценарий пользователя =========
    print('=== Контекст 1: «вход в kip8 → kip8test не должен войти» (общий профиль) ===')
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
    route_mocks(ctx)
    errs_kip8, errs_test = [], []

    pageA = new_page(ctx, errs_kip8)
    pageA.goto(URL_KIP8, wait_until='domcontentloaded')
    pageA.wait_for_timeout(2500)
    check('A1: kip8 при пустом хранилище — гостевой режим',
          pageA.evaluate('KipAuth._cachedRole') == 'Общий доступ',
          pageA.evaluate('KipAuth._cachedRole'))

    # «Вход» в kip8: исправленный kip8 пишет RAW-ключи (без префикса)
    pageA.evaluate("localStorage.setItem('kip8_session_token','t344-a')")
    pageA.evaluate("localStorage.setItem('kip8_cached_role','КИП ИОС')")
    pageA.evaluate("localStorage.setItem('kip8_cached_email','user@test.local')")
    pageA.evaluate("localStorage.setItem('kip8_cached_user_id','1')")
    pageA.reload()
    pageA.wait_for_timeout(2500)

    check('A2: kip8 вошёл: токен и роль из raw-ключей',
          pageA.evaluate('KipAuth.getToken()') == 't344-a' and
          pageA.evaluate('KipAuth._cachedRole') == 'КИП ИОС',
          (pageA.evaluate('KipAuth.getToken()'),
           pageA.evaluate('KipAuth._cachedRole')))

    keys = pageA.evaluate('Object.keys(localStorage)')
    check('A3a: raw-ключ kip8_session_token записан (без префикса)',
          'kip8_session_token' in keys, keys)
    check('A3b: НИ ОДНОГО ключа с префиксом "kip8test:" (сердце бага Task 344)',
          not [k for k in keys if k.startswith('kip8test:')], [k for k in keys if k.startswith('kip8test:')])

    # Открываем kip8test В ТОМ ЖЕ профиле (тот же origin = общее хранилище)
    pageB = new_page(ctx, errs_test)
    pageB.goto(URL_KIP8TEST, wait_until='domcontentloaded')
    pageB.wait_for_timeout(2500)
    check('A4a: kip8test НЕ видит вход kip8 — токен пуст',
          pageB.evaluate('KipAuth.getToken()') == '',
          pageB.evaluate('KipAuth.getToken()'))
    check('A4b: kip8test — гостевой режим «Общий доступ»',
          pageB.evaluate('KipAuth._cachedRole') == 'Общий доступ',
          pageB.evaluate('KipAuth._cachedRole'))
    check('A4c: raw-ключ kip8 ЕСТЬ в общем хранилище (origin общий — доказано)',
          pageB.evaluate(
              "Storage.prototype.getItem.call(localStorage, 'kip8_session_token')"
          ) == 't344-a',
          'shared storage ok')
    check('A4d: патч kip8test НЕ отдаёт токен kip8 (изолированное чтение)',
          pageB.evaluate("localStorage.getItem('kip8_session_token')") is None)

    # Обёртка kip8test жива: собственная запись префиксуется
    pageB.evaluate("localStorage.setItem('kip8_session_token','unused')")
    raw_after = pageB.evaluate(
        "Storage.prototype.getItem.call(localStorage, 'kip8test:kip8_session_token')")
    check('A5: kip8test пишет СВОЙ ключ kip8test:kip8_session_token (обёртка на месте)',
          raw_after == 'unused', raw_after)
    pageB.evaluate("localStorage.removeItem('kip8_session_token')")

    check('A6: 0 JS-ошибок kip8', len(errs_kip8) == 0, errs_kip8[:3])
    check('A6: 0 JS-ошибок kip8test', len(errs_test) == 0, errs_test[:3])
    ctx.close()

    # ========= Контекст 2: обратный сценарий =========
    print('=== Контекст 2: «вход в kip8test → kip8 не должен войти» ===')
    ctx2 = browser.new_context(viewport={'width': 1280, 'height': 800})
    route_mocks(ctx2)
    errs = []

    pageB2 = new_page(ctx2, errs)
    pageB2.goto(URL_KIP8TEST, wait_until='domcontentloaded')
    pageB2.wait_for_timeout(2000)
    # «Вход» в kip8test: его патч сам кладёт prefixed-ключи
    pageB2.evaluate("localStorage.setItem('kip8_session_token','t344-b')")
    pageB2.evaluate("localStorage.setItem('kip8_cached_role','КИП ИОС')")
    pageB2.reload()
    pageB2.wait_for_timeout(2500)
    check('B1: kip8test вошёл своим ключом (prefixed)',
          pageB2.evaluate('KipAuth.getToken()') == 't344-b' and
          pageB2.evaluate('KipAuth._cachedRole') == 'КИП ИОС',
          (pageB2.evaluate('KipAuth.getToken()'),
           pageB2.evaluate('KipAuth._cachedRole')))

    pageA2 = new_page(ctx2, errs)
    pageA2.goto(URL_KIP8, wait_until='domcontentloaded')
    pageA2.wait_for_timeout(2500)
    check('B2a: kip8 в том же профиле — токен пуст (не видит вход kip8test)',
          pageA2.evaluate('KipAuth.getToken()') == '',
          pageA2.evaluate('KipAuth.getToken()'))
    check('B2b: kip8 — гостевой режим',
          pageA2.evaluate('KipAuth._cachedRole') == 'Общий доступ',
          pageA2.evaluate('KipAuth._cachedRole'))
    check('B3: 0 JS-ошибок', len(errs) == 0, errs[:3])
    ctx2.close()

    # ========= Контекст 3: свежий профиль, kip8 жив =========
    print('=== Контекст 3: свежий профиль — kip8 загружается и работает ===')
    ctx3 = browser.new_context(viewport={'width': 390, 'height': 844},
                               device_scale_factor=2)
    route_mocks(ctx3)
    errs3 = []
    pageC = new_page(ctx3, errs3)
    pageC.goto(URL_KIP8, wait_until='domcontentloaded')
    pageC.wait_for_timeout(2500)
    check('C1: kip8 рендерится (страница dashboard в DOM)',
          pageC.evaluate("!!document.getElementById('page-dashboard')"))
    check('C2: гостевой режим «Общий доступ»',
          pageC.evaluate('KipAuth._cachedRole') == 'Общий доступ',
          pageC.evaluate('KipAuth._cachedRole'))
    check('C3: 0 JS-ошибок (мобайл)', len(errs3) == 0, errs3[:3])
    ctx3.close()

    browser.close()

server.shutdown()
print('\nИтог Task 344 browser-check: %d passed / %d failed' % (PASS, FAIL))
exit(0 if FAIL == 0 else 1)
