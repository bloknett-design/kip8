#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 395 — ПЕРЕНОС тестовой части из kip8test в БОЕВОЙ kip8:
#   1) копия tests/test-task395.js из ../kip8test с контентной
#      адаптацией SW-версий: kipia-test-v623 → kipia-v470 (ассерты),
#      kipia-test-v624 → kipia-v471 (guards) — состояние «до бампа»
#      kip8 (текущая v470); имя SW-теста — «SW поднят до kipia-v470»
#      (бамп подхватит строку целиком);
#   2) регистрация теста в tests/run-all.js;
#   3) копия scripts/task395-browser-check.py с адаптацией под kip8:
#      порт 9007, тег t395k8, localStorage БЕЗ префикса kip8test:
#      (боевой репо), пруфы task395k8-proof-*.png.
# (Правки index.html и адаптация тестов 311/385/394 — scripts/
#  task395-patch.py и task395-adapt-tests.py, применены ранее.)
import io
import sys

def patch(path, repl):
    s = io.open(path, encoding='utf-8').read()
    ok = True
    for old, new, cnt in repl:
        n = s.count(old)
        if n != cnt:
            print('  !! %s: якорь x%d (ожидалось x%d): %r' % (path, n, cnt, old[:70]))
            ok = False
            continue
        s = s.replace(old, new)
    if not ok:
        sys.exit(1)
    io.open(path, 'w', encoding='utf-8').write(s)
    print('  ok %s (%d правок)' % (path, len(repl)))

print('Task 395 — перенос тестовой части в kip8:')

# --- 1) копия test-task395.js с адаптацией SW-версий ---
src = io.open('../kip8test/tests/test-task395.js', encoding='utf-8').read()
assert src.count("kipia-test-v623") == 2, 'ассерт v623 + текст (2 вхождения)'
assert src.count('kipia-test-v624') == 1, 'guard v624'
src = src.replace('kipia-test-v623', 'kipia-v470')
src = src.replace('kipia-test-v624', 'kipia-v471')
src = src.replace('SW поднят до v623', 'SW поднят до kipia-v470')
assert 'kipia-test' not in src, 'хвосты kipia-test в тесте'
io.open('tests/test-task395.js', 'w', encoding='utf-8').write(src)
print('  ok tests/test-task395.js (SW-версии: ассерт kipia-v470, guard kipia-v471)')

# --- 2) регистрация в run-all.js ---
patch('tests/run-all.js', [
    ("""require('./test-task394.js');
require('./test-deploy-url.js');""",
     """require('./test-task394.js');
// Task 395: кнопка «Работники» скрыта для null/min по матрице
// доступа (edit/view — видна, у view карточки read-only); фон
// блоков карточек НЕ сливается с фоном окна + рамки толще/ярче
// («выступающий бордюрчик»); десктоп — колонки: отпуска под
// профилем, мероприятия под отпусками, СИЗ в верхней правой части
require('./test-task395.js');
require('./test-deploy-url.js');""", 1),
])

# --- 3) копия браузерной проверки с адаптацией под kip8 ---
br = io.open('../kip8test/scripts/task395-browser-check.py', encoding='utf-8').read()
assert br.count('PORT = 9006') == 1
br = br.replace('PORT = 9006', 'PORT = 9007')
br = br.replace('t395-', 't395k8-')
br = br.replace("'bc-t395k8-%s'", "'bc-t395k8-%s'")  # no-op guard
br = br.replace(
    "localStorage.setItem('kip8test:kip8_session_token','bc-t395k8-%s');",
    "localStorage.setItem('kip8_session_token','bc-t395k8-%s');")
br = br.replace(
    "localStorage.setItem('kip8test:app-theme','%s');",
    "localStorage.setItem('app-theme','%s');")
br = br.replace('task395-proof-', 'task395k8-proof-')
# заголовок-комментарий: порт/репо
br = br.replace('# Порт 9006 (запуск: python3 -m http.server 9006 &).',
                '# Порт 9007 (запуск: python3 -m http.server 9007 &);\n'
                '# localStorage БЕЗ префикса kip8test: (боевой репо).')
assert '9006' not in br, 'хвосты порта 9006'
assert "kip8test:kip8_session_token" not in br, 'хвосты префикса kip8test:'
io.open('scripts/task395-browser-check.py', 'w', encoding='utf-8').write(br)
print('  ok scripts/task395-browser-check.py (порт 9007, без префикса, пруфы task395k8-*)')

print('Перенос тестовой части завершён. Дальше: task395-bump-sw.py (v470→v471).')
