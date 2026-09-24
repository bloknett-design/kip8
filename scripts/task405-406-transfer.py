#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Task 405-406-transfer: перенос изменений из kip8test в kip8
# (боевой сайт). Задачи:
#   405 — разделение таблицы инструктажей (лист «Мероприятия»,
#         объединённый listTrainings, маршрутизация addTraining,
#         сквозные id, trainingsSplitInit; блок «Повторные
#         инструктажи и периодическая проверка знаний»);
#   406  — карточка: мероприятия ПОД отпусками (1-я колонка), блоки
#          СИЗ и инструктажей поменяны местами.
# ШАГИ (запуск из /home/z/my-project/kip8):
#   1) task405-patch.py — ОТНОСИТЕЛЬНЫЕ пути: запускается с cwd=kip8,
#      правит kip8/scripts/WorkSchedule.gs + kip8/index.html;
#   2) правки Task 406 — INLINE (task406-patch.py в kip8test с
#      абсолютным путём — здесь те же 5 правок с относительным);
#   3) копия 14 контентно-изменённых тестов из kip8test (HEAD 0ef0fcd)
#      с маппингом версий SW: kipia-test-v633 → kipia-v476 (ассерты),
#      kipia-test-v634 → kipia-v477 (guards); исторические строки
#      (kipia-test-v623) — ОБЩИЕ guards обоих репо, не трогаются;
#      kip8-специфичные файлы (test-task344.js, test-task340.js и
#      пр.) — НЕ копируются, их версии поднимет SW-бамп;
#   4) run-all.js kip8 — вписать require 405/406 после 404 (run-all
#      репо различаются: в kip8 есть kip8-специфичный test-task344).
# Затем отдельным скриптом — SW-бамп kipia-v476 → v477
# (двухшаговый: guards v477→v478, ассерты v476→v477).
import io
import os
import subprocess
import sys

K8TEST = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                      '..', 'kip8test'))
assert os.path.isdir(K8TEST), 'репо kip8test не найдено: %s' % K8TEST

TESTS = [
    'test-tab-numbers.js', 'test-task306.js', 'test-task384.js',
    'test-task385.js', 'test-task388.js', 'test-task393.js',
    'test-task394.js', 'test-task395.js', 'test-task396.js',
    'test-task403.js', 'test-task404.js', 'test-task405.js',
    'test-task406.js', 'test-work-events.js',
]

# ============================================================
# 1. Патч Task 405 (относительные пути — cwd=kip8)
# ============================================================
script = os.path.join(K8TEST, 'scripts', 'task405-patch.py')
print('--- patch 405 ---')
r = subprocess.run([sys.executable, script], cwd=os.getcwd())
assert r.returncode == 0, 'task405-patch.py упал'

# ============================================================
# 2. Правки Task 406 (inline, относительный путь)
# ============================================================
print('--- правки 406 (inline) ---')
PATH = 'index.html'
src = io.open(PATH, encoding='utf-8').read()
orig = src

REPL = []


def rep(old, new, tag):
    REPL.append((old, new, tag))


