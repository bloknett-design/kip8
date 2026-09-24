#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 394 — ПЕРЕНОС тестовой части из kip8test в БОЕВОЙ kip8:
#   1) копия tests/test-task394.js из ../kip8test с контентной
#      адаптацией SW-версий: kipia-test-v622 → kipia-v469 (ассерты),
#      kipia-test-v623 → kipia-v470 (guards) — состояние «до бампа»
#      kip8 (текущая v469);
#   2) регистрация теста в tests/run-all.js;
#   3) SW-бамп kipia-v469 → v470 (порядок ВАЖЕН: СНАЧАЛА guards
#      v470 → v471, ЗАТЕМ ассерты v469 → v470).
# (Правки index.html и адаптация тестов 393/309 — scripts/
#  task394-patch.py и task394-adapt-tests.py, применены ранее.)
import glob
import io
import sys


def patch(path, repl):
    s = io.open(path, encoding='utf-8').read()
    ok = True
    for old, new, cnt in repl:
        n = s.count(old)
        if n != cnt:
            print('  !! %s: якорь x%d (ожидалось x%d): %r' % (path, n, cnt, old[:70]))
            ok = False
            continue
        s = s.replace(old, new)
    if not ok:
        sys.exit(1)
    io.open(path, 'w', encoding='utf-8').write(s)
    print('  ok %s (%d правок)' % (path, len(repl)))


print('Task 394 — перенос тестовой части в kip8:')

# --- 1) копия test-task394.js с адаптацией SW-версий ---
src = io.open('../kip8test/tests/test-task394.js', encoding='utf-8').read()
assert src.count("CACHE_VERSION = 'kipia-test-v622'") == 1, 'ассерт v622'
assert src.count('kipia-test-v623') == 1, 'guard v623'
src = src.replace("CACHE_VERSION = 'kipia-test-v622'", "CACHE_VERSION = 'kipia-v469'")
src = src.replace('kipia-test-v623', 'kipia-v470')
src = src.replace("test('SW: kipia-test-v622'", "test('SW: kipia-v469'")
assert 'kipia-test' not in src, 'хвосты kipia-test в тесте'
io.open('tests/test-task394.js', 'w', encoding='utf-8').write(src)
print('  ok tests/test-task394.js (SW-версии: ассерт kipia-v469, guard kipia-v470)')

# --- 2) регистрация в run-all.js ---
patch('tests/run-all.js', [
    ("""require('./test-task393.js');
require('./test-deploy-url.js');""",
     """require('./test-task393.js');
// Task 394: десктоп — четыре блока карточки СЕТКОЙ 2×2 на весь
// экран (отпуска справа от профиля, СИЗ под отпусками); в карточках
// мероприятия — НА ВЕСЬ ГОД (listTrainings без month); окно
// мероприятий месяца — секции «Отпуска» (пересечение, частично на
// два месяца — в обоих) и «СИЗ» (дата_окончания в месяце)
require('./test-task394.js');
require('./test-deploy-url.js');""", 1),
])

# --- 3) SW-бамп kipia-v469 -> v470 ---
sw = io.open('sw.js', encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v469'"
new = "CACHE_VERSION = 'kipia-v470'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v469'
assert 'kipia-v470' not in sw, 'sw.js: v470 уже был (двойной бамп?)'
sw = sw.replace(old, new)
io.open('sw.js', 'w', encoding='utf-8').write(sw)
print('  ok sw.js: CACHE_VERSION kipia-v469 -> kipia-v470')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = io.open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v470')
    s = s.replace('kipia-v470', 'kipia-v471')
    n_assert = s.count('kipia-v469')
    s = s.replace('kipia-v469', 'kipia-v470')
    if s != orig:
        io.open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('  ok tests: SW-бамп затронул %d файлов' % len(changed))

print('Готово: перенос тестовой части завершён.')
