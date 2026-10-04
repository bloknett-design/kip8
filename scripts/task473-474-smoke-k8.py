#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 473-474: SMOKE переноса партии в kip8 (порт 8997, ключи
# localStorage БЕЗ префикса kip8test:) —
#   Task 474 «карточка прибора КИП ИОС»: текст Типа ×1.5 —
#     computed font-size 18px (было 12px) в тёмной/светлой темах и
#     на мобайле; «№ прибора»/«Место установки» смещены ниже от
#     верхней границы карточки (label1Shift ~12px, было ~2px);
#     структура карточки Task 334/335/336 жива; 0 JS-ошибок.
#   Task 473 «график ППР Приборы» (Electron UA — charts-desktop.js
#     грузится только в десктопе, Task 147): 35 значений над
#     столбцами + 1 «0»; столбцы зрительно различимы (высоты > 2px:
#     К-48 ~96%, П-15 ~30%, ТО-500 100%); правая ось 0–50; 0 JS.
#   SW: kipia-v509 (маркер один, v508 отсутствует).
import json
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8997
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(REPO), 'download',
                        'kip8-task473-474-transfer')
os.makedirs(SHOT_DIR, exist_ok=True)

ELECTRON_UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
               '(KHTML, like Gecko) kip8-desktop/1.0 Chrome/120.0.0.0 '
               'Safari/537.36 Electron/28.2.0')

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
          (('  [' + str(extra)[:220] + ']') if (extra and not ok) else ''))


