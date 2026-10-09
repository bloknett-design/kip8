#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 487-489-transfer ЧАСТЬ 3: DEPLOY-доки ×3 (копия из kip8test
# с адаптацией под kip8: версии v514→v515, проверки kip8
# 6069/0 + SMOKE 58/58 + VLM ×4, шаги развёртывания для kip8).
import io
import os
import re

K8 = '/home/z/my-project/kip8'
K8T = '/home/z/my-project/kip8test'

DOCS = [
    ('DEPLOY-Task487-timesheet-popup-readonly-hover.md',
     [('kipia-test-v710` → `kipia-test-v711', 'kipia-v514` → `kipia-v515'),
      ('(код — kip8test', '(код — kip8, перенесено из kip8test'),
      ('**6003 passed, 0 failed** (было 5976).',
       '**6069 passed, 0 failed** (было 5980).'),
      ('Browser-check (Playwright, порт 8998) — **35/35**',
       'SMOKE kip8 (Playwright, порт 9002, ключи БЕЗ префикса) —'
       ' **58/58** (объединённая проверка партии 487-489)'),
      ]),
    ('DEPLOY-Task488-timesheet-popup-marker-xlsx-simple.md',
     [('kipia-test-v711` → `kipia-test-v712', 'kipia-v514` → `kipia-v515'),
      ('(код — kip8test', '(код — kip8, перенесено из kip8test'),
      ('**6022 passed, 0 failed** (было 6003).',
       '**6069 passed, 0 failed** (было 5980).'),
      ('Browser-check (Playwright, порт 8999, мок Apps Script)',
       'SMOKE kip8 (Playwright, порт 9002, мок Apps Script)'),
      ('— **28/28**', '— блоки A/E объединённой проверки **58/58**'),
      ]),
    ('DEPLOY-Task489-employees-fullname-birth.md',
     [('(код — kip8test @v713)', '(код — kip8 @v515, перенос партии)'),
      ('`v712 → v713`', '`v514 → v515`'),
      ('(v712 → v713)', '(v514 → v515)'),
      ('**6065 passed, 0 failed**', '**6069 passed, 0 failed**'),
      ('`scripts/task489-browser-check.py` — **37/37**',
       '`scripts/task487-489-smoke-k8.py` (объединённый SMOKE'
       ' партии) — **58/58**'),
      ('VLM ×3 (`scripts/task489-vlm-check.js`)',
       'VLM ×4 kip8 (`scripts/task487-489-vlm-check.js`)'),
      ('## Проверки (kip8test)', '## Проверки (kip8)'),
      ('**Перенос в kip8 — ПО КОМАНДЕ пользователя** (в kip8 ждут\n'
       '487+488+489 одним инкрементом kipia-v514→v515).',
       '**ПЕРЕНОС ВЫПОЛНЕН** (kip8 @v515, одним инкрементом'
       ' kipia-v514→v515 по команде «Переноси в kip8»).'),
      ]),
]
# Общие замены для всех трёх
COMMON = [
    ('коммит в kip8test (SW `kipia-test-v713`)',
     'коммит в kip8 (SW `kipia-v515`)'),
    ('коммит в kip8test (SW `kipia-test-v711`)',
     'коммит в kip8 (SW `kipia-v515`)'),
    ('коммит в kip8test (SW `kipia-test-v712`)',
     'коммит в kip8 (SW `kipia-v515`)'),
    ('GitHub Pages (тестовый)', 'GitHub Pages (боевой kip8)'),
]


def adapt(name, pairs):
    s = io.open(os.path.join(K8T, name), encoding='utf-8').read()
    for old, new in pairs + COMMON:
        n = s.count(old)
        s = s.replace(old, new)
        if n == 0 and not old.endswith(')') and 'ПЕРЕНОС' not in old:
            print('  (нет вхождений: %r)' % old[:60])
    out = os.path.join(K8, name)
    io.open(out, 'w', encoding='utf-8').write(s)
    left = [ln for ln in s.splitlines() if 'kipia-test-v7' in ln]
    print('%s: записан (%d симв.), kipia-test-v7 строк: %d'
          % (name, len(s), len(left)))


for name, pairs in DOCS:
    adapt(name, pairs)
print('OK: 3 DEPLOY-дока адаптированы')
