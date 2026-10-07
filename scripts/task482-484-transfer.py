#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 482-484-transfer: перенос ПАРТИИ из kip8test (@ac339739 Task
# 482 + @3edb79ce Task 483 + @6ec17fbd Task 484) в боевой kip8 ОДНИМ
# инкрементом SW kipia-v511 → v512 (регламент Task 441: партия = один
# инкремент; команда пользователя из заявки Task 484: «И затем
# перенеси изменения в kip8»).
# Состав партии:
#   Task 482 — табель: кап раскрытия окон бара + рамки бейджей И/ПЗ +
#              галочка отметки в попапе ячейки (index.html);
#   Task 483 — Графики КИП ИОС/«Приборы»: таблица+диаграмма «как в
#              Excel» + вычисляемые тренды ППР (charts-desktop.js +
#              sync-devices.py + data/devices.json ppr_chart);
#   Task 484 — Графики КИП ИОС/«Блокировки»: тот же вид и подсчёт +
#              удаление старого _renderPPRChart (charts-desktop.js +
#              sync-lockouts.py + data/lockouts.json ppr_chart).
# КЛИЕНТ-ONLY: .gs не тронуты (Apps Script без изменений);
# десктопы — CI-автосинк.
# Метод (Task 292/401-406/429/437/441-481): де-изоляция + «дифф
# диффов». Якоря де-изоляции index.html: те же 16 rep1 (17 якорей)
# из task478-481-transfer.py (партия изоляцию не трогала).
# ОДНОРАЗОВЫЙ: повторный прогон упадёт на якорях — лечение:
# git checkout -- . + rm новых файлов партии и чистый прогон
# (подводный камень Task 471; «проверочные» перегоны — НЕ делать;
# вывод — НЕ в пайп с head: SIGPIPE).
import io
import os
import re
import shutil
import subprocess
import sys

K8 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
K8T = os.path.abspath(os.path.join(K8, '..', 'kip8test'))
assert os.path.isdir(K8T), 'репо kip8test не найдено: %s' % K8T

V_TEST = 'kipia-test-v'
fail = []


def chk(cond, msg):
    if cond:
        print('OK: %s' % msg)
    else:
        fail.append(msg)
        print('FAIL: %s' % msg)


def rd(p):
    return io.open(p, encoding='utf-8').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


def git(repo, *args):
    r = subprocess.run(['git', '-C', repo] + list(args),
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError('git %s: %s' % (args, r.stderr[:400]))
    return r.stdout


def diff_lines(a_path, b_path, drop=None):
    r = subprocess.run(['diff', a_path, b_path],
                       capture_output=True, text=True)
    lines = [ln for ln in r.stdout.splitlines()
             if ln.startswith('<') or ln.startswith('>')]
    if drop:
        lines = [ln for ln in lines
                 if not any(p in ln for p in drop)]
    return lines


# ============================================================
# 0. База партии: kip8test@345cb6b5 (docs-зеркало post-478-481,
#    код == @81dfdc42) → партия до @6ec17fbd (Task 484).
#    kip8@HEAD = f3cdf90 (post-478-481 docs).
# ============================================================
BASE_T = '345cb6b5'
BATCH_T = '6ec17fbd'
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == BATCH_T,
    'база: kip8test HEAD = %s (ожидался %s — Task 484, авто-синков в '
    'партии нет)' % (HEAD_T, BATCH_T))
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_8 == 'f3cdf90',
    'база: kip8 HEAD = %s (ожидался f3cdf90 — post-478-481 docs)' % HEAD_8)
# рабочее дерево kip8 чистое (кроме артефактов самого перенос-скрипта)
st = git(K8, 'status', '--porcelain').strip()
noise = [ln for ln in st.splitlines()
         if ln.startswith('??') and ('task482-484-transfer' in ln
                                     or '__pycache__' in ln)]
real = [ln for ln in st.splitlines() if ln not in noise]
chk(not real, 'kip8: рабочее дерево чистое (кроме артефактов перенос-'
    'скрипта): %r' % (real[:4],))

# ============================================================
# 1. index.html — де-изоляция kip8test HEAD (16 rep1 / 17 якорей из
#    task478-481-transfer.py; партия изоляцию не трогала)
# ============================================================
print('=== 1. index.html ===')
src = rd(os.path.join(K8T, 'index.html'))
orig = src


def rep1(old, new, tag, cnt=1):
    global src
    n = src.count(old)
    if n != cnt:
        fail.append('[index %s] вхождений %d, ожидалось %d' % (tag, n, cnt))
        print('FAIL [index %s]: вхождений %d, ожидалось %d' % (tag, n, cnt))
        return
    src = src.replace(old, new)
    print('OK [index %s]' % tag)


# 1.1 Комментарий Task 243 (transform)
rep1(
    '/* Task 243 (бекпорт из kip8): !important бьёт десктопное правило '
    '#sidebar{transform:translateX(-100%)!important} (specificity '
    '#sidebar.active (1,1,0) > #sidebar (1,0,0)). В kip8test wsTrSheet уже '
    'правильно закрыт, но !important оставлен для надёжности и паритета '
    'с kip8 — чтобы при следующем переносе kip8test → kip8 не потерять '
    'фикс. */',
    '/* Task 243: !important бьёт десктопное правило '
    '#sidebar{transform:translateX(-100%)!important} (specificity '
    '#sidebar.active (1,1,0) > #sidebar (1,0,0)) — фикс бага «hamburger не '
    'открывает sidebar на 377px viewport». Task 244: корневая причина — '
    'wsTrSheet не был закрыт, sidebar оказывался вложенным в него '
    '(position:fixed относительно wsTrSheet, имевшего transform). В kip8test '
    'wsTrSheet уже правильно закрыт, но !important оставлен для '
    'надёжности. */',
    'task243-transform')

# 1.2 Комментарий Task 243 (overlay)
rep1('/* Task 243 (бекпорт): то же самое для overlay */',
     '/* Task 243: то же самое для overlay */', 'task243-overlay')

# 1.3 Комментарий про ключи localStorage (2 строки)
rep1(
    '    // (в тестовом репо ключ автоматически получает префикс kip8test:\n'
    '    // через isolateLocalStorage). При первом запуске победы из старого',
    '    // (kip8 — основной репозиторий, ключи без префикса). При первом\n'
    '    // запуске победы из старого',
    'ls-comment')

# 1.4-1.6 Ключи телефонного справочника
rep1("'kip8test_phonebook_favorites'", "'kip8_phonebook_favorites'",
     'pb-fav')
