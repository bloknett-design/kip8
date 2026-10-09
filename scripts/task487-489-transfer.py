#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 487-489-transfer: перенос партии 487+488+489 из kip8test
# (@58965654 HEAD; фичи 53a7e3a6/3248998d/3f57c4c9 — docs-коммиты
# код не трогали) в боевой kip8 ОДНИМ инкрементом SW kipia-v514 →
# v515 (команда пользователя: «Переноси в kip8»; регламент Task 441).
# ЧАСТЬ 1: index.html (wholesale де-изоляция ×16 rep1/17 якорей —
# партия изоляцию НЕ трогала; «дифф диффов» сходится), sw.js (шапка
# kip8 + перенос-метка + 3 комментария партии ДОСЛОВНО + v515,
# ТЕЛО от IMAGE-якоря идентично), scripts/WorkSchedule.gs (Task 489
# — Apps Script разворачивает пользователь; репо-специфики нет).
# ЧАСТЬ 2 (отдельно): tests/ — 3-way merge + НОВЫЕ тесты с MAP.
# ОДНОРАЗОВЫЙ: лечение при сбое — git checkout -- . + rm новых
# файлов партии + чистый прогон (вывод В ФАЙЛ, не через пайпы!).
import io
import os
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


def diff_lines(p1, p2):
    # Только строки < / > (заголовки @@ несут межрепо смещения —
    # изоляция; прецедент task482-484/486-transfer.py)
    r = subprocess.run(['diff', p1, p2], capture_output=True, text=True)
    return [ln for ln in r.stdout.splitlines()
            if ln.startswith('<') or ln.startswith('>')]


# ============================================================
# 0. База: kip8test HEAD = 58965654 (docs поверх фичи 3f57c4c9),
#    kip8 HEAD = 2735ac0 (авто-коммиты данных; код с 40474c7
#    не менялся), рабочие деревья чистые
# ============================================================
print('=== 0. База ===')
BASE_T = '39e7025b'   # kip8test до партии (post-486 docs-зеркало)
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == '58965654', 'база: kip8test HEAD = %s (ожидался 58965654)'
    % HEAD_T)
chk(git(K8T, 'show', '%s:index.html' % HEAD_T) ==
    git(K8T, 'show', '%s:index.html' % '3f57c4c9'),
    'база: index.html в docs-коммитах не менялся (== фиче 489)')
chk(git(K8T, 'show', '%s:sw.js' % HEAD_T) ==
    git(K8T, 'show', '%s:sw.js' % '3f57c4c9'),
    'база: sw.js в docs-коммитах не менялся')
chk(git(K8T, 'show', '%s:scripts/WorkSchedule.gs' % HEAD_T) ==
    git(K8T, 'show', '%s:scripts/WorkSchedule.gs' % '3f57c4c9'),
    'база: WorkSchedule.gs в docs-коммитах не менялся')
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_8 == '2735ac0', 'база: kip8 HEAD = %s (ожидался 2735ac0)'
    % HEAD_8)
st = git(K8, 'status', '--porcelain').strip()
noise = [ln for ln in st.splitlines() if ln.startswith('??')
         and ('task487-489' in ln or '__pycache__' in ln
              or 'analyze-487' in ln or 'show-487' in ln)]
real = [ln for ln in st.splitlines() if ln not in noise]
chk(not real, 'kip8: рабочее дерево чистое: %r' % (real[:4],))

# ============================================================
# 1. index.html — де-изоляция kip8test HEAD (16 rep1 / 17 якорей;
#    партия изоляцию не трогала) + «дифф диффов»
# ============================================================
print('=== 1. index.html ===')
src = git(K8T, 'show', '%s:index.html' % HEAD_T)
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
    '(5 исторических + 1 комментарий KipDB): %d' % src.count('kip8test'))
chk(src.count(V_TEST) == 0,
    'index.html: строк kipia-test-v нет: %d' % src.count(V_TEST))
chk("var DB_NAME = 'kip8-cache-v1';" in src,
    'index.html: DB_NAME = kip8-cache-v1 (Task 476)')
chk(src.count("'kip8-cache-test-v1'") == 1,
    'index.html: kip8-cache-test-v1 ровно 1 — в комментарии маппинга: %d'
    % src.count("'kip8-cache-test-v1'"))

