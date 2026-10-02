#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 460-462-transfer: перенос ПАРТИИ Tasks 460+461+462 из kip8test
# (фиксы 5c9c80e/8febd23/63b10de, HEAD 92d54d7) в боевой kip8 ОДНИМ
# инкрементом SW kipia-v498 → v499 (регламент Task 441: партия = один
# инкремент, прецедент Tasks 259-262). Состав партии:
#   Task 460 — НОВЫЙ раздел «Плановые мероприятия» (статичная таблица
#              образца в «Документации ИОС»);
#   Task 461 — форма СИЗ: datalist наименований динамически из листа
#              «СИЗ» табель_КИП_ИОС (_fillPpeNameOptions);
#   Task 462 — доступ к разделу: ОТДЕЛЬНОЕ право plan.events в матрице
#              KIP8_Access (+ scripts/RoleMatrixTask462Init.gs —
#              одноразовый init-скрипт; серверный шаг УЖЕ ВЫПОЛНЕН
#              пользователем: Apps Script/матрица общие на оба репо).
# Метод (Task 292/401-406/429/437/441-459): файловый синк + де-изоляция
# + «дифф диффов». Якоря де-изоляции скопированы ТОЧНО из
# task459-transfer.py (подводные камни 455/457 учтены).
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
# 0. База партии: kip8test@3923f6a (Task 459 docs — состояние,
#    перенесённое в kip8@eb5151d; далее bf1a8dc/632f14a/доки
#    index.html не трогали) ↔ kip8@HEAD (12d5c2d — автокоммит
#    devices, index.html от eb5151d)
# ============================================================
BASE_T = '3923f6a'   # Task 459 docs в kip8test
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == '92d54d7',
    'база: kip8test HEAD = %s (Task 462 docs, ожидался 92d54d7)' % HEAD_T)
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
print('  kip8 HEAD = %s (ожидался 12d5c2d — авто-devices поверх 459)'
      % HEAD_8)
chk(HEAD_8 == '12d5c2d',
    'база: kip8 HEAD = %s — Task 459 перенесён, автокоммит devices '
    'забран' % HEAD_8)

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


# 1.1 Комментарий Task 243 (transform) — якорь из task459-transfer.py
# (скопирован ТОЧНО; подводный камень 455 учтён)
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
# ⚠️ ЯКОРЬ КОПИРОВАН ТОЧНО из task459-transfer.py (тот брал его из
# исправленного task455-transfer.py: origRemoveItem(PREFIX + key) —
# БЕЗ value; подводный камень 455)
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

# 1.15 Комментарий реестра Task 458 (упоминание isolateLocalStorage
# в kip8 запрещено тестом test-task344: 0 упоминаний) — якорь 458/459
rep1(
    '        // ключ localStorage ws_auto_dn_keys (префикс репозитория\n'
    '        // ставит isolateLocalStorage)\n',
    '        // ключ localStorage ws_auto_dn_keys (в тестовом репо\n'
    '        // ключ автоматически получает префикс)\n',
    'auto-dn-keys-comment')

assert src != orig, 'index.html: ни одной трансформации не применилась'
chk(src.count('kip8test') == 4,
    'index.html: упоминаний kip8test после де-изоляции = 4 '
    '(исторические): %d' % src.count('kip8test'))
chk(src.count(V_TEST) == 0,
    'index.html: строк kipia-test-v нет: %d' % src.count(V_TEST))

# Task 460: маркеры раздела «Плановые мероприятия»
chk('id="planEventsMenuBtn"' in src,
    'index.html: кнопка planEventsMenuBtn (хаб «Документация ИОС»)')
chk('id="page-plan-events"' in src,
    'index.html: страница #page-plan-events')
chk('В начале месяца' in src and 'В конце месяца' in src,
    'index.html: группы таблицы «В начале/В конце месяца»')
chk('class="pe-table"' in src and 'pe-th-year' in src,
    'index.html: таблица образца pe-table/pe-th-year')
# Task 461: маркеры datalist СИЗ
chk('_fillPpeNameOptions: function()' in src,
    'index.html: метод _fillPpeNameOptions (Task 461)')