rep1("'kip8test_phonebook_notes'", "'kip8_phonebook_notes'", 'pb-notes')
rep1("'kip8test_phonebook_cache'", "'kip8_phonebook_cache'",
     'pb-cache', 2)

# 1.7 Ключ кэша приборов
rep1("const DEV_CACHE_KEY = 'kip8test_devices_cache';",
     "const DEV_CACHE_KEY = 'kip8_devices_cache';", 'dev-cache-key')

# 1.8-1.10 Обращения к кэшу приборов без префикса
rep1("localStorage.setItem('kip8test:' + DEV_CACHE_KEY, "
     "JSON.stringify(devData));",
     "localStorage.setItem(DEV_CACHE_KEY, JSON.stringify(devData));",
     'dev-set')
rep1("localStorage.getItem('kip8test:' + DEV_CACHE_KEY)",
     "localStorage.getItem(DEV_CACHE_KEY)", 'dev-get')
rep1("localStorage.setItem('kip8test:' + DEV_CACHE_KEY, "
     "JSON.stringify(fresh));",
     "localStorage.setItem(DEV_CACHE_KEY, JSON.stringify(fresh));",
     'dev-set-fresh')

# 1.11 Удаление блока isolateLocalStorage (только kip8test)
ISO_BLOCK = (
    '    // ===== ТЕСТОВЫЙ РЕПОЗИТОРИЙ kip8test: изоляция localStorage =====\n'
    '    // localStorage общий для всего origin (bloknett-design.github.io).\n'
    '    // Чтобы настройки (тема, метод калибровки буя) из тестового '
    'репозитория\n'
    '    // не влияли на основной репозиторий kip8, добавляем префикс ко '
    'всем ключам.\n'
    '    // В основном репозитории kip8 этот блок ОТСУТСТВУЕТ — там ключи '
    'без префикса.\n'
    '    (function isolateLocalStorage() {\n'
    "        const PREFIX = 'kip8test:';\n"
    '        const origGetItem = localStorage.getItem.bind(localStorage);\n'
    '        const origSetItem = localStorage.setItem.bind(localStorage);\n'
    '        const origRemoveItem = '
    'localStorage.removeItem.bind(localStorage);\n'
    '        localStorage.getItem = function(key) '
    "{ return origGetItem(PREFIX + key); };\n"
    '        localStorage.setItem = function(key, value) '
    "{ return origSetItem(PREFIX + key, value); };\n"
    '        localStorage.removeItem = function(key) '
    "{ return origRemoveItem(PREFIX + key); };\n"
    '    })();\n'
)
rep1(ISO_BLOCK, '', 'isolate-block-remove')

# 1.12 Комментарий #page-id
rep1('// Если URL содержит #page-id (например, /kip8test/#exam-tickets),',
     '// Если URL содержит #page-id (например, /kip8/#exam-tickets),',
     'page-id')

# 1.13 Комментарий URL Apps Script (5-6 строк)
rep1(
    '        // URL Apps Script Web App.\n'
    '        // Task 284: URL развёртывания пользователя (AKfycbyt…) — пробы\n'
    '        // 2026-09-01 подтвердили: проект полный (Auth/Sessions/Admin/\n'
    '        // CableJournal/Flowmeter/ValidationRules/WorkSchedule) и код\n'
    '        // свежий (роутинг отпусков есть). Прежний URL (AKfycbzg…,\n'
    '        // Task 202) остался на старом снимке кода — до Task 274.',
    '        // URL Apps Script Web App (развёртывание AKfycbyt…, в kip8 с\n'
    '        // Task 245). Пробы 2026-09-01 (Task 284 в kip8test) '
    'подтвердили:\n'
    '        // проект полный (Auth/Sessions/Admin/CableJournal/Flowmeter/\n'
    '        // ValidationRules/WorkSchedule) и код свежий — роутинг '
    'отпусков\n'
    '        // (Task 274+) есть. kip8test синхронизирован с этим же URL.',
    'url-comment')

# 1.14 Комментарий Task 242
rep1(
    '        // Task 242 (бекпорт из kip8): усиление обновления SW — вместе '
    'с\n'
    '        // skipWaiting() в sw.js и reg.update() сразу при загрузке.',
    '        // Task 242: усиление обновления SW — вместе с skipWaiting() '
    'в sw.js\n'
    '        // и reg.update() сразу при загрузке.',
    'task242')

# 1.15 Комментарий реестра Task 458
rep1(
    '        // ключ localStorage ws_auto_dn_keys (префикс репозитория\n'
    '        // ставит isolateLocalStorage)\n',
    '        // ключ localStorage ws_auto_dn_keys (в тестовом репо\n'
    '        // ключ автоматически получает префикс)\n',
    'auto-dn-keys-comment')

# 1.16 Якорь партии 475-477: имя БД KipDB + комментарий (Task 476)
rep1(
    "    // Имя БД kip8test; перенос в kip8 → 'kip8-cache-v1' (маппинг\n"
    "    // де-изоляции, как IMAGE_CACHE_VERSION kipia-images-*-v3)\n"
    "    var DB_NAME = 'kip8-cache-test-v1';",
    "    // Имя БД kip8 — основной репозиторий (в kip8test — "
    "'kip8-cache-test-v1';\n"
    "    // маппинг де-изоляции переносов, как IMAGE_CACHE_VERSION "
    "kipia-images-*-v3)\n"
    "    var DB_NAME = 'kip8-cache-v1';",
    'kipdb-name')

assert src != orig, 'index.html: ни одной трансформации не применилась'
chk(src.count('kip8test') == 6,
    'index.html: упоминаний kip8test после де-изоляции = 6 '
    '(5 исторических + 1 комментарий KipDB о маппинге): %d'
    % src.count('kip8test'))
chk(src.count(V_TEST) == 0,
    'index.html: строк kipia-test-v нет: %d' % src.count(V_TEST))
chk("var DB_NAME = 'kip8-cache-v1';" in src,
    'index.html: DB_NAME = kip8-cache-v1 (Task 476)')
chk(src.count("'kip8-cache-test-v1'") == 1,
    'index.html: kip8-cache-test-v1 ровно 1 — в комментарии маппинга '
    '(де-изоляция): %d' % src.count("'kip8-cache-test-v1'"))

# Маркеры партии 482-484 (index.html; задачи 483/484 в index.html НЕ
# меняли — модуль charts-desktop.js вынесен)
for m in ('Task 482', '_barExpMaxH', 'evStateCls', 'ws-done-chk',
          'ws-ev-done', 'ws-ev-late', 'toggleTrainingDone'):
    chk(m in src, 'index.html: маркер партии (482) %r' % (m[:44],))
