#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 482-484 SMOKE (kip8 — ПЕРЕНОС партии): табель 482 (кап окон
# бара + рамки бейджей И/ПЗ + галочка в попапе) + Графики КИП ИОС
# 483/484 (таблица+диаграмма «как в Excel» для «Приборов» и
# «Блокировок», тренды из ppr_chart; старый _renderPPRChart удалён)
# + SW kipia-v512 + де-изоляция. Адаптация kip8test/scripts/
# task482-browser-check.py (46/46) + task484-browser-check.py (43/43)
# под боевой репо: порт 8996, ключи localStorage БЕЗ префикса
# kip8test:, UA kip8-desktop, кэш kipia-v512 (не v708).
import calendar
import json
import os
import threading
from datetime import datetime, date
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from playwright.sync_api import sync_playwright

PORT = 8996
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT_DIR = os.path.join(os.path.dirname(REPO), 'download', 'kip8-task482-484-transfer')
os.makedirs(SHOT_DIR, exist_ok=True)

ELECTRON_UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
               '(KHTML, like Gecko) kip8-desktop/1.0 '
               'Chrome/120.0.0.0 Electron/33.0.0 Safari/537.36')

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


# ============================================================
# 0. СТАТИЧЕСКИЕ проверки переноса (SW + де-изоляция + маркеры)
# ============================================================
print('== 0. СТАТИКА: SW kipia-v512 + де-изоляция + маркеры партии ==')
SW = open(os.path.join(REPO, 'sw.js'), encoding='utf-8').read()
INDEX = open(os.path.join(REPO, 'index.html'), encoding='utf-8').read()
CHARTS = open(os.path.join(REPO, 'charts-desktop.js'), encoding='utf-8').read()

check('SW: CACHE_VERSION = kipia-v512',
      "const CACHE_VERSION = 'kipia-v512';" in SW)
check('SW: перенос-метка партии Task 482-484',
      'Task 482-484 (перенос партии из kip8test@6ec17fbd)' in SW)
check('SW: комментарий Task 484 (Блокировки как в Excel)',
      'Task 484: Графики КИП ИОС' in SW and 'Блокировки' in SW)
check('SW: комментарий Task 483 (Приборы как в Excel)',
      'Task 483: Графики КИП ИОС' in SW)
check('SW: комментарий Task 482 (кап окон табеля)',
      'Task 482: табель' in SW and '_barExpMaxH' in SW)
check('SW: кэши kip8-формы (без -test-)',
      "const IMAGE_CACHE_VERSION = 'kipia-images-v3';" in SW and
      "const DATA_CACHE_VERSION = 'kipia-data-v1';" in SW)
check('SW: kipia-test-vXXX не осталось',
      'kipia-test-v' not in SW)

check('index.html: де-изоляция — БД kip8-cache-v1',
      "var DB_NAME = 'kip8-cache-v1';" in INDEX)
check('index.html: де-изоляция — блока isolateLocalStorage нет',
      'isolateLocalStorage' not in INDEX.replace(
          '// Task 243', '#').replace('wsTrSheet', '#'))
check('index.html: маркер 482 _barExpMaxH', '_barExpMaxH' in INDEX)
check('index.html: маркер 482 evStateCls (рамки бейджей)',
      'evStateCls' in INDEX)
check('index.html: маркер 482 галочка ws-done-chk',
      'ws-done-chk' in INDEX)

check('charts-desktop: маркер 483/484 _renderDevicesPPR',
      '_renderDevicesPPR: function' in CHARTS)
check('charts-desktop: маркер 484 _pprChartLockouts',
      '_pprChartLockouts' in CHARTS)
check('charts-desktop: старый _renderPPRChart удалён (Task 484)',
      '_renderPPRChart: function' not in CHARTS and
      'this._renderPPRChart' not in CHARTS)