# Маркеры партии 487-489 (_employeesColMap/employeesSplitInit —
# серверные, живут в WorkSchedule.gs, НЕ в index.html)
for m in ('Task 487', 'Task 488', 'Task 489',
          'onCellHover', '_openHoverPopup',      # 487: ховер
          '_wsXlsDocProps', '_wsTabelRows',       # 488: xlsx
          'wsEmpFam', 'wsEmpName', 'wsEmpPatr',
          'wsEmpBirth',                            # 489: сотрудники
          '_wsShortFio', '_wsFullFio'):
    chk(m in src, 'index.html: маркер партии %r' % (m,))
# Живые задачи прошлых партий — не размыло переносом
for m in ('function devPprStatusClass',       # 478-481
          '_barExpMaxH', 'evStateCls',        # 482
          'var KipDB = (function() {', 'var KipPreload = (function() {',
          '_schedulePreload', '_startOfflineTokenRetry',
          'silentRefresh'):                   # 486
    chk(m in src, 'index.html: якорь живой задачи %r' % (m,))

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» ---
TMP = '/home/z/my-project/scripts/.k8t-487-489-tmp'
os.makedirs(TMP, exist_ok=True)
base_t = os.path.join(TMP, 'k8t-index-base.html')
base8 = os.path.join(TMP, 'k8-index-base.html')
head_t = os.path.join(TMP, 'k8t-index-head.html')
with io.open(base_t, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', '%s:index.html' % BASE_T))
with io.open(base8, 'w', encoding='utf-8') as f:
    f.write(git(K8, 'show', 'HEAD:index.html'))
with io.open(head_t, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', '%s:index.html' % HEAD_T))
d_new = diff_lines(k8_index_new, head_t)
d_base = diff_lines(base8, base_t)
chk(d_new == d_base,
    'index.html: дифф(новый kip8, kip8test HEAD) == базовому репо-диффу '
    '(%d строк против %d)' % (len(d_new), len(d_base)))
d_task8 = diff_lines(base8, k8_index_new)
d_taskT = diff_lines(base_t, head_t)
chk(d_task8 == d_taskT,
    'index.html: дифф задач (487-489) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 2. sw.js — шапка kip8 + перенос-метка + 3 комментария партии
#    дословно + v515; ТЕЛО от IMAGE-якоря идентично kip8test HEAD
# ============================================================
print('=== 2. sw.js ===')
P_SW = os.path.join(K8, 'sw.js')
sw8 = rd(P_SW)
swt = rd(os.path.join(K8T, 'sw.js'))

ANCHOR_IMG_8 = "const IMAGE_CACHE_VERSION = 'kipia-images-v3';"
ANCHOR_IMG_T = "const IMAGE_CACHE_VERSION = 'kipia-images-test-v3';"
chk(sw8.count(ANCHOR_IMG_8) == 1, 'sw.js (kip8): IMAGE-якорь найден')
chk(swt.count(ANCHOR_IMG_T) == 1, 'sw.js (kip8test): IMAGE-якорь найден')

# Извлечь 3 комментария партии: от '// Task 487:' до CACHE_VERSION
C_START = '// Task 487:'
i_c = swt.index(C_START)
i_cv_t = swt.index("const CACHE_VERSION = 'kipia-test-v713';")
BATCH_COMMENT = swt[i_c:i_cv_t]
chk(BATCH_COMMENT.endswith('\n')
    and BATCH_COMMENT.count('Task 487') == 1
    and BATCH_COMMENT.count('Task 488') == 1
    and BATCH_COMMENT.count('Task 489') == 1,
    'sw.js: извлечены 3 комментария партии (%d симв.)'
    % len(BATCH_COMMENT))
chk(V_TEST not in BATCH_COMMENT and 'kip8test' not in BATCH_COMMENT,
    'sw.js: комментарии партии версионно-нейтральны')
for m in ('СПРАВОЧНОЕ', 'onCellHover',              # 487
          'МАРКЕР ws-done-chk', 'docProps', '[Content_Types].xml',  # 488
          '_employeesColMap', 'дата_рождения', 'employeesSplitInit'):  # 489
    chk(m in BATCH_COMMENT, 'sw.js: маркер комментария %r' % (m,))

MARK = '// Task 487-489 (перенос партии из kip8test@58965654):\n'
old_v = "const CACHE_VERSION = 'kipia-v514';"
new_v = "const CACHE_VERSION = 'kipia-v515';"
chk(sw8.count(old_v) == 1, 'sw.js: CACHE_VERSION v514 найден')
sw_new = sw8.replace(old_v, MARK + BATCH_COMMENT + new_v)
chk(sw_new.count(new_v) == 1, 'sw.js: kipia-v515 ровно один')
chk('kipia-v514' not in sw_new, 'sw.js: kipia-v514 не осталось')
chk(sw_new.startswith(sw8[:sw8.index(old_v)]),
    'sw.js: шапка kip8 до CACHE_VERSION не изменена (история жива)')
chk(sw_new.count('kip8test') == sw8.count('kip8test') + 1,
    'sw.js: kip8test-упоминания = исторические + 1 перенос-метка')

# ТЕЛО: от IMAGE-якоря идентично kip8test HEAD (кроме имён кэшей)
pbn = os.path.join(TMP, 'k8-sw-body-new.js')
pbh = os.path.join(TMP, 'k8t-sw-body-head.js')
wr(pbn, sw_new[sw_new.index(ANCHOR_IMG_8):])
wr(pbh, swt[swt.index(ANCHOR_IMG_T):])
r = subprocess.run(['diff', pbn, pbh], capture_output=True, text=True)
body_diffs = [ln for ln in r.stdout.splitlines()
              if (ln.startswith('<') or ln.startswith('>'))
              and 'kipia-data' not in ln and 'kipia-images' not in ln]
chk(body_diffs == [], 'sw.js: ТЕЛО идентично kip8test HEAD (%d расхожд.)'
    % len(body_diffs))
wr(P_SW, sw_new)

# Дистанции якорей против НОВЫХ окон тестов (значения kip8test
# HEAD: 461→11600, 471→9000, 472→8500, 473→8200, 474→8000,
# 478/479→6500, 483/484→3900, 485→4100, 486→3400; НО геометрия
# шапки kip8 отличается: блок 478-481 (переносной формат) на
# +198 симв. дальше от версии, чем в kip8test — окна 480/481/482
# получают kip8-специфичное значение 6600 вместо 5000 (ЧАСТЬ 2,
# вместе с мета-ссылками 'i - 5000' в test-task482)
i_new_v = sw_new.index(new_v)
for task_no, window in ((486, 3400), (485, 4100), (484, 3900),
                        (483, 3900), (482, 6600), (481, 6600),
                        (480, 6600), (479, 6500), (478, 6500),
                        (473, 8200), (474, 8000), (472, 8500),
                        (471, 9000), (461, 11600)):
    i_task = sw_new.rindex('Task %d' % task_no, 0, i_new_v)
    dist = i_new_v - i_task
    chk(dist < window, 'sw.js: Task %d дистанция %d < окна %d (запас %d)'
        % (task_no, dist, window, window - dist))

# ============================================================
# 3. scripts/WorkSchedule.gs — копия kip8test HEAD (Task 489)
# ============================================================
print('=== 3. WorkSchedule.gs ===')
gs_t = git(K8T, 'show', '%s:scripts/WorkSchedule.gs' % HEAD_T)
chk('kip8test' not in gs_t,
    'WorkSchedule.gs: репо-специфики нет (kip8test не упоминается)')
chk(V_TEST not in gs_t, 'WorkSchedule.gs: kipia-test-v нет')
for m in ('_employeesColMap', '_wsShortFio', '_wsFullFio',
          'employeesSplitInit', 'дата_рождения', 'listEmployees',
          'addEmployee', 'updateEmployee', 'dismissEmployee',
          '_ppeLookupEmployee'):
    chk(m in gs_t, 'WorkSchedule.gs: маркер Task 489 %r' % (m,))
chk(rd(os.path.join(K8T, 'scripts', 'WorkSchedule.gs')) == gs_t,
    'WorkSchedule.gs: рабочая копия kip8test == HEAD')
wr(os.path.join(K8, 'scripts', 'WorkSchedule.gs'), gs_t)
chk(rd(os.path.join(K8, 'scripts', 'WorkSchedule.gs')) == gs_t,
    'WorkSchedule.gs: записан в kip8 байт-в-байт')

print('\n===== ЧАСТЬ 1 ЗАВЕРШЕНА: %d FAIL =====' % len(fail))
for m in fail:
    print('FAIL: %s' % m)
if fail:
    sys.exit(1)
print('Дальше: python3 scripts/task487-489-transfer2.py (tests/)')
