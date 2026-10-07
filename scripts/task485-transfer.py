#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 485-transfer: перенос партии из kip8test (@b3c2358a, Task 485)
# в боевой kip8 ОДНИМ инкрементом SW kipia-v512 → v513 (регламент
# Task 441; команда из заявки: «Сразу обнови и в kip8»).
# Состав партии: «Кап. ремонт» блокировок + КРУГОВЫЕ диаграммы
# «Клапана»/«Регуляторы» (charts-desktop.js, удаление статистики/
# Топ-10) + sync-lockouts.py + data/lockouts.json (точечная правка).
# КЛИЕНТ-ONLY: .gs не тронуты; index.html НЕ менялся (де-изоляция
# НЕ нужна — сверка идентичности баз); десктопы — CI-автосинк.
# МЕТОД (Task 292/441-484): НЕ wholesale-копия тестов (в kip8 есть
# kip8-АДАПТИРОВАННЫЕ файлы — 480 README/cron, 476 DB_NAME и др.),
# а ЗЕРКАЛЬНЫЕ операции: (а) bump v513-guards→v514, v512→v513;
# (б) те же расширения окон, что kip8test; (в) те же адаптации
# 483/484; (г) НОВЫЙ test-task485.js с MAP версий; (д) run-all.
# ОДНОРАЗОВЫЙ: лечение при сбое — git checkout -- . + чистый прогон.
import io
import os
import shutil
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
# 0. База: kip8test HEAD = b3c2358a (Task 485), kip8 HEAD = 9255ccb
# ============================================================
BASE_T = 'dcfe7d19'   # kip8test до партии (post-482-484 docs)
BATCH_T = 'b3c2358a'  # kip8test Task 485
HEAD_T = git(K8T, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_T == BATCH_T, 'база: kip8test HEAD = %s (ожидался %s)'
    % (HEAD_T, BATCH_T))
HEAD_8 = git(K8, 'rev-parse', '--short', 'HEAD').strip()
chk(HEAD_8 == '9255ccb', 'база: kip8 HEAD = %s (ожидался 9255ccb)'
    % HEAD_8)
st = git(K8, 'status', '--porcelain').strip()
noise = [ln for ln in st.splitlines() if ln.startswith('??')
         and ('task485-transfer' in ln or '__pycache__' in ln)]
real = [ln for ln in st.splitlines() if ln not in noise]
chk(not real, 'kip8: рабочее дерево чистое: %r' % (real[:4],))

# ============================================================
# 1. index.html — партия НЕ меняла: diff kip8test(база→партия) пуст;
#    kip8-версия остаётся своей (де-изолированной — прямое сравнение
#    баз двух репо НЕ равно из-за изоляции kip8test)
# ============================================================
print('=== 1. index.html (не менялся) ===')
d_idx = git(K8T, 'diff', '--stat', BASE_T, BATCH_T, '--', 'index.html').strip()
chk(d_idx == '', 'index.html: партия не меняла файл (diff базы пуст)')
chk(not any(l.startswith(' M index.html') or l == 'M index.html'
            for l in git(K8, 'status', '--porcelain').splitlines()),
    'index.html: kip8-копия не тронута переносом (осталась '
    'де-изолированной)')

# ============================================================
# 2. charts-desktop.js — простая копия (репо-специфики нет)
# ============================================================
print('=== 2. charts-desktop.js ===')
src_mod = os.path.join(K8T, 'charts-desktop.js')
dst_mod = os.path.join(K8, 'charts-desktop.js')
mod = rd(src_mod)
chk(git(K8T, 'show', BASE_T + ':charts-desktop.js') ==
    git(K8, 'show', HEAD_8 + ':charts-desktop.js'),
    'charts-desktop: базы репо идентичны')
chk('kip8test' not in mod and V_TEST not in mod,
    'charts-desktop: репо-специфики нет')
for m in ('Task 485', '_renderPieCard', '_renderValvesPies',
          '_renderRegulatorsPies', '_PC_PALETTE', '_classifyRegParam',
          'ppr-tc-card', "'Клапана'", "'Ду не указан'"):
    chk(m in mod, 'charts-desktop: маркер партии %r' % (m[:44],))
for dead in ('var totalItems', '_renderBarChart: function',
             '_groupLabel: function', '_avgPerProd: function',
             '.chart-stats-grid {', '.chart-bar-row {'):
    chk(dead not in mod, 'charts-desktop: удалённое (485) %r' % dead)
