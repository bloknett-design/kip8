#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 463-464-transfer: перенос ПАРТИИ Tasks 463+464 из kip8test
# (фиксы 6f5b4bed/de669b9f) в боевой kip8 ОДНИМ инкрементом SW
# kipia-v499 → v500 (регламент Task 441: партия = один инкремент).
# Состав партии:
#   Task 463 — «Плановые мероприятия» ИНТЕРАКТИВНЫ: отметки
#              выполнения + архив файла Мероприятия_КИП_ИОС
#              (PlanEvents.gs list/mark + PlanEventsInit.gs);
#   Task 464 — полировка: правка даты + снятие отметки
#              (update/unmark), «Подтвердить» + красная «Отмена»,
#              ширина колонки по тексту, мобильная компактность
#              (селектор месяца + один столбец на <= 1023px).
# Метод (Task 292/401-406/429/437/441-459/460-462): файловый синк +
# де-изоляция + «дифф диффов». Якоря де-изоляции скопированы ТОЧНО
# из task460-462-transfer.py (якоря 459, подводные камни 455 учтены).
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
# 0. База партии: kip8test@67c0139e (Task 462 закрытие — состояние,
#    синхронное kip8@11617e1; далее 6f5b4bed/de669b9f — партия)
#    ↔ kip8@HEAD (11617e1 — Task 462 закрытие, index.html от 2dc2346)
# ============================================================
BASE_T = '67c0139e'   # Task 462 закрытие в kip8test
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == 'de669b9f',
    'база: kip8test HEAD = %s (Task 464, ожидался de669b9f)' % HEAD_T)
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_8 == '11617e1',
    'база: kip8 HEAD = %s (ожидался 11617e1 — Task 462 закрытие)'
    % HEAD_8)

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

# 1.15 Комментарий реестра Task 458 (0 упоминаний isolateLocalStorage
# в kip8 — тест test-task344)
rep1(
    '        // ключ localStorage ws_auto_dn_keys (префикс репозитория\n'
    '        // ставит isolateLocalStorage)\n',
    '        // ключ localStorage ws_auto_dn_keys (в тестовом репо\n'
    '        // ключ автоматически получает префикс)\n',
    'auto-dn-keys-comment')

assert src != orig, 'index.html: ни одной трансформации не применилась'
# 4 исторических (Task 243/284/274/кэш СЖ) + 1 новый осознанный —
# комментарий шапки модуля PlanEventsData: Apps Script ОДИН бэкенд
# на kip8 и kip8test (как в PlanEvents.gs)
chk(src.count('kip8test') == 5,
    'index.html: упоминаний kip8test после де-изоляции = 5 '
    '(4 исторических + 1 комментарий PlanEventsData про общий '
    'бэкенд): %d' % src.count('kip8test'))
chk(src.count(V_TEST) == 0,
    'index.html: строк kipia-test-v нет: %d' % src.count(V_TEST))

# Маркеры партии 463+464
chk('var PlanEventsData = {' in src,
    'index.html: модуль PlanEventsData (Task 463)')
chk('id="page-plan-events"' in src and 'id="peTable"' in src,
    'index.html: страница #page-plan-events + таблица peTable')
chk("api('planEvents.mark'" in src and "api('planEvents.list'" in src,
    'index.html: вызовы planEvents.list/mark (Task 463)')
chk("api('planEvents.update'" in src and "api('planEvents.unmark'" in src,
    'index.html: вызовы planEvents.update/unmark (Task 464)')
chk('id="peMonthSel"' in src and '_tagColumns' in src and '_applyMonth' in src,
    'index.html: селектор месяца + классы колонок (Task 464 мобайл)')
chk('>Подтвердить</button>' in src and 'pe-cancel-red' in src,
    'index.html: кнопка «Подтвердить» + красная «Отмена» (Task 464)')
chk('pe-unmark-btn' in src and 'Удалить отметку' in src,
    'index.html: кнопка «Удалить отметку» диалога правки (Task 464)')
