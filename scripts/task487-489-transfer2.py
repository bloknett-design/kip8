#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 487-489-transfer ЧАСТЬ 2 (v3): tests/ — 3-way merge с
# ПОСТРОЧНОЙ НОРМАЛИЗАЦИЕЙ base И theirs к ours.
# УРОК v1: слепой keep-ours на конфликтах ассертов оставлял СТАРЫЕ
# версии (v514 вместо v515); причина — kip8-историкалы (v478/v512/
# v513/v510-имена) живут в ТЕХ ЖЕ блоках SW-describe, что и
# партийные бампы версий, diff3 группирует их в один конфликт.
# УРОК v2: нормализовать ТОЛЬКО base мало — theirs содержит ТЕ ЖЕ
# не-партийные строки с kip8test-историкалами (v705/v708/v709);
# после нормализации base→ours эти строки в theirs выглядят
# «изменёнными» и merge ВЫБИРАЕТ их (порча: v705 в 482, v708/v709
# в 485/486). РЕШЕНИЕ v3: подстановки пар применяем К base И К
# theirs (точное совпадение строки): не-партийные строки становятся
# идентичными во всех трёх, партийные бампы (v713/v714) остаются
# изменениями theirs и применяются ЧИСТО. Ожидание: 0 конфликтов.
# Плюс: test-task344.js — kip8-ONLY (в kip8test его нет) — точечный
# бамп v514→v515 ×3 (прецедент 482-484 «test-task344 v511→v512»).
import io
import os
import re
import subprocess
import sys
import difflib

K8 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
K8T = os.path.abspath(os.path.join(K8, '..', 'kip8test'))
T8 = os.path.join(K8, 'tests')
TMP = '/home/z/my-project/scripts/.k8t-487-489-tmp'
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