check('charts-desktop: заШитые _PPR_LOCKOUTS удалены',
      '_PPR_LOCKOUTS: {' not in CHARTS and 'this._PPR_LOCKOUTS' not in CHARTS)

for rel in ('data/devices.json', 'data/lockouts.json'):
    d = json.load(open(os.path.join(REPO, rel), encoding='utf-8'))
    check('%s: блок ppr_chart доставлен' % rel, 'ppr_chart' in d)

# ============================================================
# Данные/моки (из task482-browser-check.py — компактная версия)
# ============================================================
TODAY = date.today()
Y, M = TODAY.year, TODAY.month
DIM = calendar.monthrange(Y, M)[1]
TODAY_ISO = '%04d-%02d-%02d' % (Y, M, TODAY.day)


def d(off):
    dd = max(1, min(DIM, TODAY.day + off))
    return '%04d-%02d-%02d' % (Y, M, dd)


CODES = [
  {'code': 'Д', 'name': 'День (12-час)', 'color': '#FFE082'},
  {'code': 'Н', 'name': 'Ночь (12-час)', 'color': '#B0BEC5'},
  {'code': 'И', 'name': 'Инструктаж', 'color': '#B3E5FC'},
  {'code': 'ОБ', 'name': 'Обучение', 'color': '#D1C4E9'},
  {'code': 'ПЗ', 'name': 'Проверка знаний', 'color': '#FFCDD2'},
]
EMPLOYEES = [
  {'таб_номер': '017', 'ФИО': 'Иванов Иван Иванович', 'тип': 'сменный',
   'смена': 1, 'шаблон_ротации': 1, 'старт_цикла': '%04d-%02d-01' % (Y, M),
   'дата_приёма': '2024-03-15', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА', 'комментарий': ''},
  {'таб_номер': '023', 'ФИО': 'Петров Пётр Петрович', 'тип': 'дневной',
   'смена': '', 'шаблон_ротации': 2, 'старт_цикла': '%04d-%02d-07' % (Y, M),
   'дата_приёма': '2025-01-20', 'дата_увольнения': '', 'в_архиве': 0,
   'должность': 'Слесарь КИПиА', 'комментарий': ''},
]
PATTERNS = [
  {'id': 1, 'name': 'Сменный сутки/двое', 'cycle': 4, 'description': '',
   'days': [{'day': 1, 'status': 'Д'}, {'day': 2, 'status': 'Н'},
            {'day': 3, 'status': ''}, {'day': 4, 'status': ''}]},
]
TRAININGS = [
  # id 100: И ВЫПОЛНЕНО (прошедшая дата) → ЗЕЛЁНАЯ рамка, галочка ON
  {'id': 100, 'тема': 'Повторный инструктаж по охране труда',
   'тип': 'инструктаж', 'дата_начала': d(-5), 'дата_окончания': d(-5),
   'таб_номер': '017', 'подразделение': '', 'выполнение': 1, 'просрочен': 0},
  # id 101: ПЗ НЕ выполнено, дата ПРОШЛА → КРАСНАЯ рамка
  {'id': 101, 'тема': 'Проверка знаний до 1000В',
   'тип': 'проверка_знаний', 'дата_начала': d(-3), 'дата_окончания': d(-3),
   'таб_номер': '017', 'подразделение': '', 'выполнение': 0, 'просрочен': 1},
  # id 102: И будущая → обычная рамка
  {'id': 102, 'тема': 'Целевой инструктаж при допуске', 'тип': 'инструктаж',
   'дата_начала': d(5), 'дата_окончания': d(5), 'таб_номер': '023',
   'подразделение': '', 'выполнение': 0, 'просрочен': 0},
  # id 103: ОБ → обычная рамка, БЕЗ галочки
  {'id': 103, 'тема': 'Обучение по новой редакции инструкций',
   'тип': 'обучение', 'дата_начала': d(-2), 'дата_окончания': d(-2),
   'таб_номер': '023', 'подразделение': ''},
]
# длинный хвост: 30 инструктажей Иванова (окно мероприятий ДЛИННЕЕ экрана)
for k in range(30):
    day = max(1, min(DIM, k + 1))
    iso = '%04d-%02d-%02d' % (Y, M, day)
    done = 1 if (iso < TODAY_ISO and k % 5 == 0) else 0
    late = 1 if (iso < TODAY_ISO and done == 0) else 0
    TRAININGS.append({
        'id': 200 + k, 'тема': 'Инструктаж по охране труда №%d (длинное '
        'название пункта для переноса строк окна мероприятий)' % (k + 1),
        'тип': 'инструктаж', 'дата_начала': iso, 'дата_окончания': iso,
        'таб_номер': '017', 'подразделение': '',
        'выполнение': done, 'просрочен': late})
ENTRIES = [
  {'id': 1, 'дата': d(-6), 'таб_номер': '017', 'статус': 'Д',
   'источник': 'авто'},
]
PPE = [{'id': 1, 'таб_номер': '017', 'наименование': 'Каска защитная',
        'дата_выдачи': d(-100), 'дата_окончания': d(4), 'состояние': ''}]


def mock_response(action, body):
    if action == 'getCurrentUser':
        return {'ok': True, 'data': {'userId': 1, 'email': 'user@test.local',
                                     'role': 'Админ'}}
    if action == 'getMyAccess':
        return {'ok': True, 'data': {'role': 'Админ', 'found': True,
                'permissions': {'kipios.view': True, 'charts.view': True,
                                'workschedule.view': True,
                                'workschedule.edit': True}}}
    if action == 'heartbeat':
        return {'ok': True, 'data': {'ok': True}}
    if action == 'workSchedule.getStatusCodes':
        return {'ok': True, 'data': {'codes': CODES}}
    if action == 'workSchedule.listEmployees':
        return {'ok': True, 'data': {'employees': EMPLOYEES}}
    if action == 'workSchedule.getPatterns':
        return {'ok': True, 'data': {'patterns': PATTERNS}}
    if action == 'workSchedule.listTrainings':
        return {'ok': True, 'data': {'trainings': TRAININGS}}
    if action == 'workSchedule.listPpe':
        return {'ok': True, 'data': {'ppe': PPE}}
    if action == 'workSchedule.listEntries':
        if body and body.get('month') == M:
            return {'ok': True, 'data': {'entries': ENTRIES}}
        return {'ok': True, 'data': {'entries': []}}
    if action == 'workSchedule.listVacations':
        return {'ok': True, 'data': {'vacations': []}}
    if action == 'workSchedule.setTrainingDone':
        tid = int((body or {}).get('id', 0))
        val = int((body or {}).get('выполнение', 0))
        rec = None
        for t in TRAININGS:
            if int(t['id']) == tid:
                rec = t
                break
        if rec:
            rec['выполнение'] = val
            rec['просрочен'] = 1 if (val != 1 and
                                     rec['дата_начала'] < TODAY_ISO) else 0
            return {'ok': True, 'data': {'id': tid, 'выполнение': val,
                    'просрочен': rec['просрочен'], 'created': [],
                    'updated': [], 'srvVer': 427}}
        return {'ok': False, 'error': 'запись не найдена'}
    return {'ok': True, 'data': {'ok': True}}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve():
    os.chdir(REPO)
    httpd = HTTPServer(('127.0.0.1', PORT), QuietHandler)
    httpd.serve_forever()


# Сид ProdCalendar: 24 особых дня → окно «Нормы» длинное (кап)
def pcal_seed_js():
    days = {}
    for k in range(24):
        day = 1 + k
        if day > DIM:
            break
        mmdd = '%02d%02d' % (M, day)
        if k % 3 == 0:
            days[mmdd] = {'off': True, 'holiday': True, 'short': False,
                          'work': False,
                          'title': 'Праздник тестовый №%d' % (k + 1)}
        elif k % 3 == 1:
            days[mmdd] = {'off': True, 'holiday': False, 'short': False,
                          'work': False,
                          'title': 'Выходной, перенесённый'}
        else:
            days[mmdd] = {'off': False, 'holiday': False, 'short': True,
                          'work': False, 'title': 'Сокращённый №%d' % (k + 1)}
    payload = json.dumps({'source': 'legalic', 'fetchedAtMs': 48 * 3600 * 1000,
                          'days': days}, ensure_ascii=False)
    # kip8: ключ БЕЗ префикса kip8test:
    return ("try{localStorage.setItem('ws_pcal_year3_%d_42', %s)}catch(e){};"
            % (Y, json.dumps(payload)))


def attach(page, ctx, theme, tag):
    js_errors = []
    page.on('pageerror', lambda e: js_errors.append(str(e)))
    page.on('dialog', lambda d: d.accept())

    def handle(route, request):
        url = request.url
        action = ''
        if 'action=' in url:
            action = unquote(url.split('action=')[1].split('&')[0])
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
    # kip8: ключи localStorage БЕЗ префикса kip8test:
    ctx.add_init_script(
        "try{localStorage.removeItem('kip8_my_access')}catch(e){};" +
        "try{localStorage.removeItem('kip8_session_token')}catch(e){};" +
        "try{if(window.navigator.serviceWorker){navigator.serviceWorker.getRegistrations()"
        ".then(function(rs){rs.forEach(function(r){r.unregister();});});}}catch(e){};" +
        "localStorage.setItem('kip8_session_token','bc-t48x-%s');" % tag +
        "localStorage.setItem('app-theme','%s');" % theme +
        pcal_seed_js())
    return js_errors


CELL_BADGES_JS = r"""(([tab, day]) => {
    const empCell = document.querySelector(
        'td.ws-emp-col[data-tab="' + tab + '"]');
    if (!empCell) return null;
    const row = empCell.closest('tr');
    if (!row) return null;
    const td = row.querySelector('td[data-day="' + day + '"]');
    if (!td) return null;
    const badges = [...td.querySelectorAll('.ws-ev-badge')].map(b => ({
        code: b.textContent.trim(), cls: b.className,
        border: getComputedStyle(b).borderColor}));
    return {day: day, badges: badges};})"""

POPUP_STATE_JS = r"""(() => {
    const evp = document.getElementById('wsEventsPopup');
    const rows = evp ? [...evp.querySelectorAll('.ws-popup-row.ws-popup-event')] : [];
    return {
        active: !!(evp && evp.classList.contains('active')),
        rows: rows.map(r => ({
            code: r.querySelector('.ws-popup-code') ?
                  r.querySelector('.ws-popup-code').textContent.trim() : '',
            chk: r.querySelector('.ws-done-chk') ?
                 r.querySelector('.ws-done-chk').className : null,
            chkTitle: r.querySelector('.ws-done-chk') ?
                      r.querySelector('.ws-done-chk').title : '',
            hasToggle: !!r.querySelector('[onclick*="toggleTrainingDone"]'),
            hasEdit: !!r.querySelector('[title="Редактировать"]'),
            hasDel: !!r.querySelector('[title="Удалить"]'),
            chkFirst: !!(r.querySelector('.ws-done-chk') &&
                        r.innerHTML.indexOf('ws-done-chk') <
                        r.innerHTML.indexOf('title="Редактировать"'))
        }))};})"""


def open_grid(page):
    page.goto('http://localhost:%d/index.html' % PORT)
    page.wait_for_timeout(2500)
    page.evaluate("navigateTo('work-schedule')")
    page.wait_for_timeout(1800)


# --- Снимок DOM графиков (из task484-browser-check.py) ---
SNAPSHOT_JS = r"""(() => {
    const card = document.querySelector('.ppr-tc-card');
    if (!card) return {error: 'карточка не найдена'};
    const q = s => [...card.querySelectorAll(s)];
    const bg = el => {
        const c = getComputedStyle(el).backgroundColor;
        const m = c.match(/rgba?\(([^)]+)\)/);
        return m ? m[1] : c;
    };
    const months = q('.ppr-tc-m');
    const names = q('.ppr-tc-name');
    const badges = q('.ppr-tc-badge');
    const vals = q('.ppr-tc-v');
    const groups = q('.ppr-tc-g');
    return {
        title: (card.querySelector('.ppr-tc-title') || {}).textContent || '',
        months: months.map(m => ({t: m.textContent.trim(), bg: bg(m),
                                  x: m.getBoundingClientRect().x,
                                  w: m.getBoundingClientRect().width})),
        rows: names.map((n, i) => ({
            name: n.textContent.trim(),
            badge: badges[i] ? {t: badges[i].textContent.trim()} : null,
            values: vals.slice(i * 12, i * 12 + 12).map(v => v.textContent.trim())})),
        groups: groups.map(g => {
            const r = g.getBoundingClientRect();
            const bcells = [...g.querySelectorAll('.ppr-tc-bcell')];
            return {x: r.x, w: r.width,
                    bcells: bcells.map(bc => {
                        const bar = bc.querySelector('.ppr-tc-bar');
                        if (!bar) return {zero: true};
                        const br = bar.getBoundingClientRect();
                        return {h: br.height,
                                bg: getComputedStyle(bar).backgroundColor,
                                img: getComputedStyle(bar).backgroundImage};})};
        }),
        cardBg: bg(card),
        valLabels: q('.ppr-tc-val').length,
        solidBars: q('.ppr-tc-bar:not(.ppr-tc-hatch)').length,
        hatchBars: q('.ppr-tc-bar.ppr-tc-hatch').length
    };
})()"""

GONE_JS = r"""(() => ({
    oldChart: !!document.querySelector('.ppr-chart-card'),
    statsGrid: !!document.querySelector('.chart-stats-grid'),
    top10: !!document.querySelector('.chart-bar-row'),
    tabActive: (document.querySelector('.charts-tab-active') || {})
               .getAttribute('data-chart-tab') || ''
}))()"""

# Эталоны данных
PPR_LOCK = json.load(open(os.path.join(REPO, 'data', 'lockouts.json'),
                          encoding='utf-8'))['ppr_chart']
PPR_DEV = json.load(open(os.path.join(REPO, 'data', 'devices.json'),
                         encoding='utf-8'))['ppr_chart']
SER_L = {s['code']: s['values'] for s in PPR_LOCK['series']}
NAM_L = {s['code']: s['name'] for s in PPR_LOCK['series']}
SER_D = {s['code']: s['values'] for s in PPR_DEV['series']}


def main():
    server = HTTPServer(('127.0.0.1', PORT), lambda *a, **k: None)
    server.server_close()
    threading.Thread(target=serve, daemon=True).start()

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ==============================================================
        print('== 1. ГРАФИКИ (десктоп 1400x900, Electron UA, тёмная) ==')
        ctx = browser.new_context(viewport={'width': 1400, 'height': 900},
                                  user_agent=ELECTRON_UA)
        page = ctx.new_page()
        js_errors = attach(page, ctx, 'dark', 'charts')
        page.goto('http://localhost:%d/index.html' % PORT)
        page.wait_for_timeout(2500)
        page.evaluate("navigateTo('charts')")
        page.wait_for_timeout(2500)

        # --- 483: вкладка «Приборы» (активна по умолчанию) ---
        snap_d = page.evaluate(SNAPSHOT_JS)
        check('483: карточка «Приборов» отрисована', 'error' not in snap_d)
        check('483: титул «Количество ПРИБОРОВ … на 2026 год»',
              snap_d.get('title', '').strip() ==
              'Количество ПРИБОРОВ по графику ППР по месяцам на 2026 год',
              snap_d.get('title'))
        check('483: 3 строки К/П/ТО, значения == ppr_chart',
              len(snap_d.get('rows', [])) == 3 and
              all(snap_d['rows'][i]['values'] ==
                  [str(v) for v in SER_D[code]]
                  for i, code in enumerate(('К', 'П', 'ТО'))))
        check('483: итоги К 350 / П 84 / ТО 2977 («Есть»-фильтр)',
              {c: sum(SER_D[c]) for c in ('К', 'П', 'ТО')} ==
              {'К': 350, 'П': 84, 'ТО': 2977})

        # --- 484: вкладка «Блокировки» ---
        page.evaluate("KipCharts.switchTab('lockouts')")
        page.wait_for_timeout(2000)
        check('484: вкладка «Блокировки» активна',
              page.evaluate("(() => {const t=document.querySelector("
                            "'.charts-tab-active');return !!t && "
                            "t.getAttribute('data-chart-tab')==="
                            "'lockouts';})()"))
        snap = page.evaluate(SNAPSHOT_JS)
        check('484: карточка отрисована', 'error' not in snap)
        gone = page.evaluate(GONE_JS)
        check('484 G: старый график/статистика/Топ-10 НЕ рендерятся',
              not gone['oldChart'] and not gone['statsGrid'] and
              not gone['top10'])
        check('484: титул «Количество БЛОКИРОВОК … на 2026 год»',
              snap['title'].strip() ==
              'Количество БЛОКИРОВОК по графику ППР по месяцам на 2026 год',
              repr(snap['title']))
        ROMANS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX',
                  'X', 'XI', 'XII']
        check('484: месяцы I–XII',
              [m['t'] for m in snap['months']] == ROMANS)
        check('484: 2 строки Кан. ремонт/Тех. обслуж.',
              [r['name'] for r in snap['rows']] == [NAM_L['Кр'], NAM_L['ТО']])
        check('484: бейджи Кр/ТО',
              snap['rows'][0]['badge'] and
              snap['rows'][0]['badge']['t'] == 'Кр' and
              snap['rows'][1]['badge']['t'] == 'ТО')
        for i, code in enumerate(('Кр', 'ТО')):
            expected = [str(v) for v in SER_L[code]]
            check('484: значения строки %s == ppr_chart' % code,
                  snap['rows'][i]['values'] == expected)
        check('484: логика «Есть»-фильтра: итоги Кр 503 / ТО 1509',
              {c: sum(SER_L[c]) for c in ('Кр', 'ТО')} ==
              {'Кр': 503, 'ТО': 1509})
        check('484: диаграмма 12 групп, 12 Кр + 12 штрихованных ТО',
              len(snap['groups']) == 12 and snap['solidBars'] == 12 and
              snap['hatchBars'] == 12)
        BLUE = 'rgb(79, 129, 189)'
        kr_bars = [g['bcells'][0] for g in snap['groups']]
        to_bars = [g['bcells'][1] for g in snap['groups']]
        check('484: цвет Кр #4F81BD (все 12)',
              all('bg' in b and b['bg'] == BLUE for b in kr_bars))
        check('484: штриховка ТО repeating-linear-gradient (все 12)',
              all('img' in b and 'repeating-linear-gradient' in b['img']
                  for b in to_bars))
        max_h = max(b['h'] for g in snap['groups']
                    for b in g['bcells'] if 'h' in b)
        to3 = to_bars[2]
        check('484: масштаб — столбец ТО/III (макс 205) самый высокий',
              to3['h'] == max_h, (to3['h'], max_h))
        for i in (0, 5, 11):
            mx = snap['months'][i]['x'] + snap['months'][i]['w'] / 2
            gx = snap['groups'][i]['x'] + snap['groups'][i]['w'] / 2
            check('484: выравнивание %s (±3px)' % ROMANS[i],
                  abs(mx - gx) <= 3, (mx, gx))
        check('484: карточка БЕЛАЯ (документ-вид, тёмная тема)',
              snap['cardBg'] == '255, 255, 255')
        shot(page, 'charts-lockouts-dark.png')
        check('0 JS-ошибок (графики тёмная)', not js_errors, js_errors[:3])
        ctx.close()

        # ==============================================================
        print('== 2. ГРАФИКИ светлая + ФОЛБЭК ==')
        ctx2 = browser.new_context(viewport={'width': 1400, 'height': 900},
                                   user_agent=ELECTRON_UA,
                                   color_scheme='light')
        page2 = ctx2.new_page()
        js_errors2 = attach(page2, ctx2, 'light', 'light')
        page2.goto('http://localhost:%d/index.html' % PORT)
        page2.wait_for_timeout(2000)
        page2.evaluate("navigateTo('charts')")
        page2.wait_for_timeout(1500)
        page2.evaluate("KipCharts.switchTab('lockouts')")
        page2.wait_for_timeout(2000)
        snap2 = page2.evaluate(SNAPSHOT_JS)
        check('светлая: карточка ТАК ЖЕ белая',
              snap2.get('cardBg') == '255, 255, 255', snap2.get('cardBg'))
        check('светлая: значения те же (2 серии × 12)',
              len(snap2['rows']) == 2 and
              all(len(r['values']) == 12 for r in snap2['rows']))
        shot(page2, 'charts-lockouts-light.png')
        check('0 JS-ошибок (светлая)', not js_errors2, js_errors2[:3])
        ctx2.close()

        ctx3 = browser.new_context(viewport={'width': 1400, 'height': 900},
                                   user_agent=ELECTRON_UA)
        page3 = ctx3.new_page()
        js_errors3 = attach(page3, ctx3, 'dark', 'fb')

        def strip_ppr(route, request):
            if 'data/lockouts.json' in request.url:
                data = json.loads(open(
                    os.path.join(REPO, 'data', 'lockouts.json'),
                    encoding='utf-8').read())
                data.pop('ppr_chart', None)
                return route.fulfill(status=200,
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(data, ensure_ascii=False))
            return route.continue_()

        ctx3.route('**/data/lockouts.json*', strip_ppr)
        page3.goto('http://localhost:%d/index.html' % PORT)
        page3.wait_for_timeout(2000)
        page3.evaluate("navigateTo('charts')")
        page3.wait_for_timeout(1500)
        page3.evaluate("KipCharts.switchTab('lockouts')")
        page3.wait_for_timeout(2500)
        note = page3.evaluate(
            "((document.querySelector('.ppr-tc-empty-note')||{})"
            ".textContent||'').trim()")
        check('фолбэк: сообщение про блокировки (без ppr_chart)',
              'Данные графика ППР' in note and 'блокировкам' in note,
              repr(note))
        shot(page3, 'charts-fallback.png')
        check('0 JS-ошибок (фолбэк)', not js_errors3, js_errors3[:3])
        ctx3.close()

        # ==============================================================
        print('== 3. ТАБЕЛЬ 482 (десктоп 1280x900, Electron UA) ==')
        ctx4 = browser.new_context(viewport={'width': 1280, 'height': 900},
                                   user_agent=ELECTRON_UA)
        page4 = ctx4.new_page()
        js_errors4 = attach(page4, ctx4, 'dark', 'ws')
        open_grid(page4)

        # A: кап раскрытия окна «Мероприятия»
        st = page4.evaluate("""(() => {
            const el = document.getElementById('wsEventsPanel');
            if (!el) return null;
            const r = el.getBoundingClientRect();
            return {hidden: el.hidden, h: r.height, top: r.top,
                    sh: el.scrollHeight, vh: window.innerHeight};})()""")
        check('окно мероприятий отрисовано, список длинный',
              st and (not st['hidden']) and st['sh'] > 650, st)
        check('в свёрнутом виде — компактная высота 95px',
              st and abs(st['h'] - 95) < 2, st)
        page4.click('#wsEventsPanel .ws-bar-exp')
        page4.wait_for_timeout(400)
        st2 = page4.evaluate("""(() => {
            const el = document.getElementById('wsEventsPanel');
            const r = el.getBoundingClientRect();
            const cs = getComputedStyle(el);
            return {open: el.classList.contains('ws-bar-open'),
                    h: r.height, top: r.top, bottom: r.bottom,
                    sh: el.scrollHeight, ch: el.clientHeight,
                    overflowY: cs.overflowY, vh: window.innerHeight};})()""")
        check('окно раскрыто (ws-bar-open)', st2['open'])
        check('КАП: низ окна НЕ ниже экрана (vh − 10)',
              st2['bottom'] <= st2['vh'] - 8, st2)
        check('КАП: содержимое листается ВНУТРИ (scrollHeight > clientHeight)',
              st2['sh'] > st2['ch'] and st2['overflowY'] == 'auto', st2)
        page4.click('#wsEventsPanel .ws-bar-exp')
        page4.wait_for_timeout(300)

        # B: рамки бейджей И/ПЗ
        day100 = int(d(-5).split('-')[2])
        day101 = int(d(-3).split('-')[2])
        day102 = int(d(5).split('-')[2])
        b1 = page4.evaluate(CELL_BADGES_JS, ['017', day100])
        b2 = page4.evaluate(CELL_BADGES_JS, ['017', day101])
        b3 = page4.evaluate(CELL_BADGES_JS, ['023', day102])
        check('бейдж И (выполнено): класс ws-ev-done + ЗЕЛЁНАЯ #43a047',
              b1 and any('ws-ev-done' in x['cls'] and
                         x['border'] == 'rgb(67, 160, 71)'
                         for x in b1['badges']), b1)
        check('бейдж ПЗ (просрочен): класс ws-ev-late + КРАСНАЯ #ef5350',
              b2 and any('ws-ev-late' in x['cls'] and
                         x['border'] == 'rgb(239, 83, 80)'
                         for x in b2['badges'] if x['code'] == 'ПЗ'), b2)
        check('бейдж И (будущая дата): обычная рамка',
              b3 and any(x['border'] == 'rgba(0, 0, 0, 0.45)'
                         for x in b3['badges'] if x['code'] == 'И'), b3)
        shot(page4, 'ws-grid-badges.png')

        # C: попап ячейки — галочка
        page4.evaluate("""(([tab, day]) => {
            const emp = document.querySelector(
                'td.ws-emp-col[data-tab="' + tab + '"]');
            const td = emp.closest('tr')
                .querySelector('td[data-day="' + day + '"]');
            td.click();})""", ['017', day100])
        page4.wait_for_timeout(350)
        ps1 = page4.evaluate(POPUP_STATE_JS)
        r_instr = [r for r in ps1['rows'] if r['code'] == 'И']
        check('попап открыт, строка И: галочка ВКЛ + клик toggle + ✎/✕',
              ps1['active'] and r_instr and r_instr[0]['chk'] and
              'ws-done-on' in r_instr[0]['chk'] and r_instr[0]['hasToggle']
              and r_instr[0]['hasEdit'] and r_instr[0]['hasDel'], ps1)
        check('галочка РЯДОМ с ✎/✕ (порядок в разметке)',
              r_instr and r_instr[0]['chkFirst'], ps1)
        shot(page4, 'ws-popup-check.png')
        check('0 JS-ошибок (табель)', not js_errors4, js_errors4[:3])
        ctx4.close()

        browser.close()

    print('\n════ ИТОГ: %d passed, %d failed ════' % (PASS, FAIL))
    return 0 if FAIL == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
