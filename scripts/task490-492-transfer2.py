#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 490-492-transfer ЧАСТЬ 2: tests/ — 3-way merge с ПОСТРОЧНОЙ
# НОРМАЛИЗАЦИЕЙ base И theirs к ours (методология task487-489-
# transfer2.py v3, прецедент). Партия: 174 изменённых + 3 новых
# (test-task490/491/492.js) + run-all.
# MAP_THEIRS (роль-семантика, прецедент 487-489):
#   v717 (guard/next)         → v517 (guard/next kip8)
#   v716 (результат партии)   → v516 (результат партии kip8)
#   v715/v714 (внутри партии) → v515 (pre-party kip8: «один инкремент»)
#   v713 (pre-party kip8test) → v515 (эпоха 487-489 = kip8 v515)
# ОЖИДАЕМЫЕ конфликты (в отличие от 487-489, где было 0):
#   (a) окна 480/481/482: ours 6600/6500 (kip8-геометрия 487-489) vs
#       theirs 6000/6800/7300/6100 → keep-ours + §5 точечные правки
#       под каскадные мета-проверки 482/486;
#   (b) данные devices.json: theirs адаптирован под 1288 приборов
#       (авто-синк kip8test 5238816d), ours — под данные kip8 →
#       keep-ours ВСЕГДА (данные репо-специфичны);
#   (c) шапки-посадки 483/484/485/486 — merge возьмёт theirs (v516),
#       §6 восстанавливает kip8-историкалы v512/v512/v513/v514.
# КОНТРОЛЬ: kipia-test-v только исторические негативы kip8 (прецедент);
# в НОВЫХ файлах партии — ноль.
import io
import os
import re
import subprocess
import sys
import difflib

K8 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
K8T = os.path.abspath(os.path.join(K8, '..', 'kip8test'))
T8 = os.path.join(K8, 'tests')
TMP = '/home/z/my-project/scripts/.k8t-490-492-tmp'
os.makedirs(TMP, exist_ok=True)
fail = []
conflicts_report = []

VER_TOK = re.compile(r'kipia-test-v\d+|kipia-v\d+|(?<![\w-])v\d+')


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


BASE_T = '58965654'   # kip8test до партии

MAP_THEIRS = [
    ('kipia-test-v717', 'kipia-v517'),   # guards (next absent)
    ('kipia-test-v716', 'kipia-v516'),   # текущие ассерты (результат партии)
    ('kipia-test-v715', 'kipia-v515'),   # 492-previous → один инкремент kip8
    ('kipia-test-v714', 'kipia-v515'),   # 491-previous → один инкремент kip8
    ('kipia-test-v713', 'kipia-v515'),   # pre-party (эпоха 487-489) = v515
    ('kipia-images-test-v3', 'kipia-images-v3'),
    ('kipia-data-test-v1', 'kipia-data-v1'),
]


def mapped(s, mp):
    for old, new in mp:
        s = s.replace(old, new)
    return s


def norm_line(ln):
    return VER_TOK.sub('{}', ln)


def derive_pairs(base_raw, ours):
    """Пары (base-строка, ours-строка) для строк, различающихся
    ТОЛЬКО версионными токенами. Порядок выравнивания — difflib."""
    base_l = base_raw.split('\n')
    ours_l = ours.split('\n')
    sm = difflib.SequenceMatcher(None, base_l, ours_l, autojunk=False)
    pairs = {}
    amb = set()
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'replace' or (i2 - i1) != (j2 - j1):
            continue
        for bi, oj in zip(range(i1, i2), range(j1, j2)):
            b_line, o_line = base_l[bi], ours_l[oj]
            if norm_line(b_line) == norm_line(o_line) and b_line != o_line:
                if b_line in pairs and pairs[b_line] != o_line:
                    amb.add(b_line)
                pairs[b_line] = o_line
    for k in amb:
        pairs.pop(k, None)
    return pairs


def apply_pairs(s, pairs):
    for b_line, o_line in sorted(pairs.items(), key=lambda t: -len(t[0])):
        if b_line in s:
            s = s.replace(b_line, o_line)
    return s


def normalize_base(base_raw, ours):
    """base' = base с подстановкой ours-строк на версионно-эквив.
    строках; + глобальная era-замена остатков текущей пары."""
    pairs = derive_pairs(base_raw, ours)
    s = apply_pairs(base_raw, pairs)
    # era-замена: не покрытое построчно (текущая пара эпохи
    # post-487-489 в kip8test = v713/pre-party)
    s = s.replace('kipia-test-v713', 'kipia-v515')
    return s, pairs


