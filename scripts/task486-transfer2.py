#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 486-transfer ЧАСТЬ 2: sw.js + тесты (после task486-transfer.py).
# sw.js — шапка kip8 + перенос-метка + комментарий Task 486 дословно
# + kipia-v514, ТЕЛО идентично kip8test HEAD. Тесты — зеркальные
# операции: bump (guards v514→v515, ассерты v513→v514), те же окна,
# что task486-windows.py (версия в паре 482 — v514 ПОСЛЕ бампа),
# WS_CLIENT 500000→600000 ×8, срез 477 700→1700, НОВЫЙ
# test-task486.js с MAP, run-all; шапка test-task485 — историческая
# v513 (возврат после бампа; прецедент 485-переноса).
import glob
import io
import os
import subprocess
import sys

K8 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
K8T = os.path.abspath(os.path.join(K8, '..', 'kip8test'))
T8 = os.path.join(K8, 'tests')
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


def rep_file(path, pairs, tag):
    """Точечные замены с контролем счётчиков; порядок пар ВАЖЕН."""
    s = rd(path)
    for old, new, cnt in pairs:
        n = s.count(old)
        assert n == cnt, '%s: %r найдено %d (ожидалось %d)' % (
            tag, old[:60], n, cnt)
        s = s.replace(old, new)
    wr(path, s)
    print('OK [%s]: %d замен' % (tag, len(pairs)))


# ============================================================
# 2. sw.js — шапка kip8 + перенос-метка + комментарий Task 486
#    дословно + v514; ТЕЛО от IMAGE-якоря идентично kip8test HEAD
# ============================================================
print('=== 2. sw.js ===')
P_SW = os.path.join(K8, 'sw.js')
sw8 = rd(P_SW)
swt = rd(os.path.join(K8T, 'sw.js'))

ANCHOR_IMG_8 = "const IMAGE_CACHE_VERSION = 'kipia-images-v3';"
ANCHOR_IMG_T = "const IMAGE_CACHE_VERSION = 'kipia-images-test-v3';"
chk(sw8.count(ANCHOR_IMG_8) == 1, 'sw.js (kip8): IMAGE-якорь найден')
chk(swt.count(ANCHOR_IMG_T) == 1, 'sw.js (kip8test): IMAGE-якорь найден')

C_START = '// Task 486:'
i_c = swt.index(C_START)
i_cv_t = swt.index("const CACHE_VERSION = 'kipia-test-v710';")
BATCH_COMMENT = swt[i_c:i_cv_t]
chk(BATCH_COMMENT.endswith('\n') and BATCH_COMMENT.count('Task 486') == 1,
    'sw.js: извлечён комментарий Task 486 (%d симв.)' % len(BATCH_COMMENT))
chk(V_TEST not in BATCH_COMMENT and 'kip8test' not in BATCH_COMMENT,
    'sw.js: комментарий партии версионно-нейтрален')
for m in ('Табель', 'ТИХОЕ обновление', 'silentRefresh', '_preloadWs',
          'троттлинг', 'Клиент-only', 'кэши не тронуты'):
    chk(m in BATCH_COMMENT, 'sw.js: маркер комментария %r' % (m,))

MARK = '// Task 486 (перенос из kip8test@c0d241ee):\n'
old_v = "const CACHE_VERSION = 'kipia-v513';"
new_v = "const CACHE_VERSION = 'kipia-v514';"
chk(sw8.count(old_v) == 1, 'sw.js: CACHE_VERSION v513 найден')
sw_new = sw8.replace(old_v, MARK + BATCH_COMMENT + new_v)
chk(sw_new.count(new_v) == 1, 'sw.js: kipia-v514 ровно один')
chk('kipia-v513' not in sw_new, 'sw.js: kipia-v513 не осталось')
chk(sw_new.startswith(sw8[:sw8.index(old_v)]),
    'sw.js: шапка kip8 до CACHE_VERSION не изменена (история жива)')
chk(sw_new.count('kip8test') == sw8.count('kip8test') + 1,
    'sw.js: kip8test-упоминания = исторические + 1 перенос-метка')

