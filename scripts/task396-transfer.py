#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 396: ПЕРЕНОС из kip8test в боевой kip8 (локальная часть —
# без push: PAT утрачен с откатом песочницы, push выполнит
# следующий цикл после переотправки PAT).
#   1) копия tests/test-task396.js с маппингом SW-версий
#      (kipia-test-v623→kipia-v471, kipia-test-v624→kipia-v472,
#       kipia-test-v625→kipia-v473) — файл в ПОСТ-БАМП форме
#      (assert kipia-v472 + guard kipia-v473);
#   2) регистрация в tests/run-all.js (после test-task395.js);
#   3) копия браузерной проверки: порт 9007, localStorage БЕЗ
#      префикса kip8test:, тег t396k8, пруфы task396k8-*.
# Патч index.html — scripts/task396-patch.py (копия kip8test,
# применена отдельно: 19/19 якорей), адаптация тестов —
# scripts/task396-adapt-tests.py (копия, 4+1 ассертов).
import io
import re

# --- 1) копия теста с маппингом версий ---
src = io.open('../kip8test/tests/test-task396.js', encoding='utf-8').read()
for old, new in [('kipia-test-v623', 'kipia-v471'),
                 ('kipia-test-v624', 'kipia-v472'),
                 ('kipia-test-v625', 'kipia-v473')]:
    n = src.count(old)
    assert n > 0, 'в test-task396.js не найдено %s' % old
    src = src.replace(old, new)
    print('  маппинг %s -> %s (%d)' % (old, new, n))
io.open('tests/test-task396.js', 'w', encoding='utf-8').write(src)
print('tests/test-task396.js скопирован (пост-бамп форма v472/v473)')

# --- 2) регистрация в run-all.js ---
ra = io.open('tests/run-all.js', encoding='utf-8').read()
if "require('./test-task396.js');" not in ra:
    anchor = "require('./test-task395.js');"
    assert ra.count(anchor) == 1, 'якорь run-all.js не найден'
    ra = ra.replace(anchor, anchor +
        "\n// Task 396 — перенос из kip8test: зебра строк блоков,"
        " компактные кнопки в шапках, оглавления ярче (SW kipia-v472)"
        "\nrequire('./test-task396.js');")
    io.open('tests/run-all.js', 'w', encoding='utf-8').write(ra)
    print('tests/run-all.js: require test-task396 добавлен')
else:
    print('tests/run-all.js: уже зарегистрирован (пропуск)')

# --- 3) копия браузерной проверки (порт 9007, без префикса) ---
bs = io.open('../kip8test/scripts/task396-browser-check.py', encoding='utf-8').read()
bs = bs.replace('PORT = 9006', 'PORT = 9007')
bs = bs.replace("'bc-t396-%s'", "'bc-t396k8-%s'")
# localStorage: БЕЗ префикса kip8test: (боевой сайт не изолирует
# хранилище). Замены — НА УРОВНЕ ИСХОДНИКА скрипта (литералы с
# кавычками/конкатенацией), НЕ склеенного значения!
bs = bs.replace("localStorage.setItem('kip8test:kip8_session_token',",
                "localStorage.setItem('kip8_session_token',")
bs = bs.replace("localStorage.setItem('kip8test:app-theme',",
                "localStorage.setItem('app-theme',")
assert "PORT = 9007" in bs and "'bc-t396k8-%s'" in bs
# контроль: в блоке attach ОСТАЛСЯ только БЕЗПРЕФИКСНЫЙ setItem
attach_src = bs.split('def attach')[1].split('EDIT_PERMS')[0]
assert "localStorage.setItem('kip8_session_token'," in attach_src
assert "localStorage.setItem('kip8test:kip8_session_token'," not in attach_src
assert "localStorage.setItem('app-theme'," in attach_src
assert "localStorage.setItem('kip8test:app-theme'," not in attach_src
# пруфы — отдельные имена kip8
bs = re.sub(r"task396-proof-", "task396k8-proof-", bs)
# комментарий шапки — kip8-специфика
bs = bs.replace('# Порт 9006 (запуск: python3 -m http.server 9006 &).',
                '# Порт 9007 (запуск: python3 -m http.server 9007 &).')
io.open('scripts/task396-browser-check.py', 'w', encoding='utf-8').write(bs)
print('scripts/task396-browser-check.py скопирован (порт 9007, без префикса, пруфы task396k8-*)')
print('task396-transfer: ГОТОВО (локальная часть)')
