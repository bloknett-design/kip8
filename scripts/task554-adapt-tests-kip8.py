#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 554 — адаптация старых тестов kip8 (srvVer 427 → 554):
те же правки, что выполнены в kip8test (test-task421/422/423/425/
426/427 + run-all.js): моки ответов, ассерты версии сервера,
пороги предупреждения, названия тестов.
"""
import io

ROOT = '/home/z/my-project/kip8/tests'

EDITS = {
    'test-task421.js': [
        ("            // srvVer актуального сервера (Task 427) — предупреждения в тосте нет\n            srvVer: '427',",
         "            // srvVer актуального сервера (Task 554) — предупреждения в тосте нет\n            srvVer: '554',"),
    ],
    'test-task422.js': [
        ('        assertTrue(fn.indexOf("srvVer: \'427\'") !== -1,\n            \'версия сервера автосоздания — в ответе (клиент отличает старый Apps Script); Task 426: День шахтёра не праздник\');',
         '        assertTrue(fn.indexOf("srvVer: \'554\'") !== -1,\n            \'версия сервера автосоздания — в ответе (клиент отличает старый Apps Script); Task 554: примечание переносится в автосозданные записи\');'),
        ("        assertEqual(r.data.srvVer, '427', 'версия сервера в ответе');\n        assertEqual(r.data.created.length, 2, 'созданы ОБЕ записи');\n        assertEqual(r.data.skipped.length, 0, 'пропусков нет');",
         "        assertEqual(r.data.srvVer, '554', 'версия сервера в ответе');\n        assertEqual(r.data.created.length, 2, 'созданы ОБЕ записи');\n        assertEqual(r.data.skipped.length, 0, 'пропусков нет');"),
        ("        assertEqual(r.data.created.length, 0, 'записей НЕТ (зависимый пункт)');\n        assertEqual(r.data.skipped.length, 0, 'пропусков нет');\n        assertEqual(r.data.srvVer, '427', 'версия сервера в ответе');",
         "        assertEqual(r.data.created.length, 0, 'записей НЕТ (зависимый пункт)');\n        assertEqual(r.data.skipped.length, 0, 'пропусков нет');\n        assertEqual(r.data.srvVer, '554', 'версия сервера в ответе');"),
        ("            id: 20, выполнение: 1, просрочен: 0, srvVer: '427',\n            autoNote: 'пункт=… родитель=- дети=…',\n            created: [{ id: 60, тема: '…общий…', дата_начала: '2027-03-01' }],",
         "            id: 20, выполнение: 1, просрочен: 0, srvVer: '554',\n            autoNote: 'пункт=… родитель=- дети=…',\n            created: [{ id: 60, тема: '…общий…', дата_начала: '2027-03-01' }],"),
        ("    test('ошибка автосоздания: ⚠ в тосте, отметка применена', async () => {\n        const rec = JSON.parse(JSON.stringify(REC));\n        const ctx = makeCtx(rec, {\n            id: 20, выполнение: 1, просрочен: 0, srvVer: '427',",
         "    test('ошибка автосоздания: ⚠ в тосте, отметка применена', async () => {\n        const rec = JSON.parse(JSON.stringify(REC));\n        const ctx = makeCtx(rec, {\n            id: 20, выполнение: 1, просрочен: 0, srvVer: '554',"),
        ("        const ctx = makeCtx(rec, {\n            id: 20, выполнение: 1, просрочен: 0, srvVer: '427',\n            autoNote: 'пункт=… ; Task 421: зависимый пункт — автосоздания нет',",
         "        const ctx = makeCtx(rec, {\n            id: 20, выполнение: 1, просрочен: 0, srvVer: '554',\n            autoNote: 'пункт=… ; Task 421: зависимый пункт — автосоздания нет',"),
    ],
    'test-task423.js': [
        ("    test('srvVer 427 — версия сервера в ответе', () => {\n        const fn = stripComments(methodText(WS_SRC, 'setTrainingDone'));\n        assertTrue(fn.indexOf(\"srvVer: '427'\") !== -1,\n            'клиент отличает сервер Task 427+ (раздельные последовательности id), Task 423+ (период 9-ОГЭ = 3 мес) и Task 426 (День шахтёра не праздник)');\n    });",
         "    test('srvVer 554 — версия сервера в ответе', () => {\n        const fn = stripComments(methodText(WS_SRC, 'setTrainingDone'));\n        assertTrue(fn.indexOf(\"srvVer: '554'\") !== -1,\n            'клиент отличает сервер Task 554+ (примечание — перенос), Task 427+ (раздельные последовательности id), Task 423+ (период 9-ОГЭ = 3 мес) и Task 426 (День шахтёра не праздник)');\n    });"),
        ("    test('toggleTrainingDone: предупреждение при srvVer < 427 (граница поднята Task 427)', () => {\n        const fn = stripComments(methodText(INDEX_SRC, 'toggleTrainingDone'));\n        assertTrue(fn.indexOf('parseInt(d.srvVer, 10) < 427') !== -1,\n            'сервер 426 и старше (сквозная нумерация id, период 9-ОГЭ из листа) — предупреждение; историческая граница 423 поглощена');",
         "    test('toggleTrainingDone: предупреждение при srvVer < 554 (граница поднята Task 554)', () => {\n        const fn = stripComments(methodText(INDEX_SRC, 'toggleTrainingDone'));\n        assertTrue(fn.indexOf('parseInt(d.srvVer, 10) < 554') !== -1,\n            'сервер 553 и старше (примечание не переносится, сквозная нумерация id, период 9-ОГЭ из листа) — предупреждение; исторические границы 423/427 поглощены');"),
        ("        assertEqual(r.data.srvVer, '427', 'версия сервера Task 427');",
         "        assertEqual(r.data.srvVer, '554', 'версия сервера Task 554');"),
        ("    test('регресс 421: отметка 9-ОГЭ — только фиксация, srvVer 423', () => {",
         "    test('регресс 421: отметка 9-ОГЭ — только фиксация, srvVer в ответе', () => {"),
        ("        assertEqual(r.data.srvVer, '427', 'версия сервера в ответе');",
         "        assertEqual(r.data.srvVer, '554', 'версия сервера в ответе');"),
        ("            'srvVer 422 < 427 — предупреждение о старом Apps Script: ' + r.shown);\n    });\n\n    test('сервер 427: без предупреждения', async () => {\n        const rec = JSON.parse(JSON.stringify(REC));\n        const ctx = makeCtx(rec, {\n            id: 20, выполнение: 1, просрочен: 0, srvVer: '427',",
         "            'srvVer 422 < 554 — предупреждение о старом Apps Script: ' + r.shown);\n    });\n\n    test('сервер 554: без предупреждения', async () => {\n        const rec = JSON.parse(JSON.stringify(REC));\n        const ctx = makeCtx(rec, {\n            id: 20, выполнение: 1, просрочен: 0, srvVer: '554',"),
        ("            'srvVer 427 — предупреждения нет');",
         "            'srvVer 554 — предупреждения нет');"),
    ],
    'test-task425.js': [
        ("    test('srvVer 427 — версия сервера в ответе setTrainingDone', () => {\n        const fn = stripComments(methodText(WS_SRC, 'setTrainingDone'));\n        assertTrue(fn.indexOf(\"srvVer: '427'\") !== -1,\n            'srvVer 427 (Task 427: раздельные последовательности id листов; День шахтёра не праздник — Task 426; мероприятия без автосоздания — Task 425)');",
         "    test('srvVer 554 — версия сервера в ответе setTrainingDone', () => {\n        const fn = stripComments(methodText(WS_SRC, 'setTrainingDone'));\n        assertTrue(fn.indexOf(\"srvVer: '554'\") !== -1,\n            'srvVer 554 (Task 554: примечание — перенос в автосозданные записи; Task 427: раздельные последовательности id листов; День шахтёра не праздник — Task 426; мероприятия без автосоздания — Task 425)');"),
        ("        assertEqual(r.data.srvVer, '427', 'версия сервера Task 427');",
         "        assertEqual(r.data.srvVer, '554', 'версия сервера Task 554');"),
    ],
    'test-task426.js': [
        ("    test('JS: srvVer 427 в ответе setTrainingDone', () => {\n        assertTrue(WS_GS_SRC.indexOf(\"srvVer: '427'\") !== -1,\n            'srvVer 427 (Task 427: раздельные последовательности id; День шахтёра не праздник — Task 426)');",
         "    test('JS: srvVer 554 в ответе setTrainingDone', () => {\n        assertTrue(WS_GS_SRC.indexOf(\"srvVer: '554'\") !== -1,\n            'srvVer 554 (Task 554: примечание — перенос; Task 427: раздельные последовательности id; День шахтёра не праздник — Task 426)');"),
        ("    test('JS: регресс — порог предупреждения «старый сервер» srvVer < 427', () => {\n        const fn = extractMethod(INDEX_SRC, 'toggleTrainingDone');\n        assertTrue(fn !== null && fn.indexOf('parseInt(d.srvVer, 10) < 427') !== -1,\n            'клиент предупреждает при srvVer < 427 (Task 427 поднял границу: сквозная нумерация id — тоже старый сервер; историческая 423 поглощена)');",
         "    test('JS: регресс — порог предупреждения «старый сервер» srvVer < 554', () => {\n        const fn = extractMethod(INDEX_SRC, 'toggleTrainingDone');\n        assertTrue(fn !== null && fn.indexOf('parseInt(d.srvVer, 10) < 554') !== -1,\n            'клиент предупреждает при srvVer < 554 (Task 554 поднял границу: примечание не переносится — тоже старый сервер; исторические 423/427 поглощены)');"),
    ],
    'test-task427.js': [
        ("    test('srvVer 427 — версия сервера в ответе setTrainingDone', () => {\n        const fn = stripComments(methodText(WS_SRC, 'setTrainingDone'));\n        assertTrue(fn.indexOf(\"srvVer: '427'\") !== -1,\n            'srvVer 427 (Task 427: раздельные последовательности id)');",
         "    test('srvVer 554 — версия сервера в ответе setTrainingDone', () => {\n        const fn = stripComments(methodText(WS_SRC, 'setTrainingDone'));\n        assertTrue(fn.indexOf(\"srvVer: '554'\") !== -1,\n            'srvVer 554 (Task 554: примечание — перенос; Task 427: раздельные последовательности id)');"),
        ("    test('порог предупреждения «старый сервер» — srvVer < 427', () => {\n        const fn = stripComments(methodText(INDEX_SRC, 'toggleTrainingDone'));\n        assertTrue(fn.indexOf('parseInt(d.srvVer, 10) < 427') !== -1,\n            'сквозная нумерация id (сервер до 427) — тоже старый сервер');",
         "    test('порог предупреждения «старый сервер» — srvVer < 554', () => {\n        const fn = stripComments(methodText(INDEX_SRC, 'toggleTrainingDone'));\n        assertTrue(fn.indexOf('parseInt(d.srvVer, 10) < 554') !== -1,\n            'примечание не переносится / сквозная нумерация id (сервер до 554) — тоже старый сервер');"),
        ("        assertEqual(r.data.srvVer, '427', 'версия сервера Task 427');",
         "        assertEqual(r.data.srvVer, '554', 'версия сервера Task 554');"),
        ("                data: { id: 5, 'выполнение': 1, 'просрочен': 0,\n                        srvVer: '427', autoNote: '', created: [],",
         "                data: { id: 5, 'выполнение': 1, 'просрочен': 0,\n                        srvVer: '554', autoNote: '', created: [],"),
    ],
}

import os
total = 0
for fname, pairs in EDITS.items():
    path = os.path.join(ROOT, fname)
    src = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        n = src.count(old)
        if n != 1:
            print('FAIL %s: паттерн найден %d раз: %s' % (fname, n, old[:60]))
            raise SystemExit(1)
        src = src.replace(old, new)
        total += 1
    io.open(path, 'w', encoding='utf-8').write(src)
    print('  %s: %d правок' % (fname, len(pairs)))

print('\nИтого: %d правок в %d файлах' % (total, len(EDITS)))
