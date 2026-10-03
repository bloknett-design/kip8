#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 468-transfer: перенос Task 468 (раскладка раздела «Плановые
# мероприятия»: таблица влево экрана строго по контенту — столбец
# «Мероприятия» по самому длинному тексту; справа окно «Описание
# раздела» с описанием и функционалом; < 1200px описание под
# таблицей) из kip8test@68e8fdbc в боевой kip8 ОДНИМ инкрементом
# SW kipia-v503 → v504 (регламент Task 441). КЛИЕНТ-ONLY: .gs не
# тронуты (Apps Script без изменений).
# Метод (Task 292/401-406/429/437/441-467): файловый синк +
# де-изоляция + «дифф диффов». Якоря де-изоляции скопированы ТОЧНО
# из task467-transfer.py (якоря 243/458/284/242, подводные камни
# учтены) — Task 468 изоляцию не трогала.
# ОДНОРАЗОВЫЙ: повторный прогон упадёт на якорях (468 подключён /
# v504 установлен) — лечение: git checkout -- . и один чистый прогон.
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
# 0. База партии: kip8test@fce2a778 (Task 467 ПЕРЕНОС —
#    состояние, синхронное kip8@83aa340; далее 68e8fdbc — Task 468)
#    ↔ kip8@HEAD (83aa340 — Task 467 перенос)
# ============================================================
BASE_T = 'fce2a778'   # Task 467 ПЕРЕНОС (docs) в kip8test
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == '68e8fdbc',
    'база: kip8test HEAD = %s (Task 468, ожидался 68e8fdbc)' % HEAD_T)
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_8 == '83aa340',
    'база: kip8 HEAD = %s (ожидался 83aa340 — Task 467 перенос)'
    % HEAD_8)

# ============================================================
# 1. index.html — де-изоляция kip8test HEAD (Task 468 изоляцию не
#    трогала — якоря прежние, применяются к текущему HEAD)
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

assert src != orig, 'index.html: ни одной трансформации не применилась'
# 4 исторических (Task 243/284/274/кэш СЖ) + 1 комментарий PlanEventsData
chk(src.count('kip8test') == 5,
    'index.html: упоминаний kip8test после де-изоляции = 5 '
    '(4 исторических + 1 комментарий PlanEventsData про общий '
    'бэкенд): %d' % src.count('kip8test'))
chk(src.count(V_TEST) == 0,
    'index.html: строк kipia-test-v нет: %d' % src.count(V_TEST))

# Маркеры партии 468 (раскладка раздела)
chk('.pe-layout {' in src and 'display: flex' in
    src[src.index('.pe-layout {'):src.index('.pe-layout {') + 200],
    'index.html: контейнер раскладки .pe-layout (flex) — Task 468')
chk('<aside class="pe-desc-card" aria-label="Описание раздела">' in src,
    'index.html: окно описания aside.pe-desc-card — Task 468')
chk('Task 468' in src,
    'index.html: маркер Task 468 в комментариях')
# min-width: 100% удалён из .pe-table (ширина по контенту)
pe_tbl = src[src.index('.pe-table {'):src.index('.pe-table {') + 600]
pe_tbl_nc = re.sub(r'/\*[\s\S]*?\*/', '', pe_tbl)
chk('min-width' not in pe_tbl_nc and 'max-content' in pe_tbl_nc,
    'index.html: .pe-table без min-width (по контенту) — ядро заявки 468')
chk('.pe-layout .pe-card {' in src and 'flex: 0 0 auto' in src,
    'index.html: карточка таблицы flex: 0 0 auto (влево, не сжимается)')
chk('@media (max-width: 1199px)' in src,
    'index.html: медиа-запрос < 1200px (описание под таблицей)')
# Task 467/466/465 живы
chk('.wspprev-frame.wsev-prev-frame { width: 794px; }' in src,
    'index.html: CSS-правило wsev-prev-frame 794px (Task 467 жив)')
chk('#wsEventsPanel .ws-bar-print { right: 27px; }' in src,
    'index.html: печать слева (27px) — Task 466 жив')
chk('.pe-col-name { width: auto; }' in src,
    'index.html: колонка наименований по тексту (Task 464 жив)')

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» ---
base_t = '/tmp/k8t-index-base468.html'
base8 = '/tmp/k8-index-base468.html'
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
    'index.html: дифф задач (468) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 2. scripts/*.gs — партия КЛИЕНТ-ONLY: общие модули не тронуты,
