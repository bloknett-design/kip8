#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task 534 — docs-коммит kip8 (по образцу task533-docs-kip8.py):
  1) версионная строка промта: post-Task 534 (зеркало kip8test
     @6ec1b01d) ЗАМЕНЯЕТ post-Task 533;
  2) ARCHITECTURE.md §2 — счётчики: 6986 тестов / 231 тест-файлов,
     зеркало CI: kip8-desktop 7001 (+29 electron-тестов −14
     workflow-гвардов — гварды окружения Tasks 517/518);
  3) worklog.md — запись Task 534 (финализация kip8).
Коммит делает обёртка (bash). Скрипт — артефакт коммита.
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
T534 = (
    '> **Версия документа:** 2026-10-16 (post-Task 534 — зеркало '
    'kip8test @6ec1b01d) (ТАБЕЛЬ: LCD-ИНФОРМЕР — ПОГОДА: ДВА ПРЯМЫХ '
    'КАНАЛА (open-meteo.com → wttr.in) + подсказка authorizeWeather; '
    'КАЛЕНДАРЬ: строки головы ПО ЛЕВОМУ КРАЮ, подписи «Год»/«Месяц» '
    'УБРАНЫ, шрифт месяца мельче года (заявка: «Погода не работает '
    '\\"Источники не дали данных (прямой запрос: Failed to fetch); '
    'сервер: meteoinfo:exception:У вас нет разрешения на вызов '
    'функции \\"UrlFetchApp.fetch\\". Т; open-meteo:exception:…\\". В '
    'календаре, кнопки с годом выравняй по левому краю, надписи '
    '\\"Год\\" и \\"Месяц\\" убери, шрифт в кнопках месяца сделай '
    'немного меньше чем в годе.»): (1) перенос — дифф 316 строк '
    'index.html (только клиент: канал 2 wttr.in — WT_URL '
    'format=j1&lang=ru + _fetchWttr + _parseWttr (lang_ru/EN-слова → '
    'русское явление, cloudcover % → балл 0..10, км/ч → м/с ÷3.6, '
    'гПа → мм ÷1.33322, UTC AM/PM → +7); _loadWeather цепочкой '
    'open-meteo → wttr → сервер; _weatherDiag.direct/.wttr — причины '
    'ОБОИХ каналов; подсказка «запустите authorizeWeather() … новая '
    'версия развёртывания» при diag «нет разрешения|UrlFetchApp»; '
    'календарь: flex-start обе строки, подписи удалены, шрифт месяца '
    '12/15/12 против года 13/16/13) + WorkSchedule.gs 83 строки '
    '(топ-уровневая authorizeWeather() — разовая авторизация '
    'script.external_request: Выполнить в редакторе → подтвердить '
    'доступ → новая версия развёртывания; diag 60→90); Code.gs и '
    'листы НЕ менялись; (2) тесты — test-task534.js/test-task533.js/'
    'test-task532.js с SW-хвостом kip8 (assert kipia-v544, гвард '
    'v545; swap хвоста вместо токен-замены — регэксп '
    'kipia-test-v\\d+ и старые версии не тянутся — урок Task 533) + '
    'бамп SW v543→v544 (ассерты 888 замен/207 файлов, гварды v545 '
    'первыми) + регистрация — итог 6986/0 (ПАРИТЕТ kip8test, +32); '
    '(3) верификация зеркальная: браузер task534-browser-check-kip8.py '
    '35/35 (порт 8997, обе темы, DPR 2/1: подписей в DOM нет, '
    'flex-start + геометрия левого края, шрифты 12/13/15/16/12; '
    'ПОГОДА: OM ok → wttr/сервер НЕ звались; OM сбой → wttr успех — '
    'сервер НЕ звался; оба сбой → сервер −12° «(через Apps '
    'Script)»; diag «нет разрешения» → подсказка authorizeWeather() '
    '+ dnote «open-meteo: http_503; wttr.in: http_502»; 1024 '
    'светлая; 0 JS-ошибок); DEPLOY-Task534 — СЕРВЕР: обновить '
    'WorkSchedule.gs в Apps Script → выполнить authorizeWeather() → '
    'новая версия развёртывания (иначе резерв погоды падает по '
    'разрешению — ошибка из заявки); КЛИЕНТ: Ctrl+Shift+R '
    '(kipia-v544, Task 534))')

promt = read(P_PROMT)
lines = promt.split('\n')
assert 'post-Task 533' in lines[2], 'строка 3 не post-Task 533!'
lines[2] = T534
write(P_PROMT, '\n'.join(lines))
print('промт: строка версии заменена post-Task 533 → post-Task 534')