shutil.copyfile(src_mod, dst_mod)

# ============================================================
# 3. scripts/sync-lockouts.py — простая копия
# ============================================================
print('=== 3. sync-lockouts.py ===')
s_t = rd(os.path.join(K8T, 'scripts', 'sync-lockouts.py'))
chk(git(K8T, 'show', BASE_T + ':scripts/sync-lockouts.py') ==
    git(K8, 'show', HEAD_8 + ':scripts/sync-lockouts.py'),
    'sync-lockouts.py: базы репо идентичны')
chk('kip8test' not in s_t and V_TEST not in s_t,
    'sync-lockouts.py: репо-специфики нет')
chk("PPR_TYPE_NAMES = {'Кр': 'Кап. ремонт', 'ТО': 'Тех. обслуж.'}" in s_t,
    'sync-lockouts.py: Кап. ремонт')
chk('Кан. ремонт' not in s_t, 'sync-lockouts.py: опечатки нет')
shutil.copyfile(os.path.join(K8T, 'scripts', 'sync-lockouts.py'),
                os.path.join(K8, 'scripts', 'sync-lockouts.py'))

# ============================================================
# 4. data/lockouts.json — точечная правка (только имя серии)
# ============================================================
print('=== 4. data/lockouts.json ===')
s_t = rd(os.path.join(K8T, 'data', 'lockouts.json'))
s_8 = rd(os.path.join(K8, 'data', 'lockouts.json'))
chk(s_t == s_8.replace('"Кан. ремонт"', '"Кап. ремонт"'),
    'lockouts.json: отличие kip8 ТОЛЬКО в имени серии (1 строка)')
shutil.copyfile(os.path.join(K8T, 'data', 'lockouts.json'),
                os.path.join(K8, 'data', 'lockouts.json'))
import json
d = json.load(open(os.path.join(K8, 'data', 'lockouts.json'), encoding='utf-8'))
chk(d['ppr_chart']['series'][0]['name'] == 'Кап. ремонт' and
    d['total_lockouts'] == 531 and len(d['lockouts']) == 531,
    'lockouts.json (kip8): Кап. ремонт, структура не задета')

# ============================================================
# 5. sw.js — шапка kip8 + перенос-метка + комментарий Task 485
#    дословно + v513; ТЕЛО от IMAGE-якоря идентично kip8test HEAD
# ============================================================
print('=== 5. sw.js ===')
P_SW = os.path.join(K8, 'sw.js')
sw8 = rd(P_SW)
swt = rd(os.path.join(K8T, 'sw.js'))

ANCHOR_IMG_8 = "const IMAGE_CACHE_VERSION = 'kipia-images-v3';"
ANCHOR_IMG_T = "const IMAGE_CACHE_VERSION = 'kipia-images-test-v3';"
chk(sw8.count(ANCHOR_IMG_8) == 1, 'sw.js (kip8): IMAGE-якорь найден')
chk(swt.count(ANCHOR_IMG_T) == 1, 'sw.js (kip8test): IMAGE-якорь найден')

C_START = '// Task 485:'
i_c = swt.index(C_START)
i_cv_t = swt.index("const CACHE_VERSION = 'kipia-test-v709';")
BATCH_COMMENT = swt[i_c:i_cv_t]
chk(BATCH_COMMENT.endswith('\n') and BATCH_COMMENT.count('Task 485') == 1,
    'sw.js: извлечён комментарий Task 485 (%d симв.)' % len(BATCH_COMMENT))
chk(V_TEST not in BATCH_COMMENT and 'kip8test' not in BATCH_COMMENT,
    'sw.js: комментарий партии версионно-нейтрален')
for m in ('Клапана', 'Регуляторы', 'круговые', 'Кап. ремонт',
          'Логика SW не менялась'):
    chk(m in BATCH_COMMENT, 'sw.js: маркер комментария %r' % (m,))

