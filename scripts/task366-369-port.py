#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# task366-369-port.py — перенос пакета Tasks 366–369 из kip8test (5e6e9ec)
# в kip8 (c230d07 = Task 365, SW kipia-v442):
#   1. index.html — cp де-изолированного /tmp/kip8_index_transfer.html
#      (подготовлен scripts/prepare-kip8-transfer.py из kip8test при 5e6e9ec;
#      дифф с kip8/index.html = 518 строк, проверен пофрагментно — только
#      зоны 366–369: баннер→цвет значений, периодные формы/закрытые
#      периоды, свайп «Проекты» + страница «Проекты по статусу»)
#   2. SW-бамп kipia-v442 → v446 (v443=366, v444=367, v445=368, v446=369).
#   3. Базовый бамп ВСЕХ существующих tests/*.js: guard v443→v447,
#      ассерты v442→v446 (как task365-port.py).
#   4. Перезапись из kip8test с версионым маппингом (ПОСЛЕ базового бампа,
#      чтобы маркер «старая до 366» = v442 не был затёрт):
#        v599→v447 (guard), v598→v446 (текущая), v596→v445 (368 «стала»),
#        v595→v444 (367), v594→v442 (366 «старая до»), v593→v441 (365)
#      Исторические guard-версии (v534/v537/v585/v586) остаются как есть —
#      принятое соглашение kip8.
#   5. run-all.js: +4 require (366–369) после test-task365.js.
# Серверные скрипты НЕ переносились (Code.gs и .gs живут только в kip8test;
# серверная часть Task 366 — FlowmeterArchive.gs — уже обновлена пользователем
# в Apps Script вручную). data/flowmeters.json идентичен — не трогаем.
# Запуск из корня репо kip8.
import glob
import io
import os
import shutil
import sys

SRC = '/home/z/my-project/kip8test/tests'
DST = 'tests'

ADAPT = ['test-task357.js', 'test-task358.js', 'test-task365.js',
         'test-flow-period-input.js', 'test-flowmeter-validation.js',
         'extract-functions.js']
NEW = ['test-task366.js', 'test-task367.js', 'test-task368.js',
       'test-task369.js']

# --- 1. index.html ---
shutil.copyfile('/tmp/kip8_index_transfer.html', 'index.html')
html = open('index.html', encoding='utf-8').read()
markers = {
    366: ['_outboxBannerText удалён вместе с ним', 'server_busy'],
    367: ['flow-summary-val-pending', 'project-card-status-cancel'],  # 2-й маркер относится к 369, ниже уточнён
    368: ['_recordCoversPeriod', 'flowWeekRangeLabel'],
    369: ['projectSwipeCell', 'PROJECT_STATUS_ORDER', 'page-projects-status'],
}
# корректировка: маркер 367 — только pending-цвета
markers[367] = ['flow-summary-val-pending']
assert 'isolateLocalStorage' not in html, 'index.html: изоляция не должна попасть в kip8'
for tid, mks in markers.items():
    for m in mks:
        assert m in html, 'index.html: маркер Task %d не найден: %s' % (tid, m)
assert html.count('_outboxBannerText') == 1, \
    'index.html: _outboxBannerText ожидается 1 (только упоминание «удалён»)'
print('[1] index.html: перенесён, маркеры 366/367/368/369 на месте, изоляции нет')

# --- 2. SW-бамп kipia-v442 → v446 ---
sw_path = 'sw.js'
sw = open(sw_path, encoding='utf-8').read()
old = "CACHE_VERSION = 'kipia-v442'"
new = "CACHE_VERSION = 'kipia-v446'"
assert old in sw, 'sw.js: не найден текущий CACHE_VERSION v442'
assert 'kipia-v446' not in sw, 'sw.js: v446 уже был (двойной бамп?)'
sw = sw.replace(old, new)
open(sw_path, 'w', encoding='utf-8').write(sw)
print('[2] sw.js: CACHE_VERSION kipia-v442 -> kipia-v446')

# --- 3. Базовый бамп существующих тестов (guard, затем ассерты) ---
changed = 0
for f in sorted(glob.glob('tests/*.js')):
    s = open(f, encoding='utf-8').read()
    orig = s
    n_guard = s.count('kipia-v443')
    s = s.replace('kipia-v443', 'kipia-v447')
    n_assert = s.count('kipia-v442')
    s = s.replace('kipia-v442', 'kipia-v446')
    s = s.replace('v443 ещё не существует', 'v447 ещё не существует')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed += 1
