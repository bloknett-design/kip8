#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 497 (ПЕРЕНОС в kip8): тесты.
#   1) Адаптации старых тестов (окна sw.js-комментариев 472/493/494 +
#      каскады 481/475; окно init 358; маркеры веток loading/error
#      Task 238 — favEmpty497 встречается раньше веток; датозависимый
#      409 — срок 10.10.2026 истёк 11.10.2026, «просрочено с…» тоже
#      валиден) — ДО бампа, на текущих литералах kipia-v520.
#   2) Бамп: СНАЧАЛА гарды kipia-v521→v522 (×150), ЗАТЕМ ассерты
#      kipia-v520→v521 (×622).
#   3) Копирование tests/test-task497.js из kip8test с MAP версий
#      (kipia-test-v721→kipia-v521, v722→v522, v720→v520) — ПОСЛЕ
#      бампа (файл не попадает под замены).
#   4) Регистрация в tests/run-all.js.
import io
import glob

T8 = '/home/z/my-project/kip8test'
T = '/home/z/my-project/kip8/tests'


def patch(path, old, new, label):
    s = io.open(path, encoding='utf-8').read()
    assert s.count(old) >= 1, '%s: якорь не найден: %r' % (path, old[:60])
    s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8').write(s)
    print('OK %-40s %s' % (path.split('/')[-1], label))


# ---------- 1. Адаптации (до бампа) ----------
patch(T + '/test-task472.js',
      """        // Task 492: комментарий (~290 симв.) отодвинул якорь Task 472
        // до ~8730 — окно 8500 → 9300.
        const ctx = SW_SRC.slice(Math.max(0, i - 9900), i);""",
      """        // Task 492: комментарий (~290 симв.) отодвинул якорь Task 472
        // до ~8730 — окно 8500 → 9300.
        // Task 497: комментарий избранного расходомеров — якорь
        // 472@9882 — окно 9900 → 10300 (запас 418).
        const ctx = SW_SRC.slice(Math.max(0, i - 10300), i);""",
      'окно 472: 9900→10300')

patch(T + '/test-task493.js',
      """        const i = SW_SRC.indexOf("const CACHE_VERSION = 'kipia-v520';");
        const ctx = SW_SRC.slice(Math.max(0, i - 900), i);
        assertTrue(ctx.indexOf('Task 493') !== -1, 'маркер задачи');""",
      """        const i = SW_SRC.indexOf("const CACHE_VERSION = 'kipia-v520';");
        // Task 497: комментарий избранного расходомеров — якорь
        // 493@1240 — окно 900 → 1400 (запас 160).
        const ctx = SW_SRC.slice(Math.max(0, i - 1400), i);
        assertTrue(ctx.indexOf('Task 493') !== -1, 'маркер задачи');""",
      'окно 493: 900→1400')

patch(T + '/test-task494.js',
      """        const i = SW_SRC.indexOf("const CACHE_VERSION = 'kipia-v520';");
        const ctx = SW_SRC.slice(Math.max(0, i - 900), i);
        assertTrue(ctx.indexOf('Task 494') !== -1, 'маркер задачи');""",
      """        const i = SW_SRC.indexOf("const CACHE_VERSION = 'kipia-v520';");
        // Task 497: комментарий избранного расходомеров — якорь
        // 494@1064 — окно 900 → 1200 (запас 136).
        const ctx = SW_SRC.slice(Math.max(0, i - 1200), i);
        assertTrue(ctx.indexOf('Task 494') !== -1, 'маркер задачи');""",
      'окно 494: 900→1200')

patch(T + '/test-task481.js',
      """        const s472 = fs.readFileSync(path.join(ROOT, 'tests', 'test-task472.js'), 'utf8');
        assertTrue(s472.indexOf('i - 9900') !== -1, 'test-task472: окно 9300 (Task 492)');""",
      """        const s472 = fs.readFileSync(path.join(ROOT, 'tests', 'test-task472.js'), 'utf8');
        assertTrue(s472.indexOf('i - 10300') !== -1, 'test-task472: окно 10300 (Task 497)');""",
      'каскад 481: 9900→10300')

patch(T + '/test-task475.js',
      """        const s = fs.readFileSync(path.join(ROOT, 'tests', 'test-task472.js'), 'utf8');
        assertTrue(s.indexOf('i - 9900') !== -1, 'окно Task 472: 9300 (Task 492)');""",
      """        const s = fs.readFileSync(path.join(ROOT, 'tests', 'test-task472.js'), 'utf8');
        assertTrue(s.indexOf('i - 10300') !== -1, 'окно Task 472: 10300 (Task 497)');""",
      'каскад 475: 9900→10300')

patch(T + '/test-task358.js',
      """        const initSrc = INDEX_SRC.slice(i, i + 4000);""",
      """        // Task 497: блок мгновенного рендера избранного (~800 симв.)
        // в середине init — флаш/watchers у конца, окно 4000 → 5000.
        const initSrc = INDEX_SRC.slice(i, i + 5000);""",
      'окно init 358: 4000→5000')