# ============================================================
# 1. Состав партии
# ============================================================
print('=== 1. Состав партии ===')
party_out = git(K8T, 'diff', '--name-only', '%s..HEAD' % BASE_T, '--',
                'tests/')
party = [os.path.basename(f) for f in party_out.splitlines()
         if f.endswith('.js')]
modified = [f for f in party if f not in
            ('run-all.js', 'test-task490.js', 'test-task491.js',
             'test-task492.js')]
chk(len(modified) == 174, 'партия: изменённых тест-файлов %d (ожидалось 174)'
    % len(modified))
missing = [f for f in modified
           if not os.path.exists(os.path.join(T8, f))]
chk(not missing, 'все файлы существуют в kip8: %r' % missing)

# ============================================================
# 2. 3-way merge c нормализованным base (ожидание: конфликты
#     только окон/данных/шапок — см. шапку скрипта)
# ============================================================
print('=== 2. 3-way merge (base нормализован к ours) ===')
n_merged = n_identical = 0
n_conf_total = 0
tot_pairs = 0
for name in sorted(modified):
    p8 = os.path.join(T8, name)
    ours = rd(p8)
    base_raw = git(K8T, 'show', '%s:tests/%s' % (BASE_T, name))
    base_n, pairs = normalize_base(base_raw, ours)
    # theirs: сначала подстановки пар (не-партийные строки —
    # kip8test-историкалы становятся kip8-строками), затем MAP
    theirs = apply_pairs(rd(os.path.join(K8T, 'tests', name)), pairs)
    theirs = mapped(theirs, MAP_THEIRS)
    tot_pairs += len(pairs)
    if theirs == ours:            # партия файл не меняла содержательно
        n_identical += 1
        continue
    if base_n == theirs:         # партия файл не меняла содержательно
        n_identical += 1
        continue
    f_ours = os.path.join(TMP, 'ours.js')
    f_base = os.path.join(TMP, 'base.js')
    f_theirs = os.path.join(TMP, 'theirs.js')
    wr(f_ours, ours)
    wr(f_base, base_n)
    wr(f_theirs, theirs)
    r = subprocess.run(['git', 'merge-file', '-p', '--diff3',
                        '-L', 'ours', '-L', 'base', '-L', 'theirs',
                        f_ours, f_base, f_theirs],
                       capture_output=True, text=True)
    if r.returncode < 0:
        fail.append('merge-file %s: %s' % (name, r.stderr[:200]))
        continue
    merged = r.stdout
    if r.returncode > 0:
        n_conf_total += r.returncode
        out = []
        mode = None
        ours_buf = []
        theirs_buf = []
        base_buf = []
        for ln in merged.split('\n'):
            if ln.startswith('<<<<<<< ours'):
                mode = 'ours'
                ours_buf = []
                continue
            if ln.startswith('||||||| base'):
                mode = 'base'
                base_buf = []
                continue
            if ln.startswith('======='):
                mode = 'theirs'
                theirs_buf = []
                continue
            if ln.startswith('>>>>>>> theirs'):
                conflicts_report.append(
                    (name,
                     ' | '.join(x.strip()[:100] for x in ours_buf[:3]),
                     ' | '.join(x.strip()[:100] for x in base_buf[:3]),
                     ' | '.join(x.strip()[:100] for x in theirs_buf[:3])))
                out.extend(ours_buf)   # keep ours; §5-§7 точечные правки
                mode = None
                continue
            if mode == 'ours':
                ours_buf.append(ln)
            elif mode == 'base':
                base_buf.append(ln)
            elif mode == 'theirs':
                theirs_buf.append(ln)
            elif mode is None:
                out.append(ln)
        merged = '\n'.join(out)
    if merged != ours:
        wr(p8, merged)
        n_merged += 1
print('  merge: записано %d, без правок %d; пар нормализации %d'
      % (n_merged, n_identical, tot_pairs))
chk(n_merged + n_identical == len(modified), 'merge: все 174 учтены')
if conflicts_report:
    print('  КОНФЛИКТОВ (keep-ours): %d в %d файлах'
          % (n_conf_total, len(set(c[0] for c in conflicts_report))))
    wr(os.path.join(TMP, 'conflicts-490-492.txt'),
       '\n\n'.join('%s:\n  OURS:   %s\n  BASE:   %s\n  THEIRS: %s' % t
                   for t in conflicts_report))
    for name, o_c, b_c, t_c in conflicts_report:
        print('  КОНФЛИКТ %s:\n    OURS:   %s\n    THEIRS: %s'
              % (name, o_c[:200], t_c[:200]))

