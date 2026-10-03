#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 470-transfer: перенос Task 470 (таблица «Плановых мероприятий»:
# точка в конце сокращения ноября «Ноя.», в группу «В конце месяца»
# добавлено мероприятие «Работы на следующий месяц», НОВАЯ группа
# «На текущий месяц» с мероприятием «Работы на месяц» — 10 строк/120
# ячеек; отметки Task 463 работают по наименованию из DOM) из
# kip8test@059dad05 в боевой kip8 ОДНИМ инкрементом SW kipia-v505 →
# v506 (регламент Task 441). КЛИЕНТ-ONLY: .gs не тронуты (Apps Script
# без изменений).
# Метод (Task 292/401-406/429/437/441-469): файловый синк +
# де-изоляция + «дифф диффов». Якоря де-изоляции скопированы ТОЧНО
# из task469-transfer.py — Task 470 изоляцию не трогала.
# ОДНОРАЗОВЫЙ: повторный прогон упадёт на якорях (470 подключён /
# v506 установлен) — лечение: git checkout -- . и один чистый прогон.
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
# 0. База партии: kip8test@3150dba9 (Task 469 ПЕРЕНОС — состояние,
#    синхронное kip8@c89dd32; далее 059dad05 — Task 470)
#    ↔ kip8@HEAD (c89dd32 — Task 469 docs)
# ============================================================
BASE_T = '3150dba9'   # Task 469 ПЕРЕНОС (docs) в kip8test
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == '059dad05',
    'база: kip8test HEAD = %s (Task 470, ожидался 059dad05)' % HEAD_T)
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_8 == 'c89dd32',
    'база: kip8 HEAD = %s (ожидался c89dd32 — Task 469 docs)'
    % HEAD_8)

# ============================================================
# 1. index.html — де-изоляция kip8test HEAD (Task 470 изоляцию не
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

# Маркеры партии 470 (таблица по заявке)
chk('<th>Ноя.</th>' in src and '<th>Ноя</th>' not in src,
    'index.html: ноябрь — «Ноя.» с точкой (Task 470)')
chk('<td class="pe-name">Работы на следующий месяц</td>' in src,
    'index.html: мероприятие «Работы на следующий месяц» (Task 470)')
chk('<tr class="pe-group"><td colspan="13">На текущий месяц</td></tr>'
    in src,
    'index.html: группа «На текущий месяц» (Task 470)')
chk('<td class="pe-name">Работы на месяц</td>' in src,
    'index.html: мероприятие «Работы на месяц» (Task 470)')
chk(src.count('<td class="pe-m"></td>') == 120,
    'index.html: 120 пустых ячеек месяцев (10 строк × 12)')
chk(src.count('<tr class="pe-group">') == 3,
    'index.html: 3 строки-группы (Task 470)')
chk('Task 470' in src,
    'index.html: маркер Task 470 в комментариях')
# Task 469 жив (описание раздела)
chk('<div class="pe-desc-lead">Периодические работы на участке КИП ИОС, '
    'выполняемые в начале и в конце каждого месяца.</div>' in src,
    'index.html: вводный абзац Task 469 жив')
# Раскладка Task 468 жива
chk('.pe-layout {' in src and 'display: flex' in
    src[src.index('.pe-layout {'):src.index('.pe-layout {') + 200],
    'index.html: контейнер раскладки .pe-layout (flex) — Task 468')
# Task 467/466/464 живы
chk('.wspprev-frame.wsev-prev-frame { width: 794px; }' in src,
    'index.html: CSS-правило wsev-prev-frame 794px (Task 467 жив)')
chk('#wsEventsPanel .ws-bar-print { right: 27px; }' in src,
    'index.html: печать слева (27px) — Task 466 жив')