# ТЕЛО: от IMAGE-якоря идентично kip8test HEAD (кроме имён кэшей)
TMP = '/home/z/my-project/scripts/.k8t-486-tmp'
os.makedirs(TMP, exist_ok=True)
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

# Дистанции якорей против НОВЫХ окон тестов (окна ниже расширяются)
i_new_v = sw_new.index(new_v)
for task_no, window in ((485, 1500), (484, 2100), (483, 2100),
                        (482, 3200), (481, 3200), (480, 3200),
                        (479, 4100), (478, 4100), (473, 5600),
                        (474, 5300), (472, 5900), (471, 6500),
                        (461, 9100)):
    i_task = sw_new.rindex('Task %d' % task_no, 0, i_new_v)
    dist = i_new_v - i_task
    chk(dist < window, 'sw.js: Task %d дистанция %d < окна %d (запас %d)'
        % (task_no, dist, window, window - dist))

# ============================================================
# 3. tests/ — зеркальные операции kip8test
# ============================================================
print('=== 3. tests/ ===')

# --- 3а. BUMP: guards v514→v515, ассерты v513→v514 (как
#     task486-bump-sw.py в kip8test; OWN 486 ещё не скопирован) ---
changed = []
tot_assert = tot_guard = 0
for f in sorted(glob.glob(os.path.join(T8, 'test-*.js'))):
    s = rd(f)
    orig = s
    n_guard = s.count('kipia-v514')
    s = s.replace('kipia-v514', 'kipia-v515')
    n_assert = s.count('kipia-v513')
    s = s.replace('kipia-v513', 'kipia-v514')
    if s != orig:
        wr(f, s)
        changed.append(os.path.basename(f))
        tot_assert += n_assert
        tot_guard += n_guard
print('  бамп: файлов %d (ассерты v513→v514: %d, guards v514→v515: %d)'
      % (len(changed), tot_assert, tot_guard))
chk(tot_assert > 500, 'бамп: ассертов перекрыто %d (> 500)' % tot_assert)
chk(tot_guard > 100, 'бамп: guards перекрыто %d (> 100)' % tot_guard)
leftover = [os.path.basename(f)
            for f in glob.glob(os.path.join(T8, 'test-*.js'))
            if 'kipia-v513' in rd(f)]
chk(not leftover, 'бамп: kipia-v513 остатков нет (кроме шапки 485 — '
    'возвращаем ниже): %r' % leftover[:4])

# --- 3б. Шапка test-task485: ИСТОРИЧЕСКАЯ версия посадки в kip8
#     (v513 — партия 485; прецедент 485-переноса для 483/484) ---
rep_file(os.path.join(T8, 'test-task485.js'), [
    ('//   SW: kipia-v514 (логика SW не менялась; окна истории',
     '//   SW: kipia-v513 (логика SW не менялась; окна истории', 1),
], 'test-task485 шапка (историч. v513)')

