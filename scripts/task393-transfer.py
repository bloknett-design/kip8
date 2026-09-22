#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 393 — ПЕРЕНОС тестовой части из kip8test в БОЕВОЙ kip8:
#   1) адаптация 6 тестов (385/388/389/390/391/392) — моки/ассерты
#      под _renderWorkerCardPanels (как task393-adapt-tests.py);
#   2) копия tests/test-task393.js из ../kip8test с контентной
#      адаптацией SW-версий: kipia-test-v621 → kipia-v468 (ассерты),
#      kipia-test-v622 → kipia-v469 (guards) — состояние «до бампа»
#      kip8 (текущая v468);
#   3) регистрация теста в tests/run-all.js;
#   4) SW-бамп kipia-v468 → v469 (порядок ВАЖЕН: СНАЧАЛА guards
#      v469 → v470, ЗАТЕМ ассерты v468 → v469).
import glob
import io
import shutil
import sys

MOCK_LINE_1_8 = "        '_renderWorkerCard: function(tabNo, withEdit) {' +\n"
MOCK_LINE_2_8 = "        '  return \"CARD:\" + tabNo + \":\" + (withEdit ? \"edit\" : \"view\"); },' +\n"
PANEL_LINE_1_8 = "        '_renderWorkerCardPanels: function(tabNo, withEdit) {' +\n"
PANEL_LINE_2_8 = ("        '  return \\'<div class=\"ws-wcard\">CARD:\\' + tabNo + "
                  "\\':\\' + (withEdit ? \"edit\" : \"view\") + \\'</div>\\'; },' +\n")

MOCK_8 = MOCK_LINE_1_8 + MOCK_LINE_2_8
MOCK_8_NEW = (MOCK_LINE_1_8 + MOCK_LINE_2_8 +
              "        // Task 393: страница «Работники» рендерит ПАНЕЛИ блоков карточки\n" +
              PANEL_LINE_1_8 + PANEL_LINE_2_8)

MOCK_LINE_1_12 = "            '_renderWorkerCard: function(tabNo, withEdit) {' +\n"
MOCK_LINE_2_12 = "            '  return \"CARD:\" + tabNo + \":\" + (withEdit ? \"edit\" : \"view\"); },' +\n"
PANEL_LINE_1_12 = "            '_renderWorkerCardPanels: function(tabNo, withEdit) {' +\n"
PANEL_LINE_2_12 = ("            '  return \\'<div class=\"ws-wcard\">CARD:\\' + tabNo + "
                   "\\':\\' + (withEdit ? \"edit\" : \"view\") + \\'</div>\\'; },' +\n")

MOCK_12 = MOCK_LINE_1_12 + MOCK_LINE_2_12
MOCK_12_NEW = (MOCK_LINE_1_12 + MOCK_LINE_2_12 +
               "            // Task 393: страница «Работники» рендерит ПАНЕЛИ блоков карточки\n" +
               PANEL_LINE_1_12 + PANEL_LINE_2_12)


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


print('Task 393 — перенос тестовой части в kip8:')

# --- 1) адаптация тестов (зеркально kip8test) ---
patch('tests/test-task385.js', [
    ("""    const HOST_METHODS = [
        '_renderEmpPopup', '_renderWorkerCard', '_renderWorkersPage',""",
     """    const HOST_METHODS = [
        '_renderEmpPopup', '_renderWorkerCard', '_renderWorkerCardPanels',
        '_renderWorkersPage',""", 1),
    ("""        assertTrue(fn.indexOf('ws-wcard') !== -1, 'обёртка карточки .ws-wcard');""",
     """        assertTrue(fn.indexOf('_renderWorkerCardPanels') !== -1,
            'обёртка карточки — панели .ws-wcard (Task 393)');""", 1),
    ("""        assertTrue(fn.indexOf('_renderWorkerCard(empTabNo, withEdit)') !== -1,
            'карточка — общий рендер с withEdit');""",
     """        assertTrue(fn.indexOf('_renderWorkerCardPanels(empTabNo, withEdit)') !== -1,
            'карточка — панели блоков с withEdit (Task 393)');""", 1),
    ("""assertEqual((body2.match(/ws-wcard/g) || []).length, 1, 'карточка выбранного');""",
     """assertEqual((body2.match(/ws-wcard/g) || []).length, 4,
            'карточка выбранного — ЧЕТЫРЕ блока-окна (Task 393)');""", 1),
])

patch('tests/test-task388.js', [
    ("""        assertTrue(fn.indexOf('_renderWorkerCard(empTabNo, withEdit)') !== -1,
            'тело вкладки работника — полная карточка');""",
     """        assertTrue(fn.indexOf('_renderWorkerCardPanels(empTabNo, withEdit)') !== -1,
            'тело вкладки работника — четыре блока-панели (Task 393)');""", 1),
    (MOCK_12, MOCK_12_NEW, 1),
])

for f in ['tests/test-task389.js', 'tests/test-task390.js',
          'tests/test-task391.js', 'tests/test-task392.js']:
    patch(f, [(MOCK_8, MOCK_8_NEW, 1)])

# --- 2) копия test-task393.js с адаптацией SW-версий ---
src = io.open('../kip8test/tests/test-task393.js', encoding='utf-8').read()
assert src.count("CACHE_VERSION = 'kipia-test-v621'") == 1, 'ассерт v621'
assert src.count('kipia-test-v622') == 1, 'guard v622'
src = src.replace("CACHE_VERSION = 'kipia-test-v621'", "CACHE_VERSION = 'kipia-v468'")
src = src.replace('kipia-test-v622', 'kipia-v469')
src = src.replace("test('SW: kipia-test-v621'", "test('SW: kipia-v468'")
assert 'kipia-test' not in src, 'хвосты kipia-test в тесте'
io.open('tests/test-task393.js', 'w', encoding='utf-8').write(src)
print('  ok tests/test-task393.js (SW-версии: ассерт kipia-v468, guard kipia-v469)')

# --- 3) регистрация в run-all.js ---
patch('tests/run-all.js', [
    ("""require('./test-task392.js');
require('./test-deploy-url.js');""",
     """require('./test-task392.js');
// Task 393: карточка работника на странице «Работники» — ШРИФТ
// КРУПНЕЕ + ЧЕТЫРЕ отдельных блока-окна (профиль с действиями /
// отпуска / мероприятия / СИЗ); попап шахматки — прежний вид
require('./test-task393.js');
require('./test-deploy-url.js');""", 1),
])

# --- 4) SW-бамп kipia-v468 -> v469 ---
sw = io.open('sw.js', encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v468'"
new = "CACHE_VERSION = 'kipia-v469'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v468'
assert 'kipia-v469' not in sw, 'sw.js: v469 уже был (двойной бамп?)'
sw = sw.replace(old, new)
io.open('sw.js', 'w', encoding='utf-8').write(sw)
print('  ok sw.js: CACHE_VERSION kipia-v468 -> kipia-v469')

changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = io.open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v469')
    s = s.replace('kipia-v469', 'kipia-v470')
    n_assert = s.count('kipia-v468')
    s = s.replace('kipia-v468', 'kipia-v469')
    if s != orig:
        io.open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('  ok tests: SW-бамп затронул %d файлов' % len(changed))

print('Готово: перенос тестовой части завершён.')