patch(T + '/test-flowmeter-validation.js',
      """    test('renderList(): ветка loading показывает «Загрузка данных»', () => {
        var marker = "this._loadState === 'loading'";
        var loadingIdx = src.indexOf(marker);""",
      """    test('renderList(): ветка loading показывает «Загрузка данных»', () => {
        // Task 497 (адаптация): сравнение '_loadState === \\'loading\\''
        // встречается и в условии favEmpty497 (раньше ветки) — ищем
        // именно ВЕТКУ else-if загрузки.
        var marker = "} else if (this._loadState === 'loading') {";
        var loadingIdx = src.indexOf(marker);""",
      'маркер loading 238')

patch(T + '/test-flowmeter-validation.js',
      """    test('renderList(): ветка error показывает «Нет связи с сервером»', () => {
        var marker = "this._loadState === 'error'";
        var errorIdx = src.indexOf(marker);""",
      """    test('renderList(): ветка error показывает «Нет связи с сервером»', () => {
        // Task 497 (адаптация): как и с loading — ищем ВЕТКУ else-if
        // ошибки, не условие favEmpty497.
        var marker = "} else if (this._loadState === 'error') {";
        var errorIdx = src.indexOf(marker);""",
      'маркер error 238')

patch(T + '/test-task409.js',
      """        assertTrue(seg.indexOf('след. срок: 10.10.2026') !== -1,
            'запись 10.04.2026 + 6 мес');""",
      """        // Адаптация даты (Task 497, 11.10.2026): срок 10.10.2026 ИСТЁК —
        // рендер показывает «⚠ просрочено с 10.10.2026» (dueIso < today),
        // до истечения показывал «след. срок: 10.10.2026 ✓». Обе формы —
        // один и тот же вычисленный срок: запись 10.04.2026 + 6 мес.
        assertTrue(seg.indexOf('10.10.2026') !== -1 &&
                   (seg.indexOf('след. срок: 10.10.2026') !== -1 ||
                    seg.indexOf('просрочено с 10.10.2026') !== -1),
            'запись 10.04.2026 + 6 мес = 10.10.2026 (будущее «след. срок», прошедшее «просрочено»)');""",
      'дата 409')

# ---------- 2. Бамп версий (гарды → потом ассерты) ----------
files = sorted(glob.glob(T + '/test-*.js')) + [T + '/run-all.js']
total_guard = total_assert = 0
for f in files:
    s = io.open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v521')
    if n_guard:
        s = s.replace('kipia-v521', 'kipia-v522')
        total_guard += n_guard
    n_assert = s.count('kipia-v520')
    if n_assert:
        s = s.replace('kipia-v520', 'kipia-v521')
        total_assert += n_assert
    if s != orig:
        io.open(f, 'w', encoding='utf-8').write(s)
assert total_guard == 150, 'гардов %d ≠ 150' % total_guard
assert total_assert == 622, 'ассертов %d ≠ 622' % total_assert
print('Бамп: гарды v521→v522 ×%d, ассерты v520→v521 ×%d' %
      (total_guard, total_assert))

# контроль: в тестах kip8 не осталось v520
left = sum(io.open(f, encoding='utf-8').read().count('kipia-v520')
           for f in files)
assert left == 0, 'остались v520: %d' % left
print('Контроль: v520 в тестах kip8 отсутствует')

# ---------- 3. Копирование test-task497.js с MAP версий ----------
src = io.open(T8 + '/tests/test-task497.js', encoding='utf-8').read()
mapping = [('kipia-test-v721', 'kipia-v521'),
           ('kipia-test-v722', 'kipia-v522'),
           ('kipia-test-v720', 'kipia-v520')]
for old, new in mapping:
    src = src.replace(old, new)
assert src.count('kipia-v521') >= 1 and src.count('kipia-v522') == 1
assert src.count('kipia-test') == 0, 'остались kipia-test-литералы'
io.open(T + '/test-task497.js', 'w', encoding='utf-8').write(src)
print('test-task497.js скопирован (MAP kipia-test→kipia, v521/v522/v520)')

# ---------- 4. Регистрация в run-all.js ----------
patch(T + '/run-all.js',
      """require('./test-task496.js');""",
      """require('./test-task496.js');
// Task 497 (баг-репорт): «Расходомеры хозрасчётные» — при наличии
// избранного карточки показываются СРАЗУ из локального кэша (до
// ответа сервера; рендер в init после _restoreCache), а заглушка
// «Нет избранных расходомеров» больше не появляется в состояниях
// loading/error при наличии избранного (только когда его действительно
// нет). SW v521 (MAP kipia-test-v721).
require('./test-task497.js');""",
      'регистрация 497')

print('ВСЁ применено')