MARK = '// Task 485 (перенос из kip8test@b3c2358a):\n'
old_v = "const CACHE_VERSION = 'kipia-v512';"
new_v = "const CACHE_VERSION = 'kipia-v513';"
chk(sw8.count(old_v) == 1, 'sw.js: CACHE_VERSION v512 найден')
sw_new = sw8.replace(old_v, MARK + BATCH_COMMENT + new_v)
chk(sw_new.count(new_v) == 1, 'sw.js: kipia-v513 ровно один')
chk('kipia-v512' not in sw_new, 'sw.js: kipia-v512 не осталось')
chk(sw_new.startswith(sw8[:sw8.index(old_v)]),
    'sw.js: шапка kip8 до CACHE_VERSION не изменена (история жива)')
chk(sw_new.count('kip8test') == sw8.count('kip8test') + 1,
    'sw.js: kip8test-упоминания = исторические + 1 перенос-метка')

# ТЕЛО: от IMAGE-якоря идентично kip8test HEAD (кроме имён кэшей)
pbn = '/home/z/my-project/scripts/.k8-sw-body-new485.js'
pbh = '/home/z/my-project/scripts/.k8t-sw-body-head485.js'
wr(pbn, sw_new[sw_new.index(ANCHOR_IMG_8):])
wr(pbh, swt[swt.index(ANCHOR_IMG_T):])
r = subprocess.run(['diff', pbn, pbh], capture_output=True, text=True)
body_diffs = [ln for ln in r.stdout.splitlines()
              if (ln.startswith('<') or ln.startswith('>'))
              and 'kipia-data' not in ln and 'kipia-images' not in ln]
chk(body_diffs == [], 'sw.js: ТЕЛО идентично kip8test HEAD (%d расхожд.'
    % len(body_diffs))
wr(P_SW, sw_new)

# Дистанции якорей против НОВЫХ окон тестов (копируются ниже)
i_new_v = sw_new.index(new_v)
for task_no, window in ((484, 1500), (483, 1500), (482, 2600),
                        (481, 2500), (480, 2600), (479, 2500),
                        (478, 3200), (473, 5100), (474, 4700),
                        (472, 5300), (471, 5900), (461, 8500)):
    i_task = sw_new.rindex('Task %d' % task_no, 0, i_new_v)
    dist = i_new_v - i_task
    chk(dist < window, 'sw.js: Task %d дистанция %d < окна %d (запас %d)'
        % (task_no, dist, window, window - dist))

# ============================================================
# 6. tests/ — зеркальные операции kip8test
# ============================================================
print('=== 6. tests/ ===')
T8 = os.path.join(K8, 'tests')

# --- 6а. BUMP: guards v513→v514, ассерты v512→v513 (как
#     task485-bump-sw.py в kip8test; OWN 485 ещё не скопирован) ---
import glob
changed = []
tot_assert = tot_guard = 0
for f in sorted(glob.glob(os.path.join(T8, 'test-*.js'))):
    s = rd(f)
    orig = s
    n_guard = s.count('kipia-v513')
    s = s.replace('kipia-v513', 'kipia-v514')
    n_assert = s.count('kipia-v512')
    s = s.replace('kipia-v512', 'kipia-v513')
    if s != orig:
        wr(f, s)
        changed.append(os.path.basename(f))
        tot_assert += n_assert
        tot_guard += n_guard
print('  бамп: файлов %d (ассерты v512→v513: %d, guards v513→v514: %d)'
      % (len(changed), tot_assert, tot_guard))
chk(tot_assert > 500, 'бамп: ассертов перекрыто %d (> 500)' % tot_assert)
chk(tot_guard > 100, 'бамп: guards перекрыто %d (> 100)' % tot_guard)
leftover = [os.path.basename(f) for f in glob.glob(os.path.join(T8, 'test-*.js'))
            if 'kipia-v512' in rd(f)]
chk(not leftover, 'бамп: kipia-v512 остатков нет: %r' % leftover[:4])
# 344: ассерты были v512 → уехали на v513 автоматически