chk('<datalist id="wsPpeNameList">' in src,
    'index.html: datalist #wsPpeNameList')
chk('list="wsPpeNameList"' in src,
    'index.html: инпут наименования СИЗ привязан к datalist')
# Task 462: маркеры права plan.events
chk("_PLAN_EVENTS_PAGES: ['plan-events']" in src,
    'index.html: группа доступа _PLAN_EVENTS_PAGES')
chk("const PLAN_EVENTS = this._PLAN_EVENTS_PAGES; // Task 462" in src,
    'index.html: константа PLAN_EVENTS в init()')
chk("_drop(this._PLAN_EVENTS_PAGES); // Task 462" in src,
    'index.html: _drop(_PLAN_EVENTS_PAGES) в _applyServerAccess')
chk("if (perm('plan.events')) _add(this._PLAN_EVENTS_PAGES);" in src,
    'index.html: доступ по perm(\'plan.events\')')
chk("Object.prototype.hasOwnProperty.call(acc.permissions, 'plan.events')"
    in src,
    'index.html: переходный hasOwnProperty-фоллбек (нет колонки → 460)')
# негатив: plan-events НЕ в _KIP_IOS_PAGES (убран Task 462)
idx = src.find('_KIP_IOS_PAGES:')
blk = src[idx:src.find(']', idx)] if idx != -1 else ''
chk(idx != -1 and "'plan-events'" not in blk,
    'index.html: plan-events УБРАН из _KIP_IOS_PAGES (своя группа)')

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» ---
# База партии 460-462: kip8test@3923f6a (Task 459 — состояние,
# перенесённое в kip8@eb5151d; docs/авто-коммиты после него index.html
# не трогали) против kip8@HEAD.
base_t = '/tmp/k8t-index-base460.html'
base8 = '/tmp/k8-index-base460.html'
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
    'index.html: дифф задач (460+461+462) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 2. scripts/*.gs — партия серверный код НЕ трогала: проверка
#    идентичности + КОПИЯ НОВОГО RoleMatrixTask462Init.gs
# ============================================================
print('=== 2. scripts/*.gs ===')
for gs in ('WorkSchedule.gs', 'PPEInit.gs', 'RoleMatrix.gs',
           'RoleMatrixGate.gs'):
    p8 = os.path.join(K8, 'scripts', gs)
    pt = os.path.join(K8T, 'scripts', gs)
    head8 = git(K8, 'show', 'HEAD:scripts/' + gs)
    chk(rd(p8) == head8,
        '%s: kip8-версия == HEAD (партия не трогала)' % gs)
    chk(rd(pt) == head8,
        '%s: kip8test HEAD == kip8 HEAD (синхронны)' % gs)
p8c = os.path.join(K8, 'scripts', 'Code.gs')
chk(rd(p8c) == git(K8, 'show', 'HEAD:scripts/Code.gs'),
    'Code.gs: kip8-версия == HEAD (партия не трогала; kip8test-версия '
    'исторически отличается — не копируется, паттерн 443-459)')

# НОВЫЙ ФАЙЛ Task 462: RoleMatrixTask462Init.gs — копия из kip8test
INIT_NAME = 'RoleMatrixTask462Init.gs'
src_gs = rd(os.path.join(K8T, 'scripts', INIT_NAME))
chk('task462AddPlanEventsPermission' in src_gs,
    '%s: функция task462AddPlanEventsPermission на месте' % INIT_NAME)
chk("'plan.events'" in src_gs,
    '%s: колонка plan.events в init-скрипте' % INIT_NAME)
dst_gs = os.path.join(K8, 'scripts', INIT_NAME)
wr(dst_gs, src_gs)
chk(rd(dst_gs) == src_gs,
    '%s: скопирован в kip8/scripts (эталон; серверный шаг уже выполнен '
    'пользователем — Apps Script один на оба репо)' % INIT_NAME)

