#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 531 — перенос из kip8test в kip8 (по образцу
task530-transfer-tests.py; УРОК 527: SW-секция вырезается по
ПОСЛЕДНЕМУ разделителю перед маркером SW — rindex):
  1) index.html — /tmp/kip8_index_transfer.html (prepare-kip8-transfer.py
     уже выполнен в kip8test; дифф 582 строки = контент Task 531:
     CSS утопленник + панель настроек + z-фикс шторок + JS WsLcdClock);
     серверная часть НЕ менялась (Только клиент);
  2) test-task531.js (НОВЫЙ) + test-task530.js + test-task529.js —
     копии kip8test с SW-секциями kip8 в ПОСТ-БАМП состоянии
     (assert kipia-v541, гварда «старой версии нет» → v540);
  3) бамп SW kip8 v540 → v541: ГВАРДЫ v541 → v542 первыми (во всех,
     КРОМЕ перенесённых файлов — они уже пост-бамп), АССЕРТЫ v540 →
     v541, sw.js CACHE_VERSION, регистрация test-task531.js;
  4) DEPLOY-Task531 — копия (в kip8 клиентская, для протокола).
"""
import io
import os
import sys

T = '/home/z/my-project/kip8test'
K = '/home/z/my-project/kip8'


def read(p):
    return io.open(p, encoding='utf-8').read()


def write(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


def swap_sw(src, new_sw):
    """Заменяет хвост файла начиная с разделителя ПЕРЕД SW-секцией
    (rindex — УРОК Task 527; маркеры: «// 5. SW» (529), «// E. SW»
    (530), «// D. SW» (531))."""
    for marker in ('// 5. SW', '// E. SW', '// D. SW'):
        if marker in src:
            sw_start = src.rindex('// ===========', 0, src.index(marker))
            return src[:sw_start] + new_sw
    raise ValueError('SW-секция не найдена')


def sw_section(title, task_note):
    return """// ============================================================
// SW — версия кэша (зеркало kip8test, Task 531)
// ============================================================
describe('""" + title + """', () => {

    test('sw.js: CACHE_VERSION = kipia-v541', () => {
        const m = SW_SRC.match(/const CACHE_VERSION = '(kipia-v\\d+)'/);
        assertTrue(m !== null, 'CACHE_VERSION найден');
        assertEqual(m[1], 'kipia-v541', 'SW поднят до v541 (""" + task_note + """)');
        assertTrue(m[1] !== 'kipia-v540', 'старая версия v540 не осталась');
    });

});
"""

# ---------- 1. index.html ----------
html = read('/tmp/kip8_index_transfer.html')
write(K + '/index.html', html)
print('[1] kip8/index.html — перенесён (дифф 582 строк = Task 531, '
      'только клиент)')

# ---------- 2. тесты: SW-секции kip8 в пост-бамп состоянии ----------
SPECS = [
    ('test-task531.js', 'Task 531 — SW: версия кэша', 'Task 531',
     '//   D. SW — kipia-test-v744.',
     '//   D. SW — kipia-v541.'),
    ('test-task530.js', 'Task 530 — SW: версия кэша', 'Task 531',
     '//   E. SW — kipia-test-v744 (Task 531).',
     '//   E. SW — kipia-v541 (Task 531).'),
    ('test-task529.js', 'Task 529 → 530 — SW: версия кэша', 'Task 530',
     '//   Слой 5 — SW: kipia-test-v744.',
     '//   Слой 5 — SW: kipia-v541.'),
]
for name, title, note, hdr_old, hdr_new in SPECS:
    src = read(T + '/tests/' + name)
    assert 'kipia-test-v744' in src, name + ': SW-блок kip8test не найден'
    src = swap_sw(src, sw_section(title, note))
    assert hdr_old in src, name + ': строка заголовка SW не найдена'
    src = src.replace(hdr_old, hdr_new)
    assert 'kipia-test-v' not in src, name + ': остатки kipia-test-v!'
    write(K + '/tests/' + name, src)
    print('[2] kip8/tests/%s — SW-секция kip8: v541' % name)

# ---------- 3. бамп SW kip8 v540 → v541 ----------
OWN = ['test-task531.js', 'test-task530.js', 'test-task529.js']
changed = {}


def bump(path, old, new):
    s = read(path)
    n = s.count(old)
    if n == 0:
        return
    write(path, s.replace(old, new))
    changed[os.path.basename(path)] = changed.get(
        os.path.basename(path), 0) + n


tests_dir = os.path.join(K, 'tests')
files = sorted(f for f in os.listdir(tests_dir) if f.endswith('.js'))

print('Шаг 3а — ГВАРДЫ v541 → v542 (кроме перенесённых):')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v541', 'kipia-v542')

print('Шаг 3б — АССЕРТЫ v540 → v541:')
for f in files:
    if f in OWN:
        continue
    bump(os.path.join(tests_dir, f), 'kipia-v540', 'kipia-v541')

print('Шаг 3в — sw.js CACHE_VERSION v540 → v541:')
sw_path = os.path.join(K, 'sw.js')
sw = read(sw_path)
if sw.count("const CACHE_VERSION = 'kipia-v540'") != 1:
    print('ОШИБКА: CACHE_VERSION v540 не найден')
    sys.exit(1)
write(sw_path, sw.replace("const CACHE_VERSION = 'kipia-v540'",
                          "const CACHE_VERSION = 'kipia-v541'"))
print('  sw.js: CACHE_VERSION v541')

print('Шаг 3г — регистрация test-task531.js в run-all.js:')
ra_path = os.path.join(tests_dir, 'run-all.js')
ra = read(ra_path)
if "require('./test-task531.js')" in ra:
    print('  уже зарегистрирован')
else:
    anchor = "require('./test-task530.js');"
    if ra.count(anchor) < 1:
        print('ОШИБКА: якорь run-all (530) не найден')
        sys.exit(1)
    ra = ra.replace(anchor, anchor +
                    "\n// Task 531 (зеркало kip8test): LCD-информер — экран-утопленник,\n"
                    "// общая нижняя линия, настройки информера, багфиксы\n"
                    "// календаря и z-полосы шторок. SW v541.\n"
                    "require('./test-task531.js');", 1)
    write(ra_path, ra)
    print('  зарегистрирован после test-task530.js')

# ---------- 4. DEPLOY-документ ----------
dep = read(T + '/DEPLOY-Task531-lcd-informer-settings.md')
write(K + '/DEPLOY-Task531-lcd-informer-settings.md', dep)
print('[4] DEPLOY-Task531 — скопирован')

print('Итог:', changed)