# --- 6б. ОКНА истории (зеркало task485-windows.py + windows2.py +
#     фикс 482-окна; порядок пар в 481 ВАЖЕН: 2500→3200 ДО 1500→2500) ---
rep_file(os.path.join(T8, 'test-task481.js'), [
    ("Math.max(0, i - 2500)", "Math.max(0, i - 3200)", 1),
    ("Math.max(0, i - 1500)", "Math.max(0, i - 2500)", 1),
    ("Math.max(0, i - 2100)", "Math.max(0, i - 2600)", 1),
    ("(i - i474) < 4000", "(i - i474) < 4700", 1),
    ("(i - i472) < 4500", "(i - i472) < 5300", 1),
    ("(i - i471) < 5000", "(i - i471) < 5900", 1),
    ("(i - i461) < 7600", "(i - i461) < 8500", 1),
], 'test-task481 окна')
rep_file(os.path.join(T8, 'test-task481.js'), [
    ("indexOf('i - 7600')", "indexOf('i - 8500')", 1),
    ("indexOf('i - 5000')", "indexOf('i - 5900')", 1),
    ("indexOf('i - 4500')", "indexOf('i - 5300')", 1),
    ("indexOf('i - 4000')", "indexOf('i - 4700')", 1),
], 'test-task481 каскады')
rep_file(os.path.join(T8, 'test-task482.js'), [
    ("Math.max(0, i - 2100)", "Math.max(0, i - 2600)", 2),
    ("Math.max(0, i - 2500)", "Math.max(0, i - 3200)", 1),
    ("(i - i474) < 4000", "(i - i474) < 4700", 1),
    ("(i - i472) < 4500", "(i - i472) < 5300", 1),
    ("(i - i471) < 5000", "(i - i471) < 5900", 1),
    ("(i - i461) < 7600", "(i - i461) < 8500", 1),
    ("s478.indexOf('i - 2500')", "s478.indexOf('i - 3200')", 1),
    ("s479.indexOf('i - 2500')", "s479.indexOf('i - 3200')", 1),
    ("s480.indexOf('i - 2100')", "s480.indexOf('i - 2600')", 1),
    # ПОРЯДОК ВАЖЕН: сначала 2500→3200 и 2100→2600 (исходные),
    # ПОТОМ 1500→2500 (создаёт новый литерал — его не должен
    # перехватить ни один следующий шаблон)
    ("s481.indexOf('i - 2500')", "s481.indexOf('i - 3200')", 1),
    ("s481.indexOf('i - 2100')", "s481.indexOf('i - 2600')", 1),
    ("s481.indexOf('i - 1500')", "s481.indexOf('i - 2500')", 1),
], 'test-task482 окна+каскады')
rep_file(os.path.join(T8, 'test-task483.js'), [
    ("Math.max(0, i - 700)", "Math.max(0, i - 1500)", 1),
    ("        const seg = CHARTS_SRC.slice(CHARTS_SRC.indexOf('_renderContent: function'),\n"
     "                                     CHARTS_SRC.indexOf('var totalItems'));",
     "        const seg = CHARTS_SRC.slice(CHARTS_SRC.indexOf('_renderContent: function'),\n"
     "                                     CHARTS_SRC.indexOf('_renderValvesPies: function'));", 1),
], 'test-task483 окно+якорь')
rep_file(os.path.join(T8, 'test-task484.js'), [
    ("Math.max(0, i - 700)", "Math.max(0, i - 1500)", 1),
    ('//   SW: kipia-v513 (логика SW не менялась; окна истории',
     '//   SW: kipia-v512 (логика SW не менялась; окна истории', 1),
], 'test-task484 окно+шапка')
rep_file(os.path.join(T8, 'test-task483.js'), [
    ('//   SW: kipia-v513 (логика SW не менялась; окна истории',
     '//   SW: kipia-v512 (логика SW не менялась; окна истории', 1),
], 'test-task483 шапка SW')
rep_file(os.path.join(T8, 'test-task480.js'), [
    ("Math.max(0, i - 2100)", "Math.max(0, i - 2600)", 1),
], 'test-task480 окно')
rep_file(os.path.join(T8, 'test-task478.js'), [
    ("Math.max(0, i - 2500)", "Math.max(0, i - 3200)", 1),
    ("(i - i474) < 4000", "(i - i474) < 4700", 1),
    ("(i - i472) < 4500", "(i - i472) < 5300", 1),
    ("(i - i471) < 5000", "(i - i471) < 5900", 1),
    ("(i - i461) < 7600", "(i - i461) < 8500", 1),
], 'test-task478 окна')
rep_file(os.path.join(T8, 'test-task479.js'), [
    ("Math.max(0, i - 2500)", "Math.max(0, i - 3200)", 1),
    ("(i - i474) < 4000", "(i - i474) < 4700", 1),
    ("(i - i472) < 4500", "(i - i472) < 5300", 1),
    ("(i - i471) < 5000", "(i - i471) < 5900", 1),
    ("(i - i461) < 7600", "(i - i461) < 8500", 1),
], 'test-task479 окна')
rep_file(os.path.join(T8, 'test-task473.js'), [
    ("Math.max(0, i - 4600)", "Math.max(0, i - 5100)", 1),
], 'test-task473 окно')
rep_file(os.path.join(T8, 'test-task474.js'), [
    ("Math.max(0, i - 4000)", "Math.max(0, i - 4700)", 1),
    ("(i - i471) < 5000", "(i - i471) < 5900", 1),
    ("(i - i461) < 7600", "(i - i461) < 8500", 1),
], 'test-task474 окна')
rep_file(os.path.join(T8, 'test-task472.js'), [
    ("Math.max(0, i - 4500)", "Math.max(0, i - 5300)", 1),
    ("Math.max(0, i - 5000)", "Math.max(0, i - 5900)", 1),
], 'test-task472 окна')
rep_file(os.path.join(T8, 'test-task471.js'), [
    ("Math.max(0, i - 5000)", "Math.max(0, i - 5900)", 1),
], 'test-task471 окно')
rep_file(os.path.join(T8, 'test-task461.js'), [
    ("Math.max(0, i - 7600)", "Math.max(0, i - 8500)", 1),
], 'test-task461 окно')
rep_file(os.path.join(T8, 'test-task476.js'), [
    ("(i - i474) < 4000", "(i - i474) < 4700", 1),
    ("(i - i472) < 4500", "(i - i472) < 5300", 1),
    ("(i - i471) < 5000", "(i - i471) < 5900", 1),
    ("(i - i461) < 7600", "(i - i461) < 8500", 1),
], 'test-task476 окна')
rep_file(os.path.join(T8, 'test-task477.js'), [
    ("(i - i474) < 4000", "(i - i474) < 4700", 1),
    ("(i - i472) < 4500", "(i - i472) < 5300", 1),
    ("(i - i471) < 5000", "(i - i471) < 5900", 1),
    ("(i - i461) < 7600", "(i - i461) < 8500", 1),
], 'test-task477 окна')
rep_file(os.path.join(T8, 'test-task475.js'), [
    ("indexOf('i - 7600')", "indexOf('i - 8500')", 1),
    ("indexOf('i - 5000')", "indexOf('i - 5900')", 2),
    ("indexOf('i - 4500')", "indexOf('i - 5300')", 1),
    ("indexOf('i - 4000')", "indexOf('i - 4700')", 1),
], 'test-task475 §9 каскады')

