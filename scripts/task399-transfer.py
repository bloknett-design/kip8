#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 399-transfer: перенос тестов из kip8test в kip8.
#   · tests/test-task399.js — копия из kip8test@35c68c2 с маппингом
#     версий SW: kipia-test-v627 → kipia-v474, kipia-test-v628 →
#     kipia-v475 (guards);
#   · tests/run-all.js — регистрация test-task399.js (после 398,
#     перед test-deploy-url.js).
import io

SRC = '../kip8test/tests/test-task399.js'
DST = 'tests/test-task399.js'

s = io.open(SRC, encoding='utf-8').read()
# «до-бамп» форма (как task397/398-transfer): ассерт v474 (текущая
# версия kip8 ДО бампа) + guard v475 — двухшаговый бамп ниже
# канонизирует: ассерт v475 + guard v476
n_map = s.count('kipia-test-v627')
s = s.replace('kipia-test-v627', 'kipia-v474')
n_guard = s.count('kipia-test-v628')
s = s.replace('kipia-test-v628', 'kipia-v475')
assert 'kipia-test-v' not in s, 'остались тестовые версии SW'
io.open(DST, 'w', encoding='utf-8').write(s)
print('test-task399.js: скопирован в до-бамп форме (v627→v474: %d, v628→v475: %d)' % (n_map, n_guard))

# run-all.js: регистрация
P2 = 'tests/run-all.js'
r = io.open(P2, encoding='utf-8').read()
old = "require('./test-task398.js');\nrequire('./test-deploy-url.js');"
new = """require('./test-task398.js');
// Task 399 — заявка «если нет доступа к просмотру информации
// мастеров в табеле, то и в окне мероприятий не должно быть
// информации мастеров (мероприятия, отпуска, СИЗ)»: уровень min —
// записи мастеров исключаются из всех трёх секций окна
// (_isMasterKipia, как фильтр сетки Task 340); edit/view — полное
require('./test-task399.js');
require('./test-deploy-url.js');"""
assert r.count(old) == 1, 'run-all.js: якорь регистрации не найден'
io.open(P2, 'w', encoding='utf-8').write(r.replace(old, new))
print('run-all.js: test-task399.js подключён')
