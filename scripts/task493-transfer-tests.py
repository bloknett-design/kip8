#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 493 — перенос в kip8: бамп SW-версий в тестах + адаптации
подписи «Табель учёта» + новый test-task493.js (kip8-версии).

Порядок (как в kip8test/scripts/task493-bump-sw.py):
  1) guards: kipia-v517 → kipia-v518 (assertFalse «следующей версии нет»)
  2) asserts: kipia-v516 → kipia-v517 (assertTrue «текущая версия»)
  3) адаптации: test-task321.js (чанк кнопки + regex реестра),
     test-work-schedule.js (regex реестра, блок Task 267)
  4) новый tests/test-task493.js — копия kip8test с заменой SW-версий
     (kipia-test-v717 → kipia-v517, guard v718 → v518) и пометкой MAP
  5) регистрация в run-all.js
Каждая замена с count-ассертом.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(ROOT, 'tests')
SRC = os.path.join(ROOT, '..', 'kip8test', 'tests', 'test-task493.js')

def replace_in(path, old, new, expected):
    with io.open(path, encoding='utf-8') as f:
        s = f.read()
    n = s.count(old)
    if n != expected:
        print('FAIL %s: %r найдено %d, ожидалось %d' % (os.path.basename(path), old, n, expected))
        return False
    if old == new:
        return True
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(s.replace(old, new))
    print('OK   %s: %d × замена' % (os.path.basename(path), n))
    return True

ok = True

# --- 1) guards v517 → v518; 2) asserts v516 → v517 ---
total_g, total_a = 0, 0
files = sorted(f for f in os.listdir(TESTS) if f.endswith('.js'))
for fn in files:
    p = os.path.join(TESTS, fn)
    with io.open(p, encoding='utf-8') as f:
        s = f.read()
    total_g += s.count('kipia-v517')
    total_a += s.count('kipia-v516')
for fn in files:
    p = os.path.join(TESTS, fn)
    with io.open(p, encoding='utf-8') as f:
        s = f.read()
    g = s.count('kipia-v517')
    if g:
        ok = replace_in(p, 'kipia-v517', 'kipia-v518', g) and ok
for fn in files:
    p = os.path.join(TESTS, fn)
    with io.open(p, encoding='utf-8') as f:
        s = f.read()
    a = s.count('kipia-v516')
    if a:
        ok = replace_in(p, 'kipia-v516', 'kipia-v517', a) and ok
print('GUARDS v517→v518: %d, ASSERTS v516→v517: %d' % (total_g, total_a))

# --- 3) адаптации подписи ---
p = os.path.join(TESTS, 'test-task321.js')
ok = replace_in(
    p,
    """        assertTrue(chunk.indexOf('Табель учёта рабочего времени') !== -1,
            'menu-btn-label — новое имя');""",
    """        // Task 493: кнопка переименована короче — «Табель учёта»
        assertTrue(chunk.indexOf('<div class="menu-btn-label">Табель учёта</div>') !== -1,
            'menu-btn-label — «Табель учёта» (Task 493, короче)');""",
    1) and ok
ok = replace_in(
    p,
    """        assertTrue(/'work-schedule':\\s*\\{ label: 'Табель учёта рабочего времени'/.test(INDEX_SRC),
            'SUBSECTIONS: новая метка (закрепление на главной)');""",
    """        assertTrue(/'work-schedule':\\s*\\{ label: 'Табель учёта'/.test(INDEX_SRC),
            'SUBSECTIONS: метка «Табель учёта» (Task 493 — закрепление на главной)');""",
    1) and ok

p = os.path.join(TESTS, 'test-work-schedule.js')
ok = replace_in(
    p,
    """            const re = /'work-schedule':\\s*\\{ label: 'Табель учёта рабочего времени',\\s*sublabel: 'Шахматка сменного и дневного персонала',\\s*target: 'work-schedule',\\s*category: 'docs' \\}/;""",
    """            // Task 493: label короче — «Табель учёта» (кнопка; заголовок
            // страницы/крошки остались полными)
            const re = /'work-schedule':\\s*\\{ label: 'Табель учёта',\\s*sublabel: 'Шахматка сменного и дневного персонала',\\s*target: 'work-schedule',\\s*category: 'docs' \\}/;""",
    1) and ok

# --- 4) новый test-task493.js с kip8-версиями ---
with io.open(SRC, encoding='utf-8') as f:
    t = f.read()
# SW-версии: test → prod; guard v718 → v518
t = t.replace("kipia-test-v717", "kipia-v517")
t = t.replace("kipia-test-v716", "kipia-v516")
t = t.replace("kipia-test-v718", "kipia-v518")
t = t.replace("// tests/test-task493.js",
              "// tests/test-task493.js (kip8 — перенос Task 493 из kip8test; "
              "MAP: kipia-test-v717→kipia-v517, guard v718→v518)")
dst = os.path.join(TESTS, 'test-task493.js')
with io.open(dst, 'w', encoding='utf-8') as f:
    f.write(t)
print('OK   test-task493.js записан (kip8-версии, %d байт)' % len(t))

# --- 5) регистрация в run-all.js ---
p = os.path.join(TESTS, 'run-all.js')
with io.open(p, encoding='utf-8') as f:
    r = f.read()
if "test-task493.js" not in r:
    marker = "require('./test-task492.js');"
    add = marker + """
// Task 493 (перенос из kip8test) — кнопка «Табель учёта рабочего
// времени», закрепляемая на главную, переименована короче — «Табель
// учёта»: статическая кнопка на page-docs-ios (workScheduleMenuBtn) +
// label в реестре SUBSECTIONS (рендер закрепления renderPinnedItems);
// заголовок страницы, крошки PAGE_LABELS и пункт сайдбара — прежние
// полные имена. SW kipia-v517 (MAP из kip8test v717).
// Адаптации: 321 (кнопка/реестр), work-schedule (реестр, блок 267).
require('./test-task493.js');"""
    if marker not in r:
        print('FAIL run-all.js: маркер 492 не найден')
        ok = False
    else:
        r = r.replace(marker, add, 1)
        with io.open(p, 'w', encoding='utf-8') as f:
            f.write(r)
        print('OK   run-all.js: test-task493.js зарегистрирован')
else:
    print('OK   run-all.js: уже зарегистрирован')

print('RESULT: %s' % ('OK' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