#    проверка синхронности (никаких копий — новых .gs нет)
# ============================================================
print('=== 2. scripts/*.gs (не тронуты) ===')
for gs in ('WorkSchedule.gs', 'PPEInit.gs', 'RoleMatrix.gs',
           'RoleMatrixGate.gs', 'PlanEvents.gs', 'PlanEventsInit.gs'):
    p8 = os.path.join(K8, 'scripts', gs)
    pt = os.path.join(K8T, 'scripts', gs)
    head8 = git(K8, 'show', 'HEAD:scripts/' + gs)
    chk(rd(p8) == head8,
        '%s: kip8-версия == HEAD (партия не трогала)' % gs)
    chk(rd(pt) == head8,
        '%s: kip8test HEAD == kip8 HEAD (синхронны)' % gs)

# Code.gs — kip8-версия (исторически отличается от kip8test-эталона):
# партия не добавляла case; проверяем, что kip8-версия на месте
code = rd(os.path.join(K8, 'scripts', 'Code.gs'))
for m in ("case 'planEvents.list':", "case 'planEvents.mark':",
          "case 'planEvents.update':", "case 'planEvents.unmark':",
          'PlanEvents (Task 463/464)'):
    chk(m in code, 'Code.gs (kip8): маркер %r жив (468 не трогал)' % m[:40])

# ============================================================
# 3. tests/ — копия с маппингом версий
# ============================================================
print('=== 3. tests/ ===')
TDIR_T = os.path.join(K8T, 'tests')
TDIR_8 = os.path.join(K8, 'tests')
MAP = [
    # текущие ассерты (бамп партии 468 — в kip8 ОДИН инкремент)
    ('kipia-test-v692', 'kipia-v504'),
    # guards следующей версии
    ('kipia-test-v693', 'kipia-v505'),
    # негатив партии 468: «версия до партии» в kip8 — v503
    ('kipia-test-v691', 'kipia-v503'),
    # негатив партии 467: «версия до партии» в kip8 — v502
    ('kipia-test-v690', 'kipia-v502'),
    # негативы партии 466: «версия до партии» в kip8 — v501
    ('kipia-test-v689', 'kipia-v501'),
    # исторические негативы (маппинг переносов 463-464/460-462/
    # 456-459/441-442)
    ('kipia-test-v687', 'kipia-v499'),
    ('kipia-test-v685', 'kipia-v498'),   # негатив task462 (×1)
    ('kipia-test-v684', 'kipia-v498'),   # негатив task461 (×3)
    ('kipia-test-v683', 'kipia-v498'),   # негатив task460 (×1)
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
chk(tot.get('kipia-test-v692', 0) > 450,
    'тесты: текущие ассерты v692 → v504 перекрыты (%d)'
    % tot.get('kipia-test-v692', 0))
chk(tot.get('kipia-test-v693', 0) > 100,
    'тесты: guards v693 → v505 перекрыты (%d)'
    % tot.get('kipia-test-v693', 0))
chk(tot.get('kipia-test-v691', 0) == 1,
    'тесты: негатив партии v691 → v503 ровно один (test-task468, %d)'
    % tot.get('kipia-test-v691', 0))
chk(tot.get('kipia-test-v690', 0) == 1,
    'тесты: негатив партии 467 v690 → v502 ровно один (test-task467, %d)'
    % tot.get('kipia-test-v690', 0))
chk(tot.get('kipia-test-v689', 0) == 2,
    'тесты: негативы партии 466 v689 → v501 ровно два (test-task465 + '
    'test-task466, %d)' % tot.get('kipia-test-v689', 0))

# новые тест-файлы партии — в kip8, с замапленными версиями
p468 = os.path.join(TDIR_8, 'test-task468.js')
chk(os.path.exists(p468), 'test-task468.js скопирован в kip8')
s468 = rd(p468)
for m in ("CACHE_VERSION = 'kipia-v504'", "indexOf('kipia-v503') === -1",
          'pe-desc-card', 'Task 468'):
    chk(m in s468, 'test-task468.js: маркер %r замаплен' % (m[:44],))
chk('kipia-test-v' not in s468,
    'test-task468.js: kip8test-версий не осталось')
s467 = rd(os.path.join(TDIR_8, 'test-task467.js'))
chk("CACHE_VERSION = 'kipia-v504'" in s467 and
    "indexOf('kipia-v502') === -1" in s467,
    'test-task467.js: ассерты 467 подняты до v504 (текущая), негатив v502')
# фикс окна комментария Task 461 пришёл из kip8test (2000 → 2500)
s461 = rd(os.path.join(TDIR_8, 'test-task461.js'))
chk('i - 2500' in s461,
    'test-task461.js: окно комментария Task 461 расширено до 2500 '
    '(комментарий Task 468 отодвинул)')

# остатки kipia-test-v6xx в kip8 после маппинга — только исторические
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
    'тесты kip8: незамапленные kipia-test-v6xx отсутствуют: %s' % bad_hist)
