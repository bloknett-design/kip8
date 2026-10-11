#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 499 (kip8): ПРОДОЛЖЕНИЕ адаптации (после частичного прогона).

Первый прогон task499-transfer-tests.py записал (по-файлово атомарно):
rtd, 371, 372, 373, 494, 498, 471 — и упал на якоре 472 (текст
комментария в kip8 отличался). Этот скрипт применяет ОСТАВШИЕСЯ:
472 (×2), 497, каскады 475/481.
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


apply(T + 'test-task472.js', [
    ('472: окно комментария 10300 → 11200',
     """        // Task 497: комментарий избранного расходомеров — якорь
        // 472@9882 — окно 9900 → 10300 (запас 418).
        const ctx = SW_SRC.slice(Math.max(0, i - 10300), i);""",
     """        // Task 497: комментарий избранного расходомеров — якорь
        // 472@9882 — окно 9900 → 10300 (запас 418).
        // Task 499: комментарий плейсхолдеров диапазонов (~430 симв.)
        // — якорь 472@10601 — окно 10300 → 11200 (запас 599).
        const ctx = SW_SRC.slice(Math.max(0, i - 11200), i);"""),
    ('472: контекст 471 — окно 11200 → 12000',
     """        // Task 474 в шапке sw.js отодвинул начало комментария Task 471
        // (~1157 символов).
        const ctx = SW_SRC.slice(Math.max(0, i - 11200), i);""",
     """        // Task 474 в шапке sw.js отодвинул начало комментария Task 471
        // (~1157 символов).
        // Task 499: комментарий плейсхолдеров (~430 симв.) — якорь
        // 471@11153 — окно 11200 → 12000.
        const ctx = SW_SRC.slice(Math.max(0, i - 12000), i);"""),
])

apply(T + 'test-task497.js', [
    ('497: окно 900 → 1300',
     """        const i = SW_SRC.indexOf("const CACHE_VERSION = 'kipia-v522';");
        const ctx = SW_SRC.slice(Math.max(0, i - 900), i);
        assertTrue(ctx.indexOf('Task 497') !== -1, 'маркер задачи');""",
     """        const i = SW_SRC.indexOf("const CACHE_VERSION = 'kipia-v522';");
        // Task 499: комментарий плейсхолдеров диапазонов (~430 симв.)
        // отодвинул Task 497 до ~1054 — окно 900 → 1300.
        const ctx = SW_SRC.slice(Math.max(0, i - 1300), i);
        assertTrue(ctx.indexOf('Task 497') !== -1, 'маркер задачи');"""),
])

apply(T + 'test-task475.js', [
    ('475: s1(471) окно 12000',
     "        assertTrue(s1.indexOf('i - 11200') !== -1, 'test-task471: 11200 (Task 498)');",
     "        assertTrue(s1.indexOf('i - 12000') !== -1, 'test-task471: 12000 (Task 499)');"),
    ('475: s(472) окно 11200',
     "        assertTrue(s.indexOf('i - 10300') !== -1, 'окно Task 472: 10300 (Task 497)');",
     "        assertTrue(s.indexOf('i - 11200') !== -1, 'окно Task 472: 11200 (Task 499)');"),
])

apply(T + 'test-task481.js', [
    ('481: s471 окно 12000',
     "        assertTrue(s471.indexOf('i - 11200') !== -1, 'test-task471: окно 10600 (Task 495)');",
     "        assertTrue(s471.indexOf('i - 12000') !== -1, 'test-task471: окно 12000 (Task 499)');"),
    ('481: s472 окно 11200',
     "        assertTrue(s472.indexOf('i - 10300') !== -1, 'test-task472: окно 10300 (Task 497)');",
     "        assertTrue(s472.indexOf('i - 11200') !== -1, 'test-task472: окно 11200 (Task 499)');"),
])

print('Продолжение адаптаций kip8 (Task 499): применено.')
