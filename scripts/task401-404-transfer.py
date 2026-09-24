#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 401-404-transfer: перенос изменений из kip8test в kip8
# (боевой сайт). Задачи 401 (годовая шторка итогов на всю ширину +
# подстрока «дней/часов» + итоговые столбцы), 402 (тип работника
# третьей строкой ячейки + столбец «группа_допуска»), 403 («разряд»
# → «р.» и без группы в столбце ФИО; попап без СИЗ; GAS-фикс бага
# комментария; ярлыки по тексту; мероприятия над СИЗ), 404 (три
# колонки карточки; кнопки ✎/✕ рядом; окно мероприятий без
# отпусков).
# ШАГИ (запуск из /home/z/my-project/kip8):
#   1) применить task401/402/403/404-patch.py к index.html и
#      scripts/WorkSchedule.gs (базы идентичны: diff только
#      localStorage-ключи/комментарии — вне зон патчей; GS совпал
#      побайтово);
#   2) скопировать 16 контентно-изменённых тестов из kip8test
#      (HEAD a038911) с маппингом версий SW: kipia-test-v631 →
#      kipia-v475 (актуальные ассерты), kipia-test-v632 → kipia-v476
#      (guards); исторические kipia-test-v5XX — ОБЩИЕ guards обоих
#      репо, не трогаются;
#   3) run-all.js kip8 — точечно вписать 4 require (401-404) после
#      test-task399.js (run-all репо различаются: в kip8 есть
#      kip8-специфичный test-task344.js — файл НЕ копируется);
#      новые тест-файлы 401-404 — тоже копируются (шаг 2).
# Затем отдельным скриптом — SW-бамп kipia-v475 → v476
# (двухшаговый, канонизирует перенесённые ассерты v475 → v476,
# guards v476 → v477).
import io
import os
import subprocess
import sys

K8TEST = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                      '..', 'kip8test'))
assert os.path.isdir(K8TEST), 'репо kip8test не найдено: %s' % K8TEST

TESTS = [
    'test-task321.js', 'test-task323.js', 'test-task333.js',
    'test-work-schedule.js', 'test-task384.js', 'test-task388.js',
    'test-task392.js', 'test-task393.js', 'test-task394.js',
    'test-task395.js', 'test-task396.js', 'test-task399.js',
    'test-task401.js', 'test-task402.js', 'test-task403.js',
    'test-task404.js',
]

# ============================================================
# 1. Патчи кода (порядок обязателен: 401 → 402 → 403 → 404)
# ============================================================
for n in ('401', '402', '403', '404'):
    script = os.path.join(K8TEST, 'scripts', 'task%s-patch.py' % n)
    print('--- patch %s ---' % n)
    r = subprocess.run([sys.executable, script], cwd=os.getcwd())
    assert r.returncode == 0, 'task%s-patch.py упал' % n

# ============================================================
# 2. Тесты: копия с маппингом версий
# ============================================================
print('--- тесты (16 файлов + маппинг версий) ---')
for name in TESTS:
    src = io.open(os.path.join(K8TEST, 'tests', name), encoding='utf-8').read()
    n_a = src.count('kipia-test-v631')
    src = src.replace('kipia-test-v631', 'kipia-v475')
    n_g = src.count('kipia-test-v632')
    src = src.replace('kipia-test-v632', 'kipia-v476')
    io.open(os.path.join('tests', name), 'w', encoding='utf-8').write(src)
    print('  %s (ассерты v631→v475: %d, guards v632→v476: %d)'
          % (name, n_a, n_g))

# ============================================================
# 3. run-all.js: регистрация 401-404 (после 399, перед deploy-url)
# ============================================================
P2 = 'tests/run-all.js'
r = io.open(P2, encoding='utf-8').read()
old = """require('./test-task399.js');
require('./test-deploy-url.js');"""
new = """require('./test-task399.js');
// Task 401 — окно итогов «Год»: полная ширина правее колонки ФИО,
// подстрока «дней/часов», итоговые столбцы (фон/разделитель)
require('./test-task401.js');
// Task 402 — тип работника третьей строкой ячейки; «группа_допуска»
// (ячейка/карточка/сводная/шторка правки; GAS — столбец по заголовку)
require('./test-task402.js');
// Task 403 — «разряд» → «р.» и БЕЗ группы допуска в столбце ФИО; попап
// без СИЗ; GAS-фикс бага комментария (столбцы по заголовкам); ярлыки
// «Работников» по самому длинному тексту
require('./test-task403.js');
// Task 404 — карточка: ТРИ колонки (профиль+отпуска | СИЗ | мероприятия),
// кнопки ✎/✕ рядом (контент строк растянут); окно мероприятий без отпусков
require('./test-task404.js');
require('./test-deploy-url.js');"""
assert r.count(old) == 1, 'run-all.js: якорь регистрации не найден'
io.open(P2, 'w', encoding='utf-8').write(r.replace(old, new))
print('run-all.js: test-task401/402/403/404.js подключены')

print('OK: перенос 401-404 завершён (SW-бамп — отдельным шагом)')