# --- 3в. ОКНА истории (зеркало task486-windows.py; порядок пар
#     ВАЖЕН — ПО УБЫВАНИЮ чисел; версия в паре 482 — v514 после
#     бампа) ---
rep_file(os.path.join(T8, 'test-task482.js'), [
    ("test('комментарии Task 479/478 не вытеснены (окно 2500)', () => {\n"
     "        const i = SW_SRC.indexOf(\"const CACHE_VERSION = 'kipia-v514';\");\n"
     "        const ctx = SW_SRC.slice(Math.max(0, i - 3200), i);",
     "test('комментарии Task 479/478 не вытеснены (окно 4100)', () => {\n"
     "        const i = SW_SRC.indexOf(\"const CACHE_VERSION = 'kipia-v514';\");\n"
     "        const ctx = SW_SRC.slice(Math.max(0, i - 4100), i);", 1),
    ("const ctx = SW_SRC.slice(Math.max(0, i - 2600), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 3200), i);", 2),
], 'test-task482 окна')
rep_file(os.path.join(T8, 'test-task481.js'), [
    ("const w1400 = SW_SRC.slice(Math.max(0, i - 3200), i);",
     "const w1400 = SW_SRC.slice(Math.max(0, i - 4100), i);", 1),
    ("const w700 = SW_SRC.slice(Math.max(0, i - 2600), i);",
     "const w700 = SW_SRC.slice(Math.max(0, i - 3200), i);", 1),
    ("const ctx = SW_SRC.slice(Math.max(0, i - 2500), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 3200), i);", 1),
], 'test-task481 окна')
rep_file(os.path.join(T8, 'test-task480.js'), [
    ("const ctx = SW_SRC.slice(Math.max(0, i - 2600), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 3200), i);", 1),
    ("test('комментарий Task 480 в шапке версий (окно 1500 → 2100, Task 484)', () => {",
     "test('комментарий Task 480 в шапке версий (окно 2600 → 3200, Task 486)', () => {", 1),
], 'test-task480 окно')
rep_file(os.path.join(T8, 'test-task479.js'), [
    ("const ctx = SW_SRC.slice(Math.max(0, i - 3200), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 4100), i);", 1),
    ("test('окна истории: якоря 461/471/472/474 в прежних окнах (без расширения)', () => {",
     "test('окна истории: якоря 461/471/472/474 в расширенных окнах (Task 486)', () => {", 1),
], 'test-task479 окно')
rep_file(os.path.join(T8, 'test-task478.js'), [
    ("const ctx = SW_SRC.slice(Math.max(0, i - 3200), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 4100), i);", 1),
], 'test-task478 окно')
rep_file(os.path.join(T8, 'test-task484.js'), [
    ("const ctx = SW_SRC.slice(Math.max(0, i - 1500), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 2100), i);", 1),
], 'test-task484 окно')
rep_file(os.path.join(T8, 'test-task483.js'), [
    ("const ctx = SW_SRC.slice(Math.max(0, i - 1500), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 2100), i);", 1),
], 'test-task483 окно')
rep_file(os.path.join(T8, 'test-task473.js'), [
    ("const ctx = SW_SRC.slice(Math.max(0, i - 5100), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 5600), i);", 1),
], 'test-task473 окно')
rep_file(os.path.join(T8, 'test-task472.js'), [
    # СНАЧАЛА контекст Task 471 (5900→6500), потом собственное
    # (5300→5900) — по убыванию, иначе перехват
    ("const ctx = SW_SRC.slice(Math.max(0, i - 5900), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 6500), i);", 1),
    ("const ctx = SW_SRC.slice(Math.max(0, i - 5300), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 5900), i);", 1),
], 'test-task472 окна')
rep_file(os.path.join(T8, 'test-task471.js'), [
    ("const ctx = SW_SRC.slice(Math.max(0, i - 5900), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 6500), i);", 1),
], 'test-task471 окно')
rep_file(os.path.join(T8, 'test-task461.js'), [
    ("const above = SW_SRC.slice(Math.max(0, i - 8500), i);",
     "const above = SW_SRC.slice(Math.max(0, i - 9100), i);", 1),
], 'test-task461 окно')
rep_file(os.path.join(T8, 'test-task474.js'), [
    ("const ctx = SW_SRC.slice(Math.max(0, i - 4700), i);",
     "const ctx = SW_SRC.slice(Math.max(0, i - 5300), i);", 1),
], 'test-task474 окно')

# ЯкОРНЫЕ окна 474/472/471/461 (по УБЫВАНИЮ) в 474/476/477/478/479/
# 481/482 — числовые «(i - iXXX) < N» (в 474 их только 2: 471/461)
ANCHOR_PAIRS = [
    ("(i - i461) < 8500", "(i - i461) < 9100"),
    ("(i - i471) < 5900", "(i - i471) < 6500"),
    ("(i - i472) < 5300", "(i - i472) < 5900"),
    ("(i - i474) < 4700", "(i - i474) < 5300"),
]
for fn in ('test-task474.js', 'test-task476.js', 'test-task477.js',
           'test-task478.js', 'test-task479.js', 'test-task481.js',
           'test-task482.js'):
    p = os.path.join(T8, fn)
    s = rd(p)
    pairs = [(o, n, s.count(o)) for o, n in ANCHOR_PAIRS if s.count(o)]
    assert pairs, '%s: числовых якорных окон не найдено' % fn
    rep_file(p, pairs, '%s якоря' % fn)