# ---------- 2. ARCHITECTURE.md §2 ----------
arch = read(P_ARCH)
old = ('`tests/`, 6954 теста, 230 тест-файлов, `node tests/run-all.js`; '
       'зеркало CI: kip8-desktop 6954')
new = ('`tests/`, 6986 тестов, 231 тест-файлов, `node tests/run-all.js`; '
       'зеркало CI: kip8-desktop 7001')
assert old in arch, 'не найден счётчик ARCHITECTURE.md'
arch = arch.replace(old, new, 1)
write(P_ARCH, arch)
print('ARCHITECTURE.md: 6954/230/6954 → 6986/231/7001')

# ---------- 3. worklog.md ----------
WLOG = (
    '\n---\n'
    'Task ID: 534 (финализация kip8)\n'
    'Agent: main (Super Z)\n'
    'Task: Перенос Task 534 из kip8test в kip8 (зеркало @6ec1b01d): '
    'погода — второй прямой канал wttr.in + подсказка authorizeWeather; '
    'календарь — левый край, без подписей, шрифт месяца мельче. '
    'Пуш/CI/синк/docs.\n'
    '\n'
    'Work Log:\n'
    '- Перенос scripts/task534-transfer-tests.py: index.html (дифф 316 '
    'строк = контент Task 534, только клиент; prepare-kip8-transfer.py '
    '— дифф сверен, изолятов нет) + WorkSchedule.gs (дифф 83 строки: '
    'топ-уровневая authorizeWeather() + diag 60→90).\n'
    '- Тесты: test-task534.js/test-task533.js/test-task532.js — копии '
    'kip8test, SW-хвост заменён единым kip8-блоком (assert kipia-v544 '
    '+ гвард v545 + тест «файл на месте» для 534/533 — паритет '
    'счётчика); заголовки — токен-замены версий; бамп SW v543→v544 '
    '(ассерты 888 замен/207 файлов, гварды v545 первыми); регистрация '
    'test-task534.js в run-all.js — итог 6986/0 (ПАРИТЕТ kip8test, '
    '+32). УРОК переноса: повторный запуск transfer-скрипта НЕ '
    'идемпотентен по бампу (ассерты v544 → гварды v545 каскадом) — '
    'при правке перенос git checkout -- . и один чистый запуск.\n'
    '- Верификация зеркальная: task534-browser-check-kip8.py 35/35 '
    '(порт 8997, localStorage без префикса; обе темы, DPR 2/1; '
    '0 JS-ошибок).\n'
    '- Пуши и зеркала: kip8 f3a97fbc (feat) → CI Tests + Pages + '
    'Build success + синк 4053c3f9 → kip8-desktop CI 7001/0 + Build '
    'success (7001 = 6986 + 29 electron-тестов − 14 workflow-гвардов '
    '— гварды окружения Tasks 517/518).\n'
    '- Docs: DEPLOY-Task534-lcd-weather-two-channels-auth-hint.md '
    '(kip8-версия), промт post-Task 534, ARCHITECTURE.md §2 '
    '(6986/231 + зеркало 7001), эта запись; scripts/: '
    'task534-transfer-tests.py + task534-browser-check-kip8.py + '
    'task534-docs-kip8.py.\n'
    '\n'
    'Stage Summary:\n'
    '- Task 534 ПОЛНОСТЬЮ ЗАКРЫТ во всех 4 репо: kip8test 6986/0 → '
    'kip8test-desktop 6971/0; kip8 6986/0 → kip8-desktop 7001/0; '
    'сборки success. Из заявки выполнено ВСЁ: (1) погода — ДВА '
    'прямых канала (open-meteo → wttr.in) + серверный резерв с '
    'подсказкой authorizeWeather (диагноз «нет разрешения '
    'UrlFetchApp» лечится разово: WorkSchedule.gs → Выполнить '
    'authorizeWeather() → новая версия развёртывания); (2) '
    'календарь — год/месяц по левому краю, подписи «Год»/«Месяц» '
    'убраны, шрифт месяца мельче года. SW: kipia-test-v747 / '
    'kipia-v544. Хвостов НЕТ. СЛЕДУЮЩАЯ ЗАДАЧА: задачи пользователя.\n')

wlog = read(P_WLOG)
wlog += WLOG
write(P_WLOG, wlog)
print('worklog.md: запись Task 534 (kip8) добавлена')
print('OK — docs готовы к коммиту')
