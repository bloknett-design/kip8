#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 499 (kip8): окна sw.js — фиксы по kip8-геометрии (замеры от
const-строки версии, комментарий 499 ~430 симв.):

  474: 'Task 474'@10069, окно 9700 → 10600 (+sync-литералы в 481/475/486)
  480: 'Task 480'@8413, окно 8100 → 8900 (+sync-литерал в 482)
  481-w700: Task 480@8413, окно 8100 → 8900
  482: '_barExpMaxH'@7763, окно 7400 → 8300
  482-480/481: Task 480@8413, окно 8100 → 8900
  483: 'Task 483'@7055, окно 6700 → 7500
"""
import io

T = '/home/z/my-project/kip8/tests/'


def apply(path, edits):
    s = io.open(path, encoding='utf-8').read()
    for name, old, new in edits:
        n = s.count(old)
        assert n == 1, 'ЯКОРЬ %s (%s): вхождений %d (ожидалось 1)' % (name, path, n)
        s = s.replace(old, new)
        print('  OK %s' % name)
    io.open(path, 'w', encoding='utf-8').write(s)


apply(T + 'test-task474.js', [
    ('474: окно 9700 → 10600',
     "        const ctx = SW_SRC.slice(Math.max(0, i - 9700), i);",
     "        // Task 499: окно 9700 → 10600 — комментарий плейсхолдеров\n"
     "        // (~430 симв.) отодвинул Task 474 до ~10069.\n"
     "        const ctx = SW_SRC.slice(Math.max(0, i - 10600), i);"),
])

apply(T + 'test-task480.js', [
    ('480: окно 8100 → 8900',
     "        const ctx = SW_SRC.slice(Math.max(0, i - 8100), i);",
     "        // Task 499: комментарий плейсхолдеров (~430 симв.) отодвинул\n"
     "        // Task 480 до ~8413 — окно 8100 → 8900.\n"
     "        const ctx = SW_SRC.slice(Math.max(0, i - 8900), i);"),
])

apply(T + 'test-task481.js', [
    ('481: w700 8100 → 8900',
     "        const w700 = SW_SRC.slice(Math.max(0, i - 8100), i);",
     "        // Task 499: окно 8100 → 8900 — Task 480 отодвинут до ~8413.\n"
     "        const w700 = SW_SRC.slice(Math.max(0, i - 8900), i);"),
    ('481: sync s474 9700 → 10600',
     "        assertTrue(s474.indexOf('i - 9700') !== -1, 'test-task474: окно 5300');",
     "        assertTrue(s474.indexOf('i - 10600') !== -1, 'test-task474: окно 10600 (Task 499)');"),
])

apply(T + 'test-task482.js', [
    ('482: окно 7400 → 8300',
     "        const ctx = SW_SRC.slice(Math.max(0, i - 7400), i);",
     "        // Task 499: _barExpMaxH отодвинут до ~7763 — окно 7400 → 8300.\n"
     "        const ctx = SW_SRC.slice(Math.max(0, i - 8300), i);"),
    ('482: 481/480-окно 8100 → 8900',
     "        // Task 493 (перенос): комментарий переименования кнопки Табель\n"
     "        // (+173 симв.) — 480@6650/«Перечень…»@6615 — окно 6600 → 6800\n"
     "        const ctx = SW_SRC.slice(Math.max(0, i - 8100), i);",
     "        // Task 493 (перенос): комментарий переименования кнопки Табель\n"
     "        // (+173 симв.) — 480@6650/«Перечень…»@6615 — окно 6600 → 6800\n"
     "        // Task 499: Task 480/481 отодвинуты до ~8413/8169 — окно 8100 → 8900.\n"
     "        const ctx = SW_SRC.slice(Math.max(0, i - 8900), i);"),
    ('482: sync s480 8100 → 8900',
     "        assertTrue(s480.indexOf('i - 8100') !== -1, 'test-task480: окно 7200 (Task 494)');",
     "        assertTrue(s480.indexOf('i - 8900') !== -1, 'test-task480: окно 8900 (Task 499)');"),
])

apply(T + 'test-task483.js', [
    ('483: окно 6700 → 7500',
     "        const ctx = SW_SRC.slice(Math.max(0, i - 6700), i);",
     "        // Task 499: Task 483 отодвинут до ~7055 — окно 6700 → 7500.\n"
     "        const ctx = SW_SRC.slice(Math.max(0, i - 7500), i);"),
])

apply(T + 'test-task475.js', [
    ('475: sync s(474) 9700 → 10600',
     "        assertTrue(s.indexOf('i - 9700') !== -1, 'окно Task 474: 5300');",
     "        assertTrue(s.indexOf('i - 10600') !== -1, 'окно Task 474: 10600 (Task 499)');"),
])

apply(T + 'test-task486.js', [
    ('486: каскад 481 9700 → 10600',
     "        assertTrue(s481.indexOf(\"'i - 9700'\") !== -1, 'каскад 481: 471 → 9700 (Task 496)');",
     "        assertTrue(s481.indexOf(\"'i - 10600'\") !== -1, 'каскад 481: 474 → 10600 (Task 499)');"),
])

print('Окна kip8 (Task 499): применены.')