MAP_THEIRS = [
    ('kipia-test-v714', 'kipia-v516'),   # guards (next absent)
    ('kipia-test-v713', 'kipia-v515'),   # текущие ассерты
    ('kipia-test-v711', 'kipia-v514'),   # 488 negative (pre-party)
    ('kipia-test-v712', 'kipia-v514'),   # 489 negative (pre-party)
    ('kipia-test-v710', 'kipia-v514'),   # 487 negative (pre-party)
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
    # era-замена: то, что не покрылось построчно (текущая пара
    # эпохи post-486 в kip8test = v710/v711)
    s = s.replace('kipia-test-v710', 'kipia-v514')
    s = s.replace('kipia-test-v711', 'kipia-v515')
    return s, pairs


# ============================================================
# 1. Состав партии
# ============================================================
print('=== 1. Состав партии ===')
party_out = git(K8T, 'diff', '--name-only', '39e7025b..HEAD', '--',
                'tests/')
party = [os.path.basename(f) for f in party_out.splitlines()
         if f.endswith('.js')]
modified = [f for f in party if f not in
            ('run-all.js', 'test-task487.js', 'test-task488.js',
             'test-task489.js')]
chk(len(modified) == 171, 'партия: изменённых тест-файлов %d (ожидалось 171)'
    % len(modified))
missing = [f for f in modified
           if not os.path.exists(os.path.join(T8, f))]
chk(not missing, 'все файлы существуют в kip8: %r' % missing)

# ============================================================
# 2. 3-way merge c нормализованным base (ожидание: 0 конфликтов)
# ============================================================
print('=== 2. 3-way merge (base нормализован к ours) ===')
n_merged = n_identical = 0
n_conf_total = 0
tot_pairs = 0
for name in sorted(modified):
    p8 = os.path.join(T8, name)
    ours = rd(p8)
    base_raw = git(K8T, 'show', '39e7025b:tests/%s' % name)
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
        for ln in merged.split('\n'):
            if ln.startswith('<<<<<<< ours'):
                mode = 'ours'
                ours_buf = []
                continue
            if ln.startswith('||||||| base'):
                mode = 'base'
                continue
            if ln.startswith('======='):
                mode = 'theirs'
                theirs_buf = []
                continue
            if ln.startswith('>>>>>>> theirs'):
                conflicts_report.append(
                    (name, ' | '.join(x.strip()[:90] for x in ours_buf[:2]),
                     ' | '.join(x.strip()[:90] for x in theirs_buf[:2])))
                out.extend(ours_buf)   # keep ours (ожидание: почти нет)
                mode = None
                continue
            if mode == 'ours':
                ours_buf.append(ln)
            elif mode == 'theirs':
                theirs_buf.append(ln)
            elif mode is None or mode == 'base':
                out.append(ln)
        merged = '\n'.join(out)
    if merged != ours:
        wr(p8, merged)
        n_merged += 1
print('  merge: записано %d, без правок %d; пар нормализации %d'
      % (n_merged, n_identical, tot_pairs))
chk(n_merged + n_identical == len(modified), 'merge: все 171 учтены')
chk(n_conf_total == 0,
    'merge: КОНФЛИКТОВ НЕТ (факт: %d)' % n_conf_total)
if conflicts_report:
    for name, o_c, t_c in conflicts_report:
        print('  КОНФЛИКТ %s:\n    OURS:   %s\n    THEIRS: %s'
              % (name, o_c, t_c))

# ============================================================
# 3. Новые файлы 487/488/489 — копия + MAP + версионные правки
# ============================================================
print('=== 3. Новые тесты ===')
FIX_487 = [
    ('kipia-v514 → v711', 'kipia-v514 → v515'),
    ('инкрементирована v710 → v711', 'инкрементирована v514 → v515'),
]
FIX_488 = [
    ('v713 — следующий не занят', 'v516 — следующий не занят'),
    ('v711 отсутствует (один инкремент)', 'v514 отсутствует (один инкремент)'),
    ("'v711 в sw.js не должно быть'", "'v514 в sw.js не должно быть'"),
    ('v713 в sw.js не должно быть (двойной бамп не сделан)',
     'v515 в sw.js не должно быть (двойной бамп не сделан)'),
]
for name, fixes in (('test-task487.js', FIX_487),
                    ('test-task488.js', FIX_488),
                    ('test-task489.js', [])):
    s = mapped(rd(os.path.join(K8T, 'tests', name)), MAP_THEIRS)
    for old, new in fixes:
        n = s.count(old)
        if n != 1:
            fail.append('[%s] правка %r: вхождений %d (ожидалось 1)'
                        % (name, old[:50], n))
        s = s.replace(old, new)
    wr(os.path.join(T8, name), s)
    s2 = rd(os.path.join(T8, name))
    chk('kipia-test-v7' not in s2,
        '%s: записан, kipia-test-v7 нет' % name)

s488 = rd(os.path.join(T8, 'test-task488.js'))
chk(s488.count('kip8test') == 1 and 'заявка (kip8test)' in s488,
    'test-task488: kip8test — только шапка заявки')
s489 = rd(os.path.join(T8, 'test-task489.js'))
chk("path.join(ROOT, 'scripts', 'WorkSchedule.gs')" in s489,
    'test-task489: читает scripts/WorkSchedule.gs (перенесён в ч.1)')

# ============================================================
# 4. run-all.js — вставка +487/+488/+489
# ============================================================
print('=== 4. run-all.js ===')
P_RUN = os.path.join(T8, 'run-all.js')
run8 = rd(P_RUN)
runt = rd(os.path.join(K8T, 'tests', 'run-all.js'))
anchor = "require('./test-task486.js');\nrequire('./test-deploy-url.js');"
chk(run8.count(anchor) == 1, 'run-all: якорь 486→deploy-url найден')
block_t = runt[runt.index("require('./test-task486.js');"):
               runt.index("require('./test-deploy-url.js');")]
insert = block_t[len("require('./test-task486.js');"):]
chk(insert.count('487') >= 2 and insert.count('488') >= 2
    and insert.count('489') >= 2 and 'kipia-test' not in insert,
    'run-all: вставка извлечена (%d симв.)' % len(insert))
run8_new = run8.replace(anchor,
                        "require('./test-task486.js');\n" + insert
                        + "require('./test-deploy-url.js');")
chk(run8_new.count("require('./test-task487.js');") == 1
    and run8_new.count("require('./test-task488.js');") == 1
    and run8_new.count("require('./test-task489.js');") == 1,
    'run-all: +487/+488/+489 зарегистрированы')
wr(P_RUN, run8_new)

# ============================================================
# 5. kip8-специфика: окна 480/481/482 5000→6600; шапки-посадки
# ============================================================
print('=== 5. kip8-специфика ===')
for name in ('test-task480.js', 'test-task481.js', 'test-task482.js'):
    p = os.path.join(T8, name)
    s = rd(p)
    n = s.count('i - 5000')
    chk(n >= 1, '%s: окон 5000 найдено %d' % (name, n))
    s = s.replace('i - 5000', 'i - 6600')
    wr(p, s)

# Шапки-посадки (merge взял theirs' v515 — возвращаем исторические):
restores = [
    ('test-task483.js', '//   SW: kipia-v515 (логика SW не менялась; окна истории',
     '//   SW: kipia-v512 (логика SW не менялась; окна истории'),
    ('test-task484.js', '//   SW: kipia-v515 (логика SW не менялась; окна истории',
     '//   SW: kipia-v512 (логика SW не менялась; окна истории'),
    ('test-task485.js', '//   SW: kipia-v515 (логика SW не менялась; окна истории',
     '//   SW: kipia-v513 (логика SW не менялась; окна истории'),
    ('test-task486.js', '//   SW: kipia-v515 (логика SW НЕ менялась; кэши не тронуты).',
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
# 482: строка посадки в шапке (v511 → v512) не должна содержать
# kip8test-версию (партия добавила только АДАПТАЦИЯ-блок выше)
s482 = rd(os.path.join(T8, 'test-task482.js'))
chk(s482.count('sw.js kipia-test-v') == 0,
    'test-task482: kip8test-строки посадки нет (есть наша v511 → v512)')
chk('sw.js kipia-v511 → v512 + комментарий Task 482' in s482,
    'test-task482: строка посадки v511 → v512 жива')
chk('АДАПТАЦИЯ Task 487' in s482,
    'test-task482: партийный АДАПТАЦИЯ-блок Task 487 перенесён')

# kip8-ONLY файл: test-task344.js (в kip8test отсутствует) —
# точечный бамп версии (прецедент 482-484 «v511→v512 ×3»)
p344 = os.path.join(T8, 'test-task344.js')
if os.path.exists(p344) and not os.path.exists(
        os.path.join(K8T, 'tests', 'test-task344.js')):
    s = rd(p344)
    n = s.count('kipia-v514')
    s = s.replace('kipia-v514', 'kipia-v515')
    wr(p344, s)
    chk(n == 3, 'test-task344 (kip8-only): бамп v514→v515 ×%d' % n)

# 485/486-негативы (v512/v513) должны остаться kip8-историкалами
s485 = rd(os.path.join(T8, 'test-task485.js'))
chk("indexOf('kipia-v512') === -1" in s485,
    'test-task485: негатив v512 (kip8-историкал) сохранён')
s486 = rd(os.path.join(T8, 'test-task486.js'))
chk("indexOf('kipia-v513') === -1" in s486,
    'test-task486: негатив v513 (kip8-историкал) сохранён')

# ============================================================
# 6. Контроль версий
# ============================================================
print('=== 6. Контроль ===')
tot_515 = tot_516 = 0
for f in sorted(os.listdir(T8)):
    if not (f.startswith('test-') and f.endswith('.js')):
        continue
    s = rd(os.path.join(T8, f))
    tot_515 += s.count('kipia-v515')
    tot_516 += s.count('kipia-v516')
chk(550 < tot_515 < 700, 'ассертов kipia-v515: %d (паритет ~598)'
    % tot_515)
chk(100 < tot_516 < 200, 'guards kipia-v516: %d (паритет ~146)' % tot_516)
# kipia-test-v допустимы ТОЛЬКО исторические негативы kip8
# (текущее количество == количеству в HEAD 2735ac0 ПО КАЖДОМУ
# файлу: 341 v57; work-schedule ×8; flow-period ×2; 309-313
# v547-v551 — «старой версии kip8test нет» — одинаковы в обоих)
bad = []
for f in sorted(os.listdir(T8)):
    if not (f.startswith('test-') and f.endswith('.js')):
        continue
    c = rd(os.path.join(T8, f)).count('kipia-test-v')
    try:
        allowed = git(K8, 'show', '2735ac0:tests/%s' % f).count(
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
if conflicts_report:
    wr(os.path.join(TMP, 'conflicts-v2.txt'),
       '\n'.join('%s: OURS=%s THEIRS=%s' % t for t in conflicts_report))
if fail:
    sys.exit(1)
print('Дальше: node tests/run-all.js (ожидание 6069/0)')
