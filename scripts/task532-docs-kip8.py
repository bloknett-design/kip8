#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 532 — docs-коммит kip8 (зеркало kip8test @5a577919):
  1) версионная строка промта: post-Task 532 ЗАМЕНЯЕТ post-Task 531;
  2) ARCHITECTURE.md §2 — счётчики: 6921 тест / 229 файлов,
     зеркало kip8-desktop 6921;
  3) worklog.md — запись Task 532 (финализация, kip8).
"""
import io

P_PROMT = 'Системный_промт_для_приложения_КИПиА.md'
P_ARCH = 'ARCHITECTURE.md'
P_WLOG = 'worklog.md'


def read(p):
    return io.open(p, encoding='utf-8').read()


def write(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


# ---------- 1. Версионная строка промта ----------
T532 = (
    '> **Версия документа:** 2026-10-16 (post-Task 532 — зеркало '
    'kip8test @5a577919) (ТАБЕЛЬ: LCD-ИНФОРМЕР — ШЕСТЕРЁНКА '
    'НАСТРОЕК В ПРАВОМ ВЕРХНЕМ УГЛУ (клик по окну — ТОЛЬКО '
    'календарь), ВЫБОР ГОДА, ДИАГНОСТИКА ПОГОДЫ + РЕЗЕРВНЫЙ '
    'ИСТОЧНИК open-meteo, АУДИТ КИРИЛЛИЦЫ FONT5 (заявка: «Обновил '
    'в Apps Script два файла (WorkSchedule.gs, Code.gs), а погода '
    'не отображается, хотя всё остальное работает. И ещё сделай в '
    'правом верхнем углу информера значок шестерёнки при нажатии '
    'на который должен появляться блок с настройками информера, а '
    'по нажатию на само окно информера должен открываться только '
    'календарь, и в календаре нужно сделать выбор года. И проверь '
    'в информере некоторые буквы не соответствуют кирилице.»): '
    'getWeather v2 — WorkSchedule.gs (браузерные заголовки, '
    'РЕЗЕРВ open-meteo.com с WMO-маппингом, diag-цепочка попыток; '
    'Code.gs НЕ менялся — роутинг Task 530); клиент: #wsLcdGear '
    '(правый верх) → настройки, клик по окну → календарь; «Год ‹ '
    '[селект ±10] ›»; _weatherDiag + статус + «Обновить сейчас» '
    '(«Unknown action» → подсказка про развёртывание Apps Script); '
    'FONT5: Ь≠Е, +Ё, Ч/З/Э/Д/Л/Ю, « » – — …, №→N (VLM-тест '
    'чтением); все 4 репо ЗЕЛЁНЫЕ: kip8 6921/0 → kip8-desktop '
    '6921/0 (+46), kip8test 6921/0 → kip8test-desktop 6906/0; '
    'перенос — дифф 425 строк клиент + 161 строка WorkSchedule.gs, '
    'SW v541→v542; ARCHITECTURE.md §2 (счётчик 6921/229 + зеркало '
    '6921); worklog.md — запись Task 532 (финализация); scripts/'
    'task532-transfer-tests.py + task532-browser-check-kip8.py + '
    'task532-docs-kip8.py (kipia-v542, Task 532))')

promt = read(P_PROMT)
lines = promt.split('\n')
assert 'post-Task 531' in lines[2], 'строка 3 не post-Task 531!'
lines[2] = T532
write(P_PROMT, '\n'.join(lines))
print('промт: строка версии заменена post-Task 531 → post-Task 532')

# ---------- 2. ARCHITECTURE.md §2 ----------
arch = read(P_ARCH)
old = ('`tests/`, 6875 тестов, 229 тест-файлов, `node tests/run-all.js`; '
       'зеркало CI: kip8-desktop 6890')
new = ('`tests/`, 6921 тест, 229 тест-файлов, `node tests/run-all.js`; '
       'зеркало CI: kip8-desktop 6921')
assert old in arch, 'не найден счётчик ARCHITECTURE.md'
arch = arch.replace(old, new, 1)
write(P_ARCH, arch)
print('ARCHITECTURE.md: 6875/229/6890 → 6921/229/6921')

# ---------- 3. worklog.md ----------
WLOG = (
    '\n---\n'
    'Task ID: 532 (финализация)\n'
    'Agent: main (Super Z)\n'
    'Task: Зеркало kip8test @1513efac (Task 532): шестерёнка '
    'настроек, клик по окну — только календарь, выбор года, '
    'диагностика погоды + резерв open-meteo, кириллица FONT5.\n'
    '\n'
    'Work Log:\n'
    '- Перенос: prepare-kip8-transfer.py — дифф 425 строк = контент '
    'Task 532 (клиент); WorkSchedule.gs — getWeather v2 (161 строка: '
    'заголовки, резерв open-meteo, diag; Code.gs не менялся).\n'
    '- task532-transfer-tests.py: test-task532.js (SW kipia-v542; фикс '
    'регэкспа версии после переноса) + адаптация 529/531/'
    'work-schedule + бамп SW v541→v542 (ассерты 717, гварды 171 '
    'первыми v543) — итог 6921/0 (+46, зеркало kip8test).\n'
    '- Верификация зеркальная: браузер task532-browser-check-kip8.py '
    '48/48 (шестерёнка/семантика кликов/год/диагностика/глифы/1024/'
    'обе темы, 0 JS-ошибок).\n'
    '- Пуш kip8 47ce257 → CI 6921/0 + Pages + Build + синк (38ab4dd) → '
    'kip8-desktop 6921/0 + Build success.\n'
    '- Docs (зеркало kip8test @5a577919): версионная строка промта '
    'post-Task 532, ARCHITECTURE.md §2 (6921/229 + зеркало 6921), '
    'эта запись.\n'
    '\n'
    'Stage Summary:\n'
    '- Task 532 в kip8 ПОЛНОСТЬЮ ЗАКРЫТ: все 4 репо ЗЕЛЁНЫЕ (6921/'
    '6906/6921/6921, сборки success). Правка КЛИЕНТ + WorkSchedule.gs. '
    'ДЕЙСТВИЕ ПОЛЬЗОВАТЕЛЯ: обновить WorkSchedule.gs в Apps Script + '
    'НОВАЯ ВЕРСИЯ развёртывания (Code.gs — если не обновлялся в Task '
    '530), затем шестерёнка → «Обновить сейчас» (DEPLOY-Task532). '
    'SW kipia-v542. Хвостов НЕТ. СЛЕДУЮЩАЯ ЗАДАЧА: задачи '
    'пользователя.\n')

wl = read(P_WLOG)
if 'Task ID: 532' not in wl:
    wl = wl.rstrip('\n') + WLOG
    write(P_WLOG, wl)
    print('worklog.md: добавлена запись Task 532 (финализация)')
else:
    print('worklog.md: запись Task 532 уже есть — пропуск')

print('ГОТОВО: правки docs применены')
