#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 499 (kip8): ПРОДОЛЖЕНИЕ tests2 (после падения проверки).

Бамп (гарды v523→v524, ассерты v522→v523) УЖЕ применён — проверка
«left == 1» была ошибочной (истор. комментарий run-all заменился
вместе с ассертами). Осталось: восстановить истор. комментарий 498,
скопировать test-task499.js с MAP, зарегистрировать в run-all.
"""
import io

T = '/home/z/my-project/kip8/tests'
SRC = '/home/z/my-project/kip8test/tests/test-task499.js'

# ---- (2) восстановление истор. комментария 497 в run-all ----
# (до бампа был v522 — состояние из Task 498; бамп 499 не должен был
# его трогать — КАМЕНЬ из 498: истор. комментарии не "едут" с бампом)
f = T + '/run-all.js'
s = io.open(f, encoding='utf-8').read()
old_hist = '// SW kipia-v523 (MAP kipia-test-v721).'
n_hist = s.count(old_hist)
if n_hist:
    assert n_hist == 1, 'истор. комментарий 497 не найден: %d' % n_hist
    s = s.replace(old_hist, '// SW kipia-v522 (MAP kipia-test-v721).')
    io.open(f, 'w', encoding='utf-8').write(s)
    print('run-all.js: истор. комментарий 497 восстановлен (v522/v721 — как до бампа).')
else:
    assert s.count('// SW kipia-v522 (MAP kipia-test-v721).') == 1
    print('run-all.js: истор. комментарий 497 уже восстановлен (v522).')

# ---- (3) копирование нового теста с MAP ----
s = io.open(SRC, encoding='utf-8').read()
assert s.count('kipia-test-v723') >= 3, 'исходник v723?'
assert s.count('kipia-test-v724') == 2, 'гард v724: %d (ожидалось 2 — титул + ассерт)' % s.count('kipia-test-v724')
s = s.replace('kipia-test-v724', 'kipia-v524')
s = s.replace('kipia-test-v723', 'kipia-v523')
s = s.replace('//   D. SW kipia-test-v723 (guard v724).',
              '//   D. SW kipia-v523 (guard v524).')
io.open(T + '/test-task499.js', 'w', encoding='utf-8').write(s)
print('test-task499.js скопирован с MAP (v523/v524).')

# ---- (4) регистрация в run-all ----
f = T + '/run-all.js'
s = io.open(f, encoding='utf-8').read()
old = "require('./test-task498.js');"
assert s.count(old) == 1
s = s.replace(old, old + "\nrequire('./test-task499.js');\n// SW kipia-v523 (MAP kipia-test-v723).")
io.open(f, 'w', encoding='utf-8').write(s)
print('run-all.js: зарегистрирован test-task499.js.')
