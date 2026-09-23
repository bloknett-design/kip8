#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 398-transfer: перенос тестов из kip8test в kip8.
#   · tests/test-task398.js — копия из kip8test@90a024c с маппингом
#     версий SW: kipia-test-v626 → kipia-v473, kipia-test-v627 →
#     kipia-v474 (guards);
#   · tests/run-all.js — регистрация test-task398.js (после 397,
#     перед test-deploy-url.js).
import io

SRC = '../kip8test/tests/test-task398.js'
DST = 'tests/test-task398.js'

s = io.open(SRC, encoding='utf-8').read()
# «до-бамп» форма (как task397-transfer): ассерт v473 (текущая
# версия kip8 ДО бампа) + guard v474 — двухшаговый бамп ниже
# канонизирует: ассерт v474 + guard v475
n_map = s.count('kipia-test-v626')
s = s.replace('kipia-test-v626', 'kipia-v473')
n_guard = s.count('kipia-test-v627')
s = s.replace('kipia-test-v627', 'kipia-v474')
assert 'kipia-test-v' not in s, 'остались тестовые версии SW'
io.open(DST, 'w', encoding='utf-8').write(s)
print('test-task398.js: скопирован в до-бамп форме (v626→v473: %d, v627→v474: %d)' % (n_map, n_guard))

# run-all.js: регистрация
P2 = 'tests/run-all.js'
r = io.open(P2, encoding='utf-8').read()
old = "require('./test-task397.js');\nrequire('./test-deploy-url.js');"
new = """require('./test-task397.js');
// Task 398 — заявка «почему роли КИП ИОС видна кнопка "Работники"
// в табеле, хотя доступа и перехода нет»: атрибут hidden перебивался
// авторским CSS (.ws-refresh-btn{display:inline-flex}); универсальное
// правило [hidden]{display:none!important} восстанавливает семантику
// атрибута — кнопка СКРЫТА уровням null/min, JS-гейты не тронуты
require('./test-task398.js');
require('./test-deploy-url.js');"""
assert r.count(old) == 1, 'run-all.js: якорь регистрации не найден'
io.open(P2, 'w', encoding='utf-8').write(r.replace(old, new))
print('run-all.js: test-task398.js подключён')
