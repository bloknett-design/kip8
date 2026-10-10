#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 490-492-transfer ЧАСТЬ 1: перенос партии 490+491+492 из kip8test
# (@ae8cbd34 HEAD; фичи 9007624c/49ca069f/a78f1b1e — docs-коммиты код
# не трогали; авто-коммиты 82e91c38/5238816d трогали только data/*.json)
# в боевой kip8 ОДНИМ инкрементом SW kipia-v515 → v516 (регламент
# Task 441; команда пользователя: «Перенос в kip8»).
# Партия: «Датчики температуры» мобильная версия — сетка 2-в-ряд
# (490), пары 50М+50М/100М+100М + featured + автотаб «Избранное»
# (491), нижний бар табов + единый крупный шрифт + feat=isFav (492).
# index.html: wholesale де-изоляция ×16 rep1/17 якорей (партия
# изоляцию НЕ трогала — каждый rep1 проверяет счётчик); «дифф
# диффов» сходится (репо-дифф == базовому, дифф задач ==
# кip8test-диффу). sw.js: шапка kip8 + перенос-метка + 3 комментария
# партии ДОСЛОВНО (1263 симв., версионно-нейтральны) + kipia-v516;
# ТЕЛО от IMAGE-якоря идентично kip8test HEAD. WorkSchedule.gs —
# партия не трогала (проверка). ЧАСТЬ 2 (tests/) — отдельным скриптом.
# ОДНОРАЗОВЫЙ: лечение при сбое — git checkout -- . + чистый прогон
# (вывод В ФАЙЛ, не через пайпы!).
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
    # изоляция; прецедент task482-484/486/487-489-transfer.py)
    r = subprocess.run(['diff', p1, p2], capture_output=True, text=True)
    return [ln for ln in r.stdout.splitlines()
            if ln.startswith('<') or ln.startswith('>')]


# ============================================================
# 0. База: kip8test HEAD = ae8cbd34 (docs поверх фичи a78f1b1e),
#    код партии начинался от 58965654 (== 82e91c38 == 16984e77
#    по index.html/sw.js — docs/auto-коммиты код не трогали);
#    kip8 HEAD = e5e21a1 (авто-коммиты данных; код с ddd7878
#    не менялся — 487-489 последний перенесённый), деревья чистые
# ============================================================
print('=== 0. База ===')
BASE_T = '58965654'   # kip8test до партии (post-487-489 docs)
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == 'ae8cbd34', 'база: kip8test HEAD = %s (ожидался ae8cbd34)'
    % HEAD_T)
chk(git(K8T, 'show', '%s:index.html' % HEAD_T) ==
    git(K8T, 'show', '%s:index.html' % 'a78f1b1e'),
    'база: index.html в docs-коммитах не менялся (== фиче 492)')
chk(git(K8T, 'show', '%s:sw.js' % HEAD_T) ==
    git(K8T, 'show', '%s:sw.js' % 'a78f1b1e'),
    'база: sw.js в docs-коммитах не менялся')
for c in ('82e91c38', '16984e77'):
    chk(git(K8T, 'show', '%s:index.html' % c) ==
        git(K8T, 'show', '%s:index.html' % BASE_T),
        'база: index.html @%s == базе (авто/docs код не трогали)' % c)
    chk(git(K8T, 'show', '%s:sw.js' % c) ==
        git(K8T, 'show', '%s:sw.js' % BASE_T),
        'база: sw.js @%s == базе' % c)
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_8 == 'e5e21a1', 'база: kip8 HEAD = %s (ожидался e5e21a1)' % HEAD_8)
chk(git(K8, 'diff', '--stat', 'ddd7878..HEAD', '--', 'index.html',
        'sw.js', 'tests/', 'scripts/WorkSchedule.gs') == '',
    'база: код kip8 HEAD == ddd7878 (авто-коммиты — только data/)')
st = git(K8, 'status', '--porcelain').strip()
noise = [ln for ln in st.splitlines() if ln.startswith('??')
         and ('task490-492' in ln or '__pycache__' in ln)]
real = [ln for ln in st.splitlines() if ln not in noise]
chk(not real, 'kip8: рабочее дерево чистое: %r' % (real[:4],))

# ============================================================
# 1. index.html — де-изоляция kip8test HEAD (16 rep1 / 17 якорей;
#    партия изоляцию не трогала — прецедент 487-489) + «дифф диффов»
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

# Маркеры партии 490-492 (клиент-only: temp-sensors)
for m in ('Task 490', 'Task 491', 'Task 492',
          'tsBottomBar', 'ts-bottom-bar',          # 492: нижний бар
          'ts-card-feat', 'renderTempSensorCards',  # 491/492: карточки
          'setTempSensorsTab', 'TempFav',           # 491: автотаб
          'cu50_1428', 'cu50_1426', 'cu100_1428', 'cu100_1426',
          'targetTab491'):                          # 490/491: каталог+flow
    chk(m in src, 'index.html: маркер партии %r' % (m,))
