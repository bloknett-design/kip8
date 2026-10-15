#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 527 — ИСПРАВЛЕНИЕ переноса тестов kip8: task527-transfer-tests.py
обрезал test-task526.js/test-task527.js по ПЕРВОМУ разделителю «// ===»
(баг: index() вместо rindex() до маркера «5. SW»). Здесь файлы
пересобираются ЦЕЛИКОМ из версий kip8test; бамп v536→v537 уже выполнен
корректно (остальные файлы, sw.js, run-all) — НЕ повторяется; SW-секции
пишутся сразу в ПОСТ-БАМП состоянии (ассерт v537, гвард v536).
"""
import io
import sys

T = '/home/z/my-project/kip8test'
K = '/home/z/my-project/kip8'


def read(p):
    return io.open(p, encoding='utf-8').read()


def write(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


def swap_sw(src, new_sw):
    """Заменяет хвост файла начиная с разделителя ПЕРЕД секцией «5. SW»."""
    marker = src.rindex('// 5. SW')
    sw_start = src.rindex('// ===========', 0, marker)
    return src[:sw_start] + new_sw


# ---------- 1. test-task526.js ----------
src = read(T + '/tests/test-task526.js')
new_sw = """// ============================================================
// 5. SW — версия кэша бампнута (index.html менялся)
// ============================================================
describe('Task 526 — SW: версия кэша', () => {

    test('SW: кэш поднят до kipia-v537 (Task 526)', () => {
        assertTrue(SW_SRC.indexOf('kipia-v537') !== -1,
            'SW несёт версию kipia-v537');
        assertTrue(SW_SRC.indexOf('kipia-v536') === -1,
            'прежней версии kipia-v536 нет');
    });
});
"""
src = swap_sw(src, new_sw)
src = src.replace('//   SW: kipia-test-v740.', '//   SW: kipia-v537.')
write(K + '/tests/test-task526.js', src)

# ---------- 2. test-task527.js ----------
src = read(T + '/tests/test-task527.js')
new_sw = """// ============================================================
// 5. SW — версия кэша бампнута (index.html менялся)
// ============================================================
describe('Task 527 — SW: версия кэша', () => {

    test('SW: кэш поднят до kipia-v537 (Task 527)', () => {
        assertTrue(SW_SRC.indexOf('kipia-v537') !== -1,
            'SW несёт версию kipia-v537');
        assertTrue(SW_SRC.indexOf('kipia-v536') === -1,
            'прежней версии kipia-v536 нет');
    });
});
"""
src = swap_sw(src, new_sw)
src = src.replace('//   SW: kipia-test-v740.', '//   SW: kipia-v537.')
write(K + '/tests/test-task527.js', src)

# ---------- Контроль ----------
ok = True
for f in ['test-task526.js', 'test-task527.js']:
    s = read(K + '/tests/' + f)
    lines = s.count('\n')
    tests = s.count('    test(')
    has_vm = 'engineCtx' in s
    print('%s: %d строк, %d тестов, VM-слой %s' % (f, lines, tests, 'есть' if has_vm else 'НЕТ'))
    if lines < 200 or tests < 15 or not has_vm:
        ok = False
if not ok:
    print('ОШИБКА: файлы неполные')
    sys.exit(1)
print('OK — файлы пересобраны целиком.')