# ============================================================
# 3. Новые файлы 490/491/492 — копия + MAP + версионные правки
#    (короткие формы v7NN прецедент чистит FIX-списками)
# ============================================================
print('=== 3. Новые тесты ===')
FIX_490 = [
    ('E. SW v714 (guard v715).', 'E. SW v516 (guard v515).'),
    ('старой версии v713 нет', 'старой версии v515 нет'),
]
FIX_491 = [
    ('F. SW v715 (guard v716).', 'F. SW v516 (guard v515).'),
    ('SW — v716.', 'SW — v516.'),
    ('старой версии v714 нет', 'старой версии v515 нет'),
]
FIX_492 = [
    ('E. SW v716 (guard v715 в sw.js отсутствует).',
     'E. SW v516 (guard v515 в sw.js отсутствует).'),
    ('старой версии v715 нет', 'старой версии v515 нет'),
]
for name, fixes in (('test-task490.js', FIX_490),
                    ('test-task491.js', FIX_491),
                    ('test-task492.js', FIX_492)):
    s = mapped(rd(os.path.join(K8T, 'tests', name)), MAP_THEIRS)
    for old, new in fixes:
        n = s.count(old)
        if n != 1:
            fail.append('[%s] правка %r: вхождений %d (ожидалось 1)'
                        % (name, old[:50], n))
        s = s.replace(old, new)
    wr(os.path.join(T8, name), s)
    s2 = rd(os.path.join(T8, name))
    chk('kipia-test-v7' not in s2, '%s: kipia-test-v7 нет' % name)
    short = re.findall(r'(?<![\w-])v7\d{2}\b', s2)
    chk(not short, '%s: коротких форм v7NN нет: %r' % (name, short[:4]))

# ============================================================
# 4. run-all.js — вставка +490/+491/+492 (после 489)
# ============================================================
print('=== 4. run-all.js ===')
P_RUN = os.path.join(T8, 'run-all.js')
run8 = rd(P_RUN)
runt = rd(os.path.join(K8T, 'tests', 'run-all.js'))
anchor = "require('./test-task489.js');\nrequire('./test-deploy-url.js');"
chk(run8.count(anchor) == 1, 'run-all: якорь 489→deploy-url найден')
block_t = runt[runt.index("require('./test-task489.js');"):
               runt.index("require('./test-deploy-url.js');")]
insert = block_t[len("require('./test-task489.js');"):]
chk(insert.count('490') >= 2 and insert.count('491') >= 2
    and insert.count('492') >= 2 and 'kipia-test' not in insert,
    'run-all: вставка извлечена (%d симв.)' % len(insert))
run8_new = run8.replace(anchor,
                        "require('./test-task489.js');\n" + insert
                        + "require('./test-deploy-url.js');")
chk(run8_new.count("require('./test-task490.js');") == 1
    and run8_new.count("require('./test-task491.js');") == 1
    and run8_new.count("require('./test-task492.js');") == 1,
    'run-all: +490/+491/+492 зарегистрированы')
wr(P_RUN, run8_new)

# ============================================================
# 5. kip8-специфика: окна под геометрию kip8 + каскадные
#    мета-литералы (прецедент 487-489 «вместе с мета-ссылками»)
# ============================================================
print('=== 5. kip8-специфика (окна) ===')
# 5.1 test-task480: окно 6600 → 6800 (theirs; мета-проверка 482:694
#     ждёт 'i - 6800'; kip8 дистанция 480@6474 < 6800 ✓)
p = os.path.join(T8, 'test-task480.js')
s = rd(p)
n = s.count('i - 6600')
if n >= 1:
    s = s.replace('i - 6600', 'i - 6800')
    wr(p, s)
    print('OK: test-task480: окна 6600 → 6800 (×%d, мета 482)' % n)
else:
    chk('i - 6800' in s, 'test-task480: окна уже 6800 или нет 6600')
# 5.2 test-task481: w700 6600→6800, w1400 6500→7300 (теirs-значения
#     проходят kip8-геометрию: 480@6474/479@6488; ctx остаётся OURS
#     6600 — kip8 481@6230 > theirs 6000); мета 482:696 ждёт 'i - 6000'
#     в 481 → 5.3 адаптирует мета-литерал под 6600
p = os.path.join(T8, 'test-task481.js')
s = rd(p)
c_w700 = s.count('i - 6600')
c_w1400 = s.count('i - 6500')
if c_w700 >= 1 and c_w1400 >= 1:
    s = s.replace('i - 6600', 'i - 6800').replace('i - 6500', 'i - 7300')
    wr(p, s)
    print('OK: test-task481: w700 6600→6800 (×%d), w1400 6500→7300 (×%d)'
          % (c_w700, c_w1400))
