#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 497 (ПЕРЕНОС в kip8): продолжение transfer-tests после бампа.
# Бамп прошёл (гарды v521→v522 ×150, ассерты v520→v521 ×624 = 622
# тестовых + 2 истор. комментария 496 в run-all.js — замер 622 их
# не учёл, сканировал только test-*.js). По прецеденту переноса 496
# («истор. комм. run-all — восстановлены 493/494/495 «v519»»)
# восстанавливаем историческое значение комментария 496 → v520,
# затем докатываем шаги 3-4: копирование test-task497.js (MAP
# версий) и регистрация в run-all.js.
import io

T8 = '/home/z/my-project/kip8test'
T = '/home/z/my-project/kip8/tests'


def patch(path, old, new, label):
    s = io.open(path, encoding='utf-8').read()
    assert s.count(old) >= 1, '%s: якорь не найден: %r' % (path, old[:60])
    s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8').write(s)
    print('OK %-40s %s' % (path.split('/')[-1], label))


# ---------- 0. Восстановить историческое значение 496-комментария ----------
patch(T + '/run-all.js',
      """// stopPropagation + blur). SW kipia-v521. MAP kipia-test-v720
// → kipia-v521. Границы: блок таблицы (next×2) и глобальный""",
      """// stopPropagation + blur). SW kipia-v520. MAP kipia-test-v720
// → kipia-v520. Границы: блок таблицы (next×2) и глобальный""",
      'история 496 восстановлена (v520)')

# ---------- 1. Копирование test-task497.js с MAP версий ----------
src = io.open(T8 + '/tests/test-task497.js', encoding='utf-8').read()
for old, new in [('kipia-test-v721', 'kipia-v521'),
                 ('kipia-test-v722', 'kipia-v522'),
                 ('kipia-test-v720', 'kipia-v520')]:
    src = src.replace(old, new)
assert src.count('kipia-v521') >= 1 and src.count('kipia-v522') == 1
assert src.count('kipia-test') == 0, 'остались kipia-test-литералы'
io.open(T + '/test-task497.js', 'w', encoding='utf-8').write(src)
print('test-task497.js скопирован (MAP kipia-test→kipia, v521/v522/v520)')

# ---------- 2. Регистрация в run-all.js ----------
patch(T + '/run-all.js',
      """require('./test-task496.js');""",
      """require('./test-task496.js');
// Task 497 (ПЕРЕНОС из kip8test@e8b7d6f6, баг-репорт):
// «Расходомеры хозрасчётные» — при наличии избранного карточки
// показываются СРАЗУ из локального кэша (до ответа сервера; рендер
// в init после _restoreCache), а заглушка «Нет избранных
// расходомеров» больше не появляется в состояниях loading/error
// при наличии избранного (только когда его действительно нет).
// SW kipia-v521 (MAP kipia-test-v721).
require('./test-task497.js');""",
      'регистрация 497')

print('ВСЁ докатано')