print('[3] базовый бамп: изменено файлов %d (guard v443→v447, ассерты v442→v446)' % changed)

# --- 4. Перезапись адаптируемых + новых тестов из kip8test ---
def adapt(s):
    # порядок важен: от старших к младшим, точные полные токены
    s = s.replace('kipia-test-v599', 'kipia-v447')   # guard «двойного бампа нет»
    s = s.replace('kipia-test-v598', 'kipia-v446')   # текущая (после 369)
    s = s.replace('kipia-test-v596', 'kipia-v445')   # 368 «стала»
    s = s.replace('kipia-test-v595', 'kipia-v444')   # 367 «стала»
    s = s.replace('kipia-test-v594', 'kipia-v442')   # 366 «старая до»
    s = s.replace('kipia-test-v593', 'kipia-v441')   # 365 «старая до»
    s = s.replace('v599 ещё не существует', 'v447 ещё не существует')
    return s

HISTORICAL = ('v534', 'v537', 'v585', 'v586')
for name in ADAPT + NEW:
    src = io.open(os.path.join(SRC, name), encoding='utf-8').read()
    out = adapt(src)
    rest = [w for w in out.split() if w.startswith('kipia-test-v') and
            not any(x in w for x in HISTORICAL)]
    if rest:
        print('ОСТАЛИСЬ тест-версии в %s: %s' % (name, sorted(set(rest))))
        sys.exit(1)
    io.open(os.path.join(DST, name), 'w', encoding='utf-8').write(out)
    kind = 'адаптирован' if name in ADAPT else 'перенесён'
    print('    %s: %s' % (name, kind))
print('[4] тесты: %d адаптировано + %d перенесено' % (len(ADAPT), len(NEW)))

# --- 5. run-all.js: +4 require после test-task365.js ---
ra = 'tests/run-all.js'
s = open(ra, encoding='utf-8').read()
anchor = "require('./test-task365.js');"
ins = anchor + """
// Task 366 — расходомеры: баннер недоставленных показаний (далее в 367
// заменён цветом значений карточек) + server_busy — повторяемая ошибка
require('./test-task366.js');
// Task 367 — баннер убран ВООБЩЕ: жёлто-оранжевые значения карточек с
// недоставленными показаниями (приоритет над красным), зелёный после
// доставки; недельные/месячные — красный по календарной неделе/месяцу
require('./test-task367.js');
// Task 368 — показания №3/№11/№9 за ПЕРИОД двух дат (дефолт — прошедшая
// календарная неделя / прошлый месяц); красный по ЗАКРЫТЫМ неделям/месяцам
require('./test-task368.js');
// Task 369 — КИП ИОС: свайп кнопки «Проекты» открывает «Проекты по
// статусу» — группы по столбцу «Статус проекта»
require('./test-task369.js');"""
assert anchor in s and "require('./test-task366.js');" not in s
s = s.replace(anchor, ins)
open(ra, 'w', encoding='utf-8').write(s)
print('[5] run-all.js: +4 require (366–369)')

# --- Контроль ---
sw2 = open(sw_path, encoding='utf-8').read()
assert sw2.count("CACHE_VERSION = 'kipia-v446'") == 1
leftover = []
for f in glob.glob('tests/*.js'):
    s = open(f, encoding='utf-8').read()
    for tok in ('kipia-test-v598', 'kipia-test-v599', 'kipia-test-v594',
                'kipia-test-v595', 'kipia-test-v596'):
        if tok in s:
            leftover.append('%s: %s' % (f, tok))
    if 'kipia-v442' in s and f not in ('tests/test-task366.js',):
        # v442 остаётся только как «старая до 366» в тесте 366
        for i, line in enumerate(s.splitlines(), 1):
            if 'kipia-v442' in line:
                leftover.append('%s:%d v442' % (f, i))
if leftover:
    print('ПРЕДУПРЕЖДЕНИЕ leftovers:')
    for l in leftover[:20]:
        print('   ', l)
else:
    print('[контроль] leftovers нет')
print('OK — порт пакета Tasks 366–369 применён к kip8')
