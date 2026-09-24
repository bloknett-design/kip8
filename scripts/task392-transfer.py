#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 392: перенос из kip8test в kip8 — тесты и SW.
#   1) sw.js: kipia-v467 → kipia-v468
#   2) существующие тесты: guard v468 → v469 (СНАЧАЛА), затем
#      ассерты v467 → v468 (конвенция бампов)
#   3) tests/test-task392.js — копия из ../kip8test/tests/ с
#      маппингом kipia-test-v620 → kipia-v468 (ассерты) и
#      kipia-test-v621 → kipia-v469 (guard)
#   4) контентные адаптации (как scripts/task392-adapt-tests.py
#      кip8test + точечные фиксы): формат «Работников на текущий
#      момент N (…)» в task391/389/390/388, _appendRowKeepText
#      4→5 (tab-numbers), loadGrid(true) 15→18 (task314),
#      require('./test-task392.js') в run-all.js
import glob, io, os, sys

def patch(path, repls):
    s = io.open(path, encoding='utf-8').read()
    for i, (old, new) in enumerate(repls):
        n = s.count(old)
        if n != 1:
            print('FAIL %s: якорь #%d найден %d раз: %r' % (path, i + 1, n, old[:60]))
            sys.exit(1)
    for (old, new) in repls:
        s = s.replace(old, new)
    io.open(path, 'w', encoding='utf-8').write(s)
    print('  OK %s: %d правок' % (path, len(repls)))

# --- 1) sw.js: v467 → v468 ---
sw_path = 'sw.js'
sw = io.open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v467'"
new = "CACHE_VERSION = 'kipia-v468'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v467'
assert 'kipia-v468' not in sw, 'sw.js: v468 уже был (двойной бамп?)'
io.open(sw_path, 'w', encoding='utf-8').write(sw.replace(old, new))
print('  OK sw.js: CACHE_VERSION kipia-v467 -> kipia-v468')

# --- 2) существующие тесты: guards v468→v469, ассерты v467→v468 ---
changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = io.open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v468')
    s = s.replace('kipia-v468', 'kipia-v469')
    n_assert = s.count('kipia-v467')
    s = s.replace('kipia-v467', 'kipia-v468')
    if s != orig:
        io.open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('tests (версии): изменено файлов: %d' % len(changed))
for f, a, g in changed:
    print('  %s (ассерты v467→v468: %d, guard v468→v469: %d)' % (f, a, g))

# --- 3) копия test-task392.js с маппингом версий ---
src = io.open('../kip8test/tests/test-task392.js', encoding='utf-8').read()
n620 = src.count('kipia-test-v620')
n621 = src.count('kipia-test-v621')
src = src.replace('kipia-test-v621', 'kipia-v469')
src = src.replace('kipia-test-v620', 'kipia-v468')
io.open('tests/test-task392.js', 'w', encoding='utf-8').write(src)
print('  OK tests/test-task392.js: копия из kip8test (ассерты v620→v468: %d, guard v621→v469: %d)' % (n620, n621))

# --- 4) контентные адаптации ---
patch('tests/test-task391.js', [
    (r"""        assertTrue(fn.indexOf("'(' + totalN + ') ('") !== -1,
            'скобки подряд: (итог) (разбивка)');""",
     r"""        assertTrue(fn.indexOf("totalN + ' ('") !== -1,
            'Task 392: ведущее число БЕЗ скобок, разбивка — в скобках');"""),
    (r"""'Работников на текущий момент (6) (2 мастера, 2 дневных, 2 сменных).') !== -1,""",
     r"""'Работников на текущий момент 6 (2 мастера, 2 дневных, 2 сменных).') !== -1,"""),
    (r"""'Работников на текущий момент (4) (1 мастер, 1 дневной, 2 сменных).') !== -1,""",
     r"""'Работников на текущий момент 4 (1 мастер, 1 дневной, 2 сменных).') !== -1,"""),
    (r"""'Работников на текущий момент (0) (0 мастеров, 0 дневных, 0 сменных).') !== -1,""",
     r"""'Работников на текущий момент 0 (0 мастеров, 0 дневных, 0 сменных).') !== -1,"""),
    (r"""body.indexOf('Работников на текущий момент (6)') !== -1,""",
     r"""body.indexOf('Работников на текущий момент 6') !== -1,"""),
])

patch('tests/test-task389.js', [
    (r"""'Работников на текущий момент (3) (0 мастеров, 1 дневной, 2 сменных).') !== -1,""",
     r"""'Работников на текущий момент 3 (0 мастеров, 1 дневной, 2 сменных).') !== -1,"""),
    (r"""'Работников на текущий момент (0) (0 мастеров, 0 дневных, 0 сменных).') !== -1,""",
     r"""'Работников на текущий момент 0 (0 мастеров, 0 дневных, 0 сменных).') !== -1,"""),
    (r"""'Работников на текущий момент (2) (0 мастеров, 1 дневной, 1 сменный).') !== -1,""",
     r"""'Работников на текущий момент 2 (0 мастеров, 1 дневной, 1 сменный).') !== -1,"""),
])

