#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 355 (kip8): актуализация 3 тестов + перенос test-task355.js
# из kip8test (замены версий) + run-all.js require.
# Аналог правок, сделанных в kip8test (те же строки).
import re

OLD_EXPR = "(showMainCode ? status : (vacPlan ? 'ОТ' : '·'))"
NEW_EXPR = "(showMainCode ? status : (vacPlan ? 'ОТ' : (dayOff ? '' : '·')))"

# 1. test-work-schedule.js — 2 вхождения выражения + розовый светлой темы
p = 'tests/test-work-schedule.js'
s = open(p, encoding='utf-8').read()
n = s.count(OLD_EXPR)
assert n == 2, 'tws expr: %d' % n
s = s.replace(OLD_EXPR, NEW_EXPR)
old_pink = """        test('CSS: светлая тема — слабый пастельный розовый (#f7d9e3)', () => {
            const re = /\\[data-theme="light"\\] \\.ws-grid tbody td\\.ws-cell\\.ws-weekend\\.ws-status-empty \\{[^}]*background:\\s*#f7d9e3;/;
            assertTrue(re.test(html),
                'Светлая тема: пастельно-розовый фон пустых ячеек выходных');
        });"""
new_pink = """        test('CSS: светлая тема — слабый пастельный розовый (#f8e2e9)', () => {
            // Task 355 (заявка: «пастельнее и бледнее»): #f7d9e3 → #f8e2e9
            const re = /\\[data-theme="light"\\] \\.ws-grid tbody td\\.ws-cell\\.ws-weekend\\.ws-status-empty \\{[^}]*background:\\s*#f8e2e9;/;
            assertTrue(re.test(html),
                'Светлая тема: пастельно-розовый фон пустых ячеек выходных (Task 355)');
        });"""
assert old_pink in s, 'tws pink not found'
s = s.replace(old_pink, new_pink)
open(p, 'w', encoding='utf-8').write(s)
print('test-work-schedule.js: 2 expr + pink')

# 2. test-task312.js — выражение
p = 'tests/test-task312.js'
s = open(p, encoding='utf-8').read()
assert s.count(OLD_EXPR) == 1, 't312 expr: %d' % s.count(OLD_EXPR)
s = s.replace(OLD_EXPR, NEW_EXPR)
s = s.replace("""        // символ в ячейке — «·» (U+00B7) как у пустых
        assertTrue(""",
"""        // символ в ячейке — «·» (U+00B7) как у пустых
        // Task 355: в нерабочих днях (dayOff) «·» НЕ выводится
        assertTrue(""")
s = s.replace("'«.» и пустая ячейка показывают один и тот же «·»'",
              "'«.» и пустая ячейка показывают один и тот же «·» (в нерабочих — пусто, Task 355)'")
open(p, 'w', encoding='utf-8').write(s)
print('test-task312.js: expr + comment')

# 3. test-task319.js — розовый тёмной темы
p = 'tests/test-task319.js'
s = open(p, encoding='utf-8').read()
old_dark = """    test('CSS: тёмная тема — выходные/пустые/бейджи как в светлой', () => {
        assertTrue(cssRule(/\\[data-theme="dark"\\] \\.ws-grid tbody td\\.ws-cell\\.ws-weekend\\.ws-status-empty \\{[^}]*background:\\s*#f7d9e3;[^}]*\\}/s),
            'пустые выходные — #f7d9e3 (светлая тема), не #6e4250');"""
new_dark = """    test('CSS: тёмная тема — выходные/пустые/бейджи как в светлой', () => {
        // Task 355: розовый выходных — пастельнее (#f7d9e3 → #f8e2e9,
        // тот же цвет, что в светлой теме)
        assertTrue(cssRule(/\\[data-theme="dark"\\] \\.ws-grid tbody td\\.ws-cell\\.ws-weekend\\.ws-status-empty \\{[^}]*background:\\s*#f8e2e9;[^}]*\\}/s),
            'пустые выходные — #f8e2e9 (светлая тема, Task 355), не #6e4250');"""
assert old_dark in s, 't319 dark not found'
s = s.replace(old_dark, new_dark)
open(p, 'w', encoding='utf-8').write(s)
print('test-task319.js: dark pink')

# 4. test-task355.js — копия из kip8test с версиями kip8
src = open('/home/z/my-project/kip8test/tests/test-task355.js', encoding='utf-8').read()
src = src.replace('kipia-test-v584', 'kipia-v432')
src = src.replace('kipia-test-v585', 'kipia-v433')
src = src.replace('SW: версия кэша kipia-test-v584', 'SW: версия кэша kipia-v432')
open('tests/test-task355.js', 'w', encoding='utf-8').write(src)
print('test-task355.js: скопирован (kipia-v432/v433)')

# 5. run-all.js — require
p = 'tests/run-all.js'
s = open(p, encoding='utf-8').read()
anchor = "require('./test-task354.js');\n"
assert anchor in s, 'run-all anchor'
add = anchor + """// Task 355 — шахматка табеля: «·» убрана из нерабочих выходных/праздничных
// ячеек; линии ячеек и шапки (дни месяца) тонкие 1px, но ярче (30% чёрного
// в светлой / стале-голубой 55% в тёмной); розовый выходных пастельнее
// #f7d9e3 → #f8e2e9 (обе темы)
require('./test-task355.js');
"""
s = s.replace(anchor, add)
open(p, 'w', encoding='utf-8').write(s)
print('run-all.js: require добавлен')