else:
    chk('i - 6800' in s and 'i - 7300' in s,
        'test-task481: окна 6800/7300 уже на месте (6600=%d, 6500=%d)'
        % (c_w700, c_w1400))
# 5.3 test-task482: мета-проверка s481 'i - 6000' → 'i - 6600'
#     (kip8-геометрия: theirs-окно 6000 < якорь 481@6230)
p = os.path.join(T8, 'test-task482.js')
s = rd(p)
old_meta = "s481.indexOf('i - 6000')"
new_meta = "s481.indexOf('i - 6600')"
if s.count(old_meta) == 1:
    s = s.replace(old_meta, new_meta)
    wr(p, s)
    print('OK: test-task482: мета-ссылка 481 6000 → 6600 (kip8-геометрия)')
else:
    chk(new_meta in s, 'test-task482: мета-ссылка уже 6600')

# ============================================================
# 6. Шапки-посадки (merge взял theirs' v516 — возвращаем
#    kip8-историкалы; прецедент 487-489, те же 4 файла)
# ============================================================
print('=== 6. Шапки-посадки ===')
restores = [
    ('test-task483.js', '//   SW: kipia-v516 (логика SW не менялась; окна истории',
     '//   SW: kipia-v512 (логика SW не менялась; окна истории'),
    ('test-task484.js', '//   SW: kipia-v516 (логика SW не менялась; окна истории',
     '//   SW: kipia-v512 (логика SW не менялась; окна истории'),
    ('test-task485.js', '//   SW: kipia-v516 (логика SW не менялась; окна истории',
     '//   SW: kipia-v513 (логика SW не менялась; окна истории'),
    ('test-task486.js', '//   SW: kipia-v516 (логика SW НЕ менялась; кэши не тронуты).',
     '//   SW: kipia-v514 (логика SW НЕ менялась; кэши не тронуты).'),
]
for name, old, new in restores:
    p = os.path.join(T8, name)
    s = rd(p)
    if s.count(old) == 1:
        wr(p, s.replace(old, new))
        chk(True, '%s: шапка-посадка восстановлена (%s)'
            % (name, new[new.index('kipia'):new.index('(', 8)]))
    else:
        chk(('SW: kipia-v51' not in s) or (s.count(new) == 1),
            '%s: шапка уже историческая или не тронута' % name)

# kip8-ONLY файл: test-task344.js (в kip8test отсутствует) —
# точечный бамп версии (прецедент 482-484/487-489)
p344 = os.path.join(T8, 'test-task344.js')
if os.path.exists(p344) and not os.path.exists(
        os.path.join(K8T, 'tests', 'test-task344.js')):
    s = rd(p344)
    n = s.count('kipia-v515')
    s = s.replace('kipia-v515', 'kipia-v516')
    wr(p344, s)
    chk(n == 3, 'test-task344 (kip8-only): бамп v515→v516 ×%d' % n)

# ============================================================
# 7. Контроль версий
# ============================================================
print('=== 7. Контроль ===')
tot_516 = tot_517 = 0
for f in sorted(os.listdir(T8)):
    if not (f.startswith('test-') and f.endswith('.js')):
        continue
    s = rd(os.path.join(T8, f))
    tot_516 += s.count('kipia-v516')
    tot_517 += s.count('kipia-v517')
chk(550 < tot_516 < 700, 'ассертов kipia-v516: %d (паритет ~604)'
    % tot_516)
chk(100 < tot_517 < 200, 'guards kipia-v517: %d (паритет ~146)'
    % tot_517)
# kipia-test-v допустимы ТОЛЬКО исторические негативы kip8
# (количество == количеству в HEAD e5e21a1 ПО КАЖДОМУ файлу)
bad = []
for f in sorted(os.listdir(T8)):
    if not (f.startswith('test-') and f.endswith('.js')):
        continue
    c = rd(os.path.join(T8, f)).count('kipia-test-v')
    try:
        allowed = git(K8, 'show', 'HEAD:tests/%s' % f).count(
            'kipia-test-v')
    except RuntimeError:
        allowed = 0          # новый файл партии
    if c > allowed:
        bad.append((f, c, allowed))
chk(not bad, 'kipia-test-v: только исторические негативы kip8: %r'
    % (bad[:5],))

print('\n===== ЧАСТЬ 2 ЗАВЕРШЕНА: %d FAIL =====' % len(fail))
for m in fail:
    print('FAIL: %s' % m)
if fail:
    sys.exit(1)
print('Дальше: node tests/run-all.js (ожидание 6128/0)')
