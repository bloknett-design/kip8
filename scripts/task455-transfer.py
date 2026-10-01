#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 455-transfer: перенос Task 455 из kip8test (HEAD 5f144f9) в
# боевой kip8 ОДНИМ инкрементом SW kipia-v493 → v494.
# Регламент Task 441. Задача — только клиентская логика «Талонов»
# (index.html) — WorkSchedule.gs/PPEInit.gs/Code.gs НЕ ТРОНУТЫ
# (проверка идентичности, паттерн 438-454). Метод (Task 292/401-406/
# 429/437/441-454): файловый синк + де-изоляция + «дифф диффов».
import io
import os
import re
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


def diff_lines(a_path, b_path):
    r = subprocess.run(['diff', a_path, b_path],
                       capture_output=True, text=True)
    return [ln for ln in r.stdout.splitlines()
            if ln.startswith('<') or ln.startswith('>')]


# ============================================================
# 0. База партии: kip8test@b41be80 (Task 454) ↔ kip8@HEAD
# ============================================================
BASE_T = 'b41be80'   # Task 454 в kip8test (перенесён в kip8@b443309)
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == '5f144f9',
    'база: kip8test HEAD = %s (Task 455, ожидался 5f144f9)' % HEAD_T)

# ============================================================
# 1. index.html — де-изоляция kip8test HEAD
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

assert src != orig, 'index.html: ни одной трансформации не применилась'
chk(src.count('kip8test') == 4,
    'index.html: упоминаний kip8test после де-изоляции = 4 '
    '(исторические): %d' % src.count('kip8test'))
chk(src.count(V_TEST) == 0,
    'index.html: строк kipia-test-v нет: %d' % src.count(V_TEST))
chk('var y = this._year, m = this._month;' in src,
    'index.html: _talonsMonthInfo Task 455 (месяц сетки) присутствует')
chk('за месяц, открытый в шахматке табеля' in src,
    'index.html: подзаголовок Task 455 присутствует')