# --- 6в. АДАПТАЦИЯ 484 (Кап. ремонт + тест стат-кода + якоря срезов
#     — СНАЧАЛА тест со стат-кодом (внутри него третий якорь
#     'var totalItems'), ПОТОМ якоря срезов; порядок как в kip8test) ---
p484 = os.path.join(T8, 'test-task484.js')
s = rd(p484)
assert s.count('Кан. ремонт') == 8, s.count('Кан. ремонт')
s = s.replace('Кан. ремонт', 'Кап. ремонт')
assert s.count('Кан.<ремонт') == 1
s = s.replace('Кан.<ремонт', 'Кап.<ремонт')
assert s.count('Кан.&lt;ремонт') == 1
s = s.replace('Кан.&lt;ремонт', 'Кап.&lt;ремонт')
OLD_TEST = """    test('сводная статистика и Топ-10 НЕ рендерятся для lockouts', () => {
        // ветка раннего возврата стоит ДО «var totalItems» — как у
        // приборов (заявка: «убери всё лишнее»)
        const iBranch = CHARTS_SRC.indexOf("if (tab === 'devices' || tab === 'lockouts')");
        const iStats = CHARTS_SRC.indexOf('var totalItems');
        assertTrue(iBranch !== -1 && iStats !== -1 && iBranch < iStats,
            'ранний возврат до сводной статистики');
    });"""