chk('.pe-col-name { width: auto; }' in src,
    'index.html: колонка мероприятий по тексту (Task 464)')
chk('peHint' not in src and 'class="pe-hint"' not in src,
    'index.html: подсказка peHint удалена (Task 464)')
chk('Мероприятия_КИП_ИОС' in src,
    'index.html: упомянут файл архива Мероприятия_КИП_ИОС')

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» ---
# База партии 463+464: kip8test@67c0139e (Task 462 закрытие —
# состояние, перенесённое в kip8@11617e1) против kip8@HEAD.
base_t = '/tmp/k8t-index-base463.html'
base8 = '/tmp/k8-index-base463.html'
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
    'index.html: дифф задач (463+464) идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 2. scripts/*.gs — партия НЕ трогала общие модули: проверка
#    идентичности + КОПИЯ НОВЫХ PlanEvents.gs/PlanEventsInit.gs +
#    Code.gs (4 case + шапка) в kip8-версии
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

# НОВЫЕ файлы Task 463: PlanEvents.gs (463+464: list/mark/update/unmark)
# и PlanEventsInit.gs — копии из kip8test
for gs, marks in (('PlanEvents.gs',
                   ["case 'planEvents.mark':", "update: function(payload)",
                    "unmark: function(payload)", "SRV_VER: '464'",
                    '1uX8Bz6FBS9HniZfWQnHeeyccTwwjwyvpPFWyFkIclCs']),
                  ('PlanEventsInit.gs',
                   ['PE_HEADERS', 'planEventsDeploy',
                    '1uX8Bz6FBS9HniZfWQnHeeyccTwwjwyvpPFWyFkIclCs'])):
    src_gs = rd(os.path.join(K8T, 'scripts', gs))
    for m in marks:
        chk(m in src_gs, '%s: маркер %r' % (gs, m[:44]))
    wr(os.path.join(K8, 'scripts', gs), src_gs)
    chk(rd(os.path.join(K8, 'scripts', gs)) == src_gs,
        '%s: скопирован в kip8/scripts (эталон; Apps Script ОДИН на оба '
        'репо — пользователь уже развернул 463, для 464 обновить)' % gs)

# Code.gs — kip8-версия: вставить 4 case planEvents.* перед default
# (в kip8test-эталоне блок уже есть; kip8-Code.gs исторически отличается
# — вставляем точечно, паттерн 292/443-459)
P_CODE = os.path.join(K8, 'scripts', 'Code.gs')
code = rd(P_CODE)
chk("case 'planEvents." not in code,
    'Code.gs (kip8): case planEvents.* ещё нет (до переноса)')
ANCHOR_CASE = "      case 'workSchedule.deletePpe':\n" \
              "        return _json(WorkSchedule.deletePpe(payload));\n"
chk(code.count(ANCHOR_CASE) == 1,
    'Code.gs (kip8): якорь case workSchedule.deletePpe найден')
CASES = (
    "\n"
    "      // === Плановые мероприятия: отметки выполнения (Task 463) ===\n"
    "      // PlanEvents.gs — архив файла Мероприятия_КИП_ИОС (лист\n"
    "      // «Архив», создаётся PlanEventsInit.gs); доступ — право\n"
    "      // plan.events матрицы KIP8_Access (Task 462)\n"
    "      case 'planEvents.list':\n"
    "        return _json(PlanEvents.list(payload));\n"
    "\n"
    "      case 'planEvents.mark':\n"
    "        return _json(PlanEvents.mark(payload));\n"
    "\n"
    "      // Task 464: правка даты отметки + снятие отметки\n"
    "      case 'planEvents.update':\n"
    "        return _json(PlanEvents.update(payload));\n"
    "\n"
    "      case 'planEvents.unmark':\n"
    "        return _json(PlanEvents.unmark(payload));\n"
)
code = code.replace(ANCHOR_CASE, ANCHOR_CASE + CASES, 1)
# Шапка сигнатур: + PlanEvents (Task 463/464)
ANCHOR_HEAD = (
    ' *     Гейт GATE_ACTIONS: admin* → admin.panel, каб. журнал (записи)\n'
    ' *     → cablejournal.edit — по матрице KIP8_Access (до модуля).\n')