chk('_TALONS_CACHE' not in src.replace(
        '// Task 455: кэш _TALONS_CACHE и подтяжка _talonsFetchMonth', ''),
    'index.html: кэш _TALONS_CACHE удалён (кроме комментария-документации)')

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» ---
# База партии: kip8test@b41be80 (Task 454 — состояние, перенесённое в
# kip8@HEAD; фикс-коммит kip8 b443309 — содержимо то же, доксы и
# автокоммит lockouts index.html не трогали) против kip8@HEAD.
base_t = '/tmp/k8t-index-base455.html'
base8 = '/tmp/k8-index-base455.html'
with io.open(base_t, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', BASE_T + ':index.html'))
with io.open(base8, 'w', encoding='utf-8') as f:
    f.write(git(K8, 'show', 'HEAD:index.html'))
d_new = diff_lines(k8_index_new, os.path.join(K8T, 'index.html'))
d_base = diff_lines(base8, base_t)
chk(d_new == d_base,
    'index.html: дифф(новый kip8, kip8test HEAD) == базовому репо-диффу '
    '(%d строк против %d)' % (len(d_new), len(d_base)))
d_task8 = diff_lines(base8, k8_index_new)
d_taskT = diff_lines(base_t, os.path.join(K8T, 'index.html'))
chk(d_task8 == d_taskT,
    'index.html: дифф задач (455) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 2. scripts/*.gs — Task 455 НЕ ТРОГАЛА (проверка идентичности)
# ============================================================
print('=== 2. scripts/*.gs — не тронуты (455 — только index.html) ===')
for gs in ('WorkSchedule.gs', 'PPEInit.gs'):
    p8 = os.path.join(K8, 'scripts', gs)
    pt = os.path.join(K8T, 'scripts', gs)
    head8 = git(K8, 'show', 'HEAD:scripts/' + gs)
    chk(rd(p8) == head8,
        '%s: kip8-версия == HEAD (455 не трогала)' % gs)
    chk(rd(pt) == head8,
        '%s: kip8test HEAD == kip8 HEAD (синхронны)' % gs)
p8c = os.path.join(K8, 'scripts', 'Code.gs')
chk(rd(p8c) == git(K8, 'show', 'HEAD:scripts/Code.gs'),
    'Code.gs: kip8-версия == HEAD (455 не трогала; kip8test-версия '
    'исторически отличается — не копируется, паттерн 443-454)')

# ============================================================
# 3. tests/ — копия с маппингом версий
# ============================================================
print('=== 3. tests/ ===')
TDIR_T = os.path.join(K8T, 'tests')
TDIR_8 = os.path.join(K8, 'tests')
MAP = [
    ('kipia-test-v679', 'kipia-v494'),   # текущие ассерты (бамп 455)
    ('kipia-test-v680', 'kipia-v495'),   # guards следующей версии
    ('kipia-test-v665', 'kipia-v481'),   # негативы 441/442
    ('kipia-test-v663', 'kipia-v478'),   # негатив task440
    ('kipia-test-v660', 'kipia-v478'),   # негативы 435/436
    ('kipia-test-v642', 'kipia-v478'),
    ('kipia-test-v641', 'kipia-v478'),
    ('kipia-test-v640', 'kipia-v478'),
    ('kipia-test-v634', 'kipia-v478'),
]
tot = {}
copied = changed = 0
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
    copied += 1
print('  test-*.js: скопировано %d, изменено на диске %d' % (copied, changed))
for old, new in MAP:
    print('  %s → %s: %d замен' % (old, new, tot.get(old, 0)))
chk(tot.get('kipia-test-v679', 0) > 400,
    'тесты: текущие ассерты v679 → v494 перекрыты (%d)'
    % tot.get('kipia-test-v679', 0))
chk(tot.get('kipia-test-v680', 0) > 90,
    'тесты: guards v680 → v495 перекрыты (%d)' % tot.get('kipia-test-v680', 0))
chk(os.path.exists(os.path.join(TDIR_8, 'test-task455.js')),
    'test-task455.js скопирован в kip8')
t455 = rd(os.path.join(TDIR_8, 'test-task455.js'))
chk("CACHE_VERSION = 'kipia-v494'" in t455,
    'test-task455.js в kip8: ассерт SW v494 замаплен')
chk('var y = this._year, m = this._month;' in t455,
    'test-task455.js в kip8: ассерты Task 455 на месте')

# остатки kipia-test (исторические, общие для репо)
hist = {}
for name in sorted(os.listdir(TDIR_8)):
    if not name.startswith('test-'):
        continue
    for ln in rd(os.path.join(TDIR_8, name)).splitlines():
        if V_TEST in ln:
            for m in re.findall(r'kipia-test-v\d+', ln):
                hist[m] = hist.get(m, 0) + 1
print('  исторические kipia-test-v* (общие, не тронуты): %s'
      % dict(sorted(hist.items())))

# 3.1 test-task344.js (kip8-специфичный) — бамп v493→v494
P344 = os.path.join(TDIR_8, 'test-task344.js')
s = rd(P344)
n = s.count('kipia-v493')
chk(n == 3, 'test-task344.js: ассертов kipia-v493 = 3 (%d)' % n)
s = s.replace('kipia-v493', 'kipia-v494')
wr(P344, s)

# 3.2 run-all.js — копия + require test-task344 после 343
RA = os.path.join(TDIR_8, 'run-all.js')
s = rd(os.path.join(TDIR_T, 'run-all.js'))
A = "require('./test-task343.js');\n"
B = "require('./test-task343.js');\nrequire('./test-task344.js');\n"
chk(s.count(A) == 1, "run-all.js: якорь test-task343 найден (%d)" % s.count(A))
chk('test-task344' not in s, 'run-all.js: 344 ещё не подключён')
s = s.replace(A, B)
for t in ['test-task%d' % n_ for n_ in range(438, 456)]:
    chk("require('./%s.js');" % t in s,
        'run-all.js: %s подключён' % t)
chk("require('./test-task455.js');" in s,
    'run-all.js: test-task455 подключён (Task 455)')
wr(RA, s)

# ============================================================
# 4. sw.js — версия + комментарий задачи
# ============================================================
print('=== 4. sw.js ===')
P = os.path.join(K8, 'sw.js')
s = rd(P)
old_v = "const CACHE_VERSION = 'kipia-v493';"
new_v = "const CACHE_VERSION = 'kipia-v494';"
chk(s.count(old_v) == 1, 'sw.js: CACHE_VERSION v493 найден (%d)'
    % s.count(old_v))
COMMENT = (
    '// Task 455 (перенос из kip8test): «Талоны» — месяц отчёта =\n'
    '// МЕСЯЦ ОТКРЫТОЙ ШАХМАТКИ табеля (селекты тулбара; до —\n'
    '// всегда текущий); записи — всегда живая сетка: кэш\n'
    '// _TALONS_CACHE и подтяжка _talonsFetchMonth удалены;\n'
    '// «Обновить данные» — всегда refreshData сетки.\n'
)
if 'Task 455 (перенос из kip8test' not in s:
    s = s.replace(old_v, COMMENT + new_v)
chk("const CACHE_VERSION = 'kipia-v494';" in s, 'sw.js: v494 установлен')
chk(s.count('kipia-v494') == 1, 'sw.js: маркёр v494 один (%d)'
    % s.count('kipia-v494'))
wr(P, s)

# ============================================================
# 5. DEPLOY-Task455 — копия док-ноты из kip8test
# ============================================================
print('=== 5. DEPLOY-Task455 (копия из kip8test) ===')
src_dep = os.path.join(
    K8T, 'DEPLOY-Task455-talons-month-follows-grid.md')
dst_dep = os.path.join(
    K8, 'DEPLOY-Task455-talons-month-follows-grid.md')
wr(dst_dep, rd(src_dep))
chk(os.path.exists(dst_dep), 'DEPLOY-Task455 скопирован в kip8')

print()
print('=== ИТОГ ===')
if fail:
    print('ПРОВАЛЕНО %d:' % len(fail))
    for m in fail:
        print('  - %s' % m)
    sys.exit(1)
print('ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ. Дальше: node tests/run-all.js в kip8.')
