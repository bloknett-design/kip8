#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 527 docs — ПРОДОЛЖЕНИЕ только для kip8 (формат строки с зеркалом).
task527-docs.py уже обновил kip8test (промт + ARCHITECTURE); здесь: kip8."""
import io

T527 = ('post-Task 527 (зеркало kip8test 178afab6) — ГЕОМЕТРИЯ: '
        'ПЕРЕСЕЧЕНИЯ ЛИНИЙ/ЦИФР ИСПРАВЛЕНЫ + РАСЧЁТНЫЕ ДАННЫЕ ВНУТРИ '
        'КАРТИНКИ ПОД ФИГУРОЙ + БЛОК УВЕЛИЧЕН (заявка: «В разделе Главная / '
        'Инженерные калькуляторы / Геометрия, на некоторых геометрических '
        'фигурах линии и цифры пересекаются и накладываются друг на друга, '
        'поправь, и расчётные данные должны отображаться на картинке под '
        'геометрической фигурой, поэтому блок с фигурой сделай немного '
        'больше.»): ДИАГНОСТИКА (VLM-аудит скриншотов Task 526 + разбор '
        'координат): сфера — подпись D пересекала штриховой меридиан; '
        'конус — L пересекала размерную линию H, D впритык (0–2 px); '
        'гориз. цилиндр — подпись h (span 45 < длины ~61) перекрывала '
        'выносную линию зеркала; кольцо — подписи D/d в отверстии '
        'ломались при малом d; ИСПРАВЛЕНИЯ: gfDimH labelPos \'below\', '
        'gfDimV — отступ 5→9 + вынос повернутой подписи за выносные линии '
        'при коротком размере, круг/сфера/кольцо — D размер ПОД фигурой, '
        'кольцо d — подпись НАД фигурой, конус L — у ЛЕВОГО ребра (anchor '
        'end), D — под линией; ДАННЫЕ В КАРТИНКЕ: #xxFigRes и .geo-fig-res* '
        'УБРАНЫ — gfDataZone рисует живой расчёт ВНУТРИ SVG под фигурой '
        '(разделитель .gf-sep y=194 + строки .gf-tx/.gf-val y=212 шаг 17, '
        'анимация .gf-resg, математика = calcGeo*); БЛОК БОЛЬШЕ: рамка '
        '320→350px, viewBox 240×240 (гориз. цилиндр 240×257); перенос '
        'index.html — prepare-kip8-transfer.py (дифф 244 строки = ровно '
        'контент Task 527, изоляты закрыты автоматически); DEPLOY-Task527 '
        '(ТОЛЬКО КЛИЕНТ); тесты test-task527 ×32 (SW kipia-v537 — два '
        'SW-теста слиты по конвенции kip8) + адаптация test-task526; УРОК '
        'ПАЙПЛАЙНА: transfer-скрипт резал файлы по первому «// ===» — '
        'пересобрано fix-скриптом; браузер 208/208 + VLM 15/15 '
        '(«дефектов пересечения НЕТ»; верификация по kip8test, скриншоты '
        'download/kip8test-task527/); SW kipia-v537 / kipia-test-v740; '
        'все 4 репо ЗЕЛЁНЫЕ: kip8 6729/0 → kip8-desktop 6744/0 (+32; '
        'Build success), kip8test 6728/0 → kip8test-desktop 6713/0')

P = '/home/z/my-project/kip8/Системный_промт_для_приложения_КИПиА.md'
s = io.open(P, encoding='utf-8').read()
old = '> **Версия документа:** 2026-10-14 (post-Task 526 (зеркало kip8test d139712f) — '
assert s.count(old) == 1, 'якорь kip8 не найден'
s = s.replace(old, '> **Версия документа:** 2026-10-15 (' + T527 +
              '. Post-Task 526 (зеркало kip8test d139712f) — ')
io.open(P, 'w', encoding='utf-8').write(s)
print('[ok] промт kip8')

A = '/home/z/my-project/kip8/ARCHITECTURE.md'
s = io.open(A, encoding='utf-8').read()
old_t, new_t = '6697', '6729'
old_f, new_f = '224', '225'
old_m, new_m = 'kip8-desktop 6712', 'kip8-desktop 6744'
i = s.index('`tests/`, %s тестов' % old_t)
seg = s[i:i + 400]
seg = seg.replace(old_t, new_t, 1).replace(old_f, new_f, 1).replace(old_m, new_m, 1)
s = s[:i] + seg + s[i + 400:]
assert new_t in s and new_m in s
io.open(A, 'w', encoding='utf-8').write(s)
print('[ok] ARCHITECTURE kip8: 6729 тестов, зеркало 6744')

W = '/home/z/my-project/kip8/worklog.md'
entry = ('\n---\nTask ID: 527 (финализация)\nAgent: main (Super Z)\n'
         'Task: Пуш/CI/синк/docs Task 527 (зеркало).\n\nWork Log:\n'
         '- Пуш b8080e5 → CI Tests 6729/0 + Pages + Build + синк (bot '
         'd366d6ae) → kip8-desktop 6744/0 + Build success.\n'
         '- Docs: версионная строка промта post-Task 527 (демоция '
         'post-Task 526), ARCHITECTURE.md §2 (6729/225 + зеркало 6744), '
         'эта запись.\n\n'
         'Stage Summary:\n- Task 527 ПОЛНОСТЬЮ ЗАКРЫТ: kip8 6729/0 → '
         'kip8-desktop 6744/0 (+32; Build success), kip8test 6728/0 → '
         'kip8test-desktop 6713/0. Правка ТОЛЬКО КЛИЕНТ — Apps Script, '
         'листы Google Sheets и деплой НЕ менялись: клиенты получат '
         'исправленные схемы по обычному циклу SW (kipia-v537). Открытых '
         'хвостов НЕТ.\n')
with io.open(W, 'a', encoding='utf-8') as f:
    f.write(entry)
print('[ok] worklog kip8')

# kip8test worklog-запись финализации (не успела записаться в task527-docs.py)
WT = '/home/z/my-project/kip8test/worklog.md'
s = io.open(WT, encoding='utf-8').read()
if 'Task ID: 527 (финализация)' not in s:
    entry = ('\n---\nTask ID: 527 (финализация)\nAgent: main (Super Z)\n'
             'Task: Пуш/CI/синк/docs Task 527.\n\nWork Log:\n'
             '- Пуш 178afab6 → CI Tests 6728/0 + Pages + синк (bot '
             '91117c8f) → kip8test-desktop 6713/0 + Build success.\n'
             '- Docs: версионная строка промта post-Task 527 (демоция '
             'post-Task 526), ARCHITECTURE.md §2 (6728/224 + зеркало '
             '6713), эта запись.\n\n'
             'Stage Summary:\n- Task 527 ПОЛНОСТЬЮ ЗАКРЫТ: kip8test '
             '6728/0 → kip8test-desktop 6713/0 (+33; Build success), '
             'kip8 6729/0 → kip8-desktop 6744/0. Правка ТОЛЬКО КЛИЕНТ — '
             'Apps Script, листы Google Sheets и деплой НЕ менялись: '
             'клиенты получат исправленные схемы по обычному циклу SW '
             '(kipia-test-v740). Открытых хвостов НЕТ.\n')
    with io.open(WT, 'a', encoding='utf-8') as f:
        f.write(entry)
    print('[ok] worklog kip8test')
else:
    print('[skip] worklog kip8test уже записан')
print('OK')