# Каскад: test-task475 §9 (литералы чужих окон) — по убыванию
rep_file(os.path.join(T8, 'test-task475.js'), [
    ("s.indexOf('i - 8500') !== -1, 'окно расширено до 7600'",
     "s.indexOf('i - 9100') !== -1, 'окно расширено до 9100'", 1),
    ("s1.indexOf('i - 5900') !== -1, 'test-task471: 5000'",
     "s1.indexOf('i - 6500') !== -1, 'test-task471: 6500'", 1),
    ("s2.indexOf('i - 5900') !== -1, 'test-task472: 5000'",
     "s2.indexOf('i - 6500') !== -1, 'test-task472: 6500'", 1),
    ("s.indexOf('i - 5300') !== -1, 'окно Task 472: 4500'",
     "s.indexOf('i - 5900') !== -1, 'окно Task 472: 5900'", 1),
    ("s.indexOf('i - 4700') !== -1, 'окно Task 474: 4000'",
     "s.indexOf('i - 5300') !== -1, 'окно Task 474: 5300'", 1),
], 'test-task475 §9 каскады')

# Каскад: test-task481 §синхронизация (литералы 461/471/472/474)
rep_file(os.path.join(T8, 'test-task481.js'), [
    ("s461.indexOf('i - 8500') !== -1, 'test-task461: окно 7600'",
     "s461.indexOf('i - 9100') !== -1, 'test-task461: окно 9100'", 1),
    ("s471.indexOf('i - 5900') !== -1, 'test-task471: окно 5000'",
     "s471.indexOf('i - 6500') !== -1, 'test-task471: окно 6500'", 1),
    ("s472.indexOf('i - 5300') !== -1, 'test-task472: окно 4500'",
     "s472.indexOf('i - 5900') !== -1, 'test-task472: окно 5900'", 1),
    ("s474.indexOf('i - 4700') !== -1, 'test-task474: окно 4000'",
     "s474.indexOf('i - 5300') !== -1, 'test-task474: окно 5300'", 1),
], 'test-task481 §синхр')

# Каскад: test-task482 §каскад (литералы окон 478-481)
rep_file(os.path.join(T8, 'test-task482.js'), [
    ("s478.indexOf('i - 3200') !== -1, 'test-task478: окно 2500'",
     "s478.indexOf('i - 4100') !== -1, 'test-task478: окно 4100'", 1),
    ("s479.indexOf('i - 3200') !== -1, 'test-task479: окно 2500'",
     "s479.indexOf('i - 4100') !== -1, 'test-task479: окно 4100'", 1),
    ("s480.indexOf('i - 2600') !== -1, 'test-task480: окно 2100'",
     "s480.indexOf('i - 3200') !== -1, 'test-task480: окно 3200'", 1),
    ("s481.indexOf('i - 2500') !== -1 &&\n"
     "                   s481.indexOf('i - 2600') !== -1 &&\n"
     "                   s481.indexOf('i - 3200') !== -1,\n"
     "            'test-task481: окна 1500/2100/2500'",
     "s481.indexOf('i - 3200') !== -1 &&\n"
     "                   s481.indexOf('i - 4100') !== -1,\n"
     "            'test-task481: окна 3200/4100'", 1),
    ("        // windows-скрипты 482/483/484: 478 2100→2500; 479 2100 (без изм.);\n"
     "        // 480 1500→2100; 481: 1500/2100/2500",
     "        // windows-скрипты 482/483/484/486: 478 3200→4100; 479 3200→4100;\n"
     "        // 480 2600→3200; 481: 3200/3200/4100", 1),
], 'test-task482 §каскад')