# Живые задачи прошлых партий — не размыло переносом
for m in ('function devPprStatusClass',       # 478-481
          'dev-ppr-ok', 'dev-ppr-warn', 'dev-ppr-bad',
          'parseInt(m[1], 10) === now.getFullYear()',
          '<textarea id="peWorkInput" class="pe-works-input" rows="1"',
          'var KipDB = (function() {', 'var KipPreload = (function() {',
          '_schedulePreload', '_startOfflineTokenRetry'):
    chk(m in src, 'index.html: якорь живой задачи %r' % (m[:44],))

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» ---
base_t = '/tmp/k8t-index-base482.html'
base8 = '/tmp/k8-index-base482.html'
with io.open(base_t, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', BASE_T + ':index.html'))
with io.open(base8, 'w', encoding='utf-8') as f:
    f.write(git(K8, 'show', 'HEAD:index.html'))
d_new = diff_lines(k8_index_new, os.path.join(K8T, 'index.html'))
d_base = diff_lines(base8, base_t)
chk(d_new == d_base,
    'index.html: дифф(новый kip8, kip8test HEAD) == базовому репо-диффу '
    '(%d строк против %d; якорей партия не добавляла)'
    % (len(d_new), len(d_base)))
d_task8 = diff_lines(base8, k8_index_new)
d_taskT = diff_lines(base_t, os.path.join(K8T, 'index.html'))
chk(d_task8 == d_taskT,
    'index.html: дифф задач (482) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 2. sw.js — шапка kip8 (полная история задач) + перенос-метка +
#    3 комментария партии Task 482/483/484 ИЗ kip8test ДОСЛОВНО +
#    v512; ЛОГИКА SW НЕ МЕНЯЛАСЬ — ТЕЛО от IMAGE-якоря идентично
#    kip8test HEAD
# ============================================================
print('=== 2. sw.js ===')
P_SW = os.path.join(K8, 'sw.js')
sw8 = rd(P_SW)
swt = rd(os.path.join(K8T, 'sw.js'))

ANCHOR_IMG_8 = "const IMAGE_CACHE_VERSION = 'kipia-images-v3';"
ANCHOR_IMG_T = "const IMAGE_CACHE_VERSION = 'kipia-images-test-v3';"
chk(sw8.count(ANCHOR_IMG_8) == 1,
    'sw.js (kip8): якорь IMAGE_CACHE_VERSION найден')
chk(swt.count(ANCHOR_IMG_T) == 1,
    'sw.js (kip8test): якорь IMAGE_CACHE_VERSION найден')

# Комментарии партии: от '// Task 482: табель' до CACHE_VERSION
C_START = '// Task 482: табель'
i_c = swt.index(C_START)
i_cv_t = swt.index("const CACHE_VERSION = 'kipia-test-v708';")
BATCH_COMMENT = swt[i_c:i_cv_t]
chk(BATCH_COMMENT.endswith('\n') and
    BATCH_COMMENT.count('Task 482') == 1 and
    BATCH_COMMENT.count('Task 483') == 2 and
    BATCH_COMMENT.count('Task 484') == 1,
    'sw.js: извлечены 3 комментария партии (482 ×1, 483 ×2 — ярлык +\n'
    ' упоминание в комментарии 484, 484 ×1), %d симв.'
    % len(BATCH_COMMENT))
chk(V_TEST not in BATCH_COMMENT and 'kip8test' not in BATCH_COMMENT,
    'sw.js: комментарий партии версионно-нейтрален')

# Перенос-метка kip8 (прецедент Task 470-481) + бамп v511→v512
MARK = '// Task 482-484 (перенос партии из kip8test@6ec17fbd):\n'
old_v = "const CACHE_VERSION = 'kipia-v511';"
new_v = "const CACHE_VERSION = 'kipia-v512';"
chk(sw8.count(old_v) == 1,
    'sw.js: CACHE_VERSION v511 найден (%d)' % sw8.count(old_v))
sw_new = sw8.replace(old_v, MARK + BATCH_COMMENT + new_v)

for m in (new_v, "const DATA_CACHE_VERSION = 'kipia-data-v1';",
          'STALE-WHILE-REVALIDATE', 'function notifyDataChanged'):
    chk(m in sw_new, 'sw.js: маркер %r' % (m[:44],))
chk(sw_new.count(new_v) == 1,
    'sw.js: kipia-v512 ровно один (%d)' % sw_new.count(new_v))
chk('kipia-v511' not in sw_new, 'sw.js: kipia-v511 не осталось')
chk(sw_new.count('kip8test') == sw8.count('kip8test') + 1,
    'sw.js: kip8test-упоминания = исторические шапки kip8 + 1 '
    'перенос-метка партии (%d против %d+1)'
    % (sw_new.count('kip8test'), sw8.count('kip8test')))
chk(sw_new.startswith(sw8[:sw8.index(old_v)]),
    'sw.js: шапка kip8 до CACHE_VERSION не изменена (история жива)')

# ТЕЛО: от IMAGE-якоря до конца файла идентично kip8test HEAD
pbn = '/tmp/k8-sw-body-new482.js'
pbh = '/tmp/k8t-sw-body-head482.js'
wr(pbn, sw_new[sw_new.index(ANCHOR_IMG_8):])
wr(pbh, swt[swt.index(ANCHOR_IMG_T):])
d_body = diff_lines(pbn, pbh, ['kipia-data', 'kipia-images'])
chk(d_body == [],
    'sw.js: ТЕЛО идентично kip8test HEAD (от IMAGE-якоря, %d строк '
    'расхождений после фильтра версий кэшей)' % len(d_body))

# Окна истории (окна из kip8test-тестов после расширений 484:
# 474 → 4000, 472 → 4500, 471 → 5000, 461 → 7600)
i_new_v = sw_new.index(new_v)
for task_no, window in ((474, 4000), (472, 4500), (471, 5000),
                        (461, 7600), (473, 4600)):
    i_task = sw_new.rindex('Task %d' % task_no, 0, i_new_v)
    dist = i_new_v - i_task
    chk(dist < window,
        'sw.js: дистанция до комментария Task %d = %d (< %d — окно '
        'test-task%d, запас %d)' % (task_no, dist, window, task_no,
                                    window - dist))

# Комментарии партии в окнах тестов (ассерты test-task482/483/484)
w700 = sw_new[i_new_v - 700:i_new_v]
w1500 = sw_new[i_new_v - 1500:i_new_v]
w2100 = sw_new[i_new_v - 2100:i_new_v]
w2500 = sw_new[i_new_v - 2500:i_new_v]
chk(w700.count('Task 484:') == 1 and 'Блокировки' in w700 and
    'ppr_chart' in w700 and 'Логика SW не менялась' in w700,
    'sw.js: комментарий Task 484 в окне 700')
chk(w700.count('Task 483') >= 1 and 'Графики КИП ИОС' in w700 and
    'ppr_chart' in w700,
    'sw.js: Task 483 в окне 700 (упоминание в комментарии 484 «(Task '
    '483)» на ~292; собственный ярлык 483 — на ~712, ассерты test-483 '
    'проверяют упоминание без двоеточия)')
chk(w2100.count('Task 482:') == 1 and '_barExpMaxH' in w2100 and
    'рамка зелёная' in w2100 and 'галочка отметки' in w2100,
    'sw.js: комментарий Task 482 в окне 2100 (Task 482: — с двоеточием,\n'
    'чтобы не ловить перенос-метку Task 482-484)')
chk(w2100.count('Task 481') == 1 and 'ГОД' in w2100 and
    w2100.count('Task 480') >= 1 and 'Логики SW не менял' in w2100,
    'sw.js: комментарии Task 481/480 в окне 2100')
chk(w2100.count('Task 481:') == 1 and
    'Перечень КИП ИОС рабочий' in w2100,
    'sw.js: комментарий Task 481 (имя таблицы) в окне 2100')

wr(P_SW, sw_new)

# ============================================================
# 3. charts-desktop.js — простая копия (репо-специфики в модуле нет)
# ============================================================
print('=== 3. charts-desktop.js ===')
src_mod = os.path.join(K8T, 'charts-desktop.js')
dst_mod = os.path.join(K8, 'charts-desktop.js')
mod = rd(src_mod)
chk(git(K8T, 'show', BASE_T + ':charts-desktop.js') ==
    git(K8, 'show', HEAD_8 + ':charts-desktop.js'),
    'charts-desktop: базы репо идентичны (BASE_T == kip8 HEAD)')
chk('kip8test' not in mod and V_TEST not in mod,
    'charts-desktop: репо-специфики нет')
for m in ('Task 483', 'Task 484', '_renderDevicesPPR', 'ppr-tc-card',
          'ppr-tc-hatch', '_pprChartLockouts', "'Кр': { suffix: 'k'",
          'noun || ', "'БЛОКИРОВОК'"):
    chk(m in mod, 'charts-desktop: маркер партии %r' % (m[:44],))
for dead in ('_renderPPRChart: function', 'this._renderPPRChart',
             '_PPR_LOCKOUTS: {', 'this._PPR_LOCKOUTS',
             '_niceMax: function'):
    chk(dead not in mod, 'charts-desktop: удалённое (Task 484) %r' % dead)
shutil.copyfile(src_mod, dst_mod)

# ============================================================
# 4. sync-скрипты — простые копии (репо-специфики нет; ID таблицы
#    одинаков с Task 480)
# ============================================================
print('=== 4. sync-скрипты ===')
for rel, marks in (
        ('scripts/sync-devices.py',
         ['def parse_ppr_chart(', "PPR_TYPES = ['К', 'П', 'ТО']",
          "'Наличие в ППР'"]),
        ('scripts/sync-lockouts.py',
         ['def parse_ppr_chart(', "PPR_TYPES = ['Кр', 'ТО']",
          "PPR_FILTER_COL = 'Наличие в перечне и в ППР'", 'type_norm'])):
    s_t = rd(os.path.join(K8T, rel))
    chk('kip8test' not in s_t and V_TEST not in s_t,
        '%s: репо-специфики нет' % rel)
    for m in marks:
        chk(m in s_t, '%s: маркер %r' % (rel, m[:44]))
    chk(git(K8T, 'show', BASE_T + ':' + rel) ==
        git(K8, 'show', HEAD_8 + ':' + rel),
        '%s: базы репо идентичны (BASE_T == kip8 HEAD)' % rel)
    shutil.copyfile(os.path.join(K8T, rel), os.path.join(K8, rel))

# ============================================================
# 5. tests/ — копия всех test-*.js из kip8test с MAP + точечные
#    fixes (партия 482-484 в kip8 = ОДИН инкремент v511→v512)
# ============================================================
print('=== 5. tests/ ===')
TDIR_T = os.path.join(K8T, 'tests')
TDIR_8 = os.path.join(K8, 'tests')
MAP = [
    # текущие ассерты (партия 482-484 — в kip8 ОДИН инкремент v511→v512)
    ('kipia-test-v708', 'kipia-v512'),
    # guards следующей версии
    ('kipia-test-v709', 'kipia-v513'),
    # негативы партии 482-484 + шапки: «до партии» = v511
    ('kipia-test-v707', 'kipia-v511'),
    ('kipia-test-v706', 'kipia-v511'),
    ('kipia-test-v705', 'kipia-v511'),
    # партия прошлого переноса 478-481: «до партии» = v510
    ('kipia-test-v704', 'kipia-v510'),
    ('kipia-test-v703', 'kipia-v510'),
    ('kipia-test-v702', 'kipia-v510'),
    ('kipia-test-v701', 'kipia-v510'),
    # партия переноса 475-477: «до партии» = v509
    ('kipia-test-v700', 'kipia-v509'),
    ('kipia-test-v699', 'kipia-v509'),
    ('kipia-test-v698', 'kipia-v509'),
    # партия переноса 473-474: «до партии» = v508
    ('kipia-test-v697', 'kipia-v508'),
    ('kipia-test-v696', 'kipia-v508'),
    # исторические негативы (маппинг переносов 472/471/470/... — как в
    # task475-477/478-481-transfer.py, без изменений)
    ('kipia-test-v695', 'kipia-v507'),
    ('kipia-test-v694', 'kipia-v506'),
    ('kipia-test-v693', 'kipia-v505'),
    ('kipia-test-v692', 'kipia-v504'),
    ('kipia-test-v691', 'kipia-v503'),
    ('kipia-test-v690', 'kipia-v502'),
    ('kipia-test-v689', 'kipia-v501'),
    ('kipia-test-v687', 'kipia-v499'),
    ('kipia-test-v685', 'kipia-v498'),
    ('kipia-test-v684', 'kipia-v498'),
    ('kipia-test-v683', 'kipia-v498'),
    ('kipia-test-v681', 'kipia-v496'),
    ('kipia-test-v680', 'kipia-v495'),
    ('kipia-test-v679', 'kipia-v494'),
    ('kipia-test-v665', 'kipia-v481'),
    ('kipia-test-v663', 'kipia-v478'),
    ('kipia-test-v660', 'kipia-v478'),
    ('kipia-test-v642', 'kipia-v478'),
    ('kipia-test-v641', 'kipia-v478'),
    ('kipia-test-v640', 'kipia-v478'),
    ('kipia-test-v634', 'kipia-v478'),
    # кэши kip8 (без -test-)
    ('kipia-images-test-v3', 'kipia-images-v3'),
    ('kip8-cache-test-v1', 'kip8-cache-v1'),
    ('kipia-data-test-v1', 'kipia-data-v1'),
]
tot = {}
changed = 0
for name in sorted(os.listdir(TDIR_T)):
    if not name.startswith('test-') or not name.endswith('.js'):
        continue
    s = rd(os.path.join(TDIR_T, name))
    for old, new in MAP:
        if old in s:
            tot[old] = tot.get(old, 0) + s.count(old)
            s = s.replace(old, new)
    dst = os.path.join(TDIR_8, name)
    if not os.path.exists(dst) or rd(dst) != s:
        wr(dst, s)
        changed += 1
print('  test-*.js: скопировано с маппингом, изменено на диске %d' % changed)
for old, new in MAP:
    if tot.get(old, 0):
        print('  %s → %s: %d замен' % (old, new, tot.get(old, 0)))
chk(tot.get('kipia-test-v708', 0) > 500,
    'тесты: текущие ассерты v708 → v512 перекрыты (%d)'
    % tot.get('kipia-test-v708', 0))
chk(tot.get('kipia-test-v709', 0) > 100,
    'тесты: guards v709 → v513 перекрыты (%d)'
    % tot.get('kipia-test-v709', 0))
for v, tag in (('kipia-test-v705', '482'), ('kipia-test-v706', '483'),
               ('kipia-test-v707', '484')):
    chk(tot.get(v, 0) >= 1,
        'тесты: негатив партии %s %s → v511 (%d)'
        % (tag, v, tot.get(v, 0)))
for v, tag in (('kipia-test-v701', '478'), ('kipia-test-v702', '479'),
               ('kipia-test-v703', '480'), ('kipia-test-v704', '481')):
    chk(tot.get(v, 0) == 3,
        'тесты: негатив партии 478-481 %s → v510 три (шапка + assert + '
        'сообщение, %d)' % (v, tot.get(v, 0)))
for v, tag in (('kipia-test-v698', '475'), ('kipia-test-v699', '476'),
               ('kipia-test-v700', '477')):
    chk(tot.get(v, 0) == 3,
        'тесты: негатив партии 475-477 %s → v509 три (%d)'
        % (v, tot.get(v, 0)))
chk(tot.get('kipia-images-test-v3', 0) >= 2,
    'тесты: кэш картинок kipia-images-test-v3 → v3 перекрыт (%d)'
    % tot.get('kipia-images-test-v3', 0))
chk(tot.get('kip8-cache-test-v1', 0) == 3,
    'тесты: kip8-cache-test-v1 → kip8-cache-v1 три (%d)'
    % tot.get('kip8-cache-test-v1', 0))
chk(tot.get('kipia-data-test-v1', 0) >= 5,
    'тесты: kipia-data-test-v1 → kipia-data-v1 (%d)'
    % tot.get('kipia-data-test-v1', 0))


def apply_fixes(path, fixes, tag):
    s = rd(path)
    ok = True
    for old_f, new_f in fixes:
        n = s.count(old_f)
        if n != 1:
            fail.append('[%s] якорь %r найден %d раз (ожидался 1)'
                        % (tag, old_f[:44], n))
            print('FAIL [%s]: якорь %r × %d' % (tag, old_f[:44], n))
            ok = False
            continue
        s = s.replace(old_f, new_f)
    if ok:
        print('OK [%s]: точечные fixes применены' % tag)
    wr(path, s)
    return s


# --- 5.1 Шапки «SW: ...» партии 478-481 (правые концы без
#     префикса kipia-test- MAP-ом не мапятся) + kip8-адаптации
p478 = os.path.join(TDIR_8, 'test-task478.js')
s478 = apply_fixes(p478, [
    ('SW: kipia-v510 → v702.', 'SW: kipia-v510 → v511.'),
    ("'SW поднят до v702 (Task 478)'", "'SW поднят до v511 (Task 478)'"),
    ("test('прежняя версия v701 отсутствует'",
     "test('прежняя версия v510 отсутствует'"),
    ("test('несуществующая v703 отсутствует (guard)'",
     "test('несуществующая v512 отсутствует (guard)'"),
], 'test-task478')
for m in ("const CACHE_VERSION = 'kipia-v512'", "indexOf('kipia-v510') === -1",
          'kipia-v513', 'devPprStatusClass', 'dev-ppr-ok', 'dev-ppr-bad'):
    chk(m in s478, 'test-task478.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s478,
    'test-task478.js: kip8test-версий не осталось')

p479 = os.path.join(TDIR_8, 'test-task479.js')
s479 = apply_fixes(p479, [
    ('SW: kipia-v510 → v703 (комментарий',
     'SW: kipia-v510 → v511 (комментарий'),
    ("'SW поднят до v703 (Task 479)'", "'SW поднят до v511 (Task 479)'"),
    ("test('прежняя версия v702 отсутствует'",
     "test('прежняя версия v510 отсутствует'"),
    ("test('несуществующая v704 отсутствует (guard)'",
     "test('несуществующая v512 отсутствует (guard)'"),
], 'test-task479')
for m in ("const CACHE_VERSION = 'kipia-v512'", "indexOf('kipia-v510') === -1",
          'kipia-v513', 'dev-ppr-warn', 'devices-table-desktop.js'):
    chk(m in s479, 'test-task479.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s479,
    'test-task479.js: kip8test-версий не осталось')

p480 = os.path.join(TDIR_8, 'test-task480.js')
s480 = apply_fixes(p480, [
    ('SW: kipia-v510 → v704 (index.html',
     'SW: kipia-v510 → v511 (index.html'),
    ("test('несуществующая v705 отсутствует (guard)'",
     "test('несуществующая v512 отсутствует (guard)'"),
], 'test-task480-шапка')

# --- 5.2 kip8-АДАПТАЦИЯ test-task480 (два отличия боевого репо):
#     (а) README.md в kip8 НЕТ; (б) cron-расписания kip8 (PROD) на 2 ч
#     РАНЬШЕ kip8test — мапа WORKFLOWS переведена на kip8-кроны
fixes480 = [
    ('новый 1ZKOPBsD9x4wdlC5rDjz09UypD86G0Cee в 15 файлах:',
     'новый 1ZKOPBsD9x4wdlC5rDjz09UypD86G0Cee в 14 файлах (в kip8 '
     'БЕЗ README.md — его в боевом репо никогда не было):'),
    ('//     data/*.json ×4 (source-поле — метаданные синка), README.md\n'
     '//     (таблица источников), Системный_промт (таблица «Источники\n'
     '//     данных»: один файл на 4 листа Приборы/Блокировки/Клапана/\n'
     '//     Регуляторы _app).',
     '//     data/*.json ×4 (source-поле — метаданные синка), '
     'Системный_промт\n'
     '//     (таблица «Источники данных»: один файл на 4 листа\n'
     '//     Приборы/Блокировки/Клапана/Регуляторы _app). kip8-ПЕРЕНОС:\n'
     '//     README.md в kip8 отсутствует — README-тесты исключены; cron\n'
     '//     kip8 (PROD) на 2 ч раньше kip8test (мапа WORKFLOWS ниже).'),
    ("const README_SRC = read('README.md');\n",
     "// kip8: README.md отсутствует — README-тесты исключены при "
     "переносе\n"),
    ("    test('README: 4 строки таблицы синков с новым ID', () => {\n"
     "        assertEqual(countOf(README_SRC, NEW_ID), 4,\n"
     "            '4 записи: devices/lockouts/valves/regulators');\n"
     "        ['sync-devices.py', 'sync-lockouts.py', "
     "'sync-valves.py', 'sync-regulators.py']\n"
     "            .forEach((s) => assertTrue(README_SRC.indexOf(s) !== -1,\n"
     "                'скрипт ' + s + ' в таблице'));\n"
     "    });\n"
     "\n"
     "    test('README: старый ID отсутствует', () => {\n"
     "        assertTrue(README_SRC.indexOf(OLD_ID) === -1, "
     "'старая ссылка убрана');\n"
     "    });\n"
     "\n",
     "    // kip8 (перенос): README.md в боевом репо отсутствует —\n"
     "    // документация источника = таблица «Источники данных» промта\n"
     "\n"),
    ("const WORKFLOWS = {\n"
     "    '.github/workflows/sync-devices.yml':    "
     "{ script: 'scripts/sync-devices.py',    cron: '0 6 * * *' },\n"
     "    '.github/workflows/sync-lockouts.yml':   "
     "{ script: 'scripts/sync-lockouts.py',   cron: '10 3 * * *' },\n"
     "    '.github/workflows/sync-valves.yml':     "
     "{ script: 'scripts/sync-valves.py',     cron: '20 3 * * *' },\n"
     "    '.github/workflows/sync-regulators.yml': "
     "{ script: 'scripts/sync-regulators.py', cron: '30 3 * * *' }\n"
     "};",
     "// kip8 (перенос): cron-расписания ПРОД-репо — на 2 ч раньше\n"
     "// kip8test (PROD работает первым; см. комментарии в yml)\n"
     "const WORKFLOWS = {\n"
     "    '.github/workflows/sync-devices.yml':    "
     "{ script: 'scripts/sync-devices.py',    cron: '0 4 * * *' },\n"
     "    '.github/workflows/sync-lockouts.yml':   "
     "{ script: 'scripts/sync-lockouts.py',   cron: '10 1 * * *' },\n"
     "    '.github/workflows/sync-valves.yml':     "
     "{ script: 'scripts/sync-valves.py',     cron: '20 1 * * *' },\n"
     "    '.github/workflows/sync-regulators.yml': "
     "{ script: 'scripts/sync-regulators.py', cron: '30 1 * * *' }\n"
     "};"),
]
s480 = apply_fixes(p480, fixes480, 'test-task480-kip8')
for m in ("const CACHE_VERSION = 'kipia-v512'", "indexOf('kipia-v510') === -1",
          'kipia-v513', "IMAGE_CACHE_VERSION = 'kipia-images-v3'",
          "DATA_CACHE_VERSION = 'kipia-data-v1'",
          "cron: '0 4 * * *'", "cron: '10 1 * * *'",
          "cron: '20 1 * * *'", "cron: '30 1 * * *'"):
    chk(m in s480, 'test-task480.js: маркер %r' % (m[:44],))
chk('README_SRC' not in s480,
    'test-task480.js: README-ссылок не осталось (kip8 без README)')
chk('kipia-test-v' not in s480,
    'test-task480.js: kip8test-версий не осталось')

p481 = os.path.join(TDIR_8, 'test-task481.js')
s481 = apply_fixes(p481, [
    ('sw.js kipia-v510 → v705 + комментарий',
     'sw.js kipia-v510 → v511 + комментарий'),
    ("'SW поднят до v705 (Task 481)'", "'SW поднят до v511 (Task 481)'"),
    ("test('прежняя версия v704 отсутствует'",
     "test('прежняя версия v510 отсутствует'"),
    ("test('несуществующая v706 отсутствует (guard)'",
     "test('несуществующая v512 отсутствует (guard)'"),
], 'test-task481')
for m in ("const CACHE_VERSION = 'kipia-v512'", "indexOf('kipia-v510') === -1",
          'kipia-v513', 'kipia-v510 → v511'):
    chk(m in s481, 'test-task481.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s481,
    'test-task481.js: kip8test-версий не осталось')

# --- 5.3 Партия 482-484: голые версии (правые концы шапок и имена
#     тестов; MAP не трогает литералы без префикса)
p482 = os.path.join(TDIR_8, 'test-task482.js')
s482 = apply_fixes(p482, [
    ('sw.js kipia-v511 → v706 + комментарий Task 482 (~375',
     'sw.js kipia-v511 → v512 + комментарий Task 482 (~375'),
    ("'версия кэша поднята v705 → v706'",
     "'версия кэша поднята v511 → v512'"),
    ("test('несуществующая v707 отсутствует (guard)'",
     "test('несуществующая v513 отсутствует (guard)'"),
    ("test('старая v705 вычищена из sw.js'",
     "test('старая v511 вычищена из sw.js'"),
    ("'v705 не должен остаться'", "'v511 не должен остаться'"),
], 'test-task482')
for m in ("const CACHE_VERSION = 'kipia-v512'", "indexOf('kipia-v511') === -1",
          'kipia-v513', '_barExpMaxH', 'evStateCls', 'ws-done-chk'):
    chk(m in s482, 'test-task482.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s482,
    'test-task482.js: kip8test-версий не осталось')

p483 = os.path.join(TDIR_8, 'test-task483.js')
s483 = apply_fixes(p483, [
    ('// 5. SW: версия v707 + комментарий Task 483',
     '// 5. SW: версия v512 + комментарий Task 483'),
    ("test('v706 в sw.js отсутствует'",
     "test('v511 в sw.js отсутствует'"),
    ("test('v708 в sw.js отсутствует (лишний инкремент не сделан)'",
     "test('v513 в sw.js отсутствует (лишний инкремент не сделан)'"),
], 'test-task483')
for m in ("const CACHE_VERSION = 'kipia-v512'", "indexOf('kipia-v511') === -1",
          'kipia-v513', '_renderDevicesPPR', 'ppr_chart', 'MOCK_PPR'):
    chk(m in s483, 'test-task483.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s483,
    'test-task483.js: kip8test-версий не осталось')

p484 = os.path.join(TDIR_8, 'test-task484.js')
s484 = apply_fixes(p484, [
    ('// 5. SW: версия v708 + комментарий Task 484',
     '// 5. SW: версия v512 + комментарий Task 484'),
    ("test('v707 в sw.js отсутствует'",
     "test('v511 в sw.js отсутствует'"),
    ("test('v709 в sw.js отсутствует (лишний инкремент не сделан)'",
     "test('v513 в sw.js отсутствует (лишний инкремент не сделан)'"),
], 'test-task484')
for m in ("const CACHE_VERSION = 'kipia-v512'", "indexOf('kipia-v511') === -1",
          'kipia-v513', '_pprChartLockouts', 'parse_ppr_chart',
          'Наличие в перечне и в ППР', 'type_norm'):
    chk(m in s484, 'test-task484.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s484,
    'test-task484.js: kip8test-версий не осталось')
# кэши: в kip8-форме
chk("kipia-images-v3" in s484 and "kipia-data-v1" in s484,
    'test-task484.js: кэши kip8-формы')

# --- 5.4 Точечные fixes тестов прошлого переноса 475-477 (свежая
#     копия kip8test-файлов затёрла kip8-адаптации — восстановлены)
p475 = os.path.join(TDIR_8, 'test-task475.js')
s475 = apply_fixes(p475, [
    ('//   SW: kipia-v509 → v699.', '//   SW: kipia-v509 → v510.'),
], 'test-task475')
for m in ("CACHE_VERSION = 'kipia-v512'", "indexOf('kipia-v509') === -1",
          'kipia-v513', "const DATA_CACHE_VERSION = 'kipia-data-v1';",
          'SW: kipia-v509 → v510', 'notifyDataChanged',
          'resetSectionDataCache', '_startOfflineTokenRetry'):
    chk(m in s475, 'test-task475.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s475,
    'test-task475.js: kip8test-версий не осталось')

p476 = os.path.join(TDIR_8, 'test-task476.js')
s476 = apply_fixes(p476, [
    ('//   SW: kipia-v509 → v700 (логика sw.js не менялась — статический',
     '//   SW: kipia-v509 → v510 (логика sw.js не менялась — статический'),
    # тест БД: kip8-вариант (де-изоляция DB_NAME)
    ("    test('имя БД kip8test с миграцией в kip8', () => {\n"
     '        const i = INDEX_SRC.indexOf("var DB_NAME = '
     "'kip8-cache-v1';\");\n"
     "        assertTrue(i !== -1, 'DB_NAME = kip8-cache-v1');\n"
     '        assertTrue(INDEX_SRC.slice(i - 200, i).indexOf("'
     "kip8 → 'kip8-cache-v1'\") !== -1,\n"
     "            'комментарий о маппинге имени при переносе в kip8');\n"
     '    });',
     "    test('имя БД kip8 (без -test-)', () => {\n"
     '        const i = INDEX_SRC.indexOf("var DB_NAME = '
     "'kip8-cache-v1';\");\n"
     "        assertTrue(i !== -1, 'DB_NAME = kip8-cache-v1');\n"
     '        assertTrue(INDEX_SRC.slice(i - 200, i).indexOf("'
     "'kip8-cache-test-v1'\") !== -1,\n"
     "            'комментарий хранит имя тестового репо (маппинг "
     "переноса)');\n"
     '    });'),
], 'test-task476')
for m in ("CACHE_VERSION = 'kipia-v512'", "indexOf('kipia-v509') === -1",
          'kipia-v513', "var DB_NAME = 'kip8-cache-v1';",
          'SW: kipia-v509 → v510', '_wipeLocalServerData',
          '_requestPersistentStorage', 'mkFakeIdb'):
    chk(m in s476, 'test-task476.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s476,
    'test-task476.js: kip8test-версий не осталось')
chk('kip8-cache-test-v1' in s476,
    'test-task476.js: тест БД хранит имя тестового репо (маппинг)')

p477 = os.path.join(TDIR_8, 'test-task477.js')
s477 = apply_fixes(p477, [
    ('//   SW: kipia-v509 → v701 (логика sw.js не менялась —',
     '//   SW: kipia-v509 → v510 (логика sw.js не менялась —'),
], 'test-task477')
chk('SW: kipia-v509 → v510' in s477,
    'test-task477.js: шапка «SW: kipia-v509 → v510» после фикса')
for m in ("CACHE_VERSION = 'kipia-v512'", "indexOf('kipia-v509') === -1",
          'kipia-v513', 'var KipPreload = (function() {',
          'canAccess: function', '_schedulePreload', 'saveData'):
    chk(m in s477, 'test-task477.js: маркер %r' % (m[:44],))
chk('kipia-test-v' not in s477,
    'test-task477.js: kip8test-версий не осталось')

# --- 5.5 Повтор фиксов прошлого переноса в test-task474
p474 = os.path.join(TDIR_8, 'test-task474.js')
s474 = apply_fixes(p474, [
    ('//   SW: kipia-v508 → v698.', '//   SW: kipia-v508 → v509.'),
    ("'текущая версия v698'", "'текущая версия v509'"),
    ('версия до партии (v697) отсутствует',
     'версия до партии (v508) отсутствует'),
    ('v699 в sw.js отсутствует', 'v510 в sw.js отсутствует'),
], 'test-task474')
chk('kipia-test-v' not in s474,
    'test-task474.js: kip8test-версий не осталось')

# --- 5.6 Остатки kipia-test-v6xx/v7xx в kip8 после маппинга
hist = {}
for name in sorted(os.listdir(TDIR_8)):
    if not name.startswith('test-'):
        continue
    for ln in rd(os.path.join(TDIR_8, name)).splitlines():
        if V_TEST in ln:
            for m in re.findall(r'kipia-test-v\d+', ln):
                hist[m] = hist.get(m, 0) + 1
bad_hist = {k: v for k, v in hist.items()
            if int(k.rsplit('v', 1)[1]) >= 634}
chk(not bad_hist,
    'тесты kip8: незамапленные kipia-test-v6xx+ отсутствуют: %s' % bad_hist)
print('  исторические kipia-test-v* (общие, не тронуты): %s'
      % dict(sorted(hist.items())))

# --- 5.7 test-task344.js (kip8-специфичный) — бамп v511→v512
P344 = os.path.join(TDIR_8, 'test-task344.js')
s = rd(P344)
n = s.count('kipia-v511')
chk(n == 3, 'test-task344.js: ассертов kipia-v511 = 3 (%d)' % n)
s = s.replace('kipia-v511', 'kipia-v512')
wr(P344, s)

# --- 5.8 run-all.js (kip8) — + require 482/483/484 после 481
RA = os.path.join(TDIR_8, 'run-all.js')
s = rd(RA)
A = "require('./test-task481.js');\n"
B = ("require('./test-task481.js');\n"
     "// Task 482 — табель: кап раскрытия окон «Мероприятия»/«Нормы»\n"
     "// бара по низу экрана (_barExpMaxH, длинный список листается\n"
     "// внутри окна); рамки бейджей И/ПЗ ячеек — зелёная (выполнение\n"
     "// отмечено) / красная (не отмечено + дата прошла); галочка\n"
     "// отметки — в попапе ячейки рядом с ✎/✕.\n"
     "require('./test-task482.js');\n"
     "// Task 483 — Графики КИП ИОС → «Приборы»: таблица «Вид\n"
     "// обслуживания × месяцы I–XII» + сгруппированная диаграмма «как\n"
     "// в Excel» (выровнена по колонкам таблицы); данные ppr_chart\n"
     "// считает sync-devices.py по листу «Приборы» с фильтром\n"
     "// «Наличие в ППР» = «Есть»; заШитые счётчики _PPR_DEVICES удалены.\n"
     "require('./test-task483.js');\n"
     "// Task 484 — Графики КИП ИОС → «Блокировки»: тот же вид «как в\n"
     "// Excel», что «Приборы» (таблица + диаграмма из ppr_chart в\n"
     "// data/lockouts.json, sync-lockouts.py по листу «Блокировки» с\n"
     "// фильтром «Наличие в перечне и в ППР» = «Есть», серии Кр/ТО);\n"
     "// старый _renderPPRChart и заШитые _PPR_LOCKOUTS удалены.\n"
     "require('./test-task484.js');\n")
chk(s.count(A) == 1, "run-all.js: якорь test-task481 найден (%d)"
    % s.count(A))
chk('test-task482' not in s and 'test-task483' not in s and
    'test-task484' not in s,
    'run-all.js (kip8): 482/483/484 ещё не подключены')
s = s.replace(A, B)
for n_ in range(438, 484):
    if n_ == 437:
        continue
    chk("require('./test-task%d.js');" % n_ in s,
        'run-all.js: test-task%d подключён' % n_)
chk("require('./test-task344.js');" in s,
    'run-all.js (kip8): test-task344 подключён (перенос 459 жив)')
wr(RA, s)

# --- 5.9 после всего: версии в тестах kip8 — семантика kip8
left511 = {name: rd(os.path.join(TDIR_8, name)).count('kipia-v511')
           for name in sorted(os.listdir(TDIR_8))
           if name.startswith('test-') and
           'kipia-v511' in rd(os.path.join(TDIR_8, name))}
chk(set(left511) >= {'test-task482.js', 'test-task483.js',
                     'test-task484.js'},
    'тесты kip8: kipia-v511 (негативы «до партии») есть в партии '
    '482-484: %s' % sorted(left511))
left510 = {name: rd(os.path.join(TDIR_8, name)).count('kipia-v510')
           for name in sorted(os.listdir(TDIR_8))
           if name.startswith('test-') and
           'kipia-v510' in rd(os.path.join(TDIR_8, name))}
chk(set(left510) == {'test-task478.js', 'test-task479.js',
                     'test-task480.js', 'test-task481.js'},
    'тесты kip8: kipia-v510 остался только в партии 478-481: %s'
    % sorted(left510))
n512 = sum(rd(os.path.join(TDIR_8, name)).count('kipia-v512')
           for name in os.listdir(TDIR_8)
           if name.startswith('test-'))
chk(n512 > 500,
    'тесты kip8: текущих ассертов kipia-v512 > 500 (%d)' % n512)
chk('kipia-test-v7' not in ''.join(
        rd(os.path.join(TDIR_8, name))
        for name in os.listdir(TDIR_8)
        if name.startswith('test-')),
    'тесты kip8: kipia-test-v7xx не осталось вообще')

# ============================================================
# 6. DEPLOY-доки партии — копия из kip8test
# ============================================================
print('=== 6. DEPLOY-доки партии ===')
for dep in ('DEPLOY-Task482-timesheet-scroll-badges-marks.md',
            'DEPLOY-Task483-charts-devices-excel-view.md',
            'DEPLOY-Task484-charts-lockouts-excel-view.md'):
    wr(os.path.join(K8, dep), rd(os.path.join(K8T, dep)))
    chk(os.path.exists(os.path.join(K8, dep)), '%s скопирован в kip8' % dep)

# ============================================================
# 7. Данные партии: ppr_chart — ручной прогон синков в kip8
#    (выполняется ОТДЕЛЬНО после скрипта: интернeт-зависимость;
#    здесь — только проверки локальных файлов)
# ============================================================
print('=== 7. Данные (проверки; прогон синков — отдельно) ===')
for rel, key in (('data/devices.json', 'ppr_chart'),
                 ('data/lockouts.json', 'ppr_chart')):
    p_t = os.path.join(K8T, rel)
    chk(key in rd(p_t), 'kip8test %s: блок %s есть (эталон)' % (rel, key))
print('  >>> ПРОГРУЗИ kip8: python3 scripts/sync-devices.py && '
      'python3 scripts/sync-lockouts.py, затем сверь байт-в-байт с '
      'kip8test (data/devices.json, data/lockouts.json)')

print()
print('=== ИТОГ ===')
if fail:
    print('ПРОВАЛЕНО %d:' % len(fail))
    for m in fail:
        print('  - %s' % m)
    sys.exit(1)
print('ВСЁ ОК: партия 482-484 (табель 482 + графики «Приборы»/ '
    '«Блокировки» 483/484) перенесена в kip8 (SW kipia-v512), '
    'клиент-only, серверных шагов нет')
