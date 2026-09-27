#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 429-transfer: перенос партии Tasks 407-428 из kip8test (HEAD f1e4291)
# в боевой kip8 ОДНИМ инкрементом SW kipia-v477 → v478.
# Метод (Task 292/401-406): файловый синк + де-изоляция:
#   1) index.html — копия kip8test HEAD + 14 репо-специфичных обратных
#      трансформаций (isolateLocalStorage, префиксы ключей, комментарии
#      Task 242/243/284, /kip8/#…); верификация «дифф диффов»;
#   2) scripts/WorkSchedule.gs — копия байт-в-байт (база была идентична);
#   3) scripts/Code.gs — точечная вставка case setTrainingDone (Task 418);
#   4) tests/ — копия всех test-*.js с маппингом версий:
#      kipia-test-v655→kipia-v478 (текущие ассерты),
#      kipia-test-v656→kipia-v479 (guards следующей версии),
#      kipia-test-v634/640/641/642→kipia-v477 (негативные guards прошлой
#      партии — у kip8test-промежуточных версий нет kip8-эквивалентов);
#      исторические строки (v623, v514-v617, v54x-v59x) — ОБЩИЕ, не трогаются;
#      test-task344.js (kip8-специфичный) — бамп v477→v478;
#      run-all.js — копия + require('./test-task344.js') после 343;
#   5) sw.js — kip8-собственный файл: v477→v478 + комментарий партии.
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


def diff_lines(a_path, b_path):
    """Список только изменённых строк (< / >) между двумя файлами."""
    r = subprocess.run(['diff', a_path, b_path],
                       capture_output=True, text=True)
    out = []
    for ln in r.stdout.splitlines():
        if ln.startswith('<') or ln.startswith('>'):
            out.append(ln)
    return out


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

assert src != orig, 'index.html: ни одной трансформации не применилось'
chk(src.count('kip8test') == 1,
    'index.html: упоминаний kip8test после де-изоляции = 1 '
    '(общая строка «для kip8test/kip8»): %d' % src.count('kip8test'))
chk(src.count(V_TEST) == 0,
    'index.html: строк kipia-test-v нет: %d' % src.count(V_TEST))

k8_index_new = os.path.join(K8, 'index.html')
wr(k8_index_new, src)

# --- Верификация «дифф диффов» (Task 401-404 паттерн) ---
git(K8T, 'show', '0ef0fcd:index.html') and None
base_t = os.path.join('/tmp', 'k8t-index-base.html')
base8 = os.path.join('/tmp', 'k8-index-base.html')
with io.open(base_t, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', '0ef0fcd:index.html'))
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
    'index.html: дифф задач 407-428 идентичен в обоих репо '
    '(%d строк против %d)' % (len(d_task8), len(d_taskT)))

# ============================================================
# 2. scripts/WorkSchedule.gs — копия байт-в-байт
# ============================================================
print('=== 2. scripts/WorkSchedule.gs ===')
ws_t = os.path.join(K8T, 'scripts', 'WorkSchedule.gs')
ws_8 = os.path.join(K8, 'scripts', 'WorkSchedule.gs')
wr(ws_8, rd(ws_t))
base_t_ws = '/tmp/k8t-ws-base.gs'
base_8_ws = '/tmp/k8-ws-base.gs'
with io.open(base_t_ws, 'w', encoding='utf-8') as f:
    f.write(git(K8T, 'show', '0ef0fcd:scripts/WorkSchedule.gs'))
with io.open(base_8_ws, 'w', encoding='utf-8') as f:
    f.write(git(K8, 'show', 'HEAD:scripts/WorkSchedule.gs'))
chk(diff_lines(base_8_ws, base_t_ws) == [],
    'WorkSchedule.gs: база репо идентична (0 строк диффа)')
chk(diff_lines(ws_8, ws_t) == [],
    'WorkSchedule.gs: новый kip8 == kip8test HEAD (0 строк диффа)')
chk(diff_lines(base_8_ws, ws_8) == diff_lines(base_t_ws, ws_t),
    'WorkSchedule.gs: дифф задач идентичен обоим репо')

# ============================================================
# 3. scripts/Code.gs — вставка case setTrainingDone (Task 418)
# ============================================================
print('=== 3. scripts/Code.gs ===')
P = os.path.join(K8, 'scripts', 'Code.gs')
src = rd(P)
ANCHOR = (
    "      case 'workSchedule.deleteTraining':\n"
    '        return _json(WorkSchedule.deleteTraining(payload));\n'
    '\n'
)
HUNK = (
    '      // Task 418: отметка о выполнении записи «Инструктажей» —\n'
    '      // столбцы «выполнение» (F) + пересчёт «просрочен» (G);\n'
    '      // галочка в блоке «Повторные инструктажи…» карточки работника\n'
    "      case 'workSchedule.setTrainingDone':\n"
    '        return _json(WorkSchedule.setTrainingDone(payload));\n'
    '\n'
)
n = src.count(ANCHOR)
chk(n == 1, 'Code.gs: якорь deleteTraining найден (%d)' % n)
if 'setTrainingDone' not in src:
    src = src.replace(ANCHOR, ANCHOR + HUNK)
    chk(src.count('setTrainingDone') == 2,
        'Code.gs: case setTrainingDone вставлен (маркёров 2)')
else:
    print('SKIP: setTrainingDone уже есть')
wr(P, src)
print('Code.gs записан (+case setTrainingDone, Task 418)')

