#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 344: восстановление ПРОД index.html в kip8 после инцидента
# «общий вход kip8 ↔ kip8test».
#
# ИНЦИДЕНТ: при переносе Task 341 (коммит e50d394, «печать графика
# работ») в kip8 был скопирован тестовый index.html ЦЕЛИКОМ — вместе
# с обёрткой isolateLocalStorage() (префикс 'kip8test:' ко ВСЕМ
# ключам localStorage) и тест-ключами kip8test_*. Оба PWA живут на
# одном origin (bloknett-design.github.io), localStorage у них общий,
# поэтому kip8 стал писать токен в 'kip8test:kip8_session_token' —
# ровно тот ключ, который читает kip8test: вход в kip8 автоматически
# логинил kip8test (заявка пользователя 2026-09-08).
#
# Скрипт — обратная изоляция по образцу scripts/prepare-kip8-transfer.py
# из kip8test + восстановление прод-формулировок комментариев (из
# эталонного расхождения kip8@5f435e1 ↔ kip8test@2c40a87, 82 строки):
#   1. Удаляет блок isolateLocalStorage() (комментарий + IIFE)
#   2. 'kip8test_devices_cache'      -> 'kip8_devices_cache'
#   3. "'kip8test:' + DEV_CACHE_KEY" -> "DEV_CACHE_KEY" (3 места)
#   4. 'kip8test_phonebook_favorites' -> 'kip8_phonebook_favorites'
#   5. 'kip8test_phonebook_notes'     -> 'kip8_phonebook_notes'
#   6. 'kip8test_phonebook_cache'     -> 'kip8_phonebook_cache' (2 места)
#   7. '/kip8test/#exam-tickets'      -> '/kip8/#exam-tickets' (комментарий)
#   8. Комментарии прод-формулировок: Task 243/244 (sidebar/overlay),
#      «Сапёр» (ключи без префикса), URL Apps Script (Task 245),
#      Task 242 (SW-обновление)
#
# Запуск из корня репо kip8. Все замены — с контролем ТОЧНОГО числа
# вхождений (любое отклонение = ошибка, файл остаётся неизменным).
import re
import sys

PATH = 'index.html'
with open(PATH, encoding='utf-8') as f:
    html = f.read()

# --- Санити-проверки ДО (работаем только с «тестовым» файлом) ---
if html.count('isolateLocalStorage') != 2:
    print('ОШИБКА: ожидалось 2 упоминания isolateLocalStorage '
          '(комментарий «Сапёра» + IIFE), найдено %d'
          % html.count('isolateLocalStorage'))
    sys.exit(1)
if '(function isolateLocalStorage() {' not in html:
    print('ОШИБКА: IIFE обёртки не найден — файл уже восстановлен?')
    sys.exit(1)


def sub1(old, new, expected=1, what=''):
    global html
    cnt = html.count(old)
    if cnt != expected:
        print('ОШИБКА: [%s] найдено %d раз (ожидалось %d)' %
              (what or old[:60].replace('\n', '\\n'), cnt, expected))
        sys.exit(1)
    html = html.replace(old, new)
    print('[ok] %s -> %s (%d зам.)' %
          (old[:56].replace('\n', '\\n'), new[:56].replace('\n', '\\n'), cnt))


# --- 1. Удаление блока isolateLocalStorage (комментарий + IIFE) ---
pattern = re.compile(
    r'\n    // ===== ТЕСТОВЫЙ РЕПОЗИТОРИЙ kip8test: изоляция localStorage =====\n'
    r'    // localStorage общий для всего origin \(bloknett-design\.github\.io\)\.\n'
    r'    // Чтобы настройки \(тема, метод калибровки буя\) из тестового репозитория\n'
    r'    // не влияли на основной репозиторий kip8, добавляем префикс ко всем ключам\.\n'
    r'    // В основном репозитории kip8 этот блок ОТСУТСТВУЕТ — там ключи без префикса\.\n'
    r'    \(function isolateLocalStorage\(\) \{\n'
    r'        const PREFIX = \'kip8test:\';\n'
    r'        const origGetItem = localStorage\.getItem\.bind\(localStorage\);\n'
    r'        const origSetItem = localStorage\.setItem\.bind\(localStorage\);\n'
    r'        const origRemoveItem = localStorage\.removeItem\.bind\(localStorage\);\n'
    r'        localStorage\.getItem = function\(key\) \{ return origGetItem\(PREFIX \+ key\); \};\n'
    r'        localStorage\.setItem = function\(key, value\) \{ return origSetItem\(PREFIX \+ key, value\); \};\n'
    r'        localStorage\.removeItem = function\(key\) \{ return origRemoveItem\(PREFIX \+ key\); \};\n'
    r'    \}\)\(\);\n'
)
html, n_block = pattern.subn('\n', html)
print('[1] isolateLocalStorage блок удалён: %d (ожидается 1)' % n_block)
if n_block != 1:
    sys.exit(1)