print('  исторические kipia-test-v* (общие, не тронуты): %s'
      % dict(sorted(hist.items())))

# 3.1 test-task344.js (kip8-специфичный) — бамп v503→v504
P344 = os.path.join(TDIR_8, 'test-task344.js')
s = rd(P344)
n = s.count('kipia-v503')
chk(n == 3, 'test-task344.js: ассертов kipia-v503 = 3 (%d)' % n)
s = s.replace('kipia-v503', 'kipia-v504')
wr(P344, s)

# 3.2 run-all.js (kip8) — + require test-task468 после 467
RA = os.path.join(TDIR_8, 'run-all.js')
s = rd(RA)
A = "require('./test-task467.js');\n"
B = "require('./test-task467.js');\nrequire('./test-task468.js');\n"
chk(s.count(A) == 1, "run-all.js: якорь test-task467 найден (%d)" % s.count(A))
chk('test-task468' not in s, 'run-all.js (kip8): 468 ещё не подключён')
s = s.replace(A, B)
for n_ in range(438, 469):
    if n_ == 437:
        continue
    chk("require('./test-task%d.js');" % n_ in s,
        'run-all.js: test-task%d подключён' % n_)
chk("require('./test-task344.js');" in s,
    'run-all.js (kip8): test-task344 подключён (перенос 459 жив)')
wr(RA, s)

# 3.3 после всего: kipia-v503 в тестах kip8 — ТОЛЬКО негатив партии 468
left503 = {name: rd(os.path.join(TDIR_8, name)).count('kipia-v503')
           for name in sorted(os.listdir(TDIR_8))
           if name.startswith('test-') and
           'kipia-v503' in rd(os.path.join(TDIR_8, name))}
chk(left503 == {'test-task468.js': 1},
    'тесты kip8: kipia-v503 остался ТОЛЬКО в негативе партии 468: %s'
    % left503)

# ============================================================
# 4. sw.js — версия + комментарий партии
# ============================================================
print('=== 4. sw.js ===')
P = os.path.join(K8, 'sw.js')
s = rd(P)
old_v = "const CACHE_VERSION = 'kipia-v503';"
new_v = "const CACHE_VERSION = 'kipia-v504';"
chk(s.count(old_v) == 1, 'sw.js: CACHE_VERSION v503 найден (%d)'
    % s.count(old_v))
COMMENT = (
    '// Task 468 (перенос из kip8test@68e8fdbc): «Плановые '
    'мероприятия» —\n'
    '// раскладка раздела: таблица влево экрана (столбец «Мероприятия» '
    'по\n'
    '// самому длинному тексту, без растяжения), справа на всё '
    'оставшееся\n'
    '// место окно «Описание раздела» (pe-layout/pe-desc-card); на '
    '< 1200px\n'
    '// описание под таблицей.\n'
)
if 'Task 468' not in s:
    s = s.replace(old_v, COMMENT + new_v)
chk("const CACHE_VERSION = 'kipia-v504';" in s, 'sw.js: v504 установлен')
chk(s.count('kipia-v504') == 1, 'sw.js: маркер v504 один (%d)'
    % s.count('kipia-v504'))
chk('Task 468' in s, 'sw.js: комментарий партии упоминает Task 468')
chk('pe-desc-card' in s,
    'sw.js: комментарий упоминает класс окна описания')
chk(s.count('слева от раскрытия') == 1,
    'sw.js: строка Task 465 — живое направление «слева» (%d)'
    % s.count('слева от раскрытия'))
chk(len(COMMENT) < 2000,
    'sw.js: комментарий партии %d символов (< 2000 — окно test-task461)'
    % len(COMMENT))
wr(P, s)

# ============================================================
# 5. DEPLOY-док партии — копия из kip8test
# ============================================================
print('=== 5. DEPLOY-Task468 (копия из kip8test) ===')
dep = 'DEPLOY-Task468-plan-events-layout-desc-window.md'
wr(os.path.join(K8, dep), rd(os.path.join(K8T, dep)))
chk(os.path.exists(os.path.join(K8, dep)), '%s скопирован в kip8' % dep)

print()
print('=== ИТОГ ===')
if fail:
    print('ПРОВАЛЕНО %d:' % len(fail))
    for m in fail:
        print('  - %s' % m)
    sys.exit(1)
print('ВСЁ ОК: Task 468 перенесён в kip8 (SW kipia-v504), '
    'клиент-only, серверных шагов нет')
