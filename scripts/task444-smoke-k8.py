#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 444 SMOKE (kip8 после переноса): приложение kip8 грузится,
# карточка работника — блок СИЗ: имя ПРИГЛУШЕНО, даты/сроки ЯРКИЕ,
# «до …» — КРУПНЕЕ + ЗЕЛЁНАЯ (действует) / ОРАНЖЕВО-КРАСНАЯ
# (просрочена), «До износа» — без выделения, 0 JS-ошибок.
# Ключи kip8 — БЕЗ префикса kip8test:. Порт 8949, мок-сервер.
import datetime
import json
import os
from urllib.parse import unquote
from http.server import HTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8949
TODAY = datetime.date.today()
TODAY_ISO = '%04d-%02d-%02d' % (TODAY.year, TODAY.month, TODAY.day)

EMPLOYEES = [
  {'таб_номер': '0871', 'ФИО': 'Федосов А. В.', 'тип': 'сменный', 'смена': 1,
   'шаблон_ротации': 1, 'старт_цикла': TODAY_ISO,
   'дата_приёма': '2024-03-15', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА 5 разряд', 'группа_допуска': 'IV',
   'комментарий': ''},
]
CODES = [
  {'code': 'Д8', 'name': 'День 8-час', 'color': '#FFF9C4', 'short': 'день 8ч'},
  {'code': '', 'name': 'Выходной', 'color': '#EEF0F2', 'short': 'выходной'},
]
PATTERNS = [
  {'id': 1, 'name': 'Сменный сутки/двое', 'cycle': 4, 'description': '',
   'days': [{'day': 1, 'status': 'Д'}, {'day': 2, 'status': 'Н'},
            {'day': 3, 'status': ''}, {'day': 4, 'status': ''}]},
]
PPE = [
  {'id': 11, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд',
   'наименование': 'Фильтрующая коробка противогаза',
   'дата_выдачи': '2026-08-17', 'дата_изготовления': '2025-01-15',
   'срок_годности': '2 года', 'дата_окончания': '2027-01-15',
   'примечание': 'банка №2'},
  {'id': 12, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд', 'наименование': 'Каска защитная',
   'дата_выдачи': '2026-08-17', 'дата_изготовления': '',
   'срок_годности': '2 года', 'дата_окончания': '2028-08-17',
   'примечание': ''},
  {'id': 13, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд', 'наименование': 'Очки закрытые',
   'дата_выдачи': '', 'дата_изготовления': '',
   'срок_годности': 'До износа', 'дата_окончания': 'До износа',
   'примечание': ''},
  {'id': 14, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд', 'наименование': 'Перчатки резиновые',
   'дата_выдачи': '2023-06-01', 'дата_изготовления': '',
   'срок_годности': '1 год', 'дата_окончания': '2024-06-01',
   'примечание': 'просрочено'},
  {'id': 15, 'таб_номер': '0871', 'работник': 'Федосов А. В.',
   'должность': 'Слесарь КИПиА 5 разряд', 'наименование': 'Респиратор',
   'дата_выдачи': '2025-09-29', 'дата_изготовления': '',
   'срок_годности': '1 год', 'дата_окончания': TODAY_ISO,
   'примечание': ''},
]
PASS = 0
FAIL = 0
SHOTS = '/home/z/my-project/download/screenshots-task444'
os.makedirs(SHOTS, exist_ok=True)


def check(name, cond, extra=''):
    global PASS, FAIL
    ok = bool(cond)
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(('  + ' if ok else '  X ') + name +
          (('  [' + str(extra)[:220] + ']') if (extra and not ok) else ''))