# ============================================================
# 4. tests/ — копия с маппингом версий
# ============================================================
print('=== 4. tests/ ===')
TDIR_T = os.path.join(K8T, 'tests')
TDIR_8 = os.path.join(K8, 'tests')
MAP = [
    ('kipia-test-v655', 'kipia-v478'),
    ('kipia-test-v656', 'kipia-v479'),
    ('kipia-test-v634', 'kipia-v477'),
    ('kipia-test-v640', 'kipia-v477'),
    ('kipia-test-v641', 'kipia-v477'),
    ('kipia-test-v642', 'kipia-v477'),
]
MSG_MAP = [
    ("'v640 не осталась в sw.js'", "'v477 (прошлая партия) не осталась в sw.js'"),
    ("'v641 не осталась в sw.js'", "'v477 (прошлая партия) не осталась в sw.js'"),
    ("'v642 не осталась в sw.js'", "'v477 (прошлая партия) не осталась в sw.js'"),
]
tot = {}
copied = changed = 0
for name in sorted(os.listdir(TDIR_T)):
    if not name.startswith('test-') or not name.endswith('.js'):
        continue
    s = rd(os.path.join(TDIR_T, name))
    c0 = s
    for old, new in MAP:
        if old in s:
            tot[old] = tot.get(old, 0) + s.count(old)
            s = s.replace(old, new)
    for old, new in MSG_MAP:
        if old in s:
            s = s.replace(old, new)
    dst = os.path.join(TDIR_8, name)
    if not os.path.exists(dst) or rd(dst) != s:
        wr(dst, s)
        changed += 1
    copied += 1
print('  test-*.js: скопировано %d, изменено на диске %d' % (copied, changed))
for old, new in MAP[:2]:
    print('  %s → %s: %d замен' % (old, new, tot.get(old, 0)))
for old, _ in MAP[2:]:
    chk(tot.get(old, 0) == 1, 'тесты: %s → v477 (%d замен)'
        % (old, tot.get(old, 0)))

# остатки kipia-test (исторические, общие для репо)
hist = {}
for name in sorted(os.listdir(TDIR_8)):
    if not name.startswith('test-'):
        continue
    for ln in rd(os.path.join(TDIR_8, name)).splitlines():
        if V_TEST in ln:
            import re
            for m in re.findall(r'kipia-test-v\d+', ln):
                hist[m] = hist.get(m, 0) + 1
print('  исторические kipia-test-v* (общие, не тронуты): %s'
      % dict(sorted(hist.items())))

# 4.1 test-task344.js (kip8-специфичный) — бамп v477→v478
P344 = os.path.join(TDIR_8, 'test-task344.js')
s = rd(P344)
n = s.count('kipia-v477')
chk(n == 3, 'test-task344.js: ассертов kipia-v477 = 3 (%d)' % n)
s = s.replace('kipia-v477', 'kipia-v478')
wr(P344, s)

# 4.2 run-all.js — копия + require test-task344 после 343
RA = os.path.join(TDIR_8, 'run-all.js')
s = rd(os.path.join(TDIR_T, 'run-all.js'))
A = "require('./test-task343.js');\n"
B = "require('./test-task343.js');\nrequire('./test-task344.js');\n"
chk(s.count(A) == 1, "run-all.js: якорь test-task343 найден (%d)" % s.count(A))
chk('test-task344' not in s, 'run-all.js: 344 ещё не подключён')
s = s.replace(A, B)
chk("require('./test-task344.js');" in s, 'run-all.js: 344 подключён')
wr(RA, s)

# ============================================================
# 5. sw.js — версия + комментарий партии
# ============================================================
print('=== 5. sw.js ===')
P = os.path.join(K8, 'sw.js')
s = rd(P)
old_v = "const CACHE_VERSION = 'kipia-v477';"
new_v = "const CACHE_VERSION = 'kipia-v478';"
chk(s.count(old_v) == 1, 'sw.js: CACHE_VERSION v477 найден (%d)'
    % s.count(old_v))
COMMENT = (
    '// Task 429 (перенос партии Tasks 407-428 из kip8test@f1e4291): '
    'блок\n'
    '// инструктажей по ШАБЛОНУ «Список_И_и_ПЗ» (строгий select, эталон 5\n'
    '// пунктов, instrListInit), формы инструктаж/мероприятие\n'
    '// (Task 410-412), автосоздание листа «Инструктажи» (413), карточка —\n'
    '// плоские записи и полные ФИО (414-417), отметка выполнения\n'
    '// (418: Code.gs case setTrainingDone + столбцы F/G), АВТОСОЗДАНИЕ\n'
    '// повторных инструктажей по правилам периодичности (419-423:\n'
    '// вводный/повторный +6 мес, 9-ОГЭ +3 мес), лист «Мероприятия» +\n'
    '// eventsInit (424-425; мероприятия — БЕЗ автосоздания), День шахтёра\n'
    '// НЕ государственный праздник (426), РАЗДЕЛЬНЫЕ id-последовательности\n'
    '// инструктажей и мероприятий (427), авто-длительность мероприятия по\n'
    '// периоду + ярлыки 8px + отступы 5px (428). Партия = один инкремент.\n'
)
if 'Task 429 (перенос партии' not in s:
    s = s.replace(old_v, COMMENT + new_v)
chk("const CACHE_VERSION = 'kipia-v478';" in s, 'sw.js: v478 установлен')
chk(s.count('kipia-v478') == 1, 'sw.js: маркёр v478 один (%d)'
    % s.count('kipia-v478'))
wr(P, s)

print()
print('=== ИТОГ ===')
if fail:
    print('ПРОВАЛЕНО %d:' % len(fail))
    for m in fail:
        print('  - %s' % m)
    sys.exit(1)
print('ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ. Дальше: node tests/run-all.js в kip8.')