chk('.pe-col-name { width: auto; }' in src,
    'index.html: колонка наименований по тексту (Task 464 жив)')

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» ---
base_t = '/tmp/k8t-index-base470.html'
base8 = '/tmp/k8-index-base470.html'
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
    'index.html: дифф задач (470) идентичен в обоих репо '
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
    chk(m in code, 'Code.gs (kip8): маркер %r жив (470 не трогал)' % m[:40])

# ============================================================
# 3. tests/ — копия с маппингом версий
# ============================================================
print('=== 3. tests/ ===')
TDIR_T = os.path.join(K8T, 'tests')
TDIR_8 = os.path.join(K8, 'tests')
MAP = [
    # текущие ассерты (бамп партии 470 — в kip8 ОДИН инкремент)
    ('kipia-test-v694', 'kipia-v506'),
    # guards следующей версии
    ('kipia-test-v695', 'kipia-v507'),
    # негатив партии 470: «версия до партии» в kip8 — v505
    ('kipia-test-v693', 'kipia-v505'),
    # негатив партии 469: «версия до партии» в kip8 — v504
    ('kipia-test-v692', 'kipia-v504'),
    # негатив партии 468: «версия до партии» в kip8 — v503
    ('kipia-test-v691', 'kipia-v503'),
    # негатив партии 467: «версия до партии» в kip8 — v502
    ('kipia-test-v690', 'kipia-v502'),
    # негативы партии 466: «версия до партии» в kip8 — v501
    ('kipia-test-v689', 'kipia-v501'),
    # кэш картинок kip8 (без -test-)
    ('kipia-images-test-v3', 'kipia-images-v3'),
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
chk(tot.get('kipia-test-v694', 0) > 450,
    'тесты: текущие ассерты v694 → v506 перекрыты (%d)'
    % tot.get('kipia-test-v694', 0))
chk(tot.get('kipia-test-v695', 0) > 100,
    'тесты: guards v695 → v507 перекрыты (%d)'
    % tot.get('kipia-test-v695', 0))
chk(tot.get('kipia-test-v693', 0) == 1,
    'тесты: негатив партии v693 → v505 ровно один (test-task470, %d)'
    % tot.get('kipia-test-v693', 0))
chk(tot.get('kipia-test-v692', 0) == 1,
    'тесты: негатив партии 469 v692 → v504 ровно один (test-task469, %d)'
    % tot.get('kipia-test-v692', 0))
chk(tot.get('kipia-test-v691', 0) == 1,
    'тесты: негатив партии 468 v691 → v503 ровно один (test-task468, %d)'
    % tot.get('kipia-test-v691', 0))
chk(tot.get('kipia-test-v690', 0) == 1,
    'тесты: негатив партии 467 v690 → v502 ровно один (test-task467, %d)'
    % tot.get('kipia-test-v690', 0))
chk(tot.get('kipia-test-v689', 0) == 2,
    'тесты: негативы партии 466 v689 → v501 ровно два (test-task465 + '
    'test-task466, %d)' % tot.get('kipia-test-v689', 0))

# новые тест-файлы партии — в kip8, с замапленными версиями
p470 = os.path.join(TDIR_8, 'test-task470.js')
chk(os.path.exists(p470), 'test-task470.js скопирован в kip8')
s470 = rd(p470)
for m in ("CACHE_VERSION = 'kipia-v506'", "indexOf('kipia-v505') === -1",
          'Работы на следующий месяц', 'На текущий месяц',
          'const IMAGE_CACHE_VERSION = \'kipia-images-v3\';'):
    chk(m in s470, 'test-task470.js: маркер %r замаплен' % (m[:44],))
chk('kipia-test-v' not in s470,
    'test-task470.js: kip8test-версий не осталось')
s460 = rd(os.path.join(TDIR_8, 'test-task460.js'))
chk("'Ноя.', 'Дек.']" in s460 and 'Работы на следующий месяц' in s460,
    'test-task460.js: адаптация 470 (Ноя./10 мероприятий) пришла')

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

# 3.1 test-task344.js (kip8-специфичный) — бамп v505→v506
P344 = os.path.join(TDIR_8, 'test-task344.js')
s = rd(P344)
n = s.count('kipia-v505')
chk(n == 3, 'test-task344.js: ассертов kipia-v505 = 3 (%d)' % n)
s = s.replace('kipia-v505', 'kipia-v506')
wr(P344, s)

# 3.2 run-all.js (kip8) — + require test-task470 после 469
RA = os.path.join(TDIR_8, 'run-all.js')
s = rd(RA)
A = "require('./test-task469.js');\n"
B = "require('./test-task469.js');\nrequire('./test-task470.js');\n"
chk(s.count(A) == 1, "run-all.js: якорь test-task469 найден (%d)" % s.count(A))
chk('test-task470' not in s, 'run-all.js (kip8): 470 ещё не подключён')
s = s.replace(A, B)
for n_ in range(438, 471):
    if n_ == 437:
        continue
    chk("require('./test-task%d.js');" % n_ in s,
        'run-all.js: test-task%d подключён' % n_)
chk("require('./test-task344.js');" in s,
    'run-all.js (kip8): test-task344 подключён (перенос 459 жив)')
wr(RA, s)

# 3.3 после всего: kipia-v505 в тестах kip8 — ТОЛЬКО негатив партии 470
left505 = {name: rd(os.path.join(TDIR_8, name)).count('kipia-v505')
           for name in sorted(os.listdir(TDIR_8))
           if name.startswith('test-') and
           'kipia-v505' in rd(os.path.join(TDIR_8, name))}
chk(left505 == {'test-task470.js': 1},
    'тесты kip8: kipia-v505 остался ТОЛЬКО в негативе партии 470: %s'
    % left505)

# ============================================================
# 4. sw.js — версия + комментарий партии
# ============================================================
print('=== 4. sw.js ===')
P = os.path.join(K8, 'sw.js')
s = rd(P)
old_v = "const CACHE_VERSION = 'kipia-v505';"
new_v = "const CACHE_VERSION = 'kipia-v506';"
chk(s.count(old_v) == 1, 'sw.js: CACHE_VERSION v505 найден (%d)'
    % s.count(old_v))
COMMENT = (
    '// Task 470 (перенос из kip8test@059dad05): таблица «Плановых\n'
    '// мероприятий» — точка в конце сокращения ноября «Ноя.», в группу\n'
    '// «В конце месяца» добавлено мероприятие «Работы на следующий\n'
    '// месяц», новая группа «На текущий месяц» с мероприятием\n'
    '// «Работы на месяц».\n'
)
if 'Task 470' not in s:
    s = s.replace(old_v, COMMENT + new_v)
chk("const CACHE_VERSION = 'kipia-v506';" in s, 'sw.js: v506 установлен')
chk(s.count('kipia-v506') == 1, 'sw.js: маркер v506 один (%d)'
    % s.count('kipia-v506'))
chk('Task 470' in s, 'sw.js: комментарий партии упоминает Task 470')
chk('«Ноя.»' in s, 'sw.js: комментарий упоминает точку сокращения')
chk('На текущий месяц' in s,
    'sw.js: комментарий упоминает новую группу')
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
print('=== 5. DEPLOY-Task470 (копия из kip8test) ===')
dep = 'DEPLOY-Task470-plan-events-november-dot-new-rows.md'
wr(os.path.join(K8, dep), rd(os.path.join(K8T, dep)))
chk(os.path.exists(os.path.join(K8, dep)), '%s скопирован в kip8' % dep)

print()
print('=== ИТОГ ===')
if fail:
    print('ПРОВАЛЕНО %d:' % len(fail))
    for m in fail:
        print('  - %s' % m)
    sys.exit(1)
print('ВСЁ ОК: Task 470 перенесён в kip8 (SW kipia-v506), '
    'клиент-only, серверных шагов нет')
