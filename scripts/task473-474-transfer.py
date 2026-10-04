#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 473-474-transfer: перенос ПАРТИИ Tasks 473+474 из kip8test
# (@145925a5 Task 473 + @d9efdd0f Task 474) в боевой kip8 ОДНИМ
# инкрементом SW kipia-v508 → v509 (регламент Task 441: партия =
# один инкремент; команда пользователя «Перенеси изменения в
# боевой kip8» получена в заявке Task 474 — Task 473 ждал переноса
# «по команде» с прошлой сессии).
# Состав партии:
#   Task 473 — график ППР «Приборы» (Графики КИП ИОС, только
#              десктоп): КОРНЕВОЙ фикс зрительной невидимости
#              столбцов (align-items:flex-end → stretch, все
#              столбцы были 2px из 165px) + значение над КАЖДЫМ
#              столбцом каждого месяца + ВСПОМОГАТЕЛЬНАЯ ПРАВАЯ
#              ОСЬ 0–50 для малых серий К/П (charts-desktop.js);
#   Task 474 — карточка прибора КИП ИОС: текст Типа ×1.5
#              (12px → 18px) + «№ прибора»/«Место установки» ниже
#              от верхней границы карточки (index.html, CSS).
# КЛИЕНТ-ONLY: .gs не тронуты (Apps Script без изменений).
# Метод (Task 292/401-406/429/437/441-472): файловый синк +
# де-изоляция + «дифф диффов». Якоря де-изоляции скопированы ТОЧНО
# из task472-transfer.py — партия изоляцию не трогала.
# ОДНОРАЗОВЫЙ: повторный прогон упадёт на якорях (473/474
# подключены / v509 установлен) — лечение: git checkout -- . + rm
# новых неотслеживаемых файлов партии (DEPLOY-Task474-*.md,
# scripts/task473-474-transfer.py) и один чистый прогон
# (подводный камень Task 471).
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
# 0. База партии: kip8test@1bf83f0d (Task 472 ПЕРЕНОС — состояние,
#    синхронное kip8@98797f3; далее 145925a5 (473) + d9efdd0f (474)
#    — партия) ↔ kip8@HEAD (98797f3 — Task 472 docs)
# ============================================================
BASE_T = '1bf83f0d'   # Task 472 ПЕРЕНОС (docs) в kip8test
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == 'd9efdd0f',
    'база: kip8test HEAD = %s (Task 474, ожидался d9efdd0f)' % HEAD_T)
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_8 == '98797f3',
    'база: kip8 HEAD = %s (ожидался 98797f3 — Task 472 docs)'
    % HEAD_8)

# ============================================================
# 1. index.html — де-изоляция kip8test HEAD (партия изоляцию не
#    трогала — якоря прежние, применяются к текущему HEAD;
#    Task 474 меняла только CSS карточки прибора)
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

# Маркеры партии 474 (index.html)
chk('Task 474 (заявка): текст типа прибора в ПОЛТОРА раза' in src,
    'index.html: комментарий Task 474 у оверлея Типа')
chk('font-size: 18px;  /* Task 474: было 12px — в полтора раза больше */'
    in src,
    'index.html: Тип ×1.5 — font-size 18px (Task 474)')
chk('padding-top: 12px;  /* Task 474: было 2px — ниже от верха карточки */'
    in src,
    'index.html: мета-блок 12px (Task 474)')
chk('Task 474 (заявка): тексты «№ прибора» и «Место установки»' in src,
    'index.html: комментарий Task 474 у мета-блока')
# Маркеры живых задач (472/471/470/469/468/464) — не размыло переносом
chk('<textarea id="peWorkInput" class="pe-works-input" rows="1"' in src,
    'index.html: textarea автороста (Task 472 жив)')
chk('background: #f0eee6;' in src,
    'index.html: бежевое окно светлой темы (Task 472 жив)')
chk('<th>Ноя.</th>' in src,
    'index.html: ноябрь «Ноя.» (Task 470 жив)')
chk('id="pePrevYearBtn"' in src,
    'index.html: кнопка предыдущего года (Task 471 жив)')
chk('var PlanWorksData = {' in src,
    'index.html: модуль PlanWorksData (Task 471 жив)')

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» ---
base_t = '/tmp/k8t-index-base473.html'
base8 = '/tmp/k8-index-base473.html'
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
    'index.html: дифф задач (474) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 1b. charts-desktop.js — Task 473: файл идентичен на базе в обоих