rep("""        // Task 395 \u2192 403 \u2192 404 (заявка): ТРИ колонки-обёртки .ws-wcol
        // (раскладка — CSS @media ≥1024px). Task 404 (заявка: «блок
        // СИЗ размести слева от блока мероприятия; в верхней части —
        // три блока слева направо: профиль (под ним отпуска), СИЗ,
        // мероприятия»): колонка 1 — ПРОФИЛЬ + ОТПУСКА (вертикальный
        // стек), колонка 2 (.ws-wcol-ppe) — СИЗ, колонка 3
        // (.ws-wcol-tr) — МЕРОПРИЯТИЯ, под ним (Task 405) — блок
        // «Повторные инструктажи и периодическая проверка знаний»:
        // три верхних блока в ОДНУ ЛИНИЮ. Мобайл ≤1023px —
        // вертикальный СТЕК колонок (профиль → отпуска → СИЗ →
        // мероприятия → инструктажи); зазоры — margin-bottom панелей
        // (Task 393) + межколоночный (CSS)
        _renderWorkerCardPanels: function(tabNo, withEdit) {
            var blocks = this._renderWorkerCard(tabNo, withEdit, true);
            var colMain = '', colPpe = '', colTr = '';
            for (var bi = 0; bi < blocks.length; bi++) {
                var panel = '<div class="ws-wcard">' + blocks[bi] + '</div>';
                if (bi < 2) colMain += panel;
                else if (bi === 3) colPpe += panel;
                else colTr += panel;
            }
            return '<div class="ws-wcol">' + colMain + '</div>' +
                   '<div class="ws-wcol ws-wcol-ppe">' + colPpe + '</div>' +
                   '<div class="ws-wcol ws-wcol-tr">' + colTr + '</div>';
        },""",
    """        // Task 395 → 403 → 404 → 406 (заявки): ТРИ колонки-обёртки
        // .ws-wcol (раскладка — CSS @media ≥1024px). Task 406
        // (заявка: «блок мероприятия перемести под блок отпуска,
        // блоки СИЗ и инструктажей поменяй местами»): колонка 1 —
        // ПРОФИЛЬ + ОТПУСКА + МЕРОПРИЯТИЯ (вертикальный стек),
        // колонка 2 (.ws-wcol-instr) — «Повторные инструктажи и
        // периодическая проверка знаний», колонка 3 (.ws-wcol-ppe)
        // — СИЗ. Мобайл ≤1023px — вертикальный СТЕК колонок
        // (профиль → отпуска → мероприятия → инструктажи → СИЗ);
        // зазоры — margin-bottom панелей (Task 393) +
        // межколоночный (CSS)
        _renderWorkerCardPanels: function(tabNo, withEdit) {
            var blocks = this._renderWorkerCard(tabNo, withEdit, true);
            var colMain = '', colInstr = '', colPpe = '';
            for (var bi = 0; bi < blocks.length; bi++) {
                var panel = '<div class="ws-wcard">' + blocks[bi] + '</div>';
                if (bi < 3) colMain += panel;
                else if (bi === 4) colInstr += panel;
                else colPpe += panel;
            }
            return '<div class="ws-wcol">' + colMain + '</div>' +
                   '<div class="ws-wcol ws-wcol-instr">' + colInstr + '</div>' +
                   '<div class="ws-wcol ws-wcol-ppe">' + colPpe + '</div>';
        },""", 'renderWorkerCardPanels')

rep("""                // Task 394 (заявка): четыре блока-окна — в обёртке
                // .ws-wgrid2: десктоп ≥1024px — ДВЕ колонки на всю
                // ширину (Task 403: слева профиль и отпуска, справа
                // мероприятия НАД СИЗ — между блоками профиля и СИЗ);
                // мобайл — прежний вертикальный стек (обёртка без
                // правил сетки)""",
    """                // Task 394 (заявка): блоки-окна — в обёртке
                // .ws-wgrid2: десктоп ≥1024px — ТРИ колонки на всю
                // ширину (Task 406: 1-я — профиль + отпуска +
                // мероприятия, 2-я — инструктажи, 3-я — СИЗ);
                // мобайл — вертикальный стек (обёртка без
                // правил сетки)""", 'renderWorkersPage-comment')

rep("""    /* Task 393: в теле вкладки карточка — ЧЕТЫРЕ блока-окна: зазор
       между ними — margin-bottom, у последнего — 0 (стек ВНУТРИ
       колонок Task 395 — и мобайл, и десктоп) */""",
    """    /* Task 393: в теле вкладки карточка — ПЯТЬ блоков-окон (Task
       405): зазор между ними — margin-bottom, у последнего — 0 (стек
       ВНУТРИ колонок Task 395 — и мобайл, и десктоп) */""", 'css-wcard-count')

rep("""    /* Task 395 (заявка): КОЛОНКИ-обёртки .ws-wcol (сборка —
       _renderWorkerCardPanels; Task 404 — ТРИ колонки: 1-я —
       профиль + отпуска, 2-я .ws-wcol-ppe — СИЗ, 3-я .ws-wcol-tr —
       мероприятия; блок СИЗ — СЛЕВА от блока мероприятий, три
       верхних блока в одну линию).
       Мобайл ≤1023px —
       колонки БЕЗ правил раскладки = блоки друг под другом; зазор
       между колонками — margin-bottom, у последней — 0 (внутри
       колонок панелям — базовые правила Task 393 выше) */""",
    """    /* Task 395 (заявка): КОЛОНКИ-обёртки .ws-wcol (сборка —
       _renderWorkerCardPanels; Task 406 — ТРИ колонки: 1-я —
       профиль + отпуска + мероприятия (мероприятия — ПОД
       отпусками), 2-я .ws-wcol-instr — инструктажи, 3-я
       .ws-wcol-ppe — СИЗ; блоки СИЗ и инструктажей поменяны
       местами).
       Мобайл ≤1023px —
       колонки БЕЗ правил раскладки = блоки друг под другом; зазор
       между колонками — margin-bottom, у последней — 0 (внутри
       колонок панелям — базовые правила Task 393 выше) */""", 'css-wcol-comment')