chk(code.count(ANCHOR_HEAD) == 1,
    'Code.gs (kip8): якорь шапки RoleMatrixGate найден')
HEAD_ADD = (
    ' *   PlanEvents (Task 463/464) — «Плановые мероприятия»: отметки\n'
    ' *     выполнения, архив файла Мероприятия_КИП_ИОС:\n'
    ' *     PlanEvents.list(payload)   → {ok, data/error}\n'
    ' *     PlanEvents.mark(payload)  → {ok, data/error} (идемпотентно)\n'
    ' *     PlanEvents.update(payload) → {ok, data/error} (Task 464: дата)\n'
    ' *     PlanEvents.unmark(payload) → {ok, data/error} (Task 464: снятие)\n')
code = code.replace(ANCHOR_HEAD, ANCHOR_HEAD + HEAD_ADD, 1)
wr(P_CODE, code)
for m in ("case 'planEvents.list':", "case 'planEvents.mark':",
          "case 'planEvents.update':", "case 'planEvents.unmark':",
          'PlanEvents (Task 463/464)'):
    chk(m in rd(P_CODE), 'Code.gs (kip8): маркер %r вставлен' % m[:40])

# ============================================================
# 3. tests/ — копия с маппингом версий
# ============================================================
print('=== 3. tests/ ===')
TDIR_T = os.path.join(K8T, 'tests')
TDIR_8 = os.path.join(K8, 'tests')
MAP = [
    # текущие ассерты (бамп партии 463+464 — в kip8 ОДИН инкремент)
    ('kipia-test-v688', 'kipia-v500'),
    # guards следующей версии
    ('kipia-test-v689', 'kipia-v501'),
    # негативы партии: «версия до партии» в kip8 одна — v499
    ('kipia-test-v687', 'kipia-v499'),   # негативы task463/task464 (×2)
    # исторические негативы (маппинг 460-462/458/459 перенесён дальше)
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
chk(tot.get('kipia-test-v688', 0) > 450,
    'тесты: текущие ассерты v688 → v500 перекрыты (%d)'
    % tot.get('kipia-test-v688', 0))
chk(tot.get('kipia-test-v689', 0) > 100,
    'тесты: guards v689 → v501 перекрыты (%d)'
    % tot.get('kipia-test-v689', 0))
chk(tot.get('kipia-test-v687', 0) == 2,
    'тесты: негативы партии v687 → v499 два (test-task463/464, %d)'
    % tot.get('kipia-test-v687', 0))

# новые тест-файлы партии — в kip8, с замапленными версиями
for name, marks in (
    ('test-task463.js', ["CACHE_VERSION = 'kipia-v500'",
                         'kipia-v499', 'PlanEventsData']),
    ('test-task464.js', ["CACHE_VERSION = 'kipia-v500'",
                         'kipia-v499', 'peMonthSel', 'planEvents.update']),
):
    p = os.path.join(TDIR_8, name)
    chk(os.path.exists(p), '%s скопирован в kip8' % name)
    s = rd(p)
    for m in marks:
        chk(m in s, '%s: маркер %r замаплен' % (name, m[:44]))

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

# 3.1 test-task344.js (kip8-специфичный) — бамп v499→v500
P344 = os.path.join(TDIR_8, 'test-task344.js')
s = rd(P344)
n = s.count('kipia-v499')
chk(n == 3, 'test-task344.js: ассертов kipia-v499 = 3 (%d)' % n)
s = s.replace('kipia-v499', 'kipia-v500')
wr(P344, s)

# 3.2 run-all.js — копия + require test-task344 после 343
RA = os.path.join(TDIR_8, 'run-all.js')
s = rd(os.path.join(TDIR_T, 'run-all.js'))
A = "require('./test-task343.js');\n"
B = "require('./test-task343.js');\nrequire('./test-task344.js');\n"
chk(s.count(A) == 1, "run-all.js: якорь test-task343 найден (%d)" % s.count(A))
chk('test-task344' not in s, 'run-all.js (kip8test): 344 ещё не подключён')
s = s.replace(A, B)
for n_ in range(438, 465):
    if n_ == 437:
        continue
    chk("require('./test-task%d.js');" % n_ in s,
        'run-all.js: test-task%d подключён' % n_)
chk("require('./test-task463.js');" in s and
    "require('./test-task464.js');" in s,
    'run-all.js: тесты партии 463+464 подключены')
wr(RA, s)
s8 = rd(RA)
chk("require('./test-task344.js');" in s8,
    'run-all.js (kip8): test-task344 подключён (перенос 459 сохранён)')

# 3.3 после всего: kipia-v499 в тестах kip8 — ТОЛЬКО негативы партии
left499 = {name: rd(os.path.join(TDIR_8, name)).count('kipia-v499')
           for name in sorted(os.listdir(TDIR_8))
           if name.startswith('test-') and
           'kipia-v499' in rd(os.path.join(TDIR_8, name))}
chk(left499 == {'test-task463.js': 1, 'test-task464.js': 1},
    'тесты kip8: kipia-v499 остался ТОЛЬКО в негативах партии '
    '(до версии v499): %s' % left499)

# ============================================================
# 4. sw.js — версия + комментарий партии
# ============================================================
print('=== 4. sw.js ===')
P = os.path.join(K8, 'sw.js')
s = rd(P)
old_v = "const CACHE_VERSION = 'kipia-v499';"
new_v = "const CACHE_VERSION = 'kipia-v500';"
chk(s.count(old_v) == 1, 'sw.js: CACHE_VERSION v499 найден (%d)'
    % s.count(old_v))
COMMENT = (
    '// Task 463-464 (перенос партии из kip8test@de669b9f): Task 463 —\n'
    '// «Плановые мероприятия» ИНТЕРАКТИВНЫ: отметки выполнения +\n'
    '// архив файла Мероприятия_КИП_ИОС (PlanEvents.gs,\n'
    '// PlanEventsInit.gs); Task 464 — полировка: правка даты + снятие\n'
    '// отметки (planEvents.update/unmark), кнопка «Подтвердить» +\n'
    '// слегка красная «Отмена», ширина колонки мероприятий по тексту,\n'
    '// мобильная компактность — селектор peMonthSel и один столбец\n'
    '// месяца на экранах <= 1023px.\n'
)
if 'Task 463-464 (перенос партии' not in s:
    s = s.replace(old_v, COMMENT + new_v)
chk("const CACHE_VERSION = 'kipia-v500';" in s, 'sw.js: v500 установлен')
chk(s.count('kipia-v500') == 1, 'sw.js: маркер v500 один (%d)'
    % s.count('kipia-v500'))
chk('Task 463' in s and 'Task 464' in s,
    'sw.js: комментарий партии упоминает Tasks 463/464')
chk('peMonthSel' in s and 'Мероприятия_КИП_ИОС' in s,
    'sw.js: маркеры партии (peMonthSel/файл архива)')
chk(len(COMMENT) < 2000,
    'sw.js: комментарий партии %d символов (< 2000 — окно test-task461)'
    % len(COMMENT))
wr(P, s)

# ============================================================
# 5. DEPLOY-доки партии — копии из kip8test
# ============================================================
print('=== 5. DEPLOY-Task463/464 (копии из kip8test) ===')
for dep in ('DEPLOY-Task463-plan-events-marks-archive.md',
            'DEPLOY-Task464-plan-events-polish-edit-unmark-mobile.md'):
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
