#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# task365-port.py — перенос Task 365 из kip8test (4a22d39) в kip8 (35eee49):
#   1. index.html — cp де-изолированного /tmp/kip8_index_transfer.html
#      (подготовлен scripts/prepare-kip8-transfer.py из kip8test при 4a22d39;
#      дифф с kip8/index.html проверен пофрагментно = ровно зона Task 365:
#      комментарий CSS .flow-summary-val-due, _normalizeMeters в 3 точках
#      данных + функция, комментарий _isOverdue)
#   2. data/flowmeters.json — №12 «Еженедельно» → «Ежедневно» (+ \n в конце)
#   3. SW-бамп kipia-v441 → v442. Порядок замен в tests/ ВАЖЕН (урок 361):
#      СНАЧАЛА guard-ы «v442 не существует» → v443, ЗАТЕМ ассерты v441 → v442.
# Запуск из корня репо kip8.
import glob
import json
import shutil

# --- 1. index.html ---
shutil.copyfile('/tmp/kip8_index_transfer.html', 'index.html')
html = open('index.html', encoding='utf-8').read()
assert '_normalizeMeters' in html and html.count('_normalizeMeters') == 4, \
    'index.html: _normalizeMeters ожидается 4 вхождения (3 вызова + определение), есть %d' % html.count('_normalizeMeters')
assert 'окна 6:00–7:00 нет' in html, 'index.html: комментарий Task 365 не найден'
assert 'isolateLocalStorage' not in html, 'index.html: изоляция не должна попасть в kip8'
print('[1] index.html: перенесён (4 вхождения _normalizeMeters, изоляции нет)')

# --- 2. data/flowmeters.json ---
raw = open('data/flowmeters.json', encoding='utf-8').read()
data = json.loads(raw)
m12 = [m for m in data['meters'] if m.get('id') == 12]
assert len(m12) == 1, '№12 не найден'
assert m12[0]['period'] == 'Еженедельно', '№12: неожиданный период «%s»' % m12[0]['period']
m12[0]['period'] = 'Ежедневно'
out = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
open('data/flowmeters.json', 'w', encoding='utf-8').write(out)
check = json.loads(open('data/flowmeters.json', encoding='utf-8').read())
assert [m for m in check['meters'] if m['id'] == 12][0]['period'] == 'Ежедневно'
print('[2] data/flowmeters.json: №12 период «Ежедневно», записей %d' % len(check['meters']))

# --- 3. SW-бамп kipia-v441 → v442 ---
sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v441'"
new = "CACHE_VERSION = 'kipia-v442'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v441'
assert 'kipia-v442' not in sw, 'sw.js: v442 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('[3] sw.js: CACHE_VERSION kipia-v441 -> kipia-v442')

# tests/*.js — guard v442→v443, затем ассерты v441→v442
changed = []
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v442')
    s = s.replace('kipia-v442', 'kipia-v443')
    n_assert = s.count('kipia-v441')
    s = s.replace('kipia-v441', 'kipia-v442')
    # сообщения guard-ов — под новую цель v443 (косметика)
    s = s.replace('v442 ещё не существует', 'v443 ещё не существует')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed.append((f, n_assert, n_guard))
print('[4] tests изменено файлов: %d' % len(changed))

# контроль
sw2 = open(sw_path, encoding='utf-8').read()
assert sw2.count('kipia-v442') == 1
leftover = []
for f in glob.glob('tests/*.js'):
    s = open(f, encoding='utf-8').read()
    if 'kipia-v441' in s and 'истор' not in f:
        # исторические guard-версии (v428/433/434) допустимы, v441 — нет
        for i, line in enumerate(s.splitlines(), 1):
            if 'kipia-v441' in line:
                leftover.append('%s:%d' % (f, i))
print('[контроль] sw.js: единственный kipia-v442' + ('; ПРЕДУПРЕЖДЕНИЕ v441 в tests: %s' % leftover if leftover else ''))
print('OK — порт Task 365 применён к kip8')