#     репо (diff base == 0), репо-специфичных строк нет — простая
#     копия + «дифф диффов»
# ============================================================
print('=== 1b. charts-desktop.js (Task 473) ===')
p_charts_t = os.path.join(K8T, 'charts-desktop.js')
p_charts_8 = os.path.join(K8, 'charts-desktop.js')
base_charts_t = '/tmp/k8t-charts-base473.js'
base_charts_8 = '/tmp/k8-charts-base473.js'
with io.open(base_charts_t, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', BASE_T + ':charts-desktop.js'))
with io.open(base_charts_8, 'w', encoding='utf-8') as f:
    f.write(git(K8, 'show', 'HEAD:charts-desktop.js'))
chk(diff_lines(base_charts_8, base_charts_t) == [],
    'charts-desktop.js: на базе партии файлы ИДЕНТИЧНЫ (синхронны)')
chk(rd(p_charts_t).count('kip8test') == 0 and
    V_TEST not in rd(p_charts_t),
    'charts-desktop.js: репо-специфичных строк нет')
wr(p_charts_8, rd(p_charts_t))
chk(rd(p_charts_8) == rd(p_charts_t),
    'charts-desktop.js: скопирован в kip8 (Task 473)')
# Маркеры Task 473
charts = rd(p_charts_8)
for m in ('align-items: stretch', '.ppr-bar-val-zero',
          '.ppr-y-axis-right', 'SECONDARY_SHARE',
          'Количество приборов по графику ППР по месяцам на 2026 год'):
    chk(m in charts, 'charts-desktop.js: маркер %r' % (m[:44],))

# ============================================================
# 2. scripts/*.gs — партия КЛИЕНТ-ONLY: серверные модули не
#    тронуты, проверка синхронности (никаких копий — новых .gs нет)
# ============================================================
print('=== 2. scripts/*.gs (не тронуты) ===')
for gs in ('WorkSchedule.gs', 'PPEInit.gs', 'RoleMatrix.gs',
           'RoleMatrixGate.gs', 'PlanEvents.gs', 'PlanEventsInit.gs',
           'PlanWorksInit.gs'):
    p8 = os.path.join(K8, 'scripts', gs)
    pt = os.path.join(K8T, 'scripts', gs)
    if not os.path.exists(p8) or not os.path.exists(pt):
        fail.append('%s: файл отсутствует' % gs)
        continue
    head8 = git(K8, 'show', 'HEAD:scripts/' + gs)
    chk(rd(p8) == head8,
        '%s: kip8-версия == HEAD (партия не трогала)' % gs)
    chk(rd(pt) == head8,
        '%s: kip8test HEAD == kip8 HEAD (синхронны)' % gs)

# Code.gs — kip8-версия (исторически отличается от kip8test-эталона):
# партия не добавляла case; проверяем, что kip8-версия на месте
code = rd(os.path.join(K8, 'scripts', 'Code.gs'))
for m in ("case 'planEvents.years':", "case 'planWorks.list':",
          "case 'planWorks.add':", "case 'planWorks.remove':",
          "case 'planWorks.setStatus':"):
    chk(m in code, 'Code.gs (kip8): роут %r жив (партия не трогала)' % m[:32])

# ============================================================
# 3. tests/ — копия с маппингом версий
# ============================================================
print('=== 3. tests/ ===')
TDIR_T = os.path.join(K8T, 'tests')
TDIR_8 = os.path.join(K8, 'tests')
MAP = [
    # текущие ассерты (бамп партии 473+474 — в kip8 ОДИН инкремент)
    ('kipia-test-v698', 'kipia-v509'),
    # guards следующей версии
    ('kipia-test-v699', 'kipia-v510'),
    # негатив партии 474: «версия до партии» в kip8 — v508
    # (assert + сообщение в test-task474 + шапка-комментарий файла,
    #  где «v697 → v698» превращается в корректное «v508 → v509»)
    ('kipia-test-v697', 'kipia-v508'),
    # негатив партии 473: партия покрывает 473 — «до партии» v508
    ('kipia-test-v696', 'kipia-v508'),
    # исторические негативы (маппинг переносов 472/471/470/469/468/
    # 467/466 — как в task472-transfer.py)
    ('kipia-test-v695', 'kipia-v507'),   # негатив task472 (×2)
    ('kipia-test-v694', 'kipia-v506'),   # негатив task471 (×2)
    ('kipia-test-v693', 'kipia-v505'),   # негатив task470 (×1)
    ('kipia-test-v692', 'kipia-v504'),   # негатив task469 (×1)
    ('kipia-test-v691', 'kipia-v503'),   # негатив task468 (×1)
    ('kipia-test-v690', 'kipia-v502'),   # негатив task467 (×1)
    ('kipia-test-v689', 'kipia-v501'),   # негативы 465/466 (×2)
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
chk(tot.get('kipia-test-v698', 0) > 500,
    'тесты: текущие ассерты v698 → v509 перекрыты (%d)'
    % tot.get('kipia-test-v698', 0))
chk(tot.get('kipia-test-v699', 0) > 100,
    'тесты: guards v699 → v510 перекрыты (%d)'
    % tot.get('kipia-test-v699', 0))
chk(tot.get('kipia-test-v697', 0) == 3,
    'тесты: v697 → v508 три (test-task474: негатив assert + сообщение '
    '+ шапка-комментарий «v508 → v509», %d)' % tot.get('kipia-test-v697', 0))
chk(tot.get('kipia-test-v696', 0) == 1,
    'тесты: негатив партии 473 v696 → v508 один (test-task473, %d)'
    % tot.get('kipia-test-v696', 0))

# новые тест-файлы партии — в kip8, с замапленными версиями
p473 = os.path.join(TDIR_8, 'test-task473.js')
chk(os.path.exists(p473), 'test-task473.js скопирован в kip8')
s473 = rd(p473)
for m in ("CACHE_VERSION = 'kipia-v509'", "indexOf('kipia-v508') === -1",
          'ppr-bar-val-zero', 'ppr-y-axis-right', 'align-items:stretch',
          '_niceMax'):
    chk(m in s473, 'test-task473.js: маркер %r замаплен' % (m[:44],))
chk('kipia-test-v' not in s473,
    'test-task473.js: kip8test-версий не осталось')

p474 = os.path.join(TDIR_8, 'test-task474.js')
chk(os.path.exists(p474), 'test-task474.js скопирован в kip8')
# Точечная адаптация под kip8-нумерацию: в шапке kip8test-файла
# «SW: kipia-test-v697 → v698.» маппинг заменяет полную форму
# («kipia-test-v697» → «kipia-v508»), но короткий хвост «v698»
# остаётся; названия тестов «v697/v698/v699» — kip8test-нумерация.
# Правим на семантику kip8 (партия = ОДИН инкремент v508 → v509)
s474 = rd(p474)
fixes = [
    ('//   SW: kipia-v508 → v698.', '//   SW: kipia-v508 → v509.'),
    ("'текущая версия v698'", "'текущая версия v509'"),
    ('версия до партии (v697) отсутствует',
     'версия до партии (v508) отсутствует'),
    ('v699 в sw.js отсутствует', 'v510 в sw.js отсутствует'),
]
for old_f, new_f in fixes:
    chk(s474.count(old_f) == 1,
        'test-task474.js: якорь адаптации %r найден (%d)'
        % (old_f[:40], s474.count(old_f)))
    s474 = s474.replace(old_f, new_f)
wr(p474, s474)
for m in ("CACHE_VERSION = 'kipia-v509'", "indexOf('kipia-v508') === -1",
          'font-size: 18px', 'padding-top: 12px',
          'SW: kipia-v508 → v509',
          "'текущая версия v509'",
          'версия до партии (v508) отсутствует',
          'v510 в sw.js отсутствует'):
    chk(m in s474, 'test-task474.js: маркер %r замаплен' % (m[:44],))
chk('kipia-test-v' not in s474,
    'test-task474.js: kip8test-версий не осталось')

# шапка test-task474: комментарий SW после адаптации корректен для kip8
chk('SW: kipia-v508 → v509' in s474,
    'test-task474.js: шапка «SW: kipia-v508 → v509» (партия — один '
    'инкремент)')

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

# 3.1 test-task344.js (kip8-специфичный) — бамп v508→v509
P344 = os.path.join(TDIR_8, 'test-task344.js')
s = rd(P344)
n = s.count('kipia-v508')
chk(n == 3, 'test-task344.js: ассертов kipia-v508 = 3 (%d)' % n)
s = s.replace('kipia-v508', 'kipia-v509')
wr(P344, s)

# 3.2 run-all.js (kip8) — + require test-task473/474 после 472
RA = os.path.join(TDIR_8, 'run-all.js')
s = rd(RA)
A = "require('./test-task472.js');\n"
B = ("require('./test-task472.js');\n"
     "require('./test-task473.js');\n"
     "require('./test-task474.js');\n")
chk(s.count(A) == 1, "run-all.js: якорь test-task472 найден (%d)" % s.count(A))
chk('test-task473' not in s and 'test-task474' not in s,
    'run-all.js (kip8): 473/474 ещё не подключены')
s = s.replace(A, B)
for n_ in range(438, 474):
    if n_ == 437:
        continue
    chk("require('./test-task%d.js');" % n_ in s,
        'run-all.js: test-task%d подключён' % n_)
chk("require('./test-task344.js');" in s,
    'run-all.js (kip8): test-task344 подключён (перенос 459 жив)')
wr(RA, s)

# 3.3 после всего: kipia-v508 в тестах kip8 — ТОЛЬКО партия 473+474
left508 = {name: rd(os.path.join(TDIR_8, name)).count('kipia-v508')
           for name in sorted(os.listdir(TDIR_8))
           if name.startswith('test-') and
           'kipia-v508' in rd(os.path.join(TDIR_8, name))}
chk(left508 == {'test-task473.js': 1, 'test-task474.js': 3},
    'тесты kip8: kipia-v508 остался ТОЛЬКО в партии 473+474 '
    '(473: негатив ×1; 474: негатив assert+сообщение ×2 + шапка '
    '«v508 → v509» ×1): %s' % left508)

# ============================================================
# 4. sw.js — версия + комментарий партии
# ============================================================
print('=== 4. sw.js ===')
P = os.path.join(K8, 'sw.js')
s = rd(P)
old_v = "const CACHE_VERSION = 'kipia-v508';"
new_v = "const CACHE_VERSION = 'kipia-v509';"
chk(s.count(old_v) == 1, 'sw.js: CACHE_VERSION v508 найден (%d)'
    % s.count(old_v))
COMMENT = (
    '// Task 473-474 (перенос партии из kip8test@d9efdd0f): Task 473 —\n'
    '// график ППР «Приборы»: столбцы были зрительно невидимы (2px) —\n'
    '// фикс + число над каждым столбцом + правая ось для К/П; Task 474 —\n'
    '// карточка прибора: Тип ×1.5 (12→18px), «№ прибора»/«Место\n'
    '// установки» ниже от верха карточки.\n'
)
if 'Task 473-474 (перенос партии' not in s:
    s = s.replace(old_v, COMMENT + new_v)
chk("const CACHE_VERSION = 'kipia-v509';" in s, 'sw.js: v509 установлен')
chk(s.count('kipia-v509') == 1, 'sw.js: маркер v509 один (%d)'
    % s.count('kipia-v509'))
chk('Task 473' in s and 'Task 474' in s,
    'sw.js: комментарий партии упоминает Tasks 473/474')
chk('правая ось' in s, 'sw.js: комментарий упоминает правую ось (473)')
chk('карточка прибора' in s, 'sw.js: комментарий упоминает карточку (474)')
# окна истории версий (тесты kip8 скопированы с окнами 3800/1300):
# комментарий партии не должен вытеснить Task 461 (3800) и Task 471 (1300)
i461 = s.rindex('Task 461', 0, s.index(new_v))
dist461 = s.index(new_v) - i461
chk(dist461 < 3800,
    'sw.js: дистанция до комментария Task 461 = %d (< 3800 — окно '
    'test-task461, запас %d)' % (dist461, 3800 - dist461))
i471 = s.rindex('Task 471', 0, s.index(new_v))
dist471 = s.index(new_v) - i471
chk(dist471 < 1300,
    'sw.js: дистанция до комментария Task 471 = %d (< 1300 — окно '
    'test-task471/472, запас %d)' % (dist471, 1300 - dist471))
wr(P, s)

# ============================================================
# 5. DEPLOY-док партии — копия из kip8test (для Task 473 DEPLOY-файл
#    не создавался: статический ассет, серверных шагов нет)
# ============================================================
print('=== 5. DEPLOY-Task474 (копия из kip8test) ===')
dep = 'DEPLOY-Task474-device-card-type-x15-meta-lower.md'
wr(os.path.join(K8, dep), rd(os.path.join(K8T, dep)))
chk(os.path.exists(os.path.join(K8, dep)), '%s скопирован в kip8' % dep)

print()
print('=== ИТОГ ===')
if fail:
    print('ПРОВАЛЕНО %d:' % len(fail))
    for m in fail:
        print('  - %s' % m)
    sys.exit(1)
print('ВСЁ ОК: партия 473+474 перенесена в kip8 (SW kipia-v509), '
    'клиент-only, серверных шагов нет')