def api_response(action, body):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'u@t.l',
                'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'workschedule.view': True,
                                'workschedule.edit': True}}}
    if action == 'workSchedule.listEmployees':
        return {'ok': True, 'data': {'employees': EMPLOYEES}}
    if action == 'workSchedule.getPatterns':
        return {'ok': True, 'data': {'patterns': PATTERNS}}
    if action == 'workSchedule.getStatusCodes':
        return {'ok': True, 'data': {'codes': CODES}}
    if action == 'workSchedule.listPpe':
        return {'ok': True, 'data': {'ppe': [dict(r) for r in PPE]}}
    return {'ok': True, 'data': {'ok': True}}


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        ctx.add_init_script(
            "try{localStorage.removeItem('kip8_ws_cache_v1')}catch(e){};" +
            "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
            "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
            "localStorage.setItem('kip8_session_token','bc-t444k8');" +
            "localStorage.setItem('app-theme','dark');")

        def handle(route, request):
            url = request.url
            action = ''
            if 'action=' in url:
                action = unquote(url.split('action=')[1].split('&')[0])
            pd_ = request.post_data
            body = {}
            if pd_:
                try:
                    body = json.loads(pd_)
                except Exception:
                    body = {}
            return route.fulfill(
                status=200, content_type='application/json; charset=utf-8',
                body=json.dumps(api_response(action, body),
                                ensure_ascii=False))
        ctx.route('**/exec?**', handle)
        ctx.route('**script.google.com/**', handle)
        ctx.route('**raw.githubusercontent.com/**',
                  lambda r: r.fulfill(status=404, body='x'))
        ctx.route('**calendar.legalic.ru/**',
                  lambda r: r.fulfill(status=404, body='x'))

        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('work-schedule')")
        page.wait_for_timeout(2500)
        check('S1: kip8 грузится, график открыт',
              page.evaluate("(function(){return !!document.querySelector(" +
              "'.ws-grid');})()"))
        page.click('#wsWorkersBtn')
        page.wait_for_timeout(1000)
        page.click('button[title="Федосов А. В."]')
        page.wait_for_timeout(900)
        c = page.evaluate("""(function(){
            var body = document.getElementById('wsWorkersBody');
            var items = body ? body.querySelectorAll('.ws-ppe-item') : [];
            function info(el) {
                if (!el) return null;
                var cs = getComputedStyle(el);
                return { color: cs.color, fs: cs.fontSize, fw: cs.fontWeight,
                         text: (el.textContent || '').slice(0, 90) };
            }
            var out = [];
            for (var i = 0; i < items.length; i++) {
                var it = items[i];
                out.push({ name: info(it.querySelector('.ws-ppe-name')),
                           meta: info(it.querySelector('.ws-ppe-meta')),
                           exp: info(it.querySelector('.ws-ppe-exp')) });
            }
            return { n: items.length,
                     sec: (body.textContent || '').indexOf(
                         'СИЗ · средства индивидуальной защиты') !== -1,
                     rows: out };
        })()""")
        check('S2: карточка kip8 — блок СИЗ, 5 записей',
              c['sec'] and c['n'] == 5, (c['sec'], c['n']))
        r1 = c['rows'][0]
        r4 = c['rows'][3]
        r3 = c['rows'][2]
        check('S3: имя ПРИГЛУШЕНО (rgba(255,255,255,0.55), вес 500)',
              r1['name']['color'] == 'rgba(255, 255, 255, 0.55)' and
              r1['name']['fw'] == '500',
              (r1['name']['color'], r1['name']['fw']))
        check('S4: мета дат/сроков ЯРКАЯ (rgb(224,224,224), 13px)',
              r1['meta']['color'] == 'rgb(224, 224, 224)' and
              r1['meta']['fs'] == '13px',
              (r1['meta']['color'], r1['meta']['fs']))
        check('S5: «до 15.01.2027» — ЗЕЛЁНАЯ, ~14.95px, вес 700',
              r1['exp'] is not None and
              r1['exp']['color'] == 'rgb(129, 199, 132)' and
              abs(float(r1['exp']['fs'].replace('px', '')) - 14.95) < 0.3 and
              r1['exp']['fw'] == '700', r1['exp'])
        check('S6: «до 01.06.2024» — ОРАНЖЕВО-КРАСНАЯ (просрочена)',
              r4['exp'] is not None and
              r4['exp']['color'] == 'rgb(255, 112, 67)', r4['exp'])
        check('S7: «До износа» — БЕЗ выделения, мета жива (регресс 392/443)',
              r3['exp'] is None and 'До износа' in r3['meta']['text'],
              r3['meta'])
        page.screenshot(path=SHOTS + '/05-kip8-card-ppe.png')
        check('S8: 0 JS-ошибок', js_errors == [], js_errors[:3])
        browser.close()

    print('\n===== SMOKE ИТОГ: %d OK / %d FAIL =====' % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    import threading
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    try:
        code = main()
    finally:
        server.shutdown()
    raise SystemExit(code)