rep("""    /* Task 394 → 395 → 403 → 404 (заявка): ДЕСКТОП (≥1024px) —
       ТРИ РАВНЫЕ колонки НА ВСЮ ШИРИНУ окна вкладок (flex, обёртка
       .ws-wgrid2 — _renderWorkersPage, только вкладка работника;
       «Общая» — без колонок): 1-я — ПРОФИЛЬ, ПОД ним ОТПУСКА
       (вертикальный стек окон); 2-я — СИЗ; 3-я — МЕРОПРИЯТИЯ
       (Task 404: блок СИЗ — СЛЕВА от блока мероприятий, три верхних
       блока — профиль/СИЗ/мероприятия — в ОДНУ ЛИНИЮ; равные доли
       flex: 1 1 0 — блоки гарантированно помещаются; align-items:
       flex-start — колонки НЕ тянутся по высоте друг друга). Зазоры:
       между колонками — gap 12px; между окнами 1-й колонки —
       margin-bottom панелей (базовые правила Task 393) */""",
    """    /* Task 394 → 395 → 403 → 404 → 406 (заявки): ДЕСКТОП (≥1024px) —
       ТРИ РАВНЫЕ колонки НА ВСЮ ШИРИНУ окна вкладок (flex, обёртка
       .ws-wgrid2 — _renderWorkersPage, только вкладка работника;
       «Общая» — без колонок): 1-я — ПРОФИЛЬ, ПОД ним ОТПУСКА, ПОД
       ними МЕРОПРИЯТИЯ (Task 406); 2-я — ИНСТРУКТАЖИ; 3-я — СИЗ
       (Task 406: блоки СИЗ и инструктажей поменяны местами; равные
       доли flex: 1 1 0 — блоки гарантированно помещаются;
       align-items: flex-start — колонки НЕ тянутся по высоте друг
       друга). Зазоры: между колонками — gap 12px; между окнами
       колонок — margin-bottom панелей (базовые правила Task 393) */""", 'css-media-comment')

fail = 0
for old, new, tag in REPL:
    n = src.count(old)
    if n != 1:
        print('FAIL [406-inline %s]: вхождений %d' % (tag, n))
        fail += 1
        continue
    src = src.replace(old, new)
    print('OK [406-inline %s]' % tag)
assert fail == 0, 'правки 406 не применились'
assert src != orig
io.open(PATH, 'w', encoding='utf-8').write(src)
print('index.html: правки Task 406 записаны (5)')

# ============================================================
# 3. Тесты: копия с маппингом версий
# ============================================================
print('--- тесты (14 файлов + маппинг версий) ---')
for name in TESTS:
    src = io.open(os.path.join(K8TEST, 'tests', name), encoding='utf-8').read()
    n_a = src.count('kipia-test-v633')
    src = src.replace('kipia-test-v633', 'kipia-v476')
    n_g = src.count('kipia-test-v634')
    src = src.replace('kipia-test-v634', 'kipia-v477')
    io.open(os.path.join('tests', name), 'w', encoding='utf-8').write(src)
    print('  %s (ассерты v633→v476: %d, guards v634→v477: %d)'
          % (name, n_a, n_g))

# ============================================================
# 4. run-all.js: регистрация 405/406 (после 404, перед deploy-url)
# ============================================================
P2 = 'tests/run-all.js'
r = io.open(P2, encoding='utf-8').read()
old = """require('./test-task404.js');
require('./test-deploy-url.js');"""
new = """require('./test-task404.js');
// Task 405 — разделение таблицы инструктажей: сервер (лист «Мероприятия»,
// объединённый listTrainings, маршрутизация addTraining, сквозные id,
// trainingsSplitInit); карточка — блок «Мероприятия» + новый блок
// «Повторные инструктажи и периодическая проверка знаний»; сводка
require('./test-task405.js');
// Task 406 — карточка: мероприятия — ПОД отпусками (1-я колонка), блоки
// СИЗ и инструктажей поменяны местами (2-я — инструктажи, 3-я — СИЗ)
require('./test-task406.js');
require('./test-deploy-url.js');"""
assert r.count(old) == 1, 'run-all.js: якорь регистрации не найден'
io.open(P2, 'w', encoding='utf-8').write(r.replace(old, new))
print('run-all.js: test-task405/406.js подключены')

print('OK: перенос 405-406 завершён (SW-бамп — отдельным шагом)')