# Живые задачи прошлых партий — не размыло переносом
for m in ('function devPprStatusClass',       # 478-481
          '_barExpMaxH', 'evStateCls',        # 482
          'var KipDB = (function() {', 'var KipPreload = (function() {',
          '_schedulePreload', '_startOfflineTokenRetry',
          'silentRefresh',                      # 486
          '_wsXlsDocProps', '_wsTabelRows',     # 488
          'onCellHover', '_openHoverPopup'):     # 487 (489 — gs-only)
    chk(m in src, 'index.html: якорь живой задачи %r' % (m,))

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» ---
TMP = '/home/z/my-project/scripts/.k8t-490-492-tmp'
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
    'index.html: дифф задач (490-492) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 2. sw.js — шапка kip8 + перенос-метка + 3 комментария партии
#    дословно + v516; ТЕЛО от IMAGE-якоря идентично kip8test HEAD
# ============================================================
print('=== 2. sw.js ===')
P_SW = os.path.join(K8, 'sw.js')
sw8 = rd(P_SW)
swt = rd(os.path.join(K8T, 'sw.js'))

ANCHOR_IMG_8 = "const IMAGE_CACHE_VERSION = 'kipia-images-v3';"
ANCHOR_IMG_T = "const IMAGE_CACHE_VERSION = 'kipia-images-test-v3';"
chk(sw8.count(ANCHOR_IMG_8) == 1, 'sw.js (kip8): IMAGE-якорь найден')
chk(swt.count(ANCHOR_IMG_T) == 1, 'sw.js (kip8test): IMAGE-якорь найден')

# Извлечь 3 комментария партии: от '// Task 490:' до CACHE_VERSION
C_START = '// Task 490:'
i_c = swt.index(C_START)
i_cv_t = swt.index("const CACHE_VERSION = 'kipia-test-v716';")
BATCH_COMMENT = swt[i_c:i_cv_t]
chk(BATCH_COMMENT.endswith('\n')
    and BATCH_COMMENT.count('Task 490') == 1
    and BATCH_COMMENT.count('Task 491') == 1
    and BATCH_COMMENT.count('Task 492') == 1,
    'sw.js: извлечены 3 комментария партии (%d симв.)'
    % len(BATCH_COMMENT))
chk(V_TEST not in BATCH_COMMENT and 'kip8test' not in BATCH_COMMENT,
    'sw.js: комментарии партии версионно-нейтральны')
for m in ('по ДВЕ в строке', 'ТХК (L) вместе',   # 490
          'ts-card-feat', 'FlowmeterData.init', 'Избранные',  # 491
          'ts-bottom-bar', 'смещены ВНИЗ', 'В ИЗБРАННОМ'):    # 492
    chk(m in BATCH_COMMENT, 'sw.js: маркер комментария %r' % (m,))

MARK = '// Task 490-492 (перенос партии из kip8test@ae8cbd34):\n'
old_v = "const CACHE_VERSION = 'kipia-v515';"
new_v = "const CACHE_VERSION = 'kipia-v516';"
chk(sw8.count(old_v) == 1, 'sw.js: CACHE_VERSION v515 найден')
sw_new = sw8.replace(old_v, MARK + BATCH_COMMENT + new_v)
chk(sw_new.count(new_v) == 1, 'sw.js: kipia-v516 ровно один')
chk('kipia-v515' not in sw_new, 'sw.js: kipia-v515 не осталось')
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

# Дистанции якорей против окон тестов kip8test (значения kip8test HEAD:
# 461→12400, 471→9800, 472→9300, 473→9000, 474→8800/9000, 478/479→7300,
# 480→6800, 481→6000(ctx; kip8-геометрия 6230 — ЧАСТЬ 2 ставит 6600,
# здесь проверяем против 6600), 482→6100, 483→5400, 484→5500, 485→5100,
# 486→4400, 488→3200; kip8-дистанции на ~1000-1500 МЕНЬШЕ kip8test —
# вставка MARK+комментариев (~1320) поглощается запасом окон
i_new_v = sw_new.index(new_v)
for task_no, window in ((488, 3200), (486, 4400), (485, 5100),
                        (484, 5500), (483, 5400), (482, 6100),
                        (481, 6600), (480, 6800), (479, 7300),
                        (478, 7300), (474, 8800), (473, 9000),
                        (472, 9300), (471, 9800), (461, 12400)):
    i_task = sw_new.rindex('Task %d' % task_no, 0, i_new_v)
    dist = i_new_v - i_task
    chk(dist < window, 'sw.js: Task %d дистанция %d < окна %d (запас %d)'
        % (task_no, dist, window, window - dist))

# ============================================================
# 3. scripts/WorkSchedule.gs — партия НЕ трогала (клиент-only);
#    проверка: остаётся как есть (идентичен с прошлым переносом)
# ============================================================
print('=== 3. WorkSchedule.gs ===')
gs_t = git(K8T, 'show', '%s:scripts/WorkSchedule.gs' % HEAD_T)
chk(gs_t == rd(os.path.join(K8, 'scripts', 'WorkSchedule.gs')),
    'WorkSchedule.gs: kip8 == kip8test HEAD (партия не трогала, '
    'копирования не требуется)')
chk(git(K8T, 'diff', '--stat', '%s..HEAD' % BASE_T, '--',
        'scripts/WorkSchedule.gs') == '',
    'WorkSchedule.gs: в партии 490-492 не менялся')

print('\n===== ЧАСТЬ 1 ЗАВЕРШЕНА: %d FAIL =====' % len(fail))
for m in fail:
    print('FAIL: %s' % m)
if fail:
    sys.exit(1)
print('Дальше: python3 scripts/task490-492-transfer2.py (tests/)')