def mock_response(action, body):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1,
                'email': 'user@test.local', 'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'calc.view': True, 'library.view': True,
                    'kipios.view': True, 'secret.view': True,
                    'whatsnew.view': True, 'charts.view': True,
                    'flowmeter.view': True, 'workschedule.view': True,
                    'workschedule.edit': True, 'admin.panel': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    return {'ok': True, 'data': {'ok': True}}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    os.chdir(REPO)
    server = HTTPServer(('127.0.0.1', PORT), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ============ Контекст 1: карточка прибора (Task 474) ============
        print('=== Task 474: карточка прибора (десктоп, светлая) ===')
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = ctx.new_page()
        js_errors = []
        page.on('pageerror', lambda e: js_errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())

        def handle(route, request):
            url = request.url
            action = ''
            if 'action=' in url:
                action = unquote(url.split('action=')[1].split('&')[0])
            route.fulfill(status=200,
                          content_type='application/json; charset=utf-8',
                          body=json.dumps(mock_response(action, None),
                                          ensure_ascii=False).encode('utf-8'))

        ctx.route('**/exec?**', handle)
        ctx.route('**script.google.com/**', handle)

        def block_external(route):
            route.fulfill(status=404, content_type='text/plain',
                          body='not found (smoke 473-474)')

        ctx.route('**raw.githubusercontent.com/**', block_external)
        ctx.route('**calendar.legalic.ru/**', block_external)
        # kip8: ключи БЕЗ префикса kip8test:
        ctx.add_init_script(
            "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
            "try{localStorage.removeItem('kip8_devices_cache')}catch(e){};" +
            "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
            "localStorage.setItem('kip8_session_token','sm-k473-474');" +
            "localStorage.setItem('app-theme','light');")

        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('kip-ios')")
        page.wait_for_timeout(1200)
        page.evaluate("devOpenDetail('1')")
        page.wait_for_timeout(800)
        m = page.evaluate("""(function(){
          var out = {};
          out.panel = document.getElementById('detailPanel')
              .classList.contains('active');
          var ov = document.querySelector('.dev-detail-type-overlay');
          out.ovText = ov ? ov.textContent.trim() : null;
          out.ovFont = ov ? getComputedStyle(ov).fontSize : null;
          var wrap = document.querySelector('.dev-detail-image-wrap');
          var wr = wrap.getBoundingClientRect();
          var or_ = ov.getBoundingClientRect();
          out.ovInWrap = or_.left >= wr.left - 1 && or_.right <= wr.right + 1
              && or_.bottom <= wr.bottom + 1;
          var top = document.querySelector('.dev-detail-top');
          var tr = top.getBoundingClientRect();
          var labels = document.querySelectorAll('.dev-detail-meta-label');
          out.labels = [];
          for (var i = 0; i < labels.length; i++)
            out.labels.push(labels[i].textContent.trim());
          out.shift1 = labels.length
              ? labels[0].getBoundingClientRect().top - tr.top : -99;
          var meta = document.querySelector('.dev-detail-meta');
          out.padTop = meta ? getComputedStyle(meta).paddingTop : null;
          return out;
        })()""")
        check('474-1: панель деталей открыта (kip8, светлая)', m['panel'])
        check('474-2: Тип прибора — «"Пульсар" ТХ»', m['ovText'] == '"Пульсар" ТХ',
              m['ovText'])
        check('474-3: computed font-size Типа = 18px (×1.5 от 12px)',
              m['ovFont'] == '18px', m['ovFont'])
        check('474-4: «№ прибора» ниже от верхней границы карточки (~12px)',
              10 <= m['shift1'] <= 15, m['shift1'])
        check('474-5: padding-top мета-блока = 12px', m['padTop'] == '12px',
              m['padTop'])
        check('474-6: подписи «№ прибора» + «Место установки»',
              m['labels'] == ['№ прибора', 'Место установки'], m['labels'])
        check('474-7: Тип в пределах картинки («перед картинкой»)',
              m['ovInWrap'], m)
        check('474-8: 0 JS-ошибок (карточка)', len(js_errors) == 0,
              js_errors[:3])
        page.screenshot(path=os.path.join(SHOT_DIR,
                                          '01-device-card-light.png'))
        print('  скриншот: 01-device-card-light.png')

        # мобильный 375 — карточка прибора
        ctxm = browser.new_context(viewport={'width': 375, 'height': 812})
        pagem = ctxm.new_page()
        js_errors_m = []
        pagem.on('pageerror', lambda e: js_errors_m.append(str(e)))
        pagem.on('dialog', lambda d: d.accept())
        ctxm.route('**/exec?**', handle)
        ctxm.route('**script.google.com/**', handle)
        ctxm.route('**raw.githubusercontent.com/**', block_external)
        ctxm.route('**calendar.legalic.ru/**', block_external)
        ctxm.add_init_script(
            "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
            "try{localStorage.removeItem('kip8_devices_cache')}catch(e){};" +
            "localStorage.setItem('kip8_session_token','sm-k473-474m');" +
            "localStorage.setItem('app-theme','dark');")
        pagem.goto('http://localhost:%d/index.html' % PORT)
        pagem.wait_for_timeout(2500)
        pagem.evaluate("navigateTo('kip-ios')")
        pagem.wait_for_timeout(1200)
        pagem.evaluate("devOpenDetail('1')")
        pagem.wait_for_timeout(800)
        mm = pagem.evaluate("""(function(){
          var out = {};
          var pg = document.getElementById('page-device-detail');
          out.page = !!pg && pg.classList.contains('active');
          var ov = document.querySelector('.dev-detail-type-overlay');
          out.font = ov ? getComputedStyle(ov).fontSize : null;
          var top = document.querySelector('.dev-detail-top');
          var tr = top.getBoundingClientRect();
          var l = document.querySelector('.dev-detail-meta-label');
          out.shift = l ? l.getBoundingClientRect().top - tr.top : -99;
          return out;
        })()""")
        check('474-9: мобильная страница device-detail открыта', mm['page'])
        check('474-10: мобайл — Тип 18px', mm['font'] == '18px', mm['font'])
        check('474-11: мобайл — смещение ~12px',
              10 <= mm['shift'] <= 15, mm['shift'])
        check('474-12: 0 JS-ошибок (мобайл)', len(js_errors_m) == 0,
              js_errors_m[:3])
        pagem.screenshot(path=os.path.join(SHOT_DIR,
                                           '02-device-card-mobile.png'))
        print('  скриншот: 02-device-card-mobile.png')
        ctx.close()
        ctxm.close()

        # ============ Контекст 2: график ППР (Task 473, Electron UA) =====
        print('=== Task 473: график ППР «Приборы» (Electron UA, тёмная) ===')
        ctxc = browser.new_context(viewport={'width': 1280, 'height': 900},
                                   user_agent=ELECTRON_UA)
        pagec = ctxc.new_page()
        js_errors_c = []
        pagec.on('pageerror', lambda e: js_errors_c.append(str(e)))
        pagec.on('dialog', lambda d: d.accept())
        ctxc.route('**/exec?**', handle)
        ctxc.route('**script.google.com/**', handle)
        ctxc.route('**raw.githubusercontent.com/**', block_external)
        ctxc.route('**calendar.legalic.ru/**', block_external)
        ctxc.add_init_script(
            "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
            "localStorage.setItem('kip8_session_token','sm-k473-474c');" +
            "localStorage.setItem('app-theme','dark');")
        pagec.goto('http://localhost:%d/index.html' % PORT)
        pagec.wait_for_timeout(2500)
        pagec.evaluate("navigateTo('charts')")
        pagec.wait_for_timeout(1200)
        c = pagec.evaluate("""(function(){
          var out = {};
          out.kipCharts = typeof KipCharts !== 'undefined';
          var t = document.querySelector('.ppr-chart-title');
          out.title = t ? t.textContent.trim() : '';
          out.vals = document.querySelectorAll('.ppr-bar-val').length;
          out.zeros = document.querySelectorAll('.ppr-bar-val-zero').length;
          out.rightLabels = [];
          var r = document.querySelectorAll('.ppr-y-axis-right .ppr-y-label');
          for (var i = 0; i < r.length; i++)
            out.rightLabels.push(r[i].textContent.trim());
          var groups = document.querySelectorAll('.ppr-month-group');
          out.groups = groups.length;
          if (groups.length === 12) {
            var row = groups[0].querySelector('.ppr-bars-row');
            var rowH = row.getBoundingClientRect().height;
            function barH(m, idx) {
              var bars = groups[m].querySelectorAll('.ppr-bar');
              return bars[idx]
                  ? bars[idx].getBoundingClientRect().height : -1;
            }
            out.kSep = barH(8, 0);   // К сентябрь = 48 → 96% от 50
            out.pApr = barH(3, 1);   // П апрель = 15 → 30% от 50
            out.toMar = barH(2, 2);  // ТО март = 500 → 100% от 500
            out.rowH = rowH;
          }
          var legend = document.querySelectorAll('.ppr-legend-item');
          out.axisLegend = 0;
          for (var j = 0; j < legend.length; j++)
            if (legend[j].textContent.indexOf('(правая ось)') !== -1)
              out.axisLegend++;
          return out;
        })()""")
        check('473-1: KipCharts загружен (Electron UA)', c['kipCharts'])
        check('473-2: заголовок ППР точный',
              c['title'] == 'Количество приборов по графику ППР '
                            'по месяцам на 2026 год', c['title'])
        check('473-3: 35 значений над столбцами (К+П+ТО по 12 месяцев)',
              c['vals'] == 35, c['vals'])
        check('473-4: 1 «0» у основания (Май, Поверка)',
              c['zeros'] == 1, c['zeros'])
        check('473-5: правая ось — метки 50…0',
              c['rightLabels'] and c['rightLabels'][0] == '50'
              and c['rightLabels'][-1] == '0', c['rightLabels'])
        check('473-6: легенда — 2 серии с «(правая ось)»',
              c['axisLegend'] == 2, c['axisLegend'])
        check('473-7: СТОЛБЦЫ ВИДИМЫ: К-48 ≈ 96% ряда (>55%), П-15 ≈ 30% '
              '(>22%), ТО-500 = 100%',
              c['kSep'] / c['rowH'] > 0.55 and c['pApr'] / c['rowH'] > 0.22
              and c['toMar'] / c['rowH'] > 0.8,
              (round(c['kSep'] / c['rowH'], 3),
               round(c['pApr'] / c['rowH'], 3),
               round(c['toMar'] / c['rowH'], 3)))
        check('473-8: 0 JS-ошибок (график)', len(js_errors_c) == 0,
              js_errors_c[:3])
        pagec.screenshot(path=os.path.join(SHOT_DIR,
                                           '03-charts-ppr-dark.png'))
        print('  скриншот: 03-charts-ppr-dark.png')
        ctxc.close()

        # ============ SW: версия kip8 ============
        import urllib.request
        sw = urllib.request.urlopen(
            'http://localhost:%d/sw.js' % PORT, timeout=10).read().decode('utf-8')
        check('SW-1: CACHE_VERSION = kipia-v509 (партия одним инкрементом)',
              "const CACHE_VERSION = 'kipia-v509';" in sw)
        check('SW-2: kipia-v508 отсутствует (v508 заменена)',
              sw.find('kipia-v508') == -1)
        check('SW-3: комментарий партии «Task 473-474»',
              'Task 473-474 (перенос партии' in sw)

        browser.close()
    server.shutdown()

    print()
    print('ИТОГО: %d + / %d X' % (PASS, FAIL))
    import sys
    sys.exit(1 if FAIL else 0)


if __name__ == '__main__':
    main()