patch('tests/test-task390.js', [
    (r"""'Работников на текущий момент (6) (2 мастера, 2 дневных, 2 сменных).') !== -1,""",
     r"""'Работников на текущий момент 6 (2 мастера, 2 дневных, 2 сменных).') !== -1,"""),
    (r"""'Работников на текущий момент (0) (0 мастеров, 0 дневных, 0 сменных).') !== -1,""",
     r"""'Работников на текущий момент 0 (0 мастеров, 0 дневных, 0 сменных).') !== -1,"""),
    (r"""'Работников на текущий момент (3) (1 мастер, 1 дневной, 1 сменный).') !== -1,""",
     r"""'Работников на текущий момент 3 (1 мастер, 1 дневной, 1 сменный).') !== -1,"""),
    (r"""'Работников на текущий момент (3) (2 мастера, 0 дневных, 1 сменный).') !== -1,""",
     r"""'Работников на текущий момент 3 (2 мастера, 0 дневных, 1 сменный).') !== -1,"""),
    # SRC-ассерт скобок (точечный фикс, как в kip8test)
    (r"""        assertTrue(fn.indexOf("'(' + totalN + ') ('") !== -1,
            'формат «(итог) (разбивка)» — скобки подряд (Task 391)');""",
     r"""        assertTrue(fn.indexOf("totalN + ' ('") !== -1,
            'Task 392: ведущее число БЕЗ СКОБОК, разбивка — в скобках');"""),
])

patch('tests/test-task388.js', [
    (r"""        assertTrue(body.indexOf('(3) (0 мастеров, 1 дневной, 2 сменных)') !== -1,
            'шапка: (3) (0 мастеров, 1 дневной, 2 сменных) — Task 391');""",
     r"""        assertTrue(body.indexOf('3 (0 мастеров, 1 дневной, 2 сменных)') !== -1,
            'шапка: 3 (0 мастеров, 1 дневной, 2 сменных) — Task 392 (итог без скобок)');"""),
    (r"""        assertTrue(html.indexOf('(3) (0 мастеров, 1 дневной, 2 сменных)') !== -1,
            'шапка: (3) (0 мастеров, 1 дневной, 2 сменных) — Task 391');""",
     r"""        assertTrue(html.indexOf('3 (0 мастеров, 1 дневной, 2 сменных)') !== -1,
            'шапка: 3 (0 мастеров, 1 дневной, 2 сменных) — Task 392 (итог без скобок)');"""),
])

patch('tests/test-tab-numbers.js', [
    (r"""    test('WorkSchedule.gs: _appendRowKeepText вызывается из 4 CRUD-функций', () => {
        const uses = WS_SRC.split('this._appendRowKeepText(').length - 1;
        assertEqual(uses, 4, 'addEmployee + addTraining + addVacation + setManualEntry');
    });""",
     r"""    test('WorkSchedule.gs: _appendRowKeepText вызывается из 5 CRUD-функций', () => {
        const uses = WS_SRC.split('this._appendRowKeepText(').length - 1;
        assertEqual(uses, 5, 'addEmployee + addTraining + addVacation + setManualEntry + addPpe (Task 392)');
    });"""),
])

patch('tests/test-task314.js', [
    (r"""        // Task 384: +2 — правка данных сотрудника (updateEmployee) и
        // правка периода отпуска (updateVacation) из карточки
        const n = (INDEX_SRC.match(/self\.loadGrid\(true\);/g) || []).length;
        assertEqual(n, 15, '14 мутаций + 1 в refreshData = 15 вызовов loadGrid(true)');""",
     r"""        // Task 384: +2 — правка данных сотрудника (updateEmployee) и
        // правка периода отпуска (updateVacation) из карточки
        // Task 392: +3 — СИЗ: добавление/правка/удаление записи
        const n = (INDEX_SRC.match(/self\.loadGrid\(true\);/g) || []).length;
        assertEqual(n, 18, '17 мутаций + 1 в refreshData = 18 вызовов loadGrid(true)');"""),
])

patch('tests/run-all.js', [
    (r"""require('./test-task391.js');
require('./test-deploy-url.js');""",
     r"""require('./test-task391.js');
// Task 392: ведущее число текущего момента БЕЗ скобок «N (…)»;
// раздел «СИЗ» — лист «СИЗ» табель_КИП_ИОС, секция в карточке
// работника (✎/✕/+), шторка, АВТО-дата окончания (выдача + срок),
// сервер listPpe/addPpe/updatePpe/deletePpe + PPEInit.gs
require('./test-task392.js');
require('./test-deploy-url.js');"""),
])

print('== Перенос тестов Task 392 в kip8 готов ==')