NEW_TEST = """    test('сводная статистика и Топ-10 НЕ рендерятся для lockouts', () => {
        // Task 485: сводная статистика и Топ-10 бары удалены из
        // charts-desktop.js ЦЕЛИКОМ (заявка 485 по «Клапанам»/
        // «Регуляторам»: «убери текущие графики и подсчёты») — ни
        // одна вкладка их больше не рендерит; для lockouts рендер
        // идёт ТОЛЬКО веткой раннего возврата ppr_chart (484)
        assertTrue(CHARTS_SRC.indexOf('var totalItems') === -1,
            'код сводной статистики удалён (Task 485)');
        assertTrue(CHARTS_SRC.indexOf('_renderBarChart: function') === -1,
            'рендерер Топ-10 баров удалён (Task 485)');
        const iBranch = CHARTS_SRC.indexOf("if (tab === 'devices' || tab === 'lockouts')");
        assertTrue(iBranch !== -1, 'ветка раннего возврата lockouts жива');
    });"""
assert s.count(OLD_TEST) == 1
s = s.replace(OLD_TEST, NEW_TEST)
# якоря срезов — ПОСЛЕ замены теста; NEW_TEST сам содержит
# indexOf('var totalItems') (проверка отсутствия) — заменяем только
# МНОГОСТРОЧНЫЕ срезовые шаблоны (×2), как в kip8test
SLICE_OLD = """        const seg = CHARTS_SRC.slice(CHARTS_SRC.indexOf('_renderContent: function'),
                                     CHARTS_SRC.indexOf('var totalItems'));"""
SLICE_NEW = """        const seg = CHARTS_SRC.slice(CHARTS_SRC.indexOf('_renderContent: function'),
                                     CHARTS_SRC.indexOf('_renderValvesPies: function'));"""
n_anchor = s.count(SLICE_OLD)
assert n_anchor == 2, 'срезовых якорей var totalItems: %d (ожидалось 2)' % n_anchor
s = s.replace(SLICE_OLD, SLICE_NEW)
wr(p484, s)
print('OK [test-task484 адаптация]: Кап. ремонт ×10 + тест стат-кода + якоря ×2')

# --- 6г. НОВЫЙ test-task485.js с MAP ---
src485 = rd(os.path.join(K8T, 'tests', 'test-task485.js'))
MAP485 = [
    ('kipia-test-v709', 'kipia-v513'),
    ('kipia-test-v710', 'kipia-v514'),
    ('kipia-test-v708', 'kipia-v512'),
    ('kipia-images-test-v3', 'kipia-images-v3'),
    ('kipia-data-test-v1', 'kipia-data-v1'),
]
for old, new in MAP485:
    n = src485.count(old)
    assert n >= 1, '485: %r не найден' % old
    src485 = src485.replace(old, new)
    print('  485: %s → %s ×%d' % (old, new, n))
chk('kipia-test-v' not in src485, 'test-task485: тестовых версий нет')
chk('kip8test' not in src485, 'test-task485: репо-специфики нет')
wr(os.path.join(T8, 'test-task485.js'), src485)

# --- 6д. run-all.js: регистрация 485 ---
RA = os.path.join(T8, 'run-all.js')
s = rd(RA)
A = "require('./test-task484.js');\n"
B = ("require('./test-task484.js');\n"
     "// Task 485 — Графики КИП ИОС → «Клапана»/«Регуляторы»: круговые\n"
     "// диаграммы (SVG, палитра Excel, стиль Приборов/Блокировок) — по\n"
     "// типам (отс/рег/дисковые/прочие «Клапана»), по Ду, футированные;\n"
     "// производства/устройства/параметры (унификация по величине);\n"
     "// сводная статистика и Топ-10 бары удалены; «Кр» = «Кап. ремонт».\n"
     "require('./test-task485.js');\n")
assert s.count(A) == 1
chk('test-task485' not in s, 'run-all.js (kip8): 485 ещё не подключён')
s = s.replace(A, B)
wr(RA, s)
print('OK [run-all.js]: test-task485.js зарегистрирован')

# ============================================================
# 7. DEPLOY-док — копия
# ============================================================
shutil.copyfile(os.path.join(K8T, 'DEPLOY-Task485-charts-pies-valves-regulators.md'),
                os.path.join(K8, 'DEPLOY-Task485-charts-pies-valves-regulators.md'))
chk(True, 'DEPLOY-Task485 скопирован')

# ============================================================
# 8. Итог
# ============================================================
print('\n===== ПЕРЕНОС ЗАВЕРШЁН: %d OK / %d FAIL =====' % (
    sum(1 for _ in ()), len(fail)))
for m in fail:
    print('FAIL: %s' % m)
if fail:
    sys.exit(1)
print('Дальше: node tests/run-all.js (kip8) → SMOKE → коммиты')