# ============================================================
# 3. tests/ — копия с маппингом версий
# ============================================================
print('=== 3. tests/ ===')
TDIR_T = os.path.join(K8T, 'tests')
TDIR_8 = os.path.join(K8, 'tests')
MAP = [
    # текущие ассерты (бамп партии 460+461+462 — в kip8 ОДИН инкремент)
    ('kipia-test-v686', 'kipia-v499'),
    # guards следующей версии
    ('kipia-test-v687', 'kipia-v500'),
    # негативы задач партии: в kip8 «версия до партии» одна — v498
    ('kipia-test-v685', 'kipia-v498'),   # негатив task462 (×1)
    ('kipia-test-v684', 'kipia-v498'),   # негатив task461 (×3)
    ('kipia-test-v683', 'kipia-v498'),   # негатив task460 (×1)
    # исторические негативы (маппинг 458/459 перенесён дальше)
    ('kipia-test-v681', 'kipia-v496'),   # негатив task458
    ('kipia-test-v680', 'kipia-v495'),   # негатив task457
    ('kipia-test-v679', 'kipia-v494'),   # негатив task456
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
chk(tot.get('kipia-test-v686', 0) > 400,
    'тесты: текущие ассерты v686 → v499 перекрыты (%d)'
    % tot.get('kipia-test-v686', 0))
chk(tot.get('kipia-test-v687', 0) > 90,
    'тесты: guards v687 → v500 перекрыты (%d)'
    % tot.get('kipia-test-v687', 0))
chk(tot.get('kipia-test-v685', 0) == 1,
    'тесты: негатив v685 → v498 один (test-task462, %d)'
    % tot.get('kipia-test-v685', 0))
chk(tot.get('kipia-test-v684', 0) == 3,
    'тесты: негатив v684 → v498 три (test-task461, %d)'
    % tot.get('kipia-test-v684', 0))
chk(tot.get('kipia-test-v683', 0) == 1,
    'тесты: негатив v683 → v498 один (test-task460, %d)'
    % tot.get('kipia-test-v683', 0))
chk(tot.get('kipia-test-v681', 0) == 1,
    'тесты: негатив v681 → v496 один (test-task458, %d)'
    % tot.get('kipia-test-v681', 0))
chk(tot.get('kipia-test-v680', 0) == 1,
    'тесты: негатив v680 → v495 один (test-task457, %d)'
    % tot.get('kipia-test-v680', 0))
chk(tot.get('kipia-test-v679', 0) == 1,
    'тесты: негатив v679 → v494 один (test-task456, %d)'
    % tot.get('kipia-test-v679', 0))

# новые тест-файлы партии — в kip8, с замапленными версиями
for name, marks in (
    ('test-task460.js', ['SW_SRC.indexOf("kipia-v499")',
                         'kipia-v498', 'Task 460']),
    ('test-task461.js', ["CACHE_VERSION = 'kipia-v499'",
                         'kipia-v498', 'wsPpeNameList']),
    ('test-task462.js', ["const CACHE_VERSION = 'kipia-v499';",
                         'kipia-v498', 'RoleMatrixTask462Init.gs',
                         'plan.events']),
):
    p = os.path.join(TDIR_8, name)
    chk(os.path.exists(p), '%s скопирован в kip8' % name)
    s = rd(p)
    for m in marks:
        chk(m in s, '%s: маркер %r замаплен' % (name, m[:44]))

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

# 3.1 test-task344.js (kip8-специфичный) — бамп v498→v499
P344 = os.path.join(TDIR_8, 'test-task344.js')
s = rd(P344)
n = s.count('kipia-v498')
chk(n == 3, 'test-task344.js: ассертов kipia-v498 = 3 (%d)' % n)
s = s.replace('kipia-v498', 'kipia-v499')
wr(P344, s)

# 3.2 run-all.js — копия + require test-task344 после 343
# (test-task344 — kip8-специфичный тест, в kip8test его НЕТ;
# копия из kip8test затирает строку — вставляем по якорю)
RA = os.path.join(TDIR_8, 'run-all.js')
s = rd(os.path.join(TDIR_T, 'run-all.js'))
A = "require('./test-task343.js');\n"
B = "require('./test-task343.js');\nrequire('./test-task344.js');\n"
chk(s.count(A) == 1, "run-all.js: якорь test-task343 найден (%d)" % s.count(A))
chk('test-task344' not in s, 'run-all.js (kip8test): 344 ещё не подключён')
s = s.replace(A, B)
for n_ in range(438, 463):
    if n_ == 437:
        continue
    chk("require('./test-task%d.js');" % n_ in s,
        'run-all.js: test-task%d подключён' % n_)
chk("require('./test-task460.js');" in s and
    "require('./test-task461.js');" in s and
    "require('./test-task462.js');" in s,
    'run-all.js: тесты партии 460+461+462 подключены')
wr(RA, s)
s8 = rd(RA)
chk("require('./test-task344.js');" in s8,
    'run-all.js (kip8): test-task344 подключён (перенос 459 сохранён)')

# 3.3 после всего: kipia-v498 в тестах kip8 — ТОЛЬКО негативы
# «версии до партии» в трёх новых файлах (5 ссылок суммарно)
left498 = {name: rd(os.path.join(TDIR_8, name)).count('kipia-v498')
           for name in sorted(os.listdir(TDIR_8))
           if name.startswith('test-') and
           'kipia-v498' in rd(os.path.join(TDIR_8, name))}
chk(left498 == {'test-task460.js': 1, 'test-task461.js': 3,
                'test-task462.js': 1},
    'тесты kip8: kipia-v498 остался ТОЛЬКО в негативах партии '
    '(до версии v498): %s' % left498)

# ============================================================
# 4. sw.js — версия + комментарий партии
# ============================================================
print('=== 4. sw.js ===')
P = os.path.join(K8, 'sw.js')
s = rd(P)
old_v = "const CACHE_VERSION = 'kipia-v498';"
new_v = "const CACHE_VERSION = 'kipia-v499';"
chk(s.count(old_v) == 1, 'sw.js: CACHE_VERSION v498 найден (%d)'
    % s.count(old_v))
COMMENT = (
    '// Task 460-462 (перенос партии из kip8test@92d54d7): Task 460 —\n'
    '// НОВЫЙ раздел «Плановые мероприятия» в «Документации ИОС»\n'
    '// (статичная таблица образца «Мероприятия × 2026 год»); Task 461 —\n'
    '// форма СИЗ: подсказки datalist #wsPpeNameList динамически из\n'
    '// листа «СИЗ» (_fillPpeNameOptions); Task 462 — доступ к разделу\n'
    '// по отдельному праву plan.events в матрице KIP8_Access.\n'
)
if 'Task 460-462 (перенос партии' not in s:
    s = s.replace(old_v, COMMENT + new_v)
chk("const CACHE_VERSION = 'kipia-v499';" in s, 'sw.js: v499 установлен')
chk(s.count('kipia-v499') == 1, 'sw.js: маркер v499 один (%d)'
    % s.count('kipia-v499'))
chk('Task 460' in s and 'Task 461' in s and 'Task 462' in s,
    'sw.js: комментарий партии упоминает Tasks 460/461/462')
chk('wsPpeNameList' in s and 'plan.events' in s and
    'Плановые мероприятия' in s,
    'sw.js: маркеры тестов партии (wsPpeNameList/plan.events/раздел)')
chk(len(COMMENT) < 700,
    'sw.js: комментарий партии %d символов (< 700 — окно test-task461)'
    % len(COMMENT))
wr(P, s)

# ============================================================
# 5. DEPLOY-доки партии — копии из kip8test
# ============================================================
print('=== 5. DEPLOY-Task460/461/462 (копии из kip8test) ===')
for dep in ('DEPLOY-Task460-plan-events-section.md',
            'DEPLOY-Task461-ppe-name-suggestions.md',
            'DEPLOY-Task462-plan-events-access-matrix.md'):
    src_dep = os.path.join(K8T, dep)
    dst_dep = os.path.join(K8, dep)
    wr(dst_dep, rd(src_dep))
    chk(os.path.exists(dst_dep), '%s скопирован в kip8' % dep)

print()
print('=== ИТОГ ===')
if fail:
    print('ПРОВАЛЕНО %d:' % len(fail))
    for m in fail:
        print('  - %s' % m)
    sys.exit(1)
print('ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ. Дальше: node tests/run-all.js в kip8.')
