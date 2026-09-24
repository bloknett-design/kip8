#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# task371-374-port-tests.py — перенос тестов Tasks 371–374 из
# kip8test в kip8 (запускать из корня kip8).
# Версионный маппинг (4 задачи пакета: v448=371 … v451=374):
#   kipia-test-v603 → kipia-v451   (текущая — asserts)
#   kipia-test-v604 → kipia-v452   (guard «ещё не существует»)
# Файлы: новые 371–374 + адаптированный test-role-access.js
# (Task 372: temp-sensors → страница карточек, расчёт — на
# temp-sensor-view; других отличий нет — проверено диффом).
# Затем базовый бамп остальных тестов kip8: guard v448→v452,
# ассерты v447→v451 (исторические v441…v446 не трогаются).
# run-all.js правится отдельно (у kip8 свой набор комментариев).
import io, os, sys, glob

SRC = '/home/z/my-project/kip8test/tests'
DST = 'tests'

NEW = ['test-task371.js', 'test-task372.js', 'test-task373.js',
       'test-task374.js']
ADAPTED = ['test-role-access.js']

def adapt(s):
    # порядок важен: сначала guard v604, затем asserts v603
    s = s.replace('kipia-test-v604', 'kipia-v452')
    s = s.replace('kipia-test-v603', 'kipia-v451')
    s = s.replace('v604 ещё не существует', 'v452 ещё не существует')
    return s

for name in NEW + ADAPTED:
    src = io.open(os.path.join(SRC, name), encoding='utf-8').read()
    out = adapt(src)
    rest = [w for w in out.split() if w.startswith('kipia-test-v')]
    if rest:
        print('ОСТАЛИСЬ тест-версии в %s: %s' % (name, sorted(set(rest))))
        sys.exit(1)
    io.open(os.path.join(DST, name), 'w', encoding='utf-8').write(out)
    kind = 'адаптирован' if name in ADAPTED else 'перенесён'
    print('%s: %s' % (name, kind))

# --- базовый бамп остальных тестов kip8 (guards v448→v452, asserts v447→v451) ---
changed = []
for f in sorted(glob.glob('tests/*.js')):
    if os.path.basename(f) in NEW or os.path.basename(f) == 'run-all.js':
        continue
    s = io.open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v448')
    s = s.replace('kipia-v448', 'kipia-v452')
    n_assert = s.count('kipia-v447')
    s = s.replace('kipia-v447', 'kipia-v451')
    s = s.replace('v448 ещё не существует', 'v452 ещё не существует')
    s = s.replace('v447 ещё не существует', 'v452 ещё не существует')
    if s != orig:
        io.open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('базовый бамп: %d файлов' % len(changed))
tot_a = sum(a for _, a, _ in changed)
tot_g = sum(g for _, _, g in changed)
print('  ассертов v447→v451: %d, guard-ов v448→v452: %d' % (tot_a, tot_g))

# --- контроль: v451 ровно 1 в sw.js, v447/v448 не осталось нигде в tests ---
sw = io.open('sw.js', encoding='utf-8').read()
assert sw.count("CACHE_VERSION = 'kipia-v451'") == 1, 'sw.js: v451'
leftover = []
for f in glob.glob('tests/*.js'):
    s = io.open(f, encoding='utf-8').read()
    if 'kipia-v447' in s or 'kipia-v448' in s:
        leftover.append(os.path.basename(f))
if leftover:
    print('ОСТАЛИСЬ старые версии в: %s' % leftover)
    sys.exit(1)
print('OK: %d новых/адаптированных + %d базовых, старых версий не осталось' %
      (len(NEW) + len(ADAPTED), len(changed)))