# --- 2-7. Функциональные замены (ключи/URL) ---
sub1("'kip8test_devices_cache'", "'kip8_devices_cache'", 1, 'ключ кэша приборов')
sub1("'kip8test:' + DEV_CACHE_KEY", 'DEV_CACHE_KEY', 3, 'префикс DEV_CACHE_KEY')
sub1("'kip8test_phonebook_favorites'", "'kip8_phonebook_favorites'", 1, 'PB_FAV_KEY')
sub1("'kip8test_phonebook_notes'", "'kip8_phonebook_notes'", 1, 'PB_NOTES_KEY')
sub1("'kip8test_phonebook_cache'", "'kip8_phonebook_cache'", 2, 'кэш справочника')
sub1('/kip8test/#exam-tickets', '/kip8/#exam-tickets', 1, 'комментарий hash-навигации')

# --- 8. Комментарии: прод-формулировки (эталон kip8@5f435e1) ---
sub1(
    '/* Task 243 (бекпорт из kip8): !important бьёт десктопное правило '
    '#sidebar{transform:translateX(-100%)!important} '
    '(specificity #sidebar.active (1,1,0) > #sidebar (1,0,0)). '
    'В kip8test wsTrSheet уже правильно закрыт, но !important оставлен '
    'для надёжности и паритета с kip8 — чтобы при следующем переносе '
    'kip8test → kip8 не потерять фикс. */',
    '/* Task 243: !important бьёт десктопное правило '
    '#sidebar{transform:translateX(-100%)!important} '
    '(specificity #sidebar.active (1,1,0) > #sidebar (1,0,0)) — '
    'фикс бага «hamburger не открывает sidebar на 377px viewport». '
    'Task 244: корневая причина — wsTrSheet не был закрыт, sidebar '
    'оказывался вложенным в него (position:fixed относительно wsTrSheet, '
    'имевшего transform). В kip8test wsTrSheet уже правильно закрыт, '
    'но !important оставлен для надёжности. */',
    1, 'комментарий Task 243/244 (sidebar)')

sub1('/* Task 243 (бекпорт): то же самое для overlay */',
     '/* Task 243: то же самое для overlay */',
     1, 'комментарий Task 243 (overlay)')

sub1(
    '// (в тестовом репо ключ автоматически получает префикс kip8test:\n'
    '    // через isolateLocalStorage). При первом запуске победы из старого',
    '// (kip8 — основной репозиторий, ключи без префикса). При первом\n'
    '    // запуске победы из старого',
    1, 'комментарий «Сапёра» (ключи без префикса)')

sub1(
    '// URL Apps Script Web App.\n'
    '        // Task 284: URL развёртывания пользователя (AKfycbyt…) — пробы\n'
    '        // 2026-09-01 подтвердили: проект полный (Auth/Sessions/Admin/\n'
    '        // CableJournal/Flowmeter/ValidationRules/WorkSchedule) и код\n'
    '        // свежий (роутинг отпусков есть). Прежний URL (AKfycbzg…,\n'
    '        // Task 202) остался на старом снимке кода — до Task 274.',
    '// URL Apps Script Web App (развёртывание AKfycbyt…, в kip8 с\n'
    '        // Task 245). Пробы 2026-09-01 (Task 284 в kip8test) подтвердили:\n'
    '        // проект полный (Auth/Sessions/Admin/CableJournal/Flowmeter/\n'
    '        // ValidationRules/WorkSchedule) и код свежий — роутинг отпусков\n'
    '        // (Task 274+) есть. kip8test синхронизирован с этим же URL.',
    1, 'комментарий URL Apps Script')

sub1(
    '// Task 242 (бекпорт из kip8): усиление обновления SW — вместе с\n'
    '        // skipWaiting() в sw.js и reg.update() сразу при загрузке.',
    '// Task 242: усиление обновления SW — вместе с skipWaiting() в sw.js\n'
    '        // и reg.update() сразу при загрузке.',
    1, 'комментарий Task 242 (SW-обновление)')

# --- Контроль ПОСЛЕ ---
n_iso = html.count('isolateLocalStorage')
if n_iso != 0:
    print('ОШИБКА: isolateLocalStorage остался (%d)' % n_iso)
    sys.exit(1)
for bad in ("'kip8test:'", "'kip8test_'", '/kip8test/#', '(function isolateLocalStorage'):
    if bad in html:
        print('ОШИБКА: осталось %r' % bad)
        sys.exit(1)
# Прод-ключи на месте:
for good in ("'kip8_devices_cache'", "'kip8_phonebook_favorites'",
             "'kip8_phonebook_notes'", "'kip8_phonebook_cache'",
             "'kip8_session_token'"):
    if good not in html:
        print('ОШИБКА: прод-ключ %s не найден' % good)
        sys.exit(1)

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(html)

n_lines = html.count('\n') + 1
print('OK: index.html восстановлен (%d строк, %d байт)' % (n_lines, len(html.encode('utf-8'))))
print('Осталось легитимных упоминаний kip8test (комментарии): %d'
      % html.count('kip8test'))
