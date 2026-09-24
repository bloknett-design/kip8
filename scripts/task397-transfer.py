#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 397-transfer: перенос тестов из kip8test в kip8.
#   · tests/test-task397.js — копия из kip8test@771f014 с маппингом
#     версий SW: kipia-test-v625 → kipia-v473, kipia-test-v626 →
#     kipia-v474 (guards);
#   · tests/run-all.js — регистрация test-task397.js (после 396,
#     перед test-deploy-url.js).
import io, shutil

SRC = '../kip8test/tests/test-task397.js'
DST = 'tests/test-task397.js'

s = io.open(SRC, encoding='utf-8').read()
# «до-бамп» форма (как task395-transfer): ассерт v472 (текущая
# версия kip8 ДО бампа) + guard v473 — двухшаговый бамп ниже
# канонизирует: ассерт v473 + guard v474
n_map = s.count('kipia-test-v625')
s = s.replace('kipia-test-v625', 'kipia-v472')
n_guard = s.count('kipia-test-v626')
s = s.replace('kipia-test-v626', 'kipia-v473')
assert 'kipia-test-v' not in s, 'остались тестовые версии SW'
io.open(DST, 'w', encoding='utf-8').write(s)
print('test-task397.js: скопирован в до-бамп форме (v625→v472: %d, v626→v473: %d)' % (n_map, n_guard))

# run-all.js: регистрация
P2 = 'tests/run-all.js'
r = io.open(P2, encoding='utf-8').read()
old = "require('./test-task396.js');\nrequire('./test-deploy-url.js');"
new = """require('./test-task396.js');
// Task 397: ОБЩЕЕ ПРАВИЛО — кнопка раздела без доступа НЕ
// отображается (универсальный проход по onclick-navigateTo +
// карта JS-кнопок; калькуляторы нижнего бара; композит docs
// упрощён; бар скрыт без видимых кнопок)
require('./test-task397.js');
require('./test-deploy-url.js');"""
assert r.count(old) == 1, 'run-all.js: якорь регистрации не найден'
io.open(P2, 'w', encoding='utf-8').write(r.replace(old, new))
print('run-all.js: test-task397.js подключён')
