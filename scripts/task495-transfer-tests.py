#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 495 — kip8: тесты ПЕРЕНОСА.

1. Адаптации 372/373/494 — те же фрагменты, что в kip8test
   (исходники тестов в репо идентичны).
2. Бамп версий: guards kipia-v519 → v520 (сначала), затем ассерты
   kipia-v518 → v519 (180 файлов).
3. Новый test-task495.js — копия kip8test с MAP-версиями:
   kipia-test-v719 → kipia-v519, kipia-test-v718 → kipia-v518,
   kipia-test-v720 → kipia-v520.
4. Регистрация в tests/run-all.js.

Внимание: test-task495.js копируется ПОСЛЕ бампа (иначе скрипт бампа
сдвинет его v519-ассерты на v520).
"""
import io
import glob
import shutil
import sys

K8 = '/home/z/my-project/kip8'
KT = '/home/z/my-project/kip8test'
OK = True


def fail(msg):
    global OK
    OK = False
    print('FAIL: ' + msg)


def rep(path, old, new, cnt=1):
    src = io.open(path, encoding='utf-8').read()
    n = src.count(old)
    if n != cnt:
        fail('%s: фрагмент найден %d раз (ожидался %d):\n%s' %
             (path.split('/')[-1], n, cnt, old[:90]))
        return
    src = src.replace(old, new)
    io.open(path, 'w', encoding='utf-8').write(src)
    print('  OK %s (%d → %d симв.)' %
          (path.split('/')[-1], len(old), len(new)))


T = K8 + '/tests/'

# --- 1. Адаптации -----------------------------------------------------
rep(T + 'test-task372.js',
    "        assertTrue(b.indexOf('id=\"tempSensorViewChip\"') !== -1, 'чип выбранного датчика');\n",
    "        assertFalse(b.indexOf('id=\"tempSensorViewChip\"') !== -1,\n"
    "            'Task 495: чип типа датчика удалён из блока ввода');\n"
    "        assertTrue(b.indexOf('ts-calc-inset') !== -1,\n"
    "            'Task 495: блок таблицы — панель с углублением');\n")

rep(T + 'test-task372.js',
    "        for (const cls of ['.ts-cards-grid', '.ts-card {', '.ts-card-name', '.ts-card-fav-btn',\n"
    "                           '.ts-tabs', '#tempSensorFavBtn', '.ts-view-chip', '.ts-calc-panel']) {\n"
    "            assertTrue(INDEX_SRC.indexOf(cls) !== -1, 'есть правило ' + cls);\n"
    "        }\n",
    "        for (const cls of ['.ts-cards-grid', '.ts-card {', '.ts-card-name', '.ts-card-fav-btn',\n"
    "                           '.ts-tabs', '#tempSensorFavBtn', '.ts-calc-panel',\n"
    "                           '.ts-calc-panel.ts-calc-inset']) {\n"
    "            assertTrue(INDEX_SRC.indexOf(cls) !== -1, 'есть правило ' + cls);\n"
    "        }\n"
    "        // Task 495: правила чипа сняты как неиспользуемые\n"
    "        assertTrue(INDEX_SRC.indexOf('.ts-view-chip') === -1,\n"
    "            'Task 495: CSS-правила чипа удалены');\n")

rep(T + 'test-task372.js',
    "        assertTrue(vmw.els['tempSensorViewChip'].innerHTML.indexOf('50М (Cu50)') !== -1, 'чип: имя');\n"
    "        assertTrue(vmw.els['tempSensorViewChip'].innerHTML.indexOf('R₀ = 50 Ом') !== -1, 'чип: meta');\n"
    "        assertTrue(vmw.els['tempSensorViewChip'].innerHTML.indexOf('ts-card-badge') === -1, 'Task 373: чип без бейджа');\n",
    "        assertFalse('tempSensorViewChip' in vmw.els,\n"
    "            'Task 495: чип удалён — openTempSensor его не трогает');\n")

rep(T + 'test-task373.js',
    "        // чип страницы датчика — без бейджа\n"
    "        const fn = grabFn('openTempSensor');\n"
    "        assertTrue(fn.indexOf('ts-view-chip-name') !== -1, 'чип: имя');\n"
    "        assertTrue(fn.indexOf('ts-card-badge') === -1, 'чип: бейджа нет');\n",
    "        // Task 495: чип удалён — openTempSensor его не заполняет\n"
    "        const fn = grabFn('openTempSensor');\n"
    "        assertTrue(fn.indexOf('ts-view-chip-name') === -1,\n"
    "            'Task 495: заполнение чипа удалено из openTempSensor');\n"
    "        assertTrue(fn.indexOf('ts-card-badge') === -1, 'бейджей нет');\n")

rep(T + 'test-task373.js',
    "        // чип: имя и электроды, без бейджа\n"
    "        const chip = vmw.els['tempSensorViewChip'].innerHTML;\n"
    "        assertTrue(chip.indexOf('ТХК (L)') !== -1, 'чип: имя');\n"
    "        assertTrue(chip.indexOf('хромель-копель') !== -1, 'чип: электроды');\n"
    "        assertTrue(chip.indexOf('ts-card-badge') === -1, 'чип: без бейджа');\n",
    "        // Task 495: чип удалён — ключа в els нет\n"
    "        assertFalse('tempSensorViewChip' in vmw.els,\n"
    "            'Task 495: чип удалён из блока ввода');\n")

rep(T + 'test-task494.js',
    "// Чанк статичной панели: от id=\"tempCustomCalcPanel\" до формы выбора\n"
    "function panelChunk() {\n"
    "    const iPanel = INDEX_SRC.indexOf('id=\"tempCustomCalcPanel\"');\n"
    "    const iRange = INDEX_SRC.indexOf('id=\"temp_sensor_min\"');\n"
    "    if (iPanel === -1 || iRange === -1) return null;\n"
    "    return INDEX_SRC.slice(iPanel, iRange);\n"
    "}\n",
    "// Чанк статичной панели: от id=\"tempCustomCalcPanel\" до панели\n"
    "// таблицы Task 495 (id=\"tempTableFormPanel\") — поля таблицы\n"
    "// (min/max/шаг) получили класс ts-calc-field в Task 495, поэтому\n"
    "// конец чанка перенесён с формы выбора на новую панель.\n"
    "function panelChunk() {\n"
    "    const iPanel = INDEX_SRC.indexOf('id=\"tempCustomCalcPanel\"');\n"
    "    const iRange = INDEX_SRC.indexOf('id=\"tempTableFormPanel\"');\n"
    "    if (iPanel === -1 || iRange === -1) return null;\n"
    "    return INDEX_SRC.slice(iPanel, iRange);\n"
    "}\n")

# --- 2. Бамп версий (guards раньше ассертов) --------------------------
OLD_ASSERT = 'kipia-v518'
NEW_ASSERT = 'kipia-v519'
OLD_GUARD = 'kipia-v519'
NEW_GUARD = 'kipia-v520'

files = sorted(glob.glob(K8 + '/tests/test-*.js'))
files += [K8 + '/tests/run-all.js']
total_guard = total_assert = touched = 0
for f in files:
    s = io.open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count(OLD_GUARD)
    if n_guard:
        s = s.replace(OLD_GUARD, NEW_GUARD)
        total_guard += n_guard
    n_assert = s.count(OLD_ASSERT)
    if n_assert:
        s = s.replace(OLD_ASSERT, NEW_ASSERT)
        total_assert += n_assert
    if s != orig:
        io.open(f, 'w', encoding='utf-8').write(s)
        touched += 1
print('Бамп: файлов %d, guards v519→v520 ×%d, ассертов v518→v519 ×%d' %
      (touched, total_guard, total_assert))
left = sum(io.open(f, encoding='utf-8').read().count(OLD_ASSERT) for f in files)
if left:
    fail('остались ассерты v518: %d' % left)

# --- 3. Новый test-task495.js с MAP-версиями --------------------------
src = io.open(KT + '/tests/test-task495.js', encoding='utf-8').read()
for old, new in [('kipia-test-v719', 'kipia-v519'),
                 ('kipia-test-v718', 'kipia-v518'),
                 ('kipia-test-v720', 'kipia-v520')]:
    src = src.replace(old, new)
# пометка переноса в шапке
src = src.replace(
    '// tests/test-task495.js\n',
    '// tests/test-task495.js (ПЕРЕНОС из kip8test@f1e9be83, Task 495;\n'
    '// версии смаплены kipia-test-v7NN → kipia-v5NN)\n')
io.open(T + 'test-task495.js', 'w', encoding='utf-8').write(src)
print('OK: tests/test-task495.js скопирован с MAP-версиями')
if src.count('kipia-test-v7') != 0:
    fail('в новом тесте остались kipia-test-версии')

# --- 4. Регистрация в run-all.js --------------------------------------
rep(K8 + '/tests/run-all.js',
    "// SW v718. Адаптации: 371 (список панели), 373 (подсказка).\n"
    "require('./test-task494.js');\n",
    "// SW v718. Адаптации: 371 (список панели), 373 (подсказка).\n"
    "require('./test-task494.js');\n"
    "// Task 495 (ПЕРЕНОС из kip8test@f1e9be83): блок ввода данных\n"
    "// расчёта таблицы — поле типа датчика (чип) и тексты «Тип\n"
    "// датчика» / «Шаг расчёта таблицы в градусах Цельсия» удалены;\n"
    "// блок оформлен как панель произвольного расчёта (ts-calc-panel\n"
    "// + ts-calc-field), но с эффектом УГЛУБЛЕНИЯ (ts-calc-inset).\n"
    "// SW v519. Адаптации: 372/373 (чип), 494 (граница чанка панели).\n"
    "require('./test-task495.js');\n")

print('RESULT: %s' % ('OK' if OK else 'FAIL'))
sys.exit(0 if OK else 1)