# --- 3г. АДАПТАЦИИ СРЕЗОВ ИСХОДНИКА (модуль вырос на ~8.7КБ) ---
# WS_CLIENT 500000 → 600000 в 8 тестах: onCellClick уехал за
# границу; 600000 — внутри модуля (~851КБ)
for fn in ('test-task337.js', 'test-task338.js', 'test-task341.js',
           'test-task342.js', 'test-task343.js', 'test-task360.js',
           'test-task361.js', 'test-task362.js'):
    p = os.path.join(T8, fn)
    rep_file(p, [
        ("const WS_CLIENT = INDEX_SRC.slice(WS_START, WS_START + 500000);",
         "const WS_CLIENT = INDEX_SRC.slice(WS_START, WS_START + 600000);", 1),
    ], '%s WS_CLIENT' % fn)
# пояснение — в тесте, который реально поймал вылет (337)
rep_file(os.path.join(T8, 'test-task337.js'), [
    ("const WS_CLIENT = INDEX_SRC.slice(WS_START, WS_START + 600000);",
     "const WS_CLIENT = INDEX_SRC.slice(WS_START, WS_START + 600000);\n"
     "// Task 486: срез 500000→600000 — модуль вырос (silentRefresh\n"
     "// ~8.7КБ), onCellClick уехал за прежнюю границу", 1),
], 'test-task337 WS_CLIENT пояснение')

# test-task477: срез _schedulePreload 700 → 1700 — литерал 4000
# отодвинут вставкой Task 486 (~1505)
rep_file(os.path.join(T8, 'test-task477.js'), [
    ("const m = INDEX_SRC.slice(i, i + 700);",
     "const m = INDEX_SRC.slice(i, i + 1700);", 1),
], 'test-task477 срез _schedulePreload')

# --- 3д. НОВЫЙ test-task486.js с MAP версий ---
src486 = rd(os.path.join(K8T, 'tests', 'test-task486.js'))
MAP486 = [
    ('kipia-test-v710', 'kipia-v514'),
    ('kipia-test-v711', 'kipia-v515'),
    ('kipia-test-v709', 'kipia-v513'),
    ('kipia-images-test-v3', 'kipia-images-v3'),
    ('kipia-data-test-v1', 'kipia-data-v1'),
]
for old, new in MAP486:
    n = src486.count(old)
    assert n >= 1, '486: %r не найден' % old
    src486 = src486.replace(old, new)
    print('  486: %s → %s ×%d' % (old, new, n))
chk(V_TEST not in src486, 'test-task486: тестовых версий нет')
chk('kip8test' not in src486, 'test-task486: репо-специфики нет')
for m in ('Task 486', 'silentRefresh', '_schedulePreload',
          '_preloadWs', '600000', 'i + 1700'):
    chk(m in src486, 'test-task486: маркер %r' % (m,))
wr(os.path.join(T8, 'test-task486.js'), src486)

# --- 3е. run-all.js: регистрация 486 ---
RA = os.path.join(T8, 'run-all.js')
s = rd(RA)
A = "require('./test-task485.js');\n"
B = ("require('./test-task485.js');\n"
     "// Task 486 — Табель: ТИХОЕ обновление данных при открытии\n"
     "// приложения (помимо ручного «Обновить»): WorkSchedule"
     ".silentRefresh\n"
     "// из KipAuth._schedulePreload (5 путей старта, 4 с, canAccess) — 7\n"
     "// read-only экшенов, копия в ОБА слоя (LS + KipDB, merge), "
     "открытый\n"
     "// раздел тихо перерисовывается (без конкуренции с «Обновить»/\n"
     "// попапом ячейки), _PENDING живы, троттлинг 5 мин, сбой —\n"
     "// console.warn; KipPreload._preloadWs — ретрай-фолбэк.\n"
     "require('./test-task486.js');\n")
assert s.count(A) == 1
chk('test-task486' not in s, 'run-all.js (kip8): 486 ещё не подключён')
s = s.replace(A, B)
wr(RA, s)
print('OK [run-all.js]: test-task486.js зарегистрирован')

print('\n===== ПЕРЕНОС ЗАВЕРШЁН: %d FAIL =====' % len(fail))
for m in fail:
    print('FAIL: %s' % m)
if fail:
    sys.exit(1)
print('Дальше: node tests/run-all.js (kip8)')
