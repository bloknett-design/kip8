#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 443-transfer: перенос Task 443 из kip8test (HEAD e6cad4c) в
# боевой kip8 ОДНИМ инкрементом SW kipia-v481 → v482.
# Регламент Task 441 («Переноси все изменения в боевой репозиторий
# kip8») — плановый перенос каждой задачи после приёмки в kip8test.
# ВАЖНО ОТ ПРЕДЫДУЩИХ ПЕРЕНОСОВ: задача 443 ТРОГАЛА СЕРВЕР —
# WorkSchedule.gs и PPEInit.gs копируются из kip8test HEAD (базы
# обоих репо идентичны); Code.gs НЕ тронут задачей — kip8-версия
# сохраняется байт-в-байт.
# Метод (Task 292/401-406/429/437/441/442): файловый синк +
# де-изоляция + верификация «дифф диффов».
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
# 1. index.html — де-изоляция kip8test HEAD (e6cad4c)
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
    '        const PREFIX = \'kip8test:\';\n'
    '        const origGetItem = localStorage.getItem.bind(localStorage);\n'
    '        const origSetItem = localStorage.setItem.bind(localStorage);\n'
    '        const origRemoveItem = '
    'localStorage.removeItem.bind(localStorage);\n'
    '        localStorage.getItem = function(key) '
    "{ return origGetItem(PREFIX + key); };\n"
    '        localStorage.setItem = function(key, value) '
    "{ return origSetItem(PREFIX + key, value); };\n"
    '        localStorage.removeItem = function(key) '
    "{ return origRemoveItem(PREFIX + key, value) — см. ниже; };\n"
)
# (блок выше — точный текст; при несовпадении упадёт с FAIL и покажет)
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
    '        const PREFIX = \'kip8test:\';\n'
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

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» ---
# База партии: kip8test@c614f6e (Task 442 — состояние, перенесённое в
# kip8@HEAD 927a177) против kip8@HEAD.
base_t = '/tmp/k8t-index-base443.html'
base8 = '/tmp/k8-index-base443.html'
with io.open(base_t, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', 'c614f6e:index.html'))
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
    'index.html: дифф задач (443) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 2. scripts/WorkSchedule.gs — задача ТРОГАЛА (СИЗ): копия из
#    kip8test HEAD; базы идентичны (srvVer 427 не тронут)
# ============================================================
print('=== 2. scripts/WorkSchedule.gs (копия — задача 443 меняла) ===')
ws_t = os.path.join(K8T, 'scripts', 'WorkSchedule.gs')
ws_8 = os.path.join(K8, 'scripts', 'WorkSchedule.gs')
with io.open('/tmp/k8t-ws-base443.gs', 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', 'c614f6e:scripts/WorkSchedule.gs'))
with io.open('/tmp/k8-ws-base443.gs', 'w', encoding='utf-8') as f:
    f.write(git(K8, 'show', 'HEAD:scripts/WorkSchedule.gs'))
chk(diff_lines('/tmp/k8-ws-base443.gs', '/tmp/k8t-ws-base443.gs') == [],
    'WorkSchedule.gs: базы партий идентичны в обоих репо (442 не трогал)')
d_ws_task8 = diff_lines('/tmp/k8-ws-base443.gs', ws_t)
chk(len(d_ws_task8) > 100,
    'WorkSchedule.gs: дифф задач 443 присутствует (%d строк)' % len(d_ws_task8))
wr(ws_8, rd(ws_t))
chk(diff_lines(ws_8, ws_t) == [],
    'WorkSchedule.gs: скопирован из kip8test HEAD (1:1)')
chk(rd(ws_8).count('дата_изготовления') > 10,
    'WorkSchedule.gs: столбец дата_изготовления на месте (%d упоминаний)'
    % rd(ws_8).count('дата_изготовления'))

# ============================================================
# 3. scripts/PPEInit.gs — задача ТРОГАЛА: копия из kip8test HEAD
# ============================================================
print('=== 3. scripts/PPEInit.gs (копия — задача 443 меняла) ===')
ppe_t = os.path.join(K8T, 'scripts', 'PPEInit.gs')
ppe_8 = os.path.join(K8, 'scripts', 'PPEInit.gs')
with io.open('/tmp/k8t-ppe-base443.gs', 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', 'c614f6e:scripts/PPEInit.gs'))
with io.open('/tmp/k8-ppe-base443.gs', 'w', encoding='utf-8') as f:
    f.write(git(K8, 'show', 'HEAD:scripts/PPEInit.gs'))
chk(diff_lines('/tmp/k8-ppe-base443.gs', '/tmp/k8t-ppe-base443.gs') == [],
    'PPEInit.gs: базы партий идентичны в обоих репо')
wr(ppe_8, rd(ppe_t))
chk(diff_lines(ppe_8, ppe_t) == [], 'PPEInit.gs: скопирован из kip8test HEAD')
chk('function ppeMigrateManufacture()' in rd(ppe_8),
    'PPEInit.gs: ppeMigrateManufacture на месте')

# ============================================================
# 4. scripts/Code.gs — задачей НЕ тронут (сохраняем kip8-версию)
# ============================================================
print('=== 4. scripts/Code.gs ===')
code_8 = os.path.join(K8, 'scripts', 'Code.gs')
with io.open('/tmp/k8-code-head443.gs', 'w', encoding='utf-8') as f:
    f.write(git(K8, 'show', 'HEAD:scripts/Code.gs'))
chk(rd(code_8) == io.open('/tmp/k8-code-head443.gs',
                          encoding='utf-8').read(),
    'Code.gs: kip8-версия сохранена как есть (задача 443 не трогала)')

# ============================================================
# 5. tests/ — копия с маппингом версий
# ============================================================
print('=== 5. tests/ ===')
TDIR_T = os.path.join(K8T, 'tests')
TDIR_8 = os.path.join(K8, 'tests')
MAP = [
    ('kipia-test-v667', 'kipia-v482'),   # текущие ассерты
    ('kipia-test-v668', 'kipia-v483'),   # guards следующей версии
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
chk(tot.get('kipia-test-v667', 0) > 400,
    'тесты: текущие ассерты v667 перекрыты (%d)'
    % tot.get('kipia-test-v667', 0))
chk(tot.get('kipia-test-v668', 0) > 90,
    'тесты: guards v668 перекрыты (%d)' % tot.get('kipia-test-v668', 0))
chk(tot.get('kipia-test-v665', 0) == 2,
    'тесты: негатив v665 (файлы 441/442) → v481 (%d замен)'
    % tot.get('kipia-test-v665', 0))
chk(tot.get('kipia-test-v663', 0) == 1,
    'тесты: негатив v663 (task440) → v478 (%d замен)'
    % tot.get('kipia-test-v663', 0))
chk(tot.get('kipia-test-v660', 0) == 2,
    'тесты: негатив v660 (435/436) → v478')

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

# 5.1 test-task344.js (kip8-специфичный) — бамп v481→v482
P344 = os.path.join(TDIR_8, 'test-task344.js')
s = rd(P344)
n = s.count('kipia-v481')
chk(n == 3, 'test-task344.js: ассертов kipia-v481 = 3 (%d)' % n)
s = s.replace('kipia-v481', 'kipia-v482')
wr(P344, s)

# 5.2 run-all.js — копия + require test-task344 после 343
RA = os.path.join(TDIR_8, 'run-all.js')
s = rd(os.path.join(TDIR_T, 'run-all.js'))
A = "require('./test-task343.js');\n"
B = "require('./test-task343.js');\nrequire('./test-task344.js');\n"
chk(s.count(A) == 1, "run-all.js: якорь test-task343 найден (%d)" % s.count(A))
chk('test-task344' not in s, 'run-all.js: 344 ещё не подключён')
s = s.replace(A, B)
for t in ('test-task438', 'test-task439', 'test-task440',
          'test-task441', 'test-task442', 'test-task443'):
    chk("require('./%s.js');" % t in s,
        'run-all.js: %s подключён' % t)
wr(RA, s)

# ============================================================
# 6. sw.js — версия + комментарий задачи
# ============================================================
print('=== 6. sw.js ===')
P = os.path.join(K8, 'sw.js')
s = rd(P)
old_v = "const CACHE_VERSION = 'kipia-v481';"
new_v = "const CACHE_VERSION = 'kipia-v482';"
chk(s.count(old_v) == 1, 'sw.js: CACHE_VERSION v481 найден (%d)'
    % s.count(old_v))
COMMENT = (
    '// Task 443 (перенос из kip8test@e6cad4c; задача С СЕРВЕРНОЙ\n'
    '// ЧАСТЬЮ — WorkSchedule.gs/PPEInit.gs обновлены, Code.gs НЕ\n'
    '// тронут, srvVer 427): СИЗ — НОВЫЙ столбец G «дата_изготовления»\n'
    '// справа от F «дата_выдачи» (срок/окончание/примечание сместились\n'
    '// в H/I/J); дата окончания = дата ИЗГОТОВЛЕНИЯ + срок\n'
    '// (ПРИОРИТЕТ — фильтрующие коробки противогазов), иначе дата\n'
    '// выдачи + срок; поле «Дата изготовления» в шторке СИЗ, «изгот.»\n'
    '// в карточке, мобильный ряд дат — столбик на <=480px; миграция\n'
    '// листа ppeMigrateManufacture() в PPEInit.gs (см. DEPLOY —\n'
    '// серверные шаги Apps Script).\n'
)
if 'Task 443 (перенос из kip8test' not in s:
    s = s.replace(old_v, COMMENT + new_v)
chk("const CACHE_VERSION = 'kipia-v482';" in s, 'sw.js: v482 установлен')
chk(s.count('kipia-v482') == 1, 'sw.js: маркёр v482 один (%d)'
    % s.count('kipia-v482'))
chk('kipia-v481' not in s.replace(new_v, ''),
    'sw.js: литерал прошлой версии v481 не встречается (негатив-гард)')
wr(P, s)

print()
print('=== ИТОГ ===')
if fail:
    print('ПРОВАЛЕНО %d:' % len(fail))
    for m in fail:
        print('  - %s' % m)
    sys.exit(1)
print('ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ. Дальше: node tests/run-all.js в kip8.')
